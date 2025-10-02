/**
 * MHDBDB Playground - Authority Files Manager
 * Handles building performance indexes from pre-loaded authority data
 * NOTE: Authority data is now loaded via pre-built index (authority-index.json.gz)
 *       in main.js using CorpusLoader, not via XML files anymore.
 */

import { TextNormalizer } from '../../lib/text-normalizer.js';

export class AuthorityFilesManager {
  constructor(authorityData) {
    this.authorityData = authorityData;

    // Performance indexes (built from pre-loaded data)
    this.indexes = {
      genreToWorks: new Map(),
      workToGenres: new Map(),
      genreHierarchy: new Map(),
      conceptToLemmas: new Map(),
    };
  }

  // ==================== PERFORMANCE INDEXES (NEW - FROM PRE-LOADED DATA) ====================

  /**
   * Build performance indexes from pre-loaded authority data
   * Called after authority index is loaded in main.js
   */
  buildPerformanceIndexes() {
    console.log('[AuthorityFilesManager] Building performance indexes from pre-loaded data...');

    // These indexes are optional - if data is missing, skip
    try {
      // Build genre-work mappings (if we have the data)
      // NOTE: Currently not available in pre-built index
      // Could be added in future versions

      // Build concept-lemma mappings (if needed for concept searches)
      // NOTE: Currently not needed as concept search doesn't use this

      console.log('[AuthorityFilesManager] Performance indexes built (optional indexes skipped)');
    } catch (error) {
      console.warn('[AuthorityFilesManager] Error building performance indexes:', error);
    }
  }

  // ==================== DEAD CODE REMOVED ====================
  // The following functions relied on parsedXML which no longer exists
  // (authority data now loaded via pre-built index in main.js):
  //   - loadAuthorityFiles()
  //   - buildIndexes()
  //   - buildGenreWorkIndexes()
  //   - buildGenreHierarchyIndex()
  //   - buildConceptLemmaIndex()
  //   - processAuthorityFileContent()
  //   - analyzeAuthorityFile()
  //   - All extraction methods (extractPersons, extractWorks, etc.)
  //   - findLemmaInXML()
  //   - findWorksInGenre()

  // ==================== LEMMA RESOLUTION ====================

  resolveLemmaNames(searchTerms) {
    const resolvedLemmas = [];
    
    searchTerms.forEach(term => {
      // Check if it's already a lemma ID
      if (/^lemma_\d+$/.test(term) || /^\d+$/.test(term)) {
        const lemmaId = term.replace('lemma_', '');
        const lemma = this.authorityData.lemmata.find(l => l.id === `lemma_${lemmaId}`);
        if (lemma) {
          resolvedLemmas.push({
            input: term,
            lemmaId: lemmaId,
            lemma: lemma
          });
        }
        return;
      }
      
      // Search by orthography
      const normalizedTerm = term.toLowerCase();
      const matchingLemma = this.authorityData.lemmata.find(l => 
        l.lemma && l.lemma.toLowerCase() === normalizedTerm
      );
      
      if (matchingLemma) {
        resolvedLemmas.push({
          input: term,
          lemmaId: matchingLemma.id.replace('lemma_', ''),
          lemma: matchingLemma
        });
      }
    });
    
    return resolvedLemmas;
  }

  searchLemmaByOrthography(orthography) {
    const normalized = orthography.toLowerCase();
    const normalizedCharacters = TextNormalizer.normalizeMHG(normalized);
    console.log(`🔎 searchLemmaByOrthography("${orthography}") → normalized: "${normalizedCharacters}"`);

    // Stage 1: Try exact match in lexicon (fastest, canonical forms)
    // Try both original and normalized
    const exactMatch = this.authorityData.lemmata.find(lemma => {
      if (!lemma.lemma) return false;
      const lemmaLower = lemma.lemma.toLowerCase();
      const lemmaNormalized = TextNormalizer.normalizeMHG(lemmaLower);
      return lemmaLower === normalized || lemmaNormalized === normalizedCharacters;
    });
    if (exactMatch) {
      console.log(`  ✅ Stage 1 (lexicon exact): Found ${exactMatch.id}`);
      return [exactMatch];
    }

    // Stage 2: Search in variants index (orthographic variants from TEI corpus)
    console.log(`  📊 Variants index size: ${this.authorityData.variants.length} entries`);
    if (this.authorityData.variants.length > 0) {
      const matchingVariants = [];

      for (const variantEntry of this.authorityData.variants) {
        // Check if any form matches the search term (with normalization)
        const hasMatch = variantEntry.forms.some(form => {
          const formLower = form.orth.toLowerCase();
          const formNormalized = TextNormalizer.normalizeMHG(formLower);
          return formLower === normalized || formNormalized === normalizedCharacters;
        });

        if (hasMatch) {
          // Find the corresponding lemma in lemmata array
          const lemma = this.authorityData.lemmata.find(l => l.id === variantEntry.lemmaId);
          if (lemma) {
            matchingVariants.push(lemma);
            console.log(`  ✅ Stage 2 (variants): Found ${lemma.id} via variant "${orthography}"`);
          }
        }
      }

      if (matchingVariants.length > 0) {
        return matchingVariants;
      }
    }

    // Stage 3: Fallback to partial match in lexicon (includes search with normalization)
    const partialMatches = this.authorityData.lemmata.filter(lemma => {
      if (!lemma.lemma) return false;
      return TextNormalizer.matchesNormalized(lemma.lemma, orthography);
    });
    if (partialMatches.length > 0) {
      console.log(`  ⚠️ Stage 3 (partial): Found ${partialMatches.length} matches`);
    } else {
      console.log(`  ❌ No matches found for "${orthography}"`);
    }
    return partialMatches;
  }

  findLemmaById(lemmaId) {
    return this.authorityData.lemmata.find(l => 
      l.id === `lemma_${lemmaId}` || l.id === lemmaId
    );
  }

  getLemmaSuggestions(partialInput, maxSuggestions = 10) {
    const normalized = partialInput.toLowerCase();
    return this.authorityData.lemmata
      .filter(lemma => 
        lemma.lemma && lemma.lemma.toLowerCase().startsWith(normalized)
      )
      .slice(0, maxSuggestions)
      .map(lemma => ({
        lemma: lemma.lemma,
        id: lemma.id.replace('lemma_', ''),
        pos: lemma.pos
      }));
  }

  // ==================== UTILITY METHODS ====================

  updateStatus(indicator, text) {
    const statusIndicator = document.getElementById("statusIndicator");
    const statusText = document.getElementById("statusText");

    if (statusIndicator) statusIndicator.textContent = indicator;
    if (statusText) statusText.textContent = text;

    // Enhanced logging with cache information
    console.log(`${indicator} ${text}`);
  }

  // ==================== DEAD CODE REMOVED ====================
  // The following cache management methods relied on storageManager which no longer exists
  // (authority data now loaded via CorpusLoader with Dexie.js caching):
  //   - getCacheStatus()
  //   - clearCache()
  //   - clearExpiredCache()
  //   - getLoadStatistics()
  //   - refreshAuthorityFile()
  //   - getStorageDebugInfo()
  //
  // Cache management is now handled by CorpusLoader in js/corpus-loader.js
}
