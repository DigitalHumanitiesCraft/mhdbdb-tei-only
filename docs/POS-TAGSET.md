# POS-Tagset

Kanonische Referenz für das Wortart-Tagset (`@pos`) der MHDBDB-TEI-Texte: das normative 19-Tag-Zielschema, die Regeln für Compound-Tags, die im Altbestand noch vorhandenen Legacy-Tags und die tatsächliche Verteilung im Korpus.

Dies ist die **Single Source of Truth** für die `@pos`-Werte. Der zugehörige operative Disambiguierungs-Workflow (LLM-gestützte Auflösung von Compound- und Falsch-Tags) ist als Agent-Skill unter `.gemini/skills/pos-disambiguator/` implementiert; er nutzt dieses Tagset, definiert es aber nicht.

> **Zielgruppe:** Diese Datei ist eine technische Referenz-Spezifikation, primär für Entwicklung und automatisierte Werkzeuge gedacht (präzise, maschinenorientiert).

## 1. Das 19-Tag-Zielschema

Jedes annotierte `<w>`-Element trägt genau einen Tag aus diesem Set (Ausnahme: dokumentierte morphologische Fusionen, siehe §2).

> **Hinweis:** `ART` ist **kein** gültiger Tag. Artikel (*der, diu, daz, ein*) werden als `DET` getaggt. `ART` im Bestand ist Legacy und wird migriert (siehe §3).

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

## 6. Disambiguierungs- und Migrations-Policy (#27)

Verbindliche Policy für die Überführung des Altbestands (Compound-Tags, Legacy-Tags, bekannte Fehlannotationen) in das 19-Tag-Schema aus §1. Sie macht den Workflow planbar: Was wird in welcher Reihenfolge migriert, was entscheidet das LLM allein, was braucht Stichproben-Review, was bleibt liegen, bis KZW entscheidet. Kein Teil dieser Policy ändert das Tagset selbst.

### 6.1 Verbindlichkeitsstufen

| Stufe | Bedeutung |
|-------|-----------|
| **P-MUSS** | Ohne Erfüllung wird kein Batch committet |
| **P-SOLL** | Abweichung erlaubt, im Provenienz-Log begründen |
| **P-OFFEN** | Explizit KZW-Entscheid nötig, bis dahin Status quo |

### 6.2 Migrations-Klassen und Reihenfolge

Die Klassen sind nach Automatisierbarkeit absteigend sortiert und werden in dieser Reihenfolge abgearbeitet; jede Klasse ist ein eigener, unabhängig prüfbarer Batch (eigener Branch/PR, eigenes Provenienz-Log).

| Klasse | Bestand (atomar, §4) | Verfahren | Stufe |
|--------|---------------------:|-----------|-------|
| K1: Rest-Artefakte (`-`, KOKOM, FM, PTK, X, SCJN) | < 100 | deterministische Tabelle (SCJN→SCNJ; Rest: Einzelfall-Liste im PR) | P-MUSS deterministisch |
| K2: ART → DET | 1.064.439 | Batch-Umbenennung, KEIN Kontext nötig (Artikel sind DET per Definition §1) | P-MUSS deterministisch |
| K3: GRA → ADJ | 60.278 | Batch gemäß §3 (Graduierung/Superlativ = ADJ) | P-MUSS deterministisch; Abweichung im Issue-Body („GRA→ADV/PART") ist ALT, siehe 6.5 |
| K4: Compound-Auflösung (ADJ ADV, VRB VEX, ART CNJ, …) | ~35–40 % der Tokens | LLM kontextabhängig (Skill-Workflow), AUSSER echte Fusionen (§2: bleiben zweiwertig + `@reason`) | P-MUSS LLM + Gates 6.3 |
| K5: CNJ → CCNJ/SCNJ | 943.199 | LLM kontextabhängig; CNJ bleibt als Fallback erlaubt bei echter Ambiguität | P-SOLL (Fallback erlaubt) |
| K6: Bekannte Fehlannotations-Muster (Issue §2: enhaben, wiest, Morphologie-als-Zweittag, NEG-Vereinheitlichung, NAM-Übergriffe) | verstreut | LLM mit Watch-List (Skill „Known Error Patterns") | P-MUSS LLM + Gates 6.3 |

Begründung der Reihenfolge: K1–K3 sind kontextfrei und schrumpfen den Problemraum messbar (über 1,1 Mio. atomare Alt-Tags), bevor die teuren LLM-Klassen laufen; K4 vor K5, weil viele CNJ-Fälle in Compounds stecken (ART CNJ: 271k) und sonst doppelt angefasst würden.

### 6.3 Qualitätsgates (für K4–K6, P-MUSS)

1. **Batch-Größe:** max. 1 Text pro LLM-Lauf-Einheit; Ausgabe als Diff-Liste (xml:id, alt, neu, Begründung, confidence).
2. **Golden Set:** vor dem ersten K4-Batch 200 händisch verifizierte Fälle (KZW/Studis) über alle Klassen; jeder Modell-/Prompt-Wechsel wird erst gegen das Golden Set gemessen (Ziel ≥ 95 % Übereinstimmung), dann eingesetzt. (Gilt nur für die LLM-Klassen K4–K6; die deterministischen K1–K3 brauchen kein Golden Set.)
3. **Stichproben-Review:** pro Batch 50 Zufallsfälle + ALLE confidence='low' an menschliche Prüfung; Fehlerquote > 5 % → Batch verworfen, Prompt/Modell nachjustieren.
4. **Invarianten (automatisch, CI-fähig):** (a) nur Tags aus §1 (+ dokumentierte Fusionen §2), (b) Token-Text/Reihenfolge/xml:id byte-identisch (nur `@pos`, `@comp`, `@needsSplit`, `@reason` ändern sich), (c) Positionszählung unverändert (Index-Rebuild diff-leer außer erwarteten pos-Feldern), (d) kein ART/GRA/Artefakt im Output.
5. **Provenienz:** pro Batch ein Log unter `ingest/pos-disambig/<batch>/` (Modell, Prompt-Version, Datum, Diff-Statistik, Review-Ergebnis); revisionDesc-Change-Eintrag pro Datei. (Bewusst ein dritter Pfad-Typ unter `ingest/`: `scripts/ingest/<sigle>/` trägt Pipeline-Skripte, `ingest/<sigle>/` Roh-Quellen pro Text, `ingest/pos-disambig/` Kampagnen-Review-Logs.)

### 6.4 Technische Attribute (aus KZW-Fixierung 20.11.2025)

- Kontraktionen/Fusionen: Token bleibt EIN `<w>`; echte morphologische Fusionen tragen zwei Tags + `@reason` (§2); zusätzlich `@comp="VRB+PRO"` und `@needsSplit="true"`, wo die Zerlegung analytisch gewünscht ist. KEINE Token-Splits in der Edition. **Caveat:** `@comp` und `@needsSplit` sind noch NICHT in `schema/mhdbdb.rnc` (die `<w>`-Produktion erlaubt sie nicht) und kommen im Korpus bisher nicht vor – vor dem ersten K4-Batch muss das Schema erweitert (oder ein GAP dokumentiert) werden, sonst bricht die CI-Schema-Validierung.
- NEG: ausschließlich für Negationspartikeln (*niht, ne, en, n, nie* …); Negationsträger anderer Wortart bekommen NUR ihre Wortart (*dehein* → DET, *nieman* → PRO, *nie* → ADV). Bestands-Kombis wie `ADJ|NEG` werden in K6 aufgelöst.
- Fremdsprachliches: NICHT über `@pos`, sondern über `@xml:lang` (+ optional `<foreign>`) – siehe #28-Phasenplan; für die POS-Migration out of scope.

### 6.5 Aufgelöste Diskrepanzen und offene Punkte

**Aufgelöst (Policy folgt Tagset-Fixierung vom 20.11.2025 = §1):**
- ART ist kein Tag (Issue-§3-Tabelle war Zwischenstand) → K2.
- PART ist NICHT im 19-Set (Issue-§5 nannte es als Kandidat; die fixierte Liste enthält es nicht). Partikeln von Partikelverben werden bis auf Weiteres ADV getaggt; siehe nächster Punkt.
- GRA → ADJ (Issue-Body sagte an zwei Stellen ADV bzw. PART; §3 dieser Datei ist SSoT).
- **Kein 20. Tag PART** (KZW-Entscheid 08.07.2026, #27): Partikeln von Partikelverben werden per Konvention ADV + `@ana` markiert. Technische Randbedingung vor der Umsetzung: `@ana` ist bereits als Sense-Referenz belegt (`lexicon.xml#lemma_{N}_sense_{M}`, siehe DATA-MODEL.md → Sense-Auflösung) – die POS-Markierung braucht deshalb ein eigenes, davon unterscheidbares Wert-Schema (Festlegung vor dem ersten K4-Batch, analog zum `@comp`/`@needsSplit`-Caveat in 6.4).
- **Doppeltagging bei Kontraktionen zulässig** (KZW-Entscheid 08.07.2026, #27): Echte mhd. Kontraktionswörter – zwei Lemmata, sprachökonomisch zu einem Token zusammengezogen (*wiltu* = wilt + du) – behalten zwei Tags (§2). Ausdrücklich NICHT gemeint sind gewöhnliche Komposita (*hûsmûs* = einfach NOM). Das bestätigt die §2-Ausnahme als Policy.

**P-OFFEN (KZW-Entscheid nötig, blockiert die jeweilige Klasse NICHT als Ganzes):**
1. **CNJ-Restquote:** „Undifferenziertes CNJ" = Tokens, die nach der K5-Kampagne weiterhin das unspezifische `CNJ` tragen statt `CCNJ`/`SCNJ` – also genau die Fälle, in denen auch der Kontext nicht entscheidet, ob koordinierend oder subordinierend (KZW-Rückfrage 08.07.2026 damit bejaht). Offene Frage: Wieviel davon ist als K5-Fallback akzeptabel? Vorschlag: ≤ 10 % der ursprünglichen CNJ-Menge (943.199 Tokens, also ≤ ~94.000).
2. **Fusions-Paarliste finalisieren:** Das Prinzip ist entschieden (s.o.), offen bleibt die abschließende Liste der zulässigen Tag-Paare – insbesondere ob Modalverb-Kontraktionen wie *wiltu* als `VEM PRO` (so §2) oder generisch `VRB PRO` getaggt werden.

### 6.6 Ausdrücklich NICHT Teil dieser Policy

Kein Pilot-Lauf, keine Korpus-Änderung, keine Token-Kampagne im Rahmen von #27 (Scope-Entscheidung chsteiner 03.07.2026). Diese Policy ist die Vorlage, nach der künftige Kampagnen-Issues (pro Klasse eines) aufgesetzt werden. #18 (Datenmigration) hängt an K1–K3.

## Querverweise

- [TEI-MODEL.md §5](TEI-MODEL.md) – `@pos` im normativen TEI-Soll-Modell
- [DATA-MODEL.md](DATA-MODEL.md) – `@pos` im Annotations-Datenmodell und in der Backfill-Pipeline
- `.gemini/skills/pos-disambiguator/SKILL.md` – operativer Disambiguierungs-Workflow und linguistische Abgrenzungsregeln
