---
name: projekt-lexikon-variants
description: Authority-Dateien, lexicon.xml und variants.xml im Review: Authority-Index, Vorschrift B, sense/@ana, Schreiber außerhalb des Lifecycle, Tokens umhängen, lemma.pos, WZB-Paare ohne @corresp, works-Siglen
metadata:
  type: project
---
Verdichtet 03.11.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Authority-Dateien und Authority-Index**
- **concepts.xml ist kein Baum:** Mehrfacheltern über `<ptr type="broader">` und eine Selbstschleife. Hüllen brauchen eine Visited-Menge. „Subtree" meint die Wurzel meist mit, „unter X" nicht: beide Lesarten messen.
- Optionale Indexfelder (`altDE`, `altEN`, `altNormalized`) stehen nur an Trägern. `totalAuthorityFiles = 7` (ui-helpers.js) zählt Index-Sammlungen, nicht Dateien. `text.genre` (Korpus-Index, entfernt) und `work.genre` (heute `work.genres`) sind zwei Ketten.
- Das Index-Schema steht an vier Orten: DATA-MODEL.md (Schema-Block und XPath-Referenz), TEI-MODEL-AUTH-FILES.md, CONTRACTS.md §G.3 (normativ). Neues Feld: alle greppen.
- contributors.xml liest build-authority-index nur in `load_contributor_names()`, `resp_name` bricht bei fremdem Präfix, unbekannter oder leerer ID ab.
- **works.xml:** Siglen mit `.//tei:idno[@type="sigle"]` zählen wie der Syncer, TRO ist die einzige Doppelsigle. Werke ohne TEI-Datei gibt es (`WG`, `WLK`). Die Werkzahl steht ungegatet an drei Stellen (TEI-MODEL-AUTH-FILES.md, Kommentar in `build-authority-index.py`, Docstring `sync_tei_headers.py`).

**Laufzeit-Wörterbuch: Vorschrift B (seit Authority 1.9.18)**
- `<form>` in variants.xml trägt Pflicht-`n` (Tokens des Typs unter dem Lemma). `parse_variants` summiert `n` je (Normalform, Lemma), rangiert absteigend, Gleichstand = Dokumentordnung. `variants[form]` = erster Kandidat, `variantCandidates[form]` nur bei >1. Gegenprobe: `@n`-Summen == corresp-Tokenzahlen je (Normalform, Lemma).
- Der Dangling-Filter ist die eine Stelle, an der der Index von lexicon.xml abhängt: ein Backfill, der ein hängendes Lemma anlegt, kann eine Form umklappen.
- `extract-variants.py` zählt Typen, nicht Formen: ein neuer Typ kann die Rangfolge drehen (`check-variants-flips.py`). Typ-Träger: `re.finditer(r'<w xml:id="([^"]+)"[^>]*corresp="variants\.xml#(type_\d+)"')`. Formen mit `mhg_normalizer.normalize_mhg` nachbauen, nicht NFC-lower. `entry/@corresp` ist `lexicon.xml#lemma_N`.

**sense/@ana und lexicon.xml**
- sense/@ana trägt Variantentypen und hat keinen Konsumenten (Index liest `ana` nur am Konzept-`title`, cross-refs überspringt `#type_N`, kein Spec und kein Frontend lädt lexicon.xml): index-, API- und testneutral. Konzepte eines Sense stehen in `sense/ptr/@target`. Hängende Typverweise: `split()` über sense/@ana gegen die variants-xml:id-Menge, `extract-variants.py --apply` räumt sie ab.
- **Selbstschließende `<sense xml:id="…"/>` gibt es:** eine Regex `<sense\b[^>]*xml:id="…"[^>]*>(.*?)</sense>` frisst dann den Folge-Sense. Gegenprobe mit lxml `iter(TEI+'sense')`.
- Schreiber außerhalb des Lifecycle: apply-228.py (löscht Einträge), backfill-lexicon.py (Stubs). „Der eine Ort, an dem tei/ lexicon.xml ändern kann" (DATA-MODEL) gilt nur für die Lifecycle-Skripte. Kein Skript vergleicht Token-@pos mit gramGrp oder Lexikon-`pos`.

**Tokens zwischen Lemmata umhängen:** Variantentypen werden nicht umgehängt, neue Nummern geprägt, `n` der alten sinkt, ein Typ ohne Rest entfällt. Das Flip-Gate verlangt die gitignorierte `variants-flips-ack.json` (`git add -f`). Sense-IDs sind nur als `lemma_M_sense_N` global, ein neuer Sense trägt kein `@ana`.

**lemma.pos / posAll (#462):** `data/lemma-pos.json.gz` aus `scripts/build-lemma-pos.py` (Regex über tei/, kein Textleer-Filter wie im Korpus-Index). `apply_corpus_pos` fasst nur `len(posAll) > 1` an, Sortkey `(-count, lexikonindex)`. Nachrechnen gegen `git show <base>:data/authority-index.json.gz` je Lemma. Altbestand: leeres `posAll` mit `pos == ''` (`posAll[0]` wirft).

**WZB-Paare ohne @corresp (#370 Punkt 2)**
- ANLEGEN heißt „neuen Typ prägen" und setzt voraus, dass keiner existiert. Vorhandener Typ über (NFC-lower-Form, Lemma) ergibt VERKNÜPFEN (nur `@corresp`), dieselbe Form unter einem anderen Lemma bleibt ANLEGEN (Homographe).
- `find-370-nachtrag.py` zählt nur neue Paare, nie neue Tokens bekannter Paare. `pruefe_urteile` prüft das Ziellemma nur bei `ANDERE_ZUORDNUNG:`, nicht beim `vorschlag` eines PRUEFSEITE-Urteils.
