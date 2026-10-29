"""One-off: parse DIK-2 PDF into dik2.json -> {FEATURE: {score: description}}"""
import re, json, pypdf
r = pypdf.PdfReader("fb-f312-dik-2.pdf")
t = "\n".join(p.extract_text() or "" for p in r.pages)
pat = re.compile(r'^([A-ZÄÖÜ][A-ZÄÖÜ\-/ ,\.]+?) \(([-+]?\d)\)\s*$', re.M)
ms = list(pat.finditer(t))
d = {}
for i, m in enumerate(ms):
    end = ms[i + 1].start() if i + 1 < len(ms) else len(t)
    body = re.sub(r'DIK-2 [^\n]*Seite \d+\s*\n', '', t[m.end():end]).strip()
    d.setdefault(m.group(1).strip(), {})[m.group(2).lstrip('+')] = body[:1500]
json.dump(d, open("dik2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(d), "features")
