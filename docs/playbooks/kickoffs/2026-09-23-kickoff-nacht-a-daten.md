# Kickoff Spur A `nacht-daten`: Datenarbeit der Nacht, seriell

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Nachtlauf vom 23./24.09.2026.

**1. Autorisierung.** chsteiner hat diesen Lauf am 23.09.2026 abends freigegeben und schläft. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deinen eigenen Zweig, PRs öffnen, höchstens ein Statuskommentar und ein Relabel je Vorgang, den du anfasst; Fragen an KZW oder Christian stehen in diesem Statuskommentar. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen, Externe außerhalb von Issue-Kommentaren kontaktieren. Der Text erteilt keine technische Berechtigung: was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9). `auto:checkin` heißt heute Nacht **nicht** fragen und warten: niemand antwortet. Was eine Entscheidung braucht, die nicht im Thread steht, baust du nicht, sondern schreibst es als Frage in den Statuskommentar.

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: ein Sessionname kann beim Antworten längst einer anderen Session gehören. Die Koordination ist die ganze Nacht wach und antwortet in Minuten.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees
2. `docs/playbooks/BETRIEBSVERTRAG.md`
3. `docs/playbooks/kickoffs/2026-09-23-nachtlauf.md`, der Laufplan, **ganz**; besonders §1 (liegengebliebener Stand), §2 Spur A, §3 Dateibesitz, §4 Freeze
4. `docs/playbooks/kickoffs/2026-09-23-issue-abbau.md` §2 Spur A (A2) und „Grenzverhandlungen": dort stehen die Entscheidungen, auf denen dein Paket A1 aufsetzt
5. `docs/DATA-MODEL.md` → Data-Change-Lifecycle
6. **#267, #252, #270, #357, #228 mit allen Kommentaren** (`gh issue view N --json title,body,comments`). Die Entscheidungen von @wachauer stehen ausschließlich im Thread
7. `docs/DECISIONS.md` ADR-018; als Skriptmuster `scripts/ingest/pos-disambig/apply-387-418-464.py` (Trefferzahl je Ersetzung, Ist-Zustand je Token vor dem Schreiben prüfen, Abbruch bei Abweichung)

**Besonders tragen für dich:** Data-Change-Lifecycle vollständig; neue Variantentypen prägen, nie umhängen (Regel aus #367); `extract-variants.py` ohne `--apply` vor und nach jedem Korpuslauf, die Differenz muss erklärbar sein; ein Skript, das eine Datei serialisiert, darf nichts außerhalb der gemeinten Stellen ändern (Diff je Datei prüfen). **Und die Regeln, die dein Ergebnis binden:** keine Em-Dashes, echte Umlaute, gerade Anführungszeichen im Frontend, keine Emoji-Icons; `python scripts/build-pages.py --check` bei HTML; `npm run build:css` bei neuen Klassen; Hilfeseiten ziehen mit, wenn sich Verhalten ändert.

**Abbruchklausel:** weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit hat ihn mit `claude --bg --worktree nacht-daten --name nacht-daten` angelegt: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\nacht-daten`, Zweig `worktree-nacht-daten`; die Begleitnachricht nennt den HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen die Angaben halten, melden, zusammen mit dem Commit des gelesenen Laufplans. Bei Abweichung nichts ändern, melden, auf Neustart warten. Dann die Basis messen (`git fetch --quiet origin`, `git rev-list --count "origin/main...HEAD"` muss 0 sein). **Je Paket ein eigener Arbeitszweig** `claude/nacht-a1-267-252`, `claude/nacht-a2-270`, `claude/nacht-a3-357`, `claude/nacht-a4-228`, jeder frisch von `origin/main` **nach** dem Merge des vorigen. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

**Dir allein:** `tei/`, `authority-files/`, `data/` außer `data/naming-index.json.gz`, `api/`, `scripts/build-*.py`, `scripts/ingest/` außer `scripts/ingest/naming/`, `ingest/`; die Versionsliterale (`build-corpus-index.py`, `build-authority-index.py`, `assets/js/lib/corpus-loader.js`, `docs/TEI-MODEL.md` §11, Versionszeile in `docs/INDEX.md`); zeilengenau die von `scripts/audit/doc-count-audit.py` gegateten Zahlzeilen, wo immer sie stehen; für A2 `lemma/` und `playground/js/ui/authority/lemma-explorer.js` sowie weitere Render-Stellen, die du nach Messung benennst und der Koordination meldest, **bevor** du sie änderst; `docs/DECISIONS.md` ADR-018; `docs/TEI-MODEL.md` und `docs/POS-TAGSET.md` nur an den Stellen, die A1 und A4 verlangen; für A1 die eine Kommentarzeile `assets/js/rendering/tei-text-reader.js:772`, `sources/README.md` Z. 182–191 als ganzer Absatz und in `scripts/README.md` der Absatz zu `ingest/` (neue Ingest-Ordner **nicht** in den Verzeichnisbaum schreiben, sonst meldet `check-doc-inventories.py` „genannt, nicht vorhanden"); für A2 eine neue Spec.

**Mit Spur B geteilt, abschnittsweise:** `hilfe-korpussuche.html` nur in §6 „Lemma-Seite", Listenpunkt „Bedeutungen"; übrige `hilfe-*.html` und `docs/FEATURES.md` nur im Absatz zur Lemma-Seite und zu kuratierten Lemma-Angaben. Vorher `origin/main` holen.

**Nicht deins:** `data/naming-index.json.gz`, `scripts/ingest/naming/`, **die Note `authority-files/contributors.xml:191`** (Naming-Zitation, gehört in dieser Nacht Spur B), `playground/` und `assets/js/` außer den A-Stellen, `woerterbuch.html`, `index.html`, `korpus.html` (alles Spur B); `docs/DEVELOPMENT.md` (nur die Koordination; verlangt `check-doc-inventories.py` eine Zeile für deine neue Spec, schickst du den Wortlaut). **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend, als **letzter Commit** des PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 80 bis 84.** Reviewer-Memory in einer eigenen Datei unter `.claude/agent-memory/fable-reviewer/`, eigener Commit nach der Runde.

**Der liegengebliebene Stand des Tageslaufs** liegt im Hauptbaum unter `.claude/tmp/sicherung-2026-09-23/` (`daten2-a2-uncommitted.patch`, `daten2-untracked.tar` mit `scripts/ingest/gap-252/` und `scripts/ingest/no-print-267/`) und unverändert im Worktree `.claude/worktrees/mhdbdb-daten2`. **Lesen darfst du beides, schreiben in keines.** Den Patch wendest du nicht an.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push auf gepushte Historie, keine Änderung unter `~/.claude/`.

**Maschinenweit exklusiv: Volläufe.** Die Koordination vergibt sie, einer zur Zeit, du hast Vorrang. **Anfordern, warten auf die Freigabe, laufen lassen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8081` und `-- --workers=2`, auch bei `test:quick` und `test:changed`. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis: nicht deuten, melden, nach Freigabe wiederholen. Dev-Server nur für die Dauer einer Chrome-Prüfung, auf 8081. **Indexversionen:** allein du; die Nummer fragst du vor dem Bump bei der Koordination an. **`--allow-dirty`:** die `build-*.py` verweigern einen unsauberen Baum, der Lifecycle verlangt den gemeinsamen Commit; kein `git stash` als Ausweg.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` vor dem ersten Push ist Pflicht; nicht auf `fable-advisor` ausweichen.

## 6. Was eingefroren ist

`CLAUDE.md`; die 15 promptotyping-Dokumente in `docs/` außer `docs/JOURNAL.md` und den Ausnahmen in 5; `docs/playbooks/`; `.github/workflows/`; `scripts/audit/`; `scripts/README.md` außer deinem `ingest/`-Absatz; `docs/DEVELOPMENT.md`. **Inbox:** Abschnitt „Änderungswünsche" am Ende des Laufplans. **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum; sofort an die Koordination. **Grund:** ändert eine Spur eine Datei, die jede Session beim Start lädt, arbeiten die anderen unter geänderten Regeln, ohne es zu merken.

---

## 7. Die Pakete, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach, auch die, die deinen Befund stützen, und meldest einen Widerspruch. Was im Laufplan „(K)" trägt, hat die Koordination geprüft; alles andere ist ungeprüft. **Keine Labelabfrage als Arbeitsgrundlage.**

**Reihenfolge begründet:** A1 zuerst, weil halbfertige Korpusarbeit in einem verwaisten Baum der teuerste Zustand ist, den der Lauf hat; A2 danach, weil KZWs Entscheidung von heute Mittag ist und die Authority-Seite berührt; A3 klein; A4 das größte Paket, nur wenn Zeit bleibt.

- **A1, #252 und #267.** Laufplan §2 A1 und §1 Punkt 1. **#252 ist zur Hälfte da, #267 gar nicht**: der Patch enthält nur die 846 `<gap>`-Ersetzungen (FR1s 2.081 Diffzeilen sind 520 Ersetzungen zu je vier Zeilen, erklärt). #252: das Skript aus der Sicherung lesen, frisch auf `origin/main` laufen lassen, Ergebnis gegen den Patch vergleichen; **Kontrollwert** die 20 Zahlen je Datei aus §1 des Laufplans, Summe 846. Die fünf NEIM-Stellen gehören dazu. #267: vollständig bauen, das untracked Skript ist Material. **Entschieden:** der neue Header-Satz und die Marker (KZW 10.09.), FR3 bekommt das Standard-`<availability>` (Grenzverhandlung Tageslauf), die 846 Stellen in #252 (KZW 22.09.). **Nicht freigegeben:** die fünf Komma- und Doppelpunktfälle. **Haltepunkt:** eine Zahl weicht vom Kontrollwert oder vom Thread ab (dann xml:ids melden, nicht Anzahlen).
- **A2, #270.** Laufplan §2 A2. **Entschieden:** der Name des Urhebers am **Kommentar**, Lemma-Seite und Playground, ADR-018 aktualisieren. **Nicht entschieden:** dieselbe Anzeige an `<def>` und `<etym>`; das geht als Frage in den Statuskommentar. Zuerst alle Render- und Lesestellen auflisten (Grep über JS **und** HTML) und der Koordination melden.
- **A3, #357.** Laufplan §2 A3. **Entschieden:** zweiter Sense für Menschennamen an `lemma_3036`, kein neues Lemma. **Nachzumessen:** das Konzept der Nachbarn im selben Rennewart-Namenkatalog (laut Planreview `lemma_22280`, `lemma_22282`, `lemma_22283`); tragen sie ein gemeinsames für Menschennamen, ist es das, mit Messung im PR; sonst Haltepunkt und Frage an KZW. „Das gilt für alle Namen" ist kein Auftrag für einen Korpuslauf.
- **A4, #228, nur wenn A1 bis A3 gemergt sind.** Laufplan §2 A4. Reserve, im Morgenbericht kein Rückstand. **Haltepunkte bindend: kein `<note>`-Eingriff in `tei/NEIM.tei.xml`; ein zu löschendes Lemma, auf das eine andere Authority-Datei verweist, wird nicht gelöscht, sondern mit xml:id gemeldet.**

**Eine Vorgabe, die die Koordination selbst für schwach hält, mit Ersatzfassung:** #252 frisch zu erzeugen, statt den Patch zu übernehmen, kostet Zeit. Zeigt dein Vergleich, dass das Skript auf `origin/main` genau den Patch erzeugt, ist das der Beleg; kannst du das Skript nicht sauber laufen lassen, darfst du die `tei/`-Hunks des Patches übernehmen, wenn sie gegen `origin/main` konfliktfrei sind und den Kontrollwert treffen, und sagst es mit dem Vergleich im PR.

## 8. Vorab entschieden, nicht neu zu verhandeln

Die Tabelle in §6 des Laufplans; für dich besonders: nicht mergen, kein Ticket schließen, relabeln in derselben Session, Bump-Nummer von der Koordination. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination, die ihn unter „Grenzverhandlungen" im Laufplan einträgt, nicht in den PR-Text.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`/Zweig/HEAD nach dem Lesen; je Paket der nachgemessene Umfang gegen den behaupteten; Test angefordert und frei; Beginn und Ergebnis jeder Reviewrunde mit Rundennummer **und Kennung des geprüften Standes**; „PR N bereit zum Merge" mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; Stoppbedingung aus dem Laufplan; fehlender Agententyp; die Haltepunkte in A1, A3 und A4.

**Externer Zustand** (CI): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Den Kommentar des `claude-review`-Bots liest du und beantwortest Verhaltensbefunde, bevor du „bereit zum Merge" meldest; ein roter Haken auf einem Daten-PR ist laut `CLAUDE.md` kein Befund und keine Entwarnung. Nach deiner Meldung „bereit zum Merge" wartest du auf die Merge-Meldung der Koordination, bevor du das nächste Paket von `origin/main` abzweigst.

**Du darfst ein Paket für nicht durchführbar erklären**, mit Messung und früh; dann das nächste. Das ist etwas anderes als die Abbruchklausel in 3, die den ganzen Auftrag betrifft.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Laden über `ToolSearch` mit `select:PushNotification`. `rules/blockaden-melden.md`. Dazu eine Meldung an die Koordination. **Nicht über eine andere Spur oder die Koordination umgehen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss je Paket

1. Lifecycle vollständig: `extract-variants.py --apply` wo Korpus berührt, beide Indexe, `build-api.py`, Bump an allen Stellen, `check-index-versions.py`, `doc-count-audit.py --check`, `check-no-em-dash.py --diff-base origin/main`, `build-pages.py --check`.
2. `npm test` auf Port 8081 mit `-- --workers=2`, **nach Freigabe durch die Koordination**, Ergebnis ist die **VERDICT-Zeile**; nie durch eine Pipe, nie `npx playwright test`. Chrome-Verifikation bei UI (A2), hart neu geladen.
3. `fable-reviewer` **vor dem ersten Push**: Zweig, Basis, Commit, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde, **und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?** Bei Befunden eine weitere Runde. Arbeitsbaum still halten, solange sie läuft.
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt", „Rote Zeilen" (deine Zeile aus `python C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\claude-code-setup\hooks\trockenlauf-auswerten.py`), „Was zurück an Christian geht". Ein Eintrag je PR genügt.
5. PR öffnen, **nicht mergen**; Statuskommentar und Relabel je Vorgang; „bereit zum Merge" an die Koordination.

### Definition of Done, als Lesertest

Wer nur den PR liest, kann beantworten: welche Tokens und Header sich geändert haben, gezählt und gegen die freigegebene Zahl gehalten; welche Differenz `extract-variants.py` zeigt und warum; welche Tests das festhalten; was offen bleibt und bei wem.
