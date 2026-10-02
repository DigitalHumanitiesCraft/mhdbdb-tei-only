# Kickoff Spur A `lauf-a-daten`: Datenarbeit, seriell

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 02.10.2026.

**1. Autorisierung.** chsteiner hat diesen Lauf am 02.10.2026 freigegeben, im Gespräch mit der Koordination; der Wortlaut der Freigaben steht im Kopf des Laufplans. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deine eigenen Zweige, PRs öffnen, je angefasstem Vorgang höchstens ein Statuskommentar und ein Relabel. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen, Externe außerhalb von Issue-Kommentaren ansprechen. Der Text erteilt keine technische Berechtigung: Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9). `auto:checkin` heißt in diesem Lauf: Entscheidungspunkte gehen an die Koordination, nicht an KZW, und du wartest auf ihre Antwort, sie kommt in Minuten.

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: Ein Sessionname kann beim Antworten längst einer anderen Session gehören. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees
2. `docs/playbooks/BETRIEBSVERTRAG.md` (wird hier nicht kopiert, sondern gelesen; nenne in deiner ersten Meldung den Commit, an dem du ihn gelesen hast)
3. `docs/playbooks/kickoffs/2026-10-02-lauf.md`, der Laufplan, **ganz**; besonders §1 bis §5. Sag in deiner ersten Meldung, ob die dort abgelegte Fassung dieses Kickoffs (`2026-10-02-kickoff-a-daten.md`) mit der zugestellten übereinstimmt.
4. `docs/DATA-MODEL.md` → Data-Change-Lifecycle und Ingest procedure
5. `docs/CONTRACTS.md` §C (ganz, mit C.1.1 und C.1.2) und `docs/DECISIONS.md` ADR-021
6. **#378, #370 und #358 mit allen Kommentaren** (`gh issue view N --json title,body,comments`). Die Entscheidungen von @wachauer stehen nur im Thread.
7. Als Skriptmuster `scripts/ingest/pos-disambig/apply-387-418-464.py` (Trefferzahl je Ersetzung, Ist-Zustand je Token vor dem Schreiben prüfen, Abbruch bei Abweichung) und für Variantentypen den PR zu `573894f12` (#456, zehn Typen geprägt)

**Besonders tragen für dich:** der Data-Change-Lifecycle vollständig; neue Variantentypen prägen, nie umhängen (#367); `extract-variants.py` ohne `--apply` vor und nach jedem Korpuslauf, und die Differenz muss erklärbar sein; ein Skript, das eine Datei serialisiert, ändert nichts außerhalb der gemeinten Stellen (Diff je Datei prüfen); ein Index-Bump nur bei Inhaltsänderung (#370, Kommentar vom 31.08.). **Regeln, die dein Ergebnis binden:** keine Em-Dashes, echte Umlaute, gerade Anführungszeichen im Frontend, keine Emoji-Icons; `python scripts/build-pages.py --check` bei HTML; `npm run build:css` bei neuen Utility-Klassen.

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit hat ihn mit `claude --bg --worktree lauf-a-daten --name lauf-a-daten --model sonnet --effort medium` angelegt: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\lauf-a-daten`, Zweig `worktree-lauf-a-daten`. Die Begleitnachricht nennt den erwarteten HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen diese Angaben halten und melden. Bei Abweichung nichts ändern, melden, auf den Neustart durch die Koordination warten. Dann die Basis messen: `git fetch --quiet origin`, `git rev-list --count "origin/main...HEAD"` muss 0 sein. **Je Paket ein eigener Arbeitszweig**, `claude/lauf-a1-378`, `claude/lauf-a2-370`, `claude/lauf-a3-358`, jeder frisch von `origin/main` **nach** dem Merge des vorigen. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

**Dir allein** (Laufplan §3): `tei/`, `authority-files/`, `data/` außer `naming-index.json.gz` und `horses-index.json.gz`, `api/`, `scripts/build-*.py`, `scripts/ingest/`, `schema/`; alle Versionsliterale (`build-corpus-index.py`, `build-authority-index.py`, `assets/js/lib/corpus-loader.js`, `docs/TEI-MODEL.md` §11, Versionszeile in `docs/INDEX.md`) und zeilengenau die von `scripts/audit/doc-count-audit.py` gegateten Zahlzeilen; die Lemma-Auflösung in `assets/js/search/search-engine.js`, `assets/js/lib/lemma-resolve.js` und im Playground (**die Playground-Dateien benennst du nach Messung und meldest sie, bevor du sie änderst**); `docs/CONTRACTS.md` §C, `docs/DECISIONS.md` ADR-021, `docs/DATA-MODEL.md`, `docs/TEI-MODEL.md` an den Stellen, die A3 verlangt; eine neue Gate-Datei unter `scripts/audit/` und ihre eine Workflow-Zeile; neue Specs.

**Abschnittsweise geteilt:** `docs/FEATURES.md` nur in den Absätzen zur Lemma-Auflösung. Hilfeseiten gehören B: Was dort zur Lemmasuche zu ändern ist, schickst du als Wortlaut an die Koordination.

**Nicht deins:** `assets/js/woerterbuch.js`, `woerterbuch.html`, `lemma/`, `playground/js/ui/authority/lemma-explorer.js`, `assets/js/rendering/tei-text-reader.js`, alle `hilfe-*.html` (Spur B); `ingest/wzb/370-corresp/` außer dem Lesen, `ingest/parzival-buecher/`, `ingest/mur-228/`, `scripts/review/` (Spur C). **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend, als **letzter Commit** des PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 90 bis 94.** Reviewer-Memory in einer eigenen Datei unter `.claude/agent-memory/fable-reviewer/`, eigener Commit nach der Runde.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push auf gepushte Historie außer `--force-with-lease` auf deinem eigenen `claude/*`-Zweig nach einem Rebase, keine Änderung unter `~/.claude/`.

**Maschinenweit exklusiv: volle Testläufe.** Die Koordination vergibt sie, einer zur Zeit. **Anfordern, auf die Freigabe warten, laufen lassen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8081` und `-- --workers=2`, auch bei `test:quick` und `test:changed`. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis: nicht deuten, melden, nach Freigabe wiederholen. **Indexversionen:** allein du; die Nummer fragst du vor dem Bump bei der Koordination an. **`--allow-dirty`:** Die `build-*.py` verweigern einen unsauberen Baum, der Lifecycle verlangt den gemeinsamen Commit; kein `git stash` als Ausweg.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` vor dem ersten Push ist Pflicht; nicht auf `fable-advisor` ausweichen.

## 6. Was eingefroren ist

Laufplan §6, vollständig: `CLAUDE.md`; `docs/playbooks/`; `.github/workflows/` außer der einen Zeile für dein neues Gate; `scripts/audit/` außer deiner neuen Gate-Datei; die 15 promptotyping-Dokumente außer `docs/JOURNAL.md` und deinen Abschnitten aus 5; `docs/DEVELOPMENT.md`. **Inbox:** Abschnitt „Änderungswünsche“ am Ende des Laufplans. **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum; als Nachricht an die Koordination, die einträgt. **Grund:** Ändert eine Spur eine Datei, die jede Session beim Start lädt, arbeiten die anderen ab dann unter geänderten Regeln, ohne es zu merken. Am 01.09.2026 hat genau das eine Spur eine Nacht lang unter anderen Regeln arbeiten lassen.

---

## 7. Die Pakete, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach, auch die, die deinen Befund stützen, und meldest einen Widerspruch. Was im Laufplan „(K)“ trägt, hat die Koordination geprüft; alles andere ist ungeprüft. **Keine Labelabfrage als Arbeitsgrundlage.**

**Reihenfolge begründet:** A1 zuerst, weil A2 laut #370 (Kommentar vom 06.09. und KZW vom 14.09.) die Regel aus #378 braucht und weil B1 vielleicht ein Indexfeld von dir braucht, das in denselben Bump gehört. A2 danach, sobald C1 fertig ist. A3 zuletzt, weil C2 die Buchgrenzen erst belegen muss.

- **A1, #378.** **Entschieden** (KZW 14.09., ADR-021): normalisierte Form auf **alle** Kandidaten, sortiert nach Vorschrift B (Belege dieser normalisierten Form unter dem Lemma); beide Konsumenten geben mehrere Kandidaten aus; Hinweis im Frontend (Wortlaut-Vorschlag im Thread, Feinschliff erlaubt); das Gate, das meldet, wenn eine Änderung eine bestehende Zuordnung umschlagen lässt. **Nachzumessen, bevor du baust:** die vier Zahlen aus dem Ticketkopf (Vorschrift B: 4.972 umstritten, 2.064 bzw. 1.328) gegen den heutigen Stand, und die Zählweise (Tokenform oder Variantentyp, laut Ticket 1 bis 3 Fälle Abweichung) legst du fest und schreibst sie in §C. **Zuerst** listest du alle Lese- und Schreibstellen der `variants`-Abbildung auf (Python **und** JS, Hauptseite, Playground, API) und meldest sie, bevor du etwas änderst. **Haltepunkte:** ein Konsument, der strukturell nur ein Lemma tragen kann (etwa ein Chip, der genau eine ID hält): dann meldest du den Fall mit Vorschlag und wartest; ein Feldwunsch von B1, der noch nicht entschieden ist, wenn du bauen willst: dann fragst du.
- **A2, #370 Punkt 2, Einspielen.** **Erst nach dem Merge von A1 und wenn C1 `ingest/wzb/370-corresp/entscheidungen.csv` gemeldet hat.** Du spielst nur `ANLEGEN` und `ANDERE_ZUORDNUNG` ein, nicht `PRUEFSEITE` und nicht `NICHT_ANLEGEN`. **Vorher** prüfst du die Datei: 484 Zeilen, jede Zeile aus `offene-faelle.csv` genau einmal, keine Zeile ohne Begründung; eine Abweichung ist ein Haltepunkt. **Entschieden:** neue Typen prägen, nie umhängen; Validierung und Plausibilitätschecks über den ganzen Batch vor dem Data Change (KZW 14.09.); die Ratsche in `corresp-coverage-baseline.json` zieht mit. **Haltepunkt:** Ein Typ, den du prägen sollst, würde eine bestehende Zuordnung umschlagen lassen (dein Gate aus A1 meldet es): dann xml:ids und Formen melden.
- **A3, #358 TEI.** **Erst wenn C2 `ingest/parzival-buecher/grenzen.csv` gemeldet hat.** **Entschieden** (Laufplan §4): `subtype="dreissiger"` an allen `div type="chapter"` in PZ und WH, `<milestone unit="book" n="I"/>` … `n="XVI"` in PZ vor dem ersten `<l>` jedes Buchs, Schema um beides erweitert (geschlossene Werte), `docs/TEI-MODEL.md` beschreibt es. **Nachzumessen:** dass der Korpus-Index sich dadurch nicht ändert (bei WH war er nach `f50612a05` byte-identisch, #358 Kommentar vom 09.08.); ändert er sich, ist das ein Befund, kein Bump-Anlass ohne Rückfrage. **Haltepunkt:** Eine Buchgrenze aus C2 trifft kein `<l>` (dann Stelle und Wort-ID melden).

**Eine Vorgabe, die die Koordination selbst für schwach hält, mit Ersatzfassung:** Für A1 ist offen, ob der Playground mehrere Kandidaten überall darstellen kann. Wenn eine Stelle nur ein Lemma halten kann, darfst du dort den ersten Kandidaten nach Vorschrift B nehmen und die übrigen im Hinweis nennen, statt die Stelle umzubauen; sag dann im PR, welche Stelle das ist.

## 8. Vorab entschieden, nicht neu zu verhandeln

Laufplan §4 und §1. Für dich besonders: nicht mergen, kein Ticket schließen, relabeln in derselben Session, Bump-Nummer von der Koordination. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination, die ihn unter „Grenzverhandlungen“ im Laufplan einträgt, nicht in den PR-Text.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig und HEAD gegen die Angaben aus 4, dazu der Commit des gelesenen Betriebsvertrags und Laufplans und ob die abgelegte Kickoff-Fassung übereinstimmt; je Paket der nachgemessene Umfang gegen den behaupteten; Test angefordert und frei; **Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes** (Commit oder `git stash create`); „PR N bereit zum Merge“ mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; fehlender Agententyp; die Haltepunkte in A1 bis A3.

**Externer Zustand** (CI, die Meldung von C): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Den Kommentar des `claude-review`-Bots liest du und beantwortest Verhaltensbefunde, bevor du „bereit zum Merge“ meldest; ein roter Haken auf einem Daten-PR ist laut `CLAUDE.md` kein Befund und keine Entwarnung. Nach „bereit zum Merge“ wartest du auf die Merge-Meldung der Koordination, bevor du das nächste Paket von `origin/main` abzweigst.

**Du darfst ein Paket für nicht durchführbar erklären**, mit Messung und früh; dann das nächste. Das ist etwas anderes als die Abbruchklausel in 3, die den ganzen Auftrag betrifft.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Laden über `ToolSearch` mit `select:PushNotification`; siehe `rules/blockaden-melden.md`. Dazu eine Meldung an die Koordination. **Eine Blockade wird nicht über eine andere Spur oder die Koordination umgangen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss je Paket

1. Lifecycle vollständig: `extract-variants.py --apply`, wo der Korpus berührt ist, beide Indexe, `build-api.py`, Bump an allen Stellen, `check-index-versions.py`, `doc-count-audit.py --check`, `check-no-em-dash.py --diff-base origin/main`, `build-pages.py --check`, `validate-corpus.py` bei A3.
2. `npm test` auf Port 8081 mit `-- --workers=2`, **nach Freigabe durch die Koordination**; das Ergebnis ist die **VERDICT-Zeile**, nie durch eine Pipe, nie `npx playwright test`.
3. `fable-reviewer` **vor dem ersten Push**: Zweig, Basis, ob ein Commit oder der uncommittete Arbeitsbaum geprüft wird, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde und ihr Umgang, **und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?** Bei Befunden eine weitere Runde. Den Arbeitsbaum still halten, solange sie läuft.
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt“, „Rote Zeilen“ und „Was zurück an Christian geht“. Ein Eintrag je PR genügt.
5. PR öffnen, **nicht mergen**; Statuskommentar und Relabel je Vorgang; „bereit zum Merge“ an die Koordination.

### Definition of Done, als Lesertest

Wer nur den PR liest, kann beantworten: welche Abbildungen, Tokens oder Elemente sich geändert haben, gezählt und gegen die nachgemessene Ausgangszahl gehalten; welche Differenz `extract-variants.py` zeigt und warum; welche Tests das festhalten; was offen bleibt und bei wem.

**Notationsfalle:** In #370 und #378 stehen Zahlen wie „41“, „23“, „18“ für Paare, nicht für Issues; `lemma_N` und `type_N` sind IDs, keine Zählungen (in #378 hat eine Session am 06.09. aus einer Belegzahl eine Lemma-ID gemacht).
