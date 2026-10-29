"""Pseudonymization: real names/birthdates never go to the LLM."""
import re


def scrub(text: str, name: str, pseudonym: str) -> str:
    for part in {p for p in re.split(r"[\s,]+", name or "") if len(p) > 1}:
        text = re.sub(re.escape(part), pseudonym, text, flags=re.I)
    return re.sub(r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b", "[Datum]", text)
