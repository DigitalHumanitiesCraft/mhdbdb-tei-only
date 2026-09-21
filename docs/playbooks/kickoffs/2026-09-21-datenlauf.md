# Laufplan 21.09.2026: die vier von KZW entsperrten Vorgänge

**Tagbetrieb, kein Nachtlauf** (chsteiner, 21.09.). Das ändert nicht den Zuschnitt, sondern den Apparat: eine Rückfrage geht direkt an Christian oder die Koordination und wartet nicht auf eine Inbox, ein Haltepunkt kostet Minuten statt Stunden, und die Abbruchregel für A3 braucht keine Uhrzeit mehr, weil jemand wach ist und entscheiden kann. **Was bleibt, ist die Parallelität**, denn sie ist der Grund für den Lauf: zwei Arbeitspakete, die einander nicht berühren, laufen gleichzeitig statt nacheinander.

**Was der Freeze trotzdem soll:** er schützt nicht vor der Nacht, sondern vor der anderen Spur. Zwei gleichzeitig laufende Sessions, von denen eine `CLAUDE.md` ändert, sind am Tag genauso ein Problem wie um drei Uhr früh, nur fällt es schneller auf.

**Was sich gegenüber den Vorfassungen geändert hat, und warum das hier steht:** `fable-advisor` hat beide gegengelesen, und die Koordination hat jeden Befund am Bestand nachgemessen statt ihn zu übernehmen.

Aus der ersten Runde: vier von fünf Umfangsangaben waren falsch, keine davon knapp. Die Lehre dazu: **die Zahl im Ticketkopf ist eine Behauptung über eine Menge, die seit ihrer Niederschrift gearbeitet hat.**

Aus der zweiten Runde kam der teuerste Befund des ganzen Vorlaufs, und er betraf nicht eine Zahl, sondern den Plan selbst: **er hätte sich nachts blockiert.** Die Typprägung in A3 hebt die dokumentierte Formenzahl, ein Gate prüft sie, und die Dateien, in denen sie steht, hatte der Plan teils eingefroren und teils niemandem zugewiesen, während die Abnahme dasselbe Gate grün verlangte. Der Absatz dazu steht unter Freeze. **Ein Plan, der eine Datei einfriert, muss wissen, welche Gates an ihr hängen**, und das ist die Lehre, die über diesen Lauf hinausgeht.

**Alle Zahlen in diesem Plan sind am 21.09.2026 von der Koordination am Bestand gemessen, nicht aus Tickets übernommen und von niemandem gegengeprüft.** Jede Spur misst sie nach, bevor sie sie verwendet, und widerspricht, wenn sie abweichen. Die Messskripte liegen im Scratchpad der Koordinationssitzung und werden dem jeweiligen Kickoff beigelegt.

---

## 1. Warum es diesen Lauf gibt

KZW hat zwischen dem 11. und 17.09. vier Vorgänge entschieden, die danach weiter als ihr Rückstand geführt wurden. Die Triage in #406 ist am 21.09. neu aufgebaut, die Labels sind korrigiert. Was sie freigegeben hat, ist jetzt Arbeit.

| Vorgang | Ihre Entscheidung | Label heute |
|---|---|---|
| #366 | 11.09. und 17.09., acht Tokens plus ein Datenauftrag | `auto:full` / `effort:small` |
| #375 | 14.09. Der größere Teil ist bereits umgesetzt, offen sind vier Fälle | `auto:full` / `effort:small` |
| #371 | 15.09., als Maschinenlesbares: 95 beurteilte Fälle, 76 davon als Arbeitsliste | `auto:checkin` / `effort:medium` |
| #359 | 16.09., Grundsatz plus drei Aufträge | `auto:checkin` / `effort:medium` |

---

## 2. Der Zuschnitt, und warum er nicht vier Spuren sind

**Die drei Datenvorgänge lassen sich nicht nach Dateibesitz trennen.** Das ist die Kernbedingung des Operator-Skills, und sie ist hier dreifach verletzt:

1. **Gemeinsame Zieldateien.** Alle drei schreiben `authority-files/variants.xml`, beide `data/*.json.gz`, die Dateien unter `api/` und die Versionsliterale an fünf Stellen (`build-corpus-index.py`, `build-authority-index.py`, `corpus-loader.js`, `docs/TEI-MODEL.md`, `docs/INDEX.md`).
2. **Inhaltliche Kopplung über das ganze Korpus.** `DATA-MODEL.md`: „per type id the most frequent form in the **entire** corpus decides", also kann ein Eingriff in einem Text Einträge umschreiben, die nur in anderen belegt sind. Ein Schnitt auf `tei/`-Ebene hilft nicht, weil `extract-variants.py` alle 667 Dateien liest.
3. **Die Versionsnummer ist ein Betriebsmittel, das zwei Zweige gleichzeitig beanspruchen können, und kein Gate merkt es.** Gemessen am 10.09.2026: #363 wurde mit 4.2.14 und 1.9.4 gemergt, während #416 dieselben Nummern beansprucht hatte. Kosten: acht konfligierende Dateien im älteren PR, plus Renumber und Vollrebuild auf fremdem Zweig.

**Daraus zwei Spuren statt vier.**

### Spur A: `daten`

Drei Pakete, streng sequenziell, **ein** Rebuild der abgeleiteten Schicht am Ende, **ein** Versions-Bump, **ein** PR.

| Paket | Vorgang | Gemessener Umfang | Stoppbedingung |
|---|---|---|---|
| A1 | #366 | **8** Tokens in 5 Dateien (DES2, KBL4, KDO ×4, KBL3, MBS2), alle ohne `@lemmaRef`. Dazu ein Datenauftrag, der **nicht ausgeführt**, sondern beantwortet wird | mehr oder weniger als 8 |
| A2 | #375 | **4** offene ADJ-Fälle: `TIT_50020_2`, `PZ_23625_1`, `NLC_196220_1`, `KU_1534_3` | mehr oder weniger als 4 |
| A3 | #371 | **76** Tokens in 37 Dateien, alle ohne `@lemmaRef`. Drei neue Variantentypen | ein Fall außerhalb des `actions`-Arrays wird angefasst |

**Reihenfolge begründet:** aufsteigend nach Zahl der berührten Korpusdateien (5, 4, 37). Bricht A3, stehen A1 und A2 bereits fest.

#### A1, im Einzelnen

Die erste Fassung nannte fünf Formen. Gemessen sind es acht: KZW hat am 17.09. fünf entschieden und am 11.09. bereits drei weitere (`KDO_123290200_10` → Zimtrinde `lemma_26776`; `KBL3_11282040_1` und `MBS2_52060_11` → hausen, der Fisch). Alle acht tragen heute kein `@lemmaRef`.

Eine Falle im Ticket: `KDO_123250200_3` ist dort als `DO_...` getippt. Die Spur sucht nach der `xml:id`, nicht nach der Schreibung im Kommentar.

**Der Datenauftrag besteht aus zwei Hälften, und nur die erste hat kein Objekt.** KZW schreibt: „Entferne diese Schreibvariante aus dem lemma hirne (lemma_2853), denn das ist leer und ohne Token. Füge es zu lemma_2039 hinzu." Die **zweite** Hälfte ist ausführbar und steckt bereits in den acht Tokens (`KDO_121160700_11` → `lemma_2039`). Die **erste** hat kein Objekt: gemessen trägt `lemma_2853` **228 Tokens in 66 Dateien**, ist also nicht leer, und die Form `gehornn` steht unter ihm gar nicht, kann dort also nicht entfernt werden.

Die Spur führt die zweite Hälfte aus und die erste nicht. **Die Rückfrage geht als Fortschreibung an #366, nicht als Frage aus dem Nichts:** sie nennt, was bereits umgesetzt ist, was gemessen wurde und warum die erste Hälfte kein Objekt hat. Ohne diesen Vorlauf liest KZW sie als genau die Sorte Wiederholung, die sie in #406 gerügt hat.

#### A3, im Einzelnen

**Die erste Fassung sagte „45 anwendbare Belege (ufer 32, stand 13)". Das war die Summe zweier Gruppenentscheidungen und nicht die Arbeitsmenge.** KZWs JSON hat auf oberster Ebene zwei Arrays: `faelle` mit 95 beurteilten Fällen und `actions` mit **76**, und `actions` ist die Arbeitsliste. Die Differenz geht auf: 76 anwendbar, 17 mit `option: OFFEN`, 2 mit `NEU_STAND`, macht 95.

**Maßgeblich ist `actions`, nicht die Gruppenentscheidung.** Zwei Gruppen stehen formal auf `OFFEN` beziehungsweise ohne Entscheidung, und trotzdem liegen 37 der 76 Arbeitsfälle in ihnen: KZW hat sie einzeln entschieden, statt die Gruppe zu schließen. Wer nach Gruppen arbeitet, lässt die Hälfte liegen. Umgekehrt sticht die Einzelentscheidung auch gegen die Gruppe: `MSP_1711020_12` steht in der Gruppe `stand` (Gruppenziel `lemma_5732`), trägt aber `option: lemma_5710` und `status: "anders"`.

**Was an Typarbeit wirklich anfällt**, gemessen gegen `variants.xml` (42.626 Einträge, 256.773 Formen mit positiver type-Nummer):

| Form | Ziellemma | Tokens | Typ |
|---|---|---|---|
| `stat` | `lemma_5710` | 18 | `type_20050`, besteht |
| `stat` | `lemma_5732` | 27 | `type_20161`, besteht |
| `stat` | `lemma_5712` | 26 | **neu** |
| `stât` | `lemma_5732` | 4 | **neu** |
| `stat` | `lemma_5713` | 1 | **neu** |

45 Tokens bekommen eine bestehende Nummer, 31 eine von drei neuen. **A1 prägt weitere sieben** (siehe dort), der Lauf kommt damit auf **zehn**. Höchste vergebene Nummer am 21.09.: `type_372376`; vergeben werden `type_372377` bis `type_372383` an A1 und `type_372384` bis `type_372386` an A3.

**Das deckt sich mit KZWs eigenem `hinweis`, und zwar in allen drei Punkten**, die Koordination hat jeden einzeln am Bestand geprüft: dass `lemma_5712` und `lemma_5713` die Schreibvariante `stat` noch nicht tragen, dass `NEU_UFER`/`NEU_STAND` erst ein neues Lemma bräuchten und deshalb nicht in `actions` stehen, und dass die vier PSG-Belege mit Zirkumflex einen neuen Typ unter `lemma_5732` brauchen. Ihre Analyse ist belastbar.

**Die Typprägung ist ein Handgriff und kein Nebenprodukt des Rebuilds.** `scripts/sync/extract-variants.py` liest ausschließlich `<w>`-Elemente, die **beide** Attribute tragen, `@lemmaRef` **und** `@corresp="variants.xml#type_N"`. Ein Token mit neuem `@lemmaRef`, aber ohne `@corresp`, erscheint in `variants.xml` nicht.

**Und ein drittes Attribut gehört dazu, das in der ersten Fassung fehlte: `@pos`.** Gemessen über das ganze Korpus: 7.547.816 `<w>` tragen `@lemmaRef` **und** `@pos`, und **kein einziges** trägt `@lemmaRef` ohne `@pos`. Ein Token ohne `@pos` wäre also eine neue Klasse im Bestand. KZWs `actions`-Einträge liefern die Wortart mit (NOM, VRB), sie muss nicht geraten werden.

**A3 wird als Skript gefahren, nicht als 76 Einzeledits.** Vorbilder im Repositorium: `scripts/apply-308-375-432.py` (Trefferzahl je Ersetzung, Abbruch bei Abweichung vom Erwartungswert) und `scripts/ingest/pos-disambig/fix-363-hausenblase.py` (Ist-Zustand je Token verifizieren, Abbruch bei fehlender Regel). Das Skript setzt je Token `@lemmaRef`, `@pos` und `@corresp`.

**Die Gegenprobe gegen die stille Fehlzuweisung**, und sie ist der Grund, warum A3 überhaupt ein Skript braucht: `extract-variants.py` nimmt je Typ die häufigste Form und das häufigste Lemma und meldet Mehrdeutigkeiten nur als Zähler, ohne Exit-Code. Ein Token, das `lemmaRef=lemma_5732` mit `corresp=type_20050` kombiniert, bleibt deshalb in der Mehrheit von `lemma_5710` unsichtbar und hängt still am falschen Lemma. Kein Gate sieht das. Deshalb: `extract-variants.py` **ohne** `--apply` vor und nach dem Lauf, und die Differenz muss genau die zehn neuen Typen des Laufs zeigen und null zusätzliche Mehrdeutigkeiten.

**Das JSON wird strikt geparst, nicht geschnitten.** Die eine bekannte Fremdzeile entfernen, dann `json.loads`, dann `len(faelle) == 95` und `len(actions) == 76` als harte Bedingung. Ein Feldschnitt über 171 Objekte hat keine Kontrolle darüber, ob er eines verliert, und `rules/bauweise.md` verlangt für eine unbekannte Eingabe einen harten Fehler statt eines stillen Überspringens. Der Feldschnitt war der Weg der Koordination beim Messen; für die Arbeit taugt er nicht.

**Nicht anzufassen:** die 17 `OFFEN` und die 2 `NEU_STAND`. Letztere braucht ein neues Lemma, und Lemmaanlage ist in diesem Lauf nirgends vorgesehen.

**Zwei Dinge, die an KZW zurückgehen und die Arbeit nicht aufhalten:**

1. Ihre `zusammenfassung` sagt `offen: 7`, gezählt sind **17**. Die Struktur ist in sich stimmig (76 + 17 + 2 = 95), die Arbeitsliste also brauchbar; falsch ist die Zahl in der Zusammenfassung.
2. **Das JSON ist nicht maschinell parsbar.** Bei Zeichen 82.382, mitten im `actions`-Array, steht eine Klartextzeile im Objekt: `"confidence": "high"` gefolgt von `Prüfer: Alan van Beek`. Einmal im ganzen Kommentar. Wie die Spur damit umgeht, steht oben: eine Zeile entfernen, dann strikt parsen. Und sie meldet die Stelle im Ticket, damit KZW und Alan wissen, dass ihr Ausgabeformat eine Handnotiz nicht verträgt.

### Spur B: `pruefseite`

| Paket | Vorgang | Inhalt |
|---|---|---|
| B1 | #443 | Das Basisformat für kuratorische Prüfseiten: eine HTML-Datei, die man verschickt und ohne Installation öffnet. Anforderungen im Body, Alans drei Punkte ebenfalls |
| B2 | #359 | Die Prüfseite für die Verdachtsfälle und Klassifikationskandidaten, gebaut mit B1, mit begründeten Vorschlägen für Pferdebezeichnungen und Gangarten |

**Die Umfangszahlen für B2 stehen hier bewusst nicht.** Sie stammen aus dem Ticketkopf, und bei drei von drei nachgemessenen Datenvorgängen war genau diese Quelle falsch. Spur B misst sie als erste Handlung und meldet sie, bevor sie baut.

### Dateibesitz

| Bereich | Schreiber |
|---|---|
| `tei/`, `authority-files/`, `data/`, `api/`, `scripts/build-*.py`, `scripts/sync/`, `scripts/ingest/` | **Spur A allein** |
| `assets/js/lib/corpus-loader.js`, `docs/TEI-MODEL.md` §11, `docs/INDEX.md` (Versionszeilen) | **Spur A allein**, weil nur sie bumpt |
| Die Fundstellen der **Formenzahl** in `docs/DATA-MODEL.md`, `docs/TEI-MODEL.md`, `docs/TEI-MODEL-AUTH-FILES.md`, `docs/CONTRACTS.md`, `schema/README.md`, `index.html`, `hilfe-daten.html` | **Spur A allein.** Siehe den eigenen Absatz unten |
| `ingest/` | Spur A für `stat`- und `waeren`-Material, Spur B für das Borek-Material unter `ingest/review/359-borek/` |
| `scripts/review/` (Generator der Prüfseite) und die erzeugten Seiten | **Spur B allein** |
| `playground/`, `assets/js/` im Übrigen | Spur B, falls B1 dort andockt; sonst niemand |

**Der Satz für beide Kickoffs:** wer eine Datei außerhalb seines Bereichs ändern muss, ändert sie nicht, sondern meldet es der Koordination.

### Geteilte Dateien und ihre Regel

| Datei | Regel |
|---|---|
| `docs/JOURNAL.md` | anhängend, **als letzter Commit**, unmittelbar nach `git fetch origin` |
| `fehlerjournal.md` | ebenso. Die Zeile nennt die Nummer der letzten Zeile zu derselben Lehre, und die liest die Spur vor dem Schreiben nach |
| `.claude/agent-memory/fable-reviewer/` | **eigene Datei je Spur**, nie eine gemeinsame Reihe. Gemessen am Lauf vom 13./14.09.: drei von vier Spuren hängten an dieselbe Indexzeile an, drei von vier Merges kollidierten, keiner in einer fachlichen Datei |
| `docs/ROADMAP.md` | **niemand.** Eingefroren |

**`git fetch origin` und nicht `merge --ff-only origin/main`.** Die erste Fassung schrieb den Merge vor, und das ist die Regel für den **Hauptbaum** nach einem fremden Merge. Auf einem Spurzweig mit eigenen Commits scheitert ein Fast-Forward, und was die Spur dann tut, um weiterzukommen, hat niemand geplant. Sie holt den Stand und schreibt ihren Eintrag; das Zusammenführen ist Sache der Koordination.

### Freeze

Eingefroren ab Laufbeginn, weil jede Session sie beim Start lädt oder sie den Rahmen des Laufs bildet:

- `CLAUDE.md`
- die 15 promptotyping-Dokumente in `docs/`, **ausgenommen** `docs/JOURNAL.md` (geteilt, siehe oben) und die Versionszeilen in `docs/TEI-MODEL.md` §11 und `docs/INDEX.md`, die Spur A beim Bump ziehen muss
- `docs/playbooks/BETRIEBSVERTRAG.md` und die MASTERPLAN-Dateien
- `.github/workflows/`, `scripts/audit/`

**Die Formenzahl ist eine ausdrückliche Ausnahme vom Freeze, so wie die Versionszeilen.** Ohne sie blockiert sich der Lauf selbst, und zwar nachts um drei: die zehn neuen Typen des Laufs heben die Zahl der Formen in `variants.xml` über die heute dokumentierten 256.773 hinaus, `scripts/audit/doc-count-audit.py --check` prüft genau diese Zahl, und der Aufruf steht in `.github/workflows/data-integrity.yml` Zeile 313. Sie steht heute in **sieben** Dateien, von denen der Freeze vier erfasst und zwei (`index.html`, `hilfe-daten.html`) in der ersten Fassung niemandem gehörten. Abnahmepunkt 4 verlangt zugleich `data-integrity.yml` grün. Spur A stünde also vor einem roten Gate, das sie nur durch Bruch des Freeze grün bekommt.

**Wie weit die Zahl steigt, steht hier bewusst nicht.** Zehn neue Typen heißen rechnerisch zehn neue Formen, aber das ist eine Vorhersage und keine Messung: was in der Datei landet, sagt der Rebuild. Die Spur liest die neue Zahl aus `variants.xml` ab, nachdem `extract-variants.py --apply` gelaufen ist, und zieht sie dann. Weicht sie von der Vorhersage ab, ist das ein Meldepunkt und kein Grund, die abgelesene Zahl zu korrigieren.

Der Handgriff hat einen Präzedenzfall mit fertiger Dateiliste und Trefferzahlen: `scripts/update-variant-count-372376.py`, geschrieben für **+1** im September. Spur A schreibt das Gegenstück und lässt `doc-count-audit.py --check` lokal als Gate laufen. **`docs/JOURNAL.md` ist ausgenommen**, die Zahl steht dort in einem datierten Bericht und ist Geschichte, nicht Bestand.

Nicht betroffen und deshalb nicht zu ziehen: die Zahl der Einträge (42.626, die Lemma-Gruppen bleiben dieselben) und die Zahl der normalisierten Mappings in `CONTRACTS.md` §C (234.245, andere Menge, siehe #279).

**Inbox:** der Abschnitt am Ende dieses Dokuments. Format eines Wunsches: Datei, eindeutiger Ankertext, der **wörtliche** Ersatztext, ein Satz warum. Die Koordination trägt ein, nicht die Spur. **Im Tagbetrieb ist die Inbox kein Wartezimmer**, sondern nur die Ablage: die Spur meldet den Wunsch zusätzlich sofort, und die Koordination trägt ihn im selben Zug ein oder lehnt ihn ab.

**Der Grund für die Konstruktion:** ändert eine Spur eine Datei, die jede Session beim Start lädt, arbeiten die anderen unter geänderten Regeln, ohne es zu merken. Am 01.09.2026 passiert, inhaltlich richtig und auf dem falschen Weg.

**Der Operator ist von diesem Freeze nicht ausgenommen.** Er ist sein häufigster Verletzer, weil er als Einziger den ganzen Lauf über wach ist und Befunde sammelt.

---

## 3. Vorbedingungen, die vor dem ersten Kickoff erfüllt sein müssen

Der Lauf startet nicht, bevor sie alle durch sind. Jede ist billig, und jede kostet hinterher ein Vielfaches.

1. ~~**Der Zweig `claude/auto-frozen-label` ist gemergt.**~~ **Erledigt am 21.09., Merge-Commit `1e75c6002`.** Er ändert `CLAUDE.md`, und ein Merge mitten im Freeze hätte allen Spuren den Boden weggezogen.
2. ~~**`auto:frozen` ist angelegt, #271 trägt es, `--apply` ist gelaufen.**~~ **Erledigt am 21.09., in dieser Reihenfolge.** Gegengeprüft: #271 steht genau einmal im Body von #44, in seiner eigenen Tabelle, und ist aus KZWs Ping-Liste verschwunden (dort jetzt 26 Einträge). Die handgeschriebene Legende in #44 ist mitgezogen.
3. **Der Freeze steht committet und gepusht auf `main`.** Committet ist die gemessene Bedingung: `--worktree` legt den Baum aus einem **Commit** an, nicht aus dem Arbeitsbaum, und ein Freeze, der nur im Arbeitsbaum steht, erreicht keine Spur. Ob der Baum vom lokalen oder vom Remote-Stand abzweigt, ist **nicht** gemessen; gepusht wird trotzdem, weil es nichts kostet und die Frage damit nicht gestellt werden muss.
4. **Die Hashes der geteilten Betriebsmittel außerhalb des Projekts sind festgehalten** (`~/.claude/rules/`, `~/.claude/agents/`, `~/.claude/hooks/`, persönliche Skills). Was per Junction in `claude-code-setup` zeigt, über dessen Commit. Das Skript dafür schreibt die Koordination vor dem Start und legt es neben dieses Dokument, damit die Gegenprobe bei der Abnahme dieselbe Messung ist und keine zweite.
5. **`gh pr list` ist gelaufen und die höchste dort beanspruchte Indexversion notiert.** Spur A bumpt auf die nächste darüber, nicht auf die nächste über `main`.
6. **In jedem Worktree läuft `npm ci`**, bevor die Spur ihn benutzt. Ein frischer Baum hat kein `node_modules`, und `npm test` scheitert dort mit einer Meldung, die nach einem Testfehler aussieht.
7. ~~**Der Hauptbaum steht auf `main` und ist auf `origin/main` gezogen**, bevor der erste Worktree abzweigt.~~ **Erledigt am 21.09.**, er stand bis dahin auf dem Zweig von #455. Vor dem Start erneut prüfen, weil andere Sitzungen denselben Baum benutzen.
8. **Port 8080 ist ein exklusives Betriebsmittel, und der Dev-Server ist der eigentliche Fall.** Die erste Fassung begründete das mit Phantomfehlern, und das ist falsch: `scripts/run-tests.js` erkennt einen fremden Server auf 8080 und bricht mit einer klaren Meldung ab. Die Regel bleibt trotzdem, aber aus dem anderen Grund: ein **dauerhaft laufender** `npm run serve`, mit dem Spur B ihre Prüfseite ansieht, sperrt jeden Testlauf von Spur A für die ganze Zeit. Regel: Spur A hat Vorrang, Spur B fährt ihren Dev-Server nur für die Dauer einer Ansicht und meldet Beginn und Ende.
9. **`--allow-dirty` gehört in den Kickoff von Spur A.** Alle drei Builds verweigern einen unsauberen Baum, der Data-Change-Lifecycle verlangt aber den gemeinsamen Commit von TEI, Indexen und `api/`. Steht das nicht im Auftrag, liest die Spur „commit or stash the changes above" und greift zu `stash`: das hat in diesem Projekt schon einmal Arbeit gekostet.
10. **Die Fehlerjournal-Nummern werden vorab vergeben**, Spur A 40 bis 44, Spur B 45 bis 49. `fehlerjournal.md` nummeriert fortlaufend und steht heute bei 39; zwei Spuren, die beide „die nächste" schreiben, kollidieren an der Nummer, und der Rückverweis auf die letzte Zeile derselben Lehre wird für beide falsch.

---

## 4. Start

Beide Spuren startet die Koordination, **ohne Prompt**, und schickt den Kickoff als erste Nachricht:

```
claude --bg --worktree mhdbdb-daten      --name mhdbdb-daten
claude --bg --worktree mhdbdb-pruefseite --name mhdbdb-pruefseite
```

`--worktree` ist nicht optional: drei von drei Spuren ohne das Flag liefen am 13.09.2026 in eine Ablehnung und legten sich selbst einen Baum an. Der Name gehört in den Startbefehl, weil nachbenennen nur ein Mensch am Terminal der Session kann.

**Adressiert wird über die Kennung aus `ListAgents`**, nicht über die ID aus `claude --bg`. Zwei Kennungsräume, die gleich aussehen.

---

## 5. Was in jeden der beiden Kickoff-Texte gehört

Gegen die Prüfliste des Skills, **je Auftrag einzeln** gehalten, nicht einmal für den Lauf. Ein Baustein darf entfallen, aber nicht stillschweigend: dann steht die Feststellung unter ihrem Gegenstand im Auftrag, nicht unter ihrer Nummer.

1. **Autorisierung:** chsteiner hat am 21.09.2026 diesen Lauf freigegeben, dieser Text ist die Autorisierung, und er erteilt keine technische Berechtigung.
2. **Adressierung:** an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text.
3. **Lese-Anordnung vor jeder Handlung**, nummeriert: `CLAUDE.md`, `docs/playbooks/BETRIEBSVERTRAG.md`, der eigene Vorgang **mit allen Kommentaren** (`gh issue view N --json title,body,comments`), `docs/DATA-MODEL.md` → Data-Change-Lifecycle (nur Spur A). Abbruchklausel: weicht etwas davon von diesem Auftrag ab, gilt die Datei und der Auftrag ist falsch.
4. **Worktree:** wörtlicher Pfad und Zweig, dazu die Aufforderung, `pwd` zu messen, gegen den genannten Baum zu halten und samt Zweig und HEAD zu melden; bei Abweichung nichts ändern, melden, auf Neustart warten.
5. **Was dieser Spur gehört:** die Dateiliste aus Abschnitt 2, der Satz über fremde Dateien, die untersagten über den Baum hinaus wirkenden Befehle, und **der Satz, dass ein fehlender vorgeschriebener Agententyp ein Halt ist und kein Weiter** (`fable-reviewer` fehlte am 02.09. zweimal).
6. **Was eingefroren ist:** die Liste, die Inbox, das Format eines Änderungswunsches, der Grund.
7. **Die Pakete** nummeriert, in fester Reihenfolge, Reihenfolge begründet, je Paket **was entschieden ist gegen was nachzumessen ist**, keine Labelabfrage als Arbeitsgrundlage, und der Satz, dass der ganze Auftragstext eine Behauptung ist. Für Spur A dazu die Messskripte der Koordination, damit sie nachmisst statt neu zu erfinden.
8. **Vorab entschieden, nicht neu zu verhandeln:** die Antworten aus Abschnitt 6. Widerspruch ist ausdrücklich erlaubt und geht an die Koordination, die ihn in dieses Dokument einträgt.
9. **Melde- und Haltepunkte:** siehe Abschnitt 7.
10. **Abschluss:** Journaleintrag als letzter Commit nach `git fetch origin`, `fable-reviewer` vor dem ersten Push mit Angabe, ob Commit oder Arbeitsbaum geprüft wird, zweite Runde bei Befunden, Gegenstand still halten solange sie läuft, **die Frage aus #397 mitgeben** (was hat diese Änderung wahr gemacht, das vorher falsch sein konnte), Bericht an die Koordination.

**Und je Vorgang, den die Spur anfasst: relabeln in derselben Session, plus ein Statuskommentar im Ticket.** Das hält die Matrix aktuell, und es ist der Punkt, an dem die alte Labelordnung verrottet ist.

---

## 6. Vorab entschieden (chsteiner, 21.09.2026)

Diese vier werden nicht neu verhandelt. Wer sie für falsch hält, sagt es, arbeitet aber danach weiter.

| Frage | Entscheidung | Begründung |
|---|---|---|
| Zuschnitt | zwei Spuren, Daten sequenziell | siehe Abschnitt 2 |
| Neue Variantentypen | **prägen**, zehn Stück: sieben in A1 (`type_372377` bis `_383`), drei in A3 (`type_372384` bis `_386`) | Präzedenz #367 (Authority 1.9.2) und #363 (1.9.4). Die Regel lautet nicht „nie prägen", sondern: umgehängt wird nur, wo korpusweit ausschließlich Tokens der wandernden Menge den Typ tragen. Hier wird nichts umgehängt, weil alle 76 Tokens heute ohne `@lemmaRef` dastehen |
| #359 | **#443 zuerst**, #359 als erste Anwendung | KZW verlangt es wörtlich („Bitte hierzu auch #443 berücksichtigen"), Alans Anforderungen liegen vor, und es wäre sonst die vierte Einzelseite, gegen die #443 geschrieben wurde |
| Merge | **nein**, PR aufmachen und melden | `CLAUDE.md`: kein Commit und kein Push ohne Freigabe. An beiden PRs hängt KZWs Abnahme |

**Eine Vorgabe, die die Koordination selbst für schwach hält, samt Ersatzfassung:** die Reihenfolge A1 → A2 → A3 ist nach berührten Dateien begründet, aber A3 ist mit 37 Dateien und drei Typprägungen das mit Abstand größte Paket und könnte die Nacht allein füllen. Ersatzfassung, falls die Spur nach dem Messen zu diesem Schluss kommt: A3 zuerst, A1 und A2 hinterher, mit demselben einen Bump am Ende. Was **nicht** zur Disposition steht, ist der eine gemeinsame Rebuild.

**Abbruchregel für A3.** Die erste Fassung sagte „nach der Hälfte der Zeit" und war nicht ausführbar, weil kein Zeitbudget im Plan stand. Im Tagbetrieb braucht sie keines: **die Spur meldet, sobald sie absehen kann, dass A3 nicht durchläuft, und die Koordination entscheidet.** Das ist billiger als jede Schwelle und genauer, weil ein Mensch den Grund kennt.

Was die Regel dennoch festlegt, weil es keine Ermessensfrage ist: bei Abbruch nimmt die Spur die gesetzten Tokens **nicht** zurück, sondern meldet den Stand und schließt mit Rebuild ab. Ein halbes A3 ist regenerationstechnisch harmlos, und zwar aus einem Grund, der nur für diesen Lauf gilt: es wird **nichts umgehängt**, weil alle 76 Tokens heute ohne `@lemmaRef` dastehen. Die Mehrheitsregel in `extract-variants.py` kann bei einem Teilstand deshalb keinen bestehenden Eintrag umschreiben; die Tokens auf bestehenden Nummern erhöhen nur Zähler eines Paars, das ohnehin gewinnt.

**Zwei Dinge gehören trotzdem zum Abbruch:**

1. Der Statuskommentar an #371 führt die **nicht** gesetzten Token-IDs mit Namen auf, nicht „36 von 76". Eine Anzahl lässt sich nicht falsifizieren, eine Namensliste schon.
2. Die Typnummern samt Paarzuordnung stehen **vor** dem ersten Token im PR-Text und in `ingest/`. Sonst prägt die Fortsetzung eine elfte.

---

## 7. Melde- und Haltepunkte

**Meldepunkte** (Spur meldet, arbeitet weiter):

- nach dem Lesen: gemessenes `pwd`, Zweig, HEAD, Vergleich mit dem erwarteten Baum
- je Paket: der **nachgemessene** Umfang gegen den im Auftrag behaupteten
- Beginn und Ergebnis jeder Reviewrunde, mit Rundennummer **und der Kennung des geprüften Standes**
- vor dem Versions-Bump (nur Spur A): die beanspruchten Nummern
- Beginn und Ende jedes Dev-Server-Laufs (nur Spur B): siehe Port 8080 in den Vorbedingungen

**Haltepunkte** (Spur hält an und wartet):

- `pwd` weicht vom erwarteten Baum ab
- ein Paket würde eine Datei außerhalb des eigenen Bereichs ändern
- eine Stoppbedingung aus Abschnitt 2 tritt ein
- der vorgeschriebene Agententyp fehlt
- **Spur A: eine Entscheidung wäre nötig, die KZW nicht getroffen hat.** Nicht schätzen, nicht aus dem Ticketkopf ableiten. Der hirne-Auftrag aus A1 ist der bereits bekannte Fall

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Das Werkzeug steht in keiner Werkzeugliste und lädt über `ToolSearch` mit `select:PushNotification`. Eine Blockade wird **nicht** über die andere Spur umgangen: Berechtigungen gelten je Session. Siehe `rules/blockaden-melden.md`.

**Kein Messfenster nötig:** keines der fünf Pakete misst eine Bedingung, die vom Zustand des eigenen Prozesses abhängt. Deshalb entfällt die Funkstille-Zusage, und die Koordination darf jederzeit rückfragen.

---

## 8. Betrieb: die zwei Listen

Die Koordination führt sie **als Datei**, nicht im Gedächtnis, weil eine Verdichtung sie sonst frisst.

**Liste 1, laufende Spuren:** je Spur, worauf sie gerade wartet. Kein Worktree wird abgebaut, solange die Spur als Prozess in ihm steht. Eine Fertigmeldung ist eine Aussage über die Arbeit, die Quittung von `claude stop` eine über den Prozess, und abgebaut wird gegen die zweite. `ListAgents` taugt dafür nicht.

**Liste 2, offene Prüfungen:** nach `main` geht nur, wofür ein Prüfergebnis für **genau diesen Stand** vorliegt. Der Eintrag trägt die Kennung, nicht nur Spur und Rundennummer. **Ein unaufgefordert gemeldeter Befund kommt in diese Liste, bevor die Koordination ihn bewertet.**

**Ein Satz, der über den einzelnen Befund hinausgeht, geht vor dem Eintragen an die Spur zurück, aus deren Messung er stammt.** Verboten ist nicht das Verdichten, sondern das Eintragen ohne den Rückweg.

**Keine Operatorzahl in einen Ticketkommentar oder ins JOURNAL, bevor eine geprüfte Fassung existiert.** Die Arbeit der Koordination geht durch keinen Review, und das ist der einzige Hebel, der auch dort greift, wo es keinen Empfänger gibt, der widersprechen könnte.

---

## 9. Abnahme

1. Beide Spuren haben ihren Journaleintrag geschrieben, **die Koordination ihren zuerst**.
2. Für jeden PR liegt ein `fable-reviewer`-Ergebnis für den gepushten Stand vor, und die Kennung im Ergebnis stimmt mit dem gepushten HEAD überein.
3. `npm test` grün, und das Ergebnis ist die VERDICT-Zeile, nicht die Konsolenzusammenfassung und nicht der Exit-Code.
4. Auf dem Daten-PR: `data-integrity.yml` grün, `check-index-version-bump.py` grün, `check-no-em-dash.py --diff-base main` grün, und der rote `claude-review`-Haken ist **geöffnet und gelesen**, bevor er abgetan wird. Zwei von vier Läufen waren fertige Reviews mit Befunden, die die Action nur verworfen hat.
5. Die Data-Change-Lifecycle-Kette ist vollständig gelaufen: `extract-variants.py --apply`, beide Indexe, `build-api.py`, Versions-Bump an allen fünf Stellen.
6. Die Hashes der Betriebsmittel aus Vorbedingung 4 sind mit demselben Skript gegengeprüft, mit dem sie erhoben wurden.
7. Jeder angefasste Vorgang ist relabelt und trägt einen Statuskommentar.
8. Die Inbox ist abgearbeitet, insbesondere `CONTRACTS.md` §C.
9. Worktrees abgebaut gegen die Quittung von `claude stop`, dann `rm`. Bleibt ein Zweig liegen, wird er benannt und nicht stillschweigend gelöscht.
10. Ist der Lauf von diesem Plan abgewichen: ein Issue in `claude-code-setup`.

---

## 10. Was dieser Lauf nicht tut

- **#443 nicht abschließen.** B1 baut die Vorlage so weit, wie #359 sie braucht. Ob sie das Basisformat für alle künftigen Seiten wird, entscheidet KZW nach dem ersten Gebrauch.
- **Die 17 `OFFEN` und die 2 `NEU_STAND` aus #371 nicht anfassen.** Letztere brauchen ein neues Lemma, und Lemmaanlage kommt in diesem Lauf nirgends vor.
- **Den hirne-Punkt aus #366 nicht ausführen**, sondern messen und zurückfragen.
- **Kein Ticket schließen.** Ein `Closes` ist keine Abnahme, und an allen vier hängt KZWs Prüfung.
- **Nichts an #237, #364, #115, #252.** Die liegen bei KZW, und dieser Lauf rührt sie nicht an.

---

## Änderungswünsche an eingefrorene Dateien

1. **`docs/CONTRACTS.md` §C, Variantenzahlen.** Sie altern mit dem Rebuild dieses Laufs. Nach dem Lauf von der Koordination gegen den dann gemessenen Stand zu ziehen, mit der Messvorschrift daneben. Eingetragen vor Laufbeginn, damit unterwegs niemand meint, es sei eine Kleinigkeit.

## Grenzverhandlungen während des Laufs

*(leer bei Laufbeginn)*
