# Kickoff Spur `spur-93-textreihen`: Umzug der Textreihentypologie (#93)

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 09.10.2026.

**1. Autorisierung.** chsteiner hat am 09.10.2026 im Gespräch mit der Koordination entschieden, #93 als eigene Spur laufen zu lassen, parallel zu einem kleinen Daten-PR der Koordination. Den Umfang hat @wachauer am 08.10.2026 im Thread von #93 festgelegt (Kommentar von 13:15 UTC). **Dieser Text ist die Autorisierung**: Commits und Pushes auf deinen eigenen `claude/*`-Zweig, einen PR öffnen, in #93 höchstens ein Statuskommentar und ein Relabel, Lesen der alten Website `https://www.marketext.at/Textreihentypologie/` und des Repos `Middle-High-German-Conceptual-Database/textseries` (beides öffentlich, beides ausdrücklich Gegenstand des Auftrags). **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen, Externe ansprechen (auch Marco Heiles nicht, KZW hält das für unnötig). Der Text erteilt keine technische Berechtigung: Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9).

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: Ein Sessionname kann beim Antworten längst einer anderen Session gehören. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees
2. `docs/playbooks/BETRIEBSVERTRAG.md` (gelesen, nicht kopiert; nenne in deiner ersten Meldung den Commit, an dem du ihn gelesen hast)
3. Diese Datei als abgelegte Fassung, `docs/playbooks/kickoffs/2026-10-09-spur-93-textreihen.md`. Sag in deiner ersten Meldung, ob sie mit der zugestellten übereinstimmt.
4. **#93 mit allen Kommentaren** (`gh issue view 93 --json title,body,comments`). Der Auftrag steht im letzten Kommentar von @wachauer, die Datenlage im Kommentar vom 10.08. Beide lesen, nicht nur den Body.
5. **#361** mit Kommentaren: dort ist die Baumansicht des bestehenden Gattungs-Explorers entstanden (transitive Reduktion, `genre.parents[]`). Das Muster für Mehrfacheltern gibt es also schon im Repo.
6. `docs/DESIGN.md`, `docs/DEVELOPMENT.md` (Abschnitte zu `build-pages.py` und zu den Tests) und `docs/ARCHITECTURE.md` zum Gattungs-Explorer
7. `includes/` und `scripts/build-pages.py`: Nav und Footer sind build-injiziert und werden nie in einer Seite von Hand geändert.

**Besonders tragen für dich:** Heroicons inline SVG als einziger Icon-Stil, keine Emoji-Icons; deutsche Oberfläche mit echten Umlauten und geraden Anführungszeichen; keine Em-Dashes (das Gate prüft HTML, JS und CSS vollständig); keine CDN-Abhängigkeit (`no-cdn-check.yml`); `python scripts/build-pages.py --check` bei HTML; `npm run build:css` bei neuen Utility-Klassen; Chrome-Verifikation am echten Inhalt, hart neu geladen; Desktop-only, min. 1200 px.

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit legt ihn mit `claude --bg --worktree spur-93-textreihen --name spur-93-textreihen --model sonnet --effort medium` an: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\spur-93-textreihen`, Zweig `worktree-spur-93-textreihen`. Die Begleitnachricht nennt den erwarteten HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen diese Angaben halten und melden. Bei Abweichung nichts ändern, melden, auf den Neustart durch die Koordination warten. Dann die Basis messen: `git fetch --quiet origin`, `git rev-list --count "origin/main...HEAD"` muss 0 sein. Arbeitszweig `claude/93-textreihen`, frisch von `origin/main`. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

**Dir allein:** ein neues Verzeichnis für die Unterseite (Name nach Messung, Vorschlag `textreihen/`), alles darin einschließlich der übernommenen SKOS-Daten und ihrer README; ein neues Build-Skript unter `scripts/` (nicht `scripts/audit/`), falls die SKOS-Daten für den Browser umgeformt werden müssen; neue Specs unter `testing/tests/`; in `includes/` nur der eine Footer-Link, den der Auftrag verlangt; die Kachel auf der Hilfe-Übersicht und eine Erwähnung im Gattungs-Explorer, falls du einen Rückverweis für nötig hältst; in `docs/FEATURES.md`, `docs/ARCHITECTURE.md` und `docs/DEVELOPMENT.md` nur die Absätze und Inventarzeilen zur neuen Unterseite.

**Nicht deins:** `tei/`, `authority-files/` (insbesondere `genres.xml`: **kein Abgleich**, KZW schließt ihn ausdrücklich aus), `data/`, `api/`, `schema/`, alle Versionsliterale, `scripts/build-*-index.py`, der bestehende Gattungs-Explorer bis auf einen Link. Die Koordination hat parallel einen Daten-PR offen, der genau die Daten- und Versionsdateien berührt. **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend, als **letzter Commit** des PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 109 bis 113**, die Koordination nimmt 114 aufwärts. Reviewer-Memory unter `.claude/agent-memory/fable-reviewer/` in einem eigenen Commit nach der Runde.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push außer `--force-with-lease` auf deinem eigenen `claude/*`-Zweig nach einem Rebase, keine Änderung unter `~/.claude/`.

**Maschinenweit exklusiv: volle Testläufe und Chrome.** Die Koordination vergibt beides, einer zur Zeit. **Anfordern, auf die Freigabe warten, nutzen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8082` und `-- --workers=2`, auch bei `test:quick` und `test:changed`; den Dev-Server für Chrome startest du auf 8082 und nur für die Dauer der Prüfung. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis: nicht deuten, melden, nach Freigabe wiederholen.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` vor dem ersten Push ist Pflicht; nicht auf `fable-advisor` ausweichen.

## 6. Was eingefroren ist

`CLAUDE.md`; `docs/playbooks/`; `.github/workflows/`; `scripts/audit/`. **Inbox:** eine Nachricht an die Koordination. **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum; die Koordination trägt ein. **Grund:** Ändert eine Spur eine Datei, die jede Session beim Start lädt, arbeiten andere ab dann unter geänderten Regeln, ohne es zu merken; am 01.09.2026 ist genau das passiert. Verlangt ein Gate unter `scripts/audit/` eine Änderung (etwa eine Inventarliste), schickst du den Wortlaut.

---

## 7. Die Pakete, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach, auch die, die deinen Befund stützen, und meldest einen Widerspruch. Die Zahlen unten stammen aus dem Kommentar vom 10.08. in #93 und sind von der Koordination heute **nicht** nachgemessen. **Keine Labelabfrage als Arbeitsgrundlage.**

**Reihenfolge begründet:** P1 zuerst, weil seine Rechtefrage über alles andere entscheidet; ist sie ungeklärt, wäre jede weitere Stunde für eine Seite, die nicht live gehen darf.

- **P1, Bestand und Rechte (messen, nichts bauen).** Die alte Website vollständig erfassen: jede Seite, jeder interne Link, jede Datei zum Download, Bibliografie, Autorennennung (laut Kommentar 10.08. Katharina Zeppezauer-Wachauer und Marco Heiles), Förderhinweise und Logos (laut demselben Kommentar DFG, CSMC, UWA Hamburg). Im Repo `textseries` den Commit festhalten, den du übernimmst (laut Kommentar letzter Commit 2023-05-24, 618 Konzepte, 881 direkte `broader`). **Nutzungsbedingungen:** was die alte Website und das Repo dazu sagen (laut Kommentar hat das Repo keine Lizenzdatei). **Sofort an die Koordination:** die Seitenliste mit Zahl, der übernommene Commit, und je Bestandteil (Texte, SKOS-Daten, Logos, Bibliografie) die Rechtelage mit Fundstelle. **Haltepunkt:** ein Bestandteil, dessen Übernahmerecht konkret ungeklärt ist (KZW: „nur konkrete ungeklärte Übernahmerechte zurückmelden"). Das Fehlen einer Lizenzdatei allein ist noch keine konkrete Unklarheit, wenn Website oder Repo die Bedingungen anders nennen; im Zweifel melden, nicht entscheiden.
- **P2, Unterseite mit allen Inhalten.** Alle bisherigen Inhalte erreichbar, Publikationsbezüge, Autorennennung und Förderhinweise erhalten. Historische URIs (`dhplus.sbg.ac.at/...`) bleiben als Identifikatoren stehen, werden aber nicht als Links vorausgesetzt (die Domain löst laut Kommentar nicht auf; nachmessen).
- **P3, „Visualization & Browser" neu.** Aufklappbare Hierarchie aus den SKOS-Daten des übernommenen Commits, mit Suche und Kategorieinformationen. Kategorien mit mehreren direkten Eltern erscheinen unter **allen** passenden Eltern. Navigation funktioniert lokal, ohne erreichbare dhplus-Adressen.
- **P4, Erklärung und Verlinkung.** README der übernommenen Daten und ein Abschnitt „Gattungs-Explorer in MHDBDB Next" auf der Unterseite: die MHDBDB führt die Typologie inzwischen in `authority-files/genres.xml` als eigenständig gepflegten TEI-Datenstand; Mehrfacheinordnungen bleiben möglich; die Datenstände sind nicht identisch; Link zum aktuellen Gattungs-Explorer. Erreichbar über Footer-Link und Hilfe-Kachel, kein neuer Menüpunkt. Das ist **nicht** von KZW entschieden, sondern ein Vorschlag der Koordination nach dem Muster, das chsteiner am 09.10. für #417 entschieden hat; widersprich, wenn der Bestand etwas anderes nahelegt.

**Eine Vorgabe, die die Koordination selbst für schwach hält, mit Ersatzfassung:** „README" im Auftrag von KZW ist mehrdeutig (README der übernommenen Daten oder `README.md` des Repositoriums). Gelesen ist es hier als README im Verzeichnis der Unterseite. Hältst du die andere Lesart für richtig, ergänze statt dessen einen Absatz im Repo-README und sag es im PR.

## 8. Vorab entschieden, nicht neu zu verhandeln

Kein Vokabularabgleich mit `genres.xml`; Datenbasis sind die ursprünglichen SKOS-Datensätze; keine Abstimmung mit Marco Heiles; nicht mergen, kein Ticket schließen, relabeln in derselben Session. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination, die ihn als Kommentar in #93 festhält, nicht in den PR-Text.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig und HEAD gegen die Angaben aus 4, dazu der Commit des gelesenen Betriebsvertrags und ob die abgelegte Kickoff-Fassung übereinstimmt; das Ergebnis von P1, **sofort**; Test oder Chrome angefordert und frei; **Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes** (Commit oder `git stash create`); „PR N bereit zum Merge" mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; fehlender Agententyp; der Haltepunkt in P1.

**Externer Zustand** (CI): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Den Kommentar des `claude-review`-Bots liest du und beantwortest Verhaltensbefunde, bevor du „bereit zum Merge" meldest. Danach wartest du auf die Merge-Meldung der Koordination.

**Du darfst ein Paket für nicht durchführbar erklären**, mit Messung und früh; dann das nächste. Das ist etwas anderes als die Abbruchklausel in 3, die den ganzen Auftrag betrifft.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Laden über `ToolSearch` mit `select:PushNotification`; siehe `rules/blockaden-melden.md`. Dazu eine Meldung an die Koordination. **Eine Blockade wird nicht über eine andere Spur oder die Koordination umgangen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss

1. `check-no-em-dash.py --diff-base origin/main`, `build-pages.py --check`, `doc-count-audit.py --check`, `check-doc-inventories.py`, `npm run build:css` bei neuen Klassen.
2. Alle internen Links und Downloads der Unterseite geprüft (Skript oder Spec, nicht Augenschein), dazu `npm test` auf Port 8082 mit `-- --workers=2`, **nach Freigabe durch die Koordination**; das Ergebnis ist die **VERDICT-Zeile**, nie durch eine Pipe, nie `npx playwright test`. Chrome-Verifikation am Baum mit einer Kategorie mit mehreren direkten Eltern und mit der Suche, hart neu geladen.
3. `fable-reviewer` **vor dem ersten Push**: Zweig, Basis, ob ein Commit oder der uncommittete Arbeitsbaum geprüft wird, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde und ihr Umgang, **und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?** Bei Befunden eine weitere Runde. Den Arbeitsbaum still halten, solange sie läuft.
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt", „Rote Zeilen" und „Was zurück an Christian geht".
5. PR öffnen mit „Bezug: #93, bleibt offen" (kein Closing-Keyword: die Abnahme steht aus), **nicht mergen**; „bereit zum Merge" an die Koordination. Den Abnahme-Ping schreibst du nach der Merge-Meldung: zuerst an @juliahin, @wachauer mitgenannt (`CLAUDE.md` → Working an Issue), Live-URL und Prüfschritte.

### Definition of Done, als Lesertest

Wer nur den PR liest, kann beantworten: welche Seiten und Dateien der alten Website übernommen sind, gezählt, und dass keine fehlt; welcher SKOS-Commit die Datenbasis ist; wie die Rechtelage je Bestandteil aussieht und wo sie belegt ist; wie der Baum Mehrfacheltern zeigt (Beispielkategorie); welche Tests Links, Downloads und Baum festhalten; was offen bleibt und bei wem.

**In diesem Kickoff gibt es keine Notationsfallen**, die über die Hinweise in den Paketen hinausgehen.
