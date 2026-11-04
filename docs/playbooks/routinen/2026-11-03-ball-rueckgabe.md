Ergebnis des Laufs vom 2026-11-03 nach `docs/playbooks/BALL-RUECKGABE.md`, auf dem Stand von #44 aus dem Lauf `issue-matrix.yml` vom 2026-11-03T12:01:42Z: 15 von 15 Einträgen, 0 schon vorgelegt.

Herkunft der Zahlen in dieser Zeile: `gh api repos/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44 --jq .body` (Zeile `| **Ball bei uns (15)** |` zwischen den MATRIX-Markern, 15 Einträge zu 14 Tickets, #537 steht für Julia und für Katharina), `gh api "repos/DigitalHumanitiesCraft/mhdbdb-tei-only/actions/workflows/issue-matrix.yml/runs?per_page=1" --jq '.workflow_runs[0].created_at'` für das Datum. Schon vorgelegt sind 0, weil `docs/playbooks/routinen/` vor diesem Lauf nicht existierte. Offene PRs mit Kopf `claude/ball-rueckgabe-*`: keine (`gh api "repos/DigitalHumanitiesCraft/mhdbdb-tei-only/pulls?state=open" --jq '.[].head.ref'` gab eine leere Ausgabe).

Gelaufen ist das als lokaler Kickoff der Koordination im Nachtlauf, den chsteiner am 03.11.2026 freigegeben hat, nicht als Cloud-Routine. Geschrieben wurde nichts außer dieser Datei: kein Kommentar, kein Label, kein Ping. Nachtrag: die Label-Vorschläge für #58, #93, #358 und #417 hat die Koordination desselben Nachtlaufs am 03.11. gleich danach gesetzt. Gepostet ist keine der Fragen.

## Übersicht

| Ticket | Person | Klasse | ein Satz |
|---|---|---|---|
| #560 | Katharina | B | Katharina hat das Ticket an Julia weitergereicht, ohne zu antworten, und Julia ist nie mit einer eigenen Frage-Zeile gefragt worden. |
| #364 | Katharina | B | Die zurückgegebene Prüfseite stammt von Alan, nicht von Katharina, und lässt 35 der 66 Belege ohne Zuordnung auf ein vorhandenes Lemma. |
| #498 | Julia | B | Julias Abnahme ist halb: Die Links gehen kopiert, die Multi-Lemma-Suche nicht, und der Link selbst fehlt zur Diagnose. |
| #358 | Julia | B | Julias Teil ist abgenommen, der Rest (elf Werke ohne Dreißiger-Gliederung) hängt an einer Frage an Katharina, die nie in der Frage-Form gestellt wurde. |
| #58 | Julia | D | Julia hat abgenommen, offen ist nur noch Katharinas Frage zum Knopf "Gesamten Text öffnen". |
| #537 | Julia | A | Julias Textvorschlag für die Seite "Demnächst im Korpus" ist fertig formuliert und noch nicht eingebaut. |
| #554 | Julia | A | Julia wünscht, dass "Weniger anzeigen" zurück an den Kommentaranfang springt. |
| #93 | Julia | D | Julia hat abgenommen, offen ist nur Katharinas Logo-Frage vom 18.10. |
| #417 | Julia | B | Julia hat abgenommen und fragt Katharina, ob die lange Publikationsliste Filter braucht. |
| #453 | Katharina | A | Katharina hat die Scans zur Klärung von Lied 9 und Lied 29/30 geliefert, der Vergleich steht aus. |
| #486 | Katharina | A | Katharina hat FLG1 auf Buch 3 bis 7 richtiggestellt, im Bestand steht an zwei Stellen noch "Buch 1-7". |
| #259 | Katharina | A | Katharina hat die Mindestabdeckung 0,5 für Stufe 3 entschieden, mit Nachmessung vor der Umsetzung. |
| #495 | Katharina | A | Katharina hat Variante A entschieden (Frauendienst bekommt Minnesang und Brief) und fragt, wie der Fehler entstand. |
| #609 | Katharina | A | Katharina gibt fünf Arbeitsaufträge zum ONAMA-Explorer und fragt nach den Q-IDs, deren Antwort in ihrem eigenen Manifest steht. |
| #537 | Katharina | B | Katharina will #141 und #651 nennen, beide tragen `wait:extern` und blieben auf der Seite unsichtbar, und "die anderen" ist offen. |

Zusammen: A 7, B 6, C 0, D 2, Summe 15.

**Seit den Antworten geschehen** (je Ticket `git log origin/main --since=<Datum der Antwort> -E --grep="#N([^0-9]|$)"` nach `git fetch`, Stand `origin/main` = `5b67c4f00`): für 12 der 14 Tickets 0 Commits. Für #417 und #537 je 1 Commit, beide derselbe `247e21258` (Monatslauf vom 03.11., PR #663: Publikationen und "Demnächst im Korpus" nachgezogen, inhaltlich keine Antwort auf die Einträge hier).

## Zum Posten (B)

Hinweis aus `CLAUDE.md` ("Who is on turn"): Eine Frage wird nur dann oben auf unseren letzten Kommentar editiert, wenn der neuer ist als ihre Antwort. In allen sechs Fällen ist die Antwort der jüngste Kommentar im Thread, also jedes Mal als **neuer Kommentar** posten.

### #560 (Eintrag Katharina, Frage an Julia)

```
@juliahin Frage: Sind die einzelnen Buchstaben, die in der WZB direkt vor einem Wort mit demselben Anfangsbuchstaben stehen (etwa "• N Nu gepot", 294 Fälle), Hilfsbuchstaben für den Rubrikator, die nicht zum Text gehören?
```

Kontext darunter: Katharina hat am 16.10. geschrieben "Schau mal hier rein bitte @juliahin, weil es geht zu weiten Teilen um die WZB" ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/560#issuecomment-6213825265)). Eine Frage-Zeile an Julia gibt es im Thread nicht, deshalb steht das Ticket in keiner Personenliste. Von den sechs Fragen im Body betreffen drei die WZB: Frage 1 (294 Hilfsbuchstaben), Frage 2 (69 Buchstaben im Umfeld der Kolumnentitel, hängt mit #390 zusammen) und Frage 6 (192 ganze Wörter ohne Lemma, Liste in `ingest/wzb/370-corresp/abc-befunde.csv`). Die Zeile oben stellt die erste, die beiden anderen gehören als Liste darunter. Fragen 3 bis 5 (Sigel, Alphabet, Währungsabkürzungen in HZU2) bleiben bei Katharina.

Belege: Bestand unverändert seit dem Body vom 10.10.: 858 `<w>` mit `lexicon.xml#lemma_2` als ganzem Token in 42 Dateien, davon 624 in WZB (`git grep -c -E 'lemmaRef="([^"]* )?lexicon\.xml#lemma_2( [^"]*)?"' origin/main -- tei/`, Zeilen summiert). Die Gruppengröße 294 stammt aus dem Regellauf im Body und ist nicht nachgezählt. Labels stimmen schon (`wait:kzw`, `wait:julia`).

### #364 (Katharina)

```
@wachauer Frage: Dürfen wir die 31 Belege, die Alan auf der Prüfseite vom 23.09. einem vorhandenen Lemma zugeordnet hat, so umhängen, und entscheidest du die übrigen 35 Belege (neue Lemmata, offen gelassen oder nicht bearbeitet)?
```

Kontext darunter: Die Datei, die Katharina am 19.10. ohne Kommentar angehängt hat ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/364#issuecomment-6265336677)), trägt als Prüfer "Alan van Beek" (59 der 66 Entscheidungen, 7 ohne Namen). Ob Katharina sie damit übernimmt, sagt der Thread nicht, und das ist der Grund für B statt A. Aufteilung: 50 entschieden (31 auf ein vorhandenes Lemma in 23 Gruppen, 11 "other", 5 "new-name", 3 "keep-id"), 4 offen, 12 nicht bearbeitet. Vorgeschlagen werden neue Lemmata für `garwen` (6 Belege unter `gart`), `quintîn`, `atlas` als Stoff, "Sant Cyrren" und "Totes Meer". An einigen Stellen weicht Alan vom mechanischen Kandidaten aus dem Kommentar vom 06.09. ab: `sabîns` (Fluss statt `lemma_5044`, Burg/Stadt), `cignus` (Person statt `lemma_20325`, Fluss), `senes` (Latein).

Belege und Lesbarkeit: Anhang lesbar (HTTP 200, 37.687 Bytes, Schema `mhdbdb-review-364-v1`, `sourceCommit` `6e36a65`, `sourceDate` 2026-09-17). Der Quellcommit ist in diesem Klon nicht vorhanden (`git cat-file -t` schlägt fehl). Von den 40 Dateien mit Prüfsumme sind 39 seither geändert (SHA-256 gegen `git show origin/main:<pfad>`), wohl durch korpusweite Kopfänderungen wie `de2a95fb7` (#505). Entscheidend ist aber: alle 66 Belege stehen auf `origin/main` unverändert mit ihrem alten `@lemmaRef` da (66 gleich, 0 geändert, 0 fehlend, je `xml:id` per `git grep` nachgesehen), die 35 toten IDs sind weiterhin nicht in `lexicon.xml` definiert und stehen alle in `scripts/audit/lexicon-baseline.json`. Die Entscheidungen beziehen sich also auf den heutigen Stand. Messskripte lagen im Scratchpad dieser Sitzung.

### #498 (Julia)

```
@juliahin Frage: Kannst du den Link zur kombinierten Multi-Lemma-Suche, den Gemini Flash ausgegeben hat, hier einfügen und sagen, was nach dem Öffnen im Browser zu sehen war?
```

Kontext darunter: Julias Antwort vom 19.10. ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/498#issuecomment-6266574913)): mit Gemini Flash teilweise, direkt im Chat klickbar nichts, kopiert in den Browser alles außer der Multi-Lemma-Suche. Der Prüfschritt 5 vom 19.10. hatte für den Fehlerfall genau das erbeten ("welche KI, und was im Link stand"), die KI ist genannt, der Link nicht. Ohne ihn ist nicht zu unterscheiden, ob die KI die Vorlage verletzt (etwa Leerzeichen, Ziffern oder eine Schreibung außerhalb der Spalte "Häufigste Lemmata", siehe `assets/downloads/mhdbdb-begriffshilfe.md` Zeile 38) oder ob der Playground einen korrekt gebauten Link nicht öffnet. Dass Links im Chat nicht klickbar sind, liegt an der Oberfläche von Gemini und nicht an der Datei. Labels: `wait:kzw` kann weg, Katharina hat die Begriffshilfe am 06.10. abgenommen und die Wiedereröffnung gilt nur dieser Abnahme.

### #358 (Eintrag Julia, Frage an Katharina)

```
@wachauer Frage: Sind die Seitenumbrüche in DIO (210 von 212 Einheiten mit 45 Versen, aus Julias Linecode-Seitenangaben) und FB (63 von 67 Einheiten mit 32 Versen) echte Seiten einer Handschrift oder Ausgabe, sodass sie als <pb> stehen bleiben?
```

Kontext darunter: Julia hat die Leseansicht für PZ und WH abgenommen ([15.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/358#issuecomment-6194867113), [19.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/358#issuecomment-6266594023)). Offen bleibt der Teil, für den das Ticket nach dem Abnahme-Kommentar vom 09.10. offen bleiben sollte: die übrigen Werke ohne Dreißiger-Gliederung. Die Fragen dazu stehen seit dem [09.08.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/358#issuecomment-5232962986) im Thread (drei Punkte: DIO und FB, WUT, RUD/WLE/FP), aber ohne `@wachauer Frage:`-Zeile, und Katharinas Antwort vom 11.09. betraf nur die Benennung im Parzival. Der [Kommentar vom 06.09.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/358#issuecomment-5561224959) zählt elf offene Werke (WUT, WRB, MR1, DIO, MR2, NAR, FB, RUD, SUB, WLE, FP). Die Zeile oben stellt den einfachsten Fall, der Rest als Liste darunter. Ebenfalls offen und im Thread am 04.10. genannt: die KWL-Bandangabe (Alan, 11.09.) und der Deep-Link `?textId=KWL` auf die Startseite (nicht nachgeprüft).

Labels: `wait:julia` entfernen, `wait:kzw` setzen (beim Lauf trug das Ticket nur `wait:julia`, ohne das wäre `auto:blocked` ohne `wait:*` ein harter Fehler im Tageslauf). `area:data`, `effort:medium` bleiben.

### #417 (Eintrag Julia, Frage an Katharina)

```
@wachauer Frage: Soll die Seite "Publikationen" (heute 294 Einträge) Filter bekommen, oder genügt ein gut sichtbarer Link auf die Zotero-Bibliothek, wie Julia am 19.10. vorschlägt?
```

Kontext darunter: Julia hat die Seite abgenommen ("die links stimmen (stichprobenartig) und die Anzeige sieht toll aus") und Katharina direkt gefragt ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/417#issuecomment-6266928500)). Diese Frage hat keine Frage-Zeile und taucht deshalb in Katharinas Liste nicht auf. Heute verlinkt die Seite die Zotero-Bibliothek nur in der Fußzeile des Listenbereichs (`hilfe-publikationen.html` Zeile 450 auf `origin/main`). 294 = 88 eigene plus 206 erwähnende Publikationen (`data/zotero-publikationen.json` auf `origin/main`, Stand 03.11.). Labels: `wait:julia` entfernen, `wait:kzw` bleibt.

### #537 (Katharina)

```
@wachauer Frage: Sollen #141 (Borte) und #651 (Greisenklage) schon auf "Demnächst im Korpus" stehen, obwohl bei beiden die Freigabe Dritter noch aussteht, und welche Texte meinst du mit "ohne Q die anderen"?
```

Kontext darunter: Katharinas Antwort vom 21.10. ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/537#issuecomment-6322268588)): #139 zuerst für 4. Q. 2026 bis 1. Q. 2027 (mit Bitte um Bestätigung durch Christian), dann #147, #651, #141 je für 1. Q. 2027, dann ohne Quartal die anderen. Am 08.10. hatte sie festgelegt, Texte mit offener Rechtefrage erst nach Freigabe zu nennen. #141 und #651 tragen `wait:extern` (`data/demnaechst-issues.json` auf `origin/main`, abgerufen 03.11.). #651 nennt im Body als offen "Herkunft und Freigabe je Transkription". `scripts/build-demnaechst.py` (Zeilen 21 bis 22 und 174) schließt `wait:extern` auch dann aus, wenn das Issue unter `freigegeben` steht. Ohne Klärung würden die beiden also trotz Eintrag nicht erscheinen.

Was unabhängig von der Antwort geht: #147 ist frei (Lizenz CC BY-NC-SA 4.0 schriftlich von Silvan, Body von #147, Stand 23.10., Label `wait:kzw` ohne `wait:extern`) und kann mit `2027-Q1` unter `freigegeben` in `data/demnaechst-zeitplan.json`. #139 braucht Christians Bestätigung des Quartals. Dazu steht im Zeitplan für #139 noch der Grund "Lizenz von CoReMA laut Body noch zu klären". Die Auto-Memory dieses Projekts hält eine Aussage von Christian vom 21.08. fest, CoReMA sei durchgehend Open Source. Das ist hier nicht am Thread geprüft.

## Zum Schließen oder Umlabeln (D)

### #58 (Julia)

Julia: "Ja, das funktioniert perfekt." ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/58#issuecomment-6266653672)), auf die Abnahme-Zeile vom 18.10. Die Abnahmen vom 13.10. (Aufklappen, a + c) und vom 18.10. vormittags (Scrollen) hat sie am 16.10. und mit derselben Antwort mit abgedeckt. Offen ist nur die zweite Zeile des Kommentars vom 18.10.: `@wachauer Frage: Soll der Knopf "Gesamten Text öffnen" im Kopf der Trefferkarte bleiben, oder lieber in eine eigene Zeile darunter?` ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/58#issuecomment-6253011809)), seither ohne Antwort von Katharina.

Vorgeschlagene Labels: `wait:julia` entfernen. Bleiben: `auto:blocked`, `wait:kzw`, `area:playground`, `effort:medium`. Schließen erst nach Katharinas Antwort auf die Knopf-Frage.

### #93 (Julia)

Julia: "Nein das alte ist weg. Sieht alles gut aus - danke!" ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/93#issuecomment-6266856856)), auf die Abnahme-Zeile vom 18.10. (neues PLUS-Logo). Die Abnahme der Unterseite vom 13.10. hat sie am 15. und 16.10. erledigt. Offen ist nur `@wachauer Frage: Soll das MHDBDB-Logo im Seitenfuß ... ebenfalls durch eine der neuen Varianten ... ersetzt werden?` ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/93#issuecomment-6250354964)), ohne Antwort.

Vorgeschlagene Labels: `wait:julia` entfernen. Bleiben: `auto:blocked`, `wait:kzw`, `area:frontend`, `effort:large`. Nach der Logo-Antwort ist kein weiterer Punkt im Thread offen, dann kann das Ticket geschlossen werden, sofern Katharina nichts nachfordert.

## Auftrag für eine autonome Session (A)

**Nachtrag aus demselben Nachtlauf:** A1 (#537), A2 (#554) und A3 (#495) setzt der Nachtlauf vom 03./04.11. selbst um, je als eigener PR. Vor dem Abschicken streichen, was bis dahin gemergt ist.

Entwurf nach `docs/playbooks/KICKOFF-VORLAGE.md`. Wer ihn abschickt, fügt den Betriebsvertrag (`docs/playbooks/BETRIEBSVERTRAG.md`) vollständig an der markierten Stelle ein und legt den Wortlaut unter `docs/playbooks/kickoffs/` ab.

### 1. Autorisierung

Issue-Session: Commits und Pushes auf `claude/*`-Branches, PRs erstellen. `main` bleibt tabu. Die Freigabe gilt für die sieben Arbeitspakete unten und nur für sie.

### 2. Betriebsvertrag

[Hier den vollständigen Inhalt von `docs/playbooks/BETRIEBSVERTRAG.md` einfügen.]

### 3. Umfang

Sieben Arbeitspakete, je eines pro Ticket, voneinander unabhängig. Reihenfolge nach Aufwand: A1 bis A3 klein, A4 bis A7 größer.

**A1, #537 (Julia), `effort:small`, Frontend.** Julias Textvorschlag vom 19.10. ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/537#issuecomment-6266754238)) einbauen. Einleitung in `hilfe-demnaechst.html` (Absatz unter der h1, heute Zeilen 136 bis 140): "Hier ist eine Übersicht der Texte, die voraussichtlich als Nächstes in das Korpus aufgenommen werden. Da externe Faktoren und Kooperationen den Zeitplan beeinflussen können, listen wir Vorhaben erst auf, sobald die Aufnahme verbindlich feststeht." Die generierten Sätze im Bereich `DEMNAECHST` kommen aus `scripts/build-demnaechst.py`: Hinweis "Alle Zeitangaben sind Richtwerte und können sich im Projektverlauf verschieben.", Leersatz "Aktuell stehen keine neuen Aufnahmen fest. Sobald konkrete Erweiterungen terminiert sind, werden sie hier veröffentlicht." Der Leersatz gilt nur für den Leerzustand. Selbsttest im Skript, `testing/tests/hilfe-unterseiten.spec.js` und `python scripts/build-pages.py --check` mitziehen. Danach `@juliahin Abnahme:` mit Live-URL. Nicht Teil davon: die Quartale aus Katharinas Antwort (B oben).

**A2, #554 (Julia), `effort:small`, Frontend.** Beim Zuklappen eines langen Kommentars ("Weniger anzeigen") zurück an den Kommentaranfang scrollen, wenn dieser oberhalb des sichtbaren Bereichs liegt ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/554#issuecomment-6266802318)). Eine Stelle: `umschalten()` in `assets/js/lib/collapsible-text.js`, gilt für Lemmaseite und Playground-Lemma-Explorer zugleich. Test in `testing/tests/comment-collapse.spec.js`. Danach `@juliahin Abnahme:`. Julias zweite offene Abnahme vom 18.10. (neue Zahlen in sieben Kommentaren) hat sie nicht beantwortet, sie bleibt stehen. Die Fragen an Katharina vom 18.10. (vier `trûbe`-Belege, Zählregel) ebenso.

**A3, #495 (Katharina), `effort:small`, Daten.** Katharina hat A gewählt ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/495#issuecomment-6296893356)): `work_6` (Frauendienst) in `authority-files/works.xml` bekommt zu `genre_88b5cae2` die Gattungen Minnesang (`genre_4ecfe25e`) und Brief (`genre_e513a99c`). Die Ausnahme für FD, FDS, FH, FLD, FP in `scripts/audit/check-header-genres.py` (`AUSNAHMEN`, Zeile 62) fällt weg. Voller Data-Change-Lifecycle aus `docs/DATA-MODEL.md` (Authority-Index, API, Versionssprung an den fünf Stellen, `check-index-versions.py`). Katharinas Rückfrage "wie der Fehler ... überhaupt entstehen konnte" im Statuskommentar beantworten, aus den Quellen: für FB und FBS steht im [Kommentar vom 01.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/495#issuecomment-5928781583) die Vermutung eines Kopierfehlers beim Frauendienst-Split (Authority-Index 1.2.0), für die fünf Frauendienst-Köpfe ist die Herkunft der `classDecl` (Ursprungstransformation, `tei-transformation.py`) erst am Git-Verlauf zu belegen, bevor sie behauptet wird.

**A4, #486 (Katharina), `effort:small`, Daten.** Katharinas Klarstellung vom 20.10. ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/486#issuecomment-6296624302)): FLG ist Buch 1 bis 2, FLG1 Buch 3 bis 7. Der Werktitel von FLG1 bleibt. Zu berichtigen ist "Buch 1-7": `authority-files/works.xml` Zeile 1970 (`analytic/title` von FLG1, "Das Fließende Licht der Gottheit: Text: Buch 1-7", kommt aus dem Zotero-Titel von `ATWPNQPS`) und die Kopie in `tei/FLG1.tei.xml` Zeile 61. Weil FLG und FLG1 sich `ATWPNQPS` teilen, braucht FLG1 wie FLG einen Eintrag für `analytic` in `BESTAND_BEHALTEN` (`scripts/sync/enhance_works_with_zotero.py`, Kommentar Zeilen 95 bis 99 sagt heute das Gegenteil). Ebenso `docs/CONTRACTS.md` Zeile 935 ("Books 1 to 2 against Books 1 to 7", "FLG1 needs no exception") und den Nebenbefund in `docs/JOURNAL.md` Zeile 70 schließen. Prüfen, ob die Notiz von FLG Bd. II (Untersuchungen, 1993) und Harsch 2009 als digitale Vorlage trägt, wie Katharina sie aufzählt. Die Harsch-Adresse kam abgeschnitten an ("mec_vorb."), erst prüfen, dann übernehmen. Header über `sync_tei_headers.py --works`, Gate `--works --check`, Lifecycle mit Authority-Index-Bump.

**A5, #453 (Katharina), `effort:small`, nur Abgleich und Kommentar, kein Commit.** Katharina hat am 20.10. Scans geliefert ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/453#issuecomment-6285664414)). Anhang lesbar (HTTP 200, 3.510.239 Bytes, drei PDFs: "Scan Neidhart 2", "Scan Neidhart C", "Scan Titel"). Damit Lied 9 (Konkordanz C 117 bis 131, 15 Strophen, NEIM 13) und Lied 29/30 (C 245 bis 248 und 249 bis 254, 10 Strophen, NEIM 11) strophenweise gegen `tei/NEIM.tei.xml` abgleichen. Die Scans sind fremdes Material (Edition): nicht ins Repo. Ergebnis und Seitenangabe gehören nur in den Kommentar. An Text und Header von NEIM nichts ändern: Katharina hat die Bereiche C 117 bis 131 und C 245 bis 254 am 08.10. aus der großen SNE-Konkordanz bestätigt (S. 403, 405, 410), und unser Kommentar vom 07.10. hat zugesagt, Text und Header bis zu ihrer Antwort unverändert zu lassen. Ihre Antwort vom 20.10. ist nur das Scan-Zip. Jedes Ergebnis des Abgleichs geht deshalb mit Seitenangabe als `@wachauer Frage:` an sie.

**A6, #259 (Katharina), `effort:medium`, Code.** Katharina hat Mindestabdeckung 0,5 entschieden ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/259#issuecomment-6296756241)), mit drei Auflagen: zuerst `scripts/audit/compare-findebuch-resolution-259.py` auf die Logik seit #463 bringen (`stage1Holds`, braucht `lemmaIndex` aus dem Korpus-Index, siehe [Kommentar vom 10.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/259#issuecomment-6096700726)) und die Wirkung am heutigen Stand neu messen. Bekannte Schreibvarianten und ausdrückliche Zeichenjoker bleiben uneingeschränkt, die Richtung "Stamm kürzer als Lemma" bleibt unberührt. Zeigt die Neumessung deutlich andere Nachteile als 217 Fehltreffer weg und 1 richtiger verloren, nicht umsetzen, sondern mit Beispielen als `@wachauer Frage:` vorlegen. Sonst Schwelle in `assets/js/lib/lemma-resolve.js` (Hauptseite und Playground), `docs/CONTRACTS.md` §C, Tests, gegebenenfalls Python-Gegenstück nach CONTRACTS. Der Findebuch-Dump liegt lokal unter `~/.cache/mhdbdb/woerterbuchnetz2015/FindeB/P5` (laut `sources/INVENTAR-ARCHIV.md` Zeile 277, Ordner am 03.11. vorhanden). Lizenzauflage: keine Trierer Schreibform in Repo, PR oder Kommentar, nur Zahlen über unsere Daten.

**A7, #609 (Katharina), `effort:large`, Playground.** Katharinas Rückmeldung vom 20.10. ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/609#issuecomment-6297056545)), Punkt für Punkt: (1) Hinweiskasten "Selektiver Bestand" und Hilfeabschnitt `hilfe-playground.html#onama-narrativ-explorer` für Menschen neu schreiben, kürzer und lesbar. (2) Zugang über Dinge bleibt. (3) Belege selbst zeigen: die Textzitate der Passagen aus dem MHDBDB-TEI ins Paket. (4) REALonline-Bilder als kleine Thumbnails, verlinkt auf den Datensatz bei REALonline. Vorher klären, ob die Bilder eingebettet oder kopiert werden dürfen: das Manifest trennt fremde Bilder ausdrücklich von der Datenfreigabe (Abschnitt 11). Ist das nicht aus den Quellen zu klären, bei IMAREAL (`@PeterF-PLUS`, der um einen Ping bei IMAREAL-Themen gebeten hat) fragen und bis dahin nur verlinken. (5) "Projektleitung" durch "Katharina Zeppezauer-Wachauer" ersetzen, im Explorer, in der Hilfe und in `meta.lizenz`. Katharinas Frage nach den Q-IDs im Statuskommentar beantworten: ONAMA-Q-IDs sind eigene Kennungen, keine Wikidata-IDs. So steht es in ihrem eigenen [Manifest](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/609#issuecomment-6210671590) (Abschnitt 7, dazu Abschnitt 5: Datenerfassung in einer eigenen Wikibase-Instanz). Dass die Q-Nummern die Item-Kennungen dieser Wikibase sind, ist eine Folgerung daraus und vor dem Kommentar am RDF (`onamaObjects.ttl`) zu prüfen. Ob die Oberfläche statt der Q-Kurzform die volle Quell-URI zeigt, ist nicht entschieden: am 18.10. stand es unter "Nicht umgesetzt, bei dir zur Entscheidung", und Katharina hat am 20.10. nicht gewählt, sondern zurückgefragt. Nach der Erklärung im Statuskommentar diese Wahl als `@wachauer Frage:` stellen, nicht umsetzen. Keine Änderung in `tei/` oder `authority-files/`. Die Frage an `@PeterF-PLUS` vom 18.10. zum Exportformat ist unbeantwortet und bleibt stehen.

### 4. Weichen

- `npm test` braucht keine Freigabe. Volle Suite vor jedem Push von A1, A2, A6, A7.
- Je Arbeitspaket ein eigener Branch und ein eigener PR, außer A5: das endet in einem Kommentar mit `@wachauer Frage:`, ohne Branch.
- Nach dem Merge: einfache Abnahmen (A1, A2, A7-Oberfläche) zuerst `@juliahin Abnahme:`, Katharina darunter mitnennen. A3, A4 und A6 gehen an Katharina allein.

### 5. Nicht anfassen

- Die B- und D-Einträge oben: #560, #364, #498, #358, #417, #537 (Quartale), #58, #93. Die B-Einträge warten darauf, dass Christian die Frage postet. Die Labels für #58, #93, #358 und #417 sind seit dem 03.11. gesetzt, #498 trägt weiter `wait:kzw` und `wait:julia`.
- In #554 die übrigen offenen Punkte (`trûbe`-Belege, Zählregel, Zotero-Untergruppe, Klug-Verweise).
- In #609 keine Disambiguierung aus ONAMA ins Lexikon oder ins Korpus, auch wenn ein Textzitat es nahelegt (Manifest Abschnitt 10).
- **Falle in A4:** "Buch 1-7" steht auch in Zotero (`ATWPNQPS`). Zotero nicht ändern, ohne dass der Kickoff es erlaubt: Katharinas Freigabe vom 16.10. galt zwei bestimmten Einträgen, nicht einem weiteren Titelfeld.
- **Falle in A6:** Die Zahlen 217 und 1 stammen aus der Messung vor #463 und gelten nicht mehr ungeprüft.

### 6. Vorab getroffene Entscheidungen

- A1: Julias Wortlaut wird übernommen, wie er dasteht. Er ist eine Abnahme-Rückmeldung zur eigenen Seite, und Katharina hat an Ton und Inhalt der Seite nichts festgelegt, was er ändert.
- A4: Der Textumfang ist keine Editionsangabe und gehört deshalb nach `BESTAND_BEHALTEN`, nicht nach Zotero (Regel "Editionsangaben kommen weiterhin aus Zotero", Katharina 12./13.10.).

### 7. Notationsfallen

- In #453 sind "C 117" usw. Strophennummern der Handschrift C, keine Issue-Nummern.
- In #609 sind Q1190, Q1309 usw. ONAMA-Kennungen, keine Wikidata-IDs.

### 8. Abschluss

"Unbeschaffbarer Input führt zum dokumentierten Überspringen, nicht zum Warten und nicht zum Nachfragen."

## Belege je Eintrag

Thread je Ticket vollständig gelesen mit `gh issue view N --repo DigitalHumanitiesCraft/mhdbdb-tei-only --json title,body,comments`. Die Antwort-Links sind die aus #44.

| Ticket | Person | Antwort | Kommentare im Thread | Commits seit der Antwort |
|---|---|---|--:|--:|
| #560 | Katharina | [16.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/560#issuecomment-6213825265) | 1 | 0 |
| #364 | Katharina | [19.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/364#issuecomment-6265336677) | 4 | 0 |
| #498 | Julia | [19.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/498#issuecomment-6266574913) | 11 | 0 |
| #358 | Julia | [19.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/358#issuecomment-6266594023) | 13 | 0 |
| #58 | Julia | [19.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/58#issuecomment-6266653672) | 15 | 0 |
| #537 | Julia | [19.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/537#issuecomment-6266754238) | 7 | 1 (`247e21258`) |
| #554 | Julia | [19.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/554#issuecomment-6266802318) | 20 | 0 |
| #93 | Julia | [19.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/93#issuecomment-6266856856) | 15 | 0 |
| #417 | Julia | [19.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/417#issuecomment-6266928500) | 9 | 1 (`247e21258`) |
| #453 | Katharina | [20.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/453#issuecomment-6285664414) | 6 | 0 |
| #486 | Katharina | [20.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/486#issuecomment-6296624302) | 11 | 0 |
| #259 | Katharina | [20.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/259#issuecomment-6296756241) | 9 | 0 |
| #495 | Katharina | [20.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/495#issuecomment-6296893356) | 3 | 0 |
| #609 | Katharina | [20.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/609#issuecomment-6297056545) | 4 | 0 |
| #537 | Katharina | [21.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/537#issuecomment-6322268588) | 7 | 1 (`247e21258`) |

Die Kommentarzahlen stammen aus demselben `gh issue view`-Abruf am 03.11., die Commit-Zahlen aus dem `git log`-Befehl oben. Zeilennummern in Dateien beziehen sich auf `origin/main` = `5b67c4f00`.
