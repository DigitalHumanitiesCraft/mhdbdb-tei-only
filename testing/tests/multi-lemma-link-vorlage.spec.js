/**
 * Link-Vorlage der Begriffshilfe (#498)
 *
 * Die Begriffshilfe lässt eine KI Links bauen nach
 * `playground/#multi-lemma&lemmata=<L1>,<L2>&dist=<N>` (ohne `&mode=`).
 * Diese Spec öffnet genau diese Form frisch, dazu die Varianten mit
 * HTML-escaptem `&amp;` und `&#38;` und ein Umlaut-Lemma. Geprüft wird Kopfzeile (beide Wörter, Abstand) und eine
 * Trefferzahl > 0, nicht eine feste Zahl.
 */

import { test, expect } from '@playwright/test';

const FAELLE = [
  { name: 'Vorlagenform ohne mode', hash: '#multi-lemma&lemmata=kiusche,vrouwe&dist=5', a: 'kiusche', b: 'vrouwe', dist: 5 },
  { name: 'mit HTML-escaptem &amp;', hash: '#multi-lemma&amp;lemmata=kiusche,vrouwe&amp;dist=5', a: 'kiusche', b: 'vrouwe', dist: 5 },
  { name: 'mit numerischem &#38;', hash: '#multi-lemma&#38;lemmata=kiusche,vrouwe&#38;dist=5', a: 'kiusche', b: 'vrouwe', dist: 5 },
  { name: 'Umlaut-Lemma (vürhten)', hash: '#multi-lemma&lemmata=schande,vürhten&dist=10', a: 'schande', b: 'vürhten', dist: 10 },
];

test.describe('#498: Link-Vorlage der Begriffshilfe öffnet die Suche', () => {
  test.beforeEach(() => {
    test.setTimeout(180000);
  });

  for (const f of FAELLE) {
    test(f.name, async ({ page }) => {
      await page.goto('/playground/' + f.hash);

      const ergebnis = page.locator('#resultsContainer');
      await expect(ergebnis).toContainText(
        `Kookkurrenz-Analyse: ${f.a} + ${f.b} (max. ${f.dist} Wörter Abstand)`,
        { timeout: 150000 }
      );

      const text = await ergebnis.textContent();
      expect(text).not.toContain('(0 Treffer)');
      const m = text.match(/(\d[\d.,]*)\s+Nähe-Beziehungen im Abstand von max\. (\d+) Wörtern/);
      expect(m, 'Trefferzeile fehlt').not.toBeNull();
      expect(parseInt(m[1].replace(/[.,]/g, ''), 10)).toBeGreaterThan(0);
      expect(parseInt(m[2], 10)).toBe(f.dist);
    });
  }
});
