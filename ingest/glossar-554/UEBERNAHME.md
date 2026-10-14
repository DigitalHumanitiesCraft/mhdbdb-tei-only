# Glossar Kochbuchforschung ins Lexikon: Übernahme (#554, B1 bis B5)

Fortsetzung des [README](README.md) (Schritt 2, Prüfliste). Hier steht, was in `lexicon.xml`
gelandet ist, was nicht und warum. Entschieden haben KZW (Vorgaben im Ticket, 12./13.10.2026)
und die Koordination; die Sitzung `lauf-554` hat umgesetzt.

## Ergebnis in Zahlen

Das Glossar hat 189 mittelhochdeutsche Einträge (`sprachstufe` gmh). Ausgang je Eintrag in
[`zuordnung.tsv`](zuordnung.tsv):

| Ausgang | Einträge |
|---|---|
| zugeordnet (Bedeutung entschieden) | 120 |
| Prüfseite: Zuordnung offen | 17 |
| kein Kommentar (siehe unten) | 52 |
| **Summe** | **189** |

Die 120 zugeordneten Einträge teilen sich so auf:

| Verbleib | Einträge |
|---|---|
| als Notiz in `lexicon.xml` | 93 |
| Prüfseite, Gruppe B (größere Kürzung) | 22 |
| Prüfseite, Gruppe D (sachliche Rückfrage: 867 grandmangerie) | 1 |
| Prüfseite, Gruppe E (1905 huon, 2253 rëphuon) | 2 |
| zusammengeführt in einen anderen Eintrag (1900 henne in 1905, 2264 rëphenne in 2253) | 2 |
| **Summe** | **120** |

Die Prüfseite [`examples/review-pages/Glossar-554-Pruefung.html`](../../examples/review-pages/Glossar-554-Pruefung.html)
hat 47 Fälle: A 17, B 22, C 5 (nicht übernommene Einträge, die Katharina entscheiden soll), D 1, E 2.
Was dort steht, geht nicht in die Daten, bevor sie geantwortet hat.

Zählregel für die Lemmata mit kuratierter Aussage (ADR-018): Lemma-Records mit nichtleerem
`origin.resp`, `senses[].definitionResp` oder `senses[].commentResp` im gebauten Authority-Index.
Vorher 1 von 43.710, nachher 94 von 43.710 (1 Bestand plus 93). Gemessen mit demselben Zähler am
Index von `origin/main` (vor dem Rebase) und am neuen.

## Kriterien

**Mehrwert der Poetisierung** (Vorgabe der Koordination): übernommen wird sie, wenn sie über
„an dieser Stelle kommt das vor“ hinausgeht, nämlich bei Redewendung, Brauch, Sachinformation
oder lexikografischer Diskussion mit Ergebnis. Ohne Mehrwert (Bedeutung wiederholen, Stelle nur
zitieren) bleibt sie weg. Die enzyklopädische Information wird immer übernommen.

**Straffen** darf Wiederholungen und ausschweifende Formulierungen entfernen. Jeder entfallene
Teil ist eingeordnet:

- (a) Wiederholung,
- (b) ausschweifende Formulierung oder Randbemerkung ohne eigene Sachaussage (auch Literaturangaben,
  Links, Abrufdaten),
- (c) eigenständige Aussage, Differenzierung, Beleg oder Beispiel.

Nur (a) und (b): **gestrafft**, geht in die Daten, gleich wie stark der Text schrumpft. Mindestens
ein (c): **gekürzt**, geht auf die Prüfseite (Gruppe B), gleich wie wenig entfällt. Die Einordnung
steht in [`einordnung.json`](einordnung.json) (Schlüssel Glossar-ID, `c` = Nummern der Stücke aus
`entfallenes-suchen.py`; `c_text` = von Hand gefundene (c)-Stücke im Wortlaut, die die Suche nicht
meldet). Die Suche nach entfallenen Stücken ist ein Hilfsmittel (Wort-Dreiergruppen und
Inhaltswörter); sie meldet Umformuliertes als entfallen und kann stark Umformuliertes übersehen.
Sie hat eine bekannte Lücke: Sätze trennt sie nur vor Großbuchstaben und vor den Zeichen U+201E und
U+201A, nicht vor einem geraden Anführungszeichen, und ein Stück mit Fußnotenanker, URL, Seitenzahl
oder Literaturangabe gilt selbsttätig als (b). So blieb in brâte (606) der Satz zum „Armen Heinrich“,
in brâten (621) die Îwein-Fundstelle und in ei (2074) die Aussage zu den Gedichten des Königs vom
Odenwald unsichtbar; die erste Prüfungsrunde hat sie gefunden, die drei Einträge liegen deshalb auf
der Prüfseite (Gruppe B). Die Einordnung ist eine Stichprobenfrage für die Prüfung, kein Beweis.

**Nachprüfung über alle 93 übernommenen Einträge** (Auflage der Koordination): Die Regel „Fußnote,
URL, Seitenzahl, Literatur“ hat in 31 der 93 Einträge zusammen 61 Stücke mit 5.587 Zeichen selbsttätig
als (b) aussortiert. Alle 61 sind von Hand gegen die Fassung gelesen (34 Stücke ab 60 Zeichen in 20
Einträgen, 27 kürzere Einleitungssätze und Bruchstücke). Ergebnis: Fundstellen, URLs und
Literaturangaben in allen bis auf drei Einträge. In 1983 wilt, 1996 wiltbrât und 2009 zam (nom)
fehlten die Definition der Zwillingsformel nach Hofmeister und der Satz zu Synonymen und Antonymen
aus Fußnote [1]; beides steht jetzt wörtlich im Text, mit Zuschreibung („Wernfried Hofmeister
definiert eine Zwillingsformel wie folgt“), wie schon in wîn (1444) und brôt (2084). In sat (1525)
und slinden (1643) fehlt nur die englische Übersetzung der Redewendung; Entstehungszeit und
Gebräuchlichkeit stehen im Text. Zusammen mit den drei von der Prüfungsrunde gefundenen Einträgen
(606, 621, 2074, auf der Prüfseite) sind es sechs Einträge, in denen die Regel mehr als eine Fundstelle
verschluckt hat; drei davon liegen jetzt auf der Prüfseite, drei sind im Text ergänzt.

Kennzahl, kein Kriterium: Die 118 Kommentartexte zusammen haben 194.198 Zeichen gegenüber 289.860
in der mechanischen Vorstufe (Enzyklopädie plus übernommene Poetisierung).

Formatregeln: Kursivierungen werden zu Anführungszeichen („…“ für mhd. Formen und Zitate, ‚…‘ für
Bedeutungsglossen); Varianten, Literatur und externe Links sind keine Felder; die Quellenzeile
(„Quelle: Glossar Kochbuchforschung dig_ESTivum von Katharina Zeppezauer-Wachauer (2016-2026)“)
hängt `kommentare-einfuegen.py` an, nie von Hand. Urheberin ist allein
`contributors.xml#contrib_003`. Je Bedeutung gibt das Schema höchstens eine Kommentarnotiz her.
Der Wortlaut bleibt der des Glossars; `kommentare-pruefen.py` prüft nur Zeichen, nicht Wörter. Die
erste Prüfungsrunde fand in einer Stichprobe zwei Umformulierungen („er besteigt deswegen …“ statt
„bzw. er deswegen …“ in ei, „Nutzer*innen“ statt „jede/r/m Nutzer/in“ in brâte), beide sind auf den
Wortlaut des Glossars zurückgesetzt. Ob weitere stecken, ist über die Stichprobe hinaus nicht geprüft.
Das Feld `kuerzung` der ersten Entwürfe in `kommentare/*.json` ist entfernt (es widersprach an sieben
Einträgen der Einordnung); maßgeblich ist allein `einordnung.json`. Das Feld `kuerz_grund` ist ein
Entwurfsvermerk ohne Gewicht.

## Nicht übernommen, ohne Prüfseite

Poetisierung ohne Mehrwert (7), der Eintrag selbst bleibt zugeordnet oder entfällt ganz, Grund je
Eintrag in `zuordnung.tsv`:

- 331 zergeselle (nennt eine Stelle, keine weitere Aussage), 721 unernert (gibt die Bedeutung wieder),
  747 ungenôʒen (nur die Bedeutung), 777 unverzert (Bedeutung und eine Stelle), 797 ernern und
  1426 nern (nur die zwei Bedeutungen, die das Lexikon schon führt), 1813 slucken (Belegzitat mit
  Übersetzung).

Kein Inhalt (32): 135 genieʒen, 152 kunrieren, 160 laben, 218 vermesten, 268 wirten, 761 enhungern,
791 erdürsten, 832 ëʒʒenzît, 845 ëʒʒer, 850 ëʒʒgeverte, 861 ëʒʒhaft, 988 hungergît, 993 hungerjâr,
1002 hungerlëben, 1059 hungerrîche, 1136 labunge, 1153 Lêrennapf, 1192 lîprât, 1242 maʒgenôʒe,
1270 muoshûs, 1290 nahtëʒʒen, 1808 verslûchen, 2539 apfel, 2542 muos, 2587 brâmberstrûch,
2593 ërtber, 2619 lôrber, 2625 reckholterber, 2630 wëcholterber, 2635 wînber, 2651 wîntrûbe,
2654 trûbe.

Nur Verweis (6): 539 etzen (auf atzen), 1434 nieʒen (auf genieszen), 1571 saten und 1596 setigen
(auf sat und seten, mit Formbemerkung), 1984 wilde (auf wilt), 2017 zam (adj) (auf zam, Nomen).

Dubletten (2): 694 enbîʒen (neg) spiegelt den **tragenden Eintrag 697 enbizen** mit denselben
Worten; 2248 pardrîsekîn ist zu 99 bis 100 Prozent gleich mit dem **tragenden Eintrag 2241
pardris**.

Auf der Prüfseite, Gruppe C (5): 1703 hërrenëʒʒen, 2116 blancmanger, 2158 lêrchenvuoʒ (kein Lemma
im Bestand, wir legen keine an), 560 atze (das einzige Lemma „Atze“ ist ein Personenname),
1611 slëc (das Feld nennt nur die Bedeutungen, die das Lexikon schon führt).

## Gleiche Texte unter verschiedenen Titeln

Mindestens 10 Gruppen (21 Einträge, Untergrenze, nicht erschöpfend gesucht) tragen dieselbe
enzyklopädische Information unter verschiedenen Titeln. Beschlossen: je Lemma übernehmen. Gruppen:
wirt, wirtliute, wirtshûs; eʒʒichkruoc, eʒʒichvaʒ; brâte, brâten (nur der Anfang); hungerlachen,
hungertuoch; jûs, jûsen; mangerîe, manger; nar, narunge; lamprîde, niunouge; henne, huon;
ant, gans. Bei den Poetisierungen sind latech und purzel ähnlich.

## Zusammengeführte Paare

Ein Lemma trägt je Bedeutung nur eine Notiz. Zwei Paare zeigen auf dieselbe Bedeutung:

- **henne (1900) und huon (1905)** auf `lemma_2961_sense_4753`. Die enzyklopädischen Teile sind
  fast wortgleich (1.628 und 1.632 Zeichen, Ähnlichkeit 0,996 nach `difflib`). Die Poetisierungen
  sind verschieden (1.019 und 13.841 Zeichen in der Vorstufe); der Poetisierungsteil von henne ist
  in den Text von huon eingegangen. Das ist mehr als gleicher Text, deshalb Prüfseite, Gruppe E.
- **rëphenne (2264) und rëphuon (2253)** auf `lemma_21938_sense_35900`. Der enzyklopädische Teil von
  rëphenne ist nur der Verweis „s. Lemma rephuon“; seine Poetisierung (1.089 Zeichen in der Vorstufe)
  ist in den Text von rëphuon eingegangen. Ebenfalls Gruppe E.

## Nebenbefunde

- **grandmangerie (867)** nennt „Ulrich von dem Türlin“ als Verfasser der „Crône“. `works.xml`
  führt „Diu Crône“ (`work_363`, Sigle CRO) mit `persons.xml#person_867`, Heinrich von dem Türlin;
  Ulrich von dem Türlîn ist `person_46`. Der Text bleibt wörtlich, die Rückfrage steht auf der
  Prüfseite (Gruppe D), der Eintrag geht erst nach der Antwort in die Daten.
- **brôt (2084)**: Das Feld „Enzyklopädische Information“ beginnt mit „Informationen aus: Peter C. A.
  Schels: Kleine Enzyklopädie des deutschen Mittelalters“, einer Internetadresse und „(17.11.2017)“;
  der gesamte Rest des Feldes (rund 8.400 Zeichen) steht in einem Zitatblock (`<blockquote>`).
  Der Block wurde nicht mit der Quelle abgeglichen. Unter KZWs Namen und ihrer Quellenzeile soll
  kein fremder Text stehen: Prüfseite, Gruppe B, mit drei Wegen (Schels-Nachweis, eigene
  Zusammenfassung, weglassen).
- Einige Glossartexte zitieren Dritte mit Quellenangabe (Blaschitz, Hanauska, Schulz, Wikipedia
  „Pfaffenschnittchen“); sie bleiben als Zitate stehen.

## B4: Einklappfunktion (Vorschlag, kein Code)

Länge der Kommentartexte (Zeichen), gemessen an `kommentare/*.json`: 93 Texte für die Daten, Median
882, Dezile 181 / 378 / 550 / 697 / 882 / 1.140 / 1.514 / 2.009 / 2.597, Maximum 5.982. Über 600
Zeichen: 61 von 93; über 1.000: 44; über 2.500: 9. Zählt man die 25 Texte der Prüfseite hinzu (22 in
Gruppe B, 3 in D und E; zusammen 118 Texte mit Text), liegt der Median bei 1.143, das Maximum bei
10.191 und 23 Texte über 2.500.

Die Lemmaseite setzt den Kommentar als einen Absatz in einen Container von ungefähr 110 Zeichen
je Zeile (Schätzung aus `max-w-4xl` und `text-sm`, nicht im Browser gemessen), 1.000 Zeichen sind
also gut neun Zeilen. Vorschlag: den Absatz auf etwa sechs Zeilen (rund 650 Zeichen) begrenzen
(`line-clamp`), darunter ein Knopf „Weiterlesen“ / „Weniger“ mit `aria-expanded`, nur wenn der Text
die Grenze überschreitet (Vergleich von `scrollHeight` und `clientHeight`). Der Playground-Lemma-Explorer
zeigt den Kommentar ebenfalls und bräuchte dasselbe. Das berührt `lemma/` und `assets/js/`, ist
also eine eigene Änderung mit Test und Abnahme.

## B5: Verweise auf das Portal der Pflanzen des Mittelalters (Helmut W. Klug)

Quelle: <http://medieval-plants.org/mps-daten/> (Redaktion Helmut W. Klug, technische Leitung Roman
Weinberger), Inhalte unter **CC BY-NC-SA 3.0 AT** laut Seitenfuß. Übernommen sind **nur Titel, URLs
und unsere Zuordnungen, kein Seitentext**. Die Rohseiten liegen nicht im Repositorium.

Abruf am 14.10.2026 mit `curl` über http, nur GET, nacheinander mit vier Sekunden Pause, ohne Crawlen
(`robots.txt` sperrt nur `/wp-admin/` und `/wp-includes/`): **31 Abrufe**, nämlich die Sprachenübersicht,
die Liste `languages/gmh/` (alle mhd. Einträge auf einer Seite), die Seite `gartenerdbeere/` und
`brestelinc-2/` als Probe, 15 mhd. Seiten und 12 übergeordnete Pflanzenseiten.

**Offen:** Die Sprachenübersicht nennt 1.428 mhd. Einträge, die Liste enthält 1.427. Der Unterschied
von 1 ist nicht geklärt; ausgewertet sind die 1.427.

**Tabelle [`klug-abgleich.tsv`](klug-abgleich.tsv)** (1.427 Zeilen; Spalten `slug`, `titel`,
`mhd_url` = Link zum mhd. Quelleintrag, `treffer`, `lemma_id`, `lemma`, `pflanzenseite_url`,
`pflanzenseite_titel`, `vermerk`). Abgleich der Titel über `mhg_normalizer` gegen die normalisierte
Lemmaform und die Varianten des Authority-Index 1.9.25:

| Treffer | Einträge |
|---|---|
| auf ein Lemma | 415 |
| auf eine Variante | 51 |
| keiner | 961 |
| **Summe** | **1.427** |

Ein Treffer ist ein **Kandidat**, keine Zuordnung: gleiche Schreibung kann ein anderes Wort sein
(`alant` trifft zwei Lemmata). Linkziel ist nach KZWs Vorgabe (13.10.) die **übergeordnete
Pflanzenseite**. Die Seite wurde nur für die 15 von 466 Treffern abgerufen, deren Lemma unter den
Lemmata der Glossar-Zuordnung liegt (apfel, brâmber, ërtber, heidelber, jeroffel, kâriôfel, koste,
latech, lôrber, nagel samt der Variante negellîn, purzel, trûbe, wîn, wîntrûbe). Für die übrigen 451
steht im `vermerk` „nicht abgerufen (Umfang)“.

**Tabelle [`klug-pflanzen.tsv`](klug-pflanzen.tsv)**: zu jeder der 12 abgerufenen Pflanzenseiten ihre
mhd. Namen, mit unserem Lemma, falls es eines gibt, und der Angabe, ob es dasselbe Lemma ist wie beim
Glossar-Treffer (`gleich`) oder ein anderes (`anders`). Das ist der Fall, auf den es ankommt: derselben
Pflanze sind bei Klug mehrere mhd. Namen zugeordnet, die bei uns auf verschiedene Lemmata zeigen.
Beispiele: unter „Echter Weinstock“ stehen neben `wîn` auch `rebe`, `wînrebe`, `wînrebez`, `wînstoc`,
`lantwîn`; unter „Weintraube“ neben `trûbe` und `wîntrûbe` auch `triubel` und `wînbere`; unter
„Gewürznelke“ neben `nagel`, `kâriôfel` und `jeroffel` auch `negelkîn` und `kâriôfelrîs`.

KZWs Beispiel `brestelinc` (Garten-Erdbeere) tritt in den 15 Treffern nicht auf: `brestelinc` ist bei
uns kein Glossar-Lemma, und der Glossar-Eintrag `ber` hat bei Klug keinen gleichlautenden Titel. Die
Seite `gartenerdbeere/` ist abgerufen und nennt als einzigen mhd. Namen `brestelinc`. Umgekehrt: Von
189 Glossar-Titeln haben 15 einen gleichlautenden Klug-Titel, 174 keinen. Bei 13 davon ist es dasselbe
Lemma. Bei zwei Titeln gibt es kein Glossar-Lemma (kein Inhalt): `brâmberstrûch` (bei Klug ohne
Lemma) und `wînber` (bei Klug über die Variante auf `wînbere`, `lemma_24316`).

**Fehlende Formen** sind die 961 Zeilen mit `treffer` = keiner. Die Liste ist **mechanisch**: sie
unterscheidet nicht, ob eine Form eine Schreibvariante eines vorhandenen Lemmas oder ein fehlendes
Lemma ist. Für 120 davon steht im `vermerk` „nächste Schreibung“ (Editierabstand 1 zu einem Lemma, nur
als Hinweis auf eine Schreibvariante), für die übrigen 841 „kein Lemma, keine Variante, keine nahe
Schreibung“. Es wurden keine Lemmata oder Varianten angelegt. Kontrollwerte aus KZWs Beispielen:
`mosber` (`mosber-2`) und `ertberblat` stehen in der Liste als „keiner“.

**`dornber`** (KZWs drittes Beispiel) steht **nicht** in der gmh-Liste. Gesucht wurde: der Rohtext der
Liste nach „dorn“ als Teilstring (Treffer: dornboum, dornbusch, dorn, dornach, dornslehe, dornstûde,
dornswam, dornwurz und weitere zusammengesetzte Namen, keiner mit „ber“); alle Linktexte der Liste,
der 15 mhd. und der 12 Pflanzenseiten normalisiert (`mhg_normalizer`, Bindestriche entfernt) auf „dorn“
mit „ber“; der Rohtext der 27 Einzelseiten, darunter die Pflanzenseiten von `brâmber` (Brombeere),
`heidelber` (Blaubeere) und `ërtber` (Walderdbeere), auf `dorn-?b[eêë]r`: kein Treffer. Als Kontrollwert
trifft „ber…“ auf denselben Pflanzenseiten (47 Vorkommen auf Brombeere, Walderdbeere, Blaubeere).
Ob Klug `dornber` in einer anderen Sprachstufe (Frühneuhochdeutsch, Deutsch) führt oder nur in einem
Eintragstext nennt, wurde **nicht** untersucht; das wären weitere Abrufe.

Nicht Teil dieses PR: Datenmodell für einen Klug-Link an der Lemmaseite (Schema- und Frontend-Entscheidung).

## Nachmessen

```
python -X utf8 -E -P scripts/ingest/glossar-554/vorstufe-bauen.py <vorstufe.json>
python -X utf8 -E -P scripts/ingest/glossar-554/kommentare-pruefen.py <vorstufe.json>
python -X utf8 -E -P scripts/ingest/glossar-554/entfallenes-suchen.py <vorstufe.json> [Glossar-ID ...]
python -X utf8 -E -P scripts/ingest/glossar-554/kommentare-einfuegen.py [--schreiben]
python -X utf8 -E -P scripts/ingest/glossar-554/pruefseite-bauen.py <vorstufe.json>
```

`kommentare-einfuegen.py` bricht ab, wenn eine Bedeutung schon eine Kommentarnotiz trägt; im
Zweitlauf nach `--schreiben` ist das Absicht.
