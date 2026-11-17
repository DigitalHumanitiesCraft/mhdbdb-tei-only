#!/usr/bin/env python3
"""20-pruefpaket.py: Pruefpaket fuer Julia und KZW (BRE, #147).

Je Phase (Lemma, Wortart, Bedeutung): alle Entscheidungen mit confidence=low und eine
Zufallsstichprobe von 20 % der Entscheidungen mit confidence=medium (aufgerundet, fester Seed 147,
reproduzierbar). Eine Entscheidung ist eine Zeile der Entscheidungstabellen: eine Bulk-Zeile
(gilt fuer alle Belege einer Form oder Gruppe, im Paket mit bis zu drei Beispielen) oder eine
Patch-Zeile (ein einzelnes Wort). abstain ist keine Zuweisung und kommt nicht ins Paket.

Dazu lemma-verdacht.tsv: alle Woerter, bei denen keine Bedeutung ihres Lemmas passte (siehe
verdacht()).

Schreibt ingest/bre/pruefung/{lemma,wortart,bedeutung,lemma-verdacht}.tsv. Spalten passt, korrektur, anmerkung
sind leer und werden von den Pruefenden gefuellt (Anleitung: ingest/bre/pruefung/README.md).

Aufruf: python -P -E scripts/ingest/bre/20-pruefpaket.py
"""
import math
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_annot as ba  # noqa: E402
import bre_common as bc  # noqa: E402

SEED = 147
ANTEIL_MEDIUM = 0.2
ZIEL = bc.INGEST_DIR / "pruefung"
FELDER = ["nr", "art", "wort", "zeuge", "text", "kontext", "zuweisung", "sicherheit", "begruendung",
          "andere_moeglichkeiten", "belege", "xml_id", "passt", "korrektur", "anmerkung"]
PHASEN = [
    # (Datei, Ordner, phase, Gruppenspalte, Ergebnisspalte)
    ("lemma.tsv", ba.PHASE1, "lemma", "norm", "resolved_lemma"),
    ("wortart.tsv", ba.PHASE2, "pos", "gruppe", "resolved_pos"),
    ("bedeutung.tsv", ba.PHASE3, "sense", "gruppe", "resolved_sense"),
]


def label(phase, wert, kandidaten, lex, konzepte):
    if phase == "lemma":
        return ba.lemma_label(wert, lex)
    if phase == "pos":
        return wert
    m = re.search(re.escape(wert) + r" :: ([^|]*)", kandidaten)
    return f"{wert} :: {m.group(1).strip()}" if m else wert


def andere(phase, wert, kandidaten):
    teile = [k.strip() for k in kandidaten.split("|")]
    return " | ".join(k for k in teile if not k.startswith(wert + " ") and k != wert)


def main():
    bc.ausgabe_utf8()
    lex = ba.lade_lexikon()
    konzepte = ba.lade_konzepte()
    for datei, ordner, phase, gspalte, rspalte in PHASEN:
        pending = ba.lies_tsv(ordner / f"{phase}-pending.tsv")
        token = {p["xml_id"]: p for p in pending}
        gruppen = {}
        for p in pending:
            gruppen.setdefault(p[gspalte], []).append(p)
        zeilen = []
        for b in ba.lies_tsv(ordner / f"{phase}-bulk.tsv"):
            if b["decision_type"] == "abstain":
                continue
            zs = gruppen[b["schluessel"]]
            # Belege, die die Bulk-Entscheidung tatsaechlich tragen (keine Patch-Ausnahme)
            traeger = [z for z in zs if z[rspalte] == b["resolved"] and z["decision_type"] == "bulk-llm"]
            bsp = traeger[:3]
            zeilen.append({"art": f"für alle {len(traeger)} Belege dieser Form" if phase == "lemma"
                           else f"für alle {len(traeger)} Belege dieser Gruppe",
                           "wort": " / ".join(sorted({z["form"] for z in zs}))[:80],
                           "zeuge": " ".join(sorted({z["zeuge"] for z in traeger})),
                           "text": bsp[0]["text"] if bsp else "",
                           "kontext": " ¶ ".join(z["kontext"] for z in bsp),
                           "zuweisung": label(phase, b["resolved"], zs[0]["kandidaten"], lex, konzepte),
                           "sicherheit": b["confidence"], "begruendung": b["begruendung"],
                           "andere_moeglichkeiten": andere(phase, b["resolved"], zs[0]["kandidaten"]),
                           "belege": len(traeger), "xml_id": " ".join(z["xml_id"] for z in bsp)})
        for p in ba.lies_tsv(ordner / f"{phase}-patch.tsv"):
            if p["decision_type"] == "abstain":
                continue
            z = token[p["xml_id"]]
            zeilen.append({"art": "einzelnes Wort", "wort": z["form"], "zeuge": z["zeuge"],
                           "text": z["text"], "kontext": z["kontext"],
                           "zuweisung": label(phase, p["resolved"], z["kandidaten"], lex, konzepte),
                           "sicherheit": p["confidence"], "begruendung": p["begruendung"],
                           "andere_moeglichkeiten": andere(phase, p["resolved"], z["kandidaten"]),
                           "belege": 1, "xml_id": p["xml_id"]})
        low = [z for z in zeilen if z["sicherheit"] == "low"]
        medium = [z for z in zeilen if z["sicherheit"] == "medium"]
        k = math.ceil(len(medium) * ANTEIL_MEDIUM)
        probe = random.Random(SEED).sample(medium, k) if medium else []
        paket = low + probe
        paket.sort(key=lambda z: (z["sicherheit"] != "low", z["zeuge"], z["xml_id"]))
        for i, z in enumerate(paket, 1):
            z["nr"] = i
        ba.schreibe_tsv(ZIEL / datei, FELDER, paket)
        print(f"{datei}: {len(paket)} Zeilen = {len(low)} low + {k} von {len(medium)} medium "
              f"(Seed {SEED}); Entscheidungen der Phase gesamt {len(zeilen)}")
    verdacht(lex)


def verdacht(lex):
    """lemma-verdacht.tsv: jedes Wort, bei dem in Phase 3 keine Bedeutung seines Lemmas passte
    (Sense-abstain). Das ist der Detektor fuer falsche Lemmata aus Phase 1, vor allem aus dem
    Auto-Match: eine Form, die variants.xml nur unter einem Lemma fuehrt, bekommt dieses Lemma
    ohne Kontextpruefung, auch wenn sie hier ein anderes Wort ist (Doerfer unter durfen)."""
    lemma_p = {p["xml_id"]: p for p in ba.lies_tsv(ba.PHASE1 / "lemma-pending.tsv")}
    zeilen, herkunft = [], {}
    for z in ba.lies_tsv(ba.PHASE3 / "sense-pending.tsv"):
        if z["decision_type"] != "abstain":
            continue
        lp = lemma_p.get(z["xml_id"])
        her = lp["decision_type"] if lp else "auto-single"
        herkunft[her] = herkunft.get(her, 0) + 1
        zeilen.append({"art": "einzelnes Wort", "wort": z["form"], "zeuge": z["zeuge"], "text": z["text"],
                       "kontext": z["kontext"], "zuweisung": ba.lemma_label(z["lemma_id"], lex),
                       "sicherheit": f"Lemma: {her}",
                       "begruendung": f"keine Bedeutung passt: {z['begruendung']}",
                       "andere_moeglichkeiten": andere("lemma", z["lemma_id"], lp["kandidaten"]) if lp else "",
                       "belege": 1, "xml_id": z["xml_id"]})
    zeilen.sort(key=lambda z: (z["zuweisung"], z["wort"], z["xml_id"]))
    for i, z in enumerate(zeilen, 1):
        z["nr"] = i
    ba.schreibe_tsv(ZIEL / "lemma-verdacht.tsv", FELDER, zeilen)
    teile = " + ".join(f"{v} {k}" for k, v in sorted(herkunft.items()))
    print(f"lemma-verdacht.tsv: {len(zeilen)} Zeilen (Lemma aus Phase 1: {teile})")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
