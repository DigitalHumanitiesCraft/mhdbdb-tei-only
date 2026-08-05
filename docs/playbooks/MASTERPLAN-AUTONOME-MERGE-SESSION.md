# Masterplan: Autonome Merge-Session

Gegenstück zum `MASTERPLAN-AUTONOME-ISSUE-SESSION.md`: Während die Issue-Session PRs **erzeugt**, arbeitet die Merge-Session den offenen PR-Bestand **nach main ab**. Playbook (wiederverwendbares Verfahren, KEIN Temporal Artifact — siehe CLAUDE.md → Temporal Artifacts): nach jeder Session Kernwissen ins JOURNAL und Datei aktualisieren, nicht löschen; der konkrete PR-Bestand steht jeweils im Anhang.

> **Status:** Erste Merge-Session am 08.07.2026 vollständig durchgeführt (13 PRs #174–#186, Lehren siehe JOURNAL-Eintrag „Autonome Merge-Session"). Die G1-/Phase-1-Regeln unten sind auf den dort verifizierten Stand korrigiert (Retarget-/Rerun-Mechanik). Datei bleibt als wiederverwendbares Verfahren; der Anhang beschreibt jeweils die NÄCHSTE Session und ist derzeit leer.

## Betriebsvertrag (gilt nur nach explizitem User-Kickoff)

Dieser Plan autorisiert NICHTS. Eine Merge-Session startet erst, wenn der User sie mit einem Kickoff-Prompt eröffnet, der ausdrücklich enthält:

1. **Merge-Autorisierung nach main** für die benannten PRs (übersteuert CLAUDE.md „NEVER commit or push without user testing and approval" — der Kickoff IST die Approval; ohne ihn bleibt main tabu).
2. Umfang: alle offenen claude/*-PRs oder eine explizite Teilmenge.
3. Ob Live-Smoke-Checks nach Deploy Teil der Session sind (empfohlen: ja).

Unverändert aus dem Issue-Session-Vertrag: Issues nie manuell schließen (nur via Closes-Trailer beim Merge; **#44 NIE**), nie `git add -A`, kein Force-Push auf main, max. 1 neuer Statuskommentar pro Issue (KZW-UI-Ping nach Live-Gang ist die etablierte Ausnahme laut Projektkonvention), keine Kontaktaufnahme mit Externen. Nicht fragen, nicht warten — bei Blockern dokumentiert überspringen.

## Merge-Gates (jeder PR, keine Ausnahme)

Ein PR wird nur gemerged, wenn ALLE Gates grün sind:

- **G1 CI grün** auf dem aktuellen Head. Achtung: Ein reines Base-Retarget (nach Merge + Branch-Löschung der Basis) triggert KEINE neuen Workflow-Läufe (`on: pull_request` hört default nur auf opened/synchronize/reopened, nicht auf den Base-Wechsel): die angezeigten grünen Checks liefen dann noch gegen die alte Base. Bei Daten-PRs (Index-/api/-Änderungen) deshalb nach dem Retarget einen frischen Lauf anstoßen, **per Close/Reopen des PRs, NICHT per `gh run rerun`**: Der Rerun recycelt das alte Event-Payload. Bis zum 02.08. schlug der Diff-Base-Step dabei mit „couldn't find remote ref" fehl, weil er `GITHUB_BASE_REF` fetchte und der Branch gelöscht war (Session 08.07., 2× reproduziert). Seit #292 liest er stattdessen den ersten Elternteil des ausgecheckten Merge-Refs, fetcht also gar nichts mehr, und diese Fehlermeldung kann nicht mehr kommen. Der Umweg bleibt trotzdem richtig, nur aus einem anderen Grund: `actions/checkout` holt den Merge-Ref über die SHA aus dem Payload (im Lauf 30745276846 sichtbar als `+503cb614…:refs/remotes/pull/337/merge`), ein Rerun prüft also weiter den alten Merge-Commit gegen die alte Base, jetzt aber ohne Fehlermeldung. Bei reinen Code-/Doku-PRs genügt der letzte grüne Lauf, das main-CI nach dem Merge ist das Netz. Nach einem Rebase (neuer Head) laufen Checks regulär neu an: abwarten.
- **G2 Review-Triage abgeschlossen:** Bot-Review(s) vorhanden und im PR-Body triagiert (umgesetzt oder begründet abgelehnt). Trifft NACH dem letzten Push ein neues Bot-Review ein, wird es erst triagiert (receiving-code-review: echter Bug / Stilfrage / False Positive), dann gemerged. **Jeder Befund wird vor der Übernahme nachgemessen**, auch der eines Reviewers: er ist selbst eine Behauptung, und eine ungeprüfte Korrektur einer ungeprüften Zahl ist schlimmer als die ursprüngliche, weil sie glaubwürdiger aussieht (Issue-Playbook Regel 22, CLAUDE.md → Selbst erzeugter Overhead).
- **G3 Kein menschliches Veto offen:** Reviews von KZW/chsteiner mit Änderungswunsch blockieren. Abgrenzung beachten: menschliche Freigaben, die das ISSUE betreffen (z. B. Alans Text-Freigabe für #86, KZWs Freigabe des Rektoratsberichts VOR VERSAND), blockieren den Repo-Merge NICHT — der PR merged Entwürfe/Teilarbeit ins Repo, das Issue bleibt offen.
- **G4 Mergeability:** GitHub meldet keinen Konflikt. Bei Konflikt: Branch auf main rebasen, Konflikt lösen, npm test (bei Code), `push --force-with-lease` (nach Rebase nötig; das Force-Verbot gilt nur für main, auf claude/*-PR-Branches ist es Standard), CI abwarten.
- **G5 Stack-Reihenfolge:** Ein gestackter PR wird nie vor seiner Basis gemerged.

## Verfahren

### Phase 0: Vorflug
1. `gh pr list` + pro PR: Checks, neue Kommentare seit letzter Triage, Mergeability, Base.
2. Merge-Reihenfolge festlegen: erst Stack-Ketten (Basis zuerst), dann Unabhängige, **Doku-/Meta-PRs zuletzt** (deren Inhalt — ROADMAP „Now", Matrix-Verweise — veraltet durch die Merges selbst; vor dem Merge per Folge-Commit auf den Endzustand bringen).
3. Bekannte Datei-Überschneidungen zwischen Ketten notieren (Konflikt-Erwartung, siehe Anhang).

### Phase 1: Merge-Schleife (pro PR)
1. Gates G1–G5 prüfen.
2. `gh pr merge <nr> --merge` — **ohne `--delete-branch`** (Repo-Konvention: Merge-Commit, kein Squash — erhält die Folge-Commit-Historie der Review-Triage). **GitHub retargetet abhängige Stack-PRs beim Branch-Löschen NICHT zuverlässig, sondern schließt sie** (Session 08.07.: #177 wurde beim #174-Merge mit `--delete-branch` CLOSED; Recovery: alten Head-SHA als Branch re-pushen → reopen → `gh pr edit --base main` → Temp-Branch löschen). Sichere Sequenz: mergen, dann SOFORT abhängige PRs per `gh pr edit <dep> --base main` retargeten — das Repo-Auto-Delete räumt den Head-Branch anschließend selbst.
3. CI auf main abwarten (v. a. `data-integrity.yml` bei Daten-PRs). Rot → STOPP der Merge-Schleife: diagnostizieren; der Fix läuft als neuer claude/*-Hotfix-Branch + PR (der gemergte PR-Branch ist gelöscht, und die Kickoff-Autorisierung deckt Merges, KEINE direkten main-Pushes). Erst nach grünem main weitermergen; NIE „einfach weitermergen".
4. Beim nächsten PR der Kette: Retarget-Verhalten aus G1 beachten (Checks laufen bei reinem Retarget NICHT automatisch neu).

### Phase 2: Nach jeder Kette und nach dem Block der unabhängigen PRs (Live-Verifikation, gebündelt zulässig)
1. GitHub-Pages-Deploy abwarten (Actions).
2. Chrome-Smoke auf der Live-URL — **Hard-Reload** (http-Cache!) und bei Index-Bumps den IndexedDB-Cache-Bust verifizieren (Konsole: neue Version geladen).
3. Kern-Flows je nach Kette (siehe Anhang).

### Phase 3: Abschluss
1. Verifizieren, dass alle Closes-Issues wirklich zu sind; Part-of-Issues offen geblieben.
2. **KZW-UI-Pings** für live gegangene UI-Features (Projektkonvention: @wachauer mit Live-URL + Test-Hinweisen; Issues offen lassen bis ihr OK — nur wo das Kommentar-Budget des Issues es erlaubt).
3. #44-Matrix aktualisieren: Bucket „PR offen" auflösen → Recently Completed; Quick Stats neu.
4. ROADMAP „Now" nachziehen; JOURNAL-Eintrag (Merges, CI-/Deploy-Vorkommnisse, Lehren).
5. Abschlussreport als Nachtrag im bestehenden #44-Session-Kommentar (Edit, kein neuer Kommentar).
6. Lokale Branches aufräumen (`git fetch --prune`; gemergte claude/*-Branches lokal löschen).

## Fehlerbilder und Reaktionen

| Situation | Reaktion |
|---|---|
| CI rot IM PR (nach Re-Run oder Rebase) | Ursache prüfen; Freshness-Gate rot = wahrscheinlich Rebuild-Drift → Indexe auf dem PR-Branch neu bauen, committen, pushen |
| CI rot AUF MAIN (nach Merge) | STOPP der Merge-Schleife; Fix als neuer claude/*-Hotfix-Branch + PR (PR-Branch ist gelöscht, direkter main-Push nicht autorisiert); erst nach grünem main weiter |
| Merge-Konflikt Kette B nach Kette-A-Merge | Erwartbar nur in geteilten Doku-Dateien (CONTRACTS/INDEX/TEI-MODEL, disjunkte Hunks) — rebase, lösen, npm test, `push --force-with-lease` |
| Neues Bot-Review mit echtem Bug kurz vor Merge | Fix als Folge-Commit + npm test + Triage-Nachtrag; erst dann mergen |
| Playwright-Report-Server hält npm test offen | `PW_TEST_HTML_REPORT_OPEN=never` setzen, Prozess auf Port 9323 killen; das Ergebnis steht in `testing/test-results/report.json`, nie in der Task-Ausgabe (Issue-Playbook §2.1 Regeln 26 und 27) |
| GitHub-API 5xx | Retry; bei anhaltend: dokumentieren, nächster PR |
| Stack-PR nach Base-Merge plötzlich CLOSED | Base-Branch wurde gelöscht, bevor der PR retargetet war → alten Head-SHA re-pushen, reopen, `--base main`, Temp-Branch löschen (siehe Phase 1 Schritt 2) |
| Rerun nach Retarget prüft gegen die alte Base | Stale Event-Payload: Close/Reopen statt `gh run rerun` (siehe G1). Seit #292 ist das stumm, vorher war der Diff-Base-Step dabei rot |

## Anhang: PR-Bestand der nächsten Merge-Session

*(derzeit leer — die erste Session vom 08.07.2026 hat den Bestand #174–#186 vollständig abgearbeitet: 13 PRs gemerged, 13 Issues geschlossen, Smoke-Checks grün. Ergebnis + Lehren: JOURNAL-Eintrag „2026-07-08 – handoff (Autonome Merge-Session)" und Abschlussreport in #44. Vor der nächsten Session hier eintragen: Reihenfolge/Stack-Ketten, Kommentar-Budgets, bekannte Datei-Überschneidungen, Smoke-Checks, erwartete Issue-Schließungen.)*
