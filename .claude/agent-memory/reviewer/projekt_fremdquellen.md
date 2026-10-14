---
name: projekt-fremdquellen
description: Fremdquellen und Fremdindizes im Review: Naming-Index (#420), Pferde-Index (#193), Glossar-Export (#554, PII), Textreihen-Unterseite (#93, Gegenprüfung gegen die alte Site, Zotero)
metadata:
  type: project
---
Zusammengelegt aus projekt_fremdindizes, projekt_glossar_554 und projekt_93_textreihen, 14.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

## Naming-Index (#420)

- **Nachbau und Pin-Prüfung:** `01-fetch-and-build-index.py` (PROJECT_ROOT = `parents[3]`, schreibt nach data/): Skript + `alias-overrides.json` nach `<scratch>/scripts/ingest/naming/`, `naming-explorer.js` nach `<scratch>/playground/js/ui/tei/` (Marker-Guard), `--ref <sha>`.
- Byte-Vergleich lokal wertlos (zlib-Version): Blob-Hash gegen `refs/pull/<N>/head`; nur er sagt bei einem Bot-PR, ob der Runner gebaut hat. Alt/neu-Index: Records als (sigle, figur, vers, json) flach diffen.
- **Lindas Repo (lindabeutel/Naming-analysis):** `raw.githubusercontent.com/.../<tag|sha>/data/<Werk>/analysis/figures_by_lemma_<lemma>_<scope>.json`; Committer-Datum per `git clone --depth 5`, `git log -1 --format=%cI` (generatedAt ist UTC).
- **Zitation** steht fest verdrahtet in contributors.xml (contrib_052), DATA-MODEL.md, FEATURES.md; kein Build liest sie. Bei Pin-Bump `git grep` nach alter Version, DOI und Kurzhash.
- **Term-Perspektive nachrechnen:** Record einmal je Term (Set über eig/deck/ant/epi); `bez` = Term in eig|deck|ant, `epi` = Term in epi; `share` mit JS-Rundung (`math.floor(x + 0.5)`); bez + epi > mentions nur, wenn ein Term im SELBEN Record in beiden Gruppen steht.
- **Beispiel-Lemmata in Beschreibungstexten gegen den Index halten** (#485): der Index führt Lindas Lemmaformen, nicht normalisierte Wörterbuch-Ansätze (`rîtaere` statt `rîter`). Messen über works[].figures[fig][].{eig,deck,ant,epi} (ganze Strings); ein Substring-Count trifft daneben `ph` (Versphrasen).
- **Diakritika-Filter (#525):** Lindas Lemmaformen tragen ë und í, die `normalizeMHG` nicht kennt; der Filter in `renderBody` ist `matchesNormalized || matchesFolded`, nur in Figuren- und Nenner-Perspektive. **Der `foldDiacritics`-Docstring (text-normalizer.js, „nicht für MHG") hat einen Zwilling in `docs/CONTRACTS.md` §F („Where the fold may be used", Aufrufstellen-Liste mit Zahl).** Messen mit `matchesFolded\|foldDiacritics` über playground/js assets/js.

## Pferde-Index (#193, Borek)

- **„Verse" hat zwei Einheiten:** `02-map-citations.py` zählt `verse=len(belege[werk])` (Boreks verschiedene Zitatnummern); die verschiedenen Sprungziele (`target`) im Index sind eine andere Zahl. Wer „N auf M Versen" prüft, muss die Einheit nennen; „von zwei Pferden zitiert" ist nicht „zweimal zitiert". Messrezept: Index per `gzip` laden, `Counter((work, citation))` und `Counter(target)` getrennt zählen.
- Datierte Altzahlen stehen bewusst in `ingest/horses/README.md` und im Kopf von `scripts/ingest/horses/mapping.py`: nicht als Drift melden. Schreibweisen: naming `source.license`, horses `source.licence`.

## Glossar-Export Kochbuchforschung (#554, WordPress-Export in sources/)

Bei jedem weiteren Fremdexport nach `sources/` diese Punkte vorab abarbeiten; Personendaten im Korpus: [[header-spiegel]].
- **PII-Prüfung nicht an der Mail-Regex aufhängen.** Die Bereinigung traf alle Mail-Vorkommen, ließ aber im Impressum die Telefonnummer der Herausgeberin neben der entfernten Mailadresse stehen. Rezept: Zeilendiff Original gegen Bereinigt (gleiche Zeilenzahl, da Textersatz), dann gezielt `Telefon`, `\+\d{2}`, `<address>`, `credit` in `_wp_attachment_metadata`, `/author/`, `?author=` suchen. Ort je Fund über das umschließende `<item>` bestimmen, nicht der Seitenangabe des Arbeiters glauben.
- **GitHub-`user-attachments` eines öffentlichen Repos sind ohne Login abrufbar** (curl -sI: 302 auf signierte S3-URL). Ein „Original nur als Anhang in #N" ist öffentlich, und das Löschen des Kommentars löscht die Datei nicht (gemessen 10.10.: HTTP 200 danach). Die Datei-ID eines solchen Anhangs gehört nie in Notizen, Commits oder Issues.
- **#397 an `sources/`:** `sources/README.md` sagt im Kopf „historische Ingest-Vorlagen" und „Auszug aus dem 9,1-GB-Archiv"; jeder neue Nicht-Legacy-Bestand macht das falsch, ohne dass der Diff die Zeilen berührt.
- **Original** gibt es nur bei KZW: Bytes und SHA-256 gegen die Glossar-README, dann `bereinige-export.py` (mit `-E -P`, nicht `-I`) und `cmp` gegen den Blob. `PHONE_RE` trifft die nationale Form ohne `Tel:` nicht.

## Textreihen-Unterseite (#93, `textreihen/`)

- **Treue gegen die alte Site messen, nicht lesen.** WebFetch liefert nur Zusammenfassungen. Geht: `curl -s -L -A "Mozilla/5.0" "https://www.marketext.at/Textreihentypologie/?page_id=N"` nach `%TEMP%\fr93\old\`, dann Textvergleich per Skript (Tags weg, typografische Anführungszeichen und nbsp normalisieren, Fragmente ab 25 Zeichen als Substring suchen). Erwartete Lücken: WP-Kommentarformulare, der Hinweis „Links noch nicht anklicken" (Browser), `#DOI (wird nachgeliefert)`, `dokument.html#MHDBDB`. Der Tippfehler „Texreihentypologie" (about) steht so im Original.
- **Zotero-Gruppe 4876216:** `/items/top` zählt weniger als `/items` (dort auch attachment und note); das Skript holt `/items/top`, sein SKIP_TYPES-Zweig greift dort nie. `include=bib` liefert `<div class="csl-bib-body"><div class="csl-entry">…</div></div>`. Schnappschuss gegen Zotero: `/items/top?format=versions` liefert `{key: version}`, `Last-Modified-Version` mitlesen. `--check` des Bibliografie-Skripts ist der lesende Lauf.
- **Quelle:** `gh api repos/Middle-High-German-Conceptual-Database/textseries/git/trees/86c233f08…` gibt die vier Blob-SHAs; `git hash-object` auf `textreihen/data/skos/*` muss sie treffen.
- **Verzeichnisbaum-Zeile in `CLAUDE.md`:** kein Skript unter `scripts/audit/` liest den Baum; sein Spiegel ist der Baum in `docs/DEVELOPMENT.md` (dort steht auch `examples/`, in `CLAUDE.md` nicht). Datenstand: `git hash-object` gegen die README-Tabelle; „kein Abgleich mit genres.xml": `gh issue view 93 --json comments` (wachauer, 2026-10-08). `marketext.at/Textreihentypologie/` antwortet weiter mit 200, „former" meint die Herkunft. Skripte unter `%TEMP%`: [[querschnitt-umgebung]].
