# Inventar des Legacy-Textarchivs

Verzeichnis dessen, was im MHDBDB-Textarchiv liegt und **nicht** im Repo ist. Zweck: wenn bei
einer Korpusfrage Unklarheit auftaucht, soll auffindbar sein, ob es dazu noch einen Scan, eine
Vorstufe, eine Lesefassung oder eine Editions-PDF gibt, ohne dass jemand 9 GB durchsucht oder
einen Druck aufschlägt.

## Zugriff: alles liegt lokal bei KZW

> Das Archiv liegt **ausschließlich auf Katharina Zeppezauer-Wachauers OneDrive**, im
> MHDBDB-Sharefolder-Backup:
>
> ```
> MHDBDB_Inhaltliches/Texte/
> ```
>
> Kein Netzlaufwerk, kein Repo, kein Zenodo-Deposit, keine Online-Kopie. **Jeder Zugriff läuft
> über KZW.** Dieses Inventar ist der Katalog dazu: hier nachsehen, dann anfragen.

- **Stand:** aufgenommen 2026-07-30.
- **Umfang:** 19.808 Dateien, 9,1 GB.
- **Dateiweises Verzeichnis:** [`archiv-inventar.csv`](archiv-inventar.csv), 5.036 Zeilen.
  Enthält alles außer den 14.771 FineReader-Projektdateien. Spalten: `folder`, `file`, `ext`,
  `kategorie`, `bytes`, `geaendert`.
- **Was daraus im Repo ist:** 306 codierte Ingest-Dateien (26,0 MB) in
  [`linecode/`](linecode/) plus `legacy-tooling/linecode-generator.dot`. Alles andere nicht.

## Was drin ist, nach Kategorie

| Kategorie | Dateien | Größe | Im Repo? |
|---|---|---|---|
| OCR-Artefakte (`.frdat`, `.aux`, `.dat`, `.opt`, `.hdr`, `.lock`) | 14.771 | 7.446 MB | nein |
| Scans (`.tif`, `.jpg`, `.bmp`, `.png`) | 2.858 | 1.145 MB | nein |
| Text (`.txt`, `.doc`, `.rtf`, `.docx`, `.dot`, `.wbk`, `.xml`) | 1.936 | 358 MB | teilweise, siehe unten |
| PDF | 215 | 171 MB | nein |
| ZIP | 28 | 162 MB | nein |

82 % der Masse sind FineReader-Projektinnereien. Der eigentliche Inhalt ist klein.

## Ordnerübersicht

| Ordner | Dateien | Größe | Was drin ist |
|---|---|---|---|
| `ERLEDIGT` | 17.373 | 8.320 MB | abgearbeitete Texterfassung, Quelle der 302 codierten Dateien; eigene Untergliederung unten |
| `Neue Texte (zu bearbeiten)` | 772 | 375 MB | nie ingestierte Transkriptionen, Liedersaal, Zweter, Spruchdichter → #264, #265 |
| `Neue Texte Margret` | 801 | 174 MB | überschneidet sich stark mit dem vorigen, dazu Marner- und Mantel-Material |
| `Neue Texte Klaus` | 182 | 150 MB | **enthält 4 codierte Dateien** (im Repo), dazu Prosa- und Fachtexte → #266 |
| `Neue Texte Katharina` | 552 | 139 MB | Buch der Natur, Lucidarius, Seifried Helbling, Gloning-Kochtexte → #263 |
| `FnhdC` | 93 | 99 MB | Bonner Frühneuhochdeutschkorpus, **lizenzrechtlich gesperrt**, siehe unten |
| `(root)` | 3 | 21 MB | `Gesammtabenteuer_Band1.pdf`, `Ersetzungen.doc`, `linecode Generator.dot` |
| `Sonstiges` | 15 | 3 MB | Stuttgart/Braun-Zuarbeit, Todo-Listen 2014 und 2015 |
| `Sicherheitskopie Textliste MANTIS` | 16 | 0,1 MB | gespeicherte HTML-Ansicht der alten MantisBT-Textliste |
| `Scanarbeiten, Verwaltungstechnisches` | 1 | 0 MB | ein Word-Dokument |

## Innerhalb von `ERLEDIGT/`

| Unterordner | Dateien | Größe | Inhalt |
|---|---|---|---|
| `Alte Texte` | 5.268 | 2.478 MB | 405 Textdateien (davon viele codiert, im Repo), 311 Scans, FineReader-Projekte `RF`, `SUW`, `ML1`–`ML26` |
| `MR1` | 1.492 | 3.711 MB | FineReader-Projekt, kein Text-Output |
| `FLG1` | 1.955 | 755 MB | FineReader-Projekt, kein Text-Output |
| `RVB1` | 5.205 | 547 MB | FineReader-Projekt, 9 Scans, 2 PDF |
| `König vom Odenwald` | 770 | 190 MB | 682 OCR-Artefakte, 58 Scans, 30 Text (inkl. `KVO.txt` codiert) |
| `Der Marner` | 242 | 103 MB | 236 Seitenscans, 6 Text (`MML`, `MRL`, `MRS` codiert) |
| `Heinrich von dem Türlin, Der Mantel` | 350 | 83 MB | FineReader-Projekt, 48 Scans |
| `Der Mantel`, `Der Mantel Bilder` | 349 | 83 MB | FineReader-Projekt und 47 Seitenscans |
| `Jenaer Meißner` | 80 | 56 MB | 78 Seitenscans, `DJEM` codiert |
| `Frauenlob_Bd2` | 310 | 55 MB | 196 Seiten-PDFs, 110 Scans, 4 RTF (eines davon codiert, im Repo) |
| `Textexport-Dateien_Feb2017` | 644 | 49 MB | Volltextexport 2017, siehe unten |
| `Der junge Meißner` | 91 | 19 MB | 87 Seitenscans, `DJUM` codiert |
| `Rumelant von Sachsen` | 139 | 12 MB | 134 Seitenscans, `RLS` codiert |
| `Tannhäuser` | 103 | 12 MB | 16 codierte Teilstücke plus Gesamtdatei, 50 Scans |
| `Freidank`, `Friedrich von Sonnenburg` | 92 | 20 MB | je Seitenscans plus RTF |
| `Neidhart-c` | 7 | 3 MB | 4 codierte Fassungen von `NEIC` |
| `SchweizerMinnesaengerCod` | 31 | 2 MB | 29 codierte Dateien, alle im Repo |
| `Kochrezepttextsammlungen` | 49 | 1 MB | Unterordner `fertig codiert` mit 15 codierten Dateien |
| `CvK_KLD_codiert` | 70 | 1 MB | 70 codierte Dateien (Carl von Kraus, KLD), alle im Repo |
| `Kaiserchronik`, `Tundalus` | 17 | 2 MB | `KAIS*.TXT` und `TUN`-Vorstufen, **nicht** codiert |

### Die großen OCR-Projekte sind als Rückfrageinstanz wertlos

`MR1` (3,7 GB), `FLG1`, `RVB1`, `Der Mantel`, `König vom Odenwald` und `Alte Texte/RF`, `SUW`,
`ML*` sind ABBYY-FineReader-Projektordner. Sie enthalten **keinen extrahierbaren Text**, nur
`batch.options.xml` und die internen `.frdat`-Container mit Seitenbild und Erkennungsergebnis.
Aufmachen geht nur mit FineReader.

Praktische Folge: das brauchbare Ergebnis liegt jeweils schon als korrigierter Text daneben. Wer
ein Seitenbild braucht, greift zu den `*Bilder`-Ordnern oder den PDFs.

### Seitenscans, nach Werk

Nutzbar, wenn eine Stelle im TEI zweifelhaft ist und der Druck geprüft werden muss.

| Werk | Scans | Ort (unter `ERLEDIGT/`) |
|---|---|---|
| Der Marner | 236 TIF | `Der Marner/Der Marner Bilder/` |
| Der Meißner (Jenaer Liederhandschrift) | 78 TIF | `Jenaer Meißner/Der Meißner der Jenaer Liederhandschrift Bilder/` |
| Rumelant von Sachsen | 134 TIF | `Rumelant von Sachsen/Rumelant  von Sachsen Bilder/` |
| Frauenlob Bd. 2 | 196 PDF (S. 152 ff.) + 110 TIF | `Frauenlob_Bd2/PDFs/`, `Frauenlob_Bd2/Frauenlob Ton X Bilder/` |
| Der junge Meißner | 87 TIF | `Der junge Meißner/Der Junge Meißner Bilder/` |
| Der Mantel | 47 TIF | `Der Mantel Bilder/`, `Heinrich von dem Türlin, Der Mantel/Der Mantel Bilder/` |
| Friedrich von Sonnenburg | 50 TIF | `Friedrich von Sonnenburg/friedrich von Sonnenburg Bilder/` |
| Freidank | 38 TIF | `Freidank/Freidank Bilder/` |
| König vom Odenwald | 58 | `König vom Odenwald/König vom Odenwald Bilder/` |
| Tannhäuser | 50 | `Tannhäuser/Tannhäuser Bilder/`, `Tannhäuser/Scans_unbearb/` |
| diverse | 311 | `Alte Texte/RF/`, `SUW/`, `ML1` bis `ML26` |
| Liedersaal | 160 MB ZIP | `Neue Texte (zu bearbeiten)/Liedersaal Scans_Originalbilder/Liedersaal I.zip` |

Vollständige Editions-PDFs: `ERLEDIGT/Appolonius-cpg154.pdf` (86 MB),
`ERLEDIGT/Reinfrid von Braunschweig.pdf` (13 MB), `ERLEDIGT/Hugo-von-Montfort_EdHofmeister.pdf`,
`ERLEDIGT/Lamprecht von Regensbg.pdf`, `Neue Texte Katharina/Seifried Helbling/Seifried_Helbling_von_Karajan.pdf`
(7,9 MB), `Neue Texte Margret/NLL Hs d.pdf`.

**Und direkt in `Texte/`: `Gesammtabenteuer_Band1.pdf`** (22 MB), von der Hagens GA Bd. 1. Genau
der Band, dessen Fehlen #236 zunächst blockiert hatte. Für künftige GA-Fragen der erste Griff.

## Volltextexport Februar 2017

`ERLEDIGT/Textexport-Dateien_Feb2017/`, 644 Dateien, 49 MB. Eine Datei je Sigle, reiner Lesetext
**ohne** Linecode, Stand 2017-02-24. 639 von 640 Sigeln stehen bereits als TEI im Repo, nur `VSP`
nicht; umgekehrt fehlen die 28 späteren Zugänge wie WZB.

Wert liegt in der **unabhängigen Gegenprobe** für Struktur- und Umfangsfragen: in #236 hat der
Export die Verszahlen aller 13 GA-Abschnitte von FR1 bestätigt, ohne den Druck zu bemühen.
Dieselbe Prüfung dürfte bei #23, #228 und künftigen Ingest-Issues wieder gebraucht werden.

**Nicht aufgenommen.** In #248 ist das eine eigene, noch offene Entscheidung. Solange sie aussteht,
läuft der Zugriff über KZW lokal.

## Codierte Dateien, die nur als Word-Datei existieren

Für vier Korpustexte liegt eine codierte Fassung im Archiv, aber nur im Word-Binärformat.
`.doc`/`.dot`/`.wbk` sind weder diffbar noch reviewbar, und eine Extraktion wäre ein abgeleitetes
Artefakt und keine Quelle. Deshalb bewusst **nicht** aufgenommen, aber hier verzeichnet, damit die
Lücke nicht unsichtbar bleibt.

| Datei (unter `ERLEDIGT/`) | Größe | Codes | Korpustext | Codierte `.txt` vorhanden? |
|---|---|---|---|---|
| `OsvoWo.doc`, `OvW.doc` | je 0,98 MB | 7.575 | `OVW` / `OSW`, Oswald von Wolkenstein | nein |
| `MSG-Endfassg.doc` | 0,46 MB | 4.511 | `MSG`, Mönch von Salzburg, geistliche Lieder | nein |
| `MSW-Endfassg.dot` | 0,30 MB | 2.246 | `MSW`, Mönch von Salzburg, weltliche Lieder | nein |
| `RVBR-backup.doc` | 2,08 MB | 27.627 | `RVBR` | ja, `linecode/erledigt/rvbr.txt` |
| `MR2.doc` | 0,73 MB | 8.986 | `MR2` | ja |
| `Alte Texte/Backup of ADP.wbk` | 0,69 MB | 8.417 | `ADP` | ja |
| `Rumelant von Sachsen_cod_02.doc` | 0,26 MB | 1.844 | `RLS` | ja |

Spalte „Codes" ist die Zahl der gefundenen Linecode-Ziffernfolgen im Rohbytestrom, ermittelt mit
`scripts/ingest/legacy-sources/02-scan-binaries.py`. Die einzige codierte Nicht-`.txt`-Datei, die
aufgenommen ist, ist `Frauenlob_Bd2-codiert.rtf`: RTF ist ein Textformat, das Git behandeln kann.

Wenn `OVW`, `OSW`, `MSG` oder `MSW` einmal eine Struktur-Diagnose brauchen: Word-Datei bei KZW
anfordern, in UTF-8-Text konvertieren und erst dann als Quelle behandeln. Alternativ liefert ein
frischer Export aus dem Alt-MHDBDB dieselbe Information sauberer, siehe
[`docs/LINECODE.md`](../docs/LINECODE.md) → „Live exports from MHDBDB-old".

## Lizenzsperre: das Bonner Frühneuhochdeutschkorpus

`FnhdC/` enthält das **Bonner Frühneuhochdeutschkorpus** von korpora.org: 40 Texte als XML plus
Originalfassungen in cp437, 99 MB, dazu Bibliographie und DTDs. Das mitgelieferte README ist
eindeutig:

> „Die Textsammlung kann für wissenschaftliche, nichtkommerzielle Zwecke verwendet werden, sofern
> auf die Quelle verwiesen wird. […] **Eine Weiterverbreitung ist nicht gestattet.**"

Zusätzlich verlangen die Bedingungen, dass Publikationen, die auf den Daten beruhen, unaufgefordert
gemeldet werden. **Nichts davon darf ins Repo**, und ein Ingest wäre eine Weiterverbreitung.

Daraus folgt eine konkrete Falle: **zwei Dateien in `Neue Texte Klaus/` stammen aus diesem
Korpus**, ohne das im Namen zu zeigen.

- `Durandus.txt` ist gar kein Text, sondern das **Quellenverzeichnis** des FNHD-Korpus
  („QUELLENVERZEICHNIS des FNHD-Korpusses mit Verweisen auf die HTML-Versionen der Einzeltexte").
- `BuchAltväter.txt` beginnt mit „Text 121: [ Buch Altväter, Stuttgart 14. Jahrhundert ]", also
  mit der FnhdC-Textnummer.

Wer die beiden für freie Rohtexte hält und einspeist, verletzt die Nutzungsbedingungen.

## Vier `.TXT`-Konvolute sind OCR-Rohtext, nicht Transkription

In `Neue Texte Klaus/` und `Neue Texte Katharina/`: `LUCIDARIUS/LUC*.TXT` (8 Dateien),
`Basler Alexander/ALEX*.TXT` (6), `GRAL/GRAL*.TXT` (7), `HELIAND/HEL*.TXT` (12). Alle mit
eingestreuten Seitenzahlen und typischem Erkennungsrauschen („CoUea Ällmacht. Cebd um seinen
Beistand"), nicht codiert, nicht bereinigt. `HELIAND` ist außerdem **altsächsisch** und damit
außerhalb des MHG-Scope. Der Lucidarius wäre inhaltlich reizvoll (fehlt im Korpus), bräuchte aber
eine Neuerfassung, keine Übernahme.

## Ingest-Kandidaten: als Issues erfasst

Was im Archiv liegt und im Korpus fehlt, ist gegen `tei/` und `authority-files/works.xml` geprüft
und in vier Issues mit Label `future plans` festgehalten, damit es nicht nur hier steht:

| Issue | Inhalt |
|---|---|
| [#262](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/262) | **Apokalypse Heinrichs von Hesler**, `Neue Texte Klaus/apk_free.xml`. Fertiges TEI.2 aus dem Trier/Virginia-MHGTA, Header sagt „publicly accessible due to 70 years time limit". Der beste Kandidat des Archivs |
| [#263](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/263) | **15 frühneuhochdeutsche Koch- und Diätetik-Texte** in Editionen von Thomas Gloning, `Neue Texte Katharina/Thomas-Gloning-eTexte/`. Bezug zu CoReMA (#139), Rückfrage bei Gloning nötig |
| [#264](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/264) | **Lyrik und Spruchdichtung** (Sammel): Liedersaal-Laßberg mit rund 120 Stücken darunter 18 Teichner-Gedichte und 23 Konstanzer Liebesbriefe, Wartburgstreit, fünf kleinere Spruchdichter, Meister Sigeher, Baldemann, Wizlav, Mügelns „Der Tum", Klara Hätzlerin, Anna von Köln |
| [#265](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/265) | **Reinmar von Zweter**, vollständige RTF-Transkription. Eigenes Issue, weil prominenter Einzelautor; Editionsgrundlage Roethe 1887 ist der Haken |
| [#266](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/266) | **Prosa, Chroniken, Fachtexte** (Sammel): Goldene Bulle in 4 Handschriften, Düringische Chronik, Dukus Horant, Nibelungen Hs. k, Johanniterhandschrift A94, Niclas von Wyle, Roriczer, Ellenbog, Hospitalregeln, Katharinenlegende. Enthält auch die FnhdC-Warnung |

Gemeinsamer Befund über alle vier: **das Material ist da, die Editionsgrundlage ist meist das
19. Jahrhundert, und nichts davon ist codiert.** Es gäbe also keinen Join gegen Bestandsdaten,
jeder Posten wäre ein vollständiger Ingest samt Annotationsschicht. Deshalb `future plans` und
nicht `claude-ready`.

## Pipeline-Dokumentation, klein und leicht zu überblicken

Kein Text, aber Belege dafür, wie der Alt-Ingest gearbeitet hat.

- **`linecode Generator.dot`** (73 KB, direkt in `Texte/`) – die Word-Vorlage, mit der die
  Linecodes erzeugt wurden. **Ins Repo aufgenommen** als
  [`legacy-tooling/linecode-generator.dot`](legacy-tooling/), weil LINECODE.md festhält, dass die
  Gegenrichtung (Linecode nach TEI) nicht erhalten ist. Das hier ist die Erzeugungsseite.
- `Neue Texte Klaus/Import-Korrekt/` – `differences` (25 KB) ist ein Diff des Alt-Imports gegen den
  Druck (Ulrich von Liechtenstein, Frauendienst, ed. Spechtler 1987) und zeigt, was die Pipeline
  still normalisiert hat, bis hinunter zu `'` gegen `‘`. Dazu `Ersetzungen.doc`, `Korrekturen.doc`.
- `Ersetzungen.doc` (direkt in `Texte/`, 40 KB) und eine zweite Fassung in
  `Neue Texte (zu bearbeiten)/` (46 KB).
- `Sicherheitskopie Textliste MANTIS/` – gespeicherte HTML-Ansicht der alten
  MantisBT-Textliste, also die historische Textplanung.
- `ERLEDIGT/Todo-Liste_9-2013.doc`, `Sonstiges/Todo-Liste_20140117.doc`,
  `Sonstiges/Todo-Liste_20150114.doc` – was damals geplant war.
- `Sonstiges/Stuttgart_Braun/` – die `*_CodeDel.docx`-Dateien (DJEM, DJUM, FR2, MML, RLS, WLE,
  WVV) sind code-gelöschte Lesefassungen, dazu die RTF-Originale. Provenienz der
  Stuttgart/Braun-Zuarbeit.

Diese Posten sind bewusst **nicht** ins Repo kopiert (außer dem Generator): sie sind Word-Binaries
und dokumentieren Prozess, nicht Daten. Wer sie braucht, fragt bei KZW an.

## Sonstiges, worauf man stoßen kann

- **Doppelte Ablagen.** `ERLEDIGT/Alte Texte/Carl von Kraus/<SIG> (1).txt` und
  `ERLEDIGT/CvK_KLD_codiert/<SIG>.txt` überschneiden sich. Zehn Paare sind byte-identisch und
  wurden beim Aufnehmen entdoppelt (Spalte `dubletten_im_archiv` im Manifest). Der Rest
  unterscheidet sich und ist doppelt aufgenommen. Ebenso überschneiden sich
  `Neue Texte (zu bearbeiten)` und `Neue Texte Margret` stark.
- **`OVB.txt.bak`, `TA_komplett.txt.bak`.** Backup-Stände. `TA_komplett.txt.bak` ist inhaltlich
  eigenständig und liegt als `linecode/erledigt/tannhauser/ta_komplett-bak.txt` im Repo, weil
  `*.bak` repoweit gitignored ist.
- **Metadaten-Schnipsel.** `Vita_Caroli_Metadata.txt`, `Vita_Caroli_Namen.txt`,
  `Tutsch-kronik-Metadaten.txt`, `Lyrik-Corpus Info.doc`, `Codierungsschema WvV.doc`. Klein, teils
  aufschlussreich für Metadatenfragen, nicht aufgenommen.
- **`ERLEDIGT/Alte Texte/CvKraus - Tanja/`.** RTF-Fassungen der KLD-Texte aus einer
  Hilfskraft-Zuarbeit, nicht codiert.
- **Julias Handover** (`OUTDATED-Texte-mit-Linecode/` mit 291 Texten, `TEXT_DATA_TABLE.xlsx`,
  `Zusammenfassung-Linecode2TEI.pdf`) liegt **nicht** hier, sondern in einem eigenen
  Handover-Ordner, ebenfalls bei KZW. Überschneidet sich inhaltlich mit `linecode/`, ist aber ein
  anderer Stand. Siehe [`docs/LINECODE.md`](../docs/LINECODE.md) → „Source Material".

## Was mit dem Rest passieren soll

Für die 9 GB ist Git das falsche Werkzeug: GitHub blockt Einzeldateien über 100 MB und warnt ab
1 GB Repo-Größe, und Git ist permanent. Der in #248 vorgeschlagene Weg ist ein Zenodo-Deposit mit
eingeschränktem Zugriff; eine DOI besteht bereits
([10.5281/zenodo.20627656](https://doi.org/10.5281/zenodo.20627656)).

Nach dem OCR-Befund wäre der sinnvolle Zuschnitt **Scans und PDFs, also 1,3 GB statt 9 GB**: die
FineReader-Artefakte enthalten keinen eigenen Inhalt. Der FnhdC-Ordner müsste ohnehin
ausgenommen werden. Entschieden ist das noch nicht. Bis dahin gilt: Archiv bleibt lokal bei KZW,
dieses Inventar ist der Zugriffsweg.
