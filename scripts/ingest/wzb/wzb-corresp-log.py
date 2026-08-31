"""Provenienz-Log fuer #370 Punkt 1 erzeugen, Muster ingest/wzb/235-breve/.

Drei Artefakte:
  config.json        die Regel, mit der zugeordnet wurde, plus die Begruendungen
  zuordnung.csv      je angewendetem Token: was gesetzt wurde und woher der Typ stammt
  offene-faelle.csv  die 5.273 ohne Zuordnung, aggregiert je Paar. Das ist die
                     Arbeitsliste fuer #370 Punkt 2 und der eigentliche Grund,
                     warum dieses Log nicht entbehrlich ist.

Liest den Korpus im JETZIGEN Stand (nach dem Lauf) und rekonstruiert die
Herkunft jedes Typs aus der Praxis ausserhalb der WZB.
"""
import csv
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "ingest" / "wzb" / "370-corresp"
sys.path.insert(0, str(ROOT / "scripts"))
from corpus_files import corpus_files  # noqa: E402

TEI = "{http://www.tei-c.org/ns/1.0}"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"
OUT.mkdir(parents=True, exist_ok=True)

# Wie viele Sigel die Stichprobenspalte hoechstens nennt.
SIGEL_PROBE = 8


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


# Praxis ausserhalb der WZB: (form, lemma) -> Counter[type], plus Belegsigel
geuebt = defaultdict(Counter)
sigel_von = defaultdict(set)
for path in corpus_files(ROOT / "tei"):
    if path.name == "WZB.tei.xml":
        continue
    body = etree.parse(str(path)).find(f".//{TEI}body")
    if body is None:
        continue
    sigle = path.name.split(".", 1)[0]
    for w in body.iter(f"{TEI}w"):
        lemma = first_lemma(w)
        t = variant_type(w)
        if not lemma or not t:
            continue
        text = "".join(w.itertext()).strip()
        if text:
            paar = (key_form(text), lemma)
            geuebt[paar][t] += 1
            sigel_von[paar].add(sigle)

# Alter WZB-Stand, um zu wissen, welche Tokens dieser Lauf angefasst hat
import subprocess  # noqa: E402
alt_bytes = subprocess.run(
    ["git", "-C", str(ROOT), "show", "origin/main:tei/WZB.tei.xml"],
    capture_output=True, check=True).stdout
alt_ohne_corresp = set()
for w in etree.fromstring(alt_bytes).find(f".//{TEI}body").iter(f"{TEI}w"):
    if w.get("lemmaRef") and not w.get("corresp") and "".join(w.itertext()).strip():
        alt_ohne_corresp.add(w.get(XMLID))

body = etree.parse(str(ROOT / "tei" / "WZB.tei.xml")).find(f".//{TEI}body")
angewendet = []
offen = defaultdict(lambda: {"tokens": 0, "beispiele": []})
for w in body.iter(f"{TEI}w"):
    wid = w.get(XMLID)
    if wid not in alt_ohne_corresp:
        continue
    lemma = first_lemma(w)
    text = "".join(w.itertext()).strip()
    paar = (key_form(text), lemma)
    typ = variant_type(w)
    if typ:
        belege = geuebt[paar][typ]
        angewendet.append({
            "xml_id": wid, "form": text, "form_schluessel": paar[0],
            "lemma": lemma, "pos": w.get("pos") or "", "typ": typ,
            "belege_ausserhalb_wzb": belege,
            # Die Sigelliste ist eine Stichprobe, keine Vollaufzaehlung: sie
            # wird bei SIGEL_PROBE gekappt, weil ein haeufiges Funktionswort
            # in hunderten Sigeln steht. Die gekappte Liste allein waere nicht
            # als Kappung erkennbar, deshalb daneben die wahre Zahl.
            "sigel_anzahl": len(sigel_von[paar]),
            "sigel_probe": " ".join(sorted(sigel_von[paar])[:SIGEL_PROBE]),
        })
    else:
        eintrag = offen[paar]
        eintrag["tokens"] += 1
        if len(eintrag["beispiele"]) < 3:
            eintrag["beispiele"].append(f"{wid} {text}")

print(f"angewendet: {len(angewendet):,}")
print(f"offene Paare: {len(offen):,}, Tokens: {sum(v['tokens'] for v in offen.values()):,}")

with (OUT / "zuordnung.csv").open("w", encoding="utf-8-sig", newline="") as fh:
    writer = csv.DictWriter(fh, delimiter=";", fieldnames=[
        "xml_id", "form", "form_schluessel", "lemma", "pos", "typ",
        "belege_ausserhalb_wzb", "sigel_anzahl", "sigel_probe"])
    writer.writeheader()
    writer.writerows(angewendet)

with (OUT / "offene-faelle.csv").open("w", encoding="utf-8-sig", newline="") as fh:
    writer = csv.writer(fh, delimiter=";")
    writer.writerow(["form_schluessel", "lemma", "tokens", "grund", "beispiele"])
    for (form, lemma), v in sorted(offen.items(), key=lambda kv: -kv[1]["tokens"]):
        writer.writerow([form, lemma, v["tokens"],
                         "kein Typ fuer dieses Paar im Korpus belegt",
                         " | ".join(v["beispiele"])])

config = {
    "serie": "#370 Punkt 1 (fehlende @corresp der WZB)",
    "art": "Verknuepfung bereits lemmatisierter Tokens mit einem BESTEHENDEN Variantentyp; keine Erstannotation, kein neuer Typ, kein LLM",
    "regel": {
        "schluessel": "(NFC-normalisierte und kleingeschriebene Schreibung, erstes Lemma aus @lemmaRef)",
        "quelle": "die Praxis des Korpus AUSSERHALB der WZB",
        "bedingung": "uebernommen wurde nur, wo dort GENAU EIN Variantentyp fuer dasselbe Paar belegt ist",
        "gemessen": "0 Paare mit mehreren Typen, die Bedingung hat also nie etwas verworfen",
    },
    "zahlen": {
        "kandidaten": 52163,
        "angewendet": 46890,
        "offen": 5273,
        "offene_paare": 484,
    },
    "revisiondesc": {
        "datum": "2026-08-31",
        "titel": "#370 Punkt 1",
        "log": "ingest/wzb/370-corresp/",
    },
    "kommentar_zaehlweise": "Das Ticket nennt 52.097 Tokens in 1.685 Paaren, gemessen am 2026-08-24. Heute sind es 52.163 in 1.733. Die Differenz ist NICHT Drift, sondern der #235-Breve-Batch (c0e8dee80) vom 31.08., der 66 Tokens bewusst ohne corresp annotiert hat. Gegengeprueft am Stand 4f61eb69f: dort liefert dieselbe Zaehlweise exakt 52.097 und 1.685. Die Kleinschreibung im Schluessel ist Teil der Vorschrift; schreibungsgetreu gezaehlt waeren es 1.886 Paare, und die Tokenzahlen des Tickets liessen sich nicht reproduzieren.",
    "kommentar_case_merge": "2.186 der 46.890 Tokens (4,66 %) tragen eine Schreibung, die fuer ihren Typ ausserhalb der WZB nicht EXAKT belegt ist, sondern erst nach Kleinschreibung und NFC zusammenfaellt. Es sind durchweg satzinitiale Grossschreibungen: Biblia, Got, An, Von, In, Hast, O. Ein case-sensitiver Schluessel haette diese 2.186 ungeheilt gelassen. Der Korpus fuehrt heute schon case-gemischte Typen je Variantentyp. Ob satzinitiale Grossschreibung ein eigener Variantentyp sein soll, ist eine redaktionelle Frage und gehoert als Zahl in die Entscheidung zu Punkt 2. Messvorschrift: je angewendetem Token pruefen, ob die NFC-normalisierte Schreibung CASE-SENSITIV unter demselben Lemma ausserhalb der WZB denselben Typ traegt; wenn nicht, ist die Zuordnung erst durch die Kleinschreibung zustande gekommen.",
    "kommentar_variants": "variants.xml gewinnt und verliert keinen Typ und keine Lemma-Zuordnung (extract-variants: 0 added, 0 removed, 0 lemma assignment changed). Genau zwei Formen kippen von Klein- auf Grossschreibung, beide bei Stimmengleichheit (type_68232 fur/Fur 2:2, type_276606 schafhirten/Schafhirten 1:1), entschieden vom alphabetischen Tiebreak. Beide Indexe bleiben byte-identisch, weil der Authority-Index nur normalisierte Formen traegt und @corresp nicht in den Korpus-Index eingeht. Deshalb kein Bump.",
    "kommentar_378": "Vorabmessung zur Stoppbedingung des Kickoffs: die Abbildung normalisierte Form auf Lemma (Stufe 2 der Lemma-Aufloesung, first-wins) bleibt bei 234.243 Eintraegen. 0 fallen weg, 0 kommen hinzu, 0 wechseln das Lemma. Es entstehen also keine neuen first-wins-Kollisionen im Sinn von #378, und der Grund ist die Auswahlregel selbst: sie praegt keinen neuen Typ.",
    "kommentar_offen": "Die 5.273 offenen Tokens in 484 Paaren stehen in offene-faelle.csv und sind die Arbeitsliste fuer #370 Punkt 2. Fuer sie muesste unter dem jeweiligen Lemma ein NEUER Variantentyp gepraegt werden, und das ist seit #216 genehmigungspflichtig (KZW).",
}
(OUT / "config.json").write_text(
    json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("geschrieben:", OUT)
