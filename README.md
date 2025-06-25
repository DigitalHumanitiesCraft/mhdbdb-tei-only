# MHDBDB TEI Transformation Tool

A Python utility for transforming Middle High German Database (MHDBDB) data from CSV files and XML dumps into structured TEI XML files, updating reference systems, and enhancing TEI headers with metadata.

## Overview

This tool performs three main functions:

1. **Authority File Generation**: Creates TEI XML authority files for persons, concepts, lexicon entries, genres, works, and word types
2. **Header Enhancement**: Adds detailed metadata to existing TEI files based on work and person information
3. **Reference System Update**: Converts token references to standardized formats and transforms `<seg>` elements to TEI-compliant `<w>` elements

## Quick Start

⚠️ **Important**: Authority files must be generated before processing TEI files, as the TEI processing depends on these reference files.

### Step 1: Generate Authority Files (Required First)

```bash
python tei-transformation.py --lists all
```

This creates the required reference files in `./lists/output/`:

- `persons.xml`, `lexicon.xml`, `concepts.xml`, `genres.xml`, `names.xml`, `works.xml`

### Step 2: Process TEI Files

After authority files exist, process your TEI text files:

```bash
# Process all TEI files in current directory
python tei-transformation.py

# OR process a single file
python tei-transformation.py --file input.tei.xml
```

## Data Sources

The input CSV files were generated from the MHDBDB RDF database using SPARQL queries ([see detailed queries in lists/sparql.md](lists/sparql.md)). Each CSV file corresponds to a specific aspect of the database:

- `persons.csv` - Author/person data with identifiers and associated works
- `lexicon.csv` - Dictionary entries with part of speech and references to senses/concepts
- `concepts.csv` - Semantic concepts with labels and hierarchical relationships
- `genres.csv` - Text genre classifications with German labels and hierarchies
- `onomastic.csv` - Name system concepts with language labels and relationships
- `works.csv` - Work metadata with sigle, title, author references, and external identifiers

Additionally, an XML dump file is used to create the word types authority:

- `TEXTWORD.xml` - Contains mappings between word types and their senses/meanings

These files serve as the source data for generating the TEI authority files and enhancing TEI text documents.

## Directory Structure

- `./*.tei.xml` - TEI text files to be processed (input)
- `./lists/` - Directory containing CSV files
- `./lists/output/` - Generated authority files (persons.xml, lexicon.xml, etc.)
- `./output/` - Generated processed TEI text files

## Complete Usage Reference

### 1. Generate Authority Files (Must Run First)

Create all authority files from CSV data:

```bash
python tei-transformation.py --lists all
```

Generate individual authority files:

```bash
python tei-transformation.py --lists persons
python tei-transformation.py --lists lexicon
python tei-transformation.py --lists concepts
python tei-transformation.py --lists genres
python tei-transformation.py --lists names
python tei-transformation.py --lists works
```

**Output**: Creates authority XML files in `./lists/output/`

### 2. Process TEI Files (Requires Authority Files)

Process all TEI files in the current directory:

```bash
python tei-transformation.py
```

Process a single TEI file:

```bash
python tei-transformation.py --file input.tei.xml [output.tei.xml]
```

**Output**: Enhanced TEI files in `./output/`

### 3. Utility Commands

Check for files that were skipped during processing:

```bash
python tei-transformation.py --check-skipped
```

Change output directory for processed TEI files:

```bash
python tei-transformation.py --output custom_output_dir
```

**Note**: The `--output` option only affects processed TEI text files. Authority files are always created in `./lists/output/`.

Enable debug output:

```bash
TEI_DEBUG=1 python tei-transformation.py
```

Show help:

```bash
python tei-transformation.py --help
```

## Workflow Dependencies

```
CSV Files + TEXTWORD.xml
         ↓
   Authority Files (Step 1)
         ↓
   TEI File Processing (Step 2)
         ↓
   Enhanced TEI Files
```

**Important**: You cannot process TEI files without first generating the authority files, as the TEI enhancement process reads metadata from these XML authority files.

## Output Files

The script generates the following TEI XML files:

**Authority Files** (always in `./lists/output/`):

- `persons.xml` - Registry of persons/authors with identifiers and references
- `lexicon.xml` - Dictionary of Middle High German lexical entries with grammatical and semantic information
- `concepts.xml` - Taxonomy of semantic concepts
- `genres.xml` - Taxonomy of text types/genres
- `names.xml` - Onomastic system with name categories
- `works.xml` - Registry of works with sigles, titles, and author information

**Processed TEI Files** (in `./output/` or custom directory specified with `--output`):

- Enhanced TEI text files with proper headers and updated reference systems

## Typical Workflow

1. **Prepare data**: Ensure CSV files and TEXTWORD.xml are in `./lists/`
2. **Generate authorities**: `python tei-transformation.py --lists all`
3. **Verify authorities**: Check `./lists/output/` for generated XML files
4. **Process texts**: `python tei-transformation.py`
5. **Check results**: Verify enhanced TEI files in `./output/`
6. **Debug if needed**: Use `--check-skipped` to find any problematic files

## TODO

Known issues that need attention:

- Currently, some files are skipped during processing due to missing work data:
  - REG.tei.xml
  - VOR.tei.xml
  - ZWR.tei.xml
- These files need to be manually verified and their corresponding work data added to the CSV files.

## Terminology Reference

For clarity on the various terms used in different data sources (SQL, RDF, TEI), see the [terminology reference](lists/terminology.md).

## Error Handling

- The script includes robust error handling and logging
- Debug mode can be enabled by setting the `TEI_DEBUG=1` environment variable
- Logs include warnings for missing data and errors during processing
- If TEI processing fails, check that authority files were generated successfully first

## Requirements

- Python 3.10+
- lxml library for XML processing
