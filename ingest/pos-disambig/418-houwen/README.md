# 418-houwen: die 13 `hawe`-Belege

Prüfcharge zu [#418](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/418).
Anders als die übrigen Chargen unter `pos-disambig/` ist dies **kein Lauf eines
Disambiguierungs-Skripts**, sondern eine Vorlage für eine Handprüfung: die
Zuordnung steht hier noch aus.

## Die Frage

Dreizehn Tokens im Korpus tragen `@corresp` auf `type_117159` (Schreibung *hawe*).
Auf `main` hängen **alle dreizehn** am Lemma `lemma_2598` *haben*. Der offene
PR [#416](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/pull/416)
setzt einen davon, `AC3_23010_1` („hawe vnd schaufel"), auf `lemma_9644` *houwe*.

Zu klären ist je Beleg, ob eine Verbform zu *houwen* (`lemma_2923`), das
Substantiv *houwe* (`lemma_9644`) oder doch *haben* (`lemma_2598`) vorliegt.
`scripts/ingest/pos-disambig/fix-198-restfaelle.py:20` aus jenem PR nennt die
zwölf übrigen pauschal „Imperative zu *houwen*". Genau das ist zu prüfen: beim
Erstellen dieser Charge sah mindestens `GAR_1530_5` („war er mein vrawen **hawe**
getan") eher nach einer Form von *haben* aus.

## Dateien

| Datei | Inhalt |
|---|---|
| `faelle.csv` | die 13 Belege mit Kontext, Werk und Ist-Zuordnung, `;`-getrennt |
| `pruefseite.html` | dieselben Belege als Prüfoberfläche, mit Markdown-Export |

Die Prüfseite liegt live unter
<https://dhcraft.org/mhdbdb-tei-only/ingest/pos-disambig/418-houwen/pruefseite.html>
und braucht keinen Build: sie trägt ihre Daten inline. Eingaben liegen im
`localStorage` des jeweiligen Browsers, der Export ist eine Markdown-Tabelle für
den Vorgang.

## Zwei Eigenheiten der Daten

**Der Reader kann nur bei zwei der sieben Texte an die Stelle springen.** Der
Sprung über `?verseId=` sucht ein gerendertes `<l>`, und AC2, AC3, CEFB, DES2 und
KFB haben keine `<l>`-Elemente, sondern Prosa mit `<lb/>`. Bei diesen fünf öffnet
der Link nur den Text. `?verse=` wäre kein Ersatz, weil sich `lb/@n` seitenweise
wiederholt (AC2: 1.110 `<lb/>` mit 31 verschiedenen Werten).

**Der Kontext trägt die Interpunktion des Korpus mit**, weil die `<pc>`-Elemente
in Dokumentordnung mitgelesen und nach ihrem `@join` angefügt werden, genau wie
im Reader. Für die Entscheidung Imperativ gegen
Konjunktiv ist die Satzgrenze oft das Ausschlaggebende. Die spitzen Klammern in
`GAR_1530_5` sind Redezeichen des Korpus, kein Markup-Rest.

## Warum das mehr als eine Zuordnungsfrage ist

Nach dem Merge von #416 hinge `type_117159` an zwei Lemmata. Das wäre der erste
Fall im Korpus: gemessen am 2026-09-10 sind 256.762 von 256.762 Typ-Ids genau
einem Lemma zugeordnet. Der Kommentar im Skript nimmt an, das kippe von selbst,
sobald die zwölf umgehängt sind. Das trägt nur, wenn alle zwölf zum selben Lemma
wandern.

`scripts/sync/extract-variants.py` meldet den Fall, gatet ihn aber nicht.
