/**
 * Übergabe vom Lemmata-Explorer in die Belegsuche (#58)
 *
 * Aus der Trefferliste des Lemmata-Explorers führte bisher kein Weg in die
 * Belegsuche. Neu ist ein Knopf pro Treffer, der die Multi-Lemma-Route mit
 * einem zusätzlichen Parameter `ids` aufruft, positionsgleich zu `lemmata`
 * gepaart:
 *
 *     #multi-lemma&lemmata=arm&ids=286&mode=document
 *
 * Warum die ID und nicht die Schreibform allein: `searchLemmaByOrthography`
 * liefert bei Homographen ALLE Treffer, nach Korpusfrequenz sortiert, und
 * `resolveLemmaIds` nimmt davon `matches[0]` (#163/#164). Wer im Explorer
 * gezielt das seltenere Lemma anklickt, landete damit stillschweigend beim
 * häufigeren.
 *
 * Leitbeispiel, gemessen am 2026-08-07 gegen `authority-files/lexicon.xml`
 * (43.879 entry-Elemente) und `data/corpus-index.json.gz` v4.2.1:
 *
 *   102 Schreibformen tragen mehr als ein entry-Element, zusammen 216 Lemmata.
 *   `arm` ist eines davon und hat genau zwei:
 *     - lemma_285 `arm` (POS ADJ ADV GRA NOM, das Adjektiv „arm"):
 *       820 Belege in 207 Texten
 *     - lemma_286 `arm` (POS NOM, das Körperteil „Arm"):
 *       157 Belege in 40 Texten
 *   Kein weiteres Lemma normalisiert auf „arm", die Auflösung bricht also in
 *   Stufe 1 ab und liefert diese beiden. Frequenzsortiert gewinnt lemma_285,
 *   das ist die Auflösung OHNE Zeiger.
 *
 * Die Tests unterscheiden die beiden Lemmata an disjunkten Texten statt an
 * Trefferzahlen, damit laufender Ingest sie nicht aus einem Grund rot macht,
 * der nichts mit der Übergabe zu tun hat. Am 2026-08-07 waren das 11 Texte,
 * die lemma_286 führen und lemma_285 nicht (darunter BIL, Das Bild), und 178
 * umgekehrt (darunter PZ, Parzival).
 *
 * Welche Texte es sind, steht hier aber NICHT als Konstante. Die Zeugen werden
 * zur Laufzeit aus dem geladenen Korpus-Index abgeleitet (`zeugen()` unten).
 * Ein fester Name wäre genau die Zeitbombe, die der Absatz oben vermeiden
 * will: sobald ein Ingest `arm` in BIL oder PZ verschiebt, wäre die Spec rot,
 * ohne dass an der Übergabe etwas kaputt ist. Die Zusicherung, um die es geht,
 * ist „ein Text aus der einen Menge ist da, keiner aus der anderen", und die
 * gilt unabhängig davon, wie die Texte heißen.
 */

import { test, expect } from '@playwright/test';

const PLAYGROUND = 'http://localhost:8080/playground/';

/** Der Homograph aus dem Kopfkommentar. */
const FORM = 'arm';
const ID_KOERPERTEIL = '286';   // seltener, gewinnt NUR mit Zeiger
const ID_ADJEKTIV = '285';      // häufiger, gewinnt ohne Zeiger

/**
 * Die beiden Zeugenmengen aus dem geladenen Korpus-Index ableiten: Dateinamen
 * der Texte, die genau eines der beiden Lemmata führen.
 *
 * Gibt zusätzlich die Größe beider Mengen zurück, damit ein Test, dem die
 * Grundlage weggezogen wurde, das SAGT statt still durchzulaufen. Ein leerer
 * Zeugensatz würde jede `toContain`-Zusicherung sinnlos machen, und ein Test,
 * dessen Grundgesamtheit man nicht kennt, beweist nichts.
 */
function zeugen(page, idA, idB) {
  return page.evaluate(([a, b]) => {
    const fuehrt = (t, id) => Array.isArray(t.lemmata?.[`lemma_${id}`]);
    const texte = window.playground.corpusData.texts;
    return {
      nurA: texte.filter(t => fuehrt(t, a) && !fuehrt(t, b)).map(t => t.filename),
      nurB: texte.filter(t => fuehrt(t, b) && !fuehrt(t, a)).map(t => t.filename),
    };
  }, [idA, idB]);
}

/**
 * Der Router hängt seinen Hash-Dispatch hinter das Laden von Authority- UND
 * Korpus-Index (playground-main.js: initRouter() nach autoLoadCorpus()). Jeder
 * Test hier wartet damit auf den vollen Korpus, und dafür reicht das
 * 60-Sekunden-Budget aus der Config nicht, wenn sechs Worker denselben
 * single-threaded http-server bedienen. Begründung wie in playground.spec.js.
 */
test.beforeEach(() => {
  test.setTimeout(120000);
});

/** Wartet, bis Authority- und Korpus-Index geladen und die UI verdrahtet ist. */
async function playgroundBereit(page) {
  await page.waitForFunction(
    () => window.playground?.authorityData?.lemmata?.length > 0 &&
          window.playground?.corpusData?.texts?.length > 0 &&
          window.playground?.ui?.multiLemmaSearch !== undefined, null,
    { timeout: 90000 }
  );
}

/**
 * Route aufrufen und auf das fertige Ergebnis der Dokumentsuche warten.
 * Liefert die Titel der Ergebniskarten, also die Dateinamen der Treffertexte
 * (createMultiLemmaSummary setzt `title` auf `result.filename`).
 */
async function belegeFuer(page, hash) {
  await page.goto(`${PLAYGROUND}${hash}`);
  // Der Kopf trägt den Titel auch im Null-Treffer-Fall („… (0 Treffer)"),
  // ist also ein Signal für „Suche fertig", nicht für „Suche erfolgreich".
  await expect(page.locator('#resultsContainer'))
    .toContainText(`Multi-Lemma-Suche: ${FORM}`, { timeout: 90000 });
  return page.locator('#resultsContainer .result-summary-static h4').allTextContents();
}

/** Hash der Seite in { view, params } zerlegen, wie parseHash() im Router. */
function hashTeile(page) {
  return page.evaluate(() => {
    const roh = window.location.hash.slice(1);
    const teile = roh.split('&');
    const params = {};
    for (const stueck of teile.slice(1)) {
      const i = stueck.indexOf('=');
      if (i === -1) continue;
      params[stueck.slice(0, i)] = decodeURIComponent(stueck.slice(i + 1));
    }
    return { view: teile[0], params };
  });
}

/**
 * Prüft, auf welches der beiden Homographen-Lemmata wirklich aufgelöst wurde.
 *
 * `da` und `nicht` sind die beiden disjunkten Zeugenmengen aus `zeugen()`.
 * Beide werden zuerst auf Nichtleere geprüft: eine leere Menge macht die
 * folgende Zusicherung trivial wahr und würde einen kaputten Zustand als
 * grünen Test melden.
 */
function erwarteAufloesung(texte, da, nicht, hinweis) {
  expect(da.length, `${hinweis}: Zeugenmenge leer, Test beweist nichts`).toBeGreaterThan(0);
  expect(nicht.length, `${hinweis}: Gegenmenge leer, Test beweist nichts`).toBeGreaterThan(0);
  expect(
    texte.filter(t => da.includes(t)).length,
    `${hinweis}: kein Zeugentext des erwarteten Lemmas im Ergebnis`
  ).toBeGreaterThan(0);
  expect(
    texte.filter(t => nicht.includes(t)),
    `${hinweis}: Text aus der Gegenmenge im Ergebnis, es wurde das andere Lemma gesucht`
  ).toEqual([]);
}

test.describe('#58: ID-exakte Übergabe über die Route', () => {
  test('der Zeiger schlägt die Schreibform-Auflösung bei Homographen', async ({ page }) => {
    const texte = await belegeFuer(
      page,
      `#multi-lemma&lemmata=${FORM}&ids=${ID_KOERPERTEIL}&mode=document`
    );
    const { nurA, nurB } = await zeugen(page, ID_KOERPERTEIL, ID_ADJEKTIV);

    // Ein Text, der nur lemma_286 führt, kann im Ergebnis nur stehen, wenn
    // wirklich auf 286 aufgelöst wurde. Umgekehrt darf kein Text auftauchen,
    // der ausschliesslich lemma_285 führt.
    erwarteAufloesung(texte, nurA, nurB, 'mit Zeiger auf 286');
  });

  test('ohne ids bleibt es bei der frequenzsortierten Auflösung', async ({ page }) => {
    // Regressionsschutz: die alte Route darf sich durch den neuen Parameter
    // nicht verändert haben. Ohne Zeiger gewinnt das häufigere lemma_285,
    // und das ist genau das dokumentierte Verhalten aus #163/#164.
    const texte = await belegeFuer(page, `#multi-lemma&lemmata=${FORM}&mode=document`);
    const { nurA, nurB } = await zeugen(page, ID_KOERPERTEIL, ID_ADJEKTIV);

    erwarteAufloesung(texte, nurB, nurA, 'ohne Zeiger');
  });

  // Drei Sorten Müll, ein erwartetes Ergebnis: die Route darf davon weder
  // abstürzen noch auf ein anderes Lemma zeigen, sondern muss sich genau wie
  // der Aufruf ohne ids verhalten. `lemma_286` steht bewusst dabei: die ID ist
  // real, aber in der falschen Schreibweise, und der Router prüft mit /^\d+$/
  // nicht auf Existenz. Je ein eigener Test statt einer Schleife, damit ein
  // Fehlschlag am Testnamen ablesbar ist und die beiden anderen Fälle trotzdem
  // laufen.
  for (const kaputt of ['', 'abc', 'lemma_286']) {
    test(`ids=${JSON.stringify(kaputt)} fällt auf die normale Auflösung zurück`, async ({ page }) => {
      const texte = await belegeFuer(
        page,
        `#multi-lemma&lemmata=${FORM}&ids=${encodeURIComponent(kaputt)}&mode=document`
      );
      const { nurA, nurB } = await zeugen(page, ID_KOERPERTEIL, ID_ADJEKTIV);

      erwarteAufloesung(texte, nurB, nurA, `ids=${JSON.stringify(kaputt)}`);
    });
  }

  test('ein leerer Term verschiebt die ids nicht auf den nächsten Begriff', async ({ page }) => {
    // Die Paarung muss VOR dem Wegwerfen leerer Begriffe passieren, sonst
    // erbt „arm" hier die 999999 des leeren ersten Terms. Der Unterschied ist
    // sichtbar und nicht bloß intern: lemma_999999 gibt es nicht (höchste
    // vergebene ID im Lexikon ist 79828), die Dokumentsuche fände dann keinen
    // einzigen Text.
    const texte = await belegeFuer(
      page,
      `#multi-lemma&lemmata=,${FORM}&ids=999999,${ID_KOERPERTEIL}&mode=document`
    );
    const { nurA, nurB } = await zeugen(page, ID_KOERPERTEIL, ID_ADJEKTIV);

    expect(texte.length, 'Suche lief auf die verschobene Phantom-ID').toBeGreaterThan(0);
    erwarteAufloesung(texte, nurA, nurB, 'leerer erster Term');
  });

  test('bei zwei Begriffen bekommt jeder seinen eigenen Zeiger', async ({ page }) => {
    // Die Paarung ist positionsgleich, und zwar für jede Stelle. Der zweite
    // Begriff bekommt hier absichtlich KEINEN Zeiger (leerer zweiter Eintrag),
    // der erste einen: das prüft beide Zweige in einem Aufruf. Gesucht wird
    // dokumentweit, das ergibt die Texte, die beide Lemmata führen.
    const texte = await belegeFuer(
      page,
      `#multi-lemma&lemmata=${FORM},minne&ids=${ID_KOERPERTEIL},&mode=document`
    );
    const { nurA, nurB } = await zeugen(page, ID_KOERPERTEIL, ID_ADJEKTIV);

    // Die Und-Verknüpfung schränkt die Treffermenge ein, hebt die Trennung der
    // beiden Zeugenmengen aber nicht auf: ein Text, der nur lemma_285 führt,
    // darf auch hier nicht auftauchen.
    erwarteAufloesung(texte, nurA, nurB, 'zwei Begriffe, Zeiger nur am ersten');
  });
});

test.describe('#58: der Knopf in der Trefferliste des Lemmata-Explorers', () => {
  /** Die Ergebniskarte eines bestimmten Lemmas, erkannt an ihrem Titel-Link. */
  function karte(page, lemmaId) {
    return page.locator('.result-item')
      .filter({ has: page.locator(`a[href="../lemma/?id=${lemmaId}"]`) });
  }

  test.beforeEach(async ({ page }) => {
    await page.goto(`${PLAYGROUND}#lemmata&q=${FORM}`);
    await playgroundBereit(page);
    await expect(page.locator('#lemmaResults'))
      .toContainText(`Treffer für "${FORM}"`, { timeout: 30000 });
  });

  test('beide Homographen bekommen je einen eigenen Knopf', async ({ page }) => {
    // Ein Knopf pro Treffer, nicht einer pro Schreibform: sonst wäre die
    // Unterscheidung, für die der Parameter da ist, in der UI gar nicht
    // treffbar. Beide Karten sind sichtbar, `arm` steht alphabetisch auf
    // Platz 2 und 3 der 154 Treffer und damit weit innerhalb der 50, die
    // handleSearchResults rendert.
    for (const id of [ID_ADJEKTIV, ID_KOERPERTEIL]) {
      await expect(karte(page, id), `Karte zu lemma_${id}`).toHaveCount(1);
      await expect(
        karte(page, id).getByRole('button', { name: 'Belege suchen' })
      ).toHaveCount(1);
    }
  });

  test('der Knopf erzeugt den Hash mit genau der ID seiner Karte', async ({ page }) => {
    await karte(page, ID_KOERPERTEIL).getByRole('button', { name: 'Belege suchen' }).click();

    const { view, params } = await hashTeile(page);
    expect(view).toBe('multi-lemma');
    expect(params.lemmata).toBe(FORM);
    expect(params.ids).toBe(ID_KOERPERTEIL);
    // Dokumentweit, nicht Nähe: die Nähe- und die Vers-Suche brauchen zwei
    // verschiedene Lemmata und würden für einen einzelnen Beleg-Aufruf nur
    // den Hinweis „braucht zwei verschiedene" anzeigen.
    expect(params.mode).toBe('document');
  });

  test('die Nachbarkarte übergibt ihre eigene ID, nicht die des ersten Treffers', async ({ page }) => {
    // Gegenprobe zum vorigen Test: ohne sie würde ein fest verdrahteter
    // matches[0] genauso grün.
    await karte(page, ID_ADJEKTIV).getByRole('button', { name: 'Belege suchen' }).click();

    const { params } = await hashTeile(page);
    expect(params.ids).toBe(ID_ADJEKTIV);
  });

  test('der Klick führt bis in die Trefferliste der Belegsuche', async ({ page }) => {
    // Die ganze Kette in einem Test: Knopf, Hash, Route, Auflösung, Ergebnis.
    // Die Einzeltests oben sagen, WO es klemmt, dieser sagt, DASS es trägt.
    await karte(page, ID_KOERPERTEIL).getByRole('button', { name: 'Belege suchen' }).click();

    await expect(page.locator('#resultsContainer'))
      .toContainText(`Multi-Lemma-Suche: ${FORM}`, { timeout: 90000 });
    const texte = await page.locator('#resultsContainer .result-summary-static h4').allTextContents();
    const { nurA, nurB } = await zeugen(page, ID_KOERPERTEIL, ID_ADJEKTIV);

    erwarteAufloesung(texte, nurA, nurB, 'Klick auf die Karte von lemma_286');
  });
});

test.describe('#58: zweite Renderstelle (showAllLemmata)', () => {
  test('auch die Listenansicht ohne Suche trägt den Knopf', async ({ page }) => {
    // showAllLemmata() ist über die UI nicht erreichbar: showLemmata()
    // verzweigt bei mehr als 500 Lemmata immer in die Suchansicht, und das
    // Lexikon hat 43.879. Die Methode wird trotzdem gepflegt und muss den
    // Knopf mitführen, sonst driften die beiden Renderstellen auseinander.
    // Deshalb hier der direkte Aufruf; geprüft wird das Ergebnis, nicht der
    // Aufruf.
    await page.goto(PLAYGROUND);
    await playgroundBereit(page);
    await page.evaluate(() => window.playground.ui.authorityExplorers.showAllLemmata());

    const karten = page.locator('#resultsContainer .result-item');
    await expect(karten.first()).toBeVisible();

    // Datenunabhängig: die erste Karte nennt ihr Lemma im Titel-Link und
    // ihre ID im href. Der Knopf muss genau diese beiden übergeben, welches
    // Lemma auch immer gerade vorne steht.
    const erste = karten.first();
    const link = erste.locator('a[href^="../lemma/?id="]');
    const form = (await link.textContent()).trim();
    const id = (await link.getAttribute('href')).replace('../lemma/?id=', '');

    await erste.getByRole('button', { name: 'Belege suchen' }).click();

    const { view, params } = await hashTeile(page);
    expect(view).toBe('multi-lemma');
    expect(params.lemmata).toBe(form);
    expect(params.ids).toBe(id);
    expect(params.mode).toBe('document');
  });
});

/**
 * Nicht #58, sondern ein Fund aus dessen Review: derselbe Fehler, denselben
 * Mechanismus, ein Feld weiter. `reset()` stellt die Nähe-Distanz auf 10
 * zurück, und gelesen wurde sie bis dahin erst nach `close()`. Der Test steht
 * hier statt in `cooccurrence-ranking.spec.js`, weil er die Kopier-vor-close-
 * Zusicherung aus CONTRACTS §C.1.1 prüft, also dieselbe Sache wie der Rest
 * dieser Datei.
 *
 * Der bestehende Test in `cooccurrence-ranking.spec.js` konnte das nicht
 * sehen: er fährt mit `dist=10`, also genau dem Wert, auf den `reset()`
 * zurückstellt.
 */
test.describe('Review-Fund zu #58: die Nähe-Distanz überlebt close() ebenfalls', () => {
  /** Die im Ergebniskopf ausgewiesene Distanz. */
  async function ausgewieseneDistanz(page, dist) {
    await page.goto(
      `${PLAYGROUND}#multi-lemma&lemmata=minne,herze&mode=proximity&dist=${dist}`
    );
    await expect(page.locator('#resultsContainer'))
      .toContainText('Kookkurrenz-Analyse', { timeout: 90000 });
    const text = await page.locator('#resultsContainer').innerText();
    const treffer = text.match(/max\. (\d+) W/);
    return treffer ? treffer[1] : null;
  }

  test('der dist-Parameter der Route kommt bei der Suche an', async ({ page }) => {
    // Bewusst zwei Werte ungleich 10, einer darunter und einer darüber: mit
    // dist=10 wäre der Test auch bei zurückgesetzter Distanz grün.
    expect(await ausgewieseneDistanz(page, 3)).toBe('3');
    expect(await ausgewieseneDistanz(page, 25)).toBe('25');
  });
});
