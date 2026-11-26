"""druck_quelle.py: Quellen des Druckfahnen-Gates der Weingruesse (BRE, #147, #743).

Importierbar (test_bre.py und druckfahnen-gate.py nutzen es), liest die geschuetzten Texte nur
im Speicher, schreibt nichts davon in eine Datei. Der Kern (n-Gramme, Treffer, Push-Texte) steht in
scripts/audit/wortlaut_gate.py.

geschuetzt(): Text der Hirzel-Druckfahnen (PDF, per pdftotext auf stdout, Silbentrennung am
Zeilenende zusammengezogen) und Silvans Word-Steckbriefe von 2022 (docling/*.md).
erlaubt(): die Wiki-Fassung (Cache temp/bre-wiki, roh und ohne Markup) und der Wortlaut der
Zeugen in ingest/bre.
Ort der geschuetzten Quellen: Umgebungsvariable BRE_DRUCK_QUELLEN=<ordner>, der die PDF
wagner-2023-weingruesse-druckfahnen.pdf und docling/ enthaelt (kein Fallback, wenn sie
gesetzt und der Ordner unvollstaendig ist). Ohne sie: sources/weingruesse im Repo, dann im
Main Worktree (Parent des git-common-dir).
"""
import html as _html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(HIER.parents[1] / "audit"))
import bre_common as bc  # noqa: E402
from wortlaut_gate import NichtMoeglich  # noqa: E402

N = 6
PDF_NAME = "wagner-2023-weingruesse-druckfahnen.pdf"
ENV_QUELLEN = "BRE_DRUCK_QUELLEN"


def wiki_klartext(inhalt):
    # Markup weg, sonst zerlegt <span ...>N</span>u ein Wort und der Vers zaehlt nicht als Wiki-Text
    t = re.sub(r"<[^>]+>|'{2,}", "", _html.unescape(inhalt))
    return re.sub(r"\[\[|\]\]|\{\{|\}\}|\|", " ", t)


def _quellordner():
    def vollstaendig(p):
        return (p / "docling").is_dir() and (p / PDF_NAME).is_file()
    vorgabe = os.environ.get(ENV_QUELLEN)
    if vorgabe:
        p = Path(vorgabe)
        if not vollstaendig(p):
            raise NichtMoeglich(f"{ENV_QUELLEN}={vorgabe} enthaelt nicht die PDF und docling/")
        return p
    try:
        common = subprocess.run(["git", "-C", str(bc.REPO), "rev-parse", "--path-format=absolute",
                                 "--git-common-dir"], capture_output=True, text=True).stdout.strip()
    except OSError:
        common = ""
    kandidaten = [bc.REPO / "sources" / "weingruesse"]
    if common:
        kandidaten.append(Path(common).parent / "sources" / "weingruesse")
    for p in kandidaten:
        if vollstaendig(p):
            return p
    raise NichtMoeglich("Druckfahnen-PDF und Steckbriefe (sources/weingruesse) nicht gefunden")


def geschuetzt():
    """Texte der Druckfahnen (PDF) und der Steckbriefe; NichtMoeglich, wenn etwas fehlt."""
    basis = _quellordner()
    try:
        pdf = subprocess.run(["pdftotext", "-enc", "UTF-8", str(basis / PDF_NAME), "-"],
                             capture_output=True, check=True).stdout.decode("utf-8")
    except (OSError, subprocess.CalledProcessError) as e:
        raise NichtMoeglich(f"pdftotext scheitert ({type(e).__name__})")
    pdf = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", pdf)
    if len(pdf) < 100000:  # Plausibilitaet: der Textauszug hat rund 189 KB
        raise NichtMoeglich("Textauszug der Druckfahnen unplausibel kurz")
    return [pdf] + [md.read_text(encoding="utf-8") for md in sorted((basis / "docling").glob("*.md"))]


def erlaubt():
    """Texte, deren Wortlaut im Repo stehen darf: Wiki-Fassung (roh und ohne Markup) und Zeugen."""
    wiki = sorted(bc.CACHE_DIR.glob("rev_*.json")) if bc.CACHE_DIR.is_dir() else []
    if not wiki:
        raise NichtMoeglich("Wiki-Cache (temp/bre-wiki) fehlt")
    texte = []
    for j in wiki:
        inhalt = json.loads(j.read_text(encoding="utf-8"))["inhalt"]
        texte += [inhalt, wiki_klartext(inhalt)]
    from lxml import etree
    for tei in sorted(bc.INGEST_DIR.glob("BRE_*.tei.xml")):
        ws = etree.parse(str(tei)).getroot().iter("{http://www.tei-c.org/ns/1.0}w")
        texte.append(" ".join("".join(w.itertext()) for w in ws))
    return texte


def zaehlen():
    """(druck, erlaubt, verboten): Zahl der n-Gramme je Menge, nur Zahlen."""
    import wortlaut_gate as wg
    druck = set()
    for t in geschuetzt():
        druck |= wg.ngramme(wg.woerter(t), N)
    erl = set()
    for t in erlaubt():
        erl |= wg.ngramme(wg.woerter(t), N)
    return len(druck), len(erl), len(druck - erl)


def pruefung():
    """Fahrt das Gate: (Zahl Dateien, Zahl Commit-Texte, Zahl weiterer Texte, Treffer).
    Wirft NichtMoeglich, wenn sich etwas nicht pruefen laesst."""
    import wortlaut_gate as wg
    verbotene = wg.verboten(geschuetzt(), erlaubt(), N)
    dat = dateien()
    push = wg.push_texte(bc.REPO)
    zusatz = wg.zusatz_texte("BRE_DRUCK_PRUEFE")
    treffer = []
    for d in dat:
        treffer += wg.treffer_in_text(str(d), d.read_text(encoding="utf-8", errors="replace"),
                                      verbotene, N, tsv=d.suffix == ".tsv")
    for name, text, tsv in push:
        treffer += wg.treffer_in_text(name, text, verbotene, N, tsv=tsv)
    for name, text in zusatz:
        treffer += wg.treffer_in_text(name, text, verbotene, N)
    return len(dat), len(push), len(zusatz), treffer


def dateien():
    """Scope der Dateipruefung: alles Textartige unter ingest/bre und scripts/ingest/bre."""
    return [p for basis in (bc.INGEST_DIR, HIER) for p in sorted(basis.rglob("*"))
            if p.is_file() and p.suffix in {".tsv", ".md", ".py", ".xml", ".txt", ".json", ".html"}]
