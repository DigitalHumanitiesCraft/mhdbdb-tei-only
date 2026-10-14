"""Baut die Pruefseite fuer Katharina (#554) aus pruefseite.template.html.

Vier Gruppen:
  A Zuordnung      17 Eintraege, bei denen offen ist, an welche Bedeutung (oder welches Lemma)
                   der Kommentar gehoert (Ausgang "pruefseite" in zuordnung.tsv)
  B Kuerzung       Eintraege, bei denen beim Straffen mindestens ein Teil der Kategorie (c)
                   (eigenstaendige Aussage, Differenzierung, Beleg, Beispiel) entfallen ist
                   (einordnung.json); gezeigt werden unsere Fassung und die entfallenen
                   Teile im Wortlaut
  C Nicht uebernommen   Eintraege ohne passendes Lemma / mit unbrauchbarem Feld
  D Sachliche Rueckfrage   grandmangerie (867): Verfasserangabe widerspricht works.xml
  E Zusammengefuehrte Eintraege   huon (mit henne), rephuon (mit rephenne)

Die Belege je Bedeutung werden aus dem Korpus gelesen (alle tei/*.tei.xml, ein bis zwei Minuten).

Aufruf (aus der Repositoriumswurzel; <vorstufe.json> erzeugt vorstufe-bauen.py):
    python -X utf8 -E -P scripts/ingest/glossar-554/pruefseite-bauen.py <vorstufe.json> [ausgabe.html]
Standardausgabe: examples/review-pages/Glossar-554-Pruefung.html
"""
import csv
import glob
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import date

from lxml import etree

T = '{http://www.tei-c.org/ns/1.0}'
XID = '{http://www.w3.org/XML/1998/namespace}id'
AUSGABE = 'examples/review-pages/Glossar-554-Pruefung.html'
TEMPLATE = 'scripts/ingest/glossar-554/pruefseite.template.html'
SCHEMA = 'mhdbdb-glossar-554-review-v1'
QUELLENZEILE_HINWEIS = 'Die Quellenzeile „Quelle: Glossar Kochbuchforschung dig_ESTivum von Katharina Zeppezauer-Wachauer (2016-2026)“ wird beim Einfügen automatisch angehängt; sie gehört nicht in das Textfeld.'

# Fall C: Lemma, auf das sich die Frage bezieht (nur zur Anzeige)
C_LEMMA = {'560': 'lemma_22732', '1611': 'lemma_39229'}
# Fall A "Lemma offen": mehrere Kandidaten
A_KANDIDATEN = {'93': ['lemma_15723', 'lemma_15724', 'lemma_29871']}


def lade_json_ordner(muster):
    alle = {}
    for pfad in sorted(glob.glob(muster)):
        alle.update(json.load(open(pfad, encoding='utf-8')))
    return alle


def einzeiler(t):
    return re.sub(r'\s*\n\s*', ' ', t).strip()


def entfallenes_modul():
    spec = importlib.util.spec_from_file_location('entfallenes', 'scripts/ingest/glossar-554/entfallenes-suchen.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def lexikon_sinne(ziele):
    lex = etree.parse('authority-files/lexicon.xml')
    cons = etree.parse('authority-files/concepts.xml')
    label = {}
    for c in cons.iter(T + 'category'):
        terms = c.findall(T + 'catDesc/' + T + 'term')
        de = [x.text for x in terms if x.get('{http://www.w3.org/XML/1998/namespace}lang') == 'de' and x.get('type') is None]
        label[c.get(XID)] = de[0] if de else '?'
    info = {}
    for e in lex.iter(T + 'entry'):
        i = e.get(XID)
        if i not in ziele:
            continue
        sinne = []
        for k, s in enumerate(e.findall(T + 'sense'), 1):
            sinne.append({
                'id': s.get(XID), 'nr': k,
                'concepts': [label.get(p.get('target').split('#')[1], '?') for p in s.findall(T + 'ptr')],
                'count': 0, 'examples': [],
            })
        info[i] = {
            'id': i, 'orth': e.find(T + 'form/' + T + 'orth').text,
            'pos': [p.text for p in e.findall(T + 'gramGrp/' + T + 'pos')],
            'senses': sinne, 'ohne_sense': 0,
        }
    return info


def belege_zaehlen(info):
    sidx = {s['id']: s for v in info.values() for s in v['senses']}
    for f in sorted(glob.glob('tei/*.tei.xml')):
        sigle = os.path.basename(f).split('.')[0]
        ws = list(etree.parse(f).iter(T + 'w'))
        texte = None
        for k, w in enumerate(ws):
            ref = w.get('lemmaRef')
            if not ref:
                continue
            for tok in ref.split():
                lid = tok.split('#')[-1]
                if lid not in info:
                    continue
                if texte is None:
                    texte = [''.join(x.itertext()) for x in ws]
                s = sidx.get((w.get('ana') or '').split('#')[-1])
                if s is None:
                    info[lid]['ohne_sense'] += 1
                    continue
                s['count'] += 1
                if len(s['examples']) < 4 and all(b['sigle'] != sigle for b in s['examples']):
                    s['examples'].append({
                        'sigle': sigle,
                        'before': ' '.join(texte[max(0, k - 5):k]),
                        'form': texte[k],
                        'after': ' '.join(texte[k + 1:k + 6]),
                    })


def sinn_option(lemma, s, prefill, text_label, mit_lemma=False):
    begriffe = ' · '.join(s['concepts']) or 'keine Begriffe'
    kopf = ('Lemma „%s“, ' % lemma['orth']) if mit_lemma else ''
    return {
        'value': 'sense:' + s['id'],
        'label': '%sBedeutung %d (%s, %d Belege)' % (kopf, s['nr'], begriffe, s['count']),
        'needsText': True, 'textLabel': text_label, 'prefill': prefill,
    }


def lemma_anzeige(l):
    return {'id': l['id'], 'orth': l['orth'], 'pos': l['pos']}


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    vor = {o['id']: o for o in json.load(open(sys.argv[1], encoding='utf-8'))}
    ausgabe = sys.argv[2] if len(sys.argv) > 2 else AUSGABE
    kom = lade_json_ordner('ingest/glossar-554/kommentare/*.json')
    einordnung = json.load(open('ingest/glossar-554/einordnung.json', encoding='utf-8'))
    zuordnung = list(csv.DictReader(open('ingest/glossar-554/zuordnung.tsv', encoding='utf-8'), delimiter='\t'))
    ent = entfallenes_modul()

    a_zeilen = [r for r in zuordnung if r['ausgang'] == 'pruefseite']
    c_zeilen = [r for r in zuordnung if r['ausgang'] == 'kein-kommentar'
                and r['grund_art'] in ('lemma-fehlt', 'lemma-passt-nicht', 'bedeutungsliste')]
    ziele = set(A_KANDIDATEN['93']) | set(C_LEMMA.values())
    ziele |= {r['lemma_id'] for r in a_zeilen if r['lemma_id']}
    info = lexikon_sinne(ziele)
    belege_zaehlen(info)

    faelle = []

    def fall(gruppe, gid, **kw):
        o = vor[gid]
        f = {'id': '%s-%s' % (gruppe, gid), 'group': gruppe, 'glossarId': gid, 'title': o['title'],
             'wortklasse': o['wk'] or '', 'nhd': o['nhd'], 'lemma': None, 'lemmaNote': '',
             'reasonLabel': 'Vorschlag · keine Entscheidung', 'proposalText': '', 'proposalLabel': '',
             'dropped': [], 'vermerk': '', 'fullText': '', 'fullLabel': '',
             'enzOriginal': o['enz_t'], 'poetOriginal': o['poet_t'], 'senses': []}
        f.update(kw)
        faelle.append(f)

    anderes = {'value': 'other', 'label': 'Anders: siehe Kommentar unten', 'needsText': False}
    nicht = {'value': 'none', 'label': 'Nicht übernehmen', 'needsText': False}

    # ---------------- A ----------------
    for r in a_zeilen:
        gid = r['glossar_id']
        o = vor[gid]
        vorschlag = einzeiler(o['enz_t'] + ('\n\n' + o['poet_t'] if o['poet_t'] else ''))
        tl = 'Kommentartext (Du kannst ihn ändern). ' + QUELLENZEILE_HINWEIS
        if gid in A_KANDIDATEN:
            lemmata = [info[l] for l in A_KANDIDATEN[gid]]
            senses = []
            options = []
            for l in lemmata:
                for s in l['senses']:
                    senses.append(dict(s, label='Lemma „%s“ (%s), Bedeutung %d' % (l['orth'], ', '.join(l['pos']), s['nr'])))
                    options.append(sinn_option(l, s, vorschlag, tl, mit_lemma=True))
            fall('A', gid, question='Welches der drei Lemmata meint das Glossar mit „âme“ (Ohm, ein Flüssigkeitsmaß)?',
                 reason='Warum wir nicht selbst entschieden haben: ' + r['grund'], reasonLabel='Warum offen',
                 proposalText=vorschlag, proposalLabel='Glossartext in Format und Anführungszeichen bereinigt, noch nicht gestrafft',
                 senses=senses, options=options + [nicht, anderes])
            continue
        lem = info[r['lemma_id']]
        sinne = lem['senses']
        if gid == '103':
            frage = 'Soll das Wort „briech“ (breiig) unter „brî“ mitlaufen? „brî“ hat nur eine Bedeutung und damit nur Platz für eine Notiz, und dafür liegt schon ein eigener Glossartext vor (Gruppe B).'
            opts = [{'value': 'sense:' + sinne[0]['id'], 'label': 'Ja, als Ergänzung zum Kommentar von „brî“ (Einarbeitung nach Deiner Entscheidung zu „brî“)',
                     'needsText': True, 'textLabel': 'Ergänzender Text zu „briech“ (Du kannst ihn ändern)', 'prefill': vorschlag}, nicht, anderes]
        elif gid == '1759':
            frage = 'Soll der Text zum Appellativ „slunthart“ an der Bedeutung des Namens „Slinthart“ stehen, obwohl ein Appellativ-Lemma fehlt?'
            opts = [sinn_option(lem, sinne[0], vorschlag, tl),
                    {'value': 'vormerken', 'label': 'Nicht jetzt: Appellativ-Lemma „slunthart“ später nachrüsten, Text dann dort', 'needsText': False},
                    nicht, anderes]
        else:
            frage = 'An welcher Bedeutung von „%s“ soll der Kommentar stehen?' % lem['orth']
            opts = [sinn_option(lem, s, vorschlag, tl) for s in sinne] + [nicht, anderes]
        note = ''
        if lem['ohne_sense']:
            note = 'Dazu %d weitere Vorkommen im Korpus, die noch keiner Bedeutung zugeordnet sind (nicht in den Zahlen oben).' % lem['ohne_sense']
        fall('A', gid, question=frage, lemma=lemma_anzeige(lem), lemmaNote=note,
             reason='Warum wir nicht selbst entschieden haben: ' + r['grund'], reasonLabel='Warum offen',
             proposalText=vorschlag, proposalLabel='Glossartext in Format und Anführungszeichen bereinigt, noch nicht gestrafft',
             senses=sinne, options=opts)

    # ---------------- B ----------------
    for gid in sorted((k for k, v in einordnung.items() if not k.startswith('_') and v.get('c')), key=int):
        o = vor[gid]
        k = kom[gid]
        auto_b, offen = ent.entfallene(o, k)
        c = einordnung[gid]['c']
        if max(c) > len(offen):
            sys.exit('FEHLER: Einordnung %s verweist auf Stueck %d, Suche liefert nur %d' % (gid, max(c), len(offen)))
        dropped = [offen[i - 1].strip() for i in c]
        zeile = next(r for r in zuordnung if r['glossar_id'] == gid)
        lem = info.get(zeile['lemma_id'])
        quelle = o['enz_t'] + ('\n\n' + o['poet_t'] if k.get('poet') == 'uebernommen' else '')
        voll = einzeiler(quelle)
        tl = 'Kommentartext (Du kannst ihn ändern). ' + QUELLENZEILE_HINWEIS
        optionen = [
            {'value': 'passt', 'label': 'Passt so: unsere gestraffte Fassung übernehmen, die entfallenen Teile bleiben weg', 'needsText': False},
            {'value': 'teile', 'label': 'Fassung übernehmen, aber bestimmte entfallene Teile bleiben bzw. kommen zurück', 'needsText': True,
             'textLabel': 'Fassung mit den Teilen, die bleiben sollen. ' + QUELLENZEILE_HINWEIS, 'prefill': k['text']},
            {'value': 'voll', 'label': 'Den ganzen Text übernehmen (nur Format und Anführungszeichen bereinigt)', 'needsText': True,
             'textLabel': tl, 'prefill': voll},
            nicht, anderes]
        extra = {}
        frage = 'Passt unsere gestraffte Fassung, oder soll einer der entfallenen Teile bleiben?'
        if gid == '2084':
            frage = 'Der enzyklopädische Teil von „brôt“ ist im Glossar ein Zitat aus Peter C. A. Schels. Wie gehen wir damit um?'
            optionen = [
                {'value': 'eigener-teil', 'label': 'Nur Deinen eigenen Teil übernehmen (Zwillingsformel und Belege), den Schels-Auszug weglassen', 'needsText': False},
                {'value': 'schels-nachweis', 'label': 'Den Schels-Auszug mit Schels-Nachweis in den Kommentar übernehmen (Titel, Adresse, Abrufdatum 17.11.2017)', 'needsText': True,
                 'textLabel': 'Kommentartext mit Schels-Nachweis. ' + QUELLENZEILE_HINWEIS, 'prefill': k['text']},
                {'value': 'eigene-zusammenfassung', 'label': 'Den Schels-Auszug durch eine eigene Zusammenfassung ersetzen', 'needsText': True,
                 'textLabel': 'Kommentartext mit eigener Zusammenfassung. ' + QUELLENZEILE_HINWEIS, 'prefill': k['text']},
                nicht, anderes]
            dropped = []
            extra['vermerk'] = ('Fundort: Im Glossareintrag „brôt“ (ID 2084) beginnt das Feld „Enzyklopädische Information“ mit der Zeile '
                                '„Informationen aus: Peter C. A. Schels: Kleine Enzyklopädie des deutschen Mittelalters“, einer Internetadresse und '
                                '„(17.11.2017)“; danach steht der gesamte Rest des Feldes (rund 8.400 Zeichen) in einem Zitatblock. '
                                'Unser Kommentartext enthält deshalb nur Deinen eigenen Teil aus dem Feld „Poetisierung des Wortes“. '
                                'Wir haben den Zitatblock nicht mit der Quelle abgeglichen und unter Deinem Namen und Deiner Quellenzeile soll kein fremder Text stehen.')
        else:
            extra['vermerk'] = einordnung[gid].get('vermerk', '')
        fall('B', gid, question=frage, lemma=lemma_anzeige(lem) if lem else None,
             reason='Beim Straffen sind in diesem Eintrag %d Teile entfallen, die eine eigenständige Aussage, Differenzierung, einen Beleg oder ein Beispiel enthalten.' % len(dropped)
             if dropped else 'Dieser Eintrag enthält fremden Text.',
             reasonLabel='Warum Du entscheidest',
             proposalText=k['text'], proposalLabel='Unsere gestraffte Fassung (ohne die entfallenen Teile)',
             dropped=dropped, options=optionen, **extra)

    # ---------------- C ----------------
    for r in c_zeilen:
        gid = r['glossar_id']
        lid = r['lemma_id'] or C_LEMMA.get(gid)
        lem = info.get(lid) if lid else None
        art = r['grund_art']
        if art == 'lemma-fehlt':
            frage = 'Das Lexikon hat kein Lemma für diesen Eintrag. Soll es als fehlendes Lemma vorgemerkt werden?'
            opts = [{'value': 'vormerken', 'label': 'Ja, als fehlendes Lemma vormerken; der Glossartext wird dann später dort eingefügt', 'needsText': False},
                    {'value': 'nicht-noetig', 'label': 'Nein, kein Lemma nötig; der Eintrag bleibt außerhalb des Lexikons', 'needsText': False}, anderes]
        elif art == 'lemma-passt-nicht':
            frage = 'Das einzige Lemma „Atze“ ist ein Personenname, der Glossareintrag meint das Appellativ („atzen“, Verweis). Was soll damit geschehen?'
            opts = [{'value': 'nicht-noetig', 'label': 'Nichts: der Eintrag ist nur ein Verweis auf „atzen“ und braucht keinen Kommentar', 'needsText': False},
                    {'value': 'vormerken', 'label': 'Appellativ-Lemma „atze“ als fehlendes Lemma vormerken', 'needsText': False}, anderes]
        else:
            frage = 'Der Eintrag nennt nur die zwei Bedeutungen, die das Lexikon schon führt. Reicht das, oder soll daraus ein Kommentar werden?'
            opts = [{'value': 'nicht-noetig', 'label': 'Reicht: nichts übernehmen', 'needsText': False},
                    {'value': 'uebernehmen', 'label': 'Doch übernehmen', 'needsText': True, 'textLabel': 'Kommentartext. ' + QUELLENZEILE_HINWEIS,
                     'prefill': einzeiler(vor[gid]['enz_t'])}, anderes]
        fall('C', gid, question=frage, lemma=lemma_anzeige(lem) if lem else None,
             reason='Warum wir den Eintrag nicht übernommen haben: ' + r['grund'], reasonLabel='Warum offen',
             senses=lem['senses'] if lem else [], options=opts)

    # ---------------- D ----------------
    o = vor['867']
    original = einzeiler(o['enz_t'])
    korrigiert = 'Altfranzösisch „grandmangerie“, etwa ‚große, herzhafte Mahlzeit‘; in Verwendung in der „Crône“ Heinrichs von dem Türlin.'
    ohne = 'Altfranzösisch „grandmangerie“, etwa ‚große, herzhafte Mahlzeit‘; in Verwendung in der „Crône“.'
    belassen = 'Altfranzösisch „grandmangerie“, etwa ‚große, herzhafte Mahlzeit‘; in Verwendung in der „Crône“ Ulrichs von dem Türlin.'
    tl = 'Kommentartext. ' + QUELLENZEILE_HINWEIS
    fall('D', '867', question='Der Glossartext nennt Ulrich von dem Türlin als Verfasser der „Crône“. Unsere Normdaten nennen Heinrich von dem Türlin. Was soll im Kommentar stehen?',
         reason=('Beleg: In authority-files/works.xml ist „Diu Crône“ (work_363, Sigle CRO) mit author ref persons.xml#person_867 geführt, das ist Heinrich von dem Türlin. '
                 'Ulrich von dem Türlîn ist ein eigener Eintrag (persons.xml#person_46). Wir ändern den Inhalt eines Glossartextes nicht ohne Deine Zustimmung; '
                 'der Eintrag geht erst nach Deiner Antwort in das Lexikon.'),
         reasonLabel='Warum wir nachfragen',
         proposalText=korrigiert, proposalLabel='Vorschlag mit Heinrich von dem Türlin',
         options=[{'value': 'heinrich', 'label': 'Verfasser berichtigen: Heinrich von dem Türlin', 'needsText': True, 'textLabel': tl, 'prefill': korrigiert},
                  {'value': 'wortlaut', 'label': 'Wortlaut des Glossars belassen (Ulrich von dem Türlin)', 'needsText': True, 'textLabel': tl, 'prefill': belassen},
                  {'value': 'ohne-verfasser', 'label': 'Verfasserangabe weglassen', 'needsText': True, 'textLabel': tl, 'prefill': ohne},
                  nicht, anderes])
    faelle[-1]['senses'] = []
    faelle[-1]['fullText'] = original
    faelle[-1]['fullLabel'] = 'Originaltext im Glossar (Wortlaut)'

    # ---------------- E ----------------
    for gid_a, gid_b, was in (('1900', '1905', 'henne'), ('2264', '2253', 'rëphenne')):
        zeile = next(r for r in zuordnung if r['glossar_id'] == gid_b)
        lem = info.get(zeile['lemma_id']) or lexikon_sinne({zeile['lemma_id']}).get(zeile['lemma_id'])
        titel_b = vor[gid_b]['title']
        k = kom[gid_b]
        fall('E', gid_b, question='„%s“ und „%s“ zeigen auf dieselbe Bedeutung, und ein Lemma trägt je Bedeutung nur eine Notiz. Wir haben die Poetisierungsteile beider Einträge in einem Kommentar zusammengeführt. Passt das?' % (was, titel_b),
             lemma=lemma_anzeige(lem) if lem else None,
             reason='Warum Du entscheidest: ' + k['zusammenfuehrung'] + '.',
             reasonLabel='Warum wir nachfragen',
             proposalText=k['text'], proposalLabel='Zusammengeführte Fassung (gestrafft)',
             fullText=vor[gid_a]['poet_t'] or vor[gid_a]['enz_t'],
             fullLabel='Originaltext im Glossar: Poetisierung des Eintrags „%s“ (Wortlaut)' % was,
             options=[{'value': 'zusammen', 'label': 'Zusammengeführte Fassung übernehmen', 'needsText': True,
                       'textLabel': 'Kommentartext (Du kannst ihn ändern). ' + QUELLENZEILE_HINWEIS, 'prefill': k['text']},
                      nicht, anderes],
             senses=lem['senses'] if lem else [])

    n = {g: sum(1 for f in faelle if f['group'] == g) for g in 'ABCDE'}
    gruppen = [
        {'id': 'A', 'title': 'Zuordnung',
         'text': 'In %d Fällen lässt sich am Text und an den Korpusbelegen nicht sicher sagen, an welcher Bedeutung des Lemmas der Kommentar stehen soll (oder welches Lemma gemeint ist). Ein Lemma trägt je Bedeutung nur eine Notiz. Der Textvorschlag ist der Glossartext in Format und Anführungszeichen bereinigt, aber noch nicht gestrafft: die Straffung folgt, sobald die Zuordnung steht.' % n['A']},
        {'id': 'B', 'title': 'Größere Kürzung',
         'text': 'In %d Einträgen sind beim Straffen auch eigenständige Aussagen, Differenzierungen, Belege oder Beispiele entfallen. Du siehst unsere gestraffte Fassung und darunter genau die entfallenen Teile im Wortlaut, den ganzen Originaltext zum Aufklappen. Bitte sag, ob die Fassung so passt oder welche Teile bleiben sollen.' % n['B']},
        {'id': 'C', 'title': 'Nicht übernommen',
         'text': '%d Einträge haben wir nicht in das Lexikon übernommen, weil es das Lemma nicht gibt oder das Feld nur einen Verweis oder eine Bedeutungsliste enthält. Wir legen keine neuen Lemmata an; bitte sag, ob der Eintrag vorgemerkt werden soll.' % n['C']},
        {'id': 'D', 'title': 'Sachliche Rückfrage',
         'text': '%d Eintrag, bei dem der Glossartext einer Angabe in unseren Normdaten widerspricht. Wir ändern keinen Inhalt ohne Dich.' % n['D']},
        {'id': 'E', 'title': 'Zusammengeführte Einträge',
         'text': 'In %d Fällen zeigen zwei Glossareinträge (Henne und Huhn, Rebhenne und Rebhuhn) auf dieselbe Bedeutung. Wir haben ihre Poetisierungsteile in einem Kommentar zusammengeführt; bitte sag, ob das passt.' % n['E']},
    ]
    intro = ('Danke, dass Du das Glossar Kochbuchforschung ins Lexikon holst. Ein Großteil der Einträge ist eindeutig und läuft ohne Deine Hilfe in die Daten (bei der Übernahme '
             'gelten Deine Vorgaben: enzyklopädische Information immer, Poetisierung nur mit Mehrwert, Ausdruck straffen ohne Inhaltsänderung). Hier stehen die %d Fälle, bei denen wir Dich '
             'brauchen: %d zur Zuordnung, %d mit größerer Kürzung, %d nicht übernommene, %d Sachfrage und %d Zusammenführungen. Was auf dieser Seite steht, geht erst nach Deiner Antwort in die Daten.'
             % (len(faelle), n['A'], n['B'], n['C'], n['D'], n['E']))

    fp = hashlib.sha256(json.dumps(faelle, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    daten = {'schema': SCHEMA, 'fingerprint': fp, 'date': date.today().isoformat(), 'commit': commit,
             'intro': intro, 'groups': gruppen, 'cases': faelle}
    html = open(TEMPLATE, encoding='utf-8').read()
    nutzlast = json.dumps(daten, ensure_ascii=False).replace('</', '<\\/')
    if '__REVIEW_DATA__' not in html:
        sys.exit('FEHLER: Platzhalter __REVIEW_DATA__ fehlt in der Vorlage')
    html = html.replace('__REVIEW_DATA__', nutzlast)
    os.makedirs(os.path.dirname(ausgabe), exist_ok=True)
    with open(ausgabe, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print('geschrieben: %s (%d Zeichen)' % (ausgabe, len(html)))
    print('Faelle: %d = %s' % (len(faelle), ' + '.join('%s %d' % (g, n[g]) for g in 'ABCDE')))
    print('Fingerabdruck %s, Commit %s' % (fp, commit[:12]))


main()
