# WVV Rohquellen: Walther von der Vogelweide

Legacy-Rohmaterial zur Lyrik Walthers von der Vogelweide (Korpustext [`tei/WVV.tei.xml`](../../tei/WVV.tei.xml), „Leich, Lieder, Sangsprüche").

## Was hier liegt

| Datei | Inhalt |
|---|---|
| `WVV.txt`, `WaltherHaupttext*.txt` | Haupttext-Exporte in mehreren Varianten (mit/ohne Codes, Teilstücke 1-3) |
| `WaltherLeich.txt` | Leich separat |
| `WaltherAnhangOhneCodes.rtf`, `WaltherHaupttextOhneCodes.rtf` | RTF-Fassungen ohne Legacy-Codes |
| `WVV-Code.doc` | Dokumentation der Legacy-Codes |
| `WVV-alleInfos.zip`, `WaltherHaupttext3.zip` | Sammelarchive (gitignored, nur lokal) |

## Provenienz und Status

Anders als bei ARI (siehe [`ingest/ari/README.md`](../ari/README.md)) gibt es **keinen Pipeline-Ordner** `scripts/ingest/wvv/`: WVV war bereits Teil der ursprünglichen Migration Alt-MHDBDB → TEI und wurde nicht über das heutige Ingest-Verfahren (Stage-0 → Phase 1-3, [`docs/DATA-MODEL.md`](../../docs/DATA-MODEL.md)) eingespielt.

Die Rohquellen hier dienten als Referenzmaterial für das Stanza-Wrapping in Issue #110 (Commit `7ad32a6ac`, 2026-05-15: 478/482 Strophen mit `<lg>` ausgezeichnet) und bleiben als Provenienz-Beleg liegen.
