# Glossar Kochbuchforschung gegen das Lexikon (#554, Schritt 2)

Prüfmaterial, keine Entscheidung. Nichts davon steht in `authority-files/` oder `tei/`, und
nichts davon ist ein Beschluss darüber, welcher Glossar-Eintrag zu welchem Lemma gehört.
Quelle: [`sources/glossar-kochbuchforschung/`](../../sources/glossar-kochbuchforschung/README.md)
(bereinigter WordPress-Export, Stand 2026-10-08). Erzeugt von
`scripts/ingest/glossar-554/ordne-lemmata-zu.py`; Stand des Lemmabestands: `api/lemmata/index.json`
und `authority-files/variants.xml` bei `origin/main` 81e4928d8 (43.710 Lemmata).

## Menge

189 veröffentlichte Glossar-Einträge mit `sprachstufe = gmh`. Der Abgleich ist der des Issues:
Titel gegen `lemma`, beide über die MHG-Normalisierung des Projekts
(`scripts/mhg_normalizer.py`) plus `ë` und `ʒ`; kein Varianten- und Präfixabgleich, kein
Abgleich der Wortart. Ergebnis wie im Issue: 159 genau ein Lemma, 5 mehrere Lemmata
(Homographen), 25 keines (159 + 5 + 25 = 189).

## Dateien (TSV, UTF-8, LF, Tab-getrennt)

| Datei | Inhalt | Zeilen |
|---|---|--:|
| `zuordnung-eindeutig.tsv` | Glossar-ID (WordPress `post_id`) → `lemma_N` für die 159 eindeutigen Titel, mit Wortklasse laut Glossar, `pos` und `posAll` des Lemmas und Belegzahl im Korpus | 159 |
| `pruefliste.tsv` | die 5 Homographen und die 25 Fälle ohne Treffer, eine Zeile je Kandidat (Fall ohne jeden Kandidaten: eine Zeile mit leerem `lemma_id`) | 67 (30 Fälle, davon 4 ohne Kandidat) |
| `pruefliste-belege.tsv` | je Kandidat der Prüfliste bis zu drei Korpusbelege: Sigle, `xml:id` des `<w>`, Kontext (vier Wörter links und rechts, das Beleg-Wort in `[[ ]]`) | 147 |

`belege_im_korpus` zählt die `<w>` mit dem Lemma in `@lemmaRef` über `tei/` (Token-genau,
CONTRACTS B.1), nicht das Feld der API. Die Belege eines Kandidaten stammen, soweit möglich,
aus verschiedenen Siglen (das erste Vorkommen je Sigle in Dateireihenfolge, dann aufgefüllt).

## Arten von Kandidaten (Spalte `kandidat_art`)

| Art | Bedeutung | Gilt für |
|---|---|---|
| `exakt` | Titel und Lemma stimmen normalisiert überein | Homographen |
| `ohne-zusatz` | Titel ohne angehängte Klammer (`zam (adj)` → `zam`) trifft exakt | Fälle ohne Treffer |
| `variante` | der Titel steht in `variants.xml` als Schreibvariante dieses Lemmas | Fälle ohne Treffer |
| `praefix` | Lemma und Titel (normalisiert, je mindestens 4 Zeichen) sind Anfangsstück voneinander, Längenunterschied höchstens 3 | Fälle ohne Treffer |
| `edit1` | Levenshtein-Abstand 1 auf der normalisierten Form, Länge mindestens 5 | Fälle ohne Treffer |

Je Fall höchstens acht Kandidaten der Arten `variante`, `praefix` und `edit1`, sortiert nach
Art, dann nach Belegzahl; wo abgeschnitten wurde, steht es in der Spalte `hinweis`. Die Spalte
`schreibvarianten_glossar` führt die Schreibvarianten auf, die der Glossar-Eintrag selbst
nennt, damit sich ein Kandidat gegen den Eintrag lesen lässt.

## Wie man die Liste liest

- **`edit1` und `praefix` sind Lesehilfen, keine Funde.** `henne` bringt `denne` und `tenne`
  hervor; wer sie annimmt, hätte nur den Abstand gemessen. Mit Belegen aus dem Korpus lässt
  sich in der Regel in einer Minute sagen, ob ein Kandidat gemeint sein kann.
- **`variante` ist stärker, aber nicht gesichert:** `variants.xml` ordnet einer Form das Lemma
  zu, unter dem sie im Korpus steht, und das kann selbst falsch sein.
- **Auch eine eindeutige Zuordnung ist Titelgleichheit, nicht Bedeutungsgleichheit.** Wo bei uns
  nur eines von zwei Homonymen existiert, trifft der Titel genau dieses. Vor einer Übernahme
  (Schritt 3 im Issue, noch nicht begonnen) gehört eine Stichprobe gegen die Wortklasse
  (`wortklasse_glossar` neben `pos`) und die Belege dazu.
- Vier Fälle ohne jeden Kandidaten: `hërrenëʒʒen`, `blancmanger`, `lêrchenvuoʒ`,
  `brâmberstrûch`. Bei `hërrenëʒʒen` und `lêrchenvuoʒ` nennt das Glossar die Schreibung
  getrennt (`herren ezzen`, `lerchen fuoz`).
- Die beiden Einträge `zam (adj)` und `zam (nom)` führen auf dasselbe Lemma `lemma_7758`; ob
  bei uns Adjektiv und Nomen getrennt werden müssten, zeigt die Prüfliste nicht.

## Nachmessen

```
python -E -P scripts/ingest/glossar-554/messe-export.py sources/glossar-kochbuchforschung/digest_ivum.wordpress.2026-10-08.bereinigt.xml
python -E -P scripts/ingest/glossar-554/ordne-lemmata-zu.py sources/glossar-kochbuchforschung/digest_ivum.wordpress.2026-10-08.bereinigt.xml
```

Der zweite Lauf liest alle 667 Korpusdateien und braucht gut drei Minuten. Er ist
deterministisch; ändert sich der Lemmabestand oder der Korpus, ändern sich Belegzahlen und
Kandidaten, und die Dateien hier sind dann ein Stand von gestern.
