# `sources/` – Legacy-Quelldateien, nicht normativ

> **Achtung: das hier sind keine Korpusdaten.**
> Normativ sind ausschließlich [`tei/`](../tei/) und [`authority-files/`](../authority-files/).
> Die Dateien in diesem Verzeichnis sind **historische Ingest-Vorlagen** aus der Zeit vor der
> TEI-Migration. Sie werden **nicht** validiert, **nicht** indexiert, von **keinem** Build-Skript
> gelesen und nie als Beleg für den aktuellen Datenstand zitiert. Wer eine Aussage über das
> Korpus braucht, liest `tei/`. Wer wissen will, was der Ingest verloren hat, liest hier.

Angelegt zu [Issue #248](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/248),
Freigabe durch KZW am 2026-07-30.

## Das Quellarchiv liegt lokal bei KZW, nicht hier

Alles in diesem Verzeichnis ist ein **Auszug** aus einem 9,1 GB großen Archiv, das
**ausschließlich lokal auf Katharina Zeppezauer-Wachauers OneDrive** liegt:

```
MHDBDB_Inhaltliches/Texte/     (im MHDBDB-Sharefolder-Backup)
```

Kein Netzlaufwerk, kein Repo, kein Zenodo-Deposit. **Zugriff läuft über KZW.** Wenn bei einer
Korpusfrage unklar bleibt, ob es dazu noch einen Scan, eine Vorstufe, eine Lesefassung oder eine
Editions-PDF gibt: erst in [`INVENTAR-ARCHIV.md`](INVENTAR-ARCHIV.md) und
[`archiv-inventar.csv`](archiv-inventar.csv) nachsehen, dann bei KZW anfragen. Das Inventar
existiert genau dafür.

## Was hier liegt

| Pfad | Inhalt |
|---|---|
| [`linecode/`](linecode/) | 306 codierte Ingest-Dateien, 26,0 MB. Volltext mit vorangestelltem Legacy-Linecode, byte-identische Kopien |
| [`legacy-tooling/`](legacy-tooling/) | `linecode-generator.dot`: die Word-Vorlage, mit der die Linecodes erzeugt wurden |
| [`linecode-manifest.csv`](linecode-manifest.csv) | Eine Zeile je Datei: Sigle, `inhaltstyp`, Originalpfad im Archiv, Zeilen, Codebreiten, `sha256`, Dubletten, Arbeitskopien. Bei `erledigt/frauenlob_bd2-codiert.rtf` sind `zeilen`, `codierte_zeilen`, `codebreiten` und `encoding_gelesen` leer: die Datei ist RTF und läuft nicht durch den Zeilenscanner |
| [`INVENTAR-ARCHIV.md`](INVENTAR-ARCHIV.md) | Was das Archiv sonst noch enthält (Scans, OCR-Projekte, Volltextexport 2017, Ingest-Kandidaten) und wie man lokal darauf zugreift |
| [`archiv-inventar.csv`](archiv-inventar.csv) | Dateiweises Verzeichnis des Archivs, 5.037 Zeilen (alles außer den 14.771 FineReader-Projektdateien) |

Die Unterordner von `linecode/` spiegeln die Archivstruktur: `erledigt/` (302 Dateien) und
`neue-texte-klaus/` (4 Dateien).

## Herkunft

Das Archiv ist die Arbeitsablage der MHDBDB-Texterfassung von etwa 2003 bis 2016: erst wurde ein
Druck gescannt und OCR-gelesen, dann der Rohtext korrigiert und mit dem Linecode versehen, dann in
die damalige Datenbank eingespielt. Die codierten Dateien sind die letzte Stufe davor, also die
eigentliche Ingest-Vorlage. `legacy-tooling/linecode-generator.dot` ist das Werkzeug, mit dem sie
entstanden sind: die Gegenrichtung, die Linecode-nach-TEI-Konversion, ist nicht erhalten (siehe
[`docs/LINECODE.md`](../docs/LINECODE.md) → Context).

Aufgenommen ist genau die Schicht, die klein, diffbar und für die QA am TEI-Bestand direkt
verwertbar ist. Für die restlichen 9 GB ist Git das falsche Werkzeug, und 82 % davon sind
FineReader-Projektinnereien ohne extrahierbaren Text.

**`ERLEDIGT/` ist nicht die ganze Ablage.** Das war die erste Annahme und sie war falsch: vier
codierte Dateien liegen in `Neue Texte Klaus/`. Deshalb ist die Archivwurzel für alle Skripte
hier `Texte/` und nicht `Texte/ERLEDIGT/`.

## Warum das nützlich ist

Der Linecode kodiert Strukturebenen, die bei der automatischen Umsetzung nach TEI teilweise
abgeflacht wurden. Wo eine Ebene fehlt, ist die codierte Quelle die einzige Stelle, an der sie
maschinenlesbar erhalten ist. Zwei dokumentierte Fälle:

- **DUB** (#85): `u=1`, Parallelüberlieferung nicht ausgezeichnet.
- **FR3** (#236): `u`-Ebene komplett verloren, 23 gleichnamige `<div type="song">`, 1.563 von
  9.595 Versen doppelt gezählt. Über die codierte Quelle exakt rekonstruiert.

Der Join zwischen Quelle und TEI ist verlustfrei und braucht keinen Textabgleich: die `@xml:id`
eines Tokens ist der Linecode ohne führende Nullen plus Token-Index
(`0000000105201010010` → `FR3_105201010010_0`).

Vollständige Erklärung des Systems, Buchstaben-Tabelle und Diagnose-Rezepte:
[`docs/LINECODE.md`](../docs/LINECODE.md). Die Templates je Sigle stehen in
[`docs/data/linecode-templates.csv`](../docs/data/linecode-templates.csv), die Bedeutung der
Stellen in [`docs/data/linecode-mapping.csv`](../docs/data/linecode-mapping.csv).

## Abdeckung

| | |
|---|---|
| Dateien | 306 (26,0 MB) |
| Distinkte Sigeln mit Treffer in `tei/` | 199 von 667 Korpustexten (30 %) |
| Dateien mit Sigle | 273 |
| Dateien ohne Sigle-Zuordnung | 33 (siehe unten) |
| Codebreiten | 13, 17, 18, 19, 20 Stellen |
| Zeichensätze | cp1252, teils UTF-8 mit BOM |

### Wie die Sigle zugeordnet wird

Zwei Wege, in dieser Reihenfolge. Erstens der **`xml:id`-Join**: der Linecode ohne führende
Nullen gegen die Token-`@xml:id` im Korpus. Das ist der belastbare Weg und steht als
`SIGLE_OVERRIDE` im Build-Skript, jeweils mit der Trefferquote als Kommentar. Zweitens, nur
wenn der Join nichts hergibt, der **Dateiname**, falls er auf eine Sigle in `tei/` passt.

Der Join hat 13 Dateien zugeordnet, deren Name von der Sigle abweicht, darunter drei
Fassungen der Vita Caroli und ein Fall, in dem Name und Join sich widersprechen:
`kbl5.txt` gehört laut Join zu `KBL4` (600/600 Stems). Der Join gewinnt.

**Wo der Join nichts beweist, bleibt die Sigle leer.** Bei 33 Dateien sind die Linecodes
trivial klein (`100`, `200`, `300` oder eine laufende Nummer ab 1). Solche Stems kommen in
jedem Korpustext vor, der Join liefert dann drei bis fünf gleichwertige Kandidaten mit
identischer Trefferzahl und entscheidet nichts. Betroffen sind `crone`/`crone1`/`crone2`,
`waltherhaupttext*` und `waltherleich`, die 16 Tannhäuser-Teilstücke, `akkon`, `osw1-doc`,
`sfl1`, `kolner-fechtbuch-1`, `hug1`, `ac3-new`, `tann` sowie `frauenlob_bd2-codiert.rtf`
(RTF, keine Zeilencodes am Zeilenanfang).

Ein Join über Schlüssel, die trivial klein sind, matcht überall und beweist nichts. Deshalb
ist „199 von 667" eine belastbare Untergrenze und keine Obergrenze: einige der 33 gehören
sicher zu einem Korpustext, nur eben nicht nachweisbar über den Code. Für `waltherhaupttext*`
ist die Nicht-Zuordnung nachprüfbar richtig: das Archiv trägt dort Template `201012`,
`tei/WVV.tei.xml` aber `1102010001`, es gibt also gar keinen direkten Join.

### Die vier Dateien außerhalb von ERLEDIGT

Ihre Dateinamen folgen nicht den Sigeln, deshalb wurden sie über den `xml:id`-Join zugeordnet
(Linecode ohne führende Nullen gegen die Token-`@xml:id` im Korpus), nicht über den Namen. Die
Zuordnung steht als `SIGLE_OVERRIDE` im Build-Skript, mit der Trefferquote als Kommentar.

| Datei | Korpustext | Beleg |
|---|---|---|
| `neue-texte-klaus/gtk2.txt` | `GWTK` Göttweiger Trojanerkrieg | 400/400 Stems |
| `neue-texte-klaus/efb.txt` | `CEFB` Fechtbuch | 399/400 |
| `neue-texte-klaus/clv.txt` | `CLV` Christi Leiden in einer Vision geschaut | 400/400 |
| `neue-texte-klaus/normal.txt` | `VTC` Vita Caroli, **Namenregister** | 14/14 Wortsonden im Volltext |

`normal.txt` ist kein Text, sondern ein **alphabetisches Namenregister** (`Aczon`, `Affensteyn`,
… `Zbyroch`) mit fortlaufendem Linecode 1 bis 468. Der Dateiname ist ein Word-Artefakt.

Der `xml:id`-Join versagt hier, weil die Stems 1 bis 468 in jedem Korpustext vorkommen;
zugeordnet wurde über 14 von 14 Wortsonden im Volltext von `VTC`. Damit die Sigle keine
Volltextquelle behauptet, trägt das Manifest eine eigene Spalte `inhaltstyp`: `volltext` für
alle anderen, `namenregister` für diese Datei. Der **codierte Volltext von VTC** liegt separat
als `erledigt/vtc_neu.txt`, `erledigt/vita_caroli_dt_gesamt_linecode_mit_tags.txt` und
`erledigt/vita_caroli_dt_gesamt_linecode_test.txt`, alle drei über den Join bestätigt
(599/599 bzw. 591/600).

**Achtung bei Namensgleichheit.** `FR3.txt` gibt es im Archiv in zwei Bedeutungen: die codierte
Ingest-Fassung (hier als `linecode/erledigt/fr3.txt`) und die Lesefassung aus dem Volltextexport
2017 (`ERLEDIGT/Textexport-Dateien_Feb2017/FR3.txt`, nicht im Repo). Immer die Spalte `quelle` im
Manifest prüfen.

## Dateinamen und Verifikation

Ordner- und Dateinamen sind auf ASCII-Kleinschreibung normalisiert, damit die Pfade auf allen
Plattformen unauffällig sind (`ERLEDIGT/Alte Texte/Kölner fechtbuch[1].txt` →
`linecode/erledigt/alte-texte/kolner-fechtbuch-1.txt`). Der **Inhalt ist unverändert**, inklusive
Zeilenenden und Zeichensatz. Der Originalpfad steht in der Manifest-Spalte `quelle`, die `sha256`
bezieht sich auf die Datei im Arbeitsverzeichnis und ist damit direkt gegen das Archiv prüfbar.

305 der 306 Dateien haben CRLF-Zeilenenden. [`sources/.gitattributes`](.gitattributes) setzt
deshalb `linecode/** -text`: ohne das würde `core.autocrlf` die Zeilenenden umschreiben und die
Prüfsummen wären wertlos. Verifiziert wurde am Blob im Git-Index, nicht nur an der Datei auf
Platte.

**Nie bearbeiten.** Auch offensichtliche Defekte bleiben stehen, damit die Dateien Quelle bleiben.
Bekanntes Beispiel: 86 der 9.605 Zeilen in `linecode/erledigt/fr3.txt` haben nur 18 statt 19
Stellen, weil eine führende Null fehlt (betrifft VIII,215 `u=1` und V,209 `u=2`). Vor dem Slicen
mit `zfill(19)` auffüllen, sonst verschwinden zwei Zeugen stillschweigend.

## Arbeitskopien an anderer Stelle im Repo

Acht dieser Dateien liegen zusätzlich als Arbeitskopie in einem Pipeline-Ordner. Sie sind
**inhaltsgleich**, nicht byte-identisch, und das ist kein Schlamperei-Vorbehalt, sondern eine
Eigenschaft von Git: sechs der acht liegen LF-normalisiert im Index, weil sie mit #110 und
#236 ins Repo kamen, bevor es `sources/.gitattributes` gab, und für ihre Pfade kein `-text`
gilt. Die Archivkopien hier tragen CRLF. Ein byte-weiser Vergleich wäre deshalb auf jedem
Linux- oder macOS-Checkout rot, obwohl inhaltlich nichts abweicht. Das Build-Skript
vergleicht daher mit auf LF normalisierten Zeilenenden und bricht nur bei einem echten
Unterschied ab. Die Zuordnung steht in der Manifest-Spalte `arbeitskopie_im_repo`.

| Archivkopie | Arbeitskopie |
|---|---|
| `linecode/erledigt/fr2.txt`, `fr3.txt` | [`scripts/ingest/frauenlob/source/`](../scripts/ingest/frauenlob/source/) (#236) |
| `linecode/erledigt/waltherhaupttext*.txt`, `waltherleich.txt` | [`ingest/wvv/`](../ingest/wvv/) (#110) |

## Rechte

Die Dateien sind Transkripte teils urheberrechtlich geschützter kritischer Editionen. Für die 199
erfassten Sigeln steht der Volltext bereits als annotiertes TEI im öffentlichen Repo, die
Aufnahme der Quelldatei ändert an der Exposition also nichts.

Ein Punkt bleibt zu beachten: **8 der 199 Sigeln tragen im TEI-Header
`<availability status="restricted">` mit `<ab type="display" n="excerpt-only"/>`**, also FR3,
HUB1, HUB2, MML, MRL, MRS, MSB1 und RLS. Das Frontend zeigt dort bewusst nur Auszüge. Eine
codierte Quelldatei ist einer glatten Lesefassung näher als annotiertes TEI. Wenn das anders
bewertet wird, sind es genau **8 Dateien**, alle über die Manifest-Spalte `sigle` auffindbar:
`erledigt/fr3.txt`, `erledigt/kochrezepttextsammlungen/fertig-codiert/hub1.txt` und `hub2.txt`,
`erledigt/der-marner/mml.txt`, `mrl.txt`, `mrs.txt`,
`erledigt/kochrezepttextsammlungen/fertig-codiert/msb1.txt` und
`erledigt/rumelant-von-sachsen/rls.txt`. Frühere Fassungen dieses Absatzes nannten 9; das war
falsch gezählt.

Nicht aufgenommen sind Seitenscans der Drucke. Das wäre ein neuer Veröffentlichungsakt und ist
in #248 ausdrücklich abgelehnt. Ebenfalls nicht aufgenommen und **lizenzrechtlich gesperrt**: das
Bonner Frühneuhochdeutschkorpus im Archivordner `FnhdC/` samt der beiden daraus stammenden
Einzeldateien in `Neue Texte Klaus/`, siehe [`INVENTAR-ARCHIV.md`](INVENTAR-ARCHIV.md) →
Lizenzsperre. Die Sperre ist im Build-Skript als Ausschlussliste **durchgesetzt** und nicht nur
beschrieben: übersprungene Pfade werden protokolliert.

## Reproduktion

Die Skripte in [`scripts/ingest/legacy-sources/`](../scripts/ingest/legacy-sources/) erzeugen
dieses Verzeichnis neu. Sie brauchen Zugriff auf das lokale Archiv bei KZW und laufen deshalb
nicht in CI. Der Lauf ist idempotent: gleicher Archivstand erzeugt identische Dateien.
