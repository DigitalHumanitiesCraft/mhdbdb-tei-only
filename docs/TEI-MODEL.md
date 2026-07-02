# MHDBDB TEI Target Model (Soll-Modell)

Defines the normative TEI encoding for all texts in the MHDBDB corpus. New texts **must** conform to this model. Existing texts are migrated incrementally (see Issue #30).

**Status:** DRAFT — pending review by Katharina Zeppezauer-Wachauer
**Issue:** #32 (TEI schema)
**Schema:** `schema/mhdbdb.rnc` (RELAX NG Compact, Source of Truth) + `schema/mhdbdb.rng` (generiert via `trang`)
**Validiert gegen:** TEI P5 Version 4.11.0 (`tei_all.rng`, 18. Feb 2026)
**Maximalbeispiel:** `schema/examples/corpus.example.tei.xml` (validiert gegen tei_all.rng)

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

The header is already largely standardized across all 667 files. This section documents the canonical structure.

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
        <idno type="handschriftencensus">{HC-Nr}</idno>   <!-- optional, 354 Texte -->
        <idno type="GND">{GND-Nr}</idno>                  <!-- optional, 216 Texte -->
        <idno type="wikidata">{Q-Nr}</idno>               <!-- optional, 129 Texte, Werk-Ebene -->
        <idno type="mwb-sigle">{MWB-Kurzsigle}</idno>     <!-- optional, 19 Texte -->
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

### 2.1bis Editor-Attribution & Credits

Attribution der an der MHDBDB mitwirkenden Personen laeuft zentral ueber `authority-files/contributors.xml` (siehe [`TEI-MODEL-AUTH-FILES.md`](TEI-MODEL-AUTH-FILES.md) §3.8). Die Korpus-Header referenzieren dieses Register via `@ref`; namentlich ausgeschrieben wird im Header nur, was pro Datei variiert oder fuer Leser:innen direkt sichtbar sein soll.

**Was wohin gehoert:**

| Information | Stelle im Header | Muster |
|-------------|-----------------|--------|
| Kollektive Team-Attribution | `<titleStmt>/<respStmt>` | `<orgName ref="contributors.xml#mhdbdb-team">` |
| Gruender + Koordinatorin (immer gleich, alle 667 Dateien) | `<publicationStmt>/<authority>` | `<persName role="founder\|coordinator" ref="contributors.xml#contrib_00X">` |
| Prominente Lead-Editor:in (nur bei TKR/TKA/VTC/JT) | zweites `<titleStmt>/<respStmt>` | `<name role="lead-editor" ref="contributors.xml#contrib_00X">` |

**Beispiel (ABG nach Migration 2026-04-14):**

```xml
<titleStmt>
  <title xml:lang="de">Von abgescheidenheit (Traktat)</title>
  <author ref="#person_445">Meister Eckhart</author>
  <respStmt>
    <resp>digitale Zusammenfuehrung, Annotation und semantische Klassifikation</resp>
    <orgName ref="contributors.xml#mhdbdb-team">MHDBDB-Team (vollständige Liste in contributors.xml)</orgName>
  </respStmt>
</titleStmt>
<publicationStmt>
  <!-- ... -->
  <authority>
    <persName role="coordinator" ref="contributors.xml#contrib_003">
      <forename>Katharina</forename><surname>Zeppezauer-Wachauer</surname>
    </persName>
    <persName role="founder" ref="contributors.xml#contrib_001">
      <forename>Klaus M.</forename><surname>Schmidt</surname>
    </persName>
    <persName role="founder" ref="contributors.xml#contrib_002">
      <forename>Horst</forename><surname>Pütz</surname>
    </persName>
  </authority>
  <!-- ... -->
</publicationStmt>
```

**Zusaetzliches Muster bei Lead-Editor:innen** (aktuell TKR/TKA/VTC mit Brom, JT mit Woesner):

```xml
<titleStmt>
  <title>...</title>
  <author>...</author>
  <respStmt>
    <resp>digitale Zusammenfuehrung, Annotation und semantische Klassifikation</resp>
    <orgName ref="contributors.xml#mhdbdb-team">...</orgName>
  </respStmt>
  <respStmt>
    <resp>Haupt-Editor dieser Ausgabe</resp>
    <name role="lead-editor" ref="contributors.xml#contrib_004">Vlastimil Brom</name>
  </respStmt>
</titleStmt>
```

**Rules:**
- `<orgName>`/`<persName>`/`<name>` tragen die Attribution-Information IMMER ueber `@ref`, nicht ueber inline-Text allein. Der sichtbare Text ist eingefroren, die kanonische Quelle ist `contributors.xml`.
- `@ref` auf `<orgName>` ist fuer Organization-Records in `contributors.xml` gedacht (MHDBDB-Team, Digital Humanities Craft). Fuer Homepages einer Organisation benutzt `contributors.xml` das TEI-P5-idiomatische Pattern `<org><idno type="URL">https://...</idno></org>` statt `@ref`.
- `<persName role>` im `<authority>`-Block darf nur die fixen Rollen aus dem Authority-Schema tragen: `"founder" | "coordinator" | "lead-editor" | "editor"`.
- 50+ weitere Editor:innen, die an den Bestandstexten mitgearbeitet haben, sind nur in `contributors.xml` gelistet — NICHT inline im jeweiligen Korpus-Header, um den Header schlank zu halten.

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
    <language ident="gmh">Mittelhochdeutsch (ca. 1050-1350)</language>
    <language ident="la">Latein</language>  <!-- falls vorhanden -->
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

### 3.5 `div/@type` Werte (Audit)

15 distinkte Werte im Bestand. Die Werte stammen als 1:1-Uebersetzungen aus dem alten Datenbank-Export (Julias TEI-Doku, Juni 2024).

Vollstaendige Uebersicht aller akzeptierten Werte: siehe Tabelle "Alle div/@type Entscheidungen komplett" weiter unten.

**Designentscheidung: `song` bleibt breit, keine Differenzierung in `spruch`/`leich`**

In der mhd. Lyrik unterscheidet man fachlich zwischen Lied, Spruch und Leich. Die Frage war, ob kuenftige Ingests feiner differenzieren sollen. Entscheidung: **Nein.**

1. **Fachlich instabil:** Die Trias Lied/Spruch/Leich ist eine moderne Forschungskategorisierung, keine mittelalterliche Selbstbezeichnung. Die Abgrenzung ist in der Germanistik umstritten — Texte wechseln zwischen Formen, Zuordnungen haengen vom Forschungsstand ab (z.B. Hugo von Montfort: "Lied" oder "Rede" je nach Edition).
2. **Information existiert an besserer Stelle:** Die Gattungstypologie im `<classDecl>` hat 600+ Genre-Bezeichnungen. Dort koennen Minnelied, Spruchdichtung, Leich als Genre-Kategorien fein unterschieden werden. `div/@type` markiert die **Struktureinheit** (= nummerierte lyrische Einheit), nicht das Genre.
3. **Konsistenz ueberwiegt Praezision:** 1,373 bestehende `song`-Einheiten muessten reklassifiziert werden (nicht scriptbar, erfordert philologische Einzelentscheidungen). Bei zukuenftigen Ingests muesste jeder Text einzeln beurteilt werden.

`song` bedeutet im MHDBDB-Modell: **"nummerierte lyrische Einheit"** — bewusst breiter als die Fachterminologie. Feinere Unterscheidungen erfolgen ueber die Genre-Taxonomie im Header.

**Migration (entschieden):**

| Typ | Count | Beispiele | Aktion |
|-----|-------|-----------|--------|
| `stanza` | 1,122 | LZT | ✓ migriert zu `<lg type="stanza">` (#23, Index v4.1.1); 0 `div type="stanza"` im Korpus |
| `deed` | 300 | HZU, HZU2 | → `number` (Genre steht im Header; `deed` war Genre-Marker, nicht Strukturtyp) |
| `part` | 176 | DL2, EHB | → `section` (identische Verwendung, Migrationsrest) |
| `sermon` | 113 | ADP, ECK | → `number` (Genre steht im Header; analog zu `deed`) |
| `subsection` | 3 | KVM | → `section` (Verschachtelung statt eigenem Typ) |
| `§` | 7 | KVM | Encoding-Artefakt (Linecode-Konvertierung) → `section` |
| `sigil` | 9 | BOP | Lied-Siglen aus Edition → `number` (analog deed/sermon) |

**Logik `deed`/`sermon` → `number`:** Diese `div`-Typen markieren keine Genre-Information (die kommt aus der `<classDecl>`-Taxonomie im Header), sondern nummerierte Einheiten (Urkunde Nr. 1, Predigt Nr. 2). Der Typ `number` drueckt die Funktion korrekt aus. Bestehendes `@n` bleibt erhalten.

**Zusaetzlich: `note type="date"` und `note type="year"` in HZU/HZU2**

HZU (36 date-notes + 19 year-notes) und HZU2 (241 date-notes + 100 year-notes) tragen Datumsangaben in Urkunden:

```xml
<note type="year" n="1293"/>        <!-- Jahreszahl, klar -->
<note type="date" n="24. Februar"/> <!-- Klartext-Format, Oesterreich-Deutsch (Jaenner statt Januar) -->
```

**Historisch:** Das `n`-Attribut auf `<note type="date">` trug ein kompaktes MMTT-Encoding (Letzte zwei Stellen = Tag, Rest = Monat: `"224"` = 24. Februar, `"1211"` = 11. Dezember). Die Migration zu Klartext ist bereits erledigt (im Zuge der Phase-D-Normalisierung 2026-04, dokumentiert als #84). Stand 2026-04-15 sind alle 277 date-notes in beiden Dateien in der Klartext-Form; neue Ingests sollen diese Form direkt verwenden, nicht die alte kompakte.

**Weitere Migrationen (entschieden am 2026-04-09):**

| Typ | Count | Beispiele | Aktion |
|-----|-------|-----------|--------|
| `paragraph` | 76 | BDK | → `number` (Katharina: "weg damit, mehr Troubles als Nutzen") |
| `volume` | 7 | FLG, FLG1 | → entfernen (veraltet, nur technische Gruende; Metadaten reichen) |

**`volume` Sonderfaelle (FLG, FLG1, PL1-3):**

Katharina: "Band und Teil hatten nur veraltete technische Gruende. Kann in die Metadaten ausgelagert werden."

- **FLG** (Buch 1-2, Edition 2009) + **FLG1** (Buch 3-7, Edition 1990-93): Zusammenziehen **nicht empfohlen** — unterschiedliche Editionsgrundlagen. `div type="volume"` entfernen, Buchnummern als `div type="section"` behalten.
- **PL1/PL2/PL3** (Prosa-Lancelot): Zusammenziehen **moeglich** — identischer Aufbau (gleicher Autor, flach `<body><p>`), nur unterschiedlicher Text. Aber: 822k `<w>` gesamt = Riesendatei. Separate Dateien mit `section`-Divs statt `volume` ist pragmatischer.

**Alle `div/@type` Entscheidungen komplett:**

| Typ | Count | Beispiele | Status |
|-----|-------|-----------|--------|
| **`song`** | 1,373 | BOP, BRH | ✓ Akzeptiert |
| **`chapter`** | 604 | AC1, BDK | ✓ Akzeptiert |
| **`recipe`** | 452 | ABS, BRIX | ✓ Akzeptiert |
| **`section`** | 433 | DL1, DL2, EHB, KVM | ✓ Akzeptiert (inkl. ex-part/subsection/§) |
| **`number`** | 498 | HZU, ADP, BDK, BOP | ✓ Akzeptiert (inkl. ex-deed/sermon/sigil/paragraph) |
| **`parallel`** | 24 | BRW, DES2 | ✓ Akzeptiert (Parallelueberlieferung) |
| **`colophon`** | 15 | ALX, APO | ✓ Akzeptiert (TEI hat `<colophon>`, aber `div type` ist kompatibel) |

**Stanza-Check (verifiziert):** `div type="stanza"` existierte historisch nur in LZT (1.122) und ist seit #23/v4.1.1 zu `lg type="stanza"` migriert; aktuell **0** `div type="stanza"` im Korpus (LZT nutzt jetzt `lg type="stanza"`).

---

## 4. Wort-Element (`<w>`)

Das `<w>`-Element ist die zentrale Annotationseinheit. Im Soll-Modell stammen alle Attribute aus TEI P5 `att.linguistic` und `att.global.analytic` (seit TEI 3.3.0, Jan 2018).

> **Status (Phase B1/B2, 2026-04 — abgeschlossen):** Die früher nötigen Migrationen `@meaningRef → @ana` und `@wordRef → @corresp` sind korpusweit durchgeführt (inkl. WZB). Es gibt **0** verbleibende `@meaningRef`/`@wordRef`-Attribute, **667/667** Dateien nutzen `@ana`, und kein aktiver JS-/Python-Code liest die alten Namen (der `@meaningRef`-Treffer in `WZB.tei.xml` ist nur ein `revisionDesc`-Logeintrag, kein Attribut). Die §§4.1, 4.3, 4.4 dokumentieren das migrierte Modell und die Migrations-Historie; vgl. §10 „Frühere Fehler (alle behoben durch Migration)".

**Vorher** (Bestand bis Phase B1/B2):
```xml
<w xml:id="{SIGLE}_{page}{line}_{pos}"
   lemmaRef="lexicon.xml#lemma_{id}"
   pos="{POS-Tags}"
   meaningRef="lexicon.xml#lemma_{id}_sense_{id}"
   wordRef="lexicon.xml#lemma_{id}_sense_{id}_type_{id}">sichtbarer Text</w>
```

**Jetzt** (TEI-konform, migriert):
```xml
<w xml:id="{SIGLE}_{page}{line}_{pos}"
   lemmaRef="lexicon.xml#lemma_{id}"
   pos="{POS-Tag}"
   ana="lexicon.xml#lemma_{id}_sense_{id}"
   corresp="variants.xml#type_{id}">sichtbarer Text</w>
```

### 4.1 Attribute

| Attribut | TEI-Status | Pflicht | IST (Audit) | SOLL |
|----------|------------|---------|-------------|------|
| `@xml:id` | Standard (att.global) | ja | 9,282,982 (100%) | behalten |
| `@lemmaRef` | **Standard** (att.linguistic) | ja* | 7,391,273 (79.6%) | behalten |
| `@pos` | **Standard** (att.linguistic) | ja* | 7,406,168 (79.8%) | behalten |
| `@ana` | **Standard** (att.global.analytic) | nein | ~5.9M (migriert aus `@meaningRef`, Phase B1) | behalten |
| `@corresp` | **Standard** (att.global) | nein | ~7.5M (migriert aus `@wordRef`, Phase B2; URI → `variants.xml`) | behalten |

Korpus zum Audit-Zeitpunkt (#32, 2026-04, vor WZB): 9,282,982 `<w>`-Elemente in 666 Dateien; 20.4% ohne `@lemmaRef` (unannotierte Woerter — werden vom Corpus-Index uebersprungen, siehe CONTRACTS.md Sec. B). Aktueller Stand: 667 Dateien, 9.432.130 `<w>` (Messung 2026-06-10 fuer den Code4Lib-Artikel, #142).

> **Wichtig:** `@lemmaRef` ist seit TEI P5 3.3.0 ein Standard-Attribut der Klasse `att.linguistic` und musste **nicht** migriert werden. `@meaningRef` und `@wordRef` **waren** die Validierungsblocker (keine TEI-Standard-Attribute); sie wurden korpusweit zu `@ana` bzw. `@corresp` migriert (Phase B1/B2, abgeschlossen — 0 verbleibende Vorkommen, 667/667 Dateien mit `@ana`).

### 4.2 `@xml:id` Format

```
{SIGLE}_{Seite}{Zeile}_{Wortposition}

Beispiele:
  ABG_400001_0    (ABG, Seite 400, Zeile 001, Wort 0)
  WUT_101_0       (WUT, Zeile 101, Wort 0)  
  WZB_1ra_6_5     (WZB, Folio 1ra, Zeile 6, Wort 5)
```

Format variiert historisch bedingt. Neue Texte sollen ein konsistentes Schema verwenden. IDs muessen innerhalb eines Dokuments eindeutig sein.

### 4.3 Migrations-Plan (abgeschlossen, Phase B1/B2)

> Historischer Plan. Die Migration ist 2026-04 korpusweit durchgeführt (inkl. WZB); die Tabelle dokumentiert, was umgesetzt wurde.

| Attribut | TEI-Status | Aktion | Aufwand | Abhaengigkeit |
|----------|------------|--------|---------|---------------|
| `@lemmaRef` | Standard | **behalten** | keiner | — |
| `@pos` | Standard | **behalten** | keiner | — |
| `@meaningRef` | nicht Standard | **→ `@ana`** | gering (Rename) | Playground JS (8 Stellen, davon 2 kritisch) |
| `@wordRef` | nicht Standard | **→ `@corresp`** | gering (Rename + URI-Korrektur) | siehe Sec. 4.4 |

**Prioritaet:** `@meaningRef` → `@ana` und `@wordRef` → `@corresp` sind beide fuer TEI-Konformanz noetig. Beide sind Batch-Renames (Attributname aendern). Bei `@wordRef` muss zusaetzlich die URI korrigiert werden (siehe Sec. 4.4).

**Code-Anpassung `@meaningRef` → `@ana`** (✓ erledigt): Der aktive Playground-JS liest bereits `@ana` (querySelectorAll `[ana]`/`getAttribute('ana')`). Es gibt **0** Stellen im aktiven JS-Code, die `meaningRef`/`wordRef` lesen (bestätigt per grep über `assets/` + `playground/`, 2026-06-05). Python-Referenzen nur im archivierten `_ARCHIVED_tei-transformation.py` (nicht aktiv).

**`@lemma` bewusst nicht umgesetzt:** TEI P5 erlaubt `@lemma` (att.linguistic) als menschenlesbare Grundform direkt am Wort. Wir setzen es nicht. Begruendung:

- **Denormalisierung.** Source of Truth fuer die Grundform ist `lexicon.xml` → `<form type="lemma"><orth>`. `@lemma` waere eine redundante Kopie neben `@lemmaRef`. Das widerspricht dem Grundsatz aus [TEI-MODEL-AUTH-FILES.md](TEI-MODEL-AUTH-FILES.md) Sec. 2.2 ("Bidirektionale Links — eine Richtung ist Master, die andere wird abgeleitet"), der fuer Authority-Files gilt und hier konsequent fortgefuehrt wird.
- **Datenvolumen.** ~9,3M `<w>`-Elemente × ~10 Byte → rund 90 MB zusaetzliche Roh-XML ueber 667 Dateien ohne funktionalen Nutzen.
- **Kein Konsument.** Weder `build-corpus-index.py` (liest nur `@lemmaRef` und extrahiert die ID) noch die JS-Renderer (`text-renderer.js`, `tei-text-reader.js`) lesen `@lemma`. Die Anzeige der Grundform laeuft im Browser ueber den Authority-Index.
- **Sync-Risiko.** Jede orthografische Korrektur im Lexikon muesste in alle 667 Korpusdateien propagiert werden, sonst driften sie auseinander.

Die menschenlesbare Grundform bleibt per Lookup `@lemmaRef` → `lexicon.xml` zugaenglich — fuer Debug-Inspektion per `xmllint`/`grep`, fuer Tooling per Authority-Index.

**WZB:** Auch WZB ist migriert und nutzt `@ana` (141.978 Vorkommen). Der einzige `@meaningRef`-Treffer in `WZB.tei.xml` ist ein `<change>`-Logeintrag im `revisionDesc`, kein Attribut.

### 4.4 `@wordRef` → `@corresp`: Wortform-Referenz beibehalten (✓ abgeschlossen)

> Die Migration ist durchgeführt; dieser Abschnitt dokumentiert die Begründung (warum nicht gelöscht) und die URI-Korrektur.

`@wordRef` war kein TEI-Standard-Attribut, trug aber **nicht-rekonstruierbare Information** (daher Migration zu `@corresp` statt Löschung):

- ~21% der `<w>`-Elemente **mit** `@wordRef` haben kein `@meaningRef` (1,553,943 von 7,406,166) — ohne Sense ist der Lookup-Pfad Sense→Type unmoeglich
- 42 von 43.404 Senses haben Types mit identischem Formtext — selbst mit Sense ist Text-Matching nicht eindeutig
- `@wordRef` ist die einzige direkte Verknuepfung einer Belegstelle mit ihrer Wortform (Type) in `variants.xml`

**Referenzkette:**
```
@wordRef="lexicon.xml#lemma_2598_sense_77615_type_8717"  (vorher: synthetische URI)
    │
    ├─ lexicon.xml: <sense xml:id="lemma_2598_sense_77615" ana="#type_8717 ...">
    │
    └─ variants.xml: <form xml:id="type_8717">hân</form>
```

**Migration (✓ abgeschlossen):** `@wordRef` wurde zu `@corresp` (Standard-Attribut aus `att.global`). Dabei wurde die URI korrigiert — das Ziel liegt in `variants.xml`, nicht in `lexicon.xml`:

```
vorher:  wordRef="lexicon.xml#lemma_2598_sense_77615_type_8717"  (synthetisch, falsche Datei)
jetzt:   corresp="variants.xml#type_8717"                        (direkt, korrekte Datei)
```

**Umsetzung:** Batch-Transformation — aus der synthetischen URI den `type_{id}`-Teil extrahiert und als `variants.xml#type_{id}` gesetzt. Kein aktiver Code las `@wordRef`, daher keine JS-Anpassung nötig.

---

## 5. POS-Tagset (19 Tags)

Kanonisches Tagset fuer alle MHDBDB-Texte. Vollstaendige Referenz (Tag-Tabelle, Compound-Regeln, Legacy-Mapping, Korpus-Verteilung): [POS-TAGSET.md](POS-TAGSET.md). Der operative Disambiguierungs-Workflow ist als Agent-Skill `.gemini/skills/pos-disambiguator/` implementiert.

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

Der Altbestand nutzt ein aelteres Tagset (`ART` statt `DET`, `CNJ` statt `CCNJ`/`SCNJ`, `GRA` geht in `ADJ` auf). Vollstaendige Mapping-Tabelle und die im Korpus verbleibenden Anteile: [POS-TAGSET.md §3](POS-TAGSET.md#3-legacy-tags-altbestand). Die CNJ-Differenzierung (CCNJ vs. SCNJ) erfordert linguistische Analyse und kann nicht mechanisch erfolgen.

### 5.2 Compound-Tags

Viele `<w>`-Elemente im Altbestand tragen Compound-Tags (~35-40%) (z.B. `pos="VRB VEX"`, `pos="ART NUM"`), die Ambiguitaet ausdruecken. Der Disambiguierungs-Workflow loest diese auf einen einzelnen Tag auf; nur echte morphologische Fusionen (z.B. `wiltu` = wilt + du -> `VEM PRO`) behalten zwei Tags. Regeln und Ausnahmen: [POS-TAGSET.md §2](POS-TAGSET.md#2-compound-tags).

---

## 6. Inline-Elemente

### 6.0 Optionale Erweiterungen (seit 2026-05-08, PD-001)

Mit der ARITHMETIC-Aufnahme wurden folgende TEI-P5-Standardelemente als **optionale** Inline-Elemente ins Schema aufgenommen. Sie sind für jedes Korpus erlaubt, aber für keines vorgeschrieben. Lyrik-, Predigt- oder Rezept-Korpora müssen sie nicht nutzen. Vollständige Begründung siehe [DECISIONS.md § PD-001](DECISIONS.md).

| Kategorie | Elemente | Verwendung |
|---|---|---|
| Editorisch | `<unclear>`, `<add>`, `<gap>`, `<abbr>`, `<expan>`, `<am>`, `<g>` | Editionen mit philologischem Apparat; `<unclear>` war im Bestand früher als Kursiv-Markierung präsent |
| Onomastik | `<roleName>`, `<occupation>`, `<placeName>`, `<persName>` (Inline), `<person>` (Inline) | Personen-/Orts-Annotationen im Body |
| Domain Arithmetik | `<unit>` (`@type` = `measurement\|weight\|length\|volume\|distance`), `<rs>` (`@type` = `currency\|goods`), `<figure>` | Maßeinheiten, Währungen, Diagramme/Rechnungs-Layout |

**Erweiterungen bestehender Elemente:**
- `<w>` darf jetzt `<hi>` enthalten (Initial-Buchstaben-Pattern wie `<hi rend="initial">A</hi>in`)
- `<lb>` darf `@break="no"` haben (TEI-P5-Standard für Wort über Zeilenende)
- `<note>` darf `@place` haben und `<p>` enthalten
- `<hi>` darf wieder `<hi>` enthalten (kontrollierte Ausnahme zu ADR-013, für Carinas durchgestrichene Brüche `<hi rend="line-through"><hi rend="superscript">2</hi>/<hi rend="subscript">3</hi></hi>`)

**`<div>/@type` Enum-Erweiterung** (für Rechenbuch-Korpora): zusätzlich zu den 7 Standard-Werten 24 weitere Werte (`outline`, `commodity_calculation`, `reckoning_example`, `fraction_calculation`, `regula_de_tri`, `addition`, `multiplication`, `division`, `subtraction` u.a.). Vollständige Liste in `schema/mhdbdb.rnc` § `div.type.arithmetic`.

**Folge-Tasks** (post-Aufnahme):
- Begriffssystem-Anbindung von `<unit>` und `<rs>` über `@ana="concepts.xml#concept_NNNN"` (Mapping-Aufgabe gemeinsam mit Beitragenden)
- Reading-View-Render-Policy minimal halten: `<expan>` statt `<abbr>` anzeigen; Bruch-/Figur-/Rechnungs-Darstellung als förderbare Folge-Baustelle

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

**Migration:** 1,370,191 Vorkommen. Einfaches Batch-Rename (`<seg type="pc">` → `<pc join="left">`). JS-Rendering muss `<pc>` als Inline-Element behandeln (analog zu `<seg type="pc">`).

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

`<hi rend="initial">` ist Korpus-Konvention und kodiert dekorierte Initialen aus Handschriften/Drucken.

**Audit: `hi/@rend` Werte (666 Dateien):**

| Wert | Count |
|------|-------|
| `initial` | 314,529 |
| `upper_case_first_letter` | 92,488 |
| `upper_case` | 7,953 |
| `bold` | 201 |
| `italic` | 124 |

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

### 6.7 Spaltenumbrueche

```xml
<cb n="{Spaltennr}"/>
```

Markiert einen Spaltenumbruch (column break). Selten (996 Vorkommen in 3 Dateien). Im Rendering als `[Sp. {n}]` dargestellt.

### 6.8 Bekannte Fehler im Bestand

- **`<suppplied>`** (Tippfehler, 1 Vorkommen in 1 Datei) — muss zu `<supplied>` korrigiert werden.

---

## 7. Authority-File-Referenzen

Alle Referenzen auf kontrollierte Vokabulare verwenden relative Pfade:

| Referenz | TEI-Status | Ziel | Beispiel |
|----------|------------|------|----------|
| `@lemmaRef` | Standard | lexicon.xml | `lexicon.xml#lemma_879` |
| `@ana` (SOLL) | Standard | lexicon.xml (Sense) | `lexicon.xml#lemma_879_sense_1234` |
| ~~`@meaningRef`~~ (IST) | nicht Standard | lexicon.xml (Sense) | → wird zu `@ana` |
| `@corresp` (SOLL) | Standard | variants.xml (Type) | `variants.xml#type_8717` |
| ~~`@wordRef`~~ (IST) | nicht Standard | lexicon.xml (synthetisch) | → wird zu `@corresp` |
| `@ref` (author) | Standard | dokumentinterner `<person>` in profileDesc (-> persons.xml via `@corresp`) | `#person_445` |
| `@corresp` (msIdentifier) | Standard | works.xml | `works.xml#work_89` |
| `@corresp` (genre) | Standard | genres.xml | `genres.xml#genre_0480b285` |

**Integritaets-Constraint:** Alle referenzierten IDs muessen in den Authority-Dateien existieren. Wird zur Build-Zeit validiert.

---

## 8. Entschiedene Migrationspunkte

### 8.1 `<l>` vs `<lb/>` in Prosa — ENTSCHIEDEN: Migration

TEI P5 definiert `<l>` als "a single line of **verse**" und nutzt in Kapitel 24 (Conformance) die Umdefinition von `<l>` als "typographic line" als **explizites Negativbeispiel** fuer Non-Konformanz.

**Entscheidung:** 18 Prosa-Texte werden von `<l>` auf `<lb/>` migriert. 3 Texte behielten bei #32 ihr `<l>` mit der Begruendung "Versdichtung" — diese Einstufung war falsch (Verwechslung mit gleichnamigen Verswerken anderer Autoren) und wurde 2026-07 revidiert (#143, KZW-Entscheid 2026-06-12):

**Korrektur 2026-07 (#143): auch diese 3 sind Prosa, `<l>` → `<lb/>` konvertiert:**

| Sigle | Titel | Befund |
|-------|-------|--------|
| HMT | Buch von Troja (Hans Mair) | Prosa lt. geschichtsquellen.de/werk/3419; Verwechslungskandidat war Konrads von Wuerzburg Vers-Trojanerkrieg (Reimquote 1,6%) |
| APO | Apollonius (Heinrich Steinhoewel, 1461) | Prosa-Uebersetzung (Terrahe-Edition); Verwechslungskandidat war Heinrichs von Neustadt "Apollonius von Tyrland" (Reimquote 4,5%) |
| HH | Himmel und Hoelle | fruehmhd. rhythmische Prosa in kurzen Kola, keine Versdichtung (Reimquote 1,1%) |

Die 17 uebrigen `<l>`-basierten Kandidaten aus der #143-Heuristik (ALX, DIO, FB, FP, GWTK, MR1, MR2, PSG, PTS, RUD, TKA, TKR, WH, WLE, WRB) wurden inhaltlich geprueft (Reimprobe 18-36%, Wortdichte) und sind Versdichtung — `<l>` bleibt dort korrekt.

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

### 9.3 Validierungs-Pipeline (Zwei-Stufen)

```bash
# Stufe 1: TEI-Konformitaet (keine illegalen Attribute/Elemente)
# schema/tei_all.rng liegt im Repo (committet, TEI P5 4.11.0) -- kein Download noetig
jing schema/tei_all.rng tei/{SIGLE}.tei.xml

# Stufe 2: MHDBDB-Konformitaet (strenger, Subset von tei_all)
jing schema/mhdbdb.rnc tei/{SIGLE}.tei.xml

# 3. Referenz-Integritaet (Korpus -> Authority): dangling @lemmaRef/@ana/@corresp/@ref/@target
python scripts/audit/check-authority-cross-refs.py --check

# 4. Index-Rebuild
python scripts/build-corpus-index.py
python scripts/build-authority-index.py

# 5. Tests
npm test
```

**Schema-Dateien:**
- `schema/mhdbdb.rnc` — Source of Truth (RELAX NG Compact, hand-editiert)
- `schema/mhdbdb.rng` — generiert via `trang schema/mhdbdb.rnc schema/mhdbdb.rng` (fuer lxml/Python)
- `schema/tei_all.rng` — TEI P5 4.11.0 Referenz (gitignored, Download-Befehl oben)

**Kein ODD:** Die TEI ODD-Toolchain (Stylesheets + Roma) hat 60-80 offene Issues, ist XSLT 2.0-abhaengig (Saxon), Roma-Webinterface instabil. TEI-Konformanzkriterium 5 ("documented via ODD or **analogous documentation**") wird durch dieses Dokument (TEI-MODEL.md) + das RELAX NG Schema gemeinsam erfuellt.

---

## 10. Validierungsbaseline

### Korpus-Status (667 Dateien, Stand 2026-05-11)

| Metrik | Wert |
|--------|------|
| Dateien | 667 (aus 675 Ausgangsdateien — 9 disamb-Dateien in Base gemergt; +1 WZB-Aufnahme 2026-05-08) |
| `<w>`-Elemente | ~9.3M |
| `<pc>`-Elemente | ~1.4M (migriert aus `<seg type="pc">`) |
| `@ana`-Attribute | ~5.9M (migriert aus `@meaningRef`) |
| `@corresp`-Attribute | ~7.5M (migriert aus `@wordRef`) |
| Unannotierte `<w>` (kein `@lemmaRef`) | ~1.9M (20.4%) |

Migrationsscripts: einmalig in den Phasen A–E ausgeführt, inzwischen in `scripts/_archived/` bzw. Git-Historie nach Abschluss von #32.
Validierungsscript: `scripts/audit/validate-corpus.py` — zweistufige RelaxNG-Validierung (Stage 1 `tei_all.rng`, Stage 2 `mhdbdb.rng`/`mhdbdb-authority.rng`). Die frühere strukturelle Python-Prüfung (5 Checks) ist seit 2026-04-15 retired und durch `schema/mhdbdb.rnc` abgedeckt.

### Validierungsergebnis (Stand 2026-05-11)

**mhdbdb.rnc:** 667/667 Dateien valide gegen projektspezifisches Schema (`schema/mhdbdb.rnc`).

**tei_all.rng:** 637/667 Dateien valide gegen TEI P5 4.11.0. 30 Dateien haben bewusst dokumentierte Abweichungen, die unser Custom-Schema ueber GAP-Kommentare 1–11 explizit abdeckt. Kategorien:

| Kategorie | Dateien | Anzahl |
|-----------|---------|-------:|
| `@reason` auf `<w>` (Compound-POS-Split wie `wiltu = wilt + du`) | ABS, AC1, AC2, AC3, ADP, AGS, FLG | 7 |
| `<hi>` direkt in Block-Kontext ohne Wrapper | DAL, DBK, DBS, DKA, DKF, DKI, DKM, DKR | 8 |
| `<div>` an von tei_all nicht erwarteter Position | DES2, DJEM, LVS, PUL, RDS, RDV, RVB | 7 |
| `<w>` direkt in Block-Kontext ohne Wrapper | DDE, FDS, KAA, PKP, PUC | 5 |
| `<p>` an unerwarteter Position | LZT | 1 |
| `<head>` fehlend/unerwartet | TKR, VOR | 2 |

Diese 30 Dateien sind **keine Bugs**, sondern dokumentierte Bestandsabweichungen. Das MHDBDB-Modell ist in diesen Punkten absichtlich permissiver als strict-tei_all — die GAP-Kommentare im Schema begruenden jede Abweichung. (Das frühere Feature-Doc `032-schema-followup.md` ist nach Issue-Abschluss gelöscht; Details in der Git-Historie.)

**Hinweis WZB (Aufnahme 2026-05-08):** Die mit der Wenzelsbibel hinzugefügte 667. Datei ist sowohl stage-1- (tei_all) als auch stage-2-konform (mhdbdb) und faellt damit nicht unter die 30er-Baseline. WZB benutzt keine der GAP-Patterns aus der Tabelle oben.

Fruehere Fehler (alle behoben durch Migration):

| Fehler | Behebung |
|--------|----------|
| `@meaningRef` (5.9M) | → `@ana` (Phase B1) |
| `@wordRef` (7.5M) | → `@corresp` (Phase B2) |
| `<seg type="pc">` (1.4M) | → `<pc join="left\|right">` (Phase C1) |
| `<l>` in 18 Prosa-Texten (86k) | → `<lb/>` (Phase C2) |
| `<author>` nach `<title>` in `<monogr>` | Reihenfolge korrigiert (Phase A2) |
| `<suppplied>` Tippfehler | → `<supplied>` (Phase A3) |

### TEI-Konformanz: 5 Kriterien (TEI P5, Kapitel 24)

| # | Kriterium | Status |
|---|-----------|--------|
| 1 | Well-formed XML | ✓ |
| 2 | Valid gegen TEI-Schema | ✓ |
| 3 | Konform mit TEI Abstract Model | ✓ |
| 4 | Korrekter TEI-Namespace | ✓ |
| 5 | Dokumentiert via ODD oder Aequivalent | ✓ (TEI-MODEL.md + mhdbdb.rnc) |

**Zwei-Stufen-Validierung:**
- **Stufe 1:** `tei_all.rng` = TEI-P5-Konformitaetstest (Kriterien 1-4). Baseline: 637/667 grün.
- **Stufe 2:** `mhdbdb.rnc` = MHDBDB-Stempel. Deckt alle Bestandsmuster ab, inkl. der 30 tei_all-Abweichungen (GAPs 1–11). Baseline: 667/667 grün.

`mhdbdb.rnc` ist **kein strenges Subset** von `tei_all.rng` — es ist in einigen Punkten strikter (enumerierte `@type`-Werte, restriktivere Kindelemente) und in anderen permissiver (GAPs). Die beiden Stufen pruefen unterschiedliche Eigenschaften und sind komplementaer, nicht redundant.

### Authority Files Status (8 Dateien, Stand 2026-05-11)

| Datei | Einträge | Validierung |
|-------|----------|-------------|
| lexicon.xml | 43,754 Lemmata (+4 mit WZB-Aufnahme 2026-05-08) | tei_all ✓ · mhdbdb-authority ✓ |
| variants.xml | 42,627 Einträge (256,759 Formen) | tei_all ✓ · mhdbdb-authority ✓ |
| persons.xml | 211 Personen | tei_all ✓ · mhdbdb-authority ✓ |
| works.xml | 584 Werke (+1 work_WZB) | tei_all ✓ · mhdbdb-authority ✓ |
| concepts.xml | 567 Kategorien | tei_all ✓ · mhdbdb-authority ✓ |
| genres.xml | 615 Kategorien | tei_all ✓ · mhdbdb-authority ✓ |
| names.xml | 90 Kategorien | tei_all ✓ · mhdbdb-authority ✓ |
| contributors.xml | 51 Personen + 2 Orgs (project-internal MHDBDB-Team-Register seit #83) | tei_all ✓ · mhdbdb-authority ✓ |

Migrationsscripts: einmalig in den Phasen F–K ausgeführt, inzwischen in `scripts/_archived/` bzw. Git-Historie nach Abschluss von #32.
Schema: `schema/mhdbdb-authority.rnc` (Source) → `schema/mhdbdb-authority.rng` (generiert)

Durchgeführte Bereinigungen:
- 3,422 Genre-`<ref>` → 870 `<ptr/>` (dedupliziert, Parent-Refs entfernt)
- 368 `<note type="identifiers">` unwrapped, 176× `gnd`→`GND`
- 209 denormalisierte `<listBibl>` aus persons.xml entfernt
- 4 UUID-Personen-IDs → numerisch, 1 Person neu angelegt (Schweizer Anonymus)
- 225 verwaiste Referenzen entfernt (154 variants, 61+10 lexicon)
- Frauendienst/Frauenbuch Split (work_6/work_7)

### Bekannte Encoding-Ausnahmen und offene Daten-Lücken (#133)

Konsolidierte Liste aller bewusst nicht-normalisierten Daten-Inseln und bekannten Lücken. **Pflegeregel:** Jeder neue Ingest und jede neue bewusste Ausnahme bekommt hier einen Eintrag mit Grund und Tracking-Issue — sonst wächst Schatten-Heterogenität unsichtbar (Befund des Doku-Health-Checks 2026-06-05).

| Ausnahme / Lücke | Betroffen | Grund | Status / Tracking |
|------------------|-----------|-------|-------------------|
| Schema-GAPs 1–11 (`schema/mhdbdb.rnc`) | 30 Korpus-Dateien (Kategorien-Tabelle oben) | Bestandsdaten; Migration unverhältnismäßig teuer oder semantisch riskant — dokumentierte Ausnahmen der Daten-vor-Schema-Regel | dauerhaft; jede GAP im Schema kommentiert |
| ARI/PD-001 Domain-Elemente | 6 ARITHMETIC-Handschriften (noch nicht im Korpus) | 12 Nicht-Schema-Element-Klassen + 24 `div/@type`- + 7 `hi/@rend`-Werte aus Carinas Rechenbüchern; blockieren Stage-2-Validierung | entschieden 2026-05-08: Domain-Tags ins Schema (DECISIONS.md § PD-001); Schema-Erweiterung + Ingest ausstehend → #92 |
| lexicon.xml-Backfill | 977 dangling `@lemmaRef`-Refs / 349 Lemma-IDs ≥78000 | WZB-Forward-Ingest prägte Lemma-IDs nur ins Korpus, nicht in lexicon.xml | offen → #115 (Lemma-Stub automatisierbar, Sense-Zuordnung kuratorisch) |
| WVV Stanza-Anchors | WVV, 23 Stanzen | ungewöhnliches Linecode-Template, Anchors fehlen (#23-Followup) | offen → #110 (depends-on-human) |
| Editorische `<div>`-Hülle | HUG, KLA, PL1–PL3, MBS-Serie | Follow-up aus dem manuellen TEI-Review (#30) | offen → #138 (needs-clarification) |
| Prosa-Policy `<l>` vs. `<lb/>` | 17 l-kodierte Prosatexte | Phase C2 wandelte 18 Texte; Policy für die verbleibenden ungeklärt | offen → #143 (depends-on-human) |
| WZB `@meaningRef` (historisch) | WZB | Alt-Annotation der Erstlieferung | **gelöst** — zu `@ana` migriert; es verbleibt nur ein `revisionDesc`-Logeintrag |

---

## 11. Versionierung

**Source of Truth für Index-Versionen.** Alle anderen Promptotyping-Docs (DATA-MODEL.md, DEVELOPMENT.md, CONTRACTS.md, INDEX.md §Status, TEI-MODEL-AUTH-FILES.md) verweisen auf diese Tabelle und nennen in ihren Code-Snippets nur generische Platzhalter (`X.Y.Z`, `"1.x.x"`). Pflege bei jedem Index-Bump: hier, in `corpus-loader.js`, im Build-Skript, in INDEX.md §Status (siehe Memory `feedback_index_version_bump`).

| Artefakt | Version | Datum |
|----------|---------|-------|
| Dieses Dokument | 1.0.0 | 2026-04-10 |
| RELAX NG Schema (`schema/mhdbdb.rnc`) | 1.0.0 | 2026-04-09 |
| POS-Tagset | 1.0 (19 Tags) | 2026-03 |
| Corpus Index | 4.1.5 | 2026-07-02 |
| Authority Index | 1.4.1 | 2026-06-12 |
| Authority Schema (`schema/mhdbdb-authority.rnc`) | 1.0.0 | 2026-04-10 |

---

## 12. Konventionen fuer neue Ingests

Beim Ingest neuer Texte gelten fuer Editor-Attribution und Credits die folgenden Defaults. Sie ergaenzen die Mindestanforderungen aus §9.

**Immer gleich (in jeder neuen Datei):**

1. **Authority-Block** in `<publicationStmt>/<authority>` — drei Eintraege in dieser Reihenfolge (Koordinatorin zuerst, dann Gruender chronologisch):
   - `<persName role="coordinator" ref="contributors.xml#contrib_003">Katharina Zeppezauer-Wachauer</persName>`
   - `<persName role="founder" ref="contributors.xml#contrib_001">Klaus M. Schmidt</persName>`
   - `<persName role="founder" ref="contributors.xml#contrib_002">Horst Pütz</persName>`
2. **Kollektive Team-Attribution** in `<titleStmt>/<respStmt>`:
   - `<orgName ref="contributors.xml#mhdbdb-team">MHDBDB-Team (vollständige Liste in contributors.xml)</orgName>`

Diese drei Bausteine sind in allen 667 Bestandsdateien identisch und wurden vom Migrationsscript `scripts/_archived/migrate-header-credits.py` gesetzt (initial 666 Files am 2026-04-15, WZB beim Branch-Merge 2026-05-06 angeglichen). Bei neuen Ingests einfach aus einer Bestandsdatei oder aus `schema/examples/corpus.example.tei.xml` kopieren.

**Nicht die volle Mitwirkenden-Liste in den Header schreiben.** Die 50+ Editor:innen, die historisch an den Bestandstexten mitgearbeitet haben, leben in `contributors.xml` und sind ueber den kollektiven `mhdbdb-team`-Verweis abgedeckt. Der Header bleibt schlank.

**Spezifische Haupteditor:innen bei neuem Ingest:** Wenn ein neuer Text einen oder mehrere Haupt-Editor:innen im Heute-Sinne hat (wie Brom bei TKR/TKA/VTC oder Woesner bei JT), dann:

1. In `contributors.xml` einen neuen `<person xml:id="contrib_NNN">` mit `@role="lead-editor"` anlegen (IDs fortlaufend ab der letzten vergebenen Nummer).
2. Im neuen Korpus-Header ein zweites `<respStmt>` neben den kollektiven einfuegen:

   ```xml
   <respStmt>
     <resp>Haupt-Editor dieser Ausgabe</resp>
     <name role="lead-editor" ref="contributors.xml#contrib_NNN">Vorname Nachname</name>
   </respStmt>
   ```

3. Beide Validierungsstufen durchlaufen — `contributors.xml` gegen `mhdbdb-authority.rng`, der neue Korpus-Header gegen `mhdbdb.rng`.

**Nicht-Haupteditor:innen (einzelne Beitraege):** Wer als Editor:in an einem einzelnen Text mitgearbeitet hat, aber nicht als "Haupt-Editor:in dieser Ausgabe" sichtbar sein soll, wird nur in `contributors.xml` als `<person role="editor">` gefuehrt, ohne dass im Korpus-Header ein separater `<respStmt>` noetig ist. Die Sichtbarkeit ueber den kollektiven `mhdbdb-team`-Verweis reicht aus.

**Externe Primaertext-Provider** (z.B. Harsch/Bibliotheca Augustana, Gloning/Kochbuchkorpus, Klug/Pflanzendissertation, oder Institutionen wie Akademie Mainz / ETC Virginia / Kompetenzzentrum Trier / TITUS Frankfurt) werden **nicht** in `contributors.xml` gefuehrt — sie sind bereits im `<sourceDesc>/<listBibl>/<bibl type="digitalIntermediary">/<respStmt>` des jeweiligen Korpus-Headers dokumentiert (siehe ADR-012, Issues #35–#40). `contributors.xml` ist bewusst auf MHDBDB-interne Beteiligung beschraenkt.

---

## Referenzen

### Projekt-intern
- [CONTRACTS.md](CONTRACTS.md) -- Cross-System Contracts (Position Counting, Normalization)
- [DATA-MODEL.md](DATA-MODEL.md) -- Authority-File-Schemas, Index-Struktur
- [ARCHITECTURE.md](ARCHITECTURE.md) -- Technische Komponenten, Datenfluss
- `.gemini/skills/pos-disambiguator/SKILL.md` -- POS-Tagset-Definition und Disambiguierungs-Regeln
- `schema/examples/corpus.example.tei.xml` -- Korpus-Maximalbeispiel (validiert gegen tei_all.rng)
- `schema/examples/authority-*.example.xml` -- Authority-File-Beispiele (validiert gegen tei_all.rng + mhdbdb-authority.rnc)
- `schema/tei_all.rng` -- TEI P5 4.11.0 RELAX NG Schema (committet im Repo, kein Download noetig)

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
