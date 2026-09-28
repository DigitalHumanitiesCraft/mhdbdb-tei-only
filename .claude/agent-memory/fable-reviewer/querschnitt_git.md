---
name: querschnitt-git
description: Git-Rezepte fuers Review: Altstand ohne stash, Basis pruefen, Rebase/Cherry-pick-Nullproben, Herkunft per log -S, Trailer, Blob-Hash
metadata:
  type: project
---
Stand 28.09.2026.

**Altstand ohne den Arbeitsbaum anzufassen**
- `git show <rev>:<pfad> > <scratch>/x` (git-Aufruf allein) oder `git archive <rev> tei scripts | tar -x -C <scratch>`. Nie `git stash` im Baum des Aufrufers. Nach einem Lauf im Archivordner fuer den Heute-Lauf heraus (sonst zweimal alt).
- Skripte, die `git show origin/main` und `HEAD` statt fester SHAs lesen, laufen in Folgerunden unveraendert.

**Basis und Stand**
- `git rev-parse origin/main` gegen die Auftragsangabe; `git merge-base --is-ancestor <basis> origin/main` (exit 1 = gestackt); `git diff --name-only <basis> origin/main` gegen die Dateien des Branch.
- `git log origin/main..HEAD` am Anfang UND am Ende der Runde: der Aufrufer committet weiter.
- „gepusht"? `git branch -r`.
- Commit-Datum aus `git show -s --format=%ci`, nicht aus der Erinnerung.

**Rebase / Cherry-pick**
- `git range-diff <altbasis>..<altkopf> <neubasis>..HEAD`: `=` identisch; `!` an JOURNAL/MEMORY-Commits sind meist nur fremde Kontextzeilen.
- Nullprobe: `git diff <alt> <neu> -- <dateien> | wc -l` = 0 (gleiche `--stat` reicht nicht); `git diff <alter-commit> HEAD --stat` darf nur zeigen, was main seither brachte.
- Konfliktmarker: `git grep -n -E '^(<<<<<<<|=======|>>>>>>>)' HEAD -- <dateien>`.
- Daten-PR nach Rebase mit `--ours`: (1) Versionskollision ueber alle Refs (`git for-each-ref` refs/heads + refs/remotes/origin, je Ref `INDEX_VERSION` aus `git show <ref>:assets/js/lib/corpus-loader.js`); Reservierungen im PR-Body ueberleben keinen Rebase. (2) Commit-Message gegen `git show --stat <sha>`. (3) Verlust auf JSON-Ebene pruefen; TEI: `git diff --stat <orig> HEAD -- tei/` zeigt nur main-Aenderungen.
- Mergbarkeit vorab: `git merge-tree --write-tree --name-only origin/main HEAD` (exit 1 + CONFLICT-Zeile).

**Herkunft und Zuschreibung**
- „seit #N kein Leser": `git log --oneline -S"<objekt>.<feld>" -- <pfade>`, Datum des Treffers gegen das Issue.
- „Folgestellen korrigiert": `git log -S <phrase> origin/main..HEAD`.
- Trailer: `git log --format='%h %(trailers:key=Co-Authored-By,valueonly)'`; Squash-Trailer koennen eine „(1M context)"-Variante tragen.
- Zeilenzitate `datei:N` per `git show <ref>:<pfad> | grep -n` pruefen.
- Blob gleich Runner-Build: `git fetch origin refs/pull/<N>/head`, `git rev-parse FETCH_HEAD:<p> HEAD:<p>`.
- Gegenlauf auf der Basis belegen: `git reflog --date=iso` gegen `testing/test-results/report.json` `stats.startTime`.
- Diff-Zeilenarten zaehlen: `git diff base...HEAD -- tei/ | grep '^+' | sed 's/xml:id="[^"]*"//g; s/when="[^"]*"//g' | sort | uniq -c`; CR im Diff per `--output=<datei>` und Python.
