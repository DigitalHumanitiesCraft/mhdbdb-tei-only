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
                (GROUP_CONCAT(DISTINCT ?workId; SEPARATOR=",") AS ?associated)
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
###############################################################################
#  FLAT export: every label on every concept and on every broader ancestor
###############################################################################
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT
  ###########################################################################
  # ── focus concept (child) -------------------------------------------------
  ###########################################################################
  ?concept                                   # full URI
  (REPLACE(STR(?concept), "^.*/(?:textType_|c_)", "")
                                             AS ?conceptId)
  ?conceptLabel                              # literal (pref OR alt)
  (LANG(?conceptLabel)                       AS ?conceptLang)
  (REPLACE(STR(?scheme), "^.*/", "")
                                             AS ?schemeId)

  ###########################################################################
  # ── immediate or distant broader concept ---------------------------------
  ###########################################################################
  ?broader                                   # ancestor URI (UNDEF if none)
  ?broaderLabel                              # every label of that ancestor
  (LANG(?broaderLabel)                       AS ?broaderLang)
  (REPLACE(STR(?broader), "^.*/(?:textType_|c_)", "")
                                             AS ?broaderId)
WHERE {
  ###########################################################################
  # 1  restrict to both genre schemes
  ###########################################################################
  ?concept a skos:Concept ;
           skos:inScheme ?scheme .

  FILTER(?scheme IN (
      <https://dhplus.sbg.ac.at/mhdbdb/instance/textTypes>,
      <https://dhplus.sbg.ac.at/mhdbdb/instance/textreihentypologie>
  ))

  ###########################################################################
  # 2  every label on the focus concept
  ###########################################################################
  { ?concept skos:prefLabel | skos:altLabel  ?conceptLabel }

  ###########################################################################
  # 3  walk the entire broader chain (zero‑to‑many)
  ###########################################################################
  OPTIONAL {
    ?concept skos:broader+ ?broader .

    # every label on each ancestor
    ?broader skos:prefLabel | skos:altLabel ?broaderLabel .
  }
}
ORDER BY ?schemeId ?conceptId ?conceptLang ?broaderId ?broaderLang
```

There are textTypes and :textreihentypologie. But where is the connection to work?

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX mhdbdbi: <https://dh.plus.ac.at/mhdbdb/instance/>
PREFIX : <https://dhplus.sbg.ac.at/mhdbdb/instance/> 

SELECT ?textType ?prefLabel ?altLabel
WHERE {
    {?textType skos:inScheme mhdbdbi:textTypes.} UNION { ?textType skos:inScheme :textreihentypologie .}
  OPTIONAL { ?textType skos:prefLabel ?prefLabel . }
  OPTIONAL { ?textType skos:altLabel ?altLabel . }
}
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
###############################################################################
#  MHDBDB  –  WORK‑LEVEL EXPORT (lean, no heavy joins, no aggregation)
#  ---------------------------------------------------------------------------
#  • 1 row for every *literal or URI* that matters
#  • Language tags kept only where they exist (work / genre labels)
#  • “bib*” literals kept once – they are not language‑tagged in the dataset
#  • Genre URIs filtered to the useful dhplus.sbg.ac.at namespace
#
#  Result columns
#  --------------
#    id                          work URI
#    label                       work label literal
#    labelLang                   its @xml:lang
#    sameAs                      every owl:sameAs link
#    authorId                    URI of every contributor with role=aut
#    instance                    every electronic instance URI
#    genreForm                   specific genre concept URI
#    genreFormLabel              its German/English prefLabel (with lang tag)
#    genreFormLabelLang
#    genreFormMainParent         parent genre URI (if stored separately)
#    genreFormMainParentLabel    its prefLabel
#    genreParentLabelLang
#    bibTitle                    every BIBFRAME main title literal (no lang tag)
#    bibPlace                    place literal  (if any, no lang tag)
#    bibAgent                    agent literal  (if any, no lang tag)
#    bibDate                     date literal   (if any)
#
#  To export ALL works: ***PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# delete the `BIND` line*** (marked below)
#  ---------------------------------------------------------------------------
###############################################################################

PREFIX dhpluso: <https://dh.plus.ac.at/ontology#>
PREFIX rel:     <http://id.loc.gov/vocabulary/relators/>
PREFIX bf:      <http://id.loc.gov/ontologies/bibframe/>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>
PREFIX mhdbdbi: <https://dh.plus.ac.at/mhdbdb/instance/>

SELECT DISTINCT
       #######################################################################
       # work identity & label ----------------------------------------------
       #######################################################################
       ?id
       ?label                         (LANG(?label) AS ?labelLang)

       #######################################################################
       # external identifier -----------------------------------------------
       #######################################################################
       ?sameAs

       #######################################################################
       # authors (role = aut) -----------------------------------------------
       #######################################################################
       ?authorId

       #######################################################################
       # electronic instance URI --------------------------------------------
       #######################################################################
       ?instance

       #######################################################################
       # genre hierarchy -----------------------------------------------------
       #######################################################################
       ?genreForm           ?genreFormLabel
                            (LANG(?genreFormLabel) AS ?genreFormLabelLang)
       ?genreFormMainParent ?genreFormMainParentLabel
                            (LANG(?genreFormMainParentLabel) AS ?genreParentLabelLang)

       #######################################################################
       # BIBFRAME literals ---------------------------------------------------
       #######################################################################
       ?bibTitle ?bibPlace ?bibAgent ?bibDate
WHERE {

  ###########################################################################
  # 0)  CHOOSE SCOPE  -------------------------------------------------------
  #     • leave the BIND line for single‑work testing
  #     • delete it for a full export of the repository
  ###########################################################################
  BIND(mhdbdbi:work_89 AS ?id)      # ← remove this line to export all works
  ?id a dhpluso:Text .

  ###########################################################################
  # 1)  work labels (we keep ALL languages) ---------------------------------
  ###########################################################################
  ?id rdfs:label ?label .

  ###########################################################################
  # 2)  external identifiers -----------------------------------------------
  ###########################################################################
  OPTIONAL { ?id owl:sameAs ?sameAs }

  ###########################################################################
  # 3)  author links (URIs only) --------------------------------------------
  ###########################################################################
  OPTIONAL {
    ?id dhpluso:contribution ?c .
    ?c dhpluso:agent ?authorId ;
       dhpluso:role  rel:aut .
  }

  ###########################################################################
  # 4)  electronic instances (URIs only) ------------------------------------
  ###########################################################################
  OPTIONAL {
    ?id dhpluso:hasExpression/dhpluso:hasInstance ?instance .
    ?instance a dhpluso:Electronic .
  }

  ###########################################################################
  # 5)  genre / text‑type ---------------------------------------------------
  #     • keep only URIs in the dhplus.sbg.ac.at namespace
  #     • pull prefLabels for both the direct genre and its main parent
  ###########################################################################
  OPTIONAL {
    ?id dhpluso:genreForm ?genreForm .
    FILTER(STRSTARTS(STR(?genreForm), "https://dhplus.sbg.ac.at/"))
    OPTIONAL { ?genreForm skos:prefLabel ?genreFormLabel }
  }
  OPTIONAL {
    ?id dhpluso:genreFormMainparent ?genreFormMainParent .
    FILTER(STRSTARTS(STR(?genreFormMainParent), "https://dhplus.sbg.ac.at/"))
    OPTIONAL { ?genreFormMainParent skos:prefLabel ?genreFormMainParentLabel }
  }

  ###########################################################################
  # 6)  BIBFRAME data -------------------------------------------------------
  #     literals are stored WITHOUT language tags – no LANG() columns here
  ###########################################################################
  OPTIONAL {
    ?bib bf:instanceOf ?id .

    # main title (nested or flat)
    { ?bib bf:title/bf:mainTitle ?bibTitle }
    UNION
    { ?bib bf:title ?t FILTER(isLiteral(?t)) BIND(?t AS ?bibTitle) }

    # provisionActivity on bib
    OPTIONAL {
      ?bib bf:provisionActivity ?pa .
      OPTIONAL { ?pa bf:place/(rdfs:label|bf:placeTerm/rdfs:label) ?bibPlace }
      OPTIONAL { ?pa bf:agent/(rdfs:label|bf:agentLiteral)        ?bibAgent }
      OPTIONAL { ?pa bf:date                                     ?bibDate  }
    }
    # provisionActivity on parent record
    OPTIONAL {
      ?bib bf:partOf/bf:provisionActivity ?pa2 .
      OPTIONAL { ?pa2 bf:place/(rdfs:label|bf:placeTerm/rdfs:label) ?bibPlace }
      OPTIONAL { ?pa2 bf:agent/(rdfs:label|bf:agentLiteral)         ?bibAgent }
      OPTIONAL { ?pa2 bf:date                                      ?bibDate  }
    }
    # legacy date literal on bib record
    OPTIONAL { ?bib bf:provisionActivityDate ?bibDate }
  }
}
ORDER BY ?id ?labelLang
```
