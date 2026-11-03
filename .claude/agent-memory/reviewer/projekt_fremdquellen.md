---
name: projekt-fremdquellen
description: Fremdquellen und Fremdindizes im Review: Naming- und Pferde-Index, Fremdexporte unter sources/, Zotero- und Issue-Monatslauf, Handschriftencensus-Datierung, Weingrüße BRE, Textreihen
metadata:
  type: project
---
Verdichtet 03.11.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Naming-Index (#420):** Nachbau mit `01-fetch-and-build-index.py` (PROJECT_ROOT = `parents[3]`) plus `alias-overrides.json` und `naming-explorer.js` in gleicher Tiefe ins Scratch, `--ref <sha>`. Byte-Vergleich lokal wertlos (zlib): Blob-Hash gegen `refs/pull/<N>/head`. Term-Perspektive: `share` mit `math.floor(x + 0.5)`, bez + epi > mentions nur bei einem Term im selben Record in beiden Gruppen.

**Pferde-Index (#193):** „Verse" hat zwei Einheiten, `Counter((work, citation))` und `Counter(target)` getrennt zählen.

**Fremdexporte nach `sources/` (Glossar #554)**
- **PII nicht an der Mail-Regex aufhängen:** Zeilendiff Original gegen Bereinigt, dann `Telefon`, `\+\d{2}`, `<address>`, `credit` in `_wp_attachment_metadata`, `/author/`, `?author=`. `PHONE_RE` trifft die nationale Form ohne `Tel:` nicht.
- **GitHub-`user-attachments` eines öffentlichen Repos sind ohne Login abrufbar**, Löschen des Kommentars löscht die Datei nicht: die Datei-ID nie in Notizen, Commits, Issues.
- **#397 an `sources/README.md`:** es zählt die Bestände auf (Legacy-Vorlagen, Archiv-„Auszug", Fremdexporte „bisher `glossar-kochbuchforschung/`"). Jeder neue Bestand macht das falsch, ohne dass der Diff die Zeilen berührt.
- Original nur bei KZW: Bytes und SHA-256 gegen die Glossar-README, `bereinige-export.py` (mit `-E -P`), `cmp` gegen den Blob. Nur `einordnung.json` (Feld `c`) steuert die Kürzungen. `entfallenes-suchen.py`: `AUTO_B` stuft still als (b) ein, nie in `offen`.

**Zotero- und Issue-Abrufe mit Monatslauf (#417, #537)**
- **Zotero `DOI` und `url` sind Freitext** (volle URLs im DOI-Feld, `10.…` und nackte Hosts im url-Feld): alle Werte gegen `^10\.\d{4,9}/\S+$` bzw. `^https?://` prüfen, gerenderte `href` greppen. Ausfallproben: querschnitt-messen.
- **#397 an Specs über eingefrorene Fremdstände:** nimmt die Spec nach einer Normalisierung noch Rohfeld = gerenderter Wert an, oder verdrahtet sie Issue-Nummern eines Zwischenstands? Beides wird beim nächsten Monatslauf rot. `not.toContain(rohtitel)` läuft leer, wo die Seite einen bereinigten Titel zeigt.
- **Das `--check` in `monatslauf-seiten.yml` ist tautologisch** (baut erst, prüft dann): „fiel im Monatslauf auf" ist falsch. Das Gate ist der `--check` in `no-cdn-check.yml`, den Monatslauf-PRs aus dem GITHUB_TOKEN nicht auslösen. Mutationsprobe im Markenbereich (`<!-- PUBLIKATIONEN:START -->`, das erste `<li` steht in der Navigation).
- **„Nicht beschlossen" und Labels als Entscheidungsersatz am ganzen Thread messen**, nicht am letzten Kommentar oder am Label (#139, #262).

**Handschriftencensus-Datierung (#118, `scripts/ingest/datierung-118/`)**
- **Nie selbst abrufen** (robots.txt sperrt KI-Agenten), offline gegen `temp/hsc-cache` im Hauptbaum. Werkseite: Handschrift-Links in `<ol class="signaturen">` unter `h3#hss`. JSON: `gnd` Liste, `standorte` Dict, HTML-Entities im Text.
- **Gefährlich ist ein zu frühes notAfter** (verworfene Klammerzusätze mit eigener Datierung). Proben mit konstruierten Freitexten über `normalisiere()`, Wortlisten gegen das ganze Vokabular von `REGELN`, Untergrenzen mit `float("nan")` (`nan < 1.0` ist False). Mehrere works.xml-Werke je HSC-Werk (Fassungen) geben den taq an jede Sigle.

**Weingrüße BRE (#147, `scripts/ingest/bre/`)**
- Proben ohne Schreiben nach `ingest/bre/`: 00 `--offline`, 01 in-process mit umgebogenem `bc.SEGMENTIERUNG`/`bc.INGEST_DIR` per `runpy`, 02 mit `--ausgabe-dir <scratch> --datum <change-Datum>` gegen das eingecheckte TEI diffen. Alt gegen neu über alle Zeugen mit Schein-Repo (`bre_common.REPO = parents[3]`, dazu `temp/bre-wiki`, `ingest/bre/*.tsv`, `schema/mhdbdb.rng`).
- Zeilennummern aus 02 gegen die Quelle zählen, nicht aus dem Log. Der Kopfzeilen-Rückgriff in `segmentiere()` darf `bc.VORSPANN` nicht umgehen. `[...]` am Spaltenanfang einer Synopse heißt meist „eingebettet", nicht „fehlt".

**Textreihen (#93, `textreihen/`):** Treue gegen marketext.at per `curl` und Skriptvergleich messen, nicht per WebFetch (fasst zusammen). Den Verzeichnisbaum in `CLAUDE.md` liest kein Skript, sein Spiegel ist der Baum in `docs/DEVELOPMENT.md`.
