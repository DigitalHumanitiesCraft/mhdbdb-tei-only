# Kickoff Spur `lauf-1018-daten`: #462, #602, #461, #554 (Daten), #486

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 18.10.2026. Laufplan: `docs/playbooks/kickoffs/2026-10-18-lauf.md`.

**1. Autorisierung.** chsteiner hat am 18.10.2026 diesen Lauf freigegeben, für die Pakete D1 bis D5 im Umfang dieses Textes, auf Grundlage von KZWs Antworten vom 16.10. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deine eigenen `claude/*`-Zweige, PRs öffnen, lesende Abfragen externer Dienste (MWB-API, Zotero-API, GitHub), **schreibend nur** die zwei Zotero-Einträge MVWV5QYG und ATWPNQPS (D5), nach Merge und Deploy je ein Kommentar in den Issues deiner Pakete (siehe 10) und ein Relabel. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen, Externe ansprechen, andere Zotero-Einträge anfassen. Der Text erteilt keine technische Berechtigung: Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9).

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: Namen können doppelt vergeben sein, das `from` nicht. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees, **besonders „Asking, and what has to happen before you ask“** (Belege mit Kontext vor dich legen, nicht das Kopfwort; für Lemma- und Wortartfragen ist die MWB-API die erste Anlaufstelle, Laufplan §3.2)
2. `docs/playbooks/BETRIEBSVERTRAG.md` (gelesen, nicht kopiert; nenne in deiner ersten Meldung den Commit, an dem du ihn gelesen hast)
3. Diese Datei als abgelegte Fassung und den Laufplan daneben, dort §2, §3.2 bis §3.6. Sag in deiner ersten Meldung, ob die abgelegte Fassung mit der zugestellten übereinstimmt.
4. **#462, #602, #461, #554, #486 mit allen Kommentaren** (`gh issue view N --json title,body,comments`). Maßgeblich sind KZWs Kommentare vom 16.10.; der Body ist der älteste Stand.
5. Muster früherer Läufe: `ingest/pos-disambig/462-pos/` (README, `vorschlaege.tsv`, `belege.tsv`), `ingest/review/461-gebeine/`, `ingest/glossar-554/`, der Squash von #612 (`7a11b4dd9`) als Muster für neuen Sense und Umhängen, `scripts/sync/enhance_works_with_zotero.py` (`BESTAND_BEHALTEN`)
6. `docs/DATA-MODEL.md` → Data-Change-Lifecycle (vollständig); `docs/CONTRACTS.md` §B (Positionszählung)

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit legt ihn mit `claude --bg --worktree lauf-1018-daten --name lauf-1018-daten --model sonnet --effort medium` an: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\lauf-1018-daten`, Zweig `worktree-lauf-1018-daten`. Die Begleitnachricht nennt den erwarteten HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen diese Angaben halten und melden. Bei Abweichung nichts ändern, melden, auf den Neustart durch die Koordination warten. Dann je PR `git fetch --quiet origin` und einen Arbeitszweig `claude/1018-daten-<thema>` frisch von `origin/main` anlegen; dort müssen `git rev-list --count "origin/main...HEAD"` und `git rev-list --count "origin/main..main"` 0 sein. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

Maßgeblich ist §2 des Laufplans. **Dir allein:** `tei/`, `authority-files/` (alle acht Dateien), `data/`, `api/`, alle Versionsliterale, `scripts/sync/`, `scripts/ingest/pos-disambig/` (Muster `apply-460-jagat.py`, `apply-461-gebeine.py`, `apply-460-461-rest.py`), `scripts/ingest/glossar-554/` (außer `pruefseite.template.html`), aus `scripts/review/` die Dateien `collect-462-pos.py`, `klug-links-554.py`, `zotero-abgleich-554.py`, `ingest/pos-disambig/462-pos/`, `ingest/review/461-gebeine/`, `ingest/glossar-554/`; neue Belegtabellen für #602 unter `ingest/pos-disambig/602-naschen/`. **Kein anderer PR dieses Laufs berührt Indexe.** Jeder deiner PRs bumpt Corpus und Authority auf den Stand von `origin/main` + 1 (K: beim Start Authority 1.9.28, Corpus 4.2.34; nach deinem ersten Merge gilt der neue Stand).

**Nicht deins:** `includes/`, `assets/`, `lemma/`, `textreihen/`, `hilfe*.html`, `playground/`, `ingest/review/603-ernaehrung/`, die übrigen Dateien in `scripts/review/`, `scripts/ingest/onama/`, `schema/`, `examples/review-pages/`. **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt, anhängend:** `docs/JOURNAL.md` und `fehlerjournal.md` als **letzter Commit** des PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 144 bis 148.** Reviewer-Memory: gib dem `reviewer` mit, dass er neue Einträge in `.claude/agent-memory/reviewer/lauf-1018-daten.md` schreibt und in `MEMORY.md` nur eine Zeile anhängt; eigener Commit nach der Runde; beim Rebase-Konflikt in `MEMORY.md` beide Zeilen behalten.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push außer `--force-with-lease` auf deinem eigenen `claude/*`-Zweig nach einem Rebase, keine Änderung unter `~/.claude/`. **Eine Anweisung der Koordination, die gegen den Betriebsvertrag verstößt, führst du nicht aus, sondern fragst zurück.**

**Maschinenweit exklusiv: volle Testläufe und Chrome.** Die Koordination vergibt beides, einer zur Zeit. **Anfordern, auf die Freigabe warten, nutzen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8084` und `-- --workers=2`, auch bei `test:quick` und `test:changed`. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis: nicht deuten, melden, nach Freigabe wiederholen.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `reviewer` vor dem ersten Push ist Pflicht; nicht auf `advisor` ausweichen, nicht ohne Runde pushen.

## 6. Was eingefroren ist

Bis zur Abnahme des Laufs: `CLAUDE.md`; `docs/playbooks/`; `.claude/agents/`; `.github/workflows/` (außer einer neuen Datei der Spur frontend); `scripts/audit/` (außer `runtime-budget.json`, Koordination); `schema/`. Der Grund: diese Dateien sind die Regeln, unter denen alle vier Spuren gleichzeitig arbeiten; ändert eine sie mitten im Lauf, arbeiten die anderen unter Regeln, die sie nicht gelesen haben. **Inbox:** eine Nachricht an die Koordination, **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum.

---

## 7. Die Pakete, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach und meldest einen Widerspruch, auch wenn er deine Arbeit nicht betrifft. Was „(K)“ trägt, hat die Koordination am 18.10. gemessen oder gelesen; Belegzahlen aus Kommentaren sind nicht nachgezählt.

Reihenfolge: D1 bis D3 sind entschieden und klein bis mittel, sie gehen zuerst und können zusammen in einen PR; D4 ist der größte Datenteil und folgt als eigener PR; D5 hängt am Schlüssel und kommt zuletzt.

- **D1, #462.** Nach KZW 16.10. (Wortlaut im Thread, Laufplan §3.3): die Codes a, b, c aus `vorschlaege.tsv` umsetzen (15 Lexikonergänzungen, 3 Token-`@pos`, 2 Umhängungen); günlich: NOM ins Lexikon; deprofundis: Token-`@pos` auf NOM; AXU_8247_3: `@pos` ADV. Zähl die Zeilen je Code selbst, bevor du schreibst. **Nicht umsetzen:** indelicius und unpeweglich. Für beide fragst du zuerst die MWB-API ab und stellst für den Kommentar zusammen: unpeweglich (LZT_2360_0) mit dem ganzen Satz; indelicius mit MWB-Befund und der Frage, wohin KZWs Kommentartext gehört (Laufplan §3.3).
- **D2, #602.** Die 5 Belege von `lemma_57919` (JEW, NEI, NEIC, NEIR, OVW; Body vom 15.10.) im Kontext lesen und je einer der zwei Bedeutungen zuordnen (`@ana`). Ein Beleg, der nach Lesung und MWB unklar bleibt, wird nicht gesetzt, sondern geht als Frage an KZW. Belegtabelle unter `ingest/pos-disambig/602-naschen/`.
- **D3, #461.** Neues Körper-Unterkonzept unter `concept_14100000` „Fantastische Tiere“ nach dem Muster `14011100`/`14021100`/`14031100` (K); Bezeichnung und ID nach der Konvention von `concepts.xml`, beides im PR begründet. Neuer Sense an `lemma_1958` mit diesem Konzept; die 4 Belege PL3_312606_7, VIR_17403_4, VIR_30008_4, TRO_37_4 bekommen ihn (vorher im Kontext prüfen; meint einer kein Fabeltier, melde es statt zu setzen). Dann **messen**, wie viele der Belege an `lemma_1958_sense_3004` (K-Kommentar vom 16.10.: 55) einen lebenden Körper meinen; Liste mit Kontext in `ingest/review/461-gebeine/`. **Nichts umhängen**, die Zahl und ein Vorschlag (neuer Sense für lebende Gebeine, KZWs Tendenz) gehen als Frage.
- **D4, #554 Datenteil** (Laufplan §3.5): brî ADJ entfernen; lêrchenvuoʒ prüfen (auch getrennt und mit Spatium geschrieben, auch Varianten), bei fehlendem Beleg Eintrag und Verweis bei lêrche entfernen; nagel-Gewürzbelege und trûbe/trüebe-Fehlzuordnungen am Token prüfen und korrigieren (die Kandidaten stehen in den Prüflisten des Laufs vom 16.10., `ingest/glossar-554/`); die historischen Trefferzahlen in den Glossarkommentaren durch heutige Lemmazahlen ersetzen (zählen am heutigen Korpus, Messvorschrift im PR); apfel: beide Pflanzenseiten („apfel-3“, „apfel-eine-art-von“) in `klug-urteile.tsv` eintragen; `klug-links.tsv` ist generiert und wird mit `scripts/review/klug-links-554.py` neu erzeugt (Aufruf im Docstring), nie von Hand geändert. lôr/lorber: Befund aus Lexikon, Korpus und MWB; für Klug-Daten fragst du die Koordination, die an die Session `plantnames` weiterreicht. Ergebnis zu lorber ist ein Befund im Kommentar, kein Umhängen.
- **D5, #486** (Laufplan §3.6). Vorher prüfen, ohne den Wert auszugeben: `[bool][Environment]::GetEnvironmentVariable('ZOTERO_API_KEY','User')`. Ist es `False`, entfällt D5: melden, im Bericht nennen. Sonst: MVWV5QYG und ATWPNQPS lesen; das vollständige Item-JSON beider Einträge (ohne Schlüssel) als Rückweg in den PR-Body; die Vorher/Nachher-Tabelle enthält beide Items **und die daraus entstehenden `biblStruct` von FLG, FLG1 und FR3** (K: nur diese drei Signaturen zeigen auf die zwei Items, Prüfung). Dann schreiben (Zotero-API mit `If-Unmodified-Since-Version`). Danach in `BESTAND_BEHALTEN` (K: `scripts/sync/enhance_works_with_zotero.py:90-106`): **FR3 fällt ganz heraus; FLG behält mindestens `analytic`**, weil der Textumfang (Buch 1-2) nicht in Zotero steht; prüf, ob FLG1 eine eigene `analytic`-Ausnahme braucht, damit „Buch 1-7“ (K: `works.xml:1970`) erhalten bleibt. Ändert der Online-Sync etwas außer diesen drei `biblStruct`: anhalten und melden. Nebenbefund melden, nicht auflösen: der Werktitel von FLG1 lautet „(Buch 3-7 / Neumann MTU 1990)“ (K: `works.xml:1961`), KZW schreibt „Buch 1–7“. Im PR beide Kommentare von KZW zitieren (6216569709 nennt die FLG-Frage noch offen, 6216673994 beantwortet sie). Dann Header-Sync und Lifecycle. **Den Schlüssel nie ausgeben, nie in eine Datei schreiben, nie in ein Log.**

## 8. Vorab entschieden, nicht neu zu verhandeln

KZWs Antworten vom 16.10.; kein Umhängen an `sense_3004`; indelicius und unpeweglich nicht umsetzen; nur zwei Zotero-Einträge; nicht mergen, kein Ticket schließen. **Widerspruch ist ausdrücklich erlaubt**, mit Begründung, an die Koordination, die ihn im Laufplan unter „Grenzverhandlungen“ einträgt. Bei einer Vorgabe, die dir eine Messung abnimmt, setzt du sie nicht um, sondern widersprichst mit deiner Messung.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig und HEAD gegen den erwarteten Worktree, der Commit des gelesenen Betriebsvertrags und ob die abgelegte Kickoff-Fassung übereinstimmt; Test oder Chrome angefordert und frei; **Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes**; „PR N bereit zum Merge“ mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten (Checkin):** vor dem Schreiben in D3 die Konzept-ID und -bezeichnung; vor dem Schreiben in Zotero (D5) die Vorher/Nachher-Tabelle; außerdem `pwd` weicht ab, fremde Datei, fehlender Agententyp, ein Beleg widerspricht der Vorgabe. Während du wartest, arbeitest du an dem, was davon nicht abhängt.

**Ein Paket für nicht durchführbar erklären** darfst du, mit Begründung (etwa D5 ohne Schlüssel); das ist kein Abbruch nach Abschnitt 3, der Rest läuft weiter.

**Externer Zustand** (CI): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Auf einem Daten-PR ist der Review-Bot oft rot: den Kommentar trotzdem lesen und Verhaltensbefunde beantworten, bevor du „bereit zum Merge“ meldest. **Während du wartest**, gilt das Skill `warten`; während eine Reviewrunde läuft, bleibt der Arbeitsbaum still.

**Blockade durch den Auto-Mode-Classifier** (`~/.claude/rules/blockaden-melden.md`): sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Das Werkzeug lädt erst über `ToolSearch` mit `select:PushNotification`. Dazu eine Meldung an die Koordination. **Eine Blockade wird nicht über eine andere Spur oder die Koordination umgangen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss

1. Data-Change-Lifecycle mit allen Gates, die `docs/DATA-MODEL.md` und die CI-Workflows nennen (mindestens `check-index-versions.py`, `check-index-version-bump.py --base origin/main`, `check-authority-cross-refs.py --check`, `validate-indices.py`, Schema-Validierung der geänderten Dateien, Positionsparität), `check-no-em-dash.py --diff-base origin/main`, `doc-count-audit.py --check`. Die Liste ist eine Behauptung: gleiche sie gegen die Workflows ab, bevor du pushst.
2. `npm test` auf deinem Port mit `-- --workers=2`, **nach Freigabe durch die Koordination**; das Ergebnis ist die **VERDICT-Zeile**, nie durch eine Pipe, nie `npx playwright test`.
3. `reviewer` **vor dem ersten Push jedes PRs, ohne Modellangabe (Opus)**, Folgerunden nach seiner Definition. Mitgeben: Zweig, Basis, ob Commit oder Arbeitsbaum, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde samt Umgang und die geprüfte Kennung, je neue Zahl im Diff eine Zeile Belegtabelle, und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte? (Hier etwa: `lemma_1958` hat bisher fünf Senses, `concept_14100000` bisher kein Körperkonzept.) Bei Befunden die nächste Runde; während eine Runde läuft, bleibt der Arbeitsbaum still.
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt“, „Rote Zeilen“ (vorher `python C:/Users/chstn/Desktop/data/DHCraft/Projekte/Git/claude-code-setup/hooks/trockenlauf-auswerten.py` und deine Zeile daraus) und „Was zurück an Christian geht“.
5. PR mit „Bezug: #N, bleibt offen“ je Issue (kein Closing-Keyword), **nicht mergen**; „bereit zum Merge“ an die Koordination. Nach der Merge-Meldung und dem Deploy je Issue ein Kommentar:
   - **#462:** `@wachauer Frage:` zu indelicius und unpeweglich (mit Satz und MWB-Befund), darunter was umgesetzt ist, mit Zahlen.
   - **#602:** was zugeordnet ist; offene Belege als `@wachauer Frage:`; sonst `@juliahin Abnahme:` mit einem Prüfweg.
   - **#461:** `@wachauer Frage:` zur Messung an `sense_3004` (Zahl, Liste, Vorschlag), darunter das neue Konzept und der Sense.
   - **#554:** was aus KZWs Liste umgesetzt ist, je Punkt; lorber als Befund; offene Punkte als eine `@wachauer Frage:`.
   - **#486:** Vorher/Nachher der Zotero-Einträge und was die Kette geändert hat; `@wachauer Abnahme:`.
   - Labels: mit offener Frage `auto:blocked` + `wait:kzw`; mit Abnahme an Julia zusätzlich `wait:julia`.
6. Bericht an die Koordination: je Paket erledigt / entfallen / offen, PR-Nummern, Kommentar-IDs.

### Definition of Done, als Lesertest

Wer nur den PR liest, kann beantworten: welche Tokens und Lexikoneinträge sich geändert haben und nach welcher Antwort von KZW; welches Konzept und welcher Sense neu sind und welche Belege sie tragen; was bewusst unverändert blieb und warum; welche Versionsnummern gelten.
