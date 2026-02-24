# Benutzerhandbuch

Anleitung zur Nutzung der MHDBDB-Weboberfläche. Die Anwendung besteht aus zwei Bereichen: der **Korpus-Suche** (Hauptseite) und dem **Playground** (Forschungswerkzeug).

## Korpus-Suche

Die Korpus-Suche ist die Hauptoberfläche zum Durchsuchen und Lesen mittelhochdeutscher Texte. Sie ist unter [Korpus](https://dhcraft.org/mhdbdb-tei-only/korpus.html) erreichbar.

### Lemma-Suche

1. Suchbegriff eingeben (z.B. "brot", "vriunt", "minne")
2. Button "Suchen" klicken oder Enter drücken
3. Die Suche normalisiert automatisch mittelhochdeutsche Zeichen:
   - Langvokale: â→a, ê→e, î→i, ô→o, û→u
   - Umlaute: ä→ae, ö→oe, ü→ue
   - Ligaturen: æ→ae, œ→oe
4. Orthographische Varianten werden automatisch aufgelöst (z.B. "brot", "brott" → "brôt")
5. Bei mehreren passenden Lemmata werden alle Treffer zusammengefasst und im blauen Infofeld angezeigt

### Textauswahl

Links neben den Suchergebnissen befindet sich die Textliste mit 666 Texten. Hier kann man:

- **Texte ein-/ausschliessen**: Checkbox neben jedem Text aktivieren/deaktivieren
- **Filtern**: Im Filterfeld nach Titel, Sigle oder Autor suchen
- **Alle/Keine**: Schnellauswahl oben rechts
- Die Suche berücksichtigt nur die ausgewählten Texte
- Die Anzahl der ausgewählten Texte wird unterhalb der Liste angezeigt

### Leseansicht

Ein Klick auf ein Suchergebnis oder das Buch-Icon neben einem Text öffnet die Leseansicht:

- **Volltext** mit Vers- und Prosastruktur, Strophen, Seitenumbrüchen und editorischen Markierungen
- **Highlighting**: Gefundene Lemmata werden farblich hervorgehoben (bis zu 5 Farben: rot, blau, grün, gelb, violett)
- **Navigation**: Mit den Buttons "Zurück" und "Weiter" zwischen Fundstellen springen
- **Metadaten**: Autor, Sigle, Gattung, Quelle - klappbar oberhalb des Textes
- **Editionen**: Bei Werken mit mehreren Editionen/Siglen kann man zwischen diesen wechseln

### TEI-Dateien direkt anzeigen

Neben jedem Text in der Textliste gibt es ein XML-Icon. Ein Klick darauf zeigt die rohe TEI-XML-Datei im Browser an.

## Playground

Der Playground ist das erweiterte Forschungswerkzeug, erreichbar unter [Playground](https://dhcraft.org/mhdbdb-tei-only/playground/). Er arbeitet in drei Schritten:

1. **Texte auswählen** (linke Spalte)
2. **Abfrage wählen** (mittlere Spalte)
3. **Ergebnisse ansehen** (rechte Spalte)

### Authority Files durchsuchen

Sechs Einstiegspunkte zum Durchsuchen der kontrollierten Vokabulare:

| Button | Inhalt | Ergebnis |
|--------|--------|----------|
| Autoren anzeigen | Autoren und historische Personen | Name, GND/Wikidata, Werkanzahl |
| Werke anzeigen | Werk- und Handschriftenmetadaten | Titel, Sigle, Autor, Gattungen |
| Lemmata anzeigen | Wörterbuch (ca. 39.000 Einträge) | Lemma, Wortart, Bedeutungen, Begriffe |
| Begriffe anzeigen | Semantische Begriffstaxonomie | Begriff, Hierarchie, zugehörige Lemmata |
| Gattungen anzeigen | Literarische Gattungsklassifikation | Gattung, Hierarchie, zugehörige Werke |
| Namen anzeigen | Eigennamen mit Relationen | Name, zugehörige Begriffe |

Jede Ansicht bietet ein Suchfeld zum Filtern. Maximal 30 Ergebnisse werden pro Suche angezeigt.

### TEI Textanalyse

Fünf Analysemodi für die TEI-Texte im Korpus:

**Multi-Lemma-Suche** (Hauptfunktion):
1. Button "Multi-Lemma-Suche" klicken - ein Dialog öffnet sich
2. Lemmata eingeben: Wörter (z.B. "brôt") oder IDs (z.B. "879"), getrennt durch Komma oder Plus
3. Eingegebene Lemmata erscheinen als Chips und können einzeln entfernt werden
4. Suchmodus wählen:
   - **Nähe-Analyse** (empfohlen): Findet Lemmata, die innerhalb eines einstellbaren Wortabstands (1-50 Wörter, Standard: 10) zusammen vorkommen
   - **Dokument-Suche**: Listet Texte auf, die alle Lemmata irgendwo enthalten
5. "Suche starten" klicken
6. Ergebnisse zeigen Fundstellen mit farbkodiertem Highlighting
7. Ein Klick auf ein Ergebnis öffnet die Leseansicht auf der Hauptseite mit allen Lemmata hervorgehoben

**Lemma-Suche**: Einzelnes Lemma im Korpus suchen (nach ID oder Wort)

**Alle Wörter**: Listet die ersten 200 Wörter der ausgewählten Texte auf

**Alle Zeilen**: Zeigt alle Textzeilen mit Zeilennummern

**Alle Annotationen**: Zeigt die TEI-Annotationen der Texte

### Workflow: Playground → Leseansicht

Der typische Forschungsworkflow:
1. Im Playground eine Multi-Lemma-Suche durchführen
2. Interessante Kookkurrenz finden
3. Auf das Ergebnis klicken
4. Die Hauptseite öffnet sich mit allen Lemmata farblich hervorgehoben
5. Automatischer Scroll zur Fundstelle

## Allgemeine Hinweise

### Erster Aufruf

Beim ersten Besuch werden die Index-Dateien geladen und im Browser zwischengespeichert (IndexedDB). Das dauert einige Sekunden. Danach laden die Seiten deutlich schneller.

### Cache leeren

Im Footer jeder Seite gibt es den Button "Clear Site Data". Dieser löscht alle lokal gespeicherten Daten (IndexedDB-Cache, zwischengespeicherte TEI-Dateien). Nützlich bei Problemen oder nach Updates.

### Systemanforderungen

- Moderner Webbrowser (Chrome, Firefox, Edge, Safari)
- Bildschirmbreite mindestens 1200px (Desktop-optimiert)
- JavaScript muss aktiviert sein
- IndexedDB muss verfügbar sein

### Bekannte Einschränkungen

- Nicht für mobile Geräte optimiert
- Grosse TEI-Dateien (z.B. lexicon.xml, 32 MB) können beim ersten Laden mehrere Sekunden dauern
- Die Suche arbeitet auf vorberechneten Indizes; Änderungen an den Quelldaten erfordern einen Neuaufbau

---

Bei Fragen oder Problemen: [mhdbdb@plus.ac.at](mailto:mhdbdb@plus.ac.at) | [GitHub Issues](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues)
