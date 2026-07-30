# Fremdsprachen-Annotation: Daten-Phasenplan (#28)

Temporal Artifact zu Issue #28 (Suche nach fremdsprachigen Passagen). Grundlage: KZW-Freigabe vom 29.05. für den Weg „LLM + Begriffssystem `concept_23123000` + externe Wörterbücher", der Audit-Befund „0 Token-Annotationen im Korpus", Julias Bestätigung, dass auch WZB kein `xml:lang` auf Token-Ebene trägt, sowie die KZW-Entscheidungen vom 29.07. (siehe „Entscheidungen"). Nach Umsetzung: Kernwissen in DATA-MODEL/TEI-MODEL/CONTRACTS überführen, Datei löschen (CLAUDE.md → Temporal Artifacts).

## Ausgangslage (verifiziert)

- 0 `<w xml:lang>`, 0 `@foreign`, 0 `<foreign>`-Wrapper im gesamten Korpus (Body-Ebene); `xml:lang` existiert nur in Header-Metadaten.
- Schema: `<w>` erlaubt `@xml:lang` BEREITS (mhdbdb.rnc, w-Definition). `@foreign` ist NICHT im Schema und wird nicht eingeführt, da `xml:lang` die Information trägt. Für mehrwortige Passagen fehlt `<foreign>` im Schema und muss in Phase 3 ergänzt werden.
- Die `<etym>`-Komponenten in lexicon.xml lösen intern auf (alle Komponenten sind selbst MHD-Lemmata) – daraus ist Fremdsprachlichkeit NICHT ableitbar (Befund 28.05.).
- Zielsprachen laut KZW: gmh (Default), la, fr, ar, he, grc, it, es, en, yi, x-rotw.

## Entscheidungen (KZW, 29.07.)

Anlass war die Frage, wo die Grenze Lehnwort/Fremdwort verläuft (26 Beispielfälle, Kategorien ZITAT / FACH / FACH-Hybrid / INT / UR). Ergebnis:

1. **Zwei getrennte Sachverhalte, nicht ein Feld.** `@xml:lang` ist nach TEI die Sprache des Elementinhalts, also Code-Switching im Text. Wortherkunft ist eine Lexikon-Eigenschaft. Das wurde vorher vermischt; die Kategorien FACH/INT ließen sich deshalb nicht entscheiden.
2. **Die Grenze FACH/INT wird nicht gezogen.** Für das Mhd. existiert dazu kein Konsens in der Fachliteratur (Integrationskontinuum statt Dichotomie; „Fremdwort" ist ein Begriff des 19. Jh.). Eine Projektfestlegung dazu würde publiziert (`tei/`, `api/`, Zenodo) und wäre nicht belegbar.
3. **Kein Integrationsgrad-Urteil in den Daten.** Statt eines kuratierten Werts nur Herkunftsangabe + Quelle der Zuschreibung + gemessene Zahlen (Belege, Streuung, Reimbindung). Der Integrationsgrad wird daraus sichtbar, aber nirgends behauptet.
4. **Auszeichnungsregel für `@xml:lang`:** ZITAT vollständig; FACH nur pro Token nach der Drei-Punkte-Prüfung (unten); INT und UR gar nicht.
5. **Frontend: ein Einstieg, kein Kategorien-Filter.** Umbrella „Fremdsprachigkeit und Lehnwortschatz". Begründung KZW: publizierte Kategorien-Filter sind fachlich angreifbar, die Nutzerinnen sollen selbst interpretieren, entscheidend ist die Auffindbarkeit.

**Drei-Punkte-Prüfung pro Token (FACH-Fälle):** auszuzeichnen ist nur, was (1) keine mhd. Flexion trägt, (2) nicht im Reim mit Erbwörtern gebunden ist (messbar über `lineEnds[]`) und (3) unflektiert in fremder Lautgestalt steht, typischerweise im Verbund mit weiteren fremden Wörtern. Kalibrier-Beispiel: `kurteis` in TAN („der knabe der wart kurteis") wird NICHT ausgezeichnet (flektiert, reimgebunden); eine zusammenhängende französische Phrase in PZ wird ausgezeichnet.

**Asymmetrie als Grund für den strikten Start:** Ausweiten kostet später einen Skriptlauf; eine zurückgenommene Massenauszeichnung steht bis dahin im zitierbaren Datensatz.

## Zwei Schichten

**Schicht A: `@xml:lang` / `<foreign>` im Korpus (Code-Switching).** Token- und passagenbezogen, NICHT lemmagetrieben, weil dieselbe Lemma-ID mal fremd und mal integriert auftritt. Größenordnung: einige hundert bis wenige tausend Stellen (lateinische Zitatsätze wie PKP „deus ego sum et ego memet ipsum", französische Phrasen bei Wolfram, lateinische und tschechische Passagen in WZB). Nachprüfbar am Beleg, deshalb hart.

**Schicht B: Herkunft in `lexicon.xml` (`<etym>`).** Quellsprache + Quelle der Zuschreibung (Lexer/MWB/Kluge/LLM mit Konfidenz), kein Projekturteil über Integration. Diese Schicht ist lemmagetrieben und trägt die Masse (43.879 Lemmata als Entscheidungsraum).

Damit ist die frühere Grundsatzentscheidung „Lemma-Ebene führt" auf Schicht B eingeschränkt. Kein Widerspruch zu CONTRACTS §F.1 („Corpus Leads, Authority Follows"): §F regelt Lemma-Existenz und -Zählung; die Herkunftsangabe ist eine neue, eigenständig kuratierte Eigenschaft, für die `lexicon.xml` die Erfassungsoberfläche ist.

## Phase 0: Zielformat + Policy (S) – Schicht B kodiert, Schicht A offen

- `@xml:lang`-Werte-Set: BCP-47 (la, fr, ar, he, grc, it, es, en, yi, x-rotw); gmh bleibt impliziter Default und wird NICHT ausgezeichnet.
- Kodierung Schicht A: `<w xml:lang>` für Einzeltoken (schema-konform), `<foreign>` für mehrwortige Passagen (Schema-Ergänzung nötig, siehe Phase 3). **Noch nicht angewendet**, siehe „Abba als Kalibrierfall“.
- Kodierung Schicht B: **entschieden und im Schema (2026-07-30).** `<etym type="borrowing">` mit `<lang @norm>` (ISO 639-3/BCP-47) plus `<note type="attribution" @resp>` für die Quelle der Zuschreibung. Getrennt von `<etym type="morphological">`, beide können an einem Lemma stehen. Variante `<orth xml:lang>` bleibt ausgeschlossen, weil sie Schicht A und B wieder vermischen würde. Im gleichen Zug `<def>` und `<note type="comment">` im `<sense>`, weil eine Herkunftsangabe ohne Platz für die Bedeutung in der Luft hängt. Dokumentiert in TEI-MODEL-AUTH-FILES.md §3.1 („Kuratierte Angaben“); Index-Abbildung `lemma.origin` / `sense.definition` / `sense.comment` ab Authority Index v1.7.0.
- Offen als Deliverable: die Drei-Punkte-Prüfung als normative Regel in TEI-MODEL-AUTH-FILES (betrifft Schicht A).

### Abba als Kalibrierfall (2026-07-30)

`lemma_37818` (Abba, aramäische Gottesanrede) ist der erste kuratierte Schicht-B-Eintrag und zeigt das Zielformat an einem echten Fall. Beim Token in ZUK 2377 wurde `@xml:lang` **bewusst nicht** gesetzt, obwohl der Fall die Drei-Punkte-Prüfung bestehen würde (keine mhd. Flexion, nicht reimgebunden, fremde Lautgestalt, dazu Zitatcharakter nach Mk 14,36):

- Das Korpus trägt heute 0 `@xml:lang`-Token. Ein einziges markiertes Token behauptet im zitierbaren Datensatz, Fremdsprachigkeit sei erfasst, und wäre irreführender als gar keine Markierung.
- Schicht A soll laut Phase 2 vollständig gesichtet und laut Phase 3 per Skript mit Provenienz-Log geschrieben werden. Ein handgesetztes Einzeltoken davor müsste der Skriptlauf entweder reproduzieren oder überschreiben.

Damit ist „abba“ ein fertiger Testfall für Phase 1 Punkt 4 (Schicht-A-Kandidaten) und für Phase 2: Findet der Kandidaten-Scan diesen Beleg nicht, ist der Scan zu eng.

## Phase 1: Kandidaten-Generierung (M, dreigleisig, unabhängig parallelisierbar)

**Vorbedingung:** Lemma-Lookup reparieren. Die Recherche zu den Beispielfällen fand `blâmensier`, `missa` und `Messias` nicht, obwohl sie im Lexikon stehen (KZW-Befund 08.07.). Vor Phase 1 klären, ob das an Normalisierung, Suchpfad oder Datenzugriff liegt, sonst zieht sich der Fehler durch die gesamte Kandidatenmenge.

1. **Begriffssystem:** Lemmata, deren senses auf den `concept_23123000`-Subtree zeigen (Einzelsprachen). Achtung: das sind zunächst Lemmata, die Sprachen BEZEICHNEN (latîn, kriechisch). Liste als Quelle A mit eigener Herkunfts-Markierung.
2. **LLM-Klassifikation (Schicht B):** Batch über alle Lemmata (Form + Bedeutungen/Konzepte als Kontext). Output: (lemma_id, Quellsprache, Konfidenz, Begründung). Kein Integrationsurteil. Doppellauf für Konfidenz-Kalibrierung.
3. **Wörterbuch-Crawl (Schicht B):** Lexer/MWB via Wörterbuchnetz-API (Pattern #73), Etymologie-Abschnitte nach Sprach-Markern (mlat., afrz., hebr., …) parsen; Quelle C. Diese Quelle ist zugleich die Kontrollinstanz für die LLM-Zuschreibungen.
4. **Schicht-A-Kandidaten separat:** Korpus-Scan nach Passagen mit mehreren aufeinanderfolgenden Token ohne mhd. Flexion bzw. ohne Lemma-Anbindung, plus die Drei-Punkte-Prüfung auf FACH-Token. Ergebnis ist eine Belegliste, keine Lemma-Liste.

## Phase 2: Kuratierung (M, Mensch im Loop)

- Schicht B: Merge der Quellen A/B/C; Übereinstimmung von 2+ Quellen → Auto-Accept; nur-LLM mit hoher Konfidenz → Stichprobe; Konflikte → Review-Liste.
- Schicht A: vollständiges Review durch KZW/Julia, da klein und hart publiziert. Sortierte Belegtabelle mit KWIC-Kontext.
- Abnahme-Kriterium: Stichproben-Präzision ≥ 95 % pro Sprache (Schicht B); Schicht A vollständig gesichtet.

## Phase 3: Anwendung (M)

- Schema: `<foreign>` für mehrwortige Passagen in `mhdbdb.rnc` ergänzen (Schicht A). `@foreign` wird weiterhin nicht eingeführt.
- Schicht A ins TEI schreiben (Skript mit Provenienz-Log unter `ingest/foreign-lang/`, Schema-Validierung).
- Schicht B in lexicon.xml schreiben (`<etym>` mit Sprache + Quelle), ebenfalls mit Provenienz-Log.
- Corpus-Index: `foreignTokens[]` pro Text aus Schicht A (Position, Sprache) plus die aus Schicht B über `@lemmaRef` ableitbare Herkunftsangabe, getrennt gehalten und im Index als getrennte Herkunft erkennbar.
- Data-Change-Lifecycle: Authority-Index-Bump (additives Lexikon-Feld), Corpus-Index-Bump, API-Rebuild. CONTRACTS: additives API-Feld in §G.3 nachtragen; der Ableitungs-Contract (zwei Schichten, Token-Ebene führt für Schicht A, Lemma-Ebene für Schicht B) als NEUE §H, nicht in §G (dort ausschließlich statische JSON-API, #45).

## Phase 4: Frontend (L, = ursprüngliches #28-Feature)

**Ein Playground-Eintrag „Fremdsprachigkeit und Lehnwortschatz"**, kein Kategorien-Filter (KZW-Entscheidung 5). Sprachauswahl, eine Trefferliste, gespeist aus beiden Schichten; die Herkunft der Angabe wird im Treffer sichtbar, ist aber keine Filterbedingung.

- Pro Treffer werden Befunde angezeigt, keine Urteile: Quellsprache mit Quellenangabe („Lexer: afrz."), Belegzahl und Streuung („2.912 Belege in 118 Texten"), Reimbindung wo messbar, Hinweis bei zusammenhängenden anderssprachigen Passagen.
- Keine Anzeige eines Integrationsgrads, kein „Fremdwort: ja/nein".
- Standardsortierung nach Auffälligkeit im Text (zusammenhängende Passagen, dann seltene, dann häufige Belege), umschaltbar auf Alphabet und Belegzahl. Begründung: ohne Filter braucht die Liste eine Ordnung, sonst ertrinken bei „Latein" die Zitatstellen in den Lemmata lateinischer Herkunft. Sortierung ordnet, ohne zu behaupten.
- Token-Detailansicht: Sprachangabe, wo Schicht A gesetzt ist.
- Hilfeseite: kurzer methodischer Absatz (fließende Grenze, Herkunft aus Wörterbüchern, keine Entscheidung über „noch fremd"), plus Hinweis auf maschinelle Erzeugung mit Stichprobenprüfung, analog zur Attribution beim Figurenbezeichnungs-Werkzeug (#59).
- Tests analog `rhyme-dictionary.spec.js`.

## Aufwand und Reihenfolge

Lemma-Lookup-Fix zuerst. Danach Phase 0+1 zusammen eine Session; Phase 2 hängt an KZW/Julia-Kapazität; Phase 3+4 je eine Session. Kein Blocker außer der Kuratierungs-Kapazität.
