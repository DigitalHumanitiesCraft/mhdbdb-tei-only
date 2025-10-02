/**
 * MHDBDB Playground - Genre Explorer
 * Handles genre browsing with work and author connections
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

export class GenreExplorer {
  constructor(authorityData) {
    this.authorityData = authorityData;
  }

  showGenres() {
    if (this.authorityData.genres.length > 30) {
      this.showGenresWithSearch();
    } else {
      this.showAllGenres();
    }
  }

  showAllGenres() {
    const results = this.authorityData.genres.map((g) => ({
      meta: `ID: ${g.id}`,
      snippet: g.termDE || g.termEN,
    }));

    displayResults("Alle Gattungen aus Authority Files", results);
  }

  showGenresWithSearch() {
    const searchHTML = createSearchInterface({
      title: "Gattungen-Explorer",
      placeholder: "Gattung suchen (z.B. Höfischer Roman, Epik, Lyrik)",
      searchInputId: "genreSearch",
      resultsId: "genreResults",
      totalCount: this.authorityData.genres.length,
    });

    renderToContainer("resultsContainer", searchHTML);
    setupSearchInput("genreSearch", (term) => this.searchGenres(term));
  }

  searchGenres(searchTerm) {
    if (!searchTerm.trim()) {
      showEmptySearchState("genreResults");
      return;
    }

    const matches = SearchPatterns.multiFieldNormalized(
      this.authorityData.genres,
      searchTerm,
      [(genre) => genre.termDE || "", (genre) => genre.termEN || ""]
    );

    const result = handleSearchResults(searchTerm, matches, {
      maxResults: 30,
      emptyMessage: 'Keine Gattungen gefunden für "{term}"',
    });

    if (typeof result === "string") {
      renderToContainer("genreResults", result);
      return;
    }

    const resultHTML = result.matches
      .map((genre) => {
        const worksInGenre = this.findWorksInGenre(genre.id);
        const parentGenre = this.getGenreHierarchy(genre.id);

        return generateResultItem({
          meta: formatMetadata([
            `ID: ${genre.id}`,
            worksInGenre.length > 0 ? `${worksInGenre.length} Werke` : null,
            parentGenre ? `Übergeordnet: ${parentGenre}` : null,
          ]),
          title: genre.termDE || genre.termEN,
          buttons:
            worksInGenre.length > 0
              ? [
                  {
                    text: "Werke anzeigen",
                    action: `window.playground.ui.authorityExplorers.showWorksInGenre('${
                      genre.id
                    }', '${escapeForJS(genre.termDE || genre.termEN)}')`,
                  },
                  {
                    text: "Autoren anzeigen",
                    action: `window.playground.ui.authorityExplorers.showAuthorsInGenre('${
                      genre.id
                    }', '${escapeForJS(genre.termDE || genre.termEN)}')`,
                  },
                ]
              : [],
          detailsId: `genre-details-${genre.id}`,
        });
      })
      .join("");

    renderToContainer("genreResults", result.headerHTML + resultHTML);
  }

  showWorksInGenre(genreId, genreName) {
    toggleDetails(`genre-details-${genreId}`, () => {
      const worksInGenre = this.findWorksInGenre(genreId);

      if (worksInGenre.length === 0) {
        return "Keine Werke in dieser Gattung gefunden.";
      }

      const worksHTML = worksInGenre
        .slice(0, 20)
        .map(
          (work) => `
            <div style="margin-bottom: 3px; font-size: 0.85rem;">
                • <strong>${work.title}</strong>${
            work.sigle ? ` (${work.sigle})` : ""
          }
                <span style="color: #666;">von ${work.author}</span>
            </div>
        `
        )
        .join("");

      return `
            <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">
                ${worksInGenre.length} Werke in "${genreName}"${
        worksInGenre.length > 20 ? " (erste 20)" : ""
      }:
            </div>
            ${worksHTML}
        `;
    });
  }

  showAuthorsInGenre(genreId, genreName) {
    const worksInGenre = this.findWorksInGenre(genreId);
    const authorsInGenre = [...new Set(worksInGenre.map((w) => w.author))];

    toggleDetails(`genre-details-${genreId}`, () => {
      if (authorsInGenre.length === 0) {
        return "Keine Autoren in dieser Gattung gefunden.";
      }

      const authorsHTML = authorsInGenre
        .slice(0, 15)
        .map((author) => {
          const worksCount = worksInGenre.filter(
            (w) => w.author === author
          ).length;
          return `
                <div style="margin-bottom: 3px; font-size: 0.85rem;">
                    • <strong>${author}</strong> (${worksCount} ${
            worksCount === 1 ? "Werk" : "Werke"
          })
                </div>
            `;
        })
        .join("");

      return `
            <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">
                ${authorsInGenre.length} Autoren in "${genreName}"${
        authorsInGenre.length > 15 ? " (erste 15)" : ""
      }:
            </div>
            ${authorsHTML}
        `;
    });
  }

  findWorksInGenre(genreId) {
    const workIds =
      window.playground.authorityManager.indexes.genreToWorks.get(genreId) ||
      [];

    return workIds
      .map((workId) => this.authorityData.works.find((w) => w.id === workId))
      .filter(Boolean);
  }

  getGenreHierarchy(genreId) {
    const hierarchyArray =
      window.playground.authorityManager.indexes.genreHierarchy.get(genreId);
    if (!hierarchyArray || hierarchyArray.length === 0) return null;

    return hierarchyArray.join(" UND ");
  }
}
