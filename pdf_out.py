"""Render the filled MAUS-Erhebungsbogen A (sections A–F, two pages) with PyMuPDF."""
import fitz

from maus import MAX_SCORE, SECTIONS

X0, LABEL_W, COL_W, DATE_W, ROW_H = 40, 230, 26, 80, 20
GREY = (0.75, 0.75, 0.75)
PAGES = [list(SECTIONS)[:3], list(SECTIONS)[3:]]  # A–C on page 1, D–F on page 2


def _text(page, x, y, s, size=9, bold=False, maxw=None):
    font = "hebo" if bold else "helv"
    while maxw and size > 6 and fitz.get_text_length(s, fontname=font, fontsize=size) > maxw:
        size -= 0.25
    page.insert_text((x, y), s, fontsize=size, fontname=font)


def _header(page):
    _text(page, X0, 45, "Berufsbildungsbereich", 14)
    _text(page, X0, 62, "MAUS-Erhebungsbogen-A", 10, True)
    page.draw_line((X0, 70), (555, 70))


def _table(page, y, sections, scores, date):
    xs = [X0 + LABEL_W + i * COL_W for i in range(8)]
    right = xs[-1] + DATE_W
    for section in sections:
        page.draw_rect(fitz.Rect(X0, y, right, y + ROW_H), fill=(0.93, 0.93, 0.93), width=0.5)
        _text(page, X0 + 3, y + 13, section, 8.5, True)
        for i, s in enumerate(range(-3, 4)):
            _text(page, xs[i] + 9, y + 13, str(s), 8.5, True)
        _text(page, xs[-1] + 4, y + 13, "Datum:", 8.5, True)
        y += ROW_H
        for t in SECTIONS[section]:
            page.draw_rect(fitz.Rect(X0, y, right, y + ROW_H), width=0.5)
            _text(page, X0 + 3, y + 13, t, 8.5, maxw=LABEL_W - 6)
            for i, s in enumerate(range(-3, 4)):
                cell = fitz.Rect(xs[i], y, xs[i] + COL_W, y + ROW_H)
                page.draw_rect(cell, fill=GREY if s > MAX_SCORE[t] else None, width=0.5)
                if scores.get(t) == s:
                    _text(page, xs[i] + 8, y + 14, "X", 11, True)
            if t in scores:
                _text(page, xs[-1] + 4, y + 13, date, 8)
            y += ROW_H
    return y


def _footer(page, n):
    _text(page, X0, 790, "Datum, Unterschrift: ______________________________", 9)
    _text(page, X0, 820, "KI-Entwurf – durch Fachkraft geprüft und freigegeben", 7)
    _text(page, 500, 820, f"Seite {n}", 8)


def build_pdf(meta, scores):
    doc = fitz.open()
    for n, sections in enumerate(PAGES, 1):
        page = doc.new_page()
        _header(page)
        y = 100
        if n == 1:
            _text(page, X0, 100, "MAUS-Erhebungsbogen A", 16, True)
            _text(page, X0, 116, "(Merkmalsprofile des Arbeits- und Sozialverhaltens)", 9)
            _text(page, X0, 140, f"Name des Teilnehmers: {meta['name']}", 10, True)
            _text(page, 330, 140, f"Geburtsdatum: {meta['dob']}", 10, True)
            _text(page, X0, 158, f"Beobachtende Fachkraft: {meta['staff']}", 9)
            _text(page, 330, 158, f"Beginn: {meta['start']}   Ende: {meta['end']}", 9)
            _text(page, X0, 190, "Beobachtungsmerkmale", 10, True)
            _text(page, X0 + LABEL_W + 60, 190, "Ausprägung", 10, True)
            y = 198
        _table(page, y, sections, scores, meta["end"])
        _footer(page, n)
    return doc.tobytes()
