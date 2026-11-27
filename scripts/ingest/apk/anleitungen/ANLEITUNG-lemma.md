# Lemma-Disambiguierung Hesler-Apokalypse (Phase 1b)

Der Text ist die Apokalypse Heinrichs von Hesler: eine mittelhochdeutsche Versdichtung des Deutschen Ordens (um 1300, ostmitteldeutsch), die die Offenbarung des Johannes nacherzählt und Stück für Stück geistlich auslegt. Gott, Christus, das Lamm, Engel, Posaunen, Siegel, der Antichrist, die Christenheit, Sünde und Gericht. Überliefert in der Danziger Handschrift, hier in der Schreibung der Ausgabe von Karl Helm (1907), ohne Längenzeichen und Umlautzeichen. Das Lexikon (MHDBDB) führt die Lemmata in normalisierter mittelhochdeutscher Form.

## Was du bekommst

Eine TSV-Datei. Spalte `kandidaten`: die Lemmata, auf die die Wortform im Lexikon passen kann, getrennt durch ` | `. Je Kandidat: `lemma_N`, Lemmaform, `[Wortarten]`, `{Konzepte der ersten Bedeutung}`, `n=` Zahl der Belege dieser Form für dieses Lemma im übrigen Korpus. `n` ist ein Hinweis auf die übliche Lesart, keine Entscheidung. Manche Kandidaten sind Rauschen alter Fehlannotationen (kleines n, unpassende Bedeutung).

Kontext: ±5 Wörter, das Zielwort in `[eckigen Klammern]`. Die Spalte `text` nennt den Vers (`V. 1234`).

## Regeln

- Wähle nur unter den Kandidaten der Zeile. Erfinde keine Lemma-ID.
- Ostmitteldeutsche Schreibung gegen normalisiertes Mittelhochdeutsch: `vor-` = `ver-` (vorendet = verendet), `ir-` = `er-` (irkant = erkant), `o` ~ `u` (dorch = durch), `u` ~ `uo`, `üe`, `iu`, `ü` (gut = guot, ubir = über), `i` ~ `î`, `ie` (min = mîn, di = die/diu), `e` ~ `æ`, `ë`, `ö` (were = wære), keine Diphthongierung (hus = hûs, uz = ûz, sin = sîn), `z`/`s`/`zz` ~ `ʒ` (daz, iz = ez, waz).
- **`her` ist im Ostmitteldeutschen meist das Personalpronomen `er`** (her sprach, als her sach). Nur wo der Sinn es verlangt, ist `her` das Adverb (hierher) oder `hêrre`.
- Possessivpronomen stehen in der MHDBDB beim Personalpronomen: min/mines → `ich`, din → `dû`, sin (= seine Sache) → `er` bzw. `ez`, unser → `wir`. `sin`, `sint`, `si`, `ist` als Verb (esse) → `sîn` [VEX/VRB].
- **`ir` ist im Text gemischt.** Possessiv oder Genitiv/Dativ der 3. Person (ihr, ihre, von ihnen, ihnen: "ir wille" der Christenheit, "ir aller houbet", "Crist ir den namen liez") → ein Lemma `sie`. Anrede, 2. Person Plural ("sult ir", "ir guten") → das Lemma `ir`. Zeigen die Belege beides in nennenswertem Umfang, ist die Antwort `SPLIT`, nicht das häufigere von beiden.
- `in`, `im`, `en` kann Präposition (`in` PRP) oder Pronomen sein (= ihn, ihnen, ihm → `er` bzw. `sie`). `im` = "in dem" → das Lemma der Kontraktion, wenn es Kandidat ist.
- `wen`, `wan` = denn, weil, außer (`wan`/`wande` CNJ) oder = wenn (`wanne`, `swenne`); achte auf die Kandidaten.
- `do` = dô (da, damals, als), `dan` = dannen/danne (von dort, dann, als nach Komparativ), `sus` = sus/sô (so).
- `abstain`, wenn keiner der Kandidaten passt (das Wort ist dann etwas, das im Lexikon fehlt) oder der Kontext nicht reicht.
- `begruendung`: höchstens 15 Wörter, deutsch, eigene Worte. **Kein Zitat aus Ausgaben, Übersetzungen oder Kommentaren.** Formulierungen wie "Personalpronomen, omd. her", "Possessiv zu ich", "Präposition vor Dativ", "Verb, Infinitiv nach wil" genügen.
- `confidence`: `high` (eindeutig), `medium` (wahrscheinlich), `low` (unsicher, aber besser als nichts).
- Lies keine anderen Dateien als diese Anleitung und deine Eingabedatei, schreibe nur die eine Ausgabedatei mit dem Write-Tool. Keine Skripte, keine Änderungen am Repo.

## Ausgabe bulk (eine Zeile je Wortform)

TSV, UTF-8, Kopfzeile genau: `schluessel	resolved_lemma	confidence	ausnahmen	begruendung`

- `schluessel`: wie in der Eingabe, gleiche Reihenfolge, jede Eingabezeile genau einmal.
- `resolved_lemma`: die Lemma-ID, die für die Form im Allgemeinen gilt (alle nicht gezeigten Belege bekommen sie auch). `SPLIT`, wenn die gezeigten Belege zu einem erheblichen Teil (etwa ein Fünftel oder mehr) verschiedene Lemmata verlangen: dann wird jedes Token einzeln entschieden. `abstain`, wenn keiner passt.
- `ausnahmen`: einzelne gezeigte Belege, die ein anderes Lemma verlangen als `resolved_lemma`: `xml_id=lemma_N` getrennt durch `;` (auch `xml_id=abstain`). Sonst leer.

## Ausgabe instance (eine Zeile je Token)

TSV, UTF-8, Kopfzeile genau: `xml_id	resolved_lemma	confidence	begruendung`

- jede Eingabezeile genau einmal, gleiche Reihenfolge; `resolved_lemma` eine Kandidaten-ID oder `abstain`.

Tabs nur als Spaltentrenner, keine Tabs oder Zeilenumbrüche in Feldern. Melde am Ende: Zahl der Zeilen, Zahl `SPLIT`, Zahl `abstain`.
