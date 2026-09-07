#!/usr/bin/env python3
"""
Sync TEI Headers from Authority Files

General-purpose tool for synchronizing authority data to TEI file headers.
Reads from authority-files/*.xml and updates corresponding TEI file headers.

Supported authority files:
- works.xml: Syncs work metadata (external IDs, biblStruct elements) to TEI headers
- persons.xml: (Future) Syncs author/person metadata
- genres.xml: (Future) Syncs genre classifications
- concepts.xml: (Future) Syncs concept annotations
- [Add more as needed]

Usage:
    # Sync all authority files
    python scripts/sync/sync_tei_headers.py --all [--dry-run]
    
    # Sync specific authority file
    python scripts/sync/sync_tei_headers.py --works [--dry-run]
    python scripts/sync/sync_tei_headers.py --persons [--dry-run]
    
    # Sync multiple specific files
    python scripts/sync/sync_tei_headers.py --works --persons [--dry-run]

Examples:
    # Preview changes from all authority files
    python scripts/sync/sync_tei_headers.py --all --dry-run
    
    # Sync only works.xml (Issue #19)
    python scripts/sync/sync_tei_headers.py --works
    
After running:
    python scripts/build-authority-index.py  # Rebuild index
"""

import sys
import re
import argparse
import logging
from pathlib import Path
from lxml import etree
from typing import Dict, List, Set
from abc import ABC, abstractmethod

# Gemeinsame Korpusauswahl (#287).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from corpus_files import TEI_DIR, corpus_files  # noqa: E402

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File paths
AUTHORITY_DIR = Path("authority-files")

# TEI namespace
TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}
TEI_NS_URI = "http://www.tei-c.org/ns/1.0"
XML_NS = {"xml": "http://www.w3.org/XML/1998/namespace"}


class AuthoritySyncer(ABC):
    """Base class for syncing authority data to TEI headers"""
    
    def __init__(self, authority_file: Path, tei_dir: Path):
        self.authority_file = authority_file
        self.tei_dir = tei_dir
        self.name = authority_file.stem  # e.g., 'works', 'persons'
    
    @abstractmethod
    def load_authority_data(self) -> Dict:
        """Load data from authority file. Returns sigle → data mapping."""
        pass
    
    @abstractmethod
    def update_tei_header(self, tei_tree: etree._ElementTree, sigle: str, 
                         data: any, dry_run: bool) -> bool:
        """Update a single TEI header. Returns True if updated."""
        pass
    
    def sync_all_tei_files(self, dry_run: bool = False) -> tuple:
        """Sync all TEI files. Returns (updated_count, skipped_count)."""
        # Load authority data
        authority_data = self.load_authority_data()
        
        if not authority_data:
            logger.warning(f"No data loaded from {self.authority_file}")
            return (0, 0)
        
        logger.info(f"Loaded data for {len(authority_data)} sigles from {self.authority_file.name}")
        
        # Process TEI files
        tei_files = corpus_files(self.tei_dir)
        logger.info(f"Processing {len(tei_files)} TEI files for {self.name}...")
        
        updated_count = 0
        skipped_count = 0
        
        for tei_file in tei_files:
            # Extract sigle from filename (e.g., ABG.tei.xml → ABG)
            sigle = tei_file.stem.replace('.tei', '')
            
            if sigle not in authority_data:
                logger.debug(f"No {self.name} data for {sigle}, skipping")
                skipped_count += 1
                continue
            
            if self._update_single_tei(tei_file, sigle, authority_data[sigle], dry_run):
                updated_count += 1
            else:
                skipped_count += 1
        
        logger.info(f"[{self.name}] {'Would update' if dry_run else 'Updated'} {updated_count} TEI files, skipped {skipped_count}")
        return (updated_count, skipped_count)
    
    def _update_single_tei(self, tei_file: Path, sigle: str, data: any, 
                          dry_run: bool = False) -> bool:
        """Update a single TEI file. Returns True if updated."""
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(str(tei_file), parser)
            
            # Call subclass-specific update logic
            updated = self.update_tei_header(tree, sigle, data, dry_run)
            
            if updated and not dry_run:
                # Save file
                tree.write(
                    str(tei_file),
                    encoding='utf-8',
                    xml_declaration=True,
                    pretty_print=True
                )
                logger.debug(f"[{self.name}] Updated {sigle}")
            elif updated and dry_run:
                logger.debug(f"[{self.name}] Would update {sigle}")
            
            return updated
            
        except Exception as e:
            logger.error(f"[{self.name}] Error updating {tei_file}: {e}")
            return False


def extract_id_from_url(url: str, id_type: str) -> str:
    """
    Extract compact ID from full URL.

    Examples:
        http://www.handschriftencensus.de/werke/217 → '217'
        https://d-nb.info/gnd/4467770-4 → '4467770-4'
        http://www.wikidata.org/entity/Q2643537 → 'Q2643537'
    """
    if not url:
        return None
    return url.rstrip('/').rsplit('/', 1)[-1]


class WorksSyncer(AuthoritySyncer):
    """Syncs all work metadata from works.xml to TEI headers"""

    def load_authority_data(self) -> Dict[str, Dict]:
        """
        Load work data from works.xml. Returns sigle → work data mapping.

        Returns:
            {
                'ABG': {
                    'work_id': 'work_89',
                    'handschriftencensus': '217',
                    'gnd': '4467770-4',
                    'wikidata': 'Q2643537',
                    'biblStructs': [<Element biblStruct...>]
                },
                ...
            }

        Nebenbei wird `self.work_by_id_and_sigle` gefuellt, geschluesselt nach
        (work_id, sigle). Beide Teile des Schluessels sind noetig: die work_id,
        weil eine Sigle nicht eindeutig ein Werk identifiziert, und die Sigle,
        weil `biblStructs` nach `@key = sigle` gefiltert ist und sich damit
        innerhalb desselben Werks je Sigle unterscheidet. 70 der 584 Werke
        tragen mehr als eine Sigle, und die Zahl der biblStruct weicht dort
        tatsaechlich ab (work_205: DES2 hat 1, GSP hat 2; work_668: WG 1,
        WGA 2, WGI 2). Eine Ablage allein nach work_id hielte den Datensatz
        der zuletzt gelesenen Sigle und haenge einer Datei die Bibliographie
        einer anderen an.

        Warum es die zweite Ablage ueberhaupt braucht: TRO traegt sowohl
        work_69 (Konrad von Wuerzburg,
        'Trojanerkrieg') als auch work_c7da236c-... (die anonyme
        'Trojanerkrieg'-Fortsetzung), weil die Datei tei/TRO.tei.xml beide
        Texte enthaelt (Ausgabe Keller 1858, Verse 1 bis 49861). Bei einer
        Doppel-Sigle gewann hier frueher der letzte Eintrag in
        Dokumentreihenfolge, und der Sync schrieb TRO die Identifier der
        Fortsetzung in den Header (#395). Eindeutig ist stattdessen das
        @corresp am msIdentifier, siehe update_tei_header.
        Gemessen am 07.09.2026: 667 von 667 Korpusdateien tragen @corresp,
        alle 667 zeigen auf eine in works.xml definierte work_id, und genau
        eine (TRO) weicht von der Sigle-Aufloesung ab.
        """
        sigle_to_work = {}
        self.work_by_id_and_sigle = {}

        tree = etree.parse(str(self.authority_file))
        root = tree.getroot()

        # Find all work entries
        works = root.xpath('//tei:bibl[starts-with(@xml:id, "work_")]', namespaces=TEI_NS)

        for work in works:
            work_id = work.get(f"{{{XML_NS['xml']}}}id")

            # Get all sigles for this work (one work can have multiple sigles)
            sigle_elems = work.xpath('.//tei:idno[@type="sigle"]', namespaces=TEI_NS)
            if not sigle_elems:
                continue

            # Extract external IDs (work-level, shared by all sigles)
            handschriftencensus_elem = work.xpath('.//tei:idno[@type="handschriftencensus"]', namespaces=TEI_NS)
            gnd_elem = work.xpath('.//tei:idno[@type="GND"]', namespaces=TEI_NS)
            wikidata_elem = work.xpath('.//tei:idno[@type="wikidata"]', namespaces=TEI_NS)

            handschriftencensus_id = extract_id_from_url(
                handschriftencensus_elem[0].text if handschriftencensus_elem else None,
                'handschriftencensus'
            )
            gnd_id = extract_id_from_url(
                gnd_elem[0].text if gnd_elem else None,
                'GND'
            )
            wikidata_id = extract_id_from_url(
                wikidata_elem[0].text if wikidata_elem else None,
                'wikidata'
            )

            # Process each sigle
            for sigle_elem in sigle_elems:
                sigle = sigle_elem.text
                if not sigle:
                    continue

                # Find biblStructs where @key matches this sigle
                biblstructs = work.xpath(f'.//tei:biblStruct[@key="{sigle}"]', namespaces=TEI_NS)

                # Build work data for this sigle
                work_data = {
                    'work_id': work_id,
                    'handschriftencensus': handschriftencensus_id,
                    'gnd': gnd_id,
                    'wikidata': wikidata_id,
                    'biblStructs': biblstructs  # List of lxml Elements
                }

                if sigle in sigle_to_work:
                    logger.warning(
                        f"[works] Sigle {sigle} kommt in works.xml mehrfach vor "
                        f"({sigle_to_work[sigle]['work_id']} und {work_id}). "
                        f"Die Zuordnung ueber die Sigle ist hier mehrdeutig; "
                        f"massgeblich ist das @corresp des jeweiligen Headers."
                    )

                sigle_to_work[sigle] = work_data
                self.work_by_id_and_sigle[(work_id, sigle)] = work_data

                logger.debug(
                    f"Works: {sigle} → {work_id} "
                    f"(hc={handschriftencensus_id}, gnd={gnd_id}, wd={wikidata_id}, "
                    f"biblStructs={len(biblstructs)})"
                )

        return sigle_to_work

    def update_tei_header(self, tei_tree: etree._ElementTree, sigle: str,
                         data: Dict, dry_run: bool) -> bool:
        """
        Update TEI header with work metadata.

        Updates:
        1. External IDs in <msIdentifier>
        2. biblStruct elements in <listBibl>
        """
        root = tei_tree.getroot()
        updated = False

        # ================================================================
        # 1. Update msIdentifier with external IDs
        # ================================================================
        ms_identifier = root.xpath('//tei:teiHeader//tei:msIdentifier', namespaces=TEI_NS)
        if not ms_identifier:
            logger.warning(f"[works] {sigle}: No msIdentifier found")
            return False

        ms_identifier = ms_identifier[0]

        # Die Sigle ist nicht eindeutig (siehe load_authority_data), das
        # @corresp ist es. Wo beide auf verschiedene Werke zeigen, gilt das
        # @corresp: die Datei sagt selbst, welches Werk sie beschreibt, und
        # ihr <author> und <title> stehen daneben. Fuer 666 der 667
        # Korpusdateien aendert das nichts, weil dort beide Wege auf dasselbe
        # Werk fuehren.
        corresp = ms_identifier.get('corresp') or ''
        corresp_work_id = corresp.split('#')[-1] if '#' in corresp else ''
        if corresp_work_id and corresp_work_id != data.get('work_id'):
            # Direkter Zugriff, kein getattr mit Voreinstellung: fehlt das
            # Attribut, ist load_authority_data nicht gelaufen, und der
            # AttributeError landet als ERROR im Log von _update_single_tei.
            # Ein getattr faenge das stumm auf und fiele auf die Sigle
            # zurueck, also genau in den Fehlermodus, den dieser Zweig
            # beseitigt.
            ziel = self.work_by_id_and_sigle.get((corresp_work_id, sigle))
            if ziel is not None:
                logger.info(
                    f"[works] {sigle}: @corresp zeigt auf {corresp_work_id}, "
                    f"die Sigle-Aufloesung auf {data.get('work_id')}. "
                    f"Es gilt {corresp_work_id}."
                )
                data = ziel
            else:
                # Warnen und bei der Sigle bleiben, nicht ueberspringen: eine
                # frisch ingestete Datei traegt zunaechst ein Platzhalter-
                # @corresp (die ARI-Vorlage schreibt work_TBD, siehe
                # scripts/ingest/ari/01-convert-original-to-mhdbdb.py:93), und
                # die soll trotzdem ihre Identifier bekommen. Heute trifft der
                # Zweig auf keine der 667 Dateien zu.
                logger.warning(
                    f"[works] {sigle}: @corresp zeigt auf {corresp_work_id}, "
                    f"aber dieses Werk fuehrt die Sigle {sigle} nicht. "
                    f"Es bleibt bei der Sigle-Aufloesung "
                    f"({data.get('work_id')}); pruefe das @corresp."
                )

        if not dry_run:
            # Remove existing external ID idno elements (but keep sigle idno)
            for old_idno in ms_identifier.xpath('.//tei:idno[@type!="sigle"]', namespaces=TEI_NS):
                old_idno.getparent().remove(old_idno)

            # Add external IDs after the sigle idno
            sigle_idno = ms_identifier.xpath('.//tei:idno[@type="sigle"]', namespaces=TEI_NS)
            if sigle_idno:
                insert_after = sigle_idno[0]

                # Add handschriftencensus
                if data['handschriftencensus']:
                    hc_idno = etree.Element(f"{{{TEI_NS_URI}}}idno")
                    hc_idno.set('type', 'handschriftencensus')
                    hc_idno.text = data['handschriftencensus']
                    insert_after.addnext(hc_idno)
                    insert_after = hc_idno
                    updated = True

                # Add GND
                if data['gnd']:
                    gnd_idno = etree.Element(f"{{{TEI_NS_URI}}}idno")
                    gnd_idno.set('type', 'GND')
                    gnd_idno.text = data['gnd']
                    insert_after.addnext(gnd_idno)
                    insert_after = gnd_idno
                    updated = True

                # Add Wikidata
                if data['wikidata']:
                    wd_idno = etree.Element(f"{{{TEI_NS_URI}}}idno")
                    wd_idno.set('type', 'wikidata')
                    wd_idno.text = data['wikidata']
                    insert_after.addnext(wd_idno)
                    updated = True
        else:
            # Dry run: just check if we have data to add
            if data['handschriftencensus'] or data['gnd'] or data['wikidata']:
                updated = True

        # ================================================================
        # 2. Update biblStruct elements in listBibl
        # ================================================================
        # Find or create additional/listBibl structure
        ms_desc = root.xpath('//tei:teiHeader//tei:msDesc', namespaces=TEI_NS)
        if not ms_desc:
            logger.warning(f"[works] {sigle}: No msDesc found")
            return updated

        ms_desc = ms_desc[0]

        if not dry_run:
            # Find or create additional element
            additional = ms_desc.xpath('.//tei:additional', namespaces=TEI_NS)
            if not additional:
                additional = etree.SubElement(ms_desc, f"{{{TEI_NS_URI}}}additional")
            else:
                additional = additional[0]

            # Find or create listBibl element
            list_bibl = additional.xpath('.//tei:listBibl', namespaces=TEI_NS)
            if not list_bibl:
                list_bibl = etree.SubElement(additional, f"{{{TEI_NS_URI}}}listBibl")
            else:
                list_bibl = list_bibl[0]

            # Remove existing biblStruct elements
            for old_biblstruct in list_bibl.xpath('.//tei:biblStruct', namespaces=TEI_NS):
                old_biblstruct.getparent().remove(old_biblstruct)

            # Add biblStruct elements from works.xml (matched by @key attribute)
            import copy
            for biblstruct in data['biblStructs']:
                list_bibl.append(copy.deepcopy(biblstruct))

            if data['biblStructs']:
                updated = True
        else:
            # Dry run: check if we have biblStructs to add
            if data['biblStructs']:
                updated = True

        if updated:
            id_summary = []
            if data['handschriftencensus']:
                id_summary.append(f"hc={data['handschriftencensus']}")
            if data['gnd']:
                id_summary.append(f"gnd={data['gnd']}")
            if data['wikidata']:
                id_summary.append(f"wd={data['wikidata']}")
            id_str = ", ".join(id_summary) if id_summary else "no IDs"

            logger.debug(
                f"[works] {sigle}: {'Would update' if dry_run else 'Updated'} "
                f"({id_str}, {len(data['biblStructs'])} biblStruct(s))"
            )

        return updated


class PersonsSyncer(AuthoritySyncer):
    """Syncs person/author data from persons.xml"""
    
    def load_authority_data(self) -> Dict:
        """Load person data from persons.xml. Returns person_id → person data."""
        # TODO: Implement when needed. Until then, fail loudly rather than
        # returning {} (which the summary would render as a clean "0 updated").
        raise NotImplementedError(
            "PersonsSyncer is a declared stub (TODO). See IMPLEMENTED_SYNCERS in main()."
        )
    
    def update_tei_header(self, tei_tree: etree._ElementTree, sigle: str, 
                         data: any, dry_run: bool) -> bool:
        """Update person/author data in TEI header."""
        # TODO: Implement when needed
        return False


class GenresSyncer(AuthoritySyncer):
    """Syncs genre classifications from genres.xml"""
    
    def load_authority_data(self) -> Dict:
        """Load genre data from genres.xml."""
        # TODO: Implement when needed. Fail loudly instead of silent (0, 0).
        raise NotImplementedError(
            "GenresSyncer is a declared stub (TODO). See IMPLEMENTED_SYNCERS in main()."
        )
    
    def update_tei_header(self, tei_tree: etree._ElementTree, sigle: str, 
                         data: any, dry_run: bool) -> bool:
        """Update genre classifications in TEI header."""
        # TODO: Implement when needed
        return False


class ConceptsSyncer(AuthoritySyncer):
    """Syncs concept annotations from concepts.xml"""
    
    def load_authority_data(self) -> Dict:
        """Load concept data from concepts.xml."""
        # TODO: Implement when needed. Fail loudly instead of silent (0, 0).
        raise NotImplementedError(
            "ConceptsSyncer is a declared stub (TODO). See IMPLEMENTED_SYNCERS in main()."
        )
    
    def update_tei_header(self, tei_tree: etree._ElementTree, sigle: str, 
                         data: any, dry_run: bool) -> bool:
        """Update concept annotations in TEI header."""
        # TODO: Implement when needed
        return False


# Registry of available syncers
SYNCERS = {
    'works': WorksSyncer,
    'persons': PersonsSyncer,
    'genres': GenresSyncer,
    'concepts': ConceptsSyncer,
}

# Only these are actually implemented; the others are declared stubs (see the
# classes above). Kept explicit so an unimplemented syncer fails LOUDLY instead
# of silently returning (0, 0), which reads as "ran fine, nothing to do".
IMPLEMENTED_SYNCERS = {'works'}

# Typen, die works.xml fuer das WERK fuehrt und die der Header spiegelt.
# sigle und mwb-sigle stehen bewusst nicht dabei: die Sigle ist header-eigen
# (works.xml fuehrt sie als Schluessel, nicht als Spiegel), und mwb-sigle ist
# textzeugenspezifisch. Das MWB vergibt je Redaktion eine eigene Sigle
# (NibA, NibB, NibC, NibD im Quellenverzeichnis), waehrend works.xml
# Identifier nur je Werk kennt: work_18 traegt die vier Siglen NBB, NLA,
# NLB und NLC, und nur NLC ist NibC. Aus works.xml generiert bekaeme NLA
# die Sigle der C-Redaktion (#399, gemessen 07.09.2026).
GESPIEGELTE_TYPEN = ('handschriftencensus', 'GND', 'wikidata')


def erster_msidentifier(tei_datei: Path):
    """Den msIdentifier einer TEI-Datei lesen, ohne die ganze Datei zu parsen.

    Die Korpusdateien sind zusammen 1,4 GB, die groesste 63 MB; ein
    vollstaendiger Parse je Datei kostet fuer ein Gate zu viel. `iterparse`
    liefert das Element, sobald sein Endtag gelesen ist, und der
    msIdentifier steht im Header. Danach wird abgebrochen.

    Returns (corresp, {typ: erster Wert}) oder (None, None).
    """
    ziel = f'{{{TEI_NS_URI}}}msIdentifier'
    try:
        for _, el in etree.iterparse(str(tei_datei), events=('end',), tag=ziel):
            werte = {}
            for idno in el.findall(f'{{{TEI_NS_URI}}}idno'):
                typ = idno.get('type')
                # erster Wert gewinnt, wie im Schreibpfad: works.xml fuehrt
                # fuer LAU zwei wikidata-IDs, und update_tei_header nimmt
                # dort ebenfalls [0]. Ein Check auf die Menge waere hier
                # dauerhaft rot, ohne dass etwas falsch ist.
                if typ in GESPIEGELTE_TYPEN and typ not in werte and idno.text:
                    werte[typ] = idno.text.strip()
            return el.get('corresp'), werte
    except etree.XMLSyntaxError as exc:
        logger.error(f"{tei_datei.name}: nicht parsebar ({exc})")
    return None, None


MSID_BLOCK = re.compile(r'<msIdentifier\b[^>]*>.*?</msIdentifier>', re.S)


def _idno_zeile(typ: str, wert: str, einzug: str, zeilenende: str) -> str:
    return f'{einzug}<idno type="{typ}">{wert}</idno>{zeilenende}'


def schreibe_werk_identifier(dry_run: bool = False) -> int:
    """--works: die gespiegelten Identifier in den msIdentifier schreiben.

    **Chirurgisch, nicht ueber lxml.** Der Weg ueber
    `etree.parse(remove_blank_text=True)` plus `tree.write(pretty_print=True)`
    setzt die Einrueckung der GANZEN Datei neu; gemessen am 07.09.2026 aendert
    ein solcher Lauf alle 667 Korpusdateien und schrumpft das Korpus von
    1.432,5 auf 1.430,6 MB, ohne dass sich inhaltlich etwas aendert. Ein Gate
    darauf waere dauerhaft rot, und die Fehlermeldung von --check verwiese auf
    ein Kommando, das mehr kaputtmacht als es repariert. Der alte Pfad
    formatiert dabei nicht nur um: er loescht die 19 mwb-sigle und aendert
    bei fuenf Dateien (AK, FR3, HZ, LUU, WZB) die Bibliographie inhaltlich. Dieselbe Begruendung
    steht in scripts/audit/drop-negative-variant-corresp.py und
    scripts/sync/build-wbnetz-lemma-list.py, die aus demselben Grund
    zeilenweise arbeiten.

    Angefasst wird ausschliesslich der msIdentifier-Block, und darin nur die
    idno der Typen in GESPIEGELTE_TYPEN. sigle und mwb-sigle bleiben stehen,
    ebenso msName, @corresp und alles ausserhalb des Blocks. Zeilenenden
    bleiben erhalten (WZB ist eine CRLF-Datei).

    Die listBibl wird NICHT angefasst, siehe --bibl-struct.
    """
    syncer = WorksSyncer(AUTHORITY_DIR / 'works.xml', TEI_DIR)
    nach_sigle = syncer.load_authority_data()
    nach_id_und_sigle = syncer.work_by_id_and_sigle

    geaendert = 0
    for tei_datei in corpus_files(TEI_DIR):
        sigle = tei_datei.stem.replace('.tei', '')
        text = tei_datei.read_text(encoding='utf-8', newline='')
        treffer = MSID_BLOCK.search(text)
        if not treffer:
            logger.warning(f"[works] {sigle}: kein msIdentifier")
            continue

        block = treffer.group(0)
        corresp_m = re.search(r'\bcorresp="([^"]*)"', block)
        corresp = corresp_m.group(1) if corresp_m else ''
        work_id = corresp.split('#')[-1] if '#' in corresp else ''
        daten = nach_id_und_sigle.get((work_id, sigle)) or nach_sigle.get(sigle)
        if daten is None:
            continue

        soll = [(typ, daten[feld]) for typ, feld in
                (('handschriftencensus', 'handschriftencensus'),
                 ('GND', 'gnd'), ('wikidata', 'wikidata')) if daten.get(feld)]

        # Einzug und Zeilenende von der sigle-Zeile abschauen, damit das
        # Ergebnis aussieht wie der Rest der Datei.
        sigle_m = re.search(r'(\r?\n)([ \t]*)<idno type="sigle">', block)
        zeilenende = sigle_m.group(1) if sigle_m else '\n'
        einzug = sigle_m.group(2) if sigle_m else '            '

        # bestehende gespiegelte idno entfernen, samt ihrer eigenen Zeile
        # `<idno` mit beliebigen weiteren Attributen und auch ohne eigene
        # Zeile treffen: sonst bliebe so ein Element stehen und bekaeme das
        # neue danebengesetzt (zwei idno desselben Typs), was --check nicht
        # bemerkt, weil dort der erste Wert gewinnt. Heute 0 von 667 Faellen,
        # und schema/mhdbdb.rnc:114 laesst am msIdentifier-idno nur @type zu;
        # die Luecke ist also latent und kostet zwei Zeichen.
        typen = '|'.join(GESPIEGELTE_TYPEN)
        neu_block = re.sub(
            rf'(?:\r?\n[ \t]*)?<idno\b[^>]*\btype="(?:{typen})"[^>]*>[^<]*</idno>',
            '', block)

        # neue direkt nach der sigle einsetzen
        if soll:
            einsatz = ''.join(_idno_zeile(t, w, einzug, zeilenende)
                              for t, w in soll)
            sigle_ende = re.search(r'<idno type="sigle">[^<]*</idno>', neu_block)
            if not sigle_ende:
                logger.warning(f"[works] {sigle}: keine sigle im msIdentifier, "
                               f"uebersprungen")
                continue
            pos = sigle_ende.end()
            neu_block = (neu_block[:pos] + zeilenende
                         + einsatz.rstrip(zeilenende) + neu_block[pos:])

        if neu_block == block:
            continue
        geaendert += 1
        if dry_run:
            logger.info(f"[works] {sigle}: wuerde geaendert")
            continue
        tei_datei.write_text(text[:treffer.start()] + neu_block
                             + text[treffer.end():],
                             encoding='utf-8', newline='')
        logger.info(f"[works] {sigle}: msIdentifier aktualisiert")

    logger.info(f"[works] {'wuerde aendern' if dry_run else 'geaendert'}: "
                f"{geaendert} Datei(en)")
    return geaendert


def pruefe_werk_identifier() -> int:
    """--check: Header gegen works.xml halten, ohne irgendetwas zu schreiben.

    Verglichen wird der INHALT, nicht die Formatierung. Das ist der
    Unterschied zu einem "Sync laufen lassen und diffen": ein Lauf von
    WorksSyncer serialisiert jede Datei ueber lxml neu und aendert damit
    alle 667, ohne dass sich inhaltlich etwas aendert (gemessen 07.09.2026:
    das Korpus schrumpft dabei von 1.432,5 auf 1.430,6 MB, reine
    Einrueckung). Ein Gate auf dem Dateidiff waere dauerhaft rot.

    Returns die Zahl der abweichenden Dateien (0 = alles synchron).
    """
    syncer = WorksSyncer(AUTHORITY_DIR / 'works.xml', TEI_DIR)
    nach_sigle = syncer.load_authority_data()
    nach_id_und_sigle = syncer.work_by_id_and_sigle

    abweichend = []
    ohne_msid = []
    geprueft = 0

    for tei_datei in corpus_files(TEI_DIR):
        sigle = tei_datei.stem.replace('.tei', '')
        corresp, ist = erster_msidentifier(tei_datei)
        if ist is None:
            ohne_msid.append(sigle)
            continue

        work_id = corresp.split('#')[-1] if corresp and '#' in corresp else ''
        # dieselbe Aufloesung wie im Schreibpfad: @corresp schlaegt die Sigle
        daten = nach_id_und_sigle.get((work_id, sigle)) or nach_sigle.get(sigle)
        if daten is None:
            continue
        geprueft += 1

        soll = {}
        for typ, feld in (('handschriftencensus', 'handschriftencensus'),
                          ('GND', 'gnd'), ('wikidata', 'wikidata')):
            if daten.get(feld):
                soll[typ] = daten[feld]

        if ist != soll:
            abweichend.append((sigle, ist, soll))

    logger.info(f"[check] {geprueft} Dateien gegen works.xml geprueft")
    if ohne_msid:
        logger.warning(f"[check] ohne msIdentifier: {', '.join(ohne_msid)}")

    if not abweichend:
        logger.info("[check] OK: Header und works.xml stimmen bei "
                    f"{', '.join(GESPIEGELTE_TYPEN)} ueberein")
        return 0

    logger.error(f"[check] {len(abweichend)} Datei(en) weichen von works.xml ab:")
    for sigle, ist, soll in abweichend:
        logger.error(f"  {sigle}: Header {ist or '{}'} gegen works.xml {soll or '{}'}")
    logger.error("Beheben mit: python scripts/sync/sync_tei_headers.py --works")
    return len(abweichend)



def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description='Sync TEI headers with authority file data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync all authority files
  python scripts/sync/sync_tei_headers.py --all
  
  # Sync only works.xml (for Issue #19)
  python scripts/sync/sync_tei_headers.py --works
  
  # Preview changes before applying
  python scripts/sync/sync_tei_headers.py --works --dry-run
  
  # Sync multiple specific files
  python scripts/sync/sync_tei_headers.py --works --persons

  # Gate: Header gegen works.xml pruefen, ohne zu schreiben (#399)
  python scripts/sync/sync_tei_headers.py --works --check
        """
    )
    
    # Authority file selection
    parser.add_argument('--all', action='store_true',
                       help='Sync all authority files')
    parser.add_argument('--works', action='store_true',
                       help='Sync works.xml (work metadata: external IDs, biblStruct elements)')
    parser.add_argument('--persons', action='store_true',
                       help='Sync persons.xml (author data) [NOT YET IMPLEMENTED]')
    parser.add_argument('--genres', action='store_true',
                       help='Sync genres.xml (genre classifications) [NOT YET IMPLEMENTED]')
    parser.add_argument('--concepts', action='store_true',
                       help='Sync concepts.xml (concept annotations) [NOT YET IMPLEMENTED]')
    
    # Options
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')
    parser.add_argument('--bibl-struct', action='store_true',
                       help='Zusaetzlich die listBibl aus works.xml ziehen. '
                            'ACHTUNG: dieser Weg laeuft ueber lxml und '
                            'serialisiert jede Datei neu (gemessen: alle 667 '
                            'geaendert, Korpus 1.432,5 -> 1.430,6 MB). Er '
                            'LOESCHT dabei die 19 mwb-sigle und aendert bei '
                            'AK, FR3, HZ, LUU und WZB die Bibliographie '
                            'inhaltlich. Nur bewusst benutzen.')
    parser.add_argument('--check', action='store_true',
                       help='Gate (#399): Header gegen works.xml pruefen, nichts '
                            'schreiben, Exit 1 bei Abweichung. Vergleicht Inhalte, '
                            'nicht Formatierung. Nur fuer works.')

    args = parser.parse_args()

    # --check ist ein eigener Modus und laeuft vor der Syncer-Auswahl: es
    # schreibt nichts, braucht keinen Syncer-Lauf und gilt nur fuer works.
    if args.check:
        if args.persons or args.genres or args.concepts:
            parser.error('--check gibt es nur fuer works (die uebrigen Syncer '
                         'sind deklarierte Stubs).')
        return 1 if pruefe_werk_identifier() else 0

    # works laeuft IMMER ueber den chirurgischen Schreiber, auch unter --all.
    # Der alte lxml-Pfad ist nur noch ueber das ausdrueckliche --bibl-struct
    # erreichbar, und das ist kein Geschmacksunterschied: er loescht alle
    # Nicht-Sigle-idno (Zeile 339, `idno[@type!="sigle"]`) und damit auch die
    # 19 mwb-sigle, die works.xml nicht kennt und nie zurueckgeben kann.
    # Gemessen am 07.09.2026 auf einer Korpuskopie: 19 Dateien mit mwb-sigle
    # vorher, 0 nachher. --check faellt darauf nicht herein, weil es
    # mwb-sigle bewusst nicht prueft. Ein --all, das still in diesen Pfad
    # faellt, waere also ein Datenverlust ohne Warnung.
    if (args.works or args.all) and not args.bibl_struct:
        schreibe_werk_identifier(dry_run=args.dry_run)
        logger.info("Hinweis: die listBibl wurde nicht angefasst (dafuer "
                    "--bibl-struct, siehe dessen Hilfetext).")
        syncers_to_run = [s for s in syncers_to_run if s != 'works']
        if not syncers_to_run:
            return 0
    
    # Determine which syncers to run
    syncers_to_run = []
    
    if args.all:
        syncers_to_run = list(SYNCERS.keys())
    else:
        if args.works:
            syncers_to_run.append('works')
        if args.persons:
            syncers_to_run.append('persons')
        if args.genres:
            syncers_to_run.append('genres')
        if args.concepts:
            syncers_to_run.append('concepts')
    
    if not syncers_to_run:
        parser.print_help()
        logger.error("\nError: Must specify at least one authority file (--all, --works, etc.)")
        return 1

    # Guard against the silent-stub trap: an explicit request for an
    # unimplemented syncer must fail loudly; --all just skips them with a note.
    unimplemented = [s for s in syncers_to_run if s not in IMPLEMENTED_SYNCERS]
    if unimplemented and not args.all:
        logger.error(
            f"Not implemented: {', '.join(unimplemented)}. "
            f"Implemented: {', '.join(sorted(IMPLEMENTED_SYNCERS))}. "
            "These are declared stubs in sync_tei_headers.py (TODO: implement when needed). "
            "Refusing to report a misleading '0 updated' success."
        )
        return 1
    if unimplemented:  # args.all
        logger.warning(
            f"Skipping not-yet-implemented syncers: {', '.join(unimplemented)} "
            "(declared stubs; nothing is synced for them)."
        )
        syncers_to_run = [s for s in syncers_to_run if s in IMPLEMENTED_SYNCERS]
    
    # Display mode
    if args.dry_run:
        logger.info("=" * 60)
        logger.info("DRY RUN MODE - No files will be modified")
        logger.info("=" * 60)
    
    logger.info(f"Syncing authority files: {', '.join(syncers_to_run)}")
    logger.info("")
    
    try:
        total_updated = 0
        total_skipped = 0
        
        # Run each syncer
        for syncer_name in syncers_to_run:
            logger.info(f"--- Processing {syncer_name}.xml ---")
            
            authority_file = AUTHORITY_DIR / f"{syncer_name}.xml"
            
            if not authority_file.exists():
                logger.warning(f"Authority file not found: {authority_file}")
                continue
            
            # Create syncer instance
            syncer_class = SYNCERS[syncer_name]
            syncer = syncer_class(authority_file, TEI_DIR)
            
            # Run sync
            updated, skipped = syncer.sync_all_tei_files(dry_run=args.dry_run)
            total_updated += updated
            total_skipped += skipped
            
            logger.info("")
        
        # Summary
        logger.info("=" * 60)
        logger.info("SUMMARY:")
        logger.info(f"  Total files {'that would be updated' if args.dry_run else 'updated'}: {total_updated}")
        logger.info(f"  Total files skipped: {total_skipped}")
        
        # Next steps
        logger.info("")
        logger.info("NEXT STEPS:")
        if args.dry_run:
            logger.info("  1. Run without --dry-run to apply changes")
            logger.info("  2. python scripts/build-authority-index.py")
        else:
            logger.info("  python scripts/build-authority-index.py")
        logger.info("=" * 60)
        
        logger.info("✓ Done!")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
