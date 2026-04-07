# MHDBDB TEI Target Model (Soll-Modell)

Defines the normative TEI encoding for all texts in the MHDBDB corpus. New texts **must** conform to this model. Existing texts are migrated incrementally (see Issue #30).

**Status:** DRAFT — pending review by Katharina Zeppezauer-Wachauer
**Issue:** #32 (TEI schema)
**Schema:** `schema/mhdbdb.rnc` (RELAX NG Compact, planned)

---

## 1. Document Skeleton

Every TEI file follows this structure:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="{SIGLE}">
  <teiHeader>
    <!-- Section 2: Header -->
  </teiHeader>
  <text>
    <body>
      <!-- Section 3: Body (genre-specific) -->
    </body>
  </text>
</TEI>
```

**Rules:**
- Namespace: `http://www.tei-c.org/ns/1.0` (always)
- Encoding: UTF-8 (always)
- `@xml:id` on `<TEI>`: the text sigle (e.g., `ABG`, `WUT`, `SUB1`)
- Sigle format: uppercase letters + optional digits, no spaces

---

## 2. Header Template (`<teiHeader>`)

The header is already largely standardized across all 675 files. This section documents the canonical structure.

### 2.1 `<fileDesc>`

```xml
<fileDesc>
  <titleStmt>
    <title xml:lang="de">{Werktitel}</title>
    <author ref="#person_{id}">{Autorname}</author>
    <respStmt>
      <resp>digitale Zusammenfuehrung, Annotation und semantische Klassifikation</resp>
      <name ref="https://mhdbdb.plus.ac.at" xml:lang="de">
        Mittelhochdeutsche Begriffsdatenbank (MHDBDB)
      </name>
    </respStmt>
  </titleStmt>

  <publicationStmt>
    <!-- Standardblock: MHDBDB/Uni Salzburg, CC BY-NC-SA 4.0 -->
    <!-- Identisch in allen Dateien -->
  </publicationStmt>

  <sourceDesc>
    <msDesc>
      <msIdentifier corresp="works.xml#work_{id}">
        <idno type="sigle">{SIGLE}</idno>
        <idno type="handschriftencensus">{HC-Nr}</idno>   <!-- optional -->
        <idno type="gnd">{GND-Nr}</idno>                  <!-- optional -->
        <msName xml:lang="de">{Werktitel}</msName>
      </msIdentifier>
      <additional>
        <listBibl>
          <!-- Primaeredition als <biblStruct> -->
          <biblStruct type="{book|bookSection}" xml:id="{SIGLE}_{SIGLE}"
                      corresp="{Zotero-URI}" key="{SIGLE}">
            <!-- monogr oder analytic+monogr -->
          </biblStruct>

          <!-- Optional: digitale Zwischenstufe -->
          <bibl type="digitalIntermediary" xml:id="{SIGLE}_etext_{name}"
                corresp="#{SIGLE}_{SIGLE}">
            <title>Elektronische Zwischenstufe ({Beschreibung})</title>
            <note type="provenance">...</note>
            <note type="fidelity">...</note>
          </bibl>
        </listBibl>
      </additional>
    </msDesc>
  </sourceDesc>
</fileDesc>
```

**Rules:**
- `<author ref>` verweist auf `persons.xml` via Fragment-ID (`#person_{id}`)
- `<msIdentifier corresp>` verweist auf `works.xml` via Fragment-ID (`works.xml#work_{id}`)
- Primaeredition immer als `<biblStruct>` mit Zotero-`corresp`
- Digitale Zwischenstufen als `<bibl type="digitalIntermediary">` (ADR-012)

### 2.2 `<encodingDesc>`

```xml
<encodingDesc>
  <projectDesc>
    <!-- Standardblock: MHDBDB-Beschreibung DE + EN -->
  </projectDesc>
  <editorialDecl>
    <!-- Standardblock: Erklaerung der lokalen Dateireferenzen DE + EN -->
  </editorialDecl>
  <classDecl>
    <taxonomy xml:id="genres">
      <bibl>Genreklassifikation gemaess der Textreihentypologie
        <ptr target="https://www.mhdbdb.sbg.ac.at/textreihen"/>
      </bibl>
      <category xml:id="genre_{hash}" ana="parent" corresp="genres.xml#genre_{hash}">
        <!-- Elterngenre mit Glossen DE/EN -->
      </category>
      <category xml:id="genre_{hash}" corresp="genres.xml#genre_{hash}">
        <!-- Spezifisches Genre mit Glossen DE/EN -->
      </category>
    </taxonomy>
  </classDecl>
</encodingDesc>
```

### 2.3 `<profileDesc>`

```xml
<profileDesc>
  <particDesc>
    <listPerson>
      <person xml:id="person_{id}" corresp="persons.xml#person_{id}">
        <persName type="preferred">{Autorname}</persName>
        <idno type="GND">{GND-Nr}</idno>           <!-- optional -->
        <idno type="wikidata">{Q-Nr}</idno>         <!-- optional -->
        <note type="works">{work_id1},{work_id2}</note>
      </person>
    </listPerson>
  </particDesc>
</profileDesc>
```

### 2.4 `<revisionDesc>`

```xml
<revisionDesc>
  <change when="{YYYY-MM-DD}" who="#{editor-id}">{Beschreibung}</change>
</revisionDesc>
```

---

## 3. Body Structure (Genre-spezifisch)

### 3.1 Vers-Texte (Epik, Lyrik)

**Ziel-Struktur:**

```xml
<body>
  <div type="section" n="1">           <!-- optional: Buch/Abschnitt -->
    <lg type="stanza" n="1">
      <l n="1">
        <w xml:id="..." ...>wort</w>
        <w xml:id="..." ...>wort</w>
      </l>
      <l n="2">...</l>
    </lg>
    <lg type="stanza" n="2">...</lg>
  </div>
</body>
```

**Regeln:**
- Verszeilen als `<l>` (line of verse) mit `@n`
- Strophen als `<lg type="stanza">` mit `@n`
- Optionale uebergeordnete `<div>` fuer Buecher/Abschnitte
- Bei Liedern: `<div type="song">` > `<lg type="stanza">` > `<l>`

**Ist-Zustand (Bestand):** Die meisten Vers-Texte haben `<l>` ohne `<lg>`-Wrapper. Die Migration erfolgt schrittweise (Issue #30, Stufe 2).

### 3.2 Prosa-Texte

**Ziel-Struktur:**

```xml
<body>
  <div type="chapter" n="1">
    <head>
      <w xml:id="..." ...>Kapiteltitel</w>
    </head>
    <p>
      <lb n="1"/>
      <w xml:id="..." ...>wort</w>
      <w xml:id="..." ...>wort</w>
      <lb n="2"/>
      <w xml:id="..." ...>wort</w>
    </p>
  </div>
</body>
```

**Regeln:**
- Absaetze als `<p>`
- Zeilenumbrueche als `<lb/>` (line beginning) mit `@n`
- Kapitel/Abschnitte als `<div type="chapter">` mit `<head>`
- `<l>` ist fuer Vers-Texte reserviert, NICHT fuer Prosa-Zeilenumbrueche

> **ENTSCHEIDUNG NOETIG (Katharina):** Der Bestand nutzt `<l>` in 468/675 Dateien auch fuer Prosa. Empfehlung: Bestand beibehalten, neue Ingests differenzieren. Siehe [Section 8.2](#82-l-vs-lb-in-prosa).

### 3.3 Rezept-Texte (Kochbuecher, medizinische Texte)

**Ziel-Struktur:**

```xml
<body>
  <div type="recipe" n="1">
    <head>
      <w xml:id="..." ...>Rezepttitel</w>
    </head>
    <p>
      <lb n="1"/>
      <w xml:id="..." ...>wort</w>
      <w xml:id="..." ...>wort</w>
    </p>
  </div>
  <div type="recipe" n="2">...</div>
</body>
```

**Regeln:**
- Jedes Rezept als `<div type="recipe">` mit `@n` (Rezeptnummer aus Edition)
- Rezepttitel als `<head>` im `<div>`
- Fliesstext im `<p>` mit `<lb/>` fuer Zeilenumbrueche

### 3.4 Gemischte Texte

Texte mit Vers- und Prosa-Abschnitten verwenden verschachtelte `<div>`-Elemente:

```xml
<body>
  <div type="section" n="1">
    <!-- Prosa-Abschnitt -->
    <p>...</p>
  </div>
  <div type="section" n="2">
    <!-- Vers-Abschnitt -->
    <lg type="stanza" n="1">
      <l n="1">...</l>
    </lg>
  </div>
</body>
```

---

## 4. Wort-Element (`<w>`)

Das `<w>`-Element ist die zentrale Annotationseinheit. Jedes annotierte Wort traegt folgende Attribute:

```xml
<w xml:id="{SIGLE}_{page}{line}_{pos}"
   lemmaRef="lexicon.xml#lemma_{id}"
   pos="{POS-Tags}"
   meaningRef="lexicon.xml#lemma_{id}_sense_{id}"
   wordRef="lexicon.xml#lemma_{id}_sense_{id}_type_{id}">
  sichtbarer Text
</w>
```

### 4.1 Attribute

| Attribut | Status | Pflicht | Beschreibung |
|----------|--------|---------|--------------|
| `@xml:id` | aktiv | ja | Eindeutige ID: `{SIGLE}_{Seite}{Zeile}_{Position}` |
| `@lemmaRef` | aktiv | ja* | Verweis auf `lexicon.xml` Lemma-Eintrag |
| `@pos` | aktiv | ja* | Part-of-Speech Tag(s), Leerzeichen-getrennt |
| `@meaningRef` | aktiv | nein | Verweis auf spezifische Bedeutung in `lexicon.xml` |
| `@wordRef` | **deprecated** | nein | Verweis auf Wortform-Typ. Wird von keinem Code gelesen. |

*`@lemmaRef` und `@pos` sind fuer die Suchfunktion erforderlich. `<w>`-Elemente ohne `@lemmaRef` werden vom Corpus-Index uebersprungen (siehe Position-Counting-Contract, CONTRACTS.MD Sec. B).

### 4.2 `@xml:id` Format

```
{SIGLE}_{Seite}{Zeile}_{Wortposition}

Beispiele:
  ABG_400001_0    (ABG, Seite 400, Zeile 001, Wort 0)
  WUT_101_0       (WUT, Zeile 101, Wort 0)  
  WZB_1ra_6_5     (WZB, Folio 1ra, Zeile 6, Wort 5)
```

Format variiert historisch bedingt. Neue Texte sollen ein konsistentes Schema verwenden. IDs muessen innerhalb eines Dokuments eindeutig sein.

### 4.3 Attribut-Migration (AUFGESCHOBEN)

Die aktuellen Attribute `@lemmaRef`, `@meaningRef`, `@wordRef` sind projektspezifische Erweiterungen, keine TEI P5 Standard-Attribute. Eine Migration zu Standard-Attributen ist geplant, aber aufgeschoben:

| Aktuell | TEI P5 Standard | Status |
|---------|-----------------|--------|
| `@lemmaRef` | `@lemma` oder `@corresp` | aufgeschoben |
| `@meaningRef` | `@ana` | aufgeschoben |
| `@wordRef` | entfernen | aufgeschoben |
| `@pos` | `@pos` (bereits Standard) | kein Handlungsbedarf |

**Grund fuer Aufschub:** 675 Dateien mit Millionen `<w>`-Elementen, aktive WZB-Annotation auf separatem Branch, alle Build-Scripts und JS-Code muessen gleichzeitig migriert werden. Kosten ueberwiegen aktuell den Nutzen. Migration nach WZB-Merge als koordinierte Batch-Operation.

---

## 5. POS-Tagset (19 Tags)

Kanonisches Tagset fuer alle MHDBDB-Texte. Definiert in `.gemini/skills/pos-disambiguator/SKILL.md`.

> **WICHTIG:** `ART` ist KEIN valider Tag. Artikel werden als `DET` getaggt.

| Tag | Name | Beispiele |
|-----|------|-----------|
| **NOM** | Nomen | acker, zit, minne |
| **NAM** | Eigenname | Uolrich, Wiene, Rhin, sant (vor Namen) |
| **ADJ** | Adjektiv | groz, schoene, guot |
| **ADV** | Adverb | schone, vil, sere, gar |
| **DET** | Determinante | der, diu, daz, ein, diser, jener, kein |
| **POS** | Possessivpronomen | min, din, unser |
| **PRO** | Pronomen | ich, ez, wir, Relativpronomen |
| **PRP** | Praeposition | uf, zuo, under, durch |
| **NEG** | Negation | nie, niht, nit, ne, en |
| **NUM** | Numeral | zwo, dri |
| **CNJ** | Konjunktion (allgemein) | Fallback bei Ambiguitaet |
| **SCNJ** | Subordinierende Konj. | daz (Nebensatz), ob, swenne, sit |
| **CCNJ** | Koordinierende Konj. | und, oder, aber, ouch |
| **IPA** | Interrogativpartikel | wie (Frage), war (wohin?) |
| **VRB** | Vollverb | liuhten, varn, machen |
| **VEX** | Hilfsverb | haben/sin/werden (mit Partizip II) |
| **VEM** | Modalverb | muezen, suln, kunnen |
| **INJ** | Interjektion | ahi, owe |
| **DIG** | Zahl (roemisch) | IX, XVII, III |

### 5.1 POS-Migration Altbestand

Der Altbestand nutzt ein aelteres Tagset (`ART` statt `DET`, `CNJ` statt `CCNJ`/`SCNJ`). Die Migration ist ein separates Vorhaben nach Schema-Erstellung:

| Alt | Neu | Aktion |
|-----|-----|--------|
| `ART` | `DET` | Batch-Umbenennung |
| `CNJ` (koordinierend) | `CCNJ` | Kontextabhaengig |
| `CNJ` (subordinierend) | `SCNJ` | Kontextabhaengig |
| `GRA` | *entfaellt* | In ADJ aufgehen (Superlativ = ADJ) |

**Hinweis:** Die CNJ-Differenzierung (CCNJ vs. SCNJ) erfordert linguistische Analyse und kann nicht mechanisch erfolgen. Der POS-Disambiguator-Workflow ist dafuer vorgesehen.

### 5.2 Compound-Tags

Die meisten `<w>`-Elemente im Altbestand tragen Compound-Tags (z.B. `pos="VRB VEX"`, `pos="ART NUM"`), die Ambiguitaet ausdruecken. Der POS-Disambiguator-Workflow loest diese auf einen einzelnen Tag auf.

**Ausnahme:** Morphologische Fusionen behalten zwei Tags:
- Verb + enklitisches Pronomen: `wiltu` = wilt + du -> `VEM PRO`
- Praeposition + Determinator: `zer` = ze + der -> `PRP DET`

---

## 6. Inline-Elemente

### 6.1 Interpunktion

```xml
<seg xml:id="{SIGLE}_{page}{line}_{pos}" type="pc">,</seg>
```

Interpunktion wird als `<seg type="pc">` kodiert, nicht als `<w>`. Achtung: `&lt;` und `&gt;` in `<seg type="pc">` sind korrekte XML-Entities (Winkelklammern im Quelltext), keine Bugs.

### 6.2 Hervorhebungen

```xml
<hi rend="initial">
  <w xml:id="...">Wort</w>
</hi>

<hi rend="upper_case_first_letter">
  <w xml:id="...">Wort</w>
</hi>
```

> **ENTSCHEIDUNG NOETIG (Katharina):** `<hi rend="initial">` ist in 496/675 Dateien mit 310.000+ Vorkommen vorhanden. Empfehlung: als Korpus-Konvention beibehalten. Siehe [Section 8.1](#81-hi-rendinitial).

### 6.3 Seitenumbrueche

```xml
<pb n="{Seitenzahl}"/>
<pb type="folio" n="{Folio}"/>
```

### 6.4 Ergaenzungen

```xml
<supplied>
  <w xml:id="...">ergaenztes Wort</w>
</supplied>
```

Nur fuer editorisch ergaenzte Textteile. Nicht fuer Rezepttitel oder Strukturmarkierung missbrauchen.

---

## 7. Authority-File-Referenzen

Alle Referenzen auf kontrollierte Vokabulare verwenden relative Pfade:

| Referenz | Ziel | Beispiel |
|----------|------|----------|
| `@lemmaRef` | lexicon.xml | `lexicon.xml#lemma_879` |
| `@meaningRef` | lexicon.xml (Sense) | `lexicon.xml#lemma_879_sense_1234` |
| `@wordRef` | lexicon.xml (Type) | `lexicon.xml#lemma_879_sense_1234_type_5678` |
| `@ref` (author) | persons.xml | `#person_445` |
| `@corresp` (msIdentifier) | works.xml | `works.xml#work_89` |
| `@corresp` (genre) | genres.xml | `genres.xml#genre_0480b285` |

**Integritaets-Constraint:** Alle referenzierten IDs muessen in den Authority-Dateien existieren. Wird zur Build-Zeit validiert.

---

## 8. Offene Entscheidungen

### 8.1 `<hi rend="initial">`

**Frage an Katharina:** Soll `<hi rend="initial">` als Korpus-Konvention beibehalten werden?

**Befund:** 496 von 675 Dateien nutzen `<hi rend="initial">` (310.000+ Vorkommen). Es markiert dekorierte Initialen aus Handschriften/Drucken und ist valides TEI.

**Optionen:**
1. **Beibehalten** (Empfehlung) -- es ist eine legitime Kodierung von Manuskript-Merkmalen
2. **Entfernen** -- wenn es ein Migrations-Artefakt ohne philologischen Wert ist
3. **Differenzieren** -- in `<head>` behalten, in `<p>` entfernen

### 8.2 `<l>` vs `<lb/>` in Prosa

**Frage an Katharina:** Wie soll mit `<l>` in Prosa-Texten umgegangen werden?

**Befund:** 468 von 675 Dateien nutzen `<l>` (Verszeile) auch in Prosa-Texten. TEI P5 empfiehlt `<lb/>` fuer Prosa-Zeilenumbrueche.

**Optionen:**
1. **Status quo + Differenzierung** (Empfehlung) -- Bestand beibehalten, neue Ingests verwenden `<l>` nur fuer Vers und `<lb/>` fuer Prosa
2. **Korpusweite Migration** -- Alle Prosa-Texte auf `<lb/>` umstellen (massiver Aufwand)
3. **Akzeptieren** -- `<l>` als generisches "Zeilen-Element" fuer alle Texttypen

---

## 9. Ingest-Anforderungen

Neue Texte muessen folgende Mindestanforderungen erfuellen:

### 9.1 Pflicht (Blocking)

- [ ] Valides XML mit TEI-Namespace
- [ ] `<TEI @xml:id>` mit eindeutigem Sigle
- [ ] `<teiHeader>` mit `<titleStmt>`, `<publicationStmt>`, `<sourceDesc>` (Template aus Sec. 2)
- [ ] `<author @ref>` verweist auf existierenden `persons.xml`-Eintrag (oder neuer Eintrag angelegt)
- [ ] `<msIdentifier @corresp>` verweist auf existierenden `works.xml`-Eintrag (oder neuer Eintrag angelegt)
- [ ] Mindestens ein Genre via `<classDecl>/<taxonomy>`
- [ ] `<w>`-Elemente mit `@xml:id` (eindeutig innerhalb Dokument)
- [ ] `<w @lemmaRef>` fuer alle annotierten Woerter
- [ ] `@pos` mit gueltigem Tag aus dem 19-Tag-Set (Sec. 5)
- [ ] Body-Struktur konform mit Genre-Muster (Sec. 3)
- [ ] Validierung gegen `schema/mhdbdb.rnc` (sobald verfuegbar)

### 9.2 Empfohlen (Non-Blocking)

- [ ] `@meaningRef` fuer semantische Suche
- [ ] `<pb>` fuer Seiten-/Folio-Referenzen
- [ ] `<bibl type="digitalIntermediary">` fuer Provenienz-Kette
- [ ] Handschriftencensus-Nr. in `<msIdentifier>`
- [ ] GND/Wikidata-IDs fuer Autor und Werk

### 9.3 Validierungs-Pipeline

```bash
# 1. Schema-Validierung (sobald Schema verfuegbar)
jing schema/mhdbdb.rnc tei/{SIGLE}.tei.xml

# 2. Referenz-Integritaet (Authority-Files)
python scripts/validate-references.py tei/{SIGLE}.tei.xml

# 3. Index-Rebuild
python scripts/build-corpus-index.py
python scripts/build-authority-index.py

# 4. Tests
npm test
```

---

## 10. Versionierung

| Artefakt | Version | Datum |
|----------|---------|-------|
| Dieses Dokument | 0.1.0 (DRAFT) | 2026-04-07 |
| RELAX NG Schema | -- (geplant) | -- |
| POS-Tagset | 1.0 (19 Tags) | 2026-03 |
| Corpus Index | 4.0.0 | 2026-02 |
| Authority Index | 1.1.0 | 2026-02 |

---

## Referenzen

- [CONTRACTS.MD](CONTRACTS.MD) -- Cross-System Contracts (Position Counting, Normalization)
- [DATA-MODEL.MD](DATA-MODEL.MD) -- Authority-File-Schemas, Index-Struktur
- [ARCHITECTURE.MD](ARCHITECTURE.MD) -- Technische Komponenten, Datenfluss
- [features/030-tei-structural-fixes.md](features/030-tei-structural-fixes.md) -- Triage-Plan fuer strukturelle Fixes
- `.gemini/skills/pos-disambiguator/SKILL.md` -- POS-Tagset-Definition und Disambiguierungs-Regeln
