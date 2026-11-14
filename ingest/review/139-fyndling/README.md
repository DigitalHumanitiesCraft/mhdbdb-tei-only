# Gegenprobe #139: fyndling-Lemmata und Lesarten zu COR_W1 und COR_BS1

Beitrag von fyndling.de (@neongrau), Stand 2026-11-15. Nachtrag zur Lieferung vom 29.08.2026 (#376, 213 Lemma-Vorschläge): **disjunkt**, keine Zeile wiederholt einen der 213 Vorschläge. Gedacht als Material für die Gegenprobe der CoReMA-Lemmatisierung in #139.

## Inhalt

| Datei | Zeilen | Inhalt |
|---|--:|---|
| `lemmata.tsv` | 17 | Wortform → MHDBDB-Lemma (16 × COR_W1, 1 × COR_BS1) |
| `lesarten.tsv` | 59 | Bedeutung einer Wortform oder Wendung im Rezeptkontext (alle COR_W1) |

Bezug ist jeweils das Token in `ingest/cor/COR_*.tei.xml` (Stand 814ce4b). Steht eine Form im selben Rezept mehrfach, nennt `xml:id` alle Vorkommen, durch Leerzeichen getrennt; Wendungen aus mehreren Tokens sind mit `+` verbunden. `Kontext` zeigt das Token aus eurem TEI, Treffer in `[[ ]]`.

Jede Zuordnung wurde gegen unsere Transkription desselben Rezepts geprüft: Die Nachbarwörter im TEI müssen dort ebenso stehen. Abweichende Schreibungen (ue/u, zusammen/getrennt) sind dabei toleriert.

## Verfahren

Ausgangspunkt sind die Lemmata und Lesarten aus unseren durchgesehenen Rezeptübersetzungen. Jede Zeile wurde einzeln gegen Wörterbücher geprüft (Lexer, BMZ, FWB, DWB, Schmeller, Idiotikon, ReF, BDO u. a., abgefragt über unser Werkzeug `lookup.rb`). **Kein Beleg** im Sinn dieser Prüfung sind: CoReMA-Glossen, andere Kochbuchtexte (nur stützend) und unser eigener Korpus; bei `lemmata.tsv` auch euer Index selbst. Die tragenden Wörterbuchstellen stehen in der Spalte `Belege` (höchstens drei, Aussage gekürzt).

Lemmata folgen eurer Praxis: Ableitungen, Diminutive und ge-Bildungen stehen beim Grundlemma, wenn euer Lexikon den feineren Ansatz nicht führt (z. B. `gwrczen`, `wurczlein` → `wurz`). Der feinere Wörterbuchansatz steht dann in `Hinweis`.

## Spalte `Einstufung`

Ergebnis der Wörterbuchprüfung unserer eigenen Lesart, nicht eine Bewertung eurer Annotation:

| Einstufung | lemmata | lesarten | Bedeutung |
|---|--:|--:|---|
| bestätigt | 15 | 40 | Wörterbücher tragen unsere Lesart so |
| präzisiert | 0 | 16 | trägt im Kern, die Bedeutungsangabe ist danach geschärft |
| korrigiert | 2 | 3 | unsere frühere Lesart war falsch; die Zeile nennt die belegte |

In `lesarten.tsv` steht immer die geprüfte, belegte Fassung. Ausgelassen sind 4 Stellen, die offen geblieben sind (`mach lab`, zweimal `gepeacht`, `gukelpip`).

## Spalten

`lemmata.tsv`: `xml:id`, `Sigle`, `Form` (Schreibung in unserer Transkription), `Kontext`, `Lemma`, `lemma_id` (aus `lexicon.xml`), `Einstufung`, `Hinweis`, `Belege`, `Rezept` (unsere Rezeptseite mit Übersetzung), `Schritt` (Prüfschritt bei uns).

`lesarten.tsv`: wie oben, statt `Lemma`/`lemma_id` die Spalte `Bedeutung`.

## Lizenz

Wie das übrige Repositorium: CC BY-NC-SA 4.0.
