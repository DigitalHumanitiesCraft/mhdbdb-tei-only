#!/usr/bin/env python3
import csv
import xml.etree.ElementTree as ET
from lxml import etree
import os
import sys
import copy
import logging
import urllib.parse, re
from datetime import datetime
from collections import defaultdict


# Define namespaces
TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"

# Global caches
_CSV_CACHE: dict[tuple[str, str | None], list | dict] = {}
_DELIM_CACHE: dict[str, str] = {}

# Register namespaces for pretty output
ET.register_namespace("", TEI_NS)
ET.register_namespace("xml", XML_NS)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("tei_transformer")

# Set DEBUG level through environment variable
if os.environ.get("TEI_DEBUG") == "1":
    logger.setLevel(logging.DEBUG)


def _local_id(uri: str) -> str:
    """Return the last path/fragment of a URI ('' if not a URI)."""
    if not uri:
        return ""
    tail = uri.rsplit("/", 1)[-1]
    return tail.split("#")[-1]


def detect_delimiter(csv_file: str, sample_size: int = 4096) -> str:
    """
    Detect the delimiter used in a CSV file.

    Priority:
      1·  csv.Sniffer().sniff() on a short sample (robust for quoted headers)
      2·  Heuristic: count occurrences of common delimiters in the *header line*
      3·  Default ','

    Returns the single‑character delimiter.
    """
    common_delims = [",", "\t", ";", "|"]
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            sample = f.read(sample_size)

            # --- 1. csv.Sniffer ------------------------------------------------
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters="".join(common_delims))
                if dialect.delimiter in common_delims:
                    logger.debug(
                        f"[detect_delimiter] Sniffer chose '{dialect.delimiter}' for {csv_file}"
                    )
                    return dialect.delimiter
            except csv.Error:
                # Sniffer gave up – fall through to heuristic
                pass

            # --- 2. simple count on header line --------------------------------
            header = sample.splitlines()[0] if sample else ""
            counts = {d: header.count(d) for d in common_delims}
            best = max(counts.values())
            if best > 0:
                # pick first delimiter with the max count
                for d in common_delims:
                    if counts[d] == best:
                        logger.debug(
                            f"[detect_delimiter] Heuristic chose '{d}' for {csv_file}"
                        )
                        return d

            # --- 3. fallback ----------------------------------------------------
            logger.warning(
                f"[detect_delimiter] Could not detect delimiter in {csv_file}; defaulting to ','"
            )
            return ","

    except Exception as e:
        logger.error(f"Error detecting delimiter in {csv_file}: {e}")
        return ","


def read_csv_data(csv_file: str, key_field: str | None = None):
    """
    Read *csv_file* and return:
      • list[dict]           when key_field is None
      • dict[key] -> list[...] when key_field is given

    The result is cached in _CSV_CACHE so subsequent calls with the
    same (csv_file, key_field) pair return a *deep copy* of the parsed
    data, avoiding redundant disk reads.
    """
    cache_key = (os.path.abspath(csv_file), key_field)
    if cache_key in _CSV_CACHE:
        logger.debug(f"[read_csv_data] Using cached rows for {csv_file} ({key_field})")
        return copy.deepcopy(_CSV_CACHE[cache_key])

    # -------- actually read from disk --------------------------------
    result = {} if key_field else []

    try:
        # reuse cached delimiter if known
        if csv_file in _DELIM_CACHE:
            delimiter = _DELIM_CACHE[csv_file]
        else:
            delimiter = detect_delimiter(csv_file)
            _DELIM_CACHE[csv_file] = delimiter

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=delimiter)

            if key_field:
                for row in reader:
                    if key_field in row and row[key_field]:
                        key = row[key_field].strip()
                        result.setdefault(key, []).append(row)
            else:
                result = list(reader)

        # store in cache (original object)
        _CSV_CACHE[cache_key] = result
        logger.debug(f"[read_csv_data] Parsed {len(result)} rows from {csv_file}")

        # hand back a copy so caller can mutate safely
        return copy.deepcopy(result)

    except Exception as e:
        logger.error(f"Error reading CSV {csv_file}: {e}", exc_info=True)
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
        id_str = id_str[len(strip_prefix) :]

    # Add prefix if needed
    if prefix and not id_str.startswith(prefix):
        id_str = f"{prefix}{id_str}"

    return id_str


def create_persons_tei(csv_file, output_file):
    """
    Transform persons CSV into a TEI personography.

    Supports either the old columns
        preferredName, labelDe, labelEn
    or a generic pair
        label / labelLang
    """
    logger.info(f"Creating TEI personography from {csv_file}")

    tei, body = create_tei_base("MHDBDB Person Registry")
    listPerson = ET.SubElement(body, f"{{{TEI_NS}}}listPerson")

    # in‑memory aggregation
    persons = defaultdict(
        lambda: {
            "preferred": set(),  # no language tag
            "labels": defaultdict(set),  # lang -> {names}
            "gnd": set(),
            "wikidata": set(),
            "works": set(),
        }
    )

    try:
        rows = read_csv_data(csv_file)

        for row in rows:
            pid_raw = row.get("personId") or _local_id(row.get("personURI"))
            if not pid_raw:
                continue
            pid = _local_id(pid_raw)

            # --- preferred name ---
            if row.get("preferredName"):
                persons[pid]["preferred"].add(row["preferredName"].strip())

            # --- language‑specific labels ---
            # legacy explicit columns
            if row.get("labelDe"):
                persons[pid]["labels"]["de"].add(row["labelDe"].strip())
            if row.get("labelEn"):
                persons[pid]["labels"]["en"].add(row["labelEn"].strip())

            # generic label / labelLang
            if row.get("label"):
                lang = (row.get("labelLang") or "").strip().lower()
                lang = lang if lang else "und"
                persons[pid]["labels"][lang].add(row["label"].strip())

            # --- external ids ---
            if row.get("gndId"):
                persons[pid]["gnd"].add(row["gndId"].strip())
            if row.get("wikidataId"):
                persons[pid]["wikidata"].add(row["wikidataId"].strip())

            # --- associated works ---
            if row.get("associatedWorks"):
                for wid in re.split(r"[;,]", row["associatedWorks"]):
                    wid = wid.strip()
                    if wid:
                        persons[pid]["works"].add(_local_id(wid))

        # ------------------------------------------------------------------
        # write TEI
        relations = []

        for pid, data in persons.items():
            person = ET.SubElement(listPerson, f"{{{TEI_NS}}}person")
            person.set(f"{{{XML_NS}}}id", normalize_id(pid, prefix="person_"))

            # preferredName – first of any preferred, else first German, else any
            pref = (
                next(iter(data["preferred"]))
                if data["preferred"]
                else (
                    next(iter(data["labels"]["de"]))
                    if data["labels"]["de"]
                    else next(iter(next(iter(data["labels"].values()))))
                )
            )

            ET.SubElement(person, f"{{{TEI_NS}}}persName", type="preferred").text = pref

            # alternative labels
            for lang, names in data["labels"].items():
                for n in names:
                    if n == pref:
                        continue
                    alt = ET.SubElement(
                        person, f"{{{TEI_NS}}}persName", type="alternative"
                    )
                    if lang != "und":
                        alt.set(f"{{{XML_NS}}}lang", lang)
                    alt.text = n

            # idnos
            for g in sorted(data["gnd"]):
                ET.SubElement(person, f"{{{TEI_NS}}}idno", type="GND").text = g
            for w in sorted(data["wikidata"]):
                ET.SubElement(person, f"{{{TEI_NS}}}idno", type="wikidata").text = w

            # note + relation list preparation
            if data["works"]:
                note = ET.SubElement(person, f"{{{TEI_NS}}}note", type="works")
                note.text = ",".join(sorted(data["works"]))
                for wid in data["works"]:
                    person_ref = f"#{normalize_id(pid, prefix='person_')}"
                    work_ref = f"works.xml#{normalize_id(wid, prefix='work_')}"
                    relations.append(("isAuthorOf", person_ref, work_ref))

        # relations section
        if relations:
            listRel = ET.SubElement(body, f"{{{TEI_NS}}}listRelation")
            for name, act, pas in relations:
                rel = ET.SubElement(
                    listRel, f"{{{TEI_NS}}}relation", name=name, active=act, passive=pas
                )

        return write_tei_file(tei, output_file)

    except Exception as e:
        logger.error(f"Error creating persons TEI file: {e}", exc_info=True)
        return False


def create_lexicon_tei(csv_file, output_file, textword_file=None):
    """Transform lemma data to TEI dictionary format with integrated word types via @ana"""
    logger.info(f"Creating TEI lexicon from {csv_file}")

    tei, body = create_tei_base("MHDBDB Middle High German Lexicon")

    # Create entry list
    entries = ET.SubElement(body, "{" + TEI_NS + "}div")
    entries.set("type", "lexicon")

    # Dictionary to collect data for each lemma
    lemma_data = {}

    # NEW: Build sense_id → [word_types] mapping from TEXTWORD.xml
    sense_to_types = defaultdict(list)
    if textword_file and os.path.exists(textword_file):
        logger.info(f"Processing word types from {textword_file}")
        type_to_sense = parse_xml_dump(textword_file)
        for word_type, sense_id in type_to_sense.items():
            sense_to_types[sense_id].append(word_type)
        logger.info(f"Found word types for {len(sense_to_types)} senses")

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

                # NEW: Add @ana with word types if available
                if sense_id in sense_to_types:
                    word_types = sense_to_types[sense_id]
                    ana_value = " ".join(f"#type_{wt}" for wt in sorted(word_types))
                    sense.set("ana", ana_value)

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
            # NEW: Report word type integration
            senses_with_types = sum(
                1
                for sense_id in sense_to_types
                if sense_id
                in [sid for ld in lemma_data.values() for sid in ld["senses"]]
            )
            logger.info(f"Integrated word types for {senses_with_types} senses")

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
        concept_data = defaultdict(
            lambda: {
                "prefLabelDe": set(),
                "prefLabelEn": set(),
                "altLabelDe": set(),
                "altLabelEn": set(),
                "broaderConcepts": set(),
            }
        )

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


# ----------------------------------------------------------------------


def create_genres_tei(csv_file, output_file):
    """NEW genre taxonomy builder, 2025 schema."""
    logger.info(f"Creating TEI genres taxonomy from {csv_file}")
    tei, body = create_tei_base("MHDBDB Text Type Taxonomy")
    try:
        # header scaffolding --------------------------------------------------
        enc = ET.SubElement(
            tei.find(f".//{{{TEI_NS}}}teiHeader"), f"{{{TEI_NS}}}encodingDesc"
        )
        classDecl = ET.SubElement(enc, f"{{{TEI_NS}}}classDecl")
        taxonomy = ET.SubElement(classDecl, f"{{{TEI_NS}}}taxonomy")
        taxonomy.set(f"{{{XML_NS}}}id", "mhdbdb-genres")
        ET.SubElement(taxonomy, f"{{{TEI_NS}}}desc").text = (
            "Text type taxonomy of the Middle High German Database"
        )

        # collect rows -------------------------------------------------------
        genre = defaultdict(
            lambda: {
                "labels": defaultdict(list),  # lang -> list[str]
                "broaders": set(),
            }
        )
        for row in read_csv_data(csv_file):
            cid = _local_id(row.get("conceptId"))
            if not cid:
                continue
            lbl = (row.get("conceptLabel") or "").strip()
            lang = (row.get("conceptLang") or "").strip()
            if lbl and lbl not in genre[cid]["labels"][lang]:
                genre[cid]["labels"][lang].append(lbl)
            bro = _local_id(row.get("broaderId"))
            if bro:
                genre[cid]["broaders"].add(bro)

        # write TEI ----------------------------------------------------------
        for cid, data in genre.items():
            cat = ET.SubElement(taxonomy, f"{{{TEI_NS}}}category")
            cat.set(f"{{{XML_NS}}}id", f"genre_{cid}")
            catDesc = ET.SubElement(cat, f"{{{TEI_NS}}}catDesc")

            # terms
            for lang, labels in data["labels"].items():
                if not labels:
                    continue
                pref = labels[0]
                term = ET.SubElement(catDesc, f"{{{TEI_NS}}}term")
                term.set(f"{{{XML_NS}}}lang", lang)
                term.text = pref
                for syn in labels[1:]:
                    t = ET.SubElement(catDesc, f"{{{TEI_NS}}}term")
                    t.set(f"{{{XML_NS}}}lang", lang)
                    t.set("type", "alternative")
                    t.text = syn

            # broader links
            for bro in sorted(data["broaders"]):
                ptr = ET.SubElement(catDesc, f"{{{TEI_NS}}}ptr")
                ptr.set("type", "broader")
                ptr.set("target", f"#genre_{bro}")

        return write_tei_file(tei, output_file)

    except Exception as e:
        logger.error(f"Error creating genres TEI file: {str(e)}")
        return False


# ----------------------------------------------------------------------


def create_works_tei(csv_file, output_file, persons_file=None, genres_csv=None):
    """Build works.xml from 2025 CSV; no duplicate titles or genre <ref>s."""
    logger.info(f"Creating TEI works registry from {csv_file}")

    tei, body = create_tei_base("MHDBDB Works Registry")
    listBibl = ET.SubElement(body, f"{{{TEI_NS}}}listBibl")

    try:
        # ------------------------------------------------------------------ #
        # 0) genre lookup (concept → labels)
        genre_lookup = defaultdict(lambda: defaultdict(set))  # gid → lang → {labels}
        if genres_csv and os.path.exists(genres_csv):
            for g in read_csv_data(genres_csv):
                gid = _local_id(g.get("conceptId"))
                lang = (g.get("conceptLang") or "").strip()
                lbl = (g.get("conceptLabel") or "").strip()
                if gid and lbl:
                    genre_lookup[gid][lang].add(lbl)

        # 1) person names
        persons = {}
        if persons_file and os.path.exists(persons_file):
            for row in read_csv_data(persons_file):
                pid = _local_id(row.get("personId") or row.get("personURI"))
                if pid and row.get("preferredName"):
                    persons[pid] = row["preferredName"]

        # 2) collect works
        work = defaultdict(
            lambda: {
                "uri": None,
                "titles": defaultdict(set),  # lang -> {title}
                "sigles": set(),
                "authors": set(),
                "wikidata": set(),
                "handschriftencensus": set(),
                "gnd": set(),
                "genres": defaultdict(  # role -> gid -> lang -> {label}
                    lambda: defaultdict(lambda: defaultdict(set))
                ),
                "editions": set(),  # {(title, place, agent, date)}
            }
        )

        for row in read_csv_data(csv_file):
            wid_uri = row.get("id") or ""
            wid = _local_id(wid_uri)
            if not wid:
                continue
            d = work[wid]
            d["uri"] = wid_uri

            # ----- titles -----
            title = (row.get("label") or "").strip()
            lang_exp = (row.get("labelLang") or "").strip()
            if title:
                lang = lang_exp or (
                    "en" if re.fullmatch(r"[A-Za-z0-9 ,.'-]+", title) else "de"
                )
                if not any(title in s for s in d["titles"].values()):
                    d["titles"][lang].add(title)

            # ----- sigle -----
            if row.get("instance"):
                d["sigles"].add(_local_id(row["instance"]))

            # ----- authors -----
            if row.get("authorId"):
                d["authors"].add(_local_id(row["authorId"]))

            # ----- sameAs -----
            same = row.get("sameAs") or ""
            host = urllib.parse.urlparse(same).hostname or ""
            if "wikidata.org" in host:
                d["wikidata"].add(same)
            elif "handschriftencensus" in host:
                d["handschriftencensus"].add(same)
            elif "d-nb.info" in host or "gnd" in host:
                d["gnd"].add(same)

            # ----- genres -----
            for role, gid_col, lbl_col, lang_col in (
                ("main", "genreForm", "genreFormLabel", "genreFormLabelLang"),
                (
                    "parent",
                    "genreFormMainParent",
                    "genreFormMainParentLabel",
                    "genreParentLabelLang",
                ),
            ):
                gid = _local_id(row.get(gid_col))
                # Strip c_ prefix if present to match genres.xml format
                if gid and gid.startswith("c_"):
                    gid = gid[2:]  # Remove "c_" prefix
                lbl = (row.get(lbl_col) or "").strip()
                lang = (row.get(lang_col) or "").strip()
                if gid:
                    if lbl:
                        if not lang:
                            lang = (
                                "en"
                                if re.fullmatch(r"[A-Za-z0-9 ,.'-]+", lbl)
                                else "de"
                            )
                        d["genres"][role][gid][lang].add(lbl)

            # ----- editions -----
            ed = tuple(
                (row.get(c) or "").strip()
                for c in ("bibTitle", "bibPlace", "bibAgent", "bibDate")
            )
            if any(ed):
                d["editions"].add(ed)

        # ------------------------------------------------------------------ #
        # 3) write TEI
        for wid, d in work.items():
            bibl = ET.SubElement(listBibl, f"{{{TEI_NS}}}bibl")
            bibl.set(f"{{{XML_NS}}}id", wid)

            for lang, titles in d["titles"].items():
                for t in sorted(titles):
                    el = ET.SubElement(bibl, f"{{{TEI_NS}}}title")
                    el.set(f"{{{XML_NS}}}lang", lang)
                    el.text = t

            for sig in sorted(d["sigles"]):
                idno = ET.SubElement(bibl, f"{{{TEI_NS}}}idno")
                idno.set("type", "sigle")
                idno.text = sig

            # ----- genre refs -----
            for role in ("main", "parent"):
                for gid in d["genres"][role]:
                    # augment with lookup terms
                    for lang, labels in genre_lookup[gid].items():
                        d["genres"][role][gid][lang].update(labels)

                emitted = set()  # (lang, label, role)
                for gid, langs in d["genres"][role].items():
                    target = f"genres.xml#genre_{gid}"
                    for lang, labels in langs.items():
                        for lbl in sorted(labels):
                            key = (lang, lbl, role)
                            if key in emitted:
                                continue
                            emitted.add(key)

                            ref = ET.SubElement(bibl, f"{{{TEI_NS}}}ref")
                            ref.set("target", target)
                            ref.set(f"{{{XML_NS}}}lang", lang)
                            if role == "parent":
                                ref.set("type", "parent")
                            # preferred label = first time this (lang,role) appears
                            if not any(
                                r.get("n") == "prefLabel"
                                and r.get(f"{{{XML_NS}}}lang") == lang
                                and (role == "parent") == (r.get("type") == "parent")
                                for r in bibl.findall(f"{{{TEI_NS}}}ref")
                            ):
                                ref.set("n", "prefLabel")
                            ref.text = lbl

            # ----- idnos (excluding URI type) -----
            for col, tp in (
                (d["wikidata"], "wikidata"),
                (d["handschriftencensus"], "handschriftencensus"),
                (d["gnd"], "gnd"),
            ):
                for uri in sorted(col):
                    el = ET.SubElement(bibl, f"{{{TEI_NS}}}idno")
                    el.set("type", tp)
                    el.text = uri

            # ----- authors -----
            for aid in sorted(d["authors"]):
                a = ET.SubElement(bibl, f"{{{TEI_NS}}}author")
                a.set("ref", f"persons.xml#{aid}")
                if aid in persons:
                    a.text = persons[aid]

            # ----- editions -----
            for title, place, agent, date_ in sorted(d["editions"]):
                ed = ET.SubElement(bibl, f"{{{TEI_NS}}}bibl")
                ed.set("type", "edition")
                if title:
                    ET.SubElement(ed, f"{{{TEI_NS}}}title").text = title
                if place:
                    ET.SubElement(ed, f"{{{TEI_NS}}}pubPlace").text = place
                if agent:
                    ET.SubElement(ed, f"{{{TEI_NS}}}publisher").text = agent
                if date_:
                    dt = ET.SubElement(ed, f"{{{TEI_NS}}}date")
                    dt.set("when", date_)
                    dt.text = date_

        return write_tei_file(tei, output_file)

    except Exception as e:
        logger.error(f"Error creating works TEI file: {str(e)}")
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
        name_data = defaultdict(
            lambda: {
                "prefLabelDe": set(),
                "prefLabelEn": set(),
                "broaderConcepts": set(),
                "exactMatches": set(),
                "closeMatches": set(),
            }
        )

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


def parse_xml_dump(xml_dump_file):
    """Parse the XML dump to extract word type to sense mappings"""
    type_to_sense = {}

    try:
        # Create a parser that ignores DTD declarations
        parser = etree.XMLParser(
            dtd_validation=False, load_dtd=False, resolve_entities=False
        )

        # Parse the full file (safer for this specific XML format)
        tree = etree.parse(xml_dump_file, parser)

        # Find all DATA_RECORD elements
        for record in tree.findall(".//DATA_RECORD"):
            word_elem = record.find("WORD")
            meaning_elem = record.find("MEANING")

            if (
                word_elem is not None
                and word_elem.text
                and meaning_elem is not None
                and meaning_elem.text
            ):
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


def enhance_tei_header_from_xml(tei_file, output_file, authority_dir="./lists/output"):
    """
    Enhanced TEI header generation reading directly from authority XML files.
    Creates comprehensive headers matching the manual template standard.
    """
    logger.info(f"Enhancing TEI header from XML authorities for {tei_file}")

    try:
        # Parse TEI file
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(tei_file, parser)
        root = tree.getroot()
        ns = {"tei": TEI_NS}

        sigle = os.path.basename(tei_file).split(".")[0]
        logger.debug(f"Extracted sigle: {sigle}")

        # Add xml:id to root TEI element
        root.set(f"{{{XML_NS}}}id", sigle)

        # Load authority XML files
        def load_authority_xml(filename):
            filepath = os.path.join(authority_dir, filename)
            if os.path.exists(filepath):
                return etree.parse(filepath)
            return None

        works_xml = load_authority_xml("works.xml")
        persons_xml = load_authority_xml("persons.xml")
        genres_xml = load_authority_xml("genres.xml")

        # Find work data by sigle
        work_data = None
        work_id_local = None
        if works_xml is not None:
            # Look for work with matching sigle
            for bibl in works_xml.findall(f".//{{{TEI_NS}}}bibl"):
                sigle_elems = bibl.findall(
                    f".//{{{TEI_NS}}}idno[@type='sigle']"
                )  # Find ALL sigles
                for sigle_elem in sigle_elems:  # Check each sigle
                    if sigle_elem is not None and sigle_elem.text == sigle:
                        work_data = bibl
                        work_id_local = bibl.get(f"{{{XML_NS}}}id", "")
                        break
                if work_data is not None:  # Break outer loop if found
                    break

        if work_data is None:
            logger.warning(f"No work found with sigle={sigle} in works.xml")
            return False

        # Extract work metadata
        work_title = ""
        title_elem = work_data.find(f".//{{{TEI_NS}}}title")
        if title_elem is not None:
            work_title = title_elem.text or sigle

        # Get authors
        work_authors = []
        for author in work_data.findall(f".//{{{TEI_NS}}}author"):
            ref = author.get("ref", "")
            if ref.startswith("persons.xml#"):
                person_id = ref.split("#")[1]
                author_name = author.text or ""
                work_authors.append((person_id, author_name))

        # Get genres
        work_genres = []
        for ref in work_data.findall(f".//{{{TEI_NS}}}ref"):
            target = ref.get("target", "")
            if target.startswith("genres.xml#"):
                genre_id = target.split("#")[1]
                genre_label = ref.text or ""
                genre_lang = ref.get(f"{{{XML_NS}}}lang", "de")
                is_parent = ref.get("type") == "parent"
                is_preferred = ref.get("n") == "prefLabel"
                work_genres.append(
                    (genre_id, genre_label, genre_lang, is_parent, is_preferred)
                )

        # Get edition info
        edition_data = {}
        edition_bibl = work_data.find(f".//{{{TEI_NS}}}bibl[@type='edition']")
        if edition_bibl is not None:
            title_ed = edition_bibl.find(f".//{{{TEI_NS}}}title")
            if title_ed is not None:
                edition_data["title"] = title_ed.text

            place_ed = edition_bibl.find(f".//{{{TEI_NS}}}pubPlace")
            if place_ed is not None:
                edition_data["place"] = place_ed.text

            pub_ed = edition_bibl.find(f".//{{{TEI_NS}}}publisher")
            if pub_ed is not None:
                edition_data["publisher"] = pub_ed.text

            date_ed = edition_bibl.find(f".//{{{TEI_NS}}}date")
            if date_ed is not None:
                edition_data["date"] = date_ed.text
                edition_data["when"] = date_ed.get("when", date_ed.text)

            # Edition authors
            edition_data["authors"] = []
            for auth_ed in edition_bibl.findall(f".//{{{TEI_NS}}}author"):
                if auth_ed.text:
                    edition_data["authors"].append(auth_ed.text)

        # Clear existing header and rebuild
        header = root.find(".//tei:teiHeader", ns)
        if header is None:
            header = etree.SubElement(root, f"{{{TEI_NS}}}teiHeader")
        header.clear()

        # ================================================================
        # 1. fileDesc
        # ================================================================
        fileDesc = etree.SubElement(header, f"{{{TEI_NS}}}fileDesc")

        # titleStmt
        titleStmt = etree.SubElement(fileDesc, f"{{{TEI_NS}}}titleStmt")
        title_el = etree.SubElement(titleStmt, f"{{{TEI_NS}}}title")
        title_el.text = work_title

        # Authors with internal references for profileDesc
        for person_id, author_name in work_authors:
            auth = etree.SubElement(titleStmt, f"{{{TEI_NS}}}author")
            auth.set("ref", f"#{person_id}")
            if author_name:
                auth.text = author_name

        # Responsibility statement
        respStmt = etree.SubElement(titleStmt, f"{{{TEI_NS}}}respStmt")
        resp = etree.SubElement(respStmt, f"{{{TEI_NS}}}resp")
        resp.text = (
            "digitale Zusammenführung, Annotation und semantische Klassifikation"
        )
        name = etree.SubElement(respStmt, f"{{{TEI_NS}}}name")
        name.set("ref", "https://mhdbdb.plus.ac.at")
        name.set(f"{{{XML_NS}}}lang", "de")
        name.text = "Mittelhochdeutsche Begriffsdatenbank (MHDBDB)"

        # Enhanced publicationStmt
        pubStmt = etree.SubElement(fileDesc, f"{{{TEI_NS}}}publicationStmt")

        # Publisher with structured info
        publisher = etree.SubElement(pubStmt, f"{{{TEI_NS}}}publisher")

        orgName1 = etree.SubElement(publisher, f"{{{TEI_NS}}}orgName")
        orgName1.text = "Mittelhochdeutsche Begriffsdatenbank (MHDBDB)"

        orgName2 = etree.SubElement(publisher, f"{{{TEI_NS}}}orgName")
        orgName2.text = "Paris Lodron Universität Salzburg"

        # Structured address
        address = etree.SubElement(publisher, f"{{{TEI_NS}}}address")
        etree.SubElement(address, f"{{{TEI_NS}}}street").text = "Erzabt-Klotz-Straße 1"
        etree.SubElement(address, f"{{{TEI_NS}}}postCode").text = "5020"
        etree.SubElement(address, f"{{{TEI_NS}}}settlement").text = "Salzburg"
        etree.SubElement(address, f"{{{TEI_NS}}}country").text = "Österreich"

        etree.SubElement(publisher, f"{{{TEI_NS}}}email").text = "mhdbdb@plus.ac.at"
        ptr = etree.SubElement(publisher, f"{{{TEI_NS}}}ptr")
        ptr.set("target", "https://mhdbdb.plus.ac.at")

        # Authority
        authority = etree.SubElement(pubStmt, f"{{{TEI_NS}}}authority")
        persName = etree.SubElement(authority, f"{{{TEI_NS}}}persName")
        persName.set("role", "coordinator")
        etree.SubElement(persName, f"{{{TEI_NS}}}forename").text = "Katharina"
        etree.SubElement(persName, f"{{{TEI_NS}}}surname").text = "Zeppezauer-Wachauer"

        # Availability and licensing
        availability = etree.SubElement(pubStmt, f"{{{TEI_NS}}}availability")
        licence = etree.SubElement(availability, f"{{{TEI_NS}}}licence")
        licence.set("target", "https://creativecommons.org/licenses/by-nc-sa/3.0/at/")
        licence.text = "CC BY-NC-SA 3.0 AT"

        p = etree.SubElement(availability, f"{{{TEI_NS}}}p")
        p.text = (
            "Die semantischen Annotationen stehen unter der Lizenz CC BY-NC-SA 3.0 AT. "
            "Die zugrunde liegenden E-Texte stammen aus unterschiedlichen Editionen und "
            "unterliegen je nach Quelle eigenen rechtlichen Bedingungen. Bitte beachten "
            "Sie die jeweiligen Angaben im Quellenverzeichnis."
        )

        # Date
        date_el = etree.SubElement(pubStmt, f"{{{TEI_NS}}}date")
        date_el.set("when", "2025")
        date_el.text = "2025"

        # References
        ref1 = etree.SubElement(pubStmt, f"{{{TEI_NS}}}ref")
        ref1.set("type", "history")
        ref1.set("target", "https://doi.org/10.25619/BmE20223203")
        ref1.text = (
            "Zeppezauer-Wachauer, Katharina (2022): 50 Jahre Mittelhochdeutsche "
            "Begriffsdatenbank (MHDBDB)"
        )

        ref2 = etree.SubElement(pubStmt, f"{{{TEI_NS}}}ref")
        ref2.set("type", "documentation")
        ref2.set("target", "https://doi.org/10.14220/mdge.2022.69.2.135")
        ref2.text = (
            "Zeppezauer-Wachauer, Katharina (2022). Die Mittelhochdeutsche "
            "Begriffsdatenbank (MHDBDB): Rückschau auf 50 Jahre digitale Mediävistik"
        )

        # Enhanced sourceDesc
        sourceDesc = etree.SubElement(fileDesc, f"{{{TEI_NS}}}sourceDesc")
        msDesc = etree.SubElement(sourceDesc, f"{{{TEI_NS}}}msDesc")
        msId = etree.SubElement(msDesc, f"{{{TEI_NS}}}msIdentifier")
        msId.set("corresp", f"works.xml#{work_id_local}")

        idno_sigle = etree.SubElement(msId, f"{{{TEI_NS}}}idno")
        idno_sigle.set("type", "sigle")
        idno_sigle.text = sigle

        # Add msName
        msName = etree.SubElement(msId, f"{{{TEI_NS}}}msName")
        msName.text = work_title

        # Edition bibliography if available
        if edition_data:
            additional = etree.SubElement(msDesc, f"{{{TEI_NS}}}additional")
            listBibl = etree.SubElement(additional, f"{{{TEI_NS}}}listBibl")
            bibl = etree.SubElement(listBibl, f"{{{TEI_NS}}}bibl")
            bibl.set("type", "edition")

            # Edition authors
            for auth_name in edition_data.get("authors", []):
                etree.SubElement(bibl, f"{{{TEI_NS}}}author").text = auth_name

            # Edition details
            if "title" in edition_data:
                etree.SubElement(bibl, f"{{{TEI_NS}}}title").text = edition_data[
                    "title"
                ]
            if "place" in edition_data:
                etree.SubElement(bibl, f"{{{TEI_NS}}}pubPlace").text = edition_data[
                    "place"
                ]
            if "publisher" in edition_data:
                etree.SubElement(bibl, f"{{{TEI_NS}}}publisher").text = edition_data[
                    "publisher"
                ]
            if "date" in edition_data:
                date_ed = etree.SubElement(bibl, f"{{{TEI_NS}}}date")
                if "when" in edition_data:
                    date_ed.set("when", edition_data["when"])
                date_ed.text = edition_data["date"]

        # ================================================================
        # 2. encodingDesc
        # ================================================================
        encodingDesc = etree.SubElement(header, f"{{{TEI_NS}}}encodingDesc")

        # Project description
        projectDesc = etree.SubElement(encodingDesc, f"{{{TEI_NS}}}projectDesc")

        p_de = etree.SubElement(projectDesc, f"{{{TEI_NS}}}p")
        p_de.set(f"{{{XML_NS}}}lang", "de")
        p_de.text = (
            "Die Annotationen der MHDBDB basieren auf kontrollierten Vokabularen "
            "und domänenspezifischen Ontologien. Hierzu zählen das auf SKOS strukturierte "
            "Begriffssystem mit semantischen Polyhierarchien, ein eigenständiges Onomastikon "
            "zur systematischen Erfassung von Eigennamen sowie eine umfassende "
            "Textreihentypologie mit über 600 Gattungsbezeichnungen. Diese Komponenten "
            "gewährleisten eine konsistente semantische Auszeichnung und fördern die "
            "Interoperabilität im Sinne der FAIR-Prinzipien."
        )

        p_en = etree.SubElement(projectDesc, f"{{{TEI_NS}}}p")
        p_en.set(f"{{{XML_NS}}}lang", "en")
        p_en.text = (
            "The annotations of the MHDBDB are based on controlled vocabularies "
            "and domain-specific ontologies. These include a SKOS-structured conceptual "
            "system with semantic polyhierarchies, a dedicated onomasticon for the systematic "
            "encoding of proper names, and a comprehensive typology of text series "
            "encompassing more than 600 genre designations. These components ensure "
            "consistent semantic markup and promote interoperability in line with FAIR "
            "principles."
        )

        # Genre taxonomy in classDecl
        classDecl = etree.SubElement(encodingDesc, f"{{{TEI_NS}}}classDecl")
        taxonomy = etree.SubElement(classDecl, f"{{{TEI_NS}}}taxonomy")
        taxonomy.set(f"{{{XML_NS}}}id", "genres")

        bibl_tax = etree.SubElement(taxonomy, f"{{{TEI_NS}}}bibl")
        bibl_tax.text = "Genreklassifikation gemäß der Textreihentypologie "
        ptr_tax = etree.SubElement(bibl_tax, f"{{{TEI_NS}}}ptr")
        ptr_tax.set("target", "https://www.mhdbdb.sbg.ac.at/textreihen")

        # Add relevant genres for this work from genres.xml
        if genres_xml is not None:
            genre_ids = set()
            for (
                genre_id,
                genre_label,
                genre_lang,
                is_parent,
                is_preferred,
            ) in work_genres:
                genre_ids.add(genre_id)

            # Find categories in genres.xml that match our work's genres
            for category in genres_xml.findall(f".//{{{TEI_NS}}}category"):
                cat_id = category.get(f"{{{XML_NS}}}id", "")

                if cat_id in genre_ids:
                    # Copy the category structure
                    new_category = etree.SubElement(taxonomy, f"{{{TEI_NS}}}category")
                    new_category.set(f"{{{XML_NS}}}id", cat_id)

                    # Check if this is a parent genre
                    is_parent_genre = any(
                        is_parent
                        for gid, _, _, is_parent, _ in work_genres
                        if gid == cat_id
                    )
                    if is_parent_genre:
                        new_category.set("ana", "parent")

                    # Add glosses from genres.xml
                    catDesc = category.find(f".//{{{TEI_NS}}}catDesc")
                    if catDesc is not None:
                        for term in catDesc.findall(f".//{{{TEI_NS}}}term"):
                            gloss = etree.SubElement(new_category, f"{{{TEI_NS}}}gloss")
                            lang = term.get(f"{{{XML_NS}}}lang", "de")
                            gloss.set(f"{{{XML_NS}}}lang", lang)
                            gloss.text = term.text

        # ================================================================
        # 3. profileDesc
        # ================================================================
        profileDesc = etree.SubElement(header, f"{{{TEI_NS}}}profileDesc")
        particDesc = etree.SubElement(profileDesc, f"{{{TEI_NS}}}particDesc")
        listPerson = etree.SubElement(particDesc, f"{{{TEI_NS}}}listPerson")

        # Add person details from persons.xml
        if persons_xml is not None:
            for person_id, author_name in work_authors:
                # Find person in persons.xml
                person_elem = persons_xml.find(
                    f".//{{{TEI_NS}}}person[@{{{XML_NS}}}id='{person_id}']"
                )
                if person_elem is not None:
                    # Copy person structure
                    new_person = etree.SubElement(listPerson, f"{{{TEI_NS}}}person")
                    new_person.set(f"{{{XML_NS}}}id", person_id)

                    # Copy all child elements
                    for child in person_elem:
                        new_person.append(copy.deepcopy(child))

        # ================================================================
        # 4. revisionDesc
        # ================================================================
        revisionDesc = etree.SubElement(header, f"{{{TEI_NS}}}revisionDesc")
        change = etree.SubElement(revisionDesc, f"{{{TEI_NS}}}change")
        change.set("when", datetime.now().strftime("%Y-%m-%d"))
        change.set("who", "#editor")
        change.text = (
            f"Version 1.0 ({datetime.now().strftime('%d.%m.%Y')}): "
            "Ergänzt um Editionsangaben, Ontologieverweise, Rollenkennzeichnung der "
            "Editor:innen, Klassifikationen, URI sowie GND- und Wikidata-Verlinkung "
            "des Autors."
        )

        return write_tei_file(root, output_file)

    except Exception as e:
        logger.error(f"Error enhancing TEI header from XML: {str(e)}", exc_info=True)
        return False


def process_text_files_with_xml_authorities(
    input_dir, output_dir, authority_dir="./lists/output"
):
    """
    Process TEI files using XML authority files instead of CSV sources.
    """
    logger.info(f"Processing TEI files from {input_dir} to {output_dir}")
    logger.info(f"Using authority files from {authority_dir}")

    text_output_dir = output_dir
    os.makedirs(text_output_dir, exist_ok=True)

    file_count = 0
    skipped_count = 0

    try:
        tei_files = [f for f in os.listdir(input_dir) if f.endswith(".tei.xml")]
        logger.info(f"Found {len(tei_files)} TEI files to process")

        for filename in tei_files:
            logger.info(f"Processing {filename}...")
            input_file = os.path.join(input_dir, filename)
            temp_file = os.path.join(output_dir, f"temp_{filename}")

            # Step 1: Enhance header from XML authorities
            success = enhance_tei_header_from_xml(input_file, temp_file, authority_dir)

            if success:
                # Step 2: Update references and convert seg to w
                final_file = os.path.join(text_output_dir, filename)
                update_tei_references(temp_file, final_file, authority_dir)

                # Remove temp file
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Could not remove temp file {temp_file}: {str(e)}")

                file_count += 1
            else:
                logger.warning(f"Skipping {filename} due to missing work data")
                skipped_count += 1

        logger.info(f"Completed processing {file_count} TEI text files.")
        logger.info(f"Skipped {skipped_count} files due to missing work data.")
        return file_count

    except Exception as e:
        logger.error(f"Error processing TEI files: {str(e)}")
        return 0


def update_tei_references(tei_file, output_file, authority_dir="./lists/output"):
    """
    Update token references in TEI file to point to authority files and
    convert <seg type="token"> elements to <w> elements with properly formatted references
    """
    logger.info(f"Updating token references in {tei_file}")

    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(tei_file, parser)
        root = tree.getroot()

        # NEW: Build type_to_sense mapping from lexicon.xml
        type_to_sense = {}
        lexicon_path = os.path.join(authority_dir, "lexicon.xml")
        if os.path.exists(lexicon_path):
            logger.info("Building type-to-sense mapping from lexicon.xml")
            try:
                lexicon_tree = etree.parse(lexicon_path)
                lex_ns = {
                    "tei": "http://www.tei-c.org/ns/1.0",
                    "xml": "http://www.w3.org/XML/1998/namespace",
                }

                for sense in lexicon_tree.findall(".//tei:sense", lex_ns):
                    sense_id = sense.get(
                        f"{{{XML_NS}}}id"
                    )  # e.g., "lemma_1097_sense_1741"
                    ana_attr = sense.get("ana")  # e.g., "#type_3398 #type_5567"

                    if sense_id and ana_attr:
                        # Extract type IDs from @ana attribute
                        for ana_value in ana_attr.split():
                            if ana_value.startswith("#type_"):
                                type_id = ana_value[6:]  # Remove "#type_" prefix
                                type_to_sense[type_id] = sense_id

                logger.info(f"Built mapping for {len(type_to_sense)} word types")
            except Exception as e:
                logger.warning(f"Could not build type-to-sense mapping: {e}")

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
                if not (name == "type" and value == "token"):
                    w_elem.set(name, value)

            # Update lemma reference first, as we'll need it for sense references
            lemma_id = None
            lemma_num = None
            if "lemmaRef" in w_elem.attrib:
                lemma_ref = w_elem.attrib["lemmaRef"]

                # Skip if already updated
                if not lemma_ref.startswith("lexicon.xml#"):
                    w_elem.attrib["lemmaRef"] = f"lexicon.xml#lemma_{lemma_ref}"
                    lemma_id = lemma_ref  # Store raw lemma ID
                else:
                    # Extract lemma ID from fully formed reference
                    if lemma_ref.startswith("lexicon.xml#lemma_"):
                        lemma_num = lemma_ref.split("#lemma_")[1]
                        lemma_id = lemma_num

            # Update meaning reference - now pointing to sense in lexicon.xml
            sense_full_id = (
                None  # Will store the full sense ID like "lemma_1097_sense_1741"
            )
            if "meaningRef" in w_elem.attrib:
                sense_ref = w_elem.attrib["meaningRef"]

                # Only process if not already pointing to a lemma-specific sense
                if not sense_ref.startswith("lexicon.xml#lemma_"):
                    references_fixed += 1

                    # Case 1: Already updated to lexicon but missing lemma prefix
                    if sense_ref.startswith("lexicon.xml#sense_"):
                        sense_num = sense_ref.split("#sense_")[1]

                        if lemma_id:
                            # Convert to proper lemma-based sense reference
                            sense_full_id = f"lemma_{lemma_id}_sense_{sense_num}"
                            w_elem.attrib["meaningRef"] = f"lexicon.xml#{sense_full_id}"

                    # Case 2: Referencing concept file
                    elif sense_ref.startswith("concepts.xml#concept_"):
                        sense_num = sense_ref.split("#concept_")[1]

                        if lemma_id:
                            # Convert concept reference to lemma-based sense reference
                            sense_full_id = f"lemma_{lemma_id}_sense_{sense_num}"
                            w_elem.attrib["meaningRef"] = f"lexicon.xml#{sense_full_id}"
                        else:
                            # No lemma available, use basic sense reference
                            w_elem.attrib["meaningRef"] = (
                                f"lexicon.xml#sense_{sense_num}"
                            )

                    # Case 3: Raw sense ID (not formatted yet)
                    else:
                        sense_num = sense_ref

                        if lemma_id:
                            # Create proper lemma-based sense reference
                            sense_full_id = f"lemma_{lemma_id}_sense_{sense_num}"
                            w_elem.attrib["meaningRef"] = f"lexicon.xml#{sense_full_id}"
                        else:
                            # No lemma available, use basic sense reference
                            w_elem.attrib["meaningRef"] = (
                                f"lexicon.xml#sense_{sense_num}"
                            )
                else:
                    # Already has proper format, extract the sense ID
                    if "#lemma_" in sense_ref:
                        sense_full_id = sense_ref.split("#")[1]

            # NEW: Update word reference with hierarchical format
            if "wordRef" in w_elem.attrib:
                word_id = w_elem.attrib["wordRef"]

                # Skip if already updated (contains "lexicon.xml#")
                if not word_id.startswith("lexicon.xml#"):
                    # Try to build hierarchical reference
                    if sense_full_id:
                        # We have the sense from meaningRef
                        w_elem.attrib["wordRef"] = (
                            f"lexicon.xml#{sense_full_id}_type_{word_id}"
                        )
                    elif word_id in type_to_sense:
                        # Lookup sense from our mapping
                        mapped_sense = type_to_sense[word_id]
                        w_elem.attrib["wordRef"] = (
                            f"lexicon.xml#{mapped_sense}_type_{word_id}"
                        )
                    else:
                        # Fallback: use just the type ID
                        logger.warning(f"Could not find sense for word type {word_id}")
                        w_elem.attrib["wordRef"] = f"lexicon.xml#type_{word_id}"

            # Copy any child elements (though tokens shouldn't typically have children)
            for child in token:
                w_elem.append(copy.deepcopy(child))

            # Replace the token with the new <w> element
            parent.replace(token, w_elem)
            processed += 1

        # Write updated file
        success = write_tei_file(root, output_file)
        if success:
            logger.info(
                f"Updated token references and converted to <w> elements in {tei_file}"
            )
            logger.info(
                f"Processed {processed} tokens and fixed {references_fixed} sense references"
            )

        return processed
    except Exception as e:
        logger.error(f"Error updating references: {str(e)}")
        return 0


# Get absolute paths for consistent reference handling
def get_authority_file_path(file_name):
    """Get the full path to an authority file in the output directory."""
    return os.path.join(authority_output_dir, file_name)


def check_skipped_files(input_dir="./", output_dir="./output"):
    """
    Check if all TEI files from the input directory have been processed and exist
    in the output directory. Reports any files that were skipped during processing.

    Args:
        input_dir: Directory containing original TEI files (default: current directory)
        output_dir: Directory containing processed TEI files (default: ./output)

    Returns:
        A set of filenames that were skipped
    """
    # Get lists of TEI files in both directories
    input_files = set([f for f in os.listdir(input_dir) if f.endswith(".tei.xml")])
    output_files = set([f for f in os.listdir(output_dir) if f.endswith(".tei.xml")])

    # Find files in input directory that are missing from output directory
    skipped_files = input_files - output_files

    # Report results
    if skipped_files:
        print(f"Found {len(skipped_files)} files that were not processed:")
        for file in sorted(skipped_files):
            print(f"  - {file}")
    else:
        print(f"All {len(input_files)} input files were successfully processed.")

    return skipped_files


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

        print("\n  Enable debug output:")
        print("    TEI_DEBUG=1 python tei-transformation.py")

        print("\n  Check for skipped files:")
        print("    python tei-transformation.py --check-skipped")
        sys.exit(0)

    # Default paths
    input_dir = "./"  # Current directory, where the script is now
    csv_dir = "./lists"  # Lists subdirectory for input CSVs
    output_dir = "./output"  # Output directory for processed TEI files
    authority_output_dir = os.path.join(
        csv_dir, "output"
    )  # Authority files output directory

    # Check for output directory override
    if "--output" in sys.argv:
        output_idx = sys.argv.index("--output")
        if output_idx + 1 < len(sys.argv):
            output_dir = sys.argv[output_idx + 1]
            # Remove these arguments from processing
            sys.argv.pop(output_idx)
            sys.argv.pop(output_idx)

    # Create output directories
    try:
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(authority_output_dir, exist_ok=True)
        logger.debug(
            f"Output directories ensured: {output_dir} and {authority_output_dir}"
        )
    except Exception as e:
        logger.error(f"Cannot create output directories: {str(e)}")
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

        logger.info(f"Processing single file: {input_file}")

        # Validate that authority files exist
        required_files = ["works.xml", "persons.xml", "genres.xml"]
        missing_files = []
        for filename in required_files:
            filepath = os.path.join(authority_output_dir, filename)
            if not os.path.exists(filepath):
                missing_files.append(filename)

        if missing_files:
            logger.error(f"Missing authority files: {missing_files}")
            logger.error("Please run 'python tei-transformation.py --lists all' first")
            sys.exit(1)

        # Step 1: Enhance header
        success = enhance_tei_header_from_xml(
            input_file, temp_file, authority_output_dir
        )

        # Only proceed if enhancement was successful
        if success:
            # Step 2: Update references and convert seg to w
            update_tei_references(temp_file, output_file, authority_output_dir)
            logger.info(f"Successfully processed {input_file} to {output_file}")
        else:
            logger.error(
                f"Could not enhance header for {input_file}, possibly due to missing work data"
            )

        # Remove the temporary file if it exists
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Could not remove temporary file {temp_file}: {str(e)}")

    # Generate authority files
    elif len(sys.argv) > 1 and sys.argv[1] == "--lists":
        if len(sys.argv) < 3:
            logger.error(
                "Please specify which lists to generate (all, persons, lexicon, etc.)"
            )
            sys.exit(1)

        list_type = sys.argv[2]

        if list_type == "all":
            logger.info("Generating all authority files...")

            # Check for TEXTWORD.xml for word type integration
            textword_file = (
                os.path.join(csv_dir, "TEXTWORD.xml")
                if os.path.exists(os.path.join(csv_dir, "TEXTWORD.xml"))
                else None
            )

            create_persons_tei(
                os.path.join(csv_dir, "persons.csv"),
                get_authority_file_path("persons.xml"),
            )
            create_lexicon_tei(
                os.path.join(csv_dir, "lexicon.csv"),
                get_authority_file_path("lexicon.xml"),
                textword_file,  # NEW: Pass TEXTWORD.xml for @ana integration
            )
            create_concepts_tei(
                os.path.join(csv_dir, "concepts.csv"),
                get_authority_file_path("concepts.xml"),
            )
            create_genres_tei(
                os.path.join(csv_dir, "genres.csv"),
                get_authority_file_path("genres.xml"),
            )
            create_names_tei(
                os.path.join(csv_dir, "onomastic.csv"),
                get_authority_file_path("names.xml"),
            )
            create_works_tei(
                os.path.join(csv_dir, "works.csv"),
                get_authority_file_path("works.xml"),
                os.path.join(csv_dir, "persons.csv"),
            )
            logger.info(f"All authority files generated in {authority_output_dir}")

        elif list_type == "persons":
            create_persons_tei(
                os.path.join(csv_dir, "persons.csv"),
                get_authority_file_path("persons.xml"),
            )

        elif list_type == "lexicon":
            textword_file = (
                os.path.join(csv_dir, "TEXTWORD.xml")
                if os.path.exists(os.path.join(csv_dir, "TEXTWORD.xml"))
                else None
            )
            create_lexicon_tei(
                os.path.join(csv_dir, "lexicon.csv"),
                get_authority_file_path("lexicon.xml"),
                textword_file,
            )

        elif list_type == "concepts":
            create_concepts_tei(
                os.path.join(csv_dir, "concepts.csv"),
                get_authority_file_path("concepts.xml"),
            )

        elif list_type == "genres":
            create_genres_tei(
                os.path.join(csv_dir, "genres.csv"),
                get_authority_file_path("genres.xml"),
            )

        elif list_type == "names":
            create_names_tei(
                os.path.join(csv_dir, "onomastic.csv"),
                get_authority_file_path("names.xml"),
            )

        elif list_type == "works":
            create_works_tei(
                os.path.join(csv_dir, "works.csv"),
                get_authority_file_path("works.xml"),
                os.path.join(csv_dir, "persons.csv"),
            )

        else:
            logger.error(f"Unknown list type: {list_type}")
            logger.error(
                "Valid options: all, persons, lexicon, concepts, genres, names, works"
            )
            sys.exit(1)

    elif len(sys.argv) > 1 and sys.argv[1] == "--check-skipped":
        check_skipped_files()

    # Default behavior: Process all TEI files
    else:

        logger.info(f"Processing all TEI files in {input_dir}...")
        logger.info(f"Output will be written to {output_dir}")

        # Validate that authority files exist
        required_files = ["works.xml", "persons.xml", "genres.xml"]
        missing_files = []
        for filename in required_files:
            filepath = os.path.join(authority_output_dir, filename)
            if not os.path.exists(filepath):
                missing_files.append(filename)

        if missing_files:
            logger.error(f"Missing authority files: {missing_files}")
            logger.error("Please run 'python tei-transformation.py --lists all' first")
            sys.exit(1)

        # Process all TEI files
        process_text_files_with_xml_authorities(
            input_dir, output_dir, authority_output_dir
        )
