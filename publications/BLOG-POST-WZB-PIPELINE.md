---
layout: post
title: "149.000 Wörter, null Annotationen: Die Wenzelsbibel trifft die MHDBDB"
author: "Julia Hintersteiner, Christopher Pollin"
date: 2026-05-12
published: false

citation:
  type: "blog-post"
  container-title: "Digital Humanities Craft"
  URL: "https://dhcraft.org/excellence/blog/WZB-Pipeline"
  language: "de"
  abstract: "Wie annotiert man 149.000 mittelhochdeutsche Wörter eines der prächtigsten Manuskripte des Mittelalters — von null auf MHDBDB-konform — in einer semiautomatischen Pipeline? Dieser Beitrag beschreibt die dreiphasige Annotationspipeline für die Wenzelsbibel (Pentateuch: Gen–Dtn), die Herausforderungen böhmischer Schreibkonventionen und tschechischer Interlinearglossen, und warum Phase 3 (Bedeutungsdisambiguierung) gleichzeitig Infrastrukturprojekt und Doktorarbeit ist."

dublin_core:
  creator: ["Julia Hintersteiner", "Christopher Pollin"]
  publisher: "Digital Humanities Craft"
  subject: ["Word Sense Disambiguation", "LLM", "Digital Humanities", "Middle High German", "TEI", "MHDBDB", "Wenzelsbibel"]
  description: "Dreiphasige Annotationspipeline für die Wenzelsbibel im MHDBDB-Korpus: automatisches Lemma-Matching, LLM-gestützte POS-Disambiguierung und Word Sense Disambiguation als empirisches Testbett für Doktoratsforschung."
  type: "Blogpost"
  format: "text/html"
  rights: "CC BY 4.0"
  language: "de"

schema_type: "BlogPosting"
keywords: ["Wenzelsbibel", "MHDBDB", "Word Sense Disambiguation", "LLM", "TEI Annotation", "Mittelhochdeutsch", "Lemmatisierung", "POS-Tagging", "Digital Humanities"]

website_title: "Digital Humanities Craft"
website_type: "Blog"
short_title: "149.000 Wörter, null Annotationen"
abstract: "Wie annotiert man 149.000 mittelhochdeutsche Wörter eines der prächtigsten Manuskripte des Mittelalters in einer semiautomatischen Pipeline? Dieser Beitrag beschreibt die dreiphasige Annotationsstrecke für die Wenzelsbibel im MHDBDB-Korpus."
---

## Das Objekt

Die Wenzelsbibel ist vielleicht das aufwändigste Buchprojekt des deutschsprachigen Mittelalters. Um 1389–1395 im Auftrag König Wenzels IV. von Böhmen entstanden, umfasst sie sechs Prachtbände (Wien, ÖNB, Cod. 2759–2764) mit insgesamt 1.214 Blättern, über 650 ganzseitigen Miniaturen und einer der frühesten volkssprachlichen Vollübersetzungen der Bibel ins Mittelhochdeutsche. Die Übersetzung des Pentateuch — Genesis, Exodus, Levitikus, Numeri, Deuteronomium — die in der MHDBDB jetzt zugänglich ist, entstand in einer höfischen Werkstatt, deren Sprache die Prager Kanzleisprache der Luxemburger-Zeit widerspiegelt: Mittelhochdeutsch mit deutlich böhmischem Kolorit.

Das Objekt war, kurz gesagt, faszinierend und für eine automatische Annotationspipeline ausgesprochen unangenehm.

## Das Problem: null zu 149.000

Die Ausgangssituation nach der strukturellen TEI-Konversion (Phase 0): Eine valide XML-Datei mit ~149.000 `<w>`-Elementen, jedes davon leer von Annotationen.

```xml
<!-- vorher -->
<w xml:id="WZB_1ra_6_5">herczen</w>

<!-- nachher (Ziel) -->
<w xml:id="WZB_1ra_6_5"
   lemmaRef="lexicon.xml#lemma_3023"
   pos="NOM"
   meaningRef="lexicon.xml#lemma_3023_sense_4892"
   wordRef="lexicon.xml#lemma_3023_sense_4892_type_10422">herczen</w>
```

Vier Attribute fehlen: `@lemmaRef` (Lemma), `@pos` (Wortart), `@meaningRef` (Bedeutung), `@wordRef` (Wortform-Typ). Die MHDBDB-Suche, Lemma-Highlighting und Konzeptnavigation funktionieren nur, wenn diese Attribute vollständig und korrekt befüllt sind. Eine rein manuelle Annotation schied aus — selbst bei zehn Entscheidungen pro Minute würde das Befüllen von vier Attributen für 149.000 Tokens Monate dauern.

Die Lösung war eine dreiphasige Pipeline, die Automatisierung, LLM-Assistenz und menschliche Kuratierung in einem klaren Eskalationsschema kombiniert.

---

## Phase 1: Automatisches Lemma-Matching

Der erste Schritt nutzte die MHDBDB-Ressourcen, die bereits existierten: `variants.xml` mit ~192.000 mittelhochdeutschen Wortformen, jede verknüpft mit einem oder mehreren Lemma-IDs aus `lexicon.xml`. Das Auto-Match-Skript (`wzb-auto-match.py`) liest jede Wortform aus der WZB, normalisiert sie nach der MHG-Konvention (`â→a, ê→e, î→i, ô→o, û→u`) und sucht in `variants.xml`:

- **Eindeutiger Treffer**: `@lemmaRef` direkt gesetzt — kein menschlicher Eingriff nötig.
- **Mehrdeutiger Treffer**: Form existiert in `variants.xml`, verweist aber auf mehrere Lemmata — wandert in die Disambiguierungs-TSV.
- **Kein Treffer**: Form ist nicht im Variantenwörterbuch — Kandidat für Phase 1b oder Restvokabular.

Ergebnis der Phase 1: Rund 60 % der Tokens direkt zuordenbar. 72.358 Zeilen für Phase 1b.

### Die böhmische Herausforderung

Was die WZB von anderen MHDBDB-Texten unterscheidet, ist ihre Schreibsprache. Die böhmischen Schreibkonventionen der Wenzelszeit folgen eigenen Regeln: `cz` steht für `z`, `v` für `u`, `ou` für `û`, das Präfix `vor-` für `ver-`. Das Normalisierungsskript musste um diese Bohemismen erweitert werden — ohne diese Erweiterung hätten Formen wie *czeit* (= Zeit), *vnd* (= und) oder *vortilgen* (= vertilgen) keine Lexikon-Treffer erzeugt.

Noch eigenartiger: Zwischen den deutschen Versen tauchen in den Exodus- und Numeri-Abschnitten Interlinearglossen in Altböhmisch auf (*toho*, *pzde*, *bzde*, *thoho*) — Randnotizen aus dem böhmischsprachigen Scriptorium. Sie wurden als nicht-mhd. Paratexte erkannt und zu `lemma_2` (Unaufgelöstes/Sonstiges) aufgelöst, damit sie die Lemma-Statistik nicht verfälschen.

## Phase 1b: LLM-gestützte Lemma-Disambiguierung

72.358 ambige oder ungematchte Tokenzeilen. Unmöglich manuell, zu komplex für Regelbasiertes. Die Lösung: ein gestaffeltes Triage-Schema mit Claude als erstem Reviewer.

Die hochfrequenten Mehrdeutigkeiten (>20 Tokens pro Form) wurden zuerst abgearbeitet — 45 Batches, je nach Schwierigkeitsgrad zwischen 50 und 200 Lemmata. Das Muster war immer gleich: Claude liest einen Kontext-Chunk (±5 Tokens), schlägt ein Lemma vor, begründet kurz, markiert mit `confidence=high/medium/low`. Julia prüft alle `low`-Entscheidungen und eine Stichprobe der `medium`-Fälle vor der Anwendung.

Am Ende der Phase 1b: **91,6 %** der 72.358 Zeilen aufgelöst, vier neue Lemmata in `lexicon.xml` angelegt (*cs* für tschechische Glossen, *herte* für Weideherde, *scot* für Schekel, *weise* für Waise) und das Restvokabular (Levitische Hapaxe, Lateinlatin-Fragmente, böhmische Eigennamen) als akzeptierte Lücke dokumentiert.

**@lemmaRef-Coverage nach Phase 1 + 1b: 95,3 %** (142.185 / 149.148 Tokens).

---

## Phase 2: Wortart-Tagging

Mit `@lemmaRef` gesetzt war Phase 2 teilweise schon automatisiert: Lemmata mit nur einem einzigen POS-Wert im Lexikon (`lexicon.xml/<gramGrp>/<pos>`) bekommen `@pos` direkt ohne LLM-Beteiligung. Das deckt rund 75 % der Fälle ab.

Die restlichen 25 % — Lemmata mit mehreren möglichen Wortarten (z.B. *daz*: DET oder SCNJ je nach Satzposition; *haben*: NOM, VEX oder VRB je nach Funktion) — gingen in eine Pending-TSV. Claude arbeitete diese in 11 Batches durch, jedes Mal mit einem ±4-Token-Kontextfenster und dem MHDBDB-Tagset (19 Tags) als harter Einschränkung.

Das 19-Tag-Set des MHDBDB ist dabei absichtlich konservativ: Es unterscheidet `SCNJ` (subordinierend), `CCNJ` (koordinierend) und `CNJ` (Fallback für Echte Ambiguität), aber es kennt kein `ART` (→ immer `DET`) und kein `GRA` (→ meist `ADV`). Diese Restriktionen müssen dem Modell explizit mitgegeben werden — sonst tendiert es zu STTS-Kategorien aus dem Moderndeutsch.

**@pos-Coverage: 95,3 %** (142.174 / 149.148 Tokens). Die verbleibenden 4,7 % sind dieselben Tokens ohne `@lemmaRef` aus Phase 1b — eine kausal saubere Lücke.

---

## Phase 3: Bedeutungsdisambiguierung — das Dissertationsprojekt

Phase 3 ist anders. Sie ist nicht nur Infrastruktur, sie ist gleichzeitig empirisches Testbett für Julias Doktorat über LLM-gestützte Word Sense Disambiguation (WSD) in historischen Sprachstufen.

Das Setup: Von den 43.754 Lexikoneinträgen der MHDBDB haben 35.985 (82,3 %) genau eine Bedeutung — die werden direkt auto-assignt. Die 7.765 polysemen Einträge (17,7 %) erfordern Disambiguierung. Da hochfrequente Wörter (Verben, Pronomen, Präpositionen) regelmäßig polysem sind, ist der Anteil der Tokens, die Disambiguierung brauchen, deutlich höher als der Anteil der Eintragstypen.

### Die Mehrheitssinn-Baseline

Bevor LLM-Entscheidungen bewertet werden können, braucht es eine Baseline. Wir haben sie aus dem gesamten MHDBDB-Korpus (675 Texte, menschlich annotiert) berechnet: Für jedes Lemma den häufigsten Sinn genommen, als ob er immer gilt. Das ergibt eine **gewichtete Genauigkeit von 66,7 %** — die Hürde, die die Pipeline überspringen muss, um ihren Nutzen zu belegen.

Die Pipeline muss besser sein als "immer die häufigste Bedeutung".

### Die Entscheidungsarchitektur

Phase 3 unterscheidet zwischen zwei Entscheidungstypen:

- **Bulk-LLM**: Lemma-weite Entscheidungen, wenn der Kontext im WZB einheitlich genug ist (z.B. *hant* → immer menschliche Hand; 99,6 % Korpusmehrheit, alle 8 WZB-Stichproben bestätigen). Skaliert auf hunderte Tokens mit einer einzigen Entscheidung.
- **Instance-LLM**: Token-genaue Entscheidungen für Lemmata, deren Bedeutung vom lokalen Satzkontext abhängt (z.B. *vater*: biologischer Vater oder theologischer Gottvater in Prologen).

Wichtig für die wissenschaftliche Berichterstattung: Beide Typen werden getrennt ausgewertet. Nur *Instance-LLM*-Entscheidungen sind mit der Mehrheitssinn-Baseline vergleichbar — *Bulk-LLM* ist strukturell etwas anderes.

Ein drittes Instrument: **ABSTAIN**. Wenn ein Kontext keine zuverlässige Entscheidung erlaubt (elliptische Konstruktionen, fehlende Anaphernauflösung), darf die Pipeline explizit abstain. Abstentionen gehen nicht in den TEI-Output und nicht in den Genauigkeitszähler — sie sind wissenschaftlich ehrlicher als eine erzwungene Rateentscheidung.

### Stand der Dinge

Sechs Bulk-Batches appliziert (3.773 Tokens manuell entschieden, dann bulk-geschrieben):

| Lemma | Sinn | Konfidenz | Tokens |
|---|---|---|---|
| *hant* | menschliche Hand | hoch | 426 |
| *tag* | Tag/Zeit | hoch | 598 |
| *an* | direktional/spatial | hoch | 967 |
| *wollen* | Modalverb Wille | hoch | 478 |
| *sollen* | Obligation/Befehl | hoch | 954 |
| *vater* | biologischer Vater/Patriarch | mittel | 350 |

**@meaningRef-Coverage: 76,2 %** (113.702 / 149.148). Noch ausstehend: die hochambigen Hochfrequenzlemmata (*in*, *haben*, *werden*), die per-Instance-LLM entschieden werden müssen — das ist der methodisch aufwändigste Teil und der Kern der Doktorarbeit.

---

## Was dabei entstanden ist

Neben den Annotationen selbst hat das Projekt eine Infrastruktur hinterlassen, die für zukünftige Ingest-Projekte direkt nachnutzbar ist:

- **20+ Pipeline-Skripte** unter `scripts/ingest/wzb/` für alle drei Phasen: Auto-Match, Bulk-Resolve, Patch, Apply, Baseline-Berechnung, Schema-Migration
- **Pre-flight checks**: `check-lexicon-senses.py` verhindert, dass Lexikoneinträge ohne `<sense>` ins Schema rutschen — gefunden während des WZB-Ingests, seitdem im CI
- **`wzb-add-lemma.py`**: Scripted lemma creation mit automatischer ID-Vergabe, Concept-Validierung und Post-write-Check
- **Evaluation-Protokoll** (prä-registriert): N=400–600, stratifiziert nach Sensanzahl (2/3–5/6+) × Wortart (NOM/VRB/ADJ+PRP), Blind-Review-Verfahren (Julia entscheidet, bevor sie die LLM-Entscheidung sieht) → drei Datenpunkte pro Token (LLM / Julia / Gold)
- **Normdaten** für `works.xml`: Wikidata Q476495, GND 4117632-7, Handschriftencensus werke/4577

---

## Fazit: Wenn Text auf Skript trifft

Was haben wir gelernt?

**Erstens:** Historische Texte brauchen textkritisches Scaffolding. Ein LLM, das ohne Kenntnis der böhmischen Schreibkonventionen, ohne das MHDBDB-Tagset und ohne das Lexikon als Constraint-System arbeitet, produziert plausible, aber philologisch falsche Entscheidungen. Das Scaffolding ist wichtiger als das Modell.

**Zweitens:** Die Trennung von Entscheidungstypen ist wissenschaftlich notwendig. Bulk-LLM und Instance-LLM haben unterschiedliche epistemische Qualitäten; sie zusammenzuwerfen würde die Evaluation unlesbar machen. Die Infrastruktur muss diesen Unterschied von Anfang an kodieren — was im WZB-Projekt durch die `decision_type`-Spalte in der Pending-TSV geschieht.

**Drittens:** Abstention ist keine Schwäche. "Ich weiß es nicht" ist eine legitime wissenschaftliche Aussage. Ein Annotationssystem, das zur Entscheidung zwingt, produziert Rauschen, kein Wissen.

Die Wenzelsbibel steht jetzt live im MHDBDB-Korpus, mit 95,3 % Lemma- und POS-Coverage, 76,2 % Bedeutungsauflösung und einer offenen wissenschaftlichen Frage, die eine ganze Dissertation trägt: Schlägt die Pipeline die Mehrheitssinn-Baseline? Die Antwort kommt mit Abschluss der Phase 3.

---

*Die Wenzelsbibel ist als Sigle **WZB** in der [MHDBDB-Korpussuche](https://dhcraft.org/mhdbdb-tei-only/korpus.html?text=WZB) zugänglich. Pipeline-Skripte und Annotationsdaten: [github.com/DigitalHumanitiesCraft/mhdbdb-tei-only](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only). Feedback und Fragen: [mhdbdb@plus.ac.at](mailto:mhdbdb@plus.ac.at)*
