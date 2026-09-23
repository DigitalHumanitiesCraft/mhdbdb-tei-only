#!/usr/bin/env node
/**
 * Dev-Server fuer `npm run serve`, auf dem Port aus test-port.js (#465).
 *
 * Liegt unter testing/ und nicht unter scripts/, weil er neben test-port.js
 * gehoert und scripts/ ein Inventar in scripts/README.md hat
 * (`check-doc-inventories.py`), das am 2026-09-23 eingefroren war.
 *
 * Ein Wrapper statt `http-server . -p $PORT` in package.json, aus zwei
 * gemessenen Gruenden: npm startet Skripte auf Windows in cmd.exe, wo `$VAR`
 * nicht expandiert; und http-server ohne `-p` nimmt `PORT` und sonst den
 * naechsten freien Port ab 8080, weicht also bei belegtem 8080 still auf 8081
 * aus. Hier steht `-p` deshalb immer da, ohne Variable mit 8080 wie vorher.
 *
 * Aufruf: npm run serve [-- weitere http-server-argumente]
 */

import { spawnSync } from 'child_process';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { testPort } from './test-port.js';

const repoWurzel = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const httpServer = resolve(repoWurzel, 'node_modules', 'http-server', 'bin', 'http-server');

let port;
try {
  port = testPort();
} catch (fehler) {
  console.error(fehler.message);
  process.exit(1);
}

const lauf = spawnSync(
  process.execPath,
  [httpServer, '.', '-p', String(port), '-c-1', ...process.argv.slice(2)],
  { cwd: repoWurzel, stdio: 'inherit' }
);

if (lauf.error) {
  console.error(`http-server nicht gestartet: ${lauf.error.message}`);
  process.exit(1);
}
process.exit(lauf.status ?? 1);
