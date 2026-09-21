# Drei Befunde aus #359, die nicht in #359 gehören

Gefunden beim Lesen der Belegstellen für die Prüfseite zu #359, am 21.09.2026.
Keiner davon ist in diesem Lauf bearbeitet worden, und keiner gehört in die
Prüfseite: sie fragen nicht nach Boreks Pferdewortschatz, sie fragen nach der
Annotation des Korpus. Sie stehen hier, damit daraus Vorgänge werden können.

Alle Zahlen sind gegen Korpus-Index 4.2.17 und Authority-Index 1.9.7 gemessen.
Die Messvorschrift steht jeweils dabei.

---

## 1. Sieben Substantive an einem Verblemma (WZB, `lemma_3702`)

**Befund.** `lemma_3702` ist das Verb `lenden` („anlanden, enden"). 44 seiner 45
Korpus-Tokens tragen `pos="VRB"`, das 45. trägt `ADV VRB`. Sieben dieser 44
meinen aber nicht das Verb, sondern den Körperteil, die Lende, und tragen
trotzdem `lemmaRef="lexicon.xml#lemma_3702"` und `pos="VRB"`. Höchstens 38
Tokens meinen also wirklich das Verb.

**Die 44 ist ein Feldwert und keine Bedeutung.** Das ist kein Detail, sondern
der Grund, warum dieser Befund fast durchgerutscht wäre: in der ersten Fassung
stand hier „44 meinen das auch" neben „sieben meinen den Körperteil", und
44 + 7 = 51 bei 45 Tokens. Gefunden hat es die Reviewrunde.

| xml:id | Wortlaut |
|---|---|
| `WZB_35va_29_1` | kvnige werden komen ous deinen **lenden** |
| `WZB_64vb_28_7` | Ew̆er **lenden** sult ir gurten |
| `WZB_100rb_36_2` | Die czwen niren mit der veisticheit, die do bedecken die **lenden** |
| `WZB_100va_31_1` | mit der veisticheit, die do ist bei den **lenden** |
| `WZB_100vb_15_7` | Die czwei nirlein mit dem neczlin, das do ouf in ist bei den **lenden** |
| `WZB_101rb_10_0` | Die czwei nirlein vnd das neczil, das do ist ouf in bei den **lenden** |
| `WZB_104rb_3_3` | die czwei nyrlein vnd die veisticheit, die do ist bei den **lenden** |

**Wohin sie gehören.** `lemma_3701` `lende` (NOM) trägt bereits
`concept_14011100` (Körper von Säugetieren) und `concept_21030000` (Körper von
Menschen). Beide Verwendungen sind hier belegt: die ersten beiden Stellen
sprechen von menschlichen Lenden, die letzten fünf stammen aus dem Levitikus
und beschreiben das Opfertier.

**Warum das zusammenhängt.** Es ist derselbe Befund wie in der Prüfseite, nur
eine Ebene tiefer: Boreks Form `lenden` hat über die exakte Stufe das Verblemma
getroffen, weil dessen Ansetzung zufällig wie der Plural des Substantivs
aussieht. Genau diese Verwechslung steckt auch in der Korpusannotation.

**Messvorschrift.**

```bash
python scripts/review/collect-359-evidence.py --write
python - # dann lemma_3702 in ingest/review/359-borek/evidence.json ansehen
```

Die 45 Belege stehen vollständig in `evidence.json`, jeder mit zwei Versen
Kontext.

**Umfang.** Sieben Tokens in einer Datei (`tei/WZB.tei.xml`). Klein, aber es ist
eine Korpusänderung und zieht den Data-Change-Lifecycle nach sich.

---

## 2. Verbformen an einem Substantivlemma (`lemma_3103`, 122 Tokens)

**Befund.** `lemma_3103` `jagât` ist die Jagd als Substantiv und trägt
`pos="NOM"`. Unter den sechs gelesenen Belegen sind vier Verbformen:

| xml:id | Wortlaut | was es ist |
|---|---|---|
| `AXR_752200_1` | dô **jaget** alexander nâch | Verb |
| `AXR_1267400_1` | dô **jaget** er die widervart | Verb |
| `AXR_1487500_1` | der **jaget** ûf der vart hin nâch | Verb |
| `AXU_15897_4` | ob in darumbe zwîvel **jaget** | Verb |
| `AXS_5585000_5` | dar zô ne frumet nehein **jaget** | Substantiv, richtig |
| `AXU_18452_5` | die wârheit hie dem gelîche **jaget** | unklar |

**Umfang, und was daran gemessen ist.** Das Lemma trägt **122 Tokens in 52
Texten**, alle mit der Schreibung `jaget`. Gelesen sind **sechs**. Die Aussage
„vier von sechs" gilt für die sechs und nicht für die 122; wie viele der
übrigen 116 Verbformen sind, ist **nicht gemessen**.

**Warum das kein Pferdethema ist.** Der Fall ist über Boreks Gangartenliste in
den Bericht geraten (`jaget` steht dort), hat aber mit Pferden nichts zu tun.
Es ist eine Wortart-Disambiguierung und gehört in die Nähe von #189/#198.

**Messvorschrift.** Dieselbe wie oben; die Belege stehen unter dem Schlüssel
`jaget|lemma_3103` in `evidence.json`.

---

## 3. Die Tokens von `gebeine` (`lemma_1958`) sind zu disambiguieren

**Befund.** `lemma_1958` `gebeine` führt in beiden Senses nur
`concept_21030000` (Körper von Menschen). Im Korpus wird das Wort aber auch für
Tiere gebraucht:

| xml:id | Wortlaut |
|---|---|
| `AXU_23544_3` | gar des **orses** gebeine und hiez daz bewinden mit sîdînen tuochen linden |
| `HTR_193190_2` | des **lewen** gebeine ist âne marc |

Damit ist KZWs Bedingung vom 16.09. erfüllt („wenn ein Text in unserem Korpus
diese Verwendung belegt"), und das Lemma bekommt zusätzlich
`concept_14011100`. Das steht als Vorschlag in der Prüfseite.

**Was offen bleibt und hier hingehört.** KZW verlangt im selben Satz, dass „die
betreffenden Tokens dabei auch gleich sauber disambiguiert werden". Das ist
Korpusarbeit an bis zu 207 Tokens in 79 Texten und kein Anhang an eine
Prüfseite.

**Was gemessen ist und was nicht.** Gelesen sind **neun** der 207 Belege,
nämlich die mit einem Pferdewort im Kontextfenster. Zwei davon sind tierisch.
Die Zahl beantwortet „kommt vor", nicht „kommt wie oft vor". Der Löwenbeleg ist
dem Filter nur zugelaufen, weil `marc` in der Wortliste steht (Streitross) und
an dieser Stelle Knochenmark heißt: ein Zufallstreffer. Ein Filter für
Tierwörter im Allgemeinen ist nicht gelaufen.

**Messvorschrift.**

```bash
python scripts/review/collect-359-evidence.py --counts
```

gibt die 207 Tokens in 79 Texten aus. Die gesammelten Belege stehen unter
`gebeine|lemma_1958` in `evidence.json`.

---

## Was diese drei gemeinsam haben

Alle drei sind an Belegstellen gefunden worden und nicht an Stichwörtern, und
alle drei betreffen `tei/` oder `authority-files/`. Beides ist der Grund, warum
sie hier stehen und nicht umgesetzt sind: Spur B dieses Laufs schreibt nicht in
die Daten.
