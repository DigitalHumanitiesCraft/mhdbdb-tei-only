# Kandidatenliste #702: absichtliche Doppeldeutigkeit

Subauftrag aus #602 auf Wunsch von @wachauer (10.11.2026): Beispiele aus dem Korpus sammeln, an denen eine Stelle absichtlich zwei Bedeutungen trägt, wie `naschen` bei Oswald von Wolkenstein. Mögliche Nachnutzung laut KZW: Aufsatz, Forschungsantrag, Feature.

**Am Korpus und am Lexikon ändert diese Sammlung nichts.** Ob ein Beleg zwei Bedeutungen bekommt, entscheidet KZW je Fall in der Spalte `Entscheidung` von `kandidaten.tsv`. Zusammengestellt am 17.11.2026 auf `main` `96e3c8245`, erweitert am 27.11.2026 auf `main` `f3cad6fc3` nach KZWs drei Kommentaren in #702 vom selben Tag (08:54, 09:01, 09:01).

Dateien:

- `kandidaten.tsv`: die Kandidaten, eine Zeile je Token.
- `vergleich.tsv`: Vergleichsmaterial (Fruchtbilder des Körpers, dræjen-Handwerksbilder). Das sind keine Kandidaten.

## Material

| Quelle | Stand |
|---|---|
| KZWs Antwort zu `naschen` in #602 (10.11.2026) mit Hofmeister 2011 und Marold 1995 | gelesen im Issue. Hofmeister und Marold selbst nicht gelesen |
| Aufsatz Borek, Zeppezauer-Wachauer, Ketschik: „Eindeutig Uneindeutig. Zur Modellierung von Unschärfe in der Mediävistik", Blog *Mittelalter*, 16.02.2022, https://doi.org/10.58079/rha5 | **nur in Fragmenten gelesen.** Die Seite (mittelalter.hypotheses.org/27658) sperrt automatische Abrufe (Anubis). Über WebFetch kamen Zusammenfassung und kurze Zitate, der Wortlaut ist nicht am HTML geprüft |
| Auszug aus KZWs Dissertation, zwei Screenshots in #602 (Fußnote 202) | gelesen, die Bilder waren ohne Login abrufbar |
| Die in Fn. 202 zitierte Literatur (Hofmeister 2005b, Müller 1986, Wackernagel, Fischer) | nicht gelesen |
| Kommentare und Forschung zu Walther, Oswald Kl. 76 und 83, Sperber, Häslein | nicht gelesen, in der Tabelle als „ungeprüft" geführt |
| KZWs Dissertation, Dateistand `20200319_DissPubl_ZeppWach.docx` | **von dieser Zusammenstellung nicht gelesen.** Alles Folgende steht im Kommentar vom 27.11.2026, 08:54. Dort heißt es: gezielt gelesen wurden die Abschnitte zu Nahrung und Sexualität, zu fruktualen Sexualmetaphern und zu den Birnen bei Neidhart samt Fußnoten, keine vollständige Durchsicht. Die genannten Forschungspositionen sind in der Diss. gelesen, nicht an den Originalen geprüft. Werk-, Lied- und Versangaben folgen der Diss. Seiten der Diss. werden nicht genannt, weil ihre Paginierung nicht am gerenderten Dokument geprüft ist |
| Aufsatz Katharina Zeppezauer-Wachauer: „Erotische Narrative. Mit der Mittelhochdeutschen Begriffsdatenbank (MHDBDB) auf den Spuren kulinarischer Sexualmimesis", S. 69–93, https://doi.org/10.1515/9783110714340-005 | **von dieser Zusammenstellung nicht gelesen.** Nach dem Kommentar vom 27.11.2026, 09:01: das PDF ist einschließlich der Fußnoten gelesen und mit der Diss.-Sammlung verglichen. Seitenangaben sind Druckseiten. Die zitierte Sekundärliteratur ist nicht eingesehen. Die Trefferzahlen und Systembeschreibungen im Aufsatz beziehen sich auf den damaligen Arbeitsstand, nicht auf den heutigen TEI-Bestand |
| Katharina Zeppezauer-Wachauer und Helmut W. Klug: „Die Wurzel sollst du genießen": Kulinarische Sexualmetaphorik im Mittelalter, DER STANDARD, Blog Historische Kulinarik, 10.10.2018 | **von dieser Zusammenstellung nicht gelesen.** Nach dem Kommentar vom 27.11.2026, 09:01: vollständig gelesen. Die dort genannte Edition (Ehlert, *Münchner Kochbuchhandschriften aus dem 15. Jahrhundert*, 1999) ist nicht geprüft |

Aus den drei neuen Quellen steht in diesem Ordner nichts im Wortlaut, nur Stellenangaben und eigene Zusammenfassung. Wörtlich zitiert werden nur mittelhochdeutsche Verse aus dem Korpus.

Was der Aufsatz von 2022 zum Thema sagt (Fragmente): mittelalterliche Dichter bedienten sich „häufig absichtlicher Ambiguitäten", es gebe Daten, die „gar nicht aufgelöst bzw. disambiguiert werden sollen, da ihre Unschärfe die poetologische Absicht des Textes ist", genannt werden Oswald von Wolkenstein, Neidhart und „Walther von der Vogelweide mit seinem *roten küssen*". Als Beispiel für Mehrdeutigkeit im Lexikon steht dort mhd. *trache* („Reptilien" und „Fantastische Tiere"). Das ist eine Eigenschaft des Lexikoneintrags, keine Stelle, und steht deshalb nicht in der Liste.

Die Diss. (Fn. 202) nennt drei Neidhart-Fälle, alle drei sind in der Liste: Minne und „Drogen" in SL 15 = SNE I: R 22 (Hofmeister 2005b: „Die kunstvolle Vagheit seines Texts erlaubte es seinem Publikum, das Gehörte gemäß eigenem Deutungsvermögen zu ‚komplettieren'"), das Wengling-Lied (c 7, f 12) und das Lied vom *hârein vingerlein* (R 40 / d 7 / c 91). Zu Letzterem schreibt sie, es sei „auch nicht gerade das, was man als ‚unscharf' bezeichnen würde", und benennt die Schwierigkeit „klar abzugrenzen, wann es sich um eine Metapher und wann um eine absichtliche Doppeldeutigkeit handelt".

## Kriterien

Stand 27.11.2026, nach KZWs Vorschlag im Kommentar von 08:54. KZW hat der Richtung zugestimmt. Eine einzelne Bedeutungsannotation ist damit nicht entschieden.

**Zwei Fragen werden getrennt.** Ihr Ausgangseinwand: beim roten Vogel im Kloben ist das sexuelle Geschehen deutlich erkennbar, und trotzdem bleibt die Stelle metaphorisch. „Nur erotisch" beschreibt den Gegenstand, nicht die sprachliche Darstellung. Deshalb fragt die Sammlung zweimal:

1. **Wie sicher ist die sexuelle Bedeutung?** Spalte `sexuelle_bedeutung_evidenz`, Werte `gesichert`, `gut begründet`, `möglich`, `offen`.
2. **Wie wird die wörtliche Bildwelt eingesetzt?** Spalte `status_woertliche_ebene`, Werte `zugleich erzählte Handlung`, `durchgeführtes Bild`, `punktuelle Metapher`, `expliziter Vergleich`, dazu `offen`.

Eine eindeutig erkennbare sexuelle Referenz beseitigt die kulinarische oder andere Bildlichkeit nicht. Der Aufsatz (S. 82–83) beschreibt Oswalds Birnenbild als eindeutig erkennbar, obwohl die Birnen nicht ausdrücklich Brüste heißen. Eindeutigkeit des Gemeinten und Fortbestehen der Metapher sind zwei Merkmale, und zwei gleichzeitig tragfähige Lesarten sind ein drittes.

**Die Kriterien vom 17.11.2026 beschreiben einen Teilbestand.** „Zwei Lesarten tragen den Vers je für sich" und „Der Text löst nicht auf" treffen einen wichtigen Teil absichtlicher Doppeldeutigkeit. Als Ausschlusskriterien für das ganze Vorhaben taugen sie nicht: Fälle wie der rote Vogel, das hârîn vingerlîn oder das Wurzelessen im Ring werden unterschieden, nicht ausgesondert. Die alten Kriterien bleiben als Merkmale dieses Teilbestands stehen:

- Die wörtliche Oberfläche bleibt kohärent (Geld verteilen, Gras mähen, Vögel fangen, ein Spiel spielen), die zweite Lesart ebenso.
- Ein Signal im Text zeigt die Absicht: eine Häufung gleichgerichteter Bilder im selben Lied, Gattung und Rolle (Rollenlied, Pastourelle, Schwankmär), eine Pointe, eine Figur, die das Wort missversteht.
- Der Text lässt das Publikum „komplettieren" (Hofmeister nach Fn. 202).
- Ein Forschungs- oder Kommentarbeleg hebt die Einschätzung, ist aber nicht Bedingung.

Die Spalte `Einstufung` (stark, mittel, schwach) hängt an diesen alten Kriterien. Sie bleibt an den 26 Zeilen vom 17.11.2026 stehen, die neuen Zeilen haben `nicht vergeben`.

**Wortannotation und Bildlichkeit bleiben getrennt.** Eine Zeile verankert ein Token, die Doppeldeutigkeit kann aber auf Vers-, Strophen- oder Szenenebene liegen (Birnenquotient, Wurzelessen, Buhlschaft auf dem Baume). Eine mitgeführte Bildwelt heißt nicht, dass jedes beteiligte Wort zwei lexikalische Bedeutungen bekommt. Bei *priet* in NEIR 31 etwa behauptet weder die Diss. noch die Zeile eine zweite Wortbedeutung von *brâten*.

**Keine feste Gleichung „Birne = X".** Nach dem Aufsatz (S. 85) bezeichnet die Birne in den erhobenen Belegen meist die Brüste, seltener den ganzen Frauenkörper und nur vereinzelt vielleicht die Vulva, gegen die ältere Zuordnung zu Vulva oder Gesäß. Der STANDARD-Beitrag nennt bei Keller Nr. 9 auch eine Zuordnung zum männlichen Geschlecht. Dasselbe gilt für Nuss, Apfel, Rübe und Wurzel: entschieden wird an der Stelle, nicht am Wort.

### Wie die Werte gesetzt sind

Alle Werte der vier Felder sind Vorschläge dieser Zusammenstellung, keine Entscheidung KZWs.

- **`sexuelle_bedeutung_evidenz`** folgt dem, was KZW oder die von ihr genannte Quelle zur Stelle sagt: `gesichert`, wo sie das Geschehen deutlich oder eindeutig nennt oder schon entschieden hat (naschen, roter Vogel, Wengling, hârîn vingerlîn, Wurzelessen). `gut begründet`, wo sie die Lesart gut begründbar oder besonders klar nennt oder einen Forschungsbeleg dafür anführt. `möglich`, wo sie die Lesart als Möglichkeit, als Kandidaten oder ohne Gewichtung referiert. `offen`, wo die Quelle offenlässt oder nur eine Agentenlesung vorliegt. Deshalb tragen die Zeilen vom 17.11.2026 mit „ungeprüft" in `Quelle` hier `offen`, auch wenn ihre alte Einstufung `stark` lautet.
- **`status_woertliche_ebene`** folgt bei den neuen Zeilen KZWs Beschreibung, bei den alten der vorhandenen `Begründung` (Bildhäufung über das Lied: `durchgeführtes Bild`, Spiel oder Tausch als Handlung: `zugleich erzählte Handlung`, „eher Metapher": `punktuelle Metapher`). Sagt keins von beiden etwas, steht `offen`.
- **`sprachliches_verfahren`** ist eine kurze freie Benennung des Mittels. Bei den Hauptbeispielen A bis F folgt sie KZWs Abschnitt 6 (Zahlrelation, körperliches Angebot, Zahlenspiel und Tausch, durchgeführte Bildlichkeit, grammatischer Kippeffekt), sonst ist sie ein Vorschlag dieser Zusammenstellung.
- **`annotation_offen_entschieden`**: `entschieden` nur beim Ausgangsfall naschen (KZW, 10.11.2026), sonst `offen`.

## Felder in `kandidaten.tsv`

`xml:id`, `Sigle`, `Stelle` (aus `div`/`lg`/`l` im TEI), `Form`, `Kontext` (Vers ± 2 Verse, Treffer in `[[ ]]`, bei Prosa ± 12 Tokens), `Annotation heute` (`@lemmaRef` und `@ana`), `Lesart 1`, `Lesart 2`, `Begründung`, `Quelle`, `Einstufung`, `Entscheidung`, dann neu `sexuelle_bedeutung_evidenz`, `status_woertliche_ebene`, `sprachliches_verfahren`, `annotation_offen_entschieden`, `pos heute` (`@pos` des Tokens) und `Bereich` (woher die Zeile kommt).

Stelle, Form, Kontext, Annotation und pos sind aus dem TEI ausgelesen. Alle Lesarten sind Agentenlesungen und so markiert, auch wo sie KZWs Beschreibung zusammenfassen. In `Quelle` steht, was KZW nennt, mit Seite, wo sie eine nennt. Was in Klammern „nicht selbst gelesen" heißt, ist nur über KZWs Kommentar bekannt.

An den 26 alten Zeilen ist nur dreimal die Spalte `Quelle` ergänzt (NEIC c 51 zweimal, NEIR 22), sonst sind ihre zwölf Felder unverändert.

## Suchverfahren

Bis 17.11.2026:

1. **Genannte Stellen** direkt im TEI gesucht: Walthers „küssen" in `tei/WVV.tei.xml`, „wurzen" in `tei/NEIR.tei.xml` Lied 22, Wengling (`lemma_24841`) in `tei/NEIC.tei.xml` Lied 7, „vingerlin" (`lemma_7084`) in NEIR Lied 40 und NEIC Lied 91. Die Liednummern der Fußnote passen zu den `div type="song"`-Nummern in NEIR und NEIC (geprüft am Inhalt der Lieder).
2. **Konzeptkollision im Lexikon** als Spur: Lemmata in `authority-files/lexicon.xml`, die eine Bedeutung mit `concept_21112000` (Sexualleben/Erotik) oder dessen Unterkonzept `concept_21045000` (Geschlechtsmerkmale/Zeugung/Geburt) haben und daneben eine Bedeutung ohne beide. Ergebnis: **411 Lemmata**. Die Menge ist für eine Liste zu grob (an der Spitze stehen *tragen*, *liebe*, *minne* mit Tausenden Belegen) und wurde nur als Fundort benutzt.
3. **Tokens mit gesetzter Erotik-Bedeutung an solchen Lemmata**: **13.422 Tokens an 120 der 411 Lemmata** tragen eine Erotik-Bedeutung als `@ana`. 8.170 davon sind *liebe*. Gelesen wurden die Konkreta am Ende der Häufigkeitsliste (*klobe*, *vogel*, *kolbe*, *gümpel*, *vingerlîn* usw.), weil dort ein wörtlicher Gegenstand und eine sexuelle Bedeutung aufeinandertreffen.
4. **Lektüre bekannter Lieder und Mären** im Kontext: Walther (Under der linden, Nemt frouwe disen kranz, Rosen- und Blumenbrechen), Oswald Kl. 76 (Graserin) und Kl. 83 (Jetterin, Vogelfang), Neidhart, die Mären *Der Sperber* (`SPW`) und *Das Häslein* (`HSL`).

Schritt 2 und 3 liefen mit einem Hilfsskript außerhalb des Repositorys (lxml über `lexicon.xml`, Zeilenscan über `tei/*.tei.xml`). Nachprüfbar mit Bordmitteln sind etwa:

```
rg -c 'lemma_24841"' tei/NEIC.tei.xml                 # 12 Wengling-Tokens in NEIC
rg -c 'lemma_24841_sense_39939' tei/NEIC.tei.xml      # davon 1 auf der Spiel-Bedeutung
rg -o 'lemma_7084_sense_\d+' tei/NEIR.tei.xml tei/NEIC.tei.xml tei/NEI.tei.xml | sort | uniq -c
rg -n 'type="song" n="(25|101)"' tei/OVW.tei.xml
```

Am 27.11.2026:

5. **KZWs TEI-Anker** (12 Tokens zu den Hauptbeispielen A, B, C, E, F) einzeln im TEI aufgeschlagen. Alle 12 stehen dort mit der Form, die KZW nennt, und im Vers, den sie zitiert.
6. **Stellen ohne Anker** (Abschnitt 3 des Kommentars von 08:54, Aufsatz-Nachtrag, STANDARD) über den Wortlaut gesucht: Zeilentext aus `<w>` und `<pc>` je `<l>` oder `<p>`, regulärer Ausdruck, erst im genannten Werk, dann über alle 667 Dateien. Ob ein Werk im Korpus liegt, ist an `authority-files/works.xml` (Titel, Sigle) und an `tei/<Sigle>.tei.xml` geprüft. Die Suche nach den Keller-Versen und den Nüssen lief mit einem Control (`teigen pirn` musste NEIM 25 treffen und traf).
7. **Vergleichsstellen** für `vergleich.tsv` ebenso über den Wortlaut gesucht. Alle 28 dort genannten Stellen sind im TEI gefunden.

Die Hilfsskripte lagen in `.claude/tmp/` (gitignoriert) und sind nicht Teil des Repositorys.

## Ergebnis

`kandidaten.tsv`, 57 Zeilen, eine je Token.

| Bereich | Zeilen |
|---|--:|
| bestehend (17.11.2026) | 26 |
| Hauptbeispiele A, B, C, E, F (D liegt nicht im Korpus) | 12 (3+3+1+4+1) |
| weitere: Diss.-Sammlung Abschnitt 3 | 14 |
| weitere: Aufsatz-Nachtrag | 3 |
| weitere: STANDARD | 2 |
| Summe | 57 |

Die 26 alten Zeilen nach ihrer Einstufung: stark 9, mittel 13, schwach 4. Nach Text: OVW 6, WVV 6, NEIR 4, NEIC 5, NEI 1, SPW 2, HSL 2. Der Ausgangsfall `OVW_1025010230_4` steht als erste Zeile mit KZWs Entscheidung dabei.

Die 31 neuen Zeilen nach KZWs Bezeichnung:

| KZW | Stelle im TEI | Zeilen |
|---|---|---|
| A, Birnenquotient, NEIR 31,4 | NEIR Lied 31, Str. 4, V. 2 und 4 | `NEIR_3104020_2`, `NEIR_3104040_1`, `NEIR_3104040_2` |
| B, „miner teigen pirn", NEIM 25,5 | NEIM Lied 25, Str. 5, V. 1 und 10 | `NEIM_2505010_1`, `NEIM_2505100_6`, `NEIM_2505100_7` |
| C, zwei Haselnüsse gegen eine, NEIM 18,1,6 | NEIM Lied 18, Str. 1, V. 6 | `NEIM_1801060_1` |
| E, Wurzeln essen, WRW 2117–2168 | WRW V. 2141, 2146, 2151, 2165 | `WRW_2141000_4`, `WRW_2146000_1`, `WRW_2151000_5`, `WRW_2165000_3` |
| F, Rüben herausziehen, Kl. 48,1,1–2 | OVW Lied 48, Str. 1, V. 1 | `OVW_1048010010_11` |
| Neidhart c 1,2,9–10 | NEIC Lied 1, Str. 2, V. 9–10 | `NEIC_102090_4`, `NEIC_102100_3` |
| Neidhart c 79,1,7–10 und R 42,1,7–10 | NEIC Lied 79 und NEIR Lied 42, je Str. 1, V. 9 | `NEIC_7901090_5`, `NEIR_4201090_2` |
| Neidhart R 34,5,5–10 | NEIR Lied 34, Str. 5, V. 10 | `NEIR_3405100_4` |
| Neidhart c 118,7,8–11 | NEIC Lied 118, Str. 7, V. 9 | `NEIC_11807090_5` |
| Der Taler, ST 4,3,1–7 | ST Str. 20, V. 3, 4, 6 | `ST_403030_4`, `ST_403040_4`, `ST_403060_4`, `ST_403060_7` |
| Buhlschaft auf dem Baume, BAB 93–108 und 101–104 | BAB V. 93, 102, 104 | `BAB_930_4`, `BAB_1020_4`, `BAB_1040_5` |
| Parzival, PZ 79,27–80,2 | PZ 80,1 | `PZ_8001_5` |
| Mätzlis Kirschenessen, WRW 6125–6128 | WRW V. 6127 | `WRW_6127000_4` |
| Reinhart Fuchs, RF 195–198 | RF V. 198 | `RF_19800_3` |
| Der Welsche Gast, WGA 4275–4276 | WGA V. 4275 | `WGA_427500_2` |
| „Frauenessen" (STANDARD) | ABS Rezept 40, KBL4 Rezept 56 | `ABS_400010_3`, `KBL4_561142010_3` |

Verteilung der neuen Felder über alle 57 Zeilen: Evidenz gesichert 11, gut begründet 11, möglich 17, offen 18. Wörtliche Ebene: zugleich erzählte Handlung 17, durchgeführtes Bild 11, punktuelle Metapher 4, offen 25.

## Nicht im Korpus oder nicht lokalisiert

**Nicht im Korpus.** Für keinen dieser Texte gibt es in `authority-files/works.xml` einen Werkeintrag, und die Suche nach dem zitierten Wortlaut über alle 667 TEI-Dateien bleibt leer.

- **Hauptbeispiel D**, Keller Nr. 7, S. 72, V. 7–18 („ob er auch epfel mog essen"), und der Parallelfall Keller Nr. 24, S. 222, V. 4–6. Dass „Keller" Adelbert von Kellers *Fastnachtspiele aus dem fünfzehnten Jahrhundert* meint, ist aus Nr. 59 („Ein Spil von Junkfraun und Gesellen") geschlossen und nicht geprüft. Kein Werktitel in `works.xml` enthält „Fastnacht".
- **Keller Nr. 45**, S. 345 (Katzenstrigel), **Nr. 59**, S. 521, V. 1–6, **Nr. 9**, S. 93, V. 29–31 (Birnen unter dem Hemd, auch im Aufsatz S. 84, Anm. 18, und im STANDARD-Beitrag), **Nr. 29**, S. 241, V. 27–28 (*nachthunger*). Dazu Keller Nr. 7 mit den Glockenschwengeln aus Abschnitt 4.
- **Der Ritter mit den Nüssen**, V. 84–85 und 96. Kein Werktitel mit „Nüsse" oder „Ritter … Nuss". Die Suche nach „nüzze b…" trifft nur AXU 20421 („mit einer nüzze boesen"), nicht diese Stelle.
- **nachthunger** überhaupt: kein Token im Korpus (Suche `nacht ?hung`, 0 Treffer). *Des Teufels Netz*, V. 6971, hat keinen Werkeintrag (die Titel mit „Teufel" sind andere Mären).
- **Heidelberger Hs. Pal. 343, Lied 128 bei Kopp 1905, S. 140** (*taygen pirn*). Kein Werkeintrag mit „Pal. 343" oder „cpg 343", die Suche nach *taig*/*teig* vor *pirn*/*birn* trifft nur NEIM 25. KZW verlangt ohnehin, Korpuszugehörigkeit und Datierung vor einer Aufnahme zu prüfen.

**Nicht lokalisiert.**

- **Die halbe Birne (A)**: das Werk liegt im Korpus (`RHB`), KZW nennt aber keine Verse. Sie beschreibt es als Szenen- und Strukturbeispiel, für das Verse und Tokens erst ausgewählt werden müssten.
- **„Frauenessen" in der genannten Edition**: der STANDARD-Beitrag weist das Rezept bei Ehlert, *Münchner Kochbuchhandschriften* (1999), nach. Die Münchner Handschriften im Korpus (`MBS1`, `MBS2`, `MBS5`, `MBS7`) haben keinen Treffer. Aufgenommen sind die beiden Rezepte, die die Agentensuche gefunden hat (ABS und KBL4), mit diesem Vorbehalt.

**Kein Korpusbeleg, nur Bezugsrahmen:** Wandbehang „Apfelernte" (um 1480, Schloss Osthausen) mit seiner Bildschrift, „Spannenlanger Hansel, nudeldicke Dirn" und Rüben- und Ripfelreime aus späterer Überlieferung, Goethes Apfelbaum-Dialog im *Faust* und Popmusik (STANDARD). KZW schlägt sie ausdrücklich nicht als mittelalterliche Korpusbelege vor.

## Vergleichsmaterial

Getrennt von den Kandidaten, weil ein ausdrücklicher Vergleich oder ein Handwerksbild nicht dasselbe ist wie lexikalische Doppeldeutigkeit. Sie dienen der Abgrenzung von Vergleich, Metapher und Doppeldeutigkeit.

**`vergleich.tsv`**, 28 Zeilen mit Stelle nach KZW, Sigle, `xml:id` des ersten Tokens der Verszeile, Vers aus dem TEI, eigener Kurzfassung des Bildes und Quelle:

- **Fruchtbilder des Körpers** (KZW, Abschnitt 4): 13 Stellen aus ENG, PRT, TRO, HUG, MNB, RDL, RVBR, MSW, OVW (Kl. 46, 58, 66), WGM und WRW, dazu Oswald Kl. 45 (Brüste wie eine Fledermaus) als nicht kulinarischer Kontrastfall.
- **dræjen-Handwerksbilder** (Aufsatz-Nachtrag, Aufsatz S. 81–82): 14 Stellen aus HUG, JEW (4), AXU, TIT, JT (4), LGR, PZ und TRO. Nach KZW dürfen sie nicht allein wegen *dræjen* eine sexuelle Bedeutung bekommen. PRT 1569 und Oswald Kl. 58 tragen beides, Frucht und *gedrât*.

Bei einigen Stellen steht das gesuchte Wort nicht in der ersten Zeile von KZWs Versbereich. Der Anker ist dann die Zeile mit dem Bild (etwa MNB 3239, OVW Kl. 66,3,3).

**Bildmaterial, ohne TEI-Bezug** (Aufsatz-Nachtrag, Angaben des Aufsatzes, nicht unabhängig geprüft):

- Codex Granatensis: Pfirsichernte (C-67, fol. 83v), süße Äpfel (fol. 83r), Marillenernte (fol. 82v), Aufsatz S. 75–77, Abb. 1–3, Kastanienernte (fol. 87v), S. 86, Abb. 7. Die erotische Aussage liegt dort auf der Bildebene, der Begleittext handelt von Gesundheit.
- Zürcher Liebesgarten, S. 77–80, Abb. 5–6.
- Elsässischer Wandbehang „Apfelernte", S. 77–78, Abb. 4.
- Phallusbäume, S. 88–92: Rosenroman-Handschrift Paris, BnF, Ms. fr. 25526, fol. 106v und 160r, Massa Marittima, Burg Lichtenberg, Moos-Schulthaus, Minnekästchen im Franziskanermuseum Villingen-Schwenningen (Inv.-Nr. 11770).

## Beobachtungen am Bestand

Nur notiert, nichts geändert.

- **Das Lexikon kennt die zweite Bedeutung oft schon.** Eine Erotik-Bedeutung neben der wörtlichen haben *naschen*, *vingerlîn*, *wurz*, *hâke*, *vogel*, *gümpel*, *klobe*, *kolbe*, dazu aus den neuen Zeilen *bir* (`lemma_712_sense_94314`), *apfel* (`lemma_261_sense_94302`), *haselnuʒ* (`lemma_27117_sense_95002` und `_95003`) und *vruht* (`lemma_7273_sense_11788`, nur mit Geschlechtsmerkmale/Zeugung/Geburt). Keine haben *küssen* stM. (Kissen), *jëten*, *gras*, *brechen*, *rôse*, *spiegel*, *riutelstap*, *hase*, *ruobe*, *krieche*, *rîben*. Bei *wengling* (`lemma_24841`) tragen beide Bedeutungen das Erotik-Konzept `concept_21112000`, die zweite dazu Spielzeug: das Lexikon trennt dort nicht zwischen Spiel und Erotik.
- **Die Tokens stehen meist auf einer Seite.** Manche nur auf der wörtlichen (Walthers *küssen*, Oswalds *voglen*, alle *pirn*, *haselnussen*, *rüben* der neuen Zeilen), manche nur auf der erotischen (Neidhart c 51 *kloben* und *vogel*, c 117 *kolbe*, *leckerheit* in RF 198 und WGA 4275 auf `lemma_3667_sense_5787`), manche ohne `@ana` (Oswalds *häcklin*, *jät*, *gümpels*, NEIM 25 *teigen*, BAB *apfel* und *gabeln*, WRW *smakes*).
- **Überlieferungen sind verschieden annotiert.** Dieselbe Strophe vom hârîn vingerlîn trägt in NEIR die Erotik-Bedeutung (`sense_83232`, 2 Tokens), in NEIC und NEI die Schmuck-Bedeutung (`sense_11475`).
- **Lemmatisierung:** *voglen* in OVW Kl. 83 steht auf dem Substantiv *vogel*, *kloben* in derselben Strophe (`OVW_1083030080_2`) hat kein `@lemmaRef`. Die drei *wurtzen* im Ring (WRW 2141, 2146, 2151) haben kein `@lemmaRef`. *teigen* in NEIM 25,5,10 steht auf dem Substantiv *teic* (`lemma_6040`). Das Frauenessen ist in ABS ein Kompositum (`lemma_26812` *vrouwenezzen*), in KBL4 zwei Tokens (*vrouwe* und *ëʒʒen*).
- **Zählungen weichen ab, die Stellen stimmen.** Parzival 79,27–80,2 (KZW): die Birne steht in 80,1. Der Taler 4,3 (KZW): im TEI `lg n="20"`, fortlaufend gezählt, die `xml:id` kodiert 4/03. R 42,1,7–10 und c 79,1,7–10: die Rübe steht je in V. 9.
- **Parallele, nicht von KZW genannt:** die Wendung aus R 34,5,10 („witen garten tuet si rueben lære") steht auch in NEIC Lied 119, Str. 2, V. 10 (`NEIC_11902100_0`). Sie ist nicht als eigene Zeile aufgenommen.
- **Liednummer des Ausgangsfalls:** der Body von #702 nennt „Kl. 101", ebenso KZWs Paraphrase von Marold in #602 (10.11.2026). Im TEI steht `OVW_1025010230_4` in `div type="song" n="25"` (Incipit „ain burger und ain hofman"), Lied 101 beginnt mit „wach auff , mein hort". Dass die `div`-Nummer der Zählung nach Klein folgt, ist aus dem Titel der Quellenangabe in `tei/OVW.tei.xml` („Die Lieder Oswalds von Wolkenstein") geschlossen und nicht an der Edition geprüft.

## Offen für KZW

- Je Zeile die Spalte `Entscheidung`, und ob die vorgeschlagenen Werte der vier neuen Felder stimmen.
- Grundsätzlich: sollen Stellen wie Neidhart c 51 oder c 117, die heute nur die Erotik-Bedeutung tragen, die wörtliche dazubekommen? KZWs Kommentar vom 27.11.2026 sagt, die Stelle beim roten Vogel bleibe metaphorisch, entscheidet die Annotation aber ausdrücklich nicht.
- Tervooren, Koitusmetaphern-Beleg S. 274: Diss. 1995, Aufsatz Anm. 19 1993. Welche Ausgabe gilt?
- Ob Kellers Fastnachtspiele (Hauptbeispiel D und die Nummern 24, 45, 59, 9 und 29) ins Korpus kommen sollen. Das wäre ein Ingest mit eigener Prüfung von Zeitgrenze und Rechten, nicht Teil dieses Tickets.
