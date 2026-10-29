"""MAUS-Erhebungsbogen A: traits, allowed score ranges and DIK-2 lookup."""
import json
from pathlib import Path

SECTIONS = {
    "A) Sozial-kommunikative Kompetenz": ["Kontaktfähigkeit", "Gruppen- und Teamfähigkeit", "Kooperationsfähigkeit"],
    "B) Methodenkompetenz": ["Konzentration", "Merkfähigkeit", "Arbeitstempo"],
    "C) Personale Kompetenz": ["Flexibilität", "Selbsteinschätzung", "Kritikfähigkeit", "Pünktlichkeit", "Anweisungsverständnis"],
    "D) Aktivitäts- und Umsetzungskompetenz": ["Selbstständiges Arbeiten", "Durchhaltevermögen", "Sorgfalt", "Leistungsbereitschaft"],
    "E) Eignung und Neigung": ["Berufsinteresse", "Fachwissen", "Leseflüssigkeit", "Sinnentnehmendes Lesen",
                               "Addition / Subtraktion", "Multiplikation / Division", "Schriftlicher Ausdruck"],
    "F) Arbeitsbezogene Kompetenz": ["Geschicklichkeit bei Arbeiten mit Werkzeuggebrauch",
                                     "Geschicklichkeit bei Arbeiten ohne Werkzeuggebrauch",
                                     "Anweisungsverständnis bei der Arbeit", "Arbeitstempo bei einfach strukturierten Arbeiten",
                                     "Ausdauer bei der Arbeit", "Sorgfalt bei der Arbeit", "Selbstständigkeit in der Arbeitsausführung"],
}
TRAITS = [t for ts in SECTIONS.values() for t in ts]

# grey cells on the form = scores that cannot be given; this is the highest allowed score
MAX_SCORE = {t: 3 for t in TRAITS}
MAX_SCORE.update({
    "Selbsteinschätzung": 1, "Pünktlichkeit": 1,
    "Durchhaltevermögen": 1,
    "Leseflüssigkeit": 1, "Addition / Subtraktion": 1, "Multiplikation / Division": 1,
    "Geschicklichkeit bei Arbeiten mit Werkzeuggebrauch": 1,
    "Geschicklichkeit bei Arbeiten ohne Werkzeuggebrauch": 1,
    "Anweisungsverständnis bei der Arbeit": 0,
    "Arbeitstempo bei einfach strukturierten Arbeiten": 1,
    "Ausdauer bei der Arbeit": 0,
    "Sorgfalt bei der Arbeit": 0,
    "Selbstständigkeit in der Arbeitsausführung": 1,
})

# MAUS trait -> DIK-2 characteristic (names as parsed from the PDF)
DIK_KEY = {
    "Kontaktfähigkeit": "KONTAKTFÄHIGKEIT",
    "Gruppen- und Teamfähigkeit": "GRUPPEN- UND TEAMFÄHIGKEIT",
    "Kooperationsfähigkeit": "KOOPERATIONSFÄHIGKEIT",
    "Konzentration": "KONZENTRATION",
    "Merkfähigkeit": "MERKFÄHIGKEIT",
    "Arbeitstempo": "ARBEITSTEMPO",
    "Flexibilität": "FLEXIBILITÄT",
    "Selbsteinschätzung": "SELBSTEINSCHÄTZUNG",
    "Kritikfähigkeit": "KRITIKFÄHIGKEIT",
    "Pünktlichkeit": "PÜNKTLICHKEIT",
    "Anweisungsverständnis": "ANWEISUNGSVERSTÄNDNIS",
    "Selbstständiges Arbeiten": "SELBSTSTÄNDIGES ARBEITEN",
    "Durchhaltevermögen": "DURCHHALTEVERMÖGEN",
    "Sorgfalt": "SORGFALT",
    "Leistungsbereitschaft": "ANSTRENGUNGSBEREITSCHAFT",
    "Berufsinteresse": "BERUFSINTERESSE",
    "Fachwissen": "FACHWISSEN",
    "Leseflüssigkeit": "LESEFLÜSSIGKEIT",
    "Sinnentnehmendes Lesen": "SINNENTNEHMENDES LESEN",
    "Addition / Subtraktion": "ADDITION / SUBTRAKTION",
    "Multiplikation / Division": "MULTIPLIKATION / DIVISION",
    "Schriftlicher Ausdruck": "SCHRIFTLICHER AUSDRUCK",
    "Geschicklichkeit bei Arbeiten mit Werkzeuggebrauch": "UMGANG MIT MASCHINEN,GERÄTEN,WERKZEUGEN",
    "Geschicklichkeit bei Arbeiten ohne Werkzeuggebrauch": "PRAKTISCHE FERTIGKEITEN",
    "Anweisungsverständnis bei der Arbeit": "ANWEISUNGSVERSTÄNDNIS",
    "Arbeitstempo bei einfach strukturierten Arbeiten": "ARBEITSTEMPO",
    "Ausdauer bei der Arbeit": "AUSDAUER",
    "Sorgfalt bei der Arbeit": "SORGFALT",
    "Selbstständigkeit in der Arbeitsausführung": "SELBSTSTÄNDIGES ARBEITEN",
}

_DIK = json.loads((Path(__file__).parent / "dik2.json").read_text(encoding="utf-8"))
# the PDF has typos in a few headings; merge them into the right characteristic
for typo, right in {"SORGAFLT": "SORGFALT", "ANSTREGUNGSBEREITSCHAFT": "ANSTRENGUNGSBEREITSCHAFT"}.items():
    for score, txt in _DIK.pop(typo, {}).items():
        _DIK.setdefault(right, {}).setdefault(score, txt)


def dik_text(trait: str, score: int, limit: int = 600) -> str:
    """Official DIK-2 behaviour description for a trait at a score (nearest available)."""
    levels = _DIK.get(DIK_KEY[trait], {})
    for s in sorted(levels, key=lambda k: abs(int(k) - score)):
        txt = " ".join(levels[s].split())
        return txt[:limit] + ("…" if len(txt) > limit else "")
    return ""
