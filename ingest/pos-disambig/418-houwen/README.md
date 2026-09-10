# 418-houwen: die 13 `hawe`-Belege

Prüfcharge zu [#418](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/418).
Anders als die übrigen Chargen unter `pos-disambig/` ist dies **kein Lauf eines
Disambiguierungs-Skripts**, sondern eine Vorlage für eine Handprüfung: die Zuordnung
steht hier noch aus.

## Die Frage

Dreizehn Tokens im Korpus tragen `@corresp` auf `type_117159` (Schreibung *hawe*).
Zwölf hängen am Lemma `lemma_2598` *haben*, einer an `lemma_9644` *houwe*
(gesetzt in PR #416). Zu klären ist je Beleg, ob eine Verbform zu *houwen*
(`lemma_2923`), das Substantiv *houwe* (`lemma_9644`) oder doch *haben*
(`lemma_2598`) vorliegt.

`scripts/ingest/pos-disambig/fix-198-restfaelle.py:19` nennt die zwölf pauschal
„Imperative zu *houwen*". Genau das ist zu prüfen: beim Erstellen dieser Charge
sah mindestens `GAR_1530_5` („war er mein vrawen **hawe** getan") eher nach einer
Form von *haben* aus.

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

## Warum das mehr als eine Zuordnungsfrage ist

Solange `type_117159` an zwei Lemmata hängt, verletzt das Korpus eine Eigenschaft,
die sonst ausnahmslos gilt: gemessen am 2026-09-10 sind 256.762 von 256.762
Typ-Ids genau einem Lemma zugeordnet. Der Kommentar im Skript nimmt an, das kippe
von selbst, sobald die zwölf umgehängt sind. Das trägt nur, wenn alle zwölf zum
selben Lemma wandern.

`scripts/sync/extract-variants.py` meldet den Fall, gatet ihn aber nicht.
