# 363-hausenblase: 19 Belege, 32 Tokens, ein Lemma

Lauf zu [#363](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/363).
Skript: `scripts/ingest/pos-disambig/fix-363-hausenblase.py`.

## Was gemeldet war und was tatsächlich dranhing

Gemeldet war ein Token: `MBS5_2151412120_10`, die Schreibung *hawssen*, gelemmatisiert
auf `lemma_2730` *heiʒ*, also als Adjektiv „heiß". Die korpusweite Suche nach den
Schreibformen (Erstglied `hau-`/`haw-`/`hu-`, Zweitglied `pl-`/`bl-` im
Nachbartoken, dazu die zusammengeschriebenen Formen) findet **19 Belege in 7
Sigeln**, und alle sieben sind Kochbücher: HUB3 (7), SUB1 (5), KDO (2), MBS5 (2),
MBS2 (1), KBL3 (1), KBL4 (1). Es gibt keinen Beleg außerhalb der Rezeptliteratur.

Von den 19 waren 5 richtig. Die übrigen 14 verteilten sich auf sieben Lemmata:
das Adjektiv *heiʒ*, das Verb *hûsen* „wohnen", den *hasen*, das Blatt einer
Pflanze (`lemma_737` *blat*, Konzept „Vegetation"), die menschliche Blase, die
Mönchstonsur (`lemma_738` *blate*) und `lemma_27031` *hasenblâse*. Sieben Tokens
trugen überhaupt kein `@lemmaRef`.

Die Bestätigung steht im Korpus selbst. KBL4 (Reichenauer Kochbuch) schreibt:

> „ovch ist die **husen blater** vnd all **fisch blatra** guot in sulcza"

Der Schreiber stellt die Hausenblase in eine Reihe mit „allen Fischblasen".

## Die Entscheidung

KZW am 10.09.2026 im Vorgang, zwei Kommentare:

> „Alle Komposita und Kookurrenzen in diesem Kontext, egal in welcher Schreibart,
> müssen zur Fischblase (,Organe von Fischen, Atmung von Fischen, Verarbeitung von
> Fischen')."

> „Schmeiß die hasenblâse weg (lemma_27031), diese existiert nicht."

Beide sind umgesetzt. `lemma_27031` hatte korpusweit genau einen Beleg, und das
war das falsch gelesene KDO-Kompositum *haußenploßenn*; nach der Korrektur stand
der Eintrag auf null.

## Was das Skript geschrieben hat

| Menge | Ziel |
|---|---|
| 6 zusammengeschriebene Komposita | `lemma_49714`, `@ana` auf `lemma_49714_sense_78649` |
| 13 getrennt geschriebene Paare, **beide** Tokens | dasselbe Lemma, derselbe Sense, `@pos` je Token, `@corresp` je Token |
| `lemma_27031` *hasenblâse* | aus `lexicon.xml` gelöscht |
| `type_131170` in `lemma_2670_sense_4300` | entfernt, die Form *haueßenn* belegt den hasen nicht mehr |

Die getrennten Paare sind als **Mehrwort-Einheit** kodiert, wie `lemma_3141`
*Joie de la Court* und `lemma_9250` *Schastel Marveile*, das ebenfalls die
getrennte und die zusammengeschriebene Schreibung trägt. Das Muster steht in
`docs/TEI-MODEL.md` §4.1a; `lemma_49714` ist der erste Fall darin, der kein
Eigenname ist.

## Die Typen, und warum nicht alle wandern

Ein `type_N` ist eine Schreibform **eines** Lemmas. `extract-variants.py` löst ein
mehrdeutiges Paar per Mehrheit auf, und das ist genau der Ausgang, den es zu
vermeiden gilt. Deshalb entscheidet das Skript pro Form:

- **Umgehängt** wird, wo korpusweit ausschließlich Tokens dieser Menge den Typ
  tragen: `type_131170` *haueßenn*, `type_131175` *haußenploßenn*, `type_272472`
  *plotter*, `type_272473` *ploter*, `type_274810` *plateren*. Dort wandert die
  Form zu Recht als Ganzes, das Quell-Lemma verliert sie.
- **Neu geprägt** wird, wo die Schreibung auch nach der Korrektur noch das alte
  Lemma belegt. `type_106683` *pleter* trägt 45 Tokens, 43 davon bleiben bei
  `lemma_737` *blat*; wer den Typ mitnähme, risse sie mit. Neu sind `type_372366`
  bis `type_372375`, sortiert nach Form.

Entschieden wird das zur Laufzeit, nicht aus einer Liste gelesen: das Skript
scannt alle 667 Korpusdateien und prägt neu, sobald ein Typ auch nur ein fremdes
Token trägt. Die Aufteilung 5 zu 10 ist damit ein Messergebnis dieses Laufs und
keine Vorgabe. Der Trockenlauf von `extract-variants.py` bestätigt es von der
anderen Seite: 10 Typen dazu, 0 weg, 5 mit geänderter Lemmazuordnung, **0 Typen
mit mehr als einem Lemma**.

## Dateien

| Datei | Inhalt |
|---|---|
| `faelle.csv` | die 32 Tokens mit Kontext, Vorher- und Nachher-Zuordnung, `;`-getrennt |

## Korrektur an den eigenen früheren Kommentaren

Zwei Kommentare in #363, vom 06.09. und vom 10.09. mittags, behaupten, eine
Mehrwort-Einheit wäre „die erste im Korpus". Beide sind falsch, ein Blick in
`variants.xml` hätte gereicht; daraus wurde #425. Und die Tabelle im Kommentar vom
10.09. nennt „fünf Belege ohne `lemmaRef`". Es sind sieben: fünf Erstglieder in
HUB3, dazu `KBL4_1051192050_12` *husen* und `KDO_121170100_3` *plossenn*.
