# Scripts

Build, validation, and data transformation scripts for MHDBDB TEI corpus.

## Index Generation

### `build-authority-index.py`
Processes all 7 authority files (`authority-files/*.xml`) and generates a compressed JSON index (`data/authority-index.json.gz`, ~1.3 MB). Includes lemmata with grammatical annotations, persons, works with bibliographic data, concepts, genres, names, and orthographic variants. Uses `mhg_normalizer.py` for text normalization to ensure search consistency.

### `build-corpus-index.py`
Parses all 666 TEI files in `tei/` directory and generates a compressed document-level corpus index (`data/corpus-index.json.gz`, ~21 MB). Extracts lemma positions, word counts, and metadata for fast lookup. Enables <100ms search latency.

### `generate-manifest.py`
Extracts metadata (title, author, sigle, word count) from all TEI file headers and generates `tei/manifest.json` (~182 KB). Used for quick corpus overview without parsing full TEI files.

## Utilities

### `mhg_normalizer.py`
Middle High German text normalizer. Normalizes long vowels (â→a, ê→e), umlauts (ä→a, ö→o, ü→u), special characters (ʒ→z, ſ→s), and applies lowercase conversion. **CRITICAL:** Must produce identical results as JavaScript version (`playground/js/utils/text-normalizer.js`) to ensure search parity between build-time indices and runtime search.

### `validate-indices.py`
Validates structure, content, and integrity of generated index files. Checks JSON structure, required fields, data types, version numbers, and statistical reasonableness. Exit code 0 = success, 1 = validation failed.

## Data Wrangling

Scripts for transforming and updating TEI source data. See [`data-wrangling/README.md`](data-wrangling/README.md) for full documentation.

### Subdirectories

| Verzeichnis | Inhalt |
|-------------|--------|
| `data-wrangling/` | Zotero-Sync, TEI-Header-Sync, PoS-Disambiguation |
| `data-wrangling/tei-model/` | TEI-Schema-Audit und -Validierung (#32) |

## Usage

```bash
# After updating TEI or authority files, rebuild all indices
python scripts/build-authority-index.py
python scripts/build-corpus-index.py
python scripts/generate-manifest.py

# Validate generated indices
python scripts/validate-indices.py

# Validate TEI corpus against RELAX NG schema
python scripts/data-wrangling/tei-model/validate-corpus.py

# Update editor metadata from Zotero API (Issue #19) - 2-step workflow
python scripts/data-wrangling/enhance_works_with_zotero.py --dry-run  # Step 1: Preview works.xml changes
python scripts/data-wrangling/enhance_works_with_zotero.py --cache    # Step 1: Update works.xml + save cache
python scripts/data-wrangling/sync_tei_headers.py --works --dry-run   # Step 2: Preview TEI header changes
python scripts/data-wrangling/sync_tei_headers.py --works             # Step 2: Sync TEI headers
python scripts/build-authority-index.py                               # Rebuild index

# Offline mode (use cached Zotero data)
python scripts/data-wrangling/enhance_works_with_zotero.py --offline --dry-run

# Sync all authority files to TEI headers (future use)
python scripts/data-wrangling/sync_tei_headers.py --all --dry-run     # Preview all changes
python scripts/data-wrangling/sync_tei_headers.py --all               # Sync all authority data
```

## Best Practices

### Archived Scripts
Scripts prefixed with `_ARCHIVED_` are preserved for reference only and should not be executed. They contain useful functions that can be extracted for new focused scripts. Example: `_ARCHIVED_tei-transformation.py`

### Data Wrangling Workflow
1. Run script with `--dry-run` to preview changes
2. Review proposed changes
3. Run script without `--dry-run` to apply
4. Review git diff of modified files
5. Rebuild indices
6. Commit changes

### Note
Data wrangling scripts modify source TEI files. Always review changes before committing.
