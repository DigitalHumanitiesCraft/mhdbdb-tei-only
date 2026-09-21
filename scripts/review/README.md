# scripts/review

Generatoren für **kuratorische Prüfseiten**: einzelne HTML-Dateien, die man an
eine Fachwissenschaftlerin verschickt und die sie ohne Installation im Browser
öffnet, um Belegstellen zu beurteilen und die Antworten zurückzuschicken.

Angelegt am 21.09.2026 für #443 (das Format) und #359 (die erste Anwendung).

| Datei | Rolle |
|---|---|
| `review_page.py` | **Das Format aus #443.** Nimmt eine Fallliste entgegen und gibt eine fertige HTML-Seite zurück. Kennt keinen Vorgang und keine Daten |
| `collect-359-evidence.py` | Holt die Belegstellen für #359 aus den 667 TEI-Dateien |
| `build-359-page.py` | Setzt Belege und Bewertungen zur Seite für #359 zusammen |

Das Material und die erzeugte Seite liegen unter
[`ingest/review/359-borek/`](../../ingest/review/359-borek/README.md), nicht
hier: erzeugte Artefakte gehören neben ihre Daten und nicht neben ihren
Generator.

## Die eine Entscheidung, die das Format trägt

**Die Seite trägt ihre Daten eingebettet und lädt nichts nach.** KZW im Body von
#443: „Für mich ist die einzelne HTML-Datei, die man verschickt und ohne
Installation im Browser öffnet, weiterhin das gewünschte Grundformat." Eine
nachladende Seite scheitert unter `file://` an CORS, also genau in der Lage,
für die sie gebaut ist.

Der Preis ist, dass die Seite altert. Die Antwort darauf ist der Generator und
nicht ein Nachladeweg: ändern sich die Daten, wird die Seite neu erzeugt. Der
Datenstand steht deshalb sichtbar im Kopf jeder Seite.

Aus derselben Entscheidung folgt, dass hier **nichts** aus `assets/` oder
`playground/` benutzt wird. Die Farben, Abstände und Icons kommen aus
`docs/DESIGN.md` und stehen wörtlich in `review_page.py`, statt importiert zu
werden. Eine Datei mit einer Abhängigkeit auf das Repositorium ist keine Datei,
die man verschicken kann.

## Eine neue Prüfseite bauen

`review_page.render(spec)` erwartet ein Wörterbuch mit diesen Pflichtfeldern:

| Feld | Inhalt |
|---|---|
| `kennung` | Kurzname der Seite. Steht im Export und verhindert, dass ein fremder Export eingelesen wird |
| `titel`, `untertitel` | Kopf der Seite |
| `vorgang` | Die Ticketnummer, etwa `#359` |
| `anleitung` | Absätze der Prüfanleitung (HTML erlaubt) |
| `datenstand` | Paare aus Beschriftung und Wert. **Ohne diese Angabe lässt sich später nicht feststellen, worauf eine Antwort sich bezog** |
| `gruppen` | Abschnitte mit `id`, `titel`, `beschreibung` |
| `faelle` | Die Karten, siehe unten |

Optional: `vorab` (ein Block über dem Datenstand, für das, was vor allen Karten
gelesen werden muss) und `fuss`.

Ein Fall braucht `id`, `gruppe`, `kopf`, `frage`, `belege`, `optionen` und
darf `merkmale`, `vorschlag` und `beleg_hinweis` tragen. Fehlt ein Pflichtfeld
oder ist eine `id` doppelt, bricht `render` ab.

**Die Antwortoptionen bringt jeder Fall selbst mit.** Das ist Alans erster
Punkt aus #443: eine Liste, die für alle Fälle dieselbe ist, besteht zum
größten Teil aus Möglichkeiten, die nicht zutreffen. Die freie Antwort hängt
das Format an jede Karte, unabhängig von den Optionen.

## Was das Format zusichert

- **Drei Bearbeitungsstände**: unbearbeitet, entschieden, geprüft und offen.
  Der dritte ist eine vollwertige Rückmeldung und bleibt im Export erhalten
  (Alans dritter Punkt).
- **Der Kommentar hängt an keiner Antwort**, ist immer sichtbar, vier Zeilen
  hoch und vergrößerbar (Alans zweiter Punkt).
- **Ein Maschinenvorschlag ist als solcher bezeichnet**, mit Begründung und
  Unsicherheit, und die Seite sagt an jeder Karte, dass er keine Entscheidung
  ist. Es gibt keine Sammelaktion, die viele Fälle auf einen Wert setzt.
- **Gespeichert wird im Browser**, mit sichtbarer Anzeige. Die Anzeige kennt
  drei Zustände, darunter „Browser speichert nicht": unter `file://` kann
  `localStorage` je nach Browsereinstellung fehlschlagen, und dann muss die
  Seite es sagen statt es zu verschweigen.
- **Zurück kommt JSON und ein lesbarer HTML-Bericht.** Der Import liest nur
  einen Export derselben Kennung ein und sagt, was er ersetzt hat.

## Was beim Bauen zu beachten ist

- **Keine externen Verweise.** Kein CDN, kein Tailwind, keine Schriftart aus
  dem Netz. `scripts/audit/check-no-cdn.py` prüft die ausgelieferten Seiten,
  aber nicht diese; die Prüfung dafür gehört in den jeweiligen Generator.
- **Keine Emoji.** Heroicons als inline SVG, wie im ganzen Projekt.
- **Echte Umlaute, keine Em-Dashes.** Der Text dieser Seiten ist
  benutzersichtbare deutsche Prosa, auch wenn er aus einer JSON-Datei kommt.
  Die ASCII-Konvention der Skriptkommentare gilt hier nicht.
- **Daten in `<script>` müssen `</` maskieren.** `review_page._json_inline`
  tut das; ein Belegtext mit `</script>` darin würde die Seite sonst zerlegen.
