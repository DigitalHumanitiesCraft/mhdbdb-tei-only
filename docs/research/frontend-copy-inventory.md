---
title: Frontend Copy Inventory — Bestandsaufnahme user-facing Text
status: Recherche-Artefakt, nicht Teil der stabilen Doku
date: 2026-04-13
scope: Parallelarbeit zu help-pages-best-practice.md — was an Copy bereits existiert, was fehlt, was widersprüchlich ist
---

> **Hinweis:** Temporäres Recherche-Artefakt. Entscheidungsgrundlage für `/hilfe/`-Implementation. Nach Umsetzung archiviert (Git-History). Nicht in INDEX.MD verlinken.

## Zweck

Systematische Bestandsaufnahme aller user-facing Copy im Frontend. Antwortet drei Fragen:

1. **Was existiert schon?** — wiederverwendbar für `/hilfe/` (ggf. nach Edit)
2. **Was fehlt?** — muss neu geschrieben werden
3. **Was ist widersprüchlich?** — muss vor Doku-Arbeit konsolidiert werden

Komplementär zu `help-pages-best-practice.md` (Struktur-Empfehlung) und `docs/USER-GUIDE.MD` (bestehender Guide-Text).

---

## 1. Seiteninventar

| Seite | Datei | Größe | Rolle | Hat Footer | Hat Mobile-Nav |
|---|---|---|---|---|---|
| Landing | [index.html](../../index.html) | 717 | Übersicht, Stats, „Doku"-Hub (dev-facing) | ✓ + Clear Site Data | ✓ |
| Korpussuche | [korpus.html](../../korpus.html) | 382 | Haupt-Suche, Reading View | ✓ + Clear Site Data | ✓ |
| Playground | [playground/index.html](../../playground/index.html) | 421 | 3-Spalten-Explorer (Browser / Queries / Ergebnisse) | ✓ + Clear Site Data | ✓ |
| Lemma-Seite | [lemma/index.html](../../lemma/index.html) | 235 | Einzel-Lemma-Ansicht (persistente URL) | Abweichend (simpler Footer, kein Kontakt-Link in Nav) | — |
| 404-Fallback | [404.html](../../404.html) | 33 | GitHub-Pages-SPA-Redirect + Fallback-Text | — | — |
| User Guide (MD) | [docs/USER-GUIDE.MD](../USER-GUIDE.MD) | 122 | Benutzerhandbuch, nur auf GitHub erreichbar | — | — |

**Beobachtung:** Vier Frontend-Seiten, eine Markdown-Datei. Keine zentrale Hilfe-Seite. Die Nav-Positionen „Dokumentation" und „Kontakt" zeigen auf Anchor-Sektionen in `index.html` (`#documentation`, `#contact`).

---

## 2. Wiederverwendbare Copy

Material, das für `/hilfe/` nach dem Sitemap-Entwurf aus `help-pages-best-practice.md` taugt — eventuell mit kleineren Edits:

| Quelle | Text / Konzept | Mögliche Ziel-Sektion |
|---|---|---|
| `docs/USER-GUIDE.MD` → „Korpus-Suche" | Vollständiger Feature-Walkthrough Suchfeld, Textauswahl, Leseansicht | `/hilfe/nachschlagen/suchfeld.html`, `reading-view.html`, `trefferliste.html` |
| `docs/USER-GUIDE.MD` → „Playground" | 3-Schritte-Workflow, Multi-Lemma-Modi, Workflow Playground → Leseansicht | `/hilfe/schnellstart/mehrere-lemmata.html`, `/hilfe/nachschlagen/playground.html` |
| `docs/USER-GUIDE.MD` → „Allgemeine Hinweise" | Erster Aufruf / Cache / Systemanforderungen / Bekannte Einschränkungen | `/hilfe/hintergrund/bekannte-grenzen.html` |
| `index.html` „Über das Projekt"-Karten (Zeilen 228–255) | Projektziel, TEI-Korpus, semantische Annotationen (3×80-Wort-Abschnitte) | `/hilfe/hintergrund/datenbasis.html` |
| `index.html` Authority-Files-Liste (Zeilen 300–375) | 7 Authority-Files mit Rolle und Größe | `/hilfe/nachschlagen/authority-files.html` |
| `index.html` „MHG Character Normalization"-Karte (Zeilen 421–434) | Normalisierungstabelle (â→a etc., Ligaturen) | `/hilfe/nachschlagen/suchfeld.html` |
| `index.html` „Playground"-Karten (Zeilen 396–444) | Feature-Gruppierung Authority / TEI Analysis / Normalisierung | `/hilfe/nachschlagen/playground.html` (Überblick) |
| `korpus.html` Intro-Text (Zeilen 102–106) | „Durchsuchen Sie 666 mittelhochdeutsche Texte mit automatischer Normalisierung…" | `/hilfe/schnellstart/erste-suche.html` (als Hook) |
| `korpus.html` Inline-Tipp (Zeile 183) | „Tipp: Um nur in bestimmten Texten zu suchen…" | `/hilfe/schnellstart/texte-filtern.html` |
| `playground/index.html` Page-Subtitle (Zeile 83) | „Forschungsplattform für mittelhochdeutsche Korpusanalyse. …" | `/hilfe/schnellstart/` Hub-Teaser |
| `playground/index.html` Multi-Lemma-Modal-Hint (Zeile 286) | „Sie können Lemma-IDs oder Lemma-Formen verwenden. Sonderzeichen werden normalisiert. Alle Varianten werden erkannt." | `/hilfe/schnellstart/mehrere-lemmata.html` |
| `playground/index.html` Modi-Beschreibungen (Zeilen 309, 329) | „Nähe-Analyse: Kookkurrenz" / „Dokument-Suche: alle Lemmata irgendwo" | `/hilfe/nachschlagen/playground.html` |
| `lemma/index.html` Sektionslabels | Morphologie, Bedeutungen, Schreibformen, Komposita, Belegstellen, Wörterbuchnetz, Weitere Verweise | `/hilfe/nachschlagen/reading-view.html` oder eigene `lemma-seite.html` |

**Fazit:** Die meiste Referenz-Prosa (`/hilfe/nachschlagen/`) existiert in Bruchstücken. Task-Walkthroughs (`/hilfe/schnellstart/`) existieren **nicht** — USER-GUIDE.MD ist Feature-geordnet, nicht Task-geordnet.

---

## 3. Copy, die komplett neu geschrieben werden muss

Für den Sitemap-Entwurf aus der Best-Practice-Recherche gibt es zu folgenden Seiten **keine** wiederverwendbare Vorlage:

### `/hilfe/` (Hub-Landingpage)
- 3-Kachel-Einstieg (Schnellstart / Nachschlagen / Hintergrund)
- Suchschlitz über die Hilfeseiten selbst (Best-Practice-Empfehlung, aber techn. Zusatzaufwand — siehe §6)

### `/hilfe/schnellstart/` (alle Seiten)
- `erste-suche.html` — Task-Narrativ „Wie finde ich Belege für *minne*?" (3 Klicks)
- `text-lesen.html` — Task-Narrativ für Reading View mit Hervorhebungen (existierende Feature-Liste ist nicht task-geordnet)
- `mehrere-lemmata.html` — Task-Narrativ Multi-Lemma im Playground mit konkretem Forschungs-Use-Case
- `texte-filtern.html` — Task-Narrativ Korpusauswahl (Tipp-Text in `korpus.html:183` ist ein guter Hook, aber kein Walkthrough)

### `/hilfe/hintergrund/`
- `zitieren.html` — **komplett fehlend**. Keine Zitationsempfehlung irgendwo. Nur correspSearch in der Best-Practice-Recherche hat das vorbildlich gelöst.
- `tei-modell.html` — Kurzfassung von `docs/TEI-MODEL.md` für Nicht-Entwickler:innen. TEI-MODEL.md selbst ist fürs Dev-Publikum.
- `aenderungen.html` — Changelog-Seite (GitHub-Releases verlinken). Existiert bisher nicht.

### `/hilfe/fuer-entwickler/` (optional, englisch)
- Im Inventar nicht weiter verfolgt — die Inhalte existieren bereits in `docs/ARCHITECTURE.MD`, `docs/DATA-MODEL.MD`, `docs/CONTRACTS.MD`. Hier reicht eine dünne Landingpage mit drei Links.

### Lemma-Seite (falls eigene Doku)
- `lemma/index.html` ist nirgends in der bestehenden Doku erwähnt — weder in `USER-GUIDE.MD` noch in `FEATURES.MD`. Das ist eine Lücke, die im Inventar am stärksten auffällt.

---

## 4. Inkonsistenzen, die vor der Doku-Arbeit geklärt werden müssen

Die Best-Practice-Recherche warnt vor Anti-Pattern #6 („Outdated Screenshots / fossile Systemhinweise") und #10 („DE/EN-Mischmasch"). Im bestehenden Frontend gibt es genau solche Fälle:

### 4.1 Widersprüchliche Zahlen

| Ort | Wörtliches Zitat aus der Quelle |
|---|---|
| `index.html:286` | `<div class="text-4xl font-bold text-brand-600 mb-2">39,436</div>` + Label „Lemmata" (US-Format) |
| `playground/index.html:83` | „… Multi-Lemma-Suche, **43.750** Lexikoneinträge, semantische Begriffsnetzwerke …" (DE-Format) |
| `docs/USER-GUIDE.MD:60` | „Wörterbuch (ca. **39.000** Einträge)" |

→ **Drei unterschiedliche Zahlen.** Muss konsolidiert werden, bevor `/hilfe/` geschrieben wird. Vermutung: unterschiedliche Zählweisen (Lemmata ohne Varianten vs. mit Compounds vs. alles). Prüfen gegen `data/authority-index.json.gz`.

### 4.2 Zahlenformate DE vs. EN

- `index.html` nutzt US-Komma-Separator: `39,436`, `192,674`
- `playground/index.html` nutzt DE-Punkt-Separator: `43.750`, `192.674`
- Auf einer deutschsprachigen Seite (`lang="de"`) ist US-Format falsch.

### 4.3 Mischsprachige Überschriften auf deutschen Seiten

Bei `lang="de"` gesetzt, aber Headings in Englisch:

| Datei | Zeile | Englisch | Deutsch wäre |
|---|---|---|---|
| `index.html` | 248 | „Semantic Annotations" | „Semantische Annotationen" |
| `index.html` | 294 | „Orthographic Variants" | „Orthographische Varianten" |
| `index.html` | 399 | „Authority Files Exploration" | „Authority Files erkunden" (oder konsequent anglifizieren) |
| `index.html` | 412 | „TEI Text Analysis" | „TEI-Textanalyse" |
| `index.html` | 423 | „MHG Character Normalization" | „Normalisierung mhd. Zeichen" |
| `playground/index.html` | 82 | `<h1>TEI Data Explorer</h1>` | „TEI-Daten-Explorer" oder als Untertitel belassen, Haupt-H1 deutsch |
| `playground/index.html` | 203 | „Query Interface" | „Abfragen" oder „Suchwerkzeuge" |
| Alle Footer | — | Button-Label „Clear Site Data" | „Website-Daten löschen" |
| `404.html` | 26 | Fallback „Page not found" / „Back to MHDBDB" | „Seite nicht gefunden" / „Zurück zur MHDBDB" |

Deine Regel laut Memory: *immer Deutsch für user-facing*. Diese Stellen verletzen das.

### 4.4 Widersprüchliche Ladezeit-Angaben

- `korpus.html:267` (Reading View): „Dies kann **30-60 Sekunden** dauern"
- `playground/index.html:101` (Korpus-Load): „Dies dauert etwa **5-10 Sekunden**"

30-60 Sekunden stammt wahrscheinlich aus einer früheren Architektur (Runtime-XML-Parsing, vgl. `ARCHITECTURE.MD:406` / `INDEX.MD:23`: „30-second browser load times" als Grund für die Index-Migration; `DECISIONS.MD` dokumentiert dieselbe Entscheidung paraphrasiert: „30-second initial load time", „Slow initial load (30 seconds)"). Nach der Index-Umstellung dürfte das nicht mehr stimmen. → In einem Browser-Smoke-Test empirisch gegenprüfen und anpassen.

### 4.5 Mobile-Navigation existiert, obwohl Desktop-only deklariert

- `CLAUDE.md` Hard Constraint: „Desktop-only: min 1200px width"
- Drei der vier Hauptseiten (`index.html`, `korpus.html`, `playground/index.html`) haben Mobile-Menü-Button + Mobile-Nav-Code; `lemma/index.html` nicht (siehe §1).
- Widersprüchlich. Entweder den Mobile-Code konsistent entfernen (konsequent zur Constraint) oder die Constraint aufweichen und `lemma/index.html` nachziehen.

### 4.6 „Dokumentation"-Nav ist dev-facing

Der Header-Link „Dokumentation" auf allen Seiten zeigt auf `#documentation`, eine Section in `index.html`, die aus drei Kacheln besteht:
- Promptotyping (Methoden-Meta)
- Knowledge Vault (Links auf GitHub-rohe `INDEX.MD`, `ARCHITECTURE.MD`, `DATA-MODEL.MD`, `RESEARCH.MD`, `CLAUDE.md`)
- Benutzerhandbuch (Link auf GitHub-rohe `USER-GUIDE.MD` + Hinweis „Webansicht in Vorbereitung")

Für die eigentliche Zielgruppe (Medievalist:innen, DH-Forscher:innen) ist das **unbrauchbar**: Sie sehen Dev-Meta-Dokumentation und einen „WIP"-Hinweis. Dieser Section sollte nach Einführung von `/hilfe/` entweder umgebaut (Kachel „Hilfe" prominent, Dev-Links als Nebenkachel) oder vollständig entfernt werden, mit `/hilfe/` als Hauptziel des Nav-Links.

### 4.7 Lemma-Seite hat abweichende Navigation

- `lemma/index.html` hat keine „Kontakt"-Option in der Nav (alle anderen Seiten haben sie)
- Footer ist simpler (kein Clear-Site-Data-Button, nur ein Zeilen-Credit)
- Nicht gravierend, aber inkonsistent. Bei der Implementation von `/hilfe/` mitnehmen: Nav-Template vereinheitlichen.

### 4.8 Behauptung „11 spezialisierte Suchfunktionen" in index.html

`index.html:391–393` sagt: „Der Playground bietet eine interaktive Web-Oberfläche zur Exploration des TEI-Korpus mit **11 spezialisierten Suchfunktionen**."

Tatsächlich im `playground/index.html`: 6 Authority-Buttons + 1 Multi-Lemma + 3 weitere TEI-Analyse-Buttons = **10**. Zählung prüfen.

---

## 5. Nicht-Copy-Artefakte (zur Kenntnis)

Folgende user-sichtbaren UI-Elemente sind keine „Copy" im engen Sinne, müssen aber in der Doku erklärt werden:

- Farb-System Multi-Lemma-Highlighting: 5 Farben (rot, blau, grün, gelb, violett) — dokumentiert in `USER-GUIDE.MD:35`
- „Schritt 1/2/3"-Pattern im Playground (visuelle Progression) — nicht dokumentiert
- Metadaten-Panel-Felder (Autor*in, Sigle, Gattung, Quelle) in `korpus.html:273–288` — Labels sind Copy, aber die Wikidata/GND-Verknüpfung dahinter ist nirgends erklärt
- „Clear Site Data" — erklärt in `USER-GUIDE.MD:103–105` (Abschnitt „Cache leeren"), Button selbst ist aber englisch beschriftet
- „Beta"-Banner (`index.html:189`) — erklärt nicht, was das heißt oder wie lange Beta-Phase dauert
- Error-States: `errorDisplay` in allen Seiten, aber der tatsächliche Fehlertext kommt aus JS (`app.js:434` „Bitte wählen Sie mindestens einen Text aus.") — Inventur nicht erschöpfend, da Fehlertexte in JS verstreut sind

---

## 6. Offene Design-Fragen für `/hilfe/`-Implementation

Aus dem Abgleich Inventar ↔ Best-Practice-Recherche entstanden:

1. **Markdown-Quelle oder direkt HTML?** — Research-Empfehlung (`help-pages-best-practice.md` §3(d)): „Hilfe liegt als Markdown in `docs/hilfe/` und wird beim Build zu statischen HTML-Seiten". **Session-Entscheidung ist davon abweichend: direktes Handschreiben von HTML im Stil von `korpus.html`, kein neuer Render-Pfad.** Der URL-Pfad-Entwurf aus dem Research (`schnellstart/erste-suche.html` usw.) bleibt identisch — die Leaf-Namen sind dort schon `.html`. Unterschied liegt im **Authoring-Workflow**. Konsequenzen, die im weiteren Plan berücksichtigt werden müssen:
   - **Keine automatische „Stand"-Zeile per Git-mtime** (Research §3(d) hätte die aus dem Build generiert). Wenn wir das Frische-Signal wollen, muss es entweder manuell gepflegt oder per Pre-Commit-Hook/CI-Check injiziert werden (z.B. Script, das bei HTML-Änderung ein `data-last-modified`-Attribut aus `git log --format=%cs -1 <file>` setzt).
   - **Kein Markdown-Komfort beim Schreiben** (Tabellen, Codeblöcke, Listen sind in HTML aufwendiger). Copy-Drafts können in MD entstehen und dann einmalig nach HTML konvertiert werden — aber das ist ein menschlicher Schritt, kein Build-Step.
   - **Wartungskonvention laut Research §3(d) („Releasekopplung, PR-Template-Check") bleibt trotzdem relevant** — sie hängt nicht am Markdown, sondern an der Disziplin, `docs/hilfe/` mit UI-Änderungen zu synchronisieren. In `CLAUDE.md` als Hard Constraint ergänzen, sobald `/hilfe/` V1 steht.
2. **Volltext-Suche in der Hilfe?** — Best-Practice-Empfehlung: „prominenter Suchschlitz über die Hilfeseiten selbst". Das braucht entweder einen Index (zusätzlicher Build-Step) oder JS-String-Scan über geladene Seiten. Kann in V1 weggelassen und später nachgerüstet werden.
3. **Kontextuelle Inline-Hilfe (Fragezeichen-Icons)** — gute Idee, aber +N Touchpoints in bestehenden Seiten. V1 oder V2?
4. **Lemma-Seite in der Sitemap** — nicht im Research-Entwurf enthalten, aber ohne Doku-Eintrag ist die Seite für Nicht-Devs unauffindbar. Empfehlung: eigene `/hilfe/nachschlagen/lemma-seite.html`.
5. **Landing-Page „Dokumentation"-Section** — nach `/hilfe/`-Launch umbauen oder entfernen (siehe §4.6). Vor dem Launch nichts anfassen, damit keine toten Links entstehen.

---

## 7. Nächste Schritte (Vorschlag, wenn wir uns koordinieren)

1. **Zahlen-Audit** (eine Person, ~30 Min): Die Lemmata-Zahl (39.436 / 43.750 / 39.000) gegen `data/authority-index.json.gz` verifizieren. Ergebnis als einziges Zahlenformat (DE) in allen Seiten konsolidieren.
2. **Sprachen-Konsolidierung** (eine Person, ~45 Min): Die englischen Headings und Button-Labels aus §4.3 auf Deutsch umstellen. Kann Kollege in Angriff nehmen — kleine, klar abgegrenzte Edits pro Datei.
3. **`/hilfe/` V1 skizzieren** (gemeinsam): Entscheidung über (a) 3-Kachel-Hub, (b) welche Schnellstart-Szenarien zuerst, (c) Nav-Integration. Sitemap aus Best-Practice-Recherche als Ausgangspunkt.
4. **Content-Migration USER-GUIDE.MD → `/hilfe/nachschlagen/`** (gemeinsam oder aufgeteilt): Feature-Beschreibungen umziehen, task-Walkthroughs neu schreiben.
5. **`index.html` Dokumentations-Section umbauen** (nach Launch): Dev-Material in eigene Sekundär-Kachel, `/hilfe/` prominent.
6. **Frische-Signal-Strategie festlegen** (bei V1-Skizze, ~15 Min Diskussion): Da wir auf den MD-Build verzichten (siehe §6.1), fällt die automatische „Stand"-Zeile aus der Research-Empfehlung weg. Optionen: (a) manuelles `data-last-modified`-Attribut pro Seite, (b) Git-Pre-Commit-Hook, der das aus `git log -1` injiziert, (c) ganz weglassen und Frische über Release-Notes/Changelog-Seite signalisieren. Entscheidung muss vor dem Schreiben der ersten Hilfe-Seite fallen, sonst setzen wir ein unbeabsichtigtes Default.

Was NICHT zum Scope gehört und parkiert bleibt:
- README auf Deutsch umstellen (eigenständiger Task, nach User-Facing-Welle)
- Vollständiger Guide „How to add your data" (#68, `depends-on-human`)
- `/schema/`-Frontend für TEI-Modell (#78, eigener Task nach `/hilfe/`)
- Mobile-Support-Entscheidung (aus §4.5 — eigene Diskussion)
