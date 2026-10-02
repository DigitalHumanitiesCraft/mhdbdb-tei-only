/**
 * Dreißiger heißen "Strophe", Parzival-Bücher "Buch N" (#358)
 *
 * KZW 11.09.2026: ein `<div type="chapter" subtype="dreissiger">` (PZ, WH) wird
 * in der Leseansicht als "Strophe N" beschriftet, nicht als "Kapitel N";
 * `<milestone unit="book" n="II"/>` erscheint als Überschrift "Buch II" an
 * seiner Stelle. `type` bleibt `chapter`, die Verszählungs-Rücksetzung und die
 * Deep-Links hängen weiter daran.
 *
 * Die Spec rendert ein Testfragment mit dem echten Reader (extractAndFormatBody)
 * und zum Schluss das echte PZ (subtype und milestone kommen mit A3).
 */

import { test, expect } from '@playwright/test';

const NS = 'http://www.tei-c.org/ns/1.0';

// Zwei Dreißiger (der zweite beginnt mit Buch II mitten im Abschnitt, mit
// eigener Überschrift), ein gewöhnliches Kapitel als Gegenprobe, ein Lied.
const FRAGMENT = `<TEI xmlns="${NS}"><text><body>
  <div type="chapter" subtype="dreissiger" n="3">
    <l n="1">ein</l><l n="2">zwei</l>
    <milestone unit="book" n="II"/>
    <l n="3">drei</l>
  </div>
  <div type="chapter" subtype="dreissiger" n="4"><head>Aventiure</head><l n="1">vier</l></div>
  <div type="chapter" n="7"><l n="1">sieben</l></div>
  <div type="song" n="2"><l n="1">lied</l></div>
</body></text></TEI>`;

async function render(page) {
    return page.evaluate(async ({ xml }) => {
        const { TEITextReader } = await import('/assets/js/rendering/tei-text-reader.js');
        const doc = new DOMParser().parseFromString(xml, 'text/xml');
        if (doc.querySelector('parsererror')) throw new Error('XML parse failed');
        const reader = new TEITextReader(null, null, null);
        const { html } = reader.extractAndFormatBody(doc, null, []);
        const host = document.createElement('div');
        host.innerHTML = html;
        const headers = [...host.querySelectorAll('.tei-div')].map(d => ({
            type: d.dataset.type,
            n: d.dataset.n,
            // erste Überschrift des div, egal ob h3.section-head oder Label-Div
            head: (d.querySelector(':scope > .section-head, :scope > .tei-div-header')?.textContent || '').trim(),
        }));
        const books = [...host.querySelectorAll('.book-heading')].map(b => ({
            tag: b.tagName, text: b.textContent.trim(), book: b.dataset.book,
            // Position: Zahl der <l>-Zeilen vor der Überschrift im selben div
            before: [...b.parentElement.children].slice(0, [...b.parentElement.children].indexOf(b)).filter(c => c.classList.contains('verse-line')).length,
        }));
        return { headers, books, html };
    }, { xml: FRAGMENT });
}

test.beforeEach(async ({ page }) => {
    // Same-origin-Dokument für den dynamischen Import (wie position-parity.spec.js)
    await page.goto('/playground/');
});

test.describe('Dreißiger und Bücher (#358)', () => {

    test('Dreißiger heißen "Strophe N", ein gewöhnliches chapter bleibt "Kapitel N"', async ({ page }) => {
        const { headers } = await render(page);
        const byN = Object.fromEntries(headers.filter(h => h.type === 'chapter').map(h => [h.n, h.head]));

        expect(byN['3']).toBe('Strophe 3');
        // Mit eigener Überschrift steht das Label darüber, mit demselben neuen Wort
        expect(byN['4']).toMatch(/^Strophe 4/);
        // Gegenprobe: kein subtype, also unverändert
        expect(byN['7']).toBe('Kapitel 7');
        // Gegenprobe: andere Typen unberührt
        expect(headers.find(h => h.type === 'song').head).toBe('Lied 2');
    });

    test('type bleibt chapter: data-type unverändert', async ({ page }) => {
        const { headers } = await render(page);
        expect(headers.filter(h => h.type === 'chapter').map(h => h.n)).toEqual(['3', '4', '7']);
    });

    test('milestone unit="book" erscheint als "Buch II" an seiner Stelle, mitten im Dreißiger', async ({ page }) => {
        const { books } = await render(page);
        expect(books).toHaveLength(1);
        expect(books[0].text).toBe('Buch II');
        expect(books[0].book).toBe('II');
        expect(books[0].tag).toBe('H2');
        // zwei Verse stehen davor, die Überschrift schneidet den Dreißiger, ohne ihn zu teilen
        expect(books[0].before).toBe(2);
    });

    test('Buch am Anfang eines Dreißigers steht ÜBER "Strophe N", genau einmal', async ({ page }) => {
        const r = await page.evaluate(async () => {
            const { TEITextReader } = await import('/assets/js/rendering/tei-text-reader.js');
            const ns = 'http://www.tei-c.org/ns/1.0';
            const xml = `<TEI xmlns="${ns}"><text><body><div type="chapter" subtype="dreissiger" n="5"><milestone unit="book" n="III"/><l n="1">a</l><l n="2">b</l></div></body></text></TEI>`;
            const doc = new DOMParser().parseFromString(xml, 'text/xml');
            const { html } = new TEITextReader(null, null, null).extractAndFormatBody(doc, null, []);
            const host = document.createElement('div');
            host.innerHTML = html;
            const div = host.querySelector('.tei-div');
            return {
                order: [...div.children].filter(c => /^H[23]$/.test(c.tagName)).map(c => `${c.tagName}:${c.textContent.trim()}`),
                bookCount: host.querySelectorAll('.book-heading').length,
            };
        });
        expect(r.order).toEqual(['H2:Buch III', 'H3:Strophe 5']);
        expect(r.bookCount).toBe(1);
    });

    test('milestone ohne n oder mit anderer unit erzeugt keine Überschrift', async ({ page }) => {
        const n = await page.evaluate(async () => {
            const { TEITextReader } = await import('/assets/js/rendering/tei-text-reader.js');
            const ns = 'http://www.tei-c.org/ns/1.0';
            const xml = `<TEI xmlns="${ns}"><text><body><div type="chapter" n="1"><milestone unit="book"/><milestone unit="section" n="2"/><l n="1">x</l></div></body></text></TEI>`;
            const doc = new DOMParser().parseFromString(xml, 'text/xml');
            const { html } = new TEITextReader(null, null, null).extractAndFormatBody(doc, null, []);
            return (html.match(/book-heading/g) || []).length;
        });
        expect(n).toBe(0);
    });

    test('Buchnummer wird escaped', async ({ page }) => {
        const html = await page.evaluate(async () => {
            const { TEITextReader } = await import('/assets/js/rendering/tei-text-reader.js');
            const ns = 'http://www.tei-c.org/ns/1.0';
            const xml = `<TEI xmlns="${ns}"><text><body><div type="chapter" n="1"><milestone unit="book" n="&lt;b&gt;"/><l n="1">x</l></div></body></text></TEI>`;
            const doc = new DOMParser().parseFromString(xml, 'text/xml');
            return new TEITextReader(null, null, null).extractAndFormatBody(doc, null, []).html;
        });
        expect(html).not.toContain('<b>');
        expect(html).toContain('Buch &lt;b&gt;');
    });

    test('echtes PZ: 16 Bücher als Überschrift, jeder Dreißiger heißt Strophe', async ({ page }) => {
        const info = await page.evaluate(async () => {
            const { TEITextReader } = await import('/assets/js/rendering/tei-text-reader.js');
            const xml = await (await fetch('/tei/PZ.tei.xml')).text();
            const doc = new DOMParser().parseFromString(xml, 'text/xml');
            const ns = 'http://www.tei-c.org/ns/1.0';
            const milestones = [...doc.getElementsByTagNameNS(ns, 'milestone')]
                .filter(m => m.getAttribute('unit') === 'book');
            const { html } = new TEITextReader(null, null, null).extractAndFormatBody(doc, null, []);
            const host = document.createElement('div');
            host.innerHTML = html;
            const chapters = [...host.querySelectorAll('.tei-div[data-type="chapter"]')];
            const label = d => (d.querySelector(':scope > h3.section-head, :scope > .tei-div-header')?.textContent || '').trim();
            return {
                milestones: milestones.length,
                chapterDivs: doc.querySelectorAll('div[type="chapter"]').length,
                dreissigerDivs: doc.querySelectorAll('div[type="chapter"][subtype="dreissiger"]').length,
                renderedChapters: chapters.length,
                strophe: chapters.filter(d => /^Strophe \d+$/.test(label(d))).length,
                kapitel: chapters.filter(d => /^Kapitel/.test(label(d))).length,
                books: [...host.querySelectorAll('.book-heading')].map(b => b.textContent.trim()),
            };
        });
        expect(info.milestones).toBe(16);
        expect(info.dreissigerDivs).toBe(info.chapterDivs);
        expect(info.renderedChapters).toBe(info.chapterDivs);
        expect(info.strophe).toBe(info.chapterDivs);
        expect(info.kapitel).toBe(0);
        // 16 Überschriften, je genau einmal (Hoist ohne Doppelung), in Buchreihenfolge
        expect(info.books).toHaveLength(16);
        expect(new Set(info.books).size).toBe(16);
    });
});
