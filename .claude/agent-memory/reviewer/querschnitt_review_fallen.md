---
name: querschnitt-review-fallen
description: Wiederkehrende Denkfallen im Review: #397-Frage, Stempel, Zwilling, benannte Ausnahmen, tautologische Gates, Kopien einer Zahl, Laufplan und Auftrag als Behauptung, Fehlerjournal-Ketten
metadata:
  type: project
---
Verdichtet 08. und 10.10.2026. Dieses Memory ist Eingabe, keine Messung: Zahlen daraus vor Gebrauch nachmessen.

**Was der Diff nicht zeigt**
- #397-Frage: was macht der Fix wahr, woran hing etwas am Gegenteil? Getroffen bei: verengter Thunk -> Werkzeugzustand; neuer Typ -> Wörterbuch-Flip; e() -> markup() -> Textkopie im Export; geteilter Hilfe-Abschnitt -> Deep-Links; gehaltene Waise -> hängender Zeiger; Stempel nur bei Ergebnis -> Rückweg aus „Kein Text ausgewählt" (#539). Auch Schreiber und Kopien suchen.
- **Das Dokument, das die Änderung motiviert, beschreibt oft das alte Verhalten** (#545). Nach dem Auslöser im Issue greppen (`grep -rn "nicht IDs"`), nicht nur nach dem Bezeichner; generierte Artefakte haben Generator und Byte-Gate.
- Ein „der Konsistenz halber" mitgeänderter Nachbarzweig (Leer-Guard, Fehlerast) ist der Ort, an dem #397 trifft: unveränderte Geschwistermodule mit derselben Folge durchspielen.
- **Ein Datenfix, der einen offenen Fall erledigt, lässt `docs/ROADMAP.md` und die Recherche-README unter `ingest/<fall>/` stehen** (#28/#216/#228). Token-, Lemma- und Sense-ID über beide greppen; JOURNAL und Kickoffs sind datiert und zählen nicht.
- **Eine Änderung an der Lemma-Auflösung (CONTRACTS §C) hat Python-Spiegel, die der Diff nicht anfasst:** `scripts/audit/compare-findebuch-resolution-259.py` `resolve()` (Reihenfolge, „Stufe 1 trifft immer“), `docs/DATA-MODEL.md` („Stages are mutually exclusive, first match wins“), `docs/DEVELOPMENT.md`. `rg -n "def resolve|stage3|variantCandidates" scripts/`, `rg -i "first match wins|mutually exclusive" docs/`.
- **Fix an einem Leser eines geänderten Felds: den Suchpfad aus dem Auftrag nicht übernehmen** (#452). Feldleser über `assets/` UND `playground/` greppen, auch nach Strings, in die es eingebaut wird (`rg "\bt\.author|text\.author"`, jeden Treffer in einem Template-String ansehen).

**Gates und Ausnahmen**
- Benannte Ausnahme: greift sie an der Bedingung oder am Namen? Am Namen schaltet sie die Prüfung ab.
- Prüft das Gate den Wert oder nur die Konsistenz zweier Stellen desselben Autors?
- Vor Klasse A über eine Invariante die Basis mitmessen: hält sie dort nicht, ist es Vorbestand.
- Zahlen stehen oft mehrfach: nach dem Gate-Lauf `grep -rn` über die alte Zahl; die Zweitzeile neben einem Anker selbst lesen.
- Harter Fehler NACH dem ersten Schreibvorgang ist kein Guard: Zeile des `raise SystemExit` gegen die des ersten `write_text` halten (sync_tei_headers; `update-disambig-status-493.py`). Sonde: Kopie mit kaputter Liste, `--apply`, Hash vor/nach.

**Auftrag, JOURNAL, Threads**
- Zahlen und Daten im Auftrag stammen oft aus Verdichtungen: im Thread nachlesen (UTC beachten); wachsende Zahlen nur als damals <= jetzt prüfbar.
- Vorher-Zahlen von der Live-Seite gehören zum dort aufgelösten Lemma (Homograph `arm`). Personennamen gegen contributors.xml.
- **„Ich habe selbst nachgemessen" im Auftrag wiederholt meine Methode, keine Gegenprobe** (#228, `.flex-shrink-0`, querschnitt_tests). Einen eigenen Vorrundenbefund mit einer ANDEREN Messung prüfen (Kontextausgabe statt Zählung).
- **Der Laufplan ist Anforderungsquelle und bewegt sich nach dem Abzweig** (`docs/playbooks/kickoffs/<datum>-lauf.md`). `git diff <basis> origin/main` auf den Kickoff zeigt die Pflicht; Allaussagen im Diff gegen den Paragraphen halten, aus dem sie stammen. **Auch während der Runde:** eine Änderung kann zwischen Pinnen und Befund landen und eine Auftragsbehauptung widerlegen; vor dem Bericht erneut `git fetch` und `git log <basis>..origin/main -- docs/playbooks/kickoffs/`.
- **„origin/main hat seither nur X geändert" im Auftrag ist eine Behauptung:** `git log <Basis>..origin/main --stat` selbst. Nach jedem Rebase die Gates (Versionen, `doc-count-audit --check`, Em-Dash) erneut fahren.
- **Nach einem Rebase zitieren JOURNAL und PR-Body oft den Vor-Rebase-SHA als Prüfstand.** Gegenprobe: `gh api repos/<o>/<r>/commits/<sha>` gibt 422, Kontrollwert ein gepushter SHA desselben Zweigs; den Nachfolger zeigt `git range-diff`.
- Kickoffs und `docs/JOURNAL.md`-Einträge sind datierte Protokolle: zitieren sie eine inzwischen geänderte CLAUDE.md-Regel, ist das kein Befund. Die `CLAUDE.md` im Session-Kontext kann älter sein als HEAD: jeden Verweis „steht in CLAUDE.md" mit `git grep` auf HEAD messen.
- **Eine Regel aus einem Issue-Kommentar hat eine zweite Quelle: die Label-Ereignisse der Autorin Sekunden danach** (`gh api .../issues/N/timeline --jq 'select(.event=="labeled" or .event=="unlabeled")'`). #378: KZW schrieb „Julia vorreihen" und setzte `wait:julia` **dazu**, ohne `wait:kzw` zu entfernen; „statt" war damit widerlegt.
- **Ein Zitat mit „mich"/„ich" gehört dem Sprecher, den der Auftrag nennt.** Eine Paraphrase kann das Pronomen still umhängen; jede Zuschreibung gegen das Pronomen im Wortlaut halten.

**Fehlerjournal**
- `claude-code-setup/hooks/lehren-zaehlen.py` parst dieses Journal nicht (Format `### N. Rot:`): Ketten von Hand über den Absatz „Die Lehre, die nicht gegriffen hat". Nummern werden je Spur vorab reserviert: Sprünge sind kein Befund.
- Kette messen: `grep -n -o "Die letzte Zeile zu dieser Lehre ist Eintrag [0-9]*"`, rückwärts folgen. Der Satz kann umbrochen sein: Fenster lesen.
- Aussetzung statt Mechanismus: `wiederholte-fehler.md` verlangt den Satz in der betroffenen Regel (`grep -i ausgesetzt rules/<regel>.md rules/belege/<regel>.md`). **Eine fehlende Aussetzung ist nicht automatisch eine Lücke** (für `mengen.md` entschied `claude-code-setup` #66, keine zu schreiben): vorher `gh issue view 53 66 64 --repo chsteiner/claude-code-setup --json body,comments`. Die „Rot N“ in dessen #66 sind Kommentare in dessen #29, nicht Einträge dieses Journals; gezählt wird je Projekt.
- `hooks/mengenaussagen.sh` proben: JSON `{"tool_name":"Write","tool_input":{"file_path":"C:/x/n.md","content":"<Satz>"}}` per `printf` auf stdin, `MENGEN_LOG=<scratch>.jsonl`, `formen` lesen.
