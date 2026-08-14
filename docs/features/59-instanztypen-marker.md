# #59: Lindas Instanztypologie im Naming-Explorer

**Angelegt:** 2026-08-14. **Typ:** Feature-Doc (temporär, lebt solange #59 offen ist).
**Anlass:** Linda Beutel-Thurow hat am 2026-08-11 auf #59 geantwortet und ihre Quelldaten
umgestellt. Alle Zahlen hier sind am 2026-08-14 gegen ihre Daten gemessen, die
Messvorschriften stehen in Abschnitt 6.

---

## 1. Was sich geändert hat

Bis zum 2026-08-10 war das Datenmodell zweiwertig: ein Identifikator der nennenden
Instanz trug entweder ein führendes `#` oder eckige Klammern, und beides bedeutete
dasselbe, nämlich „keine handelnde Figur des Werks". Genau so steht es heute im
Erklärtext des Moduls und so prüft es `NOTATION = /^[#[]/`.

Linda hat das durch eine Typologie mit acht Instanztypen ersetzt, maschinenlesbar als
`data/instance_types.json` in ihrem Repo:

| Typ | Marker | Beispiel |
|---|---|---|
| Individual | keiner | `Karl`, `Engel`, `Pförtner` |
| Collective | `[…]` | `[haiden]`, `[Menge]` |
| Role figure | `<…>` | `<hirte>`, `<suriân>` |
| Collective member | `<…>` | `<Eine von den 300 Frauen>` |
| Group | ` & ` | `Pallas & Juno` |
| Non-figure | `{…}` | `{Inschrift}` |
| Quoted | `#…` | `#David` |
| Immaterial | `°…` | `°diu stimme` |

Vier Eigenheiten, die sie ausdrücklich dokumentiert und die den Umbau bestimmen:

1. Marker stehen ausschliesslich im Feld `Nennende Instanz`, nie an `Benannte Figur`.
2. **Mischformen:** bei `[rechen] des Eneas` und `Medeas <meisterîn>` umschliesst der
   Marker nur den textentnommenen Teil. Er sitzt also nicht zwingend am Stringanfang.
3. Qualifier stehen ausserhalb des Markers: `[fürsten] (heidnisch)` und
   `[fürsten] (christlich)` sind zwei verschiedene Instanzen.
4. `Role figure` und `Collective member` teilen sich `<…>` und sind **per Muster nicht
   unterscheidbar**. Die Unterscheidung ist analytisch, nicht notationell.

## 2. Gemessene Lage

Gemessen gegen `v.0.2.1-beta` (Tag `055c88ef`), verglichen mit unserem letzten
Bau-Quellstand `b7cc0585`.

**Umfang der Markierung:** 240 markierte Nennungen von 10.502, also 2,3 Prozent.
37 global distinkte markierte Werte (je Werk Iwein 6, Eneasroman 4, Rolandslied 12,
Trojanerkrieg 19; die Summe 41 ist höher, weil 4 Werte in mehr als einem Werk stehen).
Lindas Angaben im Kommentar stimmen exakt, einschliesslich der 37.

**Der Defekt in Zahlen:** `NOTATION = /^[#[]/` erkennt am neuen Stand **103 der 240**
markierten Nennungen und verpasst **137** in 16 distinkten Werten. Die grössten
Ausfälle: `<hirte>` (37), `Pallas & Juno` (27), `<wirt>` (26), `Icalrions & Clariens`
(12). Zwei Ursachen zugleich: die Regex kennt `<`, `{`, `°` und ` & ` nicht, und ihr
`^`-Anker scheitert an den Mischformen.

**Das Gitter verschwindet fast vollständig.** Im Rolandslied fiel `#` von 69 Nennungen
in 13 Werten auf 3 Nennungen in 1 Wert, im Trojanerkrieg von 2 auf 0. Im gesamten neuen
Bestand steht `#` noch dreimal. Der Erklärtext, den wir am 10.08. ausgeliefert haben,
erklärt damit nach dem Update ein Zeichen, das dreimal in 10.502 Nennungen vorkommt.

**Verteilung neu, je Werk und Markerklasse (Nennungen):**

| Werk | `[…]` | `<…>` | ` & ` | `{…}` | `#` | `°` |
|---|---|---|---|---|---|---|
| Iwein | 14 | 6 | 0 | 3 | 0 | 0 |
| Eneasroman | 3 | 1 | 0 | 2 | 0 | 0 |
| Rolandslied | 37 | 8 | 12 | 0 | 3 | 2 |
| Trojanerkrieg | 46 | 74 | 29 | 0 | 0 | 0 |

**Weitere Bewegungen:** distinkte benannte Figuren sinken durch die zusammengeführten
Schreibvarianten (Eneasroman 111 auf 109, Rolandslied 195 auf 191, Trojanerkrieg 250 auf
248, Iwein unverändert 60). Die Recordzahl fällt von 10.505 auf 10.502, die drei fehlen
im Iwein. Lindas Kommentar sagt „keine Datensätze ergänzt oder entfernt"; das war am
11.08. richtig und wurde von ihrem eigenen Commit vom 13.08. („resolve Iwein
duplicates") überholt.

**Tag und master sind nicht identisch.** `v.0.2.1-beta` zeigt auf `055c88ef`, `master`
steht zwei Commits weiter auf `4766065c`. Der Unterschied betrifft 6 Records in ENE, ROL
und TRO, in denen ein nachgestelltes Attribut von `Bezeichnung 2` in eine
`Epitheta`-Spalte gewandert ist. Das ist genau die Klassifikation, die unser Build liest.

## 3. Entscheidung

**Marker bleiben in der Anzeige stehen, die Typologie wird als bedingte Legende erklärt,
es gibt keine Typzuweisung pro Wert.** Das ist zugleich die Antwort auf Lindas Frage,
was bei ihrer Option b „darstellbar und überhaupt sinnvoll" wäre.

Gegen ihre Option c (Marker still entfernen) spricht der eigene Code: der Kopfkommentar
des Moduls hält fest, dass dieses Abstreifen schon einmal drin war und am 2026-08-09
zurückgebaut wurde, weil `#David` und ein handelnder David denselben Schlüssel bekämen.
Die neue Typologie vergrössert diese Kollisionsfläche, statt sie zu verkleinern:
`<hirte>` gegen einen individuellen `hirte`, und `[X]`, `<X>`, `{X}` fielen alle auf `X`
zusammen, also drei Typen auf einem Schlüssel.

Gegen ihre Option b in der starken Form (strippen plus Typ-Badge) sprechen zwei Punkte:

1. Für `<…>` ist der Typ **nicht bestimmbar** (Eigenheit 4). Ein Badge „Rollenfigur" an
   `<Eine von den 300 Frauen>` wäre eine Behauptung, die die Daten nicht decken.
2. Die primäre Oberfläche ist ein `<select>`. Ein `<option>` trägt keine Badges, und ein
   Textsuffix `hirte (Rollenfigur)` ist länger als `<hirte>`. In einem Auswahlfeld ist
   der Marker selbst die kompakteste mögliche Typanzeige.

Dazu kommt die Verteilung: 97,7 Prozent der Werte sind markerlos. Eine Oberfläche, die
acht Typen gleichrangig präsentiert, richtet sich nach 2,3 Prozent der Daten.

**Zwei Architekturfestlegungen:**

- **Die Typ-Ableitung bleibt in der Ansicht, nicht im Index.** Ein `type`-Feld pro Wert
  würde die unbestimmbare Unterscheidung Rollenfigur gegen Kollektivmitglied in den
  Datenstand backen. Liefert Linda die Unterscheidung später analytisch nach, ändert
  sich so nur eine Legendenzeile statt eines Indexformats. Das ist derselbe Gedanke wie
  am 2026-08-09, wo eine Bereinigung bewusst in der Ansicht blieb und einen Tag später
  ersatzlos wegfiel. Der Gattungsbaum vom 2026-08-10 ist **nicht** der Präzedenzfall:
  dort ging es um eine Reduktion, die die Ansicht gar nicht treffen konnte.
- **`instance_types.json` wird als Build-Validierung konsumiert, nicht ins Frontend
  durchgereicht.** Ihre `pattern`-Felder sind Python-Regexe mit uneinheitlicher
  Verankerung; fremde Regexe zur Laufzeit im Client auszuführen ist ein unnötiges
  Risiko für sechs stabile Glyphenkonventionen. Die deutschen Labels werden einmalig
  ins JS übernommen, mit Quellenangabe im Kommentar, und ein Drift-Guard im Build meldet
  Divergenz.

## 4. Arbeitspakete

Die Reihenfolge ist nicht beliebig. AP5 darf **nicht vor** AP1 bis AP3 landen, sonst
zeigt die Seite Lindas neue Marker unter unserer alten Erklärung.

| AP | Inhalt | Datei | parallel zu |
|---|---|---|---|
| AP1 | `NOTATION` ersetzen durch einen Test je Markerklasse (`/\[.*\]/`, `/<.*>/`, `/\{.*\}/`, `/^#/`, `/^°/`, `/ & /`), damit die Legende weiss, welche Klassen im Werk vorkommen | `naming-explorer.js` | AP4, AP6 |
| AP2 | `renderNotationHint` von einem Satz zu einer Legende: nur die vorkommenden Klassen, Lindas deutsche Labels, je ein Beispiel aus dem Werk (Mechanismus existiert). Für `<…>` ehrlich „Rollenfigur oder Kollektivmitglied, Unterscheidung analytisch" | `naming-explorer.js` | AP4, AP6 |
| AP3 | Kopfkommentar richtigstellen (er behauptet, `#` und eckige Klammern meinten dasselbe) und **alle** Zahlen darin frisch am Index messen | `naming-explorer.js` | AP4, AP6 |
| AP4 | Drift-Guard: `instance_types.json` mitfetchen, hart failen bei einem neunten Typ, einem neuen Marker oder einem Markerzeichen in den Werten, das keiner bekannten Klasse angehört | `01-fetch-and-build-index.py` | AP1 bis AP3 |
| AP5 | Index gegen den neuen Quellstand bauen | `data/naming-index.json.gz` | nach AP1 bis AP3 |
| AP6 | Antwort an Linda (Abschnitt 5) | GitHub | alles |

**Was ausdrücklich nicht passiert:** `namerKey` wird nicht gestrippt. Lindas
Gruppierungsempfehlung `re.sub(r'[\[\]<>{}]|^[#°]', '', wert)` ist für ihre eigene
Auswertung richtig, für unseren Schlüssel wäre sie die Rückkehr des am 2026-08-09
behobenen Fehlers. Nebenbei: ` & ` fasst diese Regex gar nicht an, was korrekt ist
(`Pallas & Juno` bleibt von `Pallas` getrennt), aber bedeutet, dass die Gruppenerkennung
in AP1 einen eigenen Test braucht.

## 5. Offene Fragen an Linda

1. **Welchen Quellstand sollen wir bauen?** Der DOI-tragende Tag `v.0.2.1-beta` liegt
   zwei Commits hinter `master`, und der Unterschied ist eine Datenkorrektur. Zitierbar
   ist der Tag, aktuell ist master. Am einfachsten wäre, wenn sie den Tag nachzieht.
2. **Ist `example_values` in `instance_types.json` erschöpfend** oder wirklich nur
   beispielhaft? Wäre es erschöpfend, liesse sich Rollenfigur gegen Kollektivmitglied
   doch auflösen, und die Legende könnte präziser werden. Der Feldname spricht dagegen.
   Kein Blocker.
3. **Hinweis zum Iwein:** drei Datensätze weniger als vor der Umstellung. Sie hat
   ausdrücklich um Meldung gebeten, falls bei der Migration eine Unstimmigkeit auffällt.
   Ihr Commit vom 13.08. erklärt es vermutlich selbst.
4. **Zum Kollokations-Tooltip:** eigenes Arbeitspaket. Die Kollokationen liegen im Blatt
   „Gesamt" der Excel-Dateien, unser Build liest bisher ausschliesslich die JSONs.

## 6. Messvorschriften

Damit die Zahlen in Abschnitt 2 nachrechenbar sind statt zitierbar:

- **Markierte Nennung:** ein Wert in `Nennende Figur` oder `Benannte Figur`, der nach
  `.strip()` nicht leer ist und entweder ` & ` enthält, eines der Zeichen `[]<>{}`
  enthält, oder mit `#` oder `°` beginnt. Die Leerprüfung ist nicht optional: ohne sie
  zählt Python jeden leeren Wert als markiert, weil `'' in '#°'` wahr ist. Genau dieser
  Fehler hat bei der ersten Messung 4.295 statt 240 ergeben.
- **Distinkte markierte Werte:** nach `.strip()`, je Werk gezählt ergibt 41, global
  dedupliziert 37. Beide Zahlen sind richtig und messen Verschiedenes.
- **Regex-Trefferquote:** `^[#\[]` gegen den gestrippten Wert, angewandt auf die 240.
- **Recordzahl:** Länge der Top-Level-Liste je categorization-JSON.
