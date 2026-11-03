"""bre_wikitext.py: Wikitext-Helfer des BRE-Ingests (Weingruesse, #147).

Gemeinsam fuer 01 (Synopse -> erster Vers) und 02 (Transkription -> TEI):
beide muessen einen Vers auf dieselbe Weise zu Vergleichszwecken bereinigen.
"""
import html
import re

RE_FOLIO = re.compile(r"\[(\d+[rv]?[a-d]?)\]")
RE_REF = re.compile(r"<ref\b[^>]*?/>|<ref\b[^>]*>.*?</ref>", re.S)
RE_TAG_BEKANNT = re.compile(
    r"</?(?:span|s|u|del|sup|br|ref|references)\b[^>]*?/?>", re.I)
RE_ROT_GANZ = re.compile(r'^\s*<span style="color:#FF0000">(.*)</span>\s*(?:<br\s*/?>)?\s*$', re.S)


def vergleichstext(zeile):
    """Zeile fuer den Vergleich erster Vers <-> Transkription bereinigen.

    Entfernt Anmerkungen, bekannte HTML-Tags, Wikifettdruck, Folio-Marker und
    <br />; loest numerische Entities auf; normalisiert Leerraum. Rohe
    Spitzklammern (editorische Ergaenzungen) bleiben stehen. Kombinierende
    Diakritika werden nicht normalisiert.
    """
    z = RE_REF.sub("", zeile)
    z = html.unescape(z)
    z = RE_TAG_BEKANNT.sub("", z)
    z = z.replace("'''", "").replace("''", "")
    z = RE_FOLIO.sub("", z)
    return re.sub(r"\s+", " ", z).strip()
