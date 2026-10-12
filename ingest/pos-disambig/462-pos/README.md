# #462: pos und posAll im Authority-Index aus dem Korpus

Arbeitsnotiz zu #462. Kein Batch-Log: kein Token wird umannotiert, `lexicon.xml` bleibt unverändert. Geändert wird nur, wie der Authority-Index `lemma.pos` und `lemma.posAll` aus den Lexikonangaben ableitet.

## Stand

- **Umgesetzt** auf `claude/462-posall` (auf `main` 6036dbe), Authority-Index 1.9.24. Korpus-Index unverändert (4.2.32).
- Übernommen aus dem Zweig `claude/462-lemma-pos` sind nur die Commits der Lesart 1 (`e07dee4`, `35a1941`). Die dort zuletzt gebaute Inhaltswort-Rangfolge (`ec6433c`, Lesart 2) ist verworfen und nicht enthalten. Der alte Zweig wird nicht gemergt.

## Entscheidung (KZW, 12.10.2026, von chsteiner bestätigt)

- `posAll` eines Lemmas enthält genau die im Lexikon geführten Wortarten, geordnet nach **absteigender Korpushäufigkeit**.
- `pos` ist `posAll[0]`.
- Gleichstand zwischen gleich häufigen Tags: **Lexikonreihenfolge**.
- Lexikon-Tag ohne Korpusbeleg: **Lexikonreihenfolge** (hinter allen belegten Tags).
- **Kein Vorrang für Inhaltswörter** (keine Rangfolge VRB vor NOM vor ADJ).
- Alle Lexikonwortarten bleiben in `posAll`; ein Korpus-Tag, den das Lexikon nicht führt, kommt nicht hinzu.

Gezählt wird, wie viele Tokens (`<w>` im `<body>` mit `@lemmaRef`) einen Teil-Tag tragen. Kompositum-Tags werden zerlegt: ein Token `NEG VRB` zählt für NEG und für VRB je einmal. Daher rühren die meisten Gleichstände.

## Was gebaut ist

- `scripts/build-lemma-pos.py` schreibt `data/lemma-pos.json.gz` (je Lemma: Teil-Tag nach Anzahl der Tokens). `--check` baut im Speicher und vergleicht mit der committeten Datei; CI-Schritt in `data-integrity.yml`.
- `scripts/build-authority-index.py` liest die Datei (fehlt sie, bricht der Build ab) und ordnet `posAll` wie oben; der Authority-Build liest `tei/` weiterhin nicht.
- Lifecycle-Schritt 5b und Routing-Zeile in `docs/DATA-MODEL.md`, dazu `CONTRACTS.md`, `DEVELOPMENT.md`, `scripts/README.md`, Feldbeschreibung in `api/index.html`, `build:lemma-pos` in `package.json`, Spec-Anpassung für `salve` in `testing/tests/cooccurrence-ranking.spec.js`.

## Messung (12.10.2026, gegen Authority-Index 1.9.23 auf `main`)

- Lemmata mit mehr als einer Lexikonwortart: 10.160. Davon mit mindestens einem Korpusbeleg eines dieser Tags: 9.987; die übrigen 173 behalten die Lexikonreihenfolge.
- `pos` geändert: **1.537** Lemmata. `posAll`-Reihenfolge geändert: 1.947. Die Menge der Werte in `posAll` ändert sich bei keinem Lemma; andere Felder des Index ändern sich nicht.

| Fall (unter den 9.987) | Lemmata | pos ändert sich |
|---|--:|--:|
| eindeutiger Spitzenwert | 2.971 | 1.381 |
| Gleichstand, Lexikon-Erstwert nicht unter den Gleichständigen | 156 | 156 |
| Gleichstand, Lexikon-Erstwert unter den Gleichständigen | 6.860 | 0 |

Beispiele: `lemma_79188` salve (NOM 15, VRB 16; Lexikon NOM, VRB) hat jetzt `pos` VRB und `posAll` [VRB, NOM]. `lemma_11590` entrûwen (INJ 7, NEG 373, VRB 373; Lexikon INJ, NEG, VRB) hat `pos` NEG, weil NEG im Lexikon vor VRB steht.

## Nicht Teil dieser Umsetzung: Widersprüche zwischen Lexikon und Korpus

Die Vorab-Messung der Koordination nannte 1.562 Änderungen statt 1.537. Die Differenz von 25 sind Lemmata, bei denen der häufigste Korpus-Tag im Lexikon nicht geführt wird: 22 Lemmata, dazu 3 Gleichstände, deren Gleichständige alle außerhalb des Lexikons liegen. Für sie bleibt `pos` ein Element von `posAll`, also eine Lexikonangabe. Ob dort das Lexikon oder die Annotation falsch ist, ist eine eigene Frage und wird hier nicht entschieden.

| Lemma | Korpus | posAll im Lexikon |
|---|---|---|
| `lemma_17456` zedolne | CNJ 2, VRB 2 | NOM, PRP |
| `lemma_21642` günlich | NOM 3, ADJ 1 | ADJ, ADV |
| `lemma_28722` ordenter | ADJ 1 | PRO, VRB |
| `lemma_35938` enzerrîzen | ADJ 3 | ADV, NEG, VRB |
| `lemma_36303` wandelsâne | NOM 3 | ADJ, ADV |
| `lemma_36513` gewiʒʒenlôs | ADJ 3 | ADV, NEG |
| `lemma_36569` enerleschen | ADJ 1 | NEG, VRB |
| `lemma_36619` alwirdic | NOM 1 | ADJ, GRA |
| `lemma_39197` enfirmen | ADJ 1 | ADV, NEG, VRB |
| `lemma_40349` iniustus | NOM 1 | ADJ, NEG |
| `lemma_48265` devotus | ADV 1 | ADJ, GRA |
| `lemma_48743` enwunden | ADJ 1 | ADV, NEG, VRB |
| `lemma_52645` nâchder | DET 1, PRP 1 | ADV, ART |
| `lemma_54948` decies | NUM 1 | ADJ, ADV |
| `lemma_54949` sepcies | NUM 2 | ADJ, ADV |
| `lemma_55290` deprofundis | NAM 1 | ADJ, NOM, PRP |
| `lemma_62410` clemens | ADV 1 | ADJ, GRA |
| `lemma_67668` indelicius | ADV 1 | ADJ, NEG |
| `lemma_67689` adire | NOM 1 | PRP, VRB |
| `lemma_67708` ater | PRO 1, PRP 1 | ADJ, NOM |
| `lemma_70735` stêter | ADJ 1 | PRO, VRB |
| `lemma_78454` immo | CNJ 1 | ADJ, ADV |

Die drei Gleichstände außerhalb des Lexikons: `lemma_23289` Cristeleison (INJ 7; NAM 6, VRB 6), `lemma_24478` enbewegen (ADJ 9; NEG 5, VRB 5), `lemma_29486` ungenuoc (NOM 4; ADJ, ADV, NEG je 1).
