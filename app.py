import io
import random
from datetime import date

import streamlit as st

import eingliederungsplan_pdf as ep
import llm
import pdf_out
from maus import MAX_SCORE, SECTIONS, TRAITS, dik_text
from privacy import scrub

st.set_page_config(page_title="MAUS-Assistent", page_icon="📝", layout="wide")
ss = st.session_state

AREAS = ["Metallverarbeitung", "Kabelkonfektion", "Druckerei", "Industriemontage", "Verpackung"]
TODAY = date.today().strftime("%d.%m.%Y")

if "pid" not in ss:
    ss.pid = f"Teilnehmer_{random.randint(100, 999)}"
    ss.history = [{"role": "assistant", "content": f"Hallo! Wir füllen den MAUS-Bogen für {ss.pid} aus. "
                   f"Erzählen Sie mir bitte zuerst, wie {ss.pid} im Kontakt mit anderen Menschen in der Gruppe auftritt."}]
    ss.last_sent = ""


def score_of(t):
    v = ss.get(f"s_{t}", "–")
    return None if v == "–" else int(v)


def current_scores():
    return {t: score_of(t) for t in TRAITS if score_of(t) is not None}


def bullets(text):
    return [ln.strip().lstrip("-•▪*– ").strip() for ln in text.splitlines() if ln.strip().lstrip("-•▪*– ").strip()]


# ---- Sidebar: personal data stays local ----
with st.sidebar:
    st.header("🔒 Stammdaten (lokal)")
    st.caption("Diese Daten verlassen das Gerät nicht. Das KI-Modell sieht nur die ID.")
    ss.name = st.text_input("Name des Teilnehmers", key="name_in")
    ss.dob = st.text_input("Geburtsdatum", key="dob_in")
    ss.staff = st.text_input("Beobachtende Fachkraft", key="staff_in")
    ss.start = st.text_input("Beginn", value=TODAY)
    ss.end = st.text_input("Ende", value=TODAY)
    st.info(f"Pseudonym für die KI: **{ss.pid}**")
    with st.expander("Das sieht die KI zuletzt"):
        st.code(ss.last_sent or "–")

st.title("📝 MAUS-Erhebungsbogen A – KI-Assistent")
tab1, tab2, tab3 = st.tabs(["1 · Interview", "2 · Prüfen & Freigeben", "3 · Eingliederungsplan & PDF"])

# ---- Tab 1: chat ----
with tab1:
    done = len(current_scores())
    st.progress(done / len(TRAITS), text=f"{done} von {len(TRAITS)} Merkmalen bewertet")
    for m in ss.history:
        with st.chat_message(m["role"]):
            st.write(m["content"])
    if text := st.chat_input("Ihre Beobachtung …"):
        clean = scrub(text, ss.get("name", ""), ss.pid)
        ss.last_sent = clean
        ss.history.append({"role": "user", "content": clean})
        try:
            reply, updates = llm.interview_turn(ss.history, current_scores(), ss.pid)
        except Exception as e:
            reply, updates = f"⚠️ {e}", []
        for u in updates:
            ss[f"s_{u['trait']}"] = u["score"]
            ss[f"e_{u['trait']}"] = u["evidence"]
        ss.history.append({"role": "assistant", "content": reply})
        st.rerun()

# ---- Tab 2: human review ----
with tab2:
    st.caption("KI-Vorschläge – bitte fachlich prüfen und bei Bedarf ändern. Rechts steht die DIK-2-Beschreibung zum gewählten Wert. "
               "Graue Felder des Bogens (nicht vergebbare Werte) sind nicht wählbar.")
    for section, traits in SECTIONS.items():
        st.subheader(section)
        for t in traits:
            c1, c2, c3 = st.columns([2, 1, 4])
            c1.markdown(f"**{t}**")
            ss.setdefault(f"s_{t}", "–")
            c2.selectbox(t, ["–"] + list(range(-3, MAX_SCORE[t] + 1)), key=f"s_{t}", label_visibility="collapsed")
            sc = score_of(t)
            if sc is not None:
                if ss.get(f"e_{t}"):
                    c3.caption(f"Begründung: {ss[f'e_{t}']}")
                with c3.expander("DIK-2-Beschreibung"):
                    st.write(dik_text(t, sc))
    ss.approved = st.checkbox("✅ Ich habe die Bewertungen fachlich geprüft und gebe sie frei.")

# ---- Tab 3: Eingliederungsplan ----
with tab3:
    scores = current_scores()
    if not scores:
        st.info("Noch keine Bewertungen vorhanden.")
    else:
        st.subheader("Angaben zum Plan")
        c1, c2, c3 = st.columns(3)
        kosten = c1.multiselect("Kostenträger", ep.KOSTENTRAEGER)
        ev_von = c2.text_input("Eingangsverfahren von")
        ev_bis = c3.text_input("Eingangsverfahren bis")
        c1, c2, c3 = st.columns(3)
        areas = c1.multiselect("Bereiche (max. 3)", AREAS, max_selections=3)
        begleiter = c2.text_input("Bildungsbegleiter")
        c3.write("")
        c1, c2, c3 = st.columns(3)
        erprobung = c1.radio("Betriebliche Erprobung im kommenden Jahr", ["–", "ja", "nein"], horizontal=True)
        fahrdienst = c2.radio("Fahrdienst", ["–", "ja", "nein"], horizontal=True)
        oepnv = c3.radio("Öffentlicher Personennahverkehr", ["–", "ja", "nein"], horizontal=True)
        c1, c2 = st.columns(2)
        bbb_von = c1.text_input("Teilnahme 1. Jahr Berufsbildungsbereich von")
        bbb_bis = c2.text_input("… bis")

        st.subheader("Analyse (KI-Vorschlag)")
        if st.button("✨ Kompetenzanalyse, Hemmende Faktoren und Ziele vorschlagen"):
            with st.spinner("KI erstellt Vorschlag …"):
                try:
                    f = llm.plan_fields(scores, {t: ss.get(f"e_{t}", "") for t in scores})
                    for k, v in f.items():
                        ss[f"p_{k}"] = "\n".join(f"- {x.replace(ss.pid, ss.get('name') or 'Er/Sie')}" for x in v)
                except Exception as e:
                    st.error(str(e))
        st.warning("Vorschlag der KI – die Entscheidung trifft die Fachkraft. Ein Stichpunkt pro Zeile.")
        st.text_area("Diagnosen (von der Fachkraft; wird nicht von der KI erstellt)", key="p_diagnosen", height=80)
        st.text_area("Kompetenzanalyse", key="p_kompetenz", height=140)
        st.text_area("Hemmende Faktoren", key="p_hemmend", height=160)
        st.text_area("Förderziele", key="p_ziele", height=180)
        st.text_area("Sonstiges", key="p_sonstiges", height=80)

        st.subheader("Export")
        if not ss.approved:
            st.info("PDF-Export erst nach Freigabe in Schritt 2.")
        else:
            d = {
                "name": ss.name, "geb": ss.dob, "kosten": {ep.norm(k) for k in kosten},
                "ev_von": ev_von, "ev_bis": ev_bis, "datum": TODAY,
                "diagnosen": bullets(ss.get("p_diagnosen", "")), "kompetenz": bullets(ss.get("p_kompetenz", "")),
                "hemmend": bullets(ss.get("p_hemmend", "")), "ziele": bullets(ss.get("p_ziele", "")),
                "bereich": (areas + ["", "", ""])[:3], "begleiter": begleiter,
                "erprobung": None if erprobung == "–" else erprobung,
                "fahrdienst": None if fahrdienst == "–" else fahrdienst,
                "oepnv": None if oepnv == "–" else oepnv,
                "sonstiges": bullets(ss.get("p_sonstiges", "")), "bbb_von": bbb_von, "bbb_bis": bbb_bis,
            }
            buf = io.BytesIO()
            ep.build(d, buf)
            meta = {k: ss.get(k) or "" for k in ("name", "dob", "staff", "start", "end")}
            c1, c2 = st.columns(2)
            c1.download_button("📄 Eingliederungsplan (PDF)", buf.getvalue(),
                               file_name="Eingliederungsplan.pdf", mime="application/pdf")
            c2.download_button("📄 MAUS-Erhebungsbogen A–F (PDF)", pdf_out.build_pdf(meta, scores),
                               file_name="MAUS-Erhebungsbogen-A.pdf", mime="application/pdf")
