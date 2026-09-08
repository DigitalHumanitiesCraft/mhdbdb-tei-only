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
