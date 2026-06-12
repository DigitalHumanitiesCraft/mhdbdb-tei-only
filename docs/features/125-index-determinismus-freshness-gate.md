# #125 generatedAt-Determinismus + Freshness-Gate (Design-Spec)

**Issue:** [#125](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/125) · **Status:** Design approved (Christian, 2026-06-12) · **Lebensdauer:** bis Issue-Close, dann Wissen in stabile Docs extrahieren und löschen (Temporal-Artifacts-Konvention).

## Ziel

Identischer Quellstand soll identische Index-Bytes ergeben (Teil 1), damit ein CI-Gate „Quelle geändert, abgeleitete Schicht nicht nachgezogen" exakt erkennen kann (Teil 2). Operationalisiert den Data-Change-Lifecycle (DATA-MODEL.md) gegen die stille Drift aus #44/#115.

## Gewählter Ansatz: Rebuild-and-Compare

Das CI-Gate baut variants.xml und beide Indexe frisch und vergleicht mit dem committeten Stand. Das ist nur mit Teil 1 (Determinismus) möglich und dann **exakt**: index-irrelevante Quelländerungen erzeugen identische Bytes (kein Über-Flagging), und es gibt keinen No-op-Deadlock.

**Verworfene Alternativen:**

1. **Topologisches Gate in CI** (`check-index-freshness.py` direkt verdrahten): über-flaggt index-irrelevante Änderungen UND hat einen No-op-Deadlock — wenn ein Rebuild keinen Diff erzeugt, gibt es nichts zu committen, der Artefakt-Commit kann nie jünger werden als der Quell-Commit, das Gate bliebe dauerhaft rot.
2. **Content-Hash-Manifest** (Teil 2a im Issue): das Manifest zu prüfen heißt faktisch die Extraktion laufen zu lassen — kaum billiger als Rebuild-and-Compare, dafür mehr Code und eine zweite Wahrheit, die driften kann. Entfällt ersatzlos.
3. **generatedAt deterministisch aus Commit-Datum** (Naming-Vorbild #59): hat beim Lifecycle-Commit ein Henne-Ei-Problem — gebaut wird *vor* dem Commit, das Datum zeigt also lokal auf den Vor-Commit, beim CI-Rebuild auf den aktuellen Commit → falscher Diff. Stattdessen: Feld entfernen (wird in keinem JS/HTML referenziert, nur `validate-indices.py` verlangt es).
4. **Neuer eigener Workflow / Umbau von `index-version-check.yml`:** verworfen zugunsten der Integration in `schema-validation.yml` (Workflow-Anzahl klein halten, ein Daten-Gate statt zwei parallelen).

## Teil 1: Determinismus

| Datei | Änderung |
|---|---|
| `scripts/build-corpus-index.py` | `generatedAt` entfernen; `TEI_DIR.glob(...)` → `sorted(...)` (Z. 266, Iterationsreihenfolge ist OS-abhängig); `gzip.open(...)` → `gzip.GzipFile(..., mtime=0)`; Version `4.1.3` → `4.1.4` |
| `scripts/build-authority-index.py` | `generatedAt` entfernen; `gzip.GzipFile(..., mtime=0)`; Version `1.4.0` → `1.4.1` (kein glob, liest feste Dateien) |
| `scripts/validate-indices.py` | `generatedAt` aus den `required_fields` beider Indexe streichen |
| `assets/js/lib/corpus-loader.js` | `INDEX_VERSION` → `4.1.4`, `AUTHORITY_INDEX_VERSION` → `1.4.1` (Drei-Stellen-Regel; lokal `python scripts/audit/check-index-versions.py` als Gegenprobe) |
| `scripts/sync/extract-variants.py` | **Datum nur bei inhaltlicher Änderung:** neuen Inhalt generieren, mit bestehender Datei unter Ausblendung der einen `<date>`-Zeile (Z. 140) vergleichen; identisch → bestehendes Datum übernehmen (Output byte-identisch), sonst heutiges Datum (Datei fehlt → Fallback heutiges Datum, kein Vergleich). Semantik des `<date>` wird damit „Stand der Daten" statt „letzter Script-Lauf" — als Kommentar im Script dokumentieren |

Vorbild für `mtime=0` + Byte-Diff-Tauglichkeit: `scripts/ingest/naming/01-fetch-and-build-index.py` (#59).

**Versions-Bump-Begründung:** Inhaltlich sind die Daten identisch, aber der Patch-Bump hält den Lifecycle sauber und erzwingt einen konsistenten Cache-Stand (Nutzer laden einmal neu; das alte gecachte `generatedAt`-Feld wäre harmlos, aber inkonsistent).

**Determinismus-Annahme:** „identische Bytes" gilt für gleiche Quellen + gleiches Script + gleiche Umgebung. CI pinnt Python 3.13 wie lokal; **lxml wird im Workflow ebenfalls gepinnt** (Version beim Umsetzen aus der lokalen Umgebung übernehmen, `pip install lxml==X.Y.Z`), damit eine künftige lxml-Serialisierungsänderung nicht als falscher Drift-Alarm erscheint. Der gzip-Layer wird im Gate bewusst NICHT verglichen (theoretische zlib-Plattformvarianz Windows/Linux), sondern der dekomprimierte JSON-Inhalt.

## Teil 2: CI-Gate in `schema-validation.yml`

Kein neuer Workflow, kein neuer Job. `index-version-check.yml` wird **gelöscht** und sein Check als Step übernommen; der Workflow heißt künftig „Data Integrity" (Datei-Rename auf `data-integrity.yml`, Header-Kommentar anpassen). Ergebnis: 4 statt 5 Workflows, ein Daten-Gate.

**Step-Reihenfolge (billig → teuer, fail fast):**

1. Index-Versions-Konstanten (`check-index-versions.py`, Sekunden) — aus `index-version-check.yml` übernommen
2. RNC→RNG-Drift (Sekunden, bestehend)
3. TEI-P5-Pin (Sekunden, bestehend)
4. **Freshness variants.xml (neu):** `python scripts/sync/extract-variants.py --apply` (ohne `--apply` schreibt das Script nur einen Dry-Run nach `variants.regen.xml`) + `git diff --exit-code -- authority-files/variants.xml`. Fehlschlag = „Korpus geändert, variants.xml nicht regeneriert"
5. **Freshness Indexe (neu):** committete `data/corpus-index.json.gz` + `data/authority-index.json.gz` vorab nach `$RUNNER_TEMP` sichern; beide Builds laufen lassen; dekomprimierten Inhalt (frisch vs. gesichert) per Inline-Python-Step byteweise vergleichen. Fehlschlag = „Quelle oder Build-Skript geändert, Index nicht rebuilt". Wichtig: Step 4 muss als **blockierender** Check VOR Step 5 stehen — Step 5 allein kann variants-Drift prinzipiell nicht erkennen, weil der CI-Rebuild den Authority-Index aus derselben (ggf. veralteten) committeten variants.xml bauen und ein Match liefern würde. Nur Step 4 fängt diesen Fall; Step 4 darf deshalb nie auf „advisory" heruntergestuft werden
6. RelaxNG-Validierung (Minuten, bestehend)
7. Cross-Ref-Integrity (bestehend)

**Trigger-Pfade erweitern um:** `data/corpus-index.json.gz`, `data/authority-index.json.gz` (bewusst NICHT `data/**` — sonst zieht der Merge des wöchentlichen Naming-Index-PR auf main das volle Gate; der Auto-PR selbst triggert per `GITHUB_TOKEN` ohnehin keine Workflows, der Push danach schon), `scripts/build-corpus-index.py`, `scripts/build-authority-index.py`, `scripts/mhg_normalizer.py` (wird von beiden Build-Skripten importiert — eine Änderung dort ändert den Index-Inhalt), `scripts/sync/extract-variants.py`, `scripts/audit/check-index-versions.py`, `assets/js/lib/corpus-loader.js`. Bestehende Pfade (`schema/**`, `tei/**`, `authority-files/**`, `validate-corpus.py`, Workflow-Datei selbst) bleiben.

**Timeout:** von 20 auf 45 min erhöht (Index-Builds kommen dazu; lokal gemessen: Corpus ~4,5 min, Authority ~15 s — 45 min lassen Luft für langsame Runner, nach den ersten realen Läufen ggf. nachjustieren. Ursprünglich waren 30 min geplant).

**Akzeptierter Schönheitsfehler:** Ein PR, der nur ein Build-Skript oder `corpus-loader.js` ändert, triggert auch die RelaxNG-Validierung mit — selten und verschmerzbar.

## Flankierend

- `scripts/audit/check-index-freshness.py`: nur Docstring aktualisieren (der Hinweis „CI-Wiring als Folge-Issue ausgelagert" wäre stale). Bleibt als schnelles lokales Advisory, insbesondere für den Working-Tree-Check vor dem Commit, den CI nicht sehen kann.
- **Doku:** DATA-MODEL.md (Data-Change-Lifecycle: No-op-Rebuilds jetzt diff-frei, CI-Gate erwähnen), DEVELOPMENT.md (Workflow-Liste: index-version-check raus, data-integrity rein), TEI-MODEL.md §11 (neue Versionsnummern), CLAUDE.md Key Patterns (Versionsnummern im Index-Hinweis), README-Badge prüfen (falls einer auf den alten Workflow-Namen zeigt).
- **naming-index.json.gz bleibt außen vor:** hat eigenen Update-Workflow mit eigenem Determinismus-Mechanismus (#59); `contributors.xml` ist kein Index-Input.

## Abschlusskriterien

- Doppel-Build-Test lokal: beide Indexe zweimal bauen → Bytes identisch.
- `python scripts/audit/check-index-versions.py` grün.
- `extract-variants.py` zweimal laufen lassen → kein Diff (Datum-bei-Änderung-Logik greift).
- Der PR-CI-Lauf selbst ist der Cross-Plattform-Beweis (Windows-gebaute Indexe vs. Linux-Rebuild); taucht dort eine versteckte Ordnungs-/Formatierungsquelle auf, fixen wir sie im PR.
- Playwright (`npm test`) nur nach Rückfrage.
- Kein Commit/Push ohne Christians Freigabe; nur gezielt benannte Dateien stagen (parallele Sessions).
- Commit darf `Closes #125` enthalten (kein Evergreen-Issue betroffen).
