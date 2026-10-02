---
name: parzival-buecher-358
description: Parzival-Buchgrenzen (#358): Messrezept am OCR von Bartsch und Martin, Fallen (VIII = 398,1, Redezeichen-pc, TEI-gegen-TEI-Vergleich)
metadata:
  type: project
---

`ingest/parzival-buecher/grenzen.csv` (16 Buchanfaenge nach Lachmann) ist die Eingabe von A3 (`<milestone unit="book">`); ein falscher Wert wandert in den Korpus. Buch VIII beginnt bei 398,1 (PZ_39801_0), nicht bei 399,1.

**Messrezept**
- Quellen als OCR: `https://archive.org/download/<id>/<id>_djvu.txt` nach `.claude/tmp/` (gitignoriert). Bartsch `wolframsvonesch01bartgoog` (Bd. 9), `wolframsvonesch03bartgoog` (Bd. 10), `wolframsvonesch00bartgoog` (Bd. 11); Martin Kommentar `parzival00wolfuoft`.
- Bartsch: Ueberschrift `ACHTES BUCH.` in Grossbuchstaben, dann Inhaltsangabe, dann der erste Vers mit Marginalzahl; Kolumnentitel wiederholen die Ueberschrift. OCR von Bd. 10 schlecht, Anfangswoerter nur locker suchen.
- Martin: Buchueberschrift als kurze roemische Zeile (OCR `IL`, `YII.`, `XIIL`), dann die erste Note; Kolumnentitel nennen Buch und Stellenbereich. Eine Zahl wie `679, 4` am Zeilenanfang kann ein Querverweis in der Note zum Vorbuch sein.
- `build-grenzen.py` reproduziert die CSV byteidentisch; `git status` zeigt unter autocrlf trotzdem ` M`, der Blob-Hash (`hash-object --no-filters`) ist die Messung.

**Fallen**
- Ein Anfangswort-Vergleich TEI gegen TEI (Woerter aus dem TEI, geprueft gegen das TEI) prueft nichts gegen die Quelle; Bartsch 787,1 „Anfortas unt die sîne", TEI „amfortas und die".
- `<pc>&lt;</pc>` vor einem Buchanfang (PZ_43301_0) ist ein Redezeichen, keine editorische Klammer; die erste Wort-ID von IX ist deshalb `PZ_43301_1`.
- Martins erste kommentierte Note liegt oft nach dem Buchanfang (VII 338,2 statt 338,1): sie ist kein Beleg gegen die Grenze.
- `<hi rend="initial">` steht an 12 von 16 Buchanfaengen (nicht XI, XII, XIII, XVI) und an 398,1, nicht an 399,1; ein Buch-Markup gibt es im TEI nicht, `div type="chapter"` sind Dreissiger.
