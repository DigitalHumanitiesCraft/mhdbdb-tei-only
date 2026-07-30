# Legacy-Quelldateien aufnehmen und inventarisieren

Skripte zu [Issue #248](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/248).
Sie erzeugen [`sources/`](../../../sources/): die codierten Legacy-Ingest-Dateien plus das
Inventar des Quellarchivs.

> **Laufen nicht in CI.** Die Skripte brauchen Lesezugriff auf ein lokales, 8 GB großes Archiv,
> das bewusst nicht im Repo liegt. Sie sind hier, damit `sources/` reproduzierbar und der Weg
> dorthin prüfbar ist, nicht als Teil eines Builds.

## Voraussetzung

`$ARCHIV` ist der lokale Pfad zu `MHDBDB_Inhaltliches/Texte/ERLEDIGT/` im
MHDBDB-Sharefolder-Backup (OneDrive von KZW). Nur Python-Standardbibliothek, kein `lxml`, damit
auch das Default-Python ohne Zusatzpakete reicht.

## Ablauf

```bash
ARCHIV="/pfad/zu/MHDBDB_Inhaltliches/Texte/ERLEDIGT"
SCAN=/tmp/linecode-scan.csv

python scripts/ingest/legacy-sources/01-scan-linecode.py "$ARCHIV" "$SCAN"
python scripts/ingest/legacy-sources/03-build-sources.py "$ARCHIV" "$SCAN" .
python scripts/ingest/legacy-sources/04-inventory.py     "$ARCHIV" .
```

| Skript | Zweck |
|---|---|
| `01-scan-linecode.py` | Findet die Plaintext-Dateien mit Legacy-Linecode. Schreibt eine Zwischen-CSV, kein Repo-Schreibzugriff |
| `02-scan-binaries.py` | Diagnose: welche Word-/RTF-Dateien tragen Linecodes? Beantwortet, für welche Sigeln nur eine binäre codierte Fassung existiert. Reine stdout-Ausgabe |
| `03-build-sources.py` | Kopiert die codierten Dateien nach `sources/linecode/` und schreibt `sources/linecode-manifest.csv` |
| `04-inventory.py` | Schreibt `sources/erledigt-inventar.csv` und gibt die Tabellen für `sources/INVENTAR-ERLEDIGT.md` aus |

Schritt 01 dauert einige Minuten, weil OneDrive die Dateien beim ersten Zugriff einzeln
herunterlädt.

## Wozu 02 gebraucht wird

`02-scan-binaries.py` läuft nur bei Bedarf und schreibt nichts. Es unterscheidet echte codierte
Dateien von solchen, die nur Seitenzahlen enthalten, über die Trefferdichte: Grundrauschen liegt um
0,5 Treffer je KB, echte codierte Dateien bei 4 bis 13. Ergebnis des letzten Laufs steht in
[`sources/INVENTAR-ERLEDIGT.md`](../../../sources/INVENTAR-ERLEDIGT.md) und benennt vier
Korpustexte (`OVW`, `OSW`, `MSG`, `MSW`), deren codierte Fassung nur als Word-Datei existiert.

## Entscheidungen, die in den Skripten stecken

- **Schwelle für „codiert":** mindestens 50 % der nichtleeren Zeilen beginnen mit einer
  Ziffernfolge. In der Praxis liegen die Treffer bei 95 bis 100 %, die Lücke dazwischen ist leer.
- **Byte-identisch kopieren, nie normalisieren.** Auch defekte Codes bleiben stehen (86 Zeilen in
  `fr3.txt` haben nur 18 statt 19 Stellen). `sources/.gitattributes` verhindert die
  EOL-Konversion, sonst wären die Prüfsummen im Manifest wertlos.
- **Namen slugifiziert, Inhalt nicht.** Der Originalpfad steht in der Manifest-Spalte `quelle`.
- **Entdoppelung nach Inhalt.** `Alte Texte/Carl von Kraus/<SIG> (1).txt` und
  `CvK_KLD_codiert/<SIG>.txt` überschneiden sich; bei byte-gleichem Inhalt gewinnt der
  `CvK_KLD_codiert`-Pfad, der andere wird im Manifest als Dublette vermerkt.
- **Arbeitskopien werden geprüft.** Acht Dateien liegen zusätzlich in `ingest/wvv/` und
  `scripts/ingest/frauenlob/source/`. `03-build-sources.py` bricht ab, wenn eine davon vom Archiv
  abweicht.
