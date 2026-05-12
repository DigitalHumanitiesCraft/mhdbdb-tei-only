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
  abstract: "Wie überführt man eine hochwertige digitale Edition in eine semantische Korpusinfrastruktur, ohne die editorische Substanz des einen oder die Suchmächtigkeit des anderen zu opfern? Dieser Beitrag beschreibt das CLARIAH-AT Miniprojekt zur Integration der Wenzelsbibel (Pentateuch: Gen–Dtn) in die Mittelhochdeutsche Begriffsdatenbank: eine dreiphasige, LLM-gestützte Annotationspipeline, böhmische Schreibkonventionen als Stolpersteine, und warum die größten Hindernisse bei solchen Projekten nicht technischer, sondern epistemischer Natur sind."

dublin_core:
  creator: ["Julia Hintersteiner", "Christopher Pollin"]
  publisher: "Digital Humanities Craft"
  subject: ["Word Sense Disambiguation", "LLM", "Digital Humanities", "Middle High German", "TEI", "MHDBDB", "Wenzelsbibel", "CLARIAH-AT"]
  description: "CLARIAH-AT Miniprojekt: dreiphasige Annotationspipeline für die Integration der Wenzelsbibel in die MHDBDB — Lemmatisierung, POS-Tagging, Wortsinn-Disambiguierung."
  type: "Blogpost"
  format: "text/html"
  rights: "CC BY 4.0"
  language: "de"

schema_type: "BlogPosting"
keywords: ["Wenzelsbibel", "WB-DEA", "MHDBDB", "CLARIAH-AT", "Annotation Pipeline", "LLM", "Word Sense Disambiguation", "TEI", "Mittelhochdeutsch", "Digital Humanities"]

website_title: "Digital Humanities Craft"
website_type: "Blog"
short_title: "WB-DEA meets MHDBDB"
abstract: "Wie überführt man eine hochwertige digitale Edition in eine semantische Korpusinfrastruktur? Ein CLARIAH-AT Miniprojekt, eine böhmische Handschrift, und eine dreiphasige LLM-Pipeline."
---

## Zwei Infrastrukturen, ein Text, eine Frage

Die **Wenzelsbibel Digital Edition and Annotation** (WB-DEA) und die **Mittelhochdeutsche Begriffsdatenbank** (MHDBDB) haben auf den ersten Blick unterschiedliche Zielsetzungen. WB-DEA ist eine editorische Tiefenbohrung: diplomatische Transkription, normalisierte Formen, Rich Editorial Commentary in `<standOff>`-Strukturen — alles auf einen einzigen, außergewöhnlichen Text konzentriert. Die MHDBDB ist ein semantisches Suchnetz: ~670 mittelhochdeutsche Texte, 43.750 Lexikoneinträge, 192.674 Variantenformen, öffentlich durchsuchbar.

Die Frage des CLARIAH-AT Miniprojekts lautete: *Wie bringt man beide zusammen, ohne entweder die editorische Substanz des einen oder die semantische Infrastruktur des anderen zu beschädigen?*

Die Antwort: mit 20 Python-Skripten, drei Annotationsphasen, einem LLM-gestützten Review-Workflow — und mehr philologischen Überraschungen als erwartet.

---

## Das Objekt

Die Wenzelsbibel ist vielleicht das aufwändigste Buchprojekt des deutschsprachigen Mittelalters. Um 1389–1395 im Auftrag König Wenzels IV. von Böhmen entstanden, umfasst sie sechs Prachtbände (Wien, ÖNB, Cod. 2759–2764) mit insgesamt 1.214 Blättern und über 650 ganzseitigen Miniaturen. Sie enthält eine der frühesten volkssprachlichen Vollübersetzungen der Bibel ins Deutsche — eine Prosaübersetzung der Vulgata, die sprachlich am Übergang von Mittelhochdeutsch zu Frühneuhochdeutsch steht.

Für die MHDBDB relevant sind die fünf Bücher des Pentateuch: Prologus-Genesis, Exodus, Levitikus, Numeri, Deuteronomium. Sprachlich bairisch-österreichisch mit deutlich böhmischem Kolorit — das Ergebnis einer höfischen Werkstatt, die für Wenzels Kanzleisprache schrieb. Und das wird uns noch beschäftigen.

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

Vier fehlende Attribute, und jedes hat seine eigene Funktion im MHDBDB-Suchnetz: `@lemmaRef` macht den Text lemmasuchbar, `@pos` ermöglicht grammatische Filterung, `@meaningRef` öffnet die Konzeptnavigation, `@wordRef` verbindet Wortformvarianten. Ohne sie ist die Wenzelsbibel im Korpus vorhanden, aber blind — wie ein Buch ohne Register.

---

## Die Pipeline: Drei Phasen, eine Logik

Die Annotationspipeline folgt einem einheitlichen Prinzip: **Automatisierung so weit wie möglich, LLM-Assistenz an den Ambiguitätsgrenzen, menschliches Review an den Unsicherheitsstellen.**

Alle Entscheidungen gehen durch eine TSV-Zwischenschicht — menschlich lesbar, versionierbar, per `--dry-run` testbar. Kein Schritt schreibt direkt in das TEI; alles läuft durch überprüfte Batch-Dateien.

### Phase 1: Lexikonbasiertes Auto-Matching

Das Matching-Skript (`wzb-auto-match.py`) liest jede `<w>`-Wortform, normalisiert sie nach der MHDBDB-Konvention (`â→a, ê→e, î→i, ô→o, û→u`) und sucht in `variants.xml`:

- **Eindeutiger Treffer** (eine Form, ein Lemma): `@lemmaRef` direkt gesetzt — kein menschlicher Eingriff.
- **Mehrdeutiger Treffer**: mehrere Lemma-Kandidaten — wandert in die Disambiguierungs-TSV.
- **Kein Treffer**: nicht im Variantenwörterbuch — Phase 1b.

Das Ergebnis: rund 60 % der Tokens direkt zuordenbar. **72.358 Zeilen** für Phase 1b.

Die Normalisierung war die erste Überraschung. WB-DEA-Wortformen liegen in manuskriptnaher Schreibung vor (*herczen* statt *hêrzen*), `variants.xml` enthält nicht-normalisierte MHG-Formen — beide Seiten müssen auf denselben Nenner gebracht werden, bevor ein Abgleich überhaupt möglich ist.

### Phase 1b: LLM-gestützte Lemma-Disambiguierung

72.358 offene Fälle, von denen viele nicht mechanisch lösbar sind: Ein Wort wie *herte* kann je nach Kontext ADJ ("hart"), NOM ("Herz"), VRB ("verhärten") oder NAM ("Schäfer/Herde") sein — und die Wenzelsbibel hat alle vier.

Die Lösung war ein gestaffeltes Triage-Schema:

| Population | Strategie |
|---|---|
| Hochfrequente Ambiguitäten (21+ Tokens) | **Bulk-Resolve**: eine LLM-Entscheidung für alle Vorkommen |
| Mittelfrequenz (2–20 Tokens) | **Kontextbasiert**: LLM liest jeden Kontext einzeln |
| Hapax ambigua (count = 1) | **Zurückgestellt** (ROI zu gering) |
| Ungematchte Mittelfrequenz (6–20) | Wörterbuchnetz-Abgleich oder `NEW` |
| Ungematchter Langschwanz (1–5) | **Akzeptierter Residual** |

Der Workflow war immer gleich: TSV-Batch (50 Zeilen) → Claude liest Kontextfenster (±5 Tokens), schlägt ein Lemma vor, vergibt Konfidenz (`high/medium/low`). Julia überprüft alle `low`-Entscheidungen und eine 20-%-Stichprobe der `medium`-Fälle, bevor `wzb-bulk-resolve.py` die Entscheidungen in das TEI schreibt.

**@lemmaRef-Coverage nach Phase 1 + 1b: 95,3 %** (142.185 / 149.148 Tokens).

#### Die böhmischen Überraschungen

Die Wenzelsbibel hatte drei Kategorien von Annotationsproblemen, die kein Standard-MHG-Text hätte:

**1. Böhmische Schreibkonventionen.** `cz → z`, `v → u`, `ou → û`, `vor- → ver-`. Wörter wie *czeit*, *vnd*, *vortilgen* finden sich so in keinem Wörterbuch — obwohl sie ganz gewöhnliche mhd. Wörter sind. Die Normalisierung musste um diese Bohemismen erweitert werden.

**2. Tschechische Interlinearglossen.** In den Exodus- und Numeri-Abschnitten tauchen Marginalglossen in Altböhmisch auf: *toho*, *pzde*, *bzde*, *thoho*, *zde* — Notizen aus dem Scriptorium für Wenzels zweisprachige Kanzlei. Sie sind keine MHG-Lexeme. Lösung: ein neues Lemma `lemma_78628` (cs NOM) als Platzhalter für altböhmisches Paratextmaterial.

**3. Schreibermarken und lateinische Rubriken.** `ł`, `჻`, `=`, `CAPITULUM`, `LEUITICUS`, `GENE+SIS` (foliozeilenübergreifend aufgeteilt) — keine lexikalischen Einheiten. Sie gehen zu `lemma_2` (Catch-All für Nicht-Lexikalisches) oder `lemma_13826` (Kapitelapparat).

Diese drei Kategorien waren im Vorfeld nicht sichtbar. Das ist typisch für historische Handschriften: Das Unerwartete ist immer dabei.

**Neu in `lexicon.xml` nach Phase 1b:** vier Einträge für böhmisch-spezifisches Vokabular — *cs* (altböhmische Glossen), *herte* (Weideherde), *scot* (böhmische Münzeinheit Schekel), *weise* (Waise, distinct from *weise* adj. = weise).

### Phase 2: POS-Tagging

Mit `@lemmaRef` gesetzt war Phase 2 teilweise bereits erledigt: Lemmata mit genau einem POS-Eintrag im Lexikon werden direkt zugewiesen, kein LLM nötig. Das deckt rund 75 % der Fälle ab.

Die restlichen 25 % — Lemmata mit mehreren möglichen Wortarten — gingen in eine Pending-TSV. Das MHDBDB-Tagset umfasst 19 Tags (PRO, VRB, NOM, ADJ, ADV, DET, CNJ, SCNJ, CCNJ, PRP, VEX, POS, NAM, NUM, NEG, INJ, VEM, IPA, DIG), und die wichtigste Regel für das Modell lautet: **kein ART, immer DET**. Das ist kein Standard-STTS, und LLMs tendieren ohne explizite Einschränkung zu STTS-Kategorien.

Mitten in der Arbeit eine Korrektur: Der Tag `ART` war initial verwendet worden und existiert im MHDBDB-Tagset schlicht nicht. Ein Migration-Patch (commit `cf71ae48`) korrigierte alle bereits gesetzten `ART`-Attribute rückwirkend zu `DET`. Solche Korrekturen sind typisch für Projekte, in denen Schema und Daten parallel entstehen.

**@pos-Coverage: 95,3 %** (142.185 / 149.148). QA-Ergebnis: 0 ungültige Tags, 0 unbekannte `@lemmaRef`-Werte.

---

## Was passiert, wenn Schema und Daten gleichzeitig wachsen?

Das ist die methodische Lektion, die selten explizit dokumentiert wird. Während der WZB-Arbeit änderte sich das MHDBDB-Schema mehrmals:

| Element | Alte Kodierung | Korrekte Kodierung |
|---|---|---|
| Interpunktion | `<seg type="pc">` | `<pc join="left&#124;right">` |
| Genre-Link in `works.xml` | `<ref target="genres.xml#...">` | `<ptr target="genres.xml#..."/>` |
| Handschriftenangabe | `<note type="manuscript">` | nicht auf `<bibl>`-Ebene erlaubt |
| Artikel-POS-Tag | `ART` | `DET` |

Jede Korrektur erforderte rückwirkende Anpassungen in TEI und Authority-Files. Die Lösung: eine explizite Schema-Änderungshistorie in der Projektdokumentation — ein reproduzierbares Muster für ähnliche DH-Projekte.

---

## Phase 3: Wortsinn-Disambiguierung — der Forschungsausblick

Phase 3 geht über den Miniprojekt-Rahmen hinaus und ist gleichzeitig Gegenstand einer laufenden Dissertation (Hintersteiner). Die Frage: Kann ein LLM-gestützter Workflow die **Mehrheitssinn-Baseline** schlagen?

Die Baseline — berechnet aus 675 menschlich annotierten MHDBDB-Texten — liegt bei **66,7 % gewichteter Genauigkeit**: der Wert, den man erreicht, wenn man für jedes Lemma immer die häufigste Bedeutung wählt. Die Pipeline muss das übertreffen, um ihren Nutzen zu belegen.

Stand nach sechs Bulk-Batches: **@meaningRef-Coverage 76,2 %** (113.702 / 149.148). Noch ausstehend: die hochambigen Hochfrequenzlemmata (*in*, *haben*, *werden*), die per-Token-Entscheidungen erfordern. Das ist der Kern der Dissertation.

Das Evaluationsdesign ist prä-registriert: N=400–600, stratifiziert nach Sensanzahl (2/3–5/6+) × Wortart, Blind-Review-Verfahren. Julia trifft ihre eigene Entscheidung, bevor sie die LLM-Entscheidung sieht — das ergibt drei Datenpunkte pro Token (LLM, Julia, Gold-Standard), aus denen sich Übereinstimmungsmaße und Fehleranalysen ableiten lassen.

---

## Was die Wenzelsbibel jetzt kann

Die Wenzelsbibel ist seit Mai 2026 als Sigle **WZB** vollständig in der MHDBDB zugänglich:

- **Lemma-Suche** über 142.185 annotierte Tokens
- **Lemma-Highlighting** in der Leseansicht (bis zu 5 gleichzeitige Suchbegriffe mit Farb-Coding)
- **Gattungsklassifikation**: Bibelübersetzung — taucht in der Gattungssuche auf
- **Normdaten**: Wikidata Q476495, GND 4117632-7, Handschriftencensus werke/4577
- **Wörterbuch-Links** auf jeder Lemma-Page: Lexer (live via HTTPS-API) + MWB (Suchlink)

---

## Fazit: Die größten Hindernisse sind nicht technisch

Was hat dieses Miniprojekt gezeigt?

**Infrastruktur-Interoperabilität ist lösbar** — aber sie erfordert explizite Schema-Arbeit, nicht nur Datentransformation. Welches Format hat ein "Wort" in WB-DEA? Was ist ein "Lemma" in der MHDBDB? Diese Fragen haben keine technische Antwort; sie sind philologische Entscheidungen, die man treffen und dokumentieren muss.

**LLM-gestützte Annotation skaliert** — 91,6 % Lemma-Abdeckung und 95,3 % POS-Abdeckung in einem historischen Text mit 150.000 Tokens, mit menschlichem Review an den Schwachstellen. Das LLM skaliert philologische Intuition; es ersetzt sie nicht.

**Residuale Ambiguität ist legitim.** Die 8,4 % unaufgelösten Tokens sind kein Projektversagen. Pronomen wie *in* mit 3.486 Vorkommen in dreifacher Kasusdoppeldeutigkeit sind ohne Satzsyntax-Analyse nicht automatisch auflösbar. Diese Grenze korrekt zu benennen ist eine wissenschaftliche Aussage.

**Parallelentwicklung von Schema und Daten braucht explizite Versionierung.** Der `ART→DET`-Patch, der Genre-`<ref>→<ptr>`-Wechsel, die `<note type="manuscript">`-Abschaffung — all das passiert in einem lebenden Projekt. Dokumentiert, ist es nachvollziehbar. Undokumentiert, ist es technische Schuld.

Die Wenzelsbibel ist jetzt ein vollwertiger Teilnehmer im MHDBDB-Suchnetz. Jede Suchanfrage nach einem mittelhochdeutschen Lemma bezieht jetzt auch diesen Text ein — einen der bedeutendsten deutschen Bibeltexte des 14. Jahrhunderts, der in keiner computationellen Korpusressource nutzbar war. Und die offene Frage, ob das LLM die Mehrheitssinn-Baseline schlägt, trägt eine ganze Dissertation.

---

*Die Wenzelsbibel ist als Sigle **WZB** in der [MHDBDB-Korpussuche](https://dhcraft.org/mhdbdb-tei-only/korpus.html?text=WZB) zugänglich. Pipeline-Skripte und Annotationsdaten: [github.com/DigitalHumanitiesCraft/mhdbdb-tei-only](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only). Das Miniprojekt wurde im Rahmen von CLARIAH-AT gefördert. Kontakt: [mhdbdb@plus.ac.at](mailto:mhdbdb@plus.ac.at)*
