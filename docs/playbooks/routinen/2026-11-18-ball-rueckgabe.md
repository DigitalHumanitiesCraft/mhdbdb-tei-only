Ergebnis des Laufs vom 2026-11-18 nach `docs/playbooks/BALL-RUECKGABE.md`, auf dem Stand von #44 aus dem Lauf `issue-matrix.yml` vom 2026-11-17T15:17:51Z: 1 von 2 Einträgen, 1 schon vorgelegt.

Herkunft der Zahlen in dieser Zeile: `gh api repos/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44 --jq .body` (Zeile `| **Ball bei uns (2)** |` zwischen den MATRIX-Markern: #262 und #195, beide für Katharina), `gh api "repos/DigitalHumanitiesCraft/mhdbdb-tei-only/actions/workflows/issue-matrix.yml/runs?per_page=1" --jq '.workflow_runs[0].created_at'` für das Datum. Offene PRs mit Kopf `claude/ball-rueckgabe-*`: keine. Stand `origin/main` beim Lauf: `2ed7016c9`.

Gelaufen als wöchentliche Cloud-Routine. Geschrieben wurde nichts außer dieser Datei: kein Kommentar, kein Label, kein Ping.

## Übersicht

| Ticket | Person | Klasse | ein Satz |
|---|---|---|---|
| #195 | Katharina | B | Katharina hat alle drei Fragen beantwortet und die Veröffentlichung aufgeschoben; für Prüfsummen und README fehlt uns der Zugriff auf den Dump. |

Zusammen: A 0, B 1, C 0, D 0, Summe 1.

### Schon vorgelegt: #262 (Katharina)

Der Antwort-Link `issuecomment-6914924044` steht in `2026-11-17-ball-rueckgabe.md` (#712). Nach dieser Datei kam genau ein Kommentar dazu, und zwar von uns: Christian, 2026-11-17T15:21:45Z, [`@wachauer Frage: Gibst du hier Bescheid, sobald die Mail an Ute Recker-Hamm (Trier) raus ist …?`](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/262#issuecomment-6952332692). Das ist die Frage aus der Vorlage vom 17.11. in geänderter Form, samt dem Absatz zum Dateiweg. Der Ball liegt damit wieder bei Katharina. Auf der Liste steht #262 nur noch, weil der #44-Stand vier Minuten älter ist als dieser Kommentar (Matrixlauf 15:17:51Z, Kommentar 15:21:45Z); der nächste Tageslauf nimmt es heraus. Die Regel in §1 Punkt 4 überspringt wörtlich nur Tickets **ohne** neuen Kommentar; hier ist der neue Kommentar unsere eigene Frage, also gibt es nichts neu vorzulegen. Labels (`auto:blocked`, `wait:kzw`) stimmen dazu.

## Zum Posten (B)

Hinweis aus `CLAUDE.md` ("Who is on turn"): Eine Frage wird nur dann oben auf unseren letzten Kommentar editiert, wenn der neuer ist als ihre Antwort. Unser letzter Kommentar ist vom 09.10., ihre Antwort vom 16.11., also als **neuer Kommentar** posten.

### #195 (Katharina)

```
@wachauer Frage: Gibst du Christian eine Kopie von `SQL Dump März 2025/` aus `MHDBDB/Relaunch/Daten/`, damit wir Prüfsummen und README vorbereiten können?
```

Die Fragezeile hat ohne Anfangswort und Backticks 133 Zeichen und bleibt damit unter den 140, die `frage_text()` in `scripts/audit/build-issue-matrix.py` in ihre Liste übernimmt.

Kontext darunter, postfertig:

```
Danke für die drei Antworten. Wir halten fest: nur Daten, CC BY-NC-SA 4.0, und vorerst kein Zenodo-Deposit. Prüfsummen und README können wir erst vorbereiten, wenn die Dateien außerhalb deines OneDrive liegen. Wie beim Trierer Findebuch (#259) käme die Kopie in den DHCraft-Drive unter `Projekte/mhdbdb/extern/`, nicht ins Repo und nicht nach Zenodo.

Sollen die beiden graphDB-Exporte (je rund 7 GB) mitkommen? Sie sind der Export des RDF-Systems, aus dem dieses Repo migriert wurde; wir nehmen sie gern dazu, wenn du sie freigibst. Und falls es schon einen Zeitpunkt oder Anlass gibt, ab dem veröffentlicht werden soll, schreib ihn dazu; dann parken wir das Ticket bis dahin.
```

Was die Antwort entscheidet und deshalb nicht mehr gefragt wird ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/195#issuecomment-6917202439)):

- **Ort:** Katharinas OneDrive, `MHDBDB/Relaunch/Daten/`: `SQL Dump März 2025/` (2,6 GB, darin `Oracle_XML_Export`, `MHDBDB_XML_Export` und `mhdbdb_04.03.2025.tar.gz` mit 119.132.651 Bytes) und `graphDB Dump Februar 2025/` (zwei RDF-Exporte, je rund 7 GB).
- **Inhalt des ersten Deposits:** nur Daten, der Code des alten Frontends kommt später als eigener Schritt.
- **Lizenz:** CC BY-NC-SA 4.0.
- **Neu und entscheidend:** "Der Dump soll derzeit privat bleiben, die Veröffentlichung wird aufgeschoben. Nichts geht vorerst nach Zenodo. Prüfsummen und README können vorbereitet werden, der Deposit wird nicht veröffentlicht."

Warum B und nicht A: Die Vorbereitung, die Katharina freigibt, braucht die Dateien, und die liegen nach ihrer Angabe auf ihrem OneDrive (der Body von #195 sprach im Juli von "nur lokal bzw. serverseitig"; ob es auf dem alten Server noch eine Kopie gibt, sagt der Thread nicht). Dass sie sie herausgibt, steht nirgends im Thread. Eine Session, die Prüfsummen erzeugen soll, hätte nichts, worüber sie rechnen kann. Ein README-Entwurf ohne die Dateien müsste Formatbeschreibung und Dateiliste raten.

Warum die graphDB-Exporte nicht in die Fragezeile: Titel und Body von #195 nennen "Oracle + XML", im Ticket kommen die RDF-Exporte erst in Katharinas Antwort vor, und sie machen rund 14 der rund 16,6 GB aus. Im Repo sind sie aber keine Randsache: Die alte MHDBDB war ein RDF-Triple-Store, aus dem dieses Repo über CSV-Snapshots per SPARQL migriert wurde (`docs/INDEX.md`, Project Status, "Origin"; `docs/DECISIONS.md`, "old MHDBDB RDF → CSV → TEI"). Deshalb fragt der Kontext sie ausdrücklich mit ab (Opt-in), statt sie stillschweigend wegzulassen. Ob sie in den Deposit gehören, entscheidet Katharina.

Was die Quellen schon beantworten:

- **Kein Commit seit der Antwort:** `git log origin/main --since=2026-11-16 -E --grep="#195([^0-9]|$)"` gibt nichts aus.
- **Der Dump steht noch nirgends im Repo verzeichnet:** `grep -n "SQL Dump\|graphDB\|mhdbdb_04\|Oracle" sources/INVENTAR-ARCHIV.md` gibt nichts aus. Das Inventar listet bisher das Textarchiv unter `MHDBDB_Inhaltliches/Texte/` und zwei Bestände im DHCraft-Drive, nicht `MHDBDB/Relaunch/Daten/`.

**Unabhängig von der Frage, ohne Session:** Nach `CLAUDE.md` gehört Datenbestand, der zum Projekt gehört und nicht im Repo liegen darf, mit Lizenzbedingung und Bytezahl in `sources/INVENTAR-ARCHIV.md`. Die Antwort liefert dafür Ort, Umfang, Lizenz und die Auflage "privat" schon jetzt, nur nicht für jede Datei eine Bytezahl (exakt nur für `mhdbdb_04.03.2025.tar.gz`). Ein Abschnitt dort ist eine einzelne Stelle, weder Code noch Daten; ob er jetzt oder erst mit der Kopie und den gemessenen Bytezahlen kommt, entscheidet Christian.

**Labels:** stimmen für die Frage (`auto:blocked`, `wait:kzw`, `area:orga`, `effort:medium`). Liegt die Kopie bei uns, wird aus `auto:blocked` und `wait:kzw` ein `auto:full` für Prüfsummen und README. Nennt Katharina einen Zeitpunkt für die Veröffentlichung, ist danach `auto:frozen` bis zu diesem Datum der richtige Zustand (ohne `wait:*`). Der Titel "öffentlich auf Zenodo sichern" beschreibt seit dem 16.11. das spätere Ziel, nicht den nächsten Schritt; umbenennen ist nicht nötig.

Belege: [Antwort vom 16.11.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/195#issuecomment-6917202439); unsere [Fragen vom 09.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/195#issuecomment-6079925133). Label-Historie: `gh api --paginate .../issues/195/events` (`auto:blocked` und `wait:kzw` am 09.10. gesetzt). Thread vollständig gelesen: Body plus 2 Kommentare (`gh api --paginate .../issues/195/comments`).

## Zum Schließen oder Umlabeln (D)

Keine.

## Auftrag für eine autonome Session (A)

Keiner. Prüfsummen und README für #195 werden ein Arbeitspaket, sobald die Kopie im DHCraft-Drive liegt.
