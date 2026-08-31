"""#370 Punkt 1: die fehlenden @corresp in tei/WZB.tei.xml nachtragen.

Zuordnung: (kleingeschriebene NFC-Schreibung, erstes Lemma) -> Variantentyp,
so wie das Korpus AUSSERHALB der WZB sie uebt. Nur eindeutige Paare, also
solche, fuer die dort genau ein Typ belegt ist.

Die Zaehlweise ist am Ticket rekonstruiert und geprueft: sie liefert fuer den
WZB-Stand vom 24.08. (4f61eb69f) exakt die 52.097 Tokens und 1.685 Paare des
Tickets, und fuer heute 52.163 und 1.733. Die Differenz sind die 66 Tokens des
#235-Batches, der bewusst kein @corresp gesetzt hat.

SCHREIBWEISE, und das ist hier kein Detail:
tei/WZB.tei.xml ist die einzige CRLF-Datei im Korpus und mischt 235.974 CRLF
mit 17 reinen LF-Zeilen. Deshalb exakte Byte-Ersetzung auf dem gelesenen Text,
newline='' bei Lesen UND Schreiben, und keine Serialisierung ueber lxml. lxml
wird nur zum FINDEN der Ziel-Tokens benutzt, nie zum Schreiben. Das Zaehlerpaar
wird vor und nach dem Lauf ausgegeben.

Aufruf:
    python apply-370-corresp.py            # Trockenlauf, schreibt nichts
    python apply-370-corresp.py --apply    # schreibt tei/WZB.tei.xml
"""
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

APPLY = "--apply" in sys.argv


def key_form(text):
    return unicodedata.normalize("NFC", text).lower()


def first_lemma(w):
    ref = w.get("lemmaRef")
    return ref.split()[0].split("#")[-1] if ref else None


def variant_type(w):
    c = w.get("corresp")
    if not c:
        return None
    for frag in c.split():
        tail = frag.split("#")[-1]
        if tail.startswith("type_"):
            return tail
    return None


def zeilenenden(data):
    crlf = data.count(b"\r\n")
    return crlf, data.count(b"\n") - crlf


# ---------------------------------------------------------------- 1. Praxis
geuebt = defaultdict(Counter)
for path in corpus_files(ROOT / "tei"):
    if path.name == "WZB.tei.xml":
        continue
    body = etree.parse(str(path)).find(f".//{TEI}body")
    if body is None:
        continue
    for w in body.iter(f"{TEI}w"):
        lemma = first_lemma(w)
        t = variant_type(w)
        if not lemma or not t:
            continue
        text = "".join(w.itertext()).strip()
        if text:
            geuebt[(key_form(text), lemma)][t] += 1

# ---------------------------------------------------------------- 2. Ziele
body = etree.parse(str(WZB)).find(f".//{TEI}body")
ziele = {}          # xml_id -> type
offen = Counter()   # Paare ohne eindeutige Zuordnung
for w in body.iter(f"{TEI}w"):
    lemma = first_lemma(w)
    if not lemma or w.get("corresp"):
        continue
    text = "".join(w.itertext()).strip()
    if not text:
        continue
    paar = (key_form(text), lemma)
    typen = geuebt.get(paar)
    if typen and len(typen) == 1:
        ziele[w.get(XMLID)] = next(iter(typen))
    else:
        offen[paar] += 1

print(f"Ziel-Tokens (eindeutige Zuordnung): {len(ziele):,}")
print(f"offen (kein oder mehrdeutiger Typ): {sum(offen.values()):,} Tokens "
      f"in {len(offen):,} Paaren")
print(f"davon Paare mit MEHREREN Typen: "
      f"{sum(1 for p in offen if geuebt.get(p) and len(geuebt[p]) > 1)}")

if not APPLY:
    print("\nTrockenlauf, nichts geschrieben. Mit --apply schreiben.")
    sys.exit(0)

# ---------------------------------------------------------------- 3. Schreiben
roh = WZB.read_bytes()
crlf_vor, lf_vor = zeilenenden(roh)
print(f"\nZeilenenden vor : CRLF {crlf_vor:,}, reine LF {lf_vor}")

text = roh.decode("utf-8")

# EIN Durchlauf ueber alle <w>-Start-Tags, nicht eine Suche je Ziel: bei 46.890
# Zielen und 26 MB Text war die Variante mit einer Regex-Suche pro Ziel
# quadratisch und lief in zehn Minuten nicht durch.
#
# [^>]* ist fuer Start-Tags sicher: spitze Klammern stehen im Korpus als
# Entitaet (&lt;/&gt;), auch innerhalb von <pc>, nie roh in einem Attributwert.
W_TAG = re.compile(r'<w\s([^>]*?)(/?)>')
ID_ATTR = re.compile(r'xml:id="([^"]+)"')

ersetzt = 0
schon = 0


def ergaenze(treffer):
    global ersetzt, schon
    attrs, schrag = treffer.group(1), treffer.group(2)
    m = ID_ATTR.search(attrs)
    if m is None:
        return treffer.group(0)
    typ = ziele.get(m.group(1))
    if typ is None:
        return treffer.group(0)
    if 'corresp=' in attrs:
        schon += 1
        return treffer.group(0)
    ersetzt += 1
    return f'<w {attrs} corresp="variants.xml#{typ}"{schrag}>'


text = W_TAG.sub(ergaenze, text)
if schon:
    print(f"WARNUNG: {schon} Ziele trugen schon ein @corresp und blieben unberuehrt.")
if ersetzt != len(ziele):
    sys.exit(f"ABBRUCH: {ersetzt} ersetzt, aber {len(ziele)} Ziele. "
             "Nichts geschrieben.")

neu_roh = text.encode("utf-8")
crlf_nach, lf_nach = zeilenenden(neu_roh)
print(f"Zeilenenden nach: CRLF {crlf_nach:,}, reine LF {lf_nach}")
if (crlf_vor, lf_vor) != (crlf_nach, lf_nach):
    sys.exit("ABBRUCH: Zeilenenden haben sich geaendert, nichts geschrieben.")

with open(WZB, "wb") as fh:
    fh.write(neu_roh)
print(f"\ngeschrieben: {ersetzt:,} @corresp ergaenzt")
