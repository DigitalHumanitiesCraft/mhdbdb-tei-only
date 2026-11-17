# Kickoff Nachtsession `nacht-147-bre`: Weingrüße, Stufe 0 und Phase 1 bis 3 in `ingest/bre/` (#147)

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden. Der Wortlaut gilt für den Lauf in der Nacht vom 17. auf den 18.11.2026. Im zugestellten Prompt folgt auf diesen Text der vollständige `docs/playbooks/BETRIEBSVERTRAG.md` am Stand `1adf937cd`.

## 1. Autorisierung

chsteiner hat am 17.11.2026 in der Session am Terminal entschieden: „Stufe 0 + Phase 1–3“ für #147, als Nachtsession ohne ihn. Den Umfang hatte er davor so bestätigt: die 18 Zeugen ohne offene Frage nach `ingest/bre/` schreiben und Phase 1 bis 3 maschinell durchführen (Auto-Match, LLM-Disambiguierung, POS, Senses), mit Prüftabellen für Julia und KZW. Der PR wird gemergt, die Druckfahnen dienen nur lokal als Kontext, und nichts daraus kommt ins Repo.

**Dieser Text ist die Autorisierung.** Erlaubt sind:
- Commits und Pushes auf deinen eigenen `claude/*`-Branch,
- ein PR,
- **der Squash-Merge dieses einen PR**, sobald alles nach `CLAUDE.md` → Git Rules gelaufen ist: Gates, `npm test` mit grüner VERDICT-Zeile, `reviewer` ohne offenen Befund, CI grün und Bot-Kommentar gelesen. Das ist die ausdrückliche Merge-Freigabe, die Regel 1 des Betriebsvertrags verlangt.
- In #147 höchstens ein Statuskommentar nach dem Merge und ein Relabel (Abschnitt 8).

**Nicht erlaubt:**
- Push direkt auf `main`, Force-Push auf `main`,
- Tickets schließen,
- Externe ansprechen (Silvan, Alan und andere),
- Änderungen in `tei/`, `authority-files/`, `data/`, `api/` oder `schema/`.

Dieser Text erteilt keine technische Berechtigung. Was der Auto-Mode-Classifier oder die Deny-Liste ablehnt, bleibt abgelehnt. Bei einer solchen Blockade sofort eine `PushNotification` senden (laden mit `ToolSearch` `select:PushNotification`), mit dem, was blockiert wurde, und woran es hängt. Dann weiter mit dem, was nicht daran hängt. Nie über einen anderen Weg umgehen.

## 2. Lies das, bevor du etwas änderst

1. `CLAUDE.md` in der Root deines Worktrees.
2. Den Betriebsvertrag unten im Prompt.
3. **#147 mit allen Kommentaren** (`gh issue view 147 --repo DigitalHumanitiesCraft/mhdbdb-tei-only --json title,body,comments`). Maßgeblich sind die Kommentare ab dem 03.11.: Schema-Weg 1 umgesetzt, Hauptseite als Grundlage der Werkzuordnung (wachauer 12.11.), Umsetzung in #704 (chsteiner 13.11.), Frage zu Werk, Gattung und Autor an KZW (chsteiner 17.11., offen).
4. `scripts/ingest/bre/README.md` ganz, dazu `bre_common.py` und `test_bre.py`.
5. `docs/DATA-MODEL.md` → Ingest procedure (Phase 1 bis 3, assign → resolve → apply, TSV-Spalten, `decision_type`, Prüfquote) und Data-Change-Lifecycle.
6. Die WZB-Skripte unter `scripts/ingest/wzb/` als kanonische Vorbilder: `wzb-auto-match.py`, `wzb-generate-tsv.py`, `wzb-split-tsv.py`, `wzb-bulk-resolve.py`, `wzb-apply-lemmarefs.py`, `wzb-extract-unmatched.py`, `wzb-pos-assign.py`, `wzb-pos-apply.py`, `wzb-sense-assign.py`, `wzb-sense-apply.py`, `wzb-corresp-apply.py`. Erst lesen, dann wiederverwenden oder nach `scripts/ingest/bre/` übertragen, nicht neu erfinden.
7. `docs/POS-TAGSET.md` (19 Tags) und `scripts/mhg_normalizer.py`.

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Das gehört in den Abschlussbericht.

## 3. Worktree und Start

Gestartet mit `claude --bg --worktree nacht-147-bre --name nacht-147-bre --model opus --effort high`. Erwarteter HEAD: der Commit, der diese Datei anlegt („Kickoff Nachtsession #147“), direkt auf `1adf937cd`.

**Erste Handlung:**
- `git rev-parse --short HEAD` und `git branch --show-current` messen.
- `git fetch --quiet origin`, dann den Arbeitsbranch `claude/147-bre-phasen` frisch von `origin/main` anlegen. Dort müssen `git rev-list --count "origin/main...HEAD"` und `git rev-list --count "origin/main..main"` 0 sein.
- `npm ci` vor dem ersten Test.
- Dev-Server und `npm test` nutzen Port 8080. Kein anderer Lauf belegt ihn heute Nacht.

## 4. Umfang

**Zeugen: 18 von 21.** Alle außer **B2, d4 und d6**: dort wartet die Segmentierung auf Silvans Antwort (Kommentar 13.11., `ingest/bre/hauptseite-abgleich.tsv` „offen“). Diese drei werden weder geschrieben noch annotiert. Der Bericht nennt sie.

**D (Mscr. M 50): nur Teil A.** Teil B (Bl. 217r–221v, `<div n="B">`) stammt laut Druckfahnen aus dem 17. Jahrhundert und liegt außerhalb des Korpusumfangs „vor 1600“ (wachauer 10.09., #263, `docs/RESEARCH.md`). `02-convert-wiki-to-mhdbdb.py` konvertiert D heute vollständig. Schließ Teil B im Skript aus, mit Begründung im Code und im README und mit einem Test.

**Stufe 0:** die 18 Zeugen als `ingest/bre/BRE_<…>.tei.xml` schreiben. Siglen, Revisionen und Segmentierung wie im README. Validierung gegen `schema/mhdbdb.rng` mit 0 Fehlern je Datei. Der Header behält `work_TBD`, `genre_TBD` und Sprachstufe `TBD`: Das ist offen bei KZW (Frage vom 17.11. in #147, Sprachstufe #118). Erfinde dort nichts.

**Strukturbereinigung (#66):** Rubriken und Reihentitel sind Text, aber nicht lexikalisch. Behandle sie nach der Tabelle in `docs/DATA-MODEL.md` → Structural cleanup, und halte die Regel im README fest.

**Phase 1, Lemmatisierung:**
- 1a Auto-Match gegen `variants.xml` mit Normalisierung auf beiden Seiten.
- 1b Disambiguierung der mehrdeutigen Formen nach den Stufen in DATA-MODEL. Bulk für häufige Formen, Patch je `xml_id` für Minderheitslesarten, Hapaxe und den unaufgelösten Rest bewusst stehen lassen.
- Unaufgelöste echte Wörter als frequenzsortierte Liste für das Lexikonteam (Vorbild `wzb-extract-unmatched.py`).
- **Keine neuen Lemmata, keine neuen Senses, keine Änderung an `lexicon.xml`.** Neue Lemmata entstehen nur durch eine redaktionelle Entscheidung. Damit entfällt der Backfill.
- Die Texte sind frühneuhochdeutsch, das Lexikon ist mittelhochdeutsch. Eine niedrige Abdeckung ist ein Befund, kein Fehler. Miss sie und berichte sie.

**Phase 2, POS:** Auto-Inherit aus `lexicon.xml`. Mehrdeutige Fälle als TSV, aufgelöst nach dem Kontext. Jeder Tag aus dem 19er-Set.

**Phase 3, Senses und `@corresp`:**
- Auto-Assign bei genau einem Sense, mehrere Senses als TSV mit Konzeptlabels.
- `abstain` ist eine gültige Entscheidung und wird nicht geschrieben.
- Nie `@ana` ohne `@lemmaRef`.
- `@corresp` nur bei genau einem Treffer.
- Zu `@corresp` bei `expan` steht ein Hinweis im Kommentar vom 08.11. in #147: Die aufgelöste Form ist nicht die Graphie der Handschrift. Entscheide, welche Form für den Variantenabgleich zählt, und vermerke die Entscheidung mit Begründung im README.

**LLM-Entscheidungen:**
- Jede Entscheidung trägt `decision_type`, `confidence` und `reviewer` (`llm:<modell>`), wie in DATA-MODEL.
- Ausführen lassen Sonnet-Subagenten (`model: sonnet`) in Batches von etwa 50 Zeilen. Du als Orchestrator prüfst eine Stichprobe je Batch an der Quelle und verwirfst Batches, die bei der Stichprobe nicht halten.
- Der Kontext der Disambiguierung: ±5 Wörter aus dem Zeugen, dazu die Einzeltextseite im Wiki.

**Druckfahnen:**
- Die Hirzel-Ausgabe (Text, Übersetzung, Kommentar) liegt nur lokal im Main Worktree: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\sources\weingruesse\wagner-2023-weingruesse-druckfahnen.pdf`, dazu `docling\` daneben. Nur lesen, nicht kopieren, nicht verschieben.
- Sie dürfen als Kontext für die Entscheidungen dienen.
- **Kein Wortlaut aus Text, Übersetzung oder Kommentar der Druckfassung im Repo**: nicht in einer TSV, nicht in einer Begründungsspalte, nicht in einem Kommentar, nicht in der Commit Message, nicht im PR-Body (wachauer 11.11.: „Keine Ausschnitte aus Text, Übersetzung oder Kommentar im öffentlichen Repository oder auf der Website“).
- Eine Begründung sagt höchstens „nach Übersetzung der Druckfassung“, ohne Zitat.
- Prüf das vor dem Push per Grep. Lässt sich der Prüfschritt mechanisch fassen, gehört er als Test in `test_bre.py`.

**Prüfpaket für Julia und KZW:**
- Alle Zeilen mit `confidence=low` und eine Zufallsstichprobe von etwa 20 % der `medium`-Zeilen, je Phase. Die Stichprobe wird mit festem Seed gezogen und ist reproduzierbar.
- Ablage: `ingest/bre/pruefung/` als TSV, plus ein README mit Anleitung ohne Fachsprache: welche Datei, welche Spalte, was „passt“ und „passt nicht“ bedeutet, wie zurückgemeldet wird.
- Eine HTML-Prüfseite nach dem Muster #443 (`docs/INDEX.md` → Example review pages) ist erwünscht, wenn Zeit bleibt. Dann mit Spec und `npm test`. Sonst die TSV und der Satz im Bericht, dass die Seite fehlt.

**Zahlen:** Jede Zahl im README, im PR-Body und im Kommentar steht neben ihrem Befehl oder Skript, das sie ausgibt. Die Menge gehört in dieselbe Zeile (Anteil mit Nenner, Summe aufgeschlüsselt). Abdeckung je Zeuge und gesamt, je Attribut.

## 5. Vorab getroffene Entscheidungen

- Ein Werk je Zeuge und die Siglen sind **Vorschläge**, bis KZW antwortet. Sie berühren nur den Header und `works.xml`, also nichts in diesem Lauf.
- Rosenplüt (`person_907`) wird in diesem Lauf nirgends eingetragen. Der Header bleibt bei `person_anonym`, wie heute.
- Die drei offenen Zeugen bleiben, wie sie sind. Kein Versuch, Silvans Antwort vorwegzunehmen.
- Gate: `reviewer` ohne Modellangabe (Opus), Runde 1 auf dem ganzen Diff. Folgerunden nach seiner Definition. Bei großen TSV-Dateien gib dem Reviewer die Skripte, das README, den Prüfskript-Output und eine Stichprobe, nicht jede Zeile.
- Teile den Lauf in Commits je Phase. Ein PR am Ende genügt.

## 6. Nicht anfassen

- **#141 Borte:** auf `auto:blocked` (Rechtefrage an KZW vom 17.11.).
- **#118 Sprachstufe:** bei KZW.
- Die Leseansicht (`tei-text-reader.js`): Die Auszeichnung im Wort sichtbar zu machen, ist ein eigener Schritt (Kommentar 08.11.) und nicht freigegeben.
- **Falle:** `ingest/bre/BRE_CGM713.tei.xml` existiert schon. Er wird neu erzeugt, nicht von Hand ergänzt.
- **Falle:** `02-convert-wiki-to-mhdbdb.py` bricht ab, sobald der Hauptseiten-Abgleich eine unerklärte Abweichung findet. Das ist Absicht. Ein Abbruch wird geklärt, nicht durch einen Eintrag in `ABWEICHUNG_ERKLAERT` zum Schweigen gebracht, außer die Abweichung ist an der Hauptseite belegt.

## 7. Journal

`docs/JOURNAL.md` anhängend als letzter Commit vor dem Merge, nach `git fetch origin`. Deine `fehlerjournal.md`-Nummern sind **165 bis 169**, Format wie die Zeilen davor.

## 8. Abschluss

- Nach dem Merge: `git -C <Main Worktree> merge --ff-only origin/main` im Main Worktree, aber nur wenn dessen Working Tree sauber ist. Sonst nicht anfassen und im Bericht vermerken.
- Ein Kommentar in #147. Erste Zeile: `@juliahin Abnahme: Passen die maschinellen Lemma-, Wortart- und Bedeutungszuweisungen in ingest/bre/pruefung/ zu den Weingrüßen?` Darunter: was geprüft werden soll und wie, die Abdeckung, die drei ausgelassenen Zeugen und dass für den Korpus noch KZWs Antwort vom 17.11. fehlt. `@wachauer` mitnennen. Semantische Disambiguierung darf nach `CLAUDE.md` an Julia gehen.
- Labels von #147: `auto:blocked`, `wait:julia`, `wait:kzw`.
- Worktree-Teardown nach Regel 30 des Issue-Playbooks.
- Ein Abschlussbericht als letzte Nachricht deiner Session: je Teil erledigt oder nicht, mit Beleg, was übersprungen ist und warum, PR- und Merge-SHA, offene Punkte.

Unbeschaffbarer Input führt zum dokumentierten Überspringen, nicht zum Warten und nicht zum Nachfragen.
