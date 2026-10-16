#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sammelt alle Korpusbelege der 25 Lemmata aus #462 (22 Widersprueche + 3 Gleichstaende).

Aufruf (der Ausgabeordner ist Pflicht und darf nicht im Repo liegen, ausser unter
temp/, das gitignoriert ist; die Wurzel ist optional, Standard: dieses Repositorium):
    python scripts/review/collect-462-pos.py <ausgabeordner> [repo-wurzel]

Schreibt belege.tsv, lexikon.json und zaehlung.txt in den Ausgabeordner; im Repo wird
nichts geaendert. Davon liegt belege.tsv in ingest/pos-disambig/462-pos/; lexikon.json
und zaehlung.txt sind regenerierbar. Wer belege.tsv erneuern will, vergleicht und
kopiert bewusst. vorschlaege.tsv ist die Lesung eines Agenten und wird hier nicht
erzeugt.
"""
import sys, os, json, re, glob, collections
from lxml import etree

# cp1252-Konsole unter Windows: die Zaehlung am Ende enthaelt Umlaute und Zirkumflexe
sys.stdout.reconfigure(encoding="utf-8")

_HIER = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) < 2:
    sys.exit("FEHLER: Ausgabeordner fehlt. Aufruf: collect-462-pos.py <ausgabeordner> [repo-wurzel]")
OUT = sys.argv[1]
REPO = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.dirname(_HIER))
_o, _r = os.path.realpath(OUT), os.path.realpath(REPO)
if (_o == _r or _o.startswith(_r + os.sep)) and not _o.startswith(os.path.join(_r, "temp") + os.sep):
    sys.exit("FEHLER: Ausgabeordner liegt im Repo (erlaubt nur unter temp/): " + OUT)
os.makedirs(OUT, exist_ok=True)
IDS = """17456 21642 28722 35938 36303 36513 36569 36619 39197 40349 48265 48743 52645
54948 54949 55290 62410 67668 67689 67708 70735 78454 23289 24478 29486""".split()
IDS = ["lemma_" + i for i in IDS]
NS = {"t": "http://www.tei-c.org/ns/1.0"}
XML = "{http://www.w3.org/XML/1998/namespace}id"
T = "{http://www.tei-c.org/ns/1.0}"

# --- Lexikon ---
lex = {}
ctx = etree.iterparse(os.path.join(REPO, "authority-files", "lexicon.xml"), tag=T + "entry", huge_tree=True)
for _, e in ctx:
    i = e.get(XML)
    if i in IDS:
        lex[i] = {
            "orth": [o.text for o in e.iterfind(".//t:form[@type='lemma']/t:orth", NS)],
            "pos": [p.text for p in e.iterfind("t:gramGrp/t:pos", NS)],
            "etym": [(s.get("corresp"), s.text) for s in e.iterfind(".//t:etym/t:seg", NS)],
            "senses": [{"id": s.get(XML), "ana": s.get("ana"),
                        "concepts": [p.get("target").split("#")[-1] for p in s.iterfind("t:ptr", NS)]}
                       for s in e.iterfind("t:sense", NS)],
        }
    e.clear()
missing = [i for i in IDS if i not in lex]
if missing:
    sys.exit("FEHLER: nicht im Lexikon: %s" % missing)

# Konzeptnamen
# Konzeptnamen: nur IDs (Namen separat nachgeschlagen).

# --- Korpus ---
def text_of(el):
    return "".join(el.itertext()).strip()

def toks(body):
    return [x for x in body.iter(T + "w", T + "pc")]

rows = []
total_w_outside_body = collections.Counter()
files = sorted(glob.glob(os.path.join(REPO, "tei", "*.tei.xml")))
assert len(files) > 600, len(files)
for f in files:
    raw = open(f, encoding="utf-8").read()
    if not any(i in raw for i in IDS):
        continue
    sigle = os.path.basename(f).replace(".tei.xml", "")
    root = etree.fromstring(raw.encode("utf-8"), etree.XMLParser(huge_tree=True))
    body = root.find(".//t:body", NS)
    # auch ausserhalb body zaehlen (Kontrolle)
    for w in root.iter(T + "w"):
        ref = w.get("lemmaRef")
        if not ref:
            continue
        parts = [p.split("#")[-1] for p in ref.split()]
        for i in IDS:
            if i in parts and not any(a is body for a in w.iterancestors()):
                total_w_outside_body[i] += 1
    if body is None:
        continue
    seq = toks(body)
    idx = {id(x): n for n, x in enumerate(seq)}
    for n, w in enumerate(seq):
        if w.tag != T + "w":
            continue
        ref = w.get("lemmaRef")
        if not ref:
            continue
        parts = [p.split("#")[-1] for p in ref.split()]
        for i in IDS:
            if i not in parts:
                continue
            lo, hi = max(0, n - 8), min(len(seq), n + 9)
            def tx(x):
                return text_of(x)
            before = " ".join(tx(x) for x in seq[lo:n])
            after = " ".join(tx(x) for x in seq[n + 1:hi])
            line = ""
            for a in w.iterancestors():
                if a.tag in (T + "l", T + "p", T + "ab", T + "head", T + "item", T + "seg"):
                    line = " ".join(tx(x) for x in a.iter(T + "w", T + "pc"))
                    break
            rows.append({
                "lemma_id": i, "sigle": sigle, "xml_id": w.get(XML), "pos": w.get("pos") or "",
                "ana": (w.get("ana") or "").replace("lexicon.xml#", ""),
                "form": text_of(w), "reason": w.get("reason") or "",
                "mehrfach_lemma": "ja" if len(parts) > 1 else "",
                "kontext": (before + " [[" + text_of(w) + "]] " + after).strip(),
                "vers": line,
            })

def esc(s):
    return re.sub(r"[\t\r\n]+", " ", s or "")

rows.sort(key=lambda r: (IDS.index(r["lemma_id"]), r["sigle"], r["xml_id"]))
cols = ["lemma_id", "sigle", "xml_id", "pos", "ana", "form", "reason", "mehrfach_lemma", "kontext", "vers"]
with open(os.path.join(OUT, "belege.tsv"), "w", encoding="utf-8", newline="") as fh:
    fh.write("\t".join(cols) + "\n")
    for r in rows:
        fh.write("\t".join(esc(r[c]) for c in cols) + "\n")
json.dump(lex, open(os.path.join(OUT, "lexikon.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

with open(os.path.join(OUT, "zaehlung.txt"), "w", encoding="utf-8") as fh:
    fh.write("Dateien: %d; Belege (w im body mit lemmaRef-Token): %d\n" % (len(files), len(rows)))
    for i in IDS:
        rs = [r for r in rows if r["lemma_id"] == i]
        c = collections.Counter(r["pos"] or "(leer)" for r in rs)
        parts = collections.Counter()
        for r in rs:
            for p in set(r["pos"].split()):
                parts[p or "(leer)"] += 1
        fh.write("%s %s lex=%s | n=%d | roh=%s | teile=%s | ausserhalb_body=%d\n" % (
            i, "/".join(lex[i]["orth"]), ",".join(lex[i]["pos"]), len(rs), dict(c), dict(parts), total_w_outside_body[i]))
print(open(os.path.join(OUT, "zaehlung.txt"), encoding="utf-8").read())
