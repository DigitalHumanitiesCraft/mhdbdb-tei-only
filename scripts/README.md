# Scripts

Build, validation, and data transformation scripts for MHDBDB TEI corpus.

## Verzeichnisstruktur

```
scripts/
├── build-authority-index.py     # Authority-Index generieren
├── build-corpus-index.py        # Korpus-Index generieren
├── validate-indices.py          # Generierte Indexes validieren
├── mhg_normalizer.py            # MHG-Textnormalisierung (shared lib)
│
├── audit/                       # Korpus- & Authority-Analyse
│   ├── audit-tei-corpus.py      # Element/Attribut-Inventar des Korpus
│   ├── audit-authority-files.py # Struktur-Audit der Authority Files (authority→authority)
│   ├── check-authority-cross-refs.py # Korpus→Authority Cross-Ref-Integrität (#44/#115)
│   ├── check-index-versions.py  # Index-Versions-Konstanten konsistent
│   ├── validate-corpus.py       # Zwei-Stufen-Schema-Validierung
│   └── TEXT_DATA_TABLE.xlsx     # Legacy-Linecode-Mapping
│
├── sync/                        # Externe Daten / Korpus → TEI/Authority
│   ├── enhance_works_with_zotero.py  # Zotero API → works.xml
│   ├── extract-variants.py      # Korpus → variants.xml regenerieren (#44/#115)
│   └── sync_tei_headers.py      # Authority Files → TEI-Header
│
└── _archived/                   # Referenz, nicht ausführen
    └── tei-transformation.py    # Original RDF/MySQL→TEI-Migration
```

## Build-Pipeline (Root)

Die Build-Scripts werden über `npm run` aufgerufen und dürfen nicht verschoben werden.

### `build-authority-index.py`
Verarbeitet die 7 inhaltstragenden Authority Files und generiert `data/authority-index.json.gz` (~3 MB). Enthält Lemmata, Personen, Werke, Konzepte, Gattungen, Namen und Varianten. `contributors.xml` (8. Authority-File seit 2026-04-14) wird bewusst **nicht** indiziert — es ist Projekt-interne Editor-Attribution, kein Suchinhalt.

### `build-corpus-index.py`
Parst alle TEI-Dateien in `tei/` und generiert `data/corpus-index.json.gz` (~34 MB). Extrahiert Lemma-Positionen, Wortzählung und Metadaten.

### `validate-indices.py`
Validiert Struktur und Integrität der generierten Index-Dateien.

### `mhg_normalizer.py`
Mittelhochdeutsche Textnormalisierung (â→a, ê→e, ä→a, ö→o, ü→u, ʒ→z, ſ→s). **Muss identische Ergebnisse liefern wie die JS-Version** (`assets/js/lib/text-normalizer.js`).

## audit/ — Korpus- & Authority-Analyse

Scripts für die Analyse und Validierung der TEI-Quelldaten. Entstanden im Rahmen von Issue #32 (TEI Model Consolidation).

### `audit-tei-corpus.py`
Element- und Attribut-Inventar des gesamten Korpus. Analysiert alle TEI-Dateien (exkl. `.disamb.tei.xml`) und erzeugt eine vollständige Aufstellung aller Elemente, Attribute und Werte.

### `audit-authority-files.py`
Struktur-, Querverweis- und Datenqualitäts-Audit für alle 8 Authority Files. Prüft ID-Muster, verwaiste Referenzen und strukturelle Konsistenz **innerhalb** der Authority Files (authority→authority).

### `check-authority-cross-refs.py`
Korpus→Authority Cross-Reference-Integrität (#44/#115): scannt alle `tei/*.tei.xml` nach `@lemmaRef`/`@ana`/`@corresp`/`@ref`/`@target`, die auf nicht-existente Authority-`xml:id`s zeigen. `--check` macht daraus ein CI-Gate (scheitert bei unresolved refs außerhalb `lexicon.xml`; `lexicon.xml` hat eine bekannte Ingest-Backfill-Baseline). Läuft in `schema-validation.yml`.

### `check-index-versions.py`
Prüft, dass die Index-Versions-Konstanten in Build-Skripten und `corpus-loader.js` synchron sind. Läuft in `index-version-check.yml`.

### `validate-corpus.py`
Zwei-Stufen-Validierung: TEI P5 (`tei_all.rng`) + MHDBDB-Constraints (`mhdbdb.rng`). Validiert alle Korpus-Dateien und meldet Fehler.

### `TEXT_DATA_TABLE.xlsx`
Linecode-Mapping aus dem Legacy-MHDBDB-System. Enthält die originalen Linecode-Definitionen pro Text (Spalte E). Referenz für strukturelle Rekonstruktion (Issues #23, #30, #31).

## sync/ — Externe Daten → TEI/Authority

Scripts für die Integration externer Datenquellen.

### `enhance_works_with_zotero.py`
Holt bibliographische Metadaten (v.a. Editor:innen) von der Zotero API und aktualisiert `authority-files/works.xml`. Unterstützt `--dry-run`, `--cache`, `--offline`.

### `extract-variants.py`
Regeneriert `authority-files/variants.xml` aus dem aktuellen Korpus (#44/#115). `variants.xml` ist **korpus-abgeleitet**: pro `<w @lemmaRef @corresp>` wird (Lemma, type-id, Form) gesammelt; xml:id-Eindeutigkeit via Mehrheitsentscheid. Ersetzt den veralteten, nur auf `initial-data-wrangling` liegenden Generator (las das Pre-#32-`@wordRef`). Dry-Run-Default, `--apply` überschreibt. **Nach `--apply`: Authority-Index neu bauen + Version bumpen.**

### `sync_tei_headers.py`
Synchronisiert Authority-File-Daten in die TEI-Header (667 Dateien). Erweiterbar (aktuell: `--works` für Editor-Sync). Unterstützt `--dry-run`.

## _archived/ — Referenz

### `tei-transformation.py`
Originales Transformationsscript aus dem `initial-data-wrangling`-Branch (~2000 Zeilen). Enthält nützliche Utility-Funktionen (CSV-Parsing, TEI-Erstellung, ID-Normalisierung). **Nicht ausführen** — bei Bedarf einzelne Funktionen extrahieren.

## Verwendung

```bash
# Indexes neu bauen (nach Änderungen an TEI/Authority Files)
python scripts/build-authority-index.py
python scripts/build-corpus-index.py

# Indexes validieren
python scripts/validate-indices.py

# Korpus gegen Schema validieren
python scripts/audit/validate-corpus.py

# Zotero-Sync (immer erst --dry-run)
python scripts/sync/enhance_works_with_zotero.py --dry-run
python scripts/sync/enhance_works_with_zotero.py --cache
python scripts/sync/sync_tei_headers.py --works --dry-run
python scripts/sync/sync_tei_headers.py --works
```

## Best Practices

- **Immer `--dry-run` zuerst** bei sync-Scripts
- **`git diff` prüfen** nach jeder Transformation
- **Indexes neu bauen** nach Änderungen an TEI oder Authority Files
- **Archived Scripts nicht ausführen** — einzelne Funktionen bei Bedarf extrahieren
