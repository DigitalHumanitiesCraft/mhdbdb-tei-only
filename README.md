# MHDBDB TEI Repository

[![Code License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![Data License: CC BY-NC-SA 4.0](https://img.shields.io/badge/Data-CC%20BY--NC--SA%204.0-lightgrey.svg)](LICENSE-DATA)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20627656-blue.svg)](https://doi.org/10.5281/zenodo.20627656)

<!-- Concept-DOI 10.5281/zenodo.20627656 zeigt immer auf die neueste Version;
     Versions-DOI v1.0.0: 10.5281/zenodo.20627657 (Issue #91) -->

TEI-codierte Texte mittelhochdeutscher Literatur mit semantischen Annotationen und **zwei Web-Oberflächen** aus der [Mittelhochdeutschen Begriffsdatenbank (MHDBDB)](https://mhdbdb.plus.ac.at), Universität Salzburg.

**Live:** [Hauptseite](https://dhcraft.org/mhdbdb-tei-only/) | [Playground](https://dhcraft.org/mhdbdb-tei-only/playground/)

## Überblick

Alle Daten stammen aus der [Mittelhochdeutschen Begriffsdatenbank (MHDBDB)](https://mhdbdb.plus.ac.at) an der Universität Salzburg, einem Forschungsprojekt mit über 50 Jahren mediävistischer Text- und Begriffsforschung.

### Korpus-Inhalt
- TEI-codierte Texte mittelhochdeutscher Literatur
- Authority Files: Personen, Werke, Lexikon, Konzepte, Gattungen, Namen, Varianten (+ projektinternes Kontributoren-Register)
- Vorgebaute Indizes für schnelle Suche
- Umfassende Test-Suite mit Playwright-Integration

### Zwei Web-Oberflächen

| Aspekt | **Hauptseite** ([index.html](index.html)) | **Playground** ([playground/](playground/index.html)) |
|--------|-------------------------------------------|--------------------------------------------------------|
| **Zweck** | Öffentliche Suche & Lektüre | Erweiterte Forschung & Analyse |
| **Suche** | Einzel-Lemma mit Filtern | Mehrere Suchmodi (inkl. Multi-Lemma) |
| **Zielgruppe** | Allgemeines Publikum, Studierende | Forschende, Mediävist:innen |

Beide Interfaces nutzen vorgebaute Indizes für die Suche und laden TEI-Dateien on-demand für die Text-Anzeige.

## 📚 Dokumentation

### Für Entwickler:innen
- **[CLAUDE.md](CLAUDE.md)**: primäres Entwickler-Briefing und Projekt-Überblick
- **[docs/INDEX.md](docs/INDEX.md)**: Wissensbasis mit Verweisen auf alle Spezial-Dokumente

### Für Nutzer:innen
- Playground: integrierte Hilfe, Such-Beispiele und Authority-Daten-Browsing mit Filterung und Sortierung

## Schnellstart

### Web-Server starten
```bash
npm run serve
# Öffnet http://localhost:8080
```

### Indizes bauen (optional)
Vorgebaute Indizes sind im Repository enthalten. Zum Neubau:
```bash
npm run build              # CSS + alle Indizes + Manifest bauen
npm run build:authority    # Nur Authority-Index
npm run build:corpus       # Nur Korpus-Index
npm run build:api          # Statische JSON-API (api/) aus den Indizes
npm run validate:indices   # Generierte Indizes validieren
```

### Tests ausführen
```bash
npm test                   # Alle Tests
npm run test:ui            # Interaktives Test-UI
npm run test:headed        # Mit sichtbarem Browser
```

### Programmatischer Zugriff

**Statische JSON-API:** Alle Authority-Records und Text-Metadaten sind als zitierfähige JSON-Dateien unter [`/api/`](https://dhcraft.org/mhdbdb-tei-only/api/index.json) verfügbar, direkt von GitHub Pages serviert (kein Backend). Einstieg, URL-Schema und Beispiele: [API-Dokumentation](https://dhcraft.org/mhdbdb-tei-only/api/index.html).

TEI-Dateien referenzieren Authority-Daten über `xml:id`:
```xml
<author ref="#person_445">Meister Eckhart</author>
<w lemmaRef="lexicon.xml#lemma_879" pos="NOM" ana="lexicon.xml#lemma_879_sense_1449">brôt</w>
```

### XPath-Beispiele
```xpath
//tei:persName[@type='preferred']                    # Alle bevorzugten Personennamen
//tei:w[@lemmaRef='lexicon.xml#lemma_879']           # Alle Tokens, die auf Lemma 'brôt' verweisen
```

## Glossar

Zentrale Konzepte und ihre TEI-Repräsentation:

| Konzept | TEI-Marker | Bedeutung |
|---------|------------|-----------|
| **Token** (Wortinstanz) | `<w>` | Ein konkretes Vorkommen eines Wortes im Text |
| **Lemma** (Grundform) | `@lemmaRef` → `lexicon.xml#lemma_X` | „brôt" für die Wortform „brôtes", „vriunt" für „vriunde" |
| **Sense** (Bedeutung) | `@ana` → `lexicon.xml#lemma_X_sense_Y` | Eine von mehreren Bedeutungen eines Lemmas |
| **Konzept** (abstrakt) | `<ptr target="concepts.xml#concept_X">` in `<sense>` | Semantischer Taxonomie-Knoten, z.B. „Pflanze" |
| **Wortart** | `@pos` | NOM, VRB, ADJ, … ([19-Tag-Set](.gemini/skills/pos-disambiguator/SKILL.md)) |
| **Person / Autor** | `<author ref="#person_X">` | Historische Person (Eintrag in `persons.xml`) |
| **Werk** | `<msIdentifier corresp="works.xml#work_X">` | Literarisches Werk (Eintrag in `works.xml`) |
| **Gattung** | Verweise auf `genres.xml#genre_X` | Texttyp (Epos, Lyrik, …) |

**Hierarchie:** Ein **Token** hat ein **Lemma** (Form), optional einen **Sense** (Bedeutung), und ein Sense kann auf ein oder mehrere **Konzepte** (semantische Tags) verweisen.

Tiefergehende Details in [docs/TEI-MODEL.md](docs/TEI-MODEL.md) und [docs/DATA-MODEL.md](docs/DATA-MODEL.md).

## Authority Files

| Datei | Inhalt |
|-------|--------|
| **persons.xml** | Autor:innen und historische Personen |
| **works.xml** | Werke und Manuskript-Metadaten |
| **lexicon.xml** | Lemmata mit grammatikalischen Annotationen |
| **concepts.xml** | Semantische Konzepte (Taxonomie) |
| **genres.xml** | Literarische Gattungen (Taxonomie) |
| **names.xml** | Eigennamen mit semantischen Beziehungen |
| **variants.xml** | Orthographische Varianten, gemappt auf Lemmata |
| **contributors.xml** | Projektinternes MHDBDB-Team-Register, referenziert per `@ref` aus TEI-Headern (seit 2026-04) |

## Schema

Eigene RELAX-NG-Schemas validieren alle TEI-Dateien im Repository:

| Schema | Validiert | Dateien |
|--------|-----------|---------|
| [`mhdbdb.rnc`](schema/mhdbdb.rnc) | Korpus-Texte (`tei/*.tei.xml`) | 667 |
| [`mhdbdb-authority.rnc`](schema/mhdbdb-authority.rnc) | Authority Files (`authority-files/*.xml`) | 8 |

Die Schemas verschärfen Standard-TEI-Attribute auf MHDBDB-Konventionen (Pflicht-`@xml:id` auf `<w>`, `@join` auf `<pc>`, erlaubte `div/@type`-Werte etc.). Begründung und Design-Entscheidungen siehe [`schema/README.md`](schema/README.md).

## Architektur

### Vorgebaute Indizes

Das Repository enthält vorgebaute, komprimierte Indizes für schnelles Laden:

| Index | Inhalt |
|-------|--------|
| **authority-index.json.gz** | Die 7 durchsuchbaren Authority Files zusammengeführt (ohne `contributors.xml`) |
| **corpus-index.json.gz** | Texte mit Lemma-Positionen |

**Eigenschaften:**
- Komprimiertes JSON-Format reduziert die Download-Größe
- IndexedDB-Cache mit automatischem Ablauf
- Kein XML-Parsing-Overhead im Browser

### Technologie-Stack

- **Frontend:** Vanilla JavaScript (ES Modules), Tailwind CSS
- **Kompression:** Pako (gzip)
- **Speicherung:** Dexie.js (IndexedDB-Wrapper)
- **Tests:** Playwright
- **Build:** Python + lxml für Index-Generierung
- **Server:** http-server (npm) oder Python http.server

### Mittelhochdeutsche Normalisierung

Alle Such-Funktionen nutzen eine zentrale MHG-Zeichen-Normalisierung:
- Lange Vokale: `â→a, ê→e, î→i, ô→o, û→u`
- Umlaute: `ä→ae, ö→oe, ü→ue`
- Parität zwischen Python (Build) und JavaScript (Runtime)
- Umfassende automatisierte Test-Abdeckung

## Lizenz & Kontakt

**Lizenz (zweigeteilt):**
- **Code** (`assets/`, `scripts/`, `testing/`, Build-Konfiguration): [MIT](LICENSE) © Digital Humanities Craft OG
- **Daten** (`tei/`, `authority-files/`, `data/`): [CC BY-NC-SA 4.0](LICENSE-DATA) © Mittelhochdeutsche Begriffsdatenbank (MHDBDB), Universität Salzburg

**Kontakt:** mhdbdb@plus.ac.at | https://mhdbdb.plus.ac.at
**Projekt:** Universität Salzburg, über 50 Jahre mediävistische Forschung

## Danksagung

Dieses Projekt wurde von [CLARIAH-AT](https://clariah.at/de/) unterstützt.

CLARIAH-AT stellt essentielle Infrastruktur und Unterstützung für die digitale geisteswissenschaftliche Forschung in Österreich bereit. Wir bedanken uns ausdrücklich für diesen Beitrag.
