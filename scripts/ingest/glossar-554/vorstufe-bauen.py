"""Erzeugt die mechanische Vorstufe der 189 mittelhochdeutschen Glossar-Eintraege (#554).

Liest den bereinigten WordPress-Export (sources/glossar-kochbuchforschung/) und schreibt je
Eintrag Titel, Wortklasse, nhd. Bedeutungen, die Rohfelder "Enzyklopaedische Information"
(enz) und "Poetisierung des Wortes" (poet) sowie deren Fliesstext (enz_t, poet_t):
Kursivierung wird zu Anfuehrungszeichen, Fussnotenanker und alles ab "QUELLEN"/"LITERATUR"
entfallen. Keine Straffung, keine Auswahl.

Die uebrigen Skripte (kommentare-pruefen.py, entfallenes-suchen.py, pruefseite-bauen.py)
lesen diese Datei; sie gehoert nicht ins Repositorium, weil sie sich aus dem Export
jederzeit erzeugen laesst.

Aufruf (aus der Repositoriumswurzel):
    python -X utf8 -E -P scripts/ingest/glossar-554/vorstufe-bauen.py <ausgabe.json>
"""
import html
import json
import re
import sys

sys.path.insert(0, 'scripts/ingest/glossar-554')
from glossar_export import WP, lemma_items, parse_export  # noqa: E402

EXPORT = 'sources/glossar-kochbuchforschung/digest_ivum.wordpress.2026-10-08.bereinigt.xml'


def fliesstext(s):
    if not s:
        return ''
    s = s.replace('\r', '')
    s = re.sub(r'<a [^>]*name="_ftnref\d*"[^>]*>\s*(?:\[\d+\])?\s*</a>', '', s)
    s = re.sub(r'<sup[^>]*>.*?</sup>', '', s, flags=re.S)
    s = re.sub(r'</tr>', '\n', s)
    s = re.sub(r'</td>', ' ', s)
    s = re.sub(r'<(em|i|cite)(\s[^>]*)?>', '„', s)
    s = re.sub(r'</(em|i|cite)>', '“', s)
    s = re.sub(r'</(p|div|li|h\d|blockquote|ul|ol|section)>', '\n', s)
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = s.replace(' ', ' ')
    # Nachbarliche Anfuehrungspaare zusammenziehen: "a" "b" -> "a b"
    s = re.sub(r'“\s*„', ' ', s)
    s = re.sub(r'„\s+', '„', s)
    s = re.sub(r'\s+“', '“', s)
    s = re.sub(r'„“', '', s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n[ \t]+', '\n', s)
    s = re.sub(r'\n{3,}', '\n\n', s).strip()
    m = re.search(r'\n?\s*(QUELLEN|LITERATUR|Quellen|Literatur)\s*:?\s*\n', s)
    if m:
        s = s[:m.start()].rstrip()
    return s


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    t = parse_export(EXPORT)
    alle = lemma_items(t, 'publish')
    byid = {it.findtext(WP + 'post_id'): (it, m) for it, m in alle}
    out = []
    for it, m in alle:
        if m.get('sprachstufe') != 'gmh':
            continue
        nhd = []
        for k, v in m.items():
            mm = re.match(r'interne_links_(\d+)_nhd_bedeutung$', k)
            if mm and v:
                ref = byid.get(v)
                nhd.append(ref[0].findtext('title') if ref else 'ID' + v)
        o = {
            'id': it.findtext(WP + 'post_id'),
            'title': it.findtext('title'),
            'wk': m.get('wortklasse'),
            'enz': m.get('Enzyklopädische Information', ''),
            'poet': m.get('Poetisierung des Wortes', ''),
            'nhd': nhd,
            'extra': {k: m[k] for k in ('Belegstellen', 'Grammatische Information',
                                        'Poetische Erweiterung', 'Variante') if m.get(k)},
        }
        o['enz_t'] = fliesstext(o['enz'])
        o['poet_t'] = fliesstext(o['poet'])
        out.append(o)
    json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('%d Eintraege, enz_t %d Zeichen, poet_t %d Zeichen' % (
        len(out), sum(len(o['enz_t']) for o in out), sum(len(o['poet_t']) for o in out)))


main()
