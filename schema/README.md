# MHDBDB TEI-Schemas

RELAX NG-Schemas für das MHDBDB-Korpus und die Authority Files. Gedacht für Projekte, die TEI-Daten erzeugen möchten, die mit der [Mittelhochdeutschen Begriffsdatenbank](https://mhdbdb.plus.ac.at) kompatibel sind.

## Dateien

| Datei | Zweck |
|-------|-------|
| `mhdbdb.rnc` | Korpus-Schema (Quelldatei, RELAX NG Compact) |
| `mhdbdb.rng` | Korpus-Schema (generiert, für lxml/jing) |
| `mhdbdb-authority.rnc` | Authority-Files-Schema (Quelldatei) |
| `mhdbdb-authority.rng` | Authority-Files-Schema (generiert) |
| `tei_all.rng` | TEI P5 4.11.0 (committet im Repo, siehe unten) |
| `examples/` | Validierte Beispieldateien für alle Dokumenttypen |

## Zwei-Stufen-Validierung

Jede MHDBDB-Datei muss beide Stufen bestehen:

1. **TEI-P5-Konformität** (`tei_all.rng`) — die Datei ist valides TEI
2. **MHDBDB-Constraints** (`mhdbdb.rnc` oder `mhdbdb-authority.rnc`) — die Datei folgt den MHDBDB-Konventionen

Stufe 2 ist das maßgebliche Schema (hartes Gate in der CI). Stufe 1 stellt die Interoperabilität mit dem TEI-Ökosystem sicher und wird in der CI als Drift-Wache mitgeprüft: 30 Korpus-Files sind als #30-Baseline (GAPs 1–11 in `mhdbdb.rnc`) absichtlich nicht TEI-Standard-konform — ein 31. Fail würde als WARN im CI-Log erscheinen.

### Editor-Validation: nur Stufe 2 als `<?xml-model?>`-PI

Die TEI-Korpusdateien in `tei/` haben **nur eine** `<?xml-model?>`-Processing-Instruction, die auf `mhdbdb.rng` zeigt. `tei_all.rng` ist dort bewusst **nicht** als PI verlinkt, weil die 30 GAP-Files sonst in oXygen/VS Code Scholarly XML mit konstanten roten Markern gegen Strukturen anlaufen, die das MHDBDB-Schema bewusst toleriert. Vollständige Zwei-Stufen-Validation läuft weiterhin in der CI (`data-integrity.yml`) und im `validate-corpus.py`-Script.

Die 8 Authority-Files in `authority-files/` haben **beide** PIs — dort produziert die Stufe-1-Validierung keine false positives (alle 8 sind grün gegen `tei_all.rng`).

## Schnellstart: Datei validieren

**Gepinnt auf TEI P5 Version 4.11.0** (Last updated 2026-02-18, revision `358d2e48e`). Die Datei `schema/tei_all.rng` ist ins Repo committet, **kein Download von `tei-c.org` zur Build-Zeit** — so sind die Builds reproduzierbar und unabhängig von der Erreichbarkeit des TEI-Servers (#125; zuvor brach ein tei-c.org-Ausfall jeden CI-Run). Der CI-Workflow `.github/workflows/data-integrity.yml` prüft nur noch als Sanity-Check, ob die committete Datei noch die gepinnte Version trägt, und fängt so ein versehentliches Ersetzen. Ein P5-Upgrade ist eine bewusste Handlung: `schema/tei_all.rng` ersetzen und den Pin hier sowie die Workflow-Zeile `EXPECTED="4.11.0"` mitbumpen.

```bash
# tei_all.rng liegt bereits im Repo (schema/tei_all.rng).
# Nur bei einem bewussten TEI-P5-Upgrade neu herunterladen:
#   curl -sL "https://tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" -o schema/tei_all.rng

# RNG aus RNC neu generieren (nach Bearbeitung der .rnc)
python -m rnc2rng schema/mhdbdb.rnc schema/mhdbdb.rng
python -m rnc2rng schema/mhdbdb-authority.rnc schema/mhdbdb-authority.rng

# Korpus-Datei validieren (Python)
python -c "
from lxml import etree
tree = etree.parse('tei/ABG.tei.xml')
# Stufe 1
tei_all = etree.RelaxNG(etree.parse('schema/tei_all.rng'))
print('TEI P5:', 'VALID' if tei_all.validate(tree) else tei_all.error_log)
# Stufe 2
mhdbdb = etree.RelaxNG(etree.parse('schema/mhdbdb.rng'))
print('MHDBDB:', 'VALID' if mhdbdb.validate(tree) else mhdbdb.error_log)
"
```

## Korpus-Schema (`mhdbdb.rnc`)

Für die 667 TEI-kodierten mittelhochdeutschen Texte in `tei/`.

### Dokumentstruktur

```
TEI [@xml:id = Sigle]
  teiHeader
    fileDesc (titleStmt, publicationStmt, sourceDesc)
    encodingDesc (projectDesc, editorialDecl, classDecl)
    profileDesc (langUsage, particDesc)
    revisionDesc
  text > body
    div [@type, @n] (rekursiv)
      p, lg, head, l, ab    — Blockelemente
      w, pc, hi, ...        — Inline-Elemente (auch direkt erlaubt)
```

### Kernelemente

| Element | Attribute | Funktion |
|---------|-----------|----------|
| `<w>` | `@xml:id` (obligatorisch), `@lemmaRef`, `@pos`, `@ana`, `@corresp`, `@reason`, `@xml:lang` | Wort-Token |
| `<pc>` | `@join` (obligatorisch: `left`\|`right`), `@xml:id` | Interpunktion |
| `<div>` | `@type` (optional; Werte: chapter, section, number, song, colophon, recipe, parallel†), `@n` | Textgliederung |
| `<lg>` | `@type` (stanza), `@n` | Strophe (Vers) |
| `<l>` | `@n` | Verszeile |
| `<lb/>` | `@n` | Zeilenumbruch (Prosa) |
| `<hi>` | `@rend` (initial, upper_case_first_letter, ...) | Hervorhebung |

### Wort-Annotationsmuster

```xml
<w xml:id="ABG_101_0"
   lemmaRef="lexicon.xml#lemma_879"
   pos="NOM"
   ana="lexicon.xml#lemma_879_sense_1234"
   corresp="variants.xml#type_5678">brôt</w>
```

- `@lemmaRef` — Verweis auf den Lexikoneintrag (Authority File)
- `@pos`: POS-Tag aus dem MHDBDB-Tagset (kanonisch: [`docs/POS-TAGSET.md`](../docs/POS-TAGSET.md), seit 2026-06-17 die einzige Quelle dafür); zusammengesetzte Tags mit Leerzeichen getrennt (`VEM PRO`)
- `@ana` — Verweis auf Bedeutung/Konzept (semantische Annotation)
- `@corresp` — Verweis auf orthographischen Variantentyp
- `@reason` — Zerlegung bei zusammengesetzten POS-Tags (`wilt+du`)
- Wörter ohne `@lemmaRef` werden vom Korpus-Index übersprungen

### Querverweise zu Authority Files

Querverweise zwischen Korpus- und Authority-Dateien verwenden relative URIs:

```
lexicon.xml#lemma_879              — Lemma-Eintrag
lexicon.xml#lemma_879_sense_1234   — Bedeutung innerhalb eines Lemmas
variants.xml#type_5678             — orthographischer Variantentyp
persons.xml#person_445             — Person
works.xml#work_89                  — Werk
genres.xml#genre_aaa               — Gattungskategorie
```

†`parallel` kennzeichnet Parallelüberlieferung (derselbe Text in verschiedenen Handschriften). Verwendet in 7 Dateien (Stand 2026-08-06): FR3 mit 36 Vorkommen, dazu DL2 und PKP mit je 4, BRW 3, DL1 2, DES2 und DJEM je 1. Die 36 in FR3 sind mit #236 entstanden, als die beim Ingest verlorene Ebene aus dem Legacy-Linecode rekonstruiert wurde.

## Authority-Files-Schema (`mhdbdb-authority.rnc`)

Für die 8 XML-Dateien in `authority-files/`, die als kontrollierte Vokabulare dienen.

| Datei | Inhalt | Body-Struktur |
|-------|--------|---------------|
| `lexicon.xml` | 43.879 Lemmata mit Bedeutungen | `<div>/<entry>` |
| `variants.xml` | 256.760 Wortformen (42.627 Lemma-Gruppen) | `<div>/<entry>/<form>` |
| `persons.xml` | 211 Personen (Autoren, Herausgeber) | `<listPerson>/<person>` |
| `works.xml` | 584 Werke mit bibliographischen Daten | `<listBibl>/<bibl>` |
| `contributors.xml` | 52 MHDBDB-Mitwirkende + 2 Organisationen | `<listOrg>` + `<listPerson>` |
| `concepts.xml` | 567 semantische Konzepte | `<taxonomy>` in `<encodingDesc>` |
| `genres.xml` | 615 Gattungskategorien (hierarchisch) | `<taxonomy>` in `<encodingDesc>` |
| `names.xml` | 90 mittelalterliche Namensformen | `<taxonomy>` in `<encodingDesc>` |

### Identifier-Konventionen

- Personen-IDs: `person_` + Ganzzahl (`person_445`)
- Werk-IDs: `work_` + Ganzzahl (`work_89`)
- Lemma-IDs: `lemma_` + Ganzzahl (`lemma_879`)
- Gattungs-IDs: `genre_` + UUID-Hex (`genre_0480b285`)
- Externe IDs: `<idno type="GND">`, `<idno type="wikidata">`, `<idno type="handschriftencensus">`

## Beispieldateien

Das Verzeichnis `examples/` enthält validierte Beispieldateien für jeden Dokumenttyp:

| Beispiel | Schema | Zeigt |
|----------|--------|-------|
| `corpus.example.tei.xml` | mhdbdb.rnc | Alle Gattungsmuster (Vers, Prosa, Rezept, Lyrik, Predigt, Kolophon) |
| `authority-lexicon.example.xml` | mhdbdb-authority.rnc | Lemma-Einträge mit Bedeutungen |
| `authority-persons.example.xml` | mhdbdb-authority.rnc | Personeneinträge mit Normdaten |
| `authority-works.example.xml` | mhdbdb-authority.rnc | Werkeinträge mit Bibliographie |
| `authority-genres.example.xml` | mhdbdb-authority.rnc | Hierarchische Gattungstaxonomie |
| `authority-concepts.example.xml` | mhdbdb-authority.rnc | Semantische Begriffsontologie |
| `authority-variants.example.xml` | mhdbdb-authority.rnc | Orthographische Variantenzuordnungen |
| `authority-names.example.xml` | mhdbdb-authority.rnc | Mittelalterliche Namensformen |
| `authority-contributors.example.xml` | mhdbdb-authority.rnc | Mitwirkenden-Register (Gründer, Koordination, Editor:innen) |

## Eigene Daten MHDBDB-kompatibel machen

Wenn Sie TEI-Dateien erstellen möchten, die mit den MHDBDB-Werkzeugen funktionieren:

1. **Von einem Beispiel ausgehen** — eine Datei aus `examples/` kopieren und anpassen
2. **Das richtige Schema wählen** — Korpus-Schema für Textdateien, Authority-Schema für Vokabulare
3. **Mindestanforderung** pro `<w>`: `@xml:id` (dateiweit eindeutig) und Textinhalt
4. **Empfohlen**: `@lemmaRef` (ermöglicht Suche), `@pos` (ermöglicht Filterung)
5. **Optional**: `@ana` (semantische Annotation), `@corresp` (Variantenverknüpfung)
6. **Interpunktion**: immer `<pc join="left|right">` verwenden, nie `<seg type="pc">`
7. **Prosa-Zeilenumbrüche**: `<lb/>` verwenden, nie `<l>` (nur für Verse)
8. **Validieren** — gegen `tei_all.rng` und `mhdbdb.rnc` prüfen, bevor die Daten eingereicht werden

### Hinweis zur RNC-Bearbeitung

Die `.rnc`-Dateien sind die Quelldateien. Nach der Bearbeitung muss die `.rng` neu generiert werden:

```bash
python -m rnc2rng schema/mhdbdb.rnc schema/mhdbdb.rng
```

Hinweis: `div` ist ein reserviertes Schlüsselwort in RELAX NG Compact. Das Korpus-Schema verwendet `tei.div` als Pattern-Name für `<div>`-Elemente.

## Warum RELAX NG + Markdown, kein ODD?

Die TEI-Community verwendet traditionell ODD (One Document Does it all) zur Schema-Definition. Wir haben uns bewusst dagegen entschieden:

- **ODD-Toolchain ist de facto unmaintained.** Roma deprecated, RomaJS 50+ offene Issues, `odd2relax` XSLT 1.0 von 2004.
- **RELAX NG ist die eigentliche Validierungssprache.** ODD *generiert* RELAX NG — der direkte Weg eliminiert eine verlustbehaftete Transformation.
- **Markdown-Dokumentation ist LLM-nativ.** In einem Promptotyping-Workflow dienen die Soll-Modell-Docs (`TEI-MODEL.md`) als Kontext für Mensch und LLM. ODD-Prosa ist für keines der beiden Publikum ideal.
- **Standardwerkzeuge genügen.** `pip install lxml rnc2rng` — kein Java/Saxon/TEI-Stylesheets nötig.

## Normative Dokumente

- [TEI-MODEL.md](../docs/TEI-MODEL.md) — Kodierungsmodell für Korpusdateien (Soll-Modell)
- [TEI-MODEL-AUTH-FILES.md](../docs/TEI-MODEL-AUTH-FILES.md) — Kodierungsmodell für Authority Files
- [CONTRACTS.md](../docs/CONTRACTS.md) — Positionszählungsvertrag (Python/JS-Parität)
