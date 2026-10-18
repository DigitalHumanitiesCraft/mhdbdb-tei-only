# #462: pos und posAll im Authority-Index aus dem Korpus

Arbeitsnotiz zu #462. Stand bis 16.10.2026 (der Abschnitt "Umsetzung (18.10.2026)" unten ändert das): Kein Batch-Log, kein Token wird umannotiert, `lexicon.xml` bleibt unverändert. Geändert wurde nur, wie der Authority-Index `lemma.pos` und `lemma.posAll` aus den Lexikonangaben ableitet.

## Stand (Index-Umbau, 12.10.2026)

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

## Vorschläge (16.10.2026)

**Alle Urteile dieses Abschnitts sind maschinell vorbereitete Vorschläge. KZW entscheidet; am 16.10.2026 war nichts davon in `lexicon.xml` oder `tei/` eingetragen (Umsetzung nach ihrer Antwort: Abschnitt "Umsetzung (18.10.2026)").** Sie stammen aus einer Lesung der Belege durch einen Agenten und sind bisher von keinem Menschen geprüft. Die Begründungen nennen ihre Sicherheit selbst, wo sie geschätzt ist.

| Datei | Inhalt | Zeilen |
|---|---|--:|
| `vorschlaege.tsv` | ein Vorschlag je Lemma für die 25 Lemmata oben (22 Widersprüche und 3 Gleichstände außerhalb des Lexikons) | 25 |
| `belege.tsv` | alle Korpusbelege dieser 25 Lemmata (`<w>` im `<body>` mit dem Lemma als Token in `@lemmaRef`) mit Kontext von je acht Tokens (Satzzeichen eingeschlossen) und der umgebenden Verszeile oder dem Absatz | 66 |

Spalten von `vorschlaege.tsv`: `lemma_id`, `orth`, `lexikon_pos` (Wortarten im Lexikon), `korpus_pos_verteilung` (Token-`@pos` roh, in Klammern zerlegt in Teil-Tags), `vorschlag` (Code), `detail` (was zu tun wäre), `begruendung`, `belege_ids` (`xml:id` der gelesenen Belege, durch `;` getrennt). Spalten von `belege.tsv`: `lemma_id`, `sigle`, `xml_id`, `pos`, `ana`, `form`, `reason`, `mehrfach_lemma`, `kontext` (Beleg in `[[ ]]`), `vers`.

Die Codes, wie `detail` sie verwendet (die Zuordnung der Buchstaben ist aus den Zeilen gelesen, nicht an anderer Stelle definiert):

| Code | Bedeutung | Lemmata |
|---|---|--:|
| a | Lexikon um die Wortart ergänzen, die der Korpus trägt | 15 |
| b | Token-`@pos` am Beleg ändern, Lexikon bleibt | 3 |
| c | Beleg gehört zu einem anderen Lemma | 2 |
| d | Frage an KZW, ohne die der Vorschlag nicht möglich ist | 3 |
| e | kein Eingriff, die Konvention deckt den Befund | 2 |

Die Zählung je Code steht in der Spalte `vorschlag` und ist aus der Datei gezählt (15 + 3 + 2 + 3 + 2 = 25). Zwei Zeilen tragen einen Nebenbefund über das Hauptergebnis hinaus: bei `enbewegen` (a) ein Token, das eher ADJ wäre (b), bei `ungenuoc` (e) ein Token mit unaufgelöstem Mehrfachtag `ADJ ADV NEG`.
Erzeugt wird `belege.tsv` von `scripts/review/collect-462-pos.py` (Aufruf im Docstring); `vorschlaege.tsv` ist die Lesung eines Agenten auf diesen Belegen. Das Skript schreibt in einen Ausgabeordner außerhalb des Repos (Pflichtargument, oder unter `temp/`); wer `belege.tsv` erneuern will, vergleicht und kopiert bewusst.

## Umsetzung (18.10.2026), nach KZWs Antwort vom 16.10.2026

Umsetzung: `scripts/ingest/pos-disambig/apply-462-602.py` (Lauf vom 18.10.2026). KZW hat a, b und c übernommen, dazu günlich (Gunst als NOM), deprofundis (NOM) und ungenuoge (ADV).

| Was | Menge | Stellen |
|---|--:|---|
| Lexikon um Wortart ergänzt (Code a und günlich) | 16 Lemmata, 17 Wortarten | `lexicon.xml`, `<pos>` alphabetisch einsortiert wie in 10.158 von 10.160 Einträgen mit mehreren Wortarten; `ater` bekommt PRO und PRP |
| Token-`@pos` geändert (Code b, deprofundis, ungenuoge) | 6 Tokens | `JT_48512000_3` und `JT_48672000_3` (zedolne, `CNJ VRB` zu `PRP VRB`), `AC1_34630_0` (alwirdic, NOM zu ADJ), `AC1_35150_4` (immo, CNJ zu ADV), `ADP_8507000_12` (deprofundis, NAM zu NOM), `AXU_8247_3` (ungenuoge, `ADJ ADV NEG` zu ADV) |
| umgehängt (Code c) | 2 Tokens | `ADP_201100_7` aditus von `lemma_67689` adire auf `lemma_67813` aditus (NOM, `@ana` auf `lemma_67813_sense_105127`, dessen einziger Sense); `ADP_701000_13` standime von `lemma_70735` stêter auf `lemma_70734` stânder (ADJ, ohne `@ana`, stânder hat zwei Senses). Neue Variantentypen `type_372859` und `type_372860` nach der Regel aus #367, die alten Typen `type_341714` und `type_350509` entfallen |

Nicht umgesetzt:

- **Code e** (iniustus, ungenuoc): kein Eingriff, wie vorgeschlagen.
- **`@reason` an zedolne:** der Vorschlag sah für die Fusion ze+dolne ein `@reason` vor. Es fehlt bewusst: ein `@reason` auf `<w>` macht die Datei für `tei_all` ungültig, und JT stünde dann neu außerhalb der Baseline in `scripts/audit/validate-corpus.py` (gemessen am 18.10.2026, 35 statt 34 Dateien). Das Nachziehen ist ein offener Rest für nach dem Freeze.
- **Kommentartext unter deprofundis:** KZWs Text zu Ezechiel 28,13 erklärt den Beleg `ADP_104900_10` ("indeliciis paradisi dei fuisti"), nicht deprofundis. Er ist nicht eingetragen, solange die Lemmatisierung von indelicius offen ist.
- **indelicius** (`ADP_104900_10`): offen. MWB-Suche (18.10.2026): kein Treffer für `indelicius`, `indel*` und `delici*` in Lemmaliste, Wortformenliste und Artikelstichwörtern (Kontrollwert: `minne` 6 Treffer). Das Wörterbuch führt nur Mittelhochdeutsches, die lateinische Fügung ist dort nicht zu erwarten. Der Satz im Kontext: "tu signaculum similitudinis plenus sapientia et perfectus decore indeliciis paradisi dei fuisti, daz spricht alsus daz er ware ein insigile nach demo frone bilide". Das ist lateinisch `in deliciis`; `delicius` (`lemma_67669`) hat 0 Belege, ein Lemma deliciae fehlt im Lexikon.
- **unpeweglich** (`LZT_2360_0`): offen, KZW wollte den Satz sehen. Satz: "nach herschall strebt ir herz zu allen stunden / unpeweglich fürsichtig / auch senftes muets gen frembden unde kunden". MWB-Suche: `unpeweglich` und `unbeweglich` keine Treffer; `unbewegelich` 1 Treffer in der Lemmaliste, **un-bewëgelich Adj.** mit 21 Belegen im Belegarchiv (`konkordanz.php?lid=182883000`). Das Token ist `NEG VRB` getaggt und steht auf `lemma_24478` enbewegen; nach Satz und MWB ist es ein Adjektiv. Nach der Ergänzung von ADJ am Lemma enbewegen (Code a, oben) fehlt nur noch der Token-`@pos`.
