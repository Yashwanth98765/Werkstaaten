"""Loads the workshop Excel exports (DOKU-Bogen, Anwesenheit, Klienten) from data/ (real) or sample_data/ (synthetic)."""
from datetime import date, datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent


def data_dir() -> Path:
    real = ROOT / "data"
    return real if real.exists() and any(real.glob("*.xls*")) else ROOT / "sample_data"


def load():
    """Returns (doku, attendance, clients) DataFrames. Each file is recognised by its columns."""
    parts = {"doku": [], "att": [], "clients": []}
    for f in sorted(data_dir().glob("*.xls*")):
        if f.name.startswith("~$"):
            continue
        for df in pd.read_excel(f, sheet_name=None, dtype=str).values():
            df.columns = [str(c).strip() for c in df.columns]
            df = df.fillna("")
            cols = set(df.columns)
            if {"Reflexion", "DOKU-Element"} <= cols:
                parts["doku"].append(df)
            elif "DOKU-Element Id" in cols:
                parts["att"].append(df)
            elif "Eintritt WfbM" in cols:
                parts["clients"].append(df)
    cat = lambda l: pd.concat(l, ignore_index=True) if l else pd.DataFrame()
    return cat(parts["doku"]), cat(parts["att"]), cat(parts["clients"])


def fmt_date(v) -> str:
    v = str(v).strip()
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(v, f).strftime("%d.%m.%Y")
        except ValueError:
            pass
    return v


def age(dob: str):
    try:
        b = datetime.strptime(fmt_date(dob), "%d.%m.%Y").date()
    except ValueError:
        return None
    t = date.today()
    return t.year - b.year - ((t.month, t.day) < (b.month, b.day))


def kosten_name(raw: str) -> str:
    """Excel Kostenträger -> option of the Eingliederungsplan checkbox list."""
    r = raw.lower()
    if "unterfranken" in r:
        return "Bezirk Unterfranken"
    if "bezirk" in r:  # other Bezirke (Mittelfranken, Oberpfalz, ...) are not Bezirk Unterfranken
        return "Andere Kostenträger"
    if "arbeit" in r:
        return "Agentur für Arbeit"
    if "nordbayern" in r:
        return "DRV Nordbayern"
    if "drv" in r or "rentenversicherung" in r:
        return "DRV Bund"
    return "Andere Kostenträger" if r else ""


def prefill(clients: pd.DataFrame, kid: str) -> dict:
    """Header data for the Eingliederungsplan from the client master data."""
    row = clients[clients["Klient ID"] == kid]
    if row.empty:
        return {}
    r = row.iloc[0]
    fahr = str(r.get("Fahrdienst", "")).strip().lower()
    return {
        "dob": fmt_date(r.get("Geburtsdatum", "")),
        "kosten": kosten_name(str(r.get("Kostenträger WfbM", ""))),
        "ev_von": fmt_date(r.get("Eintritt WfbM", "")),
        "status": str(r.get("Klientenstatus WfbM", "")),
        "fahrdienst": "nein" if fahr.startswith("selbst") else "ja" if fahr.startswith("tour") else "–",
    }
