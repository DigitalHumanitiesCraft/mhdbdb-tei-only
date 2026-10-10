# Glossar Kochbuchforschung: WordPress export (raw source, not normative)

> Not corpus data. Normative are only [`tei/`](../../tei/) and
> [`authority-files/`](../../authority-files/). This file is **not validated, not indexed,
> read by no build script** and never cited as evidence for the current data state. It is
> the raw source for [#554](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/554)
> (parent: [#423](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/423)).

## Provenance and licence

- **Source:** WordPress export (WXR 1.2, generator WordPress/4.6.29, created 2026-10-08 13:39)
  of [glossar.kochbuchforschung.org](http://glossar.kochbuchforschung.org/), site title
  "digEST_ivum", "Digitales Glossar zu Essen, Speise und Trank in vernakularen
  Überlieferungen des Mittelalters".
- **Delivered by** KZW (@wachauer) on 2026-10-08 as `digest_ivum.wordpress.2026-10-08.xml`,
  attachment to a comment in #423. That comment was deleted on 2026-10-10 because the
  attachment carried personal data.
- **Licence:** released by KZW for the repository under CC BY-NC-SA 4.0. Her words in the
  deleted comment of 2026-10-08, kept here as the record: "Hier der Export. Repo unter
  CC BY-NC-SA 4.0 ist ok."

## Files

| File | Bytes | SHA-256 |
|---|--:|---|
| `digest_ivum.wordpress.2026-10-08.xml` (original, **not in the repository**: it carries personal data) | 5,791,014 | `2bc3ffbeec0c09cc6999ff2308e364a3c1f604c36f290f8ceaf61305c8162d97` |
| `digest_ivum.wordpress.2026-10-08.bereinigt.xml` (this folder) | 5,790,889 | `96f3c2cbaf8dd5876c1a1c7e8df2b366844e4c4e5d7caa0fddfe24e0db2c801b` |

The original is no longer linked anywhere; whoever needs it asks KZW. The cleaned file is byte-protected against
line-ending rewriting by `sources/.gitattributes` (`glossar-kochbuchforschung/** -text`), so
the SHA-256 above can be checked on the blob.

## What was removed, and why

Personal data does not belong in a public repository, whatever the licence of the content.
`scripts/ingest/glossar-554/bereinige-export.py` replaced it as text, leaving the rest of the
file byte for byte as delivered (536 `<item>` before and after, well-formed under lxml):

| What | Replaced by | Count |
|---|---|--:|
| `wp:author` blocks (login, e-mail, display name, first name, last name) | `author-<id>` for login and display name, empty first and last name, `(E-Mail entfernt)` for the address | 3 blocks |
| `dc:creator` login on every item | the same `author-<id>` | 536 of 536 items |
| E-mail addresses elsewhere (contact-form configuration, a `mailto:` link in the imprint page "Impressum", post 2306, one in the text of a literature note) | `(E-Mail entfernt)` | 10 occurrences |
| The same address in the imprint in the obfuscated form "name at domain.tld" | `(E-Mail entfernt)` | 1 occurrence |
| The phone number in the imprint ("Telefon: ...") | `(Telefonnummer entfernt)` | 1 occurrence |

Control value: the e-mail regex finds **5 distinct addresses in 13 occurrences** in the
original (as the issue says); it finds **0** in the cleaned file. The IP-address regexes (IPv4,
IPv6) find 0 in both. The obfuscated form: 1 hit in the original, 0 in the cleaned file. The
phone-number regex: 1 hit in the original, 0 in the cleaned file; the error message "Die
Telefonnummer ist ungültig." in the contact form is not a number and stays. The script exits
with 1 if any of these remains, or if one of the personal logins (`wachauer`, `klugi`) does.

**Deliberately kept:**

- Names inside bibliographic references and running text ("Zeppezauer-Wachauer, Katharina:
  ..."). That is content, not account data.
- Two image credit lines in the serialized attachment metadata (PHP
  `s:6:"credit";s:29:"Zeppezauer-Wachauer Katharina"`, the length prefix forbids replacing
  them without breaking the serialization).
- Public URLs, including `wp-admin/...` links inside entry texts.

**Side effect:** the serialized contact-form configuration (`wpcf7_contact_form`) carries PHP
length prefixes (`s:53:"..."`) that no longer match the shortened strings. The file is a
reading source, not an import file for a WordPress instance; do not feed it back to one.

## Contents (measured, see `scripts/ingest/glossar-554/messe-export.py`)

536 items: 482 published `lemma` entries, 2 draft `lemma` entries, 23 ACF field definitions,
7 field groups, 10 pages, 8 menu items, 3 attachments, 1 contact form; no comments. The
482 entries by field `sprachstufe`: `gmh` 189, `deu` 287, `deu-enh` 3, `rmd` 1, `nld` 1, empty
1. Entry fields are `wp:postmeta` (ACF), not running text.

## Reproduction

```
python -E -P scripts/ingest/glossar-554/bereinige-export.py <original.xml> sources/glossar-kochbuchforschung/digest_ivum.wordpress.2026-10-08.bereinigt.xml
python -E -P scripts/ingest/glossar-554/messe-export.py sources/glossar-kochbuchforschung/digest_ivum.wordpress.2026-10-08.bereinigt.xml
```

`-E -P` instead of `-I` because the project interpreter keeps `lxml` in the user site, which
`-I` switches off; neither flag set puts the working directory on the import path. The
assignment to lemmata (#554 step 2) is documented in
[`ingest/glossar-554/README.md`](../../ingest/glossar-554/README.md).
