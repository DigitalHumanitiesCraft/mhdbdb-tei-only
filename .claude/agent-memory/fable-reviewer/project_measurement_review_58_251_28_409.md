# Messreview ohne Diff: #58, #251, #28, #409 (08.09.2026)

- **Klon ist shallow mit Wurzel 4458686ab** (`git log` ab HEAD: 63 Commits), aber aeltere Objekte sind ueber
  b02596af1 erreichbar (`git log b02596af1 | wc -l` = 900). Fuer Historie also von einer alten SHA aus loggen,
  nicht von HEAD. `4458686ab^` existiert nicht.
- **revisionDesc-Eintraege tragen die je-Datei-Zahlen der Serien** (`#216 Serie 1 (minne): N Tokens`,
  `#369 Serie 2 (stat): N Tokens`). Damit lassen sich fremde Zaehlungen vor dem 24.08. schliessen:
  KZW-Zahl = Stand bb5ef386b^ + #216-Eintrag (DFL 10, KLA 3, NBB 37, RAB 1, AT 0), aufs Token exakt.
  #368 (17:31) und #372 (19:59) liegen am selben Tag; „vor dem 24.08." ist zu grob.
- **Dokumentsuche zeigt seit dem aeltesten Stand (7f2922e1a, 2025-10-02) `totalWords`** als Zahl.
  Trefferwoerter je Lemma standen nur bis a51f47196 (2025-10-05) als Detail-Meta; #327 (b02596af1) hat nur
  den toten Schreiber und die verwaisten Formatter entfernt, keine Anzeige geaendert.
- `ingest/foreign-lang/28-gleis1-kandidaten.csv`: Semikolon + BOM (`utf-8-sig`, `delimiter=';'`).
  2.677 ja = 2.636 belegt + 41 unbelegt; 2.675 = pos-Kriterium (ART vor NAM bei lemma_3141, lemma_46979).
- gebrechen-Familie: Sense-4-Mengen identisch, aber Senses 1 bis 3 der Ableitungen sind identisch oder
  Teilmengen der gebrechen-Senses (engebrechen 3 von 4 identisch). engebrechen/gebrechenhaft je 1 Token.

## Fix-Review #58 Belegzahl (11.09.2026, Branch claude/58-belegzahl-dokumentsuche)

- **`arm` ist ein Homograph, und Vorher-Zahlen von der Live-Seite gehoeren zum Lemma, das dort wirklich
  aufgeloest wurde.** Alte Kopfzeile = Summe `wordCount` der Treffertexte. 6.418.133 ist diese Summe fuer
  lemma_285 (Adjektiv, 207 Texte); lemma_286 (Koerperteil, 40 Texte) ergibt 2.195.030. Auftrag und
  Commit-Message hatten die 285-Zahl dem 286-Fall zugeschrieben. Messung: Python ueber corpus-index.json.gz,
  Skript-Muster: alle Texte mit allen Ids, `sum(len(lemmata[...]))` und `sum(wordCount)`.
- Korpus-Index v4.2.15: 513.673 Lemma-Schluessel in `texts[].lemmata`, alle mit `lemma_`-Praefix, 0 leere
  Positionslisten. `containsAll` prueft Array-Truthiness, eine leere Liste zaehlte also als „vorhanden".
- `docs/CONTRACTS.md` §C traegt die Objektform, die `searchDocumentUsingEnhancedIndex` pusht, samt Satz
  „What the result card shows is …". Bei jeder Aenderung an diesem Objekt dort nachsehen.
- **Alans Protokoll (#419) steht nur im PDF-Anhang**, der per API 403 liefert; Thread-Text (Body + 5
  Kommentare am 11.09.) nennt die Dokumentsuche-Zahl nicht. „unabhaengig getroffen in #419" ist damit
  aus dem Repo nicht pruefbar. KZW-Zitat „11250 Arme (Koerperteile) im CEFB kann nicht sein" steht
  woertlich in #58 (wachauer, 2026-09-08 15:09 UTC).
- Teillauf einer Spec auf Windows: `node scripts/run-tests.js <spec>` mit Redirect in eine Scratch-Datei,
  im Hintergrund; 15 Tests bei 13 `test(`-Aufrufen, weil einer in einer 3er-Schleife steht.
