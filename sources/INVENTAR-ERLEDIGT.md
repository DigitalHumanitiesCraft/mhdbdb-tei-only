# Inventar des Quellarchivs `ERLEDIGT/`

Verzeichnis dessen, was im Legacy-Archiv **außer** den hier aufgenommenen codierten Dateien noch
liegt. Zweck: wenn bei einer Korpusfrage Unklarheit auftaucht, soll auffindbar sein, ob es dazu
lokal noch einen Scan, eine Vorstufe oder eine Lesefassung gibt, ohne dass jemand 8 GB durchsucht
oder einen Druck aufschlägt.

- **Ort:** `MHDBDB_Inhaltliches/Texte/ERLEDIGT/` im MHDBDB-Sharefolder-Backup, OneDrive von KZW.
  Nur lokal, kein Repo, kein Netzlaufwerk. Zugriff über KZW.
- **Stand:** aufgenommen 2026-07-30.
- **Umfang:** 17.373 Dateien, 8,1 GB.
- **Dateiweises Verzeichnis:** [`erledigt-inventar.csv`](erledigt-inventar.csv), 2.923 Zeilen.
  Enthält alles außer den 14.450 FineReader-Projektdateien. Spalten: `folder`, `file`, `ext`,
  `kategorie`, `bytes`, `geaendert`.

## Was drin ist, nach Kategorie

| Kategorie | Dateien | Größe | Im Repo? |
|---|---|---|---|
| OCR-Artefakte (`.frdat`, `.aux`, `.dat`, `.opt`, `.hdr`, `.lock`) | 14.450 | 7.381 MB | nein |
| Text (`.txt`, `.doc`, `.rtf`, `.docx`, `.dot`, `.wbk`, `.xml`, dazu `.ashx`, `.TEX`, `.xls`) | 1.437 | 172 MB | teilweise, siehe unten |
| Scans (`.tif`, `.jpg`, `.bmp`, `.png`) | 1.257 | 632 MB | nein |
| PDF | 203 | 131 MB | nein |
| ZIP | 26 | 5 MB | nein |

Aufgenommen ist daraus genau eine Schicht: 302 codierte Ingest-Dateien, 24,6 MB, in
[`linecode/`](linecode/).

## Ordnerübersicht

| Ordner | Dateien | Größe | Zusammensetzung |
|---|---|---|---|
| `MR1` | 1.492 | 3.711 MB | FineReader-Projekt, kein Text-Output |
| `Alte Texte` | 5.268 | 2.478 MB | 4.530 OCR-Artefakte, 405 Text, 311 Scans, 21 ZIP |
| `FLG1` | 1.955 | 755 MB | FineReader-Projekt, kein Text-Output |
| `RVB1` | 5.205 | 547 MB | FineReader-Projekt, 9 Scans, 2 PDF |
| `König vom Odenwald` | 770 | 190 MB | 682 OCR-Artefakte, 58 Scans, 30 Text (inkl. `KVO.txt` codiert) |
| `(root)` | 109 | 139 MB | 103 Text, 4 PDF, 2 ZIP |
| `Der Marner` | 242 | 103 MB | 236 Seitenscans, 6 Text (`MML`, `MRL`, `MRS` codiert) |
| `Heinrich von dem Türlin, Der Mantel` | 350 | 83 MB | FineReader-Projekt, 48 Scans, 2 Text |
| `Der Mantel` | 302 | 65 MB | FineReader-Projekt, 1 Scan |
| `Jenaer Meißner` | 80 | 56 MB | 78 Seitenscans, 2 Text (`DJEM` codiert) |
| `Frauenlob_Bd2` | 310 | 55 MB | 196 Seiten-PDFs, 110 Scans, 4 RTF |
| `Textexport-Dateien_Feb2017` | 644 | 49 MB | Volltextexport 2017, siehe unten |
| `Der junge Meißner` | 91 | 19 MB | 87 Seitenscans, 4 Text (`DJUM` codiert) |
| `Der Mantel Bilder` | 47 | 18 MB | 47 Seitenscans |
| `Rumelant von Sachsen` | 139 | 12 MB | 134 Seitenscans, 5 Text (`RLS` codiert) |
| `Tannhäuser` | 103 | 12 MB | 53 Text (Teilstücke I bis XVI codiert), 50 Scans |
| `Freidank` | 40 | 11 MB | 38 Seitenscans, 2 Text |
| `Friedrich von Sonnenburg` | 52 | 9 MB | 50 Seitenscans, 2 Text |
| `Neidhart-c` | 7 | 3 MB | 4 codierte Fassungen von `NEIC` |
| `SchweizerMinnesaengerCod` | 31 | 2 MB | 29 codierte Dateien, alle aufgenommen |
| `Kochrezepttextsammlungen` | 49 | 1 MB | Unterordner `fertig codiert` mit 15 codierten Dateien |
| `CvK_KLD_codiert` | 70 | 1 MB | 70 codierte Dateien (Carl von Kraus, KLD), alle aufgenommen |
| `Kaiserchronik` | 9 | 1 MB | `KAIS*.TXT`, nicht codiert |
| `Tundalus` | 8 | 1 MB | `TUN`-Vorstufen, HTML-Export |

## Die vier großen OCR-Projekte

`MR1` (3,7 GB), `Alte Texte/RF` und `Alte Texte/SUW` (je etwa 100 MB), `FLG1` (755 MB), `RVB1`
(547 MB), `Der Mantel` und `König vom Odenwald` sind ABBYY-FineReader-Projektordner. Sie enthalten
**keinen extrahierbaren Text**, nur `batch.options.xml` und die internen `.frdat`-Container mit
Seitenbild und Erkennungsergebnis. Aufmachen geht nur mit FineReader.

Praktische Folge: als Rückfrageinstanz sind sie fast wertlos, weil das brauchbare Ergebnis jeweils
schon als korrigierter Text daneben liegt. Wer ein Seitenbild braucht, greift zu den `*Bilder`-
Ordnern oder den PDFs.

## Seitenscans, nach Werk

Nutzbar, wenn eine Stelle im TEI zweifelhaft ist und der Druck geprüft werden muss.

| Werk | Scans | Ort |
|---|---|---|
| Der Marner | 236 TIF | `Der Marner/Der Marner Bilder/` |
| Der Meißner (Jenaer Liederhandschrift) | 78 TIF | `Jenaer Meißner/Der Meißner der Jenaer Liederhandschrift Bilder/` |
| Rumelant von Sachsen | 134 TIF | `Rumelant von Sachsen/Rumelant  von Sachsen Bilder/` |
| Frauenlob Bd. 2 | 196 PDF (S. 152 ff.) + 110 TIF | `Frauenlob_Bd2/PDFs/`, `Frauenlob_Bd2/Frauenlob Ton X Bilder/` |
| Der junge Meißner | 87 TIF | `Der junge Meißner/Der Junge Meißner Bilder/` |
| Der Mantel | 47 TIF | `Der Mantel Bilder/`, dazu `Heinrich von dem Türlin, Der Mantel/Der Mantel Bilder/` |
| Friedrich von Sonnenburg | 50 TIF | `Friedrich von Sonnenburg/friedrich von Sonnenburg Bilder/` |
| Freidank | 38 TIF | `Freidank/Freidank Bilder/` |
| König vom Odenwald | 58 | `König vom Odenwald/König vom Odenwald Bilder/` |
| Tannhäuser | 50 | `Tannhäuser/Tannhäuser Bilder/`, `Tannhäuser/Scans_unbearb/` |
| diverse (`Alte Texte`) | 311 | `Alte Texte/RF/`, `SUW/`, `ML1` bis `ML26` |

Vier vollständige Editions-PDFs liegen direkt im Wurzelverzeichnis: `Appolonius-cpg154.pdf`
(86 MB), `Reinfrid von Braunschweig.pdf` (13 MB), `Hugo-von-Montfort_EdHofmeister.pdf`,
`Lamprecht von Regensbg.pdf`.

## Volltextexport Februar 2017

`Textexport-Dateien_Feb2017/`, 644 Dateien, 49 MB. Eine Datei je Sigle, reiner Lesetext **ohne**
Linecode, Stand 2017-02-24. 639 von 640 Sigeln stehen bereits als TEI im Repo, nur `VSP` nicht;
umgekehrt fehlen die 28 späteren Zugänge wie WZB.

Wert liegt in der **unabhängigen Gegenprobe** für Struktur- und Umfangsfragen: in #236 hat der
Export die Verszahlen aller 13 GA-Abschnitte von FR1 bestätigt, ohne den Druck zu bemühen.
Dieselbe Prüfung dürfte bei #23, #228 und künftigen Ingest-Issues wieder gebraucht werden.

**Nicht aufgenommen.** In #248 ist das eine eigene, noch offene Entscheidung. Solange sie aussteht,
läuft der Zugriff über KZW lokal.

## Codierte Dateien, die nur als Word-Datei existieren

Hier ist die Lücke: für vier Korpustexte liegt eine codierte Fassung im Archiv, aber nur im
Word-Binärformat. `.doc`/`.dot`/`.wbk` sind weder diffbar noch reviewbar, und eine Extraktion
wäre ein abgeleitetes Artefakt und keine Quelle. Deshalb bewusst **nicht** aufgenommen, aber hier
verzeichnet, damit die Lücke nicht unsichtbar bleibt.

| Datei | Größe | Codes | Korpustext | Codierte `.txt` vorhanden? |
|---|---|---|---|---|
| `OsvoWo.doc`, `OvW.doc` | je 0,98 MB | 7.575 | `OVW` / `OSW`, Oswald von Wolkenstein | nein |
| `MSG-Endfassg.doc` | 0,46 MB | 4.511 | `MSG`, Mönch von Salzburg, geistliche Lieder | nein |
| `MSW-Endfassg.dot` | 0,30 MB | 2.246 | `MSW`, Mönch von Salzburg, weltliche Lieder | nein |
| `RVBR-backup.doc` | 2,08 MB | 27.627 | `RVBR` | ja, `linecode/rvbr.txt` |
| `MR2.doc` | 0,73 MB | 8.986 | `MR2` | ja, `linecode/mr2.txt` |
| `Alte Texte/Backup of ADP.wbk` | 0,69 MB | 8.417 | `ADP` | ja, `linecode/alte-texte/adp.txt` |
| `Rumelant von Sachsen_cod_02.doc` | 0,26 MB | 1.844 | `RLS` | ja, `linecode/rumelant-von-sachsen/rls.txt` |

Spalte „Codes" ist die Zahl der gefundenen Linecode-Ziffernfolgen im Rohbytestrom, ermittelt mit
`scripts/ingest/legacy-sources/02-scan-binaries.py`. Die einzige codierte Nicht-`.txt`-Datei, die
aufgenommen ist, ist `Frauenlob_Bd2-codiert.rtf`: RTF ist ein Textformat, das Git behandeln kann.

Wenn `OVW`, `OSW`, `MSG` oder `MSW` einmal eine Struktur-Diagnose brauchen, ist der Weg: die
Word-Datei bei KZW anfordern, in UTF-8-Text konvertieren und erst dann als Quelle behandeln.
Alternativ liefert ein frischer Export aus dem Alt-MHDBDB dieselbe Information sauberer, siehe
[`docs/LINECODE.md`](../docs/LINECODE.md) → „Live exports from MHDBDB-old".

## Sonstiges, worauf man stoßen kann

- **Doppelte Ablagen.** `Alte Texte/Carl von Kraus/<SIG> (1).txt` und `CvK_KLD_codiert/<SIG>.txt`
  überschneiden sich. Zehn Paare sind byte-identisch und wurden beim Aufnehmen entdoppelt (Spalte
  `dubletten_im_archiv` im Manifest). Der Rest unterscheidet sich und ist doppelt aufgenommen.
- **`OVB.txt.bak`, `TA_komplett.txt.bak`.** Backup-Stände. `TA_komplett.txt.bak` ist inhaltlich
  eigenständig und liegt als `linecode/tannhauser/ta_komplett-bak.txt` im Repo, weil `*.bak`
  repoweit gitignored ist.
- **Metadaten-Schnipsel.** `Vita_Caroli_Metadata.txt`, `Vita_Caroli_Namen.txt`,
  `Tutsch-kronik-Metadaten.txt`, `Lyrik-Corpus Info.doc`, `Codierungsschema WvV.doc`. Klein, teils
  aufschlussreich für Metadatenfragen, nicht aufgenommen.
- **`Alte Texte/CvKraus - Tanja/`.** RTF-Fassungen der KLD-Texte aus einer Hilfskraft-Zuarbeit,
  nicht codiert.
- **Julias Handover** (`OUTDATED-Texte-mit-Linecode/` mit 291 Texten, `TEXT_DATA_TABLE.xlsx`,
  `Zusammenfassung-Linecode2TEI.pdf`) liegt **nicht** hier, sondern in einem eigenen
  Handover-Ordner. Überschneidet sich inhaltlich mit `linecode/`, ist aber ein anderer Stand.
  Siehe [`docs/LINECODE.md`](../docs/LINECODE.md) → „Source Material".

## Was mit dem Rest passieren soll

Für die 8 GB ist Git das falsche Werkzeug: GitHub blockt Einzeldateien über 100 MB und warnt ab
1 GB Repo-Größe, und Git ist permanent. Der in #248 vorgeschlagene Weg ist ein Zenodo-Deposit mit
eingeschränktem Zugriff; eine DOI besteht bereits
([10.5281/zenodo.20627656](https://doi.org/10.5281/zenodo.20627656)). Das ist noch nicht
entschieden. Bis dahin gilt: Archiv bleibt lokal, dieses Inventar ist der Zugriffsweg.
