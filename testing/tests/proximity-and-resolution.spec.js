/**
 * Nähesuche-Fenster und Lemma-Auflösung im Playground (#169)
 *
 * Deckt die drei Befunde ab, die KZW am 28.07.2026 in #169 freigegeben hat:
 *
 * Befund #15 — die 3+-Lemma-Nähesuche maß jedes weitere Lemma nur gegen das
 *   Anker-Lemma. Bei „innerhalb 5 Wörter" passierten B bei Anker−5 und C bei
 *   Anker+5 beide, obwohl sie real 10 auseinanderliegen.
 * Befund #48 — der Überlappungs-Dedup behielt den zuerst startenden statt den
 *   distanzkürzesten Treffer, während Kommentar und Log das Gegenteil sagten.
 * Befund #51 — ein hartkodiertes Lemma-Wörterbuch umging die zentrale
 *   Auflösung und war in fünf von elf Einträgen bereits falsch.
 *
 * Die Fenster- und Dedup-Tests laufen gegen einen synthetischen Korpus, den
 * sie searchProximityUsingEnhancedIndex direkt übergeben: die Methode nimmt
 * corpusData als Parameter, deshalb braucht es dafür weder den 40-MB-Index
 * noch die UI, und die erwarteten Zahlen sind von Korpus-Änderungen unabhängig.
 */

import { test, expect } from '@playwright/test';

/**
 * Synthetischer Korpus: words[i] trägt die Lemma-ID an Wortposition i.
 * placements = { position: lemmaId }, alles andere ist Füll-Lemma lemma_999.
 */
function buildCorpus(placements, length = 200) {
    const words = new Array(length).fill('lemma_999');
    for (const [pos, id] of Object.entries(placements)) {
        words[Number(pos)] = `lemma_${id}`;
    }
    return {
        includedTexts: ['T1'],
        texts: [{ id: 'T1', filename: 'T1.tei.xml', title: 'Synthetischer Testtext', words }]
    };
}

async function runProximity(page, placements, lemmaIds, maxDistance, length = 200) {
    const corpus = buildCorpus(placements, length);
    return page.evaluate(async ({ corpus, lemmaIds, maxDistance }) => {
        const corpusData = { ...corpus, includedTexts: new Set(corpus.includedTexts) };
        return window.playground.teiManager.searchProximityUsingEnhancedIndex(
            lemmaIds, maxDistance, corpusData
        );
    }, { corpus, lemmaIds, maxDistance });
}

test.describe('#169 Befund #15: Nähesuche misst die Spanne, nicht den Ankerabstand', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');
        await page.waitForFunction(() => window.playground?.teiManager !== undefined,
            { timeout: 60000 });
    });

    test('B bei Anker−5 und C bei Anker+5 sind bei maxDistance 5 kein Treffer', async ({ page }) => {
        // Der Fall aus dem Issue: beide liegen einzeln in Ankernähe, zusammen
        // aber 10 Wörter auseinander. Vor dem Fix wurde er als Treffer
        // gemeldet — mit distance 10 im selben Ergebnis-Objekt.
        const placements = { 10: '2', 15: '1', 20: '3' };

        const zuEng = await runProximity(page, placements, ['1', '2', '3'], 5);
        expect(zuEng).toHaveLength(0);

        // Gegenprobe, damit der Test nicht bloß „findet nichts mehr" belegt:
        // bei maxDistance 10 trägt dieselbe Konstellation genau einen Treffer.
        const passend = await runProximity(page, placements, ['1', '2', '3'], 10);
        expect(passend).toHaveLength(1);
        expect(passend[0].distance).toBe(10);
        expect([...passend[0].matchPositions].sort((a, b) => a - b)).toEqual([10, 15, 20]);
    });

    test('gültiges Fenster wird gefunden, auch wenn die erste Position im Ankerfenster nicht passt', async ({ page }) => {
        // Der Grund, warum es nicht reicht, die alte Auswahl nachträglich zu
        // verwerfen: positions.find() nahm B = 90 (erste Position in
        // Ankernähe), damit wäre die Spanne 109 − 90 = 19 und der Treffer
        // fiele weg. Tragfähig ist B = 110 mit C = 109 und Anker 100.
        const treffer = await runProximity(
            page, { 100: '1', 90: '2', 110: '2', 109: '3' }, ['1', '2', '3'], 10
        );

        expect(treffer).toHaveLength(1);
        expect(treffer[0].distance).toBe(10);
        expect([...treffer[0].matchPositions].sort((a, b) => a - b)).toEqual([100, 109, 110]);
    });

    test('bei zwei Lemmata bleibt die Trefferzahl unverändert', async ({ page }) => {
        // KZWs Zusicherung aus #169: der Fix betrifft erst 3+ Lemmata. Mit
        // zwei Lemmata ist der Ankerabstand identisch mit der Spanne.
        const treffer = await runProximity(page, { 50: '1', 57: '2' }, ['1', '2'], 10);

        expect(treffer).toHaveLength(1);
        expect(treffer[0].distance).toBe(7);
    });

    test('maxDistance wird auf den deklarierten UI-Bereich geklemmt', async ({ page }) => {
        // Das Eingabefeld hat max="50", die Hash-Route prüft dist aber nur auf
        // > 0. Die Fenstersuche ist im Gegensatz zur alten Ankerprüfung von
        // der Distanz abhängig teuer, deshalb klemmt die Datenschicht selbst.
        const placements = { 100: '1', 160: '2' };  // 60 Wörter auseinander

        const ueberGrenze = await runProximity(page, placements, ['1', '2'], 9999, 300);
        expect(ueberGrenze).toHaveLength(0);

        // Gegenprobe: bei 60 wäre der Treffer da, wenn nicht geklemmt würde.
        // Der Clamp macht daraus 50, also bleibt es bei null Treffern.
        const knappDrunter = await runProximity(page, placements, ['1', '2'], 60, 300);
        expect(knappDrunter).toHaveLength(0);

        // Und bei 50 trägt eine Konstellation innerhalb der Grenze weiterhin.
        const innerhalb = await runProximity(page, { 100: '1', 140: '2' }, ['1', '2'], 50, 300);
        expect(innerhalb).toHaveLength(1);
        expect(innerhalb[0].distance).toBe(40);
    });

    test('findCoveringWindow: kleinste tragfähige Spanne, sonst null', async ({ page }) => {
        const ergebnis = await page.evaluate(() => {
            const tm = window.playground.teiManager;
            return {
                keineWeiteren: tm.findCoveringWindow(100, [], 5),
                unerreichbar: tm.findCoveringWindow(100, [[200]], 5),
                kleinsteSpanne: tm.findCoveringWindow(100, [[95, 103]], 10),
                ueberAnkerHinaus: tm.findCoveringWindow(100, [[90, 110], [109]], 10),
                zuWeit: tm.findCoveringWindow(100, [[95], [105]], 5)
            };
        });

        expect(ergebnis.keineWeiteren).toEqual([]);
        expect(ergebnis.unerreichbar).toBeNull();
        // 103 liegt 3 vom Anker, 95 liegt 5 — die kleinere Spanne gewinnt.
        expect(ergebnis.kleinsteSpanne).toEqual([103]);
        expect(ergebnis.ueberAnkerHinaus).toEqual([110, 109]);
        // 95 und 105 liegen einzeln in Reichweite, zusammen 10 auseinander.
        expect(ergebnis.zuWeit).toBeNull();
    });
});

test.describe('#169 Befund #48: Dedup behält den distanzkürzesten Treffer', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');
        await page.waitForFunction(() => window.playground?.teiManager !== undefined,
            { timeout: 60000 });
    });

    test('bei Überlappung gewinnt die kleinere Distanz, nicht der frühere Start', async ({ page }) => {
        // Anker A bei 100 und 120, Partner B bei 108 und 121.
        //   Treffer 1: 100/108, Distanz 8,  Kontext [90, 119]
        //   Treffer 2: 120/121, Distanz 1,  Kontext [110, 132]
        // Die Kontexte überlappen. Vorher entschied contextStart, also gewann
        // Distanz 8; jetzt gewinnt Distanz 1.
        const treffer = await runProximity(
            page, { 100: '1', 120: '1', 108: '2', 121: '2' }, ['1', '2'], 10
        );

        expect(treffer).toHaveLength(1);
        expect(treffer[0].distance).toBe(1);
        expect([...treffer[0].matchPositions].sort((a, b) => a - b)).toEqual([120, 121]);
    });

    test('bei gleicher Distanz gewinnt der frühere Treffer', async ({ page }) => {
        // Der zweite Teil des Sortierschlüssels, (distance, contextStart).
        // Zwei überlappende Treffer mit identischer Distanz 2:
        //   Anker 100 / Partner 102, Kontext [90, 113]
        //   Anker 108 / Partner 110, Kontext [98, 121]
        // Ohne den contextStart-Tiebreak hinge das Ergebnis daran, welchen
        // die Sortierung zufällig vornliegen lässt.
        const treffer = await runProximity(
            page, { 100: '1', 108: '1', 102: '2', 110: '2' }, ['1', '2'], 10
        );

        expect(treffer).toHaveLength(1);
        expect(treffer[0].distance).toBe(2);
        expect([...treffer[0].matchPositions].sort((a, b) => a - b)).toEqual([100, 102]);
    });

    test('nicht überlappende Treffer bleiben alle erhalten, in Lesereihenfolge', async ({ page }) => {
        // Weit auseinander: kein Dedup. Die Ausgabe folgt dem Textverlauf,
        // obwohl intern nach Distanz ausgewählt wird.
        const treffer = await runProximity(
            page, { 20: '1', 22: '2', 150: '1', 159: '2' }, ['1', '2'], 10, 300
        );

        expect(treffer).toHaveLength(2);
        expect(treffer.map(t => t.distance)).toEqual([2, 9]);
        expect(treffer[0].contextStart).toBeLessThan(treffer[1].contextStart);
    });
});

test.describe('#169 Befund #51: Fast-Path-Wörterbuch ist gestrichen', () => {
    test('die elf früheren Fast-Path-Eingaben lösen regulär auf', async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');
        await page.waitForFunction(() => {
            return window.playground?.corpusData?.texts?.length > 0 &&
                   window.playground?.ui?.multiLemmaSearch;
        }, { timeout: 60000 });

        const aufgeloest = await page.evaluate(() => {
            const explorer = window.playground.ui.multiLemmaSearch.teiExplorer;
            const eingaben = ['brôt', 'brot', 'wîn', 'win', 'wein', 'fleisch',
                              'vleisch', 'käse', 'kæse', 'bier', 'bîr'];
            const ergebnis = {};
            for (const e of eingaben) ergebnis[e] = explorer.resolveLemmaIds([e])[0] || null;
            return ergebnis;
        });

        // Die sechs Einträge, die der Fast-Path richtig hatte: unverändert.
        expect(aufgeloest['brôt']).toBe('879');
        expect(aufgeloest['brot']).toBe('879');
        expect(aufgeloest['wîn']).toBe('7532');
        expect(aufgeloest['win']).toBe('7532');
        expect(aufgeloest['wein']).toBe('7532');
        expect(aufgeloest['bîr']).toBe('712');

        // Die fünf, die er falsch hatte: jetzt das inhaltlich richtige Lemma.
        expect(aufgeloest['fleisch']).toBe('7121');   // war lemma_1816 forma
        expect(aufgeloest['vleisch']).toBe('7121');   // war lemma_1816 forma
        expect(aufgeloest['käse']).toBe('3175');      // war lemma_26713 eierkæse
        expect(aufgeloest['kæse']).toBe('3175');      // war lemma_26713 eierkæse
        expect(aufgeloest['bier']).toBe('702');       // war lemma_712 bir (Birne)
    });

    test('findLemmaIdByOrthography existiert nicht mehr', async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');
        await page.waitForFunction(() => window.playground?.ui?.multiLemmaSearch !== undefined,
            { timeout: 60000 });

        const vorhanden = await page.evaluate(() => {
            const explorer = window.playground.ui.multiLemmaSearch.teiExplorer;
            return typeof explorer.findLemmaIdByOrthography;
        });

        expect(vorhanden).toBe('undefined');
    });
});

test.describe('Aufräumrunde: doppelte Lemma-IDs degenerieren die Kookkurrenz-Suche', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');
        await page.waitForFunction(() => window.playground?.teiManager !== undefined,
            { timeout: 60000 });
    });

    test('dieselbe ID zweimal ergibt keine Treffer mit Abstand 0', async ({ page }) => {
        // Ohne Guard hat findCoveringWindow keine abzudeckende Restliste mehr
        // und gibt [] zurück. Ein leeres Array ist truthy, also galt JEDE
        // Fundstelle als Treffer mit Abstand 0. Der synthetische Text trägt
        // lemma_1 an drei Stellen; ohne Guard wären das drei Treffer.
        const doppelt = await runProximity(page, { 10: '1', 40: '1', 90: '1' }, ['1', '1'], 10);
        expect(doppelt).toHaveLength(0);

        // Ein einzelnes Lemma ebenso.
        const einzeln = await runProximity(page, { 10: '1', 40: '1' }, ['1'], 10);
        expect(einzeln).toHaveLength(0);

        // Gegenprobe: mit zwei verschiedenen Lemmata sucht sie normal weiter.
        const echt = await runProximity(page, { 10: '1', 14: '2' }, ['1', '2'], 10);
        expect(echt).toHaveLength(1);
        expect(echt[0].distance).toBe(4);
    });

    test('praefixierte und bare Schreibweise derselben ID gelten als eine', async ({ page }) => {
        // Der Code unter dem Guard behandelt "1" und "lemma_1" ohnehin als
        // dieselbe ID. Zaehlte der Guard sie als zwei, kaeme das Paar durch
        // und die doppelte Positionsliste deckte sich selbst ab.
        const gemischt = await runProximity(page, { 10: '1', 40: '1' }, ['1', 'lemma_1'], 10);
        expect(gemischt).toHaveLength(0);

        // Und mit einem echten dritten Lemma bleibt es eine Suche ueber ZWEI.
        // Die beobachtbare Folge steckt in matchPositions, nicht in der
        // Distanz: ohne Dedup stuende die doppelte Positionsliste ein zweites
        // Mal unter den abzudeckenden, und die Trefferposition erschiene
        // doppelt ([12, 12, 30] statt [12, 30]). In der Oberflaeche faellt
        // das heute nicht auf (matchPositions wird dort nur als Math.min
        // fuer die Sprungmarke gelesen), deshalb wird es hier auf
        // API-Ebene festgenagelt. Die Distanz aendert sich NICHT, weil lemma_2 ohnehin
        // abgedeckt werden muss und windowStart = firstPos immer tragfaehig
        // ist; eine Zusicherung auf die Distanz allein wuerde den Dedup also
        // nicht pruefen.
        const mitDrittem = await runProximity(
            page, { 10: '1', 12: '1', 30: '2' }, ['1', 'lemma_1', '2'], 25
        );
        expect(mitDrittem).toHaveLength(1);
        expect(mitDrittem[0].distance).toBe(18);
        expect(mitDrittem[0].matchPositions).toHaveLength(2);
        expect([...mitDrittem[0].matchPositions].sort((a, b) => a - b)).toEqual([12, 30]);
    });

    test('die Vers-Suche verweigert dieselbe Arbeit', async ({ page }) => {
        // Eigener Aufbau: die Vers-Suche liest die Reverse-Map lemmata{} und
        // braucht Versgrenzen. Zwei Verse, im ersten stehen beide Lemmata.
        const treffer = await page.evaluate(async () => {
            const korpus = {
                includedTexts: new Set(['T1']),
                texts: [{
                    id: 'T1', filename: 'T1.tei.xml', title: 'Verstext',
                    words: ['lemma_1', 'lemma_2', 'lemma_9', 'lemma_1'],
                    lemmata: { lemma_1: [0, 3], lemma_2: [1] },
                    lineStarts: [0, 2], lineEnds: [1, 3]
                }]
            };
            const tm = window.playground.teiManager;
            const mitDrittem = tm.searchVerseUsingEnhancedIndex(['1', 'lemma_1', '2'], korpus);
            return {
                echt: tm.searchVerseUsingEnhancedIndex(['1', '2'], korpus).length,
                doppelt: tm.searchVerseUsingEnhancedIndex(['1', 'lemma_1'], korpus).length,
                einzeln: tm.searchVerseUsingEnhancedIndex(['1'], korpus).length,
                mitDrittemAnzahl: mitDrittem.length,
                mitDrittemPositionen: mitDrittem[0] ? mitDrittem[0].matchPositions.length : null
            };
        });

        expect(treffer.echt).toBe(1);
        // Ohne Guard waere hier JEDER Vers mit lemma_1 ein Treffer, also 2.
        expect(treffer.doppelt).toBe(0);
        expect(treffer.einzeln).toBe(0);

        // Und wie im Naehe-Pfad zeigt sich der Dedup an matchPositions: ohne
        // ihn stuende die Position von lemma_1 zweimal darin.
        expect(treffer.mitDrittemAnzahl).toBe(1);
        expect(treffer.mitDrittemPositionen).toBe(2);
    });

    test('resolveLemmaIds liefert jede Lemma-ID nur einmal', async ({ page }) => {
        // Auf die geladenen Authority-Daten warten, nicht nur auf die
        // UI-Klasse: resolveLemmaIds fragt den Authority-Manager, und solange
        // dessen Lemmaliste leer ist, liefert es kommentarlos [] statt zu
        // scheitern. Ohne diese Bedingung ist der Test ein Münzwurf.
        await page.waitForFunction(
            () => window.playground?.ui?.multiLemmaSearch !== undefined &&
                  window.playground?.authorityData?.lemmata?.length > 0,
            { timeout: 60000 }
        );

        // „wîn" trifft Stufe 1 (eigenes Lemma), „wein" Stufe 2 (belegte
        // Variante). Beide landen auf lemma_7532, ohne Dedup stand die ID
        // zweimal in der Liste und die Nähesuche lief in die Degeneration.
        const ids = await page.evaluate(() => {
            const explorer = window.playground.ui.multiLemmaSearch.teiExplorer;
            return explorer.resolveLemmaIds(['wîn', 'wein']);
        });

        // Geprüft wird die Eigenschaft, nicht das ID-Paar: welche ID „wein"
        // trifft, kann sich ändern (die Lemma-IDs wurden schon einmal neu
        // vergeben, siehe den Fast-Path-Kommentar in tei-ui.js), der Dedup
        // bleibt davon unberührt.
        expect(ids.length).toBe(1);
        expect(new Set(ids).size).toBe(ids.length);
    });
});
