# Masterplan: Autonome Issue-Abarbeitungs-Session

**Erstellt:** 2026-07-03 (Audit-Session, Fable 5); mehrere Vorgänger-Sessions sind gelaufen und gemergt.
**Zuletzt gelaufen:** 2026-08-31, zweimal am selben Tag (vormittags #315 + #367 + #235 Punkt 3, nachmittags #369 + #255 + #370, beide Opus 5). Deren Ergebnis steht unverändert in §7 und bleibt dort, bis der Lauf vom 2026-09-01 es ersetzt.
**Aktuell:** 2026-09-01, serieller Wellenlauf über #216 Punkt 3, #28, #259 und #235. **Nach Welle 1 pausiert**, Fortsetzung in der Woche ab dem 07.09.; der Wiederaufnahmepunkt steht in §7 und im Zwischenstand auf #44. §1, §3, §4, §5 und §6 beschreiben diesen Lauf und bleiben bis zu seinem Abschluss stehen. Der Wortlaut des Kickoffs liegt seit diesem Lauf getrackt unter [`kickoffs/`](kickoffs/), siehe §6.
**§2.1 zuletzt gewachsen:** 2026-07-31, Regeln 28 bis 32 (Branch-Basis, Worktree pro Session, Worktree-Abbau, die `git checkout --`-Falle beim Mutationstesten, der Umfang des Em-Dash-Gates); Regeln 22 bis 26 am 2026-07-30 aus einer interaktiven Session (#236-Merge mit vier Review-Runden, #251). Keine Playbook-Sessions, aber dieselben Fehlerklassen.
**§2.1 zuletzt geschrumpft:** 2026-08-05, erstmals, von 32 auf 26 Regeln. Die vier zur Ergebnisquelle eines Testlaufs (6, 16, 26, 27) sind eine geworden, weil `npm test` das Verdikt seither selbst bildet; die drei generischen Git- und Shell-Fallen (8, 9, 31) sind in die persistente Memory umgezogen. Sechs leere Nummern, alle im Kopf von §2.1 begründet. Das Wachstum dieser Liste ist ein Wert, ihr Umfang eine Last, und der Ausweg ist beides zugleich: was ein Skript deterministisch prüfen kann, gehört nicht in eine Merkregel.
**Status:** BEFÜLLT mit dem Plan für den 2026-09-01. §1, §3, §4, §5 und §6 beschreiben diesen Lauf und sind vor dem übernächsten Kickoff zu überschreiben; jeder von ihnen sagt in seinem ersten Absatz selbst, was hineingehört. §7 trägt noch das Ergebnis vom 2026-08-31 und wird am Ende des Laufs ersetzt.
**Typ:** Playbook (wiederverwendbares Session-Verfahren, dauerhaft). Der session-spezifische Teil (§1, §3, §4, §5, §6) wird pro Session neu befüllt; der Betriebsvertrag (§2), die Verifikations-Handwerksregeln (§2.1) und das Ergebnis der letzten Session (§7) sind der bleibende Teil.

---

## 1. Ausgangslage (Stand 2026-09-01, vor der nächsten Session überschreiben)

**Was sich geändert hat, und diesmal kam es von außen.** KZW hat am 31.08.
nachmittags zwei lange Kommentare in #216 hinterlassen: eine Durchsicht der 64
`-n`-Fälle mit einer Achtpunkteliste und eine Richtigstellung der
Parzival-Verszählung. Punkt 7 der Liste ist am 01.09. erledigt (`89b25fcf0`),
Punkt 1 liegt bei ihr, der Rest hängt an Punkt 3. Dazu hat chsteiner am 01.09.
die Datengrundlage für #259 lokal bereitgestellt, die dort seit dem 30.07.
gefehlt hat.

**Die vier Ausgangslagen:**

| Ticket | Lage am Kickoff | Was die Welle daraus macht |
|---|---|---|
| #216 | KZWs Liste vom 31.08.: Punkt 7 erledigt, Punkt 1 bei ihr, Punkte 2/4/5/6/8 hängen an Punkt 3 | Punkt 3 wird **gemessen**, nicht umgesetzt |
| #28 | seit 10.08. gemessen entblockt, aber Phase 1 hat drei Gleise, und zwei davon kosten eine Entscheidung | nur Gleis 1, Kandidatenmenge über das Begriffssystem |
| #259 | Ticket seit 30.07. offen, Dump lag auf KZWs Drive und nicht auf der Maschine | seit 01.09. unter `temp/`, 22 Dateien, 27.106.707 Bytes |
| #235 | 66 von 289 seit PR #379 annotiert, 223 offen in drei Klassen | nur die 98 mit mehrdeutiger Wortart |

**Der Zuschnitt war die eigentliche Vorarbeit dieses Laufs.** Geprüft wurde, ob
sich mehrere autonome Spuren lohnen. Sie tun es nicht: die abgeleitete Schicht
(`variants.xml`, beide Indexe, 2.742 JSON unter `api/`) ist eine Funktion des
**ganzen** Korpus, also kollidieren zwei gleichzeitige Datenläufe zwangsläufig,
und ein Dateischnitt kann das nicht auflösen. Von den fünf `auto:checkin`-Tickets
blieben nach der Messung ohnehin nur vier startbare übrig; #123 ist ein
Nice-to-have mit null Kommentaren.

**Ein Ticket ist Body und Kommentare, und bei zweien von vieren steht der
gesamte aktuelle Stand ausschließlich in den Kommentaren.** Bei #235 ist der
Body an zwei von drei Punkten überholt, bei #216 an allen.

Hier gehört hinein: was sich seit der letzten Session geändert hat, welche Entscheidungen von Menschen inzwischen vorliegen, und welche Issues diese Session anfasst.

**Die Einteilung wird nicht mehr von Hand gemacht.** Bis zum 2026-08-05 verlangte dieser Abschnitt, alle offenen Issues in sechs Gruppen zu sortieren und die Gruppenzahlen gegen `gh issue list` auf Vollständigkeit und Disjunktheit zu prüfen. Beides erledigt jetzt das Label-Schema: jedes Ticket trägt genau ein `auto:*`, ein `area:*` und ein `effort:*`, und `python scripts/audit/build-issue-matrix.py --check` meldet mit Exit 1, wenn ein Label fehlt oder der #44-Body veraltet ist. Genau ein Label pro Achse erzwingt die Disjunktheit, die vorher eine Bitte war.

**Was das Skript nicht ersetzt, und das ist der wichtigere Teil: ein Label erzeugt die Einteilung, nie die Freigabe.** Es ist eine Behauptung wie jede andere (Regel 21), und zwar eine, die zum Zeitpunkt des Vergebens galt. Vor jedem Issue, das die Session tatsächlich anfasst:

- **Die Kommentare seit der Labelvergabe lesen.** Ein `auto:full` von letzter Woche weiß nichts von dem Einwand, den KZW gestern in den Thread geschrieben hat. Das ist der eine Weg, auf dem die Matrix stillschweigend falsch wird, ohne dass ein Gate anschlägt.
- **`auto:blocked` nie „trotzdem" anfangen.** Die `wait:*`-Labels sagen, auf wen gewartet wird; bei mehreren wartet das Ticket auf alle.
- **Die Befunde am Code verifizieren**, mit aktuellen Fundorten. Zeilennummern in Issue-Bodys altern; die in diesem Playbook auch.

---

## 2. Betriebsvertrag der autonomen Session

**Der gemeinsame Teil steht in [`BETRIEBSVERTRAG.md`](BETRIEBSVERTRAG.md)** und wird beim Kickoff in den Prompt kopiert, nicht verlinkt (siehe [`KICKOFF-VORLAGE.md`](KICKOFF-VORLAGE.md)). Bis zum 2026-08-05 stand er hier und in zwei weiteren Playbooks gleichzeitig, und Kopien driften.

Was eine autonome Issue-Session darüber hinaus bindet. Dieser Abschnitt gilt für jede von ihnen und wird nicht pro Session überschrieben (siehe Kopf); eine Abweichung im Einzelfall gehört in den Kickoff, nicht hierher:

1. **`main` ist tabu.** Kein Merge, kein Push. Alle Ergebnisse sind PRs, die chsteiner reviewt und mergt. Die Kickoff-Freigabe gilt nur für `claude/*`-Branches und das Erstellen von PRs.
2. **Konfliktmanagement ohne Merges:** PRs starten von `main`; bei Datei-Überschneidung wird der spätere Branch auf den früheren gestackt und der PR-Body sagt „nach PR X mergen". Wenn das Playbook „gestackt" sagt, muss der Branch das auch sein.
3. **Verifikation gezielt pro Welle** (`npm test -- <spec-fragment>`), nicht die volle Suite nebenher. Ein gefilterter Lauf sagt TEILLAUF und belegt damit keine Vollständigkeit; vor dem Push eines Code-PRs ist der Volllauf trotzdem fällig.
4. **Wellenschnitt: Welle 0 ist der Vorflug, danach eine Welle je Arbeitspaket.** Der Vorflug prüft beide Zählungen aus Regel 28 auf 0 (`origin/main...HEAD` und `origin/main..main`), lässt `python scripts/audit/check-index-versions.py` laufen, sucht die im Playbook genannten Fundorte auf und bestätigt sie, sieht `testing/tests/` nach einschlägigen bestehenden Specs durch, und macht **keinen vollen `npm test` als Hintergrund-Baseline**. Danach eine Welle je **Arbeitspaket**, jede mit eigener Verifikation; wo ein Arbeitspaket Code oder Daten ändert, ist es je ein PR. Bis zum 2026-08-31 stand hier „eine Welle je PR", und der Nachmittagslauf desselben Tages hat gezeigt, warum das zu eng ist: zwei seiner vier Wellen haben nichts committet und trotzdem geliefert, einen Statuskommentar und eine Kostenschätzung. **Gibt es einen Meta-PR, ist er die letzte Welle.** Bis zum 2026-08-31 war er Pflicht; beide bisherigen Läufe mussten sein Fehlen im Dokument begründen, obwohl der JOURNAL-Eintrag in einer Sachwelle gut aufgehoben war. Diese Begründungspflicht entfällt, die Angabe nicht: **wo der JOURNAL-Eintrag gelandet ist, sagt §7**, sonst weiß es nach dem Überschreiben von §3 und §6 niemand mehr.

### 2.1 Verifikations-Handwerk (stabiler Kern, aus mehreren Sessions destilliert)

Diese Regeln haben in der Praxis Fehler gefangen, die alle Gates passiert hatten. Sie sind teurer erkauft als sie aussehen.

**Die Nummern sind Anker.** Andere Stellen zitieren sie, im Wellenplan, im Merge-Playbook, in der ROADMAP und in diesem Dokument selbst. Wird eine Regel ausführbar gemacht und deshalb gekürzt, hinterlässt sie eine Lücke, statt die Liste neu durchzuzählen: eine Umnummerierung würde jeden Verweis brechen und die datierten Wachstumsangaben oben auf andere Regeln zeigen lassen. Der Preis ist, dass die gerenderte Ansicht fortlaufend zählt und deshalb von den Nummern im Quelltext abweicht; maßgeblich ist der Quelltext, den lesen die Sessions. Derzeit fehlen 16, 26 und 27 (aufgegangen in Regel 6) sowie 8, 9 und 31 (umgezogen, siehe unten).

**Der erste Weg, auf dem diese Liste kürzer wird:** eine Regel, die einen deterministischen Ablauf beschreibt, gehört auf Dauer nicht hierher, sondern in ein Skript. Was dann bleibt, ist der Aufruf und der Lehrsatz, der nur Prosa sein kann. Regel 6 ist der erste Fall, an dem das durchgezogen wurde.

**Der zweite Weg ist der Geltungsbereich.** Drei frühere Regeln waren keine Projekterfahrung, sondern Fallen von Git und der Windows-Shell, die in jedem Repo gelten: dass `git rebase --continue` die `#`-Zeilen aus der Commit-Message frisst (8), dass Git-Bash-`/tmp` nicht Windows-`C:\tmp` ist (9), und dass `git checkout --` aus dem Index herstellt und dabei still jede ungestagte Arbeit an derselben Datei vernichtet (31). Sie stehen seit dem 2026-08-05 in der persistenten Memory. Der Grund ist nicht Platz, sondern Reichweite: dieses Playbook wird nur nach einem Kickoff gelesen, die Fallen aber schlagen in jeder Sitzung zu, gerade in den interaktiven. Wissen, das immer gilt, gehört an einen Ort, der immer geladen ist.

1. **Ein grünes Gate ist kein wirksames Gate. Mutation ist der Beweis.** Wer eine Prüfung ergänzt, baut den Fehler ein, den sie fangen soll, und lässt sie laufen. In der Session vom 29.07. sind dreimal hintereinander Audit-Einträge entstanden, die grün liefen und nichts fingen; jedes Mal deckte erst die Mutation es auf.
2. **Substring-Suchen lügen.** `grep -c "shrink-0"` findet einen Treffer in `flex-shrink-0`, `grep "256.760"` findet Teilstrings längerer Zahlen. Auf den Selektor bzw. das Wort ankern (`\.shrink-0{`, `\b`).
3. **Grüner Test heißt nichts, solange nicht geprüft ist, ob er auch OHNE die Änderung grün wäre.** Rückbau kostet zwei Minuten und hat mehrfach ein Scheinergebnis entlarvt.
4. **Eine Zusicherung, die strukturell trivial erfüllt ist, schützt nichts.** „NBB bleibt unverändert" war wertlos, weil NBB gar keine `<div>` hat. Vor jeder „Text X bleibt unberührt"-Aussage prüfen, ob die Struktur dort überhaupt vorkommt.
5. **`expect(await locator).toHaveCount(n)` wartet nichts ab und besteht immer.** Richtig ist `await expect(locator)`.
6. **`npm test` verkündet sein Ergebnis selbst. Die VERDICT-Zeile ist das Ergebnis.** Seit dem 2026-08-05 läuft der Aufruf über `scripts/run-tests.js` (auch `test:changed` und `test:quick`). Der Wrapper löscht den alten Report, bricht ab, wenn Port 8080 von einem fremden Arbeitsbaum bedient wird, setzt `PW_TEST_HTML_REPORT_OPEN=never`, vergleicht bei filterlosem Lauf die Spec-Dateien auf der Platte gegen die im Report, und bildet den Exit-Code aus `testing/test-results/report.json`: 0 grün, 1 rot, 2 der Lauf ist gar nicht zustande gekommen. Die Zeile nennt Testzahl, Dateizahl und den geprüften Pfad, gehört also unverändert in den Verifikations-Block des PRs. Zwei Dinge bleiben Handarbeit, weil kein Skript sie abnehmen kann: **die Zeile nie durch eine Pipe schicken** (`tail` liefert immer 0 und frisst den Exit-Code, `journal-archive.md:680`), und **kein Branchwechsel, solange ein Lauf läuft** (ein `git checkout` zieht Playwright die Spec-Dateien unter den Füßen weg; der Lauf meldet dann „Cannot find module …spec.js", die Konsole nennt aber nur eine niedrigere Bestanden-Zahl). Der Satz dahinter, der alle vier Vorgängerregeln getragen hat: **ein Testlauf, dessen Grundgesamtheit du nicht kennst, beweist nichts.** Deshalb steht sie jetzt in der Zeile.
7. **Auf CI-Checks warten heißt auf ihre Existenz warten.** `grep -c pending` ist unmittelbar nach dem Push 0, weil die Checks noch nicht angelegt sind, und die Schleife fällt sofort durch. Auf die erwartete Anzahl abgeschlossener Checks warten und den `head_sha` gegenprüfen.
10. **lxml-Proxy-`id()` wechselt zwischen Iterationen.** Elemente selbst festhalten und mit `is` vergleichen, nie ihre `id()`. Steht auch in `docs/DECISIONS.md:858`.
11. **Zahlen in Doku und Code-Kommentaren altern mit den Daten.** Ein Kommentar begründete einen fehlenden Filter mit „4.755 Korpusbelege"; nach einer Datenänderung waren es 4.049. Wer Zahlen zitiert, prüft sie im selben PR nach oder hinterlegt ein Skript.
12. **Chrome-Verifikation nicht über den JS-Bridge-Kontext, wenn es um Sichtbarkeit geht.** Dort feuern weder IntersectionObserver-Callbacks noch `scroll`-Events aus `window.scrollTo`. Die Bridge taugt für Datenabfragen und DOM-Auszählungen, nicht für Interaktionszustände.
13. **`classList.contains()` ist kein Sichtbarkeits-Check.** Nötig ist die berechnete Anzeige (`getComputedStyle`, Playwrights `toBeVisible`/`toBeHidden`).
14. **Unicode-Literale in Testdateien als Escape schreiben.** Werkzeuge normalisieren zerlegte Formen still zu NFC und entwerten den Test lautlos.
15. **Lokales `main` im Vorflug prüfen.** Es kann einen unveröffentlichten Commit voraus sein; ohne Prüfung verwaist er. Der Befehl steht bei Regel 28, zusammen mit der Basis-Messung des Session-Zweigs.
17. **Chrome hält ES-Module über `-c-1` hinweg im Cache.** Eine Verifikation kann den alten Stand zeigen, ohne dass es auffällt. Nach jeder JS-Änderung hart neu laden und eine neu hinzugefügte Funktion als Kanarienvogel abfragen (`typeof x === 'function'`), bevor man Ergebnisse interpretiert.
18. **Gezielte Mutation schlägt Komplettrückbau.** Einzelne Zusicherungen einzeln brechen. Ein Komplettrückbau macht alles rot und beweist deshalb über keine einzelne Zusicherung etwas. Den Rückbau in getrennte Tool-Aufrufe legen (stash, testen, pop): bricht der Lauf mit einem Timeout ab, bleibt der Arbeitsbaum sonst im Mutationszustand zurück.
19. **Auch prüfen, was ohnehin erfüllt scheint.** Ein Sortier-Tiebreak sah nach totem Code aus, weil die Einfügereihenfolge ihn schon erfüllte. Die Mutation zeigte das Gegenteil.
20. **Minifizierte Build-Artefakte per Selektorliste diffen.** Bei `tailwind-output.css` ist der Zeilendiff immer die ganze Datei. Selektoren vorher und nachher extrahieren und mit `comm` vergleichen; so wird sichtbar, ob der Rebuild eine Klasse ergänzt oder eine verloren hat.
21. **Beispiele aus Tickets sind Behauptungen, keine Daten.** Sowohl das Leitbeispiel von #239 (`rôtwîn`) als auch ein Tabelleneintrag dieses Playbooks (`bîr`) hielten der Messung nicht stand. Jedes Beispiel, an dem ein Akzeptanzkriterium hängt, vor der Umsetzung gegen die Daten prüfen.
22. **Auch die Zahlen eines Reviewers sind Behauptungen.** Eine Zweitmeinung rechnete für eine gedriftete Doku-Tabelle 60 und 1.360 vor, gemessen waren es 51 und 1.406: sie hatte die Altwerte fortgeschrieben, die gerade das Problem waren. Wer eine Korrektur übernimmt, messt sie wie eine Behauptung. Dasselbe gilt für Grep-Zahlen an XML: `grep -c 'parallel'` liefert 52 statt 51, weil eine Zeichenkette escaped im Text steht; gezählt wird über den Parser.
23. **Eine Fehlermeldung ist eine Behauptung und gehört gemessen wie jede andere.** An einem Tag vier Fälle in denselben Skripten: „nichts entfernt", obwohl zwei Dateien schon geschrieben waren; „die entfernten Tokens trugen teils `@lemmaRef`" bei einer Bedingung, die nur „hat überhaupt etwas entfernt" prüfte (gemessen: 16 von 42); ein Bericht, der `el.text` druckte, während die Prüfung `itertext()` las, und im Ernstfall `None` gezeigt hätte; und eine Diagnose, die eine von zwei möglichen Ursachen als die einzige nannte. Die Meldung ist der Teil, den später jemand glaubt, ohne ihn nachprüfen zu können.
24. **Ein Skript-Fix ohne Neuerzeugung der Daten erzeugt Divergenz.** Wird ein Formatierungs- oder Struktur-Fehler im Ingest-Skript behoben, die betroffene Datei aber nur „nachgebessert" oder gar nicht angefasst, erzeugt ein späterer Lauf aus der Quelle etwas anderes als das Committete. Richtig ist: Datei auf den Ausgangsstand zurücksetzen, Kette komplett neu laufen lassen, Differenz gegen den vorigen Stand ausweisen (Elementzahlen, Tokentext, `xml:id`-Folge, abgeleitete Schicht). Das prüft zugleich Reproduzierbarkeit, die mehr ist als die üblich geprüfte Idempotenz.
25. **Wer die Quelle der Wahrheit umstellt, muss alle Produzenten mitziehen.** Beim Wechsel einer UI-Auswahl von DOM-Abfrage auf ein Modell blieb eine zweite Renderstelle derselben Checkbox-Klasse ohne Handler zurück; die Auswahl dort erreichte das Modell nie. Gefangen hat es ein bestehender Test, nicht die drei neu geschriebenen, und die Chrome-Verifikation hatte an der falschen der beiden Stellen geprüft. Vor dem Umstellen alle Render- und Lesestellen auflisten (Grep über JS **und** HTML, weil das Projekt über `onclick=`-Strings verdrahtet).
28. **Die Branch-Basis wird gemessen, nicht am Branchnamen abgelesen, und zwar in Welle 0.** Am 2026-07-30 wurde #248 auf `feature/236-frauenlob` committet, einem Zweig, der seit PR #253 desselben Vormittags gemergt und oben gelöscht war; die Korrektur kostete einen vollständigen Neuaufbau. Der Fehler ist **still**, `git status` meldet „working tree clean". Gemessen wird die symmetrische Differenz, die vor dem ersten eigenen Commit null sein muss:

    ```bash
    git fetch --quiet origin
    git rev-list --count "origin/main...HEAD"    # muss 0 sein
    git rev-list --count "origin/main..main"     # muss 0 sein, das ist Regel 15
    ```

    Das ist Regel 3 („Branch frisch von `origin/main`") als Messung. Zwei Dinge dabei nicht verwechseln: die erste Zeile misst den aktuellen Checkout, die zweite den lokalen `main`. Im Session-Worktree ist HEAD nicht `main`, ein unveröffentlichter Commit auf dem `main` des Hauptordners bliebe der ersten Zeile also unsichtbar; deshalb stehen beide da. Bei gestackten Zweigen (Betriebsvertrag Regel 7) tritt an die Stelle von `origin/main` der Zweig des früheren PRs, gemessen wird immer gegen die tatsächliche Basis. Nicht geeignet ist der bloße Rückstand (`HEAD..origin/main`) als Dauerprüfung: bei 158 Commits auf `main` seit dem 1. Juli hängt jeder Feature-Zweig binnen Stunden zurück, das ist der Normalzustand und nicht der Fehler. Und der Zeitpunkt zählt: an der Basis kostet die Korrektur nichts, am ersten Commit ist die Arbeit schon auf dem falschen Fundament gemacht.
29. **Jede Session in ihrem eigenen Worktree, und am Ende räumt sie ihn wieder ab.** Der Hauptordner bleibt Referenz auf `main` und wird nicht als Arbeitsplatz benutzt; nur so sehen parallele Sessions einander nicht und keine verschiebt der anderen den Stand.

    **Der Worktree entsteht beim Start, mit `claude --bg --name <name> --worktree <name>`**, und liegt damit unter `.claude/worktrees/<name>/`. Nicht mehr von Hand daneben. Bis zum 2026-09-01 stand hier `git worktree add -b <branch> <pfad> origin/main` mit einem Pfad **neben** dem Repositorium, und der Grund dafür war die 260-Zeichen-Grenze unter Windows. **Der Grund bindet hier nicht**, gemessen am 2026-09-01: Repo-Wurzel 64 Zeichen, Worktree unter `.claude/worktrees/` 88, tiefster Pfad unter `node_modules` relativ zur Wurzel 92, macht 180 gegen 260; der längste getrackte Pfad im Repo ist 74. Messvorschrift: `git ls-files` mit Längenzählung für den getrackten Teil, volle Pfadlänge der tiefsten `node_modules`-Datei minus Länge der Repo-Wurzel für den Rest. Wer das Repositorium verschiebt, misst neu.

    **Der Grund für die Umstellung ist ein anderer, und er ist teuer belegt.** Ein Worktree außerhalb von `.claude/worktrees/` verlangt beim `EnterWorktree`-Aufruf eine interaktive Bestätigung („permission-root relocation"), und die lässt sich durch **keine** `allow`-Regel abstellen: die Dokumentation sagt ausdrücklich, dass weder eine `EnterWorktree`-Regel noch „don't ask again" den Prompt unterdrückt, nur `bypassPermissions`. Am 2026-09-01 hat das eine unbeaufsichtigte Session rund eine Stunde stillstehen lassen, mitten im Aufbau, bevor jemand zufällig hinsah. Ein Allow zu setzen wäre die schlechtere Antwort gewesen als keine Regel, weil er wirkungslos ist und trotzdem nach Lösung aussieht.

    Zwei Dinge nimmt `--worktree` niemandem ab: **Regel 28** (die Basis wird gemessen, nicht am Namen abgelesen) gilt unverändert, und die **`node_modules`-Junction** bleibt nötig, sonst läuft `run-tests.js` gar nicht erst an; unter `.claude/worktrees/` zeigt sie auf `../../../node_modules`. `.claude/worktrees/` steht seit dem 2026-09-01 in der `.gitignore`, sonst stünde jeder Worktree als ungetrackt im Hauptbaum.

    Nach dem Merge gehören Branch **und** Worktree weg, im selben Zug, nicht in einer Aufräumsitzung Wochen später: am 2026-07-30 lagen vier Worktrees und acht Branches herum, drei davon aus Sessions vom 9. Juli, dazu vier verwaiste Verwaltungsordner in `.git/worktrees`. Vor dem Löschen den Merge belegen (`gh api "repos/<R>/pulls?state=all&head=<Org>:<branch>"`), aktive Worktrees an den Dateizeiten erkennen und in Ruhe lassen.
30. **Das Abräumen eines Worktrees ist kein Einzeiler, und es scheitert genau dann, wenn vorher Tests liefen.** `git worktree remove --force` bricht mit „Permission denied" ab, zweimal: am Verzeichnis und am Eintrag unter `.git/worktrees/<name>`; `git worktree prune` bekommt den Eintrag ebenfalls nicht weg. Die Ursache ist kein kaputtes Verzeichnis, sondern ein Halter. Am 2026-07-30 war es ein übriggebliebener `node.exe` der Playwright-CLI, dessen Arbeitsverzeichnis noch im Worktree lag; gefunden über `Get-CimInstance Win32_Process` mit Filter auf die Kommandozeile. Irreführend dabei: auch `Rename-Item` blockiert, es sieht also nach Defekt aus.

    **Vor allen fünf Schritten steht seit dem 2026-09-01 einer, der leicht vergessen wird: das Agent-Memory retten.** Der `fable-reviewer` trägt `memory: project` und schreibt, was er lernt, nach `.claude/agent-memory/` **des Worktrees**, in dem er lief, nicht in den Hauptbaum. Seit dem 2026-09-01 ist dieses Verzeichnis getrackt (Entscheidung chsteiner, Begründung und Anleitung in `.claude/agent-memory/README.md`), und genau deshalb ist der Abbau die Stelle, an der es verlorengeht: wer den Worktree entfernt, ohne vorher hineinzusehen, wirft das Gelernte weg. Also `<worktree>/.claude/agent-memory/` gegen den Hauptbaum halten und Neues von Hand übernehmen, und zwar **nach jeder Review-Runde** statt nur am Ende: wann der Reviewer schreibt, entscheidet er selbst, und wer einmal nachsieht, findet es nach Rundenglück.

    Reihenfolge, die trägt:
    1. Dev-Server und Testprozesse beenden (`npm run serve`, `npm test`, Playwright-Treiber).
    2. **Junctions einzeln lösen**, bevor irgendetwas rekursiv löscht. Wer `node_modules` als Junction ins Hauptverzeichnis gelegt hat, um Playwright ohne zweite Installation zu fahren, zerstört mit einem rekursiven Löschen das Original. `rmdir <pfad>` hebt die Junction auf und lässt das Ziel unberührt; danach prüfen, dass die Einträge im Hauptordner noch stehen.
    3. `git worktree remove`, dann `git worktree prune`.
    4. **Nachsehen, ob `.git/worktrees/<name>` wirklich weg ist.** Bleibt der Ordner, von Hand entfernen. Ein Worktree, der aus `git worktree list` verschwindet, ist nicht automatisch abgeräumt: der Verwaltungsordner überlebt das regelmäßig.
    5. **Und im Elternverzeichnis nachsehen, ob die Hülle noch liegt.** Git räumt weg, was Git kennt; ungetrackte Verzeichnisse können bleiben. Am 2026-08-03 lagen vier davon herum (`mhdbdb-wt-314`, `-323`, `-327`, `-331`), jede mit genau einem leeren `node_modules` darin und sonst nichts, zusammen 56 KB. `git worktree list` zeigte dabei nur den Hauptbaum und `.git/worktrees` existierte gar nicht: das Abräumen hatte also funktioniert, übrig blieb, was nicht von Git stammt. Deshalb `git worktree remove --force` nehmen, das erfasst auch die ungetrackten Dateien (Punkt 3 nennt die Form schon), und danach einmal `ls -d ../<praefix>*` laufen lassen. Ob die vier Hüllen aus einem Remove ohne `--force` stammen, ist nachträglich nicht mehr feststellbar. **Der Blick ins Elternverzeichnis gilt nicht nur Verzeichnissen:** dieselbe Suche förderte am Abend des 2026-08-03 sieben Testlogs zutage (`../mhdbdb-wt-314-testrun*.log`, `-323-*`, 806 KB, vom 1. August). Wer `npm test > ../<name>.log` umleitet, legt die Datei neben das Repo, wo weder `git status` noch `git worktree remove` sie je sieht. Deshalb `ls -d ../<praefix>*` ohne Filter auf Verzeichnisse.

    Und die Lehre über den Vorgang hinaus: **aus dem Verschwinden eines Eintrags auf eine Ursache zu schließen, ist geraten, nicht gemessen.** Genau dieser Satz stand als „hat sich selbst aufgeräumt" schon in einem Handoff, obwohl in Wahrheit jemand vier blockierte Löschversuche von Hand aufgelöst hatte.

32. **Das Em-Dash-Gate deckt Markdown seit #292, aber nur im Diff.** Bis zum 2026-08-02 galt hier das Gegenteil, und der Satz ist es wert, stehen zu bleiben: das Gate prüfte nur HTML, JS und CSS, in PR-Bodys stand trotzdem „Gate grün" als Beleg für Doku-Änderungen, und ein Beleg, der nichts belegt, ist schlechter als keiner. Was jetzt gilt: `check-no-em-dash.py --diff-base <rev>` prüft zusätzlich jede `.md`-Zeile, die ein PR **hinzufügt**, mit Fences und Inline-Code als Ausnahme (die Hausregel stellt Code und Terminal-Ausgaben frei). In CI ist die Base der erste Elternteil des ausgecheckten Merge-Refs, in `no-cdn-check.yml` wie in `data-integrity.yml`. Der Bestand bleibt bewusst unberührt, denn die Schreibregel gilt für neuen und überarbeiteten Text: rund 470 Zeilen in den getrackten `.md` tragen einen Em-Dash, gut die Hälfte davon in `docs/journal-archive.md`. **Handarbeit bleibt nur außerhalb von `.md`**: `tei/`, `authority-files/`, `schema/` und die zwei Linecode-CSVs unter `docs/data/`, wo der Strich ohnehin Datenzeichen ist und keine Typografie.

    **Nachtrag 2026-08-03: die Regel gilt für jede `.md`, ohne Ausnahme nach Ordner.** Am selben Tag wurde beides ausprobiert. Zuerst hieß es, die Hausregel gelte nur für user-sichtbaren Text, ein Treffer in `docs/` sei also Rauschen; dann wurde die Einschränkung gebaut (weiße Liste, Umfangsprüfung an zwei Eintrittspunkten, neun Fixture-Fälle, 267 Zeilen) und noch vor dem Merge verworfen. Die Verengung erzeugte zwei eigene Löcher: `git mv docs/entwurf.md publications/entwurf.md` trug den Em-Dash-Bestand von `docs/` stumm in den Veröffentlichungspfad, weil eine erkannte Umbenennung keine hinzugefügten Zeilen hat, und derselbe Fehler noch einmal für einen Umzug aus `_archived/` heraus. Dazu kam die Frage „ist diese Datei user-sichtbar?", die pro neuer Datei wiederkommt. Gemessene Kosten der stumpfen Regel: 5 von 100 Commits der letzten zwei Wochen, zusammen 6 Zeilen. **Lehre über den Anlass hinaus: eine Ausnahme, die pro Fall entschieden werden muss, ist teurer als die Regel, die sie sparen soll.** Wer den Strich billig loswird, tut es; wo er Gegenstand ist (Zitat, Werktitel), setzt er Backticks.

---

## 3. Wellenplan (Stand 2026-09-01, vor der nächsten Session überschreiben)

Fünf Wellen plus Vorflug, drei Sach-PRs und ein Meta-PR, **in aufsteigender
Kosten- und Risikoordnung**. Die einzige Welle, die Korpus und abgeleitete
Schicht berührt, ist die vorletzte; wer bei Welle 1 stolpert, hat noch nichts
angefasst.

| Welle | Ticket | PR | Was daraus wird |
|---|---|---|---|
| 0 | Vorflug | kein PR | beide Regel-28-Zählungen, `check-index-versions.py`, `build-issue-matrix.py --check`, alle vier Tickets **mit Kommentaren** gelesen |
| 1 | #216 Punkt 3 | kein PR | die Größe der *vrouwe*-Disambiguierung, gemessen statt geschätzt |
| 2 | #28 Gleis 1 | ja | Kandidatenmenge über das Begriffssystem, kein LLM, kein Crawl |
| 3 | #259 | ja | Findebuch-Verweisgraph gegen unsere dreistufige Auflösung, Befundliste, nichts korrigiert |
| 4 | #235 Rest | ja | die 98 Breve-Fälle mit mehrdeutiger Wortart, voller Data-Change-Lifecycle |
| 5 | Meta | ja | JOURNAL-Eintrag, §7 dieses Dokuments |

**Der JOURNAL-Eintrag liegt diesmal in einem Meta-PR**, anders als am 31.08.
Der Grund ist die Zahl der Sach-PRs: drei, die alle `docs/JOURNAL.md` anfassen
wollten, würden sich gegenseitig blockieren. Das ist die Angabe, die §2 Punkt 4
verlangt.

**Jede Sachwelle hat eine Stoppbedingung, keine Checkliste.** Welle 1 endet,
sobald die Umsetzung ein neues Lemma oder einen neuen Variantentyp prägen müsste;
Welle 3, wenn die Trefferquote nach den Normalisierungsregeln zu dünn für eine
Befundliste ist; Welle 4, sobald ein Token eine neue Typnummer bräuchte. Eine
Messung, deren Ergebnis den Ablauf nicht ändern kann, ist Dekoration.

**Die Stoppbedingungen sind zugleich die Haltepunkte, die `auto:checkin`
verlangt.** Alle vier Tickets tragen dieses Label, und #44 sagt in seinen
Arbeitsregeln, `auto:checkin` sei nur mit chsteiner am Rechner anzufangen.
chsteiner hat das am 01.09. einmalig für diesen Lauf aufgehoben, datiert im Body
von #44. Der Preis dieser Aufhebung ist, dass die Haltepunkte im Kickoff
vorweggenommen sein müssen statt unterwegs erfragt zu werden.

Das Muster, nach dem geschnitten wird, steht seit dem 2026-08-31 in **§2 Punkt 4** und bleibt beim Überschreiben dieses Abschnitts stehen. Hier steht nur, wie diese eine Session es ausgefüllt hat.

Bei Datei-Überschneidungen zwischen den Wellen den späteren Branch auf den früheren stacken und die Merge-Reihenfolge in den PR-Body schreiben. Der Meta-PR berührt fast immer `JOURNAL.md` und `ROADMAP.md` und kollidiert damit mit jedem PR, der Doku anfasst.

---

## 4. Nicht anfassen (Stand 2026-09-01, vor der nächsten Session überschreiben)

Alle 48 `auto:blocked`-Tickets und alle fünf `auto:pair`-Tickets (#242, #226,
#195, #191, #139), ohne Ausnahme. Dazu **#385**, die Inbox für Änderungswünsche
an eingefrorenen Instruktionsdateien: kein Arbeitsticket.

Fünf Fallen, die im Weg liegen und nach leichtem Einstieg aussehen:

- **#378** (first-wins-Kollisionen im Variantenverzeichnis): Welle 3 baut die
  Abbildung Schreibform auf Lemma ohnehin und steht damit einen Schritt vor der
  Reparatur. Messen ja, reparieren nein. Dieselbe Versuchung hat schon am 31.08.
  die schärfste Kickoff-Vorgabe gebraucht.
- **#115** (dangling lexicon-IDs): wird in Welle 3 und Welle 4 als Nebenbefund
  auftauchen. Nicht anfassen, kein neues Ticket, die Klasse ist geführt.
- **#370 Punkt 2**: 484 offene Form-Lemma-Paare liegen als CSV im Repo und sehen
  nach Fleißarbeit aus. Neue Variantentypen sind seit #216 genehmigungspflichtig.
- **#123** (König vom Odenwald): trägt `auto:checkin` und bleibt trotzdem
  draußen. Null Kommentare seit der Anlage, „Priorität niedrig" nach eigener
  Ansage des Tickets, und ein voller Ingest mit neuer Sigle, `works.xml` und
  `persons.xml`.
- **#216 Punkte 1, 2, 4, 5, 6 und 8**: Punkt 1 liegt bei KZW, der Rest hängt an
  Punkt 3, der in Welle 1 nur gemessen wird.

Dazu die Grenze in der Gegenrichtung: nichts aus dem Trierer Dump unter `temp/`
verlässt die Maschine. Kein Artikeltext, kein Beispieleintrag im Wortlaut, auch
nicht zur Illustration in einem Issue-Kommentar. Publizierbar sind ausschließlich
aggregierte Befunde über **unsere** Daten.

Die Liste wird aus §1 abgeleitet und nennt alle Issues, die diese Session NICHT berührt, gruppiert nach Grund: Review-Gate (Ping ist draußen), menschen-blockiert, future/trigger/extern, Ingest. Dazu gehört jedes Mal:

- **Die Fallen ausdrücklich benennen**, also Issues, die nach leichtem Einstieg aussehen, sich aber im eigenen Ticket-Text auf etwas anderes sperren.
- **Kein Merge nach `main`.**
- Alle Gruppen werden nur in der #44-Matrix korrekt einsortiert, nicht bearbeitet.

---

## 5. Getroffene Entscheidungen (Stand 2026-09-01, vor der nächsten Session überschreiben)

1. **Reihenfolge nach Kosten und Risiko**, nicht nach Ticketnummer: erst die
   Messung, dann die zwei Skript-Wellen, dann der Datenlauf, dann das Meta.
   Begründung in §3.
2. **Der Merge nach `main` ist wieder freigegeben**, für die Session-PRs, jeden
   einzeln, an denselben vier Bedingungen wie am 31.08.: `npm test` gelaufen und
   die VERDICT-Zeile unverändert im PR, `fable-reviewer`-Runde abgeschlossen und
   jeder übernommene Befund nachgemessen, CI grün (auf dem Daten-PR besonders
   `data-integrity.yml`), und `Closes #N` nur für wirklich Fertiges. **Direkte
   Pushes auf `main` und jeder Force-Push dorthin bleiben tabu.** Dritte Session
   mit dieser Konstruktion.
3. **Kein `Closes` auf keinem der vier Tickets.** Bei allen vieren entscheidet
   als Nächstes ein Mensch.
4. **#28 läuft nur auf Gleis 1.** Gleis 2 (LLM-Batch) kostet nach der Messung vom
   31.08. 5 bis 6,7 Millionen Token Eingabe und 7 bis 9,4 Millionen Ausgabe, das
   ist eine Budgetentscheidung. Gleis 3 ist derselbe Trierer Dump wie #259 und
   würde die zwei Wellen verschränken.
5. **Aus #259 wird nichts korrigiert**, nur befundet. Die philologische Bewertung
   der Befunde gehört KZW, nicht der Session, und das ist im Ticket auch der
   ausdrücklich teure Teil.
6. **In Welle 4 wird kein `@corresp` geschrieben** und kein neuer Variantentyp
   geprägt.
7. **#216 Punkt 3 wird gemessen, nicht umgesetzt.**
8. **Der Lauf ist seriell**, nicht in Spuren. Die Zuschnittsprüfung dazu lief am
   01.09.; der Grund ist die global abgeleitete Schicht, nicht Vorsicht.

Hier gehören die Vorab-Festlegungen von chsteiner hinein: Reihenfolge der Wellen, Richtungsentscheidungen bei mehreren vertretbaren Umsetzungen, und was ausdrücklich draußen bleibt. Jede mit einem Satz Begründung, damit die Session sie nicht neu verhandelt.

---

## 6. Kickoff-Prompt (Stand 2026-09-01, vor der nächsten Session überschreiben)

**Der Wortlaut liegt seit diesem Lauf getrackt im Repositorium:**
[`kickoffs/2026-09-01-issue-lauf.md`](kickoffs/2026-09-01-issue-lauf.md). Dieser
Abschnitt fasst nur zusammen, was in die Platzhalter der
[`KICKOFF-VORLAGE.md`](KICKOFF-VORLAGE.md) gesetzt wurde, und ersetzt den
Wortlaut nicht.

**Warum der Ordner neu ist.** Bis zum 2026-09-01 überlebte vom Auftragstext nur
diese Zusammenfassung, und sie wird bei jedem Lauf überschrieben. Der Auftrag ist
aber der einzige Beleg dafür, was eine Session tun durfte, und die Lehren stecken
im Wortlaut, nicht in der Zusammenfassung. Jede Datei dort trägt als erste Zeile
den Vermerk, dass sie ein Protokoll ist und nicht gepflegt wird: der kopierte
Betriebsvertrag darin altert ab dem Tag des Abschickens, und eine Kopie im
Repositorium, die sich für das Original hält, ist genau die Driftquelle, wegen
der `BETRIEBSVERTRAG.md` überhaupt herausgelöst wurde.

Was der Kickoff vom 01.09. gesetzt hat:

1. **Autorisierung:** `claude/*`-Branches und PR-Erstellung, dazu der Merge der
   Session-PRs unter den vier Bedingungen aus §5, dazu je ein Statuskommentar auf
   **#28, #259, #235 und #216**, je Ticket aufgezählt. Ergebnisse aus Wellen ohne
   Kommentarslot gehen in den #44-Bericht.
2. **Umfang:** fünf Wellen plus Vorflug, eine davon ohne PR, der JOURNAL-Eintrag
   im Meta-PR der Welle 5.
3. **Weiche `npm test`:** volle Suite freigegeben, **ausdrücklich kein Volllauf
   als Hintergrund-Baseline in Welle 0**. Dazu neu der Satz, dass das Testfenster
   maschinenweit exklusiv ist und ein Exit-2-Abbruch gemeldet und nicht
   wiederholt wird.
4. **Stoppbedingungen statt Vorarbeiten**, eine je Sachwelle. Sie ersetzen die
   Haltepunkte, die `auto:checkin` sonst unterwegs verlangt; die Aufhebung der
   entsprechenden #44-Regel steht datiert im Body von #44.
5. **Verifikations-Handwerk aus §2.1** in Kurzform, mit der Mutations-Regel.
6. **Nicht anfassen** mit den fünf Fallen aus §4, #378 an erster Stelle.
7. **Fünf Notationsfallen**, darunter zwei aus dem 31.08.-Nachlauf: die Sigle
   steht vor dem **ersten** Unterstrich, nicht vor den letzten zwei, und
   Parzival-Abschnitt 257 hat 32 Verse statt 30.

Was die alte Fassung dieses Abschnitts an dieser Stelle sagte, gilt unverändert weiter:

1. **Autorisierung:** `claude/*`-Branches und PR-Erstellung, `main` bleibt tabu.
2. **Umfang:** die Wellen aus §3, geschnitten nach §2 Punkt 4. **Welle 0 als Vorflug ausschreiben**, und wenn es keinen Meta-PR gibt, im Kickoff sagen, in welcher Welle der JOURNAL-Eintrag mitläuft.
3. **Weiche `npm test`:** ob die volle Suite freigegeben ist oder nur gezielte Läufe. Ohne diesen Satz hat die Session keinen Weg, die stehende Konvention „Tests nie ungefragt" aufzulösen, und darf zugleich nicht nachfragen. Bis zum 2026-08-05 fehlte er hier, während §2 den Volllauf vor dem Push verlangte.
4. **Notationsfallen**, falls welche im Spiel sind (etwa Befund-Nummern in einem Issue-Body, die wie Issue-Nummern aussehen).
5. **Das Verifikations-Handwerk aus §2.1** in Kurzform, mindestens die Mutations-Regel.
6. **Nicht anfassen** mit den Gruppen aus §4, inklusive der Fallen („sieht nach leichtem Einstieg aus, ist aber blockiert").

---

## 7. Session-Ergebnis (Anhang)

### Der Lauf vom 2026-09-01 ist pausiert, nicht abgeschlossen

Angehalten nach Welle 1, weil das Fable-Kontingent zur Neige ging und `fable-reviewer` vor dem ersten Push jedes PR-Zweigs Pflicht ist: Welle 1 war die einzige Welle ohne PR, ein Schnitt dort verbraucht keine Review-Runde. Die Wellen 2 bis 5 sind nicht angefangen.

**Der Wiederaufnahmepunkt steht im Zwischenstand auf #44** ([`issuecomment-5492094055`](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44#issuecomment-5492094055)), mit Zweig, Commit, Worktree-Pfad, dem Ergebnis von Welle 1 samt Messvorschrift, fünf Fallen für die nächste Session und drei offenen Fragen an einen Menschen. Er ist die maßgebliche Quelle; hier steht nur der Zeiger darauf.

Kurzfassung: Zweig `claude/28-gleis1-begriffssystem` auf `f93d4a1a6`, auf `origin` und **ungereviewt**, Worktree `mhdbdb-w0901` bleibt stehen, nächster Schritt ist Welle 2. Zwei Aufträge für Welle 5 sind unterwegs dazugekommen und im Zwischenstand festgehalten (Agent-Memory-Absatz in Regel 30, Umstellung der Worktree-Platzierung über drei Dateien).

**Der JOURNAL-Eintrag zum 01.09. ist geschrieben** (Koordinationsseite, direkt auf `main`, kein Meta-PR). Das ist die Angabe, die §2 Punkt 4 an dieser Stelle verlangt. Der Meta-PR der Welle 5 fällt damit für den JOURNAL-Teil weg; die zwei Playbook-Aufträge bleiben für ihn übrig.

### Der letzte abgeschlossene Lauf, Stand 2026-08-31

Zwei PRs, drei Tickets, **keines geschlossen**, und das ist kein Rückstand,
sondern die Vorgabe: bei allen dreien entscheidet als Nächstes ein Mensch.

| Ergebnis | Issue | Inhalt |
|----|-------|--------|
| kein PR | #369 | Statuskommentar mit neu gemessenen Zahlen. Die Serie war am 24.08. gemergt, das Ticket trug null Kommentare |
| PR #380, gemergt | #255 | `parallel-witness-bias.py`: jede §H-Zählregel mit und ohne Parallelblöcke, zwei Szenarien, mit Paritätsprüfung gegen den Index und zwei Kontrollzahlen. Kein Datum, kein Index |
| PR #382, gemergt | #370 | Punkt 1 (46.890 `@corresp`) und Punkt 4 (Ratsche je Sigle im Cross-Ref-Audit). Punkt 2 bleibt kuratorisch offen, 484 Paare als CSV im Repo |
| kein PR | #28 | Kostenschätzung auf 200-Lemma-Stichprobe, Ergebnis im #44-Bericht |
| neu angelegt | keines | der einzige Kandidat fiel unter das bestehende #115 |

**Kein Meta-PR.** Der JOURNAL-Eintrag zum 2026-08-31 ist in Welle 3 mitgelaufen und
liegt in PR #382 (`15369d58c`); die ROADMAP war nicht betroffen. Das ist die Angabe,
die §2 Punkt 4 an dieser Stelle verlangt: ohne sie steht nach dem Überschreiben von
§3 und §6 nirgends mehr, wo der Eintrag hin ist.

**Sechs Dinge, die die nächste Session wissen sollte:**

1. **Ein roter CI-Review-Haken ist kein Befund, aber auch kein Beweis, dass keiner
   drinsteht.** Vier Läufe, alle im Job-Log gemessen: #368 kein Diff und nichts
   geliefert, #379 Diff berechnet und trotzdem echter `error_max_turns` ohne
   Befund, **#377 und #382 fertige Reviews** (`subtype: success`,
   `is_error: false`), deren Haken die Action nur rot gemacht hat, weil sie 59 und
   56 Züge gegen ein `--max-turns` von 50 gebraucht hatten. Zwei von vier waren gar
   nicht gescheitert. **Und es geht dabei nichts verloren:** der Kommentar wird rund
   anderthalb Minuten nach dem Start gepostet und überlebt den Fehlschlag um zehn
   Minuten. Verworfen wird die grüne Bewertung, nie das Review. Das Limit steht seit
   `6fbf7e002` auf 100, und einen Schalter, der das `throw` abstellt, gibt es nicht
   (geprüft am gepinnten `v1`); die Suche danach kann sich die nächste Session sparen.
2. **Und der teure Fall zeigt, was das kostet.** Der Bot-Kommentar auf #377 trug
   zwei sauber gemessene Befunde; neun Minuten später wurde der rote Haken als
   Plattformgrenze abgetan und der PR ungelesen gemergt. Aufgefallen ist das erst
   einen halben Tag später, als jemand die Regel selbst nachmaß; behoben sind beide
   seit PR #384 (`efb6fc0eb`). **Den Kommentar öffnen, immer**, auch wenn der Check
   rot ist und die Hausregel sagt, das sei erwartbar.
3. **Zwei Sessions haben unabhängig demselben API-Feld geglaubt.**
   `gh api .../pulls/377 -q .changed_files` gibt 0, `gh pr view 377 --json files`
   gibt 34. Für die anderen drei PRs stimmen beide überein. Wer behaupten will,
   GitHub habe den Diff nicht berechnet, liest den `<changed_files>`-Block im
   Job-Log oder nimmt `--json files`.
4. **Was ein Filter nicht zeigt, ist nicht abwesend.** Ich hatte behauptet, der
   `changed_files`-Block auf #382 sei leer, weil mein `grep` die Dateizeilen
   zwischen den Tags nicht treffen konnte und Öffnungs- plus Schlusszeile
   untereinander stehenblieben. Eine Abwesenheitsbehauptung braucht eine Abfrage,
   die Anwesenheit **zeigen könnte**.
5. **Ein Bump gehört zum Artefakt, nicht zur Quelle.** Die erste Fassung von PR
   #382 bumpte den Authority-Index, weil `variants.xml` sich geändert hatte. Der
   Index selbst war identisch, weil er nur normalisierte Formen trägt. **Kein Gate
   hätte das gefangen:** `check-index-version-bump.py` prüft nur die
   Gegenrichtung, `data-integrity.yml` hätte den gebumpten Index anstandslos
   nachgebaut. Gefunden hat es die lokale Review.
6. **Ein Provenienz-Log ohne seinen Erzeuger ist nur so weit reproduzierbar wie
   das Vertrauen in seine Zahlen.** Das Laufskript lag im Scratchpad, während die
   vier WZB-Vorgängerläufe ihres unter `scripts/ingest/wzb/` committet haben.
   Nachgeholt, und beim Neuerzeugen aus der committeten Fassung fiel auf, dass
   eine Spalte still bei 8 Werten gekappt war: `hebt`/`type_9058` las sich als 8
   Belegsigel, es sind 82, das Maximum liegt bei 644. **Eine gekappte Liste ohne
   Kappungsmarke ist eine falsche Zahl, nicht nur eine unvollständige.**

**Was aus früheren Sessions weiter gilt:** ein Worktree hat kein `node_modules`,
ohne Junction auf den Hauptbaum läuft `npm test` gar nicht erst an, und beim
Abräumen kommt zuerst `rmdir` auf die Junction (Regel 30, Punkt 2), sonst nimmt
das rekursive Entfernen das Original mit.
