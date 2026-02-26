/**
 * MHDBDB Playground - Work Explorer
 * Handles work browsing and search with detailed metadata
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

export class WorkExplorer {
  constructor(authorityData) {
    this.authorityData = authorityData;
  }

  showWorks() {
    this.showWorksWithSearch();
  }

  showWorksWithSearch() {
    const searchHTML = createSearchInterface({
      title: "Werke-Explorer",
      placeholder:
        "Werk suchen (Titel, Autor*in, Sigle) - z.B. Iwein, Hartmann, PT",
      searchInputId: "workSearch",
      resultsId: "workResults",
      totalCount: this.authorityData.works.length,
    });

    renderToContainer("resultsContainer", searchHTML);
    setupSearchInput("workSearch", (term) => this.searchWorks(term));
  }

  searchWorks(searchTerm) {
    if (!searchTerm.trim()) {
      showEmptySearchState("workResults");
      return;
    }

    const matches = SearchPatterns.multiFieldNormalized(
      this.authorityData.works,
      searchTerm,
      [
        (work) => work.title,
        (work) => work.author || "",
        (work) => work.sigle || "",
      ]
    );

    const result = handleSearchResults(searchTerm, matches, {
      maxResults: 50,
      emptyMessage: 'Keine Werke gefunden für "{term}"',
    });

    if (typeof result === "string") {
      renderToContainer("workResults", result);
      return;
    }

    const resultHTML = result.matches
      .map((work) => {
        const genre = this.getWorkGenre(work.id);
        const authorName = work.author !== "Unbekannt" ? work.author : null;

        return generateResultItem({
          meta: formatMetadata([
            `ID: ${work.id}`,
            work.sigle ? `Sigle: ${work.sigle}` : null,
            genre ? genre : null,
          ]),
          title: work.title,
          subtitle: formatMetadata([
            genre ? genre : null,
            authorName ? `Autor*in: ${authorName}` : null,
          ]),
          buttons: [
            {
              text: "Details anzeigen",
              action: `window.playground.ui.authorityExplorers.showWorkDetails('${
                work.id
              }', '${escapeForJS(work.title)}')`,
            },
          ],
          detailsId: `details-${work.id}`,
        });
      })
      .join("");

    renderToContainer("workResults", result.headerHTML + resultHTML);
  }

  showWorkDetails(workId, workTitle) {
    toggleDetails(`details-${workId}`, () => {
      const workDetails = this.getWorkDetailsFromXML(workId);
      if (!workDetails) return null;

      let detailsHTML = `
      <div style="font-weight: 500; margin-bottom: 10px; color: #667eea;">
        Details zu "${workTitle}"
      </div>
    `;

      // Multiple titles
      if (workDetails.titles && workDetails.titles.length > 1) {
        const mainTitle =
          workDetails.titles.find((t) => t.lang === "de" && !t.type) ||
          workDetails.titles[0];
        const alternateCount = workDetails.titles.length - 1;

        detailsHTML += `
    <div style="margin-bottom: 8px;">
      <strong>Titel:</strong> ${mainTitle.text}
      <span onclick="window.playground.ui.authorityExplorers.toggleAlternateTitles('${workId}')"
            style="color: #667eea; cursor: pointer; text-decoration: underline;">
        (+ ${alternateCount} weitere)
      </span>
      <div id="alternate-titles-${workId}" style="display: none; margin-top: 8px; padding: 8px; background: rgba(102, 126, 234, 0.05); border-radius: 4px;">
        ${workDetails.titles
          .filter((t) => t !== mainTitle)
          .map((title) => {
            const langLabel = title.lang ? `[${title.lang}]` : "";
            const typeLabel = title.type ? `(${title.type})` : "";
            return `<div style="font-size: 0.85rem; margin-bottom: 3px;">• ${title.text} ${langLabel} ${typeLabel}</div>`;
          })
          .join("")}
      </div>
    </div>
  `;
      }

      // Sigles
      if (workDetails.sigles && workDetails.sigles.length > 0) {
        detailsHTML += `
        <div style="margin-bottom: 8px;">
          <strong>Sigle:</strong> ${workDetails.sigles.join(", ")}
        </div>
      `;
      }

      // Genres with hierarchy
      if (workDetails.genres && workDetails.genres.length > 0) {
        const genreHTML = workDetails.genres
          .map((genre) => {
            let genreText =
              genre.termDE || genre.termEN || genre.text || genre.id;
            if (genre.parent) genreText += ` → ${genre.parent}`;

            return `
            <span style="background: rgba(102, 126, 234, 0.1); padding: 2px 6px; border-radius: 3px; font-size: 0.8rem; margin-right: 5px;">
              ${genreText}
            </span>
          `;
          })
          .join("");

        detailsHTML += `
        <div style="margin-bottom: 8px;">
          <strong>Gattung:</strong><br>
          <div style="margin-top: 3px;">${genreHTML}</div>
        </div>
      `;
      }

      // Author with navigation
      if (workDetails.author) {
        detailsHTML += `
        <div style="margin-bottom: 8px;">
          <strong>Autor*in:</strong> ${workDetails.author}
          <button onclick="window.playground.ui.authorityExplorers.searchAuthorFromWork('${escapeForJS(
            workDetails.author
          )}')"
            style="margin-left: 10px; padding: 2px 6px; background: #28a745; color: white; border: none; border-radius: 3px; font-size: 0.75rem; cursor: pointer;">
            Andere Werke
          </button>
        </div>
      `;
      }

      // GND and Wikidata for the work
      if (workDetails.gnd || workDetails.wikidata) {
        detailsHTML += `
        <div style="margin-bottom: 8px;">
          <strong>Identifikatoren:</strong><br>
        `;
        if (workDetails.gnd) {
          detailsHTML += `
          <a href="https://d-nb.info/gnd/${workDetails.gnd}" target="_blank" style="color: #667eea; margin-right: 10px; text-decoration: none;">
            GND: ${workDetails.gnd} →
          </a>
          `;
        }
        if (workDetails.wikidata) {
          detailsHTML += `
          <a href="https://www.wikidata.org/wiki/${workDetails.wikidata}" target="_blank" style="color: #667eea; text-decoration: none;">
            Wikidata: ${workDetails.wikidata} →
          </a>
          `;
        }
        detailsHTML += `
        </div>
      `;
      }

      // biblStruct sources
      if (workDetails.biblStructs && workDetails.biblStructs.length > 0) {
        detailsHTML += `
        <div style="margin-bottom: 8px;">
          <strong>Bibliographic Sources (${workDetails.biblStructs.length}):</strong><br>
      `;

        workDetails.biblStructs.forEach((biblStruct) => {
          const zoteroIcon = biblStruct.corresp
            ? `<a href="${biblStruct.corresp}" target="_blank" style="color: #667eea; text-decoration: none;">→</a>`
            : "";

          detailsHTML += `
          <div style="margin: 8px 0; padding: 8px; background: rgba(102, 126, 234, 0.05); border-radius: 4px;">
            <strong>${biblStruct.key}:</strong> ${biblStruct.textContent} ${zoteroIcon}
          </div>
        `;
        });

        detailsHTML += `</div>`;
      }

      // Handschriftencensus link
      if (workDetails.handschriftencensus) {
        detailsHTML += `
        <div style="margin-bottom: 8px;">
          <strong>Handschriftencensus:</strong>
          <a href="${workDetails.handschriftencensus}" target="_blank" style="color: #667eea;">
            ${workDetails.handschriftencensus}
          </a>
        </div>
      `;
      }

      return detailsHTML;
    });
  }

  toggleAlternateTitles(workId) {
    const container = document.getElementById(`alternate-titles-${workId}`);
    if (container) {
      container.style.display =
        container.style.display === "none" ? "block" : "none";
    }
  }

  getWorkDetailsFromXML(workId) {
    // Use pre-built index data instead of parsing XML
    const work = this.authorityData.works.find((w) => w.id === workId);

    if (!work) return null;

    const details = {};

    // Titles (already in index)
    details.titles = work.titles || [];

    // Sigles (already in index)
    details.sigles = work.sigles || [];

    // Genres - resolve genre IDs to full genre data
    if (work.genres && work.genres.length > 0) {
      details.genres = work.genres.map((genreRef) => {
        const genre = this.authorityData.genres.find((g) => g.id === genreRef.id);
        return {
          id: genreRef.id,
          termDE: genre ? genre.termDE : null,
          termEN: genre ? genre.termEN : null,
          text: genreRef.text,
        };
      });
    }

    // Author (already in index)
    details.author = work.author;

    // GND and Wikidata (from authority index v1.1.0+)
    details.gnd = work.gnd || null;
    details.wikidata = work.wikidata || null;

    // biblStructs (already in index)
    details.biblStructs = work.biblStructs || [];

    // Handschriftencensus (already in index)
    details.handschriftencensus = work.handschriftencensus;

    return details;
  }

  getWorkGenre(workId) {
    const workDetails = this.getWorkDetailsFromXML(workId);
    if (workDetails && workDetails.genres && workDetails.genres.length > 0) {
      return workDetails.genres[0].termDE || workDetails.genres[0].termEN;
    }
    return null;
  }
}
