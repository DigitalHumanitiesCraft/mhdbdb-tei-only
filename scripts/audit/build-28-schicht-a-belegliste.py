#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#28 Schicht A: Belegliste fuer KZW (lateinische Zitatstellen).

Schicht A = Sprachwechsel im Text. Der Thread (Kommentar chsteiner vom 2026-09-23,
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
      (`in`, `ad`, `me`, `nos` u.a. gibt es auch mhd.). Die Erweiterung
      der Mindestliste (LATEIN_ERW) wird zur Laufzeit um jede Form bereinigt,
      die im Korpus auch an einem Lemma ohne Lateinkonzept haengt,
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
Weil (b) allein mhd. Zufallstreffer liefert (LZT_66140_2: dreimal `in`),
zaehlen (b)-Treffer nur zusammen mit mindestens einem (c)- oder (d)-Treffer
im Fenster; ohne einen solchen ist der Score 0.

Selbsttest (`--selbsttest`): PRUEFSET im Skript nennt Faelle mit erwartetem
Ergebnis (u.a. alle MAI-et nein, deutsche engel-Belege nein, lateinische
Zitate ja); bei Abweichung harter Fehler. Die Schwelle wurde nach diesem Set
gesetzt, nicht umgekehrt.

Schwelle und Vorrang der Regeln (vorschlag): 1. dominus ist immer `ja` (Fall
ZITAT laut Thread, ABG_407050_3). 2. Steht die Form des Belegs selbst in
ZIEL_LATEIN_FORMEN (angelus, angeli, leonis, creatura ...), ist es `ja`; die
Liste ist von Hand am Formeninventar der Beleg-Token gelesen, nicht aus
LATEIN_FORMEN abgeleitet, weil dort auch `et` selbst steht. 3. Bei et sind
"alpha et o/omega" und "et cetera" feste Formeln und `ja`. 4. Sonst nach Score:
  score >= SCHWELLE_JA (3)       -> `ja`
  score == SCHWELLE_GRENZ (2)    -> `grenzfall`
  sonst                          -> `nein`
Die Spalte `regel` nennt, was entschieden hat (dominus, zielform, formel,
score). Der Score wird immer berechnet und ausgegeben.

OFFEN GESAGT: Schwelle, Kriterien und Wortlisten sind am PRUEFSET und an PKP
und den Negativkontrollen (PZ, WH, ER, LZT, MAI) eingestellt, nicht an einer
unabhaengigen Stichprobe. Die Trefferquoten sind deshalb optimistisch.

Der Vorschlag ist heuristisch. Er sieht keine Grammatik, nur Nachbarschaft:
ein kurzes lateinisches Zitat (ein Wort, eine Formel) in deutscher Umgebung
wird niedrig bewertet, auch wenn es echtes Latein ist. Eine Form, die nur
an Latein-Lemmata vorkommt, aber im Korpus nie an einem anderen Lemma
auftaucht, kann trotzdem ein deutsches Wort sein. Entscheiden tut KZW.

## Ausgabe

ingest/foreign-lang/28-schicht-a-belegliste.csv (UTF-8 mit BOM, Trennzeichen
';' wie in build-foreign-candidates-28.py, weil die Listen in Excel geoeffnet
werden), Kopfzeile: sigle, xml_id, lemma, lemma_id, form, vorschlag_latein,
latein_score, regel, kontext. ALLE Belege der sieben Lemma-IDs, auch die mit
`nein`, damit die Liste vollstaendig ist. Sortiert nach vorschlag_latein (ja,
grenzfall, nein), darin nach Sigle und Dokumentreihenfolge; zwei Laeufe sind
byte-gleich. Auf stdout je Lemma eine Zaehlzeile.

Nur lesend. Aendert nichts in tei/ oder authority-files/.

Usage:
    python scripts/audit/build-28-schicht-a-belegliste.py
"""
import argparse
import csv
import sys
import unicodedata
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
# dominus: Thread #28, Kommentar chsteiner 2026-09-23 ("Lateinisches Zitatwort").
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

LATEIN_MIN = set(
    'et est non qui quae quod ad cum per sunt ut enim autem deus dei deo domine '
    'domini in nomine patris filii spiritus sancti amen ego sum me mihi tu te '
    'tibi nos vos eius eum ab de ex sed nec vel sicut super sub inter propter '
    'quia quoniam erat esse fuit habens'.split())

# Erweiterung nach Messung an PKP. Vor Gebrauch wird jede Form gestrichen, die im
# Korpus auch an einem Lemma ohne concept_23123100 haengt (mhd. Homographe wie
# quam an komen, nam an nemen, vir an vuer/vier; siehe bereite_vor).
LATEIN_ERW = set(
    # Erweiterung nach Messung an PKP (die lateinischen Nachbarn tragen dort
    # meist ein @lemmaRef, (a) greift also nicht): haeufige Pronomen, Partikeln
    # und Formen aus Bibel und Liturgie. Nur eindeutig lateinische Formen;
    # mhd. Homographe (si, sine, unde, ita) sind bewusst nicht aufgenommen;
    # in, ad, me, nos stehen auf der Mindestliste und werden durch die
    # (b)-Regel abgefangen.
    'ipse ipsa ipsum ipsi eos eis eo ea eam illa ille illud illi hic haec hoc '
    'nisi mei tui sui nostri vestri omnes omnis omnia estote estis '
    'cui cuius quem quid quo qua quibus quos quas quem dicit dixit dicens '
    'ergo igitur tunc ecce domino dominum sancto sanctum sanctus christus '
    'jhesus jesus jhesu patri patre pater mater filio filius fili tuum tuam '
    'meum meam meus mea suam suum suus sua nostra nostrum vestra vestrum '
    'erit erunt fuerit fuerint eius eorum earum etiam quoque tamen vero quasi '
    'aut neque nunc semper omnibus omnium deum deus dei qui quae quod '
    'pro contra apud ante post usque dum quando ubi ibi '
    'verbum verba verbo opera opus mundi mundo mundus anima anime animam '
    'regnum regni celorum celi coelum terra terre terram vita vite vitam '
    'peccatum peccata peccati fide fidem fides gloria gloriam magna magnus '
    'populus populi populo viri homo hominis hominem hominum mulier '
    'dicite dicam dico dixerunt respondit autem etc'.split())

# Wirksame Liste fuer Kriterium (b): Mindestliste plus Erweiterung (nach dem
# Streichen der Homographe in bereite_vor).
LATEIN_FUNKTION = set(LATEIN_MIN) | set(LATEIN_ERW)

# Eindeutig lateinische Flexionsformen der Ziellemmata. Gelesen am
# Formeninventar der Beleg-Token je Lemma (engel 32 Formen, lewe 46, creatura
# 59, item 3, et 3; Inventar mit dem Skript im Docstring nachpruefbar), nur
# Formen mit lateinischer Endung, die kein mhd. Wort sind. Nicht LATEIN_FORMEN:
# dort stuende auch `et` selbst, und jedes et waere `ja`. Mehrdeutiges
# (angel, angels, leon, leu, item) bleibt dem Score ueberlassen.
ZIEL_LATEIN_FORMEN = {
    'lemma_1411': {'angeli', 'angelice', 'angelicis', 'angelis', 'angelo',
                   'angelorum', 'angelum', 'angelus'},
    'lemma_3726': {'leo', 'leonis', 'leonum', 'leone'},
    'lemma_1033': {'creatura'},
}

# Feste lateinische Formeln bei et (Nachbarformen, klein): "alpha et o/omega"
# (Offb 22,13; Vorgaenger alpha/alfa und zwei Schreibvarianten, Nachfolger
# o/omega) und "et cetera" (Nachfolger beginnt mit `cetera`).
ALPHA_FORMEN = {'alpha', 'alfa', 'alpfha', 'olpha'}
OMEGA_FORMEN = {'o', 'omega'}

# (d) Formen an Lemmata mit Sprachkonzept Lateinisch (Menge wird im ersten
# Korpusdurchlauf gefuellt, siehe sammle_formen)
KONZEPT_LATEIN = 'concept_23123100'
LATEIN_LEMMAS = set()   # wird in pruefe_lexikon gefuellt
LATEIN_FORMEN = set()   # wird in sammle_formen gefuellt
# Lemmata mit Konzept Lateinisch, die kein Zitat anzeigen: die im Thread
# (Kommentar chsteiner 2026-09-23) als "sicher entlehnt" und "sicher nicht fremd"
# gefuehrten Lemmata sowie schrift und nase (Gleis-1-Rauschen). Grossgeschriebene
# Lemmata (Namen) zaehlen ohnehin nicht.
D_AUSSCHLUSS = set('niht in name minner mort zunge engel lewe creatura item '
                   'bischof schrîben klâr natûre kriuze missa marter abbet '
                   'schrift nase rote baniere soldân fîn'.split())

FENSTER_SCORE = 4
FENSTER_KONTEXT = 8
SCHWELLE_JA = 3
SCHWELLE_GRENZ = 2
RANG = {'ja': 0, 'grenzfall': 1, 'nein': 2}

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
    ('id', 'LZT_66140_2', 'nein'),    # "stiess et in vil seufzen"
    ('id', 'LZT_66970_2', 'nein'),    # "er hiet et in da"
    ('id', 'BAR_1_1', 'ja'),          # alpha et o
    ('id', 'HZU2_26214221213032_10', 'ja'),   # et cetera
    ('id', 'ADP_107800_6', 'ja'),     # angeli
    ('id', 'MML_110214_1', 'ja'),     # angelus
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


def ohne_akzent(form):
    """norm ohne diakritische Zeichen (alphä -> alpha), fuer die Formeln."""
    z = unicodedata.normalize('NFD', norm(form))
    return ''.join(ch for ch in z if not unicodedata.combining(ch))


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
    jede Form, die auch an einem Lemma ohne Lateinkonzept haengt. Gibt die
    Menge dieser "anderen" Formen zurueck."""
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
    return andere


def bereite_vor(dateien):
    """Pass 1 plus Bereinigung der Erweiterungsliste von mhd. Homographen."""
    andere = sammle_formen(dateien)
    raus = sorted(LATEIN_ERW & andere)
    LATEIN_FUNKTION.clear()
    LATEIN_FUNKTION.update(LATEIN_MIN | (LATEIN_ERW - andere))
    print(f'LATEIN_FORMEN: {len(LATEIN_FORMEN)} Formen aus {len(LATEIN_LEMMAS)} Latein-Lemmata')
    print(f'LATEIN_ERW: {len(raus)} von {len(LATEIN_ERW)} Formen gestrichen (haengen auch an '
          f'Lemmata ohne Lateinkonzept): {" ".join(raus)}')


def score(ws, i):
    """Zahl der Latein-Nachbarn im Fenster um Index i; ws = Liste (form, ids)."""
    cd = 0
    nur_b = 0
    for j in range(max(0, i - FENSTER_SCORE), min(len(ws), i + FENSTER_SCORE + 1)):
        if j == i:
            continue
        form, ids = ws[j]
        nf = norm(form)
        c = bool(ids) and bool(ids & ZITAT_LEMMAS)
        if c or nf in LATEIN_FORMEN:
            cd += 1
        elif nf in LATEIN_FUNKTION:
            nur_b += 1
    # (b)-Treffer zaehlen nur zusammen mit mindestens einem (c)- oder (d)-Treffer
    return cd + nur_b if cd else 0


def vorschlag(lid, sc, ws, i):
    """(vorschlag, regel): regel nennt, was entschieden hat."""
    if lid == 'lemma_13989':
        return 'ja', 'dominus'
    if norm(ws[i][0]) in ZIEL_LATEIN_FORMEN.get(lid, ()):
        return 'ja', 'zielform'
    if lid in ('lemma_1732', 'lemma_78608'):
        vor = ohne_akzent(ws[i - 1][0]) if i > 0 else ''
        nach = ohne_akzent(ws[i + 1][0]) if i + 1 < len(ws) else ''
        if vor in ALPHA_FORMEN and nach in OMEGA_FORMEN:
            return 'ja', 'formel'
        if nach.startswith('cetera'):
            return 'ja', 'formel'
    if sc >= SCHWELLE_JA:
        return 'ja', 'score'
    if sc >= SCHWELLE_GRENZ:
        return 'grenzfall', 'score'
    return 'nein', 'score'


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
            vs, regel = vorschlag(lid, sc, ws, i)
            yield {'sigle': sigle, 'xml_id': elems[i].get(XML_ID), 'lemma': ZIELE[lid],
                   'lemma_id': lid, 'form': form, 'score': sc, 'regel': regel,
                   'vs': vs, 'kontext': ' '.join(teile)}


def selbsttest(dateien):
    """Hartes Abbrechen, wenn ein Fall des PRUEFSET abweicht oder fehlt."""
    id_erw = {k: e for a, k, e in PRUEFSET if a == 'id'}
    lem_erw = {k: e for a, k, e in PRUEFSET if a == 'lemma'}
    # Sigelmenge aus dem PRUEFSET: xml:id-Praefix vor dem ersten '_', dazu die
    # Sigle der Gruppenfaelle
    sigles = {k.split('_', 1)[0] for k in id_erw} | {k[0] for k in lem_erw}
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
          f'{sum(nlem.values())} aus {len(lem_erw)} Gruppe) in {len(sigles)} Sigeln')


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
    bereite_vor(dateien)
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
            zeilen.append((RANG[b['vs']], len(zeilen),
                           [b['sigle'], b['xml_id'], b['lemma'], b['lemma_id'], b['form'],
                            b['vs'], b['score'], b['regel'], b['kontext']]))
    # ja, grenzfall, nein; darin Reihenfolge der Dateien (Sigle) und des Dokuments
    zeilen.sort(key=lambda z: (z[0], z[1]))
    zeilen = [z[2] for z in zeilen]

    # utf-8-sig und ';' wie in build-foreign-candidates-28.py: die Listen werden
    # in Excel geoeffnet, und ohne BOM zerlegt Excel die Umlaute.
    with open(args.out, 'w', encoding='utf-8-sig', newline='') as f:
        wr = csv.writer(f, delimiter=';', lineterminator='\n')
        wr.writerow(['sigle', 'xml_id', 'lemma', 'lemma_id', 'form',
                     'vorschlag_latein', 'latein_score', 'regel', 'kontext'])
        wr.writerows(zeilen)

    for lemma in ['dominus', 'et', 'engel', 'lewe', 'creatura', 'item']:
        z = zaehl.get(lemma, Counter())
        print(f"{lemma}: {z['gesamt']} Belege, ja {z['ja']}, grenzfall {z['grenzfall']}, nein {z['nein']}")
    for lem in args.verteilung:
        for (lemma, sigle), z in sorted(je_sigle.items()):
            if lemma == lem:
                n = sum(z.values())
                print(f"  {lemma} {sigle}: {n} Belege, ja {z['ja']}, grenzfall {z['grenzfall']}, nein {z['nein']}")
    gesamt = sum(z['gesamt'] for z in zaehl.values())
    print(f"CSV: {len(zeilen)} Zeilen = alle {gesamt} Belege der sieben Lemma-IDs nach {args.out}")


if __name__ == '__main__':
    main()
