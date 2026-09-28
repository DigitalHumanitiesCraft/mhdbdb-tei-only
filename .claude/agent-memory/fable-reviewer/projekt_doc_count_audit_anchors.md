---
name: doc-count-audit-anchors
description: Review-Rezepte fuer scripts/audit/doc-count-audit.py: Anker-Erweiterungen in-process messen, Abdeckungspruefung kennt kein Drift-Fenster, CONTRACTS.md:394 traegt die Lexikonzahl ungegatet (24.09.2026)
metadata:
  type: project
---

Review eines Anker-Umbaus in `scripts/audit/doc-count-audit.py` (Zweig `claude/doc-count-lexicon-anchors`, 24.09.2026, lexicon_entries um `entries`, `lexicon entries`, `lemma pages`, `full records` erweitert).

**Rezept ohne Baumberuehrung:** Modul per `importlib` laden (vorher `os.chdir(worktree)` im Python, die Pfade sind cwd-relativ), dann mutierte Kopien der Zieldateien ins Scratchpad schreiben und `find_stale_numbers(kopie, ist, key)` direkt aufrufen. Alten Anker als Gegenprobe per Monkeypatch auf `NEAR_KEYWORDS[key]`. Das Audit selbst laeuft mit `env -C <worktree> python -X utf8 scripts/audit/doc-count-audit.py --check` (Guard laesst es durch).

**Was der Ziffern-Scan hat und die Selbstpruefung nicht:** `find_stale_numbers` verwirft Zahlen ausserhalb des Drift-Fensters (2 %, bei 43.713 = 874), `anchor_binds_number` kennt kein Fenster. Jede blanke Alternative (`entries`, `records`) laesst deshalb fremde Zahlen die Abdeckung erfuellen: gemessen FEATURES.md:116 "200 entries", :254 "100 entries", TEI-MODEL-AUTH-FILES.md:270 "206 entries", TEI-MODEL.md:971 "125 entries", ARCHITECTURE.md:383 "200 entries", DATA-MODEL.md:371 "10,500 records". Folge: faellt die Lexikonzahl aus so einer Datei heraus, bleibt das Paar gruen statt `no-hit`. Silent-obsolet ist fuer lexicon_entries derzeit unmoeglich (kein INTENTIONALLY_SILENT-Eintrag).

**Offene Nennung:** `docs/CONTRACTS.md:394` schreibt "43,713 entries" und CONTRACTS.md hat kein lexicon_entries-Target. Bindung wuerde :399 ("2026-08-07, 43,879 entries") als Drift melden, weil 166 < 874 und kein Historienmarker greift; also Zahl streichen oder Marker setzen, nicht einfach binden.

**Kommentarfalle:** "42,460 entries" steht nirgends im Bestand (`git grep -c "42,460 entries"` = 0), die Docs schreiben "42,460 variant entries" (2 Stellen) und "42.460 Lemma-Gruppen"; das blanke `entries` trifft "variant entries" gar nicht, weil ANCHOR_SEP kein Wort zulaesst.

**Why:** Anker-Erweiterungen sehen harmlos aus, aber jede blanke Alternative verschiebt die Abdeckungspruefung, nicht den Drift-Scan.
**How to apply:** bei jedem NEAR_KEYWORDS-Diff Abschnitt A/D dieser Probe fahren (alle Zahlen mit Anker ueber alle DOC_TARGETS listen, Fenster-Flag daneben).
