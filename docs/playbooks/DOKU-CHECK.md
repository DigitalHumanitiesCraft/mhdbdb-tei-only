# Doku-Check: wiederkehrende Prüfung der promptotyping-Dokumente

**Erstellt:** 2026-10-20, nach der Entscheidung von chsteiner, den Check nach Fälligkeit statt auf Zuruf laufen zu lassen (Sammelticket #641).
**Typ:** Playbook. Es autorisiert nichts für sich allein (README dieses Ordners). Ein Lauf beginnt mit einem Auftrag: dem Prompt der wöchentlichen Claude-Code-Routine oder einem Kickoff von chsteiner.

Diese Datei ist die **einzige** Prüfliste für den Doku-Check in diesem Repo. Sie muss ohne persönliche Skills und Regeln auskommen: eine Cloud-Routine klont nur das Repo und sieht weder `~/.claude/skills/promptotyping/` noch `~/.claude/rules/` (code.claude.com/docs/en/cloud-environments, "What carries over from your setup", gelesen am 2026-10-20). Was der Check aus beiden braucht, steht deshalb hier.

## 1. Fälligkeit

```
python scripts/audit/check-doc-staleness.py --faellig
```

Die Statuszeile sagt `FAELLIG: ja`, `nein` oder `pr-offen #N`.

- **Bezugspunkt** ist `scripts/audit/doc-health-state.json`: der Commit und das Datum des letzten abgeschlossenen Checks. Das JOURNAL wird dafür nicht gelesen, seine Formate und seine Reihenfolge wechseln.
- **Fällig** ab 40 Commits an den 14 stabilen Docs oder nach 60 Tagen. "Stabil" heißt hier: die 15 promptotyping-Dokumente aus `docs/INDEX.md` ohne `JOURNAL.md`, also die 13 Stable-Knowledge-Dokumente plus `ROADMAP.md`. Die Schwelle hat chsteiner am 2026-10-20 entschieden. Dass JOURNAL-, Archiv-, Playbook- und Feature-Doc-Commits nicht mitzählen, hat die Session festgelegt, die den Lauf gebaut hat: Fast jede Session schreibt ins JOURNAL, und das ist keine Drift der Doku. Nach dieser Zählung gab es 69 Commits in den 15 Tagen nach dem Check vom 05.10. (`git log --oneline 621bcf749..9a7346539 -- <14 Dateien>`). Gezählt wird mit `--first-parent`, also nur auf der Linie von `main`: Ein ohne Squash gemergter Zweig zählt als ein Commit, nicht mit jedem Einzelcommit. Ohne das machte ein Check-PR mit einem Commit je Befund den nächsten Check sofort fällig (nach PR #644, 2026-10-20).
- **Ist ein PR `claude/doku-check-*` offen**, ist nichts zu tun, bis er gemergt oder geschlossen ist.

Bei `nein` und `pr-offen` endet ein Routinenlauf sofort, ohne Branch, Kommentar oder Ausgabe.

**Außer der Reihe** lohnt ein Check, auch wenn er noch nicht fällig ist, nach neuen Build-Skripten oder geänderten Algorithmen und nach neuen Authority-Dateien oder TEI-Elementen. Bis zum 2026-10-20 waren das neben "nach PRs an `docs/`" und "quartalsweise" die Auslöser in `CLAUDE.md`. Ein solcher Check läuft auf Zuruf von chsteiner nach derselben Liste.

## 2. Vertrag

`docs/playbooks/BETRIEBSVERTRAG.md` gilt vollständig und bindend. Er wird ganz gelesen, nicht überflogen. Drei Abweichungen gelten nur für einen Lauf in der Cloud-Routine:

- **Regel 6 (eigener Worktree über `claude --bg`) entfällt.** Die Routine arbeitet in ihrem eigenen frischen Klon, der Zweck der Regel ist damit erfüllt.
- **Regel 9 und jeder andere GitHub-Zugriff laufen über `gh api` (REST).** Der Proxy der Cloud lehnt `gh pr` und `gh issue` ab, weil sie GraphQL benutzen. Issue-Threads liest man mit `gh api --paginate repos/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/N/comments`, den Body mit `gh api repos/.../issues/N`. `GITHUB_TOKEN` ist dort ein Platzhalter, und `gh api` braucht kein eigenes Token.
- **Der Vertrag wird nicht in den Routinen-Prompt kopiert**, wie es ein Kickoff sonst verlangt. Eine Kopie im Prompt würde gegen diese Datei veralten, ohne dass ein Review sie sieht. Der Prompt verweist deshalb auf beide Dateien.

## 3. Ablauf

### 3.1 Gates zuerst

```
python scripts/audit/doc-count-audit.py --check
python scripts/audit/check-doc-inventories.py
python scripts/audit/check-index-versions.py
python scripts/build-pages.py --check
python scripts/audit/check-no-em-dash.py
```

Ein rotes Gate ist der erste Befund. Ein grünes Gate sagt nur etwas über seine eigene Liste: `doc-count-audit` zählt Korpus- und Authority-Dateien und sonst nichts (#451).

### 3.2 Gegenstand bestimmen

```
git diff --stat <commit aus doc-health-state.json>..HEAD -- docs/*.md
```

Jedes stabile Doc, das sich seitdem geändert hat, wird **vollständig** gelesen, nicht nur der Diff. Eine Prüfung, die nur den Diff liest, findet nicht, was durch die Änderung neben der Änderung falsch wurde.

### 3.3 Prüfungen

Die MHDBDB-eigenen Prüfungen (bis 2026-10-20 in `CLAUDE.md` unter "Health check list"):

1. **Flow:** Liest sich jedes geänderte Doc von vorn bis hinten folgerichtig?
2. **Algorithmen:** Drei Algorithmen auswählen und den Pseudocode in CONTRACTS mit dem Code vergleichen, mit Funktionsnamen statt Zeilennummern als Anker.
3. **XPaths:** Drei XPaths aus der Doku gegen die Build-Skripte prüfen.
4. **Rebuild-Test:** Ließen sich alle `.js`/`.py` aus der Doku neu bauen? Für die kritischen Pfade (Suche, Build-Pipeline, Leseansicht) sollte die Antwort ja sein, dann liegt man bei mindestens 85 %.
5. **Meta-Fragen:** Sind die Dateinamen selbsterklärend? Gibt es zu viele oder zu wenige promptotyping-Dokumente, also Überschneidung oder vermischte Zuständigkeit? Jede strukturelle Änderung an der Doku wird mit Grund aufgeführt.

Dazu, was frühere Checks tatsächlich gefunden haben:

6. **Zahlen und Zustandssätze, die kein Gate sieht.** Am 05.10. waren 11 der 14 Sachfehler von dieser Art. Jede undatierte Zahl in einem geänderten Doc wird gemessen. Braucht der Satz die Zahl nicht, wird sie gestrichen statt nachgezogen. Bleibt sie, bekommt sie Datum und Messweg.
7. **Als offen beschrieben, längst erledigt.** Das fand der Check vom 01.09. dreimal. Jede Aussage "offen", "geplant" oder "noch nicht" mit Issue-Nummer wird gegen den Thread geprüft (Body und Kommentare).
8. **Doku-Schuld nach Build-Erweiterungen.** Neue Skripte, Partials und geteilte Module gehören in DEVELOPMENT und ARCHITECTURE, auch ohne Schemaänderung (Lehre vom 02.06.). Prüfweg: `git log --name-status <commit>..HEAD -- scripts assets/js includes` gegen beide Docs halten.
9. **Lebenszyklus.**
   - Feature-Docs zu geschlossenen Issues und die JOURNAL-Länge meldet `check-doc-staleness.py` ohne Modus.
   - Eine Feature-Doc zu einem geschlossenen Issue wird ausgewertet (Kernwissen in die stabilen Docs) und gelöscht.
   - Das JOURNAL verdichtet der Lauf nicht, das entscheidet chsteiner.
   - ROADMAP darf kein geschlossenes Issue als anstehend führen.

Aus der allgemeinen promptotyping-Prüfung, soweit die Liste oben sie nicht abdeckt:

10. **Innere Widersprüche:** Sagen zwei Docs über dieselbe Sache Verschiedenes?
11. **Ungeprüfte Annahmen:** Was steht da, das nie gegen Daten oder Code gemessen wurde?
12. **Blinde Flecken:** Welche Frage hat niemand gestellt? Was würde eine kritische Kollegin einwenden? Diese Frage bekommt auch dann eine Antwort, wenn sonst alles stimmt.

### 3.4 Befundregeln

- **Jeder Befund wird gemessen, bevor er übernommen wird**, auch der eines Subagenten. Ein Agentenbericht sagt, wo zu messen ist, er ist nicht die Messung.
- **Fehlbefunde sehen richtig aus.** Am 05.10. stimmten drei Zahlen, die falsch wirkten: "263 of 567 concepts" (zählt je Sprache), "Eight of the eleven" und "666 headers / 664 texts". Bevor eine Zahl geändert wird, steht fest, welche Menge sie zählt. Zwei Zahlen sind zwei Mengen, bis dieselbe Grundmenge gemessen ist.
- **Datierte Chronik wird nie "korrigiert"**: JOURNAL, journal-archive, datierte Korrekturnotizen in DECISIONS. Nur Ist-Aussagen werden korrigiert.
- **Je Befund ein Commit.** Wer eine Stelle ändert, liest ihre Nachbarschaft mit: den Satz darüber, jede Aufzählung mit derselben Menge, jede Zahl, die mitwächst.
- **Ein Issue nur über der Schwelle aus Regel 16 des Betriebsvertrags.** Alles andere wird im PR behoben oder verworfen.

## 4. Ergebnis

1. **Branch** `claude/doku-check-JJJJ-MM-TT` von `origin/main`, die Basis gemessen nach Regel 7 des Betriebsvertrags.
2. **Ein Commit je Befund.**
3. **Markerdatei fortschreiben:** In `scripts/audit/doc-health-state.json` kommen `commit` (der geprüfte Stand, also `origin/main` beim Start), `date` (heute) und `scorecard` (`docs/JOURNAL.md, **Scorecard Doku-Check JJJJ-MM-TT**`, passend zu Punkt 5), als eigener Commit.
4. **`reviewer` vor dem Push**, wie es seine Definition in `.claude/agents/reviewer.md` vorgibt. Schreibt er in sein Memory, gehen diese Dateien als eigener Commit in denselben PR.
5. **JOURNAL-Scorecard als letzter Commit:** ein neuer Abschnitt `## JJJJ-MM-TT – Doku-Check (Scorecard)` am Ende von `docs/JOURNAL.md`, der Absatz beginnt mit `**Scorecard Doku-Check JJJJ-MM-TT**`, drei bis sechs Sätze. Bis zum 2026-10-20 waren es drei bis vier Zeilen. Der Abschnitt nennt auch die Lehren, die über den Einzelfall hinausgehen. Steht er als letzter Commit, trifft ein Konflikt mit parallelen Sessions nur ihn. **Kein Report als `.md` in `docs/`:** der Bericht ist mit der Scorecard und dem PR erledigt.
6. **PR über REST:** `gh api repos/DigitalHumanitiesCraft/mhdbdb-tei-only/pulls -f head=<branch> -f base=main -f title=... -F body=@<datei>`. Der Body enthält:
   - die Scorecard;
   - je Befund eine Zeile;
   - eine **Belegtabelle** mit einer Zeile je geänderter Zahl oder Zustandsaussage: die Aussage, der Befehl, der sie heute ausgibt, und seine Ausgabe;
   - die Liste **"sah falsch aus, stimmt"** mit Grund;
   - die Ausgabe der Gates aus 3.1.

   Kein Closing-Keyword vor einer Issue-Nummer. Gemergt wird von Hand.
7. **Kein Kommentar in #641.** Den schreibt der Wochenlauf `doc-health.yml`.
