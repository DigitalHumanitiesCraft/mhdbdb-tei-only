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
| `00-fetch-wiki.py` | Lädt Dokumentationsseite, die 21 Transkriptionen und die Einzeltextseiten in den Cache `temp/bre-wiki/`. Mit Manifest gepinnt per Revisions-ID, sha256-Abweichung ist ein harter Fehler. `--offline`: nur Cache. `--neu`: Manifest aus den aktuellen Revisionen | `ingest/bre/revisionen.tsv` |
| `01-segmentierung.py` | Liest aus jeder Einzeltextseite die Infobox (Blattangabe je Zeuge) und die Synopse (erster Vers und Überschrift je Zeuge) | `ingest/bre/segmentierung.tsv` |
| `02-convert-wiki-to-mhdbdb.py` | Konvertiert einen Zeugen nach MHDBDB-TEI und validiert gegen `schema/mhdbdb.rng`. `--zeuge alle --trocken` fährt alle 21 ohne Ausgabedatei | `ingest/bre/<SIGLE>.tei.xml` |
| `bre_common.py` | Zeugentabelle (Editionssigle, Wiki-Seite, MHDBDB-Sigle), Vorspann-Tabelle, Faltungstabelle, API und Cache | |
| `bre_wikitext.py` | Hilfsfunktionen für den Wikitext | |
| `test_bre.py` | Mini-Fixtures aus Cgm 713 und konstruierte Fehlerfälle | |

```bash
python -P -E scripts/ingest/bre/00-fetch-wiki.py --offline
python -P -E scripts/ingest/bre/01-segmentierung.py
python -P -E scripts/ingest/bre/02-convert-wiki-to-mhdbdb.py --zeuge B
python -P -E scripts/ingest/bre/02-convert-wiki-to-mhdbdb.py --zeuge alle --trocken
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
- **Fragment** (R): drei Verse vor dem ersten Text der Synopse, keiner Einzeltextseite zugeordnet. Eigenes `<div>`, ohne Aussage darüber, ob der Anfang in der Handschrift fehlt.

Eine **Faltungstabelle** gleicht beim Vergleich, nie in der Ausgabe, eine Zeichenabweichung zwischen Synopse und Transkription aus: „ů“ gegen „uͦ“ (u mit U+0366). Sie greift zweimal, beim ersten Vers von „Weingruß Neczen Gumen“ in W¹ (Zeile 331 der Wikiseite) und bei der Kopfzeile „Gůten wein gruͤsz ich“ in d5 (Zeile 10). Das Skript gibt jede Anwendung aus.

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

- **Schema (für KZW, nach dem Muster PD-001).** `<w>` erlaubt nur Text und `<hi>`. Die Transkriptionen tragen im Wort Abkürzungsauflösungen (`<expan>`), Ergänzungen (`<supplied>`), Nachträge (`<add>`) und in zwei Fällen einen Seitenwechsel (`<pb>`): bei Cgm 713 über eine Worttrennung („schen-“ / „ken“), bei d4 als Blattmarke mitten im Wort („wein[9]reben“). Nach „Daten vor Schema“ bleibt das stehen, statt wegtransformiert zu werden. Die Validierung zählt es je Zeuge aus. Zu entscheiden ist, ob das Inhaltsmodell von `<w>` erweitert wird oder ob die Auszeichnung im Wort entfällt.
- **Siglen.** `BRE_<Signatur>` für die Handschriften und `BRE_D1` bis `BRE_D6` für die Drucke folgen dem Vorschlag vom 10.07.2026 in #147, bestätigt sind sie nicht.
- **Werk, Gattung, Sprachstufe** stehen als `work_TBD`, `genre_TBD` und `TBD` im Header. Die Sprachstufe entscheidet #118.
- **Segmentierung (Punkt 5 in #147).** Silvan hat die Frage noch nicht beantwortet. Die Synopsen tragen sie bis dahin.
- **Epoche.** Der zweite Teil der Weingrüße in D (Bl. 217r–221v) stammt laut Druckfahnen aus dem 17. Jahrhundert und liegt außerhalb des Korpusumfangs. Er ist in der Transkription Teil B und steht damit als `<div n="B">` für sich, `02` konvertiert D aber heute noch vollständig.

## Warum `ingest/bre/` und nicht `tei/`

Solange die Header Platzhalter tragen, würde `build-corpus-index.py` sie aus `tei/` mitsamt den Platzhaltern indizieren, und die Cross-Ref-Prüfung liefe ins Leere. Dieselbe Begründung wie bei ARI, siehe [`ingest/ari/README.md`](../../../ingest/ari/README.md).

## Für die Erratum-Liste an Silvan

- Druckfahnen, Kapitel V.3: N² „zwischen 1424 und 1426“, die Zeugenliste in Kapitel IV (S. XIII) und sein Steckbrief von 2022 sagen 1524–1526.
- Druckfahnen, S. XIV: „Weinmar“ statt Weimar bei W¹.
- Wiki: „Weingruß Neczen Gumen“, erster Vers in W¹, Synopse „guͦmen“, Transkription „gůmen“.
- Wiki: „Vorspruch Weingruß“, Überschrift in d5, Synopse „Guͦten“, Transkription „Gůten“.
