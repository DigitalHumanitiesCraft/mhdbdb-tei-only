"""Legt das Lemma briech (lemma_79829) in authority-files/lexicon.xml an (KZW, #554, A-103).

KZW (15.10.2026): "Eigenes/neues Lemma briech bei uns anlegen, aber mit klarer Bedeutung fuer
breiig und Kompositakomponente bri." Entscheidung der Koordination vom 15.10.2026:
  - dieselben drei Konzepte wie bri (21111300 Lebensmittel, 21111304 Nahrungszubereitung,
    21111306 Speisen), damit bri unter "gleiche Begriffe" erscheint (unsere Lesart von
    "Assoziationsrelationen"; ein Konzept "Brei" gibt es nicht),
  - etym/seg[@type="component"] auf bri (lemma_32468),
  - def "breiig" mit resp contrib_003, kein Link zum MWB (kein Feld dafuer).
Der Eintrag steht an der Zeichenkettenposition seiner xml:id (nach lemma_79828, vor lemma_7983).
Das Korpus-Token ZUK_76100_5 wird von Hand umgehaengt (tei/ZUK.tei.xml); sense/@ana setzt
extract-variants.py --apply.

Aufruf (aus der Repositoriumswurzel):
    python -X utf8 -E -P scripts/ingest/glossar-554/briech-anlegen.py
Bricht ab, wenn lemma_79829 schon existiert oder die Nachbarn nicht stimmen.
"""
import re
import sys

LEXIKON = 'authority-files/lexicon.xml'
EINTRAG = '''        <entry xml:id="lemma_79829">
          <form type="lemma">
            <orth>briech</orth>
          </form>
          <gramGrp>
            <pos>ADJ</pos>
          </gramGrp>
          <etym type="morphological">
            <seg type="component" corresp="lexicon.xml#lemma_32468">brî</seg>
          </etym>
          <sense xml:id="lemma_79829_sense_119197">
            <def xml:lang="de" resp="contributors.xml#contrib_003">breiig</def>
            <ptr target="concepts.xml#concept_21111300"/>
            <ptr target="concepts.xml#concept_21111304"/>
            <ptr target="concepts.xml#concept_21111306"/>
          </sense>
        </entry>'''

with open(LEXIKON, encoding='utf-8', newline='') as f:
    inhalt = f.read()
nl = '\r\n' if '\r\n' in inhalt else '\n'
if 'lemma_79829' in inhalt or 'sense_119197' in inhalt:
    sys.exit('FEHLER: lemma_79829 oder sense_119197 kommt schon vor')
zeilen = inhalt.split(nl)
ziel = [i for i, z in enumerate(zeilen) if z.strip() == '<entry xml:id="lemma_7983">']
if len(ziel) != 1:
    sys.exit('FEHLER: lemma_7983 kommt %d-mal vor' % len(ziel))
i = ziel[0]
vor = [j for j in range(i - 1, max(0, i - 400), -1) if zeilen[j].strip() == '</entry>']
if not vor or not re.search(r'<entry xml:id="lemma_79828">', '\n'.join(zeilen[vor[0] - 60:vor[0] + 1])):
    sys.exit('FEHLER: unmittelbar vor lemma_7983 steht nicht lemma_79828')
if vor[0] != i - 1:
    sys.exit('FEHLER: zwischen lemma_79828 und lemma_7983 liegt weiteres')
zeilen[i:i] = EINTRAG.split('\n')
with open(LEXIKON, 'w', encoding='utf-8', newline='') as f:
    f.write(nl.join(zeilen))
print('lemma_79829 briech eingefuegt vor Zeile %d' % (i + 1))
