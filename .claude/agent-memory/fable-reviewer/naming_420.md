---
name: naming-420
description: Naming-Index und Term-Perspektive (#420): Nachbau ohne Repo-Schreiben, Blob-Hash statt Byte-Vergleich, Lindas Referenzdaten, Zitationskopien, Nachrechnen mit JS-Rundung
metadata:
  type: project
---
Stand 28.09.2026.

**Nachbau und Pin-Pruefung**
- `01-fetch-and-build-index.py` (PROJECT_ROOT = `parents[3]`, schreibt nach data/): Skript + `alias-overrides.json` nach `<scratch>/scripts/ingest/naming/`, `naming-explorer.js` nach `<scratch>/playground/js/ui/tei/` (Marker-Guard liest es), `--ref <sha>`.
- Byte-Vergleich lokal wertlos (zlib-Version): Blob-Hash gegen `refs/pull/<N>/head`. Der Wochenworkflow vergleicht Bytes auf dem Runner.
- Bot-PR (peter-evans/create-pull-request): Autor = Ausloeser, Committer github-actions[bot]; nach lokalem Rebase eigener Committer. Nur der Blob-Hash sagt, ob der Runner gebaut hat.
- Alt/neu-Index: `git show <basis>:data/naming-index.json.gz > temp/...` (relativ), Records als (sigle, figur, vers, json) flach diffen.

**Lindas Repo (lindabeutel/Naming-analysis)**
- `raw.githubusercontent.com/.../<tag|sha>/data/<Werk>/analysis/figures_by_lemma_<lemma>_<scope>.json` und `.../categorization_<Werk>.json`.
- Committer-Datum: `git clone --depth 5` ins Scratch, `git log -1 --format=%cI` (generatedAt in UTC).
- Zahl in einer Commit-Message gegen die JSON-Patches halten (`commits/<sha>`; xlsx nur `changes: 0`). Der Patch zeigt das Versfeld nicht: Zeile per raw alt/neu suchen.

**Zitation** steht fest verdrahtet in contributors.xml (contrib_052), DATA-MODEL.md, FEATURES.md; kein Build liest sie. Bei Pin-Bump `git grep` nach alter Version, DOI und Kurzhash. Concept vs. Version per zenodo `conceptdoi`.

**Term-Perspektive nachrechnen**
- Record einmal je Term (Set ueber eig/deck/ant/epi); `bez` = Term in eig|deck|ant, `epi` = Term in epi.
- `share` mit JS-Rundung (`math.floor(x + 0.5)`); Pythons `round()` ergibt andere Summen. Anteile summieren wegen Rundung nicht auf 100.
- bez + epi > mentions nur, wenn ein Term im SELBEN Record in beiden Gruppen steht (selten).
- `naming-explorer.spec.js` faengt eine Mutation `BEZ_CATS = ['ant']` nicht.
- Montags-Schedule des Workflows war am 07., 14. und 21.09. rot.
