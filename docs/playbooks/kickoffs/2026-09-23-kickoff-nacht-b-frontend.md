# Kickoff Spur B `nacht-frontend`: Frontend, Playground, Naming

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Nachtlauf vom 23./24.09.2026.

**1. Autorisierung.** chsteiner hat diesen Lauf am 23.09.2026 abends freigegeben und schläft. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deinen eigenen Zweig, PRs öffnen, höchstens ein Statuskommentar und ein Relabel je Vorgang, den du anfasst; Fragen an KZW, Linda oder Christian stehen in diesem Statuskommentar. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen, Externe außerhalb von Issue-Kommentaren kontaktieren. Der Text erteilt keine technische Berechtigung: was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9). `auto:checkin` heißt heute Nacht **nicht** fragen und warten: niemand antwortet. Was eine Entscheidung braucht, die nicht im Thread steht, baust du nicht, sondern schreibst es als Frage in den Statuskommentar.

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: ein Sessionname kann beim Antworten längst einer anderen Session gehören. Die Koordination ist die ganze Nacht wach und antwortet in Minuten.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees
2. `docs/playbooks/BETRIEBSVERTRAG.md`
3. `docs/playbooks/kickoffs/2026-09-23-nachtlauf.md`, der Laufplan, **ganz**; besonders §1 Punkt 1 und 3, §2 Spur B, §3 Dateibesitz, §4 Freeze
4. `docs/DESIGN.md`, bevor du eine Zeile HTML oder CSS schreibst
5. **#433, #420, #412, #467, #448 mit allen Kommentaren** (`gh issue view N --json title,body,comments`)
6. `scripts/ingest/naming/01-fetch-and-build-index.py`, den Kopf und den Zitationswächter (`CITATION.cff`-Vergleich), vor B2
7. `docs/playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md` §2.1, Regeln 1, 3, 5, 12, 13, 17, 18, 25

**Besonders tragen für dich:** Regel 25 (alle Render- und Lesestellen auflisten, Grep über JS **und** HTML, das Projekt verdrahtet über `onclick=`-Strings); Regel 17 (Chrome hält ES-Module im Cache); ein grüner Test beweist nichts, solange nicht geprüft ist, ob er ohne die Änderung rot wäre. **Und die Regeln, die dein Ergebnis binden:** Hilfeseiten ziehen mit, wenn sich Verhalten ändert; neue Tailwind-Klassen → `npm run build:css`; HTML-Änderungen → `python scripts/build-pages.py --check`; keine Emoji-Icons, nur Heroicons inline SVG; gerade Anführungszeichen `"`; echte Umlaute; keine Em-Dashes; neue Specs mit relativen Pfaden gegen `baseURL`.

**Abbruchklausel:** weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit hat ihn mit `claude --bg --worktree nacht-frontend --name nacht-frontend` angelegt: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\nacht-frontend`, Zweig `worktree-nacht-frontend`; die Begleitnachricht nennt den HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen die Angaben halten, melden, zusammen mit dem Commit des gelesenen Laufplans. Bei Abweichung nichts ändern, melden, auf Neustart warten. Dann die Basis messen (`git fetch --quiet origin`, `git rev-list --count "origin/main...HEAD"` muss 0 sein). **Je Paket ein eigener Arbeitszweig** `claude/nacht-b1-433`, `claude/nacht-b2-420`, `claude/nacht-b3-467`, `claude/nacht-b4-448`, jeder frisch von `origin/main`. Anders als Spur A musst du nicht auf den Merge des vorigen Pakets warten, solange die Pakete keine Datei teilen; teilen sie eine, zweigst du nach dem Merge ab. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

**Dir allein:** `playground/` außer `playground/js/ui/authority/lemma-explorer.js` und weiteren #270-Render-Stellen, die Spur A benennt; `assets/js/` außer `assets/js/lib/corpus-loader.js`, der Kommentarzeile `assets/js/rendering/tei-text-reader.js:772` und denselben A-Stellen; `index.html`, `korpus.html`, `woerterbuch.html`, `assets/css/`, neue Specs unter `testing/tests/`; für B1 die bestehende `testing/tests/genre-explorer.spec.js`; für B2 `data/naming-index.json.gz`, `scripts/ingest/naming/`, die bestehende `testing/tests/naming-explorer.spec.js`, **die eine Note `authority-files/contributors.xml:191`** und **die eine Zeile `docs/DATA-MODEL.md:370`** (beide tragen die Naming-Zitation und stimmen nur mit dem Pin zusammen; benannte Ausnahmen, sonst nichts in diesen Dateien).

**Mit Spur A geteilt, abschnittsweise:** `hilfe-korpussuche.html` nur in §7 „Wörterbuch von A bis Z"; übrige `hilfe-*.html` und `docs/FEATURES.md` in allen Abschnitten außer dem zur Lemma-Seite und zu kuratierten Lemma-Angaben. Vorher `origin/main` holen.

**Die Zahlzeilen, die `scripts/audit/doc-count-audit.py` gatet, gehören Spur A**, auch in deinen Dateien. Du fasst sie nicht an.

**Nicht deins:** `tei/`, `authority-files/` außer der einen B2-Note, `data/` außer dem Naming-Index, `api/`, `scripts/` außer `scripts/ingest/naming/`, `lemma/`, die Versionsliterale, `docs/DEVELOPMENT.md` (nur die Koordination; verlangt `check-doc-inventories.py` eine Zeile für eine neue Spec, schickst du den Wortlaut an die Koordination). **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.** Bestehende Specs unter `testing/` änderst du erst nach Meldung an die Koordination.

**Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend, als **letzter Commit** des PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 85 bis 89.** Reviewer-Memory in einer eigenen Datei unter `.claude/agent-memory/fable-reviewer/`, eigener Commit nach der Runde.

**Der liegengebliebene Stand von Spur B des Tageslaufs:** Commit `5625ff334` auf dem lokalen Zweig `claude/433-filter-label` (im selben Repository, also per Cherry-pick erreichbar), dazu `.claude/tmp/sicherung-2026-09-23/playground-uncommitted.patch` im Hauptbaum und unverändert der Worktree `.claude/worktrees/mhdbdb-playground`. **Lesen darfst du alles, schreiben in keinen dieser Orte.**

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push auf gepushte Historie, keine Änderung unter `~/.claude/`.

**Maschinenweit exklusiv: Volläufe.** Die Koordination vergibt sie, einer zur Zeit, Spur A hat Vorrang. **Anfordern, warten auf die Freigabe, laufen lassen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8082` und `-- --workers=2`, auch bei `test:quick` und `test:changed`. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis: nicht deuten, melden, nach Freigabe wiederholen. Dev-Server nur für die Dauer einer Chrome-Prüfung, auf 8082. **Notationsfalle:** als Subagent lehnt der Auto-Mode-Classifier `npx playwright test --list` ab; die Testzahl eines Vollaufs steht in `testing/test-results/report.json`.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` vor dem ersten Push ist Pflicht; nicht auf `fable-advisor` ausweichen.

## 6. Was eingefroren ist

`CLAUDE.md`; die 15 promptotyping-Dokumente in `docs/` außer `docs/JOURNAL.md`, `docs/FEATURES.md` (abschnittsweise, siehe 5) und der einen Zeile `docs/DATA-MODEL.md:370`; `docs/playbooks/`; `.github/workflows/` (auch `naming-index-update.yml`: kein `workflow_dispatch`, keine Änderung); `scripts/audit/`; `scripts/README.md`; `docs/DEVELOPMENT.md`. **Inbox:** Abschnitt „Änderungswünsche" am Ende des Laufplans. **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum; sofort an die Koordination. **Grund:** ändert eine Spur eine Datei, die jede Session beim Start lädt, arbeiten die anderen unter geänderten Regeln, ohne es zu merken.

---

## 7. Die Pakete, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach, auch die, die deinen Befund stützen, und meldest einen Widerspruch. Was im Laufplan „(K)" trägt, hat die Koordination geprüft; alles andere ist ungeprüft. **Keine Labelabfrage als Arbeitsgrundlage.**

**Reihenfolge begründet:** B1 zuerst, weil fertige Arbeit in einem verwaisten Zweig liegt; B2, weil Linda die Abnahme daran gebunden hat und der Montagslauf seit dem 14.09. rot ist; B3 klein; B4 offen im Umfang.

- **B1, #433.** Laufplan §2 B1. `5625ff334` auf `claude/nacht-b1-433` übernehmen, den JOURNAL-Nachtrag aus dem Patch prüfen und übernehmen, soweit er noch stimmt. **Dazu, entschieden von KZW am 23.09. 12:32:** den ungenutzten Anzeigezweig für den Gattungs-Chip auf den Trefferkarten entfernen (`assets/js/app.js:1695`, K). Eine eigene Reviewrunde auf dem neuen Stand.
- **B2, #420.** Laufplan §2 B2 und §1 Punkt 3. **Entschieden:** Punkt 1 (Pin v0.3.0-beta) und Punkt 4 („Lemma" statt „Term", modulweit) durch Lindas Abnahme vom 16.09. **Pin:** `QUELL_VERSION` und `QUELL_DOI` **wörtlich aus Lindas `CITATION.cff`** am Tag `v0.3.0-beta` (dort der Concept-DOI `10.5281/zenodo.21914259`), Wächter unverändert, Index lokal gegen diesen Ref bauen, kein `workflow_dispatch`. Die Frage „Concept- oder Versions-DOI (`10.5281/zenodo.22690452`)?" geht an Linda in den Statuskommentar. **Haltepunkt für Punkt 1:** schlägt ein anderer Wächter an (etwa die Instanztypologie), messen, melden, Punkt 4 allein liefern. **`Closes #420` nur mit Punkt 1 und 4 im PR.** **Nicht entschieden:** der Tab „Bezeichnung" (Punkt 3) ist von Linda als optional markiert; bau ihn, wenn er ohne neue Gestaltungsfrage in die bestehenden Tabs passt, sonst nicht. #412 nicht anfassen.
- **B3, #467.** Laufplan §2 B3. **Nur das Wörterbuch bauen**; für Korpussuche und Playground messen und im Statuskommentar antworten (der Lemma-Explorer gehört heute Nacht Spur A).
- **B4, #448.** Laufplan §2 B4. Analyse je Werkzeug, Exporte nur für die tabellarischen Analysewerkzeuge unter `playground/js/ui/tei/`, nicht für die Explorer unter `authority/`. Format nach der Hauskonvention aus `assets/js/app.js` (#114).

**Eine Vorgabe, die die Koordination selbst für schwach hält, mit Ersatzfassung:** der Pin mit dem Concept-DOI in B2. Er folgt Lindas eigener Zitation und lässt die Wahl ihr; hältst du ihn trotzdem für falsch (etwa weil der Index dann eine Zitation trägt, die auf eine spätere Version auflöst), ist die Ersatzfassung: B2 liefert nur Punkt 4, und Punkt 1 geht mit deiner Messung als Vorschlag in #420.

## 8. Vorab entschieden, nicht neu zu verhandeln

Die Tabelle in §6 des Laufplans; für dich besonders: nicht mergen, kein Ticket schließen außer per `Closes #420` im PR von B2, relabeln in derselben Session. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination, die ihn unter „Grenzverhandlungen" im Laufplan einträgt, nicht in den PR-Text.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`/Zweig/HEAD nach dem Lesen; je Paket der nachgemessene Befund; Test angefordert und frei; Beginn und Ergebnis jeder Reviewrunde mit Rundennummer **und Kennung des geprüften Standes**; „PR N bereit zum Merge" mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; fehlender Agententyp; eine fachliche Frage, die niemand entschieden hat (dann: Frage ins Ticket, nächstes Paket).

**Externer Zustand** (CI): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Den Kommentar des `claude-review`-Bots liest du und beantwortest Verhaltensbefunde, bevor du „bereit zum Merge" meldest.

**Du darfst ein Paket für nicht durchführbar erklären**, mit Messung und früh; dann das nächste. Das ist etwas anderes als die Abbruchklausel in 3, die den ganzen Auftrag betrifft.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Laden über `ToolSearch` mit `select:PushNotification`. `rules/blockaden-melden.md`. Dazu eine Meldung an die Koordination. **Nicht über eine andere Spur oder die Koordination umgehen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss je Paket

1. `npm test` auf Port 8082 mit `-- --workers=2`, **nach Freigabe durch die Koordination**, Ergebnis ist die **VERDICT-Zeile**; nie durch eine Pipe, nie `npx playwright test`. Chrome-Verifikation mit realen Belegen bei jeder UI-Änderung, hart neu geladen.
2. `python scripts/build-pages.py --check`, `python scripts/audit/check-no-em-dash.py --diff-base origin/main`, `python scripts/audit/check-doc-inventories.py`, bei neuen Klassen `npm run build:css`.
3. `fable-reviewer` **vor dem ersten Push**: Zweig, Basis, Commit, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde, **und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?** Bei Befunden eine weitere Runde. Arbeitsbaum still halten, solange sie läuft.
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt", „Rote Zeilen" (deine Zeile aus `python C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\claude-code-setup\hooks\trockenlauf-auswerten.py`), „Was zurück an Christian geht". Ein Eintrag je PR genügt.
5. PR öffnen, **nicht mergen**; Statuskommentar und Relabel je Vorgang. KZW testet UI erst nach Merge und Deploy: der Statuskommentar sagt das und kündigt den Prüfweg an. „Bereit zum Merge" an die Koordination.

### Definition of Done, als Lesertest

Wer nur den PR liest, kann beantworten: was man jetzt klicken kann, das vorher nicht ging, als Prüfweg in drei Schritten; welche Tests das festhalten und ob sie ohne die Änderung rot wären; welche Hilfeseite mitgezogen ist; was offen bleibt und bei wem.
