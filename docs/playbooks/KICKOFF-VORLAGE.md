# Kickoff-Vorlage für autonome Sessions

Eine autonome Session startet nur mit einem Kickoff-Prompt von chsteiner. Kein Playbook autorisiert sich selbst. Diese Vorlage sagt, was in den Prompt gehört, damit die Session nicht auf halbem Weg nachfragen muss; das Nachfragen ist ihr ja gerade untersagt.

**Die wichtigste Regel dieser Vorlage:** der Betriebsvertrag wird **in den Prompt kopiert**, nicht verlinkt. `BETRIEBSVERTRAG.md` ist die eine Quelle, aus der kopiert wird, und ein Verweis darauf wäre ein Ladevorgang, der ausfallen kann, ohne dass jemand es merkt. Redundanz zur Laufzeit ist hier ein Sicherheitsmerkmal; Redundanz im Repo war die Driftquelle, die diese Trennung überhaupt nötig gemacht hat.

---

## Bausteine

### 1. Autorisierung (immer, wörtlich)

Was diese Session darf, und was auch sie nicht darf. Die Freigabe übersteuert die CLAUDE.md-Regel „never commit/push without user approval" für den genannten Umfang und nur für ihn.

- **Issue-Session:** Commits und Pushes auf `claude/*`-Branches, PRs erstellen. `main` bleibt tabu.
- **Merge-Session:** Merges der benannten PRs nach `main`. Keine direkten Pushes auf `main`.
- **Carearbeit-Session:** Branch- und PR-Modus wie im Playbook, Squash-Merge erst nach Prüfung durch chsteiner.

### 2. Der Betriebsvertrag (immer, kopiert)

Der vollständige Inhalt von `BETRIEBSVERTRAG.md`, eingefügt in den Prompt. Wenn er zu lang erscheint: die Abschnitte 1, 2 und 3 sind der harte Kern und dürfen nie fehlen.

### 3. Der Umfang (immer, konkret)

Welche Issues, welche PRs, welche Arbeitspakete. Bei der Issue-Session mit Wellenplan, bei der Merge-Session als Liste in Merge-Reihenfolge, bei der Carearbeit-Session als Auswahl der Arbeitspakete.

Für die Issue-Session gilt zusätzlich: die Auswahl kommt aus den `auto:*`-Labels, aber sie ist damit noch nicht freigegeben. Was in den Prompt gehört, ist die geprüfte Auswahl, nicht die Labelabfrage.

### 4. Die Weichen (session-spezifisch)

Fragen, die die Session sonst stellen müsste, was ihr untersagt ist:

- **`npm test`:** ausdrückliche Freigabe für die volle Suite, oder Beschränkung auf gezielte Läufe. Ohne diesen Satz gilt die stehende Konvention „Tests nie ungefragt", und die Session hat keinen Weg, sie aufzulösen.
- **Lösch-Policy** (Carearbeit): was gelöscht werden darf und was nach `scripts/_archived/` wandert.
- **Live-Smoke-Checks** (Merge): ob sie Teil der Session sind. Empfehlung: ja.
- **Health-Check** (Carearbeit): als eigenes Arbeitspaket ja oder nein.

### 5. Nicht anfassen (immer)

Die Issues und Bereiche, die diese Session nicht berührt, mit Grund. Dazu ausdrücklich **die Fallen**: was nach leichtem Einstieg aussieht, sich aber im eigenen Ticket-Text auf etwas anderes sperrt.

### 6. Vorab getroffene Entscheidungen (wenn es welche gibt)

Richtungsentscheidungen bei mehreren vertretbaren Umsetzungen, je mit einem Satz Begründung, damit die Session sie nicht neu verhandelt.

### 7. Notationsfallen (wenn welche im Spiel sind)

Etwa Befund-Nummern in einem Issue-Body, die wie Issue-Nummern aussehen.

### 8. Der Abschluss (immer, wörtlich)

„Unbeschaffbarer Input führt zum dokumentierten Überspringen, nicht zum Warten und nicht zum Nachfragen."

---

## Was diese Vorlage nicht ist

Kein Generator. Der Prompt wird von Hand aus diesen Bausteinen zusammengesetzt, und das bleibt so, bis die Vorlage zweimal benutzt wurde und sich zeigt, welche Teile wirklich jedes Mal gleich lauten. Ein Skript, das aus vier leeren Playbook-Abschnitten einen Prompt baut, wäre heute mehr Verwaltung als Ersparnis.
