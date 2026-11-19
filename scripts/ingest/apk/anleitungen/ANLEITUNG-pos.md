# Wortart-Disambiguierung Hesler-Apokalypse (Phase 2)

Der Text ist die Apokalypse Heinrichs von Hesler: eine mittelhochdeutsche Versdichtung des Deutschen Ordens (um 1300, ostmitteldeutsch), die die Offenbarung des Johannes nacherzählt und geistlich auslegt. Schreibung der Danziger Handschrift nach Helm (1907), ohne Längen- und Umlautzeichen; `her` ist meist das Pronomen `er`, `vor-` steht für `ver-`, `ir-` für `er-`. Jedes Wort hat sein Lemma schon (Spalte `lemma`, mittelhochdeutsche Lemmaform). Du bestimmst die Wortart (`@pos`) des Wortes **in diesem Satz**.

## Was du bekommst

Eine TSV-Datei. Spalte `kandidaten`: die Wortarten, die das Lexikon für das Lemma führt, getrennt durch ` | `. Kontext: ±5 Wörter, das Zielwort in `[eckigen Klammern]`.

## Tagset (docs/POS-TAGSET.md, 19 Tags)

NOM Substantiv, NAM Eigenname, ADJ Adjektiv, ADV Adverb, DET Artikel/Determinativ (der, diu, daz, ein, diser, kein), POS Possessivpronomen (mîn, dîn, sîn, unser, ir), PRO Pronomen (ich, du, er, ez, Relativpronomen, swer), PRP Präposition, NEG Negation, NUM Zahlwort, CNJ Konjunktion (Fallback), SCNJ unterordnende Konjunktion (daz im Nebensatz, ob, swenne, sît, als temporal), CCNJ nebenordnende Konjunktion (und, oder, aber, ouch, noch), IPA Fragepartikel, VRB Vollverb (auch haben/sîn/werden als Vollverb oder Kopula), VEX Hilfsverb (haben/sîn/werden mit Partizip II), VEM Modalverb (müezen, suln, kunnen, mügen, wellen, dürfen mit Infinitiv), INJ Interjektion, DIG römische Zahl.

## Regeln

- Wähle einen Tag aus `kandidaten`. Ausnahme: steht `CNJ` unter den Kandidaten, darfst du `CCNJ` oder `SCNJ` wählen, wenn die Art der Konjunktion im Satz klar ist; sonst `CNJ`.
- Immer genau ein Tag, nie zwei.
- Personalpronomen-Lemma (ich, dû, er, sie, wir, ir): die Pronomenform (du, dich, dir, her, er, im, in, sie) → `PRO`; die besitzanzeigende Form vor einem Substantiv oder für es stehend (min, din, sin, ir) → `POS`. `DET` nur, wenn das Wort wirklich als Artikel steht.
- haben/sîn/werden: mit Partizip II (ist gewesen, hat gesehen, wart gegeben) → `VEX`; sonst (Kopula "her ist gut", Besitz "ich han", Passiv mit Adjektiv) → `VRB`.
- Modalverben: mit Infinitiv → `VEM`; ohne Infinitiv → `VRB`.
- ADJ / ADV / NOM: Attribut oder Prädikativ → `ADJ`; bestimmt ein Verb oder Adjektiv näher → `ADV`; als Substantiv gebraucht (der gute, die heiligen) → `NOM`.
- ein: unbestimmter Artikel → `DET`, Zahl "eins" → `NUM`.
- Präposition mit Nominalgruppe → `PRP`; ohne (Verbpartikel, "dar an", "her in") → `ADV`.
- daz/der/die als Artikel oder Demonstrativ → `DET`; daz als Nebensatzeinleiter → `SCNJ` (wenn `CNJ` Kandidat ist).
- Die Rubrik ist schon ausgeschlossen.
- `abstain`, wenn keiner der Kandidaten passt (dann ist meist das Lemma falsch) oder der Kontext nicht reicht.
- `begruendung`: höchstens 15 Wörter, deutsch, eigene Worte, **kein Zitat aus Ausgaben, Übersetzungen oder Kommentaren**. Beispiele: "Possessiv vor Substantiv", "Hilfsverb mit Partizip", "Kopula".
- `confidence`: `high` (eindeutig), `medium` (wahrscheinlich), `low` (unsicher).
- Lies keine anderen Dateien als diese Anleitung und deine Eingabedatei, schreibe nur die eine Ausgabedatei mit dem Write-Tool. Keine Skripte, keine Änderungen am Repo.

## Ausgabe bulk (eine Zeile je Gruppe = Lemma und Form)

TSV, UTF-8, Kopfzeile genau: `schluessel	resolved_pos	confidence	ausnahmen	begruendung`

- `schluessel`: wie in der Eingabe, gleiche Reihenfolge, jede Eingabezeile genau einmal.
- `resolved_pos`: der Tag, der für die Gruppe im Allgemeinen gilt (alle nicht gezeigten Belege bekommen ihn auch). `SPLIT`, wenn die gezeigten Belege zu einem erheblichen Teil (etwa ein Fünftel oder mehr) verschiedene Tags verlangen: dann wird jedes Token einzeln entschieden. `abstain`, wenn keiner passt.
- `ausnahmen`: einzelne gezeigte Belege mit anderem Tag: `xml_id=TAG` getrennt durch `;` (auch `xml_id=abstain`). Sonst leer.

## Ausgabe instance (eine Zeile je Token)

TSV, UTF-8, Kopfzeile genau: `xml_id	resolved_pos	confidence	begruendung`

- jede Eingabezeile genau einmal, gleiche Reihenfolge.

Tabs nur als Spaltentrenner, keine Tabs oder Zeilenumbrüche in Feldern. Melde am Ende: Zahl der Zeilen, Zahl `SPLIT`, Zahl `abstain`.
