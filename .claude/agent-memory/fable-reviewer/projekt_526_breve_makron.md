---
name: projekt-526-breve-makron
description: WZB-Nachannotierungen im Review (#370 Punkt 2 @corresp, #526 Breve/Makron/w-n und Prüfseite): Tafelskript auf Kopie, ANLEGEN-Falle, Guard-Grenzen, EOL-Probe, Index-Abgleich, mitalternde Nachbarn
metadata:
  type: project
---
Zusammengelegt aus projekt_370_corresp und projekt_526_breve_makron, 08.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

## Gemeinsames Rezept (Tafelskripte `scripts/ingest/wzb/wzb-*.py`, `wzb-corresp-punkt2.py`)

- Sie lösen `REPO` über `Path(__file__).parents[3]` auf und lesen `tei/WZB.tei.xml` plus `data/authority-index.json.gz` hart. Probe auf Kopie: Scratch mit `scripts/ingest/wzb/`, `tei/`, `data/` nachbauen, Basis-TEI per `git show origin/main:tei/WZB.tei.xml`, Mutanten daneben. Gleiches `--out-dir` gibt bytegleiche Ausgabe wie der Arbeitsbaum. Nicht idempotent: ein zweiter Lauf bricht am Tafel-Abgleich ab, also nur auf der Basiskopie reproduzieren.
- **EOL:** der WZB-Blob hat gemischte Zeilenenden (fast alle CRLF, einige LF). Ein Handedit kann LF-Zeilen auf CRLF kippen; `git diff --stat` zeigt das nur als zu hohe Zeilenzahl. Gegenprobe: `difflib` auf `split(b"\n")` gegen den Basis-Blob und je Zeile `endswith(b"\r")`; erwartet sind genau die Token-Zeilen plus die change-Zeile.
- **Messrezept alt/neu (<2 min):** Basis und Kopf per lxml zu `xml:id -> (text, lemmaRef, corresp, pos, ana)`, Mengen vergleichen. Zeilenvergleich nur nach Entfernen der richtigen revisionDesc-Zeile (`#370 Punkt 2` trifft ZWEI change-Zeilen, Punkt 1 nennt Punkt 2 im Text).
- **Index-Abgleich ohne Neubau:** `corpus-index.json.gz` aus `git show` beider Stände laden, `texts[WZB].lemmata[lemma]`-Längen vergleichen: Summe der Differenzen = Tokenzahl des Laufs; `lemmaIndex` bleibt gleich, wenn alle Ziel-Lemmata in der WZB schon belegt waren, dann ist auch der Authority-Index unberührt (`load_corpus_lemma_ids` liest nur die Lemma-Menge). `wordCount` zählt nur lemmatisierte `<w>`.
- **Begriffshilfe bleibt unberührt**, obwohl das „FOLGEN: Begriffshilfe neu bauen" im Docstring der drei #526-Skripte etwas anderes sagt: der Generator liest nur `w/@ana`, diese Läufe schreiben keins (Gegenprobe siehe gates_und_ci, Begriffshilfe).
- **Was solche Skripte wahr machen (#397):** die #370-Ratsche `corresp-coverage-baseline.json` steigt um die Tokenzahl und muss per `--update-baseline=corresp` mitkommen; `check-authority-cross-refs.py` ohne `--check` druckt die Istwerte. Konsolenausgabe kürzt `vergleich_belege[:10]`, die CSV ist vollständig.

## #370 Punkt 2 (WZB-Paare ohne @corresp)

- **ANLEGEN heißt „neuen Typ prägen" und setzt voraus, dass keiner existiert.** Der Auto-Pfad gab jedem Paar ohne Handurteil ANLEGEN, auch bei vorhandenem Typ (25 von 74 Nachtragspaaren). Seither gibt es **VERKNÜPFEN** (nur `@corresp` setzen), gesetzt aus `lade_vorhandene_typen()` über (NFC-lower-Form, Lemma) in variants.xml. Dieselbe Form unter einem ANDEREN Lemma bleibt ANLEGEN (Homographe, Vorschrift B #378 ordnet).
- variants.xml `entry/@corresp` ist durchweg `lexicon.xml#lemma_N`: `split('#')[-1]`; `lstrip('#')` lässt das Dateipräfix stehen und jeder Vergleich fällt still durch. Die 370-Skripte brechen seit #521 bei mehrwertigem, leerem oder `#`-losem Verweis ab; Schlüssel aus `ref.split()[0]`.
- **Zwei Tokenzahlen** (31.08. gegen 01.10.): `find-370-nachtrag.py` zählt nur neue Paare, nie neue Tokens bekannter Paare; die Spalte `tokens` der Prüfseite trägt den 31.08.-Wert.
- **Nicht geprüft:** `pruefe_urteile` prüft das Ziellemma nur bei `ANDERE_ZUORDNUNG:`, nicht beim `vorschlag` eines PRUEFSEITE-Urteils; kein Skript vergleicht Lexikon-`pos` mit Token-`@pos`. `fundstelle()` in `build-370-pruefseite.py` verlangt `WZB_x_n_n$`; Split-Token-IDs wie `WZB_165vb_33_1b` (#235) ließen eine Nachtrag-Prüfseite abbrechen.
- Prüfmaßstab: nur neue @corresp, 0 bestehende verändert; neue Typen = ANLEGEN-Zahl, angehobene `n` = VERKNÜPFEN-Zahl; gemischte Groß-/Kleinschreibung stimmt nur NFC-lower.
- **Nachbarn, die mit der Einspielung veralten (kein Gate):** WZB-projectDesc Z. 83/84 (`@corresp`-Quoten), CONTRACTS.md Variant-Dictionary-Absatz und „Two numbers that have to stay different", DATA-MODEL.md `variantCandidates`-Kommentar.

## #526 (Breve, Makron, w-n; Prüfseite Punkt 4)

- **Guard-Grenzen:** Regel V prüft nur `treffer > 0`: ein falsches, aber in der WZB belegtes Lemma+pos für eine mehrdeutige Form läuft durch; dort trägt allein die Tafel, also den Vers lesen.
- **Mitalternde Allaussagen:** `docs/CONTRACTS.md` §A (um Z. 101-107) zählte unannotierte WZB-Tokens als Invariante; seit #534 stehen die Sätze datiert in der Vergangenheit. Ein neuer #526-Lauf: dort und im Thread nach Rest-Zählungen suchen. Zählvorschrift „136/64": `<w>`-Text roh (kein NFD), U+0306 auf Grundzeichen außer o/u, alle 667 Dateien. `DECISIONS.md` ~1094-1096 ist datierter ADR-Text und wird nicht nachgezogen.
- **Prüfseite (`scripts/review/build-526-pruefseite.py`):** die `xml:id` `WZB_<blatt>_<zeile>_<n>` zählt ab 0 über `<w>` **und** `<pc>`, ein Suffix kann auch `13b` sein; ein „Wort n+1" aus der id ist bei Zeilen mit Satzzeichen davor falsch (8 von 19 Karten). Messen: alle `xml:id` der Zeile mit Elementname sammeln. Ein „Sinn"-Satz über ein Lemma ist nur über `concepts.xml` prüfbar: `lexicon.xml`-Senses tragen keine `<def>`, nur `<ptr target="concepts.xml#concept_N">` (`zerströuwen`, lemma_15396, hat eine zweite Sense mit Tod/Gewalt/Vergehen).
