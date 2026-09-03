---
name: main-branch-protection-ruleset
description: main ist nur per Ruleset gegen Loeschen und Force-Push geschuetzt; `branches/main --jq .protected` = true heisst NICHT, dass ein lokaler Push nach main abgelehnt wird
metadata:
  type: project
---

`gh api repos/DigitalHumanitiesCraft/mhdbdb-tei-only/branches/main --jq .protected` liefert `true`, aber die Quelle ist Ruleset 14915989 „main-protection" mit genau zwei Regeln: `deletion` und `non_fast_forward`. Kein `pull_request`, keine `required_status_checks` (`.protection.enabled` = false, `branches/main/protection` = 404 „Branch not protected"). Ein Fast-Forward-`git push origin main` geht durch; gemessen am 02.09.2026 an 21a80d09b und c0063d3e1, beide ohne PR-Zuordnung (`commits/<sha>/pulls` = 0).

**Why:** Der Health-Check-Diff vom 02.09.2026 hat aus `protected=true` „git push origin main is rejected" gemacht, zwei Zeilen unter der Regel, dass Doku-Aenderungen direkt auf main gehen. Das Feld sagt nur „irgendeine Regel greift".

**How to apply:** Bei jeder Behauptung ueber Branch-Schutz `rules/branches/main` und `rulesets/<id>` lesen, nicht `.protected`. Aendert sich das Ruleset, diese Notiz aktualisieren.
