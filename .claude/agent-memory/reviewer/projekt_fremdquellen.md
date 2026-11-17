---
name: projekt-fremdquellen
description: Fremdindizes, Fremdexporte, Monatsläufe, HSC-Datierung, BRE, COR, fyndling, Textreihen
metadata:
  type: project
---
**Naming-Index (#420):** Nachbau mit `01-fetch-and-build-index.py` (PROJECT_ROOT = `parents[3]`) plus `alias-overrides.json` und `naming-explorer.js` in gleicher Tiefe ins Scratch, `--ref <sha>`. Bytevergleich der gz lokal wertlos: Blob-Hash gegen `refs/pull/<N>/head`. bez + epi > mentions nur bei einem Term im selben Record in beiden Gruppen.

**Pferde-Index (#193):** „Verse" hat zwei Einheiten, `Counter((work, citation))` und `Counter(target)` getrennt zählen.

**Fremdexporte nach `sources/` (Glossar #554)**
- PII nicht an der Mail-Regex aufhängen: Zeilendiff Original gegen Bereinigt, dann `Telefon`, `\+\d{2}`, `<address>`, `credit` in `_wp_attachment_metadata`, `/author/`, `?author=`. `PHONE_RE` trifft die nationale Form ohne `Tel:` nicht.
- GitHub-`user-attachments` eines öffentlichen Repos sind ohne Login abrufbar, Löschen des Kommentars löscht die Datei nicht: die Datei-ID nie in Notizen, Commits, Issues.
- `sources/README.md` zählt die Bestände auf: jeder neue Bestand macht die Aufzählung falsch, ohne dass der Diff sie berührt (#397).
- Original nur bei KZW: Bytes und SHA-256 gegen die Glossar-README, `bereinige-export.py` (mit `-E -P`), `cmp` gegen den Blob. Nur `einordnung.json` (Feld `c`) steuert die Kürzungen. `entfallenes-suchen.py`: `AUTO_B` stuft still als (b) ein, nie in `offen`.

**Zotero- und Issue-Monatslauf (#417, #537)**
- Zotero `DOI` und `url` sind Freitext: alle Werte gegen `^10\.\d{4,9}/\S+$` bzw. `^https?://` prüfen, gerenderte `href` greppen.
- Specs über eingefrorene Fremdstände: nimmt die Spec Rohfeld = gerenderter Wert an, oder verdrahtet sie Issue-Nummern eines Zwischenstands? Beides wird beim nächsten Monatslauf rot.
- Das `--check` in `monthly-pages.yml` ist tautologisch (baut erst, prüft dann). Das Gate ist der `--check` in `no-cdn-check.yml`, den Monatslauf-PRs aus dem GITHUB_TOKEN nicht auslösen. Mutationsprobe im Markenbereich (`<!-- PUBLIKATIONEN:START -->`), nicht am ersten `<li` (Navigation).
- `build-publikationen.py`: Autorenzeile, Teamfilter und `verdeckte_team` laufen seit PR #705 über ein Prädikat (`ROLLEN`). Wer eines ändert, prüft die anderen zwei. Mock mit `presenter` + `name` vor einem Teammitglied an Platz 4.
- `verdeckte_team` misst Sichtbarkeit am Nachnamen-Wort in der Zeile, nicht an der Person: ein sichtbarer Namensvetter unterdrückt das „(mit X)".
- Das Feld `autoren` im Stand wird beim Abruf berechnet, nicht beim Bauen: eine Änderung an `autoren()` sieht `--check` erst nach dem nächsten Monatslauf. Nachfahren über die aus `personen` rekonstruierten Creators gegen das gespeicherte Feld.
- „Nicht beschlossen" und Labels als Entscheidungsersatz am ganzen Thread messen, nicht am letzten Kommentar oder am Label (#139, #262).
- Wandert ein Issue zwischen `freigegeben` und `nicht_freigegeben`, wird `docs/FEATURES.md` („Demnächst im Korpus", zählt Beispiele beider Listen) still falsch. Specs mit `if (sichtbar.length === 0)` prüfen nichts, solange `freigegeben` leer ist.

**Handschriftencensus-Datierung (#118, `scripts/ingest/datierung-118/`)**
- Nie selbst abrufen (robots.txt sperrt KI-Agenten), offline gegen `temp/hsc-cache` im Main Worktree.
- Gefährlich ist ein zu frühes notAfter (verworfene Klammerzusätze mit eigener Datierung). Proben mit konstruierten Freitexten über `normalisiere()`, Wortlisten gegen das ganze Vokabular von `REGELN`, Untergrenzen mit `float("nan")` (`nan < 1.0` ist False).

**Weingrüße BRE (#147, `scripts/ingest/bre/`)**
- Proben ohne Schreiben nach `ingest/bre/`: 00 `--offline`, 01 in-process per `runpy` mit umgebogenem `bc.SEGMENTIERUNG`/`bc.INGEST_DIR`, 02 mit `--ausgabe-dir <scratch> --datum <change-Datum>` gegen das eingecheckte TEI diffen (`bre_common.REPO = parents[3]`).
- Zeilennummern aus 02 gegen die Quelle zählen, nicht aus dem Log. `[...]` am Spaltenanfang einer Synopse heißt meist „eingebettet".
- Seit 13.11.2026 ist die Hauptseite „Kategorie:Quelle Weingruß" maßgeblich für die Werkzuordnung (Abgleich 03, Gate in 02 über `ABWEICHUNG_ERKLAERT`). Altschema-Probe: `c02.SCHEMA_RNG` auf eine `git show origin/main:schema/mhdbdb.rng`-Kopie biegen, `main()` mit `--trocken`.
- Ausnahmeschlüssel, die nur die Art tragen (`(zeuge, "reihenfolge", "")`), decken jede künftige Abweichung derselben Art. Jeden Zweig, der ein Abweichungs-dict baut, einzeln proben, nicht nur die, die ein neuer Test deckt.
- `bh.abgleich` paart in `filtere()` die jeweils ersten Vorkommen: ein doppelt geführter Titel erzeugt Schein-`reihenfolge`. Liste je Zeuge und Übersichtstabelle der Hauptseite widersprechen sich, `bh.parse_matrix` liefert die Übersicht.
- **`sources/weingruesse/docling/*.md` (Main Worktree) sind die Steckbriefe 2022 („Erfassung der Quellen“), nicht die Druckfahnen.** Druckfahnentext: `pdftotext -enc UTF-8` auf `wagner-2023-weingruesse-druckfahnen.pdf` daneben. Ein Lecktest gegen docling prüft die falsche Quelle (Runde 1 Phasen, 17.11.2026).
- Phasen 10 bis 21 schreibend proben: `git archive <sha> scripts ingest/bre authority-files schema | tar -x -C <Temp>`, dort laufen lassen, Vergleich mit `diff -rq --strip-trailing-cr` (Archiv hat CRLF). Rerun-Proben: jedes Assign-Skript nach seinem Apply erneut fahren; Zählungen, die nur beim ersten Setzen zählen (18: „mit <expan>“), sind im Rerun 0.
- **Eine Umformulierung gegen den Lecktest gegen die Quelle lesen, nicht nur gegen den Test:** die d4-Neufassung in `zeugen.tsv` (Runde 2, 17.11.2026) kehrte Erst- und Nachdruck um (PDF: Hergot Erstdruck, Wachter Nachdruck; das Wiki vertauscht dazu die VD16-Nummern). Grün heißt nur „keine 6-Wort-Folge“, nicht „sachlich gleich“.

**CoReMA-Pilot COR (#139, `scripts/ingest/cor/`)**
- Quelle ist `../corema` (`data/published/annotated/<buch>.recipes.xml`), nicht GAMS: zuerst `sha256sum` gegen `ingest/cor/quellen.tsv`, dann 01 mit `--ausgabe-dir <scratch> --datum <change-Datum>` und `cmp` aller Ausgaben. Der Konverter vergleicht selbst keine Hashes, er schreibt neue.
- Mutationsproben am Fixture-Helfer `test_cor.lauf()` per Scratch-Skript mit `sys.path` auf den Skriptordner. Ganzlauf-Probe: Konverter plus `schema/mhdbdb.rng` (ohne Includes) in eine Scratch-Kopie gleicher Tiefe, `--buch w1 --trocken --corema-dir <stufe0>`. Text außerhalb von w/pc/note sieht kein Rundlauf.
- `ingest/cor/README.md` trägt eine Zeilentabelle je TSV (Datenzeilen = `wc -l` minus 1), die bei jeder neuen `art` mitwachsen muss. Lizenz: ARI und BRE übernehmen die Quelllizenz, `tei/` steht auf BY-NC-SA, DATA-MODEL.md „Stage 0" verlangt die Klärung vorab.

**fyndling-Beiträge (@neongrau, #366, #376, `ingest/review/139-fyndling/`)**
- Lokal liegt nur `temp/mhdbdb-angebot-207-lemma-vorschlaege.csv` (Siglen `w1` = COR_W1, `mha` = COR_BS1, `mon` = GR1), nicht die spätere 213er-Lieferung: „disjunkt zu den 213" ist lokal nur gegen die 207 messbar, und das so sagen.
- Token-Prüfung: `<w>`/`<pc>`-Folge aus `ingest/cor/COR_*.tei.xml` per lxml, `[[ ]]` gegen Tokentext, `+`-Gruppen auf Lückenlosigkeit, Duplikate über alle IDs einer Zeile. Der `Kontext` lässt `<pc>` weg.
- Agentenerzeugter Text trägt Arbeitsnotizen (`von Claude …`, `Wie B23`, `ev_clean/…`): in `Bedeutung` und `Hinweis` danach greppen, bevor eine README „geprüfte Fassung" stehen bleibt.
- Wörterbuchstellen über `api.woerterbuchnetz.de/open-api/dictionaries/<SIGLE>/`: `lemmata/<lemma>` liefert `bookref` (Band,Spalte,Zeile), `fulltext/<form>` die textids, `kwic/<textid>` den Kontext. Einen `wbnetzid`-Endpunkt gibt es nicht (400).

**Textreihen (#93, `textreihen/`):** Treue gegen marketext.at per `curl` und Skriptvergleich messen, nicht per WebFetch (fasst zusammen). Den Verzeichnisbaum in `CLAUDE.md` liest kein Skript, sein Spiegel ist der Baum in `docs/DEVELOPMENT.md`.
