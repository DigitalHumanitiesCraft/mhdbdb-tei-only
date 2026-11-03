---
name: projekt-fremdquellen
description: Fremdquellen und Fremdindizes im Review: Naming-Index (#420), Pferde-Index (#193), Glossar Kochbuchforschung (#554: PII, Einordnung, Entfallen-Suche, Kommentarnotizen), Textreihen-Unterseite (#93), Zotero-/Issue-Monatslauf (#417, #537: DOI-Freitext, urllib-Ausfallproben, Label als Entscheidungsersatz), Handschriftencensus-Datierung (#118: Cache-Struktur, zu frühes notAfter, Werk-Mehrfachzuordnung)
metadata:
  type: project
---
Verdichtet 18.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

## Naming-Index (#420)
- **Nachbau und Pin-Prüfung:** `01-fetch-and-build-index.py` (PROJECT_ROOT = `parents[3]`, schreibt nach data/): Skript + `alias-overrides.json` nach `<scratch>/scripts/ingest/naming/`, `naming-explorer.js` nach `<scratch>/playground/js/ui/tei/`, `--ref <sha>`. Byte-Vergleich lokal wertlos (zlib): Blob-Hash gegen `refs/pull/<N>/head`; nur er sagt bei einem Bot-PR, ob der Runner gebaut hat.
- **Term-Perspektive nachrechnen:** Record einmal je Term (Set über eig/deck/ant/epi); `bez` = Term in eig|deck|ant, `epi` = Term in epi; `share` mit `math.floor(x + 0.5)`; bez + epi > mentions nur, wenn ein Term im SELBEN Record in beiden Gruppen steht.

## Pferde-Index (#193, Borek)
- **„Verse" hat zwei Einheiten:** `02-map-citations.py` zählt `verse=len(belege[werk])` (Boreks verschiedene Zitatnummern); die verschiedenen Sprungziele (`target`) sind eine andere Zahl. Einheit nennen: `Counter((work, citation))` und `Counter(target)` getrennt zählen.

## Glossar Kochbuchforschung (#554, WordPress-Export in sources/)
Bei jedem weiteren Fremdexport nach `sources/` die ersten Punkte vorab abarbeiten; Personendaten im Korpus: projekt-header-spiegel.
- **PII nicht an der Mail-Regex aufhängen** (das Impressum behielt die Telefonnummer). Zeilendiff Original gegen Bereinigt, dann gezielt `Telefon`, `\+\d{2}`, `<address>`, `credit` in `_wp_attachment_metadata`, `/author/`, `?author=`; Ort über das umschließende `<item>`. `PHONE_RE` trifft die nationale Form ohne `Tel:` nicht.
- **GitHub-`user-attachments` eines öffentlichen Repos sind ohne Login abrufbar**; Löschen des Kommentars löscht die Datei nicht. Die Datei-ID gehört nie in Notizen, Commits oder Issues.
- **#397 an `sources/`:** `sources/README.md` nennt „historische Ingest-Vorlagen" und „Auszug aus dem 9,1-GB-Archiv"; jeder neue Nicht-Legacy-Bestand macht das falsch, ohne dass der Diff die Zeilen berührt.
- **Original** nur bei KZW: Bytes und SHA-256 gegen die Glossar-README, dann `bereinige-export.py` (mit `-E -P`, nicht `-I`) und `cmp` gegen den Blob.
- **Nur `einordnung.json` (Feld `c`) steuert die Kürzungen.** Tragen zwei Felder dieselbe Aussage, beide Mengen gegeneinander zählen.
- **Entfallen-Suche (`entfallenes-suchen.py`):** `stuecke()` trennt nur vor Großbuchstabe, „ oder ‚; `AUTO_B` (Fußnote, URL, `S. N`) stuft still als (b) ein, nie in `offen`. Messen: `vorstufe-bauen.py <tmp>.json`, `m.entfallene(o, k)` auf `enz_t`/`poet_t` neben `kommentare[gid].text`; nach jeder Textänderung neu.

## Zotero- und Issue-Abrufe mit Monatslauf (#417, #537, 18.10.2026)
- **Zotero-Felder `DOI` und `url` sind Freitext:** in Gruppe 5043625 standen volle URLs (doi.org, dx.doi, hdl, jstor) im DOI-Feld und `10.…`, `urn:…`, nackte Hosts im url-Feld. Jeder Seitenbau aus Zotero: alle Werte gegen `^10\.\d{4,9}/\S+$` bzw. `^https?://` prüfen und die gerenderten `href` greppen.
- **Ausfallfestigkeit von urllib-Skripten per In-Process-Probe** (Modul per `importlib.util.spec_from_file_location` laden, `modul.urllib.request.urlopen` ersetzen, nur `aktualisieren()` rufen, nichts schreibt): `http.client.IncompleteRead` ist weder OSError noch ValueError, `int(HTTPMessage()["fehlt"])` ist TypeError; beide fallen durch übliche except-Tupel.
- **#397 an Specs über eingefrorene Fremdstände:** nach einer Normalisierung (DOI-Vorsatz abziehen) prüfen, ob die Spec noch Rohfeld = gerenderter Wert annimmt (`find(x => x.doi)` + `href="doi.org/${doi}"`), und ob sie Issue-Nummern oder Wörter eines Zwischenstands fest verdrahtet; beides wird beim nächsten Monatslauf rot, obwohl die Seite stimmt. Umgekehrt läuft `not.toContain(rohtitel)` leer, wo die Seite einen bereinigten oder Plan-Titel zeigt (Demnächst: 5 von 11 am 18.10.); Mutationsprobe über `region_bauen()` mit geleertem Ausschluss.
- **„nicht beschlossen" am ganzen Thread messen, nicht am letzten Kommentar:** #139 (CoReMA) trug am 18.10. den Grund „Aufnahme nicht abgestimmt", der Body zitiert aber KZW 29.05. („danach können wir gerne mit dem CoReMA-Korpus starten") und ihr Kommentar 09.07. die Phase-1-Auswahl; offen war nur das nachrückende Kochbuch.
- **Das `--check` im Monatslauf ist tautologisch:** `monatslauf-seiten.yml` baut die Seiten erst (ohne `--offline`) und prüft danach; eine Handänderung im Markenbereich wird überschrieben, das `--check` bleibt grün (Probe 18.10. an Kopie in scratchpad: vor Bau Exit 1, nach `--offline`-Bau Exit 0, Änderung weg). Ein Satz „lief im Monatslauf, fiel dort auf" ist daher falsch. Seit cf25b8d (18.10.) läuft es auch in `no-cdn-check.yml`; Monatslauf-PRs aus dem GITHUB_TOKEN lösen diesen Workflow nicht aus. Mutationsprobe im Markenbereich setzen (`<!-- PUBLIKATIONEN:START -->`), das erste `<li` der Seite steht in der Navigation; bei Demnächst ein Issue ohne `wait:extern` freigeben (#92 trägt es).
- **Label als Stellvertreter einer Entscheidung gegen den Thread prüfen:** #537 setzte „offene Rechtefrage = `wait:extern`", aber #262 wurde am 06.10. auf `wait:kzw` umgelabelt, obwohl die Nachnutzungsfrage an Trier offen blieb.

## Handschriftencensus-Datierung (#118, `scripts/ingest/datierung-118/`, 21.10.2026)
- **Nie selbst abrufen** (robots.txt sperrt KI-Agenten); offline gegen `temp/hsc-cache` im Hauptbaum lesen. Werkseite: alle Handschrift-Links `href="/N"` stehen in einer `<ol class="signaturen">` unter `h3#hss`, ohne Paginierung (17 Seiten gemessen). Handschrift-JSON: `gnd` ist Liste, `standorte` Dict, Feldtexte tragen HTML-Entities (`&amp;`).
- **taq-Prüfung: die gefährliche Richtung ist ein zu frühes notAfter.** Verworfene Klammerzusätze mit eigener Datierung („Anfang 14. Jh. (um 1325)") erzeugen genau das; Proben mit konstruierten Freitexten über `normalisiere()` per `sys.path`-Import.
- **Eine Wortliste „Datierung in der Klammer" gegen das Vokabular von `REGELN` halten** (Runde 2): der Fix nannte jh/Viertel/Hälfte/um/vor/nach, aber nicht anfang/mitte/ende/oder; „Ende 13. Jh. (oder Anfang 14.)" lief auf bis 1299 statt 1320. Untergrenzen-Prüfungen mit `float("nan")` proben (`nan < 1.0` ist False).
- **10 HSC-Werke tragen mehrere works.xml-Werke** (Fassungen wie AXS/AXV/BAX, KC1/KC2/KCR, dazu work_133/work_126 auf 5720): der Werk-taq geht dann an jede Sigle.

## Weingrüße BRE (#147, `scripts/ingest/bre/`, Runde 1 am 03.11.2026)
- **Proben ohne Schreiben nach `ingest/bre/`:** 00 `--offline` schreibt nichts; 01 schreibt `segmentierung.tsv` hart, darum in-process mit umgebogenem `bc.SEGMENTIERUNG`/`bc.INGEST_DIR` per `runpy` fahren (Ergebnis byte-gleich, 247 Zeilen); 02 mit `--ausgabe-dir <scratch> --datum <change-Datum>` nachbauen und gegen das eingecheckte TEI diffen. Quellzeilen über `bc.lade_seite(bc.transkriptions_titel(sig))["inhalt"].split("\n")` lesen.
- **Zeilennummern aus 02 gegen die Quelle zählen, nicht aus dem Log übernehmen:** in Runde 1 lagen alle um +1 daneben (`erste_zeile` zählt die Überschrift doppelt), und das README übernahm „Zeile 332" aus dem Log.
- **Kopfzeilen-Rückgriff in `segmentiere()` läuft vor der Vorspann-Prüfung:** fette oder rote Zeilen vor dem ersten Text umgehen `bc.VORSPANN` (d5/d6: Drucktitel als `<head>` des ersten Einzeltexts). Kopfzahl je Text gegen die Spalte `ueberschrift` in segmentierung.tsv halten.
- **`[...]` am Spaltenanfang einer Synopse heißt meist „eingebettet in einen anderen Text"** (Infobox: „8 Verse aus [[…]]"), nicht „fehlt"; die Zeilen stehen dann zu Recht im Nachbartext.
- Header-Template aus ARI kopiert („ohne Eingriff in … Strukturhierarchie"): bei BRE baut der Konverter die `<div>`-Gliederung selbst, Teilüberschriften `=== Teil A ===` (D, W1) fallen weg.
- **Runde 2: Alt-gegen-Neu über alle 21 Zeugen** geht mit einem Schein-Repo im Scratch (`bre_common.REPO = parents[3]`: `scripts/ingest/bre/` aus `git show <alt>:`, dazu `temp/bre-wiki`, `ingest/bre/*.tsv`, `schema/mhdbdb.rng` kopieren); Diff nach Einrückung normalisieren, sonst sind D/W1 durch die Teil-`<div>` 8.000 Zeilen „anders". Ergebnis 03.11.: nur Header (4 Zeilen), d5/d6 (Reihentitel), D/W1 (Hülle).
- **Der Zweig rot/fett = `<head>` in `ist_kopfartig` entscheidet keinen Kopf:** abgeschaltet bleiben es 188 `<head>` in 21 Zeugen, alle stehen in der Synopse; seit dem Fixture-Umbau (Runde 2) prüft ihn auch kein Test mehr.
- **Kopfregel-Test (6102f52c0, 03.11.):** 188 `<head>` = 180 aus `segmentiere` + 8 Vorspann; mit Regel aus identische heads (Skript: Quelltext mit `if False:` per `exec` laden, `segmentiere` je Zeuge). Mutanten, die den Test überleben: `isspace`-Filter weg, `if not zeichen` weg (rote Wörter mit ungefärbtem Leerzeichen dazwischen fallen dann still durch; im Bestand 0 solche Zeilen). 02 kennt kein `--offline`, nur 00.

## Textreihen-Unterseite (#93, `textreihen/`)
- **Treue gegen die alte Site messen, nicht lesen** (WebFetch liefert Zusammenfassungen): `curl -s -L -A "Mozilla/5.0" "https://www.marketext.at/Textreihentypologie/?page_id=N"`, Textvergleich per Skript (Tags weg, Anführungszeichen und nbsp normalisieren, Fragmente ab 25 Zeichen als Substring). Erwartete Lücken: WP-Kommentarformulare, „Links noch nicht anklicken", `#DOI (wird nachgeliefert)`, `dokument.html#MHDBDB`.
- **Verzeichnisbaum-Zeile in `CLAUDE.md`:** kein Skript unter `scripts/audit/` liest den Baum; sein Spiegel ist der Baum in `docs/DEVELOPMENT.md`. „kein Abgleich mit genres.xml": `gh issue view 93 --json comments` (wachauer, 2026-10-08).
