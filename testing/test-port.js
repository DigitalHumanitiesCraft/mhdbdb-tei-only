/**
 * Port des lokalen Testservers, fuer alle, die ihn kennen muessen (#465).
 *
 * Bis zum 2026-09-23 stand 8080 an vier Stellen fest: `scripts/run-tests.js`,
 * `baseURL` und `webServer` in `playwright.config.js`, `npm run serve`. Zwei
 * Worktrees konnten deshalb nicht gleichzeitig testen: der zweite traf den
 * Server des ersten, und `run-tests.js` brach richtigerweise mit Exit 2 ab.
 *
 * Diese Datei ist die einzige Stelle, an der die Variable gelesen wird. Das
 * ist keine Stilfrage: `run-tests.js` prueft per Sentinel, ob der Server auf
 * dem Port unser Arbeitsbaum ist, und Playwright verwendet einen Server am
 * Port der Config wieder. Lesen beide die Variable verschieden, prueft der
 * Sentinel einen anderen Port als den, gegen den die Suite laeuft, und die
 * Pruefung ist gruen, ohne etwas zu pruefen.
 *
 * Ohne gesetzte Variable ist es 8080, wie vorher. Jeder andere Wert muss eine
 * Ganzzahl von 1 bis 65535 sein, sonst harter Fehler: 0 hiesse fuer
 * http-server "such dir einen freien", und ein Tippfehler darf nicht still auf
 * die Vorgabe zurueckfallen, denn dann testet der Lauf auf 8080, waehrend
 * jemand glaubt, er sei ausgewichen.
 *
 * Aufruf: MHDBDB_TEST_PORT=8081 npm test (Git Bash)
 *         $env:MHDBDB_TEST_PORT=8081; npm test (PowerShell)
 */

export const PORT_VARIABLE = 'MHDBDB_TEST_PORT';
export const VORGABE_PORT = 8080;

export function testPort(umgebung = process.env) {
  const roh = umgebung[PORT_VARIABLE];
  if (roh === undefined) return VORGABE_PORT;
  const port = /^[0-9]+$/.test(roh) ? Number(roh) : NaN;
  if (!(port >= 1 && port <= 65535)) {
    throw new Error(`${PORT_VARIABLE}="${roh}" ist kein Port (erwartet: Ganzzahl 1 bis 65535, ohne Variable ${VORGABE_PORT}).`);
  }
  return port;
}

export function basisUrl(umgebung = process.env) {
  return `http://localhost:${testPort(umgebung)}`;
}
