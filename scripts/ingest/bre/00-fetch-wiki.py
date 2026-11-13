#!/usr/bin/env python3
"""00-fetch-wiki.py: laedt die Weingruss-Seiten des Brevitas-Wikis (#147).

Holt die 21 Transkriptionsseiten ("Weingrüße <X>") und die Einzeltextseiten
(Liste aus dem Rohtext von "Dokumentation Edition Weingrüße") ueber die
MediaWiki-API in den Cache temp/bre-wiki/ (gitignoriert) und schreibt das
Manifest ingest/bre/revisionen.tsv (titel, pageid, revid, timestamp, user,
sha256 des Inhalts). Die Dokumentationsseite und die Hauptseite "Kategorie:Quelle
Weingruß" (Abschnitt "Überlieferung", fuer die Werkzuordnung massgeblich) stehen
ebenfalls im Manifest; fehlt die Hauptseite in einem aelteren Manifest, wird sie mit
bre_common.HAUPT_REVID geladen und angehaengt.

Existiert das Manifest, wird per revid gepinnt geladen und der sha256
geprueft; Abweichung = harter Fehler. Cache-Treffer laden nichts.

  --offline  nur Cache; Fehltreffer = harter Fehler
  --neu      Manifest aus den aktuellen Revisionen neu schreiben (Netz noetig)

Aufruf: python -P -E scripts/ingest/bre/00-fetch-wiki.py [--offline] [--neu]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_common as bc  # noqa: E402

PARAMS = {"action": "query", "prop": "revisions", "rvprop": "ids|timestamp|user|size|content",
          "rvslots": "main", "format": "json", "formatversion": "2"}


def hole(titel, revid, offline):
    """Eine Seite: gepinnt (revid) aus Cache oder Netz, sonst (revid None) aktuell vom Netz."""
    if revid is not None:
        p = bc.cache_pfad(revid)
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8")), "cache"
        if offline:
            raise bc.HarterFehler(f"--offline: Cache-Fehltreffer fuer {titel} (rev {revid})")
        antwort = bc.api_abruf({**PARAMS, "revids": str(revid)})
    else:
        if offline:
            raise bc.HarterFehler(f"--offline ohne Manifest/gepinnte revid fuer {titel}")
        antwort = bc.api_abruf({**PARAMS, "titles": titel})
    seite = bc.seite_aus_antwort(antwort, titel)
    if seite["titel"] != titel:
        raise bc.HarterFehler(f"Titel in der Antwort {seite['titel']!r} != angefragt {titel!r}")
    if revid is not None and int(seite["revid"]) != int(revid):
        raise bc.HarterFehler(f"{titel}: revid {seite['revid']} != gepinnt {revid}")
    kopf = seite["inhalt"].lstrip()[:12].upper()
    if kopf.startswith("#REDIRECT") or kopf.startswith("#WEITERLEIT"):
        raise bc.HarterFehler(f"{titel}: Weiterleitungsseite, kein Inhalt")
    bc.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    bc.cache_pfad(seite["revid"]).write_text(
        json.dumps(seite, ensure_ascii=False, indent=1), encoding="utf-8")
    return seite, "netz"


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--neu", action="store_true")
    a = ap.parse_args()
    try:
        return lauf(a)
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        return 1


def lauf(a):
    pinnen = bc.MANIFEST.exists() and not a.neu
    manifest = bc.lade_manifest() if pinnen else {}
    if a.neu and a.offline:
        raise bc.HarterFehler("--neu braucht das Netz (kein --offline)")

    haupt_neu = pinnen and bc.HAUPT_TITEL not in manifest  # aelteres Manifest ohne Hauptseite

    def rev(titel):
        if not pinnen:
            return None
        if titel == bc.HAUPT_TITEL and haupt_neu:
            return bc.HAUPT_REVID
        if titel not in manifest:
            raise bc.HarterFehler(f"Titel nicht im Manifest: {titel}")
        return manifest[titel]["revid"]

    ergebnis = {}
    stat = {"cache": 0, "netz": 0}

    def lade(titel):
        s, wo = hole(titel, rev(titel), a.offline)
        stat[wo] += 1
        ergebnis[titel] = s
        if pinnen and titel in manifest and bc.sha256_text(s["inhalt"]) != manifest[titel]["sha256"]:
            raise bc.HarterFehler(f"sha256-Abweichung: {titel} (rev {s['revid']})")
        return s

    doku = lade(bc.DOKU_TITEL)
    einzel = bc.einzeltext_titel(doku["inhalt"])
    transkr = [bc.transkriptions_titel(s) for s in bc.ZEUGEN]
    erwartet = [bc.DOKU_TITEL, bc.HAUPT_TITEL] + transkr + einzel
    if pinnen and set(manifest) | ({bc.HAUPT_TITEL} if haupt_neu else set()) != set(erwartet):
        fehlt = sorted(set(erwartet) - set(manifest))
        zu_viel = sorted(set(manifest) - set(erwartet))
        raise bc.HarterFehler(f"Manifest und erwartete Seitenmenge weichen ab: fehlt im Manifest {fehlt}, "
                              f"nicht erwartet {zu_viel}")
    lade(bc.HAUPT_TITEL)
    for i, t in enumerate(transkr + einzel, 1):
        lade(t)
        print(f"  [{i}/{len(transkr) + len(einzel)}] {t}", flush=True)

    if len(transkr) != 21:
        raise bc.HarterFehler(f"{len(transkr)} Transkriptionsseiten statt 21")
    print(f"Seiten: {len(ergebnis)} (1 Doku + 1 Hauptseite + {len(transkr)} Transkriptionen + "
          f"{len(einzel)} Einzeltexte)")
    print(f"Quelle: {stat['cache']} aus dem Cache, {stat['netz']} vom Netz")

    if not pinnen:
        bc.INGEST_DIR.mkdir(parents=True, exist_ok=True)
        zeilen = ["\t".join(["titel", "pageid", "revid", "timestamp", "user", "sha256"])]
        for t in erwartet:
            s = ergebnis[t]
            for feld in (t, s["user"]):
                if "\t" in feld or "\n" in feld:
                    raise bc.HarterFehler(f"Tab/Zeilenumbruch in Manifestfeld: {feld!r}")
            zeilen.append("\t".join([t, str(s["pageid"]), str(s["revid"]), s["timestamp"],
                                      s["user"], bc.sha256_text(s["inhalt"])]))
        bc.MANIFEST.write_text("\n".join(zeilen) + "\n", encoding="utf-8", newline="\n")
        print(f"Manifest geschrieben: {bc.MANIFEST} ({len(zeilen) - 1} Zeilen)")
    elif haupt_neu:
        s = ergebnis[bc.HAUPT_TITEL]
        zeile = "\t".join([bc.HAUPT_TITEL, str(s["pageid"]), str(s["revid"]), s["timestamp"],
                           s["user"], bc.sha256_text(s["inhalt"])])
        with open(bc.MANIFEST, "a", encoding="utf-8", newline="\n") as f:
            f.write(zeile + "\n")
        print(f"Hauptseite ans Manifest angehaengt (rev {s['revid']}); die uebrigen "
              f"{len(ergebnis) - 1} sha256 stimmen")
    else:
        print(f"Manifest unveraendert, alle {len(ergebnis)} sha256 stimmen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
