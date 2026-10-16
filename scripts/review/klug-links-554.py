# -*- coding: utf-8 -*-
"""Klug-Verweise (#554): Pruefliste Lemma x Pflanzenseite. Aendert nichts im Repo.

Aufruf:
    python scripts/review/klug-links-554.py --aus ORDNER [--nur-urteile] [--seiten ORDNER]

Phase 1 (ohne --nur-urteile): Kandidaten bilden, Lexikon, Konzepte, Korpusbelege, Seiten
  holen (curl ueber http, sequenziell, 1 s Pause, Cache im Seitenordner), Dossier nach
  dossier.txt im Ausgabeordner. Braucht Netz.
Phase 2: klug-links.tsv schreiben, aus klug-urteile.tsv im Repo (ingest/glossar-554/).
  Mit --nur-urteile laeuft nur diese Phase, ohne Netz: der Seitentitel kommt dann aus dem
  Seitenordner, wenn die Seite dort liegt, sonst aus der vorhandenen klug-links.tsv (die
  Spalte pflanzenseite_titel, nach Kennung). Fehlt er auch dort, bricht der Lauf ab.
klug-urteile.tsv: lemma_id, kennung, urteil, begruendung, belege_ids (Tab-getrennt, Eingabe,
  Urteile eines Agenten; keine CSV-Anfuehrungszeichen, ein " im Text ist ein "). Urteil nur
  passt, passt nicht oder unklar; ein Paar nur einmal; vier oder fuenf Felder. Sonst bricht
  der Lauf ab.

--aus ORDNER    Pflicht. Ausgabeordner fuer klug-links.tsv und dossier.txt; darf nicht im Repo
                liegen, ausser unter temp/ (gitignoriert). Wer die eingecheckte
                klug-links.tsv erneuern will, vergleicht und kopiert bewusst.
--seiten ORDNER Seitencache (Standard: temp/klug-seiten, gitignoriert)
"""
import csv
from collections import Counter
import html
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GLOSSAR = os.path.join(REPO, "ingest", "glossar-554")


def _arg(name, std):
    if name in sys.argv:
        return os.path.abspath(sys.argv[sys.argv.index(name) + 1])
    return std


URTEIL_WORTE = {"passt", "passt nicht", "unklar"}
NUR_URTEILE = "--nur-urteile" in sys.argv
OUT = _arg("--aus", None)
if OUT is None:
    sys.exit("FEHLER: --aus ORDNER fehlt (Ausgabeordner, nicht im Repo ausser unter temp/)")
_o, _r = os.path.realpath(OUT), os.path.realpath(REPO)
if (_o == _r or _o.startswith(_r + os.sep)) and not _o.startswith(os.path.join(_r, "temp") + os.sep):
    sys.exit("FEHLER: Ausgabeordner liegt im Repo (erlaubt nur unter temp/): " + OUT)
os.makedirs(OUT, exist_ok=True)
SEITEN = _arg("--seiten", os.path.join(REPO, "temp", "klug-seiten"))
PFL = os.path.join(GLOSSAR, "klug-pflanzen.tsv")
ABG = os.path.join(GLOSSAR, "klug-abgleich.tsv")
URT = os.path.join(GLOSSAR, "klug-urteile.tsv")
LEX = os.path.join(REPO, "authority-files", "lexicon.xml")
CON = os.path.join(REPO, "authority-files", "concepts.xml")
TEI = os.path.join(REPO, "tei")
BASE = "http://medieval-plants.org/mps-daten/mps_entry/"


def lies(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def kandidaten():
    paare = {}  # (lemma_id, kennung) -> dict
    with open(PFL, encoding="utf-8", newline="") as f:
        rd = csv.DictReader(f, delimiter="\t")
        for r in rd:
            ul = r["unser_lemma"].strip()
            if not ul:
                continue
            orth, lid = ul.rsplit(" ", 1)
            assert lid.startswith("lemma_"), ul
            k = (lid, r["pflanzenseite"])
            d = paare.setdefault(k, {"lemma_id": lid, "orth": orth, "kennung": r["pflanzenseite"],
                                     "url": r["pflanzenseite_url"], "mhd": [], "vergl": set(), "quelle": "pflanzen"})
            d["mhd"].append(r["mhd_name"])
            d["vergl"].add(r["vergleich"])
    n_pfl = len(paare)
    n_zeilen = sum(len(d["mhd"]) for d in paare.values())
    # Kontrollwert aus klug-abgleich.tsv
    gefunden = False
    with open(ABG, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["slug"].startswith("brestelinc") and r["lemma_id"] == "lemma_26984":
                gefunden = True
                k = ("lemma_26984", "gartenerdbeere")
                paare[k] = {"lemma_id": "lemma_26984", "orth": r["lemma"], "kennung": "gartenerdbeere",
                            "url": BASE + "gartenerdbeere/", "mhd": [r["titel"]], "vergl": {"Kontrollwert KZW"},
                            "quelle": "abgleich"}
    if not gefunden:
        sys.exit("brestelinc nicht in klug-abgleich.tsv gefunden")
    print("Zeilen mit unser_lemma:", n_zeilen, "-> Paare Lemma x Pflanzenseite:", n_pfl,
          "; plus brestelinc/gartenerdbeere =", len(paare))
    return paare


def konzepte():
    t = lies(CON)
    d = {}
    for m in re.finditer(r'<category xml:id="(concept_\d+)">(.*?)</category>', t, re.S):
        de = re.search(r'<term xml:lang="de">(.*?)</term>', m.group(2))
        br = re.search(r'type="broader" target="#(concept_\d+)"', m.group(2))
        d[m.group(1)] = (html.unescape(de.group(1)) if de else "?", br.group(1) if br else "")
    return d


def lexikon(lid, kon):
    t = lies(LEX)
    m = re.search(r'<entry xml:id="%s">(.*?)</entry>' % lid, t, re.S)
    if not m:
        return None
    e = m.group(1)
    orth = re.search(r"<orth>(.*?)</orth>", e).group(1)
    pos = re.findall(r"<pos>(.*?)</pos>", e)
    senses = []
    for s in re.finditer(r'<sense xml:id="([^"]+)"[^>]*>(.*?)</sense>', e, re.S):
        notiz = re.search(r"<note[^>]*>(.*?)</note>", s.group(2), re.S)
        cs = re.findall(r'concepts\.xml#(concept_\d+)', s.group(2))
        ketten = []
        for c in cs:
            lab = kon.get(c, ("?", ""))[0]
            br = kon.get(c, ("?", ""))[1]
            lab_br = kon.get(br, ("", ""))[0] if br else ""
            ketten.append("%s=%s%s" % (c.replace("concept_", ""), lab, (" < " + lab_br) if lab_br else ""))
        senses.append((s.group(1), html.unescape(notiz.group(1))[:400] if notiz else "", ketten))
    return orth, pos, senses


def korpus(lids):
    pat = {l: re.compile(r'lemmaRef="([^"]*)"') for l in lids}
    hits = {l: [] for l in lids}
    for fn in sorted(os.listdir(TEI)):
        if not fn.endswith(".tei.xml"):
            continue
        zeilen = lies(os.path.join(TEI, fn)).split("\n")
        for i, z in enumerate(zeilen):
            if "<w " not in z or "lemmaRef" not in z:
                continue
            m = re.search(r'lemmaRef="([^"]*)"', z)
            toks = [x.split("#")[-1] for x in m.group(1).split()]
            for l in lids:
                if l in toks:
                    hits[l].append((fn[:-8], i, zeilen))
    return hits


def kontext(zeilen, i, lid):
    """Text der Vers-/Satzumgebung: bis zu 10 Zeilen davor und danach, Treffer in [[ ]]."""
    out = []
    for j in range(max(0, i - 10), min(len(zeilen), i + 11)):
        z = zeilen[j]
        m = re.match(r'\s*<(w|pc)\b[^>]*>(.*?)</\1>', z)
        if not m:
            continue
        w = html.unescape(m.group(2))
        if j == i:
            w = "[[" + w + "]]"
        out.append(w)
    return " ".join(out)


def wid(z):
    return re.search(r'xml:id="([^"]+)"', z).group(1)


def seite(kennung, url):
    os.makedirs(SEITEN, exist_ok=True)
    p = os.path.join(SEITEN, kennung + ".html")
    if not os.path.exists(p):
        time.sleep(1)
        r = subprocess.run(["curl", "-s", "--max-time", "30", "-A", "mhdbdb-pruefung (christian.steiner@dhcraft.org)",
                            "-o", p, "-w", "%{http_code}", url], capture_output=True, text=True)
        print("curl", url, "->", r.stdout, r.stderr.strip())
        if r.stdout.strip() != "200":
            sys.exit("Abruf nicht 200, Abbruch: " + url + " " + r.stdout)
    t = lies(p)
    ti = re.search(r"<title>(.*?)</title>", t, re.S)
    return html.unescape(ti.group(1)).strip() if ti else "?", t


def mhd_aus_seite(t):
    """Grobe Textsicht der Seite fuer das Dossier (nur Anzeige, nichts wird gespeichert)."""
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(re.sub(r"\s+", " ", t))
    i = t.find("Mittelhochdeutsch")
    return t[max(0, i - 50):i + 600] if i >= 0 else "(kein 'Mittelhochdeutsch' im Text) " + t[:300]


def phase1(paare):
    kon = konzepte()
    lids = sorted({d["lemma_id"] for d in paare.values()})
    hits = korpus(lids)
    zeilen_aus = []
    titel = {}
    for k in sorted(paare, key=lambda x: (x[0], x[1])):
        d = paare[k]
        lex = lexikon(d["lemma_id"], kon)
        ti, t = seite(d["kennung"], d["url"])
        titel[k] = ti
        h = hits[d["lemma_id"]]
        texte = sorted({x[0] for x in h})
        zeilen_aus.append("=" * 70)
        zeilen_aus.append("%s | %s | Seite %s (%s)" % (d["lemma_id"], d["orth"], d["kennung"], ti))
        zeilen_aus.append("mhd. Namen dort: %s | Vergleich: %s | Quelle: %s" % (", ".join(d["mhd"]), ",".join(sorted(d["vergl"])), d["quelle"]))
        zeilen_aus.append("Seite: " + mhd_aus_seite(t))
        if lex:
            zeilen_aus.append("Lexikon: orth=%s pos=%s" % (lex[0], lex[1]))
            for sid, notiz, ketten in lex[2]:
                zeilen_aus.append("  Sense %s: %s" % (sid, "; ".join(ketten)))
                if notiz:
                    zeilen_aus.append("    Notiz: " + notiz.replace("\n", " "))
        zeilen_aus.append("Belege: %d Stellen in %d Texten" % (len(h), len(texte)))
        # bis zu 5 Belege, gleichmaessig ueber die Texte gestreut
        pick = []
        gesehen = set()
        schritt = max(1, len(h) // 5)
        for idx in range(0, len(h), schritt):
            if h[idx][0] in gesehen and len(pick) < 5 and len(texte) > 5:
                continue
            gesehen.add(h[idx][0])
            pick.append(h[idx])
            if len(pick) == 5:
                break
        for tx, i, zl in pick:
            ana = re.search(r'ana="lexicon.xml#([^"]+)"', zl[i])
            zeilen_aus.append("  %s %s ana=%s: %s" % (tx, wid(zl[i]), ana.group(1) if ana else "-", kontext(zl, i, d["lemma_id"])))
        # Vertiefung: Formen, Sense-Verteilung, bis zu 3 Belege je Sense, Pflanzenwort-Naehe
        fc = Counter()
        sc = Counter()
        je_sense = {}
        for tx, i, zl in h:
            m2 = re.match(r'\s*<w\b[^>]*>(.*?)</w>', zl[i])
            fc[html.unescape(m2.group(1)).lower() if m2 else "?"] += 1
            a2 = re.search(r'ana="lexicon.xml#([^"]+)"', zl[i])
            sk = a2.group(1) if a2 else "-"
            sc[sk] += 1
            je_sense.setdefault(sk, []).append((tx, i, zl))
        zeilen_aus.append("  Formen: " + ", ".join("%s %d" % x for x in fc.most_common(10)))
        zeilen_aus.append("  Senses (ana): " + ", ".join("%s %d" % x for x in sc.most_common()))
        for sk, lst in je_sense.items():
            for tx, i, zl in lst[:: max(1, len(lst) // 3)][:3]:
                zeilen_aus.append("  [%s] %s %s: %s" % (sk, tx, wid(zl[i]), kontext(zl, i, d["lemma_id"])))
        if d["lemma_id"] in ("lemma_3414", "lemma_9099"):
            pw = re.compile(r"krût|kraut|wurz|minze|salbe|blume|bluome|dost|wise|gras|stengel|bletter|pleter|blat", re.I)
            nn = 0
            for tx, i, zl in h:
                k = kontext(zl, i, d["lemma_id"])
                if pw.search(k):
                    nn += 1
                    if nn <= 8:
                        zeilen_aus.append("  Pflanzenwort-Naehe: %s %s: %s" % (tx, wid(zl[i]), k))
            zeilen_aus.append("  Treffer mit Pflanzenwort in Naehe: %d von %d" % (nn, len(h)))
            zeilen_aus.append("  davon pos=NOM: %d" % len([x for x in h if 'pos="NOM"' in x[2][x[1]]]))
    with open(os.path.join(OUT, "dossier.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(zeilen_aus) + "\n")
    return titel, hits


def titel_offline(paare):
    """Seitentitel ohne Netz: aus dem Seitencache, sonst aus der vorhandenen klug-links.tsv."""
    alt = {}
    pv = os.path.join(OUT, "klug-links.tsv")
    if not os.path.exists(pv):
        pv = os.path.join(GLOSSAR, "klug-links.tsv")
    if os.path.exists(pv):
        with open(pv, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                alt[r["kennung"]] = r["pflanzenseite_titel"]
    titel = {}
    for k, d in paare.items():
        p = os.path.join(SEITEN, d["kennung"] + ".html")
        if os.path.exists(p):
            ti = re.search(r"<title>(.*?)</title>", lies(p), re.S)
            titel[k] = html.unescape(ti.group(1)).strip() if ti else "?"
        elif "mps:" + d["kennung"] in alt:
            # die gespeicherte Spalte ist schon gekuerzt; die Kuerzung ist idempotent
            titel[k] = alt["mps:" + d["kennung"]]
        else:
            sys.exit("kein Seitentitel ohne Netz fuer " + d["kennung"] + ": Phase 1 laufen lassen")
    return titel


def phase2(paare, titel, hits):
    p = URT
    if not os.path.exists(p):
        print("klug-urteile.tsv fehlt: nur Phase 1")
        return
    kon = konzepte()
    urteile = {}
    # Reine Tab-Trennung ohne CSV-Anfuehrungszeichen: ein " im Text bleibt ein "
    with open(p, encoding="utf-8", newline="") as f:
        for nr, zeile in enumerate(f.read().split("\n"), 1):
            if not zeile.strip() or zeile.startswith("#"):
                continue
            r = zeile.rstrip("\r").split("\t")
            if len(r) not in (4, 5):
                sys.exit("klug-urteile.tsv Zeile %d: %d statt 4 bis 5 Felder" % (nr, len(r)))
            if r[2] not in URTEIL_WORTE:
                sys.exit("klug-urteile.tsv Zeile %d: unbekanntes Urteil %r (erlaubt: %s)" % (nr, r[2], ", ".join(sorted(URTEIL_WORTE))))
            if (r[0], r[1]) in urteile:
                sys.exit("klug-urteile.tsv Zeile %d: Paar doppelt: %s %s" % (nr, r[0], r[1]))
            urteile[(r[0], r[1])] = r
    fehlt = [k for k in paare if k not in urteile]
    zuviel = [k for k in urteile if k not in paare]
    if fehlt or zuviel:
        sys.exit("Urteile passen nicht zu den Kandidaten: fehlt %s, zuviel %s" % (fehlt, zuviel))
    zaehl = {}
    os.makedirs(OUT, exist_ok=True)
    kopf = ["lemma_id", "orth", "pflanzenseite_titel", "kennung", "url", "urteil", "begruendung", "konzepte", "belege_ids"]
    with open(os.path.join(OUT, "klug-links.tsv"), "w", encoding="utf-8", newline="") as f:
        def schreibe(feld):
            for x in feld:
                if "\t" in x or "\n" in x or "\r" in x:
                    sys.exit("Tab oder Zeilenumbruch in einem Feld: %r" % x[:60])
            f.write("\t".join(feld) + "\n")
        schreibe(kopf)
        for k in sorted(paare):
            d = paare[k]
            u = urteile[k]
            lex = lexikon(d["lemma_id"], kon)
            kz = " | ".join("%s: %s" % (s[0].split("_sense_")[-1], "; ".join(s[2])) for s in lex[2])
            ti = titel[k].split(" - ")[0].split(" | ")[0].strip()
            schreibe([d["lemma_id"], d["orth"], ti, "mps:" + d["kennung"], d["url"], u[2], u[3], kz, u[4] if len(u) > 4 else ""])
            zaehl[u[2]] = zaehl.get(u[2], 0) + 1
    print("Urteile:", zaehl, "Summe", sum(zaehl.values()))


if __name__ == "__main__":
    P = kandidaten()
    if NUR_URTEILE:
        phase2(P, titel_offline(P), None)
    else:
        T, H = phase1(P)
        phase2(P, T, H)
