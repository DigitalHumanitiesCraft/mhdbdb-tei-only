# BRE: Weingrüße (Brevitas-Edition, Silvan Wagner)

Ingest der Weingrüße aus der Hybridedition von Silvan Wagner (Issue [#147](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/147)): 21 Überlieferungszeugen, 15 Handschriften und 6 Drucke, transkribiert im [Brevitas-Wiki](https://wiki.brevitas.org/wiki/Dokumentation_Edition_Weingr%C3%BC%C3%9Fe). Aufgenommen wird die Überlieferung je Zeuge, nicht der Editionstext (Silvan, Mail vom 23.10.2026).

> **Stand 2026-11-27: Stufe 0 und Phase 1 bis 3 für alle 21 Zeugen**, nach dem Muster in [`docs/DATA-MODEL.md` → Ingest procedure](../../../docs/DATA-MODEL.md#ingest-procedure-taking-in-new-texts). Geschrieben sind die Zeugen in `ingest/bre/BRE_*.tei.xml`. B2, d4 und d6 sind seit Silvans Antwort vom 26.11.2026 geschrieben (Stufe 0) und seit dem 27.11.2026 annotiert und mit Normdaten im Header (`23`). Die maschinellen Zuweisungen sind nicht geprüft, das Prüfpaket liegt in [`ingest/bre/pruefung/`](../../../ingest/bre/pruefung/README.md) und ist für die ersten 18 Zeugen gebaut; für B2, d4 und d6 gibt es noch kein Prüfpaket. Nichts davon ist in `tei/`, und `lexicon.xml` ist nicht verändert.

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
| `02-convert-wiki-to-mhdbdb.py` | Konvertiert einen Zeugen nach MHDBDB-TEI und validiert gegen `schema/mhdbdb.rng`. `--zeuge alle` schreibt alle 21 Zeugen (ein Zeuge in `SEGMENTIERUNG_OFFEN` würde übersprungen, seit dem 26.11.2026 ist keiner offen), `--zeuge alle --trocken` fährt alle 21 ohne Ausgabedatei. Eine vorhandene Zieldatei ersetzt es nur mit `--ueberschreiben` (Sperre, Abschnitt unter der Befehlsfolge) | `ingest/bre/<SIGLE>.tei.xml` |
| `03-hauptseite-abgleich.py` | Gleicht die Werkzuordnung je Zeuge mit der Überlieferungsbeschreibung der Hauptseite ab (Abschnitt „Werkzuordnung“ unten). Exit 2, wenn eine Abweichung nicht in `ABWEICHUNG_ERKLAERT` steht | `ingest/bre/hauptseite-abgleich.tsv` |
| `10-lemma-assign.py` | Phase 1: Auto-Match der Wortformen gegen `variants.xml`, setzt `@lemmaRef` bei genau einem Kandidaten, sortiert die mehrdeutigen nach Stufen | `ingest/bre/phase1/lemma-pending.tsv`, `lemma-unmatched.tsv` |
| `11-batches.py` | Schneidet die Pending-TSV einer Phase in LLM-Batches zu etwa 50 Zeilen (`temp/bre-batches/`, gitignoriert). `--offen`: nur Zeilen ohne Entscheidung, für neu hinzugekommene Zeugen; `--stufe split --offen` für die Tokens in SPLIT-Gruppen ohne Token-Entscheidung | |
| `12-entscheidungen.py` | Sammelt die LLM-Antworten einer Phase (`temp/bre-entscheidungen/`), prüft sie gegen die Kandidaten und schreibt Bulk- und Patch-Tabelle mit `decision_type`, `confidence`, `reviewer`. `--ergaenzen`: behält die vorhandenen Tabellen und hängt die neuen Antworten an (B2, d4, d6 am 27.11.2026); schon eingelesene Antwortdateien gibt man dann mit `--verwerfen` an | `ingest/bre/phaseN/<phase>-bulk.tsv`, `-patch.tsv` |
| `13-lemma-apply.py` | Phase 1: setzt `@lemmaRef` aus Bulk und Patch | TEI |
| `14-pos-assign.py` | Phase 2: Wortart vom Lemma, bei genau einem Kandidaten direkt | TEI, `ingest/bre/phase2/pos-pending.tsv` |
| `15-apply.py` | Phase 2 und 3: setzt `@pos` oder `@ana` aus Bulk und Patch (`--phase pos\|sense`) | TEI |
| `16-sense-assign.py` | Phase 3: Sense bei genau einem Kandidaten direkt, sonst Kandidaten mit Konzeptlabels | TEI, `ingest/bre/phase3/sense-pending.tsv` |
| `18-corresp.py` | Phase 3: `@corresp` auf den Variantentyp, nur bei genau einem Treffer | TEI, `ingest/bre/phase3/corresp-mehrdeutig.tsv` |
| `20-pruefpaket.py` | Prüfpaket für Julia und KZW | `ingest/bre/pruefung/*.tsv` |
| `21-abdeckung.py` | Abdeckung je Zeuge und Attribut, prüft Referenzen, 19er-Tagset, `@ana` passend zu `@lemmaRef`, `<head>` unannotiert und das Schema; Exit 1 bei Fehlern | |
| `22-pruefseite.py` | HTML-Prüfseite zum Prüfpaket (aus `lemma-verdacht.tsv` die vorgesichteten Zeilen laut `vorschlaege-verdacht.tsv`, aus den drei anderen TSV je eine geschichtete Stichprobe, Seed 147), aus `pruefseite-template.html`; Exportformat im Docstring | `ingest/bre/pruefung/pruefseite.html` |
| `23-normdaten.py` | Setzt im Header der Zeugen in `ingest/bre/` an Ort und Stelle (alle 21 Dateien, auch die am 26.11.2026 geschriebenen B2, d4 und d6, sobald `23` läuft) Werk, Gattung und Autor (Entscheidung KZW, 24.11.2026), idempotent, `--trocken`. Rosenplüt steht, wo der `text_titel` der Segmentierung ihn nennt. Die Texte je Zeuge kommen aus den Kommentaren im Body. Schreibt außerdem die Werkeinträge als Fragment, validiert gegen das Authority-Schema | TEI (nur Header), `ingest/bre/works-eintraege.xml` |
| `24-lemma-korrektur.py` | Ersetzt `@lemmaRef` je `xml_id` nach `ingest/bre/pruefung/lemma-korrekturen.tsv` (Spalten `alt`, `neu`); überschreibt bewusst, aber nur wenn der Ist-Wert dem `alt` entspricht und `neu` in `lexicon.xml` steht. Entfernt `@pos`, `@ana`, `@corresp` des Tokens und dessen Zeilen in `phase2/pos-patch.tsv` und `phase3/sense-patch.tsv` (beide nur nach `xml_id` geschlüsselt, `15` würde sie sonst auf das neue Lemma anwenden). Danach müssen diese Tokens durch `14`, `15 --phase pos`, `16`, `15 --phase sense` und `18` neu laufen. `--trocken`, `--patches-behalten`, `--tabelle` (andere Tabelle, einmalige Nachkorrektur) | TEI (nur `<w>`), `phase2/pos-patch.tsv`, `phase3/sense-patch.tsv` |
| `bre_annot.py` | Gemeinsame Helfer der Phasen: Wortform, Normalisierung, Lexikon, Varianten, TSV | |
| `bre_common.py` | Zeugentabelle (Editionssigle, Wiki-Seite, MHDBDB-Sigle), Vorspann-Tabelle, Faltungstabelle, geprüfte Abweichungen zur Hauptseite, eingearbeitete Texte, Ansatz- und Schluss-Notizen, offene Segmentierung, ausgeschlossene Teile, API und Cache | |
| `bre_hauptseite.py` | Liest Liste und Übersichtstabelle der Hauptseite und vergleicht sie mit der Segmentierung | |
| `bre_wikitext.py` | Hilfsfunktionen für den Wikitext | |
| `druckfahnen-gate.py` | Druckfahnen-Gate ohne die Suite (Abschnitt „Druckfahnen“ unten): Exit 0 kein Wortlaut, 1 Treffer, 2 Prüfung nicht möglich. `--zaehlen` gibt nur Zahlen aus | |
| `druck_quelle.py` | Quellen und Scope des Gates (geschützte Texte, erlaubte Texte, zu prüfende Dateien), importierbar. Der Kern steht in `scripts/audit/wortlaut_gate.py` | |
| `test_bre.py` | Mini-Fixtures aus Cgm 713, konstruierte Fehlerfälle und Läufe gegen den Wiki-Cache (Sperre, B2, d4, d6, Hauptseite); ohne `temp/bre-wiki` bricht das Skript ab, vorher `00-fetch-wiki.py` | |

```bash
python -P -E scripts/ingest/bre/00-fetch-wiki.py --offline
python -P -E scripts/ingest/bre/01-segmentierung.py
python -P -E scripts/ingest/bre/02-convert-wiki-to-mhdbdb.py --zeuge B --trocken
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
python -P -E scripts/ingest/bre/22-pruefseite.py
python -P -E scripts/ingest/bre/23-normdaten.py --trocken
```

**Sperre in `02`** (Entscheidung Christian, 25.11.2026): Die annotierten Zeugen tragen die Annotation der Phasen 1 bis 3 und die Normdaten aus `23`, die rohe Konversion verwirft beides. Existiert die Zieldatei und läuft `02` nicht mit `--trocken`, ist das ein harter Fehler, und `--zeuge alle` prüft alle Ziele, bevor es die erste Datei schreibt. `--ueberschreiben` erlaubt das Ersetzen ausdrücklich. Zurück geht es zuerst mit `git restore ingest/bre/<SIGLE>.tei.xml`, denn die Zeugen sind committet. Für einen Stand, der nicht committet ist, führt der Weg über die Entscheidungen in `ingest/bre/phaseN/*.tsv`: danach `10`, `13`, `24 --patches-behalten` (setzt die Lemma-Korrekturen aus `pruefung/lemma-korrekturen.tsv` wieder ein, ohne die Patch-Tabellen anzufassen; ohne diesen Schritt bringen `10` und `13` das Altlemma zurück, ohne Fehlermeldung), `14`, `15 --phase pos`, `16`, `15 --phase sense`, `18` und `23` in dieser Reihenfolge neu fahren. Zeugen ohne Zieldatei schreibt `02` ohne Flag. Das gilt auch für B2, d4 und d6, die am 26.11.2026 so entstanden sind; ab dann ist auch ihre rohe Datei gesperrt.

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

- **Gepinnt:** `00-fetch-wiki.py` lädt die Hauptseite „Kategorie:Quelle Weingruß“ wie die anderen Seiten und führt sie im Manifest (Revision 31248 vom 26.11.2026, nach Silvans Korrektur der Liste von d4. Gegenüber Revision 31127 vom 11.11.2026 unterscheiden sich der Abschnitt „Überlieferung“ nur in der Reihenfolge zweier Zeilen von d4 und die Übersichtstabelle nur in den Spaltenköpfen, die jetzt Links sind, gemessen am 26.11.2026 mit `diff` der beiden Rohtexte).
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

Gemessen am 27.11.2026 mit `python -P -E scripts/ingest/bre/21-abdeckung.py --markdown`, Nenner ist je Zeile die Zahl der lexikalischen `<w>` (ohne die in `<head>`):

| Zeuge | Datei | lexikalische `<w>` | `@lemmaRef` | `@pos` | `@ana` | `@corresp` |
|---|---|--:|--:|--:|--:|--:|
| M1 | BRE_CGM216 | 93 | 84 (90.3 %) | 80 (86.0 %) | 81 (87.1 %) | 50 (53.8 %) |
| B | BRE_CGM713 | 1028 | 972 (94.6 %) | 946 (92.0 %) | 967 (94.1 %) | 535 (52.0 %) |
| S | BRE_COD13711 | 1504 | 1399 (93.0 %) | 1359 (90.4 %) | 1388 (92.3 %) | 751 (49.9 %) |
| H1 | BRE_CPG98 | 268 | 254 (94.8 %) | 248 (92.5 %) | 254 (94.8 %) | 152 (56.7 %) |
| d1 | BRE_D1 | 2742 | 2587 (94.3 %) | 2510 (91.5 %) | 2572 (93.8 %) | 1406 (51.3 %) |
| d2 | BRE_D2 | 2674 | 2505 (93.7 %) | 2462 (92.1 %) | 2497 (93.4 %) | 1396 (52.2 %) |
| d3 | BRE_D3 | 3115 | 2957 (94.9 %) | 2859 (91.8 %) | 2937 (94.3 %) | 1639 (52.6 %) |
| d4 | BRE_D4 | 672 | 641 (95.4 %) | 626 (93.2 %) | 639 (95.1 %) | 376 (56.0 %) |
| d5 | BRE_D5 | 2931 | 2756 (94.0 %) | 2709 (92.4 %) | 2746 (93.7 %) | 1635 (55.8 %) |
| d6 | BRE_D6 | 1746 | 1620 (92.8 %) | 1562 (89.5 %) | 1603 (91.8 %) | 956 (54.8 %) |
| U | BRE_GEORG1508 | 1702 | 1563 (91.8 %) | 1526 (89.7 %) | 1556 (91.4 %) | 931 (54.7 %) |
| R | BRE_GUELF296 | 475 | 447 (94.1 %) | 435 (91.6 %) | 445 (93.7 %) | 282 (59.4 %) |
| F | BRE_HS5339A | 3045 | 2833 (93.0 %) | 2789 (91.6 %) | 2821 (92.6 %) | 1560 (51.2 %) |
| N2 | BRE_MERKEL966 | 961 | 862 (89.7 %) | 798 (83.0 %) | 841 (87.5 %) | 508 (52.9 %) |
| B1 | BRE_MGQ2370 | 2443 | 2269 (92.9 %) | 2189 (89.6 %) | 2255 (92.3 %) | 1264 (51.7 %) |
| B2 | BRE_MGQ495 | 2498 | 2186 (87.5 %) | 2093 (83.8 %) | 2164 (86.6 %) | 1181 (47.3 %) |
| L | BRE_MS1590 | 648 | 605 (93.4 %) | 578 (89.2 %) | 601 (92.7 %) | 345 (53.2 %) |
| D | BRE_MSCRM50 | 1801 | 1691 (93.9 %) | 1651 (91.7 %) | 1676 (93.1 %) | 961 (53.4 %) |
| C | BRE_MSGER74 | 693 | 639 (92.2 %) | 607 (87.6 %) | 639 (92.2 %) | 367 (53.0 %) |
| W1 | BRE_OCT145 | 3085 | 2897 (93.9 %) | 2791 (90.5 %) | 2862 (92.8 %) | 1562 (50.6 %) |
| W | BRE_QUART564 | 1008 | 939 (93.2 %) | 919 (91.2 %) | 935 (92.8 %) | 536 (53.2 %) |
| gesamt |  | 35132 | 32706 (93.1 %) | 31737 (90.3 %) | 32479 (92.4 %) | 18393 (52.4 %) |

### Phase 1: Lemma

`python -P -E scripts/ingest/bre/10-lemma-assign.py --trocken` gibt aus:

- eindeutig: 20268 von 35132 (57,7 %), davon 530 nur dank der Faltung
- mehrdeutig: 12627 von 35132 (35,9 %) in 577 Formen, nach Stufen: bulk 12329 Wörter in 350 Formen (ab 3 Belegen), instance 142 in 71 Formen (2 Belege), hapax 156 in 156 Formen (zurückgestellt)
- ohne Treffer: 2237 von 35132 (6,4 %) in 1488 Formen, nach Häufigkeit in `ingest/bre/phase1/lemma-unmatched.tsv`

Die mehrdeutigen hat Claude Sonnet am Kontext entschieden (Abschnitt „LLM-Entscheidungen“ unten). Gesetzt sind 32706 `@lemmaRef` = 20268 eindeutig + 12438 entschieden (bulk-llm 10902, instance-llm 1536; Ausgabe von `13-lemma-apply.py`). Von den 12627 mehrdeutigen bleiben 189 offen: 156 Hapaxe und 33 abstain. Stand mit B2, d4 und d6 und nach den Lemma-Korrekturen vom 26.11.2026. Ein Lemma außerhalb der Kandidaten wird angenommen, wenn es im Lexikon steht, aber auf `low` gesetzt und mit „[außerhalb der Kandidaten]“ markiert, damit es im Prüfpaket landet. **Keine neuen Lemmata, keine Änderung an `lexicon.xml`.**

### Phase 2: Wortart

Die Kandidaten kommen aus dem Lemma, abgebildet auf das 19er-Set (`docs/POS-TAGSET.md`): `ART` wird `DET`, `GRA` fällt weg (§3: Graduierung ist kein eigenes Tag, `wzb-pos-assign.py` bildet es auf `ADV` ab, das widerspricht §3). Ein Lemma, das nur `GRA` trägt, bekommt `ADJ`. Steht `CNJ` unter den Kandidaten, sind auch `CCNJ` und `SCNJ` erlaubt.

`14-pos-assign.py` gibt 13928 Wörter mit genau einer Wortart aus, `15-apply.py --phase pos` von 18777 mehrdeutigen 17809 entschieden (bulk-llm 14828, instance-llm 2981), 397 abstain, 571 Hapaxe (17809 + 397 + 571 = 18777). Zusammen 31737 `@pos`. Stand mit B2, d4 und d6; ohne sie waren es 12081, 16163 mehrdeutig, 351 abstain und 27405.

Ein gültiger Tag, der nicht unter den Kandidaten des Lemmas steht, wird nicht geschrieben, sondern abstain mit dem Präfix „[verworfen: X ist kein Kandidat]“ in der Begründung (`12-entscheidungen.py`). **Befund:** 150 der 399 abstain betreffen *zuo* (`lemma_7770`), das im Lexikon nur `CNJ` und `PRP` hat. Als Gradwort („zu vil“) oder Verbpartikel wäre es `ADV`. Das ist eine Lücke im Lemma, kein Fehler der Zuweisung (Zählung: `decision_type` abstain in `phase2/pos-pending.tsv`, nach `lemma_id`).

### Phase 3: Bedeutung und Variantentyp

`16-sense-assign.py` und `15-apply.py --phase sense` geben aus: 23433 Wörter mit genau einem Sense direkt, von 9273 mehrdeutigen 9046 entschieden (bulk-llm 7206, instance-llm 1840), 97 abstain, 130 Hapaxe (9046 + 97 + 130 = 9273). Zusammen 32479 `@ana`. Stand mit B2, d4 und d6; ohne sie waren es 20272, 7973 mehrdeutig, 76 abstain und 28049. Kein Lemma ohne Sense. `@ana` steht nie ohne `@lemmaRef`, und der Sense gehört immer zum Lemma (`21-abdeckung.py`).

**Befund: Die Sense-abstains finden falsche Lemmata aus Phase 1.** Passt keine Bedeutung des Lemmas, ist meist das Lemma falsch. 190 der 233 abstain haben ihr Lemma aus dem Auto-Match: die Form steht in `variants.xml` nur unter einem Lemma und hat es ohne Kontextprüfung bekommen, ist hier aber ein anderes Wort, etwa „dorffen“ (Dörfer) unter *durfen* oder „imm“ (ihm) unter *ime*. Die übrigen 43 haben ihr Lemma aus der LLM-Entscheidung (39 bulk, 4 instance). Alle 233 stehen in `ingest/bre/pruefung/lemma-verdacht.tsv` (Ausgabe von `20-pruefpaket.py`). Die Wortart dieser Wörter ist mit dem Lemma vererbt und damit ebenso verdächtig. Am 26.11.2026 sind 160 davon korrigiert worden (`pruefung/lemma-korrekturen.tsv`, `24-lemma-korrektur.py`); Phase 2 und 3 sind für diese Tokens danach neu gelaufen, 12 Tokens der Verdachtsliste bleiben offen.

**`@corresp` nur bei genau einem Treffer** (Algorithmus wie `wzb-sense-apply.py`): Typen aus `variants.xml`, deren Form normalisiert gleich der Wortform ist, die zum Lemma gehören und im `@ana` des Senses stehen. `18-corresp.py` gibt aus: 18393 von 32479 Wörtern mit `@ana` gesetzt, 4533 ohne Typ, 9534 mit mehreren Typen (`phase3/corresp-mehrdeutig.tsv`), 19 mit `<supplied>` ausgenommen (18393 + 4533 + 9534 + 19 = 32479).

- **Welche Form zählt bei `<expan>`: die aufgelöste.** Die Abkürzungsgraphie ist nicht überliefert: das Wiki schreibt nur die Auflösung in Klammern, und Stufe 0 macht daraus `<expan>` ohne `<abbr>`. Eine andere Form als die aufgelöste gibt es im TEI nicht, und Index und Suche lesen ebenfalls itertext. 1211 der gesetzten `@corresp` stehen auf einem Wort mit `<expan>`.
- **Wörter mit `<supplied>` bekommen keinen Typ:** die ergänzten Buchstaben stehen nicht in der Handschrift, die Form wäre eine des Herausgebers.
- **Befund: Die 8211 mehrdeutigen sind fast alle Zirkumflex-Paare.** „Nu“ trifft normalisiert *nu* und *nû*, „du“ trifft *du* und *dû*. Ein exakter Vergleich der Form (klein geschrieben, gefaltet) vor dem normalisierten würde, gemessen vor den Korrekturen vom 26.11.2026 (damals 8211 mehrdeutige), 8166 der 8211 auflösen, 45 blieben (gemessen mit einem Skript im Scratchpad, nicht im Repo). Das ist eine Änderung am Algorithmus, die auch WZB beträfe, und ist deshalb nicht umgesetzt.

### LLM-Entscheidungen

- **Modell:** Claude Sonnet 5.5 als Subagent, Batches zu etwa 50 Zeilen. Jede Zeile trägt `decision_type` (`bulk-llm`, `instance-llm`, `abstain`), `confidence` (`high`, `medium`, `low`) und `reviewer` (`llm:claude-sonnet-5-5`). `abstain` ist gültig und wird nicht geschrieben.
- **Stufen:** Gruppen ab 3 Belegen werden als Ganzes entschieden (bulk) mit Ausnahmen je Beleg. Meldet das Modell `SPLIT`, weil die Belege zu verschiedenen Werten gehören, wird jedes Wort der Gruppe einzeln entschieden. Gruppen mit 2 Belegen werden je Wort entschieden, Hapaxe zurückgestellt. Gruppe ist in Phase 1 die normalisierte Form, in Phase 2 Lemma und Form, in Phase 3 das Lemma.
- **Kontext:** ±5 Wörter in der Eingabe. Die Synopse der Einzeltextseite im Wiki-Cache durfte das Modell bei Unsicherheit nachlesen, nach den eigenen Berichten hat es das selten getan. **Die Druckfahnen sind nicht benutzt worden**, weder als Kontext noch für Begründungen.
- **B2, d4, d6 (27.11.2026):** die Zeugen laufen durch dieselbe Folge wie die ersten 18, die Entscheidungen der 18 bleiben. Dazu wurden alle Attribute entfernt und `10`, `13`, `24 --patches-behalten`, `14`, `15 --phase pos`, `16`, `15 --phase sense`, `18` neu gefahren; die offenen Gruppen und Tokens haben Sonnet-Subagenten nacheinander nach den Anleitungen entschieden (`11-batches.py --offen`, `12-entscheidungen.py --ergaenzen`), Kleinstmengen die Session selbst. Bei den ersten 18 Zeugen sind dadurch 62 Tokens mit Attributen hinzugekommen (gemessen per Token-Vergleich gegen den Stand davor: `@lemmaRef` 14, `@pos` 50, `@ana` 24, `@corresp` 18), alle neu gesetzt, kein vorhandener Wert hat sich geändert; Ursache sind Gruppen, die durch die neuen Texte größer wurden (Hapax-Gruppen, die jetzt entschieden werden) und neue Lemmata. Die Abstains der Bedeutungsphase in B2, d4 und d6 zeigten falsche Lemmata; 17 davon sind nach schon getroffenen Entscheidungen in anderen Zeugen korrigiert (`pruefung/lemma-korrekturen.tsv`, Quelle „Session, Parallelstelle“), der Rest (zum Beispiel `gerenn` für gern, `armenn`, `sanden`) bleibt für die abschließende Prüfung. Ein neues Prüfpaket für B2, d4 und d6 gibt es noch nicht: `20-pruefpaket.py` würde das eingefrorene Paket der ersten 18 Zeugen überschreiben, auf dessen `nr` `lemma-korrekturen.tsv` verweist.
- **Kontrolle:** der Orchestrator (Claude Opus) hat aus Batches aller drei Phasen Stichproben am Kontext nachgesehen, verworfen werden musste keine Batch. Nachgebessert wurde einmal die Anweisung (Phase 1: „im“ = in dem), die zwei betroffenen Batches sind neu gerechnet. Werte außerhalb der Kandidaten fängt `12-entscheidungen.py` mechanisch ab (oben).
- **Die Anweisungen an das Modell** stehen in [`anleitungen/`](anleitungen/). Die Rohantworten liegen in `temp/` und sind nicht im Repository, die daraus gesammelten Entscheidungen in `ingest/bre/phaseN/*-bulk.tsv` und `*-patch.tsv` schon.

### Druckfahnen

Kein Wortlaut aus Text, Übersetzung oder Kommentar der Hirzel-Druckfassung steht im Repository. `test_bre.py` prüft das mechanisch, ebenso `druckfahnen-gate.py` ohne die Suite (Code in `druck_quelle.py` und `scripts/audit/wortlaut_gate.py`, #743). Der Ort der Quellen ist mit `BRE_DRUCK_QUELLEN=<Ordner>` setzbar (Ordner mit der PDF und `docling/`, ohne Fallback, wenn die Variable gesetzt und der Ordner unvollständig ist), sonst `sources/weingruesse` im Repo, dann im Main Worktree. Quelle ist der Text der Druckfahnen-PDF, den `pdftotext` auf stdout liefert (nie als Datei abgelegt, Silbentrennung am Zeilenende zusammengezogen), dazu Silvans Word-Steckbriefe von 2022 (`sources/weingruesse/docling/`), die der Kickoff zum selben Material zählt. Jede Folge von sechs Wörtern daraus, die nicht auch im Wiki oder im TEI-Wortlaut vorkommt, darf in keiner Datei unter `ingest/bre/` und `scripts/ingest/bre/` stehen (TSV je Feld) und weder in einer Commit Message noch in den hinzugefügten Zeilen eines Commits seit dem merge-base mit `origin/main` (auch in Dateien außerhalb dieser Ordner). Ist der merge-base leer, scheitert ein git-Call oder weicht die Zahl der gelesenen hinzugefügten Zeilen eines Commits von `git log --numstat` ab, ist die Prüfung nicht möglich und schlägt fehl. Das Diff-Format ist im Call festgelegt, eine Nutzer-Config wie `diff.noprefix` oder `color.ui=always` ändert daran nichts. Ein Merge-Commit zählt mit dem, was er gegenüber seinem ersten Parent hinzufügt. Weitere Texte vor dem Absenden (PR-Body, Issue-Kommentar) prüft `BRE_DRUCK_PRUEFE=<datei>[;<datei>]`. Fehlt die PDF, `pdftotext`, die Steckbriefe oder der Wiki-Cache, schlägt der Test fehl, statt still zu bestehen. Nicht erfasst sind Folgen unter sechs Wörtern und Ziffern.

Bis zur ersten Review-Runde las der Test nur die Steckbriefe und hielt sie für die Druckfahnen. Gefunden hatte er damals ein Steckbrief-Zitat in der Spalte `abweichung_steckbrief_2022` von `ingest/bre/zeugen.tsv` (Zeile C, seit #654 auf `main`), das in diesem Branch umformuliert ist. Der Test mit der PDF fand dann eine Wendung der Druckfahnen in der Spalte `ort` derselben Datei (Zeile d4, ebenfalls seit #654), jetzt in eigenen Worten. Beide stehen weiter in der Git-Geschichte von `main`. Gegenprobe am 17.11.2026: eine wörtliche Zeile aus dem PDF-Text und eine Folge über eine Silbentrennung, beide über `BRE_DRUCK_PRUEFE` eingespeist, machen den Test rot.

## Offene Entscheidungen

- **Schema: entschieden (Weg 1, KZW am 11.11.2026).** `<w>` erlaubt seit dem 11.11.2026 zusätzlich `<expan>`, `<supplied>`, `<add>` und `<pb>` (`schema/mhdbdb.rnc`, `.rng` neu erzeugt). Die Transkriptionen tragen im Wort Abkürzungsauflösungen, Ergänzungen, Nachträge und in zwei Fällen einen Seitenwechsel: bei Cgm 713 über eine Worttrennung („schen-“ / „ken“), bei d4 als Blattmarke mitten im Wort („wein[9]reben“). Mit dem erweiterten Schema validieren alle 21 Zeugen (`02 --zeuge alle --trocken`, gemessen 13.11.2026); vorher validierte nur d2. Die Leseansicht zeigt die Auszeichnung im Wort nicht, sie ist nicht angefasst.
- **Siglen, Werk, Gattung und Autor: entschieden (KZW, 24.11.2026, #147).** Siglen `BRE_<Signatur>` und `BRE_D1` bis `BRE_D6`. Ein Werk je Zeuge, Handschriften „Weingrüße (München, BSB, Cgm 713)“ mit der Kurzform der Aufbewahrung aus `AUFBEWAHRUNG_KURZ` in `bre_common.py` (fehlt ein Wert, bricht `23` ab), Drucke „Weingrüße (Druck, VD16 R 439)“. Gattung `genre_315cf46f` (Weingruß). Autor Hans Rosenplüt (`person_907`), wo das Brevitas-Wiki ihn nennt, sonst anonym, gemischte Zeugen tragen beide, Gengenbach nie. `23-normdaten.py` setzt das im Header, die Werkeinträge liegen als Fragment in `ingest/bre/works-eintraege.xml` und gehen mit den Zeugen nach `authority-files/works.xml`, nicht vorher. Auch `titleStmt/title` ist der Werktitel, `msName` behält die Beschreibung mit Blattangabe beziehungsweise Druckdaten. Die Kurzform ist nötig, weil die lange Form (Aufbewahrung und Signatur aus `zeugen.tsv`) bei C wörtlich in den Druckfahnen steht und das Druckfahnen-Gate in `test_bre.py` sie sonst meldet.
- **Sprachstufe** steht als `TBD` im Header. Die Sprachstufe entscheidet #118.
- **Segmentierung (Punkt 5 in #147).** Silvans Antwort (12.11.2026) benennt die Hauptseite als Grundlage für die Werkzuordnung, die Synopsen sind ergänzend (Abschnitt „Werkzuordnung“ oben). Die Abweichungen zwischen beiden stehen in `ingest/bre/hauptseite-abgleich.tsv`, Die drei offenen Fälle sind seit Silvans Antwort vom 26.11.2026 entschieden: B2 (Fehlansatz) bleibt ein eigener kurzer Abschnitt mit Notiz `ANSATZ_NOTIZ`, bei d4 war die Liste der Hauptseite falsch und ist korrigiert (Revision 31248, keine Abweichung mehr), und die drei in Klammern gesetzten Texte von d6 (Allerliebster Trunck, Allerliebster Trost, Ein Kron) sind in den Weinsegen Edles Abkülen eingearbeitet (`EINGEARBEITET`: kein eigener Abschnitt, Anfang je durch eine `<note type="editorial">` markiert). Markiert sind nur die drei Texte, deren Anfang eine Synopse der Einzeltextseiten als ersten Vers führt; die übrigen drei Klammertexte der Hauptseite für d6 (Lieber Rebenknecht, Libe Rebenprü, Süsser Geschmack) haben dort keine Zeile für d6, ihre Ausschnitte stehen unmarkiert im Text. Das Wort „ENDE“ und der vierversige Schlussreim von d6 gehören laut Hauptseite zu keinem Text: eine Notiz davor (`SCHLUSS`) grenzt sie ab, die Zeilen bleiben im letzten Abschnitt (wie „S R F“ in d3 und d5, dafür gibt es noch keinen eigenen Mechanismus).
- **Epoche: entschieden.** Der zweite Teil der Weingrüße in D (Bl. 217r–221v) stammt laut Druckfahnen (Kapitel IV) aus dem 17. Jahrhundert und liegt außerhalb des Korpusumfangs (Texte vor 1600, #263). `02` schneidet ihn ab (`TEIL_AUSGESCHLOSSEN` in `bre_common.py`), nachdem die Segmentierung den ganzen Zeugen gesehen hat. Der Grund steht im Header von `BRE_MSCRM50.tei.xml` und als Kommentar an der Schnittstelle. Tests in `test_bre.py`: ein Text bleibt, einer entfällt, die Zeilenbilanz geht auf, der Grund steht im Header.

## Warum `ingest/bre/` und nicht `tei/`

Solange die Header Platzhalter tragen, würde `build-corpus-index.py` sie aus `tei/` mitsamt den Platzhaltern indizieren, und die Cross-Ref-Prüfung liefe ins Leere. Dieselbe Begründung wie bei ARI, siehe [`ingest/ari/README.md`](../../../ingest/ari/README.md).

## Für die Erratum-Liste an Silvan

- Druckfahnen, Kapitel V.3: N² ist dort ein Jahrhundert früher datiert (1424–1426), die Zeugenliste in Kapitel IV (S. XIII) und sein Steckbrief von 2022 sagen 1524–1526.
- Druckfahnen, S. XIV: Schreibfehler im Ortsnamen Weimar bei W¹.
- Wiki: „Weingruß Neczen Gumen“, erster Vers in W¹, Synopse „guͦmen“, Transkription „gůmen“.
- Wiki: „Vorspruch Weingruß“, Überschrift in d5, Synopse „Guͦten“, Transkription „Gůten“.
