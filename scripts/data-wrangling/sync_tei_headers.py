#!/usr/bin/env python3
"""
Sync TEI Headers from Authority Files

General-purpose tool for synchronizing authority data to TEI file headers.
Reads from authority-files/*.xml and updates corresponding TEI file headers.

Supported authority files:
- works.xml: Syncs <editor> elements to TEI headers
- persons.xml: (Future) Syncs author/person metadata
- genres.xml: (Future) Syncs genre classifications
- concepts.xml: (Future) Syncs concept annotations
- [Add more as needed]

Usage:
    # Sync all authority files
    python scripts/data-wrangling/sync_tei_headers.py --all [--dry-run]
    
    # Sync specific authority file
    python scripts/data-wrangling/sync_tei_headers.py --works [--dry-run]
    python scripts/data-wrangling/sync_tei_headers.py --persons [--dry-run]
    
    # Sync multiple specific files
    python scripts/data-wrangling/sync_tei_headers.py --works --persons [--dry-run]

Examples:
    # Preview changes from all authority files
    python scripts/data-wrangling/sync_tei_headers.py --all --dry-run
    
    # Sync only works.xml (Issue #19)
    python scripts/data-wrangling/sync_tei_headers.py --works
    
After running:
    python scripts/build-authority-index.py  # Rebuild index
"""

import sys
import argparse
import logging
from pathlib import Path
from lxml import etree
from typing import Dict, List, Set
from abc import ABC, abstractmethod

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File paths
AUTHORITY_DIR = Path("authority-files")
TEI_DIR = Path("tei")

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
        tei_files = sorted(self.tei_dir.glob("*.tei.xml"))
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


class WorksEditorSyncer(AuthoritySyncer):
    """Syncs <editor> elements from works.xml"""
    
    def load_authority_data(self) -> Dict[str, List[str]]:
        """Load editor data from works.xml. Returns sigle → [editor names]."""
        sigle_to_editors = {}
        
        tree = etree.parse(str(self.authority_file))
        root = tree.getroot()
        
        # Find all work entries
        works = root.xpath('//tei:bibl[starts-with(@xml:id, "work_")]', namespaces=TEI_NS)
        
        for work in works:
            # Get sigle
            sigle_elem = work.xpath('.//tei:idno[@type="sigle"]', namespaces=TEI_NS)
            if not sigle_elem:
                continue
            
            sigle = sigle_elem[0].text
            if not sigle:
                continue
            
            # Get editors from first biblStruct
            biblstructs = work.xpath('.//tei:biblStruct', namespaces=TEI_NS)
            if not biblstructs:
                continue
            
            editors = biblstructs[0].xpath('.//tei:editor', namespaces=TEI_NS)
            editor_names = [e.text for e in editors if e.text]
            
            if editor_names:
                sigle_to_editors[sigle] = editor_names
                logger.debug(f"Works: {sigle} → {len(editor_names)} editor(s)")
        
        return sigle_to_editors
    
    def update_tei_header(self, tei_tree: etree._ElementTree, sigle: str, 
                         data: List[str], dry_run: bool) -> bool:
        """Update <editor> elements in TEI header."""
        root = tei_tree.getroot()
        
        # Find titleStmt in teiHeader
        title_stmt = root.xpath('//tei:teiHeader//tei:titleStmt', namespaces=TEI_NS)
        if not title_stmt:
            logger.warning(f"[works] {sigle}: No titleStmt found")
            return False
        
        title_stmt = title_stmt[0]
        
        # Remove existing editor elements
        for old_editor in title_stmt.xpath('.//tei:editor', namespaces=TEI_NS):
            if not dry_run:
                old_editor.getparent().remove(old_editor)
        
        # Add new editor elements
        if not dry_run:
            for editor_name in data:
                editor_elem = etree.Element(f"{{{TEI_NS_URI}}}editor")
                editor_elem.text = editor_name
                title_stmt.append(editor_elem)
        
        logger.debug(f"[works] {sigle}: {'Would add' if dry_run else 'Added'} {len(data)} editor(s)")
        return True


class PersonsSyncer(AuthoritySyncer):
    """Syncs person/author data from persons.xml"""
    
    def load_authority_data(self) -> Dict:
        """Load person data from persons.xml. Returns person_id → person data."""
        # TODO: Implement when needed
        logger.info(f"[{self.name}] Not yet implemented")
        return {}
    
    def update_tei_header(self, tei_tree: etree._ElementTree, sigle: str, 
                         data: any, dry_run: bool) -> bool:
        """Update person/author data in TEI header."""
        # TODO: Implement when needed
        return False


class GenresSyncer(AuthoritySyncer):
    """Syncs genre classifications from genres.xml"""
    
    def load_authority_data(self) -> Dict:
        """Load genre data from genres.xml."""
        # TODO: Implement when needed
        logger.info(f"[{self.name}] Not yet implemented")
        return {}
    
    def update_tei_header(self, tei_tree: etree._ElementTree, sigle: str, 
                         data: any, dry_run: bool) -> bool:
        """Update genre classifications in TEI header."""
        # TODO: Implement when needed
        return False


class ConceptsSyncer(AuthoritySyncer):
    """Syncs concept annotations from concepts.xml"""
    
    def load_authority_data(self) -> Dict:
        """Load concept data from concepts.xml."""
        # TODO: Implement when needed
        logger.info(f"[{self.name}] Not yet implemented")
        return {}
    
    def update_tei_header(self, tei_tree: etree._ElementTree, sigle: str, 
                         data: any, dry_run: bool) -> bool:
        """Update concept annotations in TEI header."""
        # TODO: Implement when needed
        return False


# Registry of available syncers
SYNCERS = {
    'works': WorksEditorSyncer,
    'persons': PersonsSyncer,
    'genres': GenresSyncer,
    'concepts': ConceptsSyncer,
}


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description='Sync TEI headers with authority file data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync all authority files
  python scripts/data-wrangling/sync_tei_headers.py --all
  
  # Sync only works.xml (for Issue #19)
  python scripts/data-wrangling/sync_tei_headers.py --works
  
  # Preview changes before applying
  python scripts/data-wrangling/sync_tei_headers.py --works --dry-run
  
  # Sync multiple specific files
  python scripts/data-wrangling/sync_tei_headers.py --works --persons
        """
    )
    
    # Authority file selection
    parser.add_argument('--all', action='store_true',
                       help='Sync all authority files')
    parser.add_argument('--works', action='store_true',
                       help='Sync works.xml (editor data)')
    parser.add_argument('--persons', action='store_true',
                       help='Sync persons.xml (author data) [NOT YET IMPLEMENTED]')
    parser.add_argument('--genres', action='store_true',
                       help='Sync genres.xml (genre classifications) [NOT YET IMPLEMENTED]')
    parser.add_argument('--concepts', action='store_true',
                       help='Sync concepts.xml (concept annotations) [NOT YET IMPLEMENTED]')
    
    # Options
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')
    
    args = parser.parse_args()
    
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
