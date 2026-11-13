# BRE: Weingrüße (Brevitas-Edition, Silvan Wagner)

Ingest der Weingrüße aus der Hybridedition von Silvan Wagner (Issue [#147](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/147)): 21 Überlieferungszeugen, 15 Handschriften und 6 Drucke, transkribiert im [Brevitas-Wiki](https://wiki.brevitas.org/wiki/Dokumentation_Edition_Weingr%C3%BC%C3%9Fe). Aufgenommen wird die Überlieferung je Zeuge, nicht der Editionstext (Silvan, Mail vom 23.10.2026).

> **Stand 2026-11-03: nur Stufe 0.** Die Konversion läuft für alle 21 Zeugen durch, geschrieben ist bisher nur der Dogfood-Zeuge Cgm 713 (`ingest/bre/BRE_CGM713.tei.xml`). Phase 1 bis 3 folgen nach dem Muster in [`docs/DATA-MODEL.md` → Ingest procedure](../../../docs/DATA-MODEL.md#ingest-procedure-taking-in-new-texts).

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
| `02-convert-wiki-to-mhdbdb.py` | Konvertiert einen Zeugen nach MHDBDB-TEI und validiert gegen `schema/mhdbdb.rng`. `--zeuge alle --trocken` fährt alle 21 ohne Ausgabedatei | `ingest/bre/<SIGLE>.tei.xml` |
| `03-hauptseite-abgleich.py` | Gleicht die Werkzuordnung je Zeuge mit der Überlieferungsbeschreibung der Hauptseite ab (Abschnitt „Werkzuordnung“ unten). Exit 2, wenn eine Abweichung nicht in `ABWEICHUNG_ERKLAERT` steht | `ingest/bre/hauptseite-abgleich.tsv` |
| `bre_common.py` | Zeugentabelle (Editionssigle, Wiki-Seite, MHDBDB-Sigle), Vorspann-Tabelle, Faltungstabelle, geprüfte Abweichungen zur Hauptseite, API und Cache | |
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
```

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
- **Abgleich:** `03-hauptseite-abgleich.py` vergleicht je Zeuge die Texte der Transkription mit der Liste (Titel, Menge, Reihenfolge) und schreibt die Abweichungen nach `ingest/bre/hauptseite-abgleich.tsv`. `02` ruft denselben Abgleich auf: eine Abweichung, die nicht in `ABWEICHUNG_ERKLAERT` (`bre_common.py`) mit Begründung steht, bricht die Konversion ab. Der Eintrag dort erklärt oder hält eine offene Frage fest, er korrigiert nichts.
- **Stand 13.11.2026:** 15 von 21 Zeugen stimmen mit der Liste überein (Titel, Menge, Reihenfolge), R nach der Korrektur oben. Die übrigen sechs (B2, N², W¹, d4, d5, d6) stehen in `hauptseite-abgleich.tsv` mit Befund. Die Liste der Hauptseite ist selbst nicht widerspruchsfrei: sie weicht bei d4 (Reihenfolge) und d5 (zwei Texte fehlen) von der Übersichtstabelle derselben Seite ab, und in B2 nennt der Satz 19 Weingrüße bei 18 Einträgen.

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

## Offene Entscheidungen

- **Schema: entschieden (Weg 1, KZW am 11.11.2026).** `<w>` erlaubt seit dem 11.11.2026 zusätzlich `<expan>`, `<supplied>`, `<add>` und `<pb>` (`schema/mhdbdb.rnc`, `.rng` neu erzeugt). Die Transkriptionen tragen im Wort Abkürzungsauflösungen, Ergänzungen, Nachträge und in zwei Fällen einen Seitenwechsel: bei Cgm 713 über eine Worttrennung („schen-“ / „ken“), bei d4 als Blattmarke mitten im Wort („wein[9]reben“). Mit dem erweiterten Schema validieren alle 21 Zeugen (`02 --zeuge alle --trocken`, gemessen 13.11.2026); vorher validierte nur d2. Die Leseansicht zeigt die Auszeichnung im Wort nicht, sie ist nicht angefasst.
- **Siglen.** `BRE_<Signatur>` für die Handschriften und `BRE_D1` bis `BRE_D6` für die Drucke folgen dem Vorschlag vom 10.07.2026 in #147, bestätigt sind sie nicht.
- **Werk, Gattung, Sprachstufe** stehen als `work_TBD`, `genre_TBD` und `TBD` im Header. Die Sprachstufe entscheidet #118.
- **Segmentierung (Punkt 5 in #147).** Silvans Antwort (12.11.2026) benennt die Hauptseite als Grundlage für die Werkzuordnung, die Synopsen sind ergänzend (Abschnitt „Werkzuordnung“ oben). Die Abweichungen zwischen beiden stehen in `ingest/bre/hauptseite-abgleich.tsv`, offene Fälle sind dort als „offen“ vermerkt: B2 (Fehlansatz), d4 (Reihenfolge), d6 (in Klammern gesetzte Texte als eigene Abschnitte).
- **Epoche.** Der zweite Teil der Weingrüße in D (Bl. 217r–221v) stammt laut Druckfahnen aus dem 17. Jahrhundert und liegt außerhalb des Korpusumfangs. Er ist in der Transkription Teil B und steht damit als `<div n="B">` für sich, `02` konvertiert D aber heute noch vollständig.

## Warum `ingest/bre/` und nicht `tei/`

Solange die Header Platzhalter tragen, würde `build-corpus-index.py` sie aus `tei/` mitsamt den Platzhaltern indizieren, und die Cross-Ref-Prüfung liefe ins Leere. Dieselbe Begründung wie bei ARI, siehe [`ingest/ari/README.md`](../../../ingest/ari/README.md).

## Für die Erratum-Liste an Silvan

- Druckfahnen, Kapitel V.3: N² „zwischen 1424 und 1426“, die Zeugenliste in Kapitel IV (S. XIII) und sein Steckbrief von 2022 sagen 1524–1526.
- Druckfahnen, S. XIV: „Weinmar“ statt Weimar bei W¹.
- Wiki: „Weingruß Neczen Gumen“, erster Vers in W¹, Synopse „guͦmen“, Transkription „gůmen“.
- Wiki: „Vorspruch Weingruß“, Überschrift in d5, Synopse „Guͦten“, Transkription „Gůten“.
