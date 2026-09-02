# Batch-Log: #235 Punkt 3, Rest (98 Breve-Tokens mit mehrdeutiger Wortart)

Provenienz-Log nach POS-TAGSET.md §6.3.5 (siebter Batch unter `ingest/pos-disambig/`,
Muster: `369-stat/`).

## Rahmen

- **Issue:** #235 Punkt 3, der Rest nach PR #379. Der Vorlauf hat 66 der 289
  Breve-Kandidaten mechanisch annotiert und 223 zurückgehalten; von diesen sind die 98
  mit mehrdeutiger Wortart am Ziel-Lemma dieses Arbeitspaket.
- **Datum:** 2026-09-02
- **Modell:** Claude Opus 5 (`claude-opus-5`), eine Session, keine Subagenten
- **Entscheidungstafel:** im Skript `scripts/ingest/wzb/wzb-breve-wortart.py`, nicht in
  einer Datendatei. Sie ist der eigentliche Befund und soll mit dem Diff gelesen werden.
- **Kontext je Fall:** Zielvers plus Vor- und Folgevers plus ein Umfeldfenster, alles
  aus `ingest/wzb/235-breve/review-faelle.csv`, erzeugt vom Vorlauf

## Zuschnitt

Neu-Annotation nackter Tokens, kein Umhängen: alle 98 tragen bisher weder `@lemmaRef`
noch `@pos`. Das Ziel-Lemma steht fest (genau ein Treffer in `variants.xml`), offen ist
allein die Wortart, weil das Lemma mehrere führt.

29 Ziel-Lemmata, 63 Schreibformen. Die drei größten Gruppen: `tœten` 15, `bœse` 13,
`hœren` 13.

## Die neun Regeln

Jede Entscheidung nennt die Regel, unter der sie fällt. Die Regeln sind so gewählt, dass
sie an der Textstelle prüfbar sind und nicht am Sprachgefühl.

| Regel | Kriterium | Tag | Fälle |
|---|---|---|---:|
| R1 | Adjektiv mit Bezugsnomen in derselben Phrase, oder als Prädikat | ADJ | 15 |
| R2 | Adjektiv besetzt die Nominalstelle selbst (Substantivierung) | NOM | 9 |
| R3 | modifiziert ein Verb oder ein Adjektiv | ADV | 4 |
| R4 | Vollverb (finit, Infinitiv, Partizip) | VRB | 41 |
| R5 | Modalverb mit abhängigem Infinitiv | VEM | 7 |
| R6 | Hilfsverb zum Partizip | VEX | 1 |
| R7 | Präposition mit Rektion | PRP | 7 |
| R8 | Partikel eines Partikelverbs | ADV | 2 |
| R9 | Substantiv | NOM | 3 |

R8 ist keine Erfindung dieses Laufs, sondern POS-TAGSET.md §6.5: einen zwanzigsten Tag
`PART` gibt es nicht (KZWs Entscheidung vom 2026-07-08), Partikeln werden bis auf
weiteres `ADV` getaggt.

**`GRA` wird nie geschrieben.** **Neun** der 29 Ziel-Lemmata führen den Tag in `posAll`
(`grôz`, `hôch`, `bœse`, `schœne`, `süeʒe`, `blœde`, `tôrlich`, `lobelich`, `vor`), aber
POS-TAGSET.md §3 führt ihn als aufgegeben (Steigerung und Superlativ sind `ADJ`) und
§6.3 Invariante (d) verbietet ihn im Ausgang eines Batches. Die Steigerungsformen unter
den 98 (`bŏsten`, `hŏchste`, `hŏhsten`, `schŏnste`, `grŏsseren`, `hŏher`) bekommen
deshalb `ADJ` oder `NOM`, je nach R1 oder R2. Es sind Komparative **und** Superlative:
`grŏsseren` und `hŏher` sind Komparative.

## Drei Entscheidungen sind am Bestand gemessen, nicht geraten

**1. Substantiviertes Adjektiv, `ADJ` oder `NOM`?** Grundgesamtheit sind **sieben der
acht** ADJ/NOM-Lemmata dieser Menge. `roete` (`lemma_10840`) bleibt draußen, weil es ein
Substantivlemma mit Adjektivlesart ist und seine `NOM`-Belege die Messung überdecken
würden, ohne etwas über Substantivierung zu sagen (mit ihm 201 Belege im heutigen Stand,
ohne ihn 69). Diese sieben hatten vor dem Lauf 60 aufgelöste `NOM`-Belege, alle außerhalb
der WZB, alle einzeln angesehen. Sie zerfallen in zwei Bauarten, die beide hier
einschlägig sind:

- **echte Substantivierungen:** *wir nemen gut unde bose in unser gewalt*, *kere von dem
  bosen unde tu das gute*, *vf das aller hoechste*, *under dien boesen*
- **die -î-Abstrakta, die unter dem Adjektivlemma geführt werden:** *in der grössin*,
  *von der schoeni des brútgovmes*, *dur mine brodi*

Das Haus taggt beide Bauarten `NOM`. Der rohe Anteil täuscht (60 `NOM` gegen rund 27.000
`ADJ`), weil attributive Verwendung um Größenordnungen häufiger ist, nicht weil diese
Bauarten anders getaggt würden.

**Zwei der 60 sind keine von beiden**, gefunden im Review und nicht von mir: `AC3_22210_11`
(*seit das nie so boser man wart*) ist attributiv und im Bestand als `NOM` fehlgetaggt,
`ADP_3500500_2` (*vf daz hoch zit*) ist die getrennt geschriebene Hälfte von *hôchzît*.
Beide widerlegen den Befund nicht, sie begrenzen seine Umkehrung: aus einem `NOM`-Tag
folgt nicht, dass eine Substantivierung vorliegt.

**2. `umbe sus/sust`, `PRP` oder `ADV`?** Zählvorschrift: Tokens mit `@lemmaRef` auf
`lemma_6422`, deren unmittelbarer Nachfolger MHG-normalisiert *sus*, *sust* oder *suz*
ergibt. Das sind 112 Vorkommen, davon 107 unaufgelöst als `ADV PRP` und 5 aufgelöst. Alle
5 sind `PRP`, keines `ADV`. Die feste Wendung ändert die Rektion nicht. Nimmt man die
v-Schreibungen *svs* und *svst* dazu, sind es 126; das Verhältnis bleibt.

**3. `vor`, Präposition oder Partikel?** Gemessen über alle aufgelösten `vor`-Belege,
aufgeteilt nach der Wortart rechts. **„Nominalphrase rechts" heißt:** der `@pos`-Wert des
Folgetokens schneidet sich mit `{DET, POS, PRO, NOM, NAM, NUM, ADJ}`. Das Legacy-`ART`
fällt damit in „etwas anderes" (dort 51 `PRP` gegen 2 `ADV`). Beginnt rechts eine
Nominalphrase, steht `vor` 738 mal `PRP` gegen 6 mal `ADV`; sonst 158 mal `ADV` gegen 105
mal `PRP`. Das Kriterium trägt in die `PRP`-Richtung sehr klar und in die `ADV`-Richtung
nur deutlich, weshalb einer der vier `vor`-Fälle mittlere Konfidenz trägt und liegen
bleibt.

## Anwendungsregel

Annotiert wird nur bei hoher Konfidenz, Regel wie in #369. Alles andere bleibt
byte-identisch stehen und geht in `review-faelle.csv`, mitsamt der Lesart, die dagegen
spricht.

| Aktion | Anzahl |
|--------|-------:|
| ANNOTATE | 89 |
| REVIEW | 9 |

Wortarten der 89: `VRB` 41, `ADJ` 15, `NOM` 12, `VEM` 7, `PRP` 7, `ADV` 6, `VEX` 1.

`@corresp` und `@ana` werden bewusst nicht gesetzt: unverändert die Begründung des
Vorlaufs (jede Schreibung bräuchte unter ihrem Ziel-Lemma eine neu geprägte Typnummer,
und neue Typen sind genehmigungspflichtig; die Sense-Zuordnung ist kuratorisch). Die 89
landen damit in derselben Lage wie die 66 und wie die 52.097 anderen WZB-Tokens aus #370.

## Der Rückhalt: 9 Fälle

**Fünf wegen mittlerer Konfidenz.** Bei ihnen ist die Wortart offen, die Gegenlesart steht
in `review-faelle.csv`: `gewŏnlichen` (ADV gegen ADJ), `pŏse` in *grose wunder vnd pŏse*
(ADJ gegen NOM), `lŏblich` (ADJ gegen ADV), `grŏsers` (NOM gegen ADJ), `vŏr` in
*czihende vŏr in dem ein gange* (ADV gegen PRP).

**Vier, bei denen gar nicht die Wortart offen ist, sondern das Ziel-Lemma nicht passt.**
Das ist der wichtigste Befund dieses Laufs, und keiner davon ist ein Annotationsfall:

| xml:id | Form | Kandidat | Was im Vers steht | Richtig wäre |
|---|---|---|---|---|
| `WZB_11rb_21_2` | `grŏsen` | `grôz` | *wil grŏsen deinen namen*, das Verb | `lemma_2535` *grôzen* `VRB`, 13 Belege in 11 Texten |
| `WZB_213ra_5_0` | `hŏrde` | `hœren` | *die vorporgin hŏrde des sandes*, der Hort | `lemma_2908` *hort* NOM |
| `WZB_26vb_34_5` | `tŏch` | `ziehen` | *von den tŏch XXVIII GENE tern*, halbes *tŏchtern* | `lemma_6135` *tohter* NOM, nach Zusammensetzung |
| `WZB_54vb_23_3` | `tŏch` | `ziehen` | *von siben tŏch EXO ter*, halbes *tŏchter* | dito |

**Für alle drei existiert das richtige Lemma bereits**, und das ist der Punkt, an dem der
erste Entwurf dieses Logs falsch war: er behauptete, ein Verblemma zu *grôz* gebe es
nicht. Es gibt es, `lemma_2535` *grôzen* `VRB`, morphologisch auf `lemma_2534`
zurückgeführt, 13 Belege in 11 Texten. Gefunden hat den Fehler der Review. Meine Suche
war über die normalisierte Form *groezen* gelaufen, während `grôzen` auf *grozen*
normalisiert: die Abfrage konnte die Anwesenheit gar nicht darstellen.

**Warum der Matcher es nicht finden konnte, ist strukturell und kein Datenfehler.** Die
flektierte Adjektivform *ist* der Verbinfinitiv. `grozen` trägt im Korpus **1.223 Tokens**
mit `@lemmaRef` auf `lemma_2534` und `@pos="ADJ"` (*mit grôzen êren*, *der grôzen
geschiht*), und `variants.xml` hält je Normalform genau ein Ziel. Also zeigen *grozen*,
*groezen* und *groesen* alle auf `lemma_2534`, und jedes Nachschlagen, das nur
`variants.xml` liest, landet zwangsläufig dort.

Die dreistufige Auflösung des Frontends ist davon **nicht** betroffen: für die Eingabe
*grôzen* trifft schon Stufe 1 auf `lemma_2535`, Stufe 2 kommt gar nicht dran. Betroffen
ist der Ingest-Matcher, der ausschließlich `variants.xml` konsultiert. Das ist genau
Kategorie C der #259-Messung, „eigenes Lemma, variants zeigt anderswohin", dort mit 361
Fällen beziffert: #259 hat die Menge ohne Beispiel, dieser Fall ist das Beispiel ohne
Menge.

Die offene Frage an KZW ist damit enger und anders: die 13 Belege sind überwiegend
intransitiv (*min herze grôzet*, *der jamer grozzet*), die WZB-Stelle ist transitiv
(*magnificabo nomen tuum*). Ob sie unter `lemma_2535` gehört oder ein eigenes Lemma
braucht, ist eine philologische Entscheidung.

Die Zeilen in `variants.xml`, die die falschen Zuordnungen erzeugen, sind für sich
**richtig**: `hoerde → lemma_2885` ist ein Präteritum von *hœren*, `toech → lemma_7861`
eines von *ziehen*. Falsch sind sie nur für diese Tokens. Ein anderes Lemma zu setzen als
das gemessene Kandidatenlemma ist eine philologische Entscheidung und keine Wortartwahl;
sie gehört zu KZW.

Die beiden `tŏch` sind **kein Wortartproblem, sondern ein Segmentierungsfehler**: ein
Blatt- oder Buchmarker (`XXVIII GENE`, `EXO`) steht mitten im Wort und erzeugt zwei
Scheintoken. Dieselbe Bauart wie Punkt 1 desselben Tickets (die 17 Tokens mit dem
literalen Escape für das Leerzeichen), nur andersherum: dort waren zwei Wörter in einem
Token, hier ist ein Wort auf zwei verteilt.

### Und der Fall ist nicht einzeln

In der Rohdatei nachgesehen statt in der Umfeld-Spalte: bei `WZB_54vb_23_3` folgt auf das
Token `tŏch` ein `<pb n="55r"/>`, ein `<cb n="a"/>`, ein `<lb n="1"/>`, ein `<w>` mit dem
Text `EXO` und dann `<lb n="2"/>` mit `<w>ter</w>`. Die Ursache ist damit nicht der
Marker, sondern seine Kodierung: **laufende Kolumnentitel und Kapitelzahlen stehen als
`<w>` im Textfluss**, wo nach der Strukturbereinigung aus #66 `<fw>` beziehungsweise
`<head>` plus `<milestone>` stünde.

Gemessen: **928 der 6.836 unannotierten `<w>` der WZB** bestehen ausschließlich aus
Großbuchstaben (`IOSUE` 104, `EXO` 88, `DUS` 88, `NUM` 86, `ERI` 86, `DEUTRO` 79,
`NOMIUS` 79, `GENE` 76, `SIS` 76), also die zeilenweise zerlegten Buchtitel des
Pentateuch.

**Die Zählvorschrift steht dazu, weil zwei richtige Zahlen kursieren.** 928 zählt Tokens,
die mindestens einen Buchstaben und keinen Kleinbuchstaben tragen; 927 zählt zusätzlich
rein alphabetisch (`str.isalpha()`). Die Differenz ist genau ein Token, `W` gefolgt von
einem weichen Trennstrich (U+00AD). Beide Zahlen sind richtig, und ohne die Vorschrift
korrigiert die nächste Session die eine in die andere.

Zählvorschrift für die zerrissenen Wörter: eine Folge aus einem unannotierten `<w>`,
einem oder mehreren reinen Großbuchstaben-`<w>` ohne `@lemmaRef` und wieder einem
unannotierten `<w>`. 23 Fundstellen, davon eine ein Artefakt des gleitenden Fensters. Von
den 22 verbleibenden sind nach Augenschein 18 ein zerrissenes Wort: `geschep|fet`,
`zukunf|tig`, `tŏch|tern`, `tŏch|ter`, `czou|berei`, `wis|sen`, `erwer|fen`, `ma|che`,
`ei|nes`, `op|ferten`, `ma|chte`, `veisti|keit`, `isra|hel`, `Nui|czig`, `Wen|ne`,
`vorkou|fen`, `besa|gunge`, `ho|rende`. Zwei sind unklar, zwei sind schlicht zwei Wörter
mit einem Kolumnentitel dazwischen.

Eine schärfere Zählung, die zusätzlich verlangt, dass die zusammengesetzte Form in
`variants.xml` steht und keine Hälfte für sich, findet nur **2**. Sie verfehlt genau die
Fälle, auf die es ankommt: `tŏchtern` steht wegen der Breve-Schreibung nicht im
Variantenbestand, und ein zerrissenes Wort ist typischerweise eines, das das Lexikon
nicht kennt. Die enge Zählung ist eine Untergrenze und als Kriterium untauglich; beide
Zahlen stehen hier, damit niemand die 2 für das Ergebnis hält.

Das ist ein eigenes Arbeitspaket: es braucht eine Kodierungsentscheidung und ändert bei
den 18 die Positionszählung ein zweites Mal.

## Dateien

- `diff-liste.csv` – alle 98 mit Entscheidung, Regel, Konfidenz, Beleg und Vers
- `review-faelle.csv` – die 9 zurückgehaltenen
- `config.json` – Rahmen und `revisionDesc`-Vorlage, Muster `369-stat/config.json`
