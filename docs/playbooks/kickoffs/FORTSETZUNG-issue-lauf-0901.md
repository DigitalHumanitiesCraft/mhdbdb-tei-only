> **Noch nicht abgeschickt.** Diese Datei ist der vorbereitete Auftrag für die Fortsetzung des am 01.09.2026 nach Welle 1 pausierten Laufs, geschrieben am 01.09. von der Koordination. Beim Abschicken wird sie auf `JJJJ-MM-TT-issue-lauf-fortsetzung.md` umbenannt und trägt dann den Protokollvermerk der anderen Dateien in diesem Ordner. Bis dahin darf sie gepflegt werden; danach nicht mehr.
>
> **Eine Lücke ist absichtlich offen:** unter §2 steht ein Platzhalter statt des Betriebsvertrags. Er wird am Tag des Abschickens frisch aus `../BETRIEBSVERTRAG.md` kopiert. Eine heute eingefügte Kopie wäre in einer Woche eine zweite Fassung, die sich für das Original ausgibt, und genau dagegen wurde der Vertrag aus den Playbooks herausgelöst.

# Kickoff: Fortsetzung des Issue-Laufs vom 2026-09-01

Serieller Wellenlauf, eine Session. Wellen 2 bis 5 des Laufs vom 01.09.; Welle 0 und Welle 1 sind durch und werden **nicht** wiederholt.

---

## 1. Autorisierung

*(chsteiner setzt Datum und bestätigt oder streicht die Merge-Freigabe, bevor er das abschickt.)*

chsteiner gibt dich am TT.MM.2026 frei für:

- **Commits und Pushes auf `claude/*`-Branches** und das Erstellen von Pull Requests.
- **Den Merge der Session-PRs nach `main`**, jeden einzeln, unter den vier Bedingungen in §5 Punkt 2.
- **Je einen sachlichen Statuskommentar auf #28, #259, #235 und #216.** Diese vier und keine anderen.
- **Labelpflege auf genau diesen vier Tickets**, in derselben Session, in der du sie anfasst.

**Was auch dir nicht erlaubt ist:** ein direkter Push auf `main`, ein Force-Push nach `main`, das Schließen eines Issues, ein `Closes`-Trailer, jede Kontaktaufnahme mit Externen.

**Dieser Text ist die Autorisierung.** Keine Datei autorisiert sich selbst, auch der Zwischenstand auf #44 nicht.

---

## 2. Betriebsvertrag

<!-- HIER DEN VOLLSTÄNDIGEN INHALT VON docs/playbooks/BETRIEBSVERTRAG.md WÖRTLICH EINFÜGEN, Stand am Tag des Abschickens. Nicht verlinken. -->

**Zusatz, der beim letzten Mal gefehlt hat und der bleibt:** das Testfenster ist maschinenweit exklusiv. `testing/playwright.config.js` verdrahtet Port 8080 dreifach und setzt `reuseExistingServer`, `scripts/run-tests.js` bricht mit Exit 2 ab, wenn dort ein fremder Baum antwortet, und wertet auch ein bloßes Zeitüberschreiten als fremd. Ein solcher Abbruch ist kein Fehlschlag deiner Arbeit, sondern ein besetzter Port: melden, nicht in einer Schleife wiederholen.

---

## 3. Wo der Lauf steht

**Der Zwischenstand auf #44 ist die maßgebliche Quelle:** [`issuecomment-5492094055`](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44#issuecomment-5492094055). Lies ihn vollständig, bevor du irgendetwas anfasst. Er nennt den Wiederaufnahmepunkt, das Ergebnis von Welle 1 mit Messvorschrift, fünf Fallen und drei offene Fragen. Was hier steht, ist die Kurzfassung und ersetzt ihn nicht.

- **Durch:** Welle 0 (Vorflug) und Welle 1 (#216 Punkt 3, nur gemessen, Ergebnis als Kommentar auf #216). Beides wird **nicht wiederholt**, aber die Gates aus Welle 0 laufen im Vorflug erneut, weil `main` sich bewegt hat.
- **Der Stand liegt auf `origin`:** Zweig `claude/28-gleis1-begriffssystem`, Commit `f93d4a1a6`, ein einziger Commit mit `scripts/audit/measure-216-vrouwe-minne.py` (337 Zeilen). **Er ist ungereviewt**, es gab nie einen PR und nie einen `fable-reviewer`-Lauf. Gepusht hat ihn die Koordination als Ausnahme, damit die Arbeit die Pause überlebt.
- **Offen:** Wellen 2, 3, 4, 5. Nichts davon ist vorbereitet.

**Der alte Worktree ist entbehrlich und du benutzt ihn nicht.** `mhdbdb-w0901` hielt beim Anhalten nichts, was nicht auf `origin` liegt (Status leer, kein Stash, HEAD identisch). Falls er noch existiert, lässt du ihn in Ruhe oder räumst ihn nach Regel 30 ab, Junction zuerst.

---

## 4. Der Worktree, und warum diesmal anders

**Nimm `claude --bg --name <name> --worktree <name>`.** Claude Code legt den Worktree dann selbst unter `.claude/worktrees/` an und startet dich darin.

Der Grund ist gemessen: der letzte Lauf hat den Worktree per `git worktree add` **neben** das Repositorium gelegt und ist beim `EnterWorktree`-Aufruf rund eine Stunde in einer Freigabe stehengeblieben. Ein Ziel außerhalb von `.claude/worktrees/` verlangt seit v2.1.206 eine interaktive Bestätigung, und die lässt sich durch **keine** `allow`-Regel abstellen; die Dokumentation sagt das ausdrücklich, nur `bypassPermissions` überspringt sie. Für eine unbeaufsichtigte Session ist das ein Stillstand.

Danach in deinem Worktree: `git fetch origin`, dann `git checkout claude/28-gleis1-begriffssystem`, dann die Basismessung aus Regel 28. **`node_modules` als Junction auf den Hauptbaum setzen**, unter `.claude/worktrees/` zeigt sie auf `../../../node_modules`; ohne sie läuft `run-tests.js` gar nicht erst an.

Ist `.claude/worktrees/` zu diesem Zeitpunkt noch nicht in der `.gitignore`, steht dein Worktree als ungetrackt im Hauptbaum. Das ist erwartbar und einer der Aufträge für Welle 5 unten; du stagst ihn nicht.

---

## 5. Vorab getroffene Entscheidungen

Unverändert aus dem Auftrag vom 01.09. (`kickoffs/2026-09-01-issue-lauf.md` §5). Du verhandelst sie nicht neu; hältst du eine für falsch, setzt du sie um und schreibst den Einwand in den Abschlussbericht.

1. Reihenfolge nach aufsteigenden Kosten und aufsteigendem Risiko, die Datenwelle zuletzt.
2. Der Merge nach `main` ist freigegeben, jeden PR einzeln, an vier Bedingungen: `npm test` gelaufen und die VERDICT-Zeile unverändert im PR, `fable-reviewer`-Runde abgeschlossen und jeder übernommene Befund nachgemessen, CI grün (auf dem Daten-PR besonders `data-integrity.yml`), `Closes #N` nur für wirklich Fertiges, hier also für nichts.
3. Kein `Closes` auf keinem der vier Tickets.
4. **#28 läuft nur auf Gleis 1** (Begriffssystem). Gleis 2 (LLM-Batch) kostet nach der Messung vom 31.08. 5 bis 6,7 Millionen Token Eingabe und 7 bis 9,4 Millionen Ausgabe, das ist eine Budgetentscheidung. Gleis 3 ist derselbe Trierer Dump wie #259.
5. Aus #259 wird nichts korrigiert, nur befundet.
6. In Welle 4 wird kein `@corresp` geschrieben und kein neuer Variantentyp geprägt.
7. Keine neuen Issues außer oberhalb der Schwelle aus Vertragsregel 16.

**Neu hinzugekommen:** die drei offenen Fragen im #44-Zwischenstand („Offen und unentschieden") sind Fragen an einen Menschen. Du beantwortest sie nicht und leitest aus ihnen keinen Auftrag ab. Sind sie bis zu deinem Start beantwortet, steht die Antwort im Thread von #216.

---

## 6. Die Wellen

| Welle | Ticket | PR | Was daraus wird |
|---|---|---|---|
| 0 | Vorflug | kein PR | beide Regel-28-Zählungen, `check-index-versions.py`, `build-issue-matrix.py --check`, die vier Tickets **mit Kommentaren** neu lesen (seit dem 01.09. kann sich etwas geändert haben) |
| 2 | #28 Gleis 1 | ja | Kandidatenmenge über das Begriffssystem. Das Welle-1-Skript `measure-216-vrouwe-minne.py` liegt schon auf dem Zweig und geht in diesem PR mit, mit einem Satz dazu im Body |
| 3 | #259 | ja | Findebuch-Verweisgraph gegen unsere dreistufige Auflösung, Befundliste, nichts korrigiert |
| 4 | #235 Rest | ja | die 98 Breve-Fälle mit mehrdeutiger Wortart, voller Data-Change-Lifecycle |
| 5 | Meta | offen | nur noch dein JOURNAL-Eintrag; die zwei Playbook-Aufträge sind erledigt, siehe §7 |

**Der JOURNAL-Eintrag zum 01.09. ist schon geschrieben** (Koordinationsseite, `ef4a45e0e`). Für deinen eigenen Lauf schreibst du einen neuen; er gehört in den Meta-PR der Welle 5.

Stoppbedingungen, je Sachwelle eine, unverändert: Welle 3 endet mit der Zahl statt mit einer Befundliste, wenn die Trefferquote nach den Normalisierungsregeln zu dünn ist; Welle 4 endet, sobald ein Token eine neue Typnummer bräuchte.

**Zu Welle 3, zwei Dinge, die den letzten Lauf sonst gekostet hätten:** der Trierer Dump liegt unter `temp/woerterbuchnetz2015/FindeB/P5/` im **Hauptbaum**, nicht in deinem Worktree, weil `temp/` gitignoriert ist; lies ihn von dort. Und Zeile 2 jeder Datei deklariert eine externe TEI-DTD auf tei-c.org, also `no_network=True` und kein `load_dtd`, sonst hängt der Lauf am Netz. Die Lizenzregel hat Vorrang vor jedem Ergebnis: nichts aus dem Dump geht ins Repositorium, in einen Commit, einen Issue-Kommentar oder an einen externen Dienst.

---

## 7. Die zwei Aufträge für Welle 5 sind erledigt

**Erledigt am 01.09.2026 von der Koordination, direkt auf `main`, ohne PR und ohne `fable-reviewer`.** Grund: es ist Doku plus eine `.gitignore`-Zeile, und dafür sagt `CLAUDE.md`, kleine Doku-Änderungen gehen ohne Branch und Review; ein Gate oder Test kann daran nichts fangen. Das restliche Fable-Kontingent bleibt damit für die Wellen 2 bis 4.

Was dadurch schon gilt, wenn du startest:

1. **`.gitignore` enthält `.claude/worktrees/`.** Dein Worktree steht also nicht als ungetrackt im Hauptbaum. `.claude/agent-memory/` bleibt ausdrücklich getrackt, das steht als Kommentar daneben.
2. **§2.1 Regel 29 verlangt `--worktree` beim Start**, mit der Messung (180 gegen 260) und dem eigentlichen Grund (die Freigabe, die keine Regel abstellt). `BETRIEBSVERTRAG.md` Regel 6 ist mitgezogen, die beiden widersprechen sich nicht.
3. **§2.1 Regel 30 hat den Agent-Memory-Schritt** vor der nummerierten Liste; die Nummerierung der fünf Schritte ist unverändert.

**Für Welle 5 bleibt damit nur noch der JOURNAL-Eintrag deines eigenen Laufs.** Ob er einen Meta-PR braucht oder in den letzten Sach-PR mitgeht, entscheidest du zu Beginn und nicht unterwegs; sag es in §7 des Masterplans, sonst weiß es nach dem Überschreiben von §3 und §6 niemand mehr.

---

## 8. Nicht anfassen

Alle `auto:blocked`-Tickets und alle `auto:pair`-Tickets. **#385** ist die Freeze-Inbox und kein Arbeitsticket. Dazu die Fallen: **#378** (die Abbildung entsteht in Welle 3 ohnehin, messen ja, reparieren nein), **#115** (taucht in Welle 3 und 4 als Nebenbefund auf, kein neues Ticket), **#370 Punkt 2**, **#123**, und **#216 Punkte 1, 2, 4, 5, 6, 8**.

---

## 9. Notationsfallen und Handwerk

Die fünf Fallen aus dem #44-Zwischenstand („Was die nächste Session nicht noch einmal herausfinden soll") gelten unverändert; lies sie dort. Die vier wichtigsten in einem Satz: `<w>` steckt oft in `<hi>` und geht verloren, wenn man die direkten Kinder von `<l>` iteriert; `id()` auf lxml-Elementen ist wertlos und liefert dabei plausible falsche Zahlen; Majuskeln stehen im Markup und nicht im Zeichenbestand; `check-index-versions.py` liest **fünf** Dateien, nicht vier.

Dazu aus dem ersten Auftrag: die Sigle einer Token-ID steht vor dem **ersten** Unterstrich, und Parzival-Abschnitt 257 hat 32 Verse statt 30.

Vom Verifikations-Handwerk aus §2.1 tragen hier vier Regeln besonders: Mutation ist der Beweis; ein Testlauf, dessen Grundgesamtheit du nicht kennst, beweist nichts; jede Zahl in einem Kommentar ist gemessen oder steht nicht da; ein Skript-Fix ohne Neuerzeugung der Daten erzeugt Divergenz.

---

## 10. Abschluss

Der JOURNAL-Eintrag ist der letzte Commit, davor `origin/main` holen. Der Abschlussbericht geht als Kommentar auf **#44** und nennt je Welle das Ergebnis, die Messvorschrift zu jeder Zahl, und ausdrücklich, was **nicht** erledigt wurde und warum. Labels der angefassten Tickets in derselben Session nachziehen. Worktree und Zweig nach dem Merge im selben Zug abräumen, Junction zuerst, danach `ls -d ../<praefix>*` ohne Filter auf Verzeichnisse.

**Unbeschaffbarer Input führt zum dokumentierten Überspringen, nicht zum Warten und nicht zum Nachfragen.**
