# 032 — Schema Follow-up Cleanup

**Status:** ✅ **17/17 erledigt** (Stand 2026-05-07). Plan ist abgeschlossen, Doku archivierbar.
**Audience:** Nächste/r CC-Kollege/in (für historischen Kontext)
**Baseline (verifiziert 2026-05-07, nach WZB-Merge + P1-5):**

| Check | Ergebnis |
|-------|---------|
| `schema/examples/*` gegen beide Stages | 9 / 9 grün |
| `authority-files/*.xml` gegen beide Stages | 8 / 8 grün |
| `schema/mhdbdb.rnc` ↔ `.rng` Sync | in sync |
| `schema/mhdbdb-authority.rnc` ↔ `.rng` Sync | in sync |
| Korpus (667 Dateien inkl. WZB) gegen beide Stages | Stage 1: 30/667 fails (#30-Baseline), Stage 2: 0/667 |

**Scope:** Rein additive Schärfungen nach Abschluss der großen Migration. Keine Architekturänderungen. Alle Punkte sind einzeln reversibel.

---

## Status-Übersicht (Stand 2026-04-15)

| Item | Status | Commit | Bemerkung |
|------|--------|--------|-----------|
| P0-1 docs `idno type="gnd"` → `GND` | ✅ done | `5b421319c` | |
| P0-2 docs `<schemaRef>`/`<tagsDecl>` raus | ✅ done | `5b421319c` | |
| P0-3 docs `usage="95"` raus | ✅ done | `5b421319c` | |
| P0-4 Korpus `gnd`→`GND` | ✅ done | `61a0b4a1a` | 2026-04-11 |
| P0-5 WorksSyncer gnd→GND Drift-Prevention | ✅ done | `05e9c2d91` | war nicht im Plan, nach P0-4 eingezogen |
| P1-5 Korpus `idno/@type` Enum | ✅ done | (siehe Schema-Commit 2026-05-07) | kontextspezifisch: 3 Patterns für `msIdentifier` / `monogr` / `person` |
| P1-6 Korpus `persName/@type` Enum | ✅ done | `f72887eaa` | 2026-04-15 |
| P1-7 Authority `lexicon.entry` gramGrp/sense | ✅ done | `f436963e0` | 2026-04-14 |
| P1-8 Authority `monogr/title` Pflicht | ✅ done | `f436963e0` | 2026-04-14 |
| P1-9 Authority `works.bibl/idno` Enum | ✅ done | `f436963e0` | 2026-04-14 |
| P1-10 Korpus `msIdentifier/@corresp` Pflicht | ✅ done | `83b511eec` | 2026-04-15 |
| P2-11 Taxonomie-Body ↔ encodingDesc Doku | ✅ done | `7e526c8f2` | 2026-04-15, Option 3 (Kommentar) |
| P2-12 `validate-corpus.py` rewrite | ✅ done | `e9d43ead4` | 2026-04-15 |
| P2-13 CI-Regression schema-validation.yml | ✅ done | `7d3801520` | 2026-04-15, zusammen mit P2-14 |
| P2-14 RNC→RNG Drift Check in CI | ✅ done | `7d3801520` | 2026-04-15, als Teil von P2-13 (git diff --exit-code auf schema/*.rng) |
| P2-15 Korpus xml-model PIs | ✅ done | `674fd3258` | 2026-04-15 |
| P3-x Schematron-Territorium | ⏳ deferred | — | bewusst vertagt, kein Ticket |

**Zusätzliche Arbeit** (nicht ursprünglich im Plan, aber zum selben Zeitraum):

| Thema | Commits |
|-------|---------|
| `<hi>`-Rekursion entfernen (Data-First Schema-Simplification) | `b3e76ce7b` Daten-Flatten + `38b0bdd10` Schema |
| Mega-`<p>` Split in PL1/PL2/PL3 (Validation-Performance) | `49d7b58aa` + `67526399e` archive |
| `contributors.xml` + Authority-Schema contributors.body | `6f80e5d47` + `b95d0ae42` (orgName/@ref → idno type="URL") |
| xml-model PIs für authority-files + examples | `9cda50c44` |
| CLAUDE.md Hard Constraint "Daten vor Schema" | `9ab92cdb2` |
| Wegfall `.github/workflows/claude.yml` | `54b450f32` |

**Arbeit nach P1-5 Re-Audit (2026-05-07):**

| Thema | Was |
|-------|-----|
| WZB shelfmark-Fix (Daten vor Schema) | `<idno type="shelfmark">` aus WZB.tei.xml entfernt — Info steht via `corresp` schon in `works.xml#work_WZB`. Kein Datenverlust, WZB jetzt Stage-1-konform. |
| P1-5 Implementation | 3 kontextspezifische Enum-Patterns: `idno.type.msIdentifier`, `idno.type.monogr`, `idno.type.person`. 7 erlaubte Werte gesamt. |
| Stage-1 PI aus 667 Korpus-Files | `<?xml-model href="...tei_all.rng"?>` entfernt, weil die 30 GAP-Files in Editoren konstante false-positives gegen `tei_all.rng` produzierten. Stage-2-PI bleibt. Volle 2-Stage-Validation läuft weiterhin in CI. |
| CI-Trigger erweitert | `schema-validation.yml` triggert jetzt auch auf direkte main-Pushes (vorher nur PRs). Schließt die Lücke, die WZB-Merge 2026-05-06 sichtbar machte. |

---

## Wie diese Liste entstanden ist

Zwei Iterationen einer manuellen Gegenüberstellung von:

- `schema/mhdbdb.rnc`, `schema/mhdbdb-authority.rnc`
- `docs/TEI-MODEL.md`, `docs/TEI-MODEL-AUTH-FILES.md`
- Stichproben aus `tei/*.tei.xml` und `authority-files/*.xml`

Verifikationskommandos, die die Befunde belegen, sind in den jeweiligen Abschnitten eingebettet — bitte vor und nach der Umsetzung laufen lassen.

---

## P0 — Dokumentation lügt (schnell fixen)

Die Doku behauptet Dinge, die es in den realen Dateien nicht gibt. Das ist das gefährlichste Szenario: jemand schreibt neue Dateien nach `TEI-MODEL.md` und produziert Schema-Violations.

### P0-1 · `docs/TEI-MODEL.md:68` — `<idno type="gnd">` ist falsch

Die Spec zeigt `<idno type="gnd">` (lowercase) im Header-Beispiel, die Authority-Doku verlangt aber einheitlich `GND` (uppercase).

**Fix:** `gnd` → `GND` in der einen Zeile.

```bash
Grep: grep -n 'type="gnd"' docs/TEI-MODEL.md
```

### P0-2 · `docs/TEI-MODEL.md:119–123` — `<schemaRef>` und `<tagsDecl>/<rendition>` existieren nicht im Korpus

```bash
Grep: grep -rl '<schemaRef\|<tagsDecl' tei/          # → 0 matches
```

**Fix:** Beide Blöcke aus dem Beispiel in §2.2 entfernen. Das Schema hat sie bewusst nicht — Spec folgt dem Schema, nicht umgekehrt.

### P0-3 · `docs/TEI-MODEL.md:145` — `<language ident="gmh" usage="95">` zeigt ein Attribut, das nirgends vorkommt

```bash
Grep: grep -rl 'language ident=".*" usage=' tei/     # → 0 matches
```

**Fix:** `usage="95"` aus dem Beispiel entfernen. Kommentar „falls vorhanden" für die Latein-Zeile bleibt, das ist ok.

### P0-4 · Korpus: `<idno type="gnd">` vs `"GND"` gemischt

In den 666 Korpusdateien existieren **beide Schreibweisen parallel** (bestätigt: jeweils 30+ Treffer). Das ist ein echtes Daten-Problem, keine reine Doku-Inkonsistenz.

```bash
Grep: grep -l 'idno type="gnd"' tei/  | wc -l
Grep: grep -l 'idno type="GND"' tei/  | wc -l
```

**Fix:** Kleines Migrationsscript analog zur Authority-Migration (`TEI-MODEL-AUTH-FILES.md §2.4`, 2026-04-10 durchgeführt). Ablauf:

1. `tei/*.tei.xml` öffnen, jedes `idno[@type="gnd"]` → `@type="GND"`.
2. `git status` prüfen (nur Attribut-Typ-Änderungen).
3. Validierung gegen beide Stages, Diff gegen `git show HEAD:tei/...` auf ein paar Samples.
4. Ein Commit mit Message `#32: Normalize idno/@type casing (gnd → GND)`.

Dieser Fix muss **vor P1-5** laufen, sonst schlägt das Enum-Enforcement bei Bestandsdateien zu.

---

## P1 — Enforcement-Lücken im Schema

Die Schemas sind strukturell solide, aber einige Werte sind als freier Text modelliert, obwohl die Spec ein Enum vorgibt. Das hat die P0-4-Drift erst möglich gemacht.

### P1-5 · `mhdbdb.rnc` — `<idno @type>` ohne Enum

> **Status:** ✅ done (2026-05-07). Re-Audit nach WZB-Merge zeigte, dass der Plan zwei Lücken hatte: (a) `shelfmark` als 8. Wert, eingeschleppt durch WZB.tei.xml — gelöst per „Daten vor Schema" (`<idno type="shelfmark">` aus WZB entfernt, Info steht via `corresp` schon in `works.xml`); (b) `person/idno` als 3. Position für `<idno>` (1.155 Vorkommen für GND/Wikidata-IDs auf Personen, der Plan hatte nur `msIdentifier` und `monogr` erfasst).
>
> **Implementiert: 3 kontextspezifische Enum-Patterns**
> - `idno.type.msIdentifier` = `"sigle" | "handschriftencensus" | "GND" | "wikidata" | "mwb-sigle"`
> - `idno.type.monogr` = `"callNumber" | "ISBN"`
> - `idno.type.person` = `"GND" | "wikidata"`
>
> Die zwei Stellen `analytic/idno` und `bibl/idno` (Provenance-Block) blieben `text`, weil dort keine Bestandsdaten existieren.
>
> Validation: 667/667 Korpus-Dateien grün gegen Stage 2, Stage-1-Baseline unverändert bei 30/667.

**Ursprünglicher Plan (veraltet, zur Referenz):**

**Vorkommen im Schema:** `mhdbdb.rnc` Z.103, 124, 146, 162, 210 — überall `attribute type { text }`.

**Fix:** Neues benanntes Pattern einführen und überall referenzieren.

```rnc
# oberhalb der ersten Verwendung
idno.type = attribute type { "GND" | "wikidata" | "handschriftencensus" | "sigle" | "mwb-sigle" }
```

Dann in jedem `<idno>`-Element `attribute type { text }` → `idno.type` ersetzen. Nach dem Edit:

```bash
python -m rnc2rng schema/mhdbdb.rnc schema/mhdbdb.rng
```

### P1-6 · `mhdbdb.rnc:203` — `persName/@type` ohne Enum

Asymmetrie: Authority-Schema erzwingt `"preferred" | "alternative"`, Korpus-Schema nicht.

**Fix:** `mhdbdb.rnc:203` — `attribute type { text }?` → `attribute type { "preferred" | "alternative" }?`.

Verifikation gegen Korpus:

```bash
Grep: grep -rh 'persName type="[^"]*"' tei/ | sort -u
```

Wenn andere Werte erscheinen, entweder Enum erweitern oder Daten migrieren.

### P1-7 · `mhdbdb-authority.rnc:76, 87` — `lexicon.entry` zu lax

Spec (`TEI-MODEL-AUTH-FILES.md §3.1`) markiert `<gramGrp>` und `<sense>` als Pflicht. Schema macht beide optional:

```rnc
element gramGrp { ... }?,          # Z.76
element sense { ... }*             # Z.87 — erlaubt 0 senses
```

**Fix:**

```rnc
element gramGrp { ... },           # ohne ?
element sense { ... }+             # + statt *
```

Verifikation: `lexicon.xml` hat 43.750 Einträge. Wenn der Schema-Edit etwas bricht, dann weil es leere Einträge gibt. Vor dem Edit:

```bash
python -c "
from lxml import etree
t = etree.parse('authority-files/lexicon.xml')
ns = {'t':'http://www.tei-c.org/ns/1.0'}
empty = t.xpath('//t:entry[not(t:sense)]', namespaces=ns)
print(f'entries without sense: {len(empty)}')
"
```

Falls Treffer: entweder Daten bereinigen oder Schema bei `*` belassen und in die Doku aufnehmen.

### P1-8 · `mhdbdb-authority.rnc:177–185` — `works.biblStruct/monogr/title` kann fehlen

Das aktuelle Pattern:

```rnc
element monogr {
    (element title {...}
     | element author {...}
     | element editor {...}
     | element idno {...}
     | element edition {text})*,
    element imprint {...}?
}
```

Durch die `*`-Quantifizierung ist `title` nicht Pflicht — ein `monogr` ohne Titel ist valid. TEI P5 verlangt aber `title+`.

**Fix:** `title` aus der Choice herausziehen und separat als Pflicht modellieren:

```rnc
element monogr {
    element title { attribute level { text }?, text }+,
    (element author { element name { text } }
     | element editor { ... }
     | element idno { attribute type { text }, text }
     | element edition { text })*,
    element imprint {...}?
}
```

Gleiche Korrektur auch für `biblStruct` im Korpus-Schema prüfen (`mhdbdb.rnc:126–141`) — die dortige Version hat `title+` drinnen, aber `idno/editor/edition` nach dem `title+` via `*`. Ist ok, aber Reihenfolge doppelchecken.

### P1-9 · `mhdbdb-authority.rnc:151` — `works.bibl/idno/@type` ohne Enum

Analog P1-5, für die Authority-Seite. Die Authority-`persons.xml` hat bereits ein Enum für idno — `works.xml` fehlt es.

**Fix:** Eigenes Pattern oder Inline:

```rnc
attribute type { "sigle" | "handschriftencensus" | "GND" | "wikidata" }
```

Verifikation:

```bash
Grep: grep -oh 'idno type="[^"]*"' authority-files/works.xml | sort -u
```

### P1-10 · `mhdbdb.rnc:102` — `msIdentifier/@corresp` optional, Spec Pflicht

Spec (`TEI-MODEL.md §2.1`) markiert den Verweis auf `works.xml#work_N` als obligatorisch, Schema hat `?`.

**Fix:** `mhdbdb.rnc:102` — `attribute corresp { text }?` → `attribute corresp { text }`.

Verifikation:

```bash
python -c "
from lxml import etree
import glob
count_missing = 0
for f in glob.glob('tei/*.tei.xml'):
    t = etree.parse(f)
    ns = {'t':'http://www.tei-c.org/ns/1.0'}
    mi = t.find('.//t:msIdentifier', ns)
    if mi is None or 'corresp' not in mi.attrib:
        count_missing += 1
        print(f)
print(f'missing: {count_missing}')
"
```

Wenn Treffer > 0: Daten fixen bevor Schema verschärft wird.

---

## P2 — Struktur, Regression, Toolchain

### P2-11 · Taxonomie-Body ↔ `encodingDesc`-Kopplung fehlt

`mhdbdb-authority.rnc:54–59`:

```rnc
authority.body =
    lexicon.div
    | variants.div
    | listPerson
    | listBibl
    | element p { text }       # taxonomy files: placeholder
```

Das `<p>`-Placeholder ist valid, auch wenn der Header keinen `<encodingDesc>/<classDecl>/<taxonomy>` hat. Die Spec sagt aber: Taxonomie-Dateien müssen die Taxonomie-Daten im `encodingDesc` haben.

**Drei Optionen:**

1. **Zwei separate Start-Symbole** — `corpus.start` und `taxonomy.start`, per `include` in zwei Datei-Schemas aufgeteilt. Bricht die „ein Schema für alle Authority-Files"-Idee.
2. **Schematron-Layer** — `<sch:pattern>` mit Assertion: wenn `body/p` (Placeholder), dann `encodingDesc/classDecl/taxonomy` Pflicht. Minimalster Schematron-Einsatz.
3. **Akzeptieren & dokumentieren** — im Schema-Kommentar klar machen, dass Stage 2 hier absichtlich schwach ist.

**Empfehlung:** Option 3 jetzt, Option 2 zusammen mit den anderen Schematron-Kandidaten (P3), falls es jemals ein Schematron gibt.

### P2-12 · `scripts/audit/validate-corpus.py` ist veraltet

Der Header-Kommentar sagt:

> Full RELAX NG validation (tei_all.rng + mhdbdb.rng) requires jing (Java) or trang to convert RNC→RNG. This script performs the structural validation that matters most for MHDBDB conformance.

Das stimmt seit nie — `lxml.etree.RelaxNG` kann RNG nativ in Python validieren. Die Python-Checks im Script sind redundant zu dem, was `mhdbdb.rng` heute tut.

**Fix:** Script ersetzen durch ~40 Zeilen, die jede Datei gegen beide Stages validieren. Skeleton:

```python
from lxml import etree
import glob, sys

tei_all  = etree.RelaxNG(etree.parse('schema/tei_all.rng'))
mhdbdb   = etree.RelaxNG(etree.parse('schema/mhdbdb.rng'))
auth     = etree.RelaxNG(etree.parse('schema/mhdbdb-authority.rng'))

fails = []
for f in sorted(glob.glob('tei/*.tei.xml')):
    t = etree.parse(f)
    if not tei_all.validate(t): fails.append((f, 'tei_all', tei_all.error_log))
    if not mhdbdb.validate(t):  fails.append((f, 'mhdbdb',  mhdbdb.error_log))

for f in sorted(glob.glob('authority-files/*.xml')):
    t = etree.parse(f)
    if not tei_all.validate(t): fails.append((f, 'tei_all', tei_all.error_log))
    if not auth.validate(t):    fails.append((f, 'mhdbdb-auth', auth.error_log))

for f, stage, err in fails:
    print(f'FAIL {stage}: {f}')
    print(f'  {str(err)[:300]}')
sys.exit(1 if fails else 0)
```

Alter Inhalt kann per `git mv` nach `scripts/_archived/` oder direkt gelöscht werden (Git-Historie reicht).

### P2-13 · CI-Regression für Schemas fehlt

Aktuell nur `.github/workflows/claude-code-review.yml` (automatische PR-Reviews). Kein Schema-Check.

**Fix:** Neuer Workflow `schema-validation.yml`, der bei PRs die `schema/**`, `tei/**`, `authority-files/**` berühren, folgendes tut:

```yaml
name: Schema Validation
on:
  pull_request:
    paths:
      - 'schema/**'
      - 'tei/**'
      - 'authority-files/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.13' }
      - run: pip install lxml rnc2rng
      - run: |
          curl -sL https://tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng -o schema/tei_all.rng
          python -m rnc2rng schema/mhdbdb.rnc schema/mhdbdb.rng
          python -m rnc2rng schema/mhdbdb-authority.rnc schema/mhdbdb-authority.rng
          python scripts/audit/validate-corpus.py   # Variante aus P2-12
```

Das schützt gegen Schema-Drift (RNC bearbeitet, RNG vergessen) und gegen neue invalide Daten.

### P2-14 · RNC→RNG-Sync per pre-commit Hook

Die `.rng`-Dateien sind generiert, können aber versehentlich aus dem Sync laufen. Zwei Optionen:

1. **Pre-commit Hook** (lokal, nicht enforced): `.git/hooks/pre-commit` regeneriert `.rng` wenn `.rnc` geändert wurde.
2. **CI-Check** (Teil von P2-13): nach `rnc2rng` ein `git diff --exit-code schema/*.rng` laufen lassen — wenn sich was ändert, ist `.rng` nicht committet → CI failed.

**Empfehlung:** CI-Check (Option 2), da enforced. Pre-commit Hook ist optional nice-to-have.

### P2-15 · `<?xml-model?>`-PIs: Editor-Live-Validation für alle TEI-Files

**Zweck:** Die `<?xml-model?>`-Processing-Instruction teilt XML-Editoren (oXygen, VS Code Scholarly XML, Emacs nxml-mode etc.) mit, welches Schema beim Editieren für Live-Validation und Code-Completion angewendet werden soll. Zwei PIs pro File (unser Custom-Schema zuerst, `tei_all.rng` zweitens) geben Editoren beide Validierungs-Stages on-the-fly — tippt jemand `<orgName ref="...">` in `persons.xml`, sieht er sofort einen roten Unterstrich statt erst beim nächsten `jing`-Lauf.

**Ist-Zustand (verifiziert 2026-04-15):**

| Bereich | Files | xml-model-PIs? |
|---------|------:|----------------|
| `authority-files/*.xml` | 8 | ✅ beide PIs (unser Schema + tei_all) |
| `schema/examples/*.xml` | 2 (authority-contributors, corpus.example) | ✅ beide PIs |
| `tei/*.tei.xml` | **666** | ❌ **keine einzige xml-model PI** |

Die Authority-Seite wurde im selben Commit erledigt, der `contributors.org/idno/@type` um `"URL"` erweitert und den `<orgName ref="...">` → `<idno type="URL">`-Fix gemacht hat. Die Korpus-Seite fehlt noch.

**Scope:** Alle 666 Korpus-Dateien bekommen zwei neue Zeilen zwischen der `<?xml?>`-Declaration und dem `<TEI>`-Root:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<?xml-model href="../schema/mhdbdb.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<?xml-model href="https://tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="ABG">
```

**Wichtig:** Für Korpus-Files ist der relative Pfad `../schema/mhdbdb.rng` (Korpus-Schema), **nicht** `mhdbdb-authority.rng`.

**Migrationsscript** (einmalig, nach Lauf löschen — analog zu `scripts/temp/normalize-idno-gnd-casing.py` aus P0-4):

```python
# scripts/temp/add-xml-model-pi.py
from pathlib import Path

PI1 = '<?xml-model href="../schema/mhdbdb.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>'
PI2 = '<?xml-model href="https://tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng"?>'

files = sorted(Path('tei').glob('*.tei.xml'))
skipped = changed = 0
for f in files:
    text = f.read_text(encoding='utf-8')
    if 'xml-model' in text:
        skipped += 1
        continue
    # Insert the two PIs directly after the <?xml?> declaration line
    lines = text.splitlines(keepends=True)
    new_text = lines[0] + PI1 + '\n' + PI2 + '\n' + ''.join(lines[1:])
    f.write_text(new_text, encoding='utf-8')
    changed += 1
print(f'{changed} files changed, {skipped} skipped')
```

**Idempotenz:** Script skippt Files, die bereits eine `xml-model` PI haben. Zweiter Lauf ist no-op.

**Verifikation nach dem Lauf:**

```bash
# 1) Exakt 2 PIs pro Datei, 666 × 2 = 1332 Treffer gesamt
grep -c 'xml-model' tei/*.tei.xml | awk -F: '{sum+=$2} END {print sum}'   # erwartet: 1332

# 2) Git-Diff-Scope: 666 files × 2 insertions, 0 deletions
git diff --stat tei/ | tail -1   # erwartet: 666 files changed, 1332 insertions(+)

# 3) Spot-Check auf 3 zufällige Files: wellformed + parsebar
for f in tei/ABG.tei.xml tei/LZT.tei.xml tei/WUT.tei.xml; do
    python -c "from lxml import etree; etree.parse('$f'); print('OK $f')"
done

# 4) Volle Zwei-Stufen-Validierung (siehe editor-attribution Commit 2 / #32-followup):
#    tei_all fails: 30 (Baseline #30), mhdbdb fails: 0
```

**Risiko:** niedrig. Rein mechanische Zeileneinfügung zwischen zwei festen Punkten (nach `<?xml?>`-Declaration, vor `<TEI>`-Root), keine Schema- oder Daten-Änderung. Voll reversibel via `git restore tei/`. Keine Wechselwirkung mit laufenden editor-attribution-Migrationen, weil die Header-Mutation dort erst unterhalb von `<TEI>/<teiHeader>` passiert.

**Aufwand:** ~20 min (Script schreiben + Sample-Test auf 5 Files + echter Lauf + 4-stufige Verifikation).

**Abhängigkeit:** Keine. Kann parallel zu oder nach den P1-Schema-Enforcement-Items laufen. Sollte aber NACH Commit 4 der editor-attribution-Migration laufen (damit der editor-attribution-Diff sauber bleibt und nicht mit xml-model-PI-Inserts vermischt wird).

---

## P3 — Schematron-Territorium (nicht jetzt)

Diese Constraints kann RELAX NG nicht ausdrücken. Entweder Schematron oder separater Python-Linter als Stage 3. **Nicht jetzt umsetzen**, sondern als eigenes Ticket eröffnen, wenn sich ein konkreter Bedarf zeigt.

| # | Constraint | Implementierungsweg |
|---|-----------|---------------------|
| P3-15 | `xml:id` Präfix-Regex pro Datei (`lemma_\d+`, `work_\d+`, `person_(\d+\|anonym)`, `genre_[0-9a-f]{8}`, `concept_\d{8}`, `name_\d{8}`, `type_\d+`) | Schematron `<sch:assert test="matches(@xml:id, '^lemma_\d+$')"/>` oder Python |
| P3-16 | Cross-File-Referenzintegrität: jedes `@lemmaRef`, `@ref`, `@corresp`, `ptr/@target` zeigt auf eine existierende ID | Python-Linter — braucht globalen ID-Index aller Authority-Files, dann Scan über alle Korpus-Files. Gleiche Logik wie `build-corpus-index.py` schon implizit hat. |
| P3-17 | `<note type="works">` CSV-Format (`work_N` oder `work_N,work_M`) | Schematron `<sch:assert test="matches(., '^work_\d+(,work_\d+)*$')"/>` |
| P3-18 | `<author ref="#person_...">` in `titleStmt` muss auf lokalen `person/@xml:id` in `particDesc` zeigen | Schematron mit `key()`-Lookup |
| P3-19 | `<change @who>` beginnt mit `#` | Regex-Assertion |

---

## Reihenfolge & Commit-Struktur

> **Hinweis:** der ursprünglich geplante 8-Commit-Flow wurde nicht 1:1 umgesetzt — die tatsächlichen Commits sind in der Status-Tabelle am Dateianfang dokumentiert. Wer die echte Historie sehen will, nutzt `git log --grep '#32-followup'`. Der Plan hier bleibt als Referenz dafür, wie der Flow ursprünglich gedacht war.

**Ursprünglicher Plan (Stand 2026-04-14, historisch):**

```
Commit 1  #32-followup: fix TEI-MODEL.md inconsistencies (P0-1..3)
          → nur docs/TEI-MODEL.md edit, keine Code-Änderung
Commit 2  #32-followup: normalize idno/@type casing (gnd → GND)  (P0-4)
          → tei/*.tei.xml, ein Migrations-Script einmalig lauffähig
Commit 3  #32-followup: tighten idno and persName enums in corpus schema  (P1-5, P1-6)
          → schema/mhdbdb.rnc + regenerierte .rng
          → Abhängigkeit: Commit 2 muss davor landen
Commit 4  #32-followup: tighten lexicon and works constraints in authority schema  (P1-7..9)
          → schema/mhdbdb-authority.rnc + regenerierte .rng
Commit 5  #32-followup: require msIdentifier/@corresp  (P1-10)
          → schema/mhdbdb.rnc + regenerierte .rng
          → vorher Dateninventur (siehe Verifikation zu P1-10)
Commit 6  #32-followup: replace validate-corpus.py with real RelaxNG validation  (P2-12)
          → scripts/audit/validate-corpus.py neu
Commit 7  #32-followup: add schema validation CI  (P2-13, P2-14)
          → .github/workflows/schema-validation.yml neu
Commit 8  #32-followup P2-15: xml-model PIs in alle 666 Korpus-Dateien
          → tei/*.tei.xml, je 2 neue Zeilen nach <?xml?>-Declaration
          → scripts/temp/add-xml-model-pi.py einmalig, dann löschen
          → Voraussetzung: NACH editor-attribution Commit 4 (Header-Migration),
            damit die Diffs nicht vermischt werden
```

P2-11 (Taxonomie-Kopplung) und P3 separat als Einzel-Tickets, falls Zeit.

## Test-Protokoll (nach jedem Commit)

```bash
# 1) Regenerate RNG wenn RNC geändert
python -m rnc2rng schema/mhdbdb.rnc schema/mhdbdb.rng
python -m rnc2rng schema/mhdbdb-authority.rnc schema/mhdbdb-authority.rng

# 2) Examples müssen weiterhin grün bleiben
python -c "
from lxml import etree
import os
tei_all = etree.RelaxNG(etree.parse('schema/tei_all.rng'))
mhdbdb  = etree.RelaxNG(etree.parse('schema/mhdbdb.rng'))
auth    = etree.RelaxNG(etree.parse('schema/mhdbdb-authority.rng'))
for f in sorted(os.listdir('schema/examples')):
    t = etree.parse(f'schema/examples/{f}')
    s2 = mhdbdb if 'corpus' in f else auth
    assert tei_all.validate(t), f'{f} fails tei_all: {tei_all.error_log}'
    assert s2.validate(t),      f'{f} fails mhdbdb: {s2.error_log}'
print('all examples green')
"

# 3) Authority Files müssen weiterhin grün bleiben
python -c "
from lxml import etree
import os
tei_all = etree.RelaxNG(etree.parse('schema/tei_all.rng'))
auth    = etree.RelaxNG(etree.parse('schema/mhdbdb-authority.rng'))
for f in sorted(os.listdir('authority-files')):
    if not f.endswith('.xml'): continue
    t = etree.parse(f'authority-files/{f}')
    assert tei_all.validate(t), f
    assert auth.validate(t),    f
print('all authority files green')
"

# 4) Korpus-Sample (30 zufällige Dateien) — billig
python -c "
from lxml import etree
import glob, random
tei_all = etree.RelaxNG(etree.parse('schema/tei_all.rng'))
mhdbdb  = etree.RelaxNG(etree.parse('schema/mhdbdb.rng'))
random.seed(42)
files = random.sample(glob.glob('tei/*.tei.xml'), 30)
for f in files:
    t = etree.parse(f)
    ok1 = tei_all.validate(t); ok2 = mhdbdb.validate(t)
    print(f'{f}: {ok1} {ok2}')
"

# 5) Volle Korpus-Validierung — nur bei größeren Schema-Änderungen, dauert ~5-10 min
# siehe Skeleton in P2-12
```

## Aufwandsschätzung

| Bucket | Aufwand | Reversibel? |
|--------|--------:|-------------|
| P0-1..3 (Doku-Edits) | 15 min | ja |
| P0-4 (gnd→GND Migration) | 1 h (Script + Validierung) | ja (Git Revert) |
| P1-5..10 (Schema-Enforcement) | 2–3 h gesamt | ja |
| P2-12 (validate-corpus Rewrite) | 30 min | ja |
| P2-13, P2-14 (CI) | 1 h | ja |
| P2-15 (xml-model PIs für Korpus) | 20 min (Script + Lauf + Verifikation) | ja (Git Revert) |
| P2-11 (Taxonomie-Kopplung) | wenn Option 3: 5 min; Option 2: 2 h | ja |
| P3 (Schematron) | 2–4 h pro Item | n/a — separate Tickets |

**Gesamtaufwand P0+P1+P2 (ohne Schematron):** ~6 h Arbeit, verteilt auf einen Tag.

---

## Bekannte Nicht-Befunde (damit niemand nochmal sucht)

- **RNC/RNG in sync:** Timestamps identisch, Inhalte konsistent (geprüft via `git ls-files schema/`).
- **`tei_all.rng`:** liegt lokal in `schema/`, ist nicht in git, README beschreibt das als „gitignored". Kein Bug, aber `.gitignore` erwähnt es nicht explizit — wenn jemand `git add schema/tei_all.rng` macht, würde es committet werden. Optional: expliziter Eintrag in `.gitignore`.
- **`<author>` in titleStmt:** real `<author ref="#person_X">Name</author>`, Schema erlaubt das korrekt über `mixed { (element name { text })* }` (mixed content, `<name>` optional). Kein Drift.
- **`<editor>` in `monogr`:** real `<editor><forename>...</forename><surname>...</surname></editor>`, Schema passt.
- **`<change>`-Struktur:** real `<change when="..." who="#editor">Text</change>`, Schema passt.
- **Authority-Dateien Validierung heute:** alle 7 grün gegen beide Stages.
- **Examples Validierung heute:** alle 8 grün gegen beide Stages.

---

## Referenzen

- `docs/TEI-MODEL.md` — Korpus-Soll-Modell
- `docs/TEI-MODEL-AUTH-FILES.md` — Authority-Soll-Modell
- `schema/README.md` — Schema-User-Guide (prüft in §Schnellstart gegen beide Stages)
- `schema/mhdbdb.rnc` / `schema/mhdbdb-authority.rnc` — Schema-Quelldateien
- Original-Issue: [#32 TEI Model Consolidation](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/32) (geschlossen 2026-04-10, Phase F-K abgeschlossen)
