# Lemma-Disambiguierung Weingrüße (Phase 1b)

Die Texte sind frühneuhochdeutsche Weingrüße und Weinsegen (Nürnberg, 15./16. Jh., meist Hans Rosenplüt zugeschrieben; Handschriften und Drucke). Gruß- und Segensformeln an den Wein ("Grüß dich got du edles getranck"), Lob, Trinkwünsche, derbe Komik. Das Lexikon (MHDBDB) ist mittelhochdeutsch: Lemmata stehen in normalisierter mhd. Form.

## Was du bekommst

Eine TSV-Datei. Spalte `kandidaten`: die Lemmata, auf die die Wortform im Lexikon passen kann, getrennt durch ` | `. Je Kandidat: `lemma_N`, Lemmaform, `[Wortarten]`, `{Konzepte der ersten Bedeutung}`, `n=` Zahl der Belege dieser Form für dieses Lemma im übrigen (meist mhd.) Korpus. `n` ist ein Hinweis auf die übliche Lesart, keine Entscheidung. Manche Kandidaten sind Rauschen alter Fehlannotationen (kleines n, unpassende Bedeutung).

Kontext: ±5 Wörter, das Zielwort in `[eckigen Klammern]`.

## Regeln

- Wähle nur unter den Kandidaten der Zeile. Erfinde keine Lemma-ID.
- Frühneuhochdeutsche Schreibung gegen mhd. Lemma: ei ~ î (mein = mîn, sein = sîn), au ~ û, eu/äu ~ iu, ie ~ ie/i, a ~ â, o ~ ô, ü ~ uo/üe, ß/sz/s ~ ʒ/z; b/p, d/t, g/k wechseln (pir = bier, prunnen = brunnen).
- Possessivpronomen stehen in der MHDBDB beim Personalpronomen: mein/meyn → `ich`, dein → `dû`, sein (= seine Sache) → `er` (bzw. `ez`), unser → `wir`. "sein/sey/sei" als Verb (esse) → `sîn` [VEX/VRB].
- "in/yn/im" kann Präposition (`in` PRP) oder Pronomen sein (= ihn/ihnen/ihm → `er` bzw. `sie`). "wann/wan" = denn/weil oder wenn: `wan`/`wande` [CNJ] gegen `wanne` usw.; achte auf die Kandidaten.
- "im/ym" = "in dem" (im bett, im mayen) → `lemma_10734` ime: das Lexikon führt die Kontraktion aus in + der als eigenes Lemma (Bestandteile der und in). "im/ym" = "ihm" → `er`.
- `abstain`, wenn keiner der Kandidaten passt (das Wort ist dann etwas, das im Lexikon fehlt) oder der Kontext nicht reicht.
- Einzeltextseiten mit der Synopse der anderen Zeugen (Paralleltext) liegen im Cache: `temp/bre-wiki/rev_<revid>.json` (Feld `inhalt`, Wikitext), die `revid` zum Titel steht in `ingest/bre/revisionen.tsv`. Nur bei Unsicherheit nachsehen.
- `begruendung`: höchstens 15 Wörter, deutsch, eigene Worte. **Kein Zitat aus Ausgaben, Übersetzungen oder Kommentaren.** Formulierungen wie "Possessiv zu ich", "Präposition vor Dativ", "Verb, Infinitiv nach wil" genügen.
- `confidence`: `high` (eindeutig), `medium` (wahrscheinlich), `low` (unsicher, aber besser als nichts).
- Lies keine anderen Dateien als die genannten, schreibe nur die eine Ausgabedatei. Keine Skripte, keine Änderungen am Repo.

## Ausgabe bulk (eine Zeile je Wortform)

TSV, UTF-8, Kopfzeile genau: `schluessel	resolved_lemma	confidence	ausnahmen	begruendung`

- `schluessel`: wie in der Eingabe, gleiche Reihenfolge, jede Eingabezeile genau einmal.
- `resolved_lemma`: die Lemma-ID, die für die Form im Allgemeinen gilt (alle nicht gezeigten Belege bekommen sie auch). `SPLIT`, wenn die gezeigten Belege zu einem erheblichen Teil (etwa ein Fünftel oder mehr) verschiedene Lemmata verlangen: dann wird jedes Token einzeln entschieden. `abstain`, wenn keiner passt.
- `ausnahmen`: einzelne gezeigte Belege, die ein anderes Lemma verlangen als `resolved_lemma`: `xml_id=lemma_N` getrennt durch `;` (auch `xml_id=abstain`). Sonst leer.

## Ausgabe instance (eine Zeile je Token)

TSV, UTF-8, Kopfzeile genau: `xml_id	resolved_lemma	confidence	begruendung`

- jede Eingabezeile genau einmal, gleiche Reihenfolge; `resolved_lemma` eine Kandidaten-ID oder `abstain`.

Tabs nur als Spaltentrenner, keine Tabs oder Zeilenumbrüche in Feldern. Melde am Ende: Zahl der Zeilen, Zahl `SPLIT`, Zahl `abstain`.
