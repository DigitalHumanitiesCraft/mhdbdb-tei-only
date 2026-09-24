#!/usr/bin/env python3
"""
Regenerate authority-files/variants.xml from the current TEI corpus (Issue #44 / #115).

variants.xml is a DERIVED authority file: it maps each orthographic-variant id
(`type_N`) to its surface form, grouped under the lemma it attests. The original
generator (scripts/extract-variants.py on the archived `initial-data-wrangling`
branch) read the pre-#32 compound `@wordRef`; #32 migrated that to
`@corresp="variants.xml#type_N"`, so the old script no longer runs and the file
drifted (64,287 forms missing as of 2026-05). This is the maintained, post-#32
replacement.

Per <w> with @lemmaRef and a variants @corresp it records (lemma, type, form):
  <w lemmaRef="lexicon.xml#lemma_7672" corresp="variants.xml#type_93122">wißent</w>
  -> entry lemma_7672 / <form xml:id="type_93122">wißent</form>

xml:id uniqueness: a `type_N` is one orthographic form of one lemma. If the
corpus attests a type id with more than one form or under more than one lemma
(noise), the most frequent wins (ties: smallest lemma number / alphabetical
form) so each type id is emitted exactly once. Such collisions are reported.

Negative type ids (legacy punctuation codes, #115) are skipped. The two
`<?xml-model?>` PIs (added in #32) are preserved.

Verwaiste Typ-Tokens im Lexikon: lexicon.xml fuehrt je Sense in sense/@ana
eine Leerzeichenliste von #type_N. Faellt ein Typ bei der Regeneration aus
variants.xml, zeigt sein Token ins Leere, und kein Build liest die Liste, also
merkt es niemand (#228, JOURNAL 2026-09-24 Paket A4: 83 Tokens in einem Lauf,
dazu 105 aeltere). --apply entfernt deshalb im selben Lauf jedes Token, dessen
Typ in der eben geschriebenen variants.xml nicht vorkommt; wird eine Liste
leer, faellt das Attribut (Schema: ana optional). Der Trockenlauf nennt nur
die Zahl. CI (data-integrity.yml, Freshness variants.xml) verlangt danach auch
fuer lexicon.xml einen leeren Diff, und check-authority-cross-refs.py --check
verlangt 0 verwaiste Tokens.

Usage:
    python scripts/sync/extract-variants.py            # dry-run -> authority-files/variants.regen.xml
    python scripts/sync/extract-variants.py --apply    # overwrite variants.xml, prune lexicon sense/@ana
    python scripts/sync/extract-variants.py --jobs 1   # sequentiell parsen (Default: bis 8 Prozesse)
"""

import concurrent.futures
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from lxml import etree

# Korpusauswahl, -reihenfolge und Worker-Obergrenze teilen sich alle
# Korpus-Leser (#287). scripts/ auf den Pfad, wie in classify-lexicon-backfill.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from corpus_files import PROJECT_ROOT, corpus_files, default_jobs  # noqa: E402

TEI_NS = 'http://www.tei-c.org/ns/1.0'
TEI = f'{{{TEI_NS}}}'
XML = '{http://www.w3.org/XML/1998/namespace}'

# Ein- und Ausgabe an derselben Wurzel (#287). Vorher war die Eingabe
# CWD-relativ und ein Lauf aus dem falschen Verzeichnis scheiterte sichtbar
# (0 Dateien gefunden). Jetzt findet die Eingabe den Korpus immer, also muss
# auch die Ausgabe dorthin zeigen: sonst laese read_existing() stillschweigend
# keine Bestandsdatei (der Diff faellt auf "alles neu") und der Schreibvorgang
# landete woanders.
VARIANTS = PROJECT_ROOT / 'authority-files' / 'variants.xml'
DRY_OUT = PROJECT_ROOT / 'authority-files' / 'variants.regen.xml'
LEXICON = PROJECT_ROOT / 'authority-files' / 'lexicon.xml'

TYPE_POS_RE = re.compile(r'^type_\d+$')        # positive type id only
TYPE_NUM_RE = re.compile(r'^type_(\d+)$')
LEMMA_NUM_RE = re.compile(r'^lemma_(\d+)$')

PI_MODEL = [
    ('xml-model', 'href="../schema/mhdbdb-authority.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"'),
    ('xml-model', 'href="../schema/tei_all.rng"'),
]


def fragment(value):
    """'lexicon.xml#lemma_7672' -> 'lemma_7672' (first whitespace token)."""
    tok = value.split()[0] if value else ''
    return tok.split('#', 1)[1] if '#' in tok else None


def collect_one(fp):
    """Eine Korpusdatei parsen (#284: Worker-Funktion, muss modullevel sein).

    Rueckgabe sind zwei einfache dicts type_id -> {wert: anzahl}. Bewusst keine
    lxml-Objekte: die ueberleben eine Prozessgrenze nicht. Counter waere
    picklebar, plain dict ist kleiner und wird beim Mergen ohnehin in einen
    Counter gefuettert.
    """
    type_form = defaultdict(Counter)
    type_lemma = defaultdict(Counter)
    tree = etree.parse(str(fp))
    for w in tree.iter(f'{TEI}w'):
        lemma_ref = w.get('lemmaRef')
        corresp = w.get('corresp')
        if not lemma_ref or not corresp:
            continue
        lemma_id = fragment(lemma_ref)
        if not lemma_id:
            continue
        form = ''.join(w.itertext()).strip()
        if not form:
            continue
        for token in corresp.split():
            if not token.startswith('variants.xml#'):
                continue
            type_id = token.split('#', 1)[1]
            if not TYPE_POS_RE.match(type_id):
                continue  # negative/malformed -> skip (#115)
            type_form[type_id][form] += 1
            type_lemma[type_id][lemma_id] += 1
    return ({t: dict(c) for t, c in type_form.items()},
            {t: dict(c) for t, c in type_lemma.items()})


def collect(base_files, jobs=1):
    """type_id -> Counter(form), type_id -> Counter(lemma_id).

    Parallelisiert wird nur das Parsen (#284); summiert wird im Elternprozess.

    Die Summen sind ordnungsunabhaengig, und resolve() bricht seit #284 jeden
    Gleichstand explizit (haeufigste Form, dann alphabetisch; haeufigstes
    Lemma, dann lemma_key). Vorher tat es das nicht ganz: der Lemma-Sortkey
    kollabierte nicht-numerische IDs auf einen konstanten Wert, womit die
    Merge-Reihenfolge mitentschied. Das war der Grund, dieses map geordnet zu
    halten; der Grund ist jetzt weg, die Ordnung bleibt trotzdem, weil sie die
    Fortschrittsausgabe in Dateireihenfolge haelt und nichts kostet.
    """
    type_form = defaultdict(Counter)
    type_lemma = defaultdict(Counter)
    if jobs <= 1:
        results = map(collect_one, base_files)
        pool = None
    else:
        pool = concurrent.futures.ProcessPoolExecutor(max_workers=jobs)
        results = pool.map(collect_one, base_files, chunksize=1)
    try:
        for i, (file_form, file_lemma) in enumerate(results):
            if (i + 1) % 100 == 0:
                print(f'  {i + 1}/{len(base_files)}...', flush=True)
            for type_id, forms in file_form.items():
                type_form[type_id].update(forms)
            for type_id, lemmas in file_lemma.items():
                type_lemma[type_id].update(lemmas)
    finally:
        if pool is not None:
            # cancel_futures: map() reicht alle 667 Tasks sofort ein. Ohne das
            # wartet ein Abbruch (z. B. XMLSyntaxError in Datei 3) erst die
            # restlichen Dateien ab, bevor der Traceback erscheint.
            pool.shutdown(cancel_futures=True)
    return type_form, type_lemma


def resolve(type_form, type_lemma):
    """Pick one lemma + one form per type id.

    Return (lemma_to_types, type_to_form, type_to_lemma, multi_form, multi_lemma).
    type_to_lemma lets the diff look up a type's lemma in O(1) instead of scanning
    lemma_to_types per type (which was O(types x lemmas) and hung the run).
    """
    lemma_to_types = defaultdict(list)
    type_to_form = {}
    type_to_lemma = {}
    multi_form = multi_lemma = 0
    for type_id in type_form:
        forms = type_form[type_id]
        lemmas = type_lemma[type_id]
        if len(forms) > 1:
            multi_form += 1
        if len(lemmas) > 1:
            multi_lemma += 1
        # most frequent; ties -> alphabetical form / smallest lemma number
        # lemma_key statt des frueheren 1<<62-Fallbacks (#284): der kollabierte
        # ALLE nicht-numerischen Lemma-IDs auf denselben Sortkey, womit der
        # stabile Sort entschied, also die Einfuegereihenfolge des Counters,
        # also die Reihenfolge, in der die Korpusdateien gelesen wurden. Beim
        # sequentiellen Lauf faellt das nicht auf; es macht die Ausgabe aber
        # von etwas abhaengig, das sie nicht sein sollte. lemma_key bricht den
        # Gleichstand alphabetisch und ist damit vollstaendig explizit.
        # Der heutige Korpus hat keine solchen IDs, das Artefakt ist
        # unveraendert (per Hash geprueft).
        form = sorted(forms.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        lemma = sorted(lemmas.items(), key=lambda kv: (-kv[1], lemma_key(kv[0])))[0][0]
        type_to_form[type_id] = form
        type_to_lemma[type_id] = lemma
        lemma_to_types[lemma].append(type_id)
    return lemma_to_types, type_to_form, type_to_lemma, multi_form, multi_lemma


def lemma_key(lemma_id):
    m = LEMMA_NUM_RE.match(lemma_id)
    return (0, int(m.group(1))) if m else (1, lemma_id)


def type_key(type_id):
    m = TYPE_NUM_RE.match(type_id)
    return int(m.group(1)) if m else 1 << 62


def build_tree(lemma_to_types, type_to_form, n_files, date_text):
    root = etree.Element(f'{TEI}TEI', nsmap={None: TEI_NS})
    header = etree.SubElement(root, f'{TEI}teiHeader')
    fileDesc = etree.SubElement(header, f'{TEI}fileDesc')
    titleStmt = etree.SubElement(fileDesc, f'{TEI}titleStmt')
    etree.SubElement(titleStmt, f'{TEI}title').text = 'MHDBDB Orthographic Variants Index'
    respStmt = etree.SubElement(titleStmt, f'{TEI}respStmt')
    etree.SubElement(respStmt, f'{TEI}resp').text = 'Extracted from'
    etree.SubElement(respStmt, f'{TEI}name').text = f'MHDBDB TEI Corpus ({n_files} texts)'
    pubStmt = etree.SubElement(fileDesc, f'{TEI}publicationStmt')
    etree.SubElement(pubStmt, f'{TEI}publisher').text = 'MHDBDB'
    # Semantik: <date> = Stand der Daten, nicht letzter Script-Lauf — siehe main()
    etree.SubElement(pubStmt, f'{TEI}date').text = date_text
    sourceDesc = etree.SubElement(fileDesc, f'{TEI}sourceDesc')
    etree.SubElement(sourceDesc, f'{TEI}p').text = 'Automatically extracted attestations from TEI corpus'

    text = etree.SubElement(root, f'{TEI}text')
    body = etree.SubElement(text, f'{TEI}body')
    div = etree.SubElement(body, f'{TEI}div')
    div.set('type', 'orthographicVariants')

    for lemma_id in sorted(lemma_to_types, key=lemma_key):
        entry = etree.SubElement(div, f'{TEI}entry')
        entry.set('corresp', f'lexicon.xml#{lemma_id}')
        for type_id in sorted(lemma_to_types[lemma_id], key=type_key):
            form = etree.SubElement(entry, f'{TEI}form')
            form.set(f'{XML}id', type_id)
            form.text = type_to_form[type_id]

    tree = etree.ElementTree(root)
    for target, content in PI_MODEL:
        root.addprevious(etree.ProcessingInstruction(target, content))
    return tree


HEADER_DATE = f'{TEI}teiHeader/{TEI}fileDesc/{TEI}publicationStmt/{TEI}date'
HEADER_NAME = f'{TEI}teiHeader/{TEI}fileDesc/{TEI}titleStmt/{TEI}respStmt/{TEI}name'


def read_existing():
    """Bestehende variants.xml in EINEM Parse einlesen (Diff + Header).

    Return (type_map, date_text, name_text):
      type_map:  type_id -> (lemma_id, form), fuer den Diff
      date_text: <date>-Text oder None (Datei fehlt / kein date)
      name_text: respStmt/<name>-Text ("MHDBDB TEI Corpus (N texts)") oder None
    """
    if not VARIANTS.exists():
        return {}, None, None
    out = {}
    tree = etree.parse(str(VARIANTS))
    for entry in tree.iter(f'{TEI}entry'):
        lemma_id = fragment(entry.get('corresp') or '')
        for form in entry.findall(f'{TEI}form'):
            tid = form.get(f'{XML}id')
            if tid:
                out[tid] = (lemma_id, (form.text or '').strip())
    date_text = tree.findtext(HEADER_DATE) or None
    name_text = tree.findtext(HEADER_NAME)
    return out, date_text, name_text


def orphan_ana_tokens(lexicon_root, type_ids):
    """sense-xml:id -> (alle Tokens, verwaiste Tokens) fuer jede Sense, deren
    @ana mindestens ein #type_N ohne Gegenstueck in type_ids traegt.

    Geteilt mit check-authority-cross-refs.py, damit Bereinigung und Gate
    dieselbe Menge meinen. Gesplittet wird an Leerzeichen: ein Muster wie
    ana="#type_\\d+" saehe nur die einwertigen Listen, und genau daran ist
    der Befund in #228 zuerst vorbeigegangen (1 statt 83).
    """
    out = {}
    for sense in lexicon_root.iter(f'{TEI}sense'):
        toks = (sense.get('ana') or '').split()
        orphans = [t for t in toks if t.startswith('#type_') and t[1:] not in type_ids]
        if orphans:
            out[sense.get(f'{XML}id')] = (toks, orphans)
    return out


def prepare_lexicon_prune(type_ids):
    """Bereinigten Text von lexicon.xml vorbereiten, ohne etwas zu schreiben.

    Textersetzung statt lxml-Serialisierung, damit der Diff genau die
    betroffenen Attribute zeigt und nicht die ganze Datei. Jeder Anker muss
    genau einmal treffen, und das Ergebnis muss parsen. Laeuft in main() VOR
    dem Schreiben von variants.xml: bricht es ab, ist keine der beiden
    Dateien angefasst (Review Runde 1; vorher stand variants.xml dann schon
    neu im Baum).
    Rueckgabe: (neuer Text oder None, Tokens, Senses).
    """
    orphans = orphan_ana_tokens(etree.parse(str(LEXICON)).getroot(), type_ids)
    n_tokens = sum(len(o) for _, o in orphans.values())
    if not orphans:
        return None, 0, 0
    with open(LEXICON, encoding='utf-8', newline='') as f:
        text = f.read()
    for sid, (toks, raus) in sorted(orphans.items()):
        old = f'<sense xml:id="{sid}" ana="{" ".join(toks)}"'
        rest = [t for t in toks if t not in raus]
        new = f'<sense xml:id="{sid}"' + (f' ana="{" ".join(rest)}"' if rest else '')
        if text.count(old) != 1:
            sys.exit(f'FEHLER: Anker fuer {sid} in lexicon.xml nicht genau einmal '
                     f'gefunden ({text.count(old)}); weder variants.xml noch '
                     f'lexicon.xml geschrieben.')
        text = text.replace(old, new)
    etree.fromstring(text.encode('utf-8'))
    return text, n_tokens, len(orphans)


def parse_jobs(argv):
    """--jobs N aus argv lesen. Default: bis corpus_files.DEFAULT_JOBS_CAP Prozesse.

    Bewusst kein argparse: das Skript liest seine Flags seit jeher direkt aus
    sys.argv, und ein halber Umstieg waere die schlechtere Variante.
    """
    eq = [a for a in argv if a.startswith('--jobs=')]
    if eq:
        # Sonst laeuft `--jobs=1` still mit dem Default-Parallelbetrieb, und
        # genau diese Schreibweise nimmt man zum sequentiellen Debuggen.
        raw = eq[0].split('=', 1)[1]
    elif '--jobs' in argv:
        i = argv.index('--jobs')
        if i + 1 >= len(argv):
            sys.exit('--jobs braucht eine Zahl')
        raw = argv[i + 1]
    else:
        return default_jobs()
    try:
        jobs = int(raw)
    except ValueError:
        sys.exit(f'--jobs braucht eine Zahl, nicht {raw!r}')
    if jobs < 1:
        sys.exit('--jobs muss mindestens 1 sein')
    return jobs


def main():
    apply = '--apply' in sys.argv
    jobs = parse_jobs(sys.argv)
    base_files = corpus_files()
    print(f'Scanning {len(base_files)} corpus files for <w @lemmaRef @corresp>... ({jobs} Prozesse)')
    type_form, type_lemma = collect(base_files, jobs=jobs)
    lemma_to_types, type_to_form, type_to_lemma, multi_form, multi_lemma = resolve(type_form, type_lemma)

    n_types = len(type_to_form)
    n_lemmas = len(lemma_to_types)

    # diff vs current
    cur, old_date, old_name = read_existing()
    new_ids = set(type_to_form)
    cur_ids = set(cur)
    added = new_ids - cur_ids
    removed = cur_ids - new_ids
    form_changed = sum(1 for t in (new_ids & cur_ids) if cur[t][1] != type_to_form[t])
    lemma_changed = sum(1 for t in (new_ids & cur_ids) if cur[t][0] != type_to_lemma[t])

    # Datum nur bei inhaltlicher Aenderung (#125): der semantische Diff
    # (Zaehler oben + Korpusgroesse im Header-<name>) entscheidet ueber den
    # Restamp. Bewusst KEIN Byte-Vergleich: der wuerde bei lxml-
    # Serialisierungs-Drift (lokale Version != requirements.txt-Pin)
    # faelschlich stempeln (Review #146). Ausser Datum und <name> ist der
    # Output eine reine Funktion der Diff-verglichenen Daten, der Diff ist
    # also vollstaendig. <date> bedeutet damit "Stand der Daten".
    today = date.today().isoformat()
    tree = build_tree(lemma_to_types, type_to_form, len(base_files), old_date or today)
    changed = (bool(added or removed or form_changed or lemma_changed)
               or tree.findtext(HEADER_NAME) != old_name)
    if changed and old_date is not None:
        tree.find(HEADER_DATE).text = today
    lexicon_text, ana_tokens, ana_senses = prepare_lexicon_prune(new_ids)
    out = VARIANTS if apply else DRY_OUT
    tree.write(str(out), xml_declaration=True, encoding='UTF-8', pretty_print=True)
    if apply and lexicon_text is not None:
        with open(LEXICON, 'w', encoding='utf-8', newline='') as f:
            f.write(lexicon_text)

    mode = 'APPLIED -> authority-files/variants.xml' if apply else f'DRY-RUN -> {out}'
    print('=' * 60)
    print(f'Regenerate variants.xml  [{mode}]')
    print('=' * 60)
    print(f'Distinct type ids (forms):  {n_types:>9,}')
    print(f'Distinct lemmas (entries):  {n_lemmas:>9,}')
    print(f'Current variants.xml:       {len(cur):>9,} type ids')
    print()
    print(f'  added (new in corpus):    {len(added):>9,}')
    print(f'  removed (gone from corpus):{len(removed):>8,}')
    print(f'  form text changed:        {form_changed:>9,}')
    print(f'  lemma assignment changed: {lemma_changed:>9,}')
    print()
    print(f'Data-quality (resolved by majority):')
    print(f'  type ids with >1 form:    {multi_form:>9,}')
    print(f'  type ids with >1 lemma:   {multi_lemma:>9,}')
    print()
    verb = 'pruned' if apply else 'to prune with --apply'
    print(f'lexicon.xml sense/@ana, orphaned type tokens {verb}: '
          f'{ana_tokens:,} in {ana_senses:,} senses')
    if not apply:
        print(f'\nDry-run only. Inspect {out}, then re-run with --apply.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
