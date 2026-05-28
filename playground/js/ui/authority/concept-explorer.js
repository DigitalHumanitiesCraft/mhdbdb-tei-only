/**
 * MHDBDB Playground - Concept Explorer
 * Handles concept browsing and search with lemma connections
 */

import {
  createSearchInterface,
  handleSearchResults,
  generateResultItem,
  setupSearchInput,
  toggleDetails,
  showEmptySearchState,
  renderToContainer,
  escapeForJS,
  formatMultiLanguage,
  formatMetadata,
  SearchPatterns,
} from "../search/SearchHelpers.js";
import { TextNormalizer } from "../../../../assets/js/lib/text-normalizer.js";

import { displayResults } from "../core/ui-helpers.js";

export class ConceptExplorer {
  constructor(authorityData) {
    this.authorityData = authorityData;
  }

  showConcepts() {
    if (this.authorityData.concepts.length > 50) {
      this.showConceptsWithSearch();
    } else {
      this.showAllConcepts();
    }
  }

  showAllConcepts() {
    const results = this.authorityData.concepts.map((c) => ({
      meta: `ID: ${c.id}`,
      snippet: formatMultiLanguage(c.termDE, c.termEN),
    }));

    displayResults("Alle Begriffe aus Authority Files", results);
  }

  showConceptsWithSearch() {
    const searchHTML = createSearchInterface({
      title: "Begriffe-Explorer",
      placeholder: "Begriff suchen (z.B. Freundschaft, Liebe, Ehre)",
      searchInputId: "conceptSearch",
      resultsId: "conceptResults",
      totalCount: this.authorityData.concepts.length,
    });

    renderToContainer("resultsContainer", searchHTML);
    setupSearchInput("conceptSearch", (term) => this.searchConcepts(term));
  }

  searchConcepts(searchTerm) {
    if (!searchTerm.trim()) {
      showEmptySearchState("conceptResults");
      return;
    }

    const matches = SearchPatterns.multiFieldNormalized(
      this.authorityData.concepts,
      searchTerm,
      [
        (concept) => concept.termDE || "",
        (concept) => concept.termEN || "",
        (concept) => (concept.altDE || []).join(" "),
        (concept) => (concept.altEN || []).join(" "),
      ]
    );

    const result = handleSearchResults(searchTerm, matches, {
      maxResults: 50,
      emptyMessage: 'Keine Begriffe gefunden für "{term}"',
    });

    if (typeof result === "string") {
      renderToContainer("conceptResults", result);
      return;
    }

    const resultHTML = result.matches
      .map((concept) => {
        const altHint = findAlternativeMatch(concept, searchTerm);
        const subtitle = altHint ? `auch: ${altHint}` : "";
        return generateResultItem({
          meta: `ID: ${concept.id}`,
          title: formatMultiLanguage(concept.termDE, concept.termEN),
          subtitle,
          buttons: [
            {
              text: "Lemmata anzeigen",
              action: `window.playground.ui.authorityExplorers.showLemmasWithConcept('${
                concept.id
              }', '${escapeForJS(
                formatMultiLanguage(concept.termDE, concept.termEN)
              )}')`,
            },
          ],
          detailsId: `lemmas-${concept.id}`,
        });
      })
      .join("");

    renderToContainer("conceptResults", result.headerHTML + resultHTML);
  }

  showLemmasWithConcept(conceptId, conceptName) {
    toggleDetails(`lemmas-${conceptId}`, () => {
      const lemmasWithConcept = this.findLemmasWithConcept(conceptId);

      if (lemmasWithConcept.length === 0) {
        return "Keine Lemmata für diesen Begriff gefunden.";
      }

      // Create full search interface for exploring lemmata
      const searchId = `lemma-concept-search-${conceptId}`;
      const resultsId = `lemma-concept-results-${conceptId}`;

      const searchHTML = createSearchInterface({
        title: `${lemmasWithConcept.length} Lemmata mit Begriff "${conceptName}"`,
        placeholder: "Lemma filtern (z.B. vriunt, minne, ere)",
        searchInputId: searchId,
        resultsId: resultsId,
        totalCount: lemmasWithConcept.length,
      });

      // Set up search after rendering
      setTimeout(() => {
        setupSearchInput(searchId, (term) =>
          this.searchLemmasInConcept(term, lemmasWithConcept, resultsId)
        );
        // Show all results initially
        this.searchLemmasInConcept("", lemmasWithConcept, resultsId);
      }, 0);

      return searchHTML;
    });
  }

  searchLemmasInConcept(searchTerm, lemmasWithConcept, resultsId) {
    // Filter lemmata by search term if provided
    const matches = searchTerm.trim()
      ? SearchPatterns.textContainsNormalized(
          lemmasWithConcept,
          searchTerm,
          (lemma) => lemma.lemma
        )
      : lemmasWithConcept;

    // Sort alphabetically
    const sortedMatches = matches.sort((a, b) =>
      (a.lemma || '').localeCompare(b.lemma || '', 'de')
    );

    // Limit to first 20
    const displayMatches = sortedMatches.slice(0, 20);

    if (displayMatches.length === 0) {
      renderToContainer(resultsId, `<p class="text-gray-500">Keine Lemmata gefunden${searchTerm ? ` für "${searchTerm}"` : ''}.</p>`);
      return;
    }

    // Simple list of clickable lemmas
    const resultHTML = `
      <div style="margin-bottom: 10px; color: #475569;">
        ${displayMatches.length} Treffer${sortedMatches.length > 20 ? ' (erste 20 angezeigt)' : ''}
      </div>
      <div style="display: flex; flex-direction: column; gap: 8px;">
        ${displayMatches.map(lemma => `
          <div style="padding: 8px; background: white; border-radius: 4px; border: 1px solid #e5e7eb;">
            <a href="javascript:void(0)"
               onclick="window.playground.ui.authorityExplorers.lemmaExplorer.showLemmaDetails('${lemma.id}', '${escapeForJS(lemma.lemma)}')"
               style="color: #1f2937; text-decoration: none; cursor: pointer; font-size: 1rem; display: flex; align-items: center; gap: 6px;"
               title="Details im Lemma-Explorer anzeigen">
              <span>${lemma.lemma}</span>
              <span style="color: #667eea; font-size: 0.85rem;">→</span>
            </a>
          </div>
        `).join('')}
      </div>
    `;

    renderToContainer(resultsId, resultHTML);
  }

  findLemmasWithConcept(conceptId) {
    const lemmaIds =
      window.playground.authorityManager.indexes.conceptToLemmas.get(
        conceptId
      ) || [];

    return lemmaIds
      .map((lemmaId) =>
        this.authorityData.lemmata.find((l) => l.id === lemmaId)
      )
      .filter(Boolean);
  }
}

/**
 * If the search term matched the concept only via an alternative term
 * (i.e. the primary termDE/termEN does not contain it, but one of the
 * altDE/altEN does), return the first matching alternative for display
 * as "auch: …" hint. Otherwise return null.
 */
function findAlternativeMatch(concept, searchTerm) {
  const primaryMatch =
    TextNormalizer.matchesNormalized(concept.termDE || "", searchTerm) ||
    TextNormalizer.matchesNormalized(concept.termEN || "", searchTerm);
  if (primaryMatch) return null;

  const altCandidates = [...(concept.altDE || []), ...(concept.altEN || [])];
  for (const alt of altCandidates) {
    if (TextNormalizer.matchesNormalized(alt, searchTerm)) {
      return alt;
    }
  }
  return null;
}
