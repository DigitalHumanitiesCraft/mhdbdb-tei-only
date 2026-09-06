#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verdicts einer Homographie-Serie ins TEI schreiben.

Verallgemeinerung von fix-216-minne.py (Serie 1). Was dort als Konstante im
Code stand (gueltige Lemmata, POS-Tags, die Zuordnung von Schreibung und Lemma
zum Variantentyp), kommt hier aus einer config.json je Serie, die im
Batch-Ordner neben cases.json liegt und mitcommittet wird.

Geschrieben wird ausschliesslich per Textersetzung am unannotierten <w>-Tag,
nicht ueber lxml: eine Serialisierung wuerde das ganze Dokument neu schreiben
und den Diff unlesbar machen. Vor jeder Ersetzung wird geprueft, dass das Ziel
noch unannotiert ist, den erwarteten Tokentext traegt und dasselbe @pos wie zur
Extraktionszeit. Ein Replay setzt damit den Korpusstand vor dem Batch voraus.

Zurueckgehalten wird (Reihenfolge fest, der erste zutreffende Grund gewinnt):
  confidence       das Verdict traegt nicht confidence=high
  prior-konflikt   ein bestehendes @pos widerspricht dem Verdict
  verdict-klasse   das Paar aus Lemma und Wortart steht in review_verdicts der
                   config. Fuer Klassen, die eine Serie grundsaetzlich nicht
                   selbst entscheidet, egal wie sicher das Modell ist. Serie 1
                   (#216) hatte diese Regel als feste Zeile im Skript, fuer die
                   Personifikation ("alle NAM-Verdicts gehen ins Review"); hier
                   ist sie eine Angabe der Serie statt einer des Werkzeugs.
  kein-typ         fuer (Schreibung, Lemma) gibt es keinen Variantentyp im
                   Bestand. Ob das abbricht oder in den Review fuehrt, sagt
                   kein_typ_bedeutet_review in der config: praegt eine Serie
                   grundsaetzlich keine neuen Typen, ist ein fehlender Typ ein
                   Fehler; kennt sie belegte Ausnahmen, ist er ein Review-Fall.

Usage:
    python scripts/ingest/pos-disambig/apply-homograph.py \
        --config ingest/pos-disambig/369-stat/config.json \
        --cases  ingest/pos-disambig/369-stat/cases.json \
        --actions ingest/pos-disambig/369-stat/actions.json \
        --out-dir ingest/pos-disambig/369-stat [--apply]
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEI_DIR = REPO / "tei"

# xml:id zuerst, dann optional pos="...", kein weiteres Attribut. Das gilt fuer
# unannotierte Tokens; annotierte matchen absichtlich nicht.
W_TEMPLATE = r'<w xml:id="{xid}"(?: pos="(?P<oldpos>[A-Z]+)")?>(?P<form>[^<]*)</w>'


def pfad(p):
    p = Path(p)
    return p if p.is_absolute() else REPO / p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--cases", required=True)
    ap.add_argument("--actions", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    cfg = json.loads(pfad(args.config).read_text(encoding="utf-8"))
    valid_lemmas = set(cfg["lemmas"])
    valid_pos = set(cfg["pos"])
    corresp = cfg["corresp"]
    kein_typ_review = cfg.get("kein_typ_bedeutet_review", False)
    review_verdicts = set(cfg.get("review_verdicts", []))

    actions = {a["xml_id"]: a for a in
               json.loads(pfad(args.actions).read_text(encoding="utf-8"))}
    cases = {c["xml_id"]: c for c in
             json.loads(pfad(args.cases).read_text(encoding="utf-8"))}
    if set(actions) != set(cases):
        sys.exit("FEHLER: Aktionen decken Faelle nicht exakt ab (fehlend: %d, fremd: %d)"
                 % (len(set(cases) - set(actions)), len(set(actions) - set(cases))))

    je_datei = {}
    for xid, c in cases.items():
        je_datei.setdefault(c["file"], []).append(xid)

    zeilen = []
    stats = Counter()
    verdicts = Counter()
    for fname in sorted(je_datei):
        fp = TEI_DIR / fname
        text = fp.read_text(encoding="utf-8", newline="")
        geaendert = False
        for xid in je_datei[fname]:
            a, c = actions[xid], cases[xid]
            if a["lemma"] not in valid_lemmas:
                sys.exit("FEHLER: %s: unbekanntes Lemma %r" % (xid, a["lemma"]))
            if a["pos"] not in valid_pos:
                sys.exit("FEHLER: %s: unerwarteter pos-Tag %r" % (xid, a["pos"]))
            m = re.search(W_TEMPLATE.format(xid=re.escape(xid)), text)
            if not m:
                sys.exit("FEHLER: %s: <w xml:id=%s> nicht unannotiert gefunden"
                         % (fname, xid))
            if m.group("form").strip() != c["form"]:
                sys.exit("FEHLER: %s: Tokentext %r != erwartete Form %r"
                         % (xid, m.group("form"), c["form"]))
            if (m.group("oldpos") or "") != c.get("pos_prior", ""):
                sys.exit("FEHLER: %s: @pos im Bestand %r != pos_prior %r"
                         % (xid, m.group("oldpos"), c.get("pos_prior")))

            prior = c.get("pos_prior", "")
            schluessel = c["form"].lower() + "|" + a["lemma"]
            typ = corresp.get(schluessel)

            if a["confidence"] != "high":
                aktion, grund = "REVIEW", "confidence"
            elif prior and prior != a["pos"]:
                aktion, grund = "REVIEW", "prior-konflikt"
            elif a["lemma"] + "/" + a["pos"] in review_verdicts:
                aktion, grund = "REVIEW", "verdict-klasse"
            elif typ is None:
                if not kein_typ_review:
                    sys.exit("FEHLER: %s: kein Bestands-Typ fuer %r" % (xid, schluessel))
                aktion, grund = "REVIEW", "kein-typ"
            else:
                aktion, grund = "ANNOTATE", ""
            stats[aktion] += 1
            if aktion == "ANNOTATE":
                verdicts[a["lemma"] + "/" + a["pos"]] += 1

            neu_lemma = neu_pos = neu_corresp = ""
            if aktion == "ANNOTATE":
                neu_lemma = "lexicon.xml#" + a["lemma"]
                neu_pos = a["pos"]
                neu_corresp = "variants.xml#" + typ
                neu_tag = ('<w xml:id="%s" lemmaRef="%s" pos="%s" corresp="%s">%s</w>'
                           % (xid, neu_lemma, neu_pos, neu_corresp, m.group("form")))
                text = text[:m.start()] + neu_tag + text[m.end():]
                geaendert = True

            zeilen.append({
                "file": fname, "xml_id": xid, "form": c["form"],
                "vers": c.get("verse_n", ""),
                "action": aktion, "review_grund": grund,
                "geaendert": "ja" if aktion == "ANNOTATE" else "nein",
                "alt_pos": prior, "neu_pos": neu_pos,
                "alt_lemmaRef": "", "neu_lemmaRef": neu_lemma,
                "alt_corresp": "", "neu_corresp": neu_corresp,
                "verdict_lemma": a["lemma"], "verdict_pos": a["pos"],
                "confidence": a["confidence"],
                "begruendung": a.get("begruendung", ""),
                # Vers-Faelle mit Nachbarversen, damit die CSV ohne Rueckgriff
                # aufs TEI pruefbar ist: Begruendungen berufen sich auf Material,
                # das im blossen Zielvers nicht steht (Review-Lehre aus #216).
                "kontext": (" / ".join(x for x in (c.get("prev_verse"), c.get("verse"),
                                                   c.get("next_verse")) if x)
                            if c.get("context_mode") == "verse" else c.get("context", "")),
            })
        if geaendert and args.apply:
            fp.write_text(text, encoding="utf-8", newline="")
            stats["dateien_geaendert"] += 1

    if not zeilen:
        sys.exit("FEHLER: keine Faelle verarbeitet, nichts zu schreiben.")

    out = pfad(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    spalten = list(zeilen[0].keys())
    for name, auswahl in (("diff-liste.csv", zeilen),
                          ("review-faelle.csv", [z for z in zeilen
                                                 if z["action"] == "REVIEW"])):
        with open(out / name, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=spalten, delimiter=";")
            w.writeheader()
            w.writerows(auswahl)

    modus = "APPLY" if args.apply else "DRY-RUN"
    print("[%s] %d Faelle: %s" % (modus, len(zeilen), dict(stats)))
    print("  Verdicts der Annotationen:", dict(verdicts))
    print("  Review-Gruende:", dict(Counter(z["review_grund"] for z in zeilen
                                            if z["action"] == "REVIEW")))
    print("  geschrieben:", out / "diff-liste.csv", "und review-faelle.csv")
    if not args.apply:
        print("  (--apply schreibt ins Korpus)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
