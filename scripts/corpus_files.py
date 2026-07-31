#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared corpus file selection for everything that reads tei/ (#287).

Beantwortet an einer Stelle die Frage "welche Dateien sind der Korpus, und in
welcher Reihenfolge". Vorher beantworteten build-corpus-index.py und
sync/extract-variants.py sie unterschiedlich (alle *.tei.xml gegen alle ausser
*.disamb.*), womit ein versehentlich in tei/ liegender Disambiguierungs-
Zwischenstand im Korpus-Index gelandet waere, aber nicht in variants.xml.

Enthaelt ausserdem die Worker-Obergrenze fuer das parallele Parsen: auch das
ist eine Frage der Art "wie liest man den Korpus", und sie stand seit #284
doppelt (Nachtrag zu #287 aus PR #288).

Import-Muster wie tei_namespaces und mhg_normalizer: scripts/ liegt auf
sys.path, wenn die Konsumenten laufen.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEI_DIR = PROJECT_ROOT / 'tei'

# Disambiguierungs-Zwischenstaende (SIG.disamb.tei.xml) sind keine Korpustexte.
# Sie tragen dieselbe idno[@type="sigle"] wie ihre Basisdatei, wuerden also
# jeden nach Sigle geschluesselten Konsumenten doppelt beliefern, ohne dass es
# auffaellt: das Freshness-Gate prueft nur, ob das committete Artefakt zum
# Quellstand passt, und das taete es dann ja. Ihr Platz ist ingest/; in tei/
# liegen sie hoechstens versehentlich (Stand 2026-07-31: keine).
DISAMB_MARKER = '.disamb.'


def corpus_files(tei_dir=None):
    """Die Korpusdateien als sortierte Liste von Path-Objekten.

    Die Reihenfolge ist Teil der Determinismus-Zusicherung aus #125: identischer
    Quellstand muss byte-identische Artefakte erzeugen, und in corpus-index.json
    ist die Schluesselreihenfolge von lemmaIndex die Reihenfolge des
    Erstauftretens ueber genau diese Liste.

    Deshalb zwei Dinge explizit:
    - sortiert, denn die glob-Reihenfolge ist OS-abhaengig;
    - key=p.name statt der Path-Objekte selbst, denn Path vergleicht auf Windows
      casefolded und auf Linux byte-weise. Erst der String-Key macht die Ordnung
      plattformgleich (Review #146).
    """
    base = TEI_DIR if tei_dir is None else Path(tei_dir)
    return sorted((f for f in base.glob('*.tei.xml') if DISAMB_MARKER not in f.name),
                  key=lambda p: p.name)


# Worker-Obergrenze (#284). Nicht cpu_count(): jeder Worker haelt einen
# kompletten lxml-Baum im Speicher, und der Elternprozess muss jedes Ergebnis
# entpicken und behalten (der fertige Korpus-Index sind rund 200 MB JSON).
#
# Gemessen am 2026-07-31 mit build-corpus-index.py, 667 Dateien, 16 Kerne,
# Hash jedes Mal identisch:
#   jobs= 1  183,5 s     jobs= 4   56,1 s     jobs=12   39,9 s
#   jobs= 2   97,9 s     jobs= 8   45,8 s     jobs=16   42,4 s
# Ab 8 ist die Kurve flach, ab 12 kippt sie (Ueberbuchung). Der Rest sind
# rund 16 s Serialisieren und Gzippen, die niemand parallelisiert.
#
# Speicher-Peak ueber alle Python-Prozesse, gleiche Messung:
#   jobs=1  1.344 MB       jobs=8  3.893 MB
# Also rund 320 MB je zusaetzlichem Worker, linear. Bei 16 waeren es ueber
# 6 GB fuer 6 gesparte Sekunden. Deshalb 8: der Grossteil des Gewinns zum
# halben Aufschlag. Wer mehr Kerne als Sorgen hat, nimmt --jobs.
DEFAULT_JOBS_CAP = 8


def default_jobs():
    """Vorgabe fuer --jobs: die Obergrenze, auf kleinen Maschinen die Kernzahl."""
    return min(DEFAULT_JOBS_CAP, os.cpu_count() or 1)
