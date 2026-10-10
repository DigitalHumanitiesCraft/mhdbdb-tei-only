#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#554 Schritt 1: die Zahlen aus dem Issue-Body am Export nachmessen (read-only).

Liest die bereinigte Fassung (oder das Original; fuer diese Zahlen macht es
keinen Unterschied) und druckt jede Zahl neben dem Erwartungswert aus dem Issue,
jeweils mit ihrer Menge. Eine Abweichung wird markiert (ABWEICHUNG), nie
angepasst. Exit 1, wenn mindestens eine Zahl abweicht.

Zaehlvorschriften (so gezaehlt, weil das Issue keine nennt):
  * Eintraege: alle <item> der Datei, nach wp:post_type und wp:status.
  * Sprachstufe: Meta "sprachstufe" der veroeffentlichten Eintraege vom Typ lemma.
    "leer" ist fehlender Schluessel oder leerer Wert, getrennt ausgewiesen.
  * Verweise: nichtleere Werte der Meta-Schluessel interne_links_<n>_nhd_bedeutung
    (nur gmh-Eintraege) und interne_links_<n>_mhd_wort (nur deu-Eintraege).
    Die aelteren Schluessel interne_links_<n>_bedeutung zaehlen nicht.
  * Kategorien/Schlagwoerter: verschiedene nicename je domain (category,
    post_tag) an veroeffentlichten Eintraegen vom Typ lemma; Zuordnungen =
    Zahl der <category>-Elemente dieser Eintraege.
  * "hat Enzyklopaedische Information / Poetisierung": Meta nichtleer nach
    Entfernen von Leerraum. Menge: die 159 eindeutig zugeordneten gmh-Eintraege
    bzw. alle 189 gmh-Eintraege.

Usage:
    python -E -P scripts/ingest/glossar-554/messe-export.py EXPORT.xml
"""
import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glossar_export import (WP, parse_export, lemma_items, lade_lemmata,  # noqa: E402
                            norm_titel)

ABW = []


def zeile(was, menge, gemessen, erwartet=None):
    """Eine Zahl mit ihrer Menge in derselben Zeile; Erwartungswert daneben."""
    if erwartet is None:
        print('  %-58s %6s   (%s)' % (was, gemessen, menge))
        return
    marke = 'ok' if gemessen == erwartet else 'ABWEICHUNG'
    if gemessen != erwartet:
        ABW.append((was, gemessen, erwartet))
    print('  %-58s %6s   erwartet %-6s %s  (%s)' % (was, gemessen, erwartet, marke, menge))


def finde_schluessel(metas, anfang):
    """Der Meta-Schluessel mit diesem Anfang, genau einer (Umlaute im Namen)."""
    cand = {k for m in metas for k in m if k.startswith(anfang)}
    if len(cand) != 1:
        raise SystemExit('Schluessel %r nicht eindeutig: %s' % (anfang, sorted(cand)))
    return cand.pop()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('export')
    args = ap.parse_args()

    tree = parse_export(args.export)
    items = list(tree.getroot().iter('item'))

    print('Eintraege nach Typ (Menge: alle %d <item>)' % len(items))
    typ = Counter((i.findtext(WP + 'post_type'), i.findtext(WP + 'status')) for i in items)
    zeile('Eintraege insgesamt', 'alle <item>', len(items), 536)
    zeile('veroeffentlichte lemma', 'post_type lemma, status publish', typ[('lemma', 'publish')], 482)
    zeile('Entwuerfe (lemma)', 'post_type lemma, status draft', typ[('lemma', 'draft')], 2)
    zeile('ACF-Felddefinitionen', 'post_type acf-field', typ[('acf-field', 'publish')], 23)
    zeile('ACF-Feldgruppen', 'post_type acf-field-group', typ[('acf-field-group', 'publish')], 7)
    zeile('Seiten', 'post_type page', typ[('page', 'publish')], 10)
    zeile('Menueeintraege', 'post_type nav_menu_item', typ[('nav_menu_item', 'publish')], 8)
    zeile('Anhaenge', 'post_type attachment', typ[('attachment', 'inherit')], 3)
    zeile('Kontaktformulare', 'post_type wpcf7_contact_form', typ[('wpcf7_contact_form', 'publish')], 1)
    zeile('Kommentare', 'wp:comment-Elemente in der Datei', len(list(tree.getroot().iter(WP + 'comment'))), 0)
    print('  alle (Typ, Status): %s' % dict(typ))

    pub = lemma_items(tree, 'publish')
    metas = [m for _, m in pub]
    k_enz = finde_schluessel(metas, 'Enzyklop')
    k_poe = finde_schluessel(metas, 'Poetisierung des Wortes')

    print('\nSprachstufe (Menge: %d veroeffentlichte lemma)' % len(pub))
    stufe = Counter()
    for _, m in pub:
        s = m.get('sprachstufe')
        stufe['(Schluessel fehlt)' if s is None else (s or '(leerer Wert)')] += 1
    zeile('gmh', 'von %d veroeffentlichten lemma' % len(pub), stufe['gmh'], 189)
    zeile('deu', 'von %d' % len(pub), stufe['deu'], 287)
    zeile('deu-enh', 'von %d' % len(pub), stufe['deu-enh'], 3)
    zeile('rmd', 'von %d' % len(pub), stufe['rmd'], 1)
    zeile('nld', 'von %d' % len(pub), stufe['nld'], 1)
    zeile('leer (fehlend oder leerer Wert)', 'von %d' % len(pub),
          stufe['(Schluessel fehlt)'] + stufe['(leerer Wert)'], 1)
    print('  Aufschluesselung leer: Schluessel fehlt %d, leerer Wert %d'
          % (stufe['(Schluessel fehlt)'], stufe['(leerer Wert)']))
    zeile('Summe der Stufen', 'muss die %d Eintraege decken' % len(pub), sum(stufe.values()), len(pub))

    print('\nVerweise gmh <-> deu (Menge: nichtleere Werte der Wiederholungsfelder)')
    id_zu_stufe = {it.findtext(WP + 'post_id'): m.get('sprachstufe') for it, m in pub}
    re_nhd = re.compile(r'^interne_links_\d+_nhd_bedeutung$')
    re_mhd = re.compile(r'^interne_links_\d+_mhd_wort$')
    gmh_deu = deu_gmh = 0
    gmh_deu_ziel_ok = deu_gmh_ziel_ok = 0
    gmh_deu_paare = set()
    deu_gmh_paare = set()
    for it, m in pub:
        pid = it.findtext(WP + 'post_id')
        s = m.get('sprachstufe')
        for k, v in m.items():
            if s == 'gmh' and re_nhd.match(k) and v.strip():
                gmh_deu += 1
                gmh_deu_paare.add((pid, v.strip()))
                gmh_deu_ziel_ok += id_zu_stufe.get(v.strip()) == 'deu'
            if s == 'deu' and re_mhd.match(k) and v.strip():
                deu_gmh += 1
                deu_gmh_paare.add((pid, v.strip()))
                deu_gmh_ziel_ok += id_zu_stufe.get(v.strip()) == 'gmh'
    # Das Issue zaehlt die Verweise, deren Ziel ein veroeffentlichter Eintrag der
    # Gegenstufe ist (420 und 394); die nichtleeren Rohwerte sind mehr (422, 406).
    zeile('Verweise gmh -> deu, Ziel veroeffentlichtes deu', 'von %d nichtleeren nhd_bedeutung-Werten in den 189 gmh'
          % gmh_deu, gmh_deu_ziel_ok, 420)
    zeile('Verweise deu -> gmh, Ziel veroeffentlichtes gmh', 'von %d nichtleeren mhd_wort-Werten in den 287 deu'
          % deu_gmh, deu_gmh_ziel_ok, 394)
    print('  Rohwerte ohne Zielpruefung: gmh->deu %d, deu->gmh %d; verschiedene Paare: %d und %d'
          % (gmh_deu, deu_gmh, len(gmh_deu_paare), len(deu_gmh_paare)))
    fehlziel = [(p, t, id_zu_stufe.get(t)) for p, t in sorted(gmh_deu_paare)
                if id_zu_stufe.get(t) != 'deu']
    fehlziel += [(p, t, id_zu_stufe.get(t)) for p, t in sorted(deu_gmh_paare)
                 if id_zu_stufe.get(t) != 'gmh']
    print('  Verweise mit falschem Ziel (Quelle post_id, Ziel post_id, Stufe des Ziels; None = '
          'kein veroeffentlichter Eintrag): %s' % fehlziel)

    print('\nTaxonomien (Menge: %d veroeffentlichte lemma)' % len(pub))
    kat = Counter()
    tag = Counter()
    for it, _ in pub:
        for c in it.findall('category'):
            (kat if c.get('domain') == 'category' else tag if c.get('domain') == 'post_tag'
             else Counter())[c.get('nicename')] += 1
    zeile('Kategorien (verschiedene nicename)', 'an den 482 Eintraegen', len(kat), 58)
    zeile('Schlagwoerter (verschiedene nicename)', 'an den 482 Eintraegen', len(tag), 163)
    zeile('Kategorie-Zuordnungen', 'Summe ueber die 482', sum(kat.values()), 877)
    zeile('Schlagwort-Zuordnungen', 'Summe ueber die 482', sum(tag.values()), 1608)
    chan = tree.getroot().find('channel')
    print('  im Kopf deklariert: wp:category %d, wp:tag %d (Menge: alle Deklarationen, auch ohne Zuordnung)'
          % (len(chan.findall(WP + 'category')), len(chan.findall(WP + 'tag'))))
    kopf_kat = {c.findtext(WP + 'category_nicename') for c in chan.findall(WP + 'category')}
    print('  Kategorien im Kopf ohne Zuordnung an den 482: %d (%s)'
          % (len(kopf_kat - set(kat)), ', '.join(sorted(kopf_kat - set(kat)))))
    print('  Kategorien mit Zuordnung, aber nicht im Kopf deklariert: %d' % len(set(kat) - kopf_kat))
    entw = [(it, m) for it, m in lemma_items(tree, 'draft')]
    kat_entw = {c.get('nicename') for it, _ in entw for c in it.findall('category')
                if c.get('domain') == 'category'}
    print('  Kategorien, die nur an den %d Entwuerfen haengen: %d'
          % (len(entw), len(kat_entw - set(kat))))

    print('\nAbgleich der gmh-Titel gegen api/lemmata/index.json (Menge: %d gmh)' % stufe['gmh'])
    lem = lade_lemmata()
    nach_norm = defaultdict(list)
    for l in lem:
        nach_norm[norm_titel(l['lemma'])].append(l)
    print('  Lemmata in der API: %d' % len(lem))
    eind, homo, kein = [], [], []
    for it, m in pub:
        if m.get('sprachstufe') != 'gmh':
            continue
        t = it.findtext('title')
        n = len(nach_norm.get(norm_titel(t), []))
        (eind if n == 1 else homo if n > 1 else kein).append((it, m))
    zeile('genau ein Lemma', 'von %d gmh-Eintraegen' % stufe['gmh'], len(eind), 159)
    zeile('mehrere Lemmata (Homographen)', 'von %d gmh-Eintraegen' % stufe['gmh'], len(homo), 5)
    zeile('kein Lemma', 'von %d gmh-Eintraegen' % stufe['gmh'], len(kein), 25)
    print('  Homographen: %s' % ', '.join(it.findtext('title') for it, _ in homo))
    print('  kein Lemma: %s' % ', '.join(it.findtext('title') for it, _ in kein))
    erw_homo = {'âme', 'brâten', 'sat', 'ber', 'diech'}
    ist_homo = {it.findtext('title') for it, _ in homo}
    print('  Homographen wie im Issue (%s): %s' % (', '.join(sorted(erw_homo)),
          'ja' if ist_homo == erw_homo else 'NEIN, Differenz: nur hier %s, nur im Issue %s'
          % (sorted(ist_homo - erw_homo), sorted(erw_homo - ist_homo))))

    def hat(m, k):
        return bool(re.sub(r'\s+', '', m.get(k, '')))

    print('\nFelder fuer das Kommentarfeld (#268)')
    zeile('eindeutig zugeordnet mit Enzyklopaedischer Information', 'von %d eindeutigen' % len(eind),
          sum(hat(m, k_enz) for _, m in eind), 100)
    zeile('eindeutig zugeordnet mit Poetisierung des Wortes', 'von %d eindeutigen' % len(eind),
          sum(hat(m, k_poe) for _, m in eind), 101)
    gm = [(it, m) for it, m in pub if m.get('sprachstufe') == 'gmh']
    zeile('alle gmh mit Enzyklopaedischer Information', 'von %d gmh' % len(gm),
          sum(hat(m, k_enz) for _, m in gm), 121)
    zeile('alle gmh mit Poetisierung des Wortes', 'von %d gmh' % len(gm),
          sum(hat(m, k_poe) for _, m in gm), 119)
    ohne_text = sum(1 for it, _ in pub
                    if not (it.findtext('{http://purl.org/rss/1.0/modules/content/}encoded') or '').strip())
    print('  Eintraege mit leerem Fliesstext (content:encoded): %d von %d' % (ohne_text, len(pub)))

    print('\nPlausibilitaet: nichtleere post_password in der Datei: %d'
          % sum(1 for i in items if (i.findtext(WP + 'post_password') or '').strip()))

    print('\n%s' % ('ALLE ZAHLEN WIE IM ISSUE' if not ABW else
                    'ABWEICHUNGEN: %d' % len(ABW)))
    for w, g, e in ABW:
        print('  %s: gemessen %s, Issue %s' % (w, g, e))
    return 1 if ABW else 0


if __name__ == '__main__':
    sys.exit(main())
