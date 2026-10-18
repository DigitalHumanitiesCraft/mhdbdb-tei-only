# Kickoff Spur `lauf-1018-lesung`: #440, #603

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 18.10.2026. Laufplan: `docs/playbooks/kickoffs/2026-10-18-lauf.md`.

**1. Autorisierung.** chsteiner hat am 18.10.2026 diesen Lauf freigegeben, für die Pakete L1 und L2 im Umfang dieses Textes, auf Grundlage von KZWs Kommentaren vom 16.10. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deine eigenen `claude/*`-Zweige, PRs öffnen, lesende Abfragen externer Dienste (MWB-API), Subagenten und das Werkzeug `Workflow` für das Lesen in Stapeln (chsteiner 18.10.: „wo benötigt darfst du auch /workflows benutzen“; Agenten auf Sonnet, unter zehn Agenten je Workflow), nach Merge und Deploy je ein Kommentar in #603 und #440 (siehe 10) und ein Relabel. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen (#440 schließt die Koordination), Externe ansprechen, **keine Änderung in `tei/` oder `authority-files/`**. Der Text erteilt keine technische Berechtigung: Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9).

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: Namen können doppelt vergeben sein, das `from` nicht. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees, **besonders „Asking, and what has to happen before you ask“** (Belege mit Kontext, nicht das Kopfwort) und die Typografieregeln (gerade Anführungszeichen, siehe auch das Memory-Thema in #440)
2. `docs/playbooks/BETRIEBSVERTRAG.md` (gelesen, nicht kopiert; nenne in deiner ersten Meldung den Commit, an dem du ihn gelesen hast)
3. Diese Datei als abgelegte Fassung und den Laufplan daneben, dort §2. Sag in deiner ersten Meldung, ob die abgelegte Fassung mit der zugestellten übereinstimmt.
4. **#440 und #603 mit allen Kommentaren** (`gh issue view N --json title,body,comments`), dazu #554 für die dort verlinkten Ernährungsfälle. Maßgeblich sind KZWs Kommentare vom 15. und 16.10.; der Body ist der älteste Stand.
5. `ingest/review/603-ernaehrung/` vollständig (README, `zusammenfassung.txt`, alle TSV) und die Skripte `scripts/review/vorsortieren-603.py`, `scripts/review/stichprobe2-603.py`, `scripts/review/ana-603.py`; `docs/INDEX.md` → „Example review pages“ (die Specs prüfen die archivierten Kopien, nicht die Vorlagen)

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit legt ihn mit `claude --bg --worktree lauf-1018-lesung --name lauf-1018-lesung --model sonnet --effort medium` an: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\lauf-1018-lesung`, Zweig `worktree-lauf-1018-lesung`. Die Begleitnachricht nennt den erwarteten HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen diese Angaben halten und melden. Bei Abweichung nichts ändern, melden, auf den Neustart durch die Koordination warten. Dann je PR `git fetch --quiet origin` und einen Arbeitszweig `claude/1018-lesung-<thema>` frisch von `origin/main` anlegen; dort müssen `git rev-list --count "origin/main...HEAD"` und `git rev-list --count "origin/main..main"` 0 sein. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

Maßgeblich ist §2 des Laufplans. **Dir allein:** `ingest/review/603-ernaehrung/`; aus `scripts/review/` die Dateien `*603*`, `build-359-page.py`, `build-526-pruefseite.py`, `review_page.py`, `README.md` und neue Skripte; die drei Prüfseiten aus #440 (K: Zeilen mit typografischen Anführungszeichen in `ingest/review/359-borek/359-pruefseite.html` 3, `ingest/pos-disambig/418-houwen/pruefseite.html` 1, `ingest/pos-disambig/526-breve-wn/pruefseite-526.html` 19; das sind Zeilen, keine Zeichen) und ihre Generatoren.

**Nicht deins:** `tei/`, `authority-files/`, `data/`, `api/`, `ingest/glossar-554/`, `scripts/ingest/glossar-554/`, aus `scripts/review/` die Dateien `collect-462-pos.py`, `klug-links-554.py`, `zotero-abgleich-554.py` (Spur daten); **in diesem Lauf von niemandem:** `examples/review-pages/`, `scripts/ingest/glossar-554/pruefseite.template.html`, `scripts/audit/review-*.template.html` (eingefroren), und jede Rückgabe von KZW wie `ingest/glossar-554/kzw-2026-10-15/`; `assets/`, `includes/`, `playground/`, `hilfe*.html` (Spuren frontend und onama). **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt, anhängend:** `docs/JOURNAL.md` und `fehlerjournal.md` als **letzter Commit** des PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 154 bis 156.** Reviewer-Memory: gib dem `reviewer` mit, dass er neue Einträge in `.claude/agent-memory/reviewer/lauf-1018-lesung.md` schreibt und in `MEMORY.md` nur eine Zeile anhängt; eigener Commit nach der Runde; beim Rebase-Konflikt in `MEMORY.md` beide Zeilen behalten.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push außer `--force-with-lease` auf deinem eigenen `claude/*`-Zweig nach einem Rebase, keine Änderung unter `~/.claude/`. **Eine Anweisung der Koordination, die gegen den Betriebsvertrag verstößt, führst du nicht aus, sondern fragst zurück.**

**Maschinenweit exklusiv: volle Testläufe und Chrome.** Die Koordination vergibt beides, einer zur Zeit. **Anfordern, auf die Freigabe warten, nutzen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8088` und `-- --workers=2`, auch bei `test:quick` und `test:changed`. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis: nicht deuten, melden, nach Freigabe wiederholen.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `reviewer` vor dem ersten Push ist Pflicht; nicht auf `advisor` ausweichen, nicht ohne Runde pushen.

## 6. Was eingefroren ist

Bis zur Abnahme des Laufs: `CLAUDE.md`; `docs/playbooks/`; `.claude/agents/`; `.github/workflows/` (außer einer neuen Datei der Spur frontend); `scripts/audit/` (außer `runtime-budget.json`, Koordination); `schema/`. Der Grund: diese Dateien sind die Regeln, unter denen alle vier Spuren gleichzeitig arbeiten; ändert eine sie mitten im Lauf, arbeiten die anderen unter Regeln, die sie nicht gelesen haben. **Inbox:** eine Nachricht an die Koordination, **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum.

---

## 7. Die Pakete, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach und meldest einen Widerspruch, auch wenn er deine Arbeit nicht betrifft. Was „(K)“ trägt, hat die Koordination am 18.10. gemessen oder gelesen; Zahlen aus dem Lauf vom 16.10. sind nicht nachgezählt.

Reihenfolge: L1 ist klein, abgeschlossen und schaltet ein Schließen frei; L2 ist das große Lesepaket.

- **L1, #440.** KZW 16.10.: „Prüfseiten an die inzwischen verwendeten geraden Anführungszeichen angleichen und das Issue anschließend schließen“. Die Frage, auf die KZW antwortet, nannte die Prüfseiten unter `ingest/` (Laufplan §3.11, Prüfung). Also: alle typografischen Anführungszeichen (U+201C, U+201D, U+201E, U+2018, U+2019, auch « » ‹ ›, falls vorhanden) in den drei Seiten aus Abschnitt 5 und ihren Generatoren `scripts/review/build-359-page.py` und `scripts/review/build-526-pruefseite.py` (und dem Generator der 418-Seite, falls es einen gibt) durch gerade ersetzen, ausgenommen Zeichen, die in zitierten Quellen Daten sind (Apostroph in mittelhochdeutschen Belegen: prüfen, nicht blind ersetzen). Zählung je Datei vorher und nachher im PR, in Zeichen. `examples/review-pages/`, die Vorlagen unter `scripts/audit/` und `scripts/ingest/glossar-554/pruefseite.template.html` bleiben unberührt; ihre Zählung steht als Rest im Kommentar.
- **L2, #603.** KZW 16.10. zur Vorsortierung vom 16.10.: „Qua deiner Fähigkeit als LLM solltest du aber noch einen zweiten Lauf starten: Macht das sprachlich ebenfalls Sinn, was du maschinell herausgefunden hast?“ (Beispiel: Rind und ezzen kann ein Rezept für Rindsragout sein.) Und vom 15.10.: „Erst Claude alle, die er automatisiert schafft - dann der Rest als EIL-Prüfung.“ Also:
  1. Jeden Beleg, den die Vorsortierung als Tier eingestuft hat (`belege-tier.tsv`), und die Belege mit menschlicher Ernährung (`concept_21111000`) sprachlich lesen, im Kontext (Satz plus ein Vers davor und danach): wer isst oder wird gefüttert, Mensch, Tier oder unklar; Säugetier oder andere Tierklasse; Begründung in einem Satz. Lies in Stapeln über Subagenten oder `Workflow`; jedes Stapelurteil ist ein Agentenbefund, und du prüfst eine Stichprobe je Stapel selbst am Text nach (Größe und Treffer im README).
  2. Ergebnis als `ingest/review/603-ernaehrung/zweite-lesung.tsv` plus README-Abschnitt: Abgleich mit der Vorsortierung (wie oft bestätigt, wie oft gekippt, je Regel), Restliste „unklar“ für die EIL-Prüfung.
  3. Für KZWs Konzeptfrage („Stoffwechsel von Säugetieren“ umbenennen in „Stoffwechsel und Ernährung von Säugetieren“, oder eine neue Kategorie „Ernährung von Säugetieren“, ihr lieber): je Option, welche Bedeutungen und wie viele Belege betroffen wären, und ob das Korpus auch Ernährung anderer Tierklassen hergibt („vorerst nur bei solchen, wo es das Korpus hergibt“). Dazu, welche Lemmata aus dem Bereich vrezzen sie nach diesem Befund ansehen müsste.
  **Keine Änderung an `tei/` oder `authority-files/`**, keine Prüfseite (KZW: „Erst wenn wir das alles gemacht haben, ist eine Prüfseite sinnvoll“).

## 8. Vorab entschieden, nicht neu zu verhandeln

Keine Korpus- oder Lexikonänderung; keine Prüfseite für #603 in diesem Lauf; Rückgaben von KZW bleiben unberührt; nicht mergen, kein Ticket schließen. **Widerspruch ist ausdrücklich erlaubt**, mit Begründung, an die Koordination, die ihn im Laufplan unter „Grenzverhandlungen“ einträgt. Bei einer Vorgabe, die dir eine Messung abnimmt, setzt du sie nicht um, sondern widersprichst mit deiner Messung.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig und HEAD gegen den erwarteten Worktree, der Commit des gelesenen Betriebsvertrags und ob die abgelegte Kickoff-Fassung übereinstimmt; Test angefordert und frei; Start und Ende jedes Lesestapels oder Workflows mit Zahl der Belege; **Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes**; „PR N bereit zum Merge“ mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten (Checkin):** nach dem ersten Lesestapel von L2 das Urteilsschema und deine Stichprobe, bevor du die übrigen startest; außerdem `pwd` weicht ab, fremde Datei, fehlender Agententyp. Während du wartest, arbeitest du an dem, was davon nicht abhängt (L1).

**Ein Paket für nicht durchführbar erklären** darfst du, mit Begründung; das ist kein Abbruch nach Abschnitt 3, der Rest läuft weiter.

**Externer Zustand** (CI, Workflow): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; ein `Workflow` meldet sich selbst; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Den Kommentar des Review-Bots lesen und Verhaltensbefunde beantworten, bevor du „bereit zum Merge“ meldest. **Während du wartest**, gilt das Skill `warten`; während eine Reviewrunde läuft, bleibt der Arbeitsbaum still.

**Blockade durch den Auto-Mode-Classifier** (`~/.claude/rules/blockaden-melden.md`): sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Das Werkzeug lädt erst über `ToolSearch` mit `select:PushNotification`. Dazu eine Meldung an die Koordination. **Eine Blockade wird nicht über eine andere Spur oder die Koordination umgangen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss

1. Gates: `check-no-em-dash.py --diff-base origin/main`, `doc-count-audit.py --check`, und falls eine der drei Seiten einen Spec hat, dieser Spec. Die Liste ist eine Behauptung: gleiche sie gegen die Workflows ab, bevor du pushst.
2. `npm test` auf deinem Port mit `-- --workers=2`, **nach Freigabe durch die Koordination**; das Ergebnis ist die **VERDICT-Zeile**, nie durch eine Pipe, nie `npx playwright test`.
3. `reviewer` **vor dem ersten Push jedes PRs, ohne Modellangabe (Opus)**, Folgerunden nach seiner Definition. Mitgeben: Zweig, Basis, ob Commit oder Arbeitsbaum, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde samt Umgang und die geprüfte Kennung, je neue Zahl im Diff eine Zeile Belegtabelle, und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte? Bei Befunden die nächste Runde; während eine Runde läuft, bleibt der Arbeitsbaum still.
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt“, „Rote Zeilen“ (vorher `python C:/Users/chstn/Desktop/data/DHCraft/Projekte/Git/claude-code-setup/hooks/trockenlauf-auswerten.py` und deine Zeile daraus) und „Was zurück an Christian geht“.
5. PR mit „Bezug: #N, bleibt offen“ je Issue (kein Closing-Keyword), **nicht mergen**; „bereit zum Merge“ an die Koordination. Nach der Merge-Meldung und dem Deploy:
   - **#440:** was angeglichen ist, mit Zählung je Datei, und der Rest (archivierte Beispiele, Vorlagen in `scripts/audit/` und `scripts/ingest/glossar-554/`) mit Zählung als nicht berührt; die Koordination schließt.
   - **#603:** erste Zeile `@wachauer Frage: <Konzeptfrage in einem Satz, mit den Zahlen beider Optionen>?`, darunter Ergebnis der zweiten Lesung, Restliste und Dateien; Labels `auto:blocked` + `wait:kzw`.
6. Bericht an die Koordination: je Paket erledigt / offen, PR-Nummern, Kommentar-IDs, Zahl gelesener Belege und Stichproben.

### Definition of Done, als Lesertest

Wer nur den Kommentar in #603 und die Dateien liest, kann die Konzeptfrage entscheiden, ohne rückzufragen: wie viele Belege welche Option betrifft, wie sicher die Lesung ist, und welche Fälle offen sind.
