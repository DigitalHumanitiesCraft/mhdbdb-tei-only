# MHDBDB TEI Repository – Jahresbericht 2025

**Projektzeitraum:** April–Dezember 2025
**Projektkontext:** CLARIAH-AT (UX/UI-Schwerpunkt)

---

## Zusammenfassung

Das Jahr 2025 brachte die Transformation des MHDBDB TEI Repository von einem experimentellen Prototyp zu einer produktionsreifen Forschungsplattform. Der Fokus lag auf Benutzerfreundlichkeit und Performance – zwei Bereiche, die für die akademische Zielgruppe (Mediävisten, Studierende) entscheidend sind.

---

## Hauptarbeiten mit UX/UI-Relevanz

### Leseansicht mit Multi-Lemma-Highlighting (Oktober)
*Aufwand: 20 Stunden*

Die neue Leseansicht ermöglicht das immersive Lesen mittelhochdeutscher Texte mit farbcodierter Hervorhebung mehrerer Lemmata gleichzeitig (bis zu 5 Farben). Nutzer können zwischen Fundstellen navigieren und sehen kontextbezogene Metadaten (Autor, Werk, Wikidata-Bilder) direkt neben dem Text. Die 3-Spalten-Ansicht (Suche – Ergebnisse – Text) wurde für Desktop-Workflows optimiert.

### Performance-Migration: XML zu JSON-Indizes (September–Oktober)
*Aufwand: 24 Stunden*

Die ursprüngliche Architektur lud 47 MB XML-Dateien direkt im Browser – mit Ladezeiten von 30 Sekunden. Die Migration auf vorberechnete JSON-Indizes reduzierte die Downloadgröße um das 19-fache (auf 2,9 MB komprimiert). Für Nutzer bedeutet das: sofortiger Start statt minutenlangem Warten.

### Modulare UI-Architektur / Phase 7 Refactoring (Oktober)
*Aufwand: 16 Stunden*

Der Playground wurde von drei monolithischen JavaScript-Dateien (je 1.500–2.800 Zeilen) in 18 spezialisierte Module zerlegt. Für Nutzer unsichtbar, aber die Basis für zukünftige Feature-Entwicklung – und 5.536 Zeilen weniger Code.

### TEI-Strukturelemente im Rendering (November)
*Aufwand: 8 Stunden*

Mittelalterliche Texte haben komplexe Strukturen: Strophen, Zäsuren, Spaltenumbrüche, Editoreneinschübe. Diese werden jetzt korrekt dargestellt, was die philologische Nutzbarkeit erhöht.

### Zotero-Integration für bibliographische Metadaten (Oktober)
*Aufwand: 6 Stunden*

Automatischer Abgleich mit der Zotero-Bibliothek der MHDBDB (580+ Werke). Titel werden in deutsche Titelschreibung konvertiert, alle bibliographischen Felder (Reihe, Band, Ausgabe) werden extrahiert. Nutzer sehen vollständige Literaturangaben ohne manuelle Pflege.

### Responsive Navigation und Footer-Vereinheitlichung (Oktober–November)
*Aufwand: 6 Stunden*

Einheitliches Navigationsmenü über alle Seiten, konsistente Fußzeilen mit Cache-Management-Button. Kleine Änderungen, die das professionelle Erscheinungsbild abrunden.

---

## Datenarchitektur-Migration (Initial Data Wrangling)

### Reverse Engineering: RDF/Oracle → TEI-Only (April–Juli)
*Aufwand: 100 Stunden*

Die aufwändigste Arbeit des Projekts. Die MHDBDB hat eine 30-jährige Geschichte mit drei überlagerten Datenmodellen:
1. **Relationales Modell** – Oracle-DB der 90er, Excel-Tabellen
2. **Graphenbasierte Erweiterung** – Linked Data als .ttl-Dateien (Autoren, Werke, Metadaten)
3. **Hierarchische Strukturen** – TEI/XML pro Text

Bevor migriert werden konnte, musste das bestehende Datenmodell erst verstanden werden – inklusive Erstellung eines ER-Diagramms und Dokumentation der (teils undokumentierten) Relationen.

**Technische Umsetzung:**
- 6 komplexe SPARQL-Queries für GraphDB-Extraktion (Persons, Works, Lemmas, Concepts, Genres, Names)
- CSV-Export und Validierung der extrahierten Daten
- Python-Transformationsskripte für CSV → TEI-XML
- Mapping der Linked-Data-Strukturen (dhpluso:role, skos:broader, owl:sameAs) auf TEI-Elemente

Die Migration erforderte das Nachvollziehen komplexer Verknüpfungen:
- **Werk-Metadaten:** mhdbdbMeta/{sigle}.ttl → work_{id}.ttl → person_{id}.ttl → GND/Wikidata
- **Lemma-Referenzen:** Jedes @lemmaRef verwies auf .ttl → Senses → Concepts in vocab/
- **Externe Identifier:** GND, Wikidata, Handschriftencensus

**Ergebnis – 7 TEI Authority Files:**
- **works.xml** – Alle Siglen, Titel, biblStruct aus Zotero
- **persons.xml** – Autorendaten mit GND/Wikidata
- **lexicon.xml** – 32 MB, Worttypen, Senses
- **concepts.xml** – Semantische Taxonomie mit Hierarchien
- **genres.xml** – Gattungstaxonomie
- **names.xml** – Onomastisches System
- **variants.xml** – 176.000 orthographische Varianten

Diese Architektur-Migration war die Voraussetzung für alle späteren Features.

---

## Weitere technische Arbeiten

- **Corpus Index v4.0.0** – Dokumentbasierte Wortindizierung für präzise Proximity-Suche
- **IndexedDB-Caching** – 30-Tage-Expiration für Referenzdaten, persistente Speicherung für Nutzerdaten
- **3-stufige Lemma-Auflösung** – Exakte Suche, Variantenwörterbuch (176.000 Einträge), Fuzzy-Fallback
- **Playwright-Testsuite** – 40 automatisierte Tests für Qualitätssicherung
- **MHG-Zeichennormalisierung** – Einheitliche Suche trotz historischer Schreibvarianten (â→a, ô→o, ü→ue)

---

## UX/UI-Schwerpunkte im Überblick

| Feature | UX-Wirkung |
|---------|------------|
| Leseansicht mit Highlighting | Forschungsworkflow ohne Medienbruch |
| JSON-Index-Migration | Ladezeit von 30s auf <3s reduziert |
| Browser-Level-Scrolling | Natürliche Navigation statt Container-Scrollbars |
| Multi-Lemma-Deduplizierung | Klare Ergebnisdarstellung ohne Duplikate |
| Wikidata-Bildintegration | Visuelle Anreicherung der Metadaten |
| Text-Selektions-Interface | Gezielte Korpusauswahl per Checkbox |

---

## Zeitlicher Verlauf

**April–Juni:** Grundlagenarbeit (erste funktionierende Version, Playground-Prototyp, Authority-Files-Integration)

**Juli:** Datenbereinigung (works.xml, Siglen, Zotero-Titel)

**September:** Performance-Optimierung (IndexedDB, Multi-Lemma-Suche, Variantenextraktion)

**Oktober:** Hauptentwicklungsphase (Leseansicht, JSON-Migration, Modularisierung, Testsuite)

**November:** Feinschliff (TEI-Rendering, Navigation, Lemma-Disambiguierung)

**Dezember:** Datenpflege und Strukturkorrekturen

---

**Gesamtaufwand:** 180 Stunden (ohne POS-Arbeiten)

**Kontakt:** mhdbdb@plus.ac.at
