# WZB Rohquellen und Pipeline-Provenienz: Wenzelsbibel (Pentateuch)

Rohmaterial und Entscheidungs-Artefakte des WZB-Ingests (Korpustext [`tei/WZB.tei.xml`](../../tei/WZB.tei.xml), „Wenzelsbibel (Pentateuch: Gen–Dtn, Cod. 2759–2764)"). Die Pipeline-Skripte samt Verfahrensdoku liegen in [`scripts/ingest/wzb/`](../../scripts/ingest/wzb/).

## Was hier liegt

| Bereich | Inhalt |
|---|---|
| `WB-DEA/` | Die 5 Quell-XML der Digitalen Edition der Wenzelsbibel (Prologus/Genesis bis Deuteronomium), Lizenz **CC BY 4.0** (siehe `teiHeader` der Dateien) |
| `phase1b/` | Lemma-Disambiguierung: Gesamt-TSV (`wzb-disambiguation.tsv`), Pending-Review-Liste, `patches/` (11 angewandte Batch-Patches) und `resolutions/` (46 Batch-Entscheidungen) |
| `phase2/` | POS-Zuweisung: `resolutions/` + Pending-Liste |
| `phase3/` | Sense-Zuweisung: `resolutions/`, Majority-Baseline + Pending-Liste |
| `reports/` | Auto-Match-Report und Liste der unmatchten Formen |

## Provenienz und Ausdünnung (2026-07-14, Issue #219)

Dieser Ordner hieß bis Juli 2026 `Wenzelsbibel/` im Repo-Root (der Ingest lief vor der heutigen Konvention `ingest/<sigle>/`). Beim Umzug wurde er um reproduzierbare Zwischenstände ausgedünnt; **die Entscheidungs-Artefakte (patches, resolutions, reports, pending) sind vollständig erhalten**. Entfernt wurden:

- 1.448 mechanische Chunk-Splitter `wzb-disambiguation-part*.tsv` (1:1-Duplikate der erhaltenen Gesamtdatei, nur für die LLM-Batch-Verarbeitung erzeugt)
- `WZB_phase0.tei.xml` und `WZB.lemma-autofill.tei.xml` (TEI-Zwischenstände zwischen den Pipeline-Phasen, aus Quellen + Patches reproduzierbar)
- `WZB.tei.xml` (veraltete Kopie des Endprodukts; das lebende File ist `tei/WZB.tei.xml`)

Alles Entfernte bleibt in der Git-History unter dem alten Pfad `Wenzelsbibel/` vollständig erhalten (letzter Vollstand: Commit vor diesem Umzug).

## Kontext

- Verfahren: dreiphasige LLM-Pipeline (Lemma → POS → Sense), beschrieben im Blog-Post-Draft `publications/BLOG-POST-WZB-PIPELINE.md` und in `scripts/ingest/wzb/README.md`
- Scope-Präzisierung „Pentateuch" (2026-05-12): siehe `docs/INDEX.md` → Recent Milestones
