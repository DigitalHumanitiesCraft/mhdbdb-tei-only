# APK: Apokalypse Heinrichs von Hesler (#262)

Ostmitteldeutsche Versdichtung des Deutschen Ordens (um 1300): Nacherzählung und Auslegung der Offenbarung des Johannes, 23.254 Verse. Vorlage ist `apk_free.xml`, die TEI-Fassung des Mittelhochdeutschen Textarchivs (MHGTA, Electronic Text Center der University of Virginia, 2002) nach der Ausgabe von Karl Helm (Deutsche Texte des Mittelalters 8, Berlin 1907). Im Textarchiv des Mittelhochdeutschen Wörterbuchs heißt der Text `HeslApk`.

## Quelle und Rechte

Die Rohdatei kommt nicht ins Repository, auch nicht in Teilen als Testfixture. Sie liegt im DHCraft-Drive unter `Projekte/mhdbdb/extern/` (Eintrag in `sources/INVENTAR-ARCHIV.md`) und lokal unter `sources/hesler-apokalypse/apk_free.xml` (gitignoriert). `apk_common.rohdatei()` prüft Größe (1.565.852 Bytes) und SHA-256 (`6d8ebb25…e7da`). Unter `.claude/worktrees/` sucht sie auch im Main Worktree.

Ob der Text aufgenommen werden darf, ist offen: Ute Recker-Hamm (MWB Trier) soll den Ingest vorher sehen (#262). Bis dahin liegt alles in `ingest/apk/`, nichts in `tei/` oder `authority-files/`.

## Skripte

| Skript | Was es tut | Schreibt |
|---|---|---|
| `01-convert-apk-to-mhdbdb.py` | Stufe 0: TEI.2 der Vorlage nach MHDBDB-TEI, mit Bestands-, Vers-, Wort-, Satzzeichen- und Stilbilanz und Validierung gegen `schema/mhdbdb.rng`. `--trocken` prüft ohne zu schreiben, eine schon annotierte Ausgabe ersetzt nur `--ueberschreiben` | `ingest/apk/APK.tei.xml` |
| `10-lemma-assign.py` | Phase 1: Auto-Match der Wortformen gegen `variants.xml`, `@lemmaRef` bei genau einem Kandidaten, die mehrdeutigen nach Stufen | `ingest/apk/phase1/lemma-pending.tsv`, `lemma-unmatched.tsv` |
| `11-batches.py` | Schneidet die Pending-TSV einer Phase in LLM-Batches zu 50 Zeilen (`temp/apk-batches/`, gitignoriert). `--nur` mit `--stufe instance` schneidet alle Tokens der genannten Gruppen (für SPLIT) | |
| `12-entscheidungen.py` | Sammelt die LLM-Antworten (`temp/apk-entscheidungen/`), prüft sie gegen die Kandidaten, schreibt Bulk- und Patch-Tabelle mit `decision_type`, `confidence`, `reviewer` | `ingest/apk/phaseN/<phase>-bulk.tsv`, `-patch.tsv` |
| `13-lemma-apply.py` | Phase 1: `@lemmaRef` aus Bulk und Patch | TEI |
| `14-pos-assign.py` | Phase 2: Wortart vom Lemma, bei genau einem Kandidaten direkt | TEI, `phase2/pos-pending.tsv` |
| `15-apply.py` | Phase 2 und 3: `@pos` oder `@ana` aus Bulk und Patch | TEI |
| `16-sense-assign.py` | Phase 3: Sense bei genau einem Kandidaten direkt, sonst Kandidaten mit Konzeptlabels | TEI, `phase3/sense-pending.tsv` |
| `18-corresp.py` | Phase 3: `@corresp` auf den Variantentyp, nur bei genau einem Treffer | TEI, `phase3/corresp-mehrdeutig.tsv` |
| `20-pruefpaket.py` | Prüfpaket: alle low-Zeilen, dazu eine Stichprobe der medium-Zeilen je Phase | `ingest/apk/pruefung/*.tsv` |
| `21-abdeckung.py` | Abdeckung je Attribut mit Nenner, prüft Referenzen, Tagset, `@ana` passend zu `@lemmaRef`, `<head>` unannotiert, Schema | |
| `22-header-stand.py` | Schreibt die gemessene Abdeckung in `normalization` und eine `change`-Zeile in den Header. Ein zweiter Lauf auf demselben Stand mit demselben `--datum` ändert nichts | TEI |
| `apk_common.py`, `apk_annot.py` | Pfade, Rohdatei-Prüfung, Helfer der Phasen (übertragen aus `scripts/ingest/bre/`) | |
| `test_apk.py` | Tests für Stufe 0 an einer erfundenen Mini-Fixture, dazu die Versbilanz an der echten Datei, wenn sie da ist (sonst SKIP) | |
| `anleitungen/ANLEITUNG-*.md` | Anleitungen für die LLM-Batches je Phase | |

Die Phasen 1 bis 3 folgen dem BRE-Lauf (`scripts/ingest/bre/README.md`): keine neuen Lemmata oder Senses, keine Änderung an `lexicon.xml`, `abstain` wird nicht geschrieben, kein `@ana` ohne `@lemmaRef`, `@corresp` nur bei genau einem Treffer.

```
python -P -E scripts/ingest/apk/01-convert-apk-to-mhdbdb.py --datum 2026-11-19
python -P -E scripts/ingest/apk/test_apk.py
python -P -E scripts/ingest/apk/10-lemma-assign.py
python -P -E scripts/ingest/apk/11-batches.py --phase lemma --stufe bulk
python -P -E scripts/ingest/apk/11-batches.py --phase lemma --stufe instance
#   LLM-Batches, Ausgaben nach temp/apk-entscheidungen/lemma-{bulk,instance}-NN.tsv
python -P -E scripts/ingest/apk/11-batches.py --phase lemma --stufe instance --praefix split- --nur <SPLIT-Schluessel>
#   LLM-Batches, Ausgaben nach temp/apk-entscheidungen/lemma-split-NN.tsv
python -P -E scripts/ingest/apk/12-entscheidungen.py --phase lemma --reviewer llm:claude-sonnet-5-5
python -P -E scripts/ingest/apk/13-lemma-apply.py
#   Phase 2 und 3 entsprechend: 14 bzw. 16, 11, 12, 15 --phase pos|sense; danach 18, 21, 22, 20
```

## Lauf vom 19.11.2026

Alle LLM-Entscheidungen: Claude Sonnet (`reviewer` = `llm:claude-sonnet-5-5`), Batches zu 50 Zeilen, je Batch eine Stichprobe des Orchestrators an den Belegen.

| Phase | eindeutig aus dem Lexikon | mehrdeutig | davon gesetzt | abstain | offen |
|---|---|---|---|---|---|
| 1 Lemma | 58.324 von 115.566 | 52.456 | 51.917 | 207 | 332 Hapaxe, ohne Treffer im Lexikon 4.786 |
| 2 Wortart | 55.586 von 110.241 | 54.655 | 39.089 | 312 | 1.329 Hapaxe, 13.925 aus SPLIT-Gruppen |
| 3 Bedeutung | 77.134 von 110.241 | 33.107 | 23.451 | 306 | 336 Hapaxe, 9.014 aus SPLIT-Gruppen |

Die Zahlen geben `10-lemma-assign.py`, `13-lemma-apply.py`, `14-pos-assign.py`, `16-sense-assign.py` und `15-apply.py` aus. In Phase 1 sind alle 144 SPLIT-Gruppen (4.978 Tokens) je Token entschieden (`lemma-split-NN`). In Phase 2 und 3 nicht: das wären 22.939 Tokens in rund 460 Batches, und ein Teil der SPLIT-Gruppen in Phase 3 geht nach den Begründungen auf falsche Lemmata zurück, die zuerst die Prüfung klären sollte. Der Nachlauf:

```
python -P -E scripts/ingest/apk/11-batches.py --phase pos --stufe instance --praefix split- --nur <SPLIT-Schluessel aus phase2/pos-bulk.tsv>
#   Ausgaben nach temp/apk-entscheidungen/pos-split-NN.tsv, dann 12 und 15 --phase pos; fuer sense ebenso
```

Eingriffe des Orchestrators, alle in den Arbeitsdateien unter `temp/` vor `12-entscheidungen.py`:

- **`ir` auf SPLIT gesetzt** (Phase 1, `lemma-bulk-01`): Die zwölf Belege des Batches zeigten nur das Possessiv der 3. Person, eine zweite Stichprobe aus 15 Belegen enthielt drei Anreden („sult ir“). Die Form wurde danach je Token entschieden. Der erste Lauf von `lemma-bulk-01` war zuvor verworfen worden, weil die Anleitung `ir` unklar regelte. Die Regel ist in `ANLEITUNG-lemma.md` präzisiert.
- **Formfehler mechanisch behoben**, Inhalt unverändert: drei fehlende Tabs (`lemma-instance-01`, `-02`, `-06`), zwei vertippte xml_ids in derselben Zeile wie ihre Eingabe (`lemma-instance-03`, `lemma-split-69`) und sieben Ausnahmen, deren xml_id nicht unter den Belegen der Zeile stand und für die genau ein Beleg desselben Verses in Frage kam (`lemma-bulk-04`, `-09`, `-10`, `pos-bulk-08`, `-10`, `-26`, `sense-bulk-05`).

Nicht versioniert sind die LLM-Ausgaben selbst (`temp/`), versioniert sind die Entscheidungstabellen in `ingest/apk/phase1/` bis `phase3/`.

## Abbildung (Stufe 0)

| Vorlage (`apk_free.xml`) | MHDBDB-TEI | Begründung |
|---|---|---|
| CSS-Vorspann vor dem Doctype, Doctype `mhg-tei.dtd` | entfällt | Darstellungsanweisung des Textarchivs, kein Text. Der Block muss mit `@namespace html` beginnen und darf kein `<` enthalten, sonst bricht der Konverter ab |
| `teiHeader` (AACR2) | neuer Header nach dem Muster von `tei/BIB.tei.xml` | Projektleitung Akademie Mainz, digitale Erfassung Kompetenzzentrum Trier, TEI-Auszeichnung ETC 2002 als `bibl type="digitalIntermediary"`. Werk, Person und Gattung als `TBD`, Vorschlag in `ingest/apk/normdaten-vorschlag.md` |
| `div1` | `div` | |
| `lg1/head` (Rubrik „Dys ist Apokalipsis.“) | `head`, Token `APK_0_i` | unannotiert wie in den anderen Ingests |
| `lg2` (415) | `div type="section"` | Abschnitte der Ausgabe |
| `l n id` (23.254) | `l n` | die id ist aus n ableitbar (`Apk-00001`), der Konverter prüft das und dass die Zählung lückenlos von 1 an läuft |
| `pb n` (342) | `pb type="edition" n` | Seiten der Ausgabe Helm |
| `fw type="folio"` (706) | `cb type="manuscript" n` | Blatt und Spalte der Handschrift, die die Ausgabe am Rand führt. `n` ist der Text in der eckigen Klammer (`[1ra]` wird `1ra`, `*1r` und `Kb1rb` bleiben) |
| `milestone unit="column"` (684) | entfällt | Spalten des Drucks, nicht der Handschrift |
| `hi rend="doublespace"` | `hi rend="doublespace"` | gesperrt, der Header der Vorlage sagt dazu: „Doublespace font in this text corresponds to text quoted from the Bible.“ (`seriesStmt/p/note`) |
| `hi rend="bold"`, `"superscript"` | gleich | Initialen, Hochstellung |
| `hi` ohne `rend` | `hi rend="italic"` | so zeigt das MWB-Textarchiv diese Stellen (`volltextanzeige.php?wbsigle=HeslApk`) |
| `orig reg` (309, Trennung am Druckzeilenende) | ein `w` mit dem verbundenen Text | 3 Fälle, in denen der verbundene Text nicht `@reg` gleicht, druckt der Konverter aus (Offene Fragen) |
| `lb` im Vers (558) | entfällt | Druckzeilen. Mitten im Wort ohne `orig` wäre ein harter Fehler (0 Fälle) |
| `corr resp="editor" sic` (5) | Inhalt im Text, die Auszeichnung der Vorlage wörtlich als Kommentar hinter dem Wort | das Schema kennt kein `choice/sic/corr` |
| Satzzeichen `,.;:?!()` und Strich am Wortrand | `pc`, öffnende Klammer und führender Strich mit `join="right"` | |

Bilanzen, die der Konverter hart prüft:

- Bestand je Element gegen `SOLL`
- dieselbe Versliste in Quelle und Ziel
- je Vers dieselben Wörter und Satzzeichen wie eine Tokenisierung des Quelltexts, die von der Konverterlogik unabhängig ist
- je Vers und `rend` derselbe Text in Quelle und Ziel (`fw` ausgenommen)
- Schema

Die Zahlen gibt der Lauf aus:

```
python -P -E scripts/ingest/apk/01-convert-apk-to-mhdbdb.py --trocken --datum 2026-11-19
```

## Offene Fragen an die Fachseite

- **Kursive:** Was markiert ein `hi` ohne `rend` in der Vorlage, aufgelöste Abkürzungen der Handschrift oder Ergänzungen der Ausgabe? Abgebildet ist es als `italic` ohne Deutung.
- **Drei Trennungen weichen von `@reg` ab:** `vorsuchen` (reg `vosuchen`), `entrieten,` (reg `entrieten`), `anderswar` (reg `anderwar`). Im Text steht die Form ohne `@reg`.
- **Korrekturen der Ausgabe:** 5 `corr` stehen als Kommentar. Ob die Lesart der Handschrift (`sic`) sichtbar werden soll, braucht eine Schemaentscheidung.
- **Fett:** nur Initialen am Abschnittsanfang? Sie stehen als `hi rend="bold"` im Wort.
- **Spalten des Drucks** entfallen. Die Seiten der Ausgabe bleiben als `pb`.
