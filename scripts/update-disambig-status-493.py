#!/usr/bin/env python3
"""
Angabe zur semantischen Disambiguierung im Header an den Stand der
Annotation angleichen (#493).

KZW am 2026-09-28 im Body von #493: "Lass den Satz in der Form nur stehen, wenn
saemtliche Tokens in einem Text noch nicht Begriffs-disambiguiert sind. Wenn
ein Teil des Textes semantisch erschlossen wurde, schreib das hin."

Der Satz steht in encodingDesc/editorialDecl/normalization als eigenes <p>,
in 52 Fassungen ("Lemmatisiert, nicht disambiguiert.", "Noch nicht
disambiguiert." ...). Er stammt aus dem Altbestand und wurde bei der Migration
mitgeschleppt.

MESSVORSCHRIFT: gezaehlt wird im <body> jedes <w> mit nicht leerem Text.
    lemmatisiert  = mit @lemmaRef
    erschlossen   = mit @lemmaRef und @ana (Verweis auf einen Sense)
Ein Token gilt als erschlossen, sobald es einen Begriff traegt, auch wenn die
Zuordnung automatisch kam, weil das Lemma nur einen Sense hat (DATA-MODEL,
Phase 3). Das ist KZWs Wortlaut: Tokens, die Begriffs-disambiguiert sind.
Ein @ana mit mehreren Senses kommt im Korpus nicht vor (0 Tokens, gemessen).

    erschlossen = 0            -> Satz bleibt
    0 < erschlossen < lemmat.  -> "teilweise semantisch disambiguiert"
    erschlossen = lemmat.      -> "semantisch disambiguiert"

ZIELMENGE, gemessen am 2026-09-30 (667 Dateien):
    Dateien mit einem solchen Satz                     572
      erschlossen = 0                                     0
      teilweise                                         402
      vollstaendig                                      170
    Dateien mit mehr als einem solchen Satz               0

Ersetzt wird nur die Aussage zur Disambiguierung; der Teil zur Lemmatisierung
bleibt stehen. Ausnahme sind die 12 Saetze, die beides in einem Zug verneinen
("Noch nicht lemmatisiert und disambiguiert.", "Weder lemmatisiert noch
disambiguiert."). Die zwoelf Texte sind zu 74 bis 86 % lemmatisiert, dort wird
der ganze Satz zu "Teilweise lemmatisiert, ...". Saetze, die schon
"teilweise", "weitgehend" oder "fast vollstaendig disambiguiert" sagen,
bleiben bei teilweise erschlossenen Texten stehen.

Ein Satz, den keine Regel abdeckt, ist ein harter Fehler: nichts wird
geschrieben.

Je geaenderter Datei kommt ein <change> in den revisionDesc (Muster #216),
mit den Zahlen dieser Datei; ein spaeterer Lauf ersetzt ihn (Marker '#493').
Ein zweiter Lauf erkennt die eigene Ausgabe und stuft nur um, wenn sich
der Stand geaendert hat (teilweise -> vollstaendig); ohne Aenderung schreibt
er nichts, auch die Liste nicht. "Vorher" bleibt dabei der Wortlaut aus dem
Altbestand, und die Liste fuehrt je Datei den letzten Stand.

ERGAENZEN (KZW am 2026-10-08 in #493: "Ja ergaenze das dort mithilfe deines
Skripts auch"): Dateien OHNE einen solchen Satz bekommen ihn, sobald
erschlossen > 0, als eigenes <p> am Ende von <normalization>, in den beiden
Formen, die im Korpus schon allein stehen: "Teilweise semantisch
disambiguiert." und "Semantisch disambiguiert.". Fehlt <normalization>, wird es
als letztes Kind von <editorialDecl> angelegt (Schema: normalization steht
dort zuletzt). Gemessen am 2026-10-08: 95 Dateien ohne Satz, 75 teilweise,
20 vollstaendig erschlossen; 4 der 75 teilweise erschlossenen haben kein
<normalization>. Ein Satz zur
Lemmatisierung wird dabei nicht erfunden. Der <change> traegt "Vorher" leer,
damit ein spaeterer Lauf das als Ursprung erkennt.

Textuelle Ersetzung statt lxml-Serialisierung, damit der Rest der Datei
byte-identisch bleibt.

Usage:
    python scripts/update-disambig-status-493.py            # Trockenlauf
    python scripts/update-disambig-status-493.py --apply
"""
import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

from lxml import etree

REPO = Path(__file__).resolve().parents[1]
TEI_DIR = REPO / "tei"
PLAN = REPO / "ingest" / "disambig-493" / "aenderungen.csv"
NS = "{http://www.tei-c.org/ns/1.0}"

DATUM = "2026-09-30"
DATUM_ERGAENZT = "2026-10-08"
MARKER = "#493"
DIS = "semantisch disambiguiert"

NORM_RE = re.compile(r"<normalization>(.*?)</normalization>", re.S)
P_RE = re.compile(r"<p>(.*?)</p>", re.S)
CLOSE_RE = re.compile(r"([ \t]*)</revisionDesc>")
LAST_CHANGE_RE = re.compile(r"([ \t]*)<change[ >]")
VORHER_RE = re.compile(r"<change [^>]*>#493: .*?Vorher: &#34;(.*?)&#34;</change>")
EIGENE_ZEILE_RE =re.compile(r"[ \t]*<change [^>]*>#493: .*?</change>\r?\n")

EIGEN = re.compile(r"(?P<vor>.*?)(?:[Tt]eilweise semantisch|[Ss]emantisch) disambiguiert(?P<rest>.*)")
QUALIFIZIERT = re.compile(r"\b(teilweise|weitgehend|fast vollständig) disambiguiert")
DOPPELT = re.compile(r"(Noch nicht|Nicht) lemmatisiert (und|oder) (nicht )?disambiguiert\.|"
                     r"Weder lemmatisiert noch disambiguiert\.")
POSITIV = re.compile(r"(?P<x>.+?) und disambiguiert(?P<rest>\.?.*)")
VORNE = re.compile(r"(?P<pre>Der Text ist )?(?:[Nn]och )?[Nn]icht disambiguiert(?P<rest>.*)")
LEMMA_TEIL = r"(?P<x>(?:.*\s)?[Ll]emmatisiert)"
UND_NICHT = re.compile(LEMMA_TEIL + r" und (?:noch )?nicht disambiguiert(?P<rest>.*)")
HINTEN = re.compile(LEMMA_TEIL + r"(?P<sep>[,;.])?\s*(?:aber\s+)?(?:[Nn]och\s+)?[Nn]icht disambiguiert(?P<rest>.*)")


class UnbekannterSatz(Exception):
    pass


def neuer_satz(s, klasse):
    """Neuer Satz, oder None, wenn der alte stimmt."""
    q = ("teilweise " if klasse == "teil" else "") + DIS
    gross = q[0].upper() + q[1:]
    # Eigene Ausgabe eines frueheren Laufs: an die aktuelle Klasse angleichen,
    # damit ein zweiter Lauf nach weiterer Annotation hochstuft statt abbricht
    m = EIGEN.fullmatch(s)
    if m:
        vorne = m["vor"] == "" or m["vor"].endswith(". ")
        ziel = gross if vorne else q
        neu = f"{m['vor']}{ziel}{m['rest']}"
        return None if neu == s else neu
    if QUALIFIZIERT.search(s):
        if klasse == "teil":
            return None
        raise UnbekannterSatz("schon eingeschraenkt, aber vollstaendig erschlossen")
    if DOPPELT.fullmatch(s):
        return f"Teilweise lemmatisiert, {q}."
    m = POSITIV.fullmatch(s)
    if m and "nicht" not in m["x"].split()[-1:]:
        return None if klasse == "alle" else f"{m['x']} und {q}{m['rest']}"
    m = VORNE.fullmatch(s)
    if m:
        return (f"Der Text ist {q}{m['rest']}" if m["pre"] else f"{gross}{m['rest']}")
    m = UND_NICHT.fullmatch(s)
    if m:
        return f"{m['x']} und {q}{m['rest']}"
    m = HINTEN.fullmatch(s)
    if m:
        sep = m["sep"] or ","
        if sep == ".":
            return f"{m['x']}. {gross}{m['rest']}"
        return f"{m['x']}{sep} {q}{m['rest']}"
    raise UnbekannterSatz("keine Regel")


def zaehle(pfad):
    doc = etree.parse(str(pfad))
    body = doc.find(f".//{NS}text/{NS}body")
    lem = ana = 0
    for w in body.iter(f"{NS}w"):
        if not "".join(w.itertext()).strip() or not w.get("lemmaRef"):
            continue
        lem += 1
        if w.get("ana"):
            ana += 1
    return lem, ana


def change_eintragen(text, eintrag, fname):
    kopf = text.split("</teiHeader>", 1)[0]
    if MARKER in kopf:
        text, _ = EIGENE_ZEILE_RE.subn("", text, count=1)
        kopf = text.split("</teiHeader>", 1)[0]
    m_close = None
    for m_close in CLOSE_RE.finditer(kopf):
        pass
    if m_close is None:
        raise SystemExit(f"FEHLER: {fname}: kein </revisionDesc> im teiHeader")
    einrueckung = None
    for m in LAST_CHANGE_RE.finditer(text[:m_close.start()]):
        einrueckung = m.group(1)
    if einrueckung is None:
        einrueckung = m_close.group(1) + "  "
    nl = "\r\n" if "\r\n" in kopf else "\n"
    return text[:m_close.start()] + einrueckung + eintrag + nl + text[m_close.start():]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    dateien = sorted(TEI_DIR.glob("*.tei.xml"))
    fehler, plan, ersetzt, neu_text = [], [], [], {}
    stat = Counter()
    for fp in dateien:
        text = fp.read_text(encoding="utf-8", newline="")
        kopf = text.split("</teiHeader>", 1)[0]
        m_norm = NORM_RE.search(kopf)
        treffer = [m for m in P_RE.finditer(m_norm.group(1))
                   if "disambig" in m.group(1).lower()] if m_norm else []
        if not treffer:
            lem, ana = zaehle(fp)
            if ana == 0:
                stat["ohne Satz, erschlossen = 0"] += 1
                continue
            klasse = "alle" if ana == lem else "teil"
            neu = "Semantisch disambiguiert." if klasse == "alle" else "Teilweise semantisch disambiguiert."
            if m_norm:
                pos = m_norm.end(1)
                text = text[:pos] + f"<p>{neu}</p>" + text[pos:]
                stat[f"ergaenzt in normalization, {klasse}"] += 1
            else:
                enden = list(re.finditer(r"</editorialDecl>", kopf))
                if len(enden) != 1:
                    fehler.append(f"{fp.name}: weder <normalization> noch genau ein </editorialDecl>")
                    continue
                pos = enden[0].start()
                text = text[:pos] + f"<normalization><p>{neu}</p></normalization>" + text[pos:]
                stat[f"ergaenzt mit neuem normalization, {klasse}"] += 1
            plan.append([fp.name[:-8], "", neu, lem, ana, f"{100 * ana / lem:.1f}"])
            ersetzt.append(("(kein Satz)", neu))
            eintrag = (f'<change when="{DATUM_ERGAENZT}" who="#editor">#493: Angabe zur semantischen '
                       f"Disambiguierung in encodingDesc/normalization ergänzt ({ana} von {lem} "
                       f"lemmatisierten Tokens tragen einen Begriff in @ana). Vorher: &#34;&#34;</change>")
            neu_text[fp] = change_eintragen(text, eintrag, fp.name)
            continue
        if len(treffer) > 1:
            fehler.append(f"{fp.name}: {len(treffer)} Saetze mit 'disambig'")
            continue
        inhalt = treffer[0].group(1)
        if "<" in inhalt:
            fehler.append(f"{fp.name}: Kindelement im Satz")
            continue
        alt = " ".join(inhalt.split())
        lem, ana = zaehle(fp)
        stat["mit Satz"] += 1
        if ana == 0:
            stat["erschlossen = 0, bleibt"] += 1
            continue
        klasse = "alle" if ana == lem else "teil"
        stat[f"Klasse {klasse}"] += 1
        try:
            neu = neuer_satz(alt, klasse)
        except UnbekannterSatz as e:
            fehler.append(f"{fp.name}: {e}: {alt!r} ({klasse})")
            continue
        if neu is None or neu == alt:
            stat["stimmt schon"] += 1
            continue
        stat["geaendert"] += 1
        # Bei einem spaeteren Lauf bleibt der Wortlaut aus dem Altbestand das
        # "Vorher", nicht die eigene Ausgabe des ersten Laufs
        m_vorher = VORHER_RE.search(kopf)
        ursprung = m_vorher.group(1) if m_vorher else alt
        plan.append([fp.name[:-8], ursprung, neu, lem, ana, f"{100 * ana / lem:.1f}"])
        ersetzt.append((alt, neu))

        start = m_norm.start(1) + treffer[0].start(1)
        ende = m_norm.start(1) + treffer[0].end(1)
        lead = inhalt[:len(inhalt) - len(inhalt.lstrip())]
        trail = inhalt[len(inhalt.rstrip()):]
        text = text[:start] + lead + neu + trail + text[ende:]
        eintrag = (f'<change when="{DATUM}" who="#editor">#493: Angabe zur semantischen '
                   f"Disambiguierung in encodingDesc/normalization an den Stand der Annotation "
                   f"angeglichen ({ana} von {lem} lemmatisierten Tokens tragen einen Begriff "
                   f"in @ana). Vorher: &#34;{ursprung}&#34;</change>")
        neu_text[fp] = change_eintragen(text, eintrag, fp.name)

    if fehler:
        print(f"FEHLER in {len(fehler)} Dateien, nichts geschrieben:")
        for f in fehler:
            print("  " + f)
        return 1

    print(f"Dateien: {len(dateien)} | " + " | ".join(f"{k}: {v}" for k, v in sorted(stat.items())))
    # Was jetzt in der Datei steht -> was dort gleich steht; der Altwortlaut
    # der Liste (Spalte alt) kann davon abweichen
    uebersicht = Counter(ersetzt)
    print(f"\n{len(uebersicht)} verschiedene Ersetzungen:")
    for (alt, neu), n in sorted(uebersicht.items(), key=lambda x: -x[1]):
        print(f"  {n:4d}  {alt}\n        -> {neu}")

    if args.apply and not plan:
        print("\n[APPLY] nichts zu aendern, nichts geschrieben")
    elif args.apply:
        # Die Liste fuehrt je Datei den letzten Stand; Zeilen von Dateien, die
        # dieser Lauf nicht beruehrt, bleiben stehen. Gelesen wird sie VOR dem
        # ersten Schreiben: ein Fehler hier darf keine TEI-Datei hinterlassen
        kopfzeile = ["sigle", "alt", "neu", "lemmatisiert", "erschlossen", "anteil_prozent"]
        zeilen = {}
        if PLAN.exists():
            with PLAN.open(encoding="utf-8", newline="") as h:
                r = csv.reader(h)
                if next(r, None) != kopfzeile:
                    raise SystemExit(f"FEHLER: {PLAN.name} hat eine unerwartete Kopfzeile, nichts geschrieben")
                zeilen = {z[0]: z for z in r}
        zeilen.update({z[0]: z for z in plan})
        for fp, t in neu_text.items():
            fp.write_text(t, encoding="utf-8", newline="")
        PLAN.parent.mkdir(parents=True, exist_ok=True)
        with PLAN.open("w", encoding="utf-8", newline="") as h:
            w = csv.writer(h)
            w.writerow(kopfzeile)
            w.writerows(zeilen[k] for k in sorted(zeilen))
        print(f"\n[APPLY] {len(neu_text)} Dateien geschrieben, Liste ({len(zeilen)} Zeilen): "
              f"{PLAN.relative_to(REPO)}")
    else:
        print("\n[DRY-RUN] --apply zum Schreiben")
    return 0


if __name__ == "__main__":
    sys.exit(main())
