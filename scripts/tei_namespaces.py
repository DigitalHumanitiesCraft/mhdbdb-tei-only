#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared TEI namespace detection for lxml trees (#171 F97).

Was previously copy-pasted in build-corpus-index.py,
build-authority-index.py and scripts/ingest/wzb/wzb-auto-match.py;
this module is the single implementation. Import pattern follows
mhg_normalizer (scripts/ is on sys.path when the consumers run).
"""

TEI_NS_URI = 'http://www.tei-c.org/ns/1.0'


def get_namespaces(tree):
    """
    Detect and return all namespaces in document (Critical Fix #2).

    Handles default namespaces and unprefixed elements: the default
    namespace is re-exposed under the 'tei' prefix so XPath queries
    using 'tei:' work regardless of how the source file declares it.
    """
    nsmap = tree.getroot().nsmap.copy()

    # Move default namespace to 'tei' prefix
    if None in nsmap:
        nsmap['tei'] = nsmap[None]
        del nsmap[None]

    # Ensure TEI namespace exists
    if 'tei' not in nsmap:
        nsmap['tei'] = TEI_NS_URI

    return nsmap
