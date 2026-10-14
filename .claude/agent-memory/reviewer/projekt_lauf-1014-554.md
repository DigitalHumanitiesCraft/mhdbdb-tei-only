---
name: projekt-lauf-1014-554
description: Glossar Kochbuchforschung ins Lexikon (#554, Spur lauf-554, Runde 1 am 14.10.2026): Kommentarnotizen in lexicon.xml prüfen, zwei Einordnungsartefakte, Splitter-Lücke der Entfallen-Suche, comment-attribution.spec.js skaliert mit der Kommentarzahl, Prüfseite regenerieren
metadata:
  type: project
---
Geschrieben 14.10.2026 (Runde 1 zu 92933ebd6). Zahlen sind Eingabe, vor Gebrauch nachmessen. Beim Verdichten gehören die Absätze zu projekt_pruefseiten, querschnitt_tests und projekt_lexikon_variants.

**Zwei Einordnungsartefakte, nur eines steuert.** `ingest/glossar-554/kommentare/*.json` trägt je Eintrag `kuerzung` (gestrafft/gekuerzt) und `kuerz_grund`; `ingest/glossar-554/einordnung.json` trägt `c` (Stücknummern). `kommentare-einfuegen.py` liest nur `einordnung.json`. Differenz messen: Menge `kuerzung == 'gekuerzt'` gegen Menge der Schlüssel mit nichtleerem `c`; in Runde 1 standen 606 und 621 nur im JSON als gekürzt und lagen deshalb in den Daten.

**Why:** Ein zweites Feld, das derselbe Autor führt, sieht aus wie eine Bestätigung und ist keine; der Einfügepfad kennt es nicht.
**How to apply:** Bei jeder Folgerunde zu #554 und bei jedem Ingest mit „gestrafft/gekürzt"-Trennung beide Mengen gegeneinander zählen, bevor die Stichproben beginnen.

**Lücke der Entfallen-Suche (`scripts/ingest/glossar-554/entfallenes-suchen.py`).** `stuecke()` trennt Sätze nur vor Großbuchstabe, „ oder ‚; vor einem geraden `"` (NHD-Zitate im Glossar) nicht. Der verschmolzene Block endet dann oft auf `(Name, S. N)`, und `AUTO_B` (`S\. ?\d+`) stuft ihn still als (b) ein: er erscheint nie in `offen`. So verschwand in 606 brâte der Satz zum „Armen Heinrich". Stichprobe: Vorstufe bauen (`vorstufe-bauen.py <tmp>.json`, 189 Einträge), Original (`enz_t`, `poet_t`) neben `kommentare[gid].text` in eine Datei schreiben und lesen; `m.entfallene(o, k)` aus dem Modul liefert `offen`, `m.stuecke()` die Zerlegung.

**Wortlaut unter KZWs Namen.** Der Export (`sources/glossar-kochbuchforschung/...bereinigt.xml`, Feld `poet`) zeigt, was sie schrieb; zwei Umformulierungen in Runde 1 (ein eingefügtes Verb in 2074, `Nutzer*innen` statt `jede/r/m Nutzer/in` in 606) standen in `lexicon.xml`. `rg -c` über lexicon.xml auf das verdächtige Wort.

**`testing/tests/comment-attribution.spec.js` skaliert mit der Kommentarzahl.** Zwei Tests iterieren über alle Index-Senses mit `comment` und `commentResp` (je ein `page.goto` pro Lemma, Lemmaseite und Playground), globales `timeout: 60000` je Test in `testing/playwright.config.js`. Mit 1 Kommentar grün, mit 97 nicht ausführbar. Außerdem verankert der Test „ein Lemma ohne Kommentar" `lemma_879` = brôt, das als Prüfseitenfall B-2084 noch einen Kommentar bekommen kann.

**Prüfseite #554 nachbauen:** `pruefseite-bauen.py <vorstufe.json> <tmp>.html` (liest tei/, ~2 min), Vergleich mit dem Archiv nach Entfernen von `"commit": "<sha>"`; Fingerprint `98b0af8c14f16cee` bleibt gleich, solange die Fälle gleich sind. Export-Zeilen: `Faelle: 44 = A 17 + B 19 + C 5 + D 1 + E 2`.

**Korpus-Sense-Zählung:** `ana="lexicon.xml#lemma_N_sense_M"` (mit Präfix; `#lemma_` allein trifft nichts). `rg -o --no-filename 'ana="lexicon\.xml#lemma_(N|M)_sense_[0-9]+"' tei | sort | uniq -c`.

**Billige Gates für Lexikon-Diffs:** `check-index-versions.py`, `check-index-version-bump.py --base origin/main`, `check-doc-inventories.py`, `build-pages.py --check`, `doc-count-audit.py --check`, `check-no-em-dash.py --diff-base origin/main`, alle unter 2 min. Index-Delta: Base-Index per `git show origin/main:data/authority-index.json.gz`, je Lemma Felddifferenz zählen (hier nur `senses.comment/commentResp/commentRespName` an 96 Lemmata).

## Runde 2 (14.10.2026, zu da3ee57fc, nach Rebase auf 0258eb9db)

**Zählfallen an diesem Diff.** Abbas Bestandskommentar trägt ebenfalls `contrib_003`: `contrib_003`-Notizen in lexicon.xml = Glossar-Notizen + 1, Lemmata mit Kommentar im Index = Glossar-Lemmata + 1. Die Dezile in UEBERNAHME.md B4 sind `statistics.quantiles(n=10, method='exclusive')` (inclusive weicht ab 181/191). Die Vorstufen-Zeichenzahl (289.860) zählt `enz_t` plus `poet_t` ohne den `\n\n`-Trenner; mit Trenner liegt sie um 2 je übernommener Poetisierung höher. Vorstufe: `vorstufe-bauen.py <scratch>.json` läuft in Sekunden, lxml-Probe über lexicon.xml ebenso; Index- und API-Vergleich gegen `git show origin/main:...` in-process unter einer Minute.

**Das zweite Einordnungsartefakt besteht weiter.** `kuerzung` in `kommentare/*.json` (72 gestrafft, 17 gekuerzt, 31 ohne Feld) widerspricht `einordnung.json` an 382, 387, 518, 579 (dort `c`, im JSON gestrafft), 1905 (Rückfrage E, nicht gekürzt), 2074 und 2084 (Feld fehlt). Steuert nichts; in Runde 2 als B gemeldet.

**Docstring-Falle:** eine Aufzählung von Anführungszeichen in einem ASCII-Docstring (`scripts/` schreibt ASCII) verliert das `„` leicht zum geraden `"`; bei Aussagen über Trennzeichen die Bytes mit `hex(ord(c))` prüfen, nicht die Konsole lesen.

**Nicht gemessen:** Laufzeit der Stichprobe (9 Seitenaufrufe je Test) in comment-attribution.spec.js; `npm test` lief beim Aufrufer parallel, darum keine eigene Playwright-Probe (Port 8080, gemeinsame Ergebnisdatei).
