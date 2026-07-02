/**
 * Shared HTML/attribute escaping for the main site and the lemma pages.
 *
 * Escapes quotes as well: values are interpolated into attribute contexts
 * (href="...") where the older textContent/innerHTML trick's missing
 * quote-escaping enabled attribute breakout (PR #157 review).
 *
 * NOTE: the playground TEI modules keep per-module escape helper copies by
 * documented convention (DESIGN.md §Playground TEI-Analysis Module Pattern)
 * — this module covers the main site (app.js) and lemma/lemma-page.js.
 */
export function escapeHtml(text) {
    if (text == null) return '';
    return String(text).replace(/[&<>"']/g, c => (
        { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
    ));
}
