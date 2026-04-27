#!/usr/bin/env python3
"""Auto-classify unresolved 'in' tokens in wzb-sense-pending.tsv using lexical heuristics."""
import csv, sys, re
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

TEMPORAL_WORDS = {
    'tage','tagen','tag','iare','iar','czit','czite','cziten','zeit','czeit',
    'nacht','nachte','nechte','stunde','stunden','monat','monaten','woche','wochen',
    'morgen','abent','abende','ewigkeit','ewickeit','czukunft','zukvnft',
    'anfange','anfang','ende','iaren','mened','meneden','stunt',
    'geperungen','geperunge','gepurt',
    'sibenden','achten','neunden','czehenden','elften','czwelften',
    'ersten','czweiten','dritten','vierden','funften','sechsten',
    'tagen','czeiten','nachten','stunden','iare','mene',
    'ewigem','ewickeit','ewige','ewigen',
}
SPATIAL_WORDS = {
    'erden','erde','lande','land','landes','landen','stat','stette','stetten',
    'wasser','wassern','mitte','arche','archen','hous','hause','hauses','house',
    'burg','burge','purge','wuste','wustenunge','paradis','velt','velde','wald',
    'more','mer','wege','wegen','stein','berg','dorf','czelt','geczelten','geczelt',
    'geczelde','ort','himele','himel','tempel','grabe','graben',
    'norden','suden','osten','westen','fluse','flussen','lager',
    'vaterlande','vaterland','garten','hant','handen','hende','hendin','henden',
    'angesicht','angesichte','angesichts','ougen','ouge','mvnde','munde',
    'herczen','herzen','heilicheit','heilikeit',
    'eingange','eingang','ausgang','ausgange','tur','tore','lant',
    'tal','talen','teile','teilen','breite','lenge','vmringe',
    'egipten','israel','canaan','moab','babylon','iodan','iordane',
    'steten','stete','stetten',
    'hutte','hauss','gemach','kamer','kammer','sale',
    'purgen','stetten','roten','velde','steden','steten',
    'hausse','richen','rich','gezcelt','gezcelten',
    'volke','volkes','getzelde','geczelde','feldes',
    'haenden','antlicz','antlicze','huse','henden',
}
RELATIONAL_WORDS = {
    'trewen','trewe','vreude','vreuden','sunden','sunde','namen','liebe',
    'arbeit','leide','swerte','wetaden','sweisse','angeste','angest','not',
    'gnaden','craft','gerechtigkeit','gehorsam','czorne','demut','hunger',
    'forme','gestalt','geslechte','geslechten','gleichnusse','smerczen',
    'wercke','sorgen','clage','wetage',
    'vleische','blute','blut','fride','czorn',
    'heiligkeit','vnreinigkeit','reinheit',
    'gegenwortigen','gegenwurtigen',
}
ARTICLES = {
    'dem','der','das','die','ein','einen','einem','einer','des',
    'iren','seinen','ihren','seinem','dein','deinen','deiner','deinem',
    'vnserm','vnserem','vnser','ir','irs','ires','irem','iren',
    'allen','disen','disem','dirre','dirres','sulchem','solchem',
    'welchem','welches','solche','solchen','aller','alle','dise',
    'iedem','ieglichem','ganczem','ewigen','selben','den','ewern',
    'ewer','deine','meiner','meinem','meines','mein','meinen',
    'deines','deiner','deinem','seiner','seinem','seines','ewerr',
    'ewrn','ewrm','ewrem','diser','andern','vnsere',
    'sein','seine','seinen','seinem','seiner',
    'iren','irer','irm','ires',
    'grosse','grossen','grossem','gar',
}

PRONOUN_PREPS = re.compile(
    r'\b(czu|zu|mit|von|ous|vor|bei|vnd|durch|vmb|vmbe|an|ouf)\s+\[in\]', re.IGNORECASE)
PRONOUN_POST = re.compile(r'\[in\]\s+(hin\b|nicht\b|sie\b|her\b|yn\b|du\b|ich\b)', re.IGNORECASE)
PRONOUN_VERB = re.compile(
    r'(gesegent|sante|furte|stiesse|saczte|machten|vorterbte|horte|nam|namen|macht|genumen|'
    r'berawe|gab|schepfte|geheissen|hatte|hat|lobete|wuste|funden|fant|vant|rief|'
    r'liebet|geleitet|leitete|bracht|brachte|erhoret|empfangen|beschniden|besniten|erschlagen|'
    r'erslug|segen|segente|rufend|wolde|solde|wil|sprach|sehend|sehende|sehet|'
    r'truge|trugen|trug|brechten|sach|sahen|antwurte|erkante|lizte|liezte|'
    r'gesehen|gesant|geschicket|gesendet|erwelet|gesegnete)\s+\[in\]', re.IGNORECASE)
IN_IN = re.compile(r'\[in\]\s+in\b', re.IGNORECASE)

SENSE_MAP = {
    'temporal':   'lemma_3028_sense_4833',
    'spatial':    'lemma_3028_sense_4834',
    'relational': 'lemma_3028_sense_63605',
    'pronoun':    'ABSTAIN',
}
NOTE_MAP = {
    'temporal':   'heuristic-auto: right-context head noun is a time word -> temporal sense',
    'spatial':    'heuristic-auto: right-context head noun is a place/body word -> spatial sense',
    'relational': 'heuristic-auto: right-context head noun is abstract/relational -> relational sense',
    'pronoun':    'PROBABLE LEMMA MISMATCH: context pattern indicates in = pronoun (ihnen/ihn/sie), not preposition',
}


def classify(ctx):
    if PRONOUN_PREPS.search(ctx) or PRONOUN_POST.search(ctx) or PRONOUN_VERB.search(ctx):
        return 'pronoun'
    if IN_IN.search(ctx):
        return 'pronoun'
    m = re.search(r'\[.*?\]\s*(.*)', ctx)
    right = m.group(1).lower().split() if m else []
    head = None
    for word in right:
        word = re.sub(r'[.,;:!?]', '', word)
        if word not in ARTICLES:
            head = word
            break
    if head:
        if head in TEMPORAL_WORDS:  return 'temporal'
        if head in SPATIAL_WORDS:   return 'spatial'
        if head in RELATIONAL_WORDS: return 'relational'
    return 'ambig'


PROJECT = Path(__file__).parent.parent
pending_path = PROJECT / 'Wenzelsbibel' / 'phase3' / 'wzb-sense-pending.tsv'
out_path = PROJECT / 'Wenzelsbibel' / 'phase3' / 'resolutions' / 'wzb-sense-patch-in-auto.tsv'

rows = []
with pending_path.open(encoding='utf-8') as f:
    for row in csv.DictReader(f, delimiter='\t'):
        if row['lemmaRef'] == 'lexicon.xml#lemma_3028' and not row['resolved_sense']:
            rows.append(row)

out_rows = []
ambig_heads = Counter()
for row in rows:
    cat = classify(row['context'])
    if cat != 'ambig':
        conf = 'low' if cat == 'pronoun' else 'high'
        out_rows.append({
            'xml_id': row['xml_id'],
            'resolved_sense': SENSE_MAP[cat],
            'confidence': conf,
            'note': NOTE_MAP[cat],
        })
    else:
        m = re.search(r'\[.*?\]\s*(.*)', row['context'])
        right = m.group(1).lower().split() if m else []
        for word in right:
            word = re.sub(r'[.,;:!?]', '', word)
            if word not in ARTICLES:
                ambig_heads[word] += 1
                break

cats = Counter()
for row in rows:
    cats[classify(row['context'])] += 1

print(f'Total unresolved in: {len(rows)}')
for k, v in cats.most_common():
    print(f'  {k:12s}: {v:4d} ({100*v/len(rows):.1f}%)')
print(f'Auto-classifiable: {len(out_rows)} ({100*len(out_rows)/len(rows):.1f}%)')
print(f'Need manual review: {len(rows)-len(out_rows)}')
print()
print('Top 20 remaining ambiguous heads:')
for w, c in ambig_heads.most_common(20):
    print(f'  {w:20s}: {c}')

with out_path.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['xml_id', 'resolved_sense', 'confidence', 'note'], delimiter='\t')
    w.writeheader()
    w.writerows(out_rows)

print(f'\nWritten {len(out_rows)} rows to {out_path}')
