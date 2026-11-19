# Prüfpaket Hesler-Apokalypse (#262)

Die Wörter der Apokalypse Heinrichs von Hesler in `ingest/apk/APK.tei.xml` haben maschinell drei Angaben bekommen:

- ein **Lemma**: welches Wort des Wörterbuchs ist das?
- eine **Wortart**
- eine **Bedeutung**: welche Bedeutung des Lemmas ist hier gemeint?

Wo das Lexikon nur eine Möglichkeit kennt, wurde sie ohne Prüfung übernommen. Wo es mehrere gibt, hat ein Sprachmodell (Claude Sonnet) am Satzzusammenhang entschieden und dazu angegeben, wie sicher es ist: `high`, `medium` oder `low`.

Dieses Paket enthält die Entscheidungen, bei denen ein Blick am meisten bringt: **alle** mit `low` und eine zufällige Auswahl von einem Fünftel der Entscheidungen mit `medium`. Was `high` ist, steht nicht darin. Finden sich in der Auswahl viele Fehler, müssen auch die übrigen `medium`-Entscheidungen durchgesehen werden.

## Die vier Dateien

| Datei | Zeilen | Was darin steht |
|---|---|---|
| `lemma.tsv` | 567 = 311 `low` + 256 von 1.280 `medium` | Lemma-Entscheidungen |
| `wortart.tsv` | 183 = 44 `low` + 139 von 695 `medium` | Wortart-Entscheidungen |
| `bedeutung.tsv` | 282 = 139 `low` + 143 von 714 `medium` | Bedeutungs-Entscheidungen |
| `lemma-verdacht.tsv` | 306 | Wörter, bei denen **keine** Bedeutung ihres Lemmas passte: Verdacht auf ein falsches Lemma |

Die Zahlen gibt `python -P -E scripts/ingest/apk/20-pruefpaket.py` aus. Eine Zeile kann für viele Wörter stehen (Spalte `belege`).

**`lemma-verdacht.tsv` ist die wichtigste Datei.** Kennt das Lexikon eine Schreibung nur unter einem einzigen Lemma, hat die Maschine dieses Lemma gesetzt, ohne auf den Satz zu sehen. Das geht schief, wenn dieselbe Schreibung hier ein anderes Wort ist: „geschaft“ steht im Lexikon nur unter dem Substantiv *geschaft*, ist bei Hesler aber das Partizip von *schaffen* („Der alle dinc hat geschaft“). Allein diese Schreibung füllt 30 Zeilen. Solche Fehler fallen erst auf, wenn keine Bedeutung des Lemmas passt. 214 der 306 Zeilen haben ihr Lemma auf diesem Weg bekommen (Spalte `sicherheit`: `Lemma: auto-single`). Hier bitte in `passt` eintragen, ob das **Lemma** stimmt, und in `korrektur` das richtige Lemma, wenn es eins gibt, sonst `kein Lemma`.

Die Dateien sind Tabellen (TSV, mit Tabulator getrennt). Sie lassen sich in Excel oder LibreOffice öffnen: Datei öffnen, Trennzeichen „Tabulator“, Zeichensatz UTF-8.

## Was in den Spalten steht

| Spalte | Bedeutung |
|---|---|
| `nr` | laufende Nummer, zum Verweisen in einer Rückmeldung |
| `art` | „einzelnes Wort“, „für alle N Belege dieser Form“ (Lemma) oder „für alle N Belege dieser Gruppe“ (Wortart, Bedeutung): dann gilt die Entscheidung für jedes dieser Vorkommen, gezeigt werden bis zu drei Beispiele |
| `wort` | die Wortform, wie sie im Text steht |
| `zeuge`, `text` | immer `APK`, dazu die Versnummer |
| `kontext` | fünf Wörter davor und danach, das Wort selbst in [eckigen Klammern], bei mehreren Beispielen durch ¶ getrennt |
| `zuweisung` | was die Maschine gewählt hat: Lemma mit Wortarten, Wortart, oder Bedeutung mit ihren Konzepten |
| `sicherheit` | `low` oder `medium` |
| `begruendung` | die Begründung des Modells, höchstens 15 Wörter |
| `andere_moeglichkeiten` | was das Lexikon sonst angeboten hätte |
| `belege` | für wie viele Wörter die Entscheidung gilt |
| `xml_id` | Kennung des Wortes in der TEI-Datei, zum Nachschlagen |
| `passt`, `korrektur`, `anmerkung` | **zum Ausfüllen** |

## Was zu tun ist

Je Zeile in der Spalte `passt` eintragen:

- `ja`: die Zuweisung stimmt.
- `nein`: sie stimmt nicht. In `korrektur` dann die richtige Wahl, wenn sie unter `andere_moeglichkeiten` steht (die Kennung genügt, etwa `lemma_1517` oder `PRO`). Fehlt sie dort, weil dem Lexikon das richtige Wort fehlt, genügt ein Hinweis in `anmerkung`.
- `?`: nicht zu entscheiden.

Leere Zeilen gelten als nicht geprüft. Die ausgefüllte Datei bitte im Issue #262 anhängen oder zurückschicken. Ein Skript, das die Korrekturen einspielt, gibt es noch nicht, es entsteht mit den ersten Rückmeldungen.

## Was dieses Paket nicht zeigt

- **Wörter, für die das Lexikon gar kein Lemma kennt:** 4.786 Wörter in 2.756 Schreibungen, viele davon ostmitteldeutsche Formen wie „dutet“ (deutet) oder „irkornen“ (erkoren). Sie stehen nach Häufigkeit sortiert in `../phase1/lemma-unmatched.tsv` und sind eine Liste für das Lexikonteam, keine Prüfaufgabe.
- **Entscheidungen, bei denen das Modell keine der Möglichkeiten für richtig hielt (`abstain`):** Diese Wörter haben die Angabe nicht bekommen. Sie stehen in den Tabellen unter `../phase1/` bis `../phase3/`.
- **Formen mit mehreren Möglichkeiten, die nur einmal vorkommen:** Sie wurden bewusst nicht entschieden und haben die Angabe nicht.
- **Gemischte Gruppen bei Wortart und Bedeutung:** Wo eine Schreibung in den Beispielen unterschiedlich gebraucht wird, etwa „daz“ als Artikel und als Nebensatzeinleitung, müsste jedes Wort einzeln entschieden werden. Das ist für Wortart (13.925 Wörter) und Bedeutung (9.014 Wörter) noch nicht geschehen, diese Wörter haben die Angabe nicht. Beim Lemma ist es geschehen. Ein Teil der gemischten Gruppen bei der Bedeutung geht nach den Begründungen des Modells auf falsche Lemmata zurück (etwa „wert“ statt *werden*, „lut“ statt *liute*). Sie stehen deshalb nicht in `lemma-verdacht.tsv`, gehören der Sache nach aber dazu.
- **Wörter, bei denen weder beim Lemma noch bei der Bedeutung eine Wahl bestand:** 41.597 der 58.324 Wörter, deren Lemma das Lexikon ohne Alternative vorgab, haben auch nur eine mögliche Bedeutung. Ein falsches Lemma fällt bei ihnen nirgends auf, auch nicht in `lemma-verdacht.tsv`. Ein Beispiel hat die automatische Durchsicht des PRs gefunden: „i“ in den Vokalaufzählungen V. 1373 und V. 1405 („Sie sint diz a e i o u“) steht unter der römischen Zahl `lemma_13826` statt unter `lemma_2` wie „a“, „o“ und „u“ im selben Vers (`APK_1373_6`, `APK_1405_3`).
- **Zwei Einträge `sie` im Lexikon:** „ir“ steht teils unter `lemma_5454` (49 Wörter), teils unter `lemma_56116` (465 Wörter), darunter jeweils das besitzanzeigende „ir“ (ihr, ihre). Entschieden hat in beiden Fällen dasselbe Modell. Beide heißen *sie*. Welcher der richtige ist, ist eine Frage an das Lexikon, nicht an diesen Text.

Erzeugt von `scripts/ingest/apk/20-pruefpaket.py` (fester Zufallswert 262, das Paket ist reproduzierbar).
