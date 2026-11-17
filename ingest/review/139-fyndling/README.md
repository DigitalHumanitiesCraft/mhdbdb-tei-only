# Gegenprobe #139: fyndling-Lemmata und Lesarten zu COR_W1 und COR_BS1

Beitrag von fyndling.de (@neongrau), Stand 2026-11-15. Nachtrag zur Lieferung vom 29.08.2026 (#376, 213 Lemma-Vorschläge). Gedacht als Material für die Gegenprobe der CoReMA-Lemmatisierung in #139.

Abgleich mit der früheren Fassung jener Lieferung (207 Vorschläge, liegt dem Projekt vor): Zwei Formen wiederholen dort schon vorgeschlagene Gleichungen von Form und Lemma, jeweils an anderer Stelle. Das sind `leczlten` → lebezelte (`lesarten.tsv`, COR_W1_022r_300, COR_W1_022v_82, COR_W1_024r_64) und `gwuercz` → wurz (`lesarten.tsv`, COR_W1_024r_131). Gegen die Fassung mit 213 Vorschlägen ist der Abgleich nicht gemacht.

## Inhalt

| Datei | Zeilen | Inhalt |
|---|--:|---|
| `lemmata.tsv` | 17 | Wortform → MHDBDB-Lemma (16 × COR_W1, 1 × COR_BS1) |
| `lesarten.tsv` | 59 | Bedeutung einer Wortform oder Wendung im Rezeptkontext (alle COR_W1) |

Bezug ist jeweils das Token in `ingest/cor/COR_*.tei.xml` (Stand 814ce4b). Steht eine Form im selben Rezept mehrfach, nennt `xml:id` alle Vorkommen, durch Leerzeichen getrennt. Wendungen aus mehreren Tokens sind mit `+` verbunden. `Kontext` zeigt das Token aus eurem TEI, Treffer in `[[ ]]`.

Jede Zuordnung wurde gegen unsere Transkription desselben Rezepts geprüft: Die Nachbarwörter im TEI müssen dort ebenso stehen. Abweichende Schreibungen (ue/u, zusammen/getrennt) sind dabei toleriert.

## Verfahren

Ausgangspunkt sind die Lemmata und Lesarten aus unseren durchgesehenen Rezeptübersetzungen. Jede Zeile wurde einzeln gegen Wörterbücher geprüft (Lexer, BMZ, FWB, DWB, Schmeller, Idiotikon, ReF, BDO u. a., abgefragt über unser Werkzeug `lookup.rb`). **Kein Beleg** im Sinn dieser Prüfung sind: CoReMA-Glossen, andere Kochbuchtexte (nur stützend) und unser eigener Korpus, bei `lemmata.tsv` auch euer Index selbst. Die tragenden Wörterbuchstellen stehen in der Spalte `Belege` (höchstens drei, Aussage gekürzt).

Lemmata folgen eurer Praxis: Ableitungen, Diminutive und ge-Bildungen stehen beim Grundlemma, wenn euer Lexikon den feineren Ansatz nicht führt (z. B. `gwrczen`, `wurczlein` → `wurz`). Der feinere Wörterbuchansatz steht dann in `Hinweis`.

## Spalte `Einstufung`

Ergebnis der Wörterbuchprüfung unserer eigenen Lesart, nicht eine Bewertung eurer Annotation:

| Einstufung | lemmata | lesarten | Bedeutung |
|---|--:|--:|---|
| bestätigt | 15 | 40 | Wörterbücher tragen unsere Lesart so |
| präzisiert | 0 | 16 | trägt im Kern, die Bedeutungsangabe ist danach geschärft |
| korrigiert | 2 | 3 | unsere frühere Lesart war falsch, die Zeile nennt die belegte |

In `lesarten.tsv` steht die Fassung nach der Wörterbuchprüfung, mit den tragenden Stellen in `Belege`. Was die Wörterbücher nicht tragen, sagt die Spalte `Bedeutung` ausdrücklich. Ausgelassen sind 4 Stellen, die offen geblieben sind (`mach lab`, zweimal `gepeacht`, `gukelpip`).

## Spalten

`lemmata.tsv`: `xml:id`, `Sigle`, `Form` (Schreibung in unserer Transkription), `Kontext`, `Lemma`, `lemma_id` (aus `lexicon.xml`), `Einstufung`, `Hinweis`, `Belege`, `Rezept` (unsere Rezeptseite mit Übersetzung), `Schritt` (Prüfschritt bei uns).

`lesarten.tsv`: wie oben, statt `Lemma`/`lemma_id` die Spalte `Bedeutung`.

## Lizenz

Die Spalte `Kontext` zitiert Text aus `ingest/cor/`, also aus CoReMA (ZIM-ACDH, Universität Graz). Dieser Text steht unter CC BY 4.0, Namensnennung erforderlich. Wen sie nennt (Quelle, Herausgeber, Transkription), steht in `ingest/cor/README.md`. Die eigenen Angaben des Beiträgers (Lemmata, Lesarten, Einstufungen, Hinweise) stehen unter CC BY-NC-SA 4.0.

## Bereinigt am 17.11.2026 durch das Projekt

Der Beitrag kam mit Arbeitsnotizen aus der Prüfung. Das Projekt hat sie entfernt oder aufgelöst, ohne eine Lesart zu ändern:

- `hosen nesel` (COR_W1_021v_166+COR_W1_021v_167): Die Notiz, die BMZ-Glosse „hosennestel = Hosenträger“ finde sich in keiner Abfrage, traf nicht zu. BMZ führt sie (2,330b,21). Die Stelle steht jetzt in `Belege`, die Schmeller-Stelle in `Hinweis`.
- `prot in gar` (COR_W1_023r_140+COR_W1_023r_141+COR_W1_023r_142): stand auf „bestätigt“ ohne `Belege`. Die nachgetragenen DWB-Stellen mit o-Schreibung von braten (s. v. kütte und sieden) sind an der Quelle geprüft und stehen jetzt in `Belege`. Die ReF-Trefferzahl für ‚prot‘ ist gestrichen, weil die Zeile `schon prot` (COR_W1_026r_184+COR_W1_026r_185) eine andere nennt.
- `weinperrn / weinper`: Die doppelt genannte Stelle COR_W1_022r_85 ist nur noch einmal aufgeführt.
- Interne Verweise sind ersetzt: Pfade von Abfragedateien durch den Namen der Abfrage, „Wie B23“ und „Wie B55“ durch Form und `xml:id` der gemeinten Zeile.
- Prüfaufträge und Notizen zum Abfragebudget sind gestrichen (`verbs`, `mach ez wol ab`, `virtails`, `puluer das wol`).
- Dieses README: Der Satz zur Disjunktheit mit der Lieferung vom 29.08. ist durch den Abgleich oben ersetzt, der Lizenzabschnitt trennt CoReMA-Text und eigene Angaben, drei Semikola sind durch Punkt oder Komma ersetzt.
