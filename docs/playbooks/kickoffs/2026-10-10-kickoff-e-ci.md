# Kickoff Spur `lauf-e-ci`: CI beschleunigen und Laufzeitgate (#564)

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden. Laufplan: `docs/playbooks/kickoffs/2026-10-10-lauf-564.md`.

**1. Autorisierung.** chsteiner hat #564 am 10.10.2026 entschieden (Kommentar „Entschieden von @chsteiner am 10.10.2026“) und den autonomen Start freigegeben. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deine eigenen `claude/*`-Zweige, je Paket ein PR, `workflow_dispatch` auf deinen eigenen Zweigen zum Messen (angemeldet), im Ticket höchstens ein Statuskommentar je Paket. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Branch-Protection oder Repo-Einstellungen ändern, Tickets schließen, Externe ansprechen. Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9).

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees (besonders Git Rules zum CI-Bot und „Self-Inflicted Overhead“: eine Aussage über ein Gate wird durch einen Lauf belegt, mit Mutationsprobe)
2. `docs/playbooks/BETRIEBSVERTRAG.md` (gelesen, nicht kopiert; nenne in deiner ersten Meldung den Commit)
3. Diese Datei und den Laufplan daneben; sag, ob die abgelegte Fassung mit der zugestellten übereinstimmt
4. **#564 mit allen Kommentaren** (`gh issue view 564 --json title,body,comments`): Ausgangsmessung je CI-Schritt, Entscheidung
5. Alle Dateien unter `.github/workflows/`, `docs/DEVELOPMENT.md` zu CI und Gates, `scripts/audit/check-index-budget.py` (#111) als Vorbild für Budgetdatei, Selbsttest und Meldungen

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei. Melde es.

---

## 4. Dein Worktree

Start mit `claude --bg --worktree lauf-e-ci --name lauf-e-ci --model sonnet --effort medium`. **Erste Handlung:** `pwd`, Zweig, HEAD messen und melden; dann `git fetch --quiet origin` und je Paket einen Arbeitszweig frisch von `origin/main` (`claude/564-checkout`, `claude/564-data-integrity`, `claude/564-laufzeitgate`); `git rev-list --count "origin/main...HEAD"` muss 0 sein.

## 5. Was dir gehört, und was nicht

Maßgeblich ist §2 des Laufplans. **Dir:** `.github/workflows/` außer dem Benchmark-Workflow von Spur D; neue Gate-Dateien unter `scripts/audit/` für das Laufzeitgate samt Budgetdatei; die Validierungs- und Freshness-Skripte nur im Umfang von E2; in `docs/DEVELOPMENT.md` die Absätze zu CI und Gates und deine Inventarzeilen.

**Nicht deins:** `playground/`, `assets/`, `scripts/run-tests.js`, `testing/` (Spur D); `tei/`, `authority-files/`, `data/`, `api/`. **Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend als letzter Commit; **deine Fehlerjournal-Nummern sind 155 bis 159**. Reviewer-Memory nur anhängend, eigener Commit, Hook-Grenze beachten.

**Maschinenweit exklusiv: volle Testläufe und Chrome**, die Koordination vergibt. Du testest mit `MHDBDB_TEST_PORT=8088` und `-- --workers=2`, nur wenn deine Änderung etwas berührt, das ein Playwright-Test fangen kann.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt.** `fable-reviewer` (mit `model: opus`, solange Fable am Limit ist; im PR vermerken) vor dem ersten Push ist Pflicht.

## 6. Was eingefroren ist

`CLAUDE.md`; `docs/playbooks/`. Die Regel „bei Rot erklären oder beheben“ gehört nach der Abnahme in `CLAUDE.md` (Git Rules); den Wortlaut schickst du als Änderungswunsch an die Koordination (Ankertext, wörtlicher Ersatztext, ein Satz warum).

---

## 7. Die Pakete, in dieser Reihenfolge, je ein PR

**Der ganze Auftragstext ist eine Behauptung.** Die Schrittzeiten in #564 stammen von einem Subagenten; die Koordination hat nur die Checkout-Einstellungen nachgesehen (K: alle Workflows nutzen `actions/checkout@v6` mit vollem Baum, `fetch-depth` 1 oder 2; nur `issue-matrix.yml` nutzt `sparse-checkout`).

- **E1, Checkout schlanker.** Je Workflow feststellen, welche Pfade seine Schritte wirklich lesen (Skripte lesen, nicht raten), und für die, die `tei/` und `data/` nicht brauchen, `sparse-checkout` oder `filter: blob:none` setzen. **Je Workflow ein Beleg**, dass jeder Schritt danach noch dieselben Dateien sieht: ein Lauf auf deinem Zweig mit demselben Ergebnis wie auf `main`, und eine Mutationsprobe für jedes Gate, das danach Dateien sehen muss, die es vorher sah. Vorher und nachher die Checkout-Dauer aus der API, gleiche Zahl von Läufen.
- **E2, Data Integrity.** Validate (in #564: Median 212 s) und die Freshness-Prüfungen (75 s und 43 s) auf Doppelarbeit prüfen: wird dasselbe zweimal geparst, laufen Schritte seriell, die parallel könnten, wird bei einem PR ohne `tei/`-Änderung das ganze Korpus validiert? **Kein Gate verliert eine Prüfung** (§3.1 des Laufplans): wer auf geänderte Dateien einschränkt, belegt mit einer Mutationsprobe an einer ungeänderten Datei, dass der Fehler weiter auffällt oder warum er dort nicht entstehen kann, und lässt die volle Prüfung auf `push` nach `main` und im Wochenlauf stehen.
- **E3, Laufzeitgate.** Nach der Entscheidung in #564: Budget je CI-Schritt in einer Datei im Repo (Wert, Datum, Grundmenge, Begründungszeile), rot ab Budget × 1,5; Schritte unter 10 s mit fester Grenze 10 s; Checkout eigenes Budget × 1,3; „Run Claude Code Review“ ausgenommen. Budgets nach der Regel in §1 des Laufplans (Läufe nach E2, sonst letzte 25 mit Vermerk). Bauart wählst du und begründest sie im PR; zu klären ist, wie das Ergebnis am PR als Check erscheint (ein `workflow_run`-Workflow läuft im Kontext von `main` und erscheint nicht von selbst am PR). Auf `main` und im Wochenlauf blockiert Rot nichts und schreibt einen Kommentar in ein Sammelticket. Selbsttest wie bei `check-index-budget.py`; Mutationsprobe: ein Budget absichtlich zu klein setzen, Gate rot, zurücksetzen. Dazu der Änderungswunsch für `CLAUDE.md` (siehe 6).

## 8. Vorab entschieden

Die Entscheidung in #564 und §3 des Laufplans. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig, HEAD, Commit des Betriebsvertrags, Übereinstimmung des Kickoffs; je Paket Messung vorher; jeder `workflow_dispatch` zum Messen vorher angemeldet; Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des Standes; „PR N bereit zum Merge“ mit HEAD, Reviewurteil, CI und gelesenem Bot-Kommentar.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; fehlender Agententyp; eine Beschleunigung, die nur mit weniger Prüfung geht.

**Externer Zustand** (CI): `Monitor` oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian (laden über `ToolSearch` mit `select:PushNotification`), dazu eine Meldung an die Koordination. Nie über eine andere Session umgehen.

## 10. Abschluss, je PR

1. Die Gates, die die Änderung berührt, und für jeden geänderten Workflow ein grüner Lauf auf dem Zweig.
2. `fable-reviewer` vor dem ersten Push mit Zweig, Basis, Ziel, Rundennummer, ab Runde 2 die Vorbefunde, und der Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte? (E1/E2: jedes Gate, das stillschweigend weniger Dateien sieht.)
3. Journaleintrag als letzter Commit nach `git fetch origin`.
4. PR mit „Bezug: #564“ ohne Closing-Keyword, Laufzeit vorher und nachher im Body, nicht mergen; „bereit zum Merge“ an die Koordination.
