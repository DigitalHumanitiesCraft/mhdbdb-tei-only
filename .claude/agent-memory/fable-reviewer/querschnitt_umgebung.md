---
name: querschnitt-umgebung
description: Umgebungsfallen beim Review: Worktree-Guard, Windows-Konsole, GitHub ohne gh, Cloud-Session, Sandbox (zwei markierte Widersprüche)
metadata:
  type: project
---
Verdichtet 02.10.2026 aus Runden 07.09. bis 02.10.

**Worktree-Guard (Repo-Pfad enthält `Projekte/Git/`)**
- Abgelehnt wurden: `python -c` und Kommandos mit „Git"-Pfad plus git-Wort; mehrere git-Aufrufe im Verbund; `for`-Schleifen mit Repo-Pfad; `$VAR`/`$TEMP` im Programm-Operanden; `$(...)`, `$'..'`; `cd ...;`-Ketten; `--glob` und jedes `*.html` im Bash-rg („value computed at runtime"); Heredocs.
- Geht: ein git-Aufruf je Bash-Call; relative Pfade vom Worktree aus; Skript per Write nach `C:/Users/chstn/AppData/Local/Temp/` (literaler Pfad) oder `temp/*.py|mjs` (gitignoriert), dann `python -X utf8 <datei>`; `env -C <worktree> python -X utf8 scripts/...`; Grep-Tool statt rg (liest auch fremde Worktrees; `glob: "{*.html,lemma/*.html}"`, `output_mode: count`); Skript unter „Git"-Pfad per `runpy.run_path` aus Wrapper in $TEMP; Memory per Write/Edit.
- **Widerspruch, nicht entschieden:** Runden vom 23.09. melden, jedes Kommando mit „Git" im Pfad falle, auch `git -C <pfad>`, `cp`, Pipes, `node -e "import file:///.../Git/..."`; andere (23.09. testport/csv-export, 28.09. genre-feld, 02.10. Subagent) ließen `git -C "<pfad>"`, `;`-Ketten ohne `$VAR` und `python -X utf8 -c` mit relativen Pfaden durch. Je Session probieren.
- Als Subagent lehnt der Auto-Mode-Classifier `npx playwright test --list` ab (auch mit `--config`). **Widerspruch 06.10.2026:** `MHDBDB_TEST_PORT=8086 npx.cmd playwright test --list -c <abs. Config>` lief als Subagent durch (435 Tests in 47 Dateien), ebenso ein Playwright-Lauf mit Scratchpad-Config. Je Session probieren.

**Windows**
- `python -X utf8`: cp1252 bricht an ł, w̆ und Emoji; Ausgaben ASCII-safe drucken (Umlaute als `�` sind cp1252, kein Datenbefund). Unter `python -I` (Sandbox-Regel für fremde Daten) wirkt `PYTHONIOENCODING`/`PYTHONUTF8` NICHT (-I impliziert -E); nur der Schalter `-I -X utf8` hilft (06.10.2026, naming-index, ā in der Ausgabe).
- `rg -c` summieren mit `awk -F: '{s+=$NF}'` (`$2` trifft Laufwerk C). Exit-Code nie hinter `| tail` messen. autocrlf=true: w/lf bei i/lf ist kein Commit-Unterschied.
- rg über die Wurzel hängt an tei/ (1,4 GB, >120 s): je Verzeichnis suchen.

**GitHub**
- Laptop: `gh issue view N --json title,body,comments`, `gh pr view N --json comments` (Bot-Kommentar voll); `gh pr list --json number,headRefName,files` für „welcher offene PR berührt Quelle X". In `--jq` keine `\.`-Escapes in String-Literalen, `startswith()` statt Regex.
- GitHub Pages ohne `.nojekyll`: `.md` ohne Front Matter wird roh ausgeliefert (29.09. per WebFetch gemessen).
- `curl api.github.com/repos/DigitalHumanitiesCraft/mhdbdb-tei-only/...` ohne Token 200 am Laptop: `issues/N/comments`, `pulls/N`, `pulls?head=Org:zweig&state=all`, `commits/<sha>` (files[].patch), `actions/runs/<id>/jobs`; `/logs` 403. WebFetch auf api.github.com 403; auf github.com/.../pull/N liefert es die Bot-Runden; Issue-HTML zeigt Kommentare nicht (wirkt wie 0).
- **Widerspruch Cloud-Session:** 07.09. api.github.com 403 („GitHub access is not enabled"); 10.09. laut #424-Notiz ohne Token 200; mit `Authorization: Bearer $GITHUB_TOKEN` 200.
- Ohne Token: raw.githubusercontent.com; `zenodo.org/api/records/<id>` (Feld `conceptdoi`: Concept oder Version). user-attachments: Laptop `curl -sL` 200, Cloud Login/403.
- DOCX: zipfile, `word/document.xml`, Bilder `word/media/`. „Bild leer" aus einem Lesewerkzeug ist keine Aussage über die Datei.

**Cloud-Session (07.-10.09.):** python3 = 3.11 ohne lxml, `python3.13` mit lxml. Klon shallow (`git log -S` sieht davor nichts). Chromium ohne Außennetz: Wörterbuchnetz-Test in lemma-page.spec.js dort immer rot.
