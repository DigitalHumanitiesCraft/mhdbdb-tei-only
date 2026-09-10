/**
 * Multi-Lemma-Suchmodus „Im selben Vers" Tests (#106 Punkt 8)
 *
 * Verifiziert den dritten Suchmodus der Multi-Lemma-Suche: Kookkurrenz
 * beschränkt auf ein gemeinsames <l>, via lineStarts[]/lineEnds[]-Binärsuche
 * (Corpus-Index v4.1.0+). Ground-Truth aus dem PR (#211): „minne + herze"
 * liefert korpusweit 64 Vers-Treffer in 18 Texten, z. B. BUH Vers 98
 * („dâ bî ûz ir herzen blüejet || diu vil süeze minne").
 */

import { test, expect } from '@playwright/test';

test.describe('Issue #106.8: Multi-Lemma-Modus „Im selben Vers"', () => {
  test('Hash-Route mode=verse liefert Vers-Kookkurrenzen (minne + herze)', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#multi-lemma&lemmata=minne,herze&mode=verse');

    // Ergebnis-Header weist den Vers-Modus aus
    await expect(page.locator('#resultsContainer')).toContainText('(im selben Vers)', { timeout: 120000 });

    // Treffer tragen die Vers-Angabe statt eines Wortabstands
    await expect(page.locator('#resultsContainer')).toContainText('Gemeinsam in Vers');
    const results = await page.locator('#resultsContainer').textContent();
    expect(results).not.toContain('undefined');
    expect(results).not.toContain('null');
  });

  test('Unbekannter mode-Wert fällt auf Proximity zurück', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#multi-lemma&lemmata=minne,herze&mode=quatsch');

    // Fallback: Proximity-Ergebnisse (Wortabstand), kein Vers-Header
    await expect(page.locator('#resultsContainer')).toContainText('Kookkurrenz-Analyse', { timeout: 120000 });
    await expect(page.locator('#resultsContainer')).not.toContainText('(im selben Vers)');
  });
});

/**
 * #424: der Null-Treffer-Fall darf keine Trefferzahl behaupten
 *
 * Gemeldet von Alan van Beek im Testprotokoll zu #419, mit Screenshot und in
 * zwei aufeinanderfolgenden Testfällen: „da steht trotzdem 1 treffer, auch
 * wenn es 0 Treffer gibt". Ursache war, dass der Null-Treffer-Zweig seine
 * Erklärung als einelementiges Ergebnis-Array durch displayResults schickte,
 * und das zählt, was es bekommt.
 *
 * Das Lemmapaar steht hier NICHT als Konstante. Es wird zur Laufzeit aus dem
 * Korpus-Index abgeleitet, und zwar so, dass null Treffer eine Eigenschaft
 * der Daten sind und keine Hoffnung: zwei Lemmata mit disjunkten Textmengen
 * können in keinem Text nebeneinander stehen, egal wie groß der Abstand ist.
 * Ein festes Paar wäre die Zeitbombe, vor der lemma-occurrence-handoff.spec.js
 * warnt: der nächste Ingest macht daraus einen Treffer, und der Test wäre rot
 * aus einem Grund, der mit #424 nichts zu tun hat.
 */
test.describe('#424: Null-Treffer meldet keine Treffer', () => {
  test.beforeEach(() => {
    test.setTimeout(120000);
  });

  test('Kopf sagt (0 Treffer) und daneben steht keine Zahl', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#multi-lemma');
    await page.waitForFunction(
      () => window.playground?.corpusData?.texts?.length > 0 &&
            window.playground?.authorityData?.lemmata?.length > 0,
      null, { timeout: 120000 }
    );

    // Zwei Lemmata mit disjunkten Textmengen suchen, beide mit einer
    // Schreibform, die unbeschadet durch einen Hash passt.
    const paar = await page.evaluate(() => {
      const texte = window.playground.corpusData.texts;
      const formVon = new Map(
        window.playground.authorityData.lemmata
          .filter(l => /^[a-zäöüß]+$/.test(l.lemma || ''))
          .map(l => [l.id, l.lemma])
      );
      // Lemma -> Menge der Dateinamen, die es führen. Nur Lemmata mit
      // wenigen Zeugen, sonst ist die Disjunktheit unwahrscheinlich.
      const zeugen = new Map();
      for (const t of texte) {
        for (const id of Object.keys(t.lemmata || {})) {
          if (!formVon.has(id)) continue;
          let m = zeugen.get(id);
          if (!m) zeugen.set(id, (m = new Set()));
          m.add(t.filename);
        }
      }
      const selten = [...zeugen.entries()].filter(([, m]) => m.size === 1);
      for (let i = 0; i < selten.length; i++) {
        for (let j = i + 1; j < selten.length; j++) {
          const [idA, mA] = selten[i], [idB, mB] = selten[j];
          if ([...mA][0] === [...mB][0]) continue;
          if (formVon.get(idA) === formVon.get(idB)) continue;
          return {
            idA: idA.replace('lemma_', ''), formA: formVon.get(idA),
            idB: idB.replace('lemma_', ''), formB: formVon.get(idB),
          };
        }
      }
      return null;
    });

    // Ohne Paar beweist der Test nichts, und das soll er dann auch sagen.
    expect(paar, 'kein Lemmapaar mit disjunkten Textmengen im Korpus gefunden').not.toBeNull();

    await page.goto(
      `http://localhost:8080/playground/#multi-lemma&lemmata=${paar.formA},${paar.formB}` +
      `&ids=${paar.idA},${paar.idB}&mode=proximity&dist=10`
    );

    const container = page.locator('#resultsContainer');
    await expect(container).toContainText('(0 Treffer)', { timeout: 120000 });

    // Der Kern von #424: nirgends im Ergebnisbereich eine Trefferzahl über null.
    const text = await container.textContent();
    expect(text).not.toMatch(/[1-9]\d* Treffer/);

    // Und die Erklärung ist nicht mit dem Zähler verschwunden.
    await expect(container).toContainText('Keine Treffer im Abstand von 10 Wörtern');
  });
});
