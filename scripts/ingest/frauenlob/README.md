# Frauenlob-Revision (FR1 / FR2 / FR3)

Skripte zur Revision der drei Frauenlob-Texte nach Issue #236: Rekonstruktion der beim
Ingest verlorenen Parallelüberlieferungs-Ebene in FR3, Bereinigung der Überschriften-Tokens
und Nachtragen der GA-Zählung.

> **Einmalig, nicht plug-and-play.** Die Skripte sind auf die Frauenlob-Linecodes zugeschnitten
> und laufen genau einmal. Sie sind idempotent geschrieben (ein zweiter Lauf ändert nichts),
> dienen aber vor allem der Nachvollziehbarkeit des Umbaus im PR.

## Quelldateien

`source/` enthält die Legacy-Ingest-Vorlagen aus dem MHDBDB-Sharefolder-Backup
(`MHDBDB_Inhaltliches/Texte/ERLEDIGT/`, Dateidatum 2013). Freigabe durch KZW am 2026-07-29,
siehe #236. Der übrige, weit größere Altbestand ist bewusst **nicht** aufgenommen – dazu #248.

| Datei | Herkunft | Inhalt |
|---|---|---|
| `FR3-linecode.txt` | `ERLEDIGT/FR3.txt` | Volltext mit 19-stelligem Legacy-Linecode |
| `FR2-linecode.txt` | `ERLEDIGT/FR2.txt` | dito für FR2 |
| `ga-tonnamen.tsv` | aus `ERLEDIGT/Frauenlob_Bd1.doc` extrahiert | Ton-/Abschnittsnamen der GA Bd. 1 |

### Linecode-Templates

Aus `docs/data/linecode-templates.csv`, Bedeutung der Stellen in `docs/data/linecode-mapping.csv`:

| Sigle | Template | Stellen |
|---|---|---|
| FR1 | `00000000000ddaaa--h` | `dd` Ton, `aaa` Abschnitt, `--` Vers, `h` Überschrift |
| FR2 | `0000000000000dss--h` | `d` Lied, `ss` Strophe, `--` Vers, `h` Überschrift |
| FR3 | `0000000uddaaass---h` | **`u` Parallelüberlieferung**, `dd` Ton, `aaa` Strophe, `ss` Strophe/`lg`, `---` Vers, `h` Überschrift |

Der `@xml:id` im TEI ist der Linecode **ohne führende Nullen**, plus Token-Index:
`0000000105201010010` → `FR3_105201010010_0`. Damit ist jede Quellzeile verlustfrei einem
TEI-Token zuzuordnen – das ist der Join-Schlüssel aller Skripte hier.

### Bekannter Defekt der Quelldatei

**86 Zeilen in `FR3-linecode.txt` haben nur 18 statt 19 Stellen** (eine führende Null fehlt).
Betroffen sind genau zwei Blöcke: VIII,215 `u=1` (29 Zeilen) und V,209 `u=2` (57 Zeilen).
Die Skripte füllen mit `zfill(19)` auf. Wer das übersieht, verliert diese beiden Zeugen
stillschweigend. Die Datei ist absichtlich **unverändert** übernommen, damit sie Quelle bleibt
und nicht stiller Bearbeitung unterliegt.

## Verifikationsstand (2026-07-29, vor dem Umbau)

Abgleich `FR3-linecode.txt` gegen `tei/FR3.tei.xml`:

| | Quelle | TEI |
|---|---|---|
| Strophen (Ton, Nr.) | 127 | 127 |
| Töne | V, VII–XV | V, VII–XV |
| Verse / `<l>` | 9.595 | 9.595 |
| Abweichungen der `u`-Menge | 0 | – |

## Skripte

In dieser Reihenfolge laufen zu lassen; jedes Skript kennt `--dry-run` (außer `01`, das
ohnehin nichts schreibt).

| Skript | Zweck |
|---|---|
| `01-verify-linecode-vs-tei.py` | Abgleich Quelle ↔ TEI, ohne Schreibzugriff. Vorbedingung für alles Weitere und danach als Gate wiederholbar: prüft u-Ebenen, Zahl der `<lg>` je Zeuge, Verssumme und Überschriften-Sitz |
| `02-restore-parallel-level.py` | Führt Töne gleicher `@n` zusammen, hängt `u ≥ 2` als `<div type="parallel">` unter die Strophe |
| `03-headings.py` | Entfernt die 42 Ordnungszahl-Tokens aus dem Textfluss (26 FR1 / 2 FR2 / 14 FR3), setzt 24 `<head>` mit GA-Nummer und Tonnamen, macht die GA-Ebene XIV in FR2 als `div/@n` explizit |
| `04-metadata.py` | Titel aller drei Texte, FR3 auf den Supplementband 2000 (ISBN, Herausgeber, Reihenband), Zotero-Title-Case-Reparatur, Supplement-Relation als `<ref type="supplement">` |
| `05-editorial-decl.py` | Verschiebt die editorischen Eingriffe von `<normalization>` nach `<editorialDecl>` und ersetzt den verstümmelten Legacy-Satz |
| `_tei_io.py` | Kein eigenständiges Skript: gemeinsames Schreiben, stellt die Prolog-Umbrüche wieder her, die `tree.write(xml_declaration=True)` verschluckt |

### Zwei Fallstricke beim Gegenzählen

1. **Quelle 10 Überschriften-Zeilen, TEI 14 entfernte Tokens.** Die Zahlen dürfen nicht
   übereinstimmen: eine Überschriftenzeile der Quelle wird im TEI zu mehreren Tokens
   (römische Zahl plus Punkt), und umgekehrt sind „Etmüllersche Ausgabe" sowie das zweite
   „VII" beim damaligen Ingest gar nicht ins TEI gelangt.
2. **Die `h`-Stelle ist eine Konvention, kein Beweis.** 339 der 620 Templates enden auf `h`,
   die übrigen 281 belegen die letzte Stelle anders. `03-headings.py` prüft deshalb zusätzlich
   den Inhalt (römische Zahl oder Satzzeichen) und bricht bei allem anderen ab, statt zu löschen.

## Zählung von `parallel/@n`

`@n` folgt der **Zählung der Edition**, nicht der `u`-Ziffer: `u=2` wird zu
`<div type="parallel" n="1">`, weil der Supplementband diesen Zeugen als
„Parallelüberlieferung 1" führt. Die `u`-Ziffer bleibt über die `@xml:id`s der Tokens
erhalten und damit verlustfrei rekonstruierbar.
