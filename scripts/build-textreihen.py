#!/usr/bin/env python3
"""MHDBDB-Textreihentypologie: SKOS (RDF/JSON) -> textreihen/data/textreihen.json (#93).

Liest den unveraenderten Quellstand aus textreihen/data/skos/ (Commit 86c233f08 des
Repos Middle-High-German-Conceptual-Database/textseries) und schreibt die kompakte
JSON-Fassung, die der SKOS-Browser unter textreihen/browser.html laedt. Nur Standardbibliothek.

Die Hierarchie wird NICHT veraendert: jede skos:broader-Aussage der Quelle bleibt eine
Kante, auch die 65, die ein anderer Elternteil derselben Kategorie schon transitiv abdeckt.
Es gibt keinen Abgleich mit authority-files/genres.xml (Auftrag von KZW, #93).
Unbekannte Praedikate, Waisen und Zyklen sind harte Fehler.

  python scripts/build-textreihen.py           # schreibt textreihen/data/textreihen.json
  python scripts/build-textreihen.py --check   # exit 1, wenn die JSON-Datei nicht zur Quelle passt
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "textreihen" / "data" / "skos" / "MHDBDB-Textreihentypologie.rj"
OUT = REPO_ROOT / "textreihen" / "data" / "textreihen.json"

SOURCE_REPO = "Middle-High-German-Conceptual-Database/textseries"
SOURCE_COMMIT = "86c233f0803b6bf1dfd0db7913d086f00b8eb92b"
BASE = "https://dhplus.sbg.ac.at/mhdbdb/instance/"
SCHEME = BASE + "textreihentypologie"

SKOS = "http://www.w3.org/2004/02/skos/core#"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
DCT = "http://purl.org/dc/terms/"
OWL = "http://www.w3.org/2002/07/owl#"

CONCEPT_PREDICATES = {
    RDF_TYPE, SKOS + "prefLabel", SKOS + "altLabel", SKOS + "broader", SKOS + "inScheme",
    SKOS + "topConceptOf", SKOS + "editorialNote", DCT + "created", DCT + "modified", OWL + "deprecated",
}


def values(po, pred):
    return po.get(pred, [])


TRIMMED = []


def by_lang(objs):
    out = {}
    for o in objs:
        lang = o.get("lang")
        if not lang:
            raise SystemExit(f"Literal ohne Sprachangabe: {o['value']!r}")
        v = o["value"]
        if v != v.strip():
            # die Quelle bleibt unveraendert; nur die Anzeigefassung wird getrimmt (z. B. "Losbuch ")
            TRIMMED.append(v)
        out.setdefault(lang, []).append(v.strip())
    return out


def build():
    raw = json.loads(SRC.read_text(encoding="utf-8"))
    concepts = {s: po for s, po in raw.items()
                if SKOS + "Concept" in [o["value"] for o in values(po, RDF_TYPE)]}
    others = [s for s in raw if s not in concepts]
    for s in others:
        types = [o["value"] for o in values(raw[s], RDF_TYPE)]
        if s not in (BASE, SCHEME) or not types:
            raise SystemExit(f"unbekanntes Nicht-Konzept-Subjekt: {s} {types}")

    def cid(uri):
        if not uri.startswith(BASE + "c_"):
            raise SystemExit(f"unerwartete Konzept-URI: {uri}")
        return uri[len(BASE):]

    out, broader_triples = {}, 0
    for uri, po in concepts.items():
        extra = set(po) - CONCEPT_PREDICATES
        if extra:
            raise SystemExit(f"{uri}: unbekannte Praedikate {sorted(extra)}")
        pref = by_lang(values(po, SKOS + "prefLabel"))
        if "de" not in pref or any(len(v) != 1 for v in pref.values()):
            raise SystemExit(f"{uri}: prefLabel muss je Sprache genau einmal vorkommen und de enthalten")
        schemes = [o["value"] for o in values(po, SKOS + "inScheme")]
        if schemes != [SCHEME]:
            raise SystemExit(f"{uri}: inScheme {schemes}")
        parents = sorted({cid(o["value"]) for o in values(po, SKOS + "broader")})
        broader_triples += len(values(po, SKOS + "broader"))
        if len(parents) != len(values(po, SKOS + "broader")):
            raise SystemExit(f"{uri}: doppelte broader-Aussage")
        rec = {"l": {k: v[0] for k, v in pref.items()}}
        alt = by_lang(values(po, SKOS + "altLabel"))
        if alt:
            rec["a"] = {k: sorted(v) for k, v in sorted(alt.items())}
        note = by_lang(values(po, SKOS + "editorialNote"))
        if note:
            rec["n"] = {k: v[0] if len(v) == 1 else "; ".join(v) for k, v in sorted(note.items())}
        if parents:
            rec["p"] = parents
        if values(po, OWL + "deprecated"):
            rec["d"] = 1
        if values(po, SKOS + "topConceptOf"):
            rec["t"] = 1
        for key, pred in (("c", "created"), ("m", "modified")):
            v = values(po, DCT + pred)
            if len(v) != 1:
                raise SystemExit(f"{uri}: {pred} {len(v)}x")
            rec[key] = v[0]["value"][:10]
        out[cid(uri)] = rec

    for k, rec in out.items():
        for p in rec.get("p", []):
            if p not in out:
                raise SystemExit(f"{k}: broader-Ziel {p} ist kein Konzept")

    # Zyklen
    state = {}

    def visit(n):
        state[n] = 1
        for p in out[n].get("p", []):
            if state.get(p) == 1:
                raise SystemExit(f"Zyklus bei {n} -> {p}")
            if p not in state:
                visit(p)
        state[n] = 2

    for n in out:
        if n not in state:
            visit(n)

    roots = sorted(k for k, r in out.items() if "p" not in r)
    top = sorted(k for k, r in out.items() if r.get("t"))
    if roots != top:
        raise SystemExit(f"Wurzeln {roots} und topConceptOf {top} stimmen nicht ueberein")

    # Kinder, nach deutschem Label geordnet (Umlaute wie Grundbuchstabe), fuer die Anzeige
    def sortkey(k):
        t = out[k]["l"]["de"].lower()
        for a, b in (("ä", "a"), ("ö", "o"), ("ü", "u"), ("ß", "ss"), ("î", "i"), ("â", "a"), ("ê", "e"), ("ô", "o"), ("û", "u")):
            t = t.replace(a, b)
        return t, k

    ordered = {k: out[k] for k in sorted(out, key=sortkey)}
    redundant = 0
    anc = {}

    def ancestors(n):
        if n not in anc:
            r = set()
            for p in ordered[n].get("p", []):
                r.add(p)
                r |= ancestors(p)
            anc[n] = r
        return anc[n]

    for n, rec in ordered.items():
        ps = rec.get("p", [])
        redundant += sum(1 for p in ps if any(p in ancestors(q) for q in ps if q != p))

    multi = sum(1 for r in ordered.values() if len(r.get("p", [])) > 1)
    meta = {
        "quelle": SOURCE_REPO,
        "commit": SOURCE_COMMIT,
        "lizenz": "CC BY 4.0",
        "uriBasis": BASE,
        "konzepte": len(ordered),
        "broaderAussagen": broader_triples,
        "mitMehrerenEltern": multi,
        "wurzeln": roots,
    }
    return {"meta": meta, "concepts": ordered}, redundant


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    data, redundant = build()
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
    m = data["meta"]
    summary = (f"{m['konzepte']} Konzepte, {m['broaderAussagen']} broader-Aussagen "
               f"(davon {redundant} durch einen anderen Elternteil transitiv abgedeckt), "
               f"{m['mitMehrerenEltern']} von {m['konzepte']} Konzepten mit mehreren Eltern, {len(m['wurzeln'])} Wurzeln, "
               f"{len(TRIMMED)} Bezeichnungen mit Leerraum am Rand getrimmt")
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("textreihen/data/textreihen.json passt nicht zur Quelle:", summary)
            return 1
        print("OK:", summary)
        return 0
    OUT.write_text(text, encoding="utf-8", newline="")
    print("geschrieben:", OUT.relative_to(REPO_ROOT), "-", summary, f"({len(text)} Bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
