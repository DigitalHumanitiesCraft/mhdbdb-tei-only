# Kickoff Spur B `mhdbdb-playground`: KZWs offene Playground- und Frontendmeldungen

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 23.09.2026.

**1. Autorisierung.** chsteiner hat diesen Lauf am 23.09.2026 freigegeben. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deinen eigenen Zweig, PRs öffnen, höchstens ein Statuskommentar und ein Relabel je Vorgang, den du anfasst. **Nicht**: mergen (das tut Christian), auf `main` pushen, Tickets schließen, Externe kontaktieren. Der Text erteilt keine technische Berechtigung, siehe 9. `auto:checkin` ist für diesen Lauf freigegeben (chsteiner, 23.09.), weil er erreichbar ist: du fragst unterwegs, statt zu schätzen.

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: ein Sessionname kann beim Antworten längst einer anderen Session gehören.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees
2. `docs/playbooks/BETRIEBSVERTRAG.md`
3. `docs/playbooks/kickoffs/2026-09-23-issue-abbau.md`, der Laufplan, **besonders §2 Spur B, §3 Dateibesitz (die Zahlzeilen gehören Spur A)**
4. `docs/DESIGN.md`, bevor du eine Zeile HTML oder CSS schreibst
5. **#58, #435, #433, #446 mit allen Kommentaren** (`gh issue view N --json title,body,comments`)
6. `docs/playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md` §2.1, Regeln 1, 3, 5, 12, 13, 17, 18, 25 (Verifikations-Handwerk, Chrome-Cache, Quelle der Wahrheit umstellen)

**Besonders tragen für dich:** Regel 25 (alle Render- und Lesestellen auflisten, Grep über JS **und** HTML, das Projekt verdrahtet über `onclick=`-Strings); Regel 17 (Chrome hält ES-Module im Cache, Kanarienvogel abfragen); ein grüner Test beweist nichts, solange nicht geprüft ist, ob er ohne die Änderung rot wäre. **Und die Regeln, die dein Ergebnis binden:** Hilfeseiten ziehen mit, wenn sich Verhalten ändert; neue Tailwind-Klassen → `npm run build:css`; HTML-Änderungen → `python scripts/build-pages.py --check`; keine Emoji-Icons, nur Heroicons inline SVG; gerade Anführungszeichen `"`; echte Umlaute; keine Em-Dashes.

**Abbruchklausel:** weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit hat ihn mit `claude --bg --worktree mhdbdb-playground` angelegt: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\mhdbdb-playground`, Zweig `worktree-mhdbdb-playground`, aus `main` bei `ae2e7a5fa` oder später; die Begleitnachricht nennt den HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen die Angaben halten, melden, zusammen mit dem Commit des gelesenen Laufplans. Bei Abweichung nichts ändern, melden, auf Neustart warten. Dann die Basis messen (`git fetch --quiet origin`, `git rev-list --count "origin/main...HEAD"` muss 0 sein). Ein sprechender Arbeitszweig `claude/playground-0923` ist erlaubt; sag es.

---

## 5. Was dir gehört, und was nicht

**Dir allein:** `playground/`, `assets/js/` außer `assets/js/lib/corpus-loader.js`, `index.html`, `korpus.html`, `hilfe-*.html`, `assets/css/`, **neue** Specs unter `testing/tests/`.

**Ausnahme in deinen Dateien:** die Zahlzeilen, die `scripts/audit/doc-count-audit.py` gatet (Formen-, Mapping-, Lemmazahl in `index.html`, `hilfe-*.html`, `playground/index.html`), gehören **Spur A**. Du fasst diese Zeilen nicht an.

**Bestehende Specs unter `testing/` gehören bis zum Merge von Spur C (#465, Port als Parameter) Spur C.** Neue Specs schreibst du mit relativen Pfaden gegen `baseURL`, **nie** `localhost:8080`. Musst du eine bestehende Spec ändern (wahrscheinlich `lemma-occurrence-handoff.spec.js` für #58, `main-site.spec.js` für #433), melde es, arbeite an einem anderen Paket weiter, und ändere sie erst, wenn die Koordination meldet, dass C gemergt ist und du `origin/main` geholt hast.

**Nicht deins:** `tei/`, `authority-files/`, `data/`, `api/`, `scripts/` (Spur A bzw. C), `package.json`, `testing/playwright.config.js`, **`docs/DEVELOPMENT.md` und `scripts/README.md`** (PR #469 einer fremden Session, eingefroren). **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend und als **letzten Commit** nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 70 bis 72.** Reviewer-Memory in einer eigenen Datei unter `.claude/agent-memory/fable-reviewer/`, eigener Commit nach der Runde.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push auf gepushte Historie, keine Änderung unter `~/.claude/`.

**Maschinenweit exklusiv: Port 8080.** `npm test` und `npm run serve` belegen ihn. **Fordere ihn bei der Koordination an und melde ihn frei**; Spur A und C haben Vorrang. Kein dauerhaft laufender Dev-Server. Für die Chrome-Prüfung gilt dasselbe: Server nur für die Dauer der Ansicht.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` vor dem ersten Push ist Pflicht; nicht auf `fable-advisor` ausweichen.

## 6. Was eingefroren ist

`CLAUDE.md`; die 15 promptotyping-Dokumente in `docs/` außer `docs/JOURNAL.md`; `docs/playbooks/`; `.github/workflows/`; `scripts/audit/`; `docs/DEVELOPMENT.md`; `scripts/README.md`. **Inbox:** Abschnitt „Änderungswünsche" am Ende des Laufplans. **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum; sofort an die Koordination. **Grund:** ändert eine Spur eine Datei, die jede Session beim Start lädt, arbeiten die anderen unter geänderten Regeln, ohne es zu merken.

---

## 7. Die Pakete, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach, auch die, die deinen Befund stützen, und meldest einen Widerspruch. Was im Laufplan „gemessen (K)" trägt, hat die Koordination geprüft; alles andere stammt aus Auditberichten und ist ungeprüft. **Keine Labelabfrage als Arbeitsgrundlage.**

**Reihenfolge begründet:** #58 zuerst, weil es KZWs jüngste Meldung ist (heute 08:46); die übrigen nach Größe.

- **B1, #58.** KZW: „Die Zahl stimmt jetzt, aber ich kann immer noch nicht weiterklicken zu den Belegen." **Entschieden:** der Durchklick von der Ergebnisanzeige der Dokumentsuche zu den Belegen fehlt und ist zugesagt (Kommentar vom 08.09., laut Audit). **Nachzumessen:** was sie klickt, wo der Klick heute endet, welche Stellen die Übergabe rendern und lesen. **Haltepunkt:** wenn es mehr als einen vernünftigen Zielort des Klicks gibt (Leseansicht, Konkordanz, Belegliste), leg die Optionen vor.
- **B2, #435.** Tippfilter im Textvergleich (laut Audit von KZW entschieden, im Thread nachsehen). Dazu ihre offene Frage zur Begriffs-Verteilung beantworten: laut Audit gibt es dort ein Autocomplete seit `a2e7b0b36` (#113). Nachmessen, bevor du es ihr schreibst.
- **B3, #433.** Gattungen in die Suche. Zuerst KZWs „achte darauf, ob das eh klappt" im Browser prüfen (laut Audit listet „Werke anzeigen" im Gattungsexplorer nur direkt zugeordnete Werke, keine Untergattungen). **Haltepunkt „Chip"**, wie im Thread benannt: Form der Auswahl in der Suchmaske vorlegen, bevor du baust.
- **B4, #446.** „das Korpus" statt „der Korpus", **nur in nutzersichtbarem Text** (Umfang von Christian am 23.09. bestätigt). Laut Audit vier Stellen, `hilfe-playground.html` und drei in Playground-JS; selbst suchen, mit einem Kontrollwert, der treffen muss.

**Eine Vorgabe, die die Koordination selbst für schwach hält, mit Ersatzfassung:** B1 zuerst. Braucht B1 eine bestehende Spec und muss deshalb auf C warten, zieh B2 oder B4 vor und sag es.

## 8. Vorab entschieden, nicht neu zu verhandeln

Die Tabelle in §6 des Laufplans; für dich besonders: nicht mergen, kein Ticket schließen, relabeln in derselben Session. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination, die ihn unter „Grenzverhandlungen" einträgt, nicht in den PR-Text.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`/Zweig/HEAD nach dem Lesen; je Paket der nachgemessene Befund; Port angefordert und frei; Beginn und Ergebnis jeder Reviewrunde mit Rundennummer **und Kennung des geprüften Standes**.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei, besonders eine bestehende Spec vor C's Merge; fehlender Agententyp; die Haltepunkte in B1 und B3; eine fachliche Frage, die KZW nicht entschieden hat.

**Externer Zustand** (CI): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`.

**Du darfst ein Paket für nicht durchführbar erklären**, mit Messung und früh.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt. Laden über `ToolSearch` mit `select:PushNotification`. `rules/blockaden-melden.md`. Nicht über eine andere Spur umgehen.

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss

1. `npm test` (Port anfordern), Ergebnis ist die **VERDICT-Zeile**; nie durch eine Pipe, nie `npx playwright test`. Chrome-Verifikation mit realen Belegen bei jeder UI-Änderung, hart neu geladen.
2. `python scripts/build-pages.py --check`, `python scripts/audit/check-no-em-dash.py --diff-base origin/main`, bei neuen Klassen `npm run build:css`.
3. `fable-reviewer` **vor dem ersten Push**: Zweig, Basis, Commit oder Arbeitsbaum, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde, **und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?** Bei Befunden eine zweite Runde. Arbeitsbaum still halten, solange sie läuft.
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt", „Rote Zeilen" (Verteilung aus `python C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\claude-code-setup\hooks\trockenlauf-auswerten.py`, deine Zeile), „Was zurück an Christian geht".
5. PR öffnen, **nicht mergen**; je Vorgang relabeln und ein Statuskommentar. KZW testet UI erst nach Merge und Deploy: der Statuskommentar sagt das und kündigt den Prüfweg an, statt eine PR-Vorschau anzubieten. Bericht an die Koordination.

### Definition of Done, als Lesertest

Wer nur den PR liest, kann beantworten: was KZW jetzt klicken kann, das vorher nicht ging, als Prüfweg in drei Schritten; welche Tests das festhalten und ob sie ohne die Änderung rot wären; welche Hilfeseite mitgezogen ist; was offen bleibt und bei wem.
