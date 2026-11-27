#!/usr/bin/env python3
"""22-header-stand.py: Bearbeitungsstand der Phasen 1 bis 3 in den Header von APK.tei.xml (#262).

Misst die Abdeckung von @lemmaRef, @pos, @ana und @corresp an den <w> im <body> ausserhalb von
<head> (dieselbe Bezugsgroesse wie 21-abdeckung.py) und schreibt sie

  - in encodingDesc/editorialDecl/normalization (ersetzt den Absatz aus Stufe 0) und
  - als <change> in revisionDesc (eine Zeile mit dem Kennwort "Phasen 1 bis 3", wird ersetzt).

Idempotent: ein zweiter Lauf auf demselben Stand mit denselben Argumenten (--datum, --stand,
--handkorrektur) aendert nichts. Ohne --stand und --handkorrektur faellt der Satz zur Handkorrektur
still weg; der Aufruf des letzten Laufs steht in scripts/ingest/apk/README.md (die Vorgabe
fuer --datum ist heute, ein Lauf an einem anderen Tag ersetzt Datum und change-Zeile). Validiert danach gegen das Schema.

--stand setzt nur das Datum im Absatz (Vorgabe --datum), --handkorrektur haengt einen Satz an den Absatz.

Aufruf: python -P -E scripts/ingest/apk/22-header-stand.py [--datum JJJJ-MM-TT] [--stand JJJJ-MM-TT] [--handkorrektur "Satz"]
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apk_common as ac  # noqa: E402

TEI = "{http://www.tei-c.org/ns/1.0}"
SCHEMA = ac.REPO / "schema" / "mhdbdb.rng"
KENNWORT = "Phasen 1 bis 3"


def de(x):
    return f"{x:,}".replace(",", ".")


def prozent(n, d):
    return f"{100 * n / d:.1f}".replace(".", ",") + " %"


def main():
    ac.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datum", default=datetime.date.today().isoformat())
    ap.add_argument("--stand", help="Datum im Absatz (Vorgabe: --datum), die change-Zeile behaelt --datum")
    ap.add_argument("--handkorrektur", help="Satz, der an den Absatz angehaengt wird (von Hand gesetzte Woerter)")
    a = ap.parse_args()
    a.stand = a.stand or a.datum
    text = ac.AUSGABE.read_text(encoding="utf-8")
    baum = etree.fromstring(text.encode("utf-8"))
    body = baum.find(f"{TEI}text/{TEI}body")
    ws = [w for w in body.iter(f"{TEI}w") if not any(x.tag == f"{TEI}head" for x in w.iterancestors())]
    n = len(ws)
    z = {att: sum(1 for w in ws if w.get(att)) for att in ("lemmaRef", "pos", "ana", "corresp")}
    if not n or not z["lemmaRef"]:
        raise ac.HarterFehler("keine annotierten <w>: erst die Phasen fahren")
    absatz = (f"Maschinell annotiert (#262, Stand {a.stand}): Lemma (@lemmaRef) {de(z['lemmaRef'])}, "
              f"Wortart (@pos) {de(z['pos'])}, Bedeutung (@ana) {de(z['ana'])}, Variantentyp (@corresp) "
              f"{de(z['corresp'])} von {de(n)} Wörtern im Text ohne die Rubrik "
              f"({prozent(z['lemmaRef'], n)}, {prozent(z['pos'], n)}, {prozent(z['ana'], n)}, "
              f"{prozent(z['corresp'], n)}). Eindeutige Fälle aus dem Lexikon, mehrdeutige durch ein "
              f"Sprachmodell entschieden (Entscheidungstabellen in ingest/apk/phase1 bis phase3), "
              f"die maschinellen Zuweisungen nicht von Hand geprüft.")
    if a.handkorrektur:
        if "<" in a.handkorrektur or "&" in a.handkorrektur:
            raise ac.HarterFehler("--handkorrektur darf kein < und & enthalten")
        absatz += " " + a.handkorrektur.strip()
    change = (f"#262, {KENNWORT}: Lemma, Wortart, Bedeutung und Variantentyp maschinell gesetzt via "
              f"scripts/ingest/apk/10 bis 18; keine neuen Lemmata oder Bedeutungen.")

    # der Absatz zum Bearbeitungsstand in <normalization>: aus Stufe 0 oder aus einem frueheren Lauf
    stand = list(re.finditer(r"<p>(?:Noch nicht lemmatisiert und disambiguiert\.|Maschinell annotiert "
                             r"\(#262[^<]*)</p>", text))
    if len(stand) != 1:
        raise ac.HarterFehler(f"Absatz zum Bearbeitungsstand {len(stand)}x gefunden, erwartet 1")
    alt_p, neu_p = stand[0].group(0), f"<p>{absatz}</p>"
    text = text[:stand[0].start()] + neu_p + text[stand[0].end():]

    zeile = f'<change when="{a.datum}" who="#mhdbdb-team">{change}</change>'
    vorhanden = re.search(r'[ \t]*<change [^>]*>#262, ' + re.escape(KENNWORT) + r':.*?</change>\n', text)
    if vorhanden:
        text = text[:vorhanden.start()] + vorhanden.group(0)[:len(vorhanden.group(0)) - len(vorhanden.group(0).lstrip())] \
            + zeile + "\n" + text[vorhanden.end():]
    else:
        m = re.search(r"\n([ \t]*)</revisionDesc>", text)
        if not m:
            raise ac.HarterFehler("revisionDesc nicht gefunden")
        einzug = m.group(1) + "  "
        text = text[:m.start()] + "\n" + einzug + zeile + text[m.start():]

    neu = etree.fromstring(text.encode("utf-8"))
    rng = etree.RelaxNG(etree.parse(str(SCHEMA)))
    if not rng.validate(etree.ElementTree(neu)):
        raise ac.HarterFehler(f"Schema: {rng.error_log.last_error}")
    with open(ac.AUSGABE, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"Bezugsgroesse: {de(n)} <w> im body ohne head")
    for att, v in z.items():
        print(f"  @{att}: {de(v)} ({prozent(v, n)})")
    if not vorhanden:
        ch = "neu"
    else:
        ch = "unveraendert" if vorhanden.group(0).strip() == zeile else "ersetzt"
    print(f"normalization: {'ersetzt' if alt_p != neu_p else 'unveraendert'}; change: {ch}; Schema gueltig")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ac.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
