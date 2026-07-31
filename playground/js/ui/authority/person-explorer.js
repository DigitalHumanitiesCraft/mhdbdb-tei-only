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
} from "../search/SearchHelpers.js";
import { TextNormalizer } from "../../../../assets/js/lib/text-normalizer.js";

import { displayResults } from "../core/ui-helpers.js";

// Self-contained per module (DESIGN.md §Escaping-Konvention). generateResultItem
// inserts the subtitle raw, because meta/title carry markup (GND links).
function escapeHtml(s) {
  if (s == null) return "";
  return String(s).replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

/**
 * If the search term matched the person only via an alternative name form
 * (#307), return that form for display as an "auch: …" hint. Returns null when
 * the preferred name already matches, so a hint only ever appears where the
 * match would otherwise look like an error.
 *
 * Matching runs against the precomputed `altNormalized`, whose entries are
 * index-parallel to `altNames` (see build-authority-index.py). `altNames` is
 * absent for 131 of 211 persons and for every index built before 1.8.0; both
 * cases leave through the length check below.
 *
 * The live-normalization fallback is pure defence against a broken contract: it
 * can only fire when `altNames` exists while `altNormalized` is missing or
 * shorter, which the build cannot produce and the index test in
 * playground-authority-index.spec.js catches. It is here so that such an index
 * degrades to a slower match instead of a TypeError.
 */
function findAlternativeMatch(person, searchTerm) {
  if (TextNormalizer.matchesNormalized(person.preferredName || "", searchTerm)) {
    return null;
  }
  const altNames = person.altNames || [];
  if (!altNames.length) return null;

  const needle = TextNormalizer.normalizeMHG(searchTerm);
  if (!needle) return null;

  const altNormalized = person.altNormalized;
  for (let i = 0; i < altNames.length; i++) {
    const normalized =
      altNormalized && altNormalized[i] !== undefined
        ? altNormalized[i]
        : TextNormalizer.normalizeMHG(altNames[i]);
    if (normalized.includes(needle)) return altNames[i];
  }
  return null;
}

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

    // #307: alternative name forms search alongside the preferred one. Each form
    // is tested on its own instead of joining them into one haystack, so a term
    // cannot match across the boundary between two forms.
    const matches = this.authorityData.persons.filter(
      (person) =>
        TextNormalizer.matchesNormalized(person.preferredName || "", searchTerm) ||
        findAlternativeMatch(person, searchTerm) !== null
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
        const altHint = findAlternativeMatch(author, searchTerm);

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
          subtitle: altHint ? `auch: ${escapeHtml(altHint)}` : "",
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
