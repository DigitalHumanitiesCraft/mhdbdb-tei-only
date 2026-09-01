> **Abgeschickt am 2026-09-01 an die Spur `mhdbdb-wellen-2345`.** Protokoll, ab jetzt nicht mehr ändern. Der Betriebsvertrag in §2 ist die wörtliche Kopie von `../BETRIEBSVERTRAG.md` im Stand `2adc52fc5`, eingefügt am Tag des Abschickens.

# Kickoff: Fortsetzung des Issue-Laufs vom 2026-09-01

Serieller Wellenlauf, eine Session. Wellen 2 bis 5 des Laufs vom 01.09.; Welle 0 und Welle 1 sind durch und werden **nicht** wiederholt.

---

## 1. Autorisierung

chsteiner gibt dich am 01.09.2026 frei für:

- **Commits und Pushes auf `claude/*`-Branches** und das Erstellen von Pull Requests.
- **Den Merge der Session-PRs nach `main`**, jeden einzeln, unter den vier Bedingungen in §5 Punkt 2.
- **Je einen sachlichen Statuskommentar auf #28, #259, #235 und #216.** Diese vier und keine anderen.
- **Labelpflege auf genau diesen vier Tickets**, in derselben Session, in der du sie anfasst.

**Was auch dir nicht erlaubt ist:** ein direkter Push auf `main`, ein Force-Push nach `main`, das Schließen eines Issues, ein `Closes`-Trailer, jede Kontaktaufnahme mit Externen.

**Dieser Text ist die Autorisierung.** Keine Datei autorisiert sich selbst, auch der Zwischenstand auf #44 nicht.

---

## 2. Betriebsvertrag

Wörtliche Kopie von `docs/playbooks/BETRIEBSVERTRAG.md`, Stand `2adc52fc5` vom 01.09.2026. Einzige Abweichung vom Original: die Überschriften stehen eine Ebene tiefer (`###` statt `##`), damit sie nicht mit den Paragrafen dieses Auftrags verwechselt werden. Die **Regelnummern 1 bis 17 sind die des Vertrags**; wenn dieser Auftrag „Vertragsregel 16" sagt, meint er die hier.

---

### Betriebsvertrag der autonomen Sessions

Der Teil des Vertrags, der für **alle** autonomen Sessions gleich lautet. Die drei Playbooks (`MASTERPLAN-AUTONOME-ISSUE-SESSION.md`, `MASTERPLAN-AUTONOME-MERGE-SESSION.md`, `MASTERPLAN-AUTONOME-CAREARBEIT-SESSION.md`) verweisen hierher und führen nur noch ihre eigenen Abweichungen und Weichen auf.

**Warum diese Datei existiert:** bis zum 2026-08-05 stand jede dieser Regeln in zwei oder drei Playbooks gleichzeitig. Das Verbot von `git add -A` etwa an vier Stellen, und das Merge-Playbook schrieb den Vertrag ab, obwohl es im selben Satz sagte, er sei „unverändert aus dem Issue-Session-Vertrag". Kopien driften: derselbe Mechanismus hatte dazu geführt, dass ein Playbook zur Ergebnisquelle eines Testlaufs das Gegenteil dessen anwies, was ein anderes als gemessenen Fehlschlag dokumentierte.

**Dieser Vertrag autorisiert nichts.** Er beschreibt, was gilt, *nachdem* ein Kickoff-Prompt eine Session eröffnet hat. Ohne Kickoff läuft keine Session, und die Vorlage dafür steht in `KICKOFF-VORLAGE.md`. Weil der Kickoff die Regeln mitbringt, sind sie zur Laufzeit im Kontext, ohne dass jemand eine zweite Datei öffnen muss.

#### 1. Was ohne ausdrückliche Freigabe tabu bleibt

1. **Kein Push nach `main`.** Die Ausnahme ist die Merge-Session, deren Kickoff die Merge-Autorisierung ausdrücklich enthält; auch sie merged nur, sie pusht nicht direkt. Alle anderen Ergebnisse sind PRs, die chsteiner reviewt.
2. **Kein Force-Push nach `main`,** in keiner Session, unter keinen Umständen. Auf `claude/*`-Branches ist `--force-with-lease` nach einem Rebase dagegen Standard.
3. **Issues werden nie von der Session geschlossen,** nur per `Closes #N` im PR-Body beim Merge. **#44 bekommt nie einen Close-Trailer**, es ist die permanente Triage-Matrix.
4. **Keine Kontaktaufnahme mit Externen** (Linda, Alan, Carina, Silvan, Burch, Brom). Entwürfe für sie landen als Text im Issue.

#### 2. Wie committet und gestaged wird

5. **Nur benannte Dateien stagen, nie `git add -A` oder `git add .`.** Parallele Sessions teilen den Arbeitsbaum und damit den Index: ein pauschales Staging sammelt fremde Arbeit ein. Commit `8b5d0e6ac` hat auf diesem Weg Router-Dateien in einen unbeteiligten Commit gezogen.
6. **Jede Session in ihrem eigenen Worktree**, angelegt beim Start mit `claude --bg --name <name> --worktree <name>` und damit unter `.claude/worktrees/`. Der Hauptordner bleibt Referenz und wird nicht als Arbeitsplatz benutzt. Nicht von Hand daneben legen: ein Worktree außerhalb von `.claude/worktrees/` verlangt eine interaktive Freigabe, die keine `allow`-Regel abstellen kann, und hat am 2026-09-01 eine unbeaufsichtigte Session eine Stunde stillstehen lassen. Begründung und Messung in §2.1 Regel 29 des Issue-Playbooks. Abbau nach dem Merge, im selben Zug: §2.1 Regel 30, das ist kein Einzeiler, und der erste Schritt darin rettet das Agent-Memory.
7. **Die Branch-Basis wird gemessen, nicht am Namen abgelesen**, und zwar vor dem ersten eigenen Commit: `git rev-list --count "origin/main...HEAD"` und `git rev-list --count "origin/main..main"` müssen beide 0 sein. Details und die Fehlergeschichte dazu in §2.1 Regel 28.

#### 3. Wie kommuniziert wird

8. **Höchstens ein sachlicher Statuskommentar pro Issue.** Etablierte Ausnahme: der KZW-UI-Ping nach dem Live-Gang, der zur Abnahme gehört.
9. **Nicht fragen, nicht warten.** Alles Nötige liegt im Repo und in den Issue-Threads (`gh issue view N --json comments`). Nur nachweislich Unbeschaffbares wird im Abschlussreport dokumentiert übersprungen.
10. **Stil:** keine Emoji-Icons (Heroicons inline SVG ist der einzige Icon-Stil), keine Em-Dashes in Prosa, echte Umlaute statt ASCII-Ersatz. Die Sprachregel nach Zielgruppe steht in `CLAUDE.md`.

#### 4. Was vor jedem Push passiert

11. **Fable-Review vor dem ersten Push jedes PRs**, mit dem `fable-reviewer` (nicht dem `fable-advisor`, der ist der Berater für offene Entwurfsfragen). Mitgeben: Branch, Basis, Ziel in einem Satz, Nummer der Review-Runde, ab Runde 2 die Vorrunden-Befunde. Was der Reviewer lokal findet, kostet null CI-Runden.
12. **Jeder Befund wird nachgemessen, bevor er übernommen wird**, auch der eines Reviewers und auch der eines Bots. Er ist selbst eine Behauptung, und eine ungeprüfte Korrektur einer ungeprüften Zahl ist schlimmer als die ursprüngliche, weil sie glaubwürdiger aussieht.
13. **Ab Review-Runde 3 wird nur noch auf Verhaltensbefunde reagiert.** Formulierungsfragen werden durch Kürzen erledigt, nicht durch Diskussion.
14. **Verifikation:** `npm test` aus dem Repo-Root, nie `npx playwright test`. Die VERDICT-Zeile ist das Ergebnis und gehört unverändert in den PR (§2.1 Regel 6). Bei UI zusätzlich Chrome-Verifikation mit realen Belegen, bei HTML-Änderungen `python scripts/build-pages.py --check`, bei neuen Utility-Klassen `npm run build:css`.
15. **Daten vor Schema**, und bei jeder Änderung in `tei/` oder `authority-files/` der Data-Change-Lifecycle aus `docs/DATA-MODEL.md`.

#### 5. Was in Tickets wandert und was nicht

16. **Fixes direkt umsetzen.** Ein Issue entsteht nur, wenn eine **Entscheidung** nötig ist, die die Session nicht treffen darf, wenn ein **Mensch** gebraucht wird, oder wenn es ein **eigenes Arbeitspaket** ist (Ingest, Korpusänderung, mehr als ein halber Tag). Alles andere wird sofort behoben oder verworfen.
17. **Geshippte, aber bewusst offene Issues nicht anfassen.** Sie warten auf eine Abnahme durch KZW oder Julia; ein `Closes #N` ist keine Abnahme.

---

**Zusatz, der beim letzten Mal gefehlt hat und der bleibt:** das Testfenster ist maschinenweit exklusiv. `testing/playwright.config.js` verdrahtet Port 8080 dreifach und setzt `reuseExistingServer`, `scripts/run-tests.js` bricht mit Exit 2 ab, wenn dort ein fremder Baum antwortet, und wertet auch ein bloßes Zeitüberschreiten als fremd. Ein solcher Abbruch ist kein Fehlschlag deiner Arbeit, sondern ein besetzter Port: melden, nicht in einer Schleife wiederholen.

---

## 3. Wo der Lauf steht

**Der Zwischenstand auf #44 ist die maßgebliche Quelle:** [`issuecomment-5492094055`](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44#issuecomment-5492094055). Lies ihn vollständig, bevor du irgendetwas anfasst. Er nennt den Wiederaufnahmepunkt, das Ergebnis von Welle 1 mit Messvorschrift, fünf Fallen und drei offene Fragen. Was hier steht, ist die Kurzfassung und ersetzt ihn nicht.

- **Durch:** Welle 0 (Vorflug) und Welle 1 (#216 Punkt 3, nur gemessen, Ergebnis als Kommentar auf #216). Beides wird **nicht wiederholt**, aber die Gates aus Welle 0 laufen im Vorflug erneut, weil `main` sich bewegt hat.
- **Der Stand liegt auf `origin`:** Zweig `claude/28-gleis1-begriffssystem`, Commit `f93d4a1a6`, ein einziger Commit mit `scripts/audit/measure-216-vrouwe-minne.py` (337 Zeilen). **Er ist ungereviewt**, es gab nie einen PR und nie einen `fable-reviewer`-Lauf. Gepusht hat ihn die Koordination als Ausnahme, damit die Arbeit die Pause überlebt.
- **Offen:** Wellen 2, 3, 4, 5. **Die Wellen 2 und 3 sind am 01.09. vorab vermessen worden**, siehe §6; Welle 4 ist unvorbereitet. Die Messungen sind Erkundung und liegen als Kommentare an den Tickets, nicht als Skripte im Repositorium: die produktionsreifen Skripte entstehen in deinen PRs und gehen dort mit Review ein.

**Der alte Worktree ist weg, du legst keinen daneben an.** `mhdbdb-w0901` ist am 01.09. von der Koordination abgeräumt worden, nach den vier Prüfungen: Status leer, ignorierte Arbeit nur `node_modules/` und `scripts/__pycache__/` (beides regenerierbar), kein Stash, und der einzige Commit `f93d4a1a6` liegt auf `origin/claude/28-gleis1-begriffssystem`. `git worktree list` führt seither nur noch den Hauptbaum.

**Die alte Spur ist ebenfalls weg**, und zwar spurloser als die Abnahmeliste es vorsieht: sie steht **gar nicht mehr** in `claude agents --json`, obwohl eine bloß beendete Session dort gelistet bliebe. Ein Abschlussbericht von ihr kommt also nicht mehr. Was sie erarbeitet hat, steht vollständig in diesem Auftrag und in den Kommentaren an den Tickets; ihr Transkript liegt noch, falls du etwas nachschlagen musst.

**Ein Vorflug-Befund, damit du ihn nicht suchst:** `build-issue-matrix.py --check` war heute rot und ist es nicht mehr. Ursache war eine einzige Zelle, das `updatedAt` von #28, das durch den Messkommentar der Koordination von `2026-08-10` auf `2026-09-01` gesprungen war. Die Koordination hat `--apply` laufen lassen, nachdem sie den Unterschied gediffed hatte, und das Gate ist grün (59 gelistet, 60 geprüft). **Der Body von #44 ist damit heute schon einmal geschrieben worden**; das ist kein Statuskommentar im Sinne von Vertragsregel 8 und verbraucht deinen nicht.

---

## 4. Dein Worktree steht schon

Die Koordination hat dich mit `claude --bg --name mhdbdb-wellen-2345 --worktree mhdbdb-wellen-2345` gestartet. Der Grund für diese Form ist gemessen: der letzte Lauf hat den Worktree per `git worktree add` **neben** das Repositorium gelegt und ist beim `EnterWorktree`-Aufruf rund eine Stunde in einer Freigabe stehengeblieben. Ein Ziel außerhalb von `.claude/worktrees/` verlangt seit v2.1.206 eine interaktive Bestätigung, die **keine** `allow`-Regel abstellen kann. Für eine unbeaufsichtigte Session ist das ein Stillstand.

Dein Baum liegt also unter `C:/Users/chstn/Desktop/data/DHCraft/Projekte/Git/mhdbdb-tei-only/.claude/worktrees/mhdbdb-wellen-2345`, ist vollständig ausgecheckt und stand beim Start auf `2014bc436`.

**Vier Dinge daran sind gemessen und weichen von dem ab, was die Playbooks beschreiben. Sie kosten dich je einen Handgriff, und der letzte kostet dich sonst den Abbau:**

1. **Miss als Allererstes dein eigenes Arbeitsverzeichnis.** `claude agents --json` führte deine Session unmittelbar nach dem Start mit `cwd` auf dem **Hauptbaum**, nicht auf deinem Worktree. Ob das ein Anzeigeartefakt des Startprozesses ist oder dein tatsächliches Verzeichnis, konnte die Koordination von außen nicht entscheiden. Gib `pwd` ein. Steht dort der Worktree, ist alles gut und du sagst es im ersten Meldepunkt. Steht dort der Hauptbaum, **arbeitest du trotzdem weiter**, aber ab dann mit `git -C <worktree>` und ausschließlich absoluten Pfaden, und du sagst es ebenfalls im ersten Meldepunkt. In keinem der beiden Fälle startest du dich neu.

2. **Dein Zweig heißt `worktree-mhdbdb-wellen-2345`**, nicht `claude/...`. Das legt `--worktree` so an. Wechsle mit `git fetch origin`, dann `git checkout claude/28-gleis1-begriffssystem`. **Der Zweig `worktree-mhdbdb-wellen-2345` bleibt danach als Leiche liegen**: er enthält nichts, was nicht auf `main` steht, und gehört beim Abräumen mit `git branch -D` weg. Er steht in keiner Regel 30, deshalb steht er hier.

3. **`node_modules` als Junction auf den Hauptbaum setzen.** Von `.claude/worktrees/<name>/` aus zeigt sie auf `../../../node_modules`. Ohne sie läuft `run-tests.js` gar nicht erst an. Danach die Basismessung aus Regel 28.

4. **Dein Worktree ist `locked`, und Regel 30 weiß das nicht.** `git worktree list --porcelain` meldet für ihn `locked initializing`. Ein `--worktree`-Baum trägt diese Sperre von Haus aus, und `git worktree remove` **verweigert einen gesperrten Baum**. Beim Abräumen kommt deshalb ein Schritt vor die fünf aus Regel 30, direkt nach dem Retten des Agent-Memory: `git worktree unlock <pfad>`. Ob die Sperre bis dahin von selbst verfällt (der Grund lautet `initializing`, was nach einem Startzustand klingt), ist **nicht gemessen**; sieh vor dem Abbau einmal nach, statt es anzunehmen. Und wenn du es weißt, schreib es in den Abschlussbericht: Regel 30 gehört danach ergänzt, und die Koordination trägt es nach.

`.claude/worktrees/` **steht seit `2adc52fc5` in der `.gitignore`**, dein Worktree taucht im Hauptbaum also gar nicht erst als ungetrackt auf. Hier ist nichts zu tun und nichts zu stagen. Der Gegenpunkt gilt weiter: `.claude/agent-memory/` **ist** getrackt, und was der `fable-reviewer` dort im Worktree ablegt, geht beim Abräumen verloren, wenn es niemand herüberholt. Regel 30 stellt diesen Schritt inzwischen vor die fünf Abbauschritte.

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
| 2 | #28 Gleis 1 | ja | Kandidatenmenge über das Begriffssystem, vorab vermessen (siehe unten). Das Welle-1-Skript `measure-216-vrouwe-minne.py` liegt schon auf dem Zweig und geht in diesem PR mit, mit einem Satz dazu im Body |
| 3 | #259 | ja | Findebuch-Verweisgraph gegen unsere dreistufige Auflösung, Befundliste aus 477 Fällen, nichts korrigiert. Stoppbedingung ist vorab geprüft und erfüllt, siehe unten |
| 4 | #235 Rest | ja | die 98 Breve-Fälle mit mehrdeutiger Wortart, voller Data-Change-Lifecycle |
| 5 | Meta | offen | nur noch dein JOURNAL-Eintrag; die zwei Playbook-Aufträge sind erledigt, siehe §7 |

**Der JOURNAL-Eintrag zum 01.09. ist schon geschrieben** (Koordinationsseite, `ef4a45e0e`). Für deinen eigenen Lauf schreibst du einen neuen. Wo er hingeht, entscheidest du zu Beginn und nicht unterwegs: eigener Meta-PR als Welle 5, oder mit dem letzten Sach-PR. Beides ist recht, siehe §7 letzter Absatz.

Stoppbedingungen, je Sachwelle eine, unverändert: Welle 3 endet mit der Zahl statt mit einer Befundliste, wenn die Trefferquote nach den Normalisierungsregeln zu dünn ist; Welle 4 endet, sobald ein Token eine neue Typnummer bräuchte.

**Zu Welle 3, zwei Dinge, die den letzten Lauf sonst gekostet hätten:** der Trierer Dump liegt unter `temp/woerterbuchnetz2015/FindeB/P5/` im **Hauptbaum**, nicht in deinem Worktree, weil `temp/` gitignoriert ist; lies ihn von dort. Und Zeile 2 jeder Datei deklariert eine externe TEI-DTD auf tei-c.org, also `no_network=True` und kein `load_dtd`, sonst hängt der Lauf am Netz. Die Lizenzregel hat Vorrang vor jedem Ergebnis: nichts aus dem Dump geht ins Repositorium, in einen Commit, einen Issue-Kommentar oder an einen externen Dienst. Aggregierte Zahlen über unsere eigenen Daten sind davon nicht betroffen, Wortformen aus dem Dump schon.

**Welle 2 ist vorab vermessen** (Koordination, 01.09., [Kommentar auf #28](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/28#issuecomment-5494178173)). Kurz:

- **Die Kandidatenmenge steht:** 17 Sprachkonzepte unter `concept_23123000`, daran 6.219 Lemmata und 225.505 Korpusbelege. Gebaut über `@lemmaRef`, nie über Zeichenketten in `lexicon.xml`, wie es der Kommentar vom 10.08. verlangt.
- **Sortiere die Menge nicht nach Belegzahl.** Oben steht das Rauschen: `niht` trägt das Konzept „Lateinisch" und allein 36,0 % der Tokenmenge. Der Grund ist, dass `concept_23123000` unter „Kommunikation/Sprache" hängt und ein Bedeutungsfeld ist, das in der Praxis auch für Herkunft benutzt wird.
- **Die Grenze liegt bei 501 Belegen, aber sie ist keine Schwelle zum Wegwerfen.** Die 25 Lemmata darüber tragen 77,5 % der Nicht-Namen-Tokens und enthalten sowohl Rauschen (`niht`, `in`, `I`) als auch echte Lehnwörter (`bischof`, `engel`, `klâr`). Sieh sie einzeln durch, das ist eine Viertelstunde. Darunter liegen 3.338 Lemmata mit 35.785 Belegen, und die sind über alle Belegklassen hinweg sauber.
- **Eigennamen sind eine eigene Menge** (2.675 Lemmata, 66.622 Tokens) und auffällig verlässlich zugeordnet. Ob sie unter „Fremdsprachigkeit" fallen, ist eine Frage an KZW und keine, die du entscheidest.
- **Nur 4 der 6.219 Lemmata tragen ausschließlich Sprachkonzepte.** Ein Filter über die Konzeptdichte hilft also nicht, das ist geprüft.

**Welle 3 ist vorab vermessen** (Koordination, 01.09., [Kommentar auf #259](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/259#issuecomment-5493488964)). Was du dadurch nicht mehr selbst herausfinden musst, aber vor der Verwendung einmal nachmisst, weil auch das eine Behauptung ist:

- **Die Stoppbedingung ist erfüllt, Welle 3 läuft.** Der Prüfdatensatz sind 8.610 Paare Schreibform → Lemma, davon 5.500 mit einem Lemma, das wir führen. Die Befundliste entsteht aus **477 Fällen**, in denen beide Seiten etwas behaupten, nicht aus Zehntausenden.
- **Der Body von #259 ist am 01.09. richtiggestellt worden**, drei Zahlen und eine übertragene Warnung. Lies ihn in der neuen Fassung, nicht aus dem Gedächtnis.
- **Die im Body genannte Normalisierungsfalle greift beim Findebuch nicht**: `ʒ` kommt dort null mal vor. Die Regeln kosten nichts, also nimm sie mit, aber rechne nicht mit einem Effekt.
- **Von `woerterbuchnetz2015` liegen nur die 22 Findebuch-Dateien vor**, die Lexer-Lemmaliste nicht. Die Referenzzahlen im Body sind deshalb nicht gegenzuprüfen. Das ist kein Grund zu warten: der Findebuch-Abgleich braucht sie nicht.
- **`effort:` steht seit dem 01.09. auf `medium`**, nachgezogen auf die Aufwandsangabe im Body, die immer schon „Mittel" sagte.

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

---

## 11. Meldepunkte an die Koordination

Antworte immer an das `from` dieser Nachricht, nie an einen Namen aus einem Text. Fünf Meldungen, kurz, je zwei bis fünf Zeilen. Sie ersetzen den Abschlussbericht nicht.

1. **Nach dem Vorflug.** Das Ergebnis von `pwd` aus §4 Punkt 1, beide Regel-28-Zählungen, der Stand der Gates. Wenn etwas davon nicht stimmt, hier und nicht später.
2. **Vor jedem `fable-reviewer`-Lauf** eine Zeile: welcher PR, welche Runde. Und **nach jedem Lauf** eine Zeile: wie viele Befunde, wie viele nach dem Nachmessen übernommen.
3. **Nach jedem Merge nach `main`** eine Zeile mit dem Commit und der VERDICT-Zeile.
4. **Bei jeder Blockade sofort**, auch mitten in der Arbeit. Eine Freigabe, die dich anhält, ein besetzter Testport, ein Gate, das du nicht grün bekommst. Melden statt umleiten: du reichst nichts an eine andere Session weiter, Berechtigungen gelten je Session.
5. **Wenn du eine Welle überspringst oder eine Stoppbedingung greift**, mit der Zahl, die es entschieden hat.

Punkt 2 ist der, der sonst fehlt: die Koordination führt eine Liste offener Prüfungen und darf nichts als fertig verbuchen, solange eine Runde darauf noch läuft. Ohne deine Meldung ist das eine Liste, deren Einträge niemand kennt.

**Der `fable-reviewer` läuft seit heute auf Fable 5.1** (`model: claude-fable-5-1` in seiner Frontmatter, nachgesehen). Das ist die Deklaration, kein Beweis: dein erster Lauf ist der erste echte. Löst die Modell-ID nicht auf, ist das ein Fall für Meldepunkt 4 und keiner, den du durch Ausweichen auf den `fable-advisor` löst.
