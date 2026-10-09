---
name: querschnitt-review-fallen
description: Wiederkehrende Denkfallen im Review: #397-Frage, Stempel, Zwilling, benannte Ausnahmen, tautologische Gates, Kopien einer Zahl, Laufplan und Auftrag als Behauptung, Fehlerjournal-Ketten
metadata:
  type: project
---
Verdichtet 08.10.2026.

**Was der Diff nicht zeigt**
- #397-Frage: was macht der Fix wahr, woran hing etwas am Gegenteil? Getroffen bei: verengter Thunk -> Instanzzustand der Werkzeuge; neuer Typ -> Wörterbuch-Flip; Feld von e() auf markup() -> Textkopie im Export; Hilfe-Abschnitt geteilt -> Deep-Links `hilfe-*.html#`; gehaltene Waise -> hängender Zeiger; Stempel nur noch bei Ergebnis -> Rückweg aus „Kein Text ausgewählt" (#539: die vier Werkzeuge mit Suchfeld löschen im Leer-Guard, die drei ohne stempeln davor, gemessen d=0 gegen d=1). Nicht nur Prüfungen suchen, auch Schreiber und Kopien.
- **Das Dokument, das die Änderung motiviert, beschreibt oft das alte Verhalten** (#545: die Begriffshilfe-Download sagte „Das Suchfeld durchsucht Benennungen, nicht IDs", und der PR machte genau das falsch). Nach dem Auslöser im Issue greppen (`grep -rn "nicht IDs"`), nicht nur nach dem geänderten Bezeichner; generierte Artefakte haben einen Generator und ein Byte-Gate.
- Ein „der Konsistenz halber" mitgeänderter Nachbarzweig (Leer-Guard, Fehlerast) ist der Ort, an dem #397 trifft: unveränderte Geschwistermodule mit derselben Folge durchspielen, der Unterschied ist der Befund.
- Ein Stempel gehört dorthin, wo das Ergebnis entsteht, nicht wo es angezeigt wird.
- Verlängert ein PR eine Umformulierung: den Zwilling suchen (z. B. Docstring in text-normalizer.js und CONTRACTS.md §F). Ein verschobener Block ändert die Reihenfolge zu BEIDEN Nachbarn. Per-Schlüssel-A-Struktur unter Schlüssel B abgelegt: letzter gewinnt.
- Zeilenangabe als Beleg: Funktion benennen, Aufrufer greppen (toter Code sieht aus wie ein Beleg).
- Hebt ein PR eine Vertagung auf („X bleibt unaufgelöst" -> jetzt aufgelöst): nach dem verneinenden Satz suchen (`stay unresolved`, `for comments only`), nicht nach dem neuen Feldnamen (#270: 8 Stellen übrig).
- **Ein Datenfix, der einen offenen Fall erledigt, lässt `docs/ROADMAP.md` und die Recherche-README unter `ingest/<fall>/` stehen** (09.10.2026, #28/#216/#228: ROADMAP sagte „neither has happened yet" und „repair cases SAX_24200_4 still ours", die mur-228-README „Geändert ist nichts in authority-files/"). Token-ID, Lemma-ID und Sense-ID des Fixes über `docs/ROADMAP.md` und `ingest/*/README.md` greppen; JOURNAL und Kickoffs sind datiert und zählen nicht.

**Gates und Ausnahmen**
- Benannte Ausnahme: greift sie an der Bedingung oder am Namen? Am Namen schaltet sie die Prüfung ab.
- Prüft das Gate den Wert oder nur die Konsistenz zweier Stellen desselben Autors?
- Vor Klasse A über eine Invariante die Basis mitmessen: hält sie dort nicht, ist es Vorbestand.
- Zahlen stehen oft mehrfach: nach dem Gate-Lauf `grep -rn` über die alte Zahl; die Zweitzeile neben einem Anker selbst lesen.
- Harter Fehler NACH dem ersten Schreibvorgang ist kein Guard: die Zeile des `raise SystemExit` gegen die des ersten `write_text` halten (sync_tei_headers; `update-disambig-status-493.py`). Sonde: Kopie mit kaputter Liste, `--apply`, Hash der Datei vor/nach.

**Auftrag, JOURNAL, Threads**
- Zahlen und Daten im Auftrag stammen oft aus Verdichtungen: im Thread nachlesen (UTC beachten). „in #N beantwortet", „PR-Text mitgezogen" per API messen; JOURNAL-Sätze über künftige Kommentare sind Bedingungen. Wachsende Zahlen sind nur als damals <= jetzt prüfbar.
- Vorher-Zahlen von der Live-Seite gehören zum dort aufgelösten Lemma (Homograph `arm`). Personennamen gegen contributors.xml. Scope-Fragen vor dem Zählen klären.
- **„Ich habe selbst nachgemessen" im Auftrag ist eine Wiederholung meiner Methode, keine Gegenprobe** (#228): der Aufrufer bestätigte meinen Nullbefund zu `.flex-shrink-0` mit derselben Regex, beide waren falsch (siehe querschnitt_tests). Einen eigenen Vorrundenbefund mit einer ANDEREN Messung prüfen (Kontextausgabe statt Zählung).
- **Der Laufplan ist Anforderungsquelle und bewegt sich nach dem Abzweig** (`docs/playbooks/kickoffs/2026-10-02-lauf.md`: nach der Basis kamen zwei Commits, einer verlangte eine DEVELOPMENT.md-Zeile für eine neue Spec). `git diff <basis> origin/main` auf den Kickoff zeigt die Pflicht. Allaussagen im Diff gegen den Laufplan-Paragraphen halten, aus dem sie stammen.
- `docs/playbooks/kickoffs/<datum>-*.md` und `docs/JOURNAL.md`-Einträge sind datierte Protokolle: zitieren sie eine inzwischen geänderte CLAUDE.md-Regel, ist das kein Befund.
- Die `CLAUDE.md` im Session-Kontext kann älter sein als HEAD. Jeden Verweis „steht in CLAUDE.md" mit `git grep` auf HEAD messen.
- **Eine Regel aus einem Issue-Kommentar hat neben dem Wortlaut eine zweite Quelle: die Label-Ereignisse der Autorin Sekunden danach** (`gh api .../issues/N/timeline --jq 'select(.event=="labeled" or .event=="unlabeled")'`). Am 09.10.2026 (#378) schrieb KZW „Julia vorreihen" und setzte `wait:julia` **dazu**, ohne `wait:kzw` zu entfernen; die Auslegung „wait:julia statt wait:kzw" im Diff war damit an der Quelle widerlegt, obwohl der Kommentartext sie zuließ.
- **Ein Zitat mit „mich"/„ich" im Auftrag gehört der Person, die der Auftrag als Sprecher nennt.** Die Paraphrase im Diff kann das Pronomen stillschweigend auf eine andere Person umhängen (09.10.2026: „Das kostet mich nur sinnlos Zeit", Christian, wurde zu „costs KZW time"). Jede Zuschreibung gegen das Pronomen im Wortlaut halten.
- **Ein Fix an einem Leser eines geänderten Felds: den Suchpfad aus dem Auftrag nicht übernehmen.** #452 Runde 3 (09.10.2026): der Auftrag sagte „rg dataset.author in assets/ und testing/", der Zwilling der behobenen Hauptseiten-Textliste stand in `playground/js/playground-main.js:306` (RHB unter „konrad" weiter unfindbar). Feldleser über `assets/` UND `playground/` greppen.

**Fehlerjournal**
- `claude-code-setup/hooks/lehren-zaehlen.py` parst dieses Journal nicht (Format `### N. Rot:`): Ketten von Hand über den Absatz „Die Lehre, die nicht gegriffen hat". Nummern werden je Spur vorab reserviert: Sprünge sind kein Befund.
- Kette messen: `grep -n -o "Die letzte Zeile zu dieser Lehre ist Eintrag [0-9]*"` und von der neuen Zeile rückwärts folgen. Der Satz kann umbrochen sein, die Einzeilen-Regex trifft ihn dann nicht: Fenster lesen. Ein Zitat aus einem Issue-Kommentar über alle Kommentare des Tages greppen, nicht am Zeitstempel des Auftrags festmachen.
- „Die Aussetzung ist der Mechanismus": `wiederholte-fehler.md` verlangt den Satz in der betroffenen Regel (`grep -i ausgesetzt rules/<regel>.md rules/belege/<regel>.md`). **Eine fehlende Aussetzung ist nicht automatisch eine Lücke:** für `mengen.md` hat `claude-code-setup` #66 am 18.09.2026 entschieden, keine zu schreiben. Vor einem Aussetzungs-Befund `gh issue view 53 66 64 --repo chsteiner/claude-code-setup --json body,comments`. Einträge auf dieselbe Lehre nicht nur über `mengen.md` greppen.
- Klassen für L3-Zeilen (`mengen.md`) stehen in #66 (Kommentar 17.09. 10:06): A im Text nachzählbar, B nur am Sitzungsverlauf, C nur am Material, D Form allein. **„Rot N" dort sind Kommentare in `claude-code-setup` #29, nicht Einträge dieses Journals**; gezählt wird „je Projekt".
- `hooks/mengenaussagen.sh` in 10 s proben: JSON `{"tool_name":"Write","tool_input":{"file_path":"C:/x/n.md","content":"<Satz>"}}` per `printf` auf stdin, `MENGEN_LOG=<scratch>.jsonl`, `formen` in der Logzeile lesen. Was die Vorsession Christian gesagt hat, steht im Transkript (`rg -n -o '"role":"user","content":"[^"]{1,120}'` auf der `.jsonl`).

**Dieses Memory** ist Eingabe für den nächsten Lauf, keine Messung: Zahlen daraus vor Gebrauch nachmessen.
