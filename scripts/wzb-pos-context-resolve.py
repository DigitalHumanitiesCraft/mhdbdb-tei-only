#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2 context-based POS resolution for the Wenzelsbibel.

For each <w> without @pos, looks at the @pos tags of neighboring <w> elements
(already resolved in Pass 1) and applies lemma-specific rules to disambiguate.

Writes decisions into wzb-pos-pending.tsv (resolved_pos column), then the
existing wzb-pos-apply.py propagates them to the TEI.

Supported lemmata:
  lemma_1097  daz        DET|SCNJ
  lemma_1331  ein        DET|NUM
  lemma_2598  haben      NOM|VEX|VRB
  lemma_6330  ûf         ADV|PRP
  lemma_6342  ûʒ         ADV|PRP
  lemma_7557  wider      ADV|PRP
  lemma_7194  vor        ADV|GRA|PRP
  lemma_1410  enkegen    ADV|PRP
  lemma_1089  dorouf     ADV|PRP
  lemma_4325  neben      ADV|PRP
  lemma_1090  dorous     ADV|PRP
  lemma_20032 hinvber    ADV|PRP
  lemma_37960 con        ADV|PRP
  lemma_56117 ir         POS|PRO
  lemma_4415  noch       ADV|CNJ|NEG
  lemma_4840  reht       ADJ|ADV|GRA|NOM
  lemma_4872  rîche      ADJ|ADV|GRA|NOM
  lemma_1281  ê          ADJ|ADV|GRA
  lemma_3659  leben      NOM|VRB
  lemma_6118  tôt        ADJ|NOM
  lemma_2617  halbe      ADJ|ADV|NOM|NUM
  lemma_7780  zehende    ADJ|NOM|NUM
  lemma_7489  wart       VEX|VRB
  lemma_4281  næhst      ADJ|ADV|GRA|NOM|PRP
  lemma_1242  dû/dein    ART|POS|PRO
  lemma_7643  wir/unser  POS|PRO
  lemma_1517  ým         POS|PRO
  lemma_9387  Latin esse VEX|VRB
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path
from lxml import etree

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML = "http://www.w3.org/XML/1998/namespace"
XML_ID = f"{{{NS_XML}}}id"
REVIEWER = "claude-context"

# POS tags that indicate a following noun phrase (→ determiner/preposition reading)
NP_POS = {"NOM", "NAM", "ADJ", "NUM", "POS", "DET"}
# POS tags that indicate a finite clause follows (→ subordinating conjunction reading)
CLAUSE_POS = {"PRO", "VRB", "VEX", "VEM", "NEG", "ADV", "SCNJ", "CCNJ", "CNJ"}
# POS tags that indicate a verbal environment (→ particle/prefix reading)
VERBAL_POS = {"VRB", "VEX", "VEM"}
# POS tags that are pronouns (→ particle before verb = ADV)
PRONOUN_POS = {"PRO", "POS"}

def build_w_index(tei_path):
    """
    Parse TEI, return:
      w_list: all <w> elements in document order
      id_to_idx: xml:id -> index in w_list
    """
    tree = etree.parse(str(tei_path))
    root = tree.getroot()
    w_list = root.findall(f".//{{{NS_TEI}}}w")
    id_to_idx = {}
    for i, w in enumerate(w_list):
        wid = w.get(XML_ID, "")
        if wid:
            id_to_idx[wid] = i
    return w_list, id_to_idx


def get_neighbors(w_list, idx, window=4):
    """Return (prev_items, next_items) each as list of (form, pos) within window."""
    prev_items = []
    for j in range(max(0, idx - window), idx):
        w = w_list[j]
        prev_items.append((w.text or "", w.get("pos", "")))

    next_items = []
    for j in range(idx + 1, min(len(w_list), idx + window + 1)):
        w = w_list[j]
        next_items.append((w.text or "", w.get("pos", "")))

    return prev_items, next_items


def has_participle_nearby(prev_items, next_items):
    """Heuristic: is there a past participle (ge-...-t/en form) nearby?"""
    for form, pos in list(prev_items) + list(next_items):
        f = form.lower().strip()
        # Past participle: starts with ge- and ends in -t or -en, or -n
        # Also handle: gesehen, gegeben, gepoten, getan, gelegt, beschriben etc.
        if f.startswith("ge") and len(f) > 4:
            return True
        # Bohemian variant: often without ge- but with -t/-en ending tagged VRB
        # If a neighboring word is tagged VRB and looks like a participle
        if pos == "VRB" and (f.endswith("en") or f.endswith("et") or f.endswith("t")):
            if len(f) > 4:
                return True
    return False


def next_real_pos(next_items):
    """Return the first non-empty @pos from next_items."""
    for form, pos in next_items:
        if pos:
            return pos, form
    return "", ""


def prev_real_pos(prev_items):
    """Return the last non-empty @pos from prev_items (closest predecessor)."""
    for form, pos in reversed(prev_items):
        if pos:
            return pos, form
    return "", ""


def resolve_daz(prev_items, next_items, form):
    """
    lemma_1097 daz → DET or SCNJ.
    DET:  modifies following noun phrase (next @pos in NP_POS)
    SCNJ: introduces subordinate clause (next @pos in CLAUSE_POS)
    Fallback: DET (Bohemian "das" is overwhelmingly the definite article in
    WZB biblical prose; SCNJ is a minority usage).
    """
    np_pos, nf = next_real_pos(next_items)

    # Deictic "daz ist" → DET (points to prior content)
    if nf.lower() in ("ist", "ist", "were", "war", "wart"):
        return "DET", "medium", "deictic das ist/war (copula without subordinate clause)"

    # "daz do" → SCNJ (relative clause opener with ADV do/da)
    if nf.lower() in ("do", "da", "dort", "hir"):
        return "SCNJ", "medium", "das + locative do/da → relative/subordinate clause"

    if np_pos in NP_POS:
        return "DET", "high", f"modifies following {np_pos} '{nf}'"
    if np_pos in CLAUSE_POS:
        return "SCNJ", "high", f"introduces clause, next is {np_pos} '{nf}'"

    # Fallback when no tagged neighbor is available: DET is the overwhelming
    # default in WZB biblical prose (Bohemian "das" = definite article).
    return "DET", "medium", "fallback DET (das overwhelmingly article in WZB)"


def resolve_ein(prev_items, next_items, form):
    """
    lemma_1331 ein → DET or NUM.
    DET:  indefinite article before NOM/ADJ/NAM
    NUM:  numeral in counting context
    """
    np_pos, nf = next_real_pos(next_items)
    pv_pos, pf = prev_real_pos(prev_items)

    # Counting context: surrounded by other numerals
    prev_forms_lower = [f.lower() for f, p in prev_items]
    next_forms_lower = [f.lower() for f, p in next_items]
    num_words = {"zwei", "drey", "drei", "czwei", "czwene", "czwo", "zwo", "dri",
                 "vier", "funf", "funfte", "sechs", "sieben", "acht", "neun", "zehn",
                 "zwelf", "zwelf", "hundert", "tousent"}
    if any(w in num_words for w in prev_forms_lower + next_forms_lower):
        if pv_pos == "NUM" or np_pos == "NUM":
            return "NUM", "medium", "counting context with neighboring NUM"

    # Standard article: next is NOM/ADJ/NAM
    if np_pos in NP_POS:
        return "DET", "high", f"indefinite article before {np_pos} '{nf}'"

    # Before pronoun or clause → NUM (standalone "one")
    if np_pos in CLAUSE_POS and np_pos not in {"NEG"}:
        return "NUM", "medium", f"standalone numeral, next is {np_pos}"

    # Default: article (overwhelmingly common in biblical prose)
    if np_pos:
        return "DET", "medium", f"default article reading, next pos={np_pos}"

    return None, "low", "no tagged neighbor"


def resolve_haben(prev_items, next_items, form):
    """
    lemma_2598 haben → VEX or VRB (NOM reading is negligible in WZB).
    VEX: perfect/passive auxiliary with Partizip II nearby
    VRB: lexical (possession, etc.)
    """
    if has_participle_nearby(prev_items, next_items):
        return "VEX", "high", "Partizip II nearby → perfect auxiliary"

    # Check if any neighbor is tagged VRB (could be participle tagged as VRB)
    for form_n, pos_n in list(prev_items) + list(next_items):
        if pos_n == "VRB" and form_n.lower().startswith("ge"):
            return "VEX", "high", f"ge- prefixed VRB neighbor '{form_n}' → likely participle"

    # Also check for infinitive patterns (modal → haben as complement)
    pv_pos, pf = prev_real_pos(prev_items)
    if pv_pos == "VEM":
        return "VRB", "medium", "after modal → lexical infinitive haben"

    return "VRB", "medium", "no participle found → lexical haben"


def resolve_adv_prp(lemma_orth, prev_items, next_items, form):
    """
    ûf, ûʒ, wider, vor → PRP or ADV.
    PRP: governs a following NP (next @pos in NP_POS)
    ADV: verbal particle/prefix (next @pos is VERBAL or nothing)
    """
    np_pos, nf = next_real_pos(next_items)

    if np_pos in NP_POS | PRONOUN_POS:
        return "PRP", "high", f"governs following {np_pos} '{nf}'"

    if np_pos in VERBAL_POS:
        return "ADV", "high", f"verbal particle before {np_pos} '{nf}'"

    # Particle at end of clause (next is NEG, SCNJ, CCNJ, punctuation-like)
    if np_pos in {"NEG", "SCNJ", "CCNJ", "CNJ"}:
        return "ADV", "medium", f"particle, next is {np_pos}"

    if not np_pos:
        return "ADV", "low", "end of sequence, default particle"

    return "PRP", "medium", f"default preposition reading, next pos={np_pos}"


def resolve_ir(prev_items, next_items, form):
    """
    lemma_56117 ir → POS (possessive) or PRO (personal pronoun).
    POS: modifies following NOM/ADJ
    PRO: subject before verb, or standalone object
    Fallback: POS when capitalised (sentence-initial possessive), PRO otherwise.
    """
    np_pos, nf = next_real_pos(next_items)

    if np_pos in NP_POS:
        return "POS", "high", f"possessive modifying {np_pos} '{nf}'"

    if np_pos in VERBAL_POS:
        return "PRO", "high", f"subject pronoun before {np_pos} '{nf}'"

    if np_pos in {"PRP", "ADV"}:
        return "PRO", "medium", f"pronoun before {np_pos}, likely object"

    # After verb → object PRO
    pv_pos, pf = prev_real_pos(prev_items)
    if pv_pos in VERBAL_POS:
        return "PRO", "medium", f"after {pv_pos}, likely object pronoun"

    # Fallback: capitalised "Ir" at clause boundary is typically possessive
    # (e.g. "Ir man", "Ir volck"); lowercase "ir" after content words → PRO
    if form[:1].isupper():
        return "POS", "medium", "capitalised Ir at clause boundary → possessive POS"
    return "PRO", "medium", "fallback PRO (ir as 3pl/2pl pronoun)"


def resolve_noch(prev_items, next_items, form):
    """
    lemma_4415 noch → ADV (yet/still), CCNJ (nor/and not), or PRP (after/according to).
    - CCNJ (nor): in negative context, coordinates two elements (nicht ... noch)
    - PRP: temporal/conformative "after/according to" + NP
    - ADV: temporal "yet/still" (nicht noch = not yet)
    Fallback: ADV (most common reading in WZB narrative prose).
    """
    np_pos, nf = next_real_pos(next_items)
    pv_pos, pf = prev_real_pos(prev_items)

    # Check for preceding NEG (nicht ... noch = nor / not yet)
    prev_has_neg = any(p == "NEG" for f, p in prev_items)
    # Check for preceding CCNJ (und ... noch = and ... still)
    prev_has_ccnj = any(p == "CCNJ" for f, p in prev_items)

    # "noch NOM/DET" in narrative without negation = PRP (after/according to)
    if np_pos in NP_POS and not prev_has_neg:
        return "PRP", "medium", f"temporal/conformative nach + {np_pos} '{nf}'"

    # "nicht ... noch ... VRB" = CCNJ (nor)
    if prev_has_neg and np_pos in VERBAL_POS | NP_POS:
        return "CCNJ", "medium", "coordinating negation: nicht...noch (nor)"

    # "noch nicht" = ADV (not yet)
    if nf.lower() in ("nicht", "ny", "nit", "nie", "niht", "kein"):
        return "ADV", "medium", "noch nicht = not yet → temporal ADV"

    # After CCNJ (und noch, oder noch) → ADV
    if prev_has_ccnj:
        return "ADV", "medium", "after CCNJ → noch as temporal ADV"

    # Fallback: ADV is the most frequent reading in WZB narrative prose
    return "ADV", "medium", "fallback ADV (noch = still/yet, most common in WZB)"


def resolve_reht(prev_items, next_items, form):
    """
    lemma_4840 reht → ADJ or NOM.
    ADJ: attributive (before NOM) or predicative (after copula)
    NOM: "das Recht" (law, right) - standalone after DET
    """
    np_pos, nf = next_real_pos(next_items)
    pv_pos, pf = prev_real_pos(prev_items)

    # After DET alone → NOM ("das recht" = the law)
    if pv_pos == "DET" and np_pos not in NP_POS:
        return "NOM", "medium", "after DET, not modifying NOM → substantive das Recht"

    # Before NOM → ADJ (attributive "rechten vinger")
    if np_pos in {"NOM", "NAM"}:
        return "ADJ", "high", f"attributive before {np_pos} '{nf}'"

    # After DET and before NOM → ADJ
    if pv_pos == "DET" and np_pos in {"NOM", "NAM", "ADJ"}:
        return "ADJ", "high", "attributive in DET+ADJ+NOM sequence"

    # Genitive form (rechts, rechtes) → NOM
    f_lower = form.lower()
    if f_lower in ("rechts", "rechtes", "recht"):
        if np_pos not in NP_POS:
            return "NOM", "medium", "genitive/standalone form → NOM das Recht"

    return "ADJ", "medium", "default ADJ reading for reht"


def resolve_riche(prev_items, next_items, form):
    """
    lemma_4872 rîche → NOM (kingdom) or ADJ (rich/powerful).
    NOM: "das reich" - after DET, or genitive "des reiches"
    ADJ: attributive/predicative
    """
    np_pos, nf = next_real_pos(next_items)
    pv_pos, pf = prev_real_pos(prev_items)

    f_lower = form.lower()
    # Genitive NOM: "des reiches", "irm reiche"
    if pv_pos == "DET" and f_lower in ("reich", "reiche", "reichs", "reiches", "reichen"):
        if np_pos not in {"NOM", "ADJ"}:
            return "NOM", "medium", "DET + reich (no following NOM) → das Reich"

    # Attributive ADJ: "ein reiches volk"
    if np_pos in {"NOM", "NAM"}:
        return "ADJ", "medium", f"attributive before {np_pos}"

    # After copula (ist, wirt) → ADJ predicative ("wirt rich")
    if pv_pos in VERBAL_POS:
        return "ADJ", "medium", "predicative after verb"

    return "NOM", "medium", "default NOM reading (das Reich)"


def resolve_e(prev_items, next_items, form):
    """
    lemma_1281 ê → ADV (before/formerly/ever) or NOM (law, Gesetz).
    ADV: temporal "before" / "ever" (most common in comparative constructions)
    NOM: "die ê" (the law/covenant) — after DET
    """
    np_pos, nf = next_real_pos(next_items)
    pv_pos, pf = prev_real_pos(prev_items)

    # After DET → NOM (die ê = the law)
    if pv_pos == "DET":
        return "NOM", "medium", "after DET → die ê (law)"

    # Comparative/temporal: "ê dann", "ê daz", or before clause
    f_lower = form.lower()
    if nf.lower() in ("daz", "dan", "dann", "danne", "als", "e"):
        return "ADV", "medium", "comparative/temporal ê daz/dann → ADV"

    if np_pos in CLAUSE_POS:
        return "ADV", "medium", f"before clause ({np_pos}) → temporal ADV"

    # Default in WZB biblical context: temporal ADV
    return "ADV", "medium", "default temporal ADV"


def resolve_leben(prev_items, next_items, form):
    """
    lemma_3659 leben → NOM (life) or VRB (to live).
    VRB: conjugated forms (lebte, lebt, gelebt) or infinitive after modal
    NOM: "das Leben" after DET, or genitive "des Lebens"
    """
    f_lower = form.lower()

    # Conjugated verbal forms
    verbal_forms = {"lebte", "lebten", "lebt", "lebest", "lebest", "gelebet",
                    "lebende", "lebenden", "lebendige"}
    if f_lower in verbal_forms or f_lower.startswith("lebte") or f_lower.startswith("lebt"):
        return "VRB", "high", "conjugated form → VRB"

    np_pos, nf = next_real_pos(next_items)
    pv_pos, pf = prev_real_pos(prev_items)

    # After DET → NOM (das Leben)
    if pv_pos == "DET":
        return "NOM", "high", "after DET → das Leben (NOM)"

    # After modal → infinitive VRB
    if pv_pos == "VEM":
        return "VRB", "high", "after modal → infinitive leben"

    # Genitive form "lebens"
    if f_lower in ("lebens", "lebenes"):
        return "NOM", "high", "genitive form → NOM des Lebens"

    # Base form "leben" after verb → infinitive VRB
    if f_lower == "leben" and pv_pos in VERBAL_POS | {"VEM"}:
        return "VRB", "medium", "infinitive after verb"

    return "NOM", "medium", "default NOM reading"


def resolve_tot(prev_items, next_items, form):
    """
    lemma_6118 tôt → ADJ (dead) or NOM (death/dead person).
    ADJ: attributive/predicative ("ein toter man", "er ist tot")
    NOM: "der Tot" (death) after DET, or "die Toten" (the dead)
    """
    f_lower = form.lower()
    np_pos, nf = next_real_pos(next_items)
    pv_pos, pf = prev_real_pos(prev_items)

    # Strong plural "die Toten" → NOM
    if f_lower in ("toten", "tote") and pv_pos == "DET":
        if np_pos not in {"NOM", "NAM"}:
            return "NOM", "medium", "die Toten → plural NOM (the dead)"

    # "der Tot" (death personified) → NOM
    if f_lower in ("tod", "tods", "todes", "tode"):
        return "NOM", "high", "genitive/dative form of Tod → NOM"

    # Attributive before NOM → ADJ
    if np_pos in {"NOM", "NAM"}:
        return "ADJ", "high", f"attributive before {np_pos} '{nf}'"

    # After copula → predicative ADJ
    if pv_pos in VERBAL_POS:
        return "ADJ", "medium", "predicative after verb → ADJ"

    return "ADJ", "medium", "default ADJ reading"


def resolve_halbe(prev_items, next_items, form):
    """
    lemma_2617 halbe → NUM (half, quantity) or ADJ (half, attribute).
    NUM: "ein halbe schussel" — quantifying
    ADJ: "das halbe geslechte" — attributive fraction
    """
    np_pos, nf = next_real_pos(next_items)
    pv_pos, pf = prev_real_pos(prev_items)

    # After DET directly → ADJ (das halbe X)
    if pv_pos == "DET":
        return "ADJ", "medium", "after DET → attributive ADJ"

    # After ein/einen → NUM (ein halbes = a half)
    if pf.lower() in ("ein", "einen", "einem", "eine", "eines"):
        return "NUM", "medium", "after ein → numeral half"

    # Before NOM → ADJ (halbe seite)
    if np_pos in {"NOM", "NAM"}:
        return "ADJ", "medium", f"attributive before {np_pos}"

    return "NUM", "medium", "default NUM reading"


def resolve_zehende(prev_items, next_items, form):
    """
    lemma_7780 zehende → NUM (tenth, ordinal) or NOM (tithe).
    NOM: "der zehende" = the tithe (tenth part as tax) after DET alone
    NUM: "der zehende tac" = the tenth day (ordinal modifying NOM)
    """
    np_pos, nf = next_real_pos(next_items)
    pv_pos, pf = prev_real_pos(prev_items)

    # Before NOM → ordinal NUM
    if np_pos in {"NOM", "NAM"}:
        return "NUM", "high", f"ordinal before {np_pos} '{nf}' → tenth X"

    # After DET, no following NOM → NOM (tithe)
    if pv_pos == "DET" and np_pos not in NP_POS:
        return "NOM", "high", "after DET, standalone → der Zehnte (tithe NOM)"

    return "NOM", "medium", "default NOM reading (tithe)"


def resolve_wart(prev_items, next_items, form):
    """
    lemma_7489 wart/wurde → VEX (passive auxiliary) or VRB (became).
    VEX: wart + Partizip II = passive ("wart geheissen")
    VRB: wart + ADJ/NOM = became ("wart ein ritter")
    """
    if has_participle_nearby(prev_items, next_items):
        return "VEX", "high", "Partizip II nearby → passive VEX"

    np_pos, nf = next_real_pos(next_items)

    if np_pos in {"NOM", "ADJ", "DET"}:
        return "VRB", "high", f"wart/wurde + {np_pos} → became (VRB)"

    if np_pos in VERBAL_POS:
        return "VEX", "medium", f"before {np_pos} → likely auxiliary"

    return "VRB", "medium", "default VRB reading (became)"


def resolve_nehst(prev_items, next_items, form):
    """
    lemma_4281 næhst/nach → ADJ (nearest), ADV, PRP (after/according to), or NOM.
    Most common in WZB: PRP "nach" (after/according to)
    ADJ: "der nehste" (the nearest/neighbor)
    """
    np_pos, nf = next_real_pos(next_items)
    pv_pos, pf = prev_real_pos(prev_items)

    f_lower = form.lower()

    # "nach" forms → PRP (after/according to)
    if f_lower in ("nach", "noch"):
        if np_pos in NP_POS | PRONOUN_POS:
            return "PRP", "high", f"nach + {np_pos} → preposition"

    # "nehste/nehsten" → ADJ (the nearest/neighbor)
    if f_lower in ("nehste", "nehsten", "nehstem", "nehster"):
        if np_pos in {"NOM", "NAM"}:
            return "ADJ", "high", f"attributive nehst + {np_pos}"
        if pv_pos == "DET":
            return "NOM", "medium", "der nehste (the neighbor) → NOM"
        return "ADJ", "medium", "nehst form → ADJ"

    if np_pos in NP_POS | PRONOUN_POS:
        return "PRP", "high", f"governs {np_pos} '{nf}' → PRP"

    return "PRP", "medium", "default PRP reading"


def resolve_du_dein(prev_items, next_items, form):
    """
    lemma_1242 dû/dein variants → DET, POS, or PRO.
    dein-forms → POS (possessive)
    du/dich/dir/dein → PRO (personal)
    """
    f_lower = form.lower()
    if f_lower in ("dein", "deinen", "deinem", "deiner", "deine", "deines",
                   "deyn", "deynem", "deynen", "deyner", "deyne", "deynes"):
        return "POS", "high", "possessive form → POS"

    if f_lower in ("du", "dv", "dich", "dir", "dy"):
        return "PRO", "high", "personal pronoun form → PRO"

    return "PRO", "medium", "default PRO reading"


def resolve_wir_unser(prev_items, next_items, form):
    """
    lemma_7643 wir/unser → POS (possessive) or PRO (personal pronoun).
    Possessive forms (unser-, vnser-, vns- paradigm) → POS
    Personal pronoun forms (wir, uns as standalone) → PRO
    In WZB all unresolved instances are possessive (Unser, unserm, vnses, etc.)
    """
    f_lower = form.lower()
    # Any declined possessive form: unser/vnser prefix covers all cases
    if f_lower.startswith("uns") or f_lower.startswith("vns"):
        return "POS", "high", "possessive form unser- → POS"
    if f_lower in ("wir", "uns"):
        return "PRO", "high", "personal pronoun wir/uns → PRO"
    return "POS", "medium", "default POS reading (wir paradigm)"


def resolve_ym(prev_items, next_items, form):
    """
    lemma_1517 ým → PRO.
    Bohemian dative of 'er' (MHG 'im' = ihm). Always personal pronoun.
    """
    return "PRO", "high", "dative pronoun ým (Bohemian ihm) → PRO"


def resolve_latin_esse(prev_items, next_items, form):
    """
    lemma_9387 Latin esse forms → VEX (copula) or VRB.
    Copula/auxiliary forms (est, erat, erant, sunt, sit) → VEX
    Jussive/modal forms (Fiat, fiat) → VRB
    """
    f_lower = form.lower()
    if f_lower in ("est", "erat", "erant", "sunt", "sit", "esset", "esse", "fuit", "erit"):
        return "VEX", "high", "Latin copula form → VEX"
    if f_lower in ("fiat", "fiant"):
        return "VRB", "medium", "Latin jussive fiat → VRB"
    return "VEX", "medium", "default Latin esse copula → VEX"


# Dispatch table: lemma_id -> resolver function
RESOLVERS = {
    "lemma_1097":  resolve_daz,
    "lemma_1331":  resolve_ein,
    "lemma_2598":  resolve_haben,
    "lemma_6330":  lambda p, n, f: resolve_adv_prp("ûf", p, n, f),
    "lemma_6342":  lambda p, n, f: resolve_adv_prp("ûʒ", p, n, f),
    "lemma_7557":  lambda p, n, f: resolve_adv_prp("wider", p, n, f),
    "lemma_7194":  lambda p, n, f: resolve_adv_prp("vor", p, n, f),
    # ADV|PRP lemmata using the same next-NP heuristic
    "lemma_1410":  lambda p, n, f: resolve_adv_prp("enkegen", p, n, f),
    "lemma_1089":  lambda p, n, f: resolve_adv_prp("dorouf", p, n, f),
    "lemma_4325":  lambda p, n, f: resolve_adv_prp("neben", p, n, f),
    "lemma_1090":  lambda p, n, f: resolve_adv_prp("dorous", p, n, f),
    "lemma_20032": lambda p, n, f: resolve_adv_prp("hinvber", p, n, f),
    "lemma_37960": lambda p, n, f: resolve_adv_prp("con", p, n, f),
    "lemma_56117": resolve_ir,
    "lemma_4415":  resolve_noch,
    "lemma_4840":  resolve_reht,
    "lemma_4872":  resolve_riche,
    "lemma_1281":  resolve_e,
    "lemma_3659":  resolve_leben,
    "lemma_6118":  resolve_tot,
    "lemma_2617":  resolve_halbe,
    "lemma_7780":  resolve_zehende,
    "lemma_7489":  resolve_wart,
    "lemma_4281":  resolve_nehst,
    "lemma_1242":  resolve_du_dein,
    # New: wir/unser possessive, dative pronoun, Latin esse
    "lemma_7643":  resolve_wir_unser,
    "lemma_1517":  resolve_ym,
    "lemma_9387":  resolve_latin_esse,
}


def main():
    parser = argparse.ArgumentParser(description="Context-based POS resolution for WZB Phase 2")
    parser.add_argument("--tei", default="Wenzelsbibel/WZB.lemma-autofill.tei.xml")
    parser.add_argument("--pending", default="Wenzelsbibel/wzb-pos-pending.tsv")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    tei_path = Path(args.tei)
    pending_path = Path(args.pending)

    print(f"Loading TEI from {tei_path} ...")
    w_list, id_to_idx = build_w_index(tei_path)
    print(f"  {len(w_list)} <w> elements indexed")

    # Load pending TSV
    rows = []
    with pending_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    # Stats
    stats = defaultdict(lambda: defaultdict(int))
    updated = 0
    skipped_already_resolved = 0
    skipped_no_resolver = 0
    skipped_no_id = 0
    skipped_low_confidence = 0

    for row in rows:
        if row["resolved_pos"].strip():
            skipped_already_resolved += 1
            continue

        lid = row["lemma_id"]
        if lid not in RESOLVERS:
            skipped_no_resolver += 1
            continue

        xml_id = row["xml_id"]
        if xml_id not in id_to_idx:
            skipped_no_id += 1
            continue

        idx = id_to_idx[xml_id]
        form = row["form"]
        prev_items, next_items = get_neighbors(w_list, idx, window=4)

        resolver = RESOLVERS[lid]
        pos, confidence, reason = resolver(prev_items, next_items, form)

        if pos is None or confidence == "low":
            skipped_low_confidence += 1
            stats[lid]["low_confidence"] += 1
            continue

        row["resolved_pos"] = pos
        row["confidence"] = confidence
        row["reviewer"] = REVIEWER
        updated += 1
        stats[lid][pos] += 1

    print(f"\nResults:")
    print(f"  Updated:                  {updated}")
    print(f"  Already resolved (skip):  {skipped_already_resolved}")
    print(f"  No resolver (skip):       {skipped_no_resolver}")
    print(f"  Low confidence (skip):    {skipped_low_confidence}")
    print(f"  xml_id not found (skip):  {skipped_no_id}")

    print(f"\nBreakdown by lemma:")
    for lid, tag_counts in sorted(stats.items()):
        total = sum(tag_counts.values())
        detail = ", ".join(f"{t}:{c}" for t, c in sorted(tag_counts.items()))
        sys.stdout.buffer.write(f"  {lid}: {total}t -> {detail}\n".encode("utf-8"))

    if args.dry_run:
        print("\nDRY RUN: no changes written.")
        return

    with pending_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWritten to {pending_path}")


if __name__ == "__main__":
    main()
