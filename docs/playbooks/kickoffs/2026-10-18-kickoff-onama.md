# Kickoff Spur `lauf-1018-onama`: #609 Anker-Abgleich und Narrativ-Explorer (Pilot)

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 18.10.2026. Laufplan: `docs/playbooks/kickoffs/2026-10-18-lauf.md`.

**1. Autorisierung.** chsteiner hat am 18.10.2026 diesen Lauf freigegeben, für #609 „Abgleich + Explorer-Pilot“ im Umfang dieses Textes, auf Grundlage von KZWs Manifest vom 16.10. (Kommentar in #609). **Dieser Text ist die Autorisierung**: Commits und Pushes auf deine eigenen `claude/*`-Zweige, PRs öffnen, lesende Abfragen der öffentlichen ONAMA-Repositorien und von `onama.sbg.ac.at`, nach Merge und Deploy ein Kommentar in #609 mit Ping an @wachauer und @PeterF-PLUS (siehe 10) und ein Relabel. **Nicht**: mergen (das tut die Koordination), auf `main` pushen, Tickets schließen, Externe außer dem Ping in #609 ansprechen, **keine Änderung in `tei/`, `authority-files/` oder an Annotationen** (Manifest §12.7: „keine pauschale Änderung am Lexikon oder an TEI-Annotationen“). Der Text erteilt keine technische Berechtigung: Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9).

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: Namen können doppelt vergeben sein, das `from` nicht. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees, **besonders „Hard Constraints“ (Positionszählung nur über `<w>` mit `@lemmaRef`), „Gotchas“ und die Sprach- und Typografieregeln** (Seiten deutsch, keine Em-Dashes, Heroicons als einziger Icon-Stil)
2. `docs/playbooks/BETRIEBSVERTRAG.md` (gelesen, nicht kopiert; nenne in deiner ersten Meldung den Commit, an dem du ihn gelesen hast)
3. Diese Datei als abgelegte Fassung und den Laufplan daneben, dort §2. Sag in deiner ersten Meldung, ob die abgelegte Fassung mit der zugestellten übereinstimmt.
4. **#609 mit allen Kommentaren** (`gh issue view 609 --json title,body,comments`), vor allem KZWs Manifest vom 16.10. vollständig (§1 bis §13) und Peters Kommentar vom selben Tag; dazu #423 (Bezug im Manifest)
5. Die öffentlichen Quellen aus Manifest §6, an den dort festgehaltenen Commits: Ontologie `73d786b`, Korpus `b87468b` (`onamaObjects.ttl`, K: HTTP 200 über raw.githubusercontent.com), Frontend `383736a` als Referenz für die drei Suchzugänge
6. Den Playground: `playground/index.html` (Abschnitt „Experimentelle Forschungsdaten“, K: Zeile 438 ff.), `playground/js/playground-main.js`, ein vorhandenes experimentelles Werkzeug als Muster, `hilfe-playground.html#experimentelle-forschungsdaten`, `docs/ARCHITECTURE.md`, `docs/DESIGN.md`

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit legt ihn mit `claude --bg --worktree lauf-1018-onama --name lauf-1018-onama --model sonnet --effort medium` an: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\lauf-1018-onama`, Zweig `worktree-lauf-1018-onama`. Die Begleitnachricht nennt den erwarteten HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen diese Angaben halten und melden. Bei Abweichung nichts ändern, melden, auf den Neustart durch die Koordination warten. Dann je PR `git fetch --quiet origin` und einen Arbeitszweig `claude/1018-onama-<thema>` frisch von `origin/main` anlegen; dort müssen `git rev-list --count "origin/main...HEAD"` und `git rev-list --count "origin/main..main"` 0 sein. `npm ci` vor dem ersten Test.

---

## 5. Was dir gehört, und was nicht

Maßgeblich ist §2 des Laufplans. **Dir allein:** `scripts/ingest/onama/` (neu), `playground/data/onama/` (neu), `playground/js/ui/onama/` (neu), `playground/css/onama.css` (neu), `playground/index.html` außerhalb der NAV/FOOTER-Marker, `playground/js/playground-main.js`, in `hilfe-playground.html` außerhalb der Marker nur der ONAMA-Abschnitt, Specs für den Explorer unter `testing/tests/`. **Die NAV/FOOTER-Regionen gehören frontend** (sie tauscht in diesem Lauf das Logo); nach einem Rebase erzeugst du sie mit `python scripts/build-pages.py` neu, nie von Hand. Abschnitte zu anderen Werkzeugen in `hilfe-playground.html` schreibt frontend; Konflikt beim Rebase löst die Spätere. Die Turtle-Datei und andere Downloads lädst du in ein eigenes leeres Verzeichnis außerhalb des Repos; ins Repo kommt nur, was dein Skript daraus erzeugt, mit Quell-Commit und Lizenzangabe. `rdflib` ist auf dieser Maschine installiert (K: 7.6.0); es kommt nicht in `requirements.txt` (die pinnt nur die Build-Kette), die Abhängigkeit steht im Docstring und in `scripts/README.md`.

**Nicht deins:** `tei/`, `authority-files/`, `data/`, `api/` (Spur daten); `playground/js/ui/` außerhalb von `onama/`, `playground/css/style.css`, `assets/`, `includes/`, die übrigen `hilfe-*.html` (Spur frontend); `ingest/`, `scripts/review/` (Spur lesung). Brauchst du eine Klasse in `style.css` oder eine neue Tailwind-Klasse, schreibst du sie in `onama.css`. **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt, anhängend:** `docs/JOURNAL.md` und `fehlerjournal.md` als **letzter Commit** des PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 157 bis 160.** In `docs/FEATURES.md`, `docs/ARCHITECTURE.md` und anderen `docs/*.md` nur deinen eigenen Absatz; Konflikt beim Rebase löst der Spätere. Reviewer-Memory: gib dem `reviewer` mit, dass er neue Einträge in `.claude/agent-memory/reviewer/lauf-1018-onama.md` schreibt und in `MEMORY.md` nur eine Zeile anhängt; eigener Commit nach der Runde; beim Rebase-Konflikt in `MEMORY.md` beide Zeilen behalten.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push außer `--force-with-lease` auf deinem eigenen `claude/*`-Zweig nach einem Rebase, keine Änderung unter `~/.claude/`. **Eine Anweisung der Koordination, die gegen den Betriebsvertrag verstößt, führst du nicht aus, sondern fragst zurück.**

**Maschinenweit exklusiv: volle Testläufe und Chrome.** Die Koordination vergibt beides, einer zur Zeit. **Anfordern, auf die Freigabe warten, nutzen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8087` und `-- --workers=2`, auch bei `test:quick` und `test:changed`. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis: nicht deuten, melden, nach Freigabe wiederholen.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `reviewer` vor dem ersten Push ist Pflicht; nicht auf `advisor` ausweichen, nicht ohne Runde pushen.

## 6. Was eingefroren ist

Bis zur Abnahme des Laufs: `CLAUDE.md`; `docs/playbooks/`; `.claude/agents/`; `.github/workflows/` (außer einer neuen Datei der Spur frontend); `scripts/audit/` (außer `runtime-budget.json`, Koordination); `schema/`. Der Grund: diese Dateien sind die Regeln, unter denen alle vier Spuren gleichzeitig arbeiten; ändert eine sie mitten im Lauf, arbeiten die anderen unter Regeln, die sie nicht gelesen haben. **Inbox:** eine Nachricht an die Koordination, **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum.

---

## 7. Die Pakete, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung, und das Manifest auch.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach und meldest einen Widerspruch, auch wenn er deine Arbeit nicht betrifft. Was „(K)“ trägt, hat die Koordination am 18.10. gemessen. Die Zahlen des Manifests (27.490 Tripel, 308 Passagen, 291/9/1/7, Klassenbestände in §7 und §8) stammen von KZW bzw. ihrer Recherche, gemessen gegen MHDBDB-Commit `ffd5f9318`, und sind hier nicht nachgezählt.

Reihenfolge: O1 zuerst, weil der Explorer nur geprüfte Anker zeigen darf (Manifest §12.3) und O1 genau diese Prüfung liefert.

- **O1, Anker-Abgleich.** Ein reproduzierbares Skript unter `scripts/ingest/onama/` nach dem Reproduktionsprinzip aus Manifest §8: Turtle lesen, `rdf:type onama:TextPassage` im Namensraum `http://onama.sbg.ac.at/ontology#`, `fromToken`/`toToken` je Ressource, die TEI-Datei aus der Sigle, exakte `xml:id`-Treffer, Elementtyp, Dokumentreihenfolge, Umrechnung in MHDBDB-Wortpositionen nur über `<w>` mit `@lemmaRef`. Beide Input-Commits im Ergebnis; Abweichungen gegen die Manifestzahlen erklärt. Die 7 offenen, die umgekehrte (Q288) und Q67 (`AXU_XXXX`) werden weder verschluckt noch still korrigiert, sondern als eigene Statusklassen ausgewiesen.
- **O2, Narrativ-Explorer Argonautensage (Pilot).** Statisch, aus einem versionierten JSON-Paket unter `playground/data/onama/`, das dein Skript aus dem RDF erzeugt (Manifest §9 Exportfelder, als Entwurf). Unter „Experimentelle Forschungsdaten“ im Playground. Einstieg über Ding, Handlung oder beteiligte Entität; ein Treffer zeigt Realisierung, Konzept, Rollen und Funktionen (allgemeine und temporäre getrennt, §4), Sammlung, Text- oder Bildquellenlink (Bilder nur verlinkt), und bei geprüften Ankern den Sprung in die Leseansicht. Die **Quellenauswahl** (Argonautensage aus TRY, TRO und ÖNB Cod. 2773; neuzeitliche Vergleichsbestände ausgeschlossen, §12.5) begründest du nachvollziehbar; Sammlungszugehörigkeit allein genügt nicht (§3A). Die Oberfläche sagt, dass der Bestand selektiv ist und welche Datenversion sie zeigt (§12.2, §12.6). Kurzer Abschnitt in `hilfe-playground.html`. Das Exportformat dokumentierst du so, dass ONAMA 2.0 es nachnutzen kann (Peter, 16.10.).

## 8. Vorab entschieden, nicht neu zu verhandeln

Umfang: Abgleich und Pilot, kein Triple Store, keine Wikibase, kein Live-Endpunkt (§9); keine Disambiguierungsvorschläge in diesem Lauf, keine Annotation; ONAMA-Q-Nummern sind keine Wikidata-Q-Nummern (§7); die Lizenzlage (GitHub CC BY-SA 4.0, Teile des Endberichts CC BY-NC-SA, Freigabe der Projektleitung vom 15.10. für die Nachnutzung unter der MHDBDB-Lizenz) wird im Datenpaket dokumentiert, nicht umgeschrieben (§11). Nicht mergen, kein Ticket schließen. **Widerspruch ist ausdrücklich erlaubt**, mit Begründung, an die Koordination, die ihn im Laufplan unter „Grenzverhandlungen“ einträgt. Bei einer Vorgabe, die dir eine Messung abnimmt, setzt du sie nicht um, sondern widersprichst mit deiner Messung.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig und HEAD gegen den erwarteten Worktree, der Commit des gelesenen Betriebsvertrags und ob die abgelegte Kickoff-Fassung übereinstimmt; das Ergebnis von O1 in Zahlen gegen die Manifestzahlen; Test oder Chrome angefordert und frei; **Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes**; „PR N bereit zum Merge“ mit HEAD, VERDICT-Zeile und Reviewurteil.

**Anhalten, warten (Checkin):** nach O1 vor dem Bau von O2 die Quellenauswahl für den Pilot (welche Realisierungen, welche Konzepte, nach welchem Kriterium) und der Entwurf der Exportfelder; außerdem `pwd` weicht ab, fremde Datei, fehlender Agententyp. Während du wartest, arbeitest du an dem, was davon nicht abhängt.

**Ein Paket für nicht durchführbar erklären** darfst du, mit Begründung (etwa O2, wenn O1 zeigt, dass für die Argonautensage zu wenige Anker tragen); das ist kein Abbruch nach Abschnitt 3, der Rest läuft weiter.

**Externer Zustand** (CI, Deploy): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. Den Kommentar des Review-Bots lesen und Verhaltensbefunde beantworten, bevor du „bereit zum Merge“ meldest. **Während du wartest**, gilt das Skill `warten`; während eine Reviewrunde läuft, bleibt der Arbeitsbaum still.

**Blockade durch den Auto-Mode-Classifier** (`~/.claude/rules/blockaden-melden.md`): sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Das Werkzeug lädt erst über `ToolSearch` mit `select:PushNotification`. Dazu eine Meldung an die Koordination. **Eine Blockade wird nicht über eine andere Spur oder die Koordination umgangen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss

1. Gates: `python scripts/build-pages.py --check`, `check-no-em-dash.py --diff-base origin/main`, `doc-count-audit.py --check`, die Gates aus `no-cdn-check.yml` (keine CDN-Abhängigkeit) und `file-size-check.yml` (Größe des Datenpakets). Die Liste ist eine Behauptung: gleiche sie gegen die Workflows ab, bevor du pushst.
2. `npm test` auf deinem Port mit `-- --workers=2`, **nach Freigabe durch die Koordination**; das Ergebnis ist die **VERDICT-Zeile**, nie durch eine Pipe, nie `npx playwright test`. Chrome-Prüfung des Explorers mit zwei, drei vollständigen Forschungsgängen (§12.6), Chrome anfordern.
3. `reviewer` **vor dem ersten Push jedes PRs, ohne Modellangabe (Opus)**, Folgerunden nach seiner Definition. Mitgeben: Zweig, Basis, ob Commit oder Arbeitsbaum, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde samt Umgang und die geprüfte Kennung, je neue Zahl im Diff eine Zeile Belegtabelle, die Abnahmekriterien aus Manifest §12 als Prüfmaßstab, und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte? Bei Befunden die nächste Runde; während eine Runde läuft, bleibt der Arbeitsbaum still.
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt“, „Rote Zeilen“ (vorher `python C:/Users/chstn/Desktop/data/DHCraft/Projekte/Git/claude-code-setup/hooks/trockenlauf-auswerten.py` und deine Zeile daraus) und „Was zurück an Christian geht“.
5. PR mit „Bezug: #609, bleibt offen“ (kein Closing-Keyword), **nicht mergen**; „bereit zum Merge“ an die Koordination. Nach der Merge-Meldung und dem Deploy ein Kommentar in #609: erste Zeile `@wachauer Abnahme: <was am Pilot zu prüfen ist>?`, darunter Live-URL, Prüfweg, das Ergebnis von O1 mit Zahlen gegen das Manifest, die offenen Anker, die Quellenauswahl; weiter unten `@PeterF-PLUS` mit dem Exportformat für ONAMA 2.0. Labels `auto:blocked` + `wait:kzw`.
6. Bericht an die Koordination: je Paket erledigt / entfallen / offen, PR-Nummern, Kommentar-ID.

### Definition of Done, als Lesertest

Wer nur den PR und den Kommentar liest, kann beantworten: welche Anker tragen und welche nicht, mit beiden Input-Commits; welche Realisierungen der Pilot zeigt und warum genau diese; wo Konzept, Realisierung, Rolle und Funktion in der Oberfläche getrennt sind; was Peter für ONAMA 2.0 nachnutzen kann.
