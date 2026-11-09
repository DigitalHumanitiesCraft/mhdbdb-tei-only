# COR: CoReMA-Pilot (Kochrezepte des Mittelalters)

Stufe 0 für den Pilot aus Issue [#139](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/139): vier Kochbücher, Bs1, GR1, M11 und W1 (Entscheidung chsteiner, 05.11.2026), Siglen `COR_BS1`, `COR_GR1`, `COR_M11`, `COR_W1`. Das Ergebnis liegt in [`ingest/cor/`](../../../ingest/cor/README.md), nicht in `tei/`, und es gibt noch keine Eintragung in `authority-files/` (Entscheidung chsteiner, 08.11.2026). Genre, Werk, Lemmatisierung und Segmentierungsfragen gehören in die gemeinsame Sitzung.

## Quelle und Rechte

- **Lokal, kein Abruf.** Die Daten stammen aus dem Nachbar-Repository `corema` (`data/published/annotated/<buch>.recipes.xml`, die Rezeptebene: normalisierter Lesetext mit semantischer Annotation). Das Skript liest nur und kopiert nichts ins Repository. `--corema-dir` nennt die Wurzel, Vorgabe ist `../corema`.
- **Gepinnt über sha256.** Jede Ausgabe nennt Pfad und sha256 der gelesenen Datei im Header (`bibl/note[@type="provenance"]`), `ingest/cor/quellen.tsv` fasst alle vier zusammen. Das Repository `corema` ändert sich laufend (Korrekturläufe), die Dateien weichen von GAMS ab. Wer neu erzeugt, vergleicht zuerst die sha256.
- **Lizenz der Textdaten:** CC BY 4.0 (steht in jedem TEI der Quelle, Faksimile-Lizenz gilt hier nicht). Die Ausgabe übernimmt sie für Daten und Annotationen (Entscheidung chsteiner, 09.11.2026). Förderhinweis FWF I 3614 und Zitierweise sind im Header.

## Skripte

| Skript | Was es tut | Schreibt |
|---|---|---|
| `01-convert-corema-to-mhdbdb.py` | Konvertiert ein Buch (`--buch bs1`) oder alle (`--buch alle`) nach MHDBDB-TEI, prüft Gegenproben und validiert gegen `schema/mhdbdb.rng`, im Speicher und nach dem Schreiben aus der Datei. `--trocken` schreibt nichts | `ingest/cor/<SIGLE>.tei.xml`, `<SIGLE>.annotationen.tsv`, bei `alle` auch `quellen.tsv` |
| `test_cor.py` | Mini-Fixtures für Tokenisierung, Platzierung von `<pb>` und `<note>`, verschachtelte `<ab>`, harte Fehler | |

```bash
python -P -E scripts/ingest/cor/01-convert-corema-to-mhdbdb.py --buch alle --corema-dir <pfad>/corema
python -P -E scripts/ingest/cor/01-convert-corema-to-mhdbdb.py --buch m11 --trocken --corema-dir <pfad>/corema
python -P -E scripts/ingest/cor/test_cor.py
```

Die letzte Zeile der Ausgabe (`VERDICT`) nennt je Buch Wörter und Schemastatus. Exit 1 bei Quellfehler, fehlgeschlagener Gegenprobe oder nicht validem Ergebnis.

## Abbildung

| Quelle | TEI |
|---|---|
| Leerraum | trennt `<w>` |
| `. , : ; ! ? " /` allein stehend oder am Wortrand | `<pc>`, `join="left"`, am Einheitsanfang und bei führendem `"` `join="right"` |
| `<ab type="recipe">` | `<div type="recipe" n>` (`n` = `ab/@n`), Text in `<p>` |
| `<ab>` mit anderem `@type` (household, kitchenTip, medicinal, artTechnology, dietetics, parody) | `<div type="section" n>`, der Originaltyp steht in der Tabelle |
| verschachtelte `<ab>` (Unterrezept) | verschachteltes `<div>`, der Text des Elternrezepts läuft danach in einem neuen `<p>` weiter |
| Titel am Rezeptanfang (vor ihm kein Wort) | `<head>` |
| `div/title`, `div/seg ana=intro\|close`, `div/dateline` | `<head>`, `<ab type="intro">`, `<ab type="close">`, `<ab type="dateline">` im äußeren `<div>` |
| `<pb n>` | `<pb n>` |
| `<note xml:lang>` | `<note type="editorial-de\|editorial-en">`, nicht tokenisiert. Das Schema kennt an `<note>` kein `@xml:lang`, deshalb steht die Sprache im Typ. Ein `<ref target>` in der Notiz (M11: 1, sonst keines in den vier Büchern) steht als Zeile `note/ref` in der Tabelle, verankert am letzten Token vor der Notiz. Ein anderes Element in der Notiz bricht ab |
| `<foreign xml:lang>` | `@xml:lang` an den betroffenen `<w>` |
| alle übrigen Elemente | Zeile in `annotationen.tsv` |

`xml:id` der Wörter: `{SIGLE}_{Blatt}_{lfd. Nr. auf dem Blatt}`, Blatt `0` vor dem ersten `<pb>`. Die Nummer zählt `<w>` und `<pc>` gemeinsam und läuft über Wiederholungen derselben Blattangabe weiter.

## annotationen.tsv

Die semantische Auszeichnung der Quelle hat im Schema keinen Platz und geht nicht verloren. Eine Zeile je Element, Spalten `einheit` (xml:id der umgebenden Quell-`<ab>`, `-` auf Ebene des äußeren `<div>`), `art` (Elementname, dazu `ab` und `seg`), `von` und `bis` (erste und letzte `xml:id` von `<w>`/`<pc>`, leer bei einem Element ohne Token), `n_w`, `attribute` (`name=wert`, getrennt durch ` | `) und `text` (nur bei kurzen Begriffen wie ingredient, tool, dish, name, ref, date, title, time). Bei `art=ab` ist `von`/`bis` das erste und letzte Token des Rezepts. Läuft der Text des Elternrezepts nach einem Unterrezept weiter, liegen die Token des Unterrezepts dazwischen und gehören zu `von..bis` (gemessen: Bs1 4 von 306, GR1 1 von 284, M11 0, W1 1). Nur `n_w` zählt den eigenen Umfang ohne Unterrezepte. Bei `art=note/ref` sind `von` und `bis` das Token vor der Notiz.

Gegenprobe im Skript: die Zeilenzahl je `art` ist gleich der Elementzahl in der Quelle, Elemente in `<note>` zählen als `note/<name>`. Zusätzlich ein eigener Zeichenrundlauf über den Text der Notizen.

## Gegenproben und harte Fehler

- Ein Element oder Attribut außerhalb der Tabellen im Skript bricht ab (`HarterFehler`), ebenso Text zwischen den Kindern des äußeren `<div>`.
- Zeichenrundlauf: die Zeichen aller `<w>`/`<pc>` (ohne Leerraum) sind gleich dem Text der Quelle ohne `<note>`.
- Gleiche Zahl `<ab>`, `<pb>`, `<note>` und Datumszeilen in Quelle und Ausgabe, keine doppelte `xml:id`.

## Offen für die Sitzung

Alles Folgende ist mechanisch entschieden worden, damit Stufe 0 durchläuft, und nicht inhaltlich beurteilt.

- **Welche Ebene.** Gewählt ist die Rezeptebene (normalisiert, annotiert). Die hyperdiplomatische Ebene (`data/published/glyph/<buch>.xml`, Abkürzungsauflösung, Zeilenumbrüche) ist nicht verwendet. Für Bs1, GR1 und W1 liegt zusätzlich `data/unpublished/normalized/` vor, für M11 nicht.
- **Segmentierung.** Eine Quell-`<ab>` ist ein `<div>`. Ob die Rezeptzählung der Edition die der Zielstruktur ist, und ob Unterrezepte eigene `<div>` bleiben, ist offen. In GR1 steht der Titel im Satz (`Item wildw machen ein guet air von mandel`), deshalb gibt es dort fast keine `<head>` (9 gegen 289, 101 und 278 in den anderen). Die Titelspannen stehen als `art=title` in der Tabelle.
- **Wortgrenzen.** An drei Stellen setzt die Quelle eine Elementgrenze ohne Leerraum zwischen zwei Buchstaben, das Skript fügt keinen Trenner ein und meldet sie. Zwei sind vermutlich fehlende Leerzeichen und bleiben als ein `<w>` verklebt: `konkaveliteZvo` (m11.1) und `caleusvnd` (m11.25). Die dritte, `Iungen|huner` (w1.164, `huner` steht im `<ingredient>`), ist ein Wort mit Elementgrenze mittendrin und richtig als ein `<w>`. Acht `<pb>` stehen in der Quelle mitten im Wort (Bs1 1, GR1 7) und sind hinter das Wort gestellt, damit das Wort ganz bleibt.
- **Interpunktion.** `. , : ; ! ? " /` wird `<pc>`. Apostroph und Binnenzeichen (`1/2`, `vah'n`) bleiben im Wort. In GR1 und W1 gibt es kaum Interpunktion (111 und 24 `<pc>`).
- **Semantische Schicht.** Die Q-IDs von ingredient, tool und dish (`commodity`) können die Sense-Disambiguierung stützen (#139, 10.07.). Wie sie in `concepts.xml` und `@ana` ankommen, ist nicht entschieden. Daran hängt eine zweite Frage: [DATA-MODEL.md → Stage 0](../../../docs/DATA-MODEL.md#stage-0-schema-conversion-mechanical) verlangt, dass Elemente, die das Schema nicht kennt, im Text stehen bleiben und als offene Entscheidung gemeldet werden. Stufe 0 legt die semantische Auszeichnung stattdessen verlustfrei in `annotationen.tsv` neben den Text. Ob das so bleibt oder die Elemente ins TEI zurückkommen (und das Schema dafür wächst), entscheidet die Sitzung.
- **Schema.** `<note>` ohne `@xml:lang` (siehe oben). Das übrige Schema reicht für alle vier Bücher, es gibt keinen Verstoß, den ein Platzhalter verdeckt.
- **Platzhalter im Header.** `works.xml#work_TBD`, `genre_TBD` (Kochbuch, MBS1 trägt `genre_1d40ec18` Kochkunst), Sprachstufe `TBD` (die Quelle nennt Bavarian-Alemannic, Early New High German, East Franconian, Bavarian), Autor `person_anonym`, Datum `2026`. Nicht mehr offen ist die Lizenz: CC BY 4.0 (chsteiner, 09.11.2026), die Lizenz der Textdaten der Quelle, übernommen wie bei ARI (dort CC BY-SA 4.0). Bis dahin trugen die Header CC BY-NC-SA 4.0 nach dem Bestandsmuster.
- **Wortzahl.** Der Pilot hat 75 106 `<w>` und 1 428 `<pc>`. Die Zahl von 79 000 Wörtern (Messung 10.07. an der hyperdiplomatischen Ebene) ist eine andere Ebene mit anderer Zählweise.
- **Gegenprobe fyndling.** Die 213 Lemmavorschläge (#376) betreffen W1 und GR1 und kommen erst nach der Lemmatisierung.
