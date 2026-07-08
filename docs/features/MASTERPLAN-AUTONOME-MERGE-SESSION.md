# Masterplan: Autonome Merge-Session

Gegenstück zum `MASTERPLAN-AUTONOME-ISSUE-SESSION.md`: Während die Issue-Session PRs **erzeugt**, arbeitet die Merge-Session den offenen PR-Bestand **nach main ab**. Wiederverwendbares Verfahren; der konkrete PR-Bestand steht jeweils im Anhang. Temporal Artifact: nach erfolgreicher Session Kernwissen ins JOURNAL, Datei aktualisieren oder löschen.

## Betriebsvertrag (gilt nur nach explizitem User-Kickoff)

Dieser Plan autorisiert NICHTS. Eine Merge-Session startet erst, wenn der User sie mit einem Kickoff-Prompt eröffnet, der ausdrücklich enthält:

1. **Merge-Autorisierung nach main** für die benannten PRs (übersteuert CLAUDE.md „NEVER commit or push without user testing and approval" — der Kickoff IST die Approval; ohne ihn bleibt main tabu).
2. Umfang: alle offenen claude/*-PRs oder eine explizite Teilmenge.
3. Ob Live-Smoke-Checks nach Deploy Teil der Session sind (empfohlen: ja).

Unverändert aus dem Issue-Session-Vertrag: Issues nie manuell schließen (nur via Closes-Trailer beim Merge; **#44 NIE**), nie `git add -A`, kein Force-Push auf main, max. 1 neuer Statuskommentar pro Issue (KZW-UI-Ping nach Live-Gang ist die etablierte Ausnahme laut Projektkonvention), keine Kontaktaufnahme mit Externen. Nicht fragen, nicht warten — bei Blockern dokumentiert überspringen.

## Merge-Gates (jeder PR, keine Ausnahme)

Ein PR wird nur gemerged, wenn ALLE Gates grün sind:

- **G1 CI grün** auf dem aktuellen Head (nach Retarget/Rebase neu abwarten!).
- **G2 Review-Triage abgeschlossen:** Bot-Review(s) vorhanden und im PR-Body triagiert (umgesetzt oder begründet abgelehnt). Trifft NACH dem letzten Push ein neues Bot-Review ein, wird es erst triagiert (receiving-code-review: echter Bug / Stilfrage / False Positive), dann gemerged.
- **G3 Kein menschliches Veto offen:** Reviews von KZW/chsteiner mit Änderungswunsch blockieren. Abgrenzung beachten: menschliche Freigaben, die das ISSUE betreffen (z. B. Alans Text-Freigabe für #86, KZWs Freigabe des Rektoratsberichts VOR VERSAND), blockieren den Repo-Merge NICHT — der PR merged Entwürfe/Teilarbeit ins Repo, das Issue bleibt offen.
- **G4 Mergeability:** GitHub meldet keinen Konflikt. Bei Konflikt: Branch auf main rebasen, Konflikt lösen, npm test (bei Code), push, CI abwarten.
- **G5 Stack-Reihenfolge:** Ein gestackter PR wird nie vor seiner Basis gemerged.

## Verfahren

### Phase 0: Vorflug
1. `gh pr list` + pro PR: Checks, neue Kommentare seit letzter Triage, Mergeability, Base.
2. Merge-Reihenfolge festlegen: erst Stack-Ketten (Basis zuerst), dann Unabhängige, **Doku-/Meta-PRs zuletzt** (deren Inhalt — ROADMAP „Now", Matrix-Verweise — veraltet durch die Merges selbst; vor dem Merge per Folge-Commit auf den Endzustand bringen).
3. Bekannte Datei-Überschneidungen zwischen Ketten notieren (Konflikt-Erwartung, siehe Anhang).

### Phase 1: Merge-Schleife (pro PR)
1. Gates G1–G5 prüfen.
2. `gh pr merge <nr> --merge --delete-branch` (Repo-Konvention: Merge-Commit, kein Squash — erhält die Folge-Commit-Historie der Review-Triage). GitHub retargetet abhängige Stack-PRs beim Löschen des Base-Branches automatisch auf main.
3. CI auf main abwarten (v. a. `data-integrity.yml` bei Daten-PRs). Rot → STOPP: diagnostizieren, fixen oder Session dokumentiert abbrechen; NIE „einfach weitermergen".
4. Beim nächsten PR der Kette: Checks laufen nach Retarget neu an — abwarten (G1).

### Phase 2: Nach jeder Kette (Live-Verifikation)
1. GitHub-Pages-Deploy abwarten (Actions).
2. Chrome-Smoke auf der Live-URL — **Hard-Reload** (http-Cache!) und bei Index-Bumps den IndexedDB-Cache-Bust verifizieren (Konsole: neue Version geladen).
3. Kern-Flows je nach Kette (siehe Anhang).

### Phase 3: Abschluss
1. Verifizieren, dass alle Closes-Issues wirklich zu sind; Part-of-Issues offen geblieben.
2. **KZW-UI-Pings** für live gegangene UI-Features (Projektkonvention: @wachauer mit Live-URL + Test-Hinweisen; Issues offen lassen bis ihr OK — nur wo das Kommentar-Budget des Issues es erlaubt).
3. #44-Matrix aktualisieren: Bucket „PR offen" auflösen → Recently Completed; Quick Stats neu.
4. ROADMAP „Now" nachziehen; JOURNAL-Eintrag (Merges, CI-/Deploy-Vorkommnisse, Lehren).
5. Abschlussreport als Nachtrag im bestehenden #44-Session-Kommentar (Edit, kein neuer Kommentar).
6. Lokale Branches aufräumen (`git fetch --prune`; gemergte claude/*-Branches lokal löschen).

## Fehlerbilder und Reaktionen

| Situation | Reaktion |
|---|---|
| CI rot nach Retarget | Ursache prüfen; Freshness-Gate rot nach Daten-Merge = wahrscheinlich Rebuild-Drift → Indexe auf dem PR-Branch neu bauen, committen |
| Merge-Konflikt Kette B nach Kette-A-Merge | Erwartbar nur in geteilten Doku-Dateien (CONTRACTS/INDEX/TEI-MODEL, disjunkte Hunks) — rebase, lösen, npm test, push |
| Neues Bot-Review mit echtem Bug kurz vor Merge | Fix als Folge-Commit + npm test + Triage-Nachtrag; erst dann mergen |
| Playwright-Report-Server hält npm test offen | Prozess auf Port 9323 killen, Ergebnis steht in der Task-Ausgabe |
| GitHub-API 5xx | Retry; bei anhaltend: dokumentieren, nächster PR |

## Anhang: PR-Bestand für die erste Merge-Session (Stand 08.07.2026)

**Reihenfolge:**
1. **Kette A:** #174 → #175 → #178 → #184
2. **Kette B:** #177 → #183 (retargeten nach #174-Merge automatisch)
3. **Unabhängig:** #176, #179, #180, #181, #182, #185
4. **Zuletzt:** #186 (vorher ROADMAP/JOURNAL per Folge-Commit auf Nach-Merge-Stand bringen)

**Bekannte Überschneidungen (erwartet konfliktfrei, da disjunkte Hunks):** CONTRACTS.md (§B in Kette A / §G.3 in Kette B), docs/INDEX.md (#177-Versionszeile / #180+#181-Zeilen), TEI-MODEL.md (§2.1 in #178 / §11 in #177), cooccurrence-ranking.spec.js (#174-Basis in beiden Ketten identisch).

**Smoke-Checks:** Nach Kette A: Reader ABG (Prosa-Zeilennummern numerisch, kein leerer Span), AK-Excerpt-Banner, Multi-Lemma rôt+munt (Treffer > 0). Nach Kette B: Kookkurrenz `salve` (Badges „NOM VRB", POS-Filter vrb findet salve), Authority-Cache-Bust auf v1.6.0. Nach #176: Korpussuche-Tabelle Sortierung + TSV-Export. Nach #179: hilfe-daten-beitragen Sektion 9 + barrierefreiheit-Kontaktblock.

**Nach-Merge-Pings (Phase 3):** #134-Banner ist KZW-relevant (via #44 oder Merge-Notiz, Kommentar-Budget beachten); #86 wartet weiter auf Alan (kein Ping — extern); #187 (posAll-Anzeige-Migration) wird durch #177-Merge startbar.

**Erwartete Issue-Schließungen:** #163 #164 #159 #168 #158 #162 #160 #161 #134 #145 #27 #167 #170. Offen bleiben: #68 #86 #28 #171 (Part of) + #44 (Evergreen).
