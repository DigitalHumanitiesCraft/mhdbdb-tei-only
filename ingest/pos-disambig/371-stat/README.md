# 371-stat: 76 Tokens, drei neue Variantentypen

Lauf zu [#371](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/371).
Skript: `scripts/ingest/pos-disambig/apply-366-375-371.py` (gemeinsam mit #366 und #375,
weil alle drei dieselbe abgeleitete Schicht anfassen und ein Rebuild teilen).

Quelle: `kzw-review-2026-09-15.json`, KZWs Kommentar vom 15.09.2026, hier abgelegt
nach dem Entfernen **einer** Zeile (siehe unten) und strikt mit `json.loads` geparst.

## Die Arbeitsliste ist `actions`, nicht die Gruppenentscheidung

Das JSON führt auf oberster Ebene zwei Arrays: `faelle` mit 95 beurteilten Fällen und
`actions` mit 76. Die Differenz geht auf: 76 anwendbar, 17 mit `option: OFFEN`, 2 mit
`option: NEU_STAND`, macht 95.

**Wer nach Gruppen arbeitet, lässt die Hälfte liegen.** Zwei Gruppen stehen formal auf
`OFFEN` beziehungsweise ohne Entscheidung, und trotzdem liegen 37 der 76 Arbeitsfälle
in ihnen (`staete` 1, `nom_vrb` 36): KZW hat sie einzeln entschieden, statt die Gruppe
zu schließen. Umgekehrt sticht die Einzelentscheidung auch gegen die Gruppe:
`MSP_1711020_12` steht in der Gruppe `stand` mit dem Gruppenziel `lemma_5732`, trägt
aber `option: lemma_5710` und `status: "anders"`. Es ist der einzige solche Fall.

Die Arbeitsliste lässt sich auf zwei unabhängigen Wegen bilden, und das Skript
verlangt, dass beide dieselbe **Menge** ergeben und nicht nur dieselbe Zahl: einmal
über `faelle`, deren `option` eine `lemma_`-Kennung trägt, einmal über das
`actions`-Array. Die symmetrische Differenz ist leer.

## Was gesetzt wird

Alle 76 Tokens tragen heute **kein** `@lemmaRef`. Es wird also nichts umgehängt.

| Form | Ziellemma | pos | Tokens | Typ |
|---|---|---|---:|---|
| `stat` | `lemma_5710` (stân) | VRB | 18 | `type_20050`, besteht |
| `stat` | `lemma_5732` (stat) | NOM | 27 | `type_20161`, besteht |
| `stat` | `lemma_5712` (stade) | NOM | 26 | **`type_372384`, neu** |
| `stât` | `lemma_5732` (stat) | NOM | 4 | **`type_372386`, neu** |
| `stat` | `lemma_5713` (stæte) | ADJ | 1 | **`type_372385`, neu** |

45 Tokens bekommen eine bestehende Nummer, 31 eine der drei neuen. Die Nummern stehen
hier und im PR-Text **vor** dem ersten gesetzten Token, damit eine Fortsetzung dieses
Laufs keine vierte prägt.

Gemessen an `variants.xml` am 21.09.2026: `lemma_5712` führt drei Formen (`stade`,
`staden`, `stades`) und `stat` ist keine davon; `lemma_5713` führt 96 Formen, darunter
`staet`, `staete`, `state`, `stæte`, aber nicht `stat`; `lemma_5732` führt 38 Formen,
darunter `stat` (`type_20161`), aber nicht `stât` mit Zirkumflex. Das deckt sich mit
KZWs eigenem `hinweis` im JSON, und zwar in allen drei Punkten.

**Kein `@ana`.** KZWs `actions`-Array führt überhaupt kein `sense`-Feld, und die
Sense-Zuordnung ist nach `docs/TEI-MODEL-AUTH-FILES.md` kuratorisch: sie ist nicht aus
dem Korpus rekonstruierbar, sondern wird vom Team vergeben. Ein hier gesetztes `@ana`
wäre kuratorische Arbeit des Skripts. Genau ein Fall (`FR1_4007060_6`) trägt im reichen
`faelle`-Array einen Sense (`lemma_5710_sense_8948`), und der stammt aus unserem
Vorschlag, nicht aus ihrer Entscheidung. Korpusweit tragen nach diesem Lauf
1.554.398 von 7.547.900 `<w>` mit `@lemmaRef` kein `@ana`, gemessen am 21.09.2026
ueber alle 667 Dateien in `tei/`; der Zustand ist also Praxis und kein Loch.

## Drei Tokens, bei denen ein vorhandener Wert weicht

`ADP_6505000_1`, `ADP_6511900_11` und `ADP_6605700_8` tragen heute bereits `pos="NOM"`
(ohne `@lemmaRef`). KZW hat für alle drei `VRB` und `lemma_5710` entschieden, der Wert
wird also überschrieben. **Das ist die einzige Stelle im ganzen Lauf, an der ein
vorhandener Attributwert weicht**, und sie steht deshalb im Skript ausdrücklich und
nicht als Nebenwirkung.

Getragen wird das allein von ihrer Entscheidung in den Feldern `pos`, `option` und
`status`. Nicht von `begruendung` und nicht von `batch_verdict`, siehe den nächsten
Abschnitt.

## Die Feldsemantik des JSON, für den nächsten Leser

Drei Felder sehen nach KZWs Stimme aus und sind es nicht. Gemessen am abgelegten JSON:

**`begruendung` ist dreiteilig.** Über alle 95 Fälle: 19 mal ist es wortgleich mit
`notiz`, also ihr eigener Text; 6 mal steht dort der generierte Satz „Abweichung von
Claudes Vorschlag, ohne Notiz."; 70 mal ein analytischer Text, der nicht aus `notiz`
stammt. Innerhalb der 76 `actions`: 8, 5 und 63. Nur `notiz` ist zuverlässig ihre
Stimme, und sie ist bei 76 der 95 Fälle leer.

**`batch_verdict` ist das Maschinenurteil und nicht ihre Begründung.** Es weicht bei 25
Fällen von `pos` ab, und alle 17 Fälle mit `pos: null` tragen trotzdem ein Urteil samt
Konfidenz. Sein `grund` steht 93 mal auf `confidence` und 2 mal auf `prior-konflikt`.

**`actions.confidence` ist kein Maß für Sicherheit, sondern eine Ableitung aus
`status`.** Die Abbildung ist eindeutig, ohne eine einzige Ausnahme: `status: ok` wird
`high` (63 Fälle), `status: anders` wird `medium` (13). Gegen
`batch_verdict.confidence` weicht sie bei 61 von 76 Fällen ab, ist also auch nicht von
dort übernommen. **Die 13 mit `medium` sind damit gerade die Fälle, in denen KZW vom
Vorschlag abgewichen ist**, also die am gründlichsten angesehenen, und nicht die
unsichersten. Acht von ihnen tragen eine eigene Notiz, darunter „könnte auch seine
stadt sein", „sonst hat der vers ja kein verb?" und „schwierig".

Messvorschrift für alle drei Aussagen: `json.load` auf `kzw-review-2026-09-15.json`,
dann `Counter` über das jeweilige Feldpaar. Die 13 sind namentlich `DAR_38101080_4`,
`DEG_147_6`, `HIS_114_6`, `PZ_66324_5`, `LZT_100650_5`, `LZT_2260_1`,
`MSP_1711020_12`, `DJEM_40210_2`, `FR1_4007060_6`, `MR2_11479100020200_5`,
`PSG_9509880_6`, `PSG_9710780_4`, `REN_222400_2`.

## Zwei Zahlen, die sich zu widersprechen scheinen und es nicht tun

Die `zusammenfassung` des JSON sagt `offen: 7`, das Feld `option` trägt 17 mal `OFFEN`.
**Beide Zahlen sind richtig, sie zählen verschiedene Mengen.** Alle vier Werte der
`zusammenfassung` decken sich exakt mit `status` (95/95, 63/63, 25/25, 7/7), und die
Kreuztabelle löst es auf: `status=offen` und `option=OFFEN` sind 7, `status=anders` und
`option=OFFEN` sind 10, zusammen 17. `status` sagt, wie KZW zu unserem Vorschlag steht,
`option` sagt, was am Ende annotierbar ist.

Das steht hier, weil eine frühere Fassung des Laufplans daraus einen Zählfehler machen
und ihn ins Ticket schreiben wollte.

## Was an KZW zurückgeht

**Das JSON ist nicht maschinell parsbar.** Bei Zeichen 82.382, mitten im
`actions`-Array, steht im Objekt zu `DFR_3102730_1` die Klartextzeile `Prüfer: Alan van
Beek` hinter `"confidence": "high"`. Genau einmal im ganzen Kommentar, und
`json.loads` bricht dort mit `Expecting ',' delimiter` ab. Nach dem Entfernen dieser
einen Zeile parst der Rest strikt durch. Das Ausgabeformat verträgt also keine
Handnotiz, und das sollten KZW und Alan wissen.

Kein Feldschnitt über Regex: der hat keine Kontrolle darüber, ob er ein Objekt verliert,
und `rules/bauweise.md` verlangt für eine unbekannte Eingabe einen harten Fehler statt
eines stillen Überspringens. Das Skript prüft `len(faelle) == 95` und
`len(actions) == 76` als harte Bedingung.

## Nicht angefasst

Die 17 mit `option: OFFEN`: `BRW_104040_7`, `DIO_18629_1`, `DJEM_130312_3`,
`ER_706600_3`, `ER_762600_3`, `FR1_13035040_2`, `GAR_34970_5`,
`HZU2_18313690125015_17`, `HZU2_22613900322026_0`, `HZU2_22913920324018_18`,
`HZU2_22913920324024_13`, `HZU2_7013280424015_5`, `MSG_10507060_4`, `OVG_975200_3`,
`PRJ_1981120_1`, `TRM_1429_3`, `TRO_25465_4`.

Die 2 mit `option: NEU_STAND`: `GAR_99470_6`, `WVO_988600_5`. Sie bräuchten ein neues
Lemma, und Lemmaanlage kommt in diesem Lauf nirgends vor.

`PRJ_1981120_1` ist zusätzlich ein Sonderfall, den der Ticketbody schon nennt: ein
lateinisches Bibelzitat (*in ore duorum vel trium stat omne verbum*), das nach
POS-TAGSET §6.4 ohnehin nicht über `@pos`, sondern über `@xml:lang` erschlossen gehört.

## Verteilung auf das Korpus

37 Dateien: TRY 14, PL2 9, PSG 4, PZ 4, ADP 3, REN 3, TR 3, CL 2, ENE 2, FR1 2, LZT 2,
MAI 2, WH 2, und je einer in AXR, CRO, DAR, DEG, DFR, DGH, DJEM, FBS, FR3, GAU, GL,
HIS, MR2, MSP, MSW, NAR, OVG, OVW, SFE, TUN, VTO, WGM, WVO, ZUK.
