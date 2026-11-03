# Ball-Rückgabe: Tickets, auf denen eine Antwort liegt

**Erstellt:** 2026-11-03, nach der Entscheidung von chsteiner, liegen gebliebene Antworten wöchentlich von einer Claude-Code-Routine vorsortieren zu lassen.
**Typ:** Playbook. Es autorisiert nichts für sich allein (README dieses Ordners). Ein Lauf beginnt mit einem Auftrag: dem Prompt der wöchentlichen Routine oder einem Kickoff von chsteiner.

**Warum es den Lauf gibt.** Der Tageslauf `issue-matrix.yml` erkennt, wenn Katharina, Julia oder Linda auf eine Frage geantwortet haben und seither nichts von uns kam („Ball bei uns“, rot nach mehr als 7 Tagen). Erkannt ist damit aber nichts erledigt: Vom 20.10. bis 03.11.2026 war der Lauf an 15 Tagen in Folge rot (`gh run list --workflow issue-matrix.yml`), am 03.11. standen 15 Einträge auf der Liste, darunter #364 mit einer zurückgegebenen Prüfseite vom 19.10. Dieser Lauf liest die Antworten und legt Christian vor, was mit jeder zu tun ist. Er tut es nicht selbst.

Wie `DOKU-CHECK.md` muss diese Datei ohne persönliche Skills und Regeln auskommen. Was der Lauf braucht, steht hier oder in den Dateien, auf die sie verweist.

## 1. Fälligkeit

1. **Eingabe ist der generierte Teil von #44**, nicht ein eigener Abruf: `gh api repos/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44 --jq .body`. Zwischen den Markern `MATRIX:BEGIN` und `MATRIX:END` steht die Zeile `| **Ball bei uns (N)** |` mit je einem Eintrag pro Ticket und Person, samt Link auf die Antwort. Den Teil schreibt `scripts/audit/build-issue-matrix.py` täglich um 04:23 UTC. Das Skript selbst läuft in der Cloud nicht, weil es `gh issue list` benutzt, also GraphQL (Abschnitt 2).
2. **`N = 0`:** Ende, ohne Branch und ohne Ausgabe.
3. **Ist ein PR mit dem Kopf `claude/ball-rueckgabe-*` offen:** Ende. `gh api "repos/DigitalHumanitiesCraft/mhdbdb-tei-only/pulls?state=open" --jq '.[].head.ref'`.
4. **Schon vorgelegt:** Ein Eintrag, dessen Antwort-Link in einer früheren Datei `docs/playbooks/kickoffs/*ball-rueckgabe-*.md` auf `main` schon steht, wird übersprungen, wenn das Ticket seither keinen neuen Kommentar hat. Bleiben keine Einträge übrig: Ende.

Ein Ticket kann zweimal auf der Liste stehen, einmal je Person (am 03.11.2026 etwa #537 für Julia und für Katharina). Jeder Eintrag wird für sich behandelt.

## 2. Vertrag

`docs/playbooks/BETRIEBSVERTRAG.md` gilt vollständig und bindend, mit denselben drei Abweichungen für die Cloud wie in `DOKU-CHECK.md` Abschnitt 2: kein eigener Worktree über `claude --bg`, GitHub nur über `gh api` (REST), der Vertrag wird nicht in den Routinen-Prompt kopiert.

Dazu, enger als der Vertrag: **Der Lauf schreibt nichts außerhalb seines PRs.** Kein Issue-Kommentar, auch nicht der eine Statuskommentar aus Regel 8, kein Label, kein `@`-Ping, keine Änderung an Daten, Code oder Doku. Christian postet und setzt um.

## 3. Ablauf je Eintrag

1. **Den Thread ganz lesen:** `gh api repos/.../issues/N` für den Body, `gh api --paginate repos/.../issues/N/comments` für alle Kommentare. Die Antwort der Person steht im Zusammenhang der Frage davor, und beide oft im Zusammenhang einer früheren Entscheidung im selben Thread.
2. **Nachsehen, was seit der Antwort geschehen ist:** `git log origin/main --since=<Datum der Antwort> --grep="#N"`, verlinkte PRs, Commits, die der Thread nennt. Was schon umgesetzt ist, ist keine offene Aufgabe.
3. **Die Quellen vor jeder neuen Frage:** Belege mit Kontext, bestehende Annotation, Authority-Dateien, Doku (`CLAUDE.md`, Abschnitt „Asking“). Eine Frage, die ein `grep` beantwortet hätte, kommt nicht auf die Liste.
4. **Einordnen in genau eine Klasse:**
   - **A, umsetzbar:** Die Antwort entscheidet die Sache. Dazu ein Plan: was zu tun ist, in welchen Dateien, ob der Data-Change-Lifecycle aus `docs/DATA-MODEL.md` greift, wie groß der Aufwand ist (`effort:*`). Bei einer zurückgegebenen Prüfseite oder JSON-Datei zusätzlich: ob der Anhang lesbar ist (ein GitHub-Anhang kann 403 liefern, dann wird das vermerkt, nicht umgangen), und welche Einträge sich seit dem Datenstand der Prüfseite geändert haben. Eine Entscheidung auf veraltetem Stand wird nicht blind angewendet.
   - **B, neue Frage nötig:** Die Antwort lässt etwas offen, oder sie wirft eine Folgefrage auf. Dazu die fertige erste Zeile eines Kommentars, `@<login> Frage: <ein Satz>?`, die ohne den Thread verständlich ist, und zwei bis vier Zeilen Kontext darunter. Die Form und warum sie zählt, steht in `CLAUDE.md` unter „Who is on turn“.
   - **C, Abnahme fällig:** Umgesetzt und live, die Person soll prüfen. Dazu die Zeile `@juliahin Abnahme: <was zu prüfen ist>?` mit Live-URL und Testschritten, Katharina weiter unten mitgenannt, wenn es eine einfache Abnahme ist. Sonst an Katharina allein (`CLAUDE.md`, „Working an Issue“).
   - **D, schließen oder umlabeln:** Die Antwort erledigt das Ticket, oder sein Zustand ist ein anderer, als die Labels sagen. Dazu der Kommentar-Link, der das belegt, und die vorgeschlagenen Labels nach dem Schema in `CLAUDE.md`.
5. **Im Zweifel B, nie A.** Ein Plan, der eine Entscheidung unterstellt, die nicht gefallen ist, ist teurer als eine Frage. Katharina hat in #406 gerade das gerügt, was eine falsche Einordnung hier anrichtet.

## 4. Ergebnis

1. **Branch** `claude/ball-rueckgabe-JJJJ-MM-TT` von `origin/main`, die Basis gemessen nach Regel 7 des Betriebsvertrags.
2. **Eine Datei** `docs/playbooks/kickoffs/FORTSETZUNG-ball-rueckgabe-JJJJ-MM-TT.md`. Das Präfix heißt nach `docs/playbooks/README.md`: vorbereitet, noch nicht abgeschickt. Aufbau:
   - Erste Zeile: dass die Datei ein vorbereiteter Auftrag aus dem Lauf vom JJJJ-MM-TT ist, mit dem Stand von #44, auf dem er beruht, und der Zahl der Einträge samt Menge (`12 von 15 Einträgen, 3 schon vorgelegt`).
   - **Zum Posten (B und C):** je Eintrag das Ticket, die fertige Kommentarzeile und der Kontext. Hinweis aus `CLAUDE.md`: Eine Frage wird nur dann oben auf unseren letzten Kommentar editiert, wenn der neuer ist als ihre Antwort, sonst als neuer Kommentar gepostet.
   - **Zum Schließen oder Umlabeln (D).**
   - **Auftrag für eine autonome Session (A):** ein Kickoff nach `KICKOFF-VORLAGE.md`, je Eintrag ein Arbeitspaket mit dem Plan. Der Betriebsvertrag wird erst beim Abschicken eingefügt, die Datei verweist nur darauf.
   - Je Eintrag die Belege: Link auf die Antwort, Commits, Stellen in den Daten.
3. **Gates und Review vor dem Push** wie in `DOKU-CHECK.md` Abschnitt 4, Punkt 4: `python scripts/audit/check-no-em-dash.py --diff-base origin/main`, dann der `reviewer`.
4. **PR über REST**, Titel `Ball-Rückgabe JJJJ-MM-TT: <Zahl> Einträge`, Body mit einer Tabelle Ticket, Person, Klasse und ein Satz. Kein Closing-Keyword vor einer Issue-Nummer. Gemergt wird von Hand.
