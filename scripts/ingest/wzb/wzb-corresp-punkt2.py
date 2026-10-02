"""#370 Punkt 2: die entschiedenen Paare aus C1 in tei/WZB.tei.xml einspielen.

Eingabe: ingest/wzb/370-corresp/entscheidungen.csv und
entscheidungen-nachtrag.csv. Eingespielt wird nur
  ANLEGEN      neuer Variantentyp (type_N ab dem naechsten freien), alle Tokens
               des Paars (kleingeschriebene NFC-Schreibung + erstes Lemma) ohne
               @corresp bekommen ihn;
  VERKNUEPFEN  der Typ existiert schon unter dem Lemma (steht in der
               Begruendung, wird gegen variants.xml gemessen), nur @corresp.
PRUEFSEITE und NICHT_ANLEGEN werden nicht angefasst, ein anderes Vokabular
(z. B. ANDERE_ZUORDNUNG) ist ein harter Fehler. Neue Typen werden gepraegt,
nie umgehaengt (#367): kein bestehendes @corresp wird veraendert.

Batch-Validierung VOR dem Schreiben (Abbruch bei jeder Abweichung):
  - jede Zeile hat eine Begruendung, kein Paar kommt doppelt vor
  - jedes Paar hat heute mindestens ein Token ohne @corresp; die Tokenzahl
    wird gegen die CSV gehalten und jede Abweichung ausgegeben
  - ANLEGEN: unter dem Lemma gibt es keinen Typ mit derselben normalisierten
    Form (sonst waere es VERKNUEPFEN); das Lemma steht in lexicon.xml
  - VERKNUEPFEN: der genannte Typ steht in variants.xml unter diesem Lemma
    und traegt dieselbe normalisierte Form
  - Ziel-Tokens mit mehr als einem Lemma in @lemmaRef werden gemeldet
    (Schluessel ist das erste Lemma, wie in Punkt 1)

SCHREIBWEISE wie in wzb-corresp-apply.py: exakte Byte-Ersetzung auf dem
gelesenen Text, newline='' und kein lxml-Schreiben; Zeilenenden vorher und
nachher gezaehlt, der revisionDesc-Eintrag bringt genau eine CRLF-Zeile.

Aufruf:
    python scripts/ingest/wzb/wzb-corresp-punkt2.py            # Trockenlauf
    python scripts/ingest/wzb/wzb-corresp-punkt2.py --apply    # schreibt WZB
"""
import csv
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from corpus_files import corpus_files  # noqa: E402

TEI = "{http://www.tei-c.org/ns/1.0}"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"
WZB = ROOT / "tei" / "WZB.tei.xml"
VARIANTS = ROOT / "authority-files" / "variants.xml"
LEXICON = ROOT / "authority-files" / "lexicon.xml"
DIR = ROOT / "ingest" / "wzb" / "370-corresp"
DATEIEN = ["entscheidungen.csv", "entscheidungen-nachtrag.csv"]
EINSPIELEN = {"ANLEGEN", "VERKNUEPFEN"}
NICHT_ANFASSEN = {"PRUEFSEITE", "NICHT_ANLEGEN"}
TYP_IN_BEGR = re.compile(r"Der Typ existiert schon: (type_\d+) unter (lemma_\d+)")
TYPE_NUM = re.compile(r"type_(\d+)")

APPLY = "--apply" in sys.argv
sys.stdout.reconfigure(encoding="utf-8")  # Schreibungen mit ŏ, Konsole ist cp1252


def key_form(text):
    return unicodedata.normalize("NFC", text).lower()


def first_lemma(w):
    ref = w.get("lemmaRef")
    return ref.split()[0].split("#")[-1] if ref else None


def fehler(msg):
    sys.exit(f"ABBRUCH: {msg}")


# ------------------------------------------------------------ 1. Entscheidungen
zeilen = []
for name in DATEIEN:
    with open(DIR / name, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            r["_datei"] = name
            zeilen.append(r)

bekannt = EINSPIELEN | NICHT_ANFASSEN
paare = {}
for r in zeilen:
    if r["entscheidung"] not in bekannt:
        fehler(f"{r['_datei']}: unbekannte Entscheidung {r['entscheidung']!r} "
               f"bei {r['schreibung']}/{r['lemma']}")
    if not r["begruendung"].strip():
        fehler(f"{r['_datei']}: ohne Begruendung: {r['schreibung']}/{r['lemma']}")
    k = (key_form(r["schreibung"]), r["lemma"])
    if k in paare:
        fehler(f"Paar doppelt ueber beide Dateien: {k}")
    paare[k] = r

todo = {k: r for k, r in paare.items() if r["entscheidung"] in EINSPIELEN}
print("Entscheidungen:", dict(Counter((r["_datei"], r["entscheidung"]) for r in zeilen)))
print(f"einzuspielen: {len(todo)} Paare "
      f"({sum(1 for r in todo.values() if r['entscheidung'] == 'ANLEGEN')} ANLEGEN, "
      f"{sum(1 for r in todo.values() if r['entscheidung'] == 'VERKNUEPFEN')} VERKNUEPFEN)")

# --------------------------------------------------------------- 2. Authority
var_root = etree.parse(str(VARIANTS)).getroot()
type_info = {}                   # type_id -> (lemma, form)
lemma_forms = defaultdict(dict)  # lemma -> {normalisierte Form: [type_id, ...]}
for entry in var_root.iter(f"{TEI}entry"):
    lemma = (entry.get("corresp") or "").split("#")[-1]
    for form in entry.iter(f"{TEI}form"):
        tid = form.get(XMLID)
        text = "".join(form.itertext()).strip()
        type_info[tid] = (lemma, text)
        lemma_forms[lemma].setdefault(key_form(text), []).append(tid)

lex_root = etree.parse(str(LEXICON)).getroot()
lemma_ids = {e.get(XMLID) for e in lex_root.iter(f"{TEI}entry") if e.get(XMLID)}

# -------------------------------------------------------------- 3. Ziel-Tokens
body = etree.parse(str(WZB)).find(f".//{TEI}body")
ziele = defaultdict(list)   # paar -> [xml_id]
mehrlemma = 0
ohne_corresp_gesamt = 0
for w in body.iter(f"{TEI}w"):
    lemma = first_lemma(w)
    if not lemma or w.get("corresp"):
        continue
    text = "".join(w.itertext()).strip()
    if not text:
        continue
    ohne_corresp_gesamt += 1
    k = (key_form(text), lemma)
    if k in todo:
        ziele[k].append(w.get(XMLID))
        if len(w.get("lemmaRef").split()) > 1:
            mehrlemma += 1
print(f"WZB heute: {ohne_corresp_gesamt:,} lemmatisierte Tokens ohne @corresp")

# Hoechste vergebene type-ID: variants.xml, alle @corresp im Korpus, lexicon.
hoechste = max(int(m.group(1)) for t in type_info if (m := TYPE_NUM.fullmatch(t)))
for path in corpus_files(ROOT / "tei"):
    for corresp in re.findall(r'corresp="([^"]*)"', path.read_text(encoding="utf-8")):
        for m in re.finditer(r"variants\.xml#type_(\d+)", corresp):
            hoechste = max(hoechste, int(m.group(1)))
for m in re.finditer(r"#type_(\d+)", LEXICON.read_text(encoding="utf-8")):
    hoechste = max(hoechste, int(m.group(1)))
print(f"hoechste vergebene type-ID: type_{hoechste}")

# ----------------------------------------------------------- 4. Batch-Pruefung
abweichend = []
zuordnung = []   # (paar, typ, entscheidung, [xml_id])
naechste = hoechste + 1
for k in sorted(todo, key=lambda p: (todo[p]["_datei"], p)):
    r = todo[k]
    ids = ziele.get(k, [])
    if not ids:
        fehler(f"{k}: kein Token ohne @corresp mehr")
    if len(ids) != int(r["tokens"]):
        abweichend.append((k, int(r["tokens"]), len(ids), r["_datei"]))
    if r["lemma"] not in lemma_ids:
        fehler(f"{k}: Lemma steht nicht in lexicon.xml")
    vorhanden = lemma_forms.get(r["lemma"], {}).get(k[0], [])
    if r["entscheidung"] == "ANLEGEN":
        if vorhanden:
            fehler(f"{k}: ANLEGEN, aber {vorhanden} existiert schon unter dem Lemma")
        typ = f"type_{naechste}"
        naechste += 1
    else:
        m = TYP_IN_BEGR.search(r["begruendung"])
        if not m or m.group(2) != r["lemma"]:
            fehler(f"{k}: VERKNUEPFEN ohne lesbaren Typ in der Begruendung")
        typ = m.group(1)
        if type_info.get(typ, (None,))[0] != r["lemma"]:
            fehler(f"{k}: {typ} steht nicht unter {r['lemma']} in variants.xml")
        if key_form(type_info[typ][1]) != k[0]:
            fehler(f"{k}: {typ} traegt die Form {type_info[typ][1]!r}")
        if len(vorhanden) > 1:
            print(f"  Hinweis: {k} hat {len(vorhanden)} Typen gleicher Form {vorhanden}, "
                  f"gewaehlt laut CSV: {typ}")
    zuordnung.append((k, typ, r["entscheidung"], ids, r["_datei"]))

soll = sum(len(z[3]) for z in zuordnung)
print(f"Soll: {soll:,} Tokens in {len(zuordnung)} Paaren, "
      f"neue Typen: type_{hoechste + 1}..type_{naechste - 1} "
      f"({naechste - hoechste - 1})")
for d in DATEIEN:
    ts = sum(len(z[3]) for z in zuordnung if z[4] == d)
    print(f"  {d}: {sum(1 for z in zuordnung if z[4] == d)} Paare, {ts} Tokens")
print(f"Tokens, deren @lemmaRef mehrere Lemmata nennt: {mehrlemma}")
print(f"Abweichungen Tokenzahl CSV gegen heute: {len(abweichend)}")
for k, csv_n, heute, d in abweichend:
    print(f"  {k} {d}: CSV {csv_n}, heute {heute}")
if len({i for z in zuordnung for i in z[3]}) != soll:
    fehler("ein Token waere in zwei Paaren")

# Provenienz: eine Zeile je Token, vorab bestimmt
log = DIR / "punkt2-zuordnung.csv"

if not APPLY:
    print("\nTrockenlauf, nichts geschrieben. Mit --apply schreiben.")
    sys.exit(0)

# ----------------------------------------------------------------- 5. Schreiben
ziel_typ = {i: z[1] for z in zuordnung for i in z[3]}
roh = WZB.read_bytes()


def zeilenenden(data):
    crlf = data.count(b"\r\n")
    return crlf, data.count(b"\n") - crlf


crlf_vor, lf_vor = zeilenenden(roh)
print(f"\nZeilenenden vor : CRLF {crlf_vor:,}, reine LF {lf_vor}")
text = roh.decode("utf-8")

W_TAG = re.compile(r"<w\s([^>]*?)(/?)>")
ID_ATTR = re.compile(r'xml:id="([^"]+)"')
ersetzt = 0
schon = 0


def ergaenze(t):
    global ersetzt, schon
    attrs, schrag = t.group(1), t.group(2)
    m = ID_ATTR.search(attrs)
    if m is None:
        return t.group(0)
    typ = ziel_typ.get(m.group(1))
    if typ is None:
        return t.group(0)
    if "corresp=" in attrs:
        schon += 1
        return t.group(0)
    ersetzt += 1
    return f'<w {attrs} corresp="variants.xml#{typ}"{schrag}>'


text = W_TAG.sub(ergaenze, text)
if schon:
    fehler(f"{schon} Ziele trugen schon ein @corresp, nichts geschrieben.")
if ersetzt != len(ziel_typ):
    fehler(f"{ersetzt} ersetzt, aber {len(ziel_typ)} Ziele, nichts geschrieben.")

n_anl = sum(len(z[3]) for z in zuordnung if z[2] == "ANLEGEN")
n_ver = sum(len(z[3]) for z in zuordnung if z[2] == "VERKNUEPFEN")
p_anl = sum(1 for z in zuordnung if z[2] == "ANLEGEN")
p_ver = sum(1 for z in zuordnung if z[2] == "VERKNUEPFEN")
eintrag = (
    f'    <change when="2026-10-02" who="#editor">#370 Punkt 2: {ersetzt:,} lemmatisierte '
    f"Tokens ohne @corresp mit einem Variantentyp verknuepft, nach den Entscheidungen "
    f"aus C1 (ingest/wzb/370-corresp/): {n_anl:,} Tokens in {p_anl} Paaren auf "
    f"{p_anl} neu gepraegten Typen type_{hoechste + 1} bis type_{naechste - 1} (Regel "
    f"aus #367), {n_ver} Tokens in {p_ver} Paaren auf bestehende Typen. Nicht "
    f"eingespielt: PRUEFSEITE und NICHT_ANLEGEN.</change>\r\n"
)
anker = "  </revisionDesc>"
if text.count(anker) != 1:
    fehler("revisionDesc-Anker nicht eindeutig")
text = text.replace(anker, eintrag + anker)

neu_roh = text.encode("utf-8")
crlf_nach, lf_nach = zeilenenden(neu_roh)
print(f"Zeilenenden nach: CRLF {crlf_nach:,}, reine LF {lf_nach}")
if (crlf_nach, lf_nach) != (crlf_vor + 1, lf_vor):
    fehler("Zeilenenden weichen vom erwarteten Stand (+1 CRLF) ab, nichts geschrieben.")

with open(WZB, "wb") as fh:
    fh.write(neu_roh)
with open(log, "w", encoding="utf-8", newline="") as fh:
    fh.write("xml_id;schreibung;lemma;typ;entscheidung;datei\n")
    for (schr, lem), typ, ent, ids, d in zuordnung:
        for i in ids:
            fh.write(f"{i};{schr};{lem};{typ};{ent};{d}\n")
print(f"\ngeschrieben: {ersetzt:,} @corresp ergaenzt, Log {log.name}")
