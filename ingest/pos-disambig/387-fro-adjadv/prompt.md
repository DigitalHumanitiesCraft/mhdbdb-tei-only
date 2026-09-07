# #387 Nachlauf: ADJ oder ADV bei feststehendem Lemma

Version 1, 06.09.2026.

## Was hier NICHT mehr zur Debatte steht

Das **Lemma ist entschieden**: alle Belege dieses Laufs sind `lemma_7250`
(*vrô* „froh"). Der erste Lauf war sich darin bei allen 30 Fällen einig, mit
hoher Übereinstimmung in der Begründung. Bitte das Lemma nicht neu aufrollen
und insbesondere nicht auf `lemma_7260` (*vrouwe*) ausweichen. Wer meint, ein
Beleg sei doch die Anrede, schreibt das als `unentschieden` mit Begründung,
statt das Lemma zu wechseln.

**`NOM` ist in diesem Lauf keine Option.** Substantivierungen sind als eigene
Klasse ausgesondert und liegen bei @wachauer.

**`GRA` wird nie vergeben** (POS-TAGSET §3 und §6.3d), auch nicht, wenn das
Lemma den Tag führt.

Zu entscheiden ist also genau eine Frage: **ADJ oder ADV.**

## Der gemessene Bestand, und er ist deutlich

Gemessen am 06.09.2026 über alle 667 Korpusdateien, Stand `origin/main`, also
**vor** dem Lauf vom selben Tag:

| `@pos` an `lemma_7250` | Tokens |
|---|---:|
| `ADJ ADV` (unaufgelöstes Kompositum) | 4.661 |
| `ADJ` | 76 |
| `ADJ GRA` | 64 |
| `NOM ADJ ADV` | 45 |
| `NOM ADJ` | 9 |
| `NOM` | 7 |
| `NAM` | 5 |
| **`ADV` allein** | **0** |

**In 5.215 annotierten Belegen von *vrô* trägt kein einziger den Tag `ADV`
allein.** Der eine, den es heute gibt (`NEIC_12710160_0`), stammt aus dem Lauf
vom 06.09. und ist damit der erste seiner Art überhaupt.

Das ist kein Verbot. Der Zielzustand nach POS-TAGSET §4 ist die Auflösung der
Komposita zu einem einzelnen Tag, und wenn ADV richtig ist, gehört ADV hin.
Aber es ist ein Prior, gegen den zu entscheiden eine Begründung braucht, die
über „lässt sich adverbial lesen" hinausgeht. Der erste Lauf hat bei 14 der 30
Fälle ADV vorgeschlagen. Das wäre, gemessen am Bestand, eine sehr große
Abweichung, und genau deshalb läuft diese Runde.

## Entscheidungsregeln

1. **Prädikativ mit Kopula** (`sîn`, `wesen`, `werden`, `belîben`, auch
   elliptisch): **ADJ**. „so wer ich fro geporn", „des wart er fro".
2. **Depiktiv**, also sekundäres Prädikat über Subjekt oder Objekt, auch ohne
   Kopula: **ADJ**. „vnd schiet enweg mit fröuden fro" sagt, dass *er* froh
   war, als er wegging, nicht wie er ging. Das ist der Fall, den man am
   leichtesten für ADV hält, und er ist der häufigste in dieser Menge.
   Prüffrage: lässt sich „und er war dabei froh" einsetzen? Dann ADJ.
3. **ADV nur**, wenn das Wort die **Art und Weise der Handlung** angibt und
   sich **nicht** als Aussage über eine Person oder Sache lesen lässt.
   Prüffrage: geht „auf frohe Weise" und geht „und er war dabei froh"
   **nicht**? Nur dann ADV.
4. **Antithesen und Ellipsen** („gein trurec fro, gein sorgen lust") tragen
   kein Verb, an dem sich ADV festmachen liesse. In der Regel ADJ; wenn die
   Fügung eher nominal wirkt, `unentschieden` mit Begründung, nicht NOM.

## Was zu liefern ist

Je Fall ein Objekt:

```json
{"xml_id": "...", "form": "...", "lemma": "lemma_7250", "pos": "ADJ",
 "begruendung": "ein Satz, der die angewandte Regel nennt",
 "confidence": "high"}
```

- `pos`: `ADJ`, `ADV` oder `unentschieden`.
- `confidence`: `high` nur, wenn die syntaktische Fügung eindeutig ist.
  `medium` ist erlaubt und wird **nicht** angewendet.
- **`unentschieden` ist ein gültiges und erwünschtes Ergebnis.** Diese Fälle
  gehen an @wachauer. Eine erzwungene Entscheidung ist schlechter als eine
  saubere Vorlage: der erste Lauf hat sie zu Recht zurückgehalten, und diese
  Runde soll nicht dasselbe Material mit mehr Zuversicht noch einmal
  beurteilen, sondern die engere Frage beantworten, wo sie beantwortbar ist.

Die Felder `vorschlag_lauf1` und `begruendung_lauf1` im Bündel sind das Urteil
der ersten Runde. Sie stehen dabei, damit sichtbar ist, worüber gestritten
wird, und sind **keine Vorgabe**. Wer ihnen widerspricht, sagt warum.
