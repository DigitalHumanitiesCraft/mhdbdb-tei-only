# Masterplan: Autonome Issue-Abarbeitungs-Session

**Erstellt:** 2026-07-03 (Audit-Session, Fable 5); mehrere Vorgänger-Sessions sind gelaufen und gemergt.
**Zuletzt gelaufen:** 2026-07-29 (Opus 5, #169 + #239). Session-Inhalte geleert; Ergebnis in §7, Git-History = Archiv.
**§2.1 zuletzt gewachsen:** 2026-07-31, Regeln 28 bis 32 (Branch-Basis, Worktree pro Session, Worktree-Abbau, die `git checkout --`-Falle beim Mutationstesten, der Umfang des Em-Dash-Gates); Regeln 22 bis 26 am 2026-07-30 aus einer interaktiven Session (#236-Merge mit vier Review-Runden, #251). Keine Playbook-Sessions, aber dieselben Fehlerklassen.
**Status:** WARTET AUF BEFÜLLUNG. §1, §3, §4, §5 und §6 sind leer und müssen vor dem nächsten Kickoff neu geschrieben werden; jeder von ihnen sagt selbst, was hineingehört.
**Typ:** Playbook (wiederverwendbares Session-Verfahren, dauerhaft). Der session-spezifische Teil (§1, §3, §4, §5, §6) wird pro Session neu befüllt; der Betriebsvertrag (§2), die Verifikations-Handwerksregeln (§2.1) und das Ergebnis der letzten Session (§7) sind der bleibende Teil.

---

## 1. Ausgangslage (leer, vor der nächsten Session befüllen)

Hier gehört hinein: Zahl der offenen Issues, was sich seit der letzten Session geändert hat, welche Entscheidungen von Menschen inzwischen vorliegen, und eine Einteilung aller offenen Issues in „autonom lösbar", „nicht in dieser Session, mit Begründung", „wartet auf Test-OK", „blockiert auf Menschen", „future/extern" und „Ingest". Die Gruppenzahlen maschinell gegen `gh issue list` prüfen, sie müssen die offenen Issues vollständig und disjunkt abdecken.

Ebenfalls hierher: die Befunde, um die es geht, **am Code verifiziert**, mit aktuellen Fundorten. Zeilennummern in Issue-Bodys altern; die in diesem Playbook auch.

---

## 2. Betriebsvertrag der autonomen Session

Die CLAUDE.md-Regel „never commit/push without user approval" wird durch den Kickoff-Prompt explizit für `claude/*`-Branches und PR-Erstellung freigegeben. Unverändert hart:

1. **`main` ist tabu.** Kein Merge, kein Push. Alle Ergebnisse sind PRs, die chsteiner reviewt und mergt.
2. **Issues werden nie von der Session geschlossen**, nur per `Closes #N` im PR-Body beim Merge. #44 bekommt nie einen Close-Trailer.
3. **Pro PR nur benannte Dateien stagen** (nie `git add -A`), Branch frisch von `origin/main`.
4. **Daten vor Schema**; Data-Change-Lifecycle bei jeder XML-Änderung (in dieser Session nicht einschlägig, beide Deliverables sind frontend-only).
5. **Verifikation je PR:** `npm test` aus dem Repo-Root, nie `npx playwright test`. Gezielt pro Welle (`npm test -- <spec-fragment>`), nicht die volle Suite nebenher. Bei UI zusätzlich Chrome-Verifikation mit realen Belegen; bei HTML-Änderungen `python scripts/build-pages.py --check`; bei neuen Utility-Klassen `npm run build:css`.
6. **Fable-Review vor Abschluss jedes PRs.** Stehende Anweisung von chsteiner (28.07.). Der Berater hat kein Bash: Diff in den Scratchpad dumpen, Pfad mitgeben, dazu PR-Body, Ziel, eigene Zweifel und **auf welchem Branch der Arbeitsbaum steht**. Befunde nachmessen, nicht glauben.
7. **Konfliktmanagement ohne Merges:** PRs starten von `main`; bei Datei-Überschneidung wird der spätere Branch auf den früheren gestackt und der PR-Body sagt „nach PR X mergen". Wenn das Playbook „gestackt" sagt, muss der Branch das auch sein.
8. **Kommunikation:** höchstens ein sachlicher Statuskommentar pro Issue; keine Kontaktaufnahme mit Externen (Linda, Alan, Carina, Silvan, Burch, Brom). Entwürfe dafür landen als Text im Issue. Keine Emoji-Icons (Heroicons inline SVG); keine Em-Dashes in Prosa; echte Umlaute, nie ASCII-Ersatz.
9. **Inputs selbst beschaffen.** Alles Nötige liegt im Repo und in den Issue-Threads (`gh issue view N --json comments`). Nur nachweislich Unbeschaffbares wird im Abschlussreport dokumentiert übersprungen; nicht auf chsteiner warten, nicht fragen.

### 2.1 Verifikations-Handwerk (stabiler Kern, aus mehreren Sessions destilliert)

Diese Regeln haben in der Praxis Fehler gefangen, die alle Gates passiert hatten. Sie sind teurer erkauft als sie aussehen.

1. **Ein grünes Gate ist kein wirksames Gate. Mutation ist der Beweis.** Wer eine Prüfung ergänzt, baut den Fehler ein, den sie fangen soll, und lässt sie laufen. In der Session vom 29.07. sind dreimal hintereinander Audit-Einträge entstanden, die grün liefen und nichts fingen; jedes Mal deckte erst die Mutation es auf.
2. **Substring-Suchen lügen.** `grep -c "shrink-0"` findet einen Treffer in `flex-shrink-0`, `grep "256.760"` findet Teilstrings längerer Zahlen. Auf den Selektor bzw. das Wort ankern (`\.shrink-0{`, `\b`).
3. **Grüner Test heißt nichts, solange nicht geprüft ist, ob er auch OHNE die Änderung grün wäre.** Rückbau kostet zwei Minuten und hat mehrfach ein Scheinergebnis entlarvt.
4. **Eine Zusicherung, die strukturell trivial erfüllt ist, schützt nichts.** „NBB bleibt unverändert" war wertlos, weil NBB gar keine `<div>` hat. Vor jeder „Text X bleibt unberührt"-Aussage prüfen, ob die Struktur dort überhaupt vorkommt.
5. **`expect(await locator).toHaveCount(n)` wartet nichts ab und besteht immer.** Richtig ist `await expect(locator)`.
6. **Die Ausgabedatei eines Hintergrund-Laufs behält nur den Schwanz.** Nach `npm test` fehlten die ersten 182 Testzeilen. Wer Abdeckung belegen will, wertet `testing/test-results/report.json` aus oder lässt die betroffenen Specs gezielt noch einmal laufen.
7. **Auf CI-Checks warten heißt auf ihre Existenz warten.** `grep -c pending` ist unmittelbar nach dem Push 0, weil die Checks noch nicht angelegt sind, und die Schleife fällt sofort durch. Auf die erwartete Anzahl abgeschlossener Checks warten und den `head_sha` gegenprüfen.
8. **`git rebase --continue` frisst `#`-Zeilen** aus der Commit-Message: Betreff „#138: …" und alle `##`-Überschriften verschwinden. Nach dem Auflösen `git commit -C <original> --cleanup=verbatim`, dann erst `--continue`.
9. **Git-Bash-`/tmp` ist nicht Windows-`C:\tmp`.** Python und `gh` sehen etwas anderes als die Shell-Umleitung; ein `cmd1 > /tmp/x || cmd2`-Fallback läuft nie an. Immer den Scratchpad-Pfad ausschreiben.
10. **lxml-Proxy-`id()` wechselt zwischen Iterationen.** Elemente selbst festhalten und mit `is` vergleichen, nie ihre `id()`. Steht auch in `docs/DECISIONS.md:858`.
11. **Zahlen in Doku und Code-Kommentaren altern mit den Daten.** Ein Kommentar begründete einen fehlenden Filter mit „4.755 Korpusbelege"; nach einer Datenänderung waren es 4.049. Wer Zahlen zitiert, prüft sie im selben PR nach oder hinterlegt ein Skript.
12. **Chrome-Verifikation nicht über den JS-Bridge-Kontext, wenn es um Sichtbarkeit geht.** Dort feuern weder IntersectionObserver-Callbacks noch `scroll`-Events aus `window.scrollTo`. Die Bridge taugt für Datenabfragen und DOM-Auszählungen, nicht für Interaktionszustände.
13. **`classList.contains()` ist kein Sichtbarkeits-Check.** Nötig ist die berechnete Anzeige (`getComputedStyle`, Playwrights `toBeVisible`/`toBeHidden`).
14. **Unicode-Literale in Testdateien als Escape schreiben.** Werkzeuge normalisieren zerlegte Formen still zu NFC und entwerten den Test lautlos.
15. **Lokales `main` im Vorflug prüfen.** Es kann einen unveröffentlichten Commit voraus sein; ohne Prüfung verwaist er. Der Befehl steht bei Regel 28, zusammen mit der Basis-Messung des Session-Zweigs.
16. **Ein fehlschlagender `npm test` blockiert die Shell bis zum Timeout.** Playwrights HTML-Reporter serviert bei Failures den Report und wartet. `PW_TEST_HTML_REPORT_OPEN=never` setzen. Rückbau-Beweise zusätzlich in getrennte Tool-Aufrufe legen (stash, testen, pop), sonst lässt ein Timeout den Arbeitsbaum im Mutationszustand zurück.
17. **Chrome hält ES-Module über `-c-1` hinweg im Cache.** Eine Verifikation kann den alten Stand zeigen, ohne dass es auffällt. Nach jeder JS-Änderung hart neu laden und eine neu hinzugefügte Funktion als Kanarienvogel abfragen (`typeof x === 'function'`), bevor man Ergebnisse interpretiert.
18. **Gezielte Mutation schlägt Komplettrückbau.** Einzelne Zusicherungen einzeln brechen. Ein Komplettrückbau macht alles rot und beweist deshalb über keine einzelne Zusicherung etwas.
19. **Auch prüfen, was ohnehin erfüllt scheint.** Ein Sortier-Tiebreak sah nach totem Code aus, weil die Einfügereihenfolge ihn schon erfüllte. Die Mutation zeigte das Gegenteil.
20. **Minifizierte Build-Artefakte per Selektorliste diffen.** Bei `tailwind-output.css` ist der Zeilendiff immer die ganze Datei. Selektoren vorher und nachher extrahieren und mit `comm` vergleichen; so wird sichtbar, ob der Rebuild eine Klasse ergänzt oder eine verloren hat.
21. **Beispiele aus Tickets sind Behauptungen, keine Daten.** Sowohl das Leitbeispiel von #239 (`rôtwîn`) als auch ein Tabelleneintrag dieses Playbooks (`bîr`) hielten der Messung nicht stand. Jedes Beispiel, an dem ein Akzeptanzkriterium hängt, vor der Umsetzung gegen die Daten prüfen.
22. **Auch die Zahlen eines Reviewers sind Behauptungen.** Eine Zweitmeinung rechnete für eine gedriftete Doku-Tabelle 60 und 1.360 vor, gemessen waren es 51 und 1.406: sie hatte die Altwerte fortgeschrieben, die gerade das Problem waren. Wer eine Korrektur übernimmt, messt sie wie eine Behauptung. Dasselbe gilt für Grep-Zahlen an XML: `grep -c 'parallel'` liefert 52 statt 51, weil eine Zeichenkette escaped im Text steht; gezählt wird über den Parser.
23. **Eine Fehlermeldung ist eine Behauptung und gehört gemessen wie jede andere.** An einem Tag vier Fälle in denselben Skripten: „nichts entfernt", obwohl zwei Dateien schon geschrieben waren; „die entfernten Tokens trugen teils `@lemmaRef`" bei einer Bedingung, die nur „hat überhaupt etwas entfernt" prüfte (gemessen: 16 von 42); ein Bericht, der `el.text` druckte, während die Prüfung `itertext()` las, und im Ernstfall `None` gezeigt hätte; und eine Diagnose, die eine von zwei möglichen Ursachen als die einzige nannte. Die Meldung ist der Teil, den später jemand glaubt, ohne ihn nachprüfen zu können.
24. **Ein Skript-Fix ohne Neuerzeugung der Daten erzeugt Divergenz.** Wird ein Formatierungs- oder Struktur-Fehler im Ingest-Skript behoben, die betroffene Datei aber nur „nachgebessert" oder gar nicht angefasst, erzeugt ein späterer Lauf aus der Quelle etwas anderes als das Committete. Richtig ist: Datei auf den Ausgangsstand zurücksetzen, Kette komplett neu laufen lassen, Differenz gegen den vorigen Stand ausweisen (Elementzahlen, Tokentext, `xml:id`-Folge, abgeleitete Schicht). Das prüft zugleich Reproduzierbarkeit, die mehr ist als die üblich geprüfte Idempotenz.
25. **Wer die Quelle der Wahrheit umstellt, muss alle Produzenten mitziehen.** Beim Wechsel einer UI-Auswahl von DOM-Abfrage auf ein Modell blieb eine zweite Renderstelle derselben Checkbox-Klasse ohne Handler zurück; die Auswahl dort erreichte das Modell nie. Gefangen hat es ein bestehender Test, nicht die drei neu geschriebenen, und die Chrome-Verifikation hatte an der falschen der beiden Stellen geprüft. Vor dem Umstellen alle Render- und Lesestellen auflisten (Grep über JS **und** HTML, weil das Projekt über `onclick=`-Strings verdrahtet).
26. **Der Rückgabewert eines Testlaufs ist kein Testergebnis.** Ein `npm test` endete mit Exit 0, obwohl `report.json` einen `unexpected` auswies. Zusammen mit Regel 6 und 22: die Zahlen kommen immer aus `report.json`, weder aus der Konsolenzeile noch aus dem Exit-Code.
27. **Kein Branchwechsel, solange ein Testlauf im Hintergrund läuft.** Der Arbeitsbaum ist geteilt: ein `git checkout` zieht Playwright die Spec-Dateien unter den Füßen weg. Der Lauf meldet dann „Cannot find module …spec.js", die Zusammenfassung nennt aber nur eine niedrigere Bestanden-Zahl und keinen Fehler. Genau deshalb `testing/test-results/report.json` auswerten statt der Konsolenzeile: dort standen 57 Tests mit einem `unexpected` und fünfzehn `skipped`, während die Konsole „41 passed" meldete.
28. **Die Branch-Basis wird gemessen, nicht am Branchnamen abgelesen, und zwar in Welle 0.** Am 2026-07-30 wurde #248 auf `feature/236-frauenlob` committet, einem Zweig, der seit PR #253 desselben Vormittags gemergt und oben gelöscht war; die Korrektur kostete einen vollständigen Neuaufbau. Der Fehler ist **still**, `git status` meldet „working tree clean". Gemessen wird die symmetrische Differenz, die vor dem ersten eigenen Commit null sein muss:

    ```bash
    git fetch --quiet origin
    git rev-list --count "origin/main...HEAD"    # muss 0 sein
    git rev-list --count "origin/main..main"     # muss 0 sein, das ist Regel 15
    ```

    Das ist Regel 3 („Branch frisch von `origin/main`") als Messung. Zwei Dinge dabei nicht verwechseln: die erste Zeile misst den aktuellen Checkout, die zweite den lokalen `main`. Im Session-Worktree ist HEAD nicht `main`, ein unveröffentlichter Commit auf dem `main` des Hauptordners bliebe der ersten Zeile also unsichtbar; deshalb stehen beide da. Bei gestackten Zweigen (Betriebsvertrag Regel 7) tritt an die Stelle von `origin/main` der Zweig des früheren PRs, gemessen wird immer gegen die tatsächliche Basis. Nicht geeignet ist der bloße Rückstand (`HEAD..origin/main`) als Dauerprüfung: bei 158 Commits auf `main` seit dem 1. Juli hängt jeder Feature-Zweig binnen Stunden zurück, das ist der Normalzustand und nicht der Fehler. Und der Zeitpunkt zählt: an der Basis kostet die Korrektur nichts, am ersten Commit ist die Arbeit schon auf dem falschen Fundament gemacht.
29. **Jede Session in ihrem eigenen Worktree, und am Ende räumt sie ihn wieder ab.** Der Hauptordner bleibt Referenz auf `main` und wird nicht als Arbeitsplatz benutzt; nur so sehen parallele Sessions einander nicht und keine verschiebt der anderen den Stand. `git worktree add -b <branch> <pfad> origin/main` legt die frische Basis aus Regel 28 im selben Zug an. Nach dem Merge gehören Branch **und** Worktree weg, im selben Zug, nicht in einer Aufräumsitzung Wochen später: am 2026-07-30 lagen vier Worktrees und acht Branches herum, drei davon aus Sessions vom 9. Juli, dazu vier verwaiste Verwaltungsordner in `.git/worktrees`. Vor dem Löschen den Merge belegen (`gh api "repos/<R>/pulls?state=all&head=<Org>:<branch>"`), aktive Worktrees an den Dateizeiten erkennen und in Ruhe lassen.
30. **Das Abräumen eines Worktrees ist kein Einzeiler, und es scheitert genau dann, wenn vorher Tests liefen.** `git worktree remove --force` bricht mit „Permission denied" ab, zweimal: am Verzeichnis und am Eintrag unter `.git/worktrees/<name>`; `git worktree prune` bekommt den Eintrag ebenfalls nicht weg. Die Ursache ist kein kaputtes Verzeichnis, sondern ein Halter. Am 2026-07-30 war es ein übriggebliebener `node.exe` der Playwright-CLI, dessen Arbeitsverzeichnis noch im Worktree lag; gefunden über `Get-CimInstance Win32_Process` mit Filter auf die Kommandozeile. Irreführend dabei: auch `Rename-Item` blockiert, es sieht also nach Defekt aus. Reihenfolge, die trägt:
    1. Dev-Server und Testprozesse beenden (`npm run serve`, `npm test`, Playwright-Treiber).
    2. **Junctions einzeln lösen**, bevor irgendetwas rekursiv löscht. Wer `node_modules` als Junction ins Hauptverzeichnis gelegt hat, um Playwright ohne zweite Installation zu fahren, zerstört mit einem rekursiven Löschen das Original. `rmdir <pfad>` hebt die Junction auf und lässt das Ziel unberührt; danach prüfen, dass die Einträge im Hauptordner noch stehen.
    3. `git worktree remove`, dann `git worktree prune`.
    4. **Nachsehen, ob `.git/worktrees/<name>` wirklich weg ist.** Bleibt der Ordner, von Hand entfernen. Ein Worktree, der aus `git worktree list` verschwindet, ist nicht automatisch abgeräumt: der Verwaltungsordner überlebt das regelmäßig.

    Und die Lehre über den Vorgang hinaus: **aus dem Verschwinden eines Eintrags auf eine Ursache zu schließen, ist geraten, nicht gemessen.** Genau dieser Satz stand als „hat sich selbst aufgeräumt" schon in einem Handoff, obwohl in Wahrheit jemand vier blockierte Löschversuche von Hand aufgelöst hatte.

31. **`git checkout -- <datei>` nimmt keine Mutation zurück, es stellt aus dem Index her.** Für `git restore <datei>` gilt dasselbe, die Default-Semantik ist identisch. Ist nichts gestaged, fällt der Index mit HEAD zusammen, und genau dann verliert man beim Zurücknehmen einer Test-Mutation (Regel 18) still jede ungestagte Arbeit an derselben Datei: sie landet auf dem letzten Commit, nicht auf dem Stand vor der Mutation, und `git status` meldet danach „clean". Am 2026-07-31 hat das eine Session eine fertige Datei gekostet, und die Rückmeldung des Werkzeugs sah dabei wie Erfolg aus. **Die Reihenfolge, die trägt: erst committen, dann mutieren, dann zurücknehmen.** Ein `git add` vor der Mutation würde technisch genügen, weil der Index dann den guten Stand hält, ist aber die schlechtere Empfehlung: die Sicherung ist unsichtbar, überlebt kein zweites Staging und steht in keinem Reflog. Im Worktree-pro-Session-Modell der Regeln 29 und 30 ist ein Commit billig.

32. **Das Em-Dash-Gate deckt Markdown seit #292, aber nur im Diff.** Bis zum 2026-08-02 galt hier das Gegenteil, und der Satz ist es wert, stehen zu bleiben: das Gate prüfte nur HTML, JS und CSS, in PR-Bodys stand trotzdem „Gate grün" als Beleg für Doku-Änderungen, und ein Beleg, der nichts belegt, ist schlechter als keiner. Was jetzt gilt: `check-no-em-dash.py --diff-base <rev>` prüft zusätzlich jede `.md`-Zeile, die ein PR **hinzufügt**, mit Fences und Inline-Code als Ausnahme (die Hausregel stellt Code und Terminal-Ausgaben frei). In CI ist die Base der erste Elternteil des ausgecheckten Merge-Refs, in `no-cdn-check.yml` wie in `data-integrity.yml`. Der Bestand bleibt bewusst unberührt, denn die Schreibregel gilt für neuen und überarbeiteten Text: rund 470 Zeilen in den getrackten `.md` tragen einen Em-Dash, gut die Hälfte davon in `docs/journal-archive.md`. **Handarbeit bleibt nur außerhalb von `.md`**: `tei/`, `authority-files/`, `schema/` und die zwei Linecode-CSVs unter `docs/data/`, wo der Strich ohnehin Datenzeichen ist und keine Typografie.

---

## 3. Wellenplan (leer, vor der nächsten Session befüllen)

Muster: Welle 0 ist der Vorflug (beide Zählungen aus Regel 28 müssen 0 sein, `origin/main...HEAD` und `origin/main..main`; `python scripts/audit/check-index-versions.py`; die im Playbook genannten Fundorte aufsuchen und bestätigen; `testing/tests/` nach einschlägigen bestehenden Specs durchsehen; **kein voller `npm test` als Hintergrund-Baseline**). Danach eine Welle je PR, jede mit eigener Verifikation. Die letzte Welle ist der Meta-PR.

Bei Datei-Überschneidungen zwischen den Wellen den späteren Branch auf den früheren stacken und die Merge-Reihenfolge in den PR-Body schreiben. Der Meta-PR berührt fast immer `JOURNAL.md` und `ROADMAP.md` und kollidiert damit mit jedem PR, der Doku anfasst.

---

## 4. Nicht anfassen (leer, vor der nächsten Session befüllen)

Die Liste wird aus §1 abgeleitet und nennt alle Issues, die diese Session NICHT berührt, gruppiert nach Grund: Review-Gate (Ping ist draußen), menschen-blockiert, future/trigger/extern, Ingest. Dazu gehört jedes Mal:

- **Die Fallen ausdrücklich benennen**, also Issues, die nach leichtem Einstieg aussehen, sich aber im eigenen Ticket-Text auf etwas anderes sperren.
- **Kein Merge nach `main`.**
- Alle Gruppen werden nur in der #44-Matrix korrekt einsortiert, nicht bearbeitet.

---

## 5. Getroffene Entscheidungen (leer, vor der nächsten Session befüllen)

Hier gehören die Vorab-Festlegungen von chsteiner hinein: Reihenfolge der Wellen, Richtungsentscheidungen bei mehreren vertretbaren Umsetzungen, und was ausdrücklich draußen bleibt. Jede mit einem Satz Begründung, damit die Session sie nicht neu verhandelt.

---

## 6. Kickoff-Prompt (leer, vor der nächsten Session befüllen)

Der Prompt wird pro Session aus §1, §3, §4 und §5 geschrieben. Diese Bestandteile haben sich bewährt und gehören immer hinein:

1. **AUTORISIERUNG:** ausdrückliche Freigabe für Commits und Pushes auf `claude/*`-Branches und für das Erstellen von PRs (übersteuert die CLAUDE.md-Regel), plus „`main` bleibt absolut tabu".
2. **Issue-Hygiene:** nie selbst schließen außer per `Closes`-Trailer im PR-Body; #44 NIE mit `Closes`; pro Issue ein frischer Branch von `origin/main`; nie `git add -A`; höchstens ein Statuskommentar pro Issue; keine Kontaktaufnahme mit Externen.
3. **Stil:** keine Emoji-Icons (Heroicons inline SVG), keine Em-Dashes in Prosa, echte Umlaute.
4. **Fable-Review vor Abschluss jedes PRs**, mit dem Hinweis, dass der Berater kein Bash hat: Diff in den Scratchpad dumpen, Pfad mitgeben, sagen, auf welchem Branch der Arbeitsbaum steht. Befunde nachmessen, nicht glauben.
5. **Notationsfallen benennen**, falls welche im Spiel sind (etwa Befund-Nummern in einem Issue-Body, die wie Issue-Nummern aussehen).
6. **Welle 0 als Vorflug** ausschreiben, siehe §3.
7. **Das Verifikations-Handwerk aus §2.1** in Kurzform, mindestens die Mutations-Regel.
8. **NICHT ANFASSEN** mit den Gruppen aus §4, inklusive der Fallen („sieht nach leichtem Einstieg aus, ist aber blockiert").
9. **Abschluss:** „Unbeschaffbarer Input führt zum dokumentierten Überspringen, nicht zum Warten und nicht zum Nachfragen."

---

## 7. Session-Ergebnis (Anhang, Stand 2026-07-29)

Zwei Code-PRs plus Meta-PR, wie geplant. Kein Issue geschlossen, drei Issue-Kommentare.

| PR | Issue | Inhalt |
|----|-------|--------|
| #245 | #169 | Die drei von KZW freigegebenen Befunde: Nähesuche misst die Spanne statt des Ankerabstands, Dedup behält den distanzkürzesten Treffer, Fast-Path-Wörterbuch gestrichen. Dazu CONTRACTS §C.2.2 neu und der datierte JOURNAL-Eintrag zur Zahlen-Zäsur |
| #246 | #239 | Wortbestandteil-Suche als zweiter, benannter Modus im Lemmata-Explorer, nach Position des Bestandteils gruppiert, Auswahl an die Multi-Lemma-Suche übergebbar |
| Meta | #44 | Matrix auf 40 offene Issues, ROADMAP, JOURNAL-Handoff, dieses Playbook |

**Drei Dinge, die die nächste Session wissen sollte:**

1. **Zwei Beispiele aus Ticket und Playbook hielten der Messung nicht stand.** `rôtwîn` (Leitbeispiel von #239 und Chrome-Verifikationsziel in §3) existiert gar nicht im Lexikon; und die §1.1-Tabelle führte `bîr` fälschlich als Abweichungsfall. Beides fiel nur auf, weil vor der Umsetzung gemessen wurde. Daraus ist Handwerksregel 21 geworden.
2. **Die naheliegende Minimallösung für die Nähesuche wäre falsch gewesen.** Die alte Auswahl behalten und zu weite Treffer verwerfen erzeugt falsche Negative, weil `positions.find()` die erste Position in Ankernähe nahm, nicht die brauchbarste. Sichtbar wurde das erst am Rückbau-Test, der mit `distance: 19` rot wird.
3. **Reviews haben vier substanzielle Befunde geliefert**, drei davon wurden umgesetzt: Mindestlänge auch auf die Brückenform, Grundwort selbst ankreuzbar, `maxDistance`-Clamp in der Datenschicht. Der vierte (fehlende Deduplizierung in `resolveLemmaIds`) ist bewusst in die Aufräumrunde verschoben.

**Erledigt am selben Tag:** die vorgeschlagene Playground-Aufräumrunde. Acht Funktionen ohne Aufrufer entfernt (zwei davon verwaisten erst durch die Löschung selbst), `resolveLemmaIds` dedupliziert, beide Kookkurrenz-Modi mit einem Guard gegen die Ein-Lemma-Degeneration versehen, die abweichende Zählweise des Upload-Fallbacks in CONTRACTS §B belegt. Übrig aus dieser Ecke: #251 (Auswahl im Wortbestandteil-Modus wird aus dem DOM abgeleitet statt geführt).
