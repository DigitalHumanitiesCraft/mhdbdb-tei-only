#!/usr/bin/env python3
"""#198 Schritt 2: die drei zurueckgehaltenen NOM-Tokens unter lemma_2598.

PR #205 (Schritt 1) hat 714 habe/hab/hawe-Tokens disambiguiert und dabei drei
Faelle bewusst offen gelassen, weil sie eine philologische Entscheidung
brauchten (ingest/pos-disambig/198-habe-nom/review-faelle.csv, action=REVIEW).
Solange sie ein NOM tragen, kann das <pos>NOM</pos> nicht aus dem
lexicon-Eintrag lemma_2598 verschwinden: das Lexikon widerspraeche dem Korpus.

Entscheidung von Julia Hintersteiner am 2026-08-21:

  AC3_23010_1   "hawe vnd schaufel"          -> lemma_9644 houwe (Haue), NOM
  DA_8222_3     "dehein habe ... diu bezzer" -> lemma_2593 habe (Besitz), NOM
  JT_6192000_1  "und habe diu werch gemeine" -> verbal, NOM aus dem Compound

Zu @corresp bei AC3_23010_1: type_117159 *hawe* bleibt stehen, obwohl er heute
unter lemma_2598 gefuehrt wird. Die Form IST *hawe*, eine zweite type-id fuer
dieselbe Oberflaeche waere ein Duplikat. extract-variants.py ordnet jede type-id
per Mehrheit genau einem Lemma zu; die Mehrheit liegt weiter bei lemma_2598,
solange die uebrigen *hawe*-Belege (Imperative zu houwen) dort haengen. Das ist
Gegenstand des houwen-Folgetickets und kippt dann von selbst. Der Lauf meldet
den Fall als "type ids with >1 lemma".

Nur @lemmaRef/@pos/@corresp aendern sich; Token-Text, Reihenfolge und xml:id
bleiben byte-identisch (Invariante POS-TAGSET.md §6.3.4).

Usage:
    python scripts/ingest/pos-disambig/fix-198-restfaelle.py [--apply]

Ohne --apply: Dry-Run. Nicht idempotent: das Skript verifiziert die Alt-Werte,
ein zweiter Lauf nach --apply bricht deshalb sichtbar ab.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEI_DIR = REPO / "tei"

# xml_id -> (Datei, Form, Alt-Zustand, Neu-Zustand, Begruendung)
# Zustand: (lemmaRef, pos, corresp); None bei ana heisst "Attribut fehlt".
CASES = [
    {
        "file": "AC3.tei.xml",
        "xml_id": "AC3_23010_1",
        "form": "hawe",
        "old": ("lexicon.xml#lemma_2598", "NOM", "variants.xml#type_117159"),
        "new": ("lexicon.xml#lemma_9644", "NOM", "variants.xml#type_117159"),
        "grund": "Geraetepaar 'hawe vnd schaufel' als Satzsubjekt: Substantiv houwe (Haue), nicht haben",
    },
    {
        "file": "DA.tei.xml",
        "xml_id": "DA_8222_3",
        "form": "habe",
        "old": ("lexicon.xml#lemma_2598", "NOM VRB VEX", "variants.xml#type_8730"),
        "new": ("lexicon.xml#lemma_2593", "NOM", "variants.xml#type_8699"),
        "grund": "'dehein habe' ist eine NP, das feminine Relativpronomen diu kongruiert mit habe (stf.); bei Hilfsverblesart stuende habe hinter gesehen",
    },
    {
        "file": "JT.tei.xml",
        "xml_id": "JT_6192000_1",
        "form": "habe",
        "old": ("lexicon.xml#lemma_2598", "NOM VRB VEX", "variants.xml#type_8730"),
        "new": ("lexicon.xml#lemma_2598", "VRB VEX", "variants.xml#type_8730"),
        "grund": "Konjunktiv mit Akkusativobjekt 'diu werch', kein Determinativ davor: verbal",
    },
]

W_RE_TEMPLATE = (
    r'<w xml:id="{xid}" lemmaRef="(?P<lemmaRef>[^"]*)" pos="(?P<pos>[^"]*)"'
    r'(?: ana="(?P<ana>[^"]*)")?(?: corresp="(?P<corresp>[^"]*)")?>'
)


def main() -> int:
    apply = "--apply" in sys.argv
    changed_files = 0

    for case in CASES:
        fp = TEI_DIR / case["file"]
        # newline="" beim Lesen UND Schreiben: der Korpus mischt LF und CRLF
        # (WZB ist CRLF), und die Zeilenenden sollen byte-identisch bleiben.
        # open() statt Path.read_text(newline=...): das Keyword gibt es erst ab
        # Python 3.13, die Build-Skripte laufen hier unter 3.11.
        with fp.open(encoding="utf-8", newline="") as fh:
            text = fh.read()
        m = re.search(W_RE_TEMPLATE.format(xid=re.escape(case["xml_id"])), text)
        if not m:
            sys.exit(
                f"FEHLER: {case['file']}: <w xml:id={case['xml_id']}> nicht im "
                f"erwarteten Attributmuster gefunden"
            )

        got = (m.group("lemmaRef"), m.group("pos"), m.group("corresp"))
        if got != case["old"]:
            sys.exit(
                f"FEHLER: {case['xml_id']}: Ist-Zustand {got} weicht vom erwarteten "
                f"Alt-Zustand {case['old']} ab (bereits gelaufen?)"
            )

        new_lemma, new_pos, new_corresp = case["new"]
        ana = m.group("ana")
        new_tag = f'<w xml:id="{case["xml_id"]}" lemmaRef="{new_lemma}" pos="{new_pos}"'
        if ana:
            new_tag += f' ana="{ana}"'
        if new_corresp:
            new_tag += f' corresp="{new_corresp}"'
        new_tag += ">"

        print(f"  {case['xml_id']}  {case['form']!r}")
        print(f"    alt: {m.group(0)}")
        print(f"    neu: {new_tag}")
        print(f"    grund: {case['grund']}")

        if apply:
            with fp.open("w", encoding="utf-8", newline="") as fh:
                fh.write(text[: m.start()] + new_tag + text[m.end():])
            changed_files += 1
        print()

    mode = "APPLY" if apply else "DRY-RUN"
    print(f"[{mode}] {len(CASES)} Faelle, {changed_files} Dateien geschrieben")
    if not apply:
        print("Dry-Run. Erneut mit --apply ausfuehren, um zu schreiben.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
