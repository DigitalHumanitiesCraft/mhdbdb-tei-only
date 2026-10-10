# Kickoff Spur `lauf-d-suche-tests`: Playground-Suche beschleunigen, Such-Benchmark mit Budget, Testlaufzeit (#564)

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden. Laufplan: `docs/playbooks/kickoffs/2026-10-10-lauf-564.md`.

**1. Autorisierung.** chsteiner hat #564 am 10.10.2026 entschieden (Kommentar „Entschieden von @chsteiner am 10.10.2026“) und den autonomen Start freigegeben. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deine eigenen `claude/*`-Zweige, je Paket ein PR, im Ticket höchstens ein Statuskommentar je Paket. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen, Externe ansprechen. Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9).

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees
2. `docs/playbooks/BETRIEBSVERTRAG.md` (gelesen, nicht kopiert; nenne in deiner ersten Meldung den Commit)
3. Diese Datei und den Laufplan daneben; sag, ob die abgelegte Fassung mit der zugestellten übereinstimmt
4. **#564 mit allen Kommentaren** (`gh issue view 564 --json title,body,comments`): Ausgangsmessung, Kandidatenliste, Entscheidung
5. `docs/CONTRACTS.md` §C (Auflösungsstufen, seit #463 mit `stage1Holds`), `playground/js/data/authority-manager.js` ganz, `assets/js/lib/lemma-resolve.js`, `assets/js/search/search-engine.js`, `scripts/run-tests.js`, `playwright.config.*`

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei. Melde es.

---

## 4. Dein Worktree

Start mit `claude --bg --worktree lauf-d-suche-tests --name lauf-d-suche-tests --model sonnet --effort medium`. **Erste Handlung:** `pwd`, Zweig, HEAD messen und melden; dann `git fetch --quiet origin` und je Paket einen Arbeitszweig frisch von `origin/main` (`claude/564-playground-suche`, `claude/564-testdauer`, `claude/564-langsame-tests`); `git rev-list --count "origin/main...HEAD"` muss 0 sein. `npm ci` vor dem ersten Test.

## 5. Was dir gehört, und was nicht

Maßgeblich ist §2 des Laufplans. **Dir:** `playground/js/data/authority-manager.js`, `assets/js/lib/lemma-resolve.js`, `assets/js/search/`, eine neue Benchmark-Datei unter `scripts/audit/` mit Budgetdatei und ein eigener Workflow dafür; `scripts/run-tests.js`, `testing/tests/`, `playwright.config.*`; in `docs/ARCHITECTURE.md` und `docs/FEATURES.md` die Absätze zur Playground-Suche; Inventarzeilen in `docs/DEVELOPMENT.md`.

**Nicht deins:** alle übrigen Workflows und das Laufzeitgate (Spur E); `tei/`, `authority-files/`, `data/`, `api/`. **Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend als letzter Commit; **deine Fehlerjournal-Nummern sind 150 bis 154**. Reviewer-Memory unter `.claude/agent-memory/fable-reviewer/` nur anhängend, eigener Commit, Hook-Grenze beachten.

**Maschinenweit exklusiv: volle Testläufe und Chrome**, die Koordination vergibt. Du testest mit `MHDBDB_TEST_PORT=8087` und `-- --workers=2`. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt.** `fable-reviewer` (mit `model: opus`, solange Fable am Limit ist; im PR vermerken) vor dem ersten Push ist Pflicht.

## 6. Was eingefroren ist

`CLAUDE.md`; `docs/playbooks/`. Änderungswünsche an die Koordination.

---

## 7. Die Pakete, in dieser Reihenfolge, je ein PR

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl misst du nach. Die ms-Werte in #564 stammen aus einem Node-Skript eines Subagenten (Pfad im Ticket nicht genannt); nur `authority-manager.js:108` (`Object.keys(this.authorityData.variants || {}).length`) hat die Koordination am Code nachgesehen (K).

- **D1, Playground-Suche plus Benchmark.** Ziel: die Auflösung im Playground in die Größenordnung der Hauptseite. Kandidaten aus #564: die Leerprüfung über alle Variantenschlüssel je Stufe-2-Auflösung; die Normalisierung aller Lemmata je Suche in Stufe 1 und 3 (einmal je geladenem Index vorberechnen); Lookups per Schleife statt Map; der Autocomplete-Vollscan je Tastendruck. **Ergebnisgleichheit ist Pflicht:** für eine feste Liste von Eingaben (exakt, Variante, Präfix, unbelegt, Homograph, mehrdeutige Variante, darunter `rosse`, `gat`, `roz`, `vlâder`) liefert die neue Fassung dieselben IDs in derselben Reihenfolge wie `origin/main`, im PR als Tabelle. Dazu ein **Node-Benchmark** unter `scripts/audit/` gegen die echten `data/*.json.gz`, der Hauptseite und Playground misst (warm, feste Wiederholungszahl, Median) und gegen eine Budgetdatei hält: Budget = gemessener Wert nach D1 × 1,5, mindestens 1 ms Untergrenze gegen Rauschen; rot bei Überschreitung, Exit 1. Ein eigener Workflow führt ihn bei Änderungen unter `assets/js/search/`, `assets/js/lib/`, `playground/js/data/` und an sich selbst aus. Mutationsprobe: eine absichtlich teure Zeile einbauen, Benchmark muss rot werden, zurücksetzen, Rücksetzung prüfen.
- **D2, `run-tests.js`.** Die Dauer je Spec-Datei aus `testing/test-results/report.json` nach der VERDICT-Zeile ausgeben, die zehn langsamsten, Summe der Testdauern und Wanduhr; die VERDICT-Zeile bleibt unverändert die erste Ergebniszeile. Kein Gate.
- **D3, langsamste Tests.** Ausgang: `multi-lemma-export` (in #564: 130,6 s für 5 Tests, ein Test 44,4 s), `results-table`, `reading-view`, `lemma-page`, `main-site`. Feste Wartezeiten durch Warten auf Ereignisse ersetzen, Großtexte durch den kleinsten passenden Text, doppelte Setup-Arbeit bündeln. **Kein Test verliert seine Aussage** (§3.2 des Laufplans): je geänderter Test ein Satz im PR, was er vorher prüfte und was jetzt. Vorher und nachher je Spec gemessen (D2-Ausgabe), gleiche Workerzahl.

## 8. Vorab entschieden

Die Entscheidung in #564 und §3 des Laufplans. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig, HEAD, Commit des Betriebsvertrags, Übereinstimmung des Kickoffs; je Paket Messung vorher; Test angefordert und frei; Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des Standes; „PR N bereit zum Merge“ mit HEAD, VERDICT-Zeile, Reviewurteil, CI und gelesenem Bot-Kommentar.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; fehlender Agententyp; Ergebnisgleichheit in D1 nicht herstellbar.

**Externer Zustand** (CI): `Monitor` oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian (laden über `ToolSearch` mit `select:PushNotification`), dazu eine Meldung an die Koordination. Nie über eine andere Session umgehen.

## 10. Abschluss, je PR

1. Die Gates, die die Änderung berührt (`check-no-em-dash.py --diff-base origin/main`, `check-doc-inventories.py`, `doc-count-audit.py --check`, bei D1 der neue Benchmark grün und nach Mutationsprobe rot).
2. `npm test` auf Port 8087 mit `-- --workers=2`, nach Freigabe; Ergebnis ist die VERDICT-Zeile.
3. `fable-reviewer` vor dem ersten Push mit Zweig, Basis, Ziel, Rundennummer, ab Runde 2 die Vorbefunde, und der Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?
4. Journaleintrag als letzter Commit nach `git fetch origin`.
5. PR mit „Bezug: #564“ ohne Closing-Keyword, Laufzeitwirkung im Body, nicht mergen; „bereit zum Merge“ an die Koordination.
