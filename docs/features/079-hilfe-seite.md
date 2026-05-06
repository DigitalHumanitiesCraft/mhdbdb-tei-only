# Issue #79: Hilfe-Seiten (`hilfe.html` + `hilfe-*.html`) – User-facing Help (V1)

Teil des Umbrella #80 („User-facing Dokumentation & Hilfe"). Geschwister-Pakete: **#78** (Schema-Frontend) und **#68** (Einreichungsguide) – beide bedienen die Zielgruppe „Mitwirkende"; dieses Paket bedient „Leser:innen / Suchende".

## Context

MHDBDB hat derzeit **keine user-facing Hilfe oder Doku**. Die einzige Benutzer-Anleitung liegt als Markdown auf GitHub (`docs/USER-GUIDE.MD`) und ist von der Landing-Seite aus nur als „Webansicht in Vorbereitung"-Placeholder verlinkt (`index.html` Dokumentations-Section). Die Zielgruppe – Mediävist:innen und DH-Forscher:innen – sieht dort ausschließlich Dev-Meta-Material: Promptotyping, `CLAUDE.md`, GitHub-rohe Architektur-Markdowns.

Der Nav-Link „Dokumentation" auf allen vier Hauptseiten zeigt auf `index.html#documentation` und führt zu Entwickler:innen-Doku, die für das Fachpublikum unbrauchbar ist.

Dieser Plan baut die Hilfe-Seiten als flache Datei-Gruppe am Project-Root (`hilfe.html` + drei `hilfe-*.html`-Walkthroughs) im Stil von `korpus.html`: statisches HTML mit Tailwind, konsistent mit dem Rest des Frontends. Kein neuer Render-Pfad, kein Markdown-Build, kein eigenes Verzeichnis – der `hilfe-`-Präfix macht die Zugehörigkeit per Basename eindeutig und löst Namens-Kollisionen mit den existierenden Tool-Dateien (`korpus.html`, `playground/index.html`).

## Grundlage

Zwei Research-Artefakte im Promptotyping-Sinn (temporär, werden nach Umsetzung archiviert):

- [docs/research/help-pages-best-practice.md](../research/help-pages-best-practice.md) – Vergleich von 9 DH-Korpusprojekten, 11 Anti-Patterns, Sitemap-Empfehlung für einen `/hilfe/`-Bereich (im Lean-Plan aufgelöst zu flachen `hilfe-*.html`-Dateien, siehe Scope-Section)
- [docs/research/frontend-copy-inventory.md](../research/frontend-copy-inventory.md) – Inventur bestehender user-facing Copy, identifiziert wiederverwendbares Material und 8 Frontend-Inkonsistenzen

### Leitprinzipien (aus Research §3 + Session-Entscheidungen)

- **Nur Deutsch** für user-facing Content. Keine halbe englische Lokalisierung (Anti-Pattern #8 laut Research). Im Lean-V1 gibt es keinen englischen Unterbaum – nur einen dezenten Verweis vom Hub auf `docs/INDEX.MD` (das ist Dev-Doku, die ohnehin englisch ist).
- **Zielgruppe Mediävist:innen + DH-Forscher:innen**. Sachlich, fachlich präzise, aber keep it simple – Fachbegriffe beim ersten Auftreten kurz erklären.
- **Hybrid aus Task-Einstieg und Feature-Referenz**. Leitbild: ReM-Gliederung + correspSearch-Zitationsseite + MED-Eindeutigkeit pro Feature (Research §3(a)).
- **Direktes HTML-Schreiben** im Stil von `korpus.html`. Kein Markdown-Build – bewusst abweichend von Research-Empfehlung §3(d), um keinen neuen Render-Pfad einzuführen.
- **Keine Screenshots** (veralten zu schnell, siehe Perseus/MED in Research §1). Lieber präzise Textbeschreibungen oder kurze Videos/GIFs.
- **Keine „Work in Progress"-Banner**. Entweder Seite steht oder existiert noch nicht.
- **Keine erfundenen Features** in der Doku. Die Research-Sitemap hatte „TEI-Upload" als Playground-Feature aufgeführt – das gibt es nicht (mehr). Alle Doku-Seiten beschreiben nur existierende UI.

## Scope V1 – Lean (4 Hilfe-Seiten + 1 Landing-Erweiterung)

**Leitprinzip: So viele Seiten wie nötig, so wenige wie möglich.** Drei essentielle Themen-Seiten (Korpus, Playground, Daten) + ein orientierender Hub mit Quick-Start. Quick-Start ist Best Practice für Hilfe-Seiten und lebt direkt im Hub, statt eine fünfte URL zu erzwingen.

**Naming-Konvention:** Jede Hilfe-Datei trägt das Präfix `hilfe-` (außer der Hub selbst, der `hilfe.html` heißt). Dadurch ist die Zugehörigkeit auf Basename-Ebene eindeutig – keine Kollision mit `korpus.html` oder `playground/index.html`, grep-bar als `hilfe*.html`.

```
hilfe.html               Hub + Quick-Start „In 3 Schritten zur ersten Suche"
                         + 3 Kachel-Links auf die Themen-Seiten
hilfe-korpussuche.html   Walkthrough für /korpus.html (Hauptseite):
                         Suchen → Filtern → Lesen → Highlighting → Lemma-Seite
hilfe-playground.html    Walkthrough für /playground/ (Forschungswerkzeug):
                         Multi-Lemma-Suche (Nähe + Dokument), Authority-Files
hilfe-daten.html         Datenbasis: 666 TEI-Texte, 7 Authority Files,
                         Provenienz, Editionen, bekannte Grenzen
```

Plus auf `index.html`: **Zitations-Sektion** in der bestehenden „Kontakt & Lizenz"-Section. Die Lizenz-Karte wird zu „Lizenz & Zitation" erweitert – Direktlink über `index.html#zitieren`.

Summe: **4 neue HTML-Dateien** am Project-Root, **1 erweiterte Sektion** in `index.html`.

### Warum genau diese 4 + 1

- **`hilfe.html`** ist Hub und Quick-Start in einem. Drei kurze Schritte („Suchwort eingeben → Texte auswählen → Treffer öffnen") bringen Erstnutzer:innen sofort an einen sichtbaren Erfolg. Darunter drei Kachel-Links auf die Themen-Seiten. Kein extra Pfad nötig; Quick-Start ist die Hauptarbeit der Hub-Seite.
- **`hilfe-korpussuche.html`** ist der Walkthrough für die Haupt-Anwendung (`korpus.html`), die 90% der Nutzer:innen tatsächlich verwenden. Sektionen: Lemma-Suche, Textauswahl/Filter, Reading View, Highlighting-Farben, Lemma-Seite (so kommen Nicht-Devs überhaupt erstmal an die Lemma-Page heran).
- **`hilfe-playground.html`** ist der Walkthrough für das Forschungswerkzeug (`playground/`). Sektionen: Multi-Lemma-Suche (Nähe/Dokument), Authority-Files-Erkundung (Personen, Werke, Lemmata, Begriffe, Gattungen, Namen), typische Forschungsfragen.
- **`hilfe-daten.html`** beantwortet die Forschungs-Frage „Was durchsuche ich da eigentlich?". Sektionen: Korpus-Übersicht (666 Texte, 43.750 Lemmata, 175.910 Varianten), 7 Authority Files mit ihrer Rolle, Provenienz und Editionen (digitale Zwischenstufen), bekannte Grenzen (Desktop-only, statisches Korpus). Bildet Brücke zu #78 (Schema) und #68 (Ingest), die später unter dem Umbrella #80 erscheinen.
- **Zitations-Sektion auf `index.html`** schließt die kritischste Lücke aus dem Inventar (Zitationsempfehlung existiert heute nirgendwo) – direkt da, wo Lizenz und Kontaktinfo schon stehen, mit Direktlink über `#zitieren`. Keine eigene URL nötig, weil das Thema thematisch zu „Lizenz & Kontakt" gehört.

### Was wegfällt vs. dem ursprünglichen 19-Seiten-Entwurf

| Dropped | Wo es jetzt lebt |
|---|---|
| `schnellstart/` × 4 + `nachschlagen/` × 6 (Verzeichnisstruktur, 10 separate Seiten) | Als thematische Sektionen direkt in `hilfe-korpussuche.html` und `hilfe-playground.html` – Walkthroughs nach Frontend-Bereich, nicht nach Doku-Sitemap-Kategorie |
| `hintergrund/datenbasis.html` | Sektion in `hilfe-daten.html` (recyclet `index.html` „Über das Projekt") |
| `hintergrund/bekannte-grenzen.html` | Sektion am Ende von `hilfe-daten.html` |
| `hintergrund/tei-modell.html` | Wegfall – kommt mit #78 (`/schema/`) als eigene Seite, dort sinnvoller verortet |
| `hintergrund/aenderungen.html` | Wegfall – GitHub-Releases reichen für Changelog. Frische-Signal-Diskussion damit auch hinfällig. |
| `nachschlagen/lemma-seite.html` | Sektion in `hilfe-korpussuche.html` (Reading View → Lemma-Seite ist der natürliche Pfad) |
| `fuer-entwickler/` × 3 | Wegfall – `hilfe.html` bekommt einen Link auf `docs/INDEX.MD` für Entwickler:innen. Keine duplizierte Dev-Doku. |

### Was nicht in V1 ist

- **Volltext-Suche** über die Hilfeseiten selbst. Bei 4 Seiten obsolet – Browser-Strg+F reicht.
- **Kontextuelle Inline-Fragezeichen-Icons** im bestehenden Frontend. Eigener PR-Zyklus, später wenn überhaupt nötig.

## Phase 0: Pre-Cleanup (Christian, solo) – ABGESCHLOSSEN

Vor dem Schreiben der Hilfe-Seiten mussten vier Aufräum-Tasks erledigt werden – drei echte Inkonsistenzen (0.1, 0.2, 0.3) plus ein Nebenbefund (0.4), sonst hätten wir Widersprüche dokumentiert (siehe Inventar §4). Alle vier sind durch und im Browser-Smoke-Test verifiziert.

### 0.1 Zahlen-Audit – ABGESCHLOSSEN

Audit über `data/authority-index.json.gz` + `data/corpus-index.json.gz` + `authority-files/variants.xml`. Der Audit war breiter als ursprünglich geplant: nicht nur die Lemmata-Zahl war falsch, sondern auch die Varianten-Zahl, die in Inventar §4.1 nur als Format-Inkonsistenz markiert war.

**Korrekte Werte (aus den Index-Files):**

| Metrik | Wert | Quelle |
|---|---|---|
| Lemmata (Wörterbuch-Einträge) | **43.750** | `authority-index.json.gz` → `lemmata: list with 43750 entries`, matched `DATA-MODEL.MD:60` |
| Varianten (nach MHG-Normalisierung, indexiert) | **175.910** | `authority-index.json.gz` → `variants: dict with 175910 keys`, matched `DATA-MODEL.MD:166` (~176k) |
| Texte | **666** | `corpus-index.json.gz` → `totalTexts: 666` |

Hintergrundinfo zu Varianten: `variants.xml` enthält 192.472 raw `<form>`-Elemente und 188.684 unique Variant-Strings. Nach MHG-Normalisierung kollabieren die auf 175.910 indexierte Keys – das ist die Zahl, die der Search tatsächlich findet und deshalb user-facing korrekt.

**Gefixte Stellen (8 Edits):**

| Datei | Zeile | Vorher | Nachher |
|---|---|---|---|
| `index.html` | 286 | `39,436` | `43.750` (DE-Format) |
| `index.html` | 292 | `192,674` | `175.910` (DE-Format) |
| `playground/index.html` | 286 | `192.674 Varianten` | `175.910 Varianten` |
| `docs/USER-GUIDE.MD` | 60 | `ca. 39.000 Einträge` | `43.750 Einträge` |
| `playground/readme.md` | 33 | `192,674 variants` | `175,910 variants` |
| `playground/readme.md` | 56 | `192,674 variant forms` | `175,910 variant forms` |
| `docs/features/034-wenzelsbibel-annotation.md` | 53 | `192,674` | `175,910` |
| `testing/tests/search-normalization.spec.js` | 484 | `192,674 orthographic forms` | `175,910 orthographic forms` |

Nicht angefasst: `docs/research/frontend-copy-inventory.md` (Historisches Artefakt, beschreibt den Zustand vor dem Audit).

### 0.2 Sprachen-Konsolidierung – ABGESCHLOSSEN

Inventar §4.3 listete 9 Stellen, der Browser-Smoke-Test enthüllte eine zehnte (`<title>` im Playground). **Erledigt: 10 Edits in 4 Dateien.**

| Datei | Vorher (englisch) | Nachher (deutsch) |
|---|---|---|
| `index.html:248` | „Semantic Annotations" | „Semantische Annotationen" |
| `index.html:294` | „Orthographic Variants" | „Orthographische Varianten" |
| `index.html:399` | „Authority Files Exploration" | „Authority Files erkunden" |
| `index.html:412` | „TEI Text Analysis" | „TEI-Textanalyse" |
| `index.html:423` | „MHG Character Normalization" | „Normalisierung mhd. Zeichen" |
| `index.html` Footer-Button | „Clear Site Data" | „Website-Daten löschen" |
| `korpus.html` Footer-Button | „Clear Site Data" | „Website-Daten löschen" |
| `playground/index.html:6` | `<title>… - TEI Data Explorer</title>` | `<title>… – TEI-Daten-Explorer</title>` |
| `playground/index.html:82` | `<h1>TEI Data Explorer</h1>` | „TEI-Daten-Explorer" |
| `playground/index.html:203` | „Query Interface" | „Abfragen" |
| `playground/index.html` Footer-Button | „Clear Site Data" | „Website-Daten löschen" |
| `404.html:26` | „Page not found / Back to MHDBDB" | „Seite nicht gefunden / Zurück zur MHDBDB" |

### 0.3 Ladezeit-Audit – ABGESCHLOSSEN

`korpus.html:267` sagte ursprünglich „Dies kann **30-60 Sekunden** dauern" – Überbleibsel der Pre-Index-Ära (`ARCHITECTURE.MD:406`: „50MB XML files caused 30-second browser load times"). Wichtiger Fund: `assets/js/storage/tei-cache-manager.js:6` dokumentiert „reduce repeat load times from 30-60s to 2-3s" – Cold-Loads sind also weiterhin im 30-60s-Bereich, warme Loads (Cache-Hit) brauchen nur 2-3s. Die alte Warnung verschwieg den Cache-Vorteil und schreckte unnötig ab.

**Erledigt: 1 Edit in 1 Datei.**

| Datei | Vorher | Nachher |
|---|---|---|
| `korpus.html:267` | „Dies kann **30-60 Sekunden** dauern" | „Beim ersten Aufruf einige Sekunden, danach aus dem Cache" |

### 0.4 Nebenbefund: stale Dokus – ABGESCHLOSSEN

`playground/readme.md` und `docs/INDEX.MD` behaupteten beide, dass der Playground TEI-Datei-Upload unterstützt. Tatsächlich ist das Feature laut `playground/js/playground-main.js:394` explizit entfernt (`// Upload UI removed in redesign`).

**Erledigt: 5 Edits in 2 Dateien.**

| Datei | Stelle | Korrektur |
|---|---|---|
| `playground/readme.md:23` | „Bulk upload of TEI and authority files (drag & drop)" | „Auto-loading of TEI corpus and authority files (no upload step – UI removed in current redesign)" |
| `playground/readme.md:83` | „Upload files:" Sektion | „Data loads automatically:" mit präzisierter Beschreibung |
| `playground/readme.md:141` | „TEI files uploaded and parsed" | „TEI corpus loaded from pre-built index and parsed" |
| `playground/readme.md:158` | „F1: TEI upload & parsing (bulk + drag & drop)" | „F1: TEI corpus loading from pre-built index" |
| `docs/INDEX.MD:49` | „TEI Analysis - Upload and analyze custom TEI files" | „TEI Analysis - Browse and analyze the pre-loaded MHDBDB corpus" |

---

**Phase 0 Gesamtbilanz:** 24 Edits in 9 Dateien, alle Browser-Smoke-getestet. Phase 1 kann starten.

Phase 0 lief **vor** Phase 1 und wurde als eigener Commit abgeschlossen. Phase 1 Schritte 1-3 (Template, Hub, Proof-of-Concept) legen ausschließlich neue `hilfe*.html`-Dateien am Project-Root an – keine Konflikte mit Phase 0. Phase 1 Schritt 4 (Nav-Integration) editiert dieselben vier Hauptdateien wie Phase 0.1 und 0.2, aber Phase 0 ist da bereits committet. Solo-Orchestrierung: sequentiell, sauber, ohne Merge-Rätsel.

## Phase 1: Gerüst + Hub + Korpussuche-Walkthrough (Christian)

1. **Template-Entscheidung**: `korpus.html` als Referenz-Template nehmen. Header (inkl. globaler Top-Nav) und Footer unverändert übernehmen, Tailwind-Klassen konsistent halten.

   **Layout der Hilfe-Seiten:** Einspaltig, mit zwei Navigations-Ebenen:
   - **Globale Top-Nav** (unverändert von `korpus.html`): Startseite | Korpussuche | Playground | **Hilfe** | Kontakt – der „Hilfe"-Eintrag (Phase 1 Schritt 4) zeigt auf `hilfe.html`. Diese Nav steht auf jeder Seite des gesamten Projekts.
   - **Hilfe-interne Nav-Leiste** direkt unter der Top-Nav, nur auf den vier Hilfe-Seiten vorhanden: **Quick-Start | Korpussuche-Hilfe | Playground-Hilfe | Daten** – vier Tabs, der aktive ist hervorgehoben. So kommt man von jeder Hilfe-Seite ohne Umweg zum Hub und zu jeder anderen Themen-Seite.
   - **Inhaltsverzeichnis-Box** am Seitenanfang (Anker-Links auf die Sektionen der jeweiligen Seite) – die innerseitige Navigation.

   Damit ist die Frage „Wie navigieren Nutzer:innen zwischen den 4 Hilfe-Seiten?" architektonisch beantwortet: **horizontal über die Hilfe-Nav-Leiste, vertikal über das TOC**. Keine versteckten Cross-Links, keine Sackgassen.

   Keine Abhängigkeit auf JS – reine statische HTML-Seiten, damit Direktlinks immer funktionieren und keine IndexedDB-Ladewartezeit entsteht.

2. **`hilfe.html`** (Hub + Quick-Start): Drei Kachel-Links auf `hilfe-korpussuche.html`, `hilfe-playground.html`, `hilfe-daten.html`. **Hauptinhalt = Quick-Start „In 3 Schritten zur ersten Suche"**: kurze nummerierte Anleitung (Suchwort eingeben → Texte filtern → Treffer öffnen), die Erstnutzer:innen sofort an einen sichtbaren Erfolg bringt. Abschluss: dezenter Verweis-Block „Für Entwickler:innen → `docs/INDEX.MD` auf GitHub". Keine eigene „Was ist MHDBDB"-Sektion – die wandert auf `hilfe-daten.html`. Keine eigene „Bekannte Grenzen"-Sektion – die wandert ans Ende von `hilfe-daten.html`.

3. **Korpussuche-Walkthrough als Proof-of-Concept**: `hilfe-korpussuche.html` ist die erste komplette Themen-Seite. Sie deckt den vollen Workflow auf der Hauptseite ab, mit klaren Sektionen:
   - Worum es geht (1 Absatz)
   - Lemma-Suche (z.B. *minne* finden, 3 Klicks)
   - Texte filtern und auswählen
   - Reading View und Highlighting (5 Farben)
   - Lemma-Seite (so kommen Nutzer:innen überhaupt erstmal an die Lemma-Page heran)
   - Was Sie als Nächstes tun können (Link auf `hilfe-playground.html` für komplexere Recherchen)

   Diese Seite ist die **Tonalitäts- und Layout-Vorlage** für die anderen beiden Themen-Seiten. Quellen aus Inventar §2: USER-GUIDE.MD „Korpus-Suche", `korpus.html` Intro + Inline-Tipp.

4. **Nav-Integration**: Header-Link „Dokumentation" (`index.html#documentation`) auf allen vier Hauptseiten (`index.html`, `korpus.html`, `playground/index.html`, `lemma/index.html`) durch „Hilfe" (→ `hilfe.html`) ersetzen. Der `#documentation`-Anchor in `index.html` bleibt vorerst bestehen, wird in Phase 3 umgebaut. Zusätzlich: auf `lemma/index.html` fehlt der „Kontakt"-Link gegenüber den anderen Seiten (Inventar §4.7) – bei dieser Gelegenheit mitnehmen und Nav-Template vereinheitlichen.

5. **Review-Gate**: Christian + Katharina prüfen Hub + Korpussuche-Walkthrough. Entscheidung über Tonalität, Layout, Detailgrad, bevor die restlichen 2 Seiten geschrieben werden.

## Phase 2: Restliche 2 Seiten + Zitations-Sektion (Christian)

Nach Review-Gate. Bei nur 2 verbleibenden Hilfe-Seiten ist Sub-Agent-Parallelisierung Overkill – sequentiell ist sauberer.

- **`hilfe-playground.html`**: Walkthrough für das Forschungswerkzeug (`playground/`). Sektionen: Was ist der Playground, Multi-Lemma-Suche (Nähe/Dokument-Modi), Authority-Files erkunden (Personen/Werke/Lemmata/Begriffe/Gattungen/Namen), typische Forschungsfragen. Quellen aus Inventar §2: USER-GUIDE.MD „Playground", `playground/index.html` Subtitle + Modal-Hint + Modi-Beschreibungen. Tonalität laut Korpussuche-Walkthrough.
- **`hilfe-daten.html`**: Datenbasis-Beschreibung. Sektionen: Korpus-Übersicht (666 TEI-Texte, 43.750 Lemmata, 175.910 Varianten – Phase-0-validierte Zahlen), 7 Authority Files mit Rolle und Größe (recyclet aus `index.html:300–375`), Provenienz und Editionen, bekannte Grenzen (Desktop-only, statisches Korpus, Rebuild-Zyklus – recyclet aus `USER-GUIDE.MD` „Allgemeine Hinweise"), Brücke zu #78 und #68.
- **Zitations-Sektion auf `index.html`** (in der bestehenden „Kontakt & Lizenz"-Section): Lizenz-Karte zu „Lizenz & Zitation" erweitern. Inhalt: Empfohlener Zitations-String, Hinweis auf Version/Release, DOI/URL-Pattern falls vorhanden, Lizenz-Hinweis CC BY-NC-SA 4.0. **Braucht Abstimmung mit Katharina** für die offizielle Zitationsempfehlung – den Inhalt schreibe ich nicht ohne ihr OK. Direkt-Linkbar über `index.html#zitieren`.

## Phase 3: Landing-Page-Umbau + Launch

- `index.html` Dokumentations-Section umbauen: die drei Dev-Kacheln (Promptotyping, Knowledge Vault, `USER-GUIDE.MD`-Link) in eine einzige sekundäre, kleinere Kachel zusammenfassen. Haupt-Kachel für `hilfe.html` mit Link-Preview der drei Themen-Seiten (Korpussuche, Playground, Daten).
- `USER-GUIDE.MD` in `docs/` archivieren oder entfernen, sobald der Content vollständig im Frontend verfügbar ist. `INDEX.MD`-Eintrag entfernen.
- Playwright-Tests: Smoke-Test für Navigation der Hilfe-Seiten (`hilfe.html` → 3 Themen-Seiten → zurück), Link-Validierung, Seitentitel.
- **Hard Constraint in `CLAUDE.md`** ergänzen (Research §3(d)): „UI-Änderungen an `korpus.html`, `playground/index.html` oder `lemma/index.html` ohne Update der betroffenen `hilfe-*.html`-Seiten werden nicht gemerged." Verhindert die Feature-Doku-Drift, die in der Best-Practice-Recherche bei fast allen Vergleichsprojekten sichtbar war (Anti-Pattern #1, #6, #7).
- Manueller Browser-Smoke-Test: Walk through Landing → `hilfe.html` → Quick-Start → `korpus.html` ohne Irritation.

## Frische-Signal

Bei nur 4 Seiten obsolet. Die Pflege ist überschaubar genug, dass Stand-Zeilen oder Pre-Commit-Hooks keinen Mehrwert bieten. Frische wird durch die Hard-Constraint-Kopplung in `CLAUDE.md` (siehe Phase 3) sichergestellt: UI-Änderungen ohne entsprechendes Hilfe-Update werden nicht gemerged. Wenn sich später herausstellt, dass die 4 Seiten doch silently rotten, kommt ein Pre-Commit-Hook mit `git log --format=%cs -1 <file>` als Nachrüstung – aber V1 braucht das nicht.

## Akzeptanzkriterien V1

- [ ] `hilfe.html` (Hub) erreichbar mit Quick-Start „In 3 Schritten zur ersten Suche" + 3 Kachel-Links
- [ ] `hilfe-korpussuche.html` existiert mit Walkthrough der Hauptseite (inkl. Lemma-Seite-Sektion)
- [ ] `hilfe-playground.html` existiert mit Walkthrough des Forschungswerkzeugs
- [ ] `hilfe-daten.html` existiert mit Korpus-Übersicht, 7 Authority Files, Provenienz, bekannte Grenzen
- [ ] `index.html` hat eine Zitations-Sektion (in Lizenz-Karte integriert), direkt-linkbar über `#zitieren`
- [ ] Nav-Header zeigt „Hilfe" statt „Dokumentation" auf allen 4 Hauptseiten (`index.html`, `korpus.html`, `playground/index.html`, `lemma/index.html`) und verlinkt auf `hilfe.html`
- [ ] `lemma/index.html` hat den fehlenden „Kontakt"-Nav-Link (aus Phase 1 Schritt 4, Inventar §4.7)
- [ ] Keine toten Links zwischen den 4 Hilfe-Seiten, alle aufeinander verlinkt
- [ ] **Phase 0 Erledigt-Checks (✅ schon durch)**:
  - [x] Lemmata-Zahl in allen Quellen konsistent (43.750)
  - [x] Varianten-Zahl in allen Quellen konsistent (175.910)
  - [x] Keine englischen UI-Strings mehr auf deutschsprachigen Hauptseiten
  - [x] Ladezeit-Hinweis in `korpus.html` modernisiert
  - [x] `playground/readme.md` und `docs/INDEX.MD` haben keine TEI-Upload-Claim mehr
- [ ] Playwright-Smoke-Test für die Hilfe-Seiten-Navigation grün
- [ ] Browser-Smoke-Test: Landing → `hilfe.html` → Quick-Start → `korpus.html` funktioniert ohne Irritation
- [ ] Hard Constraint in `CLAUDE.md` für UI/Doku-Kopplung (Phase 3)
- [ ] `index.html`-Dokumentations-Section umgebaut, `hilfe.html` als Haupt-Kachel (Phase 3)

## NICHT Teil dieses Plans

- **#78 `/schema/`-Seite für TEI-Modell** → Geschwister-Paket unter Umbrella #80. Bedient dieselbe Zielgruppe „Mitwirkende" wie #68. Reihenfolge laut Umbrella: nach #79. Koordination über den Umbrella-Parent, nicht hier.
- **#68 „How to add your data"-Guide** → Geschwister-Paket unter Umbrella #80. `depends-on-human`, braucht Wachauer-Input und Lessons Learned aus Wenzelsbibel-Ingest (#34).
- **Cross-Linking zwischen den Paketen** wird im Umbrella #80 koordiniert: die Hilfe-Seiten bekommen in V1/V2 einen dezenten Verweiskasten auf `/schema/` und den Einreichungsguide für Mitwirkende – die Texte dafür entstehen erst, wenn die Zieladressen (Phase 2 hier und #78/#68 dort) feststehen.
- README auf Deutsch umstellen → nach Hilfe-Seiten-Launch als Cleanup-Welle, eigenständig.
- Mobile-Support-Entscheidung (Inventar §4.5) → unabhängige Diskussion; V1 übernimmt aktuellen Desktop-only-Stand, `lemma/index.html` bleibt weiter ohne Mobile-Menü bis entschieden ist.
- Komplette englische Doku-Spiegelung → explizit NICHT Teil der Strategie laut Research §3(b). Es gibt im Lean-V1 keinen englischen Unterbaum mehr; der dezente Verweis von `hilfe.html` auf `docs/INDEX.MD` reicht für Entwickler:innen.
- Volltext-Suche über die Hilfeseiten selbst und kontextuelle Inline-Fragezeichen-Icons in den Hauptseiten → siehe Scope-Section „Was trotzdem NICHT in V1 ist". Eigene spätere Zyklen.

## Referenzen

- Research (temporär): [help-pages-best-practice.md](../research/help-pages-best-practice.md)
- Inventar (temporär): [frontend-copy-inventory.md](../research/frontend-copy-inventory.md)
- Bestehender Guide: [USER-GUIDE.MD](../USER-GUIDE.MD) (Quelle für Content-Migration)
- Konvention: Feature-Docs werden nach Abschluss ins Git-Archiv verschoben, kritisches Wissen wandert in stabile Docs (siehe `CLAUDE.md` → „Temporal Artifacts")
