#!/usr/bin/env python3
"""23-normdaten.py: Normdaten im Header der BRE-Zeugen setzen (#147).

Entscheidung KZW vom 24.11.2026 (#147):
  - ein Werk je Zeuge, "Weingruesse (<Aufbewahrungsort>, <Signatur>)", Sigle BRE_<Zeuge>
  - Gattung genre_315cf46f (Weingruss)
  - Autor Hans Rosenpluet (persons.xml#person_907), wo das Brevitas-Wiki ihn nennt, sonst
    anonym. Gemischte Zeugen tragen beide. Gengenbach ist nie Autor.

Was das Skript tut, an Ort und Stelle in ingest/bre/BRE_*.tei.xml, NUR im Header (02 darf
nicht neu laufen, das verlaere die Annotation der Phasen 1 bis 3):
  msIdentifier/@corresp, titleStmt/title (= Werktitel; msName bleibt), das @corresp des
  digitalIntermediary, die category der Gattung, die Autoren in titleStmt und particDesc,
  eine <change>-Zeile. Die Sprachstufe (language ident="TBD", #118) bleibt unberuehrt.

Woher die Autorschaft kommt: aus den Texten, die in der jeweiligen TEI-Datei stehen. Jeder
Text traegt einen Kommentar "Text N: <text_titel> (<Signatur>, <Blatt>)" (von 02 geschrieben);
der text_titel ist der Linkname der Dokumentationsseite in ingest/bre/segmentierung.tsv und
nennt den Autor in Klammern, "... (Hans Rosenpluet)", wo das Wiki ihn nennt. Ein Text, der
sich keiner Zeile der Segmentierung zuordnen laesst, ein anderer Autorname und ein
unbekannter Kommentar sind harte Fehler. Vorspann (bre_common.VORSPANN): ein Fragment erbt
von dem Werk, das es benennt (bre_common.VORSPANN_WERK), ein Text ohne Einzelseite ist anonym.

Zweite Ausgabe: ingest/bre/works-eintraege.xml, die Werkeintraege als Fragment (Muster
work_WZB in works.xml). Sie gehen NICHT nach authority-files/works.xml, solange die Zeugen
nicht in tei/ stehen. Das Fragment wird gegen schema/mhdbdb-authority.rng validiert, in eine
Kopie von works.xml eingesetzt.

Idempotent: ein zweiter Lauf aendert kein Byte. Jedes Feld akzeptiert genau zwei Zustaende,
den Platzhalter aus 02 und den Sollzustand; alles andere ist ein harter Fehler.

Aufruf: python -P -E scripts/ingest/bre/23-normdaten.py [--trocken]
"""
import argparse
import datetime
import re
import sys
import urllib.parse
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_annot as ba  # noqa: E402
import bre_common as bc  # noqa: E402

T = "http://www.tei-c.org/ns/1.0"
NS = {"t": T}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

ZEUGEN_TSV = bc.INGEST_DIR / "zeugen.tsv"
FRAGMENT = bc.INGEST_DIR / "works-eintraege.xml"
WORKS = bc.REPO / "authority-files" / "works.xml"
PERSONS = bc.REPO / "authority-files" / "persons.xml"
GENRES = bc.REPO / "authority-files" / "genres.xml"
SCHEMA_AUTHORITY = bc.REPO / "schema" / "mhdbdb-authority.rng"

PERSON_ROSEN = "person_907"
PERSON_ANONYM = "person_anonym"
GENRE = "genre_315cf46f"
MARKE = "Normdaten im Header gesetzt (#147"
TEXT_KOMMENTAR = re.compile(r"^ Text (\d+): (.+) $")
VORSPANN_KOMMENTAR = re.compile(r"^Vorspann \((\w+)\)$")
FRAGMENT_KOMMENTAR = re.compile(r"^(.+) \(Fragment\)$")
AUTOR_SUFFIX = re.compile(r"^(.*\S) \(([^()]+)\)$")


def q(tag):
    return f"{{{T}}}{tag}"


# ---------------------------------------------------------------- Normdaten

def lade_normdaten():
    """-> (personen, genre). personen: pid -> dict(name, idnos); genre: dict(terme).

    Der Name der Person kommt aus persons.xml, nicht aus diesem Skript: dort steht, wie der
    Autor heisst. Fehlt ein Eintrag, ist das ein harter Fehler."""
    pers = etree.parse(str(PERSONS))
    personen = {}
    for pid in (PERSON_ROSEN, PERSON_ANONYM):
        p = pers.xpath(f"//t:person[@xml:id='{pid}']", namespaces=NS)
        if len(p) != 1:
            raise bc.HarterFehler(f"{pid}: {len(p)} Eintraege in persons.xml statt 1")
        namen = p[0].xpath("t:persName[@type='preferred']/text()", namespaces=NS)
        if len(namen) != 1:
            raise bc.HarterFehler(f"{pid}: {len(namen)} preferred-Namen in persons.xml statt 1")
        idnos = [(i.get("type"), i.text) for i in p[0].findall(q("idno"))]
        personen[pid] = {"name": namen[0], "idnos": idnos if pid == PERSON_ROSEN else []}
    gen = etree.parse(str(GENRES))
    g = gen.xpath(f"//t:category[@xml:id='{GENRE}']", namespaces=NS)
    if len(g) != 1:
        raise bc.HarterFehler(f"{GENRE}: {len(g)} Eintraege in genres.xml statt 1")
    terme = [(t.get(XML_LANG), t.text) for t in g[0].iter(q("term"))]
    if not terme or terme[0][0] != "de" or any(not l or not x for l, x in terme):
        raise bc.HarterFehler(f"{GENRE}: Terme in genres.xml unlesbar: {terme}")
    return personen, {"terme": terme}


# ---------------------------------------------------------------- Autorschaft

def werktitel_von(z):
    """Werktitel aus einer Zeile von zeugen.tsv: Handschrift "Weingrüße (<Kurzform>, <Signatur>)",
    Druck "Weingrüße (Druck, <Signatur>)". Unbekannter Typ oder Aufbewahrung ist ein harter Fehler."""
    sig = z["signatur"].strip()
    if not sig:
        raise bc.HarterFehler(f"{z['mhdbdb_sigle']}: signatur leer in zeugen.tsv")
    if z["typ"] == "Druck":
        return f"Weingrüße (Druck, {sig})"
    if z["typ"] != "Handschrift":
        raise bc.HarterFehler(f"{z['mhdbdb_sigle']}: unbekannter typ {z['typ']!r} in zeugen.tsv")
    kurz = bc.AUFBEWAHRUNG_KURZ.get(z["aufbewahrung"])
    if kurz is None:
        raise bc.HarterFehler(f"{z['mhdbdb_sigle']}: Aufbewahrung {z['aufbewahrung']!r} fehlt in "
                              f"bre_common.AUFBEWAHRUNG_KURZ")
    return f"Weingrüße ({kurz}, {sig})"


def rosen_flag(titel, personen):
    """True, wenn der Linkname den Autor in Klammern nennt. Ein anderer Name ist ein harter Fehler."""
    m = AUTOR_SUFFIX.match(titel)
    if not m:
        return False
    if m.group(2) != personen[PERSON_ROSEN]["name"]:
        raise bc.HarterFehler(f"unbekannter Autorzusatz {m.group(2)!r} im text_titel {titel!r}")
    return True


def texte_aus_kommentaren(root, ed):
    """Die Kommentare der Einzeltexte im Body, in Reihenfolge. -> Liste des Kommentartexts.

    Der Kommentar zum ausgeschlossenen Teil (bre_common.TEIL_AUSGESCHLOSSEN) ist der einzige
    andere erlaubte; jeder weitere ist ein harter Fehler. Die Zahl der Kommentare muss die
    der <div type="section"> sein, sonst gibt es einen Text ohne Titel oder einen Titel ohne Text."""
    body = root.find(f".//{q('body')}")
    if body is None:
        raise bc.HarterFehler(f"{ed}: kein <body>")
    erlaubt = bc.TEIL_AUSGESCHLOSSEN[ed][1] if ed in bc.TEIL_AUSGESCHLOSSEN else None
    texte = []
    for c in body.iter(etree.Comment):
        if erlaubt and c.text.strip() == erlaubt:
            continue
        m = TEXT_KOMMENTAR.match(c.text)
        if not m:
            raise bc.HarterFehler(f"{ed}: unbekannter Kommentar im Body: {c.text!r}")
        texte.append((int(m.group(1)), m.group(2)))
    abschnitte = [d.get("n") for d in body.iter(q("div")) if d.get("type") == "section"]
    if not texte:
        raise bc.HarterFehler(f"{ed}: keine Text-Kommentare im Body")
    if [str(n) for n, _ in texte] != abschnitte:
        raise bc.HarterFehler(f"{ed}: Text-Kommentare {[n for n, _ in texte]} != Abschnitte {abschnitte}")
    return [t for _, t in texte]


def autoren_des_zeugen(ed, root, rows, personen):
    """-> (Liste der Personen-IDs, Zahl der Rosenpluet-Texte, Zahl der Texte, Belege).

    Rosenpluet steht zuerst, wie bei HOF der benannte vor dem anonymen Autor."""
    zeilen = {f"{r['text_titel']} ({r['signatur_label']}, {r['blatt']})": r
              for r in rows if r["editionssigle"] == ed}
    basis = {}  # Werktitel ohne Autorzusatz -> Flag, ueber alle Zeugen
    for r in rows:
        m = AUTOR_SUFFIX.match(r["text_titel"])
        b = m.group(1) if m and m.group(2) == personen[PERSON_ROSEN]["name"] else r["text_titel"]
        f = rosen_flag(r["text_titel"], personen)
        if basis.setdefault(b, f) != f:
            raise bc.HarterFehler(f"{b!r}: Autorzusatz in der Segmentierung nicht einheitlich")
    flags = []
    for kommentar in texte_aus_kommentaren(root, ed):
        v = VORSPANN_KOMMENTAR.match(kommentar)
        fr = FRAGMENT_KOMMENTAR.match(kommentar)
        if v:
            if ed not in bc.VORSPANN or bc.VORSPANN[ed][0] != v.group(1):
                raise bc.HarterFehler(f"{ed}: Vorspann {v.group(1)!r} steht nicht in bre_common.VORSPANN")
            flags.append((kommentar, False))  # benennt kein Werk: anonym
        elif fr:
            werk = fr.group(1)
            if bc.VORSPANN_WERK.get(ed) != werk:
                raise bc.HarterFehler(f"{ed}: Fragment {werk!r} steht nicht in bre_common.VORSPANN_WERK")
            if werk not in basis:
                raise bc.HarterFehler(f"{ed}: Werk {werk!r} des Fragments steht nicht in der Segmentierung")
            flags.append((kommentar, basis[werk]))
        elif kommentar in zeilen:
            flags.append((kommentar, rosen_flag(zeilen[kommentar]["text_titel"], personen)))
        else:
            raise bc.HarterFehler(f"{ed}: Text {kommentar!r} ist keiner Zeile der Segmentierung zuzuordnen")
    n_r = sum(1 for _, f in flags if f)
    pids = ([PERSON_ROSEN] if n_r else []) + ([PERSON_ANONYM] if n_r < len(flags) else [])
    return pids, n_r, len(flags), flags


# ---------------------------------------------------------------- Bausteine

def E(tag, attrib=None, text=None, kids=()):
    el = etree.Element(q(tag), nsmap={None: T})
    for k, v in (attrib or {}).items():
        el.set(k, v)
    el.text = text
    for k in kids:
        el.append(k)
    return el


def einruecken(el, indent):
    """Setzt Text und Tails der Kinder auf Einrueckung mit zwei Leerzeichen je Ebene."""
    if len(el):
        el.text = "\n" + indent + "  "
        for k in el:
            einruecken(k, indent + "  ")
            k.tail = "\n" + indent + "  "
        el[-1].tail = "\n" + indent
    return el


def einzug(el):
    vor = el.getprevious()
    s = vor.tail if vor is not None else el.getparent().text
    if not s or "\n" not in s:
        raise bc.HarterFehler(f"Einrueckung von <{etree.QName(el).localname}> nicht lesbar")
    return s.rsplit("\n", 1)[-1]


def sig(el):
    """Struktur samt Whitespace, ohne den Tail des Elements selbst."""
    return (el.tag, tuple(sorted(el.attrib.items())), el.text or "",
            tuple((sig(c), c.tail or "") for c in el))


def ersetze_folge(parent, alte, neue, indent):
    idx = parent.index(alte[0])
    schluss = alte[-1].tail
    for a in alte:
        parent.remove(a)
    for i, n in enumerate(neue):
        n.tail = ("\n" + indent) if i < len(neue) - 1 else schluss
        parent.insert(idx + i, n)


def autor_el(pid, personen, ref_praefix):
    return E("author", {"ref": ref_praefix + pid}, personen[pid]["name"])


def person_el(pid, personen, indent):
    kids = [E("persName", {"type": "preferred"}, personen[pid]["name"])]
    kids += [E("idno", {"type": t}, v) for t, v in personen[pid]["idnos"]]
    return einruecken(E("person", {XML_ID: pid, "corresp": f"persons.xml#{pid}"}, kids=kids), indent)


def category_el(genre, indent):
    kids = [E("gloss", {XML_LANG: lang}, text) for lang, text in genre["terme"]]
    return einruecken(E("category", {XML_ID: GENRE, "corresp": f"genres.xml#{GENRE}"}, kids=kids), indent)


def autorentext(pids, personen):
    return " und ".join(personen[p]["name"] for p in pids)


def setze_header(root, sigle, werktitel, pids, personen, genre, heute):
    """Setzt die Normdaten im Header, idempotent. -> Liste der geaenderten Felder (leer: nichts)."""
    h = root.find(q("teiHeader"))
    if h is None:
        raise bc.HarterFehler(f"{sigle}: kein teiHeader")
    geaendert = []

    def genau_eins(xpath, was):
        r = h.xpath(xpath, namespaces=NS)
        if len(r) != 1:
            raise bc.HarterFehler(f"{sigle}: {len(r)} x {was} statt 1")
        return r[0]

    # Titel: nur titleStmt/title bekommt den Werktitel. msName bleibt (Blattangabe, Druckdaten);
    # den Platzhalterzustand von 02 erkennt man daran, dass title und msName gleich lauten.
    ts = genau_eins(".//t:titleStmt", "titleStmt")
    titel = genau_eins("t:fileDesc/t:titleStmt/t:title", "titleStmt/title")
    msname = genau_eins(".//t:msIdentifier/t:msName", "msName")
    if titel.text != werktitel:
        if titel.text != msname.text:
            raise bc.HarterFehler(f"{sigle}: title {titel.text!r} != msName {msname.text!r}")
        titel.text = werktitel
        geaendert.append("Titel")

    # Autoren im titleStmt
    alte = ts.findall(q("author"))
    soll = [autor_el(p, personen, "#") for p in pids]
    ist_paare = [(a.get("ref"), a.text) for a in alte]
    soll_paare = [(s.get("ref"), s.text) for s in soll]
    if ist_paare != soll_paare:
        if ist_paare != [("#" + PERSON_ANONYM, personen[PERSON_ANONYM]["name"])]:
            raise bc.HarterFehler(f"{sigle}: unerwartete Autoren im titleStmt: {ist_paare}")
        ersetze_folge(ts, alte, soll, einzug(alte[0]))
        geaendert.append("Autoren")

    # msIdentifier und digitalIntermediary
    ident = genau_eins(".//t:msIdentifier", "msIdentifier")
    if ident.xpath("string(t:idno[@type='sigle'])", namespaces=NS) != sigle:
        raise bc.HarterFehler(f"{sigle}: idno sigle im msIdentifier weicht ab")
    soll_c = f"works.xml#work_{sigle}"
    if ident.get("corresp") != soll_c:
        if ident.get("corresp") != "works.xml#work_TBD":
            raise bc.HarterFehler(f"{sigle}: msIdentifier/@corresp {ident.get('corresp')!r} unerwartet")
        ident.set("corresp", soll_c)
        geaendert.append("msIdentifier")
    bibl = genau_eins(".//t:bibl[@type='digitalIntermediary']", "digitalIntermediary")
    if bibl.get(XML_ID) != f"{sigle}_brevitas_wiki":
        raise bc.HarterFehler(f"{sigle}: xml:id des digitalIntermediary {bibl.get(XML_ID)!r} unerwartet")
    soll_b = f"#{sigle}_{sigle}"  # wie WZB_WZB: xml:id des biblStruct im Werkeintrag
    if bibl.get("corresp") != soll_b:
        if bibl.get("corresp") != f"#{sigle}_TBD":
            raise bc.HarterFehler(f"{sigle}: digitalIntermediary/@corresp {bibl.get('corresp')!r} unerwartet")
        bibl.set("corresp", soll_b)
        geaendert.append("digitalIntermediary")

    # Gattung
    cat = genau_eins(".//t:taxonomy[@xml:id='genres']/t:category", "category in taxonomy genres")
    neu = category_el(genre, einzug(cat))
    if sig(cat) != sig(neu):
        if cat.get(XML_ID) != "genre_TBD":
            raise bc.HarterFehler(f"{sigle}: category {cat.get(XML_ID)!r} unerwartet")
        ersetze_folge(cat.getparent(), [cat], [neu], einzug(cat))
        geaendert.append("Gattung")

    # Personen im particDesc
    lp = genau_eins(".//t:particDesc/t:listPerson", "particDesc/listPerson")
    alte_p = lp.findall(q("person"))
    if not alte_p:
        raise bc.HarterFehler(f"{sigle}: listPerson ohne person")
    ind = einzug(alte_p[0])
    soll_p = [person_el(p, personen, ind) for p in pids]
    if [sig(p) for p in alte_p] != [sig(p) for p in soll_p]:
        if [sig(p) for p in alte_p] != [sig(person_el(PERSON_ANONYM, personen, ind))]:
            raise bc.HarterFehler(f"{sigle}: unerwartete Personen im particDesc")
        ersetze_folge(lp, alte_p, soll_p, ind)
        geaendert.append("Personen")

    # Aenderungszeile, einmal
    rd = genau_eins(".//t:revisionDesc", "revisionDesc")
    aenderungen = rd.findall(q("change"))
    if not aenderungen:
        raise bc.HarterFehler(f"{sigle}: revisionDesc ohne change")
    if not any((c.text or "").startswith(MARKE) for c in aenderungen):
        ch = E("change", {"when": heute, "who": "#mhdbdb-team"},
               f"{MARKE}, Entscheidung KZW vom 24.11.2026): Werk works.xml#work_{sigle}, Gattung "
               f"Weingruß ({GENRE}), Autor {autorentext(pids, personen)}, vorher Platzhalter und nur "
               f"Anonym. Setzt scripts/ingest/bre/23-normdaten.py, nur im Header.")
        letzte = aenderungen[-1]
        ch.tail = letzte.tail
        letzte.tail = "\n" + einzug(letzte)
        rd.insert(rd.index(letzte) + 1, ch)
        geaendert.append("Änderungszeile")
    return geaendert


# ---------------------------------------------------------------- Werkeintraege

def werk_el(sigle, werktitel, pids, personen, quelle_url, revision):
    seitentitel = revision["seitentitel"]
    datum = revision["timestamp"][:10]
    biblstruct = E("biblStruct", {"type": "web", XML_ID: f"{sigle}_{sigle}", "key": sigle}, kids=[
        E("monogr", kids=[
            E("author", kids=[E("name", text="Silvan Wagner")]),
            E("title", {"level": "m"}, f"Brevitas-Wiki, Hybridedition der Weingrüße: {seitentitel}"),
            E("idno", {"type": "url"}, quelle_url),
            E("imprint", kids=[E("date", text=datum)]),
        ]),
        E("note", text=f"Transkription von Silvan Wagner, Brevitas-Wiki (wiki.brevitas.org), Seite "
                       f"\"{seitentitel}\", Revision {revision['revid']} vom {datum}, "
                       f"CC BY-NC-SA 4.0."),
    ])
    kids = [E("title", {XML_LANG: "de"}, werktitel),
            E("idno", {"type": "sigle"}, sigle),
            E("ptr", {"target": f"genres.xml#{GENRE}"})]
    kids += [autor_el(p, personen, "persons.xml#") for p in pids]
    kids.append(E("relatedItem", kids=[biblstruct]))
    return E("bibl", {XML_ID: f"work_{sigle}"}, kids=kids)


def fragment_bauen(eintraege):
    wurzel = E("listBibl")
    wurzel.append(etree.Comment(
        " Werkeintraege der BRE-Zeugen (#147), erzeugt von scripts/ingest/bre/23-normdaten.py. "
        "Noch nicht in authority-files/works.xml: die Zeugen stehen noch nicht in tei/. "))
    for e in eintraege:
        wurzel.append(e)
    einruecken(wurzel, "")
    return etree.tostring(wurzel, encoding="UTF-8", xml_declaration=True) + b"\n"


def fragment_validieren(eintraege):
    """Setzt die Eintraege in eine Kopie von works.xml ein und validiert gegen das Authority-Schema."""
    works = etree.parse(str(WORKS))
    vorhanden = {b.get(XML_ID) for b in works.iter(q("bibl"))}
    doppelt = sorted(e.get(XML_ID) for e in eintraege if e.get(XML_ID) in vorhanden)
    if doppelt:
        raise bc.HarterFehler(f"schon in works.xml, das Fragment ist ueberholt: {doppelt}")
    listen = works.xpath("//t:listBibl", namespaces=NS)
    if len(listen) != 1:
        raise bc.HarterFehler(f"works.xml: {len(listen)} listBibl statt 1")
    import copy
    for e in eintraege:
        listen[0].append(copy.deepcopy(e))
    rng = etree.RelaxNG(etree.parse(str(SCHEMA_AUTHORITY)))
    if not rng.validate(works):
        raise bc.HarterFehler("Werkeintraege ungueltig gegen mhdbdb-authority.rng: "
                              + "; ".join(str(m) for m in list(rng.error_log)[:5]))


# ---------------------------------------------------------------- main

def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trocken", action="store_true", help="nichts schreiben")
    a = ap.parse_args()
    personen, genre = lade_normdaten()
    rows = ba.lies_tsv(bc.SEGMENTIERUNG)
    zeugen = {z["mhdbdb_sigle"]: z for z in ba.lies_tsv(ZEUGEN_TSV)}
    manifest = bc.lade_manifest()
    heute = datetime.date.today().isoformat()
    eintraege, geschrieben = [], 0
    for ed, pfad in ba.zeugen_dateien():  # (Editionssigle, Pfad)
        mh = bc.ZEUGEN[ed][1]
        baum = ba.lies(pfad)
        root = baum.getroot()
        if root.get(XML_ID) != mh:
            raise bc.HarterFehler(f"{pfad.name}: xml:id {root.get(XML_ID)!r} != {mh}")
        z = zeugen.get(mh)
        if not z or z["editionssigle"] != ed:
            raise bc.HarterFehler(f"{mh}: keine passende Zeile in zeugen.tsv")
        if not z["aufbewahrung"].strip() or not z["signatur"].strip():
            raise bc.HarterFehler(f"{mh}: aufbewahrung oder signatur leer in zeugen.tsv")
        werktitel = werktitel_von(z)
        pids, n_r, n, _ = autoren_des_zeugen(ed, root, rows, personen)
        geaendert = setze_header(root, mh, werktitel, pids, personen, genre, heute)
        ref = root.xpath(".//t:bibl[@type='digitalIntermediary']/t:ref/@target", namespaces=NS)
        if len(ref) != 1:
            raise bc.HarterFehler(f"{mh}: {len(ref)} ref/@target im digitalIntermediary statt 1")
        seitentitel = bc.transkriptions_titel(ed)
        rev = manifest.get(seitentitel)
        if not rev:
            raise bc.HarterFehler(f"{mh}: {seitentitel!r} nicht im Manifest")
        oldid = urllib.parse.parse_qs(urllib.parse.urlparse(ref[0]).query).get("oldid")
        if oldid != [str(rev["revid"])]:
            raise bc.HarterFehler(f"{mh}: oldid {oldid} im Header != Revision {rev['revid']} im Manifest")
        eintraege.append(werk_el(mh, werktitel, pids, personen, ref[0],
                                 {"seitentitel": seitentitel, "revid": rev["revid"],
                                  "timestamp": rev["timestamp"]}))
        if geaendert and not a.trocken:
            ba.schreibe(baum, pfad)
            geschrieben += 1
        print(f"{mh}: {werktitel} | Autor {autorentext(pids, personen)} | "
              f"{n_r} von {n} Texten nennen {personen[PERSON_ROSEN]['name']} | "
              f"geändert: {', '.join(geaendert) if geaendert else 'nichts'}")
    fragment_validieren(eintraege)
    neu = fragment_bauen(eintraege)
    alt = FRAGMENT.read_bytes() if FRAGMENT.exists() else None
    if neu != alt and not a.trocken:
        FRAGMENT.write_bytes(neu)
    print(f"Werkeintraege: {len(eintraege)}, gültig gegen mhdbdb-authority.rng, "
          f"{FRAGMENT.name} {'unverändert' if neu == alt else 'neu'}")
    print(f"{geschrieben} von {len(eintraege)} Dateien geschrieben"
          + (" (trocken: nichts geschrieben)" if a.trocken else ""))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
