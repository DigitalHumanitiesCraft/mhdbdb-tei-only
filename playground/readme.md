# MHDBDB Playground

## WARUM? (Motivation & Kontext)

**Problem:** Mediävisten haben keine flexible, explorative Tool um ihre TEI-Textkorpora und Authority Files interaktiv zu analysieren.

**Vision:** Ein "SQL Workbench für TEI" – Desktop-Browser-basierte Analyse-Engine, die Forschern ermöglicht, **alle erdenklichen Fragen** an ihre MHDBDB-Daten zu stellen.

## Domäne: Mittelhochdeutsche Begriffsdatenbank (MHDBDB)

**Was sind MHDBDB-Daten?**
- **TEI-XML Texte:** Mittelhochdeutsche Literatur mit linguistischen Annotationen
- **6 Authority Files:** persons, lexicon, concepts, genres, works, names
- **Semantische Verknüpfungen:** Cross-References zwischen allen Dateien
- **50+ Jahre Forschungsdaten** der Universität Salzburg

**Typische Forschungsfragen:**
- *"Welche Konzepte sind mit 'vriunt' (Freund) verknüpft?"*
- *"Alle Werke von Hartmann von Aue in Gattung 'Höfischer Roman'"*
- *"Zeige Textstellen mit Lemma X in semantischem Kontext Y"*
- *"Wie oft erscheint Person Z in verschiedenen Werken?"*

**Zielgruppe:** Germanistische Forscher, Mediävisten (Desktop-Arbeitsplätze)

**Offene Probleme**

```
<entry xml:id="lemma_11151">
          <form type="lemma">
            <orth>d'habe</orth>
          </form>
          <gramGrp>
            <pos>NOM</pos>
          </gramGrp>
          <sense xml:id="lemma_11151_sense_87111">
            <ptr target="concepts.xml#concept_21072000"/>
            <ptr target="concepts.xml#concept_23307210"/>
            <ptr target="concepts.xml#concept_23304300"/>
            <ptr target="concepts.xml#concept_23308000"/>
            <ptr target="concepts.xml#concept_31200000"/>
            <ptr target="concepts.xml#concept_23304100"/>
          </sense>
          <sense xml:id="lemma_11151_sense_87112">
            <ptr target="concepts.xml#concept_21072000"/>
            <ptr target="concepts.xml#concept_23307210"/>
            <ptr target="concepts.xml#concept_23304300"/>
            <ptr target="concepts.xml#concept_23308000"/>
            <ptr target="concepts.xml#concept_31200000"/>
            <ptr target="concepts.xml#concept_23304100"/>
          </sense>
          <sense xml:id="lemma_11151_sense_87113">
            <ptr target="concepts.xml#concept_21072000"/>
            <ptr target="concepts.xml#concept_23307210"/>
            <ptr target="concepts.xml#concept_23304300"/>
            <ptr target="concepts.xml#concept_23308000"/>
            <ptr target="concepts.xml#concept_31200000"/>
            <ptr target="concepts.xml#concept_23304100"/>
          </sense>
```
wieso immer wieder gleicher "koffer"?
