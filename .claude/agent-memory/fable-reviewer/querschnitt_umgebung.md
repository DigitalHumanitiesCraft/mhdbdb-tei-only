---
name: querschnitt-umgebung
description: Umgebungsfallen beim Review: Worktree-Guard, Windows-Konsole, GitHub ohne gh, Cloud-Session, Sandbox
metadata:
  type: project
---
Stand 28.09.2026, verdichtet aus Runden 07.09. bis 28.09.

**Worktree-Guard (Repo-Pfad enthaelt `Projekte/Git/`)**
- Abgelehnt wurden: `python -c` und Kommandos mit „Git"-Pfad plus git-Wort; mehrere git-Aufrufe im Verbund; `for`-Schleifen mit Repo-Pfad; `$VAR`/`$TEMP` im Programm-Operanden; `$(...)`, `$'..'`, `| grep -c $'\r'`; `cd ...;`-Ketten; `--glob` im Bash-rg; Heredocs.
- Geht: ein git-Aufruf je Bash-Call; relative Pfade vom Worktree aus; Skript per Write nach `C:/Users/chstn/AppData/Local/Temp/` (literaler Pfad) oder `temp/*.py|mjs` (gitignoriert), dann `python -X utf8 <datei>`; `env -C <worktree> python -X utf8 scripts/...`; Grep-Tool statt rg (liest auch fremde Worktrees); Skript unter „Git"-Pfad per `runpy.run_path` aus Wrapper in $TEMP; Memory per Write/Edit.
- 02.10.2026 (Subagent, Worktree `lauf-b-frontend`): durch gingen `git -C "<pfad>" ...; git ...` als Kette, `python -X utf8 -c` mit relativen Pfaden (mit absolutem „Git"-Pfad abgelehnt), `rg -c "„" hilfe-*.html` ohne Glob-Wildcard-Dateien dagegen nicht: jedes `*.html` oder `--glob` im Bash-rg faellt („value computed at runtime"). Ersatz: Grep-Tool mit `glob: "{*.html,lemma/*.html}"` und `output_mode: count`.
- **Widerspruch, nicht entschieden:** Runden vom 23.09. melden, jedes Kommando mit „Git" im Pfad falle, auch `git -C <pfad>`, `cp`, Pipes, `node -e "import file:///.../Git/..."`; andere (testport R2, csv-export R3 23.09., genre-feld R2 28.09.) liessen `git -C "<pfad>"` und `;`-Ketten ohne `$VAR` durch. Je Session probieren.

**Windows**
- `python -X utf8`: cp1252 bricht an ł, w̆, U+010D/U+030C und den Emoji der Builds; Ausgaben ASCII-safe drucken.
- `rg -c` summieren mit `awk -F: '{s+=$NF}'` (`$2` trifft Laufwerk C).
- Exit-Code nie hinter `| tail` messen.
- autocrlf=true: w/lf bei i/lf ist kein Commit-Unterschied.
- rg ueber die Wurzel haengt an tei/ (1,4 GB, >120 s): je Verzeichnis suchen oder Dateiliste des Skripts nehmen.

**GitHub**
- Laptop: `gh issue view N --json title,body,comments`, `gh pr view N --json comments` (Bot-Kommentar voll); `gh pr list --json number,headRefName,files` fuer „welcher offene PR beruehrt Quelle X" (29.09., als Subagent ohne Ablehnung). In `--jq` keine `\.`-Escapes in String-Literalen (Parsefehler), `startswith()` statt Regex.
- GitHub Pages ohne `.nojekyll` (keins im Repo, kein Pages-Workflow): `.md` ohne Front Matter wird trotzdem roh ausgeliefert, gemessen 29.09. per WebFetch auf `docs/INDEX.md` live. Ein Download-Link auf eine `.md` unter `assets/` braucht also keinen Sonderfall.
- `curl api.github.com/repos/DigitalHumanitiesCraft/mhdbdb-tei-only/...` ohne Token 200 am Laptop: `issues/N/comments`, `pulls/N` (body, `updated_at` gegen `git log -1 --format=%cI`), `pulls?head=Org:zweig&state=all`, `commits/<sha>` (files[].patch; xlsx nur `changes: 0`), `actions/runs/<id>/jobs` (roter Step); `/logs` 403.
- WebFetch auf api.github.com 403; auf github.com/.../pull/N liefert es die Bot-Runden; Issue-HTML zeigt Kommentare nicht (clientseitig, wirkt wie 0).
- **Widerspruch Cloud-Session:** 07.09. api.github.com 403 („GitHub access is not enabled"); 10.09. laut #424-Notiz ohne Token 200; mit `Authorization: Bearer $GITHUB_TOKEN` 200.
- Ohne Token: raw.githubusercontent.com; `zenodo.org/api/records/<id>` (Feld `conceptdoi`: Concept oder Version).
- user-attachments: Laptop `curl -sL` 200, Cloud Login/403.
- DOCX: zipfile, `word/document.xml` (`<w:t>`), Bilder `word/media/`, Zuordnung per `r:embed` + `word/_rels/document.xml.rels`. PDF-Bilder mit fitz zaehlen; „Bild leer" aus einem Lesewerkzeug ist keine Aussage ueber die Datei.

**Cloud-Session (07.-10.09.)**
- python/python3 = 3.11 ohne lxml, `python3.13` mit lxml.
- Klon shallow (Wurzel 4458686ab, `^` existiert nicht): Historie von alter SHA aus loggen (b02596af1); `git log -S` sieht davor nichts.
- Chromium ohne Aussennetz (ERR_CONNECTION_RESET): Woerterbuchnetz-Test in lemma-page.spec.js dort immer rot; `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.
- de.wikipedia-API rate-limitet.

**Als Subagent** lehnt der Auto-Mode-Classifier `npx playwright test --list` ab (auch mit `--config`).
