---
name: lexikon-variants
description: lexicon.xml und variants.xml im Review: Woerterbuch seit 1.9.18 nach Vorschrift B (form/@n, variantCandidates) statt first-wins, Flip-Gate mit Quittung, sense/@ana ohne Konsument, haengende Typverweise, Schreiber ausserhalb Lifecycle, Kompositum- und Ziffernlemma-Fakten
metadata:
  type: project
---
Stand 02.10.2026.

**Laufzeit-Woerterbuch: seit Authority 1.9.18 Vorschrift B statt first-wins** (Zweig `claude/lauf-a1-378`, 81121f733, Runde 1 am 02.10.; vorher galt bis 1.9.17 first-wins in Dokumentreihenfolge)
- `variants.xml` traegt je `<form>` ein Pflichtattribut `n` (Tokens des Typs unter dem Lemma, aus `extract-variants.py`; Schema `mhdbdb-authority.rnc` verlangt es). `build-authority-index.py parse_variants(known_lemma_ids)` summiert `n` je (Normalform, Lemma), rangiert absteigend, Gleichstand = Dokumentordnung (= Lemmanummer, Eintraege sind sortiert; 591 Listen mit Gleichstand oben). `variants[form]` = erster Kandidat, `variantCandidates[form]` nur bei >1 (4.961 von 233.962; 4.979 Formen von >1 Lemma beansprucht, 18 fallen durch den Dangling-Filter auf einen, 24 Listen enthielten haengende Lemmata; 15 `variants`-Werte zeigen weiter auf Lemmata ohne lexicon-Eintrag, weil die Form nur solche hat). Fehlendes `n` = harter Build-Abbruch.
- Gemessen am Korpus (eigener iterparse-Scan, 211 s, Skript im Scratch): `@n`-Summen == corresp-Tokenzahlen je (Normalform, Lemma) bei allen 4.979, Reihenfolge weicht in 0 Faellen ab, auch gegen alle `<w @lemmaRef>`. Kein `@lemmaRef` mit mehreren IDs im Korpus (0 von 667 Dateien).
- Stand 1.9.19 (#370 Punkt 2, 02.10.): 234.264 Mappings, variantCandidates 4.973, 4.991 Formen von >1 Lemma beansprucht, 18 durch Dangling-Filter auf einen, 24 Listen mit haengenden Lemmata; 10 Flips (boeze, geheisse, gepflaget, kochen, reisse, steigen, tir, vassen, verrens, weicz), Quittung 1.9.18 -> 1.9.19.
- Flips 1.9.17 -> 1.9.18: 2.063 (2.065 ohne Dangling-Filter; halap, chana). Beispiele: hab 418:15 -> lemma_2598, ne 1433:1 -> lemma_4377, froewen 35/21/1 -> lemma_7260, hawsen 5:2 -> lemma_49714; pyn bleibt lemma_4664, hawe lemma_2923.
- Inversionen (`app.js getVariantFormsFor`, `lemma-page.js renderVariants`) listen eine Form weiter nur unter dem ersten Kandidaten; ADR-021 fuehrt das als offen.
- `extract-variants.py` zaehlt Typen, nicht Formen; ein neuer Typ fuer eine anderswo existierende Form kann weiter die Rangfolge drehen, sichtbar jetzt im Gate `check-variants-flips.py` (siehe gates_und_ci).
- Typ-Id -> Lemma ist eindeutig (Regex ueber `<w>`-Tags, corresp -> set(lemmaRef), <1 min).
- Der Dangling-Filter ist die eine Stelle, an der der Index von lexicon.xml abhaengt: ein Backfill (#115), der ein haengendes Lemma anlegt, kann eine Form umklappen (halap: lemma_79230 haette 3:1 gewonnen).
- Typ-Traeger korpusweit: `re.finditer(r'<w xml:id="([^"]+)"[^>]*corresp="variants\.xml#(type_\d+)"')`, ~30 s.

**sense/@ana**
- Traegt Variantentypen, hat keinen Konsumenten: build-authority-index liest `ana` nur am Konzept-`title`, cross-refs ueberspringt `#type_N`, kein Spec/Frontend laedt lexicon.xml. Aenderungen sind index-, API- und testneutral.
- Richtig/falsch entscheidet DATA-MODEL (@corresp-Aufloesung = variants-Lookup geschnitten mit ana des Sense): der Typ gehoert zum Sense seines Tokens.
- Konzepte eines Sense stehen in `sense/ptr/@target`, nicht in @ana.
- Haengende Typverweise je Revision: lexicon + variants per `git show`, `split()` ueber sense/@ana gegen die variants-xml:id-Menge (5 Revisionen ~1 min). Eine belegfrei gehaltene Waise verliert ihren variants-Eintrag und behaelt sense/@ana. Auf main gab es solche Verweise schon vor #228; seit c0cf3e1df raeumt `extract-variants.py --apply` sie ab.
- Alle sense-Starttags mit @ana sind kanonisch `<sense xml:id=".." ana="..">`; der Textanker des Prune haengt daran.

**Schreiber von lexicon.xml ausserhalb des Lifecycle:** apply-228.py (loescht Eintraege), backfill-lexicon.py (Stubs). „der eine Ort, an dem eine tei/-Aenderung lexicon.xml aendern kann" (DATA-MODEL) gilt nur fuer die Lifecycle-Skripte.

**Wortart**
- Kein Skript vergleicht Token-@pos mit gramGrp; Corpus-Index liest @pos nicht, Playground nutzt posAll.
- Legacy-Tag ART faellt aus NP-Start-Mengen wie {DET, ADJ, NOM, NAM, PRO, POS, NUM} heraus.

**Komposita:** `<etym type="morphological">` mit >= 2 `<seg type="component">`. CONTRACTS-Zahl „Formen an Komposita / nackte Komponenten": Formen in variants.xml an diesen Lemmata, Form == Komponententext ist nackt; Regex-Skript <10 s. Zwei leere etym (lemma_933, lemma_23628).

**Ziffernlemmata:** seit dem Zweig `claude/228-ziffern` (01.10.2026, Review Runde 1) nur noch lemma_53328 „1" (63 Belege, alle NEIM, #453); 69733/69748/69749/69750 geloescht, die 26 Ziffern in `<supplied>` von MR1/WVV entannotiert (`apply-228-ziffern.py` laedt apply-228.py per importlib). Ziffern-Schluessel im Laufzeit-Woerterbuch: 62, alle auf lemma_53328. hapax-legomena.spec.js ankert seit dann nicht mehr auf `/^\d/`, sondern auf ein Orakel aus den Indexen (69 reine NUM-Hapaxe, 47 gemischte). Mur (lemma_66692) bewusst offen. Stellen, die beim Ziffern-Thema ausserhalb des Diffs veralten: CONTRACTS.md C.1.2 (`36`/aberelle-Satz, „4 lemmata ... 78 keys"), Kommentar `passesFilters` in hapax-legomena.js (42/49-Satz, „47 der 119").
