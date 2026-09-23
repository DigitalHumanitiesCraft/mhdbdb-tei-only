---
name: spur-b-2026-09-23-genre-tree-textfilter
description: Review Spur B 23.09.2026 (#446/#435/#433): Gattungs-Teilbaum-Zahlen aus den Indexdateien, Tailwind-Frischeprobe per Testbuild ins Temp, Spec-Tabelle in DEVELOPMENT.md ist vollstaendig gepflegt; Folge-Commit FILTER_LABEL (5625ff334): 92/133/41 aus dem Authority-Index, Volllaufzahl aus report.json statt --list
metadata:
  type: project
---

Review Spur B (Zweig `worktree-mhdbdb-playground`, HEAD cde8ca889 gegen merge-base 46e0964e9), Runde 1, 23.09.2026.

**Messrezepte, die sich gelohnt haben:**
- Gattungszahlen aus `data/authority-index.json.gz` + `data/corpus-index.json.gz`: 615 Gattungen, 133 mit mindestens einem Text (das ist die Vorschlagsmenge in app.js), 67 mit Teilbaum != direkt. Minnesang 131/140 Werke, 140/153 Texte; Artusroman 24 Werke, 28 Texte, keine Untergattung mit Text; Lyrik 0 direkt, 427 Werke, 485 Texte; Wurzel "Epik, Lyrik und Dramatik" 625 Texte. Nachbau von `findGenreSuggestions` (startsWith vor Textzahl vor Label) in Python ist zehn Zeilen und beantwortet Strict-Mode-Fragen der Specs ("Artus" liefert genau einen Vorschlag; "Minnesang" fuenf, davon zwei mit Label-Anfang minnesang).
- Textvergleich-Filter gegen `id-title, author` gefaltet: herzog 5 (ERB, ERD, HHP, HZU, HZU2), herzog ernst 2, parzival 1.
- **Tailwind-Frische**: `npx tailwindcss -i assets/css/tailwind-input.css -o $TEMP/x.css --minify` (0,6 s), dann `cmp` gegen `assets/css/tailwind-output.css`. Identisch heisst frisch. Escaped Klassen im Output nur mit `rg -F 'hover\:bg-brand-50'` suchen; die Regex-Form mit `\\:` in Single Quotes ging leer aus und sah wie ein Befund aus.
- **Spec-Tabelle in docs/DEVELOPMENT.md ist gepflegt**: `comm` zwischen `ls testing/tests/*.spec.js` und `rg -o '[a-z0-9-]+\.spec\.js' docs/DEVELOPMENT.md` ergab 34/34 Altbestand gelistet (plus zwei Geisterzeilen modal-debug/modal-simple). Eine neue Spec ohne Zeile dort ist deshalb ein echter Befund, kein Rauschen.
- Kontrollwert fuer die #446-Regex: dieselbe Regex auf `git show origin/main:playground/index.html` muss die alte Stelle treffen (tat sie, Zeile 126).

**Fallen:**
- Bash-`for`-Schleife, deren Body den Repo-Pfad enthaelt (".../Projekte/Git/..."), wird vom Worktree-Guard als "git in komplexer Form" abgelehnt. Einzelbefehle mit `echo`-Labels statt Schleife.
- `docs/FEATURES.md` Genre-Explorer-Absatz (Zeilen 174-199) beschrieb die #361-Trennung "eigene Werke" gegen "Werke im Zweig"; hilfe-playground.html war nachgezogen, FEATURES.md nicht. **Erledigt mit 97019dfc9** (Inbox-Commit der Koordination, FEATURES:177/186 tragen seither #433).
- `authority-ui.js:197` `findWorksInGenre` ist ein Wrapper ohne Aufrufer (Grep ueber playground/**, assets/**, *.html, testing/).

**Runde 2 (HEAD 2be362d11, Fix 6bc6f5c8d: Vorschlagsliste im Fluss statt Overlay), 23.09.2026:**
- **Laufzeitprobe mit echtem Klick statt `dispatchEvent('mousedown')`**: die Specs umgehen mouseup/click, genau der Pfad, an dem ein verschwindender Button und eine hochrueckende Textliste einen Streuklick erzeugen koennten. Skript in `$TEMP/*.mjs`, Import `from 'file:///C:/.../node_modules/playwright/index.mjs'` (ohne `file:///` wirft Node ERR_UNSUPPORTED_ESM_URL_SCHEME), Capture-Listener auf `#textList` fuer click/change zaehlen die Streutreffer. Ergebnis: 0/0 bei Minnesang (Liste rueckt 194 px hoch) und beim 8. Vorschlag von "Minne"; Chrome feuert den click am gemeinsamen Vorfahren, nicht an der Checkbox darunter.
- **Vor der Probe pruefen, welchen Baum :8080 ausliefert**: `curl localhost:8080/korpus.html | grep -c '<eindeutiger String aus dem Diff>'`; der Hauptcheckout hatte den String 0x, der Worktree 1x. Ein gruener Lauf gegen den falschen Baum saehe identisch aus.
- Eingabe fuer "Checkbox bei offener Liste anklicken" muss Gattung **und** Texttitel treffen: "Artus" laesst die Textliste leer (kein Titel enthaelt es), "lied" trifft 7 Gattungen und Texte (Nibelungenlied). Sichtbare Labels per `label:not([style*="display: none"])`.
- `node scripts/run-tests.js <spec>` ueberschreibt `testing/test-results/report.json`: wer die Volllauf-Zahl des Aufrufers (366) aus dem Artefakt pruefen will, liest es **vor** dem eigenen Einzellauf. Statisch `grep -E '^\s*test(\.only|\.skip)?\('` = 355 ueber 36 Dateien; die Differenz sind generierte Tests.
- Worktree-Guard lehnt neben `for`-Schleifen auch `python -c` ab, sobald der Repo-Pfad im Befehl steht: Skript ins Temp, `python -X utf8 skript.py`.
- Altverhalten seit Runde 1, nicht vom Fix: Tab aus `#textFilter` springt auf den ersten Vorschlags-Button, 150 ms spaeter schliesst blur die Liste und der Fokus faellt auf BODY. Pfeil+Enter ist der tragende Tastaturpfad. `tabindex="-1"` an den Optionen waere der Beraterhinweis.
- "Minne" hat genau 8 Vorschlaege mit Text, also zufaellig gleich `GENRE_SUGGESTION_LIMIT`; BKN haengt ueber Streitgedicht (Eltern: Dialogische Kurzform, Minnesang, Weltliches Meisterlied) am Minnesang-Teilbaum. `space-y-3` greift auf `:not([hidden])`, die Klasse `hidden` ist kein Attribut, der Abstand stoert bei display:none aber nicht.

**Folge-Commit 5625ff334 (Zweig claude/433-filter-label, FILTER_LABEL auf einen String), Runde 1, 23.09.2026:**
- Die Filterzahlen fuer den #119-Haken kommen allein aus `data/authority-index.json.gz` (`genres[].parents` + `maps.genreToWorks`, 92 Schluessel): direkt>0 = 92 Gattungen, Teilbaum>0 = 133, Differenz 41 (das war die Zahl im alten Spec-Kommentar). Lyrik genre_a2770533: 0 direkt / 427 Teilbaum. "lyrik" trifft gefaltet 7 Gattungen, Anlasslyrik hat Teilbaum 0 und faellt mit Haken heraus; die 30er-Grenze von handleSearchResults ist weit weg. Skript zehn Zeilen, ins Temp.
- Als Subagent lehnt der Auto-Mode-Classifier `npx playwright test --list` ab (Interfere With Workloads), auch mit `--config` auf testing/. Die Volllaufzahl des Aufrufers steht in `testing/test-results/report.json` (`stats.expected/unexpected`, Suites rekursiv fuer die Dateizahl): 366/36 am 23.09. 16:23 lokal, vor dem eigenen Einzellauf lesen.
- Alte Beschriftungen im Bestand nur noch in docs/journal-archive.md (historisch) und docs/JOURNAL.md:578/593 (Zusagen vom 23.09., durch den Commit eingeloest, nicht nachgezogen).

**Nachtlauf B1 (Zweig claude/nacht-b1-433, HEAD 73ede4b40 gegen 52575e73a, Cherry-pick 831efda0b = 5625ff334 per range-diff, plus Chip-Entfernung 936cdddda), Runde 1, 23.09.2026:**
- Authority-Index: `work.genre` 0/584 (Key fehlt ganz), `genres`-Laengen 354x1 / 229x2-5 / 1x0. Einziger searchLemma-Aufrufer app.js:819 (nur includedTexts); search-engine.spec.js ruft ohne genre. Kein Leser von result.genre (Dedup per Spread, Export/Tabelle greppen `genre` leer). Skripte temp/rev433_genre.py, rev433_counts.py.
- Auf der neuen Basis stehen die JOURNAL-Zusagen bei :583 („zwei Beschriftungen bleiben stehen") und :598 („der Chip wartet auf KZW"), also +5 gegen die Orphan-Zeilen. Der uncommittete JOURNAL-Nachtrag des Orphans (mhdbdb-playground, JOURNAL.md:593 „Erledigt nach dem Merge von #472 in 5625ff334") ist per Grep-Tool aus dem fremden Worktree lesbar, `git -C` dorthin lehnt der Guard ab.
- Worktree-Guard: absolute Pfade mit „Git" werden abgelehnt, relative ab cwd gehen (`python -X utf8 scripts/audit/check-no-em-dash.py --diff-base origin/main`, `python -X utf8 temp/x.py temp/y.json`). api.github.com/issues/433/comments ohne Token 200 am Laptop; KZW-Zitat 2026-09-23T12:32:58Z, die „12:32" im Kickoff ist UTC.
