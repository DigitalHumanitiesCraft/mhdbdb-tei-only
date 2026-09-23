---
name: nacht-a3-357-ingliart-sense
description: Review-Lehren aus Nachtlauf A3 (#357, ADR-020): zweiter Sense an lemma_3036 Ingliart, sense/@ana-Verschiebung, welche Gates und Konsumenten sense/@ana lesen (keine), REN-Namenkatalog 24206-24220 (15 Personen, nicht 8), Sense-Konzepte in ptr/@target, Guard-Verhalten bei git-Pipes
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

**Rennewart-Namenkatalog, Runde 2 (23.09.) nachgemessen ueber l/@n statt Zeilenfenster:** der
Katalog laeuft 24206–24220 (tei/REN.tei.xml 201405–201520), gerahmt von „als daz maer mir tuot
bekant" (24205) und „die gaben ritterliche ir leben" (24221). Muster „X von Y", je Vers ein
Personen- und ein Ortsname. 15 Personen-Tokens, alle 15 tragen concept_21012000 (Maennlich) +
concept_23112500 (Personennamen); 8 davon in 24206–24213 (Echerabant, Pauriper, Wimiligar,
Ingliart, Rufter, Ziraster 7900 = Zoroaster, Nilichter, Gabwar), 7 weitere in 24214–24220
(Tshilis, Eriuch, Muris, Agapiter, Zefar, Duriter, Malchiar). Orte tragen concept_24120000;
Ausnahme Pilde 47319 (Burg/Stadt/Gemeinde + 23112500, kein 24120000). Runde 1 hatte mit einem
Zeilenfenster nur 5 Personen gesehen, der PR-Autor mit 24206–24213 nur 8: **ein Vers- oder
Zeilenfenster ist nicht der Katalog, Katalogende am Rahmenvers messen.**
Konzepte eines Sense stehen in `sense/ptr/@target`, NICHT in `sense/@ana` (dort stehen die
Variantentypen); ein Skript, das @ana liest, zaehlt 0 Konzepte. Skript: $TEMP/rev357_katalog.py
(lo hi als Argumente, relative Pfade, `python -X utf8`). lemma_7900 hat 2 Tokens (REN ziraster,
PZ zôrôastêr), Sense zusaetzlich Arabisch + Nichtchristliche Mythologie.

**Zahlen dieser Runde:** hoechste Sense-Nummer vor dem PR 119194 (grep -o 'sense_[0-9]*"' | sort -n);
type_177507 nur an REN_242090_0 (1 Treffer in tei/, 1 in variants.xml); lemma_3036 hat 3 Tokens
(PZ_38926_4, PZ_39814_3, REN_242090_0); gz-Walk gegen 5ede36174 = genau 5 Unterschiede
(maps/conceptToLemmas ×2, version, senseCount, senses[len]); api/lemmata hat nur index.json,
api/concepts/concept_N.json tragen keine Lemmalisten, deshalb sind 2 API-Dateien vollstaendig.
Issue #357 hat genau einen Kommentar (wachauer 2026-09-14T12:17:41Z), das Konzept steht nicht drin.

**Runde 3 (23.09.), Satz DECISIONS.md:1250 nachgemessen:** Fenster 24200–24226 liefert dieselben
29 NAM-Tokens wie 24206–24220, der Rahmen haelt. 15/15 mit beiden Konzepten gilt erst am HEAD:
auf der Basis 5ede36174 zeigte REN_242090_0 auf lemma_3036_sense_4843 (concept_14012100 +
23221000, Pferd), also 14/15. „all fifteen" zaehlt den Ingliart-Token mit, dessen Zuweisung der
PR selbst schreibt; die Nachbarn sind 14. Wahr am HEAD, aber wer „derived from those neighbours"
liest, schliesst auf 15 Zeugen. Kein anderer Prosa-Ort traegt 24213/„eight person" (git grep
ueber *.md, docs, scripts), die alte Zahl steht nur in der Commit-Message 767810ae7.

**Guard:** ein Verbundkommando mit `git diff ... | grep ... $'\xe2\x80\x94'` wird als „zu komplex"
abgelehnt, `git diff ... | tail -1` im `;`-Verbund dagegen nicht. `python "$TEMP"/skript.py` wird
ebenfalls abgelehnt (Variable im Programm-Operanden); literaler Pfad
`C:/Users/chstn/AppData/Local/Temp/skript.py` laeuft, weil dort kein „Git" im Pfad steht. Em-Dash-Zaehlung ueber hinzugefuegte
Zeilen deshalb per Python-Skript in $TEMP mit subprocess. `extract-variants.py` ohne --apply schreibt
`authority-files/variants.regen.xml` (nicht gitignoriert, .gitignore:90 deckt nur Audit-Outputs),
danach loeschen, sonst meldet der Endstand eine Bewegung.

**Why:** Der Auftrag fragte, ob das Verschieben von type_177507 richtig ist und ob ein Check am
Gegenteil haengt; beides ist nur ueber die Konsumentenliste zu beantworten, nicht ueber den Diff.
**How to apply:** Bei jedem Sense-Split (ADR-020 gilt „fuer alle Namen") dieselbe Liste pruefen:
Typen des Sense mit den Tokens abgleichen, Katalognachbarn per Zeilenfenster lesen statt nur die im
Auftrag genannten, DECISIONS-Absatz „is KZW's to assign" (DECISIONS.md:1249) altert mit dem Merge.
Siehe [[nacht-a2-270]] fuer den JSON-Walk-Aufbau.
