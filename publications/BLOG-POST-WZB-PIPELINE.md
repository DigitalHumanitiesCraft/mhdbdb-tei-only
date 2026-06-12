---
layout: post
title: "WB-DEA meets MHDBDB: 150.000 unannotierte Wörter und was daraus wurde"
author: "Julia Hintersteiner, Christopher Pollin"
date: 2026-05-12
published: false

citation:
  type: "blog-post"
  container-title: "Digital Humanities Craft"
  URL: "https://dhcraft.org/excellence/blog/WZB-Pipeline"
  language: "de"
  abstract: "Wie überführt man eine hochwertige digitale Edition in eine semantische Korpusinfrastruktur, ohne die editorische Substanz des einen oder die Suchmächtigkeit des anderen zu opfern? Dieser Beitrag beschreibt das CLARIAH-AT Miniprojekt zur Integration der Wenzelsbibel (Pentateuch: Gen–Dtn) in die Mittelhochdeutsche Begriffsdatenbank: den historischen Kontext einer 30-jährigen Dateninfrastruktur, eine dreiphasige LLM-gestützte Annotationspipeline, böhmische Schreibkonventionen als Stolpersteine, und warum Phase 3 gleichzeitig Infrastruktur und Dissertation ist."

dublin_core:
  creator: ["Julia Hintersteiner", "Christopher Pollin"]
  publisher: "Digital Humanities Craft"
  subject: ["Word Sense Disambiguation", "LLM", "Digital Humanities", "Middle High German", "TEI", "MHDBDB", "Wenzelsbibel", "CLARIAH-AT"]
  description: "CLARIAH-AT Miniprojekt: dreiphasige Annotationspipeline für die Integration der Wenzelsbibel in die MHDBDB — Lemmatisierung, POS-Tagging, Wortsinn-Disambiguierung als Dissertationsprojekt."
  type: "Blogpost"
  format: "text/html"
  rights: "CC BY 4.0"
  language: "de"

schema_type: "BlogPosting"
keywords: ["Wenzelsbibel", "WB-DEA", "MHDBDB", "CLARIAH-AT", "Annotation Pipeline", "LLM", "Word Sense Disambiguation", "TEI", "Mittelhochdeutsch", "Digital Humanities", "Linked Open Data"]

website_title: "Digital Humanities Craft"
website_type: "Blog"
short_title: "WB-DEA meets MHDBDB"
abstract: "Wie überführt man eine hochwertige digitale Edition in eine semantische Korpusinfrastruktur? CLARIAH-AT, eine böhmische Handschrift, eine dreiphasige LLM-Pipeline — und warum Phase 3 gleichzeitig Infrastruktur und Dissertation ist."
---

## Zwei Infrastrukturen, ein Text, eine Frage

Die **Wenzelsbibel Digital Edition and Annotation** (WB-DEA) und die **Mittelhochdeutsche Begriffsdatenbank** (MHDBDB) haben unterschiedliche Zielsetzungen. WB-DEA ist eine editorische Tiefenbohrung: diplomatische Transkription, normalisierte Formen, Rich Editorial Commentary in `<standOff>`-Strukturen — alles auf einen einzigen, außergewöhnlichen Text konzentriert. Die MHDBDB ist ein semantisches Suchnetz: ~670 mittelhochdeutsche Texte, 43.750 Lexikoneinträge, 192.674 Variantenformen, öffentlich durchsuchbar.

Die Frage des CLARIAH-AT Miniprojekts lautete: *Wie bringt man beide zusammen, ohne entweder die editorische Substanz des einen oder die semantische Infrastruktur des anderen zu beschädigen?*

Die Antwort: mit 20 Python-Skripten, drei Annotationsphasen, einem LLM-gestützten Review-Workflow — und mehr philologischen Überraschungen als erwartet.

---

## Kontext: 30 Jahre Datenarchäologie

Bevor man versteht, warum das WZB-Integrationsprojekt so aufgebaut ist, wie es ist, muss man verstehen, was die MHDBDB unter der Haube ist. Die Datenbank hat eine dreißigjährige Geschichte — und drei überlagerte Datenmodelle, die nacheinander entstanden sind:

1. **Relationales Modell** — Oracle-Datenbank der 1990er, Excel-Tabellen für Metadaten
2. **Graphenbasierte Erweiterung** — Linked Data als `.ttl`-Dateien (Personen, Werke, Konzepte als RDF-Ressourcen mit GND, Wikidata, `owl:sameAs`)
3. **Hierarchische Strukturen** — TEI/XML pro Text, mit projekt-eigenen Annotationskonventionen

Das 2025er CLARIAH-AT Projekt hat zunächst diese Schichten rückwärts entrollt: sechs komplexe SPARQL-Queries für die GraphDB-Extraktion, Python-Transformationsskripte für CSV → TEI-XML, das manuelle Nachvollziehen undokumentierter Relationen zwischen Werk-Metadaten (`.ttl`), Lemma-Referenzen und externen Normdaten (GND, Wikidata, Handschriftencensus). Das Ergebnis: sieben TEI Authority Files — `lexicon.xml`, `variants.xml`, `concepts.xml`, `genres.xml`, `persons.xml`, `works.xml`, `names.xml` — und eine öffentliche Suchoberfläche, die 47 MB XML-Parsing im Browser (30 Sekunden Ladezeit) durch vorberechnete JSON-Indizes (2,9 MB komprimiert, <3 Sekunden) ersetzt.

Diese Infrastruktur war die Voraussetzung dafür, dass die Wenzelsbibel überhaupt integriert werden konnte.

---

## Das Objekt

Die Wenzelsbibel ist vielleicht das aufwändigste Buchprojekt des deutschsprachigen Mittelalters. Um 1389–1395 im Auftrag König Wenzels IV. von Böhmen entstanden, umfasst sie sechs Prachtbände (Wien, ÖNB, Cod. 2759–2764) mit insgesamt 1.214 Blättern und über 650 ganzseitigen Miniaturen. Sie enthält eine der frühesten volkssprachlichen Vollübersetzungen der Bibel ins Deutsche — eine Prosaübersetzung der Vulgata, die sprachlich am Übergang von Mittelhochdeutsch zu Frühneuhochdeutsch steht.

Für die MHDBDB relevant sind die fünf Bücher des Pentateuch: Genesis, Exodus, Levitikus, Numeri, Deuteronomium. Sprachlich bairisch-österreichisch mit deutlich böhmischem Kolorit — das Ergebnis einer höfischen Werkstatt, die für Wenzels Kanzleisprache schrieb. Und das wird uns noch beschäftigen.

Seit Mai 2026 ist die Wenzelsbibel in der MHDBDB zugänglich — mit GND-Eintrag (4117632-7), Wikidata-Link (Q476495) und Handschriftencensus-Eintrag (werke/4577), verknüpft mit dem gesamten LOD-Netz der Mittelalterforschung.

---

## Der Ausgangszustand: 150.000 leere `<w>`-Elemente

Nach der strukturellen TEI-Konversion der WB-DEA-Quelldaten lag ein valides MHDBDB-TEI-Dokument vor: 236.000 Zeilen, ~150.000 `<w>`-Elemente. Aber alle ohne Annotationen.

```xml
<!-- Ausgangszustand: WB-DEA-Transformation -->
<w xml:id="WZB_1ra_6_5">herczen</w>

<!-- Ziel: MHDBDB-konform -->
<w xml:id="WZB_1ra_6_5"
   lemmaRef="lexicon.xml#lemma_8132"
   pos="NOM"
   meaningRef="lexicon.xml#lemma_8132_sense_12440"
   wordRef="lexicon.xml#lemma_8132_sense_12440_type_19876">herczen</w>
```

Vier fehlende Attribute, jedes mit seiner eigenen Funktion: `@lemmaRef` macht den Text lemmasuchbar, `@pos` ermöglicht grammatische Filterung, `@meaningRef` öffnet die Konzeptnavigation, `@wordRef` verbindet Wortformvarianten. Ohne sie ist die Wenzelsbibel im Korpus vorhanden, aber blind.

Die Aufgabe war keine singuläre Fleißarbeit. Rund ein **Drittel des gesamten MHDBDB-Korpus** verfügt noch nicht über `@meaningRef`-Annotationen — die Wenzelsbibel ist der erste kontrollierte Testfall für eine Pipeline, die diese Lücke systematisch schließen soll.

---

## Die Pipeline: Drei Phasen, eine Logik

Die Annotationspipeline folgt dem Prinzip, das Christopher Pollin in seinem [Beitrag zum Synthetischen Philologen][synth-phil] beschrieben hat: das LLM nicht als Orakel, sondern als **stochastische Komponente in einem deterministischen Workflow**. Automatisierung so weit wie möglich, LLM-Assistenz an den Ambiguitätsgrenzen, menschliches Review an den Unsicherheitsstellen.

[synth-phil]: https://dhcraft.org/excellence/blog/The-Synthetic-Philologist

Alle Entscheidungen gehen durch eine TSV-Zwischenschicht — menschlich lesbar, versionierbar, mit `--dry-run`-Modus testbar. Kein Schritt schreibt direkt ins TEI; alles läuft durch überprüfte Batch-Dateien. Git-Commits nach jeder Phase sichern den Rollback.

### Phase 1: Lexikonbasiertes Auto-Matching

Das Matching-Skript (`wzb-auto-match.py`) liest jede `<w>`-Wortform, normalisiert sie nach der MHDBDB-Konvention (`â→a, ê→e, î→i, ô→o, û→u`) und sucht in `variants.xml` (192.674 Einträge):

- **Eindeutiger Treffer**: `@lemmaRef` direkt gesetzt — kein menschlicher Eingriff.
- **Mehrdeutiger Treffer**: mehrere Lemma-Kandidaten — wandert in die Disambiguierungs-TSV.
- **Kein Treffer**: nicht im Variantenwörterbuch — Phase 1b.

Das Ergebnis: rund 60 % der Tokens direkt zuordenbar. **72.358 Zeilen** für Phase 1b.

Erste Überraschung: WB-DEA-Wortformen liegen in manuskriptnaher Schreibung vor (*herczen* statt *hêrzen*), `variants.xml` enthält nicht-normalisierte MHG-Formen — beide Seiten müssen erst auf denselben Nenner gebracht werden, bevor ein Abgleich möglich ist.

### Phase 1b: LLM-gestützte Lemma-Disambiguierung

72.358 offene Fälle, von denen viele nicht mechanisch lösbar sind. Die Lösung: ein gestaffeltes Triage-Schema nach dem gleichen Prinzip wie die dreistufige Lemma-Auflösung der MHDBDB-Suche selbst — exakter Match zuerst, dann Varianten, dann Fallback.

| Population | Strategie |
|---|---|
| Hochfrequente Ambiguitäten (21+ Tokens) | **Bulk-Resolve**: eine LLM-Entscheidung für alle Vorkommen |
| Mittelfrequenz (2–20 Tokens) | **Kontextbasiert**: LLM liest jeden Kontext einzeln |
| Hapax ambigua (count = 1) | **Zurückgestellt** (ROI zu gering) |
| Ungematchte Mittelfrequenz (6–20) | Wörterbuchnetz-Abgleich oder `NEW` |
| Ungematchter Langschwanz (1–5) | **Akzeptierter Residual** |

Workflow: TSV-Batch (50 Zeilen) → Claude liest Kontextfenster (±5 Tokens), schlägt Lemma + Konfidenz (`high/medium/low`) vor. Julia überprüft alle `low`-Entscheidungen und eine 20 %-Stichprobe der `medium`-Fälle, bevor `wzb-bulk-resolve.py` schreibt.

**@lemmaRef-Coverage nach Phase 1 + 1b: 95,3 %** (142.185 / 149.148 Tokens).

#### Die böhmischen Überraschungen

Die Wenzelsbibel hatte drei Kategorien von Annotationsproblemen, die kein Standard-MHG-Text hätte:

**Böhmische Schreibkonventionen.** `cz → z`, `v → u`, `ou → û`, `vor- → ver-`. Wörter wie *czeit*, *vnd*, *vortilgen* finden sich so in keinem Wörterbuch — obwohl sie ganz gewöhnliche mhd. Wörter sind. Die Normalisierung musste um diese Bohemismen erweitert werden.

**Tschechische Interlinearglossen.** In den Exodus- und Numeri-Abschnitten tauchen Marginalglossen in Altböhmisch auf: *toho*, *pzde*, *bzde*, *thoho*, *zde* — Notizen aus dem Scriptorium für Wenzels zweisprachige Kanzlei. Sie sind keine MHG-Lexeme. Lösung: ein neues Lemma `lemma_78628` (cs NOM) als Platzhalter für altböhmisches Paratextmaterial.

**Schreibermarken und lateinische Rubriken.** `ł`, `჻`, `=`, `CAPITULUM`, `LEUITICUS`, `GENE+SIS` (foliozeilenübergreifend aufgeteilt) — keine lexikalischen Einheiten. Sie gehen zu `lemma_2` (Catch-All) oder `lemma_13826` (Kapitelapparat).

Diese drei Kategorien waren im Vorfeld nicht sichtbar. Das ist typisch für historische Handschriften, und besonders charakteristisch für ein Auftragswerk an der kulturellen Schnittstelle zwischen deutschem und böhmischem Sprachraum.

**Neu in `lexicon.xml`:** vier Einträge für böhmisch-spezifisches Vokabular — *cs* (altböhmische Glossen), *herte* (Weideherde), *scot* (Schekel, böhmische Münzeinheit), *weise* (Waise, distinct from *weise* adj. = klug).

### Phase 2: POS-Tagging

Mit `@lemmaRef` gesetzt, war Phase 2 teilweise automatisiert: Lemmata mit genau einem POS-Eintrag im Lexikon werden direkt zugewiesen. Das deckt ~75 % der Fälle ab.

Die restlichen 25 % — Lemmata mit mehreren möglichen Wortarten — gingen in eine Pending-TSV. Kritische Grenzfälle: *daz* (DET oder SCNJ, 4.561 Tokens), *ein* (DET oder NUM, 2.377 Tokens), *ir* (POS oder PRO, 1.162 Tokens). Das MHDBDB-Tagset mit seinen 19 Tags ist dabei kein Standard-STTS — kein `ART` (immer `DET`), kein `GRA` (meist `ADV`) — und LLMs neigen ohne explizite Einschränkung zu STTS-Kategorien aus dem Moderndeutsch.

Mitten in der Arbeit eine Korrektur: `ART` war initial verwendet worden und existiert im MHDBDB-Tagset schlicht nicht. Ein Migration-Patch (`cf71ae48`) korrigierte alle bereits gesetzten Tags rückwirkend. Solche Korrekturen sind typisch für Projekte, in denen Schema und Daten parallel entstehen.

**@pos-Coverage: 95,3 %** (142.185 / 149.148). QA: 0 ungültige Tags, 0 unbekannte `@lemmaRef`-Werte.

---

## Schema-Evolution dokumentieren, nicht verstecken

Die WZB-Arbeit verlief parallel zu einer aktiven Weiterentwicklung des MHDBDB-Schemas. Das erzeugt Divergenz:

| Element | Alte Kodierung | Korrekte Kodierung |
|---|---|---|
| Interpunktion | `<seg type="pc">` | `<pc join="left&#124;right">` |
| Genre-Link in `works.xml` | `<ref target="genres.xml#...">` | `<ptr target="genres.xml#..."/>` |
| Handschriftenangabe | `<note type="manuscript">` | nicht auf `<bibl>`-Ebene erlaubt |
| Artikel-POS-Tag | `ART` | `DET` |

Jede Korrektur erforderte rückwirkende Anpassungen in TEI und Authority Files. Die Lösung: eine explizite Schema-Änderungshistorie in der Projektdokumentation — dokumentiert, nachvollziehbar, reproduzierbar. Der wichtige Gedanke dahinter: Schema-Divergenz ist kein Fehler, sie ist der Normalzustand lebendiger Infrastrukturprojekte. Die Reaktion darauf muss Versionierung sein, nicht Verschweigen.

---

## Phase 3: Bedeutungsdisambiguierung — Infrastruktur und Dissertation

Phase 3 ist anders. Sie ist nicht nur Infrastruktur — sie ist gleichzeitig empirisches Testbett für Julias Doktorat über LLM-gestützte Word Sense Disambiguation (WSD) in historischen Sprachstufen.

Die Ausgangslage: Von den 43.754 Lexikoneinträgen der MHDBDB haben 35.985 (82,3 %) genau eine Bedeutung — die werden direkt auto-assignt. Die 7.765 polysemen Einträge erfordern Disambiguierung. Da hochfrequente Wörter regelmäßig polysem sind, ist der Anteil der Tokens, die Disambiguierung brauchen, deutlich höher als der Anteil der Eintragstypen.

Und: Rund **ein Drittel der 670 MHDBDB-Texte** hat noch kein `@meaningRef`. Das ist keine Kleinigkeit — es bedeutet, dass für diese Texte Konzeptnavigation, semantische Suche und Sinnverwandtschaftsanzeigen schlicht nicht funktionieren. Die Wenzelsbibel ist der erste systematische Anlauf, diese Lücke mit einem LLM-gestützten Workflow zu schließen.

### Die Mehrheitssinn-Baseline

Bevor LLM-Entscheidungen bewertet werden können, braucht es eine Baseline. Wir haben sie aus dem gesamten MHDBDB-Korpus (675 Texte, menschlich annotiert) berechnet: Für jedes Lemma den häufigsten Sinn genommen, als ob er immer gilt — **gewichtete Genauigkeit: 66,7 %**. Das ist die Hürde.

### Bulk vs. Instance — und ABSTAIN

Phase 3 unterscheidet zwei Entscheidungstypen:

**Bulk-LLM**: Lemma-weite Entscheidungen, wenn der Kontext einheitlich genug ist (*hant* → immer menschliche Hand, 99,6 % Korpusmehrheit). Skaliert auf hunderte Tokens mit einer Entscheidung. Kann die Baseline nicht direkt geschlagen werden — strukturell anderes Verfahren.

**Instance-LLM**: Token-genaue Entscheidungen für kontextabhängige Lemmata (*vater*: biologischer Vater oder theologisches Gottesbild in Prologen). Nur diese sind direkt mit der Mehrheitssinn-Baseline vergleichbar.

Ein drittes Instrument: **ABSTAIN**. Wenn ein Kontext keine zuverlässige Entscheidung erlaubt, darf die Pipeline explizit abstain. Abstentionen gehen nicht in den TEI-Output und nicht in den Genauigkeitszähler — sie sind wissenschaftlich ehrlicher als eine erzwungene Rateentscheidung. Das ist der Unterschied zwischen einem Annotation-Autopiloten und einem wissenschaftlichen Werkzeug.

**@meaningRef-Coverage nach sechs Bulk-Batches: 76,2 %** (113.702 / 149.148). Die hochambigen Hochfrequenzlemmata (*in*, *haben*, *werden*) warten noch auf per-Token-Entscheidungen — das ist der Kern der Dissertation.

Das Evaluationsdesign ist prä-registriert: N=400–600, stratifiziert nach Sensanzahl × Wortart, Blind-Review (Julia trifft ihre Entscheidung, bevor sie die LLM-Entscheidung sieht) → drei Datenpunkte pro Token (LLM, Julia, Gold-Standard MHDBDB).

---

## Was die Wenzelsbibel jetzt kann

Seit Mai 2026 ist die Wenzelsbibel als Sigle **WZB** im MHDBDB-Suchnetz:

- **Lemma-Suche** über 142.185 annotierte Tokens — jede Anfrage bezieht die WZB automatisch ein
- **Lemma-Highlighting** in der Leseansicht (bis zu 5 gleichzeitige Suchbegriffe, farbcodiert)
- **Konzeptnavigation** über das hierarchische Begriffssystem (Semantischer Zugang zu biblisch-mittelhochdeutschem Wortschatz)
- **Gattungsklassifikation**: Bibelübersetzung — in der Gattungssuche auffindbar
- **Normdaten**: Wikidata Q476495, GND 4117632-7, Handschriftencensus werke/4577, verknüpft im LOD-Netz
- **Wörterbuch-Links** auf Lemma-Pages: Lexer (live via HTTPS-API mit direkten Eintragslinks) + MWB (Sucheinstieg)

Das ist kein kleines Plus. Die Wenzelsbibel war in keiner computationellen Korpusressource lemmasuchbar — jetzt ist sie vollwertiger Teilnehmer in einem Suchnetz über das gesamte mittelhochdeutsche Schrifttum.

---

## Fazit: Was dieses Projekt gezeigt hat

**Infrastruktur-Interoperabilität ist lösbar** — aber sie erfordert explizite Schema-Arbeit, nicht nur Datentransformation. Welches Format hat ein "Wort" in WB-DEA? Was ist ein "Lemma" in der MHDBDB? Diese Fragen haben keine technische Antwort; sie sind philologische Entscheidungen, die man treffen und dokumentieren muss.

**LLM-gestützte Annotation skaliert** — 91,6 % Lemma-Abdeckung und 95,3 % POS-Abdeckung in einem historischen Text mit 150.000 Tokens, mit menschlichem Review an den Schwachstellen. Das LLM liest den Kontext und schlägt vor; es entscheidet nicht allein.

**Residuale Ambiguität ist legitim.** Die 8,4 % unaufgelösten Tokens sind kein Projektversagen. Pronomen wie *in* mit 3.486 Vorkommen in dreifacher Kasusdoppeldeutigkeit sind ohne Satzsyntax-Analyse nicht automatisch auflösbar. Diese Grenze korrekt zu benennen ist eine wissenschaftliche Aussage — besser als eine erzwungene Entscheidung.

**Parallelentwicklung von Schema und Daten braucht explizite Versionierung.** Der `ART→DET`-Patch, der `<ref>→<ptr>`-Wechsel, die `<note type="manuscript">`-Abschaffung — all das passiert in einem lebenden Projekt. Dokumentiert, ist es nachvollziehbar. Undokumentiert, ist es technische Schuld.

Und die eigentlich interessante Frage bleibt offen: Schlägt die Pipeline die Mehrheitssinn-Baseline von 66,7 %? Die Antwort trägt eine Dissertation.

---

*Die Wenzelsbibel (Pentateuch: Gen–Dtn) ist als Sigle **WZB** in der [MHDBDB-Korpussuche](https://dhcraft.org/mhdbdb-tei-only/korpus.html?text=WZB) zugänglich. Pipeline-Skripte und Annotationsdaten: [github.com/DigitalHumanitiesCraft/mhdbdb-tei-only](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only). Das Miniprojekt wurde im Rahmen von CLARIAH-AT gefördert. Kontakt: [mhdbdb@plus.ac.at](mailto:mhdbdb@plus.ac.at)*
