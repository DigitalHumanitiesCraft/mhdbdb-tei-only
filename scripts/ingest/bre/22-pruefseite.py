#!/usr/bin/env python3
"""22-pruefseite.py: HTML-Pruefseite zum Pruefpaket der Weingruesse (BRE, #147).

Baut aus den vier TSV des Pruefpakets (ingest/bre/pruefung/, erzeugt von 20-pruefpaket.py)
eine eigenstaendige HTML-Seite, auf der KZW die maschinellen Zuweisungen selbst prueft.
Pruefseitenmuster nach #443 (wie examples/review-pages/364-lemma-review.html): ein
maschineller Vorschlag ist keine bestaetigte Antwort, nichts ist vorausgewaehlt, die Zustaende
unberuehrt / Entwurf / entschieden / geprueft-offen bleiben unterscheidbar, der Arbeitsstand
liegt im localStorage des Browsers, Export als JSON und als HTML-Bericht, JSON-Import zum
Fortsetzen.

Umfang:
  lemma-verdacht.tsv  alle Zeilen
  lemma.tsv, wortart.tsv, bedeutung.tsv  je eine Stichprobe von STICHPROBE Zeilen, geschichtet
      nach der Spalte `sicherheit` (low / medium): jede Schicht bekommt ihren Anteil an der
      Datei (proportional, groesster Rest, bei Gleichstand die Schicht in der Reihenfolge
      SCHICHTEN), gezogen mit random.Random(SEED) je Datei, Schichten in fester Reihenfolge,
      Zeilen nach `nr` sortiert. Die Seite nennt Nenner und Seed.

Kontext je Wort: der Vers (<l>) oder die Ueberschrift (<head>), in dem das Wort steht, und
der Vers davor und danach im selben Abschnitt, aus ingest/bre/BRE_*.tei.xml ueber die xml_id.
Text kommt nur aus diesen TEI-Dateien (Wiki-Transkriptionen), dem Lexikon und den TSV;
aus der Druckausgabe steht nichts auf der Seite.

Harte Fehler (Exit 1, keine Ausgabe): eine TSV mit anderen Spalten als 20-pruefpaket.py
schreibt, eine xml_id, die in keiner TEI-Datei steht, eine unbekannte `sicherheit`, ein Teil
von `andere_moeglichkeiten` oder `zuweisung`, der nicht mit einer Kennung beginnt, eine
schon ausgefuellte Spalte passt/korrektur/anmerkung, ein fehlender Platzhalter im Template.

Exportformat (JSON, Schema mhdbdb-bre-147-pruefseite-v1), damit ein Einspielskript es
direkt lesen kann:
  {"schema": "mhdbdb-bre-147-pruefseite-v1", "issue": 147,
   "fingerprint": <sha256-Praefix der eingebetteten Daten>, "sourceCommit": <git HEAD beim Bau>,
   "sourceDate": <Baudatum>, "seed": 147, "sources": {<Pfad>: <sha256>},  # 4 TSV + TEI
   "exportedAt": <ISO-Zeit>, "reviewer": <Name>,
   "decisions": [ {
       "id": "<datei-kurz>-<nr>",       # z. B. "verdacht-12", "bedeutung-301"
       "datei": "lemma-verdacht.tsv",   # Quelldatei in ingest/bre/pruefung/
       "nr": 12,                        # Spalte nr dieser Datei (Zeilenschluessel)
       "xml_id": "...", "wort": "...", "zuweisung": "<Kennung>",   # zur Gegenprobe
       "passt": "" | "ja" | "nein" | "?",   # -> Spalte passt; "" = nicht geprueft
       "korrektur": "",                 # -> Spalte korrektur: Kennung aus andere_moeglichkeiten,
                                        #    "kein Lemma" oder Freitext
       "anmerkung": "",                 # -> Spalte anmerkung
       "status": "unreviewed" | "decided" | "open",
       "wahl": "" | "ja" | "nein",      # Auswahl, auch als Entwurf
       "korrekturWahl": "" | <Kennung> | "kein Lemma" | "frei", "korrekturFrei": "",
       "reviewer": "...", "updatedAt": <ISO-Zeit> | null } ]}
  passt ist "ja"/"nein" nur bei status decided, "?" bei status open, sonst leer. Bei passt
  "ja" ist korrektur leer. Die Zeile in der TSV ist (datei, nr); xml_id und zuweisung muessen
  dort uebereinstimmen, sonst ist der Export fuer einen anderen Paketstand gemacht.

Aufruf (aus der Repositoriumswurzel):
    python -P -E scripts/ingest/bre/22-pruefseite.py
Schreibt ingest/bre/pruefung/pruefseite.html.
"""
import hashlib
import json
import random
import re
import subprocess
import sys
import urllib.parse
from datetime import date
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_annot as ba  # noqa: E402
import bre_common as bc  # noqa: E402

SEED = 147
STICHPROBE = 50
SCHICHTEN = ["low", "medium"]
SCHEMA = "mhdbdb-bre-147-pruefseite-v1"
PAKET = bc.INGEST_DIR / "pruefung"
TEMPLATE = Path(__file__).resolve().parent / "pruefseite-template.html"
AUSGABE = PAKET / "pruefseite.html"
FELDER = ["nr", "art", "wort", "zeuge", "text", "kontext", "zuweisung", "sicherheit", "begruendung",
          "andere_moeglichkeiten", "belege", "xml_id", "passt", "korrektur", "anmerkung"]
# (Kurzname, Datei, Frage, voll oder Stichprobe, Kennungsmuster)
DATEIEN = [
    ("verdacht", "lemma-verdacht.tsv", "lemma", False, r"lemma_\d+"),
    ("lemma", "lemma.tsv", "lemma", True, r"lemma_\d+"),
    ("wortart", "wortart.tsv", "pos", True, r"[A-Z]{2,4}"),
    ("bedeutung", "bedeutung.tsv", "sense", True, r"lemma_\d+_sense_\d+"),
]
SICHERHEIT_VERDACHT = {"Lemma: auto-single", "Lemma: bulk-llm", "Lemma: instance-llm"}
T = "{http://www.tei-c.org/ns/1.0}"
XID = "{http://www.w3.org/XML/1998/namespace}id"


def fehler(text):
    raise bc.HarterFehler(text)


def sha256(pfad):
    return hashlib.sha256(pfad.read_bytes()).hexdigest()


def kennung(teil, muster, ort):
    """Zerlegt 'lemma_1517 er [POS/PRO] ...' oder 'lemma_1_sense_2 :: ...' in Kennung und Rest."""
    m = re.match(r"(" + muster + r")(?:$|\s)", teil)
    if not m:
        fehler(f"{ort}: beginnt nicht mit einer Kennung ({muster}): {teil[:60]!r}")
    return m.group(1)


def zuteilung(groessen, n):
    """Proportionale Zuteilung von n Plaetzen auf Schichten (groesster Rest)."""
    gesamt = sum(groessen.values())
    if gesamt < n:
        fehler(f"Stichprobe {n} groesser als die Datei ({gesamt})")
    roh = {s: n * g / gesamt for s, g in groessen.items()}
    zahl = {s: int(r) for s, r in roh.items()}
    rest = n - sum(zahl.values())
    for s in sorted(roh, key=lambda s: (-(roh[s] - zahl[s]), SCHICHTEN.index(s)))[:rest]:
        zahl[s] += 1
    return zahl


def lade_tei():
    """xml_id -> (Element, Datei) fuer alle <w> der BRE-Zeugen."""
    woerter = {}
    dateien = sorted(bc.INGEST_DIR.glob("BRE_*.tei.xml"))
    if not dateien:
        fehler("keine TEI-Datei unter ingest/bre/")
    for pfad in dateien:
        baum = etree.parse(str(pfad))
        for w in baum.iter(T + "w"):
            woerter[w.get(XID)] = (w, pfad)
    return woerter


def token_text(el):
    """Text eines <w>/<pc> ohne <note> und ohne XML-Kommentare (deren tail zaehlt)."""
    def rek(e):
        out = e.text or ""
        for c in e:
            if isinstance(c.tag, str) and c.tag != T + "note":
                out += rek(c)
            out += c.tail or ""
        return out
    return re.sub(r"\s+", "", rek(el))


def zeile_tokens(zeile, ziel):
    out = []
    for t in zeile.iter(T + "w", T + "pc"):
        if any(a.tag == T + "note" for a in t.iterancestors()):
            continue
        out.append({"t": token_text(t), "pc": t.tag == T + "pc", "links": t.get("join") == "left",
                    "ziel": t is ziel})
    return out


def stelle(xid, woerter, sigle_zu_zeuge):
    if xid not in woerter:
        fehler(f"xml_id {xid} steht in keiner TEI-Datei unter ingest/bre/")
    w, pfad = woerter[xid]
    zeile = next((a for a in w.iterancestors() if a.tag in (T + "l", T + "head")), None)
    if zeile is None:
        fehler(f"{xid}: weder in <l> noch in <head>")
    abschnitt = next((a for a in w.iterancestors() if a.tag == T + "div"), None)
    reihe = [z for z in abschnitt.iter(T + "l", T + "head")] if abschnitt is not None else [zeile]
    i = reihe.index(zeile)
    verse = []
    for z in reihe[max(0, i - 1): i + 2]:
        verse.append({"n": z.get("n") or ("Überschrift" if z.tag == T + "head" else ""),
                      "kopf": z.tag == T + "head", "tokens": zeile_tokens(z, w)})
    pb = w.xpath("preceding::t:pb[1]/@n", namespaces={"t": T[1:-1]})
    sigle = pfad.name.removesuffix(".tei.xml")
    if sigle not in sigle_zu_zeuge:
        fehler(f"{pfad.name}: Sigle nicht in bre_common.ZEUGEN")
    zeuge, seite = sigle_zu_zeuge[sigle]
    wiki = bc.WIKI_BASIS + "?title=" + urllib.parse.quote((bc.TRANSKRIPTIONS_PRAEFIX + seite).replace(" ", "_"))
    return {"xmlId": xid, "sigle": sigle, "zeuge": zeuge, "blatt": pb[0] if pb else "",
            "vers": zeile.get("n") or "", "verse": verse, "wiki": wiki}


def baue_zeile(kurz, datei, phase, muster, z, woerter, sigle_zu_zeuge):
    ort = f"{datei} nr {z['nr']}"
    for feld in ("passt", "korrektur", "anmerkung"):
        if z[feld].strip():
            fehler(f"{ort}: Spalte {feld} ist schon ausgefuellt, die Seite baut nur auf einem leeren Paket")
    if kurz == "verdacht":
        if z["sicherheit"] not in SICHERHEIT_VERDACHT:
            fehler(f"{ort}: unbekannte sicherheit {z['sicherheit']!r}")
    elif z["sicherheit"] not in SCHICHTEN:
        fehler(f"{ort}: unbekannte sicherheit {z['sicherheit']!r}")
    zid = kennung(z["zuweisung"].strip(), muster, ort + " zuweisung")
    alternativen = []
    if z["andere_moeglichkeiten"].strip():
        for teil in z["andere_moeglichkeiten"].split(" | "):
            teil = teil.strip()
            alternativen.append({"id": kennung(teil, muster, ort + " andere_moeglichkeiten"), "label": teil})
    ids = z["xml_id"].split()
    if not ids:
        fehler(f"{ort}: xml_id leer")
    if not re.fullmatch(r"\d+", z["belege"]) or not re.fullmatch(r"\d+", z["nr"]):
        fehler(f"{ort}: nr oder belege keine Zahl")
    return {"id": f"{kurz}-{z['nr']}", "datei": datei, "kurz": kurz, "phase": phase, "nr": int(z["nr"]),
            "art": z["art"], "belege": int(z["belege"]), "wort": z["wort"], "zeuge": z["zeuge"],
            "text": z["text"], "kontext": z["kontext"], "zuweisung": {"id": zid, "label": z["zuweisung"]},
            "sicherheit": z["sicherheit"], "begruendung": z["begruendung"], "alternativen": alternativen,
            "xmlIds": ids, "stellen": [stelle(x, woerter, sigle_zu_zeuge) for x in ids]}


def main():
    bc.ausgabe_utf8()
    woerter = lade_tei()
    sigle_zu_zeuge = {sig: (zeuge, seite) for zeuge, (seite, sig) in bc.ZEUGEN.items()}
    quellen = {}
    faelle, gruppen = [], []
    for kurz, datei, phase, stichprobe, muster in DATEIEN:
        pfad = PAKET / datei
        zeilen = ba.lies_tsv(pfad, FELDER)
        quellen[f"ingest/bre/pruefung/{datei}"] = sha256(pfad)
        alle = [baue_zeile(kurz, datei, phase, muster, z, woerter, sigle_zu_zeuge) for z in zeilen]
        if len({f["nr"] for f in alle}) != len(alle):
            fehler(f"{datei}: nr nicht eindeutig")
        gruppe = {"id": kurz, "datei": datei, "phase": phase, "gesamt": len(alle), "stichprobe": stichprobe}
        if stichprobe:
            schichten = {s: sorted((f for f in alle if f["sicherheit"] == s), key=lambda f: f["nr"])
                         for s in SCHICHTEN}
            zahl = zuteilung({s: len(v) for s, v in schichten.items()}, STICHPROBE)
            rng = random.Random(SEED)
            gewaehlt = []
            for s in SCHICHTEN:
                gewaehlt += rng.sample(schichten[s], zahl[s])
            gewaehlt.sort(key=lambda f: f["nr"])
            gruppe["schichten"] = {s: {"gesamt": len(schichten[s]), "gezogen": zahl[s]} for s in SCHICHTEN}
        else:
            gewaehlt = alle
        gruppe["anzahl"] = len(gewaehlt)
        gruppe["ids"] = [f["id"] for f in gewaehlt]
        gruppen.append(gruppe)
        faelle += gewaehlt
        teil = (" = " + " + ".join(f"{v['gezogen']} von {v['gesamt']} {s}" for s, v in gruppe["schichten"].items())
                if stichprobe else " (alle)")
        print(f"{datei}: {len(gewaehlt)} von {len(alle)} Zeilen{teil}")
    benutzt = sorted({s["sigle"] for f in faelle for s in f["stellen"]})
    for sig in benutzt:
        p = bc.INGEST_DIR / f"{sig}.tei.xml"
        quellen[f"ingest/bre/{p.name}"] = sha256(p)
    fp = hashlib.sha256(json.dumps({"faelle": faelle, "gruppen": gruppen}, ensure_ascii=False,
                                   sort_keys=True).encode("utf-8")).hexdigest()[:16]
    commit = subprocess.run(["git", "-C", str(bc.REPO), "rev-parse", "HEAD"], capture_output=True,
                            text=True, check=True).stdout.strip()
    daten = {"schema": SCHEMA, "issue": 147, "fingerprint": fp, "date": date.today().isoformat(),
             "commit": commit, "seed": SEED, "stichprobe": STICHPROBE, "sources": quellen,
             "groups": gruppen, "cases": faelle}
    html = TEMPLATE.read_text(encoding="utf-8")
    if html.count("__REVIEW_DATA__") != 1:
        fehler("Platzhalter __REVIEW_DATA__ fehlt im Template oder steht mehrfach")
    nutzlast = json.dumps(daten, ensure_ascii=False).replace("</", "<\\/")
    AUSGABE.write_text(html.replace("__REVIEW_DATA__", nutzlast), encoding="utf-8", newline="\n")
    print(f"Faelle gesamt: {len(faelle)} = " + " + ".join(f"{g['id']} {g['anzahl']}" for g in gruppen))
    print(f"Seed {SEED}, Fingerabdruck {fp}, Commit {commit[:12]}")
    print(f"geschrieben: {AUSGABE.relative_to(bc.REPO).as_posix()} ({AUSGABE.stat().st_size} Bytes)")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
