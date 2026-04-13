---
title: Hilfe-Seiten in DH-Korpusprojekten – Best-Practice-Recherche
status: Recherche-Artefakt, nicht Teil der stabilen Doku
date: 2026-04-13
scope: Vorarbeit für /hilfe/ auf mhdbdb-tei-only
---

> **Hinweis:** Dieses Dokument ist ein temporäres Recherche-Artefakt. Es dient als Entscheidungsgrundlage für die Struktur der MHDBDB-Hilfe und wird nach Umsetzung archiviert (Git-History). Nicht in INDEX.MD verlinken.

## 1. Vergleichstabelle

| Projekt | Ort der Hilfe | Struktur | Einstieg (Task/Feature) | Pflegezustand | Stärken | Schwächen |
|---|---|---|---|---|---|---|
| **Deutsches Textarchiv (DTA)** – `deutschestextarchiv.de/doku/DDC-suche_hilfe` | Menüpunkt „Dokumentation" + Inline-Link „Hilfe" neben der Suchzeile | Hierarchischer Referenz-Guide mit TOC; Tabellen statt Screenshots; Abfrage → Ergebnis → Kommentar | überwiegend Feature („Operator X macht Y") mit eingebetteten Task-Beispielen | **Veraltet**, Hinweis sinngemäß „seit 2018 nicht mehr betreut"; verweist auf DWDS-Doku | Inline-Zugriff bei der Suche; verständliche Tabellen-Didaktik | Explizite Deprecation; keine Screenshots; sehr linguistisch-akademisch (POS, XPath, Regex); naheliegender Deeplink `/doku/hilfe` liefert 404, nur `/doku/DDC-suche_hilfe` funktioniert |
| **correspSearch** – `correspsearch.net/en/help.html` + `FAQ.html` + `videos.html` + `manual.html` | Eigener Menüpunkt „Help", außerdem FAQ, Video-Tutorials, Manual, CMIF Creator/Check | Hybrid: mehrere parallele Eintrittspunkte (Help-Hub + FAQ + Videos + Manual + Changelog + Citation) | **ausgewogen**: Task-Sektionen („Participate", „Search", „API") neben Feature-Dokumentation der Tools | Aktiv (DFG-gefördert), Changelog-Seite, zweisprachig DE/EN | Mehrkanalig (Lesen/Video/FAQ), Changelog sichtbar, Zitationshinweis, echte Zweisprachigkeit | Kein „last updated" pro Seite; Aufsplittung in 6 Seiten erschwert Orientierung |
| **Perseus Digital Library** – `perseus.tufts.edu/hopper/help` | Dedizierte Help-Landing mit Unterseiten (Texts Help, Search Help, Vocab Tool) | Hierarchisch; FAQ + Feature-Guides + Archiv älterer Versionen | Feature-orientiert; FAQ erschließt Tasks | **Stark veraltet**: FAQ „updated May 2016"; Link auf geschlossene „Yahoo! Groups"; archivierte Legacy-Seiten unter derselben URL | Dedizierte URL, klare Rubriken pro Tool | Tote Links, 10 Jahre alte FAQ, kein Unterschied zwischen aktueller und superseded Doku |
| **Middle English Dictionary (MED)** – `quod.lib.umich.edu/m/middle-english-dictionary/help` | Eigener `/help`-Pfad mit Unterseiten pro Suchmodus (dictionary, extended, quotations, bibliography) | Reine Referenz: eine Seite je Suchfeld/Operator | **Feature-orientiert** („Dictionary search options", „Extended search options") | Offenbar statisches HTML in der Library-Infrastruktur; kein Datum sichtbar; 403 auf Teilen (Bot-Block) | Klare 1:1-Zuordnung Feature ↔ Hilfeseite; stabile URLs | Keine Task-Einstiege („Wie finde ich Belege für *trouthe* bei Chaucer?"); keine Screenshots; keine Updates sichtbar |
| **TEI Guidelines / tei-c.org** – `tei-c.org/support/learn/` | Menüpunkt „Support → Learn" | 5 klar getrennte Pfade: Intro, „Teach Yourself TEI", XML-Gentle-Intro, ODD-Orientierung, Bibliographie | **Lernpfad-orientiert** (Anfänger → Fortgeschrittene); keine FAQ | Community-gepflegt, „welcomes additions"; Verweis auf TEIGarage/Roma; aktiv | Klare Zielgruppen-Staffelung, mehrere Lernpfade nebeneinander | Keine schnellen Task-Antworten, stark dokumentationslastig; kein zentrales „last updated" |
| **ReM – Referenzkorpus Mittelhochdeutsch** – `linguistics.ruhr-uni-bochum.de/rem/` | Menüpunkt „Dokumentation" mit Unterseiten + „Korpus-Handbuch" | Handbuch + technische Guides (Annotation, Lemmatisierung, Morphologie) + ANNIS-Zugang | **Task-orientiert** (Übersicht, Dokumentation, Zugang, Publikationen) | „Last update: 2025-12-05" sichtbar – gepflegt | Datumsanzeige, strukturiertes Handbuch, naher Use Case zu MHDBDB | Nur Deutsch (Suche EN teilweise), keine FAQ, keine Videos, kein Tutorial-Einstieg für Nicht-Linguist:innen |
| **TextGrid Repository** – `textgridrep.org` → „Documentation" | Eigener Menüpunkt „Documentation", flache Liste mit 9 Einträgen | Flache Einzelseiten: Mission, Search (Syntax), Shelf, Download, Publication, Voyant, Switchboard, Annotate, Errata | **Feature-orientiert** (eine Seite je UI-Baustein) + separater Errata-Kanal | Footer „© 2026", keine per-Seite-Daten; DE/EN-Umschalter | Errata-Seite als expliziter Fehlertracker; klare 1:1-Abbildung UI → Doku | Keine übergreifenden Tasks („Wie publiziere ich ein Werk?"), kein FAQ, keine Lernreihenfolge |
| **Mittelhochdeutsches Wörterbuch (MWB), Trier/Mainz** – `mhdwb-online.de/hinweise.html` (eigenständiges Wörterbuchprojekt; BMZ, Lexer etc. liegen separat im Wörterbuchnetz unter `woerterbuchnetz.de`) | Einzelner Menüpunkt „Hinweise" neben Lemmaliste/Wörterbuch/Quellen/Textarchiv | Eine einzige HTML-Seite, fünf Absätze (Lemmaliste, Wörterbuch, Belegarchiv, Quellen, Textarchiv) | **Feature-orientiert**, Komponente für Komponente; keine Tasks, keine FAQ | „Last change: Dezember 2025" im Footer – gepflegt, Print-Publikationsrhythmus sichtbar | Datumsangabe, enge Zielgruppennähe zu MHDBDB, adressiert Lemmatisierungs-Unschärfe ehrlich | Dichte Absätze, keine Screenshots, keine Videos, keine Einstiegsszenarien; strukturell sehr ähnlich zu ReM – dieselbe Stärke (Datum, Pflege) und dieselben Schwächen (monolithisch, Linguist:innen-Register) |
| **Monasterium.net** – `monasterium.net/mom/help` + `monasterium.net/mom/editmom-documentation` + GitHub-Wiki | Top-Menü-Link „Help" auf der Anwendungsseite; zusätzlich separate EditMOM-Doku-Seite und externer GitHub-Wiki; Screencast-Verweise | Mehrkanalig, aber zerfasert: knappe Help-Landingpage + umfangreiche Editor-Referenz (EditMOM) + Wiki + Screencasts; keine FAQ | **Gemischt**: Help-Seite task-nah (Suchen, Registrieren, Annotieren), EditMOM rein feature-/feldorientiert (TEI/XML-Attribute) | Kein per-Seite-Datum; Hinweis „Internet Explorer ab Version 9" deutet auf jahrealte Pflegelücke; 12-Sprachen-Umschalter der Oberfläche, Doku selbst aber englisch | Mehrere Kanäle (Help, Editor-Doku, Wiki, Screencasts), echte Task-Ansprache für Mitwirkende, mehrsprachige UI | Hilfe über 3+ Orte verteilt, kein zentraler Hub; Altlasten (IE9-Hinweis); Screencasts nur referenziert, nicht eingebettet; keine Frische-Signale |

Nicht erreichbar bzw. durch Bot-Schutz blockiert während der Recherche: Perseus-FAQ-Quellseite (403 auf Detailpfad), MED-Unterseiten (403 – Inhalte über Google-Cache/Suchindex rekonstruiert), ReM-Handbuch-Unterpfad (404 auf Handbuch-Verzeichnislisting). Zusätzlich als Kandidat erwogen, aber nicht in die Tabelle aufgenommen, da die Hilfeseiten nicht auffindbar waren: Fontane-Notizbücher (301 → 404). Diese Befunde sind bereits ein Indikator: Hilfeseiten, die gegen Crawler abgeschottet sind, sind auch für LLM-gestützte Assistenzwerkzeuge schwer zu nutzen.

## 2. Anti-Patterns in DH-Hilfeseiten

Wiederkehrende Fehlermuster, die während der Recherche auftraten:

1. **Veraltete Doku ohne Entfernung.** Perseus’ FAQ „updated May 2016"; DTA-Suche-Hilfe mit dem sinngemäßen Hinweis, dass die Seite seit 2018 nicht mehr betreut wird – aber beide Seiten bleiben unter der primären URL auffindbar. Nutzer:innen landen zuerst dort. *Konsequenz:* entweder löschen/umleiten oder Banner ganz oben.
2. **Tote Community-Links.** Perseus verweist auf geschlossene Yahoo! Groups. Klassiker: Foren/Mailing­listen, die vor 5–10 Jahren relevant waren, werden nicht aktualisiert.
3. **Feature-Liste statt Task-Guides.** MED, MWB, TextGrid und teilweise DTA erklären, *was* ein Bedienelement tut, aber nicht, *wie man zu einem Forschungsergebnis kommt*. „Search field accepts Boolean operators" beantwortet keine medievalistische Frage.
4. **Fehlende Zielgruppendifferenzierung.** Kein Projekt außer TEI Guidelines trennt explizit Anfänger:innen von Forschenden. MHDBDB hat de facto drei Zielgruppen (Studierende, Medievalist:innen, Entwickler:innen), die unterschiedliche Einstiege brauchen.
5. **Versteckte oder zerfaserte Hilfe.** TextGrid und ReM binden Hilfe sinnvoll ins Hauptmenü ein; Perseus hat zwar `/help`, aber keinen prominenten Header-Link von der Landing. Monasterium zeigt die Gegenvariante – nicht versteckt, aber über `/mom/help`, eine separate EditMOM-Doku und einen externen GitHub-Wiki verteilt, ohne zentralen Hub. DTA steht zwischen den Stühlen: Top-Level-Menü „Dokumentation" plus Inline-Link bei der Suche sind solide, aber der naheliegendste Deeplink `/doku/hilfe` liefert einen 404 – Broken Canonical.
6. **Keine Updatedaten pro Seite.** Nur ReM und MWB zeigen ein globales „Last update"; correspSearch verlinkt zusätzlich einen Changelog. Perseus/MED/TextGrid/DTA/Monasterium bieten keine Frische-Signale pro Seite – Nutzer:innen können nicht beurteilen, ob der Screenshot noch zur aktuellen UI passt.
7. **Outdated Screenshots.** Perseus und MED nutzen Screenshots aus älteren UI-Generationen, ohne Kennzeichnung, dass das Bild nicht mehr zur aktuellen Oberfläche passt. Saubere Auswege: der correspSearch-Mittelweg (Videos + Text) oder DTAs konsequenter Verzicht zugunsten präziser Tabellen- und Textbeschreibungen. Nicht der Verzicht an sich ist das Problem – nur der unbemerkt veraltete Stand.
8. **DE/EN-Mischmasch.** ReM ist nur Deutsch mit halber englischer Oberfläche. correspSearch ist sauber zweisprachig. Halblokalisierung ist schlechter als monolinguale Ehrlichkeit.
9. **PDF-only Doku.** Viele linguistische Korpora packen die eigentliche Hilfe in ein PDF – nicht durchsuchbar, nicht deeplinkbar, nicht zitierbar mit Anchor. (Für das ReM-Handbuch konnte das Format im Rahmen dieser Recherche nicht verifiziert werden – der Direktpfad lieferte 404.)
10. **Fehlende Zitationshinweise.** Nur correspSearch hat eine eigene „Recommended citation"-Seite im Hilfebereich. Für DH-Korpora ist das eine Schlüsselanforderung.
11. **Fossile Systemhinweise.** Monasteriums Help-Seite nennt „Internet Explorer ab Version 9" als Anforderung – ein Browser-Hinweis, der seit mindestens einem Jahrzehnt obsolet ist. Solche Artefakte signalisieren Nutzer:innen unzuverlässig, ob der Rest der Seite noch stimmt. *Konsequenz:* Systemhinweise gehören an eine einzige Stelle und werden mit Releases mitgepflegt, sonst weg damit.

## 3. Empfehlungen für MHDBDB

### (a) Struktur: Hybrid aus Task-Einstieg und schlanker Referenz
Ein einziger Hub `/hilfe/` mit drei Säulen: **„Erste Schritte"** (Task-Szenarien), **„Nachschlagen"** (Feature-Referenz pro UI-Element), **„Hintergrund"** (Datenbasis, Zitation, Lizenz). Kein zerfasertes Netz à la correspSearch (6 Seiten), aber auch keine einzelne Wall-of-Text wie DTA. Als Leitbild: **ReM-Gliederung (task-orientiert) + correspSearch-Zitationsseite + MEDs Eindeutigkeit pro Feature**.

### (b) Ort und URL
`/hilfe/` als deutschsprachige Haupt-URL. Kein vollständiger englischer Spiegel – die englischsprachige Entwickler:innen-Dokumentation konzentriert sich auf den Unterbaum `/hilfe/fuer-entwickler/` (siehe Abschnitt 4) und vermeidet so die doppelte Pflege, an der halblokalisierte Korpora erfahrungsgemäß verrotten. Prominenter Header-Link – nicht nur unter `/help` auffindbar wie bei Perseus (siehe AP #5). Zusätzlich **kontextuelle Inline-Links** an jeder komplexen UI-Stelle (Suchzeile, Proximity-Modus, Reading View): ein Fragezeichen-Icon, das direkt zum passenden Abschnitt in `/hilfe/` springt (DTA macht das gut mit dem Inline-Link neben der Suche).

### (c) Tonalität: akademisches Deutsch, ohne Fachjargon-Wand
Primärsprache Deutsch (deckt Studierende und DACH-Medievalistik ab). Stil: sachlich, vollständige Sätze, aber mit Beispielen aus dem Korpus (*minne*, *vriunt*, *êre*) statt abstrakter Platzhalter. **Keine Emojis, keine Marketing-Sprache.** Fachbegriffe (Lemma, Variante, Konkordanz, POS) werden beim ersten Auftreten kurz erklärt, danach verwendet. Englisch nur für die Entwickler:innen-Abschnitte unter `/hilfe/fuer-entwickler/` (API, Index-Schema, Build). **Nicht der ReM-Fehler**: halbe englische Oberfläche, halbe deutsche Doku.

### (d) Wartungskonvention
- **Ein Ort, ein Owner.** Hilfe-Quellen liegen als Markdown in `docs/hilfe/` und werden beim Build zu statischen HTML-Seiten. Der Build-Step ist neu anzulegen – im aktuellen `scripts/`-Ordner gibt es nur Daten-Index-Builder, keinen MD-zu-HTML-Konverter. Kein Wiki, kein externes CMS.
- **„Stand"-Zeile pro Seite** im Frontmatter, automatisch aus Git-mtime gerendert – manuelle Datumseinträge verrotten erfahrungsgemäß schneller als der Code daneben.
- **Releasekopplung.** Jede Änderung an `assets/js/search/` oder am Index-Schema triggert einen Pflicht-Check der betroffenen Hilfeseiten im PR-Template. In `CLAUDE.md` als Hard Constraint ergänzen: *„UI-Änderungen ohne Update von `docs/hilfe/` werden nicht gemerged."*
- **Screenshots versionieren oder vermeiden.** Für MHDBDB-UI: lieber kurze animierte GIFs/Videos (wie correspSearch) oder gar keine Bilder und dafür präzise Textbeschreibungen (wie DTA). Statische Screenshots veralten zu schnell und niemand pflegt sie nach – siehe Perseus/MED.
- **Changelog-Seite** (correspSearch-Pattern): `/hilfe/hintergrund/aenderungen.html` (siehe Sitemap in Abschnitt 4), kurze Einträge pro Release, verlinkt GitHub-Releases.

### (e) Was MHDBDB vermeiden sollte
- Kein separates PDF-Handbuch – nicht durchsuchbar, nicht deeplinkbar, nicht zitierbar mit Anchor. (Der Verdacht, dass ReM es so löst, konnte im Rahmen dieser Recherche nicht verifiziert werden; die generelle Anti-Pattern-Begründung trägt trotzdem.)
- Kein „Work in Progress"-Banner. Entweder Seite steht oder sie existiert noch nicht.
- Keine 404-produzierenden Deeplinks aus dem Hauptmenü (DTA-Problem: `/doku/hilfe` liefert 404, `/doku/DDC-suche_hilfe` funktioniert). URLs stabil halten, Redirects pflegen.

## 4. Vorgeschlagene Sitemap für `/hilfe/`

```
/hilfe/                               Hilfe-Hub. 3 Kacheln: „Schnellstart",
                                      „Nachschlagen", „Hintergrund". Prominenter
                                      Suchschlitz über die Hilfeseiten selbst.

├── schnellstart/                     Task-orientierter Einstieg, für alle Zielgruppen.
│   ├── erste-suche.html              „Wie finde ich Belege für ein mhd. Wort?"
│   │                                 → Beispiel *minne*, 3 Klicks zum Ergebnis.
│   ├── text-lesen.html               „Wie lese ich einen Volltext mit Hervorhebungen?"
│   ├── mehrere-lemmata.html          „Wie kombiniere ich Suchen im Playground?"
│   │                                 → Proximity, Dokument-Level, Farbcodes.
│   └── texte-filtern.html            „Wie grenze ich das Korpus auf bestimmte Werke ein?"
│
├── nachschlagen/                     Feature-Referenz, 1:1 zur UI. Für Nutzer:innen,
│   │                                 die wissen wollen, was ein Element tut.
│   ├── suchfeld.html                 Lemma-Eingabe, Normalisierung (â→a, ü→ue),
│   │                                 3-stufige Variantenauflösung.
│   ├── trefferliste.html             Sortierung, KWIC-Fenster, Navigation.
│   ├── reading-view.html             Metadatenpanel, Wikidata/GND, Kontextsprung.
│   ├── authority-files.html          Personen, Werke, Lemmata, Begriffe, Gattungen.
│   └── playground.html               10 Einstiegspunkte (6 Authority + 4 TEI-Analyse-Modi),
│                                     Multi-Lemma-Suche (Nähe/Dokument), Korpusauswahl.
│
├── hintergrund/                      Für zitierende Forscher:innen und Entwickler:innen.
│   ├── datenbasis.html               666 TEI-Texte, 7 Authority-Files, MHDBDB Salzburg.
│   ├── tei-modell.html               Link auf TEI-MODEL.md (Kurzfassung für Nicht-Devs).
│   ├── zitieren.html                 Empfohlene Zitation, DOI/URL-Pattern, Lizenz CC BY-NC-SA.
│   ├── aenderungen.html              Changelog, verlinkt GitHub-Releases.
│   └── bekannte-grenzen.html         Desktop-only, statisches Korpus, Rebuild-Zyklus.
│
└── fuer-entwickler/                  Englisch. Einziger englischsprachiger Zweig, bewusst flach.
    ├── index-schema.html             Kurz-Version DATA-MODEL.MD mit Link auf Volldoku.
    ├── build-pipeline.html           Python-Build, Variantendict, Normalisierung.
    └── api-contracts.html            Link auf CONTRACTS.MD.
```

**Begründung der Zielgruppentrennung:**
- `schnellstart/` und `nachschlagen/` bedienen Studierende und Medievalist:innen gemeinsam – die Tasks unterscheiden sich graduell, nicht kategorial; separate Pfade würden doppelte Pflege erzwingen.
- `hintergrund/` ist für Zitierende (primär Medievalist:innen) und dient gleichzeitig als Einstieg in die stabile `docs/`-Welt.
- `fuer-entwickler/` ist explizit englisch und bewusst flach – es leitet nur in die bestehende Dev-Doku unter `docs/` weiter, statt sie zu duplizieren.

---

**Quellen (während Recherche besucht):**
- correspSearch Help-Hub: https://correspsearch.net/en/help.html
- Perseus Help: https://www.perseus.tufts.edu/hopper/help
- DTA Suchhilfe: https://www.deutschestextarchiv.de/doku/DDC-suche_hilfe
- TextGrid Repository: https://textgridrep.org/
- ReM: https://www.linguistics.rub.de/rem/
- TEI Learn: https://tei-c.org/support/learn/
- MED Help (via Suchindex rekonstruiert, 403 bei Direktabruf): https://quod.lib.umich.edu/m/middle-english-dictionary/help
- MWB Hinweise (Mittelhochdeutsches Wörterbuch, Trier/Mainz): https://mhdwb-online.de/hinweise.html
- Monasterium Help: https://www.monasterium.net/mom/help
- Monasterium EditMOM-Dokumentation: https://www.monasterium.net/mom/editmom-documentation
