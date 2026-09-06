#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#216 Punkt 3: die 155 vrouwe-Tokens vor minne extrahieren und entscheiden.

Anders als die Serien #216/minne, #369/stat und #367 braucht dieser Batch
KEINEN LLM-Lauf. Die Menge ist durch zwei Dinge vollstaendig bestimmt:

  * 150 Faelle sind mechanisch. Ihre Schreibung kommt im Variantenwoerterbuch
    nur unter einem einzigen Lemma vor, naemlich lemma_7260 (vrouwe, NOM).
  * 5 Faelle sind mehrdeutig (die Schreibungen fro und frô stehen auch bei
    lemma_7250, vrô "froh"). Sie sind von @wachauer am 01.09.2026 in #216
    entschieden: "Jedesmal Frau Minne", also ebenfalls lemma_7260.

Das Skript schreibt daher cases.json UND actions.json in einem Lauf. Die
actions.json traegt fuer jeden Fall, woher sein Verdict kommt (Feld "herkunft":
"mechanisch" oder "wachauer-2026-09-01"), damit im Batch-Log nachlesbar bleibt,
welche 5 auf einer menschlichen Entscheidung beruhen und welche 150 nicht.
Angewendet wird beides von apply-homograph.py, wie in jeder anderen Serie.

## Auswahlregel

Ein Fall ist ein Paar aus zwei aufeinanderfolgenden <w> im <body>:

  1. das erste traegt KEIN @lemmaRef und ist formal vrouwe,
  2. das zweite passt auf ^m[iíîy]nn[eè]?$ (Rohform).

**"Formal vrouwe" wird am Bestand erhoben, nicht geraten.** Es ist die Menge
der MHG-normalisierten Oberflaechenformen aller <w>, die lemma_7260 tragen.
Eine handgeschriebene Schreibungsliste waere hier nachweislich falsch: #216
(Kommentar vom 31.08.2026) hat gemessen, dass eine Sechserliste aus HUGO nur
214 von 633 Stellen deckt und ausgerechnet die haeufigste Schreibung nicht
enthaelt. Lemma-Ids werden token-genau verglichen (CONTRACTS.md B.1), nie als
Teilzeichenkette.

**"Unmittelbar" heisst: in der <w>-Folge des <body>, nicht unter den direkten
Kindern der Verszeile.** Das ist keine Feinheit. Am 01.09.2026 gemessen
enthielten 115 der 155 Paare mindestens ein <w>, das in einem <hi> steckt statt
direkt in seinem <l>; ein Durchlauf ueber die direkten Kinder fand nur 40 der
155. Beide Zaehlweisen weist scripts/audit/measure-216-vrouwe-minne.py aus.

**Nach dem Lauf dieses Skripts findet es sich selbst nicht mehr.** Die 152
annotierten Tokens tragen dann ein @lemmaRef und fallen aus Bedingung 1
heraus; ein zweiter Lauf gegen den geaenderten Korpus liefert die 3 Faelle, die
zurueckgehalten wurden. Ein Replay setzt deshalb den Korpusstand vor dem Batch
voraus, so wie apply-homograph.py es ohnehin prueft.

Das Doppel-n im minne-Muster haelt die Possessivformen min/mîn draussen.

## Was das Skript NICHT tut

Es fasst die minne-Tokens nicht an. Alle 155 tragen kein @lemmaRef, und ob sie
das NAM-Lemma "Minne" bekommen, ist der naechste Schritt in #216 und braucht
ein neues Lemma in lexicon.xml. Dieser Batch stellt nur die Voraussetzung her:
die Regel fuer die Personifikation ist als Lemma-Regel formuliert (Vorgaenger
traegt lemma_7260, Form ohne -n) und greift heute an diesen 155 Stellen nicht,
weil der Vorgaenger noch lemmalos ist.

Nur lesend am Korpus, deterministisch (corpus_files-Reihenfolge, Dokumentordnung).

Usage:
    python scripts/ingest/pos-disambig/extract-216-vrouwe155.py \
        --out-dir ingest/pos-disambig/216-vrouwe155
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))
from corpus_files import corpus_files  # noqa: E402
from mhg_normalizer import normalize_mhg  # noqa: E402

from lxml import etree  # noqa: E402

TEI_NS = "http://www.tei-c.org/ns/1.0"
W_TAG = "{" + TEI_NS + "}w"
L_TAG = "{" + TEI_NS + "}l"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

LEMMA_VROUWE = "lemma_7260"
LEMMA_VRO = "lemma_7250"
MINNE_RE = re.compile(r"^m[iíîy]nn[eè]?$")

# Entscheidung von @wachauer in #216 am 01.09.2026 ("Jedesmal Frau Minne"),
# gestellt wurde ihm genau diese Liste von fuenf Belegen. Sie steht hier als
# Menge von xml:id und nicht als Schreibungsregel, weil die Entscheidung fuer
# die Anrede vor minne gilt und ausdruecklich nicht fuer die uebrigen
# fro-Belege in beliebigem Kontext (die liegen in #387).
WACHAUER_20260901 = {
    "RVBR_4826_5",
    "RVBR_6310_4",
    "RVBR_8687_5",
    "SHF_403060_0",
    "GVN_4902008001_9",
}


def norm(s):
    return unicodedata.normalize("NFC", s or "").strip()


def token_text(el):
    return norm("".join(el.itertext()))


def lemma_ids(el):
    """Token-genaue Menge der Lemma-Ids eines @lemmaRef (CONTRACTS.md B.1)."""
    return {v.split("#")[-1] for v in (el.get("lemmaRef") or "").split()}


def verse_of(w):
    for a in w.iterancestors():
        if a.tag == L_TAG:
            return a
    return None


def render(tokens, mark=None):
    teile = []
    for t in tokens:
        txt = token_text(t)
        if not txt:
            continue
        teile.append("**" + txt + "**" if t is mark else txt)
    return " ".join(teile)


def sammle_inventar(dateien):
    """Normalisierte Oberflaechenformen von lemma_7260 und lemma_7250.

    Parst den Korpus ein zweites Mal, statt die Baeume des ersten Laufs zu
    halten. 667 geparste Dokumente gleichzeitig im Speicher sprengen den
    Arbeitsspeicher einer ueblichen Maschine (gemessen: der Prozess wird ohne
    Meldung getoetet). Der zweite Lauf kostet ein paar Minuten und nichts sonst.
    """
    inv = {LEMMA_VROUWE: set(), LEMMA_VRO: set()}
    for fp in dateien:
        root = etree.parse(str(fp)).getroot()
        for w in root.iter(W_TAG):
            ids = lemma_ids(w)
            for lid in (LEMMA_VROUWE, LEMMA_VRO):
                if lid in ids:
                    txt = token_text(w)
                    if txt:
                        inv[lid].add(normalize_mhg(txt))
        root.clear()
    return inv


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    out = Path(args.out_dir)
    if not out.is_absolute():
        out = REPO / out

    dateien = list(corpus_files())
    print("Korpusdateien: %d" % len(dateien))

    # Zwei Durchlaeufe ueber den Korpus: erst das Inventar, dann die Paare.
    # Ein Durchlauf ginge nicht, das Inventar muss vollstaendig sein, bevor der
    # erste Fall geprueft wird.
    inv = sammle_inventar(dateien)
    print("Formeninventar lemma_7260: %d Formen" % len(inv[LEMMA_VROUWE]))
    print("Formeninventar lemma_7250: %d Formen" % len(inv[LEMMA_VRO]))
    print("Schnittmenge: %s" % sorted(inv[LEMMA_VROUWE] & inv[LEMMA_VRO]))

    faelle, aktionen = [], []
    formen = Counter()
    for fp in dateien:
        root = etree.parse(str(fp)).getroot()
        body = root.find(".//{%s}body" % TEI_NS)
        if body is None:
            continue
        ws = list(body.iter(W_TAG))
        txt = [token_text(w) for w in ws]
        for i in range(len(ws) - 1):
            vor, nach = ws[i], ws[i + 1]
            if vor.get("lemmaRef"):
                continue
            if normalize_mhg(txt[i]) not in inv[LEMMA_VROUWE]:
                continue
            if not MINNE_RE.match(txt[i + 1]):
                continue

            xid = vor.get(XML_ID)
            norm_form = normalize_mhg(txt[i])
            mehrdeutig = norm_form in inv[LEMMA_VRO]

            vers = verse_of(vor)
            fall = {
                "file": fp.name,
                "xml_id": xid,
                "form": txt[i],
                "sigle": fp.name.split(".")[0],
                "pos_prior": vor.get("pos") or "",
                "context_mode": "verse" if vers is not None else "prose",
                # Was auf das Token folgt, ist hier der ganze Grund des Falls:
                # ohne die minne-Seite ist nicht nachpruefbar, warum dieses
                # Token in der Menge steht.
                "minne_xml_id": nach.get(XML_ID),
                "minne_form": txt[i + 1],
                "minne_pos_prior": nach.get("pos") or "",
                "minne_rend": (nach.getparent().get("rend") or "")
                if nach.getparent() is not None else "",
            }
            if vers is not None:
                geschwister = list(vers.itersiblings(L_TAG))
                vorher = list(vers.itersiblings(L_TAG, preceding=True))
                fall["verse_n"] = vers.get("n") or ""
                fall["verse"] = render(list(vers.iter(W_TAG)), mark=vor)
                fall["prev_verse"] = (render(list(vorher[0].iter(W_TAG)))
                                      if vorher else "")
                fall["next_verse"] = (render(list(geschwister[0].iter(W_TAG)))
                                      if geschwister else "")
            else:
                fenster = ws[max(0, i - 15):i + 16]
                fall["context"] = render(fenster, mark=vor)
            faelle.append(fall)
            formen[txt[i]] += 1

            if mehrdeutig and xid not in WACHAUER_20260901:
                sys.exit(
                    "FEHLER: %s traegt die mehrdeutige Form %r, steht aber nicht "
                    "in der Entscheidungsliste vom 01.09.2026. Ein solcher Fall "
                    "darf nicht mechanisch entschieden werden." % (xid, txt[i])
                )
            aktionen.append({
                "xml_id": xid,
                "lemma": LEMMA_VROUWE,
                "pos": "NOM",
                "confidence": "high",
                "herkunft": "wachauer-2026-09-01" if mehrdeutig else "mechanisch",
                "begruendung": (
                    "Anrede vor minne; die Schreibung ist zwischen vrouwe und "
                    "vrô mehrdeutig, entschieden von @wachauer am 01.09.2026 "
                    "in #216 ('Jedesmal Frau Minne')."
                    if mehrdeutig else
                    "Die normalisierte Schreibung kommt im Korpus nur unter "
                    "lemma_7260 vor; lemma_7260 traegt genau eine Wortart (NOM). "
                    "Keine Kontextentscheidung noetig."
                ),
            })

    # Die Entscheidungsliste muss aufgehen, sonst beruht ein Verdict auf einer
    # Entscheidung, die es nicht gibt, oder eine Entscheidung liegt brach.
    getroffen = {a["xml_id"] for a in aktionen
                 if a["herkunft"] == "wachauer-2026-09-01"}
    if getroffen != WACHAUER_20260901:
        sys.exit("FEHLER: Entscheidungsliste deckt die mehrdeutigen Faelle nicht "
                 "exakt: fehlend %s, ueberzaehlig %s"
                 % (sorted(WACHAUER_20260901 - getroffen),
                    sorted(getroffen - WACHAUER_20260901)))

    out.mkdir(parents=True, exist_ok=True)
    (out / "cases.json").write_text(
        json.dumps(faelle, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "actions.json").write_text(
        json.dumps(aktionen, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\nFaelle: %d in %d Sigeln"
          % (len(faelle), len({f['sigle'] for f in faelle})))
    print("Schreibungen:", dict(formen))
    print("Herkunft der Verdicts:",
          dict(Counter(a["herkunft"] for a in aktionen)))
    print("Kontextmodus:", dict(Counter(f["context_mode"] for f in faelle)))
    print("geschrieben:", out / "cases.json", "und actions.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
