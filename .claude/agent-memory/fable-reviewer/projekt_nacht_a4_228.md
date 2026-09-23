---
name: nacht-a4-228-entannotieren
description: Review-Lehren aus #228 (Apparatnoten entannotiert, 165 Waisen-Lemmata geloescht, Nachtlauf A4 24.09.2026): gehaltene Waise reisst Sense-Typ-Verweis, ungegatete Lemmazahl-Stellen, Messrezepte
metadata:
  type: project
---

Review von 540733092 (Branch claude/nacht-a4-228, Basis d166fa4b1) am 24.09.2026, Runde 1.

- **Eine belegfrei gehaltene Waise reisst ihren Variants-Verweis ab.** `variants.xml` wird aus dem Korpus regeneriert; ein Lemma ohne Belege verliert dort seinen Eintrag samt Typen, behaelt aber in `lexicon.xml` sein `<sense ana="#type_N">`. Gemessen: `ana="#type_\d+"` in lexicon gegen `xml:id="type_"` in variants, origin/main 0 dangling von 21.560 Refs, HEAD 1 (`type_348958`, lemma_66692 Mur). Kein Gate sieht das: `check-authority-cross-refs.py` ueberspringt nackte `#frag` (Z. 225-229) und scannt nur `tei/`; der Index liest sense/@ana nicht.
- **Why:** Der Haltepunkt „fremde Verweise" schuetzt das Lemma, nicht seine ausgehenden Zeiger; das ist der #397-Fall (Fix macht „Mur ohne variants-Eintrag" wahr, der Zeiger haengt am Gegenteil).
- **How to apply:** Bei jeder Loeschung oder Haltung von Lemmata nach Regeneration die Menge `lexicon sense/@ana -> variants type` beidseitig messen.
- **doc-count-audit gatet `lexicon_entries` nicht in DATA-MODEL, FEATURES, DESIGN, TEI-MODEL-AUTH-FILES** (DOC_TARGETS Z. 258-343): dort blieben 9 Stellen bei 43,878, waehrend die gegatete Variants-Zeile derselben Tabelle (TEI-MODEL-AUTH-FILES.md:20) mitzog. Nachtlauf-Freeze erlaubt A nur gegatete Zahlzeilen (Kickoff Z. 85), also Freeze-Ausnahme noetig, nicht stiller Sweep.
- Messrezepte, die trotz Worktree-Guard laufen: `git show <rev>:pfad > /c/Users/.../Temp/x` einzeln; Python-Skripte in `$TEMP` mit relativem Repo-Pfad vom Worktree aus; `git grep -c 'lemma_N"' HEAD -- tei` je ID einzeln (Guard lehnt Globs, `$TEMP`-Variablen und Mehrfach-git in einer Zeile ab).
- Digit-Lemmata nach #228: lemma_53328 „1" (NEIM 63), 69748 „36", 69749 „42", 69750 „49" (je 1 in WVV); 69733 „46" geloescht. hapax-legomena.spec.js ankert auf `/^\d/` und haelt, solange die WVV-Ziffern annotiert bleiben (offene Frage in #228).
