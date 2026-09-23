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
