---
name: projekt-lauf-1014-554
description: Glossar Kochbuchforschung ins Lexikon (#554, Spur lauf-554): Kommentarnotizen in lexicon.xml prüfen, Einordnungsartefakte, Lücke der Entfallen-Suche, comment-attribution.spec.js, Zählfallen
metadata:
  type: project
---
Verdichtet 15.10.2026. Zahlen vor Gebrauch nachmessen.

- **Nur `einordnung.json` (Feld `c`) steuert die Kürzungen.** Tragen zwei Felder dieselbe Aussage, beide Mengen gegeneinander zählen, bevor Stichproben beginnen.
- **Entfallen-Suche (`scripts/ingest/glossar-554/entfallenes-suchen.py`):** `stuecke()` trennt nur vor Großbuchstabe, „ oder ‚; `AUTO_B` (Fußnote, URL, `S. N`) stuft still als (b) ein, nie in `offen`. Messen: `vorstufe-bauen.py <tmp>.json`, Original (`enz_t`, `poet_t`) neben `kommentare[gid].text`, `m.entfallene(o, k)`; nach jeder Textänderung neu fahren.
- **„Wörtlich“ unter KZWs Namen** = Präfixvergleich gegen Feld `poet` im bereinigten Export (`orig.startswith(neu)`), nicht Stichwortsuche.
- **`comment-attribution.spec.js`** läuft auf fester Stichprobe (ein `page.goto` je Lemma); „Lemma ohne Kommentar“ verankert `lemma_879` (brôt).
- **Zählfallen:** abbas Bestandskommentar trägt auch `contrib_003` (Notizen = Glossar + 1). Dezile: `statistics.quantiles(n=10, method='exclusive')`.
- **Abgleich:** Notiz unter `<sense>` = `escape(text) + ' ' + QUELLE`, Index-`comment` ohne Escape; `zuordnung.tsv` liefert `sense_id`. Prüfseite nachbauen: `pruefseite-bauen.py <vorstufe.json> <tmp>.html` (~2 min), Fingerprint bleibt bei gleichen Fällen gleich.
