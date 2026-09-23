# Laufplan 23.09.2026: Issue-Abbau nach Vollaudit

**Protokoll, keine Vorlage.** Der Plan altert ab dem Tag des Laufs; wer ihn als Vorlage nimmt, misst jede Angabe neu.

**Tagbetrieb, Christian erreichbar.** Freigaben von chsteiner am 23.09.2026: `auto:checkin` für diesen Lauf (Haltepunkte über die Koordination an ihn), PRs öffnen und melden, **Christian merged**, Statuskommentare der Spuren direkt (höchstens einer je Ticket), Entwürfe an KZW und Externe über seine Freigabe. Vor dem Freeze erledigt: #466 (Satz in `CLAUDE.md`), Labelkorrekturen an #467, #18, #27, #464, #252, #58, #59 geschlossen.

**Grundlage:** ein Audit aller 90 offenen Vorgänge (ohne #44) mit Body und allen 372 Kommentaren, Stand 23.09. vormittags, `origin/main` = `da6316804`, sieben Subagenten, danach ein Planreview durch `fable-advisor`. **Was mit „gemessen (K)" markiert ist, hat die Koordination selbst am Bestand oder am Thread nachgeprüft; alles andere ist aus den Berichten übernommen und ungeprüft.** Jede Spur misst jede Angabe nach, bevor sie sie verwendet, und widerspricht, wenn sie abweicht. Der ganze Auftragstext ist eine Behauptung.

---

## 1. Was das Audit ergeben hat

1. **Durchentschiedene Datenarbeit liegt seit bis zu zwei Wochen.** #387 (21 Resttokens, KZW 17.09.), #418 (12 offene Belege, KZW 11.09.), #228 (KZW 11.09.), #267 (KZW 10.09.), #464 (KZW 22.09.), #252 (KZW 22.09.): alle an den Threads gemessen (K) entschieden. #267 gemessen (K) unumgesetzt: `n="excerpt-only"` steht in 10 Dateien.
2. **Mehrere Vorgänge führten `wait:kzw`, obwohl KZW geantwortet hat oder wir ihr etwas schulden:** #464, #252, #58 (gemessen (K), Labels am 23.09. korrigiert), dazu #147 (Besprechungsliste, erbeten am 10.07., gemessen (K)), #28 (ihre Frage vom 17.09. „Welche konkrete unbeantwortete Frage blockiert dich derzeit?", gemessen (K)), #423 (crawlen oder WordPress-Export, 10.09., gemessen (K)), #251, #452, #138.
3. **Port 8080 ist fest verdrahtet:** gemessen (K) 135 Vorkommen in 31 Dateien unter `testing/`, dazu `scripts/run-tests.js` und `package.json`. Immer nur ein Worktree kann testen (#465).
4. **Ein Datenschreiber zur Zeit**, unverändert seit dem 01.09.: `variants.xml`, beide Indexe, `api/`, Versionsliterale sind Funktionen des ganzen Korpus. Stand gemessen (K): Korpus 4.2.18, Authority 1.9.8, `check-index-versions.py` exit 0; `doc-count-audit.py --check` exit 0 auf `main`.
5. **Tag-Reihenfolge im Bestand, gemessen (K) über `tei/`:** `pos="NOM ADJ"` 119.501-mal, `pos="ADJ NOM"` 0-mal; `pos="PRO VRB"` 9.068-mal, `pos="VRB PRO"` 154-mal. `@reason` an `<w>` ist im Korpus in Gebrauch (z. B. ABS 63, AC1 55).

## 2. Zuschnitt: drei Spuren, dazu Subagenten der Koordination

**Parallel läuft die Session „KZW PR fix"** an PR #469 im Worktree `../mhdbdb-wt-469`. Sie ändert `docs/INDEX.md`, `docs/JOURNAL.md` (gepusht), `docs/DEVELOPMENT.md` und `scripts/README.md` (uncommittet). **Keine Spur und nicht die Koordination schreibt in diesem Lauf `docs/DEVELOPMENT.md` oder `scripts/README.md`**; Wortlaut dafür geht an die Inbox und wird nach dem Merge von #469 eingetragen. Spur A berührt `docs/INDEX.md` nur in der Versionszeile (Z. 111), und das wird der „KZW PR fix"-Session angesagt, zusammen mit der Bitte, Test- und Serverläufe auf Port 8080 vorher zu melden. Ein JOURNAL-Konflikt beim Merge wird durch Komposition gelöst (gemeinsamen Präfix stehen lassen, Suffixe anhängen), nicht durch Auswahl.

### Spur A `mhdbdb-daten2`: einziger Datenschreiber, seriell

| Welle | Vorgänge | Inhalt | PR |
|---|---|---|---|
| A1 | #387, #418, #464 | Annotationen nach KZWs Entscheidungen (Einzelheiten unten) | PR 1, ein Rebuild, Bump auf 4.2.19 / 1.9.9 |
| A2 | #267, #252 | Header-Marker und Lückenkodierung (Einzelheiten unten) | PR 2, erst nach Merge von PR 1, frisch von `origin/main`; Bump nur, wenn der Rebuild eine Differenz zeigt |
| A3 | #228 | 530 Notes entannotieren, 170 Lemmalöschungen (Zahlen aus #228 K13, ungeprüft). **Nur wenn A1 und A2 durch sind**, sonst nächster Lauf | PR 3 |

**A1 im Einzelnen.**
- **#387:** alle 21 Tokens laut KZWs Tabellen vom 17.09. (13 unter `lemma_7250`, 8 Restfälle auf `lemma_7256`, `lemma_7250`, `lemma_7260`). **Das Doppeltag wird in der Bestandsreihenfolge `NOM ADJ` geschrieben**, nicht als neue Zeichenkette `ADJ NOM` (siehe §1 Punkt 5); der Statuskommentar sagt KZW das ausdrücklich als Reihenfolgekonvention, nicht als Abweichung in der Sache. Der „erklärende Kommentar" steht als `@reason` am `<w>`. Die Konvention für substantivierte Adjektive kommt als neuer Absatz nach `docs/POS-TAGSET.md` (Freeze-Ausnahme). Neuer Variantentyp für `vrow̆e` unter `lemma_7260` (freigegeben von KZW), nächste freie Nummer über `type_372386` nachmessen.
- **#418:** 12 offene Belege (7 → `lemma_2923`, 3 → `lemma_9644_sense_15624`, 2 → neuer Sense an `lemma_9644` mit den Konzepten aus `lemma_2923_sense_4697`); `AC3_23010_1` ist seit #416 erledigt. Nach der Regel aus #367: neue Typnummer statt Umhängen. **Liefert zusätzlich** die Messung „Typ-IDs mit mehr als einem Lemma" (`extract-variants.py` ohne `--apply`) in die Statuskommentare an #418 und #416, wie in #418 K11 zugesagt.
- **#464:** `@pos` von `PRO VRB` auf `VRB PRO` (KZW 22.09.; POS-TAGSET kodiert Verb plus Enklitikon als `VRB PRO`, ungeprüft), `@reason` mit der Verschmelzung, keine Token-Trennung. `etym` in `lexicon.xml` auf `zeln` + `er` umstellen, wie KZW es erwartet. **Haltepunkt nur**, wenn die bestehende `etym`-Struktur dabei eine Verknüpfung verlöre.

**A2 im Einzelnen.**
- **#267:** neun Header: Marker `excerpt-only` → `no-print`, Satz „Eine vollständige Fassung der Edition inkl. Apparat kann daher nicht angeboten werden." FR3: Marker entfernen. **Haltepunkt vor jeder Änderung an `availability/@status` und dem Beschränkungssatz in FR3**, das ist nicht entschieden; Vorschlag der Spur beilegen. `docs/RESEARCH.md` ist erledigt (Melichar steht dort, gemessen (K)) und wird nicht angefasst. Die Bedeutung von `no-print` kommt nach `docs/TEI-MODEL.md` (Freeze-Ausnahme); `sources/README.md` Z. 183 zieht mit.
- **#252:** nur das Muster `( caesura )` → `<gap/>`, umgebender Text sowie Satz- und Redezeichen bleiben (KZW 22.09.). Freigegeben sind **die genannten 846** nach der Zählvorschrift in #252 vom 14.09. Weicht die Zahl ab, meldet die Spur die **xml:ids** der Differenz, nicht die Anzahl, und fasst die zusätzlichen nicht an. **Die fünf Komma- und Doppelpunktfälle sind nicht freigegeben**; die Kontextliste dazu, die KZW angemahnt hat, baut die Spur als ersten Schritt von A2 und liefert sie als Entwurf an die Koordination. `docs/TEI-MODEL.md` §6.5a (Resttabelle) zieht mit (Freeze-Ausnahme).

**A3 im Einzelnen, falls es läuft:** Haltepunkt vor jedem Eingriff in `tei/NEIM.tei.xml`: die 39 `<note n>` dort tragen die Konkordanz Lied zu Hs. C, die #453 sichern will (Audit A3, ungeprüft). Zählstelle `lexicon_entries` zieht mit (siehe §3).

**Reihenfolge begründet:** A1 klein, voll entschieden, prägt Typ und Sense nach bekannten Mustern (#366, #371). A2 strukturell ohne Lemmaarbeit, braucht aber den Stand nach A1. A3 ist das größte Paket und hat eine offene Kollision.

**Stoppbedingungen (A):** ein Token, dessen Ist-Zustand nicht dem Thread entspricht; eine Entscheidung, die KZW nicht getroffen hat; eine Datei außerhalb des eigenen Bereichs.

### Spur B `mhdbdb-playground`: Frontend und Playground, keine Daten

| Paket | Vorgang | Inhalt |
|---|---|---|
| B1 | #58 | KZW heute 08:46: „Die Zahl stimmt jetzt, aber ich kann immer noch nicht weiterklicken zu den Belegen." **Vorrang** |
| B2 | #435 | Tippfilter im Textvergleich; ihre Frage zur Begriffs-Verteilung beantworten (Autocomplete seit `a2e7b0b36`, #113, laut Audit) |
| B3 | #433 | Gattungen in die Suche bis zum Haltepunkt „Chip"; KZWs „achte darauf, ob das eh klappt" (Untergattungen) zuerst im Browser prüfen |
| B4 | #446 | „das Korpus" nur in nutzersichtbarem Text (Umfang von Christian am 23.09. bestätigt) |

**Bestehende Specs:** B ändert bis zum Merge von Spur C nur Produktcode und **neue** Specs (mit relativen Pfaden gegen `baseURL`, nie `localhost:8080`). Muss eine bestehende Spec geändert werden (wahrscheinlich `lemma-occurrence-handoff.spec.js` für B1, `main-site.spec.js` für B3), wartet B auf den Merge von C, holt `origin/main` und ändert dann.

### Spur C `mhdbdb-testport`: #465

Port für `npm test` und `npm run serve` konfigurierbar (Umgebungsvariable, Vorgabe 8080), alle hart verdrahteten `localhost:8080` in `testing/` auf `baseURL` bzw. die Variable, `run-tests.js` erkennt den eigenen Server am konfigurierten Port. Mechanisch, Ziel unter zwei Stunden, PR, Christian merged zuerst. Abnahmeprobe: zwei Testläufe auf verschiedenen Ports gleichzeitig, beide mit VERDICT. **Doku nach `docs/DEVELOPMENT.md` nur als Inbox-Wortlaut.**

### Koordination: Subagenten statt einer vierten Spur

Entwürfe an KZW und Externe, als Subagenten der Koordination (Planreview: nur Ergebnisse sammeln, keine Spur nötig), Ablage im Scratchpad der Koordination, **Posten erst nach Christians Freigabe**:
#406 Triage-Nachtrag · #147 Besprechungsliste für Silvan · #452 Quellenprüfung plus Vorschlag Zuschreibungsstatus (#444 K1/K2) · #251 Prüfweg · #262 Hinweis auf `sources/archiv-inventar.csv` (`apk_free.xml`) · #123 Rückfrage (KVO steht im Korpus) · #419 Alan-Zusammenfassung, Asterisk-Vorlage · #410 Formulierungsvorschlag · #138 was KZWs „stimme zu" vom 28.07. deckt · #28 Antwort auf ihre Frage vom 17.09. plus Vorprüfung der 26 belegstärksten Lemmata (nur lesen) · #423 Antwort crawlen oder Export.

## 3. Dateibesitz

| Bereich | Schreiber |
|---|---|
| `tei/`, `authority-files/`, `data/`, `api/`, `scripts/build-*.py`, `scripts/sync/`, `scripts/ingest/`, `ingest/` | **A** |
| Versionsliterale: `build-corpus-index.py`, `build-authority-index.py`, `assets/js/lib/corpus-loader.js`, `docs/TEI-MODEL.md` §11, `docs/INDEX.md` Z. 111 | **A** |
| `docs/POS-TAGSET.md` (neuer Absatz zu #387), `docs/TEI-MODEL.md` (`no-print`-Bedeutung, §6.5a), `sources/README.md` Z. 183 | **A**, Freeze-Ausnahme, nur diese Stellen |
| **Die von `doc-count-audit.py` gegateten Zahlzeilen** (`variants_forms`, `variants_normalized`, bei A3 `lexicon_entries`) in `index.html`, `hilfe-daten.html`, `hilfe-daten-beitragen.html`, `hilfe-korpussuche.html`, `hilfe-playground.html`, `playground/index.html`, `docs/DATA-MODEL.md`, `docs/TEI-MODEL.md`, `docs/TEI-MODEL-AUTH-FILES.md`, `docs/CONTRACTS.md`, `schema/README.md`, `README.md` | **A allein, zeilengenau.** Bewusste Abweichung von „eine Datei, ein Schreiber": das Gate läuft auf A's PR und prüft Dateien mit, die sonst B gehören. B fasst diese Zeilen nicht an. Die Stellen liefert `doc-count-audit.py` selbst, A misst sie vor dem Zug |
| `playground/`, `assets/js/` (außer `corpus-loader.js`), `index.html`, `korpus.html`, `hilfe-*.html`, `assets/css/`, neue Specs unter `testing/tests/` | **B** (außer den Zahlzeilen oben) |
| `scripts/run-tests.js`, `testing/playwright.config.js`, `package.json`, bestehende Dateien unter `testing/` | **C** (B nach C's Merge, siehe oben) |

**Der Satz für alle Kickoffs:** wer eine Datei außerhalb seines Bereichs ändern müsste, ändert sie nicht, sondern meldet es der Koordination.

### Geteilte Dateien

| Datei | Regel |
|---|---|
| `docs/JOURNAL.md` | anhängend, **letzter Commit**, unmittelbar nach `git fetch origin` |
| `fehlerjournal.md` | ebenso. Nummern vorab vergeben, letzte am 23.09. ist 65 (gemessen (K)): **A 66–69, B 70–72, C 73–74, Koordination 75–79**. Die Zeile nennt die Nummer der letzten Zeile derselben Lehre |
| `.claude/agent-memory/fable-reviewer/` | eigene Datei je Spur, nie eine gemeinsame Reihe; als eigener Commit nach der Runde |
| `docs/ROADMAP.md` | niemand |

## 4. Freeze

**Scharf ab dem Commit, der diesen Plan einführt, und vor dem ersten Kickoff gepusht.** Eingefroren: `CLAUDE.md`; die 15 promptotyping-Dokumente in `docs/` mit den Ausnahmen aus §3 (Versionszeilen, Zahlzeilen, die drei A-Stellen) und `docs/JOURNAL.md` (geteilt); `docs/playbooks/` außer diesem Plan; `.github/workflows/`; `scripts/audit/`; **zusätzlich `docs/DEVELOPMENT.md` und `scripts/README.md` wegen #469**, auch für die Koordination.

**Inbox:** der Abschnitt am Ende dieses Plans. Format: Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum. Die Koordination trägt ein. Im Tagbetrieb ist die Inbox kein Wartezimmer: die Spur meldet sofort, die Koordination entscheidet im selben Zug.

**Grund:** ändert eine Spur eine Datei, die jede Session beim Start lädt, arbeiten die anderen unter geänderten Regeln, ohne es zu merken (01.09.2026). **Die Koordination ist davon nicht ausgenommen**; sie ist der häufigste Verletzer.

**Globale Betriebsmittel:** festgehalten mit `.claude/tmp/betriebsmittel-hash-2026-09-23.py` (Hauptbaum, gitignoriert, unverändert aus dem Lauf vom 21.09. bis auf Datum), Ablage `.claude/tmp/betriebsmittel-2026-09-23.json`. `claude-code-setup` beim Start: `98c82a51b`, Arbeitsbaum sauber. Gegenprobe bei der Abnahme mit `--pruefe`.

## 5. Betriebsmittel

- **Port 8080: Warteschlange über die Koordination.** Anfordern, testen, freimelden. Vorrang A vor C vor B. Kein dauerhaft laufender Dev-Server. Nach C's Merge fällt die Warteschlange für Spuren weg, die C's Port-Variable benutzen.
- **Indexversionen:** allein A. PR 1: 4.2.19 / 1.9.9. Vor dem Bump `gh pr list` auf beanspruchte Nummern prüfen.
- **`--allow-dirty`** gehört in A's Kickoff: die Builds verweigern einen unsauberen Baum, der Lifecycle verlangt den gemeinsamen Commit.
- **`npm ci`** in jedem Worktree vor der ersten Benutzung.
- **`fable-reviewer`** vor jedem ersten Push, Pflicht. Ein fehlender Agententyp ist ein Halt, kein Weiter.
- **Nicht über den Baum hinaus:** kein `git gc`, `git worktree prune`, keine Tags, keine fremden Zweige, kein Force-Push auf fremde Historie, keine Änderung unter `~/.claude/`.

## 6. Vorab entschieden, nicht neu zu verhandeln

| Frage | Entscheidung | Grund |
|---|---|---|
| Zuschnitt | drei Spuren, Daten seriell in A | abgeleitete Schicht, §1 Punkt 4 |
| Tag-Reihenfolge #387 | `NOM ADJ` | Bestand 119.501 zu 0, §1 Punkt 5 |
| Kommentarform #387/#464 | `@reason` | im Korpus eingeführt, einziger Freitextplatz an `<w>` |
| Neue Variantentypen | prägen, nie umhängen | Regel aus #367, mehrfach angewandt |
| Merge | Christian | Freigabe vom 23.09. |
| Tickets schließen | keines | ein `Closes` ist keine Abnahme |
| Relabel | in derselben Session, plus höchstens ein Statuskommentar je Vorgang | Matrix |

**Widerspruch ist erlaubt**, auch gegen diese Tabelle, und geht an die Koordination, die ihn unter „Grenzverhandlungen" einträgt.

**Eine Vorgabe, die die Koordination selbst für schwach hält, mit Ersatzfassung:** die Reihenfolge B1 → B4 stellt #58 vorn, weil es KZWs jüngste Meldung ist. Braucht B1 eine bestehende Spec und muss deshalb auf C warten, darf B mit B2 oder B4 vorziehen.

## 7. Melde- und Haltepunkte

**Melden, weiterarbeiten:** `pwd`, Zweig, HEAD nach dem Lesen; je Paket der nachgemessene Umfang gegen den behaupteten; Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes; Port angefordert und frei; vor dem Bump die beanspruchten Nummern (A).

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; Stoppbedingung; fehlender Agententyp; eine Entscheidung, die KZW nicht getroffen hat; die benannten Haltepunkte (#464 `etym`, FR3 `availability`, NEIM-Notes, B3 „Chip").

**Externer Zustand (CI, `gh pr checks`):** nicht blind warten, sondern mit `Monitor` oder einem Hintergrundbefehl, der beim Eintreten weckt. Auf einem PR mit leeren Checks zuerst `gh pr view N --json mergeable`.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian (laden mit `ToolSearch` `select:PushNotification`), mit dem, was blockiert wurde und woran es hängt. Nicht über eine andere Spur umgehen. `rules/blockaden-melden.md`.

**Kein Messfenster:** kein Paket misst eine Bedingung des eigenen Prozesses; die Koordination darf jederzeit fragen.

**Ein Paket darf für nicht durchführbar erklärt werden**, mit Messung und früh.

## 8. Abnahme

1. Journaleinträge aller Spuren, **der der Koordination zuerst**.
2. Je PR ein `fable-reviewer`-Ergebnis für den gepushten Stand, Kennung stimmt mit HEAD.
3. `npm test` mit VERDICT-Zeile.
4. Daten-PRs: `data-integrity.yml`, `check-index-version-bump.py`, `check-no-em-dash.py --diff-base main`, `doc-count-audit.py --check` grün; roter `claude-review`-Haken geöffnet und gelesen.
5. Lifecycle vollständig: `extract-variants.py --apply`, beide Indexe, `build-api.py`, Bump an allen fünf Stellen.
6. Betriebsmittel-Gegenprobe mit `--pruefe`.
7. Jeder angefasste Vorgang relabelt, Statuskommentar, `build-issue-matrix.py --check` grün.
8. Inbox abgearbeitet (nach dem Merge von #469 für `docs/DEVELOPMENT.md`).
9. Worktrees abgebaut gegen die Quittung von `claude stop`, Agent-Memory vorher gerettet; liegenbleibende Zweige benannt.
10. Abweichungen vom Plan: Issue in `claude-code-setup`.

## 9. Was dieser Lauf nicht tut

- **#378/#370:** Build-Änderung nach ADR-021, berührt die abgeleitete Schicht; nächster Datenlauf.
- **#453** und NEIM-Notes: nichts an NEIM vor Klärung.
- **#420/#412:** `naming-index-update.yml` ist laut Audit seit dem 14.09. rot (Pin gegen Lindas v0.3.0-beta), DOI-Falle Concept gegen Version: Entscheidung Christian/Linda.
- **#414 gegen #451:** gegenläufig an `scripts/audit/doc-count-audit.py`, das ohnehin eingefroren ist; Entscheidung Christian.
- **#442, #448, #434, #463:** Überschneidung mit B oder offene Entscheidung.
- **Zweige** `origin/claude/237-aa1-vtc-biblstruct`, `origin/ingest/bre-weingruesse`, `origin/claude/235-315-wzb-tokens-lead-editor`: nur benannt, nicht gelöscht, nicht weitergebaut (Befund laut Audit B2).
- **PR #469 und sein Zweig.**
- Alle echten `auto:blocked`, `auto:pair`, `auto:frozen`.

---

## Änderungswünsche an eingefrorene Dateien

*Stand 23.09. nachmittags: 1, 3 und 4 von der Koordination nach den Merges von #471 und #474 eingetragen (die Zahlen in 3 am gemergten Stand nachgemessen, alle bestätigt). 2 ist mit #474 gekommen (Freeze-Ausnahme, s. Grenzverhandlungen). 5 wartet auf #469.*

1. **Spur B, `docs/FEATURES.md`, Genre Explorer** (FEATURES beschreibt sonst die #361-Semantik, die #433 revidiert; „Lyrik“ hätte dort keine Werke, live hat sie laut Spur B 427):
   - Anker `9 levels deep. Each node names its own works and how many sit in the branch\n  below it;` → `9 levels deep. Each node names the works of its whole branch and, where fewer, how many are assigned to it directly (#433);`
   - Anker ab `One checkbox, but its meaning has to differ between the` bis `That is 41 of the 133` → `Since #433 the checkbox means the same in both views: the category has works somewhere in its branch. Until then the result list counted only works assigned directly, which #433 revised after KZW's decision of 2026-09-15 that subgenres always come along; „Werke anzeigen" now lists the whole branch`
   - Anker `plus the\n  works assigned to it` → `plus the works of its whole branch, with the number assigned directly`
   - Nach dem Merge von Spur B's PR einzutragen. Der zweite Anker reicht bis zum Ende des Aufzählungspunkts (FEATURES.md Z. 187 bis 192, nachgesehen).
2. **Spur B, `docs/DEVELOPMENT.md`, Spec-Tabelle** (nach dem Merge von #469 und von B's PR):
   - nach der Zeile `search-engine.spec.js`: `| `genre-filter-suggestion.spec.js` | Main site | Genre suggestions in the text filter: a click selects the texts of the genre including its subgenres, checked against an oracle computed from the index files; typing alone leaves the selection unchanged (#433, #204) |`
   - nach der Zeile `genre-explorer.spec.js`: `| `text-comparison-filter.spec.js` | Playground | Typing filter above both text lists of the text comparison: folded match on siglum, title and author, auto-select of a single remaining text, selection kept when the filter misses it (#435) |`

3. **Spur A, `docs/DECISIONS.md`, ADR-021** (zweiter gemessener Flip, sonst nur im Codekommentar): hinter dem Ende von Z. 1289 (`…and until this run there was only the green.`) als eigener Unterpunkt:
   `  - **The third run is red again, twice** (2026-09-23, #387/#418/#464, Authority Index 1.9.8 against 1.9.9): **0 forms added, 0 removed, 2 re-pointed**, out of 234,250 mappings on both sides. \`hawe\` moved from \`lemma_2598\` *haben* to \`lemma_2923\` *houwen*, which is what Vorschrift B would choose (7 attestations under *houwen*, 6 under \`lemma_9644\` *houwe*, none left under *haben*). \`froewen\` moved from \`lemma_7256\` *vröuwen* to \`lemma_7250\` *vrô*, **against** Vorschrift B: the form is attested 35 times under \`lemma_7260\` *vrouwe*, 21 times under *vröuwen* and once under *vrô*, and it is that single token, minted as \`type_372389\` on KZW's decision in #387, that now wins because *vrô* sorts first. The type counter saw none of this (\`type ids with >1 lemma\` went from 1 to 0); only the dictionary comparison did.`
   Zahlen von Spur A gemessen, von der Koordination nicht nachgezählt; vor dem Eintragen gegen den gemergten Stand halten.
4. **Spur A, `docs/DECISIONS.md:782`**: `the 30 corpus files currently covered by GAPs 1–11` → `the 34 corpus files currently covered by GAPs 1–11` (dieselbe Baseline wie TEI-MODEL §10).

5. **Spur C, `docs/DEVELOPMENT.md`** (nach den Merges von #469 und #472, am Ankertext suchen):
   - `- Automated web server startup (port 8080)` → `- Automated web server startup on port 8080, or on the port in `MHDBDB_TEST_PORT` when it is set (#465). The variable is read in one place, `testing/test-port.js`, by the config, by `scripts/run-tests.js` and by `npm run serve` alike; anything but an integer from 1 to 65535 stops the run with exit 2. Two worktrees test in parallel with one command each: `npm test` in the first, `MHDBDB_TEST_PORT=8081 npm test` in the second (PowerShell: `$env:MHDBDB_TEST_PORT = "8081"`, then `npm test`). On 2026-09-23, on a 64 GB machine, a side-by-side pair of full runs at six workers each was stopped for lack of memory; with `-- --workers=2` each, both finished green in about 22 minutes.` (Wortlaut von Spur C nachträglich korrigiert)
   - `(no report written, or a foreign server on 8080)` → `(no report written, a foreign server on the test port, or an invalid `MHDBDB_TEST_PORT`)`
   - `# Opens on http://localhost:8080` → `# Opens on http://localhost:8080 (or on MHDBDB_TEST_PORT, see Testing)`
   - „64 GB“ vor dem Eintragen nachmessen, die Angabe stammt von Spur C.

## Grenzverhandlungen während des Laufs

- **Inbox-Wunsch 2 (DEVELOPMENT.md, zwei Spec-Zeilen) geht als Freeze-Ausnahme in Spur B's PR #474**: `check-doc-inventories.py` wird ohne die Zeilen rot (Run 35859225526, „36 Specs, 34 in DEVELOPMENT.md“). Der Freeze auf DEVELOPMENT.md war wegen #469 gesetzt; #469 ändert dieselbe Tabelle nur in einem anderen Hunk (@@ -234, zwei review-*.spec.js-Zeilen am Ende). Dasselbe trifft C's Inbox-Wunsch nicht, weil der Inventar-Check dort keine Zeile verlangt.
- **A2, FR3-Haltepunkt aufgelöst**: KZW 10.09. 14:59 in #267 („2026 können wir FR3 bereits von dieser Ausnahmeregel befreien“), bestätigt in unserer Zusammenfassung 15:52 („FR3 | Marker fällt“). FR3 bekommt das Standard-`<availability>`. Das Audit hatte den Punkt als offen geführt.
- **A2, Freeze-Ausnahmen**: `sources/README.md` Absatz Z. 182–191 als Ganzes (statt nur Z. 183, sonst widerspricht er sich); `assets/js/rendering/tei-text-reader.js:772` Kommentarzahl weg (Datei von Spur B, deren PR gemergt ist).
- **Maschinenweit nur ein Testlauf zur Zeit** (ab 23.09. nachmittags): Zwei Volläufe mit je 6 Workern haben zweimal den Speicher erschöpft (C mit Hauptbaum, C mit A); beide Male hat Claude Code den Lauf abgebrochen. Die Port-Warteschlange gilt deshalb für die Maschine, nicht je Port. Den Neustart nach dem Abbruch hat Christian beide Male freigegeben.

- **Tag-Reihenfolge #387 revidiert: `ADJ NOM` mit `@reason` statt `NOM ADJ`** (Widerspruch Spur A, entschieden von der Koordination am 23.09.). §1 Punkt 5 hat die Altlast gezählt und keine Konvention. Nachgezählt über 667 Dateien: `VRB PRO` 154, davon 154 mit `@reason`; `PRO VRB` 9.068 und `NOM ADJ` 119.501, jeweils 0 mit `@reason`. Ein bewusstes Doppeltag hat also eine eigene Reihenfolge plus `@reason`, und so wird es in POS-TAGSET festgehalten.
- **#387 prägt drei neue Typen statt einem, #418 Variante (a)**: zwei neue `hawe`-Typen, und `type_117159` fällt weg. Beides folgt aus der Tabellenzeile „prägen, nie umhängen“.
- **NEIM_2503080_8 darf in A1 mit**: ein einzelnes `<w>` plus `<change>`, keine `<note>`. #453 plant keine Neukonvertierung. Der Haltepunkt A3 bleibt.
- **Baseline 30 → 34 als Freeze-Ausnahme für Spur A**: validate-corpus.py (Set, :77, :98), TEI-MODEL.md 895–967 und :933, schema/README.md:23 (dort mit Ersatz eines Bestands-U+2014, sonst rot), CONTRACTS.md:381 (Nachbarzeile der gegateten Zählzeile). hilfe-daten-beitragen.html:819 zieht Spur B nach. DECISIONS.md:782 über die Inbox.
- **`froewen` kippt gegen Vorschrift B (ADR-021)** durch das Prägen nach #387 (first-wins, *vrô* sortiert zuerst). Angenommen, nicht umgehängt: die Auflösung ist das Gate aus ADR-021, nicht eine Ausnahme von „nie umhängen“. KZW bekommt es in #387 als Hinweis ohne Frage.
- **#58**: Die Form des Durchklicks geht auf Christians Entscheidung zuerst als Frage an KZW. B1 wird bis zur Antwort nicht gebaut.
- **B3 „Chip“** meint den Gattungs-Chip in der Trefferliste (app.js), nicht die Suchmaske; deren Form hat KZW am 15. und 17.09. entschieden (Lesart Spur B, bestätigt).
