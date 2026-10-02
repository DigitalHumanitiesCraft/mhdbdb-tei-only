---
name: projekt-370-corresp
description: "#370 Punkt 2 (WZB-Paare ohne @corresp) im Review: ANLEGEN-Falle bei schon vorhandenem Typ, zwei Tokenzaehlungen (31.08. vs. heute), Stichprobenrezept, was die Skripte unter scripts/review/*-370-* nicht pruefen"
metadata:
  type: project
---
Stand 02.10.2026, Runde 1 auf `claude/lauf-c1-370` (42296e72a).

**ANLEGEN heisst „neuen Typ praegen" und setzt voraus, dass keiner existiert.** `build-370-entscheidungen.py` gibt jedem Paar ohne Handurteil ANLEGEN, auch wenn `varianten_aehnlich[0]` die Form selbst ist (Begruendung sagt dann woertlich „Unterschied keiner"). Im Nachtrag (Paare seit 31.08., `urteile-nachtrag.csv` leer) traf das 25 von 74 Paaren (29 Tokens): `in`/lemma_3028 hat type_10369 mit 2.945 WZB-Tokens, die 3 offenen brauchen Punkt-1-Verknuepfung, keinen zweiten Typ. In der 484er-Liste 0 solche Faelle, weil Punkt 1 dort schon verknuepft hatte.
- **Messrezept** (<1 min): variants.xml je Lemma Formen casefold sammeln; WZB `<w>` mit `@lemmaRef` nach (NFC-lower-Text, erstes Lemma) auf `@corresp`-Counter; jedes Paar der Entscheidungsliste mit `mit_corresp > 0` ist ein Verknuepfungs-, kein Anlegefall. Casefold ist weiter als der Projektschluessel (lower): `vassen`/`vaßen` ist ein Fehlalarm.
- **Why:** G3.3 im Laufplan (`docs/playbooks/kickoffs/2026-10-02-lauf.md`) sagt nur „gleiche Methode"; der Nachtrag hat keine Handurteile, also faellt dort alles in den Auto-Pfad.

**Zwei Tokenzahlen.** `offene-faelle.csv` (31.08.) summiert 5.273, dieselben 484 Paare haben am 01.10. 5.283 offene Tokens (8 Paare mit mehr Tokens: et, tŏten, getŏtet, hŏren, vŏrchte, hŏret, hŏrt, pŏse, zusammen +10). `find-370-nachtrag.py` zaehlt nur **neue Paare**, nie neue Tokens bekannter Paare; die 10 fallen zwischen beide Listen. G3.3 kennt das („Soll fuer A2: alle Tokens ohne @corresp, nicht die CSV-Zahl"); die Spalte `tokens` und die Zaehlungsdateien tragen trotzdem die 31.08.-Werte.

**Stichprobe reproduzieren:** `random.Random(20261002).sample(sorted(auto_keys), 30)`, wobei `auto_keys` = Paare, deren Begruendung mit `[klar] Entschieden an den Belegen` beginnt (405). `stichprobe.txt` ist damit exakt nachgerechnet.

**Was die Skripte nicht pruefen:** `pruefe_urteile` prueft das Ziellemma nur bei `ANDERE_ZUORDNUNG:`, nicht beim `vorschlag` eines PRUEFSEITE-Urteils; kein Skript vergleicht Lexikon-`pos` mit Token-`@pos` (ART/DET-Legacy macht das ohnehin laut). `fundstelle()` in `build-370-pruefseite.py` verlangt `WZB_x_n_n$`; Split-Token-IDs wie `WZB_165vb_33_1b` (#235) stehen nur im Nachtrag und wuerden eine Nachtrag-Pruefseite abbrechen lassen.

**Pruefseite:** OPTIONEN hat 4 Eintraege (mit „Zustimmung zu meinem Vorschlag"), die Anleitung spricht von „drei Antworten". `scripts/review/README.md` kennt die 370-Skripte nicht (Tabelle nur 359).
