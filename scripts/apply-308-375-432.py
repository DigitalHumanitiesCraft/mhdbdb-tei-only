"""Setzt die drei am 2026-09-14 von @wachauer entschiedenen Korrekturen um.

  #432  WH_6214_3: das Zahlwort zehen wird die Zehe (lemma_9653).
  #375  acht eindeutige waeren-Belege: Verb wesen -> Adjektiv waer.
  #308  Namensansetzung HHP und SJW, VOR-@ref, WZB-@ref-Kurzform, LUU-Whitespace.

Arbeitet textuell auf den Dateien, nicht ueber einen Parse-Baum: eine
lxml-Neuserialisierung wuerde alle Bytes anfassen und die Diffs unlesbar machen
(dieselbe Begruendung wie in scripts/sync/sync_tei_headers.py).

Gibt je Ersetzung die Trefferzahl aus und BRICHT AB, wenn eine Ersetzung nicht
genau einmal greift. Ohne diese Bedingung tut das Skript still nichts und
meldet Erfolg.
"""
import io, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = "C:/Users/chstn/Desktop/data/DHCraft/Projekte/Git/mhdbdb-tei-only"

fehler = []
angefasst = {}


def ersetze(relpfad, alt, neu, erwartet=1, etikett=""):
    """Ersetzt alt durch neu und prueft die Trefferzahl."""
    pfad = os.path.join(REPO, relpfad)
    with open(pfad, encoding="utf-8", newline="") as f:
        inhalt = f.read()
    n = inhalt.count(alt)
    status = "ok " if n == erwartet else "FEHLER"
    print(f"  {status} {relpfad:32s} {etikett:28s} Treffer {n}, erwartet {erwartet}")
    if n != erwartet:
        fehler.append(f"{relpfad} / {etikett}: {n} statt {erwartet}")
        return
    with open(pfad, "w", encoding="utf-8", newline="") as f:
        f.write(inhalt.replace(alt, neu))
    angefasst[relpfad] = angefasst.get(relpfad, 0) + n


# ---------------------------------------------------------------- #432
print("\n#432  WH_6214_3: zehen (Zahlwort) -> zehe (Koerperteil)")
ersetze(
    "tei/WH.tei.xml",
    '<w xml:id="WH_6214_3" lemmaRef="lexicon.xml#lemma_7779" pos="NUM" '
    'ana="lexicon.xml#lemma_7779_sense_12748" corresp="variants.xml#type_28147">zehen</w>',
    '<w xml:id="WH_6214_3" lemmaRef="lexicon.xml#lemma_9653" pos="NOM" '
    'ana="lexicon.xml#lemma_9653_sense_15632" corresp="variants.xml#type_278700">zehen</w>',
    etikett="Wh. 62,14",
)

# ---------------------------------------------------------------- #375
# Zieltypen unter lemma_7338 (waer, ADJ):
#   waeren -> neu zu praegen, siehe unten
#   wâren  -> type_287014
#   woren  -> type_372364
NEUER_TYP_WAEREN = "type_372376"   # Maximum in variants.xml war 372375

print("\n#375  acht eindeutige Faelle: lemma_7505 wesen VRB -> lemma_7338 waer ADJ")
DREISSIG = [
    # (Sigle, Wort-ID, Quelltyp am Token, Zieltyp unter lemma_7338, Form)
    ("SL",  "SL_851_3",       "type_273599", NEUER_TYP_WAEREN, "waeren"),
    ("SL",  "SL_2648_4",      "type_273621", "type_287014",    "wâren"),
    ("SL",  "SL_3945_4",      "type_273621", "type_287014",    "wâren"),
    ("PRT", "PRT_20337_5",    "type_273621", "type_287014",    "wâren"),
    ("NAR", "NAR_9801800_5",  "type_273713", "type_372364",    "woren"),
    ("TSY", "TSY_3928_2",     "type_273621", "type_287014",    "wâren"),
    ("URS", "URS_11800_2",    "type_273621", "type_287014",    "wâren"),
    ("MSG", "MSG_21611030_3", "type_273713", "type_372364",    "woren"),
]
for sigle, wid, quelltyp, zieltyp, form in DREISSIG:
    ersetze(
        f"tei/{sigle}.tei.xml",
        f'<w xml:id="{wid}" lemmaRef="lexicon.xml#lemma_7505" pos="VRB" '
        f'corresp="variants.xml#{quelltyp}">{form}</w>',
        f'<w xml:id="{wid}" lemmaRef="lexicon.xml#lemma_7338" pos="ADJ" '
        f'corresp="variants.xml#{zieltyp}">{form}</w>',
        etikett=wid,
    )

# ---------------------------------------------------------------- #308
print("\n#308  Autorangaben")

# 1. VOR: toter @ref auf die existierende Person
ersetze("tei/VOR.tei.xml",
        '<author ref="#person_schweizer_anonymus">',
        '<author ref="#person_1772">',
        etikett="VOR toter @ref")

# 2. WZB: Langform auf die in tei/ durchgehaltene Kurzform
ersetze("tei/WZB.tei.xml",
        '<author ref="persons.xml#person_anonym">',
        '<author ref="#person_anonym">',
        etikett="WZB @ref-Kurzform")

# 3. HHP: TEI-Header folgt der preferred-Form
ersetze("tei/HHP.tei.xml",
        '<author ref="#person_1050">Heinrich von Breslau</author>',
        '<author ref="#person_1050">Heinrich von Pressela</author>',
        etikett="HHP titleStmt")
ersetze("authority-files/works.xml",
        '<author ref="persons.xml#person_1050">Heinrich von Breslau</author>',
        '<author ref="persons.xml#person_1050">Heinrich von Pressela</author>',
        etikett="HHP works.xml")

# 4. persons.xml: die beiden alternativen Namensformen
#    HHP: Breslau ergaenzen; SJW: preferred wird Warte, Wart wird alternative.
ersetze("authority-files/persons.xml",
        '<persName type="preferred">Heinrich von Pressela</persName>',
        '<persName type="preferred">Heinrich von Pressela</persName>\n'
        '      <persName type="alternative">Heinrich von Breslau</persName>',
        etikett="person_1050 alternative")
ersetze("authority-files/persons.xml",
        '<persName type="preferred">Jakob von Wart</persName>',
        '<persName type="preferred">Jakob von Warte</persName>\n'
        '      <persName type="alternative">Jakob von Wart</persName>',
        etikett="person_1249 preferred+alt")

# 5. LUU: Zeilenumbruch samt Einrueckung im Autornamen
ersetze("tei/LUU.tei.xml",
        '<author ref="#person_1771">Albertanus von\n            Brescia</author>',
        '<author ref="#person_1771">Albertanus von Brescia</author>',
        etikett="LUU Whitespace")

print("\n" + "=" * 78)
if fehler:
    print("ABGEBROCHEN, nichts ist vollstaendig:")
    for f in fehler:
        print("   ", f)
    sys.exit(1)
print("Alle Ersetzungen haben genau einmal gegriffen.")
print("Angefasste Dateien:")
for k, v in sorted(angefasst.items()):
    print(f"   {k:34s} {v}")
print(f"\nNeuer Variantentyp fuer 'waeren' unter lemma_7338: {NEUER_TYP_WAEREN}")
print("Er entsteht beim naechsten extract-variants.py-Lauf NICHT von selbst:")
print("variants.xml wird aus dem Korpus regeneriert, der Typ muss also im")
print("Korpus stehen (steht er jetzt) und die Datei wird danach neu gebaut.")
