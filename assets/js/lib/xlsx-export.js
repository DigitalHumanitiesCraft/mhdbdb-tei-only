/**
 * XLSX-Export ohne Fremdbibliothek (#448)
 *
 * KZW am 2026-09-24 in #448: "Für die Nutzung in Excel wünsche ich
 * zusätzlich einen XLSX-Export, damit Sonderzeichen und Spalten ohne manuelle
 * Import-Einstellungen funktionieren." Eine CDN-Bibliothek ist hier verboten
 * (no-cdn-check.yml), und SheetJS vendoren hiesse rund ein Megabyte fuer eine
 * Tabelle. Deshalb das Minimum von Office Open XML, von Hand:
 *
 *   - ZIP ohne Kompression ("stored"), CRC-32 selbst gerechnet
 *   - je Blatt ein worksheet mit Inline-Strings (kein sharedStrings.xml)
 *   - styles.xml mit genau zwei Formaten: normal und fett (Kopfzeile)
 *
 * Zahlen (typeof number) werden als Zahl geschrieben, alles andere als Text.
 * Zeichen, die in XML 1.0 nicht vorkommen duerfen (Steuerzeichen ausser Tab
 * und Zeilenumbruch), fallen weg; sonst verweigert Excel die ganze Datei.
 */

const CRC_TABLE = (() => {
    const t = new Uint32Array(256);
    for (let n = 0; n < 256; n++) {
        let c = n;
        for (let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
        t[n] = c >>> 0;
    }
    return t;
})();

function crc32(bytes) {
    let c = 0xFFFFFFFF;
    for (let i = 0; i < bytes.length; i++) c = CRC_TABLE[(c ^ bytes[i]) & 0xFF] ^ (c >>> 8);
    return (c ^ 0xFFFFFFFF) >>> 0;
}

/** ZIP-Container, alle Eintraege "stored". files: [{name, data: Uint8Array}] */
function zipStored(files) {
    const enc = new TextEncoder();
    const parts = [];
    const central = [];
    let offset = 0;
    for (const f of files) {
        const name = enc.encode(f.name);
        const crc = crc32(f.data);
        const size = f.data.length;
        const local = new DataView(new ArrayBuffer(30));
        local.setUint32(0, 0x04034b50, true);
        local.setUint16(4, 20, true);       // version needed
        local.setUint16(6, 0x0800, true);   // UTF-8 names
        local.setUint16(8, 0, true);        // stored
        local.setUint32(14, crc, true);
        local.setUint32(18, size, true);
        local.setUint32(22, size, true);
        local.setUint16(26, name.length, true);
        parts.push(new Uint8Array(local.buffer), name, f.data);

        const cen = new DataView(new ArrayBuffer(46));
        cen.setUint32(0, 0x02014b50, true);
        cen.setUint16(4, 20, true);
        cen.setUint16(6, 20, true);
        cen.setUint16(8, 0x0800, true);
        cen.setUint16(10, 0, true);
        cen.setUint32(16, crc, true);
        cen.setUint32(20, size, true);
        cen.setUint32(24, size, true);
        cen.setUint16(28, name.length, true);
        cen.setUint32(42, offset, true);
        central.push(new Uint8Array(cen.buffer), name);

        offset += 30 + name.length + size;
    }
    const centralSize = central.reduce((s, p) => s + p.length, 0);
    const end = new DataView(new ArrayBuffer(22));
    end.setUint32(0, 0x06054b50, true);
    end.setUint16(8, files.length, true);
    end.setUint16(10, files.length, true);
    end.setUint32(12, centralSize, true);
    end.setUint32(16, offset, true);

    const all = [...parts, ...central, new Uint8Array(end.buffer)];
    const out = new Uint8Array(all.reduce((s, p) => s + p.length, 0));
    let pos = 0;
    for (const p of all) { out.set(p, pos); pos += p.length; }
    return out;
}

function xmlText(value) {
    return String(value ?? '')
        // eslint-disable-next-line no-control-regex
        .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F￾￿]/g, '')
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/** 0 -> A, 25 -> Z, 26 -> AA */
function columnName(i) {
    let s = '';
    for (let n = i + 1; n > 0; n = Math.floor((n - 1) / 26)) s = String.fromCharCode(65 + (n - 1) % 26) + s;
    return s;
}

function cellXml(value, ref, bold) {
    const style = bold ? ' s="1"' : '';
    if (typeof value === 'number' && Number.isFinite(value)) {
        return `<c r="${ref}"${style}><v>${value}</v></c>`;
    }
    return `<c r="${ref}"${style} t="inlineStr"><is><t xml:space="preserve">${xmlText(value)}</t></is></c>`;
}

function sheetXml(header, rows) {
    const lines = [header, ...rows].map((cells, r) =>
        `<row r="${r + 1}">${cells.map((v, c) => cellXml(v, columnName(c) + (r + 1), r === 0)).join('')}</row>`);
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        + '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        + '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        + `<sheetData>${lines.join('')}</sheetData></worksheet>`;
}

/** Excel erlaubt 31 Zeichen und keines von []:*?/\ im Blattnamen. */
function sheetName(name, i) {
    const s = String(name ?? '').replace(/[[\]:*?/\\]/g, ' ').trim().slice(0, 31);
    return s || `Blatt ${i + 1}`;
}

/**
 * @param {Array<{name: string, header: Array, rows: Array<Array>}>} sheets
 * @returns {Uint8Array} Inhalt einer .xlsx-Datei
 */
export function toXlsx(sheets) {
    if (!Array.isArray(sheets) || sheets.length === 0) throw new Error('toXlsx: mindestens ein Blatt');
    const enc = new TextEncoder();
    const names = sheets.map((s, i) => sheetName(s.name, i));
    if (new Set(names).size !== names.length) throw new Error('toXlsx: Blattnamen muessen eindeutig sein');

    const head = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n';
    const files = [
        ['[Content_Types].xml', head
            + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            + '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            + '<Default Extension="xml" ContentType="application/xml"/>'
            + '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            + '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
            + names.map((_, i) => `<Override PartName="/xl/worksheets/sheet${i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`).join('')
            + '</Types>'],
        ['_rels/.rels', head
            + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            + '</Relationships>'],
        ['xl/workbook.xml', head
            + '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            + '<sheets>' + names.map((n, i) => `<sheet name="${xmlText(n)}" sheetId="${i + 1}" r:id="rId${i + 1}"/>`).join('') + '</sheets>'
            + '</workbook>'],
        ['xl/_rels/workbook.xml.rels', head
            + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + names.map((_, i) => `<Relationship Id="rId${i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${i + 1}.xml"/>`).join('')
            + `<Relationship Id="rId${names.length + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>`
            + '</Relationships>'],
        ['xl/styles.xml', head
            + '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            + '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
            + '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
            + '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
            + '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
            + '<cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs>'
            + '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
            + '</styleSheet>'],
        ...sheets.map((s, i) => [`xl/worksheets/sheet${i + 1}.xml`, sheetXml(s.header, s.rows)])
    ];
    return zipStored(files.map(([name, xml]) => ({ name, data: enc.encode(xml) })));
}

/** Startet den Browser-Download einer .xlsx-Datei. */
export function downloadXlsx(filename, bytes) {
    const blob = new Blob([bytes], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
