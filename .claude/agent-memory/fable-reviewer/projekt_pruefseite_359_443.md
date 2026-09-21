---
name: pruefseite-359-443
description: Review-Lehren zur Pruefseite #359 (Borek) und zum Format review_page.py (#443): wo das Zitat-Gate nicht hinsieht, welche Felder ohne markup() gerendert werden, Korpusfakten (lemmaRef einwertig, WZB-Breve, WZB-<l> ohne @n)
metadata:
  type: project
---

Runde 1 am 21.09.2026, Stand ce15d3f7c gegen origin/main c2e67bf8a.

**Zitat-Gate `zitate_pruefen` liest nur `begruendung`.** `kurz`, `nebenbefund`,
`stichprobe`, `vorschlag.text/unsicherheit` tragen ebenfalls Backtick-Zitate
und laufen ungeprueft durch; `kurz` von `röss|lemma_18728` zitierte so eine
Formel, die in keinem der 5 Belege steht. Nachstellen: Heuhaufen wie im Gate
bauen und `re.findall(r'`([^`]+)`')` ueber die anderen Felder laufen lassen.

**`kurz`, `vorschlag.text`, `unsicherheit`, `beleg_hinweis` gehen ueber `e()`,
nicht ueber `markup()`**: Backticks erscheinen roh im HTML. Messen mit
`Grep '`'` auf der erzeugten Seite (Runde 1: 21 Zeilen, davon 13 `kurz`).

**Why:** Der Generator ist die einzige Stelle, an der ein Fehler in
`vorschlaege.json` auffallen kann; KZW liest die fertige Seite und sieht weder
JSON noch Gate.
**How to apply:** In Folgerunden zuerst die Seite greppen, dann das Gate auf
alle Textfelder nachstellen, dann Zahlen je Fall aus evidence.json (Skript:
tokens_gesamt, texte_gesamt, len(belege), Counter(sigle), Counter(pos)).

Korpusfakten, am 21.09.2026 gemessen:
- `@lemmaRef` ist in `tei/` durchgehend einwertig: `rg -c 'lemmaRef="[^"]*#[^"]*#'` = 0 Dateien, Kontrollwert `lemmaRef="` in ERB 25.372. Die Token-Exaktheit in `lemma_ids()` hat also derzeit keinen Gegenstand, ist aber korrekt gebaut (split + set-Membership).
- WZB hat `<l>` ohne `@n` (11 Belege in evidence.json) und kombinierende Breve (`Ew̆er`): ein flacher Vergleich auf `\w` zerlegt das Wort. `fundstelle()` beschriftet solche Belege als "Prosa, ohne Verszaehlung".
- `zeilen_karte` schluesselt nach `id(w)`; das haelt nur, weil `ws = list(body.iter(w))` VOR `zeilen_karte(body)` angelegt wird und die Proxies am Leben haelt (kontextart vers 870 / prosa 132 gemessen). Reihenfolge nicht vertauschen.
- `exportDaten()` schreibt alle DATEN.faelle; "Eingelesen: N Faelle" ist deshalb bei jedem eigenen Export die Gesamtzahl.

**Runde 2 (Stand 372f88fb6), die #397-Frage traf:** `markup()` auf
`vorschlag.text` wandert ueber `render()` in `DATEN.faelle[].vorschlagText`
(review_page.py, daten=dict(...)) und von dort in den JSON-Export (`vorschlag`)
und den HTML-Bericht (`esc(a.vorschlag)`): Tags als sichtbarer Text. Vor jedem
Feld, das von e() auf markup() wechselt, in `render()` nachsehen, ob es eine
Textkopie in DATEN hat. `HTML_FELDER` nannte `frage`, aber `_fall_html` escapet
`frage` (Probe: `<b>` erscheint als `&lt;b&gt;`). Backticks im alten HTML
(ce15d3f7c) nach Definition: 58 Zeichen / 22 Zeilen gesamt, 52 / 20 sichtbar,
26 Paare; die „21“ der Doku kam aus keiner davon. Werkzeug: Mutationsproben
in-process per importlib gegen build-359-page.py (zitate_pruefen, bau_fall,
spec, render mit _fall_html-Patch), Sekunden statt Dateiaenderung.

**Runde 3 (Stand e647899f4):** `_nur_text(markup(t))` gibt t ohne Backticks/`**`
exakt zurueck (5 Proben, auch `<`, `&`, Quotes), weil markup() zuerst e()
laeuft und _nur_text erst Tags strippt, dann unescaped. Aber `_pruefe_textfelder`
sieht den UNESCAPETEN Wert und lehnt ein literales `<pc>` im Vorschlagstext als
Markup ab (falscher Abbruch, laut, kein Datum in vorschlaege.json traegt `<`:
0 Treffer). Pruefung gehoert an den Zwischenstand vor html.unescape. Sonst
haengt nichts an vorschlagText==vorschlag.text (grep: nur render + exportDaten).
Seite regeneriert in-process bitidentisch (b359.ZIEL auf $TEMP umbiegen,
main() rufen; 304.935 Zeichen). Folgebefund 4 nachgerechnet: 39 Lemmata, 5 ohne
Token, 34 mit Beleg, 4 gegen pos abweichend (jagen INJ 249/250, lenden ADV
44/45, merken INJ 7/7, roese ADJ 3/3), posAll 34/34 mit Kompositumregel, 31 ohne;
Index 43.878 Lemmata. Belege je Lemma nach xml_id dedupliziert und roh: gleich.

**Runde 4 (Stand 9cff369c9):** `_pruefe_textfelder` vergleicht jetzt
DATEN-Feld gegen `_nur_text(spec)`-Ableitung. Der Vergleich ist fuer den
INHALT tautologisch (render und Gate rechnen denselben Ausdruck auf derselben
Quelle); er misst nur Divergenz zwischen render() und der Deklaration
TEXTFELDER_DATEN/HTML_FELDER. Fehlalarm-Proben ueber vorschlag.text-Inhalte
koennen deshalb nie fehlschlagen und messen nichts. Verloren ging die
quellunabhaengige Eigenschaft der alten Regex: `kopf`/`frage` mit markup() im
Generator, aber ohne HTML_FELDER-Eintrag, gehen gruen durch (Probe: kopfText
`<span class="mono">hurt</span>` im JSON, Tag sichtbar in der Karte; alte
Regex haette kopfText gemeldet). Grund: nicht HTML_FELDER entscheidet, was
ausgezeichnet wird, sondern die 7 markup()-Aufrufe in build-359-page.py
(385, 389, 398, 402, 431, 432, 436); HTML_FELDER ist nur die Deklaration, die
das Gate liest. Bei jedem Gate fragen: prueft es den Wert oder nur die
Konsistenz zweier Stellen desselben Autors? Werkzeug: render-Quelltext per
inspect.getsource + str.replace + exec in Modul-Namensraum mutieren, statt
Dateien anzufassen. Seite bitidentisch 308.718 Bytes / 45 Karten.

Umgebung (Laptop, worktree-Sandbox): Befehle mit `python -c "..."` oder
Verbund (`;`, `${PIPESTATUS}`) werden als „git in komplexer Form“ abgelehnt,
weil der Pfad `Projekte/Git/` heisst; Skripte nach `$TEMP` schreiben und mit
`python -X utf8 <datei>` starten (cp1252-Konsole bricht sonst an ł/w̆).

Zahlen der Runde 1 (evidence.json): 45 Faelle = 25 verdacht / 15 klassifikation / 5 koerperteil; Bewertungen 18 annotation_korrekt, 10 aufloesungsartefakt, 5 konzept_fehlt, 5 unsicher, 4 kein_korpusbeleg, 3 annotation_falsch; 28 ohne Entscheidung. lenden|lemma_3702: pos VRB 44 + ADV VRB 1, WZB 7 (alle VRB). huerten|lemma_2903: 7 Tokens, 7 Belege (WUT_3909_1 der ungelesene).
