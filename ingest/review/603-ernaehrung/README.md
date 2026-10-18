# #603: Ernährung von Menschen oder von Tieren (concept_21111000)

Prüfliste zu [#603](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/603), Stand 16.10.2026, ergänzt am 18.10.2026 um die zweite Lesung (Abschnitt unten). **Prüfmaterial, keine Entscheidung.** Nichts davon steht in `authority-files/` oder `tei/`, und welches Konzept für die Ernährung von Tieren gilt, entscheidet KZW.

## Die Frage

KZW am 15.10.2026 zu den Fällen abebîʒen (A-432) und lëcken (A-1146) aus #554: Alle Belege, die „Objektbezogene Aktivität/Tätigkeit · Ernährung von Menschen“ bezeichnen, sind zu prüfen, ob wirklich immer Menschen gemeint sind oder auch Tiere. Im Kommentar vom 15.10.2026 in #603 fügt sie an: „dann sollten wir wirklich alle Belege, die mit menschlicher Ernährung annotiert sind, systematisch prüfen. Erst Claude alle, die er automatisiert schafft - dann der Rest als EIL-Prüfung.“ Die Dateien hier sind der automatisierte Teil.

## Was die Dateien sind und was nicht

**Die Klasse `tier` ist eine Prüfliste, keine Feststellung.** Sie sagt: im Umkreis des Belegs steht ein Wort, das nach Konzept oder Lemma ein Tier nennt. Sie sagt nicht, dass das Tier die Nahrung aufnimmt. In Stichprobe 1 trifft die Klasse bei 4 von 10 Belegen (siehe unten). Die Klassen `mensch` und `unklar` sind ebenso Vorsortierung und kein Urteil.

| Datei | Inhalt | Zeilen |
|---|---|--:|
| `senses-21111000.tsv` | jede Bedeutung mit `concept_21111000` (Lexikon, `ptr`), mit der Zahl ihrer Belege je Klasse | 485 |
| `belege-tier.tsv` | alle Belege der Klasse `tier`, mit und ohne `@ana` | 2.867 |
| `lemmata-ohne-ana.tsv` | je Lemma dieser Bedeutungen die Belege ohne `@ana`, nach Klasse | 471 |
| `faelle-abebizen-lecken.tsv` | alle Belege der beiden Lemmata, maschinelle Klasse und Agentenurteil (Spalte `urteil_agent`) | 39 |
| `agent-faelle.tsv` | **Eingabe:** die Urteile eines Agenten zu diesen 39 Belegen (`w_id`, `urteil`, `begruendung`), von einem Agenten gelesen, nicht von KZW | 39 |
| `konzepte-tier.tsv` | 28 Konzepte, davon 10 aus der Tierkonzeptliste (`in_tierwortliste` = ja) und 18 Nachbarkonzepte, mit Zahl der Bedeutungen im Lexikon und davon zusammen mit 21111000 | 28 |
| `stichprobe.tsv` | Stichprobe 1: je Klasse 10 Belege, Seed 603 | 30 |
| `stichprobe2-tier-ohne-mensch.tsv` | Stichprobe 2: 10 Belege der Klasse `tier` ohne Mensch-Treffer, Seed 604 | 10 |
| `stichprobe-urteile.tsv` | **Eingabe:** die Urteile zu beiden Stichproben (40 Zeilen), von einem Agenten gelesen | 40 |
| `zusammenfassung.txt` | Zählung des Laufs, Quelle der Zahlen unten | |
| `zweite-lesung.tsv` | **Zweite Lesung (18.10.2026):** das Urteil eines Agenten zu jedem der 13.135 gelesenen Belege (`wer`, `tierklasse`, `art`, `begruendung`), mit der Klasse der Vorsortierung daneben und der Spalte `pruefen` | 13.135 |
| `senses-lesung.tsv` | je Bedeutung mit `concept_21111000` die Lesung ihrer Belege | 485 |
| `lemmata-lesung.tsv` | je Lemma die Lesung seiner Belege (`keine_nahrung` ist das Lemma-Rauschen der Vorsortierung) | 391 |
| `pruefen-603.tsv` | Belege, die die Stichproben als diskutabel oder falsch ausgewiesen haben | 5 |
| `konzeptfrage.txt` | Zählung zu KZWs Konzeptfrage, Quelle der Zahlen im Abschnitt „Die Konzeptfrage“ | |

Nicht im Repo, weil regenerierbar: `alle-belege-vorsortiert.tsv` (7,5 MB, alle vorsortierten Belege; `stichprobe2-603.py` liest sie).

## Die Grundmengen

Stand des Lexikons und des Korpus bei dem Lauf (`zusammenfassung.txt`): 667 Dateien, 9.431.295 `<w>`; 62.198 Bedeutungen im Lexikon, davon 485 mit `concept_21111000` (alle verschieden), auf 471 Lemmata.

- **Belege mit `@ana` auf eine dieser Bedeutungen** (je `<w>` einmal gezählt): **11.491**. Davon Klasse `tier` 1.223, `mensch` 7.745, `unklar` 2.523 (1.223 + 7.745 + 2.523 = 11.491). 361 der 485 Bedeutungen haben mindestens einen solchen Beleg, 124 keinen.
- **Belege ohne `@ana` bei einem der 471 Lemmata**: **21.667**, davon `tier` 1.644, `mensch` 15.649, `unklar` 4.374. Sie sind nicht einer Bedeutung zugeordnet, die Klasse beruht allein auf dem Lemma. Das ist die größere Menge, und sie ist unsicherer.
- `belege-tier.tsv` führt beide `tier`-Mengen zusammen: 2.867 = 1.223 mit `@ana` + 1.644 ohne.

## Die Regeln der Vorsortierung

Für jeden Beleg werden die `<w>`-Elemente im Fenster von acht links und acht rechts angesehen (der Beleg selbst nicht; Satzzeichen `<pc>` zählen nicht mit).

| Regel | Treffer, wenn ein Wort im Fenster ... |
|---|---|
| T1 | per `@ana` eine Bedeutung mit einem der 28 Tierkonzepte trägt und diese Bedeutung kein Lebensmittelkonzept (Teilbaum 21111300, 9 Konzepte) hat |
| T2 | kein `@ana` hat und sein Lemma irgendeine Bedeutung mit Tierkonzept und keine mit Lebensmittelkonzept hat |
| M1 | eines der Pronomen ich, wir, ir mit `@pos` PRO ist |
| M2 | per `@ana` eine Bedeutung mit einem Menschkonzept trägt (13 Konzepte: Teilbäume 21010000, 21103000, 23112000, 23112500) |
| M3 | kein `@ana` hat und sein Lemma irgendeine Bedeutung mit Menschkonzept hat |

Trägt die Bedeutung eines Fensterworts ein Tier- und ein Lebensmittelkonzept, zählt das Wort nicht (Fleisch, Speisen). **Klasse:** `tier`, wenn mindestens ein T-Treffer; sonst `mensch`, wenn mindestens ein M-Treffer; sonst `unklar`. Ein Mensch-Treffer hebt einen Tier-Treffer also nicht auf: von den 1.223 `tier`-Belegen mit `@ana` haben 943 auch einen Mensch-Treffer und 280 keinen (Spalte `tier_und_mensch_treffer`).

Gezählt an den 11.491 Belegen mit `@ana` (ein Beleg kann mehrere Regeln auslösen): M1 2.875, M2 5.863, M3 2.962, T1 926, T2 347.

**`dû` ist kein Auslöser von M1.** Im Lexikon ist `lemma_1241` du eine Präposition (PRP); das Pronomen ist `lemma_1242` dû, und es steht nicht in der Liste. Die Stichproben beruhen auf diesem Stand, deshalb ist die Liste nicht geändert worden. Eine Probe mit `dû` in der Liste (Mutationsprobe des Reviewers am 16.10.2026, nicht eingecheckt, am selben Tag nachgemessen) ergab, jeweils an denselben 11.491 Belegen mit `@ana`, M1 3.143 statt 2.875, `mensch` 7.853 statt 7.745 und `unklar` 2.415 statt 2.523; `tier` blieb bei 1.223, die `tier`-Belege mit Mensch-Treffer stiegen von 943 auf 953.

Die Tierkonzepte sind eine feste Liste von 28 Konzepten (Säugetiere, Vögel, Fische, Reptilien und weitere, mit den zugehörigen Namenskonzepten; Körper, Organe, Stoffwechsel, Verarbeitung, Krankheiten und Zucht sind ausgeschlossen). Die Liste steht in `zusammenfassung.txt` und in `scripts/review/vorsortieren-603.py`. `konzepte-tier.tsv` ist eine andere Liste von ebenfalls 28 Konzepten: 10 davon stehen auf der Tierkonzeptliste (`in_tierwortliste` = ja), 18 sind Nachbarkonzepte (etwa Stoffwechsel von Säugetieren), die nicht auf ihr stehen.

## Der Fall abebîʒen und lëcken

`faelle-abebizen-lecken.tsv`: 39 Belege (lëcken 36, abebîʒen 3). Maschinell: `mensch` 22, `tier` 13, `unklar` 4. Agentenurteil (`agent-faelle.tsv`): `mensch` 17, `tier` 16, `unklar` 6. Die Agentenurteile weichen also vom Maschinenurteil ab; sie sind die Grundlage für die Frage nach einer Bedeutung „Ernährung von Tieren“, nicht deren Beschluss.

## Ergebnisse der Stichproben

**n = 10 je Klasse und Stichprobe, von einem Agenten gelesen, nicht von KZW.** Zehn Belege tragen keine Aussage über die Häufigkeit in den Mengen oben, nur über die Art der Fehler. `treffer` in `stichprobe-urteile.tsv` heißt: die maschinelle Klasse stimmt mit dem Lesen überein.

| Stichprobe | Menge, aus der gezogen wurde | n | stimmt | stimmt nicht | unsicher |
|---|---|--:|--:|--:|--:|
| 1, Klasse `tier` | 1.223 Belege mit `@ana` | 10 | 4 | 5 | 1 |
| 1, Klasse `mensch` | 7.745 | 10 | 10 | 0 | 0 |
| 1, Klasse `unklar` | 2.523 | 10 | nicht bewertet | | |
| 2, `tier` ohne Mensch-Treffer | 280 | 10 | 5 | 3 | 2 |

Bei `unklar` ist keine Trefferangabe vergeben; der Agent las alle zehn als Nahrung von Menschen oder als andere Bedeutung (9 `mensch`, 1 `mensch/andere Bedeutung`). In Stichprobe 1 lasen alle 5 falschen `tier`-Belege als Nahrung von Menschen: das Tierwort ist Objekt der Handlung oder steht nur im Umkreis. Ohne Mensch-Treffer (Stichprobe 2) trifft die Klasse in 5 von 10 Fällen; bei n = 10 lässt sich ein Unterschied zu den 4 von 10 aus Stichprobe 1 nicht belegen.

## Zweite Lesung (18.10.2026)

KZW am 16.10.2026: Die Regeln der Vorsortierung ("im Umkreis steht ein Wort, das ein Tier nennt") greifen nicht immer inhaltlich, ein Rezept mit Rind und ezzen meint nicht, dass das Rind frisst. Sie bat um einen zweiten Lauf, der die Stellen sprachlich liest. Das ist er. **Alle Urteile in diesem Abschnitt sind Lesungen von Agenten (Claude Sonnet 5.5) und nicht von KZW oder uns geprüft**; die Stichproben unten sind die einzige Gegenprobe.

**Was gelesen wurde: 13.135 Belege** = die 2.867 `tier`-Belege der Vorsortierung (1.223 mit `@ana`, 1.644 ohne) + 2.523 `unklar` + 7.745 `mensch` (die beiden letzten Mengen mit `@ana`; 1.223 + 2.523 + 7.745 = 11.491 Belege mit `@ana`, dazu 1.644 ohne = 13.135). **Nicht gelesen:** die 20.023 Belege ohne `@ana`, die nicht `tier` sind (21.667 − 1.644). Sie tragen die Annotation "Ernährung von Menschen" nicht, sondern gehören nur zum Lemma.

**Wie:** Jeder Beleg mit 30 Token Kontext (Wörter und Satzzeichen) links und rechts aus dem TEI (`scripts/review/stapel-603.py`), in Stapeln zu 80, ohne die Klasse der Vorsortierung (damit das Urteil nicht an ihr hängt). 42 Sonnet-Agenten in fünf Workflows, dazu ein Pilot mit 60 Belegen (nur zur Schemaprobe, die Belege sind im `tier`-Lauf nochmals gelesen). Schema je Beleg: `wer` (`mensch`, `tier`, `unklar` oder `keine_nahrung`: die Stelle meint gar keine Nahrungsaufnahme), `tierklasse` (nur bei `tier`: `saeugetier`, `vogel`, `fisch`, `andere`, `unbestimmt`), `art` (`nahrungsaufnahme`, `fuettern`, `rezept`, `uebertragen`, `sonstiges`) und ein Satz Begründung. Verbunden und geprüft mit `scripts/review/verbinden-lesung-603.py`, ausgewertet mit `scripts/review/auswerten-lesung-603.py`. Die Neuvorsortierung am 18.10.2026 ergab dieselben Klassenzahlen wie am 16.10.2026; nur die Zahl der Bedeutungen im Lexikon ist von 62.198 auf 62.200 gestiegen (zwei neue seit dem 16.10.), das ändert keine Zahl in dieser Liste.

### Abgleich mit der Vorsortierung

| Klasse der Vorsortierung | Belege | Lesung `tier` | `mensch` | `keine_nahrung` | `unklar` |
|---|--:|--:|--:|--:|--:|
| `tier` | 2.867 | 620 | 579 | 1.607 | 61 |
| `unklar` | 2.523 | 69 | 1.829 | 588 | 37 |
| `mensch` | 7.745 | 266 | 5.629 | 1.713 | 137 |
| zusammen | 13.135 | 955 | 8.037 | 3.908 | 235 |

Bestätigt (Klasse = Lesung): `tier` 620 von 2.867 (21,6 %), `mensch` 5.629 von 7.745 (72,7 %), `unklar` 37 von 2.523 (1,5 %). Gekippt: von den `tier`-Belegen liest der Agent 579 als Mensch und 1.607 gar nicht als Nahrung; von den `mensch`-Belegen 266 als Tier. Je Regel, an den 11.491 Belegen mit `@ana`: Von den 926 Belegen, die T1 auslösen, liest der Agent 359 als Tier (38,8 %), von den 347 mit T2 111 (32,0 %). Für M1 bis M3 ist die Aufschlüsselung nicht belastbar, weil `alle-belege-vorsortiert.tsv` je Beleg nur die ersten vier Treffer führt (M1 2.854 statt 2.875).

**`keine_nahrung` ist Lemma-Rauschen der Vorsortierung und keine Aussage über die Belege.** 3.908 von 13.135 (29,8 %) sind Homographen und Übertragenes, die das Lexikon dem Konzept zuordnet: `munt` 626 von 660, `vaste` 316 von 322, `nieʒen` 211 von 234, `vol` 177 von 193, `twingen` 149 von 163, `salse` 98 von 103 (zusammen mit dem übrigen Rauschen 12 Lemmata mit mindestens 90 % bei mindestens 20 gelesenen Belegen). Je Lemma in `lemmata-lesung.tsv`. Für die Frage "Mensch oder Tier" ist das ohne Belang; ob diese Zuordnungen im Lexikon selbst stimmen, beantwortet die Lesung nicht.

### Stichproben am Text

Ich habe je Agent drei Belege selbst am Text gelesen (zwei mit einem Urteil außer `keine_nahrung`, eines mit `keine_nahrung`); die Auswahl ist nicht zufällig über die ganze Menge.

| Lauf | gelesen | stimmt | diskutabel oder falsch |
|---|--:|--:|--:|
| `tier` (9 Agenten) | 27 | 26 | 1 (`WZB_166ra_19_1`, Opferspeise) |
| `unklar` (8 Agenten) | 24 | 23 | 1 falsch (`GAU_36101360_4`, "frazze": Völlerei, gelesen als `keine_nahrung`) |
| `mensch` (25 Agenten) | 75 | 72 | 3 (`ADP_5308600_6`, `BVSN_8110_0`: geistliches Mahl; `PL1_103931_12`: "wilpret") |
| zusammen | 126 | 121 | 5 |

Diese fünf stehen in `pruefen-603.tsv` und gehen an KZW; die Urteile in `zweite-lesung.tsv` bleiben, wie der Agent sie gesetzt hat. 5 von 126 sagen nichts über die Fehlerquote in den 13.135, nur über die Art der Fehler: die Grenzfälle sind geistliche Speise und Opfer, der falsche Fall ein übertragener Gebrauch von "fraz".

**Ein Formfehler der Agenten:** In 17 von 13.135 Zeilen (0,13 %) hat ein Agent die `w_id` falsch abgeschrieben: 2 von 2.867 im `tier`-Lauf und 15 von 7.745 im `mensch`-Lauf, im `unklar`-Lauf keine gefunden. 4 davon haben Hilfsskripte der Agenten vor dem Verbinden in den Urteildateien geflickt (`tier`: `DIO_3224_3` → `DIO_3224_2`, `FR1_5076180_1` → `FR1_5064180_1`; `mensch`: `NAR_1606100_2` → `NAR_1606100_0`, `NEI_202150_2` → `NEI_202170_2`), die übrigen 13 meldet `verbinden-lesung-603.py`. Das Urteil gehört trotzdem zur Zeile mit dieser `nr`: an den 13 am Text geprüft, die 4 geflickten sind nicht einzeln am Text geprüft. Verbunden wird deshalb über `nr`; die 13 gemeldeten Korrekturen (Agent → richtig): `ADP_5322800_9` → `ADP_5322800_12`, `ADP_5642400_2` → `ADP_5642400_0`, `CRO_214200_4` → `CRO_214200_1`, `FDS_1150003_4` → `FDS_1150003_5`, `JT_54324000_4` → `JT_54324000_12`, `JT_60984000_3` → `JT_60984000_5`, `PL3_373612_5` → `PL3_373612_4`, `TAN_114760_3` → `TAN_114760_1`, `TAN_114760_5` → `TAN_114760_3`, `WRB_36420000_3` → `WRB_36420000_1`, `WRW_3117000_3` → `WRW_3117000_2`, `WZB_28rb_15_0` → `WZB_28rb_30_1`, `WZB_184va_22_4` → `WZB_184va_21_4`.

### Die Konzeptfrage

KZW am 16.10.2026: "Stoffwechsel von Säugetieren" umbenennen (z. B. in "Stoffwechsel und Ernährung von Säugetieren") oder eine Kategorie "Ernährung von Säugetieren" anlegen (ihr lieber), "vorerst nur bei solchen, wo es das Korpus hergibt". Quelle aller Zahlen: `konzeptfrage.txt`, `senses-lesung.tsv`.

- **Was die Lesung als Tier hergibt:** 955 Belege (7,3 % von 13.135): `saeugetier` 433, `vogel` 239, `andere` 171, `unbestimmt` 95, `fisch` 17 (433 + 239 + 171 + 95 + 17 = 955). Nach `art`: Nahrungsaufnahme 602, Füttern 152, Sonstiges 105, Übertragenes 96. 776 davon mit `@ana` auf 78 der 485 Bedeutungen mit `concept_21111000`, 179 ohne `@ana` (`tier`-Belege der Vorsortierung ohne Bedeutung).
- **Das Korpus gibt also nicht nur Säugetiere her:** Vögel in 31 Bedeutungen (200 Beleg-Bedeutung-Paare), Fische in 9 (15), andere Tierklassen in 25 (147), nicht bestimmbar in 21 (81). Ein Beleg mit zwei Zielbedeutungen würde hier bei jeder zählen.
- **Option 1, "Stoffwechsel von Säugetieren" umbenennen** (`concept_14011240`): 26 Bedeutungen im Lexikon tragen das Konzept, 494 Korpusbelege (`<w>` mit `@ana`) hängen an 23 von ihnen. Nur 2 der 26 tragen zugleich `concept_21111000` (`lemma_29516_sense_46357`, `lemma_47667_sense_74826`). Die Umbenennung würde diese 26 Bedeutungen umdeuten, aber von den 433 als Säugetier gelesenen Belegen nur 2 erreichen (beide an `lemma_29516_sense_46357`, iterücken); von den übrigen 331 mit `@ana` stehen die an anderen Bedeutungen (siehe unten), und 100 haben gar kein `@ana`. Vögel und die übrigen Klassen bleiben ohne Platz (für Vögel gibt es "Stoffwechsel von Vögeln", `concept_14021230`, mit 8 Bedeutungen, davon keine zusammen mit 21111000).
- **Option 2, neue Kategorie "Ernährung von Säugetieren":** betrifft die 53 Bedeutungen mit `concept_21111000`, an denen mindestens ein Beleg als Säugetier gelesen ist (333 Belege, keiner davon mit zwei Zielbedeutungen; dazu 100 Säugetier-Belege ohne `@ana`, die an keiner Bedeutung hängen). Der Befund dahinter: **die Tierbelege sitzen meist als Minderheit in Bedeutungen, die sonst Menschen meinen.** In nur 23 der 78 Bedeutungen mit Tierbelegen ist mehr als die Hälfte der gelesenen Belege `tier` (zusammen 48 Belege); in 52 sind sie die Minderheit und in 3 genau die Hälfte (`kropfizen` 1 von 2, `vrëʒʒen` 14 von 28, `hungernôt` 4 von 8); am stärksten bei `ëʒʒen` (`lemma_1764_sense_2754`: 216 Tier-Belege unter 3.507 gelesenen), `spîse` (127 unter 1.878), `hunger` (69 unter 589) und `trinken` (45 unter 1.460). Ein zusätzliches Konzept an diesen Bedeutungen würde also meist Menschenbelege mitziehen; der Weg ist eine neue Bedeutung je Lemma, wie sie KZW für lëcken beschrieben hat.
- **Lemmata aus dem Bereich vrezzen, die sie ansehen müsste:** 98 Lemmata mit mindestens einem Beleg als Tier, 34 mit mindestens fünf, 18 mit mindestens zehn. Mit den meisten Tierbelegen, geordnet nach der Zahl: `vrëʒʒen` (46 von 75 gelesen), `verslinden` (45 von 111), `nagen` (24 von 83), `weide` (22 von 41), `sûgen` (21 von 112), `hungerc` (21 von 78), `bîʒen` (16 von 74), `nern` (14 von 32), `vuotern` (12 von 23), `erbîʒen` (11 von 31), `luoder` (10 von 17). Daneben die vier großen allgemeinen Lemmata mit absolut den meisten Tierbelegen: `ëʒʒen` 216, `spîse` 127, `hunger` 69, `trinken` 45. Alle Lemmata in `lemmata-lesung.tsv`.

**Restliste für die EIL-Prüfung:** 235 Belege mit Urteil `unklar` (218 mit `@ana`, 17 ohne), dazu die 5 Belege aus `pruefen-603.tsv`; filterbar in `zweite-lesung.tsv` über die Spalte `wer`. Daneben die 20.023 nicht gelesenen Belege ohne `@ana`.

## Regenerieren

Die Skripte der Vorsortierung lesen nur und ändern im Repo nichts (die der zweiten Lesung, siehe unten, schreiben in einen Ausgabeordner, den man bewusst wählt). Der Ausgabeordner von `vorsortieren-603.py` ist Pflicht und darf nicht im Repo liegen, außer in einem Unterordner von `temp/` (gitignoriert); `stichprobe2-603.py` schreibt in denselben Ordner, `ana-603.py` liest nur und gibt auf der Konsole aus. `vorsortieren-603.py` liest die Eingabe `agent-faelle.tsv` aus diesem Ordner im Repo und bricht ab, wenn sie nicht zu den Fallbelegen passt. Wer die Dateien hier erneuern will, vergleicht die Ausgabe und kopiert sie bewusst:

```
python scripts/review/vorsortieren-603.py <repo> <ausgabeordner>
python scripts/review/stichprobe2-603.py <ausgabeordner>
python scripts/review/ana-603.py ingest/review/603-ernaehrung
```

`vorsortieren-603.py` liest `lexicon.xml`, `concepts.xml` und alle 667 TEI-Dateien. Beim Nachlauf am 16.10.2026 waren acht Ausgaben byte-gleich mit den Dateien hier (`senses-21111000`, `belege-tier`, `lemmata-ohne-ana`, `faelle-abebizen-lecken`, `konzepte-tier`, `stichprobe`, `stichprobe2-tier-ohne-mensch`, `zusammenfassung`); `stichprobe-urteile.tsv` und `agent-faelle.tsv` sind Eingaben und werden nicht erzeugt. Ändert sich Lexikon oder Korpus, ändern sich Zahlen und Stichproben.

Die zweite Lesung (nicht deterministisch, denn die Urteile stammen von Agenten) läuft so: `alle-belege-vorsortiert.tsv` aus dem Lauf oben nach Klasse filtern (`klasse` = `unklar` oder `mensch` und `sense_ids_im_ana` beginnt mit `lemma_`; `tier` ist `belege-tier.tsv`), daraus `python scripts/review/stapel-603.py <repo> <eingabe.tsv> <stapelordner> 80` bauen, die Stapel lesen lassen, dann `python scripts/review/verbinden-lesung-603.py <stapelordner> <eingabe.tsv> <teilname>` je Klasse und zuletzt `python scripts/review/auswerten-lesung-603.py <repo> <teil-tier.tsv> <teil-unklar.tsv> <teil-mensch.tsv> ingest/review/603-ernaehrung`. Die Urteile selbst sind Eingabe, `zweite-lesung.tsv` ist ihre verbundene Form und wird nicht neu erzeugt.
