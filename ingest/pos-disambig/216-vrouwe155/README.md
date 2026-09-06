# Batch-Log: #216 Punkt 3, vrouwe vor minne (die kleine Menge)

Provenienz-Log nach POS-TAGSET.md §6.3.5. Vierter Batch unter `ingest/pos-disambig/`,
und der erste **ohne** Disambiguierungslauf.

## Rahmen

- **Issue:** #216 Punkt 3. Beauftragt von @wachauer am 01.09.2026 im Thread:
  „Kleine Menge vorziehen, andere vrouwen in eigenes Issue." Die andere Menge
  liegt seither als #387.
- **Datum:** 2026-09-06
- **Modell:** keines. Diese Serie hat keinen LLM-Lauf und keinen `prompt.md`,
  siehe „Warum hier nicht disambiguiert wird".
- **Skripte:** `extract-216-vrouwe155.py` (Extraktion und Verdicts in einem
  Lauf), dann die generischen `apply-homograph.py` und
  `revisiondesc-homograph.py` wie in jeder anderen Serie.

## Warum diese 155 Tokens zusammengehören

Die Regel für die Personifikation „Frau Minne" ist in #216 als **Lemma**-Regel
formuliert und nicht als Schreibungsregel: als Anrede gilt, was ein *vrouwe*
mit `lemma_7260` unmittelbar vor sich hat. Der Grund steht im Kommentar vom
31.08.2026 und ist gemessen: eine handgeschriebene Sechserliste aus HUGO deckte
214 von 633 Stellen und enthielt ausgerechnet die häufigste Schreibung nicht.

Diese Regel greift dort nicht, wo das vorangehende *vrouwe* selbst noch kein
Lemma trägt. Genau das sind diese 155 Stellen. Der Batch macht sie nicht
sichtbar, er stellt die Voraussetzung dafür her, dass die NAM-Frage überhaupt
an ihnen entschieden werden kann.

**Die minne-Seite ist unangetastet.** Alle 155 minne-Tokens tragen weiterhin
kein `@lemmaRef`. Ob sie das eigene NAM-Lemma „Minne" bekommen, ist der
nächste Schritt in #216 und braucht einen neuen Eintrag in `lexicon.xml`.

## Bestand und Zuschnitt

Ein Fall ist ein Paar aus zwei aufeinanderfolgenden `<w>` im `<body>`: das
erste ohne `@lemmaRef` und formal *vrouwe*, das zweite passend auf
`^m[iíîy]nn[eè]?$`.

**Das Formeninventar wird am Bestand erhoben, nicht geraten.** „Formal
*vrouwe*" ist die Menge der MHG-normalisierten Oberflächenformen aller `<w>`
mit `lemma_7260`; Lemma-Ids token-genau verglichen (CONTRACTS.md §B.1). Am
06.09.2026 gemessen: 141 Formen für `lemma_7260`, 38 für `lemma_7250`
(*vrô* „froh"), Schnittmenge `fra` und `fro`.

**„Unmittelbar" heißt: in der `<w>`-Folge des `<body>`.** Nicht unter den
direkten Kindern der Verszeile. 115 der 155 Paare enthalten mindestens ein
`<w>`, das in einem `<hi>` steckt; ein Durchlauf über die direkten Kinder
findet nur 40 der 155. Beide Zählweisen weist
`scripts/audit/measure-216-vrouwe-minne.py` aus.

Ergebnis: **155 Tokens in 6 Schreibungen und 11 Sigeln.**

| Schreibung | Tokens | in variants.xml unter |
|---|---:|---|
| `frow` | 97 | `lemma_7260` (type_25985) |
| `fraw` | 50 | `lemma_7260` (type_43131) |
| `frô` | 3 | **nur** `lemma_7250` (type_25866) |
| `fro` | 2 | `lemma_7250` **und** `lemma_7260` (type_154744) |
| `vrou` | 2 | `lemma_7260` (type_25989) |
| `frovwe` | 1 | `lemma_7260` (type_80904) |

## Warum hier nicht disambiguiert wird

Die Serien 1 (#216 minne), 2 (#369 stat) und #367 haben je einen LLM-Batch
gefahren, weil dort eine Kontextentscheidung nötig war. Hier ist sie es nicht,
und zwar aus zwei Gründen, die das Skript getrennt hält (Feld `herkunft` in
`actions.json`):

- **150 Tokens, `herkunft: mechanisch`.** Ihre Schreibung kommt im
  Variantenwörterbuch nur unter `lemma_7260` vor, und `lemma_7260` trägt genau
  eine Wortart (`NOM`). Es gibt nichts zu entscheiden. Dasselbe Kriterium wie
  in PR #379 und #382.
- **5 Tokens, `herkunft: wachauer-2026-09-01`.** Sie tragen die zwischen
  *vrouwe* und *vrô* mehrdeutige Schreibung `fro` beziehungsweise `frô`.
  @wachauer sind genau diese fünf Belege im Volltext vorgelegt worden, seine
  Antwort lautet „Jedesmal Frau Minne", also `lemma_7260`.

Das Skript bricht ab, wenn ein mehrdeutiger Fall auftaucht, der nicht in der
Entscheidungsliste steht, und ebenso, wenn ein Eintrag der Liste keinen Fall
findet. Eine mechanische Entscheidung an einer mehrdeutigen Schreibung ist
damit nicht möglich, auch nicht versehentlich.

**Diese Entscheidung gilt für die Anrede vor *minne* und wird hier nicht
ausgeweitet.** Die übrigen 387 `fro`-Belege in beliebigem Kontext liegen in
#387 und sind offen.

## Ergebnis

| | |
|---|---:|
| Fälle | 155 |
| annotiert | **152** in 10 Dateien |
| zurückgehalten | **3** |
| Verdicts der Annotationen | `lemma_7260`/`NOM`, ausnahmslos |
| neue Variantentypen | 0 |
| neue Lemmata | 0 |

Annotiert wird `lemmaRef`, `pos` und `corresp`. `@ana` wird bewusst **nicht**
gesetzt, wie in #189, #198 und Serie 1: die Sense-Zuordnung ist kuratorisch.

Je Datei: MR1 97, LZT 32, MNB 14, FR3 2, TRU 2, FLG 1, GVN 1, MR2 1, PTS 1,
SHF 1. RVBR ist nicht geändert, seine drei Fälle sind die zurückgehaltenen.

## Die drei zurückgehaltenen Fälle, und warum sie das Ärgerlichste an diesem Batch sind

`RVBR_4826_5`, `RVBR_6310_4`, `RVBR_8687_5`, alle drei die Schreibung `frô`.

**Ihr Verdict ist entschieden.** Sie gehören zu den fünf Belegen, die @wachauer
am 01.09. gelesen und als „Frau Minne" bestimmt hat. Zurückgehalten sind sie
nicht aus fachlichen, sondern aus technischen Gründen: für das Paar
(`frô`, `lemma_7260`) gibt es in `variants.xml` **keinen Typ**. Die
Zirkumflex-Schreibung ist dort nur unter `lemma_7250` geführt.

Warum der vorhandene Typ nicht genommen wird: ein `type_N` gehört zu genau
einem Lemma. Trüge `type_25866` Belege unter beiden, meldete
`extract-variants.py` die Kollision und schlüge den Typ bei der nächsten
Regenerierung der häufigeren Seite zu. Das ist derselbe Grund, aus dem #367
zwei Typen neu geprägt statt umgehängt hat (KZW).

Einen neuen Typ zu prägen ist genehmigungspflichtig (#387). Deshalb stehen die
drei in `review-faelle.csv` mit `review_grund = kein-typ`.

**Was zu entscheiden ist, in einem Satz:** soll `frô` einen eigenen
Variantentyp unter `lemma_7260` bekommen? Wenn ja, sind es drei Tokens mehr,
ein Typ mehr, ein Bump des Authority-Index und ein zweiter kleiner Lauf.

Die drei Belege im Verskontext:

```
RVBR_4826_5   trûrte in dem sinne / wâ sint ir nu , frô minne , / waz went ir nu hie schicken ?
RVBR_6310_4   von grundes herzen sinne / nu sagent an , frô minne : / waz mære ist diz ? waz meinent ir ,
RVBR_8687_5   als ob in niht beswârte / wâ sint ir nu , frô minne ? / wâ hânt ir iuwer sinne ,
```

## Zwei Nebenbefunde

**`FLG_1041210_0` trägt `pos="NAM"` ohne Lemma.** Das ist eines der 16 Tokens
aus dem Merge `82c90dd85` (#32), die als einzige Abstrakta im Korpus ein `NAM`
tragen, und es ist zugleich der einzige der 155 Fälle, dessen minne-Seite
überhaupt schon etwas trägt. Sein *vrouwe* (`FLG_1041200_12`, `frovwe`) trug
bereits `pos="NOM"` ohne Lemma und ist jetzt vollständig annotiert. Für die
NAM-Frage in #216 ist das ein Beleg, der von beiden Seiten stützt; entschieden
ist hier nichts.

**Keine der 155 minne-Rohformen beginnt mit einem Großbuchstaben**, aber 98 der
Tokens stehen in `<hi rend="upper_case_first_letter">`. Die Majuskel der Edition
steht im Markup, nicht im Zeichenbestand. Wer sie als Evidenz für die
Personifikation heranziehen will, muss `@rend` lesen; eine Prüfung auf den
ersten Buchstaben findet null Fälle. @wachauer hat `@rend` am 01.09. als Indiz
zugelassen, sobald *vrouwe* und *minne* zusammenstehen.

## Data-Change-Lifecycle

Der Eingriff vergibt `@lemmaRef` an 152 zuvor lemmalose Tokens und **verschiebt
damit die Positionszählung** in den zehn Dateien (nur `<w>` mit `@lemmaRef`
zählen). Korpus-Checkliste vollständig.

| Schritt | Ergebnis |
|---|---|
| Schema (`validate-corpus.py --corpus-only`, 10 Sigel) | Stage-2 0 Fehler. Stage-1 2 Fehlschläge, beide (FLG, LZT) in der dokumentierten 30er-Baseline und unverändert |
| Versions-Bump | Korpus-Index 4.2.8 auf **4.2.9** an vier Stellen, `check-index-versions.py` konsistent |
| `build-corpus-index.py` | 7.546.484 Tokens, exakt 152 mehr als in 4.2.8 (7.546.332) |
| `extract-variants.py --apply` | alle vier Semantik-Zähler **0**, `variants.xml` byte-identisch |
| `build-authority-index.py` | byte-identisch, deshalb **kein** Bump des Authority-Index (bleibt 1.9.2) |
| `build-api.py` | 12 Dateien geändert: die 10 Texte plus `api/index.json` und `api/texts/index.json` |
| Cross-Ref-Audit `--check` | OK, 0 unresolved, keine Sigle über ihrer Baseline |
| `validate-indices.py` | PASS |
| Index-Budget | Korpus-Index bei 84 Prozent, unverändert |

## Reproduktion

```bash
python scripts/ingest/pos-disambig/extract-216-vrouwe155.py \
    --out-dir ingest/pos-disambig/216-vrouwe155
python scripts/ingest/pos-disambig/apply-homograph.py \
    --config ingest/pos-disambig/216-vrouwe155/config.json \
    --cases  ingest/pos-disambig/216-vrouwe155/cases.json \
    --actions ingest/pos-disambig/216-vrouwe155/actions.json \
    --out-dir ingest/pos-disambig/216-vrouwe155 --apply
python scripts/ingest/pos-disambig/revisiondesc-homograph.py \
    --config ingest/pos-disambig/216-vrouwe155/config.json \
    --diff-liste ingest/pos-disambig/216-vrouwe155/diff-liste.csv --apply
```

Ein Replay setzt den Korpusstand vor dem Batch voraus: `apply-homograph.py`
prüft vor jeder Ersetzung, dass das Ziel noch unannotiert ist, den erwarteten
Tokentext trägt und dasselbe `@pos` wie zur Extraktionszeit.

## Was danach in #216 offen bleibt

1. **Das NAM-Lemma „Minne".** Eigener Eintrag in `lexicon.xml` statt
   `lemma_4130` mit `pos="NAM"`, so der Stand vom 28.08. nach Klaus Schmidts
   Zustimmung. Braucht ein neues Lemma, einen neuen Variantentyp und eine
   Sense-Zuordnung, also eine kuratorische Entscheidung.
2. **Die vier unsicheren Belege** `WGA_118600_5`, `RLS_140304_1`,
   `FR1_3026030_4`, `FR1_3001060_7`. Sie gehören nicht zu diesen 155: ihr
   *vrouwe* trägt bereits `lemma_7260`. Liegen bei @wachauer.
3. **Die Reparaturfälle** `SAX_24200_4` (trägt `lemma_3001` *ich*, richtig wäre
   `lemma_4130`) und `MR2_27022210102100_5` (ohne Lemma, ist das Verb).
4. **Die sieben WVV-Anredestellen** ohne Lemma aus dem Kommentar vom 31.08.
5. **Die Regel in `POS-TAGSET.md`**, gültig auch für *werlt* und *sælde*.
6. **Punkt 8**, die sieben GWTK-Verdachtsfälle (*minne* für *mîne*).
7. **Die drei `frô`-Tokens** aus diesem Batch, siehe oben.
