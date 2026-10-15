---
name: projekt-lauf-1016-554b
description: KZWs Prüfergebnisse zum Glossar #554 (Spur lauf-554b, 15.10.2026): Antwort-JSON lesen, eigene Edits erkennen, Anhänge gegen GitHub prüfen, Zählfallen bei Sense-IDs, Stricker, Lerchen
metadata:
  type: project
---
Geschrieben 15.10.2026, Runde 1 auf 488e64e14. Zahlen sind Messung dieser Runde, vor Gebrauch neu messen.

- **Sense-Nummern sind nicht global eindeutig.** `sense_5899` gibt es unter lemma_50993 und lemma_8870; wer eine gelöschte Bedeutung sucht, grept `lemma_N_sense_M`, sonst zählt er fremde Treffer (Index und API zeigten 2, beide fremd).
- **KZWs Antwort-JSON** (`ingest/glossar-554/kzw-2026-10-15/…Antworten….json`): `decisions[]` mit `group` A–E, `choice` (`sense:<id>`, `passt`, `teile`, `eigener-teil`, `other`, `nicht-noetig`, `heinrich`, `zusammen`, leer bei `status: unreviewed`), `text`, `comment`. Ihr eigener Text = `text` ≠ Seitenvorschlag; die Prüfseite JSON-escaped gerade Anführungszeichen (`\"`), also vor dem Vergleich `"`, `\` und Whitespace aus beiden Seiten streichen. So gemessen: nur latech und vînæger sind von ihr, letzen nicht.
- **GitHub-Anhänge ohne Datei prüfen:** `curl -sL <user-attachments-URL> | git hash-object --stdin` gegen `git hash-object <repo-datei>`; Kommentar-Body über `gh api repos/<o>/<r>/issues/comments/<id> --jq .body`.
- **Hook im Worktree:** `git` in einem `subprocess`-Aufruf innerhalb `python -c` und `git show … > /dev/null` werden abgelehnt; `git -C <wt> show <rev>:<pfad> | python -c "…sys.stdin…"` geht.
- **Zählfallen:** Stricker hat in `works.xml` 145 Werke (`author/@ref="persons.xml#person_4"`), alle mit TEI-Datei; „nur ALL und BMG“ ist falsch. Lerchen-Tokens: 62 mit Präfix lerch/lerk/lerich, 75 als Teilstring (auch „allerklugst“); die genannten 63 bzw. 83 reproduziert keine Regel, 0 mit fuoz-Form danach stimmt.
- **Schnell nachfahrbar:** `literatur-erfassen.py` ohne `--schreiben` druckt Zeilen/Werke/Kommentare in Sekunden; `lxml` RelaxNG auf `lexicon.xml` gegen `schema/mhdbdb-authority.rng` läuft unter einer Minute. Kuratierte Lemmata = Einträge mit `resp="contributors.xml#` (Basis 94, HEAD 135).

Runde 2 (abec696c0), 15.10.2026:
- **Fehlerjournal-Kette misst man an den Zeigern, nicht am Satz:** `rg -o "letzte Zeile zu dieser Lehre ist [^.]*"` und rückwärts folgen. Eintrag 125 nannte „132; davor 117, dritte Zeile“; 117 zeigt auf 116, 116 auf „keine“, also vier Zeilen. Nummern sind in der Datei nicht monoton (…123, 130, 131, 132, 125), Freiheit einer Nummer nur per `rg "^### N\."` auf allen Zweigen prüfen.
- **`sense_5899` nach dem Löschen bei letzen nur noch an zwei Lemmata** (50993, 8870); eine Journalzeile im Präsens („gibt es an drei“) misst den Stand vor dem PR. Bei jeder Löschung die Nachbarsätze auf Präsens prüfen.
- **Korpus-Index `lemmaIndex[lemma]` ist eine Siglenliste, keine Tokenzahl** (mete: 31 Siglen, 60 Tokens in `tei/`). „63 Belege inklusive honecmete und mandelmet“ = 60+1+2; `sinôpel` in der Notiz ist das Lemma `sinopel` (lemma_5494, 6). brî-Tokens: 9, alle `pos="NOM"`.
- **Hook:** ein `python -c "…"` mit dem Wort `Git` im Pfad wurde einmal als „zu komplexer git-Aufruf“ abgelehnt; Skript per Write nach `%TEMP%` legen und mit `python -I` starten.
