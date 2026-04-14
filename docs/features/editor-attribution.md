# Editor-Attribution & Credits-Modell für MHDBDB-TEI-Header

## Context

Katharina hat im Auftrag von Julia und Alan gefragt, ob die digitalen Editor*innen prominenter im TEI-Header sichtbar gemacht werden können. Heute steht in allen 666 `tei/*.tei.xml` exakt das gleiche, kollektive `<respStmt>` ("digitale Zusammenführung, Annotation und semantische Klassifikation — MHDBDB"), und keine einzige Person außer Katharina (`<authority><persName role="coordinator">`) erscheint strukturiert. Die beiden Gründer der MHDBDB (Klaus M. Schmidt, Horst Pütz) tauchen im Header ebenfalls nicht auf.

Konkrete Anforderungen vom User:

1. **Gründer in jeder Datei**: Klaus M. Schmidt + Horst Pütz als Urheber/Gründer der MHDBDB überall im Header.
2. **~50 Personen, die je an Texten gearbeitet haben** sollen sichtbar werden, ohne die Header aufzublähen.
3. **Haupteditor*innen pro Text** sollen prominenter erwähnt werden:
   - Vlastimil Brom bei TKR, TKA, VTC
   - Katrin Woesner bei JT
   - Julia Hintersteiner bei der Wenzelsbibel (`Wenzelsbibel/WZB.tei.xml`) —
     **Achtung:** liegt auf Branch `feature/wenzelsbibel-ingest` (Issue #66),
     noch nicht in `main`. `tei/ZWB.tei.xml` ist "Zweierlei Bettzeug", ein
     anderer Text — nicht verwechseln. Lead-editor-Attribution für Julia
     erfolgt nach Merge von #66 in einem separaten Mini-Commit.
4. **Konvention für neue Ingests** dokumentieren: Klaus + Horst als Gründer (immer), Katharina als Koordinatorin (immer), spezifische Editor*innen je nach realem Stand — *nicht* die volle 50er-Liste.

Vom User in der vorgelagerten Klärung entschieden:

- **Storage:** Hybrid — eine zentrale `authority-files/contributors.xml` mit allen 50+ Personen + minimale Inline-Verweise pro TEI-Datei: Gründer und Koordinatorin in `<publicationStmt>/<authority>` (per `<persName ref="contributors.xml#…">`), kollektiver MHDBDB-Team-Hinweis in `<titleStmt>/<respStmt>` (per `<orgName ref="contributors.xml#mhdbdb-team">`), Lead-Editoren bei den 4 prominenten Texten als zweites `<respStmt>` daneben (per `<name ref="contributors.xml#contrib_…">`).
- **Gründer-Position:** `publicationStmt/authority` (das Schema erlaubt `persName/@role` dort schon).
- **Schema-Followup (`docs/features/032-schema-followup.md`):** Bewusst getrennt — läuft als eigenes Vorhaben, nicht in diesem Plan.

**Erwarteter Outcome nach diesem Plan:**

- Eine neue Authority-Datei `authority-files/contributors.xml` mit 55 Einträgen (53 `<person>` + 2 `<org>`).
- Schema-Erweiterungen in `mhdbdb.rnc` (4 kleine Änderungen) + `mhdbdb-authority.rnc` (neuer Body-Typ).
- Alle 666 TEI-Header migriert (uniform: Gründer + Koordinatorin in `<authority>`, Verweis auf MHDBDB-Team in `<respStmt>`).
- 4 Header (TKR, TKA, VTC, JT) zusätzlich mit text-spezifischer `respStmt` für die Haupteditor*innen. WZB (Wenzelsbibel, Julia Hintersteiner) kommt nach Merge von `feature/wenzelsbibel-ingest` dazu — separates Mini-Ticket.
- TEI-MODEL.md + TEI-MODEL-AUTH-FILES.md + schema/README.md aktualisiert.
- Neue Ingest-Anleitung als Abschnitt in TEI-MODEL.md.
- Validierung: alle Korpus- und Authority-Dateien grün gegen `tei_all.rng` + `mhdbdb.rng` / `mhdbdb-authority.rng` (Baseline heute: 0/666 Fails gegen `mhdbdb.rng`).

**Explizit nicht im Scope:**

- Frontend-Rendering der Editor-Liste (separate Story; Reading-View liest `respStmt` heute nicht).
- GND/ORCID-Lookups für moderne Editor*innen (Felder im Schema vorgesehen, Werte später nachpflegen).
- Schema-Followup #32 (separater Plan in `docs/features/032-schema-followup.md`).
- Die 30 Korpus-Dateien, die gegen `tei_all.rng` failen (siehe `docs/TEI-MODEL.md` §10 für die Kategorien: `@reason`-Attribut auf `<w>`, `<hi>`/`<div>`/`<w>`/`<p>`/`<head>` an unerwarteten Positionen). GAPs 1–11 im Custom-Schema decken sie bewusst ab. Gehören zu #30.
- WZB (Wenzelsbibel) lead-editor-Attribution für Julia Hintersteiner — kommt nach Merge von `feature/wenzelsbibel-ingest` (#66) in einem separaten Mini-Commit, der das Datei-File explizit in `LEAD_EDITORS` ergänzt.

---

## Refinement Notes (Iteration 2 — 2026-04-14)

**Bewusste Designentscheidung: Einmal-Migration, Standalone-Script**

Es gibt bereits ein generisches Sync-Framework `scripts/sync/sync_tei_headers.py` (537 Zeilen, `AuthoritySyncer`-ABC + `WorksSyncer` als Vorbild + TODO-Stubs für Persons/Genres/Concepts). Das wäre eine naheliegende Host-Option, ist aber für diesen Plan **absichtlich nicht gewählt**:

- Der Use-Case ist eine **einmalige** Migration. Gründer und Koordinatorin ändern sich de facto nie; falls Namen in contributors.xml doch mal korrigiert werden, ist contributors.xml via `@ref` die kanonische Quelle — der Inline-Text in den 666 Korpus-Dateien bleibt bewusst eingefroren.
- Ein schlankes Standalone-Script `scripts/migrate-header-credits.py` (konzeptionell analog zu den #32-Migrations-Scripts wie `migrate-person-uuids.py`, die mittlerweile vollständig gelöscht sind, siehe §"Kritische Pfade & Reuse-Hinweise") ist einfacher, nach Ausführung archivierbar, und hat keine Wechselwirkung mit dem Sync-Framework.
- Der Aufwand, `ContributorsSyncer` in ein Framework einzubauen, das per Default Sigle-Matching erwartet (was hier nicht greift), wäre größer als ein direktes Script.

**Cross-Reference zu Schema-Followup P0-4 (gnd → GND)** (nicht Teil dieses Plans, aber Kolleg:in, die P0-4 umsetzt, muss es wissen):

`WorksSyncer` in `scripts/sync/sync_tei_headers.py` schreibt `<idno type="gnd">` **in Lowercase** an drei Stellen:

| Zeile | Code |
|-------|------|
| `scripts/sync/sync_tei_headers.py:196` | `gnd_elem = work.xpath('.//tei:idno[@type="gnd"]', namespaces=TEI_NS)` |
| `scripts/sync/sync_tei_headers.py:204–207` | Mehrzeiliger `extract_id_from_url(...)`-Aufruf; das relevante `'gnd'`-Literal sitzt auf Z. 205 als zweites Argument. |
| `scripts/sync/sync_tei_headers.py:284` | `gnd_idno.set('type', 'gnd')` |

Das ist mit-ursächlich für den gnd/GND-Drift im Korpus, den Schema-Followup P0-4 adressiert. Wer P0-4 umsetzt, muss parallel auch diese drei Zeilen auf `"GND"` umstellen, sonst revertiert der nächste `--works`-Lauf den Drift. **Gehört in den Schema-Followup-Handoff-Doc, nicht in diesen Plan** — dieser Plan schreibt `"GND"` (Uppercase) von Anfang an in contributors.xml und migriert keine works.

---

## Architektur in einem Bild

```
authority-files/contributors.xml        ← NEU
  ├─ <listOrg>
  │   ├─ <org xml:id="mhdbdb-team">     ← Anker für "gesamtes Team"-Verweis
  │   │   <orgName>MHDBDB-Team</orgName>
  │   │   <desc>Alle Mitwirkenden ...</desc>
  │   └─ <org xml:id="dhcraft">         ← Digital Humanities Craft (Org, kein Person-Eintrag)
  │       <orgName>Digital Humanities Craft</orgName>
  └─ <listPerson>
      ├─ <person xml:id="contrib_001" role="founder">     Klaus M. Schmidt
      ├─ <person xml:id="contrib_002" role="founder">     Horst Pütz
      ├─ <person xml:id="contrib_003" role="coordinator"> Katharina Zeppezauer-Wachauer
      ├─ <person xml:id="contrib_004" role="lead-editor"> Vlastimil Brom
      ├─ <person xml:id="contrib_005" role="lead-editor"> Katrin Woesner
      ├─ <person xml:id="contrib_006" role="editor">      Julia Hintersteiner
      │     # role wird nach Merge von #66 zu "lead-editor" (Wenzelsbibel)
      ├─ <person xml:id="contrib_007" role="editor">      Alan van Beek
      └─ ... 46 weitere <person xml:id="contrib_NNN" role="editor"> Einträge

tei/*.tei.xml (alle 666)
  ├─ <publicationStmt>
  │   └─ <authority>                    ← MIGRATION
  │       ├─ <persName role="founder" ref="contributors.xml#contrib_001">Klaus M. Schmidt</persName>
  │       ├─ <persName role="founder" ref="contributors.xml#contrib_002">Horst Pütz</persName>
  │       └─ <persName role="coordinator" ref="contributors.xml#contrib_003">Katharina ...</persName>
  └─ <titleStmt>
      └─ <respStmt>                     ← MIGRATION (uniform)
          <resp>digitale Zusammenführung, Annotation und semantische Klassifikation</resp>
          <orgName ref="contributors.xml#mhdbdb-team">MHDBDB-Team (vollständige Liste in contributors.xml)</orgName>

tei/{TKR,TKA,VTC,JT}.tei.xml             ← ZUSÄTZLICHE respStmt
  └─ <titleStmt>
      └─ <respStmt>                     ← NEU, text-spezifisch
          <resp>Hauptbearbeitung</resp>
          <name role="lead-editor" ref="contributors.xml#contrib_004">Vlastimil Brom</name>

# WZB.tei.xml (Wenzelsbibel) — wird nach Merge von #66 analog zu den 4 oben
# durch einen separaten Mini-Commit ergänzt: contrib_006 (Julia Hintersteiner)
```

---

## Zu erstellende / zu ändernde Dateien

### Neu

| Datei | Inhalt |
|-------|--------|
| `authority-files/contributors.xml` | TEI-Datei mit Standard-teiHeader (analog `persons.xml` aus [schema/mhdbdb-authority.rnc:29-48](../../schema/mhdbdb-authority.rnc#L29-L48)), `<listOrg>` (2 Einträge: `mhdbdb-team` als Gesamtverweis-Anker + `dhcraft`) und `<listPerson>` (53 Einträge). ID-Schema: `contrib_NNN` für Personen (numerisch, beginnt bei 001), Sonder-IDs `mhdbdb-team` und `dhcraft` für die zwei Orgs (analog zur `person_anonym`-Ausnahme in persons.xml — kein `contrib_org_*`-Präfix, weil's nur 2 sind und sie sprechende Namen verdienen). Rollen via `@role` direkt auf `<person>` und `<org>` (nicht via `<note>`). |
| `schema/examples/authority-contributors.example.xml` | Validiert gegen beide Stages, **10 Einträge total: 8 `<person>` + 2 `<org>`**. Personen-Verteilung: 2× `founder`, 1× `coordinator`, 2× `lead-editor`, 3× `editor` (einer davon mit `<idno type="GND">` als Edge-Case-Demo, einer mit `<note>` für Aufgabenbeschreibung, einer minimal). Orgs: `mhdbdb-team` und `dhcraft`. |
| `scripts/migrate-header-credits.py` | Einmal-Migrations-Script. Nach Ausführung + Validation nach `scripts/_archived/` verschoben. Skelett-Code unten in §"Migrationsskript-Skelett". Etablierte lxml-Patterns siehe `scripts/build-corpus-index.py` und `scripts/audit/audit-tei-corpus.py`. |

### Schema-Edits

| Datei | Änderung |
|-------|----------|
| `schema/mhdbdb.rnc:57` | `element respStmt { ... }` → `element respStmt { ... }+` (mehrere respStmt zulassen) |
| `schema/mhdbdb.rnc:59` | `<name>` in respStmt: `attribute role { text }?` ergänzen |
| `schema/mhdbdb.rnc:80` | `element persName { ... }` in `<authority>` → `element persName { ... }+` |
| `schema/mhdbdb.rnc:80` | `persName` zusätzlich `attribute ref { xsd:anyURI }?` ergänzen, damit Inline-Verweis auf `contributors.xml#contrib_NNN` möglich ist. **Typ:** `xsd:anyURI`, konsistent mit dem bereits vorhandenen `<name ref="...">` in `respStmt` (Z. 59) und `<orgName ref="...">` (Z. 60). Permissiv genug für relative URIs wie `contributors.xml#contrib_001`, und gibt zusätzliche Validierung gegen Tippfehler. |
| `schema/mhdbdb-authority.rnc` | (a) Neuer Body-Typ `contributors.body = (listOrg?, contributors.listPerson)`. (b) Authority-`body`-Union (Z. 54–60) um `\| contributors.body` erweitern. (c) **Neues Pattern** `contributors.listPerson` neben dem bestehenden `listPerson` aus persons.xml — eigenes Pattern, damit persons.xml-Constraints (`persName type="preferred"\|"alternative"`, `idno type="GND"\|"wikidata"`) unberührt bleiben. (d) Pattern für `<org>` mit `@xml:id` (Pflicht), `<orgName>+`, optional `<desc>` und `<idno>`. **Kein `@role` auf `<org>`** — das Rollen-Konzept ist nur für `<person>` definiert (siehe Datenfrage §3 für die Begründung). (e) Pattern für `<person>` in contributors.xml hat: `attribute role { "founder" \| "coordinator" \| "lead-editor" \| "editor" }?` direkt auf `<person>` (nicht via `<note>`); `element persName` (Pflicht, mindestens 1, mit optionalem `@xml:lang`); `element idno { attribute type { "GND" \| "ORCID" \| "wikidata" }, text }*` (strukturell vorgesehen, im Bestand initial leer — siehe Datenfrage §4); optional `element note { text }` für freitextliche Aufgabenbeschreibung. |
| `schema/mhdbdb.rng` | Aus geänderter `.rnc` regenerieren (`python -m rnc2rng schema/mhdbdb.rnc schema/mhdbdb.rng`) |
| `schema/mhdbdb-authority.rng` | Analog regenerieren |

### Korpus-Migration (über `python scripts/migrate-header-credits.py`)

| Datei(en) | Änderung | Idempotenz |
|-----------|----------|------------|
| `tei/*.tei.xml` (alle 666) | `<publicationStmt>/<authority>`: bestehenden `coordinator`-Eintrag um zwei `founder`-Einträge ergänzen, `@ref` an alle drei. | Script entfernt erst alle `<persName>` mit `@role in (founder, coordinator)` im `<authority>`-Block, baut dann die drei kanonischen Einträge neu. |
| `tei/*.tei.xml` (alle 666) | `<titleStmt>/<respStmt>`: bestehenden `<resp>` + `<name ref="https://mhdbdb.plus.ac.at">…</name>` durch `<resp>` + `<orgName ref="contributors.xml#mhdbdb-team">…</orgName>` ersetzen. | Script erkennt das Muster (`name/@ref` enthält `mhdbdb.plus.ac.at`) und ersetzt, lässt alle anderen `<respStmt>`-Blöcke unangetastet. |
| `tei/TKR.tei.xml`, `tei/TKA.tei.xml`, `tei/VTC.tei.xml` | Zusätzliche `<respStmt>` mit Vlastimil Brom als `lead-editor`. | Script prüft vorher, ob bereits ein `<respStmt>` mit `name/@ref="contributors.xml#contrib_004"` existiert — falls ja, skip. |
| `tei/JT.tei.xml` | Zusätzliche `<respStmt>` mit Katrin Woesner als `lead-editor`. | dito |
| `Wenzelsbibel/WZB.tei.xml` (deferred) | Zusätzliche `<respStmt>` mit Julia Hintersteiner als `lead-editor`. **Nicht in diesem Plan** — kommt in einem separaten Mini-Commit nach Merge von `feature/wenzelsbibel-ingest` (#66). |

### Dokumentation

| Datei | Änderung |
|-------|----------|
| `docs/TEI-MODEL.md` | Neuer Abschnitt §2.1bis "Editor-Attribution & Credits" zwischen aktueller §2.1 und §2.1a. Erklärt: was geht in `authority`, was in `respStmt`, was in `contributors.xml`. Inkl. Mini-Beispiel. |
| `docs/TEI-MODEL.md` | Neuer Abschnitt §12 "Konventionen für neue Ingests" am Ende, **nach §11 Versionierung** (§9 ist bereits "Ingest-Anforderungen", §10 "Validierungsbaseline", §11 "Versionierung" — die nächste freie Nummer ist §12). Inhalt: Klaus + Horst als Gründer (immer), Katharina als Koordinatorin (immer), text-spezifische Haupteditor*innen je nach realem Stand. Verweis auf `contributors.xml`. **Alternative falls inhaltlich näher zu §9.x:** Erweiterung des bestehenden §9 um einen Unterabschnitt §9.4 "Editor-Attribution & Credits-Pflichten". Wahl liegt bei der/dem Implementierer:in. |
| `docs/TEI-MODEL-AUTH-FILES.md` | Neuer Abschnitt §3.8 "contributors.xml — Mitwirkende-Register". Tabellen-Eintrag in §1 ergänzen (8 Authority-Files statt 7). Schema-Snippet wie bei den anderen 7 Dateien. ID-Konvention `contrib_NNN` in §2.3 ergänzen. |
| `schema/README.md` | Tabelle der Authority-Files (Z.115–123) um `contributors.xml` ergänzen. Examples-Tabelle (Z.135–146) um `authority-contributors.example.xml` ergänzen. |

---

## Migrationsskript-Skelett (`scripts/migrate-header-credits.py`)

Standalone-Script, Einmal-Migration. Idempotent (um Dry-Run + Rerun nach partiellen Fehlern zu erlauben), aber nicht als persistente Infrastruktur gedacht.

```python
#!/usr/bin/env python3
"""Migrate MHDBDB TEI headers to link editor/founder attribution to contributors.xml.

One-shot migration. After successful run + validation, move this script to
scripts/_archived/ analogous to the #32-migration scripts.

Usage:
    python scripts/migrate-header-credits.py --dry-run   # preview
    python scripts/migrate-header-credits.py             # apply
    python scripts/migrate-header-credits.py --sample ABG LZT  # limit to 2 files
"""
import argparse
import glob
import sys
from pathlib import Path
from lxml import etree

TEI_NS_URI = 'http://www.tei-c.org/ns/1.0'
TEI = f'{{{TEI_NS_URI}}}'
NS = {'t': TEI_NS_URI}

CANONICAL_AUTHORITY = [  # global, in jeder Datei
    ('founder',     'contrib_001', 'Klaus M.',  'Schmidt'),
    ('founder',     'contrib_002', 'Horst',     'Pütz'),
    ('coordinator', 'contrib_003', 'Katharina', 'Zeppezauer-Wachauer'),
]

LEAD_EDITORS = {  # Sigle → (contrib_id, full_name)
    'TKR': ('contrib_004', 'Vlastimil Brom'),
    'TKA': ('contrib_004', 'Vlastimil Brom'),
    'VTC': ('contrib_004', 'Vlastimil Brom'),
    'JT':  ('contrib_005', 'Katrin Woesner'),
    # WZB (Wenzelsbibel) → contrib_006 Julia Hintersteiner kommt nach Merge
    # von feature/wenzelsbibel-ingest (#66). NICHT 'ZWB' eintragen —
    # tei/ZWB.tei.xml ist 'Zweierlei Bettzeug', ein anderer Text.
}

def _child_indent(parent):
    """Return the whitespace that should precede a child of `parent`.

    Source-of-truth order:
    1. parent.text — this is the whitespace BEFORE the first child, i.e. always
       the correct child-indent in a pretty-printed file (works even when the
       parent has only one child, where parent[0].tail would give the smaller
       closing-tag indent).
    2. parent[0].tail — only when parent has 2+ children, where the inter-sibling
       whitespace IS the child indent.
    3. Hard-coded fallback if nothing else is available.
    """
    if parent.text and parent.text.strip() == '':
        return parent.text
    if len(parent) >= 2 and parent[0].tail and parent[0].tail.strip() == '':
        return parent[0].tail
    return '\n          '

def _capture_closing_indent(parent):
    """Return the whitespace BEFORE the closing tag of `parent`.

    This is whatever currently sits on the last child's .tail — that's the
    text that immediately precedes `</parent>`. Captured BEFORE any mutation
    so the new last element gets the same closing-tag indent.
    """
    if len(parent):
        return parent[-1].tail or '\n        '
    return parent.text or '\n        '

def migrate_authority(tree):
    """Rebuild publicationStmt/authority with founders + coordinator."""
    auth = tree.find('.//t:publicationStmt/t:authority', NS)
    if auth is None:
        return False
    # Capture indents BEFORE mutating, so we can preserve the closing-tag indent
    child_indent   = _child_indent(auth)
    closing_indent = _capture_closing_indent(auth)
    inner_indent   = child_indent + '  '   # one level deeper, for forename/surname
    # Remove existing founder/coordinator persName children
    for pn in auth.findall(f'{TEI}persName'):
        if pn.get('role') in ('founder', 'coordinator'):
            auth.remove(pn)
    # Append canonical three with proper internal + sibling indentation
    for role, cid, fore, sur in CANONICAL_AUTHORITY:
        pn = etree.SubElement(auth, f'{TEI}persName',
                              role=role, ref=f'contributors.xml#{cid}')
        pn.text = inner_indent
        pn.tail = child_indent
        fn = etree.SubElement(pn, f'{TEI}forename'); fn.text = fore; fn.tail = inner_indent
        sn = etree.SubElement(pn, f'{TEI}surname');  sn.text = sur;  sn.tail = child_indent
    # Restore the original closing-tag indent on the new last child
    if len(auth):
        auth[-1].tail = closing_indent
    return True

def _is_collective_mhdbdb_respstmt(rs):
    """True if this <respStmt> is the legacy collective MHDBDB attribution.

    Generic check: any direct child of <respStmt> with @ref containing
    'mhdbdb.plus.ac.at'. Catches both <name ref="..."> (the dominant pattern)
    and the hypothetical <orgName ref="...">, in case any file deviates.
    """
    for child in rs:
        if 'mhdbdb.plus.ac.at' in (child.get('ref') or ''):
            return True
    return False

def migrate_collective_respstmt(tree):
    """Replace MHDBDB-collective respStmt with orgName link."""
    title_stmt = tree.find('.//t:titleStmt', NS)
    if title_stmt is None:
        return False
    child_indent   = _child_indent(title_stmt)
    closing_indent = _capture_closing_indent(title_stmt)
    inner_indent   = child_indent + '  '
    # Remove ANY existing collective MHDBDB respStmt (name OR orgName variant)
    for rs in list(title_stmt.findall(f'{TEI}respStmt')):
        if _is_collective_mhdbdb_respstmt(rs):
            title_stmt.remove(rs)
    # Idempotency: skip if a migrated version is already present
    for rs in title_stmt.findall(f'{TEI}respStmt'):
        on = rs.find(f'{TEI}orgName')
        if on is not None and 'contributors.xml#mhdbdb-team' in (on.get('ref') or ''):
            return True
    # Append canonical with proper indentation
    rs = etree.SubElement(title_stmt, f'{TEI}respStmt')
    rs.text = inner_indent
    rs.tail = child_indent
    rp = etree.SubElement(rs, f'{TEI}resp')
    rp.text = 'digitale Zusammenführung, Annotation und semantische Klassifikation'
    rp.tail = inner_indent
    on = etree.SubElement(rs, f'{TEI}orgName', ref='contributors.xml#mhdbdb-team')
    on.text = 'MHDBDB-Team (vollständige Liste in contributors.xml)'
    on.tail = child_indent
    if len(title_stmt):
        title_stmt[-1].tail = closing_indent
    return True

def add_lead_editor(tree, sigle):
    """For specific texts, add a dedicated respStmt with the lead editor."""
    if sigle not in LEAD_EDITORS:
        return False
    contrib_id, full_name = LEAD_EDITORS[sigle]
    title_stmt = tree.find('.//t:titleStmt', NS)
    if title_stmt is None:
        return False
    child_indent   = _child_indent(title_stmt)
    closing_indent = _capture_closing_indent(title_stmt)
    inner_indent   = child_indent + '  '
    # Idempotent: skip if already present
    for n in title_stmt.xpath('./t:respStmt/t:name', namespaces=NS):
        if n.get('ref') == f'contributors.xml#{contrib_id}':
            return False
    rs = etree.SubElement(title_stmt, f'{TEI}respStmt')
    rs.text = inner_indent
    rs.tail = child_indent
    rp = etree.SubElement(rs, f'{TEI}resp'); rp.text = 'Hauptbearbeitung'; rp.tail = inner_indent
    name = etree.SubElement(rs, f'{TEI}name',
                            role='lead-editor',
                            ref=f'contributors.xml#{contrib_id}')
    name.text = full_name
    name.tail = child_indent
    if len(title_stmt):
        title_stmt[-1].tail = closing_indent
    return True

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--sample', nargs='+', help='Limit to specified sigles')
    args = p.parse_args()

    files = sorted(Path('tei').glob('*.tei.xml'))
    if args.sample:
        files = [f for f in files if f.stem.replace('.tei', '') in args.sample]

    print(f'Processing {len(files)} files...')
    errs = []
    for f in files:
        sigle = f.stem.replace('.tei', '')
        try:
            tree = etree.parse(str(f))
            ch1 = migrate_authority(tree)
            ch2 = migrate_collective_respstmt(tree)
            ch3 = add_lead_editor(tree, sigle)
            if args.dry_run:
                print(f'  [DRY] {sigle}: auth={ch1} resp={ch2} lead={ch3}')
            else:
                # NO pretty_print=True — that would reformat the entire document
                # whitespace, generating thousands of noise diffs across all 666
                # files. The .text/.tail handling in the migrate_* functions
                # ensures inserted elements blend with the existing indentation.
                # standalone=None matches the P0-4 GND-migration baseline
                # (Commit 61a0b4a1a) so the XML declaration is identical for
                # files that did/didn't have a standalone attribute.
                tree.write(str(f), encoding='UTF-8', xml_declaration=True, standalone=None)
        except Exception as e:
            errs.append((f, str(e)))
            print(f'  [ERR] {sigle}: {e}', file=sys.stderr)
    print(f'Done. {len(errs)} errors.')
    return 1 if errs else 0

if __name__ == '__main__':
    sys.exit(main())
```

**Idempotenz-Garantien:**

- `authority`-Block: Entfernt zuerst alle `persName[@role in (founder, coordinator)]`, baut dann neu. Mehrfach-Ausführung ergibt immer denselben Output.
- Kollektiver `respStmt`: `_is_collective_mhdbdb_respstmt(rs)` erkennt das Alt-Muster generisch via beliebiges Kind mit `@ref` enthaltend `mhdbdb.plus.ac.at` (matcht `<name>` UND hypothetisches `<orgName>`). Zweiter Durchlauf findet das schon migrierte `orgName`-Pattern und skippt.
- Lead-editor `respStmt`: Explizite Check-vor-Insert Logik via `name/@ref` Match.

**Diff-Sauberkeit (kritisch für Reviewability):** Das Script schreibt **ohne** `pretty_print=True`. Begründung: lxml's pretty-printer reformatiert nicht nur die neu eingefügten Elemente, sondern den gesamten Document-Whitespace — bei 666 Dateien wären das tausende Whitespace-Diff-Zeilen pro Datei, der Commit-Diff wäre unreviewbar. Stattdessen managen die `migrate_*`-Funktionen die Whitespace-Mimicry explizit über zwei Helper:

- **`_child_indent(parent)`** liest den korrekten Child-Indent. Quellen-Präferenz: `parent.text` zuerst (das ist garantiert die Whitespace vor dem ersten Kind, also der Child-Indent — funktioniert auch wenn der Parent nur ein Kind hat, was bei `<authority>` der Fall ist), `parent[0].tail` nur als Fallback bei 2+ Kindern, sonst Hardcoded-Default.
- **`_capture_closing_indent(parent)`** snapshottet den Indent vor dem schließenden Tag **bevor** mutiert wird. Das letzte neue Kind bekommt diesen Wert als `.tail` zurück. Diese Lösung ist robust gegen Indent-Stil (2-Space, 4-Space, Tab, gemischt) — keine `[:-2]`-Zeichenarithmetik.

Zusätzlich setzen die Funktionen `.text` und `.tail` auch auf die internen Kinder (`<forename>`/`<surname>` in `<persName>`, `<resp>`/`<orgName>` in `<respStmt>`), damit die neuen Elemente strukturell identisch zu den Bestandselementen formatiert sind. Resultat: der Diff zeigt nur die echten inhaltlichen Änderungen, analog zur P0-4-GND-Migration aus dem #32-Followup, die bitidentische 1-Zeilen-Diffs erzeugt hat.

**Empirisch verifiziert** auf `tei/AC1.tei.xml`: das Script erzeugt eine `<authority>` mit drei korrekt indentierten `<persName>`-Einträgen, jeweils mit `<forename>` und `<surname>` auf eigener Zeile — strukturell identisch zum Original-Katharina-Eintrag.

**Abort-Strategie:** `try/except` pro Datei, Fehler werden gesammelt und am Ende geloggt, Script macht weiter. Rollback auf Commit-Ebene via `git reset --hard HEAD~1`. Bei Bedarf einzelne Dateien via `--sample ABG LZT` testen.

---

## Reihenfolge & Commit-Struktur

```
Commit 1  contributors.xml + Authority-Schema
          → authority-files/contributors.xml (55 Einträge gesamt: 53 <person>
            (contrib_001..006 = die im Plan genannten Rolleninhaber:innen
            Schmidt, Pütz, Zeppezauer-Wachauer, Brom, Woesner, Hintersteiner;
            contrib_007 = van Beek; contrib_008..053 = die übrigen 46 Namen
            aus Katharinas Liste, chronologisch in deren Reihenfolge —
            inkl. Manuel Schwembacher als regulärer editor-Eintrag) + 2 <org>
            (mhdbdb-team, dhcraft))
          → schema/mhdbdb-authority.rnc (neuer Body-Typ contributors.body,
            neues Pattern contributors.listPerson)
          → schema/mhdbdb-authority.rng (regeneriert via rnc2rng)
          → schema/examples/authority-contributors.example.xml (10 Einträge
            total: 8 <person> mit allen Rollen + 2 <org>-Einträge)
          Validierung:
            (a) contributors.xml grün gegen tei_all.rng + mhdbdb-authority.rng
            (b) Example grün gegen beide Stages
            (c) Andere 7 Authority-Files bleiben grün (additive Schema-Änderung)

Commit 2  Korpus-Schema für Mehrfach-respStmt und role/ref erweitern
          → schema/mhdbdb.rnc (4 Edits, siehe Tabelle oben)
          → schema/mhdbdb.rng (regeneriert)
          Validierung: alle 8 Examples grün, Baseline gegen Bestand unverändert
            (0 zusätzliche mhdbdb-Fails erwartet — Änderungen sind additiv).

Commit 3  Migrations-Script + Dry-Run auf 5-Datei-Sample
          → scripts/migrate-header-credits.py (neues Standalone-Script)
          KEINE tei/ Änderung in diesem Commit — nur die Script-Datei.
          Validierung vor dem Commit:
            python scripts/migrate-header-credits.py --sample ABG LZT WUT BRW AK --dry-run
          Erwarteter Output pro Sample-Datei:
            [DRY] ABG: auth=True resp=True lead=False
          Anschließend ohne --dry-run auf dasselbe Sample, Diff visuell prüfen.
          git restore tei/ABG.tei.xml etc., bevor Commit 4 startet (Sample verwerfen).

Commit 4  Header-Migration: 666 Korpus-Dateien (ohne Lead-Editor-respStmts)
          Zwischenschritt für saubere Diff-Lesbarkeit:
            1. LEAD_EDITORS temporär leer machen (1 Zeile im Script)
            2. python scripts/migrate-header-credits.py --dry-run  (Überprüfung)
            3. python scripts/migrate-header-credits.py
            4. git add tei/*.tei.xml  (alle 666 Änderungen zählen)
          → Alle 666 Dateien zeigen Diffs (authority-Rebuild + kollektive
            respStmt-Ersetzung). Die 4 Lead-Editor-Dateien (TKR, TKA, VTC, JT)
            bekommen in Commit 5 zusätzlich ein text-spezifisches respStmt;
            in Commit 4 sind sie nicht von den anderen 662 zu unterscheiden.
          Validierung: volle Zwei-Stufen-Validierung
            (a) 0 Fails gegen mhdbdb.rng (Baseline gehalten)
            (b) max. 30 Fails gegen tei_all.rng (Baseline gehalten)
          Spot-Check: 5 Header (ABG, LZT, WUT, BRW, AK) visuell prüfen.

Commit 5  Lead-Editor-respStmt für TKR/TKA/VTC/JT
          LEAD_EDITORS-Block im Script restaurieren, nochmal laufen lassen
          (idempotent: authority + kollektive respStmt werden nicht erneut angefasst,
          nur die 4 Lead-Editor-Zeilen kommen hinzu).
          Validierung: nur die 4 Dateien zeigen zusätzlichen Diff.
          Spot-Check: TKR, JT visuell prüfen.

          ALTERNATIV: Commit 4 und 5 zu einem Commit verschmelzen wenn
          Diff-Split-Aufwand > Diff-Lesbarkeits-Gewinn. Empfehlung des Plans:
          zwei Commits, weil Lead-Editor fachlich eine andere Aussage ist
          (Person statt Team).

Commit 6  Dokumentation
          → docs/TEI-MODEL.md (§2.1bis "Editor-Attribution & Credits" + §12
            "Konventionen für neue Ingests" — siehe Doku-Tabelle für die
            Alternative §9.4 als Unterabschnitt des bestehenden §9)
          → docs/TEI-MODEL-AUTH-FILES.md (§1 Tabelle auf 8 Dateien, §2.3 ID-Tabelle
            um contrib_NNN erweitern, §3.8 neu: contributors.xml Schema-Doku)
          → schema/README.md (Authority-Files-Tabelle + Examples-Tabelle)

Commit 7  Script archivieren
          → git mv scripts/migrate-header-credits.py scripts/_archived/
          (analog zur #32-Migration nach Phases F-K)
```

---

## Verifikationsprotokoll

**Dry-Run-Zwang:** Vor jedem realen Lauf Pflicht. Das Script unterstützt `--dry-run` und `--sample`:

```bash
# Schritt A: Sample-Dry-Run (5 Dateien, keine Schreibzugriffe)
python scripts/migrate-header-credits.py --sample ABG LZT WUT BRW AK --dry-run

# Schritt B: Sample real, visueller Diff-Check
python scripts/migrate-header-credits.py --sample ABG LZT WUT BRW AK
git diff tei/ABG.tei.xml

# Schritt C: Wenn Sample ok — reverten und vollen Lauf starten
git restore tei/ABG.tei.xml tei/LZT.tei.xml tei/WUT.tei.xml tei/BRW.tei.xml tei/AK.tei.xml
python scripts/migrate-header-credits.py --dry-run     # nochmal dry-run für alle 666
python scripts/migrate-header-credits.py               # realer Lauf
git status --short tei/ | wc -l                         # sollte ~666 sein
```

**Nach jedem Commit (außer #6 und #7):**

```bash
# 0) tei_all.rng vorhanden? (gitignored, einmaliger Download nötig)
test -f schema/tei_all.rng || curl -sL "https://tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" -o schema/tei_all.rng

# 1) RNG aus RNC regenerieren wenn .rnc geändert
python -m rnc2rng schema/mhdbdb.rnc           schema/mhdbdb.rng
python -m rnc2rng schema/mhdbdb-authority.rnc schema/mhdbdb-authority.rng

# 2) Alle Authority-Files grün
python -c "
from lxml import etree
import os
tei_all = etree.RelaxNG(etree.parse('schema/tei_all.rng'))
auth    = etree.RelaxNG(etree.parse('schema/mhdbdb-authority.rng'))
for f in sorted(os.listdir('authority-files')):
    if not f.endswith('.xml'): continue
    t = etree.parse(f'authority-files/{f}')
    a = tei_all.validate(t); b = auth.validate(t)
    print(f'{f}: tei_all={a} auth={b}')
    if not (a and b): print(f'  err: {auth.error_log if not b else tei_all.error_log}')
"

# 3) Alle Examples grün
python -c "
from lxml import etree
import os
tei_all = etree.RelaxNG(etree.parse('schema/tei_all.rng'))
mhdbdb  = etree.RelaxNG(etree.parse('schema/mhdbdb.rng'))
auth    = etree.RelaxNG(etree.parse('schema/mhdbdb-authority.rng'))
for f in sorted(os.listdir('schema/examples')):
    t = etree.parse(f'schema/examples/{f}')
    s2 = mhdbdb if 'corpus' in f else auth
    print(f, tei_all.validate(t), s2.validate(t))
"

# 4) Volle Korpus-Validierung — nach Commit 3 und 4 Pflicht
python -c "
from lxml import etree
import glob
tei_all = etree.RelaxNG(etree.parse('schema/tei_all.rng'))
mhdbdb  = etree.RelaxNG(etree.parse('schema/mhdbdb.rng'))
fails_t, fails_m = [], []
for f in sorted(glob.glob('tei/*.tei.xml')):
    t = etree.parse(f)
    if not tei_all.validate(t): fails_t.append(f)
    if not mhdbdb.validate(t):  fails_m.append(f)
print(f'tei_all fails: {len(fails_t)}  (Baseline: 30)')
print(f'mhdbdb fails:  {len(fails_m)}  (Baseline: 0)')
assert len(fails_m) == 0, 'mhdbdb regression!'
# Baseline 30 aus docs/TEI-MODEL.md §10 (Stand 2026-04-14, post-#32-followup).
# Bei Anpassung dort synchron halten — Assertion verhindert REGRESSION,
# nicht FORTSCHRITT (falls #30 Dateien fixt, sinkt die Zahl, das ist gut).
assert len(fails_t) <= 30, 'tei_all regression!'
"
```

**Visuelle Spot-Checks nach Commit 3 + 4:**

```bash
# Helper-Funktion: gibt fileDesc des angegebenen Sigles aus
print_header() {
  python -c "
from lxml import etree
t = etree.parse('tei/$1.tei.xml')
ns = {'t':'http://www.tei-c.org/ns/1.0'}
print(etree.tostring(t.find('.//t:teiHeader/t:fileDesc', ns), pretty_print=True).decode())
"
}

# Header der 5 zufälligen Sample-Dateien (für Commit 4)
for sigle in ABG LZT WUT BRW AK; do
  echo "=== $sigle"
  print_header "$sigle"
done

# Lead-Editor-Dateien (für Commit 5)
for sigle in TKR TKA VTC JT; do
  echo "=== $sigle"
  print_header "$sigle"
done
```

---

## Datenfragen (vor / während Commit 1 zu klären)

1. **Vollständige Liste der 53 Personen** ist im Klartext vom User vorhanden:
   - Klaus M. Schmidt (Gründer)
   - Horst Pütz (Gründer)
   - Katharina Zeppezauer-Wachauer (Koordinatorin)
   - + die 50 Namen aus der Mail (Barbara Aitenbichler ... Katrin Woesner)

   Zu klären: Ist die 50er-Liste komplett, oder gibt es Personen, die noch ergänzt werden müssen?

   **ID-Vergabe-Regel (verbindlich):**
   - **contrib_001..006 = Fest-Slots nach Funktion**, in dieser Reihenfolge:
     001=Schmidt (founder), 002=Pütz (founder), 003=Zeppezauer-Wachauer (coordinator),
     004=Brom (lead-editor), 005=Woesner (lead-editor), 006=Hintersteiner
     (initial role=editor, wird nach #66-Merge zu lead-editor).
   - **contrib_007..053 = chronologisch in der Reihenfolge**, in der die übrigen 47
     Namen in Katharinas E-Mail-Liste auftauchen (also wie sie ihr im Original-Dokument
     erscheinen, NICHT alphabetisch). Begründung: stabile IDs auch wenn jemand
     ergänzt wird — neue Einträge bekommen die nächste freie Nummer ans Ende, niemand
     verschiebt sich.
   - **Visuelle Reihenfolge in `contributors.xml`:** identisch zur ID-Reihenfolge
     (also `contrib_001` zuerst, `contrib_053` zuletzt). Keine alphabetische
     Sortierung — IDs und Reihenfolge sind synchron, das macht Diff-Reviews einfacher.

2. **Rollen-Mapping pro Person:** Aktuell weiß ich nur:
   - `founder`: Schmidt, Pütz
   - `coordinator`: Zeppezauer-Wachauer
   - `lead-editor`: Brom (TKR/TKA/VTC), Woesner (JT). Hintersteiner (Wenzelsbibel/WZB) folgt nach Merge von #66 in einem separaten Mini-Commit; im aktuellen Plan ist sie als `editor` modelliert.
   - `editor` (default für alle anderen): die übrigen ~47 Personen aus der Liste, plus Hintersteiner bis WZB-Merge

   Zu klären: Soll es feinere Rollen geben (z.B. `transcriber`, `annotator`, `developer`, `reviewer`)? **Vorschlag:** Nein — Rollen knapp halten (`founder`, `coordinator`, `lead-editor`, `editor`). Detaillierte Aufgabe gehört in `<note>` innerhalb des `<person>`-Eintrags, nicht in `@role`.

3. **Digital Humanities Craft** ist in der Liste eine Organisation, kein Individuum. → `<org xml:id="dhcraft">` neben den `<person>`-Einträgen, nicht als Person modelliert. Schema-Pattern erlaubt das (`listOrg` parallel zu `listPerson` im Body von contributors.xml). **Konvention für Org-IDs:** Sprechende Sonder-IDs (`mhdbdb-team`, `dhcraft`) statt `contrib_org_*`-Präfix — analog zu `person_anonym` in persons.xml. Begründung: nur 2 Orgs, beide haben kanonische Kurznamen, ein Präfix wäre Bürokratie ohne Nutzen.

4. **GND/ORCID-IDs** für moderne Editor*innen sind heute nicht bekannt. **Vorschlag:** `<idno>`-Elemente strukturell zulassen (`type="GND" | "ORCID" | "wikidata"`) aber alle Einträge ohne idno anlegen. Spätere Anreicherung als separates Mini-Ticket.

5. **Was passiert mit existierenden `<person>`-Einträgen in `<particDesc>/<listPerson>`?** Die enthalten heute nur die mhd. Autoren mit `corresp="persons.xml#person_N"`. **Vorschlag:** Unverändert lassen — `particDesc` ist semantisch für "Personen, über die der Text spricht", nicht für "Personen, die den Text bearbeitet haben". Editor*innen gehören in `respStmt` und `authority`. Keine Vermischung.

---

## Aufwandsschätzung

| Phase | Aufwand | Risiko |
|-------|--------:|--------|
| Commit 1: contributors.xml + Authority-Schema | 1.5 h (Datenerfassung 53 Personen + 2 Orgs dauert am längsten) | niedrig (additiv) |
| Commit 2: Korpus-Schema-Erweiterungen | 30 min | niedrig (additiv) |
| Commit 3: migrate-header-credits.py + Sample-Test | 1 h (Script-Entwicklung + Sample-Validation) | niedrig (nur Script, keine Massenänderung) |
| Commit 4: Header-Migration 666 Dateien | 30 min | mittel (Bestand wird angefasst — aber idempotent, `--dry-run` vorher, revertbar via `git reset`) |
| Commit 5: Lead-Editor-respStmts für 4 Dateien | 10 min | niedrig |
| Commit 6: Dokumentation | 1 h | keins |
| Commit 7: Script archivieren | 5 min | keins |

**Gesamt:** ~5 h Arbeit. Kann an einem Vormittag durchgezogen werden. Komplett reversibel (alles in Git, kein externer State).

---

## Kritische Pfade & Reuse-Hinweise

**Script-Vorlage:** Das Skript-Skelett oben enthält bereits den vollständigen Code. Falls weitere Inspiration nötig: `scripts/build-corpus-index.py` und `scripts/audit/audit-tei-corpus.py` zeigen die im Repo etablierten Patterns (lxml, Namespace-Konstanten, `Path('tei').glob`, Argparse). Die historischen #32-Migrations-Scripts (`migrate-person-uuids.py`, `normalize-work-genres.py`) wurden nach Abschluss von #32 **vollständig gelöscht** (Commit `9cb192c51`) — wer sie als Referenz braucht, kann sie via `git show 9cb192c51^:scripts/data-wrangling/tei-model/migrate-person-uuids.py` aus der Historie ziehen. **Wichtig:** Die hier neue Funktion ist die `_tail_for(parent)`-Indentation-Mimicry, weil dieses Script Elemente einfügt (im Gegensatz zu den #32-Migrationen, die meist nur Attribute renamen oder Elemente entfernen).

**Schema-Erweiterungen:** Die Struktur des bestehenden `listPerson`-Patterns in `schema/mhdbdb-authority.rnc` (Z.117–131) ist die Vorlage, **aber nicht direkt wiederverwendbar**: persons.xml hat Constraints (`persName type="preferred"|"alternative"`, `idno type="GND"|"wikidata"`), die für contributors.xml zu eng wären. Daher ein **eigenes Pattern** `contributors.listPerson` neben dem bestehenden, beide unter dem gemeinsamen `authority.body`-Union (`contributors.body = (listOrg?, contributors.listPerson)`). Rollen via `@role` direkt auf `<person>` (nicht via `<note type="role">` — einfacher, TEI-idiomatisch, konsistent mit dem bestehenden `<authority>/<persName role="coordinator">`-Pattern im Korpus). **Wichtig:** `@role` ist nur für `<person>` definiert, **nicht** für `<org>` — die zwei Orgs (`mhdbdb-team`, `dhcraft`) haben keine vergleichbare Funktionsrolle in einem Editor-Schema.

**Konventionen-Anleitung:** Format orientiert sich an `docs/TEI-MODEL.md` §2.1 (Header-Template mit Inline-XML-Blöcken und Pflicht-Regel-Liste).

**Dateien, die NICHT angefasst werden:**
- `assets/js/**` — kein Frontend-Rendering in diesem Plan.
- `scripts/build-authority-index.py` — contributors.xml bewusst NICHT in den Authority-Index aufnehmen; das ist eine separate Story, sobald das Frontend Editor*innen darstellen will.
- `authority-files/persons.xml` — bleibt strikt für mhd. Textautoren.
- `scripts/sync/sync_tei_headers.py` — das generische Sync-Framework wird für diese Einmal-Migration nicht erweitert (siehe „Refinement Notes"). Die `WorksSyncer`-Zeilen 196/205/284 mit `gnd` lowercase sind ein separates Problem (Schema-Followup P0-4) und werden in diesem Plan nicht angefasst.
- Die 30 Korpus-Dateien, die gegen `tei_all.rng` failen — gehören zu #30. Siehe `docs/TEI-MODEL.md` §10 (Validierungsbaseline) für die strukturierte Auflistung der betroffenen Dateien und Fehler-Kategorien.

---

## Post-#66 WZB-Mini-Commit (deferred work)

Nachdem `feature/wenzelsbibel-ingest` (Issue #66) in `main` gemerged ist und `Wenzelsbibel/WZB.tei.xml` (oder seine endgültige Position im Korpus) vorhanden ist, kommt der WZB-Lead-Editor-Eintrag in einem **separaten Mini-Commit**. Schritte für den dann zuständigen Implementierer (kann jemand anderes sein als der/die Hauptautor:in dieses Plans):

1. **`contributors.xml` aktualisieren:** `contrib_006`-Eintrag von `<person xml:id="contrib_006" role="editor">` auf `role="lead-editor"` ändern. Single-line edit.
2. **WZB-Datei finden:** Nach #66-Merge prüfen, wo die Datei landet (`tei/WZB.tei.xml` oder `Wenzelsbibel/WZB.tei.xml`). Pfad merken.
3. **Lead-Editor-respStmt anhängen:** Falls `migrate-header-credits.py` noch in `scripts/` liegt: `LEAD_EDITORS`-Dict um `'WZB': ('contrib_006', 'Julia Hintersteiner')` ergänzen (mit korrekter Pfad-Anpassung in `main()` falls die Datei nicht in `tei/` liegt) und `python scripts/migrate-header-credits.py --sample WZB` laufen lassen. Falls das Script bereits in `scripts/_archived/` ist: Den entsprechenden `<respStmt>`-Block manuell in den `<titleStmt>` von WZB einfügen, analog zu TKR/TKA/VTC/JT.
4. **Validierung:** WZB-Datei gegen `tei_all.rng` und `mhdbdb.rng` (Stage 1+2). `contributors.xml` gegen beide Stages. Examples bleiben grün.
5. **Commit:** Eine einzige Message:
   ```
   #66-followup: WZB lead-editor attribution für Julia Hintersteiner

   - contributors.xml: contrib_006 role editor → lead-editor
   - WZB.tei.xml: zusätzlicher <respStmt> mit Hintersteiner als lead-editor
   - Validierung: WZB grün gegen tei_all + mhdbdb, contributors.xml grün
   ```

**Begründung für die Aufschiebung:** WZB existiert aktuell nur auf einem Feature-Branch. Wenn dieser Plan parallel ausgeführt wird, hätte das Migrationsscript keine Datei zum Bearbeiten. Der Mini-Commit nach Merge ist der saubere Weg, ohne diesen Plan vom #66-Merge-Zeitpunkt abhängig zu machen.

---

## Definition of Done

- [ ] `authority-files/contributors.xml` existiert, validiert gegen tei_all + mhdbdb-authority, enthält 55 Einträge: 53 `<person>` (contrib_001..006 = Schmidt, Pütz, Zeppezauer-Wachauer, Brom, Woesner, Hintersteiner; contrib_007..053 = van Beek + 46 weitere Editor:innen aus Katharinas Liste in chronologischer Reihenfolge) + 2 `<org>` (`mhdbdb-team`, `dhcraft`).
- [ ] `schema/examples/authority-contributors.example.xml` existiert und validiert grün.
- [ ] `schema/mhdbdb.rnc` + `mhdbdb-authority.rnc` aktualisiert, RNG regeneriert, Examples + Authority-Files weiterhin grün.
- [ ] `scripts/migrate-header-credits.py` existiert und hat `--dry-run` + `--sample` Flags.
- [ ] `migrate-header-credits.py --sample ABG LZT WUT BRW AK --dry-run` läuft sauber durch.
- [ ] Alle 666 `tei/*.tei.xml` haben in `<authority>` drei `<persName>`-Einträge (2× founder, 1× coordinator) mit `@ref` auf contributors.xml.
- [ ] Alle 666 `tei/*.tei.xml` haben einen `<respStmt>` mit `<orgName ref="contributors.xml#mhdbdb-team">`.
- [ ] `tei/{TKR,TKA,VTC,JT}.tei.xml` haben zusätzlich einen `<respStmt>` mit `<name role="lead-editor" ref="contributors.xml#contrib_…">`. (`Wenzelsbibel/WZB.tei.xml` für Julia Hintersteiner kommt nach Merge von #66 in einem separaten Mini-Commit — nicht Teil dieses Plans.)
- [ ] Volle Korpus-Validierung: 0 Fails gegen `mhdbdb.rng`, max. 30 Fails gegen `tei_all.rng` (Baseline gehalten).
- [ ] `docs/TEI-MODEL.md` hat den neuen §2.1bis und §12 Abschnitt (oder §9.4 als Unterabschnitt des bestehenden §9, je nach gewählter Variante aus der Doku-Tabelle).
- [ ] `docs/TEI-MODEL-AUTH-FILES.md` listet contributors.xml in §1, §2.3 und neu §3.8.
- [ ] `schema/README.md` Tabellen aktualisiert.
- [ ] User hat 5 Spot-Check-Header visuell abgenommen.
- [ ] `scripts/migrate-header-credits.py` wurde nach `scripts/_archived/` verschoben.
- [ ] **WorksSyncer-Drift-Audit gelaufen:** `git grep "type=.gnd." scripts/sync/sync_tei_headers.py` zeigt das aktuelle Status-Snapshot. Erwartung nach P0-4 (Commit `61a0b4a1a`): leer. Tatsächlich: drei Treffer auf Z. 196/205/284, weil P0-4 nur das Korpus, nicht den Sync-Code gefixt hat.
- [ ] **WorksSyncer-Drift fixiert ODER explizit getrackt:** Falls das Audit oben Treffer findet, ENTWEDER (a) die drei Stellen in einem Pre-Commit-0 (vor Commit 1 dieses Plans) auf `'GND'` umstellen — der Edit ist trivial und unabhängig vom Rest dieses Plans —, ODER (b) ein neues Followup-Item P0-5 in `docs/features/032-schema-followup.md` mit eindeutiger Owner-Zuordnung aufnehmen. Nicht "TODO" als schwebendes Wissen lassen — ohne einen dieser zwei Schritte revertiert der nächste `--works`-Lauf den P0-4-Drift sofort.
