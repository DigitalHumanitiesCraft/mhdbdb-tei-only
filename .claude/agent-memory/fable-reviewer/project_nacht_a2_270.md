---
name: nacht-a2-270
description: Review #270 commentRespName (Authority 1.9.10, Nachtlauf A2 23.09.2026): Messwege ohne Build-Lauf, Worktree-Guard, die drei frozen Doku-Stellen, die der Diff nicht erreicht
metadata:
  type: project
---

Review von `claude/nacht-a2-270` (593bdcb40 gegen 347998146), Runde 1, 23.09.2026 (Commit 593bdcb40 um 20:47 +0200; die erste Fassung dieser Zeile und die MEMORY.md-Indexzeile schrieben 24.09.).

**Messwege, die ohne Rebuild und ohne Testlauf tragen:**
- Index gegen Basis: `git show <basis>:data/authority-index.json.gz > $TEMP/x.gz` (git-Aufruf allein, sonst lehnt der Worktree-Guard ab), dann rekursiver Python-Walk beider gunzip-JSONs. Ergebnis 2 Diffs: `$.version` und `lemmata[22933].senses[0].commentRespName`.
- Build-Funktionen in-process per `importlib.util.spec_from_file_location` auf `scripts/build-authority-index.py`; `load_contributor_names()` liefert 54 (52 `contrib_*` + `mhdbdb-team`, `dhcraft`), `resp_name` beendet mit SystemExit bei fremdem Praefix, unbekannter ID und leerer ID.
- Der Worktree-Guard lehnt jedes Kommando ab, das einen Pfad mit „Git" enthaelt UND ein git-Wort; Probe-Skripte nach `$TEMP` (Write) und mit relativen Pfaden aus dem Worktree starten. `python -X utf8` wegen der Emoji-Ausgaben des Builds.

**Was nach #397 an der alten Invariante hing (contributors.xml wird nicht gelesen):**
- `ui-helpers.js:581` `totalAuthorityFiles = 7` zaehlt Index-Sammlungen (`authorityData.files`), nicht gelesene Dateien; bleibt richtig.
- `check-index-version-bump.py` ist inhaltsbasiert, keine Dateiliste; unberuehrt.
- `data-integrity.yml` triggert auf `authority-files/**`, Freshness-Step (Z. 418-442) ohne `if:`; der harte Fehler in `resp_name` greift dort.
- `api/index.html` nennt weder resp noch contributors (Kontrollwert `lemmata` 1 Treffer).
- Nicht mitgezogen, weil eingefroren und nicht in der Ausnahmeliste: `DATA-MODEL.md:238-243` (Index-Schema ohne `commentRespName`, „the three curated fields"), `DATA-MODEL.md:499-511` XPath-Referenz ohne contributors.xml-Zeile, obwohl Z. 893 dorthin verweist; `DATA-MODEL.md:907` „As soon as an index is rebuilt it is mandatory" gegen die neue Routingzeile 903 (Rebuild mit leerem Diff) und Z. 909.

**Runde 2 (9abad9dae, 23.09.2026, drei Fix-Commits):**
- Die Routingzeile 903 (Bump nur bei Diff) ist mit dem Gate konsistent (`check-index-version-bump.py:115` `if old == new` = OK) und mit ADR-018 :1149 („a change to a name ... needs a rebuild and a bump"); der Widerspruch sitzt allein in DATA-MODEL.md:907 („dropped only in the rows without a rebuild"), eingefroren, nicht in der Ausnahmeliste. DECISIONS.md:1093 ist der Praezedenzfall (Rebuild ohne Diff, kein Bump).
- Schemabeschreibungen des Authority-Index liegen an drei Orten: DATA-MODEL.md:238-243 (Block), :499-511 (XPath), TEI-MODEL-AUTH-FILES.md:219 („Index mapping"); CONTRACTS.md:927 ist die vierte (§G.3, normativ) und hatte commentRespName schon in Runde 1. Bei einem neuen Sense-Feld alle vier greppen (`grep -rl commentRespName --include=*.md`).
- contributors.xml: 52 person/52 persName, 2 org/2 orgName, `el.find()` trifft also je genau einen Namen.
- Spec liegt unter `testing/tests/`, nicht `testing/`; ein Glob auf `testing/*.spec.js` laeuft still leer (Kontrollwert „Kommentar von" = 4). Lemma-Seite ist `lemma/lemma-page.js`, kein `lemma/js/`.
- Datumsfehler in Runde 1: Memory mit 24.09. beschriftet, Commits sind vom 23.09. (git show -s --format=%ci).

**Runde 3 (a7aee19a1, 23.09.2026):** Die drei frozen Stellen aus Runde 1 (238-243, 499-511, 907) und TEI-MODEL-AUTH-FILES:219 sind seit 9abad9dae/a7aee19a1 mitgezogen; die MEMORY.md-Indexzeile sagt noch „nicht mitgezogen". Klassensuche nach A2-falschen Zeilen: `rg -i 'contributors\.xml' docs README.md playground/readme.md api/index.html hilfe-*.html scripts/README.md` gefiltert auf Negations- und Zaehlwoerter; einzige noch falsche Zeile ist `docs/playbooks/MASTERPLAN-EINZEL-LEMMA-KURATION.md:102` („wird nirgends angezeigt"), obwohl der Kickoff auf main (cdd8e061f, Z. 186) sie als „nicht falsch" fuehrt. README.md:151 und hilfe-daten.html:250 bleiben wahr (Sammlung / Suche). Die drei Doku-Gates (check-doc-inventories, check-index-versions, check-no-em-dash --diff-base) laufen in Sekunden und ohne Server; alle gruen. Rest-Spannung DATA-MODEL:908 „Otherwise ... mandatory" gegen :910 und DECISIONS:1093 (Pruef-Rebuild ohne Diff) ist vor-#270 und war nie Gegenstand.

**Spec-Anker statisch geprueft:** `#lemmaContent`/`#sensesContent` in `lemma/index.html:211/245`, `lemmaResults` in lemma-explorer.js:177, Router `#lemmata&q=` -> showLemmataWithSearch (router.js:42-44), Suche „abba" trifft 3 Lemmata (sabbat, Abbach, Abba) < maxResults 50. Nicht mehr geprueft: wie `lemmaItemButtons` ({text, action}) zu `onclick` gerendert wird.
