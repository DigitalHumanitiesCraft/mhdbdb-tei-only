/**
 * Ergebniskoepfe escapen die Sucheingabe (#427)
 *
 * Die Ergebniskoepfe des Playgrounds setzten den Suchbegriff roh ins
 * innerHTML. Normalerweise ist das Selbst-XSS und harmlos, weil eine
 * Schreibform vor der Anzeige durch die Lemma-Aufloesung laeuft und ein
 * Nichttreffer eine Fehlermeldung erzeugt. Der Router hat aber einen Weg
 * daran vorbei: traegt ein Term im Hash einen `ids`-Zeiger, nimmt
 * `resolveTerms` die ID und prueft die Schreibform nie
 * (multi-lemma-search.js). Ein geteilter Link fuehrt damit fremdes Markup in
 * die Seite dessen, der ihn oeffnet, also Reflected XSS.
 *
 * Der Test prueft die WIRKUNG und nicht die Schreibweise: er zaehlt Elemente
 * im Ergebnisbereich, statt auf "&lt;" zu pruefen. Eine Zusicherung auf den
 * escapten Text waere gruen, sobald jemand die Escape-Funktion durch eine
 * andere Schreibweise ersetzt, und rot, sobald jemand sie verbessert.
 *
 * Der Nutzlast-Term traegt einen Zeiger auf lemma_286 (arm, das Koerperteil),
 * der zweite auf lemma_4130 (minne). Gemessen am Korpus-Index vom 2026-09-10
 * treffen die beiden im Abstand 10 in 2 Texten mit 3 Rohtreffern zusammen: der
 * erste Test landet also im Treffer-Zweig und prueft displaySummaryResults,
 * den Pfad, den ein Besucher tatsaechlich sieht. Der zweite Test unten zielt
 * auf den Null-Treffer-Zweig, also displayHinweis.
 */

import { test, expect } from '@playwright/test';

const PLAYGROUND = 'http://localhost:8080/playground/';
// Kein Komma: der Router trennt die Terme daran (router.js).
const NUTZLAST = '<img src=x>';

test.describe('#427: Ergebniskopf escapt die Sucheingabe', () => {
  test.beforeEach(() => {
    test.setTimeout(120000);
  });

  test('Markup im Suchbegriff wird kein Element im Ergebnisbereich', async ({ page }) => {
    const hash = `#multi-lemma&lemmata=${encodeURIComponent(NUTZLAST)},minne`
      + '&ids=286,4130&mode=proximity&dist=10';
    await page.goto(PLAYGROUND + hash);

    const container = page.locator('#resultsContainer');
    await expect(container).toContainText('Kookkurrenz-Analyse', { timeout: 120000 });

    // Die Zusicherung: aus der Nutzlast ist kein Element geworden.
    await expect(container.locator('img')).toHaveCount(0);

    // Und der Begriff steht als TEXT da, ist also nicht stillschweigend
    // verschluckt worden. Ein Test, der nur "kein img" prueft, waere auch
    // dann gruen, wenn der Kopf den Begriff gar nicht mehr zeigte.
    await expect(container).toContainText(NUTZLAST);
  });

  test('derselbe Weg im Null-Treffer-Zweig', async ({ page }) => {
    // lemma_286 (arm, das Koerperteil) und lemma_308 (arzat, der Arzt).
    // Gemessen am Korpus-Index vom 2026-09-10: im Abstand 1 stehen die beiden
    // in 0 Texten mit 0 Treffern beieinander, der Kopf landet also wirklich im
    // Null-Treffer-Zweig.
    //
    // ACHTUNG beim Aendern: die Beschriftung MUSS zur ID passen. arm + vriunt
    // (lemma_7246) haette im Abstand 1 genau einen Treffer, wer also die ID an
    // eine Beschriftung "vriunt" anpasst, kippt den Test unbemerkt in den
    // Treffer-Zweig. Die Zusicherung selbst gilt in beiden Zweigen, die
    // Absicht dieses zweiten Tests aber nicht. Deshalb nagelt die letzte
    // Zusicherung den Zweig fest, statt nur davor zu warnen: '(0 Treffer)'
    // steht ausschliesslich im Kopf von displayHinweis, der Treffer-Zweig
    // schreibt dort '(max. N Woerter Abstand)' (Befund des Review-Bots auf
    // PR #428).
    const hash = `#multi-lemma&lemmata=${encodeURIComponent(NUTZLAST)},arzat`
      + '&ids=286,308&mode=proximity&dist=1';
    await page.goto(PLAYGROUND + hash);

    const container = page.locator('#resultsContainer');
    await expect(container).toContainText('Kookkurrenz-Analyse', { timeout: 120000 });
    await expect(container).toContainText('(0 Treffer)');
    await expect(container.locator('img')).toHaveCount(0);
    await expect(container).toContainText(NUTZLAST);
  });
});
