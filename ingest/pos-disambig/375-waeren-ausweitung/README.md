# 375-waeren-ausweitung: die vier letzten Fälle

Lauf zu [#375](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/375).
Skript: `scripts/ingest/pos-disambig/apply-366-375-371.py` (gemeinsam mit #366 und #371,
weil alle drei dieselbe abgeleitete Schicht anfassen und ein Rebuild teilen).

Dieser Ordner lag seit dem 31.08. mit `faelle.csv` und `ids.txt` bereit. Das README
kommt mit dem Abschluss dazu.

## Was schon getan war, und wie das gemessen wurde

Der Vorgang führt 16 Fälle: acht „eindeutige" und acht, die KZW lesen sollte. Beide
Hälften sind erledigt, aber zu verschiedenen Zeiten, und der Thread sagt das nicht
deutlich genug.

**Die acht eindeutigen sind seit dem 14.09. umannotiert**, in PR #438 zusammen mit #308
und #432. Am 21.09. nachgemessen, jedes Token einzeln gegen den Korpus: alle acht tragen
`lemma_7338` mit `pos="ADJ"`. Namentlich `SL_851_3` (`type_372376`), `SL_2648_4`,
`SL_3945_4`, `PRT_20337_5`, `TSY_3928_2`, `URS_11800_2` (alle `type_287014`),
`NAR_9801800_5` und `MSG_21611030_3` (beide `type_372364`). 8 von 8.

**KZW hat die acht zu lesenden am 14.09. beantwortet**, mit einer Tabelle: vier ADJ,
vier VRB. Die vier VRB (`OVG_6534200_1`, `BAR_2276_1`, `DFL_19560_1`, `BRF_53370_1`)
bestätigen den Ist-Zustand, sie stehen bereits auf `lemma_7505` mit `pos="VRB"` und
werden nicht angefasst.

**Arbeit sind damit genau vier Tokens**, und nicht 16.

## Die vier

| Wort-ID | Form | Sicherheit (KZW) | vorher | nachher |
|---|---|---|---|---|
| `TIT_50020_2` | wâren | sehr hoch | `lemma_7505` VRB `type_273621` | `lemma_7338` ADJ `type_287014` |
| `PZ_23625_1` | wâren | mittel bis hoch | wie oben | wie oben |
| `NLC_196220_1` | wâren | hoch | wie oben | wie oben |
| `KU_1534_3` | wâren | sehr hoch | wie oben | wie oben |

## Keine neue Typnummer

Der Ticketbody nennt drei Zieltypen (`type_287014` für `wâren`, `type_372364` für
`woren`, eine neue Nummer für `waeren`) und das Skript aus PR #438 trägt dieselbe
Tabelle. **Für diese vier Fälle wird davon nur einer gebraucht.** Alle vier tragen die
Form `wâren` mit Zirkumflex, also den bestehenden `type_287014` unter `lemma_7338`.
`woren` und `waeren` kommen unter den vier gar nicht vor.

Die Typtabelle für die ganze Menge der 16 zu übernehmen, statt die vier Formen zu
messen, wäre derselbe Fehler wie eine übernommene Zahl, nur an einer Stelle, die
niemand für eine Zahl hält.

Unverändert gilt die Warnung des Tickets: **`type_80601` gehört zur Form `waren` ohne
Zirkumflex** (47 Belege unter `lemma_7338`) und wird hier nicht angefasst.

## Kein `@ana`

Keiner der 16 Fälle trägt ein `@ana`, und der Vorgang stellt die Sense-Frage
ausdrücklich nicht (Body: „**keiner trägt ein `@ana`**, [...] Die Sense-Frage stellt
sich also auch hier nicht"). Die vier bleiben dabei, wie schon die acht aus PR #438.
