# WZB Ingest Pipeline

Annotations-Pipeline für die **Wenzelsbibel** (Sigle `WZB`, Wien ÖNB Cod. 2759–2764). Implementiert das Drei-Phasen-Muster (Lemmatisierung, POS, Sense), das als Vorbild für künftige Neu-Aufnahmen dient. Die Wenzelsbibel war 2026-04 die erste vollständige Aufnahme nach dem konsolidierten Schema (#32) und Workflow.

> **Nicht plug-and-play.** Die Skripte enthalten WZB-spezifische Pfade, Sigle-Konstanten und Heuristiken. Pro neuem Text adaptiert das Kernteam Sigle, Pfade und text-spezifische Eigenheiten. Siehe [hilfe-daten-beitragen.html §5](../../../hilfe-daten-beitragen.html) für die Beschreibung des allgemeinen Musters.

## Phasen-Übersicht

### Encoding-Cleanup (One-time)
| Skript | Zweck |
|--------|-------|
| `wzb-encoding-cleanup.py` | Historisierte Initialen, Josua.0-Klassifikation, Transition2.1-Typ, anonyme Prologus-Divs |
| `wzb-convert-seg-pc.py` | `<seg type="pc">` → `<pc join="left\|right">` nach Vorgänger-Heuristik |

### Strukturelle Bereinigung
| Skript | Zweck |
|--------|-------|
| `wzb-structural-cleanup.py` | Stript Annotation von `<fw>`/`<surplus>`, normalisiert CAPITULUM-Marker zu `<head type="chapter">` |
| `wzb-structural-fix.py` | `@type="chapter"` auf nummerierten Divs; `<head type="chapter">` aus Zeilenfluss an Div-Anfang mit `<milestone>` |

### Phase 1 — Lemmatisierung
| Skript | Zweck |
|--------|-------|
| **`wzb-auto-match.py`** | **Kanonisch.** Normalisiert Wortformen, matched gegen variants.xml/lexicon.xml, schreibt `@lemmaRef` für eindeutige Treffer |
| `wzb-generate-tsv.py` | Generiert Phase-1b-TSV-Template aus Auto-Match-Report |
| `wzb-extract-unmatched.py` | Extrahiert unmatchte Formen für Lexikon-Lücken-Analyse |
| `wzb-bulk-resolve.py` | Appliziert TSV-Auflösungen auf ambige Zeilen in `wzb-disambiguation.tsv` |
| `wzb-apply-lemmarefs.py` | Schreibt Phase-1b-Resolutionen aus TSV zurück ins TEI |
| `wzb-pending-review.py` | Verdichtet Disambiguation-TSV zu per-Form-Aggregat |
| `wzb-patch-rows.py` | Einzelzeil-Patch für Minderheits-Ausnahmen nach `xml_id` |

### Phase 2 — POS-Tagging
| Skript | Zweck |
|--------|-------|
| **`wzb-pos-assign.py`** | **Kanonisch.** Auto-assign `@pos` für Einlemma-Einträge; Multi-POS in `wzb-pos-pending.tsv` |
| `wzb-pos-bulk-resolve.py` | Batch-Auflösung auf Pending-TSV (nach lemma_id oder form) |
| `wzb-pos-apply.py` | Schreibt aufgelöste `@pos` aus Pending-TSV ins TEI |

### Phase 3 — Sense / Bedeutungsauflösung
| Skript | Zweck |
|--------|-------|
| **`wzb-sense-assign.py`** | **Kanonisch.** Auto-assign `@ana` für Einsense-Lemmata; `@corresp` via Varianten-Lookup |
| `wzb-sense-bulk-resolve.py` | Batch-Auflösung nach Lemma oder `xml_id` auf Sense-Pending-TSV |
| `wzb-sense-apply.py` | Schreibt aufgelöste `@ana`/`@corresp` aus Pending-TSV ins TEI |
| `wzb-sense-baseline.py` | Majoritäts-Sense-Baseline aus MHDBDB-Korpus für Accuracy-Schätzung |
| `wzb-sense-evaluate.py` | Stratifiziertes Gold-Sampling, Accuracy/Calibration-Metriken |
| `wzb-split-tsv.py` | Chunked TSV-Splitter für Claude-Batch-Input |

## Adaption für neuen Text

Die drei **kanonischen** Skripte (`auto-match`, `pos-assign`, `sense-assign`) zeigen das Pipeline-Pattern in idiomatischer Form. Für eine neue Text-Aufnahme:

1. Skripte als Vorlage in `scripts/ingest/<sigle>/` kopieren
2. Sigle-Konstanten und TEI-Pfade anpassen
3. Text-spezifische Heuristiken (Schreibvarianten, Sprachstufe) ergänzen
4. Pipeline iterativ durchlaufen, Coverage-Reports prüfen

Siehe [docs/features/034-wenzelsbibel-annotation.md](../../../docs/features/034-wenzelsbibel-annotation.md) für die vollständige WZB-Pipeline-Doku.

## Endzustand WZB (2026-04-15)

- 149.148 `<w>`-Tokens
- `@lemmaRef` Coverage: 95,3 %
- `@pos` Coverage: 95,3 %
- `@ana` Coverage: 95,2 %
