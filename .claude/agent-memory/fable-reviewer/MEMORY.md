# fable-reviewer Memory (mhdbdb-tei-only)

Verdichtet am 02.10.2026. Zahlen hier sind Eingabe, keine Messung.

- [Umgebung](querschnitt_umgebung.md): Worktree-Guard, Windows, GitHub ohne gh, Cloud-Session
- [Git-Rezepte](querschnitt_git.md): Altstand, Basis prüfen, range-diff, log -S, Blob-Hash, EOL-Proben im Sparse-Klon (status M bei leerem diff), Squash zählen per merge_commit_sha, Stack nach Squash (rebase --onto, Auto-Delete retargetet)
- [Messrezepte](querschnitt_messen.md): importlib in-process, Mutationsproben, Zählfallen, find-mentions-Probe
- [Tests](querschnitt_tests.md): run-tests.js, Port, report.json, Playwright-Probe, Tailwind
- [Review-Denkfallen](querschnitt_review_fallen.md): #397-Frage, Gates, Auftrag und Laufplan prüfen
- [Gates und CI](gates_und_ci.md): was jedes Gate nicht prüft, Review-Bot, main-Schutz
- [TEI-Korpus](korpus_tei.md): Korpus-Index, pc/caesura, Vers/Prosa, WZB, Header, Findebuch-Dump #259
- [Lexikon und Variants](lexikon_variants.md): Vorschrift B, Dangling-Filter, sense/@ana, Wortbestandteile #228, Ziffernlemmata
- [Authority-Dateien](authority_dateien.md): concepts kein Baum, genre-Felder, Schema an vier Orten, Siglen
- [Header-Spiegel](header_spiegel.md): Header als Kopie, sync_tei_headers-Fallen, particDesc-Zählung
- [Playground/Frontend](playground_frontend.md): Hash-Pfad, Multi-Lemma, Nummernpfad, Werkzeugzustand
- [Fremdindizes](fremdindizes.md): Naming #420 (Nachbau, Term-Perspektive) und Pferde #193 (zwei Vers-Einheiten)
- [Prüfseiten](pruefseiten.md): Zitat-Gate, markup vs. e(), Generator-Laufzeit, datengebundene Specs
- [Begriffshilfe #498](projekt_begriffshilfe_498.md): Korpusdurchgang cachen, Belege unter Begriff vs. gesamt, Freshness-Gate
- [Parzival-Bücher #358](projekt_parzival_buecher_358.md): OCR-Messrezept Bartsch/Martin, Fallen (VIII = 398,1, Redezeichen-pc, TEI-gegen-TEI-Vergleich)
- [WZB @corresp #370](projekt_370_corresp.md): ANLEGEN-Falle, zwei Tokenzählungen, Messrezept alt/neu, mitalternde Nachbarn
- [#526 Breve/Makron](projekt_526_breve_makron.md): Tafelskript auf Kopie (parents[3]), Guard-Grenzen (Regel V), CONTRACTS §A zählt Unannotiertes als Invariante
- [Warm-Context #488](projekt_warm_context_488.md): Fixture-Reihenfolge, Worker-Context erbt use+Timeout 0, Probe ohne Server, Worker-Stop nach Fehlschlag, App-Storage-Schlüssel, Nachbarn (DEVELOPMENT:188)
