"""Gemeinsames Schreiben fuer die Frauenlob-Skripte (#236).

`ElementTree.write(..., xml_declaration=True)` verliert den Tail der letzten
Processing Instruction: Wurzelelement und `<?xml-model?>` landen dadurch auf
derselben Zeile. Die uebrigen 663 Korpusdateien und alle Authority-Files haben
dort einen Umbruch; ohne Nachlauf zeigt jeder kuenftige Diff eine Phantomzeile
ganz oben, und bei `works.xml` klebten sogar beide PIs plus die Wurzel
aneinander.

Der Nachlauf arbeitet bewusst nur auf den ersten Zeilen, also im Prolog. Ein
globales Ersetzen von `?><` wuerde auch Processing Instructions im Dokument
treffen, und die duerfen sehr wohl ohne Umbruch an ein Element grenzen.
"""

from pathlib import Path

# Der Prolog ist eine Deklaration plus hoechstens zwei xml-model-PIs. Drei
# Zeilen sind die Obergrenze dafuer, egal wie stark der Writer sie zusammenzieht.
PROLOG_ZEILEN = 3


def write_tei(tree, path):
    """Schreibt den Baum und stellt die Zeilenumbrueche im Prolog wieder her."""
    path = Path(path)
    tree.write(str(path), encoding="UTF-8", xml_declaration=True)

    roh = path.read_bytes()
    zeilen = roh.split(b"\n")
    kopf = [z.replace(b"?><", b"?>\n<") for z in zeilen[:PROLOG_ZEILEN]]
    neu = b"\n".join(kopf + zeilen[PROLOG_ZEILEN:])
    if neu != roh:
        path.write_bytes(neu)
