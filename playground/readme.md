# MHDBDB Playground

## Kontext

**Problem:** Mediävist:innen haben kein flexibles, exploratives Tool, um ihre TEI-Textkorpora und Authority Files interaktiv zu analysieren.

**Vision:** Ein "SQL Workbench für TEI" – Desktop-Browser-basierte Analyse-Engine, die Forscher:innen ermöglicht, **alle erdenklichen Fragen** an ihre MHDBDB-Daten zu stellen.

## Domäne: Mittelhochdeutsche Begriffsdatenbank (MHDBDB)

**Was sind MHDBDB-Daten?**

- **TEI-XML Texte:** Mittelhochdeutsche Literatur mit mehreren Annotationsniveaus
- **6 Authority Files:** persons, lexicon, concepts, genres, works, names
- **Semantische Verknüpfungen:** Cross-References zwischen allen Dateien

**Typische Forschungsfragen:**

- _"Welche Konzepte sind mit 'vriunt' (Freund) verknüpft?"_
- _"Alle Werke von Hartmann von Aue in Gattung 'Höfischer Roman'"_
- _"Zeige Textstellen mit Lemma X in semantischem Kontext Y"_
- _"Wie oft erscheint Person Z in verschiedenen Werken?"_
- _"Wie viele neue Lemmata kommen im 'Parzival' oder bei Konrad von Würzburg vor, die nur dort belegt sind?"_
- _"Gibt es semantische Cluster rund um den Begriff 'ere' über verschiedene Werke hinweg?"_
- _"Welche Tokens stehen im Umkreis von 'vriunt' (Kookurrenzen)?"_
- _"Wie sieht das Named-Entity-Netzwerk eines kurzen höfischen Romans aus?"_
- _"Welche Eigenheiten hat mein Dissertationskorpus, bestehend aus 'Erec', 'Iwein' und 'Parzival' im Vergleich zum Gesamtbestand?"_


**Zielgruppe:** MHDBDB-Kernteam, externe germanistische und mediävistische Forscher:innen, Promovierende, Editionseditor:innen

**Offene Probleme**

- kein Standard-Interface für XPath-Queries auf lokal gehostete TEI-Korpora
- Komplexität von TEI-Strukturen erschwert Einstieg, wenn keine Vorkenntnisse vorhanden sind
- Visualisierungen (z. B. Begriffsverteilung, Named Entities) fehlen in vielen TEI-Tools
- Kein gemeinsames Tool für Editionsarbeit, Query-Prototyping und Datenreview

## Ziel des Playground

- Interne Testumgebung für MHDBDB 4.0-Komponenten
- Einstiegstor für externe Power-User:innen
- Technologisches Labor für neue Analyse-Features
- Plattform für die kollaborative Weiterentwicklung der MHDBDB-Datenmodelle






