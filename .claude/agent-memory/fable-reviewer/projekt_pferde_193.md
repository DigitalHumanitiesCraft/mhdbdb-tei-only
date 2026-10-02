---
name: pferde-193
description: Pferde-Explorer (#193, Borek-Index): zwei Vers-Einheiten (Boreks Zitatnummern vs. Korpusziele), die seit Quellversion 3695.2 auseinanderliegen; Pz. 340,29 als Ein-Pferd-Doppel; Zenodo-Versionsabfrage; datierte Altzahlen in ingest/horses/README.md und mapping.py
metadata:
  type: project
---

**„Verse" hat im Pferde-Index zwei Einheiten, und seit Quellversion 2 (hdl:tudatalib/3695.2, 02.10.2026) fallen sie auseinander.** `02-map-citations.py` zaehlt `verse=len(belege[werk])`, also Boreks verschiedene Zitatnummern: 335. Verschiedene Sprungziele (`target`) im Index: 336, vor und nach dem Wechsel gleich, weil Er. 4118 und Er. 4718 schon vorher auf `ER_471800` zeigten. Wer „346 auf N Versen" prueft, muss sagen, welche Einheit.

**Why:** Runde 1 zu #193/state am 02.10.2026: DATA-MODEL sagte „eleven verses are cited by two horses each", gemessen 11 Zitatnummern mit zwei Belegen, davon 10 von zwei Pferden und 1 (Pz. 340,29) zweimal Gringuljete, ein Reimpaar unter einer Nummer mit zwei Zielen (PZ_34029/PZ_34030).

**How to apply:**
- Messrezept: Index per `gzip` laden, `Counter((work, citation))` und `Counter(target)` getrennt zaehlen; die Doppel nach Pferdemenge aufteilen.
- `match`-Verteilung Stand 3695.2: 338 exact, 6 shifted (Pz. 339,24-28 und der zweite Vers unter 340,29), 2 distant (Pz. 604,18/19), 0 unresolved; 9 Belege mit `states`, Puzzat drei davon.
- Altzahlen mit Datum stehen bewusst in `ingest/horses/README.md` (Report vom 08.08.2026, zaehlt dort je Vers: 328 von 336) und in `scripts/ingest/horses/mapping.py` Kopf (337/6/3, Er. 4118 als distant-Beispiel). Nicht als Drift melden, aber als Nachbarschaft nennen, wenn jemand die Zahlen anfasst.
- Harte Kopien der Abweichungszahl ausserhalb des Explorers: `hilfe-playground.html` (Abschnitt „Arthurische Pferde", „neun der 346"); der Explorer selbst zaehlt seit 02.10. aus dem Index.
- Zenodo-Versionen pruefen: `https://zenodo.org/api/records?q=conceptrecid:20627656&all_versions=true` (am 02.10.2026 ein Treffer, v1.0.0 vom 2026-06-10).
- Erstes Auftauchen von `data/horses-index.json.gz` auf main: 87335df86 vom 2026-08-08 (`git log --diff-filter=A`), nicht 09.08.
