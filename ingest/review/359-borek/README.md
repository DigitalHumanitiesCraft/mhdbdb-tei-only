# #359: Prüfseite zu Boreks Pferdewortlisten

Das Material zur kuratorischen Prüfseite für #359, erzeugt am 21.09.2026 gegen
Korpus-Index 4.2.17 und Authority-Index 1.9.7.

## Was hier liegt

| Datei | Art | Inhalt |
|---|---|---|
| `359-pruefseite.html` | erzeugt | **Die Prüfseite.** Eine einzelne Datei, die man verschickt und ohne Installation im Browser öffnet |
| `crosscheck.json` | erzeugt | Der Abgleichsbericht aus `scripts/ingest/horses/01-wordlist-crosscheck.py --json`, die Herkunft der 45 Fälle |
| `evidence.json` | gemessen | Die Belegstellen mit Kontext, aus dem Korpus geholt |
| `vorschlaege.json` | von Hand | Die Bewertungen, geschrieben nach dem Lesen der Belege |
| `folgebefunde.md` | von Hand | Drei Befunde, die nicht zu #359 gehören und eigene Vorgänge brauchen |

## Wie die Seite neu entsteht

```bash
python scripts/ingest/horses/01-wordlist-crosscheck.py --json > ingest/review/359-borek/crosscheck.json
python scripts/review/collect-359-evidence.py --write
python scripts/review/build-359-page.py
```

Der erste Schritt lädt Boreks Wortlisten von TUdatalib und gleicht sie gegen
den Authority-Index ab. Der zweite liest alle 667 TEI-Dateien und holt die
Belegstellen. Der dritte setzt Belege und Bewertungen zur Seite zusammen.

`python scripts/review/build-359-page.py --pruefen` gleicht nur ab und schreibt
nichts. Das ist der schnelle Weg, wenn nur eine Bewertung geändert wurde.

## Was der Generator nicht durchgehen lässt

Der Abgleich zwischen `evidence.json` und `vorschlaege.json` ist streng und
bricht ab bei:

- einem gemessenen Fall ohne Bewertung oder einer Bewertung ohne Fall,
- einer Fundstelle in einer Begründung, die unter den gemessenen Belegen nicht
  vorkommt,
- einem Vorschlag ohne tragenden Beleg,
- **einem Zitat in einer Begründung, das so in keinem Beleg steht.**

Der letzte Punkt hat sich verdient: beim Ziehen der Umlaute in
`vorschlaege.json` sind drei mittelhochdeutsche Zitate mitgezogen worden
(`wandels bloss` zu `wandels bloß`, `tugent gross` zu `tugent groß`,
`unde fuer` zu `unde für`). Im fertigen HTML sah das richtig aus, und der Beleg
darüber las jedes Mal anders als das Zitat darunter. Wer ein Zitat schreibt,
das absichtlich kein Korpusbeleg ist, trägt es im Fall unter `zitate_frei` ein.

## Wenn KZW eine Bewertung geändert haben will

`vorschlaege.json` bearbeiten und den Generator erneut laufen lassen. Die
Belege müssen dafür nicht neu gesammelt werden. Wer Python nicht anfassen will,
ändert nur diese eine Datei: der Text der Karten steht vollständig darin.

## Woher die Fallmenge kommt

45 Zeilen des Abgleichsberichts: 25 verdächtige Zuordnungen, 15
Klassifikationskandidaten und 5 Körperteil-Zeilen. KZW hat am 16.09.2026 die
ersten 40 in die Seite bestellt; die fünf Körperteile sind dazugekommen, weil
ihre Entscheidung vom selben Tag eine Messung an den Belegen verlangt und die
hier steht.

**Eine Zeile ist ein Paar aus Schreibung und Lemma, nicht ein Lemma.** Die 25
verdächtigen Zuordnungen sind 25 Schreibungen auf 22 Lemmata, die 5
Körperteil-Zeilen sind 4 Lemmata. Eine Summe über die Zeilen zählt mehrfach.

## Attribution

Boreks drei Wortlisten stehen unter CC BY 4.0, Urheberin Luise Borek
(TU Darmstadt), [tudatalib/2953](https://tudatalib.ulb.tu-darmstadt.de/handle/tudatalib/2953),
[2954](https://tudatalib.ulb.tu-darmstadt.de/handle/tudatalib/2954),
[2955](https://tudatalib.ulb.tu-darmstadt.de/handle/tudatalib/2955). Die Listen
selbst liegen bewusst nicht im Repositorium, das Crosscheck-Skript lädt sie
über ihre Handles.
