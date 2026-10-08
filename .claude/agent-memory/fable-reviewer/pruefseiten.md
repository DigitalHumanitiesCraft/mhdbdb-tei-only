---
name: pruefseiten
description: Prüfseiten-Generatoren im Review (review_page.py, build-359-page.py, build-review-364/klaus, Archiv #469): was das Gate nicht sieht, markup vs. e(), Laufzeiten, datengebundene Specs
metadata:
  type: project
---
Verdichtet 02.10.2026.

**review_page.py / build-359-page.py (#359, #443)**
- Zitat-Gate `zitate_pruefen` liest nur `begruendung`; `kurz`, `nebenbefund`, `stichprobe`, `vorschlag.*` tragen auch Backtick-Zitate und laufen ungeprüft.
- `kurz`, `vorschlag.text`, `unsicherheit`, `beleg_hinweis` gehen über `e()`, nicht `markup()`: Backticks roh im HTML. Welche Felder ausgezeichnet werden, entscheiden die `markup()`-Aufrufe im Generator; `HTML_FELDER` ist nur die Deklaration, die das Gate liest (`_pruefe_textfelder` ist für den Inhalt tautologisch). Wechselt ein Feld von `e()` auf `markup()`: in `render()` nach seiner Textkopie in DATEN suchen (JSON-Export, Bericht).
- `zeilen_karte` schlüsselt nach `id(w)` und hält nur, weil `ws = list(body.iter(w))` die Proxies lebendig hält. `exportDaten()` schreibt alle Fälle: „Eingelesen: N" ist beim eigenen Export immer die Gesamtzahl. Kontextfenster sind Tokens (w+pc), nicht Wörter.
- Proben: `render` per `inspect.getsource` + replace + `exec` mutieren; Seite bitidentisch regenerieren (ZIEL auf $TEMP). BELEGE aus dem HTML: `re.search(r'const BELEGE = (\[.*?\]);\n', html, re.S)` + json gegen `faelle.csv` (`;`).

**Archivierte Beispiele (#469)**
- `build-review-364.py` braucht >10 min und 1,6 GB: nur im Hintergrund mit Logdatei. Beide Generatoren brechen per assert ab, wenn der Issue-Umfang nicht mehr 35/66/29 (364) bzw. 39/264/22 (Klaus) ist.
- Der eingebettete Commit 6e36a659 existiert nicht im Repo (KZWs lokaler Stand); Regeneration bettet HEAD und heutiges Datum ein. `build-review-klaus.py` liest die 364-Vorlage nur für den `<style>`-Block; Vorlage gegen Archiv: difflib zeilenweise ohne die Zeile mit `id="review-data"`.

**build-526-pruefseite.py (#526 Punkt 4, Runde 1 am 08.10.2026)**
- Probe ohne Worktree-Berührung: Quelltext lesen, `ROOT = Path(__file__)...` und `sys.path.insert(...)` auf den Worktree-Pfad, `ZIEL` auf das Scratchpad ersetzen, `exec` unter `__name__ == '__main__'`; Seite war bytegleich zum Commit. Der `print` am Ende wirft `ValueError` an `ZIEL.relative_to(ROOT)`, die Datei ist da schon geschrieben: diese Exception heißt „durchgelaufen", nicht „Gate".
- `pruefe_kandidaten()` prüft nur `orth`, nicht die Wortart: `('lemma_2816','höuwe','VRB')` läuft durch. Eigene `markup()`-Variante mit `*kursiv*`: ungerade Sternzahl kursiviert den Rest still (`sich * freuen` -> `sich <i> freuen.</i>`); Formen und Umfeld gehen durch `e()`, nicht `markup()`, also kein Risiko aus der CSV.
- `fundstelle()` schrieb „Wort N" mit dem Suffix der xml:id; das zaehlt `<w>` und `<pc>` ab 0 und ist keine Wortnummer (seit Runde 3 weggelassen). Dieselbe Zeile steht noch in `build-370-pruefseite.py:63`. Kandidaten-Begründungen tragen „…" (19 Paare), `pruefseite-370.html` 0, `359-pruefseite.html` 3; kein Gate, Scope-Frage #440 weiter offen.
- WZB-Präzedenz für Superlative von min/minner: 9 annotierte Tokens (minsten ×4, minneste ×2, minnesten ×3; Runde 1 nannte 8), alle lemma_4134 ADV sense_6491, auch attributiv; „minster" selbst 2× unannotiert daneben. `hewes` steht nicht in variants.xml; WZB annotiert heu/hŏue -> lemma_2816, howe -> lemma_9644 (houwe, Haue).

**Anführungszeichen und Scope (#440):** Prüfseiten unter `ingest/` sind ausgelieferte Seiten; ob sie im Geltungsbereich sind, vorher klären. Generatoren emittieren eigene Strings. Kommentar vs. Code in JS: eigener Zeichenscanner (kein Parser verfügbar). **Widerspruch im Bestand:** `docs/playbooks/kickoffs/2026-09-21-kickoff-spur-b-pruefseite.md:92` schreibt U+201C vor, gegen die Entscheidung für gerade Zeichen.
