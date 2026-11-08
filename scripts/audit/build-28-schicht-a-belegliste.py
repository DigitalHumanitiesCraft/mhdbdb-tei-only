#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#28 Schicht A: Belegliste fuer KZW (lateinische Zitatstellen).

Schicht A = Sprachwechsel im Text. Der Thread (Kommentar vom 09.10.2026,
"Was als Nächstes passiert", Punkt 2) verspricht KZW eine vollstaendige Liste:
alle Belege von `dominus`, die lateinischen `et`, und die lateinischen Belege
unter `engel`, `lewe`, `creatura`, `item`.

## Was das Skript tut

Liest alle tei/*.tei.xml. Belege sind <w>-Elemente mit @lemmaRef, in dem das
Token `lexicon.xml#lemma_N` einer der Ziel-IDs steht (ganzes Token, nicht
Teilstring). Der Kontext kommt aus ALLEN <w> der Datei in Dokumentreihenfolge,
auch denen ohne @lemmaRef (sonst waeren lateinische Zitate mit unannotierten
Woertern luckenhaft).

## Latein-Score (heuristischer Vorschlag, KEIN Urteil)

Je Beleg werden die Nachbarn +-4 <w> (das Zielwort selbst nicht) angesehen.
Ein Nachbar zaehlt einmal, wenn mindestens eins gilt:
  (b) seine kleingeschriebene Form steht auf der Liste LATEIN_FUNKTION
      (`in`, `ad`, `me`, `nos` u.a. gibt es auch mhd.),
  (c) er haengt an einem ZITAT-Lemma (ZITAT_LEMMAS),
  (d) seine kleingeschriebene FORM steht in LATEIN_FORMEN. Das ist die Menge
      der Formen, die im Korpus an Lemmata mit dem Sprachkonzept Lateinisch
      (concept_23123100, lexicon.xml) haengen, MINUS jeder Form, die an
      irgendeiner Stelle auch an einem Lemma ohne dieses Konzept haengt
      (ein erster Korpusdurchlauf sammelt das). Das schliesst deutsche
      Homographe aus. Namen (grossgeschriebene Lemmata) und die im Thread
      als entlehnt oder nicht fremd geklaerten Lemmata (D_AUSSCHLUSS) zaehlen
      nicht als lateinisch.
Gestrichen: das Kriterium "Nachbar ohne @lemmaRef". Es traf deutsche
Funktionswoerter (er, was, do, der, ich, ...), die im Korpus oft
unlemmatisiert stehen, und machte alle 11 MAI-et und deutsche engel-Belege
zu `ja` (gemessen am PRUEFSET). Die lateinischen Nachbarn in PKP sind dagegen
fast immer lemmatisiert, (d) ersetzt (a) deshalb durch ein Formen-Kriterium.
Weil (b) allein mhd. Zufallstreffer liefert, zaehlt ein einzelner Nachbar,
der NUR ueber (b) trifft, nur dann, wenn der Beleg insgesamt mindestens zwei
Treffernachbarn hat: ein Gesamtscore von genau 1 wird zu 0 gesetzt, wenn der
eine Treffer ein reiner (b)-Treffer ist.

Selbsttest (`--selbsttest`): PRUEFSET im Skript nennt Faelle mit erwartetem
Ergebnis (u.a. alle MAI-et nein, deutsche engel-Belege nein, lateinische
Zitate ja); bei Abweichung harter Fehler. Die Schwelle wurde nach diesem Set
gesetzt, nicht umgekehrt.

Schwelle:
  score >= SCHWELLE_JA (3)       -> `ja`
  score == SCHWELLE_GRENZ (2)    -> `grenzfall`
  sonst                          -> `nein`
`dominus` ist immer `ja` (Fall ZITAT laut Thread, ABG_407050_3). Der Score
wird trotzdem berechnet und ausgegeben.

Der Vorschlag ist heuristisch. Er sieht keine Grammatik, nur Nachbarschaft:
ein kurzes lateinisches Zitat (ein Wort, eine Formel) in deutscher Umgebung
wird niedrig bewertet, auch wenn es echtes Latein ist. Eine Form, die nur
an Latein-Lemmata vorkommt, aber im Korpus nie an einem anderen Lemma
auftaucht, kann trotzdem ein deutsches Wort sein. Entscheiden tut KZW.

## Ausgabe

ingest/foreign-lang/28-schicht-a-belegliste.csv (UTF-8, Komma, Kopfzeile):
sigle, xml_id, lemma, lemma_id, form, vorschlag_latein, latein_score, kontext.
Nur `ja` und `grenzfall`. Auf stdout je Lemma eine Zaehlzeile ueber ALLE Belege.
Sortiert nach sigle, Dokumentreihenfolge; zwei Laeufe sind byte-gleich.

Nur lesend. Aendert nichts in tei/ oder authority-files/.

Usage:
    python scripts/audit/build-28-schicht-a-belegliste.py
"""
import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

from lxml import etree

REPO = Path(__file__).resolve().parents[2]
TEI = '{http://www.tei-c.org/ns/1.0}'
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'
LEXICON = REPO / 'authority-files' / 'lexicon.xml'
OUT = REPO / 'ingest' / 'foreign-lang' / '28-schicht-a-belegliste.csv'

# lemma_id -> erwartete <orth>
ZIELE = {
    'lemma_13989': 'dominus',
    'lemma_1732': 'et',
    'lemma_78608': 'et',
    'lemma_1411': 'engel',
    'lemma_3726': 'lewe',
    'lemma_1033': 'creatura',
    'lemma_27037': 'item',
}

# ZITAT-Lemmata, die ein Nachbar tragen kann (Kriterium c).
# dominus: Thread #28, Kommentar 09.10.2026 ("Lateinisches Zitatwort").
# Die sechs weiteren sind die ZITAT-Zeilen 1-6 der 26 Beispielfaelle im Thread
# (Kommentar chsteiner, "Beispielfaelle", Tabelle Zeilen 1-6): amen, deus,
# kyrieleison, ave, alleluia, paternoster.
ZITAT_LEMMAS = {
    'lemma_13989',  # dominus
    'lemma_12',     # amen
    'lemma_10178',  # deus
    'lemma_23245',  # kyrieleison
    'lemma_14978',  # ave
    'lemma_35505',  # alleluia
    'lemma_27181',  # paternoster
}

LATEIN_FUNKTION = set(
    'et est non qui quae quod ad cum per sunt ut enim autem deus dei deo domine '
    'domini in nomine patris filii spiritus sancti amen ego sum me mihi tu te '
    'tibi nos vos eius eum ab de ex sed nec vel sicut super sub inter propter '
    'quia quoniam erat esse fuit habens '
    # Erweiterung nach Messung an PKP (die lateinischen Nachbarn tragen dort
    # meist ein @lemmaRef, (a) greift also nicht): haeufige Pronomen, Partikeln
    # und Formen aus Bibel und Liturgie. Nur eindeutig lateinische Formen;
    # mhd. Homographe (si, sine, unde, ita) sind bewusst nicht aufgenommen;
    # in, ad, me, nos stehen auf der Mindestliste und werden durch die
    # (b)-Regel abgefangen.
    'ipse ipsa ipsum ipsi eos eis eo ea eam illa ille illud illi hic haec hoc '
    'nam nisi mei tui sui nostri vestri omnes omnis omnia estote estis '
    'cui cuius quem quam quid quo qua quibus quos quas quem dicit dixit dicens '
    'ergo igitur tunc ecce domino dominum sancto sanctum sanctus christus '
    'jhesus jesus jhesu patri patre pater mater filio filius fili tuum tuam '
    'meum meam meus mea suam suum suus sua nostra nostrum vestra vestrum '
    'erit erunt fuerit fuerint eius eorum earum etiam quoque tamen vero quasi '
    'aut neque nunc semper omnibus omnium deum deus dei qui quae quod '
    'pro contra apud ante post usque dum quando ubi ibi '
    'verbum verba verbo opera opus mundi mundo mundus anima anime animam '
    'regnum regni celorum celi coelum terra terre terram vita vite vitam '
    'peccatum peccata peccati fide fidem fides gloria gloriam magna magnus '
    'populus populi populo viri vir homo hominis hominem hominum mulier '
    'dicite dicam dico dixerunt respondit autem etc'.split())

# (d) Formen an Lemmata mit Sprachkonzept Lateinisch (Menge wird im ersten
# Korpusdurchlauf gefuellt, siehe sammle_formen)
KONZEPT_LATEIN = 'concept_23123100'
LATEIN_LEMMAS = set()   # wird in pruefe_lexikon gefuellt
LATEIN_FORMEN = set()   # wird in sammle_formen gefuellt
# Lemmata mit Konzept Lateinisch, die kein Zitat anzeigen: die im Thread
# (Kommentar 09.10.2026) als "sicher entlehnt" und "sicher nicht fremd"
# gefuehrten Lemmata sowie schrift und nase (Gleis-1-Rauschen). Grossgeschriebene
# Lemmata (Namen) zaehlen ohnehin nicht.
D_AUSSCHLUSS = set('niht in name minner mort zunge engel lewe creatura item '
                   'bischof schrîben klâr natûre kriuze missa marter abbet '
                   'schrift nase rote baniere soldân fîn'.split())

FENSTER_SCORE = 4
FENSTER_KONTEXT = 8
SCHWELLE_JA = 3
SCHWELLE_GRENZ = 2

# Pruefset fuer --selbsttest: (art, schluessel, erwartet).
# art 'lemma': schluessel (sigle, lemma), gilt fuer JEDEN Beleg dieses Lemmas
# in dieser Sigle; art 'id': schluessel ist die xml:id des Belegs.
# Quelle: Durchsicht der Koordination (Kontext gelesen), 2026-11-08.
PRUEFSET = [
    ('lemma', ('MAI', 'et'), 'nein'),   # alle 11: mhd. Partikel eht
    ('id', 'FLG1_5174230170_18', 'nein'),   # engel, deutsch
    ('id', 'FR3_113203141060_3', 'nein'),
    ('id', 'MNB_3033940_3', 'nein'),
    ('id', 'FR3_111209020180_7', 'nein'),
    ('id', 'FLG1_7272190070_7', 'nein'),
    ('id', 'ECK_78351001_3', 'ja'),     # missus est gabriel angelus
    ('id', 'ADP_103500_8', 'ja'),
    ('id', 'ADP_104900_6', 'ja'),
    ('id', 'CL_850_0', 'ja'),
    ('id', 'HUL_569_0', 'ja'),
    ('id', 'BVSN_63100_0', 'ja'),
    ('id', 'LZT_45040_7', 'nein'),
    ('id', 'WGA_401900_1', 'nein'),
]


def lemma_ids(w):
    """Menge der lemma_N-Token aus @lemmaRef (ganze Token, whitespace-getrennt)."""
    ref = w.get('lemmaRef')
    if ref is None:
        return None
    ids = set()
    for tok in ref.split():
        if '#' not in tok:
            sys.exit(f'FEHLER: unbekanntes lemmaRef-Format {tok!r} in {w.get(XML_ID)}')
        ids.add(tok.rsplit('#', 1)[1])
    return ids


def pruefe_lexikon():
    """Harter Abbruch, wenn eine Ziel-ID fehlt oder eine andere <orth> traegt."""
    gefunden = {}
    for _, e in etree.iterparse(str(LEXICON), tag=TEI + 'entry'):
        eid = e.get(XML_ID)
        orth_e = e.find('.//' + TEI + 'orth')
        if orth_e is not None and orth_e.text and not orth_e.text[0].isupper() \
                and orth_e.text not in D_AUSSCHLUSS:
            for p in e.iter(TEI + 'ptr'):
                if p.get('target') == 'concepts.xml#' + KONZEPT_LATEIN:
                    LATEIN_LEMMAS.add(eid)
                    break
        if eid in ZIELE or eid in ZITAT_LEMMAS:
            orth = e.find('.//' + TEI + 'orth')
            gefunden[eid] = orth.text if orth is not None else None
        e.clear()
    erwartet = dict(ZIELE)
    erwartet.update({'lemma_12': 'âmen', 'lemma_10178': 'deus',
                     'lemma_23245': 'kyrieleison', 'lemma_14978': 'ave',
                     'lemma_35505': 'alleluia', 'lemma_27181': 'paternoster'})
    for lid, orth in erwartet.items():
        if gefunden.get(lid) != orth:
            sys.exit(f'FEHLER: {lid} soll <orth>{orth}</orth> tragen, gefunden: {gefunden.get(lid)!r}')


def norm(form):
    return form.lower().strip('.,;:!?()[]"\'')


def lade(pfad):
    """(sigle, ws, elems): ws = Liste (form, ids) ueber alle <w> in Dokumentreihenfolge."""
    sigle = pfad.name[:-len('.tei.xml')]
    root = etree.parse(str(pfad)).getroot()
    ws, elems = [], []
    for w in root.iter(TEI + 'w'):
        ws.append((''.join(w.itertext()).strip(), lemma_ids(w)))
        elems.append(w)
    return sigle, ws, elems


def sammle_formen(dateien):
    """Erster Korpusdurchlauf: LATEIN_FORMEN = Formen an Latein-Lemmata minus
    jede Form, die auch an einem Lemma ohne Lateinkonzept haengt."""
    lat, andere = set(), set()
    for pfad in dateien:
        _, ws, _ = lade(pfad)
        for form, ids in ws:
            if not ids:
                continue
            f = norm(form)
            if ids & LATEIN_LEMMAS:
                lat.add(f)
            if ids - LATEIN_LEMMAS:
                andere.add(f)
    LATEIN_FORMEN.clear()
    LATEIN_FORMEN.update(lat - andere)


def score(ws, i):
    """Zahl der Latein-Nachbarn im Fenster um Index i; ws = Liste (form, ids)."""
    gesamt = 0
    nur_b = 0
    for j in range(max(0, i - FENSTER_SCORE), min(len(ws), i + FENSTER_SCORE + 1)):
        if j == i:
            continue
        form, ids = ws[j]
        nf = norm(form)
        c = bool(ids) and bool(ids & ZITAT_LEMMAS)
        d = nf in LATEIN_FORMEN
        b = nf in LATEIN_FUNKTION
        if c or d:
            gesamt += 1
        elif b:
            gesamt += 1
            nur_b += 1
    # ein einzelner reiner (b)-Treffer zaehlt nicht
    if gesamt == 1 and nur_b == 1:
        gesamt = 0
    return gesamt


def vorschlag(lid, sc):
    if lid == 'lemma_13989':
        return 'ja'
    if sc >= SCHWELLE_JA:
        return 'ja'
    if sc >= SCHWELLE_GRENZ:
        return 'grenzfall'
    return 'nein'


def belege(pfad):
    """Alle Belege der Ziel-Lemmata einer Datei: dict je Beleg."""
    sigle, ws, elems = lade(pfad)
    for i, (form, ids) in enumerate(ws):
        if not ids:
            continue
        for lid in sorted(ids & set(ZIELE)):
            sc = score(ws, i)
            lo = max(0, i - FENSTER_KONTEXT)
            teile = [f for f, _ in ws[lo:i]] + ['**' + form + '**'] + \
                    [f for f, _ in ws[i + 1:i + 1 + FENSTER_KONTEXT]]
            yield {'sigle': sigle, 'xml_id': elems[i].get(XML_ID), 'lemma': ZIELE[lid],
                   'lemma_id': lid, 'form': form, 'score': sc,
                   'vs': vorschlag(lid, sc), 'kontext': ' '.join(teile)}


def selbsttest(dateien):
    """Hartes Abbrechen, wenn ein Fall des PRUEFSET abweicht oder fehlt."""
    sigles = {'MAI', 'FLG1', 'FR3', 'MNB', 'ECK', 'ADP', 'CL', 'HUL', 'BVSN', 'LZT', 'WGA'}
    id_erw = {k: e for a, k, e in PRUEFSET if a == 'id'}
    lem_erw = {k: e for a, k, e in PRUEFSET if a == 'lemma'}
    gesehen = set()
    fehler = []
    nlem = Counter()
    for pfad in dateien:
        if pfad.name[:-len('.tei.xml')] not in sigles:
            continue
        for b in belege(pfad):
            if b['xml_id'] in id_erw:
                gesehen.add(b['xml_id'])
                if b['vs'] != id_erw[b['xml_id']]:
                    fehler.append(f"{b['xml_id']}: erwartet {id_erw[b['xml_id']]}, Score {b['score']} -> {b['vs']}")
            k = (b['sigle'], b['lemma'])
            if k in lem_erw:
                nlem[k] += 1
                if b['vs'] != lem_erw[k]:
                    fehler.append(f"{b['xml_id']} ({k[0]} {k[1]}): erwartet {lem_erw[k]}, Score {b['score']} -> {b['vs']}")
    for k in id_erw:
        if k not in gesehen:
            fehler.append(f'{k}: Beleg nicht gefunden (kein Beleg eines Ziel-Lemmas?)')
    for k in lem_erw:
        if nlem[k] == 0:
            fehler.append(f'{k}: keine Belege gefunden')
    if fehler:
        print('SELBSTTEST FEHLGESCHLAGEN:')
        for f in fehler:
            print('  ' + f)
        sys.exit(1)
    nfaelle = len(id_erw) + sum(nlem.values())
    print(f'Selbsttest bestanden: {nfaelle} Faelle ({len(id_erw)} einzeln, '
          f'{sum(nlem.values())} aus {len(lem_erw)} Gruppe)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(OUT))
    ap.add_argument('--verteilung', metavar='LEMMA', action='append', default=[],
                    help='zusaetzlich die Verteilung dieses Lemmas je Sigle ausgeben')
    ap.add_argument('--selbsttest', action='store_true',
                    help='nur das PRUEFSET pruefen, keine CSV schreiben')
    args = ap.parse_args()
    pruefe_lexikon()
    dateien = sorted((REPO / 'tei').glob('*.tei.xml'))
    if not dateien:
        sys.exit('FEHLER: keine TEI-Dateien gefunden')
    sammle_formen(dateien)
    print(f'LATEIN_FORMEN: {len(LATEIN_FORMEN)} Formen aus {len(LATEIN_LEMMAS)} Latein-Lemmata')
    if args.selbsttest:
        selbsttest(dateien)
        return

    zeilen = []
    zaehl = {}
    je_sigle = {}
    for pfad in dateien:
        for b in belege(pfad):
            z = zaehl.setdefault(b['lemma'], Counter())
            z['gesamt'] += 1
            z[b['vs']] += 1
            je_sigle.setdefault((b['lemma'], b['sigle']), Counter())[b['vs']] += 1
            if b['vs'] == 'nein':
                continue
            zeilen.append([b['sigle'], b['xml_id'], b['lemma'], b['lemma_id'], b['form'],
                           b['vs'], b['score'], b['kontext']])

    with open(args.out, 'w', encoding='utf-8', newline='') as f:
        wr = csv.writer(f, lineterminator='\n')
        wr.writerow(['sigle', 'xml_id', 'lemma', 'lemma_id', 'form',
                     'vorschlag_latein', 'latein_score', 'kontext'])
        wr.writerows(zeilen)

    for lemma in ['dominus', 'et', 'engel', 'lewe', 'creatura', 'item']:
        z = zaehl.get(lemma, Counter())
        print(f"{lemma}: {z['gesamt']} Belege, ja {z['ja']}, grenzfall {z['grenzfall']}, nein {z['nein']}")
    for lem in args.verteilung:
        for (lemma, sigle), z in sorted(je_sigle.items()):
            if lemma == lem:
                n = sum(z.values())
                print(f"  {lemma} {sigle}: {n} Belege, ja {z['ja']}, grenzfall {z['grenzfall']}, nein {z['nein']}")
    print(f"CSV: {len(zeilen)} Zeilen (ja plus grenzfall) nach {args.out}")


if __name__ == '__main__':
    main()
