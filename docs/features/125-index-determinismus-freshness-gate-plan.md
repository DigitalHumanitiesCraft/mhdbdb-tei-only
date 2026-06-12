# #125 Index-Determinismus + Freshness-Gate — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deterministische Index-Builds (identischer Quellstand → identische Bytes) + CI-Gate, das vergessene Rebuilds der abgeleiteten Schicht blockt.

**Architecture:** Teil 1 entfernt alle Nichtdeterminismus-Quellen aus den Build-Skripten (`generatedAt`, unsortiertes glob, gzip-Header-mtime) und macht das variants.xml-Datum änderungsgetrieben. Teil 2 konsolidiert `schema-validation.yml` + `index-version-check.yml` zu einem Workflow `data-integrity.yml` mit Rebuild-and-Compare-Steps. Spec: `docs/features/125-index-determinismus-freshness-gate.md`.

**Tech Stack:** Python 3.13 (lxml, gzip, json), GitHub Actions, Vanilla JS (nur Versions-Konstanten).

**Projektregeln (überschreiben Skill-Defaults):**
- KEIN Commit/Push ohne Christians Freigabe → alle Commit-Steps sind am Ende gebündelt und explizit gegated (Task 10).
- Nur gezielt benannte Dateien stagen, nie `git add -A` (parallele Sessions).
- `npm test` nie ungefragt starten.
- Kein Python-Test-Framework im Projekt → Verifikation über explizite Kommandos (Doppel-Build-Byte-Vergleich) statt Unit-Tests.

---

### Task 0: Feature-Branch

**Files:** keine

- [ ] **Step 0.1: Sauberen Stand prüfen und Branch anlegen**

```bash
git status --porcelain
# Erwartung: nur die zwei neuen docs/features/125-*.md (untracked).
# Falls fremde Änderungen gestaged sind (parallele Session!): NICHT anfassen, weiterarbeiten ohne sie zu stagen.
git checkout -b feature/125-index-determinism
```

---

### Task 1: `scripts/build-corpus-index.py` deterministisch

**Files:**
- Modify: `scripts/build-corpus-index.py` (Docstring ~Z. 11-12, Import Z. 57, glob Z. 266, Index-Dict Z. 305-312, save_index Z. 340-342)

- [ ] **Step 1.1: Docstring-Beispiel anpassen**

Im Modul-Docstring (oben, ~Z. 11-12) die Beispiel-Struktur ändern:

```
ALT:  "version": "4.1.3",
      "generatedAt": "2025-01-01T00:00:00Z",
NEU:  "version": "4.1.4",
```

(Die `generatedAt`-Zeile ersatzlos streichen.)

- [ ] **Step 1.2: glob sortieren (Z. 266)**

```python
# ALT:
    tei_files = list(TEI_DIR.glob('*.tei.xml'))
# NEU (glob-Reihenfolge ist OS-abhängig — sortiert für deterministische Index-Bytes, #125):
    tei_files = sorted(TEI_DIR.glob('*.tei.xml'))
```

- [ ] **Step 1.3: Index-Dict — Version bumpen, generatedAt entfernen (Z. 305-312)**

```python
# NEU:
    index = {
        'version': '4.1.4',  # 4.0.0: document-level indexing. 4.0.1: WZB. 4.1.0: lineStarts/lineEnds für #47.3. 4.1.1: #23 Stanza-Wraps. 4.1.2: #104 Sigle-Titel-Differenzierung. 4.1.3: #110 WVV 478 Stanza-Wraps. 4.1.4: #125 deterministischer Build (generatedAt entfernt, sorted glob, gzip mtime=0).
        'totalTexts': len(texts),
        'totalLemmata': len(lemma_index),
        'texts': texts,
        'lemmaIndex': lemma_index
    }
```

(Die Zeile `'generatedAt': datetime.now().isoformat() + 'Z',` fällt weg.)

- [ ] **Step 1.4: gzip ohne Header-Timestamp (Z. 340-342)**

```python
# ALT:
    # Compress with gzip
    with gzip.open(OUTPUT_FILE, 'wt', encoding='utf-8') as f:
        f.write(json_data)
# NEU:
    # mtime=0: kein Zeitstempel im gzip-Header — Builds aus identischem
    # Quellstand sind byte-identisch (#125, Muster wie naming-index-Builder)
    with gzip.GzipFile(OUTPUT_FILE, mode='wb', mtime=0) as f:
        f.write(json_data.encode('utf-8'))
```

- [ ] **Step 1.5: Toten Import entfernen**

```bash
grep -n "datetime" scripts/build-corpus-index.py
```

Erwartung: nur noch Z. 57 (`from datetime import datetime`). Wenn ja → Import-Zeile löschen. Wenn weitere Treffer: Import behalten, Treffer im Abschlussbericht nennen.

- [ ] **Step 1.6: Syntax-Check**

```bash
python -m py_compile scripts/build-corpus-index.py && echo OK
```

Erwartung: `OK`

---

### Task 2: `scripts/build-authority-index.py` deterministisch

**Files:**
- Modify: `scripts/build-authority-index.py` (Import Z. 28, Index-Dict Z. 789-800, save_index Z. 830-832)

- [ ] **Step 2.1: Index-Dict — Version bumpen, generatedAt entfernen (Z. 789-791)**

In der `'version'`-Zeile `'1.4.0'` → `'1.4.1'` und an den bestehenden Kommentar anhängen:

```
 1.4.1: #125 deterministischer Build (generatedAt entfernt, gzip mtime=0).
```

Die Zeile `'generatedAt': datetime.utcnow().isoformat() + 'Z',` (Z. 791) ersatzlos löschen. Der Rest des Dicts (`lemmata` … `maps`) bleibt unverändert.

- [ ] **Step 2.2: gzip ohne Header-Timestamp (Z. 830-832)**

Identische Änderung wie Task 1 Step 1.4 (gleicher ALT-Block, gleicher NEU-Block — der `save_index`-Code ist in beiden Skripten dupliziert; Duplikat hier bewusst beibehalten, kein Refactoring-Scope).

- [ ] **Step 2.3: Toten Import entfernen**

```bash
grep -n "datetime" scripts/build-authority-index.py
```

Erwartung: nur Z. 28. Wenn ja → löschen, sonst behalten + berichten.

- [ ] **Step 2.4: Syntax-Check**

```bash
python -m py_compile scripts/build-authority-index.py && echo OK
```

---

### Task 3: `scripts/validate-indices.py` Pflichtfelder

**Files:**
- Modify: `scripts/validate-indices.py:73` und `:139`

- [ ] **Step 3.1: generatedAt aus beiden required_fields streichen**

```python
# Z. 73 ALT:
    required_fields = ['version', 'generatedAt', 'lemmata', 'persons', 'works', 'variants']
# Z. 73 NEU:
    required_fields = ['version', 'lemmata', 'persons', 'works', 'variants']

# Z. 139 ALT:
    required_fields = ['version', 'generatedAt', 'totalTexts', 'totalLemmata', 'texts', 'lemmaIndex']
# Z. 139 NEU:
    required_fields = ['version', 'totalTexts', 'totalLemmata', 'texts', 'lemmaIndex']
```

- [ ] **Step 3.2: Syntax-Check**

```bash
python -m py_compile scripts/validate-indices.py && echo OK
```

---

### Task 4: `assets/js/lib/corpus-loader.js` Versions-Konstanten

**Files:**
- Modify: `assets/js/lib/corpus-loader.js:8-9`

- [ ] **Step 4.1: Konstanten bumpen**

Z. 8: `'4.1.3'` → `'4.1.4'`, an den Zeilen-Kommentar anhängen: ` 4.1.4: #125 deterministischer Build (generatedAt entfernt).`
Z. 9: `'1.4.0'` → `'1.4.1'`, an den Zeilen-Kommentar anhängen: ` 1.4.1: #125 deterministischer Build (generatedAt entfernt).`

- [ ] **Step 4.2: Drei-Stellen-Konsistenz prüfen**

```bash
python scripts/audit/check-index-versions.py
```

Erwartung: Exit 0 (Tasks 1+2 müssen vorher erledigt sein, sonst meldet er Drift — dann zuerst dort fixen).

---

### Task 5: `scripts/sync/extract-variants.py` Datum nur bei Änderung

**Files:**
- Modify: `scripts/sync/extract-variants.py` (Imports Z. 30-36, `build_tree` Z. 129/140, `main` Z. 197-199)

- [ ] **Step 5.1: io-Import ergänzen (Z. 30-31)**

```python
import io
import re
import sys
```

- [ ] **Step 5.2: build_tree parametrisieren**

```python
# Z. 129 ALT:
def build_tree(lemma_to_types, type_to_form, n_files):
# NEU:
def build_tree(lemma_to_types, type_to_form, n_files, date_text):

# Z. 140 ALT:
    etree.SubElement(pubStmt, f'{TEI}date').text = date.today().isoformat()
# NEU (Semantik: <date> = Stand der Daten, nicht letzter Script-Lauf — siehe main()):
    etree.SubElement(pubStmt, f'{TEI}date').text = date_text
```

- [ ] **Step 5.3: Hilfsfunktion `existing_date` (direkt vor `current_map`, ~Z. 163)**

```python
def existing_date():
    """<date> der bestehenden variants.xml, oder None (Datei fehlt/kein date)."""
    if not VARIANTS.exists():
        return None
    tree = etree.parse(str(VARIANTS))
    el = tree.find(f'{TEI}teiHeader/{TEI}fileDesc/{TEI}publicationStmt/{TEI}date')
    return el.text if el is not None and el.text else None
```

- [ ] **Step 5.4: main() — Datum-bei-Änderung-Logik (ersetzt Z. 197-199)**

```python
# ALT:
    tree = build_tree(lemma_to_types, type_to_form, len(base_files))
    out = VARIANTS if apply else DRY_OUT
    tree.write(str(out), xml_declaration=True, encoding='UTF-8', pretty_print=True)
# NEU:
    # Datum nur bei inhaltlicher Aenderung (#125): erst mit dem bestehenden
    # <date> serialisieren; ist das Ergebnis byte-identisch zur committeten
    # Datei, bleibt das Datum stehen (No-op-Lauf erzeugt keinen Diff).
    # Sonst heutiges Datum. <date> bedeutet damit "Stand der Daten".
    old_date = existing_date()
    today = date.today().isoformat()
    tree = build_tree(lemma_to_types, type_to_form, len(base_files), old_date or today)
    buf = io.BytesIO()
    tree.write(buf, xml_declaration=True, encoding='UTF-8', pretty_print=True)
    if old_date is not None and buf.getvalue() != VARIANTS.read_bytes():
        d = tree.find(f'{TEI}teiHeader/{TEI}fileDesc/{TEI}publicationStmt/{TEI}date')
        d.text = today
    out = VARIANTS if apply else DRY_OUT
    tree.write(str(out), xml_declaration=True, encoding='UTF-8', pretty_print=True)
```

- [ ] **Step 5.5: Syntax-Check**

```bash
python -m py_compile scripts/sync/extract-variants.py && echo OK
```

---

### Task 6: Rebuild + Determinismus-Verifikation

**Files:**
- Modify (generiert): `data/corpus-index.json.gz`, `data/authority-index.json.gz`, ggf. `authority-files/variants.xml`

Scratch-Dateien nach `$HOME/.cache/claude-scratch/` (nie in `~/.claude/`).

- [ ] **Step 6.1: variants.xml No-op-Lauf**

```bash
mkdir -p "$HOME/.cache/claude-scratch"
python scripts/sync/extract-variants.py --apply
git status --porcelain -- authority-files/variants.xml
```

Erwartung: leere Ausgabe (byte-identisch, Datum erhalten). Falls Diff: `git diff -- authority-files/variants.xml` inspizieren — echte Korpus-Drift seit 2026-05-29 ist legitim (dann Datei im Commit mitnehmen und im Bericht erwähnen); ein Diff NUR in der `<date>`-Zeile wäre ein Bug in Task 5 → stoppen und fixen.

- [ ] **Step 6.2: Corpus-Index Doppel-Build (Dauer messen!)**

```bash
time python scripts/build-corpus-index.py
cp data/corpus-index.json.gz "$HOME/.cache/claude-scratch/ci-run1.gz"
python scripts/build-corpus-index.py
python -c "
import pathlib, os
a = pathlib.Path('data/corpus-index.json.gz').read_bytes()
b = pathlib.Path(os.path.expanduser('~/.cache/claude-scratch/ci-run1.gz')).read_bytes()
print('DETERMINISTISCH' if a == b else 'FAIL: Builds differieren')
"
```

Erwartung: `DETERMINISTISCH`. Bei FAIL: weitere Nichtdeterminismus-Quelle suchen (Verdächtige: set-Iteration, dict aus ungeordneter Quelle) — nicht weitermachen, bis grün. Die gemessene Dauer notieren (fließt in die Timeout-Plausibilität, Task 7).

- [ ] **Step 6.3: Authority-Index Doppel-Build**

```bash
time python scripts/build-authority-index.py
cp data/authority-index.json.gz "$HOME/.cache/claude-scratch/ai-run1.gz"
python scripts/build-authority-index.py
python -c "
import pathlib, os
a = pathlib.Path('data/authority-index.json.gz').read_bytes()
b = pathlib.Path(os.path.expanduser('~/.cache/claude-scratch/ai-run1.gz')).read_bytes()
print('DETERMINISTISCH' if a == b else 'FAIL: Builds differieren')
"
```

Erwartung: `DETERMINISTISCH`.

- [ ] **Step 6.4: Feld wirklich weg + Struktur valide**

```bash
python -c "
import gzip, json
for f in ('data/corpus-index.json.gz', 'data/authority-index.json.gz'):
    d = json.load(gzip.open(f, 'rt', encoding='utf-8'))
    assert 'generatedAt' not in d, f
    print(f, d['version'], 'OK')
"
python scripts/validate-indices.py
```

Erwartung: `... 4.1.4 OK`, `... 1.4.1 OK`, validate-indices durchgängig `[PASS]`.

---

### Task 7: Workflow-Konsolidierung `data-integrity.yml`

**Files:**
- Rename+Modify: `.github/workflows/schema-validation.yml` → `.github/workflows/data-integrity.yml`
- Delete: `.github/workflows/index-version-check.yml`

- [ ] **Step 7.1: Lokale lxml-Version ermitteln (für den Pin)**

```bash
python -c "import lxml; print(lxml.__version__)"
```

Die Ausgabe (z.B. `5.4.0`) unten als `<LXML_VERSION>` einsetzen.

- [ ] **Step 7.2: Umbenennen + Inhalt ersetzen**

```bash
git mv .github/workflows/schema-validation.yml .github/workflows/data-integrity.yml
```

Dann den **kompletten** Dateiinhalt ersetzen durch (`<LXML_VERSION>` aus Step 7.1 einsetzen; die Steps „Download tei_all.rng" und „Verify TEI P5 version pin" UNVERÄNDERT aus der alten Datei übernehmen, inkl. NBSP-Hinweis-Kommentar):

```yaml
name: Data Integrity

# Ein konsolidiertes Daten-Gate (#125): prueft Quellen UND abgeleitete
# Schicht (Indexe, variants.xml) in einem Job, Steps von billig nach
# teuer (fail fast). Konsolidiert das fruehere index-version-check.yml
# (Step 1) und schema-validation.yml (Steps 2-3, 6-7).
#
#   1. Index-Versions-Konstanten: Build-Skripte und corpus-loader.js
#      muessen dieselbe Version nennen, sonst greift die Cache-
#      Invalidierung nicht (#47.3).
#   2. RNC->RNG sync check (P2-14).
#   3. TEI-P5-Versions-Pin fuer tei_all.rng.
#   4. Freshness variants.xml: extract-variants.py --apply muss die
#      committete Datei byte-identisch reproduzieren, sonst wurde nach
#      einer Korpus-Aenderung die Regenerierung vergessen. MUSS als
#      blockierender Step VOR Step 5 stehen: der Index-Vergleich kann
#      variants-Drift prinzipiell nicht erkennen (der Rebuild nutzt
#      dieselbe committete variants.xml und matcht). Nie auf advisory
#      herunterstufen.
#   5. Freshness Indexe (Rebuild-and-Compare): beide Indexe frisch
#      bauen, DEKOMPRIMIERTEN Inhalt mit dem committeten Stand
#      vergleichen (gzip-Bytes koennen je zlib-Build variieren).
#      Traegt nur, weil die Builds seit #125 deterministisch sind
#      (kein generatedAt, sorted glob, gzip mtime=0).
#   6. Zweistufige RelaxNG-Validierung (P2-13): Stage 2
#      (mhdbdb.rng / mhdbdb-authority.rng) ist das harte Gate;
#      Stage-1-Baseline-Fails (#30) sind nur Warnungen.
#   7. Authority cross-reference integrity (#44/#115): dangling Refs
#      ausserhalb lexicon.xml brechen den Build (lexicon traegt eine
#      bekannte Backfill-Baseline und wird nur reportet).
#
# lxml ist gepinnt: eine neue lxml-Serialisierung wuerde sonst in
# Step 4/5 als falscher Drift-Alarm erscheinen. Bei Pin-Bump lokal
# dieselbe Version installieren und Indexe einmal rebuilden.

on:
  pull_request:
    paths:
      - 'schema/**'
      - 'tei/**'
      - 'authority-files/**'
      - 'data/corpus-index.json.gz'
      - 'data/authority-index.json.gz'
      - 'scripts/build-corpus-index.py'
      - 'scripts/build-authority-index.py'
      - 'scripts/mhg_normalizer.py'
      - 'scripts/sync/extract-variants.py'
      - 'scripts/audit/validate-corpus.py'
      - 'scripts/audit/check-index-versions.py'
      - 'assets/js/lib/corpus-loader.js'
      - '.github/workflows/data-integrity.yml'
  # Direct-to-main pushes also trigger the workflow (Branch-Protection
  # ist historisch umgangen worden, z.B. WZB-Merge 2026-05-06).
  push:
    branches:
      - main
    paths:
      - 'schema/**'
      - 'tei/**'
      - 'authority-files/**'
      - 'data/corpus-index.json.gz'
      - 'data/authority-index.json.gz'
      - 'scripts/build-corpus-index.py'
      - 'scripts/build-authority-index.py'
      - 'scripts/mhg_normalizer.py'
      - 'scripts/sync/extract-variants.py'
      - 'scripts/audit/validate-corpus.py'
      - 'scripts/audit/check-index-versions.py'
      - 'assets/js/lib/corpus-loader.js'
      - '.github/workflows/data-integrity.yml'
  workflow_dispatch:

concurrency:
  group: data-integrity-${{ github.ref }}
  cancel-in-progress: true

jobs:
  validate:
    runs-on: ubuntu-latest
    # Checkout ~2 min (grosses Repo) + Index-Builds + RelaxNG-Validierung.
    timeout-minutes: 30
    steps:
      - name: Checkout
        uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: pip install --quiet lxml==<LXML_VERSION> rnc2rng

      - name: Index version consistency (#47.3)
        run: python scripts/audit/check-index-versions.py

      - name: Regenerate RNG from RNC (P2-14 drift check)
        run: |
          python -m rnc2rng schema/mhdbdb.rnc schema/mhdbdb.rng
          python -m rnc2rng schema/mhdbdb-authority.rnc schema/mhdbdb-authority.rng

      - name: Fail if committed .rng differs from regenerated .rng
        run: |
          if ! git diff --exit-code schema/mhdbdb.rng schema/mhdbdb-authority.rng; then
            echo "::error title=RNG drift::Committed .rng files are out of sync with their .rnc sources. Run 'python -m rnc2rng schema/mhdbdb.rnc schema/mhdbdb.rng && python -m rnc2rng schema/mhdbdb-authority.rnc schema/mhdbdb-authority.rng' locally and commit the result."
            exit 1
          fi

      # >>> Steps "Download tei_all.rng" und "Verify TEI P5 version pin"
      # >>> hier 1:1 aus der alten schema-validation.yml uebernehmen <<<

      - name: Freshness variants.xml (#125)
        run: |
          python scripts/sync/extract-variants.py --apply
          if ! git diff --exit-code -- authority-files/variants.xml; then
            echo "::error file=authority-files/variants.xml::variants.xml ist nicht mit dem Korpus synchron. Lokal 'python scripts/sync/extract-variants.py --apply' ausfuehren und mitcommitten (DATA-MODEL.md -> Data-Change-Lifecycle)."
            exit 1
          fi

      - name: Freshness Indexe — Rebuild-and-Compare (#125)
        run: |
          mkdir -p "$RUNNER_TEMP/committed"
          cp data/corpus-index.json.gz data/authority-index.json.gz "$RUNNER_TEMP/committed/"
          python scripts/build-corpus-index.py
          python scripts/build-authority-index.py
          python - <<'EOF'
          import gzip, os, sys
          tmp = os.path.join(os.environ['RUNNER_TEMP'], 'committed')
          ok = True
          for name in ('corpus-index.json.gz', 'authority-index.json.gz'):
              fresh = gzip.open(os.path.join('data', name), 'rb').read()
              committed = gzip.open(os.path.join(tmp, name), 'rb').read()
              if fresh == committed:
                  print(f'{name}: OK (Rebuild byte-identisch nach Dekompression)')
              else:
                  print(f'::error file=data/{name}::{name} ist nicht mit dem Quellstand '
                        'synchron: Rebuild aus den aktuellen Quellen liefert anderen Inhalt. '
                        'Lokal rebuilden, Version bumpen und mitcommitten '
                        '(DATA-MODEL.md -> Data-Change-Lifecycle).')
                  ok = False
          sys.exit(0 if ok else 1)
          EOF

      - name: Validate corpus and authority files (P2-13)
        run: python scripts/audit/validate-corpus.py --fail-fast

      - name: Authority cross-reference integrity (#44/#115)
        run: python scripts/audit/check-authority-cross-refs.py --check
```

- [ ] **Step 7.3: Alten Versions-Workflow löschen**

```bash
git rm .github/workflows/index-version-check.yml
```

- [ ] **Step 7.4: YAML-Plausibilität**

```bash
python -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('.github/workflows/data-integrity.yml').read_text(encoding='utf-8')); print('YAML OK')"
```

Falls PyYAML lokal fehlt (`ModuleNotFoundError`): Step überspringen und vermerken — der PR-CI-Lauf validiert das YAML ohnehin.

---

### Task 8: `scripts/audit/check-index-freshness.py` Docstring

**Files:**
- Modify: `scripts/audit/check-index-freshness.py:30-35`

- [ ] **Step 8.1: Stale Advisory-Hinweis ersetzen**

```python
# ALT (Z. 30-35):
Read-only. Exit 0 = frisch, 1 = veraltet, 2 = kein git / Setup-Fehler.
Derzeit als lokales Advisory gedacht (CI-Wiring + generatedAt-Determinismus
sind als Folge-Issue ausgelagert): die Erkennung ist quelldatei-granular und
ueber-flaggt Quelländerungen, die kein indexiertes Feld betreffen (z.B. reine
@corresp-Entfernung). Vor einem Rebuild also Index-Relevanz der Aenderung
pruefen.
# NEU:
Read-only. Exit 0 = frisch, 1 = veraltet, 2 = kein git / Setup-Fehler.
Lokales Advisory, v.a. fuer den Working-Tree-Check vor dem Commit (den CI
nicht sehen kann). Das harte CI-Gate ist seit #125 der Rebuild-and-Compare-
Step in .github/workflows/data-integrity.yml. Die Erkennung hier bleibt
quelldatei-granular und ueber-flaggt Quelländerungen, die kein indexiertes
Feld betreffen (z.B. reine @corresp-Entfernung) -- vor einem Rebuild also
Index-Relevanz pruefen.
```

- [ ] **Step 8.2: Syntax-Check**

```bash
python -m py_compile scripts/audit/check-index-freshness.py && echo OK
```

---

### Task 9: Dokumentation

**Files:**
- Modify: `docs/DATA-MODEL.md` (Lifecycle-Tabellen ~Z. 759-784), `docs/DEVELOPMENT.md` (~Z. 181-210), `docs/TEI-MODEL.md` (§11, Z. 915-916), `docs/INDEX.md` (Current-Phase-Versionszeile), `CLAUDE.md` (Key Patterns)

- [ ] **Step 9.1: TEI-MODEL.md §11 (Source of Truth zuerst)**

```
| Corpus Index | 4.1.3 | 2026-05-16 |     →  | Corpus Index | 4.1.4 | 2026-06-12 |
| Authority Index | 1.4.0 | 2026-05-29 |  →  | Authority Index | 1.4.1 | 2026-06-12 |
```

- [ ] **Step 9.2: INDEX.md Versions-Pointer (Abschnitt „Current Phase", letzter Absatz)**

```
ALT: (Stand 2026-05-29: Corpus Index v4.1.3, Authority Index v1.4.0)
NEU: (Stand 2026-06-12: Corpus Index v4.1.4, Authority Index v1.4.1)
```

- [ ] **Step 9.3: CLAUDE.md Key Patterns**

```
ALT: - **Pre-built indexes**: authority (3 MB gz, v1.4.0) + corpus (~40 MB gz, v4.1.3). See DATA-MODEL.md for schemas.
NEU: - **Pre-built indexes**: authority (3 MB gz, v1.4.1) + corpus (~40 MB gz, v4.1.4). See DATA-MODEL.md for schemas.
```

- [ ] **Step 9.4: DATA-MODEL.md Lifecycle-Tabellen**

In der tei-Tabelle (Z. 761-772):
- Zeile 2, Spalte „Bricht wenn vergessen": `schema-validation.yml` → `data-integrity.yml`
- Zeile 3, Status: `manuell` → `CI (Freshness-Gate in data-integrity.yml)`
- Zeile 4, Status: `manuell` → `CI (Freshness-Gate)`
- Zeile 5, Status: `manuell` → `CI (Freshness-Gate)`
- Zeile 7, Status: `CI (in schema-validation.yml)` → `CI (in data-integrity.yml)`

In der authority-Tabelle (Z. 776-782):
- Zeile 2, Status: `manuell` → `CI (Freshness-Gate in data-integrity.yml)`

Nach der Status-Legende (Z. 752) einen Absatz ergänzen:

```markdown
**Seit #125 (2026-06-12):** Die Index-Builds sind deterministisch (kein `generatedAt`, sortiertes glob, gzip ohne mtime) — ein No-op-Rebuild aus unverändertem Quellstand erzeugt **keinen Diff** mehr; „sicherheitshalber rebuilden" ist damit kostenlos. Das CI-Gate `data-integrity.yml` rebuildet variants.xml + beide Indexe bei jedem Daten-PR und vergleicht den dekomprimierten Inhalt mit dem committeten Stand: vergessene Rebuilds (Schritte 3-5) blocken den Merge.
```

- [ ] **Step 9.5: DEVELOPMENT.md CI-Sektionen mergen**

Die Abschnitte `### CI: Schema Validation` (ab Z. 181) und `### CI: Index Version Consistency` (Z. 201-210) durch EINEN Abschnitt ersetzen:

```markdown
### CI: Data Integrity

**Workflow:** `.github/workflows/data-integrity.yml` (konsolidiert seit #125 die früheren `schema-validation.yml` + `index-version-check.yml`)
**Triggers:** PRs + main-Pushes, die `schema/`, `tei/`, `authority-files/`, die zwei Index-`.json.gz`, die Build-Skripte (`build-*-index.py`, `mhg_normalizer.py`, `extract-variants.py`), `check-index-versions.py` oder `corpus-loader.js` berühren. Plus `workflow_dispatch`.

**Sieben Checks, billig → teuer (fail fast):**

1. **Index-Versions-Konstanten** (#47.3) — Build-Skripte + `corpus-loader.js` müssen dieselben Versionen nennen, sonst greift die IndexedDB-Cache-Invalidierung nicht. Lokal: `python scripts/audit/check-index-versions.py`.
2. **RNC→RNG sync check** (P2-14) — regeneriert `.rng` aus `.rnc`, Diff = Fail.
3. **TEI-P5-Pin** — `tei_all.rng` wird frisch geladen und gegen die gepinnte Version (4.11.0) geprüft.
4. **Freshness variants.xml** (#125) — `extract-variants.py --apply` muss die committete Datei byte-identisch reproduzieren („Korpus geändert, variants.xml vergessen"). Blockierend VOR Check 5: der Index-Vergleich allein kann variants-Drift nicht erkennen.
5. **Freshness Indexe** (#125, Rebuild-and-Compare) — beide Indexe werden frisch gebaut und dekomprimiert mit dem committeten Stand verglichen („Quelle/Build-Skript geändert, Rebuild vergessen"). Funktioniert nur, weil die Builds deterministisch sind.
6. **Zweistufige RelaxNG-Validierung** (P2-13) — Stage 1 `tei_all.rng` (Warnungen, #30-Baseline), Stage 2 `mhdbdb.rng`/`mhdbdb-authority.rng` (hartes Gate).
7. **Cross-Reference-Integrity** (#44/#115) — dangling Refs außerhalb `lexicon.xml` brechen den Build.

**Hinweis lxml-Pin:** lxml ist im Workflow gepinnt, damit Serialisierungsänderungen neuer lxml-Versionen nicht als Drift-Fehlalarm erscheinen. Beim Pin-Bump lokal dieselbe Version installieren.

**Debugging failures:**
- Versions-Drift → `python scripts/audit/check-index-versions.py` lokal, Konstanten angleichen
- RNG drift → `python -m rnc2rng schema/mhdbdb.rnc schema/mhdbdb.rng` lokal, committen
- variants-/Index-Freshness → Data-Change-Lifecycle in DATA-MODEL.md abarbeiten (regenerieren, rebuilden, bumpen, alles in einem Commit)
- Stage 2 fail → `python scripts/audit/validate-corpus.py --sample <SIGLE>` lokal
- TEI version mismatch → `EXPECTED` im Workflow + `schema/README.md` bumpen
```

(Die Detail-Inhalte der zwei alten Abschnitte — „Two checks", „Hintergrund #47.3", „Was der Check macht" — gehen in dieser kompakteren Form auf; den Release-Check-Abschnitt darunter NICHT anfassen.)

- [ ] **Step 9.6: Sweep nach stale Workflow-Verweisen**

```bash
grep -rn "schema-validation.yml\|index-version-check" docs/ CLAUDE.md README.md scripts/ --include="*.md" --include="*.py"
```

Treffer bewerten: historische Erwähnungen in JOURNAL.md/INDEX.md-Milestones und DECISIONS.md bleiben (Geschichtsschreibung); operative Verweise (z.B. in DATA-MODEL.md, CLAUDE.md „Gotchas"/CI-Hinweise, Docstrings von Audit-Skripten) auf `data-integrity.yml` umstellen. Jeden geänderten Treffer im Bericht listen.

---

### Task 10: Abschluss — Freigabe-Gate, Commit, PR

**STOP: Ab hier nichts ohne Christians explizite Freigabe.**

- [ ] **Step 10.1: Statusbericht an Christian**

Zusammenfassen: Doppel-Build-Ergebnis + gemessene Build-Dauern, variants-No-op-Ergebnis (bzw. legitime Drift), geänderte Dateien (`git status --porcelain`), offene Auffälligkeiten. Fragen: (a) Freigabe für Commit + Push + PR? (b) `npm test` vorher laufen lassen?

- [ ] **Step 10.2: Nach Freigabe — gezielt stagen (NIE `git add -A`)**

```bash
git add scripts/build-corpus-index.py scripts/build-authority-index.py \
  scripts/validate-indices.py scripts/sync/extract-variants.py \
  scripts/audit/check-index-freshness.py assets/js/lib/corpus-loader.js \
  data/corpus-index.json.gz data/authority-index.json.gz \
  .github/workflows/data-integrity.yml \
  docs/DATA-MODEL.md docs/DEVELOPMENT.md docs/TEI-MODEL.md docs/INDEX.md CLAUDE.md \
  docs/features/125-index-determinismus-freshness-gate.md \
  docs/features/125-index-determinismus-freshness-gate-plan.md
# Falls Task 6.1 echte variants-Drift ergab: zusätzlich authority-files/variants.xml
# (git mv/git rm der Workflows ist bereits gestaged)
# Weitere Dateien aus Step 9.6 ggf. ergänzen
```

- [ ] **Step 10.3: Commit (Projekt-Format)**

```bash
git commit -m "Deterministische Index-Builds + CI-Freshness-Gate (Closes #125)

## Changes
- generatedAt aus beiden Index-Builds entfernt, glob sortiert, gzip mtime=0: identischer Quellstand ergibt identische Index-Bytes
- extract-variants.py: <date> nur noch bei inhaltlicher Aenderung (No-op-Lauf diff-frei)
- Index-Versionen 4.1.4 / 1.4.1 (drei Stellen + validate-indices)
- CI konsolidiert: schema-validation.yml + index-version-check.yml -> data-integrity.yml mit Rebuild-and-Compare-Freshness-Gate
- Doku: Lifecycle-Status (DATA-MODEL), CI-Sektion (DEVELOPMENT), Versionstabelle (TEI-MODEL Para 11, INDEX, CLAUDE.md)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

- [ ] **Step 10.4: Push + PR (der PR-Lauf ist der Cross-Plattform-Beweis)**

```bash
git push -u origin feature/125-index-determinism
gh pr create --title "Deterministische Index-Builds + CI-Freshness-Gate (#125)" --body "..."
```

PR-Body: Spec-Verweis, Doppel-Build-Beleg, Hinweis dass der `data-integrity`-Check in diesem PR selbst erstmals läuft (Windows-gebaute Indexe vs. Linux-Rebuild). Danach CI beobachten; schlägt Step 4/5 mit Plattform-Drift fehl → Ursache im PR fixen (Spec §Abschlusskriterien).

- [ ] **Step 10.5: Nach Merge (separate Session ok)**

Feature-Docs `125-*.md` löschen nachdem das Wissen extrahiert ist (Temporal-Artifacts-Konvention); Scorecard-Eintrag in JOURNAL.md.

---

## Self-Review (durchgeführt beim Schreiben)

- **Spec-Coverage:** Teil 1 → Tasks 1-5; Teil 2 → Task 7; Flankierend → Tasks 8-9; Abschlusskriterien → Tasks 6 + 10. Spec-Punkt „README-Badge prüfen": erledigt, README hat keine Workflow-Badges (nur Lizenz/DOI-Shields).
- **Platzhalter:** `<LXML_VERSION>` ist bewusst ein benannter Einsetz-Wert mit Ermittlungs-Step (7.1) — kein TBD.
- **Konsistenz:** Versionsnummern 4.1.4/1.4.1 in Tasks 1, 2, 4, 6, 9 identisch; Workflow-Dateiname `data-integrity.yml` in Tasks 7, 8, 9 identisch; `--apply` überall wo extract-variants produktiv läuft.
