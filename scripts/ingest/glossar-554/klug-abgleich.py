"""Gleicht die mittelhochdeutschen Eintraege des Portals der Pflanzen des Mittelalters
(Helmut W. Klug, http://medieval-plants.org) mit unseren Lemmata ab (#554, B5).

Eingaben (nichts wird hier nachgeladen; die Abrufe macht ein Mensch oder eine Sitzung
einzeln und mit Pause, die Rohdaten bleiben im Scratchpad, nicht im Repositorium):
  1. die Listenseite http://medieval-plants.org/mps-daten/languages/gmh/ (ein Abruf),
  2. ein Ordner mit abgerufenen Einzelseiten: klug_<slug>.html (mhd. Eintrag) und
     pflanze_<slug>.html (uebergeordnete Pflanzenseite).

Abgleich der Titel der Liste ueber die Normalisierung (scripts/mhg_normalizer.py) gegen
die normalisierte Lemmaform und die Variantenformen des Authority-Index. Ein Treffer ist ein
Kandidat, keine Zuordnung: gleiche Schreibung kann ein anderes Wort sein.

Die Pflanzenseite ist nur fuer Treffer abgerufen, deren Lemma zu den Glossar-Lemmata
(zuordnung.tsv) gehoert; fuer alle anderen bleibt die Spalte leer ("nicht abgerufen (Umfang)").
Uebernommen werden nur Titel, URLs und Zuordnungen, kein Seitentext.

Ausgabe in ingest/glossar-554/:
  klug-abgleich.tsv   slug, titel, mhd_url, treffer, lemma_id, lemma, pflanzenseite_url,
                      pflanzenseite_titel, vermerk
  klug-pflanzen.tsv   je abgerufener Pflanzenseite ihre mhd. Namen mit unserem Lemma und der
                      Angabe, ob es dasselbe Lemma ist wie beim Glossar-Treffer

Aufruf (aus der Repositoriumswurzel):
    python -X utf8 -E -P scripts/ingest/glossar-554/klug-abgleich.py <gmh_liste.html> <rohdaten-ordner>
"""
import csv
import gzip
import html
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, 'scripts')
from mhg_normalizer import normalize_mhg  # noqa: E402

BASIS = 'http://medieval-plants.org/mps-daten/mps_entry/'
ABRUFDATUM = '2026-10-14'
LINK = re.compile(r'<a href="' + re.escape(BASIS) + r'([^"/]+)/">([^<]+)</a>')


def lies(pfad):
    return open(pfad, encoding='utf-8').read() if os.path.exists(pfad) else None


def abschnitt(t, von, bis):
    i = t.find(von)
    if i < 0:
        return ''
    j = t.find(bis, i + len(von))
    return t[i:j if j > 0 else len(t)]


def eltern(seite):
    """Uebergeordnete Eintraege (slug, titel) einer abgerufenen Seite."""
    a = abschnitt(seite, '<h3>Übergeordnete', 'Zitierempfehlung')
    return [(s, html.unescape(x).strip()) for s, x in LINK.findall(a)]


def mhd_kinder(seite):
    """Mittelhochdeutsche Unterordnungen (slug, titel) einer Pflanzenseite."""
    a = abschnitt(seite, '<h3>Untergeordnete', '<h3>Übergeordnete')
    out = []
    for block in re.split(r'<li style="list-style-type:none"><strong>', a)[1:]:
        sprache, _, rest = block.partition('</strong>')
        if sprache.strip() == 'Mittelhochdeutsch':
            out += [(s, html.unescape(x).strip()) for s, x in LINK.findall(rest)]
    return out


def abstand_eins(a, b):
    if abs(len(a) - len(b)) > 1 or a == b:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    k, l = (a, b) if len(a) < len(b) else (b, a)
    return any(l[:i] + l[i + 1:] == k for i in range(len(l)))


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    t = open(sys.argv[1], encoding='utf-8').read()
    roh = sys.argv[2]
    eintraege = []
    for m in re.finditer(r'<li><a href="' + re.escape(BASIS) + r'([^"/]+)/">([^<\t]+?)\s*\t*\(gmh\)', t):
        eintraege.append((m.group(1), html.unescape(m.group(2)).strip()))
    if len(eintraege) < 1000:
        sys.exit('FEHLER: nur %d Eintraege gefunden, Listenformat geaendert?' % len(eintraege))
    d = json.load(gzip.open('data/authority-index.json.gz', 'rt', encoding='utf-8'))
    nach_lemma = {}
    for r in d['lemmata']:
        nach_lemma.setdefault(r['normalized'], []).append(r['id'])
    varianten = d['variants']
    namen = {r['id']: r['lemma'] for r in d['lemmata']}
    nach_anfang = {}
    for n, ids in nach_lemma.items():
        nach_anfang.setdefault(n[:1], []).append((n, ids))
    zuordnung = list(csv.DictReader(open('ingest/glossar-554/zuordnung.tsv', encoding='utf-8'), delimiter='\t'))
    glossar_lemmata = {r['lemma_id']: r['glossar_titel'] for r in zuordnung if r['lemma_id']}

    treffer = {}
    for slug, titel in eintraege:
        n = normalize_mhg(titel)
        if n in nach_lemma:
            treffer[slug] = ('lemma', nach_lemma[n])
        elif n in varianten:
            v = varianten[n]
            treffer[slug] = ('variante', [v] if isinstance(v, str) else list(v))
        else:
            treffer[slug] = ('keiner', [])

    zeilen, zaehler, seiten = [], Counter(), 0
    plant_zeilen = []
    eltern_slugs = {}
    for slug, titel in eintraege:
        art, ids = treffer[slug]
        zaehler[art] += 1
        pf_url = pf_titel = ''
        if art == 'keiner':
            n = normalize_mhg(titel)
            nah = sorted({namen[i] for f, ids2 in nach_anfang.get(n[:1], []) if abstand_eins(n, f) for i in ids2})
            vermerk = ('nächste Schreibung: ' + ', '.join(nah[:5])) if nah else 'kein Lemma, keine Variante, keine nahe Schreibung'
        else:
            im_glossar = [i for i in ids if i in glossar_lemmata]
            vermerk = ''
            seite = lies(os.path.join(roh, 'klug_%s.html' % slug))
            if im_glossar and seite is not None:
                seiten += 1
                es = eltern(seite)
                if es:
                    pf_url = ' '.join(BASIS + s + '/' for s, _ in es)
                    pf_titel = ' | '.join(x for _, x in es)
                    for s, x in es:
                        eltern_slugs.setdefault(s, []).append((slug, titel, ids))
                else:
                    vermerk = 'keine übergeordnete Pflanzenseite auf der Seite'
            elif im_glossar:
                vermerk = 'Seite fehlt in den Rohdaten'
            else:
                vermerk = 'nicht abgerufen (Umfang)'
        zeilen.append([slug, titel, BASIS + slug + '/', art, ' '.join(ids), ' '.join(namen.get(i, '?') for i in ids),
                       pf_url, pf_titel, vermerk])

    # Pflanzenseiten und ihre mhd. Namen
    pflanzen = 0
    for ps, quellen in sorted(eltern_slugs.items()):
        seite = lies(os.path.join(roh, 'pflanze_%s.html' % ps))
        if seite is None:
            plant_zeilen.append([ps, '', '', '', '', '', 'Pflanzenseite fehlt in den Rohdaten'])
            continue
        pflanzen += 1
        treffer_ids = {i for _, _, ids in quellen for i in ids if i in glossar_lemmata}
        for ks, kt in mhd_kinder(seite):
            art, ids = treffer.get(ks, ('?', []))
            gleich = 'gleich' if set(ids) & treffer_ids else ('anders' if ids else 'kein Lemma')
            plant_zeilen.append([ps, BASIS + ps + '/', kt, BASIS + ks + '/', ' '.join(namen.get(i, '?') + ' ' + i for i in ids),
                                 ' '.join(glossar_lemmata[i] for i in treffer_ids), gleich])

    with open('ingest/glossar-554/klug-abgleich.tsv', 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['slug', 'titel', 'mhd_url', 'treffer', 'lemma_id', 'lemma', 'pflanzenseite_url', 'pflanzenseite_titel', 'vermerk'])
        w.writerows(zeilen)
    with open('ingest/glossar-554/klug-pflanzen.tsv', 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['pflanzenseite', 'pflanzenseite_url', 'mhd_name', 'mhd_url', 'unser_lemma', 'glossar_lemma_beim_treffer', 'vergleich'])
        for z in plant_zeilen:
            w.writerow(z if len(z) == 7 else z[:6] + [z[6]])
    print('Eintraege in der Liste: %d (Stand der Rohdaten %s)' % (len(eintraege), ABRUFDATUM))
    print('Treffer: %s (Summe %d)' % (dict(zaehler), sum(zaehler.values())))
    print('Glossar-Lemmata mit Klug-Treffer, mhd. Seite gelesen: %d; Pflanzenseiten gelesen: %d von %d'
          % (seiten, pflanzen, len(eltern_slugs)))
    print('Pflanzenseiten, noch zu holen: ' + ' '.join(s for s in eltern_slugs
                                                      if lies(os.path.join(roh, 'pflanze_%s.html' % s)) is None))


main()
