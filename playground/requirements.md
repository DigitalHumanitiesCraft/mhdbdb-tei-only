# REQUIREMENTS.md - MHDBDB Playground

## Muss-Kriterien (F1-F6)

**F1: TEI Upload & Parsing**
- Bulk-Upload mehrerer TEI+Authority Files (Drag&Drop)
- Einzelfile-Upload möglich
- Client-side XML-Parsing und Strukturanalyse
- Fehlermeldungen bei invalid XML

**F2: Datenstruktur-Überblick**
- Nach Upload: Automatische Anzeige der gefundenen Strukturen
- Authority Files Browser (persons, lexicon, concepts, genres, works, names)
- Statistiken: Anzahl Texte, Lemmata, Personen, etc.

**F3: Explorative Query-Engine**
- Vordefinierte Query-Templates basierend auf MHDBDB-Datenstruktur
- *"Alle Werke von Autor X"*, *"Lemmata im semantischen Feld Y"*, etc.
- Queries generieren sich dynamisch aus uploadeten Daten

**F4: Kontext-Ergebnisse**
- Text-Snippets mit umgebendem Kontext (±3 Zeilen)
- Verknüpfte Metadaten anzeigen (Autor, Werk, Gattung, Konzepte)
- Click-to-navigate zwischen Cross-References

**F5: 3-Panel Desktop Layout**
- **Links:** Upload-Zone + Datenstruktur-Browser
- **Mitte:** Query-Interface mit vorgenerierte Templates
- **Rechts:** Results-Panel mit Kontext-Snippets

**F6: XPath Power-User Interface**
- Freie XPath-Eingabe für komplexe Queries
- Syntax-Highlighting für XPath
- Beispiel-XPaths basierend auf MHDBDB-Schema

## Kann-Kriterien (P1-P3)

**P1: Export-Funktionen**
- Query-Ergebnisse als CSV/JSON downloadbar
- Permalink-URLs für reproduzierbare Queries

**P2: Visualisierungen**
- Einfache Charts (Häufigkeiten, Verteilungen)
- Netzwerk-Visualisierung von Konzept-Verknüpfungen

**P3: Session-Persistierung**
- Browser LocalStorage für Upload-State
- Query-History

## Nicht-Ziele

- Mobile/Responsive Design
- Backend/Server-Komponenten  
- Performance-Optimierung für große Dateien (>50MB)
- User-Management oder Multi-Tenancy
- Editing/Annotation von TEI-Files

## Technische Constraints

- **Frontend-only:** Vanilla JavaScript, GitHub Pages hosting
- **Client-side:** Alles im Browser, keine Server-Calls
- **Desktop-fokussiert:** Min. 1200px Bildschirmbreite
- **Modern Browser:** ES6+, XML DOM APIs