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
 *   multi-lemma, words, lines, annotations
 *
 * Example URLs:
 *   playground/#authors                          → open Autoren-Explorer
 *   playground/#concepts                         → open Begriffs-Explorer
 *   playground/#multi-lemma                      → open Multi-Lemma-Suche modal
 */

const ROUTES = {
  'authors':     () => window.playground.ui.authorityExplorers.showAuthors(),
  'works':       () => window.playground.ui.authorityExplorers.showWorks(),
  'lemmata':     () => window.playground.ui.authorityExplorers.showLemmata(),
  'concepts':    () => window.playground.ui.authorityExplorers.showConcepts(),
  'genres':      () => window.playground.ui.authorityExplorers.showGenres(),
  'names':       () => window.playground.ui.authorityExplorers.showNames(),
  'multi-lemma': () => window.playground.ui.multiLemmaSearch.open(),
  'words':       () => window.playground.ui.teiExplorer.showWords(),
  'lines':       () => window.playground.ui.teiExplorer.showLines(),
  'annotations': () => window.playground.ui.teiExplorer.showAnnotations(),
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
 * Navigate to a view: update the URL hash AND dispatch the route handler.
 * Call this from button click handlers so the URL reflects what's on screen.
 */
export function navigate(view, params = {}) {
  const handler = ROUTES[view];
  if (!handler) {
    console.warn(`[Router] Unknown view: ${view}`);
    return;
  }

  // Suppress our own hashchange listener so we don't double-dispatch
  _suppressHashUpdate = true;
  window.location.hash = buildHash(view, params);
  // Release on next tick — the hashchange event fires synchronously after
  // setting location.hash in most browsers, so one tick is enough
  setTimeout(() => { _suppressHashUpdate = false; }, 0);

  handler(params);
}

/**
 * Dispatch the current hash, if any. Called once on page load (after data
 * is ready) to restore state from a bookmarked/shared URL, and from the
 * hashchange listener to handle browser back/forward.
 */
export function dispatchFromHash() {
  const parsed = parseHash();
  if (!parsed) return;

  const handler = ROUTES[parsed.view];
  if (!handler) {
    console.warn(`[Router] Unknown view in URL hash: ${parsed.view}`);
    return;
  }

  handler(parsed.params);
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
