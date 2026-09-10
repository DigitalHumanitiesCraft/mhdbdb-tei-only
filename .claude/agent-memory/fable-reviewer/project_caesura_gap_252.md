# Caesura-zu-gap-Migration #252 (Runde 1, 10.09.2026)

Gegenstand: uncommitteter Arbeitsbaum auf `claude/agents-setup-network-check-08f1ri`, Skript `scripts/migrate-caesura-to-gap-252.py`, 105 TEI-Dateien, Reader `case 'gap'`.

## Messungen, die wiederverwendbar sind

- Altzustand ohne stash: `git archive HEAD tei | tar -x -C <scratch>/head`, dann lxml darauf. Gruppen auf HEAD: A 972 (95 Dateien), B 155 (18), B' 5, C 12 (8 Dateien: EIL, FDS, FR1, GWTK, JT, MAI, MSG, WDB), Summe 1.144; A|B = 105 Dateien.
- Innere xml:id der Zielmenge: **1.413** (1.128 caesura + 285 pc), Doku/Docstring sagten 1.423. Zwei Wege: `git diff -U0 -- tei/ | grep '^-' | grep -o 'xml:id=' | wc -l` und lxml auf dem Archiv.
- WDD n=4 traegt zwei `<caesura/>` in einer Zeile (daher 1.128 zu 1.127).
- Entfernte `<pc>`-Texte: `( ) 129/129, &gt; 17, &lt; 7, ! , . je 1`. **`<` und `>` sind in GWTK/BRF/MR1 Redezeichen** (GWTK 970 lt / 963 gt pc im ganzen Text; BRF 8982 naechste Zeile `< waz danne ? > sprach her dietrîch`). `KLAMMER = [()<>\[\]]` behandelt sie als Auslassungsklammern.
- **793 Zeilen in 17 Dateien tragen nach der Migration noch `pc( caesura pc)` inline** (FR1 496, FR3 154, MSG 57, BRW 36, NEIC 22 ...), alle in Zeilen MIT `<w>`; 10 der 17 Dateien sind selbst unter den 105 migrierten. Die Verteilung im Issue-Body (FR1 543, MSG 57, BRW 39) ist diese inline-Menge, nicht die migrierte.
- Die 324/290 aus JOURNAL.md:1182 sind leere `<l>` (Gruppe A) gegen Linecode (OVG 135 = 135 `...`). Fuer die Gruppe-B-Siglen (BRF, GWTK, MR1, MR2, SJH, SUS, NEIC, NEIR) gibt es unter sources/linecode/ keine Quelle.
- caesura gesamt: vorher 53.081 in 253, nachher 51.953 in 224.
- Validierung der 105 mit lxml RelaxNG gegen schema/mhdbdb.rng: ~2 min, in den Hintergrund legen.
- build-corpus-index.py liest nur w und l (iterwalk :191), Frames ohne w werden verworfen (:197): darum ist der Index von Zeilen ohne `<w>` unabhaengig, ohne Rebuild pruefbar.

## Umgebung
- Kein `gh`; WebFetch auf github.com/.../issues/252 liefert nur den Body (keine Kommentare), api.github.com/.../comments per WebFetch 403.

## Runde 2 (10.09.2026, korrigiertes Kriterium `^\(\s*\)$`)

- Diff-Form per c14n-Vergleich aller 667 Dateien (HEAD-Archiv gegen Arbeitsbaum, Ziel-`<l>` im HEAD-Baum durch `<gap reason="lost"/>` ersetzt): 0 Abweichungen. Runde-1-Schaden vollstaendig zurueckgenommen.
- Zielmenge A 972 + B 122 = 1.094 in 103 Dateien, B' 38, C 12 in 8. Innere Elemente nur caesura 1.095 (WDD n=4 doppelt) + pc 244; ids 1.339, keine in api/ oder Indexen.
- **caesura danach: 51.986 in 225** (53.081 minus 1.095). Die 51.953/224 aus Runde 1 (minus 1.128) standen noch in TEI-MODEL.md:261/:653 und im Auftrag. Reader-Kommentar trug noch "1.127".
- Inline `( caesura )`: Rohmuster in `<l>` 844/17 (SJH 2, nicht 1; Liste in der Doku summiert 843), davon 6 in Zeilen ohne `<w>` (FR1 n=4, n=1, MSG 18 = Gruppe C; NEIC 14, NEIR 6, SJH 13 = B'). Streng zwischen Woertern: 838/17. Dazu 5 in `<p>` (HUB2 1, PL1 1, SUB1 3).
- B' 38 = 23 Zeilen mit `<`/`>` (24 Zeichen, GWTK 6658 hat zwei) + 6 Komma/Doppelpunkt (NEIR 6 `( ) ,`) + 8 einzelne Klammern + SJH lg168 n=13 `( ) !`. Klammerpaare: SJH lg179 6/7, SUS lg61 **6/10** (7-9 dazwischen sind jetzt gap), SUS lg127 7/8, SVW lg6 6/7.
- Skript prueft `find(T+'caesura')` = direkte Kinder: MUG lg5 n=7/8 (`<l><hi><caesura/></hi></l>`, Zeilen 1307/1312) fallen durch. Mit Nachfahren-Semantik 1.146 statt 1.144.
- 9 Dateien tragen gap UND inline: BRW FR1 FR3 MML MSG NEIC NEIM NEIR SGO. Kein Konsument ausser dem Reader liest caesura/gap (testing/, playground/ leer; hilfe-*.html beschreibt das `||`-Glyph nicht).
- Nuetzlich: Rohmuster `<pc[^>]*>\(</pc>\s*<caesura[^>]*/>\s*<pc[^>]*>\)</pc>` ueber den Text ist die schnellste Zaehlung; die B'-Liste druckt der Trockenlauf selbst.
