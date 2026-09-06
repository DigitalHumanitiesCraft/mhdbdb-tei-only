# Batch-Log: #387, die Schreibung fro (der kontextpflichtige Teil)

Provenienz-Log nach POS-TAGSET.md §6.3.5, Muster: `216-minne/`.

Der **Kern von #387**. Der mechanische Teil liegt als `387-vrouwe/` und hat 948
Tokens annotiert; was dort zurückgestellt wurde, weil es eine
Kontextentscheidung braucht, ist diese Menge.

## Rahmen

- **Issue:** #387, ausgelagert aus #216 auf Wunsch von @wachauer am 01.09.2026.
- **Datum:** 2026-09-06
- **Modell:** Claude Fable, 61 Disambiguierungs-Agenten, einer je Text
- **Prompt:** `prompt.md` in diesem Ordner (Version 1, unverändert über alle Bündel)
- **Kontext je Fall:** im Vers Zielvers plus Vorgänger- und Folgevers, in Prosa
  ein Fenster von ±15 Tokens; Interpunktion eingeschlossen
- **Skripte:** `extract-387-fro.py`, dann die generischen `apply-homograph.py`
  und `revisiondesc-homograph.py`

**Ein Text je Lauf-Einheit**, wie §6.3.1 es verlangt: 61 Bündel unter
`bundles/`, 61 Verdict-Dateien unter `verdicts/`, zusammengeführt zu
`actions.json` in der Reihenfolge von `cases.json`. Die Bündel bleiben
liegen, damit nachvollziehbar ist, was jeder Agent gesehen hat.

## Die Aufgabe, und warum sie schwerer ist als minne oder stat

Die Schreibung `fro` (mit und ohne Zirkumflex) ist mehrdeutig zwischen

| Lemma | Form | Wortarten am Lemma |
|---|---|---|
| `lemma_7260` | *vrouwe* | NOM |
| `lemma_7250` | *vrô* „froh" | ADJ ADV GRA NOM |

**Hier fallen zwei Entscheidungen je Beleg statt einer.** Fällt das Urteil auf
die Anrede, steht die Wortart fest. Fällt es auf das Adjektiv, ist sie offen.
Der Prompt verlangt deshalb höchstens `medium`, wenn das Lemma klar ist und
die Wortart nicht, und `medium` wird nicht angewendet. **`GRA` wird nie
vergeben** (POS-TAGSET §3 und §6.3d), dieselbe Regel wie im Breve-Lauf zu #235.

@wachauers Entscheidung vom 01.09. („Jedesmal Frau Minne") galt fünf Belegen
unmittelbar vor *minne*, die in #216 abgearbeitet sind. Der Prompt untersagt
ausdrücklich, sich darauf zu stützen.

## Ergebnis

| | |
|---|---:|
| Fälle | 390 in 61 Sigeln |
| annotiert | **355** in 58 Texten |
| zurückgehalten | **35** |
| neue Variantentypen | 0 |
| neue Lemmata | 0 |

Verdicts der Annotationen: `lemma_7250`/ADJ 345, `lemma_7260`/NOM 9,
`lemma_7250`/ADV 1. Nach Schreibung: `fro` 311, `frô` 44. Sechs der 355 trugen
bereits ein `pos_prior` von `ADJ`, das in allen sechs Fällen bestätigt wurde.

Größte Sigel: GWTK 101, RVBR 42, DIO 40, CRO 38, NEIC 10, HUG 9, FR3 8, OSW 8.

`@ana` wird bewusst nicht gesetzt, wie in #189, #198 und den vorigen Serien.

## Die neun Anreden, und warum sie einzeln gelesen wurden

Zwölf Belege sind als `lemma_7260` beurteilt worden, alle mit hoher Konfidenz.
Sie sind der Ertrag dieses Batches und **alle zwölf sind vor dem Schreiben
gelesen worden**, nicht nur die Stichprobe:

```
FLG1_7295480500_0   fro diemuetekeit , sitzent hie bi mir      Frau Demut
FLG1_7295480660_0   fro helikeit , koment har zuo mir          Frau Heiligkeit
FLG1_7295480680_0   fro hoffunge , ich bitte úch               Frau Hoffnung
GWTK_336211961300_5 das selbe gehiess mir fro thedis           Personenname
HUG_290010_1        fro welt , ir sint gar húpsch und schón    Frau Welt
HUG_290810_1        fro welt , wend ir vergessen got           Frau Welt
NEIM_806020_1       fro tohter , lât die rede besten           Anrede
SGO_1040100_1       fro kunze , jâ ist iuwer trût              Personenname
SGO_1050400_0       fro künze , dast ûf iuch gezelt            Personenname
RVBR_4826_5         wâ sint ir nu , frô minne ,                zurückgehalten
RVBR_6310_4         nu sagent an , frô minne :                 zurückgehalten
RVBR_8687_5         wâ sint ir nu , frô minne ?                zurückgehalten
```

**Die drei RVBR-Belege sind genau die, die @wachauer am 01.09. entschieden
hat.** Der Agent hat sie selbständig als Anrede bestimmt, ohne die Entscheidung
zu kennen; der Prompt untersagt ihre Verwendung. Das ist keine Bestätigung im
strengen Sinn, aber es ist die einzige unabhängige Probe, die dieser Batch
hergibt. Annotiert sind sie trotzdem nicht, siehe unten.

Jede Anrede steht unmittelbar vor einem Titel, einem Namen oder einer
personifizierten Tugend. Das Feld `next_token` trägt diese Entscheidung, und
der Extraktor liefert es deshalb mit.

## Die 35 zurückgehaltenen

| Grund | Tokens | Was das heißt |
|---|---:|---|
| `confidence` | 31 | mittlere Konfidenz, überwiegend die offene Wortart |
| `kein-typ` | 3 | die drei RVBR-Belege, siehe unten |
| `verdict-klasse` | 1 | substantiviertes *frô*, siehe unten |

Nach Verdict: `lemma_7250`/ADJ 16, `lemma_7250`/ADV 14, `lemma_7260`/NOM 3,
`lemma_7250`/NOM 2. Nach Sigle konzentriert: RVBR 10, GWTK 9, FR3 8, FR1 3.

**Die drei RVBR-Belege scheitern nicht am Urteil, sondern am Datenmodell.** Für
das Paar (Zirkumflex-Schreibung, `lemma_7260`) gibt es in `variants.xml` keinen
Typ; die Schreibung ist dort nur unter `lemma_7250` geführt. Den vorhandenen
`type_25866` zu setzen wäre falsch, weil ein Typ zu genau einem Lemma gehört
und `extract-variants.py` die Kollision der häufigeren Seite zuschlüge; jene
Seite hat korpusweit 1.410 Belege. **Es ist dieselbe Sperre, an der dieselben
drei Tokens schon in #216 liegengeblieben sind.** Einen Typ zu prägen ist
genehmigungspflichtig, und diese Entscheidung wird hier zum zweiten Mal
vorgelegt statt zum zweiten Mal umgangen.

**Das substantivierte *frô* wird als Klasse nicht maschinell entschieden.** Das
ist eine neue Angabe in der `config.json` (`review_verdicts`), und sie greift
bei genau einem Fall: `FR2_419020_7`, „so süzen sang gewinnet, ein swinendez
**fro**", mit hoher Konfidenz als Substantivierung beurteilt. Die Begründung ist
sauber (Artikel plus stark flektiertes Attribut ohne Bezugswort), aber
Substantivierung ist eine Aussage über die Wortart, die der Korpus nicht
bestätigen kann, und die Stelle ist eine dichte Frauenlob-Fügung. Der zweite
NOM-Fall (`FR1_13058020_4`) trug ohnehin nur mittlere Konfidenz.

Die Regel ist die Verallgemeinerung dessen, was Serie 1 als feste Zeile im
Skript hatte („alle NAM-Verdicts gehen ins Review"). Sie ist jetzt eine Angabe
der Serie statt eine des Werkzeugs, und ihre Wirkung ist gemessen: ohne den
Eintrag meldet ein Trockenlauf 356 Annotationen und keinen Grund
`verdict-klasse`, mit ihm 355 und einen. Ein Config ohne den Eintrag verhält
sich damit nachweislich wie vorher.

## Ein Defekt im Extraktor, gefunden nach dem Lauf

Der CI-Review-Bot hat auf PR #398 gemeldet, dass das Feld `next_token` die
Verszeile überschreitet: es nahm das nächste `<w>` in der Dokumentordnung des
ganzen `<body>`, nicht das nächste Wort derselben Zeile. Unabhängig
nachgemessen und bestätigt: bei **116 der 374 Versfälle (31 %)** steht das
Zieltoken am Versende, das Feld trug dort also das erste Wort der Folgezeile.
Das wiegt, weil `prompt.md` dieses Feld unter „Was zuerst zu prüfen ist" an
die erste Stelle stellt.

**Ein falsches Tag ist daraus nicht geworden, und das ist gemessen.** Alle
zwölf Anrede-Urteile stehen mitten im Vers, keines am Versende. Dazu war
`next_verse` in keinem der 116 Fälle leer, das Modell konnte also immer sehen,
dass das Wort eine Zeile weiter steht.

Das Skript ist korrigiert: `next_token` steht nur noch, wenn das folgende
`<w>` denselben `<l>`-Vorfahren hat, in Prosa denselben Block. Am Versende ist
das Feld jetzt leer, und das ist die richtigere Angabe.

**Die committete `cases.json` bleibt unverändert.** Sie ist das Protokoll
dessen, was die 61 Agenten tatsächlich gesehen haben, und darf nicht
nachträglich zu etwas anderem gemacht werden. Wer die 35 zurückgehaltenen
Fälle erneut extrahiert, bekommt das korrigierte Feld.

## Qualitätssicherung

- **Vollständigkeit maschinell geprüft:** 61 Verdict-Dateien gegen 61 Bündel,
  die `xml:id`-Mengen decken sich exakt, keine Auslassung und kein Fremdling.
- **Regelkonformität maschinell geprüft:** 0 Verstöße gegen das erlaubte
  Wertepaar aus Lemma und Wortart, **0 mal `GRA`**, 0 Formabweichungen
  gegenüber `cases.json`.
- **Stichprobe:** 50 Zufallsfälle aus der Nicht-Anrede-Menge, stratifiziert
  gelesen, kein Fehltreffer. Dazu **alle zwölf** Anrede-Urteile.
- **Kontrollprobe nach dem Schreiben:** alle 390 Fälle einzeln gegen das TEI
  gehalten; die 355 tragen das erwartete Tag, die 35 sind byte-identisch
  geblieben.
- Kein `low` im gesamten Lauf; die Konfidenzverteilung ist 359 `high` und
  31 `medium`.

Eine Einschränkung, die zum Verfahren gehört: **es gibt keinen externen
Goldstandard**, so wie schon in Serie 1. Die Stichprobe ist eine Lesung durch
dasselbe Verfahren, das die Urteile erzeugt hat, nur in anderer Rolle. Sie
ersetzt keine Durchsicht durch KZW.

## Data-Change-Lifecycle

Der Eingriff vergibt `@lemmaRef` an 355 zuvor lemmalose Tokens und
**verschiebt damit die Positionszählung** in 58 Dateien.

| Schritt | Ergebnis |
|---|---|
| Schema (`validate-corpus.py`, 58 Sigel) | Stage-2 0 Fehler. Stage-1 4 Fehlschläge, alle vier (AC1, AC2, AC3, LZT) in der dokumentierten 30er-Baseline |
| Versions-Bump | Korpus-Index 4.2.10 auf **4.2.11** an vier Stellen, konsistent |
| `build-corpus-index.py` | 7.547.787 Tokens, exakt 355 mehr als in 4.2.10 |
| `extract-variants.py --apply` | alle vier Semantik-Zähler **0**, `variants.xml` byte-identisch |
| `build-authority-index.py` | byte-identisch, deshalb **kein** Bump (bleibt 1.9.2) |
| `build-api.py` | 60 Dateien |
| Cross-Ref-Audit, `validate-indices.py`, Budget | OK, PASS, unverändert bei 84 Prozent |

## Reproduktion

```bash
python scripts/ingest/pos-disambig/extract-387-fro.py \
    --out-dir ingest/pos-disambig/387-fro
# Bündel schneiden, je Text ein Agent gegen prompt.md, Verdicts nach verdicts/
python scripts/ingest/pos-disambig/apply-homograph.py \
    --config ingest/pos-disambig/387-fro/config.json \
    --cases  ingest/pos-disambig/387-fro/cases.json \
    --actions ingest/pos-disambig/387-fro/actions.json \
    --out-dir ingest/pos-disambig/387-fro --apply
python scripts/ingest/pos-disambig/revisiondesc-homograph.py \
    --config ingest/pos-disambig/387-fro/config.json \
    --diff-liste ingest/pos-disambig/387-fro/diff-liste.csv --apply
```

Der LLM-Schritt ist nicht deterministisch. Ein Replay reproduziert das
Verfahren, nicht die Urteile; maßgeblich ist die committete `actions.json`.
`apply-homograph.py` prüft vor jeder Ersetzung, dass das Ziel noch unannotiert
ist und denselben Tokentext und dasselbe `@pos` trägt wie zur Extraktionszeit.

## Was in #387 danach offen bleibt

1. **Die 35 zurückgehaltenen Fälle**, mit Verskontext in `review-faelle.csv`.
   Die 31 mit mittlerer Konfidenz sind fast durchweg dieselbe Frage: prädikativ
   oder adverbial.
2. **Der Variantentyp für die Zirkumflex-Schreibung** unter `lemma_7260`. Daran
   hängen drei Belege, die zweimal entschieden und zweimal nicht geschrieben
   worden sind.
3. **`vrow̆e`** in der WZB aus dem mechanischen Teil, ebenfalls ein fehlender Typ.
4. **`fvrn` in NLA** ist kein Fall dieses Tickets, sondern das Verb *varn*.
