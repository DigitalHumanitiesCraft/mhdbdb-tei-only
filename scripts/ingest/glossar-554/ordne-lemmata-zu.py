#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#554 Schritt 2: Glossar-Eintraege (Sprachstufe gmh) den Lemmata zuordnen.

Schreibt nach ingest/glossar-554/ (alle TSV UTF-8, LF):

  zuordnung-eindeutig.tsv   Glossar-ID -> lemma_N, wo der Titel genau ein Lemma trifft
  pruefliste.tsv            Homographen und Eintraege ohne Treffer, eine Zeile je
                            Kandidat (kein Kandidat: eine Zeile mit leerem lemma_id)
  pruefliste-belege.tsv     je Kandidat bis zu 3 Korpusbelege (Sigle, xml:id, Kontext)

Nichts davon ist eine Entscheidung. Es ist Pruefmaterial; die Zuordnung der
eindeutigen Faelle gilt erst nach einer Stichprobe, denn Titelgleichheit ist
keine Gleichheit der Bedeutung (Homonymie kann auch bei genau einem Lemma
vorliegen, wenn das zweite bei uns fehlt).

Abgleich (exakt, wie im Issue): Titel und Lemma beide ueber norm_titel()
(MHG-Normalisierung des Projekts plus e-Trema und langes z). Kein Abgleich der
Wortart. Fuer die Faelle ohne exakten Treffer werden Kandidaten gesammelt, in
dieser Rangfolge der Art:
  ohne-zusatz  Titel ohne angehaengte Klammer ("zam (adj)" -> "zam") trifft exakt
  variante     der Titel steht in variants.xml als Schreibvariante eines Lemmas
  praefix      Lemma und Titel (normalisiert, je mind. 4 Zeichen) sind
               Anfangsstueck voneinander, Laengenunterschied hoechstens 3
  edit1        Levenshtein-Abstand 1 auf der normalisierten Form, Laenge mind. 5
Je Fall hoechstens MAXK Kandidaten der Arten variante/praefix/edit1, nach Art und
dann nach Belegzahl; ohne-zusatz und exakt werden nie abgeschnitten.

Belegzahl = Zahl der <w> mit diesem Lemma in @lemmaRef, ueber tei/ (Token-genau,
CONTRACTS B.1), nicht das Feld der API.

Usage:
    python -E -P scripts/ingest/glossar-554/ordne-lemmata-zu.py EXPORT.xml [--out ingest/glossar-554]
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glossar_export import (ROOT, WP, parse_export, lemma_items, lade_lemmata,  # noqa: E402
                            norm_titel)
sys.path.insert(0, str(ROOT / 'scripts'))
from corpus_files import corpus_files  # noqa: E402

TEI = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'
MAXK = 8
KONTEXT = 4          # Woerter links und rechts
BELEGE_JE_KANDIDAT = 3
SAMMELN_JE_LEMMA = 60   # erste Vorkommen, aus denen die Auswahl getroffen wird
ART_RANG = {'exakt': 0, 'ohne-zusatz': 1, 'variante': 2, 'praefix': 3, 'edit1': 4}


def kurz(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def levenshtein_leq1(a, b):
    """True, wenn der Abstand genau 1 ist (0 zaehlt nicht: das waere exakt)."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    for i in range(len(b)):
        if b[:i] + b[i + 1:] == a:
            return True
    return False


def lade_varianten():
    """variants.xml: norm(Form) -> {lemma_id: Summe n}. n ist die Zahl der Belege dieser Form."""
    t = etree.parse(str(ROOT / 'authority-files' / 'variants.xml'))
    out = defaultdict(Counter)
    for e in t.iter(TEI + 'entry'):
        lid = (e.get('corresp') or '').split('#')[-1]
        if not lid.startswith('lemma_'):
            raise ValueError('entry ohne lemma-corresp: %r' % e.get('corresp'))
        for f in e.findall(TEI + 'form'):
            out[norm_titel(f.text)][lid] += int(f.get('n') or 0)
    return out


def scanne_korpus(ziel_ids):
    """Eine Runde ueber tei/: Belegzahl je Lemma und Vorkommen fuer ziel_ids.
    Rueckgabe: (Counter lemma_id -> Tokens, dict lemma_id -> [(sigle, xml:id, kontext)])."""
    zahl = Counter()
    belege = defaultdict(list)
    dateien = corpus_files()
    for fp in dateien:
        sigle = fp.name[:-len('.tei.xml')]
        body = etree.parse(str(fp)).find('.//%sbody' % TEI)
        if body is None:
            continue
        ws = list(body.iter(TEI + 'w'))
        formen = None
        for i, w in enumerate(ws):
            ref = w.get('lemmaRef')
            if not ref:
                continue
            for tok in ref.split():
                lid = tok.split('#')[-1]
                zahl[lid] += 1
                if lid in ziel_ids and len(belege[lid]) < SAMMELN_JE_LEMMA:
                    if formen is None:
                        formen = [kurz(''.join(x.itertext())) for x in ws]
                    lo, hi = max(0, i - KONTEXT), min(len(ws), i + KONTEXT + 1)
                    ctx = ' '.join(formen[lo:i] + ['[[%s]]' % formen[i]] + formen[i + 1:hi])
                    belege[lid].append((sigle, w.get(XMLID) or '', ctx))
    print('Korpus gelesen: %d Dateien, %d Tokens mit Lemma-Verweis' % (len(dateien), sum(zahl.values())))
    return zahl, belege


def waehle_belege(liste):
    """Bis zu 3: erst je verschiedene Sigle das erste Vorkommen, dann auffuellen."""
    gewaehlt, gesehen = [], set()
    for b in liste:
        if b[0] not in gesehen:
            gewaehlt.append(b)
            gesehen.add(b[0])
        if len(gewaehlt) == BELEGE_JE_KANDIDAT:
            return gewaehlt
    for b in liste:
        if b not in gewaehlt:
            gewaehlt.append(b)
        if len(gewaehlt) == BELEGE_JE_KANDIDAT:
            break
    return gewaehlt


def schreibe_tsv(pfad, kopf, zeilen):
    with open(pfad, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        w.writerow(kopf)
        w.writerows(zeilen)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('export')
    ap.add_argument('--out', default=str(ROOT / 'ingest' / 'glossar-554'))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    tree = parse_export(args.export)
    gmh = [(it, m) for it, m in lemma_items(tree, 'publish') if m.get('sprachstufe') == 'gmh']
    print('gmh-Eintraege (veroeffentlicht): %d' % len(gmh))

    lem = lade_lemmata()
    nach_id = {l['id']: l for l in lem}
    nach_norm = defaultdict(list)
    for l in lem:
        nach_norm[norm_titel(l['lemma'])].append(l)
    varianten = lade_varianten()
    print('Lemmata: %d, verschiedene normalisierte Lemmaformen: %d, Variantenformen: %d'
          % (len(lem), len(nach_norm), len(varianten)))

    faelle = []   # (item, meta, art_des_falls, {lemma_id: art})
    for it, m in gmh:
        titel = it.findtext('title')
        n = norm_titel(titel)
        exakt = nach_norm.get(n, [])
        kand = {}
        if len(exakt) >= 1:
            for l in exakt:
                kand[l['id']] = 'exakt'
            fall = 'eindeutig' if len(exakt) == 1 else 'homograph'
        else:
            fall = 'kein-treffer'
            ohne = norm_titel(re.sub(r'\s*\([^)]*\)\s*$', '', titel))
            if ohne != n:
                for l in nach_norm.get(ohne, []):
                    kand.setdefault(l['id'], 'ohne-zusatz')
            for lid in varianten.get(n, {}):
                kand.setdefault(lid, 'variante')
            if len(n) >= 4:
                for ln, ls in nach_norm.items():
                    if len(ln) < 4 or abs(len(ln) - len(n)) > 3 or ln == n:
                        continue
                    if ln.startswith(n) or n.startswith(ln):
                        for l in ls:
                            kand.setdefault(l['id'], 'praefix')
                    elif len(n) >= 5 and len(ln) >= 5 and levenshtein_leq1(ln, n):
                        for l in ls:
                            kand.setdefault(l['id'], 'edit1')
        faelle.append((it, m, fall, kand))

    zahl_fall = Counter(f[2] for f in faelle)
    print('Faelle: %s' % dict(zahl_fall))

    alle_kand = {lid for _, _, fall, kand in faelle for lid in kand}
    zahl, belege = scanne_korpus(alle_kand)

    # Eindeutige Zuordnung
    zeilen = []
    for it, m, fall, kand in faelle:
        if fall != 'eindeutig':
            continue
        (lid,) = kand
        l = nach_id[lid]
        zeilen.append([it.findtext(WP + 'post_id'), it.findtext('title'), kurz(m.get('wortklasse')),
                       lid, l['lemma'], l.get('pos') or '', ' '.join(l.get('posAll') or []), zahl[lid]])
    zeilen.sort(key=lambda z: int(z[0]))
    schreibe_tsv(out / 'zuordnung-eindeutig.tsv',
                 ['glossar_id', 'glossar_titel', 'wortklasse_glossar', 'lemma_id', 'lemma', 'pos',
                  'pos_alle', 'belege_im_korpus'], zeilen)
    print('zuordnung-eindeutig.tsv: %d Zeilen (Menge: gmh-Eintraege mit genau einem Lemma)' % len(zeilen))
    print('  davon ohne Beleg im Korpus: %d von %d' % (sum(1 for z in zeilen if z[-1] == 0), len(zeilen)))

    # Pruefliste
    pl, pb = [], []
    n_kand_leer = 0
    for it, m, fall, kand in faelle:
        if fall == 'eindeutig':
            continue
        gid, titel = it.findtext(WP + 'post_id'), it.findtext('title')
        wk = kurz(m.get('wortklasse'))
        varformen = '|'.join(kurz(v) for k, v in sorted(m.items())
                             if re.match(r'^lemma_variant_\d+_schreibvariante$', k) and kurz(v))
        feste = [(lid, art) for lid, art in kand.items() if art in ('exakt', 'ohne-zusatz')]
        weitere = sorted(((lid, art) for lid, art in kand.items() if art not in ('exakt', 'ohne-zusatz')),
                         key=lambda x: (ART_RANG[x[1]], -zahl[x[0]]))
        abgeschnitten = max(0, len(weitere) - MAXK)
        wahl = feste + weitere[:MAXK]
        if not wahl:
            n_kand_leer += 1
            pl.append([fall, gid, titel, wk, varformen, '', '', '', '', '', 0, 0, ''])
            continue
        for lid, art in wahl:
            l = nach_id[lid]
            bel = waehle_belege(belege.get(lid, []))
            pl.append([fall, gid, titel, wk, varformen, art, lid, l['lemma'], l.get('pos') or '',
                       ' '.join(l.get('posAll') or []), zahl[lid], len(bel),
                       ('%d weitere Kandidaten nicht aufgefuehrt' % abgeschnitten) if abgeschnitten else ''])
            for nr, (sigle, xid, ctx) in enumerate(bel, 1):
                pb.append([gid, titel, lid, l['lemma'], nr, sigle, xid, ctx])
    schreibe_tsv(out / 'pruefliste.tsv',
                 ['fall', 'glossar_id', 'glossar_titel', 'wortklasse_glossar', 'schreibvarianten_glossar',
                  'kandidat_art', 'lemma_id', 'lemma', 'pos', 'pos_alle', 'belege_im_korpus',
                  'belege_unten', 'hinweis'], pl)
    schreibe_tsv(out / 'pruefliste-belege.tsv',
                 ['glossar_id', 'glossar_titel', 'lemma_id', 'lemma', 'nr', 'sigle', 'xml_id', 'kontext'], pb)
    print('pruefliste.tsv: %d Zeilen fuer %d Faelle (Menge: %d Homographen + %d ohne Treffer); '
          'ohne jeden Kandidaten: %d Faelle'
          % (len(pl), zahl_fall['homograph'] + zahl_fall['kein-treffer'], zahl_fall['homograph'],
             zahl_fall['kein-treffer'], n_kand_leer))
    print('pruefliste-belege.tsv: %d Belegzeilen' % len(pb))
    arten = Counter(r[5] for r in pl if r[0] == 'kein-treffer' and r[5])
    print('Kandidaten in den Faellen ohne Treffer nach Art: %s' % dict(arten))
    return 0


if __name__ == '__main__':
    sys.exit(main())
