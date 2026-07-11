/**
 * MHDBDB Playground - UI Helpers
 * Core UI functions: status, results display, state coordination
 */

import { lemmaRefMatchesId } from '../../../../assets/js/lib/lemma-match.js';

// ==================== TEXT LABEL DISAMBIGUATION (#121) ====================

/**
 * Mehrere Siglen können denselben Werktitel tragen (AC1/AC2/AC3 sind alle
 * "Der Ackermann aus Böhmen"). Für solche Titel-Dubletten liefert diese Map
 * ein Label-Suffix "(Hrsg. Nachname, Jahr)" bzw. "(Jahr)", abgeleitet aus
 * den biblStructs der Authority-Works (Editions-Zitat je Sigle, KZW #121).
 * Nicht-Dubletten bekommen kein Suffix.
 *
 * @param {Array} texts  Corpus-Index-Texte ({id, title, ...})
 * @param {Array} works  authorityData.works ({biblStructs: [{key, textContent}]})
 * @returns {Map<string,string>} sigle -> " (Hrsg. X, 1969)" (mit führendem Leerzeichen)
 */
export function buildTextLabelDisambiguator(texts, works) {
  const titleCounts = new Map();
  for (const t of texts || []) {
    if (t.title) titleCounts.set(t.title, (titleCounts.get(t.title) || 0) + 1);
  }

  const biblBySigle = new Map();
  for (const w of works || []) {
    for (const b of w.biblStructs || []) {
      if (b.key && b.textContent) biblBySigle.set(b.key, b.textContent);
    }
  }

  const suffixes = new Map();
  for (const t of texts || []) {
    if (!t.title || titleCounts.get(t.title) < 2) continue;
    const citation = biblBySigle.get(t.id);
    if (!citation) continue;

    const years = citation.match(/\b(1[5-9]\d{2}|20[0-2]\d)\b/g);
    const year = years ? years[years.length - 1] : null;

    // Editor aus dem formatierten Zitat ("Hrsg. von Günther Jungbluth.");
    // Klammer-Zusätze wie "(=Bibliothek ...)" beenden den Namen.
    const edMatch = citation.match(/[Hh]rsg\.?\s*(?:von|v\.)?\s*([A-ZÄÖÜ][^.,;()]{2,40})/);
    let surname = null;
    if (edMatch) {
      const nameParts = edMatch[1].trim().split(/\s+/);
      surname = nameParts[nameParts.length - 1];
    }

    if (surname && year) suffixes.set(t.id, ` (Hrsg. ${surname}, ${year})`);
    else if (year) suffixes.set(t.id, ` (${year})`);
  }
  return suffixes;
}

// ==================== STATUS MANAGEMENT ====================

export function updateStatus(indicator, text) {
  const statusIndicator = document.getElementById('statusIndicator');
  const statusText = document.getElementById('statusText');

  if (statusIndicator) {
    // Map emoji indicators to Heroicons
    const iconMap = {
      '🔄': '<svg class="w-6 h-6 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>',
      '✅': '<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
      '📥': '<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 12l3 3m0 0l3-3m-3 3V9"></path></svg>',
      '🗂️': '<svg class="w-6 h-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>'
    };

    const svgIcon = iconMap[indicator] || iconMap['🗂️']; // fallback to folder icon
    statusIndicator.innerHTML = svgIcon;
  }

  if (statusText) statusText.textContent = text;
}

// ==================== OVERVIEW UPDATES ====================

export function updateAuthorityOverview(authorityData) {
  const stats = document.getElementById('authorityStats');
  if (!stats) return;

  const ghBase = 'https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/blob/main/authority-files';
  const linkIcon = '<svg class="w-3 h-3 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>';

  const items = [
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path></svg>', label: 'Personen', value: authorityData.persons.length, ghFile: 'persons.xml', explorerBtn: 'showAuthorsBtn' },
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>', label: 'Werke', value: authorityData.works.length, ghFile: 'works.xml', explorerBtn: 'showWorksBtn' },
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m0 0V1h4a1 1 0 011 1v20a1 1 0 01-1 1H3a1 1 0 01-1-1V2a1 1 0 011-1h4v3z"></path></svg>', label: 'Lemmata', value: authorityData.lemmata.length, ghFile: 'lexicon.xml', explorerBtn: 'showLemmataBtn' },
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>', label: 'Begriffe', value: authorityData.concepts.length, ghFile: 'concepts.xml', explorerBtn: 'showConceptsBtn' },
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m0 0V1h4a1 1 0 011 1v20a1 1 0 01-1 1H3a1 1 0 01-1-1V2a1 1 0 011-1h4v3zm5 8a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>', label: 'Gattungen', value: authorityData.genres.length, ghFile: 'genres.xml', explorerBtn: 'showGenresBtn' },
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path></svg>', label: 'Namen', value: authorityData.names.length, ghFile: 'names.xml', explorerBtn: 'showNamesBtn' },
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12M8 12h12m-12 5h12M3 7h.01M3 12h.01M3 17h.01"></path></svg>', label: 'Varianten', value: Object.keys(authorityData.variants || {}).length, ghFile: 'variants.xml', explorerBtn: null }
  ];

  stats.innerHTML = `
    <dl class="space-y-1">
      ${items
        .map(
          ({ icon, label, value, ghFile, explorerBtn }) => {
            const explorerLink = explorerBtn
              ? `<button type="button" onclick="document.getElementById('${explorerBtn}').click()" class="text-brand-600 hover:text-brand-700 transition cursor-pointer" title="${label}-Explorer öffnen">${label}</button>`
              : `<span>${label}</span>`;
            const ghLink = ghFile
              ? `<a href="${ghBase}/${ghFile}" target="_blank" rel="noopener" class="text-slate-400 hover:text-brand-600 transition" title="XML auf GitHub">${linkIcon}</a>`
              : '';
            return `
            <div class="flex items-center justify-between rounded-lg bg-white/80 px-3 py-1 ring-1 ring-slate-200/70">
              <dt class="flex items-center gap-2 text-xs text-slate-600">
                <span class="w-3.5 h-3.5 [&>svg]:w-3.5 [&>svg]:h-3.5">${icon}</span>
                ${explorerLink}
                ${ghLink}
              </dt>
              <dd class="text-xs font-semibold text-brand-700">${value}</dd>
            </div>
          `;
          }
        )
        .join('')}
    </dl>
  `;
}

export function updateTEIOverview(teiData) {
  const overview = document.getElementById('teiOverview');
  const stats = document.getElementById('teiStats');

  if (teiData.files.length > 0 && overview && stats) {
    overview.style.display = 'block';

    const items = [
      { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>', label: 'TEI-Dateien', value: teiData.files.length },
      { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>', label: 'Wörter', value: teiData.words.length },
      { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>', label: 'Textzeilen', value: teiData.lines.length },
      { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path></svg>', label: 'Annotationen', value: teiData.annotations.length }
    ];

    stats.innerHTML = `
      <dl class="space-y-2">
        ${items
          .map(
            ({ icon, label, value }) => `
              <div class="flex items-center justify-between rounded-xl bg-white/80 px-4 py-2 shadow-sm ring-1 ring-brand-100/80">
                <dt class="flex items-center gap-3 text-sm font-medium text-slate-600">
                  <span class="text-lg">${icon}</span>
                  <span>${label}</span>
                </dt>
                <dd class="text-base font-bold text-brand-700">${value}</dd>
              </div>
            `
          )
          .join('')}
      </dl>
    `;
  }
}

// ==================== BUTTON STATE MANAGEMENT ====================

export function enableAuthorityQueries() {
  const buttonIds = [
    'showAuthorsBtn',
    'showWorksBtn',
    'showLemmataBtn',
    'showConceptsBtn',
    'showGenresBtn',
    'showNamesBtn',
    'xpathExecute'
  ];

  buttonIds.forEach((id) => {
    const button = document.getElementById(id);
    if (button) {
      button.disabled = false;
    }
  });
}

export function enableTEIQueries() {
  const teiQueriesSection = document.getElementById('teiQueries');
  if (teiQueriesSection) {
    teiQueriesSection.style.display = 'block';
  }
}

// ==================== RESULTS DISPLAY ====================

export function displayResults(title, results) {
  const container = document.getElementById('resultsContainer');
  if (!container) return;

  if (!results || results.length === 0) {
    container.innerHTML = `
      <div class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center text-sm text-slate-500">
        <p class="font-medium text-slate-600">${title}</p>
        <p class="mt-2 text-slate-500">Keine Ergebnisse gefunden.</p>
      </div>
    `;
    return;
  }

  const resultsHTML = results
    .map(
      (result) => `
        <article class="result-item rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm transition hover:border-brand-200">
          <header class="result-meta text-xs font-semibold uppercase tracking-wide text-brand-600">${result.meta}</header>
          <p class="result-snippet mt-2 text-sm leading-relaxed text-slate-700">${result.snippet}</p>
        </article>
      `
    )
    .join('');

  container.innerHTML = `
    <div class="mb-4 flex items-center justify-between rounded-xl bg-slate-50/80 px-4 py-2 text-sm font-medium text-slate-600">
      <span>${title}</span>
      <span class="text-sm uppercase tracking-wide text-slate-600">${results.length} Treffer</span>
    </div>
    <div class="space-y-3">
      ${resultsHTML}
    </div>
  `;
}

// ==================== SUMMARY RESULTS DISPLAY ====================

// Store raw results for lazy TEI loading
let storedRawResults = null;
let storedLemmaIds = null;

export function displaySummaryResults(title, summaryData, rawResults = null, lemmaIds = null) {
  const container = document.getElementById('resultsContainer');
  if (!container) return;

  // Store raw results for later enrichment
  storedRawResults = rawResults;
  storedLemmaIds = lemmaIds;

  if (!summaryData || summaryData.length === 0) {
    container.innerHTML = `
      <div class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center text-sm text-slate-500">
        <p class="font-medium text-slate-600">${title}</p>
        <p class="mt-2 text-slate-500">Keine Ergebnisse gefunden.</p>
      </div>
    `;
    return;
  }

  const totalResults = summaryData.reduce((sum, s) => sum + (s.count || 0), 0);
  const summariesHTML = summaryData.map((summary, index) => createSummaryCard(summary, index)).join('');

  container.innerHTML = `
    <div class="mb-4 flex items-center justify-between rounded-xl bg-slate-50/80 px-4 py-2 text-sm font-medium text-slate-600">
      <span>${title}</span>
      <span class="text-sm uppercase tracking-wide text-slate-600">${totalResults} Treffer · ${summaryData.length} Kontexte</span>
    </div>
    <div class="space-y-3">
      ${summariesHTML}
    </div>
  `;

  setupSummaryExpansion();
}

function createSummaryCard(summary, index) {
  const previewText = summary.preview || 'Klicken für Details…';
  const hasDetails = summary.details && Array.isArray(summary.details) && summary.details.length > 0;
  const detailsHTML = hasDetails ? createDetailsHTML(summary.details) : '';

  // For document search (no details), don't show expand icon or hint
  if (!hasDetails) {
    return `
      <article class="result-summary-static group overflow-hidden rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm" data-summary-id="${index}">
        <div class="summary-header flex items-start justify-between gap-4">
          <div class="flex-1">
            <h4 class="text-sm font-semibold text-slate-900">${summary.title}</h4>
            <p class="summary-preview mt-2 text-sm text-slate-600">${previewText}</p>
          </div>
          <div class="flex items-center gap-2">
            <span class="summary-count">${summary.count}</span>
          </div>
        </div>
      </article>
    `;
  }

  // For paragraph/proximity search (with details), show expandable UI
  return `
    <article class="result-summary group overflow-hidden rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm transition hover:border-brand-200" data-summary-id="${index}">
      <div class="summary-header flex items-start justify-between gap-4">
        <div class="flex-1">
          <h4 class="text-sm font-semibold text-slate-900">${summary.title}</h4>
          <p class="summary-preview mt-2 text-sm text-slate-600">${previewText}</p>
        </div>
        <div class="flex items-center gap-2">
          <span class="summary-count">${summary.count}</span>
          <span class="expand-icon text-lg">⌄</span>
        </div>
      </div>
      <p class="summary-expand-hint mt-3 text-sm font-medium uppercase tracking-wide text-slate-500">Klicken zum Erweitern</p>
      <div class="result-details">
        ${detailsHTML}
      </div>
    </article>
  `;
}

function createDetailsHTML(details) {
  if (Array.isArray(details)) {
    return details
      .map(
        (detail, idx) => `
          <div class="detail-item" data-detail-index="${idx}" style="cursor: pointer; transition: background-color 0.2s;" title="Klicken zum Öffnen im Lese-Modus" onmouseenter="this.style.backgroundColor='#f1f5f9'" onmouseleave="this.style.backgroundColor='transparent'">
            <div class="detail-meta">${detail.meta || ''}</div>
            <div class="detail-snippet">${detail.snippet || detail.text || ''}</div>
          </div>
        `
      )
      .join('');
  }
  return `<div class="detail-snippet">${details}</div>`;
}

function setupSummaryExpansion() {
  const summaries = Array.from(document.querySelectorAll('.result-summary'));
  summaries.forEach((summary) => {
    const clone = summary.cloneNode(true);
    summary.replaceWith(clone);
  });

  document.querySelectorAll('.result-summary').forEach((summary) => {
    summary.addEventListener('click', async (event) => {
      event.preventDefault();

      const isExpanding = !summary.classList.contains('expanded');

      if (isExpanding && storedRawResults && !summary.dataset.enriched) {
        // First time expanding - fetch TEI text
        const filename = summary.querySelector('h4').textContent;
        const fileResults = storedRawResults.filter(r => r.filename === filename);

        if (fileResults.length > 0 && !fileResults[0].text) {
          // Show loading indicator
          summary.querySelector('.summary-expand-hint').textContent = 'Lade Text...';

          try {
            // Fetch TEI and enrich results
            await enrichFileResults(fileResults, storedLemmaIds);

            // Rebuild the details HTML with enriched data
            const details = createDetailsFromEnrichedResults(fileResults);
            const detailsHTML = createDetailsHTML(details);
            const detailsContainer = summary.querySelector('.result-details');
            if (detailsContainer) {
              detailsContainer.innerHTML = detailsHTML;

              // Add click handlers to detail items to open main site reader
              setupDetailItemClickHandlers(detailsContainer, fileResults);
            }

            // Mark as enriched
            summary.dataset.enriched = 'true';
            summary.querySelector('.summary-expand-hint').textContent = 'Klicken zum Zuklappen';
          } catch (error) {
            console.error('Failed to enrich results:', error);
            summary.querySelector('.summary-expand-hint').textContent = 'Fehler beim Laden';
          }
        }
      }

      summary.classList.toggle('expanded');
    });
  });
}

// Enrich file results with TEI text
// (exportiert für position-parity.spec.js — der Guard gegen leere <w> ist
// der vierte Zählpfad der §B-Parität, #170)
export async function enrichFileResults(fileResults, lemmaIds) {
  // Guard against null/undefined lemmaIds
  if (!lemmaIds || !Array.isArray(lemmaIds)) {
    console.warn(`No lemmaIds provided for enrichment`);
    return;
  }

  // v4.0.0: Only proximity search (paragraph mode removed)
  const isProximitySearch = fileResults[0].contextStart !== undefined;

  for (const result of fileResults) {
    if (result.text || result.contextText) continue; // Already enriched

    try {
      const teiPath = `../tei/${result.filename}`;
      const response = await fetch(teiPath);
      if (!response.ok) continue;

      const xmlText = await response.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(xmlText, 'text/xml');

      // v4.0.0: Only proximity search remains (paragraph search removed)
      if (isProximitySearch) {
        // Proximity search: extract context text from word range with highlighting
        // v4.0.0: Match Python's simplified document-level logic
        // Python now uses: word_els = tree.xpath('//tei:body//tei:w[@lemmaRef]')
        const nsResolver = () => 'http://www.tei-c.org/ns/1.0';

        // Get words WITH lemmaRef (for position matching - matches Python index)
        const xpathIndexed = doc.evaluate(
          '//tei:body//tei:w[@lemmaRef]',
          doc,
          nsResolver,
          XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
          null
        );

        const indexedWords = [];
        for (let i = 0; i < xpathIndexed.snapshotLength; i++) {
          const w = xpathIndexed.snapshotItem(i);
          // Paritäts-Guard (#170, analog #131): der Python-Build überspringt
          // leere <w lemmaRef/> (build-corpus-index.py, text_content-Check) —
          // ohne denselben Guard verschöbe ein einziges leeres <w> alle
          // Kontextfenster hinter ihm (CONTRACTS §B). Der lemmaRef-Check
          // prüft den Attribut-WERT, nicht nur die Existenz: der XPath
          // [@lemmaRef] matcht auch lemmaRef="" — Python (falsy-Check) und
          // Reader (falsy-Check) überspringen das, dieser Pfad muss es
          // genauso tun (#184 Review-Finding, 2. Runde).
          if (!w.getAttribute('lemmaRef') || !w.textContent.trim()) continue;
          indexedWords.push(w);
        }

        // Get the matched word elements from index
        const matchedWords = indexedWords.slice(result.contextStart, result.contextEnd);

        // Expand to include ALL <w> elements (with or without lemmaRef) for complete text
        let contextWords = [];

        if (matchedWords.length > 0) {
          const firstWord = matchedWords[0];
          const lastWord = matchedWords[matchedWords.length - 1];

          // Get all <w> elements in document order
          const xpathAll = doc.evaluate(
            '//tei:body//tei:w',
            doc,
            nsResolver,
            XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
            null
          );

          const allWords = [];
          let startIdx = -1;
          let endIdx = -1;

          for (let i = 0; i < xpathAll.snapshotLength; i++) {
            const word = xpathAll.snapshotItem(i);
            allWords.push(word);

            // Find boundaries based on matched words
            if (word.isSameNode(firstWord)) startIdx = i;
            if (word.isSameNode(lastWord)) endIdx = i + 1;
          }

          // Extract complete context (including words without lemmaRef)
          contextWords = startIdx >= 0 && endIdx > startIdx
            ? allWords.slice(startIdx, endIdx)
            : matchedWords;
        }

        // Build highlighted context text
        const highlightedParts = contextWords.map(word => {
          const text = word.textContent?.trim() || '';
          const lemmaRef = word.getAttribute('lemmaRef') || '';
          // Exact lemma-id match (CONTRACTS §B.1) — never a substring. See #126.

          // Highlight matched lemmas
          for (let i = 0; i < lemmaIds.length; i++) {
            const lemmaId = lemmaIds[i];
            const cleanId = lemmaId.toString().replace('lemma_', '');
            if (lemmaRefMatchesId(lemmaRef, `lemma_${cleanId}`)) {
              const color = LEMMA_COLORS[i % LEMMA_COLORS.length];
              return `<span style="background-color: ${color.bg}; color: ${color.text}; border-bottom: 2px solid ${color.border}; padding: 2px 4px; border-radius: 3px; font-weight: 500;">${text}</span>`;
            }
          }
          return text;
        });

        result.contextText = highlightedParts.join(' ');
      } else {
        // v4.0.0: Paragraph search removed - this should not be reached
        console.warn('⚠️ Unexpected: non-proximity enrichment called in v4.0.0');
      }
    } catch (error) {
      console.warn(`Failed to enrich ${result.filename}:`, error);
    }
  }
}

// Create details from enriched results
// v4.0.0: Only proximity search remains (paragraph search removed)
function createDetailsFromEnrichedResults(results) {
  return results.map((result) => {
    // v4.0.0: Proximity results with contextText.
    // Vers-Suche-Ergebnisse (#106 Punkt 8) tragen verseN — deren Label bleibt
    // auch nach dem Enrichment "Gemeinsam in Vers N" statt Wortabstand.
    if (result.contextText !== undefined) {
      return {
        meta: result.verseN !== undefined
          ? `Gemeinsam in Vers ${result.verseN}`
          : `Abstand: ${result.distance} Wörter`,
        snippet: `"${result.contextText}"`
      };
    }

    // Fallback for unexpected result types
    return {
      meta: 'Unbekannter Ergebnistyp',
      snippet: 'Keine Daten verfügbar'
    };
  });
}

// Color palette for multi-lemma highlighting
const LEMMA_COLORS = [
  { bg: '#fecaca', text: '#991b1b', border: '#ef4444' },  // Red
  { bg: '#bfdbfe', text: '#1e3a8a', border: '#3b82f6' },  // Blue
  { bg: '#bbf7d0', text: '#14532d', border: '#22c55e' },  // Green
  { bg: '#fde68a', text: '#78350f', border: '#fbbf24' },  // Yellow
  { bg: '#e9d5ff', text: '#581c87', border: '#a855f7' },  // Purple
  { bg: '#fed7aa', text: '#7c2d12', border: '#fb923c' },  // Orange
];

// ==================== WELCOME & ERROR STATES ====================

export function showWelcomeMessage() {
  const container = document.getElementById('resultsContainer');
  if (!container) return;

  container.innerHTML = `
    <div class="rounded-2xl border border-brand-100 bg-brand-50/70 p-8 text-center">
      <h3 class="text-lg font-semibold text-brand-700">MHDBDB Playground bereit!</h3>
      <p class="mt-3 text-sm text-brand-800/90">
        Authority Files sind geladen. Laden Sie nun TEI-Textdateien oder nutzen Sie die Abfragen, um sofort mit der Forschung zu beginnen.
      </p>
    </div>
  `;
}

// ==================== UI STATE COORDINATION ====================

export function updateAllUI(authorityData, teiData) {
  const totalAuthorityFiles = 7; // persons, works, lexicon, concepts, genres, names, variants
  const loadedLabel = `${authorityData.files.length}/${totalAuthorityFiles} Authority Files geladen`;
  const indicator = authorityData.files.length === totalAuthorityFiles ? '✅' : '📥';
  updateStatus(indicator, loadedLabel);

  updateAuthorityOverview(authorityData);
  updateTEIOverview(teiData);

  enableAuthorityQueries();

  if (teiData.files.length > 0) {
    enableTEIQueries();
  }

  if (authorityData.files.length > 0 && teiData.files.length === 0) {
    showWelcomeMessage();
  }
}

// ==================== DETAIL ITEM CLICK HANDLERS ====================

/**
 * Setup click handlers for detail items to open in main site reader
 * Opens korpus.html with multi-lemma highlighting and position jump
 */
function setupDetailItemClickHandlers(detailsContainer, fileResults) {
  const detailItems = detailsContainer.querySelectorAll('.detail-item[data-detail-index]');

  detailItems.forEach((item) => {
    item.addEventListener('click', (e) => {
      e.stopPropagation(); // Don't trigger summary expansion/collapse

      const detailIndex = parseInt(item.dataset.detailIndex);
      const result = fileResults[detailIndex];

      if (!result) {
        console.warn('[DetailClick] No result found for index:', detailIndex);
        return;
      }

      // Extract text ID from filename (e.g., "ABG.tei.xml" → "ABG")
      const textId = result.filename.replace('.tei.xml', '');

      // Get lemma IDs from stored lemmaIds (without "lemma_" prefix)
      const lemmaIds = storedLemmaIds || [];

      // Build URL to open korpus.html with parameters
      const params = new URLSearchParams();
      params.set('textId', textId);
      params.set('lemmaIds', lemmaIds.join(','));

      // Use contextStart as target position if available (proximity results)
      if (result.contextStart !== undefined) {
        const targetPosition = Math.min(...result.matchPositions || [result.contextStart]);
        params.set('position', targetPosition);
      }

      const url = `../korpus.html?${params.toString()}`;

      // Open in new tab
      window.open(url, '_blank');
    });
  });
}
