---
name: spur-a-daten2-2026-09-23
description: Review Runde 1 von bf1440451 (#387/#418/#464, Index 4.2.19/1.9.9) am 23.09.2026, Spur A daten2; Messrezepte und was die Runde gefunden hat
metadata:
  type: project
---

# Spur A daten2, Runde 1 (23.09.2026), Commit bf1440451 gegen 081ad4d10

**Die #397-Antwort lag wieder im Laufzeit-Woerterbuch, nicht auf der Typ-Ebene.**
`extract-variants.py` ohne `--apply` meldet 256.787 / 42.626 / alle vier Zaehler 0 /
`>1 lemma` 0 / `>1 form` 613 und sieht nichts; der Vergleich der beiden
`authority-index.json.gz['variants']` (Basis per `git show origin/main:data/...`)
liefert **added 0, removed 0, re-pointed 2**: `froewen` lemma_7256 -> lemma_7250
(Form im Korpus: 35 unter 7260, 21 unter 7256, 1 unter 7250, also gegen ADR-021
Vorschrift B) und `hawe` lemma_2598 -> lemma_2923 (7 zu 6, 2598 leer, B-konform).
`vroewe` kippt NICHT, obwohl type_372388 unter 7256 neu ist: `vröwe` unter 7256
normalisiert schon auf `vroewe`, der Schluessel zeigte vorher dort hin.
ADR-021 (DECISIONS.md ~1288) fuehrt die Handlaeufe als Fixturen (gruen 0/0/0,
rot 5/0/1); jeder Datenlauf mit neuen Typen braucht dort die naechste Zeile.

**Why:** Dritter Lauf in Folge, bei dem der Typ-Zaehler gruen und das Woerterbuch
gekippt ist (hawsen 21.09., froewen 23.09.). Der Lifecycle in DATA-MODEL.md listet
den Vergleich nicht als Schritt, die Spur laeuft ihn deshalb nicht von selbst.

**How to apply:** Bei jedem Daten-PR mit neuen `type_N` zuerst `idx_diff`
(beide Dicts, added/removed/re-pointed, dazu Tokenzahl je (Form, Lemma) aus
tei/ per Regex) und das Ergebnis als Befund mit Fundstelle DECISIONS.md.

## Messrezepte dieser Runde
- Doppeltags und Attributreihenfolge: ein Regex-Scan ueber tei/*.xml (~1 min)
  liefert VRB PRO 156/156 mit @reason, PRO VRB 9.066/0, NOM ADJ 119.501/0,
  ADJ NOM 2/2 (Stand HEAD). Die Zahlen 154 / 9.068 in POS-TAGSET.md:52 sind
  der Stand VOR dem Commit; das Dokument behauptet sie fuer „all 667 files"
  am 23.09. Attributreihenfolge xml:id lemmaRef pos ana corresp reason: 0
  Verstoesse korpusweit; unbekannte Attribute an <w>: keine.
- WZB traegt auf main 235.981 CRLF bei 235.998 LF, also 17 nackte LF aus dem
  Bestand; die neue change-Zeile ist CRLF (HEAD 235.982/235.999). Kein Befund.
- tei_all + mhdbdb per lxml auf 19 Dateien: Schemaladen 20 s, dann Sekunden.
  FR1/FR3/ENE/ROT fallen mit „Invalid attribute reason for element w", FR2 nicht.
- `doc-count-audit.py --check` ist gruen, obwohl CONTRACTS.md:381 noch 256.783
  traegt: der Anker sitzt nur auf :380. Zweitzeile daneben immer selbst lesen.
- Sandbox lehnt `python -c` ab, sobald ein Pfad das Wort „Git" enthaelt;
  Skripte nach `$TEMP/rev-daten2/` und mit `-X utf8` starten.
- lexicon.xml lemma_28290 fuehrt gramGrp PRO, VRB (Reihenfolge); kein Skript
  vergleicht Token-@pos mit gramGrp (classify-lexicon-backfill.py nutzt
  Mengenschnitt), ADJ NOM ueberrascht keinen Konsumenten: Corpus-Index liest
  @pos nicht, Playground nutzt posAll aus dem Authority-Index.
- Issue-Threads: `gh --repo ... issue view N --json title,body,comments` in
  Datei, dann dump_issue.py; #387 hat 4, #418 11, #464 1, #416 8 Kommentare.
