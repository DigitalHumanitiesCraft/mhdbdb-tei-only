# Pruefseite #418 (hawe, type_117159), Runde 1 am 10.09.2026

- Reader-Deep-Link `?verseId=<wort_id>` (tei-text-reader.js scrollToVerseId) loest nur in
  Verstexten auf: data-core kommt aus `<l>` (verseCoreRange). Prosatexte (AC2, AC3, CEFB,
  DES2, KFB: `<l>`=0, nur `<lb>`) haben kein data-core, der Sprung warnt und bleibt oben.
  `?verse=<lb n>` ist kein Ersatz: lb@n wiederholt sich je Seite (AC2 1110 lb, 31 verschiedene n).
- Chargen-Prosa gegen die Basis messen, nicht gegen einen offenen PR: README/Seite beschrieben
  den Stand nach #416 (fix/198-lemma-2598-nom, AC3_23010_1 -> lemma_9644,
  fix-198-restfaelle.py), faelle.csv aber den Stand von origin/main (13x lemma_2598).
  Messung: `git grep -h type_117159 <ref> -- tei/ | grep -o 'lemmaRef="[^"]*"' | sort | uniq -c`.
- Kontext-Extraktion mit Zeichenfenster ueber Rohxml: XML-Reste per
  `re.search(r'[<>="]', links+rechts)` auf der CSV zaehlen (12 von 13), Wortzahl der
  sichtbaren Woerter gegen die Behauptung im Footer halten (9 bis 14 statt 28).
- Gegenprobe der Belege: lxml, `//t:w[@xml:id=...]`, 28 Tokens (w|pc) links/rechts,
  ancestor::l/@n fuer den Vers. Laufzeit ~2 min ueber 13 Belege (toks.index auf CEFB gross):
  im Hintergrund starten.
