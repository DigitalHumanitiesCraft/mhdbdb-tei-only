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

**Why:** Die Ports 8080/8081 sind maschinenweit vergeben und die Maschine war knapp an Speicher; die Runde musste ohne Server auskommen und hat trotzdem alle Behauptungen des Auftrags nachmessen koennen.
**How to apply:** Bei jeder weiteren Runde an run-tests.js oder playwright.config.js zuerst diese Proben, Volllauf nur beim Aufrufer.
