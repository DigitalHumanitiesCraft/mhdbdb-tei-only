#!/usr/bin/env python3
"""Strophenziffern als Wort-Token aus dem Verstext entfernen (#138).

Hintergrund
-----------
In HUG steht die roemische Strophenzahl als Token am Ende des letzten Verses
der VORIGEN Strophe, die Zahl der ersten Strophe in einem eigenen <ab> am
Anfang des Lieds. Die zugrundeliegende Edition (Hofmeister 2005) setzt sie
dagegen in die linke Randspalte, auf Hoehe des ersten Verses der Strophe.
Bei uns landet die Zahl dadurch mitten im Vers. KZW in #138: "das ist Unsinn
und wird auch nicht in der zugrundeliegenden Edition abgebildet. Nimm die in
diesem Text alle raus."

Der Randzahl-Ersatz existiert bereits: <lg type="stanza"> traegt @n, und zwar
strikt 1..N pro <div>. Die Leseansicht kann die Zahl aus lg/@n an den Rand
setzen, so wie der Druck.

Warum das Merkmal der ID-Block ist und nicht @pos
--------------------------------------------------
Naheliegend waere gewesen, auf w[@pos="DIG"] zu filtern. Das greift zu kurz:
in HUG sind nur 706 der 814 Ziffern lemmatisiert, die uebrigen 108 stehen als
nackte <w> ohne @pos und ohne @lemmaRef da, teils in <hi rend="upper_case">
gewickelt (es sind die Werte i, v, vi, x, l, li, c, ci). Ein DIG-Filter haette
sie stehen lassen, und genau die waeren in der Leseansicht sichtbar geblieben.

Das tragfaehige Merkmal ist der xml:id-Block: im Legacy-Linecode ist die
Randziffer eine eigene Untereinheit des Verses.

  <w xml:id="HUG_30040_8">dírn</w>      Vers-Block  HUG_30040
  <pc xml:id="HUG_30040_9">.</pc>       derselbe Block, gehoert zum Vers
  <w xml:id="HUG_30041_0">ii</w>        eigener Block HUG_30041 = die Ziffer

Ein echtes Wort im Verstext sitzt immer im Vers-Block. Deshalb bleibt etwa
das <hi rend="upper_case">-Zeichen in HUG.tei.xml Lied 38 (Verse 37 und 41,
Werte "a" und "e") unangetastet: es steht im Block des Verses und wird von
einem <pc> gefolgt.

Auswahlregel
------------
Ein Token ist eine Strophenziffer, wenn alle vier Punkte gelten:

  1. Es steht im LETZTEN xml:id-Block seines <l> bzw. <ab>.
  2. Dieser Block enthaelt genau ein <w> und kein <pc>.
  3. Bei <l>: es gibt mindestens einen frueheren Block (der Vers selbst).
     Bei <ab>: der Block ist der einzige Inhalt (alle 33 <ab> in HUG sind
     reine Zifferntraeger und stehen als erstes Kind eines <div>).
  4. Der Text besteht nur aus roemischen Ziffernzeichen, und @pos ist
     entweder "DIG" oder nicht gesetzt.

Invariante
----------
Pro <div> mit Strophen muss die Zahl der gefundenen Ziffern der Zahl der
<lg type="stanza"> entsprechen, oder null sein (Datei schon bereinigt). Jeder
andere Wert bricht ab, statt zu raten. Diese Invariante ist der eigentliche
Schutz: sie faellt, sobald die Auswahl ein Wort zu viel oder eine Ziffer zu
wenig erwischt.

Der Zahlenwert wird NICHT als Bedingung verwendet, nur berichtet: in HUG
weichen 6 der 814 Ziffern vom Wert der zugehoerigen Strophe ab, weil in der
Ziffer selbst ein Zeichen fehlt oder zu viel ist (Lied 31 "xxiii" statt
"xxviii", Lied 33 "xxxix" statt "xxix", Lied 28 "cxlvix" fuer 149).

Verwendung
----------
    python -X utf8 scripts/remove-stanza-numerals-138.py --dry-run
    python -X utf8 scripts/remove-stanza-numerals-138.py --apply

Standard ist der Probelauf. Nachgelagert (Data-Change-Lifecycle, siehe
docs/DATA-MODEL.md): variants.xml regenerieren, beide Indexe und die API neu
bauen, Versionen heben. Das Skript fasst nur das TEI an.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from lxml import etree

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML = "http://www.w3.org/XML/1998/namespace"
XML_ID = f"{{{NS_XML}}}id"
W_TAG = f"{{{NS_TEI}}}w"
PC_TAG = f"{{{NS_TEI}}}pc"
L_TAG = f"{{{NS_TEI}}}l"
AB_TAG = f"{{{NS_TEI}}}ab"
LG_TAG = f"{{{NS_TEI}}}lg"
HI_TAG = f"{{{NS_TEI}}}hi"
DIV_TAG = f"{{{NS_TEI}}}div"

ROEMISCH = re.compile(r"^[ivxlcdm]+$", re.IGNORECASE)

WURZEL = Path(__file__).resolve().parent.parent
ZIEL = WURZEL / "tei" / "HUG.tei.xml"


def id_block(xml_id):
    """Der xml:id-Block ohne den laufenden Token-Index (HUG_30041_0 -> HUG_30041)."""
    return xml_id.rsplit("_", 1)[0] if xml_id else ""


def roemisch_zu_zahl(s):
    werte = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
    s = s.lower()
    gesamt = 0
    k = 0
    while k < len(s):
        v = werte[s[k]]
        if k + 1 < len(s) and werte[s[k + 1]] > v:
            gesamt += werte[s[k + 1]] - v
            k += 2
        else:
            gesamt += v
            k += 1
    return gesamt


def bloecke(container):
    """[(block_id, [elemente]), ...] in Dokumentreihenfolge."""
    gruppen = []
    for el in container.iter(W_TAG, PC_TAG):
        b = id_block(el.get(XML_ID))
        if not gruppen or gruppen[-1][0] != b:
            gruppen.append((b, []))
        gruppen[-1][1].append(el)
    return gruppen


def ist_ziffer(container):
    """Das Ziffern-<w> des Containers, oder None."""
    gruppen = bloecke(container)
    if not gruppen:
        return None

    letzter_block, elemente = gruppen[-1]

    # Punkt 2: genau ein <w>, kein <pc>
    ws = [e for e in elemente if e.tag == W_TAG]
    if len(ws) != 1 or len(elemente) != 1:
        return None

    # Punkt 3: bei <l> muss der Vers selbst davor stehen
    if container.tag == L_TAG and len(gruppen) < 2:
        return None
    if container.tag == AB_TAG and len(gruppen) != 1:
        return None

    w = ws[0]
    text = (w.text or "").strip()

    # Punkt 4
    if not ROEMISCH.match(text):
        return None
    if w.get("pos") not in (None, "DIG"):
        return None

    return w


def sammle(root):
    """(kandidaten, verletzungen, uebersprungen).

    Verletzungen der Invariante brechen ab. `uebersprungen` sind divs ohne
    <lg type="stanza">: fuer die gibt es keine Invariante, sie werden nicht
    angefasst. Sie werden gezaehlt und berichtet, statt still zu verschwinden,
    denn eine Ziffer in einem strophenlosen div wuerde sonst kommentarlos
    ueberleben. In HUG sind das 7 der 40 Lieder, und dort liegt keine Ziffer.
    """
    kandidaten = []
    verletzungen = []
    uebersprungen = []

    for div in root.iter(DIV_TAG):
        strophen = [lg for lg in div.findall(LG_TAG) if lg.get("type") == "stanza"]
        if not strophen:
            # Nur melden, wenn dort ueberhaupt etwas Ziffernartiges liegt.
            offen = sum(1 for c in div.iter(L_TAG, AB_TAG)
                        if ist_ziffer(c) is not None)
            uebersprungen.append((div.get("n"), offen))
            continue

        gefunden = []
        for container in div.iter(L_TAG, AB_TAG):
            w = ist_ziffer(container)
            if w is not None:
                gefunden.append((container, w))

        if len(gefunden) == 0:
            continue  # dieser div ist schon bereinigt
        if len(gefunden) != len(strophen):
            verletzungen.append((div.get("n"), len(strophen), len(gefunden)))
            continue

        kandidaten.extend(gefunden)

    # Schutz gegen geschachtelte <div>: root.iter(DIV_TAG) trifft aussen und
    # innen, ein Kandidat wuerde dann zweimal in entferne() laufen. HUG hat 40
    # flache Geschwister-divs, das ist hier also Vorsorge fuer die
    # Wiederverwendung auf anderen Texten.
    doppelt = len(kandidaten) - len({id(w) for _, w in kandidaten})
    if doppelt:
        verletzungen.append(("(geschachtelte divs)", 0, doppelt))

    return kandidaten, verletzungen, uebersprungen


def wert_abgleich(kandidaten):
    """[(div_n, verstext, ist, soll)] fuer Ziffern, deren Wert nicht zur Strophe passt."""
    abweichungen = []
    for container, w in kandidaten:
        if container.tag == AB_TAG:
            soll = 1
        else:
            lg = container.getparent()
            if lg is None or lg.tag != LG_TAG:
                continue
            naechste = None
            for geschwister in lg.itersiblings():
                if geschwister.tag == LG_TAG:
                    naechste = geschwister
                    break
            if naechste is None:
                continue
            soll = naechste.get("n")
        text = (w.text or "").strip()
        ist = roemisch_zu_zahl(text)
        if str(ist) != str(soll):
            div = container
            while div is not None and div.tag != DIV_TAG:
                div = div.getparent()
            abweichungen.append((div.get("n") if div is not None else "?",
                                 container.get("n"), text, ist, soll))
    return abweichungen


def entferne(w):
    """Ziffer loeschen, samt leer werdendem <hi>- und <ab>-Huelle.

    Die Einrueckung des schliessenden Tags bleibt erhalten, indem das tail des
    entfernten Knotens an den Vorgaenger bzw. auf den Elterntext wandert.
    """
    ziel = w
    # Eine <hi>- bzw. <ab>-Huelle geht mit, aber nur wenn sie ausser der
    # Ziffer NICHTS traegt. `len(el) == 1` prueft nur Element-Kinder; ohne die
    # Textpruefung wuerde ein <hi>Anmerkung <w>ii</w></hi> samt Anmerkung
    # verschwinden. In HUG tragen die Huellen nur Einrueckungs-Whitespace.
    def huelle_leer(el):
        return not (el.text or "").strip()

    eltern = ziel.getparent()
    if (eltern is not None and eltern.tag == HI_TAG
            and len(eltern) == 1 and huelle_leer(eltern)):
        ziel = eltern
    eltern = ziel.getparent()
    if (eltern is not None and eltern.tag == AB_TAG
            and len(eltern) == 1 and huelle_leer(eltern)):
        ziel = eltern

    eltern = ziel.getparent()
    vorher = ziel.getprevious()
    if vorher is not None:
        vorher.tail = ziel.tail
    else:
        eltern.text = ziel.tail
    eltern.remove(ziel)


def serialize(tree, pfad):
    # lxml verschluckt beim Serialisieren den Umbruch zwischen der letzten
    # Processing Instruction und <TEI>.
    data = etree.tostring(tree, encoding="UTF-8", xml_declaration=True)
    data = data.replace(b"?><TEI ", b"?>\n<TEI ")
    if not data.endswith(b"\n"):
        data += b"\n"
    pfad.write_bytes(data)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--apply", action="store_true",
                   help="Aenderung schreiben (ohne diese Flag nur Bericht)")
    p.add_argument("--dry-run", action="store_true",
                   help="Probelauf, ist ohnehin der Standard (nur zur Deutlichkeit)")
    p.add_argument("--datei", type=Path, default=ZIEL,
                   help=f"TEI-Datei (Standard: {ZIEL.name})")
    args = p.parse_args()

    tree = etree.parse(str(args.datei))
    root = tree.getroot()

    vorher_w = sum(1 for _ in root.iter(W_TAG))
    kandidaten, verletzungen, uebersprungen = sammle(root)

    print(f"Datei:            {args.datei.name}")
    print(f"<w> gesamt:       {vorher_w}")
    print(f"Ziffern gefunden: {len(kandidaten)}")

    if uebersprungen:
        offen = sum(n for _, n in uebersprungen)
        print(f"divs ohne Strophen: {len(uebersprungen)} "
              f"(uebersprungen, dort {offen} ziffernartige Token)")
        if offen:
            print("  ACHTUNG: dort liegen Ziffern, die keine Invariante schuetzt:")
            for div_n, n in uebersprungen:
                if n:
                    print(f"    Lied {div_n}: {n}")

    if verletzungen:
        print()
        print(f"ABBRUCH: in {len(verletzungen)} div(s) passt die Zahl der Ziffern "
              f"nicht zur Zahl der Strophen.")
        for div_n, strophen, gefunden in verletzungen[:20]:
            print(f"  Lied {div_n}: {strophen} Strophen, aber {gefunden} Ziffern")
        print()
        print("Entweder ist die Datei halb bereinigt oder die Auswahlregel trifft")
        print("nicht. Es wurde nichts geschrieben.")
        return 1

    if not kandidaten:
        print("Nichts zu tun.")
        return 0

    traeger = Counter(etree.QName(c).localname for c, _ in kandidaten)
    lemmatisiert = sum(1 for _, w in kandidaten if w.get("pos") == "DIG")
    print(f"  davon in <l>:   {traeger.get('l', 0)}")
    print(f"  davon in <ab>:  {traeger.get('ab', 0)}")
    print(f"  als DIG lemmatisiert: {lemmatisiert}, "
          f"nicht annotiert: {len(kandidaten) - lemmatisiert}")

    abweichungen = wert_abgleich(kandidaten)
    print(f"Wert passt zur Strophennummer: {len(kandidaten) - len(abweichungen)} "
          f"von {len(kandidaten)}")
    for div_n, vers_n, text, ist, soll in abweichungen:
        print(f"  Lied {div_n}, Vers {vers_n}: '{text}' = {ist}, "
              f"Strophe waere {soll}")

    if not args.apply:
        print()
        print("Probelauf, nichts geschrieben. Mit --apply anwenden.")
        return 0

    # Differenziell: HUG hat einen Vers, der schon vorher ohne <w> ist (n=738,
    # nur ein <caesura/>). Die Elemente selbst festhalten, nicht ihre id():
    # lxml-Proxies werden zwischen Iterationen verworfen und neu erzeugt
    # (siehe docs/DECISIONS.md zum v4.1.0-Build).
    leer_vorher = [l_el for l_el in root.iter(L_TAG)
                   if not [x for x in l_el.iter(W_TAG)]]

    for _, w in kandidaten:
        entferne(w)

    nachher_w = sum(1 for _ in root.iter(W_TAG))
    if nachher_w != vorher_w - len(kandidaten):
        print(f"ABBRUCH: <w>-Bilanz stimmt nicht ({vorher_w} - {len(kandidaten)} "
              f"!= {nachher_w}). Nichts geschrieben.")
        return 1

    neu_leer = [l_el.get("n") for l_el in root.iter(L_TAG)
                if not [x for x in l_el.iter(W_TAG)]
                and not any(bekannt is l_el for bekannt in leer_vorher)]
    if neu_leer:
        print(f"ABBRUCH: {len(neu_leer)} Verse wuerden durch die Loeschung "
              f"leer: {neu_leer[:10]}")
        return 1

    leere_huellen = [etree.QName(el).localname for el in root.iter(HI_TAG, AB_TAG)
                     if len(el) == 0 and not (el.text or "").strip()]
    if leere_huellen:
        print(f"ABBRUCH: {len(leere_huellen)} leere Huellen uebrig "
              f"({Counter(leere_huellen)}). Nichts geschrieben.")
        return 1

    serialize(tree, args.datei)
    print()
    if leer_vorher:
        print(f"Hinweis: {len(leer_vorher)} Vers(e) waren schon vorher ohne <w> "
              f"(HUG n=738 traegt nur ein <caesura/>); unveraendert.")
    print(f"{len(kandidaten)} Strophenziffern entfernt, <w> jetzt {nachher_w}.")
    print("Naechste Schritte: variants.xml regenerieren, Indexe + API neu bauen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
