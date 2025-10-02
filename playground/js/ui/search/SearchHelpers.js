/**
 * MHDBDB Playground - Search Helpers
 * Tailwind-first search interfaces and utilities with MHG normalization support
 */

import { TextNormalizer } from '/lib/text-normalizer.js';

// ==================== SEARCH INTERFACE CREATION ====================

export function createSearchInterface(config) {
  const {
    title,
    placeholder,
    searchInputId,
    resultsId,
    totalCount,
    helpText = 'Geben Sie einen Suchbegriff ein, um zu starten.',
  } = config;

  return `
    <section class="space-y-4">
      <header class="rounded-xl bg-slate-50/80 px-4 py-2 text-sm font-medium text-slate-600">
        <span>${title}</span>
        <span class="ml-2 text-xs uppercase tracking-wide text-slate-400">${totalCount} Einträge</span>
      </header>
      <div>
        <input
          type="text"
          id="${searchInputId}"
          placeholder="${placeholder}"
          class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-700 shadow-sm transition focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200"
        />
      </div>
      <div
        id="${resultsId}"
        class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center text-sm text-slate-500"
      >
        ${helpText}
      </div>
    </section>
  `;
}

// ==================== SEARCH RESULT HANDLING ====================

export function handleSearchResults(searchTerm, matches, config) {
  const {
    searchTermForDisplay = searchTerm,
    maxResults = 50,
    emptyMessage = 'Keine Ergebnisse gefunden für "{term}"',
  } = config;

  if (matches.length === 0) {
    return `
      <div class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center text-sm text-slate-500">
        ${emptyMessage.replace('{term}', searchTermForDisplay)}
      </div>
    `;
  }

  const displayMatches = matches.slice(0, maxResults);
  const countInfo = matches.length > maxResults ? ` (erste ${maxResults} angezeigt)` : '';

  return {
    matches: displayMatches,
    headerHTML: `
      <div class="rounded-xl bg-slate-50/80 px-4 py-2 text-sm font-medium text-slate-600">
        ${matches.length} Treffer für "${searchTermForDisplay}"${countInfo}
      </div>
    `,
  };
}

// ==================== INPUT EVENT SETUP ====================

export function setupSearchInput(inputId, searchHandler) {
  const searchInput = document.getElementById(inputId);
  if (searchInput) {
    searchInput.addEventListener('input', (event) => {
      searchHandler(event.target.value);
    });
    return searchInput;
  }
  console.warn(`Search input not found: ${inputId}`);
  return null;
}

// ==================== RESULT ITEM GENERATION ====================

export function generateResultItem(config) {
  const { meta, title, subtitle = '', buttons = [], detailsId = '', highlight = false } = config;

  const buttonHTML = buttons
    .map(
      (btn) => `
        <button
          type="button"
          onclick="${btn.action}"
          class="rounded-lg bg-brand-600 px-3 py-1 text-xs font-semibold text-white shadow-sm transition hover:bg-brand-700"
        >
          ${btn.text}
        </button>
      `
    )
    .join('');

  const subtitleHTML = subtitle ? `<p class="mt-2 text-xs text-slate-500">${subtitle}</p>` : '';

  const detailsHTML = detailsId
    ? `<div id="${detailsId}" class="mt-3 hidden rounded-xl border border-slate-200 bg-slate-50/70 p-3 text-sm text-slate-600"></div>`
    : '';

  const titleClass = highlight ? 'highlight' : '';

  return `
    <article class="result-item rounded-2xl border border-slate-200 bg-white/95 p-4 shadow-sm">
      <header class="result-meta text-xs font-semibold uppercase tracking-wide text-brand-600">${meta}</header>
      <div class="result-snippet mt-2 space-y-2">
        <div class="flex items-start justify-between gap-3">
          <span class="${titleClass} text-sm font-semibold text-slate-900">${title}</span>
          <div class="flex flex-wrap gap-2">${buttonHTML}</div>
        </div>
        ${subtitleHTML}
      </div>
      ${detailsHTML}
    </article>
  `;
}

// ==================== TOGGLE DETAILS FUNCTIONALITY ====================

export function toggleDetails(detailsId, contentGenerator, emptyMessage = 'Details nicht verfügbar') {
  const container = document.getElementById(detailsId);
  if (!container) return false;

  const isHidden = container.classList.contains('hidden') || container.style.display === 'none' || container.style.display === '';

  if (!isHidden) {
    container.classList.add('hidden');
    container.style.display = 'none';
    return true;
  }

  try {
    const content = contentGenerator();
    if (content === null || content === '') {
      container.innerHTML = `
        <div class="text-xs italic text-slate-500">${emptyMessage}</div>
      `;
    } else {
      container.innerHTML = content;
    }
    container.classList.remove('hidden');
    container.style.display = 'block';
    return true;
  } catch (error) {
    container.innerHTML = `
      <div class="text-xs text-red-600">Fehler beim Laden: ${error.message}</div>
    `;
    container.classList.remove('hidden');
    container.style.display = 'block';
    return false;
  }
}

// ==================== EMPTY STATE HANDLING ====================

export function showEmptySearchState(containerId, message = 'Geben Sie einen Suchbegriff ein, um zu starten.') {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = `
      <div class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center text-sm text-slate-500">
        ${message}
      </div>
    `;
    return true;
  }
  return false;
}

// ==================== RENDER TO CONTAINER ====================

export function renderToContainer(containerId, html) {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = html;
    return true;
  }
  console.warn(`Container not found: ${containerId}`);
  return false;
}

// ==================== STRING UTILITIES ====================

export function escapeForJS(str) {
  return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

export function formatMetadata(items, separator = ' • ') {
  return items.filter(Boolean).join(separator);
}

export function formatMultiLanguage(termDE, termEN) {
  if (termDE && termEN) return `${termDE} / ${termEN}`;
  return termDE || termEN || '';
}

// ==================== SEARCH PATTERNS ====================

export const SearchPatterns = {
  // Legacy patterns (kept for backward compatibility, but consider using normalized versions)
  textContains: (items, searchTerm, fieldGetter) => {
    const term = searchTerm.toLowerCase().trim();
    return items.filter((item) => fieldGetter(item).toLowerCase().includes(term));
  },

  multiField: (items, searchTerm, fieldGetters) => {
    const term = searchTerm.toLowerCase().trim();
    const matchedItems = new Set();

    items.forEach((item) => {
      const hasMatch = fieldGetters.some(
        (getter) => getter(item) && getter(item).toLowerCase().includes(term)
      );
      if (hasMatch) {
        matchedItems.add(item);
      }
    });

    return Array.from(matchedItems);
  },

  exactMatch: (items, searchTerm, fieldGetter) => {
    const term = searchTerm.toLowerCase().trim();
    return items.filter((item) => fieldGetter(item).toLowerCase() === term);
  },

  // ==================== NORMALIZED PATTERNS (MHG-aware) ====================
  // Use these for Middle High German text search with special character normalization

  /**
   * Search with MHG character normalization (â→a, ô→o, ü→ue, etc.)
   * Example: searching "brot" will find "brôt"
   */
  textContainsNormalized: (items, searchTerm, fieldGetter) => {
    return items.filter((item) =>
      TextNormalizer.matchesNormalized(fieldGetter(item), searchTerm)
    );
  },

  /**
   * Multi-field search with MHG normalization
   * Searches across multiple fields, matching if ANY field contains the term
   */
  multiFieldNormalized: (items, searchTerm, fieldGetters) => {
    const matchedItems = new Set();

    items.forEach((item) => {
      const hasMatch = fieldGetters.some(
        (getter) => getter(item) && TextNormalizer.matchesNormalized(getter(item), searchTerm)
      );
      if (hasMatch) {
        matchedItems.add(item);
      }
    });

    return Array.from(matchedItems);
  },

  /**
   * Exact match with MHG normalization
   * Normalized versions must be identical
   */
  exactMatchNormalized: (items, searchTerm, fieldGetter) => {
    return items.filter((item) =>
      TextNormalizer.exactMatchNormalized(fieldGetter(item), searchTerm)
    );
  },

  /**
   * Starts-with search with MHG normalization
   * Useful for autocomplete/prefix matching
   */
  startsWithNormalized: (items, searchTerm, fieldGetter) => {
    return items.filter((item) =>
      TextNormalizer.startsWithNormalized(fieldGetter(item), searchTerm)
    );
  },
};
