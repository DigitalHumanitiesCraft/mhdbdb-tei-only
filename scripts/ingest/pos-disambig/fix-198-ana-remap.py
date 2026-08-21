#!/usr/bin/env python3
"""#198 Schritt 2: das @ana der umgehaengten habe-Tokens wiederherstellen.

PR #205 hat 25 Tokens von lemma_2598 *haben* auf lemma_2593 *habe* umgehaengt und
dabei ihr @ana entfernt, weil die Sense-Zuordnung am Sense-Review haengt
(Issue-Kommentar vom 2026-07-10: "damit sie beim Sense-Split re-mappt werden
koennen"). Ohne diesen Schritt stuenden 26 von 101 lemma_2593-Tokens ohne Sense,
also schlechter als vor #205.

Die alten Werte taugen dabei nicht als Vorlage, sie waren Teil des Fehlers:
24 der 25 zeigten auf lemma_2598_sense_77622, den Hilfsverb-Sense mit den
Konzepten "Zeit" und "Funktionswoerter".

Entscheidung von Julia Hintersteiner am 2026-08-21, nach Durchsicht der Belege:

  24 WZB-Belege + DA_8222_3  -> lemma_2593_sense_4159 (Objektbezogene
        Aktivitaet + Besitz). Durchweg "Besitz, Vermoegen": "alle seine habe
        vnd sein vich", "in vil habe vnd reichtum". Der Sense traegt im Korpus
        bereits 59 Belege.
  TKA_950041520_4            -> KEIN @ana. "von einer gar bosen habe" (Mord an
        Wenzel III., Olmuetz 1306) meint eine Handlungsweise; kein Sense von
        lemma_2593 deckt das ab. Lieber leer als falsch.
  AC3_23010_1                -> lemma_9644_sense_15624. Der Token wurde in
        fix-198-restfaelle.py auf lemma_9644 *houwe* umgehaengt, und dieses
        Lemma hat genau einen Sense: die Zuordnung ist damit keine Wahl mehr.

Zwei weitere lemma_2593-Tokens ohne @ana (FB_627018_3, TRO_10715_5) stammen aus
dem Altbestand, waren nie Gegenstand von #198 und bleiben unberuehrt.

@ana wird zwischen @pos und @corresp eingesetzt, in der Attributreihenfolge des
Korpus. Alles andere bleibt byte-identisch (Invariante POS-TAGSET.md §6.3.4).

Usage:
    python scripts/ingest/pos-disambig/fix-198-ana-remap.py [--apply]

Ohne --apply: Dry-Run. Nicht idempotent: das Skript besteht darauf, dass das
Token noch kein @ana traegt, ein zweiter Lauf bricht deshalb sichtbar ab.
"""
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEI_DIR = REPO / "tei"

SENSE_BESITZ = "lexicon.xml#lemma_2593_sense_4159"
SENSE_HOUWE = "lexicon.xml#lemma_9644_sense_15624"

# xml_id -> (erwartetes lemmaRef, zu setzendes ana)
ASSIGN = {xid: ("lexicon.xml#lemma_2593", SENSE_BESITZ) for xid in [
    "DA_8222_3",
    "WZB_7vb_7_4", "WZB_8rb_7_7", "WZB_11rb_33_2", "WZB_12ra_32_5",
    "WZB_13ra_4_0", "WZB_13ra_21_1", "WZB_30rb_17_2", "WZB_30va_14_0",
    "WZB_30vb_10_2", "WZB_30vb_17_4", "WZB_31va_8_3", "WZB_34vb_27_1",
    "WZB_36rb_16_2", "WZB_40ra_14_4", "WZB_127vb_35_2", "WZB_150va_15_3",
    "WZB_169rb_7_0", "WZB_187vb_20_1", "WZB_198rb_10_4", "WZB_204rb_28_0",
    "WZB_204vb_19_2", "WZB_206rb_30_1", "WZB_220rb_25_0", "WZB_236rb_32_7",
]}
ASSIGN["AC3_23010_1"] = ("lexicon.xml#lemma_9644", SENSE_HOUWE)

# Ohne @ana, bewusst: siehe Modul-Docstring
SKIP = {"TKA_950041520_4", "FB_627018_3", "TRO_10715_5"}

W_RE_TEMPLATE = (
    r'<w xml:id="{xid}" lemmaRef="(?P<lemmaRef>[^"]*)" pos="(?P<pos>[^"]*)"'
    r'(?: ana="(?P<ana>[^"]*)")?(?: corresp="(?P<corresp>[^"]*)")?>'
)


def sigle_of(xml_id):
    """WZB_30vb_17_4 -> WZB. Die Sigle ist das Praefix bis zum ersten '_'."""
    return xml_id.split("_", 1)[0]


def main() -> int:
    apply = "--apply" in sys.argv

    by_file = {}
    for xid in ASSIGN:
        by_file.setdefault(f"{sigle_of(xid)}.tei.xml", []).append(xid)

    stats = Counter()
    for fname in sorted(by_file):
        fp = TEI_DIR / fname
        # newline="": der Korpus mischt LF und CRLF (WZB ist CRLF).
        # open() statt Path.read_text(newline=...), das Keyword gibt es erst
        # ab Python 3.13; die Build-Skripte laufen hier unter 3.11.
        with fp.open(encoding="utf-8", newline="") as fh:
            text = fh.read()

        # Rueckwaerts ersetzen, damit frueh gefundene Offsets gueltig bleiben.
        edits = []
        for xid in by_file[fname]:
            want_lemma, want_ana = ASSIGN[xid]
            m = re.search(W_RE_TEMPLATE.format(xid=re.escape(xid)), text)
            if not m:
                sys.exit(f"FEHLER: {fname}: <w xml:id={xid}> nicht im erwarteten Attributmuster gefunden")
            if m.group("lemmaRef") != want_lemma:
                sys.exit(f"FEHLER: {xid}: lemmaRef ist {m.group('lemmaRef')}, erwartet {want_lemma}")
            if m.group("ana"):
                sys.exit(f"FEHLER: {xid}: traegt bereits ana={m.group('ana')} (bereits gelaufen?)")

            new_tag = f'<w xml:id="{xid}" lemmaRef="{want_lemma}" pos="{m.group("pos")}" ana="{want_ana}"'
            if m.group("corresp"):
                new_tag += f' corresp="{m.group("corresp")}"'
            new_tag += ">"
            edits.append((m.start(), m.end(), new_tag))
            stats[want_ana.split("#")[-1]] += 1

        for start, end, new_tag in sorted(edits, reverse=True):
            text = text[:start] + new_tag + text[end:]
        if apply:
            with fp.open("w", encoding="utf-8", newline="") as fh:
                fh.write(text)
            stats["dateien_geaendert"] += 1

    mode = "APPLY" if apply else "DRY-RUN"
    print(f"[{mode}] {len(ASSIGN)} Tokens: {dict(stats)}")
    print(f"Bewusst ohne @ana gelassen: {', '.join(sorted(SKIP))}")
    if not apply:
        print("Dry-Run. Erneut mit --apply ausfuehren, um zu schreiben.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
