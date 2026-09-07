---
name: naming-index-pin-review
description: Wie ein Pin-Bump oder Rebuild von data/naming-index.json.gz ohne Schreiben ins Repo nachgemessen wird (Scratchpad-Kopie des Build-Skripts, Blob-Hash gegen den PR-Ref, flacher Klon von Lindas Repo fuer Committer-Datum und Quell-Diff); zlib-Falle beim Byte-Vergleich. Gemessen 07.09.2026, Zweig claude/agents-setup-network-check-08f1ri
metadata:
  type: project
---

**Nachbau ohne Schreiben in den Arbeitsbaum:** `01-fetch-and-build-index.py` leitet `PROJECT_ROOT` aus `parents[3]` ab und schreibt nach `data/`. Skript + `alias-overrides.json` nach `<scratch>/scripts/ingest/naming/` und `naming-explorer.js` nach `<scratch>/playground/js/ui/tei/` kopieren (der Marker-Guard liest das JS), dann `python3 <scratch>/scripts/ingest/naming/01-fetch-and-build-index.py --ref <sha>`. `raw.githubusercontent.com` geht in Python, `api.github.com` bekommt vom Sandbox-Proxy 403 (auch per curl), also `resolve_commit` scheitert best-effort: generatedAt = Build-Zeit, kein `source.commit`. `works` und `version` sind trotzdem voll vergleichbar.

**Byte-Vergleich ist lokal wertlos:** identischer JSON-Text (794.537 Zeichen), aber gzip mit lokalem zlib 1.3 ergibt 112.681 Bytes gegen 112.699 im Runner-Build. Der Wochen-Workflow vergleicht Bytes auf dem Runner, deshalb muss die committete Datei vom Runner stammen. Pruefen: `git fetch origin refs/pull/<N>/head` und `git rev-parse FETCH_HEAD:data/naming-index.json.gz HEAD:data/naming-index.json.gz` (Blob-Hash gleich = Runner-Bytes).

**Committer-Datum und Quell-Diff:** `git clone --depth 5 https://github.com/lindabeutel/Naming-analysis.git` ins Scratchpad, `git log -1 --format=%cI` (generatedAt muss dem entsprechen, in UTC) und `git diff --stat <alt> <neu>` plus `git diff --quiet ... -- data/`.

**peter-evans/create-pull-request** setzt bei `workflow_dispatch` den Autor auf den Ausloeser (`chsteiner <28706050+chsteiner@users.noreply.github.com>`), Committer `github-actions[bot]`. Wer den PR-Commit lokal nachzieht (Rebase/Cherry-Pick), bekommt seinen eigenen Committer; der Autor bleibt. Aus dem Autor-Feld allein ist also nicht zu lesen, ob der Bot gebaut hat, nur aus dem Blob-Hash.

**Festverdrahtete Zitation ausserhalb des Skripts (Stand 07.09.2026):** `authority-files/contributors.xml` (contrib_052, undatierte Note mit DOI und Version), `docs/DATA-MODEL.md` und `docs/FEATURES.md` (beide datiert "as of 2026-08-14"). Keine davon wird von einem Build gelesen (authority-index enthaelt weder DOI noch Version). Frontend und Tests lesen `source` aus dem Index (`INDEX_QUELLE` im Spec).

**Why:** Der Aufrufer hatte selbst gemessen und nur `pruefe_zitation` als Konsument gefunden; die Note in contributors.xml stand nicht auf seiner Liste, weil sie weder Pruefung noch Schreiber ist, sondern eine dritte Kopie.

**How to apply:** Bei jedem Diff an `QUELL_VERSION`/`QUELL_DOI` oder `data/naming-index.json.gz`: `git grep` nach alter Version, alter DOI und altem Commit-Kurzhash ueber das ganze Repo, Blob-Hash gegen den PR-Ref, Nachbau im Scratchpad. Verwandt: [[rebase-review-data-prs]].
