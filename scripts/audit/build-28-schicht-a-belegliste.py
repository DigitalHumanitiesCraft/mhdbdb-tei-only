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
  (a) er traegt kein @lemmaRef,
  (b) seine kleingeschriebene Form steht auf der Liste LATEIN_FUNKTION
      (`in`, `ad`, `me`, `nos` u.a. gibt es auch mhd.),
  (c) er haengt an einem ZITAT-Lemma (ZITAT_LEMMAS),
  (d) er haengt an einem Lemma, das in lexicon.xml das Sprachkonzept
      Lateinisch (concept_23123100) traegt. Ausgenommen: Namen (gross
      geschriebene Lemmata), die im Thread als entlehnt oder nicht fremd
      geklaerten Lemmata (D_AUSSCHLUSS, u.a. niht, in, name) und die
      Homographen in/ad/a/me/nos/an (D_HOMOGRAPH).
Messbefund, der (d) noetig machte: in PKP sind die lateinischen Nachbarn
fast immer lemmatisiert, (a) und (b) allein trennen PKP nicht von PZ.
Weil (b) allein mhd. Zufallstreffer liefert, zaehlt ein einzelner Nachbar,
der NUR ueber (b) trifft, nur dann, wenn der Beleg insgesamt mindestens zwei
Treffernachbarn hat: ein Gesamtscore von genau 1 wird zu 0 gesetzt, wenn der
eine Treffer ein reiner (b)-Treffer ist.

Schwelle (festgelegt nach Messung an PKP und an den Negativkontrollen):
  score >= SCHWELLE_JA (4)       -> `ja`
  score == SCHWELLE_GRENZ (3)    -> `grenzfall`
  sonst                          -> `nein`
`dominus` ist immer `ja` (Fall ZITAT laut Thread, ABG_407050_3). Der Score
wird trotzdem berechnet und ausgegeben.

Der Vorschlag ist heuristisch. Er sieht keine Grammatik, nur Nachbarschaft:
ein Zitat in einer Handschrift ohne Lemmatisierung der Umgebung wird hoch
bewertet, ein kurzes lateinisches Zitat in dicht lemmatisierter Umgebung
niedrig. Entscheiden tut KZW.

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

# (d) Nachbar haengt an einem Lemma mit Sprachkonzept Lateinisch
KONZEPT_LATEIN = 'concept_23123100'
LATEIN_LEMMAS = set()   # wird in pruefe_lexikon gefuellt
# Lemmata mit Konzept Lateinisch, die kein Zitat anzeigen: die im Thread
# (Kommentar 09.10.2026) als "sicher entlehnt" und "sicher nicht fremd"
# gefuehrten Lemmata sowie schrift und nase (Gleis-1-Rauschen). Grossgeschriebene
# Lemmata (Namen) zaehlen ohnehin nicht.
D_AUSSCHLUSS = set('niht in name minner mort zunge engel lewe creatura item '
                   'bischof schrîben klâr natûre kriuze missa marter abbet '
                   'schrift nase kriuze rote baniere soldân fîn'.split())
D_HOMOGRAPH = set('in ad a me nos an'.split())

FENSTER_SCORE = 4
FENSTER_KONTEXT = 8
SCHWELLE_JA = 4
SCHWELLE_GRENZ = 3


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


def score(ws, i):
    """(score, a, b, c) fuer das Wort an Index i; ws = Liste (form, ids)."""
    gesamt = 0
    nur_b = 0
    for j in range(max(0, i - FENSTER_SCORE), min(len(ws), i + FENSTER_SCORE + 1)):
        if j == i:
            continue
        form, ids = ws[j]
        a = ids is None
        c = bool(ids) and bool(ids & ZITAT_LEMMAS)
        d = bool(ids) and bool(ids & LATEIN_LEMMAS) and norm(form) not in D_HOMOGRAPH
        b = norm(form) in LATEIN_FUNKTION
        if a or c or d:
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(OUT))
    ap.add_argument('--verteilung', metavar='LEMMA',
                    help='zusaetzlich die Verteilung dieses Lemmas je Sigle ausgeben')
    args = ap.parse_args()
    pruefe_lexikon()

    zeilen = []
    # Zaehler je Anzeigename; et fasst lemma_1732 und lemma_78608 zusammen
    zaehl = {}
    je_sigle = {}
    dateien = sorted((REPO / 'tei').glob('*.tei.xml'))
    if not dateien:
        sys.exit('FEHLER: keine TEI-Dateien gefunden')
    for pfad in dateien:
        sigle = pfad.name[:-len('.tei.xml')]
        root = etree.parse(str(pfad)).getroot()
        ws = []
        elems = []
        for w in root.iter(TEI + 'w'):
            form = ''.join(w.itertext()).strip()
            ws.append((form, lemma_ids(w)))
            elems.append(w)
        for i, (form, ids) in enumerate(ws):
            if not ids:
                continue
            for lid in sorted(ids & set(ZIELE)):
                lemma = ZIELE[lid]
                sc = score(ws, i)
                vs = vorschlag(lid, sc)
                z = zaehl.setdefault(lemma, Counter())
                z['gesamt'] += 1
                z[vs] += 1
                je_sigle.setdefault((lemma, sigle), Counter())[vs] += 1
                if vs == 'nein':
                    continue
                lo = max(0, i - FENSTER_KONTEXT)
                teile = [f for f, _ in ws[lo:i]] + ['**' + form + '**'] + \
                        [f for f, _ in ws[i + 1:i + 1 + FENSTER_KONTEXT]]
                zeilen.append([sigle, elems[i].get(XML_ID), lemma, lid, form, vs, sc,
                               ' '.join(teile)])

    with open(args.out, 'w', encoding='utf-8', newline='') as f:
        wr = csv.writer(f, lineterminator='\n')
        wr.writerow(['sigle', 'xml_id', 'lemma', 'lemma_id', 'form',
                     'vorschlag_latein', 'latein_score', 'kontext'])
        wr.writerows(zeilen)

    for lemma in ['dominus', 'et', 'engel', 'lewe', 'creatura', 'item']:
        z = zaehl.get(lemma, Counter())
        print(f"{lemma}: {z['gesamt']} Belege, ja {z['ja']}, grenzfall {z['grenzfall']}, nein {z['nein']}")
    if args.verteilung:
        for (lemma, sigle), z in sorted(je_sigle.items()):
            if lemma == args.verteilung:
                n = sum(z.values())
                print(f"  {lemma} {sigle}: {n} Belege, ja {z['ja']}, grenzfall {z['grenzfall']}, nein {z['nein']}")
    print(f"CSV:{len(zeilen)} Zeilen (ja plus grenzfall) nach {args.out}")


if __name__ == '__main__':
    main()
