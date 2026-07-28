#!/usr/bin/env python3
"""Wirkungsmessung fuer Stufe 3 der Lemma-Aufloesung (#224, refs #169/#45).

Hintergrund: Stufe 3 der 3-Stufen-Aufloesung (CONTRACTS.md Paragraph C) war
bidirektionales Substring-Matching:

    lemma.normalized.includes(query) OR query.includes(lemma.normalized)

Die zweite Richtung trifft jedes Kurzlemma, das irgendwo in der Eingabe steckt.
Der Korpus haelt 5 ein-, 98 zwei- und 598 dreibuchstabige normalisierte
Lemma-Formen, die so jede Suche vergiften, die Stufe 3 ueberhaupt erreicht.

Der Bug-Report #224 (Klaus Schmidt) hatte ZWEI Ursachen, das ist beim Lesen
der Zahlen wichtig:

  1. Die gezeigte Eingabe "boeses" trug ein ZERLEGTES Umlaut-oe
     (o + U+0308 statt U+00F6). Der Normalizer kannte nur die komponierte
     Form, die Eingabe fiel also durch Stufe 1 UND Stufe 2 (variants haelt
     den Schluessel "boeses", nicht die zerlegte Form).
  2. Erst dadurch landete sie in Stufe 3, wo der Substring-Test aus dem
     Fehlschlag drei Falschtreffer machte: es, o, se — und eben NICHT
     boese, was den Screenshot erklaert.

Mit komponiertem oe faengt Stufe 2 die Eingabe ab und liefert korrekt bœse.
Behoben wurde deshalb beides: NFC-Komposition im Normalizer (Ursache 1) und
die Praefix-Regel hier (Ursache 2).

Neue Regel: beidseitig praefixorientiert, Mindestlaenge 3 nur in der Richtung
"Eingabe beginnt mit Lemma" (mhd. Flexion ist suffixal).

Dieses Skript misst beide Regeln gegeneinander auf einer Stichprobe von
Varianten-Formen, deren wahres Lemma bekannt ist (variants-Map des Authority-
Index, korpus-abgeleitet aus authority-files/variants.xml).

Messmethodik (Auflagen aus dem Advisor-Review 2026-07-28):
  * Das Stage-3-Praedikat wird DIREKT aufgerufen, Stufe 1 und 2 werden
    uebersprungen. Nur so simuliert die Messung den Fall "ungesehene Form".
  * Formen, deren Normalisierung gleich der Normalisierung ihres Ziel-Lemmas
    ist, haetten Stufe 1 getroffen. Sie werden separat ausgewiesen, nicht
    stillschweigend mitgezaehlt.
  * Stichprobe mit festem Seed gezogen, nicht die ersten N.
  * Metriken sind Recall, Median der Ergebnislistengroesse und Top-1 nach
    Ranking. Die Top-1-Spalte wird DREIFACH ausgewiesen (alt / alt mit neuem
    Ranking / neu), weil der groesste Teil des Top-1-Gewinns aus der neuen
    Sortierung kommt und nicht aus der neuen Regel. Ohne die mittlere Spalte
    liest sich das Delta als 30-facher Effekt der Regel, was falsch waere.
    NICHT die 0-Treffer-Quote: die alte Regel liefert wegen der
    Kurzlemmata praktisch nie 0 Treffer, ihre Quote steigt also zwangslaeufig.
    Ein 0-Treffer-Fall, in dem die alte Regel nur Falschtreffer hatte, ist
    eine Verbesserung.

Bias-Hinweis fuer den Bericht: Echte Stage-3-Eingaben sind eher nhd. Woerter
und Tippfehler als mhd. Flexionsformen. Die Stichprobe misst den guenstigen
Fall; sie zeigt, ob der Fix Recall kostet, nicht wie haeufig Stufe 3 im Alltag
ueberhaupt das Richtige findet.

Usage:
    python scripts/audit/measure-stage3-resolution.py
    python scripts/audit/measure-stage3-resolution.py --sample 300 --seed 20260728
    python scripts/audit/measure-stage3-resolution.py --probe minnecl --probe schwertkampf

Exit codes:
    0 = Messung gelaufen (Bewertung liegt beim Menschen, das Skript urteilt nicht)
    2 = Authority-Index nicht lesbar
"""
import argparse
import gzip
import json
import random
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AUTHORITY_INDEX = REPO / "data" / "authority-index.json.gz"

# Mindestlaenge fuer die Richtung "Eingabe beginnt mit Lemma". Muss mit
# MIN_LEMMA_PREFIX_LENGTH in assets/js/lib/lemma-resolve.js uebereinstimmen.
MIN_LEMMA_PREFIX_LENGTH = 3


def stage3_old(query, lemmata):
    """Bisherige Regel: bidirektionales Substring-Matching."""
    return [l for l in lemmata
            if l["normalized"] and (query in l["normalized"] or l["normalized"] in query)]


def stage3_new(query, lemmata):
    """Neue Regel: beidseitig praefixorientiert, Mindestlaenge nur suffixseitig."""
    out = []
    for l in lemmata:
        norm = l["normalized"]
        if not norm:
            continue
        if norm.startswith(query):
            out.append(l)
        elif len(norm) >= MIN_LEMMA_PREFIX_LENGTH and query.startswith(norm):
            out.append(l)
    return out


def rank_by_distance(query, matches):
    """Distanz-Ranking: kleinste Laengendifferenz zuerst, dann stabil.

    Der Tiebreak nach l["id"] ist eine Messkonvention, damit der Lauf
    reproduzierbar ist. Produktiv bricht die Hauptseite Gleichstaende gar
    nicht (stabile Index-Reihenfolge), der Playground nach Korpus-Frequenz.
    Auf dieser Stichprobe folgenlos, aber beim Lesen der Zahlen mitdenken.
    """
    return sorted(matches, key=lambda l: (abs(len(l["normalized"]) - len(query)), l["id"]))


def load_index():
    if not AUTHORITY_INDEX.exists():
        print(f"FEHLER: {AUTHORITY_INDEX} fehlt. Erst den Index bauen.", file=sys.stderr)
        sys.exit(2)
    with gzip.open(AUTHORITY_INDEX, "rt", encoding="utf-8") as fh:
        data = json.load(fh)
    return data["lemmata"], data.get("variants", {})


def measure(lemmata, variants, sample_size, seed):
    by_id = {l["id"]: l for l in lemmata}

    # Kandidaten: Varianten-Formen mit bekanntem Ziel-Lemma. Formen, die schon
    # Stufe 1 treffen wuerden, werden getrennt gefuehrt (triviale Praefix-Hits).
    trivial, genuine = [], []
    for form, lemma_id in variants.items():
        target = by_id.get(lemma_id)
        if not target or not target["normalized"] or not form:
            continue
        (trivial if form == target["normalized"] else genuine).append((form, lemma_id))

    rng = random.Random(seed)
    sample = rng.sample(genuine, min(sample_size, len(genuine)))

    rows = []
    for form, lemma_id in sample:
        old = stage3_old(form, lemmata)
        new = rank_by_distance(form, stage3_new(form, lemmata))
        old_ids = [l["id"] for l in old]
        new_ids = [l["id"] for l in new]
        # Dritte Messreihe: alte REGEL mit neuem RANKING. Trennt den Anteil
        # des Regelwechsels vom Anteil "vorher unsortiert, jetzt sortiert".
        # Ohne diese Spalte liest sich das Top-1-Delta wie ein Effekt der
        # Regel allein, was es nicht ist.
        mid_ids = [l["id"] for l in rank_by_distance(form, old)]
        rows.append({
            "form": form,
            "target": lemma_id,
            "old_recall": lemma_id in old_ids,
            "new_recall": lemma_id in new_ids,
            "old_size": len(old_ids),
            "new_size": len(new_ids),
            # Alt hat keine Sortierung, die Index-Reihenfolge IST das Ranking.
            "old_top1": bool(old_ids) and old_ids[0] == lemma_id,
            "mid_top1": bool(mid_ids) and mid_ids[0] == lemma_id,
            "new_top1": bool(new_ids) and new_ids[0] == lemma_id,
        })
    return rows, len(genuine), len(trivial)


def report(rows, genuine_total, trivial_total, sample_size, seed):
    n = len(rows)
    if not n:
        print("Keine auswertbaren Formen gefunden.")
        return

    def pct(count):
        return f"{count} ({100.0 * count / n:.1f} %)"

    print("=" * 68)
    print("Stufe-3-Wirkungsmessung (#224)")
    print("=" * 68)
    print(f"Grundgesamtheit:  {genuine_total:,} Varianten-Formen mit bekanntem Ziel-Lemma")
    print(f"                  {trivial_total:,} weitere Formen sind mit ihrem Lemma normal-")
    print(f"                  gleich, wuerden also Stufe 1 treffen (nicht in der Stichprobe)")
    print(f"Stichprobe:       {n} Formen, Seed {seed}")
    print(f"Mindestlaenge:    {MIN_LEMMA_PREFIX_LENGTH} (nur Richtung 'Eingabe beginnt mit Lemma')")
    print()
    print("                              alt      alt + Ranking            neu")
    print(f"  Recall (Ziel in Liste)   {pct(sum(r['old_recall'] for r in rows)):>14}  "
          f"{'(unveraendert)':>14}  {pct(sum(r['new_recall'] for r in rows)):>14}")
    print(f"  Top-1 nach Ranking       {pct(sum(r['old_top1'] for r in rows)):>14}  "
          f"{pct(sum(r['mid_top1'] for r in rows)):>14}  "
          f"{pct(sum(r['new_top1'] for r in rows)):>14}")
    # Die Listengroesse haengt nur an der TrefferMENGE, nicht an der Sortierung:
    # die mittlere Spalte ist hier per Definition gleich der linken.
    print(f"  Median Listengroesse     {statistics.median(r['old_size'] for r in rows):>14.0f}  "
          f"{'(unveraendert)':>14}  "
          f"{statistics.median(r['new_size'] for r in rows):>14.0f}")
    print(f"  Mittel Listengroesse     {statistics.mean(r['old_size'] for r in rows):>14.1f}  "
          f"{'(unveraendert)':>14}  "
          f"{statistics.mean(r['new_size'] for r in rows):>14.1f}")
    print(f"  Groesste Liste           {max(r['old_size'] for r in rows):>14}  "
          f"{'(unveraendert)':>14}  "
          f"{max(r['new_size'] for r in rows):>14}")
    print()

    lost = [r for r in rows if r["old_recall"] and not r["new_recall"]]
    won = [r for r in rows if r["new_recall"] and not r["old_recall"]]
    print(f"  Recall verloren:  {len(lost)}")
    for r in lost[:10]:
        print(f"      {r['form']} -> {r['target']} (alt: {r['old_size']} Treffer)")
    if len(lost) > 10:
        print(f"      ... und {len(lost) - 10} weitere")
    print(f"  Recall gewonnen:  {len(won)}")
    for r in won[:10]:
        print(f"      {r['form']} -> {r['target']}")
    print()


def probe(lemmata, variants, terms):
    print("=" * 68)
    print("Einzelproben")
    print("=" * 68)
    print("ACHTUNG: zeigt, was das Stage-3-PRAEDIKAT taete. Ein Begriff, der")
    print("schon Stufe 1 oder 2 trifft, erreicht Stufe 3 produktiv nie — das")
    print("steht dann in der Zeile darunter.")
    by_norm = {}
    for l in lemmata:
        by_norm.setdefault(l["normalized"], []).append(l)
    for term in terms:
        old = stage3_old(term, lemmata)
        new = rank_by_distance(term, stage3_new(term, lemmata))
        fmt = lambda ms: ", ".join(f"{l['lemma']} ({l['normalized']})" for l in ms[:8]) or "keine"
        s1 = by_norm.get(term, [])
        s2 = variants.get(term)
        print(f"\n  {term!r}")
        if s1:
            print(f"    ERREICHT STUFE 3 NICHT: Stufe 1 trifft ({', '.join(l['id'] for l in s1)})")
        elif s2:
            print(f"    ERREICHT STUFE 3 NICHT: Stufe 2 trifft (variants -> {s2})")
        else:
            print(f"    erreicht Stufe 3")
        print(f"    alt ({len(old):>3}): {fmt(old)}")
        print(f"    neu ({len(new):>3}): {fmt(new)}")
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sample", type=int, default=300, help="Stichprobengroesse (Default 300)")
    ap.add_argument("--seed", type=int, default=20260728, help="RNG-Seed (Default 20260728)")
    ap.add_argument("--probe", action="append", default=[],
                    help="Einzelbegriff zusaetzlich ausgeben (mehrfach nutzbar)")
    args = ap.parse_args()

    lemmata, variants = load_index()
    rows, genuine_total, trivial_total = measure(lemmata, variants, args.sample, args.seed)
    report(rows, genuine_total, trivial_total, args.sample, args.seed)
    if args.probe:
        probe(lemmata, variants, args.probe)


if __name__ == "__main__":
    main()
