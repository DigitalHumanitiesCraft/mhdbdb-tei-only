# Arthurische Pferde (#193): Wortlisten-Abgleich und Belegstellen-Mapping

Luise Boreks Fallstudie *Arthurische Pferde als Bedeutungsträger* (Hirzel 2023, ZfdA-Beihefte 43) hat drei hippologische Wortlisten auf TUdatalib hinterlegt. Dieser Ordner hält fest, was der Abgleich mit unserem Wortschatz ergeben hat (Baustein 2) und ob ihre Belegstellen unsere Verse treffen (Vorprüfung zu Baustein 3). Gemessen am 2026-08-08 gegen Authority Index v1.8.1.

**Attribution:** die drei Wortlisten stehen unter CC BY 4.0, `arthurianHorses.xml` unter CC0, Urheberin Luise Borek (TU Darmstadt). Zitierfähig über ihre Handles, siehe Tabellen.

## Was hier liegt

| Datei | Inhalt |
|---|---|
| `README.md` | dieser Report |
| (die Wortlisten selbst) | **bewusst nicht im Repo.** [`scripts/ingest/horses/01-wordlist-crosscheck.py`](../../scripts/ingest/horses/01-wordlist-crosscheck.py) lädt sie in Sekunden reproduzierbar über ihre Handles. Eine Kopie hier wäre eine zweite Stelle, die altern kann |

Neu erzeugen lässt sich der Report mit:

```bash
python scripts/ingest/horses/01-wordlist-crosscheck.py
python scripts/ingest/horses/01-wordlist-crosscheck.py --json   # maschinenlesbar
```

## Ergebnis in Zahlen

| Liste | Handle | Formen | eindeutig | aufgelöst | Quote |
|---|---|---|---|---|---|
| `wl-pferdetypen` | [tudatalib/2955](https://tudatalib.ulb.tu-darmstadt.de/handle/tudatalib/2955) | 312 | 278 | 211 | 76 % |
| `wl-koerperteile` | [tudatalib/2954](https://tudatalib.ulb.tu-darmstadt.de/handle/tudatalib/2954) | 33 | 33 | 32 | 97 % |
| `wl-gangarten` | [tudatalib/2953](https://tudatalib.ulb.tu-darmstadt.de/handle/tudatalib/2953) | 227 | 218 | 174 | 80 % |

Aufgelöst wird über Stufe 1 und 2 der kanonischen Kette (exakte normalisierte Form, dann Varianten-Wörterbuch). Stufe 3, der beidseitige Präfix-Fallback, bleibt draußen: er ist für die Suche gebaut und würde einen Report mit Rauschen füllen (ADR-016).

## Die Quote ist keine Fehlerquote

Das ist der wichtigste Satz dieses Reports. **Eine nicht aufgelöste Form ist kein fehlendes Lemma.** `variants.xml` ist korpus-abgeleitet: es kennt nur Schreibungen, die in unseren 667 Texten wirklich vorkommen. Boreks Listen stammen aus einem weiteren Textfeld, Wörterbücher eingeschlossen. Die 24 Prozent, die nicht auflösen, messen deshalb in erster Linie unsere Korpusabdeckung und erst in zweiter Linie unseren Wortschatz.

Belegt an den Zahlen: von den 67 nicht aufgelösten Pferdebezeichnungen tragen **34 ein bekanntes Grundwort in sich**, ganz überwiegend `-ros` und `-pfert`:

```
beteros (ros)      blancros (ros)     blasros (ros)      bleichros (ros)
hantros (ros)      reitros (ros)      satelros (ros)     soumros (ros)
sperros (ros)      stechros (ros)     stuotros (stuot)   swarzros (ros)
frouwenpfert (pfert)   soumerpfert (pfert)   rösselîn (roessel)   zelterle (zelter)
```

Das Grundwort ist also da, nur diese eine Zusammensetzung ist bei uns nicht belegt. Determinativkomposita sind genau das Thema von #239 (Wortbestandteil-Suche im Lemmata-Explorer), und diese Liste ist ein brauchbarer Prüfdatensatz dafür.

Gegenprobe an den Grundwörtern selbst: `ros`, `phert`, `vole`, `zelter`, `stuot`, `schenkel`, `hurt`, `draben` lösen alle auf. Von den geprüften fehlen nur `wallach` und `merhe` wirklich.

Ein Detail derselben Art: Borek markiert 12 Formen in `wl-gangarten` mit einem Stern (`hurt*`, `rîten*`, `jagen*` und weitere). Der Stern ist Notation, nicht Wortbestand. Ungestrippt scheitern alle zwölf an der Auflösung und erschienen als Lücke; gestrippt lösen **alle zwölf** auf. Das Skript entfernt ihn deshalb vor der Auflösung und weist die betroffenen Formen aus.

## Was tatsächlich an Arbeit anfällt

Zwei Klassen, und sie führen zu verschiedenen Leuten.

### 1. Klassifikation prüfen: 20 Fälle

Das Lemma ist da und richtig getroffen, aber es trägt kein einschlägiges Konzept. Kandidaten für eine Nachklassifikation, keine gesicherten Befunde.

| Liste | Anzahl | Beispiele |
|---|---|---|
| `wl-pferdetypen` | 5 | `gorre` → `lemma_20760` (nur Politische Einheiten/Namen), `stûde` → `lemma_5834` |
| `wl-koerperteile` | 5 | `lenden` → `lemma_3702`, `brüsten` → `lemma_15400`, `gebeine` → `lemma_1958` (führt nur Körperteile **von Menschen**) |
| `wl-gangarten` | 10 | `hanc` → `lemma_2636` (nur Landschaft), `tokzelen` → `lemma_6136`, `schreit` → `lemma_32548` |

Die Körperteil-Fälle sind der klarste Block: unser Begriffssystem trennt `concept_21030000` (Körper von Menschen) und `concept_14011100` (Körper von Säugetieren), und mehrere Lemmata hängen nur an der menschlichen Seite, obwohl sie in Boreks Belegen Pferdekörper bezeichnen.

### 2. Zuordnung verdächtig: 25 Fälle

Hier ist die Form über das Varianten-Wörterbuch gelaufen, das Lemma lautet aber völlig anders. Das heißt: irgendwo im Korpus trägt ein `<w>` mit dieser Schreibung dieses Lemma. Die wahrscheinlichere Erklärung ist eine **Fehlannotation im Korpus**, nicht eine Klassifikationslücke.

| Form | löst auf | Lemma bedeutet |
|---|---|---|
| `hors` | `lemma_2590` | `hâr` (Haar) |
| `perd` | `lemma_43808` | `bærde` |
| `pert` | `lemma_542` | `bern` |
| `roes`, `roßen`, `röslîn` | `lemma_4951` | `rôse` (die Blume) |
| `röss` | `lemma_18728` | `resch` |
| `stût` | `lemma_5710` | `stân` |
| `vül`, `vüle` | `lemma_24577`, `lemma_6356` | `vollen`, `übel` |
| `rassen` | `lemma_33621` | `Râzen` (Volksname) |
| `hossen` | `lemma_2909` | `hose` |
| `gestracte` | `lemma_5824` | `stricken` |

Jeder dieser Fälle ist ein Verdacht und kein Befund: die Schreibung kann in ihrem Kontext tatsächlich das genannte Lemma meinen. Zu prüfen ist sie an der Belegstelle, nicht an dieser Liste.

## Was ausdrücklich kein Befund ist

**Homographen, die über einen Zwilling schon erfasst sind: 4 Fälle.** `ros` trifft zwei Lemmata, das Pferd und ein lateinisches Wetterwort; `bûch` trifft den Bauch und ein Lemma unter „Waffen". Solange ein Partner richtig klassifiziert ist, ist die Form abgedeckt, und den anderen nachzuklassifizieren wäre falsch. Der Report weist sie getrennt aus, damit niemand sie abarbeitet.

**Die Grundwort-Heuristik irrt sich gelegentlich.** Sie sucht die längste bekannte Form, die als Zeichenkette in der unaufgelösten steckt, ohne jede Morphologie. `schënkel (kel)` ist so ein Fehltreffer. Sie taugt, um die `-ros`-Bildungen sichtbar zu machen, nicht als Beleg im Einzelfall.

## Woher die Daten kommen

Download über die DSpace-REST-API von TUdatalib, mit festen Bitstream-UUIDs im Skript. Die Listen sind ISO-8859-1 kodiert, das Skript dekodiert entsprechend. Sie tragen keine Kopfzeile und keine Kommentare, eine Form je Zeile.

## Baustein 3, Vorprüfung: treffen Boreks Belegstellen unsere Verse?

Das ist die Frage, an der das Explorer-Feature hängt, und sie ist vor jeder UI-Entscheidung zu beantworten. `arthurianHorses.xml` ([tudatalib/3695](https://tudatalib.ulb.tu-darmstadt.de/handle/tudatalib/3695), CC0) zitiert 346 Verse aus fünf Werken, alle fünf liegen im Korpus: `WH`, `PZ`, `ER`, `IW`, `TR`.

Erzeugen lässt sich die Messung mit [`scripts/ingest/horses/02-map-citations.py`](../../scripts/ingest/horses/02-map-citations.py).

### Die Stellenangabe steckt nicht dort, wo das Ticket sie vermutet

Unsere `<l>`-Elemente tragen **kein** `xml:id`, sondern nur ein fortlaufendes `@n`. Die zitierbare Stellenangabe steckt in den `xml:id` der **Wörter**, und zwar in drei Varianten:

| Werk | Zählweise | Boreks Angabe | unsere ID |
|---|---|---|---|
| `WH`, `PZ` | Dreißiger | `339,24` | `PZ_33924_*` (Abschnitt × 100 + Vers) |
| `ER` | Vers × 100 | `4714` | `ER_471400_*` |
| `ER` | Sonderzählung | `4629,18` | `ER_462918_*` |
| `IW`, `TR` | fortlaufend | `1108` | `IW_1108_*` |

Die Erec-Sonderzählung ist kein Sonderfall unserer Daten, sondern die übliche Zählung des Einschubs nach Vers 4629. Unsere IDs bilden sie ab: `ER_462901` bis `ER_462957` existieren, alle 57 Verse des Einschubs. Im gerenderten Text stehen sie allerdings nicht als eigene Zeilen, der Einschub liegt vollständig als `<supplied>` in einem einzigen `<l n="4629">`.

### Ergebnis

Die 346 Stellenangaben entfallen auf **336 Verse**: zehn werden von zwei Pferden zitiert, vier davon mit abweichendem Wortlaut. Bewertet wird pro Vers die beste Fassung.

| Werk | Verse | Versatz 0 | Versatz | fern | ohne Entsprechung |
|---|---|---|---|---|---|
| `WH` | 97 | 97 | | | |
| `PZ` | 184 | 177 | 5 × (+2) | 2 | |
| `ER` | 14 | 13 | | 1 | |
| `IW` | 23 | 23 | | | |
| `TR` | 18 | 18 | | | |

**328 von 336 Versen sitzen exakt, 98 Prozent. Alle 336 sind textlich aufgelöst, keiner bleibt offen.**

### Warum die Trefferquote allein nichts beweist

Dass eine ID existiert, heißt nicht, dass sie auf den zitierten Vers zeigt. Der erste Durchlauf meldete 346 von 346 und sah nach einem glatten Ergebnis aus. Erst der Vergleich des **Wortlauts** zeigte, dass im Parzival fünf aufeinanderfolgende Verse (339,24 bis 339,28) genau zwei Verse tiefer stehen: Boreks 339,24 („dô hiez er gürten balde") liegt bei uns unter 339,26. Vier der fünf stimmen im Wortlaut vollständig überein, es ist also derselbe Text unter anderer Nummer, lokal und nicht systematisch.

### Warum das Vergleichsmaß zweimal gemessen wurde

Die erste Fassung verglich normalisierte **Wortmengen** und meldete neun Verse ohne Entsprechung. Sechs davon waren derselbe Vers in anderer Schreibung: „unt hetz Lehelîn genomn" gegen „und hetez lehelîn genomen", „ans grâles" gegen „an sgrâles". Das Maß scheiterte an Orthographie und Worttrennung, nicht an Textidentität, und erzeugte damit genau die Zweifelsfälle, die es finden sollte. Verglichen wird jetzt die MHD-normalisierte Buchstabenkette ohne Trennungen (`difflib`). Die Schwelle 0.75 liegt in einer leeren Zone: schwächste akzeptierte Entsprechung 0.84, stärkster verworfener Treffer 0.42.

### Warum der Suchumkreis zweimal gemessen wurde

Übrig blieben zunächst drei Verse. Der Umkreis von vier war zu eng gedacht: ein Versatz kann über die Grenze des Dreißigers gehen, und eine falsche Ziffer springt beliebig weit. Werkweit gesucht lösen sich alle drei eindeutig auf.

| Boreks Angabe | steht bei uns | Übereinstimmung | zweitbester Treffer |
|---|---|---|---|
| `Pz. 604,18` | `PZ_60318` | 1.00 | 0.68 |
| `Pz. 604,19` | `PZ_60319` | 0.95 | 0.62 |
| `Er. 4118` | `ER_471800` | 1.00 | 0.62 |

Die beiden Parzival-Stellen liegen also einen ganzen Dreißiger höher, bei uns unter 603. Boreks `4118` ist textlich als **4718** bestätigt und damit ein Zahlendreher in ihrer Datei, kein Editionsunterschied. Übernommen wird ein solcher Ferntreffer nur, wenn er eindeutig ist (mindestens 0.15 Vorsprung vor dem zweitbesten): ohne diese Bedingung fände die Suche im Versepos irgendeine Formelzeile.

### Welche Ausgabe eigentlich?

Unser Parzival folgt Leitzmann, ATB 12, 7. Auflage 1961, unser Erec Leitzmann/Wolff, ATB 39, 3. Auflage 1963. **Borek nennt keine Ausgabe**: ihr `sourceDesc` führt nur die GND des Werks, keinen Herausgeber, kein Jahr. Der Versatz ist damit kein Fehler auf einer der beiden Seiten, sondern die Differenz zwischen einer benannten und einer unbenannten Textgrundlage. Das ist der Grund, warum Boreks Angabe im Index erhalten bleiben muss und nicht stillschweigend auf unsere Zählung umgerechnet werden darf: nachprüfbar ist nur der Wortlaut, nicht die Verszahl.

### Was das für Baustein 3 heißt

Datenseitig ist das Feature machbar, und der Anschluss ans Korpus ist besser als erwartet. Was noch fehlt, ist die inhaltliche Ebene: 24 `<horse>`-Elemente (10 Deklarationen plus 14 Vorkommen), 52 `<horseName>` mit ihren Schreibvarianten, 49 `<event type="intro|combat|care|loss|...">`, 22 `<trait type="color|quality|marking">`, 32 `<object>` und 48 `<person>` mit Besitzer- und Reiterrollen.

Wie ein Beleg gespeichert wird, ist am 08.08.2026 entschieden: **beides**, Boreks Zitation wörtlich und unser aufgelöstes Ziel, dazu die gemessene Übereinstimmung. Für acht der 336 Verse fallen die beiden Angaben auseinander, und weil Borek keine Ausgabe nennt, ist die Differenz dokumentierbar, aber nicht auflösbar.

## Anschluss

- **Baustein 1** (Authority-Korrektur) ist erledigt, siehe `fc1e88cce` und #357
- **Baustein 3** (Playground-Explorer „Arthurische Pferde") ist unberührt
- Die Kandidatenlisten oben brauchen eine philologische Durchsicht, bevor daraus Änderungen werden
