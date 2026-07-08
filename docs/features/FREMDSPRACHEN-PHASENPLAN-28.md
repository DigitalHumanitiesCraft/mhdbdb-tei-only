# Fremdsprachen-Annotation: Daten-Phasenplan (#28)

Temporal Artifact zu Issue #28 (Suche nach fremdsprachigen Passagen). Grundlage: KZW-Freigabe vom 29.05. für den Weg „LLM + Begriffssystem `concept_23123000` + externe Wörterbücher", der Audit-Befund „0 Token-Annotationen im Korpus" und Julias Bestätigung, dass auch WZB kein `xml:lang` auf Token-Ebene trägt. Nach Umsetzung: Kernwissen in DATA-MODEL/TEI-MODEL/CONTRACTS überführen, Datei löschen (CLAUDE.md → Temporal Artifacts).

## Ausgangslage (verifiziert)

- 0 `<w xml:lang>`, 0 `@foreign`, 0 `<foreign>`-Wrapper im gesamten Korpus (Body-Ebene); `xml:lang` existiert nur in Header-Metadaten.
- Schema: `<w>` erlaubt `@xml:lang` BEREITS (mhdbdb.rnc, w-Definition) — Phase 3 braucht dafür keine Schema-Änderung. `@foreign` ist NICHT im Schema; da `xml:lang` die Information vollständig trägt, wird `@foreign` nicht eingeführt (Entscheidungspunkt, Empfehlung: weglassen).
- Die `<etym>`-Komponenten in lexicon.xml lösen intern auf (alle Komponenten sind selbst MHD-Lemmata) — daraus ist Fremdsprachlichkeit NICHT ableitbar (Befund 28.05.).
- Zielsprachen laut KZW: gmh (Default), la, fr, ar, he, grc, it, es, en, yi, x-rotw.

## Grundsatzentscheidung: Lemma-Ebene führt

Annotiert wird primär in `lexicon.xml` (`@xml:lang` am `<entry>` bzw. an der Lemma-Form), NICHT direkt an Millionen Token. Token-Annotation wird dann deterministisch über `@lemmaRef` abgeleitet. Vorteile: 43.879 Entscheidungen statt 7,5 Mio. (7.533.447 annotierte Tokens, Corpus-Index v4.1.5); Kuratierbarkeit; eine Quelle der Wahrheit; der Data-Change-Lifecycle bleibt beherrschbar. Token-AUSNAHMEN (ein im Kontext lateinisches Zitat eines sonst-mhd Lemmas) bleiben als manuelle Overrides möglich (direktes `<w xml:lang>`), werden aber nicht systematisch erzeugt.

Kein Widerspruch zu CONTRACTS §F.1 („Corpus Leads, Authority Follows"): §F regelt, dass Lemma-Existenz und -Zählung aus dem Korpusbestand abgeleitet werden und `lexicon.xml` dabei Index ist. Die Sprachzuordnung ist dagegen eine NEUE, eigenständig kuratierte Eigenschaft, die im Korpus nirgends vorhanden ist (0 Token-Annotationen) — `lexicon.xml` ist dafür die Erfassungsoberfläche. Das ist eine bewusste, auf dieses Feature begrenzte Festlegung, keine Änderung der generellen Authority-Source-Regel.

## Phase 0: Zielformat + Policy (S)

- `@xml:lang`-Werte-Set fixieren (BCP-47: la, fr, ar, he, grc, it, es, en, yi, x-rotw; gmh bleibt impliziter Default und wird NICHT ausgezeichnet).
- Festlegen: Lehnwort-vs.-Fremdwort-Grenze (z. B. „blêmensier" = integriertes Lehnwort → fr markieren? Empfehlung: ja, mit Konfidenz-Feld; KZW entscheidet die Grenzziehung an ~20 Beispielfällen).
- lexicon.xml-Kodierung: `<form type="lemma"><orth xml:lang="fr">…` vs. `@xml:lang` am `<entry>` — Schema-Check + TEI-MODEL-AUTH-FILES-Eintrag.
- Deliverable: 1-Seiten-Policy als Ergänzung in TEI-MODEL-AUTH-FILES.md.

## Phase 1: Kandidaten-Generierung (M, dreigleisig, unabhängig parallelisierbar)

1. **Begriffssystem:** Lemmata, deren senses auf den `concept_23123000`-Subtree zeigen (Einzelsprachen) — Achtung: das sind Lemmata, die Sprachen BEZEICHNEN (latîn, kriechisch), plus laut KZW viel bereits Abgedecktes; Liste extrahieren, als Kandidaten-Quelle A mit eigener Herkunfts-Markierung.
2. **LLM-Klassifikation:** Batch über alle 43.879 Lemmata (Form + Bedeutungen/Konzepte als Kontext): „Lehnwort/Fremdwort? Quellsprache? Konfidenz?" Output als CSV mit (lemma_id, lang, confidence, Begründung). Modell-Doppellauf (2 Modelle oder 2 Prompts) für Konfidenz-Kalibrierung.
3. **Wörterbuch-Crawl:** Lexer/MWB via Wörterbuchnetz-API (Pattern #73): Etymologie-Abschnitte nach Sprach-Markern (mlat., afrz., hebr., …) parsen; Treffer als Quelle C.

## Phase 2: Kuratierung (M, Mensch im Loop)

- Merge der 3 Quellen: Übereinstimmung 2+ Quellen → Auto-Accept-Kandidat; nur-LLM mit hoher Konfidenz → Stichprobe; Konflikte → Review-Liste.
- Review-Paket für KZW/Linda: sortierte Tabelle mit Beleg-Kontexten (KWIC aus dem Korpus), geschätzt einige hundert Grenzfälle.
- Abnahme-Kriterium definieren (z. B. Stichproben-Präzision ≥ 95 % pro Sprache).

## Phase 3: Anwendung (M)

- lexicon.xml: `xml:lang` an akzeptierte Lemmata (Skript, deterministisch, mit Provenienz-Log unter `ingest/foreign-lang/`).
- Token-Ableitung: build-corpus-index erweitert um `foreignTokens[]` pro Text (position, lang) via lemmaRef-Lookup — KEINE Massen-Edits an `tei/*.xml` nötig. (Entscheidungspunkt: Token-`@xml:lang` zusätzlich physisch ins TEI schreiben? Empfehlung: nein, die Index-Ableitung genügt fürs Feature; TEI-Schreibung nur, wenn FAIR/Export es verlangt — dann eigener Bulk-Lauf mit Schema-Validierung.)
- Data-Change-Lifecycle: Authority-Index-Bump (lexicon-Feld additiv `lang`), Corpus-Index-Bump (`foreignTokens`), API-Rebuild. CONTRACTS: das additive API-Feld `lang` in §G.3 (Full-Record-Schema) nachtragen; der Ableitungs-Contract selbst (Lemma-Ebene führt, Token via `lemmaRef` abgeleitet, Overrides gewinnen) kommt als NEUE §H — §G ist vollständig der statischen JSON-API (#45) gewidmet und darf nicht mit dem Sprach-Contract vermischt werden.

## Phase 4: Frontend (L, = ursprüngliches #28-Feature)

- Playground-Modul `foreign-language-search.js` (DESIGN.md-Pattern): Sprach-Selector (nur real vorkommende Sprachen), Trefferliste mit Kontext analog Multi-Lemma.
- Token-Detailansicht: „Sprache: Französisch" wo lang gesetzt.
- Tests analog rhyme-dictionary.spec.js.

## Aufwand und Reihenfolge

Phase 0+1 zusammen eine Session; Phase 2 hängt an KZW/Linda-Kapazität; Phase 3+4 je eine Session. Kein Blocker außer der Kuratierungs-Kapazität.
