# Masterplan: Autonome Issue-Abarbeitungs-Session

**Erstellt:** 2026-07-03 (Audit-Session, Fable 5)
**Status:** Freigegeben durch chsteiner (Entscheidungen siehe §5)
**Update 2026-07-07:** An den Repo-Stand nach Merge von PR #165 + #173 angepasst: Audit-Sammel-Issues #167–#172 einsortiert (§1.E), Wellen 1/9/10 und Kickoff-Prompt aktualisiert, Test-Baseline-Formulierung entschärft.
**Typ:** Temporal Artifact (Promptotyping-Konvention) — nach Abschluss der autonomen Session löschen; Git-History = Archiv.

Quellen des Audits: alle 35 offenen Issue-Bodies (Dump 03.07.), Triage-Matrix #44 (Stand 17.06.), ROADMAP.md, JOURNAL.md (bis 02.07.), PR #165 (Code-Audit-Report, 113 Findings). Cross-Check durch unabhängigen Digest-Agenten: bestätigt, keine Widersprüche.

---

## 1. Audit-Ergebnis: 35 offene Issues

### A. Voll autonom lösbar (10)

| # | Was | Warum autonom | Aufwand |
|---|-----|---------------|---------|
| **#163** | Kookkurrenz-Dropdown wählt immer erstes Lemma (KZW-Bugreport 03.07.) | Reproduzierbarer Frontend-Bug | S |
| **#164** | Multi-Lemma `rôt + munt` liefert nichts (KZW-Bugreport 03.07.) | Vermutlich gleiche Wurzel wie #163 (Lemma-Auflösung/Homographen); alte MHDBDB als Ground Truth (553 Zeilen-Treffer) | S–M |
| **#158 + #162** | Duplikat-Paar: leere `.lb-number`-Spans bei `h_`-Nummern; Test dauerhaft rot auf main | Fix + Test-Anpassung; maskiert aktuell echte Regressionen | S |
| **#159** | View-Clobber nach Navigation pattern-weit fixen | Lösung im Issue vorgezeichnet (Router-globales Abort-Signal) | M |
| **#160** | Tabellen-Spaltenmodell deklarativ konsolidieren (7 Sync-Stellen) + KWIC-Test | Reines Refactoring, Regressionsnetz existiert (`results-table.spec.js`) | M |
| **#161** | Multi-POS-Verlust im Authority-Index (silent data loss, betrifft API) | Lösungsweg A (additives `posAll[]`) im Issue empfohlen | M |
| **#134** | AK-Kontext (Ausschnitt der Steirischen Reimchronik, Verse 44579–53866) im Reader | Daten liegen in AK.tei.xml, nur Reader-JS (#44: claude-ready) | M |
| **#145** | Rektoratsbericht + Dankesbrief über 20.480 € | Schreibarbeit aus bestehender Doku; KZW-Review danach | M |
| **#27** | POS-Workflow: Disambiguierungs-Policy | KZW hat Policy ans LLM delegiert (29.05., Tagset fixiert); **Scope: NUR Policy-Dokument** (Entscheidung chsteiner 03.07.) | L |
| **#44** | Triage-Matrix aktualisieren | Evergreen-Meta-Aufgabe am Session-Ende; **nie schließen** | S |

### B. Autonom als definierter Teilschritt — Issue bleibt offen (7)

| # | Autonomer Teil | Bleibt offen wegen |
|---|----------------|--------------------|
| **#138** | HUG-Strophen-`<lg>` aus 814 röm. Ziffern ableiten + Index-Rebuild; MBS-Sub-Issue in #139 anlegen (KZW-Entscheid 12.06. liegt vor) | PL1–3-Kapitel brauchen Editionsmaterial |
| **#68** | KZWs MUSS/SOLL-Intake-Kriterien (geliefert 29.05.) in `hilfe-daten-beitragen.html` einbauen | Abnahme KZW |
| **#86** | van-Beek-Kontaktdaten in `barrierefreiheit.html` (KZW-Wunsch 29.05.) | Alans Freigabe des Gesamttexts |
| **#110** | WVV: 23 fehlende Anchors rekonstruieren, Korpus-Survey Ton/dône, TEI-Pattern als Entscheidungsvorlage | Finale Strophen-Entscheidung = KZW |
| **#28** | Daten-Phasenplan Fremdsprachen-Annotation (Weg von KZW freigegeben: LLM + `concept_23123000` + Lexer/MWB) | Korpus hat 0 Token-Annotationen; Umsetzung = eigene Kampagne |
| **#141** | Borte „Aufgabe 0": Metadaten-Template + Anforderungsliste an Alan (Quelltabelle: Zenodo 10.5281/zenodo.20626546) | Gesamt-Ingest wartet auf KZW-Priorisierung (nach #139) |
| **#106** | Optional (Stretch): Punkt 8 „Lemma im Vers"-Filter | Punkte 2–7 sind FWF (#109) |

**Bonus-Workstream (aktualisiert 07.07.):** PR #165 + #173 sind gemerged; alle Low-Risk-Findings sind behoben, die Rest-Findings leben strukturiert in den Sammel-Issues #167–#172 (Einsortierung: §1.E). Autonomes Abarbeitungsfeld für die Stretch-Welle: #167, #170, #171.

### C. Blockiert auf Menschen (10) — Session fasst sie NICHT an

#92 (Carina: 5–6 Metadatenfragen), #147 (Silvan: Lizenz Wiki-Transkriptionen; Stage-0-Parser-Entwurf als Stretch erlaubt), #114 (Linda-Review), #129 (KZW-UI-Test), #59 (Linda-Fachklärung), #115 B/C (KZW-Kuratorik, 196 Lemmata), #124 (Matomo-Snippet Bärthlein), #140 (Strategie-Gespräch mit chsteiner), #58 (chsteiner-Entscheidung Option A/B/C), #18 (blockiert durch #27-Datenmigration).

### D. Future / Trigger-Wait (7) — bewusst liegen lassen

#63, #93, #109, #111 (Trigger: Index > 50 MB gz), #118, #123, #139.

### E. Nachtrag 07.07.: Audit-Sammel-Issues #167–#172 (nach Plan-Erstellung angelegt)

Die Rest-Findings aus dem Code-Audit wurden am 03.07. nach Erstellung dieses Plans in sechs Sammel-Issues überführt (PR #173, Commit `cdd8f1c65`). Einsortierung:

| # | Was | Einsortierung |
|---|-----|---------------|
| **#167** | Frontend-/Playground-Kleinbugs (10 verifizierte Fixes, kein Entscheidungsbedarf) | Stretch (Welle 9) |
| **#168** | Race-Conditions Reader + Begriffs-Verteilung (Generation-Token) | **Welle 1**, zusammen mit #159: das Issue empfiehlt selbst, Router-Abort-Signal (Cross-View) und Same-View-Guards gemeinsam zu designen, z. B. als Navigation-Epoch-Zähler |
| **#169** | Suchsemantik-Entscheidungen (Nähesuche-Distanz, 3-Stufen-Drift, commonLemmas, Dedup) | Blockiert (needs-clarification, KZW/Team). Aber: bei der #163/#164-Diagnose in Welle 1 querlesen, das Issue vermerkt eine mögliche gemeinsame Wurzel; Diagnose-Erkenntnisse als Kommentar in #169, die 4 Semantik-Fixes selbst nicht umsetzen |
| **#170** | Latente §B/§B.1-Paritäts-Drifts (heute verhaltensneutral; Gate: byte-identischer Index-Rebuild) | Stretch (Welle 9), vor dem nächsten Ingest sinnvoll |
| **#171** | Python-Skript-Bugs (Build/Ingest/Audit) | Stretch (Welle 9); Priorität laut Issue: ARI-Escaping vor dem nächsten #92-Lauf, insert-stanzas-Fixes (#35/#36) vor jedem WVV-Bulk-Run (#110) |
| **#172** | Test-Suite-Entscheidungen (45%-passRate-Floor, Magic-Numbers) | Blockiert (needs-clarification); nur in der #44-Matrix einsortieren |

**Fazit:** 17 von 35 Issues (Stand 03.07.) haben einen autonom lieferbaren Kern; mit den Sammel-Issues aus §1.E (Stand 07.07.: 41 offene Issues) kommen #168 (Welle 1) sowie #167/#170/#171 (Stretch) dazu. Die Follow-up-Schicht der letzten zwei Wochen (#158–#164) ist komplett autonom wegräumbar.

---

## 2. Betriebsvertrag der autonomen Session

Die CLAUDE.md-Regel „never commit/push without user approval" wird durch den Kickoff-Prompt explizit für `claude/*`-Branches + PR-Erstellung freigegeben. Unverändert hart:

1. **`main` ist tabu.** Kein Merge, kein Push. Alle Ergebnisse = PRs, die chsteiner reviewt und mergt.
2. **Issues werden nie von der Session geschlossen** — nur via `Closes #N` im PR-Body beim Merge. #44 bekommt nie einen Close-Trailer.
3. **Pro PR nur benannte Dateien stagen** (nie `git add -A`), Branch frisch von `origin/main`.
4. **Daten vor Schema**; Data-Change-Lifecycle (Index-Rebuild + API + Versions-Bump) bei jeder XML-Änderung; deterministische Builds.
5. **Verifikation je PR:** `npm test` aus `testing/` (Referenz: die in Welle 0 erhobene Baseline. Stand 03.07. waren 2 Fails bekannt: Wörterbuchnetz extern + #158, das die Session selbst grün macht; nach der Test-Härtung in PR #173 kann sich das verschoben haben, daher neu erheben); bei UI zusätzlich Chrome-Verifikation mit realen Belegen; bei TEI-Änderungen Schema-Validierung.
6. **Konfliktmanagement ohne Merges:** PRs starten von main; bei Datei-Überschneidung wird der spätere Branch auf den früheren gestackt, PR-Body sagt „nach PR X mergen". Abschlussreport enthält die empfohlene Merge-Reihenfolge.
7. **Kommunikation:** max. 1 sachlicher Statuskommentar pro Issue; keine Kontaktaufnahme mit Externen (Alan, Carina, Silvan) — Entwürfe dafür landen als Text im Issue.
8. **Missing-Inputs-Report zuerst** (Entscheidung chsteiner 03.07.): Allererste Chat-Ausgabe der Session = vollständige Liste aller nicht zugänglichen Inputs; chsteiner providet direkt in die Session. Nicht warten — unabhängige Wellen laufen weiter, input-abhängige Items werden nachgezogen.

---

## 3. Wellenplan (Reihenfolge = Risiko aufsteigend, Nutzerwert absteigend)

| Welle | Deliverable | Issues | Inhalt |
|-------|-------------|--------|--------|
| **0** | Chat-Report | — | Vorflug: Missing-Inputs-Report (PFLICHT, zuerst), Test-Baseline auf main, AUDIT-REPORT.md-Stand einlesen |
| **1** | PR 1 | #163, #164, #159, #168 | Gemeinsame Wurzel Dropdown/Lemma-Auflösung fixen (dabei #169 querlesen: mögliche gemeinsame Wurzel in der 3-Stufen-Auflösung, Erkenntnisse dort kommentieren); `rôt + munt` gegen 553-Treffer-Erwartung plausibilisieren; Router-globales Abort-Signal zusammen mit #168-Generation-Token designen (Navigation-Epoch) + DESIGN.md |
| **2** | PR 2 | #158, #162 | `h_`-Nummern-Fix + Test-Umstellung (konservativ: Span für `h_` unterdrücken, Test auf echte Prosazeile), Begründung im PR; Duplikat-Hinweis als Kommentar |
| **3** | PR 3 | #160 | Deklarative Spalten-Spec in `app.js` + KWIC-Aufklapp-Playwright-Test |
| **4** | PR 4 | #161 | Option A: `posAll[]` additiv, Authority-Index-Bump, API-Rebuild, Konsumenten, CONTRACTS §G; Verifikation an lemma_79188 `salve` u. a. |
| **5** | PR 5 | #134 | AK-Ausschnitts-Kontext in Metadaten-Panel + Reader, wiederverwendbar für künftige Ausschnittstexte |
| **6** | PR 6 | #138-Rest | HUG-`<lg>` aus 814 röm. Ziffern (`insert-lg-stanzas-138.py`), Schema-Validierung, Index-Rebuild; MBS-Sub-Issue in #139 anlegen; veraltete Blocker-Labels vermerken |
| **7** | PR 7 | #68, #86-Teil | Intake-Kriterien in `hilfe-daten-beitragen.html`; van-Beek-Kontakt in `barrierefreiheit.html`; `build-pages.py --check` als Gate |
| **8** | PRs + Kommentare | #145, #27, #28, #110, #141 | Text-Deliverables: Rektoratsbericht (publications/, PR); POS-Policy-Dokument (**nur Doku, kein Pilot, keine Korpus-Änderung**); Fremdsprachen-Phasenplan (Kommentar + docs/features/); WVV-Entscheidungsvorlage (Kommentar); Borte-Aufgabe-0 (Kommentar) |
| **9** | Stretch | #167, #170, #171, opt. #106.8, opt. #147 | Nur wenn 1–8 komplett: Sammel-Issues in getrennten PRs, kollisionsfreie Dateien zuerst: #167 (Frontend-Kleinbugs), #170 (Paritäts-Drifts; Gate: byte-identischer Index-Rebuild), #171 (Python-Skript-Bugs; ARI-Escaping + insert-stanzas-Fixes priorisieren); optional „Lemma im Vers"-Filter; optional #147 Stage-0-Parser-Entwurf (KEINE Transkriptionsdaten committen, Lizenz-Klärungsliste als Kommentar) |
| **10** | Meta-PR + #44-Kommentar | #44, docs | Matrix komplett neu (inkl. #158–#164, #167–#172 + Session-Ergebnisse), ROADMAP.md + JOURNAL.md; Abschlussreport: PR-Liste + Merge-Reihenfolge + Übersprungenes (mit Grund) + Wer-wartet-worauf |

Geschätzter Output: 9–11 PRs, ~13–17 Issues ganz oder teilweise abgeräumt, null blockierende Rückfragen.

---

## 4. Nicht anfassen

- **Menschen-blockiert:** #92, #147 (außer Stretch-Entwurf), #114, #129, #59, #115 (B/C), #124, #140, #58, #18, #169 (nur Diagnose-Kommentar aus Welle 1 erlaubt, keine Semantik-Fixes), #172
- **Future/Trigger:** #63, #93, #109, #111, #118, #123, #139
- Beide Gruppen nur in der #44-Matrix korrekt einsortieren.

---

## 5. Getroffene Entscheidungen (chsteiner, 03.07.2026)

1. **PR #165 (Audit-Report):** chsteiner behandelt den Branch vor Kickoff selbst. *Erledigt 03.07.: PR #165 + #173 gemerged, Rest-Findings in #167–#172 überführt.*
2. **Stretch-Welle 9:** an, aber strikt nur nach Abschluss der Wellen 1–8 (Default).
3. **#27-Scope:** NUR Policy-Dokument. Kein Pilot — Thema komplex und token-intensiv.
4. **Missing Inputs:** Session meldet zuallererst alle nicht zugänglichen Daten; chsteiner providet sie direkt in die Session.

---

## 6. Kickoff-Prompt (copy-paste in die neue Session)

```
Arbeite den Issue-Masterplan autonom ab (Detailfassung: docs/features/MASTERPLAN-AUTONOME-ISSUE-SESSION.md).
Betriebsvertrag:

AUTORISIERUNG: Ich genehmige hiermit ausdrücklich Commits + Pushes auf claude/*-Feature-Branches
und das Erstellen von Pull Requests (übersteuert die CLAUDE.md-Regel „never push without approval").
main bleibt absolut tabu (kein Merge, kein Push). Issues nie selbst schließen (nur via Closes-Trailer
im PR-Body; #44 NIE mit Closes referenzieren). Pro Issue/Cluster ein frischer Branch von origin/main;
bei Datei-Überschneidung auf den Vorgänger-PR stacken und das im PR-Body vermerken. Nie git add -A.
Max. 1 Statuskommentar pro Issue, keine Kontaktaufnahme mit Externen.

WELLE 0 — VORFLUG + MISSING-INPUTS-REPORT (PFLICHT, ALLERERSTE AUSGABE):
Bevor du irgendetwas implementierst: prüfe die Zugänglichkeit ALLER benötigten Inputs und melde
mir als allererste Chat-Nachricht eine vollständige Liste dessen, was du NICHT lesen kannst
(z.B. PDF-Anhänge in #145, Kontaktdaten in #86-Kommentaren, KZW-Intake-Kriterien in #68,
Dry-Run-Output/Linecode-Quelle für #110, Zenodo-Tabelle für #141). Ich providere fehlende Daten
direkt in diese Session. Danach NICHT warten: sofort mit allen Wellen fortfahren, die nicht von
fehlenden Inputs abhängen; blockierte Items nachziehen, sobald ich die Daten geliefert habe,
sonst am Ende als übersprungen dokumentieren. Außerdem in Welle 0: Test-Baseline auf main
erheben (Stand 03.07. waren 2 Fails bekannt; nach der Test-Härtung in PR #173 neu messen) und
den aktuellen Stand des Code-Audit-Reports einlesen (AUDIT-REPORT.md im Repo-Root; PR #165 +
#173 sind gemerged, die Rest-Findings leben in den Sammel-Issues #167-#172).

REIHENFOLGE (Wellen, jede mit npm test aus testing/ + Chrome-Verifikation bei UI + Schema-Validierung
+ Index/API-Rebuild mit Versions-Bump bei XML-Änderungen):
1. PR: #163 + #164 (gemeinsame Wurzel Lemma-Dropdown/-Auflösung; Ground Truth: alte MHDBDB
   liefert für rot+munt 553 Zeilen-Treffer) + #159 + #168 (Cross-View-Clobber und Same-View-Races
   zusammen designen, z.B. Router-globaler Navigation-Epoch-Zähler; DESIGN.md nachziehen).
   Bei der #163/#164-Diagnose #169 querlesen (mögliche gemeinsame Wurzel in der 3-Stufen-
   Auflösung); Erkenntnisse als Kommentar in #169, dessen 4 Semantik-Fixes selbst NICHT
   umsetzen (KZW-Entscheid nötig).
2. PR: #158 + #162 (Duplikate; h_-Nummern-Fix + Test-Umstellung, Entscheidung im PR begründen).
3. PR: #160 deklaratives Spaltenmodell app.js + KWIC-Detail-Playwright-Test.
4. PR: #161 Option A (posAll[] additiv, Authority-Index-Bump, API-Rebuild, Konsumenten,
   CONTRACTS §G); Verifikation an lemma_79188 salve u.a.
5. PR: #134 AK-Ausschnitts-Kontext (Steirische Reimchronik, Verse 44579–53866) in
   Metadaten-Panel + Reader; wiederverwendbar für künftige Ausschnittstexte.
6. PR: #138-Rest — HUG-<lg> aus 814 röm. Ziffern (insert-lg-stanzas-138.py), Index-Rebuild;
   MBS-Sub-Issue in #139 anlegen; veraltete Blocker-Labels im Issue vermerken.
7. PR: #68 KZW-Intake-Kriterien in hilfe-daten-beitragen.html + #86-Teilschritt van-Beek-
   Kontaktdaten in barrierefreiheit.html (build-pages.py --check als Gate).
8. Text-Deliverables:
   - #145 Bericht + Dankesbrief nach publications/ (PR); Basis: KV 32/25 + 33/25 + Projekt-Doku.
   - #27 NUR Policy-Dokument (implementierbare POS-Disambiguierungs-Policy auf Basis
     POS-TAGSET.md + Issue-Regeln). KEIN Pilot, KEINE Korpus-Änderung, KEINE Token-Kampagne —
     das Thema ist bewusst auf das Dokument begrenzt.
   - #28 Daten-Phasenplan (Issue-Kommentar + docs/features/-Doc), keine Implementierung.
   - #110 Anchor-Rekonstruktion + Ton/dône-Survey + TEI-Pattern als Entscheidungsvorlage
     (Kommentar, kein Korpus-Commit).
   - #141 Aufgabe 0: borte.md-Metadaten-Template + präzise Anforderungsliste an Alan
     (Issue-Kommentar, nichts versenden).
9. Stretch NUR wenn Wellen 1–8 komplett: Sammel-Issues als getrennte PRs, kollisionsfreie
   Dateien zuerst — #167 (Frontend-Kleinbugs), #170 (Paritäts-Drifts; Gate: byte-identischer
   Index-Rebuild), #171 (Python-Skript-Bugs; ARI-Escaping vor #92 und insert-stanzas-Fixes
   vor jedem WVV-Bulk-Run priorisieren); optional #106 Punkt 8; optional #147 Stage-0-Parser
   als Entwurf (KEINE Transkriptionsdaten committen, Lizenz-Klärungsliste als Kommentar).
10. Meta: #44-Matrix komplett aktualisieren (inkl. #158–#164, #167–#172 + Session-Ergebnisse),
    ROADMAP.md + JOURNAL.md nachziehen (PR), Abschlussreport als #44-Kommentar mit PR-Liste +
    empfohlener Merge-Reihenfolge + Übersprungenem (mit Grund) + Wer-wird-worauf-gewartet-Liste.

NICHT ANFASSEN: #92 #147(außer Stretch-Entwurf) #114 #129 #59 #115(B/C) #124 #140 #58 #18
#169(nur Diagnose-Kommentar aus Welle 1 erlaubt) #172 (menschen-blockiert) und #63 #93 #109
#111 #118 #123 #139 (future) — nur in der #44-Matrix korrekt einsortieren.

Fehlender Input, der nicht nachgeliefert wurde → Issue überspringen + im Abschlussreport
begründen, NICHT auf mich warten und NICHT fragen.
```
