# Batch-Log: #216 Serie 1, minne (korpusweit)

Provenienz-Log nach POS-TAGSET.md §6.3.5 (dritter Batch unter `ingest/pos-disambig/`,
Muster: `189-gwtk-rot-junc/`).

## Rahmen

- **Issue:** #216 „Inhaltswort-Homographen nachannotieren, Serie 1: minne", Folge-Issue
  aus dem GWTK-Piloten #189 (PR #214) und der korpusweiten Quantifizierung (PR #210).
- **Datum:** 2026-08-24
- **Modell:** Claude Fable 5 (claude-fable-5), 118 Disambiguierungs-Subagenten in Wellen
- **Prompt:** `prompt.md` in diesem Ordner (Version 1, unverändert über alle Bündel)
- **Kontext je Fall:** im Vers Zielvers plus Vorgängervers plus zwei Folgeverse; in Prosa
  ein Fenster von ±15 Tokens innerhalb des Blockelements

## Bestand und Zuschnitt

Neu-Annotation nackter Tokens wie im Piloten, nicht Umhängen wie in #198. Extraktion über
alle 667 Korpusdateien (`extract-216-minne.py`): **6.982 Tokens der Oberflächenform `minne`
ohne `@lemmaRef` in 262 Texten**, exakt die Zahl aus dem Issue-Scoping. Davon stehen 5.966
im Vers und 1.016 in Prosa (`<p>` 962, `<head>` 29, `<hi>` 14, `<supplied>` 10, `<div>` 1).

Kandidaten-Lemmata, gegen `variants.xml` und `lexicon.xml` erhoben:

| Verdict | Bedeutung | Bestands-Typ |
|---------|-----------|--------------|
| `lemma_4130` NOM | Substantiv *minne* | `type_14385` |
| `lemma_4133` VRB | Verb *minnen* (1. Sg., Konjunktiv, Imperativ) | `type_38651` |
| `lemma_4130` NAM | Personifikation „Frau Minne" | (nicht angewendet) |

Beide angewendeten Paare haben Bestands-Typen; **dieser Batch prägt keine neuen
variants-Typen**, das Skript bricht ab, falls doch einer fehlte.

**326 der 6.982 Tokens tragen bereits ein `@pos` ohne Lemma** (Altannotation in ADP 183,
FLG 128 und ABG 15: 288 NOM, 22 VRB, 16 NAM). Dieses `@pos` ging als Vorinformation in den Prompt
(`pos_prior`), band das Urteil aber nicht.

## Anwendungsregel

Konservativ, Entscheidungen chsteiner 2026-08-24. Annotiert wird nur, wenn alle drei
Bedingungen gelten: `confidence = high`, Verdict ist nicht NAM, und es gibt keinen
Konflikt mit einem vorhandenen `pos_prior`. Alles andere bleibt byte-identisch und geht
in `review-faelle.csv`.

| Aktion | Anzahl |
|--------|-------:|
| ANNOTATE | 5.435 |
| REVIEW | 1.547 |

Verdict-Verteilung der Annotationen: `lemma_4130`/NOM 5.106, `lemma_4133`/VRB 329.

Die Review-Menge, nach Merkmalen aufgeschlüsselt (Mehrfachnennung möglich, weil die
Regeln in fester Reihenfolge greifen und `confidence` die übrigen Gründe verdeckt):
982 Fälle mit Verdict NAM, 16 mit `pos_prior` NAM, 1.546 mit `confidence < high`,
20 mit einem Konflikt zwischen `pos_prior` und Verdict.

`@ana` (Sense-Referenz) wird bewusst NICHT gesetzt: die Sense-Zuordnung ist kuratorisch,
gleiche Regel wie in #189 und #198.

## Zentrale Befunde

**1. Die Personifikation ist der große Posten, nicht der Randfall.** Das Issue nannte die
„Frau Minne"-Frage als Vorab-Check; gemessen sind es **982 Kandidaten** statt der 16, die
aus der Altannotation bekannt waren. In einzelnen allegorischen Texten trifft es die
Mehrheit der Belege eines Bündels. Alle 982 sind zurückgehalten. Ob die Personifikation
ein eigenes NAM-Lemma bekommt oder als `lemma_4130` mit `pos="NAM"` geführt wird, ist eine
philologische Entscheidung und liegt bei KZW; sie ist die Voraussetzung dafür, diese Menge
überhaupt anzufassen.

**2. In GWTK ist `minne` teils die Schreibvariante des Possessivs *mîne*.** Sechs Fälle hat
die Disambiguierung selbst als Possessiv-Verdacht auf `low` gesetzt (`minne wortt` = meine
Worte, `minne mage` = meine Verwandten, `minne gir`, `minne herschaft`). Ein siebter Fall
(`GWTK_125210733600_0`, `ir sölten bilich schowen / minne junckfrowen, / dü edel ist`) kam
mit `high` durch und wurde im Moderations-Pass zurückgehalten: das Relativpronomen des
Folgeverses steht im Singular, die Lesart ist „mîne juncfrouwen". GWTK schreibt das
Possessiv sonst `mine` (113 Belege) gegenüber 22 Vorkommen von `minne`.

**Zur Reichweite dieses Befunds wird hier bewusst nichts behauptet.** Zwei Versuche, das
Muster korpusweit zu suchen, sind gescheitert: eine Kontext-Heuristik lieferte 1.181
Treffer, die fast alle Genitivattribute waren (`der minne rât`, `minne twanc`, `minne
spil`), und ein Verhältnis von Possessivformen zu `minne` je Text bildet vor allem ab, wie
viel ein Text von Minne handelt (Nibelungenlied, Rolandslied stehen oben). Beide Maße haben
zu hohe Fehlalarmquoten, um als Negativbeweis zu dienen. Belegt ist der Fall für GWTK;
für die übrigen 261 Texte ist er weder belegt noch ausgeschlossen.

**3. Ein Moderations-Eingriff, dokumentiert.** `moderate-216-minne.py` hält den einen
Hand-Eingriff dieses Batches fest (GWTK_125210733600_0, `high` → `low`), statt
`actions.json` still zu ändern. Das Skript prüft den erwarteten Ausgangszustand und ist
idempotent.

## Qualitätssicherung (§6.3.3)

Drei Stichproben-Durchgänge, je 50 Fälle, jeweils von einem Prüfer ohne Kenntnis der
Verdicts. Die ersten beiden Durchgänge fanden **keinen** Fehler, taugten aber nur
eingeschränkt als Nachweis, und beide Male hat der Prüfer selbst gesagt warum:

1. `stichprobe-50.csv` (Zufall, Seed 216): 0 Fehler. Befund des Prüfers: 39 der damals 46
   NOM-Fälle sind allein durch einen unmittelbaren Nachbarmarker entschieden, die Stichprobe
   testet also das leichte Ende. Diese beiden Zahlen sind an der ausgelieferten Datei nicht
   mehr nachprüfbar: die Ziehung läuft über `random.Random(216)` aus der Liste der
   angewandten Fälle, und der Moderations-Pass hat danach einen Fall aus dieser Liste
   genommen, womit sich die Ziehung verschob. Die Datei trägt jetzt 45 NOM und 5 VRB. Die
   Aussage selbst hängt nicht an ihnen, der zweite Durchgang belegt sie unabhängig.
2. Erster Versuch einer geschichteten Stichprobe: 0 Fehler, aber der Prüfer maß nach, dass
   **46 % der Fälle doch einen Marker trugen**. Ursache war ein Filter über eine Wortliste,
   die die mittelhochdeutsche Schreibvielfalt verfehlte (`di`, `dîn`, `sîner`, `dorch`,
   `grozzer` standen nicht darin). Der Filter war unwirksam, ohne dass es aufgefallen wäre:
   derselbe Mechanismus wie in der Gate-Lehre vom 2026-07-29.
3. `stichprobe-schwer-50.csv` (Seed 21602): Filter jetzt über das `@pos` des unmittelbar
   vorangehenden `<w>` im TEI statt über eine Wortliste, Markermenge
   `DET/ART/PRP/POS/PRO/ADJ/GRA`. Von 5.435 Annotationen bleiben
   **2.041 ohne stützenden Vorgänger**; daraus 30 NOM und 20 VRB, Verben bewusst
   übergewichtet, weil Imperativ und Konjunktiv dort das Risiko sind. Ergebnis: **0 Fehler,
   getrennt gemessen 0 von 30 NOM und 0 von 20 VRB.** Entscheidend ist, dass diesmal die
   Risikoklasse getroffen wurde: fünf Imperative und drei Konjunktive ohne ausgedrücktes
   Pronomen, alle korrekt, drei davon erst durch einen Blick ins TEI verifizierbar
   (`TRU_5600_1` steht in einer Imperativkette, `REN_174350_2` hat `haz` als Subjekt,
   `WGI_405290_2` steht in einer Kapitelüberschrift).

**Auch der dritte Filter ist nicht dicht, und der Grund ist strukturell.** Der Prüfer hat
die Grundgesamtheit nachgerechnet und behalten hat davon der Einwand, nicht die Zahlen:
seine Aufgliederung (646/886/503) beruhte auf einem Formkriterium, das nicht mitgeliefert
war. Nachgemessen mit `stats-216-stichprobenbasis.py` (Vorschrift im Docstring) sieht die
Menge so aus: von den **2.041** Fällen ohne stützenden Vorgänger haben **1.144** einen
Vorgänger ganz ohne `@pos`, über den das Korpus also nichts sagt, obwohl er stützen könnte;
**1.084** haben einen Marker auf Distanz 2. Ohne jede der beiden Stützen bleiben **957**.
Ein Filter, der auf Annotationen prüft, kann in einem Korpus mit Annotationslücken nicht
dichter sein als der Annotationsstand selbst: dieselbe Lehre wie am 2026-07-29, eine Ebene
tiefer. Die Stichprobe fand in dieser Menge nichts; ein vollständiger Nachweis über alle
957 ist damit nicht erbracht und wird hier auch nicht behauptet.

Ein Personifikations-Fall ist nachweislich durch die Zurückhaltung gerutscht:
`REN_45520_5` (`daz ich sagte wie minne minne / enpfienc und vil sueze gruozte`) ist als NOM
annotiert, obwohl „wie Minne Minne empfing" im Renner ein Personifikationskontext ist. Unter
der angewandten Regel ist das kein Fehler (NAM wird nie automatisch vergeben, NOM ist der
Rückfall, und das Lemma bleibt in beiden Lesarten `lemma_4130`), aber die NAM-Zurückhaltung
ist damit nicht dicht, sondern markergesteuert.

## Nebenbefund außerhalb dieses Batches

Beim dritten Durchgang fiel auf, dass `wâren` durchgehend `lemmaRef="lexicon.xml#lemma_7505"`
(*wesen*) mit `pos="VRB"` trägt, auch dort, wo es das flektierte Adjektiv *wâr* ist.

Die Zahlen dazu haben zwei Zählvorschriften, und sie auseinanderzuhalten ist hier der
ganze Punkt. **Eng** heißt: `@corresp` trägt `type_273621`, also nur die Schreibung
`wâren`. **Breit** heißt: `@lemmaRef` trägt `lemma_7505` und die Form passt auf
`^w.{1,2}ren$`, also die ganze Schreibfamilie (`wâren` 5.641, `wæren` 907, `waren` 501,
`wâren` mit anderem Typ 471, `woren` 111, dazu sieben seltenere Schreibungen).

| | eng | breit |
|---|---|---|
| gesamt | 5.641 | 7.782 |
| davon nach ART/DET | 936 | 1.092 |
| davon zusätzlich vor NOM | 168 | 201 |
| davon direkt vor `minne` | 38 | **40** |

Keine dieser Zahlen außer der letzten ist eine Fehlerzahl: `daz wâren brüeder` ist
korrekt das Verb, und die Stellung ART + X + NOM ist überwiegend Prädikativ. Belegbar
falsch ist das Muster `der/die wâren minne`, das in einer Genitiv- oder Dativfügung kein
finites Verb enthalten kann: **40 Fälle** in CHH, ENG, FR3, GRG, HTR (5×), KWL, PRT,
RLS, SES, SFL (6×), SVW, TRH, TRO, TRU (2×), TSY (11×), WGL (3×) und WVV (2×). Die
beiden Fälle, die nur die breite Vorschrift findet, sind `CHH_35880_2` (`wæren`,
`type_273624`) und `FR3_112206030480_3` (`woren`, `type_273713`).

Eine frühere Fassung dieses Abschnitts nannte 8.385 Belege und 914 Vorkommen nach
Artikel. Beide Zahlen stammten aus einem Prüfer-Bericht und sind unter keiner der beiden
Vorschriften reproduzierbar; sie sind durch die gemessenen ersetzt. Das ist genau der
Fehler, den dieses Log an anderer Stelle beschreibt: eine Zahl übernehmen, statt sie zu
messen.

Das ist Altbestand, nicht dieser Batch, und wird als #367 eigenständig geführt.

Ein Vollständigkeits-Vorwurf aus Durchgang 2 wurde geprüft und entkräftet: die fünf
genannten Tokens sind sämtlich im Batch erfasst und tragen Verdicts (eines davon,
`WUT_20323_4`, ist gar nicht `minne`, sondern `dîner` und bereits annotiert). Die Gegenprobe
über die vier betroffenen Texte findet null nackte `minne`-Belege außerhalb des Batches.
Der Prüfer hatte den Stand vor dem Anwenden gesehen und das fehlende `@lemmaRef` als Lücke
gedeutet.

Auf Anregung aus Durchgang 1 trägt die Spalte `kontext` in allen CSV jetzt
Vorgänger-, Ziel- und Folgevers statt nur des Zielverses: mehrere Begründungen berufen
sich auf Material, das im bloßen Zielvers nicht steht, und waren aus der Datei allein
nicht nachprüfbar.

## Data-Change-Lifecycle

Abgearbeitet am 2026-08-24 nach der Korpus-Checkliste in `docs/DATA-MODEL.md`. Die
Routing-Frage entschied ein Trockenlauf statt einer Schätzung: `extract-variants.py`
ohne `--apply` meldet alle vier Semantik-Zähler auf 0 (`added`, `removed`,
`form text changed`, `lemma assignment changed`), und es kam keine Korpusdatei hinzu
oder weg. Die Schritte 5 und 6 entfallen damit, `variants.xml` und der
Authority-Index bleiben unangetastet: der Batch vergibt ausschließlich die beiden
bereits bestehenden Typen `type_14385` (minne) und `type_38651` (minnen).

| Schritt | Ergebnis |
|---|---|
| 1 UTF-8, Namespace, Wohlgeformtheit | 255/255 Dateien, 0 Fehler, je genau ein `<change>`-Eintrag mit Marker |
| 2 Schema (`validate-corpus.py --sample`) | 8/8 der größten betroffenen Texte gültig (TRO, RVBR, REN, BVSN, FLG1, WUT, ABG, GWTK) |
| 3 Version-Bump | Corpus-Index 4.2.1 → 4.2.2 an vier Stellen, `check-index-versions.py` grün; Authority-Index bleibt 1.9.0 (keine Inhaltsänderung, DATA-MODEL: kein Bump ohne Änderung) |
| 4 `build-corpus-index.py` | 667 Texte, 42.630 Lemmata, 7.538.417 Wörter |
| 5, 6 variants und Authority-Index | entfallen, siehe oben |
| 7 `build-api.py` | 2.742 Dateien; geändert haben sich `api/index.json` (Versionsfeld), die 255 Sigle-Dateien unter `api/texts/` und deren Sammelliste `api/texts/index.json` (beide wegen der Wortzahl) |
| 8 `check-authority-cross-refs.py --check` | grün, keine neuen dangling refs; lexicon.xml unverändert bei 396 Refs / 109 IDs innerhalb der Baseline |
| 9 `validate-indices.py` | beide Indexe strukturell gültig |

Der Index wurde zusätzlich positionsgenau gegen den Vorstand abgeglichen (Skript im
Session-Scratchpad, Messung protokolliert hier): Belegstellen korpusweit 7.532.982 →
7.538.417, Differenz exakt 5.435. Genau zwei Lemmata ändern ihre Belegzahl,
`lemma_4130` um +5.106 und `lemma_4133` um +329, was den Verdicts entspricht. Kein
Text und kein Lemma verliert eine Position. `lemma_4130` erscheint jetzt in 198,
`lemma_4133` in 21 Texten zusätzlich, in denen die Form vorher unannotiert stand.

Jede geänderte Datei trägt einen `<change>`-Eintrag mit ihren eigenen Zahlen
(`scripts/ingest/pos-disambig/revisiondesc-216-minne.py`, idempotent: ein zweiter Lauf
ersetzt den eigenen Eintrag, statt einen zweiten anzuhängen). Die sieben Texte, die
ausschließlich Review-Fälle enthalten, bleiben unverändert und bekommen deshalb auch
keinen Eintrag.

## Dateien

- `cases.json`: Extraktionsstand der 6.982 Tokens vor dem Batch (xml:id, Form, Vers bzw.
  Prosafenster, `pos_prior`), Eingabe `--cases` des Anwendungs-Skripts
- `actions.json`: Verdicts aller 6.982 Fälle nach dem Moderations-Pass, Eingabe `--actions`
- `diff-liste.csv`: alle Fälle mit Aktion, Review-Grund, Verdict, Konfidenz, Begründung
  und Kontext (Semikolon, UTF-8-BOM für Excel)
- `review-faelle.csv`: die 1.547 zurückgehaltenen Fälle
- `stichprobe-50.csv`: 50 Zufallsfälle aus den Annotationen (Seed 216)
- `stichprobe-schwer-50.csv`: 50 Fälle ohne stützenden Vorgänger (Seed 21602)
- `prompt.md`: der Disambiguierungs-Prompt, Version 1

Skripte: `scripts/ingest/pos-disambig/extract-216-minne.py` (Extraktion),
`fix-216-minne.py` (Anwendung), `moderate-216-minne.py` (Hand-Eingriffe),
`revisiondesc-216-minne.py` (Header-Einträge), `stats-216-stichprobenbasis.py`
(Grundgesamtheit der schweren Stichprobe und deren Ziehung).
Ein Replay setzt den Korpusstand vor dem Batch voraus (Parent-Commit): das
Anwendungs-Skript verifiziert, dass die Ziel-Tokens noch unannotiert sind, bevor es
schreibt.

## Ausdrücklich NICHT Teil dieses Batches

- Die 1.547 Review-Fälle, darunter die 982 Personifikations-Kandidaten und die sieben
  GWTK-Possessiv-Verdachtsfälle (Entscheidung KZW).
- Eine korpusweite Klärung, ob `minne` auch außerhalb von GWTK für *mîne* steht.
- Serie 2 ff. nach der Priorisierungsliste aus PR #210 (*sere*, *stat*, *not*, *nam*,
  *leit*, *rede*, *sach*, *rat* …).
