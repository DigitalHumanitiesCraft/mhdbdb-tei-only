# `sources/` – Legacy-Quelldateien, nicht normativ

> **Achtung: das hier sind keine Korpusdaten.**
> Normativ sind ausschließlich [`tei/`](../tei/) und [`authority-files/`](../authority-files/).
> Die Dateien in diesem Verzeichnis sind **historische Ingest-Vorlagen** aus der Zeit vor der
> TEI-Migration. Sie werden **nicht** validiert, **nicht** indexiert, von **keinem** Build-Skript
> gelesen und nie als Beleg für den aktuellen Datenstand zitiert. Wer eine Aussage über das
> Korpus braucht, liest `tei/`. Wer wissen will, was der Ingest verloren hat, liest hier.

Angelegt zu [Issue #248](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/248),
Freigabe durch KZW am 2026-07-30.

## Was hier liegt

| Pfad | Inhalt |
|---|---|
| [`linecode/`](linecode/) | 302 codierte Ingest-Dateien, 24,6 MB. Volltext mit vorangestelltem Legacy-Linecode, byte-identische Kopien aus dem Sharefolder-Backup |
| [`linecode-manifest.csv`](linecode-manifest.csv) | Eine Zeile je Datei: Sigle, Originalpfad im Archiv, Zeilen, Codebreiten, `sha256`, Dubletten |
| [`INVENTAR-ERLEDIGT.md`](INVENTAR-ERLEDIGT.md) | Was das Quellarchiv sonst noch enthält (Scans, OCR-Projekte, Volltextexport 2017) und wie man lokal darauf zugreift |
| [`erledigt-inventar.csv`](erledigt-inventar.csv) | Dateiweises Verzeichnis des Archivs, 2.923 Zeilen (alles außer den 14.450 FineReader-Projektdateien) |

## Herkunft

Quelle ist `MHDBDB_Inhaltliches/Texte/ERLEDIGT/` im MHDBDB-Sharefolder-Backup auf Katharinas
OneDrive. Der Ordner ist die Arbeitsablage der Texterfassung von etwa 2003 bis 2016: erst wurde
ein Druck gescannt und OCR-gelesen, dann der Rohtext korrigiert und mit dem Linecode versehen,
dann in die damalige Datenbank eingespielt. Die codierten Dateien sind die letzte Stufe davor,
also die eigentliche Ingest-Vorlage.

Das Archiv liegt **nur lokal** und bleibt dort: 8,1 GB, davon 7,4 GB reine
FineReader-Projektartefakte. Für Git ist das das falsche Werkzeug. Aufgenommen ist genau die
Schicht, die klein, diffbar und für die QA am TEI-Bestand direkt verwertbar ist.

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
| Dateien | 302 (24,6 MB) |
| Distinkte Sigeln mit Treffer in `tei/` | 193 von 667 Korpustexten (29 %) |
| Dateien ohne Sigle-Treffer | 45 (Arbeitsfassungen, Teilstücke, Vorstufen; siehe Manifest) |
| Codebreiten | 13, 17, 18, 19, 20 Stellen |
| Zeichensätze | cp1252, teils UTF-8 mit BOM |

Die 45 Dateien ohne Sigle-Treffer sind keine Fehler, sondern Arbeitsstände: Teilstücke
(`Tannh_I` bis `Tannh_XVI` gegenüber `TA_komplett`), Varianten desselben Texts
(`crone1`/`Crone`/`Crone2`), Zwischenfassungen (`NEIC_Quelle-cod`, `NEIC_exportiert`) oder
datierte Korrekturstände (`PUC_korr_12_3_2013`).

**Achtung bei Namensgleichheit.** `FR3.txt` gibt es im Archiv in zwei Bedeutungen: die codierte
Ingest-Fassung (hier als `linecode/fr3.txt`) und die Lesefassung aus dem Volltextexport 2017
(`Textexport-Dateien_Feb2017/FR3.txt`, nicht im Repo). Immer die Spalte `quelle` im Manifest
prüfen.

## Dateinamen und Verifikation

Ordner- und Dateinamen sind auf ASCII-Kleinschreibung normalisiert, damit die Pfade auf allen
Plattformen unauffällig sind (`Kölner fechtbuch[1].txt` → `linecode/alte-texte/kolner-fechtbuch-1.txt`).
Der **Inhalt ist unverändert**, inklusive Zeilenenden und Zeichensatz. Der Originalpfad steht in
der Manifest-Spalte `quelle`, die `sha256` bezieht sich auf die Datei im Arbeitsverzeichnis und
ist damit direkt gegen das Archiv prüfbar.

301 der 302 Dateien haben CRLF-Zeilenenden. [`sources/.gitattributes`](.gitattributes) setzt
deshalb `linecode/** -text`: ohne das würde `core.autocrlf` die Zeilenenden umschreiben und die
Prüfsummen wären wertlos.

**Nie bearbeiten.** Auch offensichtliche Defekte bleiben stehen, damit die Dateien Quelle bleiben.
Bekanntes Beispiel: 86 der 9.605 Zeilen in `linecode/fr3.txt` haben nur 18 statt 19 Stellen, weil
eine führende Null fehlt (betrifft VIII,215 `u=1` und V,209 `u=2`). Vor dem Slicen mit `zfill(19)`
auffüllen, sonst verschwinden zwei Zeugen stillschweigend.

## Arbeitskopien an anderer Stelle im Repo

Acht dieser Dateien liegen zusätzlich als Arbeitskopie in einem Pipeline-Ordner. Sie sind
byte-identisch; das Build-Skript prüft das bei jedem Lauf und bricht bei Abweichung ab. Die
Zuordnung steht in der Manifest-Spalte `arbeitskopie_im_repo`.

| Archivkopie | Arbeitskopie |
|---|---|
| `linecode/fr2.txt`, `linecode/fr3.txt` | [`scripts/ingest/frauenlob/source/`](../scripts/ingest/frauenlob/source/) (#236) |
| `linecode/waltherhaupttext*.txt`, `linecode/waltherleich.txt` | [`ingest/wvv/`](../ingest/wvv/) (#110) |

## Rechte

Die Dateien sind Transkripte teils urheberrechtlich geschützter kritischer Editionen. Für die 193
erfassten Sigeln steht der Volltext bereits als annotiertes TEI im öffentlichen Repo, die
Aufnahme der Quelldatei ändert an der Exposition also nichts.

Ein Punkt bleibt zu beachten: **8 der 193 Sigeln tragen im TEI-Header
`<availability status="restricted">` mit `<ab type="display" n="excerpt-only"/>`**, also FR3,
HUB1, HUB2, MML, MRL, MRS, MSB1 und RLS. Das Frontend zeigt dort bewusst nur Auszüge. Eine
codierte Quelldatei ist einer glatten Lesefassung näher als annotiertes TEI. Wenn das anders
bewertet wird, sind es genau diese 9 Dateien, die wieder herausfallen; das Manifest macht sie
über die Spalte `sigle` auffindbar.

Nicht aufgenommen sind Seitenscans der Drucke. Das wäre ein neuer Veröffentlichungsakt und ist
in #248 ausdrücklich abgelehnt.

## Reproduktion

Die Skripte in [`scripts/ingest/legacy-sources/`](../scripts/ingest/legacy-sources/) erzeugen
dieses Verzeichnis neu. Sie brauchen Zugriff auf das lokale Archiv und laufen deshalb nicht in
CI. Der Lauf ist idempotent: gleicher Archivstand erzeugt identische Dateien.
