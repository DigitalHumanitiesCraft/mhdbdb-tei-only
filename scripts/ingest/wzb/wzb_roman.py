#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roman numeral helpers shared by the WZB structural scripts (#171 F34).

WZB conventions: U counts as V (5), and spaces between letters are
ignored ("I X" -> IX = 9) because the transcription sometimes splits
numerals across <w> boundaries. Was previously duplicated (and in the
cleanup copy: not space-tolerant) in wzb-structural-cleanup.py and
wzb-structural-fix.py.
"""

ROMAN_CHARS = set("IVXLCDUM")

_VALS = {"I": 1, "V": 5, "X": 10, "L": 50,
         "C": 100, "D": 500, "M": 1000, "U": 5}


def is_roman_numeral(text: str) -> bool:
    """Return True if text consists entirely of Roman numeral chars
    (WZB: U=V; spaces between letters allowed)."""
    t = text.strip().replace(" ", "")
    return bool(t) and len(t) <= 10 and all(c in ROMAN_CHARS for c in t)


def roman_to_arabic(text: str) -> int:
    """Convert Roman numeral string (U=V; spaces between letters ignored)
    to integer. Returns 0 on failure."""
    t = text.strip().replace(" ", "")   # "I X" -> "IX"
    if not t:
        return 0
    result, prev = 0, 0
    for ch in reversed(t):
        v = _VALS.get(ch, 0)
        result = result - v if v < prev else result + v
        prev = v
    return result
