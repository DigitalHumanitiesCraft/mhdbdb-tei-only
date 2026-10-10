---
name: querschnitt-git
description: Git-Rezepte fürs Review: Altstand ohne stash, Basis prüfen, Rebase/Cherry-pick-Nullproben, Herkunft per log -S, Trailer, Blob-Hash, Squash und Stack, EOL-Probeklon
metadata:
  type: project
---
Verdichtet 08.10.2026.

**Altstand ohne den Arbeitsbaum anzufassen:** `git show <rev>:<pfad> > <scratch>/x` oder `git archive <rev> tei scripts | tar -x -C <scratch>`. Nie `git stash` im Baum des Aufrufers. Skripte, die `git show origin/main` und `HEAD` statt fester SHAs lesen, laufen in Folgerunden unverändert.

**Basis und Stand**
- `git rev-parse origin/main` gegen die Auftragsangabe; `git merge-base --is-ancestor <basis> origin/main` (exit 1 = gestackt); `git diff --name-only <basis> origin/main` gegen die Dateien des Branch.
- `git log origin/main..HEAD` am Anfang UND am Ende der Runde: der Aufrufer committet weiter. „Gepusht"? `git branch -r`. Commit-Datum aus `git show -s --format=%ci`. Ein im Auftrag genannter Stand kann ein Vor-Rebase-Stand sein, der im Repo nicht existiert (Code-Äquivalent per `range-diff` suchen).

**Rebase / Cherry-pick**
- `git range-diff <altbasis>..<altkopf> <neubasis>..HEAD`: `=` identisch; `!` an JOURNAL/MEMORY-Commits sind meist nur fremde Kontextzeilen.
- Nullprobe: `git diff <alt> <neu> -- <dateien> | wc -l` = 0 (gleiche `--stat` reicht nicht). Konfliktmarker: `git grep -n -E '^(<<<<<<<|=======|>>>>>>>)' HEAD -- <dateien>`. Mergbarkeit vorab: `git merge-tree --write-tree --name-only origin/main HEAD`.
- Daten-PR nach Rebase mit `--ours`: Versionskollision über alle Refs prüfen (je Ref `INDEX_VERSION` aus `git show <ref>:assets/js/lib/corpus-loader.js`; Reservierungen im PR-Body überleben keinen Rebase), Commit-Message gegen `git show --stat <sha>`, Verlust auf JSON-Ebene.

**Herkunft und Zuschreibung**
- „Seit #N kein Leser": `git log --oneline -S"<objekt>.<feld>" -- <pfade>`, Datum gegen das Issue. „Folgestellen korrigiert": `git log -S <phrase> origin/main..HEAD`. Erstes Auftauchen einer Datei: `git log --diff-filter=A`.
- Trailer: `git log --format='%h %(trailers:key=Co-Authored-By,valueonly)'`. Zeilenzitate `datei:N` per `git show <ref>:<pfad> | grep -n` prüfen.
- Blob gleich Runner-Build: `git fetch origin refs/pull/<N>/head`, `git rev-parse FETCH_HEAD:<p> HEAD:<p>`.
- Diff-Zeilenarten zählen: `git diff base...HEAD -- tei/ | grep '^+' | sed 's/xml:id="[^"]*"//g; s/when="[^"]*"//g' | sort | uniq -c`.

**Squash (Repo-Konvention seit 21.09.2026)**
- `git log --no-merges | grep -c '(#N)$'` zählt Commits mit Issue-Bezug, keine Squash-Merges. Squash je Commit: `gh api repos/<org>/<repo>/pulls/N --jq .merge_commit_sha` gleich Commit-SHA; 404 = Issue.
- Stack nach Squash der Basis: `rebase --onto main <alter Basis-Head>` (alter Head: `gh pr view <basis> --json headRefOid`, auch nach MERGED); schlichtes `git rebase main` bricht. GitHub meldet den dep-PR nur CONFLICTING, wenn er dieselben Zeilen berührt.
- **Lokales Zusammenfassen auf neue Basis revertiert main still** (10.10.2026, #554): ein Squash, dessen Baum aus dem alten Stand kommt („Baum identisch mit Commit X"), aber dessen Elternteil die neue `origin/main` ist, nimmt jeden zwischenzeitlichen main-Commit zurück. Probe immer `git diff --stat HEAD^ HEAD` (nicht `<alte Basis>...HEAD`, das blendet es aus) und `git diff --stat origin/main HEAD -- <Pfade außerhalb des Auftrags>`.
- Kein gesquashter Head ist Vorfahr von main: `branch --merged` listet ihn nicht, `branch -d` verweigert, nur `-D`. Jede Anweisung „gemergte Branches löschen" oder Guard auf `--merged` mitlesen. Beim Auto-Delete (`delete_branch_on_merge`) retargetet GitHub abhängige PRs selbst.

**EOL- und Attribut-Proben ohne den Arbeitsbaum**
- Probeklon im Scratchpad: `git clone --shared --no-checkout --branch main <repo> <scratch>/eolprobe`, dann `git -C ... sparse-checkout set --no-cone .gitattributes <datei>` **ohne führenden Slash** (Git Bash macht aus `/.gitattributes` den Pfad `C:/Program Files/Git/.gitattributes`) und `sparse-checkout reapply`. Erbt `core.autocrlf` aus der System-Config; `config core.autocrlf false` + `core.eol lf` simuliert Linux. Der Scratchpad-Ordner ist mit der Session des Aufrufers geteilt: eigenen Ordnernamen wählen.
- Ein `git status` M bei leerem `git diff` ist eine Größenabweichung zwischen Index-Stat und Datei (`git ls-files -s --debug`, `size:`); git vergleicht dann keinen Inhalt. `git add` der Datei (Blob bleibt) oder `git restore` löst es, `git add --renormalize` ist bei LF-Blob ein No-op. `git ls-files --eol <datei>` zeigt, was im Baum liegt.
- `rnc2rng` ist lokal installiert (`python -m rnc2rng <rnc> <ziel>`), schreibt unter Windows CRLF, unter Linux LF.
