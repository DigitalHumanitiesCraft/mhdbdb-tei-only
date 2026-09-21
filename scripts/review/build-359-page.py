#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#359: die Pruefseite fuer Boreks Verdachts- und Klassifikationsfaelle.

Setzt zwei Dateien zusammen:

  ingest/review/359-borek/evidence.json    gemessen (collect-359-evidence.py)
  ingest/review/359-borek/vorschlaege.json von Hand, nach dem Lesen der Belege

und erzeugt daraus mit `review_page.py` (dem Format aus #443) eine einzelne
HTML-Datei.

## Warum die Bewertungen eine eigene Datei sind und nicht im Code stehen

Weil sie Urteile sind und keine Programmlogik. Wer eines aendert, aendert eine
Datenzeile und laesst das Skript neu laufen; niemand muss dafuer Python lesen.
Und weil jedes Urteil seine Belege nennt, laesst sich jede Karte der Seite auf
die Stelle zurueckfuehren, aus der sie stammt.

## Der Abgleich ist streng

Ein Fall ohne Bewertung und eine Bewertung ohne Fall sind beide ein harter
Fehler. Ein `tragender_beleg`, den es in den gemessenen Belegen nicht gibt, ist
es auch: das ist die Stelle, an der eine Begruendung sonst eine Fundstelle
nennt, die niemand mehr findet.

Usage:
    python scripts/review/build-359-page.py
    python scripts/review/build-359-page.py --pruefen   # nur abgleichen, nichts schreiben
"""
import argparse
import io
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
from review_page import render, e  # noqa: E402

MATERIAL = REPO / 'ingest' / 'review' / '359-borek'
EVIDENCE = MATERIAL / 'evidence.json'
VORSCHLAEGE = MATERIAL / 'vorschlaege.json'
ZIEL = MATERIAL / '359-pruefseite.html'

# Wie viele Belege je Fall in die Seite kommen. Die GEZAEHLTE Menge steht
# daneben, sonst liest sich eine Auswahl als Vollstaendigkeit.
ANZEIGE_CAP = 8

# Die Seite ist nach dem BEFUND gruppiert, nicht nach der Klasse des
# Abgleichsberichts. Der Grund steht im Vorabpanel: die Haelfte der Faelle ist
# gar keine Frage an KZW, und wer das erst bei Karte 31 merkt, hat bis dahin
# die falsche Frage beantwortet. Die erledigten Gruppen stehen deshalb vorn,
# und die Sprungliste fuehrt direkt zu denen, die eine Entscheidung brauchen.
GRUPPEN = [
    dict(id='aufloesungsartefakt',
         titel='Erledigt: die Form hat ein anderes Wort getroffen',
         entscheidung=False,
         beschreibung=(
             'Boreks Listen enthalten gebeugte Formen (<span class="mono">lenden</span>, '
             '<span class="mono">brüsten</span>, <span class="mono">oren</span>). Der Abgleich '
             'vergleicht sie mit unseren Lemmaansetzungen. Wo eine fremde Ansetzung zufällig so '
             'aussieht wie eine gebeugte Form, trifft die Suche das falsche Wort: '
             '<span class="mono">oren</span> trifft dann nicht das Ohr, sondern das Fabelvolk der '
             '<span class="mono">Ôren</span> im Herzog Ernst. Der Homographenzähler des Berichts '
             'sieht davon nichts, weil die beiden Wörter verschiedene normalisierte Formen haben. '
             '<b>Diese Fälle brauchen keine Entscheidung</b>, sie sind hier, damit nachvollziehbar '
             'ist, warum sie im Bericht standen.')),
    dict(id='annotation_korrekt',
         titel='Erledigt: die Annotation im Korpus ist richtig',
         entscheidung=False,
         beschreibung=(
             'Hier ist eine Schreibung über das Varianten-Wörterbuch auf ein Lemma gelaufen, das '
             'inhaltlich nicht zu Boreks Liste passt, und die Belegstelle zeigt: die Annotation '
             'stimmt, Boreks Form klingt nur zufällig gleich. <span class="mono">perd</span> ist '
             'das Gebaren und nicht das Pferd, <span class="mono">trabe</span> ein Flussname und '
             'nicht der Trab. <b>Auch diese Fälle brauchen keine Entscheidung</b>, aber jede Karte '
             'zeigt die Stelle, an der sich das nachsehen lässt.')),
    dict(id='annotation_falsch',
         titel='Zu entscheiden: Fehlannotation im Korpus',
         entscheidung=True,
         beschreibung=(
             'Hier hat Borek recht: die Belegstelle meint etwas anderes als das annotierte Lemma. '
             'Jede Karte nennt die Tokens einzeln, weil bei allen dreien ein Teil der Belege '
             'richtig annotiert ist und nur ein Teil falsch.')),
    dict(id='konzept_fehlt',
         titel='Zu entscheiden: dem Lemma fehlt ein Konzept',
         entscheidung=True,
         beschreibung=(
             'Lemma und Annotation sind richtig, aber die Belege zeigen einen Gebrauch, den die '
             'Konzepte des Lemmas nicht abdecken. Hier stehen die Maschinenvorschläge, jeder mit '
             'den Stellen, aus denen er folgt, und mit dem, was daran unsicher bleibt.')),
    dict(id='kein_korpusbeleg',
         titel='Zu entscheiden: Lemma ohne einen einzigen Korpusbeleg',
         entscheidung=True,
         beschreibung=(
             'Diese Lemmata stehen im Lexikon und tragen im Korpus kein einziges Wort. Der Abgleich '
             'hat sie über die exakte Stufe gefunden, und die prüft gegen den Lexikonbestand, nicht '
             'gegen den Korpusgebrauch. <b>Es gibt hier bewusst keinen Vorschlag</b>: ein Vorschlag '
             'müsste aus Belegen kommen, und es gibt keine. Die Frage an Sie ist grundsätzlich.')),
    dict(id='unsicher',
         titel='Zu entscheiden: nach dem Lesen der Belege offen',
         entscheidung=True,
         beschreibung=(
             'Bei diesen Fällen hat das Lesen keine Antwort ergeben, oder die Antwort reicht über '
             '#359 hinaus. Auch hier steht bewusst kein Vorschlag. Was beim Lesen sichtbar wurde, '
             'steht trotzdem auf der Karte, damit Sie nicht von vorn anfangen müssen.')),
]

# Antwortoptionen je Bewertung. Alans erster Punkt: die Auswahl passt zum Fall.
# Die freie Antwort haengt das Format selbst an jede Karte.
OPTIONEN = {
    'aufloesungsartefakt': [
        'Stimmt, hier ist nichts zu tun',
        'Doch ein Fall, bitte genauer ansehen',
        'Das getroffene Lemma selbst ist falsch klassifiziert',
    ],
    'annotation_korrekt': [
        'Annotation ist richtig, kein Eingriff',
        'Annotation ist doch falsch',
        'Unklar, ich sehe mir die Handschrift an',
    ],
    'annotation_falsch': [
        'Fehlannotation bestätigt, Tokens umhängen',
        'Annotation ist richtig, kein Eingriff',
        'Teils, ich nenne im Kommentar welche',
        'Unklar, ich sehe mir die Stelle an',
    ],
    'konzept_fehlt': [
        'Vorschlag übernehmen',
        'Anderes Konzept vergeben (im Kommentar)',
        'Kein Konzept vergeben',
        'Nur an einem einzelnen Sense, nicht am Lemma',
    ],
    'kein_korpusbeleg': [
        'Ohne Beleg nicht klassifizieren',
        'Trotzdem klassifizieren (Konzept im Kommentar)',
        'Lemma gehört überprüft',
    ],
    'unsicher': [
        'Ich entscheide es so (im Kommentar)',
        'Bleibt offen, eigener Vorgang',
        'Kein Handlungsbedarf',
    ],
}

# Wie die Bewertung als Merkmal auf der Karte erscheint.
BEWERTUNG_LABEL = {
    'aufloesungsartefakt': 'Form hat ein anderes Wort getroffen',
    'annotation_korrekt': 'Annotation sieht richtig aus',
    'annotation_falsch': 'Annotation sieht falsch aus',
    'konzept_fehlt': 'Konzept fehlt',
    'kein_korpusbeleg': 'kein Korpusbeleg',
    'unsicher': 'nach dem Lesen unsicher',
}

FRAGE = {
    'aufloesungsartefakt': 'Ist hier wirklich nichts zu tun?',
    'annotation_korrekt': 'Ist die Annotation dieser Stellen richtig?',
    'annotation_falsch': 'Sind diese Stellen falsch annotiert?',
    'konzept_fehlt': 'Soll dieses Lemma das vorgeschlagene Konzept bekommen?',
    'kein_korpusbeleg': 'Soll ein Lemma ohne einen einzigen Korpusbeleg klassifiziert werden?',
    'unsicher': 'Wie soll mit diesem Fall verfahren werden?',
}


def laden():
    if not EVIDENCE.exists():
        sys.exit('%s fehlt. Erst: python scripts/review/collect-359-evidence.py --write' % EVIDENCE)
    if not VORSCHLAEGE.exists():
        sys.exit('%s fehlt.' % VORSCHLAEGE)
    with EVIDENCE.open(encoding='utf-8') as fh:
        ev = json.load(fh)
    with VORSCHLAEGE.open(encoding='utf-8') as fh:
        vo = json.load(fh)
    if 'faelle' not in ev or 'faelle' not in vo:
        sys.exit('eine der beiden Dateien hat kein Feld `faelle`')
    return ev, vo


def zitate_pruefen(schluessel, f, b):
    """Steht jedes Zitat dieser Bewertung so in den Belegen?

    Anlass: beim Ziehen der Umlaute in dieser Datei sind drei mittelhochdeutsche
    Zitate mitgezogen worden (`wandels bloss` wurde zu `wandels bloß`,
    `tugent gross` zu `tugent groß`, `unde fuer` zu `unde für`). Alle drei sahen
    im fertigen HTML richtig aus, und alle drei waren falsch: der Beleg darueber
    las anders als das Zitat darunter. Das faellt keinem Leser auf und macht die
    Begruendung wertlos.

    Geprueft werden alle Felder aus `_prosafelder`, nicht nur `begruendung`.

    Geprueft wird nur, was wie ein Zitat aussieht: in Rueckwaertsstrichen, mit
    Leerzeichen darin. Einzelne Woerter sind meist Bezeichner (`lemma_2909`,
    `@pos`) oder Nennformen und stehen nicht in den Belegen. Zitate mit `...`
    sind gekuerzt und werden stueckweise geprueft.

    Beide Seiten werden auf Buchstaben und Leerzeichen heruntergebrochen, sonst
    scheitert der Vergleich an der Zeichensetzung: im Beleg steht `cranc .` als
    eigenes Satzzeichen-Element, im Zitat `cranc.`. Nicht heruntergebrochen wird
    `ss` gegen `ß`, denn genau das ist der gesuchte Fehler.

    Was bewusst kein Korpuszitat ist, etwa die Nennung einer Formel, steht im
    Fall unter `zitate_frei` und wird uebersprungen. Das ist eine Erklaerung und
    keine Ausnahme: wer etwas dort eintraegt, sagt damit, dass es nicht aus
    einem Beleg stammt.
    """
    import re

    def flach(s):
        s = s.replace('…', ' ')
        s = re.sub(r'[^\w\säÄöÖüÜßâêîôûáéíóúàèìòùåøœæ]', ' ', s, flags=re.UNICODE)
        return re.sub(r'\s+', ' ', s).strip().lower()

    heuhaufen = flach(' '.join(
        ' '.join([z['text'] for z in x.get('zeilen_davor', [])]
                 + [x.get('treffer_davor', ''), x.get('treffer', ''), x.get('treffer_danach', '')]
                 + [z['text'] for z in x.get('zeilen_danach', [])])
        for x in f['belege']))
    frei = [flach(x) for x in b.get('zitate_frei', [])]

    fehlend = []
    for feld, text in _prosafelder(b):
        for zitat in re.findall(r'`([^`]+)`', text):
            if ' ' not in zitat.strip():
                continue
            if flach(zitat) in frei:
                continue
            for stueck in [flach(s) for s in zitat.split('...')]:
                if len(stueck) < 8 or ' ' not in stueck:
                    continue
                if stueck in frei:
                    continue
                if stueck not in heuhaufen:
                    fehlend.append('%s: %s' % (feld, stueck))
    return fehlend


def _prosafelder(b):
    """Jedes Feld einer Bewertung, dessen Text auf der Karte landet.

    Bis Runde 1 zu #443/#359 hat das Gate nur `begruendung` gelesen. Genau
    darueber steht aber `kurz`, fett gesetzt und als erstes gelesen, und dort
    stand bei `roess` ein Zitat, das kein Beleg hergibt: die Fehlerklasse, fuer
    die das Gate gebaut wurde, ein Feld weiter oben. Wer ein Feld hinzufuegt,
    das in die Seite geht, traegt es hier ein.
    """
    felder = [(name, b.get(name)) for name in
              ('kurz', 'begruendung', 'nebenbefund', 'stichprobe')]
    v = b.get('vorschlag')
    if isinstance(v, dict):
        felder += [('vorschlag.' + name, v.get(name))
                   for name in ('text', 'unsicherheit')]
    return [(name, text) for name, text in felder if isinstance(text, str)]


def abgleichen(ev, vo):
    """Streng: jeder Fall braucht eine Bewertung, jede Bewertung einen Fall,
    und jeder genannte Beleg muss unter den gemessenen stehen."""
    gemessen = {}
    for f in ev['faelle']:
        gemessen['%s|%s' % (f['form'], f['lemma_id'])] = f

    fehlt_bewertung = sorted(set(gemessen) - set(vo['faelle']))
    fehlt_fall = sorted(set(vo['faelle']) - set(gemessen))
    fehler = []
    if fehlt_bewertung:
        fehler.append('ohne Bewertung: %s' % ', '.join(fehlt_bewertung))
    if fehlt_fall:
        fehler.append('Bewertung ohne gemessenen Fall: %s' % ', '.join(fehlt_fall))

    for schluessel, b in vo['faelle'].items():
        f = gemessen.get(schluessel)
        if f is None:
            continue
        vorhanden = {x['xml_id'] for x in f['belege']}
        unbekannt = [x for x in b.get('tragende_belege', []) if x not in vorhanden]
        if unbekannt:
            fehler.append('%s nennt Belege, die nicht gemessen sind: %s'
                          % (schluessel, ', '.join(unbekannt)))
        if b['bewertung'] not in OPTIONEN:
            fehler.append('%s hat die unbekannte Bewertung %r' % (schluessel, b['bewertung']))
        if b.get('vorschlag') and not b.get('tragende_belege'):
            fehler.append('%s macht einen Vorschlag ohne tragenden Beleg' % schluessel)
        for zitat in zitate_pruefen(schluessel, f, b):
            fehler.append('%s zitiert etwas, das so in keinem Beleg steht: %r'
                          % (schluessel, zitat))
    return gemessen, fehler


def _texte_gelesen(ev):
    """Wie viele TEI-Texte der Sammellauf gelesen hat.

    Steht seit dieser Runde in `evidence.json`. Fehlt das Feld, stammt die
    Datei aus einem aelteren Lauf, und dann wird die Zahl NICHT geraten: eine
    zur Bauzeit gezaehlte Menge ist eine andere als die gesammelte, und der
    Unterschied ist genau das, was der Datenstand festhalten soll.
    """
    n = ev.get('texte_gelesen')
    return '%d TEI-Texte' % n if n else 'TEI-Texte (Anzahl im Sammellauf nicht festgehalten)'


def _korpus_version():
    """Die Korpus-Indexversion aus dem Index, nicht aus dieser Datei.

    Sie stand hier als Zeichenkette und waere beim naechsten Bump still falsch
    geworden: die Seite haette einen Datenstand behauptet, den sie nicht hat,
    und ihr Datenstand ist der einzige Grund, warum eine Antwort spaeter noch
    zuzuordnen ist. Die Belege selbst kommen aus den TEI-Dateien und nicht aus
    dem Index; die Version datiert sie, sie erzeugt sie nicht.
    """
    import gzip
    import json as _json

    pfad = REPO / 'data' / 'corpus-index.json.gz'
    if not pfad.exists():
        return 'nicht gemessen (data/corpus-index.json.gz fehlt)'
    try:
        with gzip.open(pfad, 'rt', encoding='utf-8') as fh:
            return _json.load(fh).get('version') or 'ohne Versionsangabe'
    except (OSError, ValueError) as fehler:
        return 'nicht lesbar (%s)' % fehler.__class__.__name__


def _zahlwort(n, einzahl, mehrzahl):
    """"1 Token in 1 Text" statt "1 Tokens in 1 Texten".

    Dreizehn Karten trugen die Mehrzahl bei einem einzigen Beleg. Das ist
    kosmetisch, steht aber in einer Seite, die eine Fachwissenschaftlerin
    liest, und die Zahl daneben ist eine Aussage ueber den Bestand.
    """
    return '%d %s' % (n, einzahl if n == 1 else mehrzahl)


def fundstelle(b):
    if b['kontextart'] == 'vers' and b['zeile_n']:
        return 'Vers %s' % b['zeile_n']
    return 'Prosa, ohne Verszählung'


def bau_fall(schluessel, f, b):
    form, lemma_id = schluessel.split('|', 1)
    bew = b['bewertung']

    merkmale = [
        ('Lemma', '%s (%s)' % (lemma_id, f['lemma'])),
        ('Boreks Liste', {'wl-pferdetypen': 'Pferdebezeichnungen',
                          'wl-koerperteile': 'Körperteile',
                          'wl-gangarten': 'Gangarten'}.get(f['liste'], f['liste'])),
        ('Im Bericht als', {'verdacht': 'verdächtige Zuordnung',
                            'klassifikation': 'Klassifikationskandidat',
                            'koerperteil': 'Körperteil-Zeile'}.get(f['klasse'], f['klasse'])),
        ('Belege', ('kein einziges Token im Korpus' if f['tokens_gesamt'] == 0
                    else '%s in %s' % (_zahlwort(f['tokens_gesamt'], 'Token', 'Tokens'),
                                       _zahlwort(f['texte_gesamt'], 'Text', 'Texten')))),
        ('Befund', BEWERTUNG_LABEL[bew]),
    ]
    if f['konzepte']:
        merkmale.append(('Konzepte heute', ', '.join(k['term'] or k['id'] for k in f['konzepte'])))
    else:
        merkmale.append(('Konzepte heute', 'keine'))

    # Die tragenden Belege zuerst: wer die Begruendung liest, soll nicht suchen.
    tragend = b.get('tragende_belege', [])
    rang = {x: i for i, x in enumerate(tragend)}
    sortiert = sorted(f['belege'], key=lambda x: (rang.get(x['xml_id'], 10 ** 6), x['xml_id']))
    gezeigt = sortiert[:ANZEIGE_CAP]

    belege = [dict(
        werk=x['titel'] or x['sigle'],
        fundstelle='%s, %s' % (x['sigle'], fundstelle(x)),
        xml_id=x['xml_id'],
        wortart=('Wortart %s' % x['pos']) if x['pos'] else '',
        zeilen_davor=x.get('zeilen_davor', []),
        zeile_n=x.get('zeile_n', ''),
        treffer_davor=x.get('treffer_davor', ''),
        treffer=x.get('treffer', ''),
        treffer_danach=x.get('treffer_danach', ''),
    ) for x in gezeigt]

    hinweis = None
    if f['tokens_gesamt'] > len(gezeigt):
        hinweis = markup('%d von %d Belegen gezeigt, die tragenden zuerst. %s'
                         % (len(gezeigt), f['tokens_gesamt'], b.get('stichprobe', '')
                            or 'Die übrigen stehen in evidence.json.'))
    elif b.get('stichprobe'):
        hinweis = markup(b['stichprobe'])

    vorschlag = None
    if b.get('vorschlag'):
        v = b['vorschlag']
        # Keine Begruendung im Vorschlagsblock: sie steht vollstaendig im Block
        # darueber ("Was beim Lesen der Belege herauskam"). Zweimal derselbe
        # Absatz auf einer Karte liest sich wie zwei Aussagen und ist eine.
        vorschlag = dict(
            text=markup(v['text']),
            begruendung=('Woraus das folgt, steht im Absatz darüber. Die tragenden Stellen sind '
                         + ', '.join('<span class="mono">%s</span>' % e(x)
                                     for x in b['tragende_belege']) + '.'),
            unsicherheit=markup(v.get('unsicherheit', '')),
        )

    fall = dict(
        id=schluessel.replace('|', '--'),
        gruppe=bew,
        kopf='%s  →  %s' % (form, f['lemma']),
        frage=FRAGE[bew],
        merkmale=merkmale,
        belege=belege,
        beleg_hinweis=hinweis,
        vorschlag=vorschlag,
        optionen=OPTIONEN[bew],
        sichtbar=4,
        _kurz=b['kurz'],
        _begruendung=b['begruendung'],
        _nebenbefund=b.get('nebenbefund'),
        _klasse=f['klasse'],
    )
    return fall


def lesart_block(fall):
    """Was beim Lesen herauskam, als eigener Absatz ueber dem Vorschlag.

    Das ist kein Vorschlag und wird deshalb nicht so ausgezeichnet: es ist der
    Bericht darueber, was in den Belegen steht.
    """
    teile = ['<div class="block"><p class="eyebrow">Was beim Lesen der Belege herauskam</p>',
             '<p style="font-weight:600;margin:0 0 8px">%s</p>' % markup(fall['_kurz']),
             '<p style="margin:0">%s</p>' % markup(fall['_begruendung'])]
    if fall.get('_nebenbefund'):
        teile.append('<p style="margin:10px 0 0;font-size:.9rem;color:var(--text-secondary)">'
                     '<b>Nebenbefund, gehört nicht zu dieser Frage:</b> %s</p>'
                     % markup(fall['_nebenbefund']))
    teile.append('</div>')
    return ''.join(teile)


def rohe_striche(seite):
    """Rueckwaertsstriche im sichtbaren Teil des fertigen Dokuments.

    Die Pruefung sitzt absichtlich am Ende und nicht an den Feldern: sie misst
    das Erzeugnis und nicht den Weg dorthin. In Runde 1 zu #443/#359 sind vier
    verschiedene Felder ungesetzt durchgelaufen, und jedes einzeln zu
    bewachen hiesse, das fuenfte zu vergessen.

    Der Skriptteil ist ausgenommen: dort sind Rueckwaertsstriche JavaScript
    (Template-Literale) und gehoeren hin.
    """
    import re

    sichtbar = re.sub(r'<script\b.*?</script>', '', seite, flags=re.S | re.I)
    treffer = []
    for i, zeile in enumerate(sichtbar.split('\n'), 1):
        if '`' in zeile:
            stelle = zeile.index('`')
            treffer.append((i, zeile[max(0, stelle - 40):stelle + 40].strip()))
    return treffer


def markup(text):
    """Sehr kleine Auszeichnung: `code` und **fett**. Mehr braucht es nicht,
    und mehr waere eine zweite Sprache in einer Datendatei.

    Ein Rueckwaertsstrich-Abschnitt MIT Leerzeichen ist ein mittelhochdeutscher
    Beleg und wird gesetzt wie die Belege darueber, also in der Serifenschrift.
    Ohne Leerzeichen ist es ein Bezeichner (`lemma_2909`, `@pos`) und bleibt
    dicktengleich. Ein vierzeiliges Lanzelet-Zitat in Monospace liest sich wie
    eine Fehlermeldung.
    """
    roh = e(text)
    teile = roh.split('`')
    roh = ''.join(
        t if i % 2 == 0
        else '<span class="%s">%s</span>' % ('zit' if ' ' in t.strip() else 'mono', t)
        for i, t in enumerate(teile))
    teile = roh.split('**')
    return ''.join(t if i % 2 == 0 else '<b>%s</b>' % t for i, t in enumerate(teile))


def main():
    ap = argparse.ArgumentParser(description='#359: Pruefseite bauen.')
    ap.add_argument('--pruefen', action='store_true',
                    help='Nur abgleichen, nichts schreiben.')
    args = ap.parse_args()

    ev, vo = laden()
    gemessen, fehler = abgleichen(ev, vo)
    if fehler:
        print('Abgleich fehlgeschlagen:')
        for f in fehler:
            print('  ' + f)
        return 1
    print('Abgleich in Ordnung: %d Faelle, jede Bewertung mit gemessenen Belegen.' % len(gemessen))
    if args.pruefen:
        return 0

    faelle = [bau_fall(s, gemessen[s], vo['faelle'][s]) for s in sorted(gemessen)]

    # Die Lesart steht vor dem Vorschlag. Das Format kennt den Block nicht, es
    # kennt nur Karten; deshalb wird er hier in die Karte hineingeschrieben.
    import review_page
    urspruenglich = review_page._fall_html

    def mit_lesart(f):
        roh = urspruenglich(f)
        marke = '<div class="block">'
        # Vor den Vorschlagsblock, also vor den zweiten Block der Karte.
        erster = roh.index(marke)
        zweiter = roh.index(marke, erster + 1)
        return roh[:zweiter] + lesart_block(f) + roh[zweiter:]

    review_page._fall_html = mit_lesart
    try:
        seite = render(spec(ev, faelle))
    finally:
        review_page._fall_html = urspruenglich

    uebrig = rohe_striche(seite)
    if uebrig:
        print('Rueckwaertsstriche im sichtbaren Text, %d Stelle(n):' % len(uebrig))
        for zeile, text in uebrig:
            print('  Zeile %d: %s' % (zeile, text))
        print('Hier fehlt markup(). Nichts geschrieben.')
        return 1

    ZIEL.write_text(seite, encoding='utf-8')
    print('geschrieben: %s (%d Faelle, %.0f KB)'
          % (ZIEL, len(faelle), len(seite.encode('utf-8')) / 1024.0))
    return 0


def vorab_panel(zahl):
    """Der Befund, der vor allen Karten steht.

    Die Haelfte der 45 Faelle ist keine Frage an KZW, sondern ein Befund ueber
    das Abgleichsverfahren. Wer das erst bei Karte 31 merkt, hat bis dahin die
    falsche Frage beantwortet. Deshalb steht es oben, und deshalb fuehrt eine
    Sprungliste direkt zu den Faellen, die eine Entscheidung brauchen.
    """
    mit = sum(zahl[g['id']] for g in GRUPPEN if g['entscheidung'])
    ohne = sum(zahl[g['id']] for g in GRUPPEN if not g['entscheidung'])
    punkte = []
    for g in GRUPPEN:
        n = zahl[g['id']]
        if not n:
            continue
        punkte.append(
            '<li><a href="#g-%s">%s</a> <span class="anz">%d %s</span></li>'
            % (e(g['id']), e(g['titel']), n,
               'Fall' if n == 1 else 'Fälle'))
    return (
        '<div class="panel wichtig">'
        '<h2>Bitte zuerst lesen: %d der %d Fälle brauchen keine Entscheidung</h2>'
        '<p>Der Bericht, aus dem diese Liste stammt, gleicht Boreks Wortformen mit unseren '
        'Lemmaansetzungen ab. Boreks Listen enthalten aber <b>gebeugte Formen</b>, und wo eine '
        'fremde Ansetzung zufällig so aussieht wie eine solche Form, trifft der Abgleich das '
        'falsche Wort. <span class="mono">oren</span> trifft dann das Fabelvolk der '
        '<span class="mono">Ôren</span> statt das Ohr, <span class="mono">lenden</span> das Verb '
        '„landen“ statt die Lende, <span class="mono">gorre</span> das Königreich Gorre aus dem '
        'Prosa-Lancelot statt die Gurre.</p>'
        '<p>Das ist an den Belegstellen geprüft, Fall für Fall. Übrig bleiben <b>%d Fälle, die '
        'wirklich eine Entscheidung brauchen</b>. Die anderen %d stehen trotzdem hier, mit ihren '
        'Belegen, damit nachvollziehbar ist, warum sie im Bericht standen und warum sie erledigt '
        'sind.</p>'
        '<ul class="nav">%s</ul>'
        '</div>' % (ohne, mit + ohne, mit, ohne, ''.join(punkte)))


def spec(ev, faelle):
    zahl = {g['id']: sum(1 for f in faelle if f['gruppe'] == g['id']) for g in GRUPPEN}
    aus_klasse = {}
    for f in faelle:
        aus_klasse[f['_klasse']] = aus_klasse.get(f['_klasse'], 0) + 1
    return dict(
        vorab=vorab_panel(zahl),
        kennung='mhdbdb-359-borek',
        titel='Boreks Pferdewortlisten: 45 Fälle zur philologischen Prüfung',
        untertitel=(
            'Verdächtige Lemmazuordnungen, Klassifikationskandidaten und die fünf Körperteil-Zeilen, '
            'jeder Fall mit seinen Belegstellen aus dem Korpus.'),
        vorgang='#359',
        anleitung=[
            'Diese Datei ist vollständig. Sie brauchen kein Internet, keine Anmeldung und keine '
            'Installation: alles steht in der Datei, die Sie gerade geöffnet haben.',
            'Tragen Sie oben Ihren Namen ein. Jede Antwort und jeder Kommentar wird sofort in Ihrem '
            'Browser gespeichert, und Sie können die Datei schließen und später weitermachen. '
            '<b>Die Anzeige oben rechts ist maßgeblich:</b> steht dort eine Uhrzeit, ist gespeichert. '
            'Steht dort, dass der Browser nicht speichert, arbeiten Sie trotzdem weiter und drücken '
            'vor dem Schließen <b>JSON</b>, sonst geht die Sitzung verloren.',
            'Zum Zurückschicken drücken Sie oben <b>JSON</b>. Diese Datei enthält Ihren Namen, alle '
            'Antworten, alle Kommentare und alle Bearbeitungsstände. <b>Bericht</b> erzeugt daneben '
            'eine lesbare HTML-Fassung zum Ansehen oder Ausdrucken. Mit <b>Import</b> lesen Sie einen '
            'früheren Export wieder ein, auch auf einem anderen Rechner.',
            'Jeder Fall hat drei Bearbeitungsstände: <b>unbearbeitet</b>, <b>entschieden</b> und '
            '<b>geprüft, bleibt offen</b>. Der dritte ist eine vollwertige Rückmeldung und kein '
            'Versäumnis: er sagt, dass Sie hingesehen haben und die Frage offen bleibt. Er bleibt im '
            'Export erhalten.',
            'Das Kommentarfeld steht immer offen und hängt an keiner Antwort. Sie können es an der '
            'unteren Kante größer ziehen.',
            '<b>Ein Maschinenvorschlag ist keine Entscheidung.</b> Wo einer steht, steht auch, woraus '
            'er folgt und was daran unsicher ist. Wo keiner steht, hat das Lesen der Belege keinen '
            'hergegeben, und auch das ist ein Ergebnis. Es gibt bewusst keine Schaltfläche, die viele '
            'Fälle auf einmal auf denselben Wert setzt.',
        ],
        datenstand=[
            ('Korpus', '%s, Korpus-Index %s'
             % (_texte_gelesen(ev), _korpus_version())),
            ('Wortschatz', 'Authority-Index %s' % ev.get('authority_index_version', '?')),
            ('Fallmenge', '%d Fälle aus dem Bericht: %d verdächtige Zuordnungen, '
                          '%d Klassifikationskandidaten, %d Körperteil-Zeilen'
             % (len(faelle), aus_klasse.get('verdacht', 0),
                aus_klasse.get('klassifikation', 0), aus_klasse.get('koerperteil', 0))),
            ('Davon zu entscheiden', '%d Fälle; die übrigen %d sind an den Belegen erledigt'
             % (sum(zahl[g['id']] for g in GRUPPEN if g['entscheidung']),
                sum(zahl[g['id']] for g in GRUPPEN if not g['entscheidung']))),
            ('Herkunft der Fälle', 'scripts/ingest/horses/01-wordlist-crosscheck.py, '
                                   'gemessen am 21.09.2026'),
            ('Belege gesammelt mit', 'scripts/review/collect-359-evidence.py'),
            ('Seite erzeugt mit', 'scripts/review/build-359-page.py am %s'
             % date.today().strftime('%d.%m.%Y')),
            ('Boreks Listen', 'CC BY 4.0, Luise Borek (TU Darmstadt), '
                              'tudatalib/2953, 2954, 2955'),
        ],
        gruppen=GRUPPEN,
        faelle=faelle,
        fuss=(
            '<p><b>Eine Zeile ist ein Paar aus Schreibung und Lemma, nicht ein Lemma.</b> '
            'Die 25 verdächtigen Zuordnungen sind 25 Schreibungen, aber nur 22 verschiedene Lemmata: '
            '<span class="mono">lemma_4951</span> (rôse) steht dreimal, '
            '<span class="mono">lemma_5153</span> (schaffen) zweimal. Bei den Körperteilen sind fünf '
            'Zeilen vier Lemmata, weil <span class="mono">oren</span> und '
            '<span class="mono">ôren</span> dasselbe treffen. Jedes Paar ist eine eigene Prüffrage, '
            'deshalb steht jedes als eigene Karte.</p>'
            '<p>Die Belegstellen sind Ausschnitte aus den TEI-Dateien des Korpus, mit den '
            'Verszahlen unserer Zählung und der <span class="mono">xml:id</span> des geprüften '
            'Wortes. Über diese Kennung ist jede Stelle im Repositorium wiederzufinden.</p>'
            '<p>Erzeugt aus <span class="mono">ingest/review/359-borek/evidence.json</span> '
            '(gemessen) und <span class="mono">vorschlaege.json</span> (Urteile nach der Lektüre). '
            'Wer eine Bewertung ändern will, ändert die zweite Datei und lässt den Generator '
            'erneut laufen.</p>'),
    )


if __name__ == '__main__':
    sys.exit(main())
