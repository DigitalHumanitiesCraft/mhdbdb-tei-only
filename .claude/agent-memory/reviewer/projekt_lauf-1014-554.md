---
name: projekt-lauf-1014-554
description: Glossar Kochbuchforschung ins Lexikon (#554, Spur lauf-554): Kommentarnotizen in lexicon.xml prüfen, Einordnungsartefakte, Lücke der Entfallen-Suche, comment-attribution.spec.js, Zählfallen
metadata:
  type: project
---
Destilliert 14.10.2026 aus drei Runden. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Nur `einordnung.json` (Feld `c`) steuert die Kürzungen**; `kuerzung` in `kommentare/*.json` wurde danach entfernt. Bei jedem Ingest mit zwei Feldern derselben Aussage beide Mengen gegeneinander zählen, bevor die Stichproben beginnen: der Einfügepfad liest nur eines.

**Lücke der Entfallen-Suche (`scripts/ingest/glossar-554/entfallenes-suchen.py`):** `stuecke()` trennt nur vor Großbuchstabe, „ oder ‚; `AUTO_B` (Fußnote, URL, `S. N`) stuft Stücke still als (b) ein und sie erscheinen nie in `offen`. Messen: `vorstufe-bauen.py <tmp>.json`, Original (`enz_t`, `poet_t`) neben `kommentare[gid].text` lesen, `m.entfallene(o, k)` laufen lassen. Zahlen darüber hängen am Textstand: nach einer Ergänzung neu fahren, nicht die Vorrunde zitieren.

**Wortlaut unter KZWs Namen:** Export `sources/glossar-kochbuchforschung/...bereinigt.xml`, Feld `poet`. „Wörtlich" = Präfixvergleich (`orig.startswith(neu)`, erste Abweichung ausgeben), nicht Stichwortsuche.

**`comment-attribution.spec.js` skaliert mit der Kommentarzahl** (ein `page.goto` je Lemma, 60 s je Test): läuft jetzt auf fester Stichprobe. Der Test „Lemma ohne Kommentar" verankert `lemma_879` (brôt, Prüfseitenfall).

**Zählfallen:** Abbas Bestandskommentar trägt ebenfalls `contrib_003` (Notizen = Glossar + 1). Dezile: `statistics.quantiles(n=10, method='exclusive')`. wîn (1444) und brôt (2084) liegen auf der Prüfseite, nicht in den Daten: keine Drift.

**Abgleich in einem Lauf:** Notiz unter `<sense>` = `escape(text) + ' ' + QUELLE`, Index-`comment` ohne Escape; `zuordnung.tsv` liefert `sense_id`.

**Prüfseite nachbauen:** `pruefseite-bauen.py <vorstufe.json> <tmp>.html` (~2 min); Fingerprint bleibt bei gleichen Fällen gleich.
