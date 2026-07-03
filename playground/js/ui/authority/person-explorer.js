/**
 * MHDBDB Playground - Person/Author Explorer
 * Handles author/person browsing and search
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

export class PersonExplorer {
  constructor(authorityData) {
    this.authorityData = authorityData;
  }

  showAuthors() {
    if (this.authorityData.persons.length > 50) {
      this.showAuthorsWithSearch();
    } else {
      this.showAllAuthors();
    }
  }

  showAllAuthors() {
    const results = this.authorityData.persons.map((p) => ({
      meta: formatMetadata([
        `ID: ${p.id}`,
        p.works ? `${p.works.split(",").length} Werke` : null,
        p.gnd ? `GND: ${p.gnd}` : null,
      ]),
      snippet: p.preferredName,
    }));

    displayResults("Alle Autor*innen aus Authority Files", results);
  }

  showAuthorsWithSearch() {
    const searchHTML = createSearchInterface({
      title: "Autor*innen-Explorer",
      placeholder: "Autor*in eingeben (z.B. Hartmann, Wolfram, Walther)",
      searchInputId: "authorSearch",
      resultsId: "authorResults",
      totalCount: this.authorityData.persons.length,
    });

    renderToContainer("resultsContainer", searchHTML);
    setupSearchInput("authorSearch", (term) => this.searchAuthors(term));
  }

  searchAuthorFromWork(authorName) {
    this.showAuthorsWithSearch();
    setTimeout(() => {
      const searchInput = document.getElementById("authorSearch");
      if (searchInput) {
        searchInput.value = authorName;
        this.searchAuthors(authorName);
      }
    }, 100);
  }

  searchAuthors(searchTerm) {
    if (!searchTerm.trim()) {
      showEmptySearchState("authorResults");
      return;
    }

    const matches = SearchPatterns.textContainsNormalized(
      this.authorityData.persons,
      searchTerm,
      (person) => person.preferredName
    );

    const result = handleSearchResults(searchTerm, matches, {
      maxResults: 30,
      emptyMessage: 'Keine Autor*innen gefunden für "{term}"',
    });

    if (typeof result === "string") {
      renderToContainer("authorResults", result);
      return;
    }

    const resultHTML = result.matches
      .map((author) => {
        const workCount = author.works ? author.works.split(",").length : 0;

        return generateResultItem({
          meta: formatMetadata([
            `ID: ${author.id}`,
            // #135: GND/Wikidata als externe Links (neuer Tab). IDs sind im
            // Authority-Index reine Bezeichner (kein URL-Präfix), siehe persons.xml.
            author.gnd
              ? `GND: <a href="https://d-nb.info/gnd/${author.gnd}" target="_blank" rel="noopener" class="underline hover:text-brand-900">${author.gnd}</a>`
              : null,
            author.wikidata
              ? `Wikidata: <a href="https://www.wikidata.org/wiki/${author.wikidata}" target="_blank" rel="noopener" class="underline hover:text-brand-900">${author.wikidata}</a>`
              : null,
            workCount > 0 ? `${workCount} Werke` : null,
          ]),
          title: author.preferredName,
          buttons:
            workCount > 0
              ? [
                  {
                    text: "Werke anzeigen",
                    action: `window.playground.ui.authorityExplorers.showWorksByAuthor('${
                      author.id
                    }', '${escapeForJS(author.preferredName)}')`,
                  },
                ]
              : [],
          detailsId: `works-${author.id}`,
        });
      })
      .join("");

    renderToContainer("authorResults", result.headerHTML + resultHTML);
  }

  showWorksByAuthor(authorId, authorName) {
    toggleDetails(`works-${authorId}`, () => {
      const author = this.authorityData.persons.find((p) => p.id === authorId);
      if (!author || !author.works) return null;

      const workIds = author.works.split(",").map((id) => id.trim());
      const authorWorks = workIds
        .map((workId) => this.authorityData.works.find((w) => w.id === workId))
        .filter(Boolean);

      if (authorWorks.length === 0) return null;

      const worksHTML = authorWorks
        .slice(0, 20)
        .map((work) => {
          // #135: Werk-Titel als Deep-Link in die Lesesuche, sofern eine Sigle
          // existiert (= TEI-Text vorhanden). Ohne Sigle kein Link (kein toter Link).
          // Werke mit mehreren Textzeugen tragen sigle als Komma-String
          // ("AXH, AXU"); der Reader adressiert genau EINEN Text, daher die erste
          // Einzelsigle nehmen (sigles-Array bevorzugt), nie den Komma-String.
          const sigle = (work.sigles && work.sigles[0])
            || (work.sigle ? work.sigle.split(",")[0].trim() : null)
            || null;
          const titleHTML = sigle
            ? `<a href="../korpus.html?textId=${encodeURIComponent(sigle)}" target="_blank" rel="noopener" class="text-brand-700 hover:text-brand-900 hover:underline"><strong>${work.title}</strong></a>`
            : `<strong>${work.title}</strong>`;
          return `
                <div style="margin-bottom: 3px; font-size: 0.85rem;">
                    • ${titleHTML}${sigle ? ` (${sigle})` : ""}
                </div>
            `;
        })
        .join("");

      return `
                <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">
                    ${authorWorks.length} Werke von "${authorName}"${
        authorWorks.length > 20 ? " (erste 20)" : ""
      }:
                </div>
                ${worksHTML}
            `;
    });
  }
}
