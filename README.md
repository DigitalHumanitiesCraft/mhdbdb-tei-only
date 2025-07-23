
# MHDBDB TEI Repository

Dieses Repository enthält:

- **TEI-kodierte mittelhochdeutsche Literaturtexte**
- **Kontrollierte Normdateien** (Authority Files)
- **Ein webbasiertes Explorationstool**
- **Ein Python-Tool zur Transformation und Metadatenanreicherung**

Alle Inhalte basieren auf den Daten der [Mittelhochdeutschen Begriffsdatenbank (MHDBDB)](https://www.mhdbdb.sbg.ac.at) der Universität Salzburg – einem Forschungsprojekt mit über 50 Jahren mediävistischer Text- und Begriffsforschung.

---

## TEI Transformation Tool

Ein Python-Werkzeug zur automatisierten Erzeugung, Anreicherung und Konvertierung von TEI-Dateien auf Basis von RDF-Daten, SPARQL-Exports und Volltextquellen.

### Hauptfunktionen

1. **Authority File Generation**  
   Erstellt TEI-konforme Referenzdateien (`persons.xml`, `lexicon.xml`, `concepts.xml` usw.) aus CSV-Quellen

2. **Works Enhancement**  
   Ergänzt `works.xml` mit bibliografischen Metadaten aus `print-works.csv`

3. **Header Enhancement**  
   Bereichert die TEI-Dateien mit Werk- und Personenmetadaten

4. **Reference System Update**  
   Vereinheitlicht Referenzformate und ersetzt `<seg>`-Elemente durch TEI-konforme `<w>`-Tokens


---

## Repository-Struktur

```text
/
├── authority-files/        # Generierte Referenzdaten (XML)
├── tei/                    # Mittelhochdeutsche TEI-Textdateien
├── lists/                  # CSV-Datenquellen & Output
│   ├── *.csv
│   ├── print-works.csv
│   └── output/
├── output/                 # Ergebnisdateien nach Transformation
├── playground/             # Web-Interface zur Exploration
└── tei-transformation.py   # Hauptskript
```

---

## Authority Files

Kontrollierte Vokabulare zur Verknüpfung und Annotation der TEI-Daten:

- `persons.xml` – Autoren und historische Personen  
- `lexicon.xml` – Wörterbuch mit grammatischen und semantischen Informationen  
- `concepts.xml` – Begriffssystematik mit Hierarchien  
- `genres.xml` – Klassifikation literarischer Gattungen  
- `works.xml` – Werk- und Handschriftenmetadaten  
- `names.xml` – Eigennamen mit semantischen Relationen  
- `works_enhanced.xml` – Erweiterte Werkdaten mit Druckausgaben  

---

##  Typischer Workflow

1. **Daten vorbereiten**: RDF-Daten in CSV umwandeln (mittels SPARQL)
2. **Authority Files generieren**:
   ```bash
   python tei-transformation.py --lists all
   ```
3. **Optional: Druckdaten einfügen**:
   ```bash
   python enhance_works.py works.xml print-works.csv works_enhanced.xml
   ```
4. **TEI-Dateien transformieren**:
   ```bash
   python tei-transformation.py
   ```

Weitere Optionen und Debug-Informationen siehe [Tool-Dokumentation](./README.md).

---

## Webbasierte Exploration (`/playground/`)

Ein clientseitiges Interface zur Analyse, Navigation und Recherche im TEI-Korpus und den Normdaten. Ermöglicht:

- Durchsuchen von Texten, Autoren, Werken und Begriffen
- XPath-Suche
- Visualisierung semantischer Relationen

Details: [`playground/README.md`](./playground/README.md)

---

## Lizenz

Alle Inhalte stehen unter der Lizenz **CC BY-NC-SA 3.0 AT**, sofern nicht anders in den Datei-Headern angegeben.
