# Playground: Sucheingabe -> Ergebniskopf (#427, Review 2026-09-10)

Pfad eines Hash-Terms bis ins innerHTML:
router.js parseHash (split('&'), indexOf('='), decodeURIComponent) -> handleMultiLemmaRoute
(split(','), ids nur bei /^\d+$/ als Zeiger) -> MultiLemmaSearchUI.executeSearch
(resolveTerms nimmt Zeiger, Schreibform wird dann nie geprueft) -> tei-ui.js
displayCooccurrenceResults / displayMultiLemmaResults (Titel = searchTerms.join(' + '))
-> ui-helpers.js displaySummaryResults / displayHinweis.

Was sonst noch aus dem Hash in Markup kommt: `mode` ist in router.js:196 auf
Whitelist, `dist` geht durch parseInt (router.js:206, multi-lemma-search.js:243),
`q` fuellt nur input.value (router.js:269). `show` wird nur gelesen (triggerExpand).
Chips (multi-lemma-search.js:153) und Fehlermeldungen (299, 324, 326, 368) escapen
seit #audit-66 selbst.

Nicht aus dem Hash, aber roh: concept-explorer.js:165 `${searchTerm}` aus dem
Filterfeld im Begriffspanel (Selbst-XSS), lemma-explorer.js:943/955 `componentText`
aus Authority-Daten.

Naeheprobe ohne Browser: data/corpus-index.json.gz, texts[i].lemmata ist
{lemma_id: [positions]}; Treffer bei |pa - pb| <= dist. Gemessen 2026-09-10:
arm(286)+minne(4130) dist 10 = 2 Texte/3 Rohtreffer, arm(286)+arzaat(308) dist 1 = 0,
arm(286)+vriunt(7246) dist 1 = 1. lemma_308 ist arzaat, nicht vriunt (7246).

Einzelne Spec laufen lassen: `node scripts/run-tests.js testing/tests/<spec>`,
startet den http-server selbst, VERDICT-Zeile ist das Ergebnis (~30 s fuer 2 Tests
mit Korpusladen).

DESIGN.md:275 "Escape helpers: per module, not imported" steht unter dem
TEI-Analysis-Module-Pattern; escape.js selbst sagt, die Playground-Module halten
Kopien. 17 Dateien in playground/js haben einen eigenen escapeHtml.
