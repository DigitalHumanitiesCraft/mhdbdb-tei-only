---
name: issue-matrix-auto-frozen
description: Review-Fallen an build-issue-matrix.py / auto:frozen (#406, #271): Entscheidungsdatum 10.09. nicht 11.09., Labelzahl 20 nicht 16, Mutationsharness per git show ins Scratchpad
metadata:
  type: project
---

Runde 1 zu `claude/auto-frozen-label` (21.09.2026, Basis 49f960209, HEAD d460475f7).

- **#271-Einfrierdatum ist der 10.09.2026**, nicht der 11.09.: wachauer schlaegt
  um 15:24Z „bis Juni 2026" vor (Tippfehler), bestaetigt um 16:41Z „Ja, ich habe
  Juni 2027 gemeint." Der 11.09.-Kommentar (09:27Z) ist „Ja, mach 1. zu NEIM."
  und betrifft die Konkordanz. Die Ping-Liste in #44 zeigt #271 (2026-09-11),
  weil das die letzte Wortmeldung ist. Der #406-Kommentar vom 21.09. traegt den
  falschen Tag und ist die Quelle, aus der Docstring, CLAUDE.md und
  Commit-Message ihn uebernommen haben.
- **`gh label list` liefert 20 Labels** (5 auto + 6 area + 3 effort + 4 wait +
  2 Flags). Die „16" in CLAUDE.md stammt aus 5e051105d (05.08.), das noch kein
  `wait:*` kannte; die vier `wait:*` kamen mit 61f7f06a6 am selben Tag.
- **Mutationsharness** fuer den Selbsttest: Skript per `git show <sha>:pfad`
  ins Scratchpad, `str.replace` mit Zaehlung (`count == 1`), `--selftest`
  laufen lassen, FAIL-Zeilen zaehlen. Sieben Mutationen in 2 s; die alte
  Fassung des Ping-Falls (18b98c423) blieb unter „blockierte + FROZEN" wirklich
  gruen, die neue faellt.
- Das Ein-Satz-Schema fuer Autonomiestufen steht ausserhalb des Repos in der
  handgeschriebenen Legende von #44 (Tabelle mit Spalte „Was eine Session
  damit tut"); sie kennt `auto:frozen` nach dem Merge nicht. MASTERPLAN:51
  nennt es seit 1545ab1b5 (Runde 2).

Runde 2 (21.09.2026, Commit 1545ab1b5, Vokabularpruefung in `pruefe()`):

- **„Faellt aus jeder Tabelle, steht nur noch in der Kopfzahl" gilt nur fuer
  `auto:`.** Gemessen per `baue()` im Scratchpad (importlib): ein fremdes
  `area:`/`effort:` steht in seiner Autonomietabelle mit dem Rohwert in der
  Zelle (`| #12 | T | datenbank | small |`), weil `zeile()` den ersten
  Treffer ungefiltert schreibt; und ein fremdes `auto:` zaehlt in „Nach
  Bereich" weiter mit. Der Satz stand dreimal im Commit (Kommentar :156,
  Fehlermeldung :330, DEVELOPMENT.md:358) und im Auftragstext.
- Der Tageslauf ist `--apply` (issue-matrix.yml:64), nicht `--check`;
  `--check` ist der Vorflug in MASTERPLAN:154 und den Kickoffs.
- Vokabular steht im Repo dreimal: Konstanten, Skript-Docstring :32-36,
  CLAUDE.md:149-153; nur AUTO_STUFEN<->ACHSEN ist per Selbsttest gekoppelt.
- Mutationsprobe ohne `git show`: Quelle lesen, `str.replace` mit
  `count == 1`-Assert, in Scratch-Datei schreiben, `--selftest` per subprocess,
  FAIL-Zeilen zaehlen. Drei Mutationen in einem Lauf unter 3 s.

**Why:** Datums- und Zahlenbehauptungen in diesem Diff kamen aus einer
Verdichtung (#406-Kommentar), nicht aus dem Thread; das wiederholt sich bei
jeder weiteren Runde an diesem Zweig.
**How to apply:** Bei Runde 2 die drei Datumsstellen und CLAUDE.md:147 gegen
diese Messungen halten, nicht gegen den #406-Kommentar.
