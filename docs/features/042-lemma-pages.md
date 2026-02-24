# Issue #42: Persistent Lemma Pages + MWB-API Preparation

## Context

MWB (Mittelhochdeutsches Worterbuch) and Worterbuchnetz want to link to MHDBDB lemmata from their global dictionary search. Currently, MHDBDB has no linkable lemma page. The old Java app URL (`http://mhdbdb.sbg.ac.at:8000//mhdbdb/App?action=Dic&lid=879`) still works but will die.

**Deadline:** End of March 2025 (MWB evaluation).

## Key Finding: IDs Already Aligned

| System | brôt | minne |
|--------|------|-------|
| Our `lexicon.xml` | `lemma_879` | `lemma_4130` |
| Worterbuchnetz `lid=` | 879 | 4130 |
| Wikidata P9351 | 879 | 4130 |
| Old MHDBDB URL | `?lid=879` | `?lid=4130` |

Zero mapping work. The numeric suffix IS the shared ID.

## URL Routing Decision

**Constraint:** GitHub Pages static hosting, no server-side routing, no 404.html trick configured.

| Option | URL | Pros | Cons |
|--------|-----|------|------|
| **A. Query param** | `lemma/?id=879` | Simple, works everywhere | Less clean |
| **B. Hash routing** | `lemma/#879` | Simple, no server config | Fragment not sent to server, SEO-invisible |
| **C. Clean path** | `lemma/879` | Cleanest, best for external linking | Needs 404.html redirect on GitHub Pages |

**Decision: Option C with 404.html fallback.**

Rationale: External systems (Worterbuchnetz, Wikidata) will store these URLs for years. Clean paths are the standard for persistent identifiers in DH. The 404.html trick is well-established for GitHub Pages SPAs.

**Canonical URL pattern:**
```
https://dhcraft.org/mhdbdb-tei-only/lemma/879
```

**Fallback support:** Also accept `lemma/?id=879` and `lemma/#879` — redirect both to the canonical path.

## Page Layout

Single-page design matching existing Tailwind/brand style (header, content, footer).

### Sections

1. **Header** — Same nav as korpus.html (Startseite, Korpus, Playground, Dokumentation)

2. **Lemma Title Block**
   - Lemma orthography (large): `brôt`
   - Normalized form (small, grey): `brot`
   - POS badge: `NOM`
   - Lemma ID (monospace, copyable): `lemma_879`

3. **Etymology** (if present)
   - Morphological components as clickable links to their lemma pages
   - Example: ahzehen = [zehen](lemma/7779) + [aht](lemma/95)

4. **Senses**
   - Each sense listed with its concept labels (DE + EN)
   - Concept IDs linked to playground concept explorer

5. **Corpus Occurrences**
   - Count: "Belegt in X von 666 Texten"
   - List of texts (sigle + title), each clickable to korpus.html reading view
   - Sorted by frequency (most occurrences first)

6. **External Links**
   - Worterbuchnetz: `https://woerterbuchnetz.de/?sigle=MHDBDB&lemid=L{id}`
   - Old MHDBDB: `http://mhdbdb.sbg.ac.at:8000//mhdbdb/App?action=Dic&lid={id}`
   - Wikidata (if mappable): `https://www.wikidata.org/wiki/Property:P9351`
   - MWB backlink (future, needs ID mapping)

7. **Footer** — Same as other pages (license, contact)

## Data Flow

```
URL: /lemma/879
        |
        v
lemma/index.html loads
        |
        v
Extract ID from URL path (or query param, or hash)
        |
        v
Load authority-index.json.gz (from IndexedDB cache or network)
        |
        v
Find lemma_879 in lemmata array
        |
        v
Load corpus-index.json.gz (from IndexedDB cache or network)
        |
        v
Find lemma_879 in lemmaIndex → list of text IDs
        |
        v
Render page with all sections
```

## Files to Create/Modify

### New Files
- `lemma/index.html` — The lemma page (HTML + inline loading)
- `lemma/lemma-page.js` — Page logic (ES6 module)
- `404.html` — GitHub Pages SPA redirect (copies path to query string, redirects to index)

### Modified Files
- `tailwind.config.js` — Add `./lemma/**/*.{html,js}` to content paths
- `.gitignore` — No changes needed
- `assets/css/tailwind-output.css` — Rebuild after tailwind config change

## Implementation Steps

1. Create `lemma/index.html` with static shell (header, empty content area, footer)
2. Create `lemma/lemma-page.js`:
   - Parse ID from `window.location.pathname` (split on `/lemma/`)
   - Fallback: check `?id=` and `#` for alternative access patterns
   - Load authority index via existing CorpusLoader pattern
   - Render lemma data into DOM
   - Load corpus index for occurrence count
3. Create `404.html` at project root for GitHub Pages path-based routing
4. Rebuild Tailwind CSS
5. Add Playwright test for lemma page
6. Update CLAUDE.md and docs

## Success Criteria

- [ ] `https://dhcraft.org/mhdbdb-tei-only/lemma/879` shows brôt lemma page
- [ ] `https://dhcraft.org/mhdbdb-tei-only/lemma/4130` shows minne lemma page
- [ ] Page loads in <3 seconds (authority index already cached)
- [ ] All 43,750 lemma IDs resolve to a page
- [ ] Invalid IDs show a clear "Lemma nicht gefunden" message
- [ ] External links section present and correct
- [ ] Corpus occurrence count matches actual data
- [ ] Clicking a text in occurrences opens korpus.html reading view
- [ ] Playwright test covers: load, display, navigation, invalid ID

## Out of Scope (for now)

- MWB ID mapping (needs their ID list — Katharina's "Retour-Verlinkung")
- Worterbuchnetz API integration for live cross-references
- Search within lemma page
- Lemma-to-lemma navigation (beyond etymology links)
- Updating Wikidata P9351 formatter URL

## Open Questions

1. Should the lemma page also load the full TEI text for inline attestation examples? (Probably not for v1 — too heavy)
2. Should we add `<link rel="canonical">` and structured data (JSON-LD) for SEO? (Nice to have)
3. MWB backlink: Do we need their ID mapping table, or can we derive it from Lexer references?
