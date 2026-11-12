#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#560 Frage 6: die HTML-Pruefseite fuer die ganzen Woerter der WZB, die heute
am Sammellemma lemma_2 "abc" haengen (41 Schreibungen, 247 Tokens).

Eine Karte je Schreibung, nicht je Token: entschieden wird pro Fall gesammelt
(Julia, 12.11.2026: "damit ich pro fall gesammelt entscheiden kann"). Jede
Karte zeigt alle Belege der Schreibung mit Vor- und Folgezeile aus dem TEI;
eine Ausnahme nennt die Pruefende im Kommentar mit der xml:id.

Liest ingest/wzb/370-corresp/abc-befunde.csv und tei/WZB.tei.xml und
schreibt pruefseite-560-abc.html neben die CSV: eine einzelne Datei nach dem
Format aus #443 (scripts/review/review_page.py, nur benutzt, nicht geaendert).

Drei Gruppen:
  A  ein passendes Lemma steht in lexicon.xml: umhaengen
  B  Wortreste aus Zeilenumbruch oder Getrenntschreibung: entannotieren
  C  echtes Wort ohne Lemma in lexicon.xml: Lexikonluecke

Zwei Schreibungen weichen von der CSV ab: fuer `hebreer` und `vorsaczes`
nennt die CSV kein Lemma, die Suche ueber alle orth von lexicon.xml am
12.11.2026 findet lemma_30323 Hebreaere und lemma_20808 vuersaz. Beide stehen
deshalb in A, mit dem Hinweis auf der Karte. Der Generator prueft beim Lauf,
dass jede genannte lemma_N in lexicon.xml steht und das genannte orth traegt,
und dass die Tokenzahl je Schreibung im TEI der CSV entspricht.

Aufruf aus dem Repo-Wurzelverzeichnis:
    python scripts/review/build-560-pruefseite.py
"""

import csv
import re
import subprocess
import sys
from collections import OrderedDict
from datetime import date
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_page import e, render  # noqa: E402

DIR = ROOT / 'ingest' / 'wzb' / '370-corresp'
QUELLE = DIR / 'abc-befunde.csv'
ZIEL = DIR / 'pruefseite-560-abc.html'
TEI_DATEI = ROOT / 'tei' / 'WZB.tei.xml'
ERWARTET_SCHREIBUNGEN = 41
ERWARTET_TOKENS = 247
TEI = '{http://www.tei-c.org/ns/1.0}'
XID = '{http://www.w3.org/XML/1998/namespace}id'

# Gruppe A: Schreibung -> (Kandidaten [(lemma, orth, pos)], Begruendung, Unsicherheit).
# Der erste Kandidat ist der Vorschlag. Begruendung leer: es gilt der Befund der CSV.
UMHAENGEN = {
    'schupen': ([('lemma_11597', 'schuope', 'NOM')], '',
                '`schuope` hat in der WZB noch keinen Beleg.'),
    'stakten': ([('lemma_5738', 'stecken', 'VRB')], '',
                'In der CSV nur als wahrscheinlich markiert. Die WZB führt `stecken` und `gestecket` schon auf diesem Lemma.'),
    'gepitunge': ([('lemma_45356', 'gebietunge', 'NOM')], '',
                  '`gebietunge` hat in der WZB noch keinen Beleg.'),
    'vbirdecken': ([('lemma_46787', 'überdecke', 'NOM')],
                   '', 'Der Singular `vbirdecke` steht in der WZB elfmal auf diesem Lemma.'),
    'henge': ([('lemma_2758', 'hengen', 'VRB')], '', ''),
    'gegossens': ([('lemma_2392', 'giezen', 'VRB')], '',
                  'Partizip in attributiver Stellung: VRB nach dem Lemma, am Vers auch als ADJ lesbar. '
                  'Die WZB führt `gegossen` sechsmal als VRB auf diesem Lemma.'),
    'vlossen': ([('lemma_33284', 'vlozze', 'NOM')], '',
                '`vlozze` hat in der WZB noch keinen Beleg.'),
    'levitici': ([('lemma_27649', 'Leviticus', 'NAM')], '',
                 'In der CSV nur als wahrscheinlich markiert. Für den Buchtitel *Numeri* fehlt dagegen ein Lemma (Gruppe C).'),
    'vorgebunge': ([('lemma_44185', 'vergebunge', 'NOM')], '', ''),
    'iacincteinen': ([('lemma_3088', 'jâchant', 'NOM'), ('lemma_3088', 'jâchant', 'ADJ')], '',
                     'In der CSV nur als wahrscheinlich markiert. Am Vers ein Adjektiv, `jâchant` führt in lexicon.xml aber nur NOM; '
                     'die WZB legt `iacincten` 18-mal als NOM darauf. ADJ wäre eine Wortart, die das Lemma heute nicht trägt.'),
    'vorvluchten': ([('lemma_7007', 'vervluochen', 'VRB')], '', ''),
    'silbereines': ([('lemma_5476', 'silber', 'ADJ'), ('lemma_5476', 'silber', 'NOM')], '',
                    'In der CSV nur als wahrscheinlich markiert. `silber` führt ADJ und NOM; in der WZB stehen bisher nur `silber` und `silbers`, alle als NOM.'),
    'gepowet': ([('lemma_917', 'bûwen', 'VRB')], '',
                'Dieselbe Zuordnung ist in #526 für `bow̆t`, `bow̆te` und `bow̆e` bestätigt (Prüfseite, Rückgabe vom 12.11.2026).'),
    'richticlichen': ([('lemma_67230', 'rihtec', 'ADV')], '',
                      'In der CSV nur als wahrscheinlich markiert. Ein eigenes Lemma *rihteclîche* gibt es nicht; das Adverb käme auf das Grundwort.'),
    'gemowerten': ([('lemma_4221', 'mûren', 'VRB')], '',
                   'Dieselbe Zuordnung ist in #526 für `gemaw̆erte` (WZB_233vb_15_4) bestätigt (Prüfseite, Rückgabe vom 12.11.2026).'),
    'poslich': ([('lemma_788', 'bœse', 'ADV'), ('lemma_788', 'bœse', 'ADJ')], '',
                'In der CSV nur als wahrscheinlich markiert. Ein eigenes Lemma *bœslîche* gibt es nicht; die WZB führt `bœse` 62-mal als ADJ.'),
    'mageschefte': ([('lemma_22720', 'mâcschaft', 'NOM')], '',
                    '`mageschaft` und `magschaft` stehen in der WZB 58-mal auf diesem Lemma.'),
    'uii': ([('lemma_13826', 'I', 'DIG')], '', ''),
    # Abweichend von der CSV, Lexikonsuche 12.11.2026:
    'hebreer': ([('lemma_30323', 'Hêbrêære', 'NAM'), ('lemma_18888', 'hêbrêisch', 'NOM')],
                '"den hebreer", "czwen hebreer": der Hebräer, Volksname. In lexicon.xml steht `lemma_30323` *Hêbrêære* (NAM) '
                'mit den Begriffen "Ethn. Einheit/Volk/Stamm/Namen" und "Hebräisch".',
                'Die CSV führt das Wort als Lexikonlücke; ihre Suche nach hebre, ebrê und ebræ hat den Eintrag nicht gefunden. '
                '`Hêbrêære` hat im ganzen Korpus noch keinen Beleg.'),
    'vorsaczes': ([('lemma_20808', 'vürsaz', 'NOM')],
                  '"mit broten des vorsaczes": die Schaubrote, wörtlich die Brote des Vorgesetzten. In lexicon.xml steht `lemma_20808` *vürsaz* (NOM).',
                  'Die CSV führt das Wort als Lexikonlücke. Das Lemma passt, seine Bedeutungen aber nicht: sie tragen "Absicht/Wollen", '
                  '"Vorbereitung", "Handel/Finanzen" und "Kommunikation/Sprache". Für die Schaubrote fehlt also eine Bedeutung, nicht das Lemma.'),
}

# Gruppe B: Wortreste. Der Befund der CSV traegt die Begruendung.
WORTRESTE = {
    'ber': 'Gemischt: `a ber` (aber) mit abgesetztem Anfangsbuchstaben und `ber` als Rest von *Eber*. Ein Beleg, der anders liegt, gehört in den Kommentar.',
    'be': 'Abgetrenntes Präfix (`be suchet`). Ob die beiden Teile zu einem Token verbunden werden, ist eine Frage der Tokenkorrektur (#235), nicht dieser Seite.',
    'nen': '', 'ner': '', 'dei': '', 'te': '', 'st': '',
}

# Gruppe C: Schreibung -> (Ansatz, Wortart, Zusatz zur Unsicherheit). Der Ansatz stammt aus der CSV.
LUECKEN = {
    'erstlinge': ('êrstelinc', 'NOM', ''),
    'humeral': ('humeral', 'NOM', ''),
    'numeri': ('Numeri', 'NAM', '*Leviticus* steht als NAM im Lexikon (`lemma_27649`, Gruppe A bei `levitici`).'),
    'keuchel': ('kiuchel', 'NOM', ''),
    'ostnischen': ('ôstenisch', 'ADJ', ''),
    'westnischen': ('westenisch', 'ADJ', ''),
    'nordnischen': ('nordenisch', 'ADJ', ''),
    'nichtenicht': ('nihtesniht', 'ADV', ''),
    'leuitischen': ('levîtisch', 'ADJ', 'Das Grundwort steht im Lexikon: `lemma_25104` *levîten* (NOM).'),
    'abscheidunge': ('abescheidunge', 'NOM', ''),
    'wanczen': ('wanze', 'NOM', ''),
    'sowerteig': ('sûrteic', 'NOM', 'In #526 ist `vngesow̆erteigtes` (WZB_84vb_4_3) als Lexikonlücke markiert; beide hängen am selben Wort.'),
    'pilgereimet': ('bilgerîmen', 'VRB', ''),
    'gewurmeltem': ('gewürmelt', 'ADJ', ''),
}

GRUPPEN = [
    dict(id='A', titel='A: Es gibt schon ein passendes Lemma',
         beschreibung='Für diese Wörter steht ein Lemma in <span class="mono">lexicon.xml</span>. '
                      'Die Frage ist, ob alle Belege einer Schreibung darauf umgehängt werden.'),
    dict(id='B', titel='B: Wortreste, kein eigenes Wort',
         beschreibung='Teile von Wörtern, die über einen Zeilenumbruch oder durch Getrenntschreibung abgetrennt sind, '
                      'etwa <span class="mono">dei | ner</span>. Vorschlag wie bei Frage 2: die Annotation fällt weg, der Text bleibt.'),
    dict(id='C', titel='C: Echte Wörter ohne Lemma im Lexikon',
         beschreibung='Für diese Wörter fehlt ein Lemma. Das ist dieselbe Grundsatzfrage wie bei den Lexikonlücken in '
                      '#526 Punkt 3, die bei Katharina liegt. Hier geht es darum, ob das Wort als Lücke bestätigt wird '
                      'oder vorerst ohne Lemma bleibt.'),
]

OPT_UNEINHEITLICH = 'Uneinheitlich: Ausnahmen im Kommentar (mit xml:id)'
OPT_UNANNOTIERT = 'Bewusst unannotiert lassen (abc entfernen)'


def markup(text):
    """`Beleg` und *kursiv*, alles andere ist Text."""
    roh = e(text)
    teile = roh.split('`')
    roh = ''.join(t if i % 2 == 0 else '<span class="mono">%s</span>' % t for i, t in enumerate(teile))
    teile = roh.split('*')
    return ''.join(t if i % 2 == 0 else '<i>%s</i>' % t for i, t in enumerate(teile))


def text_von(el):
    return ''.join(el.itertext()).strip()


def zeilen_schluessel(xml_id):
    # Suffix b: zweite Haelfte eines geteilten Tokens (#235), 17 Faelle im TEI
    m = re.match(r'WZB_(\w+?)_(\d+)_(\d+)b?$', xml_id or '')
    return (m.group(1), int(m.group(2))) if m else None


def fundstelle(schluessel):
    return 'Blatt %s, Zeile %d' % schluessel


def lies_korpus():
    """Zeilen in Dokumentfolge und die lemma_2-Tokens je Schreibung.

    Die Zeile ergibt sich aus der xml:id (WZB_<Blatt+Spalte>_<Zeile>_<Nr>),
    die w und pc gleichermassen tragen.
    """
    doc = etree.parse(str(TEI_DATEI))
    zeilen = OrderedDict()
    abc = {}
    for el in doc.iter(TEI + 'w', TEI + 'pc'):
        s = zeilen_schluessel(el.get(XID))
        if s is None:
            sys.exit('Token ohne lesbare xml:id: %r' % el.get(XID))
        zeilen.setdefault(s, []).append(el)
        if el.tag == TEI + 'w' and re.search(r'#lemma_2$', el.get('lemmaRef') or ''):
            abc.setdefault(text_von(el).lower(), []).append(el)
    return zeilen, abc


def zeilentext(toks):
    return ' '.join(text_von(t) for t in toks)


def beleg(el, zeilen, reihenfolge, index):
    s = zeilen_schluessel(el.get(XID))
    i = index[s]
    toks = zeilen[s]
    pos = toks.index(el)

    def nachbar(j):
        if 0 <= j < len(reihenfolge):
            n = reihenfolge[j]
            marke = str(n[1]) if n[0] == s[0] else '%s %d' % n
            return [dict(n=marke, text=zeilentext(zeilen[n]))]
        return []

    return dict(werk='Wenzelsbibel (WZB)', fundstelle=fundstelle(s), xml_id=el.get(XID), wortart='',
                zeilen_davor=nachbar(i - 1), zeile_n=str(s[1]),
                treffer_davor=zeilentext(toks[:pos]), treffer=text_von(el),
                treffer_danach=zeilentext(toks[pos + 1:]), zeilen_danach=nachbar(i + 1))


def pruefe_lemmata():
    lex = etree.parse(str(ROOT / 'authority-files' / 'lexicon.xml'))
    orth = {el.get(XID): (el.findtext(f'{TEI}form/{TEI}orth') or '').strip() for el in lex.iter(TEI + 'entry')}
    for schreibung, (kand, _, _) in UMHAENGEN.items():
        for lid, o, _ in kand:
            if orth.get(lid) != o:
                sys.exit('%s: %s traegt in lexicon.xml %r, erwartet %r' % (schreibung, lid, orth.get(lid), o))
    for lid, o in (('lemma_25104', 'levîten'), ('lemma_27649', 'Leviticus')):
        if orth.get(lid) != o:
            sys.exit('%s traegt in lexicon.xml %r, erwartet %r' % (lid, orth.get(lid), o))


def korpus_commit():
    r = subprocess.run(['git', '-C', str(ROOT), 'log', '-1', '--format=%h %ad', '--date=short', '--', 'tei/WZB.tei.xml'],
                       capture_output=True, text=True, check=True)
    return r.stdout.strip()


def befund_ohne_marke(befund):
    m = re.match(r'^\[(klar|wahrscheinlich)\]\s*(.*)$', befund, re.S)
    if not m:
        sys.exit('Befund ohne [klar]/[wahrscheinlich]: %r' % befund[:60])
    return m.group(1), m.group(2)


def bau_fall(z, gruppe, belege):
    schreibung, n = z['schreibung'], len(belege)
    marke, befund = befund_ohne_marke(z['befund'])
    merkmale = [('Belege', str(n)), ('heute', 'lemma_2 abc'), ('Befund der CSV', marke)]

    if gruppe == 'A':
        kand, begruendung, unsicher = UMHAENGEN[schreibung]
        lid, o, p = kand[0]
        if z['vorgeschlagenes_ziel'] and z['vorgeschlagenes_ziel'] != lid:
            sys.exit('%s: CSV schlaegt %s vor, UMHAENGEN %s' % (schreibung, z['vorgeschlagenes_ziel'], lid))
        if not z['vorgeschlagenes_ziel']:
            merkmale.append(('Lemma', 'neu gefunden am 12.11.2026'))
        frage = 'Gehören alle %d Belege von %s zu %s %s?' % (n, schreibung, lid, o)
        vorschlag = 'KI-Vorschlag: alle %d Belege auf %s %s, Wortart %s.' % (n, lid, o, p)
        optionen = ['Alle Belege: %s %s (%s)' % k for k in kand]
        optionen += ['Lexikonlücke: eigenes Lemma nötig', OPT_UNANNOTIERT, OPT_UNEINHEITLICH]
        begruendung = begruendung or befund
    elif gruppe == 'B':
        frage = 'Sind die %d Belege von %s Wortreste, deren Annotation abc wegfallen soll?' % (n, schreibung)
        vorschlag = 'KI-Vorschlag: abc entfernen, das Token bleibt ohne Lemma im Text.'
        optionen = ['Entannotieren: abc entfernen, Text bleibt',
                    'Tokenkorrektur: mit dem Nachbarteil verbinden (#235)',
                    'Doch ein eigenes Wort (in die freie Antwort)', OPT_UNEINHEITLICH]
        begruendung = befund
        unsicher = WORTRESTE[schreibung]
    else:
        ansatz, p, zusatz = LUECKEN[schreibung]
        frage = 'Ist %s eine Lexikonlücke, oder bleiben die %d Belege vorerst ohne Lemma?' % (schreibung, n)
        vorschlag = 'KI-Vorschlag: Lexikonlücke, neues Lemma nötig (Ansatz %s, Wortart %s).' % (ansatz, p)
        optionen = ['Lexikonlücke: neues Lemma %s (%s)' % (ansatz, p),
                    'Lexikonlücke, aber anderer Ansatz (in die freie Antwort)',
                    'Vorerst unannotiert lassen (abc entfernen)',
                    'Doch ein vorhandenes Lemma (in die freie Antwort)', OPT_UNEINHEITLICH]
        begruendung = befund
        unsicher = ('Der Ansatz *%s* stammt aus der CSV und ist nicht in einem Wörterbuch nachgeschlagen. %s' % (ansatz, zusatz)).strip()

    return dict(
        id='abc-' + schreibung,
        gruppe=gruppe,
        kopf='%s  ·  %d %s' % (schreibung, n, 'Beleg' if n == 1 else 'Belege'),
        frage=frage,
        merkmale=merkmale,
        belege=belege,
        beleg_hinweis=markup('Alle Belege der Schreibung, je mit Vor- und Folgezeile aus `tei/WZB.tei.xml`. '
                             'Eine Ausnahme bitte mit ihrer xml:id in den Kommentar.'),
        vorschlag=dict(text=markup(vorschlag), begruendung=markup(begruendung),
                       unsicherheit=markup(unsicher) if unsicher else ''),
        optionen=optionen,
        sichtbar=len(optionen),
    )


def main():
    with open(QUELLE, encoding='utf-8-sig', newline='') as f:
        csvzeilen = list(csv.DictReader(f, delimiter=';'))
    if len(csvzeilen) != ERWARTET_SCHREIBUNGEN:
        sys.exit('erwartet %d Schreibungen, gefunden %d' % (ERWARTET_SCHREIBUNGEN, len(csvzeilen)))
    alle = {z['schreibung'] for z in csvzeilen}
    gruppe_von = {}
    for name, menge in (('A', UMHAENGEN), ('B', WORTRESTE), ('C', LUECKEN)):
        for s in menge:
            if s in gruppe_von:
                sys.exit('%s steht in zwei Gruppen' % s)
            gruppe_von[s] = name
    if set(gruppe_von) != alle:
        sys.exit('Gruppen passen nicht zur CSV: fehlt %s, zuviel %s'
                 % (sorted(alle - set(gruppe_von)), sorted(set(gruppe_von) - alle)))
    for z in csvzeilen:
        if z['vorgeschlagenes_ziel'] and gruppe_von[z['schreibung']] != 'A':
            sys.exit('%s hat ein Ziel in der CSV, steht aber nicht in A' % z['schreibung'])
    pruefe_lemmata()

    zeilen, abc = lies_korpus()
    reihenfolge = list(zeilen)
    index = {s: i for i, s in enumerate(reihenfolge)}

    faelle = []
    for gruppe in ('A', 'B', 'C'):
        drin = [z for z in csvzeilen if gruppe_von[z['schreibung']] == gruppe]
        for z in sorted(drin, key=lambda z: (-int(z['tokens']), z['schreibung'])):
            toks = abc.get(z['schreibung'], [])
            if len(toks) != int(z['tokens']):
                sys.exit('%s: CSV %s Tokens, TEI %d' % (z['schreibung'], z['tokens'], len(toks)))
            faelle.append(bau_fall(z, gruppe, [beleg(t, zeilen, reihenfolge, index) for t in toks]))
    tokens = sum(len(f['belege']) for f in faelle)
    if tokens != ERWARTET_TOKENS:
        sys.exit('erwartet %d Tokens, gefunden %d' % (ERWARTET_TOKENS, tokens))
    zahl = {g: sum(1 for f in faelle if f['gruppe'] == g) for g in 'ABC'}

    spec = dict(
        kennung='mhdbdb-560-wzb-abc-woerter',
        titel='WZB: ganze Wörter am Lemma abc',
        untertitel='%d Schreibungen mit %d Belegen der Wenzelsbibel, die heute am Sammellemma <span class="mono">lemma_2</span> '
                   '„abc“ hängen. Entschieden wird je Schreibung für alle ihre Belege.' % (len(faelle), tokens),
        vorgang='#560',
        anleitung=[
            'Diese Datei ist vollständig. Sie brauchen kein Internet, keine Anmeldung und keine Installation.',
            'Tragen Sie oben Ihren Namen ein. Antworten und Kommentare werden sofort im Browser gespeichert; '
            'die Anzeige oben rechts sagt, ob das gelingt. Zum Zurückschicken drücken Sie <b>JSON</b>. '
            'Mit <b>Import</b> lesen Sie einen früheren Export wieder ein.',
            '<b>Eine Karte gilt für alle Belege einer Schreibung.</b> Unter jeder Karte stehen alle Belege mit der Zeile '
            'davor und danach. Liegt ein Beleg anders als die übrigen, wählen Sie <b>Uneinheitlich</b> und nennen '
            'die Ausnahme mit ihrer xml:id im Kommentar.',
            'Jeder Fall hat drei Stände: <b>unbearbeitet</b>, <b>entschieden</b> und <b>geprüft, bleibt offen</b>. '
            'Das Kommentarfeld hängt an keiner Antwort.',
            '<b>Der KI-Vorschlag ist keine Entscheidung.</b> Unter jedem Fall steht, woraus er folgt und was '
            'daran unsicher ist. Es gibt keine Schaltfläche, die viele Fälle auf einmal setzt.',
            'Gruppe A hat %d Fälle, B %d und C %d. Zwei Fälle in A, <span class="mono">hebreer</span> und '
            '<span class="mono">vorsaczes</span>, führt die CSV noch als Lexikonlücke; das Lemma hat erst die '
            'Suche vom 12.11.2026 gefunden.' % (zahl['A'], zahl['B'], zahl['C']),
        ],
        datenstand=[
            ('Korpus', 'tei/WZB.tei.xml, letzte Änderung %s' % korpus_commit()),
            ('Fallliste', 'ingest/wzb/370-corresp/abc-befunde.csv (%d Schreibungen, %d Tokens, Zahl je Schreibung gegen das TEI geprüft)'
             % (len(faelle), tokens)),
            ('Lemmata', 'gegen authority-files/lexicon.xml geprüft, Suche über alle orth am 12.11.2026'),
            ('Seite erzeugt mit', 'scripts/review/build-560-pruefseite.py am %s' % date.today().strftime('%d.%m.%Y')),
        ],
        gruppen=GRUPPEN,
        faelle=faelle,
    )
    seite = render(spec)
    sichtbar = re.sub(r'<script\b.*?</script>', '', seite, flags=re.S | re.I)
    if '`' in sichtbar or '—' in seite:
        sys.exit('Rückwärtsstrich oder Em-Dash in der Seite')
    ZIEL.write_text(seite, encoding='utf-8')
    print('geschrieben: %s (%d Karten, A %d, B %d, C %d, %d Belege, %.0f KB)'
          % (ZIEL.relative_to(ROOT), len(faelle), zahl['A'], zahl['B'], zahl['C'], tokens,
             len(seite.encode('utf-8')) / 1024.0))


if __name__ == '__main__':
    main()
