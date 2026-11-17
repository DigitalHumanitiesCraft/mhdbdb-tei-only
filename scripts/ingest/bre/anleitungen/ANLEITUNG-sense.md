# Bedeutungs-Disambiguierung Weingrüße (Phase 3)

Die Texte sind frühneuhochdeutsche Weingrüße und Weinsegen (Nürnberg, 15./16. Jh.): Gruß- und Segensformeln an den Wein ("Grüß dich got du edles getranck"), Lob, Trinkwünsche, derbe Komik. Jedes Wort hat sein Lemma schon (Spalte `lemma`, mittelhochdeutsche Lemmaform). Du wählst die Bedeutung (Sense) des Lemmas, die **in diesem Satz** gemeint ist.

## Was du bekommst

Eine TSV-Datei. Spalte `kandidaten`: die Bedeutungen des Lemmas im Lexikon, getrennt durch ` | `, je Bedeutung `sense_id :: Konzepte (deutsch und englisch)`. Die Konzepte beschreiben die Bedeutung, es gibt keine Definitionen. Kontext: ±5 Wörter, das Zielwort in `[eckigen Klammern]`.

## Regeln

- Wähle eine `sense_id` aus `kandidaten`. Erfinde keine.
- Entscheide nach dem Sinn im Satz: welches Konzept beschreibt, was das Wort hier bedeutet? Bei Funktionswörtern (Pronomen, Hilfsverben, Präpositionen) hat oft ein Sense das Konzept "Funktionswörter (Functional Words)": er gilt, wenn das Wort grammatisch gebraucht ist (wellen als Futur- oder Modalhilfe, haben als Hilfsverb).
- Haben zwei Kandidaten genau dieselbe Konzeptliste und passen beide, dann `abstain`.
- `abstain`, wenn keine Bedeutung passt oder der Kontext nicht reicht. abstain ist eine gültige Antwort: es wird dann nichts geschrieben.
- `begruendung`: höchstens 15 Wörter, deutsch, eigene Worte, **kein Zitat aus Ausgaben, Übersetzungen oder Kommentaren**. Beispiele: "Wille, nicht Hilfsverb", "Wein als Getränk", "räumlich".
- `confidence`: `high` (eindeutig), `medium` (wahrscheinlich), `low` (unsicher).
- Einzeltextseiten mit der Synopse der anderen Zeugen (Paralleltext) liegen im Cache: `temp/bre-wiki/rev_<revid>.json` (Feld `inhalt`), die `revid` zum Titel steht in `ingest/bre/revisionen.tsv`. Nur bei Unsicherheit nachsehen. Sonst lies keine anderen Dateien als diese Anleitung und deine Eingabedatei, schreibe nur die eine Ausgabedatei mit dem Write-Tool. Keine Skripte, keine Änderungen am Repo.

## Ausgabe bulk (eine Zeile je Lemma)

TSV, UTF-8, Kopfzeile genau: `schluessel	resolved_sense	confidence	ausnahmen	begruendung`

- `schluessel`: wie in der Eingabe, gleiche Reihenfolge, jede Eingabezeile genau einmal.
- `resolved_sense`: die sense_id, die für das Lemma in diesen Texten im Allgemeinen gilt (alle nicht gezeigten Belege bekommen sie auch). `SPLIT`, wenn die gezeigten Belege zu einem erheblichen Teil (etwa ein Fünftel oder mehr) verschiedene Bedeutungen verlangen: dann wird jedes Token einzeln entschieden. `abstain`, wenn keine passt.
- `ausnahmen`: einzelne gezeigte Belege mit anderer Bedeutung: `xml_id=sense_id` getrennt durch `;` (auch `xml_id=abstain`). Sonst leer.

## Ausgabe instance (eine Zeile je Token)

TSV, UTF-8, Kopfzeile genau: `xml_id	resolved_sense	confidence	begruendung`

- jede Eingabezeile genau einmal, gleiche Reihenfolge.

Tabs nur als Spaltentrenner, keine Tabs oder Zeilenumbrüche in Feldern. Melde am Ende: Zahl der Zeilen, Zahl `SPLIT`, Zahl `abstain`.
