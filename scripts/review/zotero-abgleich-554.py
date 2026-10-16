"""Lesender Abgleich von ingest/glossar-554/literatur.tsv gegen zwei Zotero-Gruppen (#554).

Nur GET auf die oeffentliche Zotero-API, ohne Schluessel, sequenziell, >= 1,2 s Pause.
Jede Antwort ausser 200 bricht den Lauf ab (kein Retry, kein anderer Weg).
Aufruf: python scripts/review/zotero-abgleich-554.py <ausgabeordner>
Der Ausgabeordner ist Pflicht und darf nicht im Repo liegen, ausser unter temp/ (gitignoriert).
Liest ingest/glossar-554/literatur.tsv; schreibt zotero-abgleich.tsv und
zotero-rohantworten.json in den Ausgabeordner; im Repo aendert es nichts. Wer die
eingecheckte zotero-abgleich.tsv erneuern will, vergleicht und kopiert bewusst; die
Rohantworten liegen nicht im Repo. Der Lauf ruft die Zotero-API
je Werk, Gruppe und Suchanfrage ab (mit Pause); zum Nachpruefen deshalb einen Ordner ausserhalb des Repos angeben.
"""
import csv, json, re, sys, time, unicodedata, urllib.parse, urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[2]
LIT = REPO / "ingest" / "glossar-554" / "literatur.tsv"
if len(sys.argv) < 2:
    sys.exit("FEHLER: Ausgabeordner fehlt. Aufruf: zotero-abgleich-554.py <ausgabeordner>")
HERE = Path(sys.argv[1]).resolve()
if (HERE == REPO or REPO in HERE.parents) and REPO / "temp" not in HERE.parents and HERE != REPO / "temp":
    sys.exit("FEHLER: Ausgabeordner liegt im Repo (erlaubt nur unter temp/): %s" % HERE)
HERE.mkdir(parents=True, exist_ok=True)
GRUPPEN = {"5043625": "Werk-Editionen", "4876216": "Textreihen"}
PAUSE = 1.2
SKIP = {"note", "attachment", "annotation"}

# werk_id: (Suchanfragen, Nachname oder None, Titelstichwoerter, Vorname oder None)
E = {
 "adamson": (["Adamson"], "adamson", [], None),
 "adelung": (["Adelung"], "adelung", [], None),
 "barton": (["Barton"], "barton", [], None),
 "bech": (["Bech"], "bech", [], None),
 "becker": (["Becker"], "becker", [], None),
 "berendes": (["Berendes"], "berendes", [], None),
 "birlinger": (["Birlinger"], "birlinger", [], None),
 "blaschitz": (["Blaschitz"], "blaschitz", [], None),
 "bleuler": (["Bleuler"], "bleuler", [], None),
 "bmz": (["Benecke"], "benecke", [], None),
 "borst": (["Borst"], "borst", [], None),
 "bwb": (["Bayerisches Wörterbuch"], None, ["bayerisches", "worterbuch"], None),
 "dwb": (["Deutsches Wörterbuch"], None, ["deutsches", "worterbuch"], None),
 "dwds": (["DWDS"], None, ["dwds"], None),
 "elsmw": (["Elsässischen Mundart"], None, ["mundart"], None),
 "ewd": (["Pfeifer"], "pfeifer", ["etymologisches"], None),
 "falke": (["Falke"], "falke", [], None),
 "feyl": (["Feyl"], "feyl", [], None),
 "findebuch": (["Findebuch"], None, ["findebuch"], None),
 "fnhdwb": (["Frühneuhochdeutsches Wörterbuch"], None, ["neuhochdeutsches", "worterbuch"], None),
 "friedrich": (["Phraseologisches Wörterbuch"], None, ["phraseologisches"], None),
 "frisch": (["Frisch"], "frisch", [], None),
 "gervinus": (["Gervinus"], "gervinus", [], None),
 "gloning": (["Gloning"], "gloning", [], None),
 "grafetstaetter": (["Grafetstätter", "Grafetstaetter"], "grafetstatter", [], None),
 "hanauska": (["Hanauska"], "hanauska", [], None),
 "hausner": (["Hausner"], "hausner", [], None),
 "hepp": (["Hepp"], "hepp", [], None),
 "heyne": (["Heyne"], "heyne", [], None),
 "hofmeister_a": (["Hofmeister"], "hofmeister", [], "andrea"),
 "hofmeister_w": (["Hofmeister"], "hofmeister", [], "wernfried"),
 "huschenbett": (["Huschenbett"], "huschenbett", [], None),
 "keinz": (["Keinz"], "keinz", [], None),
 "kern": (["Kern"], "kern", [], None),
 "kfnhdwb": (["Kleines Frühneuhochdeutsches"], None, ["kleines", "neuhochdeutsches"], None),
 "klug": (["Klug"], "klug", [], None),
 "koebler": (["Köbler", "Koebler"], "kobler", [], None),
 "koppitz": (["Koppitz"], "koppitz", [], None),
 "krunitz": (["Krünitz", "Krunitz"], "krunitz", [], None),
 "kuehtreiber": (["Kühtreiber", "Kuehtreiber"], "kuhtreiber", [], None),
 "kunde": (["Küpper", "Kuepper"], "kupper", [], None),
 "leitzmann": (["Leitzmann"], "leitzmann", [], None),
 "lemmer": (["Lemmer"], "lemmer", [], None),
 "lexer": (["Lexer"], "lexer", [], None),
 "loehneysen": (["Löhneysen", "Loehneysen"], "lohneysen", [], None),
 "luehr": (["Lühr", "Luehr"], "luhr", [], None),
 "meyer": (["Meyer"], "meyer", [], None),
 "mwb": (["Mittelhochdeutsches Wörterbuch"], None, ["mittelhochdeutsches", "worterbuch"], None),
 "nellmann": (["Nellmann"], "nellmann", [], None),
 "neumann": (["Neumann"], "neumann", [], "alfred"),
 "olt": (["Olt"], "olt", [], None),
 "panzer": (["Panzer"], "panzer", [], None),
 "pelzlex": (["Pelzlexikon"], None, ["pelzlexikon"], None),
 "pfwb": (["Pfälzisches Wörterbuch"], None, ["pfalzisches", "worterbuch"], None),
 "pieth": (["Pieth"], "pieth", [], None),
 "pohl": (["Pohl"], "pohl", [], None),
 "schacht": (["Schacht"], "schacht", [], None),
 "scherer": (["Scherer"], "scherer", [], None),
 "schichta": (["Schichta"], "schichta", [], None),
 "schiffmann": (["Schiffmann"], "schiffmann", [], None),
 "schmeller": (["Schmeller"], "schmeller", [], None),
 "schroeder": (["Schröder", "Schroeder"], "schroder", [], None),
 "schubert": (["Schubert"], "schubert", [], None),
 "schulz": (["Schulz"], "schulz", [], None),
 "simrock": (["Simrock"], "simrock", [], None),
 "sorbello": (["Sorbello"], "sorbello", [], None),
 "steinbauer": (["Steinbauer"], "steinbauer", [], None),
 "stoewer": (["Stöwer", "Stoewer"], "stower", [], None),
 "stosch": (["Stosch"], "stosch", [], None),
 "strauch": (["Strauch"], "strauch", [], None),
 "weick": (["Weick"], "weick", [], None),
 "wikipedia": (["Pfaffenschnittchen"], None, ["pfaffenschnittchen"], None),
 "wortschaetze": (["WortSchätze"], None, ["wortschatze"], None),
 "yao": (["Yao"], "yao", [], "shao"),
 "zeppezauer": (["Zeppezauer"], "zeppezauer", [], None),
 "zingerle": (["Zingerle"], "zingerle", [], None),
}


def fold(s):
    s = unicodedata.normalize("NFKD", s.casefold())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("ß", "ss")
    for a in ("ae", "oe", "ue"):
        s = s.replace(a, a[0])
    return s


def get(group, q):
    params = urllib.parse.urlencode({"q": q, "qmode": "titleCreatorYear", "format": "json", "limit": 50})
    url = "https://api.zotero.org/groups/%s/items?%s" % (group, params)
    req = urllib.request.Request(url, headers={"Zotero-API-Version": "3", "User-Agent": "MHDBDB-554-Abgleich/1.0 (read-only)"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            if r.status != 200:
                sys.exit("ABBRUCH: HTTP %s bei %s" % (r.status, url))
            data = json.load(r)
    except Exception as e:
        sys.exit("ABBRUCH: %r bei %s" % (e, url))
    time.sleep(PAUSE)
    return data


def cand_info(it):
    d = it["data"]
    cr = d.get("creators", [])
    names = [(c.get("lastName") or c.get("name") or "", c.get("firstName") or "") for c in cr]
    m = re.search(r"\d{4}", d.get("date", "") or "")
    return {
        "key": it["key"], "type": d.get("itemType", ""), "title": d.get("title", "") or "",
        "year": m.group(0) if m else "", "names": names,
        "text": fold(" ".join([d.get("title", "") or "", d.get("bookTitle", "") or "",
                               d.get("publicationTitle", "") or "", d.get("shortTitle", "") or ""])),
        "creators": ", ".join(n[0] for n in names[:3]),
    }


def matches(c, sur, kws, first):
    if sur:
        ok = any(sur in fold(n[0]) and (not first or fold(n[1]).startswith(first)) for n in c["names"])
        if not ok:
            return False
    return all(k in c["text"] for k in kws)


def main():
    rows = list(csv.DictReader(open(LIT, encoding="utf-8"), delimiter="\t"))
    werke = {}
    for r in rows:
        w = werke.setdefault(r["werk_id"], {"werk": r["werk"], "art": r["art"], "n": 0, "jahre": set()})
        w["n"] += 1
        w["jahre"].update(j for j in r["jahre_im_satz"].split(";") if j)
    fehl = set(werke) - set(E)
    if fehl or set(E) - set(werke):
        sys.exit("ABBRUCH: Zuordnung unvollstaendig %s %s" % (sorted(fehl), sorted(set(E) - set(werke))))
    print("Zeilen", len(rows), "Werke", len(werke))
    roh = {}
    out = []
    for wid in sorted(werke):
        w = werke[wid]
        qs, sur, kws, first = E[wid]
        for g, gname in GRUPPEN.items():
            seen = {}
            for q in qs:
                items = get(g, q)
                roh["%s|%s|%s" % (g, wid, q)] = [(i["key"], i["data"].get("itemType"), i["data"].get("title"), i["data"].get("date")) for i in items]
                for i in items:
                    if i["data"].get("itemType") in SKIP:
                        continue
                    seen[i["key"]] = cand_info(i)
            cands = [c for c in seen.values() if matches(c, sur, kws, first)]
            cands.sort(key=lambda c: (c["year"], c["key"]))
            jahre = w["jahre"]
            bem = []
            if not cands:
                klasse = "fehlt"
                bem.append("%d Roh-Treffer der Suche, keiner passt auf Nachname/Titelstichwort" % len(seen))
            elif len(cands) == 1:
                c = cands[0]
                if kws:
                    klasse = "vorhanden"
                    bem.append("Titel enthaelt %s" % "+".join(kws) + (" und Nachname" if sur else ""))
                elif c["year"] and c["year"] in jahre:
                    klasse = "vorhanden"
                    bem.append("Nachname und Jahr %s (Jahr im Satz der Glossarstelle)" % c["year"])
                else:
                    klasse = "wahrscheinlich"
                    bem.append("nur Nachname trifft; Jahre im Satz: %s, Zotero-Jahr: %s" % (";".join(sorted(jahre)) or "keine", c["year"] or "keins"))
            else:
                ym = [c for c in cands if c["year"] and c["year"] in jahre] if not kws else []
                if len(ym) == 1:
                    cands = ym + [c for c in cands if c not in ym]
                    klasse = "vorhanden"
                    bem.append("%d Kandidaten, genau einer mit Jahr aus dem Satz (%s); erster Eintrag" % (len(cands), ";".join(sorted(jahre))))
                else:
                    klasse = "wahrscheinlich"
                    bem.append("%d Kandidaten, nicht eindeutig (Jahre im Satz: %s)" % (len(cands), ";".join(sorted(jahre)) or "keine"))
            if len(cands) > 6:
                bem.append("nur die ersten 6 Kandidaten gelistet, insgesamt %d" % len(cands))
                shown = cands[:6]
            else:
                shown = cands
            out.append({
                "werk": "%s [%s]" % (w["werk"], wid), "anzahl_zitate": w["n"], "klasse": klasse,
                "gruppe": "%s (%s)" % (g, gname),
                "item_key": " | ".join(c["key"] for c in shown),
                "zotero_titel": " | ".join("%s: %s" % (c["creators"], c["title"][:90]) for c in shown),
                "zotero_jahr": " | ".join(c["year"] for c in shown),
                "bemerkung": "; ".join(bem),
            })
            print(wid, g, klasse, len(cands), flush=True)
    cols = ["werk", "anzahl_zitate", "klasse", "gruppe", "item_key", "zotero_titel", "zotero_jahr", "bemerkung"]
    with open(HERE / "zotero-abgleich.tsv", "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, cols, delimiter="\t", lineterminator="\n")
        wr.writeheader()
        wr.writerows(out)
    json.dump(roh, open(HERE / "zotero-rohantworten.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("fertig", len(out), "Zeilen")


main()
