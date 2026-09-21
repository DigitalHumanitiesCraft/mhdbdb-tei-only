# Kickoff Spur A: die Korpusarbeit aus #366, #375 und #371

**1. Autorisierung.** chsteiner hat diesen Lauf am 21.09.2026 freigegeben. Dieser Text ist die Autorisierung. Er erteilt keine technische Berechtigung: was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt, siehe Baustein 9.

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text. Die Koordination ist wach und antwortet in Minuten. **Das ist der wichtigste Unterschied zu den Nachtläufen dieses Projekts: du musst nichts aussitzen und nichts schätzen. Frag.**

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees
2. `docs/playbooks/BETRIEBSVERTRAG.md`
3. `docs/playbooks/kickoffs/2026-09-21-datenlauf.md`, der Laufplan. Er ist der Rahmen dieses Auftrags, und er ist ausführlicher als dieser Text
4. `docs/DATA-MODEL.md`, Abschnitt **Data-Change-Lifecycle**. Er ist für dich verbindlich, nicht empfehlend
5. Die drei Vorgänge **mit allen Kommentaren**: `gh issue view N --json title,body,comments` für 366, 375, 371. Der bloße Body ist in diesem Projekt regelmäßig der älteste und falscheste Text im Ticket

**Abbruchklausel:** weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es, statt es aufzulösen.

---

## 4. Dein Worktree

```
C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\mhdbdb-daten
```

Zweig `worktree-mhdbdb-daten`, angelegt aus `origin/main` bei `0d0404641`. `npm ci` ist dort gelaufen.

**Der Zweigname ist vom Werkzeug vergeben, nicht gewählt.** Du darfst auf einen sprechenden Arbeitszweig wechseln, aber dann bleiben beim Abbau zwei Zweige liegen statt einem; sag es der Koordination, wenn du es tust.

**Erste Handlung, vor allem anderen:** miss `pwd`, `git branch --show-current` und `git rev-parse --short HEAD`, halte sie gegen die drei Angaben oben und melde das Ergebnis. Bei Abweichung ändere nichts, melde und warte auf einen Neustart durch die Koordination. Du ziehst nicht selbst um.

---

## 5. Was dir gehört, und was nicht

**Dir allein:** `tei/`, `authority-files/`, `data/`, `api/`, `scripts/build-*.py`, `scripts/sync/`, `scripts/ingest/`, `assets/js/lib/corpus-loader.js` und die Versionszeilen in `docs/TEI-MODEL.md` §11 und `docs/INDEX.md`.

**Dir allein, aber nur für die Formenzahl:** die Fundstellen der Zahl `256.773` in `docs/DATA-MODEL.md`, `docs/TEI-MODEL.md`, `docs/TEI-MODEL-AUTH-FILES.md`, `docs/CONTRACTS.md`, `schema/README.md`, `index.html`, `hilfe-daten.html`. Warum das eine ausdrückliche Ausnahme vom Freeze ist, steht im Laufplan. **`docs/JOURNAL.md` ist davon ausgenommen**, die Zahl steht dort in einem datierten Bericht.

**Geteilt, und deshalb mit Regel:** `docs/JOURNAL.md` und `fehlerjournal.md` schreibst du anhängend und **als letzten Commit**, unmittelbar nach `git fetch origin`. Kein `merge`, kein `rebase`: du stehst auf einem eigenen Zweig, ein Fast-Forward scheitert dort, und was du dann tust, um weiterzukommen, hat niemand geplant. **Deine Fehlerjournal-Nummern sind 40 bis 44**, Spur B hat 45 bis 49.

**Dein eigenes Reviewer-Memory:** eine eigene Datei unter `.claude/agent-memory/fable-reviewer/`, nie eine gemeinsame Reihe. Am Lauf vom 13./14.09. hängten drei von vier Spuren an dieselbe Indexzeile an, und drei von vier Merges kollidierten.

**Nicht deins:** alles andere. Wer eine Datei außerhalb seines Bereichs ändern muss, ändert sie nicht, sondern meldet es.

**Eingefroren** (Liste und Grund im Laufplan): `CLAUDE.md`, die 15 promptotyping-Dokumente außer den genannten Ausnahmen, `docs/playbooks/`, `.github/workflows/`, `scripts/audit/`. Willst du dort etwas geändert haben, meldest du den Wunsch mit Datei, Ankertext, wörtlichem Ersatztext und einem Satz Begründung. Die Koordination trägt ein.

**Nichts wirkt über deinen Baum hinaus.** Kein `git push` auf fremde Zweige, kein Eingriff in den Hauptcheckout, keine Änderung an globalen Einstellungen unter `~/.claude/`.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` ist vor deinem ersten Push Pflicht. Am 02.09. ist zweimal ohne Runde gepusht worden, weil der Typ fehlte und die Session ausgewichen ist. Melde und warte.

**Ein maschinenweit exklusives Betriebsmittel: Port 8080.** `npm run serve` und `npm test` belegen ihn, und Spur B braucht ihn zeitweise für ihren Dev-Server. Du hast Vorrang, aber **du forderst ihn an, statt ihn zu nehmen**: melde deinen Testlauf, dann fährt er. `scripts/run-tests.js` erkennt einen fremden Server und bricht mit klarer Meldung ab, du bekommst also keine Phantomfehler, sondern einen blockierten Lauf.

Das zweite exklusive Betriebsmittel sind die **Indexversionsnummern**. Heute frei: Corpus 4.2.18, Authority 1.9.8, und es ist kein anderer PR offen, der sie beanspruchen könnte. Am 10.09. hat genau diese Kollision acht konfligierende Dateien und einen Vollrebuild auf fremdem Zweig gekostet.

---

## 6. Die Pakete, in dieser Reihenfolge

**Alle Zahlen unten hat die Koordination am 21.09. selbst gemessen. Sie sind von niemandem gegengeprüft. Miss sie nach, bevor du sie verwendest, und widersprich, wenn sie abweichen.** Die Messskripte liegen im Scratchpad der Koordination; frag danach, statt sie neu zu erfinden. **Dieser ganze Auftragstext ist eine Behauptung, kein Befund.**

Die Reihenfolge ist nach Zahl der berührten Korpusdateien begründet (5, 4, 37). Bricht A3, stehen A1 und A2 bereits fest.

### A1: #366, acht Tokens

Acht Tokens, alle heute **ohne** `@lemmaRef`, in fünf Dateien (DES2, KBL4, KDO ×4, KBL3, MBS2). KZW hat fünf davon am 17.09. entschieden und drei bereits am 11.09.

Eine Falle: `KDO_123250200_3` steht im Ticket als `DO_...` getippt. Such nach der `xml:id`, nicht nach der Schreibung im Kommentar.

**A1 prägt sieben Variantentypen, und das stand nicht in der ersten Fassung dieses Auftrags.** Keine der sieben Schreibungen ist unter ihrem Ziellemma belegt: `bersige` unter `lemma_26988`, `gewuertz`, `würtzenn` und `würczenn` unter `lemma_7736`, `gehornn` unter `lemma_2039`, `zimendtrinttenn` unter `lemma_26776`, `hawsen` unter `lemma_42619`. Sieben Paare für acht Tokens, weil zwei dieselbe Form unter demselben Lemma sind. Das ist keine neue Entscheidung: es steht seit dem 06.09. im Ticket und folgt der Regel aus #367. Bei `hawsen` ist das Umhängen ausgeschlossen, weil die Form unter `lemma_49714` als `type_372368` geführt wird und ein Umhängen die #363-Tokens mitrisse.

**Der Datenauftrag zu `hirne` hat zwei Hälften, und nur eine ist ausführbar.** KZW schreibt: „Entferne diese Schreibvariante aus dem lemma hirne (lemma_2853), denn das ist leer und ohne Token. Füge es zu lemma_2039 hinzu." Die zweite Hälfte steckt in den acht Tokens. Die erste hat kein Objekt: gemessen trägt `lemma_2853` **228 Tokens in 66 Dateien**, ist also nicht leer, und die Form `gehornn` steht gar nicht unter ihm.

Führ die erste Hälfte **nicht** aus. Schreib stattdessen eine Rückfrage an #366, und zwar **als Fortschreibung mit Vorlauf**: was bereits umgesetzt ist, was du gemessen hast, warum die erste Hälfte kein Objekt hat. Ohne diesen Vorlauf liest KZW sie als die Sorte Wiederholung, die sie am 17.09. in #406 gerügt hat.

### A2: #375, vier Tokens

`TIT_50020_2`, `PZ_23625_1`, `NLC_196220_1`, `KU_1534_3`, nach KZWs Tabelle vom 14.09. alle vier auf ADJ.

**Prüf zuerst, was schon getan ist.** Der Thread sagt, die acht „eindeutigen" Fälle seien am 14.09. in PR #438 umannotiert worden, und die vier VRB-Fälle derselben Tabelle (`OVG_6534200_1`, `BAR_2276_1`, `DFL_19560_1`, `BRF_53370_1`) bestätigen nur den Ist-Stand. **Die Koordination hat das begonnen zu messen und nicht zu Ende gebracht**, also ist es offen und du misst es. Wenn die acht schon ADJ tragen, ist A2 genau vier Tokens groß.

Das Muster steht fertig in `scripts/apply-308-375-432.py`: `lemma_7505` VRB mit Quelltyp → `lemma_7338` ADJ mit Zieltyp, Trefferzahl je Ersetzung, Abbruch bei Abweichung. Die Zieltypen nach Form: `wâren` → `type_287014`, `woren` → `type_372364`. **Warnung aus dem Ticket: `type_80601` (`waren` ohne Zirkumflex) nie anfassen.**

### A3: #371, 76 Tokens

**Maßgeblich ist das `actions`-Array in KZWs JSON-Kommentar vom 15.09., nicht die Gruppenentscheidung.** Das JSON hat zwei Arrays: `faelle` mit 95 beurteilten Fällen und `actions` mit 76. Die Differenz geht auf: 76 anwendbar, 17 mit `option: OFFEN`, 2 mit `NEU_STAND`, macht 95.

Zwei Gruppen stehen formal auf `OFFEN` oder ohne Entscheidung, und trotzdem liegen 37 der 76 Arbeitsfälle in ihnen: KZW hat sie einzeln entschieden, statt die Gruppe zu schließen. **Wer nach Gruppen arbeitet, lässt die Hälfte liegen.** Umgekehrt sticht die Einzelentscheidung auch gegen die Gruppe: `MSP_1711020_12` steht in Gruppe `stand` (Gruppenziel `lemma_5732`), trägt aber `option: lemma_5710` mit `status: "anders"`.

Alle 76 tragen heute **kein** `@lemmaRef`. Es wird also nichts umgehängt, nur gesetzt.

**Die Typarbeit**, gemessen gegen `variants.xml`:

| Form | Ziellemma | Tokens | Typ |
|---|---|---|---|
| `stat` | `lemma_5710` | 18 | `type_20050`, besteht |
| `stat` | `lemma_5732` | 27 | `type_20161`, besteht |
| `stat` | `lemma_5712` | 26 | **neu** |
| `stât` | `lemma_5732` | 4 | **neu** |
| `stat` | `lemma_5713` | 1 | **neu** |

Höchste vergebene Nummer am 21.09.: `type_372376`. **Miss das Maximum frisch**, es hat sich im September mehrfach bewegt. Die drei Nummern samt Paarzuordnung schreibst du **vor** dem ersten Token in den PR-Text und nach `ingest/`, sonst prägt eine Fortsetzung eine vierte.

Das deckt sich mit KZWs eigenem `hinweis` im JSON, den die Koordination in allen drei Punkten am Bestand geprüft hat.

**Nicht anfassen:** die 17 `OFFEN` und die 2 `NEU_STAND`. Letztere bräuchten ein neues Lemma, und Lemmaanlage kommt in diesem Lauf nirgends vor.

**Zwei Dinge gehen an KZW zurück, halten dich aber nicht auf:**

1. ~~Ihre `zusammenfassung` sagt `offen: 7`, gezählt sind **17**, falsch ist die Zahl in der Zusammenfassung.~~ **Zurückgezogen, der Vorwurf war falsch, und du hast ihn gefunden.** Die beiden Zahlen zählen verschiedene Felder: `zusammenfassung` zählt `status` (95 gesamt, 63 `ok`, 25 `anders`, 7 `offen`, alle vier decken sich exakt), die 17 zählen `option: OFFEN`, zusammengesetzt aus 7 mit `status: offen` und 10 mit `status: anders`. **Beide Zahlen sind richtig.** An KZW geht deshalb keine Korrektur, sondern diese Auflösung: ihr Feld sagt, wie sie zum Vorschlag steht, unseres, was am Ende annotierbar ist.
2. **Das JSON ist nicht parsbar.** Bei Zeichen 82.382, im `actions`-Array, steht `"confidence": "high"` gefolgt von der Klartextzeile `Prüfer: Alan van Beek`. Genau einmal im ganzen Kommentar. Entferne diese eine Zeile und parse dann **strikt** mit `json.loads`, mit `len(faelle) == 95` und `len(actions) == 76` als harter Bedingung. Kein Feldschnitt über Regex: der hat keine Kontrolle darüber, ob er ein Objekt verliert, und `rules/bauweise.md` verlangt für eine unbekannte Eingabe einen harten Fehler statt eines stillen Überspringens. Meld die Stelle im Ticket, damit KZW und Alan wissen, dass ihr Ausgabeformat eine Handnotiz nicht verträgt.

---

## 7. Wie gearbeitet wird

**Als Skript, nicht als 88 Einzeledits.** Vorbilder: `scripts/apply-308-375-432.py` (Trefferzahl je Ersetzung, Abbruch bei Abweichung vom Erwartungswert) und `scripts/ingest/pos-disambig/fix-363-hausenblase.py` (Ist-Zustand je Token verifizieren, Abbruch bei fehlender Regel). Leg es unter `scripts/ingest/` ab.

**Je Token drei Attribute: `@lemmaRef`, `@pos`, `@corresp`.** Das dritte ist der Grund, warum die Typprägung überhaupt Arbeit ist: `scripts/sync/extract-variants.py` liest ausschließlich `<w>` mit `@lemmaRef` **und** `@corresp`, ein Token ohne `@corresp` erscheint in `variants.xml` nicht. Und `@pos` ist keine Kür: gemessen am 21.09. **vor dem Lauf** tragen **7.547.816** Tokens `@lemmaRef` mit `@pos` und **null** ohne. Ein Token ohne `@pos` wäre eine neue Klasse im Bestand. KZWs `actions` liefern die Wortart mit.

**Die Gegenprobe, die den stillen Fehler fängt.** `extract-variants.py` nimmt je Typ die häufigste Form und das häufigste Lemma und meldet Mehrdeutigkeiten nur als Zähler, ohne Exit-Code. Ein Token, das `lemmaRef=lemma_5732` mit `corresp=type_20050` kombiniert, bleibt deshalb in der Mehrheit von `lemma_5710` unsichtbar und hängt still am falschen Lemma. **Kein Gate sieht das.** Also: `extract-variants.py` **ohne** `--apply` vor und nach deinem Lauf, und die Differenz muss genau die zehn neuen Typen des Laufs zeigen und **null** zusätzliche Mehrdeutigkeiten.

**Dann die Kette aus dem Data-Change-Lifecycle**, vollständig und in dieser Reihenfolge: `extract-variants.py --apply`, `build-corpus-index.py`, `build-authority-index.py`, `build-api.py`, Versions-Bump an **allen fünf** Stellen. Freie Nummern heute: Corpus **4.2.18**, Authority **1.9.8**, und es sind keine anderen PRs offen, die sie beanspruchen könnten.

**`--allow-dirty` brauchst du für alle drei Builds.** Sie verweigern sonst den unsauberen Baum, der Lifecycle verlangt aber den gemeinsamen Commit von TEI, Indexen und `api/`. **Greif nicht zu `git stash`**, wenn eine Meldung „commit or stash the changes above" erscheint: das hat in diesem Projekt schon Arbeit vernichtet.

**Danach die Formenzahl nachziehen**, nach dem Muster von `scripts/update-variant-count-372376.py`, und `scripts/audit/doc-count-audit.py --check` lokal grün fahren. **Lies die neue Zahl aus `variants.xml` ab, statt sie zu rechnen.** Zehn neue Typen heißen rechnerisch zehn neue Formen, aber das ist eine Vorhersage. Weicht die abgelesene Zahl ab, ist das ein Meldepunkt und kein Grund, sie zu korrigieren.

---

## 8. Vorab entschieden, nicht neu zu verhandeln

- **Neue Variantentypen prägen**, zehn Stück: sieben in A1, drei in A3, keine in A2. Präzedenz #367 und #363. Die Regel lautet nicht „nie prägen", sondern: umgehängt wird nur, wo korpusweit ausschließlich Tokens der wandernden Menge den Typ tragen.
- **Nicht mergen.** Du öffnest einen PR und meldest. An ihm hängt KZWs Abnahme.
- **Kein Ticket schließen.** Ein `Closes` ist keine Abnahme.
- **Relabeln**, was du anfasst, in derselben Session, plus ein Statuskommentar je Vorgang.

**Widerspruch ist ausdrücklich erlaubt**, auch gegen die vier Punkte oben, und er geht an die Koordination. Sie trägt ihn in den Laufplan ein, unter „Grenzverhandlungen", damit er nach dem Lauf noch gelesen wird. Ein Einwand in einem PR-Text ist verloren: den öffnet nach dem Merge niemand mehr.

**Eine Vorgabe hält die Koordination selbst für schwach, und hier ist die Ersatzfassung.** Die Reihenfolge A1 → A2 → A3 ist nach der Zahl der berührten Dateien begründet (5, 4, 37), aber A3 ist mit Abstand das größte Paket und könnte den Tag allein füllen. Kommst du nach dem Messen zu dem Schluss, dass A3 zuerst laufen sollte, **tu es und sag es**, mit demselben einen Bump am Ende. Was **nicht** zur Disposition steht, ist der eine gemeinsame Rebuild: drei Rebuilds für drei Pakete wären dreimal dieselbe Stunde.

---

## 9. Melden und Halten

**Melden, dann weiterarbeiten:**

- nach dem Lesen: `pwd`, Zweig, HEAD gegen die Angaben in Baustein 4
- je Paket: der **nachgemessene** Umfang gegen den hier behaupteten
- vor dem Versions-Bump: die beanspruchten Nummern
- Beginn und Ergebnis jeder Reviewrunde, mit Rundennummer **und der Kennung des geprüften Standes**

**Anhalten und warten:**

- `pwd` weicht ab
- eine Änderung würde eine fremde Datei berühren
- ein Paketumfang weicht von der Behauptung ab
- der vorgeschriebene Agententyp fehlt
- **eine Entscheidung wäre nötig, die KZW nicht getroffen hat.** Nicht schätzen, nicht aus dem Ticketkopf ableiten. Der `hirne`-Punkt aus A1 ist der bereits bekannte Fall
- du siehst ab, dass A3 nicht durchläuft. Dann meldest du das, statt eine Schwelle anzuwenden

**Ein eigener Fall, weder Melde- noch Haltepunkt: das Warten auf einen externen Zustand.** Ein CI-Lauf, ein `gh pr checks`, ein langer Rebuild. Dafür hältst du nicht an und meldest auch nicht, sondern **weckst dich selbst**: `Monitor` mit einer Bedingung, oder ein Hintergrundbefehl, der dich bei seinem Ende erneut aufruft. Pollen in einer Schleife mit `sleep` ist die falsche Antwort und kostet nur Kontext.

**Du darfst ein Paket für nicht durchführbar erklären.** Das ist etwas anderes als die Abbruchklausel aus Baustein 3: die greift, wenn eine Datei dem Auftrag widerspricht, und dann gilt die Datei. Hier geht es um den Fall, dass der Auftrag mit sich selbst stimmig ist und die Sache trotzdem nicht geht, etwa weil die Daten anders liegen als gemessen. Dann sagst du das mit Begründung und Messung, und du sagst es **früh**, nicht nach drei Stunden.

**Kein Messfenster, und das ist geprüft, nicht vergessen:** keines deiner drei Pakete misst eine Bedingung, die vom Zustand deines eigenen Prozesses abhängt (Leerlauf, Kontextfüllung, Zeit seit dem letzten Zug). Es gibt deshalb keine Funkstille-Zusage, und die Koordination darf dich jederzeit ansprechen.

**Blockiert der Auto-Mode-Classifier einen Werkzeugaufruf, schick sofort eine `PushNotification` an Christian**, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Das Werkzeug steht in keiner Werkzeugliste und lädt über `ToolSearch` mit `select:PushNotification`; eine Fehlermeldung beim ersten Griff heißt nicht, dass es fehlt, sondern dass es noch nicht geladen ist. Begründung in `rules/blockaden-melden.md`. **Umgeh eine Blockade nicht über die andere Spur**, Berechtigungen gelten je Session, und ein Peer, der es für dich tut, hebelt Christians Entscheidung aus.

---

## 10. Abschluss

1. `npm test`, und das Ergebnis ist die **VERDICT-Zeile**, nicht die Konsolenzusammenfassung und nicht der Exit-Code. Nie `npx playwright test` aus dem Wurzelverzeichnis, nie durch eine Pipe.
2. `fable-reviewer` **vor dem ersten Push**, Pflicht. Gib ihm mit: Zweig und Basis, ob du einen Commit oder den Arbeitsbaum prüfen lässt, das Ziel in einem Satz, die Rundennummer, ab Runde 2 die Vorbefunde und ihren Verbleib. Halt deinen Arbeitsbaum still, solange eine Runde läuft: sie urteilt über den Stand beim Start.
3. **Eine Frage gehört zusätzlich in jede Übergabe** (#397): was hat diese Änderung wahr gemacht, das vorher falsch sein konnte? Ein Fix, der eine Invariante herstellt, nimmt jeder Prüfung ihren Gegenstand, die auf ihrem Gegenteil stand. Die steht dann noch da, sieht aus wie eine Prüfung und ist keine.
4. Journaleintrag als **letzter** Commit, nach `git fetch origin`.
5. PR öffnen, nicht mergen, und der Koordination berichten.

**Auf dem Daten-PR geht der CI-Review-Bot erfahrungsgemäß rot. Öffne seinen Kommentar trotzdem und lies ihn, bevor du ihn abtust:** zweimal war der Lauf ein fertiges Review mit echten Befunden, das die Action nur rot markiert hat, und #377 wurde mit diesem Kommentar ungelesen gemergt. Kein Rerun, kein Aufteilen des PR in Korpus- und Index-Commit, keine Suche nach einem Konfigschalter.

**Beide Spuren starten gleichzeitig**, keine wartet auf die andere. Berührungspunkte sind nur Port 8080 und die beiden geteilten Dateien.

### Definition of Done, als Lesertest

Du bist fertig, wenn jemand, der diesen Lauf nicht miterlebt hat, aus dem PR allein beantworten kann:

- **Welche Tokens wurden angefasst, namentlich**, und auf welche Entscheidung von KZW mit Datum und Kommentarverweis geht jedes zurück?
- **Welche zehn Typnummern wurden geprägt**, für welche Form unter welchem Lemma, und warum geprägt statt umgehängt?
- **Was wurde bewusst nicht angefasst** (die 17 `OFFEN`, die 2 `NEU_STAND`, die erste Hälfte des `hirne`-Auftrags), und warum nicht?
- **Wie lautet die abgelesene Formenzahl nach dem Rebuild**, und deckt sie sich mit der Vorhersage aus zehn neuen Typen?
- **Was muss KZW noch entscheiden**, damit dieser Vorgang zu Ende geht?

Kann er eine davon nicht beantworten, fehlt sie im PR-Text, und der PR ist noch nicht fertig.
