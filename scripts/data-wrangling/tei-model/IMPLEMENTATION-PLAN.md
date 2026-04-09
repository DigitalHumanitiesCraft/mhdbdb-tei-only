# TEI Model Implementation Plan

## Context

Das Soll-Modell (TEI-MODEL.md) steht. Alle Entscheidungen sind getroffen, das Korpus-Audit ist abgeschlossen (666 Dateien, 12.7M Elemente). Jetzt geht es an die Umsetzung: die 666 TEI-Dateien vom IST-Zustand zum SOLL-Zustand transformieren und ein RELAX NG Schema schreiben, das den SOLL-Zustand validiert.

Branch: `feature/tei-model-32`
Alle Scripts: `scripts/data-wrangling/tei-model/`

---

## Phase A: Sichere Migrationen (kein Code-Impact)

Aenderungen die NUR XML betreffen — kein JS, kein Python-Build-Script muss angepasst werden. Koennen sofort laufen, kein Risiko fuer die Laufzeitumgebung.

### A1. div/@type Renames

**Script:** `migrate-div-types.py`

| IST | SOLL | Dateien | Count |
|-----|------|---------|-------|
| `deed` | `number` | HZU, HZU2 | 300 |
| `sermon` | `number` | ADP, ECK + 10 weitere | 113 |
| `sigil` | `number` | BOP | 9 |
| `paragraph` | `number` | BDK | 76 |
| `part` | `section` | DL2, EHB + weitere | 176 |
| `subsection` | `section` | KVM | 3 |
| `§` | `section` | KVM | 7 |
| `volume` | `section` | FLG, FLG1 | 7 |
| `stanza` (auf div) | → Element wird `<lg type="stanza">` | LZT | 1,122 |

LZT-Sonderfall: `<div type="stanza">` muss zu `<lg type="stanza">` werden — das ist ein Element-Wechsel, nicht nur Attribut-Rename. Braucht eigene Logik.

**Aufwand:** ~50 Zeilen Python. Laufzeit: Sekunden.

### A2. monogr Element-Reihenfolge fixen

**Script:** `fix-monogr-order.py`

In `<monogr>`: `<author>` muss vor `<title>` stehen, `<idno>` nach `<editor>`. Betrifft Dateien wo `<author>` nach `<title>` kommt (z.B. WUT).

**Aufwand:** ~30 Zeilen Python. Erkennung + Umsortierung.

### A3. suppplied Tippfehler

**Script:** `fix-typos.py` (oder inline in A1)

1 Vorkommen von `<suppplied>` → `<supplied>`.

### A4. note type="date" Dekodierung (HZU/HZU2)

**Script:** `decode-hzu-dates.py`

277 `type="date"` notes (HZU 36 + HZU2 241): `<note type="date" n="224"/>` → `<note type="date" n="24. Februar"/>`. Dekodierungslogik: letzte 2 Stellen = Tag, Rest = Monat. Die 119 `type="year"` notes (HZU 19 + HZU2 100) bleiben unveraendert — enthalten bereits Klartext-Jahreszahlen (`n="1293"`).

### A5. Header-Anreicherung: langUsage

**Script:** `enrich-headers.py`

Allen 666 Dateien `<langUsage>` hinzufuegen (fehlt aktuell komplett). Standard: `<language ident="gmh">`. Dateien mit lateinischen Einschueben (identifizierbar via `xml:lang="la"` auf `<w>`) zusaetzlich `<language ident="la">`.

---

## Phase B: Attribut-Migrationen (minimaler Code-Impact)

### B1. @meaningRef → @ana

**Script:** `migrate-meaningref.py`

- 5,852,223 Vorkommen in 666 Dateien
- Reines Attribut-Rename: Werte bleiben identisch
- **JS-Anpassung noetig (2 kritische Stellen):**
  - `tei-manager.js:208` — `querySelectorAll('[meaningRef]')` → `'[ana]'`
  - `tei-manager.js:210` — `getAttribute('meaningRef')` → `'ana'`
  - Optional: 6 weitere Stellen (Property-Name im internen Datenmodell)

### B2. @wordRef → @corresp

**Script:** `migrate-wordref.py`

- 7,406,166 Vorkommen in 666 Dateien
- Attribut-Rename PLUS URI-Transformation:
  - IST: `wordRef="lexicon.xml#lemma_2598_sense_77615_type_8717"`
  - SOLL: `corresp="variants.xml#type_8717"`
- Regex: `type_(\d+)` aus der synthetischen URI extrahieren → `variants.xml#type_{id}`
- **Kein JS-Impact** (kein Code liest @wordRef)

### B3. @lemma ergaenzen (optional, niedrige Prio)

**Script:** `add-lemma-attr.py`

- Fuer jedes `<w>` mit `@lemmaRef`: Lookup in lexicon.xml → `@lemma` setzen
- 7.4M Lookups — Performance-kritisch, braucht lexicon.xml Index im RAM
- Kein Code-Impact (rein additiv)
- **Kann spaeter gemacht werden**

---

## Phase C: Element-Migrationen (JS-Impact)

### C1. <seg type="pc"> → <pc join="left">

**Script:** `migrate-seg-to-pc.py`

- 1,370,191 Vorkommen
- `<seg xml:id="..." type="pc">X</seg>` → `<pc xml:id="..." join="...">X</pc>`
- xml:id beibehalten wenn vorhanden
- `@join` abhaengig vom Inhalt:
  - `join="left"` fuer: `)`, `.`, `,`, `;`, `:`, `!`, `?`, `&gt;`, `»`
  - `join="right"` fuer: `(`, `&lt;`, `«`
  - Default `join="left"` (Grossteil der Interpunktion)
- **JS-Anpassung:** `tei-text-reader.js` muss `<pc>` als Inline-Element rendern

### C2. <l> → <lb/> in 18 Prosa-Texten

**Script:** `migrate-l-to-lb.py`

- 18 spezifische Dateien (Liste in TEI-MODEL.md Sec. 8.1)
- `<l n="X">content</l>` → `<lb n="X"/>content`
- Container-Element wird Milestone-Element — Kinder bleiben, werden zum Parent verschoben
- **JS-Anpassung:**
  - `tei-text-reader.js:531` — `<l>` Rendering
  - `tei-manager.js:195` — `querySelectorAll('l')` Extraktion

---

## Phase D: Header-Anreicherung aus TEXT_DATA_TABLE.xlsx (#67)

### D1. Abbreviatur-/Ligatur-Dokumentation

**Script:** `enrich-headers-normalization.py`

- 124 Texte mit DESCRIPTION-Eintraegen zu Abbreviaturen/Ligaturen
- XLSX parsen, Muster erkennen, `<normalization>`-Block in teiHeader einfuegen
- Abhaengigkeit: `scripts/data-wrangling/tei-model/TEXT_DATA_TABLE.xlsx` (bereits im Repo)

---

## Phase E: RELAX NG Schema

### E1. Schema schreiben

**Dateien:**
- `schema/mhdbdb.rnc` — RELAX NG Compact Syntax (Source of Truth, hand-editiert)
- `schema/mhdbdb.rng` — RELAX NG XML Syntax (generiert via `trang`, fuer lxml)

**Build:** `trang schema/mhdbdb.rnc schema/mhdbdb.rng` (beide committen, RNC ist Source)

**Abhaengigkeit:** Java fuer `trang`/`jing`. Alternativ: `pip install jingtrang` (Python-Wrapper).

Basiert auf:
- Audit-Daten (tei-audit.json): welche Elemente/Attribute tatsaechlich vorkommen
- TEI-MODEL.md: welche Werte erlaubt sind (SOLL, nicht IST)
- TEI-MODEL-EXAMPLE.xml: Referenz-Dokument

**Ansatz:** Minimales Custom-Schema from scratch (nicht tei_all inkludieren — 1.1 MB, zu komplex). Modelliert nur was der MHDBDB-Korpus nach Migration nutzt. tei_all-Konformitaet wird separat geprueft (Stufe 1).

**Kein ODD:** Die ODD-Toolchain (TEI Stylesheets + Roma) ist XSLT 2.0-abhaengig, hat 60-80 offene Issues, Roma-Webinterface instabil. TEI-Konformanzkriterium 5 ("documented via ODD or analogous documentation") wird durch `docs/TEI-MODEL.md` + `schema/mhdbdb.rnc` gemeinsam erfuellt.

### E2. Zwei-Stufen-Validierung

**Script:** `validate-corpus.py`

| Stufe | Schema | Prueft | Tool |
|-------|--------|--------|------|
| 1 | `tei_all.rng` (TEI P5 4.11.0) | TEI-Konformitaet (keine illegalen Attribute/Elemente) | lxml / jing |
| 2 | `mhdbdb.rnc` | MHDBDB-Konformitaet (erlaubte div/@type, Pflicht-Attribute, Struktur) | jing |

Stufe 2 ist strenger als Stufe 1 (Subset). Ein Dokument das Stufe 2 besteht, besteht automatisch Stufe 1.

Alle 675 Dateien (666 base + 9 disamb) gegen beide Schemas validieren.

---

## Reihenfolge und Abhaengigkeiten

```
Phase A (sicher, kein Code-Impact)
  A1 div/@type renames
  A2 monogr order fix
  A3 suppplied typo
  A4 HZU date decode
  A5 langUsage
     ↓
Phase B (Attribut-Migration, minimaler JS-Impact)
  B1 @meaningRef → @ana  ← braucht JS-Fix in tei-manager.js
  B2 @wordRef → @corresp
     ↓
Phase C (Element-Migration, JS-Impact)
  C1 <seg> → <pc>  ← braucht JS-Fix in tei-text-reader.js
  C2 <l> → <lb/>   ← braucht JS-Fix in tei-text-reader.js + tei-manager.js
     ↓
Phase D (Header-Anreicherung, kein Code-Impact)
  D1 Abbreviaturen aus XLSX
     ↓
Phase E (Schema)
  E1 RELAX NG schreiben
  E2 Korpus validieren
```

Phase A-D koennen theoretisch als ein grosses Transformationsscript laufen. Empfehlung: Getrennte Scripts pro Phase fuer Nachvollziehbarkeit und separate Commits.

**Scope:** Alle Scripts laufen auf Base-Dateien (`*.tei.xml`) UND `.disamb.tei.xml` (9 Dateien). Die Disamb-Dateien haben dieselben Attribute und Strukturprobleme.

---

## Kritische Dateien

### Neue Scripts (zu erstellen)
- `scripts/data-wrangling/tei-model/migrate-div-types.py`
- `scripts/data-wrangling/tei-model/fix-monogr-order.py`
- `scripts/data-wrangling/tei-model/decode-hzu-dates.py`
- `scripts/data-wrangling/tei-model/enrich-headers.py`
- `scripts/data-wrangling/tei-model/migrate-meaningref.py`
- `scripts/data-wrangling/tei-model/migrate-wordref.py`
- `scripts/data-wrangling/tei-model/migrate-seg-to-pc.py`
- `scripts/data-wrangling/tei-model/migrate-l-to-lb.py`
- `scripts/data-wrangling/tei-model/enrich-headers-normalization.py`
- `schema/mhdbdb.rnc`

### Bestehende Dateien (zu aendern)
- `tei/*.tei.xml` — alle 666 Base-Dateien (XML-Transformationen)
- `playground/js/data/tei-manager.js:208,210` — @meaningRef → @ana (Phase B1)
- `assets/js/rendering/tei-text-reader.js:531` — <pc> + <lb/> Rendering (Phase C)
- `playground/js/data/tei-manager.js:195` — <l> Extraktion (Phase C2)

### Referenz-Dateien (read-only)
- `docs/TEI-MODEL.md` — Soll-Modell (Quelle der Wahrheit)
- `scripts/data-wrangling/tei-model/TEI-MODEL-EXAMPLE.xml` — Referenz-Beispiel
- `scripts/data-wrangling/tei-model/tei-audit.json` — Audit-Daten
- `scripts/data-wrangling/tei-model/TEXT_DATA_TABLE.xlsx` — Metadaten-Quelle
- `authority-files/lexicon.xml` — fuer @lemma Lookup (Phase B3)
- `authority-files/variants.xml` — fuer @wordRef URI-Validierung (Phase B2)

---

## Verifikation

### Nach jeder Phase:
1. `python -c "from lxml import etree; etree.parse('tei/ABG.tei.xml')"` — Well-formedness aller Dateien
2. `npm test` — 121/121 Playwright-Tests muessen passen
3. `npm run serve` + Stichprobe im Browser — Rendering korrekt?
4. Audit-Script erneut laufen → Diff zum vorherigen Audit = nur erwartete Aenderungen

### Nach Phase B1 (@meaningRef → @ana):
- `grep -r "meaningRef" playground/js/` → 0 Treffer (JS migriert)
- `grep -rl "meaningRef" tei/` → 0 Treffer (XML migriert)

### Nach Phase E (Schema):
- `jing schema/mhdbdb.rnc tei/ABG.tei.xml` → valid
- Stichprobe: 10 diverse Dateien validieren
- TEI-MODEL-EXAMPLE.xml gegen mhdbdb.rnc validieren

### Gesamt:
- tei_all.rng Validierung: 0 Fehler (nach Phase B)
- Alle Position-Counting-Contract-Tests bestehen (CONTRACTS.MD Sec. B)
- Index-Rebuild: `python scripts/build-corpus-index.py` → keine Aenderung am Output
