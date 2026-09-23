# Kickoff Spur C `mhdbdb-testport`: #465, der Testport als Parameter

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 23.09.2026.

**1. Autorisierung.** chsteiner hat diesen Lauf am 23.09.2026 freigegeben. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deinen eigenen Zweig, einen PR öffnen, ein Statuskommentar und ein Relabel an #465. **Nicht**: mergen (das tut Christian), auf `main` pushen, Tickets schließen. Der Text erteilt keine technische Berechtigung, siehe 9.

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: ein Sessionname kann beim Antworten längst einer anderen Session gehören.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees, **besonders den Satz zu Gates unter „Self-Inflicted Overhead"** (seit `ae2e7a5fa`)
2. `docs/playbooks/BETRIEBSVERTRAG.md`
3. `docs/playbooks/kickoffs/2026-09-23-issue-abbau.md`, der Laufplan, **besonders §2 Spur C, §5 Betriebsmittel**
4. **#465 mit allen Kommentaren** (`gh issue view 465 --json title,body,comments`)
5. `scripts/run-tests.js` ganz, `testing/playwright.config.js` ganz, `package.json`
6. `docs/playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md` §2.1 Regel 6 (was `run-tests.js` verspricht: VERDICT, Exit 0/1/2, Fremdserver-Erkennung, Spec-Abgleich)

**Besonders tragen für dich:** `run-tests.js` ist die Instanz, die ein Testergebnis überhaupt bildet. Jede seiner Zusicherungen (Fremdserver erkennen, Spec-Dateien gegen den Report abgleichen, Exit-Code aus `report.json`) muss nach deiner Änderung **nachweislich** noch greifen, durch Ausführen und Mutation, nicht durch Lesen. **Und die Regel, die dein Ergebnis bindet:** Vorgabe bleibt 8080; wer nichts setzt, merkt keinen Unterschied.

**Abbruchklausel:** weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit hat ihn mit `claude --bg --worktree mhdbdb-testport` angelegt: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\mhdbdb-testport`, Zweig `worktree-mhdbdb-testport`, aus `main` bei `ae2e7a5fa` oder später; die Begleitnachricht nennt den HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen die Angaben halten, melden, zusammen mit dem Commit des gelesenen Laufplans. Bei Abweichung nichts ändern, melden, auf Neustart warten. Dann `git fetch --quiet origin`, `git rev-list --count "origin/main...HEAD"` muss 0 sein. Ein Arbeitszweig `claude/465-testport` ist erlaubt; sag es.

---

## 5. Was dir gehört, und was nicht

**Dir allein:** `scripts/run-tests.js`, `testing/playwright.config.js`, `package.json` (nur die Skriptzeilen), **alle bestehenden Dateien unter `testing/`** (nur der Ersatz der hart verdrahteten Adresse). Spur B schreibt parallel **neue** Specs unter `testing/tests/` und fasst bestehende erst nach deinem Merge an.

**Nicht deins:** alles andere, besonders **`docs/DEVELOPMENT.md` und `scripts/README.md`** (PR #469 einer fremden Session, eingefroren) und `CLAUDE.md`. Was dort über den Port stehen muss, schreibst du als Inbox-Wunsch (Datei, Anker, wörtlicher Ersatz, ein Satz warum), die Koordination trägt es nach dem Merge von #469 ein. **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend, **letzter Commit** nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 73 und 74.** Reviewer-Memory in einer eigenen Datei, eigener Commit nach der Runde.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push auf gepushte Historie, keine Änderung unter `~/.claude/`.

**Maschinenweit exklusiv: Port 8080** und, für deine Probe, jeder zweite Port, den du benutzt. **Fordere 8080 bei der Koordination an und melde ihn frei**; Spur A hat Vorrang. Für die Parallelprobe (siehe 7) melde vorher, welchen zweiten Port du nimmst.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` vor dem ersten Push ist Pflicht.

## 6. Was eingefroren ist

`CLAUDE.md`; die 15 promptotyping-Dokumente außer `docs/JOURNAL.md`; `docs/playbooks/`; `.github/workflows/`; `scripts/audit/`; `docs/DEVELOPMENT.md`; `scripts/README.md`. **Inbox:** Abschnitt „Änderungswünsche" am Ende des Laufplans. **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum; sofort an die Koordination. **Grund:** ändert eine Spur eine Datei, die jede Session beim Start lädt, arbeiten die anderen unter geänderten Regeln, ohne es zu merken. **Falls eine Workflow-Datei den Port braucht**, ist das ein Inbox-Wunsch, keine Änderung.

---

## 7. Das Paket

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl misst du nach. Gemessen (K) von der Koordination am 23.09.: 135 Vorkommen von `8080` in 31 `.js`-Dateien unter `testing/`, dazu `run-tests.js` (u. a. `BASIS_URL`, Z. 67), `playwright.config.js` (`baseURL` Z. 67, `webServer` Z. 100 bis 101), `package.json` (`serve`). Der Ticketbody sagt „eine Datei"; das ist überholt. **Keine Labelabfrage als Arbeitsgrundlage.**

**Entschieden:** Port über eine Umgebungsvariable, Vorgabe 8080; `baseURL` und `webServer` in der Config, `BASIS_URL` und die Fremdserver-Erkennung in `run-tests.js`, `npm run serve` lesen sie; die hart verdrahteten URLs in den Specs werden relativ gegen `baseURL` oder über eine gemeinsame Konstante. **Nachzumessen:** ob eine Spec die absolute URL aus einem Grund braucht (etwa ein Vergleich gegen `location.href`), und wie `run-tests.js` den eigenen Arbeitsbaum erkennt.

**Abnahmeprobe, und sie ist der Zweck des Pakets:** zwei Läufe gleichzeitig aus zwei Arbeitsbäumen auf zwei Ports, beide mit eigener VERDICT-Zeile. Der zweite Baum kann der Hauptbaum sein, **nur lesend**: du startest dort `npm test` mit dem Standardport, du änderst dort nichts. Frag die Koordination vorher, sie gibt beide Ports frei. Dazu Mutation: ein fremder Server auf deinem Port muss weiterhin zu Exit 2 führen; eine gelöschte Spec muss der Spec-Abgleich weiterhin melden.

**Stoppbedingung:** eine Änderung, die das Verhalten ohne gesetzte Variable ändert.

**Warum du vor B fertig sein sollst:** B braucht bestehende Specs erst nach deinem Merge. Ziel unter zwei Stunden, mechanisch.

## 8. Vorab entschieden, nicht neu zu verhandeln

Umgebungsvariable mit Vorgabe 8080; nicht mergen; kein Ticket schließen; Doku nur als Inbox-Wunsch. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination, die ihn unter „Grenzverhandlungen" einträgt.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`/Zweig/HEAD nach dem Lesen; der nachgemessene Umfang; Port angefordert und frei; Beginn und Ergebnis jeder Reviewrunde mit Rundennummer **und Kennung des geprüften Standes**.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; Stoppbedingung; fehlender Agententyp; vor der Parallelprobe (Ports).

**Externer Zustand** (CI): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`.

**Du darfst das Paket für nicht durchführbar erklären**, mit Messung und früh.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt. Laden über `ToolSearch` mit `select:PushNotification`. `rules/blockaden-melden.md`. Nicht über eine andere Spur umgehen.

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss

1. Volllauf `npm test` auf dem Standardport (anfordern), VERDICT-Zeile; die Parallelprobe aus 7 mit beiden VERDICT-Zeilen in den PR.
2. `python scripts/audit/check-no-em-dash.py --diff-base origin/main`.
3. `fable-reviewer` **vor dem ersten Push**: Zweig, Basis, Commit oder Arbeitsbaum, Ziel in einem Satz, Rundennummer, **und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?** Hier konkret: welche Prüfung in `run-tests.js` setzte stillschweigend voraus, dass der Port 8080 ist? Bei Befunden eine zweite Runde. Arbeitsbaum still halten.
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt", „Rote Zeilen" (Verteilung aus `python C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\claude-code-setup\hooks\trockenlauf-auswerten.py`, deine Zeile), „Was zurück an Christian geht".
5. PR öffnen, **nicht mergen**; #465 relabeln (`effort:medium` laut Audit) und ein Statuskommentar; Inbox-Wunsch für `docs/DEVELOPMENT.md`; Bericht an die Koordination.

### Definition of Done, als Lesertest

Wer nur den PR liest, weiß: wie man zwei Läufe parallel startet (ein Befehl je Baum); dass ohne gesetzte Variable alles wie vorher ist, und woran man das sieht; welche Zusicherungen von `run-tests.js` durch Mutation nachgewiesen weiter greifen.
