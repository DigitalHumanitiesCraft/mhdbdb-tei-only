#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#526 Punkt 4: die 48 unannotierten WZB-Tokens mit Breve (U+0306) auf w oder n,
dazu der Nebenfund vom 07.10.2026: 3 nackte vnd ohne @lemmaRef.

Das Breve auf w und n (w̆, n̆) ist in der WZB ein Schreibzeichen ohne
Lautwert fuer die Annotation. Verglichen wird deshalb mit der Form ohne Breve.
Entschieden wird jeder Fall am Vers, und geschrieben wird nur, wo die
Vergleichsform in der WZB selbst schon so annotiert ist. Das Skript misst
deren Annotation im TEI nach und bricht ab, wenn sie das gewaehlte Lemma mit
der gewaehlten Wortart nicht traegt.

Regel:
  E  Die Vergleichsform traegt in der WZB ausnahmslos dieses Lemma und diese
     Wortart. Der Vers widerspricht nicht.

Nicht annotiert (REVIEW, fuer Christian):
  - strew̆e (WZB_90ra_20_7): die einzige annotierte Vergleichsform strewe ist
    stroeuwe NOM, am Vers steht ein Verb ("das ich dich icht zu strew̆e").
  - die 18 Tokens, deren Form ohne Breve in der WZB nirgends annotiert ist.

KEIN @corresp, KEIN @ana, wie in wzb-breve-526.py und wzb-makron-526.py: die
Typfrage liegt in #370. GRA wird nie vergeben.

FOLGEN: @lemmaRef kommt neu hinzu, also Korpus-Index, API und Begriffshilfe
neu bauen; variants.xml und der Authority-Index bleiben unberuehrt.

Nicht idempotent: ein zweiter Lauf findet die Tokens annotiert vor und bricht
ab.

Usage:
    python scripts/ingest/wzb/wzb-breve-wn-526.py \
        --out-dir ingest/pos-disambig/526-breve-wn [--apply]
"""
import argparse
import csv
import gzip
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DATEI = REPO / "tei" / "WZB.tei.xml"
AUTH_INDEX = REPO / "data" / "authority-index.json.gz"

TAGS_19 = {"NOM", "NAM", "ADJ", "ADV", "DET", "POS", "PRO", "PRP", "NEG", "NUM",
           "CNJ", "SCNJ", "CCNJ", "IPA", "VRB", "VEX", "VEM", "INJ", "DIG"}

BREVE = "̆"

# xml:id -> (Lemma, Wortart, Regel, Vergleichsform, Begruendung)
ENTSCHEIDUNGEN = {
    # stiure
    "WZB_1ra_20_1":   ("lemma_5779", "NOM", "E", "stewer",
                       "sendest mir Deiner gnaden stew̆er, stiure (Hilfe)"),
    # hûsvrouwe
    "WZB_12ra_10_4":  ("lemma_2938", "NOM", "E", "hausvrow",
                       "vnd sein hausvrow̆ vnd alles das er hette"),
    "WZB_22va_18_7":  ("lemma_2938", "NOM", "E", "housvrow",
                       "vnd sei ein housvrow̆ deines herren svn"),
    "WZB_37ra_26_2":  ("lemma_2938", "NOM", "E", "housvrow",
                       "vnd sein housvrow̆ was genant"),
    # tou
    "WZB_26rb_2_6":   ("lemma_6154", "NOM", "E", "taw",
                       "von dem taw̆ des himels"),
    # ir (Possessiv)
    "WZB_34va_6_2":   ("lemma_56117", "POS", "E", "ewer",
                       "Ew̆er tŏchter gebt vns"),
    "WZB_44va_3_0":   ("lemma_56117", "POS", "E", "ewerr",
                       "Ew̆err bruder einen laset ir bei mir"),
    "WZB_64vb_28_6":  ("lemma_56117", "POS", "E", "ewer",
                       "Ew̆er lenden sult ir gurten"),
    "WZB_65ra_13_4":  ("lemma_56117", "POS", "E", "ewern",
                       "in ew̆ern geslechten"),
    "WZB_88ra_33_2":  ("lemma_56117", "POS", "E", "ewern",
                       "in ew̆ern geperungen"),
    "WZB_100vb_22_5": ("lemma_56117", "POS", "E", "ewern",
                       "in ew̆ern geperungen vnd wonungen"),
    "WZB_108ra_17_6": ("lemma_56117", "POS", "E", "ewer",
                       "der czorn Ew̆er bruder"),
    "WZB_236rb_2_5":  ("lemma_56117", "POS", "E", "ewern",
                       "rue vnd fried ew̆ern brudern"),
    # beschouwen
    "WZB_44vb_9_4":   ("lemma_571", "VRB", "E", "beschowet",
                       "Ir beschow̆et nicht mein angesichte"),
    # niuwe
    "WZB_93va_10_3":  ("lemma_4390", "ADJ", "E", "newe",
                       "kvnnen vinden ouch new̆e"),
    "WZB_193va_7_4":  ("lemma_4390", "ADJ", "E", "new",
                       "der new̆ kvmene, wie new kvmene in WZB_193rb_26_0 (ADJ)"),
    "WZB_196va_35_1": ("lemma_4390", "ADJ", "E", "newes",
                       "ein new̆es hous"),
    "WZB_223ra_21_1": ("lemma_4390", "ADJ", "E", "newe",
                       "Die weinkufel fulte wir new̆e"),
    # niuwekomen
    "WZB_203ra_2_1":  ("lemma_8598", "VRB", "E", "newkomen",
                       "der new̆komen der mit dir ist"),
    "WZB_204ra_10_2": ("lemma_8598", "VRB", "E", "newkomen",
                       "das gerichte des new̆komen vnd des waisen"),
    "WZB_222va_7_2":  ("lemma_8598", "VRB", "E", "newkomen",
                       "als der new̆komen also der lantman"),
    "WZB_222va_24_4": ("lemma_8598", "VRB", "E", "newkomen",
                       "vnd den new̆komen die do wonten vnder yn"),
    # wan (Konjunktion)
    "WZB_133ra_31_4": ("lemma_7385", "SCNJ", "E", "wenn",
                       "Wenn̆ meyn ist alle erste gepurt, denn"),
    "WZB_148rb_8_6":  ("lemma_7385", "SCNJ", "E", "wenn",
                       "sprich zu in Wenn̆ ir ein geczogen seit"),
    "WZB_148vb_18_7": ("lemma_7385", "SCNJ", "E", "wenn",
                       "Wenn̆ sie nicht von willen habn gesunt"),
    "WZB_208rb_37_3": ("lemma_7385", "SCNJ", "E", "wenne",
                       "wenn̆e wider DEUTRO keren wirt vnser herre"),
    # ströuwen
    "WZB_206ra_7_0":  ("lemma_5827", "VRB", "E", "strewet",
                       "bis her dich czu strew̆et vnd vorterbet"),
    "WZB_238ra_5_3":  ("lemma_5827", "VRB", "E", "strewen",
                       "wirt sie zu strew̆en vnd ouf heben"),
    # mûre
    "WZB_219ra_24_4": ("lemma_4220", "NOM", "E", "mowern",
                       "di mow̆ern der stat alczuhant nider vilen"),
    # Nebenfund: nackte vnd
    "WZB_6rb_30_2":   ("lemma_6467", "CCNJ", "E", "vnd",
                       "dreissig vnd nevn hundert iar vnd geperte, und"),
    "WZB_11rb_2_3":   ("lemma_6467", "CCNJ", "E", "vnd",
                       "des vaters vnd melcha vnd des vaters, und"),
    "WZB_28rb_2_7":   ("lemma_6467", "CCNJ", "E", "vnd",
                       "bist mein bein vnd bist mein, und"),
}

KEINE_VERGLEICHSFORM = "Form ohne Breve in der WZB nirgends annotiert"

# xml:id -> Begruendung
NICHT_ANNOTIERT = {
    "WZB_90ra_20_7":   "strewe ist in der WZB nur stroeuwe NOM (WZB_150vb_13_3), am Vers Verb "
                       "(das ich dich icht zu strew̆e); Vorschlag lemma_5827 VRB wie czu strewet (WZB_206ra_7_0)",
    "WZB_10vb_3_3":    KEINE_VERGLEICHSFORM,
    "WZB_21ra_36_4":   KEINE_VERGLEICHSFORM,
    "WZB_21va_19_0":   KEINE_VERGLEICHSFORM,
    "WZB_34va_9_6":    KEINE_VERGLEICHSFORM,
    "WZB_42vb_3_7":    KEINE_VERGLEICHSFORM,
    "WZB_46vb_33_2":   KEINE_VERGLEICHSFORM,
    "WZB_47ra_22_3":   KEINE_VERGLEICHSFORM,
    "WZB_54ra_18_1":   KEINE_VERGLEICHSFORM,
    "WZB_61vb_18_5":   KEINE_VERGLEICHSFORM,
    "WZB_65ra_9_3":    KEINE_VERGLEICHSFORM,
    "WZB_67ra_25_6":   KEINE_VERGLEICHSFORM,
    "WZB_72va_21_2":   KEINE_VERGLEICHSFORM,
    "WZB_75rb_7_1":    KEINE_VERGLEICHSFORM,
    "WZB_76vb_35_2":   KEINE_VERGLEICHSFORM,
    "WZB_76vb_36_4":   KEINE_VERGLEICHSFORM,
    "WZB_78rb_5_6":    KEINE_VERGLEICHSFORM,
    "WZB_84vb_4_3":    KEINE_VERGLEICHSFORM,
    "WZB_233vb_15_4":  KEINE_VERGLEICHSFORM,
}

W_TEMPLATE = r'<w xml:id="{xid}">(?P<form>[^<]*)</w>'

CHANGE_VORLAGE = (
    '<change when="{datum}" who="#editor">#526 Punkt 4: {n_breve} Tokens mit '
    'Breve (U+0306) auf w oder n nachannotiert (lemmaRef und pos), je am Vers und '
    'nur, wo die Form ohne Breve in der WZB schon so annotiert ist; dazu {n_vnd} '
    'vnd ohne lemmaRef als und (CCNJ). {r} Tokens bleiben zur Pruefung '
    'unannotiert. Kein corresp und kein ana. Provenienz-Log: {log}.</change>'
)


def pfad(p):
    p = Path(p)
    return p if p.is_absolute() else REPO / p


def repo_relativ(p):
    p = pfad(p).resolve()
    try:
        return p.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        sys.exit("FEHLER: %s liegt ausserhalb des Repositoriums." % p)


def nfc(s):
    return unicodedata.normalize("NFC", s or "")


def ohne_breve(form):
    return nfc(unicodedata.normalize("NFD", form).replace(BREVE, "")).lower()


def lade_lemma_pos():
    idx = json.load(gzip.open(AUTH_INDEX, "rt", encoding="utf-8"))
    aus = {}
    for l in idx["lemmata"]:
        pa = l.get("posAll") or ([l["pos"]] if l.get("pos") else [])
        aus[l["id"]] = ([p for p in pa if p], l.get("lemma", ""))
    return aus


def messe_tei(text):
    """Unannotierte w/n-Breve-Tokens, nackte vnd, Annotation jeder Form, Umfeld."""
    tokens = []
    annot = defaultdict(Counter)
    for m in re.finditer(r'<w xml:id="(?P<id>[^"]+)"(?P<attr>[^>]*)>(?P<form>[^<]*)</w>', text):
        form = m.group("form")
        lemma = re.search(r'lemmaRef="lexicon\.xml#([^"]+)"', m.group("attr"))
        pos = re.search(r'pos="([^"]+)"', m.group("attr"))
        tokens.append((m.group("id"), form, bool(lemma)))
        if lemma:
            annot[nfc(form).lower()][(lemma.group(1), pos.group(1) if pos else "")] += 1
    ziel = {}
    umfeld = {}
    for i, (xid, form, annotiert) in enumerate(tokens):
        if annotiert:
            continue
        nfd = unicodedata.normalize("NFD", form)
        traeger = {nfd[j - 1].lower() for j, c in enumerate(nfd) if c == BREVE and j > 0}
        if traeger & {"w", "n"} or nfc(form).lower() == "vnd":
            ziel[xid] = form
            umfeld[xid] = "%s [[%s]] %s" % (" ".join(t[1] for t in tokens[max(0, i - 6):i]), form,
                                          " ".join(t[1] for t in tokens[i + 1:i + 7]))
    return ziel, annot, umfeld


def main() -> int:
    # Windows-Konsole (cp1252) kann das Breve nicht ausgeben
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    text = DATEI.read_text(encoding="utf-8", newline="")
    ziel, annot, umfeld = messe_tei(text)

    tafel = set(ENTSCHEIDUNGEN) | set(NICHT_ANNOTIERT)
    if set(ENTSCHEIDUNGEN) & set(NICHT_ANNOTIERT):
        sys.exit("FEHLER: eine xml:id steht in beiden Tafeln.")
    if set(ziel) != tafel:
        sys.exit("FEHLER: Tafel und Ziel-Tokens im TEI decken sich nicht.\n"
                 "  ohne Entscheidung: %s\n  nicht (mehr) unannotiert im TEI: %s"
                 % (sorted(set(ziel) - tafel) or "-", sorted(tafel - set(ziel)) or "-"))

    lemma_pos = lade_lemma_pos()
    zeilen = []
    for xid in sorted(tafel):
        form = ziel[xid]
        vergleich_auto = "vnd" if nfc(form).lower() == "vnd" else ohne_breve(form)
        if xid in NICHT_ANNOTIERT:
            grund = NICHT_ANNOTIERT[xid]
            if grund == KEINE_VERGLEICHSFORM and annot.get(vergleich_auto):
                sys.exit("FEHLER: %s steht als ohne Vergleichsform, aber %r ist annotiert (%s)"
                         % (xid, vergleich_auto, dict(annot[vergleich_auto])))
            zeilen.append({"file": DATEI.name, "xml_id": xid, "form": form,
                           "action": "REVIEW", "neu_lemmaRef": "", "neu_pos": "",
                           "regel": "", "vergleichsform": vergleich_auto,
                           "vergleich_belege": "; ".join("%s %s x%d" % (l, p, n) for (l, p), n
                                                         in annot.get(vergleich_auto, Counter()).most_common()),
                           "ziel_lemma_form": "", "begruendung": grund, "umfeld": umfeld[xid]})
            continue
        lemma, pos, regel, vergleich, grund = ENTSCHEIDUNGEN[xid]
        if vergleich != vergleich_auto:
            sys.exit("FEHLER: %s: Vergleichsform der Tafel %r ist nicht die Form ohne Breve %r"
                     % (xid, vergleich, vergleich_auto))
        posAll, lemmaform = lemma_pos.get(lemma, ([], ""))
        # CCNJ/SCNJ sind die ausdifferenzierten CNJ (POS-TAGSET, K5); das
        # Lexikon fuehrt bei und/wan weiter nur CNJ, die WZB annotiert CCNJ/SCNJ.
        erlaubt = set(posAll) | ({"CCNJ", "SCNJ"} if "CNJ" in posAll else set())
        if pos not in TAGS_19 or pos not in erlaubt:
            sys.exit("FEHLER: %s bekaeme %r, %s fuehrt %s" % (xid, pos, lemma, " ".join(posAll)))
        belege = annot.get(vergleich, Counter())
        treffer = belege.get((lemma, pos), 0)
        if regel != "E":
            sys.exit("FEHLER: %s: unbekannte Regel %r" % (xid, regel))
        if treffer == 0 or treffer != sum(belege.values()):
            sys.exit("FEHLER: %s: Regel E, aber %r ist in der WZB nicht ausnahmslos %s %s (%s)"
                     % (xid, vergleich, lemma, pos, dict(belege)))
        zeilen.append({"file": DATEI.name, "xml_id": xid, "form": form,
                       "action": "ANNOTATE", "neu_lemmaRef": "lexicon.xml#" + lemma,
                       "neu_pos": pos, "regel": regel, "vergleichsform": vergleich,
                       "vergleich_belege": "%d von %d" % (treffer, sum(belege.values())),
                       "ziel_lemma_form": lemmaform, "begruendung": grund, "umfeld": umfeld[xid]})

    geschrieben = n_vnd = 0
    for z in zeilen:
        if z["action"] != "ANNOTATE":
            continue
        m = re.search(W_TEMPLATE.format(xid=re.escape(z["xml_id"])), text)
        if not m:
            sys.exit("FEHLER: <w xml:id=%s> nicht ohne Attribute gefunden." % z["xml_id"])
        neu = ('<w xml:id="%s" lemmaRef="%s" pos="%s">%s</w>'
               % (z["xml_id"], z["neu_lemmaRef"], z["neu_pos"], m.group("form")))
        text = text[:m.start()] + neu + text[m.end():]
        geschrieben += 1
        n_vnd += z["vergleichsform"] == "vnd"

    n_review = sum(1 for z in zeilen if z["action"] == "REVIEW")
    change = CHANGE_VORLAGE.format(datum="2026-10-07", n_breve=geschrieben - n_vnd, n_vnd=n_vnd,
                                   r=n_review, log=repo_relativ(args.out_dir))
    if change in text:
        sys.exit("FEHLER: der revisionDesc-Eintrag steht schon in der Datei.")
    if "</revisionDesc>" not in text:
        sys.exit("FEHLER: kein </revisionDesc> in %s" % DATEI.name)
    letzte = text.rfind("<change ", 0, text.index("</revisionDesc>"))
    if letzte < 0:
        sys.exit("FEHLER: kein vorhandener <change> in %s" % DATEI.name)
    zeilenanfang = text.rfind("\n", 0, letzte) + 1
    einzug = text[zeilenanfang:letzte]
    zeilenende = text.index("\n", letzte) + 1
    umbruch = "\r\n" if text[zeilenende - 2:zeilenende] == "\r\n" else "\n"
    text = text[:zeilenende] + einzug + change + umbruch + text[zeilenende:]

    if args.apply:
        DATEI.write_text(text, encoding="utf-8", newline="")

    out = pfad(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "diff-liste.csv", "w", encoding="utf-8-sig", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(zeilen[0].keys()), delimiter=";")
        wr.writeheader()
        wr.writerows(zeilen)

    modus = "APPLY" if args.apply else "DRY-RUN"
    print("[%s] Ziel-Tokens: %d (%d Breve w/n + %d vnd)"
          % (modus, len(zeilen), len(zeilen) - sum(1 for z in zeilen if nfc(z["form"]).lower() == "vnd"),
             sum(1 for z in zeilen if nfc(z["form"]).lower() == "vnd")))
    print("  ANNOTATE: %d (%d Breve + %d vnd), REVIEW: %d"
          % (geschrieben, geschrieben - n_vnd, n_vnd, n_review))
    print("  Lemmata:", dict(Counter(z["ziel_lemma_form"] + " " + z["neu_pos"]
                                     for z in zeilen if z["action"] == "ANNOTATE")))
    for z in zeilen:
        print("  %-16s %-18s %-8s %-12s %-4s %-10s %s" % (z["xml_id"], z["form"], z["action"],
              z["neu_lemmaRef"].replace("lexicon.xml#", ""), z["neu_pos"], z["vergleich_belege"][:10],
              z["umfeld"]))
    print("  Artefakte:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
