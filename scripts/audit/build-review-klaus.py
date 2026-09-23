#!/usr/bin/env python3
"""Build Klaus' standalone #390/#115 review; read-only TEI extraction.

--extract PATH writes the source snapshot; --snapshot PATH renders a verified
snapshot without parsing again. A snapshot is rejected if a source hash changed.
"""
import argparse
import hashlib
import json
import re
import subprocess
from datetime import date
from pathlib import Path

from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[2]
NS = {'t': 'http://www.tei-c.org/ns/1.0'}
T = '{' + NS['t'] + '}'
ID = '{http://www.w3.org/XML/1998/namespace}id'
LANG = '{http://www.w3.org/XML/1998/namespace}lang'


def text(el):
    return ''.join(el.itertext()).strip()


def parse(path):
    return ET.parse(str(path), ET.XMLParser(collect_ids=False))


def flat(tree):
    """One document-order pass; retain physical milestones and verse numbers."""
    tokens = []
    page = column = line = ''
    breaks = []
    verse_ids = {e: str(i) for i, e in enumerate(tree.iter(T+'l'))}
    body = tree.find('.//t:text', NS)
    for e in body.iter():
        tag = ET.QName(e).localname
        if tag == 'pb':
            page, column, line = e.get('n', ''), '', ''
            breaks.append('Blatt ' + page)
        elif tag == 'cb':
            column, line = e.get('n', ''), ''
            breaks.append('Spalte ' + column)
        elif tag == 'lb':
            line = e.get('n', '')
        elif tag in ('w', 'pc'):
            verse = next((a for a in e.iterancestors() if a.tag == T+'l'), None)
            tokens.append({'id': e.get(ID), 'text': text(e), 'kind': tag,
                           'page': page, 'column': column, 'line': line,
                           'verse': verse.get('n', '') if verse is not None else '',
                           'verseKey': verse_ids.get(verse, ''), 'breaks': breaks,
                           'join': e.get('join', ''),
                           'old': {a: e.get(a, '') for a in ('lemmaRef', 'ana', 'pos', 'corresp')}})
            breaks = []
    return tokens


def context(tokens, first, last, target_ids, radius):
    result = []
    for token in tokens[max(0, first-radius):min(len(tokens), last+radius+1)]:
        result.append({k: token[k] for k in ('id', 'text', 'kind', 'verse', 'verseKey', 'breaks', 'join')}
                      | {'target': token['id'] in target_ids})
    return result


def location(t):
    return ' · '.join(s for s in [f'Vers {t["verse"]}' if t['verse'] else '',
                                 f'Blatt {t["page"]}{t["column"]}' if t['page'] else '',
                                 f'Zeile {t["line"]}' if t['line'] else ''] if s)


def extract():
    source_paths = [ROOT/'authority-files/lexicon.xml', ROOT/'authority-files/concepts.xml',
                    ROOT/'scripts/audit/lexicon-baseline.json']
    lex = parse(source_paths[0])
    entries = {e.get(ID): e for e in lex.findall('.//t:entry', NS)}
    defined = {e.get(ID) for e in lex.iter() if e.get(ID)}
    baseline = json.loads(source_paths[2].read_text(encoding='utf-8'))['tolerated_ids']
    missing = {s for s in baseline if '_sense_' in s and s.split('_sense_')[0] in entries and s not in defined}
    assert len(missing) == 39, f'Expected 39 missing senses, found {len(missing)}'
    concepts = {}
    for e in parse(source_paths[1]).findall('.//t:category', NS):
        term = next((t for t in e.findall('t:catDesc/t:term', NS) if t.get(LANG) == 'de' and not t.get('type')), None)
        concepts[e.get(ID)] = text(term) if term is not None else e.get(ID)
    groups = []
    for sense in sorted(missing):
        lemma = sense.split('_sense_')[0]
        e = entries[lemma]
        senses = [{'id': s.get(ID), 'concepts': [p.get('target').split('#')[-1] for p in s.findall('t:ptr', NS)],
                   'definition': ' '.join(text(x) for x in s.findall('t:def', NS))} for s in e.findall('t:sense', NS)]
        groups.append({'id': sense, 'issue': 115, 'lemma': lemma,
                       'title': e.findtext('t:form/t:orth', namespaces=NS),
                       'pos': [text(p) for p in e.findall('t:gramGrp/t:pos', NS)],
                       'senses': senses, 'caseIds': []})
    group_map = {g['id']: g for g in groups}
    cases = []
    pattern = re.compile(rb'#(?:' + b'|'.join(s.encode() for s in sorted(missing)) + rb')(?=[\s"])')
    for path in sorted((ROOT/'tei').glob('*.tei.xml')):
        raw = path.read_bytes()
        if path.name != 'WZB.tei.xml' and not pattern.search(raw):
            continue
        print('Extracting ' + path.name, flush=True)
        source_paths.append(path)
        tree = ET.fromstring(raw, ET.XMLParser(collect_ids=False))
        tokens = flat(tree)
        title = tree.findtext('t:teiHeader/t:fileDesc/t:titleStmt/t:title', namespaces=NS)
        sigle = path.name.split('.')[0]
        for i, tok in enumerate(tokens):
            matches = [r.split('#')[-1] for r in tok['old']['ana'].split() if r.split('#')[-1] in missing]
            for sense in matches:
                cid = sense + ':' + tok['id']
                case = {'id': cid, 'issue': 115, 'group': sense, 'tokenIds': [tok['id']], 'form': tok['text'],
                        'sigle': sigle, 'work': title, 'location': location(tok), 'verse': tok['verse'], 'old': tok['old'],
                        'context': context(tokens, i, i, {tok['id']}, 35),
                        'extended': context(tokens, i, i, {tok['id']}, 120)}
                cases.append(case)
                group_map[sense]['caseIds'].append(cid)
        if sigle == 'WZB':
            wi = [i for i, tok in enumerate(tokens) if tok['kind'] == 'w']
            def upper(tok):
                return not tok['old']['lemmaRef'] and tok['text'].isupper()
            j = 0
            while j < len(wi):
                if not upper(tokens[wi[j]]):
                    j += 1
                    continue
                start = j
                while j < len(wi) and upper(tokens[wi[j]]):
                    j += 1
                if start == 0 or j == len(wi):
                    continue
                left, right = tokens[wi[start-1]], tokens[wi[j]]
                if left['old']['lemmaRef'] or right['old']['lemmaRef']:
                    continue
                mids = tokens[wi[start]:wi[j]]
                cid = '390:' + left['id'] + ':' + right['id']
                group = {'id': cid, 'issue': 390, 'title': left['text']+' | '+right['text'], 'caseIds': [cid]}
                groups.append(group)
                cases.append({'id': cid, 'issue': 390, 'group': cid, 'tokenIds': [left['id'], right['id']],
                              'form': group['title'], 'sigle': sigle, 'work': title,
                              'location': location(left)+' → '+location(right), 'verse': '',
                              'left': left['text'], 'right': right['text'], 'joined': left['text']+right['text'],
                              'interruption': ' '.join(t['text'] for t in mids),
                              'middleIds': [tokens[wi[k]]['id'] for k in range(start, j)],
                              'context': context(tokens, wi[start-1], wi[j], {left['id'], right['id']}, 35),
                              'extended': context(tokens, wi[start-1], wi[j], {left['id'], right['id']}, 120),
                              'old': {'left': left['old'], 'right': right['old']}})
    groups.sort(key=lambda g: (g['issue'] != 390, -len(g['caseIds']) if g['issue'] == 115 else 0, g['title']))
    assert all(g['caseIds'] for g in groups)
    senses_count = sum(c['issue'] == 115 for c in cases)
    boundaries_count = sum(c['issue'] == 390 for c in cases)
    assert senses_count == 264, f'Expected 264 sense references, found {senses_count}'
    assert boundaries_count == 22, f'Expected 22 word boundaries, found {boundaries_count}'
    sources = {str(p.relative_to(ROOT)).replace('\\','/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    data = {'schema': 'mhdbdb-klaus-390-115-v1', 'issues': [390,115], 'date': date.today().isoformat(),
            'commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'sources': sources, 'groups': groups, 'cases': cases, 'concepts': concepts}
    data['fingerprint'] = hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--extract', type=Path)
    parser.add_argument('--snapshot', type=Path)
    args = parser.parse_args()
    if args.snapshot:
        data = json.loads(args.snapshot.read_text(encoding='utf-8'))
        for name, digest in data['sources'].items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, f'Source changed: {name}'
    else:
        data = extract()
    if args.extract:
        args.extract.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
        target = args.extract
    else:
        template = Path(__file__).with_name('review-klaus.template.html').read_text(encoding='utf-8')
        base = Path(__file__).with_name('review-364.template.html').read_text(encoding='utf-8')
        template = template.replace('__BASE_STYLE__', re.search(r'<style>(.*?)</style>', base, re.S)[1])
        target = ROOT/'Klaus-Pruefung-390-115.html'
        target.write_text(template.replace('__REVIEW_DATA__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c')),encoding='utf-8')
    print(f'{target}: {len(data["groups"])} groups, {len(data["cases"])} cases',flush=True)
