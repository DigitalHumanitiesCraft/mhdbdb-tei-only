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

**Squash-Merges zählen und Stack-Mechanik (07.10.2026, Merge-Playbook-Review)**
- `git log --no-merges | grep -c '(#N)$'` zählt keine Squash-Merges, sondern Commits mit Issue-Bezug: 01.09. bis `8a664d217` 113 Treffer, davon 80 Squash-Merges und 33 Einzelcommits (Branch-Commits, die per Merge-Commit kamen, direkte main-Commits). Messen je Commit gegen `gh api repos/<org>/<repo>/pulls/N --jq .merge_commit_sha` (404 = Issue, ungleicher SHA = kein Squash); Skript ~2 min für 113.
- Scratch-Repo-Probe (Basis 2 Commits, squash nach main, dep darauf): dep ist nur CONFLICTING, wenn er dieselben Zeilen weiterbearbeitet; bei anderer Datei mergeable, zeigt aber die Basis-Commits mit. Schlichtes `git rebase main` bricht in beiden Fällen (Basis-Commits werden replayt), `git rebase --onto main <alter Basis-Head>` geht in beiden. Unter Merge-Commit war schlichtes `rebase main` sauber: eine Squash-Umstellung macht jede Anweisung „auf main rebasen" für Stack-PRs falsch (#397-Frage).
- Nach Squash ist kein Branch-Head Vorfahr von main: `git branch --merged origin/main` listet ihn nicht, `git branch -d` verweigert („not fully merged"), nur `-D` löscht (Probe 07.10. in `git clone --shared --no-checkout` im Scratchpad an `claude/526-makron`/#534). Jede Anweisung „gemergte Branches löschen" oder jeder Guard auf `--merged` ist nach einer Squash-Umstellung mitzulesen.
- Repo: `delete_branch_on_merge` true; Auto-Delete 2 bis 3 s nach dem Merge (`head_ref_deleted` in den Issue-Events), und GitHub retargetet abhängige PRs dabei selbst (#183: `base_ref_changed` im selben Sekundenstempel wie `head_ref_deleted` von #177, 08.07.2026). Events: `gh api repos/.../issues/N/events --jq '.[] | select(.event=="base_ref_changed" ...)'`.

**EOL- und Attribut-Proben ohne den Arbeitsbaum (07.10.2026)**
- Probeklon im Scratchpad: `git clone --shared --no-checkout --branch main <repo> <scratch>/eolprobe`, dann `git -C ... sparse-checkout set --no-cone .gitattributes assets/downloads/x.md` **ohne führenden Slash** (Git Bash macht aus `/.gitattributes` den Pfad `C:/Program Files/Git/.gitattributes`; Warnung ignorieren) und `sparse-checkout reapply`. Erbt `core.autocrlf` aus der System-Config, `config core.autocrlf false` + `core.eol lf` simuliert Linux. Schreibt nichts ins Hauptrepo. Der Scratchpad-Ordner ist mit der Session des Aufrufers geteilt: eigenen Ordnernamen wählen.
- Ein `git status` M bei leerem `git diff` ist eine Größenabweichung zwischen Index-Stat und Datei (`git ls-files -s --debug`, `size:`); git vergleicht dann keinen Inhalt. `git add` der Datei (Blob bleibt) oder `git restore` löst es, `git add --renormalize` ist bei LF-Blob ein No-op.
- `rnc2rng` ist lokal installiert (`python -m rnc2rng <rnc> <ziel>`), schreibt unter Windows CRLF, unter Linux LF.
