/**
 * MHDBDB Playground - Name Explorer
 * Handles name browsing with concept connections
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
  formatMetadata,
  SearchPatterns,
} from "../search/SearchHelpers.js";

import { displayResults } from "../core/ui-helpers.js";

export class NameExplorer {
  constructor(authorityData) {
    this.authorityData = authorityData;
  }

  showNames() {
    if (this.authorityData.names.length > 50) {
      this.showNamesWithSearch();
    } else {
      this.showAllNames();
    }
  }

  showAllNames() {
    const results = this.authorityData.names.map((n) => ({
      meta: `ID: ${n.id}`,
      snippet: n.termDE || n.termEN,
    }));

    displayResults("Alle Namen aus Authority Files", results);
  }

  showNamesWithSearch() {
    const searchHTML = createSearchInterface({
      title: "Namen-Explorer",
      placeholder: "Name suchen (z.B. Universum, PhilosophInnen)",
      searchInputId: "nameSearch",
      resultsId: "nameResults",
      totalCount: this.authorityData.names.length,
    });

    renderToContainer("resultsContainer", searchHTML);
    setupSearchInput("nameSearch", (term) => this.searchNames(term));
  }

  searchNames(searchTerm) {
    if (!searchTerm.trim()) {
      showEmptySearchState("nameResults");
      return;
    }

    const matches = SearchPatterns.multiFieldNormalized(
      this.authorityData.names,
      searchTerm,
      [(name) => name.termDE || "", (name) => name.termEN || ""]
    );

    const result = handleSearchResults(searchTerm, matches, {
      maxResults: 30,
      emptyMessage: 'Keine Namen gefunden für "{term}"',
    });

    if (typeof result === "string") {
      renderToContainer("nameResults", result);
      return;
    }

    const resultHTML = result.matches
      .map((name) => {
        const conceptConnections = this.findConceptsForName(name.id);

        return generateResultItem({
          meta: formatMetadata([
            `ID: ${name.id}`,
            conceptConnections.length > 0
              ? `${conceptConnections.length} Begriffe`
              : null,
          ]),
          title: name.termDE || name.termEN,
          buttons:
            conceptConnections.length > 0
              ? [
                  {
                    text: "Begriffe anzeigen",
                    action: `window.playground.ui.authorityExplorers.showConceptsForName('${
                      name.id
                    }', '${escapeForJS(name.termDE || name.termEN)}')`,
                  },
                ]
              : [],
          detailsId: `name-details-${name.id}`,
        });
      })
      .join("");

    renderToContainer("nameResults", result.headerHTML + resultHTML);
  }

  showConceptsForName(nameId, nameText) {
    toggleDetails(`name-details-${nameId}`, () => {
      const concepts = this.findConceptsForName(nameId);

      if (concepts.length === 0) {
        return "Keine Begriffsverbindungen für diesen Namen gefunden.";
      }

      // Render each related concept as a clickable card that expands to its
      // lemmata, reusing the concept-explorer's showLemmasWithConcept (which
      // toggles a `lemmas-<conceptId>` container). Same pattern as the concept
      // explorer, so the navigation Name -> Begriff -> Lemmata works. See #120.
      const conceptsHTML = concepts
        .slice(0, 10)
        .map((concept) =>
          generateResultItem({
            meta: `ID: ${concept.id}`,
            title: concept.termDE || concept.termEN,
            buttons: [
              {
                text: "Lemmata anzeigen",
                action: `window.playground.ui.authorityExplorers.showLemmasWithConcept('${
                  concept.id
                }', '${escapeForJS(concept.termDE || concept.termEN)}')`,
              },
            ],
            detailsId: `lemmas-${concept.id}`,
          })
        )
        .join("");

      return `
            <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">
                ${concepts.length} verwandte Begriffe zu "${nameText}"${
        concepts.length > 10 ? " (erste 10)" : ""
      }:
            </div>
            ${conceptsHTML}
        `;
    });
  }

  findConceptsForName(nameId) {
    const name = this.authorityData.names.find((n) => n.id === nameId);

    if (!name || !name.conceptIds) return [];

    const relatedConcepts = name.conceptIds
      .map((conceptId) => {
        return this.authorityData.concepts.find((c) => c.id === conceptId);
      })
      .filter(Boolean);

    return relatedConcepts;
  }
}
