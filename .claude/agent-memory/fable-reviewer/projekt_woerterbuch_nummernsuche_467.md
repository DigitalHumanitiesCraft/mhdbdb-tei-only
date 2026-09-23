---
name: woerterbuch-nummernsuche-467
description: Review-Lehren zu #467 (Woerterbuch findet lemma_N), Runde 2 vom 23.09.2026: toter Beleg authority-manager.js:54, Multi-Lemma-Suche kennt nur die nackte Zahl, JOURNAL-Behauptungen ueber Issue-Kommentare und Commit-Trailer messen
metadata:
  type: project
---

**Die Multi-Lemma-Suche des Playgrounds kennt nur die nackte Zahl, nicht `lemma_N`.** Der Pfad ist
`playground/js/ui/tei/tei-ui.js:19` (`/^\d+$/` wird direkt als ID genommen), danach
`searchLemmaByOrthography`, das fuer `lemma_4086` in keiner Stufe trifft (Stufe 3: einzige
Praefixkandidaten "le" mit 2 Zeichen unter MIN_LEMMA_PREFIX_LENGTH=3). `lexicon.xml#lemma_4086`
faellt dort dagegen auf `lex` (lemma_9589).

**`authority-manager.js:49 resolveLemmaNames` hat 0 Aufrufer** (Grep ueber js/html/md), obwohl
seine Zeile 54 wie die kanonische ID-Erkennung aussieht. Wer sie als Beleg zitiert, zitiert toten Code.

**Why:** Die B3-Session hat im JOURNAL `authority-manager.js:54` als Beleg fuer das Verhalten der
Multi-Lemma-Suche genannt und "kennt die Nummer" geschrieben, waehrend KZWs Beispiel im Issue-Body
`lemma_4086` ist. Beides nur durch Aufruferkette pruefbar, nicht durch Lesen der zitierten Zeile.

**How to apply:** Bei jeder Zeilenangabe als Beleg zuerst die Funktion benennen, in der sie liegt,
und dann ihre Aufrufer greppen. JOURNAL-Saetze "in #N beantwortet" per
`curl api.github.com/repos/.../issues/N/comments` zaehlen (23.09. 2 Kommentare, beide wachauer,
keiner der Session). Trailer-Behauptungen per
`git log --format='%h %(trailers:key=Co-Authored-By,valueonly)'` messen: 026ce7586 (erster B3-Commit)
traegt "Claude Opus 5.5", das JOURNAL sagte "ab B3" in CLAUDE.md-Form.

Datenzahlen (Authority-Index 23.09.2026): variants hat 89 rein numerische Schluessel, alle auf die
5 Ziffernlemmata (53328 "1", 69733 "46", 69748 "36", 69749 "42", 69750 "49"); `variants["4086"]`
fehlt. Korpussuche `46` trifft daher das Lemma "46", nie lemma_46.

**Runde 3 (Cherry-pick-Neuaufbau, 23.09.2026 spaet):** `git range-diff <alt-basis>..<alt> origin/main..HEAD`
zeigt die uebernommenen Commits als `=`; dazu `git diff <alt-head> HEAD --stat -- <code/test/hilfe>` als
Nullprobe (leer = Code identisch). Ein Squash-Merge-Trailer kann eine Variante tragen: B1 (#478,
28a5bffda) hat "Claude Opus 5.5 (1M context)", B2 (#480) "Claude Opus 5.5"; ein JOURNAL-Satz "tragen
Opus 5.5" ist fuer B1 nur bis auf den Zusatz wahr. `trockenlauf-auswerten.py` (claude-code-setup/hooks)
druckt je Session eine Zeile (Aufrufe/Treffer/Rate) und laeuft ohne Argumente; Sessionzahlen im JOURNAL
sind nur als "damals <= jetzt" pruefbar (76/259 -> 86/316 in der Zwischenzeit). "steht in #467" war zum
Pin-Zeitpunkt weiter falsch (2 Kommentare, beide wachauer); der Aufrufer wollte vor dem Push posten.
