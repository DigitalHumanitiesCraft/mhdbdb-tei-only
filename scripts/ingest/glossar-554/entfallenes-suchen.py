"""Sucht je Eintrag die Teile der Vorstufe (Glossartext), die im uebernommenen Kommentar fehlen.

Die Vorstufe wird in Absaetze und Saetze zerlegt; ein Stueck gilt als entfallen,
wenn weniger als die Haelfte seiner Wort-Dreiergruppen (normalisiert: ohne
Satzzeichen und Anfuehrungszeichen, kleingeschrieben) und zugleich weniger als
70 % seiner Inhaltswoerter (ab sechs Buchstaben) im neuen Text vorkommen.

Einordnung: Stuecke, die nach Literaturangabe, Link, Abrufdatum oder Bruchstueck
aussehen, werden selbsttaetig als (b) gezaehlt. Alle uebrigen tragen eine
laufende Nummer je Eintrag; die Einordnung steht in
ingest/glossar-554/einordnung.json (je Eintrag: "ab" = Nummern, die nur
Wiederholung, Randbemerkung oder Umformuliertes sind; alle uebrigen Nummern
gelten als (c): eigenstaendige Aussage, Differenzierung, Beleg oder Beispiel).

Aufruf (aus der Repositoriumswurzel):
    python -X utf8 -E -P scripts/ingest/glossar-554/entfallenes-suchen.py <gmh189c.json> [glossar_id ...]
"""
import glob
import json
import re
import sys

AUTO_B = re.compile(
    r'^\[\d+\]|zuletzt (aufgerufen|abgerufen)|https?://|www\.|Verlag|\bHrsg\b|hrsg\. von|'
    r'^\s*Vgl\. |Online-Version|Bd\.|S\. ?\d+|^[A-ZÄÖÜ][^.]{0,60}:\s*$')


def lade_kommentare():
    alle = {}
    for pfad in sorted(glob.glob('ingest/glossar-554/kommentare/*.json')):
        alle.update(json.load(open(pfad, encoding='utf-8')))
    return alle


def norm(s):
    s = s.lower()
    s = re.sub(r'[^\w\s]', ' ', s)
    return s.split()


def dreier(w):
    return {tuple(w[i:i + 3]) for i in range(len(w) - 2)} or {tuple(w)}


def stuecke(text):
    out = []
    for absatz in re.split(r'\n\s*\n|\n', text):
        absatz = absatz.strip()
        if not absatz:
            continue
        for s in re.split(r'(?<=[.!?:])\s+(?=[A-ZÄÖÜ„‚])', absatz):
            s = s.strip()
            if s:
                out.append(s)
    return out


def entfallene(o, k):
    """Liefert (auto_b, offen): Listen der entfallenen Stuecke."""
    quelle = o['enz_t'] + ('\n\n' + o['poet_t'] if k.get('poet') == 'uebernommen' else '')
    neu = dreier(norm(k['text']))
    neuwoerter = set(norm(k['text']))
    auto_b, offen = [], []
    for s in stuecke(quelle):
        w = norm(s)
        if len(w) < 4:
            continue
        d = dreier(w)
        if len(d & neu) / len(d) >= 0.5:
            continue
        inhalt = [x for x in w if len(x) >= 6]
        wortanteil = (sum(1 for x in inhalt if x in neuwoerter) / len(inhalt)) if inhalt else 1.0
        if wortanteil >= 0.7:
            continue
        if len(s) < 25 or AUTO_B.search(s):
            auto_b.append(s)
        else:
            offen.append(s)
    return auto_b, offen


def main():
    vor = {o['id']: o for o in json.load(open(sys.argv[1], encoding='utf-8'))}
    kom = lade_kommentare()
    ids = sys.argv[2:] or sorted(kom, key=int)
    for gid in ids:
        k = kom[gid]
        if k.get('aufgegangen_in'):
            continue
        o = vor[gid]
        auto_b, offen = entfallene(o, k)
        print('===== %s %s | offen %d, selbsttaetig (b) %d' % (gid, o['title'], len(offen), len(auto_b)))
        for i, s in enumerate(offen, 1):
            print('  %d. %s' % (i, s[:170].replace('\n', ' ')))


if __name__ == '__main__':
    main()
