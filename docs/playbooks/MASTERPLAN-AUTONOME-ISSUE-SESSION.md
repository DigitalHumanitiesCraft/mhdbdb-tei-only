# Masterplan: Autonome Issue-Abarbeitungs-Session

**Erstellt:** 2026-07-03 (Audit-Session, Fable 5); mehrere Vorgänger-Sessions sind gelaufen und gemergt.
**Zuletzt gelaufen:** 2026-08-31 (Opus 5, #315 + #367 + #235 Punkt 3). Session-Inhalte in §1, §3, §4, §5, §6 stehen gelassen, weil sie zum ersten Mal einen Sonderfall dokumentieren, den die nächste Session brauchen wird: eine Kickoff-Freigabe, die den Merge nach `main` ausnahmsweise einschließt. Ergebnis in §7, Git-History = Archiv.
**§2.1 zuletzt gewachsen:** 2026-07-31, Regeln 28 bis 32 (Branch-Basis, Worktree pro Session, Worktree-Abbau, die `git checkout --`-Falle beim Mutationstesten, der Umfang des Em-Dash-Gates); Regeln 22 bis 26 am 2026-07-30 aus einer interaktiven Session (#236-Merge mit vier Review-Runden, #251). Keine Playbook-Sessions, aber dieselben Fehlerklassen.
**§2.1 zuletzt geschrumpft:** 2026-08-05, erstmals, von 32 auf 26 Regeln. Die vier zur Ergebnisquelle eines Testlaufs (6, 16, 26, 27) sind eine geworden, weil `npm test` das Verdikt seither selbst bildet; die drei generischen Git- und Shell-Fallen (8, 9, 31) sind in die persistente Memory umgezogen. Sechs leere Nummern, alle im Kopf von §2.1 begründet. Das Wachstum dieser Liste ist ein Wert, ihr Umfang eine Last, und der Ausweg ist beides zugleich: was ein Skript deterministisch prüfen kann, gehört nicht in eine Merkregel.
**Status:** BEFÜLLT mit dem Stand vom 2026-08-31. §1, §3, §4, §5 und §6 beschreiben die gelaufene Session und sind vor dem nächsten Kickoff zu überschreiben; jeder von ihnen sagt in seinem ersten Absatz selbst, was hineingehört.
**Typ:** Playbook (wiederverwendbares Session-Verfahren, dauerhaft). Der session-spezifische Teil (§1, §3, §4, §5, §6) wird pro Session neu befüllt; der Betriebsvertrag (§2), die Verifikations-Handwerksregeln (§2.1) und das Ergebnis der letzten Session (§7) sind der bleibende Teil.

---

## 1. Ausgangslage (Stand 2026-08-31, vor der nächsten Session überschreiben)

**Was sich geändert hat:** Julia Hintersteiner und KZW haben am 25. und 26.08. drei Fragen beantwortet, die je ein Ticket blockierten. Alle drei Tickets waren damit von `auto:blocked` frei, ohne dass sich am Code etwas geändert hätte. Das ist der Normalfall dieser Sessions: die Arbeit war nie technisch blockiert.

**Die drei Antworten und was sie freigaben:**

| Ticket | Antwort | Von wem, wann |
|---|---|---|
| #315 Punkt 2 | Die Auszeichnung `role="lead-editor"` bezeichnet die Rolle im Editionsprozess, nicht den Status des Textes; der Beitrag bleibt im `respStmt` verzeichnet, nur die Rollenbezeichnung fällt | Julia Hintersteiner, 26.08. |
| #367 | Die 40 Belege der Fügung *der/die wâren minne* sind das Adjektiv, nicht das Verb; zwei neue Variantentypen sind genehmigt | KZW, 25.08. |
| #235 Punkt 3 | Das Breve auf `w` und `n` ist böhmische Schreibkonvention, kein Umlautzeichen (ADR-017); die `o`/`u`-Kandidaten dürfen als eine Klasse laufen | Julia Hintersteiner, 26.08. |

**Bestand am Kickoff-Tag:** 59 offene Issues, davon 46 `auto:blocked`, 7 `auto:checkin`, 5 `auto:pair`, 0 `auto:full` (#44 ist als evergreen von den Achsen ausgenommen). Ein Backlog, der zu drei Vierteln auf Menschen wartet, ist kein Umsetzungsrückstand, und eine Session, die ihn nicht senken kann, hat trotzdem nichts falsch gemacht.

Hier gehört hinein: was sich seit der letzten Session geändert hat, welche Entscheidungen von Menschen inzwischen vorliegen, und welche Issues diese Session anfasst.

**Die Einteilung wird nicht mehr von Hand gemacht.** Bis zum 2026-08-05 verlangte dieser Abschnitt, alle offenen Issues in sechs Gruppen zu sortieren und die Gruppenzahlen gegen `gh issue list` auf Vollständigkeit und Disjunktheit zu prüfen. Beides erledigt jetzt das Label-Schema: jedes Ticket trägt genau ein `auto:*`, ein `area:*` und ein `effort:*`, und `python scripts/audit/build-issue-matrix.py --check` meldet mit Exit 1, wenn ein Label fehlt oder der #44-Body veraltet ist. Genau ein Label pro Achse erzwingt die Disjunktheit, die vorher eine Bitte war.

**Was das Skript nicht ersetzt, und das ist der wichtigere Teil: ein Label erzeugt die Einteilung, nie die Freigabe.** Es ist eine Behauptung wie jede andere (Regel 21), und zwar eine, die zum Zeitpunkt des Vergebens galt. Vor jedem Issue, das die Session tatsächlich anfasst:

- **Die Kommentare seit der Labelvergabe lesen.** Ein `auto:full` von letzter Woche weiß nichts von dem Einwand, den KZW gestern in den Thread geschrieben hat. Das ist der eine Weg, auf dem die Matrix stillschweigend falsch wird, ohne dass ein Gate anschlägt.
- **`auto:blocked` nie „trotzdem" anfangen.** Die `wait:*`-Labels sagen, auf wen gewartet wird; bei mehreren wartet das Ticket auf alle.
- **Die Befunde am Code verifizieren**, mit aktuellen Fundorten. Zeilennummern in Issue-Bodys altern; die in diesem Playbook auch.

---

## 2. Betriebsvertrag der autonomen Session

**Der gemeinsame Teil steht in [`BETRIEBSVERTRAG.md`](BETRIEBSVERTRAG.md)** und wird beim Kickoff in den Prompt kopiert, nicht verlinkt (siehe [`KICKOFF-VORLAGE.md`](KICKOFF-VORLAGE.md)). Bis zum 2026-08-05 stand er hier und in zwei weiteren Playbooks gleichzeitig, und Kopien driften.

Was diese Session zusätzlich oder abweichend bindet:

1. **`main` ist tabu.** Kein Merge, kein Push. Alle Ergebnisse sind PRs, die chsteiner reviewt und mergt. Die Kickoff-Freigabe gilt nur für `claude/*`-Branches und das Erstellen von PRs.
2. **Konfliktmanagement ohne Merges:** PRs starten von `main`; bei Datei-Überschneidung wird der spätere Branch auf den früheren gestackt und der PR-Body sagt „nach PR X mergen". Wenn das Playbook „gestackt" sagt, muss der Branch das auch sein.
3. **Verifikation gezielt pro Welle** (`npm test -- <spec-fragment>`), nicht die volle Suite nebenher. Ein gefilterter Lauf sagt TEILLAUF und belegt damit keine Vollständigkeit; vor dem Push eines Code-PRs ist der Volllauf trotzdem fällig.

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
29. **Jede Session in ihrem eigenen Worktree, und am Ende räumt sie ihn wieder ab.** Der Hauptordner bleibt Referenz auf `main` und wird nicht als Arbeitsplatz benutzt; nur so sehen parallele Sessions einander nicht und keine verschiebt der anderen den Stand. `git worktree add -b <branch> <pfad> origin/main` legt die frische Basis aus Regel 28 im selben Zug an. Nach dem Merge gehören Branch **und** Worktree weg, im selben Zug, nicht in einer Aufräumsitzung Wochen später: am 2026-07-30 lagen vier Worktrees und acht Branches herum, drei davon aus Sessions vom 9. Juli, dazu vier verwaiste Verwaltungsordner in `.git/worktrees`. Vor dem Löschen den Merge belegen (`gh api "repos/<R>/pulls?state=all&head=<Org>:<branch>"`), aktive Worktrees an den Dateizeiten erkennen und in Ruhe lassen.
30. **Das Abräumen eines Worktrees ist kein Einzeiler, und es scheitert genau dann, wenn vorher Tests liefen.** `git worktree remove --force` bricht mit „Permission denied" ab, zweimal: am Verzeichnis und am Eintrag unter `.git/worktrees/<name>`; `git worktree prune` bekommt den Eintrag ebenfalls nicht weg. Die Ursache ist kein kaputtes Verzeichnis, sondern ein Halter. Am 2026-07-30 war es ein übriggebliebener `node.exe` der Playwright-CLI, dessen Arbeitsverzeichnis noch im Worktree lag; gefunden über `Get-CimInstance Win32_Process` mit Filter auf die Kommandozeile. Irreführend dabei: auch `Rename-Item` blockiert, es sieht also nach Defekt aus. Reihenfolge, die trägt:
    1. Dev-Server und Testprozesse beenden (`npm run serve`, `npm test`, Playwright-Treiber).
    2. **Junctions einzeln lösen**, bevor irgendetwas rekursiv löscht. Wer `node_modules` als Junction ins Hauptverzeichnis gelegt hat, um Playwright ohne zweite Installation zu fahren, zerstört mit einem rekursiven Löschen das Original. `rmdir <pfad>` hebt die Junction auf und lässt das Ziel unberührt; danach prüfen, dass die Einträge im Hauptordner noch stehen.
    3. `git worktree remove`, dann `git worktree prune`.
    4. **Nachsehen, ob `.git/worktrees/<name>` wirklich weg ist.** Bleibt der Ordner, von Hand entfernen. Ein Worktree, der aus `git worktree list` verschwindet, ist nicht automatisch abgeräumt: der Verwaltungsordner überlebt das regelmäßig.
    5. **Und im Elternverzeichnis nachsehen, ob die Hülle noch liegt.** Git räumt weg, was Git kennt; ungetrackte Verzeichnisse können bleiben. Am 2026-08-03 lagen vier davon herum (`mhdbdb-wt-314`, `-323`, `-327`, `-331`), jede mit genau einem leeren `node_modules` darin und sonst nichts, zusammen 56 KB. `git worktree list` zeigte dabei nur den Hauptbaum und `.git/worktrees` existierte gar nicht: das Abräumen hatte also funktioniert, übrig blieb, was nicht von Git stammt. Deshalb `git worktree remove --force` nehmen, das erfasst auch die ungetrackten Dateien (Punkt 3 nennt die Form schon), und danach einmal `ls -d ../<praefix>*` laufen lassen. Ob die vier Hüllen aus einem Remove ohne `--force` stammen, ist nachträglich nicht mehr feststellbar. **Der Blick ins Elternverzeichnis gilt nicht nur Verzeichnissen:** dieselbe Suche förderte am Abend des 2026-08-03 sieben Testlogs zutage (`../mhdbdb-wt-314-testrun*.log`, `-323-*`, 806 KB, vom 1. August). Wer `npm test > ../<name>.log` umleitet, legt die Datei neben das Repo, wo weder `git status` noch `git worktree remove` sie je sieht. Deshalb `ls -d ../<praefix>*` ohne Filter auf Verzeichnisse.

    Und die Lehre über den Vorgang hinaus: **aus dem Verschwinden eines Eintrags auf eine Ursache zu schließen, ist geraten, nicht gemessen.** Genau dieser Satz stand als „hat sich selbst aufgeräumt" schon in einem Handoff, obwohl in Wahrheit jemand vier blockierte Löschversuche von Hand aufgelöst hatte.

32. **Das Em-Dash-Gate deckt Markdown seit #292, aber nur im Diff.** Bis zum 2026-08-02 galt hier das Gegenteil, und der Satz ist es wert, stehen zu bleiben: das Gate prüfte nur HTML, JS und CSS, in PR-Bodys stand trotzdem „Gate grün" als Beleg für Doku-Änderungen, und ein Beleg, der nichts belegt, ist schlechter als keiner. Was jetzt gilt: `check-no-em-dash.py --diff-base <rev>` prüft zusätzlich jede `.md`-Zeile, die ein PR **hinzufügt**, mit Fences und Inline-Code als Ausnahme (die Hausregel stellt Code und Terminal-Ausgaben frei). In CI ist die Base der erste Elternteil des ausgecheckten Merge-Refs, in `no-cdn-check.yml` wie in `data-integrity.yml`. Der Bestand bleibt bewusst unberührt, denn die Schreibregel gilt für neuen und überarbeiteten Text: rund 470 Zeilen in den getrackten `.md` tragen einen Em-Dash, gut die Hälfte davon in `docs/journal-archive.md`. **Handarbeit bleibt nur außerhalb von `.md`**: `tei/`, `authority-files/`, `schema/` und die zwei Linecode-CSVs unter `docs/data/`, wo der Strich ohnehin Datenzeichen ist und keine Typografie.

    **Nachtrag 2026-08-03: die Regel gilt für jede `.md`, ohne Ausnahme nach Ordner.** Am selben Tag wurde beides ausprobiert. Zuerst hieß es, die Hausregel gelte nur für user-sichtbaren Text, ein Treffer in `docs/` sei also Rauschen; dann wurde die Einschränkung gebaut (weiße Liste, Umfangsprüfung an zwei Eintrittspunkten, neun Fixture-Fälle, 267 Zeilen) und noch vor dem Merge verworfen. Die Verengung erzeugte zwei eigene Löcher: `git mv docs/entwurf.md publications/entwurf.md` trug den Em-Dash-Bestand von `docs/` stumm in den Veröffentlichungspfad, weil eine erkannte Umbenennung keine hinzugefügten Zeilen hat, und derselbe Fehler noch einmal für einen Umzug aus `_archived/` heraus. Dazu kam die Frage „ist diese Datei user-sichtbar?", die pro neuer Datei wiederkommt. Gemessene Kosten der stumpfen Regel: 5 von 100 Commits der letzten zwei Wochen, zusammen 6 Zeilen. **Lehre über den Anlass hinaus: eine Ausnahme, die pro Fall entschieden werden muss, ist teurer als die Regel, die sie sparen soll.** Wer den Strich billig loswird, tut es; wo er Gegenstand ist (Zitat, Werktitel), setzt er Backticks.

---

## 3. Wellenplan (Stand 2026-08-31, vor der nächsten Session überschreiben)

Drei Wellen, drei PRs, **strikt nacheinander statt gestapelt**, weil alle drei `tei/WZB.tei.xml` anfassen und zwei davon dieselbe abgeleitete Schicht. Kein Meta-PR: der JOURNAL-Eintrag für alle drei Wellen lief in der letzten Welle mit, nach derselben Überlegung wie am 2026-08-07.

| Welle | Ticket | PR | Ergebnis |
|---|---|---|---|
| 1 | #315 | #374 | `role="lead-editor"` aus der WZB entfernt, Doku von vier auf fünf Sigel; abgeleitete Schicht nachweislich unberührt, kein Bump |
| 2 | #367 | #377 | 40 Belege vom Verb aufs Adjektiv umannotiert, zwei neue Variantentypen; Korpus 4.2.5, Authority 1.9.2 |
| 3 | #235 Punkt 3 | #379 | 66 von 289 Breve-Tokens mechanisch nachannotiert, 223 als Review dokumentiert; Korpus 4.2.6, Authority unverändert |

**Was die Reihenfolge tatsächlich erzwungen hat, war nicht der Konflikt, sondern die Behauptung.** Welle 1 sagt „diese Änderung erreicht die Indexe nicht", Welle 2 und 3 sagen „diese schon, und zwar genau so". Wären sie gestapelt gelaufen, hätte keine der drei Aussagen mehr isoliert belegt werden können.

Muster: Welle 0 ist der Vorflug (beide Zählungen aus Regel 28 müssen 0 sein, `origin/main...HEAD` und `origin/main..main`; `python scripts/audit/check-index-versions.py`; die im Playbook genannten Fundorte aufsuchen und bestätigen; `testing/tests/` nach einschlägigen bestehenden Specs durchsehen; **kein voller `npm test` als Hintergrund-Baseline**). Danach eine Welle je PR, jede mit eigener Verifikation. Die letzte Welle ist der Meta-PR.

Bei Datei-Überschneidungen zwischen den Wellen den späteren Branch auf den früheren stacken und die Merge-Reihenfolge in den PR-Body schreiben. Der Meta-PR berührt fast immer `JOURNAL.md` und `ROADMAP.md` und kollidiert damit mit jedem PR, der Doku anfasst.

---

## 4. Nicht anfassen (Stand 2026-08-31, vor der nächsten Session überschreiben)

Alle 46 `auto:blocked`-Tickets, ohne Ausnahme. Ausdrücklich benannt wurden fünf, weil sie nach leichtem Einstieg aussehen:

- **#216** (minne, Serie 1) und **#371** (`stat`, 51 Belege für ein drittes Lemma): sehen wie Fortsetzungen der gerade gemergten Serien aus, warten aber auf eine editorische Entscheidung von KZW.
- **#370** (52.097 WZB-Tokens mit `lemmaRef` ohne `corresp`): liegt genau im Weg von Welle 3 und ist trotzdem tabu. Welle 3 hat deshalb bewusst kein `corresp` geschrieben, statt das Ticket nebenbei anzufangen.
- **#28** (KWIC-Grenzfälle) und **#255** (Frauenlob-Folgefrage): beide schon einmal wiedereröffnet worden.

Dazu kam die Falle in der Gegenrichtung: **#378** entstand während Welle 2 als Nebenbefund und ist sofort `auto:blocked`/`wait:kzw` gelabelt worden, statt ihn anzufangen.

Die Liste wird aus §1 abgeleitet und nennt alle Issues, die diese Session NICHT berührt, gruppiert nach Grund: Review-Gate (Ping ist draußen), menschen-blockiert, future/trigger/extern, Ingest. Dazu gehört jedes Mal:

- **Die Fallen ausdrücklich benennen**, also Issues, die nach leichtem Einstieg aussehen, sich aber im eigenen Ticket-Text auf etwas anderes sperren.
- **Kein Merge nach `main`.**
- Alle Gruppen werden nur in der #44-Matrix korrekt einsortiert, nicht bearbeitet.

---

## 5. Getroffene Entscheidungen (Stand 2026-08-31, vor der nächsten Session überschreiben)

1. **Ein PR je Issue**, Merge-Reihenfolge 1, 2, 3. Begründung in §3.
2. **Der Merge nach `main` war ausnahmsweise freigegeben**, für genau diese drei PRs, jeden einzeln, und an vier Bedingungen gebunden: `npm test` gelaufen und die VERDICT-Zeile unverändert im PR, `fable-reviewer`-Runde abgeschlossen und jeder übernommene Befund nachgemessen, CI grün (auf den Daten-PRs besonders `data-integrity.yml`), und `Closes #N` nur für das, was wirklich vollständig fertig ist. **Direkte Pushes auf `main` und jeder Force-Push dorthin blieben tabu.** Das ist die erste Session mit dieser Konstruktion, und sie hat gehalten, weil die Bedingungen prüfbar formuliert waren und nicht als Vertrauensfrage.
3. **Punkt 1 von #235 vor Punkt 3**, damit der Matcher auf gesplitteten Tokens arbeitet. Stellte sich als gegenstandslos heraus: Julia hatte Punkt 1 am 26.08. bereits erledigt.
4. **Neue Variantentypen prägen statt bestehende umhängen** (#367). Eine bestehende Nummer hinge sonst an zwei Lemmata, und `extract-variants.py` schlüge sie der häufigeren Seite zu, also weiter dem Verb.
5. **Ein neues Issue war freigegeben** (die #367-Ausweitung), weitere nur oberhalb der Regel-16-Schwelle. Geworden sind es drei: #375 (die freigegebene), #376 und #378, beide mit einer Entscheidung, die eine Session nicht treffen darf.

Hier gehören die Vorab-Festlegungen von chsteiner hinein: Reihenfolge der Wellen, Richtungsentscheidungen bei mehreren vertretbaren Umsetzungen, und was ausdrücklich draußen bleibt. Jede mit einem Satz Begründung, damit die Session sie nicht neu verhandelt.

---

## 6. Kickoff-Prompt (Stand 2026-08-31, vor der nächsten Session überschreiben)

**Die Bausteine stehen in [`KICKOFF-VORLAGE.md`](KICKOFF-VORLAGE.md)**, inklusive des Betriebsvertrags, der wörtlich in den Prompt kopiert wird. Was der Kickoff vom 31.08. in die Platzhalter gesetzt hat:

1. **Autorisierung:** `claude/*`-Branches und PR-Erstellung wie immer, dazu ausnahmsweise der Merge der drei Session-PRs unter den vier Bedingungen aus §5. Punkt 1 von §2 („`main` ist tabu") ist damit für diese Session teilweise ausgesetzt gewesen, und der Kickoff hat das ausdrücklich gesagt, statt es dem Schluss zu überlassen. **Wenn eine künftige Session dieselbe Freigabe bekommt, gehört sie genauso explizit in den Prompt**, samt der Bedingungen: eine Freigabe, die man sich aus dem Umfang erschließen muss, ist keine.
2. **Umfang:** drei Wellen, ein PR je Ticket, der JOURNAL-Eintrag in der letzten Welle.
3. **Weiche `npm test`:** volle Suite, ausdrücklich freigegeben, so oft wie nötig. Seit dem 24.08. ist das ohnehin die stehende Regel, der Satz stand trotzdem im Prompt.
4. **Notationsfallen:** Token-IDs sehen aus wie Versnummern (`WZB_5ra_14_3`), die Zeichenfolge Backslash-`u0020` stand im Korpus literal da und war keine aufzulösende Escape-Sequenz, und `lemma_7338` (das Adjektiv) ist nicht `lemma_7505` (das Verb).
5. **Verifikations-Handwerk aus §2.1** in Kurzform, mit der Mutations-Regel.
6. **Nicht anfassen** mit den fünf ausdrücklich benannten Fallen aus §4.

Was die alte Fassung dieses Abschnitts an dieser Stelle sagte, gilt unverändert weiter:

1. **Autorisierung:** `claude/*`-Branches und PR-Erstellung, `main` bleibt tabu.
2. **Umfang:** die Wellen aus §3, je eine pro PR, letzte Welle ist der Meta-PR. **Welle 0 als Vorflug ausschreiben.**
3. **Weiche `npm test`:** ob die volle Suite freigegeben ist oder nur gezielte Läufe. Ohne diesen Satz hat die Session keinen Weg, die stehende Konvention „Tests nie ungefragt" aufzulösen, und darf zugleich nicht nachfragen. Bis zum 2026-08-05 fehlte er hier, während §2 den Volllauf vor dem Push verlangte.
4. **Notationsfallen**, falls welche im Spiel sind (etwa Befund-Nummern in einem Issue-Body, die wie Issue-Nummern aussehen).
5. **Das Verifikations-Handwerk aus §2.1** in Kurzform, mindestens die Mutations-Regel.
6. **Nicht anfassen** mit den Gruppen aus §4, inklusive der Fallen („sieht nach leichtem Einstieg aus, ist aber blockiert").

---

## 7. Session-Ergebnis (Anhang, Stand 2026-08-31)

Drei PRs, drei Tickets, zwei davon geschlossen. Kein Meta-PR: der JOURNAL-Eintrag für alle drei Wellen lief in Welle 3 mit, aus demselben Grund wie am 2026-08-07.

| Ergebnis | Issue | Inhalt |
|----|-------|--------|
| PR #374, geschlossen | #315 | `role="lead-editor"` aus der WZB entfernt, Doku an vier Stellen von vier auf fünf Sigel. Die abgeleitete Schicht ist nachweislich unberührt: `lead-editor`, `Hintersteiner` und `respStmt` kommen in keiner der vier `data/*.json.gz` und in keiner der 2.742 API-Dateien vor, der Neubau ist byte-identisch, kein Bump |
| PR #377, geschlossen | #367 | 40 Belege der Fügung *der/die wâren minne* vom Verb aufs Adjektiv umannotiert (`lemma_7505` auf `lemma_7338`), zwei neu geprägte Variantentypen. Korpus 4.2.5, Authority 1.9.2 |
| PR #379, Ticket bleibt offen | #235 | Punkt 3: 66 von 289 Breve-Tokens mechanisch nachannotiert, 223 als Review dokumentiert. Punkt 1 und 2 waren erledigt, ohne dass das Ticket es wusste. Korpus 4.2.6, Authority unverändert |
| neu angelegt | #375, #376, #378 | Je eine Entscheidung, die eine autonome Session nicht treffen darf; alle drei `auto:blocked`/`wait:kzw` |

**Fünf Dinge, die die nächste Session wissen sollte:**

1. **Ein Diff, der zeichenweise stimmt, ist keine Messung.** Das Edit-Werkzeug hat beim ersten WZB-Edit 17 fremde reine LF-Zeilen still auf CRLF vereinheitlicht; die Diff-Hunks sahen exakt richtig aus. Sichtbar wurde es nur beim Byte-Vergleich. Bei jeder Datei mit gemischten Zeilenenden gehört das Zählerpaar (CRLF, LF) vor und nach der Änderung ins Protokoll, und die Änderung selbst läuft über exakte Byte-Ersetzung mit `newline=""` bei Lesen **und** Schreiben. `tei/WZB.tei.xml` ist die einzige CRLF-Datei im Korpus (1 von 667) und damit der einzige Ort, an dem das überhaupt auffällt.
2. **Und die Kontrollzahl aus Welle 1 hat denselben Fehler in Welle 3 gefangen**, ohne dass jemand nach ihm gesucht hätte: `revisiondesc-homograph.py` schrieb seinen Eintrag mit hartem `"\n"`. Der Wert dieser Zähler liegt nicht im ersten Fund, sondern in den späteren.
3. **Ein Fix an einem Skript kann den nächsten Fehler erst scharf machen.** Nachdem die Einfügung das Zeilenende der Umgebung nahm, fand die Löschregex für den eigenen Alteintrag ihn nicht mehr (`</change>\n` gegen einen CRLF-terminierten Eintrag), während der Kopf-Check darüber ihn sehr wohl sah: ein zweiter `--apply`-Lauf hätte den Eintrag verdoppelt. Gefunden hat das der lokale Review, kein Gate. **Nach einer Änderung am Zeilenende-Verhalten alle Stellen suchen, die Zeilenenden in einer Regex literal nennen.**
4. **`git checkout -- <datei>` stellt aus dem Index her, nicht aus dem Stand davor.** In einer Session mit mehreren Commits auf demselben Branch heißt das: der Rückbau vor einem Neulauf muss `git checkout origin/main -- <datei>` sein, sonst läuft das Skript auf dem bereits geänderten Bestand und meldet plausibel aussehenden Unsinn (hier: 223 statt 289 Kandidaten). Steht als Regel 31 in der Memory und ist trotzdem wieder passiert.
5. **`npm test` nie durch eine Pipe.** Ein `| tail -25` puffert die gesamte Ausgabe bis zum Ende und macht den Reporter unlesbar; der Lauf musste abgebrochen und wiederholt werden. Die VERDICT-Zeile ist das Ergebnis, und sie kommt nur unverpipet.

**Was aus der Session vom 2026-08-07 weiter gilt:** ein Worktree hat kein `node_modules`, ohne Junction auf den Hauptbaum läuft `npm test` gar nicht erst an, und beim Abräumen kommt zuerst `rmdir` auf die Junction (Regel 30, Punkt 2), sonst nimmt das rekursive Entfernen das Original mit.
