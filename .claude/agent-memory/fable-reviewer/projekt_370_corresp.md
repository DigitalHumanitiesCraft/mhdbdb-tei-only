---
name: projekt-370-corresp
description: "#370 Punkt 2 (WZB-Paare ohne @corresp) im Review: ANLEGEN-Falle, zwei Tokenzählungen, Stichprobe, Messrezept alt/neu, Nachbarn die mitaltern"
metadata:
  type: project
---
Verdichtet 02.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**ANLEGEN heißt „neuen Typ prägen" und setzt voraus, dass keiner existiert.** Runde 1: der Auto-Pfad gab jedem Paar ohne Handurteil ANLEGEN, auch bei vorhandenem Typ (25 von 74 Nachtragspaaren, z. B. `in`/lemma_3028 mit type_10369). Seither gibt es den vierten Wert **VERKNÜPFEN** (nur `@corresp` setzen), gesetzt aus `lade_vorhandene_typen()` über (NFC-lower-Form, Lemma) in variants.xml. Nicht dasselbe: dieselbe Form unter einem ANDEREN Lemma (23 ANLEGEN, `heissen`, `is`, `et`) sind Homographen, die Vorschrift B (#378) ordnet.
- **Messrezept** (<1 min): variants.xml `entry/@corresp` ist durchweg `lexicon.xml#lemma_N`: `split('#')[-1]`; ein `lstrip('#')` lässt das Dateipräfix stehen und jeder Vergleich fällt still durch. Seit der Härtung (#521) brechen die 370-Skripte bei mehrwertigem, leerem oder `#`-losem Verweis ab; Schlüssel aus `ref.split()[0]`, nicht aus dem rohen Wert (`'#lemma_12 '` trägt sonst den Randleerraum mit). Korpusweit einwertig: 7.545.736 `w/@lemmaRef`, 42.457 variants-`entry/@corresp`.
- Der Laufplan (`docs/playbooks/kickoffs/2026-10-02-lauf.md`) sagt für den Nachtrag nur „gleiche Methode"; der Nachtrag hat keine Handurteile, also fällt dort alles in den Auto-Pfad.

**Zwei Tokenzahlen.** `offene-faelle.csv` (31.08.) summiert 5.273, dieselben 484 Paare haben am 01.10. 5.283 offene Tokens. `find-370-nachtrag.py` zählt nur **neue Paare**, nie neue Tokens bekannter Paare; die Differenz fällt zwischen beide Listen. `entscheidungen-zaehlung*.txt` und der Datenstand der Prüfseite nennen beide Zahlen, die Spalte `tokens` trägt den 31.08.-Wert.

**Was die Skripte nicht prüfen:** `pruefe_urteile` prüft das Ziellemma nur bei `ANDERE_ZUORDNUNG:`, nicht beim `vorschlag` eines PRUEFSEITE-Urteils; kein Skript vergleicht Lexikon-`pos` mit Token-`@pos`. `fundstelle()` in `build-370-pruefseite.py` verlangt `WZB_x_n_n$`; Split-Token-IDs wie `WZB_165vb_33_1b` (#235) stehen nur im Nachtrag und würden eine Nachtrag-Prüfseite abbrechen lassen.

**Einspielung (`wzb-corresp-punkt2.py`)** setzt nur @corresp per Byte-Ersetzung.
- **Messrezept alt/neu (<2 min):** `git show origin/main:tei/WZB.tei.xml` nach Temp, beide per lxml zu `xml:id -> (text, lemmaRef, corresp, pos, ana)`, Mengen vergleichen. Zeilenvergleich nur nach Entfernen der richtigen revisionDesc-Zeile: `#370 Punkt 2` trifft ZWEI change-Zeilen (Punkt 1 nennt Punkt 2 im Text).
- Prüfmaßstab: nur neue @corresp, 0 bestehende verändert; neue Typen = ANLEGEN-Zahl, angehobene `n` = VERKNÜPFEN-Zahl; Typen mit gemischter Groß-/Kleinschreibung stimmen nur NFC-lower.
- **Nachbarn, die mit der Einspielung veralten und die kein Gate sieht:** WZB-projectDesc Z. 83/84 (`@corresp`-Quoten mit Datum „gemessen am 06.09.2026", gleiche Grundmengen 149.165 w bzw. 142.360 lemmatisierte); CONTRACTS.md Variant-Dictionary-Absatz (variantCandidates-Zahlen neben der nachgezogenen Mappingzahl) und die Zeile „Two numbers that have to stay different"; DATA-MODEL.md `variantCandidates`-Kommentar und Absatz.

**Prüfseite (#443):** am HTML gemessen: 0 Radios vorbelegt, Export unterscheidet `stand`+`antwort`; Radios setzt review_page.py nur je Karte und beim Import.
