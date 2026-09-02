---
name: wzb-breve-wortart-235
description: Messfallen beim Review der WZB-Breve-Wortart-Tafel (#235 Rest): Namen fehlen im WZB-TEI, Kolumnentitel sind unannotierte <w>, vor-Messvorschrift, GRA-Lemmata sind 9 nicht 4
metadata:
  type: project
---

Review-Runde 1 zu `scripts/ingest/wzb/wzb-breve-wortart.py` am 2026-09-02 (Zweig `claude/235-breve-wortart`).

**Fakten, die beim Nachmessen ueberrascht haben:**

- Die `vers`/`umfeld`-Spalten in `ingest/wzb/235-breve/review-faelle.csv` sehen aus, als
  liessen sie Eigennamen weg ("bruder des grŏsseren [Japhet]", "kvnig von [Basan]"). Sie
  tun es nicht: die Namen stehen im WZB-TEI gar nicht. Vor einem Befund "Bezugsnomen
  fehlt im Kontext" die Rohdatei um die xml:id herum lesen.
- Laufende Kolumnentitel und Buchzahlen (IOSUE, EXO, DUS, NUM, ERI, DEUTRO, NOMIUS,
  GENE, SIS, XXVIII) stehen in der WZB als unannotierte `<w>` im Textfluss. Vier
  Zaehlvorschriften, alle vier ueber die geparsten <w> ohne @lemmaRef gemessen, alle
  vier richtig: `t.upper() == t` und mind. ein Buchstabe 928 (das ist die Zahl im Log),
  dito und rein alphabetisch 927 (Differenz: `W` plus weicher Trennstrich), kein Zeichen
  mit `islower()` 926 (Differenz zu 928: `IICAPᵐ` und `ᵐ`, U+1D50 gilt Python als
  Kleinbuchstabe), nur A-Z 922. Der CI-Bot hat in #389 gemeldet, die 922 sei `\p{Lu}+`
  und A-Z ergebe 919, gemessen mit `rg -c '<w xml:id="[^"]*">[A-Z]+</w>'`. Das ist keine
  Zeilenfalle: `rg -c` und `rg -o | wc -l` liefern in der WZB dasselbe (919/919, 922/922),
  und 0 von 235.993 Zeilen tragen mehr als ein `<w>`. Die Differenz ist das Muster: es
  laesst nur `<w>` mit xml:id als einzigem Attribut zu, und drei A-Z-Tokens ohne @lemmaRef
  tragen `pos="DIG"` (XU, UIII, XU). Dass `\p{Lu}+` per rg auch 922 ergibt, ist Zufall
  (919 plus Γ, Ⱡ, OꝚ). Die Kolumnentitel zerreissen Woerter in zwei Scheintoken (22 Folgen
  unann/CAPS+/unann, 18 davon echte Woerter).
- `variants.xml` haelt NICHT je Normalform genau ein Ziel: 4.972 von 234.243 Normalformen
  (MHG-normalisiert ueber alle `<form>`) zeigen auf mehr als ein Lemma, `grossen` auf drei
  (lemma_2534, lemma_2535, lemma_31392 gros). Der Backfill-Matcher legt solche Faelle als
  `lemma-mehrdeutig` in den Review, er waehlt nicht. Jede "Einwertigkeit"-Behauptung ueber
  variants.xml ist damit Klasse B.
- `grozen` mit lemmaRef lemma_2534 und pos ADJ: 1.209 Tokens (lxml, itertext, NFC,
  mhg_normalizer), egal ob body-only oder ganze Datei. Die 1.223 aus PR #389 hat keine
  Vorschrift, die sie reproduziert.
- `vor` (lemma_7194) PRP/ADV nach Wortart rechts: die Zahlen 738:6 und 158:105 sind nur
  reproduzierbar mit NP-Start = {DET, ADJ, NOM, NAM, PRO, POS, NUM}; der Legacy-Tag ART
  (51 PRP, 2 ADV) faellt in "sonst". Multi-pos-Tokens (Leerzeichen im @pos) zaehlen als
  unaufgeloest.
- `umbe` (lemma_6422) vor sus/sust/suz: 112 = 107 "ADV PRP" + 5 PRP, exakt nur bei
  Vergleich auf NFC-lowercase-Text ohne v-Varianten (svs, svst) und ohne Diakritika-Strip;
  mit denen sind es 126.
- Von den 29 Ziel-Lemmata der 98 fuehren 9 den Tag GRA in posAll (nicht 4); 8 fuehren
  ADJ und NOM, die "sieben" der Doku sind ohne roete (lemma_10840).
- lemma_2535 `grôzen` VRB existiert (13 Belege in 11 Texten, meist intransitiv "groz
  werden"); eine Suche nach "grœzen" trifft es nicht.

**Why:** Diese Zahlen tauchen in Docstring, README, config.json und Versionskommentar
gleichzeitig auf; wer eine korrigiert, muss alle vier Stellen treffen.

**How to apply:** In Runde 2+ nur die Zeilen pruefen, die sich seit Runde 1 geaendert
haben; Messskripte lagen unter `C:/Users/chstn/.cache/claude-scratch/rev235_*.py`
(Scratch, nicht im Repo).
