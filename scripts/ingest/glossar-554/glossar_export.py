# -*- coding: utf-8 -*-
"""Gemeinsame Hilfen fuer die #554-Skripte: WordPress-Export des Glossars
Kochbuchforschung lesen. Keine Aenderung an Daten.

Der Export ist eine WordPress-WXR-Datei (Format 1.2). Ein Glossar-Eintrag ist
ein <item> mit wp:post_type "lemma"; seine Felder stehen als wp:postmeta
(ACF), nicht im Fliesstext.
"""
import io
import json
import re
import sys
from pathlib import Path

from lxml import etree

WP = '{http://wordpress.org/export/1.2/}'

# Windows-Konsole: Ausgabe von MHG-Zeichen nicht an cp1252 sterben lassen.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

# Mailadressen, bewusst weit gefasst (lokaler Teil, @, Domain mit Punkt).
MAIL_RE = re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}')
# Telefonnummern: "Tel:"/"Telefon:"-Zeile mit Ziffernfolge, oder internationale Form +NN ...
# Das Wort "Telefonnummer" in einer Fehlermeldung ("Die Telefonnummer ist ungueltig.")
# trifft nicht: nach "Tel"/"Telefon" muss ein Doppelpunkt und eine Ziffer folgen.
PHONE_RE = re.compile(r'Tel(?:efon)?\.?:\s*[+(]?\d[\d ()/\-]{5,}|\+\d{2}[\d ]{6,}')
# Verfremdete Schreibung "name at domain.tld" (so steht eine Adresse im Impressum, post 2306).
OBFUSC_RE = re.compile(r'[A-Za-z0-9._\-]+ (?:at|AT|\(at\)|\[at\]) [A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}')
# IPv4 mit Oktetten 0..255, nicht Teil einer laengeren Zifferngruppe.
IPV4_RE = re.compile(r'(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\d.])')
# IPv6 grob: mindestens vier Hex-Gruppen mit Doppelpunkt.
IPV6_RE = re.compile(r'(?<![\w:])(?:[0-9A-Fa-f]{1,4}:){4,7}[0-9A-Fa-f]{1,4}(?![\w:])')


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from mhg_normalizer import normalize_mhg  # noqa: E402


def norm_titel(s):
    """Abgleichsform: MHG-Normalisierung des Projekts (scripts/mhg_normalizer.py,
    deckt schon ae/oe-Ligaturen ab) plus die zwei Zeichen, die sie nicht kennt:
    e-Trema und langes z (U+0292). Dazu Leerraum an den Raendern weg."""
    return normalize_mhg((s or '').strip()).replace('ë', 'e').replace('ʒ', 'z')


def lade_lemmata():
    """api/lemmata/index.json als Liste von Dicts (id, lemma, pos, ...)."""
    d = json.loads((ROOT / 'api' / 'lemmata' / 'index.json').read_text(encoding='utf-8'))
    return d['items']


def abgleich(titel, nach_norm):
    """Exakter Abgleich eines Glossartitels: Liste der Lemma-Dicts mit gleicher
    Abgleichsform. Keine Varianten, kein Praefix, keine Wortart."""
    return nach_norm.get(norm_titel(titel), [])


def parse_export(path):
    """Parst die Datei strikt (wohlgeformt oder harter Fehler) und liefert den Baum."""
    return etree.parse(str(path))


def item_meta(item):
    """Postmeta eines <item> als Dict. Inhaltsfelder kommen je Eintrag einmal vor;
    kommt eines doppelt vor, ist das ein harter Fehler (unbekannte Eingabe).
    Mit Unterstrich beginnende WordPress-interne Schluessel duerfen doppelt stehen."""
    meta = {}
    for pm in item.findall(WP + 'postmeta'):
        key = pm.findtext(WP + 'meta_key')
        if key in meta and key.startswith('_'):
            continue   # WordPress-intern (etwa _wp_old_slug), darf mehrfach stehen
        if key in meta:
            raise ValueError('doppelter Meta-Schluessel %r in post_id %s'
                             % (key, item.findtext(WP + 'post_id')))
        meta[key] = pm.findtext(WP + 'meta_value') or ''
    return meta


def lemma_items(tree, status=None):
    """Alle Eintraege vom Typ lemma als Liste (item, meta); optional nach Status."""
    out = []
    for it in tree.getroot().iter('item'):
        if it.findtext(WP + 'post_type') != 'lemma':
            continue
        if status and it.findtext(WP + 'status') != status:
            continue
        out.append((it, item_meta(it)))
    return out
