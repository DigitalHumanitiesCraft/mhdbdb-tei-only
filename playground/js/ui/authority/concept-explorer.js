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
  SearchPatterns,
} from "../search/SearchHelpers.js";

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

    displayResults("Alle Konzepte aus Authority Files", results);
  }

  showConceptsWithSearch() {
    const searchHTML = createSearchInterface({
      title: "Konzepte-Explorer",
      placeholder: "Konzept suchen (z.B. Freundschaft, Liebe, Ehre)",
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
      [(concept) => concept.termDE || "", (concept) => concept.termEN || ""]
    );

    const result = handleSearchResults(searchTerm, matches, {
      maxResults: 50,
      emptyMessage: 'Keine Konzepte gefunden für "{term}"',
    });

    if (typeof result === "string") {
      renderToContainer("conceptResults", result);
      return;
    }

    const resultHTML = result.matches
      .map((concept) =>
        generateResultItem({
          meta: `ID: ${concept.id}`,
          title: formatMultiLanguage(concept.termDE, concept.termEN),
          buttons: [
            {
              text: "Lemmata zeigen",
              action: `window.playground.ui.authorityExplorers.showLemmasWithConcept('${
                concept.id
              }', '${escapeForJS(
                formatMultiLanguage(concept.termDE, concept.termEN)
              )}')`,
            },
          ],
          detailsId: `lemmas-${concept.id}`,
        })
      )
      .join("");

    renderToContainer("conceptResults", result.headerHTML + resultHTML);
  }

  showLemmasWithConcept(conceptId, conceptName) {
    toggleDetails(`lemmas-${conceptId}`, () => {
      const lemmasWithConcept = this.findLemmasWithConcept(conceptId);

      if (lemmasWithConcept.length === 0) {
        return "Keine Lemmata für dieses Konzept gefunden.";
      }

      const lemmasHTML = lemmasWithConcept
        .slice(0, 20)
        .map(
          (lemma) => `
            <div style="margin-bottom: 3px; font-size: 0.85rem;">
                • <strong>${lemma.lemma}</strong>${
            lemma.pos ? ` (${lemma.pos})` : ""
          }
            </div>
        `
        )
        .join("");

      return `
            <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">
                ${
                  lemmasWithConcept.length
                } Lemmata mit Konzept "${conceptName}"${
        lemmasWithConcept.length > 20 ? " (erste 20)" : ""
      }:
            </div>
            ${lemmasHTML}
        `;
    });
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
