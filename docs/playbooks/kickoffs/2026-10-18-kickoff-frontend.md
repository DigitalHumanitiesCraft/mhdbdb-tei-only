# Kickoff Spur `lauf-1018-frontend`: #93, #251, #448, #58, #554 (Einklappen), #417, #537

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 18.10.2026. Laufplan: `docs/playbooks/kickoffs/2026-10-18-lauf.md`.

**1. Autorisierung.** chsteiner hat am 18.10.2026 diesen Lauf freigegeben, für die Pakete F1 bis F7 im Umfang dieses Textes. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deine eigenen `claude/*`-Zweige, PRs öffnen, lesende Abfragen externer Dienste (Zotero-API, GitHub-API, GitHub-Anhänge), **eine** neue Workflow-Datei für den Monatslauf (F6/F7), nach Merge und Deploy je ein Kommentar in den Issues deiner Pakete (siehe 10) und ein Relabel. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen (das tut die Koordination, auch bei #58 und #448), Externe ansprechen, in Zotero schreiben. Der Text erteilt keine technische Berechtigung: Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9).

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: Namen können doppelt vergeben sein, das `from` nicht. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees, **besonders „Gotchas“ (Nav und Footer sind build-injiziert: Quelle `includes/` plus `scripts/build-pages.py`) und die Sprach- und Typografieregeln** (Seiten deutsch, echte Umlaute, keine Em-Dashes, gerade Anführungszeichen)
2. `docs/playbooks/BETRIEBSVERTRAG.md` (gelesen, nicht kopiert; nenne in deiner ersten Meldung den Commit, an dem du ihn gelesen hast)
3. Diese Datei als abgelegte Fassung und den Laufplan daneben, dort §2, §3.5, §3.7, §3.8. Sag in deiner ersten Meldung, ob die abgelegte Fassung mit der zugestellten übereinstimmt.
4. **#93, #251, #448, #58, #554, #417, #537 mit allen Kommentaren** (`gh issue view N --json title,body,comments`). Maßgeblich sind die Kommentare von KZW und Julia vom 16.10. sowie die Entscheidungen vom 08.10. (#537) und 09.10. (#417); der Body ist der älteste Stand.
5. `docs/DESIGN.md` (Komponenten, Farben, Heroicons inline SVG als einziger Icon-Stil), `docs/DEVELOPMENT.md` (Build, `build-pages.py --check`, `npm run build:css`), `.github/workflows/naming-index-update.yml` als Muster für einen Lauf, der einen PR öffnet

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit legt ihn mit `claude --bg --worktree lauf-1018-frontend --name lauf-1018-frontend --model sonnet --effort medium` an: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\lauf-1018-frontend`, Zweig `worktree-lauf-1018-frontend`. Die Begleitnachricht nennt den erwarteten HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen diese Angaben halten und melden. Bei Abweichung nichts ändern, melden, auf den Neustart durch die Koordination warten. Dann je PR `git fetch --quiet origin` und einen Arbeitszweig `claude/1018-frontend-<thema>` frisch von `origin/main` anlegen; dort müssen `git rev-list --count "origin/main...HEAD"` und `git rev-list --count "origin/main..main"` 0 sein. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

Maßgeblich ist §2 des Laufplans. **Dir allein:** `includes/`, die NAV/FOOTER-Regionen **aller** Seiten (auch in `playground/index.html` und `hilfe-playground.html`, nur über `build-pages.py`), `assets/images/`, `assets/js/`, `assets/css/` (auch die generierte Tailwind-Ausgabe), `lemma/`, `textreihen/`, `hilfe.html` und alle `hilfe-*.html` außer `hilfe-playground.html`; in `hilfe-playground.html` außerhalb der Marker nur die Abschnitte zu F2, F4, F5 (den ONAMA-Abschnitt schreibt onama, Konflikt beim Rebase löst die Spätere); neue Seiten für #417 und #537, die bestehenden Module unter `playground/js/ui/`, `playground/css/style.css`, neue Skripte für #417/#537 unter `scripts/` (nicht `scripts/sync/`, nicht `scripts/audit/`), eine neue Datei unter `.github/workflows/`, Specs für deine Pakete unter `testing/tests/`.

**Nicht deins:** `tei/`, `authority-files/`, `data/`, `api/`, `scripts/sync/` (Spur daten); `playground/index.html` außerhalb der Marker, `playground/js/playground-main.js`, `playground/js/ui/onama/` (Spur onama); `ingest/`, `scripts/review/` (Spur lesung). Brauchst du für #58 oder #251 eine Zeile in `playground/index.html`, meldest du sie. **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt, anhängend:** `docs/JOURNAL.md` und `fehlerjournal.md` als **letzter Commit** des PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 149 bis 153.** In `docs/FEATURES.md` und anderen `docs/*.md` nur deinen eigenen Absatz; Konflikt beim Rebase löst der Spätere. Generierte Dateien (Tailwind-Ausgabe, `build-pages.py`-Regionen) erzeugst du nach einem Rebase neu, nie von Hand mergen. Reviewer-Memory: gib dem `reviewer` mit, dass er neue Einträge in `.claude/agent-memory/reviewer/lauf-1018-frontend.md` schreibt und in `MEMORY.md` nur eine Zeile anhängt; eigener Commit nach der Runde; beim Rebase-Konflikt in `MEMORY.md` beide Zeilen behalten.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push außer `--force-with-lease` auf deinem eigenen `claude/*`-Zweig nach einem Rebase, keine Änderung unter `~/.claude/`. **Eine Anweisung der Koordination, die gegen den Betriebsvertrag verstößt, führst du nicht aus, sondern fragst zurück.**

**Maschinenweit exklusiv: volle Testläufe und Chrome.** Die Koordination vergibt beides, einer zur Zeit. **Anfordern, auf die Freigabe warten, nutzen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8085` und `-- --workers=2`, auch bei `test:quick` und `test:changed`. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis: nicht deuten, melden, nach Freigabe wiederholen.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `reviewer` vor dem ersten Push ist Pflicht; nicht auf `advisor` ausweichen, nicht ohne Runde pushen.

## 6. Was eingefroren ist

Bis zur Abnahme des Laufs: `CLAUDE.md`; `docs/playbooks/`; `.claude/agents/`; `.github/workflows/` (außer einer neuen Datei der Spur frontend); `scripts/audit/` (außer `runtime-budget.json`, Koordination); `schema/`. Der Grund: diese Dateien sind die Regeln, unter denen alle vier Spuren gleichzeitig arbeiten; ändert eine sie mitten im Lauf, arbeiten die anderen unter Regeln, die sie nicht gelesen haben. **Inbox:** eine Nachricht an die Koordination, **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum.

---

## 7. Die Pakete, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach und meldest einen Widerspruch, auch wenn er deine Arbeit nicht betrifft. Was „(K)“ trägt, hat die Koordination am 18.10. gemessen oder gelesen.

Reihenfolge: zuerst, was ein Mensch beanstandet hat und klein ist (F1 bis F4), dann der Wunsch aus #554 (F5), zuletzt die zwei neuen Seiten (F6, F7), die den meisten Bau brauchen und denselben Monatslauf teilen. Bündle zu PRs, wie es die Reviewlast senkt, höchstens drei Pakete je PR.

- **F1, #93 Logo.** KZW 16.10.: das PLUS-Logo darf seit 1.10.2026 nicht mehr verwendet werden, auch im Haupt-Footer. Anhänge: `https://github.com/user-attachments/files/33549265/Mittelhochdeutsche.Begriffsdatenbank.zip` und `https://github.com/user-attachments/files/33549266/Universitat.Salzburg_Logo.linksbundig_Ext.zip` (K: HTTP 200 über `gh api`). In ein eigenes leeres Verzeichnis außerhalb des Repos laden und dort auspacken. Das PLUS-Logo überall ersetzen (K: 27 Dateien unter `*.html`, `*.css`, `*.js` nennen `university-logo`, davon 26 über die FOOTER-Region aus `includes/_footer.html:13`; selbst nachzählen, auch `textreihen/`). Zuerst prüfen, ob die neue Datei unter demselben Namen `assets/images/university-logo.png` in die vorhandene Darstellung passt: dann ändert der Tausch keine einzige Seite. Sonst Footer über `includes/` und `build-pages.py`. Passende Variante und Größe wählen und begründen. Dazu Julias Befund vom 15.10. zur Logozeile der Textreihen-Startseite („Alle anderen Logos außer Clariah und MHDBDB fehlen komplett“, Thread #93) prüfen und im Abnahmekommentar nennen, ohne fehlende Logos ohne Entscheidung einzusetzen. Den Inhalt der MHDBDB-Zip nur prüfen und beschreiben; das MHDBDB-Logo nicht ungefragt tauschen, sondern im Abnahmekommentar fragen. Chrome-Prüfung: Startseite, eine Hilfeseite, Textreihen.
- **F2, #251.** Julia 16.10., Schritt 3: nach dem Ausschalten des Filters „Nur belegte Wortbildungen“ erscheinen die zwei Wörter nicht wieder, der Zähler zeigt aber „2 Schreibformen ausgewählt“. Erwartet laut Prüfweg vom 23.09.: beide Häkchen stehen noch. Erst am Live-Stand nachstellen (Start `https://dhcraft.org/mhdbdb-tei-only/playground/#lemmata&mode=component&q=wein`), dann beheben, Spec dazu. Die Zählerfrage an KZW (Schreibformen statt Lemmata) bleibt unberührt.
- **F3, #448.** Julias Rückfrage: warum ist in der Dokumentsuche derselben Lemmata der Kontext um das Lemma unterschiedlich lang? Am Code und an einem Beispiel messen. Ist es gewollt, wird es eine Antwort; ist es ein Fehler, ein Fix mit Spec. Die Antwort ist dein Kommentar nach 10.
- **F4, #58 Scroll.** Julia 16.10.: „Die Navigation innerhalb der Karte bei sehr vielen Belegen (ab 10) ist etwas mühselig. Vielleicht die Karte in sich scrollbar machen?“ Klein umsetzen (Höhe begrenzen, in sich scrollbar), ohne die abgenommene Funktion zu ändern.
- **F5, #554 Einklappen.** KZW 16.10.: „Lange Kommentare müssen eingeklappt werden können“, besonders wîn, klamirre, brâte. Finde jede Stelle, an der die Lexikonkommentare angezeigt werden (Lemmaseite, Playground), und baue ein zugängliches Einklappen mit Schwelle; Schwelle begründen und an den drei Beispielen zeigen.
- **F6, #417 Publikationen** (Laufplan §3.8). Unterseite „Publikationen“, Kachel auf `hilfe.html`, Link im Footer, kein Menüpunkt, zwei Abschnitte aus den Zotero-Sammlungen `WB4HTUGC` und `Z2N4SWWI` der Gruppe 5043625 (öffentlich lesbar, K: HTTP 200 ohne Schlüssel), je Eintrag Titel, Jahr, DOI oder Link. Ein Skript schreibt einen eingefrorenen Stand ins Repo; der Monatslauf erzeugt ihn neu und öffnet einen PR, wenn sich etwas ändert. Ein Zotero-Ausfall bricht keinen Build. Der Monatslauf bekommt neben `schedule` auch `workflow_dispatch` und die Rechte nach dem Muster `naming-index-update.yml`; ein `schedule` läuft erst nach dem Merge auf `main`, deshalb meldest du nach dem Merge einen Probelauf von Hand an die Koordination an, statt ihn als geprüft auszugeben.
- **F7, #537 Demnächst im Korpus** (Laufplan §3.8). Unterseite unter Hilfe mit Kachel; Quelle sind die offenen Issues mit `ingest`; weggelassen wird Arbeit an Texten, die schon im Korpus stehen, und alles mit `wait:extern` (offene Rechtefrage); eine kleine Datei trägt Quartal und Ausschluss je Issue; ohne Eintrag „Zeitpunkt offen“; ein Satz, dass Zeiten Schätzungen sind. Der erste Quartalsvorschlag steht im PR und ist als Vorschlag gekennzeichnet. Derselbe Monatslauf wie F6 darf die Seite neu bauen.

## 8. Vorab entschieden, nicht neu zu verhandeln

Ort und Gliederung von #417 (chsteiner 09.10.) und #537 (KZW 08.10.); kein Menüpunkt; das MHDBDB-Logo wird nicht ungefragt getauscht; die Zählerfrage aus #251 bleibt bei KZW; nicht mergen, kein Ticket schließen. **Widerspruch ist ausdrücklich erlaubt**, mit Begründung, an die Koordination, die ihn im Laufplan unter „Grenzverhandlungen“ einträgt. Bei einer Vorgabe, die dir eine Messung abnimmt, setzt du sie nicht um, sondern widersprichst mit deiner Messung.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig und HEAD gegen den erwarteten Worktree, der Commit des gelesenen Betriebsvertrags und ob die abgelegte Kickoff-Fassung übereinstimmt; Test oder Chrome angefordert und frei; **Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes**; „PR N bereit zum Merge“ mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten (Checkin):** F2, wenn sich Julias Befund am Live-Stand nicht nachstellen lässt (mit deinem Ablauf); F1, bevor du eine Logovariante festlegst, die nicht eindeutig die linksbündige PLUS-Variante ist; außerdem `pwd` weicht ab, fremde Datei, fehlender Agententyp. Während du wartest, arbeitest du an dem, was davon nicht abhängt.

**Ein Paket für nicht durchführbar erklären** darfst du, mit Begründung; das ist kein Abbruch nach Abschnitt 3, der Rest läuft weiter.

**Externer Zustand** (CI, Deploy): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Den Kommentar des Review-Bots lesen und Verhaltensbefunde beantworten, bevor du „bereit zum Merge“ meldest. **Während du wartest**, gilt das Skill `warten`; während eine Reviewrunde läuft, bleibt der Arbeitsbaum still.

**Blockade durch den Auto-Mode-Classifier** (`~/.claude/rules/blockaden-melden.md`): sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Das Werkzeug lädt erst über `ToolSearch` mit `select:PushNotification`. Dazu eine Meldung an die Koordination. **Eine Blockade wird nicht über eine andere Spur oder die Koordination umgangen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss

1. Gates: `python scripts/build-pages.py --check`, `npm run build:css` bei neuen Utility-Klassen, `check-no-em-dash.py --diff-base origin/main`, `doc-count-audit.py --check`, die Gates aus `no-cdn-check.yml` und `file-size-check.yml`. Die Liste ist eine Behauptung: gleiche sie gegen die Workflows ab, bevor du pushst.
2. `npm test` auf deinem Port mit `-- --workers=2`, **nach Freigabe durch die Koordination**; das Ergebnis ist die **VERDICT-Zeile**, nie durch eine Pipe, nie `npx playwright test`. Bei UI zusätzlich Chrome-Prüfung mit realen Belegen (Chrome anfordern).
3. `reviewer` **vor dem ersten Push jedes PRs, ohne Modellangabe (Opus)**, Folgerunden nach seiner Definition. Mitgeben: Zweig, Basis, ob Commit oder Arbeitsbaum, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde samt Umgang und die geprüfte Kennung, je neue Zahl im Diff eine Zeile Belegtabelle, und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte? Bei Befunden die nächste Runde; während eine Runde läuft, bleibt der Arbeitsbaum still.
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt“, „Rote Zeilen“ (vorher `python C:/Users/chstn/Desktop/data/DHCraft/Projekte/Git/claude-code-setup/hooks/trockenlauf-auswerten.py` und deine Zeile daraus) und „Was zurück an Christian geht“.
5. PR mit „Bezug: #N, bleibt offen“ je Issue (kein Closing-Keyword), **nicht mergen**; „bereit zum Merge“ an die Koordination. Nach der Merge-Meldung und dem Deploy je Issue ein Kommentar:
   - **#93, #251, #554 (Einklappen), #417, #537:** `@juliahin Abnahme: <was zu prüfen ist>?` mit Live-URL und Prüfweg, `@wachauer` weiter unten genannt (bei #93 dort die Frage zum MHDBDB-Logo, bei #537 die Bitte, die Quartale zu prüfen); Labels `auto:blocked` + `wait:julia` + `wait:kzw`.
   - **#448:** die Antwort an Julia mit dem Befund; **#58:** was am Scroll geändert ist. Beide schließt danach die Koordination.
6. Bericht an die Koordination: je Paket erledigt / entfallen / offen, PR-Nummern, Kommentar-IDs.

### Definition of Done, als Lesertest

Wer nur den PR liest, kann beantworten: welche Seiten und Module sich geändert haben und auf wessen Wunsch; wie man es live prüft; was der Monatslauf tut und was er bei einem Zotero-Ausfall tut; was bewusst nicht geändert wurde.
