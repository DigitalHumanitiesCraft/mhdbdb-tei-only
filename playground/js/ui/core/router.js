/**
 * MHDBDB Playground - Hash Router
 *
 * Hash-based URL routing so that playground explorations are bookmarkable,
 * shareable, and navigable with browser back/forward. The URL hash is the
 * authoritative source of truth for the current view; both direct URL entry
 * and button clicks go through the router.
 *
 * URL scheme: #<view>[&<key>=<value>&...]
 * Supported views:
 *   authors, works, lemmata, concepts, genres, names,
 *   multi-lemma, verse-position, word-frequency, text-statistics, lemma-distribution,
 *   concept-distribution, text-comparison, cooccurrence-ranking, rhyme-dictionary, naming
 *
 * Example URLs:
 *   playground/#authors                          → open Autoren-Explorer
 *   playground/#concepts                         → open Begriffs-Explorer
 *   playground/#multi-lemma                      → open Multi-Lemma-Suche modal
 *   playground/#verse-position                   → open Lemmasuche nach Versposition
 *   playground/#word-frequency                   → open Wortfrequenz-Analyse
 *   playground/#text-statistics                  → open Text-Statistiken
 *   playground/#lemma-distribution               → open Lemma-Verteilung
 *   playground/#concept-distribution             → open Begriffs-Verteilung
 *   playground/#text-comparison                  → open Textvergleich
 *   playground/#cooccurrence-ranking             → open Kookkurrenz-Ranking
 *   playground/#rhyme-dictionary                 → open Reim-Wörterbuch
 *   playground/#naming                           → open Erweiterte Figurenbezeichnungen (Beta)
 */

const ROUTES = {
  'authors':            (params) => window.playground.ui.authorityExplorers[params.q ? 'showAuthorsWithSearch'  : 'showAuthors'](),
  'works':              (params) => window.playground.ui.authorityExplorers[params.q ? 'showWorksWithSearch'    : 'showWorks'](),
  'lemmata':            (params) => window.playground.ui.authorityExplorers[params.q ? 'showLemmataWithSearch'  : 'showLemmata'](),
  'concepts':           (params) => window.playground.ui.authorityExplorers[params.q ? 'showConceptsWithSearch' : 'showConcepts'](),
  'genres':             (params) => window.playground.ui.authorityExplorers[params.q ? 'showGenresWithSearch'   : 'showGenres'](),
  'names':              (params) => window.playground.ui.authorityExplorers[params.q ? 'showNamesWithSearch'    : 'showNames'](),
  'multi-lemma':        (params) => handleMultiLemmaRoute(params),
  'verse-position':     ()       => window.playground.ui.versePositionSearch.show(),
  'word-frequency':     ()       => window.playground.ui.wordFrequency.show(),
  'text-statistics':    ()       => window.playground.ui.textStatistics.show(),
  'lemma-distribution': ()       => window.playground.ui.lemmaDistribution.show(),
  'concept-distribution': ()     => window.playground.ui.conceptDistribution.show(),
  'text-comparison':    ()       => window.playground.ui.textComparison.show(),
  'cooccurrence-ranking': ()     => window.playground.ui.cooccurrenceRanking.show(),
  'rhyme-dictionary':   ()       => window.playground.ui.rhymeDictionary.show(),
  'naming':             ()       => window.playground.ui.namingExplorer.show(),
};

/**
 * Mapping from view key to the DOM id of its search input (if any).
 * Used by dispatch() to auto-fill the input when a `q` param is present in
 * the URL hash. Views without a search input (multi-lemma) are intentionally
 * absent.
 */
const SEARCH_INPUT_IDS = {
  'authors':  'authorSearch',
  'works':    'workSearch',
  'lemmata':  'lemmaSearch',
  'concepts': 'conceptSearch',
  'genres':   'genreSearch',
  'names':    'nameSearch',
};

/**
 * Flag to suppress the hashchange listener during programmatic navigation.
 * Without this, `navigate()` would both push the hash AND re-dispatch via
 * the hashchange event, causing duplicate renders.
 */
let _suppressHashUpdate = false;

/** Parse the current hash into { view, params }, or null if empty. */
export function parseHash() {
  const hash = window.location.hash.slice(1); // strip leading '#'
  if (!hash) return null;

  const parts = hash.split('&');
  const view = parts[0];
  const params = {};

  for (let i = 1; i < parts.length; i++) {
    const eqIdx = parts[i].indexOf('=');
    if (eqIdx === -1) continue;
    const key = parts[i].slice(0, eqIdx);
    const rawValue = parts[i].slice(eqIdx + 1);
    try {
      params[key] = decodeURIComponent(rawValue);
    } catch (e) {
      params[key] = rawValue; // fallback for malformed encoding
    }
  }

  return { view, params };
}

/** Build a hash string from a view key and params object. */
export function buildHash(view, params = {}) {
  const parts = [view];
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      parts.push(`${key}=${encodeURIComponent(value)}`);
    }
  }
  return '#' + parts.join('&');
}

/**
 * Handle the `multi-lemma` route. Without params, just opens the (empty)
 * Multi-Lemma-Suche modal. With `lemmata` (comma-separated list), populates
 * the modal state directly and runs the search in the background — the
 * modal is never shown to the user, results appear in resultsContainer.
 *
 * Supported params:
 *   lemmata — comma-separated list of lemma terms, e.g. "minne,êre"
 *   mode    — "proximity" (default) or "document"
 *   dist    — proximity distance (integer, default 10, only used in proximity mode)
 */
function handleMultiLemmaRoute(params) {
  const ui = window.playground?.ui?.multiLemmaSearch;
  if (!ui) {
    console.warn('[Router] multi-lemma UI not available');
    return;
  }

  // No lemmata param → just open the empty modal (Phase 1+2 behavior)
  if (!params.lemmata) {
    ui.open();
    return;
  }

  const terms = params.lemmata.split(',').map(t => t.trim()).filter(t => t);
  if (terms.length === 0) {
    ui.open();
    return;
  }

  // Ensure a clean state (in case a previous route left residual chips)
  ui.lemmas = [];
  if (ui.lemmaChips) ui.lemmaChips.innerHTML = '';

  // Populate the modal's internal state + chip DOM without opening the modal.
  // executeSearch() will copy `this.lemmas` to a local `searchTerms` before
  // calling close() → reset(), so this clean-up after the search is harmless.
  for (const term of terms) {
    ui.lemmas.push(term);
    ui.addLemmaChip(term);
  }

  // Set search mode (defaults to proximity per v4.0.0 convention)
  const mode = params.mode === 'document' ? 'document' : 'proximity';
  const modeRadio = document.querySelector(`input[name="searchMode"][value="${mode}"]`);
  if (modeRadio) {
    modeRadio.checked = true;
    // Trigger change so the proximity-controls block shows/hides correctly
    modeRadio.dispatchEvent(new Event('change', { bubbles: true }));
  }

  // Set proximity distance
  if (params.dist && ui.proximityDistance) {
    const distNum = parseInt(params.dist, 10);
    if (distNum > 0) ui.proximityDistance.value = String(distNum);
  }

  // Enable the Execute button (normally disabled until lemmas.length > 0)
  // and run the search. executeSearch() is async and will update the
  // resultsContainer itself when the corpus query completes.
  ui.updateExecuteButton();
  ui.executeSearch();
}

/**
 * Trigger a drill-down expansion for a specific item in the currently-rendered
 * result set. Finds the first button whose onclick attribute references the
 * given itemId as a single-quoted substring and clicks it.
 *
 * Works for any explorer whose result items embed their item ID in the
 * expand button's onclick handler — which is the current convention across
 * all authority explorers (see generateResultItem() callers). Silently fails
 * if the target item isn't in the visible result set or the itemId doesn't
 * match any button.
 */
function triggerExpand(itemId) {
  const container = document.getElementById('resultsContainer');
  if (!container) return false;
  const needle = `'${itemId}'`;
  const buttons = container.querySelectorAll('button[onclick]');
  for (const btn of buttons) {
    if (btn.getAttribute('onclick')?.includes(needle)) {
      btn.click();
      return true;
    }
  }
  return false;
}

/**
 * Dispatch a view + params: run the route handler and, if `q` or `show`
 * params are present, auto-fill the search input (triggering the search
 * listener) and then trigger the drill-down expansion for the specified
 * item. Shared by navigate() and dispatchFromHash().
 */
function dispatch(view, params) {
  const handler = ROUTES[view];
  if (!handler) {
    console.warn(`[Router] Unknown view: ${view}`);
    return;
  }

  handler(params);

  if (params.q) {
    const inputId = SEARCH_INPUT_IDS[view];
    if (inputId) {
      // Defer to the next tick so the search UI has been inserted into the
      // DOM and setupSearchInput() has wired up the input event listener.
      setTimeout(() => {
        const input = document.getElementById(inputId);
        if (input) {
          input.value = params.q;
          input.dispatchEvent(new Event('input', { bubbles: true }));
          input.focus();
          // Search render ran synchronously inside the input listener, so
          // the result buttons are in the DOM now. Try the drill-down here.
          if (params.show) triggerExpand(params.show);
        }
      }, 0);
    }
  } else if (params.show) {
    // No q: the default view (showXxx()) has rendered either all items
    // (<500 entries) or a search-empty-state. Try the drill-down once the
    // DOM has committed the default render.
    setTimeout(() => triggerExpand(params.show), 0);
  }
}

/**
 * Navigate to a view: update the URL hash AND dispatch the route handler.
 * Call this from button click handlers so the URL reflects what's on screen.
 */
export function navigate(view, params = {}) {
  // Suppress our own hashchange listener so we don't double-dispatch
  _suppressHashUpdate = true;
  window.location.hash = buildHash(view, params);
  // Release on next tick — hashchange is queued as an async task, never
  // fired synchronously. The setTimeout(0) reset runs AFTER that queued task,
  // which is exactly why it must not be replaced by a synchronous reset
  // (the guard would expire before the event fires -> double dispatch).
  setTimeout(() => { _suppressHashUpdate = false; }, 0);

  dispatch(view, params);
}

/**
 * Dispatch the current hash, if any. Called once on page load (after data
 * is ready) to restore state from a bookmarked/shared URL, and from the
 * hashchange listener to handle browser back/forward.
 */
export function dispatchFromHash() {
  const parsed = parseHash();
  if (!parsed) return;
  dispatch(parsed.view, parsed.params);
}

/**
 * Wire up the hashchange listener. Call once after the playground has
 * finished loading its data, then immediately call dispatchFromHash() to
 * restore any initial state from the URL.
 */
export function initRouter() {
  window.addEventListener('hashchange', () => {
    if (_suppressHashUpdate) return;
    dispatchFromHash();
  });
}
