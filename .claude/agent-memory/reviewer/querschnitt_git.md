---
name: querschnitt-git
description: Git-Rezepte fürs Review ohne den Working Tree anzufassen
metadata:
  type: project
---
**Altstand ohne den Working Tree:** `git show <rev>:<pfad> > <scratch>/x` oder `git archive <rev> tei scripts | tar -x -C <scratch>`. Nie `git stash` im Baum des Callers.

**Basis und Stand**
- `git rev-parse origin/main` gegen den Prompt, `git merge-base --is-ancestor <basis> origin/main` (Exit 1 = gestackt), `git diff --name-only <basis> origin/main` gegen die Dateien des Branch. Die Basis im Prompt kann die Merge-Base sein, während origin/main weiterrückt: `git merge-tree --write-tree --name-only origin/main HEAD`.
- `git log origin/main..HEAD` am Anfang UND am Ende der Runde. „Gepusht"? `git branch -r`. Ein Stand im Prompt kann ein Vor-Rebase-Stand sein (Code-Äquivalent per `range-diff`).
- `git range-diff <altbasis>..<altkopf> <neubasis>..HEAD`: `!` an JOURNAL- oder MEMORY-Commits sind meist fremde Kontextzeilen. Nullprobe `git diff <alt> <neu> -- <dateien> | wc -l` = 0. Konfliktmarker per `git grep -n -E '^(<<<<<<<|=======|>>>>>>>)'`.
- Relative Revisionen in einer Behauptung („HEAD~1 (vor X)") sind seit ihrer Messung womöglich weitergerückt: `git diff --stat <rev> HEAD -- <datei>` zeigt, ob die Revision die Datei überhaupt anders hat.

**Gitignorierte Nutzlast im Prüfgegenstand** (lokale Fremdquelle unter `sources/`): `stash create`, `status` und `ls-files --others --exclude-standard` sehen sie nicht, die Pinning-ID hält sie also nicht fest. Am Anfang und Ende selbst hashen (`sha256sum`), dazu `git check-ignore -v` und `git ls-files <ordner>` (leer = nichts versehentlich getrackt).

**Herkunft:** „Seit #N kein Leser": `git log --oneline -S"<objekt>.<feld>" -- <pfade>`. „Folgestellen korrigiert": `git log -S <phrase> origin/main..HEAD`. Blob gleich Runner-Build: `git fetch origin refs/pull/<N>/head`, `git rev-parse FETCH_HEAD:<p> HEAD:<p>`.

**Squash (Repo-Konvention)**
- `(#N)$` im Betreff trennt keine Squash-Merges von Commits mit Issue-Bezug: **Squash-Merges trennt der Committer** (`git log origin/main --format=%ce` = `noreply@github.com`), Gegenprobe der Nummer per `gh api repos/<o>/<r>/issues/N --jq .pull_request`. Stack nach Squash der Basis: `rebase --onto main <alter Basis-Head>` (`gh pr view <basis> --json headRefOid`).
- Lokales Zusammenfassen auf neue Basis revertiert main still: `git diff --stat HEAD^ HEAD` und `git diff --stat origin/main HEAD -- <Pfade außerhalb des Prompts>`.
- „Branch-Kopf inhaltsgleich mit Squash" per `git patch-id --stable` beider Diffs messen, nicht per Baumdiff. Lokaler Kopf gleich `headRefOid` heißt gepusht, auch bei `[gone]`.
- Eine Zahl aus einem Squash-Betreff zählt keine Commits: Branch-Kopf holen (`gh pr view N --json headRefOid,commits`), `git rev-list --count <marker>..<kopf> -- <pfade>`.
- Dateiliste eines PR: Rezept in CLAUDE.md (Git Rules), nie `--json files`.
- **Eine Regel, die einen Vermerk per `git log --grep` auf `main` wiederfinden will, trägt nur über die Squash-Message:** Branch-Commits erreichen `main` nie. Sagt die Regel, dass der Mergende die Zeile übernimmt, und zwar für jede Vermerkzeile einzeln (Schuld- und `nachgeholt:`-Zeile)?
- **Nachzug der `.claude/agents/`-Kopie aus claude-code-setup:** Blob-Kette schließen, nicht nur das Ziel: `git rev-parse origin/main:.claude/agents/<f>` gleich `<alter stand>:agents/<f>` der Sammlung, HEAD-Blob gleich `<neuer stand>:agents/<f>`, dazu `merge-base --is-ancestor` und `git log <alt>..<neu> -- agents/` gegen die README-Aufzählung. Git Bash macht aus `origin/main:.claude/x` eine Windows-Pfadliste (`origin\main;...`), und `MSYS_NO_PATHCONV=1` bricht dann `-C /c/...`: stattdessen `git ls-tree origin/main .claude/agents/` (25.11.2026, #727).
- **Message eines einzelnen Commits: `git show -s --format=%B <sha>`**, nie `git log origin/main -1 <sha>`: zwei Revisionen sind eine Vereinigung, `-1` zeigt den main-Kopf. `git log --grep` mit Umlaut trägt in Git Bash.

**`git log -- <pfade>` an einem `--no-ff`-Merge:** ohne `--first-parent` erscheinen die Branch-Commits, der Merge nicht (TREESAME zum zweiten Elternteil), mit Flag nur der Merge. Eine umgestellte Pfadzählung im Probe-Repo nachmessen.

**EOL-Probeklon:** `git clone --shared --no-checkout --branch main <repo> <scratch>/<name>`, `sparse-checkout set --no-cone .gitattributes <datei>` **ohne führenden Slash** (Git Bash macht daraus einen Pfad unter `C:/Program Files/Git/`), `sparse-checkout reapply`. `core.autocrlf false` plus `core.eol lf` simuliert Linux.
