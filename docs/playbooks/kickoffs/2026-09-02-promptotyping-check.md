# Kickoff: Health-Check der Dokumentation, 2026-09-02

Auftraggeber: chsteiner, über die Koordinationssession `mhdbdb operator`.
Anlass: der Wellenlauf vom 01./02.09. hat die Dokumentation an vielen Stellen
angefasst, und das JOURNAL ist seit Wochen ohne Prüfung gewachsen.

## 1. Autorisierung

Du darfst in diesem Repositorium ohne Rückfrage:

- **lesen**, überall, auch in gitignorierten und versteckten Ordnern
- **messen**, mit eigenen Skripten in deinem Scratchpad
- **Issues anlegen und kommentieren**, aber nur oberhalb der Schwelle (siehe §8)
- **committen und pushen** auf einen eigenen Zweig, und den PR eröffnen

Du darfst **nicht**:

- direkt auf `main` pushen
- ein Issue schließen, und **#44 unter keinen Umständen** (kein `Closes #44`,
  kein `Fixes #44`; es ist der Evergreen)
- Kontakt nach außen aufnehmen, zu niemandem
- Instruktionsdateien umbauen (`CLAUDE.md`, `docs/INDEX.md`,
  `docs/playbooks/**`, `.claude/**`). Befunde daran werden **vorgeschlagen**,
  nicht umgesetzt: als Abschnitt in deinem Bericht. Das ist kein Freeze
  (siehe §6), sondern die Rollentrennung eines Prüfers.

**Blockiert der Auto-Mode-Classifier einen Werkzeugaufruf, schick sofort eine
`PushNotification` an Christian**, mit dem, was blockiert wurde und woran es
hängt, nicht nur dass etwas hängt. Umgehe eine Blockade **nicht** über eine
andere Session: Berechtigungen gelten je Session.

## 2. Adressierung

**Antworte immer an das `from` dieser Nachricht**, nie an einen Namen aus
einem Text. Die Koordinationssession heißt `mhdbdb operator`.

## 3. Was du zuerst liest, in dieser Reihenfolge

1. `CLAUDE.md`, vollständig. Besonders „Health check list
   (MHDBDB-specific)": die fünf Prüfungen dort sind dein Arbeitspaket 1.
2. `docs/INDEX.md`, den Katalog der 15 promptotyping-Dokumente.
3. Das Skill: rufe **`promptotyping` mit dem Argument `check`** auf. Es liegt
   unter `~/.claude/skills/promptotyping/` und beschreibt das Verfahren. Was
   dort steht, hat Vorrang vor meiner Zusammenfassung; wo beides sich
   widerspricht, sag es im ersten Meldepunkt.

## 4. Dein Worktree

Du bist mit `claude --bg --name mhdbdb-health-0902 --worktree mhdbdb-health-0902`
gestartet. Vier Dinge sind am 02.09. gemessen worden und kosten dich je einen
Handgriff:

1. **Miss als Allererstes dein Arbeitsverzeichnis mit `pwd`.** Steht dort der
   Hauptbaum statt deines Worktrees, arbeite trotzdem weiter, aber ab dann mit
   `git -C <worktree>` und absoluten Pfaden. Sag es im ersten Meldepunkt. In
   keinem Fall startest du dich neu.
2. **Dein Zweig heißt `worktree-mhdbdb-health-0902`**, nicht `claude/...`. Leg
   dir mit `git checkout -b claude/health-check-0902` einen eigenen an. Der
   `worktree-`Zweig bleibt als Leiche liegen und wird beim Abbau gelöscht.
3. **`node_modules` als Junction auf den Hauptbaum setzen**, sonst läuft
   `run-tests.js` nicht an. Von `.claude/worktrees/<name>/` aus zeigt sie auf
   `../../../node_modules`.
4. **Der Baum wird `locked` gemeldet, ohne dass ihn jemand gesperrt hat.** Der
   Abbau ist nicht deine Sache, sondern meine; ich brauche von dir nur die
   Meldung, ob im Worktree etwas liegt, das gerettet werden muss.

## 5. Was dir gehört

**Dir allein:** dein Zweig, dein Worktree, dein Scratchpad, die Issues, die du
anlegst.

**Geteilt, und deshalb mit Regel:** `docs/JOURNAL.md`. Die Scorecard ist der
**letzte** Commit deines Zweigs, und davor holst du `origin/main`. Rühr keine
andere Zeile dieser Datei an als die, die du hinzufügst; Befunde an
bestehenden Einträgen gehen in den Bericht, nicht in eine stille Korrektur.

**Nicht deins:** alles unter `tei/`, `authority-files/`, `data/`, `api/`. Ein
Health-Check ändert keine Daten. Findest du dort etwas, ist das ein Ticket.

## 6. Was eingefroren ist

**Nichts.** Der Freeze des Wellenlaufs ist am 02.09. von chsteiner vollständig
aufgehoben worden (#385). Es gilt kein Freeze und es gibt keine Inbox.

Das heißt **nicht**, dass du Instruktionsdateien ändern sollst: §1 verbietet
es aus einem anderen Grund, nämlich weil ein Prüfer nicht zugleich der ist,
der umbaut. Der Unterschied ist wichtig, wenn du in deinem Bericht
argumentierst.

## 7. Arbeitspakete, in dieser Reihenfolge

**Paket 1: der Health-Check nach der Liste in `CLAUDE.md`.**

- **Flow check:** jedes seit dem 01.08. geänderte Dokument in `docs/` einmal
  ganz lesen. Fließt es logisch?
- **Algorithm spot check:** drei Algorithmen aussuchen, den Pseudocode in der
  Doku gegen den echten Code halten.
- **XPath spot check:** drei XPaths aus der Doku gegen die Build-Skripte
  prüfen.
- **Rebuild test:** könnte man jede `.js`/`.py` löschen und aus der Doku
  rekonstruieren? Für die kritischen Pfade (Suche, Build-Pipeline, Leseansicht).
- **Meta:** sind die Dateinamen selbsterklärend? Zu viele oder zu wenige
  Dokumente? Strukturvorschläge immer mit Begründung.

**Paket 2: `docs/JOURNAL.md` auf Staleness und Fehler.** Ausdrücklich von
chsteiner beauftragt und der Grund, warum dieser Lauf jetzt stattfindet. Die
Datei ist über 750 Zeilen gewachsen, ohne je geprüft worden zu sein. Vier
Klassen, und für jede brauche ich Fundstellen mit Zeilennummer:

- **Zahlen, die überholt sind.** Der Lauf vom 02.09. hat mehrere widerlegt.
  Ein Beispiel, das du als Eichung benutzen kannst: die Behauptung, die
  Turn-Zahl des CI-Bots skaliere mit der Diffgröße, ist gemessen falsch
  (#389 hat 18 Dateien und 46 Turns, #382 hatte 13 und 56). In `CLAUDE.md`
  ist sie gestrichen. Steht sie im JOURNAL noch?
- **Behauptungen ohne Messvorschrift**, die als Fakt gelesen werden. Die
  Hausregel lautet: was eine Aussage nicht braucht, wird gelöscht statt
  gesourct.
- **Tote Verweise:** Dateien, Skripte, Zweige, Issues, die es nicht mehr gibt
  oder anders heißen.
- **Verhältnis zu `docs/journal-archive.md`:** die verdichteten Einträge sollen
  dort im Volltext liegen. Stimmt das noch, oder ist etwas verdichtet worden,
  ohne im Archiv zu landen?

Du **korrigierst nichts** in bestehenden Einträgen. Das JOURNAL ist ein
Protokoll; eine stille Änderung wäre schlimmer als der Fehler. Belegte Fehler
kommen in deinen Bericht, und was daraus wird, entscheidet chsteiner.

**Paket 3: die Scorecard.** Drei bis vier Zeilen, datiert, in `docs/JOURNAL.md`.
Kein `.md` in `docs/`: der Bericht ist wegwerfbar, sobald die Punkte
extrahiert sind.

## 8. Vorab getroffene Entscheidungen

Du verhandelst sie nicht neu. Hältst du eine für falsch, setzt du sie um und
schreibst den Einwand in den Abschlussbericht.

1. **Issue-Schwelle:** ein Befund wird nur dann ein Ticket, wenn er eine
   **Entscheidung** braucht, die du nicht treffen darfst, einen **Menschen**
   braucht, oder ein **eigenes Arbeitspaket** ist (mehr als ein halber Tag).
   Alles andere wird auf der Stelle behoben oder fällt weg. Der letzte Lauf
   hat gemessen, dass die Hälfte der Review-Last hausgemacht war.
2. **Jede Zahl in deinem Bericht braucht eine Messvorschrift.** Ein Befund
   ist selbst eine Behauptung, auch wenn ein Werkzeug ihn liefert.
3. **Kein `Closes` auf irgendeinem Ticket**, #44 zuerst nicht.
4. **`fable-reviewer` vor dem ersten Push deines Zweigs**, verpflichtend.
   Nicht `fable-advisor`. Gib ihm mit, was er nicht sehen kann: Zweig, Basis,
   Ziel in einem Satz, Rundennummer.
5. **Ein Statuskommentar je Issue**, nicht mehr.

## 9. Melde- und Haltepunkte

Fünf Meldungen, je zwei bis fünf Zeilen, ohne dass ich frage:

1. **Sobald dein Worktree steht**, mit dem Ergebnis von `pwd`.
2. **Nach Paket 1**, mit der Zahl der Befunde je Prüfung.
3. **Nach Paket 2**, mit der Zahl der JOURNAL-Befunde je Klasse.
4. **Vor und nach jeder Reviewrunde**, mit Rundennummer.
5. **Am Ende**, der Abschlussbericht.

**Haltepunkt, einer:** willst du mehr als drei Issues anlegen, halte an und
frag. Drei ist die Zahl, ab der eine Prüfung anfängt, Arbeit zu erzeugen statt
zu sparen.

**Was vor der Reviewrunde gemessen wird, geht in den Meldepunkt und nirgendwo
sonst.** Nicht in einen Ticketkommentar, nicht ins JOURNAL. Publiziert wird
nach der Runde. Diese Regel ist am 02.09. teuer erkauft worden: eine
Vorabmessung wurde binnen einer Stunde zu einem Ticketkommentar und einem
Journalcommit, und die Runde danach kassierte ihre Prämisse.

## 10. Abschluss

- **Der JOURNAL-Eintrag ist dein letzter Commit**, davor `git fetch origin`
  und Rebase.
- **Der Abschlussbericht geht als Kommentar auf #44** und zusätzlich als
  Nachricht an mich.
- **Rote Zeilen zählen:** ein Fehler, dessen Fehlermodus schon eine
  dokumentierte Lehre hat, bekommt eine Zeile im JOURNAL-Eintrag mit Datum,
  was passiert ist, und welche Lehre nicht gegriffen hat. Gezählt wird der
  eigene Fehler, nicht der fremde.
- **Meld mir, ob im Worktree etwas liegt, das den Abbau nicht überleben darf**,
  besonders unter `.claude/agent-memory/`.

---

**Ein Befund aus dem Lauf, den du als Beispiel benutzen kannst und nicht neu
suchen musst:** dieser Kickoff ist gegen die zehn Bausteine aus
`~/.claude/skills/operator/kickoff-bausteine.md` geschrieben und abgehakt
worden. Der Auftrag vom 01.09. hatte neun von zehn, und der fehlende war
ausgerechnet der Freeze-Baustein. Belegt in `claude-code-setup` #19.
