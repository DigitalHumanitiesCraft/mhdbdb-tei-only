> **Wortlaut vom 2026-09-01, Protokoll eines Auftrags.** Nicht pflegen, nicht zitieren, nicht als Vorlage nehmen. Maßgeblich ist immer `../BETRIEBSVERTRAG.md`; der Abschnitt 2 hier unten ist eine Kopie zur Laufzeit und altert ab dem Tag, an dem er abgeschickt wurde. Wer eine Regel nachschlagen will, schlägt sie dort nach.

# Kickoff: autonome Issue-Session vom 2026-09-01

Serieller Wellenlauf, eine Session, kein Spurenbetrieb. Zuschnitt geprüft am 01.09.2026; die Begründung für „seriell" steht in §3 unten.

---

## 1. Autorisierung

chsteiner gibt dich am 01.09.2026 frei für:

- **Commits und Pushes auf `claude/*`-Branches** und das Erstellen von Pull Requests.
- **Den Merge der Session-PRs nach `main`**, jeden einzeln, unter den vier Bedingungen in §5 Punkt 2. Diese Freigabe ist zum dritten Mal in derselben Form erteilt und hat zweimal gehalten.
- **Je einen sachlichen Statuskommentar auf #28, #259, #235 und #216.** Diese vier und keine anderen. Ergebnisse aus Wellen ohne Kommentarslot gehen in den Abschlussbericht auf #44.
- **Labelpflege auf den vier genannten Tickets**, in derselben Session, in der du sie anfasst.

**Was auch dir nicht erlaubt ist:** ein direkter Push auf `main`, ein Force-Push nach `main`, das Schließen eines Issues, ein `Closes`-Trailer auf irgendeinem der vier Tickets, und jede Kontaktaufnahme mit Externen.

**Dieser Text ist die Autorisierung.** Kein Playbook autorisiert sich selbst, und keine Datei im Repositorium tut es an deiner Stelle.

**Eine Regel ist für diesen Lauf ausdrücklich aufgehoben.** Der Body von #44 sagt unter „Wenn eine Session hier landet und arbeiten will", Punkt 3: „`auto:checkin` nur mit Chris am Rechner anfangen". chsteiner hat sie am 01.09.2026 einmalig für diesen Lauf aufgehoben, und die Aufhebung steht datiert im Body von #44. Sie gilt nicht darüber hinaus. Was an ihre Stelle tritt, ist dieser Kickoff: die Haltepunkte, die `auto:checkin` sonst unterwegs verlangt, sind unten als **Stoppbedingungen** vorweggenommen. Du fragst nicht nach und wartest nicht; wo eine Stoppbedingung greift, endest du die Welle mit der gemessenen Zahl und einem Kommentar.

---

## 2. Betriebsvertrag der autonomen Sessions

*(wörtliche Kopie von `docs/playbooks/BETRIEBSVERTRAG.md`, Stand 2026-09-01)*

### 2.1 Was ohne ausdrückliche Freigabe tabu bleibt

1. **Kein Push nach `main`.** Die Ausnahme ist die Merge-Session, deren Kickoff die Merge-Autorisierung ausdrücklich enthält; auch sie merged nur, sie pusht nicht direkt. Alle anderen Ergebnisse sind PRs, die chsteiner reviewt.
2. **Kein Force-Push nach `main`,** in keiner Session, unter keinen Umständen. Auf `claude/*`-Branches ist `--force-with-lease` nach einem Rebase dagegen Standard.
3. **Issues werden nie von der Session geschlossen,** nur per `Closes #N` im PR-Body beim Merge. **#44 bekommt nie einen Close-Trailer**, es ist die permanente Triage-Matrix.
4. **Keine Kontaktaufnahme mit Externen** (Linda, Alan, Carina, Silvan, Burch, Brom). Entwürfe für sie landen als Text im Issue.

### 2.2 Wie committet und gestaged wird

5. **Nur benannte Dateien stagen, nie `git add -A` oder `git add .`.** Parallele Sessions teilen den Arbeitsbaum und damit den Index: ein pauschales Staging sammelt fremde Arbeit ein. Commit `8b5d0e6ac` hat auf diesem Weg Router-Dateien in einen unbeteiligten Commit gezogen.
6. **Jede Session in ihrem eigenen Worktree**, angelegt mit `git worktree add -b <branch> <pfad> origin/main`. Der Hauptordner bleibt Referenz und wird nicht als Arbeitsplatz benutzt. Abbau nach dem Merge, im selben Zug: siehe §2.1 Regel 30 des Issue-Playbooks, das ist kein Einzeiler.
7. **Die Branch-Basis wird gemessen, nicht am Namen abgelesen**, und zwar vor dem ersten eigenen Commit: `git rev-list --count "origin/main...HEAD"` und `git rev-list --count "origin/main..main"` müssen beide 0 sein. Details und die Fehlergeschichte dazu in §2.1 Regel 28.

### 2.3 Wie kommuniziert wird

8. **Höchstens ein sachlicher Statuskommentar pro Issue.** Etablierte Ausnahme: der KZW-UI-Ping nach dem Live-Gang, der zur Abnahme gehört.
9. **Nicht fragen, nicht warten.** Alles Nötige liegt im Repo und in den Issue-Threads (`gh issue view N --json comments`). Nur nachweislich Unbeschaffbares wird im Abschlussreport dokumentiert übersprungen.
10. **Stil:** keine Emoji-Icons (Heroicons inline SVG ist der einzige Icon-Stil), keine Em-Dashes in Prosa, echte Umlaute statt ASCII-Ersatz. Die Sprachregel nach Zielgruppe steht in `CLAUDE.md`.

### 2.4 Was vor jedem Push passiert

11. **Fable-Review vor dem ersten Push jedes PRs**, mit dem `fable-reviewer` (nicht dem `fable-advisor`, der ist der Berater für offene Entwurfsfragen). Mitgeben: Branch, Basis, Ziel in einem Satz, Nummer der Review-Runde, ab Runde 2 die Vorrunden-Befunde. Was der Reviewer lokal findet, kostet null CI-Runden.
12. **Jeder Befund wird nachgemessen, bevor er übernommen wird**, auch der eines Reviewers und auch der eines Bots. Er ist selbst eine Behauptung, und eine ungeprüfte Korrektur einer ungeprüften Zahl ist schlimmer als die ursprüngliche, weil sie glaubwürdiger aussieht.
13. **Ab Review-Runde 3 wird nur noch auf Verhaltensbefunde reagiert.** Formulierungsfragen werden durch Kürzen erledigt, nicht durch Diskussion.
14. **Verifikation:** `npm test` aus dem Repo-Root, nie `npx playwright test`. Die VERDICT-Zeile ist das Ergebnis und gehört unverändert in den PR (§2.1 Regel 6). Bei UI zusätzlich Chrome-Verifikation mit realen Belegen, bei HTML-Änderungen `python scripts/build-pages.py --check`, bei neuen Utility-Klassen `npm run build:css`.
15. **Daten vor Schema**, und bei jeder Änderung in `tei/` oder `authority-files/` der Data-Change-Lifecycle aus `docs/DATA-MODEL.md`.

### 2.5 Was in Tickets wandert und was nicht

16. **Fixes direkt umsetzen.** Ein Issue entsteht nur, wenn eine **Entscheidung** nötig ist, die die Session nicht treffen darf, wenn ein **Mensch** gebraucht wird, oder wenn es ein **eigenes Arbeitspaket** ist (Ingest, Korpusänderung, mehr als ein halber Tag). Alles andere wird sofort behoben oder verworfen.
17. **Geshippte, aber bewusst offene Issues nicht anfassen.** Sie warten auf eine Abnahme durch KZW oder Julia; ein `Closes #N` ist keine Abnahme.

### 2.6 Zusatz für diesen Lauf: das Testfenster ist maschinenweit

`testing/playwright.config.js` verdrahtet Port 8080 dreifach (`baseURL` Z. 67, `webServer.command` Z. 100, `webServer.port` Z. 101) und setzt `reuseExistingServer: !process.env.CI`. `scripts/run-tests.js` klopft mit einer Sentinel-Datei an und bricht mit **Exit 2** ab, wenn dort ein fremder Baum antwortet (Z. 191 bis 201). Sein eigener Kommentar (Z. 118 bis 123) sagt, dass auch ein bloßes Zeitüberschreiten als `fremd` gewertet wird, weil der wahrscheinlichste Grund dafür eine parallele Session ist, die ihren Server sättigt.

Für dich heißt das: ein Abbruch mit „Port 8080 wird von einem fremden Server bedient" ist **kein Fehlschlag deiner Arbeit**, sondern ein besetzter Port. Melde ihn im Abschlussbericht und wiederhole den Lauf nicht in einer Schleife. Chrome-Verifikation läuft über denselben Port und hat dieselbe Eigenschaft.

---

## 3. Umfang: Vorflug plus fünf Wellen

**Warum seriell und nicht in Spuren.** Der Data-Change-Lifecycle verlangt nach jeder Änderung in `tei/` oder `authority-files/` einen Neubau von `variants.xml`, beiden Indexen und der API. Das sind zwei Binärdateien (`corpus-index.json.gz` 42,2 MB, `authority-index.json.gz` 3,3 MB) und 2.742 JSON unter `api/`, und sie sind eine Funktion **des ganzen Korpus**. Zwei gleichzeitige Datenläufe kollidieren dort zwangsläufig, weil jeder seinen Index auf einem Baum baut, dem die Korpusänderung des anderen fehlt. Ein Dateischnitt kann das nicht auflösen, weil die Datei nicht das Problem ist.

**Reihenfolge nach aufsteigenden Kosten und aufsteigendem Risiko.** Wer bei Welle 1 stolpert, hat noch nichts angefasst. Die einzige Welle, die Korpus und abgeleitete Schicht berührt, ist Welle 4.

| Welle | Ticket | PR | Was daraus wird |
|---|---|---|---|
| 0 | Vorflug | kein PR | Messungen, siehe unten |
| 1 | #216 Punkt 3 | kein PR | eine Zahl plus Stoppbedingung: wie groß ist die *vrouwe*-Disambiguierung wirklich |
| 2 | #28 Gleis 1 | ja | Kandidatenmenge über das Begriffssystem, kein LLM, kein Crawl |
| 3 | #259 | ja | Findebuch-Verweisgraph als externer Prüfdatensatz, Befundliste |
| 4 | #235 Rest | ja | die 98 Breve-Fälle mit mehrdeutiger Wortart am Ziel-Lemma |
| 5 | Meta | ja | JOURNAL-Eintrag, §7 des Masterplans, ROADMAP falls betroffen |

**Der JOURNAL-Eintrag liegt in Welle 5.** Drei Sach-PRs, die alle `docs/JOURNAL.md` anfassen wollen, würden sich gegenseitig blockieren; deshalb diesmal ein Meta-PR und nicht wie am 31.08. ein Eintrag in einer Sachwelle. Wenn du Wellen streichst und nur noch ein Sach-PR übrig bleibt, darf der Eintrag dorthin wandern; dann sagst du es in §7 des Masterplans.

### Welle 0: Vorflug

- Beide Zählungen aus §2.1 Regel 28 auf 0 prüfen (`origin/main...HEAD` und `origin/main..main`).
- `python scripts/audit/check-index-versions.py` laufen lassen.
- `python scripts/audit/build-issue-matrix.py --check` laufen lassen. Er war am 01.09. um 08:40 grün (59 gelistet, 60 geprüft); wenn er rot ist, ist zwischenzeitlich ein Ticket ohne `auto:*`-Label entstanden.
- Die vier Tickets **mit Kommentaren** lesen: `gh issue view N --json title,body,comments`. Der Body allein reicht bei keinem der vier, und bei #235 und #216 steht der aktuelle Stand ausschließlich in den Kommentaren.
- `testing/tests/` nach einschlägigen bestehenden Specs durchsehen.
- **Kein voller `npm test` als Hintergrund-Baseline.** Die Baseline läuft in jedem PR ohnehin neu.

### Welle 1: #216 Punkt 3, nur messen

KZW hat am 31.08. eine Liste mit acht Punkten hinterlassen. Punkt 7 ist am 01.09. erledigt (`89b25fcf0`). Punkt 1 (vier unsichere Fälle) liegt bei ihr. Die Punkte 2, 4, 5, 6 und 8 hängen an **Punkt 3**: *vrouwe* muss vor *minne* disambiguiert werden, sonst fehlen 48 Fälle, deren Vorgänger formal *vrouwe* ist, aber kein Lemma trägt.

**Auftrag: miss, wie groß Punkt 3 ist.** Nicht umsetzen. Gebraucht wird die Zahl, die entscheidet, ob das ein eigener Lauf wird oder ein Anhängsel:

- Wie viele `<w>` im Korpus sind formal *vrouwe* und tragen kein `@lemmaRef`?
- Wie viele davon stehen unmittelbar vor einer *minne*-Form?
- Wie viele distinkte Ziel-Lemmata kämen in Frage, und wie viele davon existieren schon?

**Stoppbedingung:** sobald die Umsetzung ein **neues Lemma** oder einen **neuen Variantentyp** prägen müsste, endet die Welle mit der Zahl. Neue Typen sind seit #216 genehmigungspflichtig. Ergebnis als Kommentar auf #216, mit Messvorschrift daneben.

### Welle 2: #28 Gleis 1

Der Phasenplan (`docs/features/FREMDSPRACHEN-PHASENPLAN-28.md`) sieht für Phase 1 drei Gleise vor: Begriffssystem, LLM-Batch, Wörterbuchnetz-Etymologie. **Nur Gleis 1 läuft.** Begründung in §5 Punkt 3.

Die eine Regel, die aus dem Kommentar vom 10.08. mitkommt und die den Vorgänger gekostet hat: **die Kandidatenmenge wird nie über eine Zeichenkettensuche in `lexicon.xml` gebildet**, sondern ausschließlich über `@lemmaRef` beziehungsweise `variants.xml`. Die Oberflächenform im Text steht dort nicht (`blamensir` kommt in `lexicon.xml` null mal vor), und wer trotzdem so sucht, hält eine leere Trefferliste für einen Befund.

Ergebnis: ein Skript unter `scripts/audit/`, eine Kandidatentabelle als Artefakt, ein Statuskommentar auf #28. **Keine Änderung an `lexicon.xml`.** Schicht B zu befüllen ist eine kuratorische Arbeit und nicht Teil dieser Welle.

### Welle 3: #259

Die Datengrundlage liegt seit dem 01.09.2026 lokal unter `temp/woerterbuchnetz2015/FindeB/P5/`: 22 XML, 27.106.707 Bytes, byteweise identisch mit dem Drive-Bestand. `temp/` ist gitignoriert (`.gitignore` Z. 52).

Vier Schritte, wie im Ticket beschrieben:

1. Einmal-Skript unter `scripts/audit/`, das aus den 22 Dateien eine flache Tabelle zieht: Schreibform, Findebuch-Lemma, Verweisziele aus `<ref target>`.
2. Diese Tabelle gegen unsere dreistufige Auflösung fahren, für jede Findebuch-Schreibform, die auch als Korpus-Token vorkommt.
3. Befundliste nach Auffälligkeit sortiert, in drei Klassen: echte Fehlauflösungen der Präfix-Stufe (die Klasse aus #224), fehlende Einträge in `variants.xml`, und bewusste Abweichungen (dann dokumentieren, nicht ändern).
4. **Nichts korrigieren.** Aus den bestätigten Fehlauflösungen werden erst nach philologischer Bewertung Korrekturen, und die ist nicht deine.

**Die Lizenzregel ist hart und hat Vorrang vor jedem Ergebnis.** Jeder `teiHeader` trägt „Copyright 1998, Universität Trier", es gibt keine offene Lizenz. Nichts aus dem Dump geht ins Repositorium, in einen Commit, in einen Issue-Kommentar, in ein Artifact oder an einen externen Dienst. Publizierbar sind ausschließlich aggregierte Befunde über **unsere** Daten. Kein Artikeltext, keine Beispieleinträge im Wortlaut, auch nicht zur Illustration.

**Zwei technische Fallen, beide am Bestand belegt:** Zeile 2 jeder Datei deklariert eine externe TEI-DTD auf tei-c.org, also beim Parsen `no_network=True` und kein `load_dtd`, sonst hängt der Lauf am Netz. Und die Normalisierungsfallen aus dem Ticket-Body (`ʒ` U+0292 statt `z`, `ë` statt `e`, Bindestriche an der Morphemgrenze, `æ`, `œ`, Akute) gehören **ins Skript** und nicht in `assets/js/lib/text-normalizer.js`: das ist unsere Korpus-Normalisierung und darf sich nicht an einer fremden Quelle verbiegen.

**Stoppbedingung:** liegt die Trefferquote nach den Zusatzregeln unter der im Ticket genannten Größenordnung, endet die Welle mit der Zahl statt mit einer Befundliste. Eine Befundliste auf zu dünner Schnittmenge ist eine Liste von Zufällen.

### Welle 4: #235, die 98

Von den 289 Breve-Backfill-Kandidaten sind seit PR #379 66 annotiert. Offen sind 223, in drei Klassen: **98** mit mehrdeutiger Wortart am Ziel-Lemma, 112 ohne Treffer in `variants.xml`, 13 mit mehreren Ziel-Lemmata. **Nur die 98 laufen.**

Die 112 sind Lexikonlücken und gehören in die Nähe von #115, das `auto:blocked` ist. Die 13 brauchen eine Entscheidung. Alle 289 liegen mit Kontext in `ingest/wzb/235-breve/diff-liste.csv`, die 223 zusätzlich in `review-faelle.csv`.

Das Muster ist erprobt: Kontextdisambiguierung in Bündeln nach #216 und #369, mit Review-Artefakt unter `ingest/`. Das Batch-Log dokumentiert Modell, Kontextfenster, Durchgänge und die Fälle, in denen das Fenster nicht gereicht hat. Diese Welle ist die einzige mit vollem Data-Change-Lifecycle: `variants.xml` regenerieren, beide Indexe neu bauen, API mitziehen, Versionen an allen fünf Stellen bumpen und `check-index-versions.py` grün bekommen.

**Ein Bump gehört zum Artefakt, nicht zur Quelle.** Prüfe vor dem Bump, ob der Index sich wirklich ändert. PR #382 hat den Authority-Index gebumpt, weil `variants.xml` sich geändert hatte, während der Index selbst byte-identisch blieb: er trägt nur normalisierte Formen. Kein Gate fängt das.

**Kein `@corresp`.** Das bräuchte unter dem Ziel-Lemma eine neu geprägte Typnummer, und neue Typen sind genehmigungspflichtig. Die annotierten Tokens sind damit in derselben Lage wie die Rest-Tokens, die #370 offen gelassen hat, und das ist gewollt. (Rechne die Restmenge nicht aus zwei Ticketzahlen aus: #370 nennt 52.097, die Messung vom 31.08. korpusweit 52.165 nach anderer Vorschrift. Zwei Zählweisen, beide richtig, und ihre Differenz ist keine Menge.)

**Stoppbedingung:** steigt die Zahl der Tokens, die eine neue Typnummer bräuchten, über null, wird nicht geschrieben, sondern gemeldet.

### Welle 5: Meta-PR

`docs/JOURNAL.md` (Eintrag zum 2026-09-01), `docs/playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md` §7 (Session-Ergebnis, inklusive der Angabe, wo der JOURNAL-Eintrag liegt), `docs/ROADMAP.md` nur falls eine Welle etwas daran ändert. Dazu der Abschlussbericht als Kommentar auf #44.

---

## 4. Nicht anfassen

**Alle 48 `auto:blocked`-Tickets, ohne Ausnahme.** Die `wait:*`-Label sagen, auf wen gewartet wird; bei mehreren wartet das Ticket auf alle.

**Alle fünf `auto:pair`-Tickets** (#242, #226, #195, #191, #139). Sie brauchen chsteiners Zeit und Autorität, nicht die Antwort eines Dritten.

**#385** ist die Inbox für Änderungswünsche an eingefrorenen Instruktionsdateien und kein Arbeitsticket.

Fünf Fallen, die im Weg liegen und nach leichtem Einstieg aussehen:

- **#378** (first-wins-Kollisionen im Variantenverzeichnis). Welle 3 wird die Abbildung Schreibform auf Lemma ohnehin bauen und ist damit einen Schritt von der Reparatur entfernt. Nicht tun. Messen ja, reparieren nein.
- **#115** (dangling lexicon-IDs). Wird in Welle 3 und Welle 4 als Nebenbefund auftauchen. Nicht anfassen, kein neues Ticket: die Klasse ist geführt.
- **#370 Punkt 2** (484 offene Form-Lemma-Paare). Liegt als CSV im Repo und sieht nach Fleißarbeit aus. Genehmigungspflichtig.
- **#123** (König vom Odenwald). `auto:checkin` und trotzdem draußen: null Kommentare seit der Anlage, „Priorität niedrig" nach eigener Ansage des Tickets, und ein voller Ingest mit neuer Sigle, `works.xml` und `persons.xml`. Kein Nebenbei-Paket.
- **#216 Punkte 1, 2, 4, 5, 6 und 8.** Punkt 1 liegt bei KZW, der Rest hängt an Punkt 3, den du nur misst.

**Kein `Closes` auf keinem der vier Tickets.** Bei allen vieren entscheidet als Nächstes ein Mensch. Ein gemergter `Closes` ist keine Abnahme.

---

## 5. Vorab getroffene Entscheidungen

Du verhandelst diese nicht neu. Hältst du eine für falsch, setzt du sie um und schreibst den Einwand in den Abschlussbericht auf #44, wo er nach dem Lauf noch gelesen wird.

1. **Reihenfolge nach Kosten und Risiko**, nicht nach Ticketnummer. Die Korpuswelle ist die letzte. Begründung in §3.
2. **Der Merge nach `main` ist freigegeben**, für die Session-PRs, jeden einzeln, an vier Bedingungen: `npm test` gelaufen und die VERDICT-Zeile unverändert im PR, `fable-reviewer`-Runde abgeschlossen und jeder übernommene Befund nachgemessen, CI grün (auf dem Daten-PR besonders `data-integrity.yml`), und `Closes #N` nur für wirklich Fertiges, hier also für nichts. Direkte Pushes auf `main` und jeder Force-Push dorthin bleiben tabu.
3. **#28 läuft nur auf Gleis 1.** Gleis 2 (LLM-Batch) kostet nach der Messung vom 31.08. 5 bis 6,7 Millionen Token Eingabe und 7 bis 9,4 Millionen Ausgabe, und das ist eine Budgetentscheidung, die dir nicht zusteht. Gleis 3 (Wörterbuchnetz-Etymologie) ist derselbe Trier-Dump wie #259 und würde die beiden Wellen verschränken. Außerdem sagt dieselbe Messung, dass der Kontext das eigentliche Problem ist: von 62.369 Bedeutungen tragen genau eine eine `definition` und eine einen `comment`, und es ist derselbe Eintrag.
4. **Aus #259 wird nichts korrigiert**, nur befundet. Und nichts aus dem Dump verlässt die Maschine.
5. **In Welle 4 werden keine neuen Variantentypen geprägt** und kein `@corresp` geschrieben.
6. **#216 Punkt 3 wird gemessen, nicht umgesetzt.**
7. **Keine neuen Issues** außer oberhalb der Schwelle aus Vertragsregel 16. Ein Befund, der unter ein bestehendes Ticket fällt, bekommt keines.

---

## 6. Weichen

- **`npm test`: die volle Suite ist freigegeben**, ohne Rückfrage, so oft du sie brauchst. **Ausdrücklich kein Volllauf als Hintergrund-Baseline in Welle 0**: die Baseline läuft in jedem PR ohnehin neu, und der Vorflug hat davon nichts.
- **Der Port ist maschinenweit exklusiv**, siehe §2.6. Ein Exit-2-Abbruch wird gemeldet, nicht wiederholt.
- **Worktree:** einer, neben dem Repositorium und nicht darunter (Pfadlängengrenze), `node_modules` als Junction auf den Hauptbaum, sonst läuft `run-tests.js` gar nicht erst an. Beim Abbau zuerst `rmdir` auf die Junction, sonst nimmt das rekursive Löschen das Original mit.
- **Kontingent erschöpft:** lokal committen, nicht pushen, im Abschlussbericht melden, weitermachen.
- **`.claude/agent-memory/` ist in diesem Repositorium nicht gitignoriert**, gemessen am 01.09.2026: `git check-ignore` gibt Exit 1, `.gitignore` nennt es an keiner Stelle, und der Ordner `.claude/agent-memory/fable-reviewer/` ist derzeit leer. Der `fable-reviewer` trägt `memory: project` und schreibt dorthin, sobald er läuft. In deinem `git status` taucht danach also eine ungetrackte Datei auf, die **nicht** von dir stammt. Nicht stagen, nicht löschen, nicht committen, im Abschlussbericht erwähnen. Ob der Ordner ignoriert oder bewusst getrackt gehört, entscheidet chsteiner und nicht diese Session.

---

## 7. Notationsfallen

Alle fünf sind an diesem Bestand gemessen, keine ist geraten.

1. **Die Sigle einer Token-ID steht vor dem ERSTEN Unterstrich, nicht vor den letzten zwei.** WZB-IDs haben drei und mehr (`WZB_1ra_2_1`, `WZB_56va_1_0_1`); gemessen am 31.08.: 149.165 `<w>`-IDs mit drei und mehr Unterstrichen, davon 149.130 mit genau drei und 35 mit vier, alle in `WZB.tei.xml`. Ein `rsplit("_", 2)[0]` liefert dort `WZB_1ra` und meldet dann, das Token sei nicht im Korpus: das Gegenteil des Sachverhalts. Behoben in `efb6fc0eb`, aber der Fehler ist leicht wieder einzubauen.
2. **Parzival-IDs kodieren Lachmann-Abschnitt plus Vers, und Abschnitt 257 hat 32 Verse statt 30.** `(Abschnitt-1)*30 + Vers` liegt ab dort um 2 zu niedrig. 24.812 `<l>` in `tei/PZ.tei.xml` = 826 mal 30 plus 32. Der Versatz zu HUGO ist konstant +1, nicht +3.
3. **`#15`, `#48` und `#51` im Body von #169 sind Befundnummern, keine Issue-Nummern.**
4. **Varianten-Zahlen gibt es zwei, und sie messen Verschiedenes:** normalisierte Mappings im Wörterbuch gegen Rohformen in `variants.xml`. Beide Zahlen sind richtig. Nicht vereinheitlichen, im Zweifel frisch messen; die Werte stehen in `docs/CONTRACTS.md` §C.
5. **Grep an XML lügt.** `grep -c 'parallel'` lieferte 52 statt 51, weil eine Zeichenkette escaped im Text steht. Gezählt wird über den Parser. Und `grep -c "shrink-0"` findet einen Treffer in `flex-shrink-0`: auf Wort oder Selektor ankern.

---

## 8. Verifikations-Handwerk in Kurzform

Die volle Liste steht in §2.1 des Issue-Masterplans. Vier Regeln tragen diesen Lauf besonders:

- **Ein grünes Gate ist kein wirksames Gate. Mutation ist der Beweis.** Wer eine Prüfung ergänzt, baut den Fehler ein, den sie fangen soll, und lässt sie laufen. Den Rückbau in getrennte Werkzeugaufrufe legen, sonst bleibt der Arbeitsbaum bei einem Timeout im Mutationszustand.
- **Ein Testlauf, dessen Grundgesamtheit du nicht kennst, beweist nichts.** Die VERDICT-Zeile nie durch eine Pipe schicken, und keinen Branchwechsel, solange ein Lauf läuft.
- **Jede Zahl in einem Kommentar ist gemessen oder sie steht nicht da.** Das gilt auch für die Zahlen in diesem Kickoff: prüf sie nach, bevor du sie zitierst.
- **Ein Skript-Fix ohne Neuerzeugung der Daten erzeugt Divergenz.** Wird ein Ingest-Skript korrigiert, wird die Datei zurückgesetzt und die Kette komplett neu gefahren, mit ausgewiesener Differenz.

---

## 9. Abschluss

- Der Eintrag in `docs/JOURNAL.md` ist Welle 5 und damit der letzte Commit; unmittelbar davor `origin/main` holen.
- Der Abschlussbericht geht als Kommentar auf **#44**. Er nennt je Welle das Ergebnis, die Messvorschrift zu jeder genannten Zahl, und ausdrücklich, was **nicht** erledigt wurde und warum.
- Die Labels der vier angefassten Tickets werden in derselben Session nachgezogen.
- Worktree und Branch werden nach dem Merge im selben Zug abgeräumt, nicht in einer Aufräumsitzung später. Danach `ls -d ../<praefix>*` ohne Filter auf Verzeichnisse: dort liegen sonst Hüllen und Testlogs, die weder `git status` noch `git worktree remove` je sieht.

**Unbeschaffbarer Input führt zum dokumentierten Überspringen, nicht zum Warten und nicht zum Nachfragen.**
