#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#216 Phase 1: Frau Minne als eigenes NAM-Lemma. TROCKENLAUF-STAND, nichts angewendet.

Entscheidungsgrundlage (alles in #216):
  - chsteiner 2026-08-31: eigenes NAM-Lemma "Minne"; Regel: unmittelbar
    vorangehendes Token mit lemmaRef lemma_7260 (vrouwe), Wortform OHNE -n;
    die -n-Faelle bleiben beim Abstraktum lemma_4130. KZW 2026-08-31: "die
    Umsetzung liegt bei dir".
  - chsteiner 2026-11-08: NAM-Paket jetzt. Zurueckgehalten: 4 Lesefaelle
    (WGA_118600_5, RLS_140304_1, FR1_3026030_4, FR1_3001060_7; sind -n und
    damit ohnehin nicht in der Menge), die GWTK-Faelle (Sigle GWTK) und die
    drei RVBR-fro-Faelle. MR2_27022210102100_5 ("mynne" nach "vrouwen", ohne
    Lemma) kommt auf das Verb lemma_4133 (KZW 2026-08-31: "ist das Verb").
  - Koordination 2026-11-08: JT_42944000_1 und WGL_42150_6 (heute lemma_4133)
    werden NICHT umgehaengt. Alle Schreibungen minne/mynne/mynn/minn zaehlen.

Regel (aus dem Messskript messen.py der Koordination vom 2026-11-08, Stand
02eb7ebea, uebernommen; das Messskript liegt nicht im Repo): Vorgaenger
ist das naechste <w> im body in Dokumentreihenfolge (ueber pc, lb, hi hinweg);
dessen @lemmaRef enthaelt lemma_7260; seine Form endet, ohne Combining Marks
und ohne nachlaufende Nichtbuchstaben, nicht auf n; die Form des Tokens
passt auf ^m[iíîy]nn[eè]?$.

Was das Skript tut (--apply):
  - lexicon.xml: neuer Eintrag lemma_79830 "Minne" (NAM) mit einem Sense
    (Konzepte siehe KONZEPTE) an der String-Sortierstelle der Datei.
  - tei/: je Token @lemmaRef, @pos="NAM", @ana (Sense des neuen Lemmas, abschaltbar
    mit --ana keine) und @corresp (je Schreibung ein NEUER Typ ueber der
    hoechsten vergebenen Nummer, nach KZWs Auflage aus #367: nichts wandert
    mit). Die 50 heutigen lemma_4130-Tokens verlieren ihr altes @ana/@corresp.
  - MR2_27022210102100_5: @lemmaRef lemma_4133, @pos VRB, @corresp auf den
    Bestandstyp von 'mynne' unter lemma_4133, kein @ana.
  - je geaenderter Datei ein <change> im revisionDesc.

SCHREIBWEISE wie apply-461-fabeltiere.py: textuell, Ist-Zustand je Token vorher
verifiziert (nicht idempotent), Zeilenende erhalten.

Das Skript bricht ab, wenn die gemessene Menge nicht genau die erwarteten
Zahlen ergibt (326 Kandidaten, 321 = 50 + 271 nach Abzug von 3 fro und 2 Verb).

Usage:
    python -P -E scripts/ingest/pos-disambig/apply-216-minne-nam.py           # Trockenlauf
    python -P -E scripts/ingest/pos-disambig/apply-216-minne-nam.py --apply
    python -P -E scripts/ingest/pos-disambig/apply-216-minne-nam.py --ana keine
Schreibt in jedem Modus die Protokolle nach ingest/pos-disambig/216-minne-nam/.
"""

import argparse
import concurrent.futures
import csv
import io
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from corpus_files import corpus_files, default_jobs  # noqa: E402
from mhg_normalizer import normalize_mhg  # noqa: E402
from lxml import etree  # noqa: E402

OUT_DIR = ROOT / 'ingest' / 'pos-disambig' / '216-minne-nam'
DATUM = '2026-11-08'
NS = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'

V7260 = 'lexicon.xml#lemma_7260'
L4130 = 'lexicon.xml#lemma_4130'
L4133 = 'lexicon.xml#lemma_4133'
MINNE_RE = re.compile(r'^m[iíîy]nn[eè]?$', re.I)

NEU_LEMMA = 'lemma_79830'          # hoechste heute lemma_79829
NEU_SENSE = 'lemma_79830_sense_119201'  # hoechste Sense-Nummer heute 119200
ERWARTET_HOECHSTES_LEMMA = 79829
ERWARTET_HOECHSTER_SENSE = 119200
ORTH = 'Minne'
ETYM_AUF = ('lemma_4130', 'minne')

# VORSCHLAG, im Entscheidungsblatt Punkt 1 begruendet: Muster Fortuna
# (lemma_15703: Weiblich/Frau + Abstraktum + Namenskonzept) und der Sense
# lemma_4130_sense_83291 (Personennamen/Familiennamen, 1 Beleg REN_249200_1).
KONZEPTE = ['concept_21011000',   # Weiblich/Frau
            'concept_22704010',   # Liebe/Zuneigung/Abneigung/Gleichgültigkeit
            'concept_23112500']   # Personennamen/Familiennamen

# Zurueckhaltungen (chsteiner 2026-11-08)
LESEFAELLE = ['WGA_118600_5', 'RLS_140304_1', 'FR1_3026030_4', 'FR1_3001060_7']
FRO_RVBR_VORGAENGER = ['RVBR_4826_5', 'RVBR_6310_4', 'RVBR_8687_5']   # Vorgaenger-IDs
GESPERRTE_SIGLE = {'GWTK'}
VERB_REPARATUR = 'MR2_27022210102100_5'
VERB_ZIEL = 'lemma_4133'
VERB_FORM = 'mynne'

# Erwartete Menge (gemessen 2026-11-08 an 02eb7ebea, messen.py)
ERW = dict(kandidaten=326, ohne_lemma=274, lemma4130=50, anderes_lemma=2,
           gehalten_fro=3, gehalten_gwtk=0, verb_nicht_umhaengen=2,
           final=321, final_ohne=271, final_ohne_mit_posnam=9, final_4130=50)

ANKER = re.compile(
    r'([ \t]*)(<change [^>]*>(?:(?!</change>).)*</change>)(\s*)</revisionDesc>', re.S)


def strip_marks(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def endet_auf_n(form):
    f = strip_marks(form.lower())
    f = re.sub(r'[^a-zß]+$', '', f)
    return f.endswith('n')


def wtext(w):
    return ''.join(w.itertext()).strip()


def lies(pfad):
    with open(pfad, encoding='utf-8', newline='') as fh:
        return fh.read()


def schreibe(pfad, text):
    with open(pfad, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


# ---------------------------------------------------------------- Scan ---

SPEZIAL = set(LESEFAELLE) | {VERB_REPARATUR}


def scan_datei(fp):
    """Eine Korpusdatei: Kandidaten nach der Regel, Zustand der Sonder-IDs,
    hoechste im Korpus vergebene Typnummer. Worker-Funktion (modullevel)."""
    rohe = Path(fp).read_bytes()
    hoechster_typ = 0
    for corr in re.findall(rb'corresp="([^"]*)"', rohe):
        for n in re.findall(rb'variants\.xml#type_(\d+)', corr):
            hoechster_typ = max(hoechster_typ, int(n))
    sigle = Path(fp).name.split('.')[0]
    root = etree.fromstring(rohe, etree.XMLParser(huge_tree=True))
    body = root.find(f'.//{NS}body')
    ws = list(body.iter(NS + 'w'))
    kand, spezial = [], {}
    for i, w in enumerate(ws):
        wid = w.get(XMLID)
        form = wtext(w)
        trifft = bool(MINNE_RE.match(strip_marks(form)) or MINNE_RE.match(form))
        if not trifft and wid not in SPEZIAL:
            continue
        if i == 0:
            continue
        p = ws[i - 1]
        p_lem = p.get('lemmaRef') or ''
        info = dict(
            id=wid, sigle=sigle, form=form, lemmaRef=w.get('lemmaRef') or '',
            pos=w.get('pos') or '', ana=w.get('ana') or '', corresp=w.get('corresp') or '',
            pred_id=p.get(XMLID), pred_form=wtext(p), pred_lemmaRef=p_lem,
            pred_n=endet_auf_n(wtext(p)),
            kontext=' '.join(wtext(x) for x in ws[max(0, i - 4):i]) + ' **' + form + '** '
                    + ' '.join(wtext(x) for x in ws[i + 1:i + 5]))
        if wid in SPEZIAL:
            spezial[wid] = info
        if trifft and V7260 in p_lem.split() and not info['pred_n']:
            kand.append(info)
    return sigle, kand, spezial, hoechster_typ


def scanne_korpus(jobs):
    dateien = [str(p) for p in corpus_files()]
    kand, spezial, hoechster = [], {}, 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as pool:
        for sigle, k, s, ht in pool.map(scan_datei, dateien, chunksize=1):
            kand.extend(k)
            spezial.update(s)
            hoechster = max(hoechster, ht)
    return len(dateien), kand, spezial, hoechster


# ------------------------------------------------------- Variantendaten ---

def lies_varianten():
    """type_id -> (lemma_id, Form, n); hoechste Typnummer."""
    root = etree.parse(str(ROOT / 'authority-files' / 'variants.xml')).getroot()
    typen, hoechster = {}, 0
    for e in root.iter(NS + 'entry'):
        lem = e.get('corresp').split('#')[1]
        for f in e.iter(NS + 'form'):
            tid = f.get(XMLID)
            typen[tid] = (lem, (f.text or '').strip(), int(f.get('n')))
            hoechster = max(hoechster, int(tid.split('_')[1]))
    return typen, hoechster


def rang(per_lemma):
    return sorted(per_lemma, key=lambda l: -per_lemma[l])   # stabil, wie build-authority-index


def flip_simulation(typen, plan, neue_typen, verb_typ):
    """Vorschrift B (ADR-021): wie aendert sich variants[Form] / variantCandidates[Form]?
    Naeherung: Gleichstaende werden zugunsten der Bestandslemmata gebrochen
    (die Dokumentordnung von variants.xml ist hier nicht nachgebildet)."""
    vor = defaultdict(dict)
    for tid, (lem, form, n) in typen.items():
        k = normalize_mhg(form)
        vor[k][lem] = vor[k].get(lem, 0) + n
    nach = {k: dict(v) for k, v in vor.items()}
    beruehrt = set()
    for t in plan:
        if t['aktion'] == 'UMHAENGEN':
            alt = t['alt_corresp'].split('#')[1]
            lem, form, _ = typen[alt]
            k = normalize_mhg(form)
            nach[k][lem] -= 1
            beruehrt.add(k)
    je_form = Counter(t['form'].lower() for t in plan if t['aktion'] != 'VERB')
    for form, n in je_form.items():
        k = normalize_mhg(form)
        nach.setdefault(k, {})
        nach[k][NEU_LEMMA] = nach[k].get(NEU_LEMMA, 0) + n
        beruehrt.add(k)
    if verb_typ:
        lem, form, _ = typen[verb_typ]
        k = normalize_mhg(form)
        nach[k][lem] += 1
        beruehrt.add(k)
    zeilen, flips = [], 0
    for k in sorted(beruehrt):
        vor_r = rang(vor.get(k, {}))
        nach_r = rang(nach[k])
        flip = bool(vor_r) and vor_r[0] != nach_r[0]
        flips += flip
        zeilen.append(f'    {k!r}: vorher {[(l, vor[k][l]) for l in vor_r][:4]} -> '
                      f'nachher {[(l, nach[k][l]) for l in nach_r][:4]}'
                      f'{"   UMGEKLAPPT" if flip else ""}')
    return zeilen, flips


# -------------------------------------------------------------- Haupt ---

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--ana', choices=['alle', 'keine'], default='alle',
                    help='alle: Sense des neuen Lemmas auf alle Tokens (Vorschlag); '
                         'keine: kein @ana, die 21 alten verfallen')
    ap.add_argument('--jobs', type=int, default=default_jobs())
    args = ap.parse_args()
    APPLY = args.apply

    lexpfad = ROOT / 'authority-files' / 'lexicon.xml'
    konpfad = ROOT / 'authority-files' / 'concepts.xml'
    lexikon, konzepte = lies(lexpfad), lies(konpfad)

    # ---- Vorbedingungen am Lexikon
    hoechstes = max(int(m) for m in re.findall(r'<entry xml:id="lemma_(\d+)"', lexikon))
    hoechster_sense = max(int(m) for m in re.findall(r'_sense_(\d+)"', lexikon))
    if hoechstes != ERWARTET_HOECHSTES_LEMMA:
        sys.exit(f'ABBRUCH: hoechstes Lemma lemma_{hoechstes}, erwartet lemma_{ERWARTET_HOECHSTES_LEMMA}')
    if hoechster_sense != ERWARTET_HOECHSTER_SENSE:
        sys.exit(f'ABBRUCH: hoechste Sense-Nummer {hoechster_sense}, erwartet {ERWARTET_HOECHSTER_SENSE}')
    if f'xml:id="{NEU_LEMMA}"' in lexikon:
        sys.exit(f'ABBRUCH: {NEU_LEMMA} steht schon da')
    for k in KONZEPTE:
        if f'xml:id="{k}"' not in konzepte:
            sys.exit(f'ABBRUCH: {k} fehlt in concepts.xml')

    # ---- Scan
    typen, hoechster_var = lies_varianten()
    n_dateien, kand, spezial, hoechster_korpus = scanne_korpus(args.jobs)
    print(f'Korpus: {n_dateien} Dateien. Hoechster Typ: variants.xml {hoechster_var}, '
          f'Korpus-@corresp {hoechster_korpus}')

    # ---- Einteilung
    ohne = [c for c in kand if not c['lemmaRef']]
    l4130 = [c for c in kand if c['lemmaRef'] == L4130]
    anderes = [c for c in kand if c['lemmaRef'] and c['lemmaRef'] != L4130]
    unbekannt = [c for c in anderes if c['lemmaRef'] != L4133]
    if unbekannt:
        sys.exit(f'ABBRUCH: Kandidaten mit unbekanntem Lemma: {[c["id"] for c in unbekannt]}')
    gehalten_fro = [c for c in kand if c['pred_id'] in FRO_RVBR_VORGAENGER]
    gehalten_gwtk = [c for c in kand if c['sigle'] in GESPERRTE_SIGLE]
    verb_bleibt = anderes
    sperr = {c['id'] for c in gehalten_fro + gehalten_gwtk + verb_bleibt}
    final = [c for c in kand if c['id'] not in sperr]
    final_ohne = [c for c in final if not c['lemmaRef']]
    final_4130 = [c for c in final if c['lemmaRef'] == L4130]
    final_posnam = [c for c in final_ohne if c['pos'] == 'NAM']

    ist = dict(kandidaten=len(kand), ohne_lemma=len(ohne), lemma4130=len(l4130),
               anderes_lemma=len(anderes), gehalten_fro=len(gehalten_fro),
               gehalten_gwtk=len(gehalten_gwtk), verb_nicht_umhaengen=len(verb_bleibt),
               final=len(final), final_ohne=len(final_ohne),
               final_ohne_mit_posnam=len(final_posnam), final_4130=len(final_4130))
    print('Menge nach Regel:')
    print(f'  {ist["kandidaten"]} Kandidaten = {ist["ohne_lemma"]} ohne @lemmaRef '
          f'+ {ist["lemma4130"]} lemma_4130 + {ist["anderes_lemma"]} anderes Lemma '
          f'({", ".join(c["id"] + " " + c["lemmaRef"].split("#")[1] for c in anderes)})')
    print(f'  zurueckgehalten: {ist["gehalten_fro"]} fro-RVBR ({", ".join(c["id"] for c in gehalten_fro)}), '
          f'{ist["gehalten_gwtk"]} GWTK, {ist["verb_nicht_umhaengen"]} Verb nicht umhaengen')
    print(f'  Ergebnis: {ist["final"]} = {ist["final_4130"]} (heute lemma_4130 NOM) '
          f'+ {ist["final_ohne"]} (ohne @lemmaRef, davon {ist["final_ohne_mit_posnam"]} mit pos=NAM ohne Lemma)')
    if ist != ERW:
        diff = {k: (ist[k], ERW[k]) for k in ERW if ist[k] != ERW[k]}
        sys.exit(f'ABBRUCH: Menge weicht ab (gefunden, erwartet): {diff}')
    if len({c['id'] for c in kand}) != len(kand):
        sys.exit('ABBRUCH: doppelte xml:id in der Kandidatenmenge')
    if not all(c['pos'] == 'NOM' for c in final_4130):
        sys.exit('ABBRUCH: lemma_4130-Token mit pos != NOM')
    if not all(c['pos'] in ('', 'NAM') for c in final_ohne):
        sys.exit('ABBRUCH: lemmaloses Token mit anderem pos als NAM')
    fro_formen = {c['pred_form'] for c in gehalten_fro}
    print(f'  Gegenprobe fro-Faelle, Vorgaengerformen: {sorted(fro_formen)}')

    # Lesefaelle: muessen -n sein, also nicht in der Menge
    for lid in LESEFAELLE:
        s = spezial.get(lid)
        if s is None or not s['pred_n'] or lid in {c['id'] for c in kand}:
            sys.exit(f'ABBRUCH: Lesefall {lid} nicht wie erwartet (Vorgaenger auf -n, nicht in der Menge)')
    print(f'  Lesefaelle: {len(LESEFAELLE)} von {len(LESEFAELLE)} haben Vorgaenger auf -n und liegen ausserhalb der Menge')

    # ---- Verb-Reparatur
    s = spezial.get(VERB_REPARATUR)
    if (s is None or s['lemmaRef'] or s['pos'] or s['form'] != VERB_FORM
            or V7260 not in s['pred_lemmaRef'].split()):
        sys.exit(f'ABBRUCH: {VERB_REPARATUR} nicht im erwarteten Ausgangszustand: {s}')
    verb_typen = [t for t, (lem, form, n) in typen.items() if lem == VERB_ZIEL and form == VERB_FORM]
    if len(verb_typen) != 1:
        sys.exit(f'ABBRUCH: Bestandstyp fuer {VERB_FORM} unter {VERB_ZIEL}: {verb_typen}')
    verb_typ = verb_typen[0]
    print(f'  Verb-Reparatur: {VERB_REPARATUR} ({s["pred_form"]} {s["form"]}) -> {VERB_ZIEL} VRB, Bestandstyp {verb_typ}')

    # ---- Typen und Plan
    schreibungen = Counter(c['form'] for c in final)
    if any(f != f.lower() for f in schreibungen):
        sys.exit(f'ABBRUCH: Grossschreibung in der Menge: {schreibungen}')
    naechster = max(hoechster_var, hoechster_korpus) + 1
    neue_typen = {}
    for form, _ in sorted(schreibungen.items(), key=lambda kv: (-kv[1], kv[0])):
        neue_typen[form] = f'type_{naechster}'
        naechster += 1
    print(f'  Schreibungen: {dict(schreibungen)}')
    print(f'  Neue Typen (NEUE Nummern, KZWs Auflage aus #367): {neue_typen}')

    plan = []
    for c in sorted(final, key=lambda c: (c['sigle'], c['id'])):
        aktion = 'UMHAENGEN' if c['lemmaRef'] else ('NEU_POS_NAM' if c['pos'] else 'NEU')
        plan.append(dict(
            id=c['id'], sigle=c['sigle'], form=c['form'], aktion=aktion,
            alt_lemmaRef=c['lemmaRef'], alt_pos=c['pos'], alt_ana=c['ana'], alt_corresp=c['corresp'],
            neu_lemmaRef=f'lexicon.xml#{NEU_LEMMA}', neu_pos='NAM',
            neu_ana=f'lexicon.xml#{NEU_SENSE}' if args.ana == 'alle' else '',
            neu_corresp=f'variants.xml#{neue_typen[c["form"]]}',
            vorgaenger_id=c['pred_id'], vorgaenger_form=c['pred_form'], kontext=c['kontext']))
    plan.append(dict(
        id=VERB_REPARATUR, sigle='MR2', form=VERB_FORM, aktion='VERB',
        alt_lemmaRef='', alt_pos='', alt_ana='', alt_corresp='',
        neu_lemmaRef=f'lexicon.xml#{VERB_ZIEL}', neu_pos='VRB', neu_ana='',
        neu_corresp=f'variants.xml#{verb_typ}',
        vorgaenger_id=s['pred_id'], vorgaenger_form=s['pred_form'], kontext=s['kontext']))

    # ---- @ana-Bilanz der 50
    ana_ist = Counter(c['ana'] or '(kein @ana)' for c in final_4130)
    print(f'  @ana der {len(final_4130)} lemma_4130-Tokens: {dict(ana_ist)}')
    print(f'  @corresp der {len(final_4130)} lemma_4130-Tokens: '
          f'{dict(Counter(c["corresp"] for c in final_4130))}')

    # ---- Flip-Simulation
    zeilen, flips = flip_simulation(typen, plan, neue_typen, verb_typ)
    print('Variantenranking (Vorschrift B), Naeherung:')
    print('\n'.join(zeilen))
    print(f'  Umgeklappte Formen (erste Kandidatin wechselt): {flips}')

    # ---- Texte aufbauen (im Speicher)
    je_datei = defaultdict(list)
    for t in plan:
        je_datei[t['sigle']].append(t)
    neu_texte = {}
    for sigle, ts in sorted(je_datei.items()):
        pfad = ROOT / 'tei' / f'{sigle}.tei.xml'
        text = lies(pfad)
        n_umh = n_neu = n_verb = 0
        for t in ts:
            if t['aktion'] == 'VERB':
                alt = f'<w xml:id="{t["id"]}">{t["form"]}</w>'
            else:
                attr = ''
                if t['alt_lemmaRef']:
                    attr += f' lemmaRef="{t["alt_lemmaRef"]}"'
                if t['alt_pos']:
                    attr += f' pos="{t["alt_pos"]}"'
                if t['alt_ana']:
                    attr += f' ana="{t["alt_ana"]}"'
                if t['alt_corresp']:
                    attr += f' corresp="{t["alt_corresp"]}"'
                alt = f'<w xml:id="{t["id"]}"{attr}>{t["form"]}</w>'
            neu_attr = f' lemmaRef="{t["neu_lemmaRef"]}" pos="{t["neu_pos"]}"'
            if t['neu_ana']:
                neu_attr += f' ana="{t["neu_ana"]}"'
            neu_attr += f' corresp="{t["neu_corresp"]}"'
            soll = f'<w xml:id="{t["id"]}"{neu_attr}>{t["form"]}</w>'
            if text.count(alt) != 1:
                sys.exit(f'ABBRUCH: Ist-Zustand von {t["id"]} weicht ab ({text.count(alt)}x): {alt}')
            text = text.replace(alt, soll)
            if t['aktion'] == 'UMHAENGEN':
                n_umh += 1
            elif t['aktion'] == 'VERB':
                n_verb += 1
            else:
                n_neu += 1
        m = ANKER.search(text[:text.find('</teiHeader>')])
        if not m:
            sys.exit(f'ABBRUCH: kein revisionDesc-Anker in {sigle}')
        enl = '\r\n' if '\r\n' in m.group(3) else '\n'
        teile = []
        if n_neu:
            teile.append(f'{n_neu} neu annotiert')
        if n_umh:
            teile.append(f'{n_umh} von lemma_4130 umgehängt')
        satz = (f'#216 Frau Minne: {len(ts) - n_verb} Token{"s" if len(ts) - n_verb != 1 else ""} '
                f'auf das Namenlemma lexicon.xml#{NEU_LEMMA} (Minne, NAM) gesetzt'
                + (f' ({", ".join(teile)})' if teile else ''))
        if n_verb:
            satz += f'; {n_verb} Token (mynne nach vrouwen) auf das Verb lemma_4133'
        satz += ('. Regel: unmittelbar vorangehendes Token mit lemma_7260, Form ohne -n '
                 '(Entscheidung chsteiner und K. Zeppezauer-Wachauer 2026-08-31, Umsetzung 2026-11-08; '
                 'Provenienz-Log: ingest/pos-disambig/216-minne-nam/).')
        eintrag = f'<change when="{DATUM}" who="#editor">{satz}</change>'
        # m wurde im Kopf gesucht; die Offsets gelten im selben Text
        text =text[:m.end(2)] + enl + m.group(1) + eintrag + text[m.end(2):]
        neu_texte[pfad] = text

    # ---- Lexikon-Eintrag
    nl = '\r\n' if '\r\n' in lexikon else '\n'
    ids = re.findall(r'<entry xml:id="(lemma_\d+)"', lexikon)
    groesser = [i for i in ids if i > NEU_LEMMA]
    if not groesser:
        sys.exit('ABBRUCH: keine String-Nachfolger-ID gefunden')
    nachfolger = min(groesser)
    vorgaenger = max(i for i in ids if i < NEU_LEMMA)
    if lexikon.count(f'<entry xml:id="{nachfolger}">') != 1:
        sys.exit(f'ABBRUCH: Anker {nachfolger} nicht genau einmal')
    m = re.search(r'([ \t]*)<entry xml:id="%s">' % re.escape(nachfolger), lexikon)
    e = m.group(1)
    typliste = ' '.join(sorted(f'#{t}' for t in neue_typen.values()))
    ana_attr = f' ana="{typliste}"'
    zeilen_lex = [
        f'{e}<entry xml:id="{NEU_LEMMA}">',
        f'{e}  <form type="lemma">',
        f'{e}    <orth>{ORTH}</orth>',
        f'{e}  </form>',
        f'{e}  <gramGrp>',
        f'{e}    <pos>NAM</pos>',
        f'{e}  </gramGrp>',
        f'{e}  <etym type="morphological">',
        f'{e}    <seg type="component" corresp="lexicon.xml#{ETYM_AUF[0]}">{ETYM_AUF[1]}</seg>',
        f'{e}  </etym>',
        f'{e}  <sense xml:id="{NEU_SENSE}"{ana_attr}>']
    zeilen_lex += [f'{e}    <ptr target="concepts.xml#{k}"/>' for k in KONZEPTE]
    zeilen_lex += [f'{e}  </sense>', f'{e}</entry>', '']
    lexikon_neu = lexikon[:m.start()] + nl.join(zeilen_lex) + lexikon[m.start():]
    print(f'Lexikon: {NEU_LEMMA} "{ORTH}" NAM zwischen {vorgaenger} und {nachfolger} '
          f'(Datei ist nach ID-String sortiert), Sense {NEU_SENSE} mit {len(KONZEPTE)} Konzepten, '
          f'ana {typliste}')

    # ---- Gegenprobe im Speicher: die neuen Texte sind wohlgeformt und tragen genau die Sollattribute
    parser = etree.XMLParser(huge_tree=True)
    for pfad, text in neu_texte.items():
        sigle = pfad.name.split('.')[0]
        root = etree.fromstring(text.encode('utf-8'), parser)
        by_id = {w.get(XMLID): w for w in root.iter(NS + 'w')}
        for t in je_datei[sigle]:
            w = by_id[t['id']]
            soll = {'lemmaRef': t['neu_lemmaRef'], 'pos': t['neu_pos'], 'corresp': t['neu_corresp']}
            if t['neu_ana']:
                soll['ana'] = t['neu_ana']
            ist_attr = {k: v for k, v in w.attrib.items() if k != XMLID}
            if ist_attr != soll or wtext(w) != t['form']:
                sys.exit(f'ABBRUCH: Gegenprobe {t["id"]}: {ist_attr} statt {soll}')
    etree.fromstring(lexikon_neu.encode('utf-8'), parser)
    print(f'Gegenprobe im Speicher: {len(neu_texte)} Dateien und lexicon.xml wohlgeformt, '
          f'{len(plan)} Tokens tragen genau die Sollattribute')

    # ---- Protokolle
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    spalten = list(plan[0].keys())
    with open(OUT_DIR / 'protokoll.tsv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=spalten, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(plan)
    with open(OUT_DIR / 'zurueckgehalten.tsv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n')
        w.writerow(['id', 'grund', 'lemmaRef_heute', 'pos_heute', 'vorgaenger_form', 'kontext'])
        for c in gehalten_fro:
            w.writerow([c['id'], 'frô-Fall RVBR (chsteiner 2026-11-08)', c['lemmaRef'], c['pos'], c['pred_form'], c['kontext']])
        for c in verb_bleibt:
            w.writerow([c['id'], 'Verb bleibt bei lemma_4133 (Koordination 2026-11-08)', c['lemmaRef'], c['pos'], c['pred_form'], c['kontext']])
        for lid in LESEFAELLE:
            c = spezial[lid]
            w.writerow([lid, 'Lesefall, Vorgaenger auf -n (chsteiner 2026-11-08)', c['lemmaRef'], c['pos'], c['pred_form'], c['kontext']])

    # ---- Schreiben
    if APPLY:
        for pfad, text in neu_texte.items():
            schreibe(pfad, text)
        schreibe(lexpfad, lexikon_neu)
    n_tok = len(plan)
    n_pos = sum(1 for t in plan if t['aktion'] in ('NEU', 'NEU_POS_NAM', 'VERB'))
    print(f'{n_tok} Tokens in {len(neu_texte)} Dateien, 1 Lexikoneintrag, {len(neue_typen)} neue Typen; '
          f'{n_pos} Tokens bekommen erstmals @lemmaRef (Positionen verschieben sich dort), '
          f'{n_tok - n_pos} behalten ihre Position'
          + ('' if APPLY else '  [Trockenlauf]'))
    print(f'Protokolle: {OUT_DIR / "protokoll.tsv"}, {OUT_DIR / "zurueckgehalten.tsv"}')
    if not APPLY:
        print('Trockenlauf, tei/ und authority-files/ nicht geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
