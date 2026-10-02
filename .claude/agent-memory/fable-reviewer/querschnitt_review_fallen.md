---
name: querschnitt-review-fallen
description: Wiederkehrende Denkfallen im Review: #397-Frage, Stempel, Zwilling, benannte Ausnahmen, tautologische Gates, Kopien einer Zahl, Auftrag und JOURNAL als Behauptung
metadata:
  type: project
---
Stand 28.09.2026.

**Was der Diff nicht zeigt**
- #397-Frage: was macht der Fix wahr, woran hing etwas am Gegenteil? Getroffen u.a. bei: verengter Thunk -> Instanzzustand der Werkzeuge; neuer Typ -> Woerterbuch-Flip; Feld von e() auf markup() -> Textkopie im Export; Hilfe-Abschnitt geteilt -> Deep-Links `hilfe-*.html#`; gehaltene Waise -> haengender Zeiger. Nicht nur Pruefungen suchen, auch Schreiber und Kopien.
- Ein Stempel gehoert dorthin, wo das Ergebnis entsteht, nicht wo es angezeigt wird.
- Verlaengert ein PR eine Umformulierung: den Zwilling suchen.
- Verschobener Block aendert die Reihenfolge zu BEIDEN Nachbarn.
- Per-Schluessel-A-Struktur unter Schluessel B abgelegt: letzter gewinnt.
- „Karten umgehaengt"-Diff auf das pruefen, was keine Karte ist (`git show <basis>:<f> | grep -n <Stichwort>`).
- Zeilenangabe als Beleg: Funktion benennen, Aufrufer greppen (toter Code sieht aus wie ein Beleg).
- Hebt ein PR eine Vertagung auf („X bleibt unaufgeloest" -> jetzt aufgeloest): nach dem verneinenden Satz und der Einschraenkung suchen (`stay unresolved`, `for comments only`, „Urheber eines Kommentars"), nicht nach dem neuen Feldnamen; der Autor grept den neuen Namen und trifft die Negation nie. #270, 2. Revision (30.09.2026): 8 Stellen uebrig, darunter CONTRACTS §G, TEI-MODEL-AUTH-FILES §3.1 und Statuszeile plus Konsequenzliste der eigenen ADR.

**Gates und Ausnahmen**
- Benannte Ausnahme: greift sie an der Bedingung oder am Namen? Am Namen schaltet sie die Pruefung ab.
- Prueft das Gate den Wert oder nur die Konsistenz zweier Stellen desselben Autors?
- Vor Klasse A ueber eine Invariante die Basis mitmessen: haelt sie dort nicht, ist es Vorbestand.
- Zahlen stehen oft mehrfach: nach dem Gate-Lauf `grep -rn` ueber die alte Zahl; die Zweitzeile neben einem Anker selbst lesen.
- Harter Fehler NACH dem ersten Schreibvorgang ist kein Guard: bei einem Skript, das Dateien und eine Liste schreibt, die Zeile des `raise SystemExit` gegen die Zeile des ersten `write_text` halten. Zweimal getroffen (sync_tei_headers, siehe header_spiegel.md; `update-disambig-status-493.py` Runde 3, 30.09.2026: TEI geschrieben, CSV-Kopfzeilenpruefung danach, Wiederholungslauf sagt „nichts zu aendern", Zeile fehlt dauerhaft). Sonde: Kopie mit kaputter Liste, `--apply`, Hash der Datei vor/nach.

**Auftrag, JOURNAL, Threads**
- Zahlen und Daten im Auftrag stammen oft aus Verdichtungen: im Thread nachlesen (UTC beachten), nicht in einem Zusammenfassungskommentar.
- „in #N beantwortet", „PR-Text mitgezogen" per API messen; JOURNAL-Saetze ueber kuenftige Kommentare sind Bedingungen.
- Wachsende Zahlen (Sessionzahlen) sind nur als damals <= jetzt pruefbar.
- Vorher-Zahlen von der Live-Seite gehoeren zum dort aufgeloesten Lemma (Homograph `arm`: lemma_285 Adj., lemma_286 Koerperteil).
- Personennamen gegen contributors.xml (Alan van Beek = contrib_007).
- Scope-Fragen (z.B. Pruefseiten unter ingest/) vor dem Zaehlen klaeren.
- Mehrspurige Laeufe (Laufplan unter `docs/playbooks/kickoffs/`): die Koordination antwortet auf Aenderungswuensche der Spuren mit Commits auf `main`. Ist `origin/main` weiter als die im Auftrag genannte Basis, `git log <basis>..origin/main -- docs/playbooks/kickoffs/` lesen: dort steht oft die Antwort, auf die der Aufrufer noch wartet (02.10.2026: Ae4 gab die DEVELOPMENT-Zeile frei, waehrend der Auftrag „eingefroren, nur nach deren Antwort" sagte). Allaussagen im Diff gegen den Laufplan-Paragraphen halten, aus dem sie stammen (§4.2 nannte drei Buecher, FEATURES machte „the books" daraus).

**Fehlerjournal**
- `claude-code-setup/hooks/lehren-zaehlen.py` parst dieses Journal nicht (Format `### N. Rot:`): Ketten von Hand ueber den Absatz „Die Lehre, die nicht gegriffen hat"; Ordinalzahlen gegen Vorgaenger lesen.
- Nummern werden je Spur vorab reserviert: Spruenge sind kein Befund.

**Dieses Memory** ist Eingabe fuer den naechsten Lauf, keine Messung: Zahlen daraus vor Gebrauch nachmessen.
