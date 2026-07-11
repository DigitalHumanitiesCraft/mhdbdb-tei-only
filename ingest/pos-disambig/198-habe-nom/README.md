# Batch-Log: #198 haben (NOM) — habe/hab/hawe unter lemma_2598

Provenienz-Log nach POS-TAGSET.md §6.3.5 (erster Batch unter `ingest/pos-disambig/`).

## Rahmen

- **Issue:** #198 „Herkulesaufgabe: haben (NOM)" (prio-1); Scoping-Kommentar chsteiner 2026-07-10.
- **Datum:** 2026-07-10
- **Modell:** Claude Fable 5 (claude-fable-5), 8 parallele Disambiguierungs-Subagenten
- **Prompt:** Kontext-Disambiguierung NOM vs. VERBAL mit expliziten mhd. Indikatorlisten
  (Determinativ/Possessiv/Präposition/Koordination vs. Subjektpronomen/Partizip/daz-Satz/
  Imperativ/Negation); bestehendes `@pos` nur als Prior deklariert; je Fall Begründung +
  Konfidenz (high/medium/low). Interleaved-Batching (8 × ~89 Fälle, Dateien/Genres gemischt).

## Bestand und Verfahren

Extraktion: alle `<w>` mit `lemmaRef`-Token `lexicon.xml#lemma_2598` und Oberflächenform
`habe|hab|hawe` (case-insensitiv): **714 Tokens in 102 Dateien** (Issue-Scoping: „715",
Differenz 1 durch exakte Token-Zählung). Davon 183 mit NOM im Compound-Tag.

Konservative Anwendungsregel: Änderungen nur bei `confidence=high` und nur in der
habe-„Besitz"-Kategorie. Ergebnis:

| Aktion | Anzahl | Bedeutung |
|--------|-------:|-----------|
| MOVE   | 25 | Substantiv *habe*: `lemmaRef` → `lemma_2593`, `pos="NOM"`, `@ana` entfernt, `@corresp` → type_8699 (habe) / type_80494 (hab) |
| STRIP  | 179 | verbal: NOM aus Compound-`@pos` gestrichen, sonst unverändert |
| REVIEW | 6 | zurückgehalten (houwe-Verdacht bzw. Konfidenz < high), byte-identisch belassen |
| KEEP   | 504 | verbal ohne NOM im `@pos`: kein Handlungsbedarf |

Zentrale Befunde:

1. Von den 183 NOM-getaggten Tokens ist nur **1** ein echtes habe-Substantiv
   (TKA_950041520_4 „von einer gar bosen habe"); 179 sind verbal (Konjunktiv/VEX),
   3 bleiben als REVIEW.
2. **24 echte habe-Substantive** steckten umgekehrt in rein verbal getaggten Tokens,
   fast alle WZB-Bibelprosa („alle seine habe" = Vulgata *substantia/opes*).
3. **hauen/houwen-Fehllemmatisierung** (separater Folge-Befund, nicht Teil dieses
   Batches): 12 Tokens der Formen *hawe/habe* in Fecht-, Koch- und Lehrtexten
   (AC2, AC3, CEFB, DES2, FWWB, KFB, MR2) gehören zum Verb *houwen* bzw. den
   Substantiven *hou* „Hieb" (lemma_61268) / *houwe* „Haue" (lemma_9644), sind aber
   unter lemma_2598 *haben* lemmatisiert. Alle in `review-faelle.csv` gelistet.

`@ana`-Entscheidung bei MOVE: Die alten Sense-Referenzen zeigen auf lemma_2598-Senses;
nach dem Umhängen wären sie lemma-fremd. Sie wurden entfernt und sind vollständig in
`diff-liste.csv` (Spalte `alt_ana`) dokumentiert, damit Schritt 2 des Issue-Plans
(Sense-Split lemma_2598 → lemma_2593, KZW-Review) sie re-mappen kann.

## Dateien

- `diff-liste.csv` — alle 714 Fälle: alt/neu für pos, lemmaRef, ana, corresp; Verdict,
  Konfidenz, Begründung, Kontextzeile (Semikolon-getrennt, UTF-8-BOM für Excel)
- `stichprobe-50.csv` — 50 Zufallsfälle aus den 204 Änderungen (Seed 198, reproduzierbar)
- `review-faelle.csv` — 17 Fälle für menschliches Review: 6 REVIEW (3 davon mit
  verbleibendem NOM unter lemma_2598), alle Konfidenz-<-high-Fälle, alle
  hauen/houwen-Verdachtsfälle
- `actions.json` — LLM-Verdicts aller 714 Fälle (Verdict, Aktion, Begründung,
  Konfidenz): die `--actions`-Eingabe des Anwendungs-Skripts
- `cases.json` — Extraktions-Stand der 714 Tokens vor dem Batch (Datei, xml:id,
  Form, alte Attribute, Kontext): die `--cases`-Eingabe des Anwendungs-Skripts

Anwendungs-Skript: `scripts/ingest/pos-disambig/fix-198-habe-nom.py`. Ein Replay
(Dry-Run oder `--apply`) setzt den Korpus-Stand vor dem Batch voraus
(Parent-Commit), weil das Skript die Alt-Werte verifiziert, bevor es schreibt.

## Invarianten (geprüft)

- Nur `@pos`/`@lemmaRef`/`@ana`/`@corresp` geändert; Token-Text, Reihenfolge, `xml:id`
  und Zeilenenden byte-identisch (Diff: exakt 204 geänderte Zeilen in 70 Dateien).
- Nachher-Zählung: lemma_2598 = 87.205 Tokens (−25), davon 3 mit NOM (= die 3
  dokumentierten REVIEW-Fälle); lemma_2593 = 100 Belege (75 + 25).
- Kein neuer variants-Typ nötig (alle MOVE-Formen habe/hab existieren unter lemma_2593).

## Ausdrücklich NICHT Teil dieses Batches

Schritt 2 des Issue-Plans: `<pos>NOM</pos>`-Entfernung aus dem lexicon.xml-Eintrag
lemma_2598 und der Sense-Split (welche der 8 Senses sind nominal und wandern zu
lemma_2593) — einzige philologische Entscheidung, liegt bei KZW (Nutzungstabelle im Issue).
