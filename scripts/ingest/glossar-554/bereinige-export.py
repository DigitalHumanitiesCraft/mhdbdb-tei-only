#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#554 Schritt 1: personenbezogene Daten aus dem WordPress-Export entfernen.

Eingabe: der Originalexport (nicht im Repo). Ausgabe: die bereinigte Fassung
unter sources/glossar-kochbuchforschung/.

Ersetzt wird auf Textebene (Rohstring), nicht ueber einen Parser-Roundtrip,
damit die Datei sonst Byte fuer Byte erhalten bleibt:

  1. Jeder <wp:author>-Block: Login und Anzeigename werden zu author-<id>,
     Mailadresse zu (E-Mail entfernt), Vor- und Nachname werden leer.
  2. Jedes <dc:creator>: der Login wird zum selben author-<id>.
  3. Jede uebrige Mailadresse im Text (Kontaktformular, Fliesstext) wird zu
     (E-Mail entfernt), ebenso die verfremdete Schreibung "name at domain.tld".
  4. Die Telefonnummer im Impressum wird zu (Telefonnummer entfernt).

Namen in Literaturangaben und Fliesstext (Zitate wie "Zeppezauer-Wachauer,
Katharina: ...") sind Inhalt, keine Kontodaten, und bleiben stehen. Ebenso zwei
Bildnachweis-Zeilen ("credit", s:29:"Zeppezauer-Wachauer Katharina") in den
serialisierten Anhangs-Metadaten (PHP-Laengenangabe, deshalb nicht ersetzbar,
ohne die Serialisierung zu brechen).

Danach: Kontrollwert (dieselbe Mail-Regex auf dem Original), Trefferzahl auf der
Ausgabe, IP-Adressen, Telefonnummern, Wohlgeformtheit (lxml), Zahl der <item>
vorher/nachher. Exit 1, wenn die Ausgabe noch eine Mailadresse, IP-Adresse,
Telefonnummer oder einen der personenbezogenen Logins traegt, nicht wohlgeformt
ist, oder ein Kontrollwert (5 verschiedene Adressen, 1 Telefonnummer) im
Original verfehlt wird.

Usage:
    python -E -P scripts/ingest/glossar-554/bereinige-export.py ORIGINAL.xml AUSGABE.xml
"""
import argparse
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glossar_export import MAIL_RE, OBFUSC_RE, PHONE_RE, IPV4_RE, IPV6_RE  # noqa: E402

MAIL_PLATZHALTER = '(E-Mail entfernt)'
TEL_PLATZHALTER = '(Telefonnummer entfernt)'
ERWARTETE_TELEFONNUMMERN = 1   # Impressum, post 2306
ERWARTETE_ADRESSEN = 5   # laut Issue #554

AUTHOR_RE = re.compile(r'<wp:author>.*?</wp:author>', re.S)
FIELD_RE = r'<wp:%s>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</wp:%s>'
CREATOR_RE = re.compile(r'<dc:creator><!\[CDATA\[(.*?)\]\]></dc:creator>')


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def feld(block, name):
    m = re.search(FIELD_RE % (name, name), block, re.S)
    if not m:
        raise ValueError('Feld wp:%s fehlt im Autorenblock: %r' % (name, block[:120]))
    return m.group(1)


def bereinige(text):
    """Gibt (neuer Text, Zaehler) zurueck."""
    z = Counter()
    login_zu_id = {}

    def ersetze_autor(m):
        block = m.group(0)
        aid = feld(block, 'author_id')
        login = feld(block, 'author_login')
        if login in login_zu_id:
            raise ValueError('Login %r doppelt' % login)
        login_zu_id[login] = 'author-%s' % aid
        z['wp:author-Bloecke'] += 1
        name = login_zu_id[login]
        neu = block
        for fname, wert in (('author_login', name), ('author_email', MAIL_PLATZHALTER),
                            ('author_display_name', name), ('author_first_name', ''),
                            ('author_last_name', '')):
            neu, n = re.subn(FIELD_RE % (fname, fname),
                             lambda _m, f=fname, w=wert: '<wp:%s><![CDATA[%s]]></wp:%s>' % (f, w, f),
                             neu, count=1, flags=re.S)
            if n != 1:
                raise ValueError('Feld wp:%s im Autorenblock %s nicht ersetzt' % (fname, aid))
        return neu

    text = AUTHOR_RE.sub(ersetze_autor, text)
    if not login_zu_id:
        raise ValueError('keine wp:author-Bloecke gefunden')

    def ersetze_creator(m):
        login = m.group(1)
        if login not in login_zu_id:
            # unbekannte Eingabe ist ein harter Fehler, kein stilles Ueberspringen
            raise ValueError('dc:creator %r ohne wp:author-Block' % login)
        z['dc:creator'] += 1
        return '<dc:creator><![CDATA[%s]]></dc:creator>' % login_zu_id[login]

    text = CREATOR_RE.sub(ersetze_creator, text)

    def ersetze_mail(m):
        z['uebrige Mailadressen (Vorkommen)'] += 1
        return MAIL_PLATZHALTER

    text = MAIL_RE.sub(ersetze_mail, text)

    # Verfremdete Schreibung "name at domain.tld" (Impressum, post 2306): die echte
    # Mail-Regex trifft sie nicht, sie ist aber dieselbe Adresse.
    def ersetze_verfremdet(m):
        z['verfremdete Mailadressen ("x at y.z")'] += 1
        return MAIL_PLATZHALTER

    text = OBFUSC_RE.sub(ersetze_verfremdet, text)

    def ersetze_telefon(m):
        z['Telefonnummern'] += 1
        return TEL_PLATZHALTER

    text = PHONE_RE.sub(ersetze_telefon, text)
    return text, z, login_zu_id


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('original')
    ap.add_argument('ausgabe')
    args = ap.parse_args()

    raw = Path(args.original).read_bytes()
    text = raw.decode('utf-8')
    print('Original: %d Bytes, sha256 %s' % (len(raw), sha256(raw)))

    mails_vorher = Counter(MAIL_RE.findall(text))
    print('Kontrollwert: %d verschiedene Mailadressen im Original (%d Vorkommen), erwartet %d'
          % (len(mails_vorher), sum(mails_vorher.values()), ERWARTETE_ADRESSEN))
    ips_vorher = IPV4_RE.findall(text) + IPV6_RE.findall(text)
    print('IP-Adressen im Original: %d' % len(ips_vorher))
    items_vorher = len(etree.fromstring(raw).findall('.//item'))

    neu, z, login_map = bereinige(text)
    for k, v in sorted(z.items()):
        print('ersetzt: %s: %d' % (k, v))
    print('Logins -> Platzhalter: %s' % ', '.join('%s -> %s' % kv for kv in sorted(login_map.items())))

    # newline='' bzw. bytes: Zeilenenden unveraendert lassen
    out = neu.encode('utf-8')
    Path(args.ausgabe).write_bytes(out)

    fehler = []
    mails_nachher = MAIL_RE.findall(neu)
    ips_nachher = IPV4_RE.findall(neu) + IPV6_RE.findall(neu)
    print('Bereinigt: %d Bytes, sha256 %s' % (len(out), sha256(out)))
    print('Mailadressen in der bereinigten Datei: %d Treffer' % len(mails_nachher))
    verfremdet_vorher = OBFUSC_RE.findall(text)
    verfremdet_nachher = OBFUSC_RE.findall(neu)
    print('Verfremdete Adressen ("x at y.z"): Original %d, bereinigt %d Treffer'
          % (len(verfremdet_vorher), len(verfremdet_nachher)))
    if verfremdet_nachher:
        fehler.append('verfremdete Adresse(n) uebrig: %s' % sorted(set(verfremdet_nachher)))
    print('IP-Adressen in der bereinigten Datei: %d Treffer' % len(ips_nachher))
    tel_vorher = PHONE_RE.findall(text)
    tel_nachher = PHONE_RE.findall(neu)
    print('Telefonnummern: Original %d (erwartet %d), bereinigt %d Treffer'
          % (len(tel_vorher), ERWARTETE_TELEFONNUMMERN, len(tel_nachher)))
    if len(tel_vorher) != ERWARTETE_TELEFONNUMMERN:
        fehler.append('Kontrollwert Telefon verfehlt: %d statt %d im Original'
                      % (len(tel_vorher), ERWARTETE_TELEFONNUMMERN))
    if tel_nachher:
        fehler.append('Telefonnummer(n) uebrig: %s' % tel_nachher)
    for login in login_map:
        n = len(re.findall(r'(?<![\w-])%s(?![\w-])' % re.escape(login), neu))
        print('Rest-Vorkommen des Logins %r in der bereinigten Datei: %d (Wortgrenze)' % (login, n))
        # "admin" steht auch im WordPress-Kopfkommentar ("admin panel") und in
        # wp-admin-URLs; die beiden personenbezogenen Logins duerfen nicht bleiben.
        if login != 'admin' and n:
            fehler.append('Login %r noch %d-mal vorhanden' % (login, n))
    items_nachher = len(etree.fromstring(out).findall('.//item'))
    print('Wohlgeformt (lxml): ja; <item> vorher/nachher: %d/%d' % (items_vorher, items_nachher))

    if len(mails_vorher) != ERWARTETE_ADRESSEN:
        fehler.append('Kontrollwert verfehlt: %d statt %d verschiedene Adressen im Original'
                      % (len(mails_vorher), ERWARTETE_ADRESSEN))
    if mails_nachher:
        fehler.append('Mailadresse(n) uebrig: %s' % sorted(set(mails_nachher)))
    if ips_nachher:
        fehler.append('IP-Adresse(n) uebrig: %s' % sorted(set(ips_nachher)))
    if items_vorher != items_nachher:
        fehler.append('Zahl der <item> hat sich geaendert')
    for f in fehler:
        print('FEHLER: ' + f)
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.exit(main())
