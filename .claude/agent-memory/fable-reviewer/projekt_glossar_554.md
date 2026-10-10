---
name: projekt-glossar-554
description: #554 Glossar Kochbuchforschung (WordPress-Export in sources/): PII-Pruefrezept, was nach der Mail-Bereinigung stehen blieb, Attachment-Oeffentlichkeit
metadata:
  type: project
---

Zwei Runden am 10.10.2026 (`claude/554-glossar`). Bei jedem weiteren Fremdexport nach `sources/` diese Punkte vorab abarbeiten; Personendaten im Korpus: [[header-spiegel]].

- **PII-Prüfung eines WordPress-Exports nicht an der Mail-Regex aufhängen.** Die Bereinigung traf alle Mail-Vorkommen, ließ aber im Impressum die Telefonnummer der Herausgeberin direkt neben der entfernten Mailadresse stehen. Rezept: Zeilendiff Original gegen Bereinigt (gleiche Zeilenzahl, da Textersatz), dann gezielt `Telefon`, `\+\d{2}`, `<address>`, `credit` in `_wp_attachment_metadata`, `/author/`, `?author=` suchen.
- **Ortsangaben prüfen:** Zuordnung je Fund über das umschließende `<item>`, nicht der Seitenangabe des Arbeiters glauben (er verortete Impressum-Funde auf der "Kontaktseite").
- **GitHub-`user-attachments` eines öffentlichen Repos sind ohne Login abrufbar** (curl -sI: 302 auf signierte S3-URL). Ein "Original nur als Anhang in #N" ist also öffentlich, und das Löschen des Kommentars löscht die Datei nicht (gemessen 10.10.: HTTP 200 danach). Die Datei-ID eines solchen Anhangs gehört nie in Notizen, Commits oder Issues.
- **#397 an `sources/`:** `sources/README.md` sagt im Kopf "historische Ingest-Vorlagen" und "Alles ... Auszug aus dem 9,1-GB-Archiv"; jeder neue Nicht-Legacy-Bestand macht das falsch, ohne dass der Diff die Zeilen berührt.
- **Original beschaffen:** der Anhang in #423 ist gelöscht, das Original gibt es nur bei KZW. Bytes und SHA-256 gegen die Glossar-README prüfen, dann `bereinige-export.py` (mit `-E -P`, nicht `-I`) und `cmp` gegen den Blob.
- **`PHONE_RE` frisst `-` und Leerzeichen hinter der Nummer** (`[\d ()/\-]{5,}`): eine Probe mit `<!-- Tel.: ... -->` zerbrach das `-->`, Mutationen deshalb nicht in Kommentare setzen. Nationale Form ohne `Tel:` (`0662/...`) trifft die Regex nicht.
- Der lokale Squash vor dem Push revertierte einen main-Commit, siehe [[querschnitt-git]].
