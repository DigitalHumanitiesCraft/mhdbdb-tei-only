# Batch-Log: #369 Serie 2, stat (korpusweit)

Provenienz-Log nach POS-TAGSET.md §6.3.5 (vierter Batch unter `ingest/pos-disambig/`,
Muster: `216-minne/`).

## Rahmen

- **Issue:** #369 „Inhaltswort-Homographen nachannotieren, Serie 2: stat", Folge von
  Serie 1 (#216) nach der Priorisierungsliste aus PR #210.
- **Datum:** 2026-08-24
- **Modell:** Claude Fable 5 (claude-fable-5), 131 Disambiguierungs-Subagenten, rollierend
  zu je 60 Fällen
- **Prompt:** `prompt.md` in diesem Ordner, **Version 2** (siehe „Der Prompt musste
  während des Laufs korrigiert werden")
- **Kontext je Fall:** im Vers Zielvers plus Vorgänger- und Folgevers; in Prosa ein
  Fenster von ±15 Tokens innerhalb des Blockelements

## Bestand und Zuschnitt

Neu-Annotation nackter Tokens, kein Umhängen. Extraktion über alle 667 Korpusdateien
(`extract-homograph.py --form '^st[aâ]t$'`): **7.855 Tokens ohne `@lemmaRef` in 326
Texten**.

Kandidaten-Lemmata, gegen `variants.xml` und `lexicon.xml` erhoben:

| Verdict | Bedeutung | Bestands-Typ |
|---------|-----------|--------------|
| `lemma_5732` NOM | Substantiv *stat* (Stätte, Stelle, Ort, Stadt) | `type_20161` (Schreibung `stat`) |
| `lemma_5710` VRB | Verb *stân*/*stên* | `type_20050` (`stat`), `type_20048` (`stât`) |

**Das vierte denkbare Paar fehlt absichtlich.** `stât` als Substantiv ist im Korpus genau
einmal belegt (`SKT_502140_4`, `type_218598`), und dieser eine Beleg ist ein Fehltag:
*mîn gedanc an ir vil hôhe stât* ist das Verb. Ein NOM-Verdict auf der Zirkumflex-Schreibung
findet deshalb keinen Typ und geht in den Review, statt einen fragwürdigen Typ zu
verbreiten. Die Konstruktion hat gehalten, ohne je zu greifen: alle vier NOM-Verdicts auf
`stât` trugen ohnehin nur `medium` und fielen schon an der Konfidenzregel heraus.

## Anwendungsregel

Annotiert wird nur bei `confidence = high` und ohne Konflikt mit einem vorhandenen
`pos_prior`. Alles andere bleibt byte-identisch und geht in `review-faelle.csv`.

| Aktion | Anzahl |
|--------|-------:|
| ANNOTATE | 7.760 |
| REVIEW | 95 |

Verdict-Verteilung der Annotationen: `lemma_5732`/NOM 6.665, `lemma_5710`/VRB 1.095.
Review-Gründe: 93 wegen Konfidenz, 2 wegen Konflikt mit bestehendem `@pos`
(`ADP_6505000_1` und `ADP_6605700_8`, beide im Bestand `NOM`, im Kontext aber das Verb).

`@ana` (Sense-Referenz) wird bewusst NICHT gesetzt: gleiche Regel wie in #189, #198 und #216.

## Zentrale Befunde

**1. Die Serie verlangt echte Entscheidungen, keine Mehrheitslesart.** `stat` ist korpusweit
überwiegend das Substantiv (6.665 zu 1.095), aber das Verhältnis kippt textweise vollständig.
In den Stadtchroniken und Trojaromanen (RCC, TRO, OVG, KCR, JEW) tragen ganze Bündel 60 von
60 Substantiven; in Rudolfs Weltchronik, im Tristan und bei Frauenlob überwiegt das Verb mit
bis zu 42 von 60. Eine pauschale Regel hätte in der einen Gruppe alles richtig und in der
anderen alles falsch gemacht.

**2. Das Kandidatenpaar ist zu eng, und der Lauf hat das selbst gezeigt.** 51 der 95
zurückgehaltenen Fälle sind gar kein Zweifel zwischen NOM und VRB, sondern ein anderes Wort:

| Kategorie | Fälle | Beispiele |
|---|---:|---|
| maskulines `stat` = Ufer, Gestade | 32 | Landungsszenen in TRY (11), `an den stat` (PZ 4), `uf daz stat` (DAR) |
| maskulines `stat` = Stand, Zustand | 13 | `stat und wesen` (PL2 8), `elichen stat` (TUN) |
| Adjektiv oder Adverb *stæte* | 6 | `daz disev red stat vnd vnzebrohhen beleib` (HZU2 5), `gar stat bis an mein ende` (OVW) |
| lateinisches Zitat | 1 | `PRJ_1981120_1`, *in ore duorum vel trium stat omne verbum* |

Keiner dieser Fälle wurde falsch annotiert: die Bearbeiter haben sie selbständig auf
`medium` oder `low` gesetzt, ohne dass der Prompt diese Bedeutungen kannte. 43 der 95
sind echte Zweifel zwischen den beiden Kandidaten.

**Die Zählvorschrift ist hier der halbe Befund, und der erste Anlauf war falsch.** Die
Kategorien standen zunächst als Zahl in der Prosa und stammten aus einer Stichwortsuche
über die Freitext-Begründungen der Verdicts. Diese Heuristik hat in einem Lauf drei
Fehlzuordnungen erzeugt: das Stichwort `adjektiv` fing `gût stat` (CRO) und `heiligen stât`
(PSG) ein, wo `stat` das Substantiv und das Adjektiv ein anderes Wort ist; das Stichwort
`stand` traf im Prosa-Kontextfenster statt in der Begründung und zog `ADP_6605700_8`
herein, der in Wahrheit ein Verb-Verdict mit `pos_prior`-Konflikt ist; und `staet ze haben`
fiel durch, weil es nicht auf `staete` passt. Die Zahlen stammen deshalb jetzt aus einer
Klassifikation am Beleg, die als `kategorien-review.json` neben dieser Datei liegt: wer
sie nachrechnen will, braucht die Zuordnung, nicht die Summe. Drei Fälle sind dort als
unsicher markiert (`CRO_2722800_5`, `NAR_1502600_6`, `REN_222400_2`), weil das Genus
unmarkiert bleibt.

**Für das Ufer gibt es im Korpus keine geübte Zuordnung.** Unter `lemma_5712` (*stade*)
stehen korpusweit nur `stade` (245), `staden` (101) und `stades` (8), nie `stat`. Es gibt
also weder Korpuspraxis noch Variantentyp, an den diese 32 Fälle angeschlossen werden
könnten, obwohl mehrere von ihnen das Synonym im Nachbarvers tragen (`TRY_4396_4`:
*uf den stat spranc do er uf dem stade stunt*). Das ist eine kuratorische Frage und liegt
bei KZW, vorgelegt als #371.

**3. Der Prompt musste während des Laufs korrigiert werden, und die Korrektur ist
messbar.** Version 1 formulierte die Konfidenzregel zur Schreibung symmetrisch: die
Zirkumflex-Schreibung `stât` sollte bei einem NOM-Verdict die Konfidenz deckeln, und der
Satz las sich so, als gelte dasselbe umgekehrt für ein VRB-Verdict auf `stat`. Das hätte
7.688 der 7.855 Fälle betroffen, also fast den ganzen Batch auf `medium` gedrückt und damit
in den Review geschoben. Version 2 deckelt ausdrücklich nur die eine Richtung.

Die acht bereits bearbeiteten Bündel wurden mit Version 2 neu bearbeitet. Der Vergleich
beider Läufe über dieselben 480 Fälle ist die einzige Doppelmessung dieser Serie und fiel
so aus: **100 % Übereinstimmung im Verdict**, die Konfidenz ging von 26 `medium` auf 1
zurück. Der Prompt-Fehler hätte also keine falsche Annotation erzeugt, sondern richtige
Annotationen verhindert.

## Qualitätssicherung (§6.3.3)

Zwei Stichproben zu je 50 Fällen, beide von einem Prüfer bearbeitet, der die Verdicts
**nicht** gesehen hat: die Vorlage enthielt nur Fall-ID, Form und Kontext
(`blind-369.py` im Session-Scratchpad erzeugt sie, der Abgleich läuft über die xml:id und
bricht ab, wenn die Mengen nicht deckungsgleich sind).

| Durchgang | Grundlage | Abweichungen |
|---|---|---:|
| `stichprobe-50.csv` (Seed 369) | 50 Zufallsfälle aus den 7.760 Annotationen | **0** |
| `stichprobe-schwer-50.csv` (Seed 370) | 50 Fälle ohne stützenden Vorgänger | **0** |

Gate 3 verlangt höchstens 5 %. Beide Durchgänge liegen bei 0 %.

**Die Zählvorschrift der schweren Stichprobe, und ein Fehler darin.** „Schwer" heißt: das
unmittelbar vorangehende `<w>` trägt keine Wortart, die ein folgendes Substantiv bereits
anzeigt (Markermenge `DET/ART/PRP/POS/PRO/ADJ/GRA`). Der erste Lauf verglich den ganzen
`@pos`-Wert gegen diese Menge und zählte deshalb Tokens mit Mehrfachtag (`ART NUM`,
`ADJ ADV`) als schwer, obwohl der Artikel danebensteht. Nach der Korrektur auf einen
Vergleich je Tag sind es **1.647 von 7.760 (21,2 %)** statt 2.571 (33,1 %). Beide Zahlen
sind reproduzierbar, die zweite ist die richtige.

Von den geprüften 100 Fällen hat der Prüfer zwei als unsicher markiert, beide Ufer-Belege:
er entschied die Wortart richtig und vermisste das dritte Lemma. Damit hat die Blindprüfung
denselben Befund unabhängig erzeugt wie die Bearbeitung.

## Data-Change-Lifecycle

Abgearbeitet am 2026-08-24 nach der Korpus-Checkliste in `docs/DATA-MODEL.md`. Die
Routing-Frage entschied wieder ein Trockenlauf statt einer Schätzung: `extract-variants.py`
ohne `--apply` meldet alle vier Semantik-Zähler auf 0 (`added`, `removed`,
`form text changed`, `lemma assignment changed`). Die Schritte 5 und 6 entfallen damit,
`variants.xml` und der Authority-Index bleiben unangetastet: der Batch vergibt
ausschließlich die drei bereits bestehenden Typen.

| Schritt | Ergebnis |
|---|---|
| 1 Korpusänderung | 7.760 Tokens in 322 Dateien; Diff 8.082 Einfügungen zu 7.760 Löschungen, die Differenz sind die 322 `<change>`-Zeilen |
| 2 `revisionDesc` | je Datei ein Eintrag mit den eigenen Zahlen (`revisiondesc-homograph.py`, idempotent) |
| 3 Version-Bump | Corpus-Index 4.2.2 → 4.2.3 an vier Stellen, `check-index-versions.py` grün; Authority-Index bleibt 1.9.0 |
| 4 `build-corpus-index.py` | 667 Texte, 42.630 Lemmata, 7.546.177 Wörter |
| 5, 6 variants und Authority-Index | entfallen, siehe oben |
| 7 `build-api.py` | 2.742 Dateien; geändert haben sich `api/index.json` (Versionsfeld), die 322 Sigle-Dateien unter `api/texts/` und deren Sammelliste (beide wegen der Wortzahl) |
| 8 Schema (`validate-corpus.py --sample`, 10 der größten betroffenen Texte) | 9/10 voll gültig, Stage 2 fehlerfrei; der eine Stage-1-Fail ist ADP und steht mit `@reason` auf `<w>` in der 30er-Baseline (TEI-MODEL §10) |
| 9 `check-authority-cross-refs.py --check` | grün, keine neuen dangling refs; `lexicon.xml` unverändert bei 396 Refs / 109 IDs innerhalb der Baseline |
| 10 `validate-indices.py` | beide Indexe strukturell gültig |

Der Index wurde positionsgenau gegen den Vorstand aus `HEAD` abgeglichen (Skript im
Session-Scratchpad, Messung hier protokolliert):

- Belegstellen korpusweit 7.538.417 → 7.546.177, Differenz **exakt 7.760**
- genau zwei Lemmata ändern ihre Belegzahl: `lemma_5732` um +6.665 (2.394 → 9.059),
  `lemma_5710` um +1.095 (10.959 → 12.054), was den Verdicts entspricht
- `lemma_5732` erscheint jetzt in 332 statt 160 Texten, `lemma_5710` in 485 statt 465
- kein Text und kein Lemma verliert eine Position; 322 Texte gewinnen, in der Summe
  wieder genau 7.760

Das Substantiv war im Index also bisher massiv unterrepräsentiert: seine Belegzahl steigt
auf fast das Vierfache.

**Zum Bau mit `--allow-dirty`:** der Index-Builder verweigert seit #125 den Bau bei
unsauberem Arbeitsbaum unter `tei/`. Hier stammen alle 322 Änderungen aus diesem Batch,
und Korpus und Index gehen in denselben Commit, womit der Zustand, vor dem die Sperre
schützt, gar nicht entstehen kann. Die eigentliche Absicherung ist ohnehin
`data-integrity.yml`: die CI baut den Index aus dem committeten Stand neu und vergleicht.

## Dateien

- `cases.json`: Extraktionsstand der 7.855 Tokens vor dem Batch (xml:id, Form, Vers bzw.
  Prosafenster, `pos_prior`), Eingabe `--cases`
- `actions.json`: Verdicts aller 7.855 Fälle, Eingabe `--actions`
- `config.json`: Kandidaten-Lemmata, POS-Tags, Zuordnung von Schreibung und Lemma zum
  Variantentyp, Wortlaut des `revisionDesc`-Eintrags
- `diff-liste.csv`: alle Fälle mit Aktion, Review-Grund, Verdict, Konfidenz, Begründung
  und Kontext (Semikolon, UTF-8-BOM für Excel)
- `review-faelle.csv`: die 95 zurückgehaltenen Fälle
- `stichprobe-50.csv`, `stichprobe-schwer-50.csv`: die beiden Prüfstichproben
- `kategorien-review.json`: die Klassifikation der 95 Review-Fälle am Beleg, mit
  Einordnungsbegründung und Kontext je Fall; Grundlage der Zahlen in „Zentraler Befund 2"
  und der Beleglisten in #371
- `prompt.md`: der Disambiguierungs-Prompt, Version 2

Skripte, alle generisch statt serienspezifisch, damit Serie 3 sie ohne Kopie nutzen kann:
`scripts/ingest/pos-disambig/survey-homograph.py` (Sondierung),
`extract-homograph.py` (Extraktion), `bundle-cases.py` (Bündelung),
`assemble-actions.py` (Zusammenführung und Abdeckungsprüfung),
`apply-homograph.py` (Anwendung), `revisiondesc-homograph.py` (Header-Einträge),
`stichproben-homograph.py` (Stichprobenziehung).
Ein Replay setzt den Korpusstand vor dem Batch voraus (Parent-Commit): das
Anwendungs-Skript verifiziert, dass die Ziel-Tokens noch unannotiert sind, bevor es
schreibt.

## Ausdrücklich NICHT Teil dieses Batches

- Die 95 Review-Fälle, darunter die 51 Belege, für die das Kandidatenpaar nicht reicht
  (32 Ufer, 13 Stand, 6 *stæte*). Sie sind als #371 an KZW vorgelegt.
- `PRJ_1981120_1`, das lateinische Bibelzitat *in ore duorum vel trium stat omne verbum*.
  Fremdsprachliches Material gehört nach POS-TAGSET §6.4 nicht über `@pos`, sondern über
  `@xml:lang` erschlossen und ist damit außerhalb dieser Serie.
- Die Frage, ob das maskuline `stat` an `lemma_5712` (*stade*) angeschlossen wird oder ein
  eigenes Lemma bekommt. Ohne diese Entscheidung sind die 30 Fälle nicht annotierbar.
- Der Fehltag `SKT_502140_4` (`stât` als Substantiv, `type_218598`), gefunden bei der
  Sondierung. Er ist unmittelbar nach diesem Batch in einem eigenen PR korrigiert worden,
  und zwar getrennt, weil er genau das auslöst, was der Batch nicht tut: der Beleg war
  korpusweit der einzige seines Variantentyps, mit der Korrektur wird der Typ unbelegt,
  `variants.xml` ändert sich und der Authority-Index braucht einen Bump. In diesem PR
  hätte das die zentrale Aussage oben unwahr gemacht.
- Serie 3 ff. nach der Priorisierungsliste aus PR #210 (*sere*, *not*, *nam*, *leit*,
  *rede*, *sach*, *rat* …).
