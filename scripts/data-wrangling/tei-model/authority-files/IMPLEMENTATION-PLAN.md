# Authority Files — Implementation Plan

## Context

Das Soll-Modell (`docs/TEI-MODEL-AUTH-FILES.md`) steht. Alle 7 Authority Files sind bereits tei_all-konform (Session 2026-04-09). Jetzt folgt die semantische Bereinigung: Denormalisierung entfernen, Cross-Referencing vereinheitlichen, Datenqualitaet verbessern.

Branch: `feature/tei-model-32`
Scripts: `scripts/data-wrangling/tei-model/authority-files/`

---

## Phase F: Audit

### F1. Authority Files Audit

**Script:** `audit-authority-files.py`

Inventarisiert den IST-Zustand aller 7 Authority Files:
- Element-/Attribut-Inventar pro Datei
- Cross-Referenz-Inventar (welche Datei verweist wohin, wie viele)
- Referentielle Integritaet (verwaiste Referenzen finden)
- ID-Format-Analyse (numerisch vs UUID vs hierarchisch)
- Denormalisierte Daten identifizieren (Label-Text in `<ref>`, bidirektionale Links)

**Output:** `authority-audit.json` + `AUTHORITY-AUDIT-REPORT.md` (beides in `scripts/data-wrangling/tei-model/authority-files/`)

---

## Phase G: works.xml Normalisierung

### G1. Genre-Refs entlabeln

**Script:** `normalize-work-genres.py`

IST: 3,422 `<ref target="genres.xml#..." xml:lang="...">Label</ref>` (inkl. Parent-Refs)
SOLL: 1 `<ptr target="genres.xml#..."/>` pro einzigartiger Genre-ID (229 Werke haben 2-5 Genres → mehrere `<ptr>`)

Logik:
1. Sammle alle `<ref target="genres.xml#...">` pro `<bibl>`
2. Extrahiere einzigartige Genre-IDs aus direkten Refs (nicht `type="parent"`)
3. **Sonderfall:** 2 Werke (work_560, work_197) haben NUR Parent-Refs — dort die Parent-Genre-ID als direkte Zuordnung uebernehmen
4. Entferne alle Genre-`<ref>` Elemente
5. Fuer jede einzigartige Genre-ID: erzeuge `<ptr target="genres.xml#..."/>`

**Aufwand:** ~40 Zeilen Python.

### G2. Externe IDs unwrappen

**Script:** `unwrap-work-identifiers.py`

IST: `<note type="identifiers"><idno type="GND">...</idno>...</note>` (368 notes)
SOLL: `<idno type="GND">...</idno>` direkt als Kind von `<bibl>`

Logik:
1. Fuer jede `<note type="identifiers">`: Kinder (`<idno>`) nach oben verschieben
2. Position: nach `<idno type="sigle">`, vor `<ptr>` (Genre-Zeiger)
3. `<note>` Wrapper entfernen
4. GND Casing: `type="gnd"` → `type="GND"`

**Abhaengigkeit:** G1 muss ZUERST laufen (Genre-`<ref>` → `<ptr>`, sonst `<idno>`-Position nicht tei_all-valid).

**Aufwand:** ~30 Zeilen Python.

### G3. Bibl-Kinder-Reihenfolge validieren

Nach G1+G2 die SOLL-Reihenfolge in `<bibl>` sicherstellen:
`title* → idno* → ptr* → author* → relatedItem*`

Kein separates Script noetig — in G2 integrieren.

---

## Phase H: persons.xml Bereinigung

### H1. Works-Links entfernen

**Script:** `remove-person-works-links.py`

IST: 209 `<listBibl>` mit `<bibl corresp="works.xml#..."/>` in `<person>` Elementen
SOLL: Entfernt. Build-Script leitet die Beziehung aus works.xml ab.

**Aufwand:** ~15 Zeilen Python.

### H2. UUID-IDs migrieren

**Script:** `migrate-person-uuids.py`

4 Personen mit UUID-Format → naechste freie numerische ID (person_1768 bis person_1771).

| UUID-Person | Name | Referenziert von |
|-------------|------|-----------------|
| `person_778d109...` | Karl IV. | nirgends |
| `person_b30959e...` | Ruedeger von Hunchofen | nirgends |
| `person_c5ec3a1...` | Ezzo | nirgends |
| `person_0515479...` | Albertanus von Brescia | 1 Werk in works.xml |

3 der 4 haben keinen Cascade — nur ID-Rename in persons.xml. Nur Albertanus hat 1 Werk-Ref in works.xml.

Logik:
1. Hoechste existierende numerische person-ID finden (aktuell: person_1767)
2. Fuer jede UUID-Person: neue ID = max + 1
3. In persons.xml: `xml:id` aendern
4. In works.xml: `<author ref="persons.xml#person_UUID">` aktualisieren (nur Albertanus: 1 Ref)
5. In tei/*.tei.xml: `<author ref="#person_UUID">` aktualisieren (nur LUU.tei.xml: 3 Referenzen)

**Aufwand:** ~50 Zeilen Python.

---

## Phase I: Datenqualitaet

### I1. Verwaiste Referenzen bereinigen

**Script:** `fix-orphan-refs.py`

| Problem | Datei | Anzahl | Aktion |
|---------|-------|--------|--------|
| variants → nicht-existente Lemmata | variants.xml | 154 | Eintraege entfernen |
| lexicon → nicht-existente Konzepte | lexicon.xml | 61 | `<ptr>` Elemente entfernen |
| lexicon → nicht-existente Lemmata (Etymologie) | lexicon.xml | 10 | `<seg corresp>` Elemente entfernen |
| works → nicht-existente Person | works.xml | 1 | `person_schweizer_anonymus` → Entscheidung noetig (Person anlegen oder Ref auf `person_anonym` setzen) |

**Aufwand:** ~40 Zeilen Python (plus manuelle Entscheidung fuer person_schweizer_anonymus).

### I2. work_6 Bibliographie nachpflegen

Manuell: `work_6` (Frauendienst, Ulrich von Liechtenstein) hat keine `<biblStruct>`. Muss aus Zotero oder manuell ergaenzt werden.

**Abhaengigkeit:** Menschliche Entscheidung (Katharina/Chris).

---

## Phase J: Build-Scripts anpassen

### J1. `build-authority-index.py` aktualisieren

| Aenderung | Betrifft | Grund |
|-----------|----------|-------|
| Genre-Reader: komplett umbauen | `parse_works()` | G1: `<ref>` mit Label-Text wird `<ptr/>` (leer). Genre-Text muss jetzt aus genres.xml per ID-Lookup aufgeloest werden. Dazu: zuerst genres.xml laden, `genre_id → term_de` Mapping aufbauen, dann `<ptr @target>` auflösen. |
| Persons-Reader: `<listBibl>` Reader durch works.xml-Ableitung ersetzen | `parse_persons()` | H1: `<listBibl>` wird entfernt |

### J2. `enhance_works_with_zotero.py` aktualisieren

Neue `<biblStruct>` Elemente muessen in `<relatedItem>` gewrapped werden statt direkt in `<bibl>`.

---

## Phase K: Schema aktualisieren + Validierung

### K1. `mhdbdb-authority.rnc` aktualisieren

Schema an SOLL-Modell anpassen (Genre-Refs als `<ptr>`, keine `<note type="identifiers">`, keine `<listBibl>` in persons, etc.)

### K2. Alle 7 Dateien validieren

Zwei-Stufen-Validierung:
1. `tei_all.rng` — TEI P5 Konformitaet
2. `mhdbdb-authority.rnc` — MHDBDB-spezifische Constraints

---

## Reihenfolge und Abhaengigkeiten

```
Phase F: Audit (IST-Zustand erfassen)
  F1 audit-authority-files.py
     ↓
Phase G: works.xml (groesster Impact)
  G1 Genre-Refs entlabeln       ← ZUERST
  G2 Externe IDs unwrappen       ← NACH G1 (Content Model)
     ↓
Phase H: persons.xml
  H1 Works-Links entfernen
  H2 UUID-IDs migrieren          ← Cascade: works.xml + tei/*.tei.xml
     ↓
Phase I: Datenqualitaet
  I1 Verwaiste Referenzen
  I2 work_6 Bibliographie        ← braucht menschliche Entscheidung
     ↓
Phase J: Build-Scripts
  J1 build-authority-index.py
  J2 enhance_works_with_zotero.py
     ↓
Phase K: Schema + Validierung
  K1 mhdbdb-authority.rnc
  K2 Validierung
```

---

## Kritische Dateien

### Neue Scripts (zu erstellen)
- `scripts/data-wrangling/tei-model/authority-files/audit-authority-files.py`
- `scripts/data-wrangling/tei-model/authority-files/normalize-work-genres.py`
- `scripts/data-wrangling/tei-model/authority-files/unwrap-work-identifiers.py`
- `scripts/data-wrangling/tei-model/authority-files/remove-person-works-links.py`
- `scripts/data-wrangling/tei-model/authority-files/migrate-person-uuids.py`
- `scripts/data-wrangling/tei-model/authority-files/fix-orphan-refs.py`

### Bestehende Dateien (zu aendern)
- `authority-files/works.xml` — Genre-Refs, IDs, GND Casing
- `authority-files/persons.xml` — Works-Links entfernen, UUID-IDs
- `authority-files/lexicon.xml` — 61 verwaiste Concept-Refs + 10 verwaiste Etymologie-Refs
- `authority-files/variants.xml` — 154 verwaiste Lemma-Refs
- `scripts/build-authority-index.py` — Genre-Reader + Persons-Reader
- `scripts/data-wrangling/enhance_works_with_zotero.py` — relatedItem-Wrapper
- `schema/mhdbdb-authority.rnc` — SOLL-Modell Constraints

### Referenz-Dateien (read-only)
- `docs/TEI-MODEL-AUTH-FILES.md` — Soll-Modell (Quelle der Wahrheit)

---

## Verifikation

### Nach jeder Phase:
1. `tei_all.rng` Validierung: alle 7 Dateien VALID
2. Audit erneut laufen → Diff zum vorherigen Audit = nur erwartete Aenderungen

### Nach Phase G (works.xml):
- `grep -c "<ref.*genres.xml" authority-files/works.xml` → 0 (alle entlabelt)
- `grep -c "type=\"gnd\"" authority-files/works.xml` → 0 (GND Uppercase)
- `grep -c "note type=\"identifiers\"" authority-files/works.xml` → 0 (unwrapped)

### Nach Phase H (persons.xml):
- `grep -c "listBibl" authority-files/persons.xml` → 0 (Links entfernt)
- `grep -c "person_[a-f0-9\-]\{9,\}" authority-files/persons.xml` → 0 (UUIDs migriert)

### Nach Phase J (Scripts):
- `python scripts/build-authority-index.py` → laeuft ohne Fehler
- Authority-Index-Output vergleichen: Inhalt identisch (nur Format/Timestamp anders)

### Gesamt:
- 7/7 Authority Files valid gegen tei_all.rng
- 7/7 Authority Files valid gegen mhdbdb-authority.rnc
- 0 verwaiste Referenzen (Audit-Check)
- Build-Scripts laufen ohne Fehler
- npm test → alle Tests bestehen
