# Archivierte WZB-Skripte

Skripte aus der Wenzelsbibel-Annotations-Pipeline, die einmalig liefen oder durch generischere Workflows abgelöst wurden. Bleiben für Audit/Nachvollziehbarkeit hier; **nicht für Reproduktion auf neuen Texten gedacht**.

## Inhalt

| Skript | Was es tat | Warum archiviert |
|--------|-----------|------------------|
| `wzb-sense-migrate-schema.py` | Fügte `decision_type` und `model_id` Spalten zu älteren `wzb-sense-pending.tsv`-Dateien hinzu | One-time-Schema-Migration; lief 2026-04, TSV-Format ist seither stabil |
| `wzb-fix-pronoun-in.py` | Spezial-Heuristik für 640 Instanzen von 'in' (Präposition → Pronomen) | Hardcodierte WZB-Liste; 'in'-Disambiguierung läuft jetzt regulär über `wzb-pos-bulk-resolve.py` |
| `wzb-in-auto-classify.py` | Auto-Klassifikation ungelöster 'in'-Token via temporale/räumliche Kontext-Wörter | Same; ersetzt durch reguläre Phase-2-Pipeline |
| `wzb-pos-context-resolve.py` | Context-basierte POS-Disambiguierung für 23 lemma-spezifische Heuristiken | Lemma-Liste ist hardcodiert; das Muster sollte in einen generalisierten Resolver eingehen, falls künftige Texte ähnliche Heuristiken brauchen |

Aktive Pipeline: [`scripts/ingest/wzb/`](../../ingest/wzb/).
