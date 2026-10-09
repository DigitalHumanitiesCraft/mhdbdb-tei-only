---
name: projekt-93-textreihen
description: Review der Unterseite textreihen/ (#93): wie die alte Site marketext.at gegengeprüft wird, Zotero-Endpunkte, was Runde 1 (09.10.2026) gemessen und gefunden hat
metadata:
  type: project
---

Runde 1 am 09.10.2026 auf `claude/93-textreihen` (HEAD 78896b814, Basis 99241b58d).

**Treue gegen die alte Site messen, nicht lesen.** WebFetch liefert nur Zusammenfassungen.
Geht: `curl -s -L -A "Mozilla/5.0" "https://www.marketext.at/Textreihentypologie/?page_id=N"`
nach `%TEMP%\fr93\old\`, dann Textvergleich per Skript (Tags weg, typografische
Anführungszeichen und nbsp normalisieren, Fragmente ab 25 Zeichen als Substring suchen).
Zuordnung: 9 about, 11 how-to, 195 use-cases, 13 outreach, 15 bibliography (Liste),
116 bibliography (Literatursuche/Tags), 30 browser, p=161 aufruf-zur-mitarbeit,
p=292 poster, `/` index. Erwartete Lücken: WP-Kommentarformulare, der Hinweis "Links noch
nicht anklicken" (Browser), `#DOI (wird nachgeliefert)`, `dokument.html#MHDBDB`.
Der Tippfehler "Texreihentypologie" (about) steht so im Original.

**Zotero-Gruppe 4876216:** `/items/top` meldet `Total-Results: 190`, `/items` 205
(12 attachment, 3 note). Das Skript holt `/items/top`, sein SKIP_TYPES-Zweig greift
dort nie. `include=bib` liefert `<div class="csl-bib-body"><div class="csl-entry">…</div></div>`.

**Quelle:** `gh api repos/Middle-High-German-Conceptual-Database/textseries/git/trees/86c233f08…`
gibt die vier Blob-SHAs; `git hash-object` auf `textreihen/data/skos/*` muss sie treffen.

**Why:** Runde 2 soll die Befunde von Runde 1 nachsehen, nicht die Messung neu erfinden.
**How to apply:** Befunde Runde 1: greedy `ENTRY_RE` in `build-textreihen-bibliography.py`
(jeder Eintrag endet auf `</div>`), `decodeURIComponent` in `fromHash` ohne try/catch,
Spec-Titel "Quelldateien sind der Commit" ohne Hash-Prüfung, Auftrags-"17 Seiten" sind 15
(PAGES) plus 2 MATOMO_PAGES ohne Footer, `--offline` druckt "0 übersprungen" als Zahl.
Siehe [[querschnitt-umgebung]] für Skripte unter `%TEMP%`.
