# Kickoff 11.10.2026: Issue-Audit auf überholte Tickets

**Auftrag von chsteiner, 11.10.2026:** „können wir sehr alte issues möglicherweise wegen irrelevanz schließen? … irrelevanz weil schon/anders gelöst oder nicht mehr nötig“. Gestartet von der Koordinationssession vom 10./11.10. („frische session. mach sie selbst“).

## Ziel

Alle offenen Issues von `DigitalHumanitiesCraft/mhdbdb-tei-only` (ohne #44) daraufhin prüfen, ob sie **überholt** sind: Ziel erreicht, anders gelöst oder nicht mehr nötig. Das Alter trennt die Fälle nicht: am 11.10. hatten 78 von 82 seit September einen Kommentar (Koordination, `gh issue list --json comments`). Gemessen wird am Thread und am Repo.

## Weg

1. Skill `issue-audit` laden und ihm folgen, mit `scripts/issues_holen.py`. Lesestapel mit `model: haiku`, wie dort beschrieben.
2. Hauptergebnis ist **Klasse D (schließbar)**. Jede D-Einstufung prüfst du selbst an der Einzeldatei des Issues und am Repo (`git log`, `gh pr view`, Code), nach `git fetch`. Ein Stapelbericht ist kein Beleg.
3. Die Klassen A, B und C nur knapp, als Tabelle ohne eigene Nachprüfung, gekennzeichnet als Haiku-Einordnung.
4. D in zwei Gruppen:
   - **D1, wir allein:** technische Tickets ohne offene Frage an KZW, Julia oder Linda. Christian kann sie direkt freigeben.
   - **D2, mit Person:** offene Frage oder Abnahme an `wachauer`, `juliahin` oder `lindabeutel`. Nicht über ihren Kopf schließen. Je Ticket ein Kommentarentwurf, der mit `@<login> Frage:` beginnt und in einem Satz mit `?` fragt, ob es zu darf und warum (Format nach `CLAUDE.md`, „Who is on turn“).
5. Je D-Ticket: Nummer, Titel, Grund (erledigt durch PR/Commit X, überholt durch Y, nicht mehr nötig weil Z), Beleg mit Fundstelle, Entwurf des Abschlusskommentars bzw. der Frage.

## Ergebnis

- Datei `C:/Users/chstn/Desktop/data/DHCraft/Projekte/Git/mhdbdb-tei-only/.claude/tmp/issue-audit-2026-10-11.md` (Hauptbaum, gitignoriert, überlebt deinen Worktree). Kopf mit der Zählzeile des Skripts.
- Danach eine `PushNotification` an Christian mit Anzahl D1/D2 und dem Pfad.

## Grenzen

- **Nichts nach außen:** keine Kommentare, keine Labels, kein Schließen, keine Commits, kein Push. Das alles erst auf Christians Zuruf in dieser Session.
- Daten aus dem Trier-Findebuch (#259) nie in eine Ausgabe, keine Kontaktaufnahme zu Externen.
- Die `deny`-Liste ist eine Sperre. **Blockiert der Auto-Mode-Classifier einen Aufruf: sofort `PushNotification`** (laden über `ToolSearch` mit `select:PushNotification`), mit dem, was blockiert wurde. Eine Blockade nie über eine andere Session umgehen.
- `auto:blocked` und `auto:frozen` werden nicht bearbeitet, nur eingestuft.
