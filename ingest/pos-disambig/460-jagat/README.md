# Batch-Log: #460 jagât, Verbformen am Substantivlemma

Provenienz-Log nach POS-TAGSET.md §6.3.5. Kein LLM-Batch im Sinn von K4: die Einstufung ist ein Leseurteil am Kontext, einzeln je Token, von der Koordination vorgelegt und in der Spur `lauf-a-daten` gegengelesen.

## Rahmen

- **Issue:** #460 „lemma_3103 (jagât): Verbformen an einem Substantivlemma", Zuschnitt entschieden von @chsteiner am 10.10.2026.
- **Datum der Umsetzung:** 2026-10-10
- **Einstufung:** Vorab-Messung der Koordination am 10.10.2026 (Sonnet-Agenten lasen alle 185 Tokens im Kontext; die Koordination zählte die Tabelle nach und zog eine Stichprobe von 14 `jaget`/`jeit`-Belegen ohne Abweichung). Gegenlesung in der Spur, siehe unten.
- **Arbeitsliste:** `belege.tsv` in diesem Ordner, Spalten `xml:id`, `Sigle`, `Form`, `Kontext` (Treffer in `[[ ]]`), `Einstufung`, `Begruendung`.
- **Umsetzung:** `scripts/ingest/pos-disambig/apply-460-jagat.py`

## Bestand und Zuschnitt

`lemma_3103` jagât (NOM) trägt 185 Tokens in 65 Texten, alle mit `@pos="NOM"` und `@ana` auf `lemma_3103_sense_4930`. Messvorschrift: alle `<w>` in `tei/*.tei.xml`, in deren `@lemmaRef` `#lemma_3103` als ganzes Token steht.

| Einstufung | Tokens | Behandlung |
|---|--:|---|
| Verb | 145 | auf `lemma_3102` jagen umgehängt (`@pos="VRB"`, `@ana` entfällt) |
| Substantiv | 35 | unverändert |
| unklar | 5 | unverändert, Frage an KZW |
| Summe | 185 | |

Die 145 Verbformen tragen die Schreibungen `jaget` 109, `jeit` 35, `jait` 1, in 51 Dateien. **Die Schreibung trennt die Klassen nicht:** `jaget` und `jeit` kommen auch als Substantiv vor (10 und 4 Tokens, „an einer jaget“, „zû der jaget“). Getrennt wurde am Kontext: Artikel, Possessiv oder Präposition davor gegen Subjekt mit Objekt oder Adverbial.

## Gegenlesung in der Spur (vor dem Schreiben)

Selbst gelesen und gegen die Einstufung gehalten: alle 35 Substantive (darunter die 14 unter `jaget`/`jeit`), alle 5 unklaren und 37 der 145 Verbbelege (jeder vierte der Tabelle, alle drei Schreibungen). Keine Abweichung. Knapp, aber nominal lesbar sind `FB_635017_4` und `FB_636006_4`.

## Umsetzung

- **Tokens:** je Token ändert sich nur das öffnende `<w>`-Tag: `@lemmaRef` auf `lemma_3102`, `@pos="VRB"`, `@ana` entfällt, `@corresp` auf einen neuen Variantentyp. Token-Text, Reihenfolge und `xml:id` bleiben byte-identisch; `@lemmaRef` bleibt gesetzt, die Positionszählung ändert sich damit nicht.
- **Kein `@ana`:** wie beim Großteil des Bestands unter `lemma_3102` (1.247 von 1.406 Tokens ohne `@ana`, gemessen am 10.10.2026). Eine Sense-Wahl am Kontext wäre ein eigener Auftrag.
- **Variantentypen:** nach der Regel aus #367 neu geprägt, keiner umgehängt: `type_372855` (`jaget`), `type_372856` (`jeit`), `type_372857` (`jait`), alle unter `lemma_3102`. Höchste vergebene Nummer vorher: `type_372854`. Die alten Typen `type_10674` und `type_10676` bleiben bei `lemma_3103` (Zählung `n` danach 13 und 4); `type_115155` (`jait`) verliert seinen einzigen Beleg und entfällt aus `variants.xml`.
- **`variants.xml`:** mit `extract-variants.py --apply` regeneriert: 3 Typen dazu, 1 entfällt, `n` bei 2 Typen geändert, Formtext und Lemmazuordnung 0.
- **`lexicon.xml`:** `extract-variants.py --apply` hat `#type_115155` aus `lemma_3103_sense_4930/@ana` entfernt (1 Eintrag in 1 Sense).
- **Revision:** je Datei ein `<change when="2026-10-10">` in der `revisionDesc` (51 Dateien).

## Offen bei KZW

Die 5 unklaren Belege bleiben unberührt (Kontext in `belege.tsv`):

| xml:id | Form | Stand |
|---|---|---|
| `AXU_18452_5` | `jaget` | Satzbau dunkel |
| `WVW_6542_4` | `jaget` | „daz krieclîchiu jaget“, Neigung Substantiv |
| `WH_28126_1` | `jaget` | „der jaget er manigen al den tac“, Neigung Verb |
| `JT_48611000_4` | `jagenes` | Genitiv des substantivierten Infinitivs, der Form nach eher `lemma_3102` |
| `JT_43134000_4` | `jagennes` | wie `JT_48611000_4` |
