---
name: projekt-lexikon-variants
description: Authority-Dateien, lexicon.xml, variants.xml, Senses und Umhängen von Tokens
metadata:
  type: project
---
**Authority-Dateien und Authority-Index**
- **concepts.xml ist kein Baum:** Mehrfacheltern über `<ptr type="broader">` und eine Selbstschleife. Hüllen brauchen eine Visited-Menge. „Subtree" meint die Root meist mit, „unter X" nicht: beide Lesarten messen.
- Optionale Indexfelder (`altDE`, `altEN`, `altNormalized`) stehen nur an Trägern. `totalAuthorityFiles = 7` (ui-helpers.js) zählt Index-Sammlungen, nicht Dateien.
- Das Index-Schema steht an vier Orten: DATA-MODEL.md (Schema-Block und XPath-Referenz), TEI-MODEL-AUTH-FILES.md, CONTRACTS.md §G.3 (normativ). Neues Feld: alle greppen.
- contributors.xml liest build-authority-index nur in `load_contributor_names()`, `resp_name` bricht bei fremdem Präfix, unbekannter oder leerer ID ab.
- **works.xml:** Siglen mit `.//tei:idno[@type="sigle"]` zählen wie der Syncer, TRO ist die einzige Doppelsigle. Werke ohne TEI-Datei gibt es (`WG`, `WLK`). Die Werkzahl steht ungegatet an drei Stellen (TEI-MODEL-AUTH-FILES.md, Kommentar in `build-authority-index.py`, Docstring `sync_tei_headers.py`).

**Laufzeit-Wörterbuch: Vorschrift B (seit Authority 1.9.18)**
- `<form>` in variants.xml trägt Pflicht-`n` (Tokens des Typs unter dem Lemma). `parse_variants` summiert `n` je (Normalform, Lemma), rangiert absteigend, Gleichstand = Dokumentordnung. `variants[form]` = erster Kandidat, `variantCandidates[form]` nur bei >1. Gegenprobe: `@n`-Summen == corresp-Tokenzahlen je (Normalform, Lemma).
- Der Dangling-Filter ist die eine Stelle, an der der Index von lexicon.xml abhängt: ein Backfill, der ein hängendes Lemma anlegt, kann eine Form umklappen.
- `extract-variants.py` zählt Typen, nicht Formen: ein neuer Typ kann die Rangfolge drehen (`check-variants-flips.py`). Typ-Träger: `re.finditer(r'<w xml:id="([^"]+)"[^>]*corresp="variants\.xml#(type_\d+)"')`. Formen mit `mhg_normalizer.normalize_mhg` nachbauen, nicht NFC-lower.
- `entry/@corresp` ist `lexicon.xml#lemma_N`, immer genau ein Token (so schreibt es `extract-variants.py`). Ein Leser mit `.split()` statt `split('#')[-1]` ist heute wirkungsgleich, kein A. Einige `entry/@corresp` hängen auf Lemmata ohne lexicon-Eintrag: ein Konsument, der jeden Kandidaten im Lexikon verlangt, bricht erst, wenn so einer trifft.

**sense/@ana, w/@ana und lexicon.xml**
- sense/@ana trägt Variantentypen und hat keinen Konsumenten (Index liest `ana` nur am Konzept-`title`, cross-refs überspringt `#type_N`, kein Spec und kein Frontend lädt lexicon.xml). Konzepte eines Sense stehen in `sense/ptr/@target`. Hängende Typverweise: `split()` über sense/@ana gegen die variants-xml:id-Menge, `extract-variants.py --apply` räumt sie ab.
- Kein JS liest `w/@ana` (`git grep -w ana -- '*.js'`), der Korpus-Index auch nicht. Leser sind `build-begriffshilfe.py`, `measure-498-*`, `check-authority-cross-refs.py`, `foreign-sense-contradictions-28.py`, alle trennen an Leerzeichen (mehrere Senses in einem `w/@ana` gibt es, #602).
- **Selbstschließende `<sense xml:id="…"/>` gibt es:** eine Regex `<sense\b[^>]*xml:id="…"[^>]*>(.*?)</sense>` frisst dann den Folge-Sense. Gegenprobe mit lxml `iter(TEI+'sense')`.
- Schreiber außerhalb des Lifecycle: apply-228.py (löscht Einträge), backfill-lexicon.py (Stubs). „Der eine Ort, an dem tei/ lexicon.xml ändern kann" (DATA-MODEL) gilt nur für die Lifecycle-Skripte. Kein Skript vergleicht Token-@pos mit gramGrp oder Lexikon-`pos`.
- Eine Aussage über Senses („Erotik-Bedeutung neben der wörtlichen", #702, „verliert damit Konzept X", #461) je Sense an den `ptr` prüfen, nicht am Etikett oder am Satz eines Vorläufers: dasselbe Konzept kann an mehreren Senses eines Lemmas hängen.

**Neues Lemma mit der Normalform eines bestehenden (#216 Minne/minne):** Stufe 1 liefert beide. Hauptseite gibt die Vereinigung zurück, Playground `searchLemmaByOrthography` rankt nach Korpusfrequenz, `resolveLemmaNames` nimmt `tables.lower[...][0]`. Positionen ändern sich nur in Dateien mit NEU gesetztem `@lemmaRef`: „ändert die Positionszählung in N Texten" gegen das Protokoll zählen.

**Tokens zwischen Lemmata umhängen:** Variantentypen werden nicht umgehängt, neue Nummern geprägt, `n` der alten sinkt, ein Typ ohne Rest entfällt. Das Flip-Gate verlangt die gitignorierte `variants-flips-ack.json` (`git add -f`). Sense-IDs sind nur als `lemma_M_sense_N` global, ein neuer Sense trägt kein `@ana`.

**w/@ana zwischen Senses umhängen (#461, #602)**
- `scripts/review/messen-*.py` mit fester Erwartungsmenge (`ERWARTET`) brechen nach dem Umhängen ab. Eine Quelle „Kommentare in #N" für eine Terminal-Entscheidung gegen den Thread zählen.
- Nachfahren der `apply-461-*.py` (`ROOT` = `parents[3]`, nicht idempotent): Skript aus HEAD plus `lexicon.xml`, `tei/<sigle>.tei.xml`, `belege.tsv` der Basis per `git cat-file blob` in einen Scratch-Baum gleicher Tiefe, `--apply`, dann `git hash-object --no-filters` gegen `git rev-parse HEAD:<pfad>`.
- Nebenwirkungen stehen woanders: Authority-Index lemmaweise gegen die Basis diffen (#602 klappte das `pos` eines anderen Lemmas). `comment-attribution.spec.js` zieht eine Stichprobe nach Index-Position aus der Kommentarliste: ein neuer Kommentar verschiebt sie, vorher/nachher nachrechnen.

**lemma.pos / posAll (#462):** `data/lemma-pos.json.gz` aus `scripts/build-lemma-pos.py` (Regex über tei/, kein Textleer-Filter wie im Korpus-Index). `apply_corpus_pos` fasst nur `len(posAll) > 1` an, Sortkey `(-count, lexikonindex)`. Nachrechnen gegen `git show <base>:data/authority-index.json.gz` je Lemma. Altbestand: leeres `posAll` mit `pos == ''` (`posAll[0]` wirft).

**WZB-Paare ohne @corresp (#370 Punkt 2)**
- ANLEGEN heißt „neuen Typ prägen" und setzt voraus, dass keiner existiert. Vorhandener Typ über (NFC-lower-Form, Lemma) ergibt VERKNÜPFEN (nur `@corresp`), dieselbe Form unter einem anderen Lemma bleibt ANLEGEN (Homographe).
- `find-370-nachtrag.py` zählt nur neue Paare, nie neue Tokens bekannter Paare. `pruefe_urteile` prüft das Ziellemma nur bei `ANDERE_ZUORDNUNG:`.
