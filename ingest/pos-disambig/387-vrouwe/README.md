# Batch-Log: #387, vrouwe ohne Lemma (der mechanische Teil)

Provenienz-Log nach POS-TAGSET.md §6.3.5, Muster: `216-vrouwe155/`.

Zweiter Batch dieser Reihe ohne LLM-Lauf, und der erste, der eine
Belegschwelle mitbringt. Warum, steht unten unter „Der Fall `fvrn`".

## Rahmen

- **Issue:** #387, ausgelagert aus #216 auf Wunsch von @wachauer am 01.09.2026
  („andere vrouwen in eigenes Issue").
- **Datum:** 2026-09-06
- **Modell:** keines. Kein Disambiguierungslauf, kein `prompt.md`.
- **Skripte:** `extract-387-vrouwe.py`, dann die generischen
  `apply-homograph.py` und `revisiondesc-homograph.py`.

## Zuschnitt: nur der mechanische Teil

**Die eigentliche Arbeit von #387 ist nicht in diesem Batch.** Sie besteht aus
390 Tokens der Schreibung `fro`, mehrdeutig zwischen *vrouwe* und *vrô*
„froh", und braucht eine philologische Entscheidung. @wachauers Antwort vom
01.09. („Jedesmal Frau Minne") gilt ausdrücklich der Anrede vor *minne* und
nicht diesen Belegen; das steht so im Body des Tickets.

Dieser Batch nimmt ausschließlich, was ohne Kontextentscheidung bestimmt ist.
Die kontextpflichtigen Fälle bekommen nicht einmal einen `cases.json`-Eintrag,
damit sie niemand versehentlich durch die Pipeline schiebt: sie stehen in
`offene-faelle.csv`.

## Auswahlregel

Ein Fall ist ein `<w>` im `<body>`, das

1. **kein** `@lemmaRef` trägt,
2. formal *vrouwe* ist,
3. dessen normalisierte Schreibung im gesamten Korpus nur ein einziges Lemma
   trägt, nämlich `lemma_7260`, das genau eine Wortart führt,
4. und dessen Schreibung dafür genug Zeugen hat.

Punkt 4 ist neu gegenüber `216-vrouwe155/` und der Grund für diesen Absatz.

**„Formal vrouwe" wird am Bestand erhoben, nicht geraten**, und die Menge der
Lemmata je Form wird über **alle** Lemmata gebildet, nicht gegen eine Liste
erwarteter Konkurrenten. Von den 141 Formen des `lemma_7260`-Inventars tragen
9 ein weiteres Lemma, und nur zwei davon sind `lemma_7250`: sechs hängen an
`lemma_7256` (*vröuwen*) und eine an `lemma_7251`. Wer nur gegen *vrô* prüft,
hält sieben mehrdeutige Formen für eindeutig.

## Der Fall `fvrn`, und warum Punkt 4 dazugekommen ist

Die Bedingung aus Punkt 3 ist erfüllt, sobald es **einen** annotierten Beleg
gibt: eine Menge mit einem Element ist trivial einwertig. Genau das trat ein.

Die Schreibung `fvrn` kommt im Korpus zweimal vor:

```
RF_118100_0    dvrch iwer ere ich iz gerne verhil
             > fvrn hersante schande was niht kleine     annotiert, lemma_7260
               sie beiz vor zorne in die steine

NLA_72101_5  > wie si ze der hohzit fvrn                  unannotiert
```

Der erste ist die Anrede vor dem Namen der Wölfin Hersant im Reinhart Fuchs
und korrekt. **Der zweite ist das Verb** *varn*: „wie sie zur Hochzeit
fuhren." Ohne Schwelle hätte der Lauf ihm `lemmaRef`, `pos` und `corresp` des
Substantivs gegeben, und die mitgeschriebene Begründung wäre dabei formal wahr
geblieben. Das ist die unangenehmste Sorte Fehler: die Aussage stimmt, die
Handlung nicht.

Belegzahlen der sieben in Frage kommenden Schreibungen, am 06.09.2026 gemessen:

| Schreibung | annotiert als `lemma_7260` | unannotierte Kandidaten |
|---|---:|---:|
| `vrowen` | 2.217 | 68 |
| `fraw` | 434 | 546 |
| `frow` | 254 | 330 |
| `frovwe` | 215 | 1 |
| `vrov` | 59 | 2 |
| `frov` | 6 | 1 |
| `fvrn` | **1** | 1 |

Der Abstand zwischen 6 und 1 ist die Stelle, an der die Aussage kippt. Die
Schwelle steht auf 5 und ist damit eine Ermessensentscheidung in einer
gemessenen Lücke; zwei wäre die logische Untergrenze. Sie steht als
`MIN_BELEGE` im Skript, mit dieser Begründung daneben.

**Schreibungen unterhalb der Schwelle werden nicht verworfen, sondern
gelesen**, und wer eine gelesen hat, trägt sie in `GEPRUEFT` ein. Die Menge
ist zur Zeit **leer**, und das ist richtig: unterhalb der Schwelle liegt in
diesem Lauf nur `fvrn`, und das ist gerade der Fall, der nicht freigegeben
werden darf.

**Hier stand bis zum 06.09. eine Freigabe für `frov`, und sie war in jedem
Teil falsch.** Der Satz lautete, `frov` liege unterhalb der Schwelle und
seine „beiden Vorkommen" stünden in FLG und FLG1 als Anrede vor einem Titel,
„frov kúnegin" neben „frovwe kúnegin". Gemeldet vom CI-Review-Bot auf PR
#398, Stelle für Stelle nachgemessen:

```
git grep -c -P 'lemmaRef="[^"]*"[^>]*>frov</w>' origin/main -- 'tei/*.tei.xml'
  -->  FLG 1, NBB 5     (in FLG1 kommt die Schreibung gar nicht vor)
```

| Beleg | Kontext | |
|---|---|---|
| `NBB_51_3` | *frov vote* | Anrede vor Eigenname |
| `NBB_611_6` | *frov siglint* | Anrede vor Eigenname |
| `NBB_3024_6` | *frov chrimhilt* | Anrede vor Eigenname |
| `NBB_5871_1` | *frov prvnnhilt* | Anrede vor Eigenname |
| `NBB_2622_6` | *vil manec frov vnd manech meit* | **keine Anrede**, blosses Appellativ |
| `FLG_1041100_9` | *frov minne* | Anrede vor einer Personifikation |

`frov` hat 6 Belege und liegt damit **über** der Schwelle von 5, nicht
darunter: die Tabelle direkt darüber sagt das, und der Absatz sagte das
Gegenteil. Annotiert hat die 6 die Schwelle, nicht die Freigabe. Und keiner
der sechs ist „frov kúnegin": diese Stelle ist `FLG_1041270_9`, der einzige
**unannotierte** Kandidat, also gerade der Beleg, um den es bei einer
Freigabe ginge.

Die brauchbare Lehre steckt in der letzten Zeile der Tabelle: `lemma_7260`
führt die Anrede **und** das schlichte Appellativ „Frau". Eine Menge, die
„alle Anrede" heisst, ist deshalb schon als Beschreibung falsch, auch wenn
jedes einzelne Tag stimmt.

## Ergebnis

| | |
|---|---:|
| Kandidaten (formal *vrouwe* ohne `@lemmaRef`) | 1.347 |
| annotiert | **948** in 31 Texten |
| zurückgestellt | **399** |
| neue Variantentypen | 0 |
| neue Lemmata | 0 |

Alle 948 gehen auf `lemma_7260` NOM. `@ana` wird bewusst nicht gesetzt, wie in
#189, #198 und den vorigen Serien: die Sense-Zuordnung ist kuratorisch. Zwei
der 948 trugen bereits `pos="NOM"` ohne Lemma, die übrigen 946 waren nackt.

Nach Schreibung: `fraw` 546, `frow` 330, `vrowen` 68, `vrov` 2, `frovwe` 1,
`frov` 1.

Nach Sigle: MR1 245, GWTK 102, LZT 101, EHB 97, MR2 73, NLA 68, NEIC 48,
MNB 42, HUG 27, EB1 26, FR3 21, DLF 17, DUM 13, EB2 13, APO 10, DFE 10,
HZU2 8, DJUM 4, DRE 4, PTS 3, WGM 3, BVSN 2, FLG 2, FLG1 2, und je einer in
EIH, KVO, LUU, MLB, PRJ, PSG, SGE.

### Die 399 zurückgestellten

| Grund | Tokens | Schreibungen |
|---|---:|---|
| mehrdeutig mit `lemma_7250` (*vrô* „froh") | 390 | `fro` 336, `frô` 54 |
| mehrdeutig mit `lemma_7256` (*vröuwen*) | 7 | `fröwen` 6, `vroewe` 1 |
| Belegbasis zu dünn | 1 | `fvrn` (das Verb, siehe oben) |
| kein Variantentyp unter `lemma_7260` | 1 | `vrow̆e` (WZB, Breve auf dem `w`) |

Die ersten 390 sind das offene Arbeitspaket von #387. Der letzte Fall
(`WZB_64ra_25_4`) ist derselbe, den die Messung in #216 als Stoppbedingung
genannt hat: einen Variantentyp zu prägen ist genehmigungspflichtig.

## Stichprobe

Vor dem Schreiben stratifiziert nach Schreibung gezogen und gelesen, 16 Fälle
über alle sechs Schreibungen (bei den seltenen alle). Kein Fehltreffer.
Belegbeispiele: „die **fraw** reyn", „hilff **fraw** der sel", „**fraw** jüt
iren man", „**frow** maß und frow scham", „min **frow** entsitztt des todes
twang", „wie er der **vrowen** pflach", „meide vnd **vrowen** quelten da den
lip". Die Nibelungen-Belege (`vrowen`, 68 Stück) sind durchweg Genitiv, Dativ
oder Plural des Substantivs, keine Anrede; für die Lemmazuordnung macht das
keinen Unterschied, für eine spätere Anredefrage schon.

## Data-Change-Lifecycle

Der Eingriff vergibt `@lemmaRef` an 948 zuvor lemmalose Tokens und
**verschiebt damit die Positionszählung** in 31 Dateien. Korpus-Checkliste
vollständig.

| Schritt | Ergebnis |
|---|---|
| Schema (`validate-corpus.py --corpus-only`, 31 Sigel) | Stage-2 0 Fehler. Stage-1 2 Fehlschläge, beide (FLG, LZT) in der dokumentierten 30er-Baseline und unverändert |
| Versions-Bump | Korpus-Index 4.2.9 auf **4.2.10** an vier Stellen, `check-index-versions.py` konsistent |
| `build-corpus-index.py` | 7.547.432 Tokens, exakt 948 mehr als in 4.2.9 (7.546.484) |
| `extract-variants.py --apply` | alle vier Semantik-Zähler **0**, `variants.xml` byte-identisch |
| `build-authority-index.py` | byte-identisch, deshalb **kein** Bump (bleibt 1.9.2) |
| `build-api.py` | 33 Dateien: die 31 Texte plus `api/index.json` und `api/texts/index.json` |
| Cross-Ref-Audit `--check` | OK, 0 unresolved, keine Sigle über ihrer Baseline |
| `validate-indices.py` | PASS |
| Index-Budget | Korpus-Index bei 84 Prozent, unverändert |
| Kontrollprobe | alle 948 Tokens tragen das erwartete Tag, 0 Abweichungen |

## Reproduktion

```bash
python scripts/ingest/pos-disambig/extract-387-vrouwe.py \
    --out-dir ingest/pos-disambig/387-vrouwe
python scripts/ingest/pos-disambig/apply-homograph.py \
    --config ingest/pos-disambig/387-vrouwe/config.json \
    --cases  ingest/pos-disambig/387-vrouwe/cases.json \
    --actions ingest/pos-disambig/387-vrouwe/actions.json \
    --out-dir ingest/pos-disambig/387-vrouwe --apply
python scripts/ingest/pos-disambig/revisiondesc-homograph.py \
    --config ingest/pos-disambig/387-vrouwe/config.json \
    --diff-liste ingest/pos-disambig/387-vrouwe/diff-liste.csv --apply
```

Ein Replay setzt den Korpusstand vor dem Batch voraus: `apply-homograph.py`
prüft vor jeder Ersetzung, dass das Ziel noch unannotiert ist, den erwarteten
Tokentext trägt und dasselbe `@pos` wie zur Extraktionszeit. Der Extraktor
selbst findet nach diesem Batch nur noch die zurückgestellten Fälle.

## Was in #387 offen bleibt

1. **Die 390 `fro`-Belege**, mehrdeutig zwischen *vrouwe* und *vrô* „froh". Das
   ist der Kern des Tickets und eine philologische Entscheidung.
2. **Die 7 Belege** mehrdeutig mit *vröuwen*.
3. **`vrow̆e`** in der WZB, das einen neuen Variantentyp bräuchte.
4. **`fvrn` in NLA** ist kein offener Fall dieses Tickets, sondern ein Verb.
   Es steht in `offene-faelle.csv`, damit die Zahl aufgeht, und gehört
   inhaltlich nicht zu *vrouwe*.
