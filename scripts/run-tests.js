#!/usr/bin/env node
/**
 * Playwright starten und das Ergebnis aus `report.json` verkuenden.
 *
 * Existiert, weil die Frage "hat die Suite bestanden?" bisher drei Antworten
 * hatte, die verschieden luegen. Das Issue-Playbook hat daraus vier
 * Handwerksregeln destilliert (§2.1 Regeln 6, 16, 26, 27), und das
 * Merge-Playbook wies bis zum 2026-08-05 auf ausgerechnet die Quelle, die
 * zwei dieser Regeln als falsch-gruen belegen. Eine Regel, die verlangt, nach
 * dem Lauf ein anderes Werkzeug zu befragen als das, welches gerade die
 * Zusammenfassung gedruckt hat, verliert den Wettbewerb um Aufmerksamkeit
 * gegen 31 andere Regeln. Also uebernimmt das hier der Aufruf selbst.
 *
 * Was der Wrapper prueft, und warum jeweils:
 *
 * 1. Fremder Dev-Server. `testing/playwright.config.js` setzt
 *    `reuseExistingServer: !process.env.CI`, und Playwright prueft nur, ob auf
 *    Port 8080 jemand antwortet, nicht wer. Solange alle Sessions im selben
 *    Arbeitsbaum liefen, war das harmlos, und das Journal hat es fuenfmal als
 *    harmlos abgehakt (`journal-archive.md:839, 954, 1021, 1080, 1127`). Seit
 *    Regel 29 jeder Session ihren eigenen Worktree gibt, serviert ein
 *    wiederverwendeter Server fremde Dateien: die Suite prueft dann einen
 *    anderen Arbeitsbaum und wird gruen. Das ist kein falsch abgelesenes
 *    Ergebnis, sondern ein korrekt abgelesenes falsches, und es trifft die
 *    Chrome-Verifikation ueber denselben Port gleich mit.
 *
 * 2. Alter Report. `report.json` bleibt nach jedem Lauf liegen und ist
 *    gitignored. Bricht ein Lauf ab, bevor der Reporter schreibt, liest die
 *    Anweisung "die Zahlen kommen aus report.json" den vorigen Lauf. Am
 *    2026-08-05 lag im Arbeitsbaum ein drei Tage alter Report mit 14 Tests
 *    und `unexpected: 0`. Deshalb wird die Datei vorher geloescht: fehlt sie
 *    danach, ist das ein Infrastrukturfehler und kein Testergebnis.
 *
 * 3. Geschrumpfte Grundgesamtheit. Im Vorfall zu Regel 27 meldete die Konsole
 *    "41 passed", waehrend der Lauf 57 Tests hatte, einen `unexpected` und
 *    fuenfzehn `skipped`. Ein Sollwert in einer Datei waere die falsche
 *    Abhilfe, er driftet mit jedem neuen Spec. Stattdessen werden beide
 *    Seiten zur Laufzeit gemessen: die Spec-Dateien auf der Platte gegen die
 *    Dateien im Report. Nur bei filterlosem Lauf, denn ein gefilterter Lauf
 *    hat berechtigterweise weniger, und dann sagt das Verdikt TEILLAUF statt
 *    Vollstaendigkeit zu behaupten.
 *
 * Die letzte Zeile der Ausgabe ist das Ergebnis. Sie nennt den geprueften
 * Pfad, damit auch im Nachhinein erkennbar bleibt, welcher Arbeitsbaum
 * gemessen wurde. Der Exit-Code wird aus dem Verdikt gebildet, nicht
 * durchgereicht: 0 gruen, 1 rot, 2 der Lauf ist gar nicht zustande gekommen.
 *
 * Aufruf: node scripts/run-tests.js [playwright-argumente...]
 * Ueber npm: `npm test`, `npm run test:changed`, `npm run test:quick`,
 * jeweils mit `--` vor eigenen Argumenten (`npm test -- --grep minne`).
 */

import { spawnSync } from 'child_process';
import { existsSync, rmSync, mkdirSync, writeFileSync, unlinkSync, readFileSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { randomBytes } from 'crypto';

const hier = dirname(fileURLToPath(import.meta.url));
const repoWurzel = resolve(hier, '..');
const testVerzeichnis = resolve(repoWurzel, 'testing');
const ergebnisVerzeichnis = resolve(testVerzeichnis, 'test-results');
const reportPfad = resolve(ergebnisVerzeichnis, 'report.json');
const specVerzeichnis = resolve(testVerzeichnis, 'tests');
const playwrightCli = resolve(repoWurzel, 'node_modules', '@playwright', 'test', 'cli.js');

const BASIS_URL = 'http://localhost:8080';

// Grosszuegig bemessen, in beide Richtungen begruendet: eine aktive Ablehnung
// kommt sofort und wartet nie, ein gesaettigter `http-server` dagegen kann
// unter Last mehrere Sekunden brauchen (er ist single-threaded, siehe den
// Worker-Kommentar in testing/playwright.config.js). Ein knappes Budget
// wuerde den eigenen Server bei Last faelschlich als fremd melden.
const ANKLOPF_FRIST_MS = 10000;

const argumente = process.argv.slice(2);

// Diese Modi schreiben keinen JSON-Report: `--list` zaehlt nur auf, die
// interaktiven laufen unter Aufsicht. Sie werden durchgereicht und ihr
// Exit-Code unveraendert weitergegeben.
const ohneReport = argumente.some((a) => a === '--list' || a === '--ui' || a === '--debug');

// Alles, was die Auswahl einschraenkt, macht den Lauf zum Teillauf. Bewusst
// grosszuegig: ein positionales Argument ist bei `playwright test` immer ein
// Dateifilter, und im Zweifel ist "TEILLAUF" die ehrlichere Aussage.
const FILTER_FLAGS = /^--(grep|grep-invert|only-changed|shard|last-failed|project)\b/;
const hatFilter = argumente.some((a) => !a.startsWith('-') || FILTER_FLAGS.test(a));

function abbruch(meldung, code) {
  console.error('');
  console.error(meldung);
  // Der Diagnosetext geht nach stderr, die VERDICT-Zeile nach stdout. Sonst
  // haelt die Zusage nicht, die letzte Zeile sei das Ergebnis: wer
  // `npm test > lauf.txt` umleitet, faende im Infrastrukturfall gar kein
  // Verdikt, sondern das letzte, was Playwright gedruckt hat.
  console.log(`VERDICT: KEIN ERGEBNIS (${meldung.split('\n')[0]})`);
  process.exit(code);
}

function mitFrist(url) {
  const abbrecher = new AbortController();
  const frist = setTimeout(() => abbrecher.abort(), ANKLOPF_FRIST_MS);
  return fetch(url, { signal: abbrecher.signal }).finally(() => clearTimeout(frist));
}

/**
 * Antwortet auf 8080 jemand, und ist es unser Arbeitsbaum?
 *
 * Der Test laeuft ueber eine Datei mit Zufallsnamen und Zufallsinhalt unter
 * `testing/test-results/`: das Verzeichnis ist gitignored, der Sentinel
 * beruehrt also den Index nicht, den parallele Sessions teilen. Ein fremder
 * Server liefert fuer diesen Pfad einen 404 oder etwas anderes.
 */
async function serverPruefen() {
  try {
    await mitFrist(BASIS_URL);
  } catch (fehler) {
    // Nur die aktive Ablehnung beweist, dass niemand horcht. Jeder andere
    // Fehler beweist eher das Gegenteil: da ist jemand, er antwortet nur
    // nicht (rechtzeitig). Diese Unterscheidung ist der ganze Punkt, denn
    // der wahrscheinlichste Grund fuer ein Zeitueberschreiten ist genau der
    // Fall, den der Check fangen soll: eine parallele Session faehrt ihren
    // Volllauf und saettigt dabei ihren eigenen Server.
    if (fehler.cause?.code === 'ECONNREFUSED') return { status: 'kein-server' };
    return {
      status: 'fremd',
      grund: `${fehler.name} beim Anklopfen nach ${ANKLOPF_FRIST_MS / 1000} s (${fehler.cause?.code ?? 'ohne Fehlercode'})`,
    };
  }

  mkdirSync(ergebnisVerzeichnis, { recursive: true });
  const name = `sentinel-${randomBytes(8).toString('hex')}.txt`;
  const pfad = resolve(ergebnisVerzeichnis, name);
  const inhalt = randomBytes(16).toString('hex');
  writeFileSync(pfad, inhalt, 'utf8');

  try {
    const antwort = await mitFrist(`${BASIS_URL}/testing/test-results/${name}`);
    if (!antwort.ok) return { status: 'fremd', grund: `HTTP ${antwort.status}` };
    const gelesen = (await antwort.text()).trim();
    if (gelesen !== inhalt) return { status: 'fremd', grund: 'Inhalt weicht ab' };
    return { status: 'unserer' };
  } catch (fehler) {
    return { status: 'fremd', grund: `${fehler.name}: ${fehler.message}` };
  } finally {
    try {
      unlinkSync(pfad);
    } catch {
      // Der Sentinel liegt in einem gitignorierten Verzeichnis; bleibt er
      // liegen, ist das kein Grund, den Lauf scheitern zu lassen.
    }
  }
}

/** Alle `file`-Angaben aus dem Suite-Baum einsammeln. */
function dateienImReport(knoten, menge = new Set()) {
  for (const eintrag of knoten ?? []) {
    if (eintrag.file) menge.add(eintrag.file);
    if (eintrag.suites) dateienImReport(eintrag.suites, menge);
  }
  return menge;
}

/**
 * Tests eines Status mit Datei und Titel einsammeln.
 *
 * Fuer `skipped` und `flaky` bewusst die Titel statt einer Schwelle: ein
 * einzelner bekannter Fall gehoert zum Normalzustand, fuenfzehn ploetzliche
 * nicht, und die Titel unterscheiden beide. Eine Zahl kann das nicht, und ein
 * gepflegter Sollwert dafuer waere genau die driftende Angabe, die dieses
 * Skript vermeiden soll.
 */
function testsMitStatus(knoten, status, treffer = []) {
  for (const eintrag of knoten ?? []) {
    for (const spec of eintrag.specs ?? []) {
      if ((spec.tests ?? []).some((t) => t.status === status)) {
        treffer.push(`${eintrag.file ?? '?'} > ${spec.title}`);
      }
    }
    if (eintrag.suites) testsMitStatus(eintrag.suites, status, treffer);
  }
  return treffer;
}

// --- Ablauf ---------------------------------------------------------------

if (!existsSync(playwrightCli)) {
  abbruch(`Playwright nicht gefunden unter ${playwrightCli}\nFehlt node_modules in diesem Arbeitsbaum?`, 2);
}

if (!ohneReport) {
  const server = await serverPruefen();
  if (server.status === 'fremd') {
    abbruch(
      `Port 8080 wird von einem fremden oder nicht antwortenden Server bedient (${server.grund}).\n` +
        `Playwright wuerde ihn wiederverwenden und die Suite gegen einen anderen\n` +
        `Arbeitsbaum laufen lassen. Erwartet: ${repoWurzel}\n` +
        `Abhilfe: den fremden Dev-Server beenden, dann erneut starten.`,
      2
    );
  }
  // Ein alter Report ist gefaehrlicher als gar keiner.
  rmSync(reportPfad, { force: true });
}

const lauf = spawnSync(process.execPath, [playwrightCli, 'test', ...argumente], {
  cwd: testVerzeichnis,
  stdio: 'inherit',
  env: { ...process.env, PW_TEST_HTML_REPORT_OPEN: 'never' },
});

if (lauf.error) {
  abbruch(`Start von Playwright fehlgeschlagen: ${lauf.error.message}`, 2);
}

if (ohneReport) {
  process.exit(lauf.status === null ? 1 : lauf.status);
}

if (!existsSync(reportPfad)) {
  abbruch(
    `Der Lauf hat den Reporter nie erreicht, ${reportPfad} fehlt.\n` +
      `Kein Ergebnis ist ein besseres Ergebnis als ein altes.`,
    2
  );
}

let bericht;
try {
  bericht = JSON.parse(readFileSync(reportPfad, 'utf8'));
} catch (fehler) {
  abbruch(`report.json ist nicht lesbar: ${fehler.message}`, 2);
}

const zahlen = bericht.stats ?? {};
const erwartet = zahlen.expected ?? 0;
const unerwartet = zahlen.unexpected ?? 0;
const wacklig = zahlen.flaky ?? 0;
const uebersprungen = zahlen.skipped ?? 0;
const gesamt = erwartet + unerwartet + wacklig + uebersprungen;
const laufFehler = (bericht.errors ?? []).length;

const dateienGelaufen = dateienImReport(bericht.suites);
const gruende = [];

if (unerwartet > 0) gruende.push(`${unerwartet} unexpected`);
// Auch flaky ist rot, und zwar als Fortsetzung einer Entscheidung, die schon
// in der Config steht: `failOnFlakyTests: true` haelt fest, dass ein Retry
// zur Diagnose da ist und nicht zum Durchwinken.
if (wacklig > 0) gruende.push(`${wacklig} flaky`);
if (laufFehler > 0) gruende.push(`${laufFehler} Lauffehler`);

let fehlendeDateien = [];
if (!hatFilter) {
  const dateienAufPlatte = readdirSync(specVerzeichnis).filter((d) => d.endsWith('.spec.js'));
  fehlendeDateien = dateienAufPlatte.filter((d) => !dateienGelaufen.has(d));
  if (fehlendeDateien.length > 0) {
    gruende.push(`${fehlendeDateien.length} Spec-Datei(en) nicht gelaufen`);
  }
}

console.log('');
console.log(
  `stats: ${erwartet} expected, ${unerwartet} unexpected, ${wacklig} flaky, ${uebersprungen} skipped` +
    ` (${(zahlen.duration / 1000 || 0).toFixed(0)} s)`
);

for (const titel of testsMitStatus(bericht.suites, 'skipped')) {
  console.log(`  skipped: ${titel}`);
}
for (const titel of testsMitStatus(bericht.suites, 'flaky')) {
  console.log(`  flaky:   ${titel}`);
}
for (const datei of fehlendeDateien) {
  console.log(`  NICHT GELAUFEN: ${datei}`);
}

// Playwrights eigener Exit-Code ist kein Ergebnis, das ist die Lehre der
// alten Regel 26: er darf einen roten Report nicht uebersteuern. Die
// Gegenrichtung ist aber nicht dieselbe Aussage. Endet der Prozess ungleich
// null oder per Signal, waehrend der Report nichts beanstandet,
// widersprechen sich zwei Quellen, und dann ist das kein gruener Lauf,
// sondern ein abgebrochener. Ein hart getoeteter Lauf faellt schon vorher
// durch die Report-Pruefung (gemessen), ein sanft abgebrochener kaeme sonst
// hier durch: die nicht gelaufenen Tests stehen als `skipped` im Report, und
// skipped ist kein Grund.
if (gruende.length === 0 && (lauf.status !== 0 || lauf.signal)) {
  abbruch(
    `Playwright endete mit ${lauf.signal ? `Signal ${lauf.signal}` : `Status ${lauf.status}`},` +
      ` waehrend der Report nichts beanstandet (${gesamt} Tests).\n` +
      `Das ist ein abgebrochener Lauf, kein gruenes Ergebnis.`,
    2
  );
}

if (gruende.length > 0) {
  // Testzahl, Dateizahl und Pfad stehen auch im roten Fall, sonst haelt die
  // Zusage der Playbooks nicht, die Zeile nenne alle drei. Bei fehlenden
  // Spec-Dateien ist die Dateizahl sogar der interessantere Teil.
  console.log(
    `VERDICT: ROT (${gruende.join(', ')}; ${gesamt} Tests, ${dateienGelaufen.size} Dateien,` +
      ` Pfad: ${repoWurzel})`
  );
  process.exit(1);
}

// Null Tests sind trivialerweise gruen, und genau deshalb darf hier nicht
// "GRUEN" stehen: die Zeile landet im Verifikations-Block eines PRs und
// behauptete dort eine Pruefung, die nicht stattgefunden hat. Der haeufigste
// Fall ist `test:changed` auf einem Zweig ohne Spec-Aenderungen; Playwright
// endet dabei regulaer mit 0 (DEVELOPMENT.md), es ist also kein Fehler,
// sondern nur kein Ergebnis.
if (gesamt === 0) {
  console.log(
    `VERDICT: NICHTS GELAUFEN (0 Tests${hatFilter ? `, Filter: ${argumente.join(' ')}` : ''},` +
      ` Pfad: ${repoWurzel}). Das belegt nichts.`
  );
  process.exit(0);
}

if (hatFilter) {
  console.log(
    `VERDICT: TEILLAUF GRUEN (${gesamt} Tests aus ${dateienGelaufen.size} Datei(en),` +
      ` Filter: ${argumente.join(' ')}, Pfad: ${repoWurzel})`
  );
} else {
  console.log(
    `VERDICT: VOLLLAUF GRUEN (${gesamt} Tests, ${dateienGelaufen.size} Dateien, Pfad: ${repoWurzel})`
  );
}
process.exit(0);
