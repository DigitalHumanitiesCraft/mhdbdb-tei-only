# #216 Frau Minne als eigenes NAM-Lemma: Entscheidungsblatt (Phase 1, nichts angewendet)

Stand 2026-11-08, gemessen an `02eb7ebea` (origin/main). Das Skript
`scripts/ingest/pos-disambig/apply-216-minne-nam.py` läuft als Trockenlauf und
reproduziert die Menge; `--apply` schreibt, ist aber in diesem Stand nicht gelaufen.
Protokolle dieses Ordners: `protokoll.tsv` (322 Zeilen: 321 NAM plus 1 Verb, jeweils
Ist-Zustand und Soll-Zustand je Token), `zurueckgehalten.tsv` (3 frô, 2 Verb, 4 Lesefälle
mit ihrem heutigen Zustand).

Mit **VORSCHLAG** markierte Punkte sind im Skript eingesetzt und per Konstante oder Schalter
änderbar. Wer sie anders entscheidet, ändert eine Zeile und läuft den Trockenlauf neu.

## Grundlage und Menge

Entschieden: chsteiner 2026-08-31 in #216 (eigenes NAM-Lemma "Minne"; unmittelbar
vorangehendes Token mit `lemma_7260`, Wortform ohne -n; -n-Fälle bleiben bei
`lemma_4130`), KZW 2026-08-31 ("die Umsetzung liegt bei dir", MR2-Fall ist das Verb),
chsteiner 2026-11-08 (NAM-Paket jetzt; zurückhalten: 4 Lesefälle, GWTK, 3 frô-RVBR).
Koordination 2026-11-08: die zwei Verb-Tokens JT_42944000_1 und WGL_42150_6 bleiben bei
`lemma_4133`.

Trockenlauf, wörtlich (Auszug, Gesamtausgabe im Bericht):

    326 Kandidaten = 274 ohne @lemmaRef + 50 lemma_4130 + 2 anderes Lemma (JT_42944000_1, WGL_42150_6: lemma_4133)
    zurueckgehalten: 3 fro-RVBR (RVBR_4826_6, RVBR_6310_5, RVBR_8687_6), 0 GWTK, 2 Verb nicht umhaengen
    Ergebnis: 321 = 50 (heute lemma_4130 NOM) + 271 (ohne @lemmaRef, davon 9 mit pos=NAM ohne Lemma)

Das Skript bricht bei jeder Abweichung von diesen Zahlen ab (Assert auf alle elf Teilzahlen).
Der Wert 0 für GWTK ist gemessen, nicht vorausgesetzt: kein GWTK-Token erfüllt die Regel,
die Sperre ist trotzdem im Skript, falls ein späterer Stand eines hinzubringt. Die vier
Lesefälle haben alle einen Vorgänger auf -n und liegen deshalb außerhalb der Menge; das
Skript prüft das je Fall.

Schreibungen der 321: minne 168, mynn 123, mynne 26, minn 4. Großschreibung kommt in der
Menge nicht vor (der Assert bricht ab, falls doch).

## 1. Lexikon-Eintrag

**Bestand (gemessen mit lxml über `authority-files/lexicon.xml`, 43.711 Einträge):**
11.224 Einträge führen `NAM` (davon 11.107 nur `NAM`), 11.177 mit Konzept-`ptr` im Sense,
47 ohne. 11.113 dieser 11.224 schreiben die orth groß (99,0 %).

**Personifikationen:** Es gibt keine für Âventiure, Sælde, Êre oder Welt. Diese Wörter
stehen nur als `NOM` im Lexikon (`lemma_20` âventiure, `lemma_5051` sælde, `lemma_1282`
êre, `lemma_7494` werlt). Als Vorbild bleiben göttliche und allegorische Namen:

| Lemma | Zeile in lexicon.xml | Aufbau |
|-------|----------------------|--------|
| `lemma_15703` Fortuna | 85422 | NAM, 1 Sense, 9 Konzepte: Weiblich/Frau (21011000), Glückseligkeit/Unglück, Freude/Leid, Personennamen/Familiennamen (23112500), Lateinisch, Mythologie-Konzepte, Glück/Pech; etym auf `lemma_30983` |
| `lemma_6810` Venus | 670067 | NAM, 4 Senses (Göttin: 21011000, 23112500, 23123100, 24421000, 24431000; Planet; Latein) |
| `lemma_1042` Cupido | 7481 | NAM, 1 Sense, nur 24421000 (Nichtchristliche Mythologie/Namen); etym auf `cupere` |

Der engste Vorläufer ist im Bestand selbst: `lemma_4130_sense_83291` (Zeile 434507) trägt
das Konzept 23112500 (Personennamen/Familiennamen) und hat genau einen Beleg im Korpus,
`REN_249200_1` ("vrawe minne"). Der Sense steht seit dem ersten TEI-Stand (`git log -S`
über `lexicon.xml`: nur `378aadbbf`), stammt also aus der RDF-Migration und nicht aus
einem der späteren Batches; die Namenslesart ist damit schon einmal gesetzt worden.

**Orth-Schreibung, VORSCHLAG `Minne`.** Begründung: 99,0 % der NAM-Einträge sind groß
geschrieben, und der Schreibunterschied hält die beiden `minne` auseinander. Die
Normalisierung (`normalize_mhg`) macht aus beiden `minne`; das ist bei 215 von 11.043
großgeschriebenen NAM-Einträgen schon so (z. B. `lemma_14269` Lûne neben `lemma_16709`
lûne, ebenso Elbe, Warte). Alternative: `minne` klein, dann zwei Einträge mit
identischer orth, was nirgends vorkommt und die Anzeige nicht unterscheidet.

**ID:** Höchste heute `lemma_79829`, also `lemma_79830`; höchste Sense-Nummer 119200
(Fabeltiere, `apply-461-fabeltiere.py`), also `lemma_79830_sense_119201`. **Der Satz
"Anhängen am Dateiende" trifft nicht zu:** `lexicon.xml` ist nach dem ID-String sortiert,
nicht nach der Zahl. `lemma_79829` (briech, `2ccb54659`/#606) sitzt auf Zeile 737693
zwischen `lemma_79828` und `lemma_7983`, der letzte Eintrag der Datei ist `lemma_9999`.
Das Skript setzt `lemma_79830` deshalb zwischen `lemma_7983` (Zeile 737710) und
`lemma_7984` (737730); es ermittelt den Platz selbst und bricht ab, wenn der Anker nicht
genau einmal da ist.

**Eintrag (VORSCHLAG):**

    <entry xml:id="lemma_79830">
      <form type="lemma"><orth>Minne</orth></form>
      <gramGrp><pos>NAM</pos></gramGrp>
      <etym type="morphological"><seg type="component" corresp="lexicon.xml#lemma_4130">minne</seg></etym>
      <sense xml:id="lemma_79830_sense_119201" ana="#type_372866 #type_372867 #type_372868 #type_372869">
        <ptr target="concepts.xml#concept_21011000"/>   Weiblich/Frau
        <ptr target="concepts.xml#concept_22704010"/>   Liebe/Zuneigung/Abneigung/Gleichgültigkeit
        <ptr target="concepts.xml#concept_23112500"/>   Personennamen/Familiennamen
      </sense>
    </entry>

Die etym auf `lemma_4130` folgt `lemma_4133` minnen (Zeile 434636) und briech → brî
(`2ccb54659`). Das Sense-`ana` folgt der Regel, die sich messen lässt: bei Einträgen mit
genau einem Sense ist `sense/@ana` gleich der Typenmenge des Lemmas in `variants.xml`,
bei 10.529 von 10.601 NAM-Einträgen und 23.002 von 24.196 sonstigen. Die vier Typnummern
stehen unter Punkt 3. Alternative bei den Konzepten: zusätzlich 24421000 (Nichtchristliche
Mythologie/Namen) wie bei Fortuna, Venus und Cupido. Das wäre ein Urteil, dass Minne als
mythologische Gestalt zählt, und die Minne des Korpus ist überwiegend die höfische
Allegorie; es ist eine KZW-Frage, daher nicht eingesetzt.

## 2. @ana

Bestand der 50 heutigen `lemma_4130`-Tokens (gemessen): 20 tragen `@ana` auf
`lemma_4130_sense_6485` (Sexualleben/Erotik, Liebe, Etikette, Frauendienst), 1 auf
`lemma_4130_sense_83291` (`REN_249200_1`), 29 haben kein `@ana`. Alle 50 tragen `pos="NOM"`.

Ein `@ana` auf einen Sense von `lemma_4130` kann am neuen Lemma nicht stehen bleiben (der
Sense gehört dem Abstraktum). Zwei Wege:

- **VORSCHLAG (Schalter `--ana alle`, Vorgabe):** alle 321 Tokens bekommen `@ana` auf den
  einen Sense des neuen Lemmas. Begründung: bei einem Einzelsense-NAM-Lemma ist die
  Sense-Frage nicht offen, und die Konvention ist ausnahmslos: 179.550 von 179.550 Tokens
  mit `pos="NAM"` auf einem NAM-Lemma mit genau einem Sense tragen `@ana` (gemessen per
  Regex über `tei/`, Attributreihenfolge `lemmaRef`/`pos` in beiden Richtungen); bei
  Fortuna 31 von 31, Venus 378 von 378, Cupido 32 von 32. Folge für die Begriffshilfe:
  `sense_6485` verliert 20 Belege (1.010 auf 990), `sense_83291` verliert seinen einzigen
  (1 auf 0), der neue Sense hat 321.
- Alternative (`--ana keine`): kein `@ana` auf irgendeinem der 321, die 21 alten
  verfallen ersatzlos. Das entspricht der Zurückhaltung in #189, #198, #216 Serie 1, #369
  ("kuratorisch zurückgestellt"), die dort aber auf Mehrsense-Lemmata zielte.

`lemma_4130_sense_83291` bleibt im Lexikon stehen, danach ohne Beleg (VORSCHLAG; der Sense
ist ein KZW-Bestand, Löschen wäre eine eigene Entscheidung). Es gibt weitere Senses ohne
Beleg bei `lemma_4130` (6486 hat kein `@ana`).

## 3. @corresp und variants

**Wer vergibt die Typen?** Nicht `extract-variants.py`. Es liest nur `<w>` mit `@lemmaRef`
**und** `@corresp="variants.xml#type_N"` und leitet daraus Lemma, Typ, Form und `form/@n`
ab (Docstring Zeilen 13 bis 16, `collect_one` Zeile 87 ff.). Es prägt keine Nummern. Weist
ein Typ mehrere Lemmata auf, schlägt es ihn dem häufigeren zu (`resolve`, Zeilen 159 bis
197). Daraus folgt, was #367 (`4f61eb69f`, `ingest/pos-disambig/367-waeren/config.json`,
Kommentar `kommentar_corresp`) schon festgehalten hat und was KZW als Auflage nannte
(#367, 2026-08-25): **neue Nummern statt Mitwandern.** Behielten die 49 Tokens
`type_14385` ("minne", n=6.951 unter `lemma_4130`), gewänne `lemma_4130` sie zurück und
die Zuordnung zum neuen Lemma wäre unsichtbar.

Das Apply-Skript setzt deshalb `@corresp` selbst, je Schreibung ein **neuer** Typ über der
höchsten vergebenen Nummer (variants.xml und Korpus-`@corresp` stimmen überein: 372865,
`type_372865` "trüben", Zeile 126576; die Typen 372861 bis 372865 prägte zuletzt #554):

| Schreibung | Tokens | Typ |
|------------|-------:|-----|
| minne | 168 | `type_372866` |
| mynn | 123 | `type_372867` |
| mynne | 26 | `type_372868` |
| minn | 4 | `type_372869` |

Die Nummern vergibt das Skript beim Lauf neu aus dem dann höchsten Stand (absteigend nach
Häufigkeit); sie stehen hier nur als heutiger Stand. `extract-variants.py --apply` danach
erzeugt die vier `<form>`-Zeilen unter `lemma_79830` mit `n` = 168, 123, 26, 4, senkt
`type_14385` von 6.951 auf 6.902 und `type_78204` ("minn") von 47 auf 46, und schreibt die
`<date>`-Zeile neu. In `sense/@ana` des Lexikons entfernt es nur Typen, die aus
`variants.xml` verschwinden; es fügt keine hinzu, deshalb setzt das Skript das `ana` des
neuen Sense selbst (Punkt 1). Die 271 ohne Lemma tragen heute kein `@corresp`, sie
bekommen ebenfalls den Typ ihrer Schreibung. Das Verb-Token MR2_27022210102100_5 bekommt
den Bestandstyp `type_64100` ("mynne" unter `lemma_4133`, n=5, danach 6); das Skript
verlangt, dass es genau einen solchen gibt.

**Folge für das Ranking (Vorschrift B, ADR-021), vom Skript simuliert:** eine Form kippt.
`mynn`: vorher `lemma_3001` (ich, n=54) vor `lemma_4130` (5) und `lemma_4133` (3), nachher
`lemma_79830` (123) zuerst. Die anderen drei Formen behalten ihre erste Kandidatin,
`lemma_79830` steht dort hinten (minne 168 gegen 6.903, mynne 26 gegen 64, minn 4 gegen
178). Die Simulation ist eine Näherung (Gleichstände ohne Dokumentordnung); die verbindliche
Zahl liefert `check-variants-flips.py` nach dem Neubau.

## 4. @pos und @rend

`@pos="NAM"` auf allen 321; die 9 Tokens mit `pos="NAM"` ohne Lemma bekommen nur Lemma,
`@ana` und `@corresp` dazu. `@rend` ist am `<w>` nicht vorhanden: der Befund
`upper_case_first_letter` (109 der 326 Kandidaten) sitzt auf umgebenden `<hi>`-Elementen
und bleibt unangetastet, das Skript ändert keinen anderen Teil der Datei.

## 5. Positionszählung und Lifecycle

**Positionen:** gezählt werden nur `<w>` mit `@lemmaRef`. 271 + 1 (MR2) Tokens bekommen es
neu (gemessen: 272 in 55 Dateien), die 50 `lemma_4130`-Tokens haben es schon. In den 55
Dateien verschieben sich die Positionen aller folgenden Tokens; `@n`-Verszählung und
`?verse=`-Links bleiben unberührt (nur `@n` bindet sie).

**Zeile der Routing-Tabelle** (`docs/DATA-MODEL.md`, "Routing by type of change"): "`tei/`:
the stock of `<w>`, their wording, `@lemmaRef` or `@corresp` touched" und zugleich
"`authority-files/lexicon.xml`": also die Korpus-Checkliste **voll** (Schritt 8 inklusive)
und die Authority-Checkliste (Schritt 1 entfällt, 5 inklusive). In der Reihenfolge:

1. Skript mit `--apply` (tei/ plus lexicon.xml); `git diff --stat` gegen die Erwartung
   (55 Korpusdateien, 322 Tokens, je Datei +1 `<change>`).
2. Schema: `python scripts/audit/validate-corpus.py --sample <SIG>` für die 55 Sigle
   (oder `--fail-fast` über alles).
3. **Bump** beider Indexe. Heute Corpus 4.2.36 und Authority 1.9.33 (`corpus-loader.js`
   Zeile 8, `build-authority-index.py`); die offenen PRs #688 und #689 haben am
   2026-11-08 noch nichts darüber beansprucht (gemessen: beide Köpfe tragen 4.2.36 und
   1.9.33), brauchen aber vermutlich selbst einen Bump. Vor dem Bump `gh pr list` und
   `INDEX_VERSION` in den offenen Köpfen ansehen, dann die nächste freie Nummer
   (voraussichtlich 4.2.37 und 1.9.34), danach `check-index-versions.py`. Der Bump ist
   nötig: die Positionszählung ändert sich und das Lexikon bekommt einen Eintrag.
4. `build-corpus-index.py` (`--allow-dirty` lokal).
5. `extract-variants.py` zuerst ohne `--apply` (erwartet: added 4, form text changed 0,
   lemma assignment changed 0, token count n changed 3 (type_14385, type_78204,
   type_64100), removed 0; hergeleitet, nicht gelaufen), dann mit `--apply`.
5b. `build-lemma-pos.py` (neue `@lemmaRef` und `@pos`).
6. `build-authority-index.py`, 7. `build-api.py`, 8. `build-begriffshilfe.py` (liest
   `w/@ana` und `lexicon.xml`; die Zahlen von `sense_6485` und dem neuen Sense ändern sich).
9. `check-authority-cross-refs.py --check` (die Tokens mit `@lemmaRef` ohne `@corresp`
   in `corresp-coverage-baseline.json` steigen nicht: alle 322 bekommen ein `@corresp`).
10. `validate-indices.py` und `npm test` (VERDICT-Zeile). Im Frontend die Lemmasuche
    "minne" ansehen: zwei Lemmata mit gleicher normalisierter orth, die Anzeige des
    Zweiten und der Link in die Lemmaseite sind im Chrome zu prüfen (CLAUDE.md,
    Frontend-Regel).
11. **Flip-Gate:** `check-variants-flips.py --base origin/main` meldet nach der Simulation
    **1** umgeklappte Form (`mynn`). Es braucht die Quittung in
    `scripts/audit/variants-flips-ack.json` (mit `git add -f`):
    `{"from": "1.9.33", "to": "<neue Version>", "flips": 1, "reason": ...}`; die Begründung
    wie die der Quittung von #554: 123 Belege von `mynn` sind Frau Minne gegen 54 von
    lemma_3001, die Mehrheit der Belege der Schreibform wechselt, keine Typnummer wurde
    umgehängt. Die Zahl 1 ist erst nach dem echten Neubau verbindlich.
12. Commit (Korpus, Lexikon, Indexe, API, Begriffshilfe, Bumps, Quittung zusammen), Pull
    Request, `reviewer` vor dem Push.

Nicht geprüft in dieser Phase, weil `--apply` nicht lief: Schema-Validierung des neuen
Lexikoneintrags und der geänderten Korpusdateien, der Neubau der Indexe. Im Speicher
geprüft: alle 55 geänderten Dateien und das Lexikon sind wohlgeformt, und jedes der
322 Tokens trägt nach der Ersetzung genau die Sollattribute.

## 6. docs/POS-TAGSET.md

Neuer Abschnitt `## 8.` hinter §7 (nach Zeile 185) und vor "Cross-references" (Zeile
187). Wortlaut (VORSCHLAG, englisch):

    ## 8. Personified Minne as `NAM` (#216)

    *minne* directly preceded by a token of `lemma_7260` (*vrouwe*, any spelling) whose
    own form does not end in -n is the allegorical figure Frau Minne. It is tagged `NAM`
    under the proper-name lemma `lemma_79830` (*Minne*), with its own sense and its own
    variant types (KZW and chsteiner, 2026-08-31, applied 2026-11). "Directly preceding"
    is the next `<w>` in document order, across `<pc>`, `<lb>` and `<hi>`. Where the
    preceding form ends in -n (*vrouwen minne*), the token stays with the abstract noun
    `lemma_4130` as `NOM`.

    The rule is deliberately formal. Cases a reader would have to decide (the reading
    cases WGA_118600_5, RLS_140304_1, FR1_3026030_4 and FR1_3001060_7, the GWTK cases,
    the three RVBR cases after *frô*) are not covered and stay as annotated. The other
    personified abstractions (*âventiure*, *sælde*, *êre*, *werlt*) remain `NOM`; no
    `NAM` lemma exists for them.

Der Abschnitt wird erst mit `--apply` und seinem Commit eingetragen, nicht in dieser
Phase. Zusätzlich ein Halbsatz in §1 bei der Zeile NAM ("Frau Minne, see §8") ist
möglich, aber nicht nötig.

## 7. revisionDesc-change

Je geänderter Datei ein Eintrag, Muster `apply-461-fabeltiere.py` (Anker: letztes
`<change>` vor `</revisionDesc>`, mit dessen Einrückung; Zeilenende der Datei erhalten;
Ist-Zustand je Token vorher verifiziert, nicht idempotent). Beispielwortlaut für eine
Datei mit 3 neuen und 2 umgehängten Tokens:

    <change when="2026-11-08" who="#editor">#216 Frau Minne: 5 Tokens auf das Namenlemma
    lexicon.xml#lemma_79830 (Minne, NAM) gesetzt (3 neu annotiert, 2 von lemma_4130
    umgehängt). Regel: unmittelbar vorangehendes Token mit lemma_7260, Form ohne -n
    (Entscheidung chsteiner und K. Zeppezauer-Wachauer 2026-08-31, Umsetzung 2026-11-08;
    Provenienz-Log: ingest/pos-disambig/216-minne-nam/).</change>

In MR2 kommt der Verbsatz dazu. Das Datum `2026-11-08` ist die Konstante `DATUM` im
Skript und wird beim Anwenden nachgezogen.

## Für die Entscheidung offen

1. `--ana alle` (Vorschlag) oder `keine`.
2. Konzepte des Sense (drei vorgeschlagen), ob 24421000 dazukommt.
3. orth `Minne` (Vorschlag) oder `minne`.
4. Quittung für den Umschlag von `mynn` (ich → Minne).
5. `lemma_4130_sense_83291` stehen lassen (Vorschlag) oder löschen.
6. Bumpnummern erst unmittelbar vor dem Bump festlegen.
