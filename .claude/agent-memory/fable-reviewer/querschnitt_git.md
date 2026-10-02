---
name: querschnitt-git
description: Git-Rezepte fürs Review: Altstand ohne stash, Basis prüfen, Rebase/Cherry-pick-Nullproben, Herkunft per log -S, Trailer, Blob-Hash
metadata:
  type: project
---
Verdichtet 02.10.2026.

**Altstand ohne den Arbeitsbaum anzufassen:** `git show <rev>:<pfad> > <scratch>/x` oder `git archive <rev> tei scripts | tar -x -C <scratch>`. Nie `git stash` im Baum des Aufrufers. Skripte, die `git show origin/main` und `HEAD` statt fester SHAs lesen, laufen in Folgerunden unverändert.

**Basis und Stand**
- `git rev-parse origin/main` gegen die Auftragsangabe; `git merge-base --is-ancestor <basis> origin/main` (exit 1 = gestackt); `git diff --name-only <basis> origin/main` gegen die Dateien des Branch.
- `git log origin/main..HEAD` am Anfang UND am Ende der Runde: der Aufrufer committet weiter. „Gepusht"? `git branch -r`. Commit-Datum aus `git show -s --format=%ci`.

**Rebase / Cherry-pick**
- `git range-diff <altbasis>..<altkopf> <neubasis>..HEAD`: `=` identisch; `!` an JOURNAL/MEMORY-Commits sind meist nur fremde Kontextzeilen.
- Nullprobe: `git diff <alt> <neu> -- <dateien> | wc -l` = 0 (gleiche `--stat` reicht nicht). Konfliktmarker: `git grep -n -E '^(<<<<<<<|=======|>>>>>>>)' HEAD -- <dateien>`. Mergbarkeit vorab: `git merge-tree --write-tree --name-only origin/main HEAD`.
- Daten-PR nach Rebase mit `--ours`: (1) Versionskollision über alle Refs (`git for-each-ref` refs/heads + refs/remotes/origin, je Ref `INDEX_VERSION` aus `git show <ref>:assets/js/lib/corpus-loader.js`); Reservierungen im PR-Body überleben keinen Rebase. (2) Commit-Message gegen `git show --stat <sha>`. (3) Verlust auf JSON-Ebene prüfen.

**Herkunft und Zuschreibung**
- „Seit #N kein Leser": `git log --oneline -S"<objekt>.<feld>" -- <pfade>`, Datum gegen das Issue. „Folgestellen korrigiert": `git log -S <phrase> origin/main..HEAD`.
- Trailer: `git log --format='%h %(trailers:key=Co-Authored-By,valueonly)'`. Zeilenzitate `datei:N` per `git show <ref>:<pfad> | grep -n` prüfen.
- Blob gleich Runner-Build: `git fetch origin refs/pull/<N>/head`, `git rev-parse FETCH_HEAD:<p> HEAD:<p>`.
- Gegenlauf auf der Basis belegen: `git reflog --date=iso` gegen `testing/test-results/report.json` `stats.startTime`.
- Diff-Zeilenarten zählen: `git diff base...HEAD -- tei/ | grep '^+' | sed 's/xml:id="[^"]*"//g; s/when="[^"]*"//g' | sort | uniq -c`.
