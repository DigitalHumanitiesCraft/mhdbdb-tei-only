# Stand #462: pos und posAll aus dem Korpus (angehalten, Frage an KZW)

Dieser Zweig (`claude/462-lemma-pos`) trägt den Umsetzungsstand von #462, der aus dem Daten-PR zu #460/#461 herausgenommen wurde. Entscheidung chsteiner am 10.10.2026 (G8): #462 wartet auf KZWs Antwort zum Gleichstand. Kein PR.

## Was gebaut ist

- `scripts/build-lemma-pos.py` schreibt `data/lemma-pos.json.gz` (je Lemma: Teil-Tag -> Anzahl der Tokens, Kompositum-Tags zerlegt, jeder verschiedene Teil einmal je Token). `--check` vergleicht im Speicher mit der committeten Datei.
- `scripts/build-authority-index.py` liest die Datei und ordnet `posAll` nach Korpushäufigkeit; `pos` ist das erste Element. Der Authority-Build liest `tei/` weiterhin nicht.
- Freshness-Schritt in `data-integrity.yml`, Doku in `DATA-MODEL.md`, `CONTRACTS.md`, `DEVELOPMENT.md`, `scripts/README.md`, Feldbeschreibung in `api/index.html`, `build:lemma-pos` in `package.json`, Spec-Anpassung für `salve`.

## Zwei Lesarten des Gleichstands

Grundmenge: 9.987 Lemmata mit mehr als einer Lexikonwortart und mindestens einem Korpusbeleg eines dieser Tags. Ein Gleichstand entsteht fast immer durch die Zerlegung: ein Token `NEG VRB` zählt für NEG und für VRB je einmal.

| Fall | Lemmata | pos weicht vom Lexikon-Erstwert ab |
|---|--:|--:|
| eindeutiger Spitzenwert | 2.971 | 1.381 |
| Gleichstand, Lexikon-Erstwert nicht gleichauf vorn | 156 | 156 |
| Gleichstand, Lexikon-Erstwert gleichauf vorn | 6.860 | 4.116 nur nach Lesart 2 |

- **Lesart 1 (Stand von Commit `35a1941e7`, nur der erste Teil dieser Zweigspitze):** bei Gleichstand die früheste Lexikonangabe unter den Gleichständigen. Geändert: 1.381 + 156 = **1.537**. Die Vorab-Messung der Koordination nannte 1.562; der Unterschied sind 22 Lemmata, deren häufigster Korpus-Tag im Lexikon nicht geführt wird, und 3 Gleichstände, deren Gleichständige alle außerhalb liegen.
- **Lesart 2 (Zweigspitze):** bei Gleichstand gewinnt das Inhaltswort, in der Reihenfolge VRB, NOM, ADJ vor allen anderen Tags, danach Lexikonreihenfolge. Geändert: 1.381 + 156 + 4.116 = **5.653**. Übergänge der 4.116: PRO nach VRB 1.422, PRP nach VRB 866, NEG nach VRB 630, ADJ nach NOM 300, ADV nach VRB 282, NOM nach VRB 174, NEG nach NOM 167, ART nach NOM 88. Von den 156 bekommen 145 ein anderes pos als nach Lesart 1.

Eine dritte, engere Lesart (das Inhaltswort entscheidet nur, wenn der Lexikon-Erstwert nicht gleichauf vorn liegt, 1.537 Änderungen) ist nicht gebaut.

## Die 22 Lemmata, deren häufigster Korpus-Tag im Lexikon nicht geführt wird (pos bleibt)

`pos` bleibt in beiden Lesarten Element von `posAll`. Das sind Befunde Lexikon gegen Korpus.

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

Dazu drei Gleichstände, deren Gleichständige alle außerhalb des Lexikons liegen: `lemma_23289` Cristeleison (INJ 7; NAM 6, VRB 6), `lemma_24478` enbewegen (ADJ 9; NEG 5, VRB 5), `lemma_29486` ungenuoc (NOM 4; ADJ, ADV, NEG je 1).

## Beispiele zur Frage

- `lemma_11590` entrûwen: INJ 7, NEG 373, VRB 373, Lexikon INJ, NEG, VRB. Lesart 1: pos NEG. Lesart 2: VRB.
- `lemma_10007` ûfgân: NOM 8, PRP 39, VRB 39, Lexikon NOM, PRP, VRB. Lesart 1: PRP. Lesart 2: VRB.
- `lemma_10027` enhazzen: ADV 3, NEG 10, VRB 10, Lexikon ADV, NEG, VRB. Lesart 1: NEG. Lesart 2: VRB.
