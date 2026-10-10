# Kickoff Spur `lauf-c-zahlen`: Katalogzahlen raus, seltenes Gate für Verszählungszahlen (#451, #414)

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 10.10.2026. Laufplan: `docs/playbooks/kickoffs/2026-10-10-lauf.md`.

**1. Autorisierung.** chsteiner hat #451 am 18.09.2026 entschieden (Body des Tickets: Plan, Kriterium, Reihenfolge, Abbruchbedingung) und am 10.10.2026 den Zuschnitt von #414 (Kommentar „Entschieden von @chsteiner am 10.10.2026“) sowie den Lauf mit drei Spuren freigegeben. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deine eigenen `claude/*`-Zweige, zwei PRs öffnen, in beiden Tickets höchstens ein Statuskommentar und ein Relabel. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen, Externe ansprechen. Der Text erteilt keine technische Berechtigung: Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9).

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees (besonders „Self-Inflicted Overhead“: eine Aussage über ein Gate wird durch einen Lauf belegt, mit Mutationsprobe)
2. `docs/playbooks/BETRIEBSVERTRAG.md` (gelesen, nicht kopiert; nenne in deiner ersten Meldung den Commit, an dem du ihn gelesen hast)
3. Diese Datei als abgelegte Fassung und den Laufplan daneben. Sag in deiner ersten Meldung, ob die abgelegte Fassung mit der zugestellten übereinstimmt.
4. **#451 und #414 mit allen Kommentaren** (`gh issue view N --json title,body,comments`), dazu #449 und #450 (der Anlass von #451). Die Vorab-Messung zu #414 und die Entscheidung stehen in den letzten beiden Kommentaren.
5. `scripts/audit/doc-count-audit.py` ganz, `.github/workflows/data-integrity.yml`, `docs/DEVELOPMENT.md` zu den Gates, `fehlerjournal.md` Eintrag 6 und 15 (in #451 zitiert)

**Besonders tragen für dich:** Ersetzt wird durch Größenordnung, **nie durch eine Allaussage** („alle“, „je Text“, „immer“); Vertragszahlen (Index-Versionen, Positionszählung, 1200px, 30-Tage-Cache, Budgets) und Chronik (JOURNAL, Archiv, Fehlerjournal, datierte ADRs) werden nicht angefasst; ausgelieferte Seiten deutsch mit echten Umlauten; keine Em-Dashes; `build-pages.py --check` bei HTML.

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit legt ihn mit `claude --bg --worktree lauf-c-zahlen --name lauf-c-zahlen --model sonnet --effort medium` an: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\lauf-c-zahlen`, Zweig `worktree-lauf-c-zahlen`. Die Begleitnachricht nennt den erwarteten HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen diese Angaben halten und melden. Bei Abweichung nichts ändern, melden, auf den Neustart durch die Koordination warten. Dann `git fetch --quiet origin` und den Arbeitszweig `claude/451-katalogzahlen` frisch von `origin/main` anlegen (später `claude/414-seltenes-gate`, frisch von `origin/main` nach dem Merge von C1); `git rev-list --count "origin/main...HEAD"` muss 0 sein. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

Maßgeblich ist §2 des Laufplans. **Dir allein:** `scripts/audit/doc-count-audit.py`, `scripts/audit/count-verse-numbering-resets.py`, `scripts/audit/count-editorial-notes-and-div-heads.py`, neue Gate-Dateien unter `scripts/audit/`, `.github/workflows/data-integrity.yml` und ein neuer Workflow für das seltene Gate; Kommentare mit Zahlen in `assets/js/rendering/tei-text-reader.js` und in `playground/js/`; `README.md`, `playground/readme.md`, der Text von `hilfe-playground.html` (nicht Nav und Footer, die sind generiert), `docs/DESIGN.md`, `docs/DEVELOPMENT.md`, `docs/TEI-MODEL.md` (außer §11, der Spur A gehört), `docs/FEATURES.md` außer den Absätzen zur Korpussuche und Lemma-Auflösung (Spur B).

**Grenzfall:** In `tei-text-reader.js` änderst du nur Kommentare. Schreibt Spur B dort Code, rebased, wer als zweiter merged.

**Nicht deins:** `tei/`, `authority-files/`, `data/`, `api/`, `scripts/build-*.py` (Spur A); `assets/js/search/`, `assets/js/app.js`, `docs/CONTRACTS.md` (Spuren A und B). **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.** Der offene PR #555 (Spur 93, wartet auf KZW) berührt `docs/FEATURES.md`, `docs/DEVELOPMENT.md` und `hilfe-playground.html`; wird er vor dir gemergt, rebased du.

**Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend, als **letzter Commit** des jeweiligen PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 140 bis 144.** Reviewer-Memory unter `.claude/agent-memory/fable-reviewer/` in einem eigenen Commit nach der Runde.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push außer `--force-with-lease` auf deinen eigenen `claude/*`-Zweigen nach einem Rebase, keine Änderung unter `~/.claude/`.

**Maschinenweit exklusiv: volle Testläufe und Chrome.** Die Koordination vergibt beides, einer zur Zeit. **Anfordern, auf die Freigabe warten, nutzen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8086` und `-- --workers=2`, auch bei `test:quick` und `test:changed`. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` vor dem ersten Push ist Pflicht; nicht auf `fable-advisor` ausweichen.

## 6. Was eingefroren ist

`CLAUDE.md`; `docs/playbooks/`; `.github/workflows/` außer den dir zugeteilten; `scripts/audit/` außer den dir zugeteilten Dateien. **Schritt 4 von #451 (eine Zeile in `CLAUDE.md`) schreibst du nicht selbst**, sondern schickst den Wortlaut an die Koordination (Format: Ankertext, wörtlicher Ersatztext, ein Satz warum); sie trägt ihn nach der Abnahme ein.

---

## 7. Die Pakete, in dieser Reihenfolge, je ein PR

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach und meldest einen Widerspruch. Der Body von #451 sagt selbst, dass „rund 250 von 954“ Skriptzeilen nicht einzeln nachgemessen sind. „(K)“ = von der Koordination am 10.10. gemessen oder gegengeprüft.

- **C1, #451.** Die Schritte 1 bis 3 aus dem Body, in dieser Reihenfolge und mit der Abbruchbedingung von dort. Vor Schritt 1: `doc-count-audit.py --check` auf dem Ausgangsstand laufen lassen und die Ausgabe festhalten; nach Schritt 1 noch einmal, und jede Abweichung erklären. Eine Aussage im PR über das, was das Gate danach nicht mehr prüft, belegst du mit einer Mutationsprobe (Zustand herstellen, Gate laufen lassen, zurücksetzen, Rücksetzung prüfen), und vorher prüfst du, dass die Probe die gemeinte Stelle trifft. Je Streichung in Schritt 2 ein `grep` über `testing/` und `scripts/`.
- **C2, #414.** Ein eigenes, selteneres Gate für die Verszählungs- und div-Zahlen (wöchentlicher Workflow und bei Änderungen unter `tei/`), nicht im regulären `doc-count-audit.py`-Lauf (K: Laufzeit je ein Lauf 136 s und 167 s gegen 5 s). Die beiden Skripte geben ihren Zahlenblock maschinenlesbar aus; das Gate prüft die sieben Fundstellen (heutige Lage im Kommentar vom 10.10. in #414) **und** liest dafür `.js`-Kommentare in einer benannten Dateiliste. Die Lemma-Gesamtzahlen in JS-Kommentaren außerhalb davon (K: 43.710, 43.754, 43.879 an fünf Stellen, `doc-count-audit.py` misst 43.710) ersetzt du im Sinn von C1 durch eine Größenordnung. Die veralteten Zeilenverweise im Docstring von `count-verse-numbering-resets.py` gehen mit.

## 8. Vorab entschieden, nicht neu zu verhandeln

Die Zuschnitte oben und alles, was der Body von #451 unter „Was ausdrücklich nicht passiert“ und „Entschieden“ führt; nicht mergen, kein Ticket schließen, relabeln in derselben Session. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig und HEAD, der Commit des gelesenen Betriebsvertrags und ob die abgelegte Kickoff-Fassung übereinstimmt; die Ausgabe von `doc-count-audit.py --check` vor und nach Schritt 1; der Wortlaut für `CLAUDE.md`; Test angefordert und frei; **Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes**; „PR N bereit zum Merge“ mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; fehlender Agententyp.

**Externer Zustand** (CI): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Den Kommentar des Review-Bots lesen und Verhaltensbefunde beantworten, bevor du „bereit zum Merge“ meldest.

**Du darfst ein Paket für nicht durchführbar erklären**, mit Messung und früh; dann das nächste. Für C1 gilt zusätzlich die Abbruchbedingung aus dem Body von #451: reißt die Schätzung, dann in Schritt 2, und der Rest wird dateiweise nachgeholt.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt. Laden über `ToolSearch` mit `select:PushNotification`. Dazu eine Meldung an die Koordination. **Eine Blockade wird nicht über eine andere Spur oder die Koordination umgangen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss, je PR

1. `doc-count-audit.py --check`, `check-doc-inventories.py`, `check-no-em-dash.py --diff-base origin/main`, `build-pages.py --check` bei HTML; für C2 das neue Gate selbst, grün auf dem Stand und rot nach einer Mutationsprobe an einer der sieben Stellen.
2. `npm test` auf Port 8086 mit `-- --workers=2`, **nach Freigabe durch die Koordination**; das Ergebnis ist die **VERDICT-Zeile**, nie durch eine Pipe, nie `npx playwright test`.
3. `fable-reviewer` **vor dem ersten Push**: Zweig, Basis, ob Commit oder Arbeitsbaum, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde, **und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?** (C1: jede Prüfung und jede Prosa, die sich auf die gestrichenen Ausnahmemengen oder Code-Keys stützte.)
4. Journaleintrag als **letzter** Commit nach `git fetch origin`.
5. PR mit „Bezug: #N, bleibt offen“ (kein Closing-Keyword), **nicht mergen**; „bereit zum Merge“ an die Koordination. Nach dem Merge ein Abschluss-Statuskommentar im Ticket; eine Abnahme durch KZW oder Julia braucht keines der beiden.

### Definition of Done, als Lesertest

Wer nur den PR liest, kann beantworten: welche Teile von `doc-count-audit.py` entfallen und was das Gate danach noch prüft (mit Mutationsprobe belegt); welche Katalogzahlen aus welchen Dateien verschwunden sind und wodurch ersetzt; wann das neue Gate läuft, was es prüft und wie lange es braucht.
