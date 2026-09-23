---
name: nacht-a4-228-runde2
description: Runde 2 zu #228 (f13277280): das Runde-1-Rezept fuer haengende sense/@ana-Typverweise war zu eng (Regex traf nur einwertige @ana); richtig gemessen 105 auf main, 187 auf HEAD, 82 neu durch die Entannotation
metadata:
  type: project
---

Review von f13277280 gegen 540733092 (Branch claude/nacht-a4-228), 24.09.2026, Runde 2.

- **Das Runde-1-Rezept `ana="#type_\d+"` misst nur einwertige @ana.** Ein `sense/@ana` ist im Lexikon meist eine Leerzeichenliste (main: 43.404 @ana-Attribute, 21.844 davon mehrwertig, 250.902 Typ-Tokens); das Regex sieht 21.560 Tokens und meldet 0 haengende, weil der eine einwertige Fall (Mur) behoben ist. Richtig ist Tokenisierung per `split()`: main 105 haengende Tokens gegen main-variants, HEAD 187 in 133 Senses, davon 82 neu durch 540733092 (Typen aus entannotierten GWTK/Apparat-Tokens, Beispiel type_370041 in lemma_10416_sense_16651: GWTK 3 Tokens vor, 0 nach der Entannotation). Kein Sense verliert alle Typen; Mur war der einzige einwertige.
- **Why:** Das ist `mengen.md` in Reinform: die Zahl 0 stimmte fuer die Menge des Regex, nicht fuer die Menge der Verweise. Die Invariante „kein haengender sense/@ana" galt auf main nie (105), ein Fix an einem Eintrag stellt sie nicht her.
- **How to apply:** @ana, @corresp, @lemmaRef immer per `split()` messen, nie per `attr="#id"`-Regex. Vor einem Klasse-A-Befund ueber eine Invariante die Basis mitmessen: haelt sie dort nicht, ist der Befund eine Vorbedingung des Repos und kein Bruch durch den Diff.
- Konsumenten von sense/@ana: keiner. build-authority-index.py liest an sense nur xml:id, def/@resp, note/@resp (Z. 188, 214, 222); check-authority-cross-refs.py ueberspringt nackte `#frag`. Der Gate-Lauf `--check` schreibt scripts/audit/authority-cross-refs-audit.json (im Baum, vor dem Abschluss auf git status pruefen).
- Guard: `python <absoluter Pfad mit "Git">` wird als git-Kommando abgelehnt; relativer Pfad vom Worktree aus laeuft.
