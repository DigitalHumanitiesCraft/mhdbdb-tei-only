/**
 * Mehrdeutige Schreibformen: Stufe 2 gibt alle Kandidaten aus, geordnet nach
 * Vorschrift B (#378, ADR-021, KZW 2026-09-14).
 *
 * Das Orakel fuer die benannten Faelle sind die Belege aus dem Ticket und aus
 * ADR-021: `hab` gehoert zum Verb haben (lemma_2598), nicht zum Nomen habe
 * (lemma_2593), und `pyn` ist pîn (lemma_4664), nicht sîn (lemma_5432); beides
 * hat die frueheren Regeln (first-wins, Gesamthaeufigkeit) je auf einer Seite
 * falsch gemacht. Die Invariante ueber alle Formen liest den Index von der
 * Platte.
 *
 * Relative Pfade gegen baseURL, kein fester Port (#465).
 */

import { test, expect } from '@playwright/test';
import { readFileSync } from 'fs';
import { gunzipSync } from 'zlib';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const wurzel = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const auth = JSON.parse(gunzipSync(readFileSync(resolve(wurzel, 'data', 'authority-index.json.gz'))).toString('utf-8'));
const lemmaIds = new Set(auth.lemmata.map(l => l.id));
const HAB = auth.variantCandidates?.hab;

test.describe('variantCandidates im Index (#378)', () => {
    test('der Index traegt Kandidatenlisten', () => {
        expect(Object.keys(auth.variantCandidates).length).toBeGreaterThan(1000);
    });

    test('jede Liste hat mindestens zwei verschiedene, bekannte Lemmata, und variants zeigt auf den ersten', () => {
        const kaputt = [];
        for (const [form, ids] of Object.entries(auth.variantCandidates)) {
            const ok = Array.isArray(ids) && ids.length >= 2 && new Set(ids).size === ids.length
                && ids.every(id => lemmaIds.has(id)) && auth.variants[form] === ids[0];
            if (!ok) kaputt.push(form);
        }
        expect(kaputt.slice(0, 10)).toEqual([]);
    });

    test('ein Kandidat ohne Lexikoneintrag rutscht nicht vor das echte Lemma (halap, chana)', () => {
        // Ohne den Filter im Build zeigten beide auf lemma_79230 und lemma_79728,
        // haengende Verweise (#115) mit vielen Tokens und ohne Eintrag in lexicon.xml.
        for (const form of ['halap', 'chana']) {
            expect(lemmaIds.has(auth.variants[form]), `${form} zeigt auf ein unbekanntes Lemma`).toBeTruthy();
        }
    });

    test('keine Form mit nur einem Kandidaten steht in variantCandidates', () => {
        expect(auth.variantCandidates).not.toHaveProperty('brot');
    });

    test('benannte Faelle: hab zuerst beim Verb, pyn zuerst bei pîn', () => {
        expect(HAB, 'hab fehlt in variantCandidates').toBeTruthy();
        expect(HAB[0]).toBe('lemma_2598');
        expect(HAB).toContain('lemma_2593');
        expect(auth.variantCandidates.pyn[0]).toBe('lemma_4664');
    });

    test('noCorpus steht nur als true und nur an Lemmata, die das Korpus nicht kennt', () => {
        const mit = auth.lemmata.filter(l => 'noCorpus' in l);
        expect(mit.length).toBeGreaterThan(0);
        expect(mit.every(l => l.noCorpus === true)).toBeTruthy();
        expect(auth.lemmata.find(l => l.id === 'lemma_66692')?.noCorpus).toBe(true);
        expect(auth.lemmata.find(l => l.id === 'lemma_4086')).not.toHaveProperty('noCorpus');
    });
});

test.describe('Hauptseite: alle Kandidaten und der Hinweis (#378)', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    });

    test('resolveLemmaIds gibt alle Kandidaten in der Reihenfolge des Index aus', async ({ page }) => {
        const ids = await page.evaluate(() => window._mhdbdbApp.searchEngine.resolveLemmaIds('hab'));
        expect(ids).toEqual(HAB);
    });

    test('Hinweis und Lemmata in der Reihenfolge der Aufloesung bei einer mehrdeutigen Form', async ({ page }) => {
        await page.fill('#searchInput', 'hab');
        await page.click('#searchButton');
        const badges = page.locator('#lemmaList a');
        await expect(badges.first()).toBeVisible({ timeout: 15000 });
        await expect(badges.first()).toHaveAttribute('href', 'lemma/?id=2598');
        await expect(page.locator('#lemmaAmbiguityNote')).toBeVisible();
        await expect(page.locator('#lemmaAmbiguityNote'))
            .toContainText('Diese Schreibform kann zu mehreren Lemmata gehören');
    });

    test('kein Hinweis bei einem Stufe-1-Treffer und bei einer Lemma-Nummer', async ({ page }) => {
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await expect(page.locator('#lemmaInfo')).toBeVisible({ timeout: 15000 });
        await expect(page.locator('#lemmaAmbiguityNote')).toBeHidden();

        await page.fill('#searchInput', '4086');
        await page.click('#searchButton');
        await expect(page.locator('#lemmaList a')).toHaveCount(1, { timeout: 15000 });
        await expect(page.locator('#lemmaAmbiguityNote')).toBeHidden();
    });
});

test.describe('Playground: searchLemmaByOrthography gibt die Kandidaten aus (#378)', () => {
    test('hab liefert beide Lemmata, das Verb zuerst', async ({ page }) => {
        await page.goto('/playground/');
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });
        const ids = await page.evaluate(() =>
            window.playground.authorityManager.searchLemmaByOrthography('hab').map(l => l.id));
        expect(ids).toEqual(HAB);
    });
});
