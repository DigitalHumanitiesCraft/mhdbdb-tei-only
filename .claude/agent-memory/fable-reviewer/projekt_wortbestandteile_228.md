---
name: projekt-wortbestandteile-228
description: Review-Wissen zu #228 Kennzeichnung reiner Wortbestandteile (component-only.js, noCorpus, Woerterbuch-Marke, Lemmaseite): Feldformate, Kontrollzahlen, Frontend-Anfuehrungszeichen, Laufplan als Anforderungsquelle
metadata:
  type: project
---
Stand 02.10.2026, Runde 1 zu Zweig `claude/lauf-b1-228` (Commit 154e36edc, Spur B1 des Laufs 02.10.).

**Ableitung und Formate (am Index 1.9.17 / Korpus 4.2.24 gemessen)**
- `lemma.id` und `etymology[].lemmaRef` tragen beide die Form `lemma_N` ohne `#` oder `lexicon.xml#`; 3.680 verschiedene genannte IDs, 0 Selbstverweise, 0 Verweise auf fehlende Lemmata. Der Selbstverweis-Guard in `buildComponentRefSet` ist deshalb theoretisch.
- Kontrollzahlen: 43.710 Lemmata, 42.460 Schluessel in `corpusIndex.lemmaIndex`, 1.285 ohne Schluessel, davon 273 als Bestandteil genannt. Mur `lemma_66692` (NAM, normalized `mur`) wird von `lemma_33528` Mûrouwe und `lemma_66691` Murstetten genannt; `lemma_4532` ouwe ist genannt und belegt. Prefix-Treffer im Woerterbuch: `mur` 40, `ouwe` 6, Kontrolle `zwivalten` (lemma_12015) 1.
- `noCorpus` gibt es im 1.9.17 noch nicht (0 Lemmata); die Spec `component-only.spec.js` mockt es per `page.route` auf dem echten Index. Ob A1 das Feld fuer genau die 1.285 setzt, ist B-seitig nicht pruefbar: FEATURES.md behauptet es schon.
- Veralteter Browser-Cache ist kein Loch: `corpus-loader.js` verwirft den Cache bei `cached.version !== AUTHORITY_INDEX_VERSION` (Z. 124-126), und A1 bumpt auf 1.9.18.

**Was haengt am Alten**
- `renderOccurrences` kehrt ohne `lemmaIndex[lemmaKey]` frueh zurueck, `#occurrencesSection` bleibt `hidden`: Belegstellen fuer Mur fehlen ohne eigenen Code.
- `woerterbuch.spec.js` lokalisiert nur `#entryGrid a` und `[data-lemma-number]`, ein zusaetzlicher `span` je Zeile bricht nichts.
- Die Registerzeile ist in `hilfe-korpussuche.html` Z. 445-446 beschrieben („Lemma und Wortart-Kuerzel"); der Commit erklaert die Marke stattdessen im lexicon.xml-Punkt von `hilfe-daten.html`.

**Runde 2 (Stand e1dd30b59, Basis db30475b3, 02.10.2026)**
- Befund 4 aus Runde 1 (`flex-shrink-0` ohne CSS-Regel) war falsch, siehe querschnitt_tests.md Tailwind; Korrektur auf `shrink-0` unschaedlich. `hidden` gewinnt gegen `flex` (Offsets 6801 > 6709), `mt-0.5` vorhanden.
- Gates gruen gemessen: `check-doc-inventories.py` 44/44 Specs, 11/11 lib-Module; `check-no-em-dash.py --diff-base db30475b3` leer; 0 typografische Anfuehrungszeichen in ausgelieferten HTML. report.json: expected 414, unexpected 0, 44 Dateien, Start 14:11:39 (6 s nach den Rebase-Commits, alle drei 14:11:33).
- `origin/main` war zur Runde 90f211d9a (ein Laufplan-Commit G3 ueber db30475b3, nur `kickoffs/2026-10-02-lauf.md`, keine Pflicht fuer B1); Merge-Base blieb db30475b3.
- `hilfe-korpussuche.html` Z. 445-446 „Jeder Eintrag besteht aus dem Lemma und einem Wortart-Kuerzel" bleibt eine Allaussage, die nach A1 fuer 273 Eintraege unvollstaendig ist; kein Verhaltensbefund, Formulierung.

**Zwei Fallen dieser Runde**
- Frontend-Anfuehrungszeichen: alle ausgelieferten HTML-Seiten (Wurzel, `lemma/`, `playground/`) tragen 0 typografische Zeichen U+201E/U+201C/U+201D (Grep-Tool, glob `{*.html,lemma/*.html,playground/*.html}`, count), seit PR #458 zu KZWs #440; neue „…“ in `hilfe-daten.html` fallen sofort auf. Messvorschrift steht in der Auto-Memory `feedback_deutsche_anfuehrungszeichen`.
- **Der Laufplan ist Anforderungsquelle, und er bewegt sich nach dem Abzweig:** `docs/playbooks/kickoffs/2026-10-02-lauf.md` bekam nach der Basis 5d5720399 zwei Commits (G2: `noCorpus` in A1; Ae1: DEVELOPMENT.md-Zeile fuer `component-only.spec.js`, sonst `check-doc-inventories.py` rot). Der Auftrag nannte die alte Basis; `git diff <basis> origin/main` auf den Kickoff zeigte die Pflicht, die der Commit nicht erfuellte (Gate 44 Specs gegen 43 Zeilen). Bei Laufplan-Spuren immer so messen.
