#!/usr/bin/env python3
"""
Tests fuer das Ergaenzen von sense/@ana in extract-variants.py (#753).

Jeder Test faehrt die ausgelieferten Funktionen (collect_one, prepare_lexicon_sync)
gegen ein Mini-TEI und eine Mini-lexicon.xml im Temp-Verzeichnis. Nur der Pfad
LEXICON des Moduls wird umgebogen.

Aufruf:
    python scripts/sync/test_extract_variants.py
"""
import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HIER = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('extract_variants', HIER / 'extract-variants.py')
ev = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ev)

LEXICON = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <text><body>
    <entry xml:id="lemma_1">
      <sense xml:id="lemma_1_sense_1" ana="#type_10 #type_2">
        <def>a</def>
      </sense>
      <sense xml:id="lemma_1_sense_10">
        <def>b</def>
      </sense>
      <sense xml:id="lemma_1_sense_11"/>
      <sense xml:id="lemma_1_sense_12" ana="#type_999">
        <def>c</def>
      </sense>
      <sense xml:id="lemma_1_sense_13" ana="#type_5 #type_3">
        <def>d</def>
      </sense>
      <sense xml:id="lemma_1_sense_14" ana="#type_7">
        <def>unbelegt, bleibt</def>
      </sense>
    </entry>
  </body></text>
</TEI>
'''

TEI = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <text><body><p>
    <w lemmaRef="lexicon.xml#lemma_1" ana="lexicon.xml#lemma_1_sense_1" corresp="variants.xml#type_2">a</w>
    <w lemmaRef="lexicon.xml#lemma_1" ana="lexicon.xml#lemma_1_sense_1" corresp="variants.xml#type_1">b</w>
    <w lemmaRef="lexicon.xml#lemma_1" ana="lexicon.xml#lemma_1_sense_10 lexicon.xml#lemma_1_sense_11" corresp="variants.xml#type_20">c</w>
    <w lemmaRef="lexicon.xml#lemma_1" ana="lexicon.xml#lemma_1_sense_10" corresp="variants.xml#type_3">d</w>
    <w lemmaRef="lexicon.xml#lemma_1" ana="lexicon.xml#lemma_1_sense_12" corresp="variants.xml#type_8">e</w>
    <w lemmaRef="lexicon.xml#lemma_1" ana="lexicon.xml#lemma_1_sense_13" corresp="variants.xml#type_3">f</w>
    <w lemmaRef="lexicon.xml#lemma_1" ana="lexicon.xml#lemma_1_sense_99" corresp="variants.xml#type_1">g</w>
    <w lemmaRef="lexicon.xml#lemma_1" ana="lexicon.xml#lemma_1_sense_13" corresp="variants.xml#type_555">h</w>
    <w lemmaRef="lexicon.xml#lemma_1" ana="lexicon.xml#lemma_1_sense_13" corresp="variants.xml#type_77">j</w>
    <w lemmaRef="lexicon.xml#lemma_1" corresp="variants.xml#type_77">i</w>
  </p></body></text>
</TEI>
'''

# Typen, die variants.xml nach der Regeneration fuehrt. type_555 fehlt absichtlich
# (ein Token-corresp ohne Eintrag darf nicht ergaenzt werden), type_999 ebenso
# (verwaist, wird entfernt).
TYPE_IDS = {'type_1', 'type_2', 'type_3', 'type_5', 'type_7', 'type_8', 'type_10', 'type_20', 'type_77'}


class SenseAnaErgaenzen(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='ev753-'))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / 'lexicon.xml').write_text(LEXICON, encoding='utf-8', newline='')
        (self.tmp / 'a.tei.xml').write_text(TEI, encoding='utf-8', newline='')
        self._alt = ev.LEXICON
        ev.LEXICON = self.tmp / 'lexicon.xml'
        self.addCleanup(setattr, ev, 'LEXICON', self._alt)
        _, _, self.sense_types = ev.collect_one(self.tmp / 'a.tei.xml')

    def test_k_wird_gesammelt(self):
        self.assertEqual(self.sense_types['lemma_1_sense_1'], {'type_1', 'type_2'})
        self.assertEqual(self.sense_types['lemma_1_sense_10'], {'type_20', 'type_3'})
        self.assertEqual(self.sense_types['lemma_1_sense_11'], {'type_20'})
        self.assertNotIn('lemma_1_sense_14', self.sense_types)

    def test_ergaenzt_und_bereinigt(self):
        text, stats = ev.prepare_lexicon_sync(TYPE_IDS, self.sense_types)
        self.assertIsNotNone(text)
        alt = ev.etree.fromstring(LEXICON.encode('utf-8'))
        neu = ev.etree.fromstring(text.encode('utf-8'))
        ana = lambda r: {s.get(ev.XML + 'id'): s.get('ana') for s in r.iter(ev.TEI + 'sense')}
        a, n = ana(alt), ana(neu)
        # vorhandene Liste: sortiert, Zeichenkettenordnung (type_1 vor type_10 vor type_2)
        self.assertEqual(n['lemma_1_sense_1'], '#type_1 #type_10 #type_2')
        # ohne @ana: bekommt das Attribut, auch am selbstschliessenden Sense
        self.assertEqual(n['lemma_1_sense_10'], '#type_20 #type_3')
        self.assertEqual(n['lemma_1_sense_11'], '#type_20')
        # verwaister Typ raus, belegter dazu
        self.assertEqual(n['lemma_1_sense_12'], '#type_8')
        # unsortierte Liste behaelt ihre Reihenfolge, Neues hinten; type_555
        # steht nicht in variants.xml: nicht ergaenzt
        self.assertEqual(n['lemma_1_sense_13'], '#type_5 #type_3 #type_77')
        # unbelegter Typ bleibt (kein Token nennt den Sense), Liste unveraendert
        self.assertEqual(n['lemma_1_sense_14'], '#type_7')
        self.assertEqual(a['lemma_1_sense_14'], n['lemma_1_sense_14'])
        self.assertEqual(stats['missing_senses'], 5)
        self.assertEqual(stats['missing_senses_without_ana'], 2)
        self.assertEqual(stats['orphan_senses'], 1)

    def test_rest_der_datei_bleibt(self):
        text, _ = ev.prepare_lexicon_sync(TYPE_IDS, self.sense_types)
        rx = ev.re.compile(r'(<sense xml:id="[^"]*")(?: ana="[^"]*")?')
        self.assertEqual(rx.sub(r'\1', LEXICON), rx.sub(r'\1', text))

    def test_zweiter_lauf_aendert_nichts(self):
        text, _ = ev.prepare_lexicon_sync(TYPE_IDS, self.sense_types)
        (self.tmp / 'lexicon.xml').write_text(text, encoding='utf-8', newline='')
        text2, stats = ev.prepare_lexicon_sync(TYPE_IDS, self.sense_types)
        self.assertIsNone(text2)
        self.assertEqual(stats['missing_tokens'], 0)
        self.assertEqual(stats['orphan_tokens'], 0)

    def test_unsortierte_liste_behaelt_ihre_reihenfolge(self):
        self.assertEqual(ev.neue_ana_liste(['#type_5', '#type_3'], [], ['#type_4']),
                         ['#type_5', '#type_3', '#type_4'])


if __name__ == '__main__':
    unittest.main()
