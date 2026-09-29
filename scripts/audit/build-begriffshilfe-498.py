#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#498: Begriffshilfe als Markdown-Datei zum Hochladen in eine KI erzeugen.

Die Datei enthaelt einen festen Arbeitsauftrag, das Thema aus "Meine Suche" und
das vollstaendige Begriffssystem aus concepts.xml. Die Seite analysiert nichts;
die Begriffswahl macht die externe KI. Grundlage ist KZWs Generator vom
29.09.2026 (Leser, Escaping und Rueckvalidierung stammen von dort).

Drei Varianten, jede aendert genau eine Sache gegenueber der vorigen, damit ein
Test zeigt, was welche Aenderung bringt:

  A    KZWs Datei. Mit --date 29.09.2026 byte-identisch zu ihrer Fassung.
  A2   A plus ein Satz im Vorgehen: auch Taetigkeiten, soziale Funktionen und
       Anwendungskontexte beruecksichtigen (KZW, 29.09.2026).
  B    A2 plus Angaben aus lexicon.xml und dem Korpus je Begriff: Zahl der
       Bedeutungen und Lemmata, haeufigste Lemmata, haeufigste Mitbegriffe.

## Messvorschrift fuer B

**Bedeutungen und Lemmata je Begriff zaehlen nur direkte Zuordnungen**: ein
<sense> in lexicon.xml mit ptr auf den Begriff, Unterbegriffe nicht
eingerechnet. Lemmata sind entry/@xml:id, nicht die Schreibung, wie im
Begriffe-Explorer (conceptToLemmas in build-authority-index.py).

**Belege sind die <w> im Korpus, deren @ana auf die Bedeutung zeigt**
(count_tokens aus measure-498-concept-cross-sections.py). Ein <w> mit zwei
Bedeutungen desselben Lemmas zaehlt fuer das Lemma zweimal.

**Mitbegriffe eines Begriffs C** sind die anderen Begriffe an C-Bedeutungen,
gezaehlt in Bedeutungen. Vorfahren und Nachfahren von C ueber broader sind
ausgeschlossen, sonst stuende ueberall der eigene Oberbegriff oben. Nur fuer
Begriffe mit mindestens --min-senses Bedeutungen, weil kleine Begriffe damit
Rauschen liefern.

Usage:
    python scripts/audit/build-begriffshilfe-498.py --variant A --date 29.09.2026
    python scripts/audit/build-begriffshilfe-498.py --variant B --topic Neugier
"""
import argparse
import hashlib
import html
import importlib.util
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONCEPTS_REL = 'authority-files/concepts.xml'
LEXICON_REL = 'authority-files/lexicon.xml'
NS = {'t': 'http://www.tei-c.org/ns/1.0'}
XML = '{http://www.w3.org/XML/1998/namespace}'

DEFAULT_TOPIC = 'Wachsamkeit'
DEFAULT_SCOPE = 'Keine. Zeige zunächst unterschiedliche mögliche Zugänge.'

A2_SENTENCE = (' Berücksichtige bei der Auswahl neben bedeutungsnahen Begriffen auch mögliche '
               'Tätigkeiten, soziale Funktionen und Anwendungskontexte. Kennzeichne diese als '
               'kontextabhängige Suchwege.')


def fail(msg):
    raise SystemExit(f'FEHLER: {msg}')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=PROJECT_ROOT, text=True).strip()


def source_commit(paths):
    """Letzter Commit, der eine der Quellen geaendert hat. Nicht HEAD: sonst
    aendert jeder fremde Commit die Datei, ohne dass sich ihr Inhalt aendert."""
    dirty = git('status', '--porcelain', '--', *paths)
    if dirty:
        fail(f'uncommittete Aenderungen an den Quellen, Hash und Commit passten nicht zusammen:\n{dirty}')
    return git('log', '-1', '--format=%H', '--', *paths)


# ---------------------------------------------------------------- Begriffe (KZW)

def load_concepts(raw):
    records = []
    for category in ET.fromstring(raw).findall('.//t:category', NS):
        desc = category.find('t:catDesc', NS)
        record = {'id': category.get(XML + 'id'), 'de': [], 'alt_de': [], 'en': [], 'alt_en': [], 'parents': []}
        for term in desc.findall('t:term', NS):
            lang, kind = term.get(XML + 'lang'), term.get('type')
            if lang not in ('de', 'en') or kind not in (None, 'alternative'):
                fail(f'{record["id"]}: unbekannte Benennung lang={lang} type={kind}')
            text = ' '.join(''.join(term.itertext()).split())
            if ';' in text:
                fail(f'{record["id"]}: Semikolon in "{text}" kollidiert mit dem Zellentrenner')
            record[('alt_' if kind == 'alternative' else '') + lang].append(text)
        for ptr in desc.findall('t:ptr', NS):
            if ptr.get('type') != 'broader':
                fail(f'{record["id"]}: ptr type={ptr.get("type")}')
            record['parents'].append(ptr.get('target').removeprefix('#'))
        if len(record['de']) != 1 or len(record['en']) != 1:
            fail(f'{record["id"]}: nicht genau ein Hauptname je Sprache')
        records.append(record)
    ids = {r['id'] for r in records}
    if len(ids) != len(records):
        fail('doppelte Begriffs-IDs')
    for r in records:
        for p in r['parents']:
            if p not in ids or p == r['id']:
                fail(f'{r["id"]}: Oberbegriff {p} fehlt oder ist der Begriff selbst')
    return records


def de_num(n):
    return f'{n:,}'.replace(',', '.')


def cell(value):
    if isinstance(value, list):
        value = '; '.join(value)
    return html.escape(value, quote=False).replace('|', '&#124;')


# ---------------------------------------------------------------- Angaben fuer B

def load_measure_module():
    """Die Zaehlfunktionen aus dem Messskript statt einer zweiten Fassung.
    Der Import wickelt sys.stdout auf UTF-8 um; das ist hier erwuenscht."""
    path = PROJECT_ROOT / 'scripts' / 'audit' / 'measure-498-concept-cross-sections.py'
    spec = importlib.util.spec_from_file_location('measure498', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_lexicon(raw, concept_ids):
    """{sense: frozenset(Begriffe)}, {sense: Lemma-ID}, {Lemma-ID: Schreibung}."""
    concepts_of, lemma_of, orth_of = {}, {}, {}
    for entry in ET.fromstring(raw).iter('{http://www.tei-c.org/ns/1.0}entry'):
        lid = entry.get(XML + 'id')
        orth_of[lid] = entry.findtext('t:form/t:orth', default='?', namespaces=NS)
        for sense in entry.findall('t:sense', NS):
            sid = sense.get(XML + 'id')
            if sid in concepts_of:
                fail(f'doppelte sense-ID {sid}')
            cs = frozenset(p.get('target').split('#')[-1] for p in sense.findall('t:ptr', NS))
            unknown = cs - concept_ids
            if unknown:
                fail(f'{sid}: Begriff(e) nicht in concepts.xml: {sorted(unknown)}')
            concepts_of[sid], lemma_of[sid] = cs, lid
    return concepts_of, lemma_of, orth_of


def enrich(records, concepts_of, lemma_of, orth_of, tokens, ancestors, top, co_top, min_senses):
    names = {r['id']: r['de'][0] for r in records}
    parents = {r['id']: set(r['parents']) for r in records}
    senses_of = defaultdict(list)
    for s, cs in concepts_of.items():
        for c in cs:
            senses_of[c].append(s)
    anc = {c: ancestors(c, parents) for c in names}
    extra = {}
    for c in names:
        ss = senses_of.get(c, [])
        lemma_tok = Counter()
        for s in ss:
            lemma_tok[lemma_of[s]] += tokens[s]
        belegt = [l for l in lemma_tok if lemma_tok[l] > 0]
        top_lemmata = sorted(belegt, key=lambda l: (-lemma_tok[l], orth_of[l], l))[:top]
        co = []
        if len(ss) >= min_senses:
            cnt = Counter(d for s in ss for d in concepts_of[s]
                          if d != c and d not in anc[c] and c not in anc[d])
            for d in sorted(cnt, key=lambda d: (-cnt[d], d))[:co_top]:
                co.append(f'{names[d]} ({d}, {cnt[d]} von {len(ss)})')
        extra[c] = {
            'senses': str(len(ss)),
            'lemmata': str(len(lemma_tok)),
            'top_lemmata': [f'{orth_of[l]} ({lemma_tok[l]})' for l in top_lemmata],
            'co': co,
        }
    return extra


# ---------------------------------------------------------------- Text

INTRO_HEAD = '''# MHDBDB: passende Begriffe für mein Thema finden

## Für die Person, die diese Datei verwendet

Lade diese vollständige Datei als Anhang in einen neuen KI-Chat hoch und schreibe dazu: „Bitte bearbeite den Arbeitsauftrag in der Datei.“

Für ein anderes Thema ändere nur die beiden Angaben unter „Meine Suche“. Die Begriffsliste bleibt gleich. Du brauchst dafür keine Programmierkenntnisse und keine weiteren Dateien.

## Meine Suche

- **Suchbegriff oder kurze Themenbeschreibung:** {topic}
- **Optionale Eingrenzung:** {scope}

## Arbeitsauftrag an die KI

Hilf mir, für meine Suche passende Einstiegspunkte im Begriffssystem der Mittelhochdeutschen Begriffsdatenbank (MHDBDB) zu finden. Ich möchte wissen, welche vorhandenen Begriffe ich als Nächstes nachschlagen sollte. Antworte auf Deutsch und verständlich für jemanden ohne technische Vorkenntnisse.

Nutze die vollständige Begriffsliste am Ende dieser Datei als verbindliche Quelle für vorhandene Einträge, IDs, Benennungen und Oberbegriffsbeziehungen. Dein allgemeines Sprachwissen darf helfen, Verbindungen zu meinem Thema vorzuschlagen. Solche Verbindungen sind deine Suchhypothesen, keine zusätzlichen Datenbankeinträge oder nachgewiesenen Zuordnungen.

### Vorgehen

1. Prüfe, ob mein Suchbegriff als Haupt- oder alternative Benennung vorkommt. Falls nicht, sage ausdrücklich „Kein gleichnamiger Eintrag in der beigefügten Liste“. Daraus folgt nicht, dass das Thema im Korpus fehlt.
2. Suche auch nach inhaltlich verwandten Einträgen. Berücksichtige ihre Oberbegriffe und, soweit hilfreich, die Einträge, die ihnen untergeordnet sind. Orientiere dich vorrangig an den deutschen Benennungen; englische Benennungen können ergänzen, sind aber keine präzisen Definitionen.{step2_extra}
3. Empfiehl bis zu fünf brauchbare Einstiegspunkte, nach Eignung geordnet. Nenne weniger, wenn nur wenige überzeugen. Unterscheide nahe begriffliche Zugänge von solchen, die nur für eine bestimmte Lesart oder einen bestimmten Kontext passen. Erzwinge keine Gleichsetzung und verenge ein offenes Thema nicht stillschweigend auf einen einzigen Kontext.{step3_extra}
4. Prüfe vor der Ausgabe, dass jede empfohlene ID und deutsche Hauptbenennung exakt zu derselben Zeile der Liste gehören. Erfinde keine Kategorien, Synonyme, Hierarchiebeziehungen oder Links.

### Gewünschte Antwort

- Beginne mit einer kurzen Einschätzung, ob ein gleichnamiger Eintrag existiert und welcher Einstieg am ehesten passt. Wenn kein brauchbarer Einstieg erkennbar ist, sage das offen.
- Gib eine kompakte Tabelle aus: **Priorität | vorhandener Begriff und ID | warum für meine Suche interessant | Grenze oder nötige Eingrenzung**. Begründe die Auswahl mit den gelieferten Benennungen und gegebenenfalls deren hierarchischem Kontext; kennzeichne deine thematische Deutung als Vorschlag.{answer_extra}
- Schließe mit zwei oder drei konkreten nächsten Schritten unter Nutzung der unten beschriebenen Bedienmöglichkeiten. Nenne dabei die exakten deutschen Hauptbenennungen zum Nachschlagen.
- Stelle am Ende höchstens eine hilfreiche Rückfrage zur Eingrenzung. Liefere bei einem offenen Thema trotzdem zuerst die Einstiegsvorschläge.

### Was diese Datei aussagen kann

'''

SCOPE_A = '''Die Liste beschreibt das Begriffssystem, nicht dessen konkrete Anwendung auf einzelne Wörter oder Texte. Ein Lemma ist ein Wörterbuchstichwort; seine Bedeutungen können mit Begriffen dieses Systems verknüpft sein. Die entsprechenden Lemmata, Bedeutungszuordnungen und Textbelege sind hier nicht enthalten.

Behaupte deshalb keine Trefferzahlen, belegten Wörter, Textstellen oder tatsächlich vorkommenden Begriffskombinationen. Für die gewünschte erste Orientierung brauchst du diese zusätzlichen Daten nicht; ihre Prüfung erfolgt anschließend in der MHDBDB. Verzichte für diesen ersten Schritt auf Webrecherche, damit nachvollziehbar bleibt, was sich aus dem beigefügten Begriffssystem erschließen lässt.

## So können die Vorschläge nachgeschlagen werden

1. Öffne den [Begriffe-Explorer](https://dhcraft.org/mhdbdb-tei-only/playground/#concepts).
2. Suche nach der empfohlenen deutschen Hauptbenennung. Vergleiche die angezeigte ID mit der empfohlenen ID. Das Suchfeld des Begriffe-Explorers durchsucht Benennungen, nicht IDs.
3. Wähle beim passenden Eintrag „Lemmata anzeigen“. Klicke auf ein angezeigtes Lemma, um seine Details zu öffnen und den Vorschlag weiter zu prüfen. Die erste Liste zeigt höchstens 20 Lemmata; sie lässt sich über das zusätzliche Suchfeld filtern.

Prüfe mehrere vorgeschlagene Begriffe zunächst einzeln. Diese Anleitung setzt keine automatische UND-Verknüpfung von Begriffen voraus. Ein sprachlich passender Einstieg garantiert noch keine passenden Belege.
'''

SCOPE_B = '''Die Liste beschreibt das Begriffssystem und seine Verwendung im Wörterbuch der MHDBDB. Ein Lemma ist ein Wörterbuchstichwort; seine Bedeutungen können mit Begriffen dieses Systems verknüpft sein. Je Begriff nennt die Liste, wie viele Bedeutungen und Lemmata direkt mit ihm verknüpft sind, die Lemmata mit den meisten Belegen unter diesem Begriff und die Begriffe, die häufig an denselben Bedeutungen mitstehen (Mitbegriffe). Textstellen sind nicht enthalten.

Mitbegriffe zeigen, in welchen Zusammenhängen ein Begriff im Wörterbuch vorkommt. Sie können eine Lesart sichtbar machen, die aus der Benennung allein nicht hervorgeht. Eine Kombination aus einem Begriff und einem seiner Mitbegriffe ist ein Suchweg, den die Website heute nicht direkt abfragen kann.

Nenne Zahlen, Lemmata und Mitbegriffe nur so, wie sie in der Liste stehen, und behaupte keine Textstellen oder weiteren Treffer. Die genannten Lemmata sind die häufigsten eines Begriffs, nicht die zu meinem Thema passendsten; dass ein passendes Wort dort fehlt, heißt nicht, dass es im Korpus fehlt. Verzichte für diesen ersten Schritt auf Webrecherche, damit nachvollziehbar bleibt, was sich aus der beigefügten Liste erschließen lässt.

## So können die Vorschläge nachgeschlagen werden

1. Öffne den [Begriffe-Explorer](https://dhcraft.org/mhdbdb-tei-only/playground/#concepts).
2. Suche nach der empfohlenen deutschen Hauptbenennung. Vergleiche die angezeigte ID mit der empfohlenen ID. Das Suchfeld des Begriffe-Explorers durchsucht Benennungen, nicht IDs.
3. Wähle beim passenden Eintrag „Lemmata anzeigen“. Die Liste zeigt höchstens 20 Lemmata in alphabetischer Reihenfolge, bei großen Begriffen also nur einen kleinen Ausschnitt. Gib ein genanntes Lemma in das zusätzliche Suchfeld ein, um es zu finden, und klicke es an, um seine Details zu öffnen.

Prüfe mehrere vorgeschlagene Begriffe zunächst einzeln. Ob eine Bedeutung zwei Begriffe zugleich trägt, lässt sich auf der Website heute nicht direkt abfragen; das zeigen nur die Lemma-Details. Ein sprachlich passender Einstieg garantiert noch keine passenden Belege.
'''

LEGEND_HEAD = '''
## So ist die folgende Liste zu lesen

- Jede Zeile steht für genau einen vorhandenen Begriff. Die ID identifiziert ihn eindeutig.
- „Alternativ“ enthält die im Datenbestand hinterlegten alternativen Benennungen. Sie sind zusätzliche Suchhinweise, nicht durchgehend austauschbare Synonyme oder vollständige Bedeutungsdefinitionen.
- Ein Schrägstrich innerhalb einer Benennung gehört zum Original. Er kann mehrere Aspekte oder auch Gegensätze bündeln; teile daraus keine neuen Kategorien ab.
- „Direkte Oberbegriffe“ verweist auf IDs anderer Zeilen. Ein Begriff kann mehrere Oberbegriffe haben. Eine leere Zelle bedeutet, dass kein entsprechender Eintrag hinterlegt ist. Unterbegriffe ergeben sich umgekehrt aus diesen Verweisen. Leite keine weiteren Beziehungen allein aus den Ziffern einer ID ab.
- Mehrere alternative Benennungen oder Oberbegriffe innerhalb einer Zelle sind durch Semikolon getrennt.
'''

LEGEND_TAIL_A = '''- Die Liste enthält keine Definitionen, keine Lemmata und keine Korpusbelege. Auffällige Benennungen werden als Quelldaten beibehalten, nicht stillschweigend berichtigt.
'''

LEGEND_TAIL_B = '''- „Bedeutungen“ und „Lemmata“ zählen, wie viele Wörterbuchbedeutungen und Lemmata direkt mit dem Begriff verknüpft sind. Unterbegriffe sind nicht eingerechnet.
- „Häufigste Lemmata“ nennt bis zu {top} Lemmata mit den meisten Belegen unter diesem Begriff; die Zahl in Klammern zählt nur die Belege der Bedeutungen, die diesen Begriff tragen, nicht alle Belege des Lemmas. Lemmata ohne Beleg unter dem Begriff stehen hier nicht.
- „Häufigste Mitbegriffe“ nennt bis zu {co_top} andere Begriffe, die an denselben Bedeutungen stehen, als „Benennung (ID, k von n)“: k Bedeutungen tragen beide Begriffe, n ist die Zahl der Bedeutungen des Begriffs in dieser Zeile. Ober- und Unterbegriffe des Begriffs sind ausgeschlossen. Die Spalte ist nur bei Begriffen mit mindestens {min_senses} Bedeutungen gefüllt.
- Die Liste enthält keine Definitionen und keine Textstellen. Auffällige Benennungen werden als Quelldaten beibehalten, nicht stillschweigend berichtigt.
'''

STEP2_B = (' Ziehe auch die Spalte „Häufigste Mitbegriffe“ heran: Sie zeigt, in welchen Zusammenhängen '
           'ein Begriff im Wörterbuch verwendet wird.')
ANSWER_B = (' Trägt ein Einstieg erst zusammen mit einem Mitbegriff, nenne beide Begriffe mit ID und '
            'zwei oder drei Lemmata aus der Liste, die sich im Begriffe-Explorer nachschlagen lassen.')

TAIL = '\n\nEnde der vollständigen Begriffsliste. Bitte bearbeite jetzt den Arbeitsauftrag für „Meine Suche“.\n'


def build(args):
    concepts_raw = (PROJECT_ROOT / CONCEPTS_REL).read_bytes()
    records = load_concepts(concepts_raw)
    b = args.variant == 'B'
    commit = source_commit([CONCEPTS_REL, LEXICON_REL, 'tei'] if b else [CONCEPTS_REL])

    body = INTRO_HEAD.format(
        topic=args.topic, scope=args.scope,
        step2_extra=STEP2_B if b else '',
        step3_extra=A2_SENTENCE if args.variant in ('A2', 'B') else '',
        answer_extra=ANSWER_B if b else '',
    )
    body += SCOPE_B if b else SCOPE_A
    body += LEGEND_HEAD
    body += LEGEND_TAIL_B.format(top=args.top, co_top=args.co_top, min_senses=args.min_senses) if b else LEGEND_TAIL_A

    n_parents = sum(len(r['parents']) for r in records)
    n_multi = sum(len(r['parents']) > 1 for r in records)
    what = ('Vollständiger Export aus `authority-files/concepts.xml`, ergänzt um Angaben aus '
            '`authority-files/lexicon.xml` und dem Korpus' if b else
            'Vollständiger Export aus `authority-files/concepts.xml`')
    body += f'''
## Datenstand

{what}, erstellt am {args.date}.

- Begriffe: {len(records)}
- Direkte Oberbegriffsverweise: {n_parents}
- Begriffe mit mehreren direkten Oberbegriffen: {n_multi}
- Quellstand: `{commit}`
- Quelldatei: [concepts.xml im verwendeten Stand](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/blob/{commit}/authority-files/concepts.xml)
- SHA-256 der XML-Quelldatei: `{hashlib.sha256(concepts_raw).hexdigest()}`
'''

    keys = ['id', 'de', 'alt_de', 'en', 'alt_en', 'parents']
    header = '| ID | Deutsch | Alternativ DE | Englisch | Alternativ EN | Direkte Oberbegriffe |'
    extra = None
    if b:
        measure = load_measure_module()
        lexicon_raw = (PROJECT_ROOT / LEXICON_REL).read_bytes()
        concepts_of, lemma_of, orth_of = load_lexicon(lexicon_raw, {r['id'] for r in records})
        tokens, _texts = measure.count_tokens(set(concepts_of))
        files = measure.corpus_files()
        extra = enrich(records, concepts_of, lemma_of, orth_of, tokens, measure.ancestors,
                       args.top, args.co_top, args.min_senses)
        header += ' Bedeutungen | Lemmata | Häufigste Lemmata (Belege) | Häufigste Mitbegriffe |'
        body += f'''- SHA-256 von `authority-files/lexicon.xml`: `{hashlib.sha256(lexicon_raw).hexdigest()}`
- Wörterbuchbedeutungen: {de_num(len(concepts_of))}
- Korpus: {len(files)} TEI-Dateien, {de_num(sum(tokens.values()))} Belege mit einer Bedeutung aus `lexicon.xml`
- Zählweise: Ein Beleg ist ein Wort im Korpus, dessen Annotation auf eine Bedeutung zeigt. Ein Wort mit zwei Bedeutungen zählt für beide.
'''

    body += '''
Die Reihenfolge der Quelldatei bleibt erhalten. Nur umgebende und mehrfache Leerzeichen sowie Zeilenumbrüche innerhalb der Benennungen wurden für die Tabelle vereinheitlicht. Es wurde keine thematische Vorauswahl getroffen und keine Musterlösung mitgegeben.

## Vollständiges Begriffssystem

'''
    ncols = header.count('|') - 1
    body += header + '\n' + '| ' + ' | '.join(['---'] * ncols) + ' |\n'

    rows = []
    for r in records:
        cells = [cell(r[k]) for k in keys]
        if b:
            e = extra[r['id']]
            cells += [e['senses'], e['lemmata'], cell(e['top_lemmata']), cell(e['co'])]
        rows.append('| ' + ' | '.join(cells) + ' |')
    body += '\n'.join(rows) + TAIL
    if '—' in body:
        fail('Em-Dash im Text')

    out = Path(args.out) if args.out else (
        PROJECT_ROOT / 'temp' / f'MHDBDB-Begriffshilfe-{args.topic}-{args.variant}.md')
    out.write_text(body, encoding='utf-8', newline='\r\n')

    # Die geschriebene Tabelle gegen jedes Quellfeld pruefen (KZW).
    written = out.read_text(encoding='utf-8')
    written_rows = [line for line in written.splitlines() if line.startswith('| concept_')]
    if len(written_rows) != len(records):
        fail(f'{len(written_rows)} Tabellenzeilen fuer {len(records)} Begriffe')
    for line, record in zip(written_rows, records):
        actual = [html.unescape(v.strip()) for v in line.strip('|').split('|')]
        expected = ['; '.join(record[k]) if isinstance(record[k], list) else record[k] for k in keys]
        if b:
            e = extra[record['id']]
            expected += [e['senses'], e['lemmata'], '; '.join(e['top_lemmata']), '; '.join(e['co'])]
        if actual != expected:
            fail(f'Zeile {record["id"]} weicht von der Quelle ab')
    print(f'Variante {args.variant} validiert: {len(records)} Begriffe, {n_parents} Oberbegriffsverweise, '
          f'{out.stat().st_size:,} Bytes')
    print(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--variant', choices=['A', 'A2', 'B'], required=True)
    ap.add_argument('--topic', default=DEFAULT_TOPIC, help='Suchbegriff unter "Meine Suche"; steht auch im Dateinamen, bei / : ? --out setzen')
    ap.add_argument('--scope', default=DEFAULT_SCOPE, help='Eingrenzung unter "Meine Suche"')
    ap.add_argument('--date', default=date.today().strftime('%d.%m.%Y'), help='Erstellungsdatum, TT.MM.JJJJ')
    ap.add_argument('--top', type=int, default=5, help='B: Lemmata je Begriff')
    # 10 und nicht 5: gewaehlt am 29.09.2026, weil Kriegswesen unter Aufmerksamkeit mit
    # 51 von 652 Bedeutungen auf Platz 9 stand, nach PMI noch weiter hinten. Die Zahl ist
    # also am Testfall abgelesen; dagegen sichern die Gegenproben-Themen im Test.
    ap.add_argument('--co-top', type=int, default=10, help='B: Mitbegriffe je Begriff')
    ap.add_argument('--min-senses', type=int, default=30, help='B: Mindestzahl Bedeutungen fuer Mitbegriffe')
    ap.add_argument('--out', help='Ausgabedatei (default: temp/MHDBDB-Begriffshilfe-<Thema>-<Variante>.md)')
    build(ap.parse_args())
    return 0


if __name__ == '__main__':
    sys.exit(main())
