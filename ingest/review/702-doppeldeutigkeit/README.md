# Kandidatenliste #702: absichtliche Doppeldeutigkeit

Subauftrag aus #602 auf Wunsch von @wachauer (10.11.2026): Beispiele aus dem Korpus sammeln, an denen eine Stelle absichtlich zwei Bedeutungen trägt, wie `naschen` bei Oswald von Wolkenstein. Mögliche Nachnutzung laut KZW: Aufsatz, Forschungsantrag, Feature.

**Am Korpus und am Lexikon ändert diese Liste nichts.** Ob ein Beleg zwei Bedeutungen bekommt, entscheidet KZW je Fall in der Spalte `Entscheidung` von `kandidaten.tsv`. Zusammengestellt am 17.11.2026 auf `main` `96e3c8245`.

## Material

| Quelle | Stand |
|---|---|
| KZWs Antwort zu `naschen` in #602 (10.11.2026) mit Hofmeister 2011 und Marold 1995 | gelesen im Issue. Hofmeister und Marold selbst nicht gelesen |
| Aufsatz Borek, Zeppezauer-Wachauer, Ketschik: „Eindeutig Uneindeutig. Zur Modellierung von Unschärfe in der Mediävistik", Blog *Mittelalter*, 16.02.2022, https://doi.org/10.58079/rha5 | **nur in Fragmenten gelesen.** Die Seite (mittelalter.hypotheses.org/27658) sperrt automatische Abrufe (Anubis). Über WebFetch kamen Zusammenfassung und kurze Zitate, der Wortlaut ist nicht am HTML geprüft |
| Auszug aus KZWs Dissertation, zwei Screenshots in #602 (Fußnote 202) | gelesen, die Bilder waren ohne Login abrufbar |
| Die in Fn. 202 zitierte Literatur (Hofmeister 2005b, Müller 1986, Wackernagel, Fischer) | nicht gelesen |
| Kommentare und Forschung zu Walther, Oswald Kl. 76 und 83, Sperber, Häslein | nicht gelesen, in der Tabelle als „ungeprüft" geführt |

Was der Aufsatz zum Thema sagt (Fragmente): mittelalterliche Dichter bedienten sich „häufig absichtlicher Ambiguitäten", es gebe Daten, die „gar nicht aufgelöst bzw. disambiguiert werden sollen, da ihre Unschärfe die poetologische Absicht des Textes ist", genannt werden Oswald von Wolkenstein, Neidhart und „Walther von der Vogelweide mit seinem *roten küssen*". Als Beispiel für Mehrdeutigkeit im Lexikon steht dort mhd. *trache* („Reptilien" und „Fantastische Tiere"). Das ist eine Eigenschaft des Lexikoneintrags, keine Stelle, und steht deshalb nicht in der Liste.

Die Diss. (Fn. 202) nennt drei Neidhart-Fälle, alle drei sind in der Liste: Minne und „Drogen" in SL 15 = SNE I: R 22 (Hofmeister 2005b: „Die kunstvolle Vagheit seines Texts erlaubte es seinem Publikum, das Gehörte gemäß eigenem Deutungsvermögen zu ‚komplettieren'"), das Wengling-Lied (c 7, f 12) und das Lied vom *hârein vingerlein* (R 40 / d 7 / c 91). Zu Letzterem schreibt sie, es sei „auch nicht gerade das, was man als ‚unscharf' bezeichnen würde", und benennt die Schwierigkeit „klar abzugrenzen, wann es sich um eine Metapher und wann um eine absichtliche Doppeldeutigkeit handelt".

## Kriterien

Abgeleitet aus dem Ausgangsfall, dem Aufsatz und der Fußnote. Es sind Arbeitskriterien der Zusammenstellung, keine Entscheidung.

1. **Zwei Lesarten tragen den Vers je für sich.** Die wörtliche Oberfläche bleibt kohärent (Geld verteilen, Gras mähen, Vögel fangen, ein Spiel spielen), die zweite Lesart ebenso. Schließt der Kontext eine Lesart aus, ist es Homographie oder Polysemie und gehört nicht hierher.
2. **Ein Signal im Text zeigt die Absicht.** Am stärksten wirkt eine Häufung gleichgerichteter Bilder im selben Lied (Graserin: Sichel, Hacke, Gras, jäten in der „nidern peunt". Vogelfang: Kloben, Gimpel, „voglen"). Daneben Gattung und Rolle (Rollenlied, Pastourelle, Schwankmär), eine Pointe, eine Figur, die das Wort missversteht (Sperber, Häslein).
3. **Der Text löst nicht auf.** Er lässt das Publikum „komplettieren" (Hofmeister nach Fn. 202). Wo die zweite Bedeutung allein übrig bleibt und die erste nur Verhüllung ist, liegt eher eine Metapher vor (hârîn vingerlîn).
4. **Ein Forschungs- oder Kommentarbeleg hebt die Einstufung**, ist aber nicht Bedingung.

Einstufung: **stark** heißt Kriterium 1 und 2, dazu ein Forschungsbeleg oder eine dichte Bildhäufung. **mittel** heißt Kriterium 1 und ein schwächeres Signal, oder ein Abgrenzungsfall zur Metapher. **schwach** heißt, nur ein Topos (Rosen oder Blumen brechen) trägt die zweite Lesart.

## Suchverfahren

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

## Ergebnis

`kandidaten.tsv`, 26 Zeilen, eine je Token. Spalten: `xml:id`, `Sigle`, `Stelle` (aus `div`/`lg`/`l` im TEI), `Form`, `Kontext` (Vers ± 2 Verse, Treffer in `[[ ]]`), `Annotation heute` (`@lemmaRef` und `@ana`), `Lesart 1`, `Lesart 2`, `Begründung`, `Quelle`, `Einstufung`, `Entscheidung`. Kontext, Stelle und Annotation sind aus dem TEI ausgelesen, alle Lesarten sind Agentenlesungen und so markiert.

| Einstufung | Zeilen |
|---|--:|
| stark | 9 |
| mittel | 13 |
| schwach | 4 |
| Summe | 26 |

Nach Text: OVW 6, WVV 6, NEIR 4, NEIC 5, NEI 1, SPW 2, HSL 2. Der Ausgangsfall `OVW_1025010230_4` steht als erste Zeile mit KZWs Entscheidung dabei.

## Beobachtungen am Bestand

- **Das Lexikon kennt die zweite Bedeutung oft schon.** Eine Erotik-Bedeutung neben der wörtlichen haben *naschen*, *vingerlîn*, *wurz*, *hâke*, *vogel*, *gümpel*, *klobe*, *kolbe*. Keine haben *küssen* stM. (Kissen), *jëten*, *gras*, *brechen*, *rôse*, *spiegel*, *riutelstap*, *hase*. Bei *wengling* (`lemma_24841`) tragen beide Bedeutungen das Erotik-Konzept `concept_21112000`, die zweite dazu Spielzeug: das Lexikon trennt dort nicht zwischen Spiel und Erotik.
- **Die Tokens stehen meist auf einer Seite.** Manche nur auf der wörtlichen (Walthers *küssen*, Oswalds *voglen*), manche nur auf der erotischen (Neidhart c 51 *kloben* und *vogel*, c 117 *kolbe*), manche ohne `@ana` (Oswalds *häcklin*, *jät*, *gümpels*).
- **Überlieferungen sind verschieden annotiert.** Dieselbe Strophe vom hârîn vingerlîn trägt in NEIR die Erotik-Bedeutung (`sense_83232`, 2 Tokens), in NEIC und NEI die Schmuck-Bedeutung (`sense_11475`).
- **Lemmatisierung, nur notiert:** *voglen* in OVW Kl. 83 steht auf dem Substantiv *vogel*, *kloben* in derselben Strophe (`OVW_1083030080_2`) hat kein `@lemmaRef`.
- **Liednummer des Ausgangsfalls:** der Body von #702 nennt „Kl. 101", ebenso KZWs Paraphrase von Marold in #602 (10.11.2026). Im TEI steht `OVW_1025010230_4` in `div type="song" n="25"` (Incipit „ain burger und ain hofman"), Lied 101 beginnt mit „wach auff , mein hort". Dass die `div`-Nummer der Zählung nach Klein folgt, ist aus dem Titel der Quellenangabe in `tei/OVW.tei.xml` („Die Lieder Oswalds von Wolkenstein") geschlossen und nicht an der Edition geprüft.

## Offen für KZW

- Je Zeile die Spalte `Entscheidung`.
- Grundsätzlich: sollen Stellen wie Neidhart c 51 oder c 117, die heute nur die Erotik-Bedeutung tragen, die wörtliche dazubekommen, oder gilt dort die Metapher als aufgelöst?
