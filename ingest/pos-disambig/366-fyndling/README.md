# 366-fyndling: 8 Tokens aus einem externen Beitrag, sieben neue Variantentypen

Lauf zu [#366](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/366).
Skript: `scripts/ingest/pos-disambig/apply-366-375-371.py` (gemeinsam mit #375 und #371,
weil alle drei dieselbe abgeleitete Schicht anfassen und ein Rebuild teilen).

## Herkunft

Ralf Vitasek (fyndling.de, GitHub @neongrau) hat am 12.08.2026 per Mail an
mhdbdb@plus.ac.at eine kuratierte CSV mit neun unlemmatisierten Wortformen aus unseren
Kochrezept-Texten eingesandt, entstanden durch Abgleich der fyndling-Transkriptionen
gegen `variants.xml`. Die Spalte `lemma` war bewusst leer: er liefert moderne Lesarten
und Wikidata-Konzepte, keine mittelhochdeutschen Lemmata.

Der Beitrag ist ausdrücklich unter CC BY-NC-SA 4.0 freigegeben. Die Schreibungen
stammen bei den betroffenen Handschriften aus CoReMA-Transkriptionen (Uni Graz,
CC BY 4.0).

Eine der neun (`KDO_121170100_3` *plossenn*) ist am 10.09. mit PR #429 unter #363
annotiert worden, weil sie das Zweitglied einer getrennt geschriebenen Hausenblase ist.
Die übrigen acht stehen hier.

## Die acht Tokens und ihre Entscheidung

Alle acht trugen bis zu diesem Lauf **kein** `@lemmaRef`, `@pos` oder `@corresp`,
einzeln am Korpus geprüft.

| Wort-ID | Form | Lesart | Ziellemma | Entscheidung |
|---|---|---|---|---|
| `DES2_591312010_1` | bersige | Barsch | `lemma_26988` *persich* NOM | KZW 17.09., Punkt 1 |
| `KBL4_981191050_3` | gewuertz | Gewürz | `lemma_7736` *wurz* NOM | KZW 17.09., Punkt 2 |
| `KDO_121160700_11` | gehornn | Geweih | `lemma_2039` *gehürne* NOM | KZW 17.09., Punkt 3 |
| `KDO_123250200_3` | würtzenn | Gewürz | `lemma_7736` *wurz* NOM | KZW 17.09., Punkt 4 |
| `KDO_124310400_12` | würczenn | Gewürz | `lemma_7736` *wurz* NOM | KZW 17.09., Punkt 5 |
| `KDO_123290200_10` | zimendtrinttenn | Zimt | `lemma_26776` *zinemînrinde* NOM | KZW 11.09. |
| `KBL3_11282040_1` | hawsen | Hausen, der Fisch | `lemma_42619` *hûse* NOM | KZW 11.09. |
| `MBS2_52060_11` | hawsen | Hausen, der Fisch | `lemma_42619` *hûse* NOM | KZW 11.09. |

`KDO_123250200_3` steht in KZWs Kommentar als `DO_123250200_3` getippt. Das Skript
sucht nach der `xml:id` und nicht nach der Schreibung im Kommentar.

## Die sieben neuen Typen

| Typ | Form | unter Lemma | Tokens |
|---|---|---|---:|
| `type_372377` | bersige | `lemma_26988` | 1 |
| `type_372378` | gehornn | `lemma_2039` | 1 |
| `type_372379` | gewuertz | `lemma_7736` | 1 |
| `type_372380` | hawsen | `lemma_42619` | 2 |
| `type_372381` | würczenn | `lemma_7736` | 1 |
| `type_372382` | würtzenn | `lemma_7736` | 1 |
| `type_372383` | zimendtrinttenn | `lemma_26776` | 1 |

Sieben Typen für acht Tokens, weil `KBL3_11282040_1` und `MBS2_52060_11` dieselbe Form
unter demselben Lemma sind.

Gemessen am 21.09.2026 trägt **keine** der sieben Schreibungen unter ihrem Ziellemma
bereits eine Nummer. Es wird deshalb geprägt und nicht umgehängt, nach der Regel aus
#367: eine bestehende Nummer umzuhängen risse die Tokens mit, die sie heute unter
ihrem alten Lemma tragen.

**Der Fall, an dem das hart wird, ist `hawsen`.** Die Form wird bereits geführt, aber
unter `lemma_49714` *hûsenblâter* als `type_372368`, geprägt im #363-Lauf für die
getrennt geschriebenen Erstglieder der Hausenblase. Unsere beiden Tokens gehören zum
Fisch (`lemma_42619`). Ein Umhängen von `type_372368` hätte jene Tokens mitgerissen.
Dasselbe Muster zeigt `hausen`, das unter `lemma_2934` (*hûsen*, wohnen) und unter
`lemma_49714` je eine eigene Nummer trägt.

## KZWs Frage zu `bersige`, beantwortet

Sie fragt am 17.09.: „gibt es eigentlich eh schon als Wortvariante unter persich
(lemma_26988), warum ist das nicht automatisch annotiert worden?"

Gemessen führt `lemma_26988` genau drei Formen: `bersich` (`type_130848`), `persich`
(`type_130849`) und `perschiche` (`type_270305`). **`bersige` mit -e steht nicht
darunter**, und korpusweit führt überhaupt kein Lemma diese Form. Ihre Erinnerung trifft
`bersich`, eine um einen Buchstaben abweichende Schreibung.

Das ist die Antwort auf ihr „warum nicht automatisch": die Annotation ist formgenau, und
für sie ist eine abweichende Schreibung eine andere Form, auch wenn ein Mensch beide
sofort zusammenbringt. Deshalb genau der neue Typ `type_372377`.

## Kein `@ana`

KZW hat in keinem der acht Fälle einen Sense benannt. Die Sense-Zuordnung ist nach
`docs/TEI-MODEL-AUTH-FILES.md` kuratorisch, also vom Team zu vergeben und nicht aus dem
Korpus rekonstruierbar; ein hier gesetztes `@ana` wäre kuratorische Arbeit des Skripts.
Drei der Ziellemmata (`lemma_26988`, `lemma_42619`, `lemma_26776`) tragen genau einen
Sense, die Zuordnung wäre dort technisch eindeutig, aber technisch eindeutig ist nicht
dasselbe wie entschieden. Korpusweit tragen nach diesem Lauf 1.554.398 von
7.547.900 `<w>` mit `@lemmaRef` kein `@ana`, gemessen am 21.09.2026 ueber alle
667 Dateien in `tei/`.

Das ist damit der Rest, der nach diesem Lauf an KZW offenbleibt.

## Der `hirne`-Auftrag ist nicht ausgeführt

KZW schreibt zu `gehornn`: „Ja, das dürfte tatsächlich das Hirschhorn (Geweih) sein,
daraus hat man bis ins 19. Jh. Sülze gemacht. **Entferne diese Schreibvariante aus dem
lemma hirne (lemma_2853), denn das ist leer und ohne Token. Füge es zu lemma_2039
(gehürne) hinzu.**"

Die zweite Hälfte ist ausgeführt: `KDO_121160700_11` hängt jetzt an `lemma_2039`, und
die Form `gehornn` bekommt dort mit `type_372378` ihren Eintrag in `variants.xml`.

**Die erste Hälfte hat kein Objekt und ist deshalb nicht ausgeführt.** Gemessen am
21.09.2026:

- `lemma_2853` trägt korpusweit **228 Tokens in 66 Dateien**, ist also nicht leer.
- Die Form `gehornn` steht **nicht** unter `lemma_2853`. Dort stehen `hirne`, `hirn`,
  `hirnes`, `hiern`, `hirenn`, `gehirne`, `gehirns`, `hirnn`, `hirnin` und weitere.
  Es gibt dort also nichts zu entfernen.

Beides steht als Rückfrage im Statuskommentar zu #366, mit dem Vorlauf, was bereits
umgesetzt ist. Zur Einordnung mitgemessen, am 21.09.2026 nach diesem Lauf:
`lemma_2039` trägt 40 Tokens in 15 Dateien, vor dem Lauf waren es 39. Und `gehornn`
stand auch dort noch nicht, das Hinzufügen war also echte Arbeit und kein Leerlauf.
