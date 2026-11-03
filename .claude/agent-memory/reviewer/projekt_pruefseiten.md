---
name: projekt-pruefseiten
description: Prüfseiten-Generatoren im Review (review_page.py, build-359-page.py, build-review-364/klaus, build-370- und build-526-pruefseite.py): was das Gate nicht sieht, markup gegen e(), Proben ohne Schreiben, Laufzeiten, ein markierter Widerspruch im Bestand
metadata:
  type: project
---
Verdichtet 03.11.2026.

**review_page.py / build-359-page.py (#359, #443)**
- Das Zitat-Gate `zitate_pruefen` liest nur `begruendung`. `kurz`, `nebenbefund`, `stichprobe`, `vorschlag.*` tragen auch Backtick-Zitate und laufen ungeprüft.
- `kurz`, `vorschlag.text`, `unsicherheit`, `beleg_hinweis` gehen über `e()`, nicht `markup()`: Backticks roh im HTML. Welche Felder ausgezeichnet werden, entscheiden die `markup()`-Aufrufe im Generator, `HTML_FELDER` ist nur die Deklaration, die das Gate liest. Wechselt ein Feld auf `markup()`: in `render()` nach seiner Textkopie in DATEN suchen (JSON-Export, Bericht).
- `collect-359-evidence.py` ohne `--write` nachfahren: Quelltext je Rev per `git show` ins Scratch, importlib, `REPO/AUTH_INDEX/OUT_DIR/CROSSCHECK` umsetzen, `lade_faelle()` und `scan()` beider Fassungen auf demselben Korpus vergleichen. Das trennt Diff-Wirkung von Eingangsdrift.
- Einziger `kontextart`-Leser ist `fundstelle()`, sie bricht bei unbekannter `kontextart` ab, aber nur für gezeigte Belege und nicht unter `--pruefen` (kehrt vor `bau_fall` zurück). WZB-Belege stehen nicht auf der Seite (ANZEIGE_CAP). Die 359-Seite hat kein CI-Gate.
- Proben: `render` per `inspect.getsource` + replace + `exec` mutieren, Seite bitidentisch regenerieren (ZIEL nach Temp). BELEGE aus dem HTML: `re.search(r'const BELEGE = (\[.*?\]);\n', html, re.S)` plus json gegen `faelle.csv` (`;`).

**Archivierte Beispiele (#469):** `build-review-364.py` braucht >10 min und 1,6 GB: nur im Hintergrund mit Logdatei. Beide Generatoren brechen per assert ab, wenn der Issue-Umfang nicht mehr stimmt. Regeneration bettet HEAD und heutiges Datum ein, Specs können datengebunden sein. Vorlage gegen Archiv: difflib zeilenweise ohne die Zeile mit `id="review-data"`.

**build-526-pruefseite.py und build-370-pruefseite.py**
- 526-Probe ohne Worktree-Berührung: Quelltext lesen, `ROOT`/`sys.path` auf den Worktree, `ZIEL` ins Scratch ersetzen, `exec` unter `__name__ == '__main__'`. Der `print` am Ende wirft `ValueError` an `ZIEL.relative_to(ROOT)`, die Datei ist da schon geschrieben: diese Exception heißt „durchgelaufen", nicht „Gate".
- `pruefe_kandidaten()` prüft nur `orth`, nicht die Wortart. `fundstelle()` schrieb „Wort N" mit dem Suffix der xml:id (zählt `<w>` und `<pc>`), dieselbe Zeile steht in `build-370-pruefseite.py`. Dort verlangt `fundstelle()` außerdem `WZB_x_n_n$`, Split-Token-IDs (`WZB_165vb_33_1b`) lassen sie abbrechen.

**Anführungszeichen und Scope (#440):** Prüfseiten unter `ingest/` sind ausgelieferte Seiten, den Geltungsbereich vorher klären. **Widerspruch im Bestand, nicht entschieden:** `docs/playbooks/kickoffs/2026-09-21-kickoff-spur-b-pruefseite.md:92` schreibt U+201C vor, gegen die Entscheidung für gerade Zeichen.
