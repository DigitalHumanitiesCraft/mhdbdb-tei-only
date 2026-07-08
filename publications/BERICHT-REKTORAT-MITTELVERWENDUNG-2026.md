# Bericht an das Rektorat: Mittelverwendung MHDBDB 2025/26

**Entwurf für #145. Annahme: Absenderin ist Dr. Katharina Zeppezauer-Wachauer (Koordinatorin MHDBDB), erstellt gemeinsam mit dem technischen Partner Digital Humanities Craft OG. Vor Versand von KZW zu prüfen: Anrede (Rektor/Rektorin namentlich?), Briefkopf, genaue Bezeichnung der Mittelfreigabe.**

---

## Teil 1: Dankesbrief

Sehr geehrte[r] [Anrede Rektorat],

im Oktober 2025 hat das Rektorat für die Mittelhochdeutsche Begriffsdatenbank (MHDBDB) Mittel in Höhe von 20.480 Euro freigegeben. Dafür möchte ich mich, auch im Namen des gesamten Teams, herzlich bedanken.

Der folgende Bericht legt freiwillig und über die formale Abrechnung hinaus dar, was mit diesen Mitteln erreicht wurde. Das Ergebnis lässt sich vorab in einem Satz zusammenfassen: Die MHDBDB, seit über fünfzig Jahren ein Salzburger Forschungswerkzeug der Mediävistik, steht heute als vollständig modernisierte, öffentlich zugängliche Forschungsplattform bereit, und zwar genau in dem Umfang, den wir uns bei der Beantragung erhofft hatten.

Beide Angebotspakete wurden vollständig umgesetzt: die kontinuierliche Wartung des laufenden Betriebs ebenso wie die erweiterten Such- und Analysewerkzeuge samt der technischen Evaluationsbasis für künftige Texterweiterungen. Die Plattform ist unter https://mhdbdb.plus.ac.at bzw. der Projektseite öffentlich erreichbar; ich lade Sie ein, sich selbst ein Bild zu machen.

Das Vertrauen des Rektorats in dieses Projekt hat sich aus unserer Sicht ausgezahlt. Ich stehe für Rückfragen und eine Vorführung der Plattform jederzeit zur Verfügung.

Mit freundlichen Grüßen
Dr. Katharina Zeppezauer-Wachauer
Koordinatorin der Mittelhochdeutschen Begriffsdatenbank (MHDBDB)
Fachbereich Germanistik / Interdisziplinäres Zentrum für Mittelalter und Frühneuzeit

---

## Teil 2: Bericht über die Mittelverwendung

### 1. Gegenstand und Abgrenzung

Dieser Bericht betrifft ausschließlich die im Oktober 2025 freigegebenen Mittel in Höhe von 20.480 Euro. Sie wurden auf Grundlage zweier Angebote der Digital Humanities Craft OG (Graz) verwendet:

- **Angebot 32/25** „Wartung, Bugfixes und kleinere Erweiterungen am laufenden Betrieb" (rund 60 Arbeitsstunden über sechs Monate)
- **Angebot 33/25** „Advanced Search Tools und Evaluationsbasis für Texterweiterung"

Nicht Gegenstand dieses Berichts ist die einmalige Datenmigration der MHDBDB aus der Altinfrastruktur in das heutige TEI-Format. Diese wurde separat über CLARIAH-AT gefördert und abgerechnet.

### 2. Ausgangslage

Die MHDBDB dokumentiert seit 1972 den Wortschatz der mittelhochdeutschen Literatur. Nach der technischen Neuaufstellung 2025 lag das gesamte Korpus, 667 semantisch annotierte Texte mit rund 7,5 Millionen Wortbelegen und einem Lexikon von 43.879 Lemmata, erstmals vollständig in offenen Standards (TEI-XML) vor. Die freigegebenen Mittel dienten dazu, diese Datenbasis in eine dauerhaft betreibbare, öffentlich nutzbare Forschungsplattform zu überführen und die Suchwerkzeuge auf das Niveau zu heben, das die internationale Fachcommunity von der MHDBDB erwartet.

### 3. Ergebnisse aus Angebot 33/25: Such- und Analysewerkzeuge

Der Forschungsbereich der Plattform („Playground") bietet heute sechzehn Sucheinstiege, darunter zehn korpusanalytische Werkzeuge, die es in der alten MHDBDB nicht gab:

- **Multi-Lemma-Suche** mit Abstandssuche: findet Texte, in denen mehrere Begriffe gemeinsam oder in definierter Nähe zueinander vorkommen (etwa „rôt" und „munt" innerhalb von zehn Wörtern).
- **Begriffs- und Lemma-Verteilung**: zeigt, wie sich ein Konzept (z. B. „Sterben") oder ein Einzelwort über alle 667 Texte verteilt.
- **Kookkurrenz-Ranking, Textvergleich, Wortfrequenz- und Reimanalyse**: quantitative Werkzeuge für Fragestellungen von der Stilistik bis zur Versforschung.
- **Kuratierte Figurenbezeichnungen**: erschließt 10.506 Belegstellen zu Eigennamen und Epitheta aus einer Salzburger Dissertationsarbeit.

Dazu kommen Angebote für Lehre und breiteres Publikum: eine einfache Korpussuche mit Lesefassung aller Texte, ein alphabetisches Wörterbuch mit eigenen Seiten für alle 43.879 Lemmata samt Verknüpfung zu den Standardwörterbüchern des Mittelhochdeutschen (Lexer, MWB), sowie fünf deutschsprachige Hilfeseiten.

Die im Angebot vorgesehene **Evaluationsbasis für Texterweiterungen** wurde am Pilotfall der Wenzelsbibel erprobt: Der Prager Prachtcodex (Pentateuch, Cod. 2759–2764) wurde als erster Neuzugang seit der Migration vollständig in Korpus und Suchindizes integriert. Der dabei dokumentierte Aufnahmeprozess ist inzwischen die Standardprozedur für weitere Textaufnahmen; zwei Folgeprojekte (frühneuhochdeutsche Rechenbücher, „Der Borte") sind bereits in Vorbereitung.

Als Beitrag zu offener Wissenschaft stellt die Plattform seit Juni 2026 zusätzlich eine frei zugängliche Datenschnittstelle bereit (2.742 zitierfähige JSON-Ressourcen nach FAIR-Prinzipien) sowie eine dauerhafte Archivierung mit DOI über Zenodo.

### 4. Ergebnisse aus Angebot 32/25: Wartung und Betriebsstabilität

Der laufende Betrieb wurde über den gesamten Zeitraum ohne Ausfall gewährleistet. Im Einzelnen:

- Behebung gemeldeter Fehler aus dem laufenden Nutzerbetrieb, in der Regel innerhalb weniger Tage (dokumentiert im öffentlichen Issue-Tracker des Projekts).
- Aufbau einer automatisierten Testumgebung mit über 180 Prüfroutinen, die vor jeder Änderung die Kernfunktionen (Suche, Leseansicht, Datenintegrität) absichert.
- Automatische Qualitätskontrollen bei jeder Datenänderung (Schema-Validierung, Indexprüfung), sodass Korrekturen am Textbestand nicht unbemerkt zu Inkonsistenzen führen können.
- Vollständige technische und wissenschaftliche Dokumentation im öffentlichen Repositorium, einschließlich der Editionsgrundlagen und Kodierungsrichtlinien.

### 5. Einordnung

Mit den freigegebenen 20.480 Euro wurde die MHDBDB von einem migrierten Datenbestand zu einer betriebsstabilen Forschungsplattform mit erweitertem Werkzeugkasten ausgebaut. Sämtliche Ergebnisse sind öffentlich zugänglich, quelloffen und ohne laufende Lizenzkosten betreibbar; die Plattform kommt ohne Serverinfrastruktur mit Wartungsverträgen aus, was die Folgekosten für die Universität dauerhaft niedrig hält.

Die Plattform im Überblick:

- Hauptseite mit Korpussuche: https://dhcraft.org/mhdbdb-tei-only/
- Forschungswerkzeuge (Playground): https://dhcraft.org/mhdbdb-tei-only/playground/
- Datenschnittstelle (Dokumentation): https://dhcraft.org/mhdbdb-tei-only/api/index.html
- Archivierung: https://doi.org/10.5281/zenodo.20627656

---

## Offene Punkte vor Versand (nicht Teil des Dokuments)

- Anrede/Adressat im Rektorat klären
- 20.480 vs. Angebotssummen (7.000 + 14.000 brutto = 21.000): tatsächliche Rechnungssummen von KZW/chsteiner bestätigen lassen; Bericht nennt bewusst nur die freigegebene Summe
- Zeitraum der Leistungserbringung präzisieren (Okt 2025 bis Mitte 2026?)
- Ob DHCraft als Mitabsender auftreten soll
