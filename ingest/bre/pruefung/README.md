# Prüfpaket Weingrüße (#147)

Die Wörter der 18 Weingrüße-Zeugen in `ingest/bre/` haben maschinell drei Angaben bekommen: ein **Lemma** (welches Wort des Wörterbuchs ist das?), eine **Wortart** und eine **Bedeutung** (welche Bedeutung des Lemmas ist hier gemeint?). Wo das Lexikon nur eine Möglichkeit kennt, wurde sie ohne Prüfung übernommen. Wo es mehrere gibt, hat ein Sprachmodell (Claude Sonnet) am Satzzusammenhang entschieden und dazu angegeben, wie sicher es ist: `high`, `medium` oder `low`.

Dieses Paket enthält die Entscheidungen, bei denen ein Blick am meisten bringt: **alle** mit `low` und eine zufällige Auswahl von einem Fünftel der Entscheidungen mit `medium`. Was `high` ist, steht nicht darin. Wenn sich in der Auswahl viele Fehler finden, ist das ein Zeichen, dass auch die übrigen `medium`-Entscheidungen durchgesehen werden müssen.

## Die vier Dateien

| Datei | Zeilen | Was darin steht |
|---|---|---|
| `lemma.tsv` | 98 = 45 `low` + 53 von 262 `medium` | Lemma-Entscheidungen |
| `wortart.tsv` | 185 = 74 `low` + 111 von 554 `medium` | Wortart-Entscheidungen |
| `bedeutung.tsv` | 394 = 220 `low` + 174 von 870 `medium` | Bedeutungs-Entscheidungen |
| `lemma-verdacht.tsv` | 233 | Wörter, bei denen **keine** Bedeutung ihres Lemmas passte: Verdacht auf ein falsches Lemma |

Die Zahlen gibt `python -P -E scripts/ingest/bre/20-pruefpaket.py` aus. Eine Zeile kann für viele Wörter stehen (Spalte `belege`).

**`lemma-verdacht.tsv` ist die wichtigste Datei.** Wenn das Lexikon eine Schreibung nur unter einem einzigen Lemma kennt, hat die Maschine dieses Lemma ohne Blick auf den Satz gesetzt. Das geht schief, wenn dieselbe Schreibung hier ein anderes Wort ist: „dorffen“ steht im Lexikon unter *durfen* (dürfen), meint in den Weingrüßen aber Dörfer. Solche Fehler fallen erst auf, wenn keine Bedeutung des Lemmas passt. 190 der 233 Zeilen haben ihr Lemma auf diesem Weg bekommen (Spalte `sicherheit`: `Lemma: auto-single`). Hier bitte in `passt` eintragen, ob das **Lemma** stimmt, und in `korrektur` das richtige Lemma, wenn es eins gibt, sonst `kein Lemma`.

Die Dateien sind Tabellen (TSV, mit Tabulator getrennt). Sie lassen sich in Excel oder LibreOffice öffnen: Datei öffnen, Trennzeichen „Tabulator“, Zeichensatz UTF-8.

## Was in den Spalten steht

| Spalte | Bedeutung |
|---|---|
| `nr` | laufende Nummer, zum Verweisen in einer Rückmeldung |
| `art` | „einzelnes Wort“ oder „für alle N Belege dieser Form“: dann gilt die Entscheidung für jedes Vorkommen dieser Schreibung, gezeigt werden bis zu drei Beispiele |
| `wort` | die Wortform, wie sie im Zeugen steht |
| `zeuge`, `text` | Sigle des Zeugen und Titel des Weingrußes |
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
- `nein`: sie stimmt nicht. In `korrektur` dann die richtige Wahl, wenn sie unter `andere_moeglichkeiten` steht (die Kennung genügt, etwa `lemma_1517` oder `PRO`). Steht sie dort nicht, weil dem Lexikon das richtige Wort fehlt, genügt ein Hinweis in `anmerkung`.
- `?`: nicht zu entscheiden.

Leere Zeilen gelten als nicht geprüft. Die ausgefüllte Datei bitte im Issue #147 anhängen oder zurückschicken. Ein Skript, das die Korrekturen einspielt, gibt es noch nicht, es entsteht mit den ersten Rückmeldungen.

## Prüfseite statt Tabelle

`pruefseite.html` ist dasselbe Paket zum Prüfen im Browser: herunterladen und lokal öffnen, Internet braucht es nur für die Links. Sie zeigt aus `lemma-verdacht.tsv` die **vorgesichteten** Zeilen (nächster Absatz) und aus `lemma.tsv`, `wortart.tsv` und `bedeutung.tsv` je eine **Stichprobe von 50 Zeilen**, geschichtet nach `low` und `medium` im Verhältnis der Datei und mit dem festen Zufallswert 147 gezogen; die Seite nennt bei jeder Stichprobe den Nenner. Je Zeile stehen der Vers mit dem Wort und die Nachbarverse aus der TEI-Datei, der maschinelle Vorschlag mit Begründung, die anderen Möglichkeiten, „ja“ / „nein“ / „? Nicht zu entscheiden“ und die Felder Korrektur und Anmerkung. Der Arbeitsstand bleibt im Browser; zurück kommt der **JSON-Export**, dessen Felder `passt`, `korrektur` und `anmerkung` den Spalten oben entsprechen (Format im Docstring von `scripts/ingest/bre/22-pruefseite.py`, das die Seite neu baut).

### Vorgesichtet: `vorschlaege-verdacht.tsv`

Zu jeder der 233 Zeilen von `lemma-verdacht.tsv` hat die Session am 26.11.2026 ein Urteil vorgeschlagen (Spalte `urteil`: `ja` = Lemma stimmt, `nein` = Lemma falsch, `?` = nicht zu entscheiden; `korrektur` = das passende Lexikonlemma, `notiz` = Grund in eigenen Worten). Grundlage waren der Kontext, das Lexikon und die Übersetzung der Druckausgabe (Hirzel-Druckfahnen, lokal, nicht im Repository). Das ist eine **Durchsicht der Session, keine Prüfung**: ein maschineller Vorschlag, der nicht bestätigt ist. Die Maschinenentscheidungen unter `../phase1/` bis `../phase3/` sind davon unberührt und sind ohne die Druckausgabe entstanden.

Verteilung: 139 `nein`, 60 `ja`, 34 `?`. Die Prüfseite zeigt alle 34 `?` und zur Kontrolle der Urteile je 12 Zeilen mit `nein` und mit `ja` (Zufallswert 147). Finden sich in den Kontrollzeilen Fehler, gelten die übrigen Urteile als unsicher. Offen sind bei den Urteilen die Kennung für „wer“ (`lemma_7482`, Eintrag nicht darauf geprüft, ob er das Fragepronomen führt) und die Frage, ob `lemma_702` oder `lemma_712` für „Bier“ gilt. 38 Zeilen gehören zu Texten, die im Druck nicht stehen (Metgruß, Biergruß, Pseudo-Weingrüße, Vorspruch): dort stützt sich das Urteil nur auf den Kontext. Ein Einspielskript für angenommene Urteile gibt es noch nicht.

## Was dieses Paket nicht zeigt

- Wörter, für die das Lexikon gar kein Lemma kennt. Sie stehen nach Häufigkeit sortiert in `../phase1/lemma-unmatched.tsv` und sind eine Liste für das Lexikonteam, keine Prüfaufgabe.
- Entscheidungen, bei denen das Modell keine der Möglichkeiten für richtig hielt (`abstain`). Diese Wörter haben die Angabe nicht bekommen, sie stehen in den Tabellen unter `../phase1/` bis `../phase3/`.
- Formen mit mehreren Möglichkeiten, die nur einmal vorkommen (Hapaxe): sie wurden bewusst nicht entschieden und haben die Angabe nicht.
- Wortarten, die das Lexikon für ein Lemma nicht vorsieht. Häufigster Fall: „zu“ als Gradwort („zu vil“) oder Verbteil („zu lauffen“) wäre ein Adverb, das Lemma *zuo* kennt aber nur Konjunktion und Präposition. Solche Wörter haben keine Wortart bekommen.

Die Paralleltexte der anderen Zeugen stehen auf den Einzeltextseiten des [Brevitas-Wikis](https://wiki.brevitas.org/wiki/Dokumentation_Edition_Weingr%C3%BC%C3%9Fe). Die Druckfassung wurde für die maschinellen Entscheidungen nicht verwendet.

Erzeugt von `scripts/ingest/bre/20-pruefpaket.py` (fester Zufallswert 147, das Paket ist reproduzierbar).
