# Pruefseite #418 (hawe, type_117159), Runden 1 und 2 am 10.09.2026

- Reader-Deep-Link `?verseId=<wort_id>` (app.js:1747, tei-text-reader.js scrollToVerseId) loest nur in
  Verstexten auf: data-core kommt aus `<l>`. Prosatexte (AC2, AC3, CEFB, DES2, KFB: `<l>`=0, nur `<lb>`)
  haben kein data-core. `?verse=<lb n>` ist kein Ersatz: lb@n wiederholt sich je Seite (AC2 1110 lb, 31 n).
  hat_l-Kriterium `.//t:l` existiert stimmt fuer alle 7 Texte (GAR 21.320 l, MR2 9.037 l, Rest 0),
  beide GAR/MR2-Tokens stehen in `<l>`.
- Chargen-Prosa gegen die Basis messen, nicht gegen einen offenen PR (#416 = origin/fix/198-lemma-2598-nom,
  setzt AC3_23010_1 auf lemma_9644 NOM). Messung:
  `git grep -h type_117159 <ref> -- tei/ | grep -o 'lemmaRef="[^"]*"' | sort | uniq -c`.
- Runde 2, Extraktion ueber w|pc in Dokumentordnung: Fenster = 18 TOKENS (w+pc) je Seite, sichtbare
  Woerter 13 bis 18; „18 Woerter" ist deshalb falsch, „18 Tokens" richtig. Nachbau mit lxml `tree.iter(w,pc)`
  + Index-Dict (kein list.index, sonst 2 min auf CEFB) reproduziert CSV und BELEGE byte-gleich.
- pc tragen @join (left default, right bei oeffnenden Zeichen wie `<`): der Reader
  (tei-text-reader.js:783ff) setzt Leerraum danach. Eine Zeichenmengen-Regel („kein Leerzeichen vor
  ,.;:!?»«)]") weicht davon nur bei GAR-Redezeichen `< >` ab; »« kommen als pc im Korpus nicht vor.
  Seitentemplate haengt Kontext mit festem Leerzeichen an die Markierung: bei Folge-pc (MR2 „hawe ,") sichtbar.
- BELEGE-Array aus dem HTML per `re.search(r'const BELEGE = (\[.*?\]);\n', html, re.S)` + json.loads
  gegen faelle.csv (csv, delimiter=';') feldweise vergleichen: 13/13 gleich.
- Typ-Id-Eindeutigkeit: Regex ueber `<w ...>`-Tags aller tei/*.xml, corresp -> set(lemmaRef):
  256.762 Typ-Ids, 0 mit >1 Lemma (Laufzeit unter 1 min). extract-variants.py:332 meldet, return 0 = kein Gate.
- Zeilennummern in Skriptzitaten (`datei.py:N`) mit `git show <ref>:<pfad> | grep -n` pruefen: :19 war :20.
- Runde 4 (10.09.2026, nach CI-Bot-Runde 3): Gate check-no-cdn.py um <link> erweitert. Messung ueber die
  eigene Dateiliste des Skripts per importlib (`g.html_files(g.REPO)`: 20 Dateien, find liefert 22 ohne
  tei/data/node_modules, Differenz = test-results). Vorher/nachher NICHT per git stash (Arbeitsbaum des
  Aufrufers), sondern `git show HEAD:<pfad> | grep -c`. rg ueber das Repo ohne Verzeichnisausschluss haengt
  >120 s (tei/ 1,4 GB), Dateiliste aus dem Skript ist der schnelle Weg.
- LINK_REL `rel\s*=` hat keine Attributgrenze: `data-rel="canonical"` vor `rel` und `?rel=canonical` im
  href eines <link> ohne rel werden als exempt gelesen (konstruiert, nicht blockierend); Fix waere
  `(?<![\w-])rel\s*=`. HTML-Kommentare werden mitgeprueft (wie bei <script src>), &lt;link&gt; nicht.
- 21 externe Hosts in HTML, 8 davon ausserhalb <a href> (meta og:url, <code>, svg xmlns, Matomo-Inline-JS
  webstatistics.sbg.ac.at 17x); keiner in <link>. Auftrag sagte 18 und „alle in <a href>".
