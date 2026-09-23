---
name: spur-b-2026-09-23-genre-tree-textfilter
description: Review Spur B 23.09.2026 (#446/#435/#433): Gattungs-Teilbaum-Zahlen aus den Indexdateien, Tailwind-Frischeprobe per Testbuild ins Temp, Spec-Tabelle in DEVELOPMENT.md ist vollstaendig gepflegt, FEATURES.md traegt die #361-Semantik
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
- `docs/FEATURES.md` Genre-Explorer-Absatz (Zeilen 174-199) beschreibt die #361-Trennung "eigene Werke" gegen "Werke im Zweig"; wer den Explorer auf Teilbaum umstellt, muss dort mitziehen. hilfe-playground.html war nachgezogen, FEATURES.md nicht.
- `authority-ui.js:197` `findWorksInGenre` ist ein Wrapper ohne Aufrufer (Grep ueber playground/**, assets/**, *.html, testing/).

**Runde 2 (HEAD 2be362d11, Fix 6bc6f5c8d: Vorschlagsliste im Fluss statt Overlay), 23.09.2026:**
- **Laufzeitprobe mit echtem Klick statt `dispatchEvent('mousedown')`**: die Specs umgehen mouseup/click, genau der Pfad, an dem ein verschwindender Button und eine hochrueckende Textliste einen Streuklick erzeugen koennten. Skript in `$TEMP/*.mjs`, Import `from 'file:///C:/.../node_modules/playwright/index.mjs'` (ohne `file:///` wirft Node ERR_UNSUPPORTED_ESM_URL_SCHEME), Capture-Listener auf `#textList` fuer click/change zaehlen die Streutreffer. Ergebnis: 0/0 bei Minnesang (Liste rueckt 194 px hoch) und beim 8. Vorschlag von "Minne"; Chrome feuert den click am gemeinsamen Vorfahren, nicht an der Checkbox darunter.
- **Vor der Probe pruefen, welchen Baum :8080 ausliefert**: `curl localhost:8080/korpus.html | grep -c '<eindeutiger String aus dem Diff>'`; der Hauptcheckout hatte den String 0x, der Worktree 1x. Ein gruener Lauf gegen den falschen Baum saehe identisch aus.
- Eingabe fuer "Checkbox bei offener Liste anklicken" muss Gattung **und** Texttitel treffen: "Artus" laesst die Textliste leer (kein Titel enthaelt es), "lied" trifft 7 Gattungen und Texte (Nibelungenlied). Sichtbare Labels per `label:not([style*="display: none"])`.
- `node scripts/run-tests.js <spec>` ueberschreibt `testing/test-results/report.json`: wer die Volllauf-Zahl des Aufrufers (366) aus dem Artefakt pruefen will, liest es **vor** dem eigenen Einzellauf. Statisch `grep -E '^\s*test(\.only|\.skip)?\('` = 355 ueber 36 Dateien; die Differenz sind generierte Tests.
- Worktree-Guard lehnt neben `for`-Schleifen auch `python -c` ab, sobald der Repo-Pfad im Befehl steht: Skript ins Temp, `python -X utf8 skript.py`.
- Altverhalten seit Runde 1, nicht vom Fix: Tab aus `#textFilter` springt auf den ersten Vorschlags-Button, 150 ms spaeter schliesst blur die Liste und der Fokus faellt auf BODY. Pfeil+Enter ist der tragende Tastaturpfad. `tabindex="-1"` an den Optionen waere der Beraterhinweis.
- "Minne" hat genau 8 Vorschlaege mit Text, also zufaellig gleich `GENRE_SUGGESTION_LIMIT`; BKN haengt ueber Streitgedicht (Eltern: Dialogische Kurzform, Minnesang, Weltliches Meisterlied) am Minnesang-Teilbaum. `space-y-3` greift auf `:not([hidden])`, die Klasse `hidden` ist kein Attribut, der Abstand stoert bei display:none aber nicht.
