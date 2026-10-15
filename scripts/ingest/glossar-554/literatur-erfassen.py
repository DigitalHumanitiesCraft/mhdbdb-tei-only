"""Erfasst die in den Glossar-Kommentaren (Notizen von contrib_003 in lexicon.xml) zitierte Literatur
(#554, Paket 5) und schreibt ingest/glossar-554/literatur.tsv.

Aufruf (aus der Repositoriumswurzel): python -X utf8 -E -P scripts/ingest/glossar-554/literatur-erfassen.py [--schreiben]

Eine Zeile je Werk und Kommentar. Die Werkeliste unten ist Handarbeit nach Lektüre aller Kommentare,
das Muster je Werk ist ein Regex auf den Kommentartext. Primärquellen (Dichtung, Rezepttexte) zählen
nicht. Ungeprüft: die Spalte `art` ist die Einordnung der Spur, nicht die der Autorin; die Liste ist eine Untergrenze (ein Werk, dessen Name in keinem Muster steht, fehlt),
und Jahr/Seite stehen nur, wenn sie im selben Satz im Kommentar stehen.
"""
import re, html, sys, collections, os

s = open('authority-files/lexicon.xml', encoding='utf-8').read()
notes = []
for m in re.finditer(r'<entry xml:id="(lemma_\d+)">(.*?)</entry>', s, re.S):
    lid, body = m.group(1), m.group(2)
    orth = re.search(r'<orth>(.*?)</orth>', body).group(1)
    for sm in re.finditer(r'<sense xml:id="([^"]+)"[^>]*>(.*?)</sense>', body, re.S):
        for nm in re.finditer(r'<note type="comment"[^>]*contrib_003">(.*?)</note>', sm.group(2), re.S):
            notes.append({'lemma': lid, 'orth': html.unescape(orth), 'sense': sm.group(1), 'text': html.unescape(nm.group(1))})
QU = 'Quelle: Glossar Kochbuchforschung dig_ESTivum von Katharina Zeppezauer-Wachauer (2016-2026)'
AUS = 'ingest/glossar-554/literatur.tsv'

# (id, verfasser, kurztitel, jahr, art, regex)
W = [
 ('bleuler', 'Anna Kathrin Bleuler', 'Bleuler (alimentäre Codes in der Literatur)', '2016', 'Forschung', r'Bleuler'),
 ('lexer', 'Matthias Lexer', 'Mittelhochdeutsches Handwörterbuch (Lexer)', '', 'Nachschlagewerk', r'Lexer(?!s? Rennewart)|Matthias Lexer'),
 ('bmz', 'Benecke, Müller, Zarncke', 'Mittelhochdeutsches Wörterbuch (BMZ)', '', 'Nachschlagewerk', r'Benecke|\bBMZ\b|Müller,? und Zarncke'),
 ('mwb', 'Akademie Mainz u. a.', 'Mittelhochdeutsches Wörterbuch (MWB)', '', 'Nachschlagewerk', r'\bMWB\b'),
 ('findebuch', 'Kurt Gärtner u. a.', 'Findebuch zum mittelhochdeutschen Wortschatz', '', 'Nachschlagewerk', r'Findebuch|FindeB'),
 ('dwb', 'Jacob und Wilhelm Grimm', 'Deutsches Wörterbuch (DWB)', '', 'Nachschlagewerk', r'Grimm|\bDWB\b|Deutsche[sn] Wörterbuch'),
 ('dwds', 'DWDS', 'Digitales Wörterbuch der deutschen Sprache', '', 'Web', r'DWDS'),
 ('ewd', 'Wolfgang Pfeifer', 'Etymologisches Wörterbuch des Deutschen', '', 'Nachschlagewerk', r'Etymologische[sn] Wörterbuch|Pfeifer'),
 ('fnhdwb', 'Anderson, Goebel, Reichmann u. a.', 'Frühneuhochdeutsches Wörterbuch', '', 'Nachschlagewerk', r'Frühneuhochdeutsche[sn] Wörterbuch'),
 ('kfnhdwb', 'Christa Baufeld', 'Kleines Frühneuhochdeutsches Wörterbuch', '', 'Nachschlagewerk', r'Baufeld|Kleinen Frühneuhochdeutschen'),
 ('pfwb', 'Pfälzisches Wörterbuch', 'Pfälzisches Wörterbuch', '', 'Nachschlagewerk', r'Pfälzische[sn] Wörterbuch|PfWB'),
 ('rhwb', 'Rheinisches Wörterbuch', 'Rheinisches Wörterbuch', '', 'Nachschlagewerk', r'Rheinische[sn] Wörterbuch'),
 ('elsmw', 'Martin und Lienhart', 'Wörterbuch der Elsässischen Mundart', '', 'Nachschlagewerk', r'Elsässischen Mundart'),
 ('bwb', 'Bayerische Akademie der Wissenschaften', 'Bayerisches Wörterbuch (BWB)', '', 'Nachschlagewerk', r'\bBWB\b|Bayerischen? Wörterbuch'),
 ('schmeller', 'Johann Andreas Schmeller', 'Bayerisches Wörterbuch', '1827', 'Nachschlagewerk', r'Schmeller'),
 ('adelung', 'Johann Christoph Adelung', 'Grammatisch-kritisches Wörterbuch', '', 'Nachschlagewerk', r'Adelung'),
 ('kunde', 'Heinz Küpper', 'Wörterbuch der deutschen Umgangssprache', '', 'Nachschlagewerk', r'Küpper'),
 ('frisch', 'Johann Leonhard Frisch', 'Teutsch-Lateinisches Wörterbuch', '1741', 'Nachschlagewerk', r'Frisch'),
 ('krunitz', 'Johann Georg Krünitz', 'Oekonomische Encyklopädie', '', 'Nachschlagewerk', r'Krünitz'),
 ('koebler', 'Gerhard Köbler', 'Wörterbuch', '', 'Nachschlagewerk', r'Köbler'),
 ('friedrich', 'Friedrich', 'Phraseologisches Wörterbuch des Mittelhochdeutschen', '', 'Nachschlagewerk', r'Phraseologische[sn] Wörterbuch'),
 ('pelzlex', 'Pelzlexikon', 'Pelzlexikon', '', 'Nachschlagewerk', r'Pelzlexikon'),
 ('wikipedia', 'Wikipedia', 'Pfaffenschnittchen', '', 'Web', r'Wikipedia'),
 ('klug', 'Helmut W. Klug', 'Medieval Plants Survey (MPS) / Rezeptdatenbank', '', 'Web', r'\bKlug\b|Medieval Plants|\bMPS\b|Rezeptdatenbank'),
 ('wortschaetze', 'Christa Binder / Institut für Germanistik Graz', 'WortSchätze (Belegdatenbank)', '2007', 'Web', r'WortSchätze|Binder'),
 ('hanauska', 'Hanauska', 'Hanauska (online)', '2008', 'Web', r'Hanauska'),
 ('gloning', 'Thomas Gloning', 'Gloning (Edition Rezepte)', '1998', 'Edition', r'Gloning'),
 ('zeppezauer', 'Zeppezauer-Wachauer', 'Zeppezauer-Wachauer', '2017', 'Forschung', r'Zeppezauer'),
 ('schulz', 'Anne Schulz', 'Essen und Trinken im Mittelalter (1000–1300)', '2011', 'Forschung', r'Schulz'),
 ('pieth', 'Willi Pieth', 'Pieth', '1909', 'Forschung', r'Pieth'),
 ('hepp', 'Eva Hepp', 'Hepp', '1970', 'Forschung', r'Hepp'),
 ('sorbello', 'Sorbello Staub', 'Sorbello Staub', '2002', 'Edition', r'Sorbello'),
 ('adamson', 'Melitta Weiss Adamson', 'Adamson', '2000', 'Edition', r'Adamson'),
 ('hofmeister_w', 'Wernfried Hofmeister', 'Hofmeister (Zwillingsformel)', '2009', 'Forschung', r'Wernfried Hofmeister|Hofmeister 2009|Hofmeister,? (?:Sp|S)\.'),
 ('hofmeister_a', 'Andrea Hofmeister', 'Hofmeister (Vorarbeiten)', '', 'Forschung', r'Andrea Hofmeister'),
 ('olt', 'Reinhard Olt', 'Olt (Ausgabe König vom Odenwald)', '', 'Edition', r'\bOlt'),
 ('schichta', 'Gabriele Schichta', 'Schichta (IMAREAL)', '', 'Forschung', r'Schichta'),
 ('schroeder', 'Edward Schröder', 'Schröder (Ausgaben)', '1900', 'Edition', r'Schröder'),
 ('keinz', 'Friedrich Keinz', 'Helmbrecht-Ausgabe', '1865', 'Edition', r'Keinz'),
 ('heyne', 'Moriz Heyne', 'Das deutsche Nahrungswesen', '1901', 'Forschung', r'Heyne'),
 ('panzer', 'Friedrich Panzer, Kurt Ruh', 'Helmbrecht-Ausgabe', '', 'Edition', r'Panzer'),
 ('schiffmann', 'Konrad Schiffmann', 'Studien zum Helmbrecht', '1918', 'Forschung', r'Schiffmann'),
 ('stoewer', 'Stöwer', 'Stöwer', '', 'Forschung', r'Stöwer'),
 ('scherer', 'Wilhelm Scherer', 'Scherer', '1870', 'Forschung', r'Scherer'),
 ('yao', 'Shao-Ji Yao', 'Yao', '', 'Forschung', r'Shao-Ji Yao'),
 ('feyl', 'Feyl', 'Feyl', '1963', 'Forschung', r'Feyl'),
 ('zingerle', 'Zingerle', 'Zingerle', '', 'Forschung', r'Zingerle'),
 ('barton', 'Barton', 'Barton', '', 'Forschung', r'Barton'),
 ('grafetstaetter', 'Grafetstätter', 'Grafetstätter', '', 'Forschung', r'Grafetstätter'),
 ('nellmann', 'Eberhard Nellmann', 'Nellmann', '', 'Edition', r'Nellmann'),
 ('weick', 'Weick', 'Ornithologie und Philologie', '1989', 'Forschung', r'Weick'),
 ('loehneysen', 'Georg Engelhard von Löhneysen', 'Löhneysen', '', 'Forschung', r'Löhneysen'),
 ('blaschitz', 'Gertrud Blaschitz', 'Blaschitz', '', 'Forschung', r'Blaschitz'),
 ('simrock', 'Karl Simrock', 'Simrock (Übersetzung)', '1883', 'Forschung', r'Simrock'),
 ('luehr', 'Lühr', 'Lühr', '', 'Forschung', r'Lühr'),
 ('stosch', 'Stosch', 'Stosch', '1786', 'Forschung', r'Stosch'),
 ('kern', 'Kern', 'Kern', '', 'Forschung', r'\bKern,? S\. ?\d|Kern \('),
 ('birlinger', 'Anton Birlinger', 'Birlinger', '1876', 'Forschung', r'Birlinger'),
 ('becker', 'Becker', 'Becker', '1993', 'Forschung', r'Becker'),
 ('lemmer', 'Lemmer-Harsch', 'Lemmer-Harsch', '', 'Forschung', r'Lemmer'),
 ('bech', 'Bech', 'Bech', '', 'Forschung', r'\bBech\b'),
 ('schubert', 'Ernst Schubert', 'Schubert', '', 'Forschung', r'Schubert'),
 ('strauch', 'Strauch', 'Strauch (Ausgabe)', '', 'Edition', r'Strauch'),
 ('schacht', 'Th. Schacht', 'Schacht', '1846', 'Forschung', r'Schacht'),
 ('hausner', 'Renate Hausner', 'Hausner', '', 'Forschung', r'Hausner'),
 ('neumann', 'Alfred Neumann', 'Neumann', '', 'Forschung', r'Alfred Neumann|\bNeumann\b'),
 #('moelleken', 'Moelleken', 'Moelleken (Stricker)', '', 'Forschung', r'Moelleken'),
 ('berendes', 'Julius Berendes', 'Physica (Hildegard von Bingen)', '', 'Edition', r'Berendes'),
 ('steinbauer', 'Bernd Steinbauer', 'Der Wein in der Literatur', '', 'Forschung', r'Steinbauer'),
 ('kuehtreiber', 'Kühtreiber', 'Kühtreiber', '2006', 'Forschung', r'Kühtreiber'),
 ('pohl', 'Heinz Dieter Pohl', 'Pohl', '', 'Forschung', r'Pohl'),
 ('leitzmann', 'Leitzmann, Wolff, Gärtner', 'Erec (Wolfenbütteler Fragment)', '2006', 'Edition', r'Leitzmann'),
 ('meyer', 'Meyer', 'Meyer (Jüngerer Titurel)', '', 'Forschung', r'\bMeyer\b'),
 ('huschenbett', 'Dietrich Huschenbett', 'Huschenbett', '', 'Forschung', r'Huschenbett'),
 ('borst', 'Borst', 'Borst (Rechnungsbuch Klosterneuburg)', '', 'Forschung', r'Borst'),
 ('koppitz', 'Alfred Koppitz', 'Göttweiger Trojanerkrieg', '', 'Edition', r'Koppitz'),
 ('gervinus', 'Georg Gottfried Gervinus', 'Gervinus (zit. nach Neumann)', '', 'Forschung', r'Gervinus'),
 ('falke', 'Jacob von Falke', 'Falke (zit. nach Neumann)', '', 'Forschung', r'Falke'),
]


ABK = {'S', 'V', 'Sp', 'Nr', 'Str', 'Anm', 'Komm', 'bzw', 'vgl', 'Z', 'Bd', 'Hs', 'fol', 'u', 'a', 'd', 'h', 'B', 'z', 'etc', 'usw', 'ca', 'Jh', 'Hrsg', 'hrsg', 'zit', 'St', 'Dr', 'lehrb', 'sprichw', 'Ed', 'Cod', 'Nrn', 'ff', 'f', 'm', 'o', 'II', 'III', 'I', 'K', 'W', 'H', 'J', 'M', 'E', 'A', 'C', 'T', 'P', 'R', 'L', 'G', 'F', 'N', 'D'}


def grenzen(t):
    g = [0]
    for m in re.finditer(r'([.?!])(?=\s+[„"A-ZÄÖÜ\[‚(])', t):
        w = re.search(r'(\w+)$', t[:m.start()])
        if m.group(1) == '.' and (not w or w.group(1) in ABK or w.group(1).isdigit() and False):
            continue
        g.append(m.end())
    g.append(len(t))
    return g


# Bezeichnung nur dort, wo der Kommentartext den Titel selbst nennt; sonst steht der Name, wie er im Text steht.
TITEL = {
    'kunde': 'Küpper, Wörterbuch der deutschen Umgangssprache',
    'weick': 'Weick, Ornithologie und Philologie',
    'steinbauer': 'Steinbauer, Der Wein in der Literatur',
    'birlinger': 'Birlinger, Zur altdeutschen Küchensprache',
    'heyne': 'Heyne, Das deutsche Nahrungswesen',
    'kfnhdwb': 'Baufeld, Kleines Frühneuhochdeutsches Wörterbuch',
    'friedrich': 'Friedrich, Phraseologisches Wörterbuch des Mittelhochdeutschen',
    'schiffmann': 'Schiffmann, Studien zum Helmbrecht',
    'lexer': 'Lexer, Mittelhochdeutsches Handwörterbuch',
    'bmz': 'Benecke, Müller, Zarncke, Mittelhochdeutsches Wörterbuch',
    'findebuch': 'Findebuch zum mittelhochdeutschen Wortschatz',
    'klug': 'Klug, Medieval Plants / Rezeptdatenbank',
    'wortschaetze': 'WortSchätze (Binder)',
    'berendes': 'Berendes (Physica)',
    'koppitz': 'Koppitz (Der Göttweiger Trojanerkrieg)',
    'leitzmann': 'Leitzmann, Wolff, Gärtner',
    'wikipedia': 'Wikipedia, Pfaffenschnittchen',
    'ewd': 'Etymologisches Wörterbuch (Pfeifer, zit. nach DWDS)',
    'dwb': 'Grimm, Deutsches Wörterbuch (DWB)',
    'mwb': 'MWB',
    'kern': 'Kern',
    'elsmw': 'Wörterbuch der Elsässischen Mundart',
    'pfwb': 'Pfälzisches Wörterbuch (PfWB)',
    'bwb': 'Bayerisches Wörterbuch (BWB)',
    'fnhdwb': 'Frühneuhochdeutsches Wörterbuch',
    'hofmeister_w': 'Wernfried Hofmeister',
    'hofmeister_a': 'Andrea Hofmeister',
    'neumann': 'Alfred Neumann',
}


def satz(t, m):
    g = grenzen(t)
    a = max(x for x in g if x <= m.start())
    b = min(x for x in g if x >= m.end() and x > a)
    s = t[a:b].strip()
    if len(s) > 400:
        c = m.start() - a
        lo = max(0, c - 180)
        hi = min(len(s), c + 220)
        s = ('… ' if lo else '') + s[lo:hi] + (' …' if hi < len(s) else '')
    return s


rows = []
ERSTE = {}
for wid, vf, kt, jr, art, rx in W:
    r = re.compile(rx)
    for i, n in enumerate(notes):
        t = n['text'].replace(QU, '').strip()
        ms = list(r.finditer(t))
        if not ms:
            continue
        sa = satz(t, ms[0])
        jahre = ';'.join(dict.fromkeys(re.findall(r'\b(?:1[0-9]|20)\d\d\b', sa)))
        rows.append((i, wid, TITEL.get(wid) or ERSTE.setdefault(wid, re.sub(r'[,(]?\s*S\.\s*$', '', ms[0].group(0)).strip()), art, n['orth'], n['lemma'], ms[0].group(0), jahre, sa.replace('\t', ' ').replace('\n', ' ')))
KOPF = ('werk_id', 'werk', 'art', 'lemma', 'lemma_id', 'treffer_im_text', 'jahre_im_satz', 'ausschnitt')
nw = len({r[1] for r in rows})
nk = len({r[0] for r in rows})
print('Zeilen %d, Werke %d, Kommentare mit mindestens einem Zitat %d von %d' % (len(rows), nw, nk, len(notes)))
print('Werke je Art:', dict(collections.Counter(dict((r[1], r[3]) for r in rows).values())))
if '--schreiben' in sys.argv:
    with open(AUS, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(KOPF) + '\n')
        for r in sorted(rows, key=lambda r: (r[1], r[5])):
            f.write('\t'.join(r[1:]) + '\n')
    print('geschrieben:', AUS)
