# TEI Authority Files — Soll-Modell

Normatives Datenmodell fuer die 8 Authority Files in `authority-files/`.
Pendant zu `docs/TEI-MODEL.md` (Korpusdateien).

**Status:** Implementiert (2026-04-10, Phases F-K; 2026-04-14 `contributors.xml` ergänzt)
**Schema:** `schema/mhdbdb-authority.rnc` (Source) → `schema/mhdbdb-authority.rng` (generiert)
**Beispiele:** `schema/examples/authority-*.example.xml`
**Validierung:** Alle 8 Dateien valide gegen `tei_all.rng` UND `mhdbdb-authority.rnc`.

---

## 1. Ueberblick

| Datei | Inhalt | Eintraege | Groesse |
|-------|--------|-----------|---------|
| `lexicon.xml` | Lemmata mit Senses, POS, Etymologie | 43,750 | 33 MB |
| `variants.xml` | Orthographische Varianten pro Lemma | 42,627 Eintraege, 256,759 Formen | 16 MB |
| `persons.xml` | Autoren/Personen mit Normdaten | 211 | 74 KB |
| `works.xml` | Werke mit Bibliographie und Genre | 583 | 1.4 MB |
| `contributors.xml` | MHDBDB-Mitwirkende (Gruender, Koordination, Editor:innen) | 51 Personen + 2 Orgs | 15 KB |
| `concepts.xml` | Semantische Begriffsontologie | 567 Kategorien | 207 KB |
| `genres.xml` | Gattungstaxonomie | 615 Kategorien | 405 KB |
| `names.xml` | Onomastisches System (Eigennamen) | 90 Kategorien | 33 KB |

### Funktionale Gruppen

| Gruppe | Dateien | TEI-Modell | Daten in |
|--------|---------|------------|----------|
| Woerterbuch | lexicon.xml, variants.xml | TEI Ch. 9 (Dictionaries) | `<body>` |
| Personen | persons.xml | TEI Ch. 13 (Names/People) | `<body>` |
| Bibliographie | works.xml | TEI Ch. 3 (Bibliography) | `<body>` |
| Mitwirkende | contributors.xml | TEI Ch. 13 (Names/People) + Ch. 3 (Orgs) | `<body>` |
| Taxonomien | concepts.xml, genres.xml, names.xml | TEI Ch. 2.3.7 (Taxonomy) | `<encodingDesc>/<classDecl>` |

### Provenienz und Aktualitaet

Wichtig fuer den aktiven Betrieb (siehe [INDEX.md → Current Phase](INDEX.md#current-phase)): Alle Authority-Files entstanden aus **einer einmaligen Migration** (2025-07-22), die **dreistufig** war: Alt-MHDBDB (RDF-Triple-Store bei Salzburg, SPARQL ueber dh.plus.ac.at) → CSV-Snapshots (via SPARQL-Queries, auf Branch `initial-data-wrangling` unter `lists/`) → TEI-XML (via `scripts/_archived/tei-transformation.py`, Commit `8513589ea`). **Seit dieser Migration ist dieses Repo der alleinige Master fuer alle 8 Authority-Files. Es gibt keinen Re-Export aus Salzburg und keine lebende externe Quelle.** Die CSV-Exporte waren Snapshots, keine Schnittstelle: alles Weitere wird hier gepflegt.

„Stale" heisst hier: aus dem Korpus abgeleitet und nicht mit-regeneriert, sobald sich Daten aendern. Der Korpus wird laufend editiert (Skript-Ingest UND haendische Korrekturen), daher driften korpus-gekoppelte Files. Detektor: `scripts/audit/check-authority-cross-refs.py` (in CI via `schema-validation.yml`).

| Datei | Herkunft (einmalig, 2025-07-22) | Aktuelle Pflege | Drift-Risiko |
|-------|-----------|-----------|--------------|
| `variants.xml` | korpus-extrahiert (`initial-data-wrangling`) | **korpus-abgeleitet**, regenerierbar via `scripts/sync/extract-variants.py` (#44/#115) | hoch: jede neue/geaenderte Form muss nachgezogen werden. Regenerierung verlustfrei + automatisierbar |
| `lexicon.xml` | RDF→CSV-Snapshot (`lists/lexicon.csv`) → `tei-transformation.py::create_lexicon_tei` | **Repo = Master UND Korpus-Index** (Korpus fuehrt, lexicon zieht nach) | mittel: ingest-erzeugte Lemma/Sense-IDs brauchen repo-internen Backfill (977 dangling Refs, 349 IDs, #115). Kein Salzburg-Re-Export moeglich (CSV war selbst nur Snapshot) |
| `persons.xml` | RDF→CSV→TEI-Snapshot | repo-intern handgepflegt, **kein Re-Export** | gering (0 unresolved) |
| `works.xml` | RDF-Snapshot + Zotero-Enrichment | `enhance_works_with_zotero.py` + manuell, repo-intern | gering (0 unresolved) |
| `concepts.xml` | RDF→CSV→TEI-Snapshot (Begriffssystem) | repo-intern handgepflegt, **kein Re-Export** | gering (0 unresolved) |
| `genres.xml` | RDF→CSV→TEI-Snapshot | repo-intern handgepflegt, **kein Re-Export** | gering (0 unresolved) |
| `names.xml` | RDF→CSV→TEI-Snapshot | repo-intern handgepflegt, korpus-entkoppelt | gering (0 Korpus-Kopplung) |
| `contributors.xml` | born-digital (2026-04) | **handgepflegt** (kein Generator) | keines |

**Gesamtmuster:** Alle Files sind RDF-abgeleitete Migrations-Snapshots (2025-07-22), seit der Migration **repo-intern** gepflegt — es gibt keinen externen Master mehr und keine Re-Export-Quelle. Nur `variants.xml` ist korpus-abgeleitet und regenerierbar. `lexicon.xml` ist Repo-Master UND Index der Korpus-Annotation: traegt ein Korpus-`<w>` eine `@lemmaRef`/`@ana`, die in lexicon.xml fehlt, fuehrt der Korpus und lexicon.xml muss nachgezogen werden (siehe [CONTRACTS.md → Authority Source Rules](CONTRACTS.md#f-authority-source-rules)). Neue **Sense-Bedeutungen** sind dabei kuratorisch (Team vergibt die concept-Zuordnung), nicht automatisch aus dem Korpus rekonstruierbar. `lexicon.xml` und `variants.xml` waren bis 2026-05 stale; `variants.xml` ist regeneriert (256.759 Formen, 2026-05-29), `lexicon.xml` hat noch 977 ingest-bedingte dangling Refs (349 IDs, repo-interner Backfill offen, #115; Ursache siehe §6.1). Die `_archived`-Generatoren schreiben korpus-seitig Pre-#32-Attribute (`@wordRef`/`@meaningRef`) und duerfen nie ungeprueft gegen den aktuellen Korpus laufen.

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
| contributors.xml | `contrib` | 3-stellig zero-padded | `contrib_001` |
| concepts.xml | `concept` | 8-stellig hierarchisch | `concept_11200000` |
| genres.xml | `genre` | UUID-Hash | `genre_2c9f837c` |
| names.xml | `name` | 8-stellig hierarchisch | `name_41232000` |

**Anmerkung:** Genre-UUIDs bleiben (615 IDs + 3422 Referenzen umzubenennen waere unverhältnismaessig). Concepts und Names nutzen hierarchische 8-Steller — das ist ein sinnvolles Schema fuer Taxonomien.

**Migration:** 4 Personen mit UUID-Format wurden zu `person_N` migriert (2026-04-10). 1 Person neu angelegt: `person_anonym` (Schweizer Anonymus, GND 103130276).

### 2.4 Externe Identifier (Normdaten)

**SOLL:** Einheitliche Schreibweise in allen Dateien.

| Normdatei | `@type` Wert | Beispiel |
|-----------|-------------|---------|
| GND | `GND` (Uppercase) | `<idno type="GND">118565133</idno>` |
| Wikidata | `wikidata` | `<idno type="wikidata">Q77480</idno>` |
| Handschriftencensus | `handschriftencensus` | `<idno type="handschriftencensus">217</idno>` |

Alle Dateien nutzen `GND` (Uppercase, offizielles Akronym der Deutschen Nationalbibliothek). Migriert 2026-04-10.

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

**Referentielle Integritaet:** Alle Konzept-Referenzen valide (19 verwaiste Referenzen bereinigt 2026-04-10).

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

**Referentielle Integritaet:** Alle Lemma-Referenzen valide (154 verwaiste Eintraege bereinigt 2026-04-10).

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
      <category xml:id="concept_13023100">
        <catDesc>
          <term xml:lang="de">Obst</term>
          <term xml:lang="de" type="alternative">Früchte</term>
          <term xml:lang="en">Fruits</term>
          <ptr type="broader" target="#concept_13023000"/>
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

**`<term type="alternative">`** — optionale Synonyme zum Primär-Term. Pro Sprache mehrere `type="alternative"`-Einträge erlaubt; 263 von 567 Concepts haben aktuell mindestens ein deutsches Synonym, 266 ein englisches. Build-Skript (`scripts/build-authority-index.py:parse_concepts()`) trennt Primär (`termDE`/`termEN`) von Alternative (`altDE[]`/`altEN[]`), siehe DATA-MODEL.md §Concepts. **Quirk:** Einige Einträge verwenden Slash-separierte Strings innerhalb eines einzigen `<term type="alternative">` (z.B. `Abendessen/Nachtmahl/Festmahl`); editorialer Followup für Aufteilung in separate `<term>`-Elemente offen.

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

### 3.8 contributors.xml — Mitwirkenden-Register

TEI Ch. 13 (Names/People) + Ch. 3 (Organizations). Zentrales Register aller Personen und Organisationen, die am MHDBDB-Projekt mitgewirkt haben. Dient als Authority-Quelle fuer die Editor-Attribution in den Korpus-Headern (via `@ref` aus `<titleStmt>/<respStmt>` und `<publicationStmt>/<authority>`).

**Rollen auf `<person>/@role`:** `founder` | `coordinator` | `lead-editor` | `editor`. Vom Authority-Schema enforced (`schema/mhdbdb-authority.rnc`). `<org>`-Eintraege tragen keine `@role`.

**ID-Konvention:** `contrib_NNN` (zero-padded 3-stellig). Slots 001–007 sind fest (Gruender, Koordinatorin, Lead-Editor:innen), 008+ folgen der chronologischen Mitwirkenden-Liste.

```xml
<text>
  <body>
    <listOrg>
      <org xml:id="mhdbdb-team">
        <orgName xml:lang="de">MHDBDB-Team</orgName>
        <desc xml:lang="de">Alle Mitwirkenden der MHDBDB — Verweis-Anker fuer kollektive Team-Attribution.</desc>
      </org>
      <org xml:id="dhcraft">
        <orgName xml:lang="de">Digital Humanities Craft</orgName>
        <desc xml:lang="de">Digital-Humanities-Dienstleister, technische Umsetzung.</desc>
        <idno type="URL">https://dhcraft.org</idno>
      </org>
    </listOrg>
    <listPerson>
      <person xml:id="contrib_001" role="founder">
        <persName xml:lang="de">Klaus M. Schmidt</persName>
      </person>
      <person xml:id="contrib_003" role="coordinator">
        <persName xml:lang="de">Katharina Zeppezauer-Wachauer</persName>
      </person>
      <person xml:id="contrib_004" role="lead-editor">
        <persName xml:lang="de">Vlastimil Brom</persName>
        <note xml:lang="de">Haupteditor fuer TKR, TKA, VTC.</note>
      </person>
      <!-- weitere contrib_NNN ... -->
    </listPerson>
  </body>
</text>
```

**Wie das Korpus dieses Register benutzt:**

- `<titleStmt>/<respStmt>` in jedem Korpus-Header verweist via `<orgName ref="contributors.xml#mhdbdb-team">` auf die kollektive Team-Attribution — kein Aufblaehen des Headers durch 50+ Namen.
- `<publicationStmt>/<authority>` traegt drei `<persName ref="contributors.xml#contrib_00X">` fuer die Gruender + Koordinatorin (immer gleich, in jeder Datei).
- Fuer prominente Haupteditor:innen (aktuell TKR/TKA/VTC/PUC/JT) kommt ein zweites `<respStmt>` mit `<name role="lead-editor" ref="contributors.xml#contrib_00X">` dazu.

**Namens-Struktur — bewusste Asymmetrie:**

In `contributors.xml` selbst sind die Namen als Plaintext in `<persName>` gespeichert:

```xml
<person xml:id="contrib_001" role="founder">
  <persName xml:lang="de">Klaus M. Schmidt</persName>
</person>
```

In den Korpus-Headern werden dieselben drei Fest-Slot-Personen (Schmidt, Puetz, Zeppezauer-Wachauer) dagegen **strukturiert** als `<forename>` + `<surname>` ausgegeben:

```xml
<persName role="founder" ref="contributors.xml#contrib_001">
  <forename>Klaus M.</forename>
  <surname>Schmidt</surname>
</persName>
```

Das ist bewusst so: `contributors.xml` ist die kanonische semantische Quelle (mit `@xml:id` als Identitaet), der Header-Eintrag ist eine serialisierte Darstellung, die der `scripts/_archived/migrate-header-credits.py`-Migration 2026-04-15 aus einer hardcodierten `CANONICAL_AUTHORITY`-Konstante erzeugt hat. Die Konstante steht in der Script-Datei und war das einfachste Ausdrucksmittel, da die Spaltung "Vorname | Nachname" fuer drei Personen bekannt und stabil war. Die restlichen 48+ Editor:innen haben keinen Header-Eintrag — nur den kollektiven `mhdbdb-team`-Verweis.

**Fuer zukuenftige Tools**, die contributors.xml lesen und strukturierte Namen brauchen (z.B. eine Reader-View-Integration fuer Lead-Editor-Anzeige): die Plaintext-Form muss am Whitespace gesplittet werden (letztes Token = Nachname), mit Sonder-Behandlung fuer Praefixe wie "van", "von", etc. Die Fest-Slot-Eintraege in der Script-Konstante sind keine verlaessliche Quelle fuer nicht-feste contrib_NNN-IDs.

Details siehe [`TEI-MODEL.md`](TEI-MODEL.md) §2.1bis.

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

**Korpus → Authority** (nicht dargestellt): Die 667 TEI-Dateien verweisen via `@lemmaRef` auf lexicon.xml, `@ana` auf lexicon.xml (Senses), `@corresp` auf variants.xml, `@ref` auf persons.xml und works.xml. Diese Verweise sind im Korpus-Modell (`docs/TEI-MODEL.md`) dokumentiert.

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

| Problem | Datei | Status |
|---------|-------|--------|
| Verwaiste Lemma-Referenzen | variants.xml → lexicon.xml | Bereinigt (154 entfernt, 2026-04-10) |
| Verwaiste Konzept-Referenzen | lexicon.xml → concepts.xml | Bereinigt (19 entfernt, 2026-04-10) |
| Verwaiste Personen-Referenz | works.xml → persons.xml | Geloest: `person_anonym` angelegt (GND 103130276) |
| Werk ohne Bibliographie | works.xml (work_6) | Geloest: Frauendienst/Frauenbuch-Split (work_6/work_7) |
| 30% Senses ohne @ana | lexicon.xml | Akzeptabel (keine Belegstellen mit Wortformen) |

---

## 6. Migration (abgeschlossen 2026-04-10)

Alle Migrationsschritte wurden in Phases F-K implementiert. Scripts sind nach Abschluss von #32 nach `scripts/_archived/` bzw. in die Git-Historie verschoben.

### Durchgefuehrte Aenderungen

| Schritt | Script | Ergebnis |
|---------|--------|----------|
| Genre-Refs entlabeln | `normalize-work-genres.py` | 3,422 `<ref>` → 870 `<ptr/>` (dedupliziert, Parent-Refs entfernt) |
| Externe IDs unwrappen | `unwrap-work-identifiers.py` | 368 `<note type="identifiers">` aufgeloest, 176x `gnd`→`GND` |
| Works-Links entfernen | `remove-person-works-links.py` | 209 `<listBibl>` aus persons.xml entfernt |
| UUID-IDs migrieren | `migrate-person-uuids.py` | 4 UUID→numerisch, Cascade in works.xml + tei/LUU.tei.xml |
| Schweizer Anonymus | `migrate-person-uuids.py` | `person_anonym` angelegt (GND 103130276) |
| Frauendienst-Split | `split-frauendienst.py` | work_6 (Frauendienst) / work_7 (Frauenbuch) getrennt |
| Verwaiste Referenzen | `fix-orphan-refs.py` | 154 variants + 61+10 lexicon Orphans entfernt |

### Script-Anpassungen

| Script | Aenderung |
|--------|-----------|
| `build-authority-index.py` | Genre-Text aus genres.xml aufgeloest; person→works aus works.xml abgeleitet; GND Casing. Versionierung siehe [TEI-MODEL.md §11](TEI-MODEL.md#11-versionierung). |
| `enhance_works_with_zotero.py` | `<biblStruct>` in `<relatedItem>` wrappen; 4 Bugs gefixt |

### 6.1 Post-Migration Ingest-Drift (WZB) und die Backfill-Luecke

Nach der #32-Migration begann der aktive Ingest. Die Wenzelsbibel-Pipeline (WZB, 2026-04 bis 2026-05) legte das Drift-Muster offen, das #115 aufdeckte:

- **Phase 1b** (Commit `5cdc98831`, 2026-04) erkannte neue Wortformen und vergab neue Lemma-IDs ≥78000. Davon kamen nur 4 (zunaechst sense-los) in `lexicon.xml`. Insgesamt fehlen heute **98 Lemma-IDs ≥78000** in `lexicon.xml` (#115): `wzb-apply-lemmarefs.py` schrieb sie als `@lemmaRef` ins Korpus, aber **kein Skript zog `lexicon.xml` nach**.
- **Phase 3** (Sense-Aufloesung) waehlte ueberwiegend bestehende Senses (<78000); die fehlenden Sense-IDs ≥78000 sind grossteils strukturelle Artefakte der Lemma-Erzeugung, keine neuen Bedeutungen.
- **Notreparatur** (Commits `8caa09627`/`649c0fe55`, 2026-05): die 4 sense-losen Lemmata bekamen manuell je einen `<sense>`; `scripts/audit/check-lexicon-senses.py` entstand als Regression-Schutz.

**Lesson** (→ [ADR-015](DECISIONS.md#adr-015-authority-source-modell-korpus-führt-ingest-braucht-rückwärts-sync), [CONTRACTS.md → F.3](CONTRACTS.md#f3-ingest-requires-backward-sync)): Eine Forward-Only-Ingest-Pipeline ohne `*-backfill-lexicon.py` erzeugt zwangslaeufig dangling Refs. Resultat: 977 unresolved Refs (349 IDs), repo-intern zu schliessen (Lemma-Stubs automatisch generierbar, Sense-Bedeutung kuratorisch). Detektor: `scripts/audit/check-authority-cross-refs.py --check` (CI-Gate in `schema-validation.yml`).

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
