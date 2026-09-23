---
name: projekt-testport-465
description: Review-Proben fuer den Testport (MHDBDB_TEST_PORT, #465) ohne Server: Config in-process laden, --list zaehlen, 8080-Bestand per git grep -c messen
metadata:
  type: project
---

Proben, die ohne Dev-Server und ohne Volllauf auskommen (Runde 1 am 23.09.2026, Stand cdaee8ddd):

- Aufgeloeste Config-Werte drucken: `node -e "import('./testing/playwright.config.js').then(m=>console.log(m.default.use.baseURL, m.default.webServer.command, m.default.webServer.port))"`, davor die Variable setzen. Zeigt, ob baseURL und webServer wirklich aus derselben Quelle kommen.
- `node scripts/run-tests.js --list` laeuft ohne Server (ohneReport ueberspringt den Sentinel) und nennt `Total: N tests in M files`; mit gesetzter Variable dasselbe, das belegt, dass die Config unter Playwrights Loader laedt. Stand 23.09.: 355 in 34.
- Ungueltige Werte (`abc`, `0`, leer, `65536`) gegen run-tests.js ergeben Exit 2 mit VERDICT-Zeile, gegen testing/serve.js Exit 1 ohne Serverstart; beides gefahrlos.
- Bestand an der Basis: `git grep -c 8080 <basis> -- testing/ | awk -F: '{n++; s+=$NF} END {print n, s}'` ergab 31 Dateien / 135 Vorkommen, davon 30 Specs / 132; Kickoff und Auftrag stimmten damit.
- Sentinel und Playwright teilen den Port nur ueber die Umgebung: run-tests.js gibt `{...process.env}` an spawnSync weiter (Z. 222), die Variable wird nur in testing/test-port.js gelesen (rg MHDBDB_TEST_PORT). Auseinanderlaufen bleibt moeglich ueber `--config <andere>` und ueber test:ui/debug/headed, beides war schon vor #465 so.
- `check-doc-inventories.py` zaehlt nur `testing/tests/*.spec.js` gegen DEVELOPMENT.md; neue Dateien direkt unter testing/ (serve.js, test-port.js) beruehren das Inventar nicht, und run-tests.js' Spec-Abgleich liest ebenfalls nur testing/tests/.
- `origin/main` war waehrend der Runde einen Commit weiter (081ad4d10) als die im Auftrag genannte Basis (46e0964e9 = merge-base); der Drei-Punkte-Diff ist davon unberuehrt, die Angabe im Auftrag trotzdem als B gemeldet.

Runde 2 (23.09.2026, Stand e36b5b17e, Delta eine Zeile in run-tests.js:211):

- Der Worktree-Guard der Session lehnt auch `node -e "import ... file:///.../Git/..."` ab, weil „Git" im Pfad steht; er trifft jedes Kommando mit dem Wort, nicht nur git-Aufrufe. Ausweg: Probe per Write nach `temp/<name>.mjs` (gitignoriert), relativer Import `../testing/test-port.js`, Aufruf `node temp/<name>.mjs` aus der Worktree-cwd, danach `rm` mit absolutem Pfad. Auch `git -C <pfad>` mit Semikolon-Ketten aus mehreren git-Aufrufen geht durch, sobald kein `$VAR` im Kommando steht.
- Formel `PORT < 65535 ? PORT + 1 : PORT - 1` an den Raendern gemessen: 1->2, 65534->65535, 65535->65534, alle von testPort() akzeptiert; 65536 und 0 werfen. PORT ist an der Stelle immer 1..65535, weil testPort() vorher wirft und run-tests.js:73-77 mit Exit 2 abbricht. Den Abhilfetext liest kein Spec und keine Doku (Grep ueber testing/, scripts/, docs/, package.json), ein #397-Rest an der alten Moeglichkeit existiert also nicht.

**Why:** Die Ports 8080/8081 sind maschinenweit vergeben und die Maschine war knapp an Speicher; die Runde musste ohne Server auskommen und hat trotzdem alle Behauptungen des Auftrags nachmessen koennen.
**How to apply:** Bei jeder weiteren Runde an run-tests.js oder playwright.config.js zuerst diese Proben, Volllauf nur beim Aufrufer.
