"""Arbeitet KZWs Pruefergebnisse vom 15.10.2026 (#554) in authority-files/lexicon.xml ein.

Quellen:
  ingest/glossar-554/kzw-2026-10-15/Glossar-554-Antworten-2026-10-15T11-15-12.json  (KZWs 47 Entscheidungen, unveraendert)
  ingest/glossar-554/kommentare/*.json, zuordnung.tsv                               (Stand PR #600)
  <vorstufe.json> von vorstufe-bauen.py                                              (nur fuer abebizen, dessen Text die Pruefseite nicht trug)

Was geschieht (alle Bearbeitungen stehen unten als Konstanten, jede mit Zeichenfolge,
die genau einmal im Ausgangstext vorkommen muss, sonst harter Fehler):
  - Paket 1: A-Texte mit gewaehlter Bedeutung (gestrafft nur um Verweise ins Leere, Links, Abrufdaten
    und Wiederholungen; Wortlaut sonst unveraendert), B passt / teile / eigener-teil, D, E
  - Paket 2: Neufassungen (wanne, schale, ezzich, apfelbiz, wîn, brâte, klamirre)
  - Paket 3: letzen (Bedeutung 4 loeschen, Etikette/Zeremoniell an Bedeutung 1), naschen (Reihenfolge der Bedeutungen)
  - ber: die Belegverse zu "niht ein ber" kommen auf KZWs Wunsch zurueck in den Text

Ausgaben: ingest/glossar-554/kzw-2026-10-15/endtexte.json (Text je Notiz) und umsetzung.tsv
(Laenge vorher/nachher). Ohne --schreiben wird nichts in lexicon.xml geschrieben.

Aufruf (aus der Repositoriumswurzel):
    python -X utf8 -E -P scripts/ingest/glossar-554/antworten-einarbeiten.py <vorstufe.json> [--schreiben]
Die Quellenzeile haengt dieses Skript an, nie von Hand.
"""
import csv
import glob
import json
import re
import sys
from xml.sax.saxutils import escape

LEXIKON = 'authority-files/lexicon.xml'
ORDNER = 'ingest/glossar-554/kzw-2026-10-15/'
ANTWORTEN = ORDNER + 'Glossar-554-Antworten-2026-10-15T11-15-12.json'
QUELLE = 'Quelle: Glossar Kochbuchforschung dig_ESTivum von Katharina Zeppezauer-Wachauer (2016-2026)'
RESP = 'contributors.xml#contrib_003'
STAND = '15.10.2026'

# ---- Paket 1: Straffung der A-Texte. (alt, neu); alt muss genau einmal vorkommen. ----
# Erlaubt ist nur, was die Regel von #600 als "gestrafft" fuehrt: Verweise ins Leere, Links, Abrufdaten, Wiederholungen,
# dazu fehlende Leerzeichen und Satzzeichen. Der Wortlaut bleibt der des Glossars.
STRAFFEN = {
    '178': [(' (s. auch enzyklopäd. Information)', '')],
    '911': [('„genern“ist', '„genern“ ist'), ('genert“(AC1', 'genert“ (AC1')],
    '1121': [
        (' Hier klicken für weitere 60 Belegstellen von mhd. „koste“ im „Alexander“ (MHDBDB).', ''),
        (" (insbesondere mit der kulinarischen Bedeutungsebene, 'Speise', 'Nahrung', 'Zehrung' usw., s.o.)", ''),
        (', s. Beispielliste', ''),
    ],
    '1146': [('(SAX 5374, s.u.)', '(SAX 5374)'), ('Leben“Lamprechts', 'Leben“ Lamprechts')],
    '1159': [(' (s. externe Links zu Lexer, DWB etc.)', '')],
    '1328': [('(s.u.; OVW 1,25,1,23)', '(OVW 1,25,1,23)')],
    '1331': [
        (' (s. http://www.koeblergerhard.de/mhd/2A/mhd_k.html, aufgerufen am 15.01.2017)', ''),
        ('neuen„Bayerischen', 'neuen „Bayerischen'),
    ],
    '1438': [
        ('verkürzt„nüehter“', 'verkürzt „nüehter“'),
        ('zu sich nehmen nicht betrunken sein', 'zu sich nehmen; nicht betrunken sein.'),
    ],
    '1439': [
        (' (Herkunft: Mt 3,12: "Schon hält er die Schaufel in der Hand; er wird die Spreu vom Weizen trennen und den Weizen in seine Scheune bringen; die Spreu aber wird er in nie erlöschendem Feuer verbrennen.")', ' (Herkunft: Mt 3,12)'),
        ('im„Jüngeren', 'im „Jüngeren'),
        ('kerne,“LGR', 'kerne,“ LGR'),
        ('"„sanges kerne“"', '„sanges kerne“'),
    ],
    '1821': [('Bedeutungen: Schlund, Kehle Abgrund (wie: Höllenschlund) Schlinger, Fresser, Gierschlund Die eigentlich',
              'Bedeutungen: (1) Schlund, Kehle; (2) Abgrund (wie: Höllenschlund); (3) Schlinger, Fresser, Gierschlund. Die eigentlich')],
    '2318': [('menschl. körpers Das Lemma', 'menschl. körpers. Das Lemma')],
}

# ---- Paket 2 und ber: Bearbeitung des Ausgangstextes (alt, neu) ----
BEARBEITEN = {
    '387': [(  # ezzich
        'In der mittelalterlichen Literatur ist Essig zahlreich zu finden (197 Treffer in allen 656 Texten der Mittelhochdeutschen Begriffsdatenbank MHDBDB, Stand 30.11.2015), am häufigsten in der Kochbuchliteratur und der religiösen Dichtung (der Essigtrunk, der Christus am Kreuz gereicht wurde). Erstaunlicherweise steht er kaum',
        'In der mittelalterlichen Literatur begegnet Essig am häufigsten in der Kochbuchliteratur und in der religiösen Dichtung (der Essigtrunk, der Christus am Kreuz gereicht wurde). Erstaunlicherweise steht er jedoch kaum')],
    '518': [(  # apfelbiz
        'In der MHDBDB finden sich 38 Belege (Abruf 14.06.2016) im Kontext von zehn Zeilen für „apfel + Eva“, alle bis auf einen aus der zweiten Hälfte des 13. Jahrhunderts. Der älteste stammt von Bruder Wernher („Owe daz Eva den apfel beiz“',
        'In der MHDBDB finden sich 32 Belege, in denen „apfel“ höchstens zehn Verse von „Eva“ entfernt steht (Zählung der Lemmabelege in Verstexten, Stand ' + STAND + '). Ein Beispiel ist Bruder Wernher („Owe daz Eva den apfel beiz“')],
    '1444': [(  # wîn
        'Ergebnis der Textsuche der MHDBDB (Stand 25.06.2015): „mete“ 69 Belege inklusive „honecmete“ und „mandelmet“, „môraz“ 56, „klârêt“ 47, „lûtertranc“ 26, „malvasier“ 7, „sinôpel“ 6, „alantwîn“ 1 usw.',
        'Zählung der Lemmabelege im Korpus der MHDBDB (Stand ' + STAND + '): „mete“ 63 Belege inklusive „honecmete“ und „mandelmet“, „môraz“ 57, „klârêt“ 50, „lûtertranc“ 26, „malvasier“ 8, „sinôpel“ 6, „alantwîn“ 1 usw.')],
    '606': [(  # brâte
        'Meist ist nur von „guoter spîse“ (202 Treffer in 654 Texten der MHDBDB, Stand 25.06.2015), „genuoc spîse“ (105), „spîse warm“ (11), „spîse kalt“ (16) oder „spîse süez“ (34) die Rede. Auch scheinbar genauere Termini wie „brâte“ (200 Belege) und „brâte+guot“ (60) dienen der Ausschmückung von Menge, Vielfalt und Qualität, nicht der Spezifizierung der Speisen. Die Zahlen sind nicht vollständig dem Fleischbraten zuzuordnen, denn „brât“ kann auch die Weichteile des Körpers meinen und die Disambiguierung in der MHDBDB war zum Zeitpunkt dieser Arbeit nicht abgeschlossen; bei „brâte+guot“ ist mit großer Wahrscheinlichkeit die Speise gemeint.',
        'Meist ist nur allgemein von „guoter spîse“, „genuoc spîse“, „spîse warm“, „spîse kalt“ oder „spîse süez“ die Rede. Auch scheinbar genauere Termini wie „brâte“, auch in Verbindung mit „guot“, dienen der Ausschmückung von Menge, Vielfalt und Qualität, nicht der Spezifizierung der Speisen. Nicht jeder Beleg von „brât“ ist dem Fleischbraten zuzuordnen, denn „brât“ kann auch die Weichteile des Körpers meinen; wo „brâte“ mit „guot“ verbunden ist, ist mit großer Wahrscheinlichkeit die Speise gemeint.')],
    '1685': [  # klamirre: aus der Ich-Perspektive in Lexikonstil
        ('Der einzige mir bekannte Beleg', 'Der einzige bekannte Beleg'),
        ("ist mir nicht sicher;", 'ist unsicher;'),
        ('Das älteste mir bekannte Rezept', 'Das älteste bekannte Rezept'),
        (' auf swf. „pavese“, wie ich erst gegen Ende meiner Recherchen entdeckt habe.', ' auf swf. „pavese“.'),
        ('Interessant erscheint mir die Überlegung Stöwers', 'Interessant ist die Überlegung Stöwers'),
        ('Auf gut Deutsch beziehungsweise Österreichisch wird es sich bei dem angeblich so typisch österreichischen Gericht wohl um Pofesen (Arme Ritter) handeln, also um',
         'Bei dem angeblich so typisch österreichischen Gericht handelt es sich wohl um Pofesen (Arme Ritter), also um'),
    ],
    '1913': [(  # ber: die Belegverse fuer "wertlos" kommen zurueck (KZW: "gib die Beispiele fuer wertlos wieder dazu")
        'Phraseologisch steht „niht ein ber“ für ‚überhaupt nichts‘, ‚wertlos‘: „niht ein ber ahten“ (TR 16268; REN 25028; TRO 12679; Erec, Wolffenbütteler Fragment II,76), „niht ein ber geben“ (PZ 564,30–565,2), „niht gegen ein ber“ (JT 439,4,391–394; URS 936–938).',
        'Phraseologisch steht „niht ein ber“ für ‚überhaupt nichts‘, ‚wertlos‘. Beispiele für „niht ein ber ahten“: „ern haete waerliche / Rome und elliu riche, / elliu lant und elliu mer / derwider niht gahtet ein ber“ (TR, V. 16265–16268); „so ahtes du uf sie nit ein ber“ (REN, V. 25028); „wan ich enahte ûf iuwer drô / niht sô tiure als umb ein ber“ (TRO, V. 12678–12679); „daz ahte der ander eine bere“ („Erec“, Wolffenbütteler Fragment II,76, zit. nach: Leitzmann, Wolff, Gärtner [2006]). Für „niht ein ber geben“: „vür allen sturm niht ein ber / gaebe si ze drîzec jâren, / ob man ir wolde vâren“ (PZ, V. 564,30–565,2). Für „niht gegen ein ber“: „Maria, vreuden wunne, din lop wart nie bedoenet. / waer ieglich stern ein sunne und ieglich stein uf erden sam geschoenet, / und gaeb der glast mit glaste widerstozen, / klarheit Marien schoene kund ez niht gen einer per genozen.“ (JT, V. 439,4,391–394); „sine schuofen niht gegen einer ber / und funden nihtes mê / wan daz diu wîp funden ê“ (URS, V. 936–938).')],
}

# ---- Paket 2: wanne und schale, auf Bedeutungen verteilt (Sense-ID -> Text) ----
NEU = {
    '225': {  # wanne, lemma_18414: Kornschwinge und Viehtrog an Bedeutung 1, Gefaess und Bildlichkeit an Bedeutung 4
        'lemma_18414_sense_30995':
            'Im engeren Sinn bezeichnet „wanne“ die Kornschwinge (von lat. „vannus“, ‚Getreide-, Futterschwinge‘): ein landwirtschaftliches Gerät, '
            'meist oval-rund und aus Ruten, Binsen, Stroh oder dünnen Holzspänen geflochten (Fassbinderwerk), in dem Getreide durch Schwingen und '
            'Aufwerfen von Spreu und Staub gereinigt wird. Teilweise ist die „wanne“ auch ein (Wasser-)Trog für Vieh.',
        'lemma_18414_sense_30998':
            'In weiterer Bedeutung ist die „wanne“ jedes oval-runde Gefäß mit flachem Boden, in dem Haushaltsware aufbewahrt wird. '
            'Als sprachliches Stilmittel ist sie häufig im Gebrauch, weil sie ein anschauliches Bild schafft: Ihre Eigenschaften, vor allem ihre '
            'räumliche Dimension, werden auf Personen oder deren Körperteile übertragen. Neben der Größe spielt in diesem Bild wahrscheinlich auch '
            'die unhöfische, bäuerlich-einfache Verwendung eine Rolle.',
    },
    '1442': {  # schale, lemma_5158
        'lemma_5158_sense_8016':
            'Als Küchenutensil ist die „schale“ Tafelgeschirr (z.B. „in wîten goldes schâlen met, môraz unde wîn,“ NLB 1812,3).',
        'lemma_5158_sense_80569':
            'Gemeint sein kann die Eierschale (z.B. „brich ayer vff an der spitz vnd lär die schällan gancz“, KBL4, 84,1).',
        'lemma_5158_sense_42552':
            'Gemeint sein kann der Panzer eines Krustentiers oder die Muschelschale (z.B. „Nyem gros kreps und nyem die schallan also ganz davon“, ABS 8,1).',
        'lemma_5158_sense_8017':
            'Die „schale“ ist auch die äußere Hülle oder Hülse einer Pflanze, eines Getreides, einer Hülsenfrucht oder einer Nuss. '
            'Der Marner schafft daraus eine Metapher für die Dichtung Walthers von der Vogelweide, die er als „sanges kerne“ bezeichnet: '
            '„nu merckent, wie her Walther sanges kerne von der schale schiett.“ (MRS 1,7,28,20). Walthers Kunst scheint dabei den genießbaren '
            'Nusskern darzustellen, während die harte Schale alle vom Marner nicht geschätzten Dichter sind (in 1,6,17,1 wird Walther ebenfalls '
            'als Vorbild des Marners genannt). Weitere bildhafte Verwendung nach Lexer: „bildl.“ der wilden rede nime ich den kern her von der '
            'schal Msh. 3,29a. schel uns von der sünden schal (: schal) Such. 44,117.',
    },
}

# Entscheidung steht, der Text kommt nicht in die Daten (Grund steht im Protokoll)
UEBERSPRUNGEN = {
    '1759': 'Zwilling 1753 (slinthart) traegt an derselben Bedeutung schon fast denselben Text (Notiz aus #600), eine Notiz je Bedeutung',
}
ABEBIZEN_SENSE ='lemma_27894_sense_44181'


def ez(t):
    return re.sub(r'\s*\n\s*', ' ', t).strip()


def einmal(text, alt, neu, wer):
    n = text.count(alt)
    if n != 1:
        sys.exit('FEHLER: %s: %r kommt %d-mal vor, erwartet 1' % (wer, alt[:60], n))
    return text.replace(alt, neu)


def bearbeite(text, regeln, wer):
    for alt, neu in regeln:
        text = einmal(text, alt, neu, wer)
    return text


def lade_kommentare():
    alle = {}
    for pfad in sorted(glob.glob('ingest/glossar-554/kommentare/*.json')):
        alle.update(json.load(open(pfad, encoding='utf-8')))
    return alle


def baue_endtexte(vorstufe):
    d = json.load(open(ANTWORTEN, encoding='utf-8'))
    ent = {x['glossarId']: x for x in d['decisions']}
    kom = lade_kommentare()
    zuordnung = {}
    for r in csv.DictReader(open('ingest/glossar-554/zuordnung.tsv', encoding='utf-8'), delimiter='\t'):
        if r['sense_id']:
            zuordnung[r['glossar_id']] = r
    out = []  # dict(gid, titel, art, sense, text, vorher)

    def add(gid, art, sense, text, vorher):
        out.append({'glossarId': gid, 'titel': ent[gid]['title'], 'art': art, 'sense': sense, 'text': text, 'vorher': vorher})

    for gid, x in ent.items():
        ch = x['choice']
        if x['group'] == 'A':
            if gid in NEU:
                for sense, text in NEU[gid].items():
                    add(gid, 'A neu gefasst', sense, text, len(ez(vorstufe[gid]['enz_t'] + '\n\n' + vorstufe[gid]['poet_t'])))
            elif gid == '432':
                roh = ez(vorstufe[gid]['enz_t'] + ('\n\n' + vorstufe[gid]['poet_t'] if vorstufe[gid]['poet_t'] else ''))
                add(gid, 'A abebizen (unreviewed, Bedeutung 1 laut Kommentar)', ABEBIZEN_SENSE, roh, len(roh))
            elif gid in UEBERSPRUNGEN:
                add(gid, 'A nicht eingefuegt: ' + UEBERSPRUNGEN[gid], ch.split(':')[1], None, len(x['text']))
            elif ch.startswith('sense:'):
                roh = x['text']
                text = bearbeite(roh, STRAFFEN.get(gid, []), 'A ' + gid)
                add(gid, 'A gestrafft' if text != roh else 'A unveraendert', ch.split(':')[1], text, len(roh))
            # 103 briech: neues Lemma, Paket 4 (Haltepunkt), hier nichts
        elif x['group'] == 'B':
            z = zuordnung[gid]
            if ch == 'teile':
                add(gid, 'B teile', z['sense_id'], x['text'], len(kom[gid]['text']))
            elif ch in ('passt', 'eigener-teil'):
                add(gid, 'B ' + ch, z['sense_id'], kom[gid]['text'], len(kom[gid]['text']))
            elif ch == 'other':
                if gid == '579':
                    add(gid, 'B barn (passt)', z['sense_id'], kom[gid]['text'], len(kom[gid]['text']))
                else:
                    basis = x['text'] or kom[gid]['text']
                    add(gid, 'B neu gefasst', z['sense_id'], bearbeite(basis, BEARBEITEN[gid], 'B ' + gid), len(basis))
        elif x['group'] == 'D':
            add(gid, 'D heinrich', zuordnung[gid]['sense_id'], x['text'], len(kom[gid]['text']))
        elif x['group'] == 'E':
            add(gid, 'E zusammen', zuordnung[gid]['sense_id'], x['text'], len(kom[gid]['text']))
    # ber (teile): der von KZW gelieferte Text ist die gestraffte Fassung, die Beispiele ergaenzt das Skript
    for e in out:
        if e['glossarId'] == '1913':
            e['text'] = bearbeite(e['text'], BEARBEITEN['1913'], 'ber')
            e['art'] = 'B teile (Beispiele fuer "wertlos" wieder dazu)'
    if '1913' not in {e['glossarId'] for e in out}:
        sys.exit('FEHLER: ber (1913) fehlt')
    return out


def lexikon_paket3(zeilen):
    """letzen: Bedeutung 4 loeschen, Etikette/Zeremoniell an Bedeutung 1. naschen: Bedeutungen tauschen."""
    # --- letzen ---
    i = [k for k, z in enumerate(zeilen) if '<sense xml:id="lemma_3725_sense_5899"' in z]
    if len(i) != 1:
        sys.exit('FEHLER: lemma_3725_sense_5899 kommt %d-mal vor' % len(i))
    i = i[0]
    ende = next(j for j in range(i, len(zeilen)) if '</sense>' in zeilen[j])
    block = zeilen[i:ende + 1]
    erwartet = ['<sense xml:id="lemma_3725_sense_5899">',
                '<ptr target="concepts.xml#concept_21072000"/>',
                '<ptr target="concepts.xml#concept_23132000"/>', '</sense>']
    if [z.strip() for z in block] != erwartet:
        sys.exit('FEHLER: sense_5899 sieht anders aus als vermessen: %r' % block)
    del zeilen[i:ende + 1]
    s1 = [k for k, z in enumerate(zeilen) if '<sense xml:id="lemma_3725_sense_5896"' in z]
    if len(s1) != 1:
        sys.exit('FEHLER: lemma_3725_sense_5896 kommt %d-mal vor' % len(s1))
    s1 = s1[0]
    ende1 = next(j for j in range(s1, len(zeilen)) if '</sense>' in zeilen[j])
    ptrs = [j for j in range(s1, ende1) if '<ptr ' in zeilen[j]]
    if any('concept_23132000' in zeilen[j] for j in ptrs):
        sys.exit('FEHLER: sense_5896 traegt Etikette/Zeremoniell schon')
    ids = [re.search(r'concept_(\d+)', zeilen[j]).group(1) for j in ptrs]
    if ids != sorted(ids) or ids[-1] > '23132000':
        sys.exit('FEHLER: ptr-Reihenfolge in sense_5896 nicht aufsteigend: %r' % ids)
    einzug = re.match(r'\s*', zeilen[ptrs[-1]]).group(0)
    zeilen.insert(ptrs[-1] + 1, einzug + '<ptr target="concepts.xml#concept_23132000"/>')
    # --- naschen ---
    a = [k for k, z in enumerate(zeilen) if '<sense xml:id="lemma_57919_sense_93121"' in z]
    b = [k for k, z in enumerate(zeilen) if '<sense xml:id="lemma_57919_sense_93122"' in z]
    if len(a) != 1 or len(b) != 1:
        sys.exit('FEHLER: naschen-Bedeutungen nicht eindeutig')
    a, b = a[0], b[0]
    ea = next(j for j in range(a, len(zeilen)) if '</sense>' in zeilen[j])
    eb = next(j for j in range(b, len(zeilen)) if '</sense>' in zeilen[j])
    if ea + 1 != b:
        sys.exit('FEHLER: naschen: Bedeutungen liegen nicht unmittelbar hintereinander')
    zeilen[a:eb + 1] = zeilen[b:eb + 1] + zeilen[a:ea + 1]


def main():
    schreiben = '--schreiben' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 1:
        sys.exit(__doc__)
    vorstufe = {o['id']: o for o in json.load(open(args[0], encoding='utf-8'))}
    texte = baue_endtexte(vorstufe)

    with open(LEXIKON, encoding='utf-8', newline='') as f:
        inhalt = f.read()
    nl = '\r\n' if '\r\n' in inhalt else '\n'
    zeilen = inhalt.split(nl)
    lexikon_paket3(zeilen)

    einfuegungen = []
    gesehen = set()
    for t in texte:
        sense_id = t['sense']
        if t['text'] is None:
            continue
        if sense_id in gesehen:
            sys.exit('FEHLER: zwei Texte fuer %s' % sense_id)
        gesehen.add(sense_id)
        treffer = [i for i, z in enumerate(zeilen) if '<sense xml:id="%s"' % sense_id in z]
        if len(treffer) != 1:
            sys.exit('FEHLER: %s kommt %d-mal vor (Eintrag %s)' % (sense_id, len(treffer), t['glossarId']))
        i = treffer[0]
        ende = next(j for j in range(i, len(zeilen)) if '</sense>' in zeilen[j])
        block = zeilen[i:ende + 1]
        if any('type="comment"' in z for z in block):
            sys.exit('FEHLER: %s traegt schon eine Kommentar-Notiz (Eintrag %s)' % (sense_id, t['glossarId']))
        defs = [j for j in range(i, ende + 1) if '</def>' in zeilen[j]]
        if len(defs) > 1:
            sys.exit('FEHLER: %s hat mehrere <def>' % sense_id)
        if defs:
            nach = defs[0]
            einzug = re.match(r'\s*', zeilen[nach]).group(0)
        else:
            nach = i
            einzug = re.match(r'\s*', zeilen[i]).group(0) + '  '
        text = t['text'].strip()
        if not text:
            sys.exit('FEHLER: leerer Text fuer Eintrag %s' % t['glossarId'])
        zeile = '%s<note type="comment" xml:lang="de" resp="%s">%s %s</note>' % (einzug, RESP, escape(text), escape(QUELLE))
        einfuegungen.append((nach, zeile))

    with open(ORDNER + 'endtexte.json', 'w', encoding='utf-8', newline='\n') as f:
        json.dump(texte, f, ensure_ascii=False, indent=1)
        f.write('\n')
    with open(ORDNER + 'umsetzung.tsv', 'w', encoding='utf-8', newline='\n') as f:
        f.write('glossar_id\ttitel\tart\tsense_id\tzeichen_vorher\tzeichen_nachher\n')
        for t in texte:
            f.write('%s\t%s\t%s\t%s\t%d\t%d\n' % (t['glossarId'], t['titel'], t['art'], t['sense'], t['vorher'], len(t['text'] or '')))
    print('Notizen: %d (Bedeutungen: %d)' % (len(texte), len(gesehen)))
    arten = {}
    for t in texte:
        arten[t['art'].split(' (')[0]] = arten.get(t['art'].split(' (')[0], 0) + 1
    print(' + '.join('%s %d' % (k, v) for k, v in sorted(arten.items())), '=', sum(arten.values()))
    if not schreiben:
        return
    for nach, zeile in sorted(einfuegungen, key=lambda t: -t[0]):
        zeilen.insert(nach + 1, zeile)
    with open(LEXIKON, 'w', encoding='utf-8', newline='') as f:
        f.write(nl.join(zeilen))
    print('geschrieben: %s (%d Notizen, Zeilenende %s)' % (LEXIKON, len(einfuegungen), repr(nl)))


main()
