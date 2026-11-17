# BRE: Weingrüße (Brevitas-Edition, Silvan Wagner)

Ingest der Weingrüße aus der Hybridedition von Silvan Wagner (Issue [#147](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/147)): 21 Überlieferungszeugen, 15 Handschriften und 6 Drucke, transkribiert im [Brevitas-Wiki](https://wiki.brevitas.org/wiki/Dokumentation_Edition_Weingr%C3%BC%C3%9Fe). Aufgenommen wird die Überlieferung je Zeuge, nicht der Editionstext (Silvan, Mail vom 23.10.2026).

> **Stand 2026-11-17: Stufe 0 und Phase 1 bis 3 für 18 von 21 Zeugen**, nach dem Muster in [`docs/DATA-MODEL.md` → Ingest procedure](../../../docs/DATA-MODEL.md#ingest-procedure-taking-in-new-texts). Geschrieben sind die Zeugen in `ingest/bre/BRE_*.tei.xml`. B2, d4 und d6 fehlen, weil ihre Segmentierung auf Silvans Antwort wartet (`SEGMENTIERUNG_OFFEN` in `bre_common.py`). Die maschinellen Zuweisungen sind nicht geprüft, das Prüfpaket liegt in [`ingest/bre/pruefung/`](../../../ingest/bre/pruefung/README.md). Nichts davon ist in `tei/`, und `lexicon.xml` ist nicht verändert.

## Quelle und Rechte

- **Lizenz:** Silvan hat die Transkriptionen auf wiki.brevitas.org am 23.10.2026 schriftlich unter CC BY-NC-SA 4.0 freigegeben (Mail an KZW, festgehalten in #147).
- **Rohtext nur über die API.** Der MediaWiki-Renderer verschluckt die Spitzklammern der editorischen Ergänzungen (`er<nider>`), im HTML sind sie unsichtbar. `00-fetch-wiki.py` lädt deshalb den Wikitext über `api.php`.
- **Gepinnt.** Jede Seite wird mit ihrer Revisions-ID geladen. Silvan arbeitet am Wiki weiter, ein neuer Stand kommt nur über `00-fetch-wiki.py --neu` ins Manifest.
- **Nicht im Repository**, sondern lokal unter `sources/weingruesse/` (gitignoriert): die Druckfahnen der Hirzel-Ausgabe (Verlagsrechte ungeklärt, #147) und Silvans Word-Transkriptionen von 2022 samt docling-Umwandlung. Die Word-Dateien enthalten im Kern denselben Wikitext, maßgeblich ist das Wiki.

## Skripte

| Skript | Was es tut | Schreibt |
|---|---|---|
| `00-fetch-wiki.py` | Lädt Dokumentationsseite, Hauptseite, die 21 Transkriptionen und die Einzeltextseiten in den Cache `temp/bre-wiki/`. Mit Manifest gepinnt per Revisions-ID, sha256-Abweichung ist ein harter Fehler. `--offline`: nur Cache. `--neu`: Manifest aus den aktuellen Revisionen | `ingest/bre/revisionen.tsv` |
| `01-segmentierung.py` | Liest aus jeder Einzeltextseite die Infobox (Blattangabe je Zeuge) und die Synopse (erster Vers und Überschrift je Zeuge) | `ingest/bre/segmentierung.tsv` |
| `02-convert-wiki-to-mhdbdb.py` | Konvertiert einen Zeugen nach MHDBDB-TEI und validiert gegen `schema/mhdbdb.rng`. `--zeuge alle` schreibt die 18 Zeugen ohne offene Segmentierung, `--zeuge alle --trocken` fährt alle 21 ohne Ausgabedatei | `ingest/bre/<SIGLE>.tei.xml` |
| `03-hauptseite-abgleich.py` | Gleicht die Werkzuordnung je Zeuge mit der Überlieferungsbeschreibung der Hauptseite ab (Abschnitt „Werkzuordnung“ unten). Exit 2, wenn eine Abweichung nicht in `ABWEICHUNG_ERKLAERT` steht | `ingest/bre/hauptseite-abgleich.tsv` |
| `10-lemma-assign.py` | Phase 1: Auto-Match der Wortformen gegen `variants.xml`, setzt `@lemmaRef` bei genau einem Kandidaten, sortiert die mehrdeutigen nach Stufen | `ingest/bre/phase1/lemma-pending.tsv`, `lemma-unmatched.tsv` |
| `11-batches.py` | Schneidet die Pending-TSV einer Phase in LLM-Batches zu etwa 50 Zeilen (`temp/bre-batches/`, gitignoriert) | |
| `12-entscheidungen.py` | Sammelt die LLM-Antworten einer Phase (`temp/bre-entscheidungen/`), prüft sie gegen die Kandidaten und schreibt Bulk- und Patch-Tabelle mit `decision_type`, `confidence`, `reviewer` | `ingest/bre/phaseN/<phase>-bulk.tsv`, `-patch.tsv` |
| `13-lemma-apply.py` | Phase 1: setzt `@lemmaRef` aus Bulk und Patch | TEI |
| `14-pos-assign.py` | Phase 2: Wortart vom Lemma, bei genau einem Kandidaten direkt | TEI, `ingest/bre/phase2/pos-pending.tsv` |
| `15-apply.py` | Phase 2 und 3: setzt `@pos` oder `@ana` aus Bulk und Patch (`--phase pos\|sense`) | TEI |
| `16-sense-assign.py` | Phase 3: Sense bei genau einem Kandidaten direkt, sonst Kandidaten mit Konzeptlabels | TEI, `ingest/bre/phase3/sense-pending.tsv` |
| `18-corresp.py` | Phase 3: `@corresp` auf den Variantentyp, nur bei genau einem Treffer | TEI, `ingest/bre/phase3/corresp-mehrdeutig.tsv` |
| `20-pruefpaket.py` | Prüfpaket für Julia und KZW | `ingest/bre/pruefung/*.tsv` |
| `21-abdeckung.py` | Abdeckung je Zeuge und Attribut, prüft Referenzen, 19er-Tagset, `@ana` passend zu `@lemmaRef`, `<head>` unannotiert und das Schema; Exit 1 bei Fehlern | |
| `bre_annot.py` | Gemeinsame Helfer der Phasen: Wortform, Normalisierung, Lexikon, Varianten, TSV | |
| `bre_common.py` | Zeugentabelle (Editionssigle, Wiki-Seite, MHDBDB-Sigle), Vorspann-Tabelle, Faltungstabelle, geprüfte Abweichungen zur Hauptseite, offene Segmentierung, ausgeschlossene Teile, API und Cache | |
| `bre_hauptseite.py` | Liest Liste und Übersichtstabelle der Hauptseite und vergleicht sie mit der Segmentierung | |
| `bre_wikitext.py` | Hilfsfunktionen für den Wikitext | |
| `test_bre.py` | Mini-Fixtures aus Cgm 713 und konstruierte Fehlerfälle | |

```bash
python -P -E scripts/ingest/bre/00-fetch-wiki.py --offline
python -P -E scripts/ingest/bre/01-segmentierung.py
python -P -E scripts/ingest/bre/02-convert-wiki-to-mhdbdb.py --zeuge B
python -P -E scripts/ingest/bre/02-convert-wiki-to-mhdbdb.py --zeuge alle --trocken
python -P -E scripts/ingest/bre/03-hauptseite-abgleich.py
python -P -E scripts/ingest/bre/test_bre.py

# Phasen (die LLM-Antworten liegen in temp/, gitignoriert; die Entscheidungen in ingest/bre/phaseN/)
python -P -E scripts/ingest/bre/10-lemma-assign.py
python -P -E scripts/ingest/bre/13-lemma-apply.py
python -P -E scripts/ingest/bre/14-pos-assign.py
python -P -E scripts/ingest/bre/15-apply.py --phase pos
python -P -E scripts/ingest/bre/16-sense-assign.py
python -P -E scripts/ingest/bre/15-apply.py --phase sense
python -P -E scripts/ingest/bre/18-corresp.py
python -P -E scripts/ingest/bre/20-pruefpaket.py
python -P -E scripts/ingest/bre/21-abdeckung.py --markdown
```

Die Assign-Skripte teilen die Wörter unabhängig davon ein, ob ein Attribut schon gesetzt ist: ein zweiter Lauf schreibt dieselben Zeilen in die Pending-TSV, auch mit `--trocken` (das lässt nur die TEI unberührt), aber mit leeren Auflösungsspalten. Erst das zugehörige Apply-Skript füllt sie wieder und setzt dieselben Werte noch einmal; danach sind TEI und Pending-TSV byte-gleich zum vorigen Stand (gemessen 17.11.2026 für 10 und 13, 14 und 15 `--phase pos` und für 18, das ohne Pending-TSV auskommt und dieselben Zahlen wieder ausgibt). Ein vorhandener Wert, der der Einteilung widerspricht, ist ein harter Fehler.

Der erste Lauf von `00` braucht das Netz, danach reicht `--offline`.

## Segmentierung: warum über die Synopsen

Eine Transkriptionsseite enthält alle Weingrüße eines Zeugen hintereinander, ohne Grenzmarke. Zwei naheliegende Signale tragen nicht, beide an Cgm 713 gemessen:

- **Leerzeilen** trennen Texte, stehen aber auch vor jedem Folio-Marker, sogar mitten im Wort („schen-“ / `[188v]` / „ken hat erdacht“).
- **Die Grußformel** beginnt einen Text („Nu grüß dich got …“), kommt aber auch als Schlussformel vor („Gesegen dich got und kum schier hierwider“).

Verlässlich ist die Synopse jeder Einzeltextseite: sie nennt je Zeuge den ersten Vers. `02` sucht diesen Vers in der Transkription, und jede Zeile muss genau einem Text zugeordnet sein. Was davor steht, muss in der Vorspann-Tabelle in `bre_common.py` stehen, sonst bricht das Skript ab. Dort stehen drei Arten:

- **Reihentitel** (S, d1 bis d6): eine Titelzeile vor dem ersten Weingruß, wird `<head>` des äußeren `<div>`. Vor dem ersten Text gilt eine Zeile nur dann als dessen Überschrift, wenn die Synopse sie als Überschrift dieses Zeugen führt. Eine fette oder rote Zeile allein genügt dort nicht, sonst rutschte der fett gesetzte Drucktitel von d5 und d6 in den ersten Einzeltext.
- **Text ohne Einzeltextseite** (N²): „Ain spruch vom rebhänßlin“ mit vier Versen, den die Einleitung der Druckfahnen in Kapitel V.3 zitiert. Eigenes `<div>`.
- **Fragment** (R): die ersten drei Verse auf Bl. 13r sind die letzten drei Verse von „Weinsegen Allerliebster Trost“, fragmentarisch überliefert. Die Hauptseite sagt das ausdrücklich („nur die letzten drei Verse“, siehe unten), in der Synopse und der Infobox der Einzeltextseite fehlt R. Eigenes `<div>`, `VORSPANN_WERK` in `bre_common.py` benennt das Werk. Bis zum 12.11.2026 stand hier und in `VORSPANN_NOTIZ`, die drei Verse seien „keiner Einzeltextseite zugeordnet“: aus dem Fehlen in der Synopse war auf eine fehlende Werkzuordnung geschlossen worden (#147, Kommentar vom 12.11.).

Eine **Faltungstabelle** gleicht beim Vergleich, nie in der Ausgabe, eine Zeichenabweichung zwischen Synopse und Transkription aus: „ů“ gegen „uͦ“ (u mit U+0366). Sie greift zweimal, beim ersten Vers von „Weingruß Neczen Gumen“ in W¹ (Zeile 331 der Wikiseite) und bei der Kopfzeile „Gůten wein gruͤsz ich“ in d5 (Zeile 10). Das Skript gibt jede Anwendung aus.

## Werkzuordnung: die Hauptseite ist maßgeblich

Silvan Wagner empfiehlt (Rückmeldung an KZW, festgehalten in #147 am 12.11.2026) den Abschnitt „Überlieferung“ der [Hauptseite](https://wiki.brevitas.org/wiki/Kategorie:Quelle_Weingru%C3%9F#%C3%9Cberlieferung) als Grundlage für die Identifikation der Einzeltexte: Werkzuordnung und Überlieferungsbesonderheiten je Zeuge. Die Synopsen sind ergänzend (Textvergleich, Auffinden von Stellen), die Transkriptionsseiten tragen den Wortlaut und die Reihenfolge im Zeugen. Dass jede Quellzeile genau einem Abschnitt zugeordnet ist, belegt die vollständige Verarbeitung der Zeilen, nicht die philologische Richtigkeit der Zuordnung.

- **Gepinnt:** `00-fetch-wiki.py` lädt die Hauptseite „Kategorie:Quelle Weingruß“ wie die anderen Seiten und führt sie im Manifest (Revision 31127 vom 11.11.2026; der Abschnitt „Überlieferung“ ist mit Revision 30019 vom 15.06.2026 wortgleich, die beiden Revisionen unterscheiden sich nur in der Kopfzeile der Seite).
- **Gelesen** wird zweierlei, beides in `bre_hauptseite.py`: die Liste je Zeuge (nummerierte Listen unter `;Sigle`, Anmerkungen wie „nur die letzten drei Verse“, Klammern für in andere Texte aufgenommene Abschnitte) und die „Übersicht der Überlieferung“ (Tabelle Text × Zeuge mit Stellung).
- **Abgleich:** `03-hauptseite-abgleich.py` vergleicht je Zeuge die Texte der Transkription mit der Liste (Titel, Menge, Reihenfolge) und schreibt die Abweichungen nach `ingest/bre/hauptseite-abgleich.tsv`. `02` ruft denselben Abgleich auf: eine Abweichung, die nicht in `ABWEICHUNG_ERKLAERT` (`bre_common.py`) mit Begründung steht, bricht die Konversion ab. Der Schlüssel trägt den Inhalt der Abweichung (Zeuge, Art, Text, Anzahl der Abschnitte oder fehlenden Vorkommen, bei einer anderen Reihenfolge die Stellen und die Folge auf beiden Seiten): eine andere Abweichung der gleichen Art, etwa eine zusätzliche Vertauschung, ist nicht erklärt und bricht ab (Test in `test_bre.py`). Der Eintrag dort erklärt oder hält eine offene Frage fest, er korrigiert nichts.
- **Stand 13.11.2026:** 15 von 21 Zeugen stimmen mit der Liste überein (Titel, Menge, Reihenfolge), R nach der Korrektur oben. Die übrigen sechs (B2, N², W¹, d4, d5, d6) stehen in `hauptseite-abgleich.tsv` mit Befund. Die Liste der Hauptseite ist selbst nicht widerspruchsfrei: sie weicht von der Übersichtstabelle derselben Seite ab bei d4 (Reihenfolge von Edels Getranck und Edle Leibsalb, und Allerliebster Trost als „(4)“ nur in der Übersicht), d5 (zwei Texte fehlen) und B (Creftenreiche Labung als „(7)“ nur in der Übersicht), und in B2 nennt der Satz 19 Weingrüße bei 18 Einträgen.

## Abbildung

| Wikitext | TEI |
|---|---|
| `[188v]` | `<pb n="188v"/>` |
| `===A:===`, `=== Teil A ===` (D, W¹) | `<div n="A">` um die Einzeltexte dieses Teils |
| Zeile mit `<br />` | `<l n>` |
| `<span style="color:#FF0000">` | `<hi rend="inkRed">` wie in WZB, dem bisher einzigen Text mit diesem Wert (die Leseansicht stellt ihn nicht rot dar, `docs/DESIGN.md`). Lombarde im Wort: `<w><hi rend="inkRed">Gr</hi>üß</w>` |
| rote oder fette Ganzzeile, Synopsen-Überschrift | `<head>` |
| `'''x'''`, `''x''` | `<hi rend="bold">`, `<hi rend="italic">` |
| `<s>`, `<del>`, `<u>`, `<sup>` | `<hi rend="line-through">`, `"underline"`, `"superscript"` |
| `(er)` | `<expan>er</expan>` |
| `(?)`, `(...)` | `<note type="transcription">Lesung unsicher</note>`, `<gap reason="illegible"/>` |
| `\x/`, `/x\`, `\|x\|` | `<add place="below">`, `"above"`, `"margin"` |
| `<x>` (roh) | `<supplied>` |
| `<ref>t</ref>` | `<note type="transcription">` hinter dem Wort |
| Worttrennung über Seitenwechsel, Blattmarke im Wort | ein `<w>`: `schen<pb n="188v"/>ken`, `wein<pb n="9"/>reben` |

Ein Weingruß ist ein `<div type="section">`. Die xml:id folgt dem WZB-Muster `{SIGLE}_{Blatt}_{Zeile auf dem Blatt}_{Token}`. d2 ist nach der Ausgabe Weller 1874 transkribiert und hat keine Blattangaben, dort steht Blatt `0` und die Zeilen laufen durch. Kombinierende Diakritika der Drucke bleiben unverändert.

## Phase 1 bis 3

### Was annotiert wird

- **Wortform ist `''.join(w.itertext())`, nie `w.text`.** Ein BRE-`<w>` kann `<expan>`, `<supplied>`, `<add>`, `<hi>` und `<pb>` enthalten, `w.text` gäbe bei `v<expan>er</expan>stoppffen` nur „v“. `build-corpus-index.py` und `extract-variants.py` lesen ebenfalls itertext.
- **Strukturbereinigung nach #66** (Tabelle in `docs/DATA-MODEL.md` → Structural cleanup): Satzzeichen stehen seit Stufe 0 als eigenes `<pc>` neben dem Wort (d2, d3 und d5 sind interpungiert), Apostroph und Bindestrich bleiben im Wort. **Rubriken und Reihentitel sind Text, aber nicht lexikalisch:** jedes `<w>` in `<head>` bleibt ohne `@lemmaRef`, `@pos` und `@ana`. Das sind 451 `<w>` (Ausgabe von `10-lemma-assign.py`), `21-abdeckung.py` prüft, dass keines annotiert ist.
- **Normalisierung auf beiden Seiten:** `normalize_mhg` wie in WZB, davor eine Faltung der Drucktypen (U+0364 über dem Vokal wird Umlaut, `uͦ` und `ů` werden `uo`). Ohne Faltung hätten 450 Wörter keinen eindeutigen Treffer.

### Abdeckung

Gemessen am 17.11.2026 mit `python -P -E scripts/ingest/bre/21-abdeckung.py --markdown`, Nenner ist je Zeile die Zahl der lexikalischen `<w>` (ohne die in `<head>`):

| Zeuge | Datei | lexikalische `<w>` | `@lemmaRef` | `@pos` | `@ana` | `@corresp` |
|---|---|--:|--:|--:|--:|--:|
| M1 | BRE_CGM216 | 93 | 84 (90.3 %) | 80 (86.0 %) | 80 (86.0 %) | 50 (53.8 %) |
| B | BRE_CGM713 | 1028 | 972 (94.6 %) | 944 (91.8 %) | 963 (93.7 %) | 535 (52.0 %) |
| S | BRE_COD13711 | 1504 | 1399 (93.0 %) | 1359 (90.4 %) | 1384 (92.0 %) | 751 (49.9 %) |
| H1 | BRE_CPG98 | 268 | 254 (94.8 %) | 248 (92.5 %) | 253 (94.4 %) | 152 (56.7 %) |
| d1 | BRE_D1 | 2742 | 2585 (94.3 %) | 2505 (91.4 %) | 2552 (93.1 %) | 1404 (51.2 %) |
| d2 | BRE_D2 | 2674 | 2505 (93.7 %) | 2460 (92.0 %) | 2489 (93.1 %) | 1397 (52.2 %) |
| d3 | BRE_D3 | 3115 | 2956 (94.9 %) | 2838 (91.1 %) | 2912 (93.5 %) | 1636 (52.5 %) |
| d5 | BRE_D5 | 2931 | 2755 (94.0 %) | 2698 (92.1 %) | 2736 (93.3 %) | 1634 (55.7 %) |
| U | BRE_GEORG1508 | 1702 | 1560 (91.7 %) | 1520 (89.3 %) | 1542 (90.6 %) | 929 (54.6 %) |
| R | BRE_GUELF296 | 475 | 447 (94.1 %) | 435 (91.6 %) | 443 (93.3 %) | 282 (59.4 %) |
| F | BRE_HS5339A | 3045 | 2833 (93.0 %) | 2786 (91.5 %) | 2803 (92.1 %) | 1560 (51.2 %) |
| N2 | BRE_MERKEL966 | 961 | 862 (89.7 %) | 793 (82.5 %) | 835 (86.9 %) | 506 (52.7 %) |
| B1 | BRE_MGQ2370 | 2443 | 2265 (92.7 %) | 2168 (88.7 %) | 2228 (91.2 %) | 1262 (51.7 %) |
| L | BRE_MS1590 | 648 | 605 (93.4 %) | 577 (89.0 %) | 596 (92.0 %) | 344 (53.1 %) |
| D | BRE_MSCRM50 | 1801 | 1691 (93.9 %) | 1649 (91.6 %) | 1669 (92.7 %) | 960 (53.3 %) |
| C | BRE_MSGER74 | 693 | 639 (92.2 %) | 605 (87.3 %) | 635 (91.6 %) | 367 (53.0 %) |
| W1 | BRE_OCT145 | 3085 | 2894 (93.8 %) | 2782 (90.2 %) | 2842 (92.1 %) | 1560 (50.6 %) |
| W | BRE_QUART564 | 1008 | 939 (93.2 %) | 917 (91.0 %) | 934 (92.7 %) | 536 (53.2 %) |
| gesamt |  | 30216 | 28245 (93.5 %) | 27364 (90.6 %) | 27896 (92.3 %) | 15865 (52.5 %) |

### Phase 1: Lemma

`python -P -E scripts/ingest/bre/10-lemma-assign.py --trocken` gibt aus:

- eindeutig: 17525 von 30216 (58,0 %), davon 450 nur dank der Faltung
- mehrdeutig: 10893 von 30216 (36,1 %) in 547 Formen, nach Stufen: bulk 10569 Wörter in 313 Formen (ab 3 Belegen), instance 180 in 90 Formen (2 Belege), hapax 144 in 144 Formen (zurückgestellt)
- ohne Treffer: 1798 von 30216 (6,0 %) in 1198 Formen, nach Häufigkeit in `ingest/bre/phase1/lemma-unmatched.tsv`

Die mehrdeutigen hat Claude Sonnet am Kontext entschieden (Abschnitt „LLM-Entscheidungen“ unten). Gesetzt sind 28245 `@lemmaRef` = 17525 eindeutig + 10720 entschieden (Ausgabe von `13-lemma-apply.py`). Von den 10893 mehrdeutigen bleiben 173 offen: 144 Hapaxe und 29 abstain. Ein Lemma außerhalb der Kandidaten wird angenommen, wenn es im Lexikon steht, aber auf `low` gesetzt und mit „[außerhalb der Kandidaten]“ markiert, damit es im Prüfpaket landet. **Keine neuen Lemmata, keine Änderung an `lexicon.xml`.**

### Phase 2: Wortart

Die Kandidaten kommen aus dem Lemma, abgebildet auf das 19er-Set (`docs/POS-TAGSET.md`): `ART` wird `DET`, `GRA` fällt weg (§3: Graduierung ist kein eigenes Tag, `wzb-pos-assign.py` bildet es auf `ADV` ab, das widerspricht §3). Ein Lemma, das nur `GRA` trägt, bekommt `ADJ`. Steht `CNJ` unter den Kandidaten, sind auch `CCNJ` und `SCNJ` erlaubt.

`14-pos-assign.py` gibt 12044 Wörter mit genau einer Wortart aus, `15-apply.py --phase pos` von 16200 mehrdeutigen 15320 entschieden (bulk-llm 12754, instance-llm 2566), 387 abstain, 493 Hapaxe (15320 + 387 + 493 = 16200). Zusammen 27364 `@pos`.

Ein gültiger Tag, der nicht unter den Kandidaten des Lemmas steht, wird nicht geschrieben, sondern abstain mit dem Präfix „[verworfen: X ist kein Kandidat]“ in der Begründung (`12-entscheidungen.py`). **Befund:** 132 der 387 abstain betreffen *zuo* (`lemma_7770`), das im Lexikon nur `CNJ` und `PRP` hat. Als Gradwort („zu vil“) oder Verbpartikel wäre es `ADV`. Das ist eine Lücke im Lemma, kein Fehler der Zuweisung (Zählung: `decision_type` abstain in `phase2/pos-pending.tsv`, nach `lemma_id`).

### Phase 3: Bedeutung und Variantentyp

`16-sense-assign.py` und `15-apply.py --phase sense` geben aus: 20190 Wörter mit genau einem Sense direkt, von 8055 mehrdeutigen 7706 entschieden (bulk-llm 6123, instance-llm 1583), 233 abstain, 116 Hapaxe (7706 + 233 + 116 = 8055). Zusammen 27896 `@ana`. Kein Lemma ohne Sense. `@ana` steht nie ohne `@lemmaRef`, und der Sense gehört immer zum Lemma (`21-abdeckung.py`).

**Befund: Die Sense-abstains finden falsche Lemmata aus Phase 1.** Passt keine Bedeutung des Lemmas, ist meist das Lemma falsch. 190 der 233 abstain haben ihr Lemma aus dem Auto-Match: die Form steht in `variants.xml` nur unter einem Lemma und hat es ohne Kontextprüfung bekommen, ist hier aber ein anderes Wort, etwa „dorffen“ (Dörfer) unter *durfen* oder „imm“ (ihm) unter *ime*. Die übrigen 43 haben ihr Lemma aus der LLM-Entscheidung (39 bulk, 4 instance). Alle 233 stehen in `ingest/bre/pruefung/lemma-verdacht.tsv` (Ausgabe von `20-pruefpaket.py`). Die Wortart dieser Wörter ist mit dem Lemma vererbt und damit ebenso verdächtig. Korrigiert ist nichts, das entscheidet die Prüfung.

**`@corresp` nur bei genau einem Treffer** (Algorithmus wie `wzb-sense-apply.py`): Typen aus `variants.xml`, deren Form normalisiert gleich der Wortform ist, die zum Lemma gehören und im `@ana` des Senses stehen. `18-corresp.py` gibt aus: 15865 von 27896 Wörtern mit `@ana` gesetzt, 3802 ohne Typ, 8211 mit mehreren Typen (`phase3/corresp-mehrdeutig.tsv`), 18 mit `<supplied>` ausgenommen (15865 + 3802 + 8211 + 18 = 27896).

- **Welche Form zählt bei `<expan>`: die aufgelöste.** Die Abkürzungsgraphie ist nicht überliefert: das Wiki schreibt nur die Auflösung in Klammern, und Stufe 0 macht daraus `<expan>` ohne `<abbr>`. Eine andere Form als die aufgelöste gibt es im TEI nicht, und Index und Suche lesen ebenfalls itertext. 1023 der gesetzten `@corresp` stehen auf einem Wort mit `<expan>`.
- **Wörter mit `<supplied>` bekommen keinen Typ:** die ergänzten Buchstaben stehen nicht in der Handschrift, die Form wäre eine des Herausgebers.
- **Befund: Die 8211 mehrdeutigen sind fast alle Zirkumflex-Paare.** „Nu“ trifft normalisiert *nu* und *nû*, „du“ trifft *du* und *dû*. Ein exakter Vergleich der Form (klein geschrieben, gefaltet) vor dem normalisierten würde 8166 der 8211 auflösen, 45 blieben (gemessen mit einem Skript im Scratchpad, nicht im Repo). Das ist eine Änderung am Algorithmus, die auch WZB beträfe, und ist deshalb nicht umgesetzt.

### LLM-Entscheidungen

- **Modell:** Claude Sonnet 5.5 als Subagent, Batches zu etwa 50 Zeilen. Jede Zeile trägt `decision_type` (`bulk-llm`, `instance-llm`, `abstain`), `confidence` (`high`, `medium`, `low`) und `reviewer` (`llm:claude-sonnet-5-5`). `abstain` ist gültig und wird nicht geschrieben.
- **Stufen:** Gruppen ab 3 Belegen werden als Ganzes entschieden (bulk) mit Ausnahmen je Beleg. Meldet das Modell `SPLIT`, weil die Belege zu verschiedenen Werten gehören, wird jedes Wort der Gruppe einzeln entschieden. Gruppen mit 2 Belegen werden je Wort entschieden, Hapaxe zurückgestellt. Gruppe ist in Phase 1 die normalisierte Form, in Phase 2 Lemma und Form, in Phase 3 das Lemma.
- **Kontext:** ±5 Wörter in der Eingabe. Die Synopse der Einzeltextseite im Wiki-Cache durfte das Modell bei Unsicherheit nachlesen, nach den eigenen Berichten hat es das selten getan. **Die Druckfahnen sind nicht benutzt worden**, weder als Kontext noch für Begründungen.
- **Kontrolle:** der Orchestrator (Claude Opus) hat aus Batches aller drei Phasen Stichproben am Kontext nachgesehen, verworfen werden musste keine Batch. Nachgebessert wurde einmal die Anweisung (Phase 1: „im“ = in dem), die zwei betroffenen Batches sind neu gerechnet. Werte außerhalb der Kandidaten fängt `12-entscheidungen.py` mechanisch ab (oben).
- **Die Anweisungen an das Modell** stehen in [`anleitungen/`](anleitungen/). Die Rohantworten liegen in `temp/` und sind nicht im Repository, die daraus gesammelten Entscheidungen in `ingest/bre/phaseN/*-bulk.tsv` und `*-patch.tsv` schon.

### Druckfahnen

Kein Wortlaut aus Text, Übersetzung oder Kommentar der Hirzel-Druckfassung steht im Repository. `test_bre.py` prüft das mechanisch. Quelle ist der Text der Druckfahnen-PDF, den `pdftotext` auf stdout liefert (nie als Datei abgelegt, Silbentrennung am Zeilenende zusammengezogen), dazu Silvans Word-Steckbriefe von 2022 (`sources/weingruesse/docling/`), die der Kickoff zum selben Material zählt. Jede Folge von sechs Wörtern daraus, die nicht auch im Wiki oder im TEI-Wortlaut vorkommt, darf in keiner Datei unter `ingest/bre/` und `scripts/ingest/bre/` stehen (TSV je Feld) und in keiner Commit Message seit `origin/main`. Weitere Texte vor dem Absenden (PR-Body, Issue-Kommentar) prüft `BRE_DRUCK_PRUEFE=<datei>[;<datei>]`. Fehlt die PDF, `pdftotext`, die Steckbriefe oder der Wiki-Cache, schlägt der Test fehl, statt still zu bestehen. Nicht erfasst sind Folgen unter sechs Wörtern und Ziffern.

Bis zur ersten Review-Runde las der Test nur die Steckbriefe und hielt sie für die Druckfahnen. Gefunden hatte er damals ein Steckbrief-Zitat in der Spalte `abweichung_steckbrief_2022` von `ingest/bre/zeugen.tsv` (Zeile C, seit #654 auf `main`), das in diesem Branch umformuliert ist. Der Test mit der PDF fand dann eine Wendung der Druckfahnen in der Spalte `ort` derselben Datei (Zeile d4, ebenfalls seit #654), jetzt in eigenen Worten. Beide stehen weiter in der Git-Geschichte von `main`. Gegenprobe am 17.11.2026: eine wörtliche Zeile aus dem PDF-Text und eine Folge über eine Silbentrennung, beide über `BRE_DRUCK_PRUEFE` eingespeist, machen den Test rot.

## Offene Entscheidungen

- **Schema: entschieden (Weg 1, KZW am 11.11.2026).** `<w>` erlaubt seit dem 11.11.2026 zusätzlich `<expan>`, `<supplied>`, `<add>` und `<pb>` (`schema/mhdbdb.rnc`, `.rng` neu erzeugt). Die Transkriptionen tragen im Wort Abkürzungsauflösungen, Ergänzungen, Nachträge und in zwei Fällen einen Seitenwechsel: bei Cgm 713 über eine Worttrennung („schen-“ / „ken“), bei d4 als Blattmarke mitten im Wort („wein[9]reben“). Mit dem erweiterten Schema validieren alle 21 Zeugen (`02 --zeuge alle --trocken`, gemessen 13.11.2026); vorher validierte nur d2. Die Leseansicht zeigt die Auszeichnung im Wort nicht, sie ist nicht angefasst.
- **Siglen.** `BRE_<Signatur>` für die Handschriften und `BRE_D1` bis `BRE_D6` für die Drucke folgen dem Vorschlag vom 10.07.2026 in #147, bestätigt sind sie nicht.
- **Werk, Gattung, Sprachstufe** stehen als `work_TBD`, `genre_TBD` und `TBD` im Header. Die Sprachstufe entscheidet #118.
- **Segmentierung (Punkt 5 in #147).** Silvans Antwort (12.11.2026) benennt die Hauptseite als Grundlage für die Werkzuordnung, die Synopsen sind ergänzend (Abschnitt „Werkzuordnung“ oben). Die Abweichungen zwischen beiden stehen in `ingest/bre/hauptseite-abgleich.tsv`, offene Fälle sind dort als „offen“ vermerkt: B2 (Fehlansatz), d4 (Reihenfolge), d6 (in Klammern gesetzte Texte als eigene Abschnitte).
- **Epoche: entschieden.** Der zweite Teil der Weingrüße in D (Bl. 217r–221v) stammt laut Druckfahnen (Kapitel IV) aus dem 17. Jahrhundert und liegt außerhalb des Korpusumfangs (Texte vor 1600, #263). `02` schneidet ihn ab (`TEIL_AUSGESCHLOSSEN` in `bre_common.py`), nachdem die Segmentierung den ganzen Zeugen gesehen hat. Der Grund steht im Header von `BRE_MSCRM50.tei.xml` und als Kommentar an der Schnittstelle. Tests in `test_bre.py`: ein Text bleibt, einer entfällt, die Zeilenbilanz geht auf, der Grund steht im Header.

## Warum `ingest/bre/` und nicht `tei/`

Solange die Header Platzhalter tragen, würde `build-corpus-index.py` sie aus `tei/` mitsamt den Platzhaltern indizieren, und die Cross-Ref-Prüfung liefe ins Leere. Dieselbe Begründung wie bei ARI, siehe [`ingest/ari/README.md`](../../../ingest/ari/README.md).

## Für die Erratum-Liste an Silvan

- Druckfahnen, Kapitel V.3: N² ist dort ein Jahrhundert früher datiert (1424–1426), die Zeugenliste in Kapitel IV (S. XIII) und sein Steckbrief von 2022 sagen 1524–1526.
- Druckfahnen, S. XIV: Schreibfehler im Ortsnamen Weimar bei W¹.
- Wiki: „Weingruß Neczen Gumen“, erster Vers in W¹, Synopse „guͦmen“, Transkription „gůmen“.
- Wiki: „Vorspruch Weingruß“, Überschrift in d5, Synopse „Guͦten“, Transkription „Gůten“.
