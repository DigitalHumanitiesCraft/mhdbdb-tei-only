---
name: naming-pin-420-v030
description: Review des Naming-Pins auf v0.3.0-beta (#420, 23.09.2026): Share-Summen-Zahlen haengen an der Rundung (JS Math.round vs. Python round), Lindas Bereinigungscommit ist vom 09.09., Messrezept alt/neu-Index
metadata:
  type: project
---

Die Share-Spalte in `computeFigureRows` rundet mit `Math.round` (halb nach oben). Die Zahlen "433 Lemmata mit >=2 Figuren, 247 exakt 100, Spanne 89 bis 109" (naming-explorer.js ~:472, FEATURES.md ~:319, "Reviewbefund B2") reproduzieren sich NUR mit Pythons `round()` (Banker); mit JS-Rundung sind es 433 / **244** / **91 bis 121** (Ausreisser TRO `wërt` 200 Nennungen auf 58 Figuren: JS 121, Python 89). ROL helt 98 und hêrre 95 sind in beiden Rundungen gleich, deshalb fiel es nie auf.

**Why:** Eine Zahl, die das Modul beschreibt, muss mit der Rundung des Moduls gemessen sein; eine Python-Nachrechnung mit `round()` beschreibt ein anderes Programm. Am 23.09.2026 in Runde 1 zu #420 gemessen (`temp/mess_share_420.py`, Varianten js/banker/trunc nebeneinander).

**How to apply:** Bei jeder Prozent- oder Anteilszahl aus dem Frontend die Rundungsfunktion des JS nachbauen (`math.floor(x + 0.5)`), nie `round()`. Alt/neu-Index vergleichen: `git show <basis>:data/naming-index.json.gz > temp/naming-old.json.gz` (relativer Pfad, sonst lehnt der Worktree-Guard ab), Records als (sigle, figur, vers, json) flach diffen.

Weitere Messwerte dieser Runde: Lindas Attributionsbereinigung ist Commit af531d30 vom **09.09.2026** (categorization_Iwein.json 5 Zeilen, Rolandslied 15, Trojanerkrieg 1; die TRO-Aenderung laesst den Index unveraendert), nicht 10.09.; Tag v0.3.0-beta = master = 8076467a; CITATION.cff traegt den Concept-DOI 21914259. Der Index enthaelt in keinem String "term" (case-insensitiv, alle 4 Werke), `not.toContainText('Term')` ist gegen die Daten damit nicht fragil. api.github.com und raw.githubusercontent.com am Laptop ohne Token erreichbar (compare/commits-Endpunkte liefern Dateilisten mit Datum).
