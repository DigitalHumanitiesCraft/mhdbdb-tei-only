#!/usr/bin/env python3
"""01-segmentierung.py: Segmentierungstabelle der Weingruss-Zeugen (#147).

Liest die 27 Einzeltextseiten aus dem gepinnten Cache (Manifest, siehe
00-fetch-wiki.py) und schreibt ingest/bre/segmentierung.tsv: eine Zeile je
(Einzeltext, Zeuge) mit den Spalten
  text_titel, editionssigle, signatur_label, blatt, erster_vers, ueberschrift
erster_vers = erste Verszeile in der Synopsenspalte des Zeugen (Zeile mit den
Texten, nicht die Zeile mit den Ueberschriften/Rubriken), bereinigt wie in
bre_wikitext.vergleichstext. ueberschrift = Zellinhalt der Ueberschriftenzeile
desselben Zeugen (Zeilen mit " / " verbunden, bereinigt, leer wenn keine); sie
dient 02 dazu, die Zeilen vor dem Textanfang als <head> zu erkennen.

Struktur (an allen 27 Seiten geprueft, Abweichung = harter Fehler mit Titel):
  * Synopse: eine wikitable mit genau 3 Zeilen: Spaltenkoepfe "<Signatur> (Sigle X)",
    Ueberschriften, Texte; gleich viele Zellen je Zeile.
  * Seiten ohne Synopse (Pseudo-Weingruesse): genau ein Zeuge aus der Infobox
    "ueberlieferung", Text unter "== Transkription ==".
Leere Textzelle = der Zeuge hat diesen Text nicht (gezaehlt, keine Zeile).

Aufruf: python -P -E scripts/ingest/bre/01-segmentierung.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_common as bc  # noqa: E402
import bre_wikitext as bw  # noqa: E402

KOPF = ["text_titel", "editionssigle", "signatur_label", "blatt", "erster_vers", "ueberschrift"]
RE_ZELLENKOPF = re.compile(r'^\|\s*(?:(?:style|class|colspan|rowspan|width)=[^|]*\|)?(.*)$')
FEHLSTELLEN = []
RE_SIGLE = re.compile(r"^(.*?)\s*\(Sigle\s+([^)]+)\)\s*$")


def norm_sig(s):
    return re.sub(r"[\s.]", "", s).lower()


def zerlege_label(label):
    """'Mgq 495, falscher Eintrag' -> ('Mgq 495', 'falscher Eintrag'); sonst (label, '')."""
    if ", " in label:
        basis, qual = label.split(", ", 1)
        return basis.strip(), qual.strip()
    return label, ""


def zeuge_zu_sigle(sig_roh, label_voll, titel):
    label = zerlege_label(label_voll)[0]
    sig = re.sub(r"<sup>(.*?)</sup>", r"\1", sig_roh).strip()
    if sig not in bc.ZEUGEN:
        raise bc.HarterFehler(f"{titel}: unbekannte Sigle {sig!r} (Kopf {label!r})")
    n_l = set(re.findall(r"\w+", label.replace(".", "").lower()))
    n_z = set(re.findall(r"\w+", bc.ZEUGEN[sig][0].replace(".", "").lower()))
    n_z -= {"d1", "d2", "d3", "d4", "d5", "d6"}
    if not (n_l <= n_z or n_z <= n_l):
        raise bc.HarterFehler(f"{titel}: Signatur {label!r} passt nicht zu Sigle {sig} "
                              f"({bc.ZEUGEN[sig][0]!r})")
    return sig


def infobox_ueberlieferung(inhalt, titel):
    m = re.findall(r"^\|\s*überlieferung\s*=(.*)$", inhalt, re.M)
    if len(m) != 1:
        raise bc.HarterFehler(f"{titel}: {len(m)} Infobox-Felder 'überlieferung' statt 1")
    eintraege = [e for e in re.split(r"<br\s*/?>", m[0]) if e.strip()]
    # Wikilinks "[url Text]" -> "Text"
    return [re.sub(r"\[(?:https?://\S+)\s+([^\]]*)\]", r"\1", e).strip() for e in eintraege]


def blatt_zu(label_voll, eintraege, titel):
    """Blattangabe aus dem Infobox-Eintrag, der das Label enthaelt.

    Label mit Zusatz ("Mgq 495, falscher Eintrag"): der Eintrag fuehrt mehrere
    Blattangaben, jede mit dem Zusatz in Klammern: "12r-12v (falscher Eintrag), ...".
    """
    label, qual = zerlege_label(label_voll)
    n_l = norm_sig(label)
    treffer = [e for e in eintraege if n_l in norm_sig(e)]
    if len(treffer) != 1:
        raise bc.HarterFehler(f"{titel}: {len(treffer)} Infobox-Eintraege fuer {label!r} statt 1: {treffer}")
    e = treffer[0]
    # hinter dem Label (erste Fundstelle, Leerraum/Punkte tolerant)
    muster = r"[\s.]*".join(re.escape(c) for c in re.sub(r"[\s.]", "", label))
    m = re.search(muster, e, re.I)
    if not m:
        raise bc.HarterFehler(f"{titel}: Label {label!r} nicht auffindbar in {e!r}")
    rest = e[m.end():].lstrip("] ,:")
    if qual:
        kurz = re.sub(r"^Teil\s+", "", qual)  # "Teil A" -> Infobox "(A)"
        mq = None
        for q in (qual, kurz):
            mq = re.search(r"([^,;()]+?)\s*\(" + re.escape(q) + r"\)", rest)
            if mq:
                break
        if not mq:
            raise bc.HarterFehler(f"{titel}: Zusatz {qual!r} nicht in {e!r}")
        return mq.group(1).strip()
    if rest.startswith("(") or not rest:
        if "verschollen" in rest:
            return "verschollen"
        raise bc.HarterFehler(f"{titel}: keine Blattangabe fuer {label!r} in {e!r}")
    rest = re.split(r"\s+\(", rest, maxsplit=1)[0].strip()
    rest = re.sub(r"^S\.\s*", "", rest)
    if not rest:
        raise bc.HarterFehler(f"{titel}: leere Blattangabe fuer {label!r} in {e!r}")
    return rest


def zellen(zeilenblock, titel):
    """Zellen einer wikitable-Zeile: Liste von Listen von Inhaltszeilen."""
    zs = []
    for z in zeilenblock.split("\n"):
        if z.startswith("||"):  # leere Zelle (oder Inhalt hinter dem zweiten Strich)
            zs.append([z[2:]] if z[2:].strip() else [])
        elif z.startswith("|"):
            m = RE_ZELLENKOPF.match(z)
            if not m:
                raise bc.HarterFehler(f"{titel}: Zellenkopf nicht lesbar: {z[:60]!r}")
            if not re.match(r"^\|\s*(style|class|colspan|rowspan|width)=", z):
                raise bc.HarterFehler(f"{titel}: unbekannter Zellenkopf: {z[:60]!r}")
            zs.append([m.group(1)] if m.group(1).strip() else [])
        elif z.strip():
            if not zs:
                raise bc.HarterFehler(f"{titel}: Inhalt vor der ersten Zelle: {z[:60]!r}")
            zs[-1].append(z)
    return zs


def bereinigt(zeilen):
    """Inhaltszeilen bereinigen, leere (nach Bereinigung) entfernen."""
    einzeln = [t for z in zeilen for t in re.split(r"<br\s*/?>", z)]
    return [v for v in (bw.vergleichstext(z) for z in einzeln) if v]


def seite_mit_synopse(titel, inhalt, eintraege):
    if inhalt.count("{|") != 1 or inhalt.count("\n|}") != 1:
        raise bc.HarterFehler(f"{titel}: {inhalt.count('{|')} Tabellenanfaenge / "
                              f"{inhalt.count(chr(10) + '|}')} -enden statt 1/1")
    tab = inhalt.split("{|", 1)[1].split("\n|}", 1)[0]
    teile = re.split(r"^\|-.*$", tab, flags=re.M)
    # teile[0] = Tabellenattribute vor dem ersten |-, letzter = leer vor |}
    if len(teile) != 5 or "\n" in teile[0].strip() or teile[4].strip():
        raise bc.HarterFehler(f"{titel}: {len(teile) - 2} Tabellenzeilen statt 3 "
                              f"(Teile {[len(t) for t in teile]})")
    kopf, ueb, text = (zellen(t, titel) for t in teile[1:4])
    if not (len(kopf) == len(ueb) == len(text)):
        raise bc.HarterFehler(f"{titel}: Zellenzahl Kopf/Ueberschrift/Text = "
                              f"{len(kopf)}/{len(ueb)}/{len(text)}")
    rows, leer = [], 0
    for k, u, t in zip(kopf, ueb, text):
        if len(k) != 1:
            raise bc.HarterFehler(f"{titel}: Spaltenkopf mit {len(k)} Zeilen: {k}")
        raw = re.sub(r"'''", "", k[0])
        m = RE_SIGLE.match(raw.strip())
        if not m:
            raise bc.HarterFehler(f"{titel}: Spaltenkopf ohne '(Sigle X)': {k[0]!r}")
        label = m.group(1).strip()
        sig = zeuge_zu_sigle(m.group(2), label, titel)
        verse = bereinigt(t)
        if not verse:
            leer += 1
            continue
        if verse[0] == "[...]":  # Fehlstelle am Textanfang: der Zeuge bietet den Text nicht
            FEHLSTELLEN.append(f"{titel} / {sig}")
            continue
        rows.append([titel, sig, label, blatt_zu(label, eintraege, titel), verse[0],
                     " / ".join(bereinigt(u))])
    return rows, leer, len(kopf)


def seite_ohne_synopse(titel, inhalt, eintraege):
    if "{|" in inhalt:
        raise bc.HarterFehler(f"{titel}: Tabelle vorhanden, aber nicht erwartet")
    if len(eintraege) != 1:
        raise bc.HarterFehler(f"{titel}: {len(eintraege)} Zeugen in der Infobox statt 1")
    e = eintraege[0]
    treffer = [s for s, (name, _) in bc.ZEUGEN.items() if norm_sig(name) in norm_sig(e)]
    if len(treffer) != 1:
        raise bc.HarterFehler(f"{titel}: Zeuge nicht eindeutig aus {e!r}: {treffer}")
    sig = treffer[0]
    label = bc.ZEUGEN[sig][0]
    teile = re.split(r"^==\s*Transkription\b.*$", inhalt, flags=re.M)
    if len(teile) != 2:
        raise bc.HarterFehler(f"{titel}: {len(teile) - 1} Transkriptions-Ueberschriften statt 1")
    block = re.split(r"^==", teile[1], flags=re.M)[0]
    zeilen = [z for z in block.split("\n") if z.strip()]
    kopfzeilen = []
    while zeilen and bw.RE_ROT_GANZ.match(zeilen[0]):
        kopfzeilen.append(zeilen.pop(0))
    verse = bereinigt(zeilen[:1])
    if not verse:
        raise bc.HarterFehler(f"{titel}: kein Vers unter der Transkription")
    return [[titel, sig, label, blatt_zu(label, eintraege, titel), verse[0],
             " / ".join(bereinigt(kopfzeilen))]], 0, 1


def main():
    bc.ausgabe_utf8()
    try:
        return lauf()
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        return 1


def lauf():
    doku = bc.lade_seite(bc.DOKU_TITEL)["inhalt"]
    titel_liste = bc.einzeltext_titel(doku)
    if len(titel_liste) != 27:
        raise bc.HarterFehler(f"{len(titel_liste)} Einzeltextseiten statt 27")
    alle, gesehen = [], set()
    n_synopse = n_ohne = 0
    for titel in titel_liste:
        inhalt = bc.lade_seite(titel)["inhalt"]
        eintraege = infobox_ueberlieferung(inhalt, titel)
        if "{|" in inhalt:
            rows, leer, spalten = seite_mit_synopse(titel, inhalt, eintraege)
            n_synopse += 1
        else:
            rows, leer, spalten = seite_ohne_synopse(titel, inhalt, eintraege)
            n_ohne += 1
        for r in rows:
            for f in r:
                if "\t" in f or "\n" in f:
                    raise bc.HarterFehler(f"{titel}: Tab/Zeilenumbruch im Feld {f!r}")
            k = (r[0], r[1], r[2])
            if k in gesehen:
                raise bc.HarterFehler(f"{titel}: Zeuge {r[1]} ({r[2]}) doppelt")
            gesehen.add(k)
        print(f"  {titel}: {len(rows)} Zeugen mit Text (von {spalten} Spalten, {leer} leer)")
        alle.extend(rows)
    bc.INGEST_DIR.mkdir(parents=True, exist_ok=True)
    zeilen = ["\t".join(KOPF)] + ["\t".join(r) for r in alle]
    bc.SEGMENTIERUNG.write_text("\n".join(zeilen) + "\n", encoding="utf-8", newline="\n")
    je_zeuge = {}
    for r in alle:
        je_zeuge[r[1]] = je_zeuge.get(r[1], 0) + 1
    print(f"Fehlstellen ([...] statt Text, keine Zeile): {len(FEHLSTELLEN)}: {FEHLSTELLEN}")
    print(f"Seiten: {len(titel_liste)} ({n_synopse} mit Synopse, {n_ohne} ohne)")
    print(f"Zeilen: {len(alle)} (Einzeltext x Zeuge) in {bc.SEGMENTIERUNG}")
    print("Texte je Zeuge: " + ", ".join(f"{s}={n}" for s, n in sorted(je_zeuge.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
