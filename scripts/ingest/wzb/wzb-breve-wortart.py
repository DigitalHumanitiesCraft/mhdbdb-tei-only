#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#235 Punkt 3, Rest: die 98 Breve-Tokens mit mehrdeutiger Wortart.

wzb-breve-backfill.py hat am 2026-08-31 von 289 Breve-Kandidaten 66 annotiert
und 223 zurueckgehalten. Die groesste zurueckgehaltene Gruppe sind 98 Tokens,
bei denen die normalisierte Schreibung in variants.xml genau EIN Lemma trifft,
dieses Lemma aber MEHRERE Wortarten fuehrt. Die Wahl braucht Kontext. Dieses
Skript trifft sie, Fall fuer Fall, mit einer offenliegenden Entscheidungstafel.

WAS HIER ANDERS IST ALS BEI DEN 66
----------------------------------
Die 66 sind ohne jede Kontextentscheidung gelaufen. Diese 89 nicht: jede Zeile
in ENTSCHEIDUNGEN unten ist gelesen worden, am Vers und am Umfeld aus
review-faelle.csv. Die Tafel steht deshalb im Skript und nicht in einer
Datendatei: sie IST der Befund, und sie soll mit dem Diff gelesen werden.

Die Konfidenzregel ist dieselbe wie in #369: annotiert wird nur bei hoher
Konfidenz. Die fuenf Faelle mit mittlerer bleiben byte-identisch stehen und
gehen in den Review, mitsamt der Lesart, die dagegen spricht (ALTERNATIVE).

DIE NEUN REGELN
---------------
Jede Entscheidung nennt die Regel, unter der sie faellt. Die Regeln sind so
gewaehlt, dass sie an der Textstelle pruefbar sind und nicht am Sprachgefuehl.

  R1  Adjektiv mit Bezugsnomen in derselben Phrase, oder als Praedikat  -> ADJ
  R2  Adjektiv besetzt die Nominalstelle selbst, kein Bezugsnomen in
      der Phrase (Substantivierung, auch Komparativ und Superlativ)     -> NOM
  R3  modifiziert ein Verb oder ein Adjektiv                            -> ADV
  R4  Vollverb, finite Form, Infinitiv oder Partizip                    -> VRB
  R5  Modalverb mit abhaengigem Infinitiv                               -> VEM
  R6  Hilfsverb zum Partizip                                            -> VEX
  R7  Praeposition mit Rektion                                          -> PRP
  R8  Partikel eines Partikelverbs                                      -> ADV
  R9  Substantiv                                                        -> NOM

R8 ist keine Erfindung dieses Laufs, sondern POS-TAGSET.md 6.5: einen zwanzigsten
Tag PART gibt es nicht, KZW hat das am 2026-07-08 entschieden, und Partikeln
werden bis auf weiteres als ADV getaggt.

GRA wird NIE geschrieben. POS-TAGSET.md 3 fuehrt den Tag als aufgegeben
(Steigerung und Superlativ sind ADJ), 6.3 Invariante (d) verbietet ihn im
Ausgang eines Batches. NEUN der 29 Ziel-Lemmata fuehren GRA in posAll (groz,
hoch, boese, schoene, suesse, bloede, toerlich, lobelich, vor); die
Steigerungsformen unter den 98 bekommen deshalb ADJ oder NOM, nie GRA. Es sind
Komparative und Superlative, nicht nur Superlative: grŏsseren und hŏher sind
Komparative.

DREI ENTSCHEIDUNGEN SIND AM BESTAND GEMESSEN, NICHT GERATEN
-----------------------------------------------------------
1. Substantiviertes Adjektiv, ADJ oder NOM? Grundgesamtheit sind SIEBEN der
   acht ADJ/NOM-Lemmata der 98er-Menge; roete (lemma_10840) bleibt draussen,
   weil es ein Substantivlemma mit Adjektivlesart ist und seine NOM-Belege die
   Messung ueberdecken wuerden, ohne etwas ueber Substantivierung zu sagen
   (mit ihm 201 Belege im heutigen Stand, ohne ihn 69). Diese sieben hatten vor
   dem Lauf 60 aufgeloeste NOM-Belege, alle ausserhalb der WZB, alle einzeln
   angesehen.
   Der Befund: das Haus taggt die Substantivierung NOM, in zwei Bauarten, die
   beide hier einschlaegig sind. Echte Substantivierungen ("wir nemen gut unde
   bose in unser gewalt", "kere von dem bosen unde tu das gute", "vf das aller
   hoechste", "under dien boesen") und die -i-Abstrakta unter dem
   Adjektivlemma ("in der grössin", "von der schoeni des brútgovmes", "dur
   mine brodi").
   ZWEI der 60 sind keines von beidem, gefunden im Review, nicht von mir:
   AC3_22210_11 "seit das nie so boser man wart" ist attributiv und im Bestand
   als NOM fehlgetaggt, ADP_3500500_2 "vf daz hoch zit" ist die getrennt
   geschriebene Haelfte von hôchzît. Beide widerlegen den Befund nicht, sie
   begrenzen seine Umkehrung: aus dem NOM-Tag folgt nicht, dass eine
   Substantivierung vorliegt.
   Der rohe Anteil taeuscht uebrigens (60 NOM gegen rund 27.000 ADJ), weil
   attributive Verwendung um Groessenordnungen haeufiger ist, nicht weil diese
   Bauarten anders getaggt wuerden.
2. "umbe sus/sust", PRP oder ADV? Zaehlvorschrift: Tokens mit lemmaRef auf
   lemma_6422, deren unmittelbarer Nachfolger MHG-normalisiert sus, sust oder
   suz ergibt. Das sind 112 Vorkommen, davon 107 unaufgeloest als "ADV PRP"
   und 5 aufgeloest. Alle 5 sind PRP, keines ADV. Die feste Wendung aendert
   die Rektion nicht. (Nimmt man die v-Schreibungen svs und svst dazu, sind es
   126; das Verhaeltnis bleibt.)
3. "vor", PRP oder Partikel? Gemessen ueber alle aufgeloesten vor-Belege, nach
   der Wortart rechts aufgeteilt. "Nominalphrase rechts" heisst: der pos-Wert
   des Folgetokens schneidet sich mit {DET, POS, PRO, NOM, NAM, NUM, ADJ}. Das
   Legacy-ART faellt damit in "etwas anderes", 51 PRP gegen 2 ADV. Beginnt
   rechts eine Nominalphrase, steht vor 738 mal PRP gegen 6 mal ADV; sonst 158
   mal ADV gegen 105 mal PRP. Das Kriterium traegt also in die PRP-Richtung
   sehr klar und in die ADV-Richtung nur deutlich, und die vier Faelle hier
   fallen entlang dieser Grenze.

NEUN TOKENS WERDEN NICHT ANNOTIERT
----------------------------------
Fuenf davon wegen der Konfidenzregel. Bei den anderen vier ist ueberhaupt nicht
die Wortart offen, sondern das Ziel-Lemma falsch: zweimal steht im Vers ein
anderes Wort als das Kandidatenlemma, und zweimal ist das Token gar kein Wort,
sondern die Haelfte eines durch einen Blattmarker zerrissenen. Ein anderes
Lemma zu setzen als das gemessene Kandidatenlemma ist eine philologische
Entscheidung und keine Wortartwahl; sie gehoert zu KZW. Alle neun stehen mit
Fundstelle und Vorschlag in review-faelle.csv.

Fuer alle drei Faelle, in denen ein anderes Lemma richtig waere, gibt es dieses
Lemma bereits (lemma_2535 grôzen, lemma_2908 hort, lemma_6135 tohter). Der
Matcher hat sie nicht gefunden, weil keine ihrer Variantenformen auf die
Breve-Schreibung normalisiert. Die Zuordnung, die er stattdessen gefunden hat,
ist jedes Mal fuer sich richtig und nur fuer dieses Token falsch: hoerde ist ein
Praeteritum von hoeren, toech eines von ziehen.

KEIN @corresp, KEIN @ana. Unveraendert die Begruendung des Vorlaufs: jede
Schreibung braeuchte unter ihrem Ziel-Lemma eine neu gepraegte Typnummer, und
neue Typen sind genehmigungspflichtig (#216 und #369 haben es verweigert, #367
hat fuer zwei Nummern KZWs Zustimmung eingeholt). Die Sense-Zuordnung ist
kuratorisch. Die 89 landen damit in derselben Lage wie die 66 und wie die
52.097 anderen WZB-Tokens aus #370.

FOLGEN FUER DIE ABGELEITETE SCHICHT: @lemmaRef kommt neu hinzu, und gezaehlt
werden nur <w> mit @lemmaRef. Die Positionszaehlung der WZB aendert sich also,
Korpus-Index und statische API muessen neu gebaut werden. variants.xml und der
Authority-Index bleiben unberuehrt, weil kein @corresp geschrieben wird.

Nicht idempotent: ein zweiter Lauf findet die Tokens annotiert vor und bricht
mit einer Meldung ab, statt still nichts zu tun.

Usage:
    python scripts/ingest/wzb/wzb-breve-wortart.py \
        --out-dir ingest/pos-disambig/235-breve-wortart [--apply]
"""
import argparse
import csv
import gzip
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))

DATEI = REPO / "tei" / "WZB.tei.xml"
QUELLE = REPO / "ingest" / "wzb" / "235-breve" / "review-faelle.csv"
AUTH_INDEX = REPO / "data" / "authority-index.json.gz"

# POS-TAGSET.md 1. GRA, ART und die Migrationsreste stehen absichtlich nicht drin.
TAGS_19 = {"NOM", "NAM", "ADJ", "ADV", "DET", "POS", "PRO", "PRP", "NEG", "NUM",
           "CNJ", "SCNJ", "CCNJ", "IPA", "VRB", "VEX", "VEM", "INJ", "DIG"}

REGELN = {
    "R1": "Adjektiv mit Bezugsnomen in der Phrase oder als Praedikat",
    "R2": "Substantivierung: besetzt die Nominalstelle selbst",
    "R3": "modifiziert ein Verb oder ein Adjektiv",
    "R4": "Vollverb",
    "R5": "Modalverb mit abhaengigem Infinitiv",
    "R6": "Hilfsverb zum Partizip",
    "R7": "Praeposition mit Rektion",
    "R8": "Partikel eines Partikelverbs (POS-TAGSET 6.5)",
    "R9": "Substantiv",
}

# xml:id -> (pos, regel, konfidenz, kurzbegruendung am Text)
ENTSCHEIDUNGEN = {
    # --- blœde, bœse: attributiv gegen substantiviert -------------------------
    "WZB_28rb_12_4":  ("ADJ", "R1", "hoch",   "blŏde vnd trifende ougen"),
    "WZB_184ra_14_0": ("ADJ", "R1", "hoch",   "die gar bŏse seuchen"),
    "WZB_49vb_11_1":  ("ADJ", "R1", "hoch",   "die tage ... sint ... wenig vnd bŏse"),
    "WZB_127rb_15_6": ("ADJ", "R1", "hoch",   "die bŏsen tir die wilden"),
    "WZB_176ra_11_1": ("ADJ", "R1", "hoch",   "dicz bŏsen geslechtes"),
    "WZB_40ra_24_4":  ("ADJ", "R1", "hoch",   "den bŏsen vnczimlichen wercken"),
    "WZB_192rb_5_0":  ("ADJ", "R1", "hoch",   "bŏser gedancke"),
    "WZB_7ra_27_3":   ("NOM", "R2", "hoch",   "geneiget ... zu dem bŏsten, ad malum"),
    "WZB_77va_23_1":  ("NOM", "R2", "hoch",   "ich wider sage dem bŏzen, ohne Bezugsnomen"),
    "WZB_130ra_15_5": ("NOM", "R2", "hoch",   "noch das gute noch das pŏse"),
    "WZB_154rb_4_2":  ("ADJ", "R1", "hoch",   "die pŏse stat"),
    "WZB_183ra_36_2": ("ADJ", "R1", "mittel", "grose wunder vnd pŏse, nachgestellt zu wunder"),
    "WZB_144ra_8_3":  ("NOM", "R2", "hoch",   "mit also vil pŏsem"),
    "WZB_205ra_5_2":  ("ADJ", "R1", "hoch",   "mit pŏser luft"),
    # --- die -lich/-lichen-Formen: adverbial gegen praedikativ ----------------
    "WZB_28rb_34_12": ("ADV", "R3", "mittel", "als gewŏnlichen ist, adverbiale -en-Form"),
    "WZB_14va_13_4":  ("ADV", "R3", "hoch",   "machen dich wachsende grŏslich"),
    "WZB_44vb_26_2":  ("ADV", "R3", "hoch",   "vragte vns ŏrdenlich"),
    "WZB_119rb_6_1":  ("ADJ", "R1", "mittel", "geheiligt lŏblich, laudabilis als Praedikat"),
    "WZB_31ra_22_3":  ("ADV", "R3", "hoch",   "Tŏrlichen hastu getan"),
    "WZB_145va_5_0":  ("ADV", "R3", "hoch",   "die svnde di wir tŏrlichen habn begangen"),
    "WZB_136vb_22_2": ("ADJ", "R1", "hoch",   "mit ŏsterlichen broten"),
    # --- grôz, hôch, schœne, süeʒe -------------------------------------------
    "WZB_202rb_8_2":  ("NOM", "R2", "mittel", "ein grŏsers vnd ein minners, Kopf getilgt"),
    "WZB_10rb_9_3":   ("NOM", "R2", "hoch",   "bruder des grŏsseren, der Aeltere"),
    "WZB_68ra_14_3":  ("NOM", "R2", "hoch",   "secht die grŏze der wunder"),
    "WZB_13rb_3_2":   ("NOM", "R2", "hoch",   "gesegent sei der hŏchste"),
    "WZB_210va_37_1": ("NOM", "R2", "hoch",   "do der hŏchste teilte die heiden"),
    "WZB_8ra_35_0":   ("ADJ", "R1", "hoch",   "was das wasser hŏher, praedikativ"),
    "WZB_13ra_32_4":  ("ADJ", "R1", "hoch",   "priester des hŏhsten gotis"),
    "WZB_13ra_35_0":  ("ADJ", "R1", "hoch",   "von dem hŏhsten gote"),
    "WZB_40ra_19_2":  ("ADJ", "R1", "hoch",   "schŏnes antliczes"),
    "WZB_153ra_6_9":  ("NOM", "R2", "hoch",   "das schŏnste vnd das peste"),
    "WZB_148va_2_2":  ("ADJ", "R1", "hoch",   "zu einem sŭzem ruche"),
    # --- hœren: durchgehend verbal -------------------------------------------
    "WZB_220ra_18_0": ("VRB", "R4", "hoch",   "Hŏren werden, Infinitiv"),
    "WZB_145ra_34_8": ("VRB", "R4", "hoch",   "Hŏret meine rede, Imperativ"),
    "WZB_37rb_34_0":  ("VRB", "R4", "hoch",   "Hŏret meinen trovm, Imperativ"),
    "WZB_209va_13_2": ("VRB", "R4", "hoch",   "sie mugen gehŏrn, Infinitiv"),
    "WZB_57ra_6_1":   ("VRB", "R4", "hoch",   "die dingen die got an gehŏrn"),
    "WZB_65ra_27_3":  ("VRB", "R4", "hoch",   "des das zu essen gehŏrt"),
    "WZB_18va_2_5":   ("VRB", "R4", "hoch",   "welcher hŏrende geloubte, Partizip"),
    "WZB_196rb_36_7": ("VRB", "R4", "hoch",   "das das hŏrende die andern, Partizip"),
    "WZB_1vb_25_3":   ("VRB", "R4", "hoch",   "das sie gerne hŏrent lesen"),
    "WZB_37vb_30_6":  ("VRB", "R4", "hoch",   "ich hab sie hŏrn sprechende"),
    "WZB_74ra_6_4":   ("VRB", "R4", "hoch",   "begonde man doner zu hŏrn"),
    "WZB_18rb_35_5":  ("VRB", "R4", "hoch",   "wer das hŏrt"),
    # --- die uebrigen Verben --------------------------------------------------
    "WZB_182ra_17_4": ("VRB", "R4", "hoch",   "haben heute geprŭfet"),
    "WZB_153va_5_4":  ("VRB", "R4", "hoch",   "sol sie schŭten ouserhalb den purgen"),
    "WZB_178ra_32_6": ("VRB", "R4", "hoch",   "wir slŭgen sie"),
    "WZB_155vb_8_0":  ("VRB", "R4", "hoch",   "so das wir stŭrben"),
    "WZB_137ra_29_4": ("VRB", "R4", "hoch",   "also tŭ her, 3. Sg. Konj., sic faciet"),
    "WZB_187ra_30_8": ("VRB", "R4", "hoch",   "vnd nv tŭ das, Imperativ"),
    "WZB_193ra_14_0": ("VRB", "R4", "hoch",   "das do getŏtet ist, Partizip"),
    "WZB_114ra_17_6": ("VRB", "R4", "hoch",   "des getŏtten sperlinges, Partizip"),
    "WZB_101ra_6_6":  ("VRB", "R4", "hoch",   "vnd tŏte das vor vnserm herren"),
    "WZB_101vb_30_7": ("VRB", "R4", "hoch",   "vnd tŏte sie an der stat"),
    "WZB_102ra_14_2": ("VRB", "R4", "hoch",   "vnd tŏte das an der stat"),
    "WZB_112vb_16_3": ("VRB", "R4", "hoch",   "so tŏte her das lamp"),
    "WZB_153ra_35_4": ("VRB", "R4", "hoch",   "vnd tŏte die in alles volkes angesicht"),
    "WZB_31rb_2_4":   ("VRB", "R4", "hoch",   "den tŏte man vor vnsern brudern"),
    "WZB_38ra_4_2":   ("VRB", "R4", "hoch",   "kvmet dan vnd tŏte wir in"),
    "WZB_44va_20_10": ("VRB", "R4", "hoch",   "mein czwen svne die tŏte"),
    "WZB_67ra_8_5":   ("VRB", "R4", "hoch",   "do tŏte vnser herre alle erstegeburt"),
    "WZB_85ra_17_3":  ("VRB", "R4", "hoch",   "vnd tŏte das in der angesichte"),
    "WZB_173va_2_4":  ("VRB", "R4", "hoch",   "sol den manslechtigen tŏten"),
    "WZB_16ra_6_5":   ("VRB", "R4", "hoch",   "das du tŏtest den gerechten"),
    "WZB_149vb_17_7": ("VRB", "R4", "hoch",   "das du vns tŏttest in der wŭstenunge"),
    "WZB_182vb_15_6": ("VRB", "R4", "hoch",   "dich ein gefŭret dein herre got, Partizip"),
    "WZB_183rb_19_2": ("VRB", "R4", "hoch",   "dich ein gefŭret dein herre got, Partizip"),
    "WZB_126va_16_6": ("VRB", "R4", "hoch",   "Vŏrchte deinen got, Imperativ"),
    "WZB_47va_2_5":   ("VRB", "R4", "hoch",   "nicht vŏrcht euch, Imperativ"),
    "WZB_181va_2_5":  ("VRB", "R4", "hoch",   "wenne ir vŏrchtet das fewer"),
    "WZB_75ra_2_6":   ("VRB", "R4", "hoch",   "nicht vŏrchtet euch, Imperativ"),
    "WZB_177ra_5_7":  ("VRB", "R4", "hoch",   "so das wir czŭgen vber die bach"),
    "WZB_184ra_15_6": ("VRB", "R4", "hoch",   "wirt her nicht einfŭren dir, Infinitiv"),
    # --- Modal- und Hilfsverb -------------------------------------------------
    "WZB_108vb_7_5":  ("VEM", "R5", "hoch",   "wie mŏcht ich sie gessen"),
    "WZB_159ra_11_3": ("VEM", "R5", "hoch",   "wer mŏcht geczelen den stoup"),
    "WZB_206rb_16_3": ("VEM", "R5", "hoch",   "die ... nicht gegeen mŏchte"),
    "WZB_24va_12_1":  ("VEM", "R5", "hoch",   "es mŏchte yemant ... haben vmb gegangen"),
    "WZB_154va_17_4": ("VEM", "R5", "hoch",   "mŭge wir euch ousgefuren wasser"),
    "WZB_182rb_10_0": ("VEM", "R5", "hoch",   "vnd mŭge geleben"),
    "WZB_173vb_17_2": ("VEM", "R5", "hoch",   "mit nichte mŭgen gekeren"),
    "WZB_176ra_31_0": ("VEX", "R6", "hoch",   "so das sie gevangen wŭrden gefurt, Passiv"),
    # --- Substantive ----------------------------------------------------------
    "WZB_137vb_12_4": ("NOM", "R9", "hoch",   "einen guldein mŏrser von czehen scoten"),
    "WZB_205va_30_2": ("NOM", "R9", "hoch",   "wirt toube rŏte vorczeren, Subjekt"),
    "WZB_33rb_9_3":   ("NOM", "R9", "hoch",   "yczunt geet ouf die morgen rŏte"),
    # --- umbe und vor: Praeposition gegen Partikel ----------------------------
    "WZB_23vb_37_0":  ("PRP", "R7", "hoch",   "Ŭmb dise geschicht"),
    "WZB_31va_3_5":   ("PRP", "R7", "hoch",   "Ŭmb was schult"),
    "WZB_33rb_31_4":  ("PRP", "R7", "hoch",   "Ŭmb dise sache"),
    "WZB_127vb_5_0":  ("PRP", "R7", "hoch",   "Ŭmme sust, dieselbe Wendung im Bestand 5 mal PRP und 0 mal ADV"),
    "WZB_164ra_5_4":  ("PRP", "R7", "hoch",   "Ŭmme das ist ... zu tvn"),
    "WZB_218rb_16_0": ("ADV", "R8", "hoch",   "Ŭmme geet die stat, Partikel zu umbegan"),
    "WZB_129ra_15_6": ("PRP", "R7", "hoch",   "vŏr das knechtil, rechts Nominalphrase"),
    "WZB_224va_36_1": ("ADV", "R8", "hoch",   "furet her vŏr zu mir, Partikel"),
    "WZB_68vb_14_2":  ("PRP", "R7", "hoch",   "waren in vŏr ein mawer, rechts Nominalphrase"),
    "WZB_98vb_8_5":   ("ADV", "R8", "mittel", "czihende vŏr in dem ein gange, Partikel"),
}

# Die Lesart, die bei den mittleren Konfidenzen dagegen spricht. Sie werden
# NICHT annotiert (Konfidenzregel, siehe unten), aber der Zweifel gehoert
# benannt, sonst ist "mittel" nur ein Wort.
ALTERNATIVE = {
    "WZB_28rb_34_12": "ADJ, wenn 'als gewŏnlichen ist' als Praedikatsnomen "
                      "gelesen wird statt als Adverb",
    "WZB_183ra_36_2": "NOM, wenn 'vnd pŏse' als eigenes 'und Boeses' gelesen "
                      "wird statt als Nachtrag zu 'wunder'",
    "WZB_119rb_6_1":  "ADV, wenn 'geheiligt lŏblich' als Art des Heiligens "
                      "gelesen wird statt als Praedikat zu den Fruechten",
    "WZB_202rb_8_2":  "ADJ, wenn 'ein grŏsers' als Ellipse zu 'gewichte' im "
                      "selben Satz gilt und nicht als Substantivierung",
    "WZB_98vb_8_5":   "PRP, wenn 'vŏr' die Praeposition zu 'in dem ein gange' "
                      "ist; das gemessene Kriterium traegt hier nur 158 zu 105",
}

# xml:id -> (kuerzel, was stattdessen richtig waere)
RUECKHALT = {
    "WZB_11rb_21_2": (
        "Z1",
        "'wil grŏsen deinen namen' ist das Verb. Das Ziel-Lemma grôz "
        "(lemma_2534) fuehrt ADJ ADV GRA NOM und kein VRB. Das Verblemma gibt "
        "es: lemma_2535 grôzen VRB, morphologisch auf lemma_2534 "
        "zurueckgefuehrt, 13 Belege in 11 Texten. Der Matcher hat es trotzdem "
        "nicht finden koennen, und der Grund ist eine Luecke im "
        "Variantenbestand: lemma_2535 fuehrt in variants.xml genau neun Formen "
        "(grozte grozet grozten grossen grôzte grôzet grôssen grozzet "
        "grosset), und keine davon normalisiert auf 'groesen'. Genau darauf "
        "normalisiert aber das Token 'grŏsen', und 'groesen' ist unter "
        "lemma_2534 belegt (Form 'grösen', type_289948). Fuer diesen "
        "Schluessel stand das Verblemma also gar nicht zur Wahl. Die "
        "Zuordnung ist dabei duenn: die Normalform 'groesen' hat im ganzen "
        "Korpus 2 Tokens, eines davon ist dieses hier, der Eintrag steht also "
        "auf einem einzigen Beleg. Dass "
        "variants.xml je Normalform nur ein Ziel haelt, trifft dieses "
        "Lemmapaar durchaus, aber an einer anderen Form: 'grossen' steht unter "
        "beiden (type_59047 unter lemma_2534, type_117361 unter lemma_2535). "
        "Fuer 'groesen' erklaert es nichts. Die dreistufige Aufloesung des "
        "Frontends ist "
        "nicht betroffen: fuer die Eingabe 'grôzen' trifft schon Stufe 1 auf "
        "lemma_2535, Stufe 2 kommt gar nicht dran. Das ist genau Kategorie C "
        "der #259-Messung, 'eigenes Lemma, variants zeigt anderswohin'. KZW "
        "entscheidet, ob das Token unter lemma_2535 gehoert: die 13 Belege "
        "sind ueberwiegend intransitiv ('min herze grôzet', 'der jamer "
        "grozzet'), die WZB-Stelle ist transitiv (magnificabo nomen tuum)."),
    "WZB_213ra_5_0": (
        "Z2",
        "'die vorporgin hŏrde des sandes' (thesauros absconditos harenarum) "
        "ist der Hort, nicht das Hoeren. lemma_2908 hort NOM waere richtig. "
        "Die Zeile hoerde -> lemma_2885 in variants.xml ist fuer sich richtig "
        "(Praeteritum von hoeren) und nur fuer dieses Token falsch."),
    "WZB_26vb_34_5": (
        "Z3",
        "'von den tŏch XXVIII GENE tern deines ŏhems': das Token ist kein "
        "Wort, sondern die erste Haelfte von tŏchtern, zerrissen durch einen "
        "eingeschobenen Blattmarker. lemma_6135 tohter NOM waere das Ziel, "
        "aber vorher gehoert das Token zusammengesetzt. Dieselbe Bauart wie "
        "Punkt 1 des Tickets."),
    "WZB_54vb_23_3": (
        "Z3",
        "'von siben tŏch EXO ter die quamen wasser schĕpfen': erste Haelfte "
        "von tŏchter, zerrissen durch den Blattmarker EXO. Siehe oben."),
}

# xml:id zuerst, dann optional pos, kein weiteres Attribut: trifft absichtlich
# nur unannotierte <w>. Uebernommen aus wzb-breve-backfill.py.
W_TEMPLATE = r'<w xml:id="{xid}"(?: pos="(?P<oldpos>[A-Z]+)")?>(?P<form>[^<]*)</w>'

CHANGE_VORLAGE = (
    '<change when="{datum}" who="#editor">#235 Punkt 3 (Rest): {n} der 98 '
    'zurueckgehaltenen Breve-Tokens mit mehrdeutiger Wortart am Ziel-Lemma '
    'nachannotiert (lemmaRef und pos). Anders als beim Lauf vom 2026-08-31 ist '
    'die Wortart hier am Vers entschieden, nach neun offengelegten Regeln, die '
    'mit dem Skript im Diff stehen; GRA wird nie vergeben (POS-TAGSET 3 und '
    '6.3d). Annotiert wird nur bei hoher Konfidenz, Regel wie in #369. {r} '
    'Tokens bleiben unannotiert: {k} wegen mittlerer Konfidenz und {z}, weil '
    'bei ihnen nicht die Wortart offen ist, sondern das Ziel-Lemma nicht passt. '
    'Kein corresp und kein ana, unveraendert die Begruendung des Vorlaufs. '
    'Provenienz-Log: {log}.</change>'
)


def pfad(p):
    p = Path(p)
    return p if p.is_absolute() else REPO / p


def repo_relativ(p):
    """Pfad fuer den revisionDesc-Eintrag: immer repo-relativ, immer Slashes.

    Ohne diese Umrechnung landet ein absolutes --out-dir woertlich im
    Korpusheader. Beim ersten Lauf war die Vorgabe relativ und der Eintrag
    richtig, beim Wiederholungslauf absolut, und erst der Vergleich der
    beiden Laeufe hat es gezeigt. Ein Pfad, der in eine Datei geschrieben
    wird, darf nicht davon abhaengen, wie der Aufruf getippt wurde.
    """
    p = pfad(p).resolve()
    try:
        return p.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        sys.exit("FEHLER: --out-dir %s liegt ausserhalb des Repositoriums; "
                 "der revisionDesc-Eintrag braucht einen repo-relativen "
                 "Pfad." % p)


def nfc(s):
    return unicodedata.normalize("NFC", s or "")


def lade_lemma_pos():
    """lemma_id -> (Wortarten, Lemmaform), aus dem Authority-Index."""
    idx = json.load(gzip.open(AUTH_INDEX, "rt", encoding="utf-8"))
    aus = {}
    for l in idx["lemmata"]:
        pa = l.get("posAll") or ([l["pos"]] if l.get("pos") else [])
        aus[l["id"]] = ([p for p in pa if p], l.get("lemma", ""))
    return aus


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    with QUELLE.open(encoding="utf-8-sig") as fh:
        faelle = [r for r in csv.DictReader(fh, delimiter=";")
                  if r["review_grund"] == "pos-mehrdeutig"]

    # Die Tafel muss die Faelle genau abdecken. Ein Tippfehler in einer xml:id
    # faellt sonst als stilles Ueberspringen aus, und das ist der Fehler, den
    # bei einer Handtafel niemand mehr findet.
    ids_csv = {r["xml_id"] for r in faelle}
    ids_tafel = set(ENTSCHEIDUNGEN) | set(RUECKHALT)
    if ids_csv != ids_tafel:
        fehlt = sorted(ids_csv - ids_tafel)
        zuviel = sorted(ids_tafel - ids_csv)
        sys.exit("FEHLER: Tafel und Faelle decken sich nicht.\n"
                 "  ohne Entscheidung: %s\n  nicht in der Quelle: %s"
                 % (fehlt or "-", zuviel or "-"))
    if set(ENTSCHEIDUNGEN) & set(RUECKHALT):
        sys.exit("FEHLER: xml:id steht in beiden Tafeln: %s"
                 % sorted(set(ENTSCHEIDUNGEN) & set(RUECKHALT)))

    lemma_pos = lade_lemma_pos()
    zeilen = []
    for r in sorted(faelle, key=lambda r: r["xml_id"]):
        xid = r["xml_id"]
        lemma = (r["lemma_kandidaten"] or "").split()[0] if r["lemma_kandidaten"] else ""
        posAll, lemmaform = lemma_pos.get(lemma, ([], ""))
        if xid in ENTSCHEIDUNGEN:
            pos, regel, konf, grund = ENTSCHEIDUNGEN[xid]
            if pos not in TAGS_19:
                sys.exit("FEHLER: %s bekaeme %r, das ist keiner der 19 Tags"
                         % (xid, pos))
            if pos not in posAll:
                sys.exit("FEHLER: %s bekaeme %r, das Ziel-Lemma %s fuehrt aber "
                         "nur %s. Ein solcher Fall gehoert in den Rueckhalt."
                         % (xid, pos, lemma, " ".join(posAll)))
            if konf != "hoch":
                # Konfidenzregel wie in #369: annotiert wird nur bei hoher
                # Konfidenz, alles andere bleibt byte-identisch stehen und geht
                # in den Review. Die Entscheidung wird trotzdem mitgeschrieben,
                # damit die Nachpruefung nicht bei null anfaengt.
                if xid not in ALTERNATIVE:
                    sys.exit("FEHLER: %s traegt Konfidenz %r ohne Gegenlesart "
                             "in ALTERNATIVE." % (xid, konf))
                zeilen.append({
                    "file": DATEI.name,
                    "xml_id": xid,
                    "form": r["form"],
                    "normalisiert": r["normalisiert"],
                    "action": "REVIEW",
                    "review_grund": "konfidenz-" + konf,
                    "neu_lemmaRef": "",
                    "neu_pos": "",
                    "regel": regel,
                    "regel_text": "Vorschlag %s nach %s; dagegen: %s"
                                  % (pos, regel, ALTERNATIVE[xid]),
                    "konfidenz": konf,
                    "beleg": grund,
                    "ziel_lemma_form": lemmaform,
                    "lemma_kandidaten": lemma,
                    "lemma_pos_alle": " ".join(posAll),
                    "vers": r["vers"],
                    "umfeld": r["umfeld"],
                })
                continue
            zeilen.append({
                "file": DATEI.name,
                "xml_id": xid,
                "form": r["form"],
                "normalisiert": r["normalisiert"],
                "action": "ANNOTATE",
                "review_grund": "",
                "neu_lemmaRef": "lexicon.xml#" + lemma,
                "neu_pos": pos,
                "regel": regel,
                "regel_text": REGELN[regel],
                "konfidenz": konf,
                "beleg": grund,
                "ziel_lemma_form": lemmaform,
                "lemma_kandidaten": lemma,
                "lemma_pos_alle": " ".join(posAll),
                "vers": r["vers"],
                "umfeld": r["umfeld"],
            })
        else:
            kuerzel, text = RUECKHALT[xid]
            zeilen.append({
                "file": DATEI.name,
                "xml_id": xid,
                "form": r["form"],
                "normalisiert": r["normalisiert"],
                "action": "REVIEW",
                "review_grund": "ziel-lemma-passt-nicht/" + kuerzel,
                "neu_lemmaRef": "",
                "neu_pos": "",
                "regel": kuerzel,
                "regel_text": text,
                "konfidenz": "",
                "beleg": "",
                "ziel_lemma_form": lemmaform,
                "lemma_kandidaten": lemma,
                "lemma_pos_alle": " ".join(posAll),
                "vers": r["vers"],
                "umfeld": r["umfeld"],
            })

    text = DATEI.read_text(encoding="utf-8", newline="")
    geschrieben = 0
    for z in zeilen:
        if z["action"] != "ANNOTATE":
            continue
        m = re.search(W_TEMPLATE.format(xid=re.escape(z["xml_id"])), text)
        if not m:
            sys.exit("FEHLER: <w xml:id=%s> nicht unannotiert gefunden. Ein "
                     "zweiter Lauf ueber denselben Stand ist nicht vorgesehen."
                     % z["xml_id"])
        if nfc(m.group("form")).strip() != z["form"]:
            sys.exit("FEHLER: %s: Tokentext %r != erwartete Form %r"
                     % (z["xml_id"], m.group("form"), z["form"]))
        if m.group("oldpos"):
            sys.exit("FEHLER: %s traegt bereits pos=%r" % (z["xml_id"], m.group("oldpos")))
        neu = ('<w xml:id="%s" lemmaRef="%s" pos="%s">%s</w>'
               % (z["xml_id"], z["neu_lemmaRef"], z["neu_pos"], m.group("form")))
        text = text[:m.start()] + neu + text[m.end():]
        geschrieben += 1

    n_review = sum(1 for z in zeilen if z["action"] == "REVIEW")
    n_konf = sum(1 for z in zeilen if z["review_grund"].startswith("konfidenz-"))
    change = CHANGE_VORLAGE.format(datum="2026-09-02", n=geschrieben, r=n_review,
                                   k=n_konf, z=n_review - n_konf,
                                   log=repo_relativ(args.out_dir))
    if change in text:
        sys.exit("FEHLER: der revisionDesc-Eintrag steht schon in der Datei.")
    # Hinter den letzten vorhandenen <change> haengen und dessen Einrueckung
    # uebernehmen. Nicht vor </revisionDesc>: das Element steht zwei Spalten
    # weiter links als seine Kinder, der Eintrag saesse sonst falsch eingerueckt.
    if "</revisionDesc>" not in text:
        sys.exit("FEHLER: kein </revisionDesc> in %s" % DATEI.name)
    letzte = text.rfind("<change ", 0, text.index("</revisionDesc>"))
    if letzte < 0:
        sys.exit("FEHLER: kein vorhandener <change> in %s, an dem sich die "
                 "Einrueckung ablesen liesse." % DATEI.name)
    zeilenanfang = text.rfind("\n", 0, letzte) + 1
    einzug = text[zeilenanfang:letzte]
    zeilenende = text.index("\n", letzte) + 1
    # Die WZB mischt CRLF mit 17 reinen LF (Token-Split f3dcf2a86). Der neue
    # Eintrag uebernimmt das Ende der Zeile, an die er sich haengt, statt eines
    # pauschalen "\n". Die CRLF-Zahl steht hier absichtlich nicht: die aus
    # wzb-breve-backfill.py (235.973) ist seit zwei <change>-Zeilen ueberholt,
    # sie war nie Teil der Aussage, und eine Zahl, die eine Aussage nicht
    # braucht, wird geloescht statt nachgezogen.
    umbruch = "\r\n" if text[zeilenende - 2:zeilenende] == "\r\n" else "\n"
    text = text[:zeilenende] + einzug + change + umbruch + text[zeilenende:]

    if args.apply:
        DATEI.write_text(text, encoding="utf-8", newline="")

    out = pfad(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    spalten = list(zeilen[0].keys())
    for name, auswahl in (("diff-liste.csv", zeilen),
                          ("review-faelle.csv",
                           [z for z in zeilen if z["action"] == "REVIEW"])):
        with open(out / name, "w", encoding="utf-8-sig", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=spalten, delimiter=";")
            wr.writeheader()
            wr.writerows(auswahl)

    modus = "APPLY" if args.apply else "DRY-RUN"
    print("[%s] Faelle: %d" % (modus, len(zeilen)))
    print("  ANNOTATE: %d, REVIEW: %d" % (geschrieben, n_review))
    print("  Wortarten:", dict(Counter(
        z["neu_pos"] for z in zeilen if z["action"] == "ANNOTATE")))
    print("  Regeln:", dict(Counter(
        z["regel"] for z in zeilen if z["action"] == "ANNOTATE")))
    print("  Konfidenz:", dict(Counter(
        z["konfidenz"] for z in zeilen if z["action"] == "ANNOTATE")))
    print("  Rueckhalt:", dict(Counter(
        z["review_grund"] for z in zeilen if z["action"] == "REVIEW")))
    print("  Artefakte:", out)
    if not args.apply:
        print("  (--apply schreibt ins Korpus)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
