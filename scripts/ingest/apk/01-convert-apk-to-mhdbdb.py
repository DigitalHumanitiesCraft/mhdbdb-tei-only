#!/usr/bin/env python3
"""01-convert-apk-to-mhdbdb.py: Stufe 0 der Hesler-Apokalypse (APK, #262).

Liest apk_free.xml (TEI.2 des Electronic Text Center, 2002, aus dem MHDBDB-Archiv; Fundort und
Pruefsumme in apk_common.py) und schreibt ingest/apk/APK.tei.xml im MHDBDB-Zielmodell,
validiert gegen schema/mhdbdb.rng. Abbildung und Begruendung je Element: README.md daneben.

Kurz:
  CSS-Block des Browser-Exports vor dem Doctype   entfaellt (geprueft: danach genau TEI.2)
  TEI.2-Header                                     neuer Header nach dem Muster tei/BIB.tei.xml
  front/titlePage                                  entfaellt (Titelblatt der Ausgabe, im Header)
  div1 / lg1                                       <div> (lg1 ist eine Huelle ohne Inhalt)
  lg2 (eingerueckter Abschnitt)                    <div type="section">
  l n="N" id="Apk-0000N"                           <l n="N"> (id ist eindeutig aus n ableitbar)
  head des lg1 (Rubrik)                            <head>, Woerter unannotiert
  pb n="N" (Seite der Ausgabe Helm)                <pb type="edition" n="N"/>
  milestone unit="column" (Spalte der Ausgabe)     entfaellt (Drucklayout, siehe README)
  fw type="folio" [1ra] (Blatt und Spalte der Hs.) <cb type="manuscript" n="1ra"/>
  hi rend="bold|superscript|doublespace"           <hi> mit demselben rend, im <w>
  hi ohne rend                                     <hi rend="italic"> (so zeigt es das MWB)
  orig reg="..." (Worttrennung am Druckzeilenende) ein <w>, Trennstrich und lb entfallen
  lb im Vers (Druckzeile)                          entfaellt
  corr resp="editor" sic="..."                     Lesart der Ausgabe im Text, sic als Kommentar
  Tokens                                           <w>/<pc>, xml:id APK_{Vers}_{Token}

Aufruf:
  python -P -E scripts/ingest/apk/01-convert-apk-to-mhdbdb.py [--quelle PFAD] [--trocken]
      [--datum JJJJ-MM-TT] [--ueberschreiben]
Eine Ausgabedatei, die schon @lemmaRef traegt, wird nur mit --ueberschreiben ersetzt.
"""
import argparse
import collections
import datetime
import re
import sys
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apk_common as ac  # noqa: E402

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"
XML_ID = f"{{{XML_NS}}}id"
SCHEMA = ac.REPO / "schema" / "mhdbdb.rng"
PUNKT = set(",.;:?!()")
PUNKT_RECHTS = {"("}
PI = ('<?xml-model href="../schema/mhdbdb.rng" type="application/xml" '
      'schematypens="http://relaxng.org/ns/structure/1.0"?>')

# Erwartete Bestaende der Quelle (gemessen 19.11.2026). Eine Abweichung heisst: das ist nicht
# die Datei, fuer die die Abbildung entschieden ist, und bricht ab.
SOLL = {"l": 23254, "lg2": 415, "pb": 342, "milestone": 684, "fw": 706, "orig": 309,
        "corr": 5, "lb": 867}  # Zaehlung im <body>; lb im Header und Titelblatt nicht
# Bekannte Elemente der Quelle. Ein anderes Element im <text> bricht ab.
TEXT_ELEMENTE = {"text", "front", "titlePage", "docAuthor", "docTitle", "titlePart",
                 "docEdition", "lb", "name", "byline", "docImprint", "pubPlace", "publisher",
                 "date", "body", "div1", "head", "pb", "lg1", "lg2", "l", "fw", "hi",
                 "milestone", "orig", "corr"}


def q(tag):
    return f"{{{TEI_NS}}}{tag}"


# ---------------------------------------------------------------- Quelle lesen

def quelle_parsen(daten, stat):
    """CSS-Block und Doctype entfernen, TEI.2 parsen. -> Wurzel (ohne Namespace)."""
    text = daten.decode("utf-8-sig")
    m = re.match(r'\s*<\?xml version="1\.0"\?>\s*(.*?)\s*<!DOCTYPE TEI\.2 SYSTEM "mhg-tei\.dtd">\s*', text, re.S)
    if not m:
        raise ac.HarterFehler("Prolog unerwartet: kein <?xml?> + Vorspann + <!DOCTYPE TEI.2>")
    vorspann = m.group(1)
    if not vorspann.startswith("@namespace html") or "<" in vorspann:
        raise ac.HarterFehler(f"Vorspann ist nicht der CSS-Block des Browser-Exports: {vorspann[:80]!r}")
    rest = text[m.end():]
    if not rest.startswith("<TEI.2>") or not rest.rstrip().endswith("</TEI.2>"):
        raise ac.HarterFehler("nach dem Vorspann steht nicht genau ein <TEI.2>...</TEI.2>")
    stat["css_zeichen"] = len(vorspann)
    wurzel = etree.fromstring(rest.encode("utf-8"))
    if wurzel.tag != "TEI.2":
        raise ac.HarterFehler(f"Wurzel {wurzel.tag}")
    return wurzel


def pruefe_bestand(wurzel, soll=SOLL):
    text = wurzel.find("text")
    fremd = {e.tag for e in text.iter() if isinstance(e.tag, str)} - TEXT_ELEMENTE
    if fremd:
        raise ac.HarterFehler(f"unbekannte Elemente im <text>: {sorted(fremd)}")
    body = text.find("body")
    ist = {t: sum(1 for _ in body.iter(t)) for t in soll}
    if ist != soll:
        raise ac.HarterFehler(f"Bestand weicht ab: {ist} != {soll}")
    if any(not isinstance(e.tag, str) for e in body.iter()):
        raise ac.HarterFehler("Kommentar oder PI im <body>")
    ns = [int(l.get("n")) for l in body.iter("l")]
    if ns != list(range(1, len(ns) + 1)):
        raise ac.HarterFehler("Verszaehlung nicht lueckenlos 1..N")
    for l in body.iter("l"):
        if l.get("id") != f"Apk-{int(l.get('n')):05d}":
            raise ac.HarterFehler(f"Vers-ID {l.get('id')} passt nicht zu n={l.get('n')}")
    return body


# ---------------------------------------------------------------- Atome einer Zeile

class Atome:
    """Zeichen mit Stil (Tupel der rend-Werte von aussen nach innen) und Marken."""

    def __init__(self):
        self.liste = []  # ("z", zeichen, stil) | ("cb", n) | ("lb",) | ("corr", sic)

    def text(self, s, stil):
        for ch in s or "":
            self.liste.append(("z", ch, stil))


def fw_n(fw):
    s = re.sub(r"\s+", "", "".join(fw.itertext()))
    if not (s.startswith("[") and s.endswith("]")):
        raise ac.HarterFehler(f"fw ohne eckige Klammern: {s!r}")
    return s[1:-1]


def sammle(el, stil, at, stat, protokoll):
    """Inhalt von el (ohne el.tail) als Atome."""
    at.text(el.text, stil)
    for k in el:
        if k.tag == "hi":
            rend = k.get("rend") or "italic"
            if k.get("rend") is None:
                stat["hi_ohne_rend"] += 1
            sammle(k, stil + (rend,), at, stat, protokoll)
        elif k.tag == "fw":
            if k.get("type") != "folio":
                raise ac.HarterFehler(f"fw type={k.get('type')}")
            at.liste.append(("cb", fw_n(k)))
            stat["fw"] += 1
        elif k.tag == "lb":
            at.liste.append(("lb",))
        elif k.tag == "orig":
            sub = Atome()
            sammle(k, stil, sub, stat, protokoll)
            verbunden = verbinde_trennung(sub.liste)
            form = "".join(a[1] for a in verbunden if a[0] == "z")
            reg = k.get("reg") or ""
            stat["orig"] += 1
            if form != reg:
                stat["orig_abweichend"] += 1
                protokoll.append(("orig", form, reg))
            at.liste.extend(verbunden)
        elif k.tag == "corr":
            if k.get("resp") != "editor" or k.get("sic") is None:
                raise ac.HarterFehler("corr ohne resp=editor oder sic")
            sammle(k, stil, at, stat, protokoll)
            at.liste.append(("corr", k.get("sic"), "".join(k.itertext())))
            stat["corr"] += 1
        else:
            raise ac.HarterFehler(f"unerwartetes Element {k.tag} in Zeile")
        at.text(k.tail, stil)


def verbinde_trennung(atome):
    """Trennstrich + Leerraum + <lb/> innerhalb von <orig> entfernen (genau einmal)."""
    for i, a in enumerate(atome):
        if a[0] == "lb":
            j = i - 1
            while j >= 0 and atome[j][0] == "z" and atome[j][1].isspace():
                j -= 1
            if j < 0 or atome[j][0] != "z" or atome[j][1] != "-":
                raise ac.HarterFehler("lb in orig ohne Trennstrich davor")
            k = i + 1
            while k < len(atome) and atome[k][0] == "z" and atome[k][1].isspace():
                k += 1
            return atome[:j] + atome[k:]
    raise ac.HarterFehler("orig ohne lb")


# ---------------------------------------------------------------- Tokens

def tokenisiere(atome, stat):
    """-> Liste von ("w", [(zeichen, stil)...]) | ("pc", zeichen, stil) | ("cb", n) | ("corr", sic, text)."""
    out, wort, marken = [], [], []

    def ende():
        # ein Strich am Wortrand ist ein Gedankenstrich, kein Wortteil (V. 12015 "-Da")
        vorn = []
        while wort and wort[0][0] == "-":
            vorn.append(("pc", "-", wort.pop(0)[1], "right"))
        hinten = []
        while wort and wort[-1][0] == "-":
            hinten.insert(0, ("pc", "-", wort.pop()[1]))
        stat["strich_als_pc"] += len(vorn) + len(hinten)
        out.extend(vorn)
        if wort:
            out.append(("w", list(wort)))
            wort.clear()
        out.extend(hinten)
        # corr-Marken, die waehrend des Worts kamen, stehen hinter ihm
        out.extend(marken)
        marken.clear()

    for i, a in enumerate(atome):
        if a[0] == "z":
            ch, stil = a[1], a[2]
            if ch.isspace():
                ende()
            elif ch in PUNKT:
                ende()
                out.append(("pc", ch, stil))
            else:
                if not (ch.isalpha() or ch == "-"):
                    raise ac.HarterFehler(f"unerwartetes Zeichen {ch!r}")
                if ch == "-":
                    stat["bindestrich_im_wort"] += 1
                wort.append((ch, stil))
        elif a[0] == "lb":
            # Druckzeilenwechsel ausserhalb von <orig>: zwischen Woertern ein Trenner,
            # mitten im Wort waere es eine unmarkierte Trennung (gezaehlt, dann verbunden)
            vor = atome[i - 1] if i else None
            nach = atome[i + 1] if i + 1 < len(atome) else None
            if (vor and vor[0] == "z" and not vor[1].isspace() and vor[1] not in PUNKT
                    and nach and nach[0] == "z" and not nach[1].isspace() and nach[1] not in PUNKT):
                stat["lb_im_wort"] += 1
            else:
                ende()
            stat["lb_vers"] += 1
        elif a[0] == "cb":
            ende()
            out.append(a)
        elif a[0] == "corr":
            # Marke hinter das Wort, in dem oder an dessen Ende die Korrektur steht; das Wort
            # laeuft weiter (engeli<corr sic="s"/>chen ist ein Wort)
            if wort:
                stat["corr_im_wort"] += 1
                marken.append(a)
            else:
                out.append(a)
    ende()
    return out


def inhalt(parent, zeichen):
    """Zeichen mit Stil als Mischinhalt in parent, Stile als verschachtelte <hi>."""
    gruppen = []
    for ch, stil in zeichen:
        if gruppen and gruppen[-1][1] == stil:
            gruppen[-1][0].append(ch)
        else:
            gruppen.append(([ch], stil))
    for chars, stil in gruppen:
        s = "".join(chars)
        if not stil:
            if len(parent):
                parent[-1].tail = (parent[-1].tail or "") + s
            else:
                parent.text = (parent.text or "") + s
            continue
        el = etree.SubElement(parent, q("hi"), rend=stil[0])
        innen = el
        for r in stil[1:]:
            innen = etree.SubElement(innen, q("hi"), rend=r)
        innen.text = s


def zeile_fuellen(ziel, tokens, praefix, stat):
    """Tokens als <w>/<pc>/<cb>/Kommentar in ziel; xml:id {praefix}_{i}."""
    i = 0
    for t in tokens:
        if t[0] == "w":
            w = etree.SubElement(ziel, q("w"))
            w.set(XML_ID, f"{praefix}_{i}")
            inhalt(w, t[1])
            i += 1
            stat["w"] += 1
        elif t[0] == "pc":
            ch, stil = t[1], t[2]
            join = t[3] if len(t) > 3 else ("right" if ch in PUNKT_RECHTS else "left")
            wirt = ziel
            if stil:
                wirt = etree.SubElement(ziel, q("hi"), rend=stil[0])
                for r in stil[1:]:
                    wirt = etree.SubElement(wirt, q("hi"), rend=r)
                stat["pc_mit_stil"] += 1
            pc = etree.SubElement(wirt, q("pc"), join=join)
            pc.set(XML_ID, f"{praefix}_{i}")
            pc.text = ch
            i += 1
            stat["pc"] += 1
        elif t[0] == "cb":
            etree.SubElement(ziel, q("cb"), type="manuscript", n=t[1])
            stat["cb"] += 1
        elif t[0] == "corr":
            _, sic, korr = t
            # die Auszeichnung der Vorlage woertlich; im Text steht der Inhalt von <corr>
            korr = re.sub(r"\s+", " ", korr)
            ziel.append(etree.Comment(f' apk_free.xml: <corr resp="editor" sic="{sic}">{korr}</corr> '))
    return i


# ---------------------------------------------------------------- Header

HEADER = """<teiHeader xmlns="http://www.tei-c.org/ns/1.0">
    <fileDesc>
      <titleStmt>
        <title xml:lang="de">Apokalypse</title>
        <title level="m">Die Apokalypse Heinrichs von Hesler aus der Danziger Handschrift</title>
        <title xml:lang="gmh" type="alternate" ana="historic">Dys ist Apokalipsis.</title>
        <author ref="#person_TBD">Heinrich von Hesler</author>
        <respStmt>
          <resp>digitale Zusammenführung, Annotation und semantische Klassifikation</resp>
          <orgName ref="contributors.xml#mhdbdb-team">MHDBDB-Team (vollständige Liste in contributors.xml)</orgName>
        </respStmt>
      </titleStmt>
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
          <p>Die semantischen Annotationen stehen unter der Lizenz CC BY-NC-SA 4.0. Die zugrunde liegenden E-Texte stammen aus unterschiedlichen Editionen und unterliegen je nach Quelle eigenen rechtlichen Bedingungen. Bitte beachten Sie die jeweiligen Angaben im Quellenverzeichnis.</p>
        </availability>
        <date when="{jahr}">{jahr}</date>
      </publicationStmt>
      <sourceDesc>
        <msDesc>
          <msIdentifier corresp="works.xml#work_TBD">
            <idno type="sigle">APK</idno>
            <idno type="mwb-sigle">HeslApk</idno>
            <msName xml:lang="de">Apokalypse</msName>
            <msName xml:lang="gmh">Dys ist Apokalipsis.</msName>
          </msIdentifier>
          <additional>
            <listBibl>
              <biblStruct type="book" xml:id="APK_APK" key="APK">
                <monogr>
                  <author>
                    <name>Heinrich von Hesler</name>
                  </author>
                  <title level="m">Die Apokalypse Heinrichs von Hesler aus der Danziger Handschrift</title>
                  <editor>
                    <forename>Karl</forename>
                    <surname>Helm</surname>
                  </editor>
                  <imprint>
                    <pubPlace>Berlin</pubPlace>
                    <publisher>Weidmann</publisher>
                    <date>1907</date>
                  </imprint>
                </monogr>
                <series>
                  <title level="s">Deutsche Texte des Mittelalters</title>
                  <biblScope unit="volume">8</biblScope>
                </series>
                <note>Die Apokalypse Heinrichs von Hesler. Aus der Danziger Handschrift hrsg. von Karl Helm (DTM 8. Dichtungen des Deutschen Ordens 1), Berlin: Weidmann 1907.</note>
              </biblStruct>
              <bibl type="digitalIntermediary" xml:id="APK_etext_mhgta" corresp="#APK_APK">
                <title>Elektronische Zwischenstufe (MHGTA)</title>
                <respStmt>
                  <resp>Projektleitung</resp>
                  <orgName>Akademie der Wissenschaften und der Literatur Mainz</orgName>
                </respStmt>
                <respStmt>
                  <resp>Digitale Erfassung</resp>
                  <orgName>Kompetenzzentrum Trier</orgName>
                </respStmt>
                <respStmt>
                  <resp>TEI-Auszeichnung</resp>
                  <orgName>Electronic Text Center, University of Virginia</orgName>
                </respStmt>
                <date when="2002">2002</date>
                <ref target="https://mhdwb-online.de/textarchiv.php"/>
                <note type="provenance">E-Text aus dem Mittelhochdeutschen Textarchiv (MHGTA), Kooperationsprojekt von Mainz, Trier und Virginia, im Textarchiv des Mittelhochdeutschen Wörterbuchs unter der Sigle HeslApk. Vorlage ist die TEI.2-Fassung des Electronic Text Center von 2002 (Revision September 2002: Lesley C. Pleasant und Cindy Filer Speer), Datei apk_free.xml aus dem MHDBDB-Archiv (SHA-256 {sha}). Konvertiert in das MHDBDB-Schema durch automatische Transformation (scripts/ingest/apk/01-convert-apk-to-mhdbdb.py, {heute}).</note>
                <note type="fidelity">Keine diplomatische Transkription der Druckedition. Abweichungen sind möglich. Die editorischen Beigaben der Ausgabe (Einleitung, Apparat, Glossar, sprachliche Analyse) fehlen. Seiten der Ausgabe als pb type="edition", Blatt und Spalte der Handschrift als cb type="manuscript". Worttrennungen am Druckzeilenende sind aufgehoben, die Druckzeilen und die Spalten der Ausgabe nicht übernommen.</note>
              </bibl>
            </listBibl>
          </additional>
        </msDesc>
      </sourceDesc>
    </fileDesc>
    <encodingDesc>
      <projectDesc>
        <p xml:lang="de">Die Annotationen der MHDBDB basieren auf kontrollierten Vokabularen und domänenspezifischen Ontologien. Hierzu zählen das auf SKOS strukturierte Begriffssystem mit semantischen Polyhierarchien, ein eigenständiges Onomastikon zur systematischen Erfassung von Eigennamen sowie eine umfassende Textreihentypologie mit über 600 Gattungsbezeichnungen. Diese Komponenten gewährleisten eine konsistente semantische Auszeichnung und fördern die Interoperabilität im Sinne der FAIR-Prinzipien.</p>
        <p xml:lang="en">The annotations of the MHDBDB are based on controlled vocabularies and domain-specific ontologies. These include a SKOS-structured conceptual system with semantic polyhierarchies, a dedicated onomasticon for the systematic encoding of proper names, and a comprehensive typology of text series encompassing more than 600 genre designations. These components ensure consistent semantic markup and promote interoperability in line with FAIR principles.</p>
      </projectDesc>
      <editorialDecl>
        <p xml:lang="de">Lokale Dateireferenzen (z.B. persons.xml#person_445, lexicon.xml#lemma_879, genres.xml#genre_XXX) verweisen auf kontrollierte Vokabulare im authority-files Verzeichnis dieses Repositorys. Diese internen Querverweise ermöglichen die Verknüpfung mit Personen-, Werk-, Lemma-, Konzept-, Genre- und Namensautoritätsdateien.</p>
        <p xml:lang="en">Local file references (e.g. persons.xml#person_445, lexicon.xml#lemma_879, genres.xml#genre_XXX) point to controlled vocabularies in the authority-files directory of this repository. These internal cross-references enable linking to person, work, lemma, concept, genre, and name authority files.</p>
        <p xml:lang="de">Gesperrt gesetzter Text (hi rend="doublespace") entspricht nach der Vorlage Bibelzitaten. Kursiv (hi rend="italic") steht, wo die Vorlage ein hi ohne rend trägt. Korrekturen (corr resp="editor") stehen mit ihrem Inhalt im Text, die Auszeichnung der Vorlage samt sic wörtlich als Kommentar dahinter.</p>
        <p xml:lang="de">Die Verse tragen nur @n. Die Vers-ID der Vorlage ist daraus ableitbar (n="1" entspricht id="Apk-00001", Muster Apk- und n fünfstellig mit führenden Nullen). Der Konverter prüft das für jeden Vers und bricht bei einer Abweichung ab.</p>
        <normalization>
          <p>Groß- und Kleinschreibung, Interpunktion und Verszählung folgen der Ausgabe in der Fassung des MHGTA.</p>
          <p>Noch nicht lemmatisiert und disambiguiert.</p>
        </normalization>
      </editorialDecl>
      <classDecl>
        <taxonomy xml:id="genres">
          <bibl>Genreklassifikation gemäß der Textreihentypologie <ptr target="https://www.mhdbdb.sbg.ac.at/textreihen"/></bibl>
          <category xml:id="genre_TBD" corresp="genres.xml#genre_TBD">
            <gloss xml:lang="de">TBD (Vorschlag in ingest/apk/normdaten-vorschlag.md)</gloss>
          </category>
        </taxonomy>
      </classDecl>
    </encodingDesc>
    <profileDesc>
      <langUsage>
        <language ident="gmh">Mittelhochdeutsch</language>
      </langUsage>
      <particDesc>
        <listPerson>
          <person xml:id="person_TBD" corresp="persons.xml#person_TBD">
            <persName type="preferred">Heinrich von Hesler</persName>
          </person>
        </listPerson>
      </particDesc>
    </profileDesc>
    <revisionDesc>
      <change when="{heute}" who="#mhdbdb-team">#262: Initiale Konversion aus apk_free.xml (TEI.2, Electronic Text Center 2002) via scripts/ingest/apk/01-convert-apk-to-mhdbdb.py.</change>
    </revisionDesc>
  </teiHeader>"""


# ---------------------------------------------------------------- Aufbau

def baue(body_q, sha, heute, stat, protokoll):
    tei = etree.Element(q("TEI"), nsmap={None: TEI_NS})
    tei.set(XML_ID, ac.SIGLE)
    tei.append(etree.fromstring(HEADER.replace("{jahr}", heute[:4]).replace("{heute}", heute)
                                .replace("{sha}", sha)))
    text = etree.SubElement(tei, q("text"))
    body = etree.SubElement(text, q("body"))
    div1 = body_q.find("div1")
    if div1 is None or len(body_q) != 1:
        raise ac.HarterFehler("body enthaelt nicht genau ein div1")
    div = etree.SubElement(body, q("div"))
    # div1: <head/> (leer), <pb n="1"/>, <lg1>
    kinder = list(div1)
    if [k.tag for k in kinder] != ["head", "pb", "lg1"] or len(kinder[0]) or (kinder[0].text or "").strip():
        raise ac.HarterFehler(f"div1-Kinder unerwartet: {[k.tag for k in kinder]}")
    stat["head_leer"] += 1
    etree.SubElement(div, q("pb"), type="edition", n=kinder[1].get("n"))
    stat["pb"] += 1
    lg1 = kinder[2]
    abschnitt = None
    for k in lg1:
        if k.tag == "head":
            at = Atome()
            sammle(k, (), at, stat, protokoll)
            head = etree.SubElement(div, q("head"))
            zeile_fuellen(head, tokenisiere(at.liste, stat), f"{ac.SIGLE}_0", stat)
            stat["head_w"] = sum(1 for _ in head.iter(q("w")))
        elif k.tag == "milestone":
            stat["milestone_entfallen"] += 1
        elif k.tag == "lg2":
            abschnitt = etree.SubElement(div, q("div"), type="section")
            stat["section"] += 1
            for e in k:
                if e.tag == "l":
                    n = e.get("n")
                    l = etree.SubElement(abschnitt, q("l"), n=n)
                    at = Atome()
                    sammle(e, (), at, stat, protokoll)
                    stat["l"] += 1
                    if zeile_fuellen(l, tokenisiere(at.liste, stat), f"{ac.SIGLE}_{n}", stat) == 0:
                        raise ac.HarterFehler(f"Vers {n} ohne Token")
                elif e.tag == "pb":
                    etree.SubElement(abschnitt, q("pb"), type="edition", n=e.get("n"))
                    stat["pb"] += 1
                elif e.tag == "milestone":
                    if e.get("unit") != "column":
                        raise ac.HarterFehler(f"milestone unit={e.get('unit')}")
                    stat["milestone_entfallen"] += 1
                else:
                    raise ac.HarterFehler(f"unerwartet in lg2: {e.tag}")
                if (e.tail or "").strip():
                    raise ac.HarterFehler(f"Text zwischen den Zeilen nach {e.tag}")
        else:
            raise ac.HarterFehler(f"unerwartet in lg1: {k.tag}")
    einruecken(tei, 0)
    return tei


def blatt(e):
    """Elemente, in die keine Einrueckung darf: <w> und <pc> (Mischinhalt, der Wortlaut) und
    ein <hi> ausserhalb eines <w>, das nur ein <pc> traegt. etree.indent schriebe Leerraum in
    ein <w>, das mit einem <hi> beginnt oder endet, und aenderte damit die Wortform."""
    return e.tag in (q("w"), q("pc")) or (e.tag == q("hi") and e.getparent().tag != q("w"))


def einruecken(e, ebene):
    """Einrueckung mit zwei Leerzeichen; der Header kommt fertig eingerueckt aus der Vorlage."""
    kinder = list(e)
    if not kinder or blatt(e) or e.tag == q("teiHeader"):
        return
    innen, aussen = "\n" + "  " * (ebene + 1), "\n" + "  " * ebene
    if (e.text or "").strip():
        raise ac.HarterFehler(f"Mischinhalt in {e.tag}")
    e.text = innen
    for k in kinder:
        if (k.tail or "").strip():
            raise ac.HarterFehler(f"Text nach {k.tag}")
        k.tail = innen
        einruecken(k, ebene + 1)
    kinder[-1].tail = aussen


def text_je_stil(l, ns=""):
    """Je rend-Wert der Text, der darunter steht (Leerraum und Striche entfernt), ohne fw und
    ohne Kommentare. Quelle: hi ohne rend zaehlt als italic. Unabhaengig von der Atom-Logik."""
    stil_text = {}

    def zaehle(text, e):
        t = re.sub(r"[\s\-]", "", text or "")
        if not t:
            return
        stile = {a.get("rend") or "italic" for a in [e, *e.iterancestors()] if a.tag == ns + "hi"}
        for s in stile:
            stil_text.setdefault(s, []).append(t)

    def lauf(e):
        # Dokumentreihenfolge: Text, Kinder samt ihrem tail; fw und Kommentare ohne Inhalt
        if isinstance(e.tag, str) and e.tag != ns + "fw":
            zaehle(e.text, e)
            for k in e:
                lauf(k)
                zaehle(k.tail, e)

    lauf(l)
    return {s: "".join(v) for s, v in stil_text.items()}


def text_der_quelle(body_q):
    """Wortfolge der Quelle je Vers, wie sie im Ziel stehen muss: Druckzeilen-Trennungen
    aufgehoben, fw entfernt, Satzzeichen abgetrennt. Unabhaengig von der Atom-Logik."""
    out = {}
    for l in body_q.iter("l"):
        kopie = etree.fromstring(etree.tostring(l))
        for fw in kopie.iter("fw"):
            fw.text = ""
            for c in list(fw):
                fw.remove(c)
        for o in list(kopie.iter("orig")):
            s = re.sub(r"-\s+", "", "".join(o.itertext()), count=1)
            for c in list(o):
                o.remove(c)
            o.text = s
        for lb in kopie.iter("lb"):
            lb.tail = " " + (lb.tail or "")
        out[l.get("n")] = "".join(kopie.itertext())
    return out


def konvertiere(daten, soll=SOLL, heute="1970-01-01", sha=ac.ROH_SHA256):
    """Rohbytes -> (tei, stat, protokoll, verse_quelle). Alle Bilanzen und das Schema sind
    harte Fehler. soll: erwartete Bestaende (Tests geben eigene Zahlen fuer Mini-Daten)."""
    stat = collections.Counter()
    protokoll = []
    wurzel = quelle_parsen(daten, stat)
    body_q = pruefe_bestand(wurzel, soll)
    tei = baue(body_q, sha, heute, stat, protokoll)

    # Bilanz: jeder Vers der Quelle steht genau einmal im Ziel
    ziel_l = [l.get("n") for l in tei.iter(q("l"))]
    quell_l = [l.get("n") for l in body_q.iter("l")]
    if ziel_l != quell_l:
        raise ac.HarterFehler(f"Verse: Quelle {len(quell_l)}, Ziel {len(ziel_l)}")
    if stat["pb"] != soll["pb"] or stat["cb"] != soll["fw"] or stat["corr"] != soll["corr"]:
        raise ac.HarterFehler(f"Bilanz pb/cb/corr: {stat['pb']}/{stat['cb']}/{stat['corr']}")
    if stat["milestone_entfallen"] != soll["milestone"]:
        raise ac.HarterFehler(f"milestone: {stat['milestone_entfallen']}")
    if stat["section"] != soll["lg2"]:
        raise ac.HarterFehler(f"section: {stat['section']}")
    if stat["lb_im_wort"]:
        raise ac.HarterFehler(f"{stat['lb_im_wort']} Druckzeilenwechsel mitten im Wort ohne <orig>")

    # Wortbilanz je Vers, unabhaengig von der Atom-Logik: die Woerter der Quelle (ohne fw,
    # Trennungen aus orig aufgehoben, lb als Trenner) = die <w> des Ziels, in derselben Folge;
    # dasselbe fuer die Satzzeichen
    quelle = text_der_quelle(body_q)
    for l in tei.iter(q("l")):
        z = ["".join(w.itertext()) for w in l.iter(q("w"))]
        # ein Strich zaehlt zum Wort nur zwischen zwei Buchstaben
        qt = re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)*|[,.;:?!()\-]", quelle[l.get("n")])
        qw = [t for t in qt if t[0].isalpha()]
        if z != qw:
            raise ac.HarterFehler(f"Vers {l.get('n')}: Woerter weichen ab: {qw} != {z}")
        zp = [p.text for p in l.iter(q("pc"))]
        qp = [t for t in qt if not t[0].isalpha()]
        if zp != qp:
            raise ac.HarterFehler(f"Vers {l.get('n')}: Satzzeichen weichen ab: {qp} != {zp}")
        stat["bilanz_verse"] += 1
    # Stilbilanz je Vers: unter jedem rend-Wert steht in Quelle und Ziel derselbe Text
    quell_verse = {l.get("n"): l for l in body_q.iter("l")}
    for l in tei.iter(q("l")):
        qs, zs = text_je_stil(quell_verse[l.get("n")]), text_je_stil(l, "{%s}" % TEI_NS)
        if qs != zs:
            raise ac.HarterFehler(f"Vers {l.get('n')}: Auszeichnung weicht ab: {qs} != {zs}")
        for s, t in zs.items():
            stat[f"stil_zeichen_{s}"] += len(t)

    rng = etree.RelaxNG(etree.parse(str(SCHEMA)))
    baum = etree.ElementTree(tei)
    if not rng.validate(baum):
        for e in list(rng.error_log)[:10]:
            print(f"Schema: Zeile {e.line}: {e.message}", file=sys.stderr)
        raise ac.HarterFehler(f"{len(rng.error_log)} Schemafehler")
    return tei, stat, protokoll, quell_l


def main():
    ac.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quelle", help="Pfad zu apk_free.xml (Vorgabe: sources/hesler-apokalypse/)")
    ap.add_argument("--trocken", action="store_true", help="nur pruefen, nichts schreiben")
    ap.add_argument("--datum", default=datetime.date.today().isoformat(),
                    help="Datum in Header und revisionDesc (Vorgabe heute)")
    ap.add_argument("--ueberschreiben", action="store_true",
                    help="eine schon annotierte Ausgabedatei (Phase 1 bis 3) ersetzen")
    a = ap.parse_args()
    pfad, daten = ac.rohdatei(a.quelle)
    tei, stat, protokoll, quell_l = konvertiere(daten, SOLL, a.datum)

    if (not a.trocken and not a.ueberschreiben and ac.AUSGABE.exists()
            and "lemmaRef=" in ac.AUSGABE.read_text(encoding="utf-8")):
        raise ac.HarterFehler(f"{ac.AUSGABE.name} traegt schon Annotationen aus Phase 1 bis 3; "
                              "--trocken zum Pruefen oder --ueberschreiben, dann die Phasen neu fahren")

    if not a.trocken:
        ac.INGEST_DIR.mkdir(parents=True, exist_ok=True)
        xml = etree.tostring(tei, encoding="unicode")
        with open(ac.AUSGABE, "w", encoding="utf-8", newline="\n") as f:
            f.write("<?xml version='1.0' encoding='UTF-8'?>\n" + PI + "\n" + xml + "\n")

    print(f"Quelle: {pfad} ({ac.ROH_BYTES} Bytes, SHA-256 geprueft)")
    print(f"CSS-Vorspann entfernt: {stat['css_zeichen']} Zeichen")
    print(f"Verse: {stat['l']} von {len(quell_l)} der Quelle, Abschnitte (div section): {stat['section']}")
    print(f"<w>: {stat['w']} (davon {stat['head_w']} in <head>), <pc>: {stat['pc']} "
          f"(davon {stat['pc_mit_stil']} in <hi>)")
    print(f"<pb type=edition>: {stat['pb']}, <cb type=manuscript>: {stat['cb']}, "
          f"milestone column entfallen: {stat['milestone_entfallen']}")
    print(f"hi ohne rend -> italic: {stat['hi_ohne_rend']}")
    print("Stilbilanz je Vers gleich, Zeichen unter rend (ohne fw, Leerraum, Striche): "
          + ", ".join(f"{k[13:]} {v}" for k, v in sorted(stat.items()) if k.startswith("stil_zeichen_")))
    print(f"orig verbunden: {stat['orig']}, davon Form != @reg: {stat['orig_abweichend']}")
    for art, form, reg in protokoll:
        print(f"  {art}: Text {form!r}, reg {reg!r}")
    print(f"corr: {stat['corr']} (Kommentar hinter dem Wort, das die Korrektur enthaelt oder mit ihr endet: "
          f"{stat['corr_im_wort']})")
    print(f"lb im Vers entfallen: {stat['lb_vers']} (mitten im Wort: {stat['lb_im_wort']}); "
          f"Strich am Wortrand als <pc>: {stat['strich_als_pc']}, Strich im Wort: "
          f"{stat['bindestrich_im_wort'] - stat['strich_als_pc']}")
    print("Schema: gueltig (schema/mhdbdb.rng)")
    print("(trocken: nichts geschrieben)" if a.trocken else f"geschrieben: {ac.AUSGABE.relative_to(ac.REPO)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ac.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
