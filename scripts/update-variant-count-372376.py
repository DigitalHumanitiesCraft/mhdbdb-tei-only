"""Zieht die dokumentierte Formenzahl von variants.xml auf 256.773 nach.

Anlass: #375 praegt type_372376 fuer die Schreibung waeren unter lemma_7338.
Damit steigt die Zahl der Formen in variants.xml um eins, und sie steht an
zehn Stellen, drei davon auf ausgelieferten Seiten. scripts/audit/doc-count-
audit.py --check meldet die Drift und faerbt data-integrity.yml rot.

NICHT mitgezogen wird 234.245, die Zahl der normalisierten Mappings: die neue
Schreibung normalisiert auf eine Form, die es dort schon gab. Die beiden Zahlen
messen Verschiedenes, CONTRACTS.md Paragraf C sagt das ausdruecklich.

Gibt je Ersetzung die Trefferzahl aus und bricht ab, wenn eine nicht so oft
greift wie erwartet.
"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = "C:/Users/chstn/Desktop/data/DHCraft/Projekte/Git/mhdbdb-tei-only"
fehler = []


def ersetze(relpfad, alt, neu, erwartet, etikett):
    pfad = os.path.join(REPO, relpfad)
    with open(pfad, encoding="utf-8", newline="") as f:
        inhalt = f.read()
    n = inhalt.count(alt)
    print(f"  {'ok ' if n == erwartet else 'FEHLER'} {relpfad:32s} "
          f"{etikett:26s} Treffer {n}, erwartet {erwartet}")
    if n != erwartet:
        fehler.append(f"{relpfad} / {etikett}: {n} statt {erwartet}")
        return
    with open(pfad, "w", encoding="utf-8", newline="") as f:
        f.write(inhalt.replace(alt, neu))


print("Englische Doku (Komma als Tausendertrenner)")
ersetze("docs/TEI-MODEL.md", "256,772", "256,773", 1, "Tabelle")
ersetze("docs/DATA-MODEL.md", "256,772", "256,773", 1, "Ueberschrift")
ersetze("docs/TEI-MODEL-AUTH-FILES.md", "256,772", "256,773", 2, "Tabelle + Prosa")
ersetze("docs/CONTRACTS.md", "256,772", "256,773", 2, "Paragraf C, zweimal")

print("\nDeutsche Seiten und README (Punkt als Tausendertrenner)")
ersetze("schema/README.md", "256.772", "256.773", 1, "Tabelle")
ersetze("index.html", "256.772", "256.773", 1, "Kennzahlenblock")
ersetze("hilfe-daten.html", "256.772", "256.773", 2, "Prosa + Kennzahl")

print("\nDaten in der Nachbarschaft, die mitwachsen")
ersetze("docs/TEI-MODEL-AUTH-FILES.md",
        "(most recently 256,773 forms, 2026-09-10 with #363)",
        "(most recently 256,773 forms, 2026-09-14 with #375)", 1,
        "Regenerierungsdatum")
ersetze("docs/CONTRACTS.md",
        "- 234,245 normalized entries (as of 2026-09-10; 256,773 raw forms",
        "- 234,245 normalized entries (as of 2026-09-14; 256,773 raw forms", 1,
        "Stichtag Paragraf C")

print("\n" + "=" * 72)
if fehler:
    print("ABGEBROCHEN:")
    for f in fehler:
        print("   ", f)
    sys.exit(1)
print("Alle neun Ersetzungen haben wie erwartet gegriffen.")
