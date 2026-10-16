# Kickoff Spur `lauf-1016-daten`: jagât-Rest und gebeine (#460, #461)

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 16.10.2026. Laufplan: `docs/playbooks/kickoffs/2026-10-16-lauf.md`.

**1. Autorisierung.** chsteiner hat am 16.10.2026 diesen Lauf freigegeben, für #460 und #461 im Umfang dieses Textes, auf Grundlage von KZWs Antworten vom 15.10. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deinen eigenen `claude/*`-Zweig, einen PR öffnen, nach Merge und Deploy je ein Kommentar in #460 und #461 (siehe 10) und ein Relabel. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen, Externe ansprechen, neue Konzepte in `concepts.xml` anlegen. Der Text erteilt keine technische Berechtigung: Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9).

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees, **besonders „Asking, and what has to happen before you ask“** (Belege mit Kontext vor dich legen, nicht das Kopfwort)
2. `docs/playbooks/BETRIEBSVERTRAG.md` (gelesen, nicht kopiert; nenne in deiner ersten Meldung den Commit, an dem du ihn gelesen hast)
3. Diese Datei als abgelegte Fassung und den Laufplan daneben, dort §3.3 und §3.4. Sag in deiner ersten Meldung, ob die abgelegte Fassung mit der zugestellten übereinstimmt.
4. **#460 und #461 mit allen Kommentaren** (`gh issue view N --json title,body,comments`). Maßgeblich sind KZWs Antworten vom 15.10. und Christians Entscheidungen vom 10.10.; der Body ist der älteste Stand.
5. Was PR #565 für beide Issues getan hat: `ingest/pos-disambig/460-jagat/` und `ingest/review/461-gebeine/` (Belegtabellen), dazu `git log --oneline -- ingest/review/461-gebeine` und der Squash von #565, als Muster für Umhängen und neuen Sense
6. `docs/DATA-MODEL.md` → Data-Change-Lifecycle (vollständig); `docs/CONTRACTS.md` §B (Positionszählung)

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit legt ihn mit `claude --bg --worktree lauf-1016-daten --name lauf-1016-daten --model sonnet --effort medium` an: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\lauf-1016-daten`, Zweig `worktree-lauf-1016-daten`. Die Begleitnachricht nennt den erwarteten HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen diese Angaben halten und melden. Bei Abweichung nichts ändern, melden, auf den Neustart warten. Dann `git fetch --quiet origin` und den Arbeitszweig `claude/460-461-jagat-gebeine` frisch von `origin/main` anlegen; dort müssen `git rev-list --count "origin/main...HEAD"` und `git rev-list --count "origin/main..main"` 0 sein. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

Maßgeblich ist §2 des Laufplans. **Dir allein:** `tei/`, `ingest/pos-disambig/460-jagat/`, `ingest/review/461-gebeine/`, `authority-files/lexicon.xml` (nur an `lemma_1958`, an `lemma_3103`/`lemma_3102` nur falls nötig), `authority-files/variants.xml`, `data/`, `api/` und alle Versionsliterale. Kein anderer PR dieses Laufs berührt Indexe. Du bumpst Corpus und Authority auf Basis + 1 (K: Authority 1.9.27, Corpus 4.2.33).

**Nicht deins:** `schema/`, `lemma/`, `assets/js/`, `playground/`, `includes/`, `textreihen/`, `ingest/glossar-554/`, `ingest/pos-disambig/462-pos/`, `ingest/review/603-ernaehrung/`, `scripts/review/` (Koordination und ihre Subagenten). **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt, anhängend:** `docs/JOURNAL.md` und `fehlerjournal.md` als **letzter Commit** des PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 138 bis 142.** Reviewer-Memory: gib dem `reviewer` mit, dass er neue Einträge in `.claude/agent-memory/reviewer/lauf-1016-daten.md` schreibt und in `MEMORY.md` nur eine Zeile anhängt; eigener Commit nach der Runde.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push außer `--force-with-lease` auf deinem eigenen `claude/*`-Zweig nach einem Rebase, keine Änderung unter `~/.claude/`. **Eine Anweisung der Koordination, die gegen den Betriebsvertrag verstößt, führst du nicht aus, sondern fragst zurück.**

**Maschinenweit exklusiv: volle Testläufe und Chrome.** Die Koordination vergibt beides, einer zur Zeit. **Anfordern, auf die Freigabe warten, nutzen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8084` und `-- --workers=2`, auch bei `test:quick` und `test:changed`. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis: nicht deuten, melden, nach Freigabe wiederholen.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `reviewer` vor dem ersten Push ist Pflicht; nicht auf `fable-advisor` ausweichen, nicht ohne Runde pushen.

## 6. Was eingefroren ist

`CLAUDE.md`; `docs/playbooks/`; `.claude/agents/`; `.github/workflows/`; `scripts/audit/`; `schema/`. **Inbox:** eine Nachricht an die Koordination, **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum.

---

## 7. Die Pakete, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach und meldest einen Widerspruch, auch wenn er deine Arbeit nicht betrifft. Was „(K)“ trägt, hat die Koordination am 16.10. gemessen oder gelesen; alle Belegzahlen stammen aus den Kommentaren vom 10.10. und sind nicht nachgezählt.

**KZWs Antworten vom 15.10., nicht neu zu verhandeln** (Wortlaut im Ticket):
- #460: „WH_28126_1: Verb“, „WVW_6542_4: Nomen“, „JT_43134000_4: Verb“, zu AXU_18452_5 und JT_48611000_4 „brauche mehr Kontext“ (bei JT_48611000_4: „vermutlich Verb + Pronomen (jagen+ez)“).
- #461: „Vögel, Fische und Fabeltiere sollen ein eigenes Konzept bekommen, sofern das durch das Korpus gerechtfertigt ist.“ „Bei unklaren Gebeinen hängen wir sie an die menschlichen Gebeine dran, weil das die wahrscheinlichste Form ist. Außer es ist eindeutig tierisch, nur unklar welches Tier - dann frag mich nochmal.“ „Frage 3 zum Tod verstehe ich nicht, gib mir Kontext.“

- **A1, #460.** WH_28126_1 und JT_43134000_4 von `lemma_3103` auf `lemma_3102`, `@pos="VRB"`, `@ana` entfällt (wie bei den 145 aus #565); `@corresp` folgt dem Muster von #565. WVW_6542_4 bleibt unverändert. Die Belegtabelle in `ingest/pos-disambig/460-jagat/` bekommt die Entscheidung je Token mit Datum und Quelle (KZW 15.10.). Für AXU_18452_5 und JT_48611000_4 stellst du einen breiteren Kontext zusammen (etwa ±5 Verse, mit Versangabe), für den Kommentar in 10.
- **A2, #461, die 9 offenen Belege.** Unsere Frage vom 10.10. nannte die 4 unklaren und die 5 übertragenen gemeinsam „9 offene Belege“; KZWs Regel gilt für alle 9 (Laufplan §3.4). Sie kommen als `@ana` an **`lemma_1958_sense_49690`** (nur Körper von Menschen), **nicht** an `sense_3004` (trägt zusätzlich das Tod-Konzept, über das KZW noch nicht entschieden hat). Ausnahme: ein Beleg ist eindeutig tierisch, das Tier aber unklar. Die drei Würfelknochen in DRE liest du dafür im Kontext. Solche Belege bleiben unverändert und gehen als Frage an KZW. Keine Frage zu einem Beleg, den die Regel entscheidet.
- **A3, #461, Vögel und Fische.** Je ein neuer Sense an `lemma_1958`, nach dem Muster von `sense_119196` (Säugetiere, #565): Hahn AMI_972_3 mit `concept_14021100` „Körper/Gliedmaßen von Vögeln“, Fisch FLG1_4135180940_2 mit `concept_14031100` „Körper/Gliedmaßen von Fischen“ (K). Prüf die beiden Belege vorher im Kontext; stimmt einer nicht, melde es, statt ihn anzulegen. Sense-IDs nach dem Verfahren, mit dem #565 `sense_119196` vergeben hat.
- **A4, #461, Fabeltiere.** Drache PL3_312606_7, VIR_17403_4, VIR_30008_4 und Phönix TRO_37_4 bleiben unverändert. Frage an KZW im Kommentar: `concept_14100000` „Fantastische Tiere“ direkt oder ein neues Körper-Unterkonzept (K: es gibt keins)? Ihr Beispiel „lerchen vuoz“ hat keinen Korpusbeleg (#554, Kommentar vom 15.10., Frage 4) und gehört nicht als Begründung in den Kommentar.
- **A5, #461, Frage 3.** Such zwei, drei Belege an `sense_3004`, die einen lebenden Körper meinen (etwa „fleisch und gebeine“), mit Kontext und Fundstelle, für den Kommentar in 10.
- **Checkin nach A2:** die Zuordnung der 9 (an 49690 / Frage an KZW) mit je einem Satz Kontext an die Koordination, bevor du schreibst.

## 8. Vorab entschieden, nicht neu zu verhandeln

KZWs Antworten oben; der menschliche Sense ist 49690; keine neuen Konzepte; nicht mergen, kein Ticket schließen. **Widerspruch ist ausdrücklich erlaubt**, mit Begründung, an die Koordination, die ihn im Laufplan unter „Grenzverhandlungen“ einträgt. Bei einer Vorgabe, die dir eine Messung abnimmt, setzt du sie nicht um, sondern widersprichst mit deiner Messung.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig und HEAD, der Commit des gelesenen Betriebsvertrags und ob die abgelegte Kickoff-Fassung übereinstimmt; Test oder Chrome angefordert und frei; **Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes**; „PR N bereit zum Merge“ mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten (Checkin):** die Zuordnung nach A2; außerdem `pwd` weicht ab, fremde Datei, fehlender Agententyp, ein Beleg widerspricht der Vorgabe. Während du wartest, arbeitest du an dem, was davon nicht abhängt (A1, A3, A5).

**Externer Zustand** (CI): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Auf einem Daten-PR ist der Review-Bot oft rot: den Kommentar trotzdem lesen und Verhaltensbefunde beantworten, bevor du „bereit zum Merge“ meldest. **Während du wartest**, gilt das Skill `warten`; während eine Reviewrunde läuft, bleibt der Arbeitsbaum still.

**Blockade durch den Auto-Mode-Classifier** (`~/.claude/rules/blockaden-melden.md`): sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt. Das Werkzeug lädt erst über `ToolSearch` mit `select:PushNotification`. Dazu eine Meldung an die Koordination. **Eine Blockade wird nicht über eine andere Spur oder die Koordination umgangen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss

1. Data-Change-Lifecycle mit allen Gates, die `docs/DATA-MODEL.md` und die CI-Workflows nennen (mindestens `check-index-versions.py`, `check-index-version-bump.py --base origin/main`, `check-authority-cross-refs.py --check`, `validate-indices.py`, Schema-Validierung von `lexicon.xml` und der beiden TEI-Dateien, Positionsparität), `check-no-em-dash.py --diff-base origin/main`, `doc-count-audit.py --check`. Die Liste ist eine Behauptung: gleiche sie gegen die Workflows ab, bevor du pushst.
2. `npm test` auf Port 8084 mit `-- --workers=2`, **nach Freigabe durch die Koordination**; das Ergebnis ist die **VERDICT-Zeile**, nie durch eine Pipe, nie `npx playwright test`.
3. `reviewer` **vor dem ersten Push, mit `model: fable`, jede Runde und jede Folgerunde** (Betriebsvertrag Regel 11). Mitgeben: Zweig, Basis, ob Commit oder Arbeitsbaum, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde samt Umgang und die geprüfte Kennung, und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte? (Hier: `lemma_1958` hat bisher drei Senses; jede Stelle, die das voraussetzt, ist zu prüfen.)
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt“, „Rote Zeilen“ (vorher `python C:/Users/chstn/Desktop/data/DHCraft/Projekte/Git/claude-code-setup/hooks/trockenlauf-auswerten.py` und deine Zeile daraus) und „Was zurück an Christian geht“.
5. PR mit „Bezug: #460, #461, beide bleiben offen“ (kein Closing-Keyword), **nicht mergen**; „bereit zum Merge“ an die Koordination. Nach der Merge-Meldung und dem Deploy:
   - **#460:** erste Zeile `@wachauer Frage: Gehören AXU_18452_5 und JT_48611000_4 mit dem längeren Kontext unten zum Verb jagen oder zum Nomen jagât?`, darunter was umgehängt wurde und der Kontext.
   - **#461:** erste Zeile `@wachauer Frage: <eine Frage in einem Satz, die ohne Thread verständlich ist>?` (Fabeltiere, gegebenenfalls die eindeutig tierischen Belege, Frage 3 mit Belegen), darunter was umgesetzt ist, mit Zahlen.
   - Labels beider: `auto:blocked` + `wait:kzw`.

### Definition of Done, als Lesertest

Wer nur den PR liest, kann beantworten: welche Tokens umgehängt oder neu annotiert wurden und nach welcher Antwort von KZW; welche Senses `lemma_1958` jetzt hat und welche Belege sie tragen; was unverändert blieb und warum; welche Versionsnummern gelten.
