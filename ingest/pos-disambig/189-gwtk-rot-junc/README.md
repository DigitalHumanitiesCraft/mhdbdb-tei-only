# Batch-Log: #189 GWTK-Pilot — rott/rotten/rotte/roten + jungen/junger

Provenienz-Log nach POS-TAGSET.md §6.3.5 (zweiter Batch unter `ingest/pos-disambig/`,
Muster: `198-habe-nom/`).

## Rahmen

- **Issue:** #189 „Ambige Wortformen ohne Lemma-Annotation (GWTK-Pilotfall)"; Punkt 1
  des Issue-Plans. Punkt 2 (korpusweite Quantifizierung) war bereits erledigt (PR #210).
- **Datum:** 2026-07-12
- **Modell:** Claude Fable 5 (claude-fable-5), 4 parallele Disambiguierungs-Subagenten
- **Prompt:** Kontext-Disambiguierung über Kandidaten-Lemmata mit expliziten mhd.
  Indikatorlisten (attributiv/prädikativ/nachgestellt vs. Determinativ+Substantiv vs.
  Verbsyntax); je Fall Begründung + Konfidenz (high/medium/low). Interleaved-Batching
  (4 × ~70 Fälle). Kontext je Fall: Zielvers (markiert) ± 2 Folgeverse + Vorgängervers.

## Bestand und Verfahren

Anders als #198 (Umhängen annotierter Tokens) ist dies eine **Neu-Annotation**:
Die Ziel-Tokens waren komplett nackt (`<w xml:id="...">form</w>`, kein `@lemmaRef`,
kein `@pos`). Extraktion: alle nackten `<w>` der Formen `rott|rotten|rotte|roten`
und `jungen|junger` (case-insensitiv) in GWTK: **278 Tokens** (139 rot + 139 jung,
exakt die Zahlen aus dem Issue-Scoping).

Kandidaten-Lemmata (gegenüber dem Issue um zwei Homographie-Partner erweitert):
lemma_4954 *rôt* ADJ, lemma_4978 *rote* NOM/VRB (Schar; deckt per
lemma_4978_sense_7735 → concept_25153000 auch das **Saiteninstrument** ab),
lemma_10840 *roete* NOM, lemma_11330 *Rot* NAM, lemma_3157 *junc* ADJ
(substantiviert → pos NOM, Lemma bleibt), lemma_3162 *jungen* VRB,
lemma_3163 *jünger* NOM (discipulus).

Konservative Anwendungsregel: Änderungen nur bei `confidence=high`. Ergebnis:

| Aktion | Anzahl | Bedeutung |
|--------|-------:|-----------|
| ANNOTATE | 257 | `lemmaRef` + `pos` + `corresp` eingefügt |
| REVIEW | 21 | zurückgehalten (Konfidenz < high), byte-identisch belassen |

Verdict-Verteilung der 257 Annotationen: lemma_4954/ADJ 71, lemma_3157/ADJ 70,
lemma_3157/NOM 63 (substantiviert), lemma_4978/NOM 45, lemma_4954/NOM 8 (substantiviert).

**Moderations-Pass (dokumentierte Eingriffe):** 4 Fälle in Instrumentenaufzählungen
(V. 4860, 6072, 7185, 12200: „gigen, rotten, pfiffen/harpffen") wurden von den
Subagenten mit low geflaggt, weil das Saiteninstrument nicht in der Kandidatenliste
stand. Lexikon-Prüfung ergab: lemma_4978 trägt die Instrument-Bedeutung selbst
(sense_7735, `ana="#type_17204"` = Form „rotten"). Die 4 Fälle wurden deshalb auf
lemma_4978/NOM/high gehoben; zwei Subagenten (Shards 3+4) hatten identische Kontexte
(V. 621, 22335) selbständig genauso eingestuft. Vollständig in `diff-liste.csv`
gekennzeichnet.

Zentrale Befunde:

1. **Goldstandard getroffen:** Verse mit rôt(4954) + munt(4252): 46 → **73**
   (Akzeptanzkriterium ≥ 73; externe Zählung der Anfragenden: 78 Belege inkl.
   versübergreifender Fälle). *junc*-Belege: 126 → **259** (Erwartung ~262
   ± substantivierte Formen; der Rest steckt in den 21 Review-Fällen).
2. GWTK-Coverage: 64,72 % → 64,93 % (+257 annotierte Tokens).
3. Zwei neue variants-Typen geprägt: `type_372361` (rotte) und `type_372362`
   (rotten) unter lemma_4954 — die Formen existierten dort bisher nicht, weil
   genau diese Fälle nie annotiert waren.
4. Kein einziger Fall für lemma_3162 (Verb *jungen*), lemma_3163 (*jünger*
   discipulus) oder lemma_11330 (NAM); 1 medium-Fall für lemma_10840 (*roete*,
   V. 4800) liegt im Review.

`@ana` (Sense-Referenz) wurde bewusst NICHT gesetzt: Die Sense-Zuordnung ist
kuratorisch (gleiche Regel wie bei den #198-MOVEs).

## Dateien

- `diff-liste.csv` — alle 278 Fälle: neu für pos, lemmaRef, corresp (alt = leer);
  Verdict, Konfidenz, Begründung, Verszeile (Semikolon-getrennt, UTF-8-BOM für Excel)
- `stichprobe-50.csv` — 50 Zufallsfälle aus den 257 Änderungen (Seed 189, reproduzierbar)
- `review-faelle.csv` — 21 Fälle für menschliches Review (20 medium + 1 low),
  darunter die Rotes-Volk-Episode (V. 15291 ff.), „der rotten faigen hoffartt"
  (V. 15373) und der einzelne roete-Kandidat (V. 4800)
- `actions.json` — LLM-Verdicts aller 278 Fälle (Lemma, POS, Begründung, Konfidenz):
  die `--actions`-Eingabe des Anwendungs-Skripts
- `cases.json` — Extraktions-Stand der 278 Tokens vor dem Batch (xml:id, Form,
  Vers-Nr., Verskontext ± 2 Verse): die `--cases`-Eingabe des Anwendungs-Skripts

Anwendungs-Skript: `scripts/ingest/pos-disambig/fix-189-gwtk-rot-junc.py`. Ein Replay
(Dry-Run oder `--apply`) setzt den Korpus-Stand vor dem Batch voraus (Parent-Commit),
weil das Skript verifiziert, dass die Ziel-Tokens noch nackt sind, bevor es schreibt.

## Invarianten (geprüft)

- Nur öffnende `<w>`-Tags der 257 ANNOTATE-Fälle geändert; Token-Text, Reihenfolge,
  `xml:id` und Zeilenenden byte-identisch (Diff: exakt 257 geänderte Zeilen).
- Schema-Validierung: GWTK.tei.xml valide gegen `schema/mhdbdb.rng`.
- `revisionDesc`-Change-Eintrag in GWTK.tei.xml ergänzt (§6.3.5).
- variants.xml-Regenerat: nur +2 Typen (372361/372362), 0 Form-, 0 Lemma-Umhängungen.
- Positionszählung unverändert für Bestands-Tokens (Neu-Annotationen erweitern die
  `<w>`-mit-`@lemmaRef`-Menge; das ist der Zweck des Batches und im Corpus-Index-Bump
  4.1.7 dokumentiert).

## Ausdrücklich NICHT Teil dieses Batches

- Die 21 Review-Fälle (Entscheidung KZW; Liste in `review-faelle.csv`).
- Dieselben Formen in anderen Texten (korpusweit >100 Texte, siehe
  Quantifizierung in #189/PR #210): Folge-Batches nach diesem Pilot-Muster,
  Inhaltswort-Schicht (*minne* zuerst) als Serien-Issues.
- Golden-Set-Kalibrierung nach §6.3.2: Der Batch nutzt stattdessen den externen
  Goldstandard der Anfragenden (78 *rôter munt* / 262 *jung*) als
  Validierungsreferenz; Abgleich bestanden (s. o.).
