# Playbooks: Verfahren für autonome Sessions

Wiederverwendbare Session-Verfahren, dauerhaft und nicht ticket-gebunden. Sie gehören **nicht** zu den 15 promptotyping-Dokumenten (siehe `docs/INDEX.md`) und sind deshalb auch von deren Sprachregel ausgenommen: hier steht Deutsch, weil es Arbeitsnotizen sind.

**Der Satz, der über allem steht: keine dieser Dateien autorisiert irgendetwas.** Eine Session läuft erst nach einem Kickoff-Prompt von chsteiner. Wer ein Playbook liest und daraufhin anfängt zu arbeiten, hat es falsch gelesen.

## Was hier liegt, in Lesereihenfolge

| Datei | Inhalt |
|---|---|
| [`BETRIEBSVERTRAG.md`](BETRIEBSVERTRAG.md) | Die 17 Regeln, die für **alle** autonomen Sessions gleich gelten: was ohne Freigabe tabu bleibt, wie gestaged und kommuniziert wird, was vor jedem Push passiert, was in ein Ticket wandert. Wird beim Kickoff wörtlich in den Prompt kopiert. |
| [`KICKOFF-VORLAGE.md`](KICKOFF-VORLAGE.md) | Die 8 Bausteine eines Kickoff-Prompts. Kein Generator: der Prompt wird von Hand zusammengesetzt. |
| [`MASTERPLAN-AUTONOME-ISSUE-SESSION.md`](MASTERPLAN-AUTONOME-ISSUE-SESSION.md) | Issues abarbeiten, in Wellen, je ein PR. Enthält in §2.1 das Verifikations-Handwerk: die 26 Regeln, die in der Praxis Fehler gefangen haben, welche alle Gates passiert hatten. Die werden auch von den beiden anderen Playbooks zitiert. |
| [`MASTERPLAN-AUTONOME-MERGE-SESSION.md`](MASTERPLAN-AUTONOME-MERGE-SESSION.md) | Offene PRs prüfen und mergen, mit Merge-Gates und Pilot-PR. |
| [`MASTERPLAN-AUTONOME-CAREARBEIT-SESSION.md`](MASTERPLAN-AUTONOME-CAREARBEIT-SESSION.md) | Repo-Pflege statt Feature-Arbeit: toter Code, Zähler-Drift, Health-Check. |

Die drei Masterpläne haben einen bleibenden und einen session-spezifischen Teil. Der session-spezifische wird pro Lauf neu befüllt und danach geleert; die Git-History ist das Archiv. Nach jeder Session: Lehren einarbeiten, Kernwissen ins `JOURNAL.md`.

## Warum der Vertrag eine eigene Datei ist

Bis zum 2026-08-05 stand er in allen drei Masterplänen gleichzeitig. Das Verbot von `git add -A` an vier Stellen, und das Merge-Playbook schrieb ihn ab mit dem Vermerk, er sei „unverändert aus dem Issue-Session-Vertrag", was er nach einer Weile nicht mehr war. Kopien driften: derselbe Mechanismus hatte dazu geführt, dass ein Playbook zur Ergebnisquelle eines Testlaufs das Gegenteil dessen anwies, was ein anderes als gemessenen Fehlschlag dokumentierte.
