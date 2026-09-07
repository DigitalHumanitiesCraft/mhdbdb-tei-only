---
name: header-sync-duplicate-sigle-395
description: sync_tei_headers.py --works keyt nach Sigle, letzter Eintrag gewinnt; TRO hat zwei bibl in works.xml (work_69 Konrad, work_c7da236c Fortsetzung), der Sync setzt den Header auf die Fortsetzung zurueck. Plus Umgebungsfallen der Cloud-Session (python3.13 fuer lxml, kein gh, api.github.com 403, Shallow-Clone)
metadata:
  type: project
---

Review-Runde 1 zu e8cb256 (Zweig `claude/agents-setup-network-check-08f1ri`, #395 Punkt 3) am 2026-09-07.

**Die Falle, die der Diff nicht zeigt:** `scripts/sync/sync_tei_headers.py` (`WorksSyncer.load_authority_data`, Zeile 181 bis 241) baut `sigle_to_work[sigle] = work_data` ohne Kollisionspruefung. `authority-files/works.xml` hat 584 `bibl` auf 583 Siglen; TRO ist die einzige Sigle mit zwei Eintraegen (`work_69` Konrad, hc 212 / GND 4285313-8 / Q66770444, und `work_c7da236c-...` Fortsetzung, hc 929 / GND 1181164893, kein Wikidata). Der zweite steht spaeter in der Datei und gewinnt: `d['TRO']['work_id'] == 'work_c7da236c-...'`. `update_tei_header` (Zeile 265 ff.) loescht alle Nicht-Sigle-`idno` im `msIdentifier` und schreibt hc/GND/wikidata aus dem Mapping neu; `@corresp` fasst es nicht an. Auf einer Kopie simuliert: ein Header mit 212 / 4285313-8 / Q66770444 wird zu 929 / 1181164893, Wikidata weg, corresp bleibt `work_69`. DATA-MODEL Authority-Checkliste Schritt 1 schreibt genau diesen Lauf fuer jede works.xml-Aenderung vor.

Kein Gate haelt Header-`idno` gegen works.xml: `check-authority-cross-refs.py` und `audit-tei-corpus.py` greppen weder `handschriftencensus` noch `msIdentifier` (gemessen). Der Reader (`tei-text-reader.js` ab Zeile 332) nimmt hc/GND/wikidata aus dem Work-Objekt des Authority-Index, nicht aus dem Header; Header-`idno` sind also nirgends nutzersichtbar und in keinem Build (`build-corpus-index.py` liest nur `idno[@type="sigle"]` und `msIdentifier/@corresp`, Zeile 94 und 130).

Reihenfolge-Konvention im `msIdentifier`, ueber alle 667 Dateien gemessen: sigle, handschriftencensus, GND, wikidata, [mwb-sigle], msName+. Formate im Header: nackte Ids (713 GND, 790 wikidata `Q...`, 355 hc), in works.xml URLs.

**Umgebung der Cloud-Session (07.09.2026):** `python`/`python3` sind 3.11 ohne lxml, `python3.13` hat lxml 6.0.2. Kein `gh`; `api.github.com` antwortet 403 („GitHub access is not enabled for this session"), `github.com`-Issue-Seiten gehen per curl/WebFetch (Status ueber `"state":"OPEN"` im HTML greppen). Klon ist shallow (59 Commits, aeltester 4458686 vom 24.08.), `git log -S` findet deshalb keine Herkunft vor diesem Datum. de.wikipedia-API rate-limitet nach wenigen Aufrufen.

**Why:** Der Aufrufer hatte die #397-Frage selbst gestellt und `works.xml` gefunden, aber nur nach *Pruefungen* gesucht, nicht nach *Schreibern*. Der Sync ist kein Gate und stand deshalb nicht auf seiner Liste.

**How to apply:** Bei jedem Diff an `msIdentifier`-Identifiern oder an works.xml-Siglen: `WorksSyncer.load_authority_data()` in-process laden und den Eintrag der betroffenen Sigle drucken; bei Doppel-Siglen `update_tei_header` auf einer Scratchpad-Kopie laufen lassen. Verwandt: [[rebase-review-data-prs]] (Messen statt Diff lesen bei Daten-PRs).

**Runde 2 (75887c3, 07.09.2026):** Der Fix loest ueber `@corresp` auf, aber `self.work_id_to_work[work_id] = work_data` wird pro *Sigle* geschrieben, und `work_data['biblStructs']` ist nach `@key=sigle` gefiltert. Bei 70 von 584 Werken mit mehreren Siglen (z.B. work_205 DES2: 1 biblStruct, GSP: 2) haelt der Eintrag den Datensatz der *letzten* Sigle. Heute folgenlos (work_69 hat nur TRO), bricht bei der naechsten Doppelsigle an einem Mehrfach-Siglen-Werk. Muster: eine per-Sigle-Struktur unter einem per-Werk-Schluessel ablegen.

**Verfahren alt/neu-Lauf ohne Schreiben ins Repo:** `git show <alt>:scripts/sync/sync_tei_headers.py > scratch/old_sync.py`, dann beide Fassungen per `importlib.util.spec_from_file_location` laden (vorher `sys.path.insert(0, '<repo>/scripts')` fuer `corpus_files`) und `WorksSyncer(works_xml, tei_dir=<Kopie>)` mit Kopien von `tei/` im Scratchpad instanziieren. `diff -rq` der beiden Kopien liefert die Differenzmenge; der Vergleich gegen das Repo ist wegen `remove_blank_text` + `pretty_print` wertlos (667 Dateien differieren im Layout).

**Runde 3 (0c9b8e5, 07.09.2026):** Schluessel (work_id, sigle), 669 Eintraege bei 668 Siglen. In-process-Gegenprobe alt/neu ueber 667 Dateien ohne Korpuskopie: beide Fassungen auf je einen frisch geparsten Baum anwenden und `etree.tostring(pretty_print=True)` vergleichen, 0 Differenzen; das spart die 1,4 GB Kopie. Der neue else-Zweig (corresp-Werk fuehrt die Sigle nicht) auf mutierter DES2-Kopie ausgefuehrt: warnt, schreibt Sigle-Aufloesung, laesst das falsche @corresp stehen, zaehlt als updated, Exit 0. Fehlt das Ablage-Attribut, faengt `_update_single_tei` den AttributeError als ERROR-Log pro Datei ab, kein Abbruch. Issue-Kommentare: api.github.com 403, die HTML-Seite meldet 0 Kommentare auch wenn welche existieren (clientseitig gerendert), also nicht messbar.
