#!/usr/bin/env python3
"""Datierungen aus dem Handschriftencensus-Cache normalisieren (#118).

Liest nur den Cache von hsc_abruf.py (kein Netz), authority-files/works.xml, die
TEI-Header und docs/data/linecode-templates.csv. Schreibt nach --out:

  handschriften.csv  je (werk_id, hs_id): Freitext woertlich, notBefore/notAfter,
                     Regel, unsicher, Gegenprobe
  werke.csv          je HSC-Werk: terminus ante quem (kleinstes notAfter ueber die
                     normalisierten Handschriften) neben den Legacy-Daten.
                     KEIN notBefore fuer das Werk: eine Handschrift datiert den
                     Text nur nach oben. taq_unsicher zaehlt die Handschriften, die
                     nicht in den taq eingehen (unnormalisiert oder ohne Angabe) und
                     deshalb aelter sein koennten.
  siglen.csv         je TEI-Datei: Werk ueber msIdentifier/@corresp, taq, Legacy
  unnormalisiert.txt jede nicht normalisierte entstehungszeit mit Haeufigkeit

Legacy-Spalten eines Werks mit mehreren Siglen: legacy_von = kleinstes Datum von,
legacy_bis = groesstes Datum bis; widerspruch = ja, wenn legacy_von > taq_notAfter.

Normalisierung: Regeltabelle REGELN unten. Was keine Regel vollstaendig trifft,
bekommt kein notBefore/notAfter (nie raten). Ein Klammerzusatz am Ende wird
abgetrennt, ausser er traegt selbst eine Datierung (Jahr 700-1700, Jh, Viertel,
Haelfte, Anfang/Mitte/Ende, um/vor/nach, oder, frueher/spaeter, Ordinalzahl mit
Punkt): dann ist der ganze Text unnormalisiert. Die Wortliste haelt der Test
gegen die Namen in REGELN.

Aufruf:
  python scripts/ingest/datierung-118/normalisieren.py [--cache-dir temp/hsc-cache]
      [--out ingest/datierung-118] [--werk N] [--limit K]
"""
import argparse
import collections
import csv
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hsc_abruf  # noqa: E402
from hsc_abruf import HarterFehler  # noqa: E402

REPO = Path(__file__).resolve().parents[3]

JH_MIN, JH_MAX = 8, 18  # plausible Jahrhunderte; alles andere wird nicht normalisiert

# Teilbereiche eines Jahrhunderts in Jahren ab (Jh.-1)*100
ANFANG, MITTE, ENDE = (0, 20), (40, 60), (80, 99)
HAELFTE = {1: (0, 49), 2: (50, 99)}
VIERTEL = {1: (0, 24), 2: (25, 49), 3: (50, 74), 4: (75, 99)}

_JH = r"(?:\s+(?P<jh>\d{1,2})\.?)?"  # optionales Jahrhundert (sonst vom rechten Nachbarn)

# Regeltabelle: (Name, Muster, Art, Berechnung). Reihenfolge = Vorrang.
# Art "abs": absolute Jahre, kein Jahrhundert. Art "jh": braucht ein Jahrhundert
# (aus dem Teil selbst oder vom rechten Nachbarn); Berechnung (match) -> (von, bis)
# relativ zum Jahrhundertanfang. "einheit" gibt an, ob der Teil eine
# Viertel-/Haelften-Angabe traegt (fuer das nackte "1./2. Viertel 13. Jh.").
REGELN = [
    ("jahr_bereich", r"(?P<a>\d{4})\s*[-–]\s*(?P<b>\d{4})", "abs", None),
    ("jahr_um", r"um\s+(?P<a>\d{4})", "abs", None),
    ("jahr", r"(?P<a>\d{4})", "abs", None),
    ("ende_viertel_jh", r"ende\s+(?P<n>[1-4])\.\s*viertel" + _JH, "jh", "viertel"),
    ("viertel_jh", r"(?P<n>[1-4])\.\s*viertel" + _JH, "jh", "viertel"),
    ("haelfte_jh", r"(?P<n>[12])\.\s*h(?:ä|ae)lfte" + _JH, "jh", "haelfte"),
    ("anfang_jh", r"anfang" + _JH, "jh", None),
    ("mitte_jh", r"mitte" + _JH, "jh", None),
    ("ende_jh", r"ende" + _JH, "jh", None),
    ("jh", r"(?P<jh>\d{1,2})\.?", "jh", None),
]
REGELN_KOMPILIERT = [(n, re.compile(m + r"$"), art, einheit) for n, m, art, einheit in REGELN]

RE_KLAMMER_ENDE = re.compile(r"\s*\([^()]*\)\s*$")
# Klammerzusatz mit eigener Datierungsangabe (Jahr 700-1700 oder Datierungswort)
RE_DATIERUNG_IN_KLAMMER = re.compile(
    r"\b(?:[7-9]\d\d|1[0-6]\d\d|1700)\b|jh|jahrhundert|viertel|h(?:ä|ae)lfte"
    r"|\b(?:um|vor|nach|anfang|mitte|ende|oder)\b|\bfr(?:ü|ue)her\b|\bsp(?:ä|ae)ter\b"
    r"|\b\d{1,2}\.(?!\d)")
RE_JH_WORT = re.compile(r"\b(?:jh\.?|jhd\.?|jahrhunderts?)")
RE_TRENNER = re.compile(r"\s*/\s*|\s+oder\s+")


def _teil_bereich(name, m, jh):
    """(von, bis) in absoluten Jahren fuer einen Teil mit bekanntem Jahrhundert."""
    basis = (jh - 1) * 100
    if name == "ende_viertel_jh":
        bis = basis + VIERTEL[int(m.group("n"))][1]
        return bis - 4, bis
    if name == "viertel_jh":
        v, b = VIERTEL[int(m.group("n"))]
    elif name == "haelfte_jh":
        v, b = HAELFTE[int(m.group("n"))]
    elif name == "anfang_jh":
        v, b = ANFANG
    elif name == "mitte_jh":
        v, b = MITTE
    elif name == "ende_jh":
        v, b = ENDE
    elif name == "jh":
        v, b = 0, 99
    else:
        raise AssertionError(name)
    return basis + v, basis + b


def _abs_bereich(name, m):
    a = int(m.group("a"))
    if name == "jahr_bereich":
        b = int(m.group("b"))
        return (a, b) if a <= b else None
    if name == "jahr_um":
        return a - 10, a + 10
    return a, a


def normalisiere(text):
    """-> dict(zustand, von, bis, regel, unsicher).

    zustand: "leer" (None oder nur Leerraum), "normalisiert" oder "unnormalisiert".
    von/bis/regel sind nur bei "normalisiert" gesetzt, sonst None bzw. "".
    """
    ergebnis = {"zustand": "leer", "von": None, "bis": None, "regel": "", "unsicher": False}
    if text is None or not str(text).strip():
        return ergebnis
    roh = str(text).strip()
    ergebnis["zustand"] = "unnormalisiert"
    ergebnis["unsicher"] = "?" in roh
    s = roh
    while True:
        m = RE_KLAMMER_ENDE.search(s)
        if not m:
            break
        if RE_DATIERUNG_IN_KLAMMER.search(m.group(0).lower()):
            return ergebnis  # die Klammer traegt selbst eine Datierung: nicht raten
        s = s[:m.start()]
    s = s.replace("?", "").lower()
    hat_jh = bool(RE_JH_WORT.search(s))
    s = RE_JH_WORT.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return ergebnis
    teile = [t.strip() for t in RE_TRENNER.split(s)]
    if any(not t for t in teile):
        return ergebnis
    bereiche, namen = [], []
    jh_rechts, einheit_rechts = None, None
    for teil in reversed(teile):
        treffer = None
        for name, rx, art, einheit in REGELN_KOMPILIERT:
            m = rx.match(teil)
            if not m:
                continue
            if name == "jh" and einheit_rechts is not None:
                # nackte Zahl vor einer Viertel-/Haelften-Angabe: Ordnungszahl derselben Einheit
                n = int(m.group("jh"))
                if einheit_rechts == "viertel" and 1 <= n <= 4:
                    name, einheit = "viertel_jh", "viertel"
                    m = _Treffer({"n": str(n), "jh": None})
                elif einheit_rechts == "haelfte" and 1 <= n <= 2:
                    name, einheit = "haelfte_jh", "haelfte"
                    m = _Treffer({"n": str(n), "jh": None})
            treffer = (name, m, art, einheit)
            break
        if treffer is None:
            return ergebnis
        name, m, art, einheit = treffer
        if art == "abs":
            b = _abs_bereich(name, m)
            if b is None:
                return ergebnis
            jh_rechts, einheit_rechts = None, None
        else:
            if not hat_jh:
                return ergebnis
            gruppe = m.group("jh")
            jh =int(gruppe) if gruppe else jh_rechts
            if jh is None or not (JH_MIN <= jh <= JH_MAX):
                return ergebnis
            b = _teil_bereich(name, m, jh)
            jh_rechts, einheit_rechts = jh, einheit
        bereiche.append(b)
        namen.append(name)
    namen.reverse()
    ergebnis["zustand"] = "normalisiert"
    ergebnis["von"] = min(b[0] for b in bereiche)
    ergebnis["bis"] = max(b[1] for b in bereiche)
    ergebnis["regel"] = namen[0] if len(namen) == 1 else "vereinigung:" + "+".join(namen)
    return ergebnis


class _Treffer:
    """Match-Ersatz fuer die Ordnungszahl-Umdeutung (nur group())."""

    def __init__(self, gruppen):
        self.gruppen = gruppen

    def group(self, name):
        return self.gruppen.get(name)


def bereinige_vl(text):
    """HTML-Tags entfernen, <sup>2</sup> als hochgestellte Ziffer."""
    if not text:
        return ""
    hoch = {"1": "¹", "2": "²", "3": "³"}
    text = re.sub(r"<sup>\s*([123])\s*</sup>", lambda m: hoch[m.group(1)], text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def txt(x):
    """Textfeld aus dem HSC-JSON: None -> "", HTML-Entities aufloesen."""
    return html.unescape(x) if x else ""


def signaturen(hs):
    st = hs.get("standorte") or {}
    eintraege = st.values() if isinstance(st, dict) else st
    teile = []
    for e in eintraege:
        if not isinstance(e, dict):
            continue
        felder = [html.unescape(str(e.get(k))).strip() for k in ("ort", "bibliothek", "signatur")
                  if e.get(k)]
        if felder:
            teile.append(", ".join(felder))
    return " | ".join(teile)


def lade_legacy(pfad):
    csv.field_size_limit(2 ** 31 - 1)
    with open(pfad, "r", encoding="utf-8-sig", newline="") as f:
        return {r["ID"]: r for r in csv.DictReader(f, delimiter=";")}


def jahr_oder_none(wert, sigle, spalte):
    wert = (wert or "").strip()
    if not wert:
        return None
    try:
        return int(wert)
    except ValueError:
        raise HarterFehler(f"{spalte} bei {sigle} ist keine Jahreszahl: {wert!r}")


def schreibe_csv(pfad, kopf, zeilen):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with open(pfad, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(kopf)
        w.writerows(zeilen)


def leer_wenn_none(x):
    return "" if x is None else x


def baue(werke, texte, erg, legacy):
    """Berechnet alle Tabellen; -> dict mit handschriften, werke, siglen, unnorm, zaehler."""
    norm = {}  # hs_id -> normalisiere()-Ergebnis
    for hid, hs in erg["hs_json"].items():
        norm[hid] = normalisiere(txt(hs["entstehungszeit"]))
    fehlt = set(erg["gegenprobe_fehlt"])

    hs_zeilen = []
    for wid, hids in erg["werk_hss"].items():
        for hid in hids:
            hs, n = erg["hs_json"][hid], norm[hid]
            hs_zeilen.append([
                wid, hid, f"https://handschriftencensus.de/{hid}", signaturen(hs),
                txt(hs["entstehungszeit"]), txt(hs["schreibsprache"]),
                leer_wenn_none(n["von"]), leer_wenn_none(n["bis"]), n["regel"],
                "ja" if n["unsicher"] else "",
                "fehlt" if (wid, hid) in fehlt else "ok"])

    werk_zeilen, taq_je_werk, nhss_je_werk = [], {}, {}
    for wid, hids in erg["werk_hss"].items():
        info = werke[wid]
        zustaende = collections.Counter(norm[h]["zustand"] for h in hids)
        datiert = sorted((norm[h]["bis"], h) for h in hids if norm[h]["zustand"] == "normalisiert")
        taq, taq_hs = (datiert[0] if datiert else (None, None))
        taq_je_werk[wid], nhss_je_werk[wid] = taq, len(hids)
        voneinander = [(jahr_oder_none(legacy[s]["Datum von"], s, "Datum von"),
                        jahr_oder_none(legacy[s]["Datum bis"], s, "Datum bis"))
                       for s in info["siglen"] if s in legacy]
        vons = [v for v, _ in voneinander if v is not None]
        biss = [b for _, b in voneinander if b is not None]
        lv, lb = (min(vons) if vons else None), (max(biss) if biss else None)

        def sammle(spalte):
            gesehen = []
            for s in info["siglen"]:
                t = (legacy.get(s, {}).get(spalte) or "").strip()
                if t and t not in gesehen:
                    gesehen.append(t)
            return " | ".join(gesehen)

        n_unnorm, n_leer = zustaende["unnormalisiert"], zustaende["leer"]
        werk_zeilen.append([
            wid, f"https://handschriftencensus.de/werke/{wid}",
            " | ".join(info["work_xml_ids"]), " | ".join(info["siglen"]),
            txt(erg["werk_json"][wid]["titel"]), len(hids), zustaende["normalisiert"],
            n_unnorm, n_leer, leer_wenn_none(taq), leer_wenn_none(taq_hs),
            txt(erg["hs_json"][taq_hs]["entstehungszeit"]) if taq_hs else "",
            n_unnorm + n_leer, bereinige_vl(erg["werk_json"][wid]["vlverweis"]),
            leer_wenn_none(lv), leer_wenn_none(lb), sammle("Datum Abweichung"),
            "ja" if (lv is not None and taq is not None and lv > taq) else ""])

    sig_zeilen = []
    for sigle, wxid, hsc in texte:
        row = legacy.get(sigle)
        lv = jahr_oder_none(row["Datum von"], sigle, "Datum von") if row else None
        lb = jahr_oder_none(row["Datum bis"], sigle, "Datum bis") if row else None
        sig_zeilen.append([sigle, wxid, leer_wenn_none(hsc),
                           leer_wenn_none(taq_je_werk.get(hsc)),
                           leer_wenn_none(nhss_je_werk.get(hsc)),
                           leer_wenn_none(lv), leer_wenn_none(lb)])

    unnorm = collections.Counter(
        txt(erg["hs_json"][h]["entstehungszeit"]) for h, n in norm.items()
        if n["zustand"] == "unnormalisiert")
    z = collections.Counter(n["zustand"] for n in norm.values())
    return {"handschriften": hs_zeilen, "werke": werk_zeilen, "siglen": sig_zeilen,
            "unnorm": unnorm, "zustaende": z, "taq": taq_je_werk}


KOPF_HS = ["werk_id", "hs_id", "hs_url", "signaturen", "entstehungszeit", "schreibsprache",
           "notBefore", "notAfter", "regel", "unsicher", "gegenprobe"]
KOPF_WERKE = ["werk_id", "hsc_url", "work_xml_ids", "siglen", "titel", "n_hss", "n_datiert",
              "n_unnormalisiert", "n_leer", "taq_notAfter", "taq_hs_id", "taq_entstehungszeit",
              "taq_unsicher", "vlverweis", "legacy_von", "legacy_bis", "legacy_abweichung",
              "widerspruch"]
KOPF_SIGLEN = ["sigle", "work_xml_id", "werk_id", "taq_notAfter", "n_hss", "legacy_von",
               "legacy_bis"]


def main(argv=None):
    ap = argparse.ArgumentParser(description="HSC-Datierungen normalisieren (#118)")
    ap.add_argument("--cache-dir", default=str(REPO / "temp" / "hsc-cache"))
    ap.add_argument("--out", default=str(REPO / "ingest" / "datierung-118"))
    ap.add_argument("--linecode", default=str(REPO / "docs" / "data" / "linecode-templates.csv"))
    ap.add_argument("--limit", type=int)
    ap.add_argument("--werk", type=int)
    a = ap.parse_args(argv)
    try:
        werke, texte = hsc_abruf.werkliste()
        auswahl = hsc_abruf.waehle_werke(werke, a.limit, a.werk)
        erg = hsc_abruf.lauf(auswahl, hsc_abruf.Cache(a.cache_dir, offline=True))
        legacy = lade_legacy(a.linecode)
        t = baue(werke, texte, erg, legacy)
    except HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        return 1
    out = Path(a.out)
    schreibe_csv(out / "handschriften.csv", KOPF_HS, t["handschriften"])
    schreibe_csv(out / "werke.csv", KOPF_WERKE, t["werke"])
    schreibe_csv(out / "siglen.csv", KOPF_SIGLEN, t["siglen"])
    zeilen = [f"{n}\t{text}" for text, n in sorted(t["unnorm"].items(), key=lambda x: (-x[1], x[0]))]
    (out / "unnormalisiert.txt").write_text("\n".join(zeilen) + ("\n" if zeilen else ""),
                                            encoding="utf-8", newline="")
    z = t["zustaende"]
    b = sum(z.values())
    print(f"Datierungen: {b} Handschriften (normalisiert {z['normalisiert']} + "
          f"unnormalisiert {z['unnormalisiert']}, leer {z['leer']})")
    mit_taq = sum(1 for v in t["taq"].values() if v is not None)
    texte_taq = sum(1 for s in t["siglen"] if s[3] != "")
    texte_hsc = sum(1 for x in texte if x[2] is not None)
    print(f"Werke: {len(t['werke'])} (davon mit taq {mit_taq}), Texte: {len(t['siglen'])} "
          f"(davon mit HSC-Werk {texte_hsc}, mit taq {texte_taq}); "
          f"unnormalisierte Freitexte: {len(t['unnorm'])} verschiedene")
    return 0


if __name__ == "__main__":
    sys.exit(main())
