# Betriebsvertrag der autonomen Sessions

Der Teil des Vertrags, der für **alle** autonomen Sessions gleich lautet. Die drei Playbooks (`MASTERPLAN-AUTONOME-ISSUE-SESSION.md`, `MASTERPLAN-AUTONOME-MERGE-SESSION.md`, `MASTERPLAN-AUTONOME-CAREARBEIT-SESSION.md`) verweisen hierher und führen nur noch ihre eigenen Abweichungen und Weichen auf.

**Warum diese Datei existiert:** bis zum 2026-08-05 stand jede dieser Regeln in zwei oder drei Playbooks gleichzeitig. Das Verbot von `git add -A` etwa an vier Stellen, und das Merge-Playbook schrieb den Vertrag ab, obwohl es im selben Satz sagte, er sei „unverändert aus dem Issue-Session-Vertrag". Kopien driften: derselbe Mechanismus hatte dazu geführt, dass ein Playbook zur Ergebnisquelle eines Testlaufs das Gegenteil dessen anwies, was ein anderes als gemessenen Fehlschlag dokumentierte.

**Dieser Vertrag autorisiert nichts.** Er beschreibt, was gilt, *nachdem* ein Kickoff-Prompt eine Session eröffnet hat. Ohne Kickoff läuft keine Session, und die Vorlage dafür steht in `KICKOFF-VORLAGE.md`. Weil der Kickoff die Regeln mitbringt, sind sie zur Laufzeit im Kontext, ohne dass jemand eine zweite Datei öffnen muss.

## 1. Was ohne ausdrückliche Freigabe tabu bleibt

1. **Kein Push nach `main`.** Die Ausnahme ist die Merge-Session, deren Kickoff die Merge-Autorisierung ausdrücklich enthält; auch sie merged nur, sie pusht nicht direkt. Alle anderen Ergebnisse sind PRs, die chsteiner reviewt.
2. **Kein Force-Push nach `main`,** in keiner Session, unter keinen Umständen. Auf `claude/*`-Branches ist `--force-with-lease` nach einem Rebase dagegen Standard.
3. **Issues werden nie von der Session geschlossen,** nur per `Closes #N` im PR-Body beim Merge. **#44 bekommt nie einen Close-Trailer**, es ist die permanente Triage-Matrix.
4. **Keine Kontaktaufnahme mit Externen** (Linda, Alan, Carina, Silvan, Burch, Brom). Entwürfe für sie landen als Text im Issue.

## 2. Wie committet und gestaged wird

5. **Nur benannte Dateien stagen, nie `git add -A` oder `git add .`.** Parallele Sessions teilen den Arbeitsbaum und damit den Index: ein pauschales Staging sammelt fremde Arbeit ein. Commit `8b5d0e6ac` hat auf diesem Weg Router-Dateien in einen unbeteiligten Commit gezogen.
6. **Jede Session in ihrem eigenen Worktree**, angelegt beim Start mit `claude --bg --name <name> --worktree <name>` und damit unter `.claude/worktrees/`. Der Hauptordner bleibt Referenz und wird nicht als Arbeitsplatz benutzt. Nicht von Hand daneben legen: ein Worktree außerhalb von `.claude/worktrees/` verlangt eine interaktive Freigabe, die keine `allow`-Regel abstellen kann, und hat am 2026-09-01 eine unbeaufsichtigte Session eine Stunde stillstehen lassen. Begründung und Messung in §2.1 Regel 29 des Issue-Playbooks. Abbau nach dem Merge, im selben Zug: §2.1 Regel 30, das ist kein Einzeiler, und der erste Schritt darin rettet das Agent-Memory.
7. **Die Branch-Basis wird gemessen, nicht am Namen abgelesen**, und zwar vor dem ersten eigenen Commit: `git rev-list --count "origin/main...HEAD"` und `git rev-list --count "origin/main..main"` müssen beide 0 sein. Details und die Fehlergeschichte dazu in §2.1 Regel 28.

## 3. Wie kommuniziert wird

8. **Höchstens ein sachlicher Statuskommentar pro Issue.** Etablierte Ausnahme: der KZW-UI-Ping nach dem Live-Gang, der zur Abnahme gehört.
9. **Nicht fragen, nicht warten.** Alles Nötige liegt im Repo und in den Issue-Threads (`gh issue view N --json comments`). Nur nachweislich Unbeschaffbares wird im Abschlussreport dokumentiert übersprungen.
    - **Zu jedem angefassten Issue werden die Kommentare gelesen, nicht nur der Body. Immer** (chsteiner, 06.09.2026). Der Body ist der älteste Text im Ticket, und in einem laufenden Projekt ist der älteste Text der unwahrscheinlichste. Die Entscheidungen, die Messungen und die Richtigstellungen stehen im Thread: #216 führt sein ganzes Arbeitspaket in zwölf Kommentaren und nennt im Body das Wort *vrouwe* kein einziges Mal, #392 bis #394 sagen im Body „zu entscheiden" und im Kommentar „umgesetzt und gemergt". Wer nur den Body liest, ist nicht uninformiert, sondern falsch informiert. Messung in `CLAUDE.md` → Issue Labels.
10. **Stil:** keine Emoji-Icons (Heroicons inline SVG ist der einzige Icon-Stil), keine Em-Dashes in Prosa, echte Umlaute statt ASCII-Ersatz. Die Sprachregel nach Zielgruppe steht in `CLAUDE.md`.

## 4. Was vor jedem Push passiert

11. **Fable-Review vor dem ersten Push jedes PRs**, mit dem `fable-reviewer` (nicht dem `fable-advisor`, der ist der Berater für offene Entwurfsfragen). Mitgeben: Branch, Basis, Ziel in einem Satz, Nummer der Review-Runde, ab Runde 2 die Vorrunden-Befunde. Bei einem Diff, der etwas repariert, zusätzlich die Frage: **was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?** Stellt ein Fix eine Invariante her, verliert jede Prüfung ihren Gegenstand, die auf deren Gegenteil beruhte (#397). Was der Reviewer lokal findet, kostet null CI-Runden.
12. **Jeder Befund wird nachgemessen, bevor er übernommen wird**, auch der eines Reviewers und auch der eines Bots. Er ist selbst eine Behauptung, und eine ungeprüfte Korrektur einer ungeprüften Zahl ist schlimmer als die ursprüngliche, weil sie glaubwürdiger aussieht.
13. **Ab Review-Runde 3 wird nur noch auf Verhaltensbefunde reagiert.** Formulierungsfragen werden durch Kürzen erledigt, nicht durch Diskussion.
14. **Verifikation:** `npm test` aus dem Repo-Root, nie `npx playwright test`. Die VERDICT-Zeile ist das Ergebnis und gehört unverändert in den PR (§2.1 Regel 6). Bei UI zusätzlich Chrome-Verifikation mit realen Belegen, bei HTML-Änderungen `python scripts/build-pages.py --check`, bei neuen Utility-Klassen `npm run build:css`.
15. **Daten vor Schema**, und bei jeder Änderung in `tei/` oder `authority-files/` der Data-Change-Lifecycle aus `docs/DATA-MODEL.md`.

## 5. Was in Tickets wandert und was nicht

16. **Fixes direkt umsetzen.** Ein Issue entsteht nur, wenn eine **Entscheidung** nötig ist, die die Session nicht treffen darf, wenn ein **Mensch** gebraucht wird, oder wenn es ein **eigenes Arbeitspaket** ist (Ingest, Korpusänderung, mehr als ein halber Tag). Alles andere wird sofort behoben oder verworfen.
17. **Geshippte, aber bewusst offene Issues nicht anfassen.** Sie warten auf eine Abnahme durch KZW oder Julia; ein `Closes #N` ist keine Abnahme.
