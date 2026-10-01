# fable-reviewer Memory (mhdbdb-tei-only)

Verdichtet am 28.09.2026. Zahlen hier sind Eingabe, keine Messung.

- [Umgebung](querschnitt_umgebung.md): Worktree-Guard, Windows-Konsole, GitHub ohne gh, Cloud-Session
- [Git-Rezepte](querschnitt_git.md): Altstand per show/archive, Basis pruefen, range-diff, log -S, Blob-Hash
- [Messrezepte](querschnitt_messen.md): importlib in-process, Mutationsproben, gz/c14n-Vergleich, Zaehlfallen
- [Tests](querschnitt_tests.md): run-tests.js, --reporter-Falle, report.json, Playwright-Probe, Tailwind
- [Review-Denkfallen](querschnitt_review_fallen.md): #397-Frage, Stempel, Ausnahmen, Zahlenkopien, Auftrag pruefen
- [Gates und CI](gates_und_ci.md): doc-count-audit-Luecken, Einzelgates, validate-corpus parallel (fail-fast, Speicher), extract-variants, issue-matrix, main-Schutz, Review-Bot-Log (was sanitize versteckt, PR-Workflow-Datei, Tokenmaskierung), Body-Syntaxfehler nach tei_header, Parallel-Gegenprobe, CRLF im Worktree
- [TEI-Korpus](korpus_tei.md): was der Korpus-Index liest, pc/caesura/gap, Vers/Prosa, WZB, Header
- [Lexikon und Variants](lexikon_variants.md): first-wins-Flip, sense/@ana ohne Konsument, Ziffernlemmata
- [Authority-Dateien](authority_dateien.md): concepts kein Baum, zwei genre-Felder, Schema an vier Orten, Siglen
- [Header-Spiegel](header_spiegel.md): Header als Kopie ohne Leser, sync_tei_headers-Fallen, Zotero-Sync, particDesc 670 seit #444 (Altstand 671), tei_header
- [Playground/Frontend](playground_frontend.md): Hash-Pfad, Multi-Lemma, Nummernpfad #467 und Ziffernlemmata, Werkzeugzustand #204, Zaehlungen
- [Naming #420](naming_420.md): Nachbau, Blob-Hash, Lindas Daten, Zitationskopien, JS-Rundung
- [Pruefseiten](pruefseiten.md): Zitat-Gate, markup vs. e(), Generator-Laufzeit, datengebundene Specs
- [Findebuch-Dump #259](project_findebuch_dump_259.md): gram/hi in sublemma, Trennstrich am lb, keine Wortformen
- [find-mentions #476](projekt_find_mentions_476.md): Probe ohne Netz, disjunkte Kandidatentitel, Exit-Pfade
- [Begriffshilfe #498](projekt_begriffshilfe_498.md): Korpusdurchgang cachen, Belege unter Begriff vs. gesamt, Kontrollwerte Aufmerksamkeit, Freshness-Gate und `--out`-Gegenprobe, Nummernkopplung DEVELOPMENT/Workflow
