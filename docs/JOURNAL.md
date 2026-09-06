# MHDBDB Development Journal

Chronological log of development decisions, dead ends, and savepoints. Not a changelog – captures the *reasoning* behind changes.

---

## Verdichtete Historie

Hochrangiger Trace der Einträge 2025-02 bis 2026-07-31. Volltext aller 95 verdichteten Einträge in `journal-archive.md`.

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

> Full older entries preserved in journal-archive.md

---

## 2026-07-31 – Die vierte Stelle, die niemand pflegt, weil sie nichts kaputt macht

**Summary:** Der Authority-Index wurde für #307 auf 1.8.0 gebumpt. Die drei Stellen, die dabei immer angefasst werden (Build-Skript, `corpus-loader.js`, `TEI-MODEL.md` §11), waren alle korrekt. Die unabhängige Gegenprüfung fand eine vierte: `docs/INDEX.md` nannte „Corpus Index v4.2.0, Authority Index v1.7.0" und lag damit schon **vor** diesem Branch zwei Minor-Versionen zurück.

**Warum das interessant ist:** die Pflegeanweisung existierte. `TEI-MODEL.md` §11 nennt die Stelle ausdrücklich („Pflege bei jedem Index-Bump: hier, in `corpus-loader.js`, im Build-Skript, in INDEX.md §Status"). Sie stand da, sie war richtig, und sie hat nicht geholfen. Die drei anderen Stellen werden gepflegt, weil ihr Auseinanderlaufen etwas kaputt macht: der Cache invalidiert nicht, Nutzer bekommen den neuen Index nie zu sehen, und ein Gate meldet es. Die vierte Stelle bricht nichts. Sie wird still falsch.

`check-index-versions.py` prüft deshalb jetzt acht Stellen statt vier, die beiden Doku-Angaben eingeschlossen. Belegt mit zwei Mutationen (INDEX.md 1.8.0 → 1.7.0, TEI-MODEL 4.2.1 → 4.2.0, beide Exit 1, danach wieder 0). Eine Doku-Notiz mehr hätte das nicht verhindert, denn die Notiz war ja schon da.

**Der übertragbare Teil ist nicht der Merksatz, sondern der Beleg:** die korrekte Pflegeanweisung existierte und hat nichts verhindert. Das entkräftet den Reflex, in solchen Fällen noch eine Doku-Notiz zu schreiben. Derselbe Schluss trägt den Umlaut-Befund desselben Tages (#317).

**Phase:** Betrieb. PR #312.

---

## 2026-07-31 – #314: Der Guard, der 1300 Zeilen konserviert hat

**Summary:** Der Playground trug einen vollständigen Datei-Upload-Pfad, den seit dem Redesign niemand mehr erreichen konnte: Datei einlesen, XML-DOM parsen, in IndexedDB ablegen, darin suchen, Ergebnisse rendern. Rund 2200 Zeilen über 19 Dateien, drei davon ganz gelöscht. Ausgangspunkt war ein Beschriftungs-Issue: drei Varianten, wie man den Upload-Knopf besser benennt. Die Bestandsaufnahme davor ergab, dass es den Knopf nicht mehr gibt.

**Warum es niemandem aufgefallen ist.** `setupFileUpload()` prüfte auf `#uploadZone` und kehrte still zurück, wenn das Element fehlte. Der Guard war als Robustheit gemeint, für eine Seite ohne Upload-Bereich. Als das Redesign den Bereich entfernte, hat er genau seine Aufgabe erfüllt und dabei den ganzen dahinterliegenden Zweig konserviert: keine Exception, kein Konsolenfehler, nichts, was jemandem aufgefallen wäre. Ein Guard macht Code robust gegen fehlende Voraussetzungen und damit zugleich unauffällig, wenn die Voraussetzung dauerhaft fehlt.

Dazu kam ein zweiter Mechanismus, und der ist der unangenehmere. `corpus.spec.js` prüfte `typeof teiManager.loadCorpusIntoPlayground === 'function'`. Diese Methode hatte im Produktivcode null Aufrufer; der Test war ihr einziger Nutzer. Ein Test, der nur die Existenz einer Funktion behauptet, hält sie am Leben, ohne je zu zeigen, dass sie gebraucht wird. Er sieht wie Absicherung aus und wirkt wie ein Anker. Dasselbe für `test.html`: dort instanziierten zwei Suites `TEIStorageManager` und `IndexedDBManager` direkt, also an der UI vorbei. Beide waren grün, während der Pfad, den sie prüfen sollten, aus der Oberfläche verschwunden war.

Belegt war der Tod des Pfads dann dreifach: kein `#uploadZone` in irgendeinem HTML, zwei aufruferlose Einstiege, und ein Aufruf auf `getStorageStats()`, eine Methode, die es nicht gibt. Der letzte Punkt ist der stärkste Beweis: wäre der Code je gelaufen, hätte er an dieser Stelle geworfen.

**Ein Test war falsch-grün, und zwar auf lehrreiche Weise.** `playground.spec.js` klickte „Clear Storage" und prüfte, ob danach „Cleared" in der Konsolenausgabe steht. Der Button loggt „Storage cleared", klein geschrieben. Das gesuchte „Cleared" mit großem C stammte aus `clearAllCachedFiles()` im Upload-Pfad und stand dort nur, weil derselbe Test zwei Zeilen vorher „Run Tests Again" gedrückt hatte. Der Test war also seit jeher grün, ohne den Button je zu prüfen. Aufgefallen ist das erst, als der Rückbau die fremde Quelle entfernte. Beim Aufräumen fallen fremde Fehlalarme an, und wer sie nur wieder grün macht, verschenkt den einzigen Moment, in dem sie sichtbar werden.

**Mein eigener Fehler war der teuerste Teil.** Beim Blockschnitt in `ui-helpers.js` lief der Schnitt von `updateTEIOverview` bis zur nächsten Abschnittsmarke. Dazwischen lag `enableAuthorityQueries()`, eine Funktion, die mit dem Upload nichts zu tun hat. Der Aufruf in `updateAllUI` blieb stehen, die Definition fehlte, `updateAllUI` brach ab, alle sechs Authority-Buttons blieben `disabled`: 34 gescheiterte Tests und ein 45-Minuten-Lauf, der zur Hälfte Timeouts abgewartet hat. Bei den anderen sechs Dateien war nach jedem Schnitt auf Restverweise geprüft worden, hier nicht. Genau diese Prüfung hätte den Fehler sofort gezeigt, denn der Aufruf stand ja noch da. Anker schützen davor, an der falschen Stelle anzusetzen, nicht davor, zwischen zwei richtigen Ankern etwas Fremdes einzuschließen. Dieselbe Falle schnappte in kleiner Form ein zweites Mal zu, als ein Schnittende auf das erste `});` traf, das zum inneren `page.evaluate` gehörte: dort fing es `node --check` sofort ab. Der Unterschied zwischen den beiden Fällen ist nicht die Sorgfalt, sondern ob eine billige Prüfung dazwischenlag.

Ein drittes Mal schnappte sie latent zu, und dieses Mal hat nur die Zweitmeinung sie gesehen: `waitFor()` in `test-utils.js` ruft `this.sleep()` auf, und `sleep()` fiel mit dem Upload-Pfad weg. Es brach nichts, weil `waitFor` selbst keinen Aufrufer hat. Latente Brüche dieser Art sind der Normalfall beim Aufräumen in Hilfsdateien, und kein Testlauf zeigt sie an: nur wer die Aufrufkette der entfernten Funktion rückwärts verfolgt, findet sie.

**Ein Rückbau kann eine Aufräumfunktion abschalten.** `indexed-db-manager.js` verwaltete die Datenbank `MHDBDB_Playground`, die genau einen Store hatte (`tei_files`), dessen einziger Schreiber im Upload lag. Der Manager war damit gegenstandslos, aber er trug seit #280 eine Schema-Migration, die drei schreiberlose Altstores aus bestehenden Browser-Datenbanken räumt. Nach Teil 1 instanziierte kein Produktivcode mehr den Manager, also lief diese Migration nicht mehr: der Rückbau hätte still eine gerade erst ausgelieferte Aufräumfunktion deaktiviert. Statt 397 Zeilen Schema-Pflege für eine Datenbank ohne Schreiber löscht `playground-main.js` sie jetzt beim Start einmalig. Das ist gründlicher als die Migration und kostet zehn Zeilen. Die Lehre gilt über den Fall hinaus: wer den letzten Importeur eines Moduls entfernt, entfernt auch alle Nebenwirkungen, die dieses Modul beim Laden oder Initialisieren hatte, und die stehen selten im Namen der Funktion.

**Phase:** Betrieb, reiner Code-Rückbau. Keine Daten-, Index- oder API-Änderung, kein Rebuild, kein Versions-Bump. Doku nachgezogen in ARCHITECTURE (Storage-Abschnitt), CONTRACTS §E, DECISIONS, ROADMAP, `playground/readme.md`. PR #324.

---

## 2026-08-02 – Autonome Aufräum-Session: fünf PRs, und die Hälfte der Review-Last war hausgemacht

**Summary:** Ein Tag Restarbeit aus dem Health Check vom 31.07. und aus den Aufräumbefunden #325/#327/#329. Gemergt: #330 (drei Aufräumbefunde, eine Fehlerklasse), #332 (die zweite Inventar-Tabelle hatte denselben Zustand), #333 (der Konsolen-Fehler-Test konnte nicht sehen, wogegen er schützt), #334 (#322, acht TEI-Header), #335 (#315/#318, Doku-Restposten). #336 (#316, INDEX.md) lag am Abend als PR vor.

### Die teuerste Erkenntnis kam aus einer Frage von chsteiner

„Kann es sein, dass wir over-reviewen? Bewerte das mit Zahlen und kritisch." Gemessen über die drei PRs des Tages (#330, #332, #333): **18 Review-Läufe, 27 Befunde. Davon 10 echte Defekte, 13 falsche Tatsachenbehauptungen in selbst geschriebenen Kommentaren, 4 Kosmetik.**

Die 13 sind der eigentliche Befund. Es waren durchweg Zahlen, die ich in erklärende Kommentare geschrieben und nicht gemessen hatte: „zehn weitere Stellen" statt 19, „in allen Skripten" statt 11 von 22, „der einzige Konsument" statt zwei. Jede dieser Zahlen ist eine Angriffsfläche, die ein Review pflichtgemäß prüft und meldet, und jede erzeugt eine Runde, die nichts am Verhalten ändert. Bei #332 betrafen die Runden 3 und 4 zu 100 Prozent Kommentar-Formulierungen und kosteten je rund 20 Minuten Wanduhr (7 Minuten Review plus 13 Minuten `validate`).

**Weniger reviewen ist ausdrücklich nicht die Konsequenz.** Runde 1 fand jedes Mal echte Defekte, und in #333 führte ausgerechnet ein Kommentar-Befund („zehn Stellen") zu 19 real kaputten Aufrufen. Die Konsequenz steht seither in CLAUDE.md unter „Selbst erzeugter Overhead": keine Behauptung in einen Kommentar, die nicht trägt; ab Runde 3 nur noch Verhaltensbefunde einarbeiten; kein voller CI-Lauf für reine Kommentar-Commits.

Der Tag hat die Regel danach zweimal gegen sich selbst gewendet. In #336 stand nach dem Löschen von 41 Changelog-Zeilen ein Satz über `journal-archive.md`, das sei „nur von dort verlinkt": neun Zeilen weiter verlinkte dieselbe Datei es. In #335 behauptete ein Kommentar, `names.xml` sei „die einzige doc-geprüfte Authority-Datei unter der Schwelle", und die Zeile direkt darunter fügte die zweite hinzu. Beide Male war die billigste Reparatur das Streichen des Halbsatzes, nicht das Nachzählen.

### `waitForFunction(fn, {timeout})` ist seit jeher wirkungslos gewesen

Die Signatur ist `waitForFunction(pageFunction, arg, options)`. Ohne Platzhalter landet das Options-Objekt als **Argument in der Seite**, und der Timeout gilt nie. Der Aufruf wartet dann bis zum Testbudget. Das stand an 19 Stellen in sechs Specs so, und in sechs davon lag der deklarierte Timeout unter dem Budget: dort sollte ein Wait früh mit eigener Meldung scheitern und lief in Wahrheit stumm bis zum Budget durch.

Belegt statt vermutet: mit einem eingebauten `ReferenceError` endete der Lauf vor der Korrektur nach 120 Sekunden (Test-Budget), danach nach 60 (eigener Timeout).

**Der Fix war nicht verhaltensneutral, und das ist der interessantere Teil.** An vier Stellen stand 30000 unter einem 60-Sekunden-Budget. Die Korrektur hätte diese Waits erstmals wirksam gemacht und damit still verschärft, ausgerechnet in `beforeEach`- und `beforeAll`-Hooks, wo ein Fehlschlag die ganze Datei mitreißt. Sie stehen jetzt auf 60000, mit der Begründung daneben. Nebenbei: `test.setTimeout()` läuft im Testkörper und kann einen Hook nicht mehr verlängern.

Dieselbe Klasse von stiller Wirkungslosigkeit an vier weiteren Stellen: `window._mhdbdbApp?.searchEngine !== null` ist auch dann wahr, wenn die App gar nicht existiert (`undefined !== null`).

### Ein strenger Test darf nicht an einem fremden Host hängen

#331 war, dass der Modultest seine Konsolen-Listener erst **nach** `page.goto()` registrierte und damit genau die Fehlerklasse nicht sehen konnte, gegen die er schützt. Die Reparatur (Listener davor, `pageerror` zusätzlich zu `console.error`, benannte Ausnahmen statt Freibetrag) schuf ein neues Problem, das erst die Zweitmeinung gesehen hat: der Playground zieht Matomo per Script-Injection von `webstatistics.sbg.ac.at`. Ist der Host nicht erreichbar, meldet Chromium einen Ressourcenfehler vom Typ `error`, und der Test wäre offline rot, ohne dass am Playground etwas kaputt ist.

Ausgenommen wird deshalb die **Herkunfts-URL**, nicht der Meldungstext. Ein Filter auf „Failed to load resource" hätte auch ein fehlendes lokales ES-Modul verschluckt, also genau den Fall, für den der Test existiert. Die Regel dahinter trägt über den Fall hinaus: eine Ausnahme wird an der Quelle festgemacht, nicht am Wortlaut.

### Zum dritten Mal fast eine richtige Zahl „korrigiert"

Beim Nachmessen der Verszahl kamen 1.358.973 `<l>` heraus, in der Doku standen 1.356.748. Beides ist richtig: der Index zählt nur Verse mit mindestens einem lemmatisierten Wort, weil nur die eine Boundary erzeugen. Ohne die Messvorschrift daneben wäre die richtige Angabe in eine falsche „korrigiert" worden, wie am 31.07. schon bei den Breve-Zahlen und wie bei den zwei Variantenzahlen (#279). Die Vorschrift steht jetzt in DATA-MODEL.md neben den Zahlen, samt Datumsstempel.

**Die Regel ist damit dreimal in fünf Tagen belegt: eine Zahl in der Doku ohne Angabe ihrer Zählweise ist nicht nur unprüfbar, sie zieht aktiv falsche Korrekturen an.**

### Kleinere Lehren

**Ein Gate, das nur eine von zwei gleichartigen Tabellen prüft, sieht aus wie Abdeckung.** `check-test-inventory.py` prüfte die Spec-Tabelle in DEVELOPMENT.md; die Audit-Skript-Tabelle daneben hatte 11 von 22 Einträgen. Das Gate ist jetzt datengetrieben (`check-doc-inventories.py`) und trägt beide, plus einen Selbsttest mit 20 Fällen als eigenen CI-Schritt. Beim Verallgemeinern fiel auf, dass der Fence-Parser `~~~` und ``` gegeneinander toggeln ließ: er merkt sich jetzt Zeichen und Länge des öffnenden Markers.

**Eine dritte Inventarliste stand daneben und war ungegated.** Der Verzeichnisbaum in `scripts/README.md` listet dieselben Skripte ein weiteres Mal, und ausgerechnet im PR gegen Inventar-Drift fehlte dort das neue Gate-Skript. Gefunden hat das die Zweitmeinung, nicht das Gate.

**cp1252 ist nicht ASCII.** Acht Audit-Skripte starben unter Windows an ihrer eigenen Erfolgsmeldung, weil das Häkchen U+2705 ist. Beim Messen, welche Skripte betroffen sind, war meine erste Messvorschrift (`ord(c) > 255`) selbst falsch: cp1252 ist Latin-1 plus 0x80 bis 0x9F und enthält damit Umlaute, Gedankenstriche und Anführungszeichen. Die MHG-Breven `ŏ` und `ŭ` liegen dagegen außerhalb, und Audit-Skripte drucken Korpusformen.

**Der Reader zeigt seit #250 Header-Prosa, und die trug ASCII-Substitute.** Acht Dateien, darunter zwei verschluckte Silben in OVW („Streuberlieferung" statt „Streuüberlieferung"). Der erste Scan war auf die im Issue genannten Wörter gekeyt und hat deshalb nicht geprüft, was er zu prüfen behauptete; der zweite zählt alle 70 Wörter mit `ss`, `ae`, `oe` oder `ue` in der Prosa aller `editorialDecl`-Blöcke und legt die Liste offen. Zwei weitere Dateien kamen so dazu.

### Was offen bleibt

- **#315 Punkt 2:** im Korpus tragen sechs Dateien `role="lead-editor"` (JT, PUC, TKA, TKR, VTC, WZB), die Doku nennt an drei Stellen vier, fünf und sechs. Ob WZB dazugehört, ist eine fachliche Frage an KZW und Julia.
- **#316:** die Sprachmischung in den Docs und der Feature-Katalog in INDEX.md, der FEATURES.md nacherzählt. Dazu neu: das Umleitungsziel ROADMAP → Recently Completed ist selbst nicht frisch (jüngster Eintrag 08.07.). Das Freshness-Problem ist verschoben, nicht gelöst. *(Nachtrag vom Health-Check am 02.09.: die Tabelle „Recently Completed" ist noch am selben Tag ganz entfernt worden, `ce55dde0a`.)*

**Phase:** Betrieb. PRs #330, #332, #333, #334, #335, #336.

---

## 2026-08-02 (Abend) – Reviewer und Berater sind zwei Rollen, und der Fehler saß in den Behauptungen

**Summary:** Der `fable-advisor` lief seit dem 28.07. als PR-Reviewer. Das war eine Rollenverwechslung mit messbaren Kosten, und sie ist jetzt aufgelöst: ein eigener `fable-reviewer` (Fable 5, mit Bash) prüft fertige Diffs vor dem ersten Push, der Berater bleibt für Entwurfsfragen. Dazu bekam der CI-Bot per `--append-system-prompt` ein Gedächtnis für seine Vorrunden, und `scripts/audit/review-rounds.py` macht die Wirkung messbar. Erster PR danach: #339 mit zwei Läufen.

**Die Unterscheidung, um die es geht.** Der Berater beantwortet „sollen wir X so lösen?", der Reviewer „ist dieses X korrekt?". Daraus folgen gegenteilige Pflichten. Beim Berater ist Spekulation erlaubt und nötig, weil bei einer offenen Entscheidung noch nichts zu messen ist, und Alternativen zu suchen ist sein Auftrag: sein Prompt sagt wörtlich „Suche aktiv nach dem stärksten Einwand" und „Prüfe die Alternative mit". Auf einen fertigen Diff angesetzt produziert genau diese Kalibrierung Runden ohne Verhaltensänderung. Der neue Reviewer verlangt für jeden Befund einen Anker in Datei und Zeile, trennt Verhalten (blockiert) von falscher Behauptung (nur gemessen) und Kosmetik (entfällt ab Runde 2), und hat als einziger von beiden ein Abbruchkriterium: Runde 2 nur Vorrunden-Befunde plus seither geänderte Zeilen, Runde 3 nur noch Verhalten, ab Runde 4 Schluss. Dazu der Satz, der am meisten spart: eine leere Befundliste ist ein gültiges und erwünschtes Ergebnis.

**Zwei Modelle, nicht drei.** Der ursprüngliche Vorschlag war je ein Reviewer auf Opus und auf Fable. Dagegen sprach die Bestandsaufnahme: der CI-Bot ist bereits Opus (`claude-code-review.yml`, `--model opus`), und die Hauptsession ebenfalls. Ein lokaler Opus-Reviewer wäre der dritte Kanal desselben Modells auf denselben Diff gewesen. Gebaut wurde deshalb genau einer, auf Fable.

**Der Zeitpunkt ist wichtiger als die Gründlichkeit.** Ohne `use_sticky_comment` löst jeder Push einen Review-Lauf aus, die Rundenzahl ist also die Push-Zahl plus eins. Was der lokale Reviewer findet, kostet null Runden; was der Bot findet, kostet per Konstruktion eine und schafft eine neue Gelegenheit für den nächsten Befund. Deshalb läuft der Reviewer vor dem ersten Push, nicht vor dem Merge. Playbook-Regel 6 und Kickoff-Punkt 4 sind entsprechend umgeschrieben.

**Zwei eigene Zahlen waren falsch, und beide standen in Absätzen über falsche Zahlen.** „11 Review-Runden" über #330/#332/#333 in CLAUDE.md und JOURNAL: gemessen sind es 18 Läufe (5 + 7 + 6, alle mit Ergebnis). Und in der ROADMAP stand, der 45%-passRate-Floor aus #172 habe in `testing/test.html` gelebt; die Assertion stand in `testing/tests/playground.spec.js:47`. Beide Male war der Fundort behauptet statt gemessen, das zweite Mal wenige Stunden nach dem Commit, der genau diese Regel in CLAUDE.md aufgenommen hat. Daraus die vierte Regel dort: ein Befund ist selbst eine Behauptung, und die Nachmess-Pflicht galt bis dahin nur auf der Schreibseite. Sie steht jetzt auch in Merge-Gate G2, also dort, wo ein Befund tatsächlich in Code übersetzt wird.

**Was der erste Einsatz gebracht hat.** Der Reviewer fand in `review-rounds.py` einen Klasse-A-Defekt, den ich nicht gesehen hätte, weil ich die Ausgabe geprüft hatte und nicht die Auswahl: `gh pr list --limit N` sortiert nach Erstellungsdatum, nicht nach Merge-Datum (#338 steht dort vor #337, obwohl #337 zwei Stunden später gemergt wurde). Das Skript sortierte nur die Anzeige um. Jetzt wird ein Fenster geholt, nach `mergedAt` sortiert und dann zugeschnitten; ein Hinweis nennt, wie viele PRs die naive Sortierung verfehlt hätte, und feuert bei `--limit 1` nachweislich.

**Und was er nicht gebracht hat.** Bei #339 hat er die falsche Ortsangabe zum 45%-Floor mitgetragen statt geprüft, und seine Zahl der gepurgten Tailwind-Selektoren war zu niedrig (16 statt gemessen 22, die `hover\:`-Varianten fehlten). Der CI-Bot fand beides. Ein zweiter Reviewer ersetzt das Nachmessen nicht, er verschiebt nur, wer die ungeprüfte Zahl weiterreicht.

**Erste Messung nach der Umstellung, mit Vorbehalt.** #339 brauchte zwei Läufe, beide mit Ergebnis, vier Befunde insgesamt, davon null zum Verhalten. Der Baseline-Median liegt bei 5,5 Läufen, das Baseline-Minimum aber ebenfalls bei 2 (#334). Ein kleiner PR mit zwei Runden ist also nichts, was es vorher nicht gab; Größe und Rundenzahl hängen zusammen, und ein Datenpunkt trennt die beiden Effekte nicht. `review-rounds.py --baseline` sagt das von selbst, solange Baseline-PRs in der Auswahl stehen. Belastbar ist stattdessen das beobachtete Verhalten: Runde 2 hat keinen der drei Befunde aus Runde 1 wiederholt, hat einen Randpunkt ausdrücklich als „ohne Messung, deshalb kein Befund" liegen gelassen und führt einen eigenen Abschnitt darüber, was in der CI-Umgebung nicht messbar war.

**Die Lehre des Tages.** Alle vier Befunde an #339 waren falsche Behauptungen, keine kaputte Logik. Zusammen mit der Messung vom Vormittag (13 von 27 Befunden derselben Klasse) heißt das: die teure Fehlerklasse ist nicht der Code, sondern was daneben über ihn geschrieben steht. Ein Skript fängt sie nicht, weil die Aussagen Prosa sind („in allen Skripten", „der einzige Konsument"). Deshalb hat der Reviewer Bash: Nachmessen ist die Fähigkeit, die ihn vom CI-Bot unterscheidet.

### Was offen bleibt

- **Der Reviewer ist nie gegen einen eingebauten Fehler getestet.** Nach der eigenen Regel 1 („ein grünes Gate ist kein wirksames Gate, Mutation ist der Beweis") fehlt der Nachweis, dass er einen echten Verhaltensdefekt findet. Bisher hat er nur an defektfreien Diffs gearbeitet.
- **Die Wirkung auf die Rundenzahl ist unbelegt.** Sie trägt erst, wenn kein Baseline-PR mehr in `review-rounds.py --baseline` steht, also nach vier weiteren PRs.

**Phase:** Betrieb. PR #339, Issue #326 geschlossen; drei Direkt-Commits auf main (`6a8d4caba`, `e5bd0adc9`, `fd6564bb4`) plus Merge `0d769c8e4`.

---

## 2026-08-03 – #316 abgeschlossen: die Doku ist englisch, und die Sprachregel steht jetzt im Repo

**Summary:** Die letzte Etappe von #316 ist gemergt (PR #347, `b261069cf`): `ROADMAP.md`, `POS-TAGSET.md`, `TEI-MODEL-AUTH-FILES.md` und `TEI-MODEL.md` vollständig englisch, dazu zwei deutsche Restzeilen in `LINECODE.md`. Damit sind die 13 stabilen Promptotyping-Dokumente plus ROADMAP englisch. Deutsch steht nur noch, wo es Dateninhalt ist: der eingefrorene Header-Wortlaut der 667 Korpusdateien, mittelhochdeutsche Belege in der POS-Tabelle, Werktitel, Namen und Notizen aus `contributors.xml`.

**Der teuerste Fund des ganzen Tickets: elf stille Kopplungen zwischen Doku-Prosa und Audit-Skripten.** `doc-count-audit.py` bindet jede Zahl an das Wort direkt dahinter („256.760 Formen"). Übersetzt man dieses Wort, meldet das Audit keinen Fehler, es hört stumm auf, die Stelle zu prüfen. Der Bruch ist damit unsichtbar und sieht wie Erfolg aus. Über die vier Etappen waren es elf solche Stellen; die Anker für `variants_entries`, `variants_forms`, `persons`, `concepts`, `genres`, `names` und `contributors_persons` sind jetzt zweisprachig, ebenso der Historien-Skip in `find_stale_numbers`. Alle dreizehn Zahlbindungen der beiden TEI-MODEL-Dateien sind per Mutation belegt, der Historien-Skip zusätzlich negativ: ohne den Marker im Satz fällt die 666 des #32-Audits sofort als Drift gegen 667 auf.

Eine Anker-Formulierung ist bewusst zusammengesetzt: `variant entries` statt eines blanken `entries`. Ein blankes `entries` hätte in `DATA-MODEL.md` die Lexikonzahl getroffen (43.879 statt 42.627). Das Drift-Fenster verwirft die zwar, die Anker-Abdeckungsprüfung kennt es aber nicht und meldete daraufhin einen richtigen `INTENTIONALLY_SILENT`-Eintrag als veraltet. Zwei Prüfungen desselben Skripts, verschiedene Toleranzen.

**Drei kaputte Anker-Verweise, zwei davon älter als dieses Ticket.** Beim Umbenennen von Überschriften (Paragraph 11 „Versionierung" → „Versioning", 8.1, „Provenienz und Aktualität" → „Provenance and currency") habe ich eine Prüfung über alle `docs/*.md` geschrieben. Sie fand neben den eigenen Umbenennungen zwei Verweise, die schon vorher ins Leere zeigten (POS-TAGSET Paragraph 3 aus TEI-MODEL, der ROADMAP-Abschnitt aus RESEARCH). Die CI hat keinen Link-Checker; ohne die Prüfung wäre nichts davon aufgefallen.

**Der Review-Bot kam am Diff nicht vorbei.** `claude-review` scheiterte auf PR #347 zweimal mit `error_max_turns` nach 8 und 11 Minuten, beide Male mitten in der Checkliste. Der Diff umfasst 11 Dateien und 869 zu 849 Zeilen. Bei #344 mit fünf Dateien lief er noch durch. Die inhaltliche Prüfung lieferte stattdessen der `fable-reviewer` vor dem Push: 28 Mutations-Szenarien über die Zahlbindungen, alle elf dateiübergreifenden Anker aufgelöst, Vollinventar alt gegen neu über Zahlen, Attribute, Dateinamen, XML-Elemente und IDs. **Lehre: die PR-Größe ist eine Eigenschaft, die man einplanen muss, nicht nur eine Folge.** Eine Datei pro PR hätte den Bot arbeiten lassen. *(Vorwärtsverweis, nachgetragen vom Health-Check am 02.09.: diese Lehre ist inzwischen widerlegt, siehe die Einträge vom 31.08. („Der berechnete Diff ist notwendig, nicht hinreichend") und vom 02.09. („46 Turns hier gegen 56 bei #382 mit 13 Dateien"). Der Satz oben bleibt als Protokollstand stehen.)*

**Die Sprachregel hat sich an einem Tag dreimal geschärft**, und die Endfassung ist die einfachste. Zuerst als „user-facing deutsch, Entwickler-Doku englisch, JOURNAL bleibt deutsch" in CLAUDE.md geschrieben (PR #348, `90cc3e49a`, schließt #316). Dann die Korrektur von chsteiner, dass rein für LLMs geschriebene Dateien englisch sein sollen und keine weiteren Auflagen tragen. Und schließlich: **für LLM-Dateien gibt es gar keine Auflagen, die Sprachwahl eingeschlossen** („es geht nur um qualität nicht um das wie es dort steht"). Damit entfällt auch die eben noch geplante Übersetzung von `JOURNAL.md` und `journal-archive.md`, rund 2.800 Zeilen. Dass `docs/` englisch ist und dieses Journal deutsch, ist ab jetzt Zufall der Entstehung und keine Regel.

**Zwei Regeln, die aus dem Tag selbst kommen:**

1. **Kleine Doku-Änderungen gehen direkt auf `main`**, ohne Zweig, PR und CI-Runde. Ich hatte für zwei Absätze in CLAUDE.md einen PR aufgemacht; das ist derselbe hausgemachte Overhead, den CLAUDE.md eine Ebene tiefer schon beschreibt. Zweig plus Review bleibt für Code, Daten, Build-Skripte und alles, was ein Gate oder ein Test fangen kann.
2. **Die Em-Dash-Regel gilt nur für user-sichtbaren Text.** Das Gate prüft weiterhin jede neu hinzugefügte Markdown-Zeile und ist damit weiter gefasst als die Regel, die es durchsetzen soll: ein Treffer in `docs/` ist Rauschen und kostet keine Review-Runde. Steht gleichlautend in Playbook-Regel 32, in der Audit-Tabelle von DEVELOPMENT.md und im Docstring des Gates. Ob der Markdown-Zweig auf user-sichtbare Dateien eingeschränkt gehört, ist offen und als Entscheidung markiert. **Diese Regel hat nur vier Stunden gehalten, siehe den Nachtrag unten.**

**Nachtrag am selben Abend: die Verengung gebaut, gemessen und verworfen.** Punkt 2 oben war der Stand am Nachmittag. PR #349 hat die Einschränkung dann tatsächlich umgesetzt (weiße Liste `publications/` plus `README.md`, später um die zwei aus den Hilfeseiten verlinkten READMEs erweitert) und ist ungemergt geschlossen worden, nachdem die Kosten beider Varianten nebeneinander lagen.

**Die Verengung erzeugte zwei eigene Fail-opens, beide vom `fable-reviewer` gefunden und vor der Übernahme im Wegwerf-Repo nachgestellt.** Eine erkannte Umbenennung hat keine hinzugefügten Zeilen, also trug `git mv docs/entwurf.md publications/entwurf.md` den gesamten Em-Dash-Bestand von `docs/` stumm in den Veröffentlichungspfad: `scanne_diff` lieferte `[]`. Derselbe Fehler ein zweites Mal für `publications/_archived/alt.md` → `publications/alt.md`, wo der alte Pfad zwar im Umfang liegt, aber als Archivcode übersprungen wird. **Beide Löcher gibt es nur, weil es eine weiße Liste gibt.** Eine Regel, die nach Ort unterscheidet, muss auch den Ortswechsel behandeln, und daran denkt niemand beim Schreiben der Liste.

**Die Zahlen, die entschieden haben.** Kosten der stumpfen Regel („keine Em-Dashes in jeder `.md`", weiterhin nur in hinzugefügten Zeilen): 159 von 481 Commits in 90 Tagen, 40 von 182 in 30 Tagen, **5 von 100 in den letzten 14 Tagen mit zusammen 6 Zeilen**. Der große Posten war das JOURNAL (90 Tage: 814 Zeilen) und ist praktisch verschwunden. Der 14-Tage-Wert misst dabei teilweise schon die Regel selbst, weil das Gate seit dem 02.08. so läuft. Kosten der Ausnahme dagegen: 267 Zeilen Umfangs-Maschinerie, zwei Klasse-A-Befunde in zwei Review-Runden und die Frage „ist diese Datei user-sichtbar?", die pro neuer Datei wiederkommt. Sie kam auch prompt: die ausgelieferten Hilfeseiten verlinken zehn `.md`-Dateien, sieben davon unter `docs/`, dazu `schema/README.md`, `ingest/ari/README.md` und eine Agent-Skill-Datei unter `.gemini/`. Über die letzte musste einzeln entschieden werden (draußen: für den Agenten geschrieben, auch wenn eine Hilfeseite sie als Beispiel verlinkt).

**Die Sprachregel ist dabei mitentwirrt worden**, weil „keine Auflagen für LLM-Dateien" und „`docs/` muss einheitlich englisch sein" sich widersprachen. Auflösung in drei Körben statt zwei: user-sichtbare Seiten deutsch; der `docs/`-Satz einheitlich englisch, **nicht** weil er user-sichtbar wäre, sondern weil seine 15 Dateien einander zitieren und zusammen gelesen werden (und weil #316 vier Etappen dafür bezahlt hat); Arbeitsnotizen (CLAUDE.md, JOURNAL, Archiv) ohne jede Auflage. Darüber genau eine mechanische Regel, die überall gilt und maschinenprüfbar ist: keine Em-Dashes in `.md` und user-sichtbarem HTML. Der wiederkehrende Fehler des Tages war, Sprache und Typografie in dieselbe Regel zu packen; die eine ist eine Eigenschaft des Dokumentensatzes, die andere eine Zeichenregel.

**Was davon bleibt:** eine Ausnahme, die pro Fall entschieden werden muss, ist teurer als die Regel, die sie sparen soll. Und: der Aufwand, eine Verengung zu bauen, ist kein Argument, sie zu behalten. Der PR war fertig, zweimal reviewt und grün, als die Messung ihn erledigt hat.

**CLAUDE.md überarbeitet** (`dad844b2a`, `640020235`): ganz englisch, 153 auf 135 Zeilen. Die Doku-Tabelle ist raus, weil `docs/INDEX.md` per `@`-Import ohnehin im Kontext liegt und denselben Katalog vollständig führt; die Kopie war auf 10 von 15 Dokumenten gedriftet. Der Zweig-Abschnitt nannte `feature/*` als Konvention, gemessen sind es bei den letzten 20 gemergten PRs 9 `claude/`, 3 `docs/`, je 2 `fix/` und `feature/`. Eine unbelegte Zahl entfernt („rund 470 Zeilen mit Em-Dash").

**Aufgeräumt:** vier leere Worktree-Hüllen (`mhdbdb-wt-314`, `-323`, `-327`, `-331`, je ein leeres `node_modules`, zusammen 56 KB), während `git worktree list` nur den Hauptbaum zeigte und `.git/worktrees` gar nicht existierte. Git räumt weg, was Git kennt; ungetrackte Verzeichnisse bleiben liegen. Als Punkt 5 in Playbook-Regel 30 (`011f74f9d`).

**Phase:** Betrieb, reine Doku. Kein Index- und kein API-Rebuild, keine Daten berührt.

## 2026-08-05 – Label-Neuordnung: 28 auf 16, und der Backlog hat einen einzigen vollautonomen Eintrag

**Summary:** Alle 53 offenen Issues wurden vollständig gelesen, Body und jeder Kommentar, und gegen ein neues Label-Schema triagiert. Sechs parallele Agenten mit je acht bis neun Tickets, danach zentral angewandt. Das Schema ist ausdrücklich **für Agenten** gebaut, nicht fürs Team: Chris' Vorgabe war „wir menschen nutzen die labels kaum, bitte optimiere für dich selbst". Drei orthogonale Achsen mit genau einem Label je Achse, dazu zwei Flags. `auto:*` (full, brief, checkin, pair, blocked) steuert, wie selbständig eine Session ein Ticket anfassen darf; `area:*` sagt, wo die Arbeit anfällt; `effort:*` blieb unverändert. Gelöscht wurden 23 Altlabels, angelegt 12. Legende und Ping-Liste stehen im Body von #44, die Kurzfassung seit `5e051105d` in CLAUDE.md.

**Der Befund, der die Arbeit gerechtfertigt hat: 30 der 52 offenen Tickets warten auf einen Menschen, nicht auf Arbeit.** 19 davon liegen bei KZW, drei bei Julia, acht bei Externen. Sechs sind sogar gebaut, gemergt und live und warten nur noch auf eine Abnahme (#169, #239, #250, #251, #224, #86). Auf der anderen Seite steht **ein einziges** `auto:full`-Ticket, und das sperrt sich im eigenen Text auf ein anderes (#194 auf #193). Der autonome Vorrat besteht faktisch aus den acht `auto:brief`-Tickets, also aus Arbeit, die eine Klärungsrunde vorweg braucht. Wer eine autonome Session starten will, hat derzeit nichts zu greifen, ohne vorher zu fragen.

**Warum die alten Labels so falsch waren, ist strukturell und nicht Nachlässigkeit.** `needs-clarification` klebte an Tickets, deren Klärung längst da war (#28: KZW hat am 29.07. entschieden; #27: alle Punkte seit dem 10.07.). `depends-on-human`, `external-research` und `needs-clarification` beschrieben dieselbe Sache aus drei Blickwinkeln und wurden entsprechend beliebig gesetzt. `claude-ready` war an keinem Ticket mehr korrekt. Der Grund ist immer derselbe: ein Label wird beim Anlegen vergeben und beim Fortschritt nicht nachgezogen, weil der Fortschritt im Kommentar steht und nicht im Label. Genau darum ist die einzige neue Regel, die etwas kostet, „Labels in derselben Session nachziehen, in der man das Ticket anfasst".

**Der teuerste Fund des Tages ist ein Befund über Befunde.** Der alte #44-Body führte drei tote Codepfade im Playground als Aufräum-Kandidaten: `findProximityMatchesInIndex`, `searchProximityUsingIndex` und `executeProximitySearch` mit blockierendem `prompt()`, dazu eine fehlende Deduplizierung in `resolveLemmaIds`. Chris' Reaktion darauf war „es gibt tote pfade? ja dann unbedingt ein issue draus machen". Nachgemessen: **alle drei Funktionen existieren im gesamten `.js`-Bestand nicht mehr**, das einzige verbliebene `prompt(` ist ein Kommentar in `lemma-explorer.js:832`, der die Entfernung dokumentiert, und `resolveLemmaIds` endet in `tei-ui.js` auf `return [...new Set(lemmaIds)]` mit eigenem Regressionstest. Ein Ticket darauf wäre reine Selbstbeschäftigung gewesen, gebaut auf eine Behauptung aus einer Datei, die dieses Projekt selbst geschrieben hat. Das ist derselbe Mechanismus, den CLAUDE.md unter „Self-Inflicted Overhead" für Review-Kommentare beschreibt, hier nur eine Ebene höher: **#44 ist selbst eine Quelle unbelegter Behauptungen, und zwar die zentralste, die es im Projekt gibt.** Der Body trägt seit heute eine Warnung genau dieses Inhalts an der Stelle, an der die Befunde stehen.

**Der zweite Fund derselben Sorte, mit umgekehrtem Vorzeichen.** Ein Triage-Agent meldete, die Zahl im Titel von #252 („971 Stellen in 21 Texten") sei falsch, gemessen seien es 122 in 9. Vor der Korrektur selbst nachgemessen, und die Rechnung fällt anders aus: es gibt **zwei** Zählweisen, die einander kaum überschneiden. Ein `<l>` mit `<caesura/>` und ohne jeden sichtbaren Text kommt **974-mal in 96 Texten** vor, ein `<l>`, dessen sichtbarer Text nur aus Klammern besteht, **136-mal in 14 Texten**. Die 971 im Titel ist also im Kern richtig, falsch ist die Textzahl daneben, und der Agent hatte schlicht die andere Menge gemessen. Wäre der Befund übernommen worden, hätte eine richtige Zahl eine falsche ersetzt, mit Messung als Beleg. Die Einzelaufschlüsselung im Body ist tatsächlich überholt (FR1 steht dort mit 543, gemessen sind es 1 beziehungsweise 23), was am Frauenlob-Umbau aus #236 liegt. Beide Zählweisen samt Skript stehen jetzt als Kommentar in #252, mit der Vorbedingung, dass vor der Migration zu entscheiden ist, welche der beiden gemeint ist: es geht um 838 Stellen Unterschied. Nebenbei ist auch die Schema-Annahme im Ticket überholt, `gap` steht seit `b59350bb5` in `mhdbdb.rnc` und kommt im Korpus 0-mal vor.

**#114 geschlossen**, das einzige Ticket ohne verbleibenden Adressaten: die Tabellenansicht ist seit PR #157 live und Linda hat am 13.07. abgenommen. Die anderen fünf fertigen Tickets bleiben bewusst offen, weil die Abnahme bei KZW, Julia und Alan liegt und ein Merge keine Abnahme ist.

**ROADMAP.md an drei Stellen richtiggestellt** (`aff7fe2af`), jede Zeile vorher gegen `git log` und die Issue-Kommentare geprüft: die DIG-Renderfrage in #138 hat KZW am 28.07. beantwortet und HUG ist mit PR #243 erledigt (814 Ziffern raus, HUG steht bei 0), offen ist nur der korpusweite Lauf, und der muss über den xml:id-Block gehen statt über `@pos`, weil 108 der 814 HUG-Ziffern gar kein `@pos` trugen. #250 stand als „Implementation open", liegt aber vollständig auf `main`. #114 ist aus der Linda-Zeile verschwunden.

**Was offen bleibt und keine Arbeit ist:** die Ping-Liste. Sie wäre der ertragreichste Handgriff des Tages gewesen, ist aber nicht abgesetzt worden, weil KZW und Julia gerade auf Urlaub sind. Damit bleibt der größte Posten der Matrix bis auf Weiteres genau da stehen, wo er steht.

**Die Lehre, die Chris selbst mitten in der Session formuliert hat** („#44 wird unglaublich schnell stale"): der Body macht Aussagen über 52 Tickets gleichzeitig und veraltet deshalb schneller als jede andere Datei im Projekt. Innerhalb dieser einen Session ist er zweimal falsch geworden, einmal durch das Schließen von #114 und einmal durch die eigene Dead-Code-Passage. Der belastbare Teil ist nicht die Prosa, sondern die Labels: sie hängen am Ticket und nicht an einem Absatz, und ein `gh issue list --label "auto:brief"` ist immer aktuell. Der nächste Schritt wäre folgerichtig, die abzählbaren Teile des Bodys (Quick Stats und die Tabellen je Autonomiestufe) aus den Labels zu generieren und nur die Begründungen von Hand zu pflegen, nach demselben Marker-Muster, mit dem `build-pages.py` Nav und Footer injiziert.

---

## 2026-08-05 (Nachmittag) – Loop Engineering: vier Merkregeln werden ein Skript, drei Verträge werden einer

**Summary:** Die drei Session-Playbooks wurden gegen Anthropics Loop-Engineering-Raster geprüft und daraufhin umgebaut. Ergebnis in zwei Teilen: ein Wrapper `scripts/run-tests.js` (331 Zeilen, PR #353), der `npm test` sein Ergebnis selbst verkünden lässt, und eine Aufteilung der Playbooks in einen gemeinsamen `BETRIEBSVERTRAG.md` (17 Regeln), eine `KICKOFF-VORLAGE.md` (8 Bausteine) und drei Playbooks, die nur noch ihre eigenen Abweichungen führen. §2.1 des Issue-Playbooks ist dabei erstmals geschrumpft, von 32 auf 26 Regeln.

**Der Anlass war ein Widerspruch zwischen zwei Playbooks, die einander zitieren.** Das Merge-Playbook wies in Zeile 61 die Task-Ausgabe eines Testlaufs als Ergebnisquelle aus. Die Issue-Regeln 26 und 27 belegten dieselbe Quelle als falsch-grün, mit Datum und Vorfall. Beide Sätze standen seit Wochen nebeneinander, und keine der beiden Sessions, die dazwischen liefen, ist über den Widerspruch gestolpert, weil jede nur ihr eigenes Playbook liest. Kopien driften, und zwar nicht durch Nachlässigkeit, sondern weil eine Kopie keinen Grund hat, von der Korrektur der anderen zu erfahren.

**Der Wrapper beantwortet die Frage einmal, statt sie vier Merkregeln zu überlassen.** Er löscht den alten Report, setzt `PW_TEST_HTML_REPORT_OPEN=never`, vergleicht bei filterlosem Lauf die Spec-Dateien auf der Platte gegen die im Report und bildet den Exit-Code aus `report.json`: 0 grün, 1 rot, 2 der Lauf ist gar nicht zustande gekommen. Die VERDICT-Zeile nennt Testzahl, Dateizahl und den geprüften Pfad. Damit fällt die Unterscheidung, an der die alten Regeln hingen, in den Aufruf: ein gefilterter Lauf sagt TEILLAUF und belegt keine Vollständigkeit mehr, auch wenn ihn jemand als Beleg in einen PR schreibt.

**Der teuerste Teil war die Prüfung des Wrappers, nicht sein Bau.** Runde 1 des `fable-reviewer` fand, dass die Server-Prüfung im eigenen Zielfall versagt: sie wertete jeden Fetch-Fehler als „kein Server da" und übersprang danach genau die Sentinel-Prüfung, die einen fremden Dev-Server auf Port 8080 fangen sollte. Gemessen: ein geschlossener Port liefert `ECONNREFUSED`, ein sättigender Server einen `AbortError` ohne Code. Seither gilt nur `ECONNREFUSED` als „niemand da", und die Frist steht bei zehn Sekunden. Runde 3 des Bots fand, dass die VERDICT-Zeile im Abbruchfall auf stderr ging, live bestätigt mit getrennter Umleitung, und dass Playwrights eigener Exit-Code im Report-Pfad verworfen wurde. Beides behoben. Der dritte Bot-Befund war als Befund widerlegt, führte aber zur besten Ausgabeform des Tages: `NICHTS GELAUFEN (0 Tests). Das belegt nichts.`

**Ein Zitat eines beratenden Agenten hat der Messung nicht standgehalten, und das ist der Grund, warum eine Regel unverändert blieb.** Ein Opus-Berater begründete eine vorgeschlagene Umschreibung von Regel 26 mit einem wörtlichen Zitat aus `journal-archive.md:2383`. Der Satz existiert dort nicht, und keiner der drei „Exit 0"-Treffer im Archiv ist der behauptete Vorfall. Die Regel wurde deshalb nicht auf seine Diagnose umgeschrieben. Derselbe Mechanismus wie bei #44 heute früh, nur eine Rolle weiter: **ein Berater, der eine Fundstelle nennt, macht damit eine Behauptung und keine Messung.** In dieselbe Richtung ging ein eigener Fehler in die Gegenrichtung: eine Korrektur am Vorschlag des Fable-Advisors zu `skipped > 0` war falsch, sein Vorschlag hätte funktioniert.

**Die Regelliste schrumpft auf zwei Wegen, und beide sind jetzt im Kopf von §2.1 benannt.** Der erste ist Ausführbarkeit: was ein Skript deterministisch prüfen kann, gehört nicht in eine Merkregel (die Regeln 6, 16, 26, 27 sind eine geworden). Der zweite ist Geltungsbereich: drei Regeln waren keine Projekterfahrung, sondern Fallen von Git und der Windows-Shell, die in jedem Repo gelten, und stehen seit heute in der persistenten Memory statt in einer Datei, die nur nach einem Kickoff gelesen wird (8, 9, 31). Die Nummern bleiben als Anker stehen, mit sechs Lücken, weil Wellenplan, Merge-Playbook und ROADMAP sie zitieren und die datierten Wachstumsangaben sonst auf andere Regeln zeigen würden.

**Neu im Merge-Playbook: die Pilot-PR-Regel.** Ein PR durchläuft die Schleife vollständig, bevor der zweite anfängt. Der Grund ist nicht Vorsicht vor dem einzelnen PR, sondern vor dem Verfahren: die erste Merge-Session hat 13 PRs am Stück abgearbeitet, und der Retarget-Fehler, der dabei #177 geschlossen hat, hätte jeden weiteren Stack genauso getroffen.

**Verifikation:** Volllauf nach dem Ende der parallelen Session 271 expected, 0 unexpected, 0 flaky, Exit 0. In zwei von drei vorherigen Volläufen war `playground-authority-index.spec.js` mit der 10-Sekunden-Schwelle für den Authority-Index flaky, isoliert dagegen 7 von 7 grün in 46 Sekunden. Der Test misst damit unter Last die Maschine und nicht den Code.

**Nachtrag am selben Tag, die Schwelle steigt.** Chris hat entschieden, den Test zu behalten und die Grenze anzuheben. Isoliert nachgemessen, drei Läufe: 5,5 / 5,9 / 5,9 Sekunden. Die alte Schwelle von 10 Sekunden lag damit nur um den Faktor 1,7 über dem Normalfall, was unter parallelen Workern nicht reicht. Neu sind 20 Sekunden, und der `waitForSelector` steigt von 15 auf 30 Sekunden mit, weil die Zusicherung sonst gar nicht zum Zug käme: der Wait wäre vorher gescheitert, und die wirksame Grenze wäre still eine andere gewesen als die im Testnamen. **Die Obergrenze kommt nicht aus dem Bauch, sondern aus der Regression, gegen die der Test steht:** Laufzeit-XML-Parsing hat vor den vorgebauten Indexen laut `ARCHITECTURE.md:481` rund 30 Sekunden gekostet, und genau das muss die Schwelle noch fangen. Die Zahl ist eine Doku-Angabe und keine eigene Messung, weil es diesen Codepfad nicht mehr gibt; sie steht deshalb mit Fundstelle da, im Test wie hier. Sie liegt jetzt zwischen beiden Werten statt dicht am Normalfall.

---

## 2026-08-06 – ADR-017 und ein Lifecycle, der nichts zu tun fand

**Summary:** Die editorische Frage, die ADR-016 offen an KZW abgegeben hatte, ist entschieden: das Breve über `w` und `n` ist in der Wenzelsbibel keine Umlautmarkierung, sondern böhmische Schreibkonvention, und wird deshalb getilgt statt zu einem Digraphen aufgelöst. Julia hat das als WZB-Editorin festgelegt, die beiden Regeln stehen in beiden Normalizern (`f3dcf2a8`), ADR-017 schreibt die Entscheidung samt Messung fest. Der anschließende Data-Change-Lifecycle für die 17 WZB-Tokens, die statt eines Leerzeichens die Zeichenfolge `\u0020` trugen und jetzt zwei `<w>` sind (#235 Punkt 1), endete ohne einen einzigen geänderten Byte in der abgeleiteten Schicht.

**Der Lifecycle war kein Leerlauf, sondern eine Messung.** Korpus-Index, Authority-Index und die 2.742 API-Dateien wurden vollständig neu gebaut und sind byte-identisch zum Bestand; `extract-variants.py` meldet alle vier semantischen Zähler auf 0. Damit ist belegt statt vermutet, dass beide Änderungen indexneutral sind, und der Versions-Bump entfällt zu Recht (die Regel „kein Bump ohne Inhaltsänderung" schneidet in beide Richtungen). Möglich ist diese Auskunft nur wegen der deterministischen Builds aus #125: vor ihnen hätte derselbe Rebuild einen Diff aus Zeitstempeln erzeugt und die Frage gar nicht beantworten können.

**Warum die Normalizer-Regel den Index nicht anfasst, ist der interessantere Teil.** Keines der 113 Breve-Tokens trägt ein `@corresp`, keines ist also je in `variants.xml` gelandet, und die gebaute Variantenkarte enthält null Schlüssel mit einem Breve. Die Regel erzeugt deshalb keinen neuen Treffer, sie lässt die WZB-Schreibung einen erreichen, den es schon gab: `fewer`, `ewer`, `wenn` sind aus anderen Texten als Formen belegt. Auffindbarkeit wächst von 11 auf 100 von 113 Tokens, 93 davon über Stufe 2, und für alle 64 lemmatisierten Tokens ist der erste Treffer genau das Lemma, das das Token selbst trägt.

**Zwei Zahlen in CONTRACTS §A waren falsch, und zwar in dieselbe Richtung.** Dort stand, vor der Regel sei „nicht ein einziges" der 113 Tokens auffindbar gewesen und danach 93. Gemessen waren es vorher 11 (alle über die Stufe-3-Notlösung, keines davon lemmatisiert) und nachher 100. Beide Male war die Zahl zu gefällig für die eigene These. Die Korrektur nennt jetzt die Aufteilung nach Stufen, und ADR-017 nennt die Messvorschrift dazu, weil „113 Tokens" je nach Zählweise auch 40 (distinkte Formen) oder 64 (nur lemmatisierte) heißen kann.

**Offen bleibt die Gegenrichtung, und sie ist der eigentliche Rest von #235.** Wer `fewer` tippt, findet das Lemma und über das Lemma die annotierten Stellen. Die 49 unlemmatisierten Breve-Tokens leuchten in der Leseansicht trotzdem nicht auf, dafür braucht es ein `@lemmaRef`. Zusammen mit den 289 o/u-Breve-Tokens ohne Lemmaverweis und den 8 Makron-Tokens ist das der Matcher-Rerun, den schon ADR-016 als eigene Runde vorgemerkt hat.

**Phase:** Betrieb. #235 Punkt 1 committet (`f3dcf2a8`), Punkt 2 seit 28.07. gemergt, Punkt 3 offen.

## 2026-08-07 – #58: der Weg vom Lemma zum Beleg, und warum er eine ID trägt

**Summary:** Aus dem Lemmata-Explorer führte kein Weg in die Belegsuche; das war der Rest von #58 („Begriff → Lemma → Beleg"). Neu ist ein Knopf pro Treffer und, dahinter, ein neuer Parameter `ids` an der Route `#multi-lemma`, positionsgleich zu `lemmata` gepaart. Dazu geschlossen: #68 (der Beitragsleitfaden war seit dem 29.05. vollständig, nur hatte es niemand nachgeprüft). #194 von `auto:full` auf `auto:checkin` korrigiert, weil sein eigener Body die Umsetzung an #193 bindet und #193 nicht gebaut ist.

**Die Entscheidung, um die es ging, war nicht A gegen B gegen C, sondern Schreibform gegen ID.** Der naheliegende Weg wäre gewesen, die Schreibform an die Multi-Lemma-Suche zu übergeben, so wie es die beiden bestehenden Übergaben tun (Wortbestandteil-Auswahl, Kookkurrenz-Ranking). Die Messung hat das verworfen: 102 Schreibformen im Lexikon tragen mehr als einen Eintrag, nach Normalisierung sind es 477 Formen und 993 der 43.879 Lemmata, darunter `sin`, `wal`, `mal`, `de`. Für die hätte der Knopf still die Belege eines anderen Lemmas gezeigt, und zwar immer die des häufigeren, weil `searchLemmaByOrthography` nach Korpusfrequenz sortiert und die Aufrufer `matches[0]` nehmen. An genau der Stelle hat der Nutzer aber schon entschieden, welches Lemma er meint. Die Schreibform fährt nur noch als Beschriftung mit.

**Der teuerste Fehler des Tages war meiner und wurde von einem Gegenprüfer gefunden.** `executeSearch()` schließt das Modal, bevor es auflöst, und `close()` leert über `reset()` auch die neue Zeiger-Map. Der Zeiger wäre also bei jedem Aufruf leer gewesen: die Übergabe hätte immer auf die Schreibform zurückgefallen, und zwar unbemerkt, weil das Ergebnis für 97,7 Prozent der Lemmata dasselbe ist. Der bestehende Kommentar an `searchTerms` warnt zwei Zeilen darüber genau davor. Die Map wird jetzt wie die Begriffsliste kopiert und als Argument durchgereicht statt aus `this` gelesen.

**Zwei Doku-Stellen waren nicht veraltet, sondern falsch.** `FEATURES.md` führte für den Lemmata-Explorer eine „Action: Search lemma in corpus", die es nie gab; #58 macht die Zeile erstmals wahr. Und `CONTRACTS.md` §C behauptete, die Auflösung laufe „through exactly 3 stages" ohne Ausnahme. Mit dem Zeiger gibt es einen Aufruferpfad, der alle drei überspringt, und der steht jetzt als §C.1.1 dort, samt der Einschränkung, dass zwei weitere Erzeuger derselben Route noch nach Schreibform auflösen.

**Nebenbei zu #225:** Thomas Burch hat die Verlinkung im Wörterbuchnetz umgestellt, auf drei unabhängigen Wegen nachgeprüft (Konfigurationsdatei, konsumierender Code, echte Cross-Reference über die Live-API beider Seiten). Damit ist der Rückweg von Lexer, BMZ und Findebuch auf unsere Lemma-Seiten offen. Was Trier im Gegenzug erbeten hat, ist ein aktualisierter Lemmabestand im alten XML-Format; die Messung dazu steht im Ticket, sie ist ein eigenes Arbeitspaket.

**Phase:** Betrieb. #58 im PR, #68 geschlossen, #225 mit Messung an KZW und Chris zurückgegeben.

---

## 2026-08-07 (Nachmittag) – Drei Tickets, in denen die Entscheidung teurer war als die Umsetzung

**Summary:** #269 (Playbook für die Kuration eines einzelnen Lemmas), #225 (Skript für die Trierer Lemmaliste, Mail raus), #111 (Schwellenmessung) und #270 (als ADR-018 entschieden). Keine Zeile Produktionscode an diesem Nachmittag. Geschlossen wird davon nur #270: #269 wartet auf KZWs Abnahme, #111 ist ein Trigger-Reminder und bleibt einer, #225 hängt an Trier.

**#225: die Sperre im Skript ist die Aussage, nicht ein Detail.** `build-wbnetz-lemma-list.py` weigert sich, innerhalb des Repos zu schreiben, weil Ein- und Ausgabe Copyright Trier sind. Genau diese Sperre beantwortet auch Chris' Frage, ob wir Burch die Datei nicht einfach hosten könnten: können wir nicht ohne sein Einverständnis, und aktuell halten könnten wir ohnehin nur unsere Hälfte, weil das Rückgrat der Datei 86.121 Lexer-Ansetzungen sind. Die Frage steht deshalb als Frage in der Mail, nicht als Ankündigung. Ergebnis des Laufs: 2.487 Verweise ergänzt, 54 umgebogen, 129 gestrichen, 6.657 statt 4.643 erreichbare Lemmata, kein toter Zeiger mehr in der Ausgabe.

**#111 war keine Aufgabe, sondern eine Messung, und die Messung hat vor allem eine Messvorschrift ergeben.** 40,2 MB gz und 160,5 MB roh gegen Schwellen von 50 und 200. Die 42 MB aus dem Mai sind kleiner geworden, und trotzdem steht im Ticket ausdrücklich, dass ich daraus keinen Rückgang lese: für die Mai-Werte ist keine Zählweise dokumentiert, „ca. 165" sagt es selbst, und vier Prozent gegen eine gerundete Zahl sind keine Beobachtung. Der nächste Auslöser ist ohnehin kein Datum, sondern #27, dessen Per-Word-POS mit +3 bis 5 MB allein die Hälfte des Abstands bräuchte.

**#270 hat sich beim Messen selbst widerlegt, und das ist der eigentliche Ertrag.** Das Ticket schlug vor, die Contributor-Map erst mit #28 Phase 3 zu bauen, mit dem impliziten Argument, es sei zu teuer für einen Nutzen an einem einzigen kuratierten Lemma. Gemessen sind es **764 Byte gzip** für alle 54 Einträge, 0,02 Prozent des Authority-Index. Kosten sind also kein Grund und stehen jetzt im ADR, damit niemand sie noch einmal verhandelt. Die echten Gründe sind zwei andere: bei n=1 lässt sich nicht ehrlich entscheiden, wo auf einer Lemma-Seite eine Urheberangabe steht (das ist KZWs Entscheidung über eine sichtbare Seite), und der Phasenplan von #28 liefert für Schicht B „Quellsprache plus Quelle der Zuschreibung (Lexer/MWB/Kluge/LLM)". Diese Quelle ist bibliographisch, keine Person, und `contributors.xml` modelliert weder Wörterbücher noch Pipelines. Wer die Auflösung vorher baut, baut den falschen Mechanismus, und auf tausenden Lemma-Seiten stünde „nach Katharina Zeppezauer-Wachauer", wo „Lexer, akzeptiert durch die Pipeline" die Information wäre.

**Ein Ist-Zustand ohne Auslöser ist ein Versäumnis mit Dokumentation.** Deshalb hat ADR-018 eine Schwelle statt eines Verweises auf „später": ab dem 26. kuratierten Lemma oder mit #28 Schicht B, was zuerst kommt. Die Zählweise steht daneben. Nebenbei fiel dabei eine Ausnahme im `doc-count-audit.py` weg: ADR-018 nennt die Lexikongröße jetzt selbst (1 von 43.879), der Anker greift, und die Selbstprüfung hat den veralteten `INTENTIONALLY_SILENT`-Eintrag im selben Lauf gemeldet. Zu wissen ist dazu: das Skript kennt ein `--check`, das bei Drift ungleich 0 zurückgibt, wird aber in keinem Workflow aufgerufen und ist ohne dieses Flag immer grün. Ein Handlauf also, kein Gate.

**Phase:** Betrieb. #270 geschlossen, #225 auf `auto:blocked` + `wait:extern`, weil Trier antworten muss.

---

## 2026-08-08 – #111: aus dem Reminder wird ein Gate, und die Zahl von gestern war eine Einheit

**Summary:** #111 hat jetzt `scripts/audit/check-index-budget.py` und ADR-019. Kein Splitting, der Korpus-Index steht bei 84 Prozent seines Budgets. Zwei Befunde aus der Messung sind mehr wert als das Gate selbst.

**Der Eintrag von gestern stimmt nicht ganz: „Die 42 MB aus dem Mai sind kleiner geworden" beschreibt keinen Rückgang, sondern einen Einheitenwechsel.** `data/corpus-index.json.gz` ist seit dem 31.07. unverändert (`4195581e3`). Die 42 MB aus dem Mai sind dezimal gerechnet, die 40,2 MB von gestern sind MiB. Die Mai-Datei (`ea7b0a507`) hielt 42.183.990 Bytes, das sind 42,18 dezimale MB und 40,23 MiB; heute sind es 42.165.752 Bytes, und 40,2 ist exakt deren MiB-Wert. Seit der Mai-Messung haben 12 Commits die Datei angefasst, nie mehr als 19 kB auseinander. Einen Commit weiter zurück sieht es anders aus: am 08.05. waren es noch 35,8 MB. Die vorsichtige Formulierung von gestern („daraus lese ich keinen Rückgang") war im Ergebnis richtig, aber aus dem falschen Grund: es lag nicht an einer ungenauen Mai-Zahl, sondern daran, dass zwei verschiedene Einheiten verglichen wurden. Belastbar ist: der Index ist seit Mai **flach**. Und weil die Schwellen 50/200 aus der dezimalen Messung stammen, rechnet das Gate dezimal. `check-file-sizes.py` bleibt bei MiB, weil GitHubs Wand in MiB steht; die beiden liegen bei derselben Datei um 4,9 Prozent auseinander, und das steht in beiden Docstrings.

**Der zweite Befund kippt die im Ticket vorgeschlagene Strategie.** Option A in #111 will `texts[].words` auslagern und rechnet mit einem Kern von 10 bis 15 MB gz. Gemessen komprimieren die Felder völlig unterschiedlich: `words` ist 58 Prozent des Index im Speicher, aber nur 31 Prozent auf der Leitung (7,5 Millionen Tokens aus 42.630 verschiedenen Werten, Faktor 7,5). Die Positionsarrays in `texts[].lemmata` komprimieren nur 2,4-fach und sind damit **51 Prozent des Downloads**. Wer `words` auslagert, hat noch 29 MB gz im Kern, nicht 15.

Daraus folgt die eigentliche Regel in ADR-019: die beiden Schwellen sind nicht zwei Sichten auf ein Problem, sondern zwei Probleme. Die gz-Schwelle betrifft Leitung und Cache, dort muss `lemmata` weichen; die Roh-Schwelle betrifft den Speicher nach `JSON.parse`, dort muss `words` weichen. Welche zuerst reißt, benennt das Feld. Eine Vorabfestlegung hätte für den gz-Fall das falsche gewählt.

**Das Gate warnt und wird nie rot** (Entscheidung Chris, auf Rückfrage). Eine Überschreitung ist kein Fehler des Commits, der sie auslöst: der Index wächst durch legitime Annotationsarbeit, und ein rotes Gate würde den nächsten Backfill blockieren, bis jemand ein Splitting gebaut hat. Rot wird nur die gescheiterte Messung. Weil ein dauerhaft grünes Gate nichts beweist, hängt ein Selbsttest mit 20 Fällen daran, der auch die Rangfolge-Frage festhält: der Authority-Index hat weniger MB Luft als der Korpus-Index (4,7 gegen 7,8) und ist trotzdem der harmlosere Fall (41 gegen 84 Prozent Auslastung). Berichtet wird deshalb Auslastung, nicht Abstand. Die erste Fassung hatte genau das falsch herum.

**Zwei Sachen, die dabei auffielen und nicht hierher gehören.** `maps` ist 14,5 Prozent des Authority-Downloads und wird ausschließlich von `playground-main.js:147-157` gelesen; `korpus.html`, `woerterbuch.html` und jede Lemma-Seite laden und parsen 2,5 MB roh, die sie nie anfassen. Und `playground-main.js:319-324` läuft beim ersten Aufbau über `Object.keys(text.lemmata)` aller 667 Texte, nur um eine Anzeigezahl zu füllen, für die es das ungenutzte Top-Level-Feld `totalLemmata` schon gibt. Beides steht als Konsequenz in ADR-019, beides ist Frontend-Arbeit mit eigenen Tests und nicht Teil dieser Messung.

**Nummer:** #111 verlangt im Body ADR-015. Die ist seit 05/2026 vergeben (Authority-Source-Modell), worauf der Ticket-Kommentar vom 05.08. schon hingewiesen hatte. Es ist ADR-019 geworden.

**Phase:** Betrieb. #111 bleibt offen und bleibt Trigger-Reminder, jetzt aber mit einem Wächter statt mit der Hoffnung, dass jemand nachmisst.

---

## 2026-08-08 (Nachmittag) – #193 Baustein 1: ein Pferd, das als Mann klassifiziert war

**Summary:** `lemma_3036` Ingliart trägt jetzt `concept_14012100` (Haustiere/Namen) und `concept_23221000` (Pferd und Reiten/Namen) statt `concept_21012000` (Männlich/Mann) und `concept_23112500` (Personennamen). Zwei Zeilen in `lexicon.xml`, dazu die abgeleitete Schicht. Stufe 1 nach dem Playbook, in etwa der veranschlagten halben Stunde plus Bauzeit.

**Die Streichung war der heikle Teil, und sie war gedeckt.** Das Playbook sagt: Zeiger setzen ist Stufe 1, Zeiger streichen ist eine Rückfrage. Hier beauftragt #193 die Umklassifizierung wörtlich und nennt die Belege. Nachgeprüft statt geglaubt, und beim ersten Versuch falsch nachgeprüft: Ingliart hat **drei** Tokens im Korpus, nicht zwei. `PZ_38926_4` und `PZ_39814_3` sind exakt Boreks Stellen Pz. 389,26 und 398,14, und dort entscheidet der Kontext die Sache ohne Sekundärliteratur: „mit den kurzen ôren ingliart" beschreibt kein Mannsbild. Eine halbe Umklassifizierung wäre außerdem schlechter als keine gewesen, weil Ingliart dann gleichzeitig Mann und Pferd wäre.

**Der dritte Beleg, und wie ich ihn beinahe unterschlagen hätte.** `REN_242090_0` trägt `ingligar` und steht im Rennewart in einem Namenkatalog nach dem Muster „X von Ort": `wimiligar von kartetstere`, `ingligar von jelezie`, `rufter von themarie`. Die Nachbarn tragen alle eigene Hapax-Lemmata im 22xxx-Bereich, nur dieser eine hängt am Parzival-Pferd, allem Anschein nach wegen der Formähnlichkeit. Das ist ein **älterer** Fehler, keiner dieser Session: vorher standen zwei Pferdebelege unter „Personennamen", jetzt steht ein Ritter unter „Pferdenamen". Netto besser, sauber nicht, und ob `ingligar von jelezie` überhaupt derselbe Name ist, entscheidet KZW und nicht eine Session. Liegt als Rückfrage am Ticket.

**Zwei Suchfehler auf dem Weg dahin, beide in CLAUDE.md geregelt (#126/#130).** Meine erste Zählung ergab null Tokens: `@lemmaRef` trägt `lexicon.xml#lemma_3036`, nicht `#lemma_3036`, das Dateipräfix gehört zum Token. Meine zweite Zählung lief in einen Timeout, und danach habe ich die zwei Parzival-Belege für das ganze Bild gehalten, statt die Messung zu wiederholen. Elf Dateien enthalten die Zeichenkette `lemma_3036`, neun davon nur als Präfix von `lemma_30360` bis `lemma_30369`, zwei mit echten Treffern. Gefunden hat den dritten Beleg das Review, nicht ich. Die Lehre ist weniger die Token-Regel als die banalere Hälfte: eine Messung, die in einen Timeout läuft, ist keine Messung, und ein Teilergebnis darf nicht als Gesamtzahl weitergereicht werden.

**Quercheck der Rubrik**, der zweite Teil von Baustein 1: 49 Lemmata hängen jetzt unter `concept_23221000`, das sind die 48 aus dem Ticket plus Ingliart. Alle 49 tragen `pos=NAM`, alle zehn Namen von Borek sind vertreten, und bis auf einen tragen alle zusätzlich `concept_14012100`. Der eine ist Pegasus, und der gehört dort nicht hin: er führt stattdessen Fabelwesen und Mythologie, was für ein geflügeltes Pferd der griechischen Sage richtiger ist als „Haustier". Kein Befund, sondern eine begründete Ausnahme.

**Was die Kuration praktisch ändert**, damit die Erwartung stimmt: in der Volltextsuche nichts, die zwei Belege waren immer schon auffindbar. Sichtbar wird es im Begriffs-Zugang: wer im Playground die Pferdenamen unter „Pferd und Reiten/Namen" aufblättert, fand dort bisher neun der zehn arthurischen Pferde und Ingliart stattdessen unter den Personennamen. Genau diese Lücke hat Borek von außen bemerkt.

**Lifecycle:** Authority-Index v1.8.0 auf v1.8.1, fünf Stellen gebumpt, Index und die 2.742 API-Dateien neu gebaut. Geändert haben sich davon zwei, `api/index.json` (Versionsangabe) und `api/lemmata/index.json` (der Eintrag selbst). Die Konzept-Dateien unter `api/concepts/` führen nur Metadaten und keine Lemma-Listen, deshalb bleiben sie unberührt: das ist kein vergessener Rebuild, sondern die Form der API.

**Phase:** Betrieb. #193 bleibt offen, Baustein 1 von dreien ist erledigt bis auf die Rückfrage zu `ingligar`; Baustein 2 (Wortlisten-Abgleich) und 3 (der Playground-Explorer) sind eigene Arbeitspakete.

---

## 2026-08-08 (spaeter Nachmittag) – #193 Baustein 2: was eine Quote von 76 Prozent nicht heisst

**Summary:** Boreks drei hippologische Wortlisten von TUdatalib gegen unseren Wortschatz. Neu sind `scripts/ingest/horses/01-wordlist-crosscheck.py` und `ingest/horses/README.md`. Keine Datenaenderung, das ist ein Report.

**Die Zahl, die man aus so einem Abgleich herausliest, ist fast immer die falsche.** 76 Prozent der Pferdebezeichnungen loesen auf, 80 Prozent der Gangarten, 97 Prozent der Koerperteile. Als „24 Prozent fehlen im Lexikon" gelesen waere das eine Arbeitsliste von 124 anzulegenden Lemmata. Tatsaechlich ist `variants.xml` korpus-abgeleitet und kennt nur Schreibungen aus unseren 667 Texten, waehrend Boreks Listen aus einem weiteren Textfeld stammen. Belegt statt behauptet: 34 der 67 nicht aufgeloesten Pferdebezeichnungen tragen ein bekanntes Grundwort in sich, fast alle `-ros`- und `-pfert`-Komposita, und die Gegenprobe zeigt `ros`, `phert`, `vole`, `zelter`, `stuot`, `schenkel` alle vorhanden. Von den geprueften fehlen nur `wallach` und `merhe` wirklich.

**Zwei Zwischenbefunde haetten den Report unbrauchbar gemacht, und beide sahen erst wie Ergebnisse aus.** Borek markiert zwoelf Formen mit einem Stern; ungestrippt scheiterten alle zwoelf an der Aufloesung und erschienen als Wortschatzluecke, gestrippt loesen alle zwoelf auf (Gangarten von 74 auf 80 Prozent). Und die erste Fassung meldete 21 Klassifikationsluecken, von denen die Mehrzahl Fehlaufloesungen waren: `hors` auf `haar`, `roes` auf `rose` die Blume, `oren` auf einen Volksnamen. Die stehen jetzt als eigene Klasse „Verdacht auf Fehlannotation im Korpus", weil sie zu anderer Arbeit fuehren als eine fehlende Konzeptzuordnung.

**Der Bug, den das Review gefunden hat, ist der lehrreichste Teil.** `by_norm` ist ein `defaultdict(list)` und lebt ueber alle drei Listen. Ein Lesezugriff mit eckigen Klammern, `len(by_norm[normalize(f)])`, legt fuer jede ueber Stufe 2 aufgeloeste Form einen leeren Eintrag an. Die naechste Liste nimmt dieselbe Form dann in Stufe 1 mit leerer ID-Liste: sie zaehlt als aufgeloest, faellt aber aus jeder Ergebnisklasse heraus, still. Drei Formen stehen in mehr als einer Liste, und `zeldere` ist genau so verschwunden. Ein `.get()` behebt es. Das ist die Sorte Fehler, die kein Gate faengt und keine Summe verraet, weil die Zahl, die kleiner wird, in keiner Zeile steht.

**Zur Ablage:** die Listen sind CC-BY 4.0 und duerften ins Repo, liegen aber nicht drin. Das Skript holt sie in Sekunden ueber ihre Handles, und eine Kopie waere eine zweite Stelle, die altern kann. Der Attributionsvermerk steht trotzdem prominent, wie es #193 verlangt.

**Als Arbeit bleiben 20 Kandidaten fuer eine Nachklassifikation und 25 Verdachtsfaelle.** Beide brauchen eine philologische Durchsicht, bevor daraus Aenderungen werden; der klarste Block sind die Koerperteile, wo mehrere Lemmata nur an `concept_21030000` (Koerper von Menschen) haengen, obwohl Borek sie fuer Pferdekoerper belegt.

**Phase:** Betrieb. #193 Baustein 2 erledigt, Baustein 3 (Playground-Explorer) unberuehrt.

---

## 2026-08-08 (Abend) – #193 Baustein 3: das Maß hat die Zweifelsfälle erfunden, die es finden sollte

**Summary:** Boreks Belegstellen sind an unser Korpus angeschlossen und der Index `data/horses-index.json.gz` steht (11 KB gz, 346 Belege, 13 Pferde). Neu sind `scripts/ingest/horses/mapping.py` und `03-build-index.py`, `02-map-citations.py` ist auf das gemeinsame Modul umgestellt, DATA-MODEL.md hat einen Abschnitt.

**Der Bericht vom Nachmittag meldete neun Verse ohne Entsprechung. Sechs davon gab es nicht.** Verglichen wurden normalisierte Wortmengen, und daran scheiterte „unt hetz Lehelîn genomn" gegen unser „und hetez lehelîn genomen", ebenso „ans grâles" gegen „an sgrâles". Das Maß hat an Orthographie und Worttrennung versagt, nicht an Textidentität, und damit genau die Zweifelsfälle produziert, deren Aufspüren seine Aufgabe war. Auf der MHD-normalisierten Buchstabenkette bleiben drei. Die Schwelle 0.75 sitzt danach in einer leeren Zone: schwächste akzeptierte Entsprechung 0.84, stärkster verworfener Treffer 0.42.

**Die drei Reste waren keine Reste, sondern ein zu enger Suchradius.** Vier Verse Umkreis reichen nicht, wenn der Versatz über die Grenze des Dreißigers geht: `Pz. 604,18` steht bei uns unter 603,18, textlich zu 1.00 identisch. Und eine falsche Ziffer springt beliebig weit, `Er. 4118` ist textlich `4718`. Werkweit gesucht lösen sich alle drei eindeutig auf, mit 0.32 bis 0.38 Vorsprung vor dem jeweils zweitbesten. Damit sind **336 von 336 Versen textlich verifiziert**, kein einziger bleibt offen. Der Fallback übernimmt nur bei mindestens 0.15 Vorsprung, sonst fände er im Versepos irgendeine Formelzeile.

**Der Berater hat den Fehler gefunden, und zwar nicht durch Nachrechnen, sondern durch Lesen.** Der README nannte als Beispiel für „ohne klare Entsprechung" einen Vers, der bei 0.80 lag und die eigene Schwelle von 0.60 klar überschritt. Ein Beispiel, das der Regel widerspricht, die es illustrieren soll, ist ein zuverlässigerer Indikator als jede Summe: hier hing an ihm das ganze Maß.

**Die Modellierungsfrage ist entschieden, und die Begründung kam aus einer Metadatenzeile.** Gespeichert wird beides, Boreks Zitation wörtlich und unser aufgelöstes Ziel, dazu `match` und `score`. Ausschlaggebend war nicht die Abwägung Provenienz gegen Bequemlichkeit, sondern der Befund, dass **Borek gar keine Ausgabe nennt**: ihr `sourceDesc` führt nur die GND des Werks, während unser Parzival Leitzmann ATB 12 folgt. Eine stille Umrechnung wäre damit unprüfbar, denn prüfbar ist allein der Wortlaut. Der Berater hat zusätzlich den Präzedenzfall beigebracht, den ich nicht auf dem Schirm hatte: #59 hat wegen genau dieser Frage bewusst **keine** Reader-Links gebaut. Hier sind sie vertretbar, aber nur, weil jede einzelne Stelle am Text geprüft ist.

**Nebenbefund mit Folgen für die Zählung:** ein `dict` hat die Mehrfachzitate überschrieben. 346 Stellenangaben entfallen auf 336 Verse, vier werden von zwei Pferden mit abweichendem Wortlaut zitiert, und welche Fassung gewann, hing an der Dokumentreihenfolge. Jetzt werden alle Fassungen bewertet und die beste genommen.

**Das Review fand drei Auszeichnungen, die der Index still verschluckt hat**, alle drei Einzelfälle und deshalb in keiner Summe sichtbar: ein `event`, das innerhalb des Verses steht statt um ihn herum (Pz. 549,7 trägt sein `care` so), ein `objectName` ohne umschließendes `object` (Wh. 77,14, das Schwert Schoyuse), ein `horseGrp` für eine Gruppe statt für dieses Pferd (Pz. 474,3 stellt „ein ors" neben „den orsn"). Wer nur die Vorfahren eines Verses abläuft, verliert den ersten Fall aus jedem Ereignisfilter, ohne dass eine Zahl kleiner wird. Dazu ein latenter Fehler im werkweiten Fallback: die beiden Rangplätze waren nicht nach Vers dedupliziert, also konnte derselbe Vers beide belegen und der Abstand ihn gegen sich selbst messen. Mit dieser Quelle tritt es nicht ein, aber die Falle würde jede Wiederverwendung erben.

**An KZW gemeldet** (#193): die fünf verschobenen Parzival-Verse, die drei fern aufgelösten Stellen zum Gegenlesen, und die Bitte, Luise Borek auf den Zahlendreher hinzuweisen. Eine stillschweigende lokale Korrektur einer fremden publizierten Quelle wäre nicht in Ordnung, auch bei CC0 nicht.

**Zur Lizenz:** TUdatalib führt den Datensatz als CC0 1.0 (publiziert 2023-01-18), die Datei selbst trägt im Header noch „Veröffentlichung unter CC-BY-SA wird angestrebt" und Januar 2017. Das ist der Entwurfsstand, es gilt die Lizenz des Repositoriums. Steht so in DATA-MODEL.md, damit die Frage nicht ein zweites Mal gestellt wird.

**Phase:** Betrieb. #193 Baustein 3 datenseitig fertig, die Playground-Ansicht steht noch aus und gehört mit #194 zusammen.

---

## 2026-08-08 (spät) – #193/#194: die Ansicht, und ein Deep-Link, den es nicht gab

**Summary:** Der Pferde-Explorer steht (`playground/js/ui/tei/horses-explorer.js`), dazu die Rubrik „Experimentelle Forschungsdaten" aus #194, ein Hilfe-Abschnitt, 7 Tests und ein neuer Reader-Parameter `?verseId=`. Voller Playwright-Lauf grün (290 Tests). Lokal committet, **nicht gepusht**: die Abnahme der Oberfläche durch Chris steht aus.

**Der Reader konnte 288 der 346 Belege gar nicht anspringen, und das fiel erst beim Bauen auf.** `?verse=` sucht `<l @n>`. Im Parzival trägt das `<l>` aber nur die Verszahl innerhalb des Dreißigers, die Abschnittsnummer hängt am `<div>`; ein Link auf „26" träfe einen von 827 Versen. Im Willehalm ist es schlimmer: dort gibt es **überhaupt keine Abschnittsgliederung**, die `<l>` hängen nackt in einem `<p>`, und die Dreißiger-Nummer existiert im TEI nicht. Sie steckt einzig in den Wort-IDs. Deshalb rendert jedes `<l>` jetzt `data-core`, die Kernzahl seiner ersten Wort-ID, und `?verseId=PZ_33926` löst darüber auf: korpusweit eindeutig, unabhängig von Zählweise und Struktur. Bestehende `?verse=`-Links bleiben unberührt.

**Das Review fand den Fall, den ich selbst dokumentiert und dann nicht implementiert hatte.** Der Ambraser Einschub im Erec steht vollständig als `<supplied>` in EINEM `<l n="4629">` und deckt die Kerne 462900 bis 462957 ab. Mein `data-core` trug nur den ersten. Die zehn Einschub-Belege hätten also nichts gefunden, und zwar stumm: eine Konsolenwarnung, kein Sprung, der Leser landet am Anfang eines Werks mit 10.135 Versen. Behoben über `data-core-max` und eine Spannensuche. Die Lehre ist unangenehm konkret: ich hatte den Sonderfall zwei Stunden vorher im Modulkopf beschrieben („der Sprung landet auf 4629") und beim Implementieren nicht wiedergelesen.

**Und die Zahl in derselben Beschreibung war falsch.** „24 Verse" hatte ich aus Boreks höchster Zitation (4629,24) gelesen statt aus unseren Daten. Es sind 57. Genau der Fehler, gegen den die Projektregel gemacht ist: eine Zahl, die plausibel aussieht, weil sie irgendwo steht, aber nicht gemessen wurde.

**Eine gemeldete Zahlendifferenz war diesmal keine.** Der Reviewer fand 335 verschiedene Sprungziele bei 336 Versen. Das ist kein Zählfehler, sondern der Zahlendreher: Boreks `4118` und ihr `4718` zeigen beide auf denselben Vers, und genau das ist die richtige Auflösung.

**Zur Modellierung in der Oberfläche:** sichtbar ist immer Boreks Zitation, der Link benutzt unser aufgelöstes Ziel. Die acht auseinanderfallenden Belege tragen ein Sternchen mit dem Grund im Tooltip. Der Hinweis steht am einzelnen Beleg und nicht als Fußnote unter der Tabelle: pauschal formuliert würde er 338 korrekte Stellen mit verdächtigen.

**Phase:** Betrieb. #194 ist mit erledigt und kann nach dem Push geschlossen werden. #193 bleibt offen, bis KZW die acht Stellen gegengelesen hat.

---

## 2026-08-09 – #59: die Gegenrichtung war schon in den Daten, und #111 durfte zu

**Summary:** Lindas beide Wünsche vom 29.07. sind live, dazu der Alexander-Override, der seit dem 28.07. abgesegnet herumlag. #111 geschlossen, weil das gestern gebaute Gate den Reminder ersetzt.

**Der Explorer konnte die Frage schon beantworten, er konnte sie nur nicht stellen.** Jeder Record trägt beides, `who` und `by`, seit dem ersten Build im Juni. Auswählbar war bis heute nur die benannte Figur, der Nenner stand als Beschriftung in der aufgeklappten Belegzeile und sonst nirgends. Beide Wünsche sind deshalb reine Frontend-Arbeit gewesen, kein Rebuild, kein neues Feld, nichts an Lindas Repo. Vorher gemessen statt vermutet: 3.156 Figurenrede-Records, davon genau 3 ohne erfassten Nenner, und pro Werk zwischen 29 und 73 verschiedene Nenner. Lindas eigene Beispielfrage geht exakt auf, Iwein benennt im *Iwein* 26 andere Figuren.

**Zwei Entscheidungen, die die Frage erst vollständig machen.** Der Erzähler ist in der Nenner-Perspektive ein wählbarer Nenner wie jeder andere; im *Iwein* ist er mit 619 Belegen über 47 Figuren die größte Instanz überhaupt, und „welche Benennungen für wen" ist für ihn dieselbe Frage. Und die Selbstnennungen einer Figur zählen zu ihr als Nenner, sonst hätte Iwein 120 statt 129 Belege und die Dreiteilung aus Wunsch 1 (Erzähler, Figurenrede, Selbstnennung) fiele in Wunsch 2 auf zwei Drittel zusammen. Beides steht so in der Antwort an Linda, damit sie widersprechen kann.

**Der Befund kam aus dem Nachmessen, nicht aus dem Bauen.** Die Nennerspalte trägt im Rolandslied eine Notation, die die Figurenspalte nicht hat: ein führendes `#`, Unterstriche, wechselnde Großschreibung. Fünf Nenner zerfielen dadurch in je zwei Einträge, `#David` neben `David`, `#Karlinge` neben `#karlinge`. Das ist genau die Spalte, nach der Linda filtern wollte, also wäre die Ansicht mit einem sichtbaren Defekt live gegangen. Ursache ist zur Hälfte unser Skript: `clean_figure_name` glättet die Unterstriche der benannten Figur, `by` bekommt nur `clean`.

**Gruppiert wird trotzdem in der Ansicht und nicht im Index.** Naheliegender wäre das Skript gewesen, dort stehen die anderen Quirks der Quelle schon. Dagegen sprach, dass die Notation Lindas ist und ich nicht weiß, was das `#` bedeutet: es sieht nach Kollektiv aus (`#haiden`, `#cristen`, `#alle`), aber `#David` und `#Engel` widerlegen das. Eine Bereinigung im Index hätte eine Bedeutung weggeworfen, die ich nicht gelesen habe. In der Ansicht ist es eine Funktion, die wegfällt, sobald Linda die Quelle vereinheitlicht. Die Regel dazu ist gemessen und nicht angenommen: beide erwogenen Schlüssel, mit und ohne MHD-Normalisierung, führen genau dieselben fünf Paare zusammen und sonst nichts, in den anderen drei Werken ändern beide nichts. Also der schlichtere.

**Vier weitere Namenspaare gemeldet statt zusammengefasst.** `Pförnter`/`Pförtner`, `[Bote]`/`[Boten]`, `Oetas`/`Oeteas`, `Herclues`/`Hercules`. Die sehen nach Tippfehlern aus, aber „sieht aus wie" ist bei fremden Forschungsdaten keine Erlaubnis. Der Ähnlichkeitslauf fand als fünftes Paar `die Alte vom Schwarzen Dorn` neben `die Junge vom Schwarzen Dorn`, zwei verschiedene Figuren mit 0,87 Ähnlichkeit, und genau deshalb wird hier nichts automatisch geglättet.

**Der Alias-Override war der billigste Teil und lag am längsten.** Am 12.07. entworfen, am 28.07. von Linda mit „passt sehr gut" abgesegnet, dann nie gebaut, weil der Entwurf „beim nächsten Naming-Update" sagte und das Update ein Cron ist, der keine Menschen anspricht. Wirkung nachgemessen: genau ein Record, TRO V. 20665, von Antonomasie zu Eigenname. Der Build failt hart bei unbekanntem Werk- oder Figurennamen, weil ein Tippfehler sonst wirkungslos in der Datei stünde und die Datei trotzdem so aussähe, als tue sie etwas.

**Der Reviewer hatte einen Befund, und der war ein Kommentar.** Die Begründung an `NARRATOR_KEY` behauptete Kollisionsfreiheit stärker, als `namerKey` sie herstellte: das Gitter wurde vor dem Trimmen abgeschnitten, ein Wert mit führendem Leerzeichen hätte es behalten. In den Daten kommt das nicht vor, der Kommentar wäre also nur zu entschärfen gewesen. Billiger war, den Mechanismus stimmen zu lassen, ein `trim()` weiter nach vorn.

**Kein voller Testlauf**, und das ist gemessen und nicht geraten: der Tailwind-Rebuild war rein additiv, vier neue Klassen, keine weggefallen. Damit betrifft die Änderung nur das eine Modul, dessen 12 Tests grün sind, plus fünf Gates. Die CI hat den Rebuild-and-Compare des Naming-Index mitgemacht, also nimmt auch der wöchentliche Cron den Override mit.

**#111 geschlossen.** Das Ticket war ausdrücklich ein Trigger-Reminder, und seit gestern prüft `check-index-budget.py` genau die Schwelle, die es aufschreiben wollte. Beim Schließen fiel auf, dass die Prognose von 05/2026 nicht eingetroffen ist: erwartet waren 60 bis 80 MB gz binnen zwölf Monaten, tatsächlich steht der Index nach drei Monaten fast unverändert bei 42,17 MB. Der Grund ist nicht, dass die Schätzung falsch gerechnet hätte, sondern dass #27 und #109 nicht ausgespielt wurden. Eine Größenprognose ist eben eine Roadmap-Prognose.

**Phase:** Betrieb. #59 bleibt offen auf `auto:blocked`/`wait:linda`: Linda liest die Ansicht gegen, beantwortet die `#`-Frage und schickt später den Nutzer-Leitfaden mit DOI, den wir dann im Modul verlinken.

---

## 2026-08-09 (Nachmittag) – #358: die Prüfung, die den Umfang ausweiten sollte, hat ihn halbiert

**Summary:** Der Willehalm hat seine 467 `<div type="chapter">`. Der Weg dahin ging über zwei eigene Messfehler und endete bei genau dem Umfang, den das Ticket von Anfang an genannt hatte.

**Das Ticket verlangte selbst, erst das ganze Korpus zu prüfen, und das war richtig.** Nur hat die Prüfung nicht das ergeben, wonach sie suchte. Mein erster Lauf meldete 48 betroffene Werke, weil ich nach `<div @n>` als Vorfahr gesucht hatte und die Strophentexte ihre Nummer am `<lg @n>` tragen. FDS, VIR, NBB und siebzehn weitere sind vollständig ausgezeichnet. Nach der Korrektur blieben 18, davon zehn mit genau einem „Abschnitt": das ist kein fehlendes Kapitel, sondern der Linecode-Offset des Textes selbst. Übrig blieben sieben.

**Danach hat die Messung den Umfang ein zweites Mal eingedampft, und diesmal inhaltlich.** Die sieben sind nicht dasselbe Phänomen. Entscheidend war die Länge: 465 der 467 WH-Abschnitte haben exakt 30 `<l>`. Eine Handschriftenseite mit 465 mal exakt 30 Zeilen gibt es nicht, ein Dreißiger schon. Die Gegenprobe an DIO, dessen 212 `<pb>` Commit `795670240` (#26) im Mai nachweislich aus Julias Linecode-Seitenangaben eingefügt hat, ergab 45 Verse je Einheit bei 210 von 212: echte Seiten, korrekt kodiert. Und WH steht nicht in der #26-Sigle-Liste, seine `<pb>` stammen aus der Ursprungstransformation. Damit ist belegt, was das Ticket vermutet hatte, und zugleich, dass DIO, FB, WLE, FP, RUD und WUT eben nicht mitgemeint sind.

**Ich hatte dem User vorher „alle sieben, gestaffelt" empfohlen und WUT als den billigen Einstieg verkauft.** Beides war falsch, und beides hat erst die Messung gezeigt: WUTs 346 `<lg>` decken sich zwar mit den Abschnitten, aber `lg[344]` und `lg[345]` tragen beide Abschnitt 345, die Abschnitte 326 bis 343 beginnen bei Vers 3 oder 5 statt bei 1, und 316 der „Dreißiger" haben 31 Verse. Das ist eine editorische Frage. Die Staffelung umzudrehen und dann auf einen Text zusammenzustreichen war die Konsequenz aus Zahlen, die es bei der Empfehlung noch nicht gab.

**Die eigentliche Invariante des Migrationsskripts ist nicht die Token-Sequenz.** Die auch, aber sie prüft nur, dass nichts kaputtging. Die inhaltliche Prüfung ist eine andere: je Abschnitt wird die Nummer am neuen `<div>` gegen die aus der ersten Wort-ID abgeleitete gehalten. Das vergleicht die beiden Quellen der Zahl miteinander, statt einer von beiden zu glauben, und es ist derselbe Gedanke wie bei #193, wo der Wortlaut und nicht die Zahl entschieden hat.

**Kein Frontend-Code, und das war keine Sparsamkeit, sondern der Beleg.** Der Reader rendert für `type="chapter"` längst `<h3>Kapitel N</h3>`. Dass WH die sichtbare Abschnittsnummer allein durch die Datenkorrektur bekommt, ohne dass irgendwo ein Sonderfall dazukommt, ist das Argument dafür, dass die Daten und nicht die Anzeige falsch waren. Option 3 aus dem Ticket („nur die Anzeige") hätte denselben Effekt erzeugt und die Ursache konserviert.

**Der Korpus-Index blieb byte-identisch**, bestätigt durch den Rebuild-and-Compare der CI: der Build liest im Body nur `<l>` und `<w>`, nie `div`/`pb`/`p`. Kein Version-Bump, kein Reindex. Eine Korpusänderung dieser Größe ohne jede Bewegung in der abgeleiteten Schicht ist selten genug, um sie zu notieren.

**Der Reviewer fand zwei Zahlen, und beide waren mein eigener Fehler in genau der Disziplin, die dieses Projekt sich aufgeschrieben hat.** „Die beiden anderen 23 und 28" mischte zwei Messvorschriften in einer Klammer: Abschnitt 467 hat 24 `<l>`, davon 23 mit Tokens, weil sein `<l n="24">` nur eine `<caesura>` enthält. Und „DIO: 45 Verse je Einheit" war eine Idealisierung von 210 der 212. Beide Zahlen waren für sich richtig und in der Formulierung falsch.

**Phase:** Betrieb. #358 steht auf `auto:blocked`/`wait:kzw` mit drei benannten Fragen: ob DIOs und FBs `<pb>` als Seiten richtig sind, wie WUTs Doppelabschnitt 345 und die bei Vers 3 beginnenden Abschnitte zu lesen sind, und was mit RUD, WLE und FP geschieht.

---

## 2026-08-10 (Nachmittag) – #361: die Kette war keine Hierarchie, weil die Daten eine Hülle sind

**Summary:** Der Gattungs-Explorer zeigt die Textreihentypologie als aufklappbaren Baum. Aus #93 herausgelöst, weil dieser Teil an nichts hängt, was auf KZW und Marco Heiles wartet. Authority-Index v1.8.1 auf v1.9.0.

**Der Defekt war eine Zeile, die Ursache ein Datenmodell.** Die Ansicht verkettete die übergeordneten Gattungen mit " UND ", und bei `genre_26c0ce4c` wurden daraus gemessene 408 Zeichen aus 20 Namen. Das sah nach einem Anzeigefehler aus und war keiner: `genres.xml` speichert die volle transitive Hülle, jede Kategorie nennt **alle** ihre Vorfahren statt nur der nächsten. 615 Kategorien tragen so 3.175 Kanten. Die Zeile war also korrekt, sie gab nur wieder, was dasteht. Eine Hierarchie lässt sich daraus nicht zeichnen, weil eine Abkürzungskante (Wurzel → Blatt) von einer echten Elternkante nicht zu unterscheiden ist.

**Die Reduktion gehört in den Build, nicht in die Ansicht.** `_direct_parents()` streicht jeden Elternteil, den ein anderer Elternteil bereits als Vorfahren führt: 3.175 Kanten werden 819. Danach 2 Wurzeln (*Epik, Lyrik und Dramatik*, *Wissensliteratur und Gebrauchsliteratur*), 442 Kategorien mit einem direkten Elternteil, 139 mit zwei, 29 mit drei, 3 mit vier. Der Schritt ist nur zulässig, weil die Menge wirklich eine Hülle ist, und das wurde geprüft statt angenommen: für alle 3.175 Kanten gilt die Enthaltensein-Bedingung, null Verletzungen, null tote Verweise, null Selbstbezüge.

**Die Messung hat die einzige echte Designfrage entschärft, bevor sie gestellt war.** Das Ticket kam als `auto:checkin` herein, weil 171 Kategorien mehr als einen Elternteil haben und ein Baum sie entweder mehrfach zeigen muss oder einmal mit Querverweisen. Die Sorge war der Umfang: bei Tiefe 20, wie das Ticket sagte, klingt Duplizieren nach Explosion. Gemessen ist die Tiefe aber 9 (die 20 im Ticket war die Hüllengröße, nicht die Pfadlänge), und voll entfaltet belegen die 615 Kategorien 1.167 Baumplätze, Faktor 1,9. Damit kostet Duplizieren praktisch nichts, und es ist auch das Richtige: ein *Predigtmärlein* IST *Märe* und *Predigt*, `Monatsregimen` steht unter *Kalender*, *Tagewählerei* und *Text zur Diätetik* zugleich. Es unter einen Elternteil zu zwingen wäre eine Aussage über die Typologie, die die Daten nicht machen.

**Aus derselben Einsicht folgt die DOM-Regel.** Die Schlüssel des Baums sind der **Pfad**, nicht die Kategorie-ID, sonst hätten die 171 mehrfach einsortierten Kategorien kollidierende Knoten und ließen sich nicht unabhängig auf- und zuklappen. Dasselbe Motiv beim Detailfeld: eines für den ganzen Baum statt eines pro Knoten. Der Test dafür ist der wichtigste der sieben.

**Die alte Karte ist weg statt ergänzt.** `maps.genreHierarchy` trug Eltern-*Namen* und die volle Hülle, und ihr einziger Konsument war genau die UND-Kette. Sie durch ein Feld an den Gattungs-Einträgen zu ersetzen war billiger als beides zu pflegen; der Index ist dadurch netto 5,4 KB kleiner geworden.

**Erwartungsdämpfer, der in die Ansicht gehört.** 482 der 615 Kategorien haben im ganzen Zweig unter sich kein einziges Werk unseres Korpus, benutzt werden 92 mit 874 Referenzen. Ein Baum ohne diese Angabe führt in leere Äste. Jeder Knoten nennt deshalb eigene Werke und Werke im Zweig, und was zu nichts führt, ist gedimmt und beschriftet.

**Vier Reviewrunden, und die letzte war die wertvollste.** Runde 1 und 2 (`fable-reviewer`, vor dem Push) fanden Textpfeile `▸`/`▾` statt Heroicons und ein `aria-label`, das an allen 615 Knöpfen gleich lautete und den Zustand doppelt trug. Dann schrieb der CI-Bot fünf Befunde, und Runde 3 hatte nicht mehr die Aufgabe, den Diff zu lesen, sondern **diese fünf zu beurteilen**: drei real, einer als billiger Mitnahmefix, einer fallenzulassen (ein `?.`-Fallback, den kein Ladepfad erreicht). Das ist die Projektregel „ein Befund ist selbst eine Behauptung“ in ihrer nützlichsten Form, und sie hat hier zwei Arbeitspakete gespart statt eines erzeugt.

**Der teuerste Befund war ein Nebenschaden meiner eigenen Aufräumarbeit.** Die Checkbox „Nur Gattungen mit zugeordneten Werken anzeigen“ aus #119 war im Baum-Ruhezustand ein No-op, weil ihr Handler in `searchGenres` läuft und die Methode bei leerem Suchfeld vorher zurückkehrt. Der No-op ist älter als dieser PR, unsichtbar war er aber nur, solange unter der Checkbox die Aufforderung zum Suchen stand. Sobald dort eine vollständige Ansicht steht, sieht sie aus, als beziehe sie sich darauf. Jetzt tut sie das: 1.167 Baumplätze fallen auf 246, dahinter genau die 133 belegten Kategorien. Dass das den Baum nicht zerreißen kann, ist keine Beobachtung, sondern folgt aus der Konstruktion, die Werkmenge eines Elternteils ist die Obermenge jedes Kindzweigs. Dazu zwei Barrierefreiheits-Befunde: das Detailfeld steht hinter dem ganzen Baum und war nach einem Klick weit oben nicht zu sehen, und `renderTree()` zerstörte den gedrückten Knopf samt Tastaturfokus.

**Und ein Test, der schwächer prüfte als sein eigener Kommentar.** Der wichtigste der Specs filterte mit `onclick.includes(id)`, und weil der Schlüssel der Pfad ist, traf das auch jeden Nachfahren. Zwei Treffer kamen nur heraus, weil die eine Unterkategorie der Predigt selbst keine Kinder hat. Er hätte nie falsch grün werden können, nur irreführend rot, aber der Kommentar darüber behauptete etwas anderes als der Code prüfte, und genau das verbietet die Regel.

**Nicht Teil davon:** der Abgleich mit `Middle-High-German-Conceptual-Database/textseries` (618 Konzepte dort gegen 615 hier, 157 Kanten nur dort, 95 nur hier) und die toten `dhplus`-URIs. Das bleibt in #93 und braucht eine philologische Entscheidung darüber, welcher Stand gilt.

**Phase:** Betrieb, in einem Worktree gebaut, während die Parallelsession #59 gemerged hat. Der Rebase auf den neuen `main` hatte genau einen Konflikt, die einzeilige Tailwind-Ausgabe, und der wurde durch `npm run build:css` erledigt statt von Hand.

---

## 2026-08-10 – #59: das Gitter darf bleiben, weil wir jetzt wissen, was es heißt

**Summary:** Lindas drei Punkte vom Morgen sind umgesetzt: „Nennende Instanz" statt „Nennende Figur", Alexander als eigene Kategorie *Deckname* statt als Eigenname, und ihr Quell-Commit `b7cc0585` zieht die Gruppierungsfunktion vom 09.08. ersatzlos zurück. 297/297 grün.

**Die Funktion ist weggefallen wie geplant, nur aus einem stärkeren Grund als geplant.** Gestern stand im Kommentar, die `#`-Gruppierung liege in der Ansicht statt im Index, weil sie dann bei einer Vereinheitlichung der Quelle „als Funktion wegfällt statt als Datenstand". Genau das ist eingetreten, einen Tag später. Gemessen gegen Lindas neuen Stand führt der Schlüssel nichts mehr zusammen (distinkte `by`-Werte je Werk, also ohne Erzähler und Selbstnennungen: 33/29/48/71 in IW/ENE/ROL/TRO, mit und ohne Gitter-Schnitt identisch; die Nennerliste des Moduls zählt mit Erzähler und Selbstnennungen 36/31/50/73). Der eigentliche Grund, ihn zu entfernen, ist aber ein anderer: Linda hat erklärt, wofür das `#` steht, nämlich für eine Instanz, die keine handelnde Figur des Werks ist, entweder eine unbestimmbare Menge (`#haiden`) oder eine nur zitierte Person (`#David`, den der Erzähler anführt). Damit ist das Abschneiden nicht mehr nur überflüssig, sondern falsch: `#David` und ein handelnder David wären derselbe Schlüssel und derselbe Nenner. Das Zeichen steht jetzt in der Anzeige, mit ihrer Erklärung darunter.

**Die Zurückhaltung von gestern hat sich bezahlt gemacht, und zwar messbar.** Hätte das Skript die Notation im Index bereinigt, stünde heute eine Bedeutung nicht mehr in den Daten, die wir inzwischen kennen und im Modul erklären. Der Aufwand für den Rückbau war eine Funktion und ein Regex; der Aufwand für einen Rückbau im Index wäre ein Rebuild gegen einen Quellstand gewesen, den es so nicht mehr gibt.

**Der Deckname ist eine vierte Kategorie und keine Umbenennung.** Linda: „Der Name sollte in dem Fall nicht als 'Eigenname', sondern als 'Deckname' gelabelt werden." Damit sitzt er zwischen Eigenname und Antonomasie, benennt die Figur wie ein Name, ohne ihr Name zu sein, und darf in keiner der beiden aufgehen. `alias-overrides.json` trägt deshalb jetzt ein Pflichtfeld `category` mit zwei erlaubten Werten, `deck` und `eig`; fehlt es oder steht etwas anderes darin, bricht der Build ab. Kein Default: der Unterschied zwischen einem Decknamen und einem bloß fehlenden Namensalias ist eine philologische Aussage, die ein neuer Eintrag nicht stillschweigend erben soll. Beide Fehlerfälle sind gegen die geladene Funktion getestet, nicht behauptet.

**Eine Kategorie mit genau einem Beleg im ganzen Index braucht eine Anzeigeregel.** Tab und Kachel erscheinen nur, wo die Kategorie trifft, sonst stünde in 615 von 616 Figuren eine Null neben drei gefüllten Kategorien und läse sich wie eine Erhebungslücke statt wie ein kuratierter Sonderfall. Eine Ausnahme davon ist nötig und stand nicht im ersten Entwurf: ist der Deckname-Tab gerade der gewählte, bleibt er sichtbar, auch wenn ein Unterfilter ihn auf 0 bringt. Sonst verschwindet das aktive Steuerelement, und die leere Tabelle hat keinen sichtbaren Grund mehr.

**Vier gemeldete Namenspaare, drei waren Tippfehler, eines nicht.** `Pförnter`, `Herclues` und `Oeteas` sind korrigiert, `[Bote]` neben `[Boten]` bleibt: ein sprechender Bote und mehrere sprechende Boten. Das ist die Bestätigung für die Regel von gestern, nichts automatisch zu glätten, was nach einem Tippfehler aussieht. Vier von fünf hätten gestimmt, und das fünfte hätte zwei Instanzen zu einer gemacht.

**Zwei Sessions in derselben Datei, und die Git-Regel greift dafür nicht.** Eine Parallel-Session hat `naming-explorer.js` gegen 10:05 per Skript in-place überschrieben, während diese Session dieselbe Datei bearbeitete; das Ergebnis war ein lauffähiger Mischstand, in dem zwei Methoden aus der anderen Fassung stammten. Aufgefallen ist es an einem `Edit`, dessen Suchtext nicht mehr passte, und an einem NUL-Byte, das dabei in die Datei geriet (`git grep` meldete sie als binär). Die bestehende Regel adressiert den *Index* (`git add -A`), nicht den *Arbeitsbaum*. Was hier geholfen hat, war die Übergabe im Klartext: die andere Session hat aufgeschrieben, welche Methoden ihre sind und was davon weg soll, und diese Session hat den Diff danach ganz gelesen statt nur die eigenen Stellen.

**Der Sentinel, der kollisionsfreier aussah, war der einzige echte Fehler.** `NARRATOR_KEY` hing vorher daran, dass `namerKey` das führende `#` abschnitt; als das wegfiel, brauchte er einen eigenen Grund. Meine Wahl war U+0000, und die ist falsch: der Schlüssel steht als `<option value>` in einem `innerHTML`, und der HTML-Tokenizer ersetzt U+0000 im Attributwert durch U+FFFD. Der Wert aus dem Select traf den Schlüssel damit nie, und die Erzähler-Auswahl lieferte in allen vier Werken 0 Treffer, beim belegstärksten Nenner jedes Werks. Der `fable-reviewer` und der CI-Bot haben ihn unabhängig gefunden, der eine gemessen, der andere aus der Parser-Spezifikation hergeleitet. Richtig ist ein Sentinel aus Großbuchstaben: `namerKey` schreibt alles klein, also kann kein echter Nenner ihn erzeugen, und durch ein Attribut geht er unverändert. Die 297 grünen Tests hatten den Fehler nicht gesehen, weil kein einziger den Erzähler je ausgewählt hatte, obwohl er in jedem Werk ganz oben steht.

**Der neue Test hat zweimal aus dem falschen Grund rot gezeigt**, und beide Male lag es an ihm. Erst nahm `selectOption` die RegExp im `label` nicht an, dann brach `\d+` am Tausenderpunkt des ROL-Erzählers (1.222 Belege, `toLocaleString('de-DE')`). Erst der dritte Anlauf hat gemessen, was er messen sollte. Er liest den Wert jetzt aus dem DOM zurück, statt ihn hinzuschreiben: genau die Round-Trip-Eigenschaft, an der der Sentinel gescheitert ist. Gegenprobe nach Projektregel: mit dem alten Sentinel fällt er, mit dem neuen läuft er.

**Zwei weitere Befunde waren meine eigenen Zahlen.** „Eckige Klammern (Trojanerkrieg)" stand im Kommentar, obwohl ich die Verteilung Stunden vorher selbst gemessen hatte: sie stehen in IW (7), ENE (7) und TRO (14), nur ROL hat keine. Und „33/29/48/71 Nenner" ist die Zählung über die distinkten `by`-Werte; die Liste, die das Modul anzeigt, hat mit Erzähler und Selbstnennungen 36/31/50/73. Beide Zahlen waren richtig und ohne Messvorschrift trotzdem irreführend, dieselbe Fehlerklasse wie am 31.07. bei den Breve-Zahlen.

**Phase:** Betrieb. #59 bleibt offen auf `auto:blocked`/`wait:linda`: der Nutzer-Leitfaden mit DOI fehlt weiter, und Linda will die eckigen Klammern im Trojanerkrieg noch auf die Gitter-Notation vereinheitlichen. Der Erklärsatz im Modul nennt beide Notationen und zieht seine Beispiele aus dem jeweiligen Werk, er stimmt danach also ohne Nacharbeit.

---

## 2026-08-24 – #216 Serie 1: der Filter, der die schweren Fälle finden sollte, kannte kein Mittelhochdeutsch

**Summary:** 6.982 unannotierte Tokens der Form `minne` aus 262 Texten kontextdisambiguiert, in 118 Bündeln von je etwa 60 Fällen. 5.435 sind in 255 Texten annotiert (5.106 zu `lemma_4130` NOM, 329 zu `lemma_4133` VRB), 1.547 bewusst zurückgehalten. Drei Regeln halten zurück, gemessen gefeuert haben zwei davon: 1.546 Fälle an der Konfidenz unter `high`, einer am Konflikt zwischen Verdict und bestehendem `@pos`. Die dritte, das Verbot einer automatischen NAM-Vergabe, hat nie gegriffen, weil der Prompt NAM auf höchstens `medium` deckelt und damit schon die erste Regel zieht: ein Sicherheitsnetz, das nur an einem zweiten Faden hängt. 982 der zurückgehaltenen Fälle tragen NAM als Verdict, das ist die Personifikation „Frau Minne". Der Rückhalt ist kein Rest, er ist die Entscheidung: ob eine Stelle die Allegorie meint, ist eine philologische Frage, keine LLM-Frage.

**Drei Stichproben-Durchgänge, 150 Fälle, kein Fehler – und der zweite Durchgang war wertlos.** Die „schwere" Stichprobe sollte gezielt Fälle ohne stützenden Vorgänger ziehen. Der Prüfer maß nach, dass 46 Prozent der gezogenen Fälle sehr wohl einen Artikel oder ein Possessivum vor sich hatten. Ursache war die Wortliste des Filters: sie kannte `der`, `die`, `dîn`, nicht aber `di`, `dorch`, `sîner`, `grozzer`. **Eine Wortliste ist im Mittelhochdeutschen kein Filter**, weil es die eine Schreibung nicht gibt. Der Ersatz fragt nicht mehr den Text, sondern das `@pos` des vorangehenden `<w>` im TEI, und der traf.

**Ein Nullbefund aus dem eigenen Skript ist noch kein Befund.** Die Prüfung des `wâren`-Nebenbefunds meldete zunächst null Treffer korpusweit. Der Grund lag im Skript: `@corresp` trägt `variants.xml#type_273621`, verglichen wurde auf den blanken Typnamen. Nach dem Fix waren es 5.641. Seither prüft jedes Messskript hier zuerst einen bekannten Positivfall, bevor seine Null etwas heißt.

**Zwei Heuristiken sind gescheitert, und das steht so im Log.** Der Verdacht, `minne` stehe in GWTK stellenweise für das Possessivum *mîne*, ließ sich korpusweit weder belegen noch ausschließen: die Kontextheuristik erzeugte 1.181 Fehlalarme (Genitivattribute), das Verhältnismaß bildet nur den Themenanteil eines Textes ab. Sieben Verdachtsfälle liegen als Review bei KZW. Ein „nicht entschieden" im Provenienz-Log ist billiger als eine Zahl, die niemand nachrechnen kann.

**Der Lifecycle wurde gemessen statt geschätzt.** `extract-variants.py` im Trockenlauf meldet alle vier Semantik-Zähler auf 0, also entfallen die Schritte 5 und 6 und der Authority-Index bleibt bei 1.9.0: der Batch vergibt ausschließlich die beiden bestehenden Typen. Gebumpt wurde nur der Korpus-Index (4.2.1 → 4.2.2). Die Abnahme lief nicht über das grüne Build-Log, sondern über einen positionsgenauen Abgleich gegen den Vorstand: Belegstellen 7.532.982 → 7.538.417, Differenz exakt 5.435, genau zwei Lemmata mit veränderter Belegzahl, kein Text mit Positionsverlust.

**Nebenbefund als eigenes Ticket (#367), und beim Aufschreiben ist er beinahe falsch geworden.** `wâren` ist als Verb (`wesen`) getaggt, wo das flektierte Adjektiv `wâr` steht; belegt sind 40 Fälle „der/die wâren minne". Die erste Fassung des Tickets stellte sie als „davon" unter 5.641 Vorkommen des Variantentyps `type_273621`. Das kann nicht sein: zwei der 40 schreiben `wæren` und `woren` und tragen deshalb einen anderen Typ. Über den Variantentyp gemessen sind es 38, über die Schreibfamilie unter `lemma_7505` sind es 40, und beide Zahlen sind richtig, solange die Vorschrift danebensteht. Die naheliegende Kennzahl taugt ohnehin nicht als Fehlermaß: von den 936 Vorkommen nach einem Artikel und den 168 in der Stellung ART + `wâren` + NOM ist die Mehrheit korrektes Prädikativ („daz wâren brüeder").

**Zwei Review-Runden, acht Befunde, kein einziger am Verhalten.** Alle acht betrafen Zahlen in Prosa, und drei davon zeigen dasselbe Muster: eine fremde Zahl übernommen, statt sie zu messen (8.385 Belege und 914 Vorkommen, beide aus einem Prüfer-Bericht, beide unter keiner Vorschrift reproduzierbar), eine Zahl aus einer Konsolenausgabe gelesen, in der Windows die Diakritika durch `?` ersetzt hatte (die 907 sind `waeren` mit ASCII-Digraph, nicht `wæren`), und eine Restmenge subtrahiert statt gezählt: „ohne beide Stützen 957" war arithmetisch ausgeschlossen, weil zwei überschneidende Mengen von 1.144 und 1.084 in 2.041 höchstens 897 übrig lassen können. Gezählt sind es 409. Das Skript etikettierte richtig, der Fließtext daneben nicht.

**Phase:** Betrieb, `claude/216-minne-serie1`. Schema-Stichprobe, Cross-Ref-Audit und `validate-indices.py` grün, Playwright 310/310.

---

## 2026-08-24 – #369 Serie 2: das Kandidatenpaar war zu eng, und der Lauf hat es selbst gezeigt

**Summary:** 7.855 unannotierte Tokens der Form `stat`/`stât` aus 326 Texten disambiguiert, in 131 Bündeln zu je 60 Fällen. 7.760 sind in 322 Texten annotiert (6.665 zu `lemma_5732` NOM, 1.095 zu `lemma_5710` VRB), 95 zurückgehalten. Die Rückhaltequote fällt damit von 22 Prozent in Serie 1 auf 1,2 Prozent, und der Grund ist nicht ein besserer Lauf, sondern ein anderer Gegenstand: bei `minne` war die Personifikation der große Posten, bei `stat` gibt es nichts Vergleichbares.

**Die Serie hätte man nicht mit einer Regel erledigen können, und das ist der eigentliche Befund.** Korpusweit ist `stat` sechsmal häufiger das Substantiv als das Verb, aber das Verhältnis kippt textweise vollständig. In den Stadtchroniken und Trojaromanen (RCC, TRO, OVG, KCR, JEW) tragen ganze Bündel 60 von 60 Substantiven, in Rudolfs Weltchronik, im Tristan und bei Frauenlob überwiegt das Verb mit bis zu 42 von 60. Eine Mehrheitsregel hätte in der einen Gruppe alles richtig und in der anderen alles falsch gemacht.

**51 der 95 Rückhaltefälle sind gar kein Zweifel zwischen den beiden Kandidaten, sondern ein anderes Wort.** 32 Belege meinen das maskuline `stat` im Sinn von Ufer (die Landungsszenen im Trojanerkrieg, `an den stat` im Parzival), 13 den Stand oder Zustand (`stat und wesen` im Prosalancelot), 6 sind das Adjektiv *stæte* in den Urkundenformeln von HZU2, und einer ist ein lateinisches Bibelzitat. Der Prompt kannte keine dieser Bedeutungen. Die Bearbeiter haben sie trotzdem erkannt und die Konfidenz gesenkt, statt den nächstbesten Kandidaten zu nehmen. **Ein zu enges Kandidatenpaar erzeugt keine falschen Annotationen, solange die Konfidenz die Notlage ausdrücken darf** – die Regel „bei Zweifel senke die Konfidenz" trägt mehr als die Aufzählung der erwarteten Fälle. Für das Ufer gibt es im Korpus ohnehin keine geübte Zuordnung: unter `lemma_5712` (*stade*) stehen nur `stade`, `staden`, `stades`, nie `stat`. Vorgelegt als #371.

**Diese Zahlen waren beim ersten Aufschreiben falsch, und der Fehler ist lehrreicher als die Zahlen.** Die Kategorien stammten aus einer Stichwortsuche über die Freitext-Begründungen der Verdicts, und die griff dreimal daneben: `adjektiv` fing `gût stat` und `heiligen stât` ein, wo das Adjektiv ein anderes Wort ist; `stand` traf im Prosa-Kontextfenster statt in der Begründung und zog einen Fall herein, der ein Verb-Verdict ist; `staet ze haben` fiel durch, weil es nicht auf `staete` passt. **Freitext, den ein Modell geschrieben hat, ist keine Klassifikation, auch wenn er wie eine aussieht.** Ersetzt ist die Heuristik durch eine Klassifikation am Beleg, die als `kategorien-review.json` im Batch-Ordner liegt statt als Zahl in einem Satz. Ab Serie 3 gehört ein Feld für das dritte Lemma ins Verdict-Schema, dann entsteht die Frage gar nicht erst. Aufgefallen ist der Widerspruch zuerst als Rechenfehler (30 + 12 + 6 sind 48, im Text stand 42), und erst beim Nachrechnen zeigte sich, dass auch die Summanden nicht stimmten.

**Ein Prompt-Fehler, der teuer gewesen wäre, und seine Korrektur ist gemessen.** Version 1 formulierte die Konfidenzregel zur Schreibung symmetrisch: die Zirkumflex-Form `stât` sollte ein NOM-Verdict deckeln, und der Satz las sich, als gelte dasselbe umgekehrt. Das hätte 7.688 der 7.855 Fälle auf `medium` gedrückt, also fast den ganzen Batch in den Review geschoben. Die acht bereits bearbeiteten Bündel wurden mit Version 2 wiederholt, und der Vergleich beider Läufe über dieselben 480 Fälle ergab **100 Prozent Übereinstimmung im Verdict** bei einer Konfidenz von 26 `medium` auf 1. Der Fehler hätte keine falsche Annotation erzeugt, sondern richtige verhindert. Nebenbei ist das die einzige Doppelmessung dieser Serie, und sie kostete nichts extra.

**Die Blindprüfung ist blind, seit sie es vorher nicht war.** Beide Stichproben zu je 50 Fällen gingen ohne Verdict, Konfidenz und Begründung an den Prüfer, der Abgleich lief hinterher maschinell über die xml:id. Ergebnis: null Abweichungen in beiden Durchgängen, auch in der schweren, die gezielt Fälle ohne stützenden Vorgänger zieht. Zwei Fälle hat der Prüfer als unsicher markiert, beide Ufer-Belege: er entschied die Wortart richtig und vermisste dasselbe dritte Lemma. Damit ist der Befund unabhängig zweimal entstanden.

**Der Filter der schweren Stichprobe war wieder falsch, diesmal eine Ebene höher.** Serie 1 scheiterte an einer Wortliste, die kein Mittelhochdeutsch kannte; der Ersatz fragt das `@pos` des vorangehenden `<w>`. Dieser Ersatz verglich den ganzen Attributwert gegen die Markermenge und zählte deshalb Tokens mit Mehrfachtag (`ART NUM`, `ADJ ADV`) als schwer, obwohl der Artikel danebensteht. Nach der Korrektur auf einen Vergleich je Tag sind es 1.647 statt 2.571 von 7.760. **Ein Filter, der Annotationen liest, muss das Format der Annotation kennen, nicht nur ihre Werte.**

**Der Lifecycle wurde wieder gemessen statt geschätzt**, mit demselben Ergebnis: alle vier Semantik-Zähler von `extract-variants.py` auf 0, Schritte 5 und 6 entfallen, Authority-Index bleibt 1.9.0, Korpus-Index 4.2.2 → 4.2.3. Der positionsgenaue Abgleich gegen `HEAD`: Belegstellen 7.538.417 → 7.546.177, Differenz exakt 7.760, genau zwei Lemmata verändert, kein Text mit Positionsverlust. `lemma_5732` steigt von 2.394 auf 9.059 Belege und von 160 auf 332 Texte: das Substantiv war im Index bisher massiv unterrepräsentiert.

**Sieben Skripte generisch statt serienspezifisch.** Serie 1 hinterließ `extract-216-minne.py`, `fix-216-minne.py` und `revisiondesc-216-minne.py`; Serie 2 hat daraus `extract-homograph.py`, `apply-homograph.py`, `revisiondesc-homograph.py` und vier weitere gemacht, die ihre Serienparameter aus einer `config.json` im Batch-Ordner ziehen. Serie 3 braucht damit keine Kopie mehr, sondern eine Konfigurationsdatei.

**Ein einziges Token als eigener PR, und der Grund ist die Trennschärfe.** Bei der Sondierung fiel `SKT_502140_4` auf: `stât` als Substantiv annotiert, obwohl *mîn gedanc an ir vil hôhe stât* das Verb ist. Der Beleg war korpusweit der einzige seines Variantentyps `type_218598`, weshalb die Serie für das Paar `stât` plus Substantiv-Lemma gar keinen Bestands-Typ ansetzen konnte. Die Korrektur macht den Typ unbelegt und zieht damit `variants.xml`, den Authority-Index (1.9.0 auf 1.9.1) und beide Neubauten nach: genau die Schritte, die dieser Batch nachweislich nicht auslöst. **Ein Ein-Zeilen-Fix, der den abgeleiteten Layer anfasst, gehört nicht in einen PR, dessen zentrale Aussage lautet, dass er ihn nicht anfasst.** Als eigener PR unmittelbar danach kostet er zehn Minuten und lässt beide Aussagen wahr. Präzedenzfall für dieselbe Mechanik: 1.6.4, wo `variants.xml` den nur in HUG belegten Typ `type_195524` verlor.

**Phase:** Betrieb, `claude/369-stat-serie2`. Schema-Stichprobe 9/10 (der eine Fail ist ADP aus der 30er-Baseline), Cross-Ref-Audit und `validate-indices.py` grün, Playwright 310/310.

---

## 2026-08-31 – Drei entblockte Tickets, und zweimal war die Messvorschrift das Byte

**Summary:** Julia Hintersteiner und KZW haben am 25./26.08. drei Fragen beantwortet, die je ein Ticket blockierten. Daraus drei PRs in einer Session: #374 nimmt `role="lead-editor"` aus der WZB und bringt die Doku von vier auf fünf Sigel, #377 annotiert 40 Belege der Fügung *der/die wâren minne* vom Verb aufs Adjektiv um (Korpus-Index 4.2.4 auf 4.2.5, Authority 1.9.1 auf 1.9.2), #235 Punkt 3 annotiert 66 von 289 Breve-Tokens der WZB mechanisch nach (Korpus-Index 4.2.5 auf 4.2.6, Authority unverändert). Damit ist auch die Frage beantwortet, die der Eintrag vom 02.08. offen ließ: die Auszeichnung bezeichnete Julias Rolle im Editionsprozess, nicht den Status des Textes, ihr Beitrag bleibt im `respStmt` verzeichnet und nur die Rollenbezeichnung fällt.

**Ein Diff, der zeichenweise stimmt, ist keine Messung.** Der erste WZB-Edit lief über das Edit-Werkzeug und sah im `git diff` genau so aus wie beabsichtigt: eine Zeile, ein entferntes Attribut. Tatsächlich hatte er 17 fremde reine LF-Zeilen still auf CRLF vereinheitlicht. Die WZB ist die einzige Datei im Korpus mit CRLF (gemessen: 1 von 667) und mischt darin 235.973 CRLF- mit 17 LF-Zeilen, die aus Julias Token-Split `f3dcf2a86` stammen. Sichtbar wurde das erst beim Byte-Vergleich gegen `origin/main`; die Diff-Hunks selbst waren zeichengleich. Alle drei Wellen haben ihre WZB-Änderungen danach über exakte Byte-Ersetzung mit `newline=""` beim Lesen **und** Schreiben ausgeführt und die beiden Zähler vorher und nachher protokolliert.

**Und derselbe Fehler kam ein zweites Mal, weil die Prüfung jetzt dastand.** `revisiondesc-homograph.py` hängt seinen `<change>`-Eintrag mit einem harten `"\n"` an. In den 666 reinen LF-Dateien fällt das nicht auf, in der WZB stieg die Zahl der reinen LF-Zeilen von 17 auf 18. Das Skript nimmt das Zeilenende jetzt aus der Umgebung. Der Punkt ist nicht der Fix, sondern dass die Kontrollzahl aus Welle 1 den Fehler in Welle 3 abgefangen hat, ohne dass jemand nach ihm gesucht hätte.

**Zweimal Skript reparieren und Daten neu erzeugen, nicht nachbessern.** Die Regel aus #236 wurde in Welle 3 zweimal gebraucht: einmal, weil dem Backfill-Skript die Spalte `file` fehlte, die `revisiondesc-homograph.py` als Schnittstelle liest, einmal wegen des Zeilenendes. Beide Male ging `tei/WZB.tei.xml` zurück auf `HEAD` und die ganze Kette neu, beide Male reproduzierte sie 66 ANNOTATE und 223 REVIEW identisch. Das ist der Reproduzierbarkeitsbeleg, den die Idempotenz allein nicht liefert.

**Die 66 sind mechanisch, und die 223 sind es genau deshalb nicht.** Annotiert wurde nur, wo die MHG-normalisierte Schreibung in `variants.xml` genau ein Lemma trifft und dieses Lemma genau eine Wortart hat: kein LLM, keine Kontextentscheidung, 46 NOM, 18 VRB, 1 ADJ, 1 NUM. Zurückgehalten sind 112 ohne Treffer im Lexikon (`ŏpfeltragendes`, `gevŏggeln`, `bŏvme`), 98 mit mehrdeutiger Wortart am Ziel-Lemma (`bŏse` führt auf `lemma_788` mit ADJ, ADV, GRA und NOM) und 13 mit mehreren Ziel-Lemmata. Die 98 sind ein Arbeitspaket nach dem Muster #216/#369 und bleiben in #235 stehen. Kein `corresp`: alle eindeutig auflösenden Kandidaten brauchten unter ihrem Ziel-Lemma eine neu geprägte Typnummer (113 distinkte Form-Lemma-Paare), und neue Typen sind genehmigungspflichtig. Die 66 landen damit in derselben Lage wie die 52.097 anderen WZB-Tokens aus #370.

**Der Nebenbefund war größer als das Ticket.** Bei der Sondierung für #367 fiel auf, dass die Varianten-Map beim Aufbau nach first-wins entscheidet: trägt dieselbe Schreibform Typen unter zwei Lemmata, gewinnt das zuerst gelesene, nicht das häufigere. Roh sind 1.893 Formen betroffen, für Nutzerinnen sichtbar 1.272, weil Stufe 1 der Lemma-Auflösung den Rest vorher abfängt. Die rohe Zahl allein hätte den Befund dramatischer aussehen lassen, als er ist, die kleine allein hätte den Umfang verdeckt. Beide stehen in #378, mit ihrer jeweiligen Messvorschrift. Eine Zweitmeinung nannte an derselben Stelle 2.065 und 1.331; übernommen wurde nichts davon, gemessen und in das Ticket geschrieben ist die eigene Zahl samt Zählweise, und dass die Differenz offen ist, steht dabei.

**Der Review-Bot der CI ist auf Daten-PRs weiter unbrauchbar, jetzt zum zweiten Mal belegt.** Auf #377 meldete die GitHub-API `changed_files: 0`, die Plattform hatte den Diff also gar nicht berechnet: dieselbe Lage wie bei #368, ausgelöst vom 40 MB großen `corpus-index.json.gz`. Kein Rerun, kein Aufsplitten des PR, stattdessen ein Kommentar am PR, damit der rote Haken nicht als Befund gelesen wird.

**Punkt 1 und 2 von #235 waren längst erledigt, ohne dass das Ticket es wusste.** Die 17 Tokens, die statt eines Leerzeichens die Zeichenfolge Backslash-`u0020` trugen, hat Julia am 26.08. mit `f3dcf2a86` gesplittet, die 20 kaputten Harsch-URLs sind seit PR #238 vom 29.07. repariert (gemessen: 41 Fundstellen in 25 Dateien, alle mit ASCII-Tilde). Ein Ticket, das drei Punkte bündelt, altert an jedem einzeln.

**Phase:** Betrieb. PRs #374, #377 und der Breve-PR; neue Tickets #375, #376, #378. #235 bleibt offen wegen der 223 Review-Fälle.

---

## 2026-08-31 – Zwei Messaufträge und ein Datenlauf, der den Index nicht anfasst

**Summary:** Drei Tickets in einer Session. #369 bekam nach dem Merge seinen ersten Kommentar überhaupt, #255 die von KZW bestellte Messung samt Skript (PR #380), #370 Punkt 1 den Datenlauf: 46.890 WZB-Tokens haben den Variantentyp bekommen, den das Korpus für dieselbe Schreibung schon übt. Beide PRs schließen kein Ticket, und das ist der Normalfall: der eine liefert eine Entscheidungsgrundlage, der andere erledigt einen von vier Punkten.

**Ein Datenlauf über 46.890 Tokens, der beide Indexe byte-identisch lässt.** `build-corpus-index.py` liest an `<w>` nur `@lemmaRef`, den Text und die Dokumentordnung; `@corresp` ist ihm unsichtbar. Der Neubau ergab denselben sha256 bei 42.228.352 Bytes. Der Authority-Index ändert sich ebenfalls nicht, obwohl `variants.xml` sich ändert: er trägt nur normalisierte, also kleingeschriebene Formen, und die beiden gekippten Schreibungen unterscheiden sich allein in der Großschreibung. Gegenprobe im rohen Index-JSON: `schafhirten` kommt einmal vor, `Schafhirten` und `Fur` kein einziges Mal. Die Routing-Tabelle in DATA-MODEL.md wirft `@corresp` mit `@lemmaRef` in eine Zeile und verlangt die volle Checkliste; sie ist damit nicht falsch, nur gröber als nötig. Die Schritte laufen, das Ergebnis ist an zwei Stellen leer.

**Der Bump stand trotzdem erst drin, und zwar gegen eine Regel, die derselbe Eintrag zitiert.** DATA-MODEL.md sagt wörtlich, man solle keinen Bump ohne Inhaltsänderung setzen, weil sonst jede Rückkehrerin ein Artefakt neu lädt, an dem sich nichts geändert hat, und kein CI-Gate das bemerkt. Der erste Commit dieses PRs setzte den Authority-Index trotzdem auf 1.9.3, mit der Begründung, `variants.xml` habe sich ja geändert. Das ist die falsche Bezugsgröße: gebumpt wird das Artefakt, und dessen einzige Änderung wäre der Bump selbst gewesen. Gefunden hat das der lokale Review, gemessen durch Vergleich beider dekomprimierter Indexe ohne das Versionsfeld. **Kein Gate hätte es gefangen**, denn `check-index-version-bump.py` prüft nur die Richtung „Inhalt geändert, Version vergessen", nicht die umgekehrte, und `data-integrity.yml` hätte den gebumpten Index anstandslos nachgebaut. Die 3,3 MB unnötiger Neuladung wären still geblieben.

**Die Vorabmessung zu #378 hat den Lauf freigegeben, und zwar mit null.** Die Sorge war, dass 46.890 neue `@corresp` neue first-wins-Kollisionen erzeugen, also Schreibformen, die auf das seltenere Lemma zeigen. Sie tun es nicht, und der Grund ist die Auswahlregel selbst: übernommen wurde nur, wo außerhalb der WZB genau ein Typ belegt ist, also kommt kein Typ hinzu. `extract-variants.py` meldet 0 added, 0 removed, 0 lemma assignment changed. Die Abbildung normalisierte Form auf Lemma bleibt bei 234.243 Einträgen, 0 fallen weg, 0 kommen hinzu, 0 wechseln das Lemma. **Eine Zusicherung ist erst dann etwas wert, wenn sie hätte scheitern können**, und diese hier hätte: sie hing daran, dass die Auswahlregel keine neuen Typen prägt, und genau das war zu prüfen und nicht vorauszusetzen.

**Zwei Formen kippen doch, und beide sind ein Gleichstand, kein Überstimmen.** `type_68232` geht von `fur` auf `Fur`, `type_276606` von `schafhirten` auf `Schafhirten`. Die Stimmverhältnisse sind 2:2 und 1:1: die WZB bringt keine Mehrheit, sie stellt einen Gleichstand her, und der alphabetische Tiebreak in `extract-variants.py` sortiert Großbuchstaben vor Kleinbuchstaben. Auf die Lemma-Auflösung wirkt das nicht, weil `normalize_mhg` kleinschreibt. **Sichtbar wird die Änderung überhaupt nur in `variants.xml` selbst**, und diese Zeile stand zuerst falsch hier: sie behauptete, die Rohform sei im Lemma-Explorer zu sehen. Das ist sie nicht. `build-authority-index.py` legt ausschließlich `normalize_mhg(variant)` ab, kennt die Rohform also gar nicht, und `renderVariants` in `lemma/lemma-page.js` invertiert dieselbe Map und zeigt damit ebenfalls die normalisierten Schlüssel. Gefunden hat das der CI-Bot in einem Lauf, der danach am Turn-Limit abbrach. Ob ein satzinitiales `Fur` überhaupt eine eigene orthographische Variante ist, ist eine redaktionelle Frage und nicht in diesem PR zu entscheiden; hier steht sie als gemessener Nebeneffekt.

**Die Zählweise eines Tickets gehört rekonstruiert, bevor man seine Zahlen für gedriftet hält.** #370 nennt 52.097 Tokens in 1.685 Paaren, gemessen wurden 52.163 in 1.733. Die naheliegende Deutung, das Ticket sei veraltet, war halb richtig und hätte zur falschen Korrektur geführt. Erst schreibungsgetreu gezählt ergaben sich 1.886 Paare, also noch weiter weg; mit Kleinschreibung als Schlüssel stimmten die Tokenzahlen exakt. Die Gegenprobe am WZB-Stand vor `c0e8dee80` lieferte dann genau 52.097 und 1.685. Beide Zahlensätze sind richtig, sie messen verschiedene Stände mit derselben Vorschrift, und die Differenz sind die 66 Tokens des Breve-Batches vom selben Tag.

**Das Gate zu #370 Punkt 4 ist ein Zähler-Gate, und der Kommentar zehn Zeilen darüber warnt davor.** Die #152-Ratsche im selben Skript ist bewusst eine Ratsche auf der ID-Menge, weil Zähler kompensierende Drift durchlassen. Für lemmatisierte Tokens ohne `@corresp` wäre die Mengenvariante unverhältnismäßig: sie müsste Zehntausende Token-IDs committen, und anders als bei einer hängenden Referenz ist die einzelne Token-ID kein Befund, nur die Summe. Gewählt ist deshalb eine Ratsche je Sigle mit ausgeschriebener Grenze: innerhalb einer Sigle bleibt +5/-5 grün. Die Sigle ist die Granularität, auf der der Fehler real auftritt, nämlich als Ingest, der eine Phase auslässt. Belegt ist das Gate durch Mutation in beide Richtungen: fünf `@corresp` aus EKL entfernt macht es rot (2 auf 7, Exit 1), eine künstlich erhöhte Baseline erzeugt die Nachzieh-Warnung.

**Bei #255 war der Befund nicht die Verzerrung, sondern die Auszeichnung.** `<div type="parallel">` trägt zwei Bedeutungen, getrennt allein durch `@n`: einen Zeugennamen oder eine laufende Nummer. In BRW und DL1 liegen 100 Prozent der indexierten Tokens in solchen divs, ein Filter „Zeugenvarianten nicht mitzählen" löscht diese Texte also, statt sie zu entzerren. **Die `@n`-Klasse ist trotzdem nicht der Diskriminator**, und das hat erst die lokale Review gezeigt: DL2 trägt drei benannte Blöcke mit 5,2 Prozent der Tokens neben einem Basistext, dort sind sie selbst der #255-Fall. Was entscheidet, ist der Anteil, nicht der Name. Die erste Fassung des PR-Textes hatte daraus eine Allaussage gemacht.

**Zwei Kontrollzahlen haben sich im selben Skript bezahlt gemacht.** Die 0 falsch gemeldeten Reimpaare über eine Naht ist nur deshalb ein Befund und kein kaputter Lookup, weil daneben steht, dass 7,5 Prozent der Verspaare innerhalb eines Blocks reimen. Und FR3s Typ-Token-Verhältnis steigt ohne die Zeugen um 13,9 Prozent, ein gleich langer Zufallsausschnitt aus dem vollen Text erreicht aber schon 0,0977 gegen 0,1006: der größere Teil ist Längenartefakt, weil die TTR mit der Textlänge fällt. Ohne diese Spalte hätte der Bericht ein Artefakt als Entzerrung ausgewiesen.

**Die lxml-Proxy-Falle schlägt erst zu, wenn man aufräumt.** Eine Fassung des Messskripts nahm `id(el)` als Schlüssel für die Blöcke und zählte für FR3 die richtigen 36 divs, solange sie das Element nebenbei noch in einem Feld festhielt. Nachdem dieses Feld als überflüssig entfernt war, wurden daraus 16. Regel 10 des Playbooks steht seit Langem da; was sie nicht sagt, ist dass eine Aufräumänderung den Fehler scharf machen kann, ohne ihn selbst zu enthalten.

**Zwei Sessions im selben Arbeitsbaum, und die Absprache lief über eine Versionsnummer, die am Ende niemand brauchte.** Parallel lief die Frauendienst-Titelkorrektur (#381) im Hauptbaum und hatte den Korpus-Index auf 4.2.7 gebumpt; reserviert war deshalb 4.2.8. Gebraucht wurde keine Nummer, weil dieser Lauf gar keinen Index ändert. Die Absprache war trotzdem nicht umsonst: sie hat den Konflikt sichtbar gemacht, bevor er entstand, und die Prüfung, die ihn auflöste, ist dieselbe, die den überflüssigen Bump gefunden hat. Was bleibt, ist die Regel für den Zweit-Merger bei echten Index-Änderungen: nach dem Rebase den Index **neu bauen**, nicht nur die Versionszeile anfassen, sonst passt der committete Index nicht mehr zum Korpus.

**Und die Lehre, die über den Anlass hinausgeht: Sessions im selben Repo sollten ihre Nummernabsprache nicht als Reservierung führen, sondern als Messung.** Beide Seiten haben zuerst eine Nummer verteilt und erst danach gemessen, ob eine gebraucht wird. Richtig herum ist es billiger: erst bauen und vergleichen, dann bumpen.

**Ein rot gemeldeter CI-Review kann vier Befunde tragen, und alle vier hielten der Nachmessung stand.** `CLAUDE.md` sagte bis heute, der Bot könne einen Daten-PR nicht verarbeiten; belegt war das an #368, wo die Plattform `changedFiles: 0` meldete und er ohne einen einzigen abgehakten Punkt starb. Auf #382 war der Diff sehr wohl berechnet, alle zehn Einträge standen im Prompt, die Checkliste war vollständig abgehakt, und vier Befunde standen da. **Und der Lauf ist gar nicht gescheitert:** im Log steht `subtype: success` und `is_error: false`, die Action hat nur den Haken rot gemacht, weil das Review 56 Turns gegen ein konfiguriertes Limit von 50 gebraucht hatte. Der rote Haken kam also nicht vom Bot, sondern aus einer Zahl in unserer eigenen Workflow-Datei. Seit `6fbf7e002` steht sie auf 100.

**„Verworfen" wäre trotzdem das falsche Wort, und das ist der Unterschied, an dem #377 hängt.** Die erste Fassung dieses Eintrags schrieb, die Action habe ein fertiges Review verworfen. Sie verwirft nur die grüne Bewertung. Der Kommentar wird rund anderthalb Minuten nach dem Start gepostet und überlebt den Fehlschlag um zehn Minuten: bei #377 um 09:10:53 bei einem Lauf, der 09:20:37 rot wurde, bei #382 um 13:10:42 gegen 13:19:28. Es geht nichts verloren, es sieht nur nach Verlust aus, und genau dieser Anschein hat bei #377 gereicht, damit niemand nachliest. Ein Satz, der in einem Absatz über „lies den Kommentar" behauptet, das Review sei weg, arbeitet gegen seinen eigenen Zweck.

**Eine Konfigurationslösung gibt es nicht, das ist geprüft.** Im gepinnten `v1` wirft `base-action/src/run-claude-sdk.ts` unbedingt, sobald ein `success` über dem Budget liegt; kein Input steuert das. Die beiden denkbaren Auswege sind teurer als das Problem: `--max-turns` ganz weglassen nähme die Kostenbremse bei einem Bot, der auf jedes `synchronize` läuft, und `continue-on-error` machte auch echte Abbrüche wie #379 grün, womit der Haken gar nichts mehr sagte. Die Zahl 100 bleibt, und die Suche nach einem Schalter kann sich die nächste Session sparen.

**Die naheliegende Erklärung dafür war trotzdem falsch, und das ist der lehrreichere Teil.** Ich hatte geschlossen, entscheidend sei, ob die Plattform den Diff berechnet hat. Die Gegenprobe an #379 widerlegt das: dort standen 16 Dateizeilen im Prompt, der Diff war also da, und der Lauf endete gleichwohl in einem echten `error_max_turns` mit `is_error: true`, einem von vier abgehakten Punkten und null Befunden. Der berechnete Diff ist notwendig, nicht hinreichend, und woran ein Lauf scheitert, ist von außen nicht vorherzusagen. Übrig bleibt die schmalere und haltbarere Regel: **ein roter Haken auf einem Daten-PR ist kein Befund, aber auch kein Beweis, dass keiner drinsteht.** Der Kommentar wird gelesen, immer.

**Und diese Regel hat heute schon zwei Befunde gekostet, bevor jemand sie aufgeschrieben hatte.** Die Nachfrage nach einer Zahl, die ich nicht reproduzieren konnte, hat #377 als vierten Fall aufgedeckt, und der ist der teuerste: 34 Dateien im Prompt, `subtype: success`, 59 von 50 Turns, fünf von fünf Punkten abgehakt und **zwei echte, sauber gemessene Befunde** im Kommentar. Neun Minuten nach dem Bot-Kommentar wurde der rote Haken als Plattformgrenze abgetan und der PR gemergt, ohne dass jemand ihn geöffnet hatte. Beide Befunde stehen unverändert auf `main`: eine Siglen-Ableitung per `rsplit("_", 2)`, die an WZB-Token-IDs mit drei Unterstrichen scheitert und dann meldet, das Token sei nicht im Korpus, und eine Idempotenz-Lücke in der Platzhalterprüfung von `revisiondesc-homograph.py`. Sie zu beheben ist nicht Sache dieser Session; die Meldung an chsteiner läuft über die Session, die sie gefunden hat.

**Die Ursache der Fehldiagnose war ein Feld, dem beide Seiten geglaubt haben.** `gh api .../pulls/377 -q .changed_files` liefert 0, `gh pr view 377 --json files` liefert 34. Für #368, #379 und #382 stimmen beide Endpunkte überein, für #377 nicht, und genau auf dieser falschen 0 stand die Abtun-Begründung. Zwei Sessions haben unabhängig voneinander dasselbe Feld als Beleg genommen. Wer künftig behauptet, GitHub habe den Diff nicht berechnet, liest den `<changed_files>`-Block im Job-Log oder nimmt `--json files`.

**Und der Beleg, auf den ich die erste Fassung gestützt hatte, war selbst ein Messfehler.** Ich hatte behauptet, auf #382 sei derselbe leere `<changed_files>`-Block gelaufen wie auf #368. Das kam daher, dass ich das Run-Log durch ein `grep` mit einem Suchmuster gelesen hatte, das die Zeilen zwischen den beiden Tags gar nicht treffen konnte: übrig blieben die Öffnungs- und die Schlusszeile direkt untereinander, und das sah aus wie ein leerer Block. Ein Artefakt der eigenen Filterung, gelesen als Befund über die Welt. Gefunden hat es die lokale Review, die die Zahl schlicht direkt abgefragt hat (`gh pr view 382 --json changedFiles` → 10). Die Lehre für gefilterte Logs: was ein Filter nicht zeigt, ist nicht abwesend, und eine Abwesenheitsbehauptung braucht eine Abfrage, die Anwesenheit zeigen könnte.

**Der teuerste der vier Befunde war einer, in den ich in derselben Session selbst hineingelaufen war.** `--update-baseline` schrieb beide Ratschen des Cross-Ref-Audits, die #152-ID-Menge und die neue #370-Zählung, ohne Wahlmöglichkeit. Genau das ist mir beim ersten Anlauf passiert: der Aufruf hat nebenbei das Datum in `lexicon-baseline.json` neu geschrieben, obwohl die ID-Menge unverändert war, und ich habe die Datei per `git checkout origin/main --` zurückgeholt, weil sie sonst eine Prüfung behauptet hätte, die nicht stattgefunden hat. Erst der Bot hat daraus den allgemeinen Fall gemacht: die neue Warnung schickt Sessions künftig **routinemäßig** zu diesem Kommando, und ein Ingest, der nebenbei neue dangling lexicon-IDs erzeugt, bekäme sie damit still in die Baseline. Der Flag nimmt jetzt einen Bereich (`=lexicon`, `=corresp`, nackt weiterhin beides), und die beiden Warntexte nennen je den ihren. Die Lehre ist nicht „Flags aufteilen", sondern: **ein Werkzeug, das zwei Ratschen bedient, darf nicht einen Aufruf haben, wenn die beiden Anlässe verschieden autorisiert sind.** Die #152-Ratsche zieht man nach einer KZW-Entscheidung nach, die #370-Ratsche mechanisch.

**Eine gekappte Liste ohne Kappungsmarke ist eine falsche Zahl, nicht nur eine unvollständige.** `zuordnung.csv` nannte je Zeile bis zu acht Belegsigel außerhalb der WZB, hart abgeschnitten und ohne Hinweis darauf. 92,5 Prozent der Zeilen waren gekappt. Der Bot hat den Fall an `hebt`/`type_9058` gezeigt: acht Sigel gelesen, tatsächlich sind es 82; die häufigste Zeile steht bei 644. Ausgerechnet diese Spalte war im PR-Text als das benannt, was sich nachträglich nicht mehr rekonstruieren ließe. Jetzt trägt die CSV `sigel_anzahl` neben `sigel_probe`, die Kappungsgrenze steht als Konstante im Skript.

**Und beim Nachziehen fiel auf, dass das Laufskript gar nicht im Repo war.** Die vier WZB-Vorgängerläufe liegen alle unter `scripts/ingest/wzb/`; dieser lief aus dem Scratchpad. Ein Provenienz-Log, dessen Erzeuger nicht mitkommt, ist genau so weit reproduzierbar wie das Vertrauen in die Zahlen darin. Beide Skripte sind jetzt als `wzb-corresp-apply.py` und `wzb-corresp-log.py` committet, mit `Path(__file__).resolve().parents[3]` statt des Worktree-Pfads, und das Log ist aus der committeten Fassung neu erzeugt worden: 46.890, 484, 5.273, unverändert.

**Phase:** Betrieb. PR #380 (#255, Messung) und der #370-PR; kein Ticket geschlossen. #370 Punkt 2 (5.273 Tokens, die neue Typen bräuchten) bleibt kuratorisch offen.

---

## 2026-08-14 – #59: die Erklärung durfte nicht vor den Daten kommen

**Summary:** Lindas Umstellung vom 11.08. auf acht Instanztypen mit sechs Markern ist im Naming-Explorer umgesetzt; die Ansicht kannte bis dahin nur `#` und eckige Klammern und erklärte beide als dasselbe. Gemergt als PR #365, zusammen mit Lindas Datenstand v0.2.1-beta (Quell-Commit `4766065c`, 10.502 Records). Nachtrag vom 18.08., rekonstruiert aus dem PR-Text und dem Bericht an Linda in #59; die Session selbst hatte keinen Journal-Eintrag hinterlassen.

**Der Defekt in einer Zahl:** die alte Regex `/^[#[]/` erkannte 103 von 240 markierten Nennungen. Sie kannte `<`, `{`, `°` und ` & ` nicht, und ihr `^`-Anker scheiterte an Mischformen wie `Medeas <meisterîn>`.

**Der Zuschnitt hat sich unter der Messung umgedreht.** Geplant war der PR ohne Datenupdate, die Erklärung sollte vor den Daten kommen. Gemessen trug der ausgelieferte Index aber 15 Gitter-Werte, von denen am neuen Quellstand genau einer übrig ist (`#David`; im Rolandslied fällt `#` von 69 Nennungen auf 3). Die neue Legende beschriftet jeden Gitter-Wert mit „Zitiert", ohne Datenupdate hätte sie also bei 14 von 15 Werten eine falsche Typangabe getragen. Der umgekehrte Fehler war der schlimmere, und er war übersehen. Mit demselben Schnitt erledigte sich der veraltete DOI: statt einer Pflegenotiz hält jetzt `pruefe_zitation` Version und DOI gegen die `CITATION.cff` des gebauten Quellstands.

**Drei Guards im Build, einer bewusst asymmetrisch.** `pruefe_instanztypen` bricht nur, wenn die Quelle einen Typ kennt, den wir nicht kennen, oder ein beidseitig vorhandener Typ verschiedene Marker trägt: ein alter Quellstand kann die Typologie nicht kennen, und das Freshness-Gate baut genau solche. `pruefe_frontend_paritaet` liest `MARKER_KLASSEN` aus dem JS und verlangt für jeden bekannten Marker eine Klasse. In der Legende teilen sich Rollenfigur und Kollektivmitglied das Zeichen `<…>` und stehen als eine Zeile: welcher von beiden gemeint ist, lässt sich am Zeichen nicht entscheiden, und eine Zuordnung wäre eine Behauptung ohne Deckung.

**Das Review fand zwei grüne Prüfungen ohne Haltekraft.** Vier Runden `fable-reviewer` vor den Pushes (Freshness-Blocker; ein Guard, den jeder HTTP-Fehler außer 404 still abschaltete; eine zweite Kopie der Zitation), danach der CI-Bot: eine Assertion auf `#resultsContainer`, die das Auswahlfeld mit einschloss, und `BEKANNTE_ANFANGSMARKER` als vierte, ungegatete Kopie der Typologie, jetzt abgeleitet statt gepflegt. Der Bestandstest hatte nur die Überschrift geprüft und lief deshalb vor wie nach dem Umbau grün.

**Phase:** Betrieb. 310 Tests grün, Freshness-Gate grün gegen den neuen Pin. #59 bleibt offen auf `wait:linda`: Abnahme nach Deploy steht aus, dazu drei offene Fragen an Linda (Tag auf `master`, die drei Iwein-Records, Priorität des Kollokations-Tooltips).

---

## 2026-09-01 – Der Lauf, der seriell blieb, weil die abgeleitete Schicht global ist

Geplant war ein Spurenlauf mit mehreren autonomen Sessions. Geworden ist ein serieller Wellenlauf, der nach der ersten Sachwelle pausiert wurde. Dieser Eintrag ist der der **Koordination**; der Lauf selbst hat seinen Zwischenstand als Kommentar auf #44.

**Der Zuschnitt scheitert nicht an den Dateien, sondern am Datenmodell.** Der Data-Change-Lifecycle verlangt nach jeder Änderung in `tei/` oder `authority-files/` einen Neubau von `variants.xml`, beiden Indexen und der API: zwei Binärdateien (42,2 MB und 3,3 MB) plus 2.742 JSON, und sie sind eine Funktion des **ganzen** Korpus. Zwei gleichzeitige Datenspuren kollidieren dort nicht zufällig, sondern zwangsläufig, weil jede ihren Index auf einem Baum baut, dem die Korpusänderung der anderen fehlt. Ein Dateischnitt, das übliche Mittel gegen Kollisionen, kann das nicht auflösen. Das ist der Grund, warum dieses Projekt seriell arbeitet, und er gilt unabhängig davon, wie viele Sessions verfügbar wären.

**Von fünf autonom antastbaren Tickets blieben nach Messung zwei startbare.** Alle fünf tragen `auto:checkin`. #259 hatte seine Datengrundlage nicht auf der Maschine (Trierer Dump in KZWs Drive; nach dem Nachliefern 22 XML, 27.106.707 Bytes unter `temp/`, byteweise identisch mit dem Drive-Bestand). #123 ist ein Nice-to-have mit null Kommentaren seit der Anlage. #216 hängt an seinem eigenen Punkt 3. Und #28, seit dem 10.08. als „das einzige `large`, das auf keine Entscheidung wartet" geführt, wartet doch: Phase 1 hat drei Gleise, und zwei davon kosten eine Budget- oder eine Datenentscheidung. **Ein Ticket kann entblockt sein und trotzdem an seiner ersten Handlung hängen.**

**Der Freeze, den ein Parallelbetrieb bräuchte, hätte sich selbst blockiert.** `check-index-versions.py` gatet fünf Stellen, und eine davon ist der Versionsklammerzusatz in `docs/INDEX.md`. Jede Datenspur muss ihn anfassen. Eine Einfrierliste, die `docs/INDEX.md` pauschal sperrt, sperrt damit genau die Arbeit, die sie schützen soll. Die Inbox dafür ist jetzt #385, mit benannter Ausnahme, Vierfelder-Format, Ersetzungsregel und der Festlegung, dass allein chsteiner den Freeze aufhebt und dabei die Reichweite nennt. **#44 taugt dafür nicht:** sein Body ist zwischen den `MATRIX`-Markern generiert, `--check` ist ein Gate, und am 31.08. ist es nach einem reinen `gh issue edit --body-file`-Roundtrip rot geworden, ohne dass am generierten Block etwas geändert war.

**Kickoff-Wortlaute werden ab jetzt getrackt** (`docs/playbooks/kickoffs/`, `5aa3a8df3`). Bis dahin überlebte vom Auftragstext nur die Zusammenfassung in §6 des Masterplans, und die wird bei jedem Lauf überschrieben. Der Auftrag ist aber der einzige Beleg dafür, was eine Session tun durfte. Jede Datei dort trägt als erste Zeile den Vermerk, dass sie ein Protokoll ist: der kopierte Betriebsvertrag darin altert ab dem Tag des Abschickens, und eine Kopie im Repositorium, die sich für das Original hält, ist genau die Driftquelle, wegen der `BETRIEBSVERTRAG.md` herausgelöst wurde.

**Eine Stunde Stillstand an einer Freigabe, die keine Regel abstellen kann.** Der Lauf hat den Worktree per `git worktree add` neben dem Repositorium angelegt und wollte dann mit `EnterWorktree` hineinwechseln. Das verlangt seit v2.1.206 eine interaktive Bestätigung, sobald das Ziel außerhalb von `.claude/worktrees/` liegt, und die Session stand, bis jemand hinsah. Die naheliegende Reaktion, eine `allow`-Regel zu setzen, geht ins Leere: die Dokumentation sagt ausdrücklich, dass weder eine `EnterWorktree`-Regel noch „don't ask again" diesen Prompt unterdrückt, nur `bypassPermissions`. **Ein Allow wäre hier ein wirkungsloser Allow gewesen**, also die schlechtere Variante von gar keiner Regel. Der Ausweg ist, `EnterWorktree` nicht zu brauchen: `claude --bg --name X --worktree X`. Die 260-Zeichen-Begründung für den Worktree neben dem Repositorium bindet hier nicht (gemessen: 180 gegen 260), aber die Zahl gehört von dem nachgemessen, der die Umstellung schreibt.

**`.claude/agent-memory/` wird getrackt statt ignoriert** (`b306d9f22`). Der naheliegende Weg wäre das Ignorieren gewesen: `.claude/` war bei 1001 Commits und fünf Autoren kein geteilter Ort. Entscheidung chsteiner, Begründung Wissenserhalt. Der Haken, den dieses Projekt dabei hat, steht im README daneben: der `fable-reviewer` schreibt in das Verzeichnis **des Worktrees**, und der Abbau ist damit die Stelle, an der das Gelernte verlorengeht.

**Pausiert wurde am einzigen kostenlosen Schnitt.** Das Fable-Kontingent geht zur Neige, und `fable-reviewer` ist Pflicht vor dem ersten Push jedes PR-Zweigs. Welle 1 war die einzige Welle ohne PR. Ein Schnitt dort verbraucht keine Review-Runde und liefert trotzdem ein Ergebnis; eine Welle später hätte er einen halb reviewten PR hinterlassen. Ergebnis von Welle 1: die *vrouwe*-Disambiguierung vor *minne* ist ein Anhängsel und kein eigener Lauf (155 Stellen, 150 mechanisch, null neue Lemmata). Der Zweig `claude/28-gleis1-begriffssystem` steht ungereviewt und ohne PR auf `origin`, ausnahmsweise freigegeben, damit die Arbeit über die Pause nicht nur lokal liegt.

**Rot nach der Zählregel vom 01.09.: „an allen vier Stellen konsistent" statt fünf, obwohl die richtige Zahl im Kontext stand.** Die Welle-0-Meldung der Spur-Session gab das Ergebnis von `check-index-versions.py` mit vier Stellen an. Das Gate prüft fünf Dateien (`build-corpus-index.py`, `build-authority-index.py`, `assets/js/lib/corpus-loader.js`, `docs/TEI-MODEL.md`, `docs/INDEX.md`, Zeilen 46 bis 50). Die Fehlerquelle ist die Konsolenausgabe: sie listet **je Index vier Rollen** („build-skript, loader, TEI-MODEL.md, INDEX.md"), weil der Loader beide Versionen trägt, und diese Vier wurde für die Dateizahl gehalten. Die dokumentierte Lehre dazu lag der Session von Anfang an vor und hat nicht gegriffen; gefunden hat es die Koordination, nicht die Session. Die Zeile steht hier auf Bitte der Spur-Session, die auf `main` nicht committen darf. **Die Lehre über den Anlass hinaus: eine Ausgabe, die Rollen zählt, ist keine Aussage über Dateien**, und ein Skript, das gegen eine gemerkte Zahl läuft, ist die Gelegenheit, die Zahl zu prüfen, nicht der Beleg dafür.

**Nachtrag am selben Tag:** die zwei Playbook-Aufträge, die für die Meta-Welle des pausierten Laufs übrig waren, sind mit `2adc52fc5` erledigt, direkt auf `main` ohne PR und ohne Review, weil Doku plus eine `.gitignore`-Zeile darunter fallen. Die oben eingeforderte 260-Zeichen-Messung ist damit nachgeholt und steht in Regel 29: Repo-Wurzel 64, Worktree unter `.claude/worktrees/` 88, tiefster `node_modules`-Pfad relativ 92, längster getrackter Pfad 74.

**Die Stoppbedingung von Welle 3 wurde vorgezogen, weil eine Messung kein Fable kostet.** Ergebnis: #259 läuft, aber sein Prüfdatensatz ist ein anderer als der Body annahm. Nicht die 35.366 Einträge sind es, sondern die 8.610 Paare Schreibform → Lemma auf der Sublemma-Ebene, und die Befundliste entsteht aus **477 Fällen**, in denen unsere Lemmaliste und das Findebuch dieselbe Form verschieden einordnen. Drei Zahlen im Body halten der Messung nicht stand, darunter „100 % mit Querverweis": gemessen tragen 11.394 von 34.828 Lemma-Formen gar kein `<ref target>`, also 32,7 %, und genau diese Lückenlosigkeit war die Begründung, den Dump überhaupt anzufassen. Die im Body genannte Normalisierungsfalle ist an der Lexer-Lemmaliste gemessen und auf das Findebuch übertragen worden, ohne dort geprüft zu sein: `ʒ` kommt in den 32.565 Findebuch-Lemmaformen **null** mal vor, die Quote bewegt sich um 3,1 Punkte statt um 27. Body und `effort:`-Label sind richtiggestellt, die Messvorschrift steht im Kommentar. **Die Lehre ist die alte in neuer Kleidung:** eine Zahl, die aus einer Nachbarquelle stammt, ist in der neuen Quelle ungemessen, auch wenn beide vom selben Anbieter kommen.

**Auch Welle 2 wurde vorgezogen, und ihr Befund hat eine Grenze statt eines Urteils.** Gleis 1 von #28 liefert über die 17 Sprachkonzepte unter `concept_23123000` genau 6.219 Lemmata und 225.505 Korpusbelege. Die Menge ist brauchbar, aber nicht so, wie man sie zuerst benutzen würde: die zehn belegstärksten Treffer tragen 53,0 % der Tokenmenge, und der größte ist `niht` mit 81.088 Belegen unter „Lateinisch". Der Grund steht im Baum, nicht in den Daten: `concept_23123000` hängt unter „Kommunikation/Sprache" und ist ein **Bedeutungsfeld**, das in der Praxis auch für Herkunft benutzt wird (`bischof` < *episcopus* trägt dasselbe Konzept). Ein Filter über die Konzeptdichte scheidet aus, nur 4 der 6.219 Lemmata tragen ausschließlich Sprachkonzepte. Was trägt, ist die Belegklasse: über 501 Belegen liegen 25 Lemmata mit 77,5 % der Nicht-Namen-Tokens, gemischt aus Rauschen und echten Lehnwörtern, also von Hand durchzusehen; darunter liegen 3.338 Lemmata mit 35.785 Belegen, und die Stichprobe ist dort über alle Klassen sauber. **Aus 43.879 Lemmata werden damit 3.338 plus eine Viertelstunde Handarbeit**, und das ist der eigentliche Ertrag von Gleis 1: nicht die Antwort, sondern der Faktor 13 auf die Frage.

**Am Abend desselben Tages wieder aufgenommen**, weil das Fable-Kontingent zurück war. Die Spur heißt `mhdbdb-wellen-2345` und ist die erste, die nach der neuen Regel 29 mit `--worktree` startet. Was das Flag kostet, ist damit gemessen und in Regel 29 und 30 eingearbeitet (`8a7ea2116`): der Baum ist gesperrt und `git worktree remove` verweigert ihn, der Sperrgrund wird dabei umgeschrieben statt abgebaut (`locked initializing`, dann `locked claude session <name> (pid <n>)`), der Zweig heißt `worktree-<name>` und bleibt als Leiche liegen. Der dritte Punkt ist der gefährlichste, weil er nach einem echten Fehler aussieht: **`claude agents --json` führt die Session mit `cwd` auf dem Hauptbaum, obwohl `pwd` in ihr den Worktree zeigt.** Das Feld gibt das Verzeichnis des startenden Prozesses wieder. Das globale Operator-Skill weist an, eine so angezeigte Spur abzuräumen und neu zu starten; wer dem folgt, zerstört eine korrekt stehende Session mit dem guten Gewissen, eine dokumentierte Prüfung gemacht zu haben. Rückgemeldet als Kommentar an `claude-code-setup` #6.

**Die drei offenen Menschenfragen sind beantwortet**, KZW am 01.09. auf #216: die fünf `fro-minne`-Belege sind jedesmal Frau Minne, `rend="upper_case_first_letter"` markiert die Edition und nicht zwingend die Personifikation (im Verbund Frau plus Minne aber ein brauchbares Indiz), zu einem Fall will er den Verskontext, und die kleine Menge soll vorgezogen werden. **Die zweite Hälfte des letzten Punktes ist die, die leicht verlorengeht:** „andere vrouwen in eigenes Issue" wird umgesetzt, „kleine Menge vorziehen" betrifft 155 Belege, ist eine Korpusänderung und läuft in keiner der vier Wellen mit. Sie braucht eine Terminentscheidung und steht dafür ausdrücklich im Statuskommentar auf #216.

**Rot, und zwar auf der Koordinationsseite:** der Freeze aus #385 tritt laut Ticket **mit dem Kickoff** in Kraft, nicht mit seiner Eintragung. Der Kickoff ging um kurz vor 22 Uhr hinaus, danach hat die Koordination mit `8a7ea2116` `docs/playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md` geändert, eine Datei, die auf der Einfrierliste steht. Die Lehre, die nicht gegriffen hat, ist #385 selbst: sie war nur nicht gelesen, weil der Freeze zum Zeitpunkt des Kickoffs noch nicht eingetragen war. Der Commit bleibt stehen, weil er einen Befund der laufenden Spur einarbeitet und ihr Abbau ohne ihn in die Sperre läuft; die Spur wurde in derselben Stunde mit dem Hash unterrichtet, was den eigentlichen Schaden repariert (unbemerkt geänderte Regeln). Die Konsequenz für den nächsten Lauf ist keine schärfere Formulierung, sondern eine Reihenfolge: **der Freeze wird eingetragen, bevor der Kickoff hinausgeht.** Offengelegt im Body von #385.

**Rot, zum zweiten Mal an einem Abend und wieder auf der Koordinationsseite: die Welle-2-Vorabmessung war falsch.** Die transitive Hülle unter `concept_23123000` sammelte nur die Kinder und nicht die Wurzel selbst (`gefunden, stapel = {}, [WURZEL]`, die Wurzel geht auf den Stapel und nie in die Ergebnismenge). Richtig sind **6.246 Lemmata** in **18** Kategorien mit **227.652** Belegen, nicht 6.219 in 17 mit 225.505; die Anteile 14,23 % und 3,02 % statt 14,17 % und 2,99 %. Gefunden hat es der `fable-reviewer` in Runde 1 auf dem Welle-2-PR, nachgemessen hat es die Spur, und danach die Koordination unabhängig ein drittes Mal. **Die Zahlendifferenz von 0,43 % ist das Unwichtigste daran.** Unter den 27 fehlenden Lemmata stehen `welsch`, `enwelsch`, `rotwalsch`, `englisch`, `tolmetze`, `tolken`, `vertolken`, `antvristen`, `diuten`, `diutunge`, `tiutschen`, `zediuten`, `ûzlegen`, `ûzleger`, `ûzlegerin`, `ûzlegunge`, `zunge`, `gezünge`: das Vokabular, mit dem der Text über Fremdsprachigkeit **spricht**, statt sie zu belegen. Die Wurzel heißt „Einzelsprachen" und trägt genau die Wörter, die keiner einzelnen Sprache zuzuordnen sind. In einer Messung zu #28 fehlte damit die Klasse, die das Phänomen benennt. **Die Spur hat diese Charakterisierung zu Recht eingeschränkt: sie trifft auf 24 der 27 zu**, sauber geteilt in Sprachbezeichnungen (8), Übersetzen und Auslegen (14) sowie Sprache als Organ (2). Die drei übrigen sind `gebrechen`, `engebrechen`, `gebrechenhaft`, und sie sind **kein Rauschen**, obwohl sie zunächst so aussehen: anders als `niht`, das sein Sprachkonzept am einzigen Sense trägt, tragen diese drei es am vierten von vier, und zwar alle in derselben Kombination aus „Mündliche Kommunikation" und „Einzelsprachen", während ihre Hauptbedeutung auf „Mangel/Bedürfnis/Misserfolg" sitzt. Das sieht nach gebrochener Sprachbeherrschung aus, also nach `radebrechen`, und wäre dann mit 341 Belegen in 101 Texten der belegstärkste Zugang, den Gleis 1 überhaupt hat. Damit ist es eine Frage an KZW.

**Rot, zum dritten Mal an einem Abend und wieder die Koordination: „das Korpus kann Senses nicht auflösen" war falsch.** Der Satz stand hier und im #28-Kommentar, und er ist in zwei Minuten widerlegbar gewesen. Neben `@lemmaRef` trägt jedes annotierte `<w>` ein `@ana="lexicon.xml#lemma_{id}_sense_{id}"`, das genau auf den Sense zeigt, in **667 von 667** Dateien, dokumentiert in TEI-MODEL.md §4.1 samt Migrationsgeschichte (Phase B1, `@meaningRef` zu `@ana`, rund 5,9 Millionen Vorkommen). Zustande gekommen ist der Fehler dadurch, dass die Sense-Datensätze in `api/lemmata/index.json` tatsächlich nur `conceptIds` führen und daraus auf das Korpus geschlossen wurde, ohne das Dokument aufzuschlagen, das davon handelt. Die Lehre, die nicht gegriffen hat, ist die schlichteste im Bestand: **eine Abwesenheitsbehauptung braucht eine Abfrage, die Anwesenheit zeigen könnte.** Gefunden hat es die Spur, und sie hat gleich die Sachfrage mitentschieden: von den 40 sense-disambiguierten Tokens der `gebrechen`-Familie zeigt genau eines auf den fraglichen Sense, `JT_30921000_5`, und sein Kontext lautet „secureiz wol kunde hie beidenthalp gebrechen / die rede von ir munde". Das ist das Abbrechen der Rede, nicht gebrochene Sprachbeherrschung; `radebrechen` ist vom Tisch, und die verbliebene Frage an KZW ist enger: warum trägt ein Sense für das Unterbrechen der Rede das Konzept „Einzelsprachen"? **Der nützlichere Teil des Befunds gilt Gleis 1 insgesamt:** 92,4 % der Kandidaten-Tokens tragen ein `@ana`, aber es trennt fast nie, weil 6.872 der 6.996 Senses selbst ein Sprachkonzept haben. Genau 430 Tokens zeigen auf einen Sense ohne eines, und das sind die Stellen, an denen der annotierte Bestand einer Zuordnung widerspricht: das schärfste maschinelle Ausschlusskriterium, das Gleis 1 hat (Messung der Spur, hier nicht nachgemessen). Die Lehre, die nicht gegriffen hat, steht im Auftrag desselben Laufs, §9: ein Testlauf, dessen Grundgesamtheit man nicht kennt, beweist nichts, und plausible falsche Zahlen sind der Regelfall dieser Sorte. Konkret gegen den Wiederholungsfall: **eine Hülle wird gegen ihre eigene Wurzel geprüft, bevor man ihr glaubt**, das kostet zwei Zeilen. Richtigstellung mit Messvorschrift als Kommentar auf #28; die Zahlen im abgeschickten Auftrag bleiben stehen und bekommen eine Fußnote, beantragt in #385, weil `docs/playbooks/**` eingefroren ist.

**Rot, zum vierten Mal, und die Welle-3-Vorabmessung war an zwei Stellen falsch.** Die erste ist ein Selbstwiderspruch innerhalb eines Absatzes: zum Trierer Zeichensatz steht dort erst die Messung „von 34,3 % auf 37,4 %" und zwei Sätze später das Fazit, die Zusatzregeln „kosten nur nichts und retten hier auch nichts". Mit beiden Schaltungen des Prüfskripts gemessen heben sie die Paare mit bekanntem Findebuch-Lemma von 5.081 auf 5.494 und die Befundmenge von 424 auf 465, also um 41 Fälle. Die zweite wiegt schwerer, weil sie den Zuschnitt des Tickets betrifft: die 477 Fälle waren als die Menge beschrieben, in der „genau dort unsere dreistufige Auflösung danebengreifen" kann. Dort kann sie es nicht. Das Auswahlkriterium, die Schreibform ist bei uns selbst ein Lemma, ist genau die Bedingung, unter der Stufe 1 trifft; die Menge löst deshalb zu 100 % auf Stufe 1 auf (gemessen 465 von 465), und die Fehlerklasse aus #224, wegen der #259 überhaupt existiert, kann in ihr gar nicht auftreten. Gefunden hat beides die Spur beim Bau des Skripts, nachgemessen die Koordination mit dem unveränderten Skript aus `f3a575c77` gegen denselben Dump, außerhalb des Repositoriums ausgeführt.

**Für den Zähler ist die Herkunft wichtiger als die Zahl.** Beide Fehler stammen aus derselben Vorabmessungscharge vom 01.09. wie die rote Zeile zwei und drei, also aus der Zeit **vor** der Lehre, die aus ihnen gezogen wurde. Sie sind ein weiterer Fund im selben Bestand und kein neuer Verstoß gegen eine schon stehende Regel; deshalb stehen sie hier als eine Zeile. Was sie belegen, ist die Wirksamkeitsfrage: **beide vorab vermessenen Wellen trugen einen Fehler, den erst die Spur beim Neubau fand**, und in beiden Fällen wäre er konserviert worden, wenn die Spur der Zahl gefolgt wäre, statt sie neu zu erarbeiten. Genau das war der Zweck der Vorwegnahme. Der strukturelle Grund steht in der roten Zeile drei: Operatorarbeit geht durch keinen Review, die Arbeit der Spur durch vier Runden. Richtigstellung mit Messvorschrift als Kommentar auf #259, der Body ist an beiden Stellen nachgezogen und der Vorabmessungs-Kommentar trägt eine Überholt-Notiz; die Fußnote im eingefrorenen Auftragstext ist über #385 beantragt.

**Rot, zum fünften Mal, und dies ist der erste echte Wiederholungsfall des Laufs: die Lehre stand, sie war drei Stunden alt, und sie war meine eigene.** Am Vormittag des 02.09. habe ich im Setup-Repositorium den Satz veröffentlicht, das Ergebnis einer Vorabmessung gehe nicht in Ticketkommentare oder in die Chronik, bevor eine geprüfte Fassung existiert. Keine drei Stunden später habe ich aus einer Vorab-Meldung der Spur binnen einer Stunde einen publizierten Ticketkommentar, zwei Body-Änderungen und einen Journalcommit gemacht, und zwar an dem Kommentar, der einen früheren Fehler derselben Sorte richtigstellt. Die Meldung kam aus Meldepunkt 2 **vor** der Reviewrunde, was ihr Zweck ist; die Runde fand danach einen Klasse-A-Defekt im Prüfskript, und damit waren alle Beträge überholt, die ich publiziert hatte. Der Defekt: `itertext()` auch auf `<form type="sublemma">`, wo **2.705 der 8.610 Formen ausschließlich ein Wortartkürzel und gar keine Schreibform tragen**. Selbst nachgemessen mit einem eigenen Skript direkt am Dump, damit die Gegenprobe den Fehler nicht erbt: 8.610 Formen, 3.462 mit `<gram>`-Kind, 2.705 nur Kürzel, 1.039 Ergebnisse mit Leerzeichen, 3.498 mit Punkt, auf die Stelle die Zahlen der Spur. **Die Richtungen beider Befunde halten** (die Trierer Regeln retten etwas, die Prüfmenge löst ausnahmslos auf Stufe 1 auf), die Beträge nicht. Richtiggestellt durch eine Notiz am eigenen Kommentar, und die Betragszahlen sind aus dem Ticket-Body wieder heraus: sie gehören in den PR, nicht in ein Ticket, das bei jeder Reviewrunde nachaltert.

**Im selben Kommentar noch ein zweiter Fall derselben Familie, gefunden von derselben Reviewrunde am Docstring der Spur und auf mich genauso zutreffend:** die Zahl 5.705 für das `ʒ` in der Lexer-Lemmaliste stand dort als Faktum. Sie ist keines. Sie stammt aus der Vorprüfung im Ticket-Body, der Body führt sie selbst unter „nicht nachprüfbar", und die Datei liegt auf dieser Maschine gar nicht (unter `temp/woerterbuchnetz2015` steht allein `FindeB`, nachgesehen). Erst mit Herkunft markiert, und **auch das war falsch**: `CLAUDE.md` Zeile 108 verlangt, was eine Aussage nicht braucht, zu **löschen statt zu belegen**. Die Zahl ist jetzt gelöscht. Der Umweg lohnt die Zeile, weil er eine Klasse benennt, die in der Zählung bisher fehlte und die aus dem Austausch mit `corema-operator` stammt: **die dekorative Zahl.** Sie steht neben einem Argument, das sie nicht braucht, und wird genau deshalb nie geprüft, denn niemand stützt sich auf sie. Wer bemerkt, dass sie nichts trägt, hat damit die Rechtfertigung, sie weiter nicht zu prüfen. Gefährlich wird sie, wenn sie fremd ist: diese hier kam aus einem Ticket-Body und trug dessen Autorität, obwohl sie dort selbst als unprüfbar markiert war. Ein Leser sieht ihr das nicht an.

**Was daraus folgt, ist wieder keine schärfere Formulierung, sondern eine Reihenfolge**, und das ist inzwischen das Muster beider Koordinationsfehler dieses Laufs. Beim Freeze war es „eintragen, bevor der Kickoff hinausgeht", hier ist es: **was im Meldepunkt vor einer Reviewrunde kommt, geht in die Listen und nirgendwo sonst; publiziert wird nach der Runde.** Eine Regel, die drei Stunden nach ihrer eigenen Formulierung gebrochen wird, hat kein Textproblem. Die Meldedisziplin der Spur bleibt davon unberührt und ausdrücklich richtig: ein Meldepunkt liegt vor dem Review, sonst ist er sinnlos. **Der Fehler war die Publikation, nicht die Meldung**, und aus demselben Grund wird der Skriptdefekt der Spur hier nicht gezählt: einen Fehler, den die erste Reviewrunde in einem PR findet, zählt der Zähler nicht, sonst zählt er Arbeit statt Wiederholung.

**Rot, zum sechsten Mal, und es ist dieselbe Bauart wie die vierte: Messung richtig, Mechanismus erfunden.** Zu einem Befund der Spur aus Welle 4 (das Verblemma `lemma_2535 grôzen` existiert, entgegen ihrer ersten Aussage) habe ich den Variantenbestand nachgemessen und dabei gesehen, dass `grozen`, `groezen` und `groesen` alle auf das Adjektiv `lemma_2534` zeigen. Die Messung stimmt. Daraus habe ich geschrieben, „Stufe 2 überschreibt eine Zuordnung, die Stufe 1 richtig hätte", und das ist frei erfunden: `docs/CONTRACTS.md` §C führt seit langem den Pseudocode mit `if results.length > 0: return results // EARLY RETURN, skip stages 2-3`. Stufe 1 bricht bei Treffer ab, ein Überschreiben kann es nicht geben. Die Spur hat es kassiert und die richtige Lage geliefert: betroffen ist allein der Ingest-Matcher, weil `wzb-breve-backfill.py` `variants.xml` direkt liest und die Stufenordnung nicht kennt. **Der Fehler saß im Werkzeug, nicht in der Auflösung**, und dieser Unterschied entscheidet, ob es ein Frontend-Bug ist oder eine Werkzeugeigenschaft. Ich hatte außerdem eine Frage an KZW daraus gebaut („Altlast oder Absicht?"), die mit falscher Prämisse hingegangen wäre; ihre Antwort darauf lautete **Homographie** (die flektierte Adjektivform *ist* der Verbinfinitiv, 1.223 Korpusbelege gegen 13), und **auch die ist nicht die Erklärung, was der CI-Bot zwei Stunden später gefunden und ich danach selbst nachgemessen habe.** Sie gilt für die Normalform `grozen`; der fragliche WZB-Token ist `grŏsen` und normalisiert auf `groesen`, also einen anderen Schlüssel. Gemessen in `variants.xml`: `lemma_2535` führt **neun** Formen (`grozte grozet grozten grossen grôzte grôzet grôssen grozzet grosset`), **keine davon normalisiert auf `groesen`**, und der einzige Träger dieser Normalform ist `lemma_2534` mit der Form `grösen`. Das Verblemma stand für diesen Schlüssel also nie zur Wahl. Die richtige Erklärung ist die schlichteste und stand von Anfang an in den Befund-CSVs: eine **Lücke im Variantenbestand** von `lemma_2535`. **Damit hat derselbe Fall drei Erklärungen durchlaufen, und die ersten beiden waren gebaut statt gelesen:** meine (Stufe 2 überschreibt Stufe 1), ihre (Homographie mit 1.223 Belegen), und die gemessene. Beide falschen hatten eine korrekte Messung neben sich stehen, die zu einem anderen Schlüssel gehörte.

**Die Lehre, die nicht gegriffen hat, ist die meistzitierte des Tages:** ein Befund wird erst zur Aussage, wenn die Quelle offen war, und für einen Ablauf ist die Quelle der Ablauf, nicht die Tabelle daneben. Ich hatte sie am selben Tag dreimal selbst angeführt. **Der Tag hat damit dreimal dieselbe Abwesenheits- oder Mechanismusfrage falsch beantwortet, in drei verschiedenen Gestalten:** falsche Datenquelle (`@ana`, Vormittag), falsche Kodierung (`grep -P "\xc2\xad"` findet null von zwölf weichen Trennstrichen), falsche Normalform (`groezen` statt `grozen`, Befund der Spur an sich selbst). Daraus die Fassung, die zweimal gehalten hat und die passive Formulierung ersetzt: **eine Abwesenheitsabfrage wird zuerst an einem bekannten Positivfall getestet; findet sie den nicht, ist die Abfrage widerlegt und nicht der Bestand.** Genau das hat den `grep`-Fehler binnen einer Minute gefangen, weil zwölf bekannte Vorkommen danebenlagen.

**Der substanzielle Fund aus derselben Kette, und er ist kein Fehler, sondern eine Eigenschaft, die niemand benannt hatte: `variants.xml` ist nicht einwertig, die daraus gebaute Karte schon.** Gemessen über alle `<form>` der Quelle, MHG-normalisiert: **234.243 Normalformen, davon 4.972 mit mehr als einem Ziel-Lemma.** `grossen` zeigt dort auf `lemma_2534`, `lemma_2535` und `lemma_31392`, `a` auf `lemma_1`, `lemma_2` und `lemma_37325`. In `data/authority-index.json.gz` steht unter `variants` je Normalform genau **eine** Zeichenkette (0 von 234.243 Werten ist etwas anderes), und dort bleibt von `grossen` allein `lemma_2534` übrig. **Beim Indexbau fallen also 4.972 Mehrdeutigkeiten still weg**, und Stufe 2 der Auflösung liefert deshalb immer genau ein Lemma, auch wo die Quelle mehrere kennt. Gefunden hat das die Spur beim Prüfen einer Prämisse, auf der an diesem Tag drei verschiedene Erklärungen desselben Falls standen, ihre zwei und meine eine. Die Regel daraus: **wer über `variants.xml` argumentiert, muss sagen, ob er die Quelle meint oder die gebaute Karte.** Für den Anlassfall ändert es nichts, `groesen` hat auch in der Quelle nur ein Ziel.

**Rot, zum siebten Mal, und diesmal in einer Nachricht statt in einer Datei: einen Peer-Befund als gemessen weitergegeben, den ich nicht gemessen hatte.** Die Spur hatte einen CI-Bot-Befund mit einer Zeilenfalle erklärt (`rg -c` zähle Zeilen mit Treffer, und in der WZB stünden mehrere `<w>` je Zeile). Das klang zwingend, ich habe es übernommen, an sie zurückgespiegelt und in den Statusbericht geschrieben. **Gemessen: 0 von 235.993 Zeilen der WZB tragen mehr als ein `<w>`**, die Falle existiert nicht. Die wirkliche Ursache ist enger und hat die Spur selbst nachgereicht: das Suchmuster ließ nur Tokens zu, deren einziges Attribut `xml:id` ist, und drei der 922 tragen zusätzlich ein `pos="DIG"`. Die Bot-Zahl war korrekt erzeugt, nur nicht das, wofür er sie hielt. **Der Vorgang ist getrennt von der sechsten Zeile zu zählen**, obwohl er denselben Modus hat: dort war es eine eigene Erfindung, hier eine fremde Übernahme, und der Anlass ist ein anderer. Die Lehre, die nicht gegriffen hat, ist wörtlich die, die im selben Gespräch gelobt wurde: ein Befund ist auch dann eine Behauptung, wenn er von einem Werkzeug oder von einer sorgfältigen Spur kommt. **Zwei Minuten Messung hätten gereicht, und ich hatte die Datei an diesem Tag schon dreimal offen.**

**Phase:** Betrieb, Lauf am selben Abend wieder aufgenommen. Wellen 2 und 3 vorab vermessen, Spur `mhdbdb-wellen-2345` in Welle 2, `fable-reviewer` Runde 1 auf Fable 5.1 beauftragt. Kein `npm test` auf der Koordinationsseite, keine Daten, kein Index berührt. Das Matrix-Gate lief zweimal rot und wurde beide Male nach einem Diff mit `--apply` nachgezogen; die zweite Ursache war eine einzige Zelle, das `updatedAt` von #28. Der Wiederaufnahmepunkt steht im #44-Zwischenstand.

---

## 2026-09-02 – Der Wellenlauf zu Ende gebracht, und dreimal saß der Fehler im Zuschnitt der Prüfung

Fortsetzung des am 01.09. pausierten Laufs, Spur `mhdbdb-wellen-2345`, Auftrag `docs/playbooks/kickoffs/2026-09-01-issue-lauf-fortsetzung.md` im Stand `091335fe0`. Dies ist der Eintrag der **Spur**; der Eintrag der Koordination zum selben Lauf steht unter dem 01.09.

**Die Wurzel gehörte in die Hülle, und das war nicht die interessanteste Hälfte des Befunds.** Welle 2 baute die Kandidatenmenge für #28 über die transitive Hülle unter `concept_23123000`. Die Vorabmessung hatte die Wurzel selbst ausgelassen, mein Nachbau zunächst auch. 31 Lemmata hängen direkt an ihr, 27 davon ohne Treffer in irgendeiner der 17 benannten Kategorien, und es sind genau die Wörter, mit denen der Text über Fremdsprachigkeit **spricht**, statt sie zu belegen: `welsch`, `rotwalsch`, `tolmetze`, `zunge`, `ûzlegen`. Die Menge wuchs von 6.219 auf 6.246 Lemmata und von 225.505 auf 227.652 Belege. Die Zahlendifferenz ist das Unwichtigste daran.

**Der teuerste Fix des Laufs hat einen Prüfpfad entwertet, den niemand nachgezählt hat.** Derselbe Fix machte den Guard `if not concepts` in `main()` zu totem Code: die Kategorien werden jetzt aus einer anderen Menge gefüllt, und ein falsch geschriebener Wurzel-Identifier erzeugte statt einer Fehlermeldung eine leere CSV mit Rückgabewert 0. Zwei `fable-reviewer`-Runden hatten den Fix gesehen und die Nebenwirkung nicht. Gefunden hat es der CI-Bot in Runde 3. **Die Lehre über den Anlass hinaus: ein Fix ändert nicht nur, was er soll, er kann Prüfpfade entwerten, die auf dem alten Verhalten beruhten.** Die Gegenprobe dazu ist billig und wurde in Welle 3 gleich zweimal gemacht: einmal mit einem erfundenen Wurzel-Identifier, einmal mit einem Verzeichnis erfundener Wörterbucheinträge, jeweils um zu zeigen, dass ein Gurt noch erreichbar ist.

**Rot: `check-doc-inventories.py` lief nicht lokal, und genau er wurde rot.** Der Welle-2-PR ging mit zwei neuen Skripten hinaus, von denen keines in `docs/DEVELOPMENT.md` und `scripts/README.md` stand. Das Gate liegt in `scripts/audit/`, und ich hatte drei andere aus demselben Verzeichnis von Hand aufgerufen. Die dokumentierte Lehre, die nicht gegriffen hat, ist die Bump-Gate-Lehre vom 31.07. in `feedback_index_version_bump`: ein Gate lokal laufen zu lassen spart eine Pipeline-Runde. Sie war auf Versionsstellen gemünzt und gilt für jedes Gate im selben Verzeichnis. Nachgetragen in `3b9abb3f9`.

**Die Hälfte einer Prüfmenge waren gar keine Schreibformen.** Welle 3 misst unsere dreistufige Lemmaauflösung gegen den Verweisgraphen des Findebuchs. Der erste Entwurf las die Formen mit `itertext()`, und `<form type="sublemma">` trägt im selben Element die grammatische Abkürzung: 3.462 der 8.610 Sublemmata haben ein `<gram>`-Kind, bei **2.705 ist die Abkürzung der gesamte Inhalt**, dort steht überhaupt keine Schreibform. Rund die Hälfte von Teil 2 war kontaminiert, und die kontaminierten Strings trafen trotzdem, weil Stufe 3 in der Richtung „Eingabe beginnt mit Lemma" prüft. Runde 1 des `fable-reviewer` fand es.

**Runde 2 fand denselben Fehler noch einmal in anderer Kleidung, und das ist der interessantere Fund.** 21 vermeintliche Mehrwortformen waren Einzelformen mit einem `<hi>`-Abkürzungsmarker. **Das Leerzeichen entsteht nicht im Text, sondern an der Markup-Grenze.** Beide Befunde haben dieselbe Bauart und kamen eine Runde auseinander: wer ein Element überspringt, muss fragen, welche anderen Kinder dasselbe tun. Die Gegenprobe, die in solchen Fällen meistens fehlt, ist die nach der Reichweite des Fixes: alle 39 `<hi>` unter Sublemma-Formen sind Marker, und `<form type="lemma">` trägt nur `<ref>`-Kinder, das Überspringen ändert dort **0** Formen.

**Teil 1 des #259-Prüfdatensatzes kann die Fehlerklasse nicht testen, wegen der das Ticket existiert.** Das Auswahlkriterium (die Schreibform ist bei uns selbst ein Lemma) ist genau die Bedingung, unter der Stufe 1 trifft; die Menge löst deshalb zu 100 % auf Stufe 1 auf, gemessen 543 von 543. Der Test der Stufen 2 und 3 ist Teil 2, und er ist mit 2.781 Fällen gut fünfmal so groß. Trefferquote dort 34,4 %. **Die Befundliste bleibt außerhalb des Repositoriums**, sie trägt Trierer Schreibformen; im Diff stehen nur aggregierte Zahlen über unsere eigenen Daten, und der Lauf endet mit einer Warnzeile, die das sagt.

**Welle 4 zeigt, wie eine Wortartentscheidung messbar wird, statt Sprachgefühl zu bleiben.** Die 98 Breve-Tokens der Wenzelsbibel, die der mechanische Lauf vom 31.08. wegen mehrdeutiger Wortart zurückgehalten hatte, sind am Verskontext entschieden: 89 annotiert, 9 im Rückhalt. Drei Entscheidungsklassen wurden nicht am Sprachgefühl entschieden, sondern am Bestand gemessen. Die wichtigste ist die Substantivierung: von den acht ADJ/NOM-Lemmata der Menge sind sieben gemessen (*roete* bleibt draußen, es trägt allein 132 der 201 `NOM`-Belege und fällt unter eine andere Regel), diese sieben tragen 69 eindeutig als `NOM` getaggte Belege, 60 davon außerhalb der WZB, alle einzeln angesehen. Der rohe Anteil täuscht (60 `NOM` gegen rund 27.000 eindeutige `ADJ`), weil attributive Verwendung um Größenordnungen häufiger ist, nicht weil die Bauart anders getaggt würde. **Die erste Fassung sagte „attributiv ist keiner der 60", und das war zu stark:** zwei sind es doch, einmal attributiv über die Versgrenze hinweg (`AC3_22210_11`, *seit das nie so boser man wart*), einmal als getrennte Hälfte von *hôchzît*. Die Aussage trägt nur in eine Richtung, und das genügt für die Entscheidungsrichtung dieses Laufs: das Haus taggt die Substantivierung `NOM`, aber aus einem `NOM`-Tag folgt keine Substantivierung. Dazu: `umbe` vor `sus/sust` steht in allen 5 aufgelösten Fällen `PRP` und in keinem `ADV`; `vor` steht mit Nominalphrase rechts 738 zu 6 als `PRP` und sonst 158 zu 105 als `ADV`.

**Vier der 98 sind kein Wortartproblem, sondern ein falsches Ziel-Lemma, und zwei davon sind gar keine Wörter.** `grŏsen` in „wil grŏsen deinen namen" ist das Verb *grôzen*, und `grôz` führt kein `VRB`. `hŏrde` in „die vorporgin hŏrde des sandes" ist der Hort, nicht das Hören. Und zweimal ist `tŏch` die erste Hälfte von *tŏchter*, **zerrissen durch einen mitten im Wort stehenden Blattmarker** („von den tŏch XXVIII GENE tern"). Das ist dieselbe Bauart wie Punkt 1 desselben Tickets, die 17 Tokens mit literalem Escape, nur andersherum: dort zwei Wörter in einem Token, hier ein Wort auf zwei verteilt. Bemerkenswert daran ist, dass die erzeugenden Zeilen in `variants.xml` **für sich richtig** sind: `hoerde` ist ein Präteritum von *hœren*, `toech` eines von *ziehen*. Eine korpusabgeleitete Variantenzuordnung kann global stimmen und lokal falsch sein.

**Rot, dritter Auftritt derselben Bauart an einem Tag: eine Abwesenheitsabfrage, deren Zuschnitt den gesuchten Fall ausschließt.** „Ein Lemma *grœzen* gibt es nicht" stand zwei Runden lang im Entwurf und war falsch: `lemma_2535` *grôzen* `VRB` existiert, mit 13 Belegen in 11 Texten. Meine Suche lief über die normalisierte Form `groezen`, *grôzen* normalisiert aber auf `grozen`. Die Regel, die die Koordination daraus formuliert hat und die hier festgehalten wird: **eine Abwesenheitsabfrage wird zuerst an einem bekannten Positivfall getestet; findet sie den nicht, ist die Abfrage widerlegt und nicht der Bestand.** Die Lehre, die nicht gegriffen hat, ist `feedback_zahlen_messvorschrift` vom 31.07.: eine Zahl ohne dokumentierte Zählweise. Für eine Null gilt sie genauso, und für eine Null ist sie gefährlicher, weil eine Null nicht auffällt.

**Derselbe Fall hat dann drei Erklärungen durchlaufen, und die ersten beiden waren gebaut statt gelesen.** Die Koordination erklärte den Fehlgriff mit einem Überschreiben durch Stufe 2, das es nach `docs/CONTRACTS.md` §C nicht geben kann (`EARLY RETURN -- skip stages 2-3`). Ich erklärte ihn mit Homographie: `grozen` trage 1.223 korrekte Adjektivtokens, `variants.xml` halte je Normalform ein Ziel, die häufigere Lesart gewinne. Auch falsch, gefunden vom CI-Review-Bot. **Das Token `grŏsen` normalisiert auf `groesen`, meine Messung galt `grozen`, das sind zwei Schlüssel.** `lemma_2535` führt neun Formen, keine davon normalisiert auf `groesen`; das Verblemma stand für diesen Schlüssel nie zur Wahl. Die gemessene Erklärung ist eine **Lücke im Variantenbestand**, und sie stand von Anfang an in den CSVs, bevor ich sie durch die schönere ersetzt habe. Beide falschen Erklärungen hatten eine korrekte Messung neben sich, die zu einem anderen Schlüssel gehörte. **Ein Vorgang mit drei Stationen, keine drei Fehler**, sonst zählt der Zähler Stationen statt Wiederholungen. Wie dünn die richtige Zuordnung ist, sagt die Gegenprobe: die Normalform `groesen` hat im ganzen Korpus 2 Tokens, eines davon ist dieses.

**Die vierte Station kam von der lokalen Review-Runde 2 und ist die einzige mit Wert über den Fall hinaus: `variants.xml` ist gar nicht einwertig.** Die Prämisse, auf der beide falschen Erklärungen ruhten, ist selbst falsch. Gemessen: **4.972 der 234.243** MHG-normalisierten Formen zeigen auf mehr als ein Lemma, *grossen* sogar auf drei. Einwertig ist erst die daraus **gebaute** Karte im Authority-Index, die je Normalform einen String führt, und der Backfill-Matcher wählt bei Mehrdeutigkeit nicht, sondern legt den Fall in den Review. **Wer über `variants.xml` argumentiert, muss sagen, ob er die Quelle meint oder die gebaute Karte**, und keine der drei Erklärungen dieses Vormittags hat das getan. Beruhigend immerhin: die Behauptung stand nur in den Artefakten dieses Laufs, nirgends in `docs/` und in keinem Projektskript.

Die Einordnung des Falls überlebt alle drei Korrekturen: unsichtbar für das Frontend, wirksam für jedes Werkzeug, das den Variantenbestand direkt liest. Das ist Kategorie C der #259-Messung, dort mit 361 Fällen beziffert, und damit hat diese Kategorie jetzt eine Adressatenangabe.

**Und damit zum eigentlichen Ärgernis des Tages: beides stand schon in `docs/CONTRACTS.md` §C.** Die Frühgeburt der Stufe 1 steht dort als Pseudocode (`EARLY RETURN -- skip stages 2-3`), und die Mehrwertigkeit steht drei Seiten weiter als benannte Regel: „**First occurrence wins** – if two lemmata claim the same variant form, only the first one stored", mit Quellenangabe auf die `if normalized_variant not in variants`-Wache in `build-authority-index.py`. Der Abschnitt nennt sogar die beiden Zahlen, die auseinanderzuhalten sind. **Zwei Sessions haben an einem Vormittag drei Erklärungen für einen Fall gebaut, und die richtige Antwort stand in dem Dokument, das genau für diese Frage angelegt ist.** Das ist keine Lücke in der Dokumentation und keine im Werkzeug: wir haben nicht nachgesehen. Die Lehre, die sich daraus formulieren lässt, ist unangenehm banal und deshalb hier ausgeschrieben: **bevor ein Mechanismus erklärt wird, wird das Dokument geöffnet, das ihn beschreibt.** Es gibt in diesem Projekt genau eines dafür, und es heißt CONTRACTS.md.

**Der Wiederholungslauf, der nur die Reproduzierbarkeit zeigen sollte, hat einen Defekt gefunden, den kein Gate hätte finden können.** Das Skript schreibt den Pfad seines Provenienz-Logs in den `<change>`-Eintrag des Korpusheaders, und es schrieb dorthin, was auf der Kommandozeile stand. Beim ersten Lauf war `--out-dir` relativ und der Eintrag richtig; beim zweiten absolut, und damit stand ein Windows-Pfad mit Laufwerksbuchstaben und dem Worktree-Namen im Korpus. **Ein Wert, der in eine Datei geht, darf nicht davon abhängen, wie der Aufruf getippt wurde**; das Skript rechnet den Pfad jetzt repo-relativ um und bricht ab, wenn er außerhalb des Repositoriums liegt.

**Der Lehre daraus ist ein Detail wichtig, das leicht verlorengeht:** gefangen hat den Defekt nicht die Wiederholung, sondern dass ich beim zweiten Mal zufällig anders getippt hatte. Ein Wiederholungslauf mit identischer Kommandozeile hätte ihn nicht gezeigt. **Ein wiederholter Lauf findet Nichtdeterminismus, ein anders aufgerufener findet Umgebungsabhängigkeit**, und nur der zweite greift hier. Auf `origin` ist der absolute Pfad nie gelandet, geprüft am Header des gepushten Zweigs und korpusweit über alle 667 Dateien (Muster `C:[\\/]|/Users/|/home/|worktrees|chstn`, vorher an drei Testdateien auf Trefferfähigkeit geprüft, weil eine ungetestete Abwesenheitsabfrage heute schon einmal genug Schaden angerichtet hat).

Die Variation war allerdings Zufall, und darauf lässt sich nichts bauen. **Was die Klasse dauerhaft fangen würde, ist keine Laufvorschrift, sondern eine Prüfung am Ergebnis:** kein absoluter Pfad und kein Benutzername in `tei/`. Die Abfrage steht oben, sie ist schnell und deterministisch und wäre als Zeile in einem bestehenden Audit-Gate ein Zehnzeiler. Das ist hier als **Vorschlag** notiert und nicht als Vorhaben: ob das Projekt ein weiteres Gate will, kostet CI-Zeit und Wartung für eine Fehlerklasse mit bisher genau einem Beinahefall, und das entscheidet Chris.

**Ein Kriterium, das den gesuchten Fall ausschließt, sieht wie Strenge aus und ist Blindheit.** Aus den zwei `tŏch`-Tokens wurde beim Nachsehen in der Rohdatei ein größerer Befund: laufende Kolumnentitel und Kapitelzahlen stehen in der WZB als `<w>` im Textfluss (gemessen 928 der 6.836 unannotierten `<w>`, angeführt von `IOSUE` 104 und `EXO` 88), und an 18 Stellen zerreißen sie ein Wort (`geschep|fet`, `wis|sen`, `veisti|keit`, `isra|hel`). Die naheliegende scharfe Zählung, die zusätzlich verlangt, dass die zusammengesetzte Form in `variants.xml` steht, findet davon **2**. Sie schließt per Konstruktion aus, worum es geht, denn ein zerrissenes Wort ist typischerweise eines, das das Lexikon nicht kennt. Beides steht mit Zählvorschrift in **#390**, das aus diesem Nebenbefund entstanden ist: die Kodierungsentscheidung (`<fw>` gegen `<w>`) gehört nicht in einen Annotationslauf. **Dieselbe Bauart hat der Zuschnittfehler in #259**, wo das Auswahlkriterium für die Prüfmenge genau die Bedingung war, unter der Stufe 1 trifft. Mit der Abwesenheitsabfrage nach *grœzen* ist das derselbe Fehler zum dritten Mal an einem Tag, in drei verschiedenen Wellen und von drei verschiedenen Seiten. Auffällig ist nicht, dass er passiert, sondern dass er jedes Mal wie Sorgfalt aussah.

**Die Konfidenzregel wurde gesucht statt erfunden.** Für die fünf Fälle mit mittlerer Konfidenz galt die Frage, ob sie annotiert werden. `ingest/pos-disambig/369-stat/README.md` beantwortet sie seit dem 24.08.: annotiert wird nur bei hoher Konfidenz. Eine zweite, laxere Konvention im selben Korpus hätte mehr gekostet als fünf zurückgehaltene Tokens.

**Eine Ratsche hat angeschlagen, mit der der Wellenplan nicht gerechnet hatte.** `check-authority-cross-refs.py` führt seit #370 eine Baseline für lemmatisierte Tokens ohne `@corresp`. Die 89 neuen heben die WZB von 5.273 auf 5.362 und machen das Gate rot. Das ist kein Fehler, sondern die Folge der vorab getroffenen Entscheidung, kein `@corresp` zu schreiben, und die Ratsche verlangt genau das Richtige: den Anstieg bewusst und begründet via `--update-baseline` aufnehmen, statt ihn zu übersehen.

**Der CI-Review-Bot ist an diesem PR grün geworden und hat trotzdem drei Befunde geliefert**, bei 18 Dateien samt der 40-MB-Binärdatei. Die Turn-Zahlen dazu hat die Koordination im Job-Log gemessen, ich habe sie nicht nachgeprüft: 46 Turns hier gegen 56 bei #382 mit 13 Dateien. Wenn das stimmt, ist die Vermutung hinfällig, die Turn-Zahl skaliere mit dem Diff, und die 40-MB-Datei trägt als Erklärung für den Abbruch bei #368 nicht mehr. Was ich selbst gesehen habe, ist der grüne Lauf an einem PR, für den ein roter vorhergesagt war. Von den drei Befunden waren zwei richtig und einer falsch, und meine erste Widerlegung des falschen war es auch. Ich hatte sie mit einer Zeilenfalle erklärt (`rg -c` zählt Zeilen mit Treffer), und das trifft hier nicht zu: in der WZB trägt **keine einzige** der 235.993 Zeilen mehr als ein `<w>`, 149.165 tragen genau eines (die 235.994 einer ersten Meldung war ein Teilungsrest: `split('\n')` liefert hinter dem letzten Zeilenumbruch noch eine leere Zeichenkette). Die Ursache ist enger und interessanter: das Muster des Bots, `<w xml:id="[^"]*">`, lässt nur Tokens zu, deren einziges Attribut `xml:id` ist, und **drei** der 922 A-Z-Tokens ohne `@lemmaRef` tragen zusätzlich `pos="DIG"` (`XU`, `UIII`, `XU`). 922 minus 3 ist die 919 des Bots. Gefunden hat das die lokale Review-Runde 2, ich habe es nachgemessen. **Dieselbe Familie wie die Normalform-Verwechslung, nur eine Ebene tiefer: nicht falsche Zähleinheit, sondern ein Muster, das eine Teilmenge stillschweigend ausschließt.** Und wieder gilt: ein Reviewerbefund ist auch dann eine Behauptung, wenn ein Werkzeug ihn liefert, und eine Widerlegung ist es genauso.

**Von den drei Vorrichtungen, die in diesem Lauf rot geworden sind, hat genau eine einen inhaltlichen Befund sichtbar gemacht, den niemand gesucht hat.** Die beiden anderen haben eine veraltete Aufstellung gemeldet: das Matrix-Gate zweimal (Koordinationsseite, 01.09.) und das Inventar-Gate aus #329 einmal in Welle 2, wo zwei neue Skripte in `docs/DEVELOPMENT.md` und `scripts/README.md` fehlten. Beides ist Routine im Nachziehen und liefert kein Wissen. Die dritte, die `@corresp`-Ratsche, hat eine Zahl bewegt, die sonst lautlos gestiegen wäre, und sie auf die Stelle genau beziffert. Die brauchbare Frage an eine Prüfung ist damit nicht „prüft sie richtig", sondern **„kann sie überhaupt jemals rot werden, und woran"**.

**Ein stiller Halt ist in einer Hintergrundsession ein Fehler eigener Art.** Zweimal endete ein Turn, ohne dass ein Weckruf eingeplant war: einmal im Dialog, einmal beim Warten auf CI. CI weckt eine Hintergrundsession nicht. Die Regel, die daraus gilt: wer einen Schritt fertig hat, meldet und fängt den nächsten **im selben Turn** an; nur ein laufender Subagent oder ein Hintergrundbefehl rechtfertigt das Turnende, weil beide von sich aus wecken.

**Eine Anweisung ist nicht dadurch gedeckt, dass sie vom Operator kommt.** Die Koordination bat, einen präzisierten Satz „in beide Statuskommentare" zu nehmen. Die Freigabe lautet aber je einen sachlichen Statuskommentar auf #28, #259, #235 und #216, und #259 hatte seinen bereits. Der Satz steht deshalb nur in #235, von dort auf #259 verlinkt. Die Koordination hat den Widerspruch angenommen und ihn selbst als Grenzüberschreitung verbucht. Eine Spur, die eine Freigabe nur so weit auslegt, wie sie geschrieben ist, kostet einen Satz an der falschen Stelle und spart die Frage, wer die Grenze verschoben hat.

**Rot, eigener Regelverstoß:** für einen Nachtrag an einem Issue-Kommentar habe ich `gh api -f body="$(cat ...)"` benutzt, also Command Substitution in einem Shell-Befehl, die die globale `CLAUDE.md` ausdrücklich verbietet. Erster Fall dieses Fehlermodus in diesem Lauf, also kein Wiederholungsfall, aber die Zeile steht hier, weil ein Zähler nur zählt, was gemeldet wird.

**Phase:** Betrieb. Drei Arbeits-PRs (#386, #388, #389, letzterer als `144fbbd3c`), einzeln gemergt, dazu dieser Eintrag als vierter: der Auftrag verbietet den direkten Push auf `main` ohne Ausnahme, und die Hausregel für kleine Doku-Änderungen hebt eine Auftragsgrenze nicht auf. Kein `Closes` auf keinem der vier Tickets. Statuskommentare auf #28, #216, #259 und #235. `npm test` vor jedem Push, VERDICT-Zeile jeweils im PR.

## 2026-09-02 (Abnahme) – Der Abbau traf die Spur im Laufen, und die Vorkehrung dagegen war schon geschrieben

Koordinationsseite, Abschluss des Wellenlaufs. Vier PRs gemergt (#386, #388, #389, #391), Kontrollzahl am gemergten Stand selbst nachgemessen: 149.165 `<w>` in der WZB unverändert, 6.836 ohne `@lemmaRef` statt 6.925, Differenz genau 89. Die Tokenmenge bleibt identisch, nur die Annotationen kommen dazu.

**Rot, zum achten Mal, und es ist eine Abwesenheitsbehauptung über eine Datei, die zwei Verzeichnisse entfernt liegt.** Im Freeze-Befund auf #385 stand, `kickoff-bausteine.md` verlange einen Abschnitt für Meldepunkte, aber keinen für den Freeze. Beide Hälften sind falsch: Baustein 6 heißt „Was eingefroren ist" und verlangt wörtlich Dateiliste, Inbox, Format und Grund, Baustein 9 ist einer der ausführlichsten überhaupt. Aufgefallen ist es erst, als ich für den Rückfluss den Wortlaut des angeblich fehlenden Bausteins zitieren wollte. Die Messung danach fällt schärfer aus als die Behauptung davor: von zehn Bausteinen stehen **neun** im abgeschickten Auftrag, und der eine fehlende ist ausgerechnet der Freeze-Baustein, von dem im ganzen Auftrag ein Halbsatz übrig ist. Nicht das Skill hat eine Lücke, der Kickoff hat einen vorhandenen Baustein ausgelassen, und geschrieben habe ich ihn selbst. Dieselbe Bauart wie die sechste rote Zeile (Mechanismus erfunden statt `CONTRACTS.md` gelesen). Dass ausgerechnet der Kommentar, der eine Vorkehrung gegen ungelesene Regeln fordert, selbst auf einer ungelesenen Regel steht, ist kein Zufall, sondern zeigt, wie zuverlässig dieser Fehlermodus ist.

**Rot, zum neunten Mal, und dies ist der einzige Fehler des Laufs, gegen den bereits eine ausformulierte Vorkehrung an genau der richtigen Stelle stand.** Der Abbau des Worktrees lief, während die Session der Spur noch lief. `git worktree remove` hat den Verwaltungseintrag entfernt und ist am Verzeichnis mit `Permission denied` gescheitert; der Inhalt war zu diesem Zeitpunkt bereits gelöscht. Das Operator-Skill nennt genau diesen Vorgang als Fehler 1: ein Worktree wurde entfernt, während die Spur noch darin arbeitete, auf Grundlage einer Fertigmeldung statt eines Blicks in die Liste laufender Sessions. `ListAgents` habe ich erst danach aufgerufen, und die Spur stand dort als `bg`, `idle`, seit sechs Stunden.

**Was den Schaden verhindert hat, war nicht der Dateisystem-Lock.** Die Formulierung stammt von der Spur und korrigiert meine eigene: Windows hat den leeren Ordner gerettet, den Inhalt nicht. Verhindert hat den Verlust der Zustand der Spur, nämlich fertig gemeldet, alles gepusht, Arbeitsbaum sauber, kein Stash. Beides ist Zufall gegenüber der Vorkehrung, die gegriffen hätte. Eine Welle früher wäre der Verlust **still** gewesen: ein `git checkout origin/main -- tei/WZB.tei.xml` plus ein halber Lauf hinterlässt weder Status noch Stash, und die Entscheidungstafel der 98 Fälle war zu diesem Zeitpunkt zwei Stunden nicht committete Arbeit.

**Die tragfähige Fassung, ebenfalls von der Spur, und sie ist eine Bedingung statt einer Mahnung:** eine Fertigmeldung ist eine Aussage über die **Arbeit**, `ListAgents` ist eine Aussage über den **Prozess**, und abgebaut wird gegen die zweite. Das ist dieselbe Unterscheidung wie „Quelle oder gebaute Karte" bei `variants.xml`: zwei richtige Angaben über verschiedene Dinge, und die falsche davon beantwortet die Frage nicht.

**Die Verlustprüfung vor dem Löschen von Zweigen braucht eine andere Vorschrift, als die Playbooks nahelegen.** Bei Squash-Merges sagt `git branch --merged` nichts, und `-d` schlägt bei jedem gemergten Zweig fehl, ohne dass etwas verloren ginge. Gemessen wird deshalb der Inhalt: keine Datei, die es nur auf dem Zweig gibt (`diff --name-only --diff-filter=A`), und jede Zeilendifferenz entweder eine, die `main` zusätzlich hat, oder eine 1-zu-1-Ersetzung einer älteren Versionszeile. Für den `--worktree`-Startzweig genügt `merge-base --is-ancestor`. Eine grobe Zählung über `--numstat` reicht **nicht**: sie zeigt bei zwei der vier Zweige dieses Laufs hunderte „hinzugefügte" Zeilen, die allesamt ältere Fassungen derselben Zeilen sind. Ohne die Korrektur der Spur hätte ich zwei der vier Zweige gar nicht geprüft.

**Ein Beinahe-Fehler, der nicht gezählt wird, aber hierher gehört, weil eine Regel ihn abgefangen hat:** der Entwurf des Abschlusskommentars für #385 enthielt den Satz „Der Freeze ist aufgehoben". Der Body desselben Tickets sagt „Eine koordinierende Session kann den Freeze nicht aufheben", von mir am Vortag geschrieben. Gefangen hat es die Regel, zu einer Entscheidungsfrage den bisherigen Stand daneben zu legen, nicht die eigene Aufmerksamkeit. Es ist der erste Fall in diesem Lauf, in dem eine Vorkehrung einen Fehler **vor** dem Schaden abfing, statt ihn hinterher zu zählen. Nebenbefund: der Abschnitt „Abarbeitung" in #385 verlangt, dass jeder Wunsch **vor** dem Aufheben des Freeze eingearbeitet ist, aber alle sechs betreffen eingefrorene Dateien und können erst danach eingearbeitet werden. Die Reihenfolge ist nicht erfüllbar; das entscheidet chsteiner.

**Phase:** Abnahme abgeschlossen. Vier Zweige gelöscht, Worktree-Verwaltungseintrag entfernt, Agent-Memory nachweislich identisch im Hauptbaum, kein Stash, keine unversionierte Arbeit. Offen an chsteiner: die sechs Eingaben in #385 und der Freeze selbst.

## 2026-09-02 (Nachlauf) – Zwei Befunde haben einander widerlegt, und der Test war für die falsche Sache gebaut

Fortsetzung nach der Kontingentpause, Koordinationsseite. Der Wellenlauf war
abgenommen, gearbeitet wurde nur noch an der Begleitung des Health-Checks.
Beide Fehler dieses Abschnitts sind in derselben halben Stunde passiert, und
der zweite ist beim Aufräumen des ersten aufgefallen.

**Rot, zum zehnten Mal: eine ungemessene Annahme, die eine Entscheidung
gestützt hat.** Vorgelegt wurde chsteiner die Entscheidung, die Werkzeugzahl
ganz aus den Hilfeseiten zu nehmen, mit der Begründung, die Aufzählung daneben
trage die Aussage ohnehin und sei immer aktuell. Aufgeschlagen war dafür
nichts. Die Spur meldete daraufhin, die Aufzählung lasse den Pferde-Explorer
aus, und korrigierte sich eine Stunde später selbst: er steht sehr wohl in der
Seite, in Abschnitt 7 „Experimentelle Forschungsdaten"
(`hilfe-playground.html:621`, Karte in 646), nur nicht in der einen Liste in
Zeile 196. Ihr eigener Fehler war ein Grep auf eine CSS-Klasse, die Abschnitt 7
nicht benutzt, also wörtlich „ein leerer Abruf ist kein Nullbefund".

**Die Zeile bleibt trotzdem stehen, und zwar in umformulierter Fassung.** Sie
zählt den Fehlermodus, nicht den Ausgang: die Annahme war zum Zeitpunkt der
Entscheidung durch nichts belegt, und dass sie sich beim Nachsehen
größtenteils als richtig erweist, macht sie nicht zu einer Messung. Wer sie
streicht, weil es gutgegangen ist, macht den Zähler unfalsifizierbar, und genau
das soll er nicht sein. Richtige Fassung: sie traf für die Seite zu und für die
Liste in Zeile 196 nicht.

**Rot, zum elften Mal, und diese ist die unangenehmste des Laufs: ein
Positivtest, der die falsche Sache geprüft hat.** Gemeldet wurden vier
Abweichungen zwischen TEI-Headern und `works.xml` (LAU wikidata, TRO zweimal,
WZB wikidata), ausdrücklich als „selbst gemessen, mit Positivtest". Der Test
existierte und prüft die **Normalisierung**, also dass eine nackte ID und eine
volle URL auf denselben Wert fallen. Was er nicht prüft, ist die **Zuordnung**.
Beim Aufmachen der Stellen bleiben von den vieren zwei übrig.

**Ein Test, der die falsche Sache prüft, macht eine ungeprüfte Zahl nicht
geprüft, er verkleidet sie.** Das ist der Unterschied zu den bisherigen roten
Zeilen dieses Laufs: dort fehlte die Messung, hier stand eine daneben und hat
die Lücke zugedeckt. Für den Empfänger ist das schlechter als gar keine Angabe,
weil das Prädikat ihn davon abhält, nachzurechnen. Aufgefallen ist es nur, weil
`works.xml` aus einem anderen Anlass offen war.

**Das Projektwissen dahinter, und es ist der brauchbare Teil:** der TEI-Header
führt Identifier an zwei verschiedenen Orten, und sie beschreiben verschiedene
Gegenstände.

| Ort | Gegenstand | Beispiel PZ |
|---|---|---|
| `fileDesc/sourceDesc/msDesc/msIdentifier` | das **Werk** | wikidata `Q1247232`, GND `4108542-5` |
| `profileDesc/particDesc/listPerson/person` | eine **Figur oder Person** im Text | wikidata `Q18821`, GND `118634933` |

Wer die beiden nicht trennt, misst Werk gegen Person und bekommt Konflikte, die
keine sind. Gemessen am 02.09.2026 mit PZ als Kontrollfall. Was nach der
Trennung übrigbleibt: **TRO** hat zwei echte Konflikte im `msIdentifier`
(handschriftencensus 929 gegen 212, GND 1181164893 gegen 4285313-8), und
**WZB** trägt dort außer der Sigle überhaupt keinen Identifier, während
`works.xml` vier führt. Das ist keine Abweichung, sondern eine Lücke, und sie
passt zu dem Befund der Spur, dass derselbe Header in seinem `<projectDesc>`
falsche Zahlen über sich selbst angibt.

**Ein Befund über das Verfahren, der nicht dieses Repositorium betrifft:**
`~/.claude/CLAUDE.md` wurde am 02.09. von drei Parteien an einem Abend
geändert, und keine hat es von den anderen erfahren. Ein gleichzeitiger Lauf in
`claude-code-setup` hatte die Datei ab 18:17:51 eingefroren, die Änderung von
hier fiel um 18:42 hinein. Folgenlos blieb es nur, weil keine der vier dortigen
Spuren `sed` benutzt hat, die geänderte Zeile also nichts steuerte. Der Grund
ist strukturell: **der Freeze stand in einem Ticket eines Repositoriums, die
Datei liegt in keinem.** Ein Ticket bindet nur, wer es liest, und diese Datei
liest jede Session der Maschine, während das Ticket keine liest. Der Vorschlag
dazu (eine Freeze-Zeile in der Datei selbst, gesetzt vor dem ersten Kickoff)
liegt bei der dortigen Koordination und ist unerprobt.

**Phase:** Health-Check läuft weiter auf `claude/health-check-0902`. Offen an
chsteiner: #390 umsetzen lassen, die vier nie erbetenen `wait:extern`-Antworten
(#147, #263, #86, #141), die zwei unklaren der 18 zerrissenen Wörter.

---

## 2026-09-02 (Health-Check) – Dreimal stand eine erledigte Aufgabe als offene da, und mehrfach stand eine Messung neben dem, was sie belegen sollte

**Scorecard.** Flow-Check über alle 15 promptotyping-Dokumente, jedes ganz gelesen: 14 Befunde. Algorithmen 3 von 3 zeilengenau konform, XPaths 3 von 3, Rebuild-Test bestanden. JOURNAL-Audit auf vier Fehlerklassen: 2 veraltete Zahlen, **0** Behauptungen ohne Messvorschrift (Kontrollmessung am jüngsten Eintrag: WZB 149.165 `<w>` und 6.836 ohne `@lemmaRef`, beide exakt), 2 tote Verweise, 0 Probleme im Verhältnis zum Archiv. `doc-count-audit.py` fällt von 20 Treffern auf 0. Vier Issues (#392 bis #395), drei davon im selben Lauf umgesetzt statt nur gemeldet. Drei Reviewrunden, `npm test` grün (310 Tests).

**Der Befund, der eine Klasse ist und kein Einzelfall: dreimal steht in der Doku eine Aufgabe als offen, die längst erledigt ist.** `DESIGN.md` führte die Multi-Lemma-CSS-Duplizierung unter „Known Inconsistencies", obwohl `6a9849314` sie am 13.07. beseitigt hat und in `korpus.css` an genau der Stelle ein Kommentar steht, der es sagt (gemessen als Selektorzeilen `^\s*\.multi-lemma-`: `korpus.css` 0, `playground/css/style.css` 5; die einzige Erwähnung in `korpus.css` ist der Kommentar in Zeile 698, der genau das sagt). `TEI-MODEL.md` §8.1 überschrieb eine Liste mit „To be migrated", obwohl kein einziger der Prosatexte noch ein `<l>` trägt: 0 in allen 18 der Tabelle und 0 auch in den drei aus #143 (HMT, APO, HH), die dort danebenstehen, bei zusammen 89.140 `<lb>`. Kontrollwert PZ, ein Versepos: 24.812 `<l>`, 0 `<lb>`. `DECISIONS.md` ADR-004 führte einen Clear-Cache-Button als „Future", der im build-injizierten Footer steht und damit in 14 der 16 ausgelieferten Seiten (`api/index.html` und `404.html` bekommen kein Chrome) und einen eigenen Test hat. Das ist schlimmer als eine veraltete Zahl: es steht eine Arbeit da, die niemand mehr erledigen kann, weil sie getan ist.

**Der zweitbeste Fund kam aus einem Widerspruch zwischen zwei eigenen Messungen desselben Tages**, die um 14.941 auseinanderlagen. Ursache: exakt so viele `<w>` tragen ein leeres `pos=""`. 7.596.147 zählt das Attribut, 7.581.206 den nichtleeren Wert, beide sind richtig. Beide stehen jetzt mit ihrer Vorschrift in `POS-TAGSET.md` §4, statt dass eine gewählt wird, sonst liest die nächste Session die eine als Korrektur der anderen.

### Rote Zeilen

Fünf, die letzte ist die teuerste, weil sie den Lauf selbst betrifft, und die erste ist noch während des Schreibens dieses Abschnitts ein drittes Mal eingetreten.

1. **Nackte Shell-Variablen in Schleifen, dreimal.** Lehre: globale `CLAUDE.md`, „Shell-Konventionen", Werte vorher ermitteln und literal einsetzen. Jedes Mal hat die Umgebung blockiert. Das dritte Mal ist eine halbe Stunde **nach** dem Absatz passiert, den Sie gerade lesen, in einer `for`-Schleife über zwei Issue-Nummern, und es ist damit der beste Beleg des Abends für die Regel, aus der dieser Zähler stammt: eine Lehre, die dreimal an derselben Stelle steht und trotzdem verletzt wird, braucht keine vierte Kopie, sondern einen anderen Mechanismus. Hier gibt es ihn, und er hat funktioniert: der Worktree-Guard hat alle drei abgefangen, bevor etwas lief. Die Regel wirkt also nicht über das Erinnern, sondern über die Sperre, und das ist die brauchbare Erkenntnis daraus.
2. **Aus `protected=true` auf „ein Push nach `main` wird abgelehnt" geschlossen** und das in `DEVELOPMENT.md` geschrieben. Lehre: ein Befund wird erst zur Aussage, wenn die Quelle offen war. Gemessen war das Feld, ungeprüft die Schlussfolgerung; das Ruleset trägt nur `deletion` und `non_fast_forward`, und der Widerspruch stand zwei Zeilen tiefer im eigenen Text. Gefangen vom `fable-reviewer`. **Die Verschärfung gegenüber der dokumentierten Lehre: der Befund war selbst erhoben, und das macht ihn gefährlicher, weil eine eigene Messung sich geprüft anfühlt, auch wenn nur die Zahl gemessen wurde und nicht der Schluss daraus.**
3. **Aus einem gefilterten Grep auf Abwesenheit in der ganzen Seite geschlossen.** Lehre: ein leerer Abruf ist kein Nullbefund, immer einen Kontrollwert mitmessen. Der Grep suchte `h3` einer bestimmten CSS-Klasse und blendete den Abschnitt aus, in dem der gesuchte Eintrag steht. Daraufhin war eine vollständige Werkzeugkarte für eine ausgelieferte Hilfeseite geschrieben, die eine Dublette gewesen wäre und zusätzlich die falschen Werke genannt hätte (ER ist Erec, nicht Eneasroman). Zurückgenommen vor dem Commit, und **gefangen hat sie nichts außer einem zufälligen zweiten Blick auf die Nachbarschaft der Einfügestelle.**
4. **Die Fehlalarmmessung für das neue ROADMAP-Gate maß ein anderes Prädikat als das gebaute.** Gemessen wurde „steht in den geschlossenen Issues", gebaut wurde „steht nicht in den offenen Issues". Issues und PRs teilen sich den Nummernraum, also meldete der erste echte Lauf die gemergten #245 und #246. Gefangen vom eigenen Gate, eine Minute nachdem es existierte.
5. **Fünf falsche Zahlen im eigenen Korrekturtext, in genau den Commits, die Zahlen-Drift beseitigen sollten.** „Acht Tags unverändert" statt 12 und „alle unter einem Zehntelprozent", obwohl NOM mit +0,761 % siebenfach darüber liegt; „sechs ausgelieferte Seiten" für einen Knopf, der in 14 steht; „fünf tote Einträge in der Ping-Tabelle", wo zwei stehen; „die fünf obsoleten Debug-Specs", von denen nur zwei Skips trugen; und in der Korrektur der zweiten dann „in jeder ausgelieferten Seite", obwohl zwei der 16 kein Chrome bekommen. Lehre: „No claim in a comment that does not hold", `CLAUDE.md` → Self-Inflicted Overhead. **Keine automatische Vorrichtung dieses Projekts kann sie fangen**, weil Prosa weder vom `doc-count-audit` noch von einem Test erreicht wird; gefangen hat vier der `fable-reviewer` in Runde 2 und die fünfte derselbe in Runde 3. Die Regel, die ihn vor dem ersten Push vorschreibt, hat damit den Zweck des Laufs gerettet. Was daran zu denken gibt, ist enger: **die einzige Vorrichtung gegen ungemessene Zahlen in Prosa ist ein Agent, und ein Agent kann verschwinden, ohne dass es nach einem Ausfall aussieht.** Der `fable-reviewer` war an diesem Abend zweimal nicht als Agententyp vorhanden, und der Ausfall sah aus wie eine Berechtigungsfrage. Ein Health-Check, der Zahlen-Drift korrigiert und dabei neue erzeugt, greift den Zweck des Laufs an und nicht nur seine Ausführung.

**Die gemeinsame Form von 2, 4 und einem Teil von 5, und sie ist der eigentliche Befund des Abends.** Sie hat zwei Ausprägungen, und die Unterscheidung stammt aus der Gegenlesung durch die Operator-Session, die denselben Fehler am selben Abend an eigenem Material fand:

- **Die Vorrichtung steht neben dem Prädikat, das sie sichern soll.** Das Gate prüfte „steht nicht in den offenen Issues", abgesichert war „steht in den geschlossenen"; drüben ein Positivtest, der die Normalisierung prüfte statt der Zuordnung. Dagegen hilft, die Vorrichtung selbst zu reizen.
- **Die Aussage steht neben ihrer Menge: richtig gerechnet, falsch bezogen.** Dreimal an diesem Abend allein hier. „Fünf tote Einträge" war die zutreffende Zahl für die ganze ROADMAP, eingesetzt in einen Satz über die Ping-Tabelle, in der zwei stehen. „0 Selektoren gegen 6" stellte eine Selektorzählung neben eine Zeichenkettenzählung (richtig ist 0 gegen 5, und der eine Treffer in `korpus.css` ist der Kommentar, der die Entfernung dokumentiert). „In jeder ausgelieferten Seite" war eine Allaussage neben der richtigen Zahl 14, während die Site 16 Seiten ausliefert. Eine Allaussage ist dabei nichts anderes als eine Mengenangabe ohne Zahl, und sie wird auf dieselbe Weise falsch. Dagegen hilft keine Vorrichtung, sondern nur, die Menge zu benennen, über die man spricht. Das ist die gefährlichere der beiden.

Beide Male ist etwas Vorhandenes und Funktionsfähiges der Grund, warum niemand nachsieht. Eine Messung, die nicht dasselbe misst wie die Behauptung, ist schlechter als keine.

**Wo die Fälle gestoppt wurden, ist die eigentliche Wirkungsmessung.** Vier vom `fable-reviewer`, nach dem Commit und vor dem Push. Zwei von der Operator-Session, zu spät für die Meldung und rechtzeitig für diesen Eintrag. Einer, die CSS-Zahl, **vor dem Schreiben**, durch einen mitlaufenden Kontrollwert: die erste Suche lief auf `lemma-highlight-`, lieferte sauber 0 und 0, und der Kontrollwert traf nirgends, weil der Selektor `multi-lemma-` heißt. Dieselbe Zeile hat zehn Minuten später ein zweites Mal gegriffen, als ein Dateimuster `PZ.xml` statt `PZ.tei.xml` suchte und alle 21 Prosatexte als sauber meldete, den Kontrollwert eingeschlossen. Das ist der einzige Fall des Abends, der gar keinen Text erzeugt hat, den jemand korrigieren musste, und er kostet eine Zeile im selben Aufruf. Der Reviewer kostet eine Runde und war zweimal nicht da.

Für die erste Ausprägung ist die Folgerung im Gate umgesetzt: der neue Sättigungs-Check in `build-issue-matrix.py` ist in beide Richtungen gereizt worden, mit Limit 5 (steigt aus) und mit Limit 300 und 1.000 (läuft durch), denn ein Wachhund, der nie gebellt hat, ist kein gemessener Wachhund.

**Was gut lief, damit die Liste nicht kippt:** die Algorithmen und XPaths halten zeilengenau, die Invariante aus `CONTRACTS.md` §H.2a stimmt exakt (`sum(text.wordCount)` = 7.546.332 = unabhängiger Korpusscan), die dokumentierten 396 offenen Cross-Refs über 109 IDs stimmen auf den Ref genau, und die Frage, ob der IndexedDB-Invalidierungsmechanismus ohne den Code auffindbar ist, ist mit Ja zu beantworten: `CONTRACTS.md` §E führt ihn samt der 30-Tage-Folge eines vergessenen Bumps.

**Phase:** Health-Check abgeschlossen, `claude/health-check-0902` als PR offen. Offen an chsteiner: #395 (die WZB-Selbstauskunft im Header, ein reines Korpusticket, das dieser Lauf nicht anfassen durfte) und die Frage, ob ein fehlender Agententyp künftig ein Halt sein soll statt eines Weiter. Geschrieben steht bisher nur der Fall „die Session darf keine Agenten starten"; der Fall „der Typ ist nicht da" ist heute zweimal eingetreten und wurde ohne geschriebene Grundlage als Halt behandelt.

---

## 2026-09-06 – Eindeutigkeit über einer Menge mit einem Element, und ein Alarm, der nur eine andere Zähleinheit war

Cloud-Umgebung, volles Fable-Kontingent, chsteiner eine Woche nicht am Laptop.
Zuschnitt entsprechend: alles, was ohne seine Entscheidung auskommt, wird
gemacht; alles Übrige wird bis zur Entscheidungsreife vorbereitet und liegen
gelassen. Ergebnis in Zahlen: **1.455 Tokens neu annotiert** über drei Läufe,
kein neues Lemma und kein neuer Variantentyp geprägt, Korpus-Index 4.2.8 auf
4.2.11.

| Lauf | Fälle | annotiert | zurückgehalten |
|---|--:|--:|--:|
| #216 Punkt 3 (`vrouwe` vor `minne`) | 155 | 152 | 3 |
| #387 mechanischer Teil | 948 | 948 | 0 |
| #387 Kern (`fro`, kontextpflichtig) | 390 | 355 | 35 |

Der dritte Lauf ist der einzige, der Fable gebraucht hat: 61 Bündel, eines je
Sigel, nach POS-TAGSET §6.3. Die anderen beiden sind mechanisch entschieden und
hätten kein Modell gebraucht.

**Rot: Eindeutigkeit über einer Menge mit einem Element ist keine
Eindeutigkeit.** Der #387-Extraktor sammelt je normalisierter Schreibform alle
Lemmata, die im Korpus daran hängen, und annotiert, wo diese Menge einelementig
ist. Das ist richtig gedacht und war trotzdem beinahe ein falsches Tag:
`NLA_72101_5`, „wie si ze der hohzit **fvrn**", ist das Verb *varn*. Die
Schreibung `fvrn` hat korpusweit **genau einen** annotierten Beleg
(`RF_118100_0`, „fvrn hersante", zu Recht `lemma_7260`), und eine
einelementige Menge ist trivial eindeutig. Das Skript hätte das Verb zur Frau
gemacht, mit einer Begründung, die **wörtlich wahr** gewesen wäre: „alle Belege
dieser Schreibung hängen an `lemma_7260`". Behoben mit `MIN_BELEGE = 5` plus
einer namentlichen Ausnahmeliste. Die allgemeine Form der Lehre: ein Prädikat
über einer Menge braucht eine Untergrenze für deren Größe, sonst misst es die
Stichprobe statt den Gegenstand, und der Fehler versteckt sich hinter einem
Satz, der stimmt.

**Rot: eine Zahl in der falschen Einheit macht eine verbuchte Altlast zu einem
frischen Alarm.** Gemeldet wurde chsteiner „ein echter Befund, und größer als
erwartet: 330 Korpus-Tokens verweisen mit `@ana` auf einen Sense, den weder der
Index noch das Lexikon kennt". Die 330 stimmen. Was fehlte, war die
Zähleinheit, in der die Ratsche arbeitet: **74 distinkte Sense-IDs, und alle 74
stehen seit dem 02.07.2026 in `scripts/audit/lexicon-baseline.json`.**
`check-authority-cross-refs.py` scannt `@ana` ausdrücklich (`REF_ATTRS`) und
druckt die Zeile selbst: „74 sense-ids (330 refs)", Gate grün, `CI CHECK OK`.
Es war nie ein Befund, sondern dieselbe #152-Sache in einer anderen Einheit.
Der Fehlermodus ist derselbe, vor dem der eigene #28-Kommentar desselben Tages
warnt (224 `zunge`-Widersprüche auf drei Senses), nur diesmal in eigener Sache.
**Wer eine Zahl gegen eine Ratsche hält, hält sie in deren Einheit, sonst hält
er sie gegen nichts.**

**Der Ertrag von #28 Phase 2 ist nicht die Liste, sondern ihre Reichweite.**
Der Phasenplan empfiehlt, mit den 430 `@ana`-Widersprüchen anzufangen „statt
mit einer Frequenzschwelle". Gemessen sind das keine Alternativen: **22 der 26
belegstärksten Nicht-Namen tragen keinen einzigen Widerspruch**, das sind
119.101 der 124.369 Tokens (95,8 %). `niht` ist der Fall, an dem es sichtbar
wird: 81.088 Belege, alle mit `@ana`, **jedes einzelne auf den Sprach-Sense**.
Das schärfste maschinelle Kriterium der Menge kann ihren größten
Falschpositiven nicht entfernen, weil die Annotation dort die Quelle des
Problems ist und nicht sein Korrektiv. Umgekehrt liegen 184 der 424
Widersprüche auf 15 Lemmata außerhalb der 26. Beide Listen sind zu lesen.
Nebenbei fällt die `gebrechen`-Frage quantitativ zu: 37 + 1 + 1 = 39
Widersprüche plus `JT_30921000_5` ergeben die 40 sense-disambiguierten Tokens,
die #28 nennt, unabhängig gemessen mit einem anderen Skript.

Die 430 des Plans sind übrigens 424 plus 6: sechs Tokens tragen ein `@ana` auf
einen Sense, den der Lemma-Index nicht führt. Ein Verweis ins Leere
widerspricht nichts, er sagt gar nichts, deshalb steht er jetzt als eigene
Zeile.

**Ein Befund des CI-Bots, der die Sorte war, für die er da ist.** `next_token`
im `fro`-Extraktor nahm das nächste `<w>` in Dokumentordnung des ganzen
`<body>` und überschritt damit die Verszeile. Unabhängig nachgemessen: bei
**116 der 374 Versfälle (31 %)** steht das Zieltoken am Versende, das Feld trug
dort also das erste Wort der Folgezeile, und `prompt.md` stellt genau dieses
Feld an die erste Stelle. Aus dem Lauf ist daraus nachweislich kein falsches
Tag geworden (von den zwölf Anrede-Urteilen stehen neun im Vers, keines am
Versende, drei sind Prosa), aber das Skript bleibt liegen und die 35
zurückgehaltenen Fälle laufen noch einmal hindurch. `cases.json` wurde
**bewusst nicht** neu geschrieben: die Datei ist das Protokoll dessen, was die
61 Agenten gesehen haben, und nicht das, was sie hätten sehen sollen.

**Zur Regel, die chsteiner mitten im Lauf viermal geschickt hat** („immer die
Kommentare lesen in den Issues, nicht nur den Body"): sie steht jetzt in
`CLAUDE.md` unter „Issue Labels", mit vier gemessenen Fällen statt einer
Ermahnung. Der schärfste ist #216: die 12 Kommentare tragen das ganze
Arbeitspaket, und der Body enthält das Wort *vrouwe* nicht ein einziges Mal.
In `BETRIEBSVERTRAG.md` ist sie ein Unterpunkt von Regel 9 geworden und
ausdrücklich **keine** neue nummerierte Regel: `CLAUDE.md` zitiert „Regel 11"
bei der Nummer, und ein Einschub hätte sie stillschweigend verschoben.

**Umgebungswissen für die nächste Cloud-Session, alles gemessen:**

- **Tests brauchen `CI=1`.** Ohne die Variable fährt Playwright 6 Worker auf 4
  Kernen gegen einen 42-MB-Index: 7 Fehler und 9 Flaky. Mit 2 Workern genau
  ein Fehler, und der ist echt und umgebungsbedingt: `lemma page loads
  Wörterbuchnetz entries via API` ruft `api.woerterbuchnetz.de`, was der
  Egress-Proxy mit 403 auf CONNECT abweist. Auf `origin/main` fällt derselbe
  Test identisch aus.
- **Die Authority-Datenbanken sind hier nicht erreichbar** (d-nb.info,
  lobid.org, handschriftencensus.de). Die TRO-Identifier-Frage aus #395 ist in
  dieser Umgebung deshalb nicht zu klären. `WebSearch` geht und bestätigt
  indirekt, dass handschriftencensus 212 der Trojanerkrieg ist, also
  `works.xml` recht hat und die 929 im Header falsch ist. **Das Korpus wurde
  darauf trotzdem nicht geändert**: eine indirekte Bestätigung ist keine
  Quelle.
- **`data-integrity.yml` läuft nur auf `pull_request`**, nicht auf einen Push
  auf einen Branch. Ein Datenzweig ohne PR hat also kein Gate über sich. Das
  war der ausschlaggebende Grund, PR #398 früh zu öffnen statt am Ende.
  **Kehrseite, am Nachmittag desselben Tages gemessen:** sobald der PR offen
  ist, lösen die Pfadfilter für **jeden** Push aus, auch für einen reinen
  Doku-Commit, weil `paths` bei `pull_request` gegen den gesamten PR-Diff
  gehalten wird und nicht gegen den Push. Zusammen mit `cancel-in-progress`
  heisst das: jeder Push bricht den laufenden Gate-Lauf ab.
- Chromium ist als Build 1194 installiert, das Projekt pinnt 1193 (Symlink
  genügt), und `python3` ist 3.11, während die Skripte 3.13 brauchen
  (`Path.read_text(newline=)`). Immer `python3.13` aufrufen.

**Zwischenstand am Mittag:** PR #398 offen, sechs Bot-Runden, die letzte
vollständige ohne Befund. Offen an chsteiner, alles drei eine Entscheidung und
nichts davon recherchierbar: der Variantentyp für die Zirkumflex-Schreibung
unter `lemma_7260` (blockierte dieselben 3 KZW-entschiedenen Tokens zum zweiten
Mal), die 35 zurückgehaltenen `fro`-Fälle, und ob TEI-Header die
`works.xml`-Identifier weiter duplizieren sollen. Alle drei sind am selben Tag
entschieden worden, siehe den folgenden Eintrag.

---

## 2026-09-06 (Nachmittag) – Eine Zusage im Perfekt, und sechsmal derselbe Fehler in verschiedenen Kostümen

Fortsetzung desselben Tages, nach den drei Entscheidungen von chsteiner: der
#235-Präzedenzfall gilt, an KZW geht nur, was sie wirklich braucht, den Rest
entscheidet Fable. Endstand **1.477 Tokens** (die 1.455 vom Vormittag plus 3
plus 19), Korpus-Index 4.2.11 auf 4.2.13, Authority-Index 1.9.2 auf 1.9.3, und
ein Skript, das es seit Monaten gab, hängt jetzt in der CI.

**#216 ist abgeschlossen, und der Präzedenzfall kollidierte mit einer Ratsche.**
Die 3 zurückgehaltenen `vrouwe`-Belege in RVBR sind geschrieben, damit steht
Punkt 3 auf 155/155. Der Weg dahin ist der lehrreiche Teil: der #235-Fall
erlaubt, für eine Zirkumflex-Schreibung ohne Typ einen Beleg **ohne**
`@corresp` zu schreiben, und genau das hätte die #370-Ratsche rot gemacht, die
für RVBR null Tokens ohne `@corresp` toleriert. Aufgefallen ist es mitten in
der Umsetzung, nachdem die Freigabe schon vorlag. Ich hatte bereits einen
`ohne_corresp`-Schlüssel in `apply-homograph.py` gebaut; er ist wieder draußen
(`git checkout --`), weil ein Mechanismus, der die Ratsche still umgeht, nach
genau dieser Entscheidung das Falscheste ist, was man bauen kann. Stattdessen
neu gefragt und **`type_372365` geprägt**, der erste neue Variantentyp dieser
Session (Maximum vorher `type_372364`). Kosten: `variants.xml` wächst um genau
eine Form, 256.761 auf 256.762 – und diese Zahl steht an zehn Stellen im Repo,
zwei davon auf ausgelieferten Seiten.

**Der ADJ/ADV-Nachlauf, und was ein gemessener Prior wert ist.** Die 31 mittel-
konfidenten Fälle des `fro`-Laufs waren sich beim Lemma alle einig; offen war
nur ADJ gegen ADV, und das ist nach POS-TAGSET §4 ausdrücklich **K4**, also
LLM-Aufgabe und keine kuratorische Frage. Das war der Grund, sie nicht an KZW
zu geben. Der Prior hat dann die eigentliche Arbeit getan: über alle 667
Dateien trägt auf `origin/main` **kein einziger** der 4.869 `lemma_7250`-Belege
`ADV` allein. Von 14 ADV-Vorschlägen des ersten Durchgangs sind daraufhin 13
gefallen. Geschrieben sind 19, zurückgehalten 11, und zusammen mit den zwei
Substantivierungen gehen **13 Fälle an @wachauer**. Zwei Dinge liefen anders
als sonst: `unentschieden` war ein erlaubtes Ergebnis (zwei Fälle, beide die
verblose Antithese in Parallelüberlieferung), und bei sechs Fällen wurde die
Konfidenz **nachgefragt statt überstimmt** – fünf gingen auf `high`, einer
blieb bewusst `medium`. Der einzige ADV-Fall (`RVBR_6083_0`) ist gut begründet
und steht trotzdem nicht im Batch: wäre er richtig, wäre er der erste
`ADV`-Beleg von *vrô* im Korpus, und eine Entscheidung gegen den gesamten
annotierten Bestand gehört nicht in einen maschinellen Lauf.

**`doc-count-audit.py` hängt jetzt als Gate in `data-integrity.yml`.** Das
Skript kennt seit Monaten ein `--check` mit Exit ungleich 0 bei Drift und lief
in keinem Workflow. Was das kostet, hat der Tag vorgeführt: die alte 256.761
blieb an zehn Stellen stehen, gefunden hat es der Review-Bot, nicht die CI. Der
Ort ist `data-integrity.yml` und nicht `no-cdn-check.yml`, weil dort `lxml`
ohnehin installiert ist; die Kosten sind sechs Sekunden gegen 45 Minuten
Job-Timeout. **Die Grenze steht als Kommentar daneben und hat zwei Hälften, die
verschieden wirken:** `docs/**` und `*.html` fehlen in den Pfadfiltern, dort
ändert ein PR also die **behauptete** Zahl; `playground/**` fehlt ebenfalls, und
dort ändert ein PR die **gemessene**. Ein PR, der ein UI-Modul hinzufügt, löst
diesen Workflow nicht aus und macht den nächsten, unbeteiligten Daten-PR rot.
Die Pfadfilter zu erweitern hieße, den 45-Minuten-Lauf bei jeder
Playground-Änderung zu starten; das ist ein Handel über fremde Arbeit und
deshalb bewusst nicht getroffen, sondern mit Preis daneben notiert.

**Nachgesehen statt auf grün vertraut.** Nach der #397-Regel ist ein Gate, das
grün wird, ohne etwas geprüft zu haben, genau die tote Wache. Also ins Job-Log
von `101512379175` gesehen: der Schritt lief als Nummer 7 in vier Sekunden,
druckte alle 19 gemessenen Größen (darunter `variants.xml — Formen | 256.762`,
die Zahl, um die es ging), scannte Docs und ausgelieferte HTML-Seiten und
meldete in der Anker-Selbstprüfung kein konfiguriertes Paar ohne Treffer. Vor
der Korrektur wäre er rot gewesen.

**Rot, und es ist der Befund des Tages: sechs Bot-Befunde, ein einziges
Muster.** Runde 10 (die Variantenzahl an zehn Stellen), Runde 11 (die
Konfidenz-Rechnung, die einen von zwei Läufen nannte), die Zusage „der Body ist
mitkorrigiert", die geschrieben wurde, bevor sie ausgeführt war, Runde 14
Befund 1 (der billigste Check hinter dem teuersten, obwohl der Workflow-Kopf
„billig nach teuer" ausschreibt), Runde 14 Befund 2 (die offengelegte Grenze
nannte `docs/**` und `*.html`, aber nicht `playground/**`), Runde 15 (dieselbe
Grenze nannte dann drei Herkünfte als eine, und die genannte Abhilfe deckte nur
eine davon). Und nachträglich derselbe Fehler im Nachlauf-README: „31 von 31"
über einer Menge, die 30 Elemente hat. Die 31 ist dabei nicht falsch, sie zählt
die `confidence`-Fälle des ersten Laufs, und der Bot hat sie in Runde 11 selbst
so nachgemessen; nur spricht der Satz über die Fälle des zweiten Laufs, und das
sind 30. **Zwei richtige Zahlen über zwei verschiedene Mengen**, hingeschrieben
mit dem Bezugswort der falschen. Genau die Sorte, die eine Nachmessung
bestätigt, statt sie zu finden.
**Jedesmal eine Aussage über eine Menge, geschrieben aus der Kenntnis eines
Teils davon.** Das ist dieselbe Form wie die 330 `@ana`-Tokens vom Vormittag,
nur ohne Zähleinheit als Ausrede. Die Gegenmaßnahme ist keine Regel, sondern
eine Frage vor dem Schreiben: *woher weiß ich, dass das für alle gilt, und wo
steht die Zählung?* Wo die Antwort ein Kommando ist, gehört das Kommando
danebengeschrieben; die Fälle, in denen das getan wurde, sind die, die kein Bot
mehr angefasst hat.

**Rot, und der Beleg dafür stammt aus diesem Absatz selbst: die Pfadfilter
eines `pull_request`-Triggers schützen einen Push nicht.** **16**
`data-integrity`-Läufe sind von meinen eigenen Pushes abgebrochen worden,
darunter der allererste, der das neue Gate vollständig ausgeführt hätte.
Die Zahl stand hier zuerst als „zwei", dann als „drei", und beide Male war sie
aus dem geschätzt, was mir gerade aufgefallen war. Gemessen über die
Laufhistorie des Branches:

    25 abgeschlossene data-integrity-Laeufe auf diesem Branch
    16 davon cancelled, 9 success

Alle Pushes auf diesen Branch stammen aus dieser Session, also gehen alle 16
auf sie zurück, verteilt über den ganzen Tag von 09:03 bis 17:42. Das war
mithin kein Ausrutscher am Ende, sondern die Arbeitsweise des Tages.
`cancel-in-progress` gilt in diesem Workflow für `pull_request`. Beim dritten
Mal hatte ich vorher nachgesehen und mich freigesprochen: der Commit fasst nur
`docs/JOURNAL.md` und `ingest/**` an, beide stehen nicht in den Pfadfiltern,
also könne kein Lauf starten und keiner abgebrochen werden. **Gemessen ist das
Gegenteil**, und zwar an genau diesem Push:

    git show --name-only 032d859   -->  docs/JOURNAL.md
                                        ingest/pos-disambig/387-fro-adjadv/README.md
    Lauf 34043618289 auf 032d859   -->  gestartet
    Lauf 34043424099 auf f37254e   -->  cancelled

Die Erklärung ist die dokumentierte Auswertungsregel und nicht die Messung: bei
`pull_request` werden die `paths` gegen den **gesamten** PR-Diff gehalten, nicht
gegen den einzelnen Push. PR #398 fasst `tei/`, `authority-files/`, `data/` und
`scripts/audit/` an, also löst **jeder** Push auf diesen PR den Workflow aus,
gleichgültig was er enthält. Für einen `push`-Trigger gilt das nicht, und daher
kam mein Irrtum.

Der Inhalt der Lehre bleibt und wird durch die 16 eher schärfer: **wer ein
neues Gate einbaut, wartet dessen ersten vollständigen Lauf ab, bevor er
weiterschiebt.** Dazu gehört, die Prüfung „ist der Lauf durch" wörtlich zu
nehmen: am 06.09. um 17:50 standen drei der vier Checks auf `success` und
`validate` auf `in_progress`, und der Push ging trotzdem raus, weil die drei
grünen gelesen wurden und der eine laufende nicht. **Ein Check, der noch läuft,
ist kein grüner Check**, und drei von vier ist bei einem `cancel-in-progress`
genau so viel wert wie null. Neu ist, dass der Umweg
„dieser Commit fasst ja nichts Gefiltertes an" auf einem Daten-PR nicht
existiert. Und die Form des Fehlers ist wieder dieselbe: eine Aussage über eine
Menge (was löst den Workflow aus) aus der Kenntnis eines Teils davon (die
Filterliste), geschrieben ohne die Regel, nach der sie ausgewertet wird. Der
vorstehende Absatz zählt sechs solche Fälle; dieser hier ist der siebte, und er
ist entstanden, während ich den sechsten aufschrieb.

**Phase:** PR #398 offen. Bei chsteiner liegen nur noch Dinge, die diese
Umgebung nicht lösen kann: die 13 `fro`-Fälle für KZW (#387), die
TRO-Identifier-Frage (#395, Authority-Datenbanken hier nicht erreichbar), und
ob `playground/js/ui/**` in die Pfadfilter soll. #390 wartet bewusst auf den
Merge.

---

## 2026-09-06 (Abend) – Zehn blockierte Tickets entscheidungsreif, und drei ihrer Prämissen waren abgelaufen

Auftrag von chsteiner nach den beiden Entscheidungen am Nachmittag: die Woche
für das Entscheidungsreif-Machen der blockierten Tickets nutzen, weil kein
`auto:full` und kein `auto:brief` mehr offen ist. Zehn Vorgänge bearbeitet
(#364, #378, #308, #363, #366, #375, #267, #252, #228, #358), jeder mit einer
Messung statt einer Zusammenfassung. Nichts an Korpus oder Authority geändert.

**Der Ertrag steckt nicht in der Zusammenfassung, sondern im Nachmessen. Drei
von zehn Tickets hatten Prämissen, die nicht mehr galten**, und alle drei in
dieselbe Richtung: die Lage war besser als das Ticket dachte.

- **#358** war erledigt. Das Ticket beschreibt, dass dem Willehalm die
  Dreißiger-Gliederung fehlt. Gemessen: 467 `<div type="chapter" n>`, alle
  14.002 `<l>` darunter, auf `main`. Umgestellt am 09.08.
- **#308** Punkt 1 löst sich auf. Das Ticket fragt, ob für den „Schweizer
  Anonymus" ein Personeneintrag angelegt oder auf `person_anonym` umgebogen
  werden soll. Beides unnötig: `person_1772` existiert mit GND, und `works.xml`
  verweist für genau dieses Werk schon korrekt darauf. Nur der TEI-Header zeigt
  auf eine ID, die es nie gab.
- **#252** ist beantwortbar, und war es vermutlich schon damals. Der Kommentar
  vom 31.07. hält fest, eine Gegenprüfung sei unmöglich, weil für keinen
  betroffenen Text eine Linecode-Quelle vorliegt. Die 306 Dateien von #248 sind
  laut der verdichteten Historie oben (Eintrag 2026-07-30) am **Tag davor** ins
  Repo gekommen, darunter der größte betroffene Text. Die Feststellung war also
  schon bei ihrer Niederschrift überholt. Damit ist die Frage, die den Vorgang
  blockiert, an der Quelle entschieden: **OVG hat 135 leere `<l>` im TEI und
  135 Zeilen mit `...` in der Vorlage, Bijektion in beide Richtungen.** Über
  alle prüfbaren Texte 290 von 324 auflösbar, davon **jeder einzelne** ein
  Auslassungsmarker, kein Gegenbeleg.

**Die Lehre daraus ist eine Betriebsregel, keine Einsicht:** die Prämisse eines
blockierten Tickets altert, während das Ticket wartet, und sie altert
unbeobachtet, weil niemand ein wartendes Ticket nachmisst. Drei von zehn, und
in jedem Fall hätte die Person, die es abarbeitet, Arbeit gemacht, die schon
getan war, oder eine Entscheidung getroffen, die sich erübrigt hatte. **Vor der
Vorlage steht die Nachmessung, nicht die Zusammenfassung.**

**Rot: ich habe bei #358 gemessen, bevor ich den Kommentar gelesen habe.** Der
Kommentar vom 09.08. sagt im ersten Satz, dass der Willehalm umgestellt und
live ist. Ich hatte den Body gelesen, korpusweit gemessen, mich über den Fund
gefreut und erst danach die Kommentare geöffnet. Das ist genau die Regel, die
chsteiner in dieser Session viermal geschickt hat und die seit heute in
`CLAUDE.md` steht, und ich habe sie an dem Tag gebrochen, an dem sie
aufgeschrieben wurde. Der Schaden war nur Zeit; der Fund war schon dokumentiert.

**Und schlimmer: derselbe Kommentar beschreibt den Messfehler, den ich dann
gemacht habe.** Er hält fest, ein erster Lauf habe 48 Werke gemeldet, weil nur
`div[@n]` als Vorfahr geprüft wurde, während die Strophentexte ihre Nummer am
`lg[@n]` tragen. Mein Lauf prüfte ebenfalls nur `div[@n]` und meldete 146
Werke. Der Kommentar enthielt die Korrektur, bevor ich den Fehler machte.

**Rot: beinahe Textverlust gemeldet, der keiner war.** Beim #252-Abgleich fielen
fünf RVBR-Stellen auf, an denen die Vorlage einen echten Vers trägt und das TEI
eine leere Zeile. Vor dem Absenden in beiden Dateien nachgesehen: der Vers steht
eine Zeile weiter. RVBR nummeriert die `xml:id` fortlaufend statt nach
Linecode-Zeile, der Versatz war meiner. Die Meldung wäre ein Alarm über
Datenverlust in einem publizierten Korpus gewesen.

**Was die zehn Vorgänge jetzt brauchen**, ist durchweg weniger als vorher:

| Vorgang | vorher | nachher |
|---|---|---|
| #364 | 21 Einzelfälle philologisch entscheiden | 24 Einträge mechanisch, 11 Entscheidungen |
| #366 | sieben Lemmata von Grund auf finden | sechs Vorschläge bestätigen, einer offen |
| #228 | neun Zweifelsfälle einzeln | acht als ein Paket, zwei getrennt |
| #252 | eine Frage über 838 Stellen Unterschied | an der Quelle beantwortet |
| #308 | vier Punkte | eine Frage (zwei Namensformen) |
| #358 | „prüfen, ob weitere Werke betroffen" | elf Werke, keines mechanisch entscheidbar |

**Ein Nebenfund, der in keinem Ticket stand:** `haueßenn` in KDO sitzt auf
`lemma_2670` *hase*, dem Säugetier, in einem Rezept über Hausenblase. Dritte
Handschrift, derselbe Fehlertyp wie #363, Einzelfall (unter `lemma_2670` ist es
die einzige `hau-`artige Form, ein Token korpusweit).

**Zur Zahl der abgebrochenen CI-Läufe**, die im Eintrag darüber erst „zwei",
dann „drei" hiess: gemessen **16 von 25** abgeschlossenen `data-integrity`-Läufen
auf diesem Branch, verteilt über den ganzen Tag. Beide früheren Angaben waren
geschätzt aus dem, was mir aufgefallen war. Dazu der Lesefehler, der die Lehre
im selben Zug unterlaufen hat: drei Checks auf `success` und einer auf
`in_progress` sind bei `cancel-in-progress` null grüne Checks.

**Phase:** PR #398 grün, Bot-Runden 16 bis 19 ohne Befund. Die zehn Vorgänge
bleiben `auto:blocked`/`wait:kzw`: auch wo die Frage kleiner geworden ist, ist
sie eine Entscheidung.

---

## 2026-09-06 (Nacht) – Elf weitere Vorgänge, und der Rückstand ist zu einem Drittel gar keiner

Fortsetzung des Durchgangs durch die blockierten Tickets. Zusammen mit den zehn
vom Abend sind es **21 Vorgänge** (#364, #378, #308, #363, #366, #375, #267,
#252, #228, #358, #115, #371, #189, #369, #370, #250, #251, #169, #239, #118,
#271). Nichts an Korpus oder Authority geändert.

**Sieben davon sind faktisch erledigt und warten nur auf Abnahme:** #358
(Willehalm gegliedert), #250 (alle drei Punkte, Punkt 3 über
`isInNestedParallel`), #251 (beide Punkte, der Fokusverlust unbemerkt
miterledigt), #169 (die drei ausdrücklich offengelassenen Nebenbefunde sind
alle drei entfernt), #239, #308 Punkt 1, #252. Das ist ein Drittel des
Rückstands, der als offen geführt wird, ohne es zu sein.

**Die Diagnose vom Abend war zu freundlich.** Sie lautete: die Prämisse eines
blockierten Tickets altert, weil niemand ein wartendes Ticket nachmisst. Nach
elf weiteren Fällen ist das genauer zu fassen:

- Bei **#252** war die Prämisse schon **am Tag ihrer Niederschrift falsch**. Der
  Kommentar vom 31.07. hält fest, für keinen betroffenen Text liege eine
  Linecode-Quelle vor; die 306 Dateien von #248 kamen am **30.07.**, belegt an
  drei Stellen (`docs/LINECODE.md:176`, `sources/README.md:11`,
  `sources/INVENTAR-ARCHIV.md:20`), zwei davon ausserhalb des JOURNAL.
- Bei **#169** hat dieselbe Person die angekündigte Aufräumrunde gemacht und den
  Vermerk nicht nachgezogen.
- Bei **#251** führte der eigene Statuskommentar einen Punkt als offen, der im
  selben Zug miterledigt worden war.

**Der Rückstand ist also nicht liegengeblieben, er ist nur nicht abgeschrieben
worden.** Das ist ein anderes Problem und braucht ein anderes Mittel: nicht
mehr Arbeit, sondern eine Abschlusskontrolle.

### Fünf Abhängigkeiten, die in keinem Ticket standen

Das ist der eigentliche Ertrag, weil er die Reihenfolge festlegt:

1. **#364 erledigt 64 % von #115.** Die 109 Baseline-IDs sind 35 Lemma-IDs plus
   35 Senses **derselben** 35 Lemmata plus 39 Senses an vorhandenen Lemmata.
   Schnittmenge 35, in keiner Richtung ein Rest.
2. **#371 löst die Blockade in #369.** Dort steht, für das Ufer gebe es keine
   geübte Zuordnung. `lemma_5732` trägt aber selbst einen Gewässer-Sense
   (`_sense_9002`), und `stat` ist dort als `type_20161` längst belegt: kein
   neues Lemma, kein neuer Typ.
3. **#370 hängt für 23 Paare an #378.** Ein neuer Variantentyp setzt sich unter
   first-wins nur bei kleinerer Lemmanummer durch. Für 23 der 41 irreführenden
   Paare (299 Tokens) wäre eine Freigabe **wirkungslos**: die Daten entstünden,
   und die Suche benutzte sie nie.
4. **#363 und #366 müssen dieselbe Frage gemeinsam beantworten.** `hawssen
   platern` (MBS5) und `haueßenn plossenn` (KDO) sind dieselbe Konstruktion.
5. **#189 und #118 teilen sich 16 Texte.** Die Virgel `/`, in #189 ein
   Kodierungsfehler (7.912 Tokens als `<w>` statt `<pc>`), ist in #118 der
   einzige brauchbare Indikator: sie trifft **alle neun** Texte des Augsburger
   Drucks von 1476 und nennt sieben weitere derselben Machart. Wer sie in #189
   heilt, nimmt in #118 den Marker weg.

### Zwei Funde, die über das Vorbereiten hinausgehen

**#118 hat keine Datengrundlage.** Die Entscheidungsvorlage nennt als
erstrangige Quellen Header-Datierungen und `works.xml`. Gemessen: **0 von 667**
Headern tragen `origDate` oder `creation`, und in `works.xml` haben **9 von
584** Werken eine mittelalterliche Jahreszahl, alle neun `<imprint>` 1476,
derselbe Druck. Die Schwellenregel hat im Repositorium keinen Eingabewert. Das
Vorhaben ist zuerst ein Beschaffungsprojekt, und das gehört vor die vier
Fragen.

**#271 hat ein zweites Namenregister.** Der Vorgang fragt, ob weitere
existieren, und hält fest, das sei nicht geprüft. Über alle 305 Linecode-Dateien
mit einem Formkriterium gesucht: genau zwei erfüllen es. `tann.txt` (774
Einträge) gehört nicht zu TAN, sondern mit **695 von 774 (89 %)** zu **TKR**,
„Di tutsch kronik von Behem lant". Beide Texte sind böhmische Geschichtswerke
und haben denselben Auszeichnungsstand: 0 `nameRef`, 0 `<placeName>`, 6
`<persName>` nur im Header, 1 `<name>`. Das Material ist damit 1.242
Namenformen zu zwei Texten statt 468 zu einem.

### Rot: vier eigene Fehler, drei davon selbst gefunden

- **`stat` auf 0 gemeldet, gemessen sind 95.** Ich hatte die Frequenzliste auf
  die 400 häufigsten Formen gekürzt und danach mit `dict.get(form, 0)` gefragt.
  **Ein fehlender Schlüssel wurde so zu einer Messung.** Aufgefallen, weil #369
  im Kommentar 95 zurückgehaltene Fälle dokumentiert.
- **„Seit dem 18.08." war die Wurzel eines flachen Klons.** `git log -S` zeigte
  auf `2c23520`, 4.183 Dateien, 17,5 Mio. Zeilen, `.git/shallow` zeigt darauf.
  Aus dieser Historie ist kein Zugangsdatum ablesbar. Die richtige Antwort stand
  zwei Bildschirmseiten weiter oben in derselben Datei.
- **467 statt 468 Registereinträge**, weil die BOM der Datei die erste Zeile
  nicht auf mein Zeilenmuster passen liess. Das Ticket hatte recht.
- **Nach `componentSelection` gegriffen**, dem Namen aus dem *Vorschlag*, und
  daraus geschlossen, der Umbau sei nicht gemacht. Er heisst `componentPicked`.
  Ein Grep nach dem vorgeschlagenen Namen prüft, ob jemand den Vorschlag
  wörtlich umgesetzt hat, nicht ob das Problem gelöst ist.

Die ersten drei sind dieselbe Familie wie die sechs Bot-Befunde vom Nachmittag,
nur in neuen Kostümen: ein Default, der als Messung gelesen wird; ein
Artefakt der Werkzeugkette, das als Datum gelesen wird; ein Parserdetail, das
als Bestand gelesen wird. **Jedes Mal hat eine Kette aus Werkzeug und Annahme
eine Zahl geliefert, und ich habe die Zahl genommen statt die Kette.**

**Phase:** PR #398 grün, Bot-Runden 16 bis 21 ohne Befund. Alle 21 Vorgänge
bleiben `auto:blocked`: auch wo nur noch eine Abnahme aussteht, ist sie eine
Entscheidung.
