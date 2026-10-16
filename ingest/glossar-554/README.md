# Glossar Kochbuchforschung gegen das Lexikon (#554, Schritt 2)

Die Übernahme in `lexicon.xml` (Zuordnung, Kommentare, Prüfseite, Klug-Verweise) steht in
[UEBERNAHME.md](UEBERNAHME.md); diese Datei beschreibt die Prüfliste davor. Die Literatur, die die Kommentare zitieren, steht in
[`literatur.tsv`](literatur.tsv) (Erläuterung am Ende von UEBERNAHME.md).

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

## Zotero-Abgleich der zitierten Literatur (`zotero-abgleich.tsv`, 16.10.2026)

Prüfmaterial, keine Entscheidung. Für jedes Werk aus [`literatur.tsv`](literatur.tsv) (76 `werk_id`) wurde in den beiden Zotero-Gruppen gesucht, ob es dort schon steht: 5043625 (Werk-Editionen) und 4876216 (Textreihen). Je Werk und Gruppe eine Zeile, zusammen 152. Der Abgleich ist lesend (nur GET auf die öffentliche API, Pause zwischen den Anfragen); es wurde nichts in Zotero angelegt oder geändert.

Spalten: `werk` (Werk und `werk_id`), `anzahl_zitate`, `klasse`, `gruppe`, `item_key` (Zotero-Schlüssel der Kandidaten, durch ` | ` getrennt, höchstens sechs), `zotero_titel`, `zotero_jahr`, `bemerkung` (warum diese Klasse).

| Klasse | Zeilen | Bedeutung |
|---|--:|---|
| `vorhanden` | 5 | genau ein Kandidat, und der Titel enthält die Titelstichwörter des Werks oder Nachname und ein Jahr aus dem Satz der Glossarstelle passen; oder mehrere Kandidaten, von denen genau einer das Jahr trägt (dann steht er zuerst) |
| `wahrscheinlich` | 40 | der Nachname kommt als Teilstring im Nachnamen eines Zotero-Eintrags vor (ohne Jahr), oder mehrere Kandidaten ohne eindeutigen Treffer, auch über Titelstichwörter bei Werken ohne Nachname (gezählt aus der Spalte `bemerkung`: 11 Zeilen „nur Nachname trifft“, 29 „N Kandidaten, nicht eindeutig“) |
| `fehlt` | 107 | kein Kandidat passt auf Nachname oder Titelstichwort; in 102 Zeilen hat die Suche gar nichts gefunden, in 5 etwas (Falke 3, Alfred Neumann 3, Steinbauer 1, Zeppezauer 48 und 1), das auf kein Kriterium passt |

5 + 40 + 107 = 152. Nach Gruppe: Werk-Editionen 5 `vorhanden`, 33 `wahrscheinlich`, 38 `fehlt` (= 76); Textreihen 0 `vorhanden`, 7 `wahrscheinlich`, 69 `fehlt` (= 76).

**Grenzen.** `wahrscheinlich` ist ein Teilstring-Treffer und kein Fund: Bech trifft Bechstein, Kern trifft Wackernagel, Klug trifft Kluge, Olt trifft Hetzbolt und Holtorf, und bei Werken ohne Nachnamen trifft ein Titelstichwort fremde Titel (dwb trifft auch das Mittelhochdeutsche Wörterbuch). Es ist kein Beleg dafür, dass es dasselbe Werk ist. Auch `vorhanden` ist eine Heuristik (Titelstichwort oder Nachname plus Jahr), keine Prüfung des Eintrags. Die Suche nutzt `qmode=titleCreatorYear` mit höchstens 50 Treffern je Anfrage; ein Werk mit anderer Schreibung des Namens fällt durch (`fehlt`). Wer eines übernimmt, schlägt den Eintrag in Zotero auf. Die Rohantworten der API liegen nicht im Repo. Erzeugt von `scripts/review/zotero-abgleich-554.py`, das beim Prüfen nicht neu gelaufen ist, weil es das Netz braucht.

## Klug-Verweise: Urteile je Lemma und Pflanzenseite (`klug-links.tsv`, `klug-urteile.tsv`, 16.10.2026)

Zu B5 in [UEBERNAHME.md](UEBERNAHME.md): für Lemmata aus [`klug-pflanzen.tsv`](klug-pflanzen.tsv) (plus ein Kontrollwert aus [`klug-abgleich.tsv`](klug-abgleich.tsv), brestelinc zu gartenerdbeere) ein Urteil, ob das Lemma zur Pflanzenseite des Portals „Pflanzen des Mittelalters“ passt. Prüfmaterial, keine Entscheidung; die Urteile sind maschinell vorbereitet und nicht von KZW geprüft.

| Datei | Inhalt | Zeilen |
|---|---|--:|
| `klug-urteile.tsv` | **Eingabe, Urteile eines Agenten:** `lemma_id`, `kennung`, `urteil`, `begruendung`, `belege_ids` (durch Leerzeichen getrennt). Die erste Zeile mit `#` ist Kopf | 28 |
| `klug-links.tsv` | **Ausgabe** aus den Urteilen: `lemma_id`, `orth`, `pflanzenseite_titel`, `kennung` (`mps:<Seitenkennung>`), `url`, `urteil`, `begruendung`, `konzepte` (Bedeutungen des Lemmas mit ihren Konzepten), `belege_ids` | 28 |

28 Paare aus Lemma und Pflanzenseite, 27 verschiedene Lemmata (`lemma_261` apfel steht mit zwei Seiten, `apfel-3` und `apfel-eine-art-von`) auf 13 verschiedene Pflanzenseiten. Urteile: `passt` 24, `passt nicht` 2 (koste, wolgemuot: beide gegen die Seite gewöhnlicher Dost), `unklar` 2 (lantwîn, wîn: gegen die Seite Echter Weinstock; gemeint ist überwiegend das Getränk, nicht die Pflanze). 24 + 2 + 2 = 28.

**Grenzen.** Ein Urteil beruht auf einer Stichprobe von Belegen: in 17 Zeilen drei, in 9 einer, in einer zwei, in einer keiner (`lemma_47136`, 0 Belege im Korpus, Urteil nur aus dem Lexikon), also nicht auf allen Belegen des Lemmas. `passt` heißt: die gelesenen Belege meinen die Pflanze, nicht dass jeder Beleg es tut. Die Seitentitel stammen von den Pflanzenseiten selbst.

**Entschieden ist die Form des Verweises, nicht die Übernahme von Daten:** Wird später ein Verweis gebaut, trägt er die Kennung der Pflanzenseite (`mps:...`), nicht die URL; die URL steht in `klug-links.tsv` nur als Prüfhilfe. Es werden keine Inhalte der Seiten übernommen (UEBERNAHME.md B5: nur Titel, URLs und unsere Zuordnungen). Festgelegt von chsteiner am 16.10.2026, festgehalten in [#554, Kommentar vom 16.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/554#issuecomment-6209772625); in diesem Lauf wird nur die Prüfliste gebaut, kein Schema und keine Anzeige. Erzeugt von `scripts/review/klug-links-554.py`. Der Schritt Urteile zu `klug-links.tsv` läuft ohne Netz (`--nur-urteile --aus <Ordner außerhalb des Repos>`; der Ordner ist Pflicht, das Ergebnis wird bewusst nach hier kopiert). Das Skript bricht ab, wenn ein Urteil nicht `passt`, `passt nicht` oder `unklar` heißt, ein Paar doppelt steht oder eine Zeile nicht vier bis fünf Felder hat; die Tabellen tragen keine CSV-Anführungszeichen, ein `"` im Text ist ein `"`. Der Abruf der Seiten (Phase 1) braucht Netz und ist beim Prüfen nicht gelaufen.
