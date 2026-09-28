---
name: data-integrity-nummernschemata
description: data-integrity.yml hat zwei Nummernschemata (Kopf 0,1,1a..8 vs. DEVELOPMENT.md 1..15); Zuordnung, Zaehlrezepte, PR-Bot-Kommentare ohne gh (08.09.2026)
metadata:
  type: project
---

`.github/workflows/data-integrity.yml`: der Kopf zaehlt 0, 1, 1a, 1b, 1c, 1d, 2..6, 6b, 6c, 7, 8 (15 Eintraege seit 08.09.2026), `docs/DEVELOPMENT.md` zaehlt 1..15. Zuordnung: 1b=3, 1c=4, 1d=5+6, 6=11, 6b=12, 6c=13. Kein Skript parst den Kopf.

**Messrezepte:** Header-Eintraege mit `^#   \d[a-d]?\. ` zaehlen, Steps per `yaml.safe_load` (20, davon 4 Setup). PR-Kommentare ohne `gh`: WebFetch auf `github.com/.../pull/N` liefert die Bot-Rounds.

**Why:** Zwei Nummernschemata fuer dieselbe Liste; eine Step-Nummer im Auftrag kann aus beiden stammen.
**How to apply:** Bei Step-Nummern im Auftrag zuerst fragen, welches Schema gemeint ist, dann in der Datei nachzaehlen.
