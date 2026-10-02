# Kickoff Spur B `lauf-b-frontend`: Wörterbuch, Lemmaseiten, Leseansicht

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 02.10.2026.

**1. Autorisierung.** chsteiner hat diesen Lauf am 02.10.2026 freigegeben, im Gespräch mit der Koordination; der Wortlaut der Freigaben steht im Kopf des Laufplans. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deine eigenen Zweige, PRs öffnen, je angefasstem Vorgang höchstens ein Statuskommentar und ein Relabel. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen, Externe außerhalb von Issue-Kommentaren ansprechen. Der Text erteilt keine technische Berechtigung: Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9). `auto:checkin` heißt in diesem Lauf: Entscheidungspunkte gehen an die Koordination, nicht an KZW, und du wartest auf ihre Antwort, sie kommt in Minuten.

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: Ein Sessionname kann beim Antworten längst einer anderen Session gehören. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees
2. `docs/playbooks/BETRIEBSVERTRAG.md` (wird hier nicht kopiert, sondern gelesen; nenne in deiner ersten Meldung den Commit, an dem du ihn gelesen hast)
3. `docs/playbooks/kickoffs/2026-10-02-lauf.md`, der Laufplan, **ganz**; besonders §1 bis §4. Sag in deiner ersten Meldung, ob die dort abgelegte Fassung dieses Kickoffs (`2026-10-02-kickoff-b-frontend.md`) mit der zugestellten übereinstimmt.
4. **#228 und #358 mit allen Kommentaren** (`gh issue view N --json title,body,comments`). Die Entscheidungen von @wachauer stehen nur im Thread.
5. `docs/DESIGN.md` (Komponenten, Farben) und `docs/ARCHITECTURE.md` zum Wörterbuch, zur Lemmaseite und zur Leseansicht
6. `assets/js/rendering/tei-text-reader.js` Z. 590 bis 640 (div-Beschriftung, Rücksetzung der Verszählung; K: Z. 613 bis 617 halten die Labels, Z. 628 behandelt `chapter`)

**Besonders tragen für dich:** Heroicons inline SVG als einziger Icon-Stil, keine Emoji-Icons; deutsche Oberfläche mit echten Umlauten und geraden Anführungszeichen; keine Em-Dashes; Hilfeseiten ziehen mit, wenn sich sichtbares Verhalten ändert; `python scripts/build-pages.py --check` bei HTML; `npm run build:css` bei neuen Utility-Klassen; Chrome-Verifikation mit realen Belegen, hart neu geladen (der Index wird im Browser zwischengespeichert).

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit hat ihn mit `claude --bg --worktree lauf-b-frontend --name lauf-b-frontend --model sonnet --effort medium` angelegt: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\lauf-b-frontend`, Zweig `worktree-lauf-b-frontend`. Die Begleitnachricht nennt den erwarteten HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen diese Angaben halten und melden. Bei Abweichung nichts ändern, melden, auf den Neustart durch die Koordination warten. Dann die Basis messen: `git fetch --quiet origin`, `git rev-list --count "origin/main...HEAD"` muss 0 sein. **Je Paket ein eigener Arbeitszweig**, `claude/lauf-b1-228` und `claude/lauf-b2-358`, jeder frisch von `origin/main`. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

**Dir allein** (Laufplan §3): `woerterbuch.html`, `assets/js/woerterbuch.js`, `lemma/` (`lemma/lemma-page.js` und was dazu gehört), `playground/js/ui/authority/lemma-explorer.js`, in `assets/js/rendering/tei-text-reader.js` die div-Beschriftung und die Darstellung des neuen `milestone`, alle `hilfe-*.html`; neue Specs. Weitere Render-Stellen benennst du nach Messung und meldest sie der Koordination, **bevor** du sie änderst.

**Abschnittsweise geteilt:** `docs/FEATURES.md` nur in den Absätzen zu Wörterbuch, Lemmaseite und Leseansicht. Spur A schickt über die Koordination Wortlaute für die Hilfeseiten zur Lemmasuche; die trägst du ein.

**Nicht deins:** `tei/`, `authority-files/`, `data/`, `api/`, `schema/`, `scripts/` (außer dem Lesen), alle Versionsliterale, `assets/js/search/search-engine.js`, `assets/js/lib/lemma-resolve.js`, die Lemma-Auflösung im Playground, `docs/CONTRACTS.md`, `docs/DECISIONS.md`, `docs/DATA-MODEL.md`, `docs/TEI-MODEL.md` (alles Spur A); `ingest/` (Spur C). **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend, als **letzter Commit** des PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 95 bis 99.** Reviewer-Memory in einer eigenen Datei unter `.claude/agent-memory/fable-reviewer/`, eigener Commit nach der Runde.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push auf gepushte Historie außer `--force-with-lease` auf deinem eigenen `claude/*`-Zweig nach einem Rebase, keine Änderung unter `~/.claude/`.

**Maschinenweit exklusiv: volle Testläufe und Chrome.** Die Koordination vergibt beides, einer zur Zeit. **Anfordern, auf die Freigabe warten, nutzen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8082` und `-- --workers=2`, auch bei `test:quick` und `test:changed`; den Dev-Server für Chrome startest du auf 8082 und nur für die Dauer der Prüfung. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis: nicht deuten, melden, nach Freigabe wiederholen.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` vor dem ersten Push ist Pflicht; nicht auf `fable-advisor` ausweichen.

## 6. Was eingefroren ist

Laufplan §6, vollständig: `CLAUDE.md`; `docs/playbooks/`; `.github/workflows/`; `scripts/audit/`; die 15 promptotyping-Dokumente außer `docs/JOURNAL.md` und deinen Absätzen aus 5; `docs/DEVELOPMENT.md` (verlangt `check-doc-inventories.py` eine Zeile für deine neue Spec, schickst du den Wortlaut an die Koordination). **Inbox:** Abschnitt „Änderungswünsche“ am Ende des Laufplans. **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum; als Nachricht an die Koordination, die einträgt. **Grund:** Ändert eine Spur eine Datei, die jede Session beim Start lädt, arbeiten die anderen ab dann unter geänderten Regeln, ohne es zu merken. Am 01.09.2026 hat genau das eine Spur eine Nacht lang unter anderen Regeln arbeiten lassen.

---

## 7. Die Pakete, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach, auch die, die deinen Befund stützen, und meldest einen Widerspruch. Was im Laufplan „(K)“ trägt, hat die Koordination geprüft; alles andere ist ungeprüft. **Keine Labelabfrage als Arbeitsgrundlage.**

**Reihenfolge begründet:** B1 zuerst, weil seine erste Messung entscheidet, ob Spur A ein Indexfeld in ihren ersten Bump aufnehmen muss; je früher das feststeht, desto weniger Rebuilds. B2 danach, weil die Kodierung dafür im Laufplan §4 schon feststeht, das TEI aber erst in A3 kommt.

- **B1, #228, Kennzeichnung der reinen Bestandteile.** **Entschieden** (KZW 01.10.): Wörterbuch und Lemmaseiten zeigen bei diesen Einträgen „Als Wortbestandteil erfasst; kein eigenständiger Beleg im aktuellen Korpus.“; der Status wird aus Korpusbelegen und Bestandteilsverweisen abgeleitet, nicht gespeichert; **kein** `entry/@type="component"`; die Kennzeichnung bestätigt nicht die Richtigkeit der Zerlegung (das darf der Hinweis nicht anders sagen). **Erste Messung, vor jeder Änderung, sofort an die Koordination:** Kennen Wörterbuch und Lemmaseite heute schon (a) die Zahl der Korpusbelege eines Lemmas und (b) die Lemmata, die es in ihrer Etymologie als `seg type="component"` nennen? Aus welchem Index, welchem Feld, an welcher Codezeile? Laut #228 (Kommentar vom 01.10.) gibt es 273 solche Einträge bei 1.285 Einträgen ohne Korpusbeleg; diese Zahlen sind nicht vom heutigen Stand und ungeprüft. Fehlt (b) im Index, meldest du den genauen Feldwunsch (Name, Form, wo im Index), und Spur A baut ihn in ihren ersten Bump. **Haltepunkt:** Die Ableitung ist im Frontend nicht möglich, und der Feldwunsch ist noch nicht entschieden.
- **B2, #358, Anzeige.** **Entschieden** (KZW 11.09., Laufplan §4): `div type="chapter"` mit `subtype="dreissiger"` heißt in der Leseansicht „Strophe N“ statt „Kapitel N“; `<milestone unit="book" n="II"/>` erscheint als Überschrift „Buch II“ an seiner Stelle. Alles andere an `chapter` (Rücksetzung der Verszählung, Deep-Links über `verseId`) bleibt unverändert. **Nachzumessen:** welche weiteren Stellen „Kapitel“ für `chapter` anzeigen (KWIC-Zeilenangaben, Playground, Export), Grep über JS **und** HTML; was davon PZ und WH betrifft, ziehst du mit oder meldest es. Die Spec prüft mit einem Testfragment oder, wenn A3 schon gemergt ist, am echten PZ; **gemergt wird B2 erst nach A3**. **Haltepunkt:** eine Stelle, die `chapter` anders liest, als die Leseansicht es tut.

**Eine Vorgabe, die die Koordination selbst für schwach hält, mit Ersatzfassung:** Der Hinweistext aus B1 ist lang. Passt er in der Wörterbuchliste nicht in die Zeile, darfst du dort eine kurze Marke („nur als Wortbestandteil“) mit dem vollen Satz als Tooltip zeigen und den vollen Satz auf der Lemmaseite. Sag im PR, wo du das getan hast.

## 8. Vorab entschieden, nicht neu zu verhandeln

Laufplan §4 und §1. Für dich besonders: nicht mergen, kein Ticket schließen, relabeln in derselben Session. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination, die ihn unter „Grenzverhandlungen“ im Laufplan einträgt, nicht in den PR-Text.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig und HEAD gegen die Angaben aus 4, dazu der Commit des gelesenen Betriebsvertrags und Laufplans und ob die abgelegte Kickoff-Fassung übereinstimmt; die erste Messung aus B1, **sofort**; Test oder Chrome angefordert und frei; **Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes** (Commit oder `git stash create`); „PR N bereit zum Merge“ mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; fehlender Agententyp; die Haltepunkte in B1 und B2.

**Externer Zustand** (CI, das Indexfeld von A, der Merge von A3): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Den Kommentar des `claude-review`-Bots liest du und beantwortest Verhaltensbefunde, bevor du „bereit zum Merge“ meldest. Nach „bereit zum Merge“ wartest du auf die Merge-Meldung der Koordination.

**Du darfst ein Paket für nicht durchführbar erklären**, mit Messung und früh; dann das nächste. Das ist etwas anderes als die Abbruchklausel in 3, die den ganzen Auftrag betrifft.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Laden über `ToolSearch` mit `select:PushNotification`; siehe `rules/blockaden-melden.md`. Dazu eine Meldung an die Koordination. **Eine Blockade wird nicht über eine andere Spur oder die Koordination umgangen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss je Paket

1. `check-no-em-dash.py --diff-base origin/main`, `build-pages.py --check`, `doc-count-audit.py --check`, `npm run build:css` bei neuen Klassen.
2. `npm test` auf Port 8082 mit `-- --workers=2`, **nach Freigabe durch die Koordination**; das Ergebnis ist die **VERDICT-Zeile**, nie durch eine Pipe, nie `npx playwright test`. Chrome-Verifikation mit realen Einträgen (für B1 etwa *Mur*, `lemma_66692`, und ein Eintrag mit Korpusbelegen als Gegenprobe), hart neu geladen.
3. `fable-reviewer` **vor dem ersten Push**: Zweig, Basis, ob ein Commit oder der uncommittete Arbeitsbaum geprüft wird, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde und ihr Umgang, **und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?** Bei Befunden eine weitere Runde. Den Arbeitsbaum still halten, solange sie läuft.
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt“, „Rote Zeilen“ und „Was zurück an Christian geht“.
5. PR öffnen, **nicht mergen**; Statuskommentar und Relabel je Vorgang, dazu der Abnahme-Ping an @wachauer nach dem Live-Gang, sobald die Koordination den Merge meldet; „bereit zum Merge“ an die Koordination.

### Definition of Done, als Lesertest

Wer nur den PR liest, kann beantworten: welche Einträge die Kennzeichnung bekommen, gezählt und mit der Ableitungsregel; wo sie erscheint (Screenshot oder genaue Stelle); welche Beschriftungen sich in der Leseansicht ändern und für welche Texte; welche Tests das festhalten; was offen bleibt und bei wem.

**In diesem Kickoff gibt es keine Notationsfallen**, die über die Hinweise in den Paketen hinausgehen.
