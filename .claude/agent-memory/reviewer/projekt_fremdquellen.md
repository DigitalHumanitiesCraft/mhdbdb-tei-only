---
name: projekt-fremdquellen
description: Fremdquellen und Fremdindizes im Review: Naming-Index (#420), Pferde-Index (#193), Glossar Kochbuchforschung (#554: PII, Einordnung, Entfallen-Suche, Kommentarnotizen), Textreihen-Unterseite (#93)
metadata:
  type: project
---
Zusammengelegt 14.10. und 16.10.2026 (u. a. aus dem Lauf-554-Memory). Zahlen sind Eingabe, vor Gebrauch nachmessen.

## Naming-Index (#420)

- **Nachbau und Pin-Prüfung:** `01-fetch-and-build-index.py` (PROJECT_ROOT = `parents[3]`, schreibt nach data/): Skript + `alias-overrides.json` nach `<scratch>/scripts/ingest/naming/`, `naming-explorer.js` nach `<scratch>/playground/js/ui/tei/`, `--ref <sha>`. Byte-Vergleich lokal wertlos (zlib-Version): Blob-Hash gegen `refs/pull/<N>/head`; nur er sagt bei einem Bot-PR, ob der Runner gebaut hat. Alt/neu-Index: Records als (sigle, figur, vers, json) flach diffen.
- **Lindas Repo (lindabeutel/Naming-analysis):** `raw.githubusercontent.com/.../<tag|sha>/data/<Werk>/analysis/figures_by_lemma_<lemma>_<scope>.json`; Committer-Datum per `git clone --depth 5`, `git log -1 --format=%cI` (generatedAt ist UTC).
- **Zitation** steht fest verdrahtet in contributors.xml (contrib_052), DATA-MODEL.md, FEATURES.md; kein Build liest sie. Bei Pin-Bump `git grep` nach alter Version, DOI und Kurzhash.
- **Term-Perspektive nachrechnen:** Record einmal je Term (Set über eig/deck/ant/epi); `bez` = Term in eig|deck|ant, `epi` = Term in epi; `share` mit JS-Rundung (`math.floor(x + 0.5)`); bez + epi > mentions nur, wenn ein Term im SELBEN Record in beiden Gruppen steht.
- **Beispiel-Lemmata in Beschreibungstexten gegen den Index halten** (#485): der Index führt Lindas Lemmaformen, nicht normalisierte Wörterbuch-Ansätze (`rîtaere` statt `rîter`). Messen über works[].figures[fig][].{eig,deck,ant,epi} (ganze Strings); ein Substring-Count trifft daneben `ph` (Versphrasen).
- **Diakritika-Filter (#525):** der Filter in `renderBody` ist `matchesNormalized || matchesFolded` (Lindas Lemmaformen tragen ë und í). **Der `foldDiacritics`-Docstring (text-normalizer.js, „nicht für MHG") hat einen Zwilling in `docs/CONTRACTS.md` §F („Where the fold may be used", Aufrufstellen-Liste mit Zahl).** Messen mit `matchesFolded\|foldDiacritics` über playground/js assets/js.

## Pferde-Index (#193, Borek)

- **„Verse" hat zwei Einheiten:** `02-map-citations.py` zählt `verse=len(belege[werk])` (Boreks verschiedene Zitatnummern); die verschiedenen Sprungziele (`target`) im Index sind eine andere Zahl. Wer „N auf M Versen" prüft, muss die Einheit nennen: Index per `gzip` laden, `Counter((work, citation))` und `Counter(target)` getrennt zählen.
- Datierte Altzahlen stehen bewusst in `ingest/horses/README.md` und im Kopf von `scripts/ingest/horses/mapping.py`: nicht als Drift melden. Schreibweisen: naming `source.license`, horses `source.licence`.

## Glossar Kochbuchforschung (#554, WordPress-Export in sources/)

Bei jedem weiteren Fremdexport nach `sources/` die ersten Punkte vorab abarbeiten; Personendaten im Korpus: projekt-header-spiegel.
- **PII-Prüfung nicht an der Mail-Regex aufhängen** (die Bereinigung ließ im Impressum die Telefonnummer stehen). Rezept: Zeilendiff Original gegen Bereinigt (gleiche Zeilenzahl, da Textersatz), dann gezielt `Telefon`, `\+\d{2}`, `<address>`, `credit` in `_wp_attachment_metadata`, `/author/`, `?author=` suchen. Ort je Fund über das umschließende `<item>` bestimmen, nicht der Seitenangabe des Arbeiters glauben.
- **GitHub-`user-attachments` eines öffentlichen Repos sind ohne Login abrufbar** (curl -sI: 302 auf signierte S3-URL); das Löschen des Kommentars löscht die Datei nicht. Die Datei-ID eines solchen Anhangs gehört nie in Notizen, Commits oder Issues.
- **#397 an `sources/`:** `sources/README.md` sagt im Kopf „historische Ingest-Vorlagen" und „Auszug aus dem 9,1-GB-Archiv"; jeder neue Nicht-Legacy-Bestand macht das falsch, ohne dass der Diff die Zeilen berührt.
- **Original** gibt es nur bei KZW: Bytes und SHA-256 gegen die Glossar-README, dann `bereinige-export.py` (mit `-E -P`, nicht `-I`) und `cmp` gegen den Blob. `PHONE_RE` trifft die nationale Form ohne `Tel:` nicht.
- **Nur `einordnung.json` (Feld `c`) steuert die Kürzungen.** Tragen zwei Felder dieselbe Aussage, beide Mengen gegeneinander zählen, bevor Stichproben beginnen.
- **Entfallen-Suche (`scripts/ingest/glossar-554/entfallenes-suchen.py`):** `stuecke()` trennt nur vor Großbuchstabe, „ oder ‚; `AUTO_B` (Fußnote, URL, `S. N`) stuft still als (b) ein, nie in `offen`. Messen: `vorstufe-bauen.py <tmp>.json`, Original (`enz_t`, `poet_t`) neben `kommentare[gid].text`, `m.entfallene(o, k)`; nach jeder Textänderung neu fahren.
- **„Wörtlich“ unter KZWs Namen** = Präfixvergleich gegen Feld `poet` im bereinigten Export (`orig.startswith(neu)`), nicht Stichwortsuche.
- **Zählfallen:** abbas Bestandskommentar trägt auch `contrib_003` (Notizen = Glossar + 1). `lemmaIndex[l]` ist eine Siglenliste, keine Tokenzahl; Zählregeln (Präfix oder Teilstring) gehören neben jede Zahl.
- **Abgleich:** Notiz unter `<sense>` = `escape(text) + ' ' + QUELLE`, Index-`comment` ohne Escape; `zuordnung.tsv` liefert `sense_id`. `comment-attribution.spec.js` läuft auf fester Stichprobe, „Lemma ohne Kommentar“ verankert `lemma_879` (brôt). Prüfseite nachbauen: `pruefseite-bauen.py <vorstufe.json> <tmp>.html` (~2 min).
- **Zotero-Abgleich (`scripts/review/zotero-abgleich-554.py`):** „Nachname trifft" ist Teilstring (`sur in fold(lastName)`): Bech→Bechstein, Klug→Kluge, Olt→Holtorf, Kern→Wackernagel; Werke ohne Nachname landen per Titelstichwort in `wahrscheinlich`. Ohne Netz messbar: Spalte `zotero_titel` der TSV gegen den Werknamen halten.
- **Klug-Links `--nur-urteile` holt den Seitentitel aus der eingecheckten `klug-links.tsv`**, wenn kein Seitencache da ist: „byte-gleich regeneriert" ist für diese Spalte zirkulär. Ohne `--aus` überschreibt der Lauf die Datei im Repo.
- **KZWs Antwort-JSON** (`kzw-2026-10-15/`): eigener Text = `text` ≠ Seitenvorschlag, nach Streichen von `"`, `\` und Leerraum (die Prüfseite escaped).

## Textreihen-Unterseite (#93, `textreihen/`)

- **Treue gegen die alte Site messen, nicht lesen** (WebFetch liefert nur Zusammenfassungen): `curl -s -L -A "Mozilla/5.0" "https://www.marketext.at/Textreihentypologie/?page_id=N"`, Textvergleich per Skript (Tags weg, Anführungszeichen und nbsp normalisieren, Fragmente ab 25 Zeichen als Substring). Erwartete Lücken: WP-Kommentarformulare, „Links noch nicht anklicken", `#DOI (wird nachgeliefert)`, `dokument.html#MHDBDB`.
- **Zotero-Gruppe 4876216:** `/items/top` zählt weniger als `/items`; das Skript holt `/items/top`, sein SKIP_TYPES-Zweig greift dort nie. Quelle: `gh api repos/Middle-High-German-Conceptual-Database/textseries/git/trees/86c233f08…` gibt die vier Blob-SHAs; `git hash-object` auf `textreihen/data/skos/*` muss sie treffen.
- **SKOS-Browser (`textreihen.js`) gegen `textreihen/data/textreihen.json` nachfahren:** Suche und `pathCount` in ein Node-Skript kopieren und über alle Konzepte laufen lassen (Felder `l`, `a`, `p`). Falle: „mehrere Wege" heißt nicht „mehrere direkte Eltern“, ein Teil der Mehrwegekategorien hat nur einen Elter und erbt die Wege von oben (Runde 1 #93-Vorschläge, 16.10.: 119 von 312). Alternativbezeichnungen können einer nicht-deutschen Bezeichnung `l.en`/`l.la` gleichen (`Herbarium`, `Artes Magicae`).
- **Verzeichnisbaum-Zeile in `CLAUDE.md`:** kein Skript unter `scripts/audit/` liest den Baum; sein Spiegel ist der Baum in `docs/DEVELOPMENT.md`. „kein Abgleich mit genres.xml": `gh issue view 93 --json comments` (wachauer, 2026-10-08).
