# TEI Corpus Audit Report

**Date:** 2026-04-09
**Files analyzed:** 666
**Excluded:** `*.disamb.tei.xml`
**Script:** `scripts/data-wrangling/tei-model/audit-tei-corpus.py`

---

## Korpus-Statistiken

| Metrik | Wert |
|--------|------|
| Dateien | 666 |
| Elemente gesamt | 12,767,448 |
| Groesste Datei | OVG.tei.xml (629,095 Elemente) |
| Kleinste Datei | EUS.tei.xml (161 Elemente) |
| Distinkte Elemente | 78 |

## Element-Inventar (Top 30)

| # | Element | Count | Dateien | Eltern | Attribute |
|---|---------|-------|---------|--------|-----------|
| 1 | `<w>` | 9,282,982 | 666 | l, p, hi, supplied, head | @xml:id, @pos, @corresp, @lemmaRef, @ana |
| 2 | `<pc>` | 1,370,191 | 659 | l, p, head, supplied, div | @xml:id, @join |
| 3 | `<l>` | 1,355,514 | 602 | p, lg, body, div, head | @n |
| 4 | `<hi>` | 415,295 | 649 | l, p, hi, supplied, head | @rend |
| 5 | `<lb>` | 141,944 | 64 | p, head, div, hi, supplied | @n |
| 6 | `<caesura>` | 53,081 | 253 | l, p, hi, supplied | @xml:id |
| 7 | `<lg>` | 29,717 | 76 | p, body, div | @type, @n |
| 8 | `<supplied>` | 23,402 | 315 | l, p, hi, head, note | @n |
| 9 | `<p>` | 12,399 | 666 | div, normalization, projectDesc, editorialDecl, lg | @xml:lang, @n |
| 10 | `<gloss>` | 8,698 | 666 | category | @xml:lang |
| 11 | `<pb>` | 6,197 | 46 | p, head, l, div, note | @n, @type |
| 12 | `<div>` | 5,585 | 239 | body, div, p | @type, @n |
| 13 | `<idno>` | 3,332 | 666 | msIdentifier, person, monogr | @type |
| 14 | `<title>` | 3,162 | 666 | titleStmt, monogr, analytic, series, bibl | @level, @xml:lang, @type, @ana |
| 15 | `<head>` | 3,127 | 177 | div, lg |  |
| 16 | `<note>` | 2,777 | 666 | p, person, biblStruct, bibl, l | @type, @n |
| 17 | `<persName>` | 1,880 | 666 | person, authority | @type, @role, @xml:lang |
| 18 | `<category>` | 1,800 | 666 | taxonomy | @xml:id, @corresp, @ana |
| 19 | `<orgName>` | 1,549 | 666 | publisher, respStmt |  |
| 20 | `<date>` | 1,457 | 666 | imprint, publicationStmt, bibl | @when, @notBefore, @notAfter, @from |
| 21 | `<ref>` | 1,439 | 666 | publicationStmt, bibl | @target, @type |
| 22 | `<name>` | 1,420 | 666 | respStmt, author | @ref, @xml:lang |
| 23 | `<forename>` | 1,405 | 666 | editor, persName |  |
| 24 | `<surname>` | 1,405 | 666 | editor, persName |  |
| 25 | `<author>` | 1,375 | 666 | titleStmt, analytic, monogr | @ref |
| 26 | `<msName>` | 1,362 | 666 | msIdentifier | @xml:lang |
| 27 | `<ptr>` | 1,332 | 666 | publisher, bibl | @target |
| 28 | `<publisher>` | 1,313 | 666 | publicationStmt, imprint |  |
| 29 | `<cb>` | 996 | 3 | p, div | @n, @type |
| 30 | `<respStmt>` | 933 | 666 | titleStmt, bibl |  |

## Attribut-Inventar (Schluessel-Elemente)

### `<w>` — 9,282,982 Vorkommen in 666 Dateien

**Eltern:** `<l>` (7,172,055), `<p>` (1,664,834), `<hi>` (379,939), `<supplied>` (53,894), `<head>` (7,722), `<div>` (4,355), `<body>` (103), `<note>` (60), `<lg>` (18), `<num>` (2)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@xml:id` | 9,282,982 | 666 | high | Pattern: `{SIGLE}_{position}` |
| `@pos` | 7,406,168 | 666 | high | >100 distinkte |
| `@corresp` | 7,406,166 | 666 | high | Pattern: `variants.xml#{ref}` |
| `@lemmaRef` | 7,391,273 | 666 | high | Pattern: `lexicon.xml#lemma_{id}[_sense_{id}[_type_{id}]]` |
| `@ana` | 5,852,223 | 666 | high | Pattern: `lexicon.xml#lemma_{id}[_sense_{id}[_type_{id}]]` |

---

### `<hi>` — 415,295 Vorkommen in 649 Dateien

**Eltern:** `<l>` (310,410), `<p>` (59,802), `<hi>` (36,932), `<supplied>` (5,926), `<head>` (1,805), `<note>` (226), `<div>` (184), `<body>` (10)

**Kinder:** `<w>` (379,939), `<hi>` (36,932), `<supplied>` (295), `<lb>` (258), `<pc>` (5), `<caesura>` (3), `<num>` (1)

**Haeufigste Kind-Sequenzen:**
- `w` (378,074x)
- `hi` (36,500x)
- `supplied` (289x)
- `lb > hi` (258x)
- `hi > w` (160x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@rend` | 415,295 | 649 | low | `initial` (314,529), `upper_case_first_letter` (92,488), `upper_case` (7,953), `bold` (201), `italic` (124) |

---

### `<div>` — 5,585 Vorkommen in 239 Dateien

**Eltern:** `<body>` (3,594), `<div>` (1,964), `<p>` (27)

**Kinder:** `<l>` (6,305), `<p>` (5,413), `<w>` (4,355), `<head>` (3,090), `<div>` (1,964), `<pc>` (512), `<lb>` (496), `<hi>` (184), `<lg>` (68), `<pb>` (28)

**Haeufigste Kind-Sequenzen:**
- `head > p` (3,020x)
- `p` (2,078x)
- `div` (331x)
- `p > div` (28x)
- `lg` (27x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@type` | 3,406 | 118 | low | `song` (1,373), `chapter` (604), `number` (498), `recipe` (452), `section` (440), `parallel` (24), `colophon` (15) |
| `@n` | 3,379 | 99 | high | >100 distinkte |

---

### `<l>` — 1,355,514 Vorkommen in 602 Dateien

**Eltern:** `<p>` (1,138,219), `<lg>` (187,216), `<body>` (20,315), `<div>` (6,305), `<head>` (2,356), `<supplied>` (679), `<note>` (424)

**Kinder:** `<w>` (7,172,055), `<pc>` (1,135,310), `<hi>` (310,410), `<caesura>` (52,910), `<supplied>` (20,087), `<note>` (245), `<pb>` (50), `<num>` (1)

**Haeufigste Kind-Sequenzen:**
- `w > pc` (562,155x)
- `w` (321,609x)
- `hi > w > pc` (126,455x)
- `hi > w` (107,965x)
- `w > pc > w > pc` (55,928x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@n` | 1,355,514 | 602 | high | >100 distinkte |

---

### `<lb>` — 141,944 Vorkommen in 64 Dateien

**Eltern:** `<p>` (139,073), `<head>` (2,110), `<div>` (496), `<hi>` (258), `<supplied>` (6), `<note>` (1)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@n` | 141,944 | 64 | high | >100 distinkte |

---

### `<lg>` — 29,717 Vorkommen in 76 Dateien

**Eltern:** `<p>` (28,527), `<body>` (1,122), `<div>` (68)

**Kinder:** `<l>` (187,216), `<p>` (1,122), `<note>` (132), `<head>` (37), `<w>` (18), `<pc>` (3)

**Haeufigste Kind-Sequenzen:**
- `l` (28,460x)
- `p` (1,085x)
- `note > l` (132x)
- `head > p` (37x)
- `l > w > pc` (3x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@type` | 29,717 | 76 | low | `stanza` (29,717) |
| `@n` | 29,717 | 76 | high | >100 distinkte |

---

### `<p>` — 12,399 Vorkommen in 666 Dateien

**Eltern:** `<div>` (5,413), `<normalization>` (2,209), `<projectDesc>` (1,332), `<editorialDecl>` (1,332), `<lg>` (1,122), `<availability>` (666), `<body>` (325)

**Kinder:** `<w>` (1,664,834), `<l>` (1,138,219), `<pc>` (231,903), `<lb>` (139,073), `<hi>` (59,802), `<lg>` (28,527), `<pb>` (5,894), `<supplied>` (2,675), `<cb>` (990), `<note>` (851)

**Haeufigste Kind-Sequenzen:**
- `l` (2,138x)
- `lg` (1,486x)
- `l > pb > l` (86x)
- `hi > w > l` (43x)
- `l > pb > l > pb > l` (33x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@xml:lang` | 2,664 | 666 | low | `de` (1,332), `en` (1,332) |
| `@n` | 591 | 4 | low | `11` (73), `21` (73), `1` (70), `31` (39), `41` (25) ... +71 more |

---

### `<pb>` — 6,197 Vorkommen in 46 Dateien

**Eltern:** `<p>` (5,894), `<head>` (223), `<l>` (50), `<div>` (28), `<note>` (2)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@n` | 6,197 | 46 | high | >100 distinkte |
| `@type` | 1,631 | 16 | low | `folio` (1,532), `edition` (99) |

---

### `<head>` — 3,127 Vorkommen in 177 Dateien

**Eltern:** `<div>` (3,090), `<lg>` (37)

**Kinder:** `<w>` (7,722), `<l>` (2,356), `<lb>` (2,110), `<hi>` (1,805), `<pc>` (1,597), `<pb>` (223), `<supplied>` (187), `<note>` (1)

**Haeufigste Kind-Sequenzen:**
- `l` (1,418x)
- `lb > hi > w` (362x)
- `lb > hi > w > pc` (301x)
- `lb > hi > pc` (193x)
- `lb > w` (122x)

---

### `<supplied>` — 23,402 Vorkommen in 315 Dateien

**Eltern:** `<l>` (20,087), `<p>` (2,675), `<hi>` (295), `<head>` (187), `<note>` (137), `<supplied>` (20), `<div>` (1)

**Kinder:** `<w>` (53,894), `<hi>` (5,926), `<pc>` (764), `<l>` (679), `<supplied>` (20), `<lb>` (6), `<note>` (1), `<caesura>` (1)

**Haeufigste Kind-Sequenzen:**
- `w` (18,184x)
- `hi > w` (3,526x)
- `hi` (956x)
- `l` (147x)
- `hi > w > hi > pc` (127x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@n` | 150 | 6 | low | `1` (49), `2` (25), `3` (9), `4` (7), `5` (6) ... +38 more |

---

### `<num>` — 2 Vorkommen in 2 Dateien

**Eltern:** `<hi>` (1), `<l>` (1)

**Kinder:** `<w>` (2)

**Haeufigste Kind-Sequenzen:**
- `w` (2x)

---

### `<caesura>` — 53,081 Vorkommen in 253 Dateien

**Eltern:** `<l>` (52,910), `<p>` (167), `<hi>` (3), `<supplied>` (1)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@xml:id` | 2,724 | 180 | high | Pattern: `{SIGLE}_{position}` |

---

### `<pc>` — 1,370,191 Vorkommen in 659 Dateien

**Eltern:** `<l>` (1,135,310), `<p>` (231,903), `<head>` (1,597), `<supplied>` (764), `<div>` (512), `<note>` (82), `<body>` (15), `<hi>` (5), `<lg>` (3)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@xml:id` | 1,370,191 | 659 | high | Pattern: `{SIGLE}_{position}` |
| `@join` | 1,370,191 | 659 | low | `left` (1,300,822), `right` (69,369) |

---

### `<TEI>` — 666 Vorkommen in 666 Dateien

**Eltern:** 

**Kinder:** `<teiHeader>` (666), `<text>` (666)

**Haeufigste Kind-Sequenzen:**
- `teiHeader > text` (666x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@xml:id` | 666 | 666 | high | >100 distinkte |

---

### `<teiHeader>` — 666 Vorkommen in 666 Dateien

**Eltern:** `<TEI>` (666)

**Kinder:** `<fileDesc>` (666), `<encodingDesc>` (666), `<profileDesc>` (666), `<revisionDesc>` (666)

**Haeufigste Kind-Sequenzen:**
- `fileDesc > encodingDesc > profileDesc > revisionDesc` (666x)

---

### `<title>` — 3,162 Vorkommen in 666 Dateien

**Eltern:** `<titleStmt>` (1,362), `<monogr>` (678), `<analytic>` (536), `<series>` (461), `<bibl>` (125)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@level` | 1,538 | 635 | low | `a` (541), `m` (527), `s` (461), `j` (9) |
| `@xml:lang` | 1,357 | 666 | low | `de` (766), `gmh` (563), `en` (16), `lat` (12) |
| `@type` | 638 | 253 | low | `alternate` (638) |
| `@ana` | 638 | 253 | low | `historic` (573), `science` (60), `unspecific` (5) |

---

### `<author>` — 1,375 Vorkommen in 666 Dateien

**Eltern:** `<titleStmt>` (671), `<analytic>` (576), `<monogr>` (128)

**Kinder:** `<name>` (704)

**Haeufigste Kind-Sequenzen:**
- `name` (704x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@ref` | 671 | 666 | high | Pattern: `#{fragment_id}` |

---

### `<biblStruct>` — 678 Vorkommen in 666 Dateien

**Eltern:** `<listBibl>` (678)

**Kinder:** `<monogr>` (678), `<note>` (626), `<analytic>` (536), `<series>` (461)

**Haeufigste Kind-Sequenzen:**
- `analytic > monogr > series > note` (353x)
- `analytic > monogr > note` (143x)
- `monogr > series > note` (96x)
- `analytic > monogr` (36x)
- `monogr > note` (34x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@type` | 678 | 666 | low | `bookSection` (527), `book` (141), `journalArticle` (9), `document` (1) |
| `@xml:id` | 678 | 666 | high | Pattern: `{SIGLE}_{position}` |
| `@corresp` | 678 | 666 | high | Pattern: `{URI}` |
| `@key` | 678 | 666 | high | >100 distinkte |

---

### `<bibl>` — 791 Vorkommen in 666 Dateien

**Eltern:** `<taxonomy>` (666), `<listBibl>` (125)

**Kinder:** `<ptr>` (666), `<respStmt>` (267), `<note>` (250), `<title>` (125), `<date>` (113), `<ref>` (107)

**Haeufigste Kind-Sequenzen:**
- `ptr` (666x)
- `title > respStmt > date > ref > note` (95x)
- `title > respStmt > date > note` (18x)
- `title > respStmt > ref > note` (12x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@type` | 125 | 121 | low | `digitalIntermediary` (125) |
| `@xml:id` | 125 | 121 | high | Pattern: `{SIGLE}_{position}` |
| `@corresp` | 125 | 121 | high | Pattern: `#{fragment_id}` |

---

### `<category>` — 1,800 Vorkommen in 666 Dateien

**Eltern:** `<taxonomy>` (1,800)

**Kinder:** `<gloss>` (8,698)

**Haeufigste Kind-Sequenzen:**
- `gloss` (1,800x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@xml:id` | 1,800 | 666 | high | >100 distinkte |
| `@corresp` | 1,800 | 666 | high | Pattern: `genres.xml#genre_{hash}` |
| `@ana` | 894 | 666 | low | `parent` (894) |

---

### `<person>` — 670 Vorkommen in 665 Dateien

**Eltern:** `<listPerson>` (670)

**Kinder:** `<persName>` (1,214), `<idno>` (1,154), `<note>` (670)

**Haeufigste Kind-Sequenzen:**
- `persName > idno > note` (670x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@xml:id` | 670 | 665 | high | >100 distinkte |
| `@corresp` | 670 | 665 | high | Pattern: `persons.xml#person_{id}` |

---

## IST/SOLL-Vergleich

### Nicht-Standard-Attribute

Keine nicht-Standard-Attribute auf `<w>` gefunden.

### `<l>` in `<p>` (TEI-nonkonform fuer Prosa)

1,138,219 Vorkommen von `<l>` als Kind von `<p>`. TEI P5 definiert `<l>` als Verszeile.

## Anhang: Vollstaendige Element-Liste

| Element | Count | Dateien |
|---------|-------|---------|
| `<w>` | 9,282,982 | 666 |
| `<pc>` | 1,370,191 | 659 |
| `<l>` | 1,355,514 | 602 |
| `<hi>` | 415,295 | 649 |
| `<lb>` | 141,944 | 64 |
| `<caesura>` | 53,081 | 253 |
| `<lg>` | 29,717 | 76 |
| `<supplied>` | 23,402 | 315 |
| `<p>` | 12,399 | 666 |
| `<gloss>` | 8,698 | 666 |
| `<pb>` | 6,197 | 46 |
| `<div>` | 5,585 | 239 |
| `<idno>` | 3,332 | 666 |
| `<title>` | 3,162 | 666 |
| `<head>` | 3,127 | 177 |
| `<note>` | 2,777 | 666 |
| `<persName>` | 1,880 | 666 |
| `<category>` | 1,800 | 666 |
| `<orgName>` | 1,549 | 666 |
| `<date>` | 1,457 | 666 |
| `<ref>` | 1,439 | 666 |
| `<name>` | 1,420 | 666 |
| `<forename>` | 1,405 | 666 |
| `<surname>` | 1,405 | 666 |
| `<author>` | 1,375 | 666 |
| `<msName>` | 1,362 | 666 |
| `<ptr>` | 1,332 | 666 |
| `<publisher>` | 1,313 | 666 |
| `<cb>` | 996 | 3 |
| `<respStmt>` | 933 | 666 |
| `<resp>` | 933 | 666 |
| `<biblScope>` | 883 | 618 |
| `<bibl>` | 791 | 666 |
| `<editor>` | 739 | 657 |
| `<biblStruct>` | 678 | 666 |
| `<monogr>` | 678 | 666 |
| `<imprint>` | 678 | 666 |
| `<person>` | 670 | 665 |
| `<TEI>` | 666 | 666 |
| `<teiHeader>` | 666 | 666 |
| `<fileDesc>` | 666 | 666 |
| `<titleStmt>` | 666 | 666 |
| `<publicationStmt>` | 666 | 666 |
| `<address>` | 666 | 666 |
| `<street>` | 666 | 666 |
| `<postCode>` | 666 | 666 |
| `<settlement>` | 666 | 666 |
| `<country>` | 666 | 666 |
| `<email>` | 666 | 666 |
| `<authority>` | 666 | 666 |
| `<availability>` | 666 | 666 |
| `<licence>` | 666 | 666 |
| `<sourceDesc>` | 666 | 666 |
| `<msDesc>` | 666 | 666 |
| `<msIdentifier>` | 666 | 666 |
| `<additional>` | 666 | 666 |
| `<listBibl>` | 666 | 666 |
| `<encodingDesc>` | 666 | 666 |
| `<projectDesc>` | 666 | 666 |
| `<editorialDecl>` | 666 | 666 |
| `<classDecl>` | 666 | 666 |
| `<taxonomy>` | 666 | 666 |
| `<profileDesc>` | 666 | 666 |
| `<langUsage>` | 666 | 666 |
| `<language>` | 666 | 666 |
| `<particDesc>` | 666 | 666 |
| `<listPerson>` | 666 | 666 |
| `<revisionDesc>` | 666 | 666 |
| `<change>` | 666 | 666 |
| `<text>` | 666 | 666 |
| `<body>` | 666 | 666 |
| `<normalization>` | 663 | 663 |
| `<pubPlace>` | 660 | 652 |
| `<analytic>` | 536 | 533 |
| `<series>` | 461 | 457 |
| `<edition>` | 19 | 19 |
| `<ab>` | 10 | 10 |
| `<num>` | 2 | 2 |
