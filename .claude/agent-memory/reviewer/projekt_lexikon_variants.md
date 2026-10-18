---
name: projekt-lexikon-variants
description: Authority-Dateien, lexicon.xml und variants.xml im Review: Vorschrift B (form/@n, variantCandidates), Dangling-Filter, sense/@ana ohne Konsument, Schreiber außerhalb Lifecycle, lemma.pos/posAll, WZB-Paare ohne @corresp (#370 Punkt 2), concepts-Graph, Authority-Index, works-Siglen, contributors
metadata:
  type: project
---
Verdichtet 18.10.2026, zusammengelegt mit dem früheren Authority-Dateien-Memory (Stand 28.09.2026). Zahlen sind Eingabe, vor Gebrauch nachmessen.

## Authority-Dateien und Authority-Index

- **concepts.xml ist kein Baum:** Mehrfacheltern über `<ptr type="broader">` und eine Selbstschleife (concept_12050000). Hüllen brauchen eine Visited-Menge. „Subtree" meint die Wurzel meist mit, „unter X" nicht: beide Lesarten messen.
- Optionale Indexfelder (`altDE`, `altEN`, `altNormalized`) stehen nur an Trägern.
- Zwei Felder gleichen Namens: `text.genre` (Korpus-Index, entfernt mit 4.2.22) und `work.genre` (Authority-Index, weg seit #433; heute `work.genres`, `maps.genreToWorks`). Wer „genre" greppt, sieht beide Ketten als eine.
- `totalAuthorityFiles = 7` (ui-helpers.js) zählt Index-Sammlungen, nicht Dateien.
- Das Schema steht an vier Orten: DATA-MODEL.md (Schema-Block und XPath-Referenz), TEI-MODEL-AUTH-FILES.md („Index mapping"), CONTRACTS.md §G.3 (normativ). Neues Feld: alle greppen.
- api/: `api/lemmata` hat nur index.json; `api/concepts/concept_N.json` ohne Lemmalisten.
- **contributors.xml:** build-authority-index liest sie nur in `load_contributor_names()`; `resp_name` endet mit SystemExit bei fremdem Präfix, unbekannter oder leerer ID. contrib_052 trägt eine dritte Kopie der Naming-Zitation (projekt_fremdquellen).
- **works.xml:** Siglen mit `.//tei:idno[@type="sigle"]` zählen wie der Syncer. TRO ist die einzige Doppelsigle. `work_WLK` (#237/#496) hat keinen `biblStruct`, bis der Zotero-Sync ihn nachliefert. Werk ohne TEI-Datei ist nicht neu (`WG`, `WLK`); Kontrollwert „Siglen ohne Datei". Werkzahl ungegatet an drei Stellen (TEI-MODEL-AUTH-FILES.md Overview, Kommentar in `build-authority-index.py`, Docstring `sync_tei_headers.py`); die `584` in `mhdbdb-authority.rnc` und `doc-count-audit.py` sind datiert.

## Laufzeit-Wörterbuch seit Authority 1.9.18: Vorschrift B statt first-wins

- `variants.xml` trägt je `<form>` ein Pflichtattribut `n` (Tokens des Typs unter dem Lemma, aus `extract-variants.py`). `parse_variants(known_lemma_ids)` summiert `n` je (Normalform, Lemma), rangiert absteigend, Gleichstand = Dokumentordnung (= Lemmanummer). `variants[form]` = erster Kandidat, `variantCandidates[form]` nur bei >1. Fehlendes `n` = harter Build-Abbruch. Gegenprobe (iterparse-Scan, ~3,5 min): `@n`-Summen == corresp-Tokenzahlen je (Normalform, Lemma).
- Der Dangling-Filter ist die eine Stelle, an der der Index von lexicon.xml abhängt: ein Backfill (#115), der ein hängendes Lemma anlegt, kann eine Form umklappen (halap).
- `extract-variants.py` zählt Typen, nicht Formen; ein neuer Typ für eine anderswo existierende Form kann die Rangfolge drehen, sichtbar in `check-variants-flips.py`. Typ-Träger korpusweit: `re.finditer(r'<w xml:id="([^"]+)"[^>]*corresp="variants\.xml#(type_\d+)"')`, ~30 s. Beanspruchte Formen: parse_variants-Logik mit `mhg_normalizer.normalize_mhg` nachbauen, nicht NFC-lower.

**sense/@ana**
- Trägt Variantentypen, hat keinen Konsumenten (build-authority-index liest `ana` nur am Konzept-`title`, cross-refs überspringt `#type_N`, kein Spec/Frontend lädt lexicon.xml): Änderungen sind index-, API- und testneutral. Konzepte eines Sense stehen in `sense/ptr/@target`.
- Hängende Typverweise je Revision: lexicon + variants per `git show`, `split()` über sense/@ana gegen die variants-xml:id-Menge. Eine belegfrei gehaltene Waise verliert ihren variants-Eintrag und behält sense/@ana; `extract-variants.py --apply` räumt sie ab.

**Selbstschließende `<sense xml:id="…"/>` in lexicon.xml (124 am 18.10.2026, `rg -c '<sense\b[^>]*/>'`):** jede Regex der Form `<sense\b[^>]*xml:id="…"[^>]*>(.*?)</sense>` frisst damit den Inhalt des Folge-Sense (106 bekamen fremde Konzepte, 124 Senses fehlten in der Treffermenge; #603 `auswerten-lesung-603.py`). Gegenprobe immer mit lxml `iter(TEI+'sense')` und `ptr/@target`.

**Schreiber von lexicon.xml außerhalb des Lifecycle:** apply-228.py (löscht Einträge), backfill-lexicon.py (Stubs). „Der eine Ort, an dem eine tei/-Änderung lexicon.xml ändern kann" (DATA-MODEL) gilt nur für die Lifecycle-Skripte. Kein Skript vergleicht Token-@pos mit gramGrp.




**Tokens zwischen Lemmata umhängen (#460/#461/#462)**
- Variantentypen werden nicht umgehängt (#367), neue Nummern geprägt; `n` der alten Typen sinkt, ein Typ ohne Rest entfällt. Das Flip-Gate verlangt die gitignorierte `variants-flips-ack.json` (`git add -f`): den Grund je Form lesen.
- Sense-IDs `lemma_M_sense_N` sind als Ganzes global, ein neuer Sense trägt kein `@ana`. `sense_N` nur mit `lemma_M_` davor greppen; nach einer Löschung Präsens-Sätze im Journal prüfen.
- `extract-variants.py --help` läuft als Trockenlauf und schreibt `authority-files/variants.regen.xml`: vor dem Commit löschen.

**lemma.pos / posAll seit Authority 1.9.24 (#462):** `data/lemma-pos.json.gz` aus `scripts/build-lemma-pos.py` (Regex über tei/, Teil-Tags je Token, kein Textleer-Filter wie im Korpus-Index). `apply_corpus_pos` fasst nur `len(posAll) > 1` mit Eintrag an; Sortkey `(-count, lexikonindex)`. Nachrechnen: `git show <base>:data/authority-index.json.gz`, Vergleich je Lemma von `pos`, `posAll`, `sorted(posAll)` und aller übrigen Felder; Altbestand: Lemmata mit leerem `posAll` und `pos == ''` (`posAll[0]` wirft IndexError), lemma-IDs in lemma-pos ohne Indexeintrag.

**WZB-Paare ohne @corresp (#370 Punkt 2, Skripte `wzb-*.py`; Tafelskripte siehe projekt-korpus-tei)**
- **ANLEGEN heißt „neuen Typ prägen" und setzt voraus, dass keiner existiert.** Der Auto-Pfad gab früher jedem Paar ohne Handurteil ANLEGEN, auch bei vorhandenem Typ; seither **VERKNÜPFEN** (nur `@corresp`), aus `lade_vorhandene_typen()` über (NFC-lower-Form, Lemma). Dieselbe Form unter einem ANDEREN Lemma bleibt ANLEGEN (Homographe, Vorschrift B #378).
- variants.xml `entry/@corresp` ist durchweg `lexicon.xml#lemma_N`: `split('#')[-1]`. Die 370-Skripte brechen seit #521 bei mehrwertigem, leerem oder `#`-losem Verweis ab. `find-370-nachtrag.py` zählt nur neue Paare, nie neue Tokens bekannter Paare.
- **Nicht geprüft:** `pruefe_urteile` prüft das Ziellemma nur bei `ANDERE_ZUORDNUNG:`, nicht beim `vorschlag` eines PRUEFSEITE-Urteils; kein Skript vergleicht Lexikon-`pos` mit Token-`@pos`. `fundstelle()` in `build-370-pruefseite.py` verlangt `WZB_x_n_n$`; Split-Token-IDs (`WZB_165vb_33_1b`, #235) lassen sie abbrechen.
