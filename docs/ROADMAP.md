# Roadmap

Strategic priorities for the MHDBDB TEI Repository. Updated 2026-08-02.

See [Issue #44](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44) for the full triage matrix with per-issue status.

## Now: Frauenlob ist drin, die Auswertungsfrage ist offen

**#236 gemergt (30.07., `115c3a01f`).** Die beim Legacy-Ingest verlorene Parallelüberlieferungs-Ebene in FR3 ist rekonstruiert: 23 gleichrangige Töne zu 10 zusammengeführt, 36 `<div type="parallel">`, 127 eindeutige (Ton, Strophe)-Adressen, 1.563 von 9.595 Versen als Zeugenvarianten erkennbar. Dazu 42 römische Ordnungszahl-Tokens aus dem Textfluss entfernt und durch 24 `<head>` ersetzt, FR3-Metadaten auf den Supplementband 2000 korrigiert, editorische Eingriffe nach `<editorialDecl>`. **Korpus-Index 4.2.0, Authority-Index 1.6.5**, API neu gebaut. Grundlage waren die Legacy-Ingest-Quellen, die KZW am 29.07. freigegeben hat; sie liegen unter `scripts/ingest/frauenlob/source/` und machen die Rekonstruktion reproduzierbar statt erschlossen.

**Die eigentliche Folgefrage ist neu und liegt bei KZW: #255.** Adressierbar heißt nicht ausgewertet. Zeugenvarianten zählen in Wortfrequenz, Keyness, Hapax-Werkzeug und Lemma-Verteilung weiter wie eigenständiger Text, und in der Nähesuche stehen die Fassungen desselben Verses jetzt direkt hintereinander, wodurch Selbst-Kookkurrenzen entstehen können. Der Index kennt kein Parallel-Merkmal. Entscheidung nötig, bevor Code entsteht.

**#251 gemergt (`b8aa68472`) und live:** die Auswahl im Wortbestandteil-Modus liegt als Modell auf dem Explorer statt als DOM-Schnappschuss, mit Zähler als Live-Region, Fokus-Rückgabe, Übergabe in Dokumentordnung und sechs Regressionstests (26/26). Vier Review-Durchgänge; der teuerste Befund war, dass der `aria-label`-Zusatz für Homographen an der normalisierten statt an der geschriebenen Form hing: 387 der 475 Norm-Gruppen mit mehreren Lemmata haben unterschiedliche Schreibformen. Das Issue bleibt für KZWs Abnahme offen.

**Nach vier Review-Durchgängen auf #253 gelernt** (jeder brachte genau einen echten Befund, in absteigender Größe): ein `@target`-Verweis zeigte ins Leere und wäre für das Cross-Ref-Audit dauerhaft unsichtbar geblieben; die `div/@type`-Tabelle in TEI-MODEL.md stand in fünf von sieben Zeilen falsch, überwiegend schon vor diesem PR; ein `shift_indent`-Fehler rückte 28 `</div>` zwei Spalten zu tief ein, woraufhin FR3 aus der Quelle neu erzeugt statt nachgebessert wurde; und ein Docstring behauptete noch 4.1.8. Die Handwerksregeln daraus stehen in [MASTERPLAN-AUTONOME-ISSUE-SESSION §2.1](playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md) (Regeln 22 bis 26).

**CI-Änderung, probiert und verworfen:** `use_sticky_comment` (ein Kommentar pro PR statt einer pro Lauf) war einen halben Tag aktiv und ist wieder draußen. Zusammen mit `track_progress` überschreibt der nächste Lauf den Kommentar zuerst mit seiner Fortschritts-Checkliste, und frühere Runden liegen danach nur in der Edit-Historie, also nur im Browser: über API und `gh` sind sie nicht erreichbar. Die Begründung steht im Workflow. Der `synchronize`-Trigger bleibt, weil die automatisch getriggerten Folge-Läufe an beiden PRs von heute je einen echten Befund brachten. Der Auto-Cancel beim Merge (seit 12.07.) funktioniert nachweisbar und braucht keine Handarbeit.

## Vorher: Suchsemantik entschieden und umgesetzt

**Autonome Issue-Session 29.07.** ([MASTERPLAN-AUTONOME-ISSUE-SESSION](playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md)), ausgelöst durch KZWs vier Entscheidungen vom 28.07. Zwei Code-PRs plus Meta-PR, beide Code-PRs frontend-only: kein Daten-PR, Indexe bleiben 4.1.8 / 1.6.4.

| PR | Issue | Inhalt |
|----|-------|--------|
| #245 | #169 | Nähesuche misst die Spanne statt des Ankerabstands, Dedup behält den distanzkürzesten Treffer, Fast-Path-Wörterbuch gestrichen |
| #246 | #239 | Wortbestandteil-Suche als zweiter Modus im Lemmata-Explorer |

**Merge-Reihenfolge:** #245, dann #246, dann der Meta-PR (auf #245 gestackt, weil beide `JOURNAL.md` und `ROADMAP.md` berühren). Laufende Review-Runs vor dem Merge canceln.

**Die Zahlen-Zäsur, die KZW protokolliert haben wollte:** Trefferzahlen aus Nähesuchen mit **drei oder mehr Lemmata** von vor dem 29.07.2026 liegen systematisch zu hoch. `maxDistance` begrenzte bisher nur den Abstand jedes Lemmas zum Anker, nicht die Spanne; sie konnte damit das Doppelte erreichen. Gemessen an „minne + herze + leit" bei Abstand 20: der größte alte Treffer hatte eine reale Spanne von **38**. Bei zwei Lemmata ändert der Fenster-Fix nichts, der Dedup-Fix schon (243 auf 244 bei „minne + herze"). Details im JOURNAL-Eintrag 2026-07-29.

**Der Fast-Path war kein Zukunftsrisiko mehr, sondern ein aktiver Bug:** fünf der elf hartkodierten Einträge lösten falsch auf, weil die Lemma-IDs seit dem Eintragen neu vergeben wurden. Wer im Playground „bier" suchte, bekam die Birne. Lehre für die Codebasis: ein Fast-Path vor einer zentralen Auflösung kommt per Konstruktion nie an der Stelle vorbei, die seinen Fehler bemerken würde.

Weiterhin direkt startbar: **#216 minne-Serie** (~7.000 unannotierte Tokens in 262 Texten; Mechanik erprobt, Stichproben-Review durch KZW eingeplant), danach Serie 2 ff. nach der PR-#210-Priorisierung.

**Neu belegt, für #109 und die Datenpflege gleichermaßen interessant:** 27.166 der 43.879 Lemmata (61,9 Prozent) führen im Lexikon ihre morphologischen Bestandteile mit (`<etym type="morphological">`), und diese Angaben liegen bereits im ausgelieferten Authority-Index. Die Wortbestandteil-Suche nutzt sie jetzt als Filter. Damit ist die verbreitete Annahme widerlegt, Komposita-Zerlegung im Frontend bräuchte zwingend Stemming; für die verbleibenden 38 Prozent ohne verzeichnete Wortbildung gilt sie weiter.

**Erledigt am 29.07.:** die Playground-Aufräumrunde. Acht Funktionen ohne Aufrufer entfernt (darunter zwei, die zusätzlich Kontextfenster mit Index-Positionen in die ungefilterte `<w>`-Liste schnitten, und zwei, die erst durch die Löschung selbst verwaisten), `resolveLemmaIds` dedupliziert, und beide Kookkurrenz-Modi verweigern jetzt die Arbeit statt bei einem einzigen Lemma jede Fundstelle als Treffer mit Abstand 0 zu melden. Die abweichende Zählweise des Upload-Fallbacks steht mit Messwerten in CONTRACTS §B.

**Offen aus derselben Ecke:** #251, inzwischen als PR #256 umgesetzt, siehe oben.

## Laufend: Nach-Merge-Betreuung + freigeschaltete Workstreams

**Health-Check erledigt (2026-07-09):** Drift-Prüfung gegen main nach der Merge-Woche. Befund: Kern-Docs (TEI-MODEL §11, INDEX.md, Daten-Zählungen via `doc-count-audit.py`, Algorithmus-Spot-Checks §B.1/§D.2/posAll) ohne Drift; 5 Rand-Drifts gefixt (CLAUDE.md-Versionszeiger, README-Werkzeugzahl, LINECODE-#23-Status, DATA-MODEL-Changelog v4.1.4/v4.1.5, DECISIONS-Versionsplatzhalter). Scorecard im JOURNAL.

Die autonome Merge-Session (08.07., [MASTERPLAN-AUTONOME-MERGE-SESSION](playbooks/MASTERPLAN-AUTONOME-MERGE-SESSION.md)) hat alle 13 PRs der Issue-Session nach main gebracht (#174–#186); 13 Issues wurden automatisch geschlossen (#163 #164 #159 #168 #158 #162 #160 #161 #134 #145 #27 #167 #170), #68/#86/#28/#171 bleiben planmäßig offen (Teilarbeit). Authority-Index v1.6.0 (posAll[]) ist live, Live-Smoke-Checks für beide Stack-Ketten und die Unabhängigen bestanden. Details: JOURNAL-Eintrag 08.07. (Merge-Session) + Abschlussreport in #44.

Direkt startbar geworden:
- **#92 ARITHMETIC Stage 1** – Escaping-Blocker in #185 gemerged; Metadatenfragen an Carina weiter offen
- **#18 Multi-Lemma + PoS-Suche** – POS-Policy (#27) gemerged; braucht POS-Daten im Corpus-Index

**Korrektur 31.07.:** Zwei Einträge standen hier als startbar, sind aber beide seit 10.07. erledigt und deshalb aus der Liste genommen.

- **#187 posAll-Anzeige-Migration** (Commit `edb16dd3f`, Issue als completed geschlossen; JOURNAL 10.07. Vormittag). Alle im Issue gelisteten Anzeige-Stellen lesen inzwischen `posAll[]` mit Erstwert-Fallback für ältere Caches, dazu `verse-position-search.js`, das in der Issue-Liste fehlte.
- **WVV-Strophen-Lauf**: der Halbsatz „der Lauf selbst steht noch aus" stammte vom 08.07. und wurde am 10.07. überholt (JOURNAL: „#110/WVV komplett"). Nachgemessen an `tei/WVV.tei.xml`: 489 fortlaufende `<lg>`.

Beides derselbe Fehlertyp: die ROADMAP beschreibt den Stand eines Dokuments statt den des Projekts, sobald ein Eintrag nach seiner Erledigung nicht mitgezogen wird.

**#124 (prio-1)** ist technisch fertig: cookieloses Matomo ist seit 17.06. deployed (`includes/_matomo.html`, Opt-out + Datenschutz-Abschnitt im Impressum, Commit `7abbf7672`); offen nur noch DSB-Absegnung der Rechtsgrundlage + Klärung des Dashboard-Zugangs.

## Next: Menschen-Pings (nach den Merges)

| # | What | Who's needed |
|---|------|-------------|
| #115 | Cross-Ref Phase 2 – 196 Lemmata kuratorisch (A 125 / B 36 / C 35) | KZW |
| #129 | KWIC-Belege: gebaut und live seit Juni, Prüfung steht weiter aus | KZW |
| #138 | div-/lg-Hüllen warten weiter auf Prüfung; neu dazu die Render-Policy-Frage zu den DIG-Strophenzählern in HUG (Julia, 17.07.) | KZW |
| #228 | Neu: editorischer Apparat in `<note n=…>` ist als Text lemmatisiert (400 Tokens in 165 Notes über 16 Texte, ohne die GWTK-Notes mit ganzen Versblöcken; korpusweit 587 Notes mit 2.458 Tokens) – entannotieren? | KZW |
| #239 | KZW hat am 29.07. um eine Neuerklärung gebeten („ich habe den Faden verloren"); am 30.07. mit gemessenen Gruppenzahlen beantwortet (Eingabe „wein": 67 am Wortende, 149 am Wortanfang, 191 in der Wortmitte, davon 50 belegte Wortbildungen). Zwei Fragen bleiben: ist `winter` in der Wortanfang-Gruppe akzeptabel (die positionale Definition verlangt es), und soll der Filter „nur belegte Wortbildungen" standardmäßig an sein? Empfehlung: aus, weil das Lexikon Bestandteile nur bei 61,9 Prozent der Lemmata verzeichnet | KZW |
| #250 | KZW hat am 29.07. beide Punkte entschieden (Aufklapp-Abschnitt genügt, synthetisches Label nur wo sauber prüfbar). Dritter Punkt am 30.07. ergänzt und beziffert: seit der FR3-Verschachtelung verlieren 19 von 127 Sections ihren Verszählungs-Anker, die sichtbare 1 wandert zum Parallelzeugen. Umsetzung offen | KZW-Antwort liegt vor |
| #252 | KZW hat am 29.07. entschieden: echte Auslassungen sollen `<gap/>` sein, `<caesura/>` bleibt der bewussten Zäsur innerhalb der Verszeile vorbehalten. Damit ist die Migration von 971 Stellen in 21 Texten arbeitsfähig (Datenblock, Data-Change-Lifecycle) | KZW-Antwort liegt vor |
| #255 | Neu 30.07.: zählen Zeugenvarianten in Frequenz, Keyness und Hapax wie eigenständiger Text? Drei Entscheidungsfragen im Issue, die technische Umsetzung hängt allein an der ersten | KZW |
| #169 | Neu 29.07.: die drei freigegebenen Befunde umgesetzt (PR #245), Abnahme steht aus. Die Trefferzahlen für 3+-Lemma-Nähesuchen sinken, das ist gewollt und datiert im JOURNAL | KZW |
| #224 | Fix ist gemergt und live; offen ist nur noch die Breve-Frage für die Basiszeichen `w`, `n`, `y`, `z` (64 lemmatisierte Tokens) | Julia |
| #59, #114 | Naming-Fachklärung (Alexander-Workaround-Entwurf liegt seit 12.07. im Issue, Team-Freigabe vor Linda-Ping) + Tabellenansicht-Freigabe | Linda (via Team) |
| #92 | ARITHMETIC – Metadatenfragen seit 16.05.; Escaping-Blocker gemerged (#185), Stage 1 danach in ~1–2h | Carina (via KZW) |
| #147 | Weingrüße – Lizenz/Sigle/Genre/Zuschreibungen, Stage 0 | Silvan (via KZW) |
| #86 | Barrierefreiheit – Ansprechpersonen-Block live (barrierefreiheit.html, #179); schließen nach Text-Freigabe | Alan van Beek |
| (ohne Issue) | Vermittlung Brom ↔ Nieser: Brom hat nach eigenen oder feingetunten Sprachmodellen auf MHDBDB-Daten gefragt, ParzivAI ist die nächstliegende Antwort und für beide Seiten interessant. Sachstand in [RESEARCH.md → Downstream Reuse and Related Projects](RESEARCH.md#downstream-reuse-and-related-projects) | chsteiner (an Vlastimil Brom + Florian Nieser) |

## Needs Clarification / Entscheidungs-Cluster (chsteiner)

| # | What | Key question |
|---|------|-------------|
| #140 | Doku menschenlesbar | Bereinigung umgesetzt (PR #215, 12.07.); beide Detailfragen der Abnahme vom 27.07. erledigt (DRAFT-Kopf in TEI-MODEL.md entfernt, PR #230; „Woesner" repoweit einheitlich geschrieben, keine Variante „Wösner"/„Wosner" im Bestand, keine Änderung nötig). Offen ist nur noch die Abnahme durch KZW |
| #58 | Begriff→Lemma→Beleg Workflow | Option A/B/C entscheiden |
| #169 | Suchsemantik (Audit 3/6) | Alle vier Punkte umgesetzt (Punktnummern sind Audit-Befunde, keine Issue-Nummern): Punkt 45 3-Stufen-Drift in PR #227 (ADR-016), Punkte 15/48/51 nach KZW-Freigabe vom 28.07. am 29.07. Offen ist nur noch die Abnahme. Zahlen-Zäsur für 3+-Lemma-Nähesuchen im JOURNAL 2026-07-29 |
| #172 | Test-Suite-Policy (Audit 6/6) | Der 45%-passRate-Floor ist mit #326 entfallen: die Assertion stand in `testing/tests/playground.spec.js` und ist mit den Tests auf die gelöschte Testseite weggefallen. Offen bleiben die korpusabhängigen Magic-Numbers |
| #18 | Multi-Lemma + PoS-Suche | POS-Policy (#27/#181) gemerged, spezifizierbar; braucht POS-Daten im Corpus-Index |

## Future: Needs Design / Trigger-Wait

| # | What | Key question |
|---|------|-------------|
| #141 | Borte-Ingest – Aufgabe 0 (borte.md-Metadaten-Template) im Issue geliefert | KZW-Priorisierung (nach #139) |
| #106 | Vers-Boundary-Features – Minimalvariante shipped 02.07., Rolling-Backlog | Original-Token/Phonetik → #109 |
| #28 | Fremdsprachen-Annotation – Daten-Phasenplan gemerged (`docs/features/FREMDSPRACHEN-PHASENPLAN-28.md`, Lemma-Ebene führt) | Umsetzung Phase 0–4 beim nächsten Daten-Slot |
| #139 | CoReMA-Korpus ingesten | Trigger/Kapazität |
| #118 | Sprachstufen aus Normdaten | Policy + Architekturentscheid |
| #123 | „König vom Odenwald" | Scope + Zeitfenster (KZW) |
| #63 | Begriffssystem Update | Scope/Policy (KZW) |
| #93 | Textreihentypologie-Umzug (von marketext.at auf MHDBDB-Unterseite) – SKOS-Daten aus `textseries`-Repo, Baum-Visualisierung; dysfunktionale `dhplus`-URIs zu bereinigen | Visualisierung + Authority-File-Abgleich |
| #109 | FWF-Einzelprojekt (Korpus-Tiefenanalyse, NER-Pipeline, phonetische Reimanalyse, Visualisierungen) – Antrag durch KZW, kleines Budget, max. 50% externe Mittel | Scope-Notiz für Antragstext |
| #111 | Index-Größen-Soft-Cap und modulare Splitting-Strategie | Trigger >50 MB gz (heute ~40); Optionen A modular / B brotli / C binär; keine Entscheidung bis Schwellwert erreicht |

## Fertiges steht im JOURNAL

Diese Datei blickt nach vorne. Was abgeschlossen ist, steht chronologisch und mit
Begründungen im [JOURNAL.md](JOURNAL.md), ältere Einträge in
[journal-archive.md](journal-archive.md). Bis zum 02.08.2026 stand hier
zusätzlich eine Tabelle „Recently Completed": sie reichte bis April zurück,
endete aber am 08.07., während seither 60 PRs gemergt wurden. Eine zweite
Chronik neben dem JOURNAL zu führen hat nicht funktioniert und wurde deshalb
aufgegeben (#316).

## Strategic Direction

1. **TEI model consolidation done** – Soll-Modell (#32) fully implemented, #32-followup 17/17 abgeschlossen (P1-5 mit 3 kontextspezifischen Enum-Patterns für `idno/@type`, plus WZB shelfmark, Stage-1 PI cleanup, CI push trigger). Both schemas written (`mhdbdb.rnc`, `mhdbdb-authority.rnc`), all 667 corpus + 8 authority files validated. Target models: [TEI-MODEL.md](TEI-MODEL.md) + [TEI-MODEL-AUTH-FILES.md](TEI-MODEL-AUTH-FILES.md). Architecture Decision Record: [ADR-013 "Data Consolidation Before Schema Relaxation"](DECISIONS.md#adr-013-data-consolidation-before-schema-relaxation).

2. **TEI data quality** – Structural fixes (#23, #26, #30, #85), schema hardening (#32 ✅), Wenzelsbibel (#34, Phase 3 at 92.5%) und WVV-Followup (#110) sind die aktiven Workstreams. Die meisten verbleibenden Structural Fixes sind auf KZW-Review geblockt.

3. **Playground TEI Textanalyse Release 1 done** – UX-Cleanup (#87), Wortfrequenz (#88), Text-Statistiken (#89), Lemma-Verteilung (#90) alle 2026-05-11 closed. Release 2 (Begriffs-Verteilung) und Release 3 (POS-Anteile, abhängig von #27) noch ungeplant.

4. **FAIR data + Citability** – Static JSON API (#45) und Zenodo-DOI (#91, Stub geliefert) machen MHDBDB-Daten extern zitier- und programmierbar zugänglich. Enables external collaborations (MWB, Wörterbuchnetz, ZfdG-Einreichung).

5. **Frontend refinements** – Reader (#17 ✅), UI-Polish (#20 ✅), Reading-View-Render-Policy (#101 ✅ 2026-05-12, Julia) und Lemma-Linking MWB+Lexer (#73 ✅ 2026-05-12) abgeschlossen. Upload-UI-Dead-Code-Cleanup erledigt (#314, 2026-07-31): rund 2.200 Zeilen über 19 Dateien, drei davon ganz.

6. **Advanced search** – PoS-based search (#18) and foreign language search (#28) depend on corpus index extensions.
