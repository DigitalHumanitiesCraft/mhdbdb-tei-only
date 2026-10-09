# Textreihentypologie (Unterseite)

Die Unterseite führt die bisherige Website der MHDBDB-Textreihentypologie
(`https://www.marketext.at/Textreihentypologie/`) in die MHDBDB ein (#93). Sie
liegt unter `https://dhcraft.org/mhdbdb-tei-only/textreihen/` und ist über den
Footer-Link "Textreihentypologie" und die Kachel auf der Hilfe-Übersicht
erreichbar.

## Datengrundlage

Das Vokabular ist der ursprüngliche SKOS-Datensatz von
[Middle-High-German-Conceptual-Database/textseries](https://github.com/Middle-High-German-Conceptual-Database/textseries),
**Commit `86c233f0803b6bf1dfd0db7913d086f00b8eb92b`** (12.06.2023, "Update README.md").
Die drei Datendateien stammen aus `d093fe815` (12.06.2023, "Add files via upload").

| Datei in `data/skos/` | Git-Blob-SHA-1 (stimmt mit dem Commit überein) |
|---|---|
| `MHDBDB-Textreihentypologie.ttl` | `8d7f05fc5c2d69db446ddf345a518a507ac3cf35` |
| `MHDBDB-Textreihentypologie.rdf` | `c14784d5e1c257e6bab3b251d0c52862b53aceca` |
| `MHDBDB-Textreihentypologie.rj` | `755772bdbb0d14c5a51834fdda68efc0a0cd8e14` |
| `README-textseries-repo.md` (dort `README.md`) | `85b10768ad51f709ed95e1067ae43a91c427263a` |

Nachprüfen: `git hash-object textreihen/data/skos/<datei>` muss den Wert der Tabelle
liefern. **Diese vier Dateien werden nicht bearbeitet.** Ein neuer Stand wird als
neuer Commit des Quellrepositoriums übernommen, mit neuer Tabelle.

Inhalt, gemessen am `.rj`: 618 Konzepte (`skos:Concept`), 894 `skos:broader`-Aussagen
(die Zeilenzahl der Turtle-Datei, 881, ist niedriger, weil einzelne Zeilen mehrere
Ziele tragen), drei oberste Kategorien (Epik, Lyrik und Dramatik; Wissensliteratur
und Gebrauchsliteratur; Mediale Sonderformen), 193 Konzepte mit mehreren direkten
Eltern, 4 als veraltet markierte Konzepte (`owl:deprecated`), 16 `skos:editorialNote`-Aussagen
(an acht Konzepten).

## Lizenz und Zitation

CC BY 4.0, so in der README des Quellrepositoriums (Abschnitt "Licence"). Dieselben
Daten und die zugehörige Bibliografie, Tabellen und das Poster liegen mit CC BY 4.0 im
Forschungsdatenrepositorium der Universität Hamburg
(DOI `10.25592/uhhfdm.12414`, `.12416`, `.12418`, `.13381`). Die README des Repositoriums
bittet um Zitation der Referenzpublikation: Katharina Zeppezauer-Wachauer und Marco
Heiles, unter Mitarbeit von Julia Höpfner und Leonie Weiß: Eine digitale Textreihentypologie
für deutschsprachige Texte des Mittelalters und der Frühen Neuzeit. Showcase eines
kontrollierten Vokabulars in SKOS, in: Mittelalter 6 (2023), S. 6-39,
<https://doi.org/10.26012/mittelalter-30680>.

Auf der alten Website selbst steht keine Lizenz- oder Nutzungsbedingung. Die Rechtslage
je Bestandteil steht im PR zu #93.

## Dieser Datenstand ist nicht `genres.xml`

Die MHDBDB führt die Typologie inzwischen in `authority-files/genres.xml` als
eigenständig gepflegten TEI-Datenstand. Mehrfacheinordnungen bleiben dort möglich; die
Datenstände sind nicht identisch. Ein Abgleich war ausdrücklich nicht Teil des Umzugs
(@wachauer in #93, 08.10.2026). Die Unterseite "Gattungs-Explorer in MHDBDB Next"
erklärt das und verlinkt auf den aktuellen Gattungs-Explorer.

## Historische URIs

Alle Konzept-URIs beginnen mit `https://dhplus.sbg.ac.at/mhdbdb/instance/`. Die Domain
löst nicht mehr auf (gemessen 09.10.2026, kein DNS-Eintrag). Die URIs bleiben als
Bezeichner erhalten, werden nie als Link gesetzt, und keine Seite ruft sie auf. Als
Referenz dient die ID (`c_` plus acht Hexstellen).

## Abgeleitete Dateien und ihre Skripte

| Datei | Erzeugt von | Prüfung |
|---|---|---|
| `data/textreihen.json` (SKOS-Browser) | `python scripts/build-textreihen.py` aus `data/skos/*.rj` | `--check` |
| `bibliography.html`, Abschnitt zwischen `BIB:START` und `BIB:END` | `python scripts/build-textreihen-bibliography.py` aus der Zotero-Gruppe 4876216 | `--check` (offline, gegen `data/zotero-schnappschuss.json`) |

Die Bibliografie bleibt aktuell, indem jemand das Skript ohne `--offline` laufen lässt:
es holt die Haupteinträge der öffentlichen Zotero-Gruppe neu (190 am 09.10.2026; die 205
Items der API sind 190 Einträge, 12 Anhänge und 3 Notizen) und schreibt Schnappschuss und
Seite neu. Ein Hintergrundabruf im Browser gibt es nicht.

## Was nicht übernommen ist, und warum

Bis KZW geantwortet hat, ob die Bestandteile frei übernommen werden dürfen (Anfrage in
#93), fehlen:

- die sieben Logos im Fuß der alten Website (MHDBDB, Offenes Mittelalter, CLARIAH-AT, CSMC,
  UWA Cluster of Excellence, Universität Hamburg, DFG); der Förderhinweis steht als Text auf
  der Startseite (nach der README des Quellrepositoriums, mit beiden Projektnummern);
- das Startbild (Royal MS 6 E VI, f 329r);
- drei Screenshots der MHDBDB-Oberfläche vom 17.05.2023 auf "Use cases".

An den Stellen stehen HTML-Kommentare im Quelltext (`Bild ... nicht übernommen`, auf der
Startseite ein Sammelkommentar). Die Dateien lassen sich von der alten Website laden:
`https://www.marketext.at/Textreihentypologie/wp-content/uploads/2023/...`.

Übernommen sind die erkennbar eigenen Abbildungen: die Tabellenausschnitte zu Hausbuch
und Reinmar-Korpus, die Grafik der bibliografischen Metadaten, die beiden SKOS-Play-
Beispielabbildungen und das Poster (Vorschau in `img/`, Volldatei über die DOI).

## Korrigierte Fehler der alten Website

- Der Link "Use case 1: Mittelhochdeutsche Begriffsdatenbank" zeigte auf `dokument.html#MHDBDB`,
  eine Seite, die es nicht gibt; er führt jetzt auf den Anker derselben Seite.
- "Kopie der Tabelle im Forschungsdatenrepositorium: #DOI (wird nachgeliefert)" ist durch die
  DOI `10.25592/uhhfdm.12418` aus der Outreach-Seite ersetzt.
- Die Zeile "Bitte die Links der Visualisierungen noch nicht anklicken. Die URIs funktionieren
  derzeit noch nicht" auf "Visualization & Browser" entfällt: der neue Browser verlinkt keine URI.
- Typografische Anführungszeichen sind auf das gerade `"` gesetzt (Konvention der Site).

## Dateien

```
textreihen/
├── index.html … poster.html     # 11 Seiten (Start, About, How To, Browser, Use cases, Outreach,
│                                #   Bibliography, Download, Gattungs-Explorer, 2 Beiträge)
├── textreihen.css / .js         # Stil und SKOS-Browser
├── bibliografie.js              # Literatursuche über die statische Bibliografie
├── img/                         # übernommene eigene Abbildungen
└── data/
    ├── skos/                    # Quelle, unverändert (siehe oben)
    ├── textreihen.json          # abgeleitet für den Browser
    └── zotero-schnappschuss.json
```
