---
name: projekt-526-breve-makron
description: Review-Rezepte für die #526-Nachannotierungen in der WZB (wzb-breve-526.py, wzb-makron-526.py): Tafelskript auf Kopie laufen lassen, Vergleichsform-Guard, mitalternde Allaussagen in CONTRACTS.md §A
metadata:
  type: project
---
Runde 1 zu #526 Punkt 5 am 07.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Tafelskripte (`scripts/ingest/wzb/wzb-*-526.py`)** lösen `REPO` über `Path(__file__).parents[3]` auf und lesen `tei/WZB.tei.xml` plus `data/authority-index.json.gz` hart. Probe auf Kopie: Scratch-Ordner mit `scripts/ingest/wzb/`, `tei/`, `data/` nachbauen, Basis-TEI per `git show origin/main:tei/WZB.tei.xml`, Mutanten als `mut_*.py` daneben. Apply auf der Kopie unterscheidet sich vom Arbeitsbaum nur im `Provenienz-Log:`-Pfad des change-Eintrags (relativ zum Kopie-REPO). Alle `sys.exit` stehen vor `write_text`, zweiter Lauf bricht am Tafel-Abgleich ab.

**Guard-Grenzen:** Die CCNJ/SCNJ-Lockerung (Lexikon führt `und` nur als CNJ) wird vom Vergleichsform-Guard eingefangen (SCNJ für `vn` bricht ab, weil die WZB `vn` nie SCNJ annotiert). Regel V prüft nur `treffer > 0`: ein falsches, aber in der WZB belegtes Lemma+pos für eine mehrdeutige Form (z. B. `in` -> lemma_1517 PRO) läuft durch; dort entscheidet allein die Tafel, also der Vers lesen.

**Mitalternde Allaussagen:** `docs/CONTRACTS.md` §A, Absätze um Zeile 101-107, zählen unannotierte Tokens als Invariante („none of the eight tokens carries a `@lemmaRef`“, „289 WZB `<w>` with an o/u breve still carry no `@lemmaRef`“). Jeder #526-Lauf macht einen davon falsch; die Rohzahlen daneben (8 macron, 774 marks) bleiben, weil sie Zeichen zählen, nicht Annotation. Die #526-Body-Tabelle und der Kommentar vom 06.10. („Punkt 5 (8 Makron-Tokens)“) zählen den Rest, nicht die Zeichen.

**EOL-Probe an der WZB (Runde 2, 07.10.2026):** der Blob hat gemischte Zeilenenden (236.000 von 236.018 Zeilen CRLF, `text` unset, `core.autocrlf=true`); ein Handedit an einer Zeile kann LF-Zeilen auf CRLF kippen, `git diff --stat` zeigt das nur als Zeilenzahl. Gegenprobe: `git show HEAD:tei/WZB.tei.xml` ins Scratchpad, dann `difflib.SequenceMatcher` auf `split(b"\n")` mit `autojunk=False` und je Zeile `endswith(b"\r")` ausgeben; erwartet sind genau die Token-Zeilen plus die change-Zeile. Dauer unter 10 s. Die Zeile von `WZB_143vb_10_4` ist eine der 18 LF-Zeilen.

**Begriffshilfe bleibt unberührt**, obwohl das FOLGEN-Docstring beider #526-Skripte ihren Neubau nennt: der Generator liest nur `w/@ana`, und die Läufe schreiben kein `@ana`. Gegenprobe `--out <scratch>` plus `git hash-object` gegen `HEAD:assets/downloads/mhdbdb-begriffshilfe.md` (07.10.2026 identisch, `5243c878`).

**CONTRACTS.md §A „289 WZB `<w>` with an o/u breve still carry no `@lemmaRef`" (Zeile 107)** ist seit den Breve-Läufen alt: am 07.10.2026 gemessen 91 roh, 118 nach NFD. Nicht Teil des #526-Diffs, vom Aufrufer bewusst nicht angefasst.

**Vorbestand, nicht #526:** 3 `vnd`-Tokens in der WZB ohne `@lemmaRef` (keine Diakritika), gemessen 07.10.2026 am Arbeitsbaum.
