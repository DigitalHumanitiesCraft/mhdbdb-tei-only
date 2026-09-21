# MHDBDB Development Journal

Chronological log of development decisions, dead ends, and savepoints. Not a changelog – captures the *reasoning* behind changes.

---

## 2026-09-21: Ein Prüfseiten-Format (#443), und die halbe Fallmenge war gar keine Frage (#359)

Zwei Vorgänge in einem Lauf: ein Format für kuratorische Prüfseiten (#443) und seine erste Anwendung, 45 Fälle aus Luise Boreks Pferdewortlisten (#359). Eine einzelne HTML-Datei, die man verschickt und ohne Installation im Browser öffnet, mit eingebetteten Daten, Rückgabe als JSON und als lesbarer Bericht.

**Der Befund, der die Seite umgebaut hat, steht nicht im Ticket.** Die exakte Stufe des Abgleichsberichts vergleicht Boreks flektierte Formen gegen unsere Lemmaansetzungen. Wo eine fremde Ansetzung zufällig wie eine Flexion aussieht, trifft sie das falsche Wort: `oren` nicht das Ohr, sondern das Fabelvolk der `Ôren` im Herzog Ernst, `lenden` nicht die Lende, sondern das Verb `landen`. Der Homographenzähler des Berichts sieht davon nichts, weil die normalisierten Formen auseinanderlaufen. **28 der 45 Fälle sind Artefakte dieser Art oder bestätigt richtige Annotationen und brauchen keine Entscheidung.** Die Seite ist deshalb nach Befund gruppiert und nicht nach der Klasse des Berichts, und das steht über der ersten Karte: wer 45 Karten durchklickt und bei Karte 31 merkt, dass die Hälfte keine Frage an ihn war, hat bis dahin die falsche Frage beantwortet.

**KZWs Körperteil-Frage vom 16.09. löst sich zu drei Vierteln auf.** `ôr`, `lende` und `brust` tragen `concept_14011100` längst; Boreks Formen haben andere Lemmata getroffen. Nur `gebeine` ist ein echter Kandidat, und die tierische Verwendung ist belegt (`AXU_23544_3` „gar des orses gebeine“, `HTR_193190_2` „des lewen gebeine ist âne marc“). Gelesen sind 9 der 207 Belege, nämlich die mit einem Pferdewort im Kontextfenster: das beantwortet „kommt vor“ und nicht „kommt wie oft vor“, und die Seite sagt das so. Der Löwenbeleg ist dem Filter zugelaufen, weil `marc` in der Wortliste steht und an dieser Stelle Knochenmark heißt.

### Was über den Fall hinausgilt

**Ein Gate schützt, was es liest, und die Liste dessen, was es liest, ist selbst eine Behauptung.** Gegen verfälschte Zitate war ein Gate gebaut: jedes Zitat in der Begründung muss so in den gemessenen Belegen stehen, `ss` ausdrücklich nicht gleich `ß`. Es hat gegriffen und trotzdem nichts genützt, denn über der Begründung steht `kurz`, fett gesetzt und als Erstes gelesen, und dort behauptete eine Kurzzeile eine Formel, die keiner der fünf Belege liest. Das ist dieselbe Geometrie wie #397, eine Stufe höher: dort raubt ein Fix einer Prüfung ihren Gegenstand, hier gibt ein Gate den Nachbarfeldern eine Zusage, die es nicht einlöst.

**Die Antwort darauf hat drei Stufen, und die dritte ist die einzige, die nicht mitwachsen muss.** `_prosafelder` sammelt die Felder, statt sie aufzuzählen; `HTML_FELDER` steht im Modul statt im Kopf des Autors; und `rohe_striche` prüft **das fertige Dokument** statt der Felder. Kommt ein siebtes Feld dazu, bleibt nur die dritte richtig. Vier Felder einzeln zu bewachen hieße, das fünfte zu vergessen.

**Drei Runden, drei Klasse-A-Befunde, und jeder saß in dem, was die vorige Runde gebaut hatte.** Runde 1 fand die fehlende Auszeichnung; Runde 2 fand, dass deren Fix den Rückweg verdorben hatte (`vorschlag.text` ging durch die Auszeichnung, und dasselbe Feld lebt als Text im Export weiter, wo KZW `<span class="mono">hurt</span>` gefunden hätte); Runde 3 fand den Fehler in der Prüfung, die Runde 2 dagegen gebaut hatte. Sie suchte im fertigen Wert nach einem Muster, sah aber einen Wert nach `html.unescape`: ein geschriebenes `<pc>` steht darin wieder als `<pc>` da. **Gemessen brechen `<pc>` und `<w>` ab, während `a < b und c > d` durchläuft**, also trifft der Fehlalarm genau die Formen, die hier in einer Annotationsbegründung stehen.

**Ich habe daraufhin das Gate umgebaut, es vergleichen statt suchen lassen, und Runde 4 hat gezeigt, dass der Umbau nichts prüft.** Der Vergleich leitete den erwarteten Wert mit demselben Ausdruck aus derselben Quelle ab, den der Generator benutzt: für `kopfText` `f['kopf'] == f['kopf']`. Ein ausgezeichnetes Feld ohne Eintrag in `HTML_FELDER` lief glatt durch, und das ist genau das Fehlerbild aus Runde 1. **Der Stand nach Runde 3 war schlechter als der davor**, und damit war die Entscheidung keine Abwägung mehr: zurückgebaut, die Lücke im README benannt, der Vergleich ersatzlos raus.

**Vier Runden, drei davon an derselben Stelle, und das ist für sich ein Befund über das Vorgehen.** Die Prüfung, um die es ging, hat in den 45 realen Fällen nie gefeuert und hätte es auch mit keiner der vier Fassungen getan. Was jede Runde erzeugt hat, war eine weitere Annahme über einen Fall, den es hier nicht gibt.

**Die Lehre, die bleibt, ist nicht die über Muster und Vergleiche, sondern die über den Ersatz:** wer ein Gate ersetzt, fährt die Mutationen der alten Fassung gegen die neue. Meine acht Proben waren alle für die neue Fassung erfunden, keine stammte von der alten, und keine berührte deshalb den Fall, den die alte gefangen hätte. **Eine Mutationsprobe, die nur die neue Prüfung kennt, misst, was der Autor sich vorgestellt hat; die alte Fassung weiß, was früher schiefging.** Rote Zeile 56.

**Und der Grund, warum ich es nicht selbst gesehen habe, steht in meinen eigenen Texten desselben Nachmittags.** Die #397-Frage („was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?“) steht im Eintrag oben, im Reviewauftrag für Runde 4 und in der roten Zeile 47. Ich habe sie dreimal an fremden Code gestellt und kein einziges Mal an den Fix, den ich gerade schrieb.

**Eine Prüfung, deren Greifen nicht gemessen ist, ist eine Behauptung wie jede andere.** Jede neue Prüfung dieses Laufs ist mit einer Mutationsprobe in beide Richtungen belegt: sauberer Fall durch, mutierter abgewiesen. Die Koordination hatte am selben Tag vorgemacht, warum die eine Richtung nicht reicht, und dabei einen ungültigen ersten Anlauf offengelegt, dessen Attrappe an einer Stelle saß, die das Gate ohnehin überspringt. Eine Probe, die nur den mutierten Fall zeigt, belegt, dass ein Gate etwas meldet, und nicht, dass es das Richtige meldet.

**Der Zuschnitt einer Messung ist gefährlicher als ihre Rechnung.** Dreimal an einem Nachmittag war die Menge falsch geschnitten und die Zahl darin richtig: ein Kontrollwert, der flektiert danebenlag (`Welscher Gast` gegen „Der Welsche Gast“); eine Grundmenge, die nur finden konnte, wonach sie fragte (fünf bekannte Titel statt der 36 Werk- und Autornennungen unter 59 Klammernennungen); und eine Zahl, unter der zwei Mengen lagen. Aufgefallen ist jeder der drei erst, als das Kommando für die nächste Aussage hinzuschreiben war, keiner beim Schreiben der Zahl. Rote Zeile 48. **Beim Nachzählen der Kette für diese Zeile ist derselbe Fehler noch einmal aufgetreten:** ein Grep über das Fehlerjournal nach `dateisuche.md` trifft null Einträge, und alle drei Zeilen dieser Lehre nennen sie in Prosa. Wer eine Kette über den Dateinamen zählt, zählt die Zeilen, die ihn zufällig schreiben.

**Und eine Quote, deren Nenner ein Sammel-Limit ist, sieht aus wie eine Aussage über das Korpus.** `jagen` trägt 1.406 Tokens, gesammelt sind 250, weil `BELEG_CAP` dort greift; „249 von 250“ ist eine Aussage über die Sammlung und keine über das Korpus.

### Nebenbefund, der weiter reicht: `pos` gegen `posAll`

Bevor sich Bewertungen auf die Wortart eines Lemmas berufen, ist gemessen, ob das Feld hält. Gegen `posAll` sind **34 von 34** Lemmata mit gesammelten Belegen einig, sobald Kompositum-Tags aufgelöst werden (ohne diese Regel 31, und die drei Abweichungen wären reine Notation). Gegen das Einzelfeld `pos`, also die Angabe, die als *die* Wortart erscheint, weichen **4 von 34** ab: `jagen` führt INJ bei 249 von 250 VRB, `lenden` ADV bei 44 von 45 VRB, `merken` INJ bei 7 von 7 VRB, `rôse` ADJ bei 3 von 3 NOM. Alle vier führen die Korpuswortart in `posAll` an zweiter Stelle. Das betrifft `authority-files/` und jede Ansicht, die `pos` zeigt, und steht mit Messvorschrift in `ingest/review/359-borek/folgebefunde.md`.

### Rote Zeilen

Ausgezogen nach [../fehlerjournal.md](../fehlerjournal.md): **45** die Umlaut-Ersetzung, die drei mittelhochdeutsche Zitate mitgezogen hat; **46** vier aus Siglen erschlossene Werktitel, derselbe Fehlermodus wie `Alanya`, nur an einem Kürzel; **47** das Gate, das ein Feld deckte und daneben fünf stehen ließ; **48** der dreimal falsch geschnittene Zuschnitt; **49** eine Zahl aus einem Reviewbericht, die ich in vier eigene Texte geschrieben habe, ohne sie zu messen; **56** das Gate, das ich durch ein besseres ersetzt habe, welches nichts prüfte.

## 2026-09-16: #444, Moriz von Craûn ist anonym

KZWs Korrektur aus #444: Die veraltete Zuschreibung an Bligger von Steinach entfällt in work_5 und im CR-Header. Anonym stand bereits an zweiter Stelle; der erste Eintrag bestimmte den Index-Autor. Auch der lokale Bligger-Eintrag in CR und der work_5-Rückverweis in MBS sind entfernt. Bliggers Lyrik bleibt ihm zugeordnet. Text und Annotationen bleiben unverändert. Beide Indexe (Corpus 4.2.17, Authority 1.9.7) und API neu gebaut. Die historische Zuschreibung bleibt hier dokumentiert; das Datenmodell für den Forschungsstatus und eine Prüfung aller Mehrfachzuschreibungen sind Folgeaufträge aus dieser Sitzung an Claude.

## Verdichtete Historie

Hochrangiger Trace der Einträge 2025-02 bis 2026-09-07. Volltext aller 131 verdichteten Einträge in `journal-archive.md`.

**2025-02 (Phase 0 + #42):** Stabilisierung vor #42 – Wenzelsbibel (652k Zeilen) auf `feature/wenzelsbibel-ingest`, `assets/{css,js,images}` konsolidiert, Playwright 2→36 grün / 25 skipped (#43). #42 Persistent Lemma Pages: Wörterbuchnetz-IDs schon deckungsgleich (`lid=879` = `lemma_879`), Clean URLs `/lemma/879` + 404.html-Redirect-Trick für GitHub Pages. Savepoints `4562c08`, `6849758`, `e16306d`, `5154d04`.

**2026-02 (Triage + Provenienz):** #44-Triage (23 Issues, 11 Labels; 13/23 Daten/TEI). #21 „Konzepte"→„Begriffe", #46 Lemma-Suche in Multi-Lemma gemerged, #45-API Hybrid-File-Strategie beschlossen, #36-40 Provenienz-Modell ADR-012 (flaches `<listBibl>` + `<bibl type="digitalIntermediary">`). #49-Konvention: Health-Check-Reports als Issue-Comments, keine `.md`.

**2026-04 (#32 TEI Model Consolidation – die große Migration):** 0/100 Files gegen tei_all.rng valide (nur `@meaningRef`+`@wordRef` non-standard; `@lemmaRef` IST Standard). 15M+ Transformationen über 675 Files: `@meaningRef`→`@ana` (5.9M), `@wordRef`→`@corresp` (7.5M), `seg`→`pc` (1.4M), `l`→`lb` in 18 Prosa-Files. Merge PR #69 (Korpus) + #71 (Authority); Deep-Schema-Audit fixte 11 Gaps – Root Cause: `div` ist RNC-Keyword → `tei.div` (brach RNC→RNG). 666/666 valid; Performance-Fix `tree.xpath()` O(n²) → `iter()` Clark-Notation; Branch-Protection auf `main`. WZB-Pipeline (#34/#66): Phase 1b Lemma 91,6 %, Phase 2 POS 95,5 % (Tagset ART→DET, CNJ→CCNJ/SCNJ/ADV), Phase 3 Paratext.

**2026-04-14–16 (Schema-Hardening + Frontend-Sprint):** #83 Editor-Attribution (`contributors.xml`, 51 Personen + 2 Orgs); #32-followup 16/17 + Konvention „Daten vor Schema". **PL1-Validierungs-Pathologie war ein `<p>` mit 404k Direktkindern, nicht die Größe**; nested `<hi>` über 143 Files geflattet; Validierung 830s→493s. **Mishap `8b5d0e6ac`: `git add -A` zog Kollegen-Files mit → CLAUDE.md-Git-Regel + Memory.** Frontend: #31 LINECODE.md, #56 Similar Lemmata, #48 Hash-Router, #17 Reader View (43k unstyled Compound-`@rend` gefixt, 128/128).

**2026-05-07/08 (#32-followup fertig + ARITHMETIC + PD-001):** #32-followup 17/17. #68-Guide-Architektur (user-facing HTML deutsch ≠ LLM-Docs englisch). WZB-Reorg → `scripts/ingest/wzb/`. **PD-001 „Mittelweg" (KZW+Christian): TEI-P5-Standardelemente + 24 `<div>/@type` optional ins Hauptschema; ADR-013-Ausnahme nested `<hi>` wieder erlaubt; `ingest/<sigle>/`-Konvention.** WZB live in beiden Indexen; **#94 Authority-Cache-Bug gefixt (selbstreferenzieller Versionsvergleich).**

**2026-05-11 (sechs Parallel-Sessions):** Playground Release 1 (#87-90 Wortfrequenz/Text-Statistiken/Lemma-Verteilung), #20 Lesbarkeit, #96 Reader-Download, #26 pb-Insertion (1293 `<pb>` über 14 Files, `795670240`), #78 `hilfe-schema.html` + Prism gevendort, #79 closed (5 Hilfe-Seiten), #47.1/.2 + #86-Barrierefreiheit-Draft, KZW-Loop #102/#103/#85. **`docs/data/linecode-templates.csv` (665 Templates) als kanonische Quelle – Lehre: Templates nie aus Daten ableiten.** JOURNAL 937→458 komprimiert.

**2026-05-12 (Julia + Playground-Wave):** #73 Lemma-Linking MWB+Lexer via Wörterbuchnetz-API (`dcbee3479`; Julias statischer Link war POST-only/defekt), #101 Reading-View-Render-Policy (Julia), #105 Authority-Counter 7→8, **#47.3 Versposition-Suche – Corpus-Index v4.0.1→v4.1.0 mit `lineStarts[]`/`lineEnds[]` (1,36M `<l>`)**, #47 R2 Begriffs-Verteilung, #47-Umbrella closed (#107/#108/#109 ausgelagert). Index-Versions-Drift strukturell gelöst (`check-index-versions.py` + CI + Memory, drei Stellen). #23 Stanza-Bulk (93 Texte, 11.090 `<lg>`, v4.1.1). Concept-Distribution-Perf-Patch 2747ms→60-200ms (MessageChannel-Chunking, nicht `setTimeout(0)`).

**2026-05-14/15/16 (Playground-Abschluss + Audits):** #112/#108/#107/#113 live (Verse-Click-Highlight, Textvergleich, Kookkurrenz-Ranking, Autocomplete), #110 WVV-Stanza, #104 Sigle-Gruppierung (Empfehlung: Titel statt Merge), #81 closed. **Lehre `Closes`-Trailer nur bei vollständig fertig** (#110-Reopen). Audit-driven Preparation als Pattern; Autocomplete-Helper zentralisiert.

**2026-05-28 (Großtag):** #113-Followup (`concepts.xml` Alternative-Terms vom Primär getrennt, Last-Wins-Bug; Authority-Index v1.3.0, `f7c8592c2`), #114 Tabellenansicht (Spec+Plan → Subagent-driven 11 Tasks/13 Commits), **CI `index-version-check` Timeout 2→10 min (war seit 05-12 still disabled)**, `.md`-Vereinheitlichung (9 Renames + 226 Cross-Refs), Single-Source Index-Versionen (TEI-MODEL §11). **Authority-Cross-Ref-Audit: 226.863 unresolved Refs (225.886 auf variants.xml) → #115; pb-Backlog 606 Texte → #116.**

**2026-05-29 (Authority-Drift Root Cause):** Repo ist alleiniger Master (transformation→active). Cross-Ref unresolved 226.863→977. **`variants.xml` ist korpus-abgeleitet und war stale (64.287 Formen fehlten); neuer Generator `extract-variants.py` → 192.472→256.759 Formen, Authority-Index v1.3.0→v1.4.0.** Negative type-IDs = Interpunktion, totes `@corresp` gedroppt (14.895 über 296 Files). Cross-Ref-Audit als CI-Gate, Data-Change-Lifecycle in Docs. Savepoints `0867a370f`, `e21d84bd6`.

**2026-06-01/02/03 (Site-Chrome + Paritätstests):** Site-Chrome-Refactor gemerged (`2e8d48d95`) – build-injizierte Nav/Footer (`includes/` + `build-pages.py`), #8 Mobile-Menü zentralisiert, `clearSiteData` delete-by-name. #130 Lemma-Match zentralisiert (`lemma-match.js`, §B.1 token-exakt), #131 Position-Counting-Paritätstest (§B; Leer-`<w>` JS→Python angeglichen, `7491e97b3`). Zwei Health-Checks; Doc-Schuld-Lehre (Build-Pipeline-Erweiterungen gehören in DEVELOPMENT+ARCHITECTURE).

**2026-06-05/09 (Health-Check + Re-Triage):** Multi-Agent-Check (103 Agenten): Doku hing Playground-Wachstum hinterher, ~24 Drifts gefixt, fabrizierte Worked-Examples korrigiert; **8 Blind-Spots, 1 blocking → #132 (Ingest-Verfahren in Stable-Doc), #133.** #44-Re-Triage (37 Issues): kein Bewertungs-, sondern Umsetzungs-Rückstand; #30/#34/#73 closed, #138/#139 angelegt. #53/#137/#135 geshippt.

**2026-06-10/11/12 (Zenodo + #59 + #117 + #125 + #138):** #91 Zenodo-DOI live (Concept `10.5281/zenodo.20627656`, v1.0.0 `…657`); Git-Tag als SSoT für Version (`41a71188a`). #59 Naming-Explorer (`naming-index.json.gz`, 10.506 Records) + ROL/TRO-Deep-Links, #117 Wörterbuch A–Z, #132 Ingest-Verfahren nach DATA-MODEL, #129 KWIC, #128/#23 closed. **#125 deterministische Index-Builds + CI-Freshness-Gate** (`data-integrity.yml`, byte-identische Rebuilds, `requirements.txt`-Pins; Corpus v4.1.4 / Authority v1.4.1, Merge `789708322`). #138 div-/lg-Wrapper (HUG/MBS), #121 Dropdown-Disambig, #136 Text-Statistiken-Auswahl.

**2026-06-17 (vier Sessions + Scorecard):** #45 Statische JSON-API gemerged (PR #150); tei_all.rng ins Repo committet statt CI-Download von tei-c.org (Ausfall-Blocker), xml-model-PIs repo-weit aufs lokale Schema (`559fd3163`). #44-Matrix-Drift korrigiert (7 geschlossene standen als aktiv); #138 HUG-Strophen geshippt (`9c9b78e83`, 814 `<lg>`, Index byte-identisch); dabei #151 entdeckt: TEI-Reader-Cache mit 30-Tage-TTL ohne Inhalts-Invalidierung. README-Drift-Audit 65 Findings (`e7f6d58f6`); **POS-TAGSET.md als SSoT herausgezogen** (`7e8ae95a2`, INDEX-Count 14→15). 47-Agent-Health-Check: 0 blocking, Algorithmus-/XPath-Checks konform, ~24 Count-Drifts gefixt (`54e6d64d0`) → Action-Item #152. **#124 cookieloses Matomo deployed** (`7abbf7672`): build-injizierte MATOMO-Region (`includes/_matomo.html`) + localStorage-Opt-out, weil das Uni-Opt-out-iframe extern HTTP 403 liefert.

**2026-07-02 (Fünf-PR-Welle):** #151 gefixt: Conditional-GET-Revalidierung (ETag/304) statt Deploy-Invalidierung (`4e0208f`); #143 `l`→`lb` für APO/HMT/HH (3.049) + HH-Genre-Fix + APO-Gattung nach Terrahe (Corpus v4.1.5, Authority v1.4.3); **pako/dexie vendored** (`ce34c81`, null Runtime-CDN-Abhängigkeiten). #106 Reim-Wörterbuch (10. Werkzeug, `lineEnds[]`-Scan, Suffix-Heuristik) + #114-Followups (Gesamtzeile, Types + MWB/Lexer-Links, Keyness-Log-Likelihood; Referenzkorpus = alle 667 Texte, auswahlunabhängig); Review härtete `escapeHtml` (Quote-Breakout) und zentralisierte den Wörterbuchnetz-Client (`assets/js/lib/woerterbuchnetz.js`). #152/#154 Daten-Drift-Gates in data-integrity.yml: lexicon-ID-Set-Ratsche (`lexicon-baseline.json`, nach Review statt Zahlenpaar), naming-Gates inkl. TOCTOU-Fix (Fetch unter resolviertem SHA), Versions-Bump-Gate. **#115 Kategorie-A-Backfill: 125 Stubs, 43.754→43.879 Lemmata** (dangling 977→396, 349→109 IDs), Authority v1.4.4. Lehren: Roundtrip-Skripte brauchen `newline=''` (CRLF hätte die 31-MB-lexicon.xml still umgeschrieben); doc-count-audit-50er-Kappung entfernt (war für Bulk-Sprünge blind).

**2026-07-08/09 (autonome Doppel-Session + Health-Check):** Issue-Session: 12 PRs #174–#185 (u. a. posAll[] v1.6.0 für 10.171 Multi-POS-Lemmata, AK-Excerpt-Banner via `biblScope unit="verse"`, drei latente §B-Paritäts-Drifts geschlossen) mit neuem Review-Triage-Pattern (Bot-Findings erst prüfen, dann fixen; 2 False Positives). Merge-Session: alle 13 PRs auf main, 13 Issues geschlossen, Live-Smoke grün. **GitHub-Mechanik-Lehren (je 2× reproduziert):** `gh pr merge --delete-branch` schließt gestackte PRs statt sie zu retargeten (Recovery: Head-SHA re-pushen → reopen → Base edit); `gh run rerun` nach Base-Retarget recycelt stale Event-Payload → Close/Reopen triggert frisch; GitHub schließt Issues auch über Development-Verknüpfung ohne Closes-Trailer (#171/#28 reopened). Health-Check 09.07.: Kernbestand drift-frei, 5 Rand-Drifts gefixt.

**2026-07-10 (Vormittag):** Reading-Nav-Kontrast-Fix nach KZW-Feedback (`6df766522`): `.reading-nav`-Komponenten in korpus.css statt Tailwind-Utilities, weil das vorkompilierte tailwind-output.css neue Klassen still verschluckt; Commit über temporäres Worktree (geteiltes Working-Dir). KZW-Rückstau-Session (5 Commits, 205/205): #110/WVV komplett (489 `<lg>` fortlaufend), #28 reopened mit 26 KWIC-Grenzfällen, #203 KWIC-CSV-Export, #204 Filter-vs-Auswahl-UX (noResults-Box konnte seit jeher nie erscheinen), #187 posAll-Anzeige-Migration. **Direktive chsteiner: Frontend vor Ingest** (CoReMA #139 später als gemeinsame Session); juliahin wieder regulär im Projekt; brevitas-Wiki ohne Lizenz = Blocker für #147.

**2026-07-10 (Nachmittag) bis 07-12 (Frontend-Welle + Review-Umstellung):** 8 PRs #205–#212 (Hapax-Werkzeug #196, Belege-Hilfeseite, 12 Python-Findings, Vers-Modus, Versendings-Profil), alle gemergt. #189 quantifiziert die Annotationslücke erstmals: 1,9 Mio. Tokens ohne `@lemmaRef`, stärkster Einzelfall `minne` mit 6.982 unsichtbaren Belegen → #216. Review-Workflow auf das code-review-Plugin mit `--model opus` (11.07.), dann Auto-Cancel beim Merge (`2d6335856`: `closed`-Trigger plus Concurrency-Group), womit das händische Canceln entfällt. Lehre: `read_text()` normalisiert Zeilenenden, die CRLF-Erhaltung in `build-pages.py` war seit jeher wirkungslos.

**2026-07-12/14 (GWTK-Pilot + erste Carearbeit):** PR #214 disambiguiert 278 rot/jung-Tokens und trifft den Goldstandard exakt; PR #215 räumt 252 Encoding-Fehler und 418 Em-Dashes aus den Docs. Erste Carearbeit-Session (PR #220, `6a9849314`): die Drift saß in Zählwörtern und Versionsangaben, nicht im Code, daraus das dritte Playbook `MASTERPLAN-CAREARBEIT-SESSION.md`. #219 Wenzelsbibel entschieden (Variante B+D, PR #221 dünnt 1.451 Dateien aus), `doc-count-audit.py` um den Zahlwort-Scan für code-abgeleitete Counts erweitert (PR #222).

**2026-07-28 (#224: es war ein Breve):** Klaus Schmidts Bug-Report führte über zwei falsche Diagnosen zum Fund: die Wenzelsbibel schreibt Umlaute mit kombinierendem Breve (U+0306), 830 Tokens, kein anderer der 667 Texte trägt eines. Fix aus drei Teilen (NFC als Schritt 0 der Normalisierung, `ŏ`/`ŭ` als Umlautzeichen in Contract A, Stufe 3 als beidseitiger Präfix-Test statt Substring-Suche), ADR-016. Lehre: die Erklärung, die den Screenshot erklärt, ist nicht dieselbe, die auch das Ausbleiben des erwarteten Treffers erklärt.

**2026-07-28/29 (Merge-Session + die Gate-Lehre):** vier PRs auf `main` (#241 Em-Dash-Gate, #238 kaputte Tilden, #243 814 HUG-Strophenziffern, #240). Dreimal hintereinander ein Audit-Eintrag, der grün lief und nichts fing; jedes Mal deckte erst die Mutation es auf. Daraus die Regel **ein grünes Gate ist kein wirksames Gate**, solange niemand den Fehler einbaut, den es fangen soll. Authority-Index 1.6.4, Korpus-Index 4.1.8.

**2026-07-29 (#169 Nähesuche + Playground-Aufräumrunde):** „innerhalb N Wörter" misst ab jetzt die Spanne aller Treffer statt den Abstand zum Anker; Trefferzahlen aus Suchen mit drei oder mehr Lemmata sind mit älteren nicht vergleichbar (Zäsur datiert). Das Fast-Path-Dictionary in `tei-ui.js` gestrichen: 5 von 11 Einträgen lösten falsch auf, „bier" lieferte Birnen. Acht Funktionen ohne Aufrufer entfernt; doppelte Lemma-IDs ließen beide Kookkurrenz-Modi degenerieren, der Guard sitzt jetzt in der Datenschicht. PRs #245/#246/#247/#254, `main` auf `ba6ba8e5c`, neues Issue #251. Dead end: ein Mutationsbeweis, der zwei Änderungen gleichzeitig zurücknahm und deshalb weniger zeigte als behauptet. ParzivAI-Wissen aus einer nie committeten Handover-Notiz in RESEARCH/INDEX/ROADMAP überführt (kein ADR: ein externes Projekt zur Kenntnis zu nehmen hat keine Repo-Folgen).

**2026-07-29/30 (#236 Frauenlob):** Die Parallelüberlieferung war beim Linecode-zu-TEI-Import verlorengegangen und ließ sich aus KZWs Legacy-Ordnern rekonstruieren statt am Druck zu prüfen: 23 gleichrangige Töne auf 10 zusammengeführt, 36 `<div type="parallel">`, 1.563 von 9.595 Versen als Parallelüberlieferung erkennbar. Vier Review-Runden mit je genau einem echten Befund, gemergt als `115c3a01f` (Korpus 4.2.0 / Authority 1.6.5), Folgefrage als #255. Lehren: ein Verifikationsskript darf nicht die Struktur voraussetzen, die es prüft; ein Skript-Fehler wird im Skript repariert und die Datei neu erzeugt, sonst laufen Skript und Bestand auseinander (die Kette 02–05 ist damit als reproduzierbar belegt, nicht nur als idempotent). Gegen die Zweitmeinung entschieden und selbst gemessen (51 statt 60 `parallel`, 1.406 statt 1.360 `song`). #251 als PR #256 gemergt (`b8aa68472`). `use_sticky_comment` einen halben Tag lang probiert und verworfen (`bf505a129`): zusammen mit `track_progress` überschreibt der nächste Lauf den Befund genau dann, wenn man ihn nachlesen will, und die Historie liegt danach nur im Browser. `gh pr merge --body` zerbricht an Klammern, `--body-file` nehmen.

**2026-07-30 (#248 `sources/` + kuratiertes Lemma-Wissen):** 306 codierte Legacy-Dateien für 199 der 667 Sigel als `sources/linecode/` ins Repo, byte-identisch (`-text` in `.gitattributes`), das 9,1-GB-Restarchiv katalogisiert statt kopiert; Nebenfund `apk_free.xml` als bester Ingest-Kandidat (#262), `FnhdC/` lizenzrechtlich gesperrt. Das Lexikon bekommt drei optionale Produktionen für kuratiertes Wissen (`etym[@type="borrowing"]`, `def`, `note[@type="comment"]`), erster Fall `lemma_37818` Abba; Authority-Index 1.7.0, Schema 1.1.0.

**2026-07-31 (Doku-Tag, sechs PRs):** Der Health-Check fand die Drift bei den **code-abgeleiteten** Zahlen, nicht bei den Datenzahlen, und der Hauptbefund war das Gate selbst: ein konfiguriertes Target ohne Anker-Treffer ist derselbe blinde Fleck wie ein fehlendes Target, nur schwerer zu sehen (#276–#281). #258 erweitert die Wörterbuchnetz-Verlinkung von zwei auf fünf Wörterbücher (`8a6626c68`); teuerster Befund dabei: ein verworfenes `failed`-Flag ließ das Hapax-Werkzeug eine Netzstörung als „nicht als Lemma belegt" ausgeben, jetzt CONTRACTS §D.2 „Absence of a link is not absence of attestation". CONTRACTS §H mit nachrechenbaren Zählregeln für die Analyse-Werkzeuge (#281). #228: sieben leere `<author>`-Elemente plus vier neue Befunde aus dem neuen `check-author-refs.py` (#308), Korpus-Index 4.2.1; dabei nahm eine Maßnahme gegen Fehlalarme einen echten Alarm mit. #309: 20,13 % aller `<w>` ohne `@lemmaRef`, Abdeckung je Text 58,4 bis 100 % (Median 77,4 %), Messung als `scripts/audit/coverage-bias-check.py` beigelegt. Aufräum-Session PR #275 (Directory-Layout, `scripts/README.md` gegen das Dateisystem neu geschrieben, #274 angelegt). Drei Lehren: Aussagen über **Abwesenheit** brauchen dieselbe Prüftiefe wie der Hauptteil und zählen die ausgeschlossenen Fälle namentlich auf; eine Zahl ohne Messvorschrift wird beim „Korrigieren" falsch (Breve-Zahlen in §A, NFD oder nicht); wer eine Zahl für historisch erklärt, misst das Datum dazu statt es aus der Zahl zu erschließen.

**2026-07-31 (Nachtrag):** Die vierte Stelle, an der eine Indexversion steht, pflegte niemand, weil ihr Veralten nichts kaputt macht (#307/#312/#317). #314: ein Guard hatte 1300 Zeilen toten Code konserviert, und ein Test war falsch-grün. Lehre daraus: ein Rückbau kann eine Aufräumfunktion mit abschalten, die niemand als solche gelesen hat.

**2026-08-02 (Aufräum-Session, fünf PRs, und die Hälfte der Review-Last war hausgemacht):** 18 Review-Läufe, 27 Befunde, davon 10 echte Defekte, **13 falsche Tatsachenbehauptungen in selbst geschriebenen Kommentaren**, 4 Kosmetik. Daraus die Selbstverpflichtung in CLAUDE.md: jede Zahl in einem Kommentar wird gemessen, ab Runde 3 nur noch Verhaltensbefunde. Savepoint `ce55dde0a`. Am Abend die Rollentrennung: `fable-reviewer` prüft einen fertigen Diff und hat Bash zum Nachmessen, `fable-advisor` berät bei offenen Entwurfsfragen; der Zeitpunkt entscheidet, nicht die Gründlichkeit. Savepoints `0d769c8e4`, `6a8d4caba`, `e5bd0adc9`, `fd6564bb4`.

**2026-08-03 (#316, die Doku ist englisch):** Teuerster Fund des Tickets waren **elf stille Kopplungen zwischen Doku-Prosa und Audit-Skripten**: ein übersetzter Satz kippte ein Gate. Dazu drei kaputte Ankerverweise, zwei älter als das Ticket. Der Review-Bot kam am Diff nicht vorbei, daraus die Lehre, dass die PR-Größe eine einzuplanende Eigenschaft ist und keine bloße Folge. Savepoints `011f74f9d`, `640020235`, `90cc3e49a`, `b261069cf`, `dad844b2a`.

**2026-08-05 (Label-Neuordnung 28 auf 16 + Loop Engineering):** Der Befund, der die Arbeit rechtfertigte: **30 der 52 offenen Tickets warteten auf einen Menschen, nicht auf Arbeit.** Daraus das Drei-Achsen-Schema (`auto:` / `area:` / `effort:`), gebaut für Agenten, mit der Legende im Body von #44. Savepoints `5e051105d`, `aff7fe2af`, `b59350bb5`. Am Nachmittag vier Merkregeln zu einem Wrapper-Skript und drei Playbook-Verträge zu einem zusammengezogen; die Prüfung des Wrappers kostete mehr als sein Bau, und ein Zitat eines beratenden Agenten hielt der Messung nicht stand, weshalb eine Regel unverändert blieb.

**2026-08-06/07 (ADR-017, #58, drei Entscheidungs-Tickets):** Der Lifecycle-Lauf fand nichts zu tun, und das war eine Messung, kein Leerlauf (`f3dcf2a8`). Zwei Zahlen in CONTRACTS §A waren in dieselbe Richtung falsch. #58: die Entscheidung war nicht A gegen B gegen C, sondern Schreibform gegen ID, und der Weg vom Lemma zum Beleg trägt seither eine ID. Bei #225/#111/#270 war jeweils die Entscheidung teurer als die Umsetzung; **#270 hat sich beim Messen selbst widerlegt**, und aus #111 kam vor allem eine Messvorschrift.

**2026-08-08 (#111 wird ein Gate, #193 in drei Bausteinen):** Die Zahl vom Vortag war kein Rückgang, sondern ein Einheitenwechsel; das Gate warnt seither und wird nie rot (`4195581e3`, `ea7b0a507`). #193 Baustein 1 fand ein Pferd, das als Mann klassifiziert war. Baustein 2 trägt die Lehre im Titel, „was eine Quote von 76 Prozent nicht heißt": **die Zahl, die man aus einem Abgleich herausliest, ist fast immer die falsche**, weil ihr Nenner eine andere Menge ist als die, nach der gefragt war. Baustein 3 ist der lehrreichste: das Maß erfand die Zweifelsfälle, die es finden sollte, sechs von neun gemeldeten Versen ohne Entsprechung gab es nicht, die drei Reste waren ein zu enger Suchradius. **Gefunden hat es der Berater nicht durch Nachrechnen, sondern durch Lesen.** 336 von 336 Versen danach textlich verifiziert.

**2026-08-09/10 (#59, #358, #361):** Der Naming-Explorer konnte die Frage schon beantworten, er konnte sie nur nicht stellen; das Gitter durfte bleiben, weil jetzt feststand, was es heißt, und der Deckname wurde eine vierte Kategorie statt einer Umbenennung. #358: **die Prüfung, die den Umfang ausweiten sollte, hat ihn halbiert**, über zwei eigene Messfehler hinweg, und landete bei genau dem Umfang, den das Ticket von Anfang an nannte. #361: der Defekt war eine Zeile, die Ursache ein Datenmodell (die Gattungskette ist eine Hülle, keine Hierarchie); die Reduktion gehört in den Build, nicht in die Ansicht.

**2026-08-14 (#59):** Die Erklärung durfte nicht vor den Daten kommen; der Zuschnitt drehte sich unter der Messung um. Drei Guards im Build, einer bewusst asymmetrisch. Das Review fand zwei grüne Prüfungen ohne Haltekraft.

**2026-08-24 (#216/#369, zwei Disambiguierungs-Serien):** Der Filter, der die schweren Fälle finden sollte, kannte kein Mittelhochdeutsch: **eine Wortliste ist dort kein Filter.** Drei Stichproben-Durchgänge über 150 Fälle ohne Fehler, und der zweite davon war wertlos. In Serie 2 waren 51 der 95 Rückhaltefälle gar kein Zweifel zwischen den beiden Kandidaten, sondern ein drittes Wort; ein zu enges Kandidatenpaar erzeugt keine falschen Annotationen, solange die Konfidenz die Notlage ausdrücken darf. Zwei Heuristiken gescheitert, beide im Log.

**2026-08-31 (drei entblockte Tickets, zwei Messaufträge, ein Datenlauf ohne Indexänderung):** Zweimal war die Messvorschrift das Byte, und **ein Diff, der zeichenweise stimmt, ist trotzdem keine Messung**. Ein Datenlauf über 46.890 Tokens ließ beide Indexe byte-identisch, der Versions-Bump stand trotzdem drin, gegen eine Regel, die derselbe Eintrag zitiert; kein Gate hätte das gefangen. Savepoints `6fbf7e002` (Bot-Turnbudget auf 100), `c0e8dee80`.

**2026-09-01/02 (Wellenlauf mit Koordination und Spur):** Der Lauf blieb seriell, weil die abgeleitete Schicht global ist; von fünf autonom antastbaren Tickets blieben nach Messung zwei startbare, und **ein Ticket kann entblockt sein und trotzdem an seiner ersten Handlung hängen** (`2adc52fc5`, `5aa3a8df3`, `8a7ea2116`, `b306d9f22`, `f3a575c77`). Dreimal saß der Fehler im Zuschnitt der Prüfung, nicht in der Rechnung. Der teuerste Fix entwertete einen Prüfpfad, den niemand nachzählte: daraus die #397-Frage in CLAUDE.md, **was hat dieser Fix wahr gemacht, das vorher falsch sein konnte** (`091335fe0`, `144fbbd3c`, `3b9abb3f9`). Der Health-Check desselben Tages fand eine Klasse statt eines Einzelfalls: dreimal stand in der Doku eine Aufgabe als offen, die längst erledigt war.

**2026-09-06 (vier Einträge, und der Rückstand ist zu einem Drittel keiner):** 1.455 Tokens neu annotiert, Korpus-Index 4.2.11 auf 4.2.13, Authority 1.9.2 auf 1.9.3; `doc-count-audit.py` hängt seither als Gate in `data-integrity.yml`. Rot: **Eindeutigkeit über einer Menge mit einem Element ist keine Eindeutigkeit**, und eine Zahl in der falschen Einheit macht eine verbuchte Altlast zu einem frischen Alarm. Abends zehn blockierte Tickets entscheidungsreif gemacht, **drei ihrer Prämissen waren abgelaufen**; nachts elf weitere Vorgänge (`2c23520`), ohne Korpus oder Authority anzufassen. Daraus die Regel, die seither in CLAUDE.md steht: **vor der Vorlage steht die Nachmessung, nicht die Zusammenfassung**, und ein Issue ist Body und Kommentare.

**2026-09-07 (TRO, drei Fixe, Aufräumlauf):** Beide TRO-Werte waren richtig, sie gehörten nur zu zwei verschiedenen Werken: `works.xml` führt einen zweiten `bibl` mit derselben Sigle. Gefunden hat es erst die #397-Frage, nicht der Abgleich. Am Nachmittag dreimal derselbe Fehler, und **zweimal war er der Fix des vorigen**: die Frage einmal zu stellen genügt nicht, wenn der Fix selbst wieder ein Fix ist. Der CI-Bot fand zwei davon bei grünem Check. Im Aufräumlauf lagen zwei falsche Doku-Stellen im toten Winkel eines Gates, das genau daneben greift.

> Full older entries preserved in journal-archive.md

---

## 2026-09-10/11 (Nachtsitzung) – Ein gemeldetes Token waren neunzehn Belege, und die Versionsnummer war schon vergeben

Drei freigegebene Vorgänge, zwei PRs, gemergt: **#427** (Escaping der
Ergebnisköpfe im Playground), **#425** (Mehrwort-Lemmata dokumentiert) in PR
#428, **#363** (Hausenblase) in PR #429.

**Der Vorgang war sechsmal so groß wie seine Meldung.** #363 meldete ein Token,
`hawssen` in MBS5 am Adjektiv *heiʒ*. Die Suche nach den Schreibformen statt nach
der gemeldeten ID findet **19 Belege in 7 Sigeln, 32 Tokens**, und alle sieben
Sigel sind Kochbücher. Von den 19 waren 5 richtig; die übrigen 14 hingen an
sieben Lemmata, darunter das Verb *hûsen* „wohnen", der *hase* und die
Mönchstonsur. Sieben Tokens trugen gar kein `@lemmaRef`. Die Bestätigung stand im
eigenen Korpus: KBL4 schreibt „ovch ist die **husen blater** vnd all **fisch
blatra** guot in sulcza", eine Apposition, keine Auslegung.

**Zweimal habe ich in diesem Vorgang behauptet, eine Mehrwort-Einheit wäre „die
erste im Korpus", und damit gegen die philologisch richtige Zuordnung
argumentiert.** Beide Male falsch, und beide Male hätte ein Blick in
`variants.xml` gereicht: das Muster gibt es seit Jahren an `lemma_3141` *Joie de
la Court*, `lemma_9250` *Schastel Marveile*, `lemma_9251` und `lemma_20598`, und
`Schastel Marveile` trägt sogar dieselbe Doppelung aus getrennter und
zusammengeschriebener Schreibung wie dieser Fall. Dokumentiert war es nirgends,
was genau der Grund ist, warum es zweimal übersehen werden konnte. Daraus wurde
#425, und `TEI-MODEL.md` §4.1a hält seit #363 auch fest, dass die Klasse nicht
auf Eigennamen beschränkt ist.

**Die Typ-Entscheidung ist der technische Kern und war beinahe ein Datenschaden.**
Ein `type_N` ist eine Schreibform *eines* Lemmas, und `extract-variants.py` löst
ein mehrdeutiges Paar per Mehrheit auf. Wer den Bestands-Typ mitnimmt, nimmt
fremde Tokens mit: `type_106683` *pleter* trägt 45 Tokens, 43 davon bleiben bei
`lemma_737` *blat*. Das Skript entscheidet deshalb je Form am gescannten Korpus,
5 umgehängt und 10 neu geprägt, und `extract-variants` bestätigt es von der
anderen Seite mit **0 Typen an mehr als einem Lemma**.

**Der teure Fehler war ein anderer: die Versionsnummer war schon vergeben.** #363
ist mit Korpus 4.2.14 und Authority 1.9.4 gemergt worden, während der offene PR
#416 genau diese beiden Nummern seit seinem Rebase vom 09.09. trug. Kosten, mit
`git merge-tree` gemessen: acht Konfliktdateien in Julias PR, allesamt
abgeleitete Schicht plus Versionsliterale, dazu Umnummerierung und ein
vollständiger Rebuild auf fremdem Branch. Die Quelldaten mischen sich sauber.
**Kein Gate deckt das ab, und beide waren auf beiden Seiten grün:**
`check-index-versions.py` prüft Konsistenz *innerhalb* eines Arbeitsstands, das
#154-Bump-Gate nur, *dass* gebumpt wurde. Regel steht jetzt im
Data-Change-Lifecycle, Befund als Kommentar an #416.

**Die zweite Lehre ist eine über Zahlen an ausgelieferten Seiten.** Eine
Lemma-Löschung verschiebt vier Zähler, und die stehen an 36 Stellen in 15
Dateien, einschließlich des Stats-Blocks der Startseite. `doc-count-audit.py`
läuft nur in `validate` und steht nicht in der Schrittfolge des Lifecycles, ist
also erst in der CI rot geworden. Danach hat der Review-Bot zweimal nachgesetzt,
und beide Male am selben Muster: meine Gate-Erweiterung war für zwei von drei
Dateien wirkungslos, weil der Anker `Lemmata` „Lexikoneinträge" nicht trifft, und
nach dem Ankerfix meldete eine Datei Abdeckung, ohne zu prüfen, weil „rund" vor
einer exakten Zahl den Rundungs-Skip auslöst. **Ein Target, das Abdeckung meldet
und schweigt, ist schlechter als eines, das fehlt.** Jede der drei Bindungen ist
jetzt mit eigener Mutationsprobe belegt.

**Scorecard Doku-Check 2026-09-11** (Trigger: drei PRs an `docs/`). Flow der
geänderten Abschnitte gelesen, drei Algorithmen gegen den Code (Positionszählung
gegen `extract_word_data`, Drei-Stufen-Auflösung gegen `resolveLemmaIds` plus
`lemma-resolve.js`, Auto-Match gegen `wzb-auto-match.py`): alle drei
deckungsgleich. Vier XPaths der Build Script XPath Reference gegen
`build-authority-index.py`, samt relativer Achsen: exakt. Alle Zähl-Gates grün.
**Drei Befunde, behoben:** `POS-TAGSET.md` sagte als einzige Quelle der Wahrheit
für `@pos` nichts zu Mehrwort-Einheiten, obwohl #363 dort 32 Tags vergeben hat
(neuer §7: `@pos` bleibt Eigenschaft des Tokens, *Joie de la Court* liest
`NAM PRP ART NAM`); die Glosse zu *hûsenblâter* warf die Blase mit dem daraus
gewonnenen isinglass zusammen; „the four names above" stand hinter einer Liste
von fünf. **Ein Befund offen, weil er eine Entscheidung braucht:**
`scripts/README.md` sagt, ein issue-gebundenes Einmal-Skript wandere nach
`_archived/`, sobald sein Issue geschlossen ist, die Praxis in
`scripts/ingest/pos-disambig/` tut das nicht (`fix-367-waeren.py` liegt dort bei
geschlossenem #367, und `fix-363-hausenblase.py` jetzt ebenso). Entweder die
Regel gilt dort auch, oder sie ist auf die Wurzel einzugrenzen: als #430
abgelegt, weil zwei nebeneinanderstehende Fassungen jede Session neu entscheiden
lassen.

**Phase:** Betrieb. Offen und auf Menschen wartend: #416 (zwei Antworten, dazu
die Versionskollision), #252, #366 (jetzt acht Formen statt sieben, weil
`KDO_121170100_3` erledigt ist und die beiden `hawsen`-Belege aus #363
zurückkamen: sie sind der Fisch, nicht die Blase), #410, #419.
## 2026-09-11 – #198 Schritt 2 zugestellt: die Entscheidung war eine Messfrage, das Problem war die Zustellung

**Summary:** Schritt 2 von #198 ist auf `main`. Das `<pos>NOM</pos>` ist aus `lemma_2598` *haben* entfernt, die drei seit PR #205 zurueckgehaltenen NOM-Tokens sind entschieden, und der Sense-Split, der hier seit Juli als die eine offene philologische Frage stand, findet nicht statt. Korpus-Index 4.2.15, Authority-Index 1.9.5. Die inhaltliche Arbeit ist Julias Commit `a1089cb6c` vom 21.08.2026; die Messungen unten sind am 11.09. gegen den gemergten Stand neu gerechnet, drei Zahlen haben dabei nicht gehalten.

**Die Frage war seit Juli als kuratorisch etikettiert und liess sich messen.** „Welche der acht `<sense>` von *haben* sind nominal und gehoeren zu *habe*" klingt nach einer Lesart-Entscheidung. Schluesselt man jeden Sense nach den `@pos` seiner Korpusbelege auf, ist die Antwort eindeutig: alle acht sind ausschliesslich verbal belegt. Es gibt damit keinen Sense, der umziehen muesste.

**Die Reihenfolge ist der eigentliche Inhalt des Schrittes.** Solange ein `<w>` unter `lemma_2598` ein `NOM` traegt, widerspraeche ein Lexikon ohne `<pos>NOM</pos>` dem Korpus. Erst die drei Faelle, dann die eine Zeile: `AC3_23010_1` („hawe vnd schaufel", Geraetepaar als Satzsubjekt) auf `lemma_9644` *houwe*, `DA_8222_3` („daz er dehein habe gesehen / diu bezzer waere") auf `lemma_2593`, weil `dehein habe` eine saubere NP ist und das feminine `diu` mit *habe* kongruiert, `JT_6192000_1` verbal wegen Konjunktiv mit Akkusativobjekt. Gegenprobe danach: null NOM-Tokens unter dem Lemma.

### Drei Zahlen aus dem urspruenglichen Text haben der Nachmessung nicht standgehalten

Keine davon aendert das Ergebnis, alle drei sind nach der Hausregel „jede Zahl ist gemessen oder sie steht nicht drin" zu korrigieren.

- **„26 von 101" waren 28 von 101.** Ohne die `@ana`-Nacharbeit stuenden 28 der 101 `lemma_2593`-Tokens ohne Sense. Die 26 zaehlt nur die von #198 betroffenen Tokens, der Nenner ist die volle Menge. Gemessen: auf `main` 27 von 100 ohne `@ana`, mit diesem Schritt 3 von 101.
- **„dieselben Konzepte" ist eine Obermenge.** `lemma_2598_sense_4170` traegt `concept_21072000`, `concept_23308000` und `concept_31200000`, `lemma_2593_sense_4159` nur die ersten beiden. Das dritte Konzept ist genau das, was die Senses unterscheidet. Am Schluss aendert das nichts, es stuetzt ihn eher.
- **„ein Eintrag von 43.879" sind 43.878.** Seit #363 ist `lemma_27031` *hasenblâse* geloescht.

### Und eine Annahme, die KZWs Entscheidung widerlegt hat

Der urspruengliche Text sagte, der Typ-Id-Konflikt „kippt von selbst, sobald das *houwen*-Folgeticket die zwoelf umhaengt". Das trifft nicht zu. `AC3_23010_1` behaelt sein `@corresp` auf `type_117159`, der Typ haengt damit an zwei Lemmata (12 mal `lemma_2598`, einmal `lemma_9644`), und das ist der erste Injektivitaetsverstoss im Korpus: auf `main` gilt die Eindeutigkeit bei **256.772 von 256.772** Typ-Ids ausnahmslos. (Die Zahl stand hier zunaechst als 256.762. Das war die Messung vom 10.09., vor den zehn Typen, die #363 gepraegt hat; fortgeschrieben statt neu gerechnet, gefunden von der Reviewrunde am 11.09.)

KZW hat die dreizehn Belege am 11.09. in #418 einzeln entschieden, und sie wandern **nicht** geschlossen. Seine Tabelle nennt sechs Verbbelege, sechs zum Substantiv und einen unklaren; der unklare (`AC2_9100_9`) ist in derselben Diskussion als Verb aufgeloest worden, und zwei der Substantivbelege brauchen einen neuen Sense. Endstand also sieben zum Verb `lemma_2923` *houwen*, vier auf den bestehenden Sense von `lemma_9644`, zwei auf einen neuen Sense „Schlag" desselben Lemmas. Die Aufteilung sechs zu sechs zu eins ist KZWs, die Aufloesung auf sieben zu vier zu zwei unsere. Ob `type_117159` danach noch mehrdeutig ist, ist damit eine Folge dieser Zuordnung und keine Selbstverstaendlichkeit. Es wird nach der Umsetzung von #418 gemessen und dort festgehalten, nicht vorher behauptet.

### Ein Zeilenende haette 236.000 Scheinaenderungen ins Korpus getragen

Beim Nachtragen der vier `revisionDesc`-Eintraege hat mein eigenes Skript `tei/WZB.tei.xml` im Textmodus gelesen und geschrieben. Die Datei ist die **einzige** im Korpus mit CRLF, und der Schreibvorgang hat daraus stillschweigend LF gemacht: 235.980 Zeilen geaendert, in einem einzigen Hunk ueber die ganze Datei.

Aufgefallen ist es nur an `git diff --stat`, das fuer WZB 471.961 Zeilen meldete, wo 25 zu erwarten waren. **Kein Gate und kein Test haette das gefangen:** die XML ist aequivalent, der Index baut byte-identisch aus beiden Fassungen (nachgemessen), und `.gitattributes` setzt fuer `*.xml` ausdruecklich `-text`, git normalisiert also bewusst nicht und meldet auch nichts. Die Datei traegt ausserdem 17 Zeilen, die schon vorher LF hatten, eine pauschale Rueckumwandlung waere also ebenfalls falsch gewesen; rekonstruiert wurde zeilenweise aus den Bytes von `main`.

Die Lehre ist keine ueber Zeilenenden, sondern eine ueber Werkzeuge: wer eine Korpusdatei mit einem Texteditor-Skript anfasst, aendert mehr als die Zeile, die er meint. Fuer Eingriffe in `tei/` gilt Binaermodus oder `newline=''`, und die Gegenprobe ist die Zeilenzahl im Diff, nicht der Augenschein.

### Die Nummernkollision, zum zweiten Mal in zwei Tagen

Der Commit trug urspruenglich Korpus-Index 4.2.3 und Authority 1.9.1, nach dem Rebase vom 09.09. dann 4.2.14 und 1.9.4. Genau diese beiden Nummern hat in der Nacht auf den 11.09. der #363-Merge vergeben, waehrend dieser PR offen lag. Aufgeloest als 4.2.15 und 1.9.5, die abgeleitete Schicht neu gebaut statt zeilenweise gemerged.

Das Gate `check-index-versions.py` hat dabei einen Fehler von mir gefangen, den ich sonst gepusht haette: `corpus-loader.js` fuehrt die Authority-Version in einer **zweiten** Zeile, und ich hatte nur die Korpus-Version hochgezogen. Das ist der Nutzen dieses Gates in einem Satz.

**Die Lehre ist keine ueber Rebases, sondern eine ueber Zustellung.** Die Entscheidung war am 21.08. gefallen und gemessen; sie hat trotzdem 21 Tage lang nichts bewirkt, weil kein PR existierte, und #198 las sich in dieser Zeit weiter als eine offene Frage an Julia. Ein Commit ohne PR ist in diesem Repositorium kein Zwischenstand, sondern unsichtbar.


---
## 2026-09-11 (Nachmittag) – Anhänge nachgeholt, und zwei Zahlen, die aus zwei Mengen kamen

Diese Sitzung lief auf dem Laptop, wo GitHub-Anhänge abrufbar sind. Vorausgegangene Sitzungen bekamen dort `403` (die Begründung steht in #419: `user-attachments` liegt ausserhalb der freigegebenen Repositoriumspfade). Nachgeholt wurden die Anhänge der offenen Vorgänge. Der grösste Posten war Alans Testprotokoll in #419, dessen 15 Screenshots bis dahin niemand gesehen hatte.

**Was die Screenshots hergaben, war nicht das, was im Protokoll stand.** Alan hatte zum Reimwörterbuch notiert: „nein - die belege sind nicht da und anklickbar, und man kann kein zweites lemma ‚tot' angeben" (DOCX in #419, Testfall 8). Auf dem Bild steht `Mindest-Reimpaare 6`, und Gottfried reimt `brôt` und `tôt` fünfmal. Mit der Vorbelegung 1 kommt genau seine Antwort samt anklickbaren Belegen. Der Fehler liegt trotzdem bei uns, nur woanders: bei 0 Reimpartnern nennt die Oberfläche zwei Gründe (Kreuzreime, rein klangliche Reime), die beide nicht zutreffen, und verschweigt den eingestellten Filter, der zwei Zeilen darüber im Kopf steht. **Eine Leermeldung, die den Filter des Nutzers nicht nennt, erklärt den falschen Fall.**

**#58 ist behoben, und der Fehler war zum zweiten Mal derselbe Mechanismus.** Die Dokumentsuche zeigte die Tokenzahl des Textes als Belegzahl. Entstanden ist das nicht durch eine falsche Rechnung, sondern durch eine Aufräumarbeit: #327 entfernte ein rein schreibend gewordenes Feld, und die Anzeige fiel auf das einzige verbliebene Zahlenfeld zurück. Beim Beheben stand dieselbe Falle wieder offen, weil `totalWords` nach der Umstellung seinerseits keinen Leser mehr gehabt hätte; es ist deshalb mit entfernt. `docs/CONTRACTS.md` §C trug die alte Objektform und den Satz „What the result card shows is `totalWords`", beides jetzt nachgezogen. **Gefunden hat diese Doku-Stelle der Reviewer, nicht ich.** Wer die Gestalt eines Objekts ändert, hat die Stelle zu suchen, die diese Gestalt dokumentiert; hier stand sie in §C derselben Datei, in der auch die Suchregeln des Playgrounds stehen.

### Rote Zeilen

**Rot: die 6.418.133 gehörten zu einem anderen Lemma als die 157.** Ausgezogen als rote Zeile 22 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: eine Zuschreibung, für die ich die Quelle offen vor mir hatte.** Ausgezogen als rote Zeile 23 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, in Runde 2 desselben Reviews: „im PDF waren die Bildpositionen leer" war ein übernommener Befund, und er stimmt nicht.** Ausgezogen als rote Zeile 24 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, vierte Zeile, am selben Tag gegen dieselbe Lehre: `items[0].keys()` ist nicht das Schema.** Ausgezogen als rote Zeile 25 nach [../fehlerjournal.md](../fehlerjournal.md).

Alle vier Fehler hatten dieselbe Gestalt: eine Aussage, die aus der Nähe richtig aussieht, weil ihre Bestandteile stimmen. Die 6.418.133 war gemessen, Alans Protokoll war gelesen, der Satz über das PDF stammte von jemandem, der die Datei tatsächlich vor sich hatte, und die Kollisionsmessung lief korrekt über die Felder, die sie kannte. Falsch war jeweils die Verbindung, und viermal hat sie derselbe Reviewer gelöst, der dafür nichts wusste, was mir nicht auch zur Verfügung stand.

---
## 2026-09-14/15 (Nachtlauf) – Neun Entscheidungen waren längst gefallen, und zweimal saß die Korrektur in einer Spiegelkopie

Auftrag: die Vorgänge mit `wait:kzw` durchgehen, die beantworteten vom Warten befreien, umsetzen was dadurch frei wird, und alles ohne Entscheidung aufschreiben statt raten. Die Prämisse hat sich bestätigt, und zwar quantifizierbar: **9 von 39 Vorgängen mit `wait:kzw` trugen eine Antwort, die den ganzen offenen Rest trägt**, und keiner von ihnen hatte das Label verloren.

### Ausgangsstand, selbst gemessen

Grundmenge sind die offenen Vorgänge (`gh issue list --state open --limit 200`), Kontrollwert `evergreen` trifft genau einmal (#44), die Abfrage greift also.

| Menge | vor dem Lauf | nach dem Lauf |
|---|--:|--:|
| offene Vorgänge | 71 | 69 |
| davon `auto:blocked` | 46 | 38 |
| davon `wait:kzw` | 39 | 31 |
| `wait:*` ohne `auto:blocked` | 0 | 0 |
| `auto:blocked` ohne `wait:*` | 0 | 0 |

Die vier Zustände über den 39: **beantwortet und ausführbar 9, teilweise ausführbar 4, beantwortet mit einer neuen Frage 8, wirklich noch wartend 18.** Die Messvorschrift für die letzte Gruppe steht im #44-Kommentar, weil „wartet noch" sonst die Restmenge einer Subtraktion wäre und keine benannte Gruppe.

Die Aufteilung stand zwischendurch auf 10 und 3. **#375 war in der ersten Gruppe gelandet, weil ich den ausführbaren Teil für den ganzen Vorgang gehalten hatte**: die acht eindeutigen Belege sind umannotiert, aber Punkt 1 des dortigen Arbeitsauftrags lautet wörtlich „@wachauer: die acht Fälle der zweiten Tabelle lesen". Der Vorgang bleibt deshalb offen und geht auf `auto:blocked` mit `wait:kzw` zurück. Das ist der Fehler, den dieser Lauf strukturell begünstigt: wer nach ausführbaren Resten sucht, liest einen Auftrag darauf hin, was er tun darf, und nicht darauf, was noch fehlt.

### Der Befund des Laufs: der Header spiegelt drei Master, und nur einer war geprüft

Ein TEI-Header führt an drei Stellen Daten, deren Master woanders liegt: `msIdentifier/idno` aus `works.xml`, `listBibl/biblStruct` über `works.xml` aus Zotero, `particDesc/listPerson/persName` aus `persons.xml`. Nur der erste hatte einen Schreiber und ein Gate. **Beide ungegateten Stellen sind in dieser Nacht aufgefallen, unabhängig voneinander, und beide Male saß eine Korrektur am falschen Glied.**

**#237 AA-1.** Der Auftrag führt die Bibliographie-Korrektur in `tei/VTC.tei.xml` als „sofort ausführbar, unabhängig von allem anderen". Geschrieben, validiert, Index byte-identisch, alle Gates grün, und wirkungslos: derselbe `biblStruct` steht mit derselben `xml:id` in `authority-files/works.xml`, und ausgeliefert wird diese Fassung. `api/works/work_572.json` trägt „Josef Emler" und keinen Jireček. Die Schreibrichtung steht als Kommentar im Sync-Skript selbst (`scripts/sync/enhance_works_with_zotero.py:281-285`), wo sie für #235 schon einmal teuer gelernt wurde. **AA-1 hängt an AA-4**, und AA-4 ist Handarbeit in der Zotero-Oberfläche, also ein Posten für Christian. Zweig gesichert, kein PR.

**#308.** Die Namensansetzung für `person_1249` ging auf „Jakob von Warte", in `persons.xml`, in `works.xml` und im `titleStmt` von `tei/SJW.tei.xml`. Der `particDesc`-Block derselben Datei blieb stehen und führte weiter „Jakob von Wart" als Hauptform. Die Datei widersprach sich nach der Korrektur weiter, nur andersherum, und zwar in genau der Zeile, die der #308-Kommentar vom 06.09. als Widerspruch benannt hatte.

Der zweite Fall ist repariert und bekommt ein Gate. Gemessen über alle 667 Dateien: 666 tragen den Block, 671 Einträge sind gegen `persons.xml` prüfbar, **genau 1 Abweichung, danach 0**. Kontrollwert `person_1050` ergibt „Heinrich von Pressela" wie erwartet. `check-author-refs.py` prüft das seither und läuft als Step 7b in `data-integrity.yml`.

**Dass es dort bisher nicht lief, war keine Lücke, sondern eine Entscheidung mit einer Bedingung daran**, und die stand seit #228 in `scripts/README.md`: „Läuft bewusst nicht in der CI, solange der tote `@ref` in VOR offen ist (#308); sonst wäre der Befund ein Blocker für unbeteiligte PRs." Genau diesen `@ref` hat die Korrektur dieser Nacht behoben. Die Bedingung war erfüllt, bevor irgendjemand sie nachgeschlagen hatte; gefunden habe ich sie erst, als ich die Doku zum Skript nachziehen wollte. **Eine Bedingung, die niemand überwacht, wird still wahr.**

### Das Gate ist in beide Richtungen gelaufen, und es hatte selbst ein Loch

Drei Mutationen, je einzeln eingebaut und zurückgenommen:

| eingebauter Fehler | Meldung | exit |
|---|---|--:|
| SJW preferred zurück auf die alte Form | Spiegel veraltet 1 | 1 |
| HHP `@corresp` auf `person_999999` | Spiegel tot 1 | 1 |
| preferred-Zeile in SJW gelöscht | (nichts) | **0** |

Der dritte Fall ist der Befund der dritten Reviewrunde und der interessanteste: ein Eintrag ohne `preferred`-Zeile fiel per `continue` aus der Grundmenge, der Zähler sank von 671 auf 670, und nichts wurde rot. **Ein zählendes Gate kann eine schrumpfende Bezugsmenge nicht von einem kleineren Bestand unterscheiden, solange das Schrumpfen keine eigene Klasse hat.** Jetzt hat es eine, und der dritte Fall gibt exit 1. Heute betrifft er 0 von 671 Einträgen, es war also ein Loch im Gate und kein Fehler im Bestand.

**Und dann fand der CI-Review-Bot dasselbe Loch eine Ebene höher.** Die neue Klasse deckt einen Eintrag ohne `preferred`-Zeile ab; ein ganz gelöschtes `<person>`-Element fällt durch alle Klassen, weil sie sämtlich über vorhandene Einträge sprechen. Der Zähler sinkt still von 671 auf 670, `--check` bleibt exit 0, `schema/mhdbdb.rnc:211` erlaubt ein leeres `listPerson`, und sonst greift nichts: der Cross-Ref-Audit sucht tote Verweise, und ein gelöschter Block hat keine.

**Beim dritten Mal wird nach der Hausregel nicht weitergezählt, sondern der Mechanismus gewechselt.** Statt einer vierten Fehlerklasse über gezählten Einträgen steht dort jetzt eine Invariante, die jede Datei selbst mitbringt: jede Autoren-ID des `titleStmt` muss im `particDesc` derselben Datei stehen. Gemessen über alle 667 Dateien: 672 `titleStmt`-Autoren mit `@ref`, keine einzige Datei ohne einen, 671 `particDesc`-Einträge in 666 Dateien, null Einträge ohne zugehörigen Autor. Die Differenz ist genau ein Fall, und er heißt `VOR`. Der Unterschied zur Baseline-Zahl, die der Bot als Alternative vorschlug: **eine Invariante wächst mit dem Korpus mit, eine Zahl muss jemand nachziehen.** Mit gelöschtem Block in SJW meldet das Gate „Autor ohne Spiegel 1" und exit 1, nach Rücknahme exit 0 und `tei/` byte-identisch.

`VOR` steht dabei mit Namen und Grund im Skript statt als Zahl, und das Skript meldet die Ausnahme, sobald sie überflüssig wird. Ob die Datei ihren Autor im `particDesc` nachgetragen bekommt, ist eine Modellfrage und hier ausdrücklich nicht entschieden.

Ungeprüft bleiben, ausdrücklich vermerkt: die `alternative`-Formen und die `idno`-Zeilen desselben Blocks, und die lokale `xml:id` gegen `@corresp`.

### Umgesetzt

**#308, #375 und #432** in einem Zug, weil sie dieselbe abgeleitete Schicht anfassen. Korpus-Index 4.2.16, Authority-Index 1.9.6, ein neuer Variantentyp `type_372376` für `waeren` (nie ein bestehender umgehängt, Regel aus #367).

Wirkung am Index gemessen, alt gegen neu: `lemma_7338` 3.529 → 3.537, `lemma_7505` 36.362 → 36.354, `lemma_7779` 1.001 → 1.000, `lemma_9653` 14 → 15. Die beiden Ausgangswerte 1.001 und 14 sind genau die, die #432 nennt, was die Messung an den Vorgang bindet. `wordCount` ändert sich in 0 von 667 Texten.

**Das Gate, das #378 vorschlägt, ist einmal von Hand gelaufen.** Variantenabbildung 1.9.5 gegen 1.9.6: 0 Formen hinzugekommen, 0 entfallen, 0 umgehängt, bei 234.245 Abbildungen auf beiden Seiten. Das war genau die Art Änderung, die eine Abbildung kippen kann, und sie hat es nicht getan.

**Zwei weitere Gates sind in beide Richtungen ausgeübt worden, ohne dass jemand den Fehler eigens einbauen musste**, weil der Lauf ihn mitbrachte: `check-author-refs.py` stand vor der Korrektur auf **fünf Befunden in vier Klassen** und danach auf lauter Nullen, `doc-count-audit.py` ging über die Formenzahl erst rot und nach dem Nachziehen grün. Die fünf, am Diff nachgezählt statt aus dem Gedächtnis: ein toter `@ref` (VOR), ein Präfix-Ausreißer (WZB), ein Zeilenumbruch im Namen (LUU) und zwei Namensabweichungen (HHP, SJW). Die dokumentierte Formenzahl ist an 9 Stellen von 256.772 auf 256.773 gezogen worden; die 234.245 ausdrücklich **nicht**, weil sie eine andere Menge zählt (CONTRACTS §C).

### Frontend im Browser geprüft, nicht nur im Code

Zwei ausgelieferte Seiten tragen die Formenzahl. Vorher am Livestand: `hilfe-daten.html` zeigt „256.772 orthographischen Varianten". Nachher lokal „256.773", der Zahlenblock intakt neben „667 TEI-Texte" und „43.878 Lemmata"; `index.html` zeigt im Korpus-Übersichtsblock „256.773 / Orthographische Varianten". Beides am Bildschirm gesehen.

### #410: vier Blöcke, und die Grenze ist nicht Wichtigkeit

Der zweite Teil des Abends ist die Informationsarchitektur der Abfragespalte. Die Entscheidung lag seit dem 11.09. vor, samt der Bewertung, die sie trägt, und dem einen Nachtrag: „Ich möchte beim Aufklappen immer einen kleinen erklärenden Satz, was dieser Block beinhaltet (philologisch argumentiert, nicht technisch)."

| Block | Vorgabe | Inhalt |
|---|---|--:|
| Korpusanalysen | offen | 6 Werkzeuge |
| Register & Indizes (Authority Files) | offen | 6 Register |
| Weitere Korpusanalysen | zu | 5 Werkzeuge |
| Experimentelle Forschungsdaten | zu | 2 Datensätze |

Die Aufteilung der elf Analysewerkzeuge folgt der am 10.09. an den Eingabefeldern gemessenen Regel: sechs beginnen mit einem Wort oder Begriff, fünf mit einem Text oder einer Autor*in. **Das ist keine Wertung, sondern eine Eigenschaft der Werkzeuge**, und deshalb heißen die Blöcke „Korpusanalysen" und „Weitere Korpusanalysen" statt „zentral" und „weitere".

Auch hier vorher und nachher im Browser: am Livestand ein offener Block „TEI Textanalyse" mit elf Werkzeugen darunter zwei zugeklappte; lokal stehen beim ersten Laden die sechs Register da, während der Korpus noch lädt, und nach wenigen Sekunden kommen die Korpusanalysen dazu. Der Umschalter des dritten Blocks öffnet ihn samt Satz und fünf Werkzeugen, und die Wortfrequenz-Analyse rendert nach dem Umzug unverändert ihre Tabelle.

**Ein toter Anker, gefangen durch Nachsehen statt Annehmen.** Der Hilfe-Link des neuen Blocks zeigte im Entwurf auf `hilfe-playground.html#tei-analyse`. Den Anker gibt es nicht; die Datei führt `#weitere-werkzeuge`. Ein toter Anker springt still auf den Seitenkopf und fällt niemandem auf, also ist er genau die Sorte Fehler, die nur vor dem Schreiben billig ist.

**Das Umbenennen hat drei Gate-Bindungen stumm gelöst, und das Gate blieb dabei grün.** `doc-count-audit.py` bindet eine Zahl an ein Ankerwort: „elf TEI-Analyse-Werkzeuge" wird gegen den aus dem Code gezählten Wert geprüft, aber nur, solange das Ankerwort danebensteht. #410 benennt genau diese Wörter um. Danach meldete die Selbstprüfung des Gates drei Paare als `[no-hit]`: zweimal `README.md`, einmal `hilfe-playground.html`. Gemessen: auf `origin/main` traf das Muster in der README zweimal und in der Hilfeseite einmal, danach keinmal. **Ein Gate, das seinen Gegenstand verliert, meldet das nicht als Fehler, sondern als Zeile ohne Exit-Code**, und diese Zeile stand mitten in dreißig anderen. Die Anker sind erweitert und in beide Richtungen ausgeübt: mit „zehn Korpusanalysen" und „sieben Register und Indizes" in der README meldet das Gate beide Zeilen mit Fundstelle und gibt exit 1, nach Rücknahme exit 0 und kein `[no-hit]` mehr.

Dabei eine Falle vermieden, die das erweiterte Muster selbst aufgestellt hätte: `ANCHOR_SEP` überbrückt bis zu acht Tags, also hätte ein Satz, der auf „Abschnitt 3 und 4." endet und dem eine Überschrift „Korpusanalysen" folgt, die 4 an den Anker gebunden und das Gate rot gemacht. Der Satz steht jetzt ohne Ziffer da.

**Und ein Beinahe-Fall derselben Bauart:** das Skript, das zwölf Stellen der Hilfeseite ersetzt, suchte zunächst mit `\n` in einer Datei, die durchgehend CRLF trägt. Alle zwölf Muster hätten null Treffer gehabt, und weil das Skript bei null Treffern abbricht statt stumm Erfolg zu melden, wäre es aufgefallen; aufgefallen ist es trotzdem vorher, beim Lesen des eigenen Skripts. Die Regel dahinter steht seit dem 02.07. im Journal (`read_text()` normalisiert Zeilenenden) und seit #115 in der Roundtrip-Lehre.

**Die Hilfeseite behauptete danach die falsche Blockzugehörigkeit, und zwar für vier von neun Werkzeugen.** Abschnitt 5 sagt über die Werkzeuge, die er beschreibt, wo sie in der Abfragespalte stehen. Nach dem Umbau stimmte das für fünf und nicht für vier: Kookkurrenz-Ranking, Reim-Wörterbuch, Begriffs-Verteilung und Lemma-Verteilung sind im offenen Block gelandet, der Abschnitt schickte die Leser*innen aber geschlossen in den zugeklappten. Gefunden hat es `fable-reviewer` in Runde 1, gemessen mit lxml über die Überschriften beider Panels, und ich habe es an derselben Stelle nachgemessen, bevor ich etwas geändert habe. Repariert ist nicht der Satz, sondern der Abschnitt: zwei Gruppen, jede mit ihrem Blocknamen als Überschrift, je in der Reihenfolge der Abfragespalte. **Eine Prosa-Aussage über eine Oberfläche altert genau dann, wenn die Oberfläche sich ändert, und niemand liest bei einem Umbau die Hilfeseite mit, weil sie nicht im Diff steht.**

Dieselbe Bauart traf die Startseite: die Kachel „Korpusanalysen" führte zwei Werkzeuge auf, die im zugeklappten Block darunter liegen. Wer von der Kachel kommt und im gleichnamigen Block sucht, findet sie nicht. Und in ihrer Nachbarschaft stand „mit 10 spezialisierten Suchfunktionen". Gemessen sind es elf Korpusanalysen, sechs Register und zwei Datensätze; 10 ist keine dieser Mengen. Welche gemeint war, ist nicht rekonstruierbar, also steht dort jetzt keine Zahl statt einer geratenen.

Beide Zweige sind gemergt: PR #438 (Daten und Gate) und PR #439 (#410), jeder mit vier grünen Checks und je einer Runde des CI-Bots ohne Befund. Der Bot hat auf #438 die beiden Befunde geliefert, die diese Nacht am teuersten waren.

### Was über den Einzelfall hinausgilt

| Aussage | Herkunft | verankert in |
|---|---|---|
| Ein Name kann mehrere Entitäten bezeichnen; das ist normal und wird über mehrere Senses am selben Lemma abgebildet, nicht über ein eigenes Lemma | #357 | `docs/DECISIONS.md` ADR-020 |
| Echte Ambiguität in der Variantenauflösung wird nicht durch einen Tiebreak aufgelöst: alle Kandidaten bleiben erhalten, sortiert nach der Häufigkeit genau dieser normalisierten Form unter dem jeweiligen Lemma | #378 | `docs/DECISIONS.md` ADR-021 („entschieden, nicht umgesetzt") plus ein Zeiger in `docs/CONTRACTS.md` §C |
| Bei zwei belegten Namensformen ist die historische die Hauptform und die modernisierte die Alternative; wo eine Normdatei ansetzt, folgt die Hauptform ihr | #308 | `docs/CONTRACTS.md` §F.5 |
| **Nicht verankert:** dass eine Bibliographie-Korrektur bei Zotero anfangen muss und nicht im TEI-Header | Befund dieser Nacht an #237 | steht als Kommentar im Sync-Skript und jetzt im Vorgang; gehört als §F-Abschnitt in `docs/CONTRACTS.md`, ist aber eine Vertragsänderung und braucht eine Entscheidung |

§F.5 ist der Abschnitt, der ohne die Zahlen daneben falsch gelernt würde. Gezählt über `persons.xml`, `works.xml` und `tei/` am Stand vor der Korrektur, mit der Regel, dass ein Name nur zählt, wo er nicht Präfix eines längeren ist: Pressela 7, Breslau 2, Warte 7, Wart 2. **Bei HHP war die Hauptform auch die häufigere, bei SJW die seltenere.** Wer aus „wovon haben wir mehr" argumentiert, bekommt beide Fälle richtig und den nächsten falsch.

### Rote Zeilen

**Rot: der #252-Kommentar ging mit den Zahlen von vor der Gegenprobe hinaus.** Ausgezogen als rote Zeile 26 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, zweiter Teil desselben Vorgangs, gegen eine eigene Lehre von vor acht Tagen: Eindeutigkeit aus drei Stichproben.** Ausgezogen als rote Zeile 27 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, und die unangenehmste: derselbe Fehlermodus zweimal in derselben Nacht, drei Stunden auseinander.** Ausgezogen als rote Zeile 28 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: das Datum 2026-09-15 stand an sieben Stellen und war erschlossen, nicht abgelesen.** Ausgezogen als rote Zeile 29 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, eigener Regelverstoß, und zwar zweimal in derselben Nacht aus derselben Familie.** Ausgezogen als rote Zeile 30 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: das Umbauskript hat den Abschnitt aus seinen Teilen neu zusammengesetzt, und was kein Teil war, fiel weg.** Ausgezogen als rote Zeile 31 nach [../fehlerjournal.md](../fehlerjournal.md).

Zwei Dinge daran sind über den Fall hinaus brauchbar. Erstens hätte **ein Größenvergleich es nicht gefangen**: der neue Abschnitt ist mit 12.381 Zeichen größer als der alte mit 12.132, weil zwei Gruppenüberschriften dazukamen. Ein Verlust und ein Zuwachs im selben Diff heben sich in jeder Kennzahl auf, die nur zählt. Zweitens war die brauchbare Gegenprobe ein **Inventar der Top-Level-Elemente** vorher gegen nachher, und die habe ich erst gezogen, nachdem der Reviewer die eine Box benannt hatte: sie hat dann bestätigt, dass es bei dieser einen blieb. **Wer einen Befund über ein verlorenes Element bekommt, prüft nicht das Element, sondern das Inventar.**

**Rot, gleicher Commit, anderer Fehlermodus: ein Deep-Link hing an einer Eigenschaft, die die Änderung aufgehoben hat.** Ausgezogen als rote Zeile 32 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: „Fifteen checks" über einer Liste mit sechzehn Einträgen.** Ausgezogen als rote Zeile 33 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, dritter eigener Regelverstoß derselben Familie, und der erste, der Text beschädigt hat.** Ausgezogen als rote Zeile 34 nach [../fehlerjournal.md](../fehlerjournal.md).

**Nicht rot, aber festzuhalten, weil sonst der Eindruck entsteht, es sei knapp gegangen.** Drei weitere Fehler sind vor dem Commit oder vor der Veröffentlichung gefangen worden und haben nichts getragen: ASCII-Ersatzschreibungen („Jirecek", „ueber") in deutscher Prosa im TEI-Header, um dem NFD-Problem auszuweichen statt es zu lösen; „1 Vorkommen" kombinierender Zeichen in VTC, was eine Aussage über U+0308 war und als Aussage über alle sieben gesuchten Zeichen dastand (richtig sind 4); und „als Befund in #44 vermerkt" im Perfekt, während der #44-Kommentar noch ungeschrieben war.

Drei weitere aus der zweiten Hälfte der Nacht, alle vor dem Commit gefangen und deshalb ohne Zählung, aber zwei davon aus einer Familie, die es wert ist: der neue Abschnitt der Hilfeseite verwies auf `#versposition`, während der Anker `verse-position` heißt (derselbe Fehlertyp wie `#tei-analyse` drei Stunden vorher, nur diesmal vor dem Lauf des Skripts gefangen, weil ich die Ankerliste vorher gemessen habe statt sie zu erinnern); die Ausnahme im neuen Gate begründete sich mit „`VOR` führt als einzige keinen `particDesc`-Block", was falsch ist, denn die Datei hat einen `particDesc` mit leerem `<listPerson/>`, und aufgefallen ist es nur, weil die Mutationsprobe an ihrer eigenen Vorbedingung scheiterte; und der erste Entwurf desselben Abschnitts schrieb „Die elf Korpusanalysen" in eine Seite, aus der die Werkzeugzahl am 02.09. ausdrücklich herausgenommen worden war, weil sie dort niemand nachzieht. **Der letzte ist die unangenehmste Sorte: eine Entscheidung, gegen die man verstößt, ohne sie zu kennen.** Gefunden hat sie nicht mein Gedächtnis, sondern das Gate, das die Entscheidung als Eintrag mit Begründung führt und beim Wiedereinsetzen der Zahl „veraltete Ausnahme" meldete. **Eine Entscheidung, die nur im Journal steht, schützt niemanden; eine, die als Konfigurationszeile neben ihrem Gate steht, meldet sich von selbst.**

**Und der Fall, an dem die Regel sichtbar gearbeitet hat.** Für die Einordnung des neuen CI-Schritts hatte ich „rund zwei Sekunden" geschrieben und ihn in den billigen Block gelegt. Gemessen: 1 min 47 s und in einem zweiten Lauf 1 min 44 s, weil das Skript jede der 667 Dateien ganz parst, während der Nachbarschritt per `iterparse` nach 0,7 s fertig ist. Faktor 50 daneben, und die Zahl hätte eine Entscheidung getragen, nämlich die Position im Workflow. Gefangen hat es niemand: die Zahl ist gemessen worden, weil sie in eine Datei sollte. **Das ist der billigste Fang des Laufs, und er kostet eine Zeile vor dem Schreiben statt einer Reviewrunde danach.** Nachtrag vom Ende der Nacht, und er dreht die Lehre noch einmal weiter: der erste Lauf des Schritts auf `main` brauchte **32 Sekunden**, nicht 1 min 47 s (Lauf 34910635460, Schritt 21). Beide Zahlen sind gemessen, sie sprechen über verschiedene Maschinen, und dokumentiert war die lokale in einem Satz, der die Position in der CI begründet. Die Begründung trägt weiter, weil der Nachbarschritt in derselben CI unter einer Sekunde bleibt; das Verhältnis entscheidet, nicht der Absolutwert. **Eine selbst gemessene Zahl kann trotzdem über die falsche Menge sprechen, und bei einer Laufzeit ist die Menge die Maschine.**

### Zwei Befunde ohne Vorgang

Beim Editieren eines TEI-Headers ist eine Textersetzung gescheitert, weil „Verfügung" dort nicht vorkomponiert steht, sondern als `u` plus kombinierendes Trema. Eine Suche über die NFC-Form findet solche Stellen nicht und meldet dabei keinen Fehler, sondern „nicht gefunden". Gemessen über alle 667 Dateien in `tei/`, für U+0300, U+0301, U+0302, U+0308, U+030A, U+030C und U+0327: **568 Dateien tragen mindestens eines, 1.366 Vorkommen**, Kontrollwert VTC 4, alle im `teiHeader`.

`tei/LUU.tei.xml` führt im `particDesc` die Personen-ID `person_05154796-f128-42a1-bd0d-e8335bf854e6`, korpusweit der einzige Fall dieser Form. Das `@corresp` daneben löst korrekt auf, der Name stimmt. Nicht angefasst, weil eine `xml:id` ein möglicher Deep-Link-Anker ist (#358).

Beide ohne Ticket, weil an keinem ein Arbeitspaket hängt.

### Geschlossen, je ein Satz mit dem Grund

- **#308** geschlossen, weil alle vier entschiedenen Punkte umgesetzt sind und die drei mechanischen Fälle desselben Audits mit ihnen, samt der Regel dahinter als `docs/CONTRACTS.md` §F.5 und einem Gate auf dem Spiegel, der beim Umsetzen aufgefallen ist.
- **#432** geschlossen, weil `WH_6214_3` jetzt auf `lemma_9653` hängt und die Wirkung am Index gegen die beiden Zahlen gemessen ist, die der Vorgang selbst nennt (1.001 → 1.000 und 14 → 15).
- **#375** ausdrücklich **nicht** geschlossen, obwohl der ausführbare Teil erledigt ist: Punkt 1 des dortigen Arbeitsauftrags ist eine Lesearbeit für @wachauer.
- **#410** ausdrücklich **nicht** geschlossen, obwohl umgesetzt und gemergt: die Abnahme der Oberfläche liegt nach dem Deploy bei ihr, und dafür gibt es die Regel, dass das Issue offen bleibt und nicht der PR.
- **#406** bleibt offen, obwohl der Auftrag „Aktualisiere die Triage" erfüllt ist: die Triage ist ein Lesedokument, und ihre sechs Positionen leben in ihren eigenen Vorgängen weiter.

### Was zurück an Christian geht

Alles hier ist liegengeblieben, weil eine Entscheidung fehlt, nicht weil die Arbeit fehlt.

1. **#237 AA-1 ist geschrieben und nicht gemergt, weil es an AA-4 hängt.** Der Auftrag führt AA-1 als „unabhängig von allem anderen", gemessen ist es das nicht: der `biblStruct` steht zweimal, und ausgeliefert wird die Fassung aus `works.xml`. AA-4 ist Handarbeit in der Zotero-Oberfläche und damit deine. Der Zweig liegt als `claude/237-aa1-vtc-biblstruct`.
2. **Die Richtung der `listBibl`-Kette braucht eine Entscheidung, bevor sie ein CONTRACTS-Abschnitt werden kann.** Dass eine Bibliographie-Korrektur bei Zotero anfangen muss, steht heute als Kommentar im Sync-Skript und im Vorgang. Als Vertragsabschnitt wäre es eine Festlegung darauf, dass der TEI-Header an dieser Stelle dauerhaft Kopie bleibt, und das ist keine Sitzungsentscheidung.
3. **#433, #434 und #435 sind `auto:checkin` und tragen im Körper ausdrückliche „Zu entscheiden"-Punkte.** Sie sind nicht angefasst worden, weil genau das der Fall ist, den der Auftrag ausschließt.
4. **#410 hat eine unbeantwortete Frage aus deinem Bewertungskommentar:** ob der aufgeklappte Zustand weiterhin im Browser gemerkt werden soll. Das Verhalten ist unverändert geblieben, weil „lass es, wie es ist" die einzige Variante ohne Entscheidung war.
5. **Soll `tei/VOR.tei.xml` seinen Autor im `particDesc` nachgetragen bekommen?** Die Datei führt als einzige ein leeres `<listPerson/>`. Das neue Gate nimmt sie namentlich aus und meldet die Ausnahme, sobald sie überflüssig wird. Ein Nachtrag wäre eine Datenänderung am Modell und keine Reparatur.
6. **#375 bleibt offen und geht zurück auf `wait:kzw`.** Die acht zu lesenden Fälle liegen als `ingest/pos-disambig/375-waeren-ausweitung/faelle.csv` bereit und warten auf eine Spalte `entscheidung`.
7. **#370 und #378 sind nicht angefasst worden**, wie im Auftrag vorgegeben. Die Entscheidung aus #378 ist als ADR-021 verankert, ausdrücklich als „entschieden, nicht umgesetzt".
8. **Der Mechanismuswechsel, den die dritte rote Zeile zu den Shell-Konventionen fällig macht, ist eine Entscheidung über deine Einstellungen und deshalb deine.** Die Regel selbst ist eindeutig und wurde dreimal gebrochen, obwohl sie gelesen war; der vorhandene Mechanismus (Skript per Write, dann `python skript.py`) ist billiger als der Einzeiler und wurde in dieser Nacht bei jeder größeren Ersetzung benutzt. Gebrochen wurde er nur bei Nebenbefehlen. Ein greifender Wechsel wäre eine `deny`-Regel auf `python -c`, die den Weg über die Datei erzwingt. Das sperrt auch die harmlosen Einzeiler, und ob dir das den Fang wert ist, kann ich nicht für dich entscheiden. Ein parsender `PreToolUse`-Hook scheidet aus: dass Einstellungen nicht mit Rückfragen gehärtet werden, ist schon entschieden.
## 2026-09-15 – #204 im Playground: der erbetene Hinweis wäre eine Zusicherung ohne Deckung gewesen

KZW hat #204 wiedereröffnet, weil eine zweite Nutzerin denselben Fehler machte wie im Juli: im Korpus-Browser nach `mori` filtern, annehmen dass damit Moriz von Craûn das Ausgangskorpus ist, Analyse starten, Gesamtkorpus-Ergebnisse bekommen. Erbeten war, den Hinweis aus der Korpussuche in den Playground zu übernehmen.

**Der Befund steht nicht im Ticket, sondern kam aus der ersten Messung: die Auswahl aus Schritt 1 hat auf die Analysen überhaupt nicht gewirkt.** Auswahl auf null Texte setzen und je Werkzeug `getCorpusTexts().length` lesen: **10 von 11 liefern trotzdem 667**. Nur die Multi-Lemma-Suche las sie, weil sie über `tei-manager.js` läuft und nicht über den Thunk in `playground-main.js`. Der Kontrollwert war dieselbe Messung an ihr: 0 Treffer bei 0 Texten, also misst die Probe wirklich etwas. **Hätte die Nutzerin „Nur diese" geklickt, wären die Zahlen genauso falsch gewesen, nur ohne sichtbaren Anlass zum Misstrauen.** Ein Hinweis allein hätte eine Wirkung versprochen, die es nicht gab.

Umgesetzt in PR #441: zwei Thunks statt einem. `selectedTextsThunk` filtert auf `includedTexts` und geht an sieben Werkzeuge, `corpusTextsThunk` bleibt bei dreien, jedes aus einem von KZW entschiedenen Grund (Hapax ist korpusweit per Definition, der Textvergleich wählt selbst, das Reim-Wörterbuch hat ein eigenes Filterfeld und bekommt die Sigle sichtbar vorbelegt statt still). Alle drei sagen das jetzt in ihrer Kopfzeile. Live nach dem Deploy gegengeprüft: Auswahl CR, Kookkurrenz „minne" ergibt 14 statt 7.161, Hapax bleibt bei 667.

### Was über den Fall hinausgilt

**Eine Änderung, die eine Menge verengt, entwertet jeden Zustand, der aus der alten Menge stammt.** Bis #204 war die Textmenge immer der ganze Korpus und konnte sich nicht ändern; jedes Werkzeug durfte deshalb gefahrlos IDs und fertige Ergebnisse über eine Auswahländerung hinweg behalten. Die Befunde mit genau dieser Wurzel, namentlich: das Reim-Wörterbuch behielt ein ohne Filter gerechnetes Ergebnis unter der neuen Filterzeile (`Filter „CR" → 667 Texte`, eine Aussage, die sich selbst widerspricht); Wortfrequenz und Versendings-Profil hielten in `state.scope` einen abgewählten Text, Ergebnis „Keine Daten" unter „Gesamtkorpus (666 Texte)"; die Text-Statistiken behielten verwaiste IDs in ihren eigenen Häkchen, `Ausgewählt: 3 / 1` neben „Keine Texte ausgewählt"; Kookkurrenz-Ranking und Begriffs-Verteilung überlebten die Auswahländerung sogar dauerhaft, weil sie ihr Ergebnis im State halten und beim Öffnen nur neu rendern. Das ist die #397-Frage in ihrer teuren Form, und sie lautet hier: **was hat diese Änderung falsch gemacht, das vorher wahr sein durfte.**

**Jede eigene Regressionsprobe hat den Zustand verfehlt, den sie bewachen sollte, und zwar dreimal aus demselben Grund: sie richtete den Zustand direkt ein, statt ihn entstehen zu lassen.** Der Kookkurrenz-Test verengte vor der ersten Suche, das Werkzeug besaß also nie ein korpusweites Ergebnis. Der Marker-Test leerte das Feld zuerst und lief damit durch den Leer-Zweig. Die Tests zum Sigle-Wechsel gingen direkt von einer Einzelauswahl in die nächste und nie über „Alle". Alle drei waren grün und prüften nichts. **Ein Test, der den Zustand setzt, prüft die Zeile darunter; ein Test, der den Weg geht, prüft den Zustand.** Der letzte Fall dieser Art hat es explizit gemacht: nach der Verlegung eines Stempels von `show()` nach `runSearch()` wäre der Tauschtest grün geblieben, ohne noch irgendetwas zuzusichern, weil er `state.result` von Hand setzte. Er geht jetzt durch eine echte Suche und misst als Kontrollwert mit, dass sie 14 liefert.

**Zwölf Reviewrunden auf einem Frontend-Diff.** Drei lokale `fable-reviewer`-Runden, die dritte davon als Audit auf den Restzustand statt als Diff-Review, dazu neun Runden des CI-Bots. Sechs der Bot-Runden trugen je einen Verhaltensbefund, die letzten drei keinen mehr. Der Audit-Auftrag war die ergiebigste Variante: statt den Bot einen Fehler nach dem anderen finden zu lassen, einmal systematisch über alle sieben umgestellten Werkzeuge. Er fand den Fehler in der Korrektur des vorigen Befunds, nämlich einen Stempel, der die Textmenge beim Anzeigen festhielt statt beim Rechnen.

### Rote Zeile

**Rot: eine Pluralstelle repariert und den Satz daneben nicht mitgelesen.** Ausgezogen als rote Zeile 35 nach [../fehlerjournal.md](../fehlerjournal.md).

Die Korrektur ist dann größer ausgefallen als der Befund. Statt die zwei gemeldeten Stellen zu flicken, alle gesucht, die eine Textzahl in einen Satz setzen: fünf konnten seit #204 eine Eins tragen, drei konnten es schon vorher und bleiben unberührt, weil sie nicht in diesen PR gehören. **Wer eine Grammatikstelle gemeldet bekommt, sucht nicht die Stelle, sondern ihre Klasse** – derselbe Griff wie beim Inventar statt des verlorenen Elements am 14.09.

### Offen

#204 bleibt offen bis zur Abnahme durch @wachauer und steht auf `auto:blocked` + `wait:kzw`. #442 hält fest, was dieser PR bewusst nicht löst: ändert man die Auswahl bei offenem Werkzeug, folgt dessen Ergebnis erst beim nächsten Öffnen. Das betrifft alle acht auswahlabhängigen Werkzeuge gleich und ist eine Entscheidung über den ganzen Playground.
