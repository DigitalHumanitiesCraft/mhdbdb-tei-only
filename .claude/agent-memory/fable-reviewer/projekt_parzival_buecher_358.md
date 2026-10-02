---
name: parzival-buecher-358
description: Parzival-Buchgrenzen (#358): Buch VIII beginnt 398,1 (nicht 399,1), beide Quellen und die TEI-Initiale sagen es; OCR-Fundstellen bei Bartsch und Martin; Redezeichen-pc auch in PZ; A3 konsumiert grenzen.csv
metadata:
  type: project
---

**Buch VIII des Parzival beginnt bei 398,1 „Swer was ze Bêârosche komen" (PZ_39801_0), nicht bei 399,1.** Runde 1 zu `ingest/parzival-buecher/grenzen.csv` am 02.10.2026 hatte 399,1 drin; die Spur hatte Martins erste Note aus dem OCR gelesen und 398 uebersehen. Alle anderen 15 Grenzen stimmen (I 1,1; II 58,27; III 116,5; IV 179,13; V 224,1; VI 280,1; VII 338,1; IX 433,1; X 503,1; XI 553,1; XII 583,1; XIII 627,1; XIV 679,1; XV 734,1; XVI 787,1).

**Why:** A3 (`claude/lauf-a3-358`) setzt `<milestone unit="book">` aus genau dieser CSV ins TEI; ein falscher Wert dort wandert in den Korpus.

**How to apply:**
- Quellen als OCR laden: `https://archive.org/download/<id>/<id>_djvu.txt` nach `.claude/tmp/` (gitignoriert). Bartsch Bd. 9 `wolframsvonesch01bartgoog` (2. Aufl., Vorwort Ostersonntag 1875), Bd. 10 `wolframsvonesch03bartgoog` (1876), Bd. 11 `wolframsvonesch00bartgoog` (Dritter Theil, Zweite Auflage 1877); Martin Kommentar `parzival00wolfuoft` (Germanistische Handbibliothek IX,2, 1903).
- Bartsch: Buchueberschrift `ERSTES BUCH.` usw. in Grossbuchstaben, dann Prosa-Inhaltsangabe, dann der erste Vers mit Marginalzahl. Grep `rg -n 'ACHTES BUCH'` und den ersten Treffer lesen; Kolumnentitel wiederholen die Ueberschrift auf jeder zweiten Seite. Bd. 10: `ACHTES BUCH.` Z. 10199, erster Vers Z. 10353 (`8 Swer was ze BJirosche iomen`). OCR von Bd. 10 ist schlecht, Anfangswoerter nur locker suchen.
- Martin: Buchueberschrift als kurze roemische Zeile (`^\s*[IVXYL]{1,4}[.,]?\s*$`; OCR liefert `IL`, `YII.`, `YIII.`, `XIIL`), dann Crestien-Vergleich, dann die erste Note. Kolumnentitel `VIII  399,  13  —  401,  5.  319` nennen Buch und Stellenbereich der Seite. `VIII.` Z. 27504, erste Note `398, 4` Z. 27560. Eine Zahl wie `679, 4` am Zeilenanfang kann ein Querverweis in der Note zum Vorbuch sein (Z. 37700), die erste XIV-Note ist `679, 6` (Z. 37726).
- TEI: `<hi rend="initial">` steht in PZ 21-mal, darunter an 12 der 16 Buchanfaenge (nicht XI, XII, XIII, XVI) und an 398,1, nicht an 399,1. Kein Buch-Markup, 827 `div type="chapter"` = Dreissiger.
- PZ_43301_0 (`<pc>&lt;</pc>`) ist ein Redezeichen, keine editorische Klammer: Bartsch druckt «Tuot ûf.», Martin ''Tuot ûf''; PZ hat 1092 `<` und 1101 `>` pc.
- Ein Anfangswort-Vergleich „TEI gegen TEI" (Skript nimmt die Woerter aus dem TEI und prueft sie gegen das TEI) prueft nichts gegen die Quelle; Bartsch schreibt 787,1 „Anfortas unt die sîne", TEI „amfortas und die".
