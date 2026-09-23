/**
 * CSV-Export im Hausformat (#114, #448): Komma als Trenner, Quoting nach
 * RFC 4180 nur bei Bedarf, CRLF, UTF-8 mit BOM, damit Excel Umlaute und
 * Zeilen richtig liest.
 *
 * Geteilt von der Ergebnistabelle der Korpussuche (app.js) und den
 * tabellarischen Playground-Werkzeugen. Der Hapax-Export
 * (hapax-legomena.js) trennt mit Semikolon und bleibt so, weil ein
 * Formatwechsel bestehende Auswertungen bricht (Entscheidung Nachtlauf
 * 23.09., #448).
 */

/** Eine Zelle: in "..." einfassen, wenn sie Komma, Quote oder Umbruch enthält. */
export function csvCell(value) {
    const str = String(value ?? '');
    if (/[",\n\r]/.test(str)) {
        return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
}

/** Kopfzeile plus Zeilen (Arrays von Zellwerten) zu einem CSV-Text mit CRLF. */
export function toCsv(header, rows) {
    return [header, ...rows]
        .map(cells => cells.map(csvCell).join(','))
        .join('\r\n');
}

/** Baustein für Dateinamen: nur Buchstaben, Ziffern, Umlaute und Bindestrich. */
export function csvFilenamePart(text, fallback = 'export') {
    const s = String(text ?? '').trim();
    return (s || fallback).replace(/[^a-zA-Z0-9äöüÄÖÜß-]/g, '_').slice(0, 40);
}

/** Startet den Browser-Download eines CSV-Texts (mit BOM). */
export function downloadCsv(filename, csv) {
    const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/** Heutiges Datum als JJJJ-MM-TT für Dateinamen. */
export function csvDateStamp() {
    return new Date().toISOString().slice(0, 10);
}
