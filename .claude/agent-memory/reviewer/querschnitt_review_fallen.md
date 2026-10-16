---
name: querschnitt-review-fallen
description: Wiederkehrende Denkfallen im Review: #397-Frage, Zwillinge und Kopien, benannte Ausnahmen, tautologische Gates, Laufplan und Auftrag als Behauptung, Fehlerjournal-Ketten
metadata:
  type: project
---
Verdichtet 14.10. und 15.10.2026. Dieses Memory ist Eingabe, keine Messung: Zahlen daraus vor Gebrauch nachmessen.

**Was der Diff nicht zeigt**
- #397-Frage: was macht der Fix wahr, woran hing etwas am Gegenteil? Auch Schreiber und Kopien suchen. Bringt ein Diff einen neuen Dateityp, die Endungslisten der Gates greppen und prüfen, ob der neue Fall den Zweig erreicht (#93: ein `continue` vor der Größenprobe machte `svg` im Regex tot).
- **Das Dokument, das die Änderung motiviert, beschreibt oft das alte Verhalten** (#545). Nach dem Auslöser im Issue greppen (`grep -rn "nicht IDs"`), nicht nur nach dem Bezeichner; generierte Artefakte haben Generator und Byte-Gate.
- Ein „der Konsistenz halber" mitgeänderter Nachbarzweig (Leer-Guard, Fehlerast) ist der Ort, an dem #397 trifft: unveränderte Geschwistermodule mit derselben Folge durchspielen.
- **Ein Datenfix, der einen offenen Fall erledigt, lässt `docs/ROADMAP.md` und die Recherche-README unter `ingest/<fall>/` stehen** (#28/#216/#228). Token-, Lemma- und Sense-ID über beide greppen; JOURNAL und Kickoffs sind datiert und zählen nicht.
- **Eine Änderung an der Lemma-Auflösung (CONTRACTS §C) hat Python-Spiegel, die der Diff nicht anfasst:** `scripts/audit/compare-findebuch-resolution-259.py` `resolve()`, `docs/DATA-MODEL.md` („Stages are mutually exclusive, first match wins"), `docs/DEVELOPMENT.md`. `rg -n "def resolve|stage3|variantCandidates" scripts/`, `rg -i "first match wins|mutually exclusive" docs/`.
- **Fix an einem Leser eines geänderten Felds: den Suchpfad aus dem Auftrag nicht übernehmen** (#452). Feldleser über `assets/` UND `playground/` greppen, auch nach Strings, in die es eingebaut wird (`rg "\bt\.author|text\.author"`, jeden Treffer in einem Template-String ansehen).

**Gates und Ausnahmen**
- Benannte Ausnahme: greift sie an der Bedingung oder am Namen? Am Namen schaltet sie die Prüfung ab.
- Prüft das Gate den Wert oder nur die Konsistenz zweier Stellen desselben Autors?
- Vor Klasse A über eine Invariante die Basis mitmessen: hält sie dort nicht, ist es Vorbestand.
- Zahlen stehen oft mehrfach: nach dem Gate-Lauf `grep -rn` über die alte Zahl; die Zweitzeile neben einem Anker selbst lesen.
- Harter Fehler NACH dem ersten Schreibvorgang ist kein Guard: Zeile des `raise SystemExit` gegen die des ersten `write_text` halten (sync_tei_headers; `update-disambig-status-493.py`). Sonde: Kopie mit kaputter Liste, `--apply`, Hash vor/nach.

**Auftrag, JOURNAL, Threads**
- Zahlen und Daten im Auftrag stammen oft aus Verdichtungen: im Thread nachlesen (UTC beachten); wachsende Zahlen nur als damals <= jetzt prüfbar. Vorher-Zahlen von der Live-Seite gehören zum dort aufgelösten Lemma (Homograph `arm`). Personennamen gegen contributors.xml.
- **„Ich habe selbst nachgemessen" im Auftrag wiederholt meine Methode, keine Gegenprobe** (#228). Einen eigenen Vorrundenbefund mit einer ANDEREN Messung prüfen (Kontextausgabe statt Zählung).
- **Ein Kontextfenster, das am Beleg beginnt, beantwortet keine Herkunftsfrage** (#461, 16.10.): „Herkunft des Knochens nicht genannt" für die Würfel in DRE V. 177–181 stammte aus einem Fenster V. 137–217; die Herkunft steht in V. 36–37 und 117–128 (Stockzähne des Ritters). Bei „wessen/woraus" das Fenster am Episodenanfang (Figur, Gegenstand) öffnen und den Beleg als Ende nehmen; Zeilen per `<l n=…>` als Klartext ausgeben, nicht das `[[…]]`-Fenster der Belegtabelle lesen. Ein zutreffendes Ergebnis mit falscher Begründung ist ein B-Befund an README und Tabelle, kein A.
- **Der Laufplan ist Anforderungsquelle und bewegt sich nach dem Abzweig** (`docs/playbooks/kickoffs/<datum>-lauf.md`). `git diff <basis> origin/main` auf den Kickoff zeigt die Pflicht; Allaussagen im Diff gegen den Paragraphen halten. **Auch während der Runde:** vor dem Bericht erneut `git fetch` und `git log <basis>..origin/main -- docs/playbooks/kickoffs/`.
- **Ein Datum im Diff und im Auftrag gegen drei Uhren halten:** `git log -1 --format=%ad --date=iso HEAD`, `date`, Serverzeit `curl -sI https://api.github.com/ | grep -i '^date'`, dazu das Ereignisdatum (`gh pr view N --json mergedAt`).
- **„origin/main hat seither nur X geändert" im Auftrag ist eine Behauptung:** `git log <Basis>..origin/main --stat` selbst. Nach jedem Rebase die Gates (Versionen, `doc-count-audit --check`, Em-Dash) erneut fahren.
- **Nach einem Rebase zitieren JOURNAL und PR-Body oft den Vor-Rebase-SHA als Prüfstand.** Gegenprobe: `gh api repos/<o>/<r>/commits/<sha>` gibt 422, Kontrollwert ein gepushter SHA desselben Zweigs; den Nachfolger zeigt `git range-diff`.
- Kickoffs und `docs/JOURNAL.md`-Einträge sind datierte Protokolle: zitieren sie eine inzwischen geänderte CLAUDE.md-Regel, ist das kein Befund. Die `CLAUDE.md` im Session-Kontext kann älter sein als HEAD: jeden Verweis „steht in CLAUDE.md" mit `git grep` auf HEAD messen.
- **Eine Regel aus einem Issue-Kommentar hat eine zweite Quelle: die Label-Ereignisse der Autorin Sekunden danach** (`gh api .../issues/N/timeline --jq 'select(.event=="labeled" or .event=="unlabeled")'`). (#378: „Julia vorreihen" hieß `wait:julia` **dazu**, nicht statt `wait:kzw`.)
- **Ein Zitat mit „mich"/„ich" gehört dem Sprecher, den der Auftrag nennt.** Eine Paraphrase kann das Pronomen still umhängen; jede Zuschreibung gegen das Pronomen im Wortlaut halten.
- **Eine Belegzeile, deren Befehl ein Zitat findet, belegt das Zitat, nicht die Tatsache:** ist die Quelle ein Abschlusskommentar oder eine Verdichtung, den Primärkommentar der Entscheidung öffnen (`claude-code-setup` #66 „zu reizbar“ gegen #53 „nicht sinnvoll“).

**Prüfmaterial für KZW (Prüflisten, Vorschläge)**
- **„Handarbeit", „Handurteil", „manuell" heißen für die Leserin „ein Mensch hat es gelesen".** Stammen Urteile von einem Agenten, widerspricht das Wort dem Satz „maschinell vorbereitet" daneben. `grep -n -i "hand\|manuell"` über README, Docstrings und Spaltennamen; Docstrings brechen „von\nHand" um.
- **Eine Regel, die eine Vorsortierung beschreibt, gegen die Zusammenfassung des Laufs halten**, die die tatsächlich verwendeten Lemmata ausgibt; dann Mutationsprobe auf einer Kopie im Scratchpad (Konstante ersetzen, Original und Kopie parallel in leere Ordner, `diff` der Zusammenfassungen).
- **Bekommt eine Teilmenge der Skripte einen Guard, schreibt der Fix den Sammelsatz über die ganze Tabelle** („jedes Skript verlangt einen Ausgabeordner außerhalb des Repos"; 16.10., `scripts/review/README.md`: `ana-603.py` und `stichprobe2-603.py` ohne Guard, die README daneben ruft `ana-603.py` mit einem Repo-Ordner). Je Tabellenzeile `grep -c realpath <skript>`; dazu `temp` selbst gegen „unter temp/" proben, die Guards unterscheiden sich darin.

**Fehlerjournal**
- `claude-code-setup/hooks/lehren-zaehlen.py` parst dieses Journal nicht (Format `### N. Rot:`): Ketten von Hand über den Absatz „Die Lehre, die nicht gegriffen hat". Nummern werden je Spur vorab reserviert: Sprünge sind kein Befund. Kette messen: `grep -n -o "Die letzte Zeile zu dieser Lehre ist Eintrag [0-9]*"`, rückwärts folgen; der Satz kann umbrochen sein.
- **Ein Kettenzeiger, der sich selbst „ungeprüft" nennt, ist eine Behauptung wie jede andere** (138, 16.10.): „letzte Zeile ist 61" stand da, `grep -n "dateisuche\.md" fehlerjournal.md` nennt 43, 48, 58, 61, 65, 70, 71, 95, 105, 106, 119, und 70 zitiert den Lehrsatz von 61 wörtlich. Die Bullets einer Regeldatei (Zuschnitt, Kontrollwert) ziehen 65 und 70 zu einer Kette zusammen; ab der dritten Zeile (48) ist der Mechanismus fällig, und für den Zuschnitt steht die Aussetzung im Fuß von `dateisuche.md`. Ein „Kein neuer Mechanismus: ich mache künftig X" ist eine Gewohnheit, nicht die Aussetzung (so sagt es Eintrag 48 selbst).
- Ein JOURNAL-Eintrag, der vor der letzten Runde geschrieben wird, trägt Platzhalter („Runde 3: siehe unten" ohne Text darunter): melden, sonst steht er nach dem Push als Behauptung ohne Gegenstand.
- Aussetzung statt Mechanismus: `wiederholte-fehler.md` verlangt den Satz in der betroffenen Regel (`grep -i ausgesetzt rules/<regel>.md rules/belege/<regel>.md`). Eine fehlende Aussetzung ist nicht automatisch eine Lücke (für `mengen.md` entschied `claude-code-setup` #66, keine zu schreiben; vorher dessen #53, #66, #64 samt Kommentaren lesen). „Rot N“ dort sind Kommentare in dessen #29, nicht Einträge dieses Journals.
- `hooks/mengenaussagen.sh` proben: JSON `{"tool_name":"Write","tool_input":{"file_path":"C:/x/n.md","content":"<Satz>"}}` per `printf` auf stdin, `MENGEN_LOG=<scratch>.jsonl`, `formen` lesen.
