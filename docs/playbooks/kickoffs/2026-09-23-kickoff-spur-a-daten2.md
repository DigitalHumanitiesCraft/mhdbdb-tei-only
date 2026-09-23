# Kickoff Spur A `mhdbdb-daten2`: die durchentschiedene Datenarbeit, seriell

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 23.09.2026.

**1. Autorisierung.** chsteiner hat diesen Lauf am 23.09.2026 freigegeben. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deinen eigenen Zweig, PRs öffnen, höchstens ein Statuskommentar und ein Relabel je Vorgang, den du anfasst. **Nicht**: mergen (das tut Christian), auf `main` pushen, Tickets schließen, Externe kontaktieren. Der Text erteilt keine technische Berechtigung: was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt, siehe 9. `auto:checkin` ist für diesen Lauf freigegeben (chsteiner, 23.09.), weil er erreichbar ist: du fragst unterwegs, statt zu schätzen.

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: ein Sessionname kann beim Antworten längst einer anderen Session gehören. Die Koordination ist wach und antwortet in Minuten.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees
2. `docs/playbooks/BETRIEBSVERTRAG.md`
3. `docs/playbooks/kickoffs/2026-09-23-issue-abbau.md`, der Laufplan, **besonders §2 Spur A, §3 Dateibesitz, §4 Freeze**
4. `docs/DATA-MODEL.md` → Data-Change-Lifecycle
5. **#387, #418, #464, #267, #252 mit allen Kommentaren** (`gh issue view N --json title,body,comments`). Die Entscheidungen von @wachauer stehen ausschließlich im Thread
6. `docs/POS-TAGSET.md` §2 (Verschmelzungen) und §6
7. Als Muster für Skripte: `scripts/apply-308-375-432.py` und das Laufskript des Datenlaufs vom 21.09., `scripts/ingest/pos-disambig/apply-366-375-371.py` (Trefferzahl je Ersetzung, Ist-Zustand je Token vor dem Schreiben prüfen, Abbruch bei Abweichung)

**Besonders tragen für dich:** Data-Change-Lifecycle vollständig; neue Variantentypen prägen, nie einen bestehenden umhängen (Regel aus #367); `extract-variants.py` **ohne** `--apply` vor und nach dem Lauf, die Differenz muss genau deine neuen Typen zeigen und null zusätzliche Mehrdeutigkeiten; jedes Token, das `@lemmaRef` bekommt, trägt auch `@pos` und `@corresp`. **Und die Regeln, die dein Ergebnis binden:** Versions-Bump an allen fünf Stellen, gegatete Zahlzeilen mitziehen (§3 des Laufplans), `revisionDesc` je geänderter TEI-Datei.

**Abbruchklausel:** weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es, statt es aufzulösen. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit hat ihn mit `claude --bg --worktree mhdbdb-daten2` angelegt: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\mhdbdb-daten2`, Zweig `worktree-mhdbdb-daten2`, aus `main` bei `ae2e7a5fa` oder später. Die Koordination nennt dir in ihrer Begleitnachricht den tatsächlichen HEAD.

**Erste Handlung, vor allem anderen:** miss `pwd`, `git branch --show-current`, `git rev-parse --short HEAD`, halte sie gegen die Angaben oben und melde das Ergebnis, zusammen mit dem Commit des gelesenen Laufplans. Bei Abweichung ändere nichts, melde und warte auf einen Neustart durch die Koordination. Danach die Basis messen (`git fetch --quiet origin`, `git rev-list --count "origin/main...HEAD"` muss 0 sein, sonst melden). Einen sprechenden Arbeitszweig `claude/daten-0923-a1` darfst du anlegen; sag es.

**`node_modules`:** die Koordination hat `npm ci` in deinem Baum laufen lassen oder sagt dir, dass du es tun sollst.

---

## 5. Was dir gehört, und was nicht

**Dir allein:** `tei/`, `authority-files/`, `data/`, `api/`, `scripts/build-*.py`, `scripts/sync/`, `scripts/ingest/`, `ingest/`; die Versionsliterale (`build-corpus-index.py`, `build-authority-index.py`, `assets/js/lib/corpus-loader.js`, `docs/TEI-MODEL.md` §11, `docs/INDEX.md` Z. 111); **zeilengenau** die von `scripts/audit/doc-count-audit.py` gegateten Zahlzeilen in den Dateien, die §3 des Laufplans nennt (die Fundstellen liefert das Gate selbst, miss sie vor dem Zug); als Freeze-Ausnahmen genau diese Stellen: `docs/POS-TAGSET.md` (neuer Absatz zur #387-Konvention), `docs/TEI-MODEL.md` (`no-print`-Bedeutung und §6.5a), `sources/README.md` Z. 183.

**In `docs/INDEX.md` nur Z. 111.** Die Datei wird parallel von PR #469 geändert (fremde Session, nicht anfassen).

**Nicht deins:** alles andere, insbesondere `playground/`, `assets/js/` außer `corpus-loader.js`, die übrigen Zeilen der HTML-Seiten (Spur B), `scripts/run-tests.js`, `testing/`, `package.json` (Spur C), **`docs/DEVELOPMENT.md` und `scripts/README.md`** (wegen #469 auch für dich eingefroren). **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend und **als letzten Commit**, unmittelbar nach `git fetch origin`; kein `merge`, kein `rebase` dafür. **Deine Fehlerjournal-Nummern sind 66 bis 69.** Dein Reviewer-Memory in einer eigenen Datei unter `.claude/agent-memory/fable-reviewer/`, als eigener Commit nach der Runde.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push auf gepushte Historie, keine Änderung unter `~/.claude/`, kein Eingriff in den Hauptcheckout.

**Maschinenweit exklusiv: Port 8080.** `npm test` und `npm run serve` belegen ihn. **Fordere ihn bei der Koordination an, bevor du testest, und melde ihn frei.** Du hast Vorrang vor den anderen Spuren. **Indexversionen** gehören dir allein; vor dem Bump `gh pr list` auf beanspruchte Nummern prüfen.

**`--allow-dirty`:** die Builds verweigern einen unsauberen Baum, der Lifecycle verlangt aber den gemeinsamen Commit von TEI, Indexen und `api/`. Nimm `--allow-dirty`, **nie `git stash`**.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` ist vor deinem ersten Push Pflicht; melde und warte, statt auf `fable-advisor` auszuweichen oder ohne Runde zu pushen.

## 6. Was eingefroren ist

`CLAUDE.md`; die 15 promptotyping-Dokumente in `docs/` bis auf deine Ausnahmen oben und `docs/JOURNAL.md`; `docs/playbooks/`; `.github/workflows/`; `scripts/audit/`; `docs/DEVELOPMENT.md`; `scripts/README.md`. **Inbox:** Abschnitt „Änderungswünsche" am Ende des Laufplans. **Format eines Wunsches:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum. Du meldest ihn sofort an die Koordination, sie trägt ein oder lehnt ab. **Grund:** ändert eine Spur eine Datei, die jede Session beim Start lädt, arbeiten die anderen unter geänderten Regeln, ohne es zu merken (01.09.2026, inhaltlich richtig und auf dem falschen Weg).

---

## 7. Die Wellen, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach, bevor du sie verwendest, auch die, die deinen eigenen Befund stützen. Ein Widerspruch wird gemeldet, auch wenn er deine Arbeit nicht betrifft. Die Koordination hat ihre Zahlen im Laufplan mit „gemessen (K)" markiert; alles andere stammt aus Auditberichten von Subagenten und ist ungeprüft. **Keine Labelabfrage als Arbeitsgrundlage.**

**Reihenfolge begründet:** A1 ist klein und voll entschieden und prägt Typ und Sense nach bekannten Mustern; A2 ist strukturell ohne Lemmaarbeit und braucht den Stand nach A1; A3 ist das größte Paket mit offener Kollision.

### A1: #387, #418, #464 in einem PR, ein Rebuild, Bump auf 4.2.19 / 1.9.9

- **#387:** die 21 Tokens aus KZWs zwei Tabellen vom 17.09. **Entschieden:** Lemma und Wortart je Token. **Vorab entschieden von der Koordination:** das Doppeltag wird als `NOM ADJ` geschrieben, weil der Bestand `NOM ADJ` 119.501-mal und `ADJ NOM` 0-mal trägt (gemessen (K)); der Statuskommentar sagt KZW das als Reihenfolgekonvention. Der erklärende Kommentar steht als `@reason`. Die Annotationskonvention für substantivierte Adjektive kommt als neuer Absatz nach `docs/POS-TAGSET.md`. Neuer Variantentyp für `vrow̆e` unter `lemma_7260` (KZW hat ihn freigegeben). **Nachzumessen:** Ist-Zustand jedes der 21 Tokens, höchste vergebene Typnummer.
- **#418:** 12 offene Belege: 7 → `lemma_2923`, 3 → bestehender `lemma_9644_sense_15624`, 2 (`GAR_1530_5`, `MR2_12484100113100_4`) → **neuer Sense** an `lemma_9644` mit den drei Konzepten aus `lemma_2923_sense_4697`. `AC3_23010_1` ist seit #416 erledigt. **Nachzumessen:** die Zuordnung je Token aus dem Thread, der Ist-Zustand. **Zusätzlich liefern:** die Zahl „Typ-IDs mit mehr als einem Lemma" vor und nach dem Lauf, in die Statuskommentare an #418 und #416 (in #418 zugesagt).
- **#464:** zwei Tokens, `@pos` von `PRO VRB` auf `VRB PRO` (KZW 22.09.), `@reason` mit der Verschmelzung, keine Token-Trennung. `etym` in `lexicon.xml` auf `zeln` + `er` umstellen, wie KZW es erwartet. **Haltepunkt nur**, wenn die bestehende `etym`-Struktur dabei eine Verknüpfung verlöre.

**Stoppbedingungen A1:** ein Token, dessen Ist-Zustand nicht dem Thread entspricht; eine Frage, die KZW nicht entschieden hat.

### A2: #267 und #252, erst nach Christians Merge von PR 1

Frisch von `origin/main` mit PR 1 darin (neuer Zweig; melde, bevor du ihn anlegst). Bump nur, wenn der Rebuild eine Differenz zeigt (`check-index-version-bump.py` entscheidet).

- **#252, zuerst die Schuld:** die Kontextliste der **fünf Komma- und Doppelpunktfälle**, die KZW am 22.09. angemahnt hat, als Entwurf an die Koordination (die postet nach Christians Freigabe). Dann die Migration: nur das Muster `( caesura )` → `<gap/>`, umgebender Text sowie Satz- und Redezeichen bleiben. Freigegeben sind die **846** nach der Zählvorschrift im Kommentar vom 14.09. Weicht deine Zahl ab, melde die **xml:ids** der Differenz, nicht die Anzahl, und fasse die zusätzlichen nicht an. `docs/TEI-MODEL.md` §6.5a zieht mit.
- **#267:** neun Header: Marker `n="excerpt-only"` → `n="no-print"`, Satz „Eine vollständige Fassung der Edition inkl. Apparat kann daher nicht angeboten werden." FR3: Marker entfernen. **Haltepunkt vor jeder Änderung an `availability/@status` und dem Beschränkungssatz in FR3**; das ist nicht entschieden, leg einen Vorschlag bei. `docs/RESEARCH.md` ist erledigt und wird nicht angefasst. Bedeutung von `no-print` nach `docs/TEI-MODEL.md`, `sources/README.md` Z. 183 zieht mit.

### A3: #228, nur wenn A1 und A2 durch sind und die Koordination zustimmt

Haltepunkt vor jedem Eingriff in `tei/NEIM.tei.xml` (die 39 `<note n>` tragen die Konkordanz, die #453 sichern will). Die Zählstelle `lexicon_entries` zieht mit.

## 8. Vorab entschieden, nicht neu zu verhandeln

Die Tabelle in §6 des Laufplans. **Widerspruch ist ausdrücklich erlaubt**, auch dagegen, und er geht an die Koordination, die ihn unter „Grenzverhandlungen" im Laufplan einträgt. Ein Einwand im PR-Text ist verloren, den öffnet nach dem Merge niemand. Zu einer Vorgabe, die dir eine Messung abnimmt (etwa die Tag-Reihenfolge), setzt du sie **nicht** um, wenn deine Messung widerspricht, sondern meldest mit Begründung.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`/Zweig/HEAD nach dem Lesen; je Welle der nachgemessene Umfang gegen den behaupteten; Port angefordert und frei; vor dem Bump die beanspruchten Nummern; Beginn und Ergebnis jeder Reviewrunde mit Rundennummer **und Kennung des geprüften Standes**.

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; Stoppbedingung; fehlender Agententyp; eine Entscheidung, die KZW nicht getroffen hat; die benannten Haltepunkte (#464 `etym`, FR3 `availability`, NEIM-Notes).

**Externer Zustand** (CI, `gh pr checks`): nicht blind warten, sondern `Monitor` mit einer Bedingung oder ein Hintergrundbefehl, der dich bei seinem Ende weckt. Bleiben die Checks leer, zuerst `gh pr view N --json mergeable`. **Auf dem Daten-PR wird der CI-Review-Bot rot**: öffne seinen Kommentar trotzdem und lies ihn, bevor du ihn abtust.

**Du darfst eine Welle für nicht durchführbar erklären**, mit Messung und früh. Das ist etwas anderes als die Abbruchklausel aus 3.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Das Werkzeug steht in keiner Liste und lädt über `ToolSearch` mit `select:PushNotification`; eine Fehlermeldung beim ersten Griff heißt nur, dass es noch nicht geladen ist. `rules/blockaden-melden.md`. **Umgeh eine Blockade nicht über eine andere Spur**: Berechtigungen gelten je Session.

**Kein Messfenster:** keine Welle misst eine Bedingung deines eigenen Prozesses; die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss je PR

1. `npm test` (Port anfordern), das Ergebnis ist die **VERDICT-Zeile**, nie durch eine Pipe, nie `npx playwright test`.
2. Gates lokal: `check-index-versions.py`, `doc-count-audit.py --check`, `check-no-em-dash.py --diff-base origin/main`, `build-pages.py --check`.
3. `fable-reviewer` **vor dem ersten Push**, mit Zweig und Basis, ob Commit oder Arbeitsbaum, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde und ihr Verbleib, **und der Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?** Bei Befunden eine zweite Runde. Halt den Arbeitsbaum still, solange sie läuft.
4. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit den drei Abschnitten „Was über den Einzelfall hinausgilt", „Rote Zeilen" (gemessene Verteilung aus `python C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\claude-code-setup\hooks\trockenlauf-auswerten.py`, deine Zeile), „Was zurück an Christian geht".
5. PR öffnen, **nicht mergen**, je Vorgang relabeln und einen Statuskommentar, Bericht an die Koordination.

### Definition of Done je PR, als Lesertest

Wer nur den PR liest, kann beantworten: welche Tokens wurden wie geändert und nach welcher Entscheidung (mit Fundstelle im Thread); welche Typnummern und Senses sind neu; was hat sich an Formen- und Mappingzahl geändert und woher kommt die Zahl; was bleibt für KZW zu entscheiden, und wo steht es.
