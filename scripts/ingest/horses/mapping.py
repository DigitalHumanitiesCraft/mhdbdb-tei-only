"""#193: Boreks Stellenangabe auf unsere Wort-IDs abbilden.

Gemeinsame Grundlage von `02-map-citations.py` (Vorpruefung, Bericht) und
`03-build-index.py` (Index-Bau). Die Aufloesung liegt hier und nicht in einem
der beiden Skripte, damit Bericht und Index nicht auseinanderlaufen koennen:
was der Bericht als 'sitzt exakt' zaehlt, muss im Index dasselbe `match`
tragen.

## Die Zaehlweisen

Unsere `<l>` tragen KEIN `xml:id`, nur ein fortlaufendes `@n`. Die zitierbare
Stellenangabe steckt in den `xml:id` der WOERTER, in drei Varianten:

    WH, PZ   Dreissigerzaehlung   339,24  ->  PZ_33924_*   (Abschnitt*100 + Vers)
    ER       Vers mal 100         4714    ->  ER_471400_*
    ER       Sonderzaehlung       4629,18 ->  ER_462918_*
    IW, TR   fortlaufend          1108    ->  IW_1108_*

Die Erec-Sonderzaehlung ist kein Sonderfall unserer Daten, sondern die
uebliche Zaehlung des Einschubs nach Vers 4629.

## Warum der Wortlaut und nicht die Zahl entscheidet

Alle 346 Stellenangaben lassen sich rechnerisch auf eine existierende Wort-ID
abbilden. Das ist kein Beweis: eine ID kann existieren und trotzdem auf einen
anderen Vers zeigen, wenn die zitierte Ausgabe anders zaehlt. Unser Parzival
folgt Leitzmann (ATB 12, 7. Aufl. 1961), unser Erec Leitzmann/Wolff (ATB 39,
3. Aufl. 1963); Borek nennt keine Ausgabe, ihr sourceDesc fuehrt nur die GND
des Werks. Verglichen wird deshalb der TEXT, und zwar als MHD-normalisierte
Buchstabenkette ohne Trennungen: eine Wortmengen-Fassung scheiterte an
Orthographie und Worttrennung ('ans grales' gegen 'an sgrales') und meldete
sechs Verse als zweifelhaft, die keine waren.

## Die vier Ergebnisse

    exact       Boreks Zahl trifft unseren Vers
    shifted     im Umkreis verschoben, Wortlaut belegt die Identitaet
                (Pz. 339,24 bis 339,28 stehen bei uns zwei Verse tiefer)
    distant     ausserhalb des Umkreises, aber eindeutig gefunden
                (Pz. 604,18 steht unter 603,18; Er. 4118 ist 4718)
    unresolved  kein Treffer, der die Schwelle und den Abstand haelt

Gezaehlt wird je BELEG, in Bericht wie Index: 346 Stellenangaben, nicht 336
Verse. Unter Pz. 340,29 stehen naemlich zwei verschiedene Verse, ein Reimpaar,
und wer je Versnummer bewertet, gibt beiden dasselbe Ziel.

Gemessen am 08.08.2026: 337 exact, 6 shifted, 3 distant, 0 unresolved.
"""
import difflib
import re
import sys
from collections import defaultdict
from pathlib import Path

from lxml import etree

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'scripts'))
from mhg_normalizer import normalize_mhg as normalize  # noqa: E402

TEI = '{http://www.tei-c.org/ns/1.0}'
XML = '{http://www.w3.org/XML/1998/namespace}'

# Boreks bibl-ID -> unsere Sigle. Alle fuenf Werke liegen im Korpus.
SIGLE = {'Wh.': 'WH', 'Pz.': 'PZ', 'Er.': 'ER', 'Iw.': 'IW', 'Tr.': 'TR'}
# Texte, deren Wort-IDs den Vers mit 100 multiplizieren (Platz fuer die
# Unterzaehlung eines Einschubs). Bei IW und TR steht die Verszahl blank.
MAL100 = {'WH', 'PZ', 'ER'}

UMKREIS = 4
# Ab hier gilt ein Vers als derselbe. Der Wert liegt in den gemessenen Daten
# (08.08.2026) in einer leeren Zone: schwaechste akzeptierte Entsprechung
# 0.84, staerkster verworfener Treffer 0.42, dazwischen nichts.
SCHWELLE = 0.75
# Vorsprung, den ein werkweit gesuchter Treffer vor dem zweitbesten braucht.
# Gemessen liegen die drei Faelle bei 1.00/0.68, 0.95/0.62 und 1.00/0.62.
# Ohne die Bedingung faende die Suche im Versepos eine beliebige Formelzeile.
ABSTAND = 0.15


def kette(s):
    """Ein Vers als vergleichbare Buchstabenkette: MHD-normalisiert, ohne
    Trennungen und Interpunktion. Die Worttrennung faellt bewusst weg, sie
    ist zwischen Ausgaben nicht stabil ('ans grales' / 'an sgrales')."""
    return re.sub(r'[^a-z]', '', normalize(s.lower()))


def aehnlich(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio() if a and b else 0.0


def stellenkern(n, sigle):
    """Boreks Angabe auf den Verskern unserer Wort-IDs abbilden."""
    if ',' in n:
        a, b = n.split(',')
        return int('%d%02d' % (int(a), int(b)))
    return int(n) * 100 if sigle in MAL100 else int(n)


def lade_verse(sigle):
    """Verskern -> Wortliste und Verskern -> Vergleichskette.

    Der Verskern ist zugleich die Referenz fuer den Sprung in die Leseansicht,
    und zwar die einzige, die in allen fuenf Werken traegt. Das `@n` des `<l>`
    genuegt dafuer nicht:

        PZ   <div n='339'><l n='26'>   das <l> traegt nur die 26, der
                                       Abschnitt haengt am <div>
        WH   <div n='77'><l n='14'>    seit #358 wie PZ. Vorher hingen alle
                                       14.002 <l> in EINEM <p> und die
                                       Dreissiger-Nummer steckte allein in
                                       den Wort-IDs; genau dieser Deep-Link
                                       hat den Befund ausgeloest
        ER   <l n='4629'>              der Ambraser Einschub steht als
                                       <supplied> in EINEM <l> und deckt die
                                       Kerne 462900 bis 462957 ab; seine 57
                                       Verse haben kein eigenes <l>
        IW   <l n='1108'>              deckungsgleich

    Deshalb rendert die Leseansicht jedes `<l>` mit `data-core`, der Kernzahl
    seiner ersten Wort-ID, und der Deep-Link nennt `?verseId=PZ_33926`.
    """
    root = etree.parse(str(REPO / 'tei' / ('%s.tei.xml' % sigle))).getroot()
    woerter = defaultdict(list)
    for w in root.iter(TEI + 'w'):
        wid = w.get(XML + 'id')
        if wid and w.text:
            woerter[int(wid.split('_')[1])].append(w.text)
    return woerter, {k: kette(' '.join(v)) for k, v in woerter.items()}


def aufloesen(n, sigle, fassungen, verskette):
    """Eine Stellenangabe aufloesen.

    `fassungen` ist eine Liste von Wortlauten, aus der die beste gewinnt.
    Beide Aufrufer geben hier GENAU EINEN Wortlaut hinein, naemlich den des
    einzelnen Belegs, und das ist der Grund fuer die Liste statt eines
    Strings: die erste Fassung bewertete alle Zitate einer Versnummer
    gemeinsam. Das ging gut, solange dieselbe Nummer denselben Vers meint.
    Unter Pz. 340,29 stehen aber zwei verschiedene Verse, ein Reimpaar, und
    gemeinsam bewertet bekam der zweite das Ziel des ersten. Der eigene
    Wortlaut ist die genauere Auskunft, auch wenn Boreks Nummer beide traegt.
    """
    kern = stellenkern(n, sigle)
    ketten = [k for k in (kette(t) for t in fassungen) if k]
    if not ketten:
        return dict(target=None, match='unresolved', score=0.0, versatz=None,
                    kern=kern)

    score, _, d = max((aehnlich(b, verskette.get(kern + d, '')), -abs(d), d)
                      for b in ketten for d in range(-UMKREIS, UMKREIS + 1))
    if score >= SCHWELLE:
        return dict(target='%s_%d' % (sigle, kern + d), kern=kern + d,
                    match='exact' if d == 0 else 'shifted',
                    score=round(score, 2), versatz=d)

    # Der Umkreis ist zu eng fuer zwei Faelle: ein Versatz kann ueber die
    # Grenze des Dreissigers gehen und eine falsche Ziffer springt beliebig
    # weit. Werkweit suchen, aber nur bei eindeutigem Treffer uebernehmen.
    # Je Vers nur der beste Wert, BEVOR die beiden Plaetze bestimmt werden.
    # Sonst kann derselbe Vers beide Plaetze belegen, wenn zwei Fassungen ihn
    # verschieden gut treffen, und der Abstand misst ihn gegen sich selbst:
    # ein sicherer Treffer faellt dann auf 'unresolved'. Mit dieser Quelle
    # tritt es nicht ein (alle zehn doppelt zitierten Verse sind exact), aber
    # die Falle wuerde jede Wiederverwendung des Moduls erben.
    bester = {}
    for b in ketten:
        for k, t in verskette.items():
            if t:
                q = aehnlich(b, t)
                if q > bester.get(k, -1.0):
                    bester[k] = q
    rang = sorted(((q, k) for k, q in bester.items()), reverse=True)[:2]
    (q1, k1) = rang[0] if rang else (0.0, None)
    q2 = rang[1][0] if len(rang) > 1 else 0.0
    if k1 is not None and q1 >= SCHWELLE and q1 - q2 >= ABSTAND:
        return dict(target='%s_%d' % (sigle, k1), kern=k1, match='distant',
                    score=round(q1, 2), versatz=k1 - kern)
    return dict(target=None, match='unresolved', score=round(q1, 2),
                versatz=None, kern=kern)


def lade_borek(pfad):
    """Boreks Verse je Werk: {werk: {n: [wortlaut, ...]}}."""
    baum = etree.parse(str(pfad))
    belege = defaultdict(lambda: defaultdict(list))
    for src in baum.getroot().iter(TEI + 'source'):
        werk = (src.get('ref') or '').lstrip('#')
        for l in src.iter(TEI + 'l'):
            belege[werk][l.get('n')].append(
                re.sub(r'\s+', ' ', ''.join(l.itertext())).strip())
    return belege
