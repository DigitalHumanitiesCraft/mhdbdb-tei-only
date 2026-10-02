---
name: projekt-370-corresp
description: "#370 Punkt 2 (WZB-Paare ohne @corresp) im Review: ANLEGEN-Falle bei schon vorhandenem Typ, zwei Tokenzaehlungen (31.08. vs. heute), Stichprobenrezept, was die Skripte unter scripts/review/*-370-* nicht pruefen"
metadata:
  type: project
---
Stand 02.10.2026, Runde 2 auf `claude/lauf-c1-370` (a8d86148c, Runde 1 war 42296e72a).

**ANLEGEN heisst „neuen Typ praegen" und setzt voraus, dass keiner existiert.** Runde 1: der Auto-Pfad gab jedem Paar ohne Handurteil ANLEGEN, auch bei vorhandenem Typ (25 von 74 Nachtragspaaren, 29 Tokens, etwa `in`/lemma_3028 mit type_10369). Seit a8d86148c gibt es den vierten Wert **VERKNUEPFEN** (nur `@corresp` setzen, Punkt-1-Fall), gesetzt aus `lade_vorhandene_typen()` ueber (NFC-lower-Form, Lemma) in variants.xml; Begruendung nennt die Typ-ID. In Runde 2 nachgemessen: alle 25 Typ-IDs stimmen (Form und Lemma, je genau ein Kandidat), 0 Paare mit vorhandenem Typ unter allen 484 Entscheidungen der Liste (auch unter den 7 Hand-ANLEGEN), 0 unter den 49 Nachtrag-ANLEGEN.
- **Messrezept** (<1 min): variants.xml `entry/@corresp` ist durchweg `lexicon.xml#lemma_N` (0 Mehrfachwerte, 0 Formen ohne xml:id), also `split('#')[-1]`; ein `lstrip('#')` laesst das Dateipraefix stehen und jeder Vergleich faellt still durch. WZB-`@lemmaRef` ohne `@corresp`: 5.392, 0 davon mehrwertig.
- **Nicht dasselbe wie VERKNUEPFEN:** 23 ANLEGEN der Liste haben dieselbe Form unter einem ANDEREN Lemma (`heissen`, `is`, `et` usw.), das sind Homographen, die Vorschrift B aus #378 ordnet; `tŏte` steht geteilt (lemma_6118 in der Liste, lemma_6133 im Nachtrag).
- **Why:** G3.3 im Laufplan (`docs/playbooks/kickoffs/2026-10-02-lauf.md`) sagt nur „gleiche Methode"; der Nachtrag hat keine Handurteile, also faellt dort alles in den Auto-Pfad.

**Zwei Tokenzahlen.** `offene-faelle.csv` (31.08.) summiert 5.273, dieselben 484 Paare haben am 01.10. 5.283 offene Tokens (8 Paare mit mehr Tokens: et, tŏten, getŏtet, hŏren, vŏrchte, hŏret, hŏrt, pŏse, zusammen +10). `find-370-nachtrag.py` zaehlt nur **neue Paare**, nie neue Tokens bekannter Paare; die 10 fallen zwischen beide Listen. Seit a8d86148c nennen `entscheidungen-zaehlung*.txt` und der Datenstand der Pruefseite beide Zahlen („Soll fuer Spur A ist die heutige Zahl"); die Spalte `tokens` traegt weiter den 31.08.-Wert. Zaehlungsdateien in Runde 2 gegen die CSV nachgerechnet: alle Werte stimmen (Liste 412/0/43/29, Nachtrag 49/25/0/0, abc 41/18, Stichproben reproduzierbar).

**Stichprobe reproduzieren:** `random.Random(20261002).sample(sorted(auto_keys), 30)`, wobei `auto_keys` = Paare, deren Begruendung mit `[klar] Entschieden an den Belegen` beginnt (405). `stichprobe.txt` ist damit exakt nachgerechnet.

**Was die Skripte nicht pruefen:** `pruefe_urteile` prueft das Ziellemma nur bei `ANDERE_ZUORDNUNG:`, nicht beim `vorschlag` eines PRUEFSEITE-Urteils; kein Skript vergleicht Lexikon-`pos` mit Token-`@pos` (ART/DET-Legacy macht das ohnehin laut). `fundstelle()` in `build-370-pruefseite.py` verlangt `WZB_x_n_n$`; Split-Token-IDs wie `WZB_165vb_33_1b` (#235) stehen nur im Nachtrag und wuerden eine Nachtrag-Pruefseite abbrechen lassen.

**Pruefseite:** OPTIONEN hat 4 Eintraege (mit „Zustimmung zu meinem Vorschlag"); Anleitung seit a8d86148c angepasst, README-Tabelle hat die vier 370-Skripte. #443-Bedingungen fuer die Zustimmungsoption am HTML gemessen: 0 von 116 Radios vorbelegt, Export unterscheidet `stand`+`antwort` (unbearbeitet/null vs. entschieden/Text), Radios setzt review_page.py nur je Karte (change) und beim Import. Der Fuss fuehrt seit a8d86148c einen leeren Block „VERKNUEPFEN: 0 von 484 Paaren", den die Anleitung nicht erklaert (Kosmetik).
