#!/usr/bin/env python3
"""Autorangaben im titleStmt gegen persons.xml pruefen (#228).

Anlass: sieben Texte trugen ein <author ref="#person_N"/> OHNE Textinhalt.
Die Referenz war intakt, nur der Name fehlte, und im Frontend erschienen die
Texte dadurch ohne Autor. Der Fall war jahrelang unsichtbar, weil ihn nichts
geprueft hat: die Referenz loest ja auf, und ein leeres Element ist
schema-valide (mhdbdb.rnc verlangt keinen Textinhalt).

Geprueft wird das Feld, aus dem der Korpus-Index text.author speist
(build-corpus-index.py, //tei:titleStmt/tei:author; der Index nimmt bei
mehreren Autoren nur den ersten, das Audit prueft alle). Sechs Klassen, die sich ueberschneiden koennen:

  leer        <author ref="..."/> ohne Textinhalt: Text erscheint autorlos
  toter-ref   @ref zeigt auf eine ID, die es in persons.xml nicht gibt
  praefix     @ref weicht von der Form "#person_N" ab, entweder mit
              Dateinamen davor oder ganz ohne Doppelkreuz. Beides loest auf,
              beides ist im Korpus die Ausnahme
  abweichend  Textinhalt != preferred-Name der referenzierten Person
  ohne-ref    <author> ganz ohne @ref (heute 0)
  whitespace  Textinhalt enthaelt Zeilenumbrueche oder Mehrfach-Leerzeichen.
              Nach Normalisierung passt er zum preferred-Namen, roh aber
              nicht: genau so stand LUU bis #228 in Index und API

Nur "leer" und "toter-ref" sind eindeutig Fehler. "abweichend" ist oft eine
legitime bibliographische Variante und braucht eine fachliche Entscheidung,
deshalb meldet das Skript es getrennt und ohne Exit-Code.

Seit #308 wird zusaetzlich der zweite Ort geprueft, an dem ein Header einen
Personennamen fuehrt: particDesc/listPerson/person/persName[@type="preferred"].
Anders als der titleStmt ist das ein reiner Spiegel von persons.xml, adressiert
ueber @corresp, und eine Abweichung ist deshalb nie eine Variante, sondern
immer ein veralteter Spiegel:

  spiegel        preferred-Form im particDesc != preferred-Form in persons.xml
  spiegel-tot    @corresp zeigt auf eine ID, die es in persons.xml nicht gibt
  ohne-preferred person-Eintrag ganz ohne persName[@type="preferred"]. Heute
                 0 von 671, aber ohne eigene Klasse waere er ein stilles Loch:
                 wer die preferred-Zeile loescht, faellt sonst nur aus der
                 Grundmenge und loest keine Meldung aus
  spiegel-fehlt  eine Autoren-ID aus dem titleStmt hat keinen Eintrag im
                 particDesc derselben Datei. Das ist die Untergrenze der
                 Grundmenge, und sie kommt aus den Daten und nicht aus einer
                 committeten Zahl: wer ein ganzes <person>-Element loescht,
                 faellt in keine der Klassen darueber, weil die sich alle auf
                 vorhandene Eintraege beziehen. Eine gezaehlte Menge kann ihr
                 eigenes Schrumpfen nicht melden. Die eine Sigle, die heute
                 ein leeres listPerson fuehrt, steht namentlich in LEERE_LISTPERSON,
                 und das Skript meldet sie, sobald sie ueberfluessig wird

Der Anlass: af2000a06 hat person_1249 auf "Jakob von Warte" gezogen und
tei/SJW.tei.xml:121 stehen lassen, wodurch die Datei sich nach der Korrektur
weiter widersprach.

Warum der Block altert: er entsteht beim Ingest als Vorlage
(scripts/ingest/ari/01-convert-original-to-mhdbdb.py:135-141 emittiert ihn
woertlich, scripts/_archived/tei-transformation.py hat ihn 2025 gebaut) und
wird danach von keinem Sync-Skript mehr angefasst. Gelesen hat ihn bis #308
auch nichts: build-corpus-index.py nimmt den Autor aus dem titleStmt.
Wirksam wird er nach aussen, bei jeder Nachnutzung, die den Header als
Autoritaet liest.

Nicht geprueft, und das ist Absicht: die alternative-Formen und die idno-Zeilen
im selben Block sind weitere ungeprueffte Spiegel, und die lokale xml:id wird
nicht gegen @corresp gehalten (LUU fuehrt dort als einzige Datei eine UUID).

Usage:
    python scripts/audit/check-author-refs.py           # Bericht
    python scripts/audit/check-author-refs.py --check   # exit 1 bei leer/toter-ref/spiegel
"""
import argparse
import sys
from pathlib import Path

from lxml import etree

# Gemeinsame Korpusauswahl (#287).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from corpus_files import corpus_files  # noqa: E402

NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

# Siglen mit leerem <listPerson/>, benannt statt gezaehlt. Gemessen am
# 15.09.2026 ueber alle 667 Dateien: 672 titleStmt-Autoren mit @ref, kein
# einziger ohne, 671 particDesc-Eintraege in 666 Dateien, und kein Eintrag ohne
# zugehoerigen Autor. Die Differenz ist genau dieser eine Fall.
LEERE_LISTPERSON = {
    'VOR': 'Die Datei fuehrt als einzige ein leeres <listPerson/> (Zeile 134), '
           'also particDesc ohne Person. Ob der Autor dort nachgetragen wird, '
           'ist eine Modellfrage fuer KZW und hier bewusst nicht entschieden '
           '(#228/#308).',
}


def preferred_names(root: Path) -> dict:
    tree = etree.parse(str(root / 'authority-files' / 'persons.xml'))
    out = {}
    for person in tree.xpath('//tei:person', namespaces=NS):
        pid = person.get('{http://www.w3.org/XML/1998/namespace}id')
        name = person.xpath('./tei:persName[@type="preferred"]/text()', namespaces=NS)
        out[pid] = ' '.join(name[0].split()) if name else ''
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true',
                    help='exit 1 bei leerem/totem @ref oder veraltetem particDesc-Spiegel')
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    pref = preferred_names(root)

    leer, tot, praefix, abweichend, ohne_ref, ws = [], [], [], [], [], []
    spiegel, spiegel_tot, ohne_preferred, spiegel_geprueft = [], [], [], 0
    spiegel_fehlt, ausnahme_ueberfluessig = [], []
    for path in corpus_files():
        sigle = path.name.replace('.tei.xml', '')
        tree = etree.parse(str(path))
        corresp_ids, autor_ids = set(), set()
        for person in tree.xpath('//tei:particDesc/tei:listPerson/tei:person',
                                 namespaces=NS):
            # Adressiert wird ueber @corresp, nicht ueber die lokale xml:id:
            # LUU fuehrt dort eine UUID (person_05154796-...), korpusweit der
            # einzige Fall, und das @corresp daneben loest korrekt auf.
            corresp = person.get('corresp') or ''
            pid = corresp.split('#')[-1]
            if corresp:
                corresp_ids.add(pid)
            names = person.xpath('./tei:persName[@type="preferred"]',
                                 namespaces=NS)
            if not names:
                # Nicht stillschweigend ueberspringen: ein Eintrag ohne
                # preferred-Zeile faellt sonst aus der Grundmenge und der
                # Zaehler sinkt, ohne dass etwas rot wird.
                ohne_preferred.append((sigle, corresp or '(kein @corresp)'))
                continue
            form = ' '.join(''.join(names[0].itertext()).split())
            if pid not in pref:
                spiegel_tot.append((sigle, corresp or '(kein @corresp)', form))
                continue
            spiegel_geprueft += 1
            if form != pref[pid]:
                spiegel.append((sigle, pid, form, pref[pid]))
        for author in tree.xpath('//tei:titleStmt/tei:author', namespaces=NS):
            raw_text = ''.join(author.itertext()).strip()
            text = ' '.join(raw_text.split())
            if text != raw_text:
                # Die Normalisierung schuetzt die abweichend-Klasse vor
                # Fehlalarmen, wuerde den Befund sonst aber wegblenden.
                ws.append((sigle, raw_text))
            raw = author.get('ref') or ''
            if not raw:
                ohne_ref.append((sigle, text))
                continue
            if not raw.startswith('#'):
                # Deckt beide Abweichungen ab: den Dateinamen davor
                # ("persons.xml#person_N") und das ganz fehlende Doppelkreuz
                # ("person_N"). Beides loest heute im Frontend auf, beides ist
                # eine stille Abweichung von der Konvention der uebrigen Texte.
                praefix.append((sigle, raw))
            pid = raw.split('#')[-1]
            autor_ids.add(pid)
            if pid not in pref:
                tot.append((sigle, raw))
                continue
            if not text:
                leer.append((sigle, pid))
            elif text != pref[pid]:
                abweichend.append((sigle, pid, text, pref[pid]))
        # Die Erwartung kommt aus der Datei selbst, nicht aus einer Baseline:
        # jeder Autor des titleStmt hat seinen Spiegel im particDesc. Ohne das
        # faellt ein geloeschtes <person>-Element in keine Klasse, die
        # Grundmenge sinkt still und --check bleibt gruen (CI-Review-Bot auf
        # PR #438). Eine gezaehlte Menge kann ihr eigenes Schrumpfen nicht
        # melden; eine Invariante braucht keine Zahl.
        # Die Ausnahme haengt an der Bedingung und nicht am Siglennamen: sie
        # gilt nur, solange die Datei wirklich ein leeres listPerson fuehrt.
        # Sonst schaltet sie fuer die genannte Sigle die ganze Invariante ab
        # und laesst auch eine falsche Person durch, waehrend "veraltete
        # Ausnahme" keinen Exit-Code traegt, den in einem gruenen Schritt
        # jemand liest.
        ausgenommen = sigle in LEERE_LISTPERSON and not corresp_ids
        if not ausgenommen:
            for pid in sorted(autor_ids - corresp_ids):
                spiegel_fehlt.append((sigle, pid))
        if sigle in LEERE_LISTPERSON and corresp_ids:
            ausnahme_ueberfluessig.append(sigle)

    print(f'Geprueft: {len(corpus_files())} Korpusdateien')
    print()
    print(f'  leer (ohne Textinhalt)       {len(leer)}')
    for sigle, pid in leer:
        print(f'      {sigle:6} {pid}')
    print(f'  toter @ref                   {len(tot)}')
    for sigle, raw in tot:
        print(f'      {sigle:6} {raw}')
    print(f'  @ref nicht in der Form #ID   {len(praefix)}')
    for sigle, raw in praefix:
        print(f'      {sigle:6} {raw}')
    print(f'  ohne @ref                    {len(ohne_ref)}')
    for sigle, text in ohne_ref:
        print(f'      {sigle:6} {text!r}')
    print(f'  Whitespace im Namen          {len(ws)}')
    for sigle, raw in ws:
        print(f'      {sigle:6} {raw!r}')
    print()
    print(f'  particDesc-Spiegel geprueft  {spiegel_geprueft}')
    print(f'  Spiegel veraltet             {len(spiegel)}')
    for sigle, pid, form, name in spiegel:
        print(f'      {sigle:6} {pid:12} Header {form!r} <-> persons.xml {name!r}')
    print(f'  Spiegel-@corresp tot         {len(spiegel_tot)}')
    for sigle, corresp, form in spiegel_tot:
        print(f'      {sigle:6} {corresp} {form!r}')
    print(f'  Spiegel ohne preferred-Zeile {len(ohne_preferred)}')
    for sigle, corresp in ohne_preferred:
        print(f'      {sigle:6} {corresp}')
    print(f'  Autor ohne Spiegel           {len(spiegel_fehlt)}')
    for sigle, pid in spiegel_fehlt:
        print(f'      {sigle:6} {pid} steht im titleStmt, nicht im particDesc')
    if ausnahme_ueberfluessig:
        print()
        print('  Veraltete Ausnahme, bitte aus LEERE_LISTPERSON entfernen:')
        for sigle in ausnahme_ueberfluessig:
            print(f'      {sigle:6} fuehrt inzwischen mindestens eine Person')
    print()
    for sigle, grund in sorted(LEERE_LISTPERSON.items()):
        if sigle not in ausnahme_ueberfluessig:
            print(f'  Leeres listPerson, bewusst: {sigle} - {grund}')
    print()
    print(f'  Text weicht vom preferred-Namen ab: {len(abweichend)}')
    print('      (kein Fehler an sich, aber jeder Fall ist eine Entscheidung)')
    for sigle, pid, text, name in abweichend:
        print(f'      {sigle:6} {pid:12} TEI {text!r} <-> persons.xml {name!r}')

    if args.check and (leer or tot or spiegel or spiegel_tot or ohne_preferred
                       or spiegel_fehlt):
        sys.exit(1)


if __name__ == '__main__':
    main()
