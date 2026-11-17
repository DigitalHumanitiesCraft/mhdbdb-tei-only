"""bre_annot.py: gemeinsame Helfer fuer Phase 1 bis 3 der Weingruesse (BRE, #147).

Vorbild sind die WZB-Skripte (scripts/ingest/wzb/wzb-auto-match.py, wzb-pos-assign.py,
wzb-sense-assign.py). Zwei Abweichungen, beide aus den Daten:

- Der Wortinhalt ist ''.join(w.itertext()), nie w.text: ein BRE-<w> kann <expan>, <supplied>,
  <add>, <hi> oder <pb> enthalten (Schema-Weg 1, #147). w.text liefert bei "v<expan>er</expan>
  stoppffen" nur "v". build-corpus-index.py und extract-variants.py lesen ebenfalls itertext.
- <w> in <head> (Rubriken, Reihentitel) bleibt unannotiert: Text, aber nicht lexikalisch
  (#66, Tabelle in docs/DATA-MODEL.md -> Structural cleanup, Zeile "Running headers").

Geschrieben wird mit lxml ohne Umformatierung: Parse und Write der Stufe-0-Dateien sind
byte-gleich (gemessen 2026-11-17), die Phasen fuegen nur Attribute hinzu.
"""
import collections
import csv
import re
import sys
import unicodedata
from pathlib import Path

from lxml import etree

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(HIER.parents[1]))
import bre_common as bc  # noqa: E402
from mhg_normalizer import normalize_mhg  # noqa: E402

TEI_NS = "http://www.tei-c.org/ns/1.0"
T = "{" + TEI_NS + "}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
AUTH = bc.REPO / "authority-files"
LEXIKON = AUTH / "lexicon.xml"
VARIANTEN = AUTH / "variants.xml"
KONZEPTE = AUTH / "concepts.xml"
PHASE1 = bc.INGEST_DIR / "phase1"
PHASE2 = bc.INGEST_DIR / "phase2"
PHASE3 = bc.INGEST_DIR / "phase3"
KONTEXT = 5  # Woerter je Seite

VALID_POS = {"NOM", "NAM", "ADJ", "ADV", "DET", "POS", "PRO", "PRP", "NEG", "NUM", "CNJ", "SCNJ",
             "CCNJ", "IPA", "VRB", "VEX", "VEM", "INJ", "DIG"}  # docs/POS-TAGSET.md, 19 Tags
LEGACY_POS = {"GRA": "ADV", "ART": "DET"}  # wie wzb-pos-assign.py; nur fuer die Lemma-Labels
# der Phase 1, die Wortart-Kandidaten der Phase 2 stehen in lade_lexikon()["pos19"]


def pos_kandidaten(text):
    """Wortart-Kandidaten aus einer Kandidatenspalte; CNJ laesst die Verfeinerung CCNJ/SCNJ zu
    (docs/POS-TAGSET.md §1 und §3: CNJ ist der Fallback, der Bestand soll differenziert werden)."""
    k = {t.strip() for t in text.split("|") if t.strip() in VALID_POS}
    return k | {"CCNJ", "SCNJ"} if "CNJ" in k else k
DECISION_TYPES = {"auto-single", "bulk-llm", "bulk-human", "instance-llm", "instance-human",
                  "abstain"}
CONFIDENCE = {"high", "medium", "low"}
RE_REVIEWER = re.compile(r"^(llm:[\w.\-]+|human:\w+)$")

# Faltung der Fruehdrucke vor normalize_mhg, auf BEIDEN Seiten (Text und variants.xml):
# kombinierendes e ueber a/o/u (U+0364) ist das Umlautzeichen der Drucke ("gruͤß" = "grüß");
# kombinierendes o ueber u (U+0366) und ů (U+016F) stehen fuer den Diphthong uo ("gůt" = "guot").
# Wirkung je Faltung gibt 10-lemma-assign.py aus.
FALTUNGEN = [
    ("aͤ", "ä"), ("oͤ", "ö"), ("uͤ", "ü"),
    ("Aͤ", "Ä"), ("Oͤ", "Ö"), ("Uͤ", "Ü"),
    ("uͦ", "uo"), ("Uͦ", "Uo"), ("ů", "uo"), ("Ů", "Uo"),
]


def falte(s):
    s = unicodedata.normalize("NFD", s)
    s = unicodedata.normalize("NFC", s.replace("ů", "ů").replace("Ů", "Ů"))
    for a, b in FALTUNGEN:
        s = s.replace(a, b)
    return s


def norm(s):
    """Vergleichsform: Faltung der Drucke, dann normalize_mhg (CONTRACTS.md, Contract A)."""
    return normalize_mhg(falte(s.strip()))


def wort(w):
    return "".join(w.itertext()).strip()


def zeugen_dateien():
    """Die geschriebenen Zeugen (alle ausser bre_common.SEGMENTIERUNG_OFFEN), harter Fehler,
    wenn eine Datei fehlt oder eine unerwartete daliegt."""
    soll = {mh: z for z, (_, mh) in bc.ZEUGEN.items() if z not in bc.SEGMENTIERUNG_OFFEN}
    ist = {p.name[:-len(".tei.xml")]: p for p in bc.INGEST_DIR.glob("BRE_*.tei.xml")}
    if set(ist) != set(soll):
        raise bc.HarterFehler(f"Zeugendateien weichen ab: fehlen {sorted(set(soll) - set(ist))}, "
                              f"unerwartet {sorted(set(ist) - set(soll))}")
    return [(soll[k], ist[k]) for k in sorted(ist)]


def lies(pfad):
    return etree.parse(str(pfad))


def schreibe(baum, pfad):
    baum.write(str(pfad), encoding="UTF-8", xml_declaration=True)


def in_head(w):
    p = w.getparent()
    while p is not None:
        if p.tag == T + "head":
            return True
        if p.tag in (T + "l", T + "div", T + "body"):
            return False
        p = p.getparent()
    return False


def text_titel(w):
    """Titel des Einzeltexts aus dem Kommentar vor dem <div type="section"> (Stufe 0)."""
    p = w.getparent()
    while p is not None and not (p.tag == T + "div" and p.get("type") == "section"):
        p = p.getparent()
    if p is None:
        return ""
    c = p.getprevious()
    if c is not None and isinstance(c, etree._Comment):
        m = re.match(r"\s*Text \d+: (.*?)(?: \(.*\))?\s*$", c.text)
        if m:
            return m.group(1)
    return ""


def tokens(baum):
    """-> Liste dict(w, id, form, head, titel, kontext) in Dokumentreihenfolge, Kontext +-5
    Woerter (nur Woerter, Ziel in eckigen Klammern)."""
    ws = list(baum.getroot().iter(T + "w"))
    formen = [wort(w) for w in ws]
    out = []
    for i, w in enumerate(ws):
        a, b = max(0, i - KONTEXT), min(len(ws), i + KONTEXT + 1)
        kontext = " ".join(f"[{formen[j]}]" if j == i else formen[j] for j in range(a, b))
        out.append({"w": w, "id": w.get(XML_ID), "form": formen[i], "head": in_head(w),
                    "titel": text_titel(w), "kontext": kontext})
    return out


# ---------------------------------------------------------------- Authority-Dateien

def lade_lexikon():
    """lemma_id -> dict(orth, pos[list, normalisiert], senses[list of dict(id, konzepte)])."""
    lex = {}
    for _, e in etree.iterparse(str(LEXIKON), tag=T + "entry"):
        lid = e.get(XML_ID)
        orth = e.findtext(f"{T}form/{T}orth") or ""
        pos, pos19 = [], []
        for p in e.findall(f"{T}gramGrp/{T}pos"):
            roh = (p.text or "").strip()
            t = LEGACY_POS.get(roh, roh)
            if t and t not in pos:
                pos.append(t)
            # Kandidaten fuer Phase 2 nach docs/POS-TAGSET.md §3: ART -> DET; GRA ist eine
            # Steigerungsmarke und faellt weg (GRA -> ADV aus wzb-pos-assign.py widerspricht
            # §3), die uebrigen Tags des Lemmas entscheidet der Kontext; nur GRA allein -> ADJ
            t19 = {"ART": "DET", "GRA": None}.get(roh, roh)
            if t19 and t19 not in pos19:
                pos19.append(t19)
        if not pos19 and pos:
            pos19 = ["ADJ"]
        senses = []
        for s in e.findall(f"{T}sense"):
            senses.append({"id": s.get(XML_ID),
                           "konzepte": [p.get("target").split("#")[-1] for p in s.findall(f"{T}ptr")
                                        if "concepts.xml#" in (p.get("target") or "")],
                           "typen": {t.lstrip("#") for t in (s.get("ana") or "").split()}})
        lex[lid] = {"orth": orth, "pos": pos, "pos19": pos19, "senses": senses}
        e.clear()
    return lex


def lade_varianten():
    """-> (norm -> Counter(lemma_id -> Korpusbelege), norm -> list((type_id, lemma_id, form))).

    Die Belegzahl ist die Summe von form/@n (Tokens je Typ im Korpus, #378) ueber alle Formen
    mit derselben normalisierten Form; sie ist Evidenz fuer die Disambiguierung, keine Entscheidung.
    """
    lemmata, typen = collections.defaultdict(collections.Counter), collections.defaultdict(list)
    for _, e in etree.iterparse(str(VARIANTEN), tag=T + "entry"):
        lid = (e.get("corresp") or "").split("#")[-1]
        if lid:
            for f in e.findall(T + "form"):
                t = (f.text or "").strip()
                if t:
                    n = norm(t)
                    lemmata[n][lid] += int(f.get("n") or 0)
                    typen[n].append((f.get(XML_ID), lid, t))
        e.clear()
    return lemmata, typen


def lade_konzepte():
    out = {}
    for _, c in etree.iterparse(str(KONZEPTE), tag=T + "category"):
        de = c.findtext(f"{T}catDesc/{T}term[@{{http://www.w3.org/XML/1998/namespace}}lang='de']")
        en = c.findtext(f"{T}catDesc/{T}term[@{{http://www.w3.org/XML/1998/namespace}}lang='en']")
        out[c.get(XML_ID)] = f"{(de or '').strip()} ({(en or '').strip()})" if en else (de or "").strip()
    return out


def lemma_label(lid, lex, konzepte=None):
    e = lex.get(lid)
    if e is None:
        return f"{lid} (fehlt im Lexikon)"
    s = f"{lid} {e['orth']} [{'/'.join(e['pos'])}]"
    if konzepte is not None and e["senses"]:
        k = [konzepte.get(c, c) for c in e["senses"][0]["konzepte"]][:2]
        if k:
            s += " {" + "; ".join(k) + ("; …" if len(e["senses"]) > 1 else "") + "}"
    return s


# ---------------------------------------------------------------- TSV

def schreibe_tsv(pfad, felder, zeilen):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with open(pfad, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=felder, delimiter="\t", lineterminator="\n",
                           quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for z in zeilen:
            w.writerow({k: z.get(k, "") for k in felder})


def lies_tsv(pfad, felder=None):
    if not pfad.exists():
        raise bc.HarterFehler(f"TSV fehlt: {pfad}")
    with open(pfad, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        if felder and r.fieldnames != felder:
            raise bc.HarterFehler(f"{pfad.name}: Spalten {r.fieldnames} != {felder}")
        return list(r)


def pruefe_entscheidung(z, ort):
    """Harte Pruefung der Entscheidungsspalten einer aufgeloesten Zeile."""
    if z["decision_type"] not in DECISION_TYPES:
        raise bc.HarterFehler(f"{ort}: decision_type {z['decision_type']!r} unbekannt")
    if z["decision_type"] != "abstain" and z["confidence"] not in CONFIDENCE:
        raise bc.HarterFehler(f"{ort}: confidence {z['confidence']!r} unbekannt")
    if not RE_REVIEWER.match(z["reviewer"]):
        raise bc.HarterFehler(f"{ort}: reviewer {z['reviewer']!r} nicht llm:<modell> oder human:<name>")


def prozent(n, d):
    return f"{n}/{d} ({100 * n / d:.1f} %)" if d else f"{n}/0"
