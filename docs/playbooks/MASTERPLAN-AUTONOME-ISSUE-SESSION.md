# Masterplan: Autonome Issue-Abarbeitungs-Session

**Erstellt:** 2026-07-03 (Audit-Session, Fable 5); Vorgänger-Session (Wellen 1-10) ist gelaufen und gemergt.
**Neu befüllt:** 2026-07-12 (Voll-Audit aller 35 offenen Issues, Fable 5). Alte Session-Inhalte geleert; Git-History = Archiv.
**Status:** Session 2026-07-12 GELAUFEN (Kickoff „starte gleich hier", Entscheidungen §5). Ergebnis und Lehren: §7. Vor der nächsten Session §1/§3/§5/§6 neu befüllen.
**Typ:** Playbook (wiederverwendbares Session-Verfahren, dauerhaft). Der session-spezifische Teil (§1, §3, §5, §6) wird pro Session neu befüllt; der Betriebsvertrag (§2) ist der stabile Kern.

Quellen des Audits: alle 35 offenen Issue-Bodies + vollständige Kommentarverläufe (Dump 12.07.), git log (main bis `2d6335856`), Index-Größen-Check für den #111-Trigger (corpus-index.json.gz: 42,2 MB, Schwelle 50 MB, nicht erreicht).

---

## 1. Audit-Ergebnis: 35 offene Issues (Stand 2026-07-12)

Die Lage unterscheidet sich deutlich von der Juli-Anfang-Session: Die damalige Follow-up-Schicht (#158-#164, #167-#171) ist komplett abgeräumt. Was heute offen ist, hängt überwiegend an Menschen (Review-Gates, Kuratorik, needs-clarification) oder ist Ingest/Future. Voll autonom lieferbar sind genau zwei Kern-Deliverables plus die Meta-Pflege.

### A. Voll autonom lösbar (2 + Meta)

| # | Was | Warum autonom | Aufwand |
|---|-----|---------------|---------|
| **#189** | GWTK-Pilot (Punkt 1): Nachannotation der ambigen Formen *rott/rotten/rotte/roten* (139 Tokens) und *jungen/junger* (139 Tokens) in GWTK | Exakt das Muster von #198/PR #205 (autonom gelaufen, gemergt): konservativer Batch nach POS-TAGSET §6.3 mit Review-Artefakten. Externer Goldstandard existiert (händische Zählung der Anfragenden: 78 Belege *rôter munt*, 262 *jung*); alle Akzeptanzkriterien im Issue sind maschinell prüfbar. Bestehende Daten, kein Ingest. Punkt 2 (Quantifizierungs-Skript) ist bereits erledigt (PR #210). | M |
| **#140** | Dokumentation in /docs für Menschen lesbar aufbereiten (LLM-Artefakte bereinigen) | Reine Doku-/Frontend-Arbeit: Steuerungsphrasen wie „(ENTSCHIEDEN)" entfernen, Encoding-Fehler (ae/oe/ue statt ä/ö/ü) und Em-Dashes in Prosa bereinigen, kaputte Markdown-Escapes fixen, Mensch/Agent-Doku trennen. Die einzige Weiche (TEI-MODEL.md ausblenden vs. deklarieren) bietet das Issue selbst als Alternativen an; konservative Variante (als technische Referenz deklarieren) ist ohne Rückfrage wählbar. | M |
| **#44** | Triage-Matrix aktualisieren | Evergreen-Meta-Aufgabe am Session-Ende; **nie schließen**, nie mit Closes referenzieren | S |

### B. Autonome Teilschritte als Stretch (Issue bleibt offen; Freigabe siehe §5)

| # | Autonomer Teil | Bleibt offen wegen |
|---|----------------|--------------------|
| **#59** | Alexander-Decknamen-Workaround: Lindas Frage vom 16.06. ist unbeantwortet. Technischer Vorschlag (Override-Mapping im Build-Skript `scripts/ingest/naming/`, damit Decknamen als Eigenname klassifizierbar werden, ohne Lindas `lemma_normalization.json` zu verbiegen) als Issue-Kommentar-Entwurf; Umsetzung erst nach Lindas OK | Kategorien-Umbenennung („Bezeichnungsvariante"/„Bezeichnungsattribute") ist KZW-Entscheid; Datenhoheit liegt bei Linda |
| **#118** | Konzept-Entscheidungsvorlage Sprachstufen (Regeln + Datenquellen + TEI-Repräsentation + Unsicherheitsstufen) als docs/features/-Dokument + Issue-Kommentar; keine Header-Änderung | Umsetzung ist wissenschaftlich-kuratorisch; Issue ist explizit nachrangig (future plans) |
| **#189-Follow-up** | Nach validiertem GWTK-Pilot: erstes Serien-Issue der Inhaltswort-Schicht anlegen (*minne* zuerst, ~7.000 unsichtbare Belege; Priorisierungsliste aus PR #210) | Serien-Umsetzung ist eigene Kampagne; Funktionswort-Grundsatzentscheidung liegt bei KZW |

### C. Umgesetzt, warten nur auf Test-OK: Session fasst sie NICHT an (5)

#204 (UX Textfilter, KZW gepingt 10.07.), #203 (KWIC-CSV-Export, KZW gepingt 10.07.), #196 (Hapaxlegomena, KZW gepingt 10.07.), #190 (Hilfe-Seite Belegstellen, KZW gepingt 10.07.), #114 (Tabellenansicht-Integrationswünsche, Linda gepingt 02.07.). Alle Pings sind draußen; kein erneutes Anpingen, kein Nacharbeiten vor dem OK (auch nicht der in #196 vermerkte Subkorpus-Follow-up).

### D. Blockiert auf Menschen (13): Session fasst sie NICHT an

#198 (Schritt 2 = KZW-Sense-Split lemma_2598, Review-Artefakte liegen im PR #205), #28 (wartet auf KZW/Julia-Antwort zu den 26 Beispielfällen vom 10.07.; danach wäre Phase 1 autonom), #115 (Rest = Kategorien B/C + Stub-Review, kuratorisch), #138 (KZW-Prüffragen), #169, #172 (needs-clarification/depends-on-human), #86 (Alans Freigabe), #63, #27, #18, #58 (needs-clarification), #68 (KZW-Abnahme), #59 (bis auf Stretch-Teil B).

### E. Future / Trigger / extern blockiert (7): bewusst liegen lassen

#93 (KZW-Entscheid Visualization + dysfunktionale SKOS-URIs), #106 (Rest ist FWF #109; dazu KZWs lokaler Branch `feature/106-reim-belege-versende`), #109 (FWF-Antrag), #111 (Trigger nicht erreicht: 42,2 MB < 50 MB, geprüft 12.07.), #118 (bis auf Stretch-Teil B), #194 (per Issue-Text blockiert auf #193), #195 (externe Dump-Beschaffung + Zenodo-Publikation).

### F. Ingest: nicht Teil dieses Playbooks (7)

#92 (ARITHMETIC), #123 (König vom Odenwald), #139 (CoReMA; laut Memory gemeinsame Einzelsession, nie autonom), #141 (Borte), #147 (Weingrüße), #191 (Flore und Blanscheflur), #193 (Arthurische Pferde).

**Fazit:** 2 Kern-PRs (#189, #140) + Meta (#44) sind der gesamte voll autonome Bestand. Die Stretch-Teilschritte (§1.B) sind Text-/Entwurfs-Deliverables ohne Korpus-Risiko. Alles andere wartet auf Menschen oder ist bewusst ausgelagert.

---

## 2. Betriebsvertrag der autonomen Session

Die CLAUDE.md-Regel „never commit/push without user approval" wird durch den Kickoff-Prompt explizit für `claude/*`-Branches + PR-Erstellung freigegeben. Unverändert hart:

1. **`main` ist tabu.** Kein Merge, kein Push. Alle Ergebnisse = PRs, die chsteiner reviewt und mergt.
2. **Issues werden nie von der Session geschlossen**: nur via `Closes #N` im PR-Body beim Merge. #44 bekommt nie einen Close-Trailer.
3. **Pro PR nur benannte Dateien stagen** (nie `git add -A`), Branch frisch von `origin/main`.
4. **Daten vor Schema**; Data-Change-Lifecycle bei jeder XML-Änderung: variants.xml regenerieren, Corpus- + Authority-Index-Rebuild, API-Rebuild, Versions-Bump an allen drei Stellen (`python scripts/audit/check-index-versions.py` lokal vor Push), deterministische Builds (`git status --porcelain`-Pre-flight).
5. **Verifikation je PR:** `npm test` aus dem Repo-Root (nie `npx playwright test`); Referenz ist die in Welle 0 erhobene Baseline auf main. Bei UI zusätzlich Chrome-Verifikation mit realen Belegen; bei TEI-Änderungen Schema-Validierung; bei HTML-Änderungen `python scripts/build-pages.py --check` und bei neuen Utility-Klassen `npm run build:css`.
6. **Konfliktmanagement ohne Merges:** PRs starten von main; bei Datei-Überschneidung wird der spätere Branch auf den früheren gestackt, PR-Body sagt „nach PR X mergen". Abschlussreport enthält die empfohlene Merge-Reihenfolge und den Hinweis, laufende Opus-Review-Runs vor dem Merge zu canceln (nie `[skip ci]` bei Daten-PRs).
7. **Kommunikation:** max. 1 sachlicher Statuskommentar pro Issue; keine Kontaktaufnahme mit Externen (Linda, Alan, Carina, Silvan); Entwürfe dafür landen als Text im Issue. Keine Emoji-Icons in UI/Doku (Heroicons inline SVG); keine Em-Dashes in Prosa (docs/, Hilfe-Seiten, Issue-Kommentare); echte Umlaute.
8. **Inputs selbst beschaffen:** Für diese Session liegen alle Inputs im Repo bzw. in den Issue-Threads (`gh issue view N --json comments`); es sind keine externen Quellen (Drive/Gmail/Zenodo) nötig. Der Goldstandard für #189 steht im Issue-Body (78 *rôter munt* / 262 *jung*, plus eigene TEI-Auszählung 73 Vers-Kookkurrenzen / 265 junc-Formen). Nur nachweislich Unbeschaffbares wird im Abschlussreport dokumentiert übersprungen; nicht auf chsteiner warten, nicht fragen.

---

## 3. Wellenplan (Reihenfolge = Risiko aufsteigend innerhalb der Kern-Deliverables)

| Welle | Deliverable | Issues | Inhalt |
|-------|-------------|--------|--------|
| **0** | Chat-Report | - | Vorflug: Test-Baseline auf main erheben; `check-index-versions.py` + Index-Freshness prüfen; POS-TAGSET.md §6.3 und die PR-#205-Artefakte (`ingest/pos-disambig/198-habe-nom/`) als Muster einlesen; #189-Datenlage verifizieren (Token-Zählung der 6 Zielformen in GWTK gegen die Issue-Zahlen) |
| **1** | PR 1 | #189 | GWTK-Pilot nach §6.3-Mechanik: alle *rott/rotten/rotte/roten*- und *jungen/junger*-Tokens ohne `@lemmaRef` in GWTK kontext-disambiguieren. Zuordnungen: rot-Formen → `lemma_4954` (*rôt* ADJ) vs. `lemma_4978` (*rote* NOM „Schar"); jung-Formen → `lemma_3157` (*junc* ADJ, inkl. substantivierter Fälle) vs. `lemma_3162` (*jungen* VRB). Konservativ: nur High-Confidence-Änderungen, Rest in `review-faelle.csv`. Artefakte nach `ingest/pos-disambig/189-gwtk-rot-junc/` (diff-liste.csv, stichprobe-50.csv, review-faelle.csv). Validierung gegen Goldstandard: Multi-Lemma-Suche „Im selben Vers" *rôt* + *munt* in GWTK ≥ 73 Treffer; *junc*-Belege in GWTK ~262 (± substantivierte Formen). Kompletter Data-Change-Lifecycle (§2 Regel 4); 1 Statuskommentar in #189 mit Diff-Zusammenfassung + Goldstandard-Abgleich |
| **2** | PR 2 | #140 | Doku-Bereinigungs-Pass über alle docs/*.md: LLM-Steuerungsphrasen raus, Encoding-Fehler + Em-Dashes in Prosa + kaputte Escapes fixen. TEI-MODEL.md (und die ähnlich technischen CONTRACTS/LINECODE/POS-TAGSET/TEI-MODEL-AUTH-FILES) per Einleitungs-Banner als maschinenorientierte Referenz deklarieren, NICHT löschen oder entkernen (Rebuild-Fähigkeits-Kriterium der Health-Check-Checkliste bleibt Pflicht). Verlinkungen auf/in `hilfe-daten-beitragen.html` prüfen; falls HTML angefasst: `build-pages.py --check`. Danach Flow-Check über jede geänderte Datei; Doc-Count-Drift-Kontrolle (INDEX/FEATURES/ARCHITECTURE/DECISIONS/DESIGN) |
| **3** | Stretch (nur wenn 1-2 komplett UND in §5 freigegeben) | #59-Teil, #118-Teil, #189-Follow-up | Nur Text-/Entwurfs-Deliverables: (a) #59 Workaround-Vorschlag als Issue-Kommentar (Override-Mapping-Design, kein Code-Merge-Anspruch); (b) #118 Konzept-Entscheidungsvorlage als docs/features/-Doc + Kommentar; (c) nach bestandenem Goldstandard-Abgleich aus Welle 1: Serien-Issue „Inhaltswort-Homographen: minne" anlegen (Mechanik-Verweis auf #189-Pilot + PR #210-Priorisierungsliste) |
| **4** | Meta-PR + #44-Kommentar | #44, docs | Triage-Matrix aktualisieren (inkl. Kategorien C-F dieses Audits), ROADMAP.md + JOURNAL.md nachziehen; Abschlussreport als #44-Kommentar: PR-Liste + empfohlene Merge-Reihenfolge + Übersprungenes (mit Grund) + Wer-wartet-worauf-Liste (KZW: #204/#203/#196/#190/#198-Schritt-2/#28-Beispielfälle/#115-B/C; Linda: #114/#59) |

Geschätzter Output: 3-4 PRs, 2 Issues substanziell abgeräumt (#189-Pilot, #140), Meta gepflegt, null blockierende Rückfragen.

---

## 4. Nicht anfassen

- **Review-Gates (Pings sind draußen):** #204, #203, #196, #190, #114
- **Menschen-blockiert:** #198 (Schritt 2), #28, #115 (B/C), #138, #169, #172, #86, #68, #63, #59 (außer Stretch-Kommentar), #58, #27, #18
- **Future/Trigger/extern:** #93, #106, #109, #111, #118 (außer Stretch-Vorlage), #194, #195
- **Ingest:** #92, #123, #139, #141, #147, #191, #193
- Alle Gruppen nur in der #44-Matrix korrekt einsortieren.

---

## 5. Getroffene Entscheidungen (chsteiner, 2026-07-12)

1. **Stretch-Welle 3:** an, aber strikt erst nach Abschluss der Wellen 1-2.
2. **#59-Workaround:** nur Kommentar-Entwurf (Override-Mapping-Design als Issue-Kommentar). Kein Code-PR; Datenhoheit liegt bei Linda, Kategorien-Frage parallel bei KZW.
3. **#189-Serien-Issue (minne):** ja, anlegen sobald der Pilot den Goldstandard erfüllt. Reine Issue-Anlage, keine Umsetzung.
4. **#140-Tiefe:** nur Bereinigung + Deklarations-Banner. Keine strukturellen Umbauten; Strukturfragen gehören in einen Health-Check mit Begründungsliste.

---

## 6. Kickoff-Prompt (copy-paste in die neue Session)

```
Arbeite den Issue-Masterplan autonom ab (Detailfassung: docs/playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md, Stand 2026-07-12).
Betriebsvertrag:

AUTORISIERUNG: Ich genehmige hiermit ausdrücklich Commits + Pushes auf claude/*-Feature-Branches
und das Erstellen von Pull Requests (übersteuert die CLAUDE.md-Regel „never push without approval").
main bleibt absolut tabu (kein Merge, kein Push). Issues nie selbst schließen (nur via Closes-Trailer
im PR-Body; #44 NIE mit Closes referenzieren). Pro Issue ein frischer Branch von origin/main;
bei Datei-Überschneidung auf den Vorgänger-PR stacken und das im PR-Body vermerken. Nie git add -A.
Max. 1 Statuskommentar pro Issue, keine Kontaktaufnahme mit Externen (Linda, Alan, Carina, Silvan).
Keine Emoji-Icons, keine Em-Dashes in Prosa, echte Umlaute.

WELLE 0 (VORFLUG):
- Test-Baseline auf main erheben (npm test aus dem Repo-Root; hiermit genehmigt).
- python scripts/audit/check-index-versions.py + Index-Freshness prüfen.
- Muster einlesen: docs/POS-TAGSET.md §6.3 und die Review-Artefakte aus PR #205
  (ingest/pos-disambig/198-habe-nom/: diff-liste.csv, stichprobe-50.csv, review-faelle.csv).
- #189-Datenlage verifizieren: Token-Zählung der Formen rott/rotten/rotte/roten und
  jungen/junger ohne @lemmaRef in tei/GWTK.tei.xml gegen die Issue-Zahlen (je 139).

WELLE 1 (PR): #189 GWTK-Pilot, Punkt 1.
- Kontext-Disambiguierung aller unannotierten Zielform-Tokens in GWTK nach §6.3-Mechanik,
  konservativ (nur High-Confidence; Rest nach review-faelle.csv).
- Zuordnungen: rot-Formen -> lemma_4954 (rôt ADJ) vs. lemma_4978 (rote NOM „Schar");
  jung-Formen -> lemma_3157 (junc ADJ, inkl. substantivierter Faelle) vs. lemma_3162 (jungen VRB).
- Artefakte nach ingest/pos-disambig/189-gwtk-rot-junc/.
- Validierung gegen den Goldstandard aus dem Issue: Multi-Lemma-Suche „Im selben Vers"
  rôt + munt in GWTK >= 73 Treffer; junc in GWTK ~262 Belege (± substantivierte Formen).
- Kompletter Data-Change-Lifecycle: variants.xml regenerieren, Corpus- + Authority-Index-
  Rebuild, API-Rebuild, Versions-Bump an allen drei Stellen, Schema-Validierung,
  deterministischer Build. 1 Statuskommentar in #189 (Diff-Zusammenfassung + Goldstandard-Abgleich).

WELLE 2 (PR): #140 Doku-Bereinigung.
- Alle docs/*.md: LLM-Steuerungsphrasen (z. B. „(ENTSCHIEDEN)") raus, Encoding-Fehler
  (ae/oe/ue statt ä/ö/ü), Em-Dashes in Prosa und kaputte Markdown-Escapes fixen.
- TEI-MODEL.md und die ähnlich technischen Referenzen (CONTRACTS, LINECODE, POS-TAGSET,
  TEI-MODEL-AUTH-FILES) per Einleitungs-Banner als maschinenorientierte Referenz deklarieren.
  NICHTS löschen oder entkernen; die Docs müssen rekonstruktionsfähig bleiben
  (Health-Check-Kriterium). Keine strukturellen Umbauten, nur Bereinigung.
- Verlinkungen auf/in hilfe-daten-beitragen.html prüfen; falls HTML angefasst:
  python scripts/build-pages.py --check; bei neuen Utility-Klassen npm run build:css.
- Danach Flow-Check über jede geänderte Datei + Doc-Count-Drift-Kontrolle.

WELLE 3 (STRETCH, nur wenn Wellen 1-2 komplett): nur Text-/Entwurfs-Deliverables.
- #59: Workaround-Vorschlag für Lindas Alexander-Decknamen-Frage (16.06.) als Issue-Kommentar
  (Override-Mapping-Design im Build-Skript, kein Code, keine Umsetzung); die Kategorien-
  Umbenennungs-Frage NICHT beantworten (KZW-Entscheid).
- #118: Konzept-Entscheidungsvorlage Sprachstufen als docs/features/-Doc + Issue-Kommentar,
  keine Header-Änderung.
- #189-Follow-up: NUR wenn der Goldstandard-Abgleich aus Welle 1 bestanden ist, das erste
  Serien-Issue „Inhaltswort-Homographen: minne" anlegen (Mechanik-Verweis auf Pilot + PR #210).

WELLE 4 (META): #44-Matrix komplett aktualisieren, ROADMAP.md + JOURNAL.md nachziehen (PR);
Abschlussreport als #44-Kommentar: PR-Liste + empfohlene Merge-Reihenfolge (inkl. Hinweis,
laufende Review-Runs vor dem Merge zu canceln; bei Daten-PRs nie [skip ci]) + Übersprungenes
mit Grund + Wer-wartet-worauf-Liste (KZW: #204/#203/#196/#190/#198-Schritt-2/#28-Beispielfälle/
#115-B/C; Linda: #114/#59).

NICHT ANFASSEN: #204 #203 #196 #190 #114 (Review-Gates, Pings sind draußen) / #198 #28 #115
#138 #169 #172 #86 #68 #63 #58 #27 #18 (menschen-blockiert; #59 nur Stretch-Kommentar) /
#93 #106 #109 #111 #194 #195 (future/extern; #118 nur Stretch-Vorlage) / #92 #123 #139 #141
#147 #191 #193 (Ingest). Alle nur in der #44-Matrix einsortieren.

Jede Welle mit Verifikation: npm test gegen die Welle-0-Baseline; bei TEI-Änderungen
Schema-Validierung; bei Index-Änderungen check-index-versions.py; bei UI/HTML Chrome-
Verifikation bzw. build-pages.py --check. Unbeschaffbarer Input -> Item dokumentiert
überspringen und weiterarbeiten, NICHT auf mich warten und NICHT fragen.
```

---

## 7. Session-Ergebnis 2026-07-12 (Anhang, vor nächster Session leeren)

Alle 4 Wellen komplett, null blockierende Rückfragen. Output: 3 PRs, 1 neues Issue, 4 Issue-Kommentare, Matrix + Docs nachgezogen.

| Welle | Ergebnis |
|-------|----------|
| 0 | Baseline 212/212; Indexe synchron; variants.xml hart drift-frei verifiziert; GWTK-Zahlen exakt bestätigt (2×139) |
| 1 | **PR #214**: 257/278 Tokens annotiert (21 Review), Goldstandard exakt (73 rôt+munt-Verse, 259 junc); Corpus v4.1.7 + Authority v1.6.1 + API; 212/212 |
| 2 | **PR #215**: 252 Encoding-Fixes + 418 Em→En-Dashes + 4 Marker + 5 Banner; doc-count-audit grün; 212/212 |
| 3 | #59-Workaround-Entwurf (ohne Linda-Ping), #118-Entscheidungsvorlage (Kommentar + features-Doc), **#216** minne-Serie angelegt |
| 4 | #44-Matrix aktualisiert (Body-Edit), JOURNAL + ROADMAP nachgezogen, Meta-PR (auf #215 gestackt), Abschlussreport in #44 |

**Merge-Reihenfolge:** #214 (Daten-PR: Review-Runs canceln, kein [skip ci]) → #215 → Meta-PR.

**Lehren (in die nächste Fassung einarbeiten):**
1. **3-Commit-Muster auf Daten-Branches:** Die Pre-flight-Gates der Build-Skripte (#100) verlangen saubere Quell-Trees; auf Branches heißt das Quellen-Commit → Index-Commit → API-Commit. Der Squash-Merge stellt den Ein-Commit-Lifecycle auf main wieder her. Gehört als Standard in §2 Regel 4.
2. **Freshness-Check nach Checkout misstrauen:** mtime-Rauschen erzeugt False Positives; hart verifizieren per Regenerat-Vergleich (`cmp` gegen `variants.regen.xml` – der Dry-Run schreibt NICHT in die Live-Datei, `git diff` greift ins Leere).
3. **Lexikon-Senses der Kandidaten VOR dem Batch prüfen:** verborgene Lesarten stecken im selben Lemma (rote = Schar UND Saiteninstrument via sense_7735). Kandidaten-Erweiterung übers Issue hinaus lohnt (4 genannt, 7 relevant).
4. **Moderations-Pass-Muster:** Subagenten-Verdicts nur mit dokumentiertem Beleg heben (hier: 2 andere Shards fanden dieselbe Zuordnung unabhängig = Bestätigung); Kennzeichnung in Diff-Liste + README.
5. **revisionDesc ist P-MUSS (§6.3.5):** PR #205 hatte den Eintrag ausgelassen; diese Session hat ihn gesetzt. Bei künftigen Batches nicht dem #205-IST folgen, sondern der Policy.
6. **Externen-Regel greift auch bei Assignees:** Linda ist Issue-Beteiligte, aber laut Betriebsvertrag extern → Entwurf ohne @-Ping, Team gibt frei.
