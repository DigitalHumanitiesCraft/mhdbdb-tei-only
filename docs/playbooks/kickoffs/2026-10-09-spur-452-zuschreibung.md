# Kickoff Spur `spur-452-zuschreibung`: Zuschreibungsstatus für Werkautoren (#452)

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 09.10.2026.

**1. Autorisierung.** chsteiner hat am 09.10.2026 im Gespräch mit der Koordination entschieden, #452 nach dem Daten-PR #553 anzugehen; die Koordination lässt es als zweite Spur neben `spur-93-textreihen` laufen, weil die Dateien sich nicht überschneiden. Die fachlichen Entscheidungen hat @wachauer am 16.09. in #444 und am 08.10.2026 in #452 getroffen. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deinen eigenen `claude/*`-Zweig, einen PR öffnen, in #452 höchstens ein Statuskommentar und ein Relabel. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen, Externe ansprechen. Der Text erteilt keine technische Berechtigung: Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9). `auto:checkin` heißt hier: Entscheidungspunkte gehen an die Koordination, nicht an KZW, und du wartest auf die Antwort.

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: Ein Sessionname kann beim Antworten längst einer anderen Session gehören. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees
2. `docs/playbooks/BETRIEBSVERTRAG.md` (gelesen, nicht kopiert; nenne in deiner ersten Meldung den Commit, an dem du ihn gelesen hast)
3. Diese Datei als abgelegte Fassung, `docs/playbooks/kickoffs/2026-10-09-spur-452-zuschreibung.md`. Sag in deiner ersten Meldung, ob sie mit der zugestellten übereinstimmt.
4. **#452, #444 und PR #445 mit allen Kommentaren** (`gh issue view N --json title,body,comments`, `gh pr view 445 --json body,comments`). Der Vorschlag steht im Kommentar vom 23.09. in #452, KZWs Antworten am 08.10. darunter, ihre Grundsatzentscheidung vom 16.09. in #444.
5. `docs/DATA-MODEL.md` → Data-Change-Lifecycle (vollständig), `docs/TEI-MODEL-AUTH-FILES.md` zu `works.xml`, `docs/TEI-MODEL.md` zum `titleStmt`, `docs/CONTRACTS.md` zu Autorfeldern in Index und API
6. `schema/mhdbdb-authority.rnc` und `schema/mhdbdb.rnc` an den Stellen für `<author>`

**Besonders tragen für dich:** Data-Change-Lifecycle vollständig, Daten vor Schema (eine Schema-Erweiterung ist hier gewollt, aber nur so weit, wie die neuen Daten sie brauchen); Versionsbump an allen Stellen mit `check-index-versions.py`; deutsche Oberfläche mit echten Umlauten und geraden Anführungszeichen; keine Em-Dashes; Heroicons inline SVG; `build-pages.py --check` bei HTML; `npm run build:css` bei neuen Klassen.

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit legt ihn mit `claude --bg --worktree spur-452-zuschreibung --name spur-452-zuschreibung --model sonnet --effort medium` an: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\spur-452-zuschreibung`, Zweig `worktree-spur-452-zuschreibung`. Die Begleitnachricht nennt den erwarteten HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen diese Angaben halten und melden. Bei Abweichung nichts ändern, melden, auf den Neustart durch die Koordination warten. Dann `git fetch --quiet origin` und den Arbeitszweig `claude/452-zuschreibung` frisch von `origin/main` anlegen; dort muss `git rev-list --count "origin/main...HEAD"` 0 sein. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

**Dir allein:** `authority-files/works.xml` (nur die Werke dieses Auftrags), die `titleStmt`-Autoren in `tei/CR.tei.xml`, `tei/BAX.tei.xml`, `tei/HOF.tei.xml`, `tei/VDH.tei.xml`, `tei/RHB.tei.xml`; `schema/mhdbdb-authority.rnc/.rng` und `schema/mhdbdb.rnc/.rng` an den Stellen für `<author>`; die Autor-Extraktion in `scripts/build-corpus-index.py`, `scripts/build-authority-index.py` und `scripts/build-api.py`; alle Versionsliterale (du nimmst Korpus 4.2.31 und Authority 1.9.22, falls nötig; vor dem Bump `gh pr list` prüfen, wie `docs/DATA-MODEL.md` es verlangt); die Autoranzeige im Frontend (Leseansicht-Metadaten, Personen- und Werk-Explorer im Playground, wo sonst der Autor eines Textes erscheint: nach Messung); `contributors.xml` nur lesend; die Abschnitte zu Autoren in `docs/TEI-MODEL.md`, `docs/TEI-MODEL-AUTH-FILES.md`, `docs/CONTRACTS.md`, `docs/DATA-MODEL.md`, `docs/FEATURES.md`; neue oder angepasste Specs.

**Nicht deins:** alles unter `textreihen/` oder wie die #93-Spur ihr neues Verzeichnis nennt, `includes/`, die Hilfe-Übersicht und ihre Kacheln (das ist die Spur `spur-93-textreihen`); `lexicon.xml`, `variants.xml`, `genres.xml`; jeder andere TEI-Inhalt. **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend, als **letzter Commit** des PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 115 bis 119**; die Spur 93 hat 109 bis 113, die Koordination 120 aufwärts. Reviewer-Memory unter `.claude/agent-memory/fable-reviewer/` in einem eigenen Commit nach der Runde.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push außer `--force-with-lease` auf deinem eigenen `claude/*`-Zweig nach einem Rebase, keine Änderung unter `~/.claude/`.

**Maschinenweit exklusiv: volle Testläufe und Chrome.** Die Koordination vergibt beides, einer zur Zeit; die Spur 93 nutzt Port 8082. **Anfordern, auf die Freigabe warten, nutzen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8083` und `-- --workers=2`, auch bei `test:quick` und `test:changed`; den Dev-Server für Chrome startest du auf 8083 und nur für die Dauer der Prüfung. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis: nicht deuten, melden, nach Freigabe wiederholen.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` vor dem ersten Push ist Pflicht; nicht auf `fable-advisor` ausweichen.

## 6. Was eingefroren ist

`CLAUDE.md`; `docs/playbooks/`; `.github/workflows/`; `scripts/audit/`. **Inbox:** eine Nachricht an die Koordination. **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum; die Koordination trägt ein. **Grund:** Ändert eine Spur eine Datei, die jede Session beim Start lädt, arbeiten andere ab dann unter geänderten Regeln, ohne es zu merken; am 01.09.2026 ist genau das passiert. Verlangt ein Gate unter `scripts/audit/` eine Änderung, schickst du den Wortlaut.

---

## 7. Die Pakete, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach, auch die, die deinen Befund stützen, und meldest einen Widerspruch. Was unten „(K)“ trägt, hat die Koordination am 09.10. selbst gemessen; alles andere ist ungeprüft. **Keine Labelabfrage als Arbeitsgrundlage.**

**Reihenfolge begründet:** Z1 zuerst, weil die Kodierung alles Weitere bestimmt und an genau einer Stelle (Rolle „Bearbeiter“) noch nicht entschieden ist.

**Was entschieden ist** (KZW, 08.10. in #452, und 16.09. in #444; nachlesen):

- Vier Status: ohne Zusatz = anerkannt; „umstritten“; „unsicher zugeschrieben“; „verworfen“.
- „Anonym“ bleibt zusätzlicher Autor, auch wenn der Status die Unsicherheit schon ausdrückt.
- BAX: Lamprecht als Autor der Vorlage, dazu der anonyme Bearbeiter der Basler Fassung ausdrücklich als **Bearbeiter**.
- RHB: Konrad von Würzburg „umstritten“, dazu Anonym, **Anonym an erster Stelle**.
- HOF/VDH: „Für HOF/VDH gilt Stricker.“
- CR: KZW hat am 16.09. geschrieben, Bligger könne wieder zugeordnet werden, sobald es einen Zuschreibungsstatus gibt; dann als „verworfen“ neben Anonym.

**Heutiger Stand (K):** `works.xml` führt `work_5` nur mit Anonym, `work_462`, `work_408` und `work_325` je mit benanntem Autor zuerst und Anonym danach; die TEI-Header von BAX, HOF, VDH, RHB spiegeln das, CR trägt nur Anonym.

- **Z1, Kodierung (messen und vorschlagen, nichts schreiben).** Wo der Status sitzt (Vorschlag vom 23.09.: Attribut auf `<author>` plus `<note type="attribution">` mit `@resp` und Datum), wie die Rolle „Bearbeiter“ ausgedrückt wird (eigenes Element, `@role`, anderes), welche Schema-Erweiterung beides braucht, und wie Index und API daraus den angezeigten Autor bestimmen (Vorschlag: der erste nicht verworfene) und den Status als eigenes Feld führen. **Sofort an die Koordination**, mit den betroffenen Codestellen. **Haltepunkt:** bis die Koordination die Kodierung bestätigt.
- **Z2, Daten.** `works.xml` und die fünf Header nach der bestätigten Kodierung, mit Beleg und Datum je Status aus den Quellen im Kommentar vom 23.09.; Schema; Data-Change-Lifecycle vollständig.
- **Z3, Anzeige.** Überall, wo ein Werkautor erscheint, die Statustexte; verworfene Zuschreibungen nur unter „Frühere Zuschreibungen“ und nicht als Autor in Suche, Filtern und Personenansicht; die Rolle Bearbeiter sichtbar. Welche Stellen das sind, misst du (Grep über JS **und** HTML) und meldest die Liste, bevor du sie änderst.
- **Z4, Doku und Tests.** Die Doku-Abschnitte aus 5, eine Spec, die je Status eine reale Seite prüft.

**Eine Vorgabe, die die Koordination selbst für schwach hält, mit Ersatzfassung:** „Für HOF/VDH gilt Stricker“ lese ich als Antwort auf die Frage, ob Anonym dort entfällt, also **Stricker allein**, weil die Quellenprüfung vom 23.09. keine Quelle für eine anonyme Autorschaft fand und KZWs allgemeine Regel („Anonym bleibt“) an die ausgedrückte Unsicherheit gebunden ist, die es bei HOF nicht gibt. Die andere Lesart wäre: Stricker anerkannt **und** Anonym bleibt. Setz die erste um, nenne die Wahl im PR ausdrücklich, und der Abnahme-Ping stellt KZW genau diese Frage. Ist sie falsch, ist es ein Einzeiler.

## 8. Vorab entschieden, nicht neu zu verhandeln

Die Entscheidungen oben; nicht mergen, kein Ticket schließen, relabeln in derselben Session. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination, die ihn als Kommentar in #452 festhält, nicht in den PR-Text.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig und HEAD gegen die Angaben aus 4, dazu der Commit des gelesenen Betriebsvertrags und ob die abgelegte Kickoff-Fassung übereinstimmt; das Ergebnis von Z1 **sofort**; die Stellenliste aus Z3; Test oder Chrome angefordert und frei; **Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes** (Commit oder `git stash create`); „PR N bereit zum Merge“ mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; fehlender Agententyp; der Haltepunkt in Z1.

**Externer Zustand** (CI): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Auf einem Daten-PR ist der Review-Bot oft rot: den Kommentar trotzdem lesen (`CLAUDE.md` → Git Rules) und Verhaltensbefunde beantworten, bevor du „bereit zum Merge“ meldest. Danach wartest du auf die Merge-Meldung der Koordination.

**Du darfst ein Paket für nicht durchführbar erklären**, mit Messung und früh; dann das nächste. Das ist etwas anderes als die Abbruchklausel in 3, die den ganzen Auftrag betrifft.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Laden über `ToolSearch` mit `select:PushNotification`; siehe `rules/blockaden-melden.md`. Dazu eine Meldung an die Koordination. **Eine Blockade wird nicht über eine andere Spur oder die Koordination umgangen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss

1. Data-Change-Lifecycle mit allen Gates (`check-index-versions.py`, `check-index-version-bump.py --base origin/main`, `check-variants-flips.py --base origin/main`, `check-authority-cross-refs.py --check`, `validate-corpus.py` für die fünf Sigel, `validate-indices.py`), `check-no-em-dash.py --diff-base origin/main`, `build-pages.py --check`, `doc-count-audit.py --check`, `npm run build:css` bei neuen Klassen.
2. `npm test` auf Port 8083 mit `-- --workers=2`, **nach Freigabe durch die Koordination**; das Ergebnis ist die **VERDICT-Zeile**, nie durch eine Pipe, nie `npx playwright test`. Chrome-Verifikation an CR, BAX, HOF und RHB in Leseansicht und Personenansicht, hart neu geladen (der Index wird im Browser zwischengespeichert).
3. `fable-reviewer` **vor dem ersten Push**: Zweig, Basis, ob ein Commit oder der uncommittete Arbeitsbaum geprüft wird, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde und ihr Umgang, **und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?** (Hier besonders: jede Stelle, die heute „erster `<author>`“ als „der Autor“ liest.) Bei Befunden eine weitere Runde. Den Arbeitsbaum still halten, solange sie läuft.
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt“, „Rote Zeilen“ und „Was zurück an Christian geht“.
5. PR öffnen mit „Bezug: #452, #444, bleiben offen“ (kein Closing-Keyword: die Abnahme steht aus), **nicht mergen**; „bereit zum Merge“ an die Koordination. Den Abnahme-Ping schreibst du nach der Merge-Meldung an @wachauer allein, weil Zuschreibungen tiefes Fachwissen brauchen (`CLAUDE.md` → Working an Issue), mit Live-URLs, Prüfschritten und der HOF/VDH-Frage aus 7.

### Definition of Done, als Lesertest

Wer nur den PR liest, kann beantworten: wie der Status kodiert ist (mit Beispiel aus `works.xml`); welcher Autor jetzt bei CR, BAX, HOF, VDH und RHB angezeigt wird und mit welchem Hinweis; wo die Rolle Bearbeiter erscheint; welche Stellen im Code bisher „erster Autor“ lasen und was sie jetzt tun; welche Tests das festhalten; was offen bleibt und bei wem.

**In diesem Kickoff gibt es keine Notationsfallen**, die über die Hinweise in den Paketen hinausgehen.
