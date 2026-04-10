# TEI Authority Files — Soll-Modell

Normatives Datenmodell fuer die 7 Authority Files in `authority-files/`.
Pendant zu `docs/TEI-MODEL.md` (Korpusdateien).

**Status:** Entwurf
**Schema:** `schema/mhdbdb-authority.rnc`
**Validierung:** Alle 7 Dateien muessen gegen `tei_all.rng` UND `mhdbdb-authority.rnc` valide sein.

---

## 1. Ueberblick

| Datei | Inhalt | Eintraege | Groesse |
|-------|--------|-----------|---------|
| `lexicon.xml` | Lemmata mit Senses, POS, Etymologie | 43,750 | 33 MB |
| `variants.xml` | Orthographische Varianten pro Lemma | 39,436 Eintraege, 192,674 Formen | 13 MB |
| `persons.xml` | Autoren/Personen mit Normdaten | 210 | 74 KB |
| `works.xml` | Werke mit Bibliographie und Genre | 583 | 1.4 MB |
| `concepts.xml` | Semantische Begriffsontologie | 567 Kategorien | 207 KB |
| `genres.xml` | Gattungstaxonomie | 615 Kategorien | 405 KB |
| `names.xml` | Onomastisches System (Eigennamen) | 90 Kategorien | 33 KB |

### Funktionale Gruppen

| Gruppe | Dateien | TEI-Modell | Daten in |
|--------|---------|------------|----------|
| Woerterbuch | lexicon.xml, variants.xml | TEI Ch. 9 (Dictionaries) | `<body>` |
| Personen | persons.xml | TEI Ch. 13 (Names/People) | `<body>` |
| Bibliographie | works.xml | TEI Ch. 3 (Bibliography) | `<body>` |
| Taxonomien | concepts.xml, genres.xml, names.xml | TEI Ch. 2.3.7 (Taxonomy) | `<encodingDesc>/<classDecl>` |

---

## 2. Grundregeln (gelten fuer alle 7 Dateien)

### 2.1 Daten-Platzierung

| Datei | Daten in | Modell |
|-------|----------|--------|
| lexicon.xml | `<body>` | TEI Ch. 9 Dictionaries |
| variants.xml | `<body>` | TEI Ch. 9 Dictionaries |
| persons.xml | `<body>` | TEI Ch. 13 Names/People |
| works.xml | `<body>` | TEI Ch. 3 Bibliography |
| concepts.xml | `<encodingDesc>/<classDecl>` | TEI Ch. 2.3.7 Taxonomy |
| genres.xml | `<encodingDesc>/<classDecl>` | TEI Ch. 2.3.7 Taxonomy |
| names.xml | `<encodingDesc>/<classDecl>` | TEI Ch. 2.3.7 Taxonomy |

**Taxonomien bleiben in `<encodingDesc>`.** TEI erlaubt `<taxonomy>` NUR in `<encodingDesc>/<classDecl>` — nicht in `<body>` (getestet gegen tei_all.rng). Das ist die TEI-vorgesehene Platzierung fuer Klassifikationssysteme. Der `<body>` enthaelt einen Platzhalter-`<p>`.

### 2.2 Cross-Referencing

**SOLL:** Ein Mechanismus pro Semantik, konsistent ueber alle Dateien.

| Semantik | Attribut/Element | Wann verwenden |
|----------|-----------------|----------------|
| Kanonische Definition | `@ref` | Element VERWEIST auf seine Definition: `<author ref="persons.xml#person_1">` |
| Korrespondenz | `@corresp` | Element ENTSPRICHT einem anderen: `<entry corresp="lexicon.xml#lemma_1">` |
| Zeiger (kein Label) | `<ptr target="..."/>` | Verweis ohne sichtbaren Text: `<ptr target="concepts.xml#concept_N"/>` |

**VERBOTEN:**
- `<ref target="...">Label Text</ref>` fuer cross-file Verweise — das ist Denormalisierung. Der Label-Text gehoert in die Zieldatei.
- Bidirektionale Links (gleiche Information an 2 Stellen) — eine Richtung ist Master, die andere wird abgeleitet.

### 2.3 Identifier

**Format:** `{prefix}_{id}`

| Datei | Prefix | ID-Format | Beispiel |
|-------|--------|-----------|----------|
| lexicon.xml | `lemma` | numerisch | `lemma_879` |
| lexicon.xml | `lemma_N_sense` | numerisch | `lemma_879_sense_1177` |
| variants.xml | `type` | numerisch | `type_2239` |
| persons.xml | `person` | numerisch | `person_1` |
| works.xml | `work` | numerisch | `work_89` |
| concepts.xml | `concept` | 8-stellig hierarchisch | `concept_11200000` |
| genres.xml | `genre` | UUID-Hash | `genre_2c9f837c` |
| names.xml | `name` | 8-stellig hierarchisch | `name_41232000` |

**Anmerkung:** Genre-UUIDs bleiben (615 IDs + 3422 Referenzen umzubenennen waere unverhältnismaessig). Concepts und Names nutzen hierarchische 8-Steller — das ist ein sinnvolles Schema fuer Taxonomien.

**Migration:** 4 Personen mit UUID-Format (`person_778d109...`) werden zu `person_N` migriert.

### 2.4 Externe Identifier (Normdaten)

**SOLL:** Einheitliche Schreibweise in allen Dateien.

| Normdatei | `@type` Wert | Beispiel |
|-----------|-------------|---------|
| GND | `GND` (Uppercase) | `<idno type="GND">118565133</idno>` |
| Wikidata | `wikidata` | `<idno type="wikidata">Q77480</idno>` |
| Handschriftencensus | `handschriftencensus` | `<idno type="handschriftencensus">217</idno>` |

**IST-Problem:** persons.xml nutzt `GND`, works.xml nutzt `gnd`. SOLL: `GND` ueberall (offizielles Akronym der Deutschen Nationalbibliothek).

### 2.5 Gemeinsamer teiHeader

Alle 7 Dateien haben denselben minimalen Header:

```xml
<teiHeader>
  <fileDesc>
    <titleStmt>
      <title>MHDBDB {Dateiname}</title>
    </titleStmt>
    <publicationStmt>
      <publisher>Mittelhochdeutsche Begriffsdatenbank (MHDBDB)</publisher>
      <date>{Datum}</date>
    </publicationStmt>
    <sourceDesc>
      <p>{Herkunftsbeschreibung}</p>
    </sourceDesc>
  </fileDesc>
</teiHeader>
```

Taxonomie-Dateien (concepts, genres, names) haben zusaetzlich `<encodingDesc>/<classDecl>/<taxonomy>` — dort leben die Taxonomie-Daten (TEI erlaubt `<taxonomy>` nur dort).

---

## 3. Datei-spezifische Modelle

### 3.1 lexicon.xml — Woerterbuch

TEI Ch. 9 (Dictionaries). Containert alle Lemmata des MHDBDB-Lexikons.

```xml
<body>
  <div type="lexicon">
    <entry xml:id="lemma_879">
      <form type="lemma"><orth>vriunt</orth></form>
      <gramGrp><pos>NOM</pos></gramGrp>
      <etym type="morphological">
        <seg type="component" corresp="lexicon.xml#lemma_X">Komponente</seg>
      </etym>
      <sense xml:id="lemma_879_sense_1177" ana="#type_2239 #type_5544">
        <ptr target="concepts.xml#concept_31422000"/>
      </sense>
    </entry>
  </div>
</body>
```

**Elemente:**

| Element | Pflicht | Attribute | Inhalt |
|---------|---------|-----------|--------|
| `<entry>` | ja | `@xml:id` (lemma_N) | form + gramGrp + sense* + etym? |
| `<form type="lemma">` | ja | `@type="lemma"` | `<orth>` |
| `<gramGrp>` | ja | — | `<pos>` (1+, manche Lemmata mehrere POS) |
| `<etym>` | optional | `@type="morphological"` | `<seg type="component">` |
| `<sense>` | ja (1+) | `@xml:id`, `@ana`? | `<ptr target="concepts.xml#..."/>` |

**`@ana` auf `<sense>`:** Raum-separierte `#type_N` Werte (Verweise auf variants.xml). 30% der Senses haben kein `@ana` — das ist akzeptabel (nicht alle Senses haben Belegstellen mit Wortformen).

**Referentielle Integritaet:** 19 `<ptr target="concepts.xml#...">` Referenzen zeigen auf nicht-existente Konzepte. Bereinigen.

### 3.2 variants.xml — Orthographische Varianten

TEI Ch. 9 (Dictionaries). Jeder Eintrag entspricht einem Lemma und listet alle belegten Schreibweisen.

```xml
<body>
  <div type="orthographicVariants">
    <entry corresp="lexicon.xml#lemma_879">
      <form xml:id="type_2239">vriunt</form>
      <form xml:id="type_5544">vriwnt</form>
      <form xml:id="type_8891">vrivnt</form>
    </entry>
  </div>
</body>
```

**Design-Entscheidung:** Varianten in separater Datei statt in lexicon.xml (192k Formen wuerden das 33MB-Lexikon auf >60MB aufblaehen). Verknuepfung via `@corresp`.

**Referentielle Integritaet:** 154 Eintraege verweisen auf nicht-existente Lemmata. Bereinigen.

### 3.3 persons.xml — Personenregister

TEI Ch. 13 (Names, Dates, People, Places).

```xml
<body>
  <listPerson>
    <person xml:id="person_1">
      <persName type="preferred">Konrad von Wuerzburg</persName>
      <persName type="alternative" xml:lang="en">Conrad of Wuerzburg</persName>
      <idno type="GND">118565133</idno>
      <idno type="wikidata">Q77480</idno>
    </person>
  </listPerson>
</body>
```

**SOLL-Aenderungen gegenueber IST:**

| IST | SOLL | Begruendung |
|-----|------|-------------|
| `<listBibl><bibl corresp="works.xml#..."/>` | entfernt | Redundant: works.xml hat `<author ref="persons.xml#...">`. Build-Script leitet ab. |
| 4x `person_UUID` | `person_N` | Konsistenz mit restlichen 206 Eintraegen |
| `<idno type="GND">` | `<idno type="GND">` | Bereits korrekt (Uppercase) |

**Kein persons→works Link:** works.xml ist Master fuer die Autor-Werk-Beziehung. Der Build-Script (`build-authority-index.py`) leitet `person.works` aus works.xml ab.

### 3.4 works.xml — Werkverzeichnis

TEI Ch. 3 (Core Tags for Headers / Bibliography).

```xml
<body>
  <listBibl>
    <bibl xml:id="work_350">
      <title xml:lang="de">Aalener Stadtratsgedicht</title>
      <idno type="sigle">ASG</idno>
      <idno type="GND">4467770-4</idno>
      <idno type="wikidata">Q2643537</idno>
      <idno type="handschriftencensus">217</idno>
      <ptr target="genres.xml#genre_2c9f837c"/>
      <author ref="persons.xml#person_786">Heinrich von Rang</author>
      <relatedItem>
        <biblStruct type="journalArticle" xml:id="ASG_ASG"
                    corresp="http://zotero.org/..." key="ASG">
          <analytic>
            <author><name>Heinrich von Rang</name></author>
            <title level="a">Das Stadtratsgedicht</title>
          </analytic>
          <monogr>
            <title level="j">Aalener Jahrbuch</title>
            <idno type="callNumber">ASG</idno>
            <imprint>
              <biblScope unit="page">45-74</biblScope>
              <date>1978</date>
            </imprint>
          </monogr>
        </biblStruct>
      </relatedItem>
    </bibl>
  </listBibl>
</body>
```

**SOLL-Aenderungen gegenueber IST:**

| IST | SOLL | Begruendung |
|-----|------|-------------|
| `<biblStruct>` direkt in `<bibl>` | `<biblStruct>` in `<relatedItem>` | TEI: biblStruct nicht erlaubt als Kind von bibl |
| `<ref target="genres.xml#...">Label</ref>` | `<ptr target="genres.xml#..."/>` | Label ist denormalisiert; Genre-Name gehoert in genres.xml |
| `<idno type="gnd">` | `<idno type="GND">` | Einheitliche Grossschreibung |
| Externe IDs in `<note type="identifiers">` | Externe IDs als direkte `<idno>` | Moeglich weil `<ref>` → `<ptr>` (getestet: valid) |
| Genre-Parent-Refs `<ref type="parent">` | entfernt | Hierarchie gehoert in genres.xml, nicht in works.xml |
| `<monogr>`: editor vor idno | idno vor editor | TEI Content Model |

**Genre-Referenzen — IST vs SOLL:**

IST (denormalisiert, 4 Elemente pro Genre):
```xml
<ref target="genres.xml#genre_2c9f837c" xml:lang="de" n="prefLabel">Kleindidaxe</ref>
<ref target="genres.xml#genre_2c9f837c" xml:lang="en" n="prefLabel">Didactic Short Poetry</ref>
<ref target="genres.xml#genre_d75ff6ba" xml:lang="de" type="parent" n="prefLabel">Lehrdichtung</ref>
<ref target="genres.xml#genre_d75ff6ba" xml:lang="en" type="parent" n="prefLabel">Didactic Poetry</ref>
```

SOLL (normalisiert, 1 Element):
```xml
<ptr target="genres.xml#genre_2c9f837c"/>
```

Label und Parent-Hierarchie werden zur Laufzeit aus genres.xml aufgeloest. Der Build-Script macht das bereits.

**Autorenname in `<author>`:** Der Textinhalt (`Heinrich von Rang`) bleibt — TEI erwartet lesbaren Text in `<author>`. Die Quelle der Wahrheit fuer den Autorennamen ist `persons.xml`; der Text in `<author>` ist Convenience fuer menschliche Leser. Das ist keine Denormalisierung im selben Sinne wie Genre-Labels, weil `<author>` ohne Text semantisch unvollstaendig waere.

### 3.5 concepts.xml — Begriffsontologie

TEI Ch. 2.3.7 (The Classification Declaration / Taxonomy). Daten in `<encodingDesc>/<classDecl>` (TEI erlaubt `<taxonomy>` nur dort).

```xml
<encodingDesc>
  <classDecl>
    <taxonomy xml:id="mhdbdb-concepts">
      <desc>Semantische Begriffsontologie der MHDBDB</desc>
      <category xml:id="concept_11200000">
        <catDesc>
          <term xml:lang="de">Wetter/Winde</term>
          <term xml:lang="en">Weather/Winds</term>
          <ptr type="broader" target="#concept_11000000"/>
        </catDesc>
      </category>
    </taxonomy>
  </classDecl>
</encodingDesc>
...
<body>
  <p>Taxonomy data in encodingDesc/classDecl.</p>
</body>
```

### 3.6 genres.xml — Gattungstaxonomie

Identisches Modell wie concepts.xml.

```xml
<taxonomy xml:id="mhdbdb-genres">
  <desc>Gattungstaxonomie der MHDBDB</desc>
  <category xml:id="genre_2c9f837c">
    <catDesc>
      <term xml:lang="de">Kleindidaxe</term>
      <term xml:lang="en">Didactic Short Poetry</term>
      <ptr type="broader" target="#genre_d75ff6ba"/>
    </catDesc>
  </category>
</taxonomy>
```

### 3.7 names.xml — Onomastisches System

Identisches Modell wie concepts.xml, mit zusaetzlichen Concept-Verweisen.

```xml
<taxonomy xml:id="mhdbdb-names">
  <desc>Onomastisches System der MHDBDB</desc>
  <category xml:id="name_41232000">
    <catDesc>
      <term xml:lang="de">Staedtenamen (Urbanonyme)</term>
      <term xml:lang="en">City names (Urbanonyms)</term>
      <ptr type="broader" target="#name_41230000"/>
      <ptr type="exactMatch" target="concepts.xml#concept_24212000"/>
    </catDesc>
  </category>
</taxonomy>
```

---

## 4. Referenz-Graphen

### 4.1 Wer verweist auf wen? (nur Authority-intern)

```
lexicon.xml ──ptr──> concepts.xml
     ^                    ^
     │corresp             │exactMatch/closeMatch
variants.xml        names.xml

works.xml ──author @ref──> persons.xml
     │
     └──ptr──> genres.xml
```

**Keine Rueckverweise:** persons.xml verweist NICHT auf works.xml. Der Build-Script leitet die Rueckrichtung ab.

**Korpus → Authority** (nicht dargestellt): Die 666 TEI-Dateien verweisen via `@lemmaRef` auf lexicon.xml, `@ana` auf lexicon.xml (Senses), `@corresp` auf variants.xml, `@ref` auf persons.xml und works.xml. Diese Verweise sind im Korpus-Modell (`docs/TEI-MODEL.md`) dokumentiert.

### 4.2 Verweistypen

| Von | Nach | Element/Attribut | Kardinalitaet |
|-----|------|-----------------|---------------|
| lexicon → concepts | `<ptr target="concepts.xml#..."/>` | sense hat 0-N concept-Zeiger |
| lexicon → lexicon | `<seg corresp="lexicon.xml#...">` | Etymologie-Komponenten |
| variants → lexicon | `@corresp="lexicon.xml#..."` | 1:1 (ein Entry pro Lemma) |
| works → persons | `<author ref="persons.xml#...">` | 1:N (4 Werke haben 2 Autoren) |
| works → genres | `<ptr target="genres.xml#..."/>` | 1:N (ein Werk, mehrere Genres) |
| names → concepts | `<ptr type="exactMatch\|closeMatch" target="concepts.xml#..."/>` | 0-N |
| Taxonomien intern | `<ptr type="broader" target="#..."/>` | 0-N (Polyhierarchie) |

---

## 5. Datenqualitaet — Bekannte Probleme

| Problem | Datei | Anzahl | Aktion |
|---------|-------|--------|--------|
| Verwaiste Lemma-Referenzen | variants.xml → lexicon.xml | 154 | Bereinigen |
| Verwaiste Konzept-Referenzen | lexicon.xml → concepts.xml | 19 | Bereinigen |
| Verwaiste Personen-Referenz | works.xml → persons.xml | 1 (`person_schweizer_anonymus`) | Person anlegen oder Ref entfernen |
| Werk ohne Bibliographie | works.xml (work_6) | 1 | biblStruct nachpflegen |
| 30% Senses ohne @ana | lexicon.xml | 18,836 | Akzeptabel (keine Belegstellen) |

---

## 6. Migration IST → SOLL

### Reihenfolge und Abhaengigkeiten

```
6.1 works.xml: Genre-Refs + IDs + GND  (Genre-Entlabelung VOR ID-Unwrapping!)
     ↓
6.2 persons.xml: Works-Links entfernen
     ↓
6.3 persons.xml: UUID-IDs migrieren  (Cascade in works.xml + tei/*.tei.xml)
```

### 6.1 works.xml: Genre-Refs entlabeln + externe IDs unwrappen

**Script:** `normalize-works.py` (zu erstellen)

Drei Aenderungen in einem Durchlauf (Reihenfolge wichtig!):

1. **Genre-Refs entlabeln** (ZUERST — aendert Content Model):
   IST: 3,422 `<ref target="genres.xml#..." xml:lang="...">Label Text</ref>` (inkl. Parent-Refs)
   SOLL: 1 `<ptr target="genres.xml#..."/>` pro Genre (ohne Label, ohne Parents, dedupliziert)

2. **Externe IDs aus `<note type="identifiers">` unwrappen** (DANACH — erst valid wenn `<ref>` → `<ptr>`):
   IST: `<note type="identifiers"><idno type="GND">...</idno>...</note>`
   SOLL: `<idno type="GND">...</idno>` direkt in `<bibl>`

3. **GND Casing:** `<idno type="gnd">` → `<idno type="GND">`

**Script-Impact:**

| Script | Aenderung |
|--------|-----------|
| `build-authority-index.py` | Genre-Refs: `.//tei:ref[contains(@target, "genres.xml#")]` → `.//tei:ptr[contains(@target, "genres.xml#")]` |
| `enhance_works_with_zotero.py` | Neue `<biblStruct>` in `<relatedItem>` wrappen statt direkt in `<bibl>` einfuegen |
| `sync_tei_headers.py` | Liest `<biblStruct>` aus works.xml via `.//tei:biblStruct` (funktioniert durch `<relatedItem>` hindurch), schreibt in TEI-Header `<additional>/<listBibl>` (anderer Kontext, dort valid) |

### 6.2 persons.xml: Works-Links entfernen

Die `<listBibl>` (in dieser Session von `<note>` migriert) wird entfernt. `build-authority-index.py` leitet die Beziehung aus works.xml ab.

**Script:** Inline (trivial — `<listBibl>` Elemente entfernen)
**Script-Impact:** `build-authority-index.py` persons-Reader muss umgebaut werden — liest works.xml statt persons.xml fuer person→works Mapping.

### 6.3 persons.xml: UUID-IDs migrieren

4 Personen: UUID → naechste freie numerische ID.

| IST | SOLL |
|-----|------|
| `person_778d109...` | `person_N` (naechste freie ID) |

**Cascade:**
- `works.xml`: `<author ref="persons.xml#person_UUID">` aktualisieren
- `tei/*.tei.xml`: `<author ref="#person_UUID">` in TEI-Headern aktualisieren (666 Dateien, aber nur die ~4 betroffenen Autoren)

---

## 7. Validierung

Zwei-Stufen-Validierung analog zu den Korpusdateien:

| Stufe | Schema | Prueft |
|-------|--------|--------|
| 1 | `tei_all.rng` | TEI P5 Konformitaet |
| 2 | `mhdbdb-authority.rnc` | MHDBDB-spezifische Constraints (Pflicht-Attribute, erlaubte Werte, Referenz-Muster) |

---

## 8. Referenzen

- TEI P5 Ch. 2.3.7: [The Classification Declaration](https://tei-c.org/release/doc/tei-p5-doc/en/html/HD.html#HD55)
- TEI P5 Ch. 3.12: [Bibliographic Citations](https://tei-c.org/release/doc/tei-p5-doc/en/html/CO.html#COBI)
- TEI P5 Ch. 9: [Dictionaries](https://tei-c.org/release/doc/tei-p5-doc/en/html/DI.html)
- TEI P5 Ch. 13: [Names, Dates, People, Places](https://tei-c.org/release/doc/tei-p5-doc/en/html/ND.html)
- TEI att.canonical: [`@ref`](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.canonical.html)
- TEI att.global.linking: [`@corresp`](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.global.linking.html)
