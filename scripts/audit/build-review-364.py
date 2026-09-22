#!/usr/bin/env python3
"""Read-only corpus extraction for the portable #364 review page (#443)."""
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from mhg_normalizer import normalize_mhg

NS = {'t': 'http://www.tei-c.org/ns/1.0'}
T = '{' + NS['t'] + '}'
ID = '{http://www.w3.org/XML/1998/namespace}id'
LANG = '{http://www.w3.org/XML/1998/namespace}lang'
PRIMARY = {'lemma_' + str(n) for n in [78728, 78748, 79089, 79108, 79268, 79315, 79316, 79408, 79449, 79728, 79808]}


def words(el):
    return ''.join(el.itertext()).strip()


def extract():
    lex = ET.parse(str(ROOT / 'authority-files/lexicon.xml'))
    entries = {e.get(ID): e for e in lex.findall('.//t:entry', NS)}
    concepts = {e.get(ID): e.findtext('t:catDesc/t:term[@xml:lang="de"]', namespaces={**NS, 'xml': 'http://www.w3.org/XML/1998/namespace'}) or e.get(ID)
                for e in ET.parse(str(ROOT / 'authority-files/concepts.xml')).findall('.//t:category', NS)}
    lookup = defaultdict(set)
    for key, el in entries.items():
        for orth in el.findall('t:form/t:orth', NS):
            lookup[normalize_mhg(words(orth))].add(key)
    variants = ET.parse(str(ROOT / 'authority-files/variants.xml'))
    missing = {}
    for el in variants.findall('.//t:entry', NS):
        key = el.get('corresp', '').split('#')[-1]
        forms = sorted({words(f) for f in el.findall('t:form', NS)})
        if key not in entries:
            missing[key] = forms
        else:
            for f in forms:
                lookup[normalize_mhg(f)].add(key)
    assert len(missing) == 35, f'Issue scope changed: {len(missing)} missing entries'
    groups = []
    candidates = {}
    for key, forms in missing.items():
        ids = sorted(set().union(*(lookup[normalize_mhg(f)] for f in forms)))
        groups.append({'id': key, 'forms': forms, 'primary': key in PRIMARY, 'candidates': ids})
        for cid in ids:
            el = entries[cid]
            candidates[cid] = {'id': cid, 'form': el.findtext('t:form/t:orth', namespaces=NS),
                               'pos': [words(p) for p in el.findall('t:gramGrp/t:pos', NS)],
                               'senses': [{'id': s.get(ID), 'concepts': [concepts.get(p.get('target', '').split('#')[-1], p.get('target')) for p in s.findall('t:ptr', NS)]} for s in el.findall('t:sense', NS)]}
    cases = []
    hashes = {}
    ref_pattern = re.compile(rb'lemmaRef="([^"]+)"')
    for p in [ROOT / 'authority-files' / name for name in ['lexicon.xml', 'variants.xml', 'concepts.xml']]:
        hashes[str(p.relative_to(ROOT)).replace('\\', '/')] = hashlib.sha256(p.read_bytes()).hexdigest()
    for path in sorted((ROOT / 'tei').glob('*.tei.xml')):
        raw = path.read_bytes()
        if not any(r.split(b'#')[-1].decode() in missing for m in ref_pattern.finditer(raw) for r in m[1].split()):
            continue
        print('Extracting ' + path.name, flush=True)
        tree = ET.fromstring(raw, ET.XMLParser(collect_ids=False))
        tokens = tree.xpath('.//t:text//*[self::t:w or self::t:pc]', namespaces=NS)
        line_ids = {line: str(n) for n, line in enumerate(tree.iter(T+'l'))}
        title = tree.findtext('t:teiHeader/t:fileDesc/t:titleStmt/t:title', namespaces=NS)
        sigle = path.name.split('.')[0]
        for idx, tok in enumerate(tokens):
            matched = {r.split('#')[-1] for r in tok.get('lemmaRef', '').split()} & missing.keys()
            if not matched:
                continue
            assert len(matched) == 1
            key = next(iter(matched))
            def context(radius):
                out = []
                for t in tokens[max(0, idx-radius):idx+radius+1]:
                    line = next((a for a in t.iterancestors() if a.tag == T+'l'), None)
                    out.append({'text': words(t), 'id': t.get(ID), 'line': line.get('n', '') if line is not None else '',
                                'lineId': line_ids[line] if line is not None else '',
                                'target': t is tok, 'related': key in {r.split('#')[-1] for r in t.get('lemmaRef', '').split()},
                                'join': t.get('join', ''), 'pc': t.tag == T+'pc'})
                return out
            ancestors = list(tok.iterancestors())
            line = next((a for a in ancestors if a.tag == T+'l'), None)
            page = tok.xpath('preceding::t:pb[1]/@n', namespaces=NS)
            old = {a: tok.get(a, '') for a in ['lemmaRef', 'ana', 'corresp', 'pos']}
            cases.append({'id': tok.get(ID), 'group': key, 'form': words(tok), 'sigle': sigle, 'title': title,
                          'line': line.get('n', '') if line is not None else '', 'page': page[0] if page else '',
                          'old': old, 'context': context(65), 'extended': context(180)})
        hashes[str(path.relative_to(ROOT)).replace('\\', '/')] = hashlib.sha256(raw).hexdigest()
    groups.sort(key=lambda g: (not g['primary'], g['forms'][0], g['id']))
    for g in groups:
        g['caseIds'] = [c['id'] for c in cases if c['group'] == g['id']]
    assert len(cases) == 66 and len({c['id'] for c in cases}) == 66
    assert sum(len(g['caseIds']) for g in groups if g['primary']) == 29
    payload = {'issue': 364, 'schema': 'mhdbdb-review-364-v1', 'date': date.today().isoformat(),
               'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'sources': hashes, 'groups': groups, 'cases': cases, 'candidates': candidates}
    payload['fingerprint'] = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return payload


if __name__ == '__main__':
    data = extract()
    if '--extract' in sys.argv:
        target = Path(sys.argv[sys.argv.index('--extract') + 1])
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    else:
        template = Path(__file__).with_name('review-364.template.html').read_text(encoding='utf-8')
        target = ROOT / '364-lemma-review.html'
        target.write_text(template.replace('__REVIEW_DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')), encoding='utf-8')
    print(f'{target}: {len(data["groups"])} groups, {len(data["cases"])} tokens; 11/29 primary')
