#!/usr/bin/env python3
import csv
import xml.etree.ElementTree as ET
from lxml import etree
import os
import sys
import copy
import logging
from datetime import datetime
from collections import defaultdict

# Define namespaces
TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"

# Register namespaces for pretty output
ET.register_namespace("", TEI_NS)
ET.register_namespace("xml", XML_NS)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('tei_transformer')

# Set DEBUG level through environment variable
if os.environ.get('TEI_DEBUG') == '1':
    logger.setLevel(logging.DEBUG)


def detect_delimiter(csv_file):
    """
    Auto-detect delimiter from CSV file using a more robust approach.
    Checks for common delimiters and counts their occurrence in the first line.
    """
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()

            # Common delimiters to check
            delimiters = [',', '\t', ';', '|']
            counts = {d: first_line.count(d) for d in delimiters}

            # Return the delimiter with the highest count
            max_count = max(counts.values())
            if max_count > 0:
                for d, count in counts.items():
                    if count == max_count:
                        logger.debug(f"Detected delimiter '{d}' in {csv_file}")
                        return d

            # Fallback to comma if nothing found
            logger.warning(f"Could not detect delimiter in {csv_file}, using comma as default")
            return ','
    except Exception as e:
        logger.error(f"Error detecting delimiter in {csv_file}: {str(e)}")
        return ','


def read_csv_data(csv_file, key_field=None):
    """
    Read CSV file into a dictionary mapped by key_field if provided.
    Otherwise, return a list of row dictionaries.
    Handles delimiter detection automatically.
    """
    result = {} if key_field else []

    try:
        delimiter = detect_delimiter(csv_file)
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=delimiter)

            if key_field:
                # Group by key field
                for row in reader:
                    if key_field in row and row[key_field]:
                        key = row[key_field].strip()
                        if key not in result:
                            result[key] = []
                        result[key].append(row)
            else:
                # Just return the list
                result = list(reader)

        if key_field:
            logger.debug(f"Read {len(result)} unique entries from {csv_file}")
        else:
            logger.debug(f"Read {len(result)} rows from {csv_file}")

        # Print first row for debugging if in debug mode
        if logger.isEnabledFor(logging.DEBUG) and (key_field and result or result):
            if key_field:
                first_key = next(iter(result))
                logger.debug(f"First entry sample: {first_key} -> {result[first_key][0]}")
            else:
                logger.debug(f"First row sample: {result[0]}")

        return result
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_file}: {str(e)}")
        return {} if key_field else []


def create_tei_base(title):
    """Create base TEI structure with header"""
    # Create TEI structure
    tei = ET.Element("{" + TEI_NS + "}TEI")

    # Create TEI Header
    teiHeader = ET.SubElement(tei, "{" + TEI_NS + "}teiHeader")
    fileDesc = ET.SubElement(teiHeader, "{" + TEI_NS + "}fileDesc")

    # Title statement
    titleStmt = ET.SubElement(fileDesc, "{" + TEI_NS + "}titleStmt")
    title_elem = ET.SubElement(titleStmt, "{" + TEI_NS + "}title")
    title_elem.text = title

    # Publication statement
    publicationStmt = ET.SubElement(fileDesc, "{" + TEI_NS + "}publicationStmt")
    publisher = ET.SubElement(publicationStmt, "{" + TEI_NS + "}publisher")
    publisher.text = "Middle High German Database (MHDBDB)"
    date = ET.SubElement(publicationStmt, "{" + TEI_NS + "}date")
    date.text = datetime.now().strftime("%Y-%m-%d")

    # Source description
    sourceDesc = ET.SubElement(fileDesc, "{" + TEI_NS + "}sourceDesc")
    p = ET.SubElement(sourceDesc, "{" + TEI_NS + "}p")
    p.text = "Converted from RDF data"

    # Create main text and body
    text = ET.SubElement(tei, "{" + TEI_NS + "}text")
    body = ET.SubElement(text, "{" + TEI_NS + "}body")

    return tei, body


def write_tei_file(tei, output_file):
    """Write TEI element to file with proper formatting"""
    try:
        tree_string = ET.tostring(tei, encoding="utf-8")
        parser = etree.XMLParser(remove_blank_text=True)
        parsed = etree.fromstring(tree_string, parser)
        pretty = etree.tostring(
            parsed, pretty_print=True, encoding="utf-8", xml_declaration=True
        )

        with open(output_file, "wb") as f:
            f.write(pretty)

        logger.debug(f"Successfully wrote TEI file: {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error writing TEI file {output_file}: {str(e)}")
        return False


def normalize_id(id_str, prefix=None, strip_prefix=None):
    """
    Normalize ID by:
    1. Removing specified prefix if present
    2. Adding specified prefix if provided
    3. Stripping whitespace
    """
    if not id_str:
        return id_str

    # Clean the id string
    id_str = id_str.strip()

    # Remove prefix if needed
    if strip_prefix and id_str.startswith(strip_prefix):
        id_str = id_str[len(strip_prefix):]

    # Add prefix if needed
    if prefix and not id_str.startswith(prefix):
        id_str = f"{prefix}{id_str}"

    return id_str


def create_persons_tei(csv_file, output_file):
    """Transform persons CSV to TEI personography"""
    logger.info(f"Creating TEI personography from {csv_file}")

    tei, body = create_tei_base("MHDBDB Person Registry")

    # Create listPerson element
    listPerson = ET.SubElement(body, "{" + TEI_NS + "}listPerson")

    # Dictionary to collect data for each person
    person_data = defaultdict(lambda: {
        "preferredName": set(),
        "labelDe": set(),
        "labelEn": set(),
        "gndId": set(),
        "wikidataId": set(),
        "associatedWorks": set(),
    })

    # To store all relations for later
    relations = []

    # Read CSV data with error handling
    try:
        rows = read_csv_data(csv_file)

        for row in rows:
            # Extract person ID
            person_id = None
            if "personId" in row and row["personId"]:
                person_id = row["personId"]
            elif "personURI" in row and row["personURI"]:
                # Extract ID from URI
                person_id = row["personURI"].split("/")[-1]

            if not person_id:
                continue

            # Normalize ID
            person_id = normalize_id(person_id, strip_prefix="person_")

            # Collect all values
            for field in ["preferredName", "labelDe", "labelEn", "gndId", "wikidataId"]:
                if field in row and row[field]:
                    person_data[person_id][field].add(row[field])

            # Handle associated works
            if "associatedWorks" in row and row["associatedWorks"]:
                if "," in row["associatedWorks"]:
                    # Split comma-separated work IDs
                    for work_id in row["associatedWorks"].split(","):
                        if work_id.strip():
                            person_data[person_id]["associatedWorks"].add(work_id.strip())
                else:
                    person_data[person_id]["associatedWorks"].add(row["associatedWorks"].strip())

        # Now create person elements from collected data
        for person_id, data in person_data.items():
            # Create person element with standardized ID
            person = ET.SubElement(listPerson, "{" + TEI_NS + "}person")
            person.set("{" + XML_NS + "}id", f"person_{person_id}")

            # Add preferred name (use first one if multiple exist)
            if data["preferredName"]:
                persName = ET.SubElement(person, "{" + TEI_NS + "}persName")
                persName.set("type", "preferred")
                persName.text = next(iter(data["preferredName"]))

            # Add German name if different from preferred name
            if data["labelDe"]:
                preferred = (
                    next(iter(data["preferredName"])) if data["preferredName"] else None
                )
                for label in data["labelDe"]:
                    if label != preferred:
                        persName = ET.SubElement(person, "{" + TEI_NS + "}persName")
                        persName.set("type", "alternative")
                        persName.set("{" + XML_NS + "}lang", "de")
                        persName.text = label

            # Add English name if available and different
            if data["labelEn"]:
                preferred = (
                    next(iter(data["preferredName"])) if data["preferredName"] else None
                )
                for label in data["labelEn"]:
                    if label != preferred and label not in data["labelDe"]:
                        persName = ET.SubElement(person, "{" + TEI_NS + "}persName")
                        persName.set("type", "alternative")
                        persName.set("{" + XML_NS + "}lang", "en")
                        persName.text = label

            # Add all GND identifiers
            for gnd in data["gndId"]:
                idno = ET.SubElement(person, "{" + TEI_NS + "}idno")
                idno.set("type", "GND")
                idno.text = gnd

            # Add all Wikidata identifiers
            for wikidata in data["wikidataId"]:
                idno = ET.SubElement(person, "{" + TEI_NS + "}idno")
                idno.set("type", "wikidata")
                idno.text = wikidata

            # Add associated works as note
            if data["associatedWorks"]:
                works_list = sorted(data["associatedWorks"])
                note = ET.SubElement(person, "{" + TEI_NS + "}note")
                note.set("type", "works")
                note.text = ",".join(works_list)

                # Store relations for later addition at document level
                for work_id in works_list:
                    # Normalize work ID
                    work_id = normalize_id(work_id, strip_prefix="work_")

                    relations.append(
                        {
                            "name": "isAuthorOf",
                            "active": f"#person_{person_id}",
                            "passive": f"works.xml#work_{work_id}",
                        }
                    )

        # Add relations at the document level - after listPerson
        if relations:
            listRelation = ET.SubElement(body, "{" + TEI_NS + "}listRelation")
            for rel in relations:
                relation = ET.SubElement(listRelation, "{" + TEI_NS + "}relation")
                relation.set("name", rel["name"])
                relation.set("active", rel["active"])
                relation.set("passive", rel["passive"])

        # Write to file with proper formatting
        success = write_tei_file(tei, output_file)
        if success:
            logger.info(f"Created TEI personography file: {output_file}")
            logger.info(f"Processed {len(person_data)} unique persons")
            logger.info(f"Added {len(relations)} work relations")

        return success
    except Exception as e:
        logger.error(f"Error creating persons TEI file: {str(e)}")
        return False


def create_lexicon_tei(csv_file, output_file):
    """Transform lemma data to TEI dictionary format based on actual data model"""
    logger.info(f"Creating TEI lexicon from {csv_file}")

    tei, body = create_tei_base("MHDBDB Middle High German Lexicon")

    # Create entry list
    entries = ET.SubElement(body, "{" + TEI_NS + "}div")
    entries.set("type", "lexicon")

    # Dictionary to collect data for each lemma
    lemma_data = {}

    try:
        # Read CSV data
        rows = read_csv_data(csv_file)

        for row in rows:
            if "lemmaId" not in row or not row["lemmaId"]:
                continue

            lemma_id = normalize_id(row["lemmaId"], strip_prefix="lemma_")

            # Get part of speech (default to "UNKNOWN" if missing)
            pos = row.get("partOfSpeech", "UNKNOWN")

            # Initialize lemma data if not yet seen
            if lemma_id not in lemma_data:
                lemma_data[lemma_id] = {
                    "writtenRep": set(),
                    "pos_variants": set(),
                    "senses": {},  # Dictionary to map sense IDs to concepts
                }

            # Collect written form and POS
            if "writtenRep" in row and row["writtenRep"]:
                lemma_data[lemma_id]["writtenRep"].add(row["writtenRep"])

            lemma_data[lemma_id]["pos_variants"].add(pos)

            # Process senses and concepts
            senses = []
            if "senses" in row and row["senses"]:
                if "," in row["senses"]:
                    senses = [s.strip() for s in row["senses"].split(",") if s.strip()]
                else:
                    senses = [row["senses"].strip()]

            concepts = []
            if "relatedConcepts" in row and row["relatedConcepts"]:
                if "," in row["relatedConcepts"]:
                    concepts = [
                        c.strip()
                        for c in row["relatedConcepts"].split(",")
                        if c.strip()
                    ]
                else:
                    concepts = [row["relatedConcepts"].strip()]

            # Associate concepts with senses
            if senses:
                for sense_id in senses:
                    sense_id = normalize_id(sense_id, strip_prefix="sense_")

                    # Initialize this sense if not seen
                    if sense_id not in lemma_data[lemma_id]["senses"]:
                        lemma_data[lemma_id]["senses"][sense_id] = set()

                    # Add concepts to this sense
                    for concept in concepts:
                        lemma_data[lemma_id]["senses"][sense_id].add(concept)

        # Now create entry elements from collected data
        for lemma_id, data in lemma_data.items():
            # Create entry element
            entry = ET.SubElement(entries, "{" + TEI_NS + "}entry")
            entry.set("{" + XML_NS + "}id", f"lemma_{lemma_id}")

            # Form group - contains the written representation
            if data["writtenRep"]:
                form = ET.SubElement(entry, "{" + TEI_NS + "}form")
                form.set("type", "lemma")
                orth = ET.SubElement(form, "{" + TEI_NS + "}orth")
                orth.text = next(iter(data["writtenRep"]))

            # Add grammatical information for all parts of speech
            gramGrp = ET.SubElement(entry, "{" + TEI_NS + "}gramGrp")
            for pos in sorted(data["pos_variants"]):
                pos_elem = ET.SubElement(gramGrp, "{" + TEI_NS + "}pos")
                pos_elem.text = pos

            # Add senses
            for sense_id, concepts in data["senses"].items():
                sense = ET.SubElement(entry, "{" + TEI_NS + "}sense")
                # Make the ID unique by combining lemma ID and sense ID
                sense.set("{" + XML_NS + "}id", f"lemma_{lemma_id}_sense_{sense_id}")

                # Add concept references
                for concept in concepts:
                    concept = normalize_id(concept, strip_prefix="concept_")
                    ptr = ET.SubElement(sense, "{" + TEI_NS + "}ptr")
                    ptr.set("target", f"concepts.xml#concept_{concept}")

        # Write to file
        success = write_tei_file(tei, output_file)
        if success:
            logger.info(f"Created TEI lexicon file: {output_file}")
            logger.info(f"Processed {len(lemma_data)} unique lemmas")
            logger.info(
                f"Number of lemmas with multiple parts of speech: {sum(1 for data in lemma_data.values() if len(data['pos_variants']) > 1)}"
            )

        return success
    except Exception as e:
        logger.error(f"Error creating lexicon TEI file: {str(e)}")
        return False


def create_concepts_tei(csv_file, output_file):
    """Transform concept data to TEI taxonomy format with correct TEI structure"""
    logger.info(f"Creating TEI concepts taxonomy from {csv_file}")

    # Create TEI structure
    tei = ET.Element("{" + TEI_NS + "}TEI")

    # Create TEI Header
    teiHeader = ET.SubElement(tei, "{" + TEI_NS + "}teiHeader")
    fileDesc = ET.SubElement(teiHeader, "{" + TEI_NS + "}fileDesc")

    # Title statement
    titleStmt = ET.SubElement(fileDesc, "{" + TEI_NS + "}titleStmt")
    title_elem = ET.SubElement(titleStmt, "{" + TEI_NS + "}title")
    title_elem.text = "MHDBDB Semantic Concepts Taxonomy"

    # Publication statement
    publicationStmt = ET.SubElement(fileDesc, "{" + TEI_NS + "}publicationStmt")
    publisher = ET.SubElement(publicationStmt, "{" + TEI_NS + "}publisher")
    publisher.text = "Middle High German Database (MHDBDB)"
    date = ET.SubElement(publicationStmt, "{" + TEI_NS + "}date")
    date.text = datetime.now().strftime("%Y-%m-%d")

    # Source description
    sourceDesc = ET.SubElement(fileDesc, "{" + TEI_NS + "}sourceDesc")
    p = ET.SubElement(sourceDesc, "{" + TEI_NS + "}p")
    p.text = "Converted from RDF data"

    # Add encodingDesc with classDecl for taxonomy
    encodingDesc = ET.SubElement(teiHeader, "{" + TEI_NS + "}encodingDesc")
    classDecl = ET.SubElement(encodingDesc, "{" + TEI_NS + "}classDecl")

    # Create taxonomy element within classDecl
    taxonomy = ET.SubElement(classDecl, "{" + TEI_NS + "}taxonomy")
    taxonomy.set("{" + XML_NS + "}id", "mhdbdb-concepts")

    # Add description for the taxonomy
    desc = ET.SubElement(taxonomy, "{" + TEI_NS + "}desc")
    desc.text = "Semantic concept taxonomy of the Middle High German Database"

    try:
        # Dictionary to collect data for each concept
        concept_data = defaultdict(lambda: {
            "prefLabelDe": set(),
            "prefLabelEn": set(),
            "altLabelDe": set(),
            "altLabelEn": set(),
            "broaderConcepts": set(),
        })

        # Read CSV data
        rows = read_csv_data(csv_file)

        for row in rows:
            if "conceptId" not in row or not row["conceptId"]:
                continue

            concept_id = normalize_id(row["conceptId"], strip_prefix="concept_")

            # Collect text fields
            for field in ["prefLabelDe", "prefLabelEn", "altLabelDe", "altLabelEn"]:
                if field in row and row[field]:
                    concept_data[concept_id][field].add(row[field])

            # Process broader concepts
            if "broaderConcepts" in row and row["broaderConcepts"]:
                for broader in row["broaderConcepts"].split(","):
                    broader = broader.strip()
                    if broader:
                        broader = normalize_id(broader, strip_prefix="concept_")
                        concept_data[concept_id]["broaderConcepts"].add(broader)

        # Create category elements
        for concept_id, data in concept_data.items():
            # Create category element
            category = ET.SubElement(taxonomy, "{" + TEI_NS + "}category")
            category.set("{" + XML_NS + "}id", f"concept_{concept_id}")

            # Create a single catDesc element to contain all terms and references
            catDesc = ET.SubElement(category, "{" + TEI_NS + "}catDesc")

            # Add German label as term
            if data["prefLabelDe"]:
                term = ET.SubElement(catDesc, "{" + TEI_NS + "}term")
                term.set("{" + XML_NS + "}lang", "de")
                term.text = next(iter(data["prefLabelDe"]))

            # Add English label as term
            if data["prefLabelEn"]:
                term = ET.SubElement(catDesc, "{" + TEI_NS + "}term")
                term.set("{" + XML_NS + "}lang", "en")
                term.text = next(iter(data["prefLabelEn"]))

            # Add alternative German labels as terms with type="alternative"
            for label in data["altLabelDe"]:
                term = ET.SubElement(catDesc, "{" + TEI_NS + "}term")
                term.set("type", "alternative")
                term.set("{" + XML_NS + "}lang", "de")
                term.text = label

            # Add alternative English labels as terms with type="alternative"
            for label in data["altLabelEn"]:
                term = ET.SubElement(catDesc, "{" + TEI_NS + "}term")
                term.set("type", "alternative")
                term.set("{" + XML_NS + "}lang", "en")
                term.text = label

            # Add broader concept references inside catDesc
            for broader_id in data["broaderConcepts"]:
                ptr = ET.SubElement(catDesc, "{" + TEI_NS + "}ptr")
                ptr.set("type", "broader")
                ptr.set("target", f"#concept_{broader_id}")

        # Create text/body with basic explanation
        text = ET.SubElement(tei, "{" + TEI_NS + "}text")
        body = ET.SubElement(text, "{" + TEI_NS + "}body")
        p = ET.SubElement(body, "{" + TEI_NS + "}p")
        p.text = "This file contains the semantic concept taxonomy of the Middle High German Database (MHDBDB). The taxonomy is defined in the header's <classDecl> section."

        # Write to file
        success = write_tei_file(tei, output_file)
        if success:
            logger.info(f"Created TEI concepts taxonomy file: {output_file}")
            logger.info(f"Processed {len(concept_data)} unique concepts")

        return success
    except Exception as e:
        logger.error(f"Error creating concepts TEI file: {str(e)}")
        return False


def create_genres_tei(csv_file, output_file):
    """Transform genre data to TEI taxonomy format with correct TEI structure"""
    logger.info(f"Creating TEI genres taxonomy from {csv_file}")

    # Create TEI structure
    tei = ET.Element("{" + TEI_NS + "}TEI")

    # Create TEI Header
    teiHeader = ET.SubElement(tei, "{" + TEI_NS + "}teiHeader")
    fileDesc = ET.SubElement(teiHeader, "{" + TEI_NS + "}fileDesc")

    # Title statement
    titleStmt = ET.SubElement(fileDesc, "{" + TEI_NS + "}titleStmt")
    title_elem = ET.SubElement(titleStmt, "{" + TEI_NS + "}title")
    title_elem.text = "MHDBDB Text Type Taxonomy"

    # Publication statement
    publicationStmt = ET.SubElement(fileDesc, "{" + TEI_NS + "}publicationStmt")
    publisher = ET.SubElement(publicationStmt, "{" + TEI_NS + "}publisher")
    publisher.text = "Middle High German Database (MHDBDB)"
    date = ET.SubElement(publicationStmt, "{" + TEI_NS + "}date")
    date.text = datetime.now().strftime("%Y-%m-%d")

    # Source description
    sourceDesc = ET.SubElement(fileDesc, "{" + TEI_NS + "}sourceDesc")
    p = ET.SubElement(sourceDesc, "{" + TEI_NS + "}p")
    p.text = "Converted from RDF data"

    # Add encodingDesc with classDecl for taxonomy
    encodingDesc = ET.SubElement(teiHeader, "{" + TEI_NS + "}encodingDesc")
    classDecl = ET.SubElement(encodingDesc, "{" + TEI_NS + "}classDecl")

    # Create taxonomy element within classDecl
    taxonomy = ET.SubElement(classDecl, "{" + TEI_NS + "}taxonomy")
    taxonomy.set("{" + XML_NS + "}id", "mhdbdb-genres")

    # Add description for the taxonomy
    desc = ET.SubElement(taxonomy, "{" + TEI_NS + "}desc")
    desc.text = "Text type taxonomy of the Middle High German Database"

    try:
        # Dictionary to collect data for each genre
        genre_data = defaultdict(lambda: {"labelDe": set()})

        # Read CSV data
        rows = read_csv_data(csv_file)

        for row in rows:
            if "genreId" not in row or not row["genreId"]:
                continue

            genre_id = normalize_id(row["genreId"], strip_prefix="genre_")

            # Collect label
            if "labelDe" in row and row["labelDe"]:
                genre_data[genre_id]["labelDe"].add(row["labelDe"])

        # Second pass: create category elements
        for genre_id, data in genre_data.items():
            # Create category element
            category = ET.SubElement(taxonomy, "{" + TEI_NS + "}category")
            category.set("{" + XML_NS + "}id", f"genre_{genre_id}")

            # Create a single catDesc element to contain all terms
            catDesc = ET.SubElement(category, "{" + TEI_NS + "}catDesc")

            # Add German label as term
            if data["labelDe"]:
                for label in data["labelDe"]:
                    term = ET.SubElement(catDesc, "{" + TEI_NS + "}term")
                    term.set("{" + XML_NS + "}lang", "de")
                    term.text = label

        # Create text/body with basic explanation
        text = ET.SubElement(tei, "{" + TEI_NS + "}text")
        body = ET.SubElement(text, "{" + TEI_NS + "}body")
        p = ET.SubElement(body, "{" + TEI_NS + "}p")
        p.text = "This file contains the text type (genre) taxonomy of the Middle High German Database (MHDBDB). The taxonomy is defined in the header's <classDecl> section."

        # Write to file
        success = write_tei_file(tei, output_file)
        if success:
            logger.info(f"Created TEI genres taxonomy file: {output_file}")
            logger.info(f"Processed {len(genre_data)} unique genres")

        return success
    except Exception as e:
        logger.error(f"Error creating genres TEI file: {str(e)}")
        return False


def create_names_tei(csv_file, output_file):
    """Transform onomastic data to TEI taxonomy format with correct TEI structure"""
    logger.info(f"Creating TEI names taxonomy from {csv_file}")

    # Create TEI structure
    tei = ET.Element("{" + TEI_NS + "}TEI")

    # Create TEI Header
    teiHeader = ET.SubElement(tei, "{" + TEI_NS + "}teiHeader")
    fileDesc = ET.SubElement(teiHeader, "{" + TEI_NS + "}fileDesc")

    # Title statement
    titleStmt = ET.SubElement(fileDesc, "{" + TEI_NS + "}titleStmt")
    title_elem = ET.SubElement(titleStmt, "{" + TEI_NS + "}title")
    title_elem.text = "MHDBDB Onomastic System"

    # Publication statement
    publicationStmt = ET.SubElement(fileDesc, "{" + TEI_NS + "}publicationStmt")
    publisher = ET.SubElement(publicationStmt, "{" + TEI_NS + "}publisher")
    publisher.text = "Middle High German Database (MHDBDB)"
    date = ET.SubElement(publicationStmt, "{" + TEI_NS + "}date")
    date.text = datetime.now().strftime("%Y-%m-%d")

    # Source description
    sourceDesc = ET.SubElement(fileDesc, "{" + TEI_NS + "}sourceDesc")
    p = ET.SubElement(sourceDesc, "{" + TEI_NS + "}p")
    p.text = "Converted from RDF data"

    # Add encodingDesc with classDecl for taxonomy
    encodingDesc = ET.SubElement(teiHeader, "{" + TEI_NS + "}encodingDesc")
    classDecl = ET.SubElement(encodingDesc, "{" + TEI_NS + "}classDecl")

    # Create taxonomy element within classDecl
    taxonomy = ET.SubElement(classDecl, "{" + TEI_NS + "}taxonomy")
    taxonomy.set("{" + XML_NS + "}id", "mhdbdb-names")

    # Add description for the taxonomy
    desc = ET.SubElement(taxonomy, "{" + TEI_NS + "}desc")
    desc.text = "Onomastic system of the Middle High German Database"

    try:
        # Dictionary to collect data for each name
        name_data = defaultdict(lambda: {
            "prefLabelDe": set(),
            "prefLabelEn": set(),
            "broaderConcepts": set(),
            "exactMatches": set(),
            "closeMatches": set(),
        })

        # Read CSV data
        rows = read_csv_data(csv_file)

        for row in rows:
            if "nameConceptId" not in row or not row["nameConceptId"]:
                continue

            name_id = normalize_id(row["nameConceptId"], strip_prefix="name_")

            # Collect text fields
            for field in ["prefLabelDe", "prefLabelEn"]:
                if field in row and row[field]:
                    name_data[name_id][field].add(row[field])

            # Process broader concepts
            if "broaderConcepts" in row and row["broaderConcepts"]:
                for broader in row["broaderConcepts"].split(","):
                    broader = broader.strip()
                    if broader:
                        broader = normalize_id(broader, strip_prefix="name_")
                        name_data[name_id]["broaderConcepts"].add(broader)

            # Process exact matches to concepts
            if "exactMatches" in row and row["exactMatches"]:
                for concept in row["exactMatches"].split(","):
                    concept = concept.strip()
                    if concept:
                        concept = normalize_id(concept, strip_prefix="concept_")
                        name_data[name_id]["exactMatches"].add(concept)

            # Process close matches to concepts
            if "closeMatches" in row and row["closeMatches"]:
                for concept in row["closeMatches"].split(","):
                    concept = concept.strip()
                    if concept:
                        concept = normalize_id(concept, strip_prefix="concept_")
                        name_data[name_id]["closeMatches"].add(concept)

        # Second pass: create category elements
        for name_id, data in name_data.items():
            # Create category element
            category = ET.SubElement(taxonomy, "{" + TEI_NS + "}category")
            category.set("{" + XML_NS + "}id", f"name_{name_id}")

            # Create a single catDesc element to contain all content
            catDesc = ET.SubElement(category, "{" + TEI_NS + "}catDesc")

            # Add German label as term
            if data["prefLabelDe"]:
                for label in data["prefLabelDe"]:
                    term = ET.SubElement(catDesc, "{" + TEI_NS + "}term")
                    term.set("{" + XML_NS + "}lang", "de")
                    term.text = label

            # Add English label as term
            if data["prefLabelEn"]:
                for label in data["prefLabelEn"]:
                    term = ET.SubElement(catDesc, "{" + TEI_NS + "}term")
                    term.set("{" + XML_NS + "}lang", "en")
                    term.text = label

            # Add broader name references
            for broader_id in data["broaderConcepts"]:
                ptr = ET.SubElement(catDesc, "{" + TEI_NS + "}ptr")
                ptr.set("type", "broader")
                ptr.set("target", f"#name_{broader_id}")

            # Add exact match references to concepts
            for concept_id in data["exactMatches"]:
                ptr = ET.SubElement(catDesc, "{" + TEI_NS + "}ptr")
                ptr.set("type", "exactMatch")
                ptr.set("target", f"concepts.xml#concept_{concept_id}")

            # Add close match references to concepts
            for concept_id in data["closeMatches"]:
                ptr = ET.SubElement(catDesc, "{" + TEI_NS + "}ptr")
                ptr.set("type", "closeMatch")
                ptr.set("target", f"concepts.xml#concept_{concept_id}")

        # Create text/body with basic explanation
        text = ET.SubElement(tei, "{" + TEI_NS + "}text")
        body = ET.SubElement(text, "{" + TEI_NS + "}body")
        p = ET.SubElement(body, "{" + TEI_NS + "}p")
        p.text = "This file contains the onomastic system of the Middle High German Database (MHDBDB). The taxonomy is defined in the header's <classDecl> section."

        # Write to file
        success = write_tei_file(tei, output_file)
        if success:
            logger.info(f"Created TEI names file: {output_file}")
            logger.info(f"Processed {len(name_data)} unique name concepts")

        return success
    except Exception as e:
        logger.error(f"Error creating names TEI file: {str(e)}")
        return False


def create_works_tei(csv_file, output_file, persons_file=None):
    """Transform works data to TEI format with proper handling of multiple sigles and titles"""
    logger.info(f"Creating TEI works registry from {csv_file}")

    tei, body = create_tei_base("MHDBDB Works Registry")

    # Create list of works
    listBibl = ET.SubElement(body, "{" + TEI_NS + "}listBibl")

    try:
        # Dictionary to collect data for each work
        work_data = defaultdict(lambda: {
            'sigle': set(),
            'title': set(),
            'authors': set(),
            'handschriftencensus': set(),
            'wikidata': set(),
            'gnd': set()
        })

        # Load person data if available
        persons = {}
        if persons_file and os.path.exists(persons_file):
            person_rows = read_csv_data(persons_file)
            for row in person_rows:
                person_id = row.get('personId') or (
                    row.get('personURI', '').split('/')[-1] if row.get('personURI') else ''
                )
                if person_id:
                    person_id = normalize_id(person_id, strip_prefix="person_")
                    if 'preferredName' in row and row['preferredName']:
                        persons[person_id] = row['preferredName']

        # Read works data
        work_rows = read_csv_data(csv_file)

        for row in work_rows:
            if 'workId' not in row or not row['workId']:
                continue

            work_id = normalize_id(row['workId'], strip_prefix="work_")

            # Add sigle if present
            if 'sigle' in row and row['sigle']:
                work_data[work_id]['sigle'].add(row['sigle'].strip())

            # Add title if present
            if 'title' in row and row['title']:
                work_data[work_id]['title'].add(row['title'].strip())

            # Add author if present
            if 'authorId' in row and row['authorId']:
                author_id = normalize_id(row['authorId'], strip_prefix="person_")
                work_data[work_id]['authors'].add(author_id)

            # Add external IDs if present
            if 'handschriftencensusId' in row and row['handschriftencensusId']:
                work_data[work_id]['handschriftencensus'].add(row['handschriftencensusId'].strip())

            if 'wikidataId' in row and row['wikidataId']:
                work_data[work_id]['wikidata'].add(row['wikidataId'].strip())

            if 'gndId' in row and row['gndId']:
                work_data[work_id]['gnd'].add(row['gndId'].strip())

        # Create bibliographic entries
        for work_id, data in work_data.items():
            # Create bibliographic entry
            bibl = ET.SubElement(listBibl, "{" + TEI_NS + "}bibl")
            bibl.set("{" + XML_NS + "}id", f"work_{work_id}")

            # Add all titles
            for title_text in sorted(data['title']):
                title = ET.SubElement(bibl, "{" + TEI_NS + "}title")
                title.text = title_text

            # Add all sigles
            for sigle_text in sorted(data['sigle']):
                idno = ET.SubElement(bibl, "{" + TEI_NS + "}idno")
                idno.set("type", "sigle")
                idno.text = sigle_text

            # Add authors
            for author_id in sorted(data['authors']):
                author = ET.SubElement(bibl, "{" + TEI_NS + "}author")
                author.set("ref", f"persons.xml#person_{author_id}")
                if author_id in persons:
                    author.text = persons[author_id]

            # Add external identifiers
            for hc_id in sorted(data['handschriftencensus']):
                if hc_id.strip():  # Skip empty values
                    idno = ET.SubElement(bibl, "{" + TEI_NS + "}idno")
                    idno.set("type", "handschriftencensus")
                    idno.text = hc_id

            for wikidata_id in sorted(data['wikidata']):
                if wikidata_id.strip():  # Skip empty values
                    idno = ET.SubElement(bibl, "{" + TEI_NS + "}idno")
                    idno.set("type", "wikidata")
                    idno.text = wikidata_id

            for gnd_id in sorted(data['gnd']):
                if gnd_id.strip():  # Skip empty values
                    idno = ET.SubElement(bibl, "{" + TEI_NS + "}idno")
                    idno.set("type", "GND")
                    idno.text = gnd_id

        # Write to file
        success = write_tei_file(tei, output_file)
        if success:
            logger.info(f"Created TEI works file: {output_file}")
            logger.info(f"Processed {len(work_data)} unique works")
            logger.info(f"Total number of sigles: {sum(len(data['sigle']) for data in work_data.values())}")
            logger.info(f"Total number of titles: {sum(len(data['title']) for data in work_data.values())}")

        return success
    except Exception as e:
        logger.error(f"Error creating works TEI file: {str(e)}")
        return False

def parse_xml_dump(xml_dump_file):
    """Parse the XML dump to extract word type to sense mappings"""
    type_to_sense = {}

    try:
        # Create a parser that ignores DTD declarations
        parser = etree.XMLParser(dtd_validation=False, load_dtd=False, resolve_entities=False)

        # Parse the full file (safer for this specific XML format)
        tree = etree.parse(xml_dump_file, parser)

        # Find all DATA_RECORD elements
        for record in tree.findall("//DATA_RECORD"):
            word_elem = record.find("WORD")
            meaning_elem = record.find("MEANING")

            if word_elem is not None and word_elem.text and meaning_elem is not None and meaning_elem.text:
                type_id = word_elem.text.strip()
                sense_id = meaning_elem.text.strip()

                # Store the mapping
                if type_id and sense_id:
                    type_to_sense[type_id] = sense_id

        logger.info(f"Parsed {len(type_to_sense)} type-sense mappings from XML dump")
        return type_to_sense
    except Exception as e:
        logger.error(f"Error parsing XML dump: {str(e)}")
        return {}


def extract_sense_concepts(lexicon_file):
    """Extract sense-concept mappings from lexicon.xml"""
    sense_to_concepts = {}

    try:
        tree = etree.parse(lexicon_file)
        ns = {"tei": TEI_NS, "xml": XML_NS}

        for sense in tree.findall(f".//tei:sense", ns):
            sense_id_full = sense.get(f"{{{XML_NS}}}id")
            if not sense_id_full or "_sense_" not in sense_id_full:
                continue

            # Extract the basic sense ID
            sense_id = sense_id_full.split("_sense_")[1]

            # Get all concept references
            concepts = []
            for ptr in sense.findall(f".//tei:ptr", ns):
                target = ptr.get('target')
                if target and 'concept_' in target:
                    concept_id = target.split('concept_')[1]
                    concepts.append(concept_id)

            # Store mapping
            sense_to_concepts[sense_id] = concepts

        logger.info(f"Extracted {len(sense_to_concepts)} sense-concept mappings from lexicon.xml")
        return sense_to_concepts
    except Exception as e:
        logger.error(f"Error extracting sense-concept mappings: {str(e)}")
        return {}


def create_types_tei(xml_dump_file, lexicon_file, output_file):
    """Create types.xml connecting types to senses and concepts"""
    logger.info(f"Creating TEI types registry from {xml_dump_file}")

    try:
        # Get type-sense mappings from XML dump
        type_to_sense = parse_xml_dump(xml_dump_file)

        # Get sense-concept mappings from lexicon.xml
        sense_to_concepts = extract_sense_concepts(lexicon_file)

        # Create TEI structure
        tei, body = create_tei_base("MHDBDB Word Type Registry")
        type_registry = ET.SubElement(body, "{" + TEI_NS + "}div")
        type_registry.set("type", "typeRegistry")

        # Count of processed types
        processed = 0

        # Create entries
        for type_id, sense_id in type_to_sense.items():
            form = ET.SubElement(type_registry, "{" + TEI_NS + "}form")
            form.set("{" + XML_NS + "}id", f"type_{type_id}")

            # Add sense reference
            ptr = ET.SubElement(form, "{" + TEI_NS + "}ptr")
            ptr.set("type", "sense")
            ptr.set("target", f"lexicon.xml#sense_{sense_id}")

            # Add concept references if available
            if sense_id in sense_to_concepts:
                for concept_id in sense_to_concepts[sense_id]:
                    concept_ptr = ET.SubElement(form, "{" + TEI_NS + "}ptr")
                    concept_ptr.set("type", "concept")
                    concept_ptr.set("target", f"concepts.xml#concept_{concept_id}")

            processed += 1

        # Write to file
        success = write_tei_file(tei, output_file)
        if success:
            logger.info(f"Created TEI types file: {output_file}")
            logger.info(f"Processed {processed} unique word types")

        return success
    except Exception as e:
        logger.error(f"Error creating types TEI file: {str(e)}")
        return False


def enhance_tei_header(tei_file, works_csv, persons_csv, output_file):
    """Add metadata from works and persons data to TEI file headers"""
    logger.info(f"Enhancing TEI header for {tei_file}")

    try:
        # Parse the existing TEI file
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(tei_file, parser)
        root = tree.getroot()

        # Extract the sigle from the file
        sigle = os.path.basename(tei_file).split('.')[0]
        logger.debug(f"Extracted sigle: {sigle}")

        # Load works and persons data
        works_by_sigle = read_csv_data(works_csv, key_field='sigle')
        works_by_id = read_csv_data(works_csv, key_field='workId')
        persons_data = read_csv_data(persons_csv, key_field='personId')

        # Also check for personURI field in persons data
        for row in read_csv_data(persons_csv):
            if 'personURI' in row and row['personURI'] and 'personId' not in row:
                person_id = row['personURI'].split('/')[-1]
                person_id = normalize_id(person_id, strip_prefix="person_")
                if person_id not in persons_data:
                    persons_data[person_id] = [row]

        # Find work data for this sigle
        work_id = None
        work_data = {
            'title': set(),
            'sigle': set(),
            'authors': set(),
            'handschriftencensus': set(),
            'wikidata': set(),
            'gnd': set()
        }

        # Check if we have data for this sigle
        if sigle in works_by_sigle:
            logger.debug(f"Found work data for sigle {sigle}")

            # Get work ID from first matching row
            first_match = works_by_sigle[sigle][0]
            work_id = normalize_id(first_match['workId'], strip_prefix="work_")

            # Collect data from all rows with this sigle
            for row in works_by_sigle[sigle]:
                if 'title' in row and row['title']:
                    work_data['title'].add(row['title'].strip())

                if 'sigle' in row and row['sigle']:
                    work_data['sigle'].add(row['sigle'].strip())

                if 'authorId' in row and row['authorId']:
                    author_id = normalize_id(row['authorId'], strip_prefix="person_")
                    work_data['authors'].add(author_id)

                if 'handschriftencensusId' in row and row['handschriftencensusId']:
                    work_data['handschriftencensus'].add(row['handschriftencensusId'].strip())

                if 'wikidataId' in row and row['wikidataId']:
                    work_data['wikidata'].add(row['wikidataId'].strip())

                if 'gndId' in row and row['gndId']:
                    work_data['gnd'].add(row['gndId'].strip())
        else:
            logger.warning(f"No work data found for sigle {sigle}")
            return False

        # Now collect data from other rows with the same work_id
        if work_id and work_id in works_by_id:
            for row in works_by_id[work_id]:
                # Skip rows we've already processed
                if 'sigle' in row and row['sigle'] and row['sigle'].strip() == sigle:
                    continue

                if 'title' in row and row['title']:
                    work_data['title'].add(row['title'].strip())

                if 'sigle' in row and row['sigle'] and row['sigle'] != sigle:
                    work_data['sigle'].add(row['sigle'].strip())

                if 'authorId' in row and row['authorId']:
                    author_id = normalize_id(row['authorId'], strip_prefix="person_")
                    work_data['authors'].add(author_id)

                if 'handschriftencensusId' in row and row['handschriftencensusId']:
                    work_data['handschriftencensus'].add(row['handschriftencensusId'].strip())

                if 'wikidataId' in row and row['wikidataId']:
                    work_data['wikidata'].add(row['wikidataId'].strip())

                if 'gndId' in row and row['gndId']:
                    work_data['gnd'].add(row['gndId'].strip())

        # Find header element
        ns = {"tei": "http://www.tei-c.org/ns/1.0"}
        header = root.find(".//tei:teiHeader", ns)

        if header is None:
            logger.error(f"No teiHeader found in {tei_file}")
            return False

        # Find fileDesc
        file_desc = header.find(".//tei:fileDesc", ns)
        if file_desc is None:
            file_desc = etree.SubElement(header, "{" + TEI_NS + "}fileDesc")

        # Save existing elements we want to preserve
        # (Not used in this implementation, but kept for reference)
        old_title_stmt = file_desc.find(".//tei:titleStmt", ns)
        old_source_desc = file_desc.find(".//tei:sourceDesc", ns)

        # Clear the fileDesc to rebuild with correct order
        for child in list(file_desc):
            file_desc.remove(child)

        # 1. Create/Update titleStmt
        title_stmt = etree.SubElement(file_desc, "{" + TEI_NS + "}titleStmt")

        # Add title - use first title from work_data if available
        title = etree.SubElement(title_stmt, "{" + TEI_NS + "}title")
        if work_data['title']:
            # Get the first title from the sorted list of titles
            title.text = sorted(work_data['title'])[0]
        else:
            title.text = sigle

        # Add author references if available
        if work_data['authors']:
            for author_id in sorted(work_data['authors']):
                # Find author name
                author_name = None
                if author_id in persons_data and persons_data[author_id]:
                    # Use preferredName from first entry
                    author_data = persons_data[author_id][0]
                    if 'preferredName' in author_data and author_data['preferredName']:
                        author_name = author_data['preferredName']

                # Add author element
                author = etree.SubElement(title_stmt, "{" + TEI_NS + "}author")
                author.set("ref", f"persons.xml#person_{author_id}")
                if author_name:
                    author.text = author_name

        # 2. Create the publicationStmt with hardcoded content (before sourceDesc)
        pub_stmt = etree.SubElement(file_desc, "{" + TEI_NS + "}publicationStmt")

        # Add publisher
        publisher = etree.SubElement(pub_stmt, "{" + TEI_NS + "}publisher")
        org_name1 = etree.SubElement(publisher, "{" + TEI_NS + "}orgName")
        org_name1.text = "Paris Lodron Universität Salzburg"
        org_name2 = etree.SubElement(publisher, "{" + TEI_NS + "}orgName")
        org_name2.set("type", "project")
        org_name2.text = "Mittelhochdeutsche Begriffsdatenbank (MHDBDB)"

        # Add address
        address = etree.SubElement(publisher, "{" + TEI_NS + "}address")
        street = etree.SubElement(address, "{" + TEI_NS + "}street")
        street.text = "Erzabt-Klotz-Straße 1"
        post_code = etree.SubElement(address, "{" + TEI_NS + "}postCode")
        post_code.text = "5020"
        settlement = etree.SubElement(address, "{" + TEI_NS + "}settlement")
        settlement.text = "Salzburg"
        country = etree.SubElement(address, "{" + TEI_NS + "}country")
        country.text = "Österreich"

        # Add email and website
        email = etree.SubElement(publisher, "{" + TEI_NS + "}email")
        email.text = "mhdbdb@plus.ac.at"
        ptr = etree.SubElement(publisher, "{" + TEI_NS + "}ptr")
        ptr.set("target", "https://mhdbdb.plus.ac.at")

        # Add authority
        authority = etree.SubElement(pub_stmt, "{" + TEI_NS + "}authority")
        pers_name = etree.SubElement(authority, "{" + TEI_NS + "}persName")
        pers_name.set("role", "coordinator")
        forename = etree.SubElement(pers_name, "{" + TEI_NS + "}forename")
        forename.text = "Katharina"
        surname = etree.SubElement(pers_name, "{" + TEI_NS + "}surname")
        surname.text = "Zeppezauer-Wachauer"

        # Add availability
        availability = etree.SubElement(pub_stmt, "{" + TEI_NS + "}availability")
        licence = etree.SubElement(availability, "{" + TEI_NS + "}licence")
        licence.set("target", "https://creativecommons.org/licenses/by-nc-sa/3.0/at/")
        licence.text = "CC BY-NC-SA 3.0 AT"
        p = etree.SubElement(availability, "{" + TEI_NS + "}p")
        p.text = "Die Annotationen der MHDBDB stehen unter der Lizenz CC BY-NC-SA 3.0 AT. Die E-Texte selbst sind individuell ausgezeichnet."

        # Add date, idno and refs
        date = etree.SubElement(pub_stmt, "{" + TEI_NS + "}date")
        date.set("when", "2025")
        date.text = "2025"
        idno = etree.SubElement(pub_stmt, "{" + TEI_NS + "}idno")
        idno.set("type", "URI")
        idno.text = "https://mhdbdb.plus.ac.at"

        ref1 = etree.SubElement(pub_stmt, "{" + TEI_NS + "}ref")
        ref1.set("type", "history")
        ref1.set("target", "https://doi.org/10.25619/BmE20223203")
        ref1.text = "Zeppezauer-Wachauer, Katharina (2022): 50 Jahre Mittelhochdeutsche Begriffsdatenbank (MHDBDB)"

        ref2 = etree.SubElement(pub_stmt, "{" + TEI_NS + "}ref")
        ref2.set("type", "documentation")
        ref2.set("target", "https://doi.org/10.14220/mdge.2022.69.2.135")
        ref2.text = "Zeppezauer-Wachauer, Katharina (2022). Die Mittelhochdeutsche Begriffsdatenbank (MHDBDB): Rückschau auf 50 Jahre digitale Mediävistik"

        # 3. Create sourceDesc with msDesc structure
        source_desc = etree.SubElement(file_desc, "{" + TEI_NS + "}sourceDesc")

        # Create msDesc structure
        ms_desc = etree.SubElement(source_desc, "{" + TEI_NS + "}msDesc")
        ms_identifier = etree.SubElement(ms_desc, "{" + TEI_NS + "}msIdentifier")
        ms_identifier.set("corresp", f"works.xml#work_{work_id}")

        # Add sigle
        idno = etree.SubElement(ms_identifier, "{" + TEI_NS + "}idno")
        idno.set("type", "sigle")
        idno.text = sigle

        # Write enhanced file
        success = write_tei_file(root, output_file)
        if success:
            logger.info(f"Enhanced TEI header for {sigle}")

        return success
    except Exception as e:
        logger.error(f"Error enhancing TEI header: {str(e)}")
        return False


def update_tei_references(tei_file, output_file):
    """
    Update token references in TEI file to point to authority files and
    convert <seg type="token"> elements to <w> elements with properly formatted references
    """
    logger.info(f"Updating token references in {tei_file}")

    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(tei_file, parser)
        root = tree.getroot()

        # Find all token segments
        ns = {"tei": "http://www.tei-c.org/ns/1.0"}
        tokens = root.findall(".//tei:seg[@type='token']", ns)

        # Count of processed tokens
        processed = 0
        references_fixed = 0

        # Update references in each token and convert to <w> element
        for token in tokens:
            # Create new <w> element
            parent = token.getparent()
            w_elem = etree.Element("{" + TEI_NS + "}w")

            # Copy text content
            if token.text is not None:
                w_elem.text = token.text

            # Copy all attributes except type="token"
            for name, value in token.attrib.items():
                if not (name == 'type' and value == 'token'):
                    w_elem.set(name, value)

            # Update lemma reference first, as we'll need it for sense references
            lemma_id = None
            lemma_num = None
            if 'lemmaRef' in w_elem.attrib:
                lemma_ref = w_elem.attrib['lemmaRef']

                # Skip if already updated
                if not lemma_ref.startswith("lexicon.xml#"):
                    w_elem.attrib['lemmaRef'] = f"lexicon.xml#lemma_{lemma_ref}"
                    lemma_id = lemma_ref  # Store raw lemma ID
                else:
                    # Extract lemma ID from fully formed reference
                    if lemma_ref.startswith("lexicon.xml#lemma_"):
                        lemma_num = lemma_ref.split('#lemma_')[1]
                        lemma_id = lemma_num

            # Update meaning reference - now pointing to sense in lexicon.xml
            if 'meaningRef' in w_elem.attrib:
                sense_ref = w_elem.attrib['meaningRef']

                # Only process if not already pointing to a lemma-specific sense
                if not sense_ref.startswith("lexicon.xml#lemma_"):
                    references_fixed += 1

                    # Case 1: Already updated to lexicon but missing lemma prefix
                    if sense_ref.startswith("lexicon.xml#sense_"):
                        sense_num = sense_ref.split('#sense_')[1]

                        if lemma_id:
                            # Convert to proper lemma-based sense reference
                            w_elem.attrib['meaningRef'] = f"lexicon.xml#lemma_{lemma_id}_sense_{sense_num}"

                    # Case 2: Referencing concept file
                    elif sense_ref.startswith("concepts.xml#concept_"):
                        sense_num = sense_ref.split('#concept_')[1]

                        if lemma_id:
                            # Convert concept reference to lemma-based sense reference
                            w_elem.attrib['meaningRef'] = f"lexicon.xml#lemma_{lemma_id}_sense_{sense_num}"
                        else:
                            # No lemma available, use basic sense reference
                            w_elem.attrib['meaningRef'] = f"lexicon.xml#sense_{sense_num}"

                    # Case 3: Raw sense ID (not formatted yet)
                    else:
                        sense_num = sense_ref

                        if lemma_id:
                            # Create proper lemma-based sense reference
                            w_elem.attrib['meaningRef'] = f"lexicon.xml#lemma_{lemma_id}_sense_{sense_num}"
                        else:
                            # No lemma available, use basic sense reference
                            w_elem.attrib['meaningRef'] = f"lexicon.xml#sense_{sense_num}"

            # Update word reference
            if 'wordRef' in w_elem.attrib:
                word_id = w_elem.attrib['wordRef']
                # Skip if already updated
                if not word_id.startswith("types.xml#"):
                    w_elem.attrib['wordRef'] = f"types.xml#type_{word_id}"

            # Copy any child elements (though tokens shouldn't typically have children)
            for child in token:
                w_elem.append(copy.deepcopy(child))

            # Replace the token with the new <w> element
            parent.replace(token, w_elem)
            processed += 1

        # Write updated file
        success = write_tei_file(root, output_file)
        if success:
            logger.info(f"Updated token references and converted to <w> elements in {tei_file}")
            logger.info(f"Processed {processed} tokens and fixed {references_fixed} sense references")

        return processed
    except Exception as e:
        logger.error(f"Error updating references: {str(e)}")
        return 0


def process_text_files(input_dir, works_csv, persons_csv, output_dir):
    """
    Process only the TEI text files to enhance headers and update references,
    without recreating the authority files.
    """
    logger.info(f"Processing TEI files from {input_dir} to {output_dir}")

    # Use output directory directly instead of creating a texts subdirectory
    text_output_dir = output_dir
    os.makedirs(text_output_dir, exist_ok=True)

    # Process all TEI files
    file_count = 0
    skipped_count = 0

    try:
        tei_files = [f for f in os.listdir(input_dir) if f.endswith(".tei.xml")]
        logger.info(f"Found {len(tei_files)} TEI files to process")

        for filename in tei_files:
            logger.info(f"Processing {filename}...")
            input_file = os.path.join(input_dir, filename)

            # Create a temporary file for the intermediate step
            temp_file = os.path.join(output_dir, f"temp_{filename}")

            # Step 1: Enhance header
            success = enhance_tei_header(input_file, works_csv, persons_csv, temp_file)

            # Only proceed if enhancement was successful
            if success:
                # Step 2: Update references and convert seg to w
                final_file = os.path.join(text_output_dir, filename)
                update_tei_references(temp_file, final_file)

                # Remove the temporary file
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Could not remove temporary file {temp_file}: {str(e)}")

                file_count += 1
            else:
                logger.warning(f"Skipping {filename} due to missing work data")
                skipped_count += 1

        logger.info(f"Completed processing {file_count} TEI text files.")
        logger.info(f"Skipped {skipped_count} files due to missing work data.")
        logger.info(f"Enhanced files are in: {text_output_dir}")
        return file_count
    except Exception as e:
        logger.error(f"Error processing TEI files: {str(e)}")
        return 0


if __name__ == "__main__":
    # Setup command line argument parsing
    if len(sys.argv) == 1 or sys.argv[1] == "--help":
        print("MHDBDB TEI Migration Tool")
        print("\nUsage:")
        print("  Default (process all TEI files):")
        print("    python tei-transformation.py")

        print("\n  Process a single TEI file:")
        print("    python tei-transformation.py --file input.tei.xml [output.tei.xml]")

        print("\n  Generate authority files:")
        print("    python tei-transformation.py --lists all")
        print("    python tei-transformation.py --lists persons")
        print("    python tei-transformation.py --lists lexicon")
        print("    python tei-transformation.py --lists concepts")
        print("    python tei-transformation.py --lists genres")
        print("    python tei-transformation.py --lists names")
        print("    python tei-transformation.py --lists works")
        print("    python tei-transformation.py --lists types path/to/xml_dump.xml")

        print("\n  Change output directory:")
        print("    python tei-transformation.py --output output_dir")

        print("\n  Enable debug output:")
        print("    TEI_DEBUG=1 python tei-transformation.py")
        sys.exit(0)

    # Default paths
    input_dir = "./"  # Current directory, where the script is now
    csv_dir = "./lists"  # Lists subdirectory
    output_dir = "./output"  # Output directory

    # Check for output directory override
    if "--output" in sys.argv:
        output_idx = sys.argv.index("--output")
        if output_idx + 1 < len(sys.argv):
            output_dir = sys.argv[output_idx + 1]
            # Remove these arguments from processing
            sys.argv.pop(output_idx)
            sys.argv.pop(output_idx)

    # Create output directory
    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Output directory ensured: {output_dir}")
    except Exception as e:
        logger.error(f"Cannot create output directory {output_dir}: {str(e)}")
        sys.exit(1)

    # Handle a single file
    if len(sys.argv) > 1 and sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            logger.error("Missing input file path")
            sys.exit(1)

        input_file = sys.argv[2]

        # Determine output file
        if len(sys.argv) >= 4:
            output_file = sys.argv[3]
        else:
            # Use input filename with output directory
            output_file = os.path.join(output_dir, os.path.basename(input_file))

        # Create a temporary file for the intermediate step
        temp_file = os.path.join(output_dir, f"temp_{os.path.basename(input_file)}")

        # Files needed for processing
        works_csv = os.path.join(csv_dir, "works.csv")
        persons_csv = os.path.join(csv_dir, "persons.csv")

        logger.info(f"Processing single file: {input_file}")

        # Step 1: Enhance header
        success = enhance_tei_header(input_file, works_csv, persons_csv, temp_file)

        # Only proceed if enhancement was successful
        if success:
            # Step 2: Update references and convert seg to w
            update_tei_references(temp_file, output_file)
            logger.info(f"Successfully processed {input_file} to {output_file}")
        else:
            logger.error(f"Could not enhance header for {input_file}, possibly due to missing work data")

        # Remove the temporary file if it exists
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Could not remove temporary file {temp_file}: {str(e)}")

    # Generate authority files
    elif len(sys.argv) > 1 and sys.argv[1] == "--lists":
        if len(sys.argv) < 3:
            logger.error("Please specify which lists to generate (all, persons, lexicon, etc.)")
            sys.exit(1)

        list_type = sys.argv[2]

        if list_type == "all":
            logger.info("Generating all authority files...")
            create_persons_tei(
                os.path.join(csv_dir, "persons.csv"),
                os.path.join(output_dir, "persons.xml")
            )
            create_lexicon_tei(
                os.path.join(csv_dir, "lexicon.csv"),
                os.path.join(output_dir, "lexicon.xml")
            )
            create_concepts_tei(
                os.path.join(csv_dir, "concepts.csv"),
                os.path.join(output_dir, "concepts.xml")
            )
            create_genres_tei(
                os.path.join(csv_dir, "genres.csv"),
                os.path.join(output_dir, "genres.xml")
            )
            create_names_tei(
                os.path.join(csv_dir, "onomastic.csv"),
                os.path.join(output_dir, "names.xml")
            )
            create_works_tei(
                os.path.join(csv_dir, "works.csv"),
                os.path.join(output_dir, "works.xml"),
                os.path.join(csv_dir, "persons.csv")
            )
            logger.info(f"All authority files generated in {output_dir}")

        elif list_type == "persons":
            create_persons_tei(
                os.path.join(csv_dir, "persons.csv"),
                os.path.join(output_dir, "persons.xml")
            )

        elif list_type == "lexicon":
            create_lexicon_tei(
                os.path.join(csv_dir, "lexicon.csv"),
                os.path.join(output_dir, "lexicon.xml")
            )

        elif list_type == "concepts":
            create_concepts_tei(
                os.path.join(csv_dir, "concepts.csv"),
                os.path.join(output_dir, "concepts.xml")
            )

        elif list_type == "genres":
            create_genres_tei(
                os.path.join(csv_dir, "genres.csv"),
                os.path.join(output_dir, "genres.xml")
            )

        elif list_type == "names":
            create_names_tei(
                os.path.join(csv_dir, "onomastic.csv"),
                os.path.join(output_dir, "names.xml")
            )

        elif list_type == "works":
            create_works_tei(
                os.path.join(csv_dir, "works.csv"),
                os.path.join(output_dir, "works.xml"),
                os.path.join(csv_dir, "persons.csv")
            )

        elif list_type == "types":
            if len(sys.argv) < 4:
                logger.error("Error: Missing XML dump file path for types list generation")
                print("Usage: python tei-transformation.py --lists types path/to/xml_dump.xml")
                sys.exit(1)

            xml_dump_file = sys.argv[3]
            lexicon_file = os.path.join(output_dir, "lexicon.xml")
            types_output_file = os.path.join(output_dir, "types.xml")

            # Check if lexicon.xml exists, create it if not
            if not os.path.exists(lexicon_file):
                logger.info("lexicon.xml not found, creating it first...")
                create_lexicon_tei(
                    os.path.join(csv_dir, "lexicon.csv"),
                    lexicon_file
                )

            create_types_tei(xml_dump_file, lexicon_file, types_output_file)

        else:
            logger.error(f"Unknown list type: {list_type}")
            logger.error("Valid options: all, persons, lexicon, concepts, genres, names, works")
            sys.exit(1)

    # Default behavior: Process all TEI files
    else:
        works_csv = os.path.join(csv_dir, "works.csv")
        persons_csv = os.path.join(csv_dir, "persons.csv")

        logger.info(f"Processing all TEI files in {input_dir}...")
        logger.info(f"Output will be written to {output_dir}")

        # Process all TEI files
        process_text_files(input_dir, works_csv, persons_csv, output_dir)