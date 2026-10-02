"""#358 TEI: Dreissiger und Buchgrenzen des Parzival in PZ und WH auszeichnen.

1. `subtype="dreissiger"` an jedem `div type="chapter"` in tei/PZ.tei.xml und
   tei/WH.tei.xml (nirgends sonst). Vorab gemessen: in beiden Dateien ist jedes
   div ein chapter ohne weitere Attribute ausser @n, @n laeuft lueckenlos von 1.
2. `<milestone unit="book" n="I"/>` bis `XVI` in PZ, als direktes Kind des
   chapter-div, unmittelbar vor dem `<l>`, das die `erste_wort_id` der Zeile
   aus ingest/parzival-buecher/grenzen.csv traegt. Nie in einem `lg`.

Haltepunkte (harter Abbruch, nichts geschrieben): ein `lg` in PZ, eine Grenze,
deren Wort-ID fehlt, deren `<l>` nicht direktes Kind eines chapter-div ist oder
deren `<l>`-Startzeile nicht eindeutig im Text zu finden ist.

SCHREIBWEISE: exakte Ersetzung auf dem gelesenen Text (newline=''), kein lxml-
Schreiben; lxml findet nur die Ziele und prueft das Ergebnis. Beide Dateien sind
reine LF-Dateien, das wird vor und nach dem Lauf gezaehlt.

Aufruf:
    python scripts/ingest/parzival-358/pz-wh-struktur.py            # Trockenlauf
    python scripts/ingest/parzival-358/pz-wh-struktur.py --apply    # schreibt
"""
import csv
import re
import sys
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[3]
TEI = "{http://www.tei-c.org/ns/1.0}"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"
GRENZEN = ROOT / "ingest" / "parzival-buecher" / "grenzen.csv"
APPLY = "--apply" in sys.argv
sys.stdout.reconfigure(encoding="utf-8")


def abbruch(msg):
    sys.exit(f"ABBRUCH: {msg}")


def zeilenenden(data):
    crlf = data.count(b"\r\n")
    return crlf, data.count(b"\n") - crlf


def roemisch(n):
    out = ""
    for wert, zeichen in [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]:
        while n >= wert:
            out += zeichen
            n -= wert
    return out


DIV_TAG = re.compile(r'<div type="chapter" n="(\d+)">')

ergebnis = {}
for sigle in ("PZ", "WH"):
    pfad = ROOT / "tei" / f"{sigle}.tei.xml"
    roh = pfad.read_bytes()
    zeilenenden_vor = zeilenenden(roh)
    if zeilenenden_vor[0] != 0:
        abbruch(f"{sigle} ist keine reine LF-Datei {zeilenenden_vor}")
    text = roh.decode("utf-8")
    body = etree.fromstring(roh).find(f".//{TEI}body")
    divs = list(body.iter(f"{TEI}div"))
    if any(d.get("type") != "chapter" or d.get("subtype") or set(d.attrib) != {"type", "n"} for d in divs):
        abbruch(f"{sigle}: ein div ist kein reines chapter mit @n")
    if len(DIV_TAG.findall(text)) != len(divs):
        abbruch(f"{sigle}: {len(DIV_TAG.findall(text))} div-Startzeilen im Text, {len(divs)} im Baum")
    if list(body.iter(f"{TEI}lg")):
        abbruch(f"{sigle}: lg vorhanden, vor A3 melden")
    if list(body.iter(f"{TEI}milestone")):
        abbruch(f"{sigle}: milestone schon vorhanden")
    ziele = []   # (div_n, l_n, buch)
    if sigle == "PZ":
        with open(GRENZEN, encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh, delimiter=";"))
        if len(rows) != 16:
            abbruch(f"grenzen.csv hat {len(rows)} Zeilen statt 16")
        ids = {w.get(XMLID): w for w in body.iter(f"{TEI}w")}
        for r in rows:
            w = ids.get(r["erste_wort_id"])
            if w is None:
                abbruch(f"{r['buch']}: Wort-ID {r['erste_wort_id']} fehlt")
            l = next((a for a in w.iterancestors() if a.tag == f"{TEI}l"), None)
            if l is None or l.getparent().tag != f"{TEI}div" or l.getparent().get("type") != "chapter":
                abbruch(f"{r['buch']}: <l> ist kein direktes Kind eines chapter-div")
            ziele.append((l.getparent().get("n"), l.get("n"), r["buch"].replace("Buch ", "")))
        if [z[2] for z in ziele] != [roemisch(i) for i in range(1, 17)]:
            abbruch("Buchfolge in grenzen.csv ist nicht I bis XVI")

    # --- Text bearbeiten
    neu = DIV_TAG.sub(lambda m: f'<div type="chapter" subtype="dreissiger" n="{m.group(1)}">', text)
    n_sub = len(divs)
    n_ms = 0
    for div_n, l_n, buch in ziele:
        start = neu.find(f'<div type="chapter" subtype="dreissiger" n="{div_n}">')
        if start < 0 or neu.count(f'subtype="dreissiger" n="{div_n}">') != 1:
            abbruch(f"{sigle}: div n={div_n} nicht eindeutig")
        m = re.compile(rf'^( *)<l n="{l_n}">\n', re.M).search(neu, start)
        if m is None:
            abbruch(f"{sigle}: <l n={l_n}> nach div {div_n} nicht gefunden")
        # kein weiteres div zwischen div-Start und <l>
        if "<div " in neu[start + 10:m.start()]:
            abbruch(f"{sigle}: <l n={l_n}> liegt nicht im div {div_n}")
        neu = neu[:m.start()] + f'{m.group(1)}<milestone unit="book" n="{buch}"/>\n' + neu[m.start():]
        n_ms += 1
    ergebnis[sigle] = (pfad, roh, neu, n_sub, n_ms, ziele)
    print(f"{sigle}: {n_sub} div bekommen subtype, {n_ms} milestone")

# --- Pruefung des Ergebnisses am Baum (vor dem Schreiben, aus dem Text)
for sigle, (pfad, roh, neu, n_sub, n_ms, ziele) in ergebnis.items():
    wurzel = etree.fromstring(neu.encode("utf-8"))
    body = wurzel.find(f".//{TEI}body")
    divs = list(body.iter(f"{TEI}div"))
    if not all(d.get("subtype") == "dreissiger" for d in divs):
        abbruch(f"{sigle}: nicht jedes div traegt subtype")
    mss = list(body.iter(f"{TEI}milestone"))
    if len(mss) != n_ms:
        abbruch(f"{sigle}: {len(mss)} milestone im Ergebnis, erwartet {n_ms}")
    for ms, (div_n, l_n, buch) in zip(mss, ziele):
        nxt = ms.getnext()
        if (ms.getparent().tag != f"{TEI}div" or ms.getparent().get("n") != div_n
                or nxt is None or nxt.tag != f"{TEI}l" or nxt.get("n") != l_n
                or ms.get("unit") != "book" or ms.get("n") != buch or len(ms) or ms.tail.strip()):
            abbruch(f"{sigle}: milestone {buch} sitzt nicht richtig")
    # alles andere unveraendert: <w>-Folge und Text identisch
    alt = etree.fromstring(roh).find(f".//{TEI}body")
    if [(w.get(XMLID), "".join(w.itertext())) for w in alt.iter(f"{TEI}w")] != \
       [(w.get(XMLID), "".join(w.itertext())) for w in body.iter(f"{TEI}w")]:
        abbruch(f"{sigle}: <w>-Folge hat sich veraendert")
    print(f"{sigle}: Pruefung am Ergebnis bestanden")

if not APPLY:
    print("\nTrockenlauf, nichts geschrieben. Mit --apply schreiben.")
    sys.exit(0)

for sigle, (pfad, roh, neu, n_sub, n_ms, ziele) in ergebnis.items():
    neu_roh = neu.encode("utf-8")
    if zeilenenden(neu_roh) != (0, zeilenenden(roh)[1] + n_ms):
        abbruch(f"{sigle}: Zeilenenden weichen ab, nichts geschrieben")
    with open(pfad, "wb") as fh:
        fh.write(neu_roh)
    print(f"geschrieben: {pfad.name}: {n_sub} subtype, {n_ms} milestone, LF {zeilenenden(roh)[1]} -> {zeilenenden(neu_roh)[1]}")
