#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#526 Punkt 4: die HTML-Pruefseite fuer die 19 WZB-Breve-Tokens auf w/n, die
#536 nicht annotiert hat (action REVIEW in diff-liste.csv).

Liest ingest/pos-disambig/526-breve-wn/diff-liste.csv und schreibt
pruefseite-526.html daneben: eine einzelne Datei nach dem Format aus #443
(scripts/review/review_page.py, nur benutzt, nicht geaendert).

Die Kandidaten je Fall stehen unten in KANDIDATEN. Sie sind am Vers gelesen
und gegen lexicon.xml nachgeschlagen (08.10.2026); der Generator prueft beim
Lauf, dass jede genannte lemma_N in lexicon.xml steht und das genannte orth
traegt. Sie sind KI-Vorschlaege, keine Entscheidungen.

Aufruf aus dem Repo-Wurzelverzeichnis:
    python scripts/review/build-526-pruefseite.py
"""

import csv
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_page import e, render  # noqa: E402

DIR = ROOT / 'ingest' / 'pos-disambig' / '526-breve-wn'
QUELLE = DIR / 'diff-liste.csv'
ZIEL = DIR / 'pruefseite-526.html'
ERWARTET = 19
TEI = '{http://www.tei-c.org/ns/1.0}'
XID = '{http://www.w3.org/XML/1998/namespace}id'

# xml:id -> (Kandidaten [(lemma, orth, pos)], Begruendung, Unsicherheit)
# Leere Kandidatenliste: in lexicon.xml steht kein passendes Lemma.
KANDIDATEN = {
    'WZB_10vb_3_3': ([('lemma_5827', 'ströuwen', 'VRB'), ('lemma_15396', 'zerströuwen', 'VRB')],
                     'Am Vers „von danne zu strew̆te sie vnser herre“: ein Verb im Präteritum, „zerstreute“.',
                     'Ob „zu strew̆te“ als *zerströuwen* in zwei Wörtern zu lesen ist, entscheidet die Worttrennung, nicht das Lemma von `strew̆te` allein. '
                     '*zerströuwen* hat in der WZB keinen Beleg; #536 hat „czu strew̆et“ und „zu strew̆en“ auf *ströuwen* gelegt.'),
    'WZB_21ra_36_4': ([('lemma_3159', 'juncvrouwe', 'NOM')],
                      '„ein schŏne iuncvrow̆“: Substantiv, die Jungfrau.', ''),
    'WZB_76vb_35_2': ([('lemma_3159', 'juncvrouwe', 'NOM')],
                      '„ein iuncvrow̆ enpfurt die noch nicht ist vortrew̆et“: Substantiv, die Jungfrau.', ''),
    'WZB_21va_19_0': ([('lemma_2816', 'höuwe', 'NOM')],
                      '„futers vnd hew̆es ist zu vns“: Futter und Heu. `höuwe` trägt in lexicon.xml Konzepte wie Ernte und Wiesenwirtschaft; '
                      'die WZB legt `heu` (WZB_21vb_14_2) und `hŏue` (WZB_126va_6_3) schon darauf.',
                      'Ähnlich geformt, aber am Vers unpassend: `lemma_61268` hou (der Hieb) und `lemma_9644` houwe (die Haue, in der WZB zweimal als `howe`).'),
    'WZB_233vb_15_4': ([('lemma_4221', 'mûren', 'VRB')],
                       '„gar wol gemaw̆erte stete“: Partizip zu *mûren*, ummauerte Städte.',
                       'Partizip in attributiver Stellung: VRB nach dem Lemma, am Vers auch als ADJ lesbar.'),
    'WZB_34va_9_6': ([('lemma_917', 'bûwen', 'VRB')],
                     '„die ist in ewerr gewalt bow̆t sie vnd koufslagit“: bebauen, bewirtschaften.', ''),
    'WZB_54ra_18_1': ([('lemma_917', 'bûwen', 'VRB')],
                      '„dorumbe bow̆te her in heuser“: er baute ihnen Häuser.', ''),
    'WZB_75rb_7_1': ([('lemma_917', 'bûwen', 'VRB')],
                     '„nicht bow̆e den mit gehowen steinen“: bauen.', ''),
    'WZB_78rb_5_6': ([('lemma_917', 'bûwen', 'VRB')],
                     '„Nicht bow̆o ir werk“: nach dem Vers ein Verb des Tuns oder Bauens.',
                     'Die Endung -o ist für die WZB ungewöhnlich; ob hier *bûwen* gemeint ist oder ein Schreibfehler für ein anderes Verb, sagt der Vers allein nicht.'),
    'WZB_42vb_3_7': ([('lemma_1739', 'eteswenne', 'ADV')],
                     '„Muge wir etwenn̆ vinden einen semelichen man“: Adverb, etwa, wohl.',
                     '`eteswenne` führt in lexicon.xml nur das Konzept Zeit (irgendwann); am Vers ist eher „etwa, vielleicht“ gemeint.'),
    'WZB_46vb_33_2': ([('lemma_4134', 'minner', 'ADV'), ('lemma_4134', 'minner', 'ADJ'), ('lemma_4128', 'min', 'ADJ')],
                      '„vnser min̆ster bruder“: Superlativ, der jüngste Bruder. Die WZB hat den Superlativ schon neunmal annotiert '
                      '(`minsten`, `minneste`, `minnesten`), alle auf `lemma_4134` *minner* mit Wortart ADV, auch attributiv wie „die minneste tochter“ (WZB_28rb_17_3).',
                      'Die Form `minster` selbst steht in der WZB nur unannotiert (WZB_45va_34_6, WZB_46vb_22_2), daher „nirgends“ oben. '
                      'Ob ADV auch für den attributiven Gebrauch richtig ist, betrifft alle neun Belege; die Entscheidung hier trägt dazu `minster` (2), `minnest` und `minnester` mit.'),
    'WZB_47ra_22_3': ([('lemma_6215', 'triuwe', 'NOM')],
                      '„ouf mein trew̆ hab genomen“: Substantiv, die Treue, das gegebene Wort.', ''),
    'WZB_61vb_18_5': ([('lemma_5827', 'ströuwen', 'VRB')],
                      '„vnd strew̆ die in den himel“: Imperativ, streue.', ''),
    'WZB_65ra_9_3': ([('lemma_15396', 'zerströuwen', 'VRB'), ('lemma_5827', 'ströuwen', 'VRB')],
                     '„euch wirt kein pflage nicht zu strew̆ende“: flektierter Infinitiv. Am Vers ist eher „verderben“ gemeint als „zerstreuen“; '
                     'diesen Sinn trägt *zerströuwen* in seiner zweiten Bedeutung (`lemma_15396_sense_56021`, unter anderem mit den Begriffen „Natürlicher Tod/Gewaltsamer Tod“, „Gewalt/Strafe/Vergebung“ und „Vergehen“), *ströuwen* nicht.',
                     'Das setzt voraus, dass „zu strew̆ende“ als *zerströuwen* in zwei Wörtern zu lesen ist, wie bei WZB_10vb_3_3. '
                     'Die zwei vergleichbaren Stellen hat #536 auf *ströuwen* gelegt.'),
    'WZB_67ra_25_6': ([('lemma_537', 'beriuwen', 'VRB')],
                      '„das sies leichte icht berew̆te“: dass es sie nicht etwa reue.', ''),
    'WZB_72va_21_2': ([('lemma_7256', 'vröuwen', 'VRB')],
                      '„der vrew̆te sich“: sich freuen.', ''),
    'WZB_76vb_36_4': ([('lemma_6997', 'vertrûwen', 'VRB')],
                      '„die noch nicht ist vortrew̆et“: verlobt. `vertrûwen` trägt in lexicon.xml das Konzept Ehe.', ''),
    'WZB_84vb_4_3': ([],
                     '„ein vngesow̆erteigtes crustilbrot“: ungesäuert, ohne Sauerteig.',
                     'In lexicon.xml steht kein Lemma für *ungesûrteiget* oder eine nahe Form. Das ist eine Lexikonlücke und gehört zur Grundsatzfrage aus Punkt 3 von #526.'),
    'WZB_90ra_20_7': ([('lemma_5827', 'ströuwen', 'VRB'), ('lemma_15396', 'zerströuwen', 'VRB')],
                      '„das ich dich icht zu strew̆e an dem wege“: ein Verb. Die einzige annotierte Vergleichsform `strewe` ist ströuwe NOM (WZB_150vb_13_3).',
                      'Vorschlag wie im Lauf vom 07.10. (#536) bei „czu strew̆et“ (WZB_206ra_7_0). Zur Worttrennung wie bei WZB_10vb_3_3; '
                      'unannotiert steht dazu `czustrewe` in einem Wort (WZB_183vb_21_7).'),
}


def markup(text):
    """`Beleg` und *kursiv*, alles andere ist Text."""
    roh = e(text)
    teile = roh.split('`')
    roh = ''.join(t if i % 2 == 0 else '<span class="mono">%s</span>' % t for i, t in enumerate(teile))
    teile = roh.split('*')
    return ''.join(t if i % 2 == 0 else '<i>%s</i>' % t for i, t in enumerate(teile))


def fundstelle(xml_id):
    m = re.match(r'WZB_(\w+?)_(\d+)_(\d+)$', xml_id)
    if not m:
        raise ValueError('unerwartete xml:id ' + xml_id)
    # keine Wortnummer: das Suffix der xml:id zaehlt w und pc ab 0
    return 'Blatt %s, Zeile %s' % (m.group(1), m.group(2))


def pruefe_kandidaten():
    lex = etree.parse(str(ROOT / 'authority-files' / 'lexicon.xml'))
    orth = {el.get(XID): (el.findtext(f'{TEI}form/{TEI}orth') or '').strip() for el in lex.iter(TEI + 'entry')}
    for xid, (kand, _, _) in KANDIDATEN.items():
        for lid, o, _ in kand:
            if orth.get(lid) != o:
                sys.exit('%s: %s traegt in lexicon.xml %r, erwartet %r' % (xid, lid, orth.get(lid), o))


def korpus_commit():
    r = subprocess.run(['git', '-C', str(ROOT), 'log', '-1', '--format=%h %ad', '--date=short', '--', 'tei/WZB.tei.xml'],
                       capture_output=True, text=True, check=True)
    return r.stdout.strip()


def bau_fall(z):
    xid, form = z['xml_id'], z['form']
    kand, begruendung, unsicher = KANDIDATEN[xid]
    m = re.match(r'^(.*)\[\[(.*?)\]\](.*)$', z['umfeld'])
    if not m:
        sys.exit('%s: Umfeld ohne [[...]]-Markierung' % xid)
    optionen = ['%s %s (%s)' % (lid, o, p) for lid, o, p in kand]
    optionen += ['Lexikonlücke: hier fehlt ein Lemma (zu Punkt 3)', 'Bewusst unannotiert lassen']
    if kand:
        lid, o, p = kand[0]
        text = 'KI-Vorschlag: %s %s, Wortart %s.' % (lid, o, p)
    else:
        text = 'KI-Vorschlag: kein passendes Lemma in lexicon.xml.'
    merkmale = [('Schreibung', form),
                ('Form ohne Breve', z['vergleichsform'] or '-'),
                ('In der WZB annotiert', z['vergleich_belege'] or 'nirgends')]
    return dict(
        id=xid,
        gruppe='offen',
        kopf='%s  ·  %s' % (form, fundstelle(xid)),
        frage='Welches Lemma und welche Wortart gehören zu %s an dieser Stelle?' % form,
        merkmale=merkmale,
        belege=[dict(werk='Wenzelsbibel (WZB)', fundstelle=fundstelle(xid), xml_id=xid, wortart='',
                     zeilen_davor=[], zeile_n='',
                     treffer_davor=m.group(1).strip(), treffer=m.group(2), treffer_danach=m.group(3).strip())],
        beleg_hinweis=markup('Umfeld aus `diff-liste.csv` des Laufs vom 07.10.2026 (#536).'),
        vorschlag=dict(text=markup(text), begruendung=markup(begruendung),
                       unsicherheit=markup(unsicher) if unsicher else ''),
        optionen=optionen,
        sichtbar=len(optionen),
    )


def main():
    with open(QUELLE, encoding='utf-8-sig', newline='') as f:
        zeilen = [z for z in csv.DictReader(f, delimiter=';') if z['action'] == 'REVIEW']
    if len(zeilen) != ERWARTET:
        sys.exit('erwartet %d REVIEW-Zeilen, gefunden %d' % (ERWARTET, len(zeilen)))
    ids = {z['xml_id'] for z in zeilen}
    if ids != set(KANDIDATEN):
        sys.exit('KANDIDATEN passt nicht zur Liste: fehlt %s, zuviel %s'
                 % (sorted(ids - set(KANDIDATEN)), sorted(set(KANDIDATEN) - ids)))
    pruefe_kandidaten()
    faelle = [bau_fall(z) for z in sorted(zeilen, key=lambda z: z['xml_id'])]
    ohne = sum(1 for z in zeilen if not KANDIDATEN[z['xml_id']][0])

    spec = dict(
        kennung='mhdbdb-526-wzb-breve-wn',
        titel='WZB: Breve-Schreibungen ohne Vergleichsform',
        untertitel='%d Wörter der Wenzelsbibel mit Breve auf w oder n, die kein Lauf mechanisch annotieren konnte.' % len(faelle),
        vorgang='#526',
        anleitung=[
            'Diese Datei ist vollständig. Sie brauchen kein Internet, keine Anmeldung und keine Installation.',
            'Tragen Sie oben Ihren Namen ein. Antworten und Kommentare werden sofort im Browser gespeichert; '
            'die Anzeige oben rechts sagt, ob das gelingt. Zum Zurückschicken drücken Sie <b>JSON</b>. '
            'Mit <b>Import</b> lesen Sie einen früheren Export wieder ein.',
            'Jeder Fall hat drei Stände: <b>unbearbeitet</b>, <b>entschieden</b> und <b>geprüft, bleibt offen</b>. '
            'Das Kommentarfeld hängt an keiner Antwort.',
            '<b>Der KI-Vorschlag ist keine Entscheidung.</b> Unter jedem Fall steht, woraus er folgt und was '
            'daran unsicher ist. Es gibt keine Schaltfläche, die viele Fälle auf einmal setzt.',
            'Die Antworten nennen die Lemmata, die in <span class="mono">lexicon.xml</span> in Frage kommen. '
            'Passt keines, wählen Sie <b>Lexikonlücke</b> oder schreiben die richtige Zuordnung in die freie Antwort. '
            'Bei %d Fall steht gar kein Kandidat: dort fehlt das Lemma im Wörterbuch.' % ohne,
        ],
        datenstand=[
            ('Korpus', 'tei/WZB.tei.xml, letzte Änderung %s' % korpus_commit()),
            ('Fallliste', 'ingest/pos-disambig/526-breve-wn/diff-liste.csv, Zeilen mit action REVIEW (%d)' % len(faelle)),
            ('Kandidaten', 'am Vers gelesen und gegen authority-files/lexicon.xml geprüft, 08.10.2026'),
            ('Seite erzeugt mit', 'scripts/review/build-526-pruefseite.py am %s' % date.today().strftime('%d.%m.%Y')),
        ],
        gruppen=[dict(id='offen', titel='Zu entscheiden',
                      beschreibung='Für diese Wörter ist die Form ohne Breve in der Wenzelsbibel nirgends annotiert, '
                                   'oder die einzige annotierte Vergleichsform passt am Vers nicht.')],
        faelle=faelle,
    )
    seite = render(spec)
    sichtbar = re.sub(r'<script\b.*?</script>', '', seite, flags=re.S | re.I)
    if '`' in sichtbar or '—' in seite:
        sys.exit('Rückwärtsstrich oder Em-Dash in der Seite')
    ZIEL.write_text(seite, encoding='utf-8')
    print('geschrieben: %s (%d Karten, %d ohne Kandidat, %.0f KB)'
          % (ZIEL.relative_to(ROOT), len(faelle), ohne, len(seite.encode('utf-8')) / 1024.0))


if __name__ == '__main__':
    main()
