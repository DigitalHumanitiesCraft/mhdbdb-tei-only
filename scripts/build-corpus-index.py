#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Corpus Index

Generates pre-built corpus index from tei/ directory (667 TEI files).
Output: data/corpus-index.json.gz (~3-5 MB compressed)

Index structure (v4.2.0 - DOCUMENT-LEVEL + LINE BOUNDARIES):
{
  "version": "4.2.0",
  "totalTexts": 667,
  "totalLemmata": 45000,
  "texts": [
    {
      "id": "ABG",
      "filename": "ABG.tei.xml",
      "title": "Von der Abgeschiedenheit",
      "author": "Meister Eckhart",
      "authorRef": "#person_445",
      "workRef": "works.xml#work_89",   # verbatim aus msIdentifier/@corresp, mit Datei-Praefix
      "genre": "",                      # leer in allen 667 Texten: term[@type="genre"] kommt
                                        # im Korpus nicht vor (DATA-MODEL, XPath-Tabelle)
      "wordCount": 1500,
      "words": ["lemma_879", "lemma_123", "lemma_879", ...],  # all lemmatized <w> in <body> (only @lemmaRef-bearing)
      "lemmata": {
        "lemma_879": [0, 2, 15],  # Word positions
        "lemma_123": [1]
      },
      "lineStarts": [0, 8, 15, ...],   # word-index where each <l> starts (#47.3)
      "lineEnds":   [7, 14, 22, ...]   # word-index where each <l> ends (inclusive)
    }
  ],
  "lemmaIndex": {
    "lemma_879": ["ABG", "BRZ", "HZU2"],  # Texts containing this lemma
    "lemma_123": ["ABG"]
  }
}

Notes on lineStarts/lineEnds (added in v4.1.0 for #47.3):
- Same length as the number of <l> elements with at least one indexed word.
- Empty for prose texts without <l> elements (~10% of corpus).
- A lemma occurrence at position P is at Versanfang iff P in lineStarts,
  at Versende iff P in lineEnds.
- Words outside any <l> (e.g. inside <head>, <note>, mid-paragraph <fw>)
  match neither.
"""

import argparse
import concurrent.futures
import json
import gzip
import subprocess
import sys
import time
from pathlib import Path
from collections import defaultdict

# Check dependencies
try:
    from lxml import etree
except ImportError:
    print("❌ ERROR: lxml not installed")
    print("   Install with: pip install lxml")
    sys.exit(1)

# Import our normalizer
sys.path.insert(0, str(Path(__file__).parent))
from mhg_normalizer import normalize_mhg
from tei_namespaces import get_namespaces
# PROJECT_ROOT/TEI_DIR kommen mit, damit TEI_DIR.relative_to(PROJECT_ROOT) in
# check_working_tree() nicht davon abhaengt, ob beide gleich aufgeloest sind.
from corpus_files import PROJECT_ROOT, TEI_DIR, corpus_files, default_jobs

# Paths
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_FILE = DATA_DIR / 'corpus-index.json.gz'

# TEI namespace
TEI_NS = {'tei': 'http://www.tei-c.org/ns/1.0'}


def extract_metadata(filepath):
    """Extract metadata from TEI file."""
    try:
        tree = etree.parse(str(filepath))
        ns = get_namespaces(tree)

        # Get sigle from filename or XML
        filename = filepath.name
        sigle = filename.replace('.tei.xml', '')

        # Try to get sigle from idno
        sigle_nodes = tree.xpath('//tei:idno[@type="sigle"]/text()', namespaces=ns)
        if sigle_nodes:
            sigle = sigle_nodes[0].strip()

        # Get title
        # Wie beim Autor unten (#228): itertext() statt text() gegen mixed
        # content, und ' '.join(...split()) gegen die XML-Einrueckung. Sechs
        # Titel trugen einen Umbruch mitten im Wert, sichtbar bis in
        # api/texts/*.json.
        title_nodes = tree.xpath('//tei:titleStmt/tei:title', namespaces=ns)
        title = (' '.join(''.join(title_nodes[0].itertext()).split())
                 if title_nodes else sigle)

        # Get author
        author = ''
        authorRef = ''
        author_nodes = tree.xpath('//tei:titleStmt/tei:author', namespaces=ns)
        if author_nodes:
            author_el = author_nodes[0]
            # itertext() statt .text (#228): schema/mhdbdb.rnc erlaubt in
            # titleStmt/author <name>-Kinder. .text laese dann den leeren
            # Textknoten davor und der Index bekaeme einen leeren Autor,
            # genau die Klasse Fehler, die dieser Zweig gerade beseitigt.
            # Heute hat keine der 667 Dateien dort Kindelemente, der Index
            # bleibt also byte-identisch.
            # ' '.join(...split()) statt .strip() (#228): in LUU steht der
            # Autorname ueber zwei eingerueckte Zeilen, .strip() trimmt nur die
            # Raender und liess den Umbruch samt Einrueckung mitten im
            # Namen stehen, in Index und API. XML-Einrueckung ist beliebig,
            # die Normalisierung gehoert deshalb zum Leser, nicht in die
            # Quelldatei.
            author = ' '.join(''.join(author_el.itertext()).split())
            authorRef = author_el.get('ref', '')

        # Get work reference
        workRef = ''
        ms_id_nodes = tree.xpath('//tei:msIdentifier', namespaces=ns)
        if ms_id_nodes:
            workRef = ms_id_nodes[0].get('corresp', '')

        # Get genre (if available - may not be in all files)
        genre = ''
        # Genre might be in different places, try a few options
        genre_nodes = tree.xpath('//tei:keywords/tei:term[@type="genre"]/text()', namespaces=ns)
        if not genre_nodes:
            genre_nodes = tree.xpath('//tei:term[@type="genre"]/text()', namespaces=ns)
        if genre_nodes:
            genre = genre_nodes[0].strip()

        return {
            'id': sigle,
            'filename': filename,
            'title': title,
            'author': author,
            'authorRef': authorRef,
            'workRef': workRef,
            'genre': genre
        }

    except Exception as e:
        print(f"⚠️  Error extracting metadata from {filepath.name}: {e}")
        return None


def extract_word_data(filepath, text_id):
    """
    Extract word data using document-level indexing (v4.1.0).

    Returns: (words_list, lemmata_dict, word_count, line_starts, line_ends)
    where:
      words_list = ["lemma_879", "lemma_123", ...]  # ALL words in <body> in document order
      lemmata_dict = {"lemma_879": [0, 2, 15], ...}
      line_starts = [0, 8, 15, ...]  # word-index where each <l> starts
      line_ends   = [7, 14, 22, ...] # word-index where each <l> ends (inclusive)
    """
    try:
        tree = etree.parse(str(filepath))

        # Get body element
        TEI = '{http://www.tei-c.org/ns/1.0}'
        body = tree.find(f'.//{TEI}body')
        if body is None:
            return [], {}, 0, [], []

        words = []  # All lemma IDs in document order
        lemmata = defaultdict(list)
        word_count = 0

        line_starts = []
        line_ends = []
        # Stack tracks <l> nesting depth (in practice always 0 or 1, but defensive)
        # Each frame holds (first_w_idx, last_w_idx) for the currently-open <l>.
        l_stack = []

        # Single-pass iterwalk: start/end events for <w> and <l> together.
        # This avoids lxml's proxy-id instability between separate .iter() calls.
        for event, el in etree.iterwalk(body, events=('start', 'end'),
                                         tag=(f'{TEI}w', f'{TEI}l')):
            tag = el.tag

            if tag == f'{TEI}l':
                if event == 'start':
                    l_stack.append([None, None])  # [first_idx, last_idx]
                else:  # end
                    frame = l_stack.pop()
                    if frame[0] is not None:
                        line_starts.append(frame[0])
                        line_ends.append(frame[1])
                continue

            # tag == <w>, event == 'start' (we ignore <w>-end events)
            if event != 'start':
                continue

            lemma_ref = el.get('lemmaRef')
            if not lemma_ref:
                continue
            text_content = ''.join(el.itertext()).strip()
            if not text_content:
                continue

            # Mehrfach-Referenzen (CONTRACTS §B.1: whitespace-getrennt, z.B.
            # "lexicon.xml#lemma_308 lexicon.xml#lemma_5") pro Fragment
            # auflösen — der alte split('#')[1] erzeugte daraus den defekten
            # Key "lemma_308 lexicon.xml" (#170). words[] behält die ERSTE ID
            # (ein Slot pro Token, Format unverändert); lemmata{} listet die
            # Position unter JEDER referenzierten ID, damit die Index-Suche
            # jedes der Lemmata findet. Heute 0 Mehrfach-Fälle im Korpus:
            # der Rebuild muss byte-identisch bleiben.
            lemma_ids = [
                frag.split('#')[1] if '#' in frag else frag
                for frag in lemma_ref.split()
            ]
            if not lemma_ids:
                continue

            word_idx = len(words)
            words.append(lemma_ids[0])
            for lemma_id in dict.fromkeys(lemma_ids):
                lemmata[lemma_id].append(word_idx)
            word_count += 1

            # If we're inside one or more <l>, update each open frame.
            # (Inner-most <l> defines Versanfang/Versende; outer frames are
            # extremely rare in TEI but cost nothing to track.)
            for frame in l_stack:
                if frame[0] is None:
                    frame[0] = word_idx
                frame[1] = word_idx

        return words, dict(lemmata), word_count, line_starts, line_ends

    except Exception as e:
        print(f"⚠️  Error extracting word data from {filepath.name}: {e}")
        return [], {}, 0, [], []


def process_tei_file(filepath):
    """Process single TEI file and return text data."""
    # Extract metadata
    metadata = extract_metadata(filepath)
    if not metadata:
        return None

    text_id = metadata['id']

    # Extract full word data + line boundaries (document-level)
    words, lemmata, word_count, line_starts, line_ends = extract_word_data(filepath, text_id)

    # Combine
    text_data = {
        **metadata,
        'wordCount': word_count,
        'words': words,
        'lemmata': lemmata,
        'lineStarts': line_starts,
        'lineEnds': line_ends
    }

    return text_data


def iter_processed(tei_files, jobs):
    """Yield process_tei_file(f) for each f, IN INPUT ORDER (#284).

    Parallelisiert wird ausschliesslich das Parsen. process_tei_file liest genau
    eine Datei und liefert ein reines dict aus JSON-Typen zurueck; lxml-Objekte
    ueberleben eine Prozessgrenze nicht und werden hier auch nicht gebraucht.

    Die Reduktion (texts, lemma_index) bleibt im Elternprozess UND in
    Dateireihenfolge, denn an dieser Reihenfolge haengen die Index-Bytes: die
    Schluessel- und Wertereihenfolge von lemmaIndex ist die Reihenfolge des
    Erstauftretens ueber die sortierte Dateiliste (#125). Deshalb executor.map
    (geordnet) und ausdruecklich NICHT as_completed.

    chunksize=1, weil die Kosten pro Datei ueber Groessenordnungen streuen:
    zwischen wenigen KB und 66 MB (OVG). Statisches Chunking teilt Nachbarn
    derselben sortierten Liste demselben Worker zu und kann damit mehrere
    teure Dateien hintereinander an einem Worker aufhaengen, waehrend die
    anderen leerlaufen. Bei rund einer Viertelsekunde Parse-Zeit pro Datei ist
    der Dispatch-Overhead pro Task dagegen vernachlaessigbar.

    Kein cancel_futures noetig, anders als in extract-variants.py: der von
    map() zurueckgegebene Generator canceled die offenen Futures in seinem
    eigenen finally, sobald er geschlossen wird oder eine Exception
    durchreicht. Der with-Block danach findet nichts mehr zu warten.
    """
    if jobs <= 1:
        yield from map(process_tei_file, tei_files)
        return
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as pool:
        yield from pool.map(process_tei_file, tei_files, chunksize=1)


def build_corpus_index(jobs=1):
    """Build complete corpus index from all TEI files."""
    print("\n🔨 Building corpus index...")
    print(f"TEI directory: {TEI_DIR}")

    # Auswahl und Sortierung liegen in scripts/corpus_files.py (#287), damit
    # extract-variants.py und die audit/-Skripte dieselbe Liste sehen.
    tei_files = corpus_files()
    total_files = len(tei_files)

    print(f"Found {total_files} TEI files")

    if total_files == 0:
        print("❌ ERROR: No TEI files found!")
        sys.exit(1)

    # Process all files
    texts = []
    lemma_index = defaultdict(list)  # lemma_id -> list of text IDs

    start_time = time.time()
    print(f"Parsing with {jobs} worker process(es)")

    for idx, text_data in enumerate(iter_processed(tei_files, jobs), 1):
        if idx % 10 == 0 or idx == total_files:
            elapsed = time.time() - start_time
            rate = idx / elapsed if elapsed > 0 else 0
            remaining = (total_files - idx) / rate if rate > 0 else 0
            print(f"   Processing {idx}/{total_files} ({rate:.1f} files/sec, ~{remaining:.0f}s remaining)...")

        if not text_data:
            continue

        texts.append(text_data)

        # Build lemma index (reverse index: lemma -> texts)
        for lemma_id in text_data['lemmata'].keys():
            lemma_index[lemma_id].append(text_data['id'])

    # Sort texts by ID
    texts.sort(key=lambda t: t['id'])

    # Convert lemma_index to regular dict
    lemma_index = dict(lemma_index)

    # Build final index
    index = {
        'version': '4.2.6',  # 4.1.5: #143 APO/HMT/HH Prosa-Konversion l→lb (lineStarts/lineEnds entfallen für die drei Texte). 4.1.6: #198 habe/hab-Disambiguierung (25 Tokens zu lemma_2593, 179 NOM-Strips). 4.1.7: #189 GWTK-Pilot — 257 nackte rot/jung-Tokens neu annotiert (rôt/rote/junc, Goldstandard-validiert). 4.1.8: #138 814 Strophenziffern aus dem HUG-Verstext entfernt (706 davon pos=DIG, 108 unannotiert; die Strophenzahl steht ab jetzt nur noch in lg/@n). 4.2.0: #236 Frauenlob-Revision — FR3 Parallelueberlieferungs-Ebene rekonstruiert (23 gleichrangige Toene zu 10 zusammengefuehrt, 36 <div type="parallel">, 1.563 Verse jetzt als Parallelueberlieferung erkennbar); 42 roemische Ordnungszahl-Tokens aus FR1/FR2/FR3 entfernt und durch <head> ersetzt. 4.2.1: #228 sieben leere <author>-Elemente im titleStmt gefuellt (ALX/BVSN/PSG/PTS Moench von Heilsbronn, BOP Boppe, MHG Herger, MRB Burggraf von Riedenburg); betrifft nur das Feld text.author, keine Token- oder Positionsdaten. Ausserdem normalisiert der Build Whitespace im Autornamen: LUU trug ihn ueber zwei eingerueckte Zeilen, der Umbruch stand so in Index und API. 4.2.2: #216 Serie 1 (minne): 5.435 zuvor unannotierte Tokens der Form minne in 255 Texten kontextdisambiguiert (5.106 zu lemma_4130 NOM, 329 zu lemma_4133 VRB); 1.547 ambige Faelle blieben absichtlich unannotiert. Betrifft lemmaRef und corresp, also Trefferzahlen und Positionen; variants.xml bleibt unveraendert (alle vier Semantik-Zaehler von extract-variants auf 0). 4.2.3: #369 Serie 2 (stat): 7.760 zuvor unannotierte Tokens der Formen stat (7.597) und stât (163) in 322 Texten kontextdisambiguiert (6.665 zu lemma_5732 NOM, 1.095 zu lemma_5710 VRB); 95 Faelle blieben absichtlich unannotiert, darunter die, in denen weder das feminine Substantiv noch das Verb passt (maskulines stat = Ufer bzw. Stand, Adjektiv staete; Aufschluesselung im Provenienz-Log). variants.xml wieder unveraendert. 4.2.4: #369 Nachlauf — ein einzelner Fehltag korrigiert: SKT_502140_4 trug 'stât' als Substantiv, obwohl 'mîn gedanc an ir vil hôhe stât' das Verb ist. Jetzt lemma_5710 VRB; das falsche @ana ist ersatzlos entfernt, weil eine neue Sense-Zuordnung kuratorisch waere. Anders als der Batch selbst aendert das variants.xml (Typ type_218598 wird unbelegt), deshalb Authority-Index 1.9.0 auf 1.9.1. 4.2.5: #367 — 40 Tokens der Fuegung 'der/die waeren minne' in 17 Texten vom Verb aufs Adjektiv umannotiert (lemma_7505 wesen VRB auf lemma_7338 waer ADJ). Anders als die Serien 1 und 2 ist das keine Erstannotation, sondern eine Umannotation bereits annotierter Tokens; entschieden von KZW am 25.08. Betrifft lemmaRef, pos und corresp, also Trefferzahlen je Lemma, nicht aber die Positionszaehlung (alle 40 trugen schon ein @lemmaRef). Zwei neue Variantentypen fuer die Schreibungen waeren und woren, deshalb Authority-Index 1.9.1 auf 1.9.2. 4.2.6: #235 Punkt 3 - 66 bisher unannotierte Tokens der WZB mit Breve auf o oder u nachannotiert (lemmaRef und pos, NOM 46, VRB 18, ADJ 1, NUM 1). Rein mechanisch: annotiert wurde nur, wo die MHG-normalisierte Schreibung in variants.xml genau ein Lemma trifft und dieses genau eine Wortart hat. 223 weitere Breve-Tokens blieben unannotiert. Betrifft Trefferzahlen je Lemma UND die Positionszaehlung, weil die 66 vorher kein @lemmaRef trugen und deshalb nicht mitgezaehlt wurden. Kein corresp (siehe #370), also keine neuen Variantentypen und kein Bump des Authority-Index.
        'totalTexts': len(texts),
        'totalLemmata': len(lemma_index),
        'texts': texts,
        'lemmaIndex': lemma_index
    }

    # Statistics
    total_words = sum(t['wordCount'] for t in texts)
    avg_words = total_words // len(texts) if texts else 0

    print(f"\n📊 Statistics:")
    print(f"   Total texts: {len(texts):,}")
    print(f"   Total unique lemmata: {len(lemma_index):,}")
    print(f"   Total words: {total_words:,}")
    print(f"   Average words per text: {avg_words:,}")

    return index


def save_index(index):
    """Save index to compressed JSON file."""
    print(f"\n💾 Saving to {OUTPUT_FILE}...")

    # Create data directory if needed
    DATA_DIR.mkdir(exist_ok=True)

    # Serialize to JSON (einmal encodieren — der String ist ~200 MB)
    json_bytes = json.dumps(index, ensure_ascii=False, separators=(',', ':')).encode('utf-8')

    # Get uncompressed size
    uncompressed_size = len(json_bytes)

    # mtime=0: kein Zeitstempel im gzip-Header — Builds aus identischem
    # Quellstand sind byte-identisch (#125, Muster wie naming-index-Builder)
    with gzip.GzipFile(OUTPUT_FILE, mode='wb', mtime=0) as f:
        f.write(json_bytes)

    # Get compressed size
    compressed_size = OUTPUT_FILE.stat().st_size

    compression_ratio = (1 - compressed_size / uncompressed_size) * 100

    print(f"   Uncompressed: {uncompressed_size / (1024 * 1024):.2f} MB")
    print(f"   Compressed: {compressed_size / (1024 * 1024):.2f} MB")
    print(f"   Compression: {compression_ratio:.1f}%")
    print(f"\n✅ Corpus index saved successfully!")


def check_working_tree(directory, allow_dirty):
    """Pre-flight check: warn (or fail) when directory has uncommitted or
    untracked TEI files. Prevents accidentally bundling work-in-progress
    files into the published index. See #100."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain', '--', str(directory)],
            capture_output=True, text=True, check=True, cwd=PROJECT_ROOT
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"⚠️  git status check skipped: {e}")
        return

    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    untracked = [ln for ln in lines if ln.startswith('??')]
    modified = [ln for ln in lines if not ln.startswith('??')]

    if not lines:
        return

    print(f"⚠️  Working tree under {directory}/ is not clean:")
    print(f"   {len(untracked)} untracked, {len(modified)} modified/staged")
    for ln in lines[:10]:
        print(f"     {ln}")
    if len(lines) > 10:
        print(f"     ... +{len(lines) - 10} more")

    if allow_dirty:
        print("   --allow-dirty set, continuing anyway.")
    else:
        sys.exit(
            "Refusing to build a possibly-inconsistent index.\n"
            "Commit/stash the changes above, or pass --allow-dirty for local tests."
        )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build MHDBDB corpus index from tei/")
    parser.add_argument(
        '--allow-dirty', action='store_true',
        help="Build even if tei/ has untracked or modified files (use for local tests)."
    )
    parser.add_argument(
        '--jobs', type=int, default=default_jobs(),
        help="Worker-Prozesse fuer das Parsen (1 = sequentiell). Das Ergebnis ist "
             "von diesem Wert unabhaengig und byte-identisch (#284)."
    )
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error('--jobs muss mindestens 1 sein')

    print("=" * 60)
    print("MHDBDB Corpus Index Builder")
    print("=" * 60)

    check_working_tree(TEI_DIR.relative_to(PROJECT_ROOT), args.allow_dirty)

    try:
        # Build index
        index = build_corpus_index(jobs=args.jobs)

        # Save index
        save_index(index)

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
