# Kickoff Spur `lauf-b-suche`: exakte Stufe und URL-Zustand der Korpussuche (#463, #434)

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 10.10.2026. Laufplan: `docs/playbooks/kickoffs/2026-10-10-lauf.md`.

**1. Autorisierung.** chsteiner hat am 10.10.2026 die Zuschnitte von #463 und #434 entschieden (je ein Kommentar „Entschieden von @chsteiner am 10.10.2026“ im Ticket) und den Lauf mit drei Spuren freigegeben. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deine eigenen `claude/*`-Zweige, zwei PRs öffnen, in beiden Tickets höchstens ein Statuskommentar und ein Relabel, nach dem Merge der Abnahme-Ping. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen, Externe ansprechen. Der Text erteilt keine technische Berechtigung: Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9).

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees (besonders „Key Patterns“: dreistufige Lemma-Auflösung)
2. `docs/playbooks/BETRIEBSVERTRAG.md` (gelesen, nicht kopiert; nenne in deiner ersten Meldung den Commit, an dem du ihn gelesen hast)
3. Diese Datei als abgelegte Fassung und den Laufplan daneben. Sag in deiner ersten Meldung, ob die abgelegte Fassung mit der zugestellten übereinstimmt.
4. **#463, #434, #224 und #144 mit allen Kommentaren** (`gh issue view N --json title,body,comments`). Die Vorab-Messungen vom 10.10. und die Entscheidungen stehen in #463 und #434 jeweils in den letzten beiden Kommentaren.
5. `docs/CONTRACTS.md` §C, `docs/ARCHITECTURE.md` zur Suche, `docs/DECISIONS.md` ADR-021
6. `assets/js/search/search-engine.js`, `assets/js/lib/lemma-resolve.js`, `assets/js/app.js` (`handleURLParameters()`), `playground/js/ui/core/router.js` als Vorbild für History

**Besonders tragen für dich:** Python und JS gleich (falls ein Python-Gegenstück der Auflösung existiert, messen); deutsche Oberfläche mit echten Umlauten; keine Em-Dashes; Heroicons inline SVG; `build-pages.py --check` bei HTML; `npm run build:css` bei neuen Klassen.

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit legt ihn mit `claude --bg --worktree lauf-b-suche --name lauf-b-suche --model sonnet --effort medium` an: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\lauf-b-suche`, Zweig `worktree-lauf-b-suche`. Die Begleitnachricht nennt den erwarteten HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen diese Angaben halten und melden. Bei Abweichung nichts ändern, melden, auf den Neustart durch die Koordination warten. Dann `git fetch --quiet origin` und den Arbeitszweig `claude/463-exakte-stufe` frisch von `origin/main` anlegen (später `claude/434-url-zustand`, ebenfalls frisch von `origin/main`); `git rev-list --count "origin/main...HEAD"` muss 0 sein. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

Maßgeblich ist §2 des Laufplans. **Dir allein:** `assets/js/search/`, `assets/js/lib/lemma-resolve.js`, `assets/js/app.js`, `korpus.html` (nur falls nötig), Specs zu Suche und URL-Zustand, `docs/CONTRACTS.md` §C, in `docs/FEATURES.md` die Absätze zur Korpussuche und Lemma-Auflösung. Inventarzeilen für neue Specs in `docs/DEVELOPMENT.md` schreibst du selbst in deinem PR (englisch).

**Grenzfall:** Braucht B2 Codezeilen in `assets/js/rendering/tei-text-reader.js` (Lesepanel öffnen oder schließen), schreibst du sie; Spur C ändert in derselben Datei nur Kommentare mit Zahlen. Melde es der Koordination, bevor du die Datei anfasst.

**Nicht deins:** `tei/`, `authority-files/`, `data/`, `scripts/build-*.py` (Spur A); `scripts/audit/`, `README.md`, `playground/readme.md`, `hilfe-playground.html`, `docs/DESIGN.md`, `docs/TEI-MODEL.md` (Spur C). **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend, als **letzter Commit** des jeweiligen PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 135 bis 139.** Reviewer-Memory unter `.claude/agent-memory/fable-reviewer/` in einem eigenen Commit nach der Runde.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push außer `--force-with-lease` auf deinen eigenen `claude/*`-Zweigen nach einem Rebase, keine Änderung unter `~/.claude/`.

**Maschinenweit exklusiv: volle Testläufe und Chrome.** Die Koordination vergibt beides, einer zur Zeit. **Anfordern, auf die Freigabe warten, nutzen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8085` und `-- --workers=2`, auch bei `test:quick` und `test:changed`; den Dev-Server für Chrome startest du auf 8085 und nur für die Dauer der Prüfung. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` vor dem ersten Push ist Pflicht; nicht auf `fable-advisor` ausweichen.

## 6. Was eingefroren ist

`CLAUDE.md`; `docs/playbooks/`; `.github/workflows/`; `scripts/audit/`. **Inbox:** eine Nachricht an die Koordination, Format: Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum.

---

## 7. Die Pakete, in dieser Reihenfolge, je ein PR

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach und meldest einen Widerspruch. „(K)“ = von der Koordination am 10.10. gemessen oder gegengeprüft.

- **B1, #463.** Bringt Stufe 1 in `resolveLemmaIds()` keinen einzigen Treffer mit Korpusbeleg, wird Stufe 2 mitgefragt (und, wenn auch die nichts Belegtes bringt, Stufe 3 wie heute). Stufe-1-Treffer bleiben in der Liste. (K: `search-engine.js` Z. 161 f. kehrt nach dem ersten Stufe-1-Treffer zurück; nachgestellt mit Node gegen die echten Indexe liefern `rosse`, `gat`, `hanc` heute 0 Zeilen und `roz` 1 statt der Belege von `ros`; 473 Lemmata ohne Beleg sind der einzige Stufe-1-Treffer ihrer Form, während Stufe 2 Belegtes hätte.) Prüfe, ob der Playground (`authority-manager.js`) dieselbe Regel braucht, und ob `lemma-resolve.js` der gemeinsame Ort ist; melde den Befund, bevor du den Playground anfasst. Nicht in diesem Zuschnitt: der `lenden`-Fall (belegtes, aber falsches Stufe-1-Lemma). Spec: die fünf Eingaben aus #463 mit erwarteten Zeilenzahlen. Vertrag in `docs/CONTRACTS.md` §C nachziehen.
- **B2, #434.** Die Suche setzt `?search=` per `replaceState`; das Öffnen eines Textes setzt `?search=…&textId=…` (bei KWIC-Treffern mit `position`) per `pushState`; ein `popstate`-Handler schließt oder öffnet das Lesepanel; `handleURLParameters()` wertet `search` und `textId` gemeinsam aus (erst suchen, dann öffnen). Textauswahl, Filter, Seite und Sortierung bleiben draußen. (K: `app.js:1903` und `:1943` sind die beiden `replaceState`; `main-site.spec.js:198` verlangt heute, dass `search=` verschwindet, und wird bewusst umgestellt.) Prüfe die Zeitsteuerung beim Laden (300 ms in `app.js`, Start nach 500 ms) an einem echten Lauf. Spec: Browser-Zurück aus einem geöffneten Text führt zur Trefferliste; Neuladen von `korpus.html?search=minne` zeigt die Treffer.

## 8. Vorab entschieden, nicht neu zu verhandeln

Die Zuschnitte oben; nicht mergen, kein Ticket schließen, relabeln in derselben Session. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig und HEAD, der Commit des gelesenen Betriebsvertrags und ob die abgelegte Kickoff-Fassung übereinstimmt; der Playground-Befund aus B1; ob B2 `tei-text-reader.js` braucht; Test oder Chrome angefordert und frei; **Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes**; „PR N bereit zum Merge“ mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; fehlender Agententyp.

**Externer Zustand** (CI): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Den Kommentar des Review-Bots lesen und Verhaltensbefunde beantworten, bevor du „bereit zum Merge“ meldest.

**Du darfst ein Paket für nicht durchführbar erklären**, mit Messung und früh; dann das nächste.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt. Laden über `ToolSearch` mit `select:PushNotification`. Dazu eine Meldung an die Koordination. **Eine Blockade wird nicht über eine andere Spur oder die Koordination umgangen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss, je PR

1. `check-no-em-dash.py --diff-base origin/main`, `build-pages.py --check` bei HTML, `doc-count-audit.py --check`, `npm run build:css` bei neuen Klassen.
2. `npm test` auf Port 8085 mit `-- --workers=2`, **nach Freigabe durch die Koordination**; das Ergebnis ist die **VERDICT-Zeile**, nie durch eine Pipe, nie `npx playwright test`. Chrome-Verifikation: B1 mit `rosse`, `gat`, `roz`; B2 mit Suche, Text öffnen, Browser-Zurück, Neuladen, Adresszeile kopieren und in neuem Tab öffnen.
3. `fable-reviewer` **vor dem ersten Push**: Zweig, Basis, ob Commit oder Arbeitsbaum, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde, **und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?** (B1: jede Stelle, die sich darauf verließ, dass ein Stufe-1-Treffer Stufe 2 ausschließt; B2: jede Stelle und jeder Test, die eine saubere Adresszeile voraussetzen.)
4. Journaleintrag als **letzter** Commit nach `git fetch origin`.
5. PR mit „Bezug: #N, bleibt offen“ (kein Closing-Keyword), **nicht mergen**; „bereit zum Merge“ an die Koordination. Nach der Merge-Meldung der Abnahme-Ping: erste Zeile `@juliahin Abnahme: …?` (UX-Prüfung, einfach), darunter Live-URL, Prüfschritte und `@wachauer` mitgenannt; Labels `auto:blocked`, `wait:julia` und `wait:kzw`.

### Definition of Done, als Lesertest

Wer nur den PR liest, kann beantworten: wann die Auflösung jetzt Stufe 2 fragt und was `rosse`, `gat`, `roz` vorher und nachher liefern; welcher Zustand in der URL steht, wann `pushState` und wann `replaceState` läuft, und was Browser-Zurück jetzt tut; welche Tests das festhalten.
