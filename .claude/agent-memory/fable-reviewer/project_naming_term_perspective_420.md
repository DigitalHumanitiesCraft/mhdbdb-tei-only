---
name: naming-term-perspective-420
description: Messmuster fuer die Term-Perspektive des Naming-Explorers (#420, 11.09.2026): Paritaet gegen Lindas Referenzdatei per raw.githubusercontent am Tag, die drei Records mit Term in beiden Gruppen, die 3 IW-Zeilen, die am Pin v0.2.2 anders attribuiert sind als nach Lindas Regel, Rundungssummen der Anteilsspalte
metadata:
  type: project
---

Runde 1 auf uncommittetem Arbeitsstand (`claude/agents-setup-network-check-08f1ri`), `playground/js/ui/tei/naming-explorer.js` Perspektive `lemma`.

## Lindas Referenzdaten sind ohne gh erreichbar
`https://raw.githubusercontent.com/lindabeutel/Naming-analysis/<tag-oder-sha>/data/<Werk>/analysis/figures_by_lemma_<lemma>_<scope>.json` und `.../data/<Werk>/categorization_<Werk>.json` liefern 200 (Tag `v0.3.0-beta`, Pin-SHA `2f16f0ea...`). `api.github.com/repos/lindabeutel/...` gibt 403 (Session an unser Repo gebunden), unser eigenes Issue per `api.github.com/repos/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/420` geht (Body vollstaendig, 0 Kommentare am 11.09.).

## Nachrechnen der Term-Perspektive in Python
Record zaehlt einmal je Term (Set ueber eig/deck/ant/epi), `bez` = Term in eig|deck|ant, `epi` = Term in epi, `share = round(mentions/total*100)`. ROL/helt: 78/22, erz 61, Ruolant 34/31/3/0/34/0/44; alle 22 Zeilen identisch mit ihrer Datei (scope `naming_variants`, helt hat epi 0). ROL/hêrre 222/23, erz 55, fig 167. TRO/got 133/11, Jupiter 17/9/8/0/17/1.

## Zahlen, die leicht falsch zitiert werden
- **bez+epi > mentions gibt es nur bei Term in beiden Gruppen im SELBEN Record: 3 Records im ganzen Index** (IW `der` Graf vom Schwarzen Dorn V. 5629, ROL `der` Gott V. 7720, TRO `got` Jupiter V. 14383), ENE 0. Die Zahl „Terme in beiden Gruppen ueber verschiedene Records" ist IW 23 / ENE 25 / ROL 29 / TRO 90 und belegt die Ueberschreitung NICHT (dort ist bez+epi == mentions).
- Anteilsspalte summiert wegen Rundung nicht auf 100: helt 98, hêrre 95; von 433 Termen mit >=2 Figuren nur 247 exakt 100 (Spanne 89..109). Lindas Datei summiert helt ebenfalls auf 98.
- `who` im Index: erz 7.239 / fig 3.154 / self 109 = 10.502 Records; `fig` ohne `by` = 2 (Skript-/JS-Kommentar sagen „3x im Iwein").
- **Am Pin v0.2.2 weichen 3 IW-Zeilen von Lindas Attributionsregel ab:** Lunete V. 2216 (`juncvrouwe`) und Gawein V. 4905 (`hêrre`, `Gawein`) sind bei ihr `unattributed`, bei uns `fig` ohne by; Laudine V. 1805 hat Nennende Figur ohne Bezeichnung, bei ihr `figure_speech`, bei unserem `build_record` `erz`. In v0.3.0-beta sind alle drei korrigiert (0/0), ein Pin-Bump loest es.
- Keine lower()-Kollisionen unter den Termen (IW 145, ENE 256, ROL 394, TRO 657), exakter Vergleich ist damit gleichwertig zu ihrem lower()-Vergleich.
- `naming-explorer.spec.js`: 23 `test(`; helt, hêrre, got sind alle `ant`, `alt` eig+epi: eine Mutation `BEZ_CATS = ['ant']` faengt die Suite nicht.

**How to apply:** Bei jedem Diff an der Term-Perspektive oder am Pin: das Python-Muster oben laufen lassen und gegen die Referenzdatei am Tag vergleichen, nicht nur die Kopfzahlen. Verwandt: [[naming-index-pin-review]].
