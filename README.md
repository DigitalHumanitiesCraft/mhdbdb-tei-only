
# MHDBDB TEI Repository

TEI-encoded Middle High German literature texts with semantic annotations and web-based exploration interface from the [Mittelhochdeutsche Begriffsdatenbank (MHDBDB)](https://www.mhdbdb.sbg.ac.at), University of Salzburg.

## Content

Alle Inhalte basieren auf den Daten der [Mittelhochdeutschen Begriffsdatenbank (MHDBDB)](https://www.mhdbdb.sbg.ac.at) der Universität Salzburg – einem Forschungsprojekt mit über 50 Jahren mediävistischer Text- und Begriffsforschung.
- **666 TEI-encoded texts** (Middle High German literature)
- **6 authority files** (34.8 MB): persons, works, lexicon, concepts, genres, names
- **Web playground** for exploration and XPath queries

## Structure

```
├── tei/                     # 666 TEI texts (.tei.xml)
├── authority-files/         # 6 controlled vocabularies
└── playground/              # Web-based exploration tool
```

## Usage

### Web Interface
Open `playground/index.html` in a browser or run:
```bash
python -m http.server 8000
```

### Programmatic Access
TEI files reference authority data via `xml:id`:
```xml
<author ref="#person_445">Meister Eckhart</author>
<w lemma="vriunt" ana="#concept_12345">vriunt</w>
```

### XPath Examples
```xpath
//tei:persName[@type='preferred']  # All preferred person names
//tei:w[@lemma='vriunt']           # All instances of 'vriunt'
```

## Authority Files

- **persons.xml** (0.12 MB) - Authors and historical persons
- **works.xml** (1.41 MB) - Work and manuscript metadata  
- **lexicon.xml** (32.59 MB) - Dictionary with grammatical annotations
- **concepts.xml** (0.21 MB) - Semantic concept taxonomy
- **genres.xml** (0.4 MB) - Literary genre classification
- **names.xml** (0.03 MB) - Proper names with semantic relations

## License & Contact

**License:** [CC BY-NC-SA 3.0 AT](https://creativecommons.org/licenses/by-nc-sa/3.0/at/)  
**Contact:** mhdbdb@plus.ac.at | https://mhdbdb.plus.ac.at
