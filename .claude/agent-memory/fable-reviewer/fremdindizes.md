---
name: fremdindizes
description: Fremdindizes im Review: Naming-Index (#420, Nachbau, Blob-Hash, Lindas Repo, Zitationskopien, Term-Perspektive, Diakritika-Filter) und Pferde-Index (#193, zwei Vers-Einheiten, Zenodo)
metadata:
  type: project
---
Verdichtet 08.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

## Naming-Index (#420)

**Nachbau und Pin-Prüfung**
- `01-fetch-and-build-index.py` (PROJECT_ROOT = `parents[3]`, schreibt nach data/): Skript + `alias-overrides.json` nach `<scratch>/scripts/ingest/naming/`, `naming-explorer.js` nach `<scratch>/playground/js/ui/tei/` (Marker-Guard), `--ref <sha>`.
- Byte-Vergleich lokal wertlos (zlib-Version): Blob-Hash gegen `refs/pull/<N>/head`; nur er sagt bei einem Bot-PR, ob der Runner gebaut hat. Alt/neu-Index: Records als (sigle, figur, vers, json) flach diffen.

**Lindas Repo (lindabeutel/Naming-analysis):** Dateien per `raw.githubusercontent.com/.../<tag|sha>/data/<Werk>/analysis/figures_by_lemma_<lemma>_<scope>.json`; Committer-Datum per `git clone --depth 5` und `git log -1 --format=%cI` (generatedAt ist UTC). Zahl in einer Commit-Message gegen die JSON-Patches halten (`commits/<sha>`); der Patch zeigt das Versfeld nicht.

**Zitation** steht fest verdrahtet in contributors.xml (contrib_052), DATA-MODEL.md, FEATURES.md; kein Build liest sie. Bei Pin-Bump `git grep` nach alter Version, DOI und Kurzhash.

**Term-Perspektive nachrechnen:** Record einmal je Term (Set über eig/deck/ant/epi); `bez` = Term in eig|deck|ant, `epi` = Term in epi; `share` mit JS-Rundung (`math.floor(x + 0.5)`), Anteile summieren wegen Rundung nicht auf 100; bez + epi > mentions nur, wenn ein Term im SELBEN Record in beiden Gruppen steht. `naming-explorer.spec.js` fängt eine Mutation `BEZ_CATS = ['ant']` nicht.

**Beispiel-Lemmata in Beschreibungstexten gegen den Index halten** (#485): der Index führt Lindas Lemmaformen, nicht normalisierte Wörterbuch-Ansätze (`rîtaere` statt `rîter`). Messen über works[].figures[fig][].{eig,deck,ant,epi} (ganze Strings); ein Substring-Count trifft daneben `ph` (Versphrasen). Ein Wächter gegen „Term" im Spec braucht Substring-Semantik (`/Term(?!ini)/`); `/\bTerm\b/` ließ „12 Terme" durch.

**Diakritika-Filter (#525):** Lindas Lemmaformen tragen ë und í, die `normalizeMHG` nicht kennt; der Filter in `renderBody` ist `matchesNormalized || matchesFolded`, nur in Figuren- und Nenner-Perspektive. **Der `foldDiacritics`-Docstring (text-normalizer.js ~102, „nicht für MHG") hat einen Zwilling in `docs/CONTRACTS.md` §F („Where the fold may be used", Aufrufstellen-Liste mit Zahl)**; Runde 1 übersah ihn. Messen mit `matchesFolded\|foldDiacritics` über playground/js assets/js (am 06.10. sieben Dateien gegen „Four call sites" im Text). Verbotssätze in Docstrings haben in CONTRACTS.md meist einen Zwilling. „Strings mit ë" hat zwei Zählweisen (distinkte Terme vs. alle JSON-String-Blätter inkl. `ph`): Menge dazusagen.

## Pferde-Index (#193, Borek)

**„Verse" hat zwei Einheiten, die seit Quellversion 3695.2 auseinanderfallen.** `02-map-citations.py` zählt `verse=len(belege[werk])`, Boreks verschiedene Zitatnummern (335); verschiedene Sprungziele (`target`) im Index: 336, weil Er. 4118 und Er. 4718 auf `ER_471800` zeigen. Wer „346 auf N Versen" prüft, muss die Einheit nennen. Fall: DATA-MODEL sagte „eleven verses are cited by two horses each"; gemessen 10 von zwei Pferden und 1 (Pz. 340,29) zweimal dasselbe Pferd (Reimpaar, zwei Ziele).
- Messrezept: Index per `gzip` laden, `Counter((work, citation))` und `Counter(target)` getrennt zählen; Doppel nach Pferdemenge aufteilen.
- Datierte Altzahlen stehen bewusst in `ingest/horses/README.md` (Report vom 08.08.2026) und `scripts/ingest/horses/mapping.py` Kopf: nicht als Drift melden, aber als Nachbarschaft nennen. Harte Kopie der Abweichungszahl außerhalb des Explorers: `hilfe-playground.html` („neun der 346").
- Fremdindizes tragen verschiedene Schreibweisen: naming `source.license`, horses `source.licence`.
