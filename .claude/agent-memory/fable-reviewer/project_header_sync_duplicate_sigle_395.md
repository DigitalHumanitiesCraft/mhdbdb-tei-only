---
name: header-sync-duplicate-sigle-395
description: sync_tei_headers.py --works keyt nach Sigle, letzter Eintrag gewinnt; TRO hat zwei bibl in works.xml (work_69 Konrad, work_c7da236c Fortsetzung), der Sync setzt den Header auf die Fortsetzung zurueck. Plus Umgebungsfallen der Cloud-Session (python3.13 fuer lxml, kein gh, api.github.com 403, Shallow-Clone)
metadata:
  type: project
---

Review-Runde 1 zu e8cb256 (Zweig `claude/agents-setup-network-check-08f1ri`, #395 Punkt 3) am 2026-09-07.

**Die Falle, die der Diff nicht zeigt:** `scripts/sync/sync_tei_headers.py` (`WorksSyncer.load_authority_data`, Zeile 181 bis 241) baut `sigle_to_work[sigle] = work_data` ohne Kollisionspruefung. `authority-files/works.xml` hat 584 `bibl`, 669 Sigle-Eintraege und 668 verschiedene Siglen; TRO ist die einzige Sigle mit zwei Eintraegen (`work_69` Konrad, hc 212 / GND 4285313-8 / Q66770444, und `work_c7da236c-...` Fortsetzung, hc 929 / GND 1181164893, kein Wikidata). Der zweite steht spaeter in der Datei und gewinnt: `d['TRO']['work_id'] == 'work_c7da236c-...'`. `update_tei_header` (Zeile 265 ff.) loescht alle Nicht-Sigle-`idno` im `msIdentifier` und schreibt hc/GND/wikidata aus dem Mapping neu; `@corresp` fasst es nicht an. Auf einer Kopie simuliert: ein Header mit 212 / 4285313-8 / Q66770444 wird zu 929 / 1181164893, Wikidata weg, corresp bleibt `work_69`. DATA-MODEL Authority-Checkliste Schritt 1 schreibt genau diesen Lauf fuer jede works.xml-Aenderung vor.

Kein Gate haelt Header-`idno` gegen works.xml: `check-authority-cross-refs.py` und `audit-tei-corpus.py` greppen weder `handschriftencensus` noch `msIdentifier` (gemessen). Der Reader (`tei-text-reader.js` ab Zeile 332) nimmt hc/GND/wikidata aus dem Work-Objekt des Authority-Index, nicht aus dem Header; Header-`idno` sind also nirgends nutzersichtbar und in keinem Build (`build-corpus-index.py` liest nur `idno[@type="sigle"]` und `msIdentifier/@corresp`, Zeile 94 und 130).

Reihenfolge-Konvention im `msIdentifier`, ueber alle 667 Dateien gemessen: sigle, handschriftencensus, GND, wikidata, [mwb-sigle], msName+. Formate im Header: nackte Ids (713 GND, 790 wikidata `Q...`, 355 hc), in works.xml URLs.

**Umgebung der Cloud-Session (07.09.2026):** `python`/`python3` sind 3.11 ohne lxml, `python3.13` hat lxml 6.0.2. Kein `gh`; `api.github.com` antwortet 403 („GitHub access is not enabled for this session"), `github.com`-Issue-Seiten gehen per curl/WebFetch (Status ueber `"state":"OPEN"` im HTML greppen). Klon ist shallow (59 Commits, aeltester 4458686 vom 24.08.), `git log -S` findet deshalb keine Herkunft vor diesem Datum. de.wikipedia-API rate-limitet nach wenigen Aufrufen.

**Why:** Der Aufrufer hatte die #397-Frage selbst gestellt und `works.xml` gefunden, aber nur nach *Pruefungen* gesucht, nicht nach *Schreibern*. Der Sync ist kein Gate und stand deshalb nicht auf seiner Liste.

**How to apply:** Bei jedem Diff an `msIdentifier`-Identifiern oder an works.xml-Siglen: `WorksSyncer.load_authority_data()` in-process laden und den Eintrag der betroffenen Sigle drucken; bei Doppel-Siglen `update_tei_header` auf einer Scratchpad-Kopie laufen lassen. Verwandt: [[rebase-review-data-prs]] (Messen statt Diff lesen bei Daten-PRs).

**Runde 2 (75887c3, 07.09.2026):** Der Fix loest ueber `@corresp` auf, aber `self.work_id_to_work[work_id] = work_data` wird pro *Sigle* geschrieben, und `work_data['biblStructs']` ist nach `@key=sigle` gefiltert. Bei 70 von 584 Werken mit mehreren Siglen (z.B. work_205 DES2: 1 biblStruct, GSP: 2) haelt der Eintrag den Datensatz der *letzten* Sigle. Heute folgenlos (work_69 hat nur TRO), bricht bei der naechsten Doppelsigle an einem Mehrfach-Siglen-Werk. Muster: eine per-Sigle-Struktur unter einem per-Werk-Schluessel ablegen.

**Verfahren alt/neu-Lauf ohne Schreiben ins Repo:** `git show <alt>:scripts/sync/sync_tei_headers.py > scratch/old_sync.py`, dann beide Fassungen per `importlib.util.spec_from_file_location` laden (vorher `sys.path.insert(0, '<repo>/scripts')` fuer `corpus_files`) und `WorksSyncer(works_xml, tei_dir=<Kopie>)` mit Kopien von `tei/` im Scratchpad instanziieren. `diff -rq` der beiden Kopien liefert die Differenzmenge; der Vergleich gegen das Repo ist wegen `remove_blank_text` + `pretty_print` wertlos (667 Dateien differieren im Layout).

**Runde 3 (0c9b8e5, 07.09.2026):** Schluessel (work_id, sigle), 669 Eintraege bei 668 Siglen. In-process-Gegenprobe alt/neu ueber 667 Dateien ohne Korpuskopie: beide Fassungen auf je einen frisch geparsten Baum anwenden und `etree.tostring(pretty_print=True)` vergleichen, 0 Differenzen; das spart die 1,4 GB Kopie. Der neue else-Zweig (corresp-Werk fuehrt die Sigle nicht) auf mutierter DES2-Kopie ausgefuehrt: warnt, schreibt Sigle-Aufloesung, laesst das falsche @corresp stehen, zaehlt als updated, Exit 0. Fehlt das Ablage-Attribut, faengt `_update_single_tei` den AttributeError als ERROR-Log pro Datei ab, kein Abbruch. Issue-Kommentare: api.github.com 403, die HTML-Seite meldet 0 Kommentare auch wenn welche existieren (clientseitig gerendert), also nicht messbar.

**Runde 4 und 5, vom CI-Bot (07.09.2026):** die Zahl in diesem Eintrag stand
zuerst auf "584 bibl auf 583 Siglen" und war falsch. Herkunft: je `bibl` wurde
nur die ERSTE Sigle gelesen (`find` statt `findall`), 583 ist damit die Zahl der
verschiedenen ersten Siglen und bedeutet nichts. Richtig sind 584 `bibl`, 669
Sigle-Eintraege, 668 verschiedene Siglen. **Die Lehre ist nicht die Zahl:**
dieselbe Methode haette eine Doppelsigle uebersehen, die nicht an erster Stelle
steht, und genau darauf steht die Reichweitenaussage des Fixes. Mit `findall`
nachgemessen bleibt TRO die einzige. Wer hier nach Siglen zaehlt, nimmt
`findall` und pruefe die Zahl gegen eine zweite Groesse aus demselben Text: der
Bot hat den Fehler nicht an der Zahl gesehen, sondern an ihrem Widerspruch zu
den 70 Mehrfach-Siglen-Werken aus demselben PR.

Zwei Messungen aus derselben Runde, damit sie niemand wiederholen muss:
`update_tei_header` loescht in Abschnitt 2 alle `biblStruct` und schreibt
`data['biblStructs']` neu; waere die Liste leer, bliebe `listBibl` leer,
waehrend die Datei wegen Abschnitt 1 trotzdem geschrieben wird. Gemessen:
**0 von 669 Paaren (work_id, sigle) haben eine leere biblStruct-Liste**, das
Risiko ist heute rein hypothetisch. Und: eine Zahl in diesem Verzeichnis ist
Eingabe fuer den naechsten Lauf, nicht Prosa. Ein Eintrag, der sich selbst
widerspricht, liefert die Grundgesamtheit fuer die naechste Aussage.

**Runde 1 zu #399 (chirurgischer Schreiber + `--check`, ungestagt, 07.09.2026):**
Der alte lxml-Pfad (`update_tei_header`, `idno[@type!="sigle"]` loeschen) bleibt
ueber `--works --bibl-struct` UND ueber `--all` erreichbar (main: `nur_works`
ist bei `--all` False). Auf voller Korpuskopie gemessen: 52 s, alle 667
Dateien neu serialisiert (1.432.472.114 -> 1.430.556.264 Bytes), **alle 19
`mwb-sigle` geloescht** (0 von 667 danach), und die listBibl aus works.xml
ueberschrieben. Die 127 listBibl-Abweichungen sind NICHT reine Reihenfolge:
116 Reihenfolge, 6 zusaetzlich Whitespace im Text, 5 Inhalt (AK: biblScope +
note nur im Header; WZB: 3 editor, 2 publisher, 4 note nur im Header; FR3:
ref/@target; HZ, LUU: xml:id zwischen zwei biblStruct vertauscht). Der alte
Pfad verliert also Header-Information, er sortiert nicht nur um.
Der `--check` (iterparse bis msIdentifier, 0,6 s) prueft nur Inhalt der drei
gespiegelten Typen; Reihenfolge, mwb-sigle, Dateien ohne msIdentifier und
Dateien, die works.xml nicht kennt, faerben ihn nie rot (heute 667/667
geprueft). Regex-Schreiber: Entfern-Muster verlangt `\n<indent><idno type="X">`
exakt; idno mit Zusatzattribut oder auf der sigle-Zeile wird nicht entfernt,
sondern dupliziert (Schema laesst am msIdentifier-idno nur @type zu, Zeile 114
mhdbdb.rnc; heute 0 Vorkommen beider Faelle). Mutationsproben: Scratch-Layout
mit scripts/corpus_files.py + scripts/sync/ + tei/<8 Dateien> + authority-files/
works.xml, cwd = Scratch (TEI_DIR haengt an __file__, AUTHORITY_DIR ist
relativ), Mutation mit `assert new != blk` absichern.
MWB-Quellenverzeichnis: `https://www.mhdwb-online.de/quellenverzeichnis.php?buchstabe=N`
fuehrt NibA, NibB, NibB_(B), NibC, NibD (WebFetch 07.09.2026).

**Runde 2 zu #399 (07.09.2026, nach Bot-Fixes, ungestagt):** Der nach hinten
verschobene Block (chirurgischer Schreiber NACH `syncers_to_run`) steht jetzt
VOR dem Stub-Guard: `--works --persons` schreibt erst das Korpus und endet dann
mit Exit 1 „Refusing …"; auf origin/main stand der Guard (Z. 563) vor der
Syncer-Schleife (Z. 593), nichts wurde geschrieben. Muster: ein verschobener
Block aendert die Reihenfolge zu BEIDEN Nachbarn, nicht nur zu dem, der den
Fehler ausgeloest hat. Hartes Gate fuer `ohne_msid`: die Zeile „Beheben mit:
--works" gilt dort nicht, der Schreiber ueberspringt Dateien ohne msIdentifier
(`continue`, Exit 0), Gate bleibt rot. Unter `--all` druckt die alte Summe
„Total files that would be updated: 0" direkt nach „[works] wuerde aendern: 1".
Messwerte: Check 0,591 s; OVG 65.999.808 B (= 66,0 MB dezimal, 62,9 MiB);
Korpus 1.432.472.114 -> 1.430.556.264 B nach lxml-Pfad (lab2-Kopie, 667
geaendert, mwb-sigle 19 -> 0). Lab-Layout wie oben, `cp -r tei` passt bei
9 GB frei; Vergleich der listBibl mit kanonischer (sortierte Kinder,
whitespace-normalisiert) Form dauert Minuten, im Hintergrund starten.
Der Zweig-Commit 5369b9aa3 (main-site.spec.js reload) haengt mit #399 nicht
zusammen und ist nicht in main.
