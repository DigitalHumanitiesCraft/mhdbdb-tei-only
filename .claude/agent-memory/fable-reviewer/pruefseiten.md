---
name: pruefseiten
description: Pruefseiten-Generatoren im Review (review_page.py, build-359-page.py, build-review-364/klaus, Archiv #469): was das Gate nicht sieht, markup vs. e(), Laufzeiten, datengebundene Specs
metadata:
  type: project
---
Stand 28.09.2026.

**review_page.py / build-359-page.py (#359, #443)**
- Zitat-Gate `zitate_pruefen` liest nur `begruendung`; `kurz`, `nebenbefund`, `stichprobe`, `vorschlag.*` tragen auch Backtick-Zitate und laufen ungeprueft.
- `kurz`, `vorschlag.text`, `unsicherheit`, `beleg_hinweis` gehen ueber `e()`, nicht `markup()`: Backticks roh im HTML.
- Welche Felder ausgezeichnet werden, entscheiden die `markup()`-Aufrufe im Generator; `HTML_FELDER` ist nur die Deklaration, die das Gate liest. Der Vergleich in `_pruefe_textfelder` ist fuer den Inhalt tautologisch.
- Wechselt ein Feld von `e()` auf `markup()`: in `render()` nach seiner Textkopie in DATEN suchen (landet im JSON-Export und im Bericht).
- `zeilen_karte` schluesselt nach `id(w)` und haelt nur, weil `ws = list(body.iter(w))` vorher die Proxies lebendig haelt.
- `exportDaten()` schreibt alle Faelle: „Eingelesen: N" ist beim eigenen Export immer die Gesamtzahl.
- Proben: `render` per `inspect.getsource` + replace + `exec` mutieren; Seite bitidentisch regenerieren (ZIEL auf $TEMP).
- BELEGE aus dem HTML: `re.search(r'const BELEGE = (\[.*?\]);\n', html, re.S)` + json gegen `faelle.csv` (`;`).
- Kontextfenster sind Tokens (w+pc), nicht Woerter.

**Archivierte Beispiele (#469)**
- `build-review-364.py` braucht >10 min und 1,6 GB: nur im Hintergrund mit Logdatei.
- Beide Generatoren brechen per assert ab, wenn der Issue-Umfang nicht mehr 35/66/29 (364) bzw. 39/264/22 (Klaus) ist.
- Eingebetteter Commit 6e36a659 existiert nicht im Repo (KZWs lokaler Stand); Regeneration bettet HEAD und heutiges Datum ein.
- `build-review-klaus.py` liest die 364-Vorlage nur fuer den `<style>`-Block. Vorlage gegen Archiv: difflib zeilenweise ohne die Zeile mit `id="review-data"`.

**Anfuehrungszeichen und Scope (#440)**
- Pruefseiten unter `ingest/` sind ausgelieferte Seiten; ob sie im Geltungsbereich sind, vorher klaeren. Generatoren emittieren eigene Strings (z.B. build-359-page.py), nicht nur Daten.
- Kommentar vs. Code in JS: eigener Zeichenscanner (kein Parser verfuegbar).
- Widerspruch im Bestand: `docs/playbooks/kickoffs/2026-09-21-kickoff-spur-b-pruefseite.md:92` schreibt U+201C vor, gegen die Entscheidung fuer gerade Zeichen.
