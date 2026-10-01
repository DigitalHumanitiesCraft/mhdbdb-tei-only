---
name: lexikon-variants
description: lexicon.xml und variants.xml im Review: first-wins-Woerterbuch kippt bei neuen Typen, sense/@ana ohne Konsument, haengende Typverweise, Schreiber ausserhalb Lifecycle, Kompositum- und Ziffernlemma-Fakten
metadata:
  type: project
---
Stand 28.09.2026.

**Laufzeit-Woerterbuch kippt, Typ-Zaehler bleibt gruen**
- `authority-index.json.gz['variants']` ist first-wins in Dokumentreihenfolge (`build-authority-index.py` ~:807 `if normalized_variant not in variants`); die kleinere Lemmanummer gewinnt nur, weil variants.xml danach sortiert ist. Nicht „nach Lemmanummer" schreiben.
- Ein neuer Typ fuer eine anderswo existierende Form kann eine Zuordnung umbiegen; `extract-variants.py` zaehlt Typen, nicht Formen, und sieht es nicht (mehrfach passiert: hawsen, froewen).
- Rezept bei jedem Daten-PR mit neuen `type_N`: Basis-Index per `git show <basis>:data/authority-index.json.gz`, beide `variants`-Dicts: added/removed/re-pointed, dazu Tokenzahl je (Form, Lemma) aus tei/. ADR-021 (DECISIONS.md) fuehrt diese Handlaeufe als Fixturen (Vorschrift B); ein Datenlauf mit neuen Typen braucht dort eine Zeile.
- variants.xml ist je Normalform NICHT einwertig (02.09.: 4.972 von 234.243 Normalformen zeigen auf mehr als ein Lemma): „Einwertigkeit" ist falsch. Typ-Id -> Lemma ist dagegen eindeutig (Regex ueber `<w>`-Tags, corresp -> set(lemmaRef), <1 min).
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
