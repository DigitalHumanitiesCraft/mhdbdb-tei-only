# Laufplan Nacht 23./24.09.2026: Nachlass des Tageslaufs und durchentschiedene Pakete

**Protokoll, keine Vorlage.** Der Plan altert ab dem Tag des Laufs; wer ihn als Vorlage nimmt, misst jede Angabe neu.

**Nachtbetrieb, Christian schläft.** Freigaben von chsteiner am 23.09.2026 abends, wörtlich: „Freigabe für den Merge von #476 und #469 hast du!", „#430 ... ja B", „starte die night session mit genug material für eine nacht! du hast auch merge freigabe wenn die reviews keine befunde mehr liefern!", und auf die Rückfrage nach Sessions und Index-Bumps: „keine sessions mehr, index-bumps darfst du auch mergen!". Daraus für diesen Lauf:

- **Die Koordination merged**, die Spuren nicht. Gemergt wird ein PR, wenn (1) die letzte `fable-reviewer`-Runde auf genau dem gepushten HEAD keinen offenen Befund der Klasse A oder B mehr trägt, (2) alle Checks außer `claude-review` grün sind, (3) der Kommentar des `claude-review`-Bots geöffnet und gelesen ist und keinen offenen Verhaltensbefund trägt, **auch wenn der Haken rot ist** (auf Daten-PRs ist er das laut `CLAUDE.md` regelmäßig), (4) `npm test` auf diesem Stand eine grüne VERDICT-Zeile hat, und bei Datenänderungen (5) die Lifecycle-Gates aus §8 grün sind. Index-Bumps sind eingeschlossen. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`.
- **`auto:checkin` gilt nachts nicht als Freigabe zum Fragen.** Niemand antwortet. Was eine Entscheidung braucht, die nicht im Thread steht, wird nicht gebaut, sondern als Frage an KZW, Linda oder Christian in den Statuskommentar geschrieben (Issue-Kommentare sind frei).
- **Kein Ticket wird geschlossen**, außer über `Closes #N` bei Vorgängen, die keine Abnahme durch KZW, Julia oder Externe mehr brauchen. Frontend-Vorgänge von KZW bleiben offen bis zu ihrer Abnahme nach dem Deploy.

**Vor dem Freeze erledigt (K):** #430 nach Variante B auf `main` (`be4c78a27`); #476 (zwei lokale Runden, Bot sauber, `0be0bcdd0`) und #469 (eine lokale Runde, Bot sauber, Vollauf `VERDICT: VOLLLAUF GRUEN (362 Tests, 36 Dateien)`, `546edb293`) gemergt; Inbox-Wunsch 5 des Tageslaufs in `docs/DEVELOPMENT.md` eingetragen, „64 GB" gemessen (63,6 GiB), die ungeprüfte Laufzeitangabe von Spur C dabei weggelassen; Betriebsmittel-Gegenprobe des Tageslaufs gefahren (Abweichungen nur `rules/audio-transkription.md`, `rules/google-konten.md`, `skills/whisper-transkription/SKILL.md`, alle drei Christians eigene Revisionen vom 23.09., kein Projektbezug).

**Planreview:** `fable-advisor` am 23.09. abends, Urteil „anpassen, dann starten". Übernommen sind die Befunde, die die Koordination nachgemessen hat (die Patch-Zählungen, die drei DOI-Kopien, der Gattungs-Chip, KZWs Satz vom 23.09. 12:32 in #433); die übrigen stehen mit „laut Planreview" dabei.

**Kennzeichnung:** „(K)" heißt, die Koordination hat es selbst am Bestand, am Thread oder an der API gemessen. Alles andere stammt aus einem Subagenten oder aus dem Tageslauf und ist ungeprüft. **Der ganze Auftragstext ist eine Behauptung**; jede Spur misst nach, bevor sie verwendet, und widerspricht, wenn es abweicht.

---

## 1. Ausgangslage

1. **Der Tageslauf ist nicht abgenommen, und zwei Spuren haben Arbeit liegen lassen.** Beide Spurprozesse sind beendet (K: PIDs 28856 und 36292 existieren nicht mehr; ob `claude stop` quittiert hat, ist nicht bekannt).
   - `.claude/worktrees/mhdbdb-daten2`, Zweig `claude/daten-0923-a2` auf `e7fb900cc`, nicht gepusht, kein PR (K). **Uncommittet liegt nur die #252-Hälfte**: 846 Ersetzungen `( caesura )` → `<gap reason="lost"/>` in 20 Dateien (K, gezählt an den eingefügten `<gap reason="lost"/>`-Zeilen im Patch: BRW 38, FR1 520, FR3 176, MSG 57, NEIC 22, NEIR 10, NEIM 5, SKL 3, SUB1 3, MML 2, je 1 in HUB2, PL1, SDG, SDT, SGO, SHF, SJH, SKT, SP, SUB), dazu `docs/TEI-MODEL.md` (Resttabelle) und `assets/js/rendering/tei-text-reader.js:772` (Kommentarzahl). **Die 2.081 Zeilen in FR1 sind erklärt**: 520 Ersetzungen, je drei Zeilen zu einer, das sind 520 × 4 + 1 Diffzeilen (laut Planreview, die 520 von der Koordination gezählt). **#267 ist im Patch nicht angefasst** (K: 0 Treffer auf `no-print` und `excerpt-only`); es liegt nur das Skript `scripts/ingest/no-print-267/apply-no-print.py` untracked daneben.
   - `.claude/worktrees/mhdbdb-playground`, Zweig `claude/433-filter-label`: **Commit `5625ff334`** (FILTER_LABEL für den Gattungs-Explorer, #433) nicht gepusht, kein PR (K). Er ändert laut Planreview auch die bestehende `genre-explorer.spec.js`. Uncommittet: ein JOURNAL-Nachtrag und zwei Reviewer-Memory-Dateien (K).
   - **Gesichert** als Patch und Tar unter `.claude/tmp/sicherung-2026-09-23/` im Hauptbaum (gitignoriert, K). Die Worktrees bleiben stehen, bis ihr Inhalt übernommen ist.
2. **Indexstand auf `main`:** Korpus 4.2.19, Authority 1.9.9, `check-index-versions.py` konsistent (K, 23.09. abends).
3. **Naming-Index-Update ist seit dem 14.09. jeden Montag rot** (K: Runs 34834313876, 35590353330). Grund laut Log (K): `CITATION.cff: v0.3.0-beta / 10.5281/zenodo.21914259` gegen `hier fest: v0.2.2-beta / 10.5281/zenodo.22248457`. Gemessen an der Zenodo-API (K): `21914259` ist der **Concept-DOI** von Naming-analysis, `22248457` der Versions-DOI von v0.2.2-beta, und **v0.3.0-beta hat einen eigenen Versions-DOI `10.5281/zenodo.22690452`** (Record vom 10.09.2026). Lindas `CITATION.cff` nennt also seit v0.3.0-beta den Concept-DOI, bis v0.2.2-beta den Versions-DOI.
   **Der Tageslauf hat die Frage „Concept gegen Version" als Entscheidung Christian/Linda geparkt (§9 dort). Dieser Plan revidiert das bewusst, aber nicht in der Sache:** er entscheidet nicht, welcher DOI der richtige ist, sondern übernimmt Lindas eigene Zitation wörtlich, wie der Wächter es seit jeher verlangt, und legt die Frage Linda vor (Paket B2). Ein früherer Entwurf dieses Plans wollte den Versions-DOI erzwingen; das hat der Planreview als Entscheidung gegen Lindas Zitation erkannt, und es ist gestrichen.
4. **Maschine:** 63,6 GiB (K). Zwei Volläufe mit je sechs Workern haben am 23.09. zweimal den Speicher erschöpft (Tageslauf, Grenzverhandlungen). Seit #472 gibt es `MHDBDB_TEST_PORT`; `scripts/run-tests.js` reicht `--workers` durch (laut Planreview, `run-tests.js:88/219`).

## 2. Zuschnitt: zwei Spuren, die Koordination merged

### Spur A `nacht-daten`: einziger Datenschreiber, seriell, je Paket ein PR

| Paket | Vorgänge | Inhalt | Bump |
|---|---|---|---|
| A1 | #252, #267 | #252 aus dem Nachlass zu Ende bringen, #267 vollständig bauen | nur wenn der Rebuild eine Differenz zeigt |
| A2 | #270 | Urheberangabe an kuratierten Kommentaren sichtbar machen | Authority |
| A3 | #357 | zweiter Sense für Menschennamen an `lemma_3036`, Umhängen von `REN_242090_0` | Authority + Korpus |
| A4 | #228 | Entannotieren nach KZWs Entscheidung vom 11.09. | beide |

Jedes Paket startet frisch von `origin/main`, **nach** dem Merge des vorigen. Die Koordination nennt die Bump-Nummer auf Anfrage.

**A1 im Einzelnen.** Die Entscheidungen stehen im Tageslaufplan (`2026-09-23-issue-abbau.md` §2 A2 und die Grenzverhandlungen, FR3-Haltepunkt dort aufgelöst) und in den Threads. **#252:** das Skript `scripts/ingest/gap-252/migrate-inline-gap.py` aus der Sicherung lesen, frisch auf `origin/main` laufen lassen, das Ergebnis gegen den Patch vergleichen (`git diff` der `tei/`-Dateien muss mit dem Patch übereinstimmen). **Kontrollwert:** eingefügte `<gap reason="lost"/>` je Datei gegen die 20 Zahlen aus §1, Summe 846. Nur das Muster wird ersetzt; die fünf Komma- und Doppelpunktfälle sind **nicht** freigegeben (Kontextliste am 23.09. 14:05 an KZW, keine Antwort, K). Weicht eine Zahl ab, die **xml:ids** der Differenz melden und nichts Zusätzliches anfassen. **Die fünf NEIM-Stellen gehören dazu**: KZWs Freigabe umfasst sie, und eine `<gap>`-Ersetzung berührt keine `<note n>`. Die NEIM-Sperre aus A4 gilt `<note>`-Eingriffen, nicht diesen fünf. **#267:** vollständig zu bauen, nicht fortzusetzen. Das Skript `scripts/ingest/no-print-267/apply-no-print.py` ist Material, das vor Gebrauch gelesen wird. Neun Header: Marker `excerpt-only` → `no-print`, KZWs Satz vom 10.09.; FR3: Marker fällt, Standard-`<availability>` (Grenzverhandlung des Tageslaufs). Mitzuziehen: `docs/TEI-MODEL.md` (Bedeutung von `no-print`, §6.5a), `sources/README.md` Z. 182–191 als ganzer Absatz, `tei-text-reader.js:772`.

**A2 im Einzelnen.** KZW am 23.09. 12:12 in #270 (K, wörtlich): „Die bereits gespeicherte Urheberangabe soll direkt beim Kommentar sichtbar sein, auf der Lemma-Seite und im Playground. Zum Beispiel: ‚Kommentar von Katharina Zeppezauer-Wachauer'. Die bestehende Zuschreibung bei ‚Abba' kann bleiben. [...] Bitte umsetzen und ADR-018 entsprechend aktualisieren." Die bibliographische Quellenangabe aus #28 ist ausdrücklich **nicht** Teil davon. Heute rendert `lemma/lemma-page.js` `sense.comment` ohne Urheber (K, Z. 201–210), ebenso `playground/js/ui/authority/lemma-explorer.js` (laut Planreview Z. 1077–1079). Der Index trägt `commentResp` schon, `contributors.xml` kommt im Build nirgends vor (laut Planreview); die Contributor-Map ist also der ganze Indexanteil. **Nachzumessen:** alle Stellen, die `comment`, `definition` und `origin` kuratierter Lemmata rendern, Grep über JS **und** HTML. Ob „Kommentar von" auch an `<def>` und `<etym>` gehört, steht **nicht** im Thread: gebaut wird es für den Kommentar, die anderen beiden gehen als Frage in den Statuskommentar.

**A3 im Einzelnen.** KZW am 14.09. in #357 (K, wörtlich): „Das braucht kein eigenes Lemma, aber es darf nicht nur einen Sense mit ‚Pferdenamen' haben, sondern auch einen zweiten mit Menschennamen. Das gilt für alle Namen." Welches Konzept der neue Sense trägt, steht nicht im Thread. **Aus derselben Stelle ableiten, nicht wählen:** die Nachbarn im Rennewart-Namenkatalog (laut Planreview `wimiligar` `lemma_22280`, `rufter` `lemma_22282`, `echerabant` `lemma_22283`). Tragen sie ein gemeinsames Konzept für Menschennamen, ist es das, mit der Messung im PR; tragen sie keines, ist das ein Haltepunkt, und die Frage geht an KZW. Der Satz „Das gilt für alle Namen" ist **kein** Auftrag für einen Korpuslauf über alle Namen; er geht als Beobachtung in den Statuskommentar.

**A4 im Einzelnen, nur wenn A1 bis A3 gemergt sind.** Entscheidungen KZW 11.09. 13:42 (K) und chsteiner 11.09. 13:52 (K) in #228: acht Dichternamen-Notes entannotieren, 422 GWTK-Inhaltsangaben entannotieren, alle dadurch belegfreien Lemmata löschen, `lob` in KVO nachtragen, kein NAM-Lemma für NIU. Größenordnung laut Thread 530 Notes, 2.294 Tokens, 170 Löschungen (von einer Claude-Session gerechnet, ungeprüft). **Haltepunkt, bindend: kein `<note>`-Eingriff in `tei/NEIM.tei.xml`**, dessen `<note n>` die Konkordanz aus #453 tragen; die NEIM-Anteile bleiben liegen und werden im Statuskommentar benannt. **Zusätzliche Stoppbedingung:** ein zu löschendes Lemma, auf das eine andere Authority-Datei verweist (`check-authority-cross-refs.py` prüft die Verweisattribute), wird nicht gelöscht, sondern mit xml:id gemeldet. Die Nebenbefunde (MR2-`Handschrift`, `lemma_2` „abc") gehören nicht in dieses Paket. **A4 erreicht die Nacht realistisch nicht**; es ist Reserve und im Morgenbericht kein Rückstand.

**Stoppbedingungen (A):** ein Token, dessen Ist-Zustand nicht dem Thread entspricht; eine Entscheidung, die KZW nicht getroffen hat; eine Datei außerhalb des eigenen Bereichs; eine Zahl, die vom freigegebenen Umfang abweicht.

### Spur B `nacht-frontend`: Frontend, Playground, Naming; keine Korpus- oder Authority-Daten

| Paket | Vorgang | Inhalt |
|---|---|---|
| B1 | #433 | Nachlass von Spur B: `5625ff334` übernehmen, samt JOURNAL-Nachtrag und Reviewer-Memory; dazu den Gattungs-Chip entfernen, wie KZW am 23.09. entschieden hat |
| B2 | #420 | Lindas Punkte 1 und 4: Pin auf v0.3.0-beta, „Term" → „Lemma" im ganzen Modul; Punkt 3 (Tab „Bezeichnung") wenn billig |
| B3 | #467 | Suche nach der Lemma-Nummer im Wörterbuch; für Korpussuche und Playground nur messen und antworten |
| B4 | #448 | Werkzeug-Analyse für CSV-Export im Playground, Exporte für die eindeutig tabellarischen Analysewerkzeuge |

**B1.** Cherry-pick von `5625ff334` auf einen frischen Zweig, die uncommitteten Teile aus `.claude/tmp/sicherung-2026-09-23/playground-uncommitted.patch` gelesen und übernommen, soweit sie noch stimmen. **Dazu:** KZW am 23.09. 12:32 in #433 (K, wörtlich): „Bitte den ungenutzten Anzeigezweig für die Gattungs-Chips entfernen. Auf den Trefferkarten möchte ich keine zusätzlichen Gattungsbeschriftungen." Der Zweig steht noch in `assets/js/app.js:1695` (K). Eine eigene `fable-reviewer`-Runde auf dem neuen Stand, denn die alte deckt eine andere Basis.

**B2.** Linda am 16.09. in #420 (K, wörtlich): „Von meiner Seite abgenommen. Wenn ihr Punkt 1 und 4 übernehmt, kann das Ticket zu." Punkt 1: „Pin auf v0.3.0-beta heben." Punkt 4: „Beschriftung: *Lemma* statt *Term*", ausdrücklich für das ganze Modul (Hilfe, `FEATURES.md`, Filterbeschriftungen).
- **Pin:** `QUELL_VERSION = "v0.3.0-beta"` und `QUELL_DOI` **wörtlich aus Lindas `CITATION.cff`** (`10.5281/zenodo.21914259`), der Wächter bleibt unverändert. Er fängt „neue Daten unter alter Zitation" weiter über den exakten Versionsvergleich. Index lokal bauen mit `01-fetch-and-build-index.py --ref v0.3.0-beta` (die Optionen im Skript nachsehen), committen; kein `workflow_dispatch` von `naming-index-update.yml`, denn der baut gegen master und öffnet einen eigenen PR ohne CI (laut Planreview). **Schlägt ein weiterer Wächter an** (etwa `pruefe_instanztypen`, weil Lindas Typologie gewachsen ist), ist das ein Haltepunkt für Punkt 1: messen, melden, Punkt 4 allein liefern.
- **Die Frage an Linda** in den Statuskommentar von #420: ihre `CITATION.cff` nennt seit v0.3.0-beta den Concept-DOI; übernommen ist ihr Wortlaut; soll der Index lieber den Versions-DOI `10.5281/zenodo.22690452` zitieren? Keine Antwort nötig, damit der PR steht.
- **Zitationskopien, die mitziehen:** `docs/FEATURES.md:325` (Naming-Absatz, B); `docs/DATA-MODEL.md:370` (eingefroren, **benannte Freeze-Ausnahme für B2**, nur diese Zeile); `authority-files/contributors.xml:191` (A-Datei, **benannte Ausnahme für B2**, nur diese Note, weil sie nur mit dem Pin zusammen stimmt).
- **Punkt 4 ändert eine bestehende Spec**, `testing/tests/naming-explorer.spec.js` (laut Planreview 29-mal „Term"): für B2 vorab freigegeben.
- **`Closes #420` nur, wenn Punkt 1 und 4 beide im PR sind.** Fällt Punkt 1 aus, bleibt #420 offen, und der Statuskommentar sagt warum. #412 bleibt unberührt (wartet auf Lindas Kollokationen).

**B3.** KZW in #467: die Nummernsuche im Wörterbuch (`woerterbuch.html`, K); am 22.09.: „Und prüfen, ob das in der Korpussuche und im Playground auch Sinn machen würde oder unnötig kompliziert wäre"; am 23.09.: „Hab gerade festgestellt, dass das in der Multi-Lemma-Suche bereits geht." **Gebaut wird nur das Wörterbuch.** Für Korpussuche und Playground wird gemessen und im Statuskommentar geantwortet; im Playground liegt die einzige denkbare Stelle im Lemma-Explorer, der in dieser Nacht Spur A gehört.

**B4.** KZW im Body von #448 (K): „Denke systematisch die einzelnen Tools im Playground durch. Ich denke, das wird nicht bei allen möglich sein, aber bei manchen wahrscheinlich schon." Liefern: die Analyse je Werkzeug als Tabelle im Statuskommentar (tabellarisch ja/nein, welche Spalten), und Exporte für die Werkzeuge unter `playground/js/ui/tei/`, deren Ergebnis schon eine Tabelle ist. **Die Explorer unter `playground/js/ui/authority/` sind ausgenommen.** Das Format folgt der Hauskonvention (laut Planreview: Komma, RFC 4180, CRLF, UTF-8 mit BOM, `assets/js/app.js:1408–1443` aus #114, dieselbe in `hapax-legomena.js:624`); wer sie nach `assets/js/lib/` zieht, trägt sie in `assets/js/lib/README.md` ein (Inventar-Gate). Was eine Gestaltungsfrage wäre (Export einer Grafik), wird nicht gebaut.

### Koordination

Merges; Inbox; Testvergabe (§5); Abbau der beiden alten Worktrees nach Übernahme ihres Inhalts; der zugesagte Prüfweg in #251 (K: am 08.09. zugesagt „erst, wenn der #58-Fix live ist"; KZW bestätigt am 23.09. in #58 „Die Zahl stimmt jetzt"); am Ende ein Nachtrag in #406, wenn sich für KZW etwas bewegt hat; der Morgenbericht.

## 3. Dateibesitz

| Bereich | Schreiber |
|---|---|
| `tei/`, `authority-files/` (außer der einen B2-Note), `data/` außer `data/naming-index.json.gz`, `api/`, `scripts/build-*.py`, `scripts/ingest/` außer `scripts/ingest/naming/`, `ingest/` | **A** |
| Versionsliterale: `build-corpus-index.py`, `build-authority-index.py`, `assets/js/lib/corpus-loader.js`, `docs/TEI-MODEL.md` §11, die Versionszeile in `docs/INDEX.md` | **A** |
| die von `doc-count-audit.py` gegateten Zahlzeilen, wo immer sie stehen | **A**, zeilengenau |
| `assets/js/rendering/tei-text-reader.js:772` (die eine Kommentarzeile), `sources/README.md` Z. 182–191, in `scripts/README.md` der Absatz zu `ingest/` (neue Ingest-Ordner **nicht** in den Verzeichnisbaum schreiben, sonst meldet `check-doc-inventories.py` „genannt, nicht vorhanden") | **A** |
| `lemma/`, `playground/js/ui/authority/lemma-explorer.js`, weitere #270-Render-Stellen nach Messung und Meldung; eine neue Spec für #270 | **A** |
| `docs/DECISIONS.md` ADR-018; `docs/TEI-MODEL.md` und `docs/POS-TAGSET.md` an den Stellen, die A1 und A4 verlangen | **A** |
| `data/naming-index.json.gz`, `scripts/ingest/naming/`, `authority-files/contributors.xml:191`, `docs/DATA-MODEL.md:370`, `testing/tests/naming-explorer.spec.js` | **B** (B2) |
| `testing/tests/genre-explorer.spec.js` | **B** (B1) |
| `playground/` außer den A-Stellen, `assets/js/` außer `corpus-loader.js` und den A-Stellen, `index.html`, `korpus.html`, `woerterbuch.html`, `assets/css/`, neue Specs für B | **B** |
| `hilfe-korpussuche.html` | **A** nur in §6 „Lemma-Seite", Listenpunkt „Bedeutungen"; **B** nur in §7 „Wörterbuch von A bis Z" |
| übrige `hilfe-*.html`, `docs/FEATURES.md` | **B**; **A** nur im Absatz zur Lemma-Seite und zu kuratierten Lemma-Angaben. Wer dieselbe Datei braucht, holt vorher `origin/main` |
| `docs/DEVELOPMENT.md` | **Koordination**; Spec-Zeilen, die `check-doc-inventories.py` verlangt, als Wortlaut an sie oder, wenn das Gate sonst rot bleibt, als benannte Ausnahme im PR |
| übrige bestehende Specs unter `testing/` | nach Meldung an die Koordination |

**Der Satz für beide Kickoffs:** wer eine Datei außerhalb seines Bereichs ändern müsste, ändert sie nicht, sondern meldet es.

### Geteilte Dateien

| Datei | Regel |
|---|---|
| `docs/JOURNAL.md` | anhängend, letzter Commit des PR, unmittelbar nach `git fetch origin` |
| `fehlerjournal.md` | ebenso. Vergeben bis 73, 74 bis 79 frei und nicht mehr beansprucht (K). **A 80–84, B 85–89, Koordination 90–94.** Die Zeile nennt die Nummer der letzten Zeile derselben Lehre |
| `.claude/agent-memory/fable-reviewer/` | eigene Datei je Spur, eigener Commit nach der Runde; die Indexzeile in `MEMORY.md` als eigene neue Zeile, nie eine bestehende verlängern. Der Stand der Koordination ist mit dem Freeze-Commit committet |
| `docs/ROADMAP.md` | niemand |

## 4. Freeze

**Scharf ab dem Commit, der diesen Plan einführt, gepusht vor dem ersten Kickoff. Er löst den Freeze des Tageslaufs vom 23.09. ab**; dessen offene Abnahmepunkte (Worktrees, Nachlass) laufen unter §8 dieses Plans.

Eingefroren: `CLAUDE.md`; die 15 promptotyping-Dokumente in `docs/` mit den Ausnahmen aus §3 und `docs/JOURNAL.md` (geteilt); `docs/playbooks/` außer diesem Plan (Inbox, Grenzverhandlungen); `.github/workflows/`; `scripts/audit/`; `scripts/README.md` außer dem A-Absatz aus §3.

**Inbox:** Abschnitt am Ende. Format: Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum. Die Koordination trägt ein.

**Globale Betriebsmittel:** festgehalten mit `.claude/tmp/betriebsmittel-hash-2026-09-23-nacht.py` (Hauptbaum, gitignoriert, Kopie des Tagesskripts mit eigener Ablage), Ablage `.claude/tmp/betriebsmittel-2026-09-23-nacht.json`. `claude-code-setup` beim Start: `c6746bc1e`, Arbeitsbaum sauber (K). Gegenprobe bei der Abnahme mit `--pruefe`.

## 5. Betriebsmittel

- **Volläufe vergibt die Koordination, einer zur Zeit**, Vorrang A. Anfordern, laufen lassen, freimelden. Jede Spur testet auf ihrem eigenen Port (A `MHDBDB_TEST_PORT=8081`, B `8082`) mit `-- --workers=2`, auch bei `test:quick` und `test:changed`. Die Tagesregel „maschinenweit ein Testlauf zur Zeit" bleibt damit in Kraft. **Parallel erst**, wenn die Koordination selbst ein Paar mit zwei Workern je Lauf und zwei VERDICT-Zeilen gemessen hat, und dann als benannte Revision unter „Grenzverhandlungen". **Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis**: nicht deuten, melden, nach Freigabe wiederholen.
- **Dev-Server** nur für die Dauer einer Chrome-Prüfung, auf dem eigenen Port.
- **Indexversionen:** allein A, Nummer vor dem Bump bei der Koordination anfragen.
- **`--allow-dirty`**: die `build-*.py` verweigern einen unsauberen Baum, der Lifecycle verlangt den gemeinsamen Commit (Tageslauf §5, laut Planreview bei allen drei Builds). Kein `git stash` als Ausweg.
- **`npm ci`** in jedem neuen Worktree vor der ersten Benutzung.
- **`fable-reviewer`** vor jedem ersten Push und nach jedem Commit, der auf einen Befund antwortet. Ein fehlender Agententyp ist ein Halt, kein Weiter.
- **Nicht über den Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, keine fremden Zweige, kein Force-Push auf gepushte Historie, keine Änderung unter `~/.claude/`.
- **Notationsfalle:** als Subagent lehnt der Auto-Mode-Classifier `npx playwright test --list` ab (Reviewer-Memory von Spur B, 23.09.). Die Testzahl eines Vollaufs steht in `testing/test-results/report.json`.

## 6. Vorab entschieden

| Frage | Entscheidung | Grund |
|---|---|---|
| Merge | Koordination, nach den Bedingungen oben | Freigabe chsteiner 23.09. abends |
| Neue Variantentypen | prägen, nie umhängen | Regel aus #367 |
| Naming-DOI | Lindas `CITATION.cff` wörtlich übernehmen, Frage an Linda | §1 Punkt 3; die Wahl zwischen Concept und Version trifft nicht dieser Lauf |
| #420 schließen | per `Closes`, **nur** mit Punkt 1 und 4 im PR | Linda hat die Abnahme an beide gebunden |
| übrige Tickets | offen bis zur Abnahme | ein Merge ist keine Abnahme |
| Fragen nachts | als Statuskommentar ins Issue | niemand kann antworten |
| Testläufe | seriell über die Koordination | zwei Speicherabbrüche am 23.09. |

**Widerspruch ist erlaubt**, auch gegen diese Tabelle, und geht an die Koordination.

## 7. Melde- und Haltepunkte

**Melden, weiterarbeiten:** `pwd`, Zweig, HEAD nach dem Lesen; je Paket der nachgemessene Umfang gegen den behaupteten; Beginn und Ergebnis jeder Reviewrunde mit Kennung des geprüften Standes; Testlauf angefordert und frei; PR bereit zum Merge, mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; Stoppbedingung; fehlender Agententyp; die Haltepunkte (A1 Kontrollwert weicht ab, A3 kein gemeinsames Konzept, A4 NEIM-Notes und fremde Verweise, B2 weiterer Wächter).

**Externer Zustand (CI):** nicht blind warten, sondern mit `Monitor` oder einem Hintergrundbefehl, der beim Eintreten weckt; kein Pollen mit `sleep`. Bot-Befunde auf dem eigenen PR werden beantwortet, bevor „bereit zum Merge" gemeldet wird. Auf einem PR mit leeren Checks zuerst `gh pr view N --json mergeable`.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian (laden über `ToolSearch` mit `select:PushNotification`), was blockiert wurde und woran es hängt, dazu Meldung an die Koordination. Nicht über die andere Spur oder die Koordination umgehen. `rules/blockaden-melden.md`.

**Ein Paket darf für nicht durchführbar erklärt werden**, mit Messung und früh. Danach das nächste.

## 8. Abnahme

1. Journaleinträge beider Spuren und der Koordination, die der Koordination zuerst.
2. Je PR ein `fable-reviewer`-Urteil für den gemergten HEAD.
3. `npm test` mit VERDICT-Zeile je PR.
4. Daten-PRs: `data-integrity.yml`, `check-index-versions.py`, `check-index-version-bump.py`, `check-no-em-dash.py --diff-base origin/main`, `doc-count-audit.py --check` grün, Bot-Kommentar gelesen.
5. Lifecycle vollständig: `extract-variants.py --apply` wo Korpus berührt, beide Indexe, `build-api.py`, Bump an allen Stellen.
6. Betriebsmittel-Gegenprobe mit `python .claude/tmp/betriebsmittel-hash-2026-09-23-nacht.py --pruefe`.
7. Jeder angefasste Vorgang relabelt, Statuskommentar, `build-issue-matrix.py --check` grün.
8. Die alten Worktrees `mhdbdb-daten2`, `mhdbdb-playground` und die neuen abgebaut nach `abnahme.md` (Quittung von `claude stop` wo möglich, Prüfungen samt `--ignored`, Agent-Memory vorher gerettet), liegenbleibende Zweige benannt.
9. Bericht an Christian für den Morgen: was gemergt ist, was offen ist und bei wem, welche Fragen in welchen Tickets stehen.
10. Abweichungen vom Operator-Playbook: Issue in `claude-code-setup`.

## 9. Was dieser Lauf nicht tut

- `auto:blocked`, `auto:pair`, `auto:frozen`, und von den `auto:checkin`-Tickets alle, deren offene Frage kein Mensch beantwortet hat: #434, #442, #414, #459, #462, #463 (Triage-Subagent; die Zitate für #357, #378 und #228 von der Koordination am Thread nachgeprüft).
- #378 (Option 3 ist UI-offen, das Gate liegt in `scripts/audit/`, eingefroren), #451 (berührt `doc-count-audit.py`), #453, `<note>`-Eingriffe in NEIM.
- Keine Mail, kein Kontakt zu Externen außerhalb von Issue-Kommentaren.

---

## Änderungswünsche an eingefrorene Dateien

*(leer bei Laufbeginn)*

## Grenzverhandlungen während des Laufs

- **A1 ohne Bump gemergt, wenn es so weit ist**: `data/`, `api/` und `authority-files/` ohne Diff nach allen drei Builds (Spur A, `check-index-version-bump.py` bestätigt laut Reviewer). `<gap>` und `<caesura>` sind keine `<w>`.
- **A2 (#270), benannte Freeze-Ausnahmen** (Anfrage Spur A, entschieden von der Koordination): sobald `build-authority-index.py` `contributors.xml` liest, werden diese Stellen falsch und ziehen im A2-PR mit, nur soweit sie davon handeln: `docs/DATA-MODEL.md` Z. 465, 548, 893, **903** (Routingzeile „contributors.xml: no rebuild, no bump"; bliebe sie stehen, veraltete der Name im Index still), `docs/CONTRACTS.md` Z. 927 (§G.3), `docs/TEI-MODEL-AUTH-FILES.md` Z. 211, `docs/DECISIONS.md` Z. 46 (ADR-001), `scripts/README.md` Z. 123. Nicht falsch und deshalb nicht angefasst: `RESEARCH.md:136`, `playground/readme.md:190`, `MASTERPLAN-EINZEL-LEMMA-KURATION.md:102`. Spur B berührt in `DATA-MODEL.md` nur Z. 370; verschiedene Hunks.
- **Spur B ist nach ihrer Startmeldung ohne Commit und ohne Meldung ausgefallen** (Prozess tot, `claude logs`: „job not found"); neu gestartet als `nacht-frontend-2` auf `52575e73a`, derselbe Auftrag, zusätzlich Meldung je Schritt. Der alte Worktree `nacht-frontend` bleibt unberührt bis zur Abnahme.
- **B1, benannte Freeze-Ausnahme `docs/DESIGN.md:148`** (Zeile „Genre tag"): das Muster steht nur noch am entfernten Chip in `assets/js/app.js` (Koordination nachgemessen); die Zeile fällt im B1-PR.
- **B2 baut mit `--ref master` statt `--ref v0.3.0-beta`** (Widerspruch Spur B, angenommen): master und Tag sind beide `8076467a` (Koordination nachgemessen), das Skript schreibt den ref wörtlich in den Index, der Montagslauf baut ohne `--ref` und vergliche sonst bytegenau gegen ein anderes ref-Feld; der heutige Index trägt ebenfalls `ref: master`.
