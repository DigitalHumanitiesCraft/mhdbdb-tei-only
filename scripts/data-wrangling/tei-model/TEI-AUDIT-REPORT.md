# TEI Corpus Audit Report

**Date:** 2026-04-08
**Files analyzed:** 666
**Excluded:** `*.disamb.tei.xml`
**Script:** `scripts/data-wrangling/tei-model/audit-tei-corpus.py`

---

## Korpus-Statistiken

| Metrik | Wert |
|--------|------|
| Dateien | 666 |
| Elemente gesamt | 12,763,244 |
| Groesste Datei | OVG.tei.xml (629,089 Elemente) |
| Kleinste Datei | EUS.tei.xml (154 Elemente) |
| Distinkte Elemente | 76 |

## Element-Inventar (Top 30)

| # | Element | Count | Dateien | Eltern | Attribute |
|---|---------|-------|---------|--------|-----------|
| 1 | `<w>` | 9,282,982 | 666 | l, p, hi, supplied, head | @xml:id, @pos, @wordRef, @lemmaRef, @meaningRef |
| 2 | `<l>` | 1,441,605 | 620 | p, lg, body, div, head | @n |
| 3 | `<seg>` | 1,370,191 | 659 | l, p, head, supplied, div | @xml:id, @type |
| 4 | `<hi>` | 415,295 | 649 | l, hi, p, supplied, head | @rend |
| 5 | `<lb>` | 55,853 | 46 | p, head, hi, div, supplied | @n |
| 6 | `<caesura>` | 53,081 | 253 | l, p, hi, supplied | @xml:id |
| 7 | `<lg>` | 28,595 | 75 | p, div | @type, @n |
| 8 | `<supplied>` | 23,401 | 315 | l, p, hi, note, head | @n |
| 9 | `<p>` | 10,190 | 666 | div, projectDesc, editorialDecl, availability, body | @xml:lang, @n |
| 10 | `<gloss>` | 8,698 | 666 | category | @xml:lang |
| 11 | `<div>` | 6,707 | 240 | body, div, p | @type, @n |
| 12 | `<pb>` | 6,197 | 46 | p, l, head, div, note | @n, @type |
| 13 | `<idno>` | 3,332 | 666 | msIdentifier, person, monogr | @type |
| 14 | `<title>` | 3,162 | 666 | titleStmt, monogr, analytic, series, bibl | @level, @xml:lang, @type, @ana |
| 15 | `<head>` | 3,127 | 177 | div |  |
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

**Eltern:** `<l>` (8,224,841), `<p>` (619,298), `<hi>` (379,939), `<supplied>` (53,746), `<head>` (3,783), `<div>` (1,044), `<suppplied>` (148), `<body>` (103), `<note>` (60), `<lg>` (18)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@xml:id` | 9,282,982 | 666 | high | Pattern: `{SIGLE}_{position}` |
| `@pos` | 7,406,168 | 666 | high | >100 distinkte |
| `@wordRef` | 7,406,166 | 666 | high | Pattern: `lexicon.xml#{ref}` |
| `@lemmaRef` | 7,391,273 | 666 | high | Pattern: `lexicon.xml#lemma_{id}[_sense_{id}[_type_{id}]]` |
| `@meaningRef` | 5,852,223 | 666 | high | Pattern: `lexicon.xml#lemma_{id}[_sense_{id}[_type_{id}]]` |

---

### `<seg>` — 1,370,191 Vorkommen in 659 Dateien

**Eltern:** `<l>` (1,304,030), `<p>` (64,150), `<head>` (1,054), `<supplied>` (738), `<div>` (88), `<note>` (82), `<suppplied>` (26), `<body>` (15), `<hi>` (5), `<lg>` (3)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@xml:id` | 1,370,191 | 659 | high | Pattern: `{SIGLE}_{position}` |
| `@type` | 1,370,191 | 659 | low | `pc` (1,370,191) |

---

### `<hi>` — 415,295 Vorkommen in 649 Dateien

**Eltern:** `<l>` (358,376), `<hi>` (36,932), `<p>` (12,472), `<supplied>` (5,916), `<head>` (1,345), `<note>` (226), `<body>` (10), `<suppplied>` (10), `<div>` (8)

**Kinder:** `<w>` (379,939), `<hi>` (36,932), `<supplied>` (295), `<lb>` (258), `<seg>` (5), `<caesura>` (3), `<num>` (1)

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

### `<div>` — 6,707 Vorkommen in 240 Dateien

**Eltern:** `<body>` (4,716), `<div>` (1,964), `<p>` (27)

**Kinder:** `<l>` (6,709), `<p>` (6,535), `<head>` (3,127), `<div>` (1,964), `<w>` (1,044), `<lb>` (92), `<seg>` (88), `<lg>` (68), `<pb>` (28), `<hi>` (8)

**Haeufigste Kind-Sequenzen:**
- `p` (3,163x)
- `head > p` (3,057x)
- `div` (331x)
- `p > div` (28x)
- `lg` (27x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@type` | 4,528 | 119 | low | `song` (1,373), `stanza` (1,122), `chapter` (604), `recipe` (452), `deed` (300) ... +10 more |
| `@n` | 4,501 | 100 | high | >100 distinkte |

---

### `<l>` — 1,441,605 Vorkommen in 620 Dateien

**Eltern:** `<p>` (1,223,226), `<lg>` (187,216), `<body>` (20,315), `<div>` (6,709), `<head>` (3,036), `<supplied>` (679), `<note>` (424)

**Kinder:** `<w>` (8,224,841), `<seg>` (1,304,030), `<hi>` (358,376), `<caesura>` (52,950), `<supplied>` (21,446), `<pb>` (292), `<note>` (245), `<num>` (1), `<suppplied>` (1)

**Haeufigste Kind-Sequenzen:**
- `w > seg` (565,873x)
- `w` (328,003x)
- `hi > w > seg` (127,003x)
- `hi > w` (109,798x)
- `w > seg > w > seg` (59,804x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@n` | 1,441,605 | 620 | high | >100 distinkte |

---

### `<lb>` — 55,853 Vorkommen in 46 Dateien

**Eltern:** `<p>` (54,066), `<head>` (1,430), `<hi>` (258), `<div>` (92), `<supplied>` (6), `<note>` (1)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@n` | 55,853 | 46 | high | >100 distinkte |

---

### `<lg>` — 28,595 Vorkommen in 75 Dateien

**Eltern:** `<p>` (28,527), `<div>` (68)

**Kinder:** `<l>` (187,216), `<note>` (132), `<w>` (18), `<seg>` (3)

**Haeufigste Kind-Sequenzen:**
- `l` (28,460x)
- `note > l` (132x)
- `l > w > seg` (3x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@type` | 28,595 | 75 | low | `stanza` (28,595) |
| `@n` | 28,595 | 75 | high | >100 distinkte |

---

### `<p>` — 10,190 Vorkommen in 666 Dateien

**Eltern:** `<div>` (6,535), `<projectDesc>` (1,332), `<editorialDecl>` (1,332), `<availability>` (666), `<body>` (325)

**Kinder:** `<l>` (1,223,226), `<w>` (619,298), `<seg>` (64,150), `<lb>` (54,066), `<lg>` (28,527), `<hi>` (12,472), `<pb>` (5,719), `<supplied>` (1,379), `<cb>` (990), `<note>` (851)

**Haeufigste Kind-Sequenzen:**
- `l` (2,358x)
- `lg` (1,486x)
- `l > pb > l` (259x)
- `l > pb > l > pb > l` (93x)
- `hi > w > l` (43x)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@xml:lang` | 2,664 | 666 | low | `de` (1,332), `en` (1,332) |
| `@n` | 591 | 4 | low | `11` (73), `21` (73), `1` (70), `31` (39), `41` (25) ... +71 more |

---

### `<pb>` — 6,197 Vorkommen in 46 Dateien

**Eltern:** `<p>` (5,719), `<l>` (292), `<head>` (156), `<div>` (28), `<note>` (2)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@n` | 6,197 | 46 | high | >100 distinkte |
| `@type` | 1,631 | 16 | low | `folio` (1,532), `edition` (99) |

---

### `<head>` — 3,127 Vorkommen in 177 Dateien

**Eltern:** `<div>` (3,127)

**Kinder:** `<w>` (3,783), `<l>` (3,036), `<lb>` (1,430), `<hi>` (1,345), `<seg>` (1,054), `<pb>` (156), `<supplied>` (123), `<note>` (1)

**Haeufigste Kind-Sequenzen:**
- `l` (1,869x)
- `lb > hi > w` (310x)
- `lb > hi > w > seg` (256x)
- `lb > hi > seg` (185x)
- `lb > w` (91x)

---

### `<supplied>` — 23,401 Vorkommen in 315 Dateien

**Eltern:** `<l>` (21,446), `<p>` (1,379), `<hi>` (295), `<note>` (137), `<head>` (123), `<supplied>` (20), `<div>` (1)

**Kinder:** `<w>` (53,746), `<hi>` (5,916), `<seg>` (738), `<l>` (679), `<supplied>` (20), `<lb>` (6), `<note>` (1), `<caesura>` (1)

**Haeufigste Kind-Sequenzen:**
- `w` (18,184x)
- `hi > w` (3,526x)
- `hi` (956x)
- `l` (147x)
- `hi > w > hi > seg` (127x)

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

**Eltern:** `<l>` (52,950), `<p>` (127), `<hi>` (3), `<supplied>` (1)

| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |
|----------|-------|---------|---------------|---------------|
| `@xml:id` | 2,724 | 180 | high | Pattern: `{SIGLE}_{position}` |

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

| Attribut | Count | Dateien | Migration |
|----------|-------|---------|-----------|
| `@meaningRef` | 5,852,223 | 666 | → `@ana` |
| `@wordRef` | 7,406,166 | 666 | → `@corresp` |

### `<seg type="pc">` → `<pc>`

1,370,191 Vorkommen von `<seg type="pc">`. TEI P5 empfiehlt `<pc>` als Ersatz.

### `<l>` in `<p>` (TEI-nonkonform fuer Prosa)

1,223,226 Vorkommen von `<l>` als Kind von `<p>`. TEI P5 definiert `<l>` als Verszeile.

## Anhang: Vollstaendige Element-Liste

| Element | Count | Dateien |
|---------|-------|---------|
| `<w>` | 9,282,982 | 666 |
| `<l>` | 1,441,605 | 620 |
| `<seg>` | 1,370,191 | 659 |
| `<hi>` | 415,295 | 649 |
| `<lb>` | 55,853 | 46 |
| `<caesura>` | 53,081 | 253 |
| `<lg>` | 28,595 | 75 |
| `<supplied>` | 23,401 | 315 |
| `<p>` | 10,190 | 666 |
| `<gloss>` | 8,698 | 666 |
| `<div>` | 6,707 | 240 |
| `<pb>` | 6,197 | 46 |
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
| `<particDesc>` | 666 | 666 |
| `<listPerson>` | 666 | 666 |
| `<revisionDesc>` | 666 | 666 |
| `<change>` | 666 | 666 |
| `<text>` | 666 | 666 |
| `<body>` | 666 | 666 |
| `<pubPlace>` | 660 | 652 |
| `<analytic>` | 536 | 533 |
| `<series>` | 461 | 457 |
| `<edition>` | 19 | 19 |
| `<ab>` | 10 | 10 |
| `<num>` | 2 | 2 |
| `<suppplied>` | 1 | 1 |
