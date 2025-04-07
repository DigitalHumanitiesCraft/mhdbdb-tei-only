#!/usr/bin/env python3
import csv
import xml.etree.ElementTree as ET
from lxml import etree
import os
import sys
import copy
from datetime import datetime

# Create output directory if it doesn't exist
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Define namespaces
TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"

# Register namespaces for pretty output
ET.register_namespace("", TEI_NS)
ET.register_namespace("xml", XML_NS)


def debug_csv(csv_file):
    """Print debug info about a CSV file"""
    print(f"Analyzing CSV file: {csv_file}")
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            # Try to determine delimiter from first line
            first_line = f.readline().strip()
            print(f"First line: {first_line}")

            if "\t" in first_line:
                delimiter = "\t"
            else:
                delimiter = ","
            print(f"Detected delimiter: '{delimiter}'")

            # Reset file pointer
            f.seek(0)

            # Read with csv.reader
            reader = csv.reader(f, delimiter=delimiter)
            header = next(reader)
            print(f"Header row (columns): {header}")

            # Print first data row if available
            try:
                first_row = next(reader)
                print(f"First data row: {first_row}")
            except StopIteration:
                print("No data rows found")
    except Exception as e:
        print(f"Error analyzing CSV: {e}")


def detect_delimiter(csv_file):
    """Auto-detect delimiter from CSV file"""
    with open(csv_file, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        if "\t" in first_line:
            return "\t"
        else:
            return ","


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
    tree_string = ET.tostring(tei, encoding="utf-8")
    parser = etree.XMLParser(remove_blank_text=True)
    parsed = etree.fromstring(tree_string, parser)
    pretty = etree.tostring(
        parsed, pretty_print=True, encoding="utf-8", xml_declaration=True
    )

    with open(output_file, "wb") as f:
        f.write(pretty)


def create_persons_tei(csv_file, output_file):
    """Transform persons CSV to TEI personography"""
    # Debug the CSV first
    debug_csv(csv_file)

    tei, body = create_tei_base("MHDBDB Person Registry")

    # Create listPerson element
    listPerson = ET.SubElement(body, "{" + TEI_NS + "}listPerson")

    # Dictionary to collect data for each person
    # Structure: {person_id: {field: [values]}}
    person_data = {}

    # To store all relations for later
    relations = []

    # Determine delimiter
    delimiter = detect_delimiter(csv_file)

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)

        for i, row in enumerate(reader):
            # For debugging, print the first row
            if i == 0:
                print(f"Processing first row: {row}")

            # Extract person ID
            if "personId" in row:
                person_id = row["personId"]
            elif "personURI" in row:
                # Extract ID from URI
                person_id = row["personURI"].split("/")[-1]
            else:
                print(f"Warning: No ID found for row {i+1}")
                continue

            # Remove "person_" prefix if already present to avoid doubling
            if person_id.startswith("person_"):
                person_id = person_id[7:]

            # Initialize person data if not yet seen
            if person_id not in person_data:
                person_data[person_id] = {
                    "preferredName": set(),
                    "labelDe": set(),
                    "labelEn": set(),
                    "gndId": set(),
                    "wikidataId": set(),
                    "associatedWorks": set(),
                }

            # Collect all values
            for field in person_data[person_id]:
                if field in row and row[field]:
                    if field == "associatedWorks" and "," in row[field]:
                        # Split comma-separated work IDs
                        for work_id in row[field].split(","):
                            person_data[person_id][field].add(work_id.strip())
                    else:
                        person_data[person_id][field].add(row[field])

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
                # Remove "work_" prefix if already present to avoid doubling
                if work_id.startswith("work_"):
                    work_id = work_id[5:]

                relations.append(
                    {
                        "name": "isAuthorOf",
                        "active": f"#person_{person_id}",
                        "passive": f"works.xml#work_{work_id.strip()}",
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
    write_tei_file(tei, output_file)

    print(f"Created TEI personography file: {output_file}")
    print(f"Processed {len(person_data)} unique persons")
    print(f"Added {len(relations)} work relations")


def create_lexicon_tei(csv_file, output_file):
    """Transform lemma data to TEI dictionary format based on actual data model"""
    # Debug the CSV first
    debug_csv(csv_file)

    tei, body = create_tei_base("MHDBDB Middle High German Lexicon")

    # Create entry list
    entries = ET.SubElement(body, "{" + TEI_NS + "}div")
    entries.set("type", "lexicon")

    # Dictionary to collect data for each lemma
    lemma_data = {}

    # Determine delimiter
    delimiter = detect_delimiter(csv_file)

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)

        for row in reader:
            if "lemmaId" not in row or not row["lemmaId"]:
                continue

            lemma_id = row["lemmaId"]

            # Remove "lemma_" prefix if already present to avoid doubling
            if lemma_id.startswith("lemma_"):
                lemma_id = lemma_id[6:]

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
                    if sense_id.startswith("sense_"):
                        sense_id = sense_id[6:]

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
                if concept.startswith("concept_"):
                    concept = concept[8:]

                ptr = ET.SubElement(sense, "{" + TEI_NS + "}ptr")
                ptr.set("target", f"concepts.xml#concept_{concept}")

    # Write to file
    write_tei_file(tei, output_file)

    print(f"Created TEI lexicon file: {output_file}")
    print(f"Processed {len(lemma_data)} unique lemmas")
    print(
        f"Number of lemmas with multiple parts of speech: {sum(1 for data in lemma_data.values() if len(data['pos_variants']) > 1)}"
    )


def create_concepts_tei(csv_file, output_file):
    """Transform concept data to TEI taxonomy format with correct TEI structure"""
    # Debug the CSV first
    debug_csv(csv_file)

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

    # Dictionary to collect data for each concept
    concept_data = {}
    delimiter = detect_delimiter(csv_file)

    # Collect all data
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            if "conceptId" not in row or not row["conceptId"]:
                continue

            concept_id = row["conceptId"]
            # Remove "concept_" prefix if already present
            if concept_id.startswith("concept_"):
                concept_id = concept_id[8:]

            # Initialize concept data if not yet seen
            if concept_id not in concept_data:
                concept_data[concept_id] = {
                    "prefLabelDe": set(),
                    "prefLabelEn": set(),
                    "altLabelDe": set(),
                    "altLabelEn": set(),
                    "broaderConcepts": set(),
                }

            # Collect text fields
            for field in ["prefLabelDe", "prefLabelEn", "altLabelDe", "altLabelEn"]:
                if field in row and row[field]:
                    concept_data[concept_id][field].add(row[field])

            # Process broader concepts
            if "broaderConcepts" in row and row["broaderConcepts"]:
                for broader in row["broaderConcepts"].split(","):
                    broader = broader.strip()
                    if broader:
                        # Remove "concept_" prefix if present
                        if broader.startswith("concept_"):
                            broader = broader[8:]
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
    write_tei_file(tei, output_file)

    print(f"Created TEI concepts taxonomy file: {output_file}")
    print(f"Processed {len(concept_data)} unique concepts")


def create_genres_tei(csv_file, output_file):
    """Transform genre data to TEI taxonomy format with correct TEI structure"""
    # Debug the CSV first
    debug_csv(csv_file)

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

    # Dictionary to collect data for each genre
    genre_data = {}
    delimiter = detect_delimiter(csv_file)

    # First pass: collect all data
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)

        for row in reader:
            if "genreId" not in row or not row["genreId"]:
                continue

            genre_id = row["genreId"]

            # Remove "genre_" prefix if already present
            if genre_id.startswith("genre_"):
                genre_id = genre_id[6:]

            # Initialize genre data if not yet seen
            if genre_id not in genre_data:
                genre_data[genre_id] = {
                    "labelDe": set(),
                }

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
    write_tei_file(tei, output_file)

    print(f"Created TEI genres taxonomy file: {output_file}")
    print(f"Processed {len(genre_data)} unique genres")


def create_names_tei(csv_file, output_file):
    """Transform onomastic data to TEI taxonomy format with correct TEI structure"""
    # Debug the CSV first
    debug_csv(csv_file)

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

    # Dictionary to collect data for each name
    name_data = {}

    # Determine delimiter
    delimiter = detect_delimiter(csv_file)

    # First pass: collect all data
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)

        for row in reader:
            if "nameConceptId" not in row or not row["nameConceptId"]:
                continue

            name_id = row["nameConceptId"]

            # Remove "name_" prefix if already present
            if name_id.startswith("name_"):
                name_id = name_id[5:]

            # Initialize name data if not yet seen
            if name_id not in name_data:
                name_data[name_id] = {
                    "prefLabelDe": set(),
                    "prefLabelEn": set(),
                    "broaderConcepts": set(),
                    "exactMatches": set(),
                    "closeMatches": set(),
                }

            # Collect text fields
            for field in ["prefLabelDe", "prefLabelEn"]:
                if field in row and row[field]:
                    name_data[name_id][field].add(row[field])

            # Process broader concepts
            if "broaderConcepts" in row and row["broaderConcepts"]:
                for broader in row["broaderConcepts"].split(","):
                    broader = broader.strip()
                    if broader:
                        # Remove "name_" prefix if present
                        if broader.startswith("name_"):
                            broader = broader[5:]
                        name_data[name_id]["broaderConcepts"].add(broader)

            # Process exact matches to concepts
            if "exactMatches" in row and row["exactMatches"]:
                for concept in row["exactMatches"].split(","):
                    concept = concept.strip()
                    if concept:
                        # Remove "concept_" prefix if present
                        if concept.startswith("concept_"):
                            concept = concept[8:]
                        name_data[name_id]["exactMatches"].add(concept)

            # Process close matches to concepts
            if "closeMatches" in row and row["closeMatches"]:
                for concept in row["closeMatches"].split(","):
                    concept = concept.strip()
                    if concept:
                        # Remove "concept_" prefix if present
                        if concept.startswith("concept_"):
                            concept = concept[8:]
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
    write_tei_file(tei, output_file)

    print(f"Created TEI names file: {output_file}")
    print(f"Processed {len(name_data)} unique name concepts")


def create_works_tei(csv_file, output_file, persons_file=None):
    """Transform works data to TEI format with proper handling of multiple sigles and titles"""
    # Debug the CSV first
    debug_csv(csv_file)

    tei, body = create_tei_base("MHDBDB Works Registry")

    # Create list of works
    listBibl = ET.SubElement(body, "{" + TEI_NS + "}listBibl")

    # Dictionary to collect data for each work
    # Structure: {work_id: {field: set()}}
    work_data = {}

    # Load person data if available
    persons = {}
    if persons_file and os.path.exists(persons_file):
        person_delimiter = detect_delimiter(persons_file)
        with open(persons_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=person_delimiter)
            for row in reader:
                person_id = row['personId'] if 'personId' in row else row['personURI'].split('/')[-1]
                # Remove "person_" prefix if already present
                if person_id.startswith("person_"):
                    person_id = person_id[7:]

                if 'preferredName' in row and row['preferredName']:
                    persons[person_id] = row['preferredName']

    # Determine delimiter
    delimiter = detect_delimiter(csv_file)

    # First pass: collect all data, grouped by work ID
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=delimiter)

        for row in reader:
            if 'workId' not in row or not row['workId']:
                continue

            work_id = row['workId'].strip()

            # Remove "work_" prefix if already present
            if work_id.startswith("work_"):
                work_id = work_id[5:]

            # Initialize work data if not yet seen
            if work_id not in work_data:
                work_data[work_id] = {
                    'sigle': set(),
                    'title': set(),
                    'authors': set(),
                    'handschriftencensus': set(),
                    'wikidata': set(),
                    'gnd': set()
                }

            # Add sigle if present
            if 'sigle' in row and row['sigle']:
                work_data[work_id]['sigle'].add(row['sigle'].strip())

            # Add title if present
            if 'title' in row and row['title']:
                work_data[work_id]['title'].add(row['title'].strip())

            # Add author if present
            if 'authorId' in row and row['authorId']:
                author_id = row['authorId'].strip()
                # Remove "person_" prefix if already present
                if author_id.startswith("person_"):
                    author_id = author_id[7:]
                work_data[work_id]['authors'].add(author_id)

            # Add external IDs if present
            if 'handschriftencensusId' in row and row['handschriftencensusId']:
                work_data[work_id]['handschriftencensus'].add(row['handschriftencensusId'].strip())

            if 'wikidataId' in row and row['wikidataId']:
                work_data[work_id]['wikidata'].add(row['wikidataId'].strip())

            if 'gndId' in row and row['gndId']:
                work_data[work_id]['gnd'].add(row['gndId'].strip())

    # Second pass: create bibliographic entries
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
    write_tei_file(tei, output_file)

    print(f"Created TEI works file: {output_file}")
    print(f"Processed {len(work_data)} unique works")
    print(f"Total number of sigles: {sum(len(data['sigle']) for data in work_data.values())}")
    print(f"Total number of titles: {sum(len(data['title']) for data in work_data.values())}")


def enhance_tei_header(tei_file, works_csv, persons_csv, output_file):
    """Add metadata from works and persons data to TEI file headers"""
    # Parse the existing TEI file
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(tei_file, parser)
    root = tree.getroot()

    # Extract the sigle from the file
    sigle = os.path.basename(tei_file).split('.')[0]

    # Find work data for this sigle
    work_id = None
    work_data = {}

    # Load works data
    works_delimiter = detect_delimiter(works_csv)
    with open(works_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=works_delimiter)
        for row in reader:
            # Match by sigle
            if row.get('sigle') and row.get('sigle').strip() == sigle:
                # Get work ID
                work_id = row['workId'].strip()
                if work_id.startswith("work_"):
                    work_id = work_id[5:]

                # Initialize work data if first match
                if not work_data:
                    work_data = {
                        'title': set(),
                        'sigle': set(),
                        'authors': set(),
                        'handschriftencensus': set(),
                        'wikidata': set(),
                        'gnd': set()
                    }

                # Now collect all data from this row
                if 'title' in row and row['title']:
                    work_data['title'].add(row['title'].strip())

                if 'sigle' in row and row['sigle']:
                    work_data['sigle'].add(row['sigle'].strip())

                if 'authorId' in row and row['authorId']:
                    author_id = row['authorId'].strip()
                    # Remove "person_" prefix if already present
                    if author_id.startswith("person_"):
                        author_id = author_id[7:]
                    work_data['authors'].add(author_id)

                if 'handschriftencensusId' in row and row['handschriftencensusId']:
                    work_data['handschriftencensus'].add(row['handschriftencensusId'].strip())

                if 'wikidataId' in row and row['wikidataId']:
                    work_data['wikidata'].add(row['wikidataId'].strip())

                if 'gndId' in row and row['gndId']:
                    work_data['gnd'].add(row['gndId'].strip())

                # Continue scanning to collect all data for this sigle
                # (Don't break after first match)

    if not work_id:
        print(f"Warning: No work data found for sigle {sigle}")
        return False

    # Now collect other rows with the same work_id to get complete data
    with open(works_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=works_delimiter)
        for row in reader:
            if row.get('workId') and row.get('workId').strip() == work_id:
                # Add any data not already collected
                if 'title' in row and row['title']:
                    work_data['title'].add(row['title'].strip())

                if 'sigle' in row and row['sigle'] and row['sigle'] != sigle:
                    work_data['sigle'].add(row['sigle'].strip())

                if 'authorId' in row and row['authorId']:
                    author_id = row['authorId'].strip()
                    # Remove "person_" prefix if already present
                    if author_id.startswith("person_"):
                        author_id = author_id[7:]
                    work_data['authors'].add(author_id)

                if 'handschriftencensusId' in row and row['handschriftencensusId']:
                    work_data['handschriftencensus'].add(row['handschriftencensusId'].strip())

                if 'wikidataId' in row and row['wikidataId']:
                    work_data['wikidata'].add(row['wikidataId'].strip())

                if 'gndId' in row and row['gndId']:
                    work_data['gnd'].add(row['gndId'].strip())

    # Load persons data
    persons_data = {}
    persons_delimiter = detect_delimiter(persons_csv)
    with open(persons_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=persons_delimiter)
        for row in reader:
            person_id = row['personId'] if 'personId' in row else row['personURI'].split('/')[-1]
            if person_id.startswith("person_"):
                person_id = person_id[7:]

            persons_data[person_id] = {
                'preferredName': row.get('preferredName', f"Person {person_id}")
            }

    # Find header element
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    header = root.find(".//tei:teiHeader", ns)

    if header is None:
        print(f"Error: No teiHeader found in {tei_file}")
        return False

    # Find fileDesc
    file_desc = header.find(".//tei:fileDesc", ns)
    if file_desc is None:
        file_desc = etree.SubElement(header, "{" + TEI_NS + "}fileDesc")

    # We'll recreate the fileDesc elements in the correct order
    # Save existing elements we want to preserve
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
            if author_id in persons_data:
                author_name = persons_data[author_id]['preferredName']

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
    pretty = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
    with open(output_file, 'wb') as f:
        f.write(pretty)

    print(f"Enhanced TEI header for {sigle}")
    return True


def update_tei_references(tei_file, output_file):
    """
    Update token references in TEI file to point to authority files and
    convert <seg type="token"> elements to <w> elements with properly formatted references
    """
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
    pretty = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
    with open(output_file, 'wb') as f:
        f.write(pretty)

    print(f"Updated token references and converted to <w> elements in {tei_file}")
    print(f"Processed {processed} tokens and fixed {references_fixed} sense references")
    return processed


def process_text_files(input_dir, works_csv, persons_csv, output_dir):
    """
    Process only the TEI text files to enhance headers and update references,
    without recreating the authority files.
    """
    # Use output directory directly instead of creating a texts subdirectory
    text_output_dir = output_dir
    os.makedirs(text_output_dir, exist_ok=True)

    # Process all TEI files
    file_count = 0
    skipped_count = 0
    for filename in os.listdir(input_dir):
        if filename.endswith(".tei.xml"):
            print(f"Processing {filename}...")
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
                os.remove(temp_file)

                file_count += 1
            else:
                print(f"Skipping {filename} due to missing work data")
                skipped_count += 1

    print(f"Completed processing {file_count} TEI text files.")
    print(f"Skipped {skipped_count} files due to missing work data.")
    print(f"Enhanced files are in: {text_output_dir}")


def process_all_files(input_dir, csv_dir, output_dir):
    """Process all input files to create a complete TEI-centric dataset"""
    # 1. Create authority files
    create_persons_tei(
        os.path.join(csv_dir, "persons.csv"), os.path.join(output_dir, "persons.xml")
    )

    create_lexicon_tei(
        os.path.join(csv_dir, "lexicon.csv"), os.path.join(output_dir, "lexicon.xml")
    )

    create_concepts_tei(
        os.path.join(csv_dir, "concepts.csv"), os.path.join(output_dir, "concepts.xml")
    )

    create_genres_tei(
        os.path.join(csv_dir, "genres.csv"), os.path.join(output_dir, "genres.xml")
    )

    create_names_tei(
        os.path.join(csv_dir, "onomastic.csv"), os.path.join(output_dir, "names.xml")
    )

    create_works_tei(
        os.path.join(csv_dir, "works.csv"),
        os.path.join(output_dir, "works.xml"),
        os.path.join(csv_dir, "persons.csv"),
    )

    # 2. Process all TEI files to enhance headers and update references
    tei_output_dir = os.path.join(output_dir, "texts")
    os.makedirs(tei_output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".tei.xml"):
            input_file = os.path.join(input_dir, filename)
            enhanced_file = os.path.join(tei_output_dir, filename)

            # First enhance header
            enhance_tei_header(
                input_file,
                os.path.join(csv_dir, "works.csv"),
                os.path.join(csv_dir, "persons.csv"),
                enhanced_file,
            )

            # Then update references
            final_file = enhanced_file  # Same file, will be overwritten
            update_tei_references(enhanced_file, final_file)


if __name__ == "__main__":
    # Setup command line argument parsing
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
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

        print("\n  Change output directory:")
        print("    python tei-transformation.py --output output_dir")
        sys.exit(0)

    # Default paths
    input_dir = "./"  # Current directory, where the script is now
    csv_dir = "./lists"  # Lists subdirectory
    output_dir = "./output"  # Output directory
    os.makedirs(output_dir, exist_ok=True)

    # Check for output directory override
    if "--output" in sys.argv:
        output_idx = sys.argv.index("--output")
        if output_idx + 1 < len(sys.argv):
            output_dir = sys.argv[output_idx + 1]
            # Remove these arguments from processing
            sys.argv.pop(output_idx)
            sys.argv.pop(output_idx)
            os.makedirs(output_dir, exist_ok=True)

    # Handle a single file
    if len(sys.argv) > 1 and sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("Error: Missing input file path")
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

        print(f"Processing single file: {input_file}")

        # Step 1: Enhance header
        success = enhance_tei_header(input_file, works_csv, persons_csv, temp_file)

        # Only proceed if enhancement was successful
        if success:
            # Step 2: Update references and convert seg to w
            update_tei_references(temp_file, output_file)
            print(f"Successfully processed {input_file} to {output_file}")
        else:
            print(f"Error: Could not enhance header for {input_file}, possibly due to missing work data")

        # Remove the temporary file if it exists
        if os.path.exists(temp_file):
            os.remove(temp_file)

    # Generate authority files
    elif len(sys.argv) > 1 and sys.argv[1] == "--lists":
        if len(sys.argv) < 3:
            print("Error: Please specify which lists to generate (all, persons, lexicon, etc.)")
            sys.exit(1)

        list_type = sys.argv[2]

        if list_type == "all":
            print(f"Generating all authority files...")
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
            print(f"All authority files generated in {output_dir}")

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

        else:
            print(f"Unknown list type: {list_type}")
            print("Valid options: all, persons, lexicon, concepts, genres, names, works")
            sys.exit(1)

    # Default behavior: Process all TEI files
    else:
        works_csv = os.path.join(csv_dir, "works.csv")
        persons_csv = os.path.join(csv_dir, "persons.csv")

        print(f"Processing all TEI files in {input_dir}...")
        print(f"Output will be written to {output_dir}")

        # Process all TEI files
        process_text_files(input_dir, works_csv, persons_csv, output_dir)
