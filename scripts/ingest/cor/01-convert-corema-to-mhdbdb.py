#!/usr/bin/env python3
"""01-convert-corema-to-mhdbdb.py: Stufe 0 fuer den CoReMA-Pilot (COR, #139).

Konvertiert die Rezeptebene ("annotated", normalisierter Lesetext mit
semantischer Annotation) von Bs1, GR1, M11 und W1 aus dem lokalen
CoReMA-Datenrepository in das MHDBDB-Schema: ingest/cor/<SIGLE>.tei.xml.
Die Quelle wird nicht veraendert und nicht ins Repository kopiert.

Mechanisch, ohne Eingriff in Wortgrenzen:
  Leerraum trennt <w>; allein stehende oder angehaengte . , : ; ! ? " / werden
  <pc> (join="left", am Einheitsanfang und bei fuehrendem " join="right");
  <ab> = <div type="recipe"> (ab/@type == recipe) bzw. <div type="section">
  (household, kitchenTip, medicinal, ...), verschachtelte <ab> als verschachteltes
  <div>; ein Titel am Rezeptanfang = <head>; <pb n> = <pb n>; Titel, Einleitung
  (seg ana=intro/close) und Datumszeile auf Ebene des aeusseren <div> = <head>
  bzw. <ab type>; <note xml:lang> = <note type="editorial" xml:lang>, nicht
  tokenisiert; <foreign xml:lang> setzt @xml:lang an den <w>.
Die semantische Auszeichnung (ingredient, tool, dish, instruction, opener, closer,
alternative, kitchenTip, servingTip, householdTip, time, dietetics, religion, name,
ref, date, sp, foreign, unclear, title, ab) hat im Schema keinen Platz. Sie bleibt
verlustfrei in ingest/cor/<SIGLE>.annotationen.tsv, verankert an den xml:id der
<w>/<pc>. Ein Element oder Attribut ausserhalb der Tabellen unten ist ein harter
Fehler, kein stilles Ueberspringen.

Validiert wird gegen schema/mhdbdb.rng (im Speicher und nach dem Schreiben aus
der Datei). Exit 1 bei Quellfehler, fehlgeschlagener Gegenprobe oder Schemafehler.

Aufruf (--corema-dir: Wurzel des Repositoriums corema, Vorgabe ../corema):
  python -P -E scripts/ingest/cor/01-convert-corema-to-mhdbdb.py --buch m11 --corema-dir <pfad>
  python -P -E scripts/ingest/cor/01-convert-corema-to-mhdbdb.py --buch alle --corema-dir <pfad> --trocken
"""
import argparse
import bisect
import collections
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from lxml import etree

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"
REPO = Path(__file__).resolve().parents[3]
SCHEMA_RNG = REPO / "schema" / "mhdbdb.rng"
INGEST_DIR = REPO / "ingest" / "cor"

# Editionssigle -> MHDBDB-Sigle (Entscheidung chsteiner 05.11.2026, #139)
BUECHER = {"bs1": "COR_BS1", "gr1": "COR_GR1", "m11": "COR_M11", "w1": "COR_W1"}

# Elemente, die zu einer Zeile in annotationen.tsv werden (Text bleibt im Fluss).
# Wert: erlaubte Attribute (lokale Namen; xml:lang als "xml:lang").
SPAN_ATTRS = {
    "ingredient": {"commodity", "en", "ana"},
    "tool": {"commodity", "en", "ana"},
    "dish": {"commodity", "en", "ana"},
    "instruction": set(),
    "opener": set(),
    "closer": set(),
    "alternative": {"reason"},
    "kitchenTip": set(),
    "servingTip": {"ana"},
    "householdTip": set(),
    "time": set(),
    "dietetics": set(),
    "religion": set(),
    "name": set(),
    "ref": {"target"},
    "date": set(),
    "sp": {"ana"},
    "foreign": {"xml:lang"},
    "unclear": set(),
    "title": {"key", "type", "ana", "corresp"},
}
# Spans, deren Text in die Tabelle kommt (kurze Begriffe); bei den uebrigen
# genuegen von/bis, der Text steht in der TEI.
TEXT_IM_TSV = {"ingredient", "tool", "dish", "name", "ref", "date", "religion",
               "title", "unclear", "time", "dietetics"}
AB_ATTRS = {"n", "xml:id", "xml:lang", "type", "subtype"}
PB_ATTRS = {"n", "xml:id"}
NOTE_ATTRS = {"xml:lang"}
DIV_KINDER = {"pb", "note", "title", "seg", "dateline", "ab"}
SEG_ATTRS = {"ana"}
SEG_TYPEN = {"intro", "close"}

PUNKT_ALLEIN = set('.,:;!?"/')
PUNKT_ENDE = '.,:;!?"'
PUNKT_ANFANG = '"'
NCNAME_TEIL = re.compile(r"^[A-Za-z0-9._-]+$")

TSV_SPALTEN = ["einheit", "art", "von", "bis", "n_w", "attribute", "text"]


class HarterFehler(Exception):
    pass


def q(tag):
    return f"{{{TEI_NS}}}{tag}"


def lokal(el):
    qn = etree.QName(el)
    if qn.namespace != TEI_NS:
        raise HarterFehler(f"Element ausserhalb des TEI-Namensraums: {el.tag}")
    return qn.localname


def attr_name(k):
    qn = etree.QName(k)
    if qn.namespace == XML_NS:
        return "xml:" + qn.localname
    if qn.namespace is None:
        return qn.localname
    raise HarterFehler(f"Attribut in fremdem Namensraum: {k}")


def pruefe_attribute(el, erlaubt, ctx=""):
    name = lokal(el)
    for k in el.attrib:
        a = attr_name(k)
        if a not in erlaubt:
            raise HarterFehler(f"<{name}> hat unbekanntes Attribut {a!r}{ctx}")


def kollabiere(s):
    return re.sub(r"\s+", " ", s).strip()


# ------------------------------------------------------------------ Lauf


class Run:
    """Zusammenhaengender Textfluss einer Einheit (ohne Notizen, ohne Unter-<ab>)."""

    def __init__(self):
        self.teile = []
        self.laenge = 0
        self.events = []  # (offset, art, nutzlast, folge)
        self.spans = []  # dict(art, attribute, start, ende)

    def add(self, s):
        self.teile.append(s)
        self.laenge += len(s)

    def event(self, art, nutzlast):
        self.events.append((self.laenge, art, nutzlast, len(self.events)))

    def text(self):
        return "".join(self.teile)


class Einheit:
    """Eine Quell-<ab> (Rezept oder Abschnitt) oder eine Einheit auf div-Ebene."""

    def __init__(self, form, quell_id, attribute, run, ab_el=None):
        self.form = form  # "ab" | "head" | "intro" | "dateline"
        self.quell_id = quell_id
        self.attribute = attribute
        self.run = run


def attribute_dict(el):
    return {attr_name(k): v for k, v in el.attrib.items()}


def laufe(el, run, einheit_id, zaehler):
    """Fuellt run mit dem Inhalt von el (Text, Kinder, Schwanztexte)."""
    if el.text:
        run.add(el.text)
    for ch in el:
        if not isinstance(ch.tag, str):
            zaehler["kommentar_oder_pi"] += 1
        else:
            kind(ch, run, einheit_id, zaehler)
        if ch.tail:
            run.add(ch.tail)


def kind(ch, run, einheit_id, zaehler):
    name = lokal(ch)
    if name == "pb":
        pruefe_attribute(ch, PB_ATTRS)
        n = ch.get("n")
        if not n or not NCNAME_TEIL.match(n):
            raise HarterFehler(f"<pb> ohne lesbares @n: {n!r}")
        if len(ch) or kollabiere(ch.text or ""):
            raise HarterFehler("<pb> mit Inhalt")
        run.event("pb", n)
    elif name == "note":
        pruefe_attribute(ch, NOTE_ATTRS)
        run.event("note", (ch.get(f"{{{XML_NS}}}lang"), kollabiere("".join(ch.itertext()))))
        zaehler["note"] += 1
    elif name == "ab":
        run.event("sub", baue_ab(ch, zaehler))
    elif name in SPAN_ATTRS:
        pruefe_attribute(ch, SPAN_ATTRS[name])
        start = run.laenge
        laufe(ch, run, einheit_id, zaehler)
        run.spans.append({"art": name, "attribute": attribute_dict(ch),
                          "start": start, "ende": run.laenge, "einheit": einheit_id})
        zaehler[f"span_{name}"] += 1
    else:
        raise HarterFehler(f"unbekanntes Element <{name}> im Rezepttext")


def baue_ab(ab, zaehler):
    pruefe_attribute(ab, AB_ATTRS)
    quell_id = ab.get(f"{{{XML_NS}}}id")
    if not quell_id:
        raise HarterFehler("<ab> ohne xml:id")
    run = Run()
    laufe(ab, run, quell_id, zaehler)
    zaehler["ab"] += 1
    return Einheit("ab", quell_id, attribute_dict(ab), run)


def baue_einheiten(body, zaehler):
    """-> Liste von ("pb", n) | ("note", (lang, text)) | ("einheit", Einheit)"""
    divs = [c for c in body if isinstance(c.tag, str)]
    if len(divs) != 1 or lokal(divs[0]) != "div":
        raise HarterFehler(f"body hat {len(divs)} Kinder statt genau einem <div>")
    div = divs[0]
    pruefe_attribute(div, set())
    if kollabiere(div.text or ""):
        raise HarterFehler("Text direkt im aeusseren <div>")
    liste = []
    for ch in div:
        if not isinstance(ch.tag, str):
            zaehler["kommentar_oder_pi"] += 1
        else:
            name = lokal(ch)
            if name not in DIV_KINDER:
                raise HarterFehler(f"unbekanntes Element <{name}> im aeusseren <div>")
            if name == "pb":
                run = Run()
                kind(ch, run, "-", zaehler)
                liste.append(("pb", run.events[0][2]))
            elif name == "note":
                run = Run()
                kind(ch, run, "-", zaehler)
                liste.append(("note", run.events[0][2]))
            elif name == "ab":
                liste.append(("einheit", baue_ab(ch, zaehler)))
            else:
                if name == "title":
                    pruefe_attribute(ch, SPAN_ATTRS["title"])
                elif name == "seg":
                    pruefe_attribute(ch, SEG_ATTRS)
                    if ch.get("ana") not in SEG_TYPEN:
                        raise HarterFehler(f"<seg ana={ch.get('ana')!r}> nicht vorgesehen")
                else:
                    pruefe_attribute(ch, set())
                run = Run()
                laufe(ch, run, "-", zaehler)
                if name == "title":
                    run.spans.append({"art": "title", "attribute": attribute_dict(ch),
                                      "start": 0, "ende": run.laenge, "einheit": "-"})
                    zaehler["span_title"] += 1
                    form = "head"
                elif name == "seg":
                    run.spans.append({"art": "seg", "attribute": attribute_dict(ch),
                                      "start": 0, "ende": run.laenge, "einheit": "-"})
                    zaehler["seg"] += 1
                    form = "intro"
                else:
                    zaehler["dateline"] += 1
                    form = "dateline"
                liste.append(("einheit", Einheit(form, "-", attribute_dict(ch), run)))
        if ch.tail and kollabiere(ch.tail):
            raise HarterFehler(f"Text zwischen den Kindern des aeusseren <div>: {ch.tail[:40]!r}")
    return liste


# ------------------------------------------------------------------ Tokens


def zerlege(s):
    """Text -> [(art, text, start, ende)], art in {"w", "pc"}; Zerlegung nach Leerraum."""
    out = []
    for m in re.finditer(r"\S+", s):
        t, b = m.group(), m.start()
        if all(c in PUNKT_ALLEIN for c in t):
            out.extend(("pc", c, b + i, b + i + 1) for i, c in enumerate(t))
            continue
        i = 0
        while i < len(t) and t[i] in PUNKT_ANFANG:
            out.append(("pc", t[i], b + i, b + i + 1))
            i += 1
        j = len(t)
        while j > i and t[j - 1] in PUNKT_ENDE:
            j -= 1
        out.append(("w", t[i:j], b + i, b + j))
        out.extend(("pc", t[k], b + k, b + k + 1) for k in range(j, len(t)))
    return out


class Zustand:
    def __init__(self, sigle):
        self.sigle = sigle
        self.folio = None
        self.zaehler = collections.Counter()  # je Folio-Bezeichnung
        self.stat = collections.Counter()
        self.zeilen = []  # Zeilen der annotationen.tsv
        self.texte = []  # emittierter Text in Dokumentreihenfolge
        self.verklebt = []  # (Einheit, Kontext) an Elementgrenzen ohne Leerraum
        self.pb_im_wort = []  # (Blatt, Kontext) fuer <pb> mitten im Wort

    def neue_id(self):
        f = self.folio if self.folio is not None else "0"
        self.zaehler[f] += 1
        return f"{self.sigle}_{f}_{self.zaehler[f]}"


def E(parent, tag, **attrs):
    el = etree.SubElement(parent, q(tag))
    for k, v in attrs.items():
        el.set(k, v)
    return el


def emittiere_lauf(run, einheit_id, wurzel_div, kopf_erlaubt, z, ab_zeile):
    """Schreibt den Lauf in wurzel_div. kopf_erlaubt: fuehrender Titel -> <head>."""
    s = run.text()
    units = zerlege(s)
    starts = [u[2] for u in units]
    ends = [u[3] for u in units]
    n = len(units)
    foreign = [sp for sp in run.spans if sp["art"] == "foreign"]

    # Elementgrenze ohne Leerraum zwischen zwei Zeichen: kein Eingriff in
    # Wortgrenzen, die Stelle wird nur gemeldet.
    gesehen = set()
    for sp in run.spans:
        for off in (sp["start"], sp["ende"]):
            if 0 < off < len(s) and off not in gesehen and s[off - 1].isalnum() and s[off].isalnum():
                gesehen.add(off)
                z.verklebt.append((einheit_id, s[max(0, off - 12):off] + "|" + s[off:off + 12]))

    # Fuehrender Titel -> head
    kopf = None
    if kopf_erlaubt:
        erstes_sub = min((e[0] for e in run.events if e[1] == "sub"), default=None)
        for sp in sorted((sp for sp in run.spans if sp["art"] == "title"), key=lambda x: x["start"]):
            if s[:sp["start"]].strip() == "" and sp["ende"] > sp["start"]:
                if erstes_sub is None or erstes_sub >= sp["ende"]:
                    ha = bisect.bisect_right(ends, sp["start"])
                    hb = bisect.bisect_left(starts, sp["ende"])
                    if hb > ha:
                        kopf = (sp["start"], sp["ende"], ha, hb)
            break

    # Ereignisse einsortieren
    slots = collections.defaultdict(list)
    for off, art, nutzlast, folge in sorted(run.events, key=lambda e: (e[0], e[3])):
        slot = bisect.bisect_left(starts, off)
        if slot > 0 and starts[slot - 1] < off < ends[slot - 1]:
            if art == "pb":
                z.stat["pb_im_wort"] += 1
                z.pb_im_wort.append((nutzlast, s[max(0, off - 12):off] + "|" + s[off:off + 12]))
        if kopf is None:
            gruppe = "body"
        elif off <= kopf[0]:
            gruppe = "pre"
        elif off < kopf[1]:
            gruppe = "head"
        else:
            gruppe = "body"
        if art == "sub" and gruppe != "body":
            raise HarterFehler("verschachtelte <ab> im Titel")
        slots[slot].append((gruppe, art, nutzlast))

    folge = []
    for i in range(n + 1):
        folge.extend(("ev",) + e for e in slots[i])
        if i < n:
            folge.append(("tok", i))

    zustand = {"p": None, "head": None}
    ids = [None] * n

    def container(gruppe):
        if gruppe == "pre" or not kopf_erlaubt:
            return wurzel_div
        if gruppe == "head":
            if zustand["head"] is None:
                zustand["head"] = E(wurzel_div, "head")
            return zustand["head"]
        if zustand["p"] is None:
            zustand["p"] = E(wurzel_div, "p")
        return zustand["p"]

    erste = True
    for item in folge:
        if item[0] == "tok":
            i = item[1]
            if kopf is not None and kopf[2] <= i < kopf[3]:
                gruppe = "head"
            else:
                gruppe = "body"
            cont = container(gruppe)
            art, text, b, e = units[i]
            xid = z.neue_id()
            ids[i] = xid
            if art == "w":
                el = E(cont, "w")
                el.set(f"{{{XML_NS}}}id", xid)
                if any(sp["start"] < e and sp["ende"] > b for sp in foreign):
                    lang = [sp["attribute"].get("xml:lang") for sp in foreign
                            if sp["start"] < e and sp["ende"] > b]
                    if len(set(lang)) != 1:
                        raise HarterFehler(f"widerspruechliche foreign-Sprachen am Wort {text!r}")
                    el.set(f"{{{XML_NS}}}lang", lang[0])
                    z.stat["w_foreign"] += 1
                el.text = text
                z.stat["w"] += 1
            else:
                el = E(cont, "pc")
                el.set(f"{{{XML_NS}}}id", xid)
                if erste or (text in PUNKT_ANFANG and (i == 0 or ends[i - 1] < b)):
                    el.set("join", "right")
                else:
                    el.set("join", "left")
                el.text = text
                z.stat["pc"] += 1
            z.texte.append(text)
            erste = False
        else:
            _, gruppe, art, nutzlast = item
            if art == "pb":
                E(container(gruppe), "pb", n=nutzlast)
                z.folio = nutzlast
                z.stat["pb"] += 1
            elif art == "note":
                schreibe_note(container(gruppe), nutzlast, z)
            else:  # sub
                zustand["p"] = None
                emittiere_ab(nutzlast, wurzel_div, z)

    # Zeilen fuer die Tabelle (nach der Vergabe der IDs)
    def von_bis(start, ende):
        a = bisect.bisect_right(ends, start)
        b = bisect.bisect_left(starts, ende) - 1
        if b < a:
            return "", "", 0
        nw = sum(1 for k in range(a, b + 1) if units[k][0] == "w")
        return ids[a], ids[b], nw

    if ab_zeile is not None:
        v, b, nw = von_bis(0, len(s))
        ab_zeile.update(von=v, bis=b, n_w=nw)
    for sp in sorted(run.spans, key=lambda x: (x["start"], -x["ende"], x["art"])):
        v, b, nw = von_bis(sp["start"], sp["ende"])
        text = kollabiere(s[sp["start"]:sp["ende"]]) if sp["art"] in TEXT_IM_TSV else ""
        z.zeilen.append({"einheit": sp["einheit"], "art": sp["art"], "von": v, "bis": b,
                         "n_w": nw, "attribute": attr_text(sp["attribute"]), "text": text})


def schreibe_note(parent, nutzlast, z):
    """Editorische Notiz der Quelle. <note> hat im Schema kein @xml:lang, die
    Sprache steht darum im @type (editorial-de, editorial-en)."""
    lang, text = nutzlast
    el = E(parent, "note", type=f"editorial-{lang}" if lang else "editorial")
    el.text = text
    z.stat["note"] += 1


def attr_text(d):
    return " | ".join(f"{k}={kollabiere(v)}" for k, v in d.items())


def emittiere_ab(e, eltern_div, z):
    typ = "recipe" if e.attribute.get("type") == "recipe" else "section"
    div = E(eltern_div, "div", type=typ)
    if e.attribute.get("n"):
        div.set("n", e.attribute["n"])
    zeile = {"einheit": e.quell_id, "art": "ab", "von": "", "bis": "", "n_w": 0,
             "attribute": attr_text(e.attribute), "text": ""}
    z.zeilen.append(zeile)
    z.stat["div_" + typ] += 1
    emittiere_lauf(e.run, e.quell_id, div, True, z, zeile)


def baue_body(einheiten, z):
    body = etree.Element(q("body"))
    aussen = E(body, "div")
    for art, nutz in einheiten:
        if art == "pb":
            E(aussen, "pb", n=nutz)
            z.folio = nutz
            z.stat["pb"] += 1
        elif art == "note":
            schreibe_note(aussen, nutz, z)
        else:
            e = nutz
            if e.form == "ab":
                emittiere_ab(e, aussen, z)
            else:
                if e.form == "head":
                    cont = E(aussen, "head")
                    z.stat["head_aussen"] += 1
                else:
                    cont = E(aussen, "ab", type=e.form if e.form != "intro" else e.attribute["ana"])
                    z.stat["ab_" + cont.get("type")] += 1
                wrapper = cont
                emittiere_lauf(e.run, "-", wrapper, False, z, None)
    return body


# ------------------------------------------------------------------ Kopf

HEADER_TEMPLATE = """<teiHeader xmlns="http://www.tei-c.org/ns/1.0">
    <fileDesc>
      <titleStmt>
        <title xml:lang="de">{title_de}</title>
        <author ref="#person_anonym">Anonym</author>
        <respStmt>
          <resp>digitale Zusammenführung, Annotation und semantische Klassifikation</resp>
          <orgName ref="contributors.xml#mhdbdb-team">MHDBDB-Team (vollständige Liste in contributors.xml)</orgName>
        </respStmt>
{resp_extra}      </titleStmt>
      <publicationStmt>
        <publisher>
          <orgName>Mittelhochdeutsche Begriffsdatenbank (MHDBDB)</orgName>
          <orgName>Paris Lodron Universität Salzburg</orgName>
          <address>
            <street>Erzabt-Klotz-Straße 1</street>
            <postCode>5020</postCode>
            <settlement>Salzburg</settlement>
            <country>Österreich</country>
          </address>
          <email>mhdbdb@plus.ac.at</email>
          <ptr target="https://mhdbdb.plus.ac.at"/>
        </publisher>
        <authority>
          <persName role="coordinator" ref="contributors.xml#contrib_003">
            <forename>Katharina</forename>
            <surname>Zeppezauer-Wachauer</surname>
          </persName>
          <persName role="founder" ref="contributors.xml#contrib_001">
            <forename>Klaus M.</forename>
            <surname>Schmidt</surname>
          </persName>
          <persName role="founder" ref="contributors.xml#contrib_002">
            <forename>Horst</forename>
            <surname>Pütz</surname>
          </persName>
        </authority>
        <availability>
          <licence target="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</licence>
          <p>Textdaten der Quelle (CoReMA, ZIM-ACDH Universität Graz) unter CC BY 4.0, Namensnennung erforderlich. Faksimiles der Quelle sind nicht übernommen. Förderhinweis der Quelle: {funder}.</p>
        </availability>
        <date when="2026">2026</date>
      </publicationStmt>
      <sourceDesc>
        <msDesc>
          <msIdentifier corresp="works.xml#work_TBD">
            <idno type="sigle">{sigle}</idno>
            <msName xml:lang="de">{title_de}</msName>
          </msIdentifier>
          <additional>
            <listBibl>
              <bibl type="digitalIntermediary" xml:id="{sigle}_corema_gams" corresp="#{sigle}_TBD">
                <title>CoReMA. Cooking Recipes of the Middle Ages (ZIM-ACDH, Universität Graz)</title>
                <respStmt>
                  <resp>Elektronische Bereitstellung, Transkription und semantische Annotation</resp>
                  <name>CoReMA-Projekt, Graz (Hg. Helmut W. Klug)</name>
                </respStmt>
                <ref target="{source_url}"/>
                <note type="provenance">Rezeptebene (normalisierter Lesetext mit semantischer Annotation) aus dem CoReMA-Datenrepository, Datei {quelldatei}, sha256 {sha256}. Konvertiert in das MHDBDB-Schema durch automatische Transformation (scripts/ingest/cor/01-convert-corema-to-mhdbdb.py, {heute}).</note>
                <note type="fidelity">Mechanische Konversion ohne Eingriff in Wortgrenzen. Die semantische Auszeichnung der Quelle (Zutaten, Werkzeuge, Gerichte, Handlungsanweisungen u. a.) steht verlustfrei in ingest/cor/{sigle}.annotationen.tsv, verankert an den xml:id der Wörter.</note>
              </bibl>
            </listBibl>
          </additional>
        </msDesc>
      </sourceDesc>
    </fileDesc>
    <encodingDesc>
      <projectDesc>
        <p xml:lang="de">Die Annotationen der MHDBDB basieren auf kontrollierten Vokabularen und domänenspezifischen Ontologien.</p>
        <p xml:lang="en">The annotations of the MHDBDB are based on controlled vocabularies and domain-specific ontologies.</p>
      </projectDesc>
      <editorialDecl>
        <p xml:lang="de">Lokale Dateireferenzen (z.B. persons.xml#person_anonym, lexicon.xml#lemma_879) verweisen auf kontrollierte Vokabulare im authority-files Verzeichnis dieses Repositorys.</p>
      </editorialDecl>
      <classDecl>
        <taxonomy xml:id="genres">
          <bibl>Genreklassifikation gemäß der Textreihentypologie <ptr target="https://www.mhdbdb.sbg.ac.at/textreihen"/></bibl>
          <category xml:id="genre_TBD" corresp="genres.xml#genre_TBD">
            <gloss xml:lang="de">Kochbuch (TBD: konkrete Genre-ID)</gloss>
          </category>
        </taxonomy>
      </classDecl>
    </encodingDesc>
    <profileDesc>
      <langUsage>
        <language ident="TBD">TBD (Sprachstufe offen; Quelle: {sprache})</language>
      </langUsage>
      <particDesc>
        <listPerson>
          <person xml:id="person_anonym" corresp="persons.xml#person_anonym">
            <persName type="preferred">Anonym</persName>
          </person>
        </listPerson>
      </particDesc>
    </profileDesc>
    <revisionDesc>
      <change when="{heute}" who="#mhdbdb-team">Initiale Konversion aus dem CoReMA-Datenrepository (Rezeptebene {pid}) via scripts/ingest/cor/01-convert-corema-to-mhdbdb.py.</change>
    </revisionDesc>
  </teiHeader>"""


def xp(root, pfad):
    return root.xpath(pfad, namespaces={"t": TEI_NS})


def erstes(root, pfad):
    r = xp(root, pfad)
    if not r:
        return ""
    v = r[0]
    return kollabiere(v if isinstance(v, str) else "".join(v.itertext()))


def quell_meta(root):
    ms = "//t:sourceDesc/t:msDesc/t:msIdentifier"
    meta = {
        "land": erstes(root, ms + "/t:country"),
        "ort": erstes(root, ms + "/t:settlement"),
        "institution": erstes(root, ms + "/t:institution"),
        "signatur": erstes(root, ms + "/t:idno"),
        "msname": erstes(root, ms + "/t:msName"),
        "kurzsigle": erstes(root, ms + "/t:altIdentifier/t:idno"),
        "pid": erstes(root, "//t:publicationStmt/t:idno[@type='PID']"),
        "datierung": erstes(root, "//t:sourceDesc//t:origDate/t:date[@xml:lang='de']"),
        "sprache": erstes(root, "//t:msContents/t:textLang/t:lang[@ana='main']"),
        "editor": " ".join(x for x in (erstes(root, "//t:editionStmt/t:editor/t:forename"),
                                       erstes(root, "//t:editionStmt/t:editor/t:surname")) if x),
        "principal": " ".join(x for x in (erstes(root, "//t:editionStmt/t:principal/t:forename"),
                                          erstes(root, "//t:editionStmt/t:principal/t:surname")) if x),
        "funder": "; ".join(kollabiere("".join(f.itertext()))
                            for f in xp(root, "//t:editionStmt/t:funder")),
    }
    if not meta["signatur"] or not meta["pid"]:
        raise HarterFehler("msIdentifier/idno oder PID fehlt in der Quelle")
    return meta


def baue_kopf(sigle, meta, quelldatei, sha, heute):
    titel = ", ".join(x for x in (meta["ort"], meta["institution"], meta["signatur"]) if x)
    resp = ""
    if meta["editor"]:
        resp += (f"        <respStmt>\n          <resp>Transkription und Rezeptedition der Quelle</resp>\n"
                 f"          <name>{escape(meta['editor'])}</name>\n        </respStmt>\n")
    if meta["principal"]:
        resp += (f"        <respStmt>\n          <resp>Projektleitung der Quelle (CoReMA)</resp>\n"
                 f"          <name>{escape(meta['principal'])}</name>\n        </respStmt>\n")
    attr = lambda s: escape(s, {'"': "&quot;"})  # noqa: E731
    return etree.fromstring(HEADER_TEMPLATE.format(
        sigle=sigle, title_de=escape(titel), resp_extra=resp,
        funder=escape(meta["funder"] or "nicht angegeben"),
        source_url=attr(f"https://gams.uni-graz.at/{meta['pid']}"),
        quelldatei=escape(quelldatei), sha256=sha, heute=heute,
        sprache=escape(meta["sprache"] or "nicht angegeben"), pid=escape(meta["pid"]))), titel


# ------------------------------------------------------------------ Pruefung


def schema_pruefen(tei, rng):
    ok = rng.validate(etree.ElementTree(tei))
    return ok, [f"Zeile {e.line}: {e.message}" for e in list(rng.error_log)[:5]]


def zaehle_quelle(body):
    c = collections.Counter(lokal(e) for e in body.iter() if isinstance(e.tag, str)
                            and not any(a.tag == q("note") for a in e.iterancestors()))
    return c


def konvertiere(buch, corema_dir, ausgabe_dir, trocken, heute, rng):
    sigle = BUECHER[buch]
    rel = f"data/published/annotated/{buch}.recipes.xml"
    quelle = corema_dir / rel
    if not quelle.is_file():
        raise HarterFehler(f"Quelle fehlt: {quelle}")
    roh = quelle.read_bytes()
    sha = hashlib.sha256(roh).hexdigest()
    wurzel = etree.fromstring(roh, etree.XMLParser(remove_blank_text=False))
    meta = quell_meta(wurzel)
    body_q = wurzel.find(f".//{q('body')}")
    if body_q is None:
        raise HarterFehler("kein <body>")
    quell_zaehler = zaehle_quelle(body_q)

    zaehler = collections.Counter()
    einheiten = baue_einheiten(body_q, zaehler)
    z = Zustand(sigle)
    body = baue_body(einheiten, z)

    header, titel = baue_kopf(sigle, meta, rel, sha, heute)
    tei = etree.Element(q("TEI"), nsmap={None: TEI_NS})
    tei.set(f"{{{XML_NS}}}id", sigle)
    tei.append(header)
    text = E(tei, "text")
    text.append(body)
    etree.indent(tei, space="  ")

    # Gegenproben
    probleme = []
    ids = tei.xpath("//t:w/@xml:id | //t:pc/@xml:id", namespaces={"t": TEI_NS})
    dup = [k for k, c in collections.Counter(ids).items() if c > 1]
    if dup:
        probleme.append(f"{len(dup)} doppelte xml:id, z.B. {dup[:5]}")
    erwartet = "".join(re.sub(r"\s+", "", t) for t in
                       body_q.xpath(".//text()[not(ancestor::t:note)]", namespaces={"t": TEI_NS}))
    erzeugt = "".join(re.sub(r"\s+", "", t) for t in z.texte)
    if erwartet != erzeugt:
        d = next((i for i, (a, b) in enumerate(zip(erwartet, erzeugt)) if a != b),
                 min(len(erwartet), len(erzeugt)))
        probleme.append(f"Zeichenrundlauf: {len(erwartet)} Zeichen Quelle, {len(erzeugt)} in w/pc, "
                        f"erste Abweichung bei {d}: {erwartet[d - 10:d + 10]!r} gegen {erzeugt[d - 10:d + 10]!r}")
    n_div = len(tei.xpath("//t:div[@type]", namespaces={"t": TEI_NS}))
    if n_div != zaehler["ab"]:
        probleme.append(f"{n_div} <div type> gegen {zaehler['ab']} verarbeitete <ab>")
    if zaehler["ab"] != quell_zaehler["ab"]:
        probleme.append(f"{zaehler['ab']} <ab> verarbeitet gegen {quell_zaehler['ab']} in der Quelle")
    n_pb = len(tei.xpath("//t:pb", namespaces={"t": TEI_NS}))
    if n_pb != quell_zaehler["pb"]:
        probleme.append(f"{n_pb} <pb> gegen {quell_zaehler['pb']} in der Quelle")
    n_note = len(tei.xpath("//t:text//t:note", namespaces={"t": TEI_NS}))
    if n_note != quell_zaehler["note"]:
        probleme.append(f"{n_note} <note> gegen {quell_zaehler['note']} in der Quelle")
    je_art = collections.Counter(r["art"] for r in z.zeilen)
    for art in list(SPAN_ATTRS) + ["seg", "ab"]:
        soll = quell_zaehler[art]
        if je_art[art] != soll:
            probleme.append(f"Tabelle: {je_art[art]} Zeilen {art} gegen {soll} Elemente in der Quelle")
    quell_dateline = quell_zaehler["dateline"]
    n_dateline = len(tei.xpath("//t:ab[@type='dateline']", namespaces={"t": TEI_NS}))
    if n_dateline != quell_dateline:
        probleme.append(f"{n_dateline} Datumszeilen gegen {quell_dateline}")
    ok, fehler = schema_pruefen(tei, rng)

    pfad = ausgabe_dir / f"{sigle}.tei.xml"
    tsv = ausgabe_dir / f"{sigle}.annotationen.tsv"
    ok_datei = None
    if not trocken and not probleme:
        pi1 = etree.ProcessingInstruction(
            "xml-model", 'href="../schema/mhdbdb.rng" type="application/xml" '
                         'schematypens="http://relaxng.org/ns/structure/1.0"')
        pi2 = etree.ProcessingInstruction(
            "xml-model", 'href="https://tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng"')
        tei.addprevious(pi1)
        tei.addprevious(pi2)
        ausgabe_dir.mkdir(parents=True, exist_ok=True)
        etree.ElementTree(tei).write(str(pfad), encoding="UTF-8", xml_declaration=True)
        schreibe_tsv(tsv, z.zeilen)
        ok_datei, _ = schema_pruefen(etree.parse(str(pfad)).getroot(), rng)

    n_w = z.stat["w"]
    ausgabe = collections.OrderedDict()
    print(f"== {buch} -> {sigle}  [{meta['pid']}, {quelle.stat().st_size} Bytes, sha256 {sha[:12]}]")
    print(f"Titel: {titel}; Sprache laut Quelle: {meta['sprache'] or '-'}; Datierung: {meta['datierung'] or '-'}")
    print(f"Woerter: {n_w} <w> (davon {z.stat['w_foreign']} mit @xml:lang), {z.stat['pc']} <pc>; "
          f"{z.stat['pb']} <pb> (davon {z.stat['pb_im_wort']} im Wort, hinter das Wort gestellt); "
          f"{z.stat['note']} <note>")
    for blatt, k in z.pb_im_wort:
        print(f"  <pb n={blatt!r}> im Wort: {k!r}")
    print(f"Einheiten: {z.stat['div_recipe']} <div type=recipe> + {z.stat['div_section']} "
          f"<div type=section> = {zaehler['ab']} <ab>; <head> aussen {z.stat['head_aussen']}, "
          f"<ab type=intro/close/dateline> {z.stat['ab_intro'] + z.stat['ab_close'] + z.stat['ab_dateline']}; "
          f"Kommentare/PI uebersprungen: {zaehler['kommentar_oder_pi']}")
    print(f"Elementgrenzen ohne Leerraum zwischen zwei Zeichen (kein Trenner eingefuegt): {len(z.verklebt)}"
          + "".join(f"\n  {e}: {k!r}" for e, k in z.verklebt))
    print(f"Tabelle: {len(z.zeilen)} Zeilen: " + ", ".join(f"{k}={v}" for k, v in sorted(je_art.items())))
    print(f"Schema (im Speicher): {'valide' if ok else 'NICHT valide'}"
          + (f"; Datei nach dem Schreiben: {'valide' if ok_datei else 'NICHT valide'}"
             if ok_datei is not None else ""))
    for f in fehler:
        print("  " + f)
    if probleme:
        raise HarterFehler("Gegenprobe fehlgeschlagen: " + "; ".join(probleme))
    print(f"Geschrieben: {pfad} und {tsv.name}" if not trocken else "(trocken: nichts geschrieben)")
    ausgabe.update(buch=buch, sigle=sigle, w=n_w, pc=z.stat["pc"], valide=ok if ok_datei is None else ok_datei,
                   meta=meta, sha256=sha, quelldatei=rel, bytes=len(roh))
    return ausgabe


def schreibe_tsv(pfad, zeilen):
    def feld(v):
        v = str(v)
        if "\t" in v or "\n" in v or "\r" in v:
            raise HarterFehler(f"Tab oder Zeilenumbruch im TSV-Feld: {v[:40]!r}")
        return v

    zeilen_text = ["\t".join(TSV_SPALTEN)]
    for r in zeilen:
        zeilen_text.append("\t".join(feld(r[s]) for s in TSV_SPALTEN))
    pfad.write_text("\n".join(zeilen_text) + "\n", encoding="utf-8", newline="\n")


def schreibe_quellen(ausgabe_dir, ergebnisse):
    spalten = ["sigle", "buch", "signatur", "ort", "institution", "msname", "kurzsigle", "datierung",
               "sprache", "pid", "quelldatei", "bytes", "sha256", "w", "pc"]
    zeilen = ["\t".join(spalten)]
    for e in ergebnisse:
        m = e["meta"]
        werte = [e["sigle"], e["buch"], m["signatur"], m["ort"], m["institution"], m["msname"],
                 m["kurzsigle"], m["datierung"], m["sprache"], m["pid"], e["quelldatei"], e["bytes"],
                 e["sha256"], e["w"], e["pc"]]
        zeilen.append("\t".join(str(w) for w in werte))
    (ausgabe_dir / "quellen.tsv").write_text("\n".join(zeilen) + "\n", encoding="utf-8", newline="\n")


def main():
    for strom in (sys.stdout, sys.stderr):
        strom.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--buch", required=True, help="bs1, gr1, m11, w1 oder alle")
    ap.add_argument("--corema-dir", type=Path, default=REPO.parent / "corema")
    ap.add_argument("--ausgabe-dir", type=Path, default=INGEST_DIR)
    ap.add_argument("--trocken", action="store_true", help="nichts schreiben")
    ap.add_argument("--datum", default=datetime.date.today().isoformat(),
                    help="Datum fuer revisionDesc, JJJJ-MM-TT (Vorgabe: heute)")
    a = ap.parse_args()
    try:
        datetime.date.fromisoformat(a.datum)
    except ValueError:
        ap.error(f"--datum {a.datum!r} ist kein JJJJ-MM-TT")
    if a.buch != "alle" and a.buch not in BUECHER:
        ap.error(f"--buch {a.buch!r} unbekannt")
    buecher = list(BUECHER) if a.buch == "alle" else [a.buch]
    rng = etree.RelaxNG(etree.parse(str(SCHEMA_RNG)))
    rc, ergebnisse = 0, []
    for b in buecher:
        try:
            ergebnisse.append(konvertiere(b, a.corema_dir, a.ausgabe_dir, a.trocken, a.datum, rng))
        except HarterFehler as e:
            print(f"FEHLER ({b}): {e}", file=sys.stderr)
            print(f"== {b}: HARTER FEHLER, siehe stderr")
            rc = 1
    if ergebnisse and not a.trocken and rc == 0 and a.buch == "alle":
        schreibe_quellen(a.ausgabe_dir, ergebnisse)
    if any(not e["valide"] for e in ergebnisse):
        rc = 1
    print("VERDICT: " + ("; ".join(f"{e['sigle']} {e['w']} w, {'valide' if e['valide'] else 'NICHT valide'}"
                                    for e in ergebnisse) or "KEIN ERGEBNIS"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
