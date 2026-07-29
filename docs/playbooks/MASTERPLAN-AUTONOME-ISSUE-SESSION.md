# Masterplan: Autonome Issue-Abarbeitungs-Session

**Erstellt:** 2026-07-03 (Audit-Session, Fable 5); mehrere Vorgänger-Sessions sind gelaufen und gemergt.
**Neu befüllt:** 2026-07-29 (nach der Merge-Session 28./29.07., Opus 5). Session-Inhalte 28.07. geleert; Git-History = Archiv.
**Status:** BEREIT. Kickoff-Prompt steht in §6. Vor der übernächsten Session §1/§3/§5/§6 neu befüllen.
**Typ:** Playbook (wiederverwendbares Session-Verfahren, dauerhaft). Der session-spezifische Teil (§1, §3, §5, §6) wird pro Session neu befüllt; der Betriebsvertrag (§2) und die Verifikations-Handwerksregeln (§2.1) sind der stabile Kern.

Quellen dieses Audits: alle 41 offenen Issue-Bodies und die Kommentarverläufe seit 27.07. (Stand 29.07. 10:00), die Entscheidungen von KZW vom 28.07. in #169 und #138, `git log` auf `main` bis `aa774199c`, sowie eigene Messungen gegen `data/authority-index.json.gz`, `playground/js/data/tei-manager.js` und `playground/js/ui/tei/tei-ui.js`.

---

## 1. Ausgangslage (Stand 2026-07-29)

41 offene Issues. Die Merge-Session vom 28./29.07. hat sechs PRs auf `main` gebracht (#241, #238, #243, #240, #244, #231); es ist kein PR mehr offen. **#196 hat KZW am 29.07. um 08:17 selbst geschlossen**, 14 Minuten nach dem Ping mit der Live-URL: das Hapax-Detailpanel ist abgenommen.

**Der Anlass dieser Session ist, dass KZW am 28.07. vier Entscheidungen getroffen hat**, die vorher blockierten:

In **#169** steht wörtlich „Option B ist bestätigt", dazu „**#15 Nähesuche: bitte fixen**" und „**#51 und #48: einverstanden, bitte umsetzen**". Achtung, Stolperstelle: `#15`, `#51` und `#48` sind **Befund-Nummern innerhalb des #169-Bodys**, keine Issue-Nummern. Wer sie als Issues nachschlägt, landet bei einem Actions-Workflow von 2025 und zwei längst geschlossenen Tickets.

In **#138** steht „stimme zu" unter der Kollation gegen die Hofmeister-Edition. Die Verszählung ist damit fachlich bestätigt; der Kern von #138 (die editorischen `<div>`-Hüllen) bleibt offen und weiter bei KZW.

Neu von KZW angelegt (28.07.): #242 Sparkling Science, #239 Wortbestandteil-Suche, #237 Vlastimil Brom, #236 Frauenlob. Neu von chsteiner: #235, #228.

### A. Voll autonom lösbar (2 + Meta)

| Rang | # | Was | Warum autonom | Aufwand |
|-----:|---|-----|---------------|---------|
| **1** | **#169** | Die drei von KZW freigegebenen Audit-Befunde fixen | Entscheidungen liegen schriftlich vor; alle drei Befunde am Code verifiziert (§1.1); frontend-only ohne Datenberührung | M |
| **2** | **#239** | Wortbestandteil-Suche als eigener Modus im Lemmata-Explorer | KZWs Spezifikation ist vollständig, inklusive Akzeptanzkriterien und benannter Fehltreffer-Quelle; frontend-only | M |
| (kein Rang) | **#44** | Triage-Matrix aktualisieren | Evergreen-Meta-Aufgabe am Session-Ende; **nie schließen**, nie mit `Closes` referenzieren | S |

### 1.1 Die drei #169-Befunde, am Code verifiziert (29.07.)

Die Zeilennummern im Issue sind veraltet: `tei-manager.js` ist seit dem Audit von 1.198 auf 1.158 Zeilen geschrumpft. Aktuelle Fundorte und Sachstand:

**Befund #15, Nähesuche misst nur zum Anker.** `playground/js/data/tei-manager.js:1043`:

```js
const nearbyPos = positions.find(pos => Math.abs(pos - firstPos) <= maxDistance);
```

Jedes weitere Lemma wird ausschließlich gegen `firstPos` geprüft. Bei „innerhalb 5 Wörter" passieren B bei Anker−5 und C bei Anker+5 beide, real liegen sie 10 auseinander. Die Ironie: `actualDistance = maxPos - minPos` einige Zeilen darunter rechnet die 10 korrekt aus und meldet sie im Ergebnis, der Filter hat sie aber schon durchgelassen. Der Fix ist eine paarweise Prüfung über alle Positionen. **Er verkleinert Treffermengen ab 3 Lemmata.** KZW hat das ausdrücklich in Kauf genommen und dazu gesagt: „bitte im Journal mit Datum festhalten, damit ältere Zahlen zuordenbar bleiben." Bei zwei Lemmata ändert sich nichts.

**Befund #51, hartkodiertes Fast-Path-Wörterbuch.** `playground/js/ui/tei/tei-ui.js:120-138`, aufgerufen in `resolveLemmaIds` (`:95`) **vor** der regulären Auflösung. Das Issue führt es als künftiges Risiko („bei künftigem Renumbering"). Das ist zu milde: **fünf der elf Einträge liefern schon heute das falsche Lemma.** Gemessen gegen `data/authority-index.json.gz`:

| Eingabe | Fast-Path liefert | reguläre Auflösung | Urteil |
|---|---|---|---|
| `brôt`, `brot` | lemma_879 `brôt` | lemma_879 `brôt` | ok |
| `wîn`, `win`, `wein` | lemma_7532 `wîn` | lemma_7532 `wîn` | ok |
| `fleisch`, `vleisch` | lemma_1816 **`forma`** | lemma_7121 `vleisch` | falsch |
| `käse`, `kæse` | lemma_26713 **`eierkæse`** | lemma_3175 `kæse` | falsch |
| `bier` | lemma_712 **`bir`** (Birne) | lemma_702 `bier` | falsch |
| `bîr` | lemma_712 `bir` | lemma_542 `bern` | beide fragwürdig |

Wer heute im Playground „fleisch" sucht, bekommt also *forma*, wer „bier" sucht, bekommt die Birne. Das ersatzlose Streichen ist damit nicht nur Hygiene, sondern ein Bugfix. Die fünf korrekten Einträge (`brôt`, `brot`, `wîn`, `win`, `wein`) verlieren nichts: die reguläre Auflösung findet sie über Stufe 1 bzw. Stufe 2 genauso. Das ist wichtig, weil `wein` zugleich das Leitbeispiel von #239 ist.

**Befund #48, Dedup behält den Falschen und lügt darüber.** `playground/js/data/tei-manager.js:1096-1112`. Sortiert wird nach `contextStart`, behalten wird der zuerst hinzugefügte nicht-überlappende Treffer. Der Kommentar darüber sagt „keep closest", und das Log gibt bei jeder Überlappung wörtlich aus: `keeping shorter distance (${existing.distance} vs ${result.distance})`. Beides ist unwahr: `existing` gewinnt allein, weil er früher startet. Dem Nutzer wird gegebenenfalls die weiter entfernte Kookkurrenz angezeigt.

### B. Nicht in dieser Session, mit Begründung

**#194 (Rubrik „Experimentelle Forschungsdaten") bleibt draußen.** Das Ticket sperrt sich unter „Timing" selbst: „Erst umsetzen, wenn das Arthurische-Pferde-Feature (#193) gebaut ist, bis dahin bleibt der Naming-Explorer, wo er ist." Es sieht nach einem leichten Einstieg aus und ist per Auftrag blockiert.

**#228 (TEI-Putzen Ziffern-Lemmata) ist halb-autonom und bleibt draußen.** Die Beleglage steht vollständig im Issue (fünf bedeutungslose Ziffern-Lemmata, 118 Belege, davon 92 in `<note n="…">`). Was fehlt, ist die kuratorische Entscheidung, was mit dem Sammeltopf `lemma_53328` geschieht, auf den in MR1 die Tokens 1 bis 15 annotiert sind. Das ist KZWs Ruf.

### C. Umgesetzt, warten auf Test-OK: Session fasst sie NICHT an (3)

#138-Frontend (Randnummern, KZW und Julia angepingt 29.07.), #114 (Linda seit 02.07.), #140 (Em-Dash-Gate, Health-Check und Emoji-Icons erledigt; KZW hat „für die Abnahme“ geschrieben, nicht „schließen“, deshalb offen).

### D. Blockiert auf Menschen: Session fasst sie NICHT an (17)

#198 (bei Julia), #59 (Linda gepingt), #115 (Kategorien B/C, kuratorisch), #189 (21 Review-Fälle), #138-Kern (`<div>`-Hüllen), #224 (Fix ist gemergt; offen ist nur noch Julias Breve-Frage für `w`/`n`/`y`/`z`), #228 (siehe oben), #235 (bei Julia), #236 (Frauenlob, `depends-on-human`), #242 (Sparkling Science), #28, #27, #68, #86, #63, #58, #172.

### E. Future / Trigger / extern (12)

#93, #106 (Rolling-Backlog), #109, #111, #118, #194 (siehe oben), #195, #216 (technisch entsperrt, Batch-Größe braucht KZW), #225 und #237 (Externenkontakt), #226 (Text in chsteiners Stimme), #18.

### F. Ingest: nicht Teil dieses Playbooks (7)

#92, #123, #139 (laut Memory gemeinsame Einzelsession, nie autonom), #141, #147, #191, #193.

**Fazit:** zwei Kern-PRs plus Meta-PR. Kleiner als die Session vom 28.07., dafür mit schriftlich vorliegenden Entscheidungen zu jedem Punkt.

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
15. **`git log origin/main..main` im Vorflug.** Lokales `main` kann einen unveröffentlichten Commit voraus sein; ohne Prüfung verwaist er.

---

## 3. Wellenplan

Die beiden Kern-Deliverables berühren teils dieselbe Datei (`playground/js/ui/tei/tei-ui.js` in Welle 1, der Lemmata-Explorer in Welle 2), liegen aber in verschiedenen Funktionen. Beide Branches starten frisch von `origin/main`; sollte es beim Merge haken, gilt die Reihenfolge 1 vor 2.

| Welle | Deliverable | Issues | Inhalt |
|-------|-------------|--------|--------|
| **0** | Chat-Report | - | Vorflug: `git log origin/main..main` (muss leer sein); `python scripts/audit/check-index-versions.py`; die drei Fundorte aus §1.1 aufsuchen und bestätigen, dass sie noch dort stehen (die Zeilennummern in diesem Playbook sind vom 29.07.); `testing/tests/` nach bestehenden Specs für Nähesuche und Lemmata-Explorer durchsehen und die Ausgangslage protokollieren. **Kein voller `npm test` als Hintergrund-Baseline.** |
| **1** | PR 1 | #169 | **Die drei freigegebenen Befunde.** (a) **Nähesuche paarweise:** in `findProximityMatchesInIndex` bzw. der Stelle um `tei-manager.js:1043` alle gewählten Positionen paarweise gegen `maxDistance` prüfen, nicht nur gegen `firstPos`. Vor dem Commit die Wirkung messen: dieselbe Beispielsuche mit 3 Lemmata alt gegen neu, Trefferzahl und ein konkreter Fall, der jetzt korrekt herausfällt. (b) **Fast-Path streichen:** `findLemmaIdByOrthography` und ihren Aufruf in `resolveLemmaIds` ersatzlos entfernen. Im PR-Text die Tabelle aus §1.1 zeigen: fünf der elf Einträge liefern heute das falsche Lemma, und die fünf korrekten verlieren nichts, weil Stufe 1 und 2 sie ohnehin finden. Gegenprobe für alle elf Eingaben nach dem Fix. (c) **Dedup:** entweder tatsächlich den distanzkürzesten Treffer behalten (dann Kommentar und Log stimmen) oder das Log ehrlich machen. **Empfehlung: distanzkürzesten behalten**, weil Kommentar, Log und #169 das seit jeher behaupten und der Nutzer es so erwartet; die Änderung im PR-Body als Verhaltensänderung benennen. Playwright: bestehende Playground-Specs müssen grün bleiben, neue Tests für (a) und (c). Ein Statuskommentar in #169 mit den gemessenen Auswirkungen. **JOURNAL-Eintrag mit Datum**, weil KZW ausdrücklich darum gebeten hat, damit ältere Trefferzahlen zuordenbar bleiben. |
| **2** | PR 2 | #239 (refs #169, #224) | **Wortbestandteil-Suche im Lemmata-Explorer.** Eigener, benannter Modus, klar getrennt von der normalen Lemmasuche. Sucht gegen die Lemmaliste, nicht gegen den Korpus; Ergebnis ist eine Lemma-Liste. Treffer nach Position gruppiert: am Wortende (Grundwort) zuerst und aufgeklappt, am Wortanfang als zweite Gruppe, in der Wortmitte als dritte, standardmäßig eingeklappte Gruppe. Gesucht wird auf der normalisierten Form, angezeigt wird die Originalform, und die UI sagt das. Mindestlänge 3 Zeichen. Ausgewählte Lemmata müssen gesammelt an die Multi-Lemma-Suche übergeben werden können. In der UI kurz benennen, dass `win` auch `winter`, `gewinnen`, `winden` trifft: das ist der Preis eines zeichenbasierten Verfahrens ohne Morphologie, die echte Lösung gehört zu #109. **Nicht in Scope:** keine Änderung an Stufe 1 bis 3 der normalen Auflösung (ADR-016 bleibt), kein Rückbau der Infix-Suche in die Haupt- oder Playground-Suche. Regressionstest, dass die normale Lemmasuche unverändert arbeitet. `hilfe-playground.html` um den Modus ergänzen, danach `python scripts/build-pages.py --check` und `python scripts/audit/doc-count-audit.py`. Chrome-Verifikation mit „wein" (muss `rôtwîn` in der Gruppe „am Wortende" zeigen) und mit „win" (muss `winter` in der eingeklappten Wortmitten-Gruppe zeigen). Alle fünf Akzeptanzkriterien aus dem Issue einzeln abhaken. |
| **3** | Meta-PR (von origin/main) + #44-Kommentar | #44, docs | #44-Matrix aktualisieren, ROADMAP.md und JOURNAL.md nachziehen, §7 dieses Playbooks befüllen und §1/§3/§5/§6 für die Folgesession leeren. Abschlussreport als #44-Kommentar: PR-Liste, empfohlene Merge-Reihenfolge samt Hinweis, laufende Review-Runs vor dem Merge zu canceln, Übersprungenes mit Grund, Wer-wartet-worauf-Liste. |

Erwarteter Output: 2 Code-PRs plus Meta-PR, kein Issue geschlossen (beide bleiben bis zur Abnahme offen), 2 bis 3 Issue-Kommentare.

---

## 4. Nicht anfassen

- **Review-Gate, Ping ist draußen:** #138-Frontend (29.07. an KZW und Julia), #114 (Linda seit 02.07.), #140 (Abnahme durch KZW).
- **Menschen-blockiert:** #198, #59, #115, #189, #138-Kern, #224, #228, #235, #236, #242, #28, #27, #68, #86, #63, #58, #172.
- **Future/Trigger/extern:** #93, #106, #109, #111, #118, #194 (per Issue-Text auf #193 blockiert), #195, #216, #225, #226, #237, #18.
- **Ingest:** #92, #123, #139, #141, #147, #191, #193.
- **Kein Merge nach `main`.**
- Alle Gruppen nur in der #44-Matrix korrekt einsortieren.

---

## 5. Getroffene Entscheidungen (chsteiner, 2026-07-29)

1. **Reihenfolge:** erst #169, dann #239. #194 fällt entgegen der ersten Empfehlung heraus, weil das Ticket sich unter „Timing" selbst auf #193 sperrt.
2. **Fast-Path (#51):** ersatzloses Streichen, nicht Korrigieren der falschen IDs. Ein hartkodiertes Wörterbuch vor der zentralen Auflösung ist auch mit richtigen IDs ein Fehler; die reguläre Auflösung liefert alle elf Eingaben korrekt.
3. **Dedup (#48):** tatsächlich den distanzkürzesten Treffer behalten, nicht bloß das Log an das falsche Verhalten anpassen. Kommentar, Log und Ticket behaupten es seit jeher, und es ist die Erwartung der Nutzer.
4. **Nähesuche (#15):** paarweise Prüfung, sinkende Trefferzahlen sind von KZW abgenommen. Pflicht ist der datierte JOURNAL-Eintrag, damit ältere Zahlen zuordenbar bleiben.
5. **#239 bleibt streng im Lemmata-Explorer.** Kein Rückbau der Infix-Suche in die normale Suche, ADR-016 unangetastet.
6. **Keine TEI-Datenänderung in dieser Session.** Beide Deliverables sind frontend-only; damit entfällt der Data-Change-Lifecycle und der Index-Versions-Bump.

---

## 6. Kickoff-Prompt (copy-paste in die neue Session)

```
Arbeite den Issue-Masterplan autonom ab (Detailfassung: docs/playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md, Stand 2026-07-29).
Betriebsvertrag:

AUTORISIERUNG: Ich genehmige hiermit ausdrücklich Commits + Pushes auf claude/*-Feature-Branches
und das Erstellen von Pull Requests (übersteuert die CLAUDE.md-Regel „never push without approval").
main bleibt absolut tabu (kein Merge, kein Push). Issues nie selbst schließen außer per Closes-Trailer
im PR-Body; #44 NIE mit Closes referenzieren. Pro Issue ein frischer Branch von origin/main, auch der
Meta-PR. Nie git add -A. Max. 1 Statuskommentar pro Issue, keine Kontaktaufnahme mit Externen.
Keine Emoji-Icons (Heroicons inline SVG), keine Em-Dashes in Prosa, echte Umlaute.
Jeden PR vor Abschluss zusätzlich vom fable-advisor reviewen lassen (er hat kein Bash: Diff in den
Scratchpad dumpen, Pfad mitgeben, sagen auf welchem Branch der Arbeitsbaum steht). Befunde nachmessen,
nicht glauben.

WICHTIG ZUR NOTATION: In #169 sind „#15", „#51" und „#48" BEFUND-Nummern innerhalb des Issue-Bodys,
keine Issue-Nummern. Nicht als Issues nachschlagen.

WELLE 0 (VORFLUG):
- git log origin/main..main (muss leer sein).
- python scripts/audit/check-index-versions.py.
- Die drei Fundorte aus §1.1 des Playbooks aufsuchen und bestätigen, dass sie noch dort stehen;
  die Zeilennummern im Playbook sind vom 29.07.
- testing/tests/ nach bestehenden Specs für Nähesuche und Lemmata-Explorer durchsehen.
- KEIN voller npm test als Hintergrund-Baseline (40+ min bei 1 Worker, testet den Zwischenstand).

WELLE 1 (PR): #169, die drei von KZW am 28.07. freigegebenen Befunde.
(a) Nähesuche paarweise prüfen statt nur gegen firstPos (tei-manager.js:1043). Wirkung vor dem
    Commit messen: dieselbe 3-Lemma-Suche alt gegen neu, plus ein konkreter Fall, der jetzt
    korrekt herausfällt. Sinkende Trefferzahlen sind abgenommen.
(b) Fast-Path-Wörterbuch ersatzlos streichen (tei-ui.js:120-138 + Aufruf :95). Im PR-Text zeigen,
    dass fünf der elf Einträge HEUTE falsch auflösen (fleisch/vleisch -> forma, käse/kæse ->
    eierkæse, bier -> bir/Birne) und die fünf korrekten nichts verlieren. Nach dem Fix alle elf
    Eingaben gegenprüfen.
(c) Dedup: den distanzkürzesten Treffer behalten (tei-manager.js:1096-1112). Kommentar und Log
    behaupten das seit jeher, der Code tut es nicht. Als Verhaltensänderung benennen.
- Playwright: bestehende Playground-Specs grün halten, neue Tests für (a) und (c).
- 1 Statuskommentar in #169 mit den gemessenen Auswirkungen.
- JOURNAL-Eintrag MIT DATUM: KZW hat ausdrücklich darum gebeten, damit ältere Trefferzahlen
  zuordenbar bleiben.

WELLE 2 (PR): #239 Wortbestandteil-Suche im Lemmata-Explorer.
- Eigener, benannter Modus, getrennt von der normalen Lemmasuche. Sucht gegen die Lemmaliste,
  Ergebnis ist eine Lemma-Liste.
- Treffer nach Position gruppiert: Wortende (Grundwort) zuerst aufgeklappt, Wortanfang zweite
  Gruppe, Wortmitte dritte und standardmäßig EINGEKLAPPT.
- Gesucht auf normalisierter Form, angezeigt in Originalform, und die UI sagt das. Mindestlänge 3.
- Ausgewählte Lemmata sammelbar an die Multi-Lemma-Suche übergeben.
- In der UI benennen, dass „win" auch winter/gewinnen/winden trifft (zeichenbasiert ohne
  Morphologie; echte Lösung gehört zu #109).
- NICHT IN SCOPE: keine Änderung an Stufe 1-3 der normalen Auflösung (ADR-016 bleibt), kein
  Rückbau der Infix-Suche in die Haupt- oder Playground-Suche.
- Regressionstest, dass die normale Lemmasuche unverändert arbeitet.
- hilfe-playground.html ergänzen, dann build-pages.py --check und doc-count-audit.py.
- Chrome-Verifikation: „wein" muss rôtwîn unter „am Wortende" zeigen, „win" muss winter in der
  eingeklappten Wortmitten-Gruppe zeigen. Alle fünf Akzeptanzkriterien aus #239 einzeln abhaken.

WELLE 3 (META): #44-Matrix aktualisieren, ROADMAP.md + JOURNAL.md nachziehen, §7 des Playbooks
befüllen und §1/§3/§5/§6 für die Folgesession leeren (Meta-PR, von origin/main). Abschlussreport
als #44-Kommentar: PR-Liste, empfohlene Merge-Reihenfolge (Review-Runs vor dem Merge canceln),
Übersprungenes mit Grund, Wer-wartet-worauf-Liste.

VERIFIKATIONS-HANDWERK (§2.1 des Playbooks, gilt durchgehend):
- Neue Prüfung? Mutation bauen und beweisen, dass sie rot wird. Ein grünes Gate ist kein Gate.
- Substring-Greps lügen (shrink-0 in flex-shrink-0). Auf Selektor/Wortgrenze ankern.
- Neuer Test? Prüfen, ob er OHNE die Änderung auch grün wäre.
- expect(await locator) wartet nichts ab. await expect(locator) ist richtig.
- Hintergrund-Logs behalten nur den Schwanz: testing/test-results/report.json auswerten.
- Auf CI warten heißt auf die EXISTENZ der Checks warten und head_sha gegenprüfen.
- git rebase --continue frisst #-Zeilen: git commit -C <original> --cleanup=verbatim.
- Git-Bash-/tmp ist nicht Windows-C:\tmp. Scratchpad-Pfad ausschreiben.

NICHT ANFASSEN: #138 #114 #140 (Review-Gate, Pings sind draußen) / #198 #59 #115 #189 #224
#228 #235 #236 #242 #28 #27 #68 #86 #63 #58 #172 (menschen-blockiert) / #93 #106 #109 #111 #118
#194 #195 #216 #225 #226 #237 #18 (future/extern) / #92 #123 #139 #141 #147 #191 #193 (Ingest).
#194 sieht nach leichtem Einstieg aus, sperrt sich aber im eigenen Ticket-Text auf #193.
Alle nur in der #44-Matrix einsortieren.

Jede Welle mit Verifikation. Unbeschaffbarer Input -> Item dokumentiert überspringen und
weiterarbeiten, NICHT auf mich warten und NICHT fragen.
```

---

## 7. Session-Ergebnis (Anhang, wird von der nächsten Session befüllt)

Leer. Die vorige Fassung (Session 2026-07-28, sechs Wellen, vier Code-PRs) ist in der Git-History und im JOURNAL-Eintrag vom 28.07. archiviert; ihre übertragbaren Lehren stehen jetzt in §2.1, ihre inhaltlichen Ergebnisse im JOURNAL.
