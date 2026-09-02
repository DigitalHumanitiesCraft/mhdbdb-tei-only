---
name: rebase-review-data-prs
description: Was bei einem rebasten Daten-PR nachzumessen ist (Versionskollision, Commit-Messages nach --ours, Verlustpruefung auf JSON-Ebene); Vorfall PR #381 am 2026-09-02
metadata:
  type: project
---

Ein Daten-PR, der nach einem Rebase auf main mit `git checkout --ours` fuer die
generierten Dateien aufgeloest wurde, hat drei typische Stellen, an denen etwas
kippt, und keine davon findet ein Diff `main...HEAD` allein.

1. **Versionskollision.** PR #381 und main hatten beide Corpus-Index 4.2.7
   vergeben (PR fuer Titel, main fuer #235 Breve-Welle 4). PR-Bodies tragen
   Reservierungen unter "Koordination" ("4.2.8 ist an #370 vergeben"), die einen
   Rebase nicht ueberleben. Messen statt glauben: `git for-each-ref` ueber
   refs/heads und refs/remotes/origin, je Ref `git show <ref>:assets/js/lib/corpus-loader.js`
   und `INDEX_VERSION` auslesen. Am 2026-09-02 lag 4.2.8 nur auf dem PR-Zweig.
2. **Commit-Message des rebasten Originalcommits.** Sie bleibt zeichengleich,
   beschreibt aber Bump, gz-Neubau und API-Dateien, die nach `--ours` in
   Folgecommits gewandert sind. `git show --stat <sha>` gegen die Message halten.
3. **Verlustpruefung.** Am billigsten auf JSON-Ebene: gz von main und HEAD
   dekomprimieren, Top-Level-Keys und `texts` je Sigle vergleichen. Identischer
   `lemmaIndex` heisst: die Annotationen von main sind im Neubau drin.
   Fuer die TEI: `git diff --stat <orig-commit> HEAD -- tei/` darf nur zeigen,
   was main seither selbst geaendert hat.

**Why:** Der Aufrufer hatte alle sechs Konflikte mit `--ours` geloest und
selbst gefragt, ob dabei PR-Inhalt verloren ging; Punkt 3 hat das in einer
Messung beantwortet, Punkt 2 war der einzige Befund.

**How to apply:** Bei jedem Review, dessen Auftrag "rebased" oder
"Konflikte aufgeloest" enthaelt, diese drei Messungen vor allem anderen.
Verwandt: [[concepts-graph-pitfalls]] fuer Zaehlfallen in Authority-Daten.
