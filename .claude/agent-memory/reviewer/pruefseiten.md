---
name: pruefseiten
description: Prüfseiten-Generatoren im Review (review_page.py, build-359-page.py, build-review-364/klaus, Archiv #469, build-526-pruefseite.py): was das Gate nicht sieht, markup vs. e(), Laufzeiten, datengebundene Specs
metadata:
  type: project
---
Verdichtet 08.10.2026.

**review_page.py / build-359-page.py (#359, #443)**
- Zitat-Gate `zitate_pruefen` liest nur `begruendung`; `kurz`, `nebenbefund`, `stichprobe`, `vorschlag.*` tragen auch Backtick-Zitate und laufen ungeprüft.
- `kurz`, `vorschlag.text`, `unsicherheit`, `beleg_hinweis` gehen über `e()`, nicht `markup()`: Backticks roh im HTML. Welche Felder ausgezeichnet werden, entscheiden die `markup()`-Aufrufe im Generator; `HTML_FELDER` ist nur die Deklaration, die das Gate liest (`_pruefe_textfelder` ist für den Inhalt tautologisch). Wechselt ein Feld von `e()` auf `markup()`: in `render()` nach seiner Textkopie in DATEN suchen (JSON-Export, Bericht).
- `zeilen_karte` schlüsselt nach `id(w)` und hält nur, weil `ws = list(body.iter(w))` die Proxies lebendig hält. `exportDaten()` schreibt alle Fälle: „Eingelesen: N" ist beim eigenen Export immer die Gesamtzahl. Kontextfenster sind Tokens (w+pc), nicht Wörter.
- Proben: `render` per `inspect.getsource` + replace + `exec` mutieren; Seite bitidentisch regenerieren (ZIEL auf $TEMP). BELEGE aus dem HTML: `re.search(r'const BELEGE = (\[.*?\]);\n', html, re.S)` + json gegen `faelle.csv` (`;`).

**Archivierte Beispiele (#469)**
- `build-review-364.py` braucht >10 min und 1,6 GB: nur im Hintergrund mit Logdatei. Beide Generatoren brechen per assert ab, wenn der Issue-Umfang nicht mehr stimmt. Regeneration bettet HEAD und heutiges Datum ein; Specs können datengebunden sein, ein neuer Datenstand bricht sie ohne Vorlagenänderung. Vorlage gegen Archiv: difflib zeilenweise ohne die Zeile mit `id="review-data"`.

**build-526-pruefseite.py (#526 Punkt 4)**
- Probe ohne Worktree-Berührung: Quelltext lesen, `ROOT`/`sys.path` auf den Worktree, `ZIEL` ins Scratchpad ersetzen, `exec` unter `__name__ == '__main__'`. Der `print` am Ende wirft `ValueError` an `ZIEL.relative_to(ROOT)`, die Datei ist da schon geschrieben: diese Exception heißt „durchgelaufen“, nicht „Gate“.
- `pruefe_kandidaten()` prüft nur `orth`, nicht die Wortart. `fundstelle()` schrieb „Wort N“ mit dem Suffix der xml:id (zählt `<w>` und `<pc>`, projekt_526_breve_makron); dieselbe Zeile steht noch in `build-370-pruefseite.py`.

**Anführungszeichen und Scope (#440):** Prüfseiten unter `ingest/` sind ausgelieferte Seiten; ob sie im Geltungsbereich sind, vorher klären. Kommentar vs. Code in JS: eigener Zeichenscanner (kein Parser verfügbar). **Widerspruch im Bestand:** `docs/playbooks/kickoffs/2026-09-21-kickoff-spur-b-pruefseite.md:92` schreibt U+201C vor, gegen die Entscheidung für gerade Zeichen.
