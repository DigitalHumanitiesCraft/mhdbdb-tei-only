---
name: querschnitt-git
description: Git-Rezepte fürs Review: Altstand ohne stash, Basis prüfen, Rebase/Cherry-pick-Nullproben, Herkunft per log -S, Trailer, Blob-Hash, Squash und Stack, Dateiliste eines offenen oder gemergten PR, EOL-Probeklon
metadata:
  type: project
---
Verdichtet 18.10.2026.

**Altstand ohne den Arbeitsbaum anzufassen:** `git show <rev>:<pfad> > <scratch>/x` oder `git archive <rev> tei scripts | tar -x -C <scratch>`. Nie `git stash` im Baum des Aufrufers.

**Basis und Stand**
- `git rev-parse origin/main` gegen die Auftragsangabe; `git merge-base --is-ancestor <basis> origin/main` (exit 1 = gestackt); `git diff --name-only <basis> origin/main` gegen die Dateien des Branch.
- `git log origin/main..HEAD` am Anfang UND am Ende der Runde: der Aufrufer committet weiter. „Gepusht"? `git branch -r`. Ein im Auftrag genannter Stand kann ein Vor-Rebase-Stand sein, der im Repo nicht existiert (Code-Äquivalent per `range-diff`).

**Rebase / Cherry-pick**
- `git range-diff <altbasis>..<altkopf> <neubasis>..HEAD`: `=` identisch; `!` an JOURNAL/MEMORY-Commits sind meist nur fremde Kontextzeilen.
- Nullprobe: `git diff <alt> <neu> -- <dateien> | wc -l` = 0 (gleiche `--stat` reicht nicht). Konfliktmarker: `git grep -n -E '^(<<<<<<<|=======|>>>>>>>)' HEAD -- <dateien>`. Mergbarkeit vorab: `git merge-tree --write-tree --name-only origin/main HEAD`.

**Herkunft und Zuschreibung**
- „Seit #N kein Leser": `git log --oneline -S"<objekt>.<feld>" -- <pfade>`, Datum gegen das Issue. „Folgestellen korrigiert": `git log -S <phrase> origin/main..HEAD`. Erstes Auftauchen einer Datei: `git log --diff-filter=A`.
- Blob gleich Runner-Build: `git fetch origin refs/pull/<N>/head`, `git rev-parse FETCH_HEAD:<p> HEAD:<p>`.

**Squash (Repo-Konvention seit 21.09.2026)**
- `git log --no-merges | grep -c '(#N)$'` zählt Commits mit Issue-Bezug, keine Squash-Merges. Squash je Commit: `gh api repos/<org>/<repo>/pulls/N --jq .merge_commit_sha` gleich Commit-SHA; 404 = Issue.
- Stack nach Squash der Basis: `rebase --onto main <alter Basis-Head>` (alter Head: `gh pr view <basis> --json headRefOid`, auch nach MERGED); schlichtes `git rebase main` bricht.
- **Lokales Zusammenfassen auf neue Basis revertiert main still** (#554): ein Squash, dessen Baum aus dem alten Stand kommt, aber dessen Elternteil die neue `origin/main` ist, nimmt jeden zwischenzeitlichen main-Commit zurück. Probe `git diff --stat HEAD^ HEAD` (nicht `<alte Basis>...HEAD`) und `git diff --stat origin/main HEAD -- <Pfade außerhalb des Auftrags>`.
- **„Spurkopf inhaltsgleich mit Squash" per patch-id messen, nicht per `git diff <head> <squash>`** (#564): kam zwischen Abzweig und Squash ein anderer main-Commit, ist der Baumdiff nicht leer. Probe: `git diff <sq>^ <sq> | git patch-id --stable` gegen `git diff $(merge-base <head> <sq>^) <head> | git patch-id --stable`. Lokaler Kopf gleich `gh pr view N --json headRefOid` heißt gepusht, auch wenn der Remote-Zweig `[gone]` ist.
- **Dateiliste eines PR:** offen (auch CONFLICTING) `git diff --name-only origin/main...<branch>`; gemergt `git diff --name-only <sq>~1 <sq>` (`<sq>` aus `gh pr view N --json mergeCommit`), denn der Zweig ist meist gelöscht und die Drei-Punkte-Form bricht dann mit „unknown revision". Nie `--json files` (Kappung bei 100, siehe [[projekt-gates-und-ci]]).
- **`git log -- <pfade>` mit und ohne `--first-parent` an einem `--no-ff`-Merge** (20.10.2026, Git 2.56, Probe-Repo im Scratchpad): ohne Flag erscheinen die Zweig-Commits und der Merge NICHT (TREESAME zum zweiten Elternteil), mit Flag nur der Merge. Wer eine Pfadzählung auf `--first-parent` umstellt, misst das so in 10 Zeilen nach, statt es zu glauben. Journal-Verdichtung prüfen: je entfernter `## `-Abschnitt der Basis als Teilstring im neuen Archiv (Python, `git show <rev>:<pfad>`), Zahlen der Trace-Absätze gegen die Einträge desselben Datums.

**EOL- und Attribut-Proben ohne den Arbeitsbaum**
- Probeklon im Scratchpad: `git clone --shared --no-checkout --branch main <repo> <scratch>/<eigener Name>`, dann `sparse-checkout set --no-cone .gitattributes <datei>` **ohne führenden Slash** (Git Bash macht aus `/.gitattributes` einen Pfad unter `C:/Program Files/Git/`) und `sparse-checkout reapply`. `config core.autocrlf false` + `core.eol lf` simuliert Linux.
