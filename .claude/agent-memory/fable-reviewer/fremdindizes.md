---
name: fremdindizes
description: Fremdindizes im Review: Naming-Index (#420, Nachbau, Blob-Hash, Lindas Repo, Zitationskopien, Term-Perspektive) und Pferde-Index (#193, zwei Vers-Einheiten, Zenodo)
metadata:
  type: project
---
Verdichtet 02.10.2026 aus naming_420 und projekt_pferde_193. Zahlen sind Eingabe, vor Gebrauch nachmessen.

## Naming-Index (#420)

**Nachbau und Pin-Prüfung**
- `01-fetch-and-build-index.py` (PROJECT_ROOT = `parents[3]`, schreibt nach data/): Skript + `alias-overrides.json` nach `<scratch>/scripts/ingest/naming/`, `naming-explorer.js` nach `<scratch>/playground/js/ui/tei/` (Marker-Guard), `--ref <sha>`.
- Byte-Vergleich lokal wertlos (zlib-Version): Blob-Hash gegen `refs/pull/<N>/head`; nur er sagt bei einem Bot-PR (Committer github-actions[bot], nach lokalem Rebase eigener Committer), ob der Runner gebaut hat.
- Alt/neu-Index: `git show <basis>:data/naming-index.json.gz > temp/...` (relativ), Records als (sigle, figur, vers, json) flach diffen.

**Lindas Repo (lindabeutel/Naming-analysis)**
- Dateien per `raw.githubusercontent.com/.../<tag|sha>/data/<Werk>/analysis/figures_by_lemma_<lemma>_<scope>.json` und `categorization_<Werk>.json`. Committer-Datum: `git clone --depth 5` ins Scratch, `git log -1 --format=%cI` (generatedAt in UTC).
- Zahl in einer Commit-Message gegen die JSON-Patches halten (`commits/<sha>`; xlsx nur `changes: 0`); der Patch zeigt das Versfeld nicht.

**Zitation** steht fest verdrahtet in contributors.xml (contrib_052), DATA-MODEL.md, FEATURES.md; kein Build liest sie. Bei Pin-Bump `git grep` nach alter Version, DOI und Kurzhash. Concept vs. Version per zenodo `conceptdoi`.

**Term-Perspektive nachrechnen:** Record einmal je Term (Set über eig/deck/ant/epi); `bez` = Term in eig|deck|ant, `epi` = Term in epi; `share` mit JS-Rundung (`math.floor(x + 0.5)`), Anteile summieren wegen Rundung nicht auf 100; bez + epi > mentions nur, wenn ein Term im SELBEN Record in beiden Gruppen steht. `naming-explorer.spec.js` fängt eine Mutation `BEZ_CATS = ['ant']` nicht.

**Beispiel-Lemmata in Beschreibungstexten gegen den Index halten** (#485): der Index führt Lindas Lemmaformen, nicht normalisierte Wörterbuch-Ansätze (`rîtaere` statt `rîter`, `künic` statt `künec`, `Paris` statt `Pârîs`). Messen: Index entpacken, über works[].figures[fig][].{eig,deck,ant,epi} greppen (Listenwerte, ganze Strings); ein Substring-Count trifft daneben `ph` (Versphrasen: „künec" 0 als JSON-String, 60 als Substring). `ant`-Werte tragen keinen Artikel; die Maske zeigt `e.term`. Ein Wächter gegen „Term" im Spec muss die Substring-Semantik (`/Term(?!ini)/`) haben; `/\bTerm\b/` ließ „12 Terme" durch.

## Pferde-Index (#193, Borek)

**„Verse" hat zwei Einheiten, die seit Quellversion 3695.2 (02.10.2026) auseinanderfallen.** `02-map-citations.py` zählt `verse=len(belege[werk])`, Boreks verschiedene Zitatnummern (335); verschiedene Sprungziele (`target`) im Index: 336, weil Er. 4118 und Er. 4718 auf `ER_471800` zeigen. Wer „346 auf N Versen" prüft, muss die Einheit nennen. Fall: DATA-MODEL sagte „eleven verses are cited by two horses each"; gemessen 10 von zwei Pferden und 1 (Pz. 340,29) zweimal dasselbe Pferd (Reimpaar, zwei Ziele).
- Messrezept: Index per `gzip` laden, `Counter((work, citation))` und `Counter(target)` getrennt zählen; Doppel nach Pferdemenge aufteilen.
- Datierte Altzahlen stehen bewusst in `ingest/horses/README.md` (Report vom 08.08.2026, je Vers: 328 von 336) und `scripts/ingest/horses/mapping.py` Kopf (337/6/3): nicht als Drift melden, aber als Nachbarschaft nennen. Harte Kopie der Abweichungszahl außerhalb des Explorers: `hilfe-playground.html` („neun der 346"); der Explorer zählt seit 02.10. aus dem Index.
- Zenodo-Versionen: `https://zenodo.org/api/records?q=conceptrecid:20627656&all_versions=true`. Erstes Auftauchen einer Datei auf main: `git log --diff-filter=A`.
- Fremdindizes tragen verschiedene Schreibweisen: naming `source.license`, horses `source.licence`.
