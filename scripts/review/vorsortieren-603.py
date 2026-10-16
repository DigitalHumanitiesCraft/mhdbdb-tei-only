# -*- coding: utf-8 -*-
"""Vorsortierung der Belege von Senses mit concept_21111000 (Ernaehrung von Menschen), Issue #603.

Aufruf (liest nur, aendert im Repo nichts):
    python scripts/review/vorsortieren-603.py <repo-wurzel> <ausgabeordner>

Schreibt: senses-21111000.tsv, belege-tier.tsv, lemmata-ohne-ana.tsv, konzepte-tier.tsv,
faelle-abebizen-lecken.tsv (maschinell; manuelle Urteile aus manuell-faelle.tsv im
Ausgabeordner, falls vorhanden), stichprobe.tsv (je Klasse 10 Belege, Seed 603),
zusammenfassung.txt und alle-belege-vorsortiert.tsv (7,5 MB, nicht im Repo, wird von
stichprobe2-603.py gelesen). Zum Nachlaufen einen leeren Ordner nehmen (nicht
ingest/review/603-ernaehrung/, die Dateien dort wuerden ueberschrieben),
manuell-faelle.tsv hineinkopieren und die Ausgabe mit dem Repo vergleichen.
"""
import sys, os, re, glob, random, collections
from lxml import etree

sys.stdout.reconfigure(encoding='utf8')
REPO = sys.argv[1].rstrip('/\\')
OUT = sys.argv[2].rstrip('/\\')
T = '{http://www.tei-c.org/ns/1.0}'
XID = '{http://www.w3.org/XML/1998/namespace}id'
NS = {'t': 'http://www.tei-c.org/ns/1.0'}
TARGET = 'concepts.xml#concept_21111000'
WIN = 8          # Kontextfenster fuer die Regeln
SHOW = 12        # Kontextanzeige in den TSV
CRIT = ('abebîʒen', 'lecken')   # Fallstudie

# ---------- Konzepte ----------
ctree = etree.parse(REPO + '/authority-files/concepts.xml')
cname, cbroad = {}, {}
for c in ctree.iter(T + 'category'):
    cid = c.get(XID)
    de = c.xpath('t:catDesc/t:term[@xml:lang="de" and not(@type)]', namespaces=NS)
    br = c.xpath('t:catDesc/t:ptr[@type="broader"]/@target', namespaces=NS)
    cname[cid] = de[0].text if de else ''
    cbroad[cid] = br[0][1:] if br else ''
children = collections.defaultdict(list)
for k, v in cbroad.items():
    if v:
        children[v].append(k)


def subtree(root):
    out, st = set(), [root]
    while st:
        x = st.pop()
        out.add(x)
        st.extend(children.get(x, []))
    return out


# Tierkonzepte: explizite Liste (ohne Koerper/Organe/Stoffwechsel/Verarbeitung/Krankheiten/Zucht)
TIER_CONCEPTS = ['concept_14010000', 'concept_14011400', 'concept_14012000', 'concept_14012100',
                 'concept_14013000', 'concept_14014000', 'concept_14015000', 'concept_14016000',
                 'concept_14017000', 'concept_14017100', 'concept_14020000', 'concept_14022000',
                 'concept_14023000', 'concept_14024000', 'concept_14025000', 'concept_14026000',
                 'concept_14027000', 'concept_14030000', 'concept_14032000', 'concept_14033000',
                 'concept_14034000', 'concept_14040000', 'concept_14043000', 'concept_14050000',
                 'concept_14060000', 'concept_14080000', 'concept_14100000', 'concept_14110000']
TIER_SET = set(TIER_CONCEPTS)
FOOD_SET = subtree('concept_21111300')          # Lebensmittel (Fleisch, Speisen, ...)
# Menschkonzepte: Geschlecht, Altersstufen, Ehe/Familie (inkl. Personennamen)
MENSCH_SET = subtree('concept_21010000') | subtree('concept_21103000') | subtree('concept_23112000')
MENSCH_SET.discard('concept_23112500')  # Personennamen/Familiennamen: kommt gleich wieder rein
MENSCH_SET |= subtree('concept_23112500')
PRON_ORTH = {'ich', 'wir', 'du', 'ir'}

# ---------- Lexikon ----------
ltree = etree.parse(REPO + '/authority-files/lexicon.xml')
orth, lpos = {}, {}
sense_c = {}          # sense_id -> set(concept_ids)
sense_lemma = {}
lemma_senses = collections.defaultdict(list)
target_senses = []    # Reihenfolge wie in der Datei
for e in ltree.iter(T + 'entry'):
    lid = e.get(XID)
    o = e.xpath('t:form[@type="lemma"]/t:orth', namespaces=NS)
    orth[lid] = o[0].text if o else ''
    lpos[lid] = set(e.xpath('t:gramGrp/t:pos/text()', namespaces=NS))
    for s in e.findall(T + 'sense'):
        sid = s.get(XID)
        cs = set()
        for p in s.findall(T + 'ptr'):
            tg = p.get('target')
            cs.add(tg.split('#')[-1])
            if tg == TARGET:
                target_senses.append(sid)
        sense_c[sid] = cs
        sense_lemma[sid] = lid
        lemma_senses[lid].append(sid)
print('Entries', len(orth), 'Senses', len(sense_c))
n_ptr = sum(1 for s in sense_c.values() if 'concept_21111000' in s)
print('Senses mit concept_21111000', len(target_senses), '(distinct', len(set(target_senses)), ')')
TSET = set(target_senses)
target_lemmas = sorted({sense_lemma[s] for s in TSET})


def lemma_flags(lid):
    ss = lemma_senses.get(lid, [])
    tier = any(sense_c[s] & TIER_SET for s in ss)
    food = any(sense_c[s] & FOOD_SET for s in ss)
    mensch = any(sense_c[s] & MENSCH_SET for s in ss)
    return tier, food, mensch


LF = {l: lemma_flags(l) for l in orth}
tier_lemmas = [l for l, f in LF.items() if f[0]]
mensch_lemmas = [l for l, f in LF.items() if f[2]]
pron_lemmas = [l for l in orth if orth[l] in PRON_ORTH and 'PRO' in lpos[l]]
print('Tierwort-Lemmata (Konzeptliste)', len(tier_lemmas), ' davon ohne Lebensmittel-Sense', sum(1 for l in tier_lemmas if not LF[l][1]))
print('Mensch-Lemmata', len(mensch_lemmas), 'Pronomen-Lemmata', [(l, orth[l]) for l in pron_lemmas])


def tier_word(w):
    """-> 'T1' (ana-Sense mit Tierkonzept, ohne Lebensmittelkonzept), 'T2' (nur Lemma), 'X' (ausgeschlossen: Lebensmittel), None"""
    for lid in w['lem']:
        if w['ana']:
            hit = [s for s in w['ana'] if sense_lemma.get(s) == lid and sense_c.get(s, set()) & TIER_SET]
            if hit:
                if any(sense_c[s] & FOOD_SET for s in hit):
                    return 'X'
                return 'T1'
        else:
            tier, food, _ = LF.get(lid, (False, False, False))
            if tier:
                return 'X' if food else 'T2'
    return None


def mensch_word(w):
    for lid in w['lem']:
        if lid in pron_lemmas and 'PRO' in (w['pos'] or ''):
            return 'M1'
        if w['ana']:
            if any(sense_lemma.get(s) == lid and sense_c.get(s, set()) & MENSCH_SET for s in w['ana']):
                return 'M2'
        elif LF.get(lid, (0, 0, 0))[2]:
            return 'M3'
    return None


def classify(ws, i):
    tier_hits, mensch_hits = [], []
    for j in range(max(0, i - WIN), min(len(ws), i + WIN + 1)):
        if j == i:
            continue
        r = tier_word(ws[j])
        if r in ('T1', 'T2'):
            tier_hits.append((r, j - i, ws[j]))
        r = mensch_word(ws[j])
        if r:
            mensch_hits.append((r, j - i, ws[j]))
    return tier_hits, mensch_hits


def ctx(ws, i, n=SHOW):
    a = ' '.join(x['txt'] for x in ws[max(0, i - n):i])
    b = ' '.join(x['txt'] for x in ws[i + 1:i + 1 + n])
    return a + ' [[' + ws[i]['txt'] + ']] ' + b


def tok(s):
    return [x.split('#')[-1] for x in (s or '').split()]


# ---------- Korpus ----------
sense_n = collections.Counter()
sense_cls = collections.defaultdict(collections.Counter)    # sid -> Zaehler der Klassen
sense_both = collections.Counter()
rule_fire = collections.Counter()
tokens_target_unique = 0
cls_unique = collections.Counter()
ana_missing = collections.Counter()          # lemma -> w ohne ana
ana_missing_cls = collections.defaultdict(collections.Counter)
tier_rows, case_rows, all_rows = [], [], []
tlem = set(target_lemmas)
crit_lemmas = {l for l in orth if orth[l] in CRIT}
files = sorted(glob.glob(REPO + '/tei/*.xml'))
n_files = len(files)
total_w = 0
for f in files:
    sig = os.path.basename(f).split('.')[0]
    tr = etree.parse(f)
    ws = []
    for w in tr.iter(T + 'w'):
        ws.append({'id': w.get(XID), 'lem': (w.get('lemmaRef') or '').replace('lexicon.xml#', '').split(),
                   'pos': w.get('pos'), 'ana': tok(w.get('ana')), 'txt': ''.join(w.itertext()).strip()})
    total_w += len(ws)
    for i, w in enumerate(ws):
        hit_s = [s for s in w['ana'] if s in TSET]
        lem_hit = [l for l in w['lem'] if l in tlem]
        crit = any(l in crit_lemmas for l in w['lem'])
        if not (hit_s or (lem_hit and not w['ana']) or crit):
            continue
        th, mh = classify(ws, i)
        if th:
            cls = 'tier'
        elif mh:
            cls = 'mensch'
        else:
            cls = 'unklar'
        both = bool(th and mh)
        rule = ','.join(sorted({h[0] for h in th} | {h[0] for h in mh}))
        tdesc = '; '.join('%s:%s(%+d)' % (h[0], h[2]['txt'], h[1]) for h in th[:4])
        mdesc = '; '.join('%s:%s(%+d)' % (h[0], h[2]['txt'], h[1]) for h in mh[:4])
        c12 = ctx(ws, i)
        if hit_s:
            tokens_target_unique += 1
            cls_unique[cls] += 1
            for s in hit_s:
                sense_n[s] += 1
                sense_cls[s][cls] += 1
                if both:
                    sense_both[s] += 1
            for r_ in {h[0] for h in th}:
                rule_fire['Belege mit Regel ' + r_] += 1
            for r_ in {h[0] for h in mh}:
                rule_fire['Belege mit Regel ' + r_] += 1
            if th and mh:
                rule_fire['Belege mit Tier- und Mensch-Treffer (-> tier)'] += 1
        elif lem_hit and not w['ana']:
            for l in lem_hit:
                ana_missing[l] += 1
                ana_missing_cls[l][cls] += 1
        row = [sig, w['id'], ','.join(hit_s) or ('(ohne ana)' if not w['ana'] else '(ana ohne Ziel-Sense)'), ','.join(w['lem']), orth.get(w['lem'][0], '') if w['lem'] else '',
               w['txt'], cls, 'ja' if both else '', tdesc, mdesc, c12]
        all_rows.append(row)
        if cls == 'tier' and (hit_s or (lem_hit and not w['ana'])):
            tier_rows.append(row)
        if crit and any(l in crit_lemmas for l in w['lem']):
            case_rows.append(row + [','.join(w['ana'])])
print('Dateien', n_files, 'w gesamt', total_w)

# ---------- Ausgabe ----------
def wr(name, header, rows):
    with open(OUT + '/' + name, 'w', encoding='utf8', newline='') as fh:
        fh.write('\t'.join(header) + '\n')
        for r in rows:
            fh.write('\t'.join(str(x).replace('\t', ' ').replace('\n', ' ') for x in r) + '\n')


# senses (jede Sense einmal, Reihenfolge der Datei)
seen, rows = set(), []
for s in target_senses:
    if s in seen:
        continue
    seen.add(s)
    l = sense_lemma[s]
    c = sense_cls[s]
    rows.append([s, l, orth[l], sense_n[s], c['tier'], c['mensch'], c['unklar'], sense_both[s],
                 ' '.join(sorted(sense_c[s] - {'concept_21111000'}))])
wr('senses-21111000.tsv', ['sense_id', 'lemma_id', 'orth', 'belege_gesamt', 'tier', 'mensch', 'unklar', 'tier_davon_auch_mensch_treffer', 'weitere_konzepte'], rows)

wr('lemmata-ohne-ana.tsv', ['lemma_id', 'orth', 'belege_ohne_ana', 'tier', 'mensch', 'unklar', 'belege_lemma_gesamt_mit_lemmaRef'],
   [[l, orth[l], ana_missing[l], ana_missing_cls[l]['tier'], ana_missing_cls[l]['mensch'], ana_missing_cls[l]['unklar'], ''] for l in target_lemmas])

H = ['sigle', 'w_id', 'sense_ids_im_ana', 'lemma_id', 'lemma', 'form', 'klasse', 'tier_und_mensch_treffer', 'tierwoerter_im_fenster', 'mensch_treffer', 'kontext']
wr('belege-tier.tsv', H, tier_rows)
wr('alle-belege-vorsortiert.tsv', H, [r for r in all_rows])

# Faelle
manual = {}
mp = OUT + '/manuell-faelle.tsv'
if os.path.exists(mp):
    for ln in open(mp, encoding='utf8').read().splitlines()[1:]:
        p = ln.split('\t')
        if len(p) >= 3:
            manual[p[0]] = (p[1], p[2])
fr = []
for r in case_rows:
    m = manual.get(r[1], ('', ''))
    fr.append([r[3], r[4], r[0], r[1], r[2], r[5], r[6], r[8], r[9], r[10], m[0], m[1], r[11]])
wr('faelle-abebizen-lecken.tsv', ['lemma_id', 'lemma', 'sigle', 'w_id', 'sense_ids_im_ana', 'form', 'maschinell', 'tierwoerter_im_fenster', 'mensch_treffer', 'kontext', 'urteil_manuell', 'begruendung', 'ana_roh'], fr)

# Stichprobe
random.seed(603)
smp = []
src = [r for r in all_rows if r[2].startswith('lemma_')]
for c in ('tier', 'mensch', 'unklar'):
    pool = [r for r in src if r[6] == c]
    for r in random.sample(pool, min(10, len(pool))):
        smp.append(r)
wr('stichprobe.tsv', H, smp)

# Konzepte Tier: Zahl Senses und Korpus-Tokens je Konzept (Konzeptliste + Kandidaten)
cand = ['concept_14011240', 'concept_14021230', 'concept_14012000', 'concept_14025000', 'concept_13060000',
        'concept_23303110', 'concept_23303400', 'concept_14000000', 'concept_14010000', 'concept_14020000',
        'concept_14030000', 'concept_14040000', 'concept_14050000', 'concept_14060000', 'concept_14080000',
        'concept_14100000', 'concept_14011300', 'concept_14021300', 'concept_14031300', 'concept_14028000',
        'concept_14011200', 'concept_14021200', 'concept_14031200', 'concept_14042000', 'concept_14052000',
        'concept_14081200', 'concept_21044000', 'concept_21111000']
cs_count = collections.Counter()
for s, cs in sense_c.items():
    for c in cs:
        cs_count[c] += 1
sense_in_both = collections.Counter()
for s in TSET:
    for c in sense_c[s]:
        sense_in_both[c] += 1
wr('konzepte-tier.tsv', ['concept_id', 'de', 'broader', 'senses_lexikon_gesamt', 'davon_zusammen_mit_21111000', 'in_tierwortliste'],
   [[c, cname.get(c, '?'), cbroad.get(c, ''), cs_count[c], sense_in_both[c], 'ja' if c in TIER_SET else ''] for c in cand])

# Zusammenfassung
S = []
S.append('Dateien %d, w gesamt %d' % (n_files, total_w))
S.append('Senses lexicon.xml gesamt %d; mit concept_21111000: %d (distinct %d), Lemmata: %d' % (len(sense_c), len(target_senses), len(TSET), len(target_lemmas)))
S.append('Tierkonzepte (%d): %s' % (len(TIER_CONCEPTS), ', '.join(c + ' ' + cname[c] for c in TIER_CONCEPTS)))
S.append('Lebensmittelkonzepte (Ausschluss): Teilbaum concept_21111300, %d Konzepte' % len(FOOD_SET))
S.append('Menschkonzepte: %d Konzepte (Teilbaeume 21010000, 21103000, 23112000, 23112500)' % len(MENSCH_SET))
S.append('Tierwort-Lemmata %d (davon mit Lebensmittel-Sense %d); Mensch-Lemmata %d; Pronomen-Lemmata %s' % (
    len(tier_lemmas), sum(1 for l in tier_lemmas if LF[l][1]), len(mensch_lemmas), [(l, orth[l]) for l in pron_lemmas]))
S.append('Belege (w mit ana-Token einer Ziel-Sense, je w einmal): %d; tier %d, mensch %d, unklar %d' % (
    tokens_target_unique, cls_unique['tier'], cls_unique['mensch'], cls_unique['unklar']))
S.append('Summe belege_gesamt ueber Senses: %d' % sum(sense_n.values()))
S.append('Belege ohne ana in Ziel-Lemmata: %d' % sum(ana_missing.values()))
for k, v in sorted(rule_fire.items()):
    S.append('Regel %s: %d' % (k, v))
S.append('Fall-Belege (abebizen/lecken): %d' % len(case_rows))
open(OUT + '/zusammenfassung.txt', 'w', encoding='utf8').write('\n'.join(S) + '\n')
print('\n'.join(S))
