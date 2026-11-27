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

`pruefseite.html` ist dasselbe Paket zum Prüfen im Browser: herunterladen und lokal öffnen, Internet braucht es nur für die Links. Sie zeigt **alle** Zeilen aus `lemma-verdacht.tsv` und aus `lemma.tsv`, `wortart.tsv` und `bedeutung.tsv` je eine **Stichprobe von 50 Zeilen**, geschichtet nach `low` und `medium` im Verhältnis der Datei und mit dem festen Zufallswert 147 gezogen; die Seite nennt bei jeder Stichprobe den Nenner. Je Zeile stehen der Vers mit dem Wort und die Nachbarverse aus der TEI-Datei, der maschinelle Vorschlag mit Begründung, die anderen Möglichkeiten, „ja“ / „nein“ / „? Nicht zu entscheiden“ und die Felder Korrektur und Anmerkung. Der Arbeitsstand bleibt im Browser; zurück kommt der **JSON-Export**, dessen Felder `passt`, `korrektur` und `anmerkung` den Spalten oben entsprechen (Format im Docstring von `scripts/ingest/bre/22-pruefseite.py`, das die Seite neu baut).

## Übernommene Lemma-Korrekturen: lemma-korrekturen.tsv

Am 26.11.2026 hat KZW 50 der 233 Verdachtsfälle auf der Prüfseite entschieden (24 Kontrollzeilen, alle gleich wie der Vorschlag der Session, dazu die 26 offenen). Danach hat sie die übrigen 183 Vorschläge der Session zur Übernahme freigegeben und im Chat sechs weitere Fälle (`wer`) und zwei (`quelen`) entschieden. `lemma-korrekturen.tsv` hält je Token (`xml_id`) das Altlemma, das neue Lemma und die Quelle fest: 179 Tokens (160 davon stehen in `lemma-verdacht.tsv`), davon 31 nach KZWs Entscheidung (23 Prüfseite, 8 Chat), 120 nach dem freigegebenen Vorschlag der Session, 15 Nachkorrekturen der Session und 13 Parallelstellen in B2, d4 und d6 (27.11.2026, Quelle „Session, Parallelstelle“, nicht von KZW freigegeben), für die die Freigabe nicht galt (siehe unten). `scripts/ingest/bre/24-lemma-korrektur.py` hat sie in die Zeugen übernommen. Dabei fielen bei 107 Tokens `@pos` weg (`@ana` und `@corresp` waren bei diesen Tokens nicht gesetzt) und 20 Zeilen in `phase2/pos-patch.tsv` und 83 in `phase3/sense-patch.tsv`. Phase 2 und 3 sind für diese Tokens danach neu gelaufen (entschieden von der Session, `llm:claude-sonnet-5-5`, Zeilen in `phase2/pos-bulk.tsv`, `pos-patch.tsv`, `phase3/sense-bulk.tsv`, `sense-patch.tsv`); 9 Tokens ohne `@pos` und 7 ohne `@ana` bleiben (Hapaxe oder abstain). Nachkorrekturen der Session, bei der Durchsicht der Wortart und Bedeutung aufgefallen (Reviewer der Phase 2 und 3 hat die Paare gegen das Lexikon gelesen): `sannt` (nr 142, 143) stand zuerst unter `lemma_5107` (sant, Sand), richtig ist `lemma_18884` Sankt; `hayst` (nr 60) stand unter `lemma_18885` (heizen), richtig ist `lemma_2731` heiʒʒen; alle neun annotierten Belege von „an perg und an leiten/leyten“ (nr 81 und 33 bis 37 sowie drei weitere, die alle nicht in der Verdachtsliste standen, eines davon als Einsinn-Lemma liuten) standen unter `lemma_19575` (leite, Leitung), legen oder liuten, der Hang ist `lemma_3746` lîte (Reviewer, Lexikon geprüft). Dazu drei Parallelstellen korrigierter Verse in anderen Zeugen, die ebenfalls nicht in der Verdachtsliste standen: `BRE_D5_12_9_1` (nemen, jetzt name wie nr 106), `BRE_D2_0_315_8` (quâle, jetzt quellen wie nr 120 bis 122), `BRE_D3_8_15_0` (her, jetzt herre wie im Parallelvers von GEORG1508). Die Zeugen wurden einmalig mit `24 --tabelle` nachkorrigiert, die Tabelle im Repository trägt die Werte für einen Wiederaufbau ab Phase 1. `wer` als Pronomen steht im Korpus weit überwiegend unter `lemma_5961` (swer): 643 `<w>` mit `PRO IPA` in `tei/*.xml`, Zählung des Reviewers per lxml, so auch hier.

Nicht übernommen, weil offen (13 Tokens):
- `reucht` (nr 70, 71): KZW findet in den Wörterbüchern kein „reuchen“, die Übersetzung sagt „reich werden“. Ein Lemma ist noch zu suchen.
- `gespreng`, `gespring` (nr 156 bis 163): KZW will ein neues Lemma `gesprinc` stN. im Lexikon (drei Bedeutungen: Quelle/Brunnen, bildlich Ursprung/Ausgangspunkt, Getränk). Das Lemma gibt es noch nicht; das Anlegen ist ein Datenschritt mit dem Data-Change-Lifecycle für `authority-files/`.
- `leitten` in `BRE_OCT145_104v_6_3` („in zitzel und auch an leitten mit genaden“, Hapax unter `lemma_3692` leiten): vermutlich eine entstellte Fassung desselben Verses wie „an perg und an leiten“, philologische Frage, nicht von der Session gesetzt; kommt auf das Blatt für Silvan.
- `denest` (nr 15, 16): vermutlich „dennoch“ (`lemma_1077` dannoch), die Zuordnung hat KZW nicht bestätigt.

Aufruf: `python -P -E scripts/ingest/bre/24-lemma-korrektur.py --trocken`. Ein zweiter Lauf bricht mit einem harten Fehler ab, weil das Altlemma nicht mehr dasteht.

## Was dieses Paket nicht zeigt

- Wörter, für die das Lexikon gar kein Lemma kennt. Sie stehen nach Häufigkeit sortiert in `../phase1/lemma-unmatched.tsv` und sind eine Liste für das Lexikonteam, keine Prüfaufgabe.
- Entscheidungen, bei denen das Modell keine der Möglichkeiten für richtig hielt (`abstain`). Diese Wörter haben die Angabe nicht bekommen, sie stehen in den Tabellen unter `../phase1/` bis `../phase3/`.
- Formen mit mehreren Möglichkeiten, die nur einmal vorkommen (Hapaxe): sie wurden bewusst nicht entschieden und haben die Angabe nicht.
- Wortarten, die das Lexikon für ein Lemma nicht vorsieht. Häufigster Fall: „zu“ als Gradwort („zu vil“) oder Verbteil („zu lauffen“) wäre ein Adverb, das Lemma *zuo* kennt aber nur Konjunktion und Präposition. Solche Wörter haben keine Wortart bekommen.

Die Paralleltexte der anderen Zeugen stehen auf den Einzeltextseiten des [Brevitas-Wikis](https://wiki.brevitas.org/wiki/Dokumentation_Edition_Weingr%C3%BC%C3%9Fe). Die Druckfassung wurde für die maschinellen Entscheidungen nicht verwendet.

Erzeugt von `scripts/ingest/bre/20-pruefpaket.py` (fester Zufallswert 147, das Paket ist reproduzierbar).
