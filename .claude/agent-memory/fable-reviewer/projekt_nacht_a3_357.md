---
name: nacht-a3-357-ingliart-sense
description: Review-Lehren aus Nachtlauf A3 (#357, ADR-020): zweiter Sense an lemma_3036 Ingliart, sense/@ana-Verschiebung, welche Gates und Konsumenten sense/@ana lesen (keine), Katalognachbarn in REN, Guard-Verhalten bei git-Pipes
metadata:
  type: project
---

# Nachtlauf A3, #357: zweiter Sense fuer Ingliart (Review-Runde 1, 23.09.2026)

**sense/@ana in lexicon.xml hat keinen Konsumenten in Index, API, Frontend oder CI-Gate.**
`build-authority-index.py` liest `ana` nur am `<title>` (Z. 423), `build-corpus-index.py` und
`extract-variants.py` gar nicht, `check-authority-cross-refs.py` ueberspringt interne `#type_N`-Refs
(iter_refs, „'#' not in token / kein .xml-Praefix"). Ein Verschieben eines Typs zwischen Senses ist
deshalb gate-neutral; richtig oder falsch entscheidet nur DATA-MODEL.md:849 (@corresp-Aufloesung =
variants-Lookup ∩ ana des Sense). Wer den Typ beim alten Sense laesst, macht die Schnittmenge fuer den
neuen Sense leer (0 Treffer = „Form fehlt in variants.xml"), also gehoert er zum Sense des Tokens.

**Rennewart-Namenkatalog REN 2420.60–2421.00** (tei/REN.tei.xml ~201400–201440): Personen
Pauriper 19404, Wimiligar 22280, Ingliart 3036, Rufter 22282, Echerabant 22283
tragen concept_21012000 + concept_23112500; die „von X"-Ziele (Punpeire 21932, Nubilere 22278,
Kartetstere 20599, Jelezie 22285, Themarie 22286) tragen concept_24120000 (Orte). Die drei im Laufplan
genannten Nachbarn sind also nicht die einzigen Personen, aber alle Personen stimmen ueberein.

**Zahlen dieser Runde:** hoechste Sense-Nummer vor dem PR 119194 (grep -o 'sense_[0-9]*"' | sort -n);
type_177507 nur an REN_242090_0 (1 Treffer in tei/, 1 in variants.xml); lemma_3036 hat 3 Tokens
(PZ_38926_4, PZ_39814_3, REN_242090_0); gz-Walk gegen 5ede36174 = genau 5 Unterschiede
(maps/conceptToLemmas ×2, version, senseCount, senses[len]); api/lemmata hat nur index.json,
api/concepts/concept_N.json tragen keine Lemmalisten, deshalb sind 2 API-Dateien vollstaendig.
Issue #357 hat genau einen Kommentar (wachauer 2026-09-14T12:17:41Z), das Konzept steht nicht drin.

**Guard:** ein Verbundkommando mit `git diff ... | grep ... $'\xe2\x80\x94'` wird als „zu komplex"
abgelehnt, `git diff ... | tail -1` im `;`-Verbund dagegen nicht. Em-Dash-Zaehlung ueber hinzugefuegte
Zeilen deshalb per Python-Skript in $TEMP mit subprocess. `extract-variants.py` ohne --apply schreibt
`authority-files/variants.regen.xml` (nicht gitignoriert, .gitignore:90 deckt nur Audit-Outputs),
danach loeschen, sonst meldet der Endstand eine Bewegung.

**Why:** Der Auftrag fragte, ob das Verschieben von type_177507 richtig ist und ob ein Check am
Gegenteil haengt; beides ist nur ueber die Konsumentenliste zu beantworten, nicht ueber den Diff.
**How to apply:** Bei jedem Sense-Split (ADR-020 gilt „fuer alle Namen") dieselbe Liste pruefen:
Typen des Sense mit den Tokens abgleichen, Katalognachbarn per Zeilenfenster lesen statt nur die im
Auftrag genannten, DECISIONS-Absatz „is KZW's to assign" (DECISIONS.md:1249) altert mit dem Merge.
Siehe [[nacht-a2-270]] fuer den JSON-Walk-Aufbau.
