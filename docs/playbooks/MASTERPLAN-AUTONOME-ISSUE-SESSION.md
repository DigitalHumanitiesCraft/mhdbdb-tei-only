# Masterplan: Autonome Issue-Abarbeitungs-Session

**Erstellt:** 2026-07-03 (Audit-Session, Fable 5); Vorgänger-Sessions sind gelaufen und gemergt.
**Neu befüllt:** 2026-07-28 (Voll-Audit aller 36 offenen Issues, Opus 5). Session-Inhalte 12.07. geleert; Git-History = Archiv.
**Status:** Session 2026-07-28 GELAUFEN (Kickoff „starte den plan autonom", Entscheidungen §5). Ergebnis und Lehren: §7. Vor der nächsten Session §1/§3/§5/§6 neu befüllen.
**Typ:** Playbook (wiederverwendbares Session-Verfahren, dauerhaft). Der session-spezifische Teil (§1, §3, §5, §6) wird pro Session neu befüllt; der Betriebsvertrag (§2) ist der stabile Kern.

Quellen des Audits: alle 36 offenen Issue-Bodies + Kommentarverläufe seit 13.07. (Dump 28.07.), die beiden Screenshots aus #224 und #196, git log (main bis `ee37bece4`), Belegzählungen gegen `authority-files/lexicon.xml`, `data/authority-index.json.gz` und `tei/*.tei.xml`.

---

## 1. Audit-Ergebnis: 36 offene Issues (Stand 2026-07-28)

Auslöser dieser Session ist KZWs Durchgang vom 27.07.: zwei Issues geschlossen (#203, #204), drei mit konkreten Nachbesserungen zurückgegeben (#196, #190, #140), eines an Julia übergeben (#198), eines an Linda gepingt (#59). Dazu drei neue Issues (#224, #225, #226) und vier Beobachtungen von Julia in #138. Der autonom lieferbare Bestand ist damit deutlich größer als am 12.07.: fünf Kern-Deliverables statt zwei.

Zwei Befunde aus dem Vorflug-Audit bestimmen den Zuschnitt:

**#224 ist kein WZB-Problem, sondern Stufe 3 der Lemma-Auflösung.** `assets/js/search/search-engine.js:142` wertet `normalized.includes(lemma.normalized)` aus. Gegen `data/authority-index.json.gz` nachgerechnet liefert die Suche nach „böses" (normalisiert `boeses`) genau vier Stage-3-Treffer: `ês`/`es`, `ô`/`o`, `sê`/`se` und `bœse`/`boese`. Die drei Kurzlemmata sind der Bug, `bœse` ist die gesuchte Antwort. Der Korpus enthält 5 einbuchstabige, 98 zweibuchstabige und 598 dreibuchstabige normalisierte Lemma-Formen; sie vergiften jede Suche mit einem nicht im Lexikon stehenden Wort. Damit ist der seit Juli offene Entscheidungspunkt #169/#45 („welche Stage-3-Variante ist kanonisch?") nicht mehr theoretisch, sondern hat einen externen Bug-Report.

**#196: KZWs Intuition trifft zu, aber für 5 statt 202 Lemmata.** `lexicon.xml` enthält 202 NUM-only-Lemmata. 197 davon sind echte Zahlwörter (drî, hundert, zweite, drîzehenhundert) und damit keine „stummen Lemmata"; NUM ist reguläres Tag des 19er-Sets (116.966 `@pos`-Vorkommen laut POS-TAGSET.md §2; lemma-seitig 121.258 Tokens im Korpus-Index). Reine Ziffern-Lemmata gibt es genau fünf: `1` (lemma_53328), `36` (lemma_69748), `42` (lemma_69749), `46` (lemma_69733), `49` (lemma_69750), zusammen 118 Belege über fünf Texte (NEIM 63, BRW 26, MR1 15, WVV 11, NML 3). Genau diese fünf stehen in KZWs Screenshot. Der Filter-Wunsch und die TEI-Putz-Frage sind deshalb zwei getrennte Deliverables.

### A. Voll autonom lösbar (5 + Meta)

| Rang | # | Was | Warum autonom | Aufwand |
|-----:|---|-----|---------------|---------|
| **1** | **#224** | Stufe 3 der Lemma-Auflösung entschärfen und die Parität zum Playground-Pendant herstellen | Ursache lokalisiert und gegen den realen Index nachgerechnet; Fix ist frontend-only ohne Datenberührung; Wirkung messbar (Präzisions-Messung gegen `variants.xml`, siehe §3 Welle 1) | M |
| **2** | **#196** | NUM aus der Hapax-Liste nehmen, Sweep über die anderen elf Werkzeuge, Sub-Issue für die 5 Ziffern-Lemmata | KZWs Rückgabe ist eine konkrete Anweisung; das Filter-Muster (`FUNCTION_WORD_POS`) existiert bereits; die Beleglage für das Sub-Issue ist erhoben | S |
| **3** | **#190** | Zwei von KZW wörtlich diktierte Textänderungen in `hilfe-belege-beitragen.html` (Zeile 179 und 269) | Wortlaut steht im Issue; KZW hat den Close explizit an diese beiden Punkte gebunden | XS |
| **4** | **#140** | `docs/TEI-MODEL.md:7` DRAFT-Kopf entfernen | KZW-Punkt 2 („Woesner") ist bereits erfüllt: repoweit 6 Vorkommen, alle korrekt, keine Falschschreibung im Repo | XS |
| **5** | **#138** (2 Teilpunkte Julias) | Nach-oben-Button in der Leseansicht; Verszählungs-Einstieg pro Lied | Beide frontend-only. Punkt 2 ist diagnostiziert: die Daten sind korrekt (jedes `div type="song"` in HUG startet bei `l n="1"`), `state.firstNumericLineShown` in `tei-text-reader.js:422` ist dokumentweit statt pro Nummerierungsbereich | S |
| — | **#44** | Triage-Matrix aktualisieren | Evergreen-Meta-Aufgabe am Session-Ende; **nie schließen**, nie mit Closes referenzieren | S |

### B. Autonome Teilschritte als Stretch (Issue bleibt offen; Freigabe siehe §5)

| # | Autonomer Teil | Bleibt offen wegen |
|---|----------------|--------------------|
| **#169** | Punkt #45 ist durch #224 entscheidungsreif: drei Optionen (nur Präfix / bidirektional mit Mindestlänge / Stage 3 streichen) mit gemessenen Trefferzahlen aus Welle 1, als Entscheidungsvorlage im Issue | Die anderen drei Punkte (#15 Nähesuche-Distanz, #51 Fast-Path-Wörterbuch, #48 Dedup) verändern Forschungsergebnisse und brauchen chsteiner |
| **#225** | Mail-Entwurf an Dr. Thomas Burch (Wörterbuchnetz) nach Mail-Stil-Konvention, KZW im Cc, mit den drei Bitten aus dem Issue-Body und der offenen Domain-Frage als eigenem Absatz | Versand ist chsteiners Sache; Externen-Kontakt ist per Betriebsvertrag ausgeschlossen |
| **#223** | Plausibilitätsprüfung des offenen Auto-Rebuild-PRs als Kommentar (10.505 gegen 10.506 Records, 0 übersprungen, Figuren-Zahlen unverändert) | Merge nach main ist per §2 Regel 1 tabu |

### C. Umgesetzt, warten nur auf Test-OK: Session fasst sie NICHT an (1)

#114 (Tabellenansicht-Integrationswünsche, Linda gepingt 02.07.). Kein erneutes Anpingen, kein Nacharbeiten vor dem OK.

### D. Blockiert auf Menschen (12): Session fasst sie NICHT an

#198 (KZW hat am 27.07. an @juliahin übergeben; Schritt 2 Sense-Split bleibt danach KZW), #59 (KZW hat Linda am 27.07. gepingt; Antwort abwarten, nicht nachfassen), #115 (Kategorien B/C + Stub-Review, kuratorisch), #189 (21 Review-Fälle + Funktionswort-Grundsatzentscheidung), #138-Kern (die `<div>`-Hüllen selbst, KZW-Prüffragen), #28, #27, #68, #86, #63, #58, #172.

### E. Future / Trigger / extern blockiert (10): bewusst liegen lassen

#93, #106 (Rolling-Backlog), #109, #111 (Trigger nicht erreicht), #118 (Vorlage liegt seit 12.07., KZW-Antwort offen), #194 (per Issue-Text blockiert auf #193), #195, #216 (technisch entsperrt, aber Batch-Größe und Stichproben-Review brauchen KZW-Begleitung), #226 (chsteiner-Review eines Google-Docs), #18 (braucht Query-Syntax-Entscheid).

### F. Ingest: nicht Teil dieses Playbooks (7)

#92 (ARITHMETIC), #123 (König vom Odenwald), #139 (CoReMA; laut Memory gemeinsame Einzelsession, nie autonom), #141 (Borte), #147 (Weingrüße), #191 (Flore und Blanscheflur), #193 (Arthurische Pferde).

**Fazit:** 5 Kern-PRs + Meta sind der voll autonome Bestand, davon zwei (#190, #140) im XS-Bereich und mit KZW-Freigabe zum Schließen. Die Stretch-Teilschritte (§1.B) sind Text-Deliverables ohne Code-Risiko. Alles andere wartet auf Menschen oder ist bewusst ausgelagert.

---

## 2. Betriebsvertrag der autonomen Session

Die CLAUDE.md-Regel „never commit/push without user approval" wird durch den Kickoff-Prompt explizit für `claude/*`-Branches + PR-Erstellung freigegeben. Unverändert hart:

1. **`main` ist tabu.** Kein Merge, kein Push. Alle Ergebnisse = PRs, die chsteiner reviewt und mergt.
2. **Issues werden nie von der Session geschlossen**: nur via `Closes #N` im PR-Body beim Merge. #44 bekommt nie einen Close-Trailer.
3. **Pro PR nur benannte Dateien stagen** (nie `git add -A`), Branch frisch von `origin/main`.
4. **Daten vor Schema**; Data-Change-Lifecycle bei jeder XML-Änderung: variants.xml regenerieren, Corpus- + Authority-Index-Rebuild, API-Rebuild, Versions-Bump an allen drei Stellen (`python scripts/audit/check-index-versions.py` lokal vor Push), deterministische Builds (`git status --porcelain`-Pre-flight). **3-Commit-Muster auf Daten-Branches** (Lehre 12.07.): Quellen-Commit → Index-Commit → API-Commit, weil die Pre-flight-Gates aus #100 saubere Quell-Trees verlangen; der Merge stellt den Ein-Commit-Lifecycle auf main wieder her. Freshness-Checks direkt nach einem Checkout nicht glauben (mtime-Rauschen), sondern hart per Regenerat-Vergleich prüfen.
5. **Verifikation je PR:** `npm test` aus dem Repo-Root (nie `npx playwright test`); Referenz ist die in Welle 0 erhobene Baseline auf main. Bei UI zusätzlich Chrome-Verifikation mit realen Belegen; bei TEI-Änderungen Schema-Validierung; bei HTML-Änderungen `python scripts/build-pages.py --check` und bei neuen Utility-Klassen `npm run build:css`.
6. **Konfliktmanagement ohne Merges:** PRs starten von main; bei Datei-Überschneidung wird der spätere Branch auf den früheren gestackt, PR-Body sagt „nach PR X mergen". Abschlussreport enthält die empfohlene Merge-Reihenfolge und den Hinweis, laufende Opus-Review-Runs vor dem Merge zu canceln (nie `[skip ci]` bei Daten-PRs).
7. **Kommunikation:** max. 1 sachlicher Statuskommentar pro Issue; keine Kontaktaufnahme mit Externen (Linda, Alan, Carina, Silvan); Entwürfe dafür landen als Text im Issue. Keine Emoji-Icons in UI/Doku (Heroicons inline SVG); keine Em-Dashes in Prosa (docs/, Hilfe-Seiten, Issue-Kommentare); echte Umlaute.
8. **Inputs selbst beschaffen:** Für diese Session liegen alle Inputs im Repo bzw. in den Issue-Threads (`gh issue view N --json comments`); es sind keine externen Quellen (Drive/Gmail/Zenodo) nötig. Der Goldstandard für #189 steht im Issue-Body (78 *rôter munt* / 262 *jung*, plus eigene TEI-Auszählung 73 Vers-Kookkurrenzen / 265 junc-Formen). Nur nachweislich Unbeschaffbares wird im Abschlussreport dokumentiert übersprungen; nicht auf chsteiner warten, nicht fragen.

---

## 3. Wellenplan (Reihenfolge = Risiko aufsteigend innerhalb der Kern-Deliverables)

Die fünf Kern-Deliverables berühren disjunkte Dateien, deshalb startet jeder Branch frisch von `origin/main`; nur der Meta-PR wird auf Welle 3 gestackt (beide fassen `docs/` an). Reihenfolge nach Wirkung, nicht nach Risiko: #224 ist der einzige extern gemeldete Bug und braucht die frischeste Analyse.

| Welle | Deliverable | Issues | Inhalt |
|-------|-------------|--------|--------|
| **0** | Chat-Report | - | Vorflug: Test-Baseline auf main (`npm test`); `check-index-versions.py`; die zweite Stage-3-Implementierung in `playground/js/data/authority-manager.js:135` lesen und die Richtungs-Drift gegen `search-engine.js:142` protokollieren; `assets/js/lib/lemma-match.js` als Muster für die Modul-Extraktion einlesen; bestehende Such-Specs in `testing/tests/` sichten |
| **1** | PR 1 | #224 (refs #169) | **Stage-3-Fix.** Neues Modul `assets/js/lib/lemma-resolve.js` nach dem Muster von `lemma-match.js`, aber **nur Prädikat + Comparator als pure Funktionen**; die Orchestrierung bleibt je Aufrufer, weil `search-engine.js` vorberechnetes `lemma.normalized` liest und `authority-manager.js` zur Laufzeit normalisiert (kleinerer Blast-Radius bei gleicher Paritätswirkung). Regel: Stage 3 matcht **beidseitig präfixorientiert** (`lemmaNorm.startsWith(query)` für Stammeingabe, `query.startsWith(lemmaNorm)` für flektierte Eingabe); die Mindestlänge 3 gilt nur in der zweiten Richtung. Sortierung nach Längendifferenz, im Playground mit Tie-Break nach Korpus-Frequenz (Lehre #163/#164: sonst steht eine 1-Beleg-Rarität vor dem frequenten Lemma). Belegte Wirkung auf „böses": `ês`, `ô`, `sê` fallen weg, `bœse` bleibt. **Keine gestufte Fallback-Strategie**: sie präjudiziert die offene #169/#45-Entscheidung und holt den Infix-Müll zurück. **Messpflicht vor dem Commit:** Stage-3-Prädikat direkt aufrufen (Stage 1+2 umgehen), 300 mit festem Seed gezogene flektierte Formen aus `authority-files/variants.xml`; Formen, deren Normalisierung gleich der Lemma-Normalisierung ist, separat ausweisen (die hätten Stage 1 getroffen). Metriken: **Recall** (wahres Lemma irgendwo in der Liste, alt vs. neu), **Median der Ergebnislistengröße**, **Top-1 nach Ranking**. Ausdrücklich NICHT die 0-Treffer-Quote als Abbruchkriterium: die alte Regel liefert wegen der 5 ein- und 98 zweibuchstabigen Lemmata fast nie 0 Treffer, die Quote steigt also zwangsläufig; ein 0-Treffer-Fall, in dem alt nur Falschtreffer hatte, ist eine Verbesserung. Sample-Bias (echte Stage-3-Eingaben sind eher nhd. Wörter und Tippfehler) im Messbericht benennen. **Doku- und Spec-Nachzug in derselben Welle:** CONTRACTS.md §C (Pseudocode + das Beispiel „`bro` → `brot`, `brogen`"), CLAUDE.md Key Patterns, ARCHITECTURE.md, der irreführende Kommentar in `tei-ui.js:99-104`; `testing/tests/search-engine.spec.js:74-81` (erwartet für `fri` einen Stage-3-Treffer) vorab prüfen und bewusst anpassen. Zusätzlich den Keyness-Pfad `app.js:619` mit einem Stage-3-Begriff gegenprüfen. Playwright-Regressionstest analog #126/#130. Im PR- und Issue-Text nur von **Stage-3-Parität** sprechen, nicht von Parität überhaupt. 1 Statuskommentar in #224 mit Ursachenanalyse und Messergebnis (dabei klarstellen, dass es kein WZB-Sonderzeichen-Problem ist) |
| **2** | PR 2 | #196 | **NUM-Filter + Feature-Sweep.** NUM aus der Hapax-Liste nehmen (Filter-Set analog `FUNCTION_WORD_POS` in `word-frequency.js`, mit sichtbarem Ausblend-Zähler statt stiller Unterdrückung). Danach KZWs zweiten Auftrag ausführen: alle zwölf TEI-Analyse-Werkzeuge daraufhin prüfen, ob NUM dort sinnvoll ist, und das Ergebnis je Werkzeug im Statuskommentar begründen (nicht pauschal überall filtern). Sub-Issue „TEI-Putzen: 5 Ziffern-Lemmata" mit der fertigen Belegliste (118 Tokens in BRW/WVV/NML) anlegen und KZWs Frage beantworten: 197 der 202 NUM-Lemmata sind echte Zahlwörter, nur die 5 Ziffern sind Altbestands-Artefakte. Chrome-Verifikation der Hapax-Liste vorher/nachher |
| **3** | PR 3 | #190, #140 | **KZW-Abnahme-Nachbesserungen.** `hilfe-belege-beitragen.html:179` zum vollständigen Satz umbauen, `:269` auf „CC BY-NC-SA 4.0" ohne Verhandlungsformel kürzen; `docs/TEI-MODEL.md:7` DRAFT-Kopf ersatzlos entfernen. `python scripts/build-pages.py --check`; bei neuen Utility-Klassen `npm run build:css`. `Closes #190` (KZW hat den Close ausdrücklich an diese zwei Punkte gebunden); **#140 bleibt offen** mit einem Kommentar, der beide Punkte als erledigt meldet und um die Abnahme bittet, weil KZW dort nur „für die Abnahme" geschrieben hat |
| **4** | PR 4 | #138 (2 Teilpunkte) | **Leseansicht.** (a) Nach-oben-Button: Heroicons inline SVG, kein Emoji, sichtbar ab Scroll-Schwelle, Tastatur-erreichbar. (b) `state.firstNumericLineShown` zurücksetzen, **aber ausschließlich an `div`-Grenzen und nur, wenn die erste numerische `<l>` des `div` `n="1"` trägt**. Der Reset darf NIE an `lg`-Grenzen greifen: NBB restartet `l/@n` pro Strophe (1..4), ein `lg`-Reset würde dort in jeder Strophe eine Marginal-„1" zeigen, also genau die Regression, die der #127-Kommentar verhindert. Die `n="1"`-Bedingung verhindert zusätzlich, dass Kapitel-Texte mit durchlaufender Zählung neu einen Anker je Kapitel bekommen. Der bestehende Kommentar über der Stelle wird mit der neuen Begründung fortgeschrieben, nicht gelöscht, und die Regel in CONTRACTS nachgezogen. Bestehende Specs `reading-view.spec.js` müssen grün bleiben; neue Tests für den Reset **inklusive NBB-Fall**. Chrome-Verifikation an HUG (Lied 2 und 3) **und NBB und einem Kapitel-Text**. Der PR-Body sagt ausdrücklich, dass hier ein als #127-Entscheidung dokumentiertes Teilverhalten auf Julias Input geändert wird, damit der Merge eine bewusste Entscheidung ist. 1 Statuskommentar in #138, der zugleich Julias andere zwei Punkte beantwortet: die Winkelklammern in HUG sind editorische Klammern der Vorlage und als `<pc>` korrekt kodiert (kein Encoding-Fehler, offen ist nur die Render-Policy für KZW); für die „Kleinziffern (ii)" fehlt eine Textstelle, da weder römische `@n`-Werte noch `<milestone unit="verse">` in HUG/KLA/PL1/MBS1 vorkommen |
| **5** | Stretch (nur wenn 1-4 komplett UND in §5 freigegeben) | #169, #225, #223 | Nur Text-Deliverables: (a) #169-Entscheidungsvorlage zu Punkt #45 mit den Messzahlen aus Welle 1 und drei benannten Optionen; (b) #225 Mail-Entwurf an Burch als Issue-Kommentar, ohne Versand und ohne Externen-Ping; (c) #223 Plausibilitätskommentar am offenen PR, ohne Merge |
| **6** | Meta-PR (auf Welle 3 gestackt) + #44-Kommentar | #44, docs | #44-Matrix aktualisieren, ROADMAP.md + JOURNAL.md nachziehen, §7 dieses Playbooks befüllen und §1/§3/§5/§6 für die Folgesession leeren. Abschlussreport als #44-Kommentar: PR-Liste, empfohlene Merge-Reihenfolge (inkl. Hinweis, laufende Review-Runs vor dem Merge zu canceln), Übersprungenes mit Grund, Wer-wartet-worauf-Liste (KZW: #140-Abnahme, #115 B/C, #189-Review-Fälle, #138-Kern, #198-Schritt-2; Linda: #114, #59; Julia: #198-Prüffälle; extern: #92 Carina, #147 Silvan, #86 Alan) |

Geschätzter Output: 5 PRs plus Meta-PR, 1 Issue geschlossen (#190), 3 substanziell abgeräumt (#224, #196, #140), 1 neues Sub-Issue, 5 bis 7 Issue-Kommentare.

---

## 4. Nicht anfassen

- **Review-Gate (Ping ist draußen):** #114 (Linda seit 02.07.)
- **Menschen-blockiert:** #198 (jetzt bei Julia), #59 (KZW hat Linda am 27.07. gepingt), #115 (B/C), #189 (Review-Fälle + Funktionswort-Grundsatz), #138-Kern (die `<div>`-Hüllen selbst), #28, #27, #68, #86, #63, #58, #172
- **Future/Trigger/extern:** #93, #106, #109, #111, #118, #194, #195, #216, #226, #18
- **Ingest:** #92, #123, #139, #141, #147, #191, #193
- **Kein Merge nach main**, auch nicht bei PR #223 (Auto-Rebuild) trotz grüner Plausibilitätsprüfung.
- Alle Gruppen nur in der #44-Matrix korrekt einsortieren.

---

## 5. Getroffene Entscheidungen (chsteiner, 2026-07-28)

1. **Stretch-Welle 5:** an, aber strikt erst nach Abschluss der Wellen 1-4.
2. **#224-Tiefe:** der Fix bleibt auf Stage 3 beschränkt. Die drei anderen #169-Punkte (Nähesuche-Distanz #15, Fast-Path-Wörterbuch #51, Dedup #48) werden nicht mitgefixt, weil sie Forschungsergebnisse verändern; sie bleiben Entscheidungsvorlage.
3. **#196-Reichweite:** NUM wird nicht pauschal aus allen Werkzeugen gefiltert, sondern je Werkzeug begründet. In Wortfrequenz und Text-Statistiken sind Zahlwörter legitime Daten; die Filterung zielt auf die Raritäten-Werkzeuge.
4. **#140:** wird nicht selbst geschlossen (KZW hat nur „für die Abnahme" geschrieben), #190 schon (expliziter Close-Auftrag).
5. **Ziffern-Lemmata:** diese Session ändert keine TEI-Daten. Die 5 Ziffern-Lemmata werden ausschließlich als Sub-Issue mit Belegliste dokumentiert; die Entscheidung, ob sie stumm geschaltet, umannotiert oder gelöscht werden, ist kuratorisch.

### Nachträge aus dem Advisor-Review (Fable 5, 28.07.)

Drei Befunde waren echte Planfehler und sind in §3 eingearbeitet:

1. **Messmetrik Welle 1 war falsch kalibriert.** Die 0-Treffer-Quote als Abbruchkriterium hätte immer ausgelöst, weil die alte Regel wegen der Kurzlemmata praktisch nie 0 Treffer liefert. Ersetzt durch Recall, Median-Listengröße und Top-1. Ablaut-Fälle (`slüege`/`slahen`) findet auch die alte Regel nicht, sie liefert dort nur zufälligen Müll: 0 Treffer sind das ehrlichere Ergebnis, keine Regression.
2. **Reset-Bereich in #138(b) war unterspezifiziert** und hätte über `lg`-Grenzen die NBB-Regression reproduziert, die #127 gerade verhindert hat.
3. **Doku- und Spec-Nachzug fehlte in Welle 1.** CONTRACTS §C dokumentiert das bidirektionale Substring-Verhalten als Vertrag; `search-engine.spec.js:74-81` erwartet es. Beides gehört in denselben PR.

Zwei weitere Punkte übernommen, ohne dass sie Fehler waren: der Modul-Zuschnitt (nur Prädikat + Comparator statt voller 3-Stufen-Orchestrierung) und der Hinweis, dass die Playground-Stage-3 heute unidirektional Infix ist und den #224-Bug gar nicht hat. Die Vereinheitlichung entfernt dort Infix-Discovery, das ist eine echte Verhaltensänderung und wird im PR so benannt.

---

## 6. Kickoff-Prompt (copy-paste in die neue Session)

```
Arbeite den Issue-Masterplan autonom ab (Detailfassung: docs/playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md, Stand 2026-07-28).
Betriebsvertrag:

AUTORISIERUNG: Ich genehmige hiermit ausdrücklich Commits + Pushes auf claude/*-Feature-Branches
und das Erstellen von Pull Requests (übersteuert die CLAUDE.md-Regel „never push without approval").
main bleibt absolut tabu (kein Merge, kein Push) — auch PR #223 wird NICHT gemerged. Issues nie selbst
schließen außer per Closes-Trailer im PR-Body; #44 NIE mit Closes referenzieren. Pro Issue ein frischer
Branch von origin/main; nur der Meta-PR wird auf den #190/#140-Branch gestackt. Nie git add -A.
Max. 1 Statuskommentar pro Issue, keine Kontaktaufnahme mit Externen (Linda, Alan, Carina, Silvan, Burch).
Keine Emoji-Icons (Heroicons inline SVG), keine Em-Dashes in Prosa, echte Umlaute.

WELLE 0 (VORFLUG):
- Test-Baseline auf main erheben (npm test aus dem Repo-Root; hiermit genehmigt).
- python scripts/audit/check-index-versions.py.
- playground/js/data/authority-manager.js:135 gegen assets/js/search/search-engine.js:142 lesen
  und die Richtungs-Drift protokollieren (#169/#45).
- assets/js/lib/lemma-match.js als Muster für die Modul-Extraktion einlesen; bestehende
  Such-Specs in testing/tests/ sichten.

WELLE 1 (PR): #224 Stage-3-Fix (refs #169).
- Neues Modul assets/js/lib/lemma-resolve.js: NUR Stage-3-Prädikat + Comparator als pure
  Funktionen; Orchestrierung bleibt je Aufrufer (verschiedene Datenformen).
- Regel: beidseitig präfixorientiert (lemmaNorm.startsWith(query) ODER query.startsWith(lemmaNorm)),
  Mindestlänge 3 nur in der zweiten Richtung. Sortierung nach Längendifferenz, im Playground
  Tie-Break nach Korpus-Frequenz (Lehre #163/#164). KEINE gestufte Fallback-Strategie.
- MESSPFLICHT vor dem Commit: Stage-3-Prädikat direkt aufrufen (Stage 1+2 umgehen),
  300 Formen aus variants.xml mit festem Seed gezogen; Formen mit Normalisierung == Lemma-
  Normalisierung separat ausweisen. Metriken: Recall (wahres Lemma in der Liste, alt vs. neu),
  Median der Listengröße, Top-1 nach Ranking. NICHT die 0-Treffer-Quote als Abbruchkriterium.
  Sample-Bias im Messbericht benennen.
- Im selben PR nachziehen: CONTRACTS.md §C (Pseudocode + „bro"-Beispiel), CLAUDE.md Key Patterns,
  ARCHITECTURE.md, Kommentar tei-ui.js:99-104. testing/tests/search-engine.spec.js:74-81
  (erwartet Stage-3-Treffer für „fri") vorab prüfen und bewusst anpassen.
  Keyness-Pfad app.js:619 mit einem Stage-3-Begriff gegenprüfen.
- Playwright-Regressionstest analog #126/#130.
- Im PR- und Issue-Text nur von Stage-3-Parität sprechen. Benennen, dass die Playground-Stage-3
  heute unidirektional Infix ist und Infix-Discovery dort wegfällt.
- 1 Statuskommentar in #224 mit Ursachenanalyse + Messergebnis; ausdrücklich klarstellen,
  dass es kein WZB-Sonderzeichen-Problem ist.

WELLE 2 (PR): #196 NUM-Filter.
- NUM aus der Hapax-Liste nehmen (Filter-Set analog FUNCTION_WORD_POS, mit sichtbarem
  Ausblend-Zähler statt stiller Unterdrückung).
- KZWs zweiten Auftrag ausführen: alle zwölf TEI-Analyse-Werkzeuge prüfen und je Werkzeug
  BEGRÜNDEN, ob NUM dort sinnvoll ist. Nicht pauschal überall filtern.
- Sub-Issue „TEI-Putzen: 5 Ziffern-Lemmata" anlegen (1/36/42/46/49, 118 Belege in NEIM/BRW/MR1/WVV/NML);
  KZWs Frage im Statuskommentar beantworten: 197 von 202 NUM-Lemmata sind echte Zahlwörter.
- Chrome-Verifikation der Hapax-Liste vorher/nachher. KEINE TEI-Datenänderung in dieser Session.

WELLE 3 (PR): #190 + #140 KZW-Abnahme-Nachbesserungen.
- hilfe-belege-beitragen.html:179 zum vollständigen Satz; :269 auf „CC BY-NC-SA 4.0" kürzen.
- docs/TEI-MODEL.md:7 DRAFT-Kopf ersatzlos entfernen (Woesner ist bereits überall korrekt).
- python scripts/build-pages.py --check; bei neuen Utility-Klassen npm run build:css.
- Closes #190. #140 BLEIBT OFFEN, nur Kommentar mit Bitte um Abnahme.

WELLE 4 (PR): #138 zwei Teilpunkte Julias.
- Nach-oben-Button in der Leseansicht (Heroicons inline SVG, Tastatur-erreichbar).
- state.firstNumericLineShown zurücksetzen (tei-text-reader.js:422), aber NUR an div-Grenzen
  und nur, wenn die erste numerische l des div n="1" trägt. NIE an lg-Grenzen: NBB restartet
  l/@n pro Strophe (1..4), ein lg-Reset reproduziert die #127-Regression. Den bestehenden
  #127-Kommentar fortschreiben, nicht löschen; Regel in CONTRACTS nachziehen. Tests für den
  Reset INKLUSIVE NBB-Fall; reading-view.spec.js muss grün bleiben. Chrome-Verifikation an
  HUG Lied 2 und 3, an NBB und an einem Kapitel-Text.
- PR-Body sagt ausdrücklich, dass ein als #127-Entscheidung dokumentiertes Teilverhalten auf
  Julias Input geändert wird.
- 1 Statuskommentar in #138, der zugleich Julias andere zwei Punkte beantwortet
  (Winkelklammern = korrekte editorische Klammern, Render-Policy-Frage an KZW;
  „Kleinziffern (ii)" nicht lokalisierbar, Textstelle erbeten).

WELLE 5 (STRETCH, nur wenn 1-4 komplett): nur Text-Deliverables.
- #169: Entscheidungsvorlage zu Punkt #45 mit den Messzahlen aus Welle 1, drei benannte Optionen.
- #225: Mail-Entwurf an Burch als Issue-Kommentar (kein Versand, kein Externen-Ping).
- #223: Plausibilitätskommentar am PR (kein Merge).

WELLE 6 (META): #44-Matrix aktualisieren, ROADMAP.md + JOURNAL.md nachziehen, §7 dieses
Playbooks befüllen und §1/§3/§5/§6 für die Folgesession leeren (Meta-PR, auf Welle 3 gestackt).
Abschlussreport als #44-Kommentar: PR-Liste, empfohlene Merge-Reihenfolge (Review-Runs vor dem
Merge canceln), Übersprungenes mit Grund, Wer-wartet-worauf-Liste.

NICHT ANFASSEN: #114 (Review-Gate, Ping ist draußen) / #198 #59 #115 #189 #138-Kern #28 #27 #68
#86 #63 #58 #172 (menschen-blockiert) / #93 #106 #109 #111 #118 #194 #195 #216 #226 #18
(future/extern) / #92 #123 #139 #141 #147 #191 #193 (Ingest). Alle nur in der #44-Matrix einsortieren.

Jede Welle mit Verifikation: npm test gegen die Welle-0-Baseline; bei UI/HTML Chrome-Verifikation
bzw. build-pages.py --check. Unbeschaffbarer Input -> Item dokumentiert überspringen und
weiterarbeiten, NICHT auf mich warten und NICHT fragen.
```

---

## 7. Session-Ergebnis 2026-07-28 (Anhang, vor nächster Session leeren)

Alle sechs Wellen komplett, null blockierende Rückfragen. Output: 5 PRs, 1 neues Issue, 6 Issue-Kommentare, 1 PR-Kommentar, Matrix und Docs nachgezogen.

| Welle | Ergebnis |
|-------|----------|
| 0 | Vorflug: Stage-3-Drift protokolliert, `lemma-match.js` als Muster gelesen, Messskript gebaut. Baseline-Lauf abgebrochen (siehe Lehre 2) |
| 1 | **PR #227**: `lemma-resolve.js` (Prädikat + Comparator), beidseitiges Präfix mit Mindestlänge 3, Messung Top-1 0,3 % → 10,0 %, CONTRACTS §C + ARCHITECTURE + CLAUDE.md + INDEX + ADR-016 nachgezogen, 2 Regressionstests; `search-engine.spec.js` 11/11 |
| 2 | **PR #229**: NUM-Filter (nur reines NUM), begründeter Sweep über alle zwölf Werkzeuge, Chrome-verifiziert (11.815 → 11.862 nach Schärfung). **#228** angelegt |
| 3 | **PR #230**: beide KZW-Textänderungen, `Closes #190`; #140 offen gelassen mit Kommentar |
| 4 | **PR #231**: Nach-oben-Button + Verszählungs-Reset; `reading-view.spec.js` 19/19 plus neuer #138-Test, #127-Tests grün |
| 5 | #169-Entscheidungsvorlage mit Messzahlen, #225-Mailentwurf, #223-Plausibilitätskommentar |
| 6 | #44-Matrix, JOURNAL, ROADMAP, dieses §7; verwaister Commit `ee37bece4` per Cherry-Pick gerettet |

**Merge-Reihenfolge:** #230 → #229 → #231 → #227 → Meta-PR. Kein Daten-PR dabei, Indexe bleiben 4.1.7/1.6.1.

**Lehren (in die nächste Fassung einarbeiten):**

1. **Der Advisor-Durchgang vor dem Start lohnt sich bei Semantik-Änderungen.** Drei echte Planfehler gefunden und alle bestätigt: falsch kalibrierte Messmetrik (0-Treffer-Quote hätte immer ausgelöst), unterspezifizierter Reset-Bereich (hätte über `<lg>` die #127-Regression reproduziert), fehlender Doku-/Spec-Nachzug in derselben Welle. Sollte fester Bestandteil von Welle 0 werden, wenn eine Welle Suchsemantik oder Render-Policy anfasst.
2. **Kein `npm test` als Hintergrund-Baseline, während Dateien geändert werden.** Der Lauf braucht bei 1 Worker über 40 Minuten und testet dann den Zwischenstand. Stattdessen pro Welle die betroffene Spec-Datei gezielt (`npx playwright test --config=testing/playwright.config.js <spec> --reporter=list`, unter 3 Minuten), Voll-Lauf nur einmal am Ende oder gar nicht.
3. **Chrome-Verifikation nicht über den JS-Bridge-Kontext, wenn es um Sichtbarkeit geht.** Dort feuern weder IntersectionObserver-Callbacks noch `scroll`-Events aus `window.scrollTo`. Echtes Scrollen per `computer`-Tool plus Screenshot zeigt das wahre Verhalten; die Bridge taugt für Datenabfragen (`resolveLemmaIds`, DOM-Auszählungen), nicht für Interaktions-Zustände.
4. **Screenshots aus Issues herunterladen und ansehen.** Beide entscheidenden Befunde dieser Session (die drei Kurzlemmata in #224, die Ziffern-Lemmata in #196) standen im Bild, nicht im Text.
5. **`git log origin/main..main` im Vorflug.** Lokales `main` war einen unveröffentlichten Commit voraus; ohne Prüfung wäre er verwaist.
6. **Bei einer Datei, die zwei Wellen berührt** (hier `FEATURES.md`), nicht stacken, sondern den Hunk beim Branch-Wechsel kurz zurücknehmen und auf dem Zielbranch neu setzen. Kostet zwei Edits und hält die PRs unabhängig reviewbar.
