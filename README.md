# MHDBDB TEI Transformation Tool

A Python utility for transforming Middle High German Database (MHDBDB) data from CSV files into structured TEI XML files, updating reference systems, and enhancing TEI headers with metadata.

## Overview

This tool performs three main functions:

1. **Authority File Generation**: Creates TEI XML authority files for persons, concepts, lexicon entries, genres, and works
2. **Header Enhancement**: Adds detailed metadata to existing TEI files based on work and person information
3. **Reference System Update**: Converts token references to standardized formats and transforms `<seg>` elements to TEI-compliant `<w>` elements

## Data Sources

The input CSV files were generated from the MHDBDB RDF database using SPARQL queries ([see detailed queries in lists/sparql.md](lists/sparql.md)). Each CSV file corresponds to a specific aspect of the database:

- `persons.csv` - Author/person data with identifiers and associated works
- `lexicon.csv` - Dictionary entries with part of speech and references to senses/concepts
- `concepts.csv` - Semantic concepts with labels and hierarchical relationships
- `genres.csv` - Text genre classifications with German labels and hierarchies
- `onomastic.csv` - Name system concepts with language labels and relationships
- `works.csv` - Work metadata with sigle, title, author references, and external identifiers

These CSV files serve as the source data for generating the TEI authority files and enhancing TEI text documents.

## Directory Structure

- `./*.tei.xml` - TEI text files to be processed (input)
- `./lists/` - Directory containing CSV files
- `./output/` - Generated output files

## Usage

### Process All TEI Files (Default)

Enhances headers and updates references for all TEI files in the current directory:

```bash
python tei-transformation.py
```

### Process a Single TEI File

Processes just one specific TEI file:

```bash
python tei-transformation.py --file input.tei.xml [output.tei.xml]
```

### Generate Authority Files

Creates all authority files from CSV data:

```bash
python tei-transformation.py --lists all
```

Generate a specific authority file:

```bash
python tei-transformation.py --lists persons
python tei-transformation.py --lists lexicon
python tei-transformation.py --lists concepts
python tei-transformation.py --lists genres
python tei-transformation.py --lists names
python tei-transformation.py --lists works
```

### Change Output Directory

```bash
python tei-transformation.py --output custom_output_dir
```

### Enable Debug Output

```bash
TEI_DEBUG=1 python tei-transformation.py
```

## Output Files

The script generates the following TEI XML files:

- `persons.xml` - Registry of persons/authors with identifiers and references
- `lexicon.xml` - Dictionary of Middle High German lexical entries with grammatical and semantic information
- `concepts.xml` - Taxonomy of semantic concepts
- `genres.xml` - Taxonomy of text types/genres
- `names.xml` - Onomastic system with name categories
- `works.xml` - Registry of works with sigles, titles, and author information
- Enhanced TEI text files with proper headers and updated reference systems

## Error Handling

- The script includes robust error handling and logging
- Debug mode can be enabled by setting the `TEI_DEBUG=1` environment variable
- Logs include warnings for missing data and errors during processing

## Requirements

- Python 3.6+
- lxml library for XML processing