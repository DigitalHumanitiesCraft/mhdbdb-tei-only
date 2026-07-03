# Code-Audit Report — MHDBDB TEI Repository

**Datum:** 2026-07-02  
**Code-Stand:** `997be03` (main nach Merge PR #157)  
**Branch:** `claude/workflows-code-audit-24waqy`

**Methode:** Multi-Agent-Workflow (`/workflows`), Opus 4.8. 47 Finder-Agenten lasen alle 120 JS/Python/Test-Dateien vollständig (Batches pro Datei + 12 Dimensions-Agenten für Dead-Code, Refactoring, Klarheit, Cross-Language-Parität, Docs-Drift, XSS- und Async/Storage-Sweeps). Jedes Finding wurde anschließend adversarial verifiziert — Critical/High-Bugs durch ein 3-Linsen-Skeptiker-Panel (Logik, Erreichbarkeit, Datenrealität), der Rest durch beweispflichtige Einzel-Verifizierer, die die betroffene Datei erneut lasen und Dead-Code-Greps selbst wiederholten.

> **Dies ist ein reiner Audit — es wurden keinerlei Code-Änderungen vorgenommen.** Jedes Finding enthält einen Behebungsvorschlag, aber die Umsetzung ist bewusst dir überlassen (Triage zuerst).

## Zusammenfassung

Von **129 Roh-Findings** (120 nach Deduplizierung) haben **113 die adversariale Verifikation bestanden**, 7 wurden widerlegt (Anhang B).

| Severity | Anzahl | | Kategorie | Anzahl |
|---|---|---|---|---|
| 🔴 Critical | 1 | | Bug | 58 |
| 🟠 High | 11 | | Dead Code | 23 |
| 🟡 Medium | 45 | | Klarheit | 13 |
| ⚪ Low | 56 | | Docs-Drift | 10 |
|  |  | | Parität | 5 |
|  |  | | Refactoring | 4 |

**Hotspots (Dateien mit den meisten Findings):**

- `playground/js/ui/core/ui-helpers.js` — 9
- `playground/js/data/tei-manager.js` — 6
- `assets/js/app.js` — 4
- `docs/DATA-MODEL.md` — 4
- `lemma/lemma-page.js` — 4
- `playground/js/ui/tei/multi-lemma-search.js` — 3
- `scripts/ingest/wzb/wzb-auto-match.py` — 3
- `scripts/ingest/wzb/wzb-sense-apply.py` — 3

**Wichtigste Muster:**
- **WZB-Ingest-Skripte sind reihenweise abgestürzt-by-default:** Nach der Skript-Reorg (`scripts/ingest/wzb/`, 2026-05) zeigen mehrere `sys.path`-Inserts noch auf das alte Verzeichnis → `mhg_normalizer`-Import scheitert; dazu fehlender `Counter`-Import, `argparse`-dest-Kollision, KeyError auf totem Stats-Key. Diese Skripte laufen aktuell bei jedem Aufruf sofort auf einen Fehler.
- **Vertrags-Drift beim Lemma-Matching:** Mehrere Playground-Pfade nutzen CSS-Substring-Selektoren bzw. präfixlose IDs und verletzen damit den Exact-Token-Vertrag aus CONTRACTS.md §B.1 (`#lemma_308` matcht `#lemma_3089`).
- **`last-wins`-Term-Bug im Authority-Build:** `parse_genres` überschreibt (wie zuvor schon bei `concepts`) den Primär-Term mit dem alternativen — betrifft Index-Daten.
- **Ein reflektiertes DOM-XSS** über den teilbaren Multi-Lemma-URL-Parameter (einzige Critical).

---

## Nachtrag (2026-07-03): Korrekturen & Behebungsstand

Nach Erstellung des Reports wurden Findings triagiert und teils behoben. Zwei Korrekturen am Report selbst:

**1. Die „Archiv-Kandidat"-Dead-Code-Findings sind HINFÄLLIG.** Eine Live-Prüfung der GitHub-Issues widerlegt die Annahme, die betroffenen `scripts/`-Wurzel-Skripte seien abgeschlossene One-Shots:

| Finding | Skript | Issue-Status | Verdikt |
|---|---|---|---|
| Z. 1359 | `convert-l-to-lb-143.py` | **#143 offen** (Policy-Entscheidung; bei „konvertieren" läuft genau dieses Skript) | kein Archiv |
| #105 (Z. 1450) | `insert-lg-stanzas-138.py` | **#138 offen** (editorischer Substream, Kat. A = Skript-Umsetzung) | kein Archiv |
| Low-Liste (Z. 1570) | `insert-div-wrappers-138.py` | **#138 offen** | kein Archiv |

Ebenfalls nicht archivierbar (im Report nicht einzeln als Archiv-Finding gerendert): `insert-stanzas-from-linecode.py` (**#110 offen**, WVV-Bulk-Run steht aus) und `insert-pb-from-linecode.py` (#26 zu, aber als wiederverwendbares Template dokumentiert). Diese Skripte sind **dormant tooling an offenen Issues**, nicht legacy — Archivierung würde referenzierte Werkzeuge entfernen. Begründung: DATA-MODEL.md → Ingest-Verfahren.

**2. Der `all()`-Schreib-Short-Circuit ist korrekt `convert-l-to-lb-143.py` zugeschrieben** (Z. 1375), nicht `insert-lg-stanzas-138.py` (letzteres hat `--dry-run` bereits). Diese Report-Zuordnung war richtig.

**Behebungsstand (Commits auf diesem Branch bzw. Folge-Branch):**
- ✅ 6 Crash-/Import-Bugs in den dormanten Ingest-Skripten gefixt (`381d977`): WZB-`sys.path`/`PROJECT_ROOT`, fehlender `Counter`-Import, KeyError `auto_word_ref`→`auto_corresp`, argparse-dest-Kollision (`wzb-add-lemma`), sowie der `all()`-Short-Circuit + `--dry-run` in `convert-l-to-lb-143.py`.
- ✅ Die einzige **Critical** (reflektiertes DOM-XSS, `multi-lemma-search.js`) und die **High**-Frontend-Bugs (`app.js` Pagination + Lemma-Präfix-Normalisierung, `lemma-page.js`-Emitter + Test, `person-explorer.js` Multi-Sigle) behoben (`a86c715`).

**Nachtrag 2 (2026-07-03, Branch `claude/workflows-audit-status-i0h2hi`):**
- ✅ **#28–#32, #70**: `PROJECT_ROOT` in den 7 restlichen WZB-Skripten auf Repo-Root korrigiert (komplettiert `381d977`); alle Default-Pfade verifiziert, Dry-Runs laufen end-to-end.
- ✅ **#18, #19, #60–62, #66**: Escaping-Cluster — SearchHelpers-Suchbegriff, file-display (onclick → addEventListener-Closure), lemma-page-Index-Felder, multi-lemma-search Attribut-Kontext + querySelector.
- ✅ **#47, #64, #65**: lebende `lemmaRef*=`-Substring-Selektoren in `tei-manager.js` durch `lemmaRefMatchesId` ersetzt (§B.1). Tote Methoden mit demselben Muster (`extractMatchingWordsFromParagraph`, `searchWordsInText`, `findWordsByLemmaRef`) bleiben für den Dead-Code-Sweep.
- ✅ **#5** (letzter offener High): `parse_genres` last-wins gefixt (250 DE- + 308 EN-Labels), Authority-Index v1.5.0 + API-Rebuild.
- ✅ **#43, #44, #54, #76, #77, #81–85, #87, #100, #104, #106, #108**: Docs-Drift + Klarheits-Kommentare. Dabei entdeckt und mitgefixt (nicht im Report): `audit-tei-corpus.py` `repo_root` zeigte nach der Reorg eine Ebene zu hoch — Skript war komplett lauffunfähig; identische stale Pfade auch in `sync_tei_headers.py` (10×) korrigiert.
- ✅ **#38**: Tailwind-content-Globs — 8 ungescannte Seiten, Rebuild strikt additiv (405→437 Selektoren).
- ✅ **Dead-Code-Sweep** (#42, #46, #52, #78–80, #88–94, #101–103, #107, #109): −753 Zeilen; jedes Finding vor dem Löschen per repo-weitem Grep gegenverifiziert. Dabei 12 weitere tote Legacy-teiData-Helfer in `tei-manager.js` mit demselben Beweisstandard entfernt (im Report nicht einzeln gelistet). CONTRACTS §C angepasst (Vergleichs-Helfer nur noch JS-seitig). Volle Suite danach 185/187 (2 bekannte Umgebungs-Fails).
- ✅ **Test-Härtung** (#12, #39–41, #55–57, #73, #110–113): vakuöse Tests durch echte Assertions ersetzt (Work→Author über reale UI statt totem „→ Autor"-Button; Lemma→Concept über senses[].conceptIds; Touch-Targets mit Mess-Pflicht; Cache-Tests mit Cache-Entry- bzw. Zero-Refetch-Assertion im selben Test; Multi-Lemma-Farbtest auf HTR mit ≥2-Farben-Pflicht — ABG enthielt wîn gar nicht; 3-Stufen-Test prüft jetzt konkrete Lemma-IDs pro Stufe); No-op-XPath-Test und assertionsfreier Log-„Test" gelöscht; neuer Click-Through-Test Lemma-Seite → Reader-Highlight (#12-Rest).
- ➡️ **Alle verbleibenden offenen Findings sind in 6 Sammel-Issues überführt (2026-07-03):** [#167](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/167) Frontend-Kleinbugs (Findings 13, 16, 17, 21–23, 59, 63, 67, 86) · [#168](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/168) Race-Conditions (14, 20) · [#169](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/169) Suchsemantik-Entscheidungen (15, 45, 48, 51) · [#170](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/170) latente §B-Paritäts-Drifts (49/50, 53, 58) · [#171](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/171) Python-Skript-Bugs (24–27, 33–37, 68, 69, 71, 72, 95–97) · [#172](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/172) Test-Suite-Entscheidungen (74, 75). Damit ist jedes der 113 Findings entweder behoben, widerlegt (Anhang B), als hinfällig markiert oder in einem Issue getrackt.

---

## 🔴 Critical (1)

### 1. `playground/js/ui/tei/multi-lemma-search.js:215` — Bug
*Reflektiertes XSS: unescapte Suchbegriffe werden per innerHTML in die Fehlermeldung geschrieben*

Im Fehlerpfad "Keine gültigen Lemmata gefunden" werden die rohen Suchbegriffe (searchTerms.join(', ')) ohne jede Maskierung per innerHTML in den DOM geschrieben. searchTerms stammt aus this.lemmas, das über den Router (handleMultiLemmaRoute, router.js:143-145) direkt aus dem URL-Hash-Parameter `lemmata` befüllt und via ui.executeSearch() (router.js:167) automatisch ausgeführt wird. Da alle anderen innerHTML-Ausgaben in dieser Datei escapeHtml nutzen, ist genau diese Stelle die Lücke. Der Fehlerpfad wird immer dann erreicht, wenn kein Term auf ein Lemma auflöst — also gerade bei beliebigem/bösartigem Input.

**Fehlerszenario:** Opfer öffnet den präparierten Link .../playground/#multi-lemma?lemmata=<img src=x onerror=alert(document.cookie)>. Der Router legt den Term in ui.lemmas ab und ruft executeSearch(). resolveLemmaIds() findet kein Lemma → lemmaIds.length===0 → Zeile 215 injiziert das <img>-Tag ungefiltert per innerHTML → onerror-Handler feuert (reflektiertes XSS über teilbare URL auf der öffentlichen Seite).

```
❌ Keine gültigen Lemmata gefunden für: ${searchTerms.join(', ')}
```
**Vorschlag:** searchTerms vor der Interpolation maskieren, z.B. ${searchTerms.map(t => this.escapeHtml(t)).join(', ')} — analog zu den übrigen innerHTML-Ausgaben.


---

## 🟠 High (11)

### 2. `assets/js/app.js:715` — Bug
*displayResults setzt currentPage nicht zurück – Listenansicht zeigt nach Tabellen-Umschaltung die falsche (oder leere) Ergebnisseite*

this.currentPage wird nur im Konstruktor, in handleSearch und in clearSearch auf 0 gesetzt, aber in loadMoreResults hochgezählt. displayResults leert zwar resultsList.innerHTML, ruft loadMoreResults aber mit dem bereits hochgezählten currentPage auf, ohne ihn zurückzusetzen. setViewMode('list') ruft displayResults erneut auf. Nach jeder erneuten Listen-Darstellung wird also ein späterer Slice (startIdx = currentPage * 20) gerendert statt ab Ergebnis 0.

**Fehlerszenario:** Nutzer sucht (Listenansicht) → loadMoreResults setzt currentPage=1. Nutzer klickt Tabellen-Toggle (renderTable, currentPage bleibt 1) und wieder Listen-Toggle → displayResults → loadMoreResults mit startIdx = 1*20 = 20 → slice(20,40). Die ersten 20 Treffer fehlen. Liefert die Suche ≤20 Texte (bei seltenen Lemmata der Normalfall), ist slice(20,40) leer: die Ergebnisliste erscheint komplett leer, obwohl der Header 'N Texte gefunden' anzeigt.

```
// Display first page (Listen-Mode) ODER ganze Tabelle (Tabellen-Mode)
        if (this.viewMode === 'table') {
            this.renderTable();
        } else {
            this.loadMoreResults();
        }
```
**Vorschlag:** In displayResults vor dem Aufruf von loadMoreResults (bzw. am Anfang von displayResults) this.currentPage = 0 setzen, damit die Listenansicht immer bei Seite 0 beginnt.


### 3. `assets/js/app.js:1442` — Bug
*handleURLParameters reicht rohe numerische lemmaIds an den Reader durch – Playground-Multi-Lemma-Sprung hebt nichts hervor*

Der Playground erzeugt die Sprung-URL mit lemma-IDs OHNE 'lemma_'-Präfix (tei-ui.js: p.lemmaRef.replace('lemma_','') → '879'; ui-helpers.js Kommentar 'without lemma_ prefix'). handleURLParameters splittet den lemmaIds-Parameter und übergibt die Werte unverändert als options.lemmaIds an openReadingView. Der Reader vergleicht diese über lemmaRefMatchesId gegen das @lemmaRef-Fragment nach '#', das 'lemma_879' lautet. '879' ist kein exakter Token von 'lemma_879' → kein Treffer, kein Highlight.

**Fehlerszenario:** Nutzer klickt im Playground (Multi-Lemma-/Kookkurrenz-Suche) auf einen Treffer → öffnet korpus.html?textId=X&lemmaIds=879,7532&position=N (exakt das im Doc-Kommentar dokumentierte Format). Der Reader scrollt zwar über targetPosition zur Stelle, aber lemmaRefMatchesId('lexicon.xml#lemma_879','879') ist false, sodass KEIN gesuchtes Wort farblich hervorgehoben wird – der eigentliche Zweck des Sprungs (Treffer sichtbar markieren) entfällt.

```
const lemmaIds = lemmaIdsParam
            ? lemmaIdsParam.split(',').map(id => id.trim()).filter(id => id)
            : [];
```
**Vorschlag:** In handleURLParameters die IDs auf das vom Reader erwartete Format normalisieren, z. B. rein numerische IDs mit 'lemma_' präfixen (id => /^\d+$/.test(id) ? `lemma_${id}` : id), oder das URL-Format der Playground-Generatoren und den Reader-Vertrag (CONTRACTS §B.1) auf ein einheitliches ID-Format vereinheitlichen.


### 4. `playground/js/ui/authority/person-explorer.js:147` — Bug
*Werk-Deep-Link bricht bei Werken mit mehreren Siglen (Komma-String als textId)*

**Fehlerszenario:** Nutzer sucht eine Autor*in und klickt „Werke anzeigen“. Für ein Werk mit mehreren Siglen (z. B. work_21 „AXH, AXU“) liefert der Authority-Index in work.sigle den kommaverbundenen String „AXH, AXU“ (scripts/build-authority-index.py:312: sigle = ', '.join(sigles)). Da work.sigle truthy ist, greift der beabsichtigte Fallback work.sigles[0] nie. Der Titel-Link wird zu ../korpus.html?textId=AXH%2C%20AXU, was keiner TEI-Datei entspricht → toter Link/„Text nicht gefunden“. Betrifft 70 Werke im aktuellen Index (bestätigt: 70 Einträge mit Komma in .sigle).

```
const sigle = work.sigle || (work.sigles && work.sigles[0]) || null;
          const titleHTML = sigle
            ? `<a href="../korpus.html?textId=${encodeURIComponent(sigle)}" ...>
```
**Vorschlag:** Für die Deep-Link-Sigle die Einzelsigle bevorzugen: `const sigle = (work.sigles && work.sigles[0]) || (work.sigle && !work.sigle.includes(',') ? work.sigle : null);` — also nie den kommaverbundenen work.sigle-String als textId verwenden.


### 5. `scripts/build-authority-index.py:516` — Bug
*parse_genres überschreibt den Primär-Term mit dem alternativen Term (last-wins) – derselbe Bug, der für concepts bereits gefixt wurde*

In parse_genres wird term_de in der Schleife über alle <term> ohne Berücksichtigung von @type gesetzt. Bei Kategorien mit mehreren de-Termen gewinnt der letzte. Da @type="alternative"-Terme in genres.xml regelmäßig NACH dem Primär-Term stehen, wird der kanonische deutsche Gattungsname durch die alternative Schreibform ersetzt. termDE und das daraus abgeleitete normalized im genres-Array enthalten dann den Alternativbegriff statt der Vorzugsbenennung. Genau dieser last-wins-Fehler wurde für concepts (parse_concepts, Zeilen 440-456) unter #113-Followup behoben, für genres aber nie. Zusätzlich entsteht eine Inkonsistenz: _build_genre_names (Zeile 251-255) und die genreHierarchy-Namensauflösung (Zeile 727-731) verwenden per break den ERSTEN de-Term (Primär), sodass dieselbe Gattung in works[].genres[].text und genreHierarchy anders (korrekt) beschriftet ist als in genres[].termDE (falsch, alternativ).

**Fehlerszenario:** Kategorie genre_01bf2b8b hat <term xml:lang="de">Dialogische Kurzform</term> (Primär) gefolgt von <term xml:lang="de" type="alternative">Dialogform in der Kurzdichtung</term>. Nach parse_genres ist genres[].termDE = "Dialogform in der Kurzdichtung" und normalized entsprechend, statt "Dialogische Kurzform". Der Genre-Explorer im Playground zeigt für 250 von den Gattungskategorien den Alternativbegriff als Hauptlabel und die normalisierte Suche matcht auf den Alternativbegriff statt auf die Vorzugsbenennung. Verifiziert: 250 genre_-Kategorien betroffen (letzter de-Term != erster de-Term); names.xml und concepts.xml sind in der Praxis nicht betroffen.

```
for term_el in term_els:
            lang = term_el.get('{http://www.w3.org/XML/1998/namespace}lang')
            if lang == 'de':
                term_de = term_el.text.strip() if term_el.text else ''
```
**Vorschlag:** Analog zu parse_concepts unterscheiden: nur nicht-alternative de-Terme dürfen term_de setzen (elif not term_de: term_de = text), alternative in eine separate altDE-Liste ablegen. Damit stimmt genres[].termDE wieder mit _genre_names und genreHierarchy überein.


### 6. `scripts/ingest/wzb/wzb-auto-match.py:40` — Bug
*mhg_normalizer-Import scheitert, weil sys.path auf das wzb-Verzeichnis statt scripts/ zeigt*

**Fehlerszenario:** Nach dem Skript-Reorg (2026-05-07) liegt das Skript in scripts/ingest/wzb/, mhg_normalizer.py aber weiterhin nur in scripts/ (per find bestaetigt: einzige Kopie ./scripts/mhg_normalizer.py). Zeile 39 fuegt Path(__file__).parent = scripts/ingest/wzb in sys.path ein - nicht scripts/. Aufruf `python scripts/ingest/wzb/wzb-auto-match.py` (bzw. wie im Docstring `py scripts/wzb-auto-match.py`) endet mit ModuleNotFoundError: No module named 'mhg_normalizer' beim Import, bevor irgendeine Logik laeuft.

```
sys.path.insert(0, str(Path(__file__).parent))
from mhg_normalizer import normalize_mhg
```
**Vorschlag:** Pfad auf das scripts/-Verzeichnis korrigieren, z. B. sys.path.insert(0, str(Path(__file__).parent.parent.parent)) (oder mhg_normalizer als paketierten Import ansprechen).


### 7. `scripts/ingest/wzb/wzb-auto-match.py:95` — Bug
*Counter() wird verwendet, aber nie importiert - NameError bricht das Skript ab*

**Fehlerszenario:** Die Imports lauten nur `from collections import defaultdict` (Zeile 25); `Counter` fehlt. Sobald annotate_wzb() aufgerufen wird (immer, direkt aus __main__), wirft Zeile 95 `NameError: name 'Counter' is not defined`. Das Skript kann keine einzige WZB-Datei annotieren.

```
form_counts = Counter()
```
**Vorschlag:** Import auf `from collections import defaultdict, Counter` erweitern.


### 8. `scripts/ingest/wzb/wzb-sense-apply.py:37` — Bug
*sys.path.insert zeigt nach der Skript-Reorg auf scripts/ingest/wzb, mhg_normalizer liegt aber in scripts/ — ImportError beim Modulladen*

**Fehlerszenario:** Zeile 37 fügt Path(__file__).parent (= scripts/ingest/wzb) dem sys.path hinzu, Zeile 38 macht 'from mhg_normalizer import normalize_mhg'. mhg_normalizer.py liegt jedoch in scripts/ (bestätigt: find findet nur ./scripts/mhg_normalizer.py, keine Kopie in scripts/ingest/wzb/, keine __init__.py). Beim Start von 'python scripts/ingest/wzb/wzb-sense-apply.py' scheitert der Import mit ModuleNotFoundError, bevor überhaupt Argumente geparst werden. Identisches Problem in wzb-sense-assign.py Zeile 39-40. Der Pfad war korrekt, solange die Skripte direkt in scripts/ lagen (siehe alte Usage-Zeile im Docstring 'py scripts/wzb-sense-apply.py'); die Reorg vom 2026-05-07 nach scripts/ingest/wzb/ hat ihn gebrochen.

```
sys.path.insert(0, str(Path(__file__).parent))
from mhg_normalizer import normalize_mhg
```
**Vorschlag:** Auf das scripts/-Verzeichnis zeigen, z.B. sys.path.insert(0, str(Path(__file__).resolve().parents[2])) (wzb -> ingest -> scripts), in beiden sense-Skripten.


### 9. `scripts/ingest/wzb/wzb-sense-assign.py:283` — Bug
*KeyError auf nicht existierendem stats-Schlüssel 'auto_word_ref' bricht den kompletten Lauf ab, bevor die TEI geschrieben wird*

**Fehlerszenario:** assign_senses() erreicht nach der Verarbeitung immer den Summary-Block. Zeile 283 liest stats['auto_word_ref'], aber das stats-Dict (Zeilen 210-218) kennt nur 'auto_corresp' (gefüllt in Zeile 257). Da stats ein normales dict ist, wirft der Zugriff einen KeyError. Der Abbruch passiert nach den w.set('ana'/'corresp')-Mutationen im Speicher, aber VOR tree.write() (Zeile 305). Ergebnis: Bei jedem Nicht-Dry-Run werden alle Auto-Zuweisungen berechnet, aber die TEI-Datei wird nie geschrieben und das Skript endet mit Traceback. Phase-3-Auto-Assign ist damit vollständig funktionsunfähig.

```
print(f"  Auto-assigned @wordRef:    {stats['auto_word_ref']}")
```
**Vorschlag:** Schlüssel korrigieren auf stats['auto_corresp'] (analog zur Definition in Zeile 212 und dem Increment in Zeile 257).


### 10. `scripts/ingest/wzb/wzb-sense-evaluate.py:51` — Bug
*Import von mhg_normalizer schlägt fehl — Skript stürzt bei jedem Aufruf sofort ab*

sys.path bekommt in Zeile 50 nur das Skriptverzeichnis scripts/ingest/wzb hinzugefügt, mhg_normalizer.py liegt aber unter scripts/ (bestätigt: find zeigt nur ./scripts/mhg_normalizer.py). Der Import in Zeile 51 wirft daher beim Modul-Laden ModuleNotFoundError, bevor argparse überhaupt läuft. Verschärfend: normalize_mhg wird im gesamten Modul nie verwendet (grep zeigt nur die Import-Zeile) — der Import ist tot UND fatal. Die Skripte standen ursprünglich in scripts/ (dort funktionierte parent==scripts); nach dem Reorg 2026-05-07 nach scripts/ingest/wzb/ wurde der Pfad nicht mitgezogen.

**Fehlerszenario:** `python scripts/ingest/wzb/wzb-sense-evaluate.py --help` (oder sample/evaluate) → Traceback ModuleNotFoundError: No module named 'mhg_normalizer' (real reproduziert). Das Evaluations-Werkzeug ist komplett unbenutzbar, in keinem Modus lauffähig.

```
sys.path.insert(0, str(Path(__file__).parent))
from mhg_normalizer import normalize_mhg
```
**Vorschlag:** Import ersatzlos entfernen (normalize_mhg wird nicht benutzt) oder sys.path korrekt auf das scripts/-Verzeichnis setzen (Path(__file__).parent.parent.parent / 'scripts').


### 11. `scripts/wzb-add-lemma.py:145` — Bug
*argparse-dest-Kollision: --concept und --concepts schreiben beide nach args.concepts, Skript stürzt bei jedem normalen Aufruf ab*

**Fehlerszenario:** Aufruf laut Docstring: `py scripts/wzb-add-lemma.py --orth weise --pos NOM --concept concept_23112700`. Das required-append-Argument `--concept` (Zeile 139) hat dest="concepts"; das Pfad-Override-Argument `--concepts` (Zeile 145) erhält von argparse denselben dest "concepts". Da das Namespace-Attribut bereits durch die append-Option belegt ist, wird der Default von `--concepts` (DEFAULT_CON-Pfad) nie angewendet. Nach dem Parsen ist `args.concepts` die Concept-ID-Liste `['concept_23112700']`. In Zeile 153 wird daraus `con_path = Path(args.concepts)` gebildet → `Path(list)` wirft `TypeError: expected str, bytes or os.PathLike object, not list`. Real reproduziert: der --dry-run-Aufruf endet mit Traceback in Zeile 153 und Exit-Code 1. Das Tool ist damit für den dokumentierten Ingest-Workflow (neue Lemmata für WZB/ARITHMETIC) vollständig unbenutzbar; zusätzlich ist die dokumentierte Option `--concepts PATH` (Docstring Zeile 24) faktisch tot, weil sie bei Nutzung die Concept-ID-Liste mit dem Pfad-String überschreibt.

```
parser.add_argument("--concept", required=True, action="append", dest="concepts", ...)
...
parser.add_argument("--concepts", default=str(DEFAULT_CON))
...
con_path = Path(args.concepts)
```
**Vorschlag:** Den dest-Konflikt auflösen: entweder `--concept` einen eigenen dest geben (z. B. dest="concept_ids") und alle Verwender (Zeilen 160, 172) anpassen, oder das Pfad-Argument in `--concepts-file`/dest="concepts_path" umbenennen und Zeile 153 auf diesen neuen dest umstellen. Ein Regressionstest mit dem Docstring-Beispielaufruf würde den Absturz sofort aufdecken.


### 12. `testing/tests/lemma-page.spec.js:216` — Parität
*Test zementiert kaputtes Link-Format (lemmaIds=879 ohne lemma_-Präfix) und prüft nur den href-String, nicht das Highlighting*

**Fehlerszenario:** Der Occurrence-Link der Lemma-Seite wird in lemma/lemma-page.js:226 als korpus.html?...&lemmaIds=879 (lemmaKey.replace('lemma_','')) erzeugt. app.js:handleURLParameters übergibt diesen Wert unverändert an openReadingView, und processWord ruft lemmaRefMatchesId('lexicon.xml#lemma_879','879') auf → refIds=['lemma_879'].includes('879') === false. Reales Szenario: Nutzer klickt auf der Lemma-Seite brôt eine Fundstelle → Text ABG öffnet sich OHNE jedes Highlight und ohne Treffer-Navigation. Der Test bemerkt das nicht, weil er nur expect(href).toContain('lemmaIds=879') prüft — und schreibt damit sogar das falsche Format als Sollwert fest. Der reading-view.spec.js:20-61-Pfad benutzt dagegen das funktionierende Format lemma_879, sodass beide Tests grün sind, obwohl der reale Klickpfad defekt ist.

```
expect(href).toContain('lemmaIds=879');
```
**Vorschlag:** Sollwert an das vom Reader konsumierbare Format anpassen (lemmaIds=lemma_879) UND das eigentliche Verhalten prüfen: Link tatsächlich öffnen und expect(page.locator('#readingBody .highlight').count()).toBeGreaterThan(0) verifizieren. Zugrundeliegender App-Bug (bare-numeric vs. lemma_-Präfix) separat fixen.


---

## 🟡 Medium (45)

### 13. `assets/js/lib/woerterbuchnetz.js:61` — Bug
*Fehlgeschlagene/getimeoutete Wörterbuchnetz-Abfrage wird für die ganze Session als leer gecacht und erholt sich nie*

**Fehlerszenario:** Ein Nutzer öffnet eine Lemma-Seite (#73) oder das Korpus-Suche-Lemma-Panel (#114). Beim ersten Lookup ist die Wörterbuchnetz-API kurz überlastet, sodass der 10s-Timeout (AbortSignal.timeout(10000)) feuert oder ein Netzfehler auftritt. Jeder innere fetch-Task fängt den Fehler ab und liefert {sigle, entries: []}, wodurch das per Promise.all gebildete Promise erfolgreich mit lauter leeren Entry-Listen resolved. Dieses Promise wird über entryCache.set(normalizedForm, promise) unbedingt (unabhängig vom Erfolg) memoisiert. Sucht der Nutzer danach in derselben Session dasselbe Lemma erneut (oder ruft es im Korpus-Panel bei einem anderen Text auf), liefert entryCache.get() das gecachte leere Ergebnis zurück — es findet kein zweiter API-Call statt. Die MWB-/Lexer-Wörterbuchlinks bleiben dauerhaft unsichtbar, obwohl die API längst wieder erreichbar ist; nur ein vollständiger Seiten-Reload (der das modul-globale entryCache verwirft) stellt sie wieder her.

```
const promise = Promise.all(DICTIONARIES.map(async sigle => {
        try {
            const r = await fetch(...);
            if (!r.ok) return { sigle, entries: [] };
            ...
        } catch (e) {
            console.warn(...);
            return { sigle, entries: [] };
        }
    }));
    entryCache.set(normalizedForm, promise);
```
**Vorschlag:** Nur erfolgreiche (nicht-degradierte) Ergebnisse cachen. Z.B. den fetch-Erfolg pro Sigle als Flag zurückgeben und das Promise nach Auflösung prüfen: enthält es mindestens einen fehlgeschlagenen Dictionary-Call, den Eintrag per entryCache.delete(normalizedForm) wieder entfernen (im .then()/nach await), damit ein späterer Lookup neu anfragen kann. Erfolgreiche Leer-Ergebnisse (Lemma existiert im Wörterbuch nicht) dürfen weiterhin gecacht werden — nur transiente Fehler nicht.


### 14. `assets/js/rendering/tei-text-reader.js:76` — Bug
*Race Condition: gleichzeitige/schnelle openReadingView-Aufrufe desynchronisieren DOM und Instanz-State*

openReadingView() ist async und lädt die TEI-Datei über `await this.loadTEIFile()` (Ladezeiten im Sekundenbereich, siehe Log in loadTEIFile). Es gibt keinen Request-Generation-Guard: Alle Zustandsfelder (this.currentTextId, this.currentHighlights, Textlisten-Markierung via showPanel→highlightTextInList) werden bei jedem Aufruf überschrieben, aber populateModal() schreibt den DOM mit lokal berechneten Daten. Der Sigle-Link-Handler (Zeile 738) ruft openReadingView() re-entrant und ohne await auf. Wenn ein langsamer Ladevorgang (großes, ungecachtes File) NACH einem später gestarteten, schnelleren (kleines, gecachtes File) auflöst, gewinnt der ältere Aufruf das DOM-Rendering, während currentTextId/Textlisten-Markierung bereits auf den neueren Text zeigen.

**Fehlerszenario:** Nutzer öffnet Text A (großes, ungecachtes TEI), klickt sofort auf einen Sigle-Link zu Text B (kleines, gecachtes TEI). B lädt zuerst → populateModal(B), Textliste markiert B, currentHighlights=B. Danach löst A auf → populateModal(A) überschreibt den Lesebereich mit A's Text und setzt currentHighlights=A (Zeile 93), aber this.currentTextId bleibt B und die Textliste zeigt weiter B aktiv. Angezeigter Text, aktive Sigle in der Liste und Treffer-Navigation gehören zu verschiedenen Werken.

```
const teiDoc = await this.loadTEIFile(textMeta.filename);
```
**Vorschlag:** Einen monoton steigenden Request-Zähler (z. B. this._loadSeq) am Anfang von openReadingView erhöhen, den Wert lokal festhalten und nach jedem await prüfen; bei Nichtübereinstimmung early-return, bevor populateModal/State-Zuweisung erfolgt.


### 15. `playground/js/data/tei-manager.js:1196` — Bug
*3+-Lemma-Nähesuche misst nur Abstand zum Anker-Lemma, actualDistance kann maxDistance überschreiten*

Für jede Fundstelle des ersten Lemmas wird pro weiterem Lemma nur geprüft, ob eine Position innerhalb maxDistance des Ankers (firstPos) liegt. Ob die weiteren Lemmata auch untereinander innerhalb maxDistance liegen, wird nicht geprüft. Die anschließend gemeldete actualDistance = maxPos - minPos kann bis zu 2*maxDistance betragen und damit über dem vom Nutzer gesetzten Grenzwert liegen.

**Fehlerszenario:** Nähesuche über drei Lemmata mit maxDistance=5: Lemma B steht bei firstPos-5, Lemma C bei firstPos+5. Beide sind ≤5 vom Anker entfernt, also gilt der Treffer als gültig, aber B und C sind 10 Wörter auseinander. Ergebnis wird mit distance=10 angezeigt, obwohl der Nutzer 'innerhalb 5 Wörter' gefiltert hat → über den Filter hinausgehender Treffer.

```
const nearbyPos = positions.find(pos =>
                        Math.abs(pos - firstPos) <= maxDistance
                    );
```
**Vorschlag:** Alle paarweisen Abstände (bzw. Spannweite maxPos-minPos) gegen maxDistance prüfen, bevor der Treffer aufgenommen wird, statt nur den Abstand zum Anker-Lemma.


### 16. `playground/js/ui/authority/genre-explorer.js:182` — Bug
*"Werke anzeigen" und "Autor*innen anzeigen" teilen sich denselben Details-Container und heben sich per Toggle gegenseitig auf*

Beide Buttons einer Gattungs-Karte rufen toggleDetails mit derselben ID `genre-details-${genreId}` auf (showWorksInGenre Zeile 146, showAuthorsInGenre Zeile 182). generateResultItem erzeugt nur einen einzigen Details-Container pro Karte (detailsId `genre-details-${genre.id}`, Zeile 137). toggleDetails (SearchHelpers.js Zeile 144-150) blendet einen bereits sichtbaren Container aus und kehrt zurück, OHNE den Content-Generator auszuführen. Der Wechsel von Werken zu Autor*innen (oder umgekehrt) versteckt daher das Panel, statt den anderen Inhalt zu zeigen.

**Fehlerszenario:** Nutzer klickt bei einer Gattung mit zugeordneten Werken auf "Werke anzeigen" (Panel zeigt Werkliste), dann auf "Autor*innen anzeigen": Statt der Autorenliste verschwindet das Panel (toggleDetails sieht den Container als sichtbar und blendet ihn aus). Erst ein zweiter Klick auf "Autor*innen anzeigen" zeigt die Autoren. Das Wechseln zwischen beiden Ansichten ist dadurch dauerhaft doppelklick-abhängig und wirkt kaputt.

```
toggleDetails(`genre-details-${genreId}`, () => {
```
**Vorschlag:** Für die beiden Buttons getrennte Container-IDs verwenden (z.B. `genre-works-${genreId}` und `genre-authors-${genreId}`) und im generateResultItem entsprechend zwei Details-Bereiche anlegen — oder statt Toggle bei Ansichtswechsel den Container immer neu befüllen und anzeigen.


### 17. `playground/js/ui/authority/lemma-explorer.js:170` — Bug
*"← Zurück" bei Etymologie-Komponenten blendet das Panel aus, statt zu den Original-Bedeutungen zurückzukehren*

showComponentLemma befüllt den Container `senses-${originalLemmaId}` direkt via innerHTML (Zeile 167), ohne toggleDetails — der Container bleibt sichtbar (keine 'hidden'-Klasse, style.display='block'). Der eingebettete "← Zurück"-Button ruft showLemmaSenses(originalLemmaId) auf, welches toggleDetails auf denselben, aktuell sichtbaren Container anwendet. toggleDetails (SearchHelpers.js Zeile 146-150) erkennt den Container als sichtbar und blendet ihn aus, statt die Original-Bedeutungen wieder darzustellen.

**Fehlerszenario:** Nutzer öffnet die Bedeutungen eines Lemmas mit Morphologie (etymology mit lemmaRef), klickt auf das "→"-Icon einer Komponente (zeigt Komponenten-Bedeutungen via showComponentLemma) und dann auf "← Zurück": Statt zu den Bedeutungen des Ausgangslemmas zurückzukehren, verschwindet das gesamte Panel. Erst ein erneuter Klick auf "Bedeutungen anzeigen" bringt es zurück.

```
<button onclick="window.playground.ui.authorityExplorers.showLemmaSenses('${originalLemmaId}')"
```
**Vorschlag:** Der "Zurück"-Button sollte den Original-Content direkt neu rendern statt toggleDetails aufzurufen — z.B. eine Methode, die generateLemmaSenseContent(originalLemma) berechnet und container.innerHTML setzt (analog zu showComponentLemma), ohne den Sichtbarkeits-Toggle zu triggern.


### 18. `playground/js/ui/core/file-display.js:97` — Bug
*displayFileItem baut onclick-Attribut mit ungeschütztem Dateinamen*

Der Remove-Button für hochgeladene/gecachte Dateien setzt den Dateinamen unescaped in einen JS-String innerhalb eines onclick-Attributs (Zeile 97) sowie in die sichtbare Anzeige (Zeile 89) und wird via innerHTML gerendert (Zeile 84/108). Enthält der Dateiname ein Apostroph oder HTML, bricht der JS-String auf bzw. es wird Markup injiziert.

**Fehlerszenario:** Nutzer lädt eine TEI-Datei mit dem Namen `a');alert(1)//.xml` (oder `x'-alert(1)-'.xml`) hoch. Der generierte onclick wird zu `removeTEIFile('a');alert(1)//.xml')` -> beim Klick auf Entfernen wird alert(1) ausgeführt und removeTEIFile mit falschem/kaputtem Argument aufgerufen, der Datei-Eintrag lässt sich nicht mehr korrekt entfernen.

```
onclick="window.playground.removeTEIFile('${filename}')"
```
**Vorschlag:** Den Handler per addEventListener statt inline-onclick anhängen und den Dateinamen als data-Attribut (bereits als data-filename vorhanden) auslesen; alternativ escapeForJS + HTML-Escaping anwenden.


### 19. `playground/js/ui/search/SearchHelpers.js:70` — Bug
*handleSearchResults interpoliert den rohen Suchbegriff ungeschützt in innerHTML (DOM-XSS)*

Der vom Nutzer eingegebene Suchbegriff (searchTermForDisplay, Default = searchTerm) wird sowohl in den Treffer-Header (Zeile 70) als auch in die Leer-Meldung (Zeile 58) direkt in einen HTML-String eingesetzt, ohne HTML-Escaping. Alle sechs Authority-Explorer (genre/name/person/concept/lemma/work) geben dieses HTML über renderToContainer(...) via innerHTML aus (z.B. genre-explorer.js:142 `renderToContainer("genreResults", result.headerHTML + resultHTML)` bzw. :101 für den String-Fall). Damit wird beliebiges Markup aus der Sucheingabe als DOM interpretiert und Event-Handler ausgeführt.

**Fehlerszenario:** Nutzer tippt in das Personen-/Gattungs-Suchfeld `<img src=x onerror=alert(document.domain)>`. Der Begriff matcht nichts, also greift die emptyMessage (Zeile 58), die den rohen Term via innerHTML rendert -> das onerror-Skript feuert. (Analog feuert bei einem Term, der Treffer erzeugt, der Header in Zeile 70.)

```
${matches.length} Treffer für "${searchTermForDisplay}"${countInfo}
```
**Vorschlag:** searchTermForDisplay vor der Interpolation HTML-escapen (z.B. eine escapeHTML-Utility statt des im selben File bereits vorhandenen, aber nur JS-quotenden escapeForJS).


### 20. `playground/js/ui/tei/concept-distribution.js:576` — Bug
*Race-Condition-Guard bei paralleler Begriffssuche verwirft die falsche (die neuere) Suche und zeigt Concept-Header mit fremder Verteilung*

Der Guard nach der asynchronen Aggregation prueft nur das Flag `this.state.computing`, nicht ob es sich noch um die aktuelle Suche handelt. Bei einer zweiten Suche waehrend `computeDistribution` einer ersten Suche noch laeuft (nur moeglich, weil `computeDistribution` bei grossen Concepts via `yieldToMain()`/MessageChannel auf echte Macrotasks yieldet und so Klicks dazwischenlaesst), setzt die zweite runSearch `computing` erneut auf true. Die zuerst gestartete Aggregation laeuft zuerst durch, sieht `computing === true`, schreibt ihre Verteilung in den State und setzt `computing = false`. Wenn danach die zweite (neuere) Aggregation fertig wird, sieht sie `computing === false` und verwirft sich selbst. Ergebnis: `resolvedConcept`/`candidates`/`matchingLemmata` gehoeren zur zweiten (neueren) Suche, `distribution` aber zur ersten. Der Header/die Lemma-Vorschau zeigen Begriff B, das Balkendiagramm die Verteilung von Begriff A. Der Kommentar behauptet ausserdem, es werde geprueft, ob sich `matchingLemmata` geaendert habe, was der Code nicht tut.

**Fehlerszenario:** Nutzer sucht Begriff A mit >2000 zugeordneten Lemmata (z.B. das worst-case-Concept mit 8718 Lemmata). Waehrend der mehrsekuendigen, chunked Aggregation klickt er erneut Suchen fuer Begriff B. Die aeltere Aggregation (A) gewinnt, setzt computing=false, die neuere (B) verwirft sich. Angezeigt wird der Header/Name von Begriff B zusammen mit der Text-Verteilung von Begriff A -> sichtbar falsches Forschungsergebnis (Concept-Beschriftung passt nicht zu den Balken).

```
// Falls inzwischen eine neue Suche gestartet wurde (matchingLemmata
      // hat sich geaendert), Ergebnis verwerfen.
      if (!this.state.computing) return;

      this.state.distribution = dist;
```
**Vorschlag:** Generations-Token einfuehren: vor jeder Suche einen Zaehler (z.B. `this._searchGen`) inkrementieren, den Wert lokal in runSearch festhalten und nach dem await nur dann in den State schreiben, wenn der lokale Wert noch dem aktuellen `this._searchGen` entspricht; das `computing`-Flag ist als Identitaetskriterium ungeeignet.


### 21. `playground/js/ui/tei/cooccurrence-ranking.js:562` — Bug
*Ändern der Mindest-Frequenz nach der Suche filtert die Partnerliste nicht neu — Tabelle widerspricht dem angezeigten Cutoff*

Der Cutoff `minFreq` wird ausschließlich in `enrichPartners()` angewandt (Zeile 149: `if (count < this.state.minFreq) continue;`). `enrichPartners()` läuft nur in `runSearch()` (Zeile 196) und im `posMode`-Change-Handler (Zeile 572), der die Partner neu berechnet. Der `minFreq`-Change-Handler setzt dagegen nur `this.state.minFreq` und ruft `this.render()` auf — `renderResults()` liest aber `this.state.result.partners`, die noch mit dem alten `minFreq`-Wert aus der Suche berechnet wurden. Der Kommentar „kein Re-Compute noetig" ist sachlich falsch, denn der Cutoff lebt genau im Compute-Schritt. Der `topN`-Handler funktioniert nur zufällig, weil `slice(0, topN)` erst zur Render-Zeit greift; `minFreq` hat kein solches Render-Zeit-Pendant.

**Fehlerszenario:** Nutzer sucht „minne" mit Mindest-Frequenz 2, Ergebnis zeigt Partner mit Frequenz ≥2. Nun ändert er die Mindest-Frequenz im Zahlenfeld auf 50. `state.minFreq` wird 50, `render()` läuft, aber `state.result.partners` enthält weiterhin alle Partner mit Frequenz ≥2. Die Tabelle zeigt weiter Partner mit Kookkurrenz-Frequenz 2, 3, 4 …, während der Header „X Partner ≥ 50" und der Tooltip die 50 behaupten — die Frequenzspalte widerspricht sichtbar dem angeblichen Filter. Umgekehrt (Absenken von 2 auf 1) fehlen die Frequenz-1-Partner, obwohl der Filter sie zulassen müsste. Workaround existiert nur über das versehentliche Umschalten des Wortart-Filters, der neu enricht.

```
const v = parseInt(e.target.value, 10);
      this.state.minFreq = isNaN(v) || v < 1 ? 1 : v;
      // Wenn ein Result existiert, nur re-render (kein Re-Compute noetig).
      if (this.state.result) this.render();
```
**Vorschlag:** Im `minFreq`-Change-Handler analog zum `posMode`-Handler `this.state.result.partners = this.enrichPartners(this.state.result._rawCounts || new Map());` vor `this.render()` aufrufen (und den irreführenden Kommentar korrigieren).


### 22. `playground/js/ui/tei/multi-lemma-search.js:195` — Bug
*Multi-Lemma-Suche: kein „Korpus noch nicht geladen"-Guard — Suche vor Corpus-Load liefert stillschweigend leere Ergebnisse*

executeSearch() prüft nur, ob window.playground.teiManager existiert (Zeile 195-205), nicht aber, ob der Corpus-Index bereits geladen ist. Alle acht anderen TEI-Analyse-Werkzeuge (word-frequency.js:98, text-statistics.js:64, lemma-distribution.js:36, verse-position-search.js:33, concept-distribution.js:67, text-comparison.js:33, cooccurrence-ranking.js:58, rhyme-dictionary.js:78) haben den Guard `if (!texts || texts.length === 0) { renderError('Korpus ist noch nicht geladen ...'); return; }`. In playground-main.js werden die Buttons in initializeEventListeners() (Zeile 94) verdrahtet, BEVOR `await this.loadAuthorityIndex()` und `await this.autoLoadCorpus()` laufen. Zwischen Authority-Load (fertig zuerst) und Corpus-Load (40 MB gz-Dekompression, mehrere Sekunden) ist window.playground.corpusData noch undefined.

**Fehlerszenario:** Erstbesuch/langsame Verbindung: Nutzer öffnet die Multi-Lemma-Suche, tippt „minne, êre" und klickt Ausführen, während der Corpus-Index noch lädt (Authority ist schon da). resolveLemmaIds() liefert gültige Lemma-IDs, aber teiManager.searchMultipleLemmasUsingIndex() sieht window.playground.corpusData === undefined (tei-manager.js:901-910) und fällt auf die XML-Suche über das leere teiData.parsedXML zurück → Rückgabe []. Die UI zeigt definitiv „keine Kookkurrenzen/Treffer" für eine Anfrage, die tatsächlich tausende Belege hat.

```
const teiManager = window.playground?.teiManager;
        if (!teiManager) {
```
**Vorschlag:** Analog zu den anderen Werkzeugen zu Beginn von executeSearch() prüfen, ob der Corpus geladen ist (z.B. window.playground?.corpusData?.texts?.length > 0 bzw. teiManager.corpusIndex), und bei Nichtvorhandensein eine „Korpus wird noch geladen"-Meldung im resultsContainer anzeigen statt eine leere Suche auszuführen.


### 23. `playground/js/ui/tei/text-comparison.js:132` — Bug
*Lemma-Filter im Textvergleich ignoriert die MHG-Normalisierung und findet diakritische Lemmata nicht*

filterByName vergleicht rein mit toLowerCase().includes() ohne die zentrale MHG-Normalisierung (â→a, ê→e, ...). Rund 30% der Lexikon-Lemmata tragen Diakritika (verifiziert: 1505 von 5000 Lemmata, z.B. 'tôtwunt', 'ûfgân', 'lîm'). Dadurch liefert der Filter unvollständige Ergebnisse, wenn die Nutzerin die Sonderzeichen weglässt. Das widerspricht dem harten Vertrag (c) zur zentralisierten Normalisierung und ist inkonsistent zum Schwester-Werkzeug naming-explorer.js, das für exakt diesen Fall TextNormalizer.matchesNormalized() nutzt (dortiger Kommentar Z.208: 'damit "riter" auch "rîter"/"rîtaere" findet').

**Fehlerszenario:** Nutzerin vergleicht zwei Texte und tippt im Lemma-Filter 'tot' (ohne Zirkumflex). Das Lemma 'tôtwunt' bleibt unsichtbar, obwohl es in der Ergebnismenge liegt → gefiltertes Ergebnis wirkt leer/unvollständig, Trefferzahl im Tab und in der Tabelle divergieren gefühlt.

```
const f = this.state.nameFilter.trim().toLowerCase();
    if (!f) return rows;
    return rows.filter(r => (r.lemma || r.lemmaId).toLowerCase().includes(f));
```
**Vorschlag:** filterByName analog zum naming-explorer über die zentrale Normalisierung führen, z.B. TextNormalizer.matchesNormalized(r.lemma || r.lemmaId, f) statt roher toLowerCase-includes-Vergleich; TextNormalizer importieren.


### 24. `scripts/audit/audit-authority-files.py:142` — Bug
*Referenz auf komplett fehlende Ziel-Datei wird still übersprungen statt als Orphan gemeldet*

**Fehlerszenario:** Ein Authority-File enthält z.B. <ref target="persosn.xml#person_5"/> (Tippfehler im Dateinamen) oder verweist auf eine noch nicht angelegte Authority-Datei. Da 'persosn.xml' nicht in all_ids liegt, ist die äußere Bedingung 'target_file in all_ids' False → die Referenz wird komplett übersprungen und landet nie in orphans. Der Report meldet 'No orphaned references found', obwohl die gravierendste Form eines gebrochenen Verweises (Zieldatei existiert gar nicht) vorliegt. Das korpus-seitige Pendant check-authority-cross-refs.py behandelt genau diesen Fall über missing_target_files — die Authority-Prüfung ist hier inkonsistent blind.

```
if target_file in all_ids:
            if fragment not in all_ids[target_file]:
                orphans.append({
```
**Vorschlag:** Einen else-Zweig ergänzen, der Refs mit fragment, deren target_file nicht in all_ids ist, als eigene Orphan-Kategorie ('missing target file') meldet.


### 25. `scripts/audit/doc-count-audit.py:98` — Bug
*Doc-Drift-Audit übersieht die dominante Korpus-Zählungs-Schreibweise „NNN Dateien" / „NNN Files" / „NNN TEI-Dateien" und meldet fälschlich „kein Drift"*

Der Keyword-Anker für `corpus_files` verlangt, dass unmittelbar nach der Zahl entweder „TEI" gefolgt von Whitespace und „files/Dateien" ODER „Korpus…" steht. Die in den Ziel-Docs tatsächlich vorherrschende Schreibweise ist aber bares „NNN Dateien" (TEI-MODEL.md L110/436/471/795/813), „NNN Files" (TEI-MODEL.md L923, ROADMAP.md L86) bzw. das deutsche Komposita „NNN TEI-Dateien" (Bindestrich statt Space). Der Anker `TEI(?:-XML)?\s+(?:files?|Dateien)` scheitert an all diesen Fällen: bares „Dateien"/„Files" hat kein TEI/Korpus-Präfix, und „TEI-Dateien" hat einen Bindestrich statt des geforderten `\s+`. Damit ist genau der Anwendungsfall unerkennbar, den der Kommentar (L96–99) explizit zu fangen behauptet („catches the common case 'WZB ingest bumped 666 -> 667 but doc still says 666'"). Der `--check`-Modus (CI-Freshness-Gate laut Docstring) gibt dadurch falsches Grün.

**Fehlerszenario:** Ein Ingest bumpt das Korpus von 667 auf 668, aber in docs/TEI-MODEL.md bleibt „667 Dateien" stehen. `python scripts/audit/doc-count-audit.py --check` läuft, `find_stale_numbers` findet die stale „667" nicht (Anker matcht bares „Dateien" nicht), meldet „No drift detected" und exit 0 — der CI-Gate lässt die veraltete Doku durch. Live reproduziert: gegen die aktuelle Zahl 667 werden „666 Dateien", „666 TEI-Dateien" und „666 Files" alle als MISSED zurückgegeben, während nur „666 TEI files" (Space) und „666 Korpus-Dateien" flagged werden.

```
'corpus_files': r'\s*(?:TEI(?:-XML)?\s+(?:files?|Dateien)|Korpus(?:-?[Dd]ateien)?)',
```
**Vorschlag:** Den Anker um die bloße Nomen-Form erweitern, z.B. `r'\s*(?:TEI(?:[-\s]XML)?[-\s]?(?:files?|Dateien)|Korpus(?:[-\s]?[Dd]ateien)?|Dateien|Files?)'`, sodass „Dateien"/„Files"/„TEI-Dateien" ebenfalls greifen; alternativ ein separates, generisches „Dateien|Files"-Muster mit engem Drift-Fenster. Anschließend gegen die bestehenden historischen 666er-Belege (die bewusst stehen bleiben sollen) prüfen, um False Positives zu vermeiden.


### 26. `scripts/build-pages.py:188` — Bug
*CRLF-Erhaltung ist wirkungslos, weil read_text() bereits alle Zeilenenden auf \n normalisiert — Docstring-Versprechen bricht*

**Fehlerszenario:** Windows-Checkout mit CRLF-Zeilenenden, eine registrierte Seite (z.B. korpus.html) wird durch geänderte Partials neu generiert. `raw = path.read_text(...)` liefert wegen Pythons Universal-Newlines bereits reinen \n-Text (verifiziert: eine \r\n-Datei ergibt raw.count('\r\n') == 0). Damit ist `crlf` immer 0, `lf_only` == Gesamtzeilenzahl, und `newline` wird IMMER '\n'. Beim Schreiben (`built.replace('\n', newline)`, Zeile 201) wird die ganze CRLF-Datei auf LF umgeschrieben — also genau der 'spurious whole-file diff on Windows checkouts', den der Modul-Docstring (Zeilen 28-30) explizit zu verhindern behauptet. `norm = raw.replace('\r\n','\n')` (Zeile 191) ist ebenfalls ein No-op.

```
crlf = raw.count("\r\n")
    lf_only = raw.count("\n") - crlf
    newline = "\r\n" if crlf > lf_only else "\n"
    norm = raw.replace("\r\n", "\n")
```
**Vorschlag:** Entweder die Datei roh (binär) einlesen, um die tatsächlichen Zeilenenden zu erkennen (`path.read_bytes()` und auf `b'\r\n'` zählen), oder `read_text(..., newline='')` verwenden (Newline-Übersetzung deaktiviert, ab Python 3.13 unterstützt), damit `raw` echte \r\n enthält und die Dominant-Style-Logik greift. Alternativ das Docstring-Versprechen streichen, falls CRLF-Erhaltung nicht gewünscht ist.


### 27. `scripts/ingest/ari/01-convert-original-to-mhdbdb.py:247` — Bug
*Header-Template-Befüllung escaped nur Anführungszeichen, nicht &/</> — Titel oder Source-URL mit '&' lässt etree.fromstring crashen*

title_de und source_url werden per str.format() roh in einen XML-Template-String eingesetzt, der danach mit etree.fromstring geparst wird. Escaped wird nur das Anführungszeichen (das im Elementtext gar nicht escaped werden müsste), während die XML-kritischen Zeichen &, < und > unbehandelt bleiben. Ein '&' oder '<' im Titel oder in der Source-URL erzeugt nicht-wohlgeformtes XML und lässt fromstring mit XMLSyntaxError abbrechen.

**Fehlerszenario:** Aufruf mit --title-de "Nürnberg, Cent. V, 64 & 65" (Sammelhandschrift) oder mit einer GAMS-Source-URL mit Query-Parametern (…?context=a&format=b) → das eingesetzte '&' steht roh in <title>…&…</title> bzw. target="…&…" → etree.fromstring wirft lxml.etree.XMLSyntaxError → das Konvertierungsskript bricht mit Traceback ab, obwohl die CLI-Eingabe gültig war.

```
title_de=title_de.replace('"', "&quot;"),
```
**Vorschlag:** Statt der manuellen replace-Logik xml.sax.saxutils.escape() auf title_de und source_url anwenden (für Attributwerte quoteattr bzw. escape inkl. "), oder den Header nicht per String-Format, sondern per lxml-Elementbau mit .text/.set() erzeugen, sodass lxml selbst escaped.


### 28. `scripts/ingest/wzb/wzb-apply-lemmarefs.py:42` — Bug
*PROJECT_ROOT zeigt auf scripts/ingest - Default-TEI/TSV-Pfade sind falsch*

**Fehlerszenario:** In scripts/ingest/wzb/ liefert .parent.parent = scripts/ingest, also DEFAULT_TEI = scripts/ingest/Wenzelsbibel/WZB.lemma-autofill.tei.xml (existiert nicht). Ohne explizite --tei/--tsv-Angabe scheitert etree.parse in Zeile 83 mit Datei-nicht-gefunden. Zusaetzlich zeigt der Docstring in Zeile 44 selbst, dass die DEFAULT_TSV auf 'phase1b' liegt - inkonsistente Annahme ueber das Wurzelverzeichnis.

```
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_TEI  = PROJECT_ROOT / "Wenzelsbibel" / "WZB.lemma-autofill.tei.xml"
```
**Vorschlag:** PROJECT_ROOT auf das Repo-Root korrigieren (.parent.parent.parent.parent).


### 29. `scripts/ingest/wzb/wzb-extract-unmatched.py:23` — Bug
*PROJECT_ROOT zeigt auf scripts/ingest - REPORT_CSV existiert nie und es gibt keinen CLI-Override*

**Fehlerszenario:** In scripts/ingest/wzb/ liefert .parent.parent = scripts/ingest, also REPORT_CSV = scripts/ingest/Wenzelsbibel/reports/... - dieser Pfad existiert nicht (Wenzelsbibel/ liegt im Repo-Root). Das Skript hat keine argparse-Optionen, die Konstanten sind hartkodiert; Zeile 28-30 bricht mit 'ERROR: missing report file' ab, obwohl der Report unter Wenzelsbibel/reports/ tatsaechlich vorliegt. Der Extract-Schritt ist ohne Codeaenderung nicht ausfuehrbar.

```
PROJECT_ROOT = Path(__file__).parent.parent
REPORT_CSV = PROJECT_ROOT / 'Wenzelsbibel' / 'reports' / 'wzb-auto-match-report.csv'
```
**Vorschlag:** PROJECT_ROOT = Path(__file__).parent.parent.parent.parent (Repo-Root) verwenden.


### 30. `scripts/ingest/wzb/wzb-generate-tsv.py:22` — Bug
*PROJECT_ROOT zeigt auf scripts/ingest - Default-Pfade fuer Report und TSV-Ausgabe sind falsch*

**Fehlerszenario:** In scripts/ingest/wzb/ ist .parent.parent = scripts/ingest; die Defaults verweisen auf das nicht existierende scripts/ingest/Wenzelsbibel/. Ohne die (vorhandenen) --report/--output-Flags bricht Zeile 36-38 mit 'report file not found' ab, obwohl der Report im Repo-Root-Wenzelsbibel/reports/ liegt. Wartungsfalle: die dokumentierte Standardnutzung `python scripts/wzb-generate-tsv.py` funktioniert nicht.

```
PROJECT_ROOT = Path(__file__).parent.parent
REPORT_CSV = PROJECT_ROOT / 'Wenzelsbibel' / 'reports' / 'wzb-auto-match-report.csv'
OUTPUT_TSV = PROJECT_ROOT / 'Wenzelsbibel' / 'phase1b' / 'wzb-disambiguation.tsv'
```
**Vorschlag:** PROJECT_ROOT auf das Repo-Root korrigieren (.parent.parent.parent.parent).


### 31. `scripts/ingest/wzb/wzb-pos-apply.py:37` — Bug
*PROJECT_ROOT = parent.parent löst nach der Reorg auf scripts/ingest statt auf das Repo-Root auf — alle Default-Pfade zeigen ins Leere*

**Fehlerszenario:** Datei liegt unter scripts/ingest/wzb/. Path(__file__).parent.parent = /repo/scripts/ingest (verifiziert), das Repo-Root wäre erst parents[3]. Dadurch ist DEFAULT_TEI = scripts/ingest/Wenzelsbibel/WZB.lemma-autofill.tei.xml und DEFAULT_LEX/PENDING analog — alle unter scripts/ingest/, wo weder Wenzelsbibel/ noch authority-files/ existieren (verifiziert: exists() == False). Ein Aufruf ohne explizite --tei/--pending-Argumente scheitert mit FileNotFoundError bei etree.parse bzw. beim Öffnen der TSV. Gleicher Fehler in wzb-pos-assign.py (Z. 37), wzb-sense-apply.py (Z. 43) und wzb-sense-assign.py (Z. 45).

```
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_TEI     = PROJECT_ROOT / "Wenzelsbibel" / "WZB.lemma-autofill.tei.xml"
```
**Vorschlag:** Um eine Ebene tiefer korrigieren: PROJECT_ROOT = Path(__file__).resolve().parents[3] (bzw. drei zusätzliche .parent) in allen vier betroffenen Skripten.


### 32. `scripts/ingest/wzb/wzb-sense-bulk-resolve.py:32` — Bug
*PROJECT_ROOT zeigt nach Reorg auf scripts/ingest — Default-Pending-TSV nicht gefunden*

Gleiche Ursache wie in baseline.py: Path(__file__).parent.parent == scripts/ingest, daher zeigt DEFAULT_PENDING (Zeile 33) auf scripts/ingest/Wenzelsbibel/phase3/wzb-sense-pending.tsv statt auf das Repo-Root-Verzeichnis. Die eigentliche Pending-TSV liegt unter <repo>/Wenzelsbibel/. Der Docstring-Aufruf (Zeile 20) setzt nur -r (Resolutions), verlässt sich für --pending auf den Default.

**Fehlerszenario:** `python scripts/ingest/wzb/wzb-sense-bulk-resolve.py -r <resolutions.tsv>` ohne explizites --pending: pending_path.exists() ist False → 'ERROR: pending TSV not found' und sys.exit(1). Die dokumentierte Bulk-Auflösung schlägt fehl, solange man --pending nicht manuell auf den Repo-Root-Pfad setzt.

```
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_PENDING = PROJECT_ROOT / "Wenzelsbibel" / "phase3" / "wzb-sense-pending.tsv"
```
**Vorschlag:** PROJECT_ROOT = Path(__file__).parent.parent.parent verwenden.


### 33. `scripts/ingest/wzb/wzb-sense-evaluate.py:424` — Bug
*Asymmetrisches strip() bei ABSTAIN-Partitionierung — whitespace-behaftetes ABSTAIN wird doppelt gezählt und verfälscht die Accuracy*

Der abstain-Filter normalisiert mit .strip().upper() == 'ABSTAIN', der evaluated-Filter prüft die ABSTAIN-Ausnahme aber ohne strip (r.get('resolved_sense','').upper() != 'ABSTAIN', Zeile 425). Ein Wert mit umgebendem Whitespace (z. B. ' ABSTAIN', von einem LLM/TSV leicht erzeugt) landet damit gleichzeitig in abstain UND evaluated (verifiziert). Dadurch gilt n_abstain + n_eval + n_missing > n_total, und die vermeintliche Abstention geht als falsch klassifizierter Token in die Accuracy-Berechnung (correct/n_eval) ein, senkt also die berichtete Genauigkeit und macht die ABSTAIN-Rate inkonsistent.

**Fehlerszenario:** Resolved-TSV enthält eine Zelle ' ABSTAIN' (führendes Leerzeichen): Token zählt als ABSTAIN und zugleich als evaluated; sense_match schlägt fehl → als incorrect gewertet. Berichtete OVERALL ACCURACY und Stratum-Werte fallen niedriger aus als real, obwohl die Zeile eine Abstention ist.

```
abstain   = [(g, r) for g, r in joined if r.get("resolved_sense","").strip().upper() == "ABSTAIN"]
evaluated = [(g, r) for g, r in joined if r.get("resolved_sense","").strip() and r.get("resolved_sense","").upper() != "ABSTAIN"]
```
**Vorschlag:** In beiden Filtern denselben normalisierten Wert verwenden, z. B. rs = r.get('resolved_sense','').strip().upper() einmal berechnen und abstain via rs=='ABSTAIN', evaluated via rs and rs!='ABSTAIN' partitionieren.


### 34. `scripts/ingest/wzb/wzb-structural-cleanup.py:78` — Bug
*roman_to_arabic in cleanup ist nicht space-tolerant und liefert falsche Kapitelnummer fuer getrennt tokenisierte Subtraktions-Ziffern*

Die CAPITULUM-Nummer wird aus mehreren benachbarten <w>-Geschwistern zusammengesetzt und mit Leerzeichen verbunden (numeral_text = 'I X'). Die lokale roman_to_arabic() entfernt diese Leerzeichen NICHT: die Schleife setzt bei jedem Space-Zeichen v=0 und damit prev=0, wodurch die Subtraktionslogik (kleinere Ziffer vor groesserer) zerbricht. 'I X' ergibt 11 statt 9 (IX). Das falsche arabic_n wird als @n auf das erzeugte <head type='chapter'> geschrieben. wzb-structural-fix.py besitzt eine ZWEITE, abweichende, space-tolerante Implementierung derselben Funktion (t.replace(' ', '')), die den Wert spaeter wieder korrigiert (belegt im Docstring von fix.py). In der dokumentierten Pipeline landen alle 106 Marker in <l>/<p> und werden von fix.py neu berechnet, sodass der Fehler maskiert ist; die von cleanup.py geschriebene Zwischendatei enthaelt aber @n=11 fuer Kapitel IX, und die duplizierte-aber-divergente Funktion ist eine Wartungsfalle, sobald der Fix-Schritt entfernt/umgestellt wird oder ein Marker nicht in <l>/<p> steht.

**Fehlerszenario:** Realdaten Wenzelsbibel/WZB.tei.xml: CAPITULUM mit Folge-Ziffern <w>I</w><w>X</w> (Kapitel 9). collect_capitulum_group liefert numeral_text='I X', roman_to_arabic('I X') liefert 11 statt 9 -> head_el bekommt n='11'. Die von cleanup.py geschriebene Datei traegt fuer das 9. Kapitel die Nummer 11. Nur weil wzb-structural-fix.py denselben Head danach mit seiner eigenen space-toleranten roman_to_arabic neu berechnet, erscheint am Ende 9.

```
t = text.strip()
    result, prev = 0, 0
    for ch in reversed(t):
        v = vals.get(ch, 0)
        result = result - v if v < prev else result + v
```
**Vorschlag:** Nur EINE roman_to_arabic-Implementierung verwenden (die space-tolerante aus fix.py in ein gemeinsames Modul ziehen und in cleanup.py importieren), damit beide Skripte garantiert dieselbe Semantik haben und die Zwischendatei bereits korrekte @n-Werte enthaelt.


### 35. `scripts/insert-stanzas-from-linecode.py:244` — Bug
*Nicht aufgelöster Zwischen-Anker lässt die vorige Strophe bis zum Container-Ende überlaufen (Strophen-Überlappung / geschachtelte <lg>)*

**Fehlerszenario:** Anker-Liste [A0, A1, A2] mit first_ls = [L0, None, L2] (A1 ist z.B. ein als <head>/<supplied> gerenderter Abschnittstitel, für den find_first_l_for_anchor auch nach 12 Kandidaten kein <l> findet → None, dokumentierter Fall). Bei idx=0 ist first_ls[1] None, deshalb greift NICHT der Grenzfall-Zweig, sondern der else-Zweig 'letzte Strophe': L0 läuft per Vorwärts-Walk bis zum letzten <l> des Elternknotens und verschlingt damit die Verse von A1 UND A2. Sind alle Elemente von L0 bis Ende <l> (Titel liegt in separatem Container, vgl. Kommentar Z.268), verschiebt wrap_stanza sie alle in <lg n='1'>. Danach hat L2 als Elternknoten dieses neue <lg>; bei idx=2 wird L2 erneut gewrappt und erzeugt ein VERSCHACHTELTES <lg n='3'> innerhalb von <lg n='1'>. Da dieses Skript (anders als die 138er-Skripte) keinerlei Token-/Count-Invariante nach dem Umbau prüft und trotzdem schreibt (stats['wrapped']>0), landet die kaputte, überlappende/geschachtelte Strophenstruktur auf der Platte.

```
if idx + 1 < len(anchors) and first_ls[idx + 1] is not None:
```
**Vorschlag:** Die Strophengrenze muss zum nächsten AUFGELÖSTEN Anker springen, nicht nur zum unmittelbar folgenden. Statt 'first_ls[idx+1] is not None' den nächsten Index j>idx mit first_ls[j] is not None suchen und dessen first_l als Grenze verwenden; nur wenn kein weiterer aufgelöster Anker existiert, den Vorwärts-Walk bis Container-Ende nutzen. Zusätzlich analog zu den 138er-Skripten eine Token-Sequenz-Invariante nach dem Umbau prüfen und bei Verletzung abbrechen.


### 36. `scripts/insert-stanzas-from-linecode.py:281` — Bug
*Strophen-@n als idx+1 erzeugt Nummerierungslücken (n=1, n=3) sobald ein Anker übersprungen wird — widerspricht der zugesagten fortlaufenden Nummerierung*

**Fehlerszenario:** Bei 3 Ankern, von denen idx=1 nicht aufgelöst werden kann (missing_anchors) oder für den wrap_stanza False zurückgibt (wrap_failed, z.B. 'parent mismatch' — beides sind explizit vorgesehene Fälle mit eigenem Stats-Feld), werden die verbleibenden Strophen mit n=idx+1 = 1 und 3 geschrieben. Die resultierende TEI hat <lg n='1'> direkt gefolgt von <lg n='3'>, ohne n='2'. Das widerspricht dem Modul-Docstring (Z.17-19: 'N is assigned sequentially (1, 2, 3, ...) per KZW-decision') und liefert falsche Strophen-Metadaten. Das Skript schreibt trotzdem (kein Abbruch bei missing_anchors/wrap_failed).

```
if wrap_stanza(first_l, last_l, idx + 1):
```
**Vorschlag:** Einen eigenen, nur bei tatsächlichem Erfolg inkrementierten Zähler für @n verwenden (z.B. stanza_n = len(erfolgreich gewrappt)+1) statt des Anker-Index idx+1, damit die @n-Werte lückenlos 1..k bleiben.


### 37. `scripts/sync/enhance_works_with_zotero.py:264` — Bug
*convert_to_title_case zerstört mit str.capitalize() Binnenmajuskeln, Bindestrich-Komposita und Akronyme in Titeln*

**Fehlerszenario:** Ein Zotero-Item liefert title/bookTitle/series wie "Prosa-Lancelot", "Vers-Roman", "MTU" oder "Neuausgabe des ATB-Textes". str.capitalize() macht nur den ersten Buchstaben groß und alle folgenden klein: "Prosa-Lancelot" -> "Prosa-lancelot", "MTU" -> "Mtu", "...ATB-Textes" -> "...atb-textes". Der verfälschte Titel wird in den generierten <biblStruct> geschrieben, landet in works.xml und über den Build in Authority-Index und öffentlicher JSON-API. Live verifiziert; solche Bindestrich-Komposita (Prosa-Lancelot, Theophilus-Spiel, Tristan-Fortsetzung) existieren real im Bestand.

```
result.append(clean_word.capitalize() + trailing_punct)
```
**Vorschlag:** Statt clean_word.capitalize() nur den ersten Buchstaben anheben und den Rest unberührt lassen (z.B. clean_word[0].upper() + clean_word[1:]) oder mindestens Wörter mit Binnenmajuskeln/Bindestrich-Segmenten und All-Caps-Akronyme von der Kleinschreibung ausnehmen; Segmente nach Bindestrich separat behandeln.


### 38. `tailwind.config.js:3` — Bug
*Tailwind content-Globs listen 8 Hilfe-/Rechtsseiten nicht, deren Utility-Klassen werden aus tailwind-output.css gepurgt*

Das content-Array scannt nur 6 HTML-Dateien (index, korpus, woerterbuch, playground/index, lemma/index, testing/test) plus die JS-Verzeichnisse. Es gibt aber 14 HTML-Seiten, die assets/css/tailwind-output.css einbinden. Die 8 nicht gescannten Seiten hilfe.html, hilfe-daten.html, hilfe-daten-beitragen.html, hilfe-korpussuche.html, hilfe-playground.html, hilfe-schema.html, impressum.html und barrierefreiheit.html werden von Tailwind nie gesehen. Jede Utility-Klasse, die ausschliesslich auf diesen Seiten vorkommt (und in keiner gescannten Datei/JS), wird beim Purge aus der minifizierten Ausgabe entfernt. Verifiziert gegen die aktuell committete assets/css/tailwind-output.css: py-12, mb-16, pt-6, gap-x-8, h-10, w-10, border-b-2, border-transparent, -mb-px, hover:border-slate-300, group-hover:text-brand-700 sowie list-decimal und ml-4 fehlen komplett in der CSS-Datei, werden aber auf diesen Seiten verwendet. py-12 kommt in keiner gescannten Seite vor, group-hover:text-brand-700 nur in den Hilfe-Seiten, list-decimal nirgends in der Ausgabe.

**Fehlerszenario:** Nutzer oeffnet impressum.html oder hilfe.html: Der Haupt-Container mit class="py-12" erhaelt keine vertikale Innenabstand-Regel (Klasse ist aus tailwind-output.css gepurgt) -> Layout klebt oben/unten zusammen. In hilfe.html funktioniert das Nav-/Karten-Hover (group + group-hover:text-brand-700) nicht, weil beide Klassen fehlen. In barrierefreiheit.html verlieren die rechtlich nummerierten Listen ihre Nummerierung (list-decimal fehlt). Sichtbar kaputtes Styling auf realen, nutzer-facing Seiten nach jedem `npm run build:css`.

```
content: [
    './index.html',
    './korpus.html',
    './woerterbuch.html',
    './playground/index.html',
    './lemma/index.html',
    './testing/test.html',
    './assets/js/**/*.js',
    './playground/js/**/*.js',
    './lemma/**/*.js',
  ],
```
**Vorschlag:** content-Array um alle Seiten erweitern, die tailwind-output.css einbinden, z.B. Glob './*.html' statt der Einzelaufzaehlung (deckt hilfe-*.html, impressum.html, barrierefreiheit.html automatisch ab) plus die Unterverzeichnis-HTMLs; danach build:css neu ausfuehren und tailwind-output.css committen.


### 39. `testing/tests/cross-reference-test.spec.js:26` — Bug
*Work→Author-Test bestätigt bei fehlendem Button-Label leer und testet dann nichts*

**Fehlerszenario:** Die einzige Assertion (`expect(authorSearch).toBeGreaterThan(0)`) liegt im if-Zweig. Ändert sich das Button-Label '→ Autor' (z.B. auf '→ Verfasser') oder liefert die Suche 'Predigt' keine Treffer mit Autor-Link, ist `hasAuthorLink === 0`, der else-Zweig loggt nur 'No author links found' und der Test wird ohne jede Assertion grün. Ein reales Brechen der Work→Author-Navigation bliebe unbemerkt.

```
const hasAuthorLink = await page.locator('button:has-text("→ Autor")').count();

        if (hasAuthorLink > 0) {
```
**Vorschlag:** Vor der if-Prüfung `expect(hasAuthorLink).toBeGreaterThan(0)` erzwingen (mit einem Suchbegriff, der garantiert Autor-Links liefert), damit das Ausbleiben der Links als Fehler gilt statt als stiller Erfolg.


### 40. `testing/tests/cross-reference-test.spec.js:53` — Bug
*Tautologische Assertion prüft Lemma→Concept-Verknüpfung gar nicht und kann nie fehlschlagen*

**Fehlerszenario:** page.evaluate(...) gibt immer einen Boolean zurück (true oder false), nie undefined. Damit ist `hasConceptLinks !== undefined` konstant true und die Assertion kann nie rot werden. Verschärfend: die Lemma-Objekte in authorityData.lemmata besitzen gar kein `.concepts`-Feld (in playground/js/data/authority-manager.js wird `.concepts` nirgends gesetzt), weshalb `lemmata.some(l => l.concepts && l.concepts.length > 0)` faktisch immer false liefert. Der Test loggt also dauerhaft 'No concept annotations found' und würde selbst dann grün bleiben, wenn die im Test-Namen behauptete Lemma→Concept-Verknüpfung komplett fehlt.

```
expect(hasConceptLinks !== undefined).toBe(true);
```
**Vorschlag:** Entweder das reale Datenmodell verwenden (Concept-Zuordnung über den tatsächlichen Pfad concept→senses→lemmata bzw. die Struktur, die concept-distribution.js nutzt) und darauf eine echte Assertion setzen, oder den Test entfernen. `x !== undefined` als Zusicherung streichen.


### 41. `testing/tests/visual-mobile-test.spec.js:118` — Bug
*Touch-Target-Test besteht vakuös, wenn keiner der geprüften Buttons eine Bounding-Box hat*

**Fehlerszenario:** minHeight startet bei Infinity und wird nur für Buttons mit sichtbarer Bounding-Box aktualisiert. Sind die ersten 10 `button`-Elemente unsichtbar (display:none / 0-Höhe, z.B. eingeklappte Karten oder Modal-Buttons im DOM), bleibt jede boundingBox() null, minHeight bleibt Infinity und `Infinity >= 44` ist true — der Test bestätigt Touch-Tauglichkeit, ohne einen einzigen Button gemessen zu haben. Dasselbe Muster beim Main-Site-Test (Zeile 94: `if (searchBtnBox)` ohne else-Assertion) lässt den Test bei fehlender Bounding-Box komplett assertionslos durchlaufen.

```
let minHeight = Infinity;
    for (let i = 0; i < Math.min(count, 10); i++) {
        const box = await buttons.nth(i).boundingBox();
        if (box) {
            minHeight = Math.min(minHeight, box.height);
        }
    }

    expect(minHeight).toBeGreaterThanOrEqual(44);
```
**Vorschlag:** Vor der Höhenprüfung sicherstellen, dass mindestens ein Button gemessen wurde (z.B. `expect(minHeight).not.toBe(Infinity)` bzw. nur sichtbare Buttons via `:visible`-Locator einsammeln), und im Main-Site-Test einen else-Zweig oder ein vorheriges `toBeVisible()` erzwingen.


### 42. `assets/js/rendering/text-renderer.js:30` — Dead Code
*Der gesamte Render-/Highlight-Pfad von TextRenderer ist toter Code – nur der Cache wird genutzt.*

**Fehlerszenario:** app.js instanziiert TextRenderer nur, um an dessen `cache` zu kommen (`new TEITextReader(corpusIndex, authorityIndex, this.textRenderer.cache)`, app.js:178). Die öffentlichen Methoden renderText/findLemmaContexts/extractContext/renderContext/navigateContext/updateNavigationButtons werden nirgends aufgerufen – grep über assets/, playground/, lemma/ findet keine externe `.renderText(`-Verwendung; sie rufen sich nur gegenseitig auf. Die eigentliche Leseansicht liegt vollständig in tei-text-reader.js (openReadingView). Konsequenz: Dieser ~200-Zeilen-Pfad dupliziert Positions- und Highlight-Logik (Kontextfenster, Vor/Zurück-Navigation), die parallel zur lebenden TEITextReader-Implementierung driftet. Ein Wartender, der hier einen Bug fixt oder Verhalten ändert, sieht keinerlei Wirkung auf der Website; umgekehrt wird eine Contract-Änderung (§B/§B.1) hier nie mitgezogen. Zudem enthält der tote Pfad bereits ein feineres Kontextmodell (schließt an p/div/ab/lg statt am Body an), was fälschlich als aktive Logik gelesen wird.

```
async renderText(textId, lemmaId, elements) {
        this.currentTextId = textId;
        this.currentLemmaId = lemmaId;
```
**Vorschlag:** Entweder die Render-/Navigations-Methoden aus text-renderer.js entfernen und die Klasse auf das Bereitstellen/Verwalten des TEICacheManager reduzieren (oder den Cache direkt in app.js/TEITextReader erzeugen), oder – falls historisch gewollt – klar als deprecated markieren. So bleibt nur eine Quelle der Positions-/Highlight-Wahrheit (tei-text-reader.js) erhalten.


### 43. `docs/DATA-MODEL.md:200` — Docs-Drift
*Authority-Index-Schema: persons.works ist ein String, kein Array*

Das Schema zeigt `works: ["work_001", ...]` (Array). Tatsächlich baut `_build_person_works_map()` in scripts/build-authority-index.py:173-175 einen komma-separierten String (`_person_works[pid] = ','.join(...)`), der in parse_persons (Zeile 219/224) unverändert als `works` gespeichert wird. Die Doku widerspricht sich selbst: der API-Abschnitt (DATA-MODEL.md:426) hält fest, dass `persons.works` erst beim API-Build „from comma-string to array" normalisiert wird — im Authority-Index ist es also ein String.

**Fehlerszenario:** Code, der laut Doku `person.works.forEach(...)` oder `person.works.map(...)` auf dem Authority-Index aufruft, wirft einen TypeError bzw. iteriert über einzelne Zeichen, weil `works` ein String wie "work_1,work_2" ist.

```
works: ["work_001", ...],
```
**Vorschlag:** Schema auf `works: "work_001,work_002"  // comma-separated string` ändern und auf den API-Normalisierungshinweis verweisen.


### 44. `docs/DATA-MODEL.md:216` — Docs-Drift
*Authority-Index-Schema: biblStructs-Felder stimmen nicht mit build-authority-index.py überein*

Das dokumentierte Feld `biblStructs: [{type, key, title}]` widerspricht dem tatsächlichen Build. `parse_works()` in scripts/build-authority-index.py:347-352 emittiert pro biblStruct das Objekt `{'key': key, 'corresp': corresp, 'textContent': text_content}` — es gibt weder `type` noch `title`, dafür die undokumentierten Felder `corresp` und `textContent`.

**Fehlerszenario:** Ein Entwickler, der authority-index.json.gz gemäß Doku konsumiert und `work.biblStructs[i].title` bzw. `.type` liest, erhält immer `undefined`, weil die realen Felder `key`, `corresp`, `textContent` heißen.

```
biblStructs: [{type, key, title}],
```
**Vorschlag:** Zeile auf `biblStructs: [{key, corresp, textContent}]` korrigieren.


### 45. `playground/js/data/authority-manager.js:135` — Refactoring
*3-Stufen-Lemma-Auflösung doppelt implementiert - Stage-3-Partial-Match driftet zwischen Hauptseite (bidirektional) und Playground (einseitig)*

**Fehlerszenario:** Dieselbe dokumentierte '3-Stufen-Lemma-Auflösung' existiert zweimal: assets/js/search/search-engine.js:119-147 (Hauptseite) und playground/js/data/authority-manager.js:99-138 (Playground). In Stage 3 (Partial Match) driften sie: search-engine.js:142 prüft BIDIREKTIONAL (`lemma.normalized.includes(normalized) || normalized.includes(lemma.normalized)`), authority-manager.js:135 nur EINSEITIG via matchesNormalized (= `normalizedText.includes(normalizedSearch)`, also nur lemma.includes(suchbegriff)). Eingabe: Suchbegriff, der ein Superset einer kurzen Lemma-Normalform ist (z.B. Lemma normalisiert 'min', Suchbegriff 'minne'). Hauptseite: `'minne'.includes('min')` → true → Lemma 'min' wird aufgelöst und im Korpus getroffen. Playground: `'min'.includes('minne')` → false → kein Treffer. Für exakt dieselbe Nutzereingabe liefern Hauptseiten-Suche und Playground-Suche unterschiedliche Lemma-Auflösung und damit unterschiedliche Ergebnismengen.

```
return TextNormalizer.matchesNormalized(lemma.lemma, orthography);
```
**Vorschlag:** Die 3-Stufen-Auflösung in ein gemeinsames Modul (z.B. assets/js/lib/) ziehen, das beide Seiten importieren - analog zu lemma-match.js/text-normalizer.js. Bis dahin mindestens die Partial-Match-Richtung angleichen (eine der beiden Varianten als kanonisch festlegen und in CONTRACTS dokumentieren).


### 46. `playground/js/data/tei-manager.js:349` — Dead Code
*Toter CSV-Export-Cluster in TEIFilesManager (exportWordsAsCSV/exportLinesAsCSV/exportAnnotationsAsCSV + arrayToCSV) wird nie aufgerufen*

Der komname unter dem Kommentar '==================== EXPORT FUNCTIONS ====================' definierte Block aus exportWordsAsCSV() (349), exportLinesAsCSV() (362), exportAnnotationsAsCSV() (373) sowie das nur von diesen drei genutzte arrayToCSV() (397) ist vollstaendig unerreichbar. Kein Aufrufer existiert, und arrayToCSV wird ausschliesslich von den drei toten Methoden referenziert. Der Cluster stammt aus einem alten Datenmodell (roher teiData.words/.lines/.annotations-Export) und ist mit dem vorgebauten Index-Modell nicht mehr Teil eines Nutzungspfads.

**Fehlerszenario:** Beweiskette Nicht-Referenzierung: grep -rn 'exportWordsAsCSV|exportLinesAsCSV|exportAnnotationsAsCSV' ueber assets/, playground/, lemma/, testing/ (inkl. *.html) liefert je genau EINE Zeile — die Definition selbst in tei-manager.js. Kein Aufruf, kein Router (router.js), keine onclick-Referenz in playground/index.html. arrayToCSV() (Z.397) wird nur von diesen drei toten Methoden aufgerufen (Z.359/370/383), sonst nirgends. Ergebnis: der gesamte Block ist unerreichbar und faellt beim Loeschen weg, ohne dass Verhalten sich aendert.

```
exportWordsAsCSV() {
        const headers = ['filename', 'text', 'pos', 'lemmaRef', 'line'];
        const rows = this.teiData.words.map(word => [
```
**Vorschlag:** Die vier Methoden exportWordsAsCSV/exportLinesAsCSV/exportAnnotationsAsCSV/arrayToCSV samt EXPORT-FUNCTIONS-Kommentarblock entfernen; sie referenzieren ausserdem das Legacy-Feld teiData.words/.lines/.annotations, das im Index-Modell nur noch als Rest-Struktur existiert.


### 47. `playground/js/data/tei-manager.js:481` — Parität
*CSS-Substring-Selektor lemmaRef*= umgeht lemma-match.js und über-matcht Lemma-IDs (#126-Muster)*

**Fehlerszenario:** Im XML-Fallback der Multi-Lemma-Dokumentsuche (searchMultipleLemmas, erreichbar über searchMultipleLemmasUsingIndex Zeile 908, wenn window.playground.corpusData nicht geladen ist, z. B. bei fehlgeschlagenem Index-Load) prüft containsAllLemmas per doc.querySelectorAll(`w[lemmaRef*="lexicon.xml#lemma_${lemmaId}"]`). Der Substring-Selektor *= matcht "lemma_308" auch in "lemma_3089" (jâmer). Suche nach Lemma 308 meldet daher Texte als Treffer, die nur 3089 enthalten; extractMatchingWordsFromDocument (Zeile 586) hebt dieselben falschen Wörter hervor. Das verletzt CONTRACTS §B.1, wegen dem lemma-match.js erstellt wurde, und divergiert vom korrekten Index-Pfad (searchDocumentUsingEnhancedIndex, exakte Key-Prüfung) sowie vom Proximity-Fallback findCooccurringLemmas (Zeile 518), der lemmaRefMatchesId korrekt nutzt.

```
const elements = doc.querySelectorAll(`w[lemmaRef*="lexicon.xml#lemma_${lemmaId}"]`);
```
**Vorschlag:** Analog zu Zeile 518/1124 über alle w[lemmaRef] iterieren und lemmaRefMatchesId(lemmaRef, `lemma_${lemmaId}`) prüfen; den *=-Selektor an den Zeilen 481, 551 und 586 entfernen. Auch die ungenutzten Helfer searchWordsInText (228) und findWordsByLemmaRef (235) benutzen .includes-Substring auf lemmaRef und sollten dieselbe Funktion verwenden bzw. entfernt werden.


### 48. `playground/js/data/tei-manager.js:1263` — Klarheit
*Proximity-Deduplizierung behält den zuerst startenden statt den distanzkürzesten Treffer — Log-Text behauptet Gegenteil*

Die Ergebnisse werden je Datei nach contextStart aufsteigend sortiert und der erste eines überlappenden Fensters behalten; spätere überlappende Treffer werden verworfen, ohne die Distanz zu vergleichen. Der Log-Text behauptet jedoch 'keeping shorter distance (existing vs result)'. Behauptung und Verhalten widersprechen sich; tatsächlich kann ein Treffer mit größerer Distanz erhalten und der engere verworfen werden.

**Fehlerszenario:** Zwei überlappende Nähe-Treffer im selben Text: der frühere hat distance 9, der spätere (größerer contextStart) distance 2. Der Deduplizierer behält den distance-9-Treffer und verwirft den distance-2-Treffer, loggt aber 'keeping shorter distance (9 vs 2)'. Dem Nutzer wird die weiter entfernte Kookkurrenz statt der engsten angezeigt.

```
console.log(`  🔄 Overlap detected: ${filename} [${result.contextStart}-${result.contextEnd}] overlaps with [${existing.contextStart}-${existing.contextEnd}], keeping shorter distance (${existing.distance} vs ${result.distance})`);
```
**Vorschlag:** Beim Overlap den Treffer mit kleinerer distance auswählen (bzw. den bestehenden ersetzen, wenn result.distance < existing.distance) und den Log-Text entsprechend anpassen.


### 49. `playground/js/ui/core/ui-helpers.js:413` — Parität
*Proximity-Anreicherung mappt Index-Positionen ohne den Leer-<w>-Filter des Build zurück auf DOM-Wörter (vierter, nicht mit #131 angeglichener Zählpfad)*

**Fehlerszenario:** Zustand: Ein künftiger Ingest fügt (wie in CONTRACTS §B/#131 ausdrücklich antizipiert) Platzhalter-/Gap-Tokens als <w lemmaRef> mit leerem Textinhalt ein. build-corpus-index.py überspringt diese (`if not text_content: continue`), sodass words[]/Positionen sie nicht mitzählen. enrichFileResults selektiert die Kontext-Wörter jedoch über `//tei:body//tei:w[@lemmaRef]` (ohne Leer-Filter) und schneidet mit `indexedWords.slice(result.contextStart, result.contextEnd)`. Dann ist indexedWords länger als words[] und um jedes vorangehende Leer-<w> verschoben → das Kontextfenster der Nähe-Suche zeigt die falschen Wörter und das Multi-Lemma-Highlight (lemmaRefMatchesId-Schleife) landet auf falschen Tokens. Heute 0 solcher Fälle (empirisch verifiziert: 7.533.447 <w lemmaRef>, 0 mit leerem Text), daher latent — aber genau der Drift, den #131 für Reader/KWIC bereits geschlossen hat, hier im vierten Pfad offen.

```
const xpathIndexed = doc.evaluate(
          '//tei:body//tei:w[@lemmaRef]',
          doc,
          nsResolver,
          XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
          null
        );
```
**Vorschlag:** Beim Aufbau von indexedWords zusätzlich den Textinhalt prüfen und leere <w lemmaRef> überspringen (analog `if not text_content: continue` in build-corpus-index.py bzw. dem `hasText`-Guard in tei-text-reader.js / kwic-service.js), damit indexedWords deckungsgleich mit dem Index-words[] ist. Idealerweise diesen Remap-Pfad ebenfalls durch position-parity.spec.js absichern (aktuell deckt der Test nur tei-text-reader.js ab).


### 50. `playground/js/ui/core/ui-helpers.js:414` — Refactoring
*Positionszählung im Playground zählt <w>[@lemmaRef] per XPath OHNE den Leertext-Guard, den alle anderen drei Kopien haben*

**Fehlerszenario:** Die harte Positionszählungs-Vertrag (CONTRACTS §B) verlangt: nur <w> mit @lemmaRef UND nicht-leerem Textinhalt zählen. Python build-corpus-index.py:207-209 (`if not text_content: continue`), assets/js/rendering/tei-text-reader.js:423-427 (`hasLemmaRef && hasText`) und assets/js/search/kwic-service.js:80-102 (`if (text) { ... if (lemmaRef) position++; }`) implementieren diesen Guard alle. Die Playground-Kopie in enrichFileResults zählt jedoch per XPath `//tei:body//tei:w[@lemmaRef]` ALLE lemmaRef-tragenden <w> unabhängig vom Textinhalt und sliced dieses Array mit den aus dem Python-Index stammenden `result.contextStart/contextEnd`. Eingabe: ein Korpus mit auch nur einem leeren `<w lemmaRef=...></w>` (Platzhalter-/Gap-Token, wie im tei-text-reader.js-Kommentar für künftige Ingests explizit gewarnt) → der Python-Index überspringt es, die JS-XPath-Liste enthält es → alle nachfolgenden Positionen sind gegen den Index verschoben → in der Playground-Nähe-Suche wird der falsche Kontext extrahiert und die falschen Wörter hervorgehoben. Aktuell 0 Korpusfälle, aber bei laufendem Ingest latent drift-anfällig.

```
'//tei:body//tei:w[@lemmaRef]',
```
**Vorschlag:** Statt roher XPath eine gemeinsame, den Vertrag durchsetzende Positions-Iteration verwenden (wie kwic-service.js sie bereits kapselt): leere <w>-Elemente (`textContent.trim() === ''`) beim Aufbau von indexedWords überspringen, damit die Playground-Zählung byte-genau der Python-Index-Zählung entspricht. Idealerweise die Zähllogik zentralisieren analog zu lemma-match.js.


### 51. `playground/js/ui/tei/tei-ui.js:121` — Refactoring
*Hartcodiertes 12-Eintrag-Lemma-Wörterbuch in tei-ui.js umgeht die zentrale Varianten-Auflösung (~257k Einträge)*

**Fehlerszenario:** resolveLemmaIds (tei-ui.js:83, aufgerufen aus multi-lemma-search.js:209) benutzt findLemmaIdByOrthography als 'fast path', der aus einem hartcodierten 12-Eintrag-Dictionary (brôt→879, wîn→7532, käse→26713 …) eine Lemma-ID zurückgibt und dabei die Authority-Daten NICHT konsultiert (short-circuit vor searchLemmaByOrthography). Diese IDs duplizieren, was die geteilte variants-Dictionary im authority-index bereits liefert. Eingabe: Nutzer sucht im Multi-Lemma-Tool nach 'wein' → immer ID 7532, ungeprüft. Wenn bei einem künftigen lexicon-Rebuild/Renumbering (aktiver Ingest, laufende Korrekturen) die ID eines dieser Lemmata wechselt, liefert die Playground-Multi-Lemma-Suche für genau diese 12 gängigen Begriffe still das falsche Lemma, während Hauptseite und alle anderen Pfade über die Authority-Auflösung korrekt bleiben.

```
const commonLemmas = {
            'brôt': '879',
            'brot': '879', 
            'wîn': '7532',
```
**Vorschlag:** Das hartcodierte commonLemmas-Dictionary streichen und ausschließlich über authorityManager.searchLemmaByOrthography (bzw. die zentrale variants-Auflösung) resolven, damit es keine zweite, driftende Quelle der Wahrheit für Lemma-IDs gibt.


### 52. `scripts/audit/audit-authority-files.py:96` — Dead Code
*Klassifizierungs-Zweig 'hierarchical' ist toter Code — von 'numeric' vollständig verdeckt*

**Fehlerszenario:** Eine xml:id wie 'concept_10000000' (alle 567 Concept-IDs und die 8-stelligen name-IDs haben genau diese Form) → der erste Zweig '^[a-z]+_\d+$' matcht bereits (beliebig viele Ziffern bis Zeilenende), also wird sie als 'numeric' gezählt. Der zweite Zweig '^[a-z]+_\d{8}$' kann für KEINE Eingabe je erreicht werden, weil jede 8-stellige Ziffernfolge auch '\d+$' erfüllt. Der Report weist 'hierarchical' dauerhaft als 0 aus und behauptet damit fälschlich, es gäbe keine hierarchischen Taxonomie-Codes, obwohl concepts.xml/names.xml ausschließlich aus solchen bestehen.

```
if re.match(r'^[a-z]+_\d+$', xid):
            id_formats['numeric'] += 1
        elif re.match(r'^[a-z]+_\d{8}$', xid):
            id_formats['hierarchical'] += 1
```
**Vorschlag:** Reihenfolge umdrehen (spezifischeres '^[a-z]+_\d{8}$' vor '^[a-z]+_\d+$' prüfen) oder den numeric-Zweig auf 1–7 Ziffern begrenzen (z.B. '^[a-z]+_\d{1,7}$'), damit 8-stellige IDs als 'hierarchical' erkannt werden.


### 53. `scripts/build-corpus-index.py:211` — Parität
*Corpus-Index-Build extrahiert Lemma-ID mit split('#')[1] und verarbeitet Mehrfach-lemmaRef nicht, anders als lemma-match.js*

**Fehlerszenario:** lemma-match.js unterstützt laut Doku und Vertrag (CONTRACTS §B.1) explizit whitespace-getrennte Mehrfachwerte in @lemmaRef, Beispiel `lexicon.xml#lemma_308 lexicon.xml#lemma_5`. Für ein solches <w> berechnet die JS-Leseansicht per lemmaRefMatchesId korrekt beide IDs und hebt das Wort hervor. Der Python-Indexer nimmt dagegen lemma_ref.split('#')[1], was für diesen Wert die Zeichenkette "lemma_308 lexicon.xml" liefert — ein defekter Key, unter dem das Wort im Index landet. Folge: das Wort ist über die indexbasierte Dokument-/Nähe-Suche und die Lemma-Zählungen unauffindbar, obwohl die Leseansicht es als Treffer markiert → sichtbare JS/Python-Divergenz zwischen Suche und Reader. Im aktuellen Korpus gibt es 0 Mehrfach-lemmaRef, aber bei laufendem Ingest (WZB/ARITHMETIC) erzeugt der erste solche <w> stillen Index-Drift ohne Fehlermeldung.

```
lemma_id = lemma_ref.split('#')[1] if '#' in lemma_ref else lemma_ref
```
**Vorschlag:** lemmaRef wie in lemma-match.js zuerst an Whitespace splitten und pro Fragment die ID nach '#' extrahieren, dann jedes so gewonnene lemma_id in words/lemmata eintragen. So bleiben Index-Build (Python) und Highlight/Contract (JS) für Mehrfachwerte konsistent.


### 54. `scripts/sync/enhance_works_with_zotero.py:802` — Docs-Drift
*Zur Laufzeit gedruckte NEXT-STEPS- und Usage-Pfade zeigen auf nicht existierendes Verzeichnis scripts/data-wrangling/*

**Fehlerszenario:** Nach erfolgreichem Lauf druckt das Skript "NEXT STEPS: 1. python scripts/data-wrangling/sync_tei_headers.py --works". Ein Nutzer kopiert dieses Kommando und erhält "No such file or directory", weil das Verzeichnis scripts/data-wrangling/ nicht existiert; das Skript liegt tatsächlich unter scripts/sync/sync_tei_headers.py. Dasselbe falsche Präfix steht im Modul-Docstring (Zeilen 23-35) und im argparse-Epilog (Zeilen 721-733), inklusive des Selbstaufrufs dieses Skripts.

```
logger.info("  1. python scripts/data-wrangling/sync_tei_headers.py --works")
```
**Vorschlag:** Alle Pfad-Referenzen von scripts/data-wrangling/ auf scripts/sync/ korrigieren (Docstring, Epilog und beide NEXT-STEPS-Zeilen).


### 55. `testing/tests/search-with-corpus.spec.js:194` — Dead Code
*Test 'Search 10: XPath Query on TEI' ist ein garantierter No-Op ohne jede Assertion*

**Fehlerszenario:** Der gesamte if-Zweig hängt an `xpathInput.isVisible()`. Ein grep über das komplette playground/-Verzeichnis findet weder `xpathInput` noch `xpathTarget` irgendwo (kein HTML-Element, kein JS). Der Zweig ist also unerreichbar; der Test nimmt IMMER den else-Zweig, der nur `console.log` ausführt und nichts prüft. Ergebnis: Der Test ist dauerhaft grün, selbst wenn die gesamte TEI-Suchfunktion kaputt wäre — er testet nichts.

```
if (await xpathInput.isVisible({ timeout: 2000 }).catch(() => false)) {
```
**Vorschlag:** Test löschen oder mit `test.skip(true, 'XPath-UI im Redesign entfernt')` explizit als übersprungen markieren, statt einen dauerhaft grünen Schein-Test zu behalten.


### 56. `testing/tests/tei-caching.spec.js:32` — Dead Code
*'first load caches TEI file' verifiziert kein Caching — networkFetch wird berechnet, aber nie assertiert*

**Fehlerszenario:** Die Variable networkFetch wird aus den Konsolen-Logs berechnet, danach aber nie in einer expect-Zusicherung verwendet. Die einzige Assertion des Tests ist titleText.length>0. Regressions-Szenario: Wenn der Cache-Schreibpfad (cache.set nach fetch) komplett bricht, bleibt der Test grün, weil er nur prüft, dass überhaupt ein Titel geladen wurde. Der Testname 'first load caches TEI file' behauptet etwas, das der Test nicht prüft.

```
const networkFetch = logs.some(log => log.includes('Fetching from network') || log.includes('fetch'));
```
**Vorschlag:** Entweder auf networkFetch assertieren (expect(networkFetch).toBe(true)) und anschließend prüfen, dass der Cache-Eintrag via cache.getEntry existiert, oder die tote Variable und den irreführenden Testnamen entfernen.


### 57. `testing/tests/tei-caching.spec.js:58` — Klarheit
*'second load uses cache (faster)' misst Ladezeit, assertiert sie aber nie; Cross-Test-Cache-Annahme trägt in isolierten Playwright-Contexts ohnehin nicht*

**Fehlerszenario:** Kommentar behauptet 'Cached load should be notably faster than first load', doch loadTime wird nur geloggt, nie assertiert (einzige Assertion: titleText.length>0). Zusätzlich läuft jeder Playwright-Test in einem frischen Browser-Context mit isoliertem IndexedDB, sodass die Prämisse 'same text as first test' (Cache aus dem vorherigen Test) gar nicht gilt. Regressions-Szenario: Selbst wenn Caching völlig deaktiviert wäre und jeder Load 60s bräuchte (Timeout 15s würde greifen) — solange irgendein Titel < 15s erscheint, ist der Test grün und meldet keine Geschwindigkeits-Regression.

```
// Cached load should be notably faster than first load
```
**Vorschlag:** Innerhalb EINES Tests zweimal denselben Text laden (erster Load primt den Cache, zweiter misst) und eine relative Zeit-/Netzwerk-Assertion setzen (z.B. keine Netzwerk-Fetches beim zweiten Load, analog Zeile 172-196), statt auf Test-übergreifenden Cache zu bauen.


---

## ⚪ Low (56)

### 58. `assets/js/rendering/tei-text-reader.js:395` — Bug
*Datums-/Jahres-Notizen rendern als Badge ohne Kinder – latente Verletzung der Positionszählungs-Parität (§B).*

**Fehlerszenario:** Im Reader wird eine `<note type="date|year" n="...">` als Badge zurückgegeben, OHNE children() aufzurufen (Zeile 395-397). Dadurch durchläuft der `<w>`-Zweig (Zeile 414-428) für Wörter innerhalb einer solchen Notiz nie `state.wordPosition++`. build-corpus-index.py (iterwalk über ALLE `<w lemmaRef>` im body, Zeile 204-216) und kwic-service.js (TreeWalker über den kompletten body, Zeile 78-102) zählen diese `<w>` dagegen mit. Trigger-Szenario: Sobald eine Datums-/Jahres-Notiz ein lemmatisiertes `<w>` mit Textinhalt enthält, verschiebt sich im Reader jede nachfolgende Highlight-Position gegenüber dem Index um genau die Zahl solcher Wörter → findClosestHighlight(targetPosition) landet auf dem falschen Wort, KWIC-'Beleg öffnen' und Nähe-/Verspositionssuche springen an die falsche Stelle. Aktuell 0 Fälle im Korpus (die date/year-Notizen in HZU/HZU2 sind leere `<note .../>`-Selfclosing-Elemente), daher heute nicht sichtbar – aber die drei laut CONTRACTS §B bit-genau gekoppelten Zähler laufen an dieser Stelle auseinander, und der aktive Ingest kann jederzeit eine gefüllte Datumsnotiz einbringen.

```
if ((noteType === 'date' || noteType === 'year') && noteN) {
                        return `<span class="note-badge note-${this.escapeHtml(noteType)}" title="${noteType === 'date' ? 'Datum' : 'Jahr'}">${this.escapeHtml(noteN)}</span>`;
                    }
                    return children();
```
**Vorschlag:** Auch im date/year-Zweig die Kinder verarbeiten, damit enthaltene `<w lemmaRef>` positionsgezählt werden – z.B. `return badge + children();` (Badge plus gerenderter Inhalt), oder die Position im `<w>`-Zweig unabhängig vom umschließenden Notiz-Rendering hochzählen. Idealerweise durch position-parity.spec.js mit einem Fixture abdecken, das ein `<w lemmaRef>` in einer date/year-Notiz enthält.


### 59. `lemma/lemma-page.js:146` — Bug
*clipboard.writeText ohne .catch führt zu unhandled rejection und stummem Fehlschlag*

Der Copy-ID-Button ruft navigator.clipboard.writeText(...).then(...) ohne Catch. Schlägt der Clipboard-Zugriff fehl (verweigerte Permission, nicht-fokussiertes Dokument, unsicherer Kontext), wird das Promise rejected, ohne dass der Nutzer Feedback bekommt; der Button-Text wechselt nie zu 'kopiert!', und es entsteht eine unhandled promise rejection in der Konsole.

**Fehlerszenario:** Nutzer klickt 'kopieren' in einem Kontext, in dem die Clipboard-Permission verweigert ist → writeText rejected → keine Rückmeldung, unhandled rejection; der Nutzer weiß nicht, ob die ID kopiert wurde.

```
navigator.clipboard.writeText(lemma.id).then(() => {
                this.elements.copyIdBtn.textContent = 'kopiert!';
                setTimeout(() => { this.elements.copyIdBtn.textContent = 'kopieren'; }, 1500);
            });
```
**Vorschlag:** Ein .catch() ergänzen, das dem Nutzer einen Fehlerhinweis am Button anzeigt (z. B. Text 'Kopieren fehlgeschlagen') oder einen Fallback bereitstellt.


### 60. `lemma/lemma-page.js:155` — Bug
*Authority-Daten (Etymologie, Begriffslabels, Varianten, Komposita, aehnliche Lemmata) unescaped in innerHTML*

**Fehlerszenario:** Die Render-Methoden schreiben mehrere aus Authority-Files stammende Felder ungefiltert in innerHTML: comp.text der Etymologie (Z. 158/160), Begriffslabels concept.termDE/termEN (Z. 174), Variantenformen (Z. 323), Kompositum-Lemmata c.lemma (Z. 343) und aehnliche Lemmata l.lemma (Z. 399). Enthaelt eines dieser fremdgepflegten Felder ein HTML-Metazeichen (etwa '<' oder '&' in einem lexicon.xml-Eintrag), wird es als Markup interpretiert statt als Text. Die Datei hat escapeHtml importiert, umgeht es hier aber durchgehend.

```
return `<a href="?id=${numId}" class="etymology-link">${comp.text}</a>`;
```
**Vorschlag:** Alle interpolierten Authority-Textwerte (comp.text, conceptLabels, Variantenformen, c.lemma, l.lemma) mit dem bereits importierten escapeHtml() umschliessen — konsistent zur escapeAttr-Nutzung in fetchWoerterbuchnetz und zu app.js.


### 61. `lemma/lemma-page.js:223` — Bug
*Korpus-Titel und Autor unescaped in Belegstellen-Liste der Lemma-Seite*

**Fehlerszenario:** Enthaelt ein TEI-Text im Korpus-Index einen Titel oder Autor mit HTML-Metazeichen (z. B. ein '<' oder ein Markup-Fragment aus fremdgepflegten TEI-Daten), so wird occ.title / occ.author ungefiltert in occurrencesContent.innerHTML gerendert. Ergebnis: zerstoertes Layout bzw. injizierbares Markup. Die Datei importiert escapeHtml (Z. 8), nutzt es aber nur fuer Woerterbuchnetz-Daten, nicht hier.

```
<a href="../korpus.html?textId=${encodeURIComponent(occ.textId)}&lemmaIds=${lemmaKey.replace('lemma_', '')}"
                       class="text-sm font-medium text-brand-600 hover:text-brand-800 transition">
                        ${occ.title}
                    </a>
                    ${occ.author ? `<span class="text-xs text-slate-400 ml-2">${occ.author}</span>` : ''}
```
**Vorschlag:** occ.title und occ.author mit escapeHtml() umschliessen, analog zu app.js (dort werden r.title/r.author konsequent escaped).


### 62. `lemma/lemma-page.js:229` — Bug
*Index-Datenfelder werden ungeschützt in innerHTML interpoliert, obwohl dieselbe Datei escapeHtml importiert*

Fast alle Render-Methoden bauen HTML per Template-String und innerHTML aus Roh-Feldern des Authority-/Korpus-Index, ohne zu escapen: occurrence.title/author (Z. 229-230), Etymologie-Text comp.text (Z. 158/160), Concept-Labels (Z. 174), Variantenformen v (Z. 325), Compound-Lemma c.lemma (Z. 343) und Similar-Lemma l.lemma (Z. 399). Auffällig ist die Inkonsistenz: exakt dieselbe Datei importiert escapeHtml und nutzt es diszipliniert für die externen Wörterbuchnetz-Daten (escapeAttr, Z. 285/288/303-305), vergisst es aber für die eigenen Index-Daten. Da das Projekt laut CLAUDE.md aktiven Ingest betreibt (WZB, ARITHMETIC, weitere), sind Titel-/Autor-/Lemma-Strings nicht eingefroren. Ein Titel oder Name mit &, <, > oder " (z. B. ein Werktitel 'A & B' oder ein Editor-Name mit Sonderzeichen) zerstört das Rendering oder injiziert Markup. Ich habe den aktuellen Index geprüft: derzeit enthält kein Titel/Autor/Concept/Etymology-Feld solche Zeichen, der Fehler ist also latent, aber über den nächsten Ingest erreichbar.

**Fehlerszenario:** Ingest fügt einen Text mit Titel 'Reinfried & Yrkane' oder ein Concept-Label mit '<' hinzu → renderOccurrences/renderLemma interpolieren den Rohstring in innerHTML → das '&' bzw. '<' wird als Markup interpretiert, der Titel wird abgeschnitten/verstümmelt oder ein injiziertes Tag verändert das DOM.

```
<a href="../korpus.html?textId=${encodeURIComponent(occ.textId)}&lemmaIds=${lemmaKey.replace('lemma_', '')}"
                       class="text-sm font-medium text-brand-600 hover:text-brand-800 transition">
                        ${occ.title}
                    </a>
                    ${occ.author ? `<span class="text-xs text-slate-400 ml-2">${occ.author}</span>` : ''}
```
**Vorschlag:** Die betroffenen Felder (occ.title, occ.author, comp.text, Concept-Labels, v, c.lemma, l.lemma) vor der Interpolation durch das bereits importierte escapeHtml() leiten – analog zur bestehenden escapeAttr-Nutzung für Wörterbuchnetz-Daten.


### 63. `playground/js/data/storage/tei-storage.js:20` — Bug
*TEIStorageManager.initialize() ignoriert das false-Ergebnis der IndexedDB-Initialisierung und meldet fälschlich Erfolg*

**Fehlerszenario:** `IndexedDBManager.initialize()` gibt ohne Exception `false` zurück, wenn `window.indexedDB` fehlt (indexed-db-manager.js:23-26) oder das Öffnen fehlschlägt (Zeile 32-35). Der Rückgabewert wird hier nicht geprüft: In einem Browser ohne/mit deaktiviertem IndexedDB setzt `initialize()` trotzdem `this.isInitialized = true`, loggt „Storage initialized: IndexedDB cache ready" und liefert `true`. Aufrufer (saveToCache/loadFromCache) glauben, der Cache sei verfügbar; erst der spätere `ensureInitialized()`-Throw im IndexedDBManager wird in den einzelnen Operationen abgefangen (Rückgabe false/null). Folge: irreführende Erfolgsmeldung und kein sauberer Fallback-Status.

```
await this.indexedDBManager.initialize();
            this.isInitialized = true;

            console.log('🔧 Storage initialized: IndexedDB cache ready');
            return true;
```
**Vorschlag:** Rückgabewert auswerten: `const ok = await this.indexedDBManager.initialize(); if (!ok) { this.isInitialized = false; return false; } this.isInitialized = true;`.


### 64. `playground/js/data/tei-manager.js:481` — Bug
*Dokument-Trefferprüfung in searchMultipleLemmas nutzt Substring-Selektor und verletzt CONTRACTS §B.1*

Die 'containsAllLemmas'-Prüfung selektiert per CSS-Substring `w[lemmaRef*="lexicon.xml#lemma_${lemmaId}"]`. `*=` matcht Teilstrings, sodass die Suche nach lemma_308 auch Wörter mit lemma_3089/lemma_3087/lemma_30800 findet. Damit gilt ein Text fälschlich als Treffer, obwohl er das gesuchte Lemma gar nicht enthält. CONTRACTS §B.1 fordert exakten, whitespace-separierten Token-Match (zentral in lemmaRefMatchesId), den die Proximity-/Enrich-Pfade auch nutzen — dieser Dokument-Suchpfad wurde bei der #130-Vereinheitlichung übersehen.

**Fehlerszenario:** Nutzer lädt eigene TEI-Dateien hoch (Upload-Workflow setzt window.playground.corpusData nicht) und startet Multi-Lemma-Dokumentsuche nach lemma_308. searchMultipleLemmasUsingIndex fällt auf searchMultipleLemmas zurück; ein Text, der nur lemma_3089 (jâmer) enthält, wird als Treffer für lemma_308 gemeldet → falsches Forschungsergebnis.

```
const elements = doc.querySelectorAll(`w[lemmaRef*="lexicon.xml#lemma_${lemmaId}"]`);
```
**Vorschlag:** Statt des `*=`-Selektors alle `w[lemmaRef]` iterieren und mit lemmaRefMatchesId(lemmaRef, `lemma_${lemmaId}`) exakt prüfen, wie in findCooccurringLemmas (Zeile 518) bereits geschehen.


### 65. `playground/js/data/tei-manager.js:586` — Bug
*extractMatchingWordsFromDocument sammelt über Substring-Selektor fremde Lemmata ein (§B.1-Verletzung)*

Die Wort-Extraktion vereinigt drei Selektoren in einem Set; der erste, `w[lemmaRef*="lexicon.xml#lemma_${lemmaId}"]`, ist ein Substring-Match und zieht dadurch auch Wörter mit längeren IDs (lemma_3089 bei Suche nach lemma_308) in die Trefferliste. Da die anderen beiden Selektoren nur eine Teilmenge liefern, bestimmt der `*=`-Selektor das Ergebnis und überzählt. Dieselbe Methode wird auch von searchDocumentUsingIndex (Zeile 951) genutzt.

**Fehlerszenario:** Dokumentsuche (XML-Fallback) nach lemma_308 in einem Text mit lemma_3089-Wörtern: matchingWords[308] enthält die jâmer-Belege, der angezeigte Beleg-Zähler ist zu hoch — exakt der Bug-Typ, den #126/§B.1 (Zeile 173: lemma_3089 vs lemma_308 = no) verbietet.

```
`w[lemmaRef*="lexicon.xml#lemma_${lemmaId}"]`,
```
**Vorschlag:** Selektor-Liste durch eine Iteration über `w[lemmaRef]` + lemmaRefMatchesId ersetzen; das Set-Dedup entfällt dann, weil pro Wort genau einmal geprüft wird.


### 66. `playground/js/ui/tei/multi-lemma-search.js:136` — Bug
*escapeHtml maskiert keine Anführungszeichen, wird aber im Attribut-Kontext (aria-label) und in querySelector verwendet*

escapeHtml (Zeile 248-252) nutzt div.textContent → div.innerHTML. Diese Technik maskiert < > & korrekt, lässt aber " und ' unangetastet (im Textknoten müssen sie nicht maskiert werden). Der Rückgabewert wird jedoch in Zeile 136 in einen Attributwert (aria-label="Remove ...") eingesetzt. Enthält ein Lemma ein ", bricht das Attribut auf und es entsteht fehlerhaftes/injizierbares Markup. Dieselbe rohe Lemma-Zeichenkette wird zudem in Zeile 154 unescaped in einen CSS-Attributselektor interpoliert (`[data-lemma="${lemma}"]`), was bei " eine SyntaxError-Ausnahme in querySelector wirft.

**Fehlerszenario:** Nutzer gibt (oder Link liefert per lemmata-Param) ein Lemma wie a"b ein. In addLemmaChip entsteht aria-label="Remove a"b" → aufgebrochenes Attribut/kaputtes Chip-Markup. Beim späteren Entfernen des Chips wirft removeLemma in Zeile 154 querySelector('[data-lemma="a"b"]') eine SyntaxError; da this.lemmas in Zeile 152 bereits gefiltert wurde, der Chip aber nicht aus dem DOM entfernt wird, laufen Array-Zustand und angezeigte Chips auseinander und updateExecuteButton wird nie erreicht.

```
<button type="button" aria-label="Remove ${this.escapeHtml(lemma)}">
```
**Vorschlag:** Eine echte, kontextbewusste Attribut-Maskierung verwenden (auch " und ' zu &quot;/&#39; kodieren, wie das escapeHtml in lemma-distribution.js) und in Zeile 154 den Attributwert per CSS.escape() bzw. über iteratives Prüfen von chip.dataset.lemma statt String-Interpolation selektieren.


### 67. `playground/js/ui/tei/text-statistics.js:245` — Bug
*Im Modus „Nur Auswahl anzeigen" bleibt eine gerade abgewählte Zeile sichtbar (kein Re-Render)*

Der Einzel-Checkbox-Handler aktualisiert bewusst nur das `selected`-Set und die Aktionsleiste (`updateBar()`), ohne `render()` — laut Kommentar zur Erhaltung der Scroll-Position. Ist jedoch `showSelectedOnly` aktiv, filtert `sortedStats()` (Zeile 197-199) auf die selektierten Texte; eine gerade abgewählte Zeile fällt damit logisch aus der Ansicht, wird aber erst beim nächsten `render()` entfernt. Bis dahin steht im Modus „Nur Auswahl anzeigen" ein Text ohne gesetztes Häkchen in der Tabelle, was den Modus-Invarianten widerspricht.

**Fehlerszenario:** Nutzer aktiviert „Nur Auswahl anzeigen" (zeigt z.B. 5 selektierte Texte), entfernt dann bei einem davon das Häkchen. Der Zähler springt auf 4, die Zeile bleibt aber sichtbar (unmarkiert) stehen, bis eine andere Aktion (Sortieren, Toggle) ein Re-Render auslöst — die Ansicht zeigt vorübergehend einen nicht ausgewählten Text im Auswahl-Only-Modus.

```
cb.addEventListener('change', () => {
        if (cb.checked) this.selected.add(cb.dataset.selectId);
        else this.selected.delete(cb.dataset.selectId);
        updateBar();
      });
```
**Vorschlag:** Wenn `this.showSelectedOnly` aktiv ist, im Einzel-Checkbox-Handler `this.render()` statt nur `updateBar()` aufrufen (im Normalmodus wie bisher ohne Re-Render, um Scroll zu erhalten).


### 68. `scripts/audit/check-authority-cross-refs.py:337` — Bug
*CI-Fehlermeldung zählt Refs auf fehlende Ziel-Dateien doppelt*

**Fehlerszenario:** Ein Korpus-File referenziert N-mal eine nicht vorhandene Datei 'foo.xml'. In der Scan-Schleife wird für jede dieser Refs sowohl by_target['foo.xml'] (Zeile 184, bei jedem unresolved) als auch missing_target_files['foo.xml'] (Zeile 178, bei not known_file) hochgezählt — beide erreichen N. Im --check-Gate wird offenders['foo.xml'] zunächst aus by_target mit N befüllt und dann nochmals um missing_target_files N erhöht → gemeldet werden 2N statt N. Das Gate schlägt zwar korrekt fehl (nonzero), aber die ausgegebene Trefferzahl ist doppelt so hoch wie real und führt bei der Fehlerdiagnose in die Irre.

```
offenders = {tf: c for tf, c in by_target.items() if tf != 'lexicon.xml'}
        for tf, c in missing_target_files.items():
            offenders[tf] = offenders.get(tf, 0) + c
```
**Vorschlag:** missing_target_files nicht erneut aufaddieren (die Refs stecken bereits in by_target), sondern nur zur Kategorisierung/Meldung nutzen — z.B. offenders direkt aus by_target[tf für tf != 'lexicon.xml'] bilden und missing_target_files separat ausweisen.


### 69. `scripts/ingest/wzb/wzb-pos-apply.py:113` — Bug
*Dry-Run-Coverage zählt überschriebene @pos-Werte doppelt*

**Fehlerszenario:** Im Dry-Run wird w.set() nie ausgeführt, has_pos (Z. 112) zählt also die bereits vorhandenen @pos-Werte. will_have = has_pos + stats['applied']. stats['applied'] (Z. 108) inkludiert aber auch die 'overwrite'-Fälle (Z. 104-105), bei denen das <w> bereits ein @pos hatte und somit schon in has_pos enthalten ist. Bei einem Pending-TSV, das N Zeilen auf bereits annotierte <w> anwendet, meldet der Dry-Run eine um N zu hohe projizierte Coverage (kann sogar >total ausweisen). Nur Reporting betroffen, keine Datenänderung.

```
will_have = has_pos + (stats["applied"] if dry_run else 0)
```
**Vorschlag:** Nur die netto neu hinzukommenden verwenden: will_have = has_pos + (stats['applied'] - stats['overwrite'] if dry_run else 0).


### 70. `scripts/ingest/wzb/wzb-sense-baseline.py:36` — Bug
*PROJECT_ROOT zeigt nach Reorg auf scripts/ingest statt Repo-Root — Default-Pfade existieren nicht*

Das Skript liegt unter scripts/ingest/wzb/, daher ist Path(__file__).parent.parent == scripts/ingest. Alle daraus abgeleiteten Defaults (DEFAULT_TEI_DIR, DEFAULT_PENDING, DEFAULT_OUT, Zeilen 37-39) zeigen ins nicht existierende scripts/ingest/tei bzw. scripts/ingest/Wenzelsbibel/. Korrekt wäre parent.parent.parent. Der Docstring dokumentiert den Aufruf ohne Pfad-Flags (`py scripts/wzb-sense-baseline.py [--dry-run]`), d.h. der dokumentierte Standardaufruf ist defekt.

**Fehlerszenario:** `python scripts/ingest/wzb/wzb-sense-baseline.py --dry-run` (dokumentierter Aufruf): scan_corpus glob't scripts/ingest/tei (0 Dateien, existiert nicht, verifiziert exists=False), danach öffnet load_pending_lemmata die nicht existierende DEFAULT_PENDING → FileNotFoundError. Baseline lässt sich nur noch mit explizit gesetztem --tei-dir/--pending/--output ausführen.

```
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_TEI_DIR = PROJECT_ROOT / "tei"
```
**Vorschlag:** PROJECT_ROOT = Path(__file__).parent.parent.parent setzen (analog müsste in allen mitverschobenen wzb-Skripten geprüft werden).


### 71. `scripts/ingest/wzb/wzb-sense-bulk-resolve.py:101` — Bug
*reviewer wird immer auf 'claude' gesetzt — widerspricht --decision-type bulk-human/instance-human*

REVIEWER ist hart auf 'claude' verdrahtet (Zeile 34) und wird in Zeile 101 unabhängig vom gewählten --decision-type in jede aufgelöste Zeile geschrieben. Für die als wissenschaftlichen Provenienz-Record gedachten Werte (decision_type kann bulk-human/instance-human sein) entsteht ein Widerspruch: decision_type dokumentiert eine menschliche Entscheidung, reviewer behauptet aber 'claude'.

**Fehlerszenario:** `--decision-type bulk-human` (menschliche Auflösung) → betroffene Zeilen erhalten decision_type=bulk-human, aber reviewer=claude. Die Provenienz-Spalte im Datensatz ist damit falsch und für spätere Auswertung irreführend.

```
REVIEWER = "claude"
...
                row["reviewer"]       = REVIEWER
```
**Vorschlag:** reviewer aus --decision-type ableiten (human → tatsächlicher Bearbeitername/CLI-Argument, llm → model_id/claude) oder als eigenes CLI-Argument führen statt fest 'claude'.


### 72. `scripts/insert-div-wrappers-138.py:191` — Bug
*Bei mehreren aufeinanderfolgenden <pb> vor einem lb-n=1-Reset wird deren Dokumentreihenfolge umgekehrt*

**Fehlerszenario:** Stehen im MBS-Container zwei (oder mehr) <pb>-Elemente unmittelbar vor einem <lb n='1'/> (Rezeptgrenze), etwa [.., pbA, pbB, lb-n=1], so werden sie per pop() in umgekehrter Reihenfolge in den neuen Chunk gezogen: erst pbB, dann pbA → Ergebnis [pbB, pbA, lb]. Die Seitenumbruch-Marker erscheinen danach in falscher (absteigender) Seitenreihenfolge. Die Token-Invariante schlägt NICHT an, weil <pb> keine <w>/<pc> enthält, sodass der Fehler ungeprüft in die Datei geschrieben wird. Der Einzel-pb-Fall (Regelfall, MBS5-Muster) funktioniert korrekt; nur der im Kommentar ausdrücklich erwähnte Mehrfachfall ('ggf. mehrere') ist betroffen.

```
while chunks[-2] and chunks[-2][-1].tag == PB_TAG:
                chunks[-1].append(chunks[-2].pop())
```
**Vorschlag:** Die vorangehenden <pb> als zusammenhängenden Block in Originalreihenfolge übernehmen, z.B. Indexgrenze im vorigen Chunk bestimmen und den Slice per chunks[-1].extend(chunks[-2][start:]) + del chunks[-2][start:] anhängen, statt einzeln zu poppen.


### 73. `testing/tests/concept-distribution.spec.js:91` — Bug
*Baseline-Performance-Test verspricht im Namen "<2s", erzwingt aber nur <5s*

Der Testname (Zeile 67) behauptet, der Baseline-Fall (Sterben) rendere in unter 2 Sekunden ('rendert <2s'). Die tatsaechliche Zeit-Assertion prueft jedoch nur `toBeLessThan(5000)`, also 5 Sekunden. Die Long-Task-Assertion (<200ms, Zeile 90) ist konsistent, aber die im Namen versprochene Render-Zeit-Schranke ist mehr als doppelt so locker wie behauptet. Dieser Test ist explizit als 'Performance Lock' konzipiert (describe-Block Zeile 27) — der Zweck ist, Regressionen einzufangen. Die Diskrepanz macht den Lock schwaecher als seine Selbstbeschreibung suggeriert.

**Fehlerszenario:** Eine Performance-Regression in concept-distribution.js laesst 'Sterben' statt in ~1s nun in 3,5s rendern (Long-Tasks weiterhin jeweils <200ms, weil das Chunking greift). Der Test heisst 'rendert <2s', bleibt aber gruen, weil 3500 < 5000. Ein Entwickler, der die Suite liest, glaubt faelschlich, die 2s-Grenze sei abgesichert; die reale Verlangsamung wird nicht gemeldet.

```
expect(elapsed, `Sterben total elapsed ${elapsed}ms`).toBeLessThan(5000);
```
**Vorschlag:** Entweder die Assertion auf `toBeLessThan(2000)` verschaerfen (passend zum Namen) oder den Testnamen auf die real erzwungene Schranke ('<5s') korrigieren, damit Name und Assertion uebereinstimmen.


### 74. `testing/tests/playground.spec.js:47` — Bug
*passRate-Schwelle von 45% lässt massive Regressionen der eingebetteten Test-Suite unbemerkt durch*

**Fehlerszenario:** Die gesamte eingebettete Test-Suite (window.getTestResults) wird nur gegen passRate >= 45 geprüft. Regressions-Szenario: Wenn eine Änderung die Hälfte der eingebetteten Tests (z.B. alle IndexedDB- oder TEIStorageManager-Tests) bricht und die passRate auf 50% fällt, bleibt dieser Playwright-Test trotzdem grün. Der Gate-Wert ist so niedrig, dass er reale Ausfälle nicht mehr fängt.

```
expect(passRate).toBeGreaterThanOrEqual(45); // 45% pass rate minimum (accounting for IndexedDB test environment flakiness)
```
**Vorschlag:** Umgebungsabhängig flakige Suites gezielt skippen/markieren und für die stabilen Suites eine strenge Schwelle (z.B. 100% bzw. namentliche Pflicht-Tests) assertieren, statt einen globalen 45%-Floor zu setzen.


### 75. `testing/tests/results-table.spec.js:32` — Bug
*Hartkodierte Trefferzahl (140 Zeilen für 'minne') bricht bei jedem Korpus-Ingest*

**Fehlerszenario:** `toHaveCount(140)` fixiert die exakte Zeilenzahl für die Suche nach 'minne'. Laut CLAUDE.md ist das Korpus NICHT eingefroren (laufender Ingest WZB/ARITHMETIC + händische Korrekturen). Sobald ein neuer Text mit 'minne'-Belegen hinzukommt oder wegfällt, schlägt der Test fehl, obwohl die Tabellen-Render-Logik korrekt ist. Der Kommentar 'passe an, falls Korpus wächst' bestätigt die Wartungsfalle. Gleiches Muster bei Zeile 58/59 (JT '612 Treffer' fest angenommen).

```
await expect(page.locator('#resultsList table tbody tr')).toHaveCount(140);
```
**Vorschlag:** Gegen die tatsächliche Ergebnismenge asserten statt gegen eine Magic-Number, z.B. Zeilenzahl == `window._mhdbdbApp.currentResults.length`, sodass der Test die Render-Parität prüft statt einen korpus-abhängigen Absolutwert.


### 76. `assets/js/app.js:901` — Klarheit
*Kommentar bezeichnet vollständig implementierte Tabellen-Methoden fälschlich als noch zu implementierende 'Stubs'*

**Fehlerszenario:** Die direkt folgenden Methoden (handleSortClick, handleTableRowClick, serializeResultsAsTSV, copyResultsToClipboard, downloadResultsAsCSV) sind vollständig implementiert und produktiv im Einsatz (Sortier-Header, Zeilen-Klick, CSV-Export der Tabellenansicht). Der Kommentar 'Stubs — werden in Tasks 6, 7, 8, 9 implementiert' stammt aus der Bauphase. Ein Entwickler liest 'Stubs', hält die Handler für unfertige Platzhalter und implementiert sie evtl. doppelt oder traut dem Export-/Sortier-Feature nicht.

```
// Stubs — werden in Tasks 6, 7, 8, 9 implementiert
    handleSortClick(column) {
```
**Vorschlag:** Den veralteten 'Stubs'-Kommentar entfernen oder durch eine kurze Beschreibung der fertigen Tabellen-Interaktionen ersetzen.


### 77. `assets/js/app.js:1059` — Klarheit
*Kommentar verweist auf nicht existierende Methode `performSearch` für das Zurücksetzen des Keyness-Flags*

**Fehlerszenario:** Eine Methode `performSearch` existiert in app.js nicht (Grep bestätigt: nur dieses Kommentar-Vorkommen). Das Flag `_keynessComputed` wird tatsächlich in `handleSearch()` (Zeile 491: `this._keynessComputed = false;`) zurückgesetzt. Ein Entwickler, der der Doc folgt und nach `performSearch` sucht, findet nichts, hält den Reset-Pfad für fehlend und riskiert bei einer Umstrukturierung, dass Keyness über mehrere Suchen hinweg stale bleibt.

```
* Issue #114 (Followup): Keyness einmalig pro Suche berechnen, erst wenn
     * die Tabellen-Ansicht sie braucht. Flag wird in performSearch zurückgesetzt.
```
**Vorschlag:** `performSearch` im Kommentar durch `handleSearch` ersetzen.


### 78. `assets/js/lib/corpus-loader.js:184` — Dead Code
*CorpusLoader.getCacheStats() und clearCache() sind ungenutzte Debug-Helfer*

Beide Methoden (clearCache() Z.172, getCacheStats() Z.184) sind laut ihren Doc-Kommentaren „useful for debugging", werden aber nirgends im ausgelieferten Code aufgerufen. Die einzige Erwähnung von clearCache ist ein auskommentierter Verweis in playground/js/data/authority-manager.js:226.

**Fehlerszenario:** Beweiskette: `grep -rn 'getCacheStats' .` liefert nur die Deklaration; `grep -rn 'clearCache' .` liefert die Deklaration plus eine reine Kommentarzeile (`//   - clearCache()`) in authority-manager.js. Kein ausführbarer Aufruf, kein window.*, kein Handler. Beide Codepfade sind unerreichbar. Folge: Wartungslast; suggeriert eine Cache-Verwaltungs-API, die faktisch nicht angebunden ist.

```
async getCacheStats() {
```
**Vorschlag:** Beide Methoden entfernen oder – falls als Konsolen-Debug-Werkzeug gewünscht – bewusst z.B. als `window.__mhdbdbCache` exponieren, damit die Absicht sichtbar ist.


### 79. `assets/js/lib/text-normalizer.js:96` — Dead Code
*TextNormalizer.getNormalizedPreview() wird nie aufgerufen*

Die statische Methode getNormalizedPreview() (laut Kommentar für Debugging/UI-Hinweise gedacht) wird nirgends verwendet.

**Fehlerszenario:** Beweiskette: `grep -rn 'getNormalizedPreview' .` (js/html/md, außer node_modules) liefert ausschließlich die Deklaration in text-normalizer.js:96. Kein Aufruf, kein Import-Konsument, kein Handler. Unerreichbarer Code in einem der harten Contract-Module (Normalisierung). Folge: geringe Wartungslast, aber unnötige Oberfläche an einem sicherheitskritischen Vertragsmodul.

```
static getNormalizedPreview(text) {
```
**Vorschlag:** getNormalizedPreview() entfernen, da kein UI-Konsument existiert.


### 80. `assets/js/rendering/tei-text-reader.js:1033` — Dead Code
*TEITextReader.closePanel() wird nie aufgerufen*

Die Methode closePanel() setzt den Reader-Zustand zurück und leert das Panel, wird aber nirgends aufgerufen. Das Gegenstück showPanel() wird verwendet (Z.744-Bereich), closePanel() nicht. Der Kommentar im Rumpf („We might not actually want to hide the panel in the new UX") deutet an, dass die Schließen-Funktion beim UX-Umbau verwaist ist.

**Fehlerszenario:** Beweiskette: `grep -rn 'closePanel' assets lemma playground index.html korpus.html woerterbuch.html` liefert ausschließlich die Deklaration in tei-text-reader.js:1033 – kein `this.closePanel()`, kein Button-Handler, kein onclick, kein window.*. Der Codepfad ist unerreichbar. Folge: Wartungsfalle – toter Zustands-Reset, der bei künftigen Reader-Änderungen fälschlich als aktive Aufräum-Logik gelesen werden kann.

```
closePanel() {
        // Note: We might not actually want to hide the panel in the new UX
```
**Vorschlag:** closePanel() entfernen, oder – falls ein Schließen-Button vorgesehen ist – tatsächlich verdrahten.


### 81. `docs/ARCHITECTURE.md:62` — Docs-Drift
*Quellenverweis `showEmptyState()`, app.js:947 zeigt auf falsche Codestelle*

**Fehlerszenario:** Ein Entwickler will die Empty-State-Logik prüfen, springt laut Doku zu assets/js/app.js:947 und findet dort nicht `showEmptyState`. Die Funktion ist tatsächlich bei assets/js/app.js:1382 definiert (`showEmptyState() {`) und wird bei assets/js/app.js:129 aufgerufen (`if (!hasURLParams) this.showEmptyState();`). Die Zeilenangabe 947 ist um ~435 Zeilen falsch und führt in unzusammenhängenden Code.

```
a placeholder prompting the user to enter a word/lemma or click a text (`showEmptyState()`, app.js:947)
```
**Vorschlag:** Zeilenangabe von app.js:947 auf app.js:1382 korrigieren (oder generisch nur `showEmptyState()` ohne Zeilennummer nennen, da absolute Zeilennummern schnell driften).


### 82. `docs/ARCHITECTURE.md:426` — Docs-Drift
*Wörterbuchnetz-Endpoint-Verweis auf `lemma-page.js:278` ist veraltet*

**Fehlerszenario:** Im Abschnitt External Services wird die Endpoint-Konstruktion `/dictionaries/{sigle}/lemmata/{form}` mit `lemma-page.js:278` belegt. Der Fetch/Endpoint wurde jedoch (#73/#114) in den geteilten Client `assets/js/lib/woerterbuchnetz.js` (`fetchWbnetzEntries`) ausgelagert und in lemma-page.js nur noch importiert (Zeile 9) bzw. aufgerufen (Zeile 275). Zeile 278 enthält `const container = document.getElementById('wbnetzLinks');` und hat mit dem Endpoint nichts zu tun. CONTRACTS.md §D.2 (Zeile 394) benennt korrekt woerterbuchnetz.js als einzige Implementierung; ARCHITECTURE.md widerspricht dem.

```
**Queried dictionaries**: MWB, Lexer (both via `/dictionaries/{sigle}/lemmata/{form}`; `lemma-page.js:278`)
```
**Vorschlag:** Verweis auf `assets/js/lib/woerterbuchnetz.js` (`fetchWbnetzEntries`) umstellen, analog zu CONTRACTS.md §D.2.


### 83. `docs/CONTRACTS.md:258` — Docs-Drift
*§C.2.1 Quellenangabe `app.js:451-469` deckt den Dedup-Code nicht ab*

**Fehlerszenario:** Die Doku verortet die textId-Deduplizierung in `assets/js/app.js:451-469`. Tatsächlich ist Zeile 451 nur ein `console.log(...)`; der Dedup-Code beginnt mit den Deklarationen bei app.js:460-461 (`const lemmaSet = new Set(); const textMap = new Map();`) und der aggregierenden `rawResults.forEach`-Schleife bei app.js:463-477. Die angegebene Range startet auf einer Logging-Zeile und endet (469) mitten in der Schleife, so dass ein Leser den falschen Ausschnitt liest.

```
Source: inline dedup in `handleSearch()`, `assets/js/app.js:451-469` (no standalone function)
```
**Vorschlag:** Range auf ca. app.js:459-477 aktualisieren (Deklarationen + `forEach`-Aggregation), oder Zeilennummern durch den Funktionsnamen `handleSearch()` ersetzen.


### 84. `docs/DATA-MODEL.md:238` — Docs-Drift
*Authority-Index-Schema: concepts.broader/narrower existieren nicht im Index*

Das Concept-Schema listet `broader: "concept_5678"` und `narrower: ["concept_9012"]`. `parse_concepts()` in scripts/build-authority-index.py:460-471 emittiert ausschließlich `id, termDE, termEN, normalized` (plus optional `altDE/altEN/altNormalized`). Weder `broader` noch `narrower` werden geschrieben; es gibt auch keine conceptHierarchy-Map (nur genreHierarchy existiert in `maps`).

**Fehlerszenario:** Code, der eine Konzept-Hierarchie aus `concept.broader`/`concept.narrower` gemäß Doku aufbaut, erhält durchgängig `undefined`, weil diese Felder nie erzeugt werden.

```
broader: "concept_5678",
    narrower: ["concept_9012"],
```
**Vorschlag:** Die beiden Zeilen aus dem Concept-Schema entfernen (Konzept-Hierarchie wird im Index nicht abgelegt).


### 85. `docs/DATA-MODEL.md:250` — Docs-Drift
*Authority-Index-Schema: genres.broader existiert nicht im Genre-Eintrag*

Das Genre-Schema zeigt `broader: ["Prosa", "Mystik"]` als Feld des Genre-Objekts. `parse_genres()` in scripts/build-authority-index.py:523-528 emittiert nur `id, termDE, termEN, normalized`. Die Eltern-Namen liegen stattdessen in `maps.genreHierarchy` (build_performance_maps, Zeile 754), nicht im Genre-Eintrag selbst — wie im selben Schema unter `maps.genreHierarchy` (Zeile 275-277) korrekt dargestellt.

**Fehlerszenario:** Ein Konsument, der `genre.broader` laut Doku liest, erhält `undefined`; die Hierarchie ist nur über `index.maps.genreHierarchy[genre_id]` erreichbar.

```
broader: ["Prosa", "Mystik"],
```
**Vorschlag:** `broader`-Zeile aus dem Genre-Eintrag entfernen und auf `maps.genreHierarchy` verweisen.


### 86. `playground/js/data/authority-manager.js:177` — Parität
*Autocomplete-Normalisierung weicht vom kanonischen MHG-Normalizer ab und findet Ligatur-/Makron-Eingaben nicht*

**Fehlerszenario:** Der Index-Feldwert `l.normalized` wird per `mhg_normalizer.py` erzeugt (build-authority-index.py:141), der u.a. `æ→ae`, `œ→oe`, `ǒ→o` sowie die Makron-Vokale `ā ē ī ō ū` expandiert. Die hier inline gebaute Suchnadel `needle` behandelt diese Zeichen NICHT (nur Zirkumflex/Akut/Gravis/Umlaute/ß). Gibt ein Nutzer in einem der vier Live-Autocomplete-Felder (verse-position-search.js:264, lemma-distribution.js:323, rhyme-dictionary.js:506, cooccurrence-ranking.js:477) ein echtes MHG-Wort mit Ligatur oder Makron ein, z.B. „mære" oder „brōt", bleibt needle = „mære" bzw. „brōt", während das gespeicherte Lemma als „maere" / „brot" normalisiert ist. Weder startsWith noch includes matcht → das Dropdown zeigt fälschlich keine Vorschläge für ein existierendes Lemma. Zusätzlich transformiert needle `áàéèóò…` und `ß`, die der kanonische Normalizer gar nicht anfasst (umgekehrte Divergenz).

```
const needle = trimmed.toLowerCase()
      .replace(/[âáà]/g, 'a').replace(/[êéè]/g, 'e').replace(/[îíì]/g, 'i')
      .replace(/[ôóò]/g, 'o').replace(/[ûúù]/g, 'u')
      .replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss');
```
**Vorschlag:** Statt der inline-Regex-Kette `TextNormalizer.normalizeMHG(partialInput)` verwenden (bereits importiert), damit die Nadel identisch zu dem beim Build erzeugten `l.normalized`-Feld normalisiert wird. Das entspricht auch dem Vertrag „Normalisierung zentral in text-normalizer.js".


### 87. `playground/js/ui/core/router.js:244` — Klarheit
*Kommentar behauptet fälschlich, hashchange feuere synchron – Wartungsfalle für den Doppel-Dispatch-Schutz*

**Fehlerszenario:** Der Kommentar ist die tragende Begründung für den setTimeout-basierten Reset des _suppressHashUpdate-Flags. Tatsächlich wird das hashchange-Event nie synchron ausgelöst, sondern immer als asynchrone Task in der Event-Loop eingereiht. Ein Entwickler, der dem Kommentar glaubt ("feuert synchron"), könnte den setTimeout entfernen und _suppressHashUpdate direkt nach dem Setzen von location.hash auf false zurücksetzen. Dann läuft das Flag ab, BEVOR die noch ausstehende hashchange-Task feuert -> der Guard greift nicht -> dispatchFromHash() dispatcht die Route ein zweites Mal (bei navigate('multi-lemma', {lemmata:...}) würde die Korpus-Suche doppelt laufen). Der Kommentar dokumentiert also das Gegenteil der Realität und lädt zu genau der Änderung ein, die den Bug einführt.

```
// Release on next tick — the hashchange event fires synchronously after
  // setting location.hash in most browsers, so one tick is enough
```
**Vorschlag:** Kommentar korrigieren: hashchange wird asynchron als Task eingereiht; der setTimeout(0)-Reset ist genau deshalb nötig, damit das Flag erst NACH der (ebenfalls asynchronen) hashchange-Task zurückgesetzt wird. Formulierung 'fires synchronously ... in most browsers' entfernen.


### 88. `playground/js/ui/core/ui-helpers.js:267` — Dead Code
*Exportierte Funktion getRawResults() wird nie importiert oder intern aufgerufen*

getRawResults() ist exportiert, hat aber keinen einzigen Aufrufer. Kein Import in irgendeiner Datei, kein interner Gebrauch.

**Fehlerszenario:** Beweiskette: grep -rn 'getRawResults' ueber das ganze Repo (ausser den ausgenommenen Verzeichnissen) liefert ausschliesslich die Definitionszeile 267. Kein import, keine onclick-Referenz in playground/index.html, keine Router-Route in router.js, kein Test in testing/. Innerhalb ui-helpers.js taucht der Name nur an Z.267 auf. Funktion ist unerreichbar.

```
export function getRawResults() {
```
**Vorschlag:** Funktion loeschen.


### 89. `playground/js/ui/core/ui-helpers.js:524` — Dead Code
*highlightMatchedWords ist toter Code mit latentem Wortgrenzen-Bug für mittelhochdeutsche Sonderzeichen*

Die Funktion highlightMatchedWords wird nirgends aufgerufen (Grep über das gesamte Repo liefert nur die Definition in ui-helpers.js:524). Der aktive Highlight-Pfad in enrichFileResults nutzt stattdessen lemmaRefMatchesId. Zusätzlich enthält die tote Funktion einen latenten Fehler: die Wortgrenze `\b` im RegExp ist ASCII-basiert und funktioniert für Formen mit MHG-Sonderzeichen (â, ê, î, ô, û, ä, ö, ü) an Wortanfang/-ende nicht korrekt; das ist aber wegen der Nicht-Referenzierung folgenlos.

**Fehlerszenario:** Beweiskette Nicht-Referenzierung: `grep -r highlightMatchedWords` findet ausschließlich die Definitionszeile; kein export, kein Aufruf. Der belassene console.log (Zeile 527) und die Funktion sind reiner Wartungsballast, der einen bereits gelösten Highlight-Bug (#126 CONTRACTS §B.1) scheinbar erneut einführt und Leser in die Irre führt.

```
const regex = new RegExp(`\\b${escapedWord}\\b`, 'gi');
```
**Vorschlag:** Funktion samt console.log entfernen; falls doch als Fallback gedacht, dokumentieren und die Wortgrenzen-Logik auf lemmaRef-Matching statt ASCII-`\b` umstellen.


### 90. `playground/js/ui/core/ui-helpers.js:559` — Dead Code
*Exportierte Funktion displayGroupedResults() wird nie importiert oder intern aufgerufen*

displayGroupedResults(title, groupedData) ist als Modul-Export definiert, aber weder innerhalb von ui-helpers.js (etwa von updateAllUI oder displayResults) noch von irgendeinem Konsumenten importiert.

**Fehlerszenario:** Beweiskette: grep -rn 'displayGroupedResults' ueber das gesamte Repo (ausser node_modules/data/tei/authority-files/api/scripts/_archived) liefert nur die Definitionszeile 559 in ui-helpers.js. Kein import { displayGroupedResults } in playground/js, assets/js, lemma/ oder testing/; keine interne Aufrufstelle in ui-helpers.js (grep im File zeigt nur Z.559). Die tatsaechlich importierten ui-helpers-Exporte sind ausschliesslich buildTextLabelDisambiguator, displayResults, displaySummaryResults, updateAllUI.

```
export function displayGroupedResults(title, groupedData) {
```
**Vorschlag:** Funktion loeschen.


### 91. `playground/js/ui/core/ui-helpers.js:622` — Dead Code
*Exportierte freie Funktion showError() in ui-helpers.js wird nie importiert oder intern aufgerufen*

showError(message) ist als freie Funktion exportiert, hat aber keinen Konsument. Die zahlreichen showError-Treffer im Repo sind ausnahmslos Methoden this.showError() eigener Klassen (app.js, tei-text-reader.js, lemma-page.js, woerterbuch.js) und stehen in keinem Bezug zu diesem Modul-Export.

**Fehlerszenario:** Beweiskette: grep -rn 'showError' ueber das Repo zeigt Treffer nur als Klassenmethoden this.showError()/showError(message){ in assets/js/app.js, assets/js/rendering/tei-text-reader.js, lemma/lemma-page.js, assets/js/woerterbuch.js — keine davon importiert die freie Funktion aus playground/js/ui/core/ui-helpers.js. Es existiert kein 'import { showError } from ...ui-helpers.js' und kein interner Aufruf in ui-helpers.js (nur Z.622). Der Export ist unerreichbar.

```
export function showError(message) {
```
**Vorschlag:** Freie Funktion showError() aus ui-helpers.js entfernen.


### 92. `playground/js/ui/core/ui-helpers.js:634` — Dead Code
*Exportierte Funktion renderToContainer() in ui-helpers.js ist tot — Konsumenten nutzen die gleichnamige Funktion aus SearchHelpers.js*

ui-helpers.js exportiert renderToContainer(containerId, html), doch alle sechs Authority-Explorer importieren renderToContainer aus '../search/SearchHelpers.js' (dort eigener Export, Z.191), nicht aus ui-helpers.js. Die ui-helpers-Variante hat damit keinen Konsumenten.

**Fehlerszenario:** Beweiskette: Von renderToContainer existieren zwei Definitionen — SearchHelpers.js:191 und ui-helpers.js:634. Die Import-Anweisungen fuer renderToContainer stehen ausschliesslich in den Authority-Explorern (z.B. genre-explorer.js:6-17) und zeigen auf '../search/SearchHelpers.js'. Kein 'import { renderToContainer } from ...ui-helpers.js' existiert irgendwo (grep der ui-helpers-Import-Bloecke zeigt nur buildTextLabelDisambiguator/displayResults/displaySummaryResults/updateAllUI). Intern in ui-helpers.js wird renderToContainer nur an Z.634 genannt. Die ui-helpers-Kopie ist unerreichbar.

```
export function renderToContainer(containerId, html) {
```
**Vorschlag:** Die renderToContainer-Definition in ui-helpers.js entfernen; die einzige lebende Implementierung liegt in SearchHelpers.js.


### 93. `playground/js/ui/core/ui-helpers.js:644` — Dead Code
*Exportierte Funktion appendToContainer() wird nie importiert oder intern aufgerufen*

appendToContainer(containerId, html) ist exportiert, aber ohne Konsument. Weder ein Import noch ein interner Aufruf existiert.

**Fehlerszenario:** Beweiskette: grep -rn 'appendToContainer' ueber das gesamte Repo (ausser ausgenommene Verzeichnisse) liefert nur die Definitionszeile 644 in ui-helpers.js. Kein import in playground/js/**, assets/js/**, lemma/**, testing/**; intern nur an Z.644. Unerreichbar.

```
export function appendToContainer(containerId, html) {
```
**Vorschlag:** Funktion loeschen.


### 94. `playground/js/ui/core/ui-helpers.js:724` — Dead Code
*Exportierte Funktion delegateClick() wird nie importiert oder intern aufgerufen*

delegateClick(containerId, selector, handler) ist exportiert, wird aber von keinem Modul importiert und intern nicht verwendet.

**Fehlerszenario:** Beweiskette: grep -rn 'delegateClick' ueber assets/, playground/, lemma/, testing/ (inkl. *.html) liefert nur die Definitionszeile 724 in ui-helpers.js. Kein Import, kein interner Aufruf (im File nur Z.724), keine dynamische Referenz. Unerreichbar.

```
export function delegateClick(containerId, selector, handler) {
```
**Vorschlag:** Funktion loeschen.


### 95. `scripts/audit/check-index-versions.py:78` — Docs-Drift
*Dokumentierter Exit-Code 2 für Parse-Fehler ist unerreichbar — sys.exit(<string>) liefert immer 1*

**Fehlerszenario:** Ein Wartungs-Skript oder Runner ruft check-index-versions.py auf und verzweigt anhand des Exit-Codes: 1 = Versions-Drift (Daten fixen), 2 = Parse-/Format-Fehler (Regex im Audit-Skript reparieren), so wie es der Docstring in Zeile 23-26 zusagt. Läuft dann tatsächlich der Parse-Fehler-Pfad (z.B. weil das version-Feld in build-corpus-index.py von einfachen auf doppelte Quotes umgestellt wurde und die Regex nicht mehr matcht), ruft extract() `sys.exit(f"::error ...")` mit einem String-Argument auf. CPython gibt den String auf stderr aus und beendet mit Exit-Code 1 — nicht 2. Der Aufrufer behandelt den Skript-Format-Fehler fälschlich als Daten-Drift und leitet die falsche Fehlerbehebung ein.

```
sys.exit(
            f"::error title=Index version audit::Pattern not found in {target['path'].relative_to(PROJECT_ROOT)}. "
            f"File format may have drifted from what this script expects. Update the regex in check-index-versions.py."
        )
```
**Vorschlag:** Für die dokumentierte Exit-2-Semantik explizit `print(..., file=sys.stderr); sys.exit(2)` statt `sys.exit(<string>)` verwenden (analog zu check-index-freshness.py, das `return 2` korrekt nutzt). Alternativ den Docstring auf 'Exit 1 bei Parse-Fehler' korrigieren, falls die Unterscheidung nicht gebraucht wird.


### 96. `scripts/audit/check-release-version.py:66` — Docs-Drift
*Dokumentierter Exit-Code 2 (Parse-Fehler / kein Tag) ist unerreichbar — alle sys.exit(<string>)-Pfade liefern 1*

**Fehlerszenario:** Der Docstring (Zeile 25-28) trennt explizit '1 = drift' von '2 = parse error / kein Tag ermittelbar'. Tatsächlich beenden alle vier Fehler-Pfade — kein Tag (Zeile 53), CITATION.cff nicht gefunden (Zeile 62), CFF-version-Regex matcht nicht (Zeile 66-69), .zenodo.json-JSON-Parse-Fehler (Zeile 84) — via `sys.exit(<string>)`, was in CPython immer mit Exit-Code 1 endet, nie 2. Konkret: Wird das version-Feld in CITATION.cff ohne Quotes geschrieben (`version: 1.1.0`, valides YAML), schlägt die Regex fehl, das Skript exit-t mit 1 statt des zugesagten 2 — ununterscheidbar von einem echten Versions-Drift zwischen Tag und CFF. Ein Release-Tooling, das Exit 2 als 'Skript reparieren, Release nicht blockieren' behandelt, würde stattdessen wie bei einem Daten-Drift reagieren.

```
if not m:
        sys.exit(
            "::error title=Release version audit::Kein version-Feld in CITATION.cff gefunden. "
            "File-Format-Drift? Regex in check-release-version.py anpassen."
        )
```
**Vorschlag:** Für die Parse-/Kein-Tag-Fälle explizit `print(..., file=sys.stderr); sys.exit(2)` verwenden, damit der im Docstring versprochene Exit-Code 2 tatsächlich zurückkommt; oder den Docstring an das Ist-Verhalten (alles Exit 1) angleichen.


### 97. `scripts/build-corpus-index.py:80` — Refactoring
*get_namespaces() dreifach kopiert statt in gemeinsamem Modul*

Die Hilfsfunktion get_namespaces(tree) (Default-NS auf 'tei'-Präfix umbiegen, TEI-NS sicherstellen) existiert byte-nahezu identisch in drei nicht-archivierten Skripten: scripts/build-corpus-index.py:80, scripts/build-authority-index.py:51 und scripts/ingest/wzb/wzb-auto-match.py:54. Die drei Kopien sind funktional identisch (build-corpus und build-authority wortgleich; wzb-auto-match nutzt lediglich TEI_NS['tei'] statt des Literals). Ein gemeinsames Modul existiert bereits als Muster (mhg_normalizer.py wird per sys.path-Insert importiert), get_namespaces gehört genau dorthin.

**Fehlerszenario:** Ein künftiges Ingest liefert TEI-Dateien mit einer zusätzlichen Namespace-Eigenheit (z.B. ein weiterer Default-NS-Sonderfall). Ein Entwickler korrigiert get_namespaces nur in build-authority-index.py (die er gerade bearbeitet); build-corpus-index.py und wzb-auto-match.py behalten die alte Fassung. Folge: Authority-Index baut korrekt, Corpus-Index bzw. WZB-lemmaRef-Zuordnung resolvt XPath-Abfragen still falsch, ohne Fehler.

```
def get_namespaces(tree):
    """
    Detect and return all namespaces in document (Critical Fix #2).
    """
    nsmap = tree.getroot().nsmap.copy()
```
**Vorschlag:** get_namespaces in ein gemeinsames Hilfsmodul (z.B. scripts/tei_utils.py) ziehen und in allen drei Skripten importieren — analog zum bestehenden mhg_normalizer-Import.


### 98. `scripts/convert-l-to-lb-143.py:1` — Dead Code
*Abgeschlossenes Einmal-Migrationsskript convert-l-to-lb-143.py ist Archiv-Kandidat*

> ⚠️ **HINFÄLLIG (Archiv-Teil):** #143 ist offen — Skript ist dormant tooling, kein Archiv. Der beschriebene `all()`/`--dry-run`-Bug ist jedoch real und in `381d977` behoben. Siehe Nachtrag oben.

**Fehlerszenario:** Beweiskette Nicht-Referenzierung: Das Skript wandelt fest verdrahtet SIGLES = ['APO', 'HMT', 'HH'] (Zeile 26) einmalig von <l> auf <lb/> um (KZW-Entscheid #143, 2026-06-12, abgeschlossene Migration). Grep ueber .github/workflows/, package.json, requirements.txt, docs/ und alle anderen scripts/ findet KEINE Referenz ausser docs/journal-archive.md (disposabler Log). Es fehlt in scripts/README.md. Kein CLI-Parameter zur Wiederverwendung auf andere Texte (Ziel-Sigel hartcodiert). Ergebnis: das Skript liegt im aktiven scripts/-Wurzelverzeichnis, obwohl seine Migration erledigt ist und es von keiner lebenden Pipeline aufgerufen wird.

```
SIGLES = ['APO', 'HMT', 'HH']
...
def main():
    ok = all(convert(s) for s in SIGLES)
```
**Vorschlag:** nach scripts/_archived/ verschieben


### 99. `scripts/convert-l-to-lb-143.py:64` — Klarheit
*Mutierendes Korpus-Skript ohne --dry-run schreibt nicht-atomar; Teilkonvertierung des Korpus möglich*

Das Skript überschreibt drei TEI-Korpusdateien (APO, HMT, HH) direkt in place (path.write_text, Zeile 58) und besitzt weder argparse noch einen --dry-run-Schalter. Der Docstring bezeichnet die Transformation als 'analog insert-lg-stanzas-138.py' (Zeile 11), doch genau dieses Schwester-Skript (wie auch insert-div-wrappers-138.py, insert-pb-from-linecode.py, insert-stanzas-from-linecode.py) bietet durchgängig --dry-run mit 'Mode: DRY-RUN/WRITE'. Zusätzlich wird die Konvertierung über all(convert(s) for s in SIGLES) getrieben (Zeile 64): all() wertet den Generator kurzschlüssig aus, bricht also beim ersten False ab. convert() prüft die Layout-Vorbedingung (Zeile 40) und gibt bei Verletzung False zurück, nachdem für vorherige Sigel bereits geschrieben wurde.

**Fehlerszenario:** Ein Nutzer ruft das Skript erneut auf, nachdem eine der drei Dateien (z.B. HMT) manuell so umformatiert wurde, dass die Layout-Annahme verletzt ist (opens != closes). Ablauf: convert('APO') schreibt APO.tei.xml bereits um und liefert True; convert('HMT') bricht mit der Vorbedingungsprüfung ab und liefert False; all() short-circuitet, convert('HH') wird nie ausgeführt. Ergebnis: APO ist konvertiert, HMT und HH sind unverändert — das Korpus liegt in einem inkonsistenten Teilzustand, ohne Rollback und ohne dass vorab eine Vorschau möglich gewesen wäre.

```
ok = all(convert(s) for s in SIGLES)
```
**Vorschlag:** Analog zu den insert-*-Schwesterskripten einen --dry-run-Schalter (argparse) ergänzen und im Nicht-Dry-Run erst alle Vorbedingungen für ALLE Sigel prüfen, bevor die erste Datei geschrieben wird (Vorbedingungs-Pass von Schreib-Pass trennen), damit keine Teilkonvertierung entstehen kann.


### 100. `scripts/ingest/wzb/wzb-apply-lemmarefs.py:70` — Klarheit
*Docstring von build_id_index behauptet einen Fallback, den der Code nicht enthaelt*

**Fehlerszenario:** Der Docstring verspricht einen Rueckgriff auf den rohen Attributstring, falls der Standard-Accessor nichts liefert. Der tatsaechliche Code (Zeile 73-77) macht ausschliesslich w.get(XML_ID_ATTR, '') und ueberspringt leere Ergebnisse - es gibt keinen Fallback. Ein Wartender vertraut darauf, dass ungueltige NCName-xml:ids behandelt werden; tatsaechlich landen betroffene <w> gar nicht im Index und ihre Phase-1b-Aufloesung wird still als 'not_found' gezaehlt.

```
lxml may drop invalid NCName xml:id values when recover=True is used,
    so we fall back to the raw attribute string if the standard accessor
    returns nothing.
```
**Vorschlag:** Entweder den beschriebenen Fallback implementieren oder den irrefuehrenden Docstring-Absatz entfernen.


### 101. `scripts/ingest/wzb/wzb-auto-match.py:45` — Dead Code
*Ungenutzte Konstante LEXICON_FILE mit selbst-eingestehendem Kommentar*

LEXICON_FILE wird auf Modulebene definiert, aber im gesamten Skript nie referenziert. Der Kommentar '# may not be used here' gesteht die Unsicherheit selbst ein. Die weiteren Vorkommen von 'lexicon' im Skript (Zeilen 73, 124) sind unabhängige String-Literale ('lexicon.xml#...') und nutzen die Konstante nicht.

**Fehlerszenario:** Ein Entwickler will das Skript so anpassen, dass es das Lexikon einliest, und verlässt sich auf LEXICON_FILE als etabliertem Pfad. Der Kommentar signalisiert jedoch, dass niemand weiß, ob die Konstante gebraucht wird — die Konstante ist toter Code und stiftet über den geplanten Datenfluss Verwirrung, statt ihn zu dokumentieren.

```
LEXICON_FILE = PROJECT_ROOT / 'authority-files' / 'lexicon.xml'  # may not be used here
```
**Vorschlag:** Die ungenutzte Konstante ersatzlos entfernen (oder, falls das Lexikon tatsächlich benötigt wird, tatsächlich verwenden und den 'may not be used'-Kommentar streichen).


### 102. `scripts/ingest/wzb/wzb-sense-apply.py:216` — Dead Code
*Immer-falscher decision_type-Zweig mit irreführendem Kommentar; report_decision_breakdown() wird nie aufgerufen*

**Fehlerszenario:** load_resolutions() liefert Werte-Dicts mit ausschließlich den Schlüsseln sense_id, lemma_id, form (Z. 137-141). Die Bedingung in Z. 216 prüft 'decision_type' in diesen keys — das ist strukturell immer False, der pass-Block läuft nie. Der Kommentar 'handled below via pending TSV re-read' behauptet eine Nachverarbeitung, die es nicht gibt: report_decision_breakdown() (Z. 234) ist definiert, wird aber nirgends aufgerufen (grep bestätigt: nur die Definitionszeile). Wartungsfalle — ein Entwickler erwartet ein Decision-Type-Reporting, das faktisch tot ist.

```
if "decision_type" in (list(resolutions.values())[0].keys() if resolutions else {}):
        pass  # handled below via pending TSV re-read
```
**Vorschlag:** Entweder den toten Block entfernen oder report_decision_breakdown(pending_path) tatsächlich aufrufen; Kommentar entsprechend korrigieren.


### 103. `scripts/ingest/wzb/wzb-sense-apply.py:234` — Dead Code
*Ungenutzte Debug-Funktion report_decision_breakdown in wzb-sense-apply.py*

**Fehlerszenario:** report_decision_breakdown(pending_path) ist definiert, wird aber nirgends aufgerufen: Grep ueber das gesamte Repo liefert nur die Definition in Zeile 234, keinen Call. Der __main__-Block (Zeilen ~296-273) ruft ausschliesslich apply_senses(...) auf und wertet keinen decision_type-Breakdown aus, obwohl die Funktion genau diese Diagnose ('=== Decision-type breakdown ===') drucken sollte. Ergebnis: der Nutzer, der wzb-sense-apply.py ausfuehrt, sieht diese Aufschluesselung nie; die Funktion ist toter Code in einem sonst aktiven WZB-Ingest-Skript.

```
def report_decision_breakdown(pending_path: Path):
    """Print @ana coverage broken down by decision_type."""
```
**Vorschlag:** Entweder im __main__-Block nach apply_senses aufrufen (z.B. hinter --dry-run), falls die Diagnose gewuenscht ist, oder die Funktion entfernen.


### 104. `scripts/ingest/wzb/wzb-structural-cleanup.py:191` — Klarheit
*Kommentar 'Preserve tail text (spacing)' luegt: das ausgelesene tail wird verworfen (Dead Code, Whitespace-Verlust)*

Beim Entfernen der Gruppen-Elemente (CAPITULUM + Ziffern) wird tail = el_to_remove.tail or '' berechnet, aber nirgends wieder verwendet. Der Kommentar direkt darueber behauptet, das tail werde erhalten. Tatsaechlich entfernt lxml mit parent.remove() auch den Tail-Text des Elements; die zwischen den entfernten Tokens und dem Folgetext stehende Trennwhitespace geht damit verloren. Das erzeugte <milestone> (spaeter in fix.py) erhaelt spaeter head.tail=None, sodass an der frueheren Position keine Trennung mehr existiert. Ein Wartender, der dem Kommentar vertraut, nimmt faelschlich an, Spacing sei behandelt.

**Fehlerszenario:** CAPITULUM-Gruppe steht in einem <l> mit Tail-Whitespace nach der letzten Ziffer (z.B. ' ' vor dem naechsten <w>). Nach process_capitulum ist dieser Whitespace geloescht; die Variable tail, die ihn haelt, wird nie an head_el oder das vorherige Geschwister zurueckgehaengt. Der Code tut nicht, was der Kommentar sagt.

```
tail = el_to_remove.tail or ""
            parent.remove(el_to_remove)
```
**Vorschlag:** Entweder das ausgelesene tail tatsaechlich an das eingefuegte head_el (bzw. das letzte verbleibende Geschwister) anhaengen, oder die tote Zuweisung samt irrefuehrendem Kommentar entfernen.


### 105. `scripts/insert-lg-stanzas-138.py:1` — Dead Code
*Abgeschlossenes Einmal-Migrationsskript insert-lg-stanzas-138.py ist Archiv-Kandidat*

> ⚠️ **HINFÄLLIG:** #138 ist offen — Skript wird für den editorischen Substream gebraucht, kein Archiv. Siehe Nachtrag oben.

**Fehlerszenario:** Beweiskette Nicht-Referenzierung: Das Skript wrappt einmalig 814 <lg type="stanza"> in die HUG-Lieder aus KZWs HUG.txt-Linecode-Export (Issue #138 Punkt 5, laut JOURNAL 2026-06-12 als 9c9b78e83 gepusht/deployt/CI gruen = abgeschlossen). Ziel (HUG) und Mechanik sind hartcodiert. Grep ueber .github/workflows/, package.json, requirements.txt, docs/ und alle anderen scripts/ findet KEINE lebende Referenz ausser docs/JOURNAL.md/journal-archive.md (disposabler Log) und einem Kommentar-Verweis in convert-l-to-lb-143.py (selbst Archiv-Kandidat); es fehlt in scripts/README.md. Ergebnis: erledigtes One-Shot-Skript verbleibt im aktiven scripts/-Wurzelverzeichnis.

```
"""Insert <lg type="stanza"> wrappers into HUG songs from the linecode export.

  Issue: #138 Punkt 5 (HUG-Strophen, @wachauer 2026-06-12: "Ja, mach das.")
```
**Vorschlag:** nach scripts/_archived/ verschieben


### 106. `scripts/mhg_normalizer.py:7` — Klarheit
*Modul-Docstring nennt als kritischen Parity-Partner eine nicht existierende Datei (playground/js/utils/text-normalizer.js)*

**Fehlerszenario:** Ein Maintainer aendert die MHG-Normalisierung und liest im Modul-Docstring 'This module MUST produce IDENTICAL normalization results as playground/js/utils/text-normalizer.js'. Er sucht/oeffnet playground/js/utils/text-normalizer.js, um die JS-Seite mitzupflegen — die Datei existiert nicht (find playground -iname '*normaliz*' liefert nichts). Der tatsaechliche, vom Parity-Test (testing/tests/normalization-parity.spec.js, Zeilen 57/95/119) geladene Parity-Partner ist /assets/js/lib/text-normalizer.js. Der Hinweis fuehrt aktiv zur falschen (leeren) Fundstelle; die eine Seite der harten Cross-Language-Parity kann dabei unbeabsichtigt undokumentiert/uneditiert bleiben.

```
as playground/js/utils/text-normalizer.js
```
**Vorschlag:** Pfad in Zeile 7 (und die generische Nennung in Zeile 27) auf assets/js/lib/text-normalizer.js korrigieren — identisch zu dem Pfad, den normalization-parity.spec.js importiert.


### 107. `scripts/mhg_normalizer.py:73` — Dead Code
*Drei ungenutzte Vergleichs-Helfer in der geteilten Lib mhg_normalizer.py*

**Fehlerszenario:** matches_normalized (Zeile 73), exact_match_normalized (Zeile 93) und starts_with_normalized (Zeile 110) werden nirgends aufgerufen: alle sieben Importstellen im Repo importieren ausschliesslich 'from mhg_normalizer import normalize_mhg' (build-corpus-index.py, build-authority-index.py, classify-lexicon-backfill.py, wzb-*.py), keine importiert oder verwendet die drei Helfer. Wartungsfalle in einer contract-kritischen Datei (CONTRACTS §C, JS/Python-Paritaet): Ein Entwickler, der die MHG-Normalisierung anpasst, muss diese toten Vergleichsfunktionen mitpflegen und mit der JS-Seite abgleichen, obwohl kein Codepfad sie erreicht — Aufwand ohne Nutzen, Risiko fuer stille Divergenz.

```
def matches_normalized(text, search_term):
...
def exact_match_normalized(text, search_term):
...
def starts_with_normalized(text, search_term):
```
**Vorschlag:** Die drei ungenutzten Funktionen (Zeilen 73, 93, 110) entfernen; die Lib exportiert dann nur noch das tatsaechlich importierte normalize_mhg.


### 108. `scripts/wzb-add-lemma.py:121` — Klarheit
*Docstring von find_insertion_point beschreibt 2-Tupel, Funktion gibt 3-Tupel zurück*

**Fehlerszenario:** Der Docstring sagt `Return (parent_element, index_after_which_to_insert)`, tatsächlich liefert die Funktion `return parent, idx, max_id` (3 Werte), und der Aufrufer in Zeile 180 entpackt konsequenterweise drei: `parent, idx, prev_max_id = find_insertion_point(doc)`. Wer sich beim Weiterentwickeln auf den Docstring verlässt, unterschätzt die Rückgabe und schreibt fehlerhaften Entpack-Code.

```
"""Return (parent_element, index_after_which_to_insert) for the max-id entry."""
...
    return parent, idx, max_id
```
**Vorschlag:** Docstring auf `(parent_element, index_after_which_to_insert, max_id)` korrigieren.


### 109. `testing/test-utils.js:474` — Dead Code
*loadTestModules importiert nicht existierende Module aus nicht existierendem Pfad*

loadTestModules() versucht `./js/storage-manager.js`, `./js/tei-files.js` und `./js/main.js` relativ zu testing/test-utils.js zu importieren, also aus testing/js/. Dieses Verzeichnis existiert nicht (verifiziert via `ls testing/js` -> No such file or directory), und die produktiven Module heissen anders und liegen woanders (playground/js/data/storage/tei-storage.js, playground/js/data/tei-manager.js, playground/js/playground-main.js). Die Methode hat zudem keinerlei Aufrufer (grep ueber testing/, playground/, assets/ findet nur die Definition selbst). Es ist toter Code mit falschen Pfaden und veralteten Modulnamen.

**Fehlerszenario:** Ein Entwickler ruft in einem neuen Test window.testUtils.loadTestModules() auf, um Module vorzuladen. Der erste import scheitert am nicht existierenden Pfad testing/js/storage-manager.js, und die Methode wirft 'Failed to load module storage-manager.js: ...' — unabhaengig vom eigentlichen Testziel. Der irrefuehrende Helper kostet Debugging-Zeit, weil er suggeriert, es gebe ladbare Module dieser Namen.

```
await import(`./js/${module}`);
```
**Vorschlag:** Entweder loadTestModules() (und das ebenfalls ungenutzte initializePlayground()) entfernen oder die Pfade/Modulnamen auf die real existierenden playground/js/-Module aktualisieren.


### 110. `testing/tests/reading-view.spec.js:122` — Klarheit
*Multi-Lemma-Farbtest kann faktisch nie fehlschlagen — Assertion (>=1) widerspricht dem eigenen Kommentar (>=2)*

**Fehlerszenario:** Der Test heißt 'should color-code multi-lemma highlights' und der Kommentar sagt 'we expect at least 2 different background colors'. Da processWord jedes Highlight mit inline background-color rendert und count>0 bereits (Zeile 107) gesichert ist, ist colors.length immer >=1. Regressions-Szenario: Wenn die Farbzuordnung (lemmaColorMap) bricht und ALLE Treffer dieselbe Farbe bekommen, bleibt der Test grün. Der Test prüft also nicht, was Name und Kommentar behaupten.

```
expect(colors.length).toBeGreaterThanOrEqual(1);
```
**Vorschlag:** Einen Text + zwei Lemmata wählen, die beide nachweislich in diesem Text vorkommen, und colors.length >= 2 assertieren; sonst den irreführenden Kommentar/Namen entfernen.


### 111. `testing/tests/search-engine.spec.js:37` — Klarheit
*Testname behauptet 'searchLemma()', der Body ruft weder searchLemma noch resolveLemmaIds auf*

**Fehlerszenario:** Der Test heißt 'searchLemma() returns no exact/variant match for gibberish', der Kommentar spricht von `resolveLemmaIds`, aber der Body ruft keine der beiden Methoden auf — er filtert direkt `se.authorityIndex.lemmata` und liest `se.authorityIndex.variants`. Ein Bug in `searchLemma()`/`resolveLemmaIds()` bei Gibberish-Eingabe (z.B. fälschliche Stage-3-Treffer) würde von diesem Test niemals erfasst, obwohl der Name das suggeriert. Wer den Test pflegt, sucht die Ursache am falschen Code.

```
const exact = se.authorityIndex.lemmata.filter(l => l.normalized === 'zzzzqxjk');
```
**Vorschlag:** Entweder tatsächlich `se.resolveLemmaIds('zzzzqxjk')` bzw. `se.searchLemma(...)` aufrufen und dessen Verhalten asserten, oder Namen/Kommentar an das ehrliche Ziel ('Index enthält keinen Exact-/Variant-Eintrag') anpassen.


### 112. `testing/tests/search-normalization.spec.js:283` — Klarheit
*Test 8 '3-Stage Resolution' prüft die aufgelöste Stufe nie — nur, dass irgendetwas gefunden wird*

**Fehlerszenario:** Die Testfälle deklarieren explizit `stage: 1/2/2/3` und `desc` pro Eingabe, aber die einzige Assertion ist `expect(tc.foundLemmas).toBeGreaterThan(0)`. `expectedStage` wird nirgends verglichen. Szenario: Wenn Stage-1-Exact-Match ('brôt') brechen würde, aber der Partial-Fallback (Stage 3) trotzdem irgendein Lemma zurückliefert, bliebe der Test grün — obwohl die im Namen behauptete 3-Stufen-Logik defekt ist. Der Test verifiziert nur Nicht-Leerheit, nicht die Auflösungsstufe.

```
expect(tc.foundLemmas).toBeGreaterThan(0);
```
**Vorschlag:** Die tatsächlich genutzte Stufe verifizieren (z.B. für Stage 1 den erwarteten konkreten lemmaId asserten, für Stage 2 die Auflösung über den Variants-Index nachweisen), oder den irreführenden Namen/`expectedStage`-Feldern entfernen.


### 113. `testing/tests/search-normalization.spec.js:469` — Dead Code
*Test 'Display comprehensive test report' enthält keine einzige Assertion*

**Fehlerszenario:** Der Test besteht ausschließlich aus `console.log`-Aufrufen und ruft nie `expect` auf. Er ist per Konstruktion immer grün und trägt nichts zur Verifikation bei; im Report erscheint er jedoch als bestandener Test und suggeriert Coverage, die nicht existiert. Die geloggten Behauptungen (z.B. '175,910 orthographic forms', Zeile 484) können zudem beliebig von der Realität abweichen, ohne dass etwas rot wird.

```
test('Display comprehensive test report', async () => {
```
**Vorschlag:** Reinen Log-'Test' entfernen; solche Zusammenfassungen gehören nicht als Playwright-Testfall in die Suite.


---

## Anhang B — Widerlegte Findings

Diese 7 Findings wurden von der Verifikation zurückgewiesen (z. B. bereits behoben, nicht erreichbar oder Fehlinterpretation):

- `playground/js/playground-main.js:94` [Bug] — Button-Event-Listener werden vor dem Laden der Authority-/Korpus-Daten verdrahtet – früher Klick rendert leere Ansicht ohne Auto-Refresh  
  ↳ ✗ Die zentrale Behauptung ('bleibt leer, bis der Nutzer erneut klickt') ist durch den echten Code widerlegt. init() (playground-main.js:93-108) ruft nach beiden await-Ladeschritten (loadAuthorityIndex Z.97, autoLoadCorpus Z.100) am Ende dispatchFromHash() auf (Z.107). Ein frueher Klick setzt via nav
- `scripts/validate-indices.py:146` [Docs-Drift] — Versions-Mismatch führt nur zu WARN, nicht zu Validierungsfehler — Docstring/README versprechen ein Gate, das nicht existiert  
  ↳ ✗ Interpretationsspielraum, kein eindeutiger Widerspruch. Der Code entspricht zwar dem Zitat (Zeile 146-147: Versions-Mismatch nur WARN, Funktion laeuft bis 'return True' Zeile 216 weiter). Aber die docs-drift-Praemisse — der Docstring verspreche einen harten Gate — traegt nicht: Im selben 'Checks:'
- `scripts/ingest/naming/01-fetch-and-build-index.py:113` [Bug] — serialize_verse gibt bei NaN-Versangabe den Literal-String "nan" in den Index  
  ↳ ✗ Die Fehlerlogik ist code-seitig korrekt beschrieben: repr(float('nan'))=='nan', float('nan').is_integer()==False, und build_record (Z.194) ruft serialize_verse(row.get('Vers')) ungeguardet auf, waehrend jedes andere Feld mit filled() gegen NaN geschuetzt wird. ABER die Bug-Regel verlangt reale Err
- `scripts/insert-div-wrappers-138.py:1` [Dead Code] — Abgeschlossenes Einmal-Migrationsskript insert-div-wrappers-138.py ist Archiv-Kandidat  
  ↳ ✗ Kein Defekt, subjektive Housekeeping-Meinung. Ein standalone CLI-Migrationsskript ist naturgemäß von keinem Code importiert/aufgerufen — das macht es nicht zu totem Code. Der Grep bestätigt eine echte Referenz in docs/journal-archive.md (Provenienz). Vor allem: das Skript liegt im scripts/-Root NE
- `testing/tests/search-with-corpus.spec.js:176` [Bug] — Test 'Search 7-9: Multi-Lemma searches' besteht still, wenn der Button fehlt  
  ↳ ✗ Widerlegt für den realen Betrieb. Im Gegensatz zu Finding [0] existiert `#findMultiLemmaBtn` tatsächlich: playground/index.html:243 rendert den Button, playground-main.js:479 verdrahtet ihn ({ id: 'findMultiLemmaBtn', handler: () => navigate('multi-lemma') }), und das erwartete `#multiLemmaModal` 
- `testing/tests/error-handling.spec.js:37` [Bug] — Fehler-Erkennung akzeptiert das Allerweltswort 'nicht' als Fehlerindikator (False-Pass möglich)  
  ↳ ✗ Der 'nicht'-Zweig (Zeile 37) ist zwar redundant, aber der behauptete False-Pass ist unter den Testbedingungen nicht erreichbar. Der Test bricht ALLE TEI-Requests ab (Zeile 18: route.abort() auf '**/tei/**'), sodass kein Korpustext (potentielle 'nicht'-Quelle) rendern kann. Der tatsaechliche Fehler
- `assets/js/storage/tei-cache-manager.js:284` [Dead Code] — TEICacheManager.getStats() wird nie aufgerufen  
  ↳ ✗ Widerlegt. Die Beweiskette grep-te nur 'assets lemma playground *.html' und liess das testing/-Verzeichnis aus. Mein repo-weiter grep findet drei echte Aufrufe in testing/tests/tei-caching.spec.js: Zeile 72 'return await cache.getStats();', Zeile 207 'const beforeStats = await cache.getStats();', 

## Anhang C — Methodische Grenzen

- Die Zeilennummern beziehen sich auf Commit `997be03`; nach dem zwischenzeitlichen Merge von PR #157 wurden die Verifizierer angewiesen, Fundstellen primär über das Evidence-Zitat zu lokalisieren.
- Der Audit prüfte `.js`/`.py`/Tests + die im Scope genannten Docs. Nicht auditiert: TEI-Korpus-Inhalte, Authority-XML-Daten, HTML/CSS, `scripts/_archived/`.
- Dead-Code-Findings wurden per wiederholtem Repo-Grep verifiziert, können aber theoretisch von nicht-durchsuchten dynamischen Aufrufen (z. B. String-basiertes Dispatch) erreicht werden — vor dem Löschen kurz gegenprüfen.