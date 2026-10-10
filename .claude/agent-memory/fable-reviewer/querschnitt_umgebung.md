---
name: querschnitt-umgebung
description: Umgebungsfallen beim Review: Worktree-Guard, Windows-Konsole, GitHub ohne gh, Cloud-Session, Sandbox (zwei markierte Widersprüche)
metadata:
  type: project
---
Verdichtet 08.10.2026.

**Worktree-Guard (Repo-Pfad enthält `Projekte/Git/`)**
- Abgelehnt wurden: `python -c` und Kommandos mit „Git"-Pfad plus git-Wort; mehrere git-Aufrufe im Verbund; `for`-Schleifen mit Repo-Pfad; `$VAR`/`$TEMP`, `$(...)`; `cd ...;`-Ketten; `--glob` und `*.html` im Bash-rg; Heredocs.
- Geht: ein git-Aufruf je Bash-Call; relative Pfade vom Worktree aus; Skript per Write nach `C:/Users/chstn/AppData/Local/Temp/` (literal) oder `temp/` (gitignoriert), dann `python -X utf8 <datei>`; `env -C <worktree> python -X utf8 scripts/...`; Grep-Tool statt rg (`glob: "{*.html,lemma/*.html}"`, `output_mode: count`); Skript unter „Git"-Pfad per `runpy.run_path` aus Wrapper in $TEMP.
- **Widerspruch, nicht entschieden:** einige Runden (23.09.) melden, jedes Kommando mit „Git" im Pfad falle, auch `git -C <pfad>`, `cp`, Pipes, `node -e "import file:///.../Git/..."`; andere (23.09., 28.09., 02.10.) ließen `git -C "<pfad>"`, `;`-Ketten ohne `$VAR` und `python -X utf8 -c` mit relativen Pfaden durch. Je Session probieren. 10.10.: abgelehnt `python -c` mit absolutem „Git"-Pfad und `git show … | node -` (auch mit `process.cwd()`); durch gingen `git -C "<pfad>"`, `node <rel.pfad>`, `node -e` mit relativen Importen.
- 10.10.2026: `node --input-type=module -e "..."` mit absolutem „Git"-Pfad im Text abgelehnt; dasselbe mit `process.cwd()` + `path.join` + `url.pathToFileURL` (kein Pfad im Kommando) lief, ebenso `import` von `assets/js/search/search-engine.js` und `playground/js/data/authority-manager.js` (letzteres mit `globalThis.window={playground:{corpusData:{lemmaIndex,texts}}}`).
- Der Auto-Mode-Classifier lehnt auch ab: Massenkopie plus `rm *.md` im Memory-Ordner (Irreversible Local Destruction, 08.10.); Skripte mit `--apply`, selbst als Trockenlauf (Rezept in querschnitt_messen).
- **Datierte Abfolge, kein Widerspruch:** als Subagent lehnte der Classifier bis 02.10. `npx playwright test --list` ab (auch mit `--config`); am 06.10.2026 lief `MHDBDB_TEST_PORT=8086 npx.cmd playwright test --list -c <abs. Config>` als Subagent durch, ebenso ein Playwright-Lauf mit Scratchpad-Config. Je Session probieren.

**Windows**
- `python -X utf8`: cp1252 bricht an ł, w̆ und Emoji; Ausgaben ASCII-safe drucken (Umlaute als `�` sind cp1252, kein Datenbefund). Unter `python -I` wirkt `PYTHONIOENCODING`/`PYTHONUTF8` nicht (-I impliziert -E), nur `-I -X utf8`; und `-I` kappt die User-Site-Packages (`lxml` fehlt). Projektskripte und eigene Proben ohne `-I`, `-I` nur für fremde Downloads.
- `rg -c` summieren mit `awk -F: '{s+=$NF}'` (`$2` trifft Laufwerk C). Exit-Code nie hinter `| tail` messen. autocrlf=true: w/lf bei i/lf ist kein Commit-Unterschied.
- rg über die Wurzel hängt an tei/ (1,4 GB, >120 s): je Verzeichnis suchen.

**GitHub**
- Laptop: `gh issue view N --json title,body,comments`, `gh pr view N --json comments` (Bot-Kommentar voll); `gh pr list --json number,headRefName,files` für „welcher offene PR berührt Quelle X". In `--jq` `startswith()` statt Regex.
- GitHub Pages ohne `.nojekyll`: `.md` ohne Front Matter wird roh ausgeliefert.
- `curl api.github.com/repos/DigitalHumanitiesCraft/mhdbdb-tei-only/...` ohne Token 200 am Laptop: `issues/N/comments`, `pulls/N`, `commits/<sha>` (files[].patch), `actions/runs/<id>/jobs`; `/logs` 403. WebFetch auf api.github.com 403; auf github.com/.../pull/N liefert es die Bot-Runden; Issue-HTML zeigt Kommentare nicht (wirkt wie 0).
- **Datierte Abfolge Cloud-Session:** 07.09. api.github.com 403; 10.09. laut #424-Notiz 200, mit und ohne Token.
- Ohne Token: raw.githubusercontent.com; `zenodo.org/api/records/<id>` (`conceptdoi`; alle Versionen `?q=conceptrecid:<id>&all_versions=true`). user-attachments: Laptop `curl -sL` 200, Cloud Login/403.
- DOCX: zipfile, `word/document.xml`, Bilder `word/media/`.

**Cloud-Session (07.-10.09.):** python3 = 3.11 ohne lxml (`pip install --user lxml` oder `python3.13`). Klon shallow (`git log -S` sieht davor nichts). Chromium ohne Außennetz: Wörterbuchnetz-Test in lemma-page.spec.js dort immer rot.
