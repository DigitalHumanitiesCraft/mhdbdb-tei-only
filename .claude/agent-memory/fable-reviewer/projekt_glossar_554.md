---
name: projekt-glossar-554
description: #554 Glossar Kochbuchforschung (WordPress-Export in sources/): PII-Pruefrezept, was nach der Mail-Bereinigung stehen blieb, Attachment-Oeffentlichkeit
metadata:
  type: project
---

Runde 1 am 10.10.2026 auf `claude/554-glossar` @ 1698fe97d (Basis 81e4928d8).

- **PII-Pruefung eines WordPress-Exports nicht an der Mail-Regex aufhaengen.** Die Bereinigung
  traf alle 13 Mail-Vorkommen, liess aber im Impressum (`page`, post 2306) die Telefonnummer
  der Herausgeberin stehen, direkt neben der entfernten Mailadresse. Rezept: Zeilendiff
  Original gegen Bereinigt (gleiche Zeilenzahl, da Textersatz), dann gezielt `Telefon`, `\+\d{2}`,
  `<address>`, `credit` in `_wp_attachment_metadata`, `/author/`, `?author=` suchen.
- **Ortsangaben pruefen:** der Arbeiter verortete mailto und verfremdete Adresse auf der
  "Kontaktseite"; beides steht im Impressum. Zuordnung je Fund ueber das umschliessende `<item>`.
- **GitHub-`user-attachments` eines oeffentlichen Repos sind ohne Login abrufbar** (curl -sI:
  302 auf signierte S3-URL). Ein "Original nur als Anhang in #N" ist also oeffentlich, und
  das Loeschen des Kommentars loescht die Datei nicht (gemessen 10.10.: HTTP 200 danach).
  Die Datei-ID eines solchen Anhangs gehoert deshalb nie in Notizen, Commits oder Issues.
- **#397 an `sources/`:** `sources/README.md` sagt im Kopf "historische Ingest-Vorlagen" und
  "Alles ... Auszug aus dem 9,1-GB-Archiv"; jeder neue Nicht-Legacy-Bestand macht das falsch,
  ohne dass der Diff die Zeilen beruehrt.

Runde 2 am 10.10.2026 auf `69d49bc25` (Elternteil 047dae093):

- **Original beschaffen:** Der Kommentar mit dem Anhang in #423 wurde am 10.10. wegen der
  Personendaten geloescht; das Original gibt es nur noch bei KZW. Bytes und SHA-256 gegen die
  Glossar-README pruefen. Dann `bereinige-export.py` (mit `-E -P`, nicht `-I`) und `cmp` gegen den Blob:
  war byte-gleich, Exit 0.
- **`PHONE_RE` frisst `-` und Leerzeichen hinter der Nummer** (`[\d ()/\-]{5,}`): eine Probe mit
  `<!-- Tel.: ... -->` zerbrach das `-->`. Mutationen deshalb nicht in Kommentare setzen. Nationale
  Form ohne `Tel:` (`0662/...`) trifft die Regex nicht; im Bestand gibt es keine solche.
- Der Squash vor dem Push hat #558 revertiert, siehe [[querschnitt-git]].

**How to apply:** bei jedem weiteren Fremdexport nach `sources/` diese vier Punkte vorab
abarbeiten. Siehe auch [[header-spiegel]] fuer Personendaten im Korpus.
