# Wortart-Disambiguierung Weingrüße (Phase 2)

Die Texte sind frühneuhochdeutsche Weingrüße und Weinsegen (Nürnberg, 15./16. Jh.): Gruß- und Segensformeln an den Wein ("Grüß dich got du edles getranck"), Lob, Trinkwünsche, derbe Komik. Jedes Wort hat sein Lemma schon (Spalte `lemma`, mittelhochdeutsche Lemmaform). Du bestimmst die Wortart (`@pos`) des Wortes **in diesem Satz**.

## Was du bekommst

Eine TSV-Datei. Spalte `kandidaten`: die Wortarten, die das Lexikon für das Lemma führt, getrennt durch ` | `. Kontext: ±5 Wörter, das Zielwort in `[eckigen Klammern]`.

## Tagset (docs/POS-TAGSET.md, 19 Tags)

NOM Substantiv, NAM Eigenname, ADJ Adjektiv, ADV Adverb, DET Artikel/Determinativ (der, diu, daz, ein, diser, kein), POS Possessivpronomen (mîn, dîn, sîn, unser, ir), PRO Pronomen (ich, du, er, ez, Relativpronomen, swer), PRP Präposition, NEG Negation, NUM Zahlwort, CNJ Konjunktion (Fallback), SCNJ unterordnende Konjunktion (daz im Nebensatz, ob, swenne, sît, als temporal), CCNJ nebenordnende Konjunktion (und, oder, aber, ouch, noch), IPA Fragepartikel, VRB Vollverb (auch haben/sîn/werden als Vollverb oder Kopula), VEX Hilfsverb (haben/sîn/werden mit Partizip II), VEM Modalverb (müezen, suln, kunnen, mügen, wellen, dürfen mit Infinitiv), INJ Interjektion, DIG römische Zahl.

## Regeln

- Wähle einen Tag aus `kandidaten`. Ausnahme: steht `CNJ` unter den Kandidaten, darfst du `CCNJ` oder `SCNJ` wählen, wenn die Art der Konjunktion im Satz klar ist; sonst `CNJ`.
- Immer genau ein Tag, nie zwei.
- Personalpronomen-Lemma (ich, dû, er, sie, wir, ir): die Pronomenform (du, dich, dir, er, im, in) → `PRO`; die besitzanzeigende Form vor einem Substantiv oder für es stehend (mein, dein, sein, ir kel) → `POS`. `DET` nur, wenn das Wort wirklich als Artikel steht.
- haben/sîn/werden: mit Partizip II (ist gewesen, hast getrunken, wirt geben) → `VEX`; sonst (Kopula "du bist gut", "selig sei", Besitz "ich hab", Passiv-Zukunft ohne Partizip) → `VRB`.
- Modalverben: mit Infinitiv → `VEM`; ohne Infinitiv (ich mag den wein = ich mag ihn gern) → `VRB`.
- ADJ / ADV / NOM: Attribut oder Prädikativ → `ADJ`; bestimmt ein Verb oder Adjektiv näher → `ADV`; als Substantiv gebraucht (der alte, mein lieber als Anrede ohne Substantiv) → `NOM`.
- ein: unbestimmter Artikel → `DET`, Zahl "eins" → `NUM`.
- Präposition mit Nominalgruppe → `PRP`; ohne (Verbpartikel, "dar an", "her ein") → `ADV`.
- daz/der/die als Artikel oder Demonstrativ → `DET`; daz als Nebensatzeinleiter → `SCNJ` (wenn `CNJ` Kandidat ist).
- Rubriken stehen nicht in den Daten; Überschriften sind schon ausgeschlossen.
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
