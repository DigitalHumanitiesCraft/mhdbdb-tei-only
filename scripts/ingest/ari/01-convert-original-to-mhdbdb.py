"""01-convert-original-to-mhdbdb.py

Konvertiert Carinas Original-MHDBDB-XML (Arithmetic-Projekt, GAMS Graz) in das
aktuelle MHDBDB-Korpus-Schema. Erste Stufe der ARITHMETIC-Pipeline (Issue #92),
Dogfood für hilfe-daten-beitragen.html.

Mechanische Transformationen (kein Carina-Input nötig):
  - tei:-Präfix entfernen (Default-NS bleibt als einziger TEI-Namespace)
  - <seg type="token"> → <w>      (xml:id wird übernommen)
  - <seg type="pc">    → <pc join="left|right">  (WZB-Heuristik, identisch
                                                  zu wzb-convert-seg-pc.py)
  - <?xml-model?>-PIs hinzufügen
  - <TEI xml:id="{SIGLE}"> als Root
  - Header-Stub mit ARI-Defaults aus Template (Lizenz CC BY-SA 4.0,
    Autor person_anonym, Genre als Platzhalter)

Bewusst stehen gelassen — das ist genau die offene Frage in
docs/DECISIONS.MD § PD-001:
  - <div type="commodity_calculation"|"reckoning_example">
  - <unit type="...">, <rs type="...">
  - <unclear>, <hi rend="superscript|subscript">
Diese Elemente brechen Stage-2-Validierung. Die Liste der Schema-Verletzungen
ist genau der Befund, den PD-001 für die Schema-Erweiterungs- vs.
Wegtransformations-Entscheidung braucht.

Verwendung:
    python scripts/ingest/ari/01-convert-original-to-mhdbdb.py \\
        --input <pfad zur carina-XML> \\
        --sigle ARI_MUE279 \\
        --title-de "München, Universitätsbibliothek, 8 Cod.ms. 279" \\
        --source-url https://gams.uni-graz.at/o:arithmetic.mue279 \\
        --output tei/ARI_MUE279.tei.xml \\
        [--dry-run]
"""

import argparse
import sys
from pathlib import Path
from lxml import etree

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"

SKIP_TAGS_FOR_JOIN = {f"{{{TEI_NS}}}lb", f"{{{TEI_NS}}}cb", f"{{{TEI_NS}}}pb"}


HEADER_TEMPLATE = """<teiHeader xmlns="http://www.tei-c.org/ns/1.0">
    <fileDesc>
      <titleStmt>
        <title xml:lang="de">{title_de}</title>
        <author ref="#person_anonym">Anonym</author>
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
          <licence target="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</licence>
          <p>Daten und Annotationen unter CC BY-SA 4.0. Originaldaten aus dem Arithmetic-Projekt (Universität Graz, GAMS); Share-Alike-Klausel der Quell-Lizenz wird übernommen (CC BY-NC-SA 4.0 wäre mit BY-SA inkompatibel, daher kein Lizenz-Stack wie im MHDBDB-Bestand).</p>
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
              <bibl type="digitalIntermediary" xml:id="{sigle}_arithmetic_gams" corresp="#{sigle}_TBD">
                <title>Arithmetic-Projekt, GAMS (Universität Graz)</title>
                <respStmt>
                  <resp>Elektronische Bereitstellung und TEI-Erstkodierung</resp>
                  <name>Carina (Arithmetic-Projekt)</name>
                </respStmt>
                <ref target="{source_url}"/>
                <note type="provenance">TEI-Originaldaten aus dem GAMS-Repositorium der Universität Graz, Arithmetic-Projekt zu fnhd. Rechenbüchern. Konvertiert in das MHDBDB-Schema durch automatische Transformation (scripts/ingest/ari/01-convert-original-to-mhdbdb.py, 2026-05).</note>
                <note type="fidelity">Mechanische Schema-Konversion ohne Eingriff in Wortgrenzen, Auszeichnungs-Semantik oder Strukturhierarchie.</note>
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
            <gloss xml:lang="de">Rechenbuch (TBD: konkrete Genre-ID von Carina)</gloss>
          </category>
        </taxonomy>
      </classDecl>
    </encodingDesc>
    <profileDesc>
      <langUsage>
        <language ident="gmf">Frühneuhochdeutsch</language>
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
      <change when="2026-05-08" who="#mhdbdb-team">Initiale Konversion aus Arithmetic_MHDBDB.zip via scripts/ingest/ari/01-convert-original-to-mhdbdb.py.</change>
    </revisionDesc>
  </teiHeader>"""


def has_text(s):
    return bool(s and s.strip())


def determine_join(seg):
    """WZB-Heuristik (siehe scripts/ingest/wzb/wzb-convert-seg-pc.py)."""
    parent = seg.getparent()
    children = list(parent)
    idx = children.index(seg)

    if idx == 0:
        return "left" if has_text(parent.text) else "right"

    for i in range(idx - 1, -1, -1):
        prev = children[i]
        if prev.tag in SKIP_TAGS_FOR_JOIN:
            if has_text(prev.tail):
                return "left"
            continue
        return "left"

    return "left" if has_text(parent.text) else "right"


def deep_clone(elem, new_parent, counters):
    """Rekursiver Kopier-Walk in den Default-TEI-NS.

    Transformiert on-the-fly:
      <seg type="token">  → <w>
      <seg type="pc">     → <pc join="...">
    Alle anderen Elemente werden tag-erhaltend in den Default-NS überführt.
    """
    local = etree.QName(elem.tag).localname

    if local == "seg":
        seg_type = elem.get("type")
        if seg_type == "token":
            new_tag = "w"
            attrs_to_copy = {k: v for k, v in elem.attrib.items() if k != "type"}
            counters["seg_token_to_w"] += 1
        elif seg_type == "pc":
            new_tag = "pc"
            attrs_to_copy = {k: v for k, v in elem.attrib.items() if k != "type"}
            join = determine_join(elem)
            attrs_to_copy["join"] = join
            counters[f"seg_pc_to_pc_join_{join}"] += 1
        else:
            new_tag = "seg"
            attrs_to_copy = dict(elem.attrib)
            counters["seg_other"] += 1
    else:
        new_tag = local
        attrs_to_copy = dict(elem.attrib)

    new_elem = etree.SubElement(new_parent, f"{{{TEI_NS}}}{new_tag}")
    for k, v in attrs_to_copy.items():
        new_elem.set(k, v)
    new_elem.text = elem.text

    for child in elem:
        deep_clone(child, new_elem, counters)

    new_elem.tail = elem.tail


def convert(input_path, sigle, title_de, source_url, output_path, dry_run):
    parser = etree.XMLParser(remove_blank_text=False)
    src = etree.parse(str(input_path), parser)
    src_root = src.getroot()

    src_body = src_root.find(f".//{{{TEI_NS}}}body")
    if src_body is None:
        print(f"FEHLER: Kein <body> in {input_path}", file=sys.stderr)
        return 1

    # Neuer TEI-Tree mit nur Default-NS
    nsmap = {None: TEI_NS}
    tei = etree.Element(f"{{{TEI_NS}}}TEI", nsmap=nsmap)
    tei.set(f"{{{XML_NS}}}id", sigle)

    # Header aus Template
    header_xml = HEADER_TEMPLATE.format(
        sigle=sigle,
        title_de=title_de.replace('"', "&quot;"),
        source_url=source_url,
    )
    header = etree.fromstring(header_xml)
    tei.append(header)

    # text/body bauen
    text_el = etree.SubElement(tei, f"{{{TEI_NS}}}text")
    body_el = etree.SubElement(text_el, f"{{{TEI_NS}}}body")

    counters = {
        "seg_token_to_w": 0,
        "seg_pc_to_pc_join_left": 0,
        "seg_pc_to_pc_join_right": 0,
        "seg_other": 0,
    }

    # Body-Inhalte rüberkopieren (ohne den body-Knoten selbst — nur Kinder)
    for child in src_body:
        deep_clone(child, body_el, counters)

    # Output assemblieren mit xml-model PIs
    pi1 = etree.ProcessingInstruction(
        "xml-model",
        'href="../schema/mhdbdb.rng" type="application/xml" '
        'schematypens="http://relaxng.org/ns/structure/1.0"',
    )
    pi2 = etree.ProcessingInstruction(
        "xml-model",
        'href="https://tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng"',
    )
    tei.addprevious(pi1)
    tei.addprevious(pi2)

    output_tree = etree.ElementTree(tei)

    print(f"{'[DRY RUN] ' if dry_run else ''}Konversion {input_path.name} -> {output_path}")
    print(f"  <seg type='token'> -> <w>:                  {counters['seg_token_to_w']:>6d}")
    print(f"  <seg type='pc'>    -> <pc join='left'>:     {counters['seg_pc_to_pc_join_left']:>6d}")
    print(f"  <seg type='pc'>    -> <pc join='right'>:    {counters['seg_pc_to_pc_join_right']:>6d}")
    if counters["seg_other"]:
        print(f"  <seg type='other'> (unveraendert):          {counters['seg_other']:>6d}")

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_tree.write(
            str(output_path),
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=True,
        )
        print(f"Geschrieben: {output_path}")

    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True, type=Path, help="Carinas Original-XML")
    p.add_argument("--sigle", required=True, help="MHDBDB-Sigle, z.B. ARI_MUE279")
    p.add_argument("--title-de", required=True, help="Deutscher Titel für teiHeader")
    p.add_argument("--source-url", required=True, help="GAMS-URL (z.B. https://gams.uni-graz.at/o:arithmetic.mue279)")
    p.add_argument("--output", required=True, type=Path, help="Ziel-Pfad, z.B. tei/ARI_MUE279.tei.xml")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    return convert(args.input, args.sigle, args.title_de, args.source_url, args.output, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
