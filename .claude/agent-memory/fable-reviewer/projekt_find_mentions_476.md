---
name: find-mentions-exit-probe-476
description: In-process-Probe fuer scripts/sync/find-mentions.py main() ohne Netz (Patches, Kandidatenform, Fallen), Exit-Pfade Stand 23.09.2026; Em-Dash-Gate-Artefakt bei Branch aelter als main
metadata:
  type: project
---

Probe fuer alle Exit-Pfade von `find-mentions.py` laeuft in unter 1 s ohne
Netz: Modul per importlib laden, `sys.modules["requests"]` vorher stubben,
dann `fm.zotero_baseline`, `fm.SOURCES` (Tupel mit einer Funktion, `__name__`
setzen, weil main() es druckt) und `fm.zotero_write` ersetzen, `fm.PROBLEME`
zwischen den Faellen leeren, `SystemExit` fangen. candidates.json landet im
cwd, also vorher `os.chdir` ins Scratchpad.

**Falle:** Kandidatentitel muessen paarweise fast disjunkte Wortmengen haben.
Der erste Kandidat geht bei Z. 817 sofort in `eintraege`, und jeder weitere
mit >= 85 % Ueberlappung (oder Teilmenge mit Zweitmerkmal, gleicher Autor
reicht) gilt als bekannt. "MHDBDB Probe Nummer i" ergab 1 statt 45
Kandidaten, weil `woerter()` Kurztokens und Ziffern streicht und `stamm()`
faltet. Loesung: `f"MHDBDB zq{i:02d}ab zq{i:02d}cd zq{i:02d}ef"`.

Gemessen 23.09.2026 (Stand 76965045f): Exit-1-Quellen im Schreibpfad
jenseits von PROBLEME sind drei, nicht zwei: Zotero-Ablehnung (`fehler`),
Kappung (`gekappt`), fehlender ZOTERO_API_KEY (Z. 877). `basis_ok=False`
kommt im echten Lauf immer mit PROBLEME (vier Stellen in
`zotero_baseline()`). Trockenlauf: candidates.json traegt alle Kandidaten,
Exit haengt nur an PROBLEME. Beim Schreiben traegt candidates.json ebenfalls
alle, Zotero bekommt nur MAX_NEU.

**Em-Dash-Gate:** `check-no-em-dash.py --diff-base origin/main` meldet auf
einem Branch, der aelter als main ist, jede Zeile, die main seither geaendert
hat und die im Branch noch einen Em-Dash traegt (schema/README.md:23 am
23.09.). Gegenprobe: `git show <merge-base>:<datei> | awk 'NR==23'` gegen
`origin/main`, und `git diff --stat origin/main...HEAD` muss die Datei nicht
nennen.

**How to apply:** Bei jedem weiteren Vertragssatz zu diesem Skript die Probe
aus dem Scratchpad nachbauen statt Zeilen zu lesen; sie deckt Trockenlauf,
Kappung, Basis, Schluessel und Ablehnung in einem Lauf.
