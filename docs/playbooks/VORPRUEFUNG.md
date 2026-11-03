# Vorprüfung: offene Fragen an Katharina gegen die Quellen halten

**Erstellt:** 2026-11-03, nach der Entscheidung von chsteiner, Katharinas Entscheidungsstau monatlich von einer Claude-Code-Routine vorprüfen zu lassen.
**Typ:** Playbook. Es autorisiert nichts für sich allein (README dieses Ordners). Ein Lauf beginnt mit einem Auftrag: dem Prompt der monatlichen Routine oder einem Kickoff von chsteiner.

**Warum es den Lauf gibt.** Am 03.11.2026 lagen bei Katharina 34 Fragen zum Entscheiden, die älteste vom 31.08. (generierter Teil von #44, Tabelle „Wer ist gerade dran?“). Sie hat mehrfach verlangt, dass vorher geprüft wird, was sich ohne sie klären lässt:

- #28, 17.09.2026: „prüfe die 26 belegstärksten Lemmata anhand von Korpuskontext, bestehenden Annotationen und seriösen Quellen vor. Lege mir anschließend nur die verbleibenden fachlichen Unsicherheiten mit Belegen und begründetem Vorschlag vor.“
- #603, 15.10.2026: „Erst Claude alle, die er automatisiert schafft - dann der Rest als EIL-Prüfung.“
- #406, 17.09.2026: „Bereits beantwortete Fragen dürfen nicht erneut als Entscheidungsrückstand bei mir erscheinen.“

Dazu kommt die Regel in `CLAUDE.md` unter „Asking“: erst die Quellen, dann der Mensch. Dieser Lauf holt die Quellenprüfung für Fragen nach, die schon gestellt sind. **Er senkt ihre Last, er erzeugt keine.** Eine Frage, die sie heute nicht hat, entsteht hier nicht.

Wie `DOKU-CHECK.md` muss diese Datei ohne persönliche Skills und Regeln auskommen.

## 1. Fälligkeit

1. **Eingabe ist der generierte Teil von #44:** `gh api repos/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44 --jq .body`, zwischen `PERSONEN:BEGIN` und `PERSONEN:END` der Abschnitt „Für Katharina“. Jede Zeile hat Art, Datum (`seit`), Ticket und die Frage als Link auf ihren Kommentar.
2. **Gegenstand sind die Zeilen mit der Art `Entscheiden`, deren Datum mehr als 14 Tage zurückliegt.** Abnahmen nicht, die prüft sie am laufenden System. Julia und Linda nicht, entschieden am 03.11.2026 für Katharina, weil der Stau bei ihr liegt.
3. **Schon vorgeprüft:** Eine Frage, deren Link in einer früheren Datei `docs/playbooks/kickoffs/*vorpruefung-*.md` auf `main` schon steht, wird übersprungen, wenn das Ticket seither keinen neuen Kommentar hat.
4. **Ende ohne Ausgabe**, wenn danach nichts übrig ist oder ein PR mit dem Kopf `claude/vorpruefung-*` offen ist (`gh api "repos/.../pulls?state=open" --jq '.[].head.ref'`).

## 2. Vertrag

Wie `BALL-RUECKGABE.md` Abschnitt 2: Betriebsvertrag vollständig, die drei Cloud-Abweichungen aus `DOKU-CHECK.md` Abschnitt 2, und der Lauf schreibt nichts außerhalb seines PRs, keine Kommentare, keine Labels, keine Daten.

## 3. Ablauf je Frage

1. **Den Thread ganz lesen**, Body und alle Kommentare über `gh api --paginate`.
2. **Die Quellen in dieser Reihenfolge:**
   - **Andere Threads und Commits:** Ist die Frage anderswo schon entschieden? `gh api "search/issues?q=repo:DigitalHumanitiesCraft/mhdbdb-tei-only+<Stichwort>"`, `git log origin/main --grep=<Stichwort>`, und jedes Ticket, das der Thread verlinkt. Das ist der Fall aus #406.
   - **Die Daten:** Belege **mit Kontext**, nicht das Stichwort allein. Für ein Lemma die Belegstellen in `tei/` über `@lemmaRef` samt Vers davor und danach, die bestehende Annotation (`@ana`, `@pos`), den Eintrag in `authority-files/lexicon.xml`. Für Werke und Personen `works.xml` und `persons.xml`. Der Fall „Alanya“ in `CLAUDE.md` zeigt, was ein Urteil vom Stichwort allein kostet.
   - **Die Doku:** `docs/`, besonders `TEI-MODEL.md`, `POS-TAGSET.md`, `DECISIONS.md`.
3. **Einordnen in genau eine Klasse:**
   - **1, anderswo entschieden:** mit dem Link auf die Entscheidung. Vorschlag: Frage zurückziehen.
   - **2, aus den Quellen beantwortbar:** mit den zitierten Belegen (Sigle, Stelle, Wortlaut) und einem Antwortvorschlag. Vorschlag: die Frage zu einer Bestätigung verkürzen, die in einer Minute zu geben ist. Die Entscheidung bleibt bei Katharina.
   - **3, enger fassbar:** Die Quellen klären einen Teil. Dazu die neue, kürzere Fragezeile `@wachauer Frage: <ein Satz>?`.
   - **4, bleibt offen:** ein Satz, warum die Quellen nicht reichen.
4. **Im Zweifel die höhere Nummer.** Ein falsches „beantwortbar“ wiegt schwerer als ein „bleibt offen“ zu viel, weil Christian die Frage daraufhin zurückziehen könnte.

## 4. Ergebnis

1. **Branch** `claude/vorpruefung-JJJJ-MM-TT` von `origin/main`, die Basis gemessen nach Regel 7 des Betriebsvertrags.
2. **Eine Datei** `docs/playbooks/kickoffs/FORTSETZUNG-vorpruefung-JJJJ-MM-TT.md`:
   - Erste Zeile: dass die Datei ein vorbereiteter Auftrag aus dem Lauf vom JJJJ-MM-TT ist, mit dem Stand von #44 und der Zahl der Fragen samt Menge (`9 von 34 Fragen geprüft, 25 jünger als 14 Tage oder schon vorgeprüft`).
   - Je Klasse ein Abschnitt, je Frage: Ticket, die heutige Fragezeile, Klasse, Belege, Vorschlag. Für Klasse 3 die neue Zeile fertig zum Einsetzen. Hinweis aus `CLAUDE.md`: Eine Frage wird nur dann oben auf unseren letzten Kommentar editiert, wenn der neuer ist als ihre letzte Antwort, sonst als neuer Kommentar gepostet.
3. **Gates und Review vor dem Push** wie in `DOKU-CHECK.md` Abschnitt 4, Punkt 4.
4. **PR über REST**, Titel `Vorprüfung JJJJ-MM-TT: <Zahl> Fragen`, Body mit einer Tabelle Ticket, Klasse und ein Satz. Kein Closing-Keyword vor einer Issue-Nummer. Gemergt wird von Hand.
