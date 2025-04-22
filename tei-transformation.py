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
            person.set(f"{{{XML_NS}}}id", f"person_{pid}")

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
                    relations.append(
                        ("isAuthorOf", f"#person_{pid}", f"works.xml#work_{wid}")
                    )

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
                "idno_uri": set(),
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
            d["idno_uri"].add(wid_uri)

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

            # ----- idnos -----
            for col, tp in (
                (d["idno_uri"], "URI"),
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
                a.set("ref", f"persons.xml#person_{aid}")
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
        for record in tree.findall("//DATA_RECORD"):
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
                target = ptr.get("target")
                if target and "concept_" in target:
                    concept_id = target.split("concept_")[1]
                    concepts.append(concept_id)

            # Store mapping
            sense_to_concepts[sense_id] = concepts

        logger.info(
            f"Extracted {len(sense_to_concepts)} sense-concept mappings from lexicon.xml"
        )
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
    """Add metadata from works/persons CSVs to the TEI header of a text file."""
    logger.info(f"Enhancing TEI header for {tei_file}")

    try:
        # ------------------------------------------------------------------ #
        # 1.  Parse TEI file
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(tei_file, parser)
        root = tree.getroot()

        ns = {"tei": TEI_NS}

        sigle = os.path.basename(tei_file).split(".")[0]  # filename‑based siglum
        logger.debug(f"Extracted sigle (instance): {sigle}")

        # ------------------------------------------------------------------ #
        # 2.  Load CSVs
        works_by_sigle = read_csv_data(works_csv, key_field="instance")
        works_by_iduri = read_csv_data(works_csv, key_field="id")

        persons_data = read_csv_data(persons_csv, key_field="personId")
        # supplement with personURI
        for row in read_csv_data(persons_csv):
            if row.get("personURI"):
                pid = _local_id(row["personURI"])
                if pid and pid not in persons_data:
                    persons_data[pid] = [row]

        if sigle not in works_by_sigle:
            logger.warning(f"No work row with instance={sigle}")
            return False

        # ------------------------------------------------------------------ #
        # 3.  Collect work metadata (title, authors, ext IDs …)
        first_row = works_by_sigle[sigle][0]
        work_id_local = _local_id(first_row["id"])

        work_data = defaultdict(set)

        def harvest(row):
            if row.get("label"):
                work_data["title"].add(row["label"].strip())
            if row.get("instance"):
                work_data["sigle"].add(_local_id(row["instance"]))
            if row.get("authorId"):
                work_data["authors"].add(_local_id(row["authorId"]))
            # external IDs come from sameAs
            uri = (row.get("sameAs") or "").strip()
            if uri:
                host = urllib.parse.urlparse(uri).hostname or ""
                if "wikidata.org" in host:
                    work_data["wikidata"].add(uri)
                elif "handschriftencensus" in host:
                    work_data["handschriftencensus"].add(uri)
                elif "d-nb.info" in host or "gnd" in host:
                    work_data["gnd"].add(uri)

        for r in works_by_sigle[sigle]:
            harvest(r)
        # harvest other rows of same work (same URI id)
        for r in works_by_iduri.get(first_row["id"], []):
            harvest(r)

        # ------------------------------------------------------------------ #
        # 4.  TEI header manipulation
        header = root.find(".//tei:teiHeader", ns)
        if header is None:
            logger.error("teiHeader missing")
            return False

        fileDesc = header.find(".//tei:fileDesc", ns)
        if fileDesc is None:
            fileDesc = etree.SubElement(header, f"{{{TEI_NS}}}fileDesc")
        # wipe existing children for clean rebuild
        for c in list(fileDesc):
            fileDesc.remove(c)

        # ----- titleStmt ----------------------------------------------------
        titleStmt = etree.SubElement(fileDesc, f"{{{TEI_NS}}}titleStmt")
        title_el = etree.SubElement(titleStmt, f"{{{TEI_NS}}}title")
        title_el.text = sorted(work_data["title"])[0] if work_data["title"] else sigle

        # authors
        for aid in sorted(work_data["authors"]):
            auth = etree.SubElement(titleStmt, f"{{{TEI_NS}}}author")
            auth.set("ref", f"persons.xml#person_{aid}")
            pref = None
            if aid in persons_data and persons_data[aid]:
                pref = persons_data[aid][0].get("preferredName")
            if pref:
                auth.text = pref

        # ----- publicationStmt ---------------------------------------------
        pubStmt = etree.SubElement(fileDesc, f"{{{TEI_NS}}}publicationStmt")
        publisher = etree.SubElement(pubStmt, f"{{{TEI_NS}}}publisher")
        publisher.text = "Mittelhochdeutsche Begriffsdatenbank (MHDBDB)"
        date_el = etree.SubElement(pubStmt, f"{{{TEI_NS}}}date")
        date_el.set("when", datetime.now().strftime("%Y"))
        date_el.text = datetime.now().strftime("%Y")

        # external IDs
        for coll, tp in (
            (work_data["wikidata"], "wikidata"),
            (work_data["handschriftencensus"], "handschriftencensus"),
            (work_data["gnd"], "gnd"),
        ):
            for uri in sorted(coll):
                idno = etree.SubElement(pubStmt, f"{{{TEI_NS}}}idno")
                idno.set("type", tp)
                idno.text = uri

        # ----- sourceDesc ---------------------------------------------------
        sourceDesc = etree.SubElement(fileDesc, f"{{{TEI_NS}}}sourceDesc")
        msDesc = etree.SubElement(sourceDesc, f"{{{TEI_NS}}}msDesc")
        msId = etree.SubElement(msDesc, f"{{{TEI_NS}}}msIdentifier")
        msId.set("corresp", f"works.xml#work_{work_id_local}")

        idno_sigle = etree.SubElement(msId, f"{{{TEI_NS}}}idno")
        idno_sigle.set("type", "sigle")
        idno_sigle.text = sigle

        # ------------------------------------------------------------------ #
        success = write_tei_file(root, output_file)
        if success:
            logger.info(f"Enhanced header for {sigle}")
        return success

    except Exception as e:
        logger.error(f"Error enhancing TEI header: {str(e)}", exc_info=True)
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
                            w_elem.attrib["meaningRef"] = (
                                f"lexicon.xml#lemma_{lemma_id}_sense_{sense_num}"
                            )

                    # Case 2: Referencing concept file
                    elif sense_ref.startswith("concepts.xml#concept_"):
                        sense_num = sense_ref.split("#concept_")[1]

                        if lemma_id:
                            # Convert concept reference to lemma-based sense reference
                            w_elem.attrib["meaningRef"] = (
                                f"lexicon.xml#lemma_{lemma_id}_sense_{sense_num}"
                            )
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
                            w_elem.attrib["meaningRef"] = (
                                f"lexicon.xml#lemma_{lemma_id}_sense_{sense_num}"
                            )
                        else:
                            # No lemma available, use basic sense reference
                            w_elem.attrib["meaningRef"] = (
                                f"lexicon.xml#sense_{sense_num}"
                            )

            # Update word reference
            if "wordRef" in w_elem.attrib:
                word_id = w_elem.attrib["wordRef"]
                # Skip if already updated
                if not word_id.startswith("types.xml#"):
                    w_elem.attrib["wordRef"] = f"types.xml#type_{word_id}"

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
                    logger.warning(
                        f"Could not remove temporary file {temp_file}: {str(e)}"
                    )

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
        print("    python tei-transformation.py --lists types path/to/xml_dump.xml")

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
            create_persons_tei(
                os.path.join(csv_dir, "persons.csv"),
                get_authority_file_path("persons.xml"),
            )
            create_lexicon_tei(
                os.path.join(csv_dir, "lexicon.csv"),
                get_authority_file_path("lexicon.xml"),
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
            create_lexicon_tei(
                os.path.join(csv_dir, "lexicon.csv"),
                get_authority_file_path("lexicon.xml"),
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

        elif list_type == "types":
            if len(sys.argv) < 4:
                logger.error(
                    "Error: Missing XML dump file path for types list generation"
                )
                print(
                    "Usage: python tei-transformation.py --lists types path/to/xml_dump.xml"
                )
                sys.exit(1)

            xml_dump_file = sys.argv[3]
            lexicon_file = get_authority_file_path("lexicon.xml")
            types_output_file = get_authority_file_path("types.xml")

            # Check if lexicon.xml exists, create it if not
            if not os.path.exists(lexicon_file):
                logger.info(
                    f"lexicon.xml not found at {lexicon_file}, creating it first..."
                )
                create_lexicon_tei(os.path.join(csv_dir, "lexicon.csv"), lexicon_file)

            create_types_tei(xml_dump_file, lexicon_file, types_output_file)

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
        works_csv = os.path.join(csv_dir, "works.csv")
        persons_csv = os.path.join(csv_dir, "persons.csv")

        logger.info(f"Processing all TEI files in {input_dir}...")
        logger.info(f"Output will be written to {output_dir}")

        # Process all TEI files
        process_text_files(input_dir, works_csv, persons_csv, output_dir)
