# Masterplan: Carearbeit-Session (Repo-Pflege)

**Erstellt:** 2026-07-13 (destilliert aus der ersten Carearbeit-Session, Fable 5, PR #220).
**Status:** Session 2026-07-13 GELAUFEN (PR #220, Squash `6a9849314`: +86/−1.982 Zeilen über 26 Dateien; Scorecard im JOURNAL-Eintrag 17:45). Der Anhang (§6) beschreibt jeweils die NÄCHSTE Session.
**Typ:** Playbook (wiederverwendbares Session-Verfahren, dauerhaft, KEIN Temporal Artifact). §2 ist der stabile Kern, §4/§5 wachsen fortlaufend, §6 wird pro Session neu befüllt.

---

## 1. Zweck und Abgrenzung

Wiederkehrende Repo-Pflege statt Feature-Arbeit: toten Code entfernen, verwaiste Scripts und Leftover-Dateien aufräumen, Zähler-/Versions-Drift in Doku und Hilfeseiten beheben, formaler Doku-Health-Check nach der CLAUDE.md-Checkliste. Sinnvoller Rhythmus: quartalsweise oder nach größeren Feature-Wellen (der Haupt-Drift entsteht, wenn Features schneller shippen als Zählwörter nachgezogen werden).

NICHT Teil dieses Playbooks: Feature-Arbeit, Ingest (eigene Verfahren in DATA-MODEL.md), Issue-Abarbeitung (`MASTERPLAN-AUTONOME-ISSUE-SESSION.md`), PR-Merges (`MASTERPLAN-AUTONOME-MERGE-SESSION.md`).

## 2. Betriebsvertrag (gilt nur nach explizitem User-Kickoff)

Dieser Plan autorisiert NICHTS. Eine Carearbeit-Session startet erst mit einem Kickoff-Prompt. Der Kickoff regelt vier Weichen (Defaults = Session 1):

- **Branch-/PR-Modus:** ein Branch `chore/carearbeit-YYYY-MM`, thematische Commits (ein Commit pro Arbeitspaket), ein PR; Squash-Merge nach User-Prüfung.
- **Lösch-Policy:** klar Totes löschen (Git-History = Archiv), nur erledigte Einmal-Migrationen mit Doku-Wert nach `scripts/_archived/`.
- **npm test:** einmalige Freigabe für die volle Suite (Konvention: Tests nie ungefragt).
- **Health-Check:** als eigenes Arbeitspaket integriert ja/nein.

Harte Regeln (unabhängig vom Kickoff):

1. **Fixes direkt umsetzen.** Ein GitHub-Issue entsteht nur, wenn eine menschliche Entscheidung oder externe Abhängigkeit nötig ist oder der Umfang die Session sprengt.
2. **Geshippte, aber bewusst offene Issues nicht anfassen** (warten auf Test-OK von KZW/Linda). Vorab per `gh issue list` identifizieren.
3. **Dormante Einmal-Migrations-Scripts nicht löschen** (`insert-*`, `convert-l-to-lb-*`, `fix-*`): werden seit #171 bewusst lauffähig gehalten.
4. **Historische, datierte Chronik-Einträge nie „fixen"** (JOURNAL, DECISIONS-Korrekturnotizen, INDEX-Milestones): nur Ist-Aussagen korrigieren. Eine Zahl in einem datierten Log-Eintrag war zum damaligen Zeitpunkt korrekt.
5. Nur benannte Dateien stagen (nie `git add -A`), kein Push ohne Freigabe, kein `Closes #44`, Doku-Fixes referenzieren #140 (`refs`, nie `Closes`).

## 3. Verfahren

**Phase 0, Kartierung (parallel):** Drei Explore-Agents plus Issue-Bestand:

| Agent | Auftrag |
|---|---|
| JS/CSS | Lade-Mechanismus + Import-Graph aller Entry-Points, Orphan-Kandidaten mit Git-Historie, Dead Code in lebenden Dateien, CSS-Kandidaten mit False-Positive-Risiken |
| Scripts/Repo | Scripts-Topologie + Referenz-Analyse (npm, CI, docs, Playbooks), Verwaiste mit Urteil, Leftovers in Root/testing/includes, CI-Workflow-Zustand |
| Doku/Hilfe | Hilfeseiten vollständig gegen Feature-Stand lesen, Zähler-Drift-Tabelle, Versions-Konsistenz (TEI-MODEL §11 vs. Loader vs. Build-Skripte), docs/features-Bestand vs. Issue-Status |

Parallel: `gh issue list` für den Regel-2-Bestand (geshippt-aber-offen).

**Phase 1, mechanische Gates zuerst:** `python scripts/build-pages.py --check`, `python scripts/audit/doc-count-audit.py`, `python scripts/audit/check-index-versions.py`. Rote Gates sind die ersten Fixes (Session 1: Footer-Drift auf einer Hilfeseite, variants-Zahl). Diese drei fanden 2 von 3 Befund-Klassen mechanisch.

**Phase 2, Arbeitspakete in dieser Reihenfolge, je ein Commit:**

- **WP A Doku-/Hilfe-Staleness** (geringstes Risiko zuerst): Zähler, Versionen, Stand-Zeilen.
- **WP B Dead Code** (chirurgisch): je Kandidat Gegenprüfung nach §4; `npm test` direkt nach den Code-Edits im Hintergrund starten und parallel weiterarbeiten, aber ohne Branchwechsel (Issue-Playbook §2.1 Regel 6). Die frühere Angabe „~15 min" stammte aus der Ein-Worker-Zeit vor #323 und stand hier nur, um das Nebenherlaufen zu begründen; die Dauer misst der Lauf jetzt selbst und druckt sie.
- **WP C Scripts-/Repo-Hygiene**: Löschungen, Verschiebungen (Pfad-Logik anpassen + Dry-Run), READMEs, .gitignore.
- **WP D Health-Check**: `/promptotyping check` als Rahmen; 3 Algorithmen-Spot-Checks (CONTRACTS-Pseudocode vs. Code) und 3 XPath-Spot-Checks (Docs vs. Build-Skripte) als zwei parallele Explore-Agents; Scorecard (3-4 Zeilen, datiert) + Session-Eintrag mit Lehren ins JOURNAL. Kein Report als .md in `docs/`.
- **WP E Issues** für Nicht-Fixbares (Regel 1).

**Verifikation:** Gates aus Phase 1 erneut, `npm test` mit grüner VERDICT-Zeile (Issue-Playbook §2.1 Regel 6; sie nennt Testzahl, Dateizahl und geprüften Pfad und gehört so in den PR), `git diff --stat` pro Commit, PR mit Verifikations-Block. Bei neuen Utility-Klassen `npm run build:css` (in reinen Text-/Zahlen-Fixes nicht nötig).

## 4. Dead-Code-Fallen (Gegenprüfung vor jeder Löschung)

1. **Dynamische Imports mit String-Literalen** (`import('…corpus-loader.js')` in `playground-main.js`, `tei-manager.js`): auch `import(` greppen, nicht nur `import … from`.
2. **Berechnete Methodennamen im Playground-Router** (`show*` / `show*WithSearch`, `router.js`): Callgraph-Suche nach Literalen übersieht sie.
3. **JS-generierte CSS-Klassen** (`multi-lemma-${id}` im Playground, `highlight-${n}` im Reader): CSS nie rein statisch scannen. Derselbe Block kann in einer Datei tot und in der anderen lebendig sein (Session 1: `korpus.css` tot, `playground/css/style.css` lebendig).
4. **CI/Python liest JS-Konstanten per Regex:** `INDEX_VERSION`/`AUTHORITY_INDEX_VERSION` in `corpus-loader.js` nie entfernen (`validate-indices.py`, `check-index-versions.py`).
5. **Test-only-Reachability:** `testing/tests/*.spec.js` importiert Produktionsmodule direkt; `window.SearchPatterns`/`window._mhdbdbApp` sind Test-Expositionen.
6. **onclick-String-Handler** in Template-Literalen (Authority-Explorer): Funktionen, die nur dort referenziert werden, findet kein JS-Callgraph.
7. **Cross-Language-Parität** `text-normalizer.js` ↔ `mhg_normalizer.py` (CONTRACTS §A): Änderungen immer spiegeln.

## 5. Lehren-Log

**Session 1 (2026-07-13, PR #220):**

1. Drift-Klasse Nr. 1 sind **code-abgeleitete Counts** (Werkzeug-/Entry-Point-Zahlen in Hilfe, README, Docs), genau die prüft `doc-count-audit.py` nicht. Erweiterungskandidat: Playground-Sidebar-Buttons zählen.
2. Mechanische Gates zuerst laufen lassen: billig, objektiv, fanden den Footer-Drift und die variants-Zahl sofort.
3. Audit-Reports altern: zwei geplante Löschungen waren bereits erledigt. Ist-Stand vor jeder Löschung neu verifizieren, nie dem Report vertrauen.
4. Der Code selbst war nach #171-Audit + Dead-Code-Sweep schon sauber (keine einzige verwaiste JS-Datei); der Ertrag lag überwiegend in Doku/Hilfe. Erwartung für Folge-Sessions entsprechend setzen.
5. `variants.xml`-Formen-Zahl ändert sich bei jeder Nachannotation mit. Ist-Stellen der konkreten Zahl minimieren statt überall nachpflegen.
6. Kein Issue für Niedrig-Ertrags-Sweeps (Beispiel: voller Selektor-Sweep über `playground/css/style.css` nach leerer Stichprobe): JOURNAL-Notiz reicht, Issue wäre Tracker-Rauschen.

## 6. Anhang: Nächste Session

Vor der nächsten Session hier befüllen: Scope-Besonderheiten, seit der letzten Session bekannte Kandidaten, offene §5-Punkte.

**Stand nach Session 1 (2026-07-13):**
- ~~#219 Wenzelsbibel-Entscheidung~~: entschieden und umgesetzt 2026-07-14 (Ausdünnen + Umzug nach `ingest/wzb/`, siehe dortiges README).
- ~~`doc-count-audit.py` um code-abgeleitete Counts erweitern (Lehre 1)~~: umgesetzt 2026-07-14 (Zahlwort-Scan für Werkzeug-/Explorer-/Entry-Point-Claims, Chronik-Zeilen ausgenommen).
- `playground/css/style.css`-Voll-Sweep nur bei konkretem Anlass (Lehre 6).
