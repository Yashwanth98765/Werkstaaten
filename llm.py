"""LLM calls (OpenAI-compatible: Groq or xAI Grok). Configure in .env."""
import json
import os

import requests
from dotenv import load_dotenv

from maus import MAX_SCORE, SECTIONS, TRAITS, dik_text

load_dotenv()
API_KEY = os.getenv("LLM_API_KEY", "")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")  # xAI: https://api.x.ai/v1
MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")


def _call(messages, json_mode=False, temperature=0.2):
    if not API_KEY:
        raise RuntimeError("LLM_API_KEY fehlt – bitte in .env eintragen.")
    body = {"model": MODEL, "messages": messages, "temperature": temperature}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    r = requests.post(f"{BASE_URL}/chat/completions", json=body, timeout=60,
                      headers={"Authorization": f"Bearer {API_KEY}"})
    if not r.ok:
        raise RuntimeError(f"LLM-Fehler {r.status_code}: {r.text[:300]}")
    return r.json()["choices"][0]["message"]["content"]


LIMITS = ", ".join(f"{t} (max. {m:+d})" for t, m in MAX_SCORE.items() if m < 3)
GROUPS = "\n".join(f"- {k}: {', '.join(v)}" for k, v in SECTIONS.items())

INTERVIEW_SYSTEM = f"""Du bist ein freundlicher Assistent für Fachkräfte der Mainfränkischen Werkstätten.
Du führst ein kurzes Interview, um den MAUS-Erhebungsbogen A (Arbeits- und Sozialverhalten) auszufüllen.
Skala je Merkmal: -3 (starke Beeinträchtigung) … 0 (durchschnittlich/unauffällig) … +3 (ausgeprägte Stärke).
Merkmale nach Gruppen:
{GROUPS}
Höchstwerte (graue Felder im Bogen): {LIMITS}.

Regeln:
- Frage nach konkreten Beobachtungen, jeweils zu 2-4 thematisch zusammengehörigen offenen Merkmalen, in einfachem Deutsch, max. 3 Sätze.
- Wenn die Fachkraft viel auf einmal erzählt, bewerte alle Merkmale, für die die Aussagen ausreichen.
- Vergib eine Bewertung nur, wenn die Aussagen dafür ausreichen; sonst frage nach.
- Die Fachkraft entscheidet final – deine Werte sind Vorschläge.
- Frage niemals nach Namen oder Geburtsdatum. Der Teilnehmer heißt nur mit der ID, die du bekommst.
Antworte AUSSCHLIESSLICH als JSON:
{{"reply": "<deine nächste Frage/Antwort>", "updates": [{{"trait": "<Merkmal exakt wie oben>", "score": <int>, "evidence": "<kurze Begründung aus den Aussagen>"}}]}}
"updates" ist leer, wenn keine neue Bewertung möglich ist."""


def interview_turn(history, current, pseudonym):
    """history: [{role, content}] (already pseudonymized). current: {trait: score}."""
    open_traits = [t for t in TRAITS if t not in current]
    state = f"Teilnehmer-ID: {pseudonym}. Bereits bewertet: {current or 'nichts'}. Noch offen: {open_traits or 'nichts – bedanke dich und verweise auf die Prüfung'}."
    raw = _call([{"role": "system", "content": INTERVIEW_SYSTEM + "\n\n" + state}] + history, json_mode=True)
    data = json.loads(raw)
    updates = []
    for u in data.get("updates", []):
        t = u.get("trait")
        if t in TRAITS and isinstance(u.get("score"), int):
            updates.append({"trait": t, "score": max(-3, min(MAX_SCORE[t], u["score"])),
                            "evidence": str(u.get("evidence", ""))})
    return data.get("reply", ""), updates


def plan_fields(scores, evidence):
    """Draft the Eingliederungsplan text fields from MAUS scores + DIK-2 descriptions.
    Returns {"kompetenz": [...], "hemmend": [...], "ziele": [...], "sonstiges": [...]} (lists of bullet strings)."""
    lines = [f"- {t}: {s:+d}" + (f" ({evidence[t]})" if evidence.get(t) else "") for t, s in scores.items()]
    weak = sorted((t for t, s in scores.items() if s <= -1), key=lambda t: scores[t])[:8]
    strong = [t for t, s in scores.items() if s >= 1]
    prompt = f"""MAUS-Bewertungen einer Person:
{chr(10).join(lines)}

Stärken (Wert >= +1): {', '.join(strong) or 'keine'}

Schwächen laut DIK-2-Katalog (Wert <= -1):
{chr(10).join(f"- {t} ({scores[t]:+d}): {dik_text(t, scores[t], 300)}" for t in weak) or 'keine'}

Schreibe für das Formular „Eingliederungsplan" auf Deutsch, in einfacher Sprache, als Vorschlag für die Fachkraft.
Sprich von „Er/Sie" – nenne keinen Namen und keine ID. Nutze nur die Informationen oben, erfinde keine Diagnosen.
Antworte AUSSCHLIESSLICH als JSON mit diesen Listen (jeder Eintrag ein vollständiger Stichpunkt, ohne Aufzählungszeichen):
{{"kompetenz": ["<2-5 Stichpunkte: Stärken und Fähigkeiten>"],
 "hemmend": ["<2-6 Stichpunkte: hemmende Faktoren, bezogen auf die Schwächen>"],
 "ziele": ["<2-3 konkrete, überprüfbare Förderziele, je mit passender Fördermaßnahme: 'Ziel: … – Maßnahme: …'>"],
 "sonstiges": ["<0-2 Hinweise zur weiteren Planung, z. B. betriebliche Erprobung, falls passend>"]}}"""
    raw = _call([
        {"role": "system", "content": "Du unterstützt Fachkräfte bei der Förderplanung. Du machst nur Vorschläge; die Entscheidung trifft die Fachkraft."},
        {"role": "user", "content": prompt}], json_mode=True, temperature=0.3)
    data = json.loads(raw)
    return {k: [str(x) for x in data.get(k, []) if str(x).strip()] for k in ("kompetenz", "hemmend", "ziele", "sonstiges")}
