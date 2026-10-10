#!/usr/bin/env node
/**
 * Laufzeit der Lemma-Aufloesung (Hauptseite und Playground) gegen die echten
 * Indexe in data/, gehalten gegen ein Budget (#564).
 *
 * Warum es das gibt: In PR #562 (#463) fand ein Review eine Pruefung, die je
 * Aufruf ueber alle rund 42.000 Schluessel des lemmaIndex lief (ca. 4 ms,
 * dreimal je Suche). So etwas faengt sonst nur ein Mensch beim Lesen.
 *
 * Was gemessen wird: je Eingabe und Oberflaeche der kleinste von drei
 * Blockmedianen zu je REPS warmen Aufrufen (ein Aufruf vorab, der die Caches
 * fuellt; Begruendung am Minimum bei messen()), jede Oberflaeche in einem
 * eigenen Prozess (Begruendung beim Kindprozess). Gemessen wird in Node,
 * nicht im Browser: dieselben Module, dieselben Daten, aber ohne Netz,
 * Entpacken und Seitenaufbau.
 *   - main:  SearchEngine.resolveSearchTerm (assets/js/search/search-engine.js)
 *   - pg:    AuthorityFilesManager.searchLemmaByOrthography
 *   - pg-ac: AuthorityFilesManager.getLemmaAutocompleteMatches
 *
 * Budget: scripts/audit/search-budget.json, je Schluessel ein Wert in ms.
 * Rot (Exit 1) bei Median > Budget. Ein Budget wird nur bewusst und im Diff
 * erhoeht (Entscheidung chsteiner in #564).
 *
 * Aufruf:
 *   node scripts/audit/benchmark-search.mjs                 pruefen
 *   node scripts/audit/benchmark-search.mjs --measure       nur messen, kein Budget
 *   node scripts/audit/benchmark-search.mjs --dump datei    Ergebnis-IDs aller Eingaben schreiben
 *   Weitere: --reps N, --manager pfad (anderes authority-manager.js, fuer den Vergleich mit origin/main)
 *
 * Exit: 0 gruen, 1 ueber Budget, 2 Lauf nicht zustande gekommen.
 */

import { gunzipSync } from 'zlib';
import { readFileSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath, pathToFileURL } from 'url';
import { spawnSync } from 'child_process';

const wurzel = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const budgetPfad = resolve(wurzel, 'scripts', 'audit', 'search-budget.json');

const args = process.argv.slice(2);
const arg = (name) => {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : null;
};
const nurMessen = args.includes('--measure');
const dumpPfad = arg('--dump');
const REPS = Number(arg('--reps') ?? 50);
const BLOECKE = 3;
// Kindprozess: misst nur die Faelle einer Oberflaeche und druckt JSON (siehe unten)
const nur = arg('--only');
const managerPfad = resolve(arg('--manager') ?? resolve(wurzel, 'playground/js/data/authority-manager.js'));

function abbruch(text) {
  console.error(text);
  console.log(`BENCHMARK: KEIN ERGEBNIS (${text.split('\n')[0]})`);
  process.exit(2);
}

if (!Number.isInteger(REPS) || REPS < 1) {
  abbruch(`--reps muss eine ganze Zahl ab 1 sein, war: ${arg('--reps')}`);
}

function ladeIndex(name) {
  try {
    return JSON.parse(gunzipSync(readFileSync(resolve(wurzel, 'data', name))).toString('utf8'));
  } catch (fehler) {
    abbruch(`data/${name} nicht lesbar: ${fehler.message}`);
  }
}

const authority = ladeIndex('authority-index.json.gz');
const corpus = ladeIndex('corpus-index.json.gz');

// Der Playground liest den Corpus-Index ueber window.playground (authority-manager.js)
globalThis.window = { playground: { corpusData: { texts: corpus.texts || [], lemmaIndex: corpus.lemmaIndex || {} } } };

const { SearchEngine } = await import(pathToFileURL(resolve(wurzel, 'assets/js/search/search-engine.js')));
const { AuthorityFilesManager } = await import(pathToFileURL(managerPfad));

const engine = new SearchEngine(authority, corpus);
const manager = new AuthorityFilesManager({
  lemmata: authority.lemmata || [],
  variants: authority.variants || {},
  variantCandidates: authority.variantCandidates || {},
});

// Feste Eingaben je Aufloesungsweg. Die Namen stehen im Budget, nicht umbenennen
// ohne das Budget mitzunehmen.
const EINGABEN = [
  ['exakt', 'minne'],
  ['exakt-diakritisch', 'vlâder'],
  ['homograph', 'rôt'],
  ['variante', 'brott'],
  ['variante-mehrdeutig', 'hab'],
  ['unbelegt-mit-variante', 'rosse'],
  ['belegt-kurz', 'roz'],
  ['gat', 'gat'],
  ['praefix', 'minnecl'],
  ['unbekannt', 'schwertkampf'],
];
// Autocomplete wird getippt: ein Fall ist die Folge aller Praefixe eines Worts,
// gemessen als Summe der Tastendruecke. Vorab ein unbeteiligtes Wort, damit ein
// Zwischenspeicher des vorigen Falls nicht schon verengt ist.
const AUTOCOMPLETE = [
  ['kurz', 'm'],
  ['minne', 'minne'],
  ['diakritisch', 'êre'],
  ['ohne-treffer', 'xqzv'],
];
const tippen = (wort) => {
  const folge = [];
  for (let i = 1; i <= wort.length; i++) folge.push(wort.slice(0, i));
  return folge;
};
const AUTOCOMPLETE_RESET = 'zzzzzz';

function median(werte) {
  const s = [...werte].sort((a, b) => a - b);
  return s[Math.floor(s.length / 2)];
}

function messen(fn, vorab = () => {}) {
  vorab();
  fn(); // warm: fuellt die Tafeln des Playgrounds
  // BLOECKE Bloecke zu je REPS Aufrufen, gewertet wird der kleinste Blockmedian:
  // Last durch andere Prozesse verlaengert einen Block, verkuerzt aber keinen,
  // waehrend ein echter Mehraufwand in jedem Block steht. Gemessen am
  // 10.10.2026: dieselbe unveraenderte Hauptseiten-Aufloesung schwankte
  // zwischen 0,6 und 1,8 ms, je nachdem, was sonst auf dem Rechner lief.
  const blockmediane = [];
  for (let b = 0; b < BLOECKE; b++) {
    const dauern = [];
    for (let i = 0; i < REPS; i++) {
      vorab();
      const t0 = performance.now();
      fn();
      dauern.push(performance.now() - t0);
    }
    blockmediane.push(median(dauern));
  }
  return Math.min(...blockmediane);
}

const ids = (liste) => liste.map((l) => (typeof l === 'string' ? l : l.id));

const faelle = [];
for (const [name, eingabe] of EINGABEN) {
  faelle.push({ key: `main:${name}`, eingabe, lauf: () => ids(engine.resolveSearchTerm(eingabe)) });
  faelle.push({ key: `pg:${name}`, eingabe, lauf: () => ids(manager.searchLemmaByOrthography(eingabe)) });
}
for (const [name, eingabe] of AUTOCOMPLETE) {
  faelle.push({
    key: `pg-ac:${name}`,
    eingabe,
    vorab: () => manager.getLemmaAutocompleteMatches(AUTOCOMPLETE_RESET),
    lauf: () => {
      let letzte = [];
      for (const teil of tippen(eingabe)) letzte = ids(manager.getLemmaAutocompleteMatches(teil));
      return letzte;
    },
  });
}

if (dumpPfad) {
  // Ergebnisgleichheit: zusaetzlich zu den festen Eingaben eine seedfeste Stichprobe
  // aus Lemmata, Variantenschluesseln, Kuerzungen und Fremdwoertern.
  let seed = 564;
  const zufall = () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
  const wahl = (liste) => liste[Math.floor(zufall() * liste.length)];
  const lemmata = authority.lemmata.map((l) => l.lemma).filter(Boolean);
  const varianten = Object.keys(authority.variants);
  const stichprobe = [];
  for (let i = 0; i < 400; i++) stichprobe.push(wahl(lemmata));
  for (let i = 0; i < 400; i++) stichprobe.push(wahl(varianten));
  for (let i = 0; i < 300; i++) {
    const w = wahl(lemmata);
    stichprobe.push(w.slice(0, Math.max(1, Math.ceil(w.length * 0.6))));
  }
  for (let i = 0; i < 300; i++) stichprobe.push(wahl(lemmata) + 'xyz');
  stichprobe.push('Cordoba', 'hanc', 'lenden', 'böses', 'böses', 'lemma_4086', '4086', '');
  const aus = {};
  for (const f of faelle) aus[f.key] = ids(f.lauf());
  for (const e of stichprobe) {
    aus[`main|${e}`] = ids(engine.resolveSearchTerm(e));
    aus[`pg|${e}`] = ids(manager.searchLemmaByOrthography(e));
    aus[`pg-ac|${e}`] = ids(manager.getLemmaAutocompleteMatches(e));
  }
  // Getippt: jeder Praefix in Folge, Ergebnis nach jedem Tastendruck
  for (const e of stichprobe.slice(0, 300)) {
    aus[`pg-tippen|${e}`] = tippen(e).map((teil) => ids(manager.getLemmaAutocompleteMatches(teil)));
  }
  writeFileSync(resolve(dumpPfad), JSON.stringify(aus));
  console.log(`dump: ${Object.keys(aus).length} Eintraege (${faelle.length} feste Faelle + ${stichprobe.length} Stichproben x 3) -> ${dumpPfad}`);
  process.exit(0);
}

// Jede Oberflaeche in einem eigenen Prozess. Gemessen am 10.10.2026 (Review):
// dieselbe Playground-Aufloesung brauchte allein 1,0 ms, im selben Prozess nach
// der Hauptseite 2,8 bis 3,6 ms, und zwar in jedem Block. Der Zustand des
// Heaps haengt an der Reihenfolge; die Bloecke oben filtern das nicht.
const oberflaeche = (key) => (key.startsWith('main:') ? 'main' : 'pg');
if (nur) {
  const gewaehlt = faelle.filter((f) => oberflaeche(f.key) === nur);
  const teil = {};
  for (const f of gewaehlt) teil[f.key] = messen(f.lauf, f.vorab);
  console.log(`KIND ${JSON.stringify({ gemessen: teil, lemmata: authority.lemmata.length, varianten: Object.keys(authority.variants).length })}`);
  process.exit(0);
}

const gemessen = {};
let kopf = '';
for (const art of ['main', 'pg']) {
  const kind = spawnSync(process.execPath, [fileURLToPath(import.meta.url), '--only', art, '--reps', String(REPS), '--manager', managerPfad], {
    encoding: 'utf8',
    maxBuffer: 1 << 24,
  });
  const zeile = (kind.stdout || '').split('\n').find((z) => z.startsWith('KIND '));
  if (kind.status !== 0 || !zeile) {
    abbruch(`Kindprozess ${art} ohne Ergebnis (Status ${kind.status}): ${(kind.stderr || '').trim().split('\n')[0]}`);
  }
  const antwort = JSON.parse(zeile.slice(5));
  Object.assign(gemessen, antwort.gemessen);
  kopf = `${antwort.lemmata} Lemmata, ${antwort.varianten} Varianten`;
}
for (const f of faelle) {
  if (!Number.isFinite(gemessen[f.key])) abbruch(`Messwert fuer ${f.key} ist keine Zahl: ${gemessen[f.key]}`);
}

let budget = null;
if (!nurMessen) {
  try {
    budget = JSON.parse(readFileSync(budgetPfad, 'utf8'));
  } catch (fehler) {
    abbruch(`Budgetdatei nicht lesbar (${budgetPfad}): ${fehler.message}`);
  }
}

console.log(`Kleinster von ${BLOECKE} Blockmedianen (je ${REPS} warme Aufrufe) je Eingabe, ${kopf}, je Oberflaeche ein eigener Prozess`);
let rot = 0;
let fehlend = 0;
for (const f of faelle) {
  const ms = gemessen[f.key];
  const erlaubt = budget?.budgets?.[f.key]?.budgetMs;
  let urteil = '';
  if (budget) {
    if (erlaubt === undefined) {
      urteil = '  KEIN BUDGET';
      fehlend++;
    } else if (!Number.isFinite(erlaubt) || erlaubt <= 0) {
      abbruch(`Budget fuer ${f.key} ist keine positive Zahl: ${erlaubt}`);
    } else if (ms > erlaubt) {
      urteil = `  ROT (Budget ${erlaubt} ms)`;
      rot++;
    } else {
      urteil = `  ok (Budget ${erlaubt} ms)`;
    }
  }
  console.log(`  ${f.key.padEnd(34)} ${ms.toFixed(3).padStart(9)} ms${urteil}`);
}

if (budget) {
  const ohneFall = Object.keys(budget.budgets ?? {}).filter((k) => !(k in gemessen));
  if (ohneFall.length) {
    console.log(`  Budget ohne Fall: ${ohneFall.join(', ')}`);
    fehlend += ohneFall.length;
  }
}

if (nurMessen) {
  console.log(`BENCHMARK: GEMESSEN (${faelle.length} Faelle, kein Budget geprueft)`);
  process.exit(0);
}
if (rot > 0 || fehlend > 0) {
  console.log(`BENCHMARK: ROT (${rot} ueber Budget, ${fehlend} ohne Budget oder Fall, von ${faelle.length} Faellen)`);
  process.exit(1);
}
console.log(`BENCHMARK: GRUEN (${faelle.length} Faelle innerhalb des Budgets)`);
