# MHDBDB Migration: SPARQL Queries Overview

## 1. Persons Query

**Purpose**: Extracts author/person data with identifiers and associated works

```sparql
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dhpluso: <https://dh.plus.ac.at/ontology#>
PREFIX dhplusv: <https://dh.plus.ac.at/vocabulary/>
PREFIX mhdbdbi: <https://dh.plus.ac.at/mhdbdb/instance/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX gnd: <https://d-nb.info/gnd/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?personId ?preferredName 
                (SAMPLE(?labelDe) AS ?labelDe) 
                (SAMPLE(?labelEn) AS ?labelEn) 
                ?gndId ?wikidataId
                (MAX(?creationDate) AS ?latestDate)
                (GROUP_CONCAT(DISTINCT ?workId; SEPARATOR=",") AS ?associatedWorks)
WHERE {
  # Person basic data
  ?personURI a dhpluso:Person .
  
  # Extract the ID from the URI
  BIND(REPLACE(STR(?personURI), "^.*/", "") AS ?personId)
  
  # Preferred name if available
  OPTIONAL {
    ?personURI dhpluso:preferredNameEntityForThePerson ?nameNode .
    ?nameNode rdfs:label ?preferredName .
  }
  
  # Language-specific labels
  OPTIONAL { ?personURI rdfs:label ?labelDe . FILTER(LANG(?labelDe) = "de") }
  OPTIONAL { ?personURI rdfs:label ?labelEn . FILTER(LANG(?labelEn) = "en") }
  
  # External identifiers
  OPTIONAL { 
    ?personURI owl:sameAs ?gnd . 
    FILTER(STRSTARTS(STR(?gnd), "https://d-nb.info/gnd/"))
    BIND(REPLACE(STR(?gnd), "^https://d-nb.info/gnd/", "") AS ?gndId)
  }
  OPTIONAL { 
    ?personURI owl:sameAs ?wikidata . 
    FILTER(STRSTARTS(STR(?wikidata), "http://www.wikidata.org/entity/"))
    BIND(REPLACE(STR(?wikidata), "^http://www.wikidata.org/entity/", "") AS ?wikidataId)
  }
  
  # Creation metadata
  OPTIONAL { ?personURI dcterms:created ?creationDate }
  
  # Find associated works
  OPTIONAL {
    ?workURI dhpluso:contribution ?contribution .
    ?contribution dhpluso:agent ?personURI ;
                  dhpluso:role <http://id.loc.gov/vocabulary/relators/aut> .
    BIND(REPLACE(STR(?workURI), "^.*/", "") AS ?workId)
  }
}
GROUP BY ?personId ?preferredName ?gndId ?wikidataId
ORDER BY ?personId
```

## 2. Lemmas Query

**Purpose**: Extracts dictionary entries with part of speech and references to senses/concepts

```sparql
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dhpluso: <https://dh.plus.ac.at/ontology#>
PREFIX dhplusv: <https://dh.plus.ac.at/vocabulary/>
PREFIX mhdbdbi: <https://dh.plus.ac.at/mhdbdb/instance/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?lemmaId ?writtenRep ?partOfSpeech 
       (GROUP_CONCAT(DISTINCT ?senseId; SEPARATOR=",") AS ?senses)
       (GROUP_CONCAT(DISTINCT ?conceptId; SEPARATOR=",") AS ?relatedConcepts)
       ?creationDate
WHERE {
  # Get word entities
  ?wordURI a dhpluso:Word ;
           dhpluso:canonicalForm ?formURI .
  
  # Extract the word ID
  BIND(REPLACE(STR(?wordURI), "^.*/word_", "") AS ?lemmaId)
  
  # Get the written representation
  ?formURI dhpluso:writtenRep ?writtenRep .
  
  # Get part of speech if available
  OPTIONAL { 
    ?wordURI dhpluso:partOfSpeech ?posURI .
    BIND(REPLACE(STR(?posURI), "^.*/", "") AS ?partOfSpeech)
  }
  
  # Get creation date
  OPTIONAL { ?wordURI dcterms:created ?creationDate }
  
  # Get associated senses and their concepts
  OPTIONAL {
    ?wordURI dhpluso:sense ?senseList .
    ?senseList rdf:rest*/rdf:first ?senseURI .
    BIND(REPLACE(STR(?senseURI), "^.*/sense_", "") AS ?senseId)
    
    # Get concepts associated with each sense
    OPTIONAL {
      ?senseURI dhpluso:isLexicalizedSenseOf ?conceptURI .
      BIND(REPLACE(STR(?conceptURI), "^.*/concept_", "") AS ?conceptId)
    }
  }
}
GROUP BY ?lemmaId ?writtenRep ?partOfSpeech ?creationDate
ORDER BY ?lemmaId
```

## 3. Concepts Query

**Purpose**: Extracts semantic concepts with labels and hierarchical relationships

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?conceptId 
       (SAMPLE(?prefLabelDe) AS ?prefLabelDe)
       (SAMPLE(?prefLabelEn) AS ?prefLabelEn)
       (SAMPLE(?altLabelDe) AS ?altLabelDe)
       (SAMPLE(?altLabelEn) AS ?altLabelEn)
       (GROUP_CONCAT(DISTINCT ?broaderConceptId; SEPARATOR=",") AS ?broaderConcepts)
       (GROUP_CONCAT(DISTINCT ?narrowerConceptId; SEPARATOR=",") AS ?narrowerConcepts)
WHERE {
  # Get concept entities
  ?conceptURI a skos:Concept .
  
  # Extract the concept ID
  BIND(REPLACE(STR(?conceptURI), "^.*/concept_", "") AS ?conceptId)
  
  # Get preferred labels by language
  OPTIONAL { ?conceptURI skos:prefLabel ?prefLabelDe . FILTER(LANG(?prefLabelDe) = "de") }
  OPTIONAL { ?conceptURI skos:prefLabel ?prefLabelEn . FILTER(LANG(?prefLabelEn) = "en") }
  
  # Get alternative labels by language
  OPTIONAL { ?conceptURI skos:altLabel ?altLabelDe . FILTER(LANG(?altLabelDe) = "de") }
  OPTIONAL { ?conceptURI skos:altLabel ?altLabelEn . FILTER(LANG(?altLabelEn) = "en") }
  
  # Get broader concepts
  OPTIONAL {
    ?conceptURI skos:broader ?broaderURI .
    BIND(REPLACE(STR(?broaderURI), "^.*/concept_", "") AS ?broaderConceptId)
  }
  
  # Get narrower concepts
  OPTIONAL {
    ?conceptURI skos:narrower ?narrowerURI .
    BIND(REPLACE(STR(?narrowerURI), "^.*/concept_", "") AS ?narrowerConceptId)
  }
}
GROUP BY ?conceptId
ORDER BY ?conceptId
```

## 4. Genres/Text Types Query

**Purpose**: Extracts text genre classifications with German labels and hierarchies

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?genreId ?labelDe
       (GROUP_CONCAT(DISTINCT ?broaderGenreId; SEPARATOR=",") AS ?broaderGenres)
WHERE {
  # Focus only on text types
  ?genreURI a skos:Concept .
  FILTER(REGEX(STR(?genreURI), "textType_"))
  
  # Extract the genre ID
  BIND(REPLACE(STR(?genreURI), "^.*/textType_", "") AS ?genreId)
  
  # Get German labels
  ?genreURI skos:prefLabel ?labelDe . 
  FILTER(LANG(?labelDe) = "de")
  
  # Get broader genres
  OPTIONAL {
    ?genreURI skos:broader ?broaderURI .
    FILTER(REGEX(STR(?broaderURI), "textType_"))
    BIND(REPLACE(STR(?broaderURI), "^.*/textType_", "") AS ?broaderGenreId)
  }
}
GROUP BY ?genreId ?labelDe
ORDER BY ?genreId
```

## 5. Names/Onomastic Concepts Query

**Purpose**: Extracts name system concepts with language labels and relationships

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX mhdbdbi: <https://dh.plus.ac.at/mhdbdb/instance/>

SELECT DISTINCT ?nameConceptId ?prefLabelDe ?prefLabelEn
       (GROUP_CONCAT(DISTINCT ?broaderConceptId; SEPARATOR=",") AS ?broaderConcepts)
       (GROUP_CONCAT(DISTINCT ?exactMatchId; SEPARATOR=",") AS ?exactMatches)
       (GROUP_CONCAT(DISTINCT ?closeMatchId; SEPARATOR=",") AS ?closeMatches)
WHERE {
  # Get onomastic concepts
  ?conceptURI a skos:Concept ;
              skos:inScheme mhdbdbi:nameSystem .
  
  # Extract the concept ID
  BIND(REPLACE(STR(?conceptURI), "^.*/onomasticConcept_", "") AS ?nameConceptId)
  
  # Get preferred labels
  OPTIONAL { ?conceptURI skos:prefLabel ?prefLabelDe . FILTER(LANG(?prefLabelDe) = "de") }
  OPTIONAL { ?conceptURI skos:prefLabel ?prefLabelEn . FILTER(LANG(?prefLabelEn) = "en") }
  
  # Get broader concepts
  OPTIONAL {
    ?conceptURI skos:broader ?broaderURI .
    BIND(REPLACE(STR(?broaderURI), "^.*/onomasticConcept_", "") AS ?broaderConceptId)
  }
  
  # Get exact matches to regular concepts
  OPTIONAL {
    ?conceptURI skos:exactMatch ?exactURI .
    BIND(REPLACE(STR(?exactURI), "^.*/", "") AS ?exactMatchId)
  }
  
  # Get close matches to regular concepts
  OPTIONAL {
    ?conceptURI skos:closeMatch ?closeURI .
    BIND(REPLACE(STR(?closeURI), "^.*/", "") AS ?closeMatchId)
  }
}
GROUP BY ?nameConceptId ?prefLabelDe ?prefLabelEn
ORDER BY ?nameConceptId
```

## 6. Works Query

**Purpose**: Extracts work metadata with sigle, title, author references, and external identifiers

```sparql
PREFIX dhpluso: <https://dh.plus.ac.at/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?workURI ?workId ?title ?sigle ?handschriftencensusId ?wikidataId ?gndId
WHERE {
  # Find all works
  ?workURI a dhpluso:Text .
  
  # Get the work ID (whether numeric or UUID)
  BIND(REPLACE(STR(?workURI), "^.*/", "") AS ?workId)
  
  # Get titles
  OPTIONAL {
    ?workURI rdfs:label ?label .
    FILTER(LANG(?label) = "de" || LANG(?label) = "")
    BIND(STR(?label) AS ?title)
  }
  
  # Get sigles through expression and instance
  OPTIONAL {
    ?workURI dhpluso:hasExpression ?expressionURI .
    ?expressionURI dhpluso:hasInstance ?instanceURI .
    
    # Extract sigle from instance URI
    BIND(REPLACE(STR(?instanceURI), "^.*/([^/]+)(?:/.*)?$", "$1") AS ?rawSigle)
    
    # Filter out non-sigle values
    FILTER(?rawSigle != "print")
    FILTER(!REGEX(?rawSigle, "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"))
    
    BIND(?rawSigle AS ?sigle)
  }
  
  # Get external identifiers
  OPTIONAL {
    ?workURI owl:sameAs ?hcURI .
    FILTER(CONTAINS(STR(?hcURI), "handschriftencensus.de"))
    BIND(REPLACE(STR(?hcURI), "^.*werke/", "") AS ?handschriftencensusId)
  }
  
  OPTIONAL {
    ?workURI owl:sameAs ?wdURI .
    FILTER(CONTAINS(STR(?wdURI), "wikidata.org"))
    BIND(REPLACE(STR(?wdURI), "^.*/", "") AS ?wikidataId)
  }
  
  OPTIONAL {
    ?workURI owl:sameAs ?gndURI .
    FILTER(CONTAINS(STR(?gndURI), "d-nb.info/gnd"))
    BIND(REPLACE(STR(?gndURI), "^.*/gnd/", "") AS ?gndId)
  }
}
ORDER BY ?workId ?sigle
```