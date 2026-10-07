---
name: projekt-526-breve-makron
description: Review-Rezepte für die #526-Nachannotierungen in der WZB (wzb-breve-526.py, wzb-makron-526.py): Tafelskript auf Kopie, Guard-Grenzen, EOL-Probe, mitalternde Allaussagen in CONTRACTS.md §A
metadata:
  type: project
---
**Tafelskripte (`scripts/ingest/wzb/wzb-*-526.py`)** lösen `REPO` über `Path(__file__).parents[3]` auf und lesen `tei/WZB.tei.xml` plus `data/authority-index.json.gz` hart. Probe auf Kopie: Scratch-Ordner mit `scripts/ingest/wzb/`, `tei/`, `data/` nachbauen, Basis-TEI per `git show origin/main:tei/WZB.tei.xml`, Mutanten daneben. Mit gleichem `--out-dir` ist die Ausgabe bytegleich mit dem Arbeitsbaum. Nicht idempotent: ein zweiter Lauf bricht am Tafel-Abgleich ab, also nur auf der Basiskopie reproduzieren.

**Guard-Grenzen:** Die CCNJ/SCNJ-Lockerung (Lexikon führt `und` nur als CNJ) fängt der Vergleichsform-Guard ein. Regel V prüft nur `treffer > 0`: ein falsches, aber in der WZB belegtes Lemma+pos für eine mehrdeutige Form läuft durch; dort trägt allein die Tafel, also den Vers lesen.

**EOL-Probe an der WZB:** der Blob hat gemischte Zeilenenden (`text` unset, fast alle CRLF, einige LF). Ein Handedit kann LF-Zeilen auf CRLF kippen; `git diff --stat` zeigt das nur als zu hohe Zeilenzahl. Gegenprobe: Basis-Blob ins Scratchpad, `difflib` auf `split(b"\n")` und je Zeile `endswith(b"\r")`; erwartet sind genau die Token-Zeilen plus die change-Zeile.

**Begriffshilfe bleibt unberührt**, obwohl das FOLGEN-Docstring ihren Neubau nennt: der Generator liest nur `w/@ana`, die #526-Läufe schreiben keins. Gegenprobe `build-begriffshilfe.py --out <scratch>` plus `git hash-object` gegen HEAD.

**Mitalternde Allaussagen:** `docs/CONTRACTS.md` §A (um Zeile 101-107) zählte unannotierte WZB-Tokens als Invariante; seit #534 (07.10.) stehen beide Sätze datiert in der Vergangenheit. Die Rohzahlen daneben (Zeichen, nicht Annotation) bleiben gültig. Ein neuer #526-Lauf: dort und im #526-Thread nach Rest-Zählungen suchen.
