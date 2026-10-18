---
name: projekt-fremdquellen
description: Fremdquellen und Fremdindizes im Review: Naming-Index (#420), Pferde-Index (#193), Glossar Kochbuchforschung (#554: PII, Einordnung, Entfallen-Suche, Kommentarnotizen), Textreihen-Unterseite (#93), Zotero-/Issue-Monatslauf (#417, #537: DOI-Freitext, urllib-Ausfallproben, Label als Entscheidungsersatz)
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
- **Label als Stellvertreter einer Entscheidung gegen den Thread prüfen:** #537 setzte „offene Rechtefrage = `wait:extern`", aber #262 wurde am 06.10. auf `wait:kzw` umgelabelt, obwohl die Nachnutzungsfrage an Trier offen blieb.

## Textreihen-Unterseite (#93, `textreihen/`)
- **Treue gegen die alte Site messen, nicht lesen** (WebFetch liefert Zusammenfassungen): `curl -s -L -A "Mozilla/5.0" "https://www.marketext.at/Textreihentypologie/?page_id=N"`, Textvergleich per Skript (Tags weg, Anführungszeichen und nbsp normalisieren, Fragmente ab 25 Zeichen als Substring). Erwartete Lücken: WP-Kommentarformulare, „Links noch nicht anklicken", `#DOI (wird nachgeliefert)`, `dokument.html#MHDBDB`.
- **Verzeichnisbaum-Zeile in `CLAUDE.md`:** kein Skript unter `scripts/audit/` liest den Baum; sein Spiegel ist der Baum in `docs/DEVELOPMENT.md`. „kein Abgleich mit genres.xml": `gh issue view 93 --json comments` (wachauer, 2026-10-08).
