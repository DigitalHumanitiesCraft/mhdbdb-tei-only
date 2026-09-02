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
  GENE, SIS, XXVIII) stehen in der WZB als unannotierte `<w>` im Textfluss (922 nur A-Z
  von 6.836 unannotierten, Stand nach dem Lauf). Sie zerreissen Woerter in zwei
  Scheintoken (22 Folgen unann/CAPS+/unann, 18 davon echte Woerter).
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
