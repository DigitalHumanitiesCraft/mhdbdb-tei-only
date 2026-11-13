#!/usr/bin/env python3
"""02-convert-wiki-to-mhdbdb.py: Stage 0 fuer die Weingruesse (BRE, #147).

Konvertiert die Transkription eines Zeugen aus dem Brevitas-Wiki (gepinnter
Cache, siehe 00-fetch-wiki.py) in das MHDBDB-Schema:
ingest/bre/<SIGLE>.tei.xml. Segmentierung in Einzeltexte ueber
ingest/bre/segmentierung.tsv (01-segmentierung.py).

Quellformat -> TEI (mechanisch, ohne Eingriff in Wortgrenzen):
  Leerraum trennt <w>; ein Vers = eine Zeile = <l n>; "[188v]" auf eigener Zeile
  oder im Vers = <pb n="188v"/>; rot (<span color:#FF0000>) = <hi rend="inkRed">;
  '''x''' = <hi rend="bold">; ''x'' = <hi rend="italic">; <s>/<del> =
  <hi rend="line-through">; <u> = <hi rend="underline">; <sup> = superscript;
  (x) = <expan>; \\x/ = <add place="below">, /x\\ = place="above", |x| =
  place="margin"; <x> oder &lt;x&gt; = <supplied>; <ref>t</ref> = <note
  type="transcription">t</note> nach dem Wort. Zeile auf "-" + Folio-Marker +
  Fortsetzung = EIN Vers, EIN <w> ("schen<pb/>ken").
Nicht Schema-konformes (expan, supplied, add, pb im <w>) bleibt stehen
(PD-001/"Daten vor Schema"); die Validierung gegen schema/mhdbdb.rng am Ende
gibt die Fehler nach Klasse aus. Exit 0 auch bei Schemafehlern, Exit 1 bei
Parse- oder Segmentierungsfehlern oder fehlgeschlagener Gegenprobe.

Aufruf:
  python -P -E scripts/ingest/bre/02-convert-wiki-to-mhdbdb.py --zeuge B
  python -P -E scripts/ingest/bre/02-convert-wiki-to-mhdbdb.py --zeuge alle --trocken
"""
import argparse
import collections
import copy
import datetime
import html
import re
import sys
import urllib.parse
from pathlib import Path
from xml.sax.saxutils import escape

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_common as bc  # noqa: E402
import bre_hauptseite as bh  # noqa: E402
import bre_wikitext as bw  # noqa: E402

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"
SCHEMA_RNG = bc.REPO / "schema" / "mhdbdb.rng"

REF_OPEN, REF_CLOSE = "\uE000", "\uE001"
RE_REFPLATZ = re.compile(REF_OPEN + r"(\d+)" + REF_CLOSE)
RE_FOLIOZEILE = re.compile(r"^\[(\d+[rv]?[a-d]?)\]\s*$")
RE_TEILZEILE = re.compile(r"^={3,}\s*(.*?)\s*={3,}\s*$")
RE_HYPHEN_ENDE = re.compile(r"-((?:\s*</(?:span|s|u|sup)\s*>)*)\s*$")

RE_KLAMMER = re.compile(r"\(([^()]*)\)")

TOKEN = re.compile(r"""
  (?P<ref>""" + REF_OPEN + r"""(?P<refn>\d+)""" + REF_CLOSE + r""")
 |(?P<rot><span\s+style="color:\s*\#FF0000;?"\s*>)
 |(?P<rotzu></span\s*>)
 |(?P<tagauf><(?P<tn>s|del|u|sup)\s*>)
 |(?P<tagzu></(?P<tc>s|del|u|sup)\s*>)
 |(?P<bad></?(?:span|div|p|small|big|font|center|nowiki|math|code|table|tr|td|th|h[1-6]
        |strike|sub|em|strong|tt|b|i|br|ref|references)\b[^<>]*>)
 |(?P<badzu></[^<>]*>)
 |(?P<fett>''')
 |(?P<kursiv>'')
 |(?P<folio>\[(?P<fol>\d+[rv]?[a-d]?)\])
 |(?P<ent>&(?:lt|gt|amp|\#\d+|\#x[0-9a-fA-F]+);)
 |(?P<lt><)
 |(?P<gt>>)
 |(?P<lpar>\()
 |(?P<rpar>\))
 |(?P<bs>\\)
 |(?P<sl>/)
 |(?P<bar>\|)
 |(?P<ch>.)
""", re.X | re.S)

# Span-Art -> (Elementname, Attribute)
SPAN_EL = {
    "red": ("hi", {"rend": "inkRed"}),
    "bold": ("hi", {"rend": "bold"}),
    "italic": ("hi", {"rend": "italic"}),
    "del": ("hi", {"rend": "line-through"}),
    "u": ("hi", {"rend": "underline"}),
    "sup": ("hi", {"rend": "superscript"}),
    "add_below": ("add", {"place": "below"}),
    "add_above": ("add", {"place": "above"}),
    "add_margin": ("add", {"place": "margin"}),
    "expan": ("expan", {}),
    "supplied": ("supplied", {}),
}


class QuellFehler(bc.HarterFehler):
    pass


def q(tag):
    return f"{{{TEI_NS}}}{tag}"


# ---------------------------------------------------------------- Lexer

def lexe(raw, noten, ctx):
    """Eine Quellzeile (Refs schon durch Platzhalter ersetzt) -> (toks, meta).

    toks: ('c', zeichen, spans) | ('pb', folio, spans) | ('note', text, spans);
    spans = Tupel der offenen Span-Ids (aussen -> innen); meta: id -> Art.
    """
    toks, meta, stack = [], {}, []
    zaehler = [0]

    def auf(art):
        zaehler[0] += 1
        meta[zaehler[0]] = art
        stack.append((zaehler[0], art))

    def zu(art):
        if not stack or stack[-1][1] != art:
            offen = [a for _, a in stack]
            raise QuellFehler(f"{ctx}: schliessendes {art} ohne passendes Oeffnen "
                              f"(offen: {offen}) in {raw!r}")
        stack.pop()

    def sp():
        return tuple(s for s, _ in stack)

    def oben():
        return stack[-1][1] if stack else None

    pos = 0
    while pos < len(raw):
        m = TOKEN.match(raw, pos)
        pos = m.end()
        k = m.lastgroup
        # lastgroup ist bei verschachtelten benannten Gruppen die innere: ueber Gruppen pruefen
        for name in ("ref", "rot", "rotzu", "tagauf", "tagzu", "bad", "badzu", "fett", "kursiv",
                     "folio", "ent", "lt", "gt", "lpar", "rpar", "bs", "sl", "bar", "ch"):
            if m.group(name) is not None:
                k = name
                break
        if k == "ref":
            toks.append(("note", noten[int(m.group("refn"))], sp()))
        elif k == "rot":
            auf("red")
        elif k == "rotzu":
            zu("red")
        elif k == "tagauf":
            auf({"s": "del", "del": "del", "u": "u", "sup": "sup"}[m.group("tn")])
        elif k == "tagzu":
            zu({"s": "del", "del": "del", "u": "u", "sup": "sup"}[m.group("tc")])
        elif k in ("bad", "badzu"):
            raise QuellFehler(f"{ctx}: unbekanntes Tag {m.group(0)!r} in {raw!r}")
        elif k == "fett":
            zu("bold") if oben() == "bold" else auf("bold")
        elif k == "kursiv":
            zu("italic") if oben() == "italic" else auf("italic")
        elif k == "folio":
            toks.append(("pb", m.group("fol"), sp()))
        elif k == "ent":
            e = m.group(0)
            if e == "&lt;":
                auf("supplied")
            elif e == "&gt;":
                zu("supplied")
            else:
                for c in html.unescape(e):
                    toks.append(("c", c, sp()))
        elif k == "lt":
            auf("supplied")
        elif k == "gt":
            zu("supplied")
        elif k == "lpar":
            leer = RE_KLAMMER.match(raw, m.start())
            if leer and not re.search(r"[^\W\d_]", leer.group(1)):
                # Klammer ohne Buchstaben ist keine Abkuerzungsaufloesung
                inhalt = leer.group(1).strip()
                if inhalt == "?":
                    toks.append(("note", "Lesung unsicher", sp()))
                elif inhalt == "...":
                    toks.append(("gap", None, sp()))
                else:
                    raise QuellFehler(f"{ctx}: Klammerinhalt ohne Buchstaben {leer.group(0)!r} "
                                      f"(weder (?) noch (...)) in {raw!r}")
                pos = leer.end()
            else:
                auf("expan")
        elif k == "rpar":
            zu("expan")
        elif k == "bs":
            zu("add_above") if oben() == "add_above" else auf("add_below")
        elif k == "sl":
            zu("add_below") if oben() == "add_below" else auf("add_above")
        elif k == "bar":
            zu("add_margin") if oben() == "add_margin" else auf("add_margin")
        else:
            toks.append(("c", m.group(0), sp()))
    if stack:
        raise QuellFehler(f"{ctx}: Auszeichnung nicht geschlossen ({[a for _, a in stack]}) in {raw!r}")
    return toks, meta


def noten_text(roh):
    t = re.sub(r"<ref\b[^>]*>", "", roh)
    t = re.sub(r"</ref>", "", t)
    t = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"\[(?:https?://\S+)\s+([^\]]*)\]", r"\1", t)
    t = html.unescape(t)
    t = re.sub(r"<br\s*/?>", " ", t)
    t = t.replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------- Seite -> Items

def lies_transkription(inhalt):
    """-> (signatur, items). items: dict(kind='folio'|'part'|'verse', ...)."""
    mt = re.search(r"^==\s*Transkription.*$", inhalt, re.M)
    if not mt:
        raise QuellFehler("keine Transkriptions-Ueberschrift")
    kopf = inhalt[:mt.start()]
    sig = [z.strip() for z in kopf.split("\n")
           if z.strip() and not z.lstrip().startswith("=")]
    if not sig:
        raise QuellFehler("keine Signatur/Zitation vor der Transkription")
    signatur = bw.vergleichstext(sig[0])
    rest = inhalt[mt.end():]
    ma = re.search(r"^==\s*Anmerkungen\s*==", rest, re.M)
    if not ma:
        raise QuellFehler("keine Anmerkungen-Ueberschrift hinter der Transkription")
    block = rest[:ma.start()]
    # block beginnt VOR dem Zeilenende der Ueberschrift: split("\n")[0] ist deren Rest,
    # also 1-basierte Zeilennummer der Ueberschrift (nicht +1 dahinter)
    erste_zeile = inhalt[:mt.start()].count("\n") + 1
    noten = []

    def merk(m):
        noten.append(noten_text(m.group(0)))
        return f"{REF_OPEN}{len(noten) - 1}{REF_CLOSE}"

    geschuetzt = bw.RE_REF.sub(merk, block)
    items = []
    schluss = []
    n_stueck = 0  # unabhaengige Gegenprobe: nicht leere Stuecke, die weder Folio noch Teil sind
    for i, zeile in enumerate(geschuetzt.split("\n")):
        lineno = erste_zeile + i
        if RE_TEILZEILE.match(zeile.strip()):
            items.append({"kind": "part", "label": RE_TEILZEILE.match(zeile.strip()).group(1),
                          "line": lineno})
            continue
        for stueck in re.split(r"<br\s*/?>", zeile):
            s = stueck.strip()
            if not s:
                continue
            m = RE_FOLIOZEILE.match(s)
            if s in ("/", "\\", "|") and items and items[-1]["kind"] == "verse":
                # Schlusszeichen eines Nachtrags hinter dem Zeilenumbruch (Quelle Cod. Oct 145,
                # "...\schercze(n) <br />/"): an die Vorzeile haengen, nicht als Vers zaehlen
                items[-1]["raw"] += s
                schluss.append(lineno)
            elif m:
                items.append({"kind": "folio", "n": m.group(1), "line": lineno})
            else:
                items.append({"kind": "verse", "raw": s, "lines": [lineno]})
                n_stueck += 1
    # Fortsetzung: Zeile endet auf "-", dann Folio-Marker, dann Fortsetzungszeile
    out, merged, warn = [], 0, []
    i = 0
    while i < len(items):
        it = items[i]
        if it["kind"] == "verse" and RE_HYPHEN_ENDE.search(it["raw"]):
            j = i + 1
            folios = []
            while j < len(items) and items[j]["kind"] == "folio":
                folios.append(items[j])
                j += 1
            if folios and j < len(items) and items[j]["kind"] == "verse":
                raw = RE_HYPHEN_ENDE.sub(lambda m: m.group(1), it["raw"], count=1)
                raw += "".join(f"[{f['n']}]" for f in folios) + items[j]["raw"]
                out.append({"kind": "verse", "raw": raw,
                            "lines": it["lines"] + [f["line"] for f in folios] + items[j]["lines"],
                            "fortsetzung": True})
                merged += 1
                i = j + 1
                continue
            warn.append(it["lines"][0])
        out.append(it)
        i += 1
    return signatur, out, noten, {"stuecke": n_stueck, "fortsetzungen": merged,
                                  "bindestrich_ohne_fortsetzung": warn, "schlusszeichen": schluss}


# ---------------------------------------------------------------- Segmentierung

def lade_segmentierung(sigle):
    if not bc.SEGMENTIERUNG.exists():
        raise bc.HarterFehler(f"{bc.SEGMENTIERUNG} fehlt (erst 01-segmentierung.py ausfuehren)")
    zeilen = bc.SEGMENTIERUNG.read_text(encoding="utf-8").splitlines()
    kopf = zeilen[0].split("\t")
    rows = []
    for z in zeilen[1:]:
        d = dict(zip(kopf, z.split("\t")))
        if d["editionssigle"] == sigle:
            rows.append(d)
    return rows


def falte(s):
    for a, b in bc.FALTUNG.items():
        s = s.replace(a, b)
    return s


def segmentiere(items, lex, rows, sigle):
    """Weist jede Zeile genau einem Text zu.

    -> (Texte nach Position, angewandte Faltungen, Vorspann oder None)
    """
    verse = [i for i, it in enumerate(items) if it["kind"] == "verse"]
    cmp_ = {i: re.sub(r"\s+", " ", RE_REFPLATZ.sub("", bw.vergleichstext(items[i]["raw"]))).strip()
            for i in verse}
    fehler, starts, faltungen = [], [], []
    for r in rows:
        treffer = [i for i in verse if cmp_[i] == r["erster_vers"]]
        if not treffer:  # Faltung nur im Vergleich, nur wenn der exakte Vergleich nichts findet
            treffer = [i for i in verse if falte(cmp_[i]) == falte(r["erster_vers"])]
            if len(treffer) == 1:
                faltungen.append(f"Faltung angewandt: {sigle} Zeile {items[treffer[0]]['lines'][0]}, "
                                 f"{'/'.join(a + '~' + b for a, b in bc.FALTUNG.items())} "
                                 f"({r['text_titel']}: {r['erster_vers']!r} ~ {cmp_[treffer[0]]!r})")
        if len(treffer) != 1:
            fehler.append(f"erster Vers {len(treffer)}x gefunden statt 1: {r['text_titel']} / "
                          f"{r['signatur_label']}: {r['erster_vers']!r}"
                          + (f" (Zeilen {[items[i]['lines'][0] for i in treffer]})" if treffer else ""))
        else:
            starts.append((treffer[0], r))
    doppelt = collections.Counter(i for i, _ in starts)
    for i, c in doppelt.items():
        if c > 1:
            fehler.append(f"Zeile {items[i]['lines'][0]} ist Textanfang von {c} Texten")
    if fehler:
        raise bc.HarterFehler("Segmentierung geht nicht auf:\n  " + "\n  ".join(fehler))
    starts.sort(key=lambda x: x[0])

    def in_kopfzeilen(i, kopfzeilen):
        if cmp_[i] in kopfzeilen:
            return True
        if falte(cmp_[i]) in {falte(z) for z in kopfzeilen}:  # Faltung nur im Vergleich
            faltungen.append(f"Faltung angewandt: {sigle} Zeile {items[i]['lines'][0]}, "
                             f"{'/'.join(a + '~' + b for a, b in bc.FALTUNG.items())} "
                             f"(Kopfzeile {cmp_[i]!r})")
            return True
        return False

    def ist_kopfartig(i, kopfzeilen, erster_text):
        if erster_text:
            # vor dem ersten Text gilt nur die Spalte ueberschrift der Synopse; rote/fette
            # Zeilen davor muessen durch bre_common.VORSPANN erklaert sein
            return in_kopfzeilen(i, kopfzeilen)
        toks, meta = lex[i]
        zeichen = [t for t in toks if t[0] == "c" and not t[1].isspace()]
        if not zeichen:
            return False
        arten = lambda t: {meta[s] for s in t[2]}  # noqa: E731
        if all("red" in arten(t) for t in zeichen) or all("bold" in arten(t) for t in zeichen):
            return True
        return in_kopfzeilen(i, kopfzeilen)

    texte = []
    for k, (s, r) in enumerate(starts):
        kopfzeilen = {z.strip() for z in r.get("ueberschrift", "").split(" / ") if z.strip()}
        untergrenze = starts[k - 1][0] if k else -1
        heads, j = [], s - 1
        while j > untergrenze:
            it = items[j]
            if it["kind"] == "part":
                break
            if it["kind"] == "verse":
                if ist_kopfartig(j, kopfzeilen, k == 0):
                    heads.insert(0, j)
                else:
                    break
            j -= 1
        erstes = heads[0] if heads else s
        b = erstes
        while b - 1 > untergrenze and items[b - 1]["kind"] in ("folio", "part"):
            b -= 1
        texte.append({"row": r, "start": s, "heads": heads, "grenze": b})
    if not texte:
        raise bc.HarterFehler("kein Text in segmentierung.tsv fuer diesen Zeugen")
    # Vorspann: Zeilen vor dem ersten Textanfang muessen der ausdruecklichen Tabelle entsprechen
    vor = [i for i in verse if i < texte[0]["grenze"]]
    ist = [cmp_[i] for i in vor]
    art, soll = bc.VORSPANN.get(sigle, (None, []))
    if ist != soll:
        raise bc.HarterFehler(
            f"Vorspann weicht von bre_common.VORSPANN ab: {len(ist)} Zeile(n) vor dem ersten Textanfang "
            f"(Zeilen {[items[i]['lines'][0] for i in vor]}) {ist!r}, erwartet {len(soll)}: {soll!r}")
    return texte, faltungen, ({"art": art, "idx": vor, "werk": bc.VORSPANN_WERK.get(sigle)}
                              if vor else None)


# ---------------------------------------------------------------- TEI-Aufbau

class Zustand:
    def __init__(self, sigle):
        self.sigle = sigle
        self.folio = None
        self.zeile = 0
        self.tokidx = 0


def E(parent, tag, **attrs):
    el = etree.SubElement(parent, q(tag)) if parent is not None else etree.Element(q(tag))
    for k, v in attrs.items():
        el.set(k, v)
    return el


def anhaengen_text(el, s):
    kinder = list(el)
    if kinder:
        kinder[-1].tail = (kinder[-1].tail or "") + s
    else:
        el.text = (el.text or "") + s


def zerlege_woerter(toks):
    items, cur, pend = [], None, []

    def flush():
        nonlocal cur
        if cur is not None:
            items.append({"kind": "w", "toks": cur})
            cur = None
            items.extend(pend)
            pend.clear()

    def naechstes_zeichen(i):
        for t in toks[i + 1:]:
            if t[0] == "c":
                return t
        return None

    for i, t in enumerate(toks):
        if t[0] == "c":
            if t[1].isspace():
                flush()
            else:
                if cur is None:
                    cur = []
                cur.append(t)
        elif t[0] == "pb":
            nz = naechstes_zeichen(i)
            innen = cur is not None and nz is not None and not nz[1].isspace()
            if innen:
                cur.append(t)
            else:
                flush()
                items.append({"kind": "pb", "n": t[1], "spans": t[2]})
        elif t[0] == "gap":  # "(...)": eigenes Token zwischen den <w>
            flush()
            items.append({"kind": "gap", "spans": t[2]})
        else:  # note
            it = {"kind": "note", "text": t[1], "spans": t[2]}
            if cur is not None:
                pend.append(it)
            else:
                items.append(it)
    flush()
    return items


def baue_zeile(container, toks, meta, zust, stat, containers, ctx):
    """Fuellt <l> oder <head> mit <w>, <pb>, <note>; liefert die erwartete Zeichenfolge."""
    zust.zeile += 1
    zust.tokidx = 0
    items = zerlege_woerter(toks)
    # mehrwortige, wortgenaue Spans an Zeilenebene heben
    wortspans = collections.defaultdict(list)  # sid -> [(wortindex, voll)]
    for wi, it in enumerate(items):
        if it["kind"] != "w":
            continue
        zeichen = [t for t in it["toks"] if t[0] == "c"]
        sids = {s for t in zeichen for s in t[2]}
        for s in sids:
            wortspans[s].append((wi, all(s in t[2] for t in zeichen)))
    gehoben = set()
    for s, lst in wortspans.items():
        if len(lst) >= 2:
            if all(v for _, v in lst):
                gehoben.add(s)
            else:
                stat["span_dupliziert"][meta[s]] += 1
    erwartet = []

    stack = [(None, container)]
    for pos, it in enumerate(items):
        if it["kind"] == "w":
            spans0 = [t for t in it["toks"] if t[0] == "c"][0][2]
        else:
            spans0 = it["spans"]
        want = tuple(s for s in spans0 if s in gehoben)
        k = 0
        while k < len(stack) - 1 and k < len(want) and stack[k + 1][0] == want[k]:
            k += 1
        del stack[k + 1:]
        for sid in want[k:]:
            tag, attrs = SPAN_EL[meta[sid]]
            el = E(stack[-1][1], tag, **attrs)
            containers.add(id(el))
            stat["el"][tag + ("/" + attrs.get("rend", attrs.get("place", "")) if attrs else "")] += 1
            stack.append((sid, el))
        parent = stack[-1][1]
        if it["kind"] == "pb":
            weitere_woerter = any(x["kind"] == "w" for x in items[pos + 1:])
            zust.folio = it["n"]
            zust.zeile = 1 if weitere_woerter else 0
            zust.tokidx = 0
            E(parent, "pb", n=it["n"])
            stat["pb"] += 1
        elif it["kind"] == "gap":
            E(parent, "gap", reason="illegible")
            stat["el"]["gap"] += 1
        elif it["kind"] == "note":
            n = E(parent, "note", type="transcription")
            n.text = it["text"]
            stat["note"] += 1
        else:
            if zust.folio is None:
                raise QuellFehler(f"{ctx}: Wort vor dem ersten Folio-Marker")
            wid = f"{zust.sigle}_{zust.folio}_{zust.zeile}_{zust.tokidx}"
            w = E(parent, "w")
            w.set(f"{{{XML_NS}}}id", wid)
            stat["w"] += 1
            erwartet.append("".join(t[1] for t in it["toks"] if t[0] == "c"))
            innen_pb = False
            wstack = [(None, w)]
            for t in it["toks"]:
                spans = tuple(s for s in t[2] if s not in gehoben)
                kk = 0
                while kk < len(wstack) - 1 and kk < len(spans) and wstack[kk + 1][0] == spans[kk]:
                    kk += 1
                del wstack[kk + 1:]
                for sid in spans[kk:]:
                    tag, attrs = SPAN_EL[meta[sid]]
                    el = E(wstack[-1][1], tag, **attrs)
                    stat["el"][tag + ("/" + attrs.get("rend", attrs.get("place", "")) if attrs else "")] += 1
                    wstack.append((sid, el))
                if t[0] == "c":
                    anhaengen_text(wstack[-1][1], t[1])
                else:
                    E(wstack[-1][1], "pb", n=t[1])
                    stat["pb_im_wort"] += 1
                    stat["pb"] += 1
                    zust.folio = t[1]
                    zust.zeile = 1
                    zust.tokidx = 1
                    innen_pb = True
            if not innen_pb:
                zust.tokidx += 1
    return erwartet


def einruecken(el, ebene, containers):
    kinder = list(el)
    if not kinder:
        return
    pad = "\n" + "  " * (ebene + 1)
    el.text = pad
    for k in kinder:
        k.tail = pad
    kinder[-1].tail = "\n" + "  " * ebene
    for k in kinder:
        if ist_huelle(k):
            einruecken(k, ebene + 1, containers)


def ist_huelle(k):
    """Strukturelement, das nur Elemente enthaelt (kein Mischinhalt): body, div, l, head
    und die an die Zeilenebene gehobenen Auszeichnungen, nie etwas innerhalb eines <w>.
    (lxml-Proxys haben keine stabile id(), darum strukturell statt per Merkliste.)"""
    if k.tag in (q("body"), q("div"), q("l"), q("head")):
        return True
    if k.tag in (q("hi"), q("add"), q("expan"), q("supplied")):
        p = k.getparent()
        while p is not None:
            if p.tag == q("w"):
                return False
            p = p.getparent()
        return True
    return False


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
          <licence target="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</licence>
          <p>Transkription von Silvan Wagner (wiki.brevitas.org), Freigabe unter CC BY-NC-SA 4.0 per Mail an Katharina Zeppezauer-Wachauer, Oktober 2026 (#147).</p>
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
              <bibl type="digitalIntermediary" xml:id="{sigle}_brevitas_wiki" corresp="#{sigle}_TBD">
                <title>Brevitas-Wiki, Hybridedition der Weingrüße (Silvan Wagner)</title>
                <respStmt>
                  <resp>Transkription</resp>
                  <name>Silvan Wagner</name>
                </respStmt>
                <ref target="{source_url}"/>
                <note type="provenance">Transkription aus dem Brevitas-Wiki (wiki.brevitas.org), Seite "{wiki_titel}", Revision {revid} vom {timestamp}. Konvertiert in das MHDBDB-Schema durch automatische Transformation (scripts/ingest/bre/02-convert-wiki-to-mhdbdb.py, {heute}).</note>
                <note type="fidelity">Mechanische Konversion ohne Eingriff in Wortgrenzen und Auszeichnungs-Semantik. Die Gliederung in Einzeltexte folgt den Synopsen der Einzeltextseiten des Brevitas-Wikis, Teile einer Transkription (Teil A/B) als div/@n.</note>
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
            <gloss xml:lang="de">Weingruß (TBD: konkrete Genre-ID)</gloss>
          </category>
        </taxonomy>
      </classDecl>
    </encodingDesc>
    <profileDesc>
      <langUsage>
        <language ident="TBD">TBD (Sprachstufe offen, #118)</language>
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
      <change when="{heute}" who="#mhdbdb-team">Initiale Konversion aus dem Brevitas-Wiki (Revision {revid}) via scripts/ingest/bre/02-convert-wiki-to-mhdbdb.py.</change>
    </revisionDesc>
  </teiHeader>"""


def baue_tei(sigle, signatur, seite, items, lex, texte, stat, vorspann=None, datum="1970-01-01"):
    """-> (tei_root, containers, erwartete_zeilen)"""
    attr = lambda s: escape(s, {'"': "&quot;"})  # noqa: E731
    quelle = (f"{bc.WIKI_BASIS}?title={urllib.parse.quote(seite['titel'].replace(' ', '_'))}"
              f"&oldid={seite['revid']}")
    header = etree.fromstring(HEADER_TEMPLATE.format(
        sigle=sigle, title_de=escape(signatur), source_url=attr(quelle),
        wiki_titel=escape(seite["titel"]), revid=seite["revid"], timestamp=seite["timestamp"],
        heute=datum))
    tei = etree.Element(q("TEI"), nsmap={None: TEI_NS})
    tei.set(f"{{{XML_NS}}}id", sigle)
    tei.append(header)
    text = E(tei, "text")
    body = E(text, "body")
    aussen = E(body, "div")
    containers = {id(body), id(aussen)}
    zust = Zustand(sigle)
    if not any(it["kind"] == "folio" for it in items):
        zust.folio = "0"  # Quelle ohne Folio-Marker (d2, Abschrift nach Weller 1874): xml:id mit Folio 0
        stat["ohne_folio"] = True
    grenzen = [t["grenze"] for t in texte] + [len(items)]
    erwartet_zeilen = []  # (Quellzeile, erwartete Zeichen)

    def emit(div, indices, heads):
        vnr = 0
        for i in indices:
            it = items[i]
            if it["kind"] == "part":
                continue
            if it["kind"] == "folio":
                zust.folio = it["n"]
                zust.zeile = 0
                zust.tokidx = 0
                E(div, "pb", n=it["n"])
                stat["pb"] += 1
                continue
            toks, meta = lex[i]
            if i in heads:
                el = E(div, "head")
                stat["head"] += 1
            else:
                vnr += 1
                el = E(div, "l", n=str(vnr))
                stat["l"] += 1
            containers.add(id(el))
            ws = baue_zeile(el, toks, meta, zust, stat, containers, f"Zeile {it['lines'][0]}")
            erwartet_zeilen.append((it["lines"][0], "".join(ws), it["raw"]))

    n_abschnitt = 0
    vor_indices = range(0, grenzen[0])
    if vorspann and vorspann["art"] == "reihentitel":
        # Reihentitel: <head> des aeusseren <div>, vor dem ersten Abschnitt
        emit(aussen, vor_indices, {i for i in vor_indices if items[i]["kind"] == "verse"})
    elif vorspann:
        n_abschnitt += 1
        werk = vorspann.get("werk")
        if vorspann["art"] == "fragment" and not werk:
            raise QuellFehler("Fragment ohne Werkzuordnung: bre_common.VORSPANN_WERK nennt den Text "
                              "laut Hauptseite (Abschnitt Überlieferung)")
        aussen.append(etree.Comment(
            f" Text {n_abschnitt}: {werk} (Fragment) " if werk and vorspann["art"] == "fragment"
            else f" Text {n_abschnitt}: Vorspann ({vorspann['art']}) "))
        div = E(aussen, "div", type="section", n=str(n_abschnitt))
        containers.add(id(div))
        n = E(div, "note", type="editorial")
        n.text = bc.VORSPANN_NOTIZ[vorspann["art"]].format(werk=werk)
        verse_idx = [i for i in vor_indices if items[i]["kind"] == "verse"]
        heads = {verse_idx[0]} if vorspann["art"] == "text_ohne_einzelseite" else set()
        emit(div, vor_indices, heads)
    elif any(items[i]["kind"] == "folio" for i in vor_indices):
        raise QuellFehler("Folio-Marker vor dem ersten Textanfang ohne Vorspann (nicht zugeordnet)")
    if any(items[i]["kind"] == "part" for i in vor_indices):
        raise QuellFehler("Teil-Marker (===...===) im Vorspann: nicht vorgesehen")
    elter = aussen  # aeusseres <div> der Reihe, oder das <div n="A"> des laufenden Teils
    for k, t in enumerate(texte):
        r = t["row"]
        region = range(grenzen[k], grenzen[k + 1])
        fuehrend = []
        for i in region:
            if items[i]["kind"] == "part":
                fuehrend.append(i)
            elif items[i]["kind"] != "folio":
                break
        if any(items[i]["kind"] == "part" and i not in fuehrend for i in region):
            raise QuellFehler("Teil-Marker (===...===) mitten in einem Text")
        if fuehrend:
            label = re.sub(r"^Teil\s+", "", items[fuehrend[-1]]["label"]).rstrip(":").strip()
            if not re.fullmatch(r"\w+", label):
                raise QuellFehler(f"Teil-Marker {items[fuehrend[-1]]['label']!r} nicht lesbar")
            elter = E(aussen, "div", n=label)
            containers.add(id(elter))
        n_abschnitt += 1
        elter.append(etree.Comment(
            f" Text {n_abschnitt}: {r['text_titel']} ({r['signatur_label']}, {r['blatt']}) "))
        div = E(elter, "div", type="section", n=str(n_abschnitt))
        containers.add(id(div))
        emit(div, range(grenzen[k], grenzen[k + 1]), set(t["heads"]))
    return tei, containers, erwartet_zeilen


# ---------------------------------------------------------------- Pruefung

def _signatur(el):
    attrs = tuple(sorted((k, v) for k, v in el.attrib.items()
                         if k not in (f"{{{XML_NS}}}id", "n")))
    return (el.tag, attrs, tuple(_signatur(c) for c in el if isinstance(c.tag, str)))


def schema_pruefen(tei):
    """Validiert das Ganze und zaehlt die Verstoesse einzeln.

    libxml2 meldet je Dokument nur die erste Fehlerkette. Darum wird jede
    Einheit (<l>, <head>, <pb>, <note>, <w>, Huellelemente) einzeln in einem
    Geruest mit den Vorfahren-Schalen validiert; ein fehlerhaftes Element, dessen
    Kinder alle einzeln gueltig sind (oder das ein <w> ist), zaehlt als ein
    Verstoss seiner Klasse. Gleiche Struktur wird nur einmal validiert.
    -> (ganzes_dokument_valide, Counter{(tag, meldung): n}, Counter{kind-tag im <w>: n})
    """
    rng = etree.RelaxNG(etree.parse(str(SCHEMA_RNG)))
    ok = rng.validate(etree.ElementTree(tei))
    header = tei.find(q("teiHeader"))
    cache = {}
    ergebnis = collections.Counter()

    def geruest(el):
        kette = []
        p = el.getparent()
        while p is not None and p.tag != q("TEI"):
            kette.append(p)
            p = p.getparent()
        kette.reverse()  # text, body, div, div, l, ...
        t = etree.Element(q("TEI"), nsmap={None: TEI_NS})
        t.set(f"{{{XML_NS}}}id", "X")
        t.append(copy.deepcopy(header))
        cur = t
        for s in kette:
            n = etree.SubElement(cur, s.tag)
            for k, v in s.attrib.items():
                if k != f"{{{XML_NS}}}id":
                    n.set(k, v)
            cur = n
        cur.append(copy.deepcopy(el))
        return etree.ElementTree(t)

    def gueltig(el):
        kette = []
        p = el.getparent()
        while p is not None:
            kette.append(p.tag if isinstance(p.tag, str) else "?")
            p = p.getparent()
        schluessel = (tuple(kette), _signatur(el))
        if schluessel not in cache:
            doc = geruest(el)
            if rng.validate(doc):
                cache[schluessel] = (True, "")
            else:
                cache[schluessel] = (False, re.sub(r"\d+", "N", rng.error_log[0].message))
        return cache[schluessel]

    def pruefe(el):
        if not isinstance(el.tag, str):
            return
        g, msg = gueltig(el)
        if g:
            return
        if el.tag != q("w"):
            vorher = sum(ergebnis.values())
            for c in el:
                pruefe(c)
            if sum(ergebnis.values()) > vorher:
                return
        ergebnis[(etree.QName(el).localname, msg)] += 1

    for div in tei.iter(q("div")):
        if div.get("type") == "section":
            pruefe(div)
    im_wort = collections.Counter(
        etree.QName(c).localname for w in tei.iter(q("w")) for c in w
        if isinstance(c.tag, str) and c.tag != q("hi"))
    return ok, ergebnis, im_wort


def runde(text_zeichen):
    return re.sub(r"[\s\\/|()<>]", "", text_zeichen)


def konvertiere(sigle, trocken, ausgabe_dir, datum):
    name, mhdbdb = bc.ZEUGEN[sigle]
    titel = bc.transkriptions_titel(sigle)
    seite = bc.lade_seite(titel)
    signatur, items, noten, info = lies_transkription(seite["inhalt"])
    rows = lade_segmentierung(sigle)

    lex = {}
    for i, it in enumerate(items):
        if it["kind"] == "verse":
            lex[i] = lexe(it["raw"], noten, f"{titel} Zeile {it['lines'][0]}")
    texte, faltungen, vorspann = segmentiere(items, lex, rows, sigle)
    if len(texte) != len(rows):
        raise bc.HarterFehler(f"{len(texte)} Texte gefunden statt {len(rows)} in segmentierung.tsv")
    n_vor_text = 1 if vorspann and vorspann["art"] != "reihentitel" else 0

    # Abgleich mit der Hauptseite (Werkzuordnung massgeblich, #147): jede nicht geprueft
    # erklaerte Abweichung ist ein harter Fehler (bre_common.ABWEICHUNG_ERKLAERT)
    haupt_seite, haupt = bh.lade_hauptseite()
    unsere = [t["row"]["text_titel"] for t in texte]
    if vorspann and vorspann.get("werk"):
        unsere = [vorspann["werk"]] + unsere
    abw = bh.abgleich(sigle, haupt[sigle], unsere, None)
    offen = [x for x in abw if (sigle, x["art"], x["titel"]) not in bc.ABWEICHUNG_ERKLAERT]
    if offen:
        raise bc.HarterFehler(
            f"Abweichung zur Hauptseite (rev {haupt_seite['revid']}), nicht in "
            f"bre_common.ABWEICHUNG_ERKLAERT: "
            + "; ".join(f"{x['art']} {x['titel']!r}: bisher {x['bisher']!r}, Hauptseite "
                        f"{x['hauptseite']!r}" for x in offen))

    stat = {"w": 0, "l": 0, "head": 0, "pb": 0, "pb_im_wort": 0, "note": 0,
            "el": collections.Counter(), "span_dupliziert": collections.Counter()}
    tei, containers, erwartet = baue_tei(mhdbdb, signatur, seite, items, lex, texte, stat,
                                         vorspann, datum)

    # Gegenproben
    n_l = len(tei.xpath("//t:l", namespaces={"t": TEI_NS}))
    n_head = len(tei.xpath("//t:head", namespaces={"t": TEI_NS}))
    n_div = len(tei.xpath("//t:div[@type='section']", namespaces={"t": TEI_NS}))
    n_w = len(tei.xpath("//t:w", namespaces={"t": TEI_NS}))
    probleme = []
    if n_l + n_head + info["fortsetzungen"] != info["stuecke"]:
        probleme.append(f"Zeilen: {n_l} <l> + {n_head} <head> + {info['fortsetzungen']} Fortsetzung(en) "
                        f"!= {info['stuecke']} Quellzeilen")
    if n_div != len(rows) + n_vor_text:
        probleme.append(f"Texte: {n_div} <div> != {len(rows)} Zeilen in segmentierung.tsv "
                        f"+ {n_vor_text} Vorspann-Text")
    if n_w != stat["w"]:
        probleme.append(f"Woerter: {n_w} <w> im Baum != {stat['w']} gebaut")
    ids = tei.xpath("//t:w/@xml:id", namespaces={"t": TEI_NS})
    dup = [k for k, c in collections.Counter(ids).items() if c > 1]
    if dup:
        probleme.append(f"{len(dup)} doppelte xml:id, z.B. {dup[:5]}")
    # Rundlauf je Zeile: Zeichen der <w> == Zeichen der bereinigten Quellzeile (ohne Klammersymbole)
    abweichend = []
    for lineno, zeichen, raw in erwartet:
        quelle = RE_REFPLATZ.sub("", html.unescape(raw))
        quelle = re.sub(r"</?(?:span|s|u|del|sup)\b[^>]*>", "", quelle).replace("'''", "").replace("''", "")
        quelle = bw.RE_FOLIO.sub("", quelle).replace("(...)", "").replace("(?)", "")
        if runde(quelle) != runde(zeichen):
            abweichend.append((lineno, raw[:60], zeichen[:60]))
    if abweichend:
        probleme.append(f"{len(abweichend)} Zeile(n) mit Textabweichung Quelle/Baum, z.B. {abweichend[:3]}")
    words_roh = sum(len(re.sub(r"[()<>\\/|]", "", RE_REFPLATZ.sub(
        "", bw.vergleichstext(i["raw"]).replace("(...)", "").replace("(?)", ""))).split())
                    for i in items if i["kind"] == "verse")
    # (Wortzahl der Quelle nach Fortsetzungs-Verschmelzung; Abweichung nur gemeldet)
    wzahl_hinweis = None if words_roh == n_w else f"Wortzahl Quelle {words_roh} != <w> {n_w}"

    root = tei
    einruecken(root.find(q("text")), 1, containers)
    root.text = "\n  "
    root.find(q("teiHeader")).tail = "\n  "
    root.find(q("text")).tail = "\n"
    ok, klassen, im_wort = schema_pruefen(root)

    pfad = ausgabe_dir / f"{mhdbdb}.tei.xml"
    if not trocken and not probleme:
        pi1 = etree.ProcessingInstruction(
            "xml-model", 'href="../schema/mhdbdb.rng" type="application/xml" '
                         'schematypens="http://relaxng.org/ns/structure/1.0"')
        pi2 = etree.ProcessingInstruction(
            "xml-model", 'href="https://tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng"')
        root.addprevious(pi1)
        root.addprevious(pi2)
        ausgabe_dir.mkdir(parents=True, exist_ok=True)
        etree.ElementTree(root).write(str(pfad), encoding="UTF-8", xml_declaration=True)

    print(f"== {sigle} ({name}) -> {mhdbdb}  [Seite {titel!r}, rev {seite['revid']}]")
    print(f"Datum im Header: {datum}")
    print(f"Texte: {len(texte)} (von {len(rows)} in segmentierung.tsv)"
          + (f" + {n_vor_text} Vorspann-Text" if n_vor_text else ""))
    if vorspann:
        print(f"Vorspann ({vorspann['art']}): {len(vorspann['idx'])} Zeile(n), Quellzeilen "
              f"{[items[i]['lines'][0] for i in vorspann['idx']]}")
    print(f"Hauptseite (rev {haupt_seite['revid']}): {len(haupt[sigle])} Eintraege, "
          + ("keine Abweichung" if not abw else f"{len(abw)} geprueft erklaerte Abweichung(en)"))
    for x in abw:
        print(f"  Abweichung {x['art']} {x['titel']!r}: {bc.ABWEICHUNG_ERKLAERT[(sigle, x['art'], x['titel'])]}")
    for f in faltungen:
        print(f)
    for k, t in enumerate(texte):
        r = t["row"]
        print(f"  {k + 1}. Zeile {items[t['start']]['lines'][0]}: {r['text_titel']}"
              f" ({len(t['heads'])} Kopfzeile(n))")
    print(f"Zeilen: {n_l} <l> + {n_head} <head> + {info['fortsetzungen']} Fortsetzung(en) "
          f"= {n_l + n_head + info['fortsetzungen']} (von {info['stuecke']} Quellzeilen)")
    print(f"Woerter: {n_w} <w>; Folio-Marker: {stat['pb']} <pb> (davon {stat['pb_im_wort']} im Wort); "
          f"Anmerkungen: {stat['note']} <note>")
    print("Elemente: " + ", ".join(f"{k}={v}" for k, v in sorted(stat["el"].items())))
    if stat["span_dupliziert"]:
        print("Auszeichnungen ueber Wortgrenzen, nicht wortgenau, je Wort dupliziert: "
              + ", ".join(f"{k}={v}" for k, v in stat["span_dupliziert"].items()))
    if info["bindestrich_ohne_fortsetzung"]:
        print(f"Hinweis: {len(info['bindestrich_ohne_fortsetzung'])} Zeile(n) auf '-' ohne Folio-Marker "
              f"(nicht verschmolzen): Zeilen {info['bindestrich_ohne_fortsetzung']}")
    if stat.get("ohne_folio"):
        print("Hinweis: Quelle ohne Folio-Marker; xml:id tragen Folio 0, Zeilenzaehlung laeuft durch")
    if info["schlusszeichen"]:
        print(f"Hinweis: {len(info['schlusszeichen'])} Nachtrags-Schlusszeichen hinter <br /> an die "
              f"Vorzeile gehaengt (Quellzeilen {info['schlusszeichen']})")
    if wzahl_hinweis:
        print(f"Hinweis: {wzahl_hinweis}")
    print(f"Schema: {'valide' if ok else 'NICHT valide'}; Verstoesse einzeln gezaehlt: "
          f"{sum(klassen.values())} in {len(klassen)} Klasse(n)")
    for (tag, msg), c in klassen.most_common():
        print(f"  {c:5d}x <{tag}>: {msg}")
    if im_wort:
        print("  Kinder im <w> ausser <hi> (Vorkommen): "
              + ", ".join(f"{k}={v}" for k, v in im_wort.most_common()))
    if probleme:
        raise bc.HarterFehler("Gegenprobe fehlgeschlagen: " + "; ".join(probleme))
    print(f"Geschrieben: {pfad}" if not trocken else "(trocken: nichts geschrieben)")
    return 0


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zeuge", required=True, help="Editionssigle (z.B. B, d3) oder 'alle'")
    ap.add_argument("--trocken", action="store_true", help="nichts schreiben")
    ap.add_argument("--ausgabe-dir", type=Path, default=bc.INGEST_DIR)
    ap.add_argument("--datum", default=datetime.date.today().isoformat(),
                    help="Datum fuer revisionDesc, JJJJ-MM-TT (Vorgabe: heute)")
    a = ap.parse_args()
    try:
        datetime.date.fromisoformat(a.datum)
    except ValueError:
        ap.error(f"--datum {a.datum!r} ist kein JJJJ-MM-TT")
    zeugen = list(bc.ZEUGEN) if a.zeuge == "alle" else [a.zeuge]
    rc = 0
    for z in zeugen:
        try:
            konvertiere(z, a.trocken, a.ausgabe_dir, a.datum)
        except bc.HarterFehler as e:
            print(f"FEHLER ({z}): {e}", file=sys.stderr)
            print(f"== {z}: HARTER FEHLER, siehe oben/stderr")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
