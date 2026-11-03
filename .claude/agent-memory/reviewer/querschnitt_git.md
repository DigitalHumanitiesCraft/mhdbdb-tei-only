---
name: querschnitt-git
description: Git-Rezepte fürs Review: Altstand ohne stash, Basis prüfen, Rebase-Nullproben, Herkunft per log -S, Squash und Stack, Dateiliste eines PR, first-parent, EOL-Probeklon
metadata:
  type: project
---
Verdichtet 03.11.2026.

**Altstand ohne den Arbeitsbaum:** `git show <rev>:<pfad> > <scratch>/x` oder `git archive <rev> tei scripts | tar -x -C <scratch>`. Nie `git stash` im Baum des Aufrufers.

**Basis und Stand**
- `git rev-parse origin/main` gegen den Auftrag, `git merge-base --is-ancestor <basis> origin/main` (Exit 1 = gestackt), `git diff --name-only <basis> origin/main` gegen die Dateien des Branch.
- `git log origin/main..HEAD` am Anfang UND am Ende der Runde. „Gepusht"? `git branch -r`. Ein Stand im Auftrag kann ein Vor-Rebase-Stand sein (Code-Äquivalent per `range-diff`).
- `git range-diff <altbasis>..<altkopf> <neubasis>..HEAD`: `!` an JOURNAL- oder MEMORY-Commits sind meist fremde Kontextzeilen. Nullprobe `git diff <alt> <neu> -- <dateien> | wc -l` = 0. Konfliktmarker per `git grep -n -E '^(<<<<<<<|=======|>>>>>>>)'`. Mergbarkeit: `git merge-tree --write-tree --name-only origin/main HEAD`.

**Herkunft:** „Seit #N kein Leser": `git log --oneline -S"<objekt>.<feld>" -- <pfade>`. „Folgestellen korrigiert": `git log -S <phrase> origin/main..HEAD`. Blob gleich Runner-Build: `git fetch origin refs/pull/<N>/head`, `git rev-parse FETCH_HEAD:<p> HEAD:<p>`.

**Squash (Repo-Konvention)**
- `grep -c '(#N)$'` über `git log --no-merges` zählt Commits mit Issue-Bezug, keine Squash-Merges. Stack nach Squash der Basis: `rebase --onto main <alter Basis-Head>` (`gh pr view <basis> --json headRefOid`).
- **Lokales Zusammenfassen auf neue Basis revertiert main still:** Probe `git diff --stat HEAD^ HEAD` und `git diff --stat origin/main HEAD -- <Pfade außerhalb des Auftrags>`.
- „Spurkopf inhaltsgleich mit Squash" per `git patch-id --stable` beider Diffs messen, nicht per Baumdiff. Lokaler Kopf gleich `headRefOid` heißt gepusht, auch bei `[gone]`.
- **Dateiliste eines PR:** offen `git diff --name-only origin/main...<branch>`, gemergt `git diff --name-only <sq>~1 <sq>` (`gh pr view N --json mergeCommit`). Nie `--json files` (kappt bei 100).
- Eine Zahl aus einem Squash-Betreff zählt keine Commits: Zweigkopf holen (`gh pr view N --json headRefOid,commits`), `git rev-list --count <marker>..<kopf> -- <pfade>`.

**`git log -- <pfade>` an einem `--no-ff`-Merge:** ohne `--first-parent` erscheinen die Zweig-Commits, der Merge nicht (TREESAME zum zweiten Elternteil), mit Flag nur der Merge. Eine umgestellte Pfadzählung im Probe-Repo nachmessen.

**EOL-Probeklon:** `git clone --shared --no-checkout --branch main <repo> <scratch>/<name>`, `sparse-checkout set --no-cone .gitattributes <datei>` **ohne führenden Slash** (Git Bash macht daraus einen Pfad unter `C:/Program Files/Git/`), `sparse-checkout reapply`. `core.autocrlf false` plus `core.eol lf` simuliert Linux.
