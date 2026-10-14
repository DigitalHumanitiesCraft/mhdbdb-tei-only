# -*- coding: utf-8 -*-
"""#554 B1: Bedeutungszuordnung fuer die 189 Glossar-Eintraege (gmh).

Liest die Zuordnung aus PR #559 (ingest/glossar-554/zuordnung-eindeutig.tsv und
pruefliste.tsv), das Lexikon (Bedeutungen je Lemma) und den bereinigten Export
und schreibt ingest/glossar-554/zuordnung.tsv: je Glossar-Eintrag Lemma,
Bedeutung und vorlaeufigen Ausgang mit Grund. Keine Aenderung an Daten.

Die Entscheidungen stehen unten als Tabellen, jede mit ihrem Grund. Sie sind
von Hand am Inhalt des Glossartexts, an den Konzepten der Bedeutungen und an
den Korpusbelegen getroffen (Stand 14.10.2026), nicht berechnet. Der Rest
(Lemma mit genau einer Bedeutung) ist mechanisch.

Ausgaenge:
  zugeordnet   Lemma und Bedeutung stehen fest, ein Text ist vorhanden
  pruefseite   Zuordnung bleibt nach der Vorpruefung unklar (Pruefseite fuer KZW)
  kein-kommentar  es geht kein Kommentar ins Lexikon (Grund in der Spalte)
"""
import csv
import sys
from collections import Counter
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glossar_export import ROOT, WP, parse_export, lemma_items  # noqa: E402

T = '{http://www.tei-c.org/ns/1.0}'
XID = '{http://www.w3.org/XML/1998/namespace}id'
EXPORT = ROOT / 'sources/glossar-kochbuchforschung/digest_ivum.wordpress.2026-10-08.bereinigt.xml'
OUT = ROOT / 'ingest/glossar-554/zuordnung.tsv'

# --- Lemma mit mehreren Bedeutungen, Zuordnung entschieden: id -> (Nr., Grund) ---
MULTI = {
    '252': (4, 'Text handelt von der Verengung zum Gastgeber/Wirt; nur Bedeutung 4 traegt Gastgewerbe (1430 Belege)'),
    '280': (2, 'Text handelt von der Gastgeberin/Wirtin; Bedeutung 2 traegt Ernaehrung und Hilfeleistung, wie bei wirt'),
    '579': (5, 'Futtertrog/Krippe; Bedeutung 5 (Ernaehrung, Viehhaltung) mit Beleg "gelabete in den barn" (PZ)'),
    '596': (1, 'Biss/Bissen; Bedeutung 1 traegt alle 11 Belege und die Ernaehrung, Bedeutung 2 (Tiere) hat keinen'),
    '606': (2, 'Braten als Speise; Bedeutung 2 (Fleisch, Speisen, 31 Belege), Bedeutung 1 sind Koerperteile'),
    '666': (1, 'verdauen; Bedeutung 1 (Stoffwechsel, 3 Belege), das Glossar kennt nur diese NHD-Entsprechung'),
    '697': (1, 'verstaerkende Praefixform "essend"; Bedeutung 1 traegt 119 Belege, die uebrigen keinen'),
    '766': (3, 'nicht ernaehren; nur Bedeutung 3 traegt Ernaehrung von Menschen'),
    '962': (3, 'Krapfen als Gebaeck; Bedeutung 3 Backwaren, die anderen vier sind kein Gebaeck'),
    '1168': (1, 'Erste Lesart Leibesnahrung (83 Belege); die zweite Lesart Kostgeld steht im Text als Alternative'),
    '1254': (1, 'maesten, fuettern; Bedeutung 1 (Viehzucht, 32 Belege)'),
    '1266': (1, 'Milch/Molke; Bedeutung 1 (Milchprodukte); Muttermilch (Bedeutung 2) nennt der Text nur als selteneren Fall'),
    '1297': (1, 'woertlich Nahrung/Speise (erste Lesart); die uebertragene Lesart steht im Text als Erweiterung'),
    '1493': (1, 'Koeder/Lockspeise; Bedeutung 1 (Jagd/Fischerei, 6 Belege), Bedeutung 2 ist Kleidung'),
    '1952': (3, 'Gewuerznelke; nur Bedeutung 3 traegt Gewuerzpflanzen und Zutaten'),
    '2074': (2, 'Ei als Speise; Bedeutung 2 (Voegel, Lebensmittel, Eier, 99 Belege)'),
    '2415': (1, 'kemenate; Bedeutung 1 (Gebaeude, 29 Belege), Bedeutung 2 (Rechtswesen) kann nicht gemeint sein'),
}

# --- Lemma mit mehreren Bedeutungen, Zuordnung bleibt unklar: id -> Grund ---
MULTI_PRUEF = {
    '178': 'Pfruende: Mahlzeit fuer Kleriker (Bedeutung 2) oder Versorgungsstelle/Lehen (Bedeutungen 4, 5); der Text beschreibt den Weg von der einen zur anderen',
    '225': 'wanne: der Text nennt Kornschwinge, Viehtrog und Gefaess; keine der vier Bedeutungen traegt Getreide',
    '432': 'abebizen: der Text nennt als Hauptfall das Abbeissen eines Koerpergliedes (Bedeutung 2, 0 Belege), die Belege stehen aber unter Bedeutung 1',
    '911': 'genern: der Text nennt heilen/schuetzen zuerst und ernaehren erst spaeter (Bedeutungen 1 und 2)',
    '1121': 'koste: der Text nennt zwei gleichrangige Hauptbedeutungen, pekuniaer (Bedeutung 1) und kulinarisch (Bedeutung 2)',
    '1146': 'lecken: der Text nennt abschlecken/benetzen zuerst und das kulinarische Aufschlecken als selteneren Fall (Bedeutungen 1 und 2)',
    '1159': 'letzen: der Text nennt Abschied nehmen (Bedeutung 4, 0 Belege) und die Verschiebung zur Ernaehrung (Bedeutung 1)',
    '1328': 'naschen: Bedeutung 1 (Erotik) und 2 (Genussmittel), beide ohne Beleg; der Text behandelt beide gleich ausfuehrlich',
    '1331': 'kleibasche: Bedeutung 1 (Boden, einziger Beleg) oder 2 (Lebensmittel, kein Beleg); der Text diskutiert beide Lesarten',
    '1438': 'nuehtern: der Text nennt nichts gegessen (Bedeutung 1) und nicht betrunken (Bedeutung 2) gleichrangig',
    '1439': 'kerne: Wesen/Kern (Bedeutungen 3, 4), Getreidekorn (1), Nusskern (5); der Text belegt alle',
    '1821': 'slunt: der Text fuehrt drei Bedeutungen auf und beschreibt ihr Verschmelzen im Ackermann',
    '2318': 'hut: der Text nennt Tierhaut im Allgemeinen und gebratene Huehnerhaut (Bedeutungen 3, 4, 9)',
}

# --- Kein Kommentar bei den 159, mit Grund: id -> (Grund-Kennung, Grund) ---
KEIN_159 = {
    '560': ('lemma-passt-nicht', 'Das Lemma "Atze" ist ein Personenname, der Eintrag meint das Appellativ; der Text ist nur ein Verweis'),
    '539': ('verweis', 'Der Text ist nur der Verweis auf den Eintrag atzen'),
    '1434': ('verweis', 'Der Text ist nur der Verweis auf den Eintrag genieszen'),
    '1571': ('verweis', 'Verweis auf den Eintrag sat mit einer Formbemerkung (saten gegen gesaten) ohne eigene Aussage zur Sache'),
    '1596': ('verweis', 'Verweis auf die Eintraege sat und seten mit der Formbemerkung, setigen sei eine spaetere Form'),
    '1984': ('verweis', 'Der Text ist nur der Verweis auf den Eintrag wilt; die Poetisierung ist ebenfalls ein Verweis'),
    '797': ('poetisierung-ohne-mehrwert', 'Poetisierung gibt nur die zwei Bedeutungen wieder, die das Lexikon schon fuehrt'),
    '1426': ('poetisierung-ohne-mehrwert', 'Poetisierung gibt nur die zwei Bedeutungen wieder, die das Lexikon schon fuehrt'),
    '1813': ('poetisierung-ohne-mehrwert', 'Poetisierung ist ein Belegzitat mit Uebersetzung, ohne weitere Aussage'),
    '1611': ('bedeutungsliste', 'Das Feld nennt nur die zwei Bedeutungen, die das Lexikon schon fuehrt'),
    '331': ('poetisierung-ohne-mehrwert', 'Poetisierung nennt eine Stelle (Tod als Begleiter) ohne weitere Aussage; die Belegstelle steht unter Bedeutung 1, die Lesart waere Bedeutung 2'),
}

# --- Die 30 der Pruefliste: id -> (Ausgang, Lemma, Bedeutungsnr., Grund-Kennung, Grund) ---
PL = {
    '93': ('pruefseite', None, None, 'homograph', 'Ohm (Volumenmass): die drei Kandidaten "aeme" (Nomen), "Ame" (Name) und lat. "ame" sind je einmal belegt; ob die Stelle das Mass meint, laesst sich am Beleg nicht entscheiden'),
    '103': ('pruefseite', 'lemma_32468', 1, 'zweiter-eintrag', 'briech (Adj. breiig) ist im Korpus eine Form von bri; bri hat einen eigenen Glossar-Eintrag, das Lemma nur eine Bedeutung und damit eine Notiz'),
    '130': ('zugeordnet', 'lemma_16993', 1, '', 'ungelabet ist im Korpus Form von enlaben (variants.xml, beide Belege); das Lemma hat eine Bedeutung'),
    '135': ('kein-kommentar', None, None, 'kein-inhalt', 'Weder Enzyklopaedische Information noch Poetisierung'),
    '536': ('zugeordnet', 'lemma_36833', 1, '', 'atzen ist im Korpus Form von etzen (variants.xml, Belege azte/acz); Bekoestigung von Menschen = Bedeutung 1, Bedeutung 2 meint zusaetzlich Viehhaltung'),
    '621': ('zugeordnet', 'lemma_829', 1, '', 'braeten (239 Belege, eine Bedeutung); das andere Lemma "braten" hat einen Beleg'),
    '694': ('kein-kommentar', 'lemma_1383', 1, 'dublette', 'Spiegelt die Aussage von Eintrag 697 (enbizen) mit denselben Worten; die Poetisierung ist bis auf das Zeichen gleich'),
    '721': ('kein-kommentar', None, None, 'poetisierung-ohne-mehrwert', 'Poetisierung gibt die Bedeutung wieder und vermerkt, dass Lexer und BMZ eine andere Bedeutung kennen, die hier nicht verfolgt wird'),
    '747': ('kein-kommentar', None, None, 'poetisierung-ohne-mehrwert', 'Poetisierung gibt nur die Bedeutung wieder'),
    '777': ('kein-kommentar', None, None, 'poetisierung-ohne-mehrwert', 'Poetisierung gibt die Bedeutung wieder und nennt eine Stelle'),
    '1475': ('zugeordnet', 'lemma_23230', 1, '', 'oblei (45 Belege, eine Bedeutung); der Beleg HTR "pfaffen oblei und kloster ampt" passt zur Abgabe an kirchliche Einrichtungen'),
    '1525': ('zugeordnet', 'lemma_5122', 2, '', 'sat (Adjektiv, nicht "saet" Nomen); Bedeutung 2 traegt Ernaehrung (14 Belege), der Text nennt satt zuerst'),
    '1759': ('pruefseite', 'lemma_25919', 1, 'name-oder-appellativ', 'Der Text trennt den Namen Slinthart vom Appellativ slunthart; vorhanden ist nur das Namenlemma, das schon einen eigenen Eintrag hat'),
    '1442': ('pruefseite', 'lemma_5158', None, 'bedeutung-offen', 'Schale: das Lemma schal hat 15 Bedeutungen; der Text nennt Tafelgeschirr (7), Eierschale (15), Pflanzenhuelse (8) und weitere'),
    '1913': ('zugeordnet', 'lemma_518', 1, '', 'ber (108 Belege, eine Bedeutung); die beiden anderen Lemmata haben je einen Beleg'),
    '2009': ('zugeordnet', 'lemma_7758', 3, '', 'zam als Nomen (Nutztier); Bedeutung 3 Haustiere/Nutztiere, 10 Belege'),
    '1703': ('kein-kommentar', None, None, 'lemma-fehlt', 'Kein Lemma "herren ezzen" im Bestand'),
    '1900': ('zugeordnet', 'lemma_2961', 1, 'zweiter-eintrag', 'henne ist im Korpus Form von huon (variants.xml); die Enzyklopaedische Information ist wortgleich mit der von huon, die Poetisierung eigen'),
    '2017': ('kein-kommentar', None, None, 'verweis', 'Der Text ist nur der Verweis auf zam (Nomen)'),
    '2116': ('kein-kommentar', None, None, 'lemma-fehlt', 'Kein Lemma blancmanger im Bestand; der Text verweist auf blamensier'),
    '2158': ('kein-kommentar', None, None, 'lemma-fehlt', 'Kein Lemma "lerchen fuoz" im Bestand'),
    '2248': ('kein-kommentar', 'lemma_4565', 1, 'dublette', 'Die Texte von pardris (2241) und pardrisekin sind zu 99 bis 100 Prozent gleich'),
    '2264': ('zugeordnet', 'lemma_21938', 1, 'zweiter-eintrag', 'rephenne ist im Korpus Form von rephuon (variants.xml); die Enzyklopaedische Information ist nur ein Verweis, die Poetisierung eigen'),
    '2324': ('zugeordnet', 'lemma_14782', 1, '', 'diech Nomen (32 Belege, Oberschenkel); das andere Lemma ist Artikel/Pronomen "die ich"'),
    '2332': ('zugeordnet', 'lemma_60328', 1, '', 'phaffensniz: der Beleg KVO "pfaffensnitze" ist genau die Form des Glossars'),
    '2502': ('zugeordnet', 'lemma_48749', 1, '', 'ascherkuoche: der Beleg FLG "eschekuochen" ist genau die Form des Glossars'),
    '2587': ('kein-kommentar', None, None, 'kein-inhalt', 'Weder Enzyklopaedische Information noch Poetisierung'),
    '2625': ('kein-kommentar', None, None, 'kein-inhalt', 'Weder Enzyklopaedische Information noch Poetisierung'),
    '2635': ('kein-kommentar', None, None, 'kein-inhalt', 'Weder Enzyklopaedische Information noch Poetisierung'),
    '2665': ('zugeordnet', 'lemma_62068', 1, '', 'krakeling: der Beleg KVO "grakoelikin" ist genau die Form des Glossars'),
}


def lade_bedeutungen():
    lex = etree.parse(str(ROOT / 'authority-files/lexicon.xml'))
    out = {}
    for e in lex.iter(T + 'entry'):
        out[e.get(XID)] = [s.get(XID) for s in e.findall(T + 'sense')]
    return out


def main():
    tree = parse_export(EXPORT)
    texte = {}
    for it, m in lemma_items(tree, 'publish'):
        if m.get('sprachstufe') == 'gmh':
            texte[it.findtext(WP + 'post_id')] = (
                it.findtext('title'), bool(m.get('Enzyklopädische Information', '').strip()),
                bool(m.get('Poetisierung des Wortes', '').strip()))
    assert len(texte) == 189, len(texte)
    bed = lade_bedeutungen()

    eind = list(csv.DictReader((ROOT / 'ingest/glossar-554/zuordnung-eindeutig.tsv').open(encoding='utf-8'), delimiter='\t'))
    pl_ids = list(dict.fromkeys(r['glossar_id'] for r in csv.DictReader(
        (ROOT / 'ingest/glossar-554/pruefliste.tsv').open(encoding='utf-8'), delimiter='\t')))
    assert len(eind) == 159 and len(pl_ids) == 30
    assert set(pl_ids) == set(PL), set(pl_ids) ^ set(PL)
    assert set(MULTI) | set(MULTI_PRUEF) | set(KEIN_159) <= {r['glossar_id'] for r in eind}

    rows = []
    for r in eind:
        gid, lid = r['glossar_id'], r['lemma_id']
        titel, enz, poet = texte[gid]
        senses = bed[lid]
        hat = enz or poet
        if not hat:
            res = (gid, titel, lid, '', 'kein-kommentar', 'kein-inhalt', 'Weder Enzyklopaedische Information noch Poetisierung')
        elif gid in KEIN_159:
            k, g = KEIN_159[gid]
            res = (gid, titel, lid if k != 'lemma-passt-nicht' else '', '', 'kein-kommentar', k, g)
        elif gid in MULTI_PRUEF:
            res = (gid, titel, lid, '', 'pruefseite', 'bedeutung-offen', MULTI_PRUEF[gid])
        elif gid in MULTI:
            nr, g = MULTI[gid]
            assert len(senses) > 1 and nr <= len(senses), gid
            res = (gid, titel, lid, senses[nr - 1], 'zugeordnet', 'bedeutung-entschieden', 'Bedeutung %d von %d: %s' % (nr, len(senses), g))
        else:
            assert len(senses) == 1, (gid, titel, len(senses))
            res = (gid, titel, lid, senses[0], 'zugeordnet', 'eine-bedeutung', 'Das Lemma hat genau eine Bedeutung')
        rows.append(res)
    for gid in pl_ids:
        titel, enz, poet = texte[gid]
        ausgang, lid, nr, k, g = PL[gid]
        sid = ''
        if lid and nr:
            assert nr <= len(bed[lid]), (gid, lid)
            sid = bed[lid][nr - 1]
        if ausgang == 'zugeordnet':
            assert enz or poet, gid
        rows.append((gid, titel, lid or '', sid, ausgang, k, g))

    assert len(rows) == 189 and len({r[0] for r in rows}) == 189
    rows.sort(key=lambda r: int(r[0]))
    with OUT.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['glossar_id', 'glossar_titel', 'lemma_id', 'sense_id', 'ausgang', 'grund_art', 'grund'])
        w.writerows(rows)
    z = Counter(r[4] for r in rows)
    print('189 Eintraege: %d zugeordnet, %d pruefseite, %d kein-kommentar' % (z['zugeordnet'], z['pruefseite'], z['kein-kommentar']))
    ka = Counter(r[5] for r in rows if r[4] == 'kein-kommentar')
    print('kein Kommentar nach Grund:', ', '.join('%s %d' % kv for kv in sorted(ka.items())))
    print('geschrieben:', OUT.relative_to(ROOT))


if __name__ == '__main__':
    main()
