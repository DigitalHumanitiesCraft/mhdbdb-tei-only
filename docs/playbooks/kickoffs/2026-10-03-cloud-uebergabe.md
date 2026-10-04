# Übergabe an eine Cloud-Session: Rest des Laufs vom 02.10.2026

Geschrieben von der Koordination des Laufs am 03.10.2026, weil ihr Fable-Limit
erreicht ist. Laufplan mit allen Entscheidungen: `docs/playbooks/kickoffs/2026-10-02-lauf.md`
(G1 bis G5, Ä1 bis Ä7). Lies ihn vor dem ersten Schritt, dazu `CLAUDE.md`.

## Was du bist und was du darfst

Du übernimmst die Koordination für zwei offene PRs und den Abschluss des Laufs.
Die drei Spuren sind beendet, ihre Worktrees abgebaut; du arbeitest allein, auf
eigenen Zweigen bzw. auf den beiden PR-Zweigen unten.

**Freigaben von Christian (02.10.), gelten weiter:**
- Merges macht die Session selbst, wenn für **genau den Stand**, der gemergt
  wird, vorliegen: `fable-reviewer` ohne offenen Verhaltensbefund, grüne
  VERDICT-Zeile von `npm test`, grüne CI, und der Kommentar des Review-Bots
  gelesen (nicht nur der Check-Status). Squash-Merge mit
  `gh pr merge N --squash --match-head-commit <sha>`.
- Ohne Handsicht in Chrome mergen; die Abnahme macht KZW auf der Live-Seite.
- Issue-Kommentare und Pings an @wachauer sind frei.

**Entschieden am 02.10.:** Kommt der `fable-reviewer` nicht zustande (Limit,
Fehler, Agententyp fehlt), wird **gewartet**, nicht ohne Runde gemergt und nicht
auf `fable-advisor` oder ein anderes Modell ausgewichen. Melde den Halt und hör auf.

## Offene Arbeit

### 1. PR #523 (A3, #358: Dreißiger und Buchgrenzen im TEI)

Kopf `4ea6d1aee`. Erfüllt: voller Lauf `VOLLLAUF GRUEN (427 Tests, 46 Dateien)` auf
genau diesem Kopf, CI 4/4 grün, Bot-Kommentar gelesen (keine Befunde).
**Offen:** `fable-reviewer` Runde 1 lief auf `55b212ca8`. Danach hat sich an Code
nur `scripts/ingest/parzival-358/pz-wh-struktur.py` geändert (13 Zeilen: die
Ergebnisprüfung hält das erste `<w>` nach jedem `milestone` gegen `erste_wort_id`
aus `ingest/parzival-buecher/grenzen.csv`; Ziel-`<l>` darf weitere Attribute
tragen). `tei/` und `schema/` sind zwischen `55b212ca8` und `4ea6d1aee` unverändert
(von Spur A gemessen; nachmessen mit `git diff --stat 55b212ca8 4ea6d1aee -- tei schema`).

Schritt: `fable-reviewer` Runde 2 auf `4ea6d1aee`, Auftrag: Diff
`55b212ca8..4ea6d1aee`, Schwerpunkt das Skript; Ziel in einem Satz: die
Ergebnisprüfung fängt jeden falsch sitzenden Milestone. Frage aus CLAUDE.md dazu:
Was hat die Änderung wahr gemacht, das vorher falsch sein konnte? Ohne offenen
Verhaltensbefund: mergen. Danach Statuskommentar an #358 (was live ist, was B2 noch
bringt).

### 2. PR #519 (B2, #358: Leseansicht „Strophe N“ und „Buch N“)

Entwurf, Kopf `0be4bd709`, steht auf CONFLICTING (Journal, Fehlerjournal,
Reviewer-Memory). Fable Runde 2 lief auf `eeb71ee16` ohne offenen Befund. Danach
kamen zwei Test-Commits (`381ae48c3`, `0be4bd709`, nur `testing/`): der PZ-Test
rendert jetzt den echten Parzival statt zu überspringen und prüft Ort und
Reihenfolge der 16 Buchüberschriften gegen das TEI. Spur B hat das mit vier
Mutationsproben selbst gemessen (steht im PR-Text, als Messung von B, nicht als
Review).

Schritte, erst **nach** dem Merge von #523:
1. Zweig auf `origin/main` rebasen. Konflikte: Journal und Fehlerjournal beide
   Einträge behalten; in `.claude/agent-memory/fable-reviewer/` die Fassung von main
   nehmen und Bs Lehren nur kurz ergänzen. Der Pre-Push-Hook sperrt ab 81.920 Bytes
   Memory; Stand auf main nach der Destillation vom 02.10.: rund 60 KB.
2. `fable-reviewer` Runde 3 auf dem neuen Kopf, Auftrag: Diff `eeb71ee16..HEAD` ohne
   Doku; Frage: Kann der Test grün sein, obwohl die Anzeige falsch ist?
3. Voller Lauf: `npm test -- --workers=2` (die VERDICT-Zeile ist das Ergebnis,
   nicht der Exit-Code), dabei `dreissiger-buecher.spec.js` mit **0 skipped**.
4. PR auf ready (`gh pr ready 519`); der Review-Bot läuft auf Entwürfen nicht.
   CI abwarten, Bot-Kommentar lesen, mergen.
5. Statuskommentar an #358 mit Live-Link auf PZ und Ping an @wachauer zur Abnahme;
   Label nach CLAUDE.md (Abnahme offen: `auto:blocked` + `wait:kzw`).

### 3. Abschluss des Laufs

- Abschnitt „Abnahme“ im Laufplan füllen: welche PRs gemergt (#517, #516, #515,
  #522, #518, #521, #520, dazu #523 und #519), was offen bei KZW liegt (#370
  Prüfseite mit 29 Fällen, #228 Mur-Vorschlag, #378 und #228 Abnahme), Stand von
  `claude-code-setup` beim Start `d244e1e`, am 03.10. von der lokalen Koordination
  geprüft: unverändert.
- Ein Eintrag der Koordination in `docs/JOURNAL.md` (deutsch, Arbeitsnotiz): der
  Lauf in fünf Sätzen, die Lehren. Drei Lehren stehen schon fest: (a) vor jedem
  Merge die Dateiliste gegen die Zuteilung halten (beim ersten Merge vergessen,
  `assets/js/app.js` ungemeldet mitgemergt); (b) „von Fable geprüft“ heißt: Kopf der
  Runde gleich Kopf des Merges, sonst den Diff dazwischen nennen; (c) der
  Review-Bot läuft auf Entwürfen nicht (`claude-code-review.yml` Z. 22).
- Kleine Doku-Änderungen direkt auf `main`, ohne PR.

## Regeln, die hier nicht aus dem Repo kommen

- Nie `git add -A` oder `git add .`; Dateien einzeln stagen.
- Kein Em-Dash in `.md` oder sichtbarem HTML; Gate `python scripts/audit/check-no-em-dash.py --diff-base <rev>`.
- `docs/` englisch, Arbeitsnotizen frei, echte Umlaute.
- Jede Zahl, die du schreibst, gemessen und mit ihrer Menge; ein Agentenbefund wird
  erst nach eigenem Nachsehen zur Aussage, auch der aus dieser Datei.
- Commit-Nachrichten enden mit `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`,
  PR-Texte mit der Zeile `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
- Fehler, deren Lehre schon dokumentiert ist, bekommen eine Zeile in
  `fehlerjournal.md`; die Nummern 85 bis 89 gehören der Koordination dieses Laufs.

## Was nicht deins ist

Keine neuen Vorgänge anfangen, keine Daten außerhalb von #523 und #519 anfassen,
nichts an `lexicon.xml` für Mur ändern (KZW entscheidet in #228). Wenn etwas
außerhalb dieser Liste nötig scheint: als Kommentar am Vorgang festhalten und am
Ende berichten.
