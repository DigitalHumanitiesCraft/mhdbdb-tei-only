#!/usr/bin/env python3
"""Tests fuer hsc_abruf.py und normalisieren.py (#118), pytest-frei.

Aufruf: python scripts/ingest/datierung-118/test_normalisieren.py
Kein Netz: die Laufe gegen testdaten/ sind --offline. Beendet mit Exit 1, wenn
ein Test fehlschlaegt.
"""
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import normalisieren as nm  # noqa: E402

TESTDATEN = HIER / "testdaten"
ABRUF = HIER / "hsc_abruf.py"
NORM = HIER / "normalisieren.py"

# (Freitext, von, bis, regel oder None = nicht pruefen, unsicher)
FAELLE = [
    ("2. Viertel / Mitte 13. Jh.", 1225, 1260, "vereinigung:viertel_jh+mitte_jh", False),
    ("Ende 1. Viertel 14. Jh.", 1320, 1324, "ende_viertel_jh", False),
    ("Ende 1. Viertel 14. Jh. (Karin Schneider briefl. am 30.11.2007)", 1320, 1324,
     "ende_viertel_jh", False),
    ("Ende 13./Anfang 14. Jh.", 1280, 1320, "vereinigung:ende_jh+anfang_jh", False),
    ("13./14. Jh.", 1200, 1399, "vereinigung:jh+jh", False),
    ("13. Jh.", 1200, 1299, "jh", False),
    ("1. Hälfte 14. Jh.", 1300, 1349, "haelfte_jh", False),
    ("2. Hälfte 14. Jh.", 1350, 1399, "haelfte_jh", False),
    ("1. Viertel 13. Jh.", 1200, 1224, "viertel_jh", False),
    ("2. Viertel 13. Jh.", 1225, 1249, "viertel_jh", False),
    ("3. Viertel 15. Jh.", 1450, 1474, "viertel_jh", False),
    ("4. Viertel 12. Jh.", 1175, 1199, "viertel_jh", False),
    ("Anfang 13. Jh.", 1200, 1220, "anfang_jh", False),
    ("Mitte 14. Jh.", 1340, 1360, "mitte_jh", False),
    ("Ende 15. Jh.", 1480, 1499, "ende_jh", False),
    ("um 1300", 1290, 1310, "jahr_um", False),
    ("1350", 1350, 1350, "jahr", False),
    ("1350-1360", 1350, 1360, "jahr_bereich", False),
    ("1350–1360", 1350, 1360, "jahr_bereich", False),
    ("13. Jh.?", 1200, 1299, "jh", True),
    ("13. Jh. (?)", 1200, 1299, "jh", True),
    ("1./2. Hälfte 13. Jh.", 1200, 1299, "vereinigung:haelfte_jh+haelfte_jh", False),
    ("1. oder 2. Viertel 14. Jh.", 1300, 1349, "vereinigung:viertel_jh+viertel_jh", False),
    ("Anfang / Mitte 14. Jh.", 1300, 1360, "vereinigung:anfang_jh+mitte_jh", False),
    ("1280 / 1300", 1280, 1300, "vereinigung:jahr+jahr", False),
    ("ENDE 13. JH.", 1280, 1299, "ende_jh", False),
    ("14. Jahrhundert", 1300, 1399, "jh", False),
]

# Freitext, der keine Regel vollstaendig trifft: nie raten
UNNORMALISIERT = [
    "ohne Datierung",
    "nach 1250",
    "vor 1300",
    "1270/80",
    "Ende 1. Viertel",          # kein Jahrhundert
    "13.",                      # keine Jh.-Angabe
    "Mitte 25. Jh.",            # unplausibles Jahrhundert
    "1350-1340",                # umgekehrter Bereich
    "(1250)",                   # nur Klammer
    "Mitte 1. Viertel 14. Jh.",  # Mitte im Viertel ist nicht definiert
    "um 13. Jh.",
    "Mitte 14. Jh., vermutlich",
    "13. Jh. / ",               # leerer Teil der Vereinigung
    "kurz vor 1300 (?)",
]

LEER = [None, "", "   "]

zaehler = {"faelle": 0}


def pruefe(bedingung, meldung):
    zaehler["faelle"] += 1
    if not bedingung:
        raise AssertionError(meldung)


def test_regeltabelle():
    for text, von, bis, regel, unsicher in FAELLE:
        n = nm.normalisiere(text)
        pruefe(n["zustand"] == "normalisiert", f"{text!r}: Zustand {n['zustand']}")
        pruefe((n["von"], n["bis"]) == (von, bis), f"{text!r}: {n['von']}..{n['bis']} statt {von}..{bis}")
        if regel is not None:
            pruefe(n["regel"] == regel, f"{text!r}: Regel {n['regel']!r} statt {regel!r}")
        pruefe(n["unsicher"] == unsicher, f"{text!r}: unsicher {n['unsicher']}")


def test_negativ():
    for text in UNNORMALISIERT:
        n = nm.normalisiere(text)
        pruefe(n["zustand"] == "unnormalisiert", f"{text!r} haette nicht normalisiert werden duerfen: {n}")
        pruefe(n["von"] is None and n["bis"] is None and n["regel"] == "", f"{text!r}: Werte gesetzt")
    for text in LEER:
        pruefe(nm.normalisiere(text)["zustand"] == "leer", f"{text!r} ist leer")
    pruefe(nm.normalisiere("kurz vor 1300 (?)")["unsicher"], "? in Klammer setzt unsicher auch bei unnormalisiert")


def test_hilfen():
    pruefe(nm.bereinige_vl("Vgl. Joachim Bumke, in: <sup>2</sup>VL 10 (1999), Sp. 1376-1418.")
           == "Vgl. Joachim Bumke, in: ²VL 10 (1999), Sp. 1376-1418.", "vlverweis")
    pruefe(nm.bereinige_vl(None) == "", "vlverweis None")
    s = nm.signaturen({"standorte": {"1": {"ort": "Amberg", "bibliothek": "Bibl.", "signatur": "Ms. 1"},
                                     "2": {"ort": "Berlin", "signatur": "mgf 1"}}})
    pruefe(s == "Amberg, Bibl., Ms. 1 | Berlin, mgf 1", f"signaturen: {s}")
    pruefe(nm.signaturen({"standorte": None}) == "", "signaturen None")


def lauf(skript, *args):
    return subprocess.run([sys.executable, "-P", "-E", str(skript), *args],
                          capture_output=True, text=True, encoding="utf-8")


def kopiere_testdaten(ziel):
    ziel.mkdir(parents=True, exist_ok=True)
    for p in TESTDATEN.iterdir():
        shutil.copy(p, ziel / p.name)


def lies_csv(pfad):
    with open(pfad, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_cli(tmp):
    cache = tmp / "cache"
    kopiere_testdaten(cache)

    # vollstaendiger Offline-Lauf
    r = lauf(ABRUF, "--werk", "437", "--offline", "--cache-dir", str(cache))
    pruefe(r.returncode == 0, f"Offline-Lauf: Exit {r.returncode}: {r.stderr}")
    pruefe("Werke: 1 (abgerufen 0 + Cache 1)" in r.stdout, r.stdout)
    pruefe("Handschriften: 2 (davon 0 in mehreren Werken)" in r.stdout, r.stdout)
    pruefe("Gegenprobe fehlt: 0" in r.stdout and "Parsefehler: 0" in r.stdout, r.stdout)
    print("hsc_abruf:", r.stdout.strip())

    out = tmp / "out"
    r = lauf(NORM, "--werk", "437", "--cache-dir", str(cache), "--out", str(out))
    pruefe(r.returncode == 0, f"normalisieren: Exit {r.returncode}: {r.stderr}")
    print("normalisieren:", r.stdout.strip().replace("\n", "\n              "))
    pruefe("Datierungen: 2 Handschriften (normalisiert 2 + unnormalisiert 0, leer 0)" in r.stdout, r.stdout)
    werke = lies_csv(out / "werke.csv")
    pruefe(len(werke) == 1, f"werke.csv: {len(werke)} Zeilen")
    w = werke[0]
    pruefe(w["werk_id"] == "437" and w["taq_notAfter"] == "1260" and w["taq_hs_id"] == "1037", str(w))
    pruefe(w["taq_entstehungszeit"] == "2. Viertel / Mitte 13. Jh.", str(w))
    pruefe(w["n_hss"] == "2" and w["n_datiert"] == "2" and w["taq_unsicher"] == "0", str(w))
    pruefe(w["vlverweis"] == "Vgl. Joachim Bumke, in: ²VL 10 (1999), Sp. 1376-1418.", w["vlverweis"])
    hss = {h["hs_id"]: h for h in lies_csv(out / "handschriften.csv")}
    pruefe(set(hss) == {"1037", "1051"}, str(set(hss)))
    pruefe((hss["1037"]["notBefore"], hss["1037"]["notAfter"]) == ("1225", "1260"), str(hss["1037"]))
    pruefe((hss["1051"]["notBefore"], hss["1051"]["notAfter"]) == ("1320", "1324"), str(hss["1051"]))
    pruefe(hss["1051"]["entstehungszeit"].startswith("Ende 1. Viertel 14. Jh. (Karin"), "woertlich")
    pruefe(hss["1037"]["gegenprobe"] == "ok" and hss["1037"]["hs_url"] == "https://handschriftencensus.de/1037", "hs")
    pruefe(hss["1037"]["signaturen"] == "Amberg, Provinzialbibl., 8 Ms. 1 | Berlin, Staatsbibl., mgf 734 Nr. 8", hss["1037"]["signaturen"])
    siglen = lies_csv(out / "siglen.csv")
    pruefe(len(siglen) == 667, f"siglen.csv: {len(siglen)} Zeilen")
    pz = [s for s in siglen if s["werk_id"] == "437"]
    pruefe(pz and all(s["taq_notAfter"] == "1260" and s["n_hss"] == "2" for s in pz), str(pz))
    pruefe((out / "unnormalisiert.txt").read_text(encoding="utf-8") == "", "unnormalisiert.txt leer")
    for name in ("handschriften.csv", "werke.csv", "siglen.csv", "unnormalisiert.txt"):
        pruefe(b"\r" not in (out / name).read_bytes(), f"CR in {name}")

    # Cache-Fehltreffer: 1051.json fehlt -> Exit != 0 mit Pfad
    (cache / "1051.json").unlink()
    r = lauf(ABRUF, "--werk", "437", "--offline", "--cache-dir", str(cache))
    pruefe(r.returncode != 0, "Fehltreffer muss abbrechen")
    pruefe("Cache-Fehltreffer" in r.stderr and str(cache / "1051.json") in r.stderr, r.stderr)

    # nur Links ohne Handschrift: harter Fehler
    kopiere_testdaten(cache)
    (cache / "werke_437.html").write_text('<a href="/impressum">x</a><a href="/werke/437/x">y</a>', encoding="utf-8")
    r = lauf(ABRUF, "--werk", "437", "--offline", "--cache-dir", str(cache))
    pruefe(r.returncode != 0 and "kein Handschrift-Link" in r.stderr, r.stderr)

    # fehlender Pflichtschluessel
    kopiere_testdaten(cache)
    d = json.loads((cache / "1037.json").read_text(encoding="utf-8"))
    del d["schreibsprache"]
    (cache / "1037.json").write_text(json.dumps(d), encoding="utf-8")
    r = lauf(ABRUF, "--werk", "437", "--offline", "--cache-dir", str(cache))
    pruefe(r.returncode != 0 and "schreibsprache" in r.stderr and "1037.json" in r.stderr, r.stderr)

    # Gegenprobe: 1051 verweist auf ein anderes Werk -> zaehlt, bricht nicht ab
    kopiere_testdaten(cache)
    d = json.loads((cache / "1051.json").read_text(encoding="utf-8"))
    d["gnd"] = [{"werk_id": 999}]
    (cache / "1051.json").write_text(json.dumps(d), encoding="utf-8")
    r = lauf(ABRUF, "--werk", "437", "--offline", "--cache-dir", str(cache))
    pruefe(r.returncode == 0 and "Gegenprobe fehlt: 1 (von 2 Paaren)" in r.stdout, r.stdout + r.stderr)
    r = lauf(NORM, "--werk", "437", "--cache-dir", str(cache), "--out", str(out))
    pruefe(r.returncode == 0, r.stderr)
    hss = {h["hs_id"]: h for h in lies_csv(out / "handschriften.csv")}
    pruefe(hss["1051"]["gegenprobe"] == "fehlt" and hss["1037"]["gegenprobe"] == "ok", str(hss))


def main():
    test_regeltabelle()
    test_negativ()
    test_hilfen()
    tmp = Path(tempfile.mkdtemp(prefix="datierung118-"))
    try:
        test_cli(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"OK: {zaehler['faelle']} Pruefungen "
          f"({len(FAELLE)} Regelfaelle, {len(UNNORMALISIERT)} nicht normalisierbar, {len(LEER)} leer)")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
