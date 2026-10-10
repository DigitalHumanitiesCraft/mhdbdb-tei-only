---
name: querschnitt-review-fallen
description: Wiederkehrende Denkfallen im Review: #397-Frage, Stempel, Zwilling, benannte Ausnahmen, tautologische Gates, Kopien einer Zahl, Laufplan und Auftrag als Behauptung, Fehlerjournal-Ketten
metadata:
  type: project
---
Verdichtet 08.10. und 10.10.2026.

**Was der Diff nicht zeigt**
- #397-Frage: was macht der Fix wahr, woran hing etwas am Gegenteil? Getroffen bei: verengter Thunk -> Werkzeugzustand; neuer Typ -> Wörterbuch-Flip; e() -> markup() -> Textkopie im Export; geteilter Hilfe-Abschnitt -> Deep-Links; gehaltene Waise -> hängender Zeiger; Stempel nur bei Ergebnis -> Rückweg aus „Kein Text ausgewählt" (#539). Auch Schreiber und Kopien suchen.
- **Das Dokument, das die Änderung motiviert, beschreibt oft das alte Verhalten** (#545: die Begriffshilfe-Download sagte „Das Suchfeld durchsucht Benennungen, nicht IDs"). Nach dem Auslöser im Issue greppen (`grep -rn "nicht IDs"`), nicht nur nach dem geänderten Bezeichner; generierte Artefakte haben einen Generator und ein Byte-Gate.
- Ein „der Konsistenz halber" mitgeänderter Nachbarzweig (Leer-Guard, Fehlerast) ist der Ort, an dem #397 trifft: unveränderte Geschwistermodule mit derselben Folge durchspielen, der Unterschied ist der Befund.
- Ein Stempel gehört dorthin, wo das Ergebnis entsteht, nicht wo es angezeigt wird.
- Verlängert ein PR eine Umformulierung: den Zwilling suchen (z. B. Docstring in text-normalizer.js und CONTRACTS.md §F). Ein verschobener Block ändert die Reihenfolge zu BEIDEN Nachbarn. Per-Schlüssel-A-Struktur unter Schlüssel B abgelegt: letzter gewinnt.
- Zeilenangabe als Beleg: Funktion benennen, Aufrufer greppen (toter Code sieht aus wie ein Beleg).
- Hebt ein PR eine Vertagung auf („X bleibt unaufgelöst" -> jetzt aufgelöst): nach dem verneinenden Satz suchen (`stay unresolved`, `for comments only`), nicht nach dem neuen Feldnamen (#270).
- **Ein Datenfix, der einen offenen Fall erledigt, lässt `docs/ROADMAP.md` und die Recherche-README unter `ingest/<fall>/` stehen** (#28/#216/#228). Token-ID, Lemma-ID und Sense-ID des Fixes über `docs/ROADMAP.md` und `ingest/*/README.md` greppen; JOURNAL und Kickoffs sind datiert und zählen nicht.
- **Eine Änderung an der Lemma-Auflösung (CONTRACTS §C) hat Python-Spiegel, die der Diff nicht anfasst** (#463, 10.10.2026): `scripts/audit/compare-findebuch-resolution-259.py` `resolve()` behauptet „in der Reihenfolge, in der sie produktiv laeuft", und seine Teilmengen/Kategorien bauen auf „Stufe 1 trifft immer"; dazu `docs/DATA-MODEL.md` „Stages are mutually exclusive, first match wins" und `docs/DEVELOPMENT.md` (Skripttabelle). `rg -n "def resolve|stage3|variantCandidates" scripts/` und `rg -i "first match wins|mutually exclusive" docs/`.
- **Ein Fix an einem Leser eines geänderten Felds: den Suchpfad aus dem Auftrag nicht übernehmen** (#452). Feldleser über `assets/` UND `playground/` greppen, und nicht nur nach Filtern auf dem Feld suchen, sondern nach Strings, in die es eingebaut wird (`text-comparison.js`: `t.author` in einer Optionsbeschriftung, der Tippfilter läuft auf dem Label). `rg "\bt\.author|text\.author"` plus Blick auf jeden Treffer in einem Template-String.

**Gates und Ausnahmen**
- Benannte Ausnahme: greift sie an der Bedingung oder am Namen? Am Namen schaltet sie die Prüfung ab.
- Prüft das Gate den Wert oder nur die Konsistenz zweier Stellen desselben Autors?
- Vor Klasse A über eine Invariante die Basis mitmessen: hält sie dort nicht, ist es Vorbestand.
- Zahlen stehen oft mehrfach: nach dem Gate-Lauf `grep -rn` über die alte Zahl; die Zweitzeile neben einem Anker selbst lesen.
- Harter Fehler NACH dem ersten Schreibvorgang ist kein Guard: die Zeile des `raise SystemExit` gegen die des ersten `write_text` halten (sync_tei_headers; `update-disambig-status-493.py`). Sonde: Kopie mit kaputter Liste, `--apply`, Hash der Datei vor/nach.

**Auftrag, JOURNAL, Threads**
- Zahlen und Daten im Auftrag stammen oft aus Verdichtungen: im Thread nachlesen (UTC beachten). „in #N beantwortet", „PR-Text mitgezogen" per API messen; JOURNAL-Sätze über künftige Kommentare sind Bedingungen. Wachsende Zahlen sind nur als damals <= jetzt prüfbar.
- Vorher-Zahlen von der Live-Seite gehören zum dort aufgelösten Lemma (Homograph `arm`). Personennamen gegen contributors.xml. Scope-Fragen vor dem Zählen klären.
- **„Ich habe selbst nachgemessen" im Auftrag ist eine Wiederholung meiner Methode, keine Gegenprobe** (#228, `.flex-shrink-0`, siehe querschnitt_tests). Einen eigenen Vorrundenbefund mit einer ANDEREN Messung prüfen (Kontextausgabe statt Zählung).
- **Der Laufplan ist Anforderungsquelle und bewegt sich nach dem Abzweig** (`docs/playbooks/kickoffs/<datum>-lauf.md`). `git diff <basis> origin/main` auf den Kickoff zeigt die Pflicht. Allaussagen im Diff gegen den Laufplan-Paragraphen halten, aus dem sie stammen. **Auch während der Runde:** am 10.10. (#564 R2) landete G4 (Budget-Untergrenze 0,1 statt 1 ms) auf origin/main zwischen Pinnen und Befund und widerlegte die Auftragsbehauptung „mindestens 1 ms vorgegeben"; vor dem Bericht erneut `git fetch` und `git log <basis>..origin/main -- docs/playbooks/kickoffs/`.
- **Nach einem Rebase zitieren JOURNAL und PR-Body oft den Vor-Rebase-SHA als Prüfstand** (#564 R3: `f55a133e0`, nur lokal). Gegenprobe: `gh api repos/<o>/<r>/commits/<sha>` gibt 422, Kontrollwert ein gepushter SHA desselben Zweigs; den Nachfolger zeigt `git range-diff`.
- Kickoffs und `docs/JOURNAL.md`-Einträge sind datierte Protokolle: zitieren sie eine inzwischen geänderte CLAUDE.md-Regel, ist das kein Befund.
- Die `CLAUDE.md` im Session-Kontext kann älter sein als HEAD. Jeden Verweis „steht in CLAUDE.md" mit `git grep` auf HEAD messen.
- **Eine Regel aus einem Issue-Kommentar hat eine zweite Quelle: die Label-Ereignisse der Autorin Sekunden danach** (`gh api .../issues/N/timeline --jq 'select(.event=="labeled" or .event=="unlabeled")'`). #378: KZW schrieb „Julia vorreihen" und setzte `wait:julia` **dazu**, ohne `wait:kzw` zu entfernen; „wait:julia statt wait:kzw" war damit widerlegt, obwohl der Wortlaut es zuließ.
- **Ein Zitat mit „mich"/„ich" gehört der Person, die der Auftrag als Sprecher nennt.** Eine Paraphrase kann das Pronomen still auf eine andere Person umhängen. Jede Zuschreibung gegen das Pronomen im Wortlaut halten.

**Fehlerjournal**
- `claude-code-setup/hooks/lehren-zaehlen.py` parst dieses Journal nicht (Format `### N. Rot:`): Ketten von Hand über den Absatz „Die Lehre, die nicht gegriffen hat". Nummern werden je Spur vorab reserviert: Sprünge sind kein Befund.
- Kette messen: `grep -n -o "Die letzte Zeile zu dieser Lehre ist Eintrag [0-9]*"` und rückwärts folgen. Der Satz kann umbrochen sein: Fenster lesen. Ein Zitat aus einem Issue-Kommentar über alle Kommentare des Tages greppen.
- „Die Aussetzung ist der Mechanismus": `wiederholte-fehler.md` verlangt den Satz in der betroffenen Regel (`grep -i ausgesetzt rules/<regel>.md rules/belege/<regel>.md`). **Eine fehlende Aussetzung ist nicht automatisch eine Lücke** (für `mengen.md` entschied `claude-code-setup` #66 am 18.09.2026, keine zu schreiben): vorher `gh issue view 53 66 64 --repo chsteiner/claude-code-setup --json body,comments`. Einträge auf dieselbe Lehre nicht nur über `mengen.md` greppen.
- Klassen für L3-Zeilen (`mengen.md`) in #66 (17.09.): A im Text nachzählbar, B nur am Sitzungsverlauf, C nur am Material, D Form allein. **„Rot N" dort sind Kommentare in `claude-code-setup` #29, nicht Einträge dieses Journals**; gezählt wird je Projekt.
- `hooks/mengenaussagen.sh` proben: JSON `{"tool_name":"Write","tool_input":{"file_path":"C:/x/n.md","content":"<Satz>"}}` per `printf` auf stdin, `MENGEN_LOG=<scratch>.jsonl`, `formen` lesen. Was eine Vorsession Christian sagte: `rg -n -o '"role":"user","content":"[^"]{1,120}'` auf der `.jsonl`.

**Dieses Memory** ist Eingabe für den nächsten Lauf, keine Messung: Zahlen daraus vor Gebrauch nachmessen.

**Auftrag nach Abzweigung (10.10.2026):** „origin/main hat seither nur X geändert“ im Auftrag ist eine Behauptung. `git log <Basis>..origin/main --stat` selbst; am 10.10. war der Satz veraltet, ein weiterer Merge (#451) war dazugekommen. Nach jedem Rebase die Gates (Versionen, `doc-count-audit --check`, Em-Dash) erneut fahren.
