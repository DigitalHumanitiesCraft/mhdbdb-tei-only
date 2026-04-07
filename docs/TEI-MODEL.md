# MHDBDB TEI Target Model (Soll-Modell)

Defines the normative TEI encoding for all texts in the MHDBDB corpus. New texts **must** conform to this model. Existing texts are migrated incrementally (see Issue #30).

**Status:** DRAFT — pending review by Katharina Zeppezauer-Wachauer
**Issue:** #32 (TEI schema)
**Schema:** `schema/mhdbdb.rnc` (RELAX NG Compact, planned)
**Validiert gegen:** TEI P5 Version 4.11.0 (`tei_all.rng`, 18. Feb 2026)
**Maximalbeispiel:** `docs/TEI-MODEL-EXAMPLE.xml` (validiert gegen tei_all.rng)

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
- `<author ref>` verweist auf den `<person>`-Eintrag im selben Dokument (`profileDesc`), der via `@corresp` auf `persons.xml` verweist
- `<msIdentifier corresp>` verweist auf `works.xml` via Fragment-ID (`works.xml#work_{id}`)
- Primaeredition immer als `<biblStruct>` mit Zotero-`corresp`
- Digitale Zwischenstufen als `<bibl type="digitalIntermediary">` (ADR-012)

### 2.1a `<monogr>` Element-Reihenfolge

TEI P5 verlangt in `<monogr>`: `(author|editor)*, title+, editor*, (idno|imprint)*`. Das heisst `<author>` **vor** `<title>`, `<idno>` **nach** `<editor>`. Einige Bestandsdateien (z.B. WUT) haben die falsche Reihenfolge und scheitern an der tei_all Validierung.

### 2.2 `<encodingDesc>`

```xml
<encodingDesc>
  <projectDesc>
    <!-- Standardblock: MHDBDB-Beschreibung DE + EN -->
  </projectDesc>
  <editorialDecl>
    <!-- Standardblock: Erklaerung der lokalen Dateireferenzen DE + EN -->
    <interpretation>
      <p>Part-of-Speech-Tags folgen dem MHDBDB-Tagset (19 Tags).
         Dokumentation: .gemini/skills/pos-disambiguator/SKILL.md</p>
    </interpretation>
  </editorialDecl>
  <schemaRef key="mhdbdb" url="schema/mhdbdb.rnc"/>
  <tagsDecl>
    <rendition xml:id="in" scheme="css">font-size: 150%; font-weight: bold;</rendition>
    <rendition xml:id="uc" scheme="css">text-transform: uppercase;</rendition>
  </tagsDecl>
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
  <langUsage>
    <language ident="gmh" usage="95">Mittelhochdeutsch (ca. 1050-1350)</language>
    <language ident="la" usage="5">Latein</language>  <!-- falls vorhanden -->
  </langUsage>
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
- Strophen als `<lg>` mit `@n`. Erlaubte `@type`-Werte: `stanza`
- Optionale uebergeordnete `<div>` fuer Buecher/Abschnitte
- Bei Liedern: `<div type="song">` > `<lg type="stanza">` > `<l>`
- Zaesuren als `<caesura/>` innerhalb von `<l>` (optional, selten)

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
- `<l>` ist fuer Vers-Texte reserviert, `<lb/>` fuer Prosa-Zeilenumbrueche (ENTSCHIEDEN)
- 18 Prosa-Texte im Bestand werden migriert (`<l>` → `<lb/>`), siehe [Section 8.1](#81-l-vs-lb-in-prosa--entschieden-migration)

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

Das `<w>`-Element ist die zentrale Annotationseinheit. Im Soll-Modell stammen alle Attribute aus TEI P5 `att.linguistic` und `att.global.analytic` (seit TEI 3.3.0, Jan 2018).

**IST** (Bestand):
```xml
<w xml:id="{SIGLE}_{page}{line}_{pos}"
   lemmaRef="lexicon.xml#lemma_{id}"
   pos="{POS-Tags}"
   meaningRef="lexicon.xml#lemma_{id}_sense_{id}"
   wordRef="lexicon.xml#lemma_{id}_sense_{id}_type_{id}">sichtbarer Text</w>
```

**SOLL** (TEI-konform):
```xml
<w xml:id="{SIGLE}_{page}{line}_{pos}"
   lemmaRef="lexicon.xml#lemma_{id}"
   lemma="{Grundform}"
   pos="{POS-Tag}"
   ana="lexicon.xml#lemma_{id}_sense_{id}">sichtbarer Text</w>
```

### 4.1 Attribute

| Attribut | TEI-Status | Pflicht | IST | SOLL |
|----------|------------|---------|-----|------|
| `@xml:id` | Standard (att.global) | ja | ✓ | behalten |
| `@lemmaRef` | **Standard** (att.linguistic) | ja* | ✓ | behalten |
| `@lemma` | **Standard** (att.linguistic) | nein | **fehlt** | ergaenzen (menschenlesbare Grundform) |
| `@pos` | **Standard** (att.linguistic) | ja* | ✓ | behalten |
| `@meaningRef` | **NICHT Standard** | nein | ✓ (100% der Dateien) | → `@ana` migrieren |
| `@wordRef` | **NICHT Standard** | nein | ✓ (15% der Dateien) | entfernen (deprecated, kein Code liest es) |

*`@lemmaRef` und `@pos` sind fuer die Suchfunktion erforderlich. `<w>`-Elemente ohne `@lemmaRef` werden vom Corpus-Index uebersprungen (siehe Position-Counting-Contract, CONTRACTS.MD Sec. B).

> **Wichtig:** `@lemmaRef` ist seit TEI P5 3.3.0 ein Standard-Attribut der Klasse `att.linguistic`. Es muss **nicht** migriert werden. `@meaningRef` ist der einzige Validierungsblocker — 100% der Dateien scheitern an tei_all.rng wegen dieses Attributs.

### 4.2 `@xml:id` Format

```
{SIGLE}_{Seite}{Zeile}_{Wortposition}

Beispiele:
  ABG_400001_0    (ABG, Seite 400, Zeile 001, Wort 0)
  WUT_101_0       (WUT, Zeile 101, Wort 0)  
  WZB_1ra_6_5     (WZB, Folio 1ra, Zeile 6, Wort 5)
```

Format variiert historisch bedingt. Neue Texte sollen ein konsistentes Schema verwenden. IDs muessen innerhalb eines Dokuments eindeutig sein.

### 4.3 Migrations-Plan

| Attribut | TEI-Status | Aktion | Aufwand | Abhaengigkeit |
|----------|------------|--------|---------|---------------|
| `@lemmaRef` | Standard | **behalten** | keiner | — |
| `@pos` | Standard | **behalten** | keiner | — |
| `@lemma` | Standard | **ergaenzen** | mittel (Lookup je `<w>`) | lexicon.xml Zugriff |
| `@meaningRef` | nicht Standard | **→ `@ana`** | gering (Rename) | Playground JS (1 Stelle) |
| `@wordRef` | nicht Standard | **entfernen** | gering (Strip) | keiner (kein Code liest es) |

**Prioritaet:** `@meaningRef` → `@ana` ist die einzige Migration, die fuer TEI-Konformanz noetig ist. Sie ist ein einfaches Batch-Rename (Attributname aendern, Werte bleiben identisch). Einzige Code-Anpassung: `tei-manager.js` (1 Stelle) liest `@meaningRef` im Playground.

**`@lemma` ergaenzen** ist optional aber wertvoll: Die menschenlesbare Grundform direkt am Wort (z.B. `lemma="brôt"`) macht die XML ohne Authority-File-Lookup lesbar. Erfordert einen Lookup-Schritt beim Indexbau.

**Aufschub fuer WZB:** Die `@meaningRef` → `@ana` Migration betrifft den WZB-Branch nicht (WZB hat noch kein `@meaningRef`). Sie kann unabhaengig erfolgen.

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

Viele `<w>`-Elemente im Altbestand tragen Compound-Tags (~35-40%) (z.B. `pos="VRB VEX"`, `pos="ART NUM"`), die Ambiguitaet ausdruecken. Der POS-Disambiguator-Workflow loest diese auf einen einzelnen Tag auf.

**Ausnahme:** Morphologische Fusionen behalten zwei Tags:
- Verb + enklitisches Pronomen: `wiltu` = wilt + du -> `VEM PRO`
- Praeposition + Determinator: `zer` = ze + der -> `PRP DET`

---

## 6. Inline-Elemente

### 6.1 Interpunktion

**IST** (Bestand):
```xml
<seg xml:id="{SIGLE}_{page}{line}_{pos}" type="pc">,</seg>
```

**SOLL** (TEI P5 hat ein dediziertes Element):
```xml
<pc join="left">.</pc>
```

TEI P5 stellt `<pc>` (punctuation character) als Gegenstueck zu `<w>` bereit. Es ist Member von `att.linguistic` und unterstuetzt daher `@pos`, `@lemma` etc. — anders als `<seg type="pc">`. Das `@join`-Attribut (`left`, `right`, `both`, `no`) regelt Whitespace-Adjacenz.

**Migration:** Einfaches Batch-Rename (`<seg type="pc">` → `<pc join="left">`). JS-Rendering muss `<pc>` als Inline-Element behandeln (analog zu `<seg type="pc">`).

**Achtung:** `&lt;` und `&gt;` in `<seg type="pc">` (bzw. kuenftig `<pc>`) sind korrekte XML-Entities (Winkelklammern im Quelltext), keine Bugs.

### 6.2 Hervorhebungen

```xml
<hi rend="initial">
  <w xml:id="...">Wort</w>
</hi>

<hi rend="upper_case_first_letter">
  <w xml:id="...">Wort</w>
</hi>
```

`<hi rend="initial">` ist Korpus-Konvention (655/675 Dateien, 310.000+ Vorkommen) und kodiert dekorierte Initialen aus Handschriften/Drucken.

**Optionale Verbesserung (DTABf-Modell):** `@rendition` statt `@rend` mit zentralisierten Definitionen in `<tagsDecl>`:
```xml
<!-- Im Header: -->
<rendition xml:id="in" scheme="css">font-size: 150%;</rendition>
<!-- Im Text: -->
<hi rendition="#in"><w ...>Wort</w></hi>
```
Vorteil: Konsistente, zentral verwaltete Rendition-Definitionen statt Freitext-Werte.

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

### 6.5 Zaesur

```xml
<caesura/>
```

Markiert eine Verszeilen-Zaesur innerhalb von `<l>`. Selten (5 Dateien im Bestand).

### 6.6 Zahlen

```xml
<num>
  <w xml:id="..." pos="DIG">ccccvi</w>
</num>
```

Wrapt `<w>`-Elemente mit numerischem Inhalt (roemische Zahlen etc.). Im Rendering als `<span class="number">` dargestellt.

---

## 7. Authority-File-Referenzen

Alle Referenzen auf kontrollierte Vokabulare verwenden relative Pfade:

| Referenz | TEI-Status | Ziel | Beispiel |
|----------|------------|------|----------|
| `@lemmaRef` | Standard | lexicon.xml | `lexicon.xml#lemma_879` |
| `@ana` (SOLL) | Standard | lexicon.xml (Sense) | `lexicon.xml#lemma_879_sense_1234` |
| ~~`@meaningRef`~~ (IST) | nicht Standard | lexicon.xml (Sense) | → wird zu `@ana` |
| ~~`@wordRef`~~ | nicht Standard | lexicon.xml (Type) | → wird entfernt |
| `@ref` (author) | Standard | dokumentinterner `<person>` in profileDesc (-> persons.xml via `@corresp`) | `#person_445` |
| `@corresp` (msIdentifier) | Standard | works.xml | `works.xml#work_89` |
| `@corresp` (genre) | Standard | genres.xml | `genres.xml#genre_0480b285` |

**Integritaets-Constraint:** Alle referenzierten IDs muessen in den Authority-Dateien existieren. Wird zur Build-Zeit validiert.

---

## 8. Entschiedene Migrationspunkte

### 8.1 `<l>` vs `<lb/>` in Prosa — ENTSCHIEDEN: Migration

TEI P5 definiert `<l>` als "a single line of **verse**" und nutzt in Kapitel 24 (Conformance) die Umdefinition von `<l>` als "typographic line" als **explizites Negativbeispiel** fuer Non-Konformanz.

**Entscheidung:** 18 Prosa-Texte werden von `<l>` auf `<lb/>` migriert. 3 urspruenglich als Prosa eingestufte Texte behalten `<l>`, weil sie Versdichtung sind.

**Korrektur Genre-Zuordnung (`<l>` bleibt korrekt):**

| Sigle | Titel | Begruendung |
|-------|-------|-------------|
| HMT | Buch von Troja | Klassisches Versepos |
| APO | Apollonius von Tyrus | Klassisches Versepos |
| HH | Himmel und Hoelle | Religioese Versdichtung |

**Zu migrieren (`<l>` → `<lb/>`):** 18 Dateien

| Sigle | Titel | Gruppe |
|-------|-------|--------|
| PL1 | Prosa-Lancelot | Prosa-Roman |
| PL2 | Prosa-Lancelot | Prosa-Roman |
| PL3 | Prosa-Lancelot | Prosa-Roman |
| FLG1 | Das fliessende Licht der Gottheit (Buch 3-7) | Mystik |
| VTC | Vita Caroli Quarti Imperatoris | Chronik |
| NBU | Dat nuwe Boych | Chronik |
| PUC | Pulkava Chronik | Chronik |
| ESB | Engelthaler Schwesternbuch | Chronik |
| LUU | Lehre und Unterweisung | Baemler-Druck 1476 |
| EHB | Ehbuechlein | Baemler-Druck 1476 |
| EB1 | Erstes Ehbuechlein | Baemler-Druck 1476 |
| EB2 | Zweites Ehbuechlein | Baemler-Druck 1476 |
| MSP | Der menschen spiegel | Baemler-Druck 1476 |
| PRJ | Processus juris | Baemler-Druck 1476 |
| REG | Register der Augsburger Sittenlehre | Baemler-Druck 1476 |
| ATF | Facetiae Latinae et Germanicae | Sonstige |
| SPH | Der Stein philosophorum | Sonstige |
| WGI | Der Welsche Gast (Prosavorrede) | Sonstige |

**Hinweis:** Die Baemler-1476-Gruppe (7 Texte) faellt auf — zwei weitere Texte desselben Drucks (FAN, NST) nutzen bereits korrekt `<lb/>`.

**Migration:** `<l n="X">content</l>` → `<lb n="X"/>content`. JS-Anpassung: 2 Stellen (`tei-text-reader.js`, `tei-manager.js`).

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

- [ ] `@ana` fuer semantische Suche (Verweis auf Sense in lexicon.xml)
- [ ] `<pb>` fuer Seiten-/Folio-Referenzen
- [ ] `<bibl type="digitalIntermediary">` fuer Provenienz-Kette
- [ ] Handschriftencensus-Nr. in `<msIdentifier>`
- [ ] GND/Wikidata-IDs fuer Autor und Werk

### 9.3 Validierungs-Pipeline

```bash
# 1. Schema-Validierung — TODO: schema/mhdbdb.rnc existiert noch nicht
# jing schema/mhdbdb.rnc tei/{SIGLE}.tei.xml

# 2. Referenz-Integritaet (Authority-Files) — Script geplant, noch nicht verfuegbar
# python scripts/validate-references.py tei/{SIGLE}.tei.xml

# 3. Index-Rebuild
python scripts/build-corpus-index.py
python scripts/build-authority-index.py

# 4. Tests
npm test
```

---

## 10. Validierungsbaseline (tei_all.rng)

Ergebnis der Validierung von 100 Dateien gegen TEI P5 4.11.0 (`schema/tei_all.rng`):

**0/100 Dateien valide.** Fehlertypen:

| Fehler | Dateien | Ursache |
|--------|---------|---------|
| `Invalid attribute meaningRef for element w` | 100/100 | Nicht-Standard-Attribut |
| `Invalid attribute wordRef for element w` | 15/100 | Nicht-Standard-Attribut (nur Dateien ohne POS-Disambiguierung) |
| `<author>` nach `<title>` in `<monogr>` | vereinzelt | Falsche Element-Reihenfolge |
| `Element listPerson failed to validate content` | 1 (VOR) | Einzelfall |

**Konsequenz:** Eine einzige Batch-Operation (`@meaningRef` → `@ana`) wuerde den Grossteil des Korpus TEI-konform machen. Die `.disamb.tei.xml`-Dateien enthalten `@wordRef` weiterhin — der POS-Disambiguator aendert dieses Attribut nicht.

### TEI-Konformanz: 5 Kriterien (TEI P5, Kapitel 24)

1. Well-formed XML ✓
2. Valid gegen TEI-abgeleitetes Schema ✗ (`@meaningRef` blockiert)
3. Konform mit TEI Abstract Model ✗ (`<l>` in Prosa — Migration der 18 Dateien beschlossen, Sec. 8.1)
4. Korrekter TEI-Namespace ✓
5. Dokumentiert via ODD oder Aequivalent ✗ (kein ODD, dieses Dokument ist der Ersatz)

---

## 11. Versionierung

| Artefakt | Version | Datum |
|----------|---------|-------|
| Dieses Dokument | 0.1.0 (DRAFT) | 2026-04-07 |
| RELAX NG Schema | -- (geplant) | -- |
| POS-Tagset | 1.0 (19 Tags) | 2026-03 |
| Corpus Index | 4.0.0 | 2026-02 |
| Authority Index | 1.1.0 | 2026-02 |

---

## Referenzen

### Projekt-intern
- [CONTRACTS.MD](CONTRACTS.MD) -- Cross-System Contracts (Position Counting, Normalization)
- [DATA-MODEL.MD](DATA-MODEL.MD) -- Authority-File-Schemas, Index-Struktur
- [ARCHITECTURE.MD](ARCHITECTURE.MD) -- Technische Komponenten, Datenfluss
- [features/030-tei-structural-fixes.md](features/030-tei-structural-fixes.md) -- Triage-Plan fuer strukturelle Fixes
- `.gemini/skills/pos-disambiguator/SKILL.md` -- POS-Tagset-Definition und Disambiguierungs-Regeln
- `docs/TEI-MODEL-EXAMPLE.xml` -- Maximalbeispiel (validiert gegen tei_all.rng)
- `schema/tei_all.rng` -- TEI P5 4.11.0 RELAX NG Schema (Validierungs-Referenz)

### TEI P5 Spezifikation
- [att.linguistic](https://www.tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.linguistic.html) -- `@lemma`, `@lemmaRef`, `@pos`, `@msd`, `@join`
- [att.global.analytic](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.global.analytic.html) -- `@ana` (Ersatz fuer `@meaningRef`)
- [Element `<w>`](https://www.tei-c.org/release/doc/tei-p5-doc/en/html/ref-w.html) -- Wort-Element
- [Element `<pc>`](https://www.tei-c.org/release/doc/tei-p5-doc/en/html/ref-pc.html) -- Interpunktions-Element (Ersatz fuer `<seg type="pc">`)
- [Element `<l>`](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-l.html) -- "a single line of verse" (nicht fuer Prosa)
- [Element `<lb/>`](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-lb.html) -- "line beginning" (fuer Zeilenumbrueche)
- [Kapitel 24: Conformance](https://tei-c.org/release/doc/tei-p5-doc/en/html/USE.html) -- 5 Konformanzkriterien

### Vergleichsprojekte
- [DTABf (Deutsches Textarchiv)](https://www.deutschestextarchiv.de/doku/basisformat/) -- Gold-Standard fuer historische deutsche Texte
- [MENOTA (Medieval Nordic Text Archive)](https://www.menota.org/HB3_ch11.xml) -- Mittelalterliche Texte mit Custom-Namespace-Erweiterungen
- [ReM (Referenzkorpus Mittelhochdeutsch)](https://www.linguistics.rub.de/rem/) -- MHG-Korpus mit HiTS-Tagset
