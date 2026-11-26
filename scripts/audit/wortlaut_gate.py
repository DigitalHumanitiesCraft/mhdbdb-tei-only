"""wortlaut_gate.py: quellenunabhaengiger Kern eines Wortlaut-Gates (#743).

Ein Gate dieser Art sorgt dafuer, dass kein Wortlaut aus einer geschuetzten Quelle (etwa einer
Druckfassung) im Repository oder in dem steht, was ein Push traegt. Dieses Modul liest selbst
keine geschuetzte Quelle: der Aufrufer liefert deren Texte, dazu die Texte, die ausdruecklich
erlaubt sind (lizenzierte Fassung, Wortlaut der Zeugen).

Gesucht wird jede Folge von n Woertern aus den geschuetzten Texten, die in keinem erlaubten
Text vorkommt ("verboten"), in den zu pruefenden Texten. Geprueft wird:
- Dateien und weitere Texte, die der Aufrufer reicht (`treffer_in_text`),
- fuer einen Push: die Commit Message und die hinzugefuegten Zeilen jedes Commits seit dem
  merge-base mit `origin/main` (`push_texte`), nicht der Rest der Dateien.

Nicht erfasst sind Folgen unter n Woertern, Paraphrasen und Ziffern (eine Jahreszahl allein ist
kein Wortlaut). URLs fallen auf beiden Seiten weg, Folgen aus lauter Ein-Buchstaben-Woertern
(Siglenlisten) auch.

Das Gate ist fail-closed: laesst sich etwas nicht pruefen (merge-base leer, ein git-Call
scheitert, eine genannte Datei fehlt), wirft es `NichtMoeglich`, nie still eine leere Liste.
"""
import os
import re
import subprocess
import unicodedata
from pathlib import Path


class NichtMoeglich(Exception):
    """Die Pruefung laesst sich nicht fahren; der Grund steht in der Meldung."""


def woerter(text):
    # Diakritika (auch die uebergeschriebenen e/o der Handschriften) fallen auf beiden Seiten weg,
    # sonst zerlegen sie ein Wort und eine Folge der erlaubten Fassung sieht aus wie eine der
    # geschuetzten
    text = re.sub(r"https?://\S+", " ", text)
    roh = unicodedata.normalize("NFKD", text.lower())
    return re.findall(r"[^\W\d_]+", "".join(c for c in roh if not unicodedata.combining(c)))


def ngramme(ws, n):
    return {g for g in (tuple(ws[i:i + n]) for i in range(len(ws) - n + 1))
            if any(len(w) > 1 for w in g)}


def verboten(geschuetzt_texte, erlaubt_texte, n):
    """Folgen von n Woertern, die in den geschuetzten, aber in keinem erlaubten Text stehen."""
    geschuetzt = set()
    for t in geschuetzt_texte:
        geschuetzt |= ngramme(woerter(t), n)
    erlaubt = set()
    for t in erlaubt_texte:
        erlaubt |= ngramme(woerter(t), n)
    return geschuetzt - erlaubt


def treffer_in_text(name, text, verbotene, n, tsv=False):
    """[(name, folge)] fuer jede verbotene Folge im Text; TSV je Feld (Split an Tab und Zeilenende)."""
    # eine Folge ueber die Spaltengrenze (etwa Blatt + Incipit) ist keine Stelle
    teile = re.split(r"[\t\n]", text) if tsv else [text]
    gefunden = set()
    for t in teile:
        gefunden |= ngramme(woerter(t), n) & verbotene
    return [(name, " ".join(g)) for g in sorted(gefunden)]


def _git(repo, *args):
    try:
        r = subprocess.run(["git", "-c", "core.quotepath=off", "-C", str(repo), *args],
                           capture_output=True)
    except OSError as e:
        raise NichtMoeglich(f"git nicht aufrufbar ({e})")
    if r.returncode != 0:
        raise NichtMoeglich(f"git {' '.join(args[:2])} schlug fehl (Exit {r.returncode})")
    return r.stdout.decode("utf-8", errors="replace")


def push_texte(repo, basis="origin/main"):
    """[(name, text, tsv)]: je Commit seit merge-base(HEAD, basis) die Commit Message und die
    hinzugefuegten Zeilen je Datei (ein Text je Datei und Commit)."""
    merge_base = _git(repo, "merge-base", "HEAD", basis).strip()
    if not merge_base:
        raise NichtMoeglich(f"merge-base mit {basis} ist leer")
    log = _git(repo, "log", "-p", "--format=%x01%H%x00%B%x02", f"{merge_base}..HEAD")
    texte = []
    for eintrag in log.split("\x01"):
        if "\x00" not in eintrag:
            continue
        sha, rest = eintrag.split("\x00", 1)
        sha9 = sha[:9]
        nachricht, _, patch = rest.partition("\x02")
        texte.append((f"Commit {sha9}", nachricht, False))
        pfad, zeilen, im_hunk = None, [], False

        def abschluss():
            if pfad is not None and zeilen:
                texte.append((f"Commit {sha9} {pfad}", "\n".join(zeilen), pfad.endswith(".tsv")))
        for z in patch.split("\n"):
            if z.startswith("diff --git "):
                abschluss()
                pfad, zeilen, im_hunk = None, [], False
            elif not im_hunk and z.startswith("+++ "):
                ziel = z[4:].rstrip("\r")
                pfad = ziel[2:] if ziel.startswith("b/") else None  # /dev/null: Datei geloescht
            elif z.startswith("@@"):
                im_hunk = True
            elif im_hunk and z.startswith("+"):
                zeilen.append(z[1:])
        abschluss()
    return texte


def zusatz_texte(env_var):
    """[(pfad, text)] aus den Dateien einer ;-getrennten Umgebungsvariable (PR-Body, Kommentar)."""
    texte = []
    for p in filter(None, os.environ.get(env_var, "").split(";")):
        datei = Path(p)
        if not datei.is_file():
            raise NichtMoeglich(f"Datei aus {env_var} fehlt: {p}")
        texte.append((p, datei.read_text(encoding="utf-8")))
    return texte
