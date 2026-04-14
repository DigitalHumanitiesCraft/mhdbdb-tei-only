# 032 — Schema Follow-up Cleanup

**Status:** Open (Follow-up zu geschlossenem #32)
**Audience:** Nächste/r CC-Kollege/in
**Baseline (verifiziert 2026-04-14):**

| Check | Ergebnis |
|-------|---------|
| `schema/examples/*` gegen beide Stages | 8 / 8 grün |
| `authority-files/*.xml` gegen beide Stages | 7 / 7 grün |
| `schema/mhdbdb.rnc` ↔ `.rng` Sync | in sync (beide 2026-04-10) |
| `schema/mhdbdb-authority.rnc` ↔ `.rng` Sync | in sync |
| Korpus (666 Dateien) gegen beide Stages | nicht in dieser Session gemessen (sollte im Zuge der Arbeit passieren, `#32`-Roadmap markiert 682 Dateien als valid) |

**Scope:** Rein additive Schärfungen nach Abschluss der großen Migration. Keine Architekturänderungen. Alle Punkte sind einzeln reversibel.

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

Abhängigkeit: **P0-4 muss vorher laufen**, sonst failen 30+ Korpusdateien an Stage 2.

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

Aktuell nur `.github/workflows/claude-code-review.yml` und `claude.yml`. Kein Schema-Check.

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

## Reihenfolge & Commit-Struktur (Vorschlag)

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
| P2-11 (Taxonomie-Kopplung) | wenn Option 3: 5 min; Option 2: 2 h | ja |
| P3 (Schematron) | 2–4 h pro Item | n/a — separate Tickets |

**Gesamtaufwand P0+P1+P2 (ohne Schematron):** ~5–6 h Arbeit, verteilt auf einen Tag.

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
