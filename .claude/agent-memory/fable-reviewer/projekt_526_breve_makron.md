---
name: projekt-526-breve-makron
description: WZB-Nachannotierungen im Review (#370 Punkt 2 @corresp, #526 Breve/Makron/w-n und Prüfseite): Tafelskript auf Kopie, ANLEGEN-Falle, Guard-Grenzen, EOL-Probe, Index-Abgleich, mitalternde Nachbarn
metadata:
  type: project
---
Zusammengelegt aus projekt_370_corresp und projekt_526_breve_makron, 08.10.2026; verdichtet 10.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

## Gemeinsames Rezept (Tafelskripte `scripts/ingest/wzb/wzb-*.py`, `wzb-corresp-punkt2.py`)

- `REPO` = `Path(__file__).parents[3]`, lesen `tei/WZB.tei.xml` und `data/authority-index.json.gz` hart. Probe auf Kopie: Scratch mit `scripts/ingest/wzb/`, `tei/`, `data/`, Basis-TEI per `git show origin/main:tei/WZB.tei.xml`. Gleiches `--out-dir` gibt bytegleiche Ausgabe. Nicht idempotent (zweiter Lauf bricht am Tafel-Abgleich ab): nur auf der Basiskopie reproduzieren.
- **EOL:** WZB-Blob mit gemischten Zeilenenden (header_spiegel). Ein Handedit kann LF-Zeilen auf CRLF kippen, `git diff --stat` zeigt nur eine zu hohe Zeilenzahl. Gegenprobe: `difflib` auf `split(b"\n")` gegen den Basis-Blob, je Zeile `endswith(b"\r")`; erwartet nur Token-Zeilen plus change-Zeile.
- **Alt/neu (<2 min):** beide Stände per lxml zu `xml:id -> (text, lemmaRef, corresp, pos, ana)`, Mengen vergleichen. Zeilenvergleich nur nach Entfernen der richtigen revisionDesc-Zeile (`#370 Punkt 2` trifft ZWEI change-Zeilen).
- **Index-Abgleich ohne Neubau:** `corpus-index.json.gz` beider Stände per `git show`, `texts[WZB].lemmata[lemma]`-Längen vergleichen: Summe der Differenzen = Tokenzahl des Laufs; `lemmaIndex` gleich, wenn alle Ziel-Lemmata in der WZB schon belegt waren, dann ist auch der Authority-Index unberührt. `wordCount` zählt nur lemmatisierte `<w>`.
- **Begriffshilfe bleibt unberührt**, entgegen „FOLGEN: Begriffshilfe neu bauen" im Docstring der drei #526-Skripte: der Generator liest nur `w/@ana`, diese Läufe schreiben keins.
- **#397:** die Ratsche `corresp-coverage-baseline.json` steigt um die Tokenzahl und muss per `--update-baseline=corresp` mitkommen; `check-authority-cross-refs.py` ohne `--check` druckt die Istwerte. Die Konsolenausgabe kürzt `vergleich_belege[:10]`, die CSV ist vollständig.

## #370 Punkt 2 (WZB-Paare ohne @corresp)

- **ANLEGEN heißt „neuen Typ prägen" und setzt voraus, dass keiner existiert.** Der Auto-Pfad gab früher jedem Paar ohne Handurteil ANLEGEN, auch bei vorhandenem Typ. Seither **VERKNÜPFEN** (nur `@corresp`), aus `lade_vorhandene_typen()` über (NFC-lower-Form, Lemma). Dieselbe Form unter einem ANDEREN Lemma bleibt ANLEGEN (Homographe, Vorschrift B #378).
- variants.xml `entry/@corresp` ist durchweg `lexicon.xml#lemma_N`: `split('#')[-1]`. Die 370-Skripte brechen seit #521 bei mehrwertigem, leerem oder `#`-losem Verweis ab.
- `find-370-nachtrag.py` zählt nur neue Paare, nie neue Tokens bekannter Paare.
- **Nicht geprüft:** `pruefe_urteile` prüft das Ziellemma nur bei `ANDERE_ZUORDNUNG:`, nicht beim `vorschlag` eines PRUEFSEITE-Urteils; kein Skript vergleicht Lexikon-`pos` mit Token-`@pos`. `fundstelle()` in `build-370-pruefseite.py` verlangt `WZB_x_n_n$`; Split-Token-IDs (`WZB_165vb_33_1b`, #235) lassen sie abbrechen.
- Prüfmaßstab: nur neue @corresp, 0 bestehende verändert; neue Typen = ANLEGEN-Zahl, angehobene `n` = VERKNÜPFEN-Zahl.
- **Mitalternde Nachbarn (kein Gate):** WZB-projectDesc (`@corresp`-Quoten), CONTRACTS.md Variant-Dictionary-Absatz und „Two numbers that have to stay different", DATA-MODEL.md `variantCandidates`-Kommentar.

## #526 (Breve, Makron, w-n; Prüfseite Punkt 4)

- **Guard-Grenzen:** Regel V prüft nur `treffer > 0`: ein falsches, aber in der WZB belegtes Lemma+pos für eine mehrdeutige Form läuft durch; dort trägt allein die Tafel, also den Vers lesen.
- **Mitalternde Allaussagen:** `docs/CONTRACTS.md` §A zählte unannotierte WZB-Tokens als Invariante; seit #534 datiert. Bei einem neuen Lauf dort und im Thread nach Rest-Zählungen suchen. Zählvorschrift „136/64": `<w>`-Text roh (kein NFD), U+0306 auf Grundzeichen außer o/u, alle 667 Dateien. Der ADR-Text in `DECISIONS.md` ist datiert und wird nicht nachgezogen.
- **Prüfseite (`scripts/review/build-526-pruefseite.py`):** die `xml:id` `WZB_<blatt>_<zeile>_<n>` zählt ab 0 über `<w>` **und** `<pc>`, Suffix auch `13b`; ein „Wort n+1" aus der id ist bei Satzzeichen davor falsch. Ein „Sinn"-Satz über ein Lemma ist nur über `concepts.xml` prüfbar: `lexicon.xml`-Senses tragen keine `<def>`, nur `<ptr target="concepts.xml#concept_N">`.
