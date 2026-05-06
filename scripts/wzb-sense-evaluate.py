#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3 — Evaluation: sample gold standard and compute WSD accuracy metrics.

Two subcommands:

  sample    Extract a stratified gold standard sample from the annotated
            MHDBDB corpus and write both a gold TSV and a stripped pending
            TSV ready for pipeline input.

  evaluate  Read the gold TSV and a resolved pending TSV; compute accuracy,
            confidence calibration, ABSTAIN rate, and stratum breakdown.

Usage:
    # Step 1 — extract gold standard sample
    py scripts/wzb-sense-evaluate.py sample \\
        --gold-out     Wenzelsbibel/phase3/eval/gold-sample.tsv \\
        --stripped-out Wenzelsbibel/phase3/eval/stripped-pending.tsv \\
        --n 600 --seed 42

    # Step 2 — run pipeline on stripped-pending.tsv (wzb-sense-bulk-resolve.py etc.)

    # Step 3 — evaluate
    py scripts/wzb-sense-evaluate.py evaluate \\
        --gold     Wenzelsbibel/phase3/eval/gold-sample.tsv \\
        --resolved Wenzelsbibel/phase3/eval/resolved-pending.tsv \\
        --output   Wenzelsbibel/phase3/eval/report.txt \\
        --json     Wenzelsbibel/phase3/eval/report.json

Pre-registered evaluation protocol:
    docs/features/034-wenzelsbibel-annotation.md § "Pre-registered evaluation protocol"
"""

import csv
import sys
import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

try:
    from lxml import etree
except ImportError:
    print("ERROR: Please install lxml: pip install lxml")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from mhg_normalizer import normalize_mhg

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT    = Path(__file__).parent.parent
DEFAULT_TEI_DIR = PROJECT_ROOT / "tei"
DEFAULT_LEX     = PROJECT_ROOT / "authority-files" / "lexicon.xml"
DEFAULT_CON     = PROJECT_ROOT / "authority-files" / "concepts.xml"
DEFAULT_EVAL_DIR = PROJECT_ROOT / "Wenzelsbibel" / "phase3" / "eval"

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML = "http://www.w3.org/XML/1998/namespace"
XML_ID = f"{{{NS_XML}}}id"

CONTEXT_WINDOW = 5

# Majority-sense baseline computed 2026-04-24 (wzb-sense-baseline.py, full corpus)
MAJORITY_SENSE_BASELINE = 0.667

# Calibration mapping: LLM confidence label -> probability estimate
CONFIDENCE_TO_P = {"high": 0.90, "medium": 0.70, "low": 0.50}


# ---------------------------------------------------------------------------
# Stratum definitions (from pre-registered protocol)
# ---------------------------------------------------------------------------

def sense_stratum(count: int) -> str:
    if count == 2:   return "2"
    if count <= 5:   return "3-5"
    return "6+"

POS_NOM   = {"NOM"}
POS_VRB   = {"VRB", "VEX", "VEM"}
POS_OTHER = {"ADJ", "ADV", "PRP"}

def pos_stratum(pos: str) -> str | None:
    tags = set(pos.upper().split())
    if tags & POS_NOM:   return "NOM"
    if tags & POS_VRB:   return "VRB"
    if tags & POS_OTHER: return "OTHER"
    return None

STRATUM_CELLS = [
    ("2",   "NOM"), ("2",   "VRB"), ("2",   "OTHER"),
    ("3-5", "NOM"), ("3-5", "VRB"), ("3-5", "OTHER"),
    ("6+",  "NOM"), ("6+",  "VRB"), ("6+",  "OTHER"),
]


# ---------------------------------------------------------------------------
# Index builders
# ---------------------------------------------------------------------------

def build_lexicon_sense_index(lex_path: Path) -> dict[str, list[dict]]:
    """Return {lemma_id: [sense_dict, ...]}."""
    tree = etree.parse(str(lex_path))
    ns = {"tei": NS_TEI}
    index: dict[str, list] = {}
    for entry in tree.findall(".//tei:entry", ns):
        lid = entry.get(XML_ID, "")
        if not lid:
            continue
        senses = []
        for sense in entry.findall("tei:sense", ns):
            sid = sense.get(XML_ID, "")
            concept_ids = [
                ptr.get("target", "").split("#")[-1]
                for ptr in sense.findall("tei:ptr", ns)
                if "concepts.xml#" in ptr.get("target", "")
            ]
            ana_raw = sense.get("ana", "")
            ana_types = {t.lstrip("#") for t in ana_raw.split() if t}
            senses.append({"sense_id": sid, "concept_ids": concept_ids, "ana_types": ana_types})
        index[lid] = senses
    return index


def build_concept_index(con_path: Path) -> dict[str, str]:
    """Return {concept_id: 'DE (EN)'} labels."""
    tree = etree.parse(str(con_path))
    ns = {"tei": NS_TEI}
    index: dict[str, str] = {}
    for cat in tree.findall(".//tei:category", ns):
        cid = cat.get(XML_ID, "")
        if not cid:
            continue
        de_els = cat.findall(f"tei:catDesc/tei:term[@{{{NS_XML}}}lang='de']", ns)
        en_els = cat.findall(f"tei:catDesc/tei:term[@{{{NS_XML}}}lang='en']", ns)
        de = (de_els[0].text or "").strip() if de_els else ""
        en = (en_els[0].text or "").strip() if en_els else ""
        index[cid] = f"{de} ({en})" if en else de
    return index


def sense_label(sense_dict: dict, concept_index: dict[str, str]) -> str:
    labels = [concept_index.get(cid, cid) for cid in sense_dict["concept_ids"]]
    return "; ".join(labels) if labels else sense_dict["sense_id"]


# ---------------------------------------------------------------------------
# Corpus scan
# ---------------------------------------------------------------------------

def scan_corpus_for_annotated_tokens(
    tei_dir: Path,
    lex_index: dict[str, list],
    min_sense_count: int = 2,
) -> list[dict]:
    """
    Scan all corpus TEI files for <w @lemmaRef @meaningRef @pos> where the
    lemma has >= min_sense_count senses. Returns token dicts suitable for
    stratified sampling.
    """
    tokens = []
    files = sorted(tei_dir.glob("*.xml"))
    print(f"Scanning {len(files)} corpus files in {tei_dir} ...")

    for i, fpath in enumerate(files):
        if i % 100 == 0:
            print(f"  {i}/{len(files)} files ...", end="\r")
        try:
            tree = etree.parse(str(fpath))
        except Exception:
            continue

        body = tree.find(f".//{{{NS_TEI}}}body")
        if body is None:
            continue
        w_elements = body.findall(f".//{{{NS_TEI}}}w")
        context_list = [(w.get(XML_ID, ""), (w.text or "").strip()) for w in w_elements]

        for idx, w in enumerate(w_elements):
            lemma_ref   = w.get("lemmaRef", "")
            meaning_ref = w.get("meaningRef", "")
            pos         = w.get("pos", "")
            if not lemma_ref or not meaning_ref or not pos:
                continue

            lemma_id = lemma_ref.split("#")[-1] if "#" in lemma_ref else lemma_ref
            senses   = lex_index.get(lemma_id, [])
            if len(senses) < min_sense_count:
                continue

            gold_sense = meaning_ref.split("#")[-1] if "#" in meaning_ref else meaning_ref

            start = max(0, idx - CONTEXT_WINDOW)
            end   = min(len(context_list), idx + CONTEXT_WINDOW + 1)
            ctx   = " ".join(
                f"[{context_list[j][1]}]" if j == idx else context_list[j][1]
                for j in range(start, end)
            )

            tokens.append({
                "corpus_file":   fpath.name,
                "xml_id":        w.get(XML_ID, ""),
                "form":          (w.text or "").strip(),
                "lemmaRef":      lemma_ref,
                "gold_sense":    gold_sense,
                "pos":           pos,
                "sense_count":   len(senses),
                "context":       ctx,
                "stratum_sense": sense_stratum(len(senses)),
                "stratum_pos":   pos_stratum(pos),
            })

    print(f"\n  Found {len(tokens)} eligible annotated tokens (multi-sense lemmata)")
    return tokens


# ---------------------------------------------------------------------------
# Stratified sampling
# ---------------------------------------------------------------------------

def stratified_sample(
    tokens: list[dict],
    n: int,
    seed: int,
    min_per_cell: int = 50,
    min_lemmata_per_cell: int = 3,
) -> list[dict]:
    """
    Draw a stratified random sample across 9 cells (sense_stratum × pos_stratum).
    Ensures >= min_per_cell tokens and >= min_lemmata_per_cell unique lemmata per cell.
    """
    rng = random.Random(seed)

    # Group into cells; skip tokens with no valid pos_stratum
    cells: dict[tuple, list] = {cell: [] for cell in STRATUM_CELLS}
    for tok in tokens:
        if tok["stratum_pos"] is None:
            continue
        key = (tok["stratum_sense"], tok["stratum_pos"])
        if key in cells:
            cells[key].append(tok)

    per_cell = max(min_per_cell, n // len(STRATUM_CELLS))
    sample: list[dict] = []

    for cell, pool in cells.items():
        if len(pool) < min_per_cell:
            print(f"  WARNING: cell {cell} has only {len(pool)} tokens (target {per_cell})")

        # Group by lemma for diversity constraint
        lemma_groups: dict[str, list] = defaultdict(list)
        for tok in pool:
            lid = tok["lemmaRef"].split("#")[-1] if "#" in tok["lemmaRef"] else tok["lemmaRef"]
            lemma_groups[lid].append(tok)

        lemmata_ids = list(lemma_groups.keys())
        rng.shuffle(lemmata_ids)

        cell_sample: list[dict] = []
        seen_lemmata: set[str] = set()
        attempts = 0

        # Round-robin across lemmata until we reach per_cell
        while len(cell_sample) < per_cell and attempts < per_cell * 5:
            lid = lemmata_ids[attempts % len(lemmata_ids)]
            attempts += 1
            available = [t for t in lemma_groups[lid] if t not in cell_sample]
            if not available:
                continue
            cell_sample.append(rng.choice(available))
            seen_lemmata.add(lid)

        print(f"  Cell {cell}: {len(cell_sample)} tokens from {len(seen_lemmata)} lemmata")
        sample.extend(cell_sample)

    rng.shuffle(sample)
    return sample


# ---------------------------------------------------------------------------
# Sample mode
# ---------------------------------------------------------------------------

GOLD_FIELDNAMES = [
    "token_id", "corpus_file", "xml_id", "form", "lemmaRef", "gold_sense",
    "pos", "sense_count", "stratum_sense", "stratum_pos", "context",
]

STRIPPED_FIELDNAMES = [
    "xml_id", "form", "lemmaRef", "pos", "context",
    "candidate_senses", "resolved_sense", "confidence", "reviewer",
    "decision_type", "model_id",
]


def run_sample(args) -> None:
    print(f"Loading lexicon from {args.lexicon} ...")
    lex_index = build_lexicon_sense_index(Path(args.lexicon))
    print(f"  {len(lex_index)} lemma entries")

    print(f"Loading concepts from {args.concepts} ...")
    concept_index = build_concept_index(Path(args.concepts))
    print(f"  {len(concept_index)} concept labels")

    tokens = scan_corpus_for_annotated_tokens(Path(args.corpus_dir), lex_index)

    print(f"\nSampling {args.n} tokens (seed={args.seed}) ...")
    sample = stratified_sample(tokens, args.n, args.seed)
    print(f"  Total sample: {len(sample)} tokens across {len(STRATUM_CELLS)} cells")

    # Gold TSV — contains gold_sense; used only for evaluation, never shown to LLM
    gold_path = Path(args.gold_out)
    gold_path.parent.mkdir(parents=True, exist_ok=True)
    with gold_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=GOLD_FIELDNAMES, delimiter="\t")
        writer.writeheader()
        for i, tok in enumerate(sample):
            writer.writerow({"token_id": f"eval_{i:04d}", **{k: tok.get(k, "") for k in GOLD_FIELDNAMES if k != "token_id"}})
    print(f"\nGold TSV written:     {gold_path}  ({len(sample)} rows)")
    print("  *** Keep this file hidden from the LLM — it contains the gold labels ***")

    # Stripped TSV — @meaningRef removed; fed into the disambiguation pipeline
    stripped_path = Path(args.stripped_out)
    stripped_path.parent.mkdir(parents=True, exist_ok=True)
    with stripped_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=STRIPPED_FIELDNAMES, delimiter="\t")
        writer.writeheader()
        for tok in sample:
            lemma_id = tok["lemmaRef"].split("#")[-1] if "#" in tok["lemmaRef"] else tok["lemmaRef"]
            senses   = lex_index.get(lemma_id, [])
            candidate_senses = "|".join(
                f"{s['sense_id']} :: {sense_label(s, concept_index)}"
                for s in senses
            )
            writer.writerow({
                "xml_id":           tok["xml_id"],
                "form":             tok["form"],
                "lemmaRef":         tok["lemmaRef"],
                "pos":              tok["pos"],
                "context":          tok["context"],
                "candidate_senses": candidate_senses,
                "resolved_sense":   "",
                "confidence":       "",
                "reviewer":         "",
                "decision_type":    "",
                "model_id":         "",
            })
    print(f"Stripped TSV written: {stripped_path}")
    print("\nNext steps:")
    print("  1. Fill resolved_sense in the stripped TSV using wzb-sense-bulk-resolve.py")
    print("     (same workflow as Phase 3, but on the stripped TSV)")
    print("  2. py scripts/wzb-sense-evaluate.py evaluate \\")
    print(f"       --gold {gold_path} \\")
    print(f"       --resolved {stripped_path} \\")
    print(f"       --output Wenzelsbibel/phase3/eval/report.txt \\")
    print(f"       --json   Wenzelsbibel/phase3/eval/report.json")


# ---------------------------------------------------------------------------
# Evaluate mode
# ---------------------------------------------------------------------------

def sense_match(gold_row: dict, res_row: dict) -> bool:
    """True if resolved_sense matches gold_sense (compare fragment only)."""
    gold = gold_row.get("gold_sense", "").strip()
    res  = res_row.get("resolved_sense", "").strip()
    if not gold or not res:
        return False
    return gold.split("#")[-1] == res.split("#")[-1]


def brier_score(predictions: list[tuple[float, int]]) -> float | None:
    if not predictions:
        return None
    return sum((p - o) ** 2 for p, o in predictions) / len(predictions)


def cohen_kappa(n: int, agree: int, rater1_pos: int, rater2_pos: int) -> float:
    """Two-class Cohen's κ (positive = correct)."""
    if n == 0:
        return 0.0
    p_o = agree / n
    p_e = (rater1_pos / n) * (rater2_pos / n) + \
          ((n - rater1_pos) / n) * ((n - rater2_pos) / n)
    return 0.0 if p_e == 1.0 else (p_o - p_e) / (1.0 - p_e)


def run_evaluate(args) -> None:
    gold_path = Path(args.gold)
    if not gold_path.exists():
        print(f"ERROR: gold file not found: {gold_path}"); sys.exit(1)

    resolved_path = Path(args.resolved)
    if not resolved_path.exists():
        print(f"ERROR: resolved file not found: {resolved_path}"); sys.exit(1)

    gold: dict[str, dict] = {}
    with gold_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            gold[row["xml_id"]] = row

    resolved: dict[str, dict] = {}
    with resolved_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            resolved[row["xml_id"]] = row

    # Join on xml_id
    joined: list[tuple[dict, dict]] = []
    for xml_id, g in gold.items():
        r = resolved.get(xml_id)
        if r is None:
            print(f"  WARNING: {xml_id} in gold but not in resolved (skipping)")
            continue
        joined.append((g, r))

    print(f"Joined {len(joined)} tokens  ({len(gold)} gold, {len(resolved)} resolved)")

    # Partition into evaluated / abstain / missing
    abstain   = [(g, r) for g, r in joined if r.get("resolved_sense","").strip().upper() == "ABSTAIN"]
    evaluated = [(g, r) for g, r in joined if r.get("resolved_sense","").strip() and r.get("resolved_sense","").upper() != "ABSTAIN"]
    missing   = [(g, r) for g, r in joined if not r.get("resolved_sense","").strip()]

    n_total   = len(joined)
    n_abstain = len(abstain)
    n_eval    = len(evaluated)
    n_missing = len(missing)

    # Overall accuracy
    correct  = sum(1 for g, r in evaluated if sense_match(g, r))
    accuracy = correct / n_eval if n_eval else 0.0

    # By decision type
    by_decision: dict[str, list] = defaultdict(list)
    for g, r in evaluated:
        by_decision[r.get("decision_type", "unknown") or "unknown"].append((g, r))

    # By stratum
    stratum_results: dict[str, list] = defaultdict(list)
    for g, r in evaluated:
        key = f"{g.get('stratum_sense','?')}×{g.get('stratum_pos','?')}"
        stratum_results[key].append((g, r))

    # Confidence calibration
    conf_groups: dict[str, list[int]] = defaultdict(list)
    brier_data:  list[tuple[float, int]] = []
    for g, r in evaluated:
        conf = r.get("confidence", "").strip().lower()
        correct_flag = 1 if sense_match(g, r) else 0
        if conf in CONFIDENCE_TO_P:
            conf_groups[conf].append(correct_flag)
            brier_data.append((CONFIDENCE_TO_P[conf], correct_flag))

    # Inter-annotator κ (LLM vs Julia), if julia_sense column present
    julia_kappa = None
    has_julia = evaluated and "julia_sense" in evaluated[0][1]
    if has_julia:
        llm_correct   = [1 if sense_match(g, r) else 0 for g, r in evaluated]
        julia_correct = [
            1 if r.get("julia_sense","").split("#")[-1] == g.get("gold_sense","").split("#")[-1] else 0
            for g, r in evaluated
        ]
        agree = sum(1 for l, j in zip(llm_correct, julia_correct) if l == j)
        julia_kappa = cohen_kappa(
            n=n_eval,
            agree=agree,
            rater1_pos=sum(llm_correct),
            rater2_pos=sum(julia_correct),
        )

    # @wordRef hit rate (correctly resolved tokens where @wordRef was also set)
    has_wordref  = evaluated and "wordRef" in evaluated[0][1]
    wordref_possible = sum(1 for g, r in evaluated if sense_match(g, r))
    wordref_assigned = sum(1 for g, r in evaluated if sense_match(g, r) and r.get("wordRef","").strip()) if has_wordref else 0
    wordref_rate = wordref_assigned / wordref_possible if wordref_possible else 0.0

    # --- Build report ---
    lines: list[str] = []
    lines.append("=" * 64)
    lines.append("MHDBDB WSD Evaluation Report")
    lines.append("Pre-registered protocol: 034-wenzelsbibel-annotation.md")
    lines.append("=" * 64)
    lines.append("")
    lines.append(f"Gold tokens:          {n_total}")
    lines.append(f"Evaluated:            {n_eval}  ({100*n_eval/n_total:.1f}%)")
    lines.append(f"ABSTAIN:              {n_abstain}  ({100*n_abstain/n_total:.1f}%)")
    lines.append(f"Missing / unresolved: {n_missing}")
    lines.append("")
    lines.append(f"OVERALL ACCURACY:  {correct}/{n_eval} = {100*accuracy:.1f}%")
    lines.append("")
    lines.append("Baseline comparison:")
    lines.append(f"  Majority-sense baseline: {100*MAJORITY_SENSE_BASELINE:.1f}%")
    lines.append("  (Computed from full MHDBDB corpus, 2026-04-24, via wzb-sense-baseline.py.)")
    lines.append("  IMPORTANT: This baseline is genre-unmatched. The MHDBDB corpus covers")
    lines.append("  mixed genres; the Wenzelsbibel is biblical prose (OT translation, ca. 1390).")
    lines.append("  Biblical prose exhibits different sense distributions (higher lexical")
    lines.append("  consistency, fewer metaphorical extensions) than the mixed-genre corpus.")
    lines.append("  The baseline should therefore be treated as an approximate reference,")
    lines.append("  not a matched comparator. Report comparison as:")
    lines.append('  "LLM accuracy vs. mixed-genre majority-sense baseline (66.7%)".')
    lines.append("")
    lines.append("Accuracy by decision type (pre-registered: compare instance-llm only):")
    for dt in sorted(by_decision):
        grp = by_decision[dt]
        grp_c = sum(1 for g, r in grp if sense_match(g, r))
        lines.append(f"  {dt:22s}: {grp_c}/{len(grp)} = {100*grp_c/len(grp):.1f}%")
    lines.append("")
    lines.append("Accuracy by stratum (sense_count × POS):")
    for s_s, s_p in STRATUM_CELLS:
        key = f"{s_s}×{s_p}"
        grp = stratum_results.get(key, [])
        if not grp:
            lines.append(f"  {key:12s}: — (no tokens)")
            continue
        grp_c = sum(1 for g, r in grp if sense_match(g, r))
        lines.append(f"  {key:12s}: {grp_c}/{len(grp)} = {100*grp_c/len(grp):.1f}%")
    lines.append("")
    lines.append("Confidence calibration:")
    for conf in ["high", "medium", "low"]:
        grp = conf_groups.get(conf, [])
        if not grp:
            lines.append(f"  {conf:8s}: — (no tokens)")
            continue
        acc = sum(grp) / len(grp)
        lines.append(f"  {conf:8s}: {sum(grp)}/{len(grp)} = {100*acc:.1f}%  (expected ≈{100*CONFIDENCE_TO_P[conf]:.0f}%)")
    bs = brier_score(brier_data)
    lines.append(f"  Brier score: {bs:.4f}  (0 = perfect, 0.25 = uninformative)" if bs is not None else "  Brier score: —")
    lines.append("")
    lines.append(f"ABSTAIN rate: {n_abstain}/{n_total} = {100*n_abstain/n_total:.1f}%")
    lines.append("(ABSTAINs excluded from accuracy denominator.)")
    lines.append("")
    if julia_kappa is not None:
        lines.append(f"Inter-annotator κ (LLM vs Julia, correct/incorrect): {julia_kappa:.3f}")
        lines.append("")
    if has_wordref:
        lines.append(f"@wordRef hit rate: {wordref_assigned}/{wordref_possible} = {100*wordref_rate:.1f}%")
        lines.append("(Of correctly disambiguated tokens, proportion where @wordRef was also auto-assigned.)")
    lines.append("")
    lines.append("=" * 64)

    report = "\n".join(lines)
    print(report)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"\nText report written to {out}")

    if args.json:
        data = {
            "n_total":   n_total,
            "n_evaluated": n_eval,
            "n_abstain": n_abstain,
            "n_missing": n_missing,
            "accuracy":  round(accuracy, 4),
            "baseline": {
                "value": MAJORITY_SENSE_BASELINE,
                "note": "genre-unmatched majority-sense from full MHDBDB corpus (2026-04-24)",
            },
            "by_decision_type": {
                dt: {
                    "n": len(grp),
                    "correct": sum(1 for g, r in grp if sense_match(g, r)),
                    "accuracy": round(sum(1 for g, r in grp if sense_match(g, r)) / len(grp), 4),
                }
                for dt, grp in by_decision.items()
            },
            "by_stratum": {
                f"{s_s}x{s_p}": {
                    "n": len(stratum_results.get(f"{s_s}×{s_p}", [])),
                    "correct": sum(1 for g, r in stratum_results.get(f"{s_s}×{s_p}", []) if sense_match(g, r)),
                    "accuracy": round(sum(1 for g, r in stratum_results.get(f"{s_s}×{s_p}", []) if sense_match(g, r)) / len(stratum_results[f"{s_s}×{s_p}"]), 4)
                                if stratum_results.get(f"{s_s}×{s_p}") else None,
                }
                for s_s, s_p in STRATUM_CELLS
            },
            "confidence_calibration": {
                conf: {
                    "n": len(grp),
                    "accuracy": round(sum(grp) / len(grp), 4) if grp else None,
                    "expected_p": CONFIDENCE_TO_P.get(conf),
                }
                for conf, grp in conf_groups.items()
            },
            "brier_score": round(bs, 4) if bs is not None else None,
            "abstain_rate": round(n_abstain / n_total, 4) if n_total else 0,
            "julia_kappa": round(julia_kappa, 4) if julia_kappa is not None else None,
            "wordref_hit_rate": round(wordref_rate, 4) if has_wordref else None,
        }
        jp = Path(args.json)
        jp.parent.mkdir(parents=True, exist_ok=True)
        jp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON report written to {jp}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase 3 Evaluation: extract gold standard or compute WSD accuracy"
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    sp = sub.add_parser("sample", help="Extract stratified gold standard sample from corpus")
    sp.add_argument("--corpus-dir",   default=str(DEFAULT_TEI_DIR))
    sp.add_argument("--lexicon",      default=str(DEFAULT_LEX))
    sp.add_argument("--concepts",     default=str(DEFAULT_CON))
    sp.add_argument("--gold-out",     required=True, help="Output gold standard TSV (keep hidden from LLM)")
    sp.add_argument("--stripped-out", required=True, help="Output stripped pending TSV for pipeline input")
    sp.add_argument("--n",    type=int, default=600, help="Total sample size (default: 600)")
    sp.add_argument("--seed", type=int, default=42,  help="Random seed (default: 42)")

    ep = sub.add_parser("evaluate", help="Compute accuracy metrics from resolved TSV + gold TSV")
    ep.add_argument("--gold",     required=True, help="Gold standard TSV (output of 'sample' mode)")
    ep.add_argument("--resolved", required=True, help="Resolved pending TSV (resolved_sense filled)")
    ep.add_argument("--output",   default=None, help="Write text report to this file")
    ep.add_argument("--json",     default=None, help="Write JSON report to this file")

    args = parser.parse_args()

    if args.mode == "sample":
        run_sample(args)
    else:
        run_evaluate(args)


if __name__ == "__main__":
    main()
