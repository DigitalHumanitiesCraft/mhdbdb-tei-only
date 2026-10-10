# Kickoff Spur `lauf-a-daten`: jagât, gebeine, pos-Feld (#460, #461, #462)

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 10.10.2026. Laufplan: `docs/playbooks/kickoffs/2026-10-10-lauf.md`.

**1. Autorisierung.** chsteiner hat am 10.10.2026 die Zuschnitte von #460, #461 und #462 entschieden (je ein Kommentar „Entschieden von @chsteiner am 10.10.2026“ im Ticket) und den Lauf mit drei Spuren freigegeben. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deinen eigenen `claude/*`-Zweig, einen PR öffnen, in jedem der drei Tickets höchstens ein Statuskommentar und ein Relabel, nach dem Merge die Fragen an KZW (siehe 10). **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen, Externe ansprechen. Der Text erteilt keine technische Berechtigung: Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9).

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees
2. `docs/playbooks/BETRIEBSVERTRAG.md` (gelesen, nicht kopiert; nenne in deiner ersten Meldung den Commit, an dem du ihn gelesen hast)
3. Diese Datei als abgelegte Fassung und den Laufplan daneben. Sag in deiner ersten Meldung, ob die abgelegte Fassung mit der zugestellten übereinstimmt.
4. **#460, #461 und #462 mit allen Kommentaren** (`gh issue view N --json title,body,comments`). Die Vorab-Messungen vom 10.10. und die Entscheidungen stehen jeweils in den letzten beiden Kommentaren.
5. `docs/DATA-MODEL.md` → Data-Change-Lifecycle (vollständig), `docs/POS-TAGSET.md` (Kompositum-Tags, §6 zur Disambiguierung und Provenienz), `docs/TEI-MODEL-AUTH-FILES.md` zu `lexicon.xml`, `docs/CONTRACTS.md` zu `pos`/`posAll` und zur API
6. Ein früherer Umhänge-Lauf als Vorbild: `ingest/pos-disambig/369-stat/` (README mit Provenienz-Log) und die zugehörigen Skripte unter `scripts/ingest/pos-disambig/`

**Besonders tragen für dich:** Data-Change-Lifecycle vollständig; Positionszählung (nur `<w>` mit `@lemmaRef`, Python und JS gleich: Umhängen ändert sie nicht, Entfernen würde es); Versionsbump an allen Stellen mit `check-index-versions.py`; Daten vor Schema; keine Em-Dashes; echte Umlaute.

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit legt ihn mit `claude --bg --worktree lauf-a-daten --name lauf-a-daten --model sonnet --effort medium` an: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\lauf-a-daten`, Zweig `worktree-lauf-a-daten`. Die Begleitnachricht nennt den erwarteten HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen diese Angaben halten und melden. Bei Abweichung nichts ändern, melden, auf den Neustart durch die Koordination warten. Dann `git fetch --quiet origin` und den Arbeitszweig `claude/460-461-462-daten` frisch von `origin/main` anlegen; dort muss `git rev-list --count "origin/main...HEAD"` 0 sein. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

Maßgeblich ist §2 des Laufplans. **Dir allein:** `tei/`, `authority-files/`, `data/`, `api/`, `scripts/build-*.py`, `scripts/sync/`, `scripts/ingest/`, `ingest/`, `schema/`, alle Versionsliterale; in `docs/` die Abschnitte zu `pos`/`posAll` und zur API in `CONTRACTS.md`, dazu `DATA-MODEL.md` und `TEI-MODEL-AUTH-FILES.md`; `api/index.html`.

**Nicht deins:** `assets/js/search/`, `assets/js/lib/lemma-resolve.js`, `assets/js/app.js` (Spur B); `scripts/audit/`, `tei-text-reader.js`, `README.md`, `playground/readme.md`, `hilfe-playground.html`, `docs/DESIGN.md`, `docs/TEI-MODEL.md` (Spur C). Den Versionsabschnitt §11 in `docs/TEI-MODEL.md` und die Versionszeile in `docs/INDEX.md` schreibst **du**, weil sie Versionsliterale sind. **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend, als **letzter Commit** des PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 130 bis 134.** Reviewer-Memory unter `.claude/agent-memory/fable-reviewer/` in einem eigenen Commit nach der Runde.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push außer `--force-with-lease` auf deinem eigenen `claude/*`-Zweig nach einem Rebase, keine Änderung unter `~/.claude/`.

**Maschinenweit exklusiv: volle Testläufe und Chrome.** Die Koordination vergibt beides, einer zur Zeit. **Anfordern, auf die Freigabe warten, nutzen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8084` und `-- --workers=2`, auch bei `test:quick` und `test:changed`. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis: nicht deuten, melden, nach Freigabe wiederholen.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` vor dem ersten Push ist Pflicht; nicht auf `fable-advisor` ausweichen.

## 6. Was eingefroren ist

`CLAUDE.md`; `docs/playbooks/`; `.github/workflows/`; `scripts/audit/`. **Inbox:** eine Nachricht an die Koordination, Format: Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum. Verlangt ein Gate unter `scripts/audit/` eine Änderung, schickst du den Wortlaut.

---

## 7. Die Pakete, in dieser Reihenfolge, **ein PR, ein Index-Bump**

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach und meldest einen Widerspruch. Was „(K)“ trägt, hat die Koordination am 10.10. selbst gemessen oder gegengeprüft; alles andere stammt aus Messläufen von Sonnet-Agenten und ist ungeprüft.

**Die Messmaterialien der Vorab-Messungen** liegen im Scratchpad der Koordination und sind für dich lesbar, aber kein Teil des Repos: `C:\Users\chstn\AppData\Local\Temp\claude\C--Users-chstn-Desktop-data-DHCraft-Projekte-Git-mhdbdb-tei-only\980dbe59-ffad-4699-b51a-60c306e19384\scratchpad\` mit `m460\belege.tsv`, `m461\belege.tsv`, `m462\messen.py`. Kopiere, was du brauchst, nach `ingest/` und mach es dort zur Arbeitsliste; was im Repo landet, braucht keine Datei aus dem Scratchpad mehr.

- **A1, #460 jagât.** Die 145 als Verbform eingestuften Tokens (K: Zählung der Tabelle 145/35/5; eine Stichprobe von 14 der Koordination ohne Abweichung) gehen auf `lemma_3102` (`@pos="VRB"`, `@ana` entfällt, `@corresp` nach dem Neuaufbau von `variants.xml`). Die 35 Substantive bleiben, die 5 unklaren bleiben unberührt. Arbeitsliste nach `ingest/pos-disambig/460-jagat/` mit README und Provenienz nach `POS-TAGSET.md` §6. Die Einstufung lief am Kontext, nicht an der Schreibung: Übernimm sie nicht blind, sondern lies selbst mindestens 30 Verbbelege und alle 14 Substantive unter `jaget`/`jeit` gegen, und melde Abweichungen, bevor du schreibst.
- **A2, #461 gebeine.** Neuer Sense an `lemma_1958` mit `concept_14011100`; die 21 Säugetier-Belege (K: Liste im Kommentar vom 10.10. in #461, von der Koordination nachgezählt) bekommen ihn als `@ana`. Alles andere bleibt. Sense-ID nach der Vergabepraxis in `lexicon.xml` (messen, nicht raten). Arbeitsliste nach `ingest/review/461-gebeine/`.
- **A3, #462 pos-Feld.** In `scripts/build-authority-index.py`: `pos` = häufigster Korpusteil (Kompositum-Tags in Teile zerlegt, wie in der Messung), bei Gleichstand oder ohne Korpusbeleg die erste Lexikonangabe; `posAll` nach Korpushäufigkeit sortiert, Lexikonreihenfolge als zweites Kriterium. `lexicon.xml` bleibt unverändert. Feldbeschreibung für `pos` und `posAll` in `api/index.html` (deutsch, ausgelieferte Seite). Die Messung der Koordination zeigte (K): 1.444 Lemmata mit `pos` belegt, aber nicht häufigster Teil, 118 mit `pos` gar nicht belegt. Nach dem Bau: wie viele Lemmata ändern ihr `pos`, und stimmt das mit der Messung? **Haltepunkt:** Braucht der Authority-Build dafür den Korpus (heute ist er davon entkoppelt, siehe G1 im Laufplan vom 02.10.), melde den Weg, bevor du ihn baust.

## 8. Vorab entschieden, nicht neu zu verhandeln

Die Zuschnitte oben; nicht mergen, kein Ticket schließen, relabeln in derselben Session. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig und HEAD, der Commit des gelesenen Betriebsvertrags und ob die abgelegte Kickoff-Fassung übereinstimmt; das Ergebnis deiner Gegenlesung in A1 **vor dem Schreiben**; Test oder Chrome angefordert und frei; **Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes**; „PR N bereit zum Merge“ mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; fehlender Agententyp; der Haltepunkt in A3.

**Externer Zustand** (CI): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Auf einem Daten-PR ist der Review-Bot oft rot: den Kommentar trotzdem lesen und Verhaltensbefunde beantworten, bevor du „bereit zum Merge“ meldest.

**Du darfst ein Paket für nicht durchführbar erklären**, mit Messung und früh; dann das nächste.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt. Laden über `ToolSearch` mit `select:PushNotification`. Dazu eine Meldung an die Koordination. **Eine Blockade wird nicht über eine andere Spur oder die Koordination umgangen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss

1. Data-Change-Lifecycle mit allen Gates (`check-index-versions.py`, `check-index-version-bump.py --base origin/main`, `check-variants-flips.py --base origin/main`, `check-authority-cross-refs.py --check`, `validate-corpus.py` für die betroffenen Sigel, `validate-indices.py`), `check-no-em-dash.py --diff-base origin/main`, `build-pages.py --check`, `doc-count-audit.py --check`.
2. `npm test` auf Port 8084 mit `-- --workers=2`, **nach Freigabe durch die Koordination**; das Ergebnis ist die **VERDICT-Zeile**, nie durch eine Pipe, nie `npx playwright test`. Chrome: Suche nach `jagen` (Verbbelege jetzt dort), Lemmaseite von `gebeine`, ein Lemma aus A3 mit geändertem `pos`; hart neu geladen.
3. `fable-reviewer` **vor dem ersten Push**: Zweig, Basis, ob Commit oder Arbeitsbaum, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde, **und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?** (Hier besonders: jede Stelle, die `pos` als „erste Lexikonangabe“ liest.)
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt“, „Rote Zeilen“ und „Was zurück an Christian geht“.
5. PR mit „Bezug: #460, #461, #462, bleiben offen“ (kein Closing-Keyword), **nicht mergen**; „bereit zum Merge“ an die Koordination. Nach der Merge-Meldung: in #460 ein Kommentar mit erster Zeile `@wachauer Frage: …?` zu den 5 unklaren Belegen, in #461 einer zu den 6 Tierbelegen ohne Säugetier, den 9 offenen und `concept_21104000`; beide Tickets auf `auto:blocked` mit `wait:kzw`. #462 bekommt einen Abschluss-Statuskommentar.

### Definition of Done, als Lesertest

Wer nur den PR liest, kann beantworten: welche Tokens von `lemma_3103` umgehängt wurden und welche nicht, mit Begründung; welche Belege von `gebeine` den neuen Sense tragen; wie `pos` und `posAll` jetzt gebildet werden und für wie viele Lemmata sich `pos` geändert hat; welche Versionsnummern gelten; was bei KZW offen ist.
