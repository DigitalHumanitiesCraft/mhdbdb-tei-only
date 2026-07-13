/**
 * MHDBDB Playground - Authority Files Manager
 * Handles building performance indexes from pre-loaded authority data
 * NOTE: Authority data is now loaded via pre-built index (authority-index.json.gz)
 *       in main.js using CorpusLoader, not via XML files anymore.
 */

import { TextNormalizer } from '../../../assets/js/lib/text-normalizer.js';

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

    // Stage 1: Exact match in lexicon (canonical forms). Sammelt ALLE
    // Homographen (z.B. rôt: NAM lemma_11330, NOM lemma_19417, ADJ
    // lemma_4954) statt nur den ersten Array-Treffer — matches[0]-Konsumenten
    // (Multi-Lemma-Suche, Kookkurrenz, Reim, Versposition) bekamen sonst
    // je nach Index-Reihenfolge einen 1-Beleg-Eigennamen statt des
    // hochfrequenten Appellativs (#163/#164). Sortierung: Korpus-Frequenz
    // absteigend, bei Gleichstand diakritisch-exakte Eingabe zuerst.
    const exactMatches = this.authorityData.lemmata.filter(lemma => {
      if (!lemma.lemma) return false;
      const lemmaLower = lemma.lemma.toLowerCase();
      const lemmaNormalized = TextNormalizer.normalizeMHG(lemmaLower);
      return lemmaLower === normalized || lemmaNormalized === normalizedCharacters;
    });
    if (exactMatches.length > 0) {
      return this.rankHomographs(exactMatches, normalized);
    }

    // Stage 2: Search in variants index (orthographic variants from TEI corpus)
    // Structure: variants = {normalized_variant: lemma_id, ...}
    const variantsCount = Object.keys(this.authorityData.variants || {}).length;

    if (variantsCount > 0) {
      // Try normalized lookup in variants dictionary
      const lemmaId = this.authorityData.variants[normalizedCharacters];

      if (lemmaId) {
        // Find the corresponding lemma in lemmata array
        const lemma = this.authorityData.lemmata.find(l => l.id === lemmaId);
        if (lemma) {
          return [lemma];
        }
      }
    }

    // Stage 3: Fallback to partial match in lexicon (includes search with normalization)
    const partialMatches = this.authorityData.lemmata.filter(lemma => {
      if (!lemma.lemma) return false;
      return TextNormalizer.matchesNormalized(lemma.lemma, orthography);
    });
    return partialMatches;
  }

  /**
   * Homographen nach Korpus-Frequenz absteigend sortieren; bei Gleichstand
   * gewinnt die diakritisch-exakte Schreibform der Eingabe, danach bleibt
   * die Index-Reihenfolge stabil. Ist der Corpus-Index noch nicht geladen,
   * sind alle Frequenzen 0 und die bisherige Reihenfolge bleibt erhalten.
   */
  rankHomographs(lemmata, normalizedInput) {
    if (lemmata.length <= 1) return lemmata;
    const decorated = lemmata.map((lemma, idx) => ({
      lemma,
      idx,
      freq: this.getCorpusFrequency(lemma.id),
      exact: lemma.lemma && lemma.lemma.toLowerCase() === normalizedInput ? 0 : 1
    }));
    decorated.sort((a, b) =>
      (b.freq - a.freq) || (a.exact - b.exact) || (a.idx - b.idx)
    );
    return decorated.map(d => d.lemma);
  }

  /**
   * Gesamtzahl der Vorkommen eines Lemmas im Korpus (Summe über alle
   * texts[].lemmata[id]-Positionslisten des Corpus-Index). Ergebnisse werden
   * gecacht — aber erst, sobald der Corpus-Index geladen ist, damit ein
   * früher Aufruf (Autocomplete vor Corpus-Load) keine Nullen einfriert.
   */
  getCorpusFrequency(lemmaId) {
    if (this._corpusFreqCache?.has(lemmaId)) {
      return this._corpusFreqCache.get(lemmaId);
    }
    const texts = window.playground?.corpusData?.texts;
    if (!texts || texts.length === 0) return 0;
    let total = 0;
    for (const t of texts) {
      const positions = t.lemmata?.[lemmaId];
      if (positions) total += positions.length;
    }
    if (!this._corpusFreqCache) this._corpusFreqCache = new Map();
    this._corpusFreqCache.set(lemmaId, total);
    return total;
  }

  findLemmaById(lemmaId) {
    return this.authorityData.lemmata.find(l => 
      l.id === `lemma_${lemmaId}` || l.id === lemmaId
    );
  }

  /**
   * Live-Autocomplete-Suggestions: prefix-match auf `lemma.normalized`
   * (mhd-normalisiert) mit includes-Fallback. Liefert vollständige Lemma-
   * Objekte (`{id, lemma, pos, ...}` mit `lemma_X`-Präfix).
   *
   * Genutzt von lemma-distribution.js, verse-position-search.js,
   * cooccurrence-ranking.js für Live-Dropdown im Lemma-Input. Siehe
   * DESIGN.md §Live-Autocomplete-Dropdown.
   *
   * Eingabe wird mit TextNormalizer.normalizeMHG normalisiert (â→a, ê→e,
   * ü→ue, æ→ae, ō→o, …) damit „ere" auch „êre" matcht — derselbe Normalizer,
   * mit dem lemma.normalized gebaut wird (CONTRACTS §A). Linear scan über
   * 43.754 Lemmata, ~5-10ms pro Aufruf — akzeptabel für keystroke-Frequenz.
   */
  getLemmaAutocompleteMatches(partialInput, maxSuggestions = 8) {
    const trimmed = (partialInput || '').trim();
    if (!trimmed) return [];
    // Kanonischer Normalizer statt Inline-Regex-Kette: lemma.normalized ist
    // mit normalizeMHG gebaut — eine abweichende Eingabe-Normalisierung
    // (fehlende Ligaturen æ/œ, Makrons ā/ē/ī/ō/ū) liefert für „mære" oder
    // „brōt" sonst keine Vorschläge (#167 Finding 86, CONTRACTS §A).
    const needle = TextNormalizer.normalizeMHG(trimmed);
    const lemmata = this.authorityData?.lemmata || [];
    const startsWith = [];
    const includes = [];
    // Voll-Scan (43k) ohne Early-Break, sonst springen kurze Treffer wie „êre"
    // unter längere wie „êrengir" weil das Lemma-Array nicht ID-sortiert ist.
    // 43k Iterationen sind ~3-5ms — pro Keystroke akzeptabel.
    for (const l of lemmata) {
      if (!l.normalized) continue;
      const ln = l.normalized;
      if (ln.startsWith(needle)) startsWith.push(l);
      else if (ln.includes(needle)) includes.push(l);
    }
    // Sortierung: exakt-match → kürzere Lemmata → alphabetisch. So steht
    // „êre" über „êrengir" und „minne" über „minnesänger".
    const sortByRelevance = (a, b) => {
      const an = a.normalized;
      const bn = b.normalized;
      const aExact = an === needle ? 0 : 1;
      const bExact = bn === needle ? 0 : 1;
      if (aExact !== bExact) return aExact - bExact;
      if (an.length !== bn.length) return an.length - bn.length;
      return an.localeCompare(bn, 'de');
    };
    startsWith.sort(sortByRelevance);
    includes.sort(sortByRelevance);
    return [...startsWith, ...includes].slice(0, maxSuggestions);
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

}
