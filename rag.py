"""Small retrieval layer: BM25 over DOKU reflections + the DIK-2 catalogue, plus per-client context.
No vector DB needed at this size (a few thousand chunks)."""
import math
import re
from collections import Counter

import data
import maus


def _tok(s):
    # crude German stemming: first 6 letters ("Konzentration" ~ "Konzentrationsspanne")
    return [w[:6] for w in re.findall(r"[a-zäöüß]{3,}", s.lower())]


class Index:
    def __init__(self, docs):
        self.docs = docs
        self.toks = [Counter(_tok(d["text"])) for d in docs]
        self.len = [sum(c.values()) for c in self.toks]
        self.avg = (sum(self.len) / len(docs)) if docs else 1
        df = Counter(t for c in self.toks for t in c)
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def search(self, query, k=4, kind=None):
        q = _tok(query)
        scored = []
        for i, c in enumerate(self.toks):
            if kind and self.docs[i]["kind"] != kind:
                continue
            s = sum(self.idf.get(t, 0) * c[t] * 2.2 / (c[t] + 1.2 * (0.25 + 0.75 * self.len[i] / self.avg))
                    for t in q if t in c)
            if s > 0:
                scored.append((s, i))
        return [self.docs[i] for _, i in sorted(scored, reverse=True)[:k]]


def build_index(doku):
    docs = list(maus.dik_chunks())
    for _, r in doku.iterrows():
        if not (r.get("Reflexion") or r.get("Beispiel/Ziel")):
            continue
        el = str(r["DOKU-Element"]).strip()
        docs.append({"kind": "doku", "kid": r["Klient ID"], "source": f"DOKU Klient {r['Klient ID']} · {el[:6].strip()}",
                     "text": f"{el}. Ziel: {r.get('Beispiel/Ziel', '')}. Reflexion: {r.get('Reflexion', '')}. "
                             f"{r.get('Erreicht/Nicht erreicht', '')}"})
    return Index(docs)


def client_context(kid, doku, att, clients):
    """Compact, pseudonymous summary of what is already documented for this client."""
    lines = []
    info = data.prefill(clients, kid)
    if info:
        row = clients[clients["Klient ID"] == kid].iloc[0]
        a = data.age(info["dob"])
        lines.append(f"Stammdaten: Status {info['status']}, Alter ca. {a}, Kostenträger {row.get('Kostenträger WfbM', '')}, "
                     f"Eintritt {info['ev_von']}, Fahrdienst {row.get('Fahrdienst', '')}.")
    d = doku[doku["Klient ID"] == kid] if len(doku) else doku
    if len(d):
        done = int((d["Erreicht/Nicht erreicht"].str.lower() == "erreicht").sum())
        lines.append(f"DOKU-Bogen: {len(d)} Elemente, davon {done} erreicht.")
        for _, r in d.iterrows():
            if r["Reflexion"]:
                lines.append(f"- {str(r['DOKU-Element'])[:6].strip()} (Stufe {r['Stufe']}, {r['Erreicht/Nicht erreicht'] or 'offen'}): "
                             f"{r['Reflexion'][:220]}")
    if len(att):
        a_ = att[att["Klient ID"] == kid]
        filled = int((a_["Angaben/Auswahl"].str.strip() != "").sum())
        lines.append(f"Anwesenheit: {filled} von {len(a_)} Einträgen erfasst." if len(a_) else "Anwesenheit: keine Daten.")
    return "\n".join(lines) or "Keine Vordokumentation vorhanden."


def build_context(kid, query, index, doku, att, clients, k=5):
    """Context block for the LLM: client summary + top-k sources for the specialist's latest message."""
    hits = (index.search(query, k - 1, "doku") + index.search(query, 2, "dik")) if query.strip() else []
    ctx = "Vordokumentation dieses Klienten:\n" + client_context(kid, doku, att, clients)
    if hits:
        ctx += "\n\nRelevante Quellen (zitiere sie als [Quelle]):\n" + "\n".join(
            f"[{h['source']}] {h['text'][:450]}" for h in hits)
    return ctx, hits
