# Scripts

Build, validation, and data transformation scripts for MHDBDB TEI corpus.

## Verzeichnisstruktur

```
scripts/
├── build-api.py                 # Statische JSON-API unter api/ generieren (#45)
├── build-authority-index.py     # Authority-Index generieren
├── build-corpus-index.py        # Korpus-Index generieren
├── build-pages.py               # Nav/Footer/Matomo aus includes/ in alle Seiten injizieren (--check Drift-Gate)
├── build-vendor.js              # Vendored JS-Dependencies bündeln
├── validate-indices.py          # Generierte Indexes validieren
├── mhg_normalizer.py            # MHG-Textnormalisierung (shared lib)
├── tei_namespaces.py            # TEI-Namespace-Erkennung für lxml-Bäume (shared lib)
├── corpus_files.py              # welche Dateien der Korpus sind, in welcher Reihenfolge, plus Worker-Cap (shared lib, #287)
├── insert-pb-from-linecode.py   # <pb> aus Legacy-Linecode einfügen (#26)
├── insert-stanzas-from-linecode.py # Stanza-Anchors aus Legacy-Linecode (#23)
├── insert-div-wrappers-138.py   # Editorische <div>-Hüllen für HUG und MBS (#138)
├── insert-lg-stanzas-138.py     # <lg type="stanza"> in HUG-Lieder einfügen (#138)
├── remove-stanza-numerals-138.py # Strophenziffern aus dem Verstext entfernen (#138)
│
├── ingest/                      # Korpus-Ingest je Vorhaben
│   ├── ari/                     # ARITHMETIC, 6 Rechenbuch-Handschriften (#92)
│   ├── frauenlob/               # Frauenlob-Revision (#236)
│   ├── legacy-sources/          # Linecode-Quellen ins Repo spiegeln (#248)
│   ├── naming/                  # Figurenbezeichnungen, naming-index bauen (#59)
│   ├── pos-disambig/            # PoS-/Lemma-Disambiguierung in Batches (#189/#198)
│   └── wzb/                     # Wenzelsbibel (#224 und Vorläufer)
│
├── audit/                       # Korpus- & Authority-Analyse, CI-Gates
│   ├── audit-tei-corpus.py      # Element/Attribut-Inventar des Korpus
│   ├── audit-authority-files.py # Struktur-Audit der Authority Files (authority→authority)
│   ├── check-authority-cross-refs.py # Korpus→Authority Cross-Ref-Integrität (#44/#115)
│   ├── check-author-refs.py     # titleStmt/author gegen persons.xml (#228)
│   ├── check-doc-inventories.py  # Specs und Audit-Skripte stehen in DEVELOPMENT.md (#329)
│   ├── check-index-version-bump.py # Inhalt geändert => Version gebumpt (#154)
│   ├── check-index-versions.py  # Index-Versions-Konstanten konsistent
│   ├── check-lexicon-senses.py  # jeder <entry> in lexicon.xml hat mindestens einen <sense>
│   ├── check-naming-index.py    # naming-index: Provenienz + Sigle-Existenz (#152)
│   ├── check-no-cdn.py          # keine externen <script src> in committeten Seiten
│   ├── check-no-em-dash.py      # keine Em-Dashes in user-sichtbarem Text
│   ├── check-release-version.py # Release-Version gegen CITATION.cff und .zenodo.json
│   ├── classify-lexicon-backfill.py # Backfill-Lücken in lexicon.xml klassifizieren (#115)
│   ├── count-editorial-notes-and-div-heads.py # Zahlen hinter den Reader-Änderungen (#250)
│   ├── count-verse-numbering-resets.py # Reichweite der Verszählung messen (#138)
│   ├── coverage-bias-check.py   # Coverage-Bias der pro-1000-Raten (#309)
│   ├── doc-count-audit.py       # Zählungen aus den Daten gegen die Doku prüfen
│   ├── drop-negative-variant-corresp.py # tote @corresp aus <w> entfernen (#115)
│   ├── measure-stage3-resolution.py # Wirkung von Stufe 3 der Lemma-Auflösung (#224)
│   ├── quantify-unannotated-tokens.py # unannotierte Wortformen korpusweit zählen (#189)
│   ├── survey-concept-distribution.py # Concepts für die Begriffs-Verteilung (#47)
│   ├── validate-corpus.py       # Zwei-Stufen-Schema-Validierung
│   ├── lexicon-baseline.json    # committete Referenzmenge des #152-Gates, per !-Regel vom *.json-Ignore ausgenommen
│   └── TEXT_DATA_TABLE.xlsx     # Legacy-Linecode-Mapping
│
├── sync/                        # Externe Daten / Korpus → TEI/Authority
│   ├── backfill-lexicon.py      # Kategorie-A-Stubs in lexicon.xml nachtragen (#115)
│   ├── enhance_works_with_zotero.py  # Zotero API → works.xml
│   ├── extract-variants.py      # Korpus → variants.xml regenerieren (#44/#115)
│   └── sync_tei_headers.py      # Authority Files → TEI-Header
│
└── _archived/                   # Referenz, nicht ausführen
    ├── tei-transformation.py    # Original RDF/MySQL→TEI-Migration
    ├── add-xml-model-pi.py      # xml-model-PI nachrüsten (#32 Stage 1)
    ├── flatten-nested-hi.py     # verschachtelte <hi> auflösen (#32-Followup)
    ├── migrate-header-credits.py # Editor-Attribution in die Header (#83)
    ├── split-prose-mega-p.py    # Mega-<p> an <pb/> teilen (#32-Followup)
    ├── convert-l-to-lb-143.py   # <l> → <lb/> in drei Prosatexten (#143, geschlossen)
    └── wzb/                     # WZB-Sackgassen, siehe wzb/README.md
```

Ein issue-gebundenes Einmal-Skript wandert nach `_archived/`, sobald sein Issue geschlossen ist. Die Grenze ist der Issue-Status, nicht die Frage, ob das Skript schon gelaufen ist: solange das Issue offen ist, kann eine Prüffrage einen erneuten Lauf erzwingen. Deshalb stehen die drei `*-138.py` oben, bis #138 geschlossen ist, und `convert-l-to-lb-143.py` liegt im Archiv. Die beiden `insert-*-from-linecode.py` sind keine Einmal-Skripte, sie werden für weitere Texte gebraucht.

Skripte im Archiv sind Referenz und nicht lauffähig: sie berechnen die Repo-Wurzel als `Path(__file__).resolve().parent.parent`, was eine Ebene tiefer auf `scripts/` zeigt. Wer eines wieder braucht, verschiebt es zurück, statt es aus `_archived/` heraus aufzurufen.

## Build-Pipeline (Root)

Die Build-Scripts werden über `npm run` aufgerufen und dürfen nicht verschoben werden.

### `build-authority-index.py`
Verarbeitet die 7 inhaltstragenden Authority Files und generiert `data/authority-index.json.gz` (~3 MB). Enthält Lemmata, Personen, Werke, Konzepte, Gattungen, Namen und Varianten. `contributors.xml` (8. Authority-File seit 2026-04-14) wird bewusst **nicht** indiziert — es ist Projekt-interne Editor-Attribution, kein Suchinhalt.

### `build-corpus-index.py`
Parst alle TEI-Dateien in `tei/` und generiert `data/corpus-index.json.gz` (~40 MB, v4.1.x). Extrahiert Lemma-Positionen, Wortzählung und Metadaten.

### `build-pages.py`
Injiziert die geteilte Navigation + Footer + Matomo-Snippet aus `includes/_nav.html` / `includes/_footer.html` / `includes/_matomo.html` in die Marker-Regionen (`NAV:START`/`FOOTER:START`/`MATOMO:START`) der Seiten. Idempotent; `{{ROOT}}`-Token wird pro Seitentiefe ersetzt; aktive Nav-Seite bekommt `aria-current="page"`. Zwei Seitenlisten: `PAGES` bekommt die volle Chrome (Nav+Footer+Matomo); `MATOMO_PAGES` (Standalone-Seiten mit eigenem Layout wie `api/index.html`, `404.html`) bekommt nur das Matomo-Snippet vor `</head>`, ohne Header/Footer anzufassen. `--check` ist ein Drift-Gate (exit 1 bei Out-of-Sync, keine Writes). Nach Änderung an `includes/` ausführen — nicht die Seiten direkt editieren.

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
Korpus→Authority Cross-Reference-Integrität (#44/#115): scannt alle `tei/*.tei.xml` nach `@lemmaRef`/`@ana`/`@corresp`/`@ref`/`@target`, die auf nicht-existente Authority-`xml:id`s zeigen. `--check` macht daraus ein CI-Gate (scheitert bei unresolved refs außerhalb `lexicon.xml`; `lexicon.xml` wird als ID-Set-Ratsche gegen die committete `lexicon-baseline.json` gegated — neue dangling IDs = rot, tolerierter Backfill-Altbestand = grün, #152). `--update-baseline` zieht die Ratsche nach gelandetem Backfill nach. Läuft in `data-integrity.yml`.

### `check-author-refs.py`
Autorangaben im `titleStmt` gegen `persons.xml` (#228): meldet leere `<author ref="..."/>` (Text erscheint autorlos), tote `@ref`, Abweichungen von der Referenzform `#person_N`, Textinhalte mit Zeilenumbruch (die so in Index und API landen) und Textinhalte, die vom `preferred`-Namen abweichen. `--check` setzt den Exit-Code nur bei den ersten beiden, die Namensabweichung ist oft eine legitime bibliographische Variante. **Läuft bewusst nicht in der CI**, solange der tote `@ref` in VOR offen ist (#308); sonst wäre der Befund ein Blocker für unbeteiligte PRs.

### `check-index-version-bump.py`
Versions-Bump-Gate (#154): hat sich der dekomprimierte Inhalt von corpus-/authority-index gegenüber `--base <rev>` geändert, muss der `version`-String mitgeändert sein — sonst invalidiert der Dexie-Cache nicht. Läuft in `data-integrity.yml` (Diff-Base = PR-Base-Tip bzw. `event.before`).

### `check-naming-index.py`
Naming-Index-Konsistenz (#152): `source.commit`-Provenienz vorhanden + alle `works[].sigle` existieren als `tei/<SIG>.tei.xml`. `--print-source-commit` liefert den Quell-Pin für die Workflows. Läuft in `data-integrity.yml` und `naming-index-update.yml`.

### `check-index-versions.py`
Prüft, dass die Index-Versions-Konstanten in Build-Skripten und `corpus-loader.js` synchron sind. Läuft in `data-integrity.yml`.

### `validate-corpus.py`
Zwei-Stufen-Validierung: TEI P5 (`tei_all.rng`) + MHDBDB-Constraints (`mhdbdb.rng`). Validiert alle Korpus-Dateien und meldet Fehler.

### `TEXT_DATA_TABLE.xlsx`
Linecode-Mapping aus dem Legacy-MHDBDB-System. Enthält die originalen Linecode-Definitionen pro Text in Spalte `LINECODE` (die kanonischen Templates liegen in `docs/data/linecode-templates.csv`, ebenfalls Spalte `LINECODE` — die frühere „Spalte E"-Annahme war falsch, siehe LINECODE.md). Referenz für strukturelle Rekonstruktion (Issues #23, #30, #31).

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
