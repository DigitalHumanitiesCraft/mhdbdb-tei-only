# POS-Tagset

Kanonische Referenz für das Wortart-Tagset (`@pos`) der MHDBDB-TEI-Texte: das normative 19-Tag-Zielschema, die Regeln für Compound-Tags, die im Altbestand noch vorhandenen Legacy-Tags und die tatsächliche Verteilung im Korpus.

Dies ist die **Single Source of Truth** für die `@pos`-Werte. Der zugehörige operative Disambiguierungs-Workflow (LLM-gestützte Auflösung von Compound- und Falsch-Tags) ist als Agent-Skill unter `.gemini/skills/pos-disambiguator/` implementiert; er nutzt dieses Tagset, definiert es aber nicht.

## 1. Das 19-Tag-Zielschema

Jedes annotierte `<w>`-Element trägt genau einen Tag aus diesem Set (Ausnahme: dokumentierte morphologische Fusionen, siehe §2).

> **WICHTIG:** `ART` ist **kein** gültiger Tag. Artikel (*der, diu, daz, ein*) werden als `DET` getaggt. `ART` im Bestand ist Legacy und wird migriert (siehe §3).

| Tag | Name | Beispiele |
|-----|------|-----------|
| **NOM** | Nomen | acker, zît, minne |
| **NAM** | Eigenname | Uolrîch, Wiene, Rhîn, sant (vor Namen) |
| **ADJ** | Adjektiv | grôz, schoene, guot, wâr |
| **ADV** | Adverb | schône, vil, sêre, gar, als/wie (komparativ) |
| **DET** | Determinante | der, diu, daz, ein, diser, jener, kein, dekein, dehein |
| **POS** | Possessivpronomen | mîn, dîn, unser |
| **PRO** | Pronomen | ich, ez, wir, Relativpronomen, swer (indefinit) |
| **PRP** | Präposition | ûf, zuo, under, durch |
| **NEG** | Negation | nie, niht, nit, nich, nieht, ne, en, âne |
| **NUM** | Numeral | zwô, drî, zweinzegest |
| **CNJ** | Konjunktion (allgemein) | Fallback bei Ambiguität (danne additiv) |
| **SCNJ** | Subordinierende Konjunktion | daz (Nebensatz), ob, swenne, sît, als (temporal) |
| **CCNJ** | Koordinierende Konjunktion | und, oder, aber, ouch, noch |
| **IPA** | Interrogativpartikel | wie (Frage), war (wohin?), swer (interrogativ) |
| **VRB** | Vollverb | liuhten, varn, machen; haben/sîn/werden (lexikalisch) |
| **VEX** | Hilfsverb | haben/sîn/werden (mit Partizip II) |
| **VEM** | Modalverb | müezen, suln, kunnen |
| **INJ** | Interjektion | ahî, owê |
| **DIG** | Zahl (römisch) | IX, XVII, III |

Die ausführlichen linguistischen Abgrenzungen (DET vs. PRO, VRB vs. VEX, *als/wie* kontextabhängig, MHG-Negationsmuster usw.) stehen im Disambiguierungs-Skill (`.gemini/skills/pos-disambiguator/SKILL.md`).

## 2. Compound-Tags

Im Altbestand tragen viele `<w>`-Elemente (~35–40 %) durch Leerzeichen getrennte Compound-Werte (z.B. `pos="VRB VEX"`, `pos="ADJ ADV"`), die eine ungelöste Ambiguität ausdrücken. **Standardregel:** der Disambiguierungs-Workflow löst sie kontextabhängig auf einen einzelnen Tag auf.

**Ausnahme:** Echte morphologische Fusionen behalten zwei Tags und erhalten ein `reason`-Attribut:

| Fusion | Beispiel | Tags | `reason` |
|--------|----------|------|----------|
| Verb + enklitisches Pronomen | *wiltu* = wilt + du | `VEM PRO` | `wilt+du` |
| Verb + enklitisches Pronomen | *färbs* = färbe + ez | `VRB PRO` | `färbe+ez` |
| Präposition + Determinante | *zer* = ze + der | `PRP DET` | `ze+der` |
| Präposition + Determinante | *zem* = ze + dem | `PRP DET` | `ze+dem` |

## 3. Legacy-Tags (Altbestand)

Der aus der RDF-Migration übernommene Bestand nutzt teilweise ein älteres Tagset. Diese Tags sind **nicht** Teil des 19-Tag-Schemas und werden migriert:

| Legacy | Ziel | Aktion |
|--------|------|--------|
| `ART` | `DET` | Batch-Umbenennung (Artikel sind Determinanten) |
| `CNJ` (koordinierend) | `CCNJ` | kontextabhängig (linguistische Analyse nötig) |
| `CNJ` (subordinierend) | `SCNJ` | kontextabhängig (linguistische Analyse nötig) |
| `GRA` | *entfällt* | geht in `ADJ` auf (Graduierung/Superlativ = ADJ) |

`CNJ` bleibt als allgemeiner Fallback-Tag im 19-Set gültig, der Großteil der `CNJ`-Vorkommen im Bestand ist jedoch noch nicht in `CCNJ`/`SCNJ` differenziert.

Daneben existieren vereinzelt nicht-kanonische Rest-Artefakte aus der Migration (`-`, `KOKOM`, `FM`, `PTK`, `X` sowie der Tippfehler `SCJN` für `SCNJ`), die bei der Disambiguierung normalisiert werden.

## 4. Verteilung im Korpus

`@pos` ist auf 7.406.168 `<w>`-Elementen gesetzt (79,8 % aller `<w>`; Stand und Methodik siehe [TEI-MODEL.md §10](TEI-MODEL.md)). Die folgende Tabelle zählt **atomare Tag-Vorkommen**: Compound-Werte werden an Leerzeichen aufgespalten, ein Token `pos="ADJ ADV"` zählt also je einmal bei `ADJ` und `ADV`. Die Summe übersteigt daher die Zahl der Tokens.

| Tag | Vorkommen (atomar) | Status |
|-----|-------------------:|--------|
| VRB | 1.535.938 | 19-Set |
| NOM | 1.508.545 | 19-Set |
| ADV | 1.362.350 | 19-Set |
| **ART** | 1.064.439 | Legacy → DET |
| ADJ | 1.029.930 | 19-Set |
| CNJ | 943.199 | 19-Set (Großteil noch nach CCNJ/SCNJ zu differenzieren) |
| PRP | 659.793 | 19-Set |
| PRO | 658.741 | 19-Set |
| VEX | 223.294 | 19-Set |
| NEG | 204.786 | 19-Set |
| NAM | 194.319 | 19-Set |
| POS | 150.663 | 19-Set |
| VEM | 133.057 | 19-Set |
| NUM | 116.966 | 19-Set |
| **GRA** | 60.278 | Legacy → ADJ |
| IPA | 59.061 | 19-Set |
| DET | 53.443 | 19-Set |
| INJ | 22.071 | 19-Set |
| CCNJ | 13.805 | 19-Set |
| SCNJ | 7.371 | 19-Set |
| DIG | 4.783 | 19-Set |
| `-`, KOKOM, FM, PTK, X, SCJN | < 100 gesamt | Rest-Artefakte → Normalisierung |

Die Dominanz von `ART` (über 1 Mio.) und der niedrige `DET`-Wert (53k) zeigen, dass die ART→DET-Migration den Großteil des Bestands noch betrifft. Die häufigsten Compound-Werte sind `ADJ ADV` (304.069), `ART CNJ` (271.352) und `VRB VEX` (206.261).

> **Reproduktion:** atomare Verteilung über das Korpus:
> ```bash
> grep -rhoE 'pos="[^"]*"' tei/ | sed 's/pos="//;s/"$//' | tr ' ' '\n' | sed '/^$/d' | sort | uniq -c | sort -rn
> ```
> Die Zahlen sind ein Snapshot und verschieben sich mit fortschreitender Disambiguierung und neuem Ingest.

## 5. Disambiguierung

Die Auflösung von Compound-Tags, die Korrektur von Falsch-Tags und die ART/CNJ/GRA-Migration erfolgen nicht mechanisch, sondern kontextabhängig über semantisch-grammatische Analyse. Der dafür vorgesehene Workflow ist als Agent-Skill `.gemini/skills/pos-disambiguator/` implementiert (Phasen: Split → Analyse → Merge → Validierung → Refinement). Pädagogische Beispiele für Mehrdeutigkeiten (*daz*, *als*, *haben*) liegen unter `.gemini/skills/pos-disambiguator/references/examples.md`.

## Querverweise

- [TEI-MODEL.md §5](TEI-MODEL.md) – `@pos` im normativen TEI-Soll-Modell
- [DATA-MODEL.md](DATA-MODEL.md) – `@pos` im Annotations-Datenmodell und in der Backfill-Pipeline
- `.gemini/skills/pos-disambiguator/SKILL.md` – operativer Disambiguierungs-Workflow und linguistische Abgrenzungsregeln
