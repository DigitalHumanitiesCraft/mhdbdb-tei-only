---
name: lexikon-variants
description: lexicon.xml und variants.xml im Review: Vorschrift B (form/@n, variantCandidates), Dangling-Filter, sense/@ana ohne Konsument, Schreiber außerhalb Lifecycle, Komposita und noCorpus (#228), Ziffernlemmata
metadata:
  type: project
---
Verdichtet 08.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Laufzeit-Wörterbuch seit Authority 1.9.18: Vorschrift B statt first-wins** (bis 1.9.17 gewann die Dokumentreihenfolge)
- `variants.xml` trägt je `<form>` ein Pflichtattribut `n` (Tokens des Typs unter dem Lemma, aus `extract-variants.py`; Schema verlangt es). `parse_variants(known_lemma_ids)` summiert `n` je (Normalform, Lemma), rangiert absteigend, Gleichstand = Dokumentordnung (= Lemmanummer). `variants[form]` = erster Kandidat, `variantCandidates[form]` nur bei >1. Fehlendes `n` = harter Build-Abbruch. Gegenprobe (iterparse-Scan, ~3,5 min): `@n`-Summen == corresp-Tokenzahlen je (Normalform, Lemma).
- Der Dangling-Filter ist die eine Stelle, an der der Index von lexicon.xml abhängt: ein Backfill (#115), der ein hängendes Lemma anlegt, kann eine Form umklappen (halap).
- Inversionen (`app.js getVariantFormsFor`, `lemma-page.js renderVariants`) listen eine Form weiter nur unter dem ersten Kandidaten; ADR-021 führt das als offen.
- `extract-variants.py` zählt Typen, nicht Formen; ein neuer Typ für eine anderswo existierende Form kann die Rangfolge drehen, sichtbar in `check-variants-flips.py` (gates_und_ci). Typ-Id -> Lemma ist eindeutig. Typ-Träger korpusweit: `re.finditer(r'<w xml:id="([^"]+)"[^>]*corresp="variants\.xml#(type_\d+)"')`, ~30 s.
- Zählung der beanspruchten Formen: parse_variants-Logik mit `mhg_normalizer.normalize_mhg` nachbauen, nicht NFC-lower.

**sense/@ana**
- Trägt Variantentypen, hat keinen Konsumenten (build-authority-index liest `ana` nur am Konzept-`title`, cross-refs überspringt `#type_N`, kein Spec/Frontend lädt lexicon.xml): Änderungen sind index-, API- und testneutral. Richtig/falsch entscheidet DATA-MODEL (der Typ gehört zum Sense seines Tokens). Konzepte eines Sense stehen in `sense/ptr/@target`.
- Hängende Typverweise je Revision: lexicon + variants per `git show`, `split()` über sense/@ana gegen die variants-xml:id-Menge. Eine belegfrei gehaltene Waise verliert ihren variants-Eintrag und behält sense/@ana; `extract-variants.py --apply` räumt sie ab.

**Schreiber von lexicon.xml außerhalb des Lifecycle:** apply-228.py (löscht Einträge), backfill-lexicon.py (Stubs). „Der eine Ort, an dem eine tei/-Änderung lexicon.xml ändern kann" (DATA-MODEL) gilt nur für die Lifecycle-Skripte.

**Wortart:** kein Skript vergleicht Token-@pos mit gramGrp; Legacy-Tag ART fällt aus NP-Start-Mengen heraus.

**Ziffernlemmata:** seit `claude/228-ziffern` nur noch lemma_53328 „1" (Belege alle NEIM, #453); alle Ziffernschlüssel im Laufzeit-Wörterbuch zeigen darauf. hapax-legomena.spec.js ankert auf ein Orakel aus den Indexen. Außerhalb des Diffs veraltend: CONTRACTS.md C.1.2 („4 lemmata ... 78 keys"), Kommentar `passesFilters` in hapax-legomena.js.

**Reine Wortbestandteile (#228, `component-only.js`, `noCorpus`)**
- `lemma.id` und `etymology[].lemmaRef` tragen beide `lemma_N` ohne `#`/`lexicon.xml#`. `noCorpus` gibt es erst seit 1.9.18; die Spec mockt es per `page.route`; veralteter Browser-Cache ist kein Loch (`corpus-loader.js` verwirft ihn bei Versionsabweichung). `renderOccurrences` kehrt ohne `lemmaIndex[lemmaKey]` früh zurück.
- `hilfe-korpussuche.html` ~Z. 445-446 („Jeder Eintrag besteht aus dem Lemma und einem Wortart-Kürzel") ist nach #228 eine Allaussage mit Ausnahmen.

**Tokens zwischen Lemmata umhängen (#460/#461/#462, 10.10.2026)**
- Variantentypen werden nicht umgehängt (#367), neue Nummern geprägt; `n` der alten Typen sinkt, ein Typ ohne Rest entfällt. Das Flip-Gate verlangt die gitignorierte `scripts/audit/variants-flips-ack.json` (`git add -f`): den Grund je Form lesen.
- Sense-IDs sind global, ein neuer Sense trägt kein `@ana`. `extract-variants.py --help` läuft als Trockenlauf und schreibt `authority-files/variants.regen.xml`: vor dem Commit löschen.
- Zerlegte Tags zählen für beide Teile (`NEG VRB`): ein „häufigste Wortart“ aus Korpuszählung hat bei Gleichstand keinen Sieger. Die Grundmenge zerlegen, bevor eine Regel darauf steht (#462: 1.537 abweichende `pos` nach der Wortlaut-Lesart gegen 5.653 nach „Inhaltswort gewinnt“).
