/**
 * Python-Interpreter auflösen, statt einen Namen zu raten (#318 Punkt 6).
 *
 * Vorher stand `python3.13` als fester String an neun Stellen: drei Aufrufe
 * in den beiden Paritätstests und sechs Vorkommen in fünf npm-Skripten in
 * `package.json` (`build:data` enthält zwei), darunter `build:corpus`,
 * `build:authority` und `build:api`, also der in DEVELOPMENT.md
 * dokumentierte Build-Weg.
 *
 * Dieser Name ist keine verlässliche Zusage. Unter Windows existiert er nur,
 * wenn Python aus dem Microsoft Store kommt; dann liegt er als
 * App-Execution-Alias in %LOCALAPPDATA%\Microsoft\WindowsApps. Auf dem
 * Rechner, auf dem dieser Kommentar entstanden ist, ist es genau so:
 * `python3.13`, `python3` und `python` zeigen alle drei dorthin, `py` fehlt.
 *
 * Bei einer Installation von python.org ist es umgekehrt, und deshalb steht
 * `py` mit in der Liste: der Installer setzt `python.exe` in seiner
 * Voreinstellung NICHT in den PATH, registriert aber den Launcher `py`. Ohne
 * ihn scheiterte die Auflösung ausgerechnet in dem Fall, für den sie gebaut
 * ist. `py` steht zuletzt, damit eine vorhandene versionsgenaue Installation
 * vorgeht; meldet der Launcher eine ältere Voreinstellung (`PY_PYTHON`),
 * sortiert ihn die Versionsprüfung aus.
 *
 * Gemerkt wird nicht der Name, sondern der Pfad, den der geprüfte Interpreter
 * selbst meldet. Der Grund steht bei der Auflösung: ein Name allein bindet
 * nicht, sobald ein Skript mit Shebang läuft.
 *
 * Gefordert sind 3.13 oder neuer, weil das die Projektvorgabe ist
 * (DEVELOPMENT.md, Prerequisites).
 *
 * Fehlt jeder Kandidat, ist das ein harter Fehler mit der Liste des
 * Versuchten. Ein stilles Überspringen wäre die schlechtere Wahl: die beiden
 * Specs sind die einzigen Wächter über die sprachübergreifenden Verträge
 * (CONTRACTS §A Normalisierung, §B Positionszählung), und ein übersprungener
 * Wächter sieht im Report aus wie ein bestandener.
 *
 * Override für abweichende Setups (venv, Conda, mehrere Versionen
 * nebeneinander): MHDBDB_PYTHON=/pfad/zu/python npm test
 *
 * Der Override nimmt einen Pfad, keine Kommandozeile: "py -3.13" geht nicht.
 * Ein naives Zerlegen an Leerzeichen bräche an `C:\Program Files\...`, und
 * mit `py` in der Kandidatenliste gibt es den Bedarf nicht. Er sollte auf
 * die echte `python.exe` zeigen und nicht auf ein `.bat`-Shim (pyenv-win):
 * Node lehnt seit dem CVE-Fix Shims ohne `shell: true` mit EINVAL ab.
 *
 * Aufruf aus npm-Skripten über `node scripts/run-python.js <skript.py>`.
 */

import { execFileSync } from 'child_process';

const KANDIDATEN = ['python3.13', 'python3', 'python', 'py'];
const MIN_MAJOR = 3;
const MIN_MINOR = 13;

let aufgeloest = null;

/**
 * Pfad oder Name eines nutzbaren Interpreters. Ergebnis wird gemerkt, damit
 * nicht jeder Testfall die Kandidaten erneut durchprobiert.
 */
export function resolvePython() {
  if (aufgeloest) return aufgeloest;

  const kandidaten = process.env.MHDBDB_PYTHON
    ? [process.env.MHDBDB_PYTHON]
    : KANDIDATEN;
  const versuche = [];

  for (const bin of kandidaten) {
    let ausgabe;
    try {
      ausgabe = execFileSync(bin, ['--version'], {
        encoding: 'utf-8',
        stdio: ['ignore', 'pipe', 'pipe'],
      }).trim();
    } catch (err) {
      versuche.push(`${bin}: nicht ausführbar (${err.code || err.message})`);
      continue;
    }
    // Python 2 schrieb die Version nach stderr, 3.4+ nach stdout. Wir lesen
    // stdout; eine Fassung, die hier leer ist, ist ohnehin zu alt.
    const treffer = ausgabe.match(/(\d+)\.(\d+)/);
    if (!treffer) {
      versuche.push(`${bin}: unverständliche Versionsausgabe "${ausgabe}"`);
      continue;
    }
    const [major, minor] = [Number(treffer[1]), Number(treffer[2])];
    if (major < MIN_MAJOR || (major === MIN_MAJOR && minor < MIN_MINOR)) {
      versuche.push(`${bin}: ${ausgabe}, gebraucht wird ${MIN_MAJOR}.${MIN_MINOR}+`);
      continue;
    }
    // Ab hier ist die Version geprüft, der Name aber noch nicht bindend: alle
    // aufgerufenen Skripte tragen `#!/usr/bin/env python3`, und der Windows-
    // Launcher nimmt genau diese Form beim Wort. Er durchsucht dann zuerst den
    // PATH nach `python3` und greift erst danach auf seine Versionslogik
    // (`PY_PYTHON3`) zurück. Im Mischversions-Fall, für den `py` überhaupt in
    // der Liste steht, liefe das Skript also womöglich unter der Fassung, die
    // die Prüfung oben gerade aussortiert hat. Bei `-c` tritt das nicht auf,
    // weil es dort keine Shebang gibt: schon diese Inkonsistenz zwischen den
    // beiden Aufrufformen wäre ein Fehler.
    //
    // Deshalb den Interpreter nach seinem eigenen Pfad fragen. Das läuft in
    // genau der Fassung, die eben die Version gemeldet hat, und macht das
    // Ergebnis für jede Aufrufform gleich. Ein aktiviertes venv zeigt damit
    // ebenfalls auf sein eigenes python.
    let pfad = '';
    try {
      pfad = execFileSync(
        bin,
        ['-c', 'import sys; sys.stdout.write(sys.executable)'],
        // pythonEnv() ist hier nicht Kosmetik: bei gepiptem stdout kodiert
        // Python unter Windows sonst mit der ANSI-Codepage, Node liest aber
        // UTF-8. Ein Pfad mit Umlaut (python.org installiert nach
        // C:\Users\<Name>\AppData\Local\Programs\Python\...) käme mit
        // Ersatzzeichen zurück, und der spätere Start scheiterte mit ENOENT,
        // obwohl der bloße Name funktioniert hätte. Das wäre der einzige
        // Fall, in dem der aufgelöste Pfad schlechter ist als der Name.
        { encoding: 'utf-8', stdio: ['ignore', 'pipe', 'pipe'], env: pythonEnv() }
      ).trim();
    } catch {
      // Eingebettete Fassungen können `sys.executable` leer lassen. Dann
      // bleibt der Name, der eben nachweislich lief.
    }
    aufgeloest = pfad || bin;
    return aufgeloest;
  }

  throw new Error(
    `Kein Python ${MIN_MAJOR}.${MIN_MINOR}+ gefunden. Versucht:\n  ` +
    versuche.join('\n  ') +
    '\nAbhilfe: Python 3.13+ installieren oder MHDBDB_PYTHON auf den ' +
    'Interpreter setzen (z.B. MHDBDB_PYTHON=.venv/bin/python npm test).'
  );
}

/**
 * Standard-Umgebung für Python-Aufrufe.
 *
 * PYTHONIOENCODING ist nicht Kosmetik: die Paritätstests vergleichen Strings
 * mit mittelhochdeutschen Sonderzeichen, und Pythons stdout folgt unter
 * Windows sonst der Konsolen-Codepage (cp1252). Ein `ŏ` käme dann als
 * Ersatzzeichen zurück, und der Test meldete eine Paritätsverletzung, die
 * keine ist. Dieselbe Codepage tötet unter Windows Audit-Skripte an ihrer
 * eigenen Ausgabe; dort steht deshalb ein io-Wrapper im Skript (#329).
 */
export function pythonEnv(extra = {}) {
  return { ...process.env, PYTHONIOENCODING: 'utf-8', ...extra };
}
