# MHDBDB Development Journal

Chronological log of development decisions, dead ends, and savepoints. Not a changelog – captures the *reasoning* behind changes.

---

## 2026-10-19 (Koordination): Suchlinks in der Begriffshilfe (#498)

Anlass ist ein externer Praxistest. Ein Fachkollege hat die Begriffshilfe in ChatGPT hochgeladen, die Antwort fand er brauchbar. Seine Kritik: das Modell sucht nicht selbst. Es schlug Lemma-Paare mit Abständen vor, die man dann von Hand eintippen musste.

Selbst suchen kann es auch nicht. Der Playground ist eine JS-App, und die API liefert keine Treffer. Die Hash-Routen nehmen aber vorbelegte Suchen an. Die Datei gibt der KI deshalb jetzt zwei Linkmuster vor (`#concepts&q=`, `#multi-lemma&lemmata=…&dist=`).

Zwei Prüfungen vor dem Start (Fable als Berater, Opus) haben zwei Dinge gekippt, die ich vorhatte:
- Der Satz „prüfe die Lemma-Chips“: `executeSearch()` setzt die Suche über `reset()` zurück, nach einem Link gibt es also keine Chips mehr.
- Lemma-Links ohne Einschränkung: Die Suche nimmt bei einer Schreibung still `matches[0]`. In einen Link dürfen deshalb nur Schreibungen aus der Spalte „Häufigste Lemmata“. Die Lemmata des Testfalls stehen alle dort.

Lemma-IDs in die Tabelle aufzunehmen, um zu pinnen, ist verworfen: Das deckte nur die Top 5 je Begriff ab.

## 2026-10-19 (Koordination): Nachschau zum Lauf vom 18.10.

**Was:** Nach dem Lauf sind fünf weitere PRs gemergt, #631 bis #633 am Abend des 18.10. und #635, #636 am 19.10. (Tabelle im Laufplan, Abschnitt Abnahme); die Nachschau prüfte danach Aufräumen, Doku und Issues. Elf Drift-Gates grün. Neun alte lokale Zweige von vor dem Lauf (#583 bis #608) gegen ihren Squash abgeglichen (0 abweichende Dateien) und gelöscht. Zwei Sonnet-Agenten lasen Doku gegen die Commits seit 18.10. und 28 Issues gegen ihre Threads; nachgezogen sind ROADMAP (geschlossene #123, #404, #406, #228, #369 und der Stand von #58, #251, #93), FEATURES und DEVELOPMENT (Kartenkopf, Einklappen, ONAMA "abgeleitet", Formatfehler als harter Fehler), `scripts/review/README.md` (fünf Skripte des Laufs fehlten) und dieser Laufplan.

**Was über den Einzelfall hinausgilt:**
- Die tägliche Issue-Matrix war seit dem 16.10. rot, und niemand im Lauf hat es gesehen: #358 trug `wait:kzw`, obwohl Katharina am 11.09. geantwortet hatte und keine Frage an sie folgte, und Julias Antwort vom 15.10. stand ohne Erwiderung. Behoben am 19.10.: Antwort an Julia, `wait:kzw` entfernt. Ein roter Matrixlauf steht nur in der Actions-Liste, nicht in einem Ticket; vor einem Lauf und nach ihm gehört `gh run list --workflow issue-matrix.yml --limit 3` in die Prüfung.
- Ein PR, der ein Ticket nur im Commit nennt ("Bezug: #N"), lässt das Ticket stumm: #564 trug nach #618 als letzten Kommentar die Bot-Erinnerung, die #618 abgearbeitet hatte.
- Eine Prüfseite, die bei einer Person liegt, wird bei Korpusdrift nicht neu gebaut, sondern eingegrenzt: bei #359 betrafen die Änderungen seit 21.09. vier von 17 offenen Fällen, alle aus schon umgesetzten Entscheidungen (#460, #461, #471).

---

## 2026-10-18 (Koordination lauf-1018): vier Spuren, Nachzug, Abnahme

**Was:** Issue-Audit (78 offene Issues, 471 von 471 Kommentaren), daraus vier Sonnet-Spuren (daten, frontend, lesung, onama) unter dem Laufplan `docs/playbooks/kickoffs/2026-10-18-lauf.md`, dort auch die Grenzverhandlungen G1 bis G8 und die Abnahme. 14 PRs gemergt (#617 bis #630), davon vier als Nachzug auf chsteiners Zuruf über einen Workflow der Koordination (Freigabeliste für "Demnächst im Korpus", ONAMA-Status umgerechneter Passagen, harte Fehler statt stillem Weiterlaufen, Klick in die Fundstellen). Geschlossen: #440, #448, #463, #535, #545.

**Was über den Einzelfall hinausgilt:**
- Zwei Zweige, die denselben Satz wahr machen müssen, haben eine Merge-Reihenfolge: der Kommentar in `monatslauf-seiten.yml` zu Formatfehlern stimmte für `build-publikationen.py` erst nach #627; #628 ging deshalb danach.
- Workflow-Worktrees unter `.claude/worktrees/` haben kein `node_modules`; eine Junction auf den Hauptbaum reicht für `npm test`, und sie wird vor `git worktree remove` als Verweis gelöscht (`[System.IO.Directory]::Delete(p, $false)`), nicht rekursiv.
- `claude agents --json` meldet "blocked" auch für eine Spur, die nur wartet; nur die daten-Spur stand wirklich am Nutzungslimit.

**Rote Zeilen:** keine.

**Was zurück an Christian geht:** die Berater-Punkte der Runden (Liste im Abschlussbericht der Sitzung) und chsteiner/claude-code-setup#88 (Reviewer setzte `taskkill /IM python.exe` ab).

---

## 2026-10-18 (Spur lauf-1018-daten, D4): Glossar #554, Datenteil

**Was:** Nach KZWs Entscheidungen vom 16.10.2026: brî ohne ADJ, der Verweis auf lêrchenvuoʒ bei lêrche entfällt (kein Korpusbeleg, auch nicht getrennt), 9 nagel-Belege im Gewürzkontext tragen jetzt `@ana` auf `lemma_4302_sense_6725`, 17 Tokens von trûbe sind am Token geprüft und umgehängt (13 Adjektive auf trüebe, 4 Verben auf trüeben, altes `@ana` entfällt; 4 Belege bleiben offen: HIS_98_2, WZB_79rb_15_5, FR1_2007050_8, ROT_19160_2). 11 historische MHDBDB-Trefferzahlen in 9 Glossarkommentaren sind durch Messungen am heutigen Korpus ersetzt (`scripts/review/messen-554-zahlen.py`). lôr/lôrber: Befund, nichts umgehängt (lôrber, 7 Belege, ist das Ziel, ergänzt um lôrboum). Indexe Authority 1.9.31, Corpus 4.2.36, fünf neue Variantentypen `type_372861` bis `type_372865`, ein Flip (trube) quittiert.

**Was über den Einzelfall hinausgilt:**
- Eine Zählung über `@lemmaRef` ist keine Zählung des Textes. Die Messung rôt+rôse ergibt 48 Verszeilen, die alte MHDBDB-Zahl 116; die Differenz sind rôse-Belege neben unannotierten rôt-Formen. Die Kommentarsätze sagen deshalb, dass nur mit Lemma annotierte Wörter gezählt sind.
- WZB ist Prosa und nutzt `<l>` als Satzeinheit (Handschriftenzeile in `<lb/>`): eine "Verszeile" ist ein `<l>` in einem Text ohne `<lb/>`. Sonst steht hungerc mit 41 statt 39 in Verszeilen.
- Die Aufteilung "innerhalb der Dichtung" bei wîn und brôt entfällt: sie hat keine reproduzierbare Definition.
- Aus dem Satz im Kommentar zu wîn ("brôt zählt zu den häufigsten Wörtern in Zwillingsformeln", gefolgt von "wîn und") ist ersichtlich, dass der Text aus dem brôt-Kommentar übernommen wurde; nicht verändert.

**Rote Zeilen:** keine.

**Was zurück an Christian geht:** nichts; die offenen Belege und zwei nicht angefasste Altzahlen (salse: MPS-Suche; visch+haben: Lesung der Stellen) gehen als Frage an KZW in #554.

**Review:** Runde 1 (Opus, voll) auf `0160e7125`: kein A, vier B (Zählsätze, "unmittelbar vor", hungerc, CONTRACTS-Zahlen), behoben. Runde 2 (schmal): kein A, drei B (WZB als Prosa, DATA-MODEL 4,976, Kopfzeile), behoben. Runde 3 (schmal) auf `b80f823f2`: kein Befund. Voller `npm test` auf `0160e7125` grün (528 Tests), Teillauf nach den Folgecommits grün (76 Tests, 8 Specs: Lemmaseite, Kommentare, Lemma-ID-Suche, Varianten, Playground, Wörterbuch). Der Reviewer beendete in Runde 1 mit `taskkill /IM python.exe` einen eigenen Lauf und möglicherweise Python-Läufe anderer Spuren.

---

## 2026-10-18 (Spur lauf-1018-daten, D5): Zotero-Kette FR3 und FLG/FLG1 (#486)

**Was:** Nach KZWs Entscheidungen vom 16.10.2026 sind die zwei Zotero-Einträge geschrieben: `MVWV5QYG` (FR3) auf das Supplement von 2000 (Haustein/Stackmann, ISBN 3-525-82504-8, Reihe 232; Version 1563 auf 2962) und `ATWPNQPS` (FLG1/FLG) auf den Textband 1990 mit Gisela Vollmann-Profe (Artemis, München; 1563 auf 2963). Danach Online-Sync: in `works.xml` ändern sich nur die drei `biblStruct` FLG, FLG1, FR3; Header-Sync auf `tei/FLG`, `FLG1`, `FR3`. `BESTAND_BEHALTEN` ist `{'FLG': ('analytic','note'), 'FR3': ('analytic','note')}`, Authority-Index 1.9.30 (Corpus unverändert 4.2.35). Rückweg: das Item-JSON beider Einträge vor dem Schreiben steht im PR-Body.

**Was über den Einzelfall hinausgilt:**
- Vor dem Schreiben nach außen den Sync lokal gegen einen gepatchten Cache simulieren: die Simulation zeigte, dass die Vorgabe "FR3 fällt ganz heraus" den Supplement-Verweis und die Mitarbeit der Notiz gekostet hätte (Zotero hat dafür kein Feld). Die Koordination entschied daraufhin, beides dauerhaft zu behalten.
- Der Header-Sync entfernt ein Element nicht, das aus `works.xml` verschwunden ist (hier `biblScope unit="volume"` bei FR3); das Gate meldet es, die Handänderung ist einmalig. Ein erneuter `--offline`-Sync und `--works` erzeugten danach keinen Diff, die Handänderung wird also nicht zurückgeholt.
- Der Werktitel von FLG1 "(Buch 3-7 / Neumann MTU 1990)" und sein `analytic` "Buch 1-7" widersprechen sich weiterhin; als Nebenbefund in #486, nicht aufgelöst.

**Rote Zeilen:** keine.

**Was zurück an Christian geht:** nichts über die Fragen in #486 hinaus (Werktitel FLG1, für KZW).

**Review:** Runde 1 auf `cedee251a`, mergefähig, kein A-Befund; B-Befund (CONTRACTS F.4a und DATA-MODEL beschrieben die alte Lage) in einem Folgecommit ohne weitere Runde behoben. Teillauf `npm test` auf Port 8084 grün (reading-view, genre-explorer, genre-filter-suggestion, authority-id-search, lemma-id-search, variant-candidates; sie lesen Header-Metadaten, Werk- und Gattungsdaten des Authority-Index).

---

## 2026-10-18 (Spur lauf-1018-daten, D1 bis D3): Lexikon gegen Korpus, naschen, Fabeltiere (#462, #602, #461)

**Was:** #462 nach KZWs Antwort vom 16.10.2026: 16 Lexikoneinträge bekommen 17 Wortarten (Codes a und günlich), 6 Token-`@pos` sind geändert (zedolne ×2, alwirdic, immo, deprofundis, ungenuoge), 2 Tokens umgehängt (aditus auf `lemma_67813`, standime auf `lemma_70734`, neue Typen `type_372859` und `type_372860`). #602: 4 naschen-Belege auf `lemma_57919_sense_93122` (Essen), `OVW_1025010230_4` bleibt offen. #461: `concept_14101100` und `lemma_1958_sense_119200` für Drache und Phönix (4 Belege); Messung an `sense_3004`: 55 Belege, 38 tot, 12 lebend, 3 lebend mit Zweifel, 2 Tier, nichts umgehängt. Indexe Authority 1.9.29, Corpus 4.2.35. Skripte `apply-462-602.py`, `apply-461-fabeltiere.py`, `messen-461-sense3004.py`; Belege unter `ingest/pos-disambig/462-pos/`, `602-naschen/` und `ingest/review/461-gebeine/`.

**Was über den Einzelfall hinausgilt:**
- Ein `@reason` auf `<w>` macht die Datei für `tei_all` ungültig und lässt sie aus der Baseline in `validate-corpus.py` fallen (JT: 35 statt 34 Dateien). Der Vorschlag für zedolne sah eines vor; es fehlt bewusst und ist ein offener Rest für nach dem Freeze.
- Zwei Umhängungen, bei denen eine Form nur ein Token hat, lassen den Eintrag des alten Lemmas in `variants.xml` verschwinden: das senkt die Zahl der Einträge (42.460 auf 42.458) und löst den Flip-Gate aus. Beides gehört in dieselbe Datenänderung wie die Quittung und die Zählzeilen in den Docs.
- Die Einstufung vom 10.10. zu gebeine hielt die Ochsen in Pharaos Traum (`JEW_556900000_3`, `JEW_557800000_0`) für menschlich; sie stehen im selben Traum wie `JEW_566800000_5` (tierisch). Eine Einstufung am Fenster statt am Zusammenhang übersieht das.
- MWB: die Suche über Lemma, Wortform und Artikelstichwort ist schnell, die Volltextsuche läuft in einen Timeout. Ergebnisse wie "0 Treffer" brauchen einen Kontrollwert (`minne`: 6 Treffer).

**Rote Zeilen:** keine. (`trockenlauf-auswerten.py` lief vor diesem Eintrag, der Kontrollwert hat gefeuert: 73 Zeilen nicht auswertbar.)

**Was zurück an Christian geht:**
- Fragen an KZW (nach Merge und Deploy): indelicius (Satz, MWB ohne Treffer, Wohin gehört ihr Kommentartext zu Ezechiel 28,13), unpeweglich (Satz, MWB: un-bewëgelich Adj.), `OVW_1025010230_4` (Essen oder Erotik), die Messung an `sense_3004` mit dem Vorschlag eines eigenen Sense für lebende Gebeine.
- Ob die Hunde bei NEI, NEIC und NEIR unter "Ernährung von Menschen" (`concept_21111000`) fallen.
- Die zwei Ochsen-Belege an `sense_3004` gehören sachlich an `sense_119196`; nicht umgehängt.

**Review:** Runde 1 auf `184715a94`, Urteil mergefähig, kein A-Befund; B-Befund (README 462-pos datiert) in `9de0a0b63` ohne weitere Runde behoben. Volllauf `npm test` grün auf der Basis `111aef2b1` (512 Tests), danach auf `origin/main` die drei neuen Specs aus #619 (37 Tests) grün.

---

## 2026-10-18 (Spur lauf-1018-onama): ONAMA-Anker-Abgleich und Narrativ-Explorer, Pilot Argonautensage (#609)

**Was:** KZWs Manifest vom 16.10. umgesetzt, soweit es Abgleich und Pilot betrifft. O1: `scripts/ingest/onama/anker-abgleich.py` liest `onamaObjects.ttl` (onama-corpus `b87468b`) und prüft die 308 `TextPassage`-Ressourcen gegen die `xml:id` im TEI (MHDBDB `a89aaf788`): 291 Wortanker, 9 Nichtwort-Anker (7 `pc`, 2 `caesura`), 1 umgekehrt (Q288), 7 nicht gefunden, dazu die 309. Aussage Q67 (`AXU_XXXX`) in eigener Liste. Das sind die Manifestzahlen. O2: `scripts/ingest/onama/build-paket.py` erzeugt aus dem RDF `playground/data/onama/argonauten.json` (Teilbaum Q1309, Sammlungen TRO, TRY, ÖNB cod. 2773; 179 Realisierungen), der Explorer steht unter `playground/#onama` (`playground/js/ui/onama/`, `playground/css/onama.css`), dazu ein Hilfeabschnitt. Nichts in `tei/`, `authority-files/` oder an Annotationen.

**Was über den Einzelfall hinausgilt:**
- Der Konzeptbaum trägt die Auswahl nur halb: mehrere TRO- und TRY-Konzepte mit Argonautenbezug (etwa Q163 "Jason wählt Argonauten aus"; gesichtet, nicht abschließend gezählt) haben kein `broader` und hängen nicht an Q1309. Eine Auswahl über `narrower` allein hätte sie still ausgelassen; sie stehen als Randfälle (49 insgesamt, mit Grund) beim Pilot, die Entscheidung liegt bei KZW.
- Von 41 Bildrealisierungen ohne `partOfCollection` teilen nur 9 den RO-Nummernkreis (erste fünf Zeichen) mit Sammlungsmitgliedern. Die Handschrift ist für sie nicht belegt; sie stehen als Quelle `REALONLINE`, Zuordnung "abgeleitet".
- Bei 93 Wortanker-Passagen und einer Nichtwort-Passage ist ein Endpunkt ein `<w>` ohne `@lemmaRef`, das die Positionszählung nicht zählt. Die Wortspanne wird auf das nächste bzw. vorige gezählte Wort umgerechnet und je Passage als "umgerechnet" markiert (51 von 163 Passagen mit Wortspanne). Das Manifest hatte die Frage gestellt, die Zahl stand nicht darin.
- Ein `<caesura xml:id>` kann Endpunkt einer Passage sein; der erste Lader kannte nur `w` und `pc` und zählte 9 statt 7 nicht gefundene Anker. Der Abgleich gegen die Manifestzahl hat es gefangen.
- Der Prüfstatus hat festen Vorrang offen vor abgeleitet vor geprüft; "geprüft" heißt technisch, nie fachlich. Verteilung am Ende 78 geprüft, 74 abgeleitet, 27 offen (179). Frühere Stände: 119/46/14 (erste Regel), 78/87/14 (ohne Vorrang). Die Verschiebung von 87/14 auf 74/27 sind 13 Bilder ohne Bildlink.

**Rote Zeilen:** Vier, Nr. 157 bis 160 (RO-Zuordnung als Allaussage ohne Messung; Spec-Titel verspricht, was die Assertion nicht prüft; `umgerechnet` an der Wortspanne statt am Status, #397; Statusdefinitionen und README-Satz ohne Nachzählen). `trockenlauf-auswerten.py` lief vor diesem Eintrag, der Kontrollwert hat gefeuert (73 Zeilen nicht auswertbar), die Zahlen sind eine Untergrenze: der Spur zugeordnete Zeilen shell-konventionen 125 (davon 20 Treffer), mengenaussagen 70 (17 Treffer).

**Was zurück an Christian geht:**
- Die Berater-Punkte des Reviewers: Die Oberfläche zeigt nur die Q-Kurzform (die volle Quell-URI steht im Tooltip und im Paket; ob das Kriterium 2 genügt, entscheidet KZW), das exportierte Feld `gleichzeitig` (23 Realisierungen) wird nicht angezeigt, und die Passagenebene hat bei umgerechneter Spanne weiter das grüne "Anker geprüft", daneben die Markierung "umgerechnet".
- Im Kommentar in #609 nach Merge und Deploy: die 93 plus 1 umgerechneten Spannen mit der Regel, die 49 Randfälle, die Quellenauswahl, und für Peter das Exportformat (DATA-MODEL.md, Abschnitt ONAMA pilot package).
- Der volle Lauf vor dem Merge: im ersten Lauf auf dem Stand vor den Fixes `VERDICT: ROT (1 flaky ...)`, 0 unexpected; der Flaky-Fall war `playground-router-start.spec.js` ("#naming rendert, waehrend der Korpus-Index noch laedt"), mit `--repeat-each=3` grün.

**Review:** Opus. Runde 1 auf 6f211c556 (vor Rebase): ein A-Befund (Spec "nicht verlinkt" prüfte den Link nicht), vier B-Befunde (Statusdefinitionen, Auswahltext, README, Inventare). Runde 2 auf 76389aa0d (Delta): ein A-Befund (`umgerechnet` hing an `bool(wortspanne)`, #397), drei B. Runde 3 auf 98e5c4252 (Delta nach A, Opus): kein A-Befund, mergefähig. Danach ein rein mechanischer Commit ohne Review (Umlaute in einem Anzeigetext, Zeile `Ohne Review:` im Commit), nach dem Rebase auf `9eaf1fd78` ohne Konflikt und mit Chrome-Prüfung am Endstand (Einstieg über Ding, über Entität, Filter Nur Bild). Ein zweiter Rebase auf `d6d7b51f3` (#621, Index 1.9.29/4.2.35) hatte nur im Journal einen Konflikt (beide Einträge behalten).

---

## 2026-10-18 (Spur lauf-1018-lesung, L2): zweite Lesung zu Ernährung von Menschen oder Tieren (#603)

**Was:** KZWs Wunsch vom 16.10.2026, die Vorsortierung sprachlich gegenzulesen, ist umgesetzt. 13.135 Belege (tier 2.867, unklar 2.523, mensch 7.745) von 42 Sonnet-Agenten in fünf Workflows gelesen, blind gegen die Klasse der Vorsortierung, Kontext 30 Token links und rechts. Lesung: mensch 8.037, keine_nahrung 3.908 (Lemma-Rauschen der Vorsortierung), tier 955 (Säugetier 433, Vogel 239, andere 171, unbestimmt 95, Fisch 17), unklar 235. Nicht gelesen: 20.023 Belege ohne `@ana`, die nicht `tier` sind. Ergebnis in `ingest/review/603-ernaehrung/` (`zweite-lesung.tsv`, `senses-lesung.tsv`, `lemmata-lesung.tsv`, `konzeptfrage.txt`, `pruefen-603.tsv`, README-Abschnitt), Skripte `stapel-603.py`, `verbinden-lesung-603.py`, `auswerten-lesung-603.py`. Nichts in `tei/` oder `authority-files/`; die Konzeptfrage steht bei KZW.

**Was über den Einzelfall hinausgilt:**
- Die Tierbelege sind meist eine Minderheit innerhalb von Bedeutungen, die sonst Menschen meinen (23 von 78 Bedeutungen mit Tierbelegen haben Tier-Mehrheit); ein zusätzliches Konzept an der Bedeutung allein trennt sie nicht. Das Korpus gibt auch Vögel (239) und andere Tierklassen her, nicht nur Säugetiere.
- Agenten schreiben Schlüssel falsch ab (17 von 13.135 w_id, 0,13 %) und flicken sie mit eigenen Hilfsskripten, ohne es zu melden. Verbunden wird über die Zeilennummer, und der Stand der Eingabe wird nicht aus dem Bericht des Agenten, sondern aus den Workflow-Transkripten gelesen (`rg 'fix [0-9]+ [0-9]+'`).
- Eine Regex über `<sense>...</sense>` im Lexikon ist falsch, weil 124 Senses selbstschließend sind; Lexikon immer mit lxml lesen.

**Rote Zeilen:** Eine, Nr. 154 (Differenz subtrahiert statt die fehlenden Elemente zu benennen: "431" statt 331 plus 100 ohne `@ana`, im README bis zur Review-Runde 1). `trockenlauf-auswerten.py` lief vor diesem Eintrag, der Kontrollwert hat gefeuert (73 Zeilen nicht auswertbar); die Zahlen sind eine Untergrenze und der Hook ist nachzusehen.

**Was zurück an Christian geht:**
- Die Konzeptfrage an KZW (Umbenennen von "Stoffwechsel von Säugetieren" oder neue Kategorie "Ernährung von Säugetieren") nach Merge und Deploy im #603-Kommentar, mit der Prüfliste der fünf Belege.
- Berater-Punkt des Reviewers: `verbinden-lesung-603.py` schreibt auch bei gemeldeten Formfehlern `teil-*.tsv` und endet mit Exit 0. Ob Prüfmaterial einen harten Abbruch braucht, ist eine Entwurfsfrage, nicht umgesetzt. Ebenso: der neue Abbruch in `auswerten-lesung-603.py` vergleicht gegen die eingecheckte `senses-21111000.tsv` und fängt ein geändertes Lexikon nur, wenn jemand sie neu erzeugt hat.

**Review:** Opus. Runde 1 auf b859cd41e: zwei A-Befunde (Regex über `<sense>` kennt keine selbstschließenden Senses; Docstring versprach einen harten Fehler, der Code tat `pass`), drei B-Befunde (17 statt 13 Korrekturen, 331 statt 431, 52 Minderheit statt 55), alle nachgemessen und behoben. Runde 2 auf aea8b8f67 (Delta, Opus nach einem A-Befund): kein Befund, mergefähig.

---

## 2026-10-18 (Spur lauf-1018-lesung, L1): Prüfseiten auf gerade Anführungszeichen (#440)

**Was:** Auf KZWs Antwort vom 16.10.2026 sind die schrägen Anführungszeichen (U+201E, U+201C) in den drei Prüfseiten aus #440 und in ihren Generatoren durch das gerade `"` ersetzt: `359-pruefseite.html` 8 Zeichen in 3 Zeilen, `418-houwen/pruefseite.html` 1 in 1, `pruefseite-526.html` 66 in 19, `build-359-page.py` 2, `build-526-pruefseite.py` 66, dazu `vorschlaege.json` (6, als `\"`), die Eingabe des 359-Generators und Quelle von zwei der drei Zeilen der Seite. Rückzählung in allen sechs Dateien: 0. Die Seiten sind nicht neu generiert, denn ein Lauf von `build-359-page.py` hätte Stand-Datum und Index-Version mitgeändert und setzt `&quot;` statt `"` (gleiche Darstellung).

**Nicht berührt (Zählung, Zeichen):** `examples/review-pages/` (364: 28, 371: 208, Klaus: 43, Glossar-554: 7.563), Vorlagen `scripts/audit/review-364.template.html` 28 und `review-klaus.template.html` 39, `scripts/ingest/glossar-554/pruefseite.template.html` 12, dazu `359-borek/folgebefunde.md` 16, `359-borek/evidence.json` 5 (« » in Quelltext, Daten) und `418-houwen/README.md` 3.

**Was über den Einzelfall hinausgilt:** Ein Generator hat oft mehr Eingaben als sein Skript: die 359-Seite bezieht Text aus `vorschlaege.json`, und ein Ersetzen nur im Skript hätte beim nächsten Lauf die schrägen Zeichen zurückgebracht. Vor dem Ersetzen die Eingaben des Generators mitzählen.

**Rote Zeilen:** keine.

**Was zurück an Christian geht:** nichts. `trockenlauf-auswerten.py` lief vor diesem Eintrag, der Kontrollwert hat gefeuert (73 Zeilen nicht auswertbar); die Zahlen sind eine Untergrenze und der Hook ist nachzusehen, bevor jemand sie zitiert.

**Review:** keine Runde, rein mechanische Zeichenersetzung (`Ohne Review:` im Commit); Syntaxcheck `ast`/`json` grün.

---

## 2026-10-16 (Spur lauf-1016-daten): jagât-Rest und gebeine nach KZWs Antworten (#460, #461)

**Was:** KZWs Antworten vom 15.10.2026 sind umgesetzt. #460: `WH_28126_1` (jaget) und `JT_43134000_4` (jagennes) von `lemma_3103` jagât auf `lemma_3102` jagen (`@pos="VRB"`, ohne `@ana`); `WVW_6542_4` bleibt Nomen, `AXU_18452_5` und `JT_48611000_4` bleiben unverändert (KZW braucht mehr Kontext). `lemma_3103` trägt danach 38 Tokens, `lemma_3102` 1.553. #461: `lemma_1958` gebeine hat zwei neue Senses, `sense_119198` (Vögel, `concept_14021100`, Hahn `AMI_972_3`) und `sense_119199` (Fische, `concept_14031100`, `FLG1_4135180940_2`); die 9 offenen Belege kommen nach KZWs Regel an `sense_49690` (8 Tokens ändern sich, `NAR_9400900_3` trug ihn schon; `JSG_410_1` wechselt von `sense_3004` und verliert das Tod-Konzept). Drache und Phönix bleiben unverändert. Corpus Index 4.2.34, Authority Index 1.9.28; 12 Tokens in 10 TEI-Dateien. Umsetzung: `scripts/ingest/pos-disambig/apply-460-461-rest.py`, Belege mit Entscheidung und Quelle in den Tabellen der beiden `ingest/`-Ordner.

**Was über den Einzelfall hinausgilt:**
- Die drei "Würfelknochen" in DRE sind menschlich: die Würfel sind aus den Stockzähnen des Ritters gemacht (`tei/DRE.tei.xml`, V. 36, 117 und 122 bis 126). Die Einstufung vom 10.10. las nur V. 137 bis 217 und hielt die Herkunft für nicht genannt; meine Bestätigung ("kein Tier genannt") stützte sich auf dasselbe Fenster. Ergebnis (`sense_49690`) bleibt, die Begründung war falsch. Eine Herkunftsfrage ("woraus ist es gemacht") wird am Anfang der Episode gesucht, nicht in dem Fenster, in dem das Wort vorkommt.
- Die Tabelle vom 10.10. behauptete für `NAR_9303540_3` "Sense 49690 gesetzt"; im TEI trug nur `NAR_9400900_3` den Sense. Eine Zustandsangabe in einer Arbeitstabelle ist eine Behauptung, bis das TEI sie trägt.
- Der Auftrag nannte "Authority 1.9.27, Corpus 4.2.33" als Ziel der Basis + 1; das war der Stand von `origin/main`. Die Koordination hat es bestätigt (G2), die Versionen sind 1.9.28 und 4.2.34.
- Die Flip-Quittung `scripts/audit/variants-flips-ack.json` liegt unter dem eingefrorenen `scripts/audit/`, ist aber gitignoriert und wird mit `git add -f` aufgenommen, wie bei #554; die Koordination hat sie als benannte Ausnahme bestätigt.
- Sense-Nummern: die höchste war nicht mehr 119196, sondern 119197 (`lemma_79829_sense_119197`, #554). Vor dem Vergeben messen, nicht aus der Vorgängerarbeit übernehmen.

**Rote Zeilen:** Eine, Nr. 138 (Herkunft am Fenster statt an der Episode gesucht und der Koordination als Befund gemeldet).

**Was zurück an Christian geht:**
- Die Fragen an KZW (nach Merge und Deploy): Drache und Phönix direkt an `concept_14100000` "Fantastische Tiere" oder ein neues Körper-Unterkonzept; Frage 3 (Tod-Konzept an `sense_3004`) mit Belegen eines lebenden Körpers; in #460 der längere Kontext zu `AXU_18452_5` und `JT_48611000_4`.
- Hinweis an KZW: `JSG_410_1` (Riesin) verliert mit dem Sensewechsel das Tod-Konzept, obwohl sie als Tote gemeint ist; das gehört zu Frage 3.
- `trockenlauf-auswerten.py` lief vor diesem Eintrag, der Kontrollwert hat gefeuert (73 Zeilen nicht auswertbar); die Zahlen dort sind eine Untergrenze, keine Messung, und der Hook ist nachzusehen, bevor jemand sie zitiert.

**Review:** Fable. Runde 1 auf 5af8af2ba: kein A-Befund; B (DRE-Begründung) und C (Zählung in README 460) nachgemessen und behoben. Runde 2 (erste schmale) auf fe2ea471f: kein A-Befund, drei B-Befunde (Versangabe zu kurz, behoben; Spaltennummer im Auftrag verschoben und fehlende Belegtabelle im Auftrag, beides ohne Änderung im Diff). Runde 3 (zweite schmale) auf 49bb8d8bc: kein A-Befund, drei B-Befunde (der Kettenzeiger in Fehlerjournal 138 war mit 61 statt 119 falsch und zu früh abgebrochen, behoben; ein Platzhalter in diesem Absatz, behoben; eine unvollständige Belegtabelle im Auftrag). Nach der zweiten schmalen Runde ohne A-Befund ist ohne weitere Runde gepusht.

---

## 2026-10-15 (Spur lauf-554b): KZWs Prüfergebnisse zum Glossar Kochbuchforschung eingearbeitet, briech als neues Lemma (#554)

**Was:** Katharinas 47 Antworten zur Prüfseite (JSON vom 15.10.2026) sind in `lexicon.xml` umgesetzt: 44 Notizen (19 aus Gruppe A, 22 aus B, 1 D, 2 E), letzen verliert eine Bedeutung, naschen tauscht zwei, briech ist ein eigenes Lemma (`lemma_79829`), das einzige Token ZUK_76100_5 hängt von brî darauf um. Authority Index 1.9.27, Corpus Index 4.2.33; die Lemmazahl steigt auf 43.711, Varianteneinträge 42.460, und die Zahl steht in zwölf Doku- und Seitendateien nach. Dazu `ingest/glossar-554/literatur.tsv` (193 Zeilen, 76 Werke, 74 von 138 Notizen mit mindestens einem Zitat; Untergrenze, ungeprüft). Umsetzung je Fall: `ingest/glossar-554/UEBERNAHME.md`, Abschnitt "Einarbeitung der Prüfergebnisse".

**Was über den Einzelfall hinausgilt:**
- Ein neues Lemma ist eine Änderung an der Lemmazahl in zwölf Dateien; `doc-count-audit.py --check` fand sie erst nach der Datenänderung. Datierte Messungen (CONTRACTS L344/L418) behalten ihre Zahl und bekommen den Vermerk "not today's count" hinter der Zahl, auf derselben Zeile (das Audit liest nur bis zum Zeilenende, höchstens 120 Zeichen).
- Sense-Nummern sind nicht global eindeutig (`sense_5899` gab es an drei Lemmata, nach der Löschung bei letzen sind es zwei); wer eine gelöschte Bedeutung sucht, sucht mit Lemma-Präfix.
- Die wîn-Zählung (mete 63, môraz 57, klârêt 50, lûtertranc 26, malvasier 8, sinôpel 6, alantwîn 1) ist am Korpus-Index nachgemessen und trägt den Stand 15.10.2026.
- Die Kommentare enthalten Altzählungen, Suchsyntax und Ich-Form von 2015 bis 2017 (grobe Textsuche: 12 mit Stand- oder Abrufdatum, 10 mit Trefferzahl, 19 mit Ich-Form; ungeprüft). Kein Eingriff in diesem PR, eigene Frage an Katharina.

**Rote Zeilen:** Eine, Nr. 125 (Zahlen aus der eigenen Verdichtung ungeprüft in die Doku geschrieben; vierte Zeile zu dieser Lehre, 116, 117 und 132 davor).

**Was zurück an Christian geht:**
- Der Mechanismus zu Eintrag 125: vierte Zeile zur Lehre "Zahl neu messen, bevor sie in eine Doku kommt" (116, 117, 132, 125); der Wechsel war nach der Regel schon bei 132 fällig. Vorschlag: Zahlen in Übernahmedokumenten erzeugt ein Skript (`literatur-erfassen.py` macht es vor), die Doku zitiert dessen Ausgabe.
- brî führt nach dem Umhängen `<pos>ADJ</pos>` ohne ein ADJ-Token (Reviewer-Beobachtung, kein Gate sieht es); ob die Wortart am Lemma dem Korpus folgen soll, ist eine Entwurfsfrage.
- Offene Fragen an Katharina (nach Merge und Deploy im Abnahmekommentar): slunthart 1759 ergänzen oder weglassen, lêrchenvuoʒ (a) ohne Beleg anlegen oder (b) bis zum Ingest des Strickers zurückstellen, eigene Bedeutung "Kornschwinge" bei wanne, Fehlannotation "von wannen" (JT), die briech-Konzepte, die Altzählungen in den "passt"-Texten.
- Die Laufplan-Zahl 83 Lerchen-Formen (G5) ist mit keiner Zählregel reproduzierbar (62 Präfix, 75 Teilstring).

**Review:** Fable, Runde 1 auf 488e64e14: kein A-Befund, drei Zahlenbefunde (B1 bis B3) von der Spur nachgemessen und behoben, B4 betraf nur die Basisangabe im Auftrag.

---

## 2026-10-13: #93, Bilder der Textreihentypologie nachgezogen, PR #555 rebased

KZW hat die drei offenen Bildfragen aus #93 über Christian beantwortet: Logos, Startbild und Screenshots dürfen übernommen werden. Alle elf Dateien liegen jetzt unter `textreihen/img/` (Startbild als JPEG in der 1024-px-Fassung, die Logos einmal auf der Startseite statt im Fuß jeder Seite). PR #555 stand vier Tage offen, ohne dass jemand etwas sagte, und war inzwischen `CONFLICTING`; nach dem Rebase lagen die Konflikte im umbenannten Reviewer-Memory (`fable-reviewer/` zu `reviewer/`, #593) und in den beiden Journalen.

**Was über den Einzelfall hinausgilt:** Die Frage in #93 nannte zu Punkt 3 die "Reinmar-Tabelle", die schon übernommen war; die drei Screenshots zeigen die MHDBDB-Oberfläche. Ein Fehler in einer Frage an einen Menschen wandert in jede Nachricht, die aus ihr abgeschrieben wird (hier in den Entwurf einer Signal-Nachricht an KZW).

**Rote Zeilen:** Eine, Nr. 120 (Punkt 3 aus dem Kommentar abgeschrieben statt an README und Zweig geprüft).

---

## 2026-10-10 (Spur D, #564 D3): langsamste Tests schneller, ohne Abdeckung zu verlieren

**Was:** `main-site`, `lemma-page` und `results-table` laufen im warmen Context (#488), zwei Tests in `main-site` bleiben kalt. In `multi-lemma-export` gibt es die große Suche (minne + herze, 66 Dateien im Versmodus) nur noch einmal auf einer gemeinsamen Seite (Fehlerfall, CSV, XLSX aus dem Zwischenspeicher der Suche); Nähe- und Dokumentfall laufen auf kleinen Suchen. Feste Wartezeiten in `main-site` und `reading-view` sind Ereignissen gewichen.

**Messung** (voller `npm test`, Port 8087, `--workers=2`, 492 Tests, beide Läufe grün): Summe der Testdauern 2347 s auf 2062 s, Wanduhr 1205 s auf 1058 s. Je Spec (Summe der Dauern, vorher/nachher): multi-lemma-export 170,4/58,5 s, results-table 124,5/56,5 s, main-site 99,1/47,6 s, lemma-page 99,2/36,3 s, reading-view 95,8/94,1 s. Die Zeit eines `beforeAll` steckt in keinem `duration`; bei multi-lemma-export kommen rund 6 s (Schätzung, nicht gemessen) hinzu.

**Was über den Einzelfall hinausgeht:**
- `waitForLoadState('networkidle')` kehrt sofort zurück, wenn die Seite den Zustand einmal erreicht hatte (gemessen 1 ms bei vier offenen Anfragen). Als Ersatz für eine feste Frist taugt es nicht; der Test zählt jetzt offene `/tei/`-Anfragen. Mutationsprobe (Guard `abgebrochen` entfernt) macht ihn rot an der Endprüfung.
- Im warmen Context bleiben Tabs, die ein Test öffnet, bis zum Workerende offen; `warm-page.js` schließt übrige Seiten jetzt im Teardown.
- Ein Hook läuft mit dem Projekt-Timeout, nicht mit dem des Testblocks.
- Nicht angefasst, aber die nächsten Kandidaten: `attribution-status` (104,8 s), `proximity-and-resolution` (83,7 s), `search-with-corpus`, `korpus-url-zustand`, `position-parity`.

**Review:** Opus, zwei Runden. Runde 1: networkidle wirkungslos, Tab-Leck, Regeltexte zu weit, Zahlen im Kommentar; alles behoben. Runde 2: kein A-Befund, ein überholter Kommentar (behoben), eine Zahl im Auftrag aus einem anderen Lauf (korrigiert). Reviewer-Memory dafür destilliert (eigener Commit).

**Rote Zeilen:** Keine. Nummern 150 bis 154 weiter unverbraucht.

---

## 2026-10-10 (Spur D, #564 D2): `run-tests.js` druckt die Dauer je Spec-Datei

**Was:** Vor der VERDICT-Zeile stehen jetzt Summe der Testdauern (alle Versuche), Wanduhr, tatsächliche Workerzahl und die zehn langsamsten Spec-Dateien. Kein Gate; Verdikt und Exit-Code sind unverändert, die VERDICT-Zeile bleibt die letzte Zeile (Abweichung vom Kickoff-Wortlaut „nach der VERDICT-Zeile“, G1 des Laufplans).

**Was über den Einzelfall hinausgeht:** `config.workers` im Playwright-Report ist das konfigurierte Maximum (hier 6), die tatsächliche Zahl steht in `config.metadata.actualWorkers`; bei einer Datei und `fullyParallel: false` läuft ein Worker. Mein Teillauf mit zwei Dateien und `--workers=2` hat den Unterschied zufällig verdeckt, der Review fand ihn. Wer vorher und nachher je Spec „bei gleicher Workerzahl“ vergleicht, braucht die tatsächliche.

**Verifikation:** Gegengerechnet mit einer unabhängigen Zählung über `report.json`: Teillauf (2 Dateien, 109 s Summe) und der Volllauf-Report von D1 (492 Tests, 51 Dateien, Summe 2.346 s, Wanduhr 1.213 s mit 2 Workern) ergeben dieselben Summen und dieselbe Top-10. Zwei Teilläufe auf Port 8087 (2 Dateien mit `--workers=2`, eine Datei ohne), beide grün. Kein voller `npm test` für dieses Paket: geändert ist nur die Ausgabe vor dem Verdikt, den Volllauf-Zweig lässt der Diff unberührt; D3 fährt ohnehin Volllauf. Review auf Opus, eine Runde (2 B-Befunde, 1 C-Befund, behoben).

**Rote Zeilen:** Keine. Nummern 150 bis 154 weiter unverbraucht.

---

## 2026-10-10 (Spur D, #564 D1): Playground-Suche beschleunigt, Such-Benchmark mit Budget aus dem Runner

**Was:** `authority-manager.js` rechnet Kleinform, normalisierte Form und ID-Zeile einmal je Lemma-Array vor (`getLemmaTables`), prüft die Varianten einmal je Objekt auf Leere (`hasVariants`) und verengt den Autocomplete-Scan auf die Treffer des vorigen Tastendrucks. Dazu `scripts/audit/benchmark-search.mjs` mit `search-budget.json` und eigenem Workflow `search-benchmark.yml`; PR #570. Messwerte vorher und nachher stehen im PR-Body (Node gegen die echten Indexe, 24 Fälle).

### Was über den Einzelfall hinausgeht

**(a) Ein Zeitgate muss die Reihenfolge seiner Fälle kennen.** Dieselbe Playground-Auflösung (`schwertkampf`) brauchte allein 1,0 ms und im selben Prozess nach den Hauptseitenfällen 2,8 bis 3,6 ms, in jedem Block. Der Review fand es, weil das Gate auf seinem eigenen Commit viermal von vier Läufen rot war. Das Minimum mehrerer Blockmediane filtert Last von außen, nicht diesen Zustand; geholfen hat nur ein eigener Prozess je Oberfläche. Die Ursache ist nicht geklärt (Müllsammlung und frische Instanz sind es laut Review nicht).

**(b) Ein Budget gehört dem Ort, an dem es gilt.** Auf dem Entwicklungsrechner schwankten dieselben unveränderten Hauptseitenfälle zwischen 0,6 und 1,8 ms, je nach Last der Nachbarsessions. Auf dem Runner lagen drei Läufe bei 0,345 / 0,672 / 0,655 ms für `main:exakt`: der Runner streut um den Faktor 2 zwischen Läufen, aber nicht mit der Last des Entwicklungsrechners. Das Budget stammt daher aus dem größten von drei Runner-Werten mal 1,5 (Entscheidung G2 der Koordination).

**(c) Eine Untergrenze ist eine Aussage über den kleinsten Rückfall, den das Gate noch fängt.** Mit 1 ms blieb ein `Object.keys(variantCandidates)` je Aufruf (rund 0,3 ms) bei Messwerten von 0,001 ms grün; G4 senkte sie auf 0,1 ms. Die Mutationsprobe mit genau dieser Zeile in `searchLemmaByOrthography` trifft nur die acht schnellen `pg:`-Fälle (gemessen 0,29 bis 0,32 ms gegen 0,001 bis 0,002 ms vorher, Budget 0,1 ms); `pg:praefix` und `pg:unbekannt` bleiben grün. Lokal war das Gate auf einem belasteten Rechner auch ohne Mutation 5 von 24 rot, gegen die Runner-Budgets.

**(d) `NaN > Budget` ist falsch, also grün.** `--reps 0` ergab 24 Zeilen `NaN ms ok`. Ungültige Zahlen enden jetzt mit Exit 2.

### Verifikation

Voller `npm test` (Port 8087, `--workers=2`) auf `1c82b9a5f` (vor dem Rebase lokal `f55a133e0`): `VERDICT: VOLLLAUF GRUEN (492 Tests, 51 Dateien)`; danach änderten sich nur Benchmark-Skript, Budgetdatei, Docs und Agent-Memory. Ergebnisgleichheit gegen `origin/main`: 4.530 Schlüssel byte-gleich. Review auf Opus (Fable-Limit), Runde 1 (5 Befunde, 2 der Klasse A und 3 der Klasse B, alle nachgemessen und behoben) und Runde 2 (Untergrenze nach G4, Ursachenformulierung, stderr).

### Rote Zeilen

Keine. Ein Heredoc-Versuch für eine Scratch-Datei wurde vom Hook gesperrt, bevor er etwas schrieb; das ist abgewendet, nicht gezählt. Die Nummern 150 bis 154 sind unverbraucht.

### Was zurück an Christian geht

#564 bleibt offen (D2, D3 und die Pakete der Spur E). Nichts zu entscheiden.

---

## 2026-10-10 (Lauf C, Zahlen): #451 Katalogzahlen raus, #414 seltenes Gate für die Verszählungs- und div-Zahlen

Zwei Pakete derselben Spur. **C1 (#451, Schritte 1 bis 3):** `doc-count-audit.py` zählt nur noch, was ein XPath zählt (Datenzahlen), die Katalogzahlen (Tests, Tools, Spalten) sind aus Gate und Prosa heraus; PR #561, Squash `641d0ed2b`. **C2 (#414):** `scripts/audit/check-measured-counts.py` hält 28 wörtliche Sätze in vier Dateien (Reader-Kommentare, `korpus.css`, `docs/FEATURES.md`, `docs/TEI-MODEL.md`) gegen die Messung der beiden Zählskripte, die dafür ein maschinenlesbares `measure()` bekamen (gedruckte Ausgabe unverändert, per Diff geprüft). Läuft im eigenen Workflow `measured-counts.yml` (wöchentlich, bei `tei/` und an den gelesenen Dateien), weil ein Lauf rund vier Minuten braucht (263 s, ein Lauf) gegen fünf Sekunden für den Audit.

### Was über den Einzelfall hinausgilt

**(a) Eine Fundstelle ist erst gegatet, wenn ihr Satz in `CLAIMS` steht.** Runde 1 fand drei Zwillingsstellen derselben Zahlen, die ich übersehen hatte (Reader "159 der qualifizierenden divs", FEATURES "discards 1,169", `korpus.css` "1.061 der 1.097"). Der Weg dorthin war der Suchlauf über den ganzen Bestand nach den Zahlen, nicht nach dem Satz.

**(b) Zahlenrand zählt.** Der erste Entwurf suchte den Satz als Teilstring: "500" hätte in "1.500" getroffen. Jetzt hat der Satz an Ziffernrändern eine Grenze, und die Diagnose "Zahl weicht ab" vs. "Anker nicht gefunden" kommt aus einem zweiten Muster mit beliebigen Zahlen.

**(c) Zwei Allaussagen im Text sind Messbedingungen geworden** ("in keinem dieser Fälle", "no further types"); sie bleiben rot, bis jemand den Eintrag ändert.

**(d) Bewusst nicht gegatet:** TEI-MODEL.md:352 (1,406 undatiert, gleich dem Tabellenwert), NLA "38 untypisierte" (Einzeltext, das Gate misst ihn nicht), "WH +466" (historische Diff-Aussage). Ebenso die Datumsstempel neben den Zahlen ("Stand 2026-09-08"): das Gate hält die Zahl, nicht das Datum.

**(e) Lemma-Gesamtzahlen in Kommentaren** sind durch "rund 44.000" ersetzt oder samt Nenner gestrichen (drei Stellen in Runde 1). `lemma-explorer.js:74` trägt weiter "16.713 der rund 44.000"; der Reviewer vermerkt es als Randnotiz. G8 (der Kommentar bei ~874) ist nicht angefasst, er wartet auf B1.

### Messung

Mutationsproben mit gemessenen Werten, jeweils zurückgestellt und die Rücknahme geprüft: JS-Kommentar, FEATURES, TEI-MODEL, CSS, Randfall 159 → 1159, umformulierter Satz → "Anker nicht gefunden". Voller `npm test` (Port 8086, `--workers=2`): `VERDICT: VOLLLAUF GRUEN (473 Tests, 50 Dateien)`. Zwei Review-Runden auf Opus statt Fable (Fable-Limit, G4 in `docs/playbooks/kickoffs/2026-10-10-lauf.md`); Runde 2 ohne Befund.

### Rote Zeilen

Keine. Zwei eigene Zahlen (32 statt 34 Zeilen, 716 statt 715) habe ich vor dem Weiterreichen nachgemessen und in der Folgemeldung richtiggestellt; getragen hat keine etwas, die PR-Texte tragen die gemessenen Werte. Die Nummern 140 bis 144 sind unverbraucht.

### Was zurück an Christian geht

#451 bleibt offen, bis die Koordination Schritt 4 (die Zeile in `CLAUDE.md`) schreibt. #414 bleibt nach dem Merge offen (Bezug, kein Schließen).

## 2026-10-09 (Spur 452): Zuschreibungsstatus für Werkautoren, Corpus Index 4.2.31, Authority Index 1.9.22

Ein Vorgang (#452, im Zusammenhang mit #444) auf dem Zweig `claude/452-zuschreibung`: Autoren eines Werks tragen einen Status (ohne Zusatz anerkannt, `disputed`, `uncertain`, `rejected`) oder die Rolle `adapter`. Betroffen sind fünf Sigel: CR (Bligger von Steinach verworfen), BAX (Anonym als Bearbeiter), HOF und VDH (Stricker allein), RHB (Konrad von Würzburg umstritten, zählt als Autor). Daten, Schema, beide Indizes, API, Leseansicht, Suche und Playground tragen die Unterscheidung; die Anzeigetexte stammen von KZW („umstritten“, „unsicher zugeschrieben“, „verworfen“, „Bearbeiter“, Rubrik „Frühere Zuschreibungen“). Gemessen am Zweigkopf `75e5caf10`: `npm test` mit `VERDICT: VOLLLAUF GRUEN (473 Tests, 50 Dateien)`; fünf Review-Runden des Reviewers, die letzte ohne Befund.

### Was über den Einzelfall hinausgilt

**(a) „Zählender Autor“ ist ein eigener Begriff, kein Feld.** Zählend heißt: weder Bearbeiter noch verworfen. Das Kompatibilitätsfeld `author` bleibt der erste zählende Autor, alle Zuschreibungen stehen in `works[].attributions`. Jede Stelle, die einen Autor als Zeichenkette liest, sieht deshalb nur diesen ersten. Im Korpus betrifft das nach der Messung des Reviewers genau RHB und work_325; die Auswertung der Analysewerkzeuge (Gruppierung, Statistik) liest weiter nur den ersten Namen, eine eigene Autorenzeile im Korpusindex gehört nicht in diesen PR.

**(b) Die Fehlerklasse „Autor als Zeichenkette“ hat drei Runden gebraucht.** Gefunden wurde sie nacheinander in `app.js` (Runde 2), in Dateiliste und Reim-Textfilter des Playgrounds (Runde 3) und im Tippfilter des Textvergleichs (Runde 4). Erst der Sweep in Runde 5 ging vom Eingabefeld rückwärts statt von `text.author` vorwärts und fand nichts mehr. Ein Suchlauf über `text.author` übersieht zusammengesetzte Strings (Beschriftungen, `data-`Attribute); das Eingabefeld ist der bessere Ausgangspunkt.

**(c) Vor dem Push alle Schritte aus `data-integrity.yml` lokal laufen lassen, nicht die Liste aus dem Gedächtnis.** `check-author-refs.py` fehlte in meiner Liste und war in der CI rot; nach dem PR ging es mit `check-doc-inventories.py` (neue Spec und neues Lib-Modul fehlten in den Inventaren) noch einmal so. Wer eine Spec oder ein Modul anlegt, zieht `docs/DEVELOPMENT.md` und `assets/js/lib/README.md` im selben Zug nach. Behoben mit einer Ausnahme für verworfene Zuschreibungen (`0e5f1ab6e`), die die Koordination wegen des Freezes auf diesem Skript freigegeben hat.

**(d) Die Werkesuche zählt Autorfelder fest auf** (`attributionNames(work)[1]`, `[2]`). Bei höchstens zwei zählenden Autoren je Werk (gemessen vom Reviewer) reicht das; bekommt ein Werk einen dritten, findet niemand den, und kein Test merkt es.

### Rote Zeilen

Vier, Nr. 115 bis 118: zweimal die unvollständige Gate-Liste vor dem Push (115 `check-author-refs.py`, 118 `check-doc-inventories.py`, beide erst in der CI rot) und zwei Wiederholungen der Fehlerklasse aus (b), nachdem die Lehre schon im Reviewer-Memory stand.

### Was zurück an Christian geht

Die Abnahme geht nach dem Merge an @wachauer allein, mit der Frage nach HOF und VDH (Stricker allein, der Anonym-Rest in `particDesc` bleibt mit veralteten Werklisten stehen) und der Frage, ob die Analysewerkzeuge alle Zuschreibungen zeigen sollen. Die Reviews liefen ausnahmsweise auf Opus statt Fable (Fable-Limit, Freigabe 09.10.); der erste volle Testlauf lief ohne gesetzten `MHDBDB_TEST_PORT`, also vermutlich auf dem Standardport 8080 statt auf dem zugeteilten 8083; die Koordination hat deshalb einen zweiten verlangt, der mit `MHDBDB_TEST_PORT=8083` auf dem Code-Endstand grün lief (473 Tests, 50 Dateien).

---

## 2026-10-09 (Spur 93): #93, Umzug der Textreihentypologie auf `textreihen/`

Die alte Website `marketext.at/Textreihentypologie` liegt als Unterseite unter `textreihen/`: elf Seiten (Start, About, How To, Visualization & Browser, Use cases, Outreach, Bibliography mit Literatursuche, Download, "Gattungs-Explorer in MHDBDB Next", die zwei Beiträge), erreichbar über einen Footer-Link und eine Kachel auf `hilfe.html`, ohne Menüpunkt. Datenbasis ist der unveränderte SKOS-Stand `86c233f08` (12.06.2023, CC BY 4.0 laut README des Quellrepos), nicht `genres.xml`; der SKOS-Browser zeigt die 618 Kategorien mit 894 `broader`-Aussagen, und eine Kategorie mit mehreren direkten Eltern steht unter jedem (193 von 618, "Beschwörung" unter zwölf). Die Bibliografie (190 Zotero-Einträge) ist statisch gebaut. Zwei Review-Runden, Volllauf grün (466 Tests). Offen: KZW hat nicht beantwortet, ob Logos, Startbild und drei Screenshots übernommen werden dürfen (Kommentar vom 09.10. in #93); der Merge wartet darauf.

### Was über den Einzelfall hinausgilt

**(a) Die Lizenz stand im README, nicht in einer Lizenzdatei.** GitHub zeigte `license: null`, und der Kommentar vom 10.08. in #93 schloss daraus "keine Lizenz". Wer die Rechte eines Repos prüft, liest die README und die Datensätze an anderer Stelle (hier die Hamburger DOI-Einträge, ebenfalls CC BY 4.0), nicht nur das Lizenzfeld.

**(b) Eine Zählung am Dateitext ist keine Zählung der Aussagen.** 881 Zeilen mit `skos:broader`, 894 Aussagen (siehe Fehlerjournal 109). Dasselbe bei Zotero: 205 Items über `/items`, 190 Bibliografieeinträge über `/items/top`; das Skript muss sagen, welchen Endpunkt es holt.

**(c) Die Beispiele einer Anleitung tragen Alternativbezeichnungen, nicht die Vorzugsbezeichnung.** "Dietrichsepik" im How To ist `altLabel` von "Dietrichsepos". Der Browser findet beides; ein Test, der den Titel einer Beispiel-ID aus der Anleitung erwartet, scheitert sonst.

**(d) Ein gieriger Regex im Bauskript hat 190 von 190 Einträgen ein `</div>` mitgegeben, unsichtbar, weil `<main>` kein offenes `<div>` hatte** (Runde 1). Ein Test, der nur Zahlen zählt, merkt das nicht; die Spec prüft jetzt die Zeile.

**(e) Die Mutationsprobe der Linkspec traf beim ersten Versuch beide eingebauten Fehler** (kaputter Anker, fehlendes Bild); damit ist belegt, dass sie Anker und Bildquellen wirklich prüft und nicht nur Seiten abruft.

**(f) Die alte Website hatte zwei eigene Fehler**, die beim Umzug nicht mitgewandert sind: einen internen Link auf `dokument.html#MHDBDB` (Seite existiert nicht) und den Platzhalter "#DOI (wird nachgeliefert)". Beides steht in `textreihen/README.md`.

### Rote Zeilen

Eine, Nr. 109: die Zeilenzahl der Turtle-Datei als Zahl der Aussagen gemeldet.

### Was zurück an Christian geht

Nichts, was er entscheiden müsste. Für KZW (und zuerst Julia, einfache Abnahme) nach dem Merge: die drei Bildgruppen (Antwort auf den Kommentar in #93 steht aus), und die Prüfschritte der Unterseite. In `CLAUDE.md` fehlt `textreihen/` im Verzeichnisbaum (Inbox an die Koordination).

---

## 2026-10-04 (Koordination): Lauf vom 02.10. abgeschlossen, Parzival-Bücher und „Strophe“ auf `main`

Vier Vorgänge (#378, #370 Punkt 2, #358, #228) in drei Spuren, neun PRs gemergt; die Tabelle mit den Commits steht im Laufplan unter „Abnahme“. Die lokale Koordination hat am 03.10. an ihrem Fable-Limit an eine Cloud-Session übergeben, die #523 (A3) und #519 (B2) gemergt hat. Damit trägt der Parzival die 16 Bücher im TEI und zeigt sie als „Buch N“, die Dreißiger in PZ und WH heißen „Strophe N“. Bei KZW liegen jetzt die Prüfseite zu #370, der Mur-Vorschlag in #228 und die Abnahmen von #378, #228 und #358. Der `fable-reviewer` lief in der Cloud-Session ohne Limit; die Übergabe hat also getragen.

### Lehren

**(a) Vor jedem Merge die Dateiliste gegen die Zuteilung halten.** Beim ersten Merge (#517) vergessen, `assets/js/app.js` ging ungemeldet mit; ab da Teil der Merge-Prüfung, bei #523 und #519 gegen §3 gehalten.

**(b) „Von Fable geprüft“ heißt: Kopf der Runde gleich Kopf des Merges, sonst den Diff dazwischen nennen.** Bei #523 lag zwischen Runde 1 und dem Merge-Kopf ein eingemergter `main`-Stand; erst die Trennung zwischen eigenem Diff und Merge machte sichtbar, dass sich nur das Einspielskript geändert hatte.

**(c) Der Review-Bot läuft auf Entwürfen nicht** (`claude-code-review.yml` Z. 22). Ein Entwurf mit grüner CI hat deshalb keinen Bot-Kommentar, nicht einen ohne Befund.

**(d) Ein Volllauf in einer Cloud-Session braucht zwei Handgriffe, die das Repo nicht mitbringt:** Playwright 1.55.1 erwartet den Chromium-Build 1193, der Container hat 1194, und `python3.13` hat kein `lxml`. Beides führt zu roten Tests, die nichts über den Code sagen (beim ersten Lauf 401 von 427). Wer einen Volllauf in der Cloud zählt, prüft vorher Browser-Build und `lxml`.

### Rote Zeilen

Eine, Nr. 85: eine Testursache als belegt in einen Merge-Commit und einen Issue-Kommentar geschrieben, gestützt auf eine Probe, die etwas anderes gemessen hatte.

### Was zurück an Christian geht

Die drei nicht blockierenden Test- und Kommentarlücken aus der Abnahme sind am selben Tag in #524 geschlossen. Dabei ist die Lehre aus dem B2-Eintrag vom 02.10. („ein Test, der ein Wort aus den Daten erwartet, muss dem Datenstand folgen“) zurückgenommen worden: sie galt nur, solange A3 noch ausstand. Seit WH die Kennzeichnung trägt, erwartet der Test fest „Strophe 77“, denn ein Test, der dem Datenstand folgt, meldet auch dessen Rückschritt nicht. Die Ursache des einen roten Wörterbuchnetz-Tests auf #523 bleibt ungeklärt.

## 2026-10-02 (Spur B, B2): #358, Dreißiger heißen "Strophe", Parzival-Bücher "Buch N"

KZW hat am 11.09. entschieden: im Parzival heißen die Bücher "Buch I" usw., die Dreißiger "Strophe" statt "Kapitel". Umgesetzt in der Leseansicht: `<div type="chapter" subtype="dreissiger">` wird als "Strophe N" beschriftet, `<milestone unit="book" n="II"/>` als Überschrift "Buch II" an seiner Stelle, mit eigener CSS-Regel `.section-head.book-heading` (Ä3). `type` bleibt `chapter`, damit Verszählungs-Rücksetzung und Deep-Links über `verseId` unberührt greifen. Die Kodierung selbst baut Spur A (A3); B2 wird erst danach gemergt, bis dahin prüft die Spec mit einem Testfragment.

### Was über den Einzelfall hinausgilt

**Die Messung "welche Stellen sagen Kapitel" hat genau eine Stelle ergeben.** Grep über JS, HTML und CSS: nur `divLabels` in `tei-text-reader.js` beschriftet `chapter`; kein KWIC, kein Playground, kein Export. Die übrigen HTML-Treffer dokumentieren das TEI-Enum. Das ist der Grund, warum die Umbenennung ein Einzeiler im Reader ist und kein Querschnitt.

**Ein Test, der ein Wort aus den Daten erwartet, muss dem Datenstand folgen.** `reading-view.spec.js` erwartete für WH fest "Kapitel 77" und wäre mit A3 rot geworden. Er liest jetzt `subtype` aus dem TEI und erwartet entsprechend "Strophe 77" oder "Kapitel 77", damit er vor und nach der Umkodierung dasselbe prüft.

**Die Position eines milestone ist eine Darstellungsfrage, nicht nur eine Kodierungsfrage.** Steht ein Buchmilestone laut Laufplan als erstes Kind eines Dreißiger-div, rendert er unter dem Label "Strophe N". Das hat die Fable-Runde 1 als Randbemerkung gefunden; behoben ist es im Reader (der milestone wird vor das Label gezogen, `state.hoisted` verhindert die Doppelung). Der Hoist hängt an `firstElementChild`: ein künftiges `<pb>` vor dem milestone würde ihn wieder unter das Label setzen, heute 0 Fälle (PZ 827 div, WH 467, alle mit `<l>` als erstem Kind).

### Rote Zeilen

Eine, Nr. 96: eine erfundene Stellenangabe ("Buch V bei 4,1") in einem Code-Kommentar.

### Was zurück an Christian geht

Nichts aus B2. Offen bis A3 und C2: die tatsächlichen Buchgrenzen (Laufplan nennt drei, II 58,27, III 116,5, IV 179,13, als ungeprüft); der PZ-Test in `dreissiger-buecher.spec.js` ist bis A3 übersprungen und wird danach entfernt (0 skipped auf dem Merge-Stand).

## 2026-10-02: #358 TEI, Dreißiger-subtype und Buchgrenzen des Parzival (Spur A3 des Laufs vom 02.10.)

PZ und WH tragen die Gliederung jetzt im Markup: `subtype="dreissiger"` an allen 827 (PZ) und 467 (WH) `div type="chapter"`, dazu in PZ 16 `<milestone unit="book" n="I"/>` bis `XVI`. Grenzen aus `ingest/parzival-buecher/grenzen.csv` (C2), Einspielskript `scripts/ingest/parzival-358/pz-wh-struktur.py`, Schema um beides erweitert (`div.subtype` geschlossen, kein GAP; `milestone` nur als Kind von `div`).

### Was über den Einzelfall hinausgilt

**Gemessen vor dem Schreiben, nicht angenommen.** In beiden Dateien ist jedes `div` ein `chapter` ohne weiteres Attribut außer `@n` (lückenlos 1..N), die Kinder sind nur `<l>`, es gibt kein `lg` und kein `milestone`; deshalb durfte `subtype` an jedes `div`. Alle 16 Grenzen sind `<l>` direkt unter dem chapter-div; II, III und IV liegen mitten im Dreißiger (58,27, 116,5, 179,13), die anderen 13 am Divanfang.

**„Dreißiger" ist die Gliederungseinheit, keine Verszahl.** Von 827 PZ-Dreißigern haben 826 genau 30 Verse, Nr. 257 hat 32 (HUGO-Verszählung). Von 467 in WH haben 465 30 Verse, Nr. 57 hat 28, Nr. 467 (unvollendetes Ende) 24. Die Koordination hat die Abweichungen als Editionsbefund akzeptiert, der Schema-Kommentar sagt es ausdrücklich.

**Kein Index-Bump.** Beide Indexe sind nach der Änderung auf sauberem Baum byte-identisch neu gebaut worden (`git status --short` leer). Der Korpus-Index liest `<w>` und `<l>` in Dokumentordnung (`build-corpus-index.py`, iterwalk), keines der beiden ändert sich; Index 4.2.25 ist deshalb zurückgegeben. Konsumenten gemessen: der Reader gibt für `milestone` mit `@unit != "verse"` nichts aus (Anzeige liegt bei B2, #519), KWIC, Reimwörterbuch und Positionszählung laufen über `w` und `lb`/`pb`, `build-api.py` liest keine TEI, kein Code vergleicht das Attributset eines `div`.

**Ein Docstring versprach einen Haltepunkt, den es nicht gab.** Das Skript nannte als Haltepunkt eine nicht eindeutig zu findende `<l>`-Startzeile; die Prüfung am Ergebnis verglich aber nur `div/@n` und `l/@n`, nicht die `erste_wort_id`. Gefunden hat es der Fable-Reviewer per Mutationsprobe (ein zweites `<l n="27">` in div 58 lief durch). Behoben: die Ergebnisprüfung hält das erste `<w>` der Zeile nach dem `milestone` gegen die Wort-ID der CSV, und die Probe auf einer Kopie des Basisstands bricht jetzt ab; derselbe Lauf auf der Basis reproduziert beide Dateien byte-identisch. Die Daten waren nie betroffen (0 doppelte `l/@n` in einem `div`).

**Das Schema bleibt eng, die Tabellenzeile sagt es jetzt.** `docs/DATA-MODEL.md` (Zeile zum Kapitelapparat, #66) schreibt `<milestone unit="chapter" n="N"/>` inline im Textfluss vor; das Schema erlaubt `milestone` nur als Kind von `div` mit `@unit="book"`. Im Korpus `tei/` gibt es heute außer den 16 neuen keine `milestone` (`unit="chapter"` steht nur im WZB-Ingest-Skript `scripts/ingest/wzb/wzb-structural-fix.py`), ein künftiger Ingest nach der Zeile fiele aber im Stage-2-Gate durch. Entschieden von der Koordination (G5 des Laufplans): die Werteliste wird nicht auf Vorrat geöffnet, weil keine Daten es verlangen; die Zeile trägt einen Satz, dass der erste Ingest, der `unit="chapter"` im Textfluss braucht, `schema/mhdbdb.rnc` in einem eigenen PR erweitert. #66 selbst bleibt unberührt.

### Rote Zeilen

Keine.

### Was zurück an Christian geht

Nichts aus A3.

## 2026-10-02: #370 Punkt 2 eingespielt, Authority-Index 1.9.19 (Spur A2 des Laufs vom 02.10.)

Die in C1 entschiedenen WZB-Paare sind in `tei/WZB.tei.xml` eingespielt: 486 Paare (461 ANLEGEN, 25 VERKNUEPFEN), 4.794 Tokens. Die 461 ANLEGEN-Paare tragen 4.765 Tokens und haben neue Typen `type_372393` bis `type_372853` bekommen; die 25 VERKNUEPFEN-Paare tragen 29 Tokens auf bestehenden Typen. Nicht angefasst: PRUEFSEITE (29 Paare, 338 Tokens) und NICHT_ANLEGEN (43 Paare, 260 Tokens). Einspielskript `scripts/ingest/wzb/wzb-corresp-punkt2.py` mit Batch-Prüfung vor dem Schreiben, Provenienz je Token in `ingest/wzb/370-corresp/punkt2-zuordnung.csv`.

### Was über den Einzelfall hinausgilt

**Die Ratsche stimmt, die zwei Zahlen waren zwei Mengen.** 5.273 ist die CSV-Zählung der Hauptliste (4.675 ANLEGEN + 598 PRUEFSEITE/NICHT_ANLEGEN), 5.392 der Stand der WZB: 5.273 + 10 Tokens, die seit der CSV-Zählung in 8 bereits entschiedenen Paaren dazukamen (`ŏ`-Schreibungen, `et`, u. a.), + 109 aus dem Nachtrag. Entschieden wird je Paar, deshalb gehen alle heutigen Tokens eines entschiedenen Paars mit. Baseline neu 600 (WZB 598, EKL 2).

**Korpus-Index byte-identisch, Authority-Index nicht.** `build-corpus-index.py` liest `@corresp` nur am `msIdentifier`, nie am `<w>`; auch nach der Änderung der projectDesc-Quoten bleibt `data/corpus-index.json.gz` unverändert (Kommando: Build auf sauberem Baum, danach `git status --short` leer). Der Authority-Index trägt dagegen 302 neue Formen (233.962 auf 234.264) und 12 neue Kandidatenlisten (4.961 auf 4.973), also 1.9.19.

**Zehn Zuordnungen schlagen um, und das ist Vorschrift B, kein Umhängen.** Je ein neu geprägter Typ hebt die Tokenzahl einer Form unter dem neuen Lemma über die des bisherigen Spitzenreiters (boeze, geheisse, gepflaget, kochen, reisse, steigen, tir, vassen, verrens, weicz). Kein bestehender Typ wurde umgehängt (`extract-variants`: lemma assignment changed 0, form text changed 0). Quittung im Flip-Gate für 1.9.18 auf 1.9.19, genau 10; die Tabelle mit Tokens je Kandidat steht im PR.

**Was ein Gate nicht deckt, deckt auch eine Gegenzählung nicht.** Der Fable-Reviewer fand drei Nachbarzahlen, die der Lifecycle nicht gatet: die Kandidatenlisten- und Mehrfachzahlen in CONTRACTS und DATA-MODEL (4.961/4.979 auf 4.973/4.991), die Mengenangabe in der Zeile darunter, und die `@corresp`-Quote in der projectDesc der WZB (91,8 % auf 95,0 % der 149.165 `<w>`, 96,2 % auf 99,6 % der 142.360 lemmatisierten). Alle vor dem Push behoben; die Quote ist die Folge der eigentlichen Änderung und stand im Diff nicht.

### Rote Zeilen

Keine.

### Was zurück an Christian geht

Die 10 Umklappungen (Tabelle im PR) zur Abnahme durch KZW; `tir` und `kochen` sind die Grenzfälle. Offen bleiben die 29 PRUEFSEITE-Paare auf der Prüfseite.

## 2026-10-02: #378 gebaut, Authority-Index 1.9.18 (Spur A1 des Laufs vom 02.10.)

ADR-021 ist umgesetzt: Eine mehrdeutige normalisierte Schreibform liefert in Stufe 2 alle Kandidaten, geordnet nach Vorschrift B (Korpus-Tokens dieser Form unter dem Lemma), statt first-wins. Dazu das Gate gegen kippende Zuordnungen und, für Spur B (#228), das Feld `lemma.noCorpus`. Gemessen und gebaut wie folgt.

**Frequenzquelle `form/@n` in `variants.xml`** (`extract-variants.py` schreibt es, Schema Pflichtattribut). Preis: jede Korpusänderung an einem `@corresp`-tragenden `<w>` ändert nun auch `variants.xml`, eine Zeile je Typ (drei mutierte Tokens gaben `token count n changed: 3`). Die Erstregeneration änderte alle 256.497 Zeilen und sonst nichts. **Indexformat additiv:** `variants[form]` bleibt eine ID, jetzt der erste Kandidat; `variantCandidates[form]` nur bei mehreren (4.961 Formen). Index 1.9.18, 2.063 bestehende Zuordnungen klappen gegen 1.9.17 um.

### Was über den Einzelfall hinausgilt

**Die Ticketzahlen haben gehalten, die Zählweise ist jetzt festgelegt.** Heute 4.979 umstrittene Formen (Ticket 31.08.: 4.972), nach Vorschrift B folgt first-wins bei 2.065 nicht dem häufigsten (2.064), davon 1.330 erreichbar (1.328). Gezählt wird nach Tokenform, nicht nach Variantentyp; die `@n`-Reihenfolge stimmt bei allen 4.979 Formen mit einer direkt am Korpus gezählten Vorschrift B überein, und der Fable-Reviewer hat dasselbe unabhängig gemessen.

**Hängende Lemma-Verweise (#115) sind Kandidaten ohne Gegenstück.** Die erste Fassung ließ 24 Kandidatenlisten Lemma-IDs ohne Eintrag in `lexicon.xml` tragen; `halap` und `chana` wären darauf umgeklappt. Gefunden hat es die neue Spec, bevor irgendetwas gepusht war. Seither scheiden solche Kandidaten aus, solange die Form ein bekanntes Lemma hat (4.979 mehrfach beanspruchte Formen, 4.961 mit Kandidatenliste, 2.063 statt 2.065 Umklappungen). Kopplung, die bleibt: Legt #115 später ein dort fehlendes Lemma an, kann die Zuordnung umklappen, und das Gate verlangt eine Quittung für einen Nebeneffekt eines Lexikon-Commits.

**Das Gate quittiert genau ein Versionspaar mit genau einer Zahl.** `check-variants-flips.py` ist rot bei jeder umgeklappten Form, außer `scripts/audit/variants-flips-ack.json` nennt Von- und Nach-Version und die exakte Anzahl; beim nächsten Bump ist die Quittung von selbst wirkungslos. Mutationsproben: unverändert grün, Einzelform umgehängt rot, Invariante `variants[form] = variantCandidates[form][0]` verletzt rot, Quittung mit 2.064 statt 2.063 rot. Die `.gitignore` schließt `scripts/audit/*.json` aus, die Quittung ist wie die Baselines mit `git add -f` eingetragen.

**`noCorpus` kommt aus dem Korpus-Index, nicht aus `variants.xml`.** Quelle (a) hätte 1.288 geliefert (drei Lemmata sind nur über Tokens ohne `@corresp` belegt), (b) trifft die 1.285 von Spur B. Der Authority-Build liest damit `data/corpus-index.json.gz` und bricht bei fehlender oder versionsfremder Datei ab; die CI-Reihenfolge (Korpus vor Authority) stimmte schon.

**Die Beispieldatei war gegen das eigene neue Schema ungültig**, und kein Gate prüft die Beispiele; der Reviewer fand es, nicht ein Werkzeug. Korrigiert und mit lxml-RelaxNG validiert (True); `hilfe-schema.html` lädt die Datei und zeigt sie jetzt richtig.

**Offen, bei Spur B:** Die Form-Chips auf der Lemmaseite und im Suchpanel invertieren `variants` und führen eine Form nur unter ihrem ersten Kandidaten, wie vorher unter first-wins.

### Rote Zeilen

Keine.

### Was zurück an Christian geht

Nichts aus A1. Für A2 steht die Prüfung der Ratsche in `corresp-coverage-baseline.json` aus (Spur C meldet heute 5.392 statt 5.273 Tokens ohne `@corresp`).

## 2026-10-02 (Spur B, B1): #228, reine Wortbestandteile im Wörterbuch und auf der Lemmaseite

KZW hat am 01.10. entschieden: die 273 Einträge ohne Korpusbeleg, die eine andere Etymologie als Bestandteil nennt, tragen in Wörterbuch und Lemmaseite „Als Wortbestandteil erfasst; kein eigenständiger Beleg im aktuellen Korpus.“; der Status wird abgeleitet, nicht gespeichert, kein `entry/@type`. Umgesetzt: eine gemeinsame Regel in `assets/js/lib/component-only.js` (`noCorpus === true` am Lemma und Nennung in `etymology[].lemmaRef` eines anderen Lemmas), im Wörterbuch die Kurzmarke „nur als Wortbestandteil“ mit dem vollen Satz als Tooltip, auf der Lemmaseite der volle Satz unter dem Titelblock, dazu Hilfetext und `component-only.spec.js`. Gemergt wird erst nach A1, weil `noCorpus` im Authority-Index 1.9.17 noch nicht steht.

### Was über den Einzelfall hinausgilt

**Die Ableitung brauchte ein Indexfeld, und das hat die erste Messung entschieden, nicht das Raten.** Die Bestandteilsverweise standen längst im Authority-Index (`etymology[].lemmaRef`, nur `seg type="component"`), die Belegzahl nicht; sie steht nur im 40-MB-Corpus-Index, den die Lemmaseite lädt und das Wörterbuch nicht laden darf. Gemessen am Index 1.9.17 / 4.2.24: 1.285 Einträge ohne Beleg, davon 273 als Bestandteil genannt, *Mur* dabei. Beide Zahlen aus #228 reproduzierten. Spur A baut `noCorpus: true` in den ersten Bump.

**Eine Spec, die ein noch nicht gebautes Feld braucht, mockt den Index.** `component-only.spec.js` ersetzt `authority-index.json.gz` per Route durch eine Kopie mit `noCorpus` an drei Fällen: *Mur* (Hinweis), ein ungenanntes Lemma (keiner), *ouwe* (genannt, aber belegt: keiner). Sie läuft damit vor A1; der dritte Test bindet die Sichtbarkeit an das Feld im echten Index und kippt nach A1 nur, wenn *Mur* es nicht bekommt, dann wäre der A1-Build der Befund.

**Die Kennzeichnung sagt nichts über die Zerlegung.** Das war KZWs Bedingung, und die Spec prüft es am Wortlaut (kein „geprüft“, „bestätigt“, „korrekt“, „richtig“). Dass Murstetten überhaupt auf den Fluss zurückgeht, ist offen (C3).

### Rote Zeilen

Eine, Nr. 95: einen Reviewerbefund mit derselben fehlerhaften Messung „bestätigt“, mit der er selbst entstanden war.

### Was zurück an Christian geht

Nichts aus B1. Offen für die Hilfe: `hilfe-korpussuche.html` Z. 445 f. nennt für Registereinträge nur Lemma und Wortart-Kürzel; die Marke steht stattdessen in `hilfe-daten.html`. Ein Halbsatz dort wäre nach A1 stimmiger, ist aber nicht blockierend.

## 2026-10-01: Sechs PRs, und die CI ist um ein Viertel schneller, nicht um die Hälfte

Gemergt: #508 (#485, Lindas Beschreibung der Figurenbezeichnungen), #509 (#459, sieben WZB-Tokens auf *lende*, Index 4.2.24 / 1.9.17), #510 (#495, Gattungen im TEI-Kopf gegen `works.xml`, neues Gate `check-header-genres.py`), #511 und #512 (Laufzeit), #513 (#485, Beispielformen *Paris* / *der künic* nach Lindas Freigabe). #459 geschlossen.

**Laufzeit.** `validate-corpus.py` läuft auf `--jobs` Workern (#511), drei Kopf-Prüfungen lesen per `corpus_files.tei_header` nur den `teiHeader`, `check-authority-cross-refs.py` und `build-begriffshilfe.py` scannen parallel, `build-corpus-index.py` parst jede Datei einmal statt zweimal (#512); jede Ausgabe ist gegen den alten Stand byte-identisch oder bis auf die Worker-Zeile gleich gemessen. Lokal fällt die Validierung von 393 bis 608 s auf 64 bis 68 s. **In CI fällt der Job `validate` nur von 748 auf 545 s** (Validierungsschritt 329 → 216 s), weil der Runner vier Kerne hat. Der größte Einzelposten ist danach der Checkout.

**Der Checkout ist kein Hebel, und das ist gemessen, nicht vermutet.** Je 8 Läufe von `data-integrity`, `no-cdn-check` und `file-size-check`: die Dauer springt in allen drei zwischen rund 80 s und 130 bis 160 s, auch bei `fetch-depth: 1`; davon gut 60 s Download, gut 20 s Auspacken. Alle drei Workflows brauchen die Dateiinhalte (`check-file-sizes.py` liest Größen aus `git ls-tree -l`, `doc-count-audit` zählt `tei/`). Deshalb keine Änderung, und aus demselben Grund kein Aufteilen von `validate` in parallele Jobs: jeder brächte seinen eigenen Checkout mit. gzip bleibt auf Stufe 9 (Entscheidung chsteiner): zehn Sekunden Build gegen einen größeren Download für alle Leser.

**Was eine Suche nach weiteren Hebeln nebenbei gefunden hat, betrifft Nutzer und nicht die Suite:** der Playground lädt beim Start den Korpus-Index, bevor der Router läuft (`playground-main.js:147-156`), auch für Routen, die ihn nicht brauchen. Notiert in #488, nicht umgesetzt.

**Audit-Skripte sind cwd-relativ.** Aus dem Hauptbaum gegen einen Worktree gestartet, messen sie den Hauptbaum; zweimal an diesem Tag hat das ein falsches Ergebnis geliefert, beide Male vor dem Push gefangen. Im Worktree heißt der Aufruf `env -C <worktree> python scripts/audit/...`.

Antworten des Tages: @wachauer zu #228 (Mur bleibt vorerst, Zuordnung erst an Quellen prüfen; die 273 reinen Bestandteile werden aus Belegen und Bestandteilsverweisen abgeleitet gekennzeichnet, kein `entry/@type`), @lindabeutel zu #485. Labels entsprechend nachgezogen.

## Verdichtete Historie

Hochrangiger Trace der Einträge 2025-02 bis 2026-09-24 (bis 2026-09-07 waren es 131 verdichtete Einträge, heute 153). Volltext aller 153 verdichteten Einträge in `journal-archive.md`.

**2025-02 (Phase 0 + #42):** Stabilisierung vor #42 – Wenzelsbibel (652k Zeilen) auf `feature/wenzelsbibel-ingest`, `assets/{css,js,images}` konsolidiert, Playwright 2→36 grün / 25 skipped (#43). #42 Persistent Lemma Pages: Wörterbuchnetz-IDs schon deckungsgleich (`lid=879` = `lemma_879`), Clean URLs `/lemma/879` + 404.html-Redirect-Trick für GitHub Pages. Savepoints `4562c08`, `6849758`, `e16306d`, `5154d04`.

**2026-02 (Triage + Provenienz):** #44-Triage (23 Issues, 11 Labels; 13/23 Daten/TEI). #21 „Konzepte"→„Begriffe", #46 Lemma-Suche in Multi-Lemma gemerged, #45-API Hybrid-File-Strategie beschlossen, #36-40 Provenienz-Modell ADR-012 (flaches `<listBibl>` + `<bibl type="digitalIntermediary">`). #49-Konvention: Health-Check-Reports als Issue-Comments, keine `.md`.

**2026-04 (#32 TEI Model Consolidation – die große Migration):** 0/100 Files gegen tei_all.rng valide (nur `@meaningRef`+`@wordRef` non-standard; `@lemmaRef` IST Standard). 15M+ Transformationen über 675 Files: `@meaningRef`→`@ana` (5.9M), `@wordRef`→`@corresp` (7.5M), `seg`→`pc` (1.4M), `l`→`lb` in 18 Prosa-Files. Merge PR #69 (Korpus) + #71 (Authority); Deep-Schema-Audit fixte 11 Gaps – Root Cause: `div` ist RNC-Keyword → `tei.div` (brach RNC→RNG). 666/666 valid; Performance-Fix `tree.xpath()` O(n²) → `iter()` Clark-Notation; Branch-Protection auf `main`. WZB-Pipeline (#34/#66): Phase 1b Lemma 91,6 %, Phase 2 POS 95,5 % (Tagset ART→DET, CNJ→CCNJ/SCNJ/ADV), Phase 3 Paratext.

**2026-04-14–16 (Schema-Hardening + Frontend-Sprint):** #83 Editor-Attribution (`contributors.xml`, 51 Personen + 2 Orgs); #32-followup 16/17 + Konvention „Daten vor Schema". **PL1-Validierungs-Pathologie war ein `<p>` mit 404k Direktkindern, nicht die Größe**; nested `<hi>` über 143 Files geflattet; Validierung 830s→493s. **Mishap `8b5d0e6ac`: `git add -A` zog Kollegen-Files mit → CLAUDE.md-Git-Regel + Memory.** Frontend: #31 LINECODE.md, #56 Similar Lemmata, #48 Hash-Router, #17 Reader View (43k unstyled Compound-`@rend` gefixt, 128/128).

**2026-05-07/08 (#32-followup fertig + ARITHMETIC + PD-001):** #32-followup 17/17. #68-Guide-Architektur (user-facing HTML deutsch ≠ LLM-Docs englisch). WZB-Reorg → `scripts/ingest/wzb/`. **PD-001 „Mittelweg" (KZW+Christian): TEI-P5-Standardelemente + 24 `<div>/@type` optional ins Hauptschema; ADR-013-Ausnahme nested `<hi>` wieder erlaubt; `ingest/<sigle>/`-Konvention.** WZB live in beiden Indexen; **#94 Authority-Cache-Bug gefixt (selbstreferenzieller Versionsvergleich).**

**2026-05-11 (sechs Parallel-Sessions):** Playground Release 1 (#87-90 Wortfrequenz/Text-Statistiken/Lemma-Verteilung), #20 Lesbarkeit, #96 Reader-Download, #26 pb-Insertion (1293 `<pb>` über 14 Files, `795670240`), #78 `hilfe-schema.html` + Prism gevendort, #79 closed (5 Hilfe-Seiten), #47.1/.2 + #86-Barrierefreiheit-Draft, KZW-Loop #102/#103/#85. **`docs/data/linecode-templates.csv` (665 Templates) als kanonische Quelle – Lehre: Templates nie aus Daten ableiten.** JOURNAL 937→458 komprimiert.

**2026-05-12 (Julia + Playground-Wave):** #73 Lemma-Linking MWB+Lexer via Wörterbuchnetz-API (`dcbee3479`; Julias statischer Link war POST-only/defekt), #101 Reading-View-Render-Policy (Julia), #105 Authority-Counter 7→8, **#47.3 Versposition-Suche – Corpus-Index v4.0.1→v4.1.0 mit `lineStarts[]`/`lineEnds[]` (1,36M `<l>`)**, #47 R2 Begriffs-Verteilung, #47-Umbrella closed (#107/#108/#109 ausgelagert). Index-Versions-Drift strukturell gelöst (`check-index-versions.py` + CI + Memory, drei Stellen). #23 Stanza-Bulk (93 Texte, 11.090 `<lg>`, v4.1.1). Concept-Distribution-Perf-Patch 2747ms→60-200ms (MessageChannel-Chunking, nicht `setTimeout(0)`).

**2026-05-14/15/16 (Playground-Abschluss + Audits):** #112/#108/#107/#113 live (Verse-Click-Highlight, Textvergleich, Kookkurrenz-Ranking, Autocomplete), #110 WVV-Stanza, #104 Sigle-Gruppierung (Empfehlung: Titel statt Merge), #81 closed. **Lehre `Closes`-Trailer nur bei vollständig fertig** (#110-Reopen). Audit-driven Preparation als Pattern; Autocomplete-Helper zentralisiert.

**2026-05-28 (Großtag):** #113-Followup (`concepts.xml` Alternative-Terms vom Primär getrennt, Last-Wins-Bug; Authority-Index v1.3.0, `f7c8592c2`), #114 Tabellenansicht (Spec+Plan → Subagent-driven 11 Tasks/13 Commits), **CI `index-version-check` Timeout 2→10 min (war seit 05-12 still disabled)**, `.md`-Vereinheitlichung (9 Renames + 226 Cross-Refs), Single-Source Index-Versionen (TEI-MODEL §11). **Authority-Cross-Ref-Audit: 226.863 unresolved Refs (225.886 auf variants.xml) → #115; pb-Backlog 606 Texte → #116.**

**2026-05-29 (Authority-Drift Root Cause):** Repo ist alleiniger Master (transformation→active). Cross-Ref unresolved 226.863→977. **`variants.xml` ist korpus-abgeleitet und war stale (64.287 Formen fehlten); neuer Generator `extract-variants.py` → 192.472→256.759 Formen, Authority-Index v1.3.0→v1.4.0.** Negative type-IDs = Interpunktion, totes `@corresp` gedroppt (14.895 über 296 Files). Cross-Ref-Audit als CI-Gate, Data-Change-Lifecycle in Docs. Savepoints `0867a370f`, `e21d84bd6`.

**2026-06-01/02/03 (Site-Chrome + Paritätstests):** Site-Chrome-Refactor gemerged (`2e8d48d95`) – build-injizierte Nav/Footer (`includes/` + `build-pages.py`), #8 Mobile-Menü zentralisiert, `clearSiteData` delete-by-name. #130 Lemma-Match zentralisiert (`lemma-match.js`, §B.1 token-exakt), #131 Position-Counting-Paritätstest (§B; Leer-`<w>` JS→Python angeglichen, `7491e97b3`). Zwei Health-Checks; Doc-Schuld-Lehre (Build-Pipeline-Erweiterungen gehören in DEVELOPMENT+ARCHITECTURE).

**2026-06-05/09 (Health-Check + Re-Triage):** Multi-Agent-Check (103 Agenten): Doku hing Playground-Wachstum hinterher, ~24 Drifts gefixt, fabrizierte Worked-Examples korrigiert; **8 Blind-Spots, 1 blocking → #132 (Ingest-Verfahren in Stable-Doc), #133.** #44-Re-Triage (37 Issues): kein Bewertungs-, sondern Umsetzungs-Rückstand; #30/#34/#73 closed, #138/#139 angelegt. #53/#137/#135 geshippt.

**2026-06-10/11/12 (Zenodo + #59 + #117 + #125 + #138):** #91 Zenodo-DOI live (Concept `10.5281/zenodo.20627656`, v1.0.0 `…657`); Git-Tag als SSoT für Version (`41a71188a`). #59 Naming-Explorer (`naming-index.json.gz`, 10.506 Records) + ROL/TRO-Deep-Links, #117 Wörterbuch A–Z, #132 Ingest-Verfahren nach DATA-MODEL, #129 KWIC, #128/#23 closed. **#125 deterministische Index-Builds + CI-Freshness-Gate** (`data-integrity.yml`, byte-identische Rebuilds, `requirements.txt`-Pins; Corpus v4.1.4 / Authority v1.4.1, Merge `789708322`). #138 div-/lg-Wrapper (HUG/MBS), #121 Dropdown-Disambig, #136 Text-Statistiken-Auswahl.

**2026-06-17 (vier Sessions + Scorecard):** #45 Statische JSON-API gemerged (PR #150); tei_all.rng ins Repo committet statt CI-Download von tei-c.org (Ausfall-Blocker), xml-model-PIs repo-weit aufs lokale Schema (`559fd3163`). #44-Matrix-Drift korrigiert (7 geschlossene standen als aktiv); #138 HUG-Strophen geshippt (`9c9b78e83`, 814 `<lg>`, Index byte-identisch); dabei #151 entdeckt: TEI-Reader-Cache mit 30-Tage-TTL ohne Inhalts-Invalidierung. README-Drift-Audit 65 Findings (`e7f6d58f6`); **POS-TAGSET.md als SSoT herausgezogen** (`7e8ae95a2`, INDEX-Count 14→15). 47-Agent-Health-Check: 0 blocking, Algorithmus-/XPath-Checks konform, ~24 Count-Drifts gefixt (`54e6d64d0`) → Action-Item #152. **#124 cookieloses Matomo deployed** (`7abbf7672`): build-injizierte MATOMO-Region (`includes/_matomo.html`) + localStorage-Opt-out, weil das Uni-Opt-out-iframe extern HTTP 403 liefert.

**2026-07-02 (Fünf-PR-Welle):** #151 gefixt: Conditional-GET-Revalidierung (ETag/304) statt Deploy-Invalidierung (`4e0208f`); #143 `l`→`lb` für APO/HMT/HH (3.049) + HH-Genre-Fix + APO-Gattung nach Terrahe (Corpus v4.1.5, Authority v1.4.3); **pako/dexie vendored** (`ce34c81`, null Runtime-CDN-Abhängigkeiten). #106 Reim-Wörterbuch (10. Werkzeug, `lineEnds[]`-Scan, Suffix-Heuristik) + #114-Followups (Gesamtzeile, Types + MWB/Lexer-Links, Keyness-Log-Likelihood; Referenzkorpus = alle 667 Texte, auswahlunabhängig); Review härtete `escapeHtml` (Quote-Breakout) und zentralisierte den Wörterbuchnetz-Client (`assets/js/lib/woerterbuchnetz.js`). #152/#154 Daten-Drift-Gates in data-integrity.yml: lexicon-ID-Set-Ratsche (`lexicon-baseline.json`, nach Review statt Zahlenpaar), naming-Gates inkl. TOCTOU-Fix (Fetch unter resolviertem SHA), Versions-Bump-Gate. **#115 Kategorie-A-Backfill: 125 Stubs, 43.754→43.879 Lemmata** (dangling 977→396, 349→109 IDs), Authority v1.4.4. Lehren: Roundtrip-Skripte brauchen `newline=''` (CRLF hätte die 31-MB-lexicon.xml still umgeschrieben); doc-count-audit-50er-Kappung entfernt (war für Bulk-Sprünge blind).

**2026-07-08/09 (autonome Doppel-Session + Health-Check):** Issue-Session: 12 PRs #174–#185 (u. a. posAll[] v1.6.0 für 10.171 Multi-POS-Lemmata, AK-Excerpt-Banner via `biblScope unit="verse"`, drei latente §B-Paritäts-Drifts geschlossen) mit neuem Review-Triage-Pattern (Bot-Findings erst prüfen, dann fixen; 2 False Positives). Merge-Session: alle 13 PRs auf main, 13 Issues geschlossen, Live-Smoke grün. **GitHub-Mechanik-Lehren (je 2× reproduziert):** `gh pr merge --delete-branch` schließt gestackte PRs statt sie zu retargeten (Recovery: Head-SHA re-pushen → reopen → Base edit); `gh run rerun` nach Base-Retarget recycelt stale Event-Payload → Close/Reopen triggert frisch; GitHub schließt Issues auch über Development-Verknüpfung ohne Closes-Trailer (#171/#28 reopened). Health-Check 09.07.: Kernbestand drift-frei, 5 Rand-Drifts gefixt.

**2026-07-10 (Vormittag):** Reading-Nav-Kontrast-Fix nach KZW-Feedback (`6df766522`): `.reading-nav`-Komponenten in korpus.css statt Tailwind-Utilities, weil das vorkompilierte tailwind-output.css neue Klassen still verschluckt; Commit über temporäres Worktree (geteiltes Working-Dir). KZW-Rückstau-Session (5 Commits, 205/205): #110/WVV komplett (489 `<lg>` fortlaufend), #28 reopened mit 26 KWIC-Grenzfällen, #203 KWIC-CSV-Export, #204 Filter-vs-Auswahl-UX (noResults-Box konnte seit jeher nie erscheinen), #187 posAll-Anzeige-Migration. **Direktive chsteiner: Frontend vor Ingest** (CoReMA #139 später als gemeinsame Session); juliahin wieder regulär im Projekt; brevitas-Wiki ohne Lizenz = Blocker für #147.

**2026-07-10 (Nachmittag) bis 07-12 (Frontend-Welle + Review-Umstellung):** 8 PRs #205–#212 (Hapax-Werkzeug #196, Belege-Hilfeseite, 12 Python-Findings, Vers-Modus, Versendings-Profil), alle gemergt. #189 quantifiziert die Annotationslücke erstmals: 1,9 Mio. Tokens ohne `@lemmaRef`, stärkster Einzelfall `minne` mit 6.982 unsichtbaren Belegen → #216. Review-Workflow auf das code-review-Plugin mit `--model opus` (11.07.), dann Auto-Cancel beim Merge (`2d6335856`: `closed`-Trigger plus Concurrency-Group), womit das händische Canceln entfällt. Lehre: `read_text()` normalisiert Zeilenenden, die CRLF-Erhaltung in `build-pages.py` war seit jeher wirkungslos.

**2026-07-12/14 (GWTK-Pilot + erste Carearbeit):** PR #214 disambiguiert 278 rot/jung-Tokens und trifft den Goldstandard exakt; PR #215 räumt 252 Encoding-Fehler und 418 Em-Dashes aus den Docs. Erste Carearbeit-Session (PR #220, `6a9849314`): die Drift saß in Zählwörtern und Versionsangaben, nicht im Code, daraus das dritte Playbook `MASTERPLAN-CAREARBEIT-SESSION.md`. #219 Wenzelsbibel entschieden (Variante B+D, PR #221 dünnt 1.451 Dateien aus), `doc-count-audit.py` um den Zahlwort-Scan für code-abgeleitete Counts erweitert (PR #222).

**2026-07-28 (#224: es war ein Breve):** Klaus Schmidts Bug-Report führte über zwei falsche Diagnosen zum Fund: die Wenzelsbibel schreibt Umlaute mit kombinierendem Breve (U+0306), 830 Tokens, kein anderer der 667 Texte trägt eines. Fix aus drei Teilen (NFC als Schritt 0 der Normalisierung, `ŏ`/`ŭ` als Umlautzeichen in Contract A, Stufe 3 als beidseitiger Präfix-Test statt Substring-Suche), ADR-016. Lehre: die Erklärung, die den Screenshot erklärt, ist nicht dieselbe, die auch das Ausbleiben des erwarteten Treffers erklärt.

**2026-07-28/29 (Merge-Session + die Gate-Lehre):** vier PRs auf `main` (#241 Em-Dash-Gate, #238 kaputte Tilden, #243 814 HUG-Strophenziffern, #240). Dreimal hintereinander ein Audit-Eintrag, der grün lief und nichts fing; jedes Mal deckte erst die Mutation es auf. Daraus die Regel **ein grünes Gate ist kein wirksames Gate**, solange niemand den Fehler einbaut, den es fangen soll. Authority-Index 1.6.4, Korpus-Index 4.1.8.

**2026-07-29 (#169 Nähesuche + Playground-Aufräumrunde):** „innerhalb N Wörter" misst ab jetzt die Spanne aller Treffer statt den Abstand zum Anker; Trefferzahlen aus Suchen mit drei oder mehr Lemmata sind mit älteren nicht vergleichbar (Zäsur datiert). Das Fast-Path-Dictionary in `tei-ui.js` gestrichen: 5 von 11 Einträgen lösten falsch auf, „bier" lieferte Birnen. Acht Funktionen ohne Aufrufer entfernt; doppelte Lemma-IDs ließen beide Kookkurrenz-Modi degenerieren, der Guard sitzt jetzt in der Datenschicht. PRs #245/#246/#247/#254, `main` auf `ba6ba8e5c`, neues Issue #251. Dead end: ein Mutationsbeweis, der zwei Änderungen gleichzeitig zurücknahm und deshalb weniger zeigte als behauptet. ParzivAI-Wissen aus einer nie committeten Handover-Notiz in RESEARCH/INDEX/ROADMAP überführt (kein ADR: ein externes Projekt zur Kenntnis zu nehmen hat keine Repo-Folgen).

**2026-07-29/30 (#236 Frauenlob):** Die Parallelüberlieferung war beim Linecode-zu-TEI-Import verlorengegangen und ließ sich aus KZWs Legacy-Ordnern rekonstruieren statt am Druck zu prüfen: 23 gleichrangige Töne auf 10 zusammengeführt, 36 `<div type="parallel">`, 1.563 von 9.595 Versen als Parallelüberlieferung erkennbar. Vier Review-Runden mit je genau einem echten Befund, gemergt als `115c3a01f` (Korpus 4.2.0 / Authority 1.6.5), Folgefrage als #255. Lehren: ein Verifikationsskript darf nicht die Struktur voraussetzen, die es prüft; ein Skript-Fehler wird im Skript repariert und die Datei neu erzeugt, sonst laufen Skript und Bestand auseinander (die Kette 02–05 ist damit als reproduzierbar belegt, nicht nur als idempotent). Gegen die Zweitmeinung entschieden und selbst gemessen (51 statt 60 `parallel`, 1.406 statt 1.360 `song`). #251 als PR #256 gemergt (`b8aa68472`). `use_sticky_comment` einen halben Tag lang probiert und verworfen (`bf505a129`): zusammen mit `track_progress` überschreibt der nächste Lauf den Befund genau dann, wenn man ihn nachlesen will, und die Historie liegt danach nur im Browser. `gh pr merge --body` zerbricht an Klammern, `--body-file` nehmen.

**2026-07-30 (#248 `sources/` + kuratiertes Lemma-Wissen):** 306 codierte Legacy-Dateien für 199 der 667 Sigel als `sources/linecode/` ins Repo, byte-identisch (`-text` in `.gitattributes`), das 9,1-GB-Restarchiv katalogisiert statt kopiert; Nebenfund `apk_free.xml` als bester Ingest-Kandidat (#262), `FnhdC/` lizenzrechtlich gesperrt. Das Lexikon bekommt drei optionale Produktionen für kuratiertes Wissen (`etym[@type="borrowing"]`, `def`, `note[@type="comment"]`), erster Fall `lemma_37818` Abba; Authority-Index 1.7.0, Schema 1.1.0.

**2026-07-31 (Doku-Tag, sechs PRs):** Der Health-Check fand die Drift bei den **code-abgeleiteten** Zahlen, nicht bei den Datenzahlen, und der Hauptbefund war das Gate selbst: ein konfiguriertes Target ohne Anker-Treffer ist derselbe blinde Fleck wie ein fehlendes Target, nur schwerer zu sehen (#276–#281). #258 erweitert die Wörterbuchnetz-Verlinkung von zwei auf fünf Wörterbücher (`8a6626c68`); teuerster Befund dabei: ein verworfenes `failed`-Flag ließ das Hapax-Werkzeug eine Netzstörung als „nicht als Lemma belegt" ausgeben, jetzt CONTRACTS §D.2 „Absence of a link is not absence of attestation". CONTRACTS §H mit nachrechenbaren Zählregeln für die Analyse-Werkzeuge (#281). #228: sieben leere `<author>`-Elemente plus vier neue Befunde aus dem neuen `check-author-refs.py` (#308), Korpus-Index 4.2.1; dabei nahm eine Maßnahme gegen Fehlalarme einen echten Alarm mit. #309: 20,13 % aller `<w>` ohne `@lemmaRef`, Abdeckung je Text 58,4 bis 100 % (Median 77,4 %), Messung als `scripts/audit/coverage-bias-check.py` beigelegt. Aufräum-Session PR #275 (Directory-Layout, `scripts/README.md` gegen das Dateisystem neu geschrieben, #274 angelegt). Drei Lehren: Aussagen über **Abwesenheit** brauchen dieselbe Prüftiefe wie der Hauptteil und zählen die ausgeschlossenen Fälle namentlich auf; eine Zahl ohne Messvorschrift wird beim „Korrigieren" falsch (Breve-Zahlen in §A, NFD oder nicht); wer eine Zahl für historisch erklärt, misst das Datum dazu statt es aus der Zahl zu erschließen.

**2026-07-31 (Nachtrag):** Die vierte Stelle, an der eine Indexversion steht, pflegte niemand, weil ihr Veralten nichts kaputt macht (#307/#312/#317). #314: ein Guard hatte 1300 Zeilen toten Code konserviert, und ein Test war falsch-grün. Lehre daraus: ein Rückbau kann eine Aufräumfunktion mit abschalten, die niemand als solche gelesen hat.

**2026-08-02 (Aufräum-Session, fünf PRs, und die Hälfte der Review-Last war hausgemacht):** 18 Review-Läufe, 27 Befunde, davon 10 echte Defekte, **13 falsche Tatsachenbehauptungen in selbst geschriebenen Kommentaren**, 4 Kosmetik. Daraus die Selbstverpflichtung in CLAUDE.md: jede Zahl in einem Kommentar wird gemessen, ab Runde 3 nur noch Verhaltensbefunde. Savepoint `ce55dde0a`. Am Abend die Rollentrennung: `fable-reviewer` prüft einen fertigen Diff und hat Bash zum Nachmessen, `fable-advisor` berät bei offenen Entwurfsfragen; der Zeitpunkt entscheidet, nicht die Gründlichkeit. Savepoints `0d769c8e4`, `6a8d4caba`, `e5bd0adc9`, `fd6564bb4`.

**2026-08-03 (#316, die Doku ist englisch):** Teuerster Fund des Tickets waren **elf stille Kopplungen zwischen Doku-Prosa und Audit-Skripten**: ein übersetzter Satz kippte ein Gate. Dazu drei kaputte Ankerverweise, zwei älter als das Ticket. Der Review-Bot kam am Diff nicht vorbei, daraus die Lehre, dass die PR-Größe eine einzuplanende Eigenschaft ist und keine bloße Folge. Savepoints `011f74f9d`, `640020235`, `90cc3e49a`, `b261069cf`, `dad844b2a`.

**2026-08-05 (Label-Neuordnung 28 auf 16 + Loop Engineering):** Der Befund, der die Arbeit rechtfertigte: **30 der 52 offenen Tickets warteten auf einen Menschen, nicht auf Arbeit.** Daraus das Drei-Achsen-Schema (`auto:` / `area:` / `effort:`), gebaut für Agenten, mit der Legende im Body von #44. Savepoints `5e051105d`, `aff7fe2af`, `b59350bb5`. Am Nachmittag vier Merkregeln zu einem Wrapper-Skript und drei Playbook-Verträge zu einem zusammengezogen; die Prüfung des Wrappers kostete mehr als sein Bau, und ein Zitat eines beratenden Agenten hielt der Messung nicht stand, weshalb eine Regel unverändert blieb.

**2026-08-06/07 (ADR-017, #58, drei Entscheidungs-Tickets):** Der Lifecycle-Lauf fand nichts zu tun, und das war eine Messung, kein Leerlauf (`f3dcf2a8`). Zwei Zahlen in CONTRACTS §A waren in dieselbe Richtung falsch. #58: die Entscheidung war nicht A gegen B gegen C, sondern Schreibform gegen ID, und der Weg vom Lemma zum Beleg trägt seither eine ID. Bei #225/#111/#270 war jeweils die Entscheidung teurer als die Umsetzung; **#270 hat sich beim Messen selbst widerlegt**, und aus #111 kam vor allem eine Messvorschrift.

**2026-08-08 (#111 wird ein Gate, #193 in drei Bausteinen):** Die Zahl vom Vortag war kein Rückgang, sondern ein Einheitenwechsel; das Gate warnt seither und wird nie rot (`4195581e3`, `ea7b0a507`). #193 Baustein 1 fand ein Pferd, das als Mann klassifiziert war. Baustein 2 trägt die Lehre im Titel, „was eine Quote von 76 Prozent nicht heißt": **die Zahl, die man aus einem Abgleich herausliest, ist fast immer die falsche**, weil ihr Nenner eine andere Menge ist als die, nach der gefragt war. Baustein 3 ist der lehrreichste: das Maß erfand die Zweifelsfälle, die es finden sollte, sechs von neun gemeldeten Versen ohne Entsprechung gab es nicht, die drei Reste waren ein zu enger Suchradius. **Gefunden hat es der Berater nicht durch Nachrechnen, sondern durch Lesen.** 336 von 336 Versen danach textlich verifiziert.

**2026-08-09/10 (#59, #358, #361):** Der Naming-Explorer konnte die Frage schon beantworten, er konnte sie nur nicht stellen; das Gitter durfte bleiben, weil jetzt feststand, was es heißt, und der Deckname wurde eine vierte Kategorie statt einer Umbenennung. #358: **die Prüfung, die den Umfang ausweiten sollte, hat ihn halbiert**, über zwei eigene Messfehler hinweg, und landete bei genau dem Umfang, den das Ticket von Anfang an nannte. #361: der Defekt war eine Zeile, die Ursache ein Datenmodell (die Gattungskette ist eine Hülle, keine Hierarchie); die Reduktion gehört in den Build, nicht in die Ansicht.

**2026-08-14 (#59):** Die Erklärung durfte nicht vor den Daten kommen; der Zuschnitt drehte sich unter der Messung um. Drei Guards im Build, einer bewusst asymmetrisch. Das Review fand zwei grüne Prüfungen ohne Haltekraft.

**2026-08-24 (#216/#369, zwei Disambiguierungs-Serien):** Der Filter, der die schweren Fälle finden sollte, kannte kein Mittelhochdeutsch: **eine Wortliste ist dort kein Filter.** Drei Stichproben-Durchgänge über 150 Fälle ohne Fehler, und der zweite davon war wertlos. In Serie 2 waren 51 der 95 Rückhaltefälle gar kein Zweifel zwischen den beiden Kandidaten, sondern ein drittes Wort; ein zu enges Kandidatenpaar erzeugt keine falschen Annotationen, solange die Konfidenz die Notlage ausdrücken darf. Zwei Heuristiken gescheitert, beide im Log.

**2026-08-31 (drei entblockte Tickets, zwei Messaufträge, ein Datenlauf ohne Indexänderung):** Zweimal war die Messvorschrift das Byte, und **ein Diff, der zeichenweise stimmt, ist trotzdem keine Messung**. Ein Datenlauf über 46.890 Tokens ließ beide Indexe byte-identisch, der Versions-Bump stand trotzdem drin, gegen eine Regel, die derselbe Eintrag zitiert; kein Gate hätte das gefangen. Savepoints `6fbf7e002` (Bot-Turnbudget auf 100), `c0e8dee80`.

**2026-09-01/02 (Wellenlauf mit Koordination und Spur):** Der Lauf blieb seriell, weil die abgeleitete Schicht global ist; von fünf autonom antastbaren Tickets blieben nach Messung zwei startbare, und **ein Ticket kann entblockt sein und trotzdem an seiner ersten Handlung hängen** (`2adc52fc5`, `5aa3a8df3`, `8a7ea2116`, `b306d9f22`, `f3a575c77`). Dreimal saß der Fehler im Zuschnitt der Prüfung, nicht in der Rechnung. Der teuerste Fix entwertete einen Prüfpfad, den niemand nachzählte: daraus die #397-Frage in CLAUDE.md, **was hat dieser Fix wahr gemacht, das vorher falsch sein konnte** (`091335fe0`, `144fbbd3c`, `3b9abb3f9`). Der Health-Check desselben Tages fand eine Klasse statt eines Einzelfalls: dreimal stand in der Doku eine Aufgabe als offen, die längst erledigt war.

**2026-09-06 (vier Einträge, und der Rückstand ist zu einem Drittel keiner):** 1.455 Tokens neu annotiert, Korpus-Index 4.2.11 auf 4.2.13, Authority 1.9.2 auf 1.9.3; `doc-count-audit.py` hängt seither als Gate in `data-integrity.yml`. Rot: **Eindeutigkeit über einer Menge mit einem Element ist keine Eindeutigkeit**, und eine Zahl in der falschen Einheit macht eine verbuchte Altlast zu einem frischen Alarm. Abends zehn blockierte Tickets entscheidungsreif gemacht, **drei ihrer Prämissen waren abgelaufen**; nachts elf weitere Vorgänge (`2c23520`), ohne Korpus oder Authority anzufassen. Daraus die Regel, die seither in CLAUDE.md steht: **vor der Vorlage steht die Nachmessung, nicht die Zusammenfassung**, und ein Issue ist Body und Kommentare.

**2026-09-07 (TRO, drei Fixe, Aufräumlauf):** Beide TRO-Werte waren richtig, sie gehörten nur zu zwei verschiedenen Werken: `works.xml` führt einen zweiten `bibl` mit derselben Sigle. Gefunden hat es erst die #397-Frage, nicht der Abgleich. Am Nachmittag dreimal derselbe Fehler, und **zweimal war er der Fix des vorigen**: die Frage einmal zu stellen genügt nicht, wenn der Fix selbst wieder ein Fix ist. Der CI-Bot fand zwei davon bei grünem Check. Im Aufräumlauf lagen zwei falsche Doku-Stellen im toten Winkel eines Gates, das genau daneben greift.

**2026-09-10/11 (#427, #425, #363):** Ein gemeldetes Token (`hawssen`) waren 19 Belege in 7 Sigeln, 32 Tokens, und alle sieben Texte sind Kochbücher. Mehrwort-Lemmata gibt es im Korpus seit Jahren, nur dokumentiert war es nirgends, und deshalb wurde zweimal "die erste im Korpus" behauptet. Der teure Fehler war eine schon vergebene Versionsnummer (Korpus 4.2.14, Authority 1.9.4) und ein Gate, das auf beiden Seiten grün war: Konsistenz innerhalb eines Arbeitsstands ist keine Eindeutigkeit über offene PRs hinweg.

**2026-09-11 (#198 Schritt 2):** Die seit Juli "kuratorische" Frage, welche der acht Senses von *haben* nominal sind, war eine Messfrage: alle acht sind nur verbal belegt, also zieht nichts um. Das `<pos>NOM</pos>` fiel erst, nachdem die drei NOM-Tokens entschieden waren (Korpus 4.2.15, Authority 1.9.5). Lehre: ein Commit ohne PR ist hier unsichtbar, die Entscheidung vom 21.08. hat 21 Tage nichts bewirkt. Ein Skript im Textmodus hätte aus der einzigen CRLF-Datei (WZB) 235.980 Scheinänderungen gemacht, gefangen hat es nur `git diff --stat`.

**2026-09-11 (Nachmittag, #419, #58):** Alans 15 Screenshots, erstmals gesehen, widersprachen dem Protokoll: Der Fehler lag bei uns, aber woanders, denn die Leermeldung des Reimwörterbuchs nannte den eingestellten Filter nicht. #58 war zum zweiten Mal derselbe Mechanismus, eine Aufräumarbeit ließ die Anzeige auf das einzige verbliebene Zahlenfeld zurückfallen. Vier rote Zeilen (22 bis 25) mit einer Gestalt: eine Aussage, die aus der Nähe stimmt, weil ihre Bestandteile stimmen, und falsch ist in der Verbindung.

**2026-09-14/15 (Nachtlauf, #237, #308, #375, #410, #432):** 9 von 39 Vorgängen mit `wait:kzw` trugen eine Antwort, die den ganzen Rest trägt. Befund des Laufs: der TEI-Header spiegelt drei Master, und nur `msIdentifier` hatte ein Gate. Die Bibliographie-Korrektur in VTC war wirkungslos, weil ausgeliefert wird die Fassung aus `works.xml`. `check-author-refs.py` läuft seither als Schritt in `data-integrity.yml`, und beim dritten Loch wurde der Mechanismus gewechselt: eine Invariante statt einer vierten Fehlerklasse. #410 ordnet die Abfragespalte in vier Blöcke, dabei lösten sich drei Gate-Bindungen still (Korpus 4.2.16, Authority 1.9.6). Rote Zeilen 26 bis 34.

**2026-09-15 (#204, PR #441):** Die Auswahl aus Schritt 1 wirkte auf 10 von 11 Playground-Werkzeugen gar nicht, der erbetene Hinweis hätte eine Wirkung versprochen, die es nicht gab. Zwei Thunks statt einem (`selectedTextsThunk`, `corpusTextsThunk`). Wer eine Menge verengt, entwertet jeden Zustand aus der alten Menge, und Tests, die den Zustand setzen statt ihn entstehen zu lassen, prüfen die Zeile darunter. Zwölf Reviewrunden. Rote Zeile 35.

**2026-09-16 (#444):** Moriz von Craûn ist anonym, die Zuschreibung an Bligger von Steinach entfällt in work_5 und im CR-Header (Korpus 4.2.17, Authority 1.9.7). Folgeaufträge: ein Datenmodell für den Forschungsstatus und eine Prüfung aller Mehrfachzuschreibungen.

**2026-09-21 (Spur A, #366, #375, #371):** 88 Tokens in 45 Dateien, zehn neue Variantentypen statt der geplanten drei, Korpus 4.2.18, Authority 1.9.8. Dreimal stand die Zahl im Auftrag gegen die Zahl im Bestand, und KZWs `zusammenfassung` war entgegen dem geplanten Vorwurf richtig: zwei Felder, zwei Mengen. Die #397-Frage ergab erst im zweiten Anlauf den Befund, dass `hawsen` im Laufzeit-Wörterbuch umklappt, gegen Vorschrift B von ADR-021. Rote Zeilen 40 bis 44.

**2026-09-21 (#443, #359):** Ein Format für kuratorische Prüfseiten und seine erste Anwendung auf 45 Fälle aus Boreks Pferdewortlisten, von denen 28 Artefakte des Abgleichs oder bestätigte Annotationen waren. Ein Gate schützt, was es liest, und die Liste dessen ist selbst eine Behauptung. Wer ein Gate ersetzt, fährt die Mutationen der alten Fassung gegen die neue. Der Zuschnitt einer Messung ist gefährlicher als ihre Rechnung. Rote Zeilen 45 bis 49 und 56.

**2026-09-22 (Prüfseiten-Beispiele):** `examples/review-pages/` hält die leeren Prüfseiten zu #364, #371 und #390/#115 als byte-identische Kopien, mit Überblick in INDEX und Browsertests auf den Archivpfaden. Keine Entscheidungen und keine Korpusänderungen enthalten.

**2026-09-23 (Spur A, #387, #418, #464):** 36 Tokens, Korpus 4.2.19, Authority 1.9.9. Eine Bestandszahl zählt die Altlast mit, bis man fragt, welches Merkmal die Fälle trennt: `VRB PRO` hat 154 von 154 ein `@reason`, `PRO VRB` 0 von 9.068, deshalb steht das Doppeltag in der Reihenfolge `ADJ NOM`. Der Typzähler war zum zweiten Mal grün, während das Wörterbuch umklappte (`froewen`), und die Reviewrunde fand es.

**2026-09-23 (Spur B, #446, #435, #433, #58):** Vier KZW-Meldungen im Frontend, #58 bewusst nicht gebaut. Ein Haltepunkt im Auftrag kann den falschen Gegenstand tragen, ein totes Feld hat oft einen falschen Leser statt eines fehlenden Schreibers (`work.genre` gegen die Liste `genres`), und ein Overlay über Checkboxen macht aus einem Fehlklick eine andere Handlung. Rote Zeilen 70 und 71.

**2026-09-23 (Spur C, #465, PR #472):** Der Testport als Parameter `MHDBDB_TEST_PORT`, 132 absolute Adressen in 30 Specs sind relativ. `http-server` ohne `-p` weicht still auf den nächsten Port aus, deshalb ein Wrapper. Eine Testzahl, die von der Umgebung abhängt, ist keine Eigenschaft der Suite (370 gegen 355, wegen fremder Worktrees), und eine Abnahmeprobe, die die Maschine überfordert, sagt etwas über die Probe. Rote Zeile 73.

**2026-09-23 (Nachtlauf, Paket A1, #252, #267):** 846 Stellen `( caesura )` wurden `<gap reason="lost"/>` in 20 Dateien, neun Header tragen `no-print`. Ein gesicherter Patch ist ein Kontrollwert und kein Ergebnis, und ein Marker, den niemand liest, kann jahrelang das Gegenteil sagen (`excerpt-only` wertete nirgends etwas aus). Kein Index-Bump, weil keiner der Builds eine Differenz erzeugt.

**2026-09-23 (Nachtlauf, Paket B1, #433):** Der Gattungs-Chip auf den Trefferkarten hat nie gerendert, weil `work.genre` in keinem der 584 Werke steht. Ein toter Anzeigezweig hat eine tote Kette hinter sich, und die geht mit weg. Ein Test auf das Fehlen wäre auf der Basis ebenso grün gewesen und hätte nichts festgehalten.

**2026-09-23 (Nachtlauf, Paket A2, #270):** Der Kommentar nennt seinen Urheber, aufgelöst beim Bauen (ADR-018 Option 2, `commentRespName`), Authority 1.9.10. Der Index-Diff ist die Messung: genau zwei Felder ändern sich, und eine unbekannte Urheberangabe hält den Build an.

**2026-09-23 (Nachtlauf, Paket B2, #420):** Pin auf Naming-analysis v0.3.0-beta, gebaut gegen `master` (derselbe Commit), weil ein wörtlich ins Artefakt geschriebener Parameter zum Inhalt gehört. "Lemma" statt "Term" im Modul. Eine Zahl, die ein Skript für ein Modul nachrechnet, muss rechnen wie das Modul: `Math.round` gegen `round()` ergab 244 statt 247.

**2026-09-23 (Nachtlauf, Paket A3, #357):** Ingliart bekommt einen zweiten Sense für den Menschennamen (ADR-020), Authority 1.9.11. Das Konzept ist aus dem Namenkatalog abgeleitet: alle 15 Personen des Katalogs tragen dieselben zwei Konzepte. Der Korpus-Index sieht keine Sense-Zuordnung, ein Bump wäre ohne Inhalt.

**2026-09-23 (Nachtlauf, Paket B3, #467):** Das Wörterbuch nimmt die Lemma-Nummer, auch in der Schreibung aus `@lemmaRef`. Eine nackte Zahl ist dort nicht eindeutig (fünf Lemmata beginnen mit einer Ziffer), und ein Hilfebeispiel ist auch eine Behauptung über die Daten.

**2026-09-23 (Nachtlauf, Paket B4, #448):** CSV-Export in neun von 13 Playground-Werkzeugen, Hapax behält seinen älteren Export. Die Datei trägt die Menge und nicht die Anzeige, und die Multi-Lemma-Suche als Anwendungsfall des Tickets hat keinen Export, die Frage dazu liegt bei KZW. Zwei CSV-Formate bleiben nebeneinander, Helfer `csv-export.js`.

**2026-09-24 (Nachtlauf, Paket A4, #228):** Apparat entannotiert (69 Noten, 422 GWTK-Noten), 165 Lemmata gelöscht, Korpus 4.2.20, Authority 1.9.12. Ein gehaltenes Lemma (Mur) hatte 82 Geschwister im Lexikon, weil das Suchmuster nur einwertige `@ana` sah: 21.844 von 43.404 Attributen sind mehrwertig. Ein gelöschtes Lemma kann das Beispiel einer anderen Spur sein.

**2026-09-24 (Nachtlauf, Koordination):** Zehn PRs gemergt, Schlusslauf grün (389 Tests). Zwei dateidisjunkte Spuren sind es über die Daten nicht (A4 löschte das Prüfbeispiel von B3), und ein "sofern" in einer Entscheidung ist keine Entscheidung. Die Koordination wies einen Force-Push an, den der Spurvertrag verbietet, Spur B lehnte ab.

**2026-09-24 (#237):** VTC-Editionsnachweis aus Zotero (Authority 1.9.13), Josef Jireček als Mitherausgeber. Ein Online-Sync ändert alles, was seit dem letzten auseinandergelaufen ist: 171 Werke mit Großschreibung und zwei Handkorrekturen (FLG, FR1) kamen mit. Entschieden: nur VTC in diesem PR, der Rest in #486, und die Richtung der Kette ist Zotero, dann `works.xml`, dann Header als Kopie.

> Full older entries preserved in journal-archive.md

---

## 2026-10-02 – #370 Punkt 2: Vorprüfung der offenen Paare (Spur C)

484 WZB-Paare aus Schreibung und Lemma ohne `@corresp` sind am Kontext entschieden: ANLEGEN 412 von 484 Paaren (4.675 von 5.273 Tokens), NICHT_ANLEGEN 43 (260), PRUEFSEITE 29 (338), VERKNUEPFEN 0. Dazu 74 Paare (109 Tokens), die seit der Arbeitsliste vom 31.08. dazugekommen sind: ANLEGEN 49 (80), VERKNUEPFEN 25 (29). Die 29 Prüfseitenfälle stehen auf `ingest/wzb/370-corresp/pruefseite-370.html` nach #443. Ausgang: `entscheidungen.csv`, `entscheidungen-nachtrag.csv`, Belege in `evidenz.json`.

### Was über den Einzelfall hinausgilt

**Die Liste vom 31.08. und der Korpus waren nicht mehr dieselbe Menge.** Die 484 Paare tragen heute 5.283 Tokens ohne `@corresp`, nicht 5.273 (8 Paare mit mehr Belegen), und 25 der 74 Paare danach hatten ihren Typ unter dem Lemma schon: das sind Punkt-1-Fälle, kein Anlegen. Der erste Entwurf hatte sie auf ANLEGEN gesetzt, und `fable-reviewer` hat es in Runde 1 gefunden. Die Koordination hat dafür den Wert `VERKNUEPFEN` festgelegt. **Soll für Spur A ist „alle Tokens ohne `@corresp` je Paar", nicht die Zahl der Liste.**

**Ein Sammellemma verdeckt Befunde.** 41 der 484 Paare stehen unter `lemma_2` abc, das KZW am 11.09. (#228) ausdrücklich als eigenes Thema abgetrennt hat: alle NICHT_ANLEGEN, Zielvorschläge für 18 davon in `abc-befunde.csv`. Außerhalb von abc stehen 7 Paare der meil-Familie (82 Tokens) unter `heiligen`, obwohl die Belege „beflecken" meinen (Lexer Bd. 1, Sp. 2077): als KI-Vorschlag auf der Prüfseite, nicht angewendet.

### Rote Zeilen

Eine, Eintrag 100: `cd` und zweimal ein Heredoc in Shell-Befehlen. Der Hook hat die Heredocs geblockt.

### Was zurück an Christian geht

- Die 29 Fälle der Prüfseite (KZW oder wen sie benennt), darunter die cs-Randglossen (6 Paare) und die gemischten Paare `wirft`, `lose`, `weiden`, `pilgereimen`.
- Offen für die Koordination: ob Spur A die 25 VERKNUEPFEN-Paare wie Punkt 1 behandelt.

## 2026-10-02 – #358: die 16 Buchgrenzen des Parzival (Spur C)

Die Bücher fehlten im TEI komplett (Alan, #358); KZW hat am 11.09. die Benennung „Buch I" usw. entschieden. `ingest/parzival-buecher/grenzen.csv` bildet die 16 Buchanfänge nach Lachmann auf die erste Wort-ID in `PZ.tei.xml` ab: I 1,1; II 58,27; III 116,5; IV 179,13; V 224,1; VI 280,1; VII 338,1; VIII 398,1; IX 433,1; X 503,1; XI 553,1; XII 583,1; XIII 627,1; XIV 679,1; XV 734,1; XVI 787,1. Quellen: Bartsch (Deutsche Classiker des Mittelalters 9-11, 1875-77) und Martin (Kommentar, 1903), beide als OCR-Volltext von archive.org gelesen, nicht am Scan.

### Was über den Einzelfall hinausgilt

**Die Bücher II bis IV beginnen mitten im Dreißiger, die anderen 13 an einem Dreißigeranfang**, und die Zählung der Dreißiger in den Wort-IDs trägt die Abbildung ohne Umweg. **Zwei Stellen waren aus dem Gedächtnis oder dem Eindruck falsch:** XIII beginnt bei 627,1, nicht bei 643,1 (Bartsch und Martin einig), und VIII bei 398,1, nicht bei 399,1. Die zweite hat erst die Gegenprobe des Reviewers gefunden. **Ein Skript, das die Anfangswörter gegen die Datei prüft, aus der sie stammen, prüft nur die Wort-ID-Abbildung**, nicht die Grenze; die Quellenspalte sagt es jetzt.

### Rote Zeilen

Eine, Eintrag 101: VIII am Erzählerton statt am ersten Vers der Quelle festgemacht.

### Was zurück an Christian geht

Nichts aus diesem Paket. Spur A3 setzt die Milestones aus der gemergten Datei.

## 2026-10-02 – #228: Mur bei Murstetten (Spur C)

KZW hat am 25.09. gefragt, ob der Bestandteil `Mur` (`lemma_66692`, Gewässername) in Murstetten (`lemma_66691`) stimmt, und am 01.10. präzisiert. Die drei Belege (HZU2, 1339, 1392, 1396) meinen denselben Ort in Niederösterreich und sagen über die Herkunft des Namens nichts. Winter (Jb. LKNÖ 54/55, S. 349–361) gibt für das Bestimmungswort Schusters Deutung wieder (vermutlich slawischer Personenname); von der Mur ist bei ihm nicht die Rede. Vorschlag als Kommentar in #228: `Mur` aus der Etymologie von `lemma_66691` streichen, kein Ersatzziel, `lemma_66692` bleibt wegen `Mûrouwe`. Die Notiz liegt unter `ingest/mur-228/README.md`, geändert ist nichts in `authority-files/`.

### Was über den Einzelfall hinausgilt

**Eine Deutung aus zweiter Hand trägt ihren Weg mit.** Schuster habe ich nicht geöffnet, nur Winters Wiedergabe von 1990 gelesen. Der Satz mit den Mauer-Orten ist Winters eigener, und `fable-reviewer` hat es in Runde 1 gefunden, weil der erste Entwurf ihn Schuster zugeschrieben hatte. Nach dem Befund steht jede Deutung mit der Person, die sie sagt, und dem Weg, auf dem sie zu mir kam.

### Rote Zeilen

Keine.

### Was zurück an Christian geht

- Die Entscheidung über den Vorschlag liegt bei KZW (#228). Die zweite Hälfte ihrer Frage vom 25.09., die Deutung von Murau, ist in diesem Schritt nicht geprüft.

## 2026-10-05 – Doku-Check nach 178 Commits (Scorecard)

**Scorecard Doku-Check 2026-10-05** (Anlass: 178 Commits seit dem Check vom 11.09., 13 der 15 Docs angefasst). Gates alle grün (`doc-count-audit`, `check-doc-inventories`, `check-index-versions`, `check-release-version v1.1.0`, `check-no-cdn`, Em-Dash, `build-pages --check`). Drei Algorithmen gegen den Code deckungsgleich (§C.1.2 Lemma-Nummer als Eingabe, §H.1 Keyness, §C.2.3 Dokumentsuche), drei XPaths der Build Script XPath Reference exakt (Korpus-Titel per `itertext`, `persName[@type="alternative"]`, `biblStruct`). Flow der 13 geänderten Docs von drei Sonnet-Agenten vollständig gelesen; jeder übernommene Befund selbst gegengelesen oder nachgemessen. **14 falsche Sachaussagen und 12 Kleinigkeiten behoben, je Befund ein Commit**, darunter `npm test` mit „ask the user first" im Lifecycle, `tei_all.rng` als „gitignored", ein `lemmaRef`-Beispiel in falscher Form, „15" statt 7 `div`-Typen, `<cb>` ohne die WZB, „98 today" statt 35 fehlender Ingest-Lemma-IDs, „GAPs 1–11" bei einem Schema mit 1 bis 9, 11 und 12, die verrutschten Zeilenanker in CONTRACTS und DECISIONS (jetzt Funktionsnamen).

**Was über den Einzelfall hinausgilt:** elf der 14 Sachfehler sind Zahlen und Zustandssätze, die kein Gate sieht, `doc-count-audit` deckt nur seine eigene Liste. Wo der Satz die Zahl nicht braucht, ist sie gestrichen oder datiert worden statt mitgezogen. **Ein Agentenbefund war zur Hälfte falsch:** „396 refs / 109 IDs" sah wie veraltet aus, stimmt aber, weil `check-authority-cross-refs.py --check` Lemma- und Sense-IDs zusammen zählt; veraltet war nur die „98 today"-Stelle daneben. Bewusst nicht angefasst: zwei Em-Dashes in Bestandstext und die Zahlen 4.991 und 4.979 in CONTRACTS §C, die aus zwei Zählwegen stammen (`variants.xml` gegen Korpuszählung); ihre Differenz von 12 ist nicht nachgemessen.

**Nachgang am selben Tag: ungegatete Zahlen und Zustandssätze.** Inventur per Skript über die 14 stabilen Docs: 199 undatierte Zahlen in 120 Absätzen vorher, 194 nachher (Summe beider Läufe 524). Jeder Kandidat erst gegen `doc-count-audit` geprüft (Lexikon, Varianten, Module sind gegatet und blieben), dann gemessen. **Zehn Befunde, je ein Commit:** API-Dateizahl 2,742 an fünf Stellen gestrichen (gemessen 2,743, die neue ist `api/works/work_WLK.json` aus #496; Verweis jetzt auf die Zählung in `api/index.json`); „19×" an drei Stellen, eine Zahl, die schon bei ihrer Einführung (`cd4734fc8`) nicht zu den eigenen Werten passte, auf die ~15× aus ADR-001; drei statt zwei Suchmodi in ARCHITECTURE; IndexedDB-Fristen nach #314; „the lexicon grows" (es ist gesunken); Tokenstand in TEI-MODEL 4.1 auf heute; `hi/@rend`-Tabelle datiert; Breve-ADR mit dem Stand von #235 Punkt 3 (48 von 113 Tokens ohne `@lemmaRef`); #18 hieß „data migration"; **WZB hat keinen `<authority>`-Block**, obwohl TEI-MODEL zweimal „all 667" sagte (`git log -S contrib_003` auf der Datei: nie vorhanden).

**Drei Zahlen sahen falsch aus und stimmten:** „263 of 567 concepts" (zählt je Sprache; 304 wären die Konzepte mit irgendeinem Alternativbegriff, eine andere Menge), „Eight of the eleven" (die 12 in derselben Datei zählt die Module samt Naming und Pferden) und „666 headers / 664 texts" in FEATURES. Wer sie „korrigiert" hätte, hätte die Doku falsch gemacht. Die Größenangaben „~40 MB" für 42.22 MB blieben stehen: Rundung, kein Fehler. Offen und nicht Sache der Doku: der fehlende `<authority>`-Block in WZB (Korpusänderung) und, ob ein offener Vorgang die 48 Breve-Tokens führt (gesucht nur über das Wort „breve", #492 ist es nicht).

**Beides noch am selben Tag erledigt.** Der Breve-Rest steht in **#526** (190 Tokens: 134 o/u, 48 w/n, 8 Makron; acht Suchbegriffe über alle offenen Issues, kein Vorgang führte ihn). #235 war versehentlich zugegangen: der Merge-Commit `144fbbd3c` enthielt „Kein Closes: #235", und GitHub liest `Closes: #235` als Schließbefehl, die Verneinung davor nicht. Der `<authority>`-Block steht seit Branch `claude/wzb-authority-block` auch in WZB, aus PZ übernommen bis auf die Zeilenenden: WZB ist die einzige Datei in `tei/` mit CRLF im Blob (`.gitattributes` setzt `*.xml -text`, `core.autocrlf` greift dort nicht). Ein `grep -c $'\r$'` in Git Bash meldet für dieselbe Datei 0 CR; byte-genau gezählt sind es 235,999. Indexe und API nach Neubau byte-identisch, kein Bump.

## 2026-10-10 – #451: das Gate zählt nur noch Bestand (Spur C, Paket C1)

**Was geschehen ist.** `doc-count-audit.py` zählt seit diesem PR nur noch, was ein XPath ohne menschliche Definition liefert (Korpusdateien und Authority-Dateien). Weg sind die Playground-Katalogzahlen mit ihren drei Ausnahmemengen, der Zahlwort-Scan, die sieben `INTENTIONALLY_SILENT`-Einträge an Code-Keys und der Kommentarblock in `data-integrity.yml`, der über die Playground-Grenze sprach. Das Skript hat 1002 Zeilen vorher und 715 nachher (`wc -l`), der Body von #451 nennt 954 und trifft keinen der beiden Stände.

**Belegt, nicht behauptet.** Mutationsprobe in zwei Hälften: eine falsche Korpuszahl in `README.md` (667 auf 666) fängt das neue Gate weiter, eine falsche Werkzeugzahl in `playground/readme.md` (11 auf 10) fing nur das alte, das neue bleibt grün. Beide Dateien zurückgesetzt, `git status` leer. Das ist der Preis der Entscheidung, in einer Zeile.

**Prosa.** Katalogzahlen raus aus `hilfe-playground.html`, `README.md`, `playground/readme.md` (auch die Checklistenzeile F3 mit „12 analysis tools“, die das Häkchen-Skip des alten Gates deckte), `docs/DESIGN.md`, `docs/FEATURES.md`, `docs/ARCHITECTURE.md` und zwei Kommentaren in `playground/js/`; Zeilennummern in Skriptkommentaren sind Namen geworden. Ersetzt wurde durch Streichen, nirgends durch eine Allaussage. Die Review-Runden fanden Restzahlen und eine Allaussage, die ich selbst eingebaut hatte („Each analysis tool has ...“). Runde 2 fand zwei weitere in `docs/FEATURES.md`, die Runde 1 und meine Suche übersehen hatten: „six controlled vocabularies“ und „the other ten“. Meine Suche lief über die Nomen (Werkzeuge, Module, Entry Points); die Runde fand sie über Zahlwörter ohne Katalognomen. Wer eine Streichung dieser Art prüft, sucht beide Wege.

**Review auf Opus.** Der `fable-reviewer` lief wegen des Fable-Limits mit `model: opus` (G4 im Laufplan vom 10.10.). Er musste nach 40 Zügen zum Berichten aufgefordert werden.

**Offen, bei der Koordination:** Ä1 (Zeile in `CLAUDE.md`), Ä2 (Kommentar in `no-cdn-check.yml`); und `docs/playbooks/MASTERPLAN-AUTONOME-CAREARBEIT-SESSION.md` Zeile 83 nennt das Erweitern des Gates um code-abgeleitete Counts „umgesetzt 2026-07-14“, was seit #451 zurückgenommen ist.

## 2026-10-10 – #460 und #461: Verbformen von jagât, Säugetierknochen bei gebeine (Spur A, Lauf vom 10.10.)

**Was geschehen ist.** #460: 145 der 185 Tokens von `lemma_3103` jagât (NOM) sind Verbformen (`jaget` 109, `jeit` 35, `jait` 1, 51 Dateien) und stehen jetzt auf `lemma_3102` jagen (`VRB`, ohne `@ana`, drei neu geprägte Variantentypen `type_372855` bis `type_372857`). Die 35 Substantive und die 5 unklaren Belege (`AXU_18452_5`, `WVW_6542_4`, `WH_28126_1`, `JT_48611000_4`, `JT_43134000_4`) sind unberührt; die Einstufung ist ein Leseurteil am Kontext, die Schreibung trennt die Klassen nicht (`jaget` und `jeit` tragen auch 14 echte Substantive). #461: `lemma_1958` gebeine bekommt `lemma_1958_sense_119196` mit `concept_14011100`, 21 Säugetier-Belege in 15 Dateien tragen ihn als `@ana`. Korpus-Index 4.2.32, Authority-Index 1.9.23. Arbeitslisten unter `ingest/pos-disambig/460-jagat/` und `ingest/review/461-gebeine/`, Skripte `apply-460-jagat.py` und `apply-461-gebeine.py` prüfen den Ist-Zustand vor dem Schreiben.

**Belegt.** Beide Tabellen gegen `tei/` nachgelesen (185 von 185, 207 von 207). Die variants-Änderung ist genau die erwartete: 3 Typen dazu, 1 entfällt (`type_115155`), `n` bei `type_10674` 122 auf 13 und bei `type_10676` 39 auf 4. Das Flip-Gate meldet drei gewollte Umklappungen (`jaget`, `jeit`, `jait` von `lemma_3103` auf `lemma_3102`), die Quittung deckt genau sie. Alle CI-Schritte aus den Workflow-Dateien lokal gefahren, die Frische-Schritte reproduzieren byte-gleich; `npm test` auf Port 8084: VOLLLAUF GRUEN, 473 Tests in 50 Dateien. Review auf Opus (Fable am Limit): Runde 1 auf einem größeren Stand, Runde 2 auf dem Stand dieses PR ohne Befund am Diff. Chrome war nicht verbunden; ersatzweise ein headless-Playwright-Wegwerfskript gegen Port 8084 (nicht im Repo): die Lemmaseite von `gebeine` zeigt „Bedeutung 3: Körper/Gliedmaßen von Säugetieren“; die Suche nach `jagen` meldet 1.551 Treffer (1.406 vorher plus 145), die nach `jaget` 1.591 mit `jagen` vor `jagât` (1.551 plus die 40 verbliebenen). Das ist kein hart neu geladener Chrome-Lauf, sondern ein frischer Browserkontext. **Laufzeitwirkung:** keine Änderung an Build, Gate oder Test; die Build-Skripte ändern nur ihre Versionsliterale, der Volltest lief wie zuvor durch.

### Was über den Einzelfall hinausgilt

**Ein Feld, das aus zerlegten Tags zählt, erzeugt Gleichstände dort, wo es am meisten zu unterscheiden gäbe.** Aus #462 (pos und posAll aus dem Korpus): ein Token `NEG VRB` zählt für beide Teile, bei Negations- und Partikelverben stehen sie deshalb exakt gleichauf, und die Reihenfolge im Lexikon entschied. Die Vorab-Messung hatte 6.859 Gleichstände genannt und sie als unproblematisch geführt; mein erster Entwurf schrieb „die häufigste Wortart“ in die Doku, was bei Gleichstand nicht stimmt. Der Reviewer hat es gefunden (156 Lemmata, die nur durch einen Gleichstand ein neues pos bekamen). Die Entscheidung „das Inhaltswort gewinnt“ hob die Zahl der abweichenden pos von 1.537 auf 5.653 (beide von 9.987 mehrwertigen Lemmata mit Korpusbeleg), weil sie auch die 4.116 Gleichstände erfasste, bei denen der Lexikon-Erstwert gleichauf vorn lag. Daraufhin hat chsteiner #462 angehalten und KZW gefragt; der Stand liegt auf `claude/462-lemma-pos`, die Zerlegung in `ingest/pos-disambig/462-pos/README.md` auf diesem Zweig. **Vor der Regel die Grundmenge zerlegen, nicht nur die Fälle, auf die sie zielt.**

**Ein Test, der eine Reihenfolge festschreibt, die ein Ingest kippen kann.** `cooccurrence-ranking.spec.js` erwartete für `salve` `posAll` `['NOM','VRB']`; im Korpus steht NOM 15 gegen VRB 16. Der Test gehört zu A3 und ist mit ihm herausgenommen.

### Rote Zeilen

Keine.

### Was zurück an Christian geht

- **#460, an KZW:** die 5 unklaren Belege (Kontext in `belege.tsv`), Frage nach dem Merge.
- **#461, an KZW:** die 6 Tierbelege ohne Säugetier (Hahn, Fisch, Phönix, drei Drachen), die 9 offenen Belege und `concept_21104000` an `lemma_1958_sense_3004`, Frage nach dem Merge.
- **#462, an KZW:** gestellt (Gleichstand durch zerlegte Tags, dazu 22 Lemmata, deren häufigster Korpus-Tag im Lexikon nicht geführt wird); #462 steht auf `auto:blocked`, `wait:kzw`.
- Die Chrome-Prüfung in einem echten Browser steht aus (Erweiterung nicht verbunden), ersetzt durch das Playwright-Skript oben.

## 2026-10-10 – #463: Stufe 1 ohne Korpusbeleg hält Stufe 2 nicht mehr ab (Spur lauf-b-suche)

Entschieden war nur Stufe 2: Bringt Stufe 1 keinen belegten Treffer (Eintrag in `corpusIndex.lemmaIndex`), wird die Variantenliste mitgefragt, die Stufe-1-Treffer bleiben hinten in der Liste. Haupt- und Playground-Auflösung benutzen dasselbe Prädikat (`lemma-resolve.js`), die Schleifen bleiben je Seite. Gemessen (Authority 1.9.22, Korpus 4.2.31): 1.285 von 43.710 Lemmata ohne Beleg, `lemmaIndex` hat für die belegten genau einen Eintrag, 0 leere. Zeilen: `rosse` 0 auf 184, `gat` 0 auf 525, `hanc` 0 auf 0, `roz` 1 auf 1 (`rôz` ist belegt), `lenden` 20 auf 20.

**Review auf Opus (G4), zwei Runden.** Runde 1 fand, dass der erste Entwurf Stufe 3 mitfragte, obwohl der Entscheidungstext sie nicht nennt (`Cordoba` löste per Präfix auf `cor` auf); Stufe 3 läuft wieder nur bei leerer Stufe 1 und 2. Runde 2 fand, dass der Playground unbelegte Homographen ungerankt zurückgab (`vlâder` gegen `vlader`); die Gleichstandsregel gilt jetzt auch ohne Beleg.

**Folge, die bleibt:** Wer die Schreibform eines unbelegten Lemmas als Suchbegriff weitergibt (Wortbestandteil-Suche, "Im Korpus suchen"), landet beim belegten Lemma der Variante. Von 1.285 unbelegten Lemmata trifft das bei 573 (je Lemma gezählt). Eine ID-Übergabe nach CONTRACTS §C.1.1 würde es schließen und ist nicht Teil dieses Zuschnitts.

**Runde 3** (Opus, nur das Delta) ohne Befund. **Runden 4 und 5** gehören dem CI-Bot-Kommentar zum PR: Er fand, dass der Playground-Rückfall `lemmaIndex || {}` (ein leeres, aber wahres Objekt) den Rückfall "ohne Index gilt alles als belegt" umging. Meine erste Antwort, eine `for...in`-Leerprüfung in `isAttestedLemma`, fand Runde 4 als Laufzeitfehler: O(n), gemessen ca. 4 ms je Aufruf bei 42.460 Schlüsseln, dreimal je Suche. Die Prüfung sitzt jetzt einmal je geladenem Index-Objekt in `authority-manager.js` (`getAttestationIndex()`), `isAttestedLemma` blieb ein Property-Zugriff. Lehre: ein O(1) aussehendes `for...in` mit `break` ist auf einem Objekt mit vielen Schlüsseln nicht O(1). **Nachgezogen:** DATA-MODEL.md Z. 643 ("first match wins"), DEVELOPMENT.md und der Modul-Docstring von `compare-findebuch-resolution-259.py` sagen jetzt, dass das Skript die Auflösung vor #463 nachbildet; sein Verhalten bleibt unverändert, die Anpassung ist Folgearbeit in #259 (der Funktions-Docstring Z. 295 behauptet noch "wie produktiv"). Der Kommentar in `lemma-explorer.js` Z. 874 geht an Spur C.

## 2026-10-10 – #434: Die Korpussuche hat einen URL-Zustand und Browser-Zurück funktioniert (Spur lauf-b-suche)

Entschieden (chsteiner, 10.10.): In der Adresse stehen der Suchbegriff und der geöffnete Text samt Fundstelle, sonst nichts. Die Suche schreibt `?search=` per `replaceState`, `openText()` schreibt `&textId=` (bei KWIC-Treffern `&position=`) per `pushState`, ein `popstate`-Handler öffnet oder schließt das Lesepanel, `handleURLParameters()` sucht zuerst und öffnet dann. Der alte `replaceState`, der die Parameter wegputzte, ist weg; die Begründung dafür stand nirgends (`6b339c57c` "keeps URL clean", `ddadb06ae` übernahm das Muster als Konvention). Neu im Reader: `closeReadingView()`, die ein laufendes Laden verwirft (`_loadSeq`), sonst öffnete ein Schließen während des Ladens das Panel nachträglich.

**Review auf Opus (G4).** Runde 1 fand: Nach Browser-Zurück blieb die Autorzeile des geschlossenen Textes stehen (`showEmptyState` lief vorher nur auf frischem Panel, nie auf einem befüllten); der Test "Schließen während des Ladens" wartete fest 5 s und wäre bei einem Großtext auch ohne Abbruch grün gewesen. Mutationsprobe danach: Zeile `_loadSeq` in `closeReadingView` auskommentiert, `VERDICT: ROT`, zurückgenommen, `git diff` leer.

**Laufzeit (#564).** Die Specs öffnen nicht mehr den ersten Treffer von "minne" (ein Großtext, JT hat 44 MB), sondern den kleinsten Treffertext. Die neue Spec: 9 Tests, Summe 77,7 s.

**Bekannte Grenze:** ein Text, der aus einem Sigle-Link im Lesepanel geöffnet wird, ist noch kein History-Schritt. Bricht die Suche nach Browser-Zurück ab (leere Textauswahl), bleiben Suchfeld und Adresse bei der zuletzt ausgeführten Suche.

## 2026-10-10 – #564 E1: Die leichten Gates holen den Korpus nicht mehr (Spur lauf-e-ci)

`tei/` ist 1.366 von 1.651 MiB des Baums, und der Checkout war bei `no-cdn-check` (median 117 s von 124 s Job) und `file-size-check` (115 s von 119 s) der ganze Job. Jetzt: `no-cdn-check` 12 s Checkout, 20 s Job (5 Läufe); `file-size-check` 1 s und 6 s (5 Läufe). Gemessen per `workflow_dispatch` auf einem Wegwerfzweig, Vorher aus den letzten 25 erfolgreichen Läufen.

**Drei Funde, die kein Gate gemeldet hätte.** (1) Ohne `tei/` zählt `doc-count-audit.py` "Korpus-Dateien 0", überspringt alle neun `corpus_files`-Paare ("pruefen derzeit nichts") und endet mit Exit 0: ein stilles Grün, die Prüfung wäre weg gewesen. Es liest nur die Dateinamen, also leere Platzhalter aus `git ls-tree` mit Guard 667 = 667; Mutationsprobe 667 auf 665: mit Platzhaltern rot, ohne `tei/` grün. (2) `check-no-cdn.py` und `check-no-em-dash.py` lesen auch `ingest/` und `examples/` (HTML-Prüfseiten, Markdown); ausgeschlossen wird deshalb nur `tei/*.tei.xml` und `data/*.json.gz`, und ein Kontrollschritt verlangt, dass jede andere getrackte Datei im Arbeitsbaum liegt. (3) `sparse-checkout` schaltet in der Action `--filter=blob:none` ein; `git ls-tree -l` lädt dann jeden Blob einzeln nach (Lauf 38047147806, Timeout nach 5 min 10 s), der volle Abruf ohne Arbeitsbaum brauchte 197 s. Die Zeit steckt im Abruf der 193 MiB, nicht im Schreiben. Lösung für den Größenwächter: Größen aus der Trees-API (`--github-tree`), Pfad für Pfad gegen `git ls-tree -r -z HEAD` belegt (G3 der Koordination).

**Nicht übernommen:** derselbe sparse-Checkout für `data-integrity` und `measured-counts` war langsamer (167 s gegen 72 s, 345 s gegen 98 s), weil `tei/` danach nachgeladen wird. Lehre: ein Gate, das seinen Baum verkleinert, braucht einen Kontrollwert außerhalb des Zuschnitts, und die Beschleunigung braucht die Messung am echten Runner; der Gedanke "weniger Dateien ist schneller" stimmte bei zwei von vier Workflows nicht.

## 2026-10-10 – #564 E2: Data Integrity läuft in zwei parallelen Jobs (Spur lauf-e-ci)

Ein Job mit 24 Schritten summierte sich auf median 475 s (25 erfolgreiche Läufe vor 11:00 UTC; Checkout 72, RelaxNG-Validierung 212, Index-Rebuild 74, variants-Freshness 43, Cross-Refs 35). Jetzt zwei Jobs: `validate` (Schema- und Spiegel-Gates auf dem committeten Stand) und `freshness` (alles, was neu baut und vergleicht). Wanduhr median 349 s (5 Läufe, 296 bis 417), Job `validate` 340 s, Job `freshness` 296 s; die Summe der Job-Sekunden steigt von 475 auf 607 (zwei Checkouts). Der längere Job bleibt `validate`, weil die Validierung allein 212 s braucht; sie auf zwei Shards zu verteilen brächte rechnerisch rund 50 s Wanduhr gegen einen dritten Checkout und eine neue Option im Skript, und `freshness` läge dann mit 296 s vorn.

**Nicht gemacht, mit Grund:** die RelaxNG-Validierung bei PRs ohne `tei/`-, `authority-files/`- und `schema/`-Änderung zu überspringen. Der Gewinn wäre nach der Teilung klein (Wanduhr bestimmt `freshness`, nicht `validate`), der Preis eine Lockerung: ein roter Stand auf `main` würde bei späteren Skript-PRs nicht mehr auffallen, und `data-integrity` hat keinen Wochenlauf, auf den man sich dafür stützen könnte.

**Beleg, dass kein Gate etwas verliert.** Mechanisch: beide Fassungen als YAML geparst, jeder der 24 Schritte steht mit identischem Inhalt in genau einem Job (drei, Checkout/Python/Install, in beiden), Reihenfolge je Job eine Teilfolge der alten, `on:` und `concurrency` gleich. Mutationsprobe auf einem Wegwerfzweig (variants.xml: Zähler einer Form geändert; tei/EUS.tei.xml: `<bogus/>` im Body): `validate` rot am Schritt "Validate corpus" (`RELAXNG_ERR_ELEMNAME … got bogus`), `freshness` rot am Schritt "Freshness variants.xml", jeweils der erwartete Schritt. Ein Reviewer fand dazu drei Kommentare, die der Umbau falsch gemacht hatte (z. B. "vor der RelaxNG-Validierung" über dem Cross-Ref-Gate, das jetzt im anderen Job steht): ein Kommentar über die Reihenfolge ist eine Aussage über das Gate und muss mit dem Umbau umziehen.

## 2026-10-10 – #564 E3: Laufzeitbudget der CI-Schritte

Bis hierher wurde in den PR-Workflows nichts rot, wenn ein Schritt langsamer wurde; es gab nur `timeout-minutes` (5, 5 und 20 Minuten, in `data-integrity.yml` 45). Jetzt endet jeder Job von `no-cdn-check`, `file-size-check`, `measured-counts` und `data-integrity` (beide Jobs) mit einem Schritt (`if: always()`), der die Dauern der fertigen Schritte über die Actions-API liest und gegen `scripts/audit/runtime-budget.json` hält (Grenze Budget mal 1,5, Checkout mal 1,3, Untergrenze 10 s, Entscheidung chsteiner). Rot nur am PR; auf push und dispatch ein Kommentar in #574, nur auf `main`.

**Warum letzter Schritt und kein `workflow_run`:** ein `workflow_run`-Workflow läuft im Kontext von `main`, läse das Budget nicht aus dem PR und wäre erst nach dem Merge testbar. `claude-code-review.yml` bleibt unberührt, die Action verlangt, dass die Datei der auf `main` gleicht.

**Fail-closed:** auf einem PR ist jede unmögliche Messung (API, Job nicht gefunden, kein fertiger Schritt, Budgetdatei kaputt) Exit 2. Ein schon roter Job bekommt nur eine Warnung, damit das Gate die Ursache weder verdeckt noch verdoppelt. Selbsttest mit 28 Fällen, darunter eine Mutation (Faktor und Untergrenze 0 färbt jeden Schritt rot); Trockenlauf gegen eine echte API-Antwort ohne Überschreitung.

**Offen:** die Budgets von `no-cdn-check`, `file-size-check` (je 3 bis 4 Läufe seit E1) und `measured-counts` (6) sind "n unter 10, vorläufig" und werden nachkalibriert (`--measure --since`). Der erste PR-Lauf zeigte den Fehler, den der Reviewer als ungeprüft markiert hatte: die Jobs-API führt den Schritt direkt vor dem Gate noch als `in_progress`, in jedem Job fehlte also genau der letzte, oft größte Schritt (in `validate` die 227 s der RelaxNG-Validierung) und das Gate blieb stumm grün. Ein laufender Schritt zählt jetzt mit "jetzt" als Ende, vier neue Selbsttestfälle. Das reichte nicht für `file-size-check` (3 von 4 Schritten, die API führte den Schritt noch ohne Startzeit), also fragt das Skript bis zu sechsmal nach, solange ein Schritt vor dem Gate weder fertig noch laufend ist, und ein danach unmessbarer Schritt ist auf dem PR rot. Danach meldeten alle Jobs ihre vollständige Schrittzahl (11, 4, 4, 12 und 14 in `no-cdn-check`, `file-size-check`, `measured-counts`, `validate`, `freshness`). Lehre: ein Gate, das Daten über sich selbst liest, bekommt sie vom Lauf, der noch läuft; "alle Schritte gemessen" ist eine Zahl, die man im ersten echten Lauf gegen die Schrittliste zählt. Die Delta-Runde über genau diese Korrektur fand zwei Fehler darin, die erst die Korrektur geschaffen hatte: die Wartezeit der Wiederholungen wurde dem laufenden Schritt angerechnet (ein 0-s-Schritt hätte 10 s bekommen und die feste Grenze gerissen), und auf push verschluckte ein unmessbarer Schritt den ganzen Bericht samt Kommentar in #574. Der Start des Skripts ist jetzt das Ende des laufenden Schritts, und Exit 2 gilt nur auf dem PR. Eine Korrektur am Gate braucht dieselbe Review-Runde wie das Gate. Reviewer-Frage: ein Faktor 1,3 auf einen 12-s-Checkout lässt nur 15,6 s; Rauschen von wenigen Sekunden wäre ein roter PR.

## 2026-10-14 – #486: Editionsnachweis-Kette Zotero → works.xml → Header

Spur `lauf-486`. Umgesetzt: der Header-`biblStruct` (`listBibl`) bekommt einen chirurgischen Schreiber und ein Gate in `sync_tei_headers.py`, der Online-Sync der Großschreibung ist in `works.xml` und in 183 Headern, FLG wird über den Zotero-Schlüssel ATWPNQPS zugeordnet, FR3 steht als befristete Ausnahme im Skript. Authority-Index 1.9.25, kein Korpus-Bump. Die Regeln der Kette stehen in CONTRACTS.md F.4a.

**Was die Ticketangaben und die Messung auseinanderbrachten.** (1) Der Body nannte für die Frauenlob-Handkorrektur FR1/NCQNST4V. Sie hängt an FR3/MVWV5QYG: `115c3a01f` ändert in `works.xml` den Block `key="FR3"`, und der Sync hätte FR3 mit dem Inhalt von FR1 und FR2 überschrieben. FR1 bleibt beim Sync unverändert. (2) Der Body nannte "drei Abweichungen" zwischen Header und `works.xml`. Gemessen elementweise über alle 667 Header: von 678 Blöcken mit `@corresp` stehen 553 gleich, 119 nur in anderer Kindreihenfolge und 5 in 3 Dateien anders (FR3: Pfad des einzigen `<ref>`, HZ und LUU: nur die `@xml:id`-Suffixe); dazu der AK-Block mit 2 Zusatzelementen nur im Header und WZB ohne `@corresp`. Daraus wurde Enthaltensein statt Gleichheit. (3) 171 Werke und 187 Titelelemente stimmten (184 `biblStruct`, nur Großschreibung, kein Großbuchstabe fällt weg).

**Was über den Einzelfall hinausgilt.** Ein Header, der eine Kopie plus textspezifische Ergänzungen trägt (AK, #134), lässt sich nur mit Enthaltensein prüfen und nur mit einem Schreiber pflegen, der Änderungen überträgt, statt den Block zu ersetzen. Daraus folgt eine Grenze, die dokumentiert und nicht behoben ist: ein Element, das in `works.xml` verschwindet oder seine Attribute ändert, steht im Header weiter oder doppelt, und das Gate sieht es nicht. Ein Sync, der eine Ausnahme tragen muss (FLG, FR3), trägt sie im Skript als benannte Konstante mit hartem Abbruch, nicht als Handkorrektur danach: der Lauf mit den zwei Ausnahmen ist byteweise gleich dem Lauf mit Handrücksetzung. Review: vier Runden, in Runde 2 zwei Befunde der Klasse A, die erst die Korrekturen aus Runde 1 geschaffen hatten (ein Tail-Vergleich über eine Schlüsselmenge machte ein erlaubtes Zusatzelement zum Fehler, und beim Verallgemeinern des Ersetzens fiel der Guard weg, der verhinderte, dass ein Container mit Kindern durch ein Blatt ersetzt wird). Beides unerreichbar im heutigen Korpus, beides vor dem Push gefunden. Ein dritter Fehler kam **nicht** aus dem lokalen Review, sondern vom CI-Bot auf dem gepushten PR, nach drei sauberen lokalen Runden: bei gleichem Anfang lief die Einfügung vor dem ersten Kind vor der Ersetzung desselben Kindes, die Ersetzung traf die eingefügten Bytes (Traceback). Die Mutationsproben der Runden 1 bis 3 setzten nie ein neues und ein geändertes erstes Kind zugleich. Der Bot-Kommentar ist hier gelesen worden, obwohl alle Checks grün waren: genau dafür steht diese Regel in CLAUDE.md.

**Rote Zeilen.** Keine. Die zwei A-Befunde der Runde 2 sind im Kern der Lehre aus #397 ("was hing am Gegenteil dessen, was die Änderung wahr macht"), wurden aber von der Reviewrunde abgewendet, bevor sie trugen.

**Was zurück an Christian geht.** (1) Das Zotero-Item MVWV5QYG (FR3) trägt den Inhalt von FR1 und FR2; die Frage an KZW steht in #486, bis zur Korrektur gilt die Ausnahme im Skript. (2) `BESTAND_BEHALTEN` hält für FLG Angaben fest, die nicht aus Zotero kommen: `analytic`, `editor`, `imprint` und `note` (Buch 1-2, Vollmann-Profe, 1990 gegen Buch 1-7, 1990-1993 bei FLG1). (3) Kommentar und Name des Steps "Werk-Identifier" in `data-integrity.yml` sagen nur `msIdentifier`; die Koordination zieht sie nach (Ä1 im Laufplan). (4) Die Grenze oben: verschwundene Elemente werden nicht propagiert.

## 2026-10-14 – #554: Glossar Kochbuchforschung ins Lexikon

Spur `lauf-554`. Umgesetzt: 93 Kommentare aus dem Glossar Kochbuchforschung stehen als `<note type="comment">` (`resp="contributors.xml#contrib_003"`, höchstens eine je Bedeutung) in `lexicon.xml`; Authority-Index 1.9.26, kein Korpus-Bump. Von den 189 mhd. Einträgen sind 120 einer Bedeutung zugeordnet, 17 offen, 52 ohne Kommentar. Von den 120 gehen 93 in die Daten, 22 als größere Kürzung, 1 als sachliche Rückfrage (grandmangerie: Verfasserangabe gegen `works.xml`) und 2 als Zusammenführung (huon, rëphuon) auf die Prüfseite `examples/review-pages/Glossar-554-Pruefung.html` (47 Fälle: A 17, B 22, C 5, D 1, E 2); 2 sind in diese beiden aufgegangen (henne, rëphenne). Lemmata mit kuratierter Aussage (Zählregel ADR-018): 1 von 43.710 vorher, 94 nachher. B5: Verweistabellen auf das Portal der Pflanzen des Mittelalters (nur Titel, URLs, Zuordnungen). Zahlen und Kriterien: `ingest/glossar-554/UEBERNAHME.md`.

**Was über den Einzelfall hinausgilt.** (1) Eine Hilfssuche, die entfallene Textteile meldet, ist ein Hinweis und kein Beweis, und ihre Ausschlussregeln wirken in allen Einträgen: die Regel "Fußnote, URL, Seitenzahl, Literatur gilt als (b)" hat in 6 von 93 Einträgen mehr als eine Fundstelle verschluckt (drei auf der Prüfseite, drei im Text ergänzt). Wer so eine Regel schreibt, misst sie über den ganzen Bestand, nicht an den Fällen, die sie gerade zeigen. (2) Ein Lemma trägt je Bedeutung nur eine Notiz; zwei Glossareinträge mit derselben Bedeutung (henne und huon) lassen sich nur zusammenführen, und das ist, wenn die Poetisierungsteile verschieden sind, mehr als gleicher Text und eine Entscheidung für KZW. (3) Bis zu diesem PR trug genau ein Lemma einen Kommentar; Tests, die über "alle Kommentare" iterieren (`comment-attribution.spec.js`), laufen jetzt auf einer festen Stichprobe, weil 97 Seitenaufrufe unter der 60-Sekunden-Grenze nicht passen. Das wäre ohne die #397-Frage des Reviewers erst in der CI aufgefallen. (4) Fremder Text unter dem Namen der Urheberin: brôt enthält im Feld "Enzyklopädische Information" einen Zitatblock aus Peter C. A. Schels (Feldanfang "Informationen aus: …, 17.11.2017", rund 8.400 Zeichen); er ist nicht in den Daten, sondern Frage an KZW. Der Fundort ist das Feld selbst, nicht mit der Quelle abgeglichen.

**Rote Zeilen.** Drei, Fehlerjournal 130 bis 132: ein `cd` in das Scratchpad (wieder zu `shell-konventionen.md`), die schmale Reviewrunde ohne `model: fable` (Regel 11 des Betriebsvertrags), und mehrere Aussagen in Docstring und README über den eigenen Text, die die Stelle nicht hergab. Review: drei Runden auf Fable, Runde 1 mit drei A-Befunden (Test über 97 Kommentare, drei übersehene (c)-Teile, zwei Umformulierungen), Runden 2 und 3 ohne A-Befund; dazu eine abgebrochene Opus-Runde.

**Was zurück an Christian geht.** (1) KZW: die Prüfseite (47 Fälle) mit der Frage zur Zuordnung, zu den 22 Kürzungen, zu den 5 nicht übernommenen Einträgen, zu grandmangerie und zu huon/rëphuon; erst nach ihrer Antwort geht ein Fall in die Daten. (2) brôt: Schels-Auszug, siehe oben. (3) Ein Klug-Link an der Lemmaseite wäre eine Schema- und Frontend-Entscheidung; Linkziel nach KZW die übergeordnete Pflanzenseite. Klugs Seiten verlinken ihrerseits schon in die MHDBDB. (4) `dornber` (KZWs Beispiel einer bei Klug verzeichneten Form) steht in Klugs gmh-Liste nicht und in den 27 abgerufenen Seiten nicht; ob er in einer anderen Sprachstufe steht, ist nicht untersucht. (5) B4, Einklappfunktion für lange Kommentare: Vorschlag in `UEBERNAHME.md`, 61 von 93 Texten über 600 Zeichen, nicht umgesetzt. (6) Die Geviertstrich-Regel und die Du-Ansprache gelten für die Prüfseite; der Wortlaut der Texte ist über eine Stichprobe hinaus nicht gegen das Original geprüft.

## 2026-10-14 – Lauf mit zwei Spuren (#486, #554): Koordination

Operator-Lauf mit den Spuren `lauf-486` und `lauf-554` (Sonnet, unter dem Betriebsvertrag); Laufplan, Grenzverhandlungen G1 bis G7 und Abnahme in `docs/playbooks/kickoffs/2026-10-14-lauf.md`. Gemergt: #599 (`0258eb9db`, Authority 1.9.25) und #600 (`3dc1b189c`, Authority 1.9.26), nacheinander, die zweite Spur hat dazwischen rebased und den Index neu gebaut. Beide Tickets offen auf `auto:blocked` + `wait:kzw`.

**Was über den Einzelfall hinausgilt.** (1) Die Widerspruchsklausel im Kickoff hat zweimal Ticketangaben gekippt, bevor Daten geschrieben waren: FR1 statt FR3 in #486 (die Angabe stand im Body, in einer Frage an KZW und im Kickoff) und "drei Abweichungen" im Header, wo 125 Blöcke abwichen, alle begründet. (2) Eine Längenschwelle (60 %) trennt "gestrafft" nicht von "inhaltlich gekürzt": `brî` lag mit 0,62 darüber und verlor trotzdem eine ganze Aufzählung. Was trennt, ist KZWs eigenes Kriterium, angewandt auf jedes entfallene Stück (G5). (3) Ein rotes Laufzeitbudget lässt sich an einem Schritt beurteilen, dessen Eingaben der PR nicht berührt: `lemma-pos` liest nur `tei/` und wurde ohne eine geänderte Datei dort von 18 auf 34 s langsamer. (4) `gh pr view --json files` schneidet bei 100 Dateien ab, ohne es zu sagen; die Dateiliste eines Daten-PR kommt aus `git diff --name-only`.

**Rote Zeilen.** Eine aus der Koordination, Fehlerjournal 121 (FR1 ungeprüft aus dem Ticket in den Kickoff übernommen, obwohl `git show 115c3a01f` ein Aufruf war). Aus den Spuren 130 bis 132 (`lauf-554`), aus `lauf-486` keine.

**Was zurück an Christian geht.** (1) Ein Datenmodell für Klug-Links an der Lemmaseite (Schema und Frontend). (2) Der Einklapp-Vorschlag für lange Kommentare (PR #600, `UEBERNAHME.md`). (3) Die Gate-Grenze aus #486: aus `works.xml` verschwundene Elemente bleiben im Header stehen. (4) `BESTAND_BEHALTEN` für FLG hält Angaben ohne Zotero-Quelle fest.

## 2026-10-15 – Lauf mit einer Spur (#554) und zwei eigenen PRs: Koordination

Laufplan, Grenzverhandlungen G1 bis G6 und Abnahme in `docs/playbooks/kickoffs/2026-10-15-lauf.md`. Spur `lauf-554b` (Sonnet) hat KZWs Antworten auf die Prüfseite eingearbeitet: #606 (`2ccb54659`, Authority 1.9.27, Korpus 4.2.33, neues Lemma briech). Die Koordination hat daneben #604 (`e8d533e98`, Dateiliste eines PR über `git diff`) und #605 (`9b2e02f86`, listBibl-Gate mit `ERLAUBTE_ZUSAETZE`) gebaut. Neue Tickets: #602 (naschen-Belege), #603 (Ernährung von Tieren). #554 und #486 offen auf `auto:blocked` + `wait:kzw`.

**Was über den Einzelfall hinausgilt.** (1) Der Probelauf mit einer zusätzlichen Fable-Runde 1 (#605) fand ein A, das beide Modelle fanden, und ein A, das nur Opus fand (ganzer Block mit Zotero-`@corresp`, der aus `works.xml` verschwindet). Eine Allowlist für „nur im Header“ hat drei Ränder: Kindelemente, einen in `works.xml` geleerten Container und ganze Blöcke. (2) `gh pr view --json files` ist in gh selbst auf 100 gekappt (`files(first: 100)`), und die Plattform liefert für manche gemergte PRs auf allen Feldern 0. Ob ein Diff berechnet wurde, zeigt nur das Job-Log, und auch dessen `<changed_files>`-Block endet bei 100. (3) Ein Freeze mit benannten Ausnahmen trägt: Drei Ausnahmen waren nötig (eine Zeile in `CLAUDE.md`, `variants-flips-ack.json`, zwei Zahlen in `schema/README.md`), jede steht mit Grund im Laufplan. (4) KZWs Rückfragen setzen manchmal eine Lage voraus, die das Korpus nicht hat („Verweise auf die Textstellen setzen“ bei lêrchenvuoʒ, das im Korpus nicht vorkommt). Das klärt eine Messung, bevor ein Lemma angelegt wird.

**Rote Zeilen.** Zwei aus der Koordination: Fehlerjournal 122 (Klug-Link-Frage ohne KZWs Vorgabe vom 13.10.) und 123 (Datum 16.10. erschlossen statt abgelesen). Aus der Spur 125.

**Was zurück an Christian geht.** (1) Fehlerjournal 125 ist laut Spur die vierte Zeile zur Lehre aus `agentenbefunde.md` (Kette 116, 117, 132, 125). Der Mechanismuswechsel nach `wiederholte-fehler.md` war bei der dritten fällig und ist ausgeblieben. (2) Nachzuziehen, solange es eingefroren war: der Kommentar in `.github/workflows/data-integrity.yml:52-53` zu den erlaubten Header-Zusätzen und `docs/playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md:357-360` zu `--json files`. (3) Bei KZW: Klug-Verweise und Einklappen (Kommentar 6194629707), FLG in Zotero (#486), die Abnahme mit den Fragen zu briech, brî ADJ, slunthart, lêrchenvuoʒ und den Altzählungen (Kommentar 6196973713).

## 2026-10-16 – Lauf mit einer Spur (#460, #461) und sieben Subagenten: Koordination

Ausgelöst durch einen Issue-Audit über 78 offene Tickets (448 von 448 Kommentaren gelesen), danach die Entscheidungen von Christian per `/entscheiden`. Laufplan, Grenzverhandlungen G1, G2, D3 und Abnahme in `docs/playbooks/kickoffs/2026-10-16-lauf.md`. Gemergt: #610 (#93 Textreihen-Browser, `861476a25`), #611 (Prüflisten zu #462, #603, #554, `f8a49ef1a`), #612 (Spur `lauf-1016-daten`, #460/#461, `7a11b4dd9`, Authority 1.9.28, Corpus 4.2.34). Fragen an KZW in #419, #460, #461, #462, #554, #579, #603; Abnahme an Julia in #93; #434 geschlossen.

**Was über den Einzelfall hinausgilt.** (1) Der Probelauf mit einer Fable-Runde 1 neben dem Opus-Gate fand auf #610 dieselben Befunde in beiden Modellen und auf #611 bei Opus mehr (stilles Überspringen von Eingaben, Wortwahl "Handurteil" für Agentenurteile); bei Fable nichts, was Opus nicht auch fand. (2) Eine Vorsortierung über eine Wortliste aus Lexikonformen prüft man gegen die Laufzusammenfassung des Skripts: `du` ist im Lexikon eine Präposition, das Pronomen ist `dû`, und die Regel feuerte deshalb nie, ohne Fehlermeldung. Die Zusammenfassung des Laufs nannte die drei tatsächlich gefundenen Pronomen und hätte es gezeigt. (3) Ein Squash-Merge macht die Commits einer Spur "unpushed", sobald der Zweig auf GitHub gelöscht ist; `claude rm` weigert sich dann zu Recht. Ob nichts verloren geht, zeigt der Vergleich der Bäume (`rev-parse <zweig>^{tree} <squash>^{tree}`). (4) Der Status einer Hintergrundspur kommt aus `claude agents --json`, nicht aus ihrer Antwort: sie meldet ihren Stand nach dem Lösen einer Rückfrage, nicht den davor (Fehlerjournal 133).

**Rote Zeilen.** Eine aus der Koordination, Fehlerjournal 133. Aus der Spur 138.

**Was zurück an Christian geht.** (1) #453 wird am 22.10. unter "Ball bei uns" rot, gewollt, keine neue Frage an KZW. (2) Den MPS-Export im Inventar erfassen; er liegt jetzt in `DigitalHumanitiesCraft/medieval-plantnames-archive` (privat, Ordner `mps/`), nicht mehr nur in CoReMA. (3) Die Frage zum PLUS-Logo im Seitenfuß (#93). (4) Die Prüfseite für #603 als Folgepaket, falls KZW sie will. (5) Einklappen und Literaturanzeige für #554 waren nicht in diesem Lauf. (6) Zur Lehre aus `agentenbefunde.md` (Fehlerjournal 125, 133) ist kein Mechanismuswechsel offen: die begründete Aussetzung (#58) ist der Mechanismus, entschieden von chsteiner am 16.10. und in 125 nachgetragen. (7) `claude-code-setup` ist während des Laufs von `ef3abe9` auf `ee80d66` gegangen (40 Commits, darunter `rules/modelle.md`); der Lauf hat die Gate-Regel vom Start befolgt.

## 2026-10-18 – Spur lauf-1018-frontend, PR 1: Playground und Lemmaseite (#251, #58, #554 Einklappen)

Spur `lauf-1018-frontend` (Sonnet, unter dem Betriebsvertrag, Laufplan `docs/playbooks/kickoffs/2026-10-18-lauf.md`). Umgesetzt auf Julias Abnahme vom 16.10. und KZWs Wunsch vom 16.10.: (#251) im Wortbestandteil-Modus stehen die Namen der gewählten Schreibformen neben dem unveränderten Zähler (`#componentPickList`); (#58) die Fundstellen-Liste je Lemma in der Karte der Dokumentsuche scrollt in sich (`.beleg-liste`, 36 rem); (#554) Lexikonkommentare über 600 Zeichen stehen auf sechs Zeilen gekürzt mit "Weiterlesen", auf der Lemmaseite und im Lemma-Explorer (neues Modul `assets/js/lib/collapsible-text.js`). Dazu die Antwort für #448 (Kommentar nach dem Merge): der Kontext im Export der Dokumentsuche ist fest 10 Wörter je Seite; 24.958 von 24.995 Treffern von minne und herze haben beide Seiten voll, die übrigen 37 liegen am Textrand, und die Zeichenlänge der vollen Fenster schwankt zwischen 75 und 148 (Median 102), weil die Wörter verschieden lang sind.

**Was über den Einzelfall hinausgilt.** (1) Eine Funktion, die nach `innerHTML` Layout misst (`clientHeight`, `scrollHeight`), läuft ins Leere, solange ein Elternteil `hidden` trägt: auf der Lemmaseite steht `renderLemma` vor dem Aufdecken von `#lemmaContent`, jede Höhe war 0, und der Knopf blieb auch ohne verdeckten Text. Der Reviewer fand es in Runde 1 (A); die Spec prüfte nur die drei langen Beispiele und sah es nicht. Wer so eine Nachmessung schreibt, verfolgt den Aufrufpfad bis zum Aufdecken und prüft den Fall knapp über der Schwelle. (2) Julias Satz zu #251 klang nach verlorener Auswahl und war eine Sichtbarkeitsfrage: am Live-Stand blieben nach Filter an und aus beide Häkchen (2 von 2) und der Zähler stand bei 2, nur hieß keine Stelle die Namen. Erst den Prüfweg nachstellen, dann bauen. (3) Eine Suche über die Schreibform findet nicht das Lemma, das man meint: "wîn" trifft 345 Lemmata, die Liste zeigt 50, wîn selbst steht nicht darunter (#545); Specs gehen über die ID.

**Rote Zeilen.** Keine. Trockenlauf-Zeile dieser Session (`lauf-1018-frontend`, Stand der Auswertung vor dem PR): 176 Aufrufe, 65 Treffer (37 %). Beinahe-Fälle, nicht gezählt, weil etwas sie vor dem Tragen abgewendet hat: ein Heredoc im Befehl (der Hook sperrte ihn) und eine `Ohne Review:`-Zeile an einem Commit, der nur das Reviewer-Memory berührt (nach CLAUDE.md trägt der keine; vor dem Push selbst nachgelesen und amendiert).

**Was zurück an Christian geht.** (1) Der Klick auf eine freie Fläche der Fundstellen-Liste klappt die ganze Karte zu, weil `ui-helpers.js:414` nur Links ausnimmt; bei einer scrollbaren Region liegt der Griff näher. Der Reviewer ordnete es als Punkt für den Berater ein, nicht umgesetzt. (2) Der Gegentest "knapp über der Schwelle" trennt mit null Zeilen Marge (`lemma_1079` darben, 683 Zeichen, genau sechs Zeilen bei 1.280 px); er prüft eine Invariante und bleibt bei anderer Schrift grün, kann dann aber nichts mehr unterscheiden. (3) Für F2 liegt die Antwort bei Julia: ist die sichtbare Liste das, was ihr gefehlt hat? Die Zählerfrage (Schreibformen oder Lemmata) bleibt bei KZW.

## 2026-10-18 – Spur lauf-1018-frontend, PR 2: PLUS-Logo im Seitenfuß (#93)

KZW hat am 16.10. geschrieben, das alte PLUS-Logo dürfe seit 1.10.2026 nicht mehr verwendet werden, auch im Haupt-Footer, und zwei Zips angehängt. `assets/images/university-logo.png` zeigte nicht nur das alte PLUS-Zeichen, sondern PLUS plus den Schriftzug "Mittelhochdeutsche Begriffsdatenbank" (1.279 x 828, Verhältnis 1,54). Ersetzt ist es durch die linksbündige Farbvariante aus `Universitat.Salzburg_Logo.linksbundig_Ext.zip`, vom Sicherheitsrand befreit (Inhalt 2.945 x 715 von 3.887 x 1.649) und auf 900 x 219 skaliert (Verhältnis 4,1). Weil sich das Verhältnis ändert, ist die Footer-Höhe von `h-24` auf `h-16` gegangen, 26 Seiten neu gebaut. Das MHDBDB-Logo bleibt: die zweite Zip enthält sechs Varianten als PNG und als EPS (dazu ein PDF); die eine, die ich mir angesehen habe (`Mittelhochdeutsche Begriffsdatenbank.png`), zeigt "UNIVERSITÄT SALZBURG" mit dem Schriftzug "Mittelhochdeutsche Begriffsdatenbank", die übrigen fünf sind nicht angesehen; ob eine davon das bisherige `mhdbdb-logo.png` ersetzen soll, ist eine Frage an KZW im Abnahmekommentar.

**Was über den Einzelfall hinausgilt.** (1) Ein Austausch "unter demselben Namen" ändert keine Seite nur dann, wenn sich Format und Verhältnis nicht ändern; hier wechselte das Verhältnis, und die Höhenklasse im Include war Teil der Darstellung. (2) Julias Befund "Alle anderen Logos außer Clariah und MHDBDB fehlen komplett" ließ sich nicht nachstellen: am Live-Stand laden alle 7 Logos der Textreihen-Startseite (7 von 7, `naturalWidth` größer als 0), und alle 7 Dateien liegen in `textreihen/img/`. Die Koordination hatte denselben Befund am 16.10. Die Logozeile der Textreihen-Startseite enthält weiter kein PLUS-Logo; das wurde nicht ohne Entscheidung ergänzt.

**Rote Zeilen.** Keine.

**Was zurück an Christian geht.** (1) KZW: soll das MHDBDB-Logo durch eine der sechs neuen Varianten ersetzt werden? (2) Julia hat vermutlich eine zwischengespeicherte oder blockierte Ansicht gesehen; ohne Bildschirmfoto bleibt es eine Vermutung.

## 2026-10-18 – Spur lauf-1018-frontend, PR 3: Unterseiten Publikationen und Demnächst im Korpus (#417, #537)

Zwei Hilfe-Unterseiten, beide aus eingefrorenen Ständen unter `data/` gebaut, nie live: `hilfe-publikationen.html` aus den Zotero-Sammlungen WB4HTUGC (88 Einträge) und Z2N4SWWI (205) der Gruppe 5043625, `hilfe-demnaechst.html` aus den offenen `ingest`-Issues (15, davon 0 sichtbar) und einer von Hand gepflegten Zeitplan-Datei. Ein Monatslauf (`monatslauf-seiten.yml`, Muster `naming-index-update.yml`) zieht beide nach und öffnet bei Änderung einen PR.

**Entscheidungen.** (1) Wie der Vorgänger `build-textreihen-bibliography.py`: Marker-Region in der Seite, Stand als JSON, `--offline` und `--check`. (2) Ein Ausfall von Zotero oder GitHub lässt den alten Stand liegen und endet mit Exit 0; auch weniger als die Hälfte der bisherigen Einträge gilt als misslungener Abruf. Probe mit totem Proxy: beide Skripte Exit 0, Stand und Seite unverändert. (3) Das Abrufdatum ändert sich nur mit dem Inhalt, sonst öffnete jeder Monat einen PR. (4) Der Em-Dash eines Zotero-Titels (Naming-analysis) wird erst beim Bauen der Seite ersetzt; der Stand behält den Titel. (5) Ausgeschlossen sind `wait:extern` per Label (auch wenn der Zeitplan das Issue nennt) und elf Issues per Eintrag in der Zeitplan-Datei: Pipeline, WZB schon im Korpus, Zusammenarbeit ohne Text, zwei zurückgestellte, #262 und #263 mit offener Rechtefrage, und #264, #265, #266, #139, die noch nicht genannt werden dürfen (#265: Frage an KZW vom 09.10. offen, #264 hängt daran, #266 ohne Beschluss; #139 ist beschlossen, aber die Lizenz von CoReMA steht laut Body noch offen und die Kochbuchwahl des Piloten auch; die Koordination hat das Lesen der Threads vor der Nennung verlangt, der Reviewer hat meine erste Lesart von #139 "nicht beschlossen" am ganzen Thread widerlegt). Die Seite startet deshalb leer ("Zurzeit steht keine Aufnahme fest"). Der erste Bau hatte #262 und #263 mit Quartal auf der Seite, weil die Spur "offene Rechtefrage" mit dem Label `wait:extern` gleichsetzte; der Reviewer hat es am Thread von #537 gemessen (KZW 08.10.: "erst nach Freigabe nennen", #262 und #263 genannt, #262 seit 06.10. `wait:kzw`). Das Label ersetzt keine Entscheidung aus dem Thread. Die Quartalsvorschläge (262: 2026-Q4, 263: 2027-Q1, 265: 2027-Q2) stehen im Grund der jeweiligen `ausgeschlossen`-Zeile, bis die Freigabe da ist; `"vorschlag": true` würde den Hinweis "noch nicht abgestimmt" auf der Seite einschalten; zurzeit steht es auf `false`, weil kein Quartal drinsteht. (6) Das DOI-Feld in Zotero ist Freitext: von 293 Einträgen standen in 13 Links als `doi.org/https://...` oder relativ; jetzt gilt nur eine echte DOI oder eine Web-Adresse als Link, 87 Einträge zeigen "kein Link hinterlegt". (7) Das Datum gehört zum Abschnitt, damit ein ausgefallener Abschnitt die Seite nicht frischer macht; der PR-Body trägt das Build-Log.

**Rote Zeilen.** Keine.

## 2026-10-20 – Doku-Check (Scorecard)

**Scorecard Doku-Check 2026-10-20** (Anlass: Fälligkeit nach `check-doc-staleness.py --faellig`, 70 Commits an den 14 stabilen Docs seit dem 05.10., erster Lauf als Cloud-Routine nach `docs/playbooks/DOKU-CHECK.md`). Gates alle grün (`doc-count-audit`, `check-doc-inventories`, `check-index-versions`, `build-pages --check`, Em-Dash), geprüft gegen `ede78bca3`; die 12 geänderten Docs haben sechs Agenten vollständig gelesen, jeder übernommene Befund ist selbst nachgemessen. Drei Algorithmen gegen den Code (§A Normalisierung mit Parität über 280.619 Strings, §B Positionszählung, §C Drei-Stufen-Auflösung samt #463) stimmen, die Fehler saßen in den Beispielen (`brott`, `brot`); von drei XPaths stimmte einer nicht beim Leser (`broader` liest `parse_genres`, nicht `build_performance_maps`). **52 Befunde behoben, je Befund ein Commit**, darunter ein Rebuild-Block, der den Authority-Index vor dem Korpus-Index baute und `build-lemma-pos.py` ausließ, „ein kuratiertes Lemma" an vier Stellen bei heute 134 Lemmata mit Kommentar (#554), zwei P-OFFEN-Punkte in POS-TAGSET, die KZW am 10.07. entschieden hatte, fünf ROADMAP-Zeilen, die der Thread überholt hatte (#58, #63, #93, #109, #139), und „~35 bis 40 %" Compound-Tags bei gemessenen 28 %. Zurückgelassen, weil Code statt Doku: `npm run build:data` ruft `build:authority` ohne `--allow-dirty` auf und bricht darum genau nach einem `extract-variants --apply`, das `variants.xml` ändert, ab (DATA-MODEL Schritt 6 nennt das Flag jetzt); der Schemakommentar zu `<interpretation>` in `mhdbdb.rnc` („present in some files", heute in keinem).

**Was über den Einzelfall hinausgilt.** (1) Die Zahl der Befunde hing an den Ist-Sätzen, die ein früherer Zustand geschrieben hat und kein Gate liest: Status, Beispiele und Zählungen in Prosa, wie am 05.10. (2) Erledigtes stand dreimal als offen in TEI-MODEL, obwohl §10 desselben Docs es als erledigt führt (`<seg type="pc">`, `<suppplied>`, WUT): ein Doc, das Soll und Migrationsgeschichte trennt, muss beim Abschluss beide Stellen anfassen. (3) „~40 MB" für den Korpus-Index blieb wie am 05.10. stehen, die Rundung ist kein Fehler. (4) Der Check selbst macht sich fällig, wenn sein PR nicht gesquasht wird: `check-doc-staleness.py` zählt `git log <commit>..HEAD -- <docs>` ohne `--first-parent`, die 52 Befund-Commits allein überschreiten die Schwelle von 40. (5) Eine Korrektur ist selbst eine Behauptung: die neu geschriebene `<monogr>`-Regel in TEI-MODEL §2.1a war aus einer Korpuszählung erschlossen und falsch, erst die Probe des Reviewers gegen `schema/tei_all.rng` zeigte die Zweige des Inhaltsmodells (drei, wie Runde 2 nachzählte). Der Reviewer (Opus, Runde 1 und schmale Runde 2, beide ohne A) fand vier Fehler in Sätzen dieses PRs (monogr zweimal, `join="left|right"`, fehlende `--allow-dirty` im Rebuild-Block), behoben in je einem Commit vor der Scorecard.
