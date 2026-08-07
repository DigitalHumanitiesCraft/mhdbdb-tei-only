# Masterplan: Kuration eines einzelnen Lemmas

**Erstellt:** 2026-08-07, aus #269 (Bitte von KZW nach dem Fall „Abba", PR #268).
**Typ:** Playbook (wiederverwendbares Session-Verfahren, dauerhaft). Kein session-spezifischer Teil, dieses Playbook wird nicht pro Lauf befüllt.
**Gilt für:** einen Auftrag der Form „nimm dieses eine Wort und trag X dazu ein". Nicht für Ingest (dafür `docs/DATA-MODEL.md` → Ingest procedure) und nicht für Massen-Nachannotation (#216 und Verwandte sind eigene Arbeitspakete).

**Dieses Playbook autorisiert nichts.** Es beschreibt, was gilt, nachdem ein Auftrag von chsteiner oder KZW eine Session eröffnet hat. Der gemeinsame Teil steht in [`BETRIEBSVERTRAG.md`](BETRIEBSVERTRAG.md) und wird beim Kickoff wörtlich in den Prompt kopiert; hier stehen nur die Abweichungen.

---

## 1. Warum es das gibt, und was die Messung sagt

Der Auftrag lautete: **ein** Wort mit Zusatzinformationen annotieren, `lemma_37818` „Abba", aramäische Gottesanrede. Herausgekommen ist PR #268 mit 20 Dateien. KZWs Rückmeldung: „Du machst aus dem EINEN Wort jetzt voll das große Ding. Ich weiß, ein Wort hat mittlerweile relativ viele Auswirkungen, aber du tust dir wahrscheinlich leichter, wenn wir sowas strukturiert angehen."

Die 20 Dateien, nach Stufen sortiert (gemessen am 2026-08-07 über `gh pr view 268 --json files`):

| Stufe | Dateien | Welche |
|---|---|---|
| 1, Daten | 1 | `authority-files/lexicon.xml` |
| 2, Schema | 7 | `mhdbdb-authority.rnc`, `.rng`, `authority-lexicon.example.xml`, `build-authority-index.py`, `audit-authority-files.py`, `TEI-MODEL-AUTH-FILES.md`, `CONTRACTS.md` |
| Lifecycle, unvermeidlich | 6 | `data/authority-index.json.gz`, `api/index.json`, `api/lemmata/index.json`, `corpus-loader.js`, `TEI-MODEL.md` §11, `INDEX.md` §Status |
| 3, sichtbar machen | 4 | `lemma/index.html`, `lemma/lemma-page.js`, `lemma-explorer.js`, `lemma-page.spec.js` |
| immer | 2 | `JOURNAL.md`, der Phasenplan zu #28 |

**Das ist die eigentliche Lehre, und sie war nicht die erwartete.** Die naheliegende Vermutung war, dass das Frontend die Kaskade treibt. Es waren 4 von 20 Dateien. Der Bauch sind Schema (7) und abgeleitete Schicht (6), zusammen 13. Wer diese Session kürzen will, kürzt sie **nicht** am Frontend, sondern an der Frage, ob das Schema überhaupt angefasst wird. Genau deshalb sitzt die einzige Stopp-Stelle dieses Playbooks zwischen Stufe 1 und Stufe 2 und nicht zwischen 2 und 3.

Die abgeleitete Schicht ist dabei nicht verhandelbar: ohne Index-Rebuild und Versions-Bump sehen Nutzerinnen mit gefülltem IndexedDB die Kuration nie. Das ist keine Gründlichkeit, das ist die Bedingung dafür, dass die Arbeit überhaupt ankommt.

---

## 2. Die eine Frage, die die Stufe bestimmt

> **Passt die Annotation in das bestehende Datenmodell, ja oder nein?**

Prüfbar, nicht Ermessenssache: steht für das, was eingetragen werden soll, ein Element und ein Attribut in `schema/mhdbdb-authority.rnc` bereit, und ist der Wertebereich weit genug?

- **Ja** → Stufe 1, und die Session läuft bis zum PR durch.
- **Nein** → Stufe 2, und die Session **endet mit einem Vorschlag**, statt das Schema anzufassen.

Bei „Abba" war die Antwort nein, und zwar hart: `lexicon.entry` kannte nur Klassifikation (POS, Konzept-Zeiger, Kompositions-Komponenten). Für eine Erläuterung, eine Bedeutungsangabe oder eine Bibelstelle gab es kein Element. Der Auftrag „nimm die Erklärung in die Daten auf" war ohne Schema-Erweiterung nicht erfüllbar. Das zu erkennen ist Stufe 0, nicht Stufe 2: es kostet einen Blick ins `.rnc` und entscheidet über den Umfang der ganzen Session.

---

## 3. Stufe 0: Vorflug (immer, etwa zehn Minuten)

Die ersten drei Punkte stehen hier, weil sie beim Abba-Lauf Zeit gekostet haben, ohne mit dem Inhalt zu tun zu haben.

1. **Branch-Basis messen, nicht am Namen ablesen.** Beide Zählungen müssen 0 sein:
   ```bash
   git fetch --quiet origin
   git rev-list --count "origin/main...HEAD"
   git rev-list --count "origin/main..main"
   ```
   Der Abba-Lauf startete auf `feature/236-frauenlob`, einem gemergten und oben gelöschten Zweig, 10 Commits hinter `main`. Der erste Index-Build lief gegen einen veralteten `works.xml`-Stand, und gemerkt hat es KZW, nicht die Session. Begründung und Fehlergeschichte in [`MASTERPLAN-AUTONOME-ISSUE-SESSION.md`](MASTERPLAN-AUTONOME-ISSUE-SESSION.md) §2.1 Regel 28.
2. **Eigener Worktree.** `git worktree add -b <branch> <pfad> origin/main`. Der Hauptordner bleibt Referenz. Parallele Sessions teilen sonst den Index, und beim Abba-Lauf war ein Umschalten im gemeinsamen Verzeichnis nicht möglich, weil eine zweite Session dort gestagte Dateien liegen hatte. Ein Worktree hat kein `node_modules`; ohne Junction auf den Hauptbaum läuft `npm test` gar nicht erst an.
3. **Port prüfen, bevor getestet wird.** Beim Abba-Lauf servierte Port 8080 das Verzeichnis der Nachbarsession. Ein `npm test` hätte zwanzig Minuten lang die falschen Dateien geprüft. Seit dem 2026-08-05 bricht `scripts/run-tests.js` in diesem Fall selbst ab; verlassen sollte man sich trotzdem nicht darauf, ein `curl` auf eine gerade geänderte Datei kostet nichts.
4. **Den Auftrag gegen das Schema halten.** `schema/mhdbdb-authority.rnc` lesen, und zwar den `entry`-Block. Daraus folgt die Stufe (Abschnitt 2).
5. **Den Ist-Zustand des Lemmas ansehen**, in `lexicon.xml` und live auf der Lemma-Seite. Was steht schon da, was widerspricht dem Auftrag, welche Konzept-Zeiger hängen dran?

---

## 4. Stufe 1: reine Daten (der Normalfall)

Die Annotation nutzt nur vorhandene Elemente und Vokabulare: einen Konzept-Zeiger setzen, ein `@pos` korrigieren, eine Variante ergänzen, einen `<sense>` sortieren.

1. Datei ändern, eine Sache pro Commit.
2. **Schema-Validierung** zweistufig laufen lassen (`schema/README.md`).
3. **Data-Change-Lifecycle** abarbeiten. Nicht hier nachbauen, sondern anwenden: [`docs/DATA-MODEL.md` → Data-Change-Lifecycle](../DATA-MODEL.md#data-change-lifecycle), Routing-Tabelle. Für eine Änderung an `lexicon.xml` heißt das die Authority-Checkliste ohne Schritt 1, gemessen etwa 17 Sekunden Bauzeit.
4. **Versions-Bump** an den fünf Stellen, sobald ein Index neu gebaut wurde. `python scripts/audit/check-index-versions.py` lokal laufen lassen, das spart eine CI-Runde.
5. **Cross-Ref-Audit** und die übrigen Gates, dann PR.

Wenn dieser Weg länger als eine Stunde dauert, stimmt die Stufeneinschätzung nicht. Dann zurück zu Abschnitt 2.

**Was Stufe 1 nicht deckt und wo trotzdem gern zugegriffen wird:** einen Konzept-Zeiger zu **entfernen** ist eine philologische Entscheidung, keine Datenpflege. Beim Abba-Lauf wurde `concept_24452000` („Kirchliche Hierarchie") gestrichen; KZW hat es hinterher freigegeben, aber die Streichung war vor der Freigabe passiert. Zeiger setzen ist Stufe 1, Zeiger streichen ist eine Rückfrage.

---

## 5. Stufe 2: das Datenmodell reicht nicht

**Hier endet die Session.** Nicht mit einer blockierenden Rückfrage mitten im Lauf, sondern mit einem fertigen Vorschlag und einem sauberen Arbeitsbaum.

Der Grund ist nicht Vorsicht, sondern Widerspruchsfreiheit: eine autonome Session darf laut Betriebsvertrag Regel 9 nicht auf eine Antwort warten. Ein „blockierender Stopp" wäre eine Regel, die sich selbst aufhebt. Also läuft die Session bis an die Grenze und legt die Entscheidung vor, statt sie zu treffen oder auf sie zu warten.

Was die Session in diesem Fall abliefert:

1. **Alles Daten-Seitige, das ohne Schema-Änderung geht.** Oft ist das mehr als gedacht.
2. **Die Lücke beschrieben**: welches Element fehlt, für welche Aussage, mit dem Zitat aus dem Auftrag, das ohne die Erweiterung nicht erfüllbar ist.
3. **Einen Kodierungsvorschlag** mit Alternativen und dem Grund für die Empfehlung. Beim Abba-Fall war das `<etym type="borrowing">` mit `<lang @norm>` plus Attributionsnotiz.
4. **Den Umfang der Erweiterung beziffert**: RNC **und** RNG, Beispieldatei, Doku-Abschnitt, getypte Attribute, Negativtest. Das sind die 7 Dateien aus der Tabelle in Abschnitt 1, und das ist die Zahl, um die es bei der Entscheidung geht.
5. **Ob die Erweiterung eine offene Entscheidung eines anderen Tickets mitentscheidet.** Beim Abba-Fall legte sie die Kodierung für #28 Schicht B fest, die der Phasenplan ausdrücklich offengelassen hatte. Ein Ein-Wort-Auftrag hat damit eine Phase-0-Entscheidung eines Umbrella-Issues erledigt. Das war vertretbar, weil am echten Fall billiger als am Reißbrett, aber es war nicht beauftragt, und **genau das gehört in den Vorschlag statt in den Diff.**

Ein Schema ist kein Implementierungsdetail: es wird publiziert (`tei/`, `api/`, Zenodo) und Dritte richten sich danach. Deshalb die Sonderbehandlung, und deshalb gilt hier ausdrücklich auch **„Daten vor Schema"** (CLAUDE.md, ADR-013): wo die vorhandenen Daten mit dem Schema kollidieren, wird zuerst die Datenmigration geprüft, nicht die Lockerung.

---

## 6. Stufe 3: sichtbar machen (voreingestellt ein eigenes Ticket)

Frontend-Rendering, Tests dafür, Hilfeseiten. **Standardmäßig nicht Teil der Kurations-Session**, entschieden am 2026-08-07.

Wenn die Aufgabe ausdrücklich sagt „soll online sichtbar sein", dann gehört es dazu, und dann gilt: **beide Oberflächen oder keine.** Lemma-Seite und Playground-Lemmata-Explorer zeigen dieselben Lemma-Daten; nur eine von beiden zu bedienen erzeugt genau die Drift, die sonst Audits einsammeln.

Die Kehrseite dieser Voreinstellung ist bekannt und in Kauf genommen: es entsteht ein Bestand kuratierter Daten, die in der Oberfläche nicht vorkommen. Für genau diesen Zustand gibt es bereits ein Beispiel, #270 (`@resp` der kuratierten Angaben wird nirgends angezeigt, weil `contributors.xml` nicht im Index ist). Wer Stufe 3 vertagt, **verlinkt das Folgeticket im PR**, sonst wird aus „vertagt" stillschweigend „vergessen".

---

## 7. Der Grenzfall: das Modell passt, aber das Vokabular fehlt

Die Frage aus #269, die das Stufenmodell zunächst nicht abdeckte: eine Annotation, die ins Schema passt, aber einen Eintrag braucht, den es noch nicht gibt, etwa ein fehlendes Konzept.

Das ist **nicht** Stufe 2. Das Schema bleibt unangetastet, es kommt eine Zeile Daten dazu. Es ist auch nicht glatt Stufe 1, weil ein neuer Eintrag in einer Authority-Datei eine Setzung ist, die andere Lemmata mitbenutzen werden.

Regel: **anlegen ja, aber als eigener Commit mit Begründung, und im PR-Body benannt.** Wer ein Konzept, eine Person oder eine Gattung neu anlegt, schreibt dazu, warum kein bestehender Eintrag passt, und nennt die drei nächstliegenden, die geprüft wurden. Bei „Abba" war das nicht nötig, `concept_23123905` (Aramäisch) existierte bereits: Glück, nicht Methode.

Für `lexicon.xml` gilt zusätzlich die Grundregel aus CONTRACTS §F: **das Korpus führt.** Ein Lemma wird nicht angelegt, weil es fehlt, sondern weil ein `<w>` im Korpus darauf zeigt.

---

## 8. Abschluss (immer)

Dieselbe Liste, dieselbe Reihenfolge, unabhängig von der Stufe:

1. Schema-Validierung zweistufig
2. `check-index-versions.py`, falls ein Index neu gebaut wurde
3. Cross-Ref-Audit
4. Em-Dash-Gate mit `--diff-base origin/main`
5. `npm test`, die VERDICT-Zeile unverändert in den PR
6. Fable-Review vor dem ersten Push (Betriebsvertrag Regel 11)
7. JOURNAL-Eintrag, datiert. Berichtenswert ist nicht, dass ein Wort kuratiert wurde, sondern welche Entscheidung dabei anfiel und was verworfen wurde
8. Ein Statuskommentar am Ticket, und wenn KZW oder Julia abnehmen: das Issue bleibt offen (Betriebsvertrag Regel 17)

---

## 9. Entscheidungen, auf denen dieses Playbook steht

Getroffen von chsteiner am 2026-08-07, aus den Fragen in #269:

| Frage | Entscheidung | Grund |
|---|---|---|
| Playbook, Skill oder Prompt-Vorlage? | **Playbook**, hier im Repo | Wiederverwendbares Session-Verfahren, erbt den Betriebsvertrag statt ihn zu kopieren, und ist für KZW und Julia sichtbar. Das Skill-Verzeichnis bleibt bewusst schlank |
| Wo endet eine Session? | **Bei korrekten Daten.** Stufe 3 ist ein eigenes Ticket | KZWs Rückmeldung zum Abba-Fall. Kostet 4 der 20 Dateien, siehe Abschnitt 1 |
| Wie hart ist der Stufe-2-Stopp? | **Session endet mit Vorschlag**, kein Warten im Lauf | Betriebsvertrag Regel 9 verbietet einer autonomen Session das Warten; ein blockierender Stopp widerspräche ihr |
| Neues Vokabular nötig? | Eigene Stufe zwischen 1 und 2, siehe Abschnitt 7 | Aus der vierten Frage in #269, die das Modell zunächst nicht abdeckte |
