# Shared Library (`/lib`)

This directory contains shared utilities used by both the main site (`/js`) and the playground (`/playground/js`).

## Files

### `text-normalizer.js`
Middle High German character normalization utilities.

**Exports:**
- `TextNormalizer` class with static methods for MHG text normalization

**Usage:**
```javascript
import { TextNormalizer } from '../../lib/text-normalizer.js';

const normalized = TextNormalizer.normalizeMHG('brôt'); // 'brot'
const matches = TextNormalizer.matchesNormalized('brôt', 'brot'); // true
```

### `corpus-loader.js`
Shared corpus loading logic with IndexedDB integration.

**Exports:**
- `CorpusLoader` class for loading TEI corpus and authority data

**Usage:**
```javascript
import { CorpusLoader } from '../../lib/corpus-loader.js';

const loader = new CorpusLoader();
const authorityData = await loader.loadAuthorityIndex();
```

### `lemma-match.js`
Exact-token matching of a searched lemma id against a `@lemmaRef` (CONTRACTS §B.1). Single source for the highlight/match decision, shared by reader and playground (#130 — was 6 inline copies).

**Exports:**
- `lemmaRefMatchesId(lemmaRef, lemmaId)` → boolean (exact whitespace-separated token, never a substring)

**Usage:**
```javascript
import { lemmaRefMatchesId } from '../../lib/lemma-match.js';

lemmaRefMatchesId('lexicon.xml#lemma_308', 'lemma_308');  // true
lemmaRefMatchesId('lexicon.xml#lemma_3089', 'lemma_308'); // false (substring trap)
```

## Design Principles

1. **DRY (Don't Repeat Yourself)**: All shared code lives here
2. **Framework-agnostic**: Vanilla JavaScript, no dependencies
3. **ES6 Modules**: Use `export` and `import` syntax
4. **Documented**: Each file has usage examples in this README
