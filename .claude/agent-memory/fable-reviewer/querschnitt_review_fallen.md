---
name: querschnitt-review-fallen
description: Wiederkehrende Denkfallen im Review: #397-Frage, Stempel, Zwilling, benannte Ausnahmen, tautologische Gates, Kopien einer Zahl, Laufplan und Auftrag als Behauptung
metadata:
  type: project
---
Verdichtet 02.10.2026.

**Was der Diff nicht zeigt**
- #397-Frage: was macht der Fix wahr, woran hing etwas am Gegenteil? Getroffen bei: verengter Thunk -> Instanzzustand der Werkzeuge; neuer Typ -> Wörterbuch-Flip; Feld von e() auf markup() -> Textkopie im Export; Hilfe-Abschnitt geteilt -> Deep-Links `hilfe-*.html#`; gehaltene Waise -> hängender Zeiger. Nicht nur Prüfungen suchen, auch Schreiber und Kopien.
- Ein Stempel gehört dorthin, wo das Ergebnis entsteht, nicht wo es angezeigt wird.
- Verlängert ein PR eine Umformulierung: den Zwilling suchen. Ein verschobener Block ändert die Reihenfolge zu BEIDEN Nachbarn. Per-Schlüssel-A-Struktur unter Schlüssel B abgelegt: letzter gewinnt.
- Zeilenangabe als Beleg: Funktion benennen, Aufrufer greppen (toter Code sieht aus wie ein Beleg).
- Hebt ein PR eine Vertagung auf („X bleibt unaufgelöst" -> jetzt aufgelöst): nach dem verneinenden Satz suchen (`stay unresolved`, `for comments only`), nicht nach dem neuen Feldnamen; der Autor grept den neuen Namen und trifft die Negation nie (#270: 8 Stellen übrig, darunter CONTRACTS §G und TEI-MODEL-AUTH-FILES §3.1).

**Gates und Ausnahmen**
- Benannte Ausnahme: greift sie an der Bedingung oder am Namen? Am Namen schaltet sie die Prüfung ab.
- Prüft das Gate den Wert oder nur die Konsistenz zweier Stellen desselben Autors?
- Vor Klasse A über eine Invariante die Basis mitmessen: hält sie dort nicht, ist es Vorbestand.
- Zahlen stehen oft mehrfach: nach dem Gate-Lauf `grep -rn` über die alte Zahl; die Zweitzeile neben einem Anker selbst lesen.
- Harter Fehler NACH dem ersten Schreibvorgang ist kein Guard: die Zeile des `raise SystemExit` gegen die des ersten `write_text` halten (sync_tei_headers; `update-disambig-status-493.py`: TEI geschrieben, CSV-Prüfung danach, Wiederholungslauf sagt „nichts zu ändern"). Sonde: Kopie mit kaputter Liste, `--apply`, Hash der Datei vor/nach.

**Auftrag, JOURNAL, Threads**
- Zahlen und Daten im Auftrag stammen oft aus Verdichtungen: im Thread nachlesen (UTC beachten).
- „in #N beantwortet", „PR-Text mitgezogen" per API messen; JOURNAL-Sätze über künftige Kommentare sind Bedingungen. Wachsende Zahlen sind nur als damals <= jetzt prüfbar.
- Vorher-Zahlen von der Live-Seite gehören zum dort aufgelösten Lemma (Homograph `arm`). Personennamen gegen contributors.xml. Scope-Fragen vor dem Zählen klären.
- **„Ich habe selbst nachgemessen" im Auftrag ist eine Wiederholung meiner Methode, keine Gegenprobe** (#228 Runde 2): der Aufrufer bestätigte meinen Nullbefund zu `.flex-shrink-0` mit derselben Regex, beide waren falsch (siehe querschnitt_tests). Einen eigenen Vorrundenbefund mit einer ANDEREN Messung prüfen (Kontextausgabe statt Zählung).
- **Der Laufplan ist Anforderungsquelle und bewegt sich nach dem Abzweig** (`docs/playbooks/kickoffs/2026-10-02-lauf.md`: nach der Basis zwei Commits, einer verlangte eine DEVELOPMENT.md-Zeile für eine neue Spec, sonst `check-doc-inventories.py` rot). Der Auftrag nannte die alte Basis; `git diff <basis> origin/main` auf den Kickoff zeigt die Pflicht. Bei Laufplan-Spuren immer so messen.
- Allaussagen im Diff gegen den Laufplan-Paragraphen halten, aus dem sie stammen (B2: §4.2 nannte drei Bücher, FEATURES machte „the books“ daraus).
- `docs/playbooks/kickoffs/<datum>-*.md` sind datierte Prompts: zitieren sie eine inzwischen geänderte CLAUDE.md-Regel, ist das kein Befund (07.10.: datenlauf :222 zitiert die alte Commit-Freigabe von vor dem 07.10.).
- Die `CLAUDE.md` im Session-Kontext kann älter sein als HEAD. Jeden Verweis „steht in CLAUDE.md" mit `git grep` auf HEAD messen, nie aus dem Kontext bestätigen oder widerlegen.

**Fehlerjournal**
- `claude-code-setup/hooks/lehren-zaehlen.py` parst dieses Journal nicht (Format `### N. Rot:`): Ketten von Hand über den Absatz „Die Lehre, die nicht gegriffen hat". Nummern werden je Spur vorab reserviert: Sprünge sind kein Befund.
- Kette messen: `grep -n -o "Die letzte Zeile zu dieser Lehre ist Eintrag [0-9]*"` und von der neuen Zeile rückwärts folgen (Eintrag 106 am 07.10.: 106→105→95→71→70→65, „mindestens die vierte" war damit wahr); der Satz ist bei 71 umbrochen, die Einzeilen-Regex traf ihn nicht, also Fenster lesen. Ein Zitat aus einem Issue-Kommentar über alle Kommentare des Tages greppen, nicht am Zeitstempel des Auftrags festmachen: der Auftrag nannte ~15:56, der Satz stand im Kommentar 17:07.
- „Die Aussetzung ist der Mechanismus" gegen die Regel messen: `wiederholte-fehler.md` verlangt den Satz in der betroffenen Regel. `grep -i ausgesetzt rules/<regel>.md rules/belege/<regel>.md`; am 07.10. trug nur `agentenbefunde.md` einen, `mengen.md` keinen. **Eine fehlende Aussetzung ist nicht automatisch eine Lücke:** für `mengen.md` hat `claude-code-setup` #66 am 18.09.2026 entschieden, keine zu schreiben (Runde 1 am 07.10. hat das als Lücke gemeldet, ohne den Vorgang zu lesen). Vor einem Aussetzungs-Befund `gh issue view 53 66 64 --repo chsteiner/claude-code-setup --json body,comments`. Einträge auf dieselbe Lehre nicht nur über `mengen.md` greppen, Eintrag 22 nennt sie als `feedback_aussage_neben_ihrer_menge`.
- Klassen für L3-Zeilen (`mengen.md`) stehen in #66, Kommentar 17.09. 10:06: A im Text nachzählbar, B nur am Sitzungsverlauf („ob ein Befehl lief und woher die Zahl stammt"), C nur am Material („gemessen und richtig, falsch ist, worauf sie sich bezieht"), D Form allein. „Richtig gemessen, falsch bezogen" ist C, nicht B; B liegt als Bauart in #64, C ist laut Abschluss 18.09. „unter der Dreierschwelle" mit Rot 57 und Rot 2. **„Rot N" dort sind Kommentare in `claude-code-setup` #29 (Zähler 1–75 jenes Repos), nicht Einträge dieses Journals**: mhdbdb `### 57.` ist eigene-quellen, `### 2.` der Freeze. Eine mhdbdb-Zeile zählt nach `wiederholte-fehler.md` („je Projekt") nicht als dritte zu jenen zwei.
- `hooks/mengenaussagen.sh` in 10 s proben: JSON `{"tool_name":"Write","tool_input":{"file_path":"C:/x/n.md","content":"<Satz>"}}` per `printf` auf stdin, `MENGEN_LOG=<scratch>.jsonl`, dann `formen` in der Logzeile lesen. „113 Squash-Commits seit 01.09." und „113 = 80 Squash + 33 andere" ergaben beide `formen: []` (07.10.).
- Was die Vorsession Christian gesagt hat, steht im Transkript: `rg -n -o '"role":"user","content":"[^"]{1,120}'` auf der `.jsonl` listet seine Antworten mit Zeilennummer, die Frage davor per `rg -n` auf ihren Wortlaut (07.10.: Frage :3941, „1. ja 2. ja" :3944).

**Dieses Memory** ist Eingabe für den nächsten Lauf, keine Messung: Zahlen daraus vor Gebrauch nachmessen.
