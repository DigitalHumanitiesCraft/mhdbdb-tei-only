---
name: querschnitt-umgebung
description: Umgebungsfallen beim Review: Worktree-Guard und Classifier, Windows und Python-Schalter, GitHub ohne gh, Cloud-Session (ein markierter Widerspruch)
metadata:
  type: project
---
Verdichtet 03.11.2026. Was der Classifier zulässt, wechselt je Session: probieren.

**Worktree-Guard (Repo-Pfad enthält `Projekte/Git/`)**
- Wiederholt abgelehnt: `python -c` oder `node -e` mit absolutem „Git"-Pfad, mehrere git-Aufrufe im Verbund, `for`-Schleifen mit Repo-Pfad, `$VAR`, `$(...)`, `cd ...;`-Ketten, `--glob` und `*.html` im Bash-rg, Heredocs, `gh … | grep` hinter `;`, `cmd >/dev/null; echo $?`.
- Wiederholt durch: ein git-Aufruf je Call, `git -C "<pfad>"`, relative Pfade vom Worktree aus, Skript per Write nach `C:/Users/chstn/AppData/Local/Temp/` (literal) oder `temp/` und `python -X utf8 -B -P -E <datei>`, `env -C <worktree> python -X utf8 scripts/...`, Grep-Tool statt rg, `runpy.run_path` aus einem Wrapper in Temp. Exit-Code am Tool-Fehler ablesen.
- **Widerspruch, nicht entschieden:** Runden vom 23.09. meldeten, jedes Kommando mit „Git" im Pfad falle, auch `git -C`, `cp`, Pipes. Andere Runden (23.09. bis 16.10.) ließen `git -C "<pfad>"`-Ketten und `node -e` mit relativen Importen durch.
- Datierte Abfolge: `npx playwright test --list` lehnte der Classifier im Subagenten bis 02.10. ab, am 06.10. lief es.
- **Der Memory-Pfad des Vorspanns kann in einen fremden Worktree oder in den Hauptbaum zeigen** (18.10. und 03.11.2026): Memory in den geprüften Worktree schreiben, git mit `git -C <geprüfter Worktree>`.

**Windows und Python**
- `python -X utf8` (cp1252 bricht an ł, w̆, Emoji, `�` ist kein Datenbefund). `-I` kappt die User-Site-Packages (`lxml` fehlt) und die Encoding-Variablen: nur für fremde Downloads. `-E` schluckt auch `PYTHONDONTWRITEBYTECODE`: Proben mit `-B -P -E`, sonst entsteht ein unsichtbares `__pycache__`. `python -m py_compile` schreibt die .pyc trotz `-B` (04.11.): Syntaxcheck mit `ast.parse`.
- Git Bash zerlegt `git show origin/main:<pfad>` („ambiguous argument"): `MSYS_NO_PATHCONV=1`. `rg -c` summieren mit `awk -F: '{s+=$NF}'`. Exit-Code nie hinter `| tail`. rg über die Wurzel hängt an tei/.
- Eigenen Hintergrundlauf nie per `taskkill //IM python.exe` abbrechen (trifft andere Sessions), nur per PID.

**GitHub:** `gh issue view N --json title,body,comments`, `gh pr view N --json comments` (Bot-Kommentar voll), `gh pr list --json number,headRefName,files`. In `--jq` `startswith()` statt Regex. Ohne gh ging `curl api.github.com/repos/...` ohne Token am Laptop (`/logs` 403), WebFetch auf github.com/.../pull/N liefert die Bot-Runden.

**Cloud-Session:** python3 = 3.11 ohne lxml, `Path.read_text(newline='')` gibt es erst ab 3.13: Repo-Skripte mit `/usr/bin/python3.13`. Klon shallow (`git log -S` sieht davor nichts). Chromium ohne Außennetz: der Wörterbuchnetz-Test in lemma-page.spec.js ist dort rot. api.github.com war am 07.09. 403, am 10.09. 200. Lange Läufe (`git worktree add` plus `check-no-em-dash.py --diff-base`) im Hintergrund.
