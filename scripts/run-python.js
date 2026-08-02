#!/usr/bin/env node
/**
 * Ein Python-Skript mit dem aufgelösten Interpreter starten (#318 Punkt 6).
 *
 * Existiert, weil npm-Skripte keine Auflösungslogik haben: in `package.json`
 * stand `python3.13` sechsmal als fester String, und auf einer Maschine ohne
 * genau diesen Namen scheiterte `npm run build` an der ersten Zeile. Statt
 * einen anderen Namen zu raten, ruft die `package.json` jetzt hier durch.
 *
 * Der Wrapper reicht Argumente, Exit-Code und beide Ausgabekanäle
 * unverändert weiter; er ist nichts als der Namensauflöser davor. Signale
 * werden nicht eigens behandelt: ohne `detached` bleibt das Kind in der
 * Prozessgruppe des Elternprozesses, ein Strg-C erreicht also beide.
 *
 * Aufruf: node scripts/run-python.js <skript.py> [argumente...]
 * Direkt geht weiterhin alles wie bisher, etwa
 * `python scripts/build-corpus-index.py`; dieser Weg ist nur der, den npm
 * nimmt.
 */

import { spawnSync } from 'child_process';
import { resolvePython, pythonEnv } from './python-bin.js';

const args = process.argv.slice(2);

if (args.length === 0) {
  console.error('Aufruf: node scripts/run-python.js <skript.py> [argumente...]');
  process.exit(2);
}

let interpreter;
try {
  interpreter = resolvePython();
} catch (err) {
  console.error(err.message);
  process.exit(2);
}

const ergebnis = spawnSync(interpreter, args, {
  stdio: 'inherit',
  env: pythonEnv(),
});

if (ergebnis.error) {
  console.error(`Start von "${interpreter}" fehlgeschlagen: ${ergebnis.error.message}`);
  process.exit(2);
}

// Von einem Signal beendet: kein numerischer Exit-Code, aber auch kein
// Erfolg. Die Shell-Konvention 128+Signalnummer nachbilden wäre hier
// Überbau; wichtig ist nur, dass es nicht als 0 durchgeht.
process.exit(ergebnis.status === null ? 1 : ergebnis.status);
