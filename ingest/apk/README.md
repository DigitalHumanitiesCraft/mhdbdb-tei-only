# Hesler-Apokalypse (APK) zur Ansicht (#262)

Die Apokalypse Heinrichs von Hesler in der Fassung des Mittelhochdeutschen Textarchivs (MHGTA, heute im Textarchiv des MWB unter `HeslApk`), umgesetzt in das TEI der MHDBDB und maschinell annotiert. **Das ist ein Entwurf zur Ansicht, nicht Teil des Korpus.** Nichts davon steht in `tei/` oder in den Normdaten, nichts ist auf der Website zu sehen. Aufgenommen wird der Text erst, wenn das MWB in Trier (Ute Recker-Hamm) zugestimmt hat.

## Was hier liegt

| Datei | Inhalt |
|---|---|
| `APK.tei.xml` | der ganze Text, 23.254 Verse in 415 Abschnitten, mit den Seiten der Ausgabe Helm (1907) und den Blatt- und Spaltenangaben der Danziger Handschrift; jedes Wort mit Lemma, Wortart und Bedeutung, soweit sie gesetzt werden konnten |
| `normdaten-vorschlag.md` | Vorschlag für den Werkeintrag und für Heinrich von Hesler als Person, mit GND, Wikidata und Handschriftencensus |
| `pruefung/` | Prüfpaket für die maschinellen Zuweisungen (Anleitung in `pruefung/README.md`) |
| `phase1/` bis `phase3/` | die Entscheidungstabellen von Lemma, Wortart und Bedeutung, Grundlage für einen Nachlauf |

Wie die Vorlage abgebildet ist und warum, steht in `scripts/ingest/apk/README.md`. Die Vorlage `apk_free.xml` selbst liegt nicht im Repository.

## Stand

| Angabe | Wörter mit Angabe | Anteil |
|---|---|---|
| Lemma (`@lemmaRef`) | 110.241 | 95,4 % |
| Wortart (`@pos`) | 94.675 | 81,9 % |
| Bedeutung (`@ana`) | 100.585 | 87,0 % |
| Variantentyp (`@corresp`) | 59.057 | 51,1 % |

Bezugsgröße sind die 115.566 Wörter im Text ohne die Rubrik am Anfang. Die Zahlen gibt `python -P -E scripts/ingest/apk/21-abdeckung.py` aus.

- **Lemma:** Ohne Lemma sind 4.786 Wörter, deren Schreibung das Lexikon nicht kennt (oft ostmitteldeutsche Formen, Liste in `phase1/lemma-unmatched.tsv`). Dazu kommen 207, bei denen kein Vorschlag des Lexikons passte, und 332 Formen, die nur einmal vorkommen und mehrdeutig sind.
- **Wortart und Bedeutung:** 13.925 Wörter (Wortart) und 9.014 Wörter (Bedeutung) gehören zu Schreibungen, die im Text unterschiedlich gebraucht werden. Sie müssten einzeln entschieden werden; das ist noch nicht geschehen.
- **Variantentyp:** Er wird nur gesetzt, wenn das Variantenverzeichnis für Schreibung und Bedeutung genau einen Typ kennt. Bei 32.516 Wörtern kennt es mehrere, bei 9.012 keinen (`18-corresp.py`).

Neue Lemmata oder Bedeutungen sind nicht angelegt worden.

## Offen

- **Zustimmung des MWB Trier** zur Aufnahme (über KZW, #262).
- **Normdaten:** Werk, Person und Gattung stehen im Header als Platzhalter `TBD`. Die Gattung (Bibeldichtung oder zusätzlich Exegetischer Text) entscheidet KZW, Vorschlag in `normdaten-vorschlag.md`.
- **Prüfung der maschinellen Zuweisungen** über `pruefung/`.
- **Fragen zur Abbildung** der Vorlage (Kursive, drei abweichende Trennungen, Korrekturen der Ausgabe): `scripts/ingest/apk/README.md`, Abschnitt „Offene Fragen an die Fachseite“.
