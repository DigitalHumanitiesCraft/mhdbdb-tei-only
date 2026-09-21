"""Zieht die dokumentierten Variantenzahlen auf den Stand nach #366/#375/#371.

Anlass: der Lauf vom 21.09.2026 praegt zehn Typen (type_372377 bis type_372386).
Damit steigen ZWEI Zahlen, und das ist der Unterschied zum Vorgaengerskript
update-variant-count-372376.py:

  Formen in variants.xml                     256.773 -> 256.783   (+10)
  normalisierte Mappings im Laufzeit-Dict    234.245 -> 234.250   (+5)

Beim vorigen Zug (#375, eine einzige neue Schreibung) blieb die zweite Zahl
stehen, weil die neue Form auf eine schon vorhandene normalisierte Form fiel.
Diesmal nicht: fuenf der zehn neuen Rohformen normalisieren auf etwas, das im
Woerterbuch noch nicht steht. Gemessen, nicht angenommen:

  Formen:   len(set(f.get(xml:id) for f in variants.xml//form))  -> 256.783
  Mappings: len(json.load(gzip.open('data/authority-index.json.gz'))['variants'])
                                                                 -> 234.250

Die beiden Zahlen messen weiterhin Verschiedenes, CONTRACTS.md Paragraf C sagt
das ausdruecklich. Sie werden hier nur deshalb zusammen gezogen, weil sie in
denselben zwei Saetzen stehen und ein gemeinsames Datum tragen: eine allein zu
ziehen macht genau den Satz falsch, der vor ihrer Verwechslung warnt.

NICHT mitgezogen werden drei Sorten von Vorkommen:

  1. docs/JOURNAL.md. Ein Journaleintrag ist ein Datum mit einer Zahl daran.
  2. scripts/update-variant-count-372376.py. Das Skript des vorigen Zugs
     dokumentiert seinen eigenen Stand.
  3. Die historischen Werte in docs/CONTRACTS.md und docs/DECISIONS.md, die
     ausdruecklich einen frueheren Indexstand benennen (234.244 als Stand von
     v1.6.2; der Vergleich 1.9.5 gegen 1.9.6). Welche davon in dieser Datei
     stehen und welche nicht, steht unten bei der jeweiligen Ersetzung.

Gibt je Ersetzung die Trefferzahl aus und bricht ab, wenn eine nicht so oft
greift wie erwartet.
"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fehler = []


def ersetze(relpfad, alt, neu, erwartet, etikett):
    pfad = os.path.join(REPO, relpfad)
    with open(pfad, encoding="utf-8", newline="") as f:
        inhalt = f.read()
    n = inhalt.count(alt)
    print(f"  {'ok ' if n == erwartet else 'FEHLER'} {relpfad:34s} "
          f"{etikett:30s} Treffer {n}, erwartet {erwartet}")
    if n != erwartet:
        fehler.append(f"{relpfad} / {etikett}: {n} statt {erwartet}")
        return
    with open(pfad, "w", encoding="utf-8", newline="") as f:
        f.write(inhalt.replace(alt, neu))


print("Formenzahl, englische Doku (Komma als Tausendertrenner)")
ersetze("docs/TEI-MODEL.md", "256,773", "256,783", 1, "Tabelle")
ersetze("docs/DATA-MODEL.md", "256,773", "256,783", 1, "Ueberschrift")
ersetze("docs/TEI-MODEL-AUTH-FILES.md", "256,773", "256,783", 2, "Tabelle + Prosa")
ersetze("docs/CONTRACTS.md", "256,773", "256,783", 2, "Paragraf C, zweimal")

print("\nFormenzahl, deutsche Seiten und README (Punkt als Tausendertrenner)")
ersetze("schema/README.md", "256.773", "256.783", 1, "Tabelle")
ersetze("index.html", "256.773", "256.783", 1, "Kennzahlenblock")
ersetze("hilfe-daten.html", "256.773", "256.783", 2, "Prosa + Kennzahl")

print("\nMappingzahl, dort wo sie einen Ist-Stand nennt")
# Paragraf C: beide Zahlen in einem Satz, mit gemeinsamem Stichtag. Die
# Reihenfolge ist hier nicht beliebig: erst die Zahl, dann der Stichtag, denn
# der Stichtag-Anker enthaelt die schon gezogene Zahl.
ersetze("docs/CONTRACTS.md",
        "234,245 the count of mappings",
        "234,250 the count of mappings", 1,
        "Paragraf C, Warnsatz")
ersetze("docs/CONTRACTS.md",
        "- 234,245 normalized entries",
        "- 234,250 normalized entries", 1,
        "Paragraf C, Eintragszahl")
ersetze("docs/CONTRACTS.md",
        "- 234,250 normalized entries (as of 2026-09-14; 256,783 raw forms",
        "- 234,250 normalized entries (as of 2026-09-21; 256,783 raw forms", 1,
        "Paragraf C, Stichtag")
# Zeile 99: zwei Zahlen mit verschiedenen Rollen. 234.244 ist der Stand von
# v1.6.2 und bleibt; nur das nachgestellte "today" wird gezogen. Der ganze
# Satz existiert, um die Differenz als echten Datenschritt zu erklaeren (#277).
ersetze("docs/CONTRACTS.md",
        "(today 234,245, see §C)",
        "(today 234,250, see §C)", 1,
        "v1.6.2-Satz, nur das today")
ersetze("docs/DATA-MODEL.md",
        "// ... 234,245 mappings (2026-09-10)",
        "// ... 234,250 mappings (2026-09-21)", 1,
        "Schema-Kommentar")
ersetze("hilfe-daten.html", "234.245", "234.250", 1, "Prosa")

print("\nMappingzahl auf den ausgelieferten Seiten (Punkt als Tausendertrenner)")
ersetze("hilfe-korpussuche.html", "234.245", "234.250", 1, "Stufenliste")
ersetze("hilfe-playground.html", "234.245", "234.250", 1, "Prosa")
ersetze("playground/index.html", "234.245", "234.250", 1, "Suchhilfe")

print("\ndocs/DECISIONS.md: eine Ist-Angabe ziehen, eine historische kennzeichnen")
# Zeile 1256 sagt "so the three counts above describe a slightly smaller set
# than today's", ist also eine Aussage ueber heute und zieht mit. Die 234.243
# zwei Saetze davor bleibt: sie ist der Messstand von #378 und traegt sein Datum.
ersetze("docs/DECISIONS.md",
        "the dictionary has since grown to **234,245** mappings "
        "(measured against Authority Index 1.9.6 on 2026-09-14)",
        "the dictionary has since grown to **234,250** mappings "
        "(measured against Authority Index 1.9.8 on 2026-09-21)", 1,
        "ADR-Ist-Angabe")
# Zeile 1288 vergleicht zwei benannte Indexstaende: 1.9.5 gegen 1.9.6 hatten
# beide 234.245. Die Zahl hochzuziehen waere eine Falschaussage ueber eine
# dokumentierte Messung. Stattdessen der nachgestellte Stand-von-Version-
# Vermerk, den find_stale_numbers dafuer kennt (Zeile 704 dort, #297).
ersetze("docs/DECISIONS.md",
        "out of 234,245 mappings on both sides.",
        "out of 234,245 mappings on both sides, which is the state of v1.9.6 "
        "and not today's.", 1,
        "historischer Vergleich, markiert")

print("\nDaten in der Nachbarschaft, die mitwachsen")
ersetze("docs/TEI-MODEL-AUTH-FILES.md",
        "(most recently 256,783 forms, 2026-09-14 with #375)",
        "(most recently 256,783 forms, 2026-09-21 with #366/#375/#371)", 1,
        "Regenerierungsdatum")

print("\n" + "=" * 78)
if fehler:
    print("ABGEBROCHEN:")
    for f in fehler:
        print("   ", f)
    sys.exit(1)
print("Alle Ersetzungen haben wie erwartet gegriffen.")
print("Formen 256.773 -> 256.783, Mappings 234.245 -> 234.250")
