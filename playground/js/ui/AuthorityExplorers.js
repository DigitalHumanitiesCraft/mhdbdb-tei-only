/**
 * MHDBDB Playground - Authority Files Explorers
 * Handles all authority file exploration: Authors, Works, Lemmata, Concepts, Genres, Names
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
  formatMultiLanguage,
  SearchPatterns,
} from "./SearchHelpers.js";

import { displayResults } from "./UICore.js";

export class AuthorityExplorers {
  constructor(authorityData) {
    this.authorityData = authorityData;
  }

  // ==================== AUTHORS EXPLORER ====================

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

    displayResults("👥 Alle Autoren aus Authority Files", results);
  }

  showAuthorsWithSearch() {
    const searchHTML = createSearchInterface({
      title: "👥 Autoren-Explorer",
      placeholder: "Autor eingeben (z.B. Hartmann, Wolfram, Walther)",
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

    const matches = SearchPatterns.textContains(
      this.authorityData.persons,
      searchTerm,
      (person) => person.preferredName
    );

    const result = handleSearchResults(searchTerm, matches, {
      maxResults: 30,
      emptyMessage: 'Keine Autoren gefunden für "{term}"',
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
            author.gnd ? `GND: ${author.gnd}` : null,
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
        .map(
          (work) => `
                <div style="margin-bottom: 3px; font-size: 0.85rem;">
                    • <strong>${work.title}</strong>${
            work.sigle ? ` (${work.sigle})` : ""
          }
                </div>
            `
        )
        .join("");

      return `
                <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">
                    📚 ${authorWorks.length} Werke von "${authorName}"${
        authorWorks.length > 20 ? " (erste 20)" : ""
      }:
                </div>
                ${worksHTML}
            `;
    });
  }

  // ==================== WORKS EXPLORER ====================

  showWorks() {
    this.showWorksWithSearch();
  }

  showWorksWithSearch() {
    const searchHTML = createSearchInterface({
      title: "📚 Werke-Explorer",
      placeholder:
        "Werk suchen (Titel, Autor, Sigle) - z.B. Iwein, Hartmann, PT",
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

    const matches = SearchPatterns.multiField(
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
            genre ? `🎭 ${genre}` : null,
            authorName ? `👤 ${authorName}` : null,
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
                    📖 Details zu "${workTitle}"
                </div>
            `;

      // Sigles
      if (workDetails.sigles && workDetails.sigles.length > 0) {
        detailsHTML += `
                    <div style="margin-bottom: 8px;">
                        <strong>🏷️ Sigle:</strong> ${workDetails.sigles.join(
                          ", "
                        )}
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
                        <strong>🎭 Gattung:</strong><br>
                        <div style="margin-top: 3px;">${genreHTML}</div>
                    </div>
                `;
      }

      // Author with navigation
      if (workDetails.author) {
        detailsHTML += `
                    <div style="margin-bottom: 8px;">
                        <strong>👤 Autor:</strong> ${workDetails.author}
                        <button onclick="window.playground.ui.authorityExplorers.searchAuthorFromWork('${escapeForJS(
                          workDetails.author
                        )}')"
                                style="margin-left: 10px; padding: 2px 6px; background: #28a745; color: white; border: none; border-radius: 3px; font-size: 0.75rem; cursor: pointer;">
                            Andere Werke
                        </button>
                    </div>
                `;
      }

      // Edition info
      if (workDetails.edition) {
        detailsHTML += `
                    <div style="margin-bottom: 8px;">
                        <strong>📅 Edition:</strong> ${
                          workDetails.edition.title || workTitle
                        }<br>
                        <span style="font-size: 0.85rem; color: #666;">
                            ${formatMetadata(
                              [
                                workDetails.edition.pubPlace,
                                workDetails.edition.publisher,
                                workDetails.edition.date,
                              ],
                              ": "
                            )}
                        </span>
                    </div>
                `;
      }

      return detailsHTML;
    });
  }

  getWorkDetailsFromXML(workId) {
    const worksXML = this.authorityData.parsedXML.find((xml) =>
      xml.filename.includes("works")
    );

    if (!worksXML) return null;

    const workElement = Array.from(worksXML.doc.querySelectorAll("bibl")).find(
      (bibl) => bibl.getAttribute("xml:id") === workId
    );

    if (!workElement) return null;

    const details = {};

    // Extract sigles
    const sigleElements = workElement.querySelectorAll('idno[type="sigle"]');
    details.sigles = Array.from(sigleElements)
      .map((s) => s.textContent?.trim())
      .filter(Boolean);

    // Extract genres with hierarchy
    const genreRefs = workElement.querySelectorAll(
      'ref[target*="genres.xml#"]'
    );
    details.genres = Array.from(genreRefs)
      .filter((ref) => ref.getAttribute("xml:lang") === "de")
      .map((ref) => {
        const target = ref.getAttribute("target");
        const genreId = target.split("#")[1];
        const genre = this.authorityData.genres.find((g) => g.id === genreId);
        return {
          id: genreId,
          termDE: genre ? genre.termDE : null,
          termEN: genre ? genre.termEN : null,
          text: ref.textContent?.trim(),
        };
      });

    // Extract author
    const authorElement = workElement.querySelector("author");
    if (authorElement) {
      details.author = authorElement.textContent?.trim();
    }

    // Extract edition
    const editionElement = workElement.querySelector('bibl[type="edition"]');
    if (editionElement) {
      details.edition = {
        title: editionElement.querySelector("title")?.textContent?.trim(),
        pubPlace: editionElement.querySelector("pubPlace")?.textContent?.trim(),
        publisher: editionElement
          .querySelector("publisher")
          ?.textContent?.trim(),
        date: editionElement.querySelector("date")?.textContent?.trim(),
      };
    }

    return details;
  }

  getWorkGenre(workId) {
    const workDetails = this.getWorkDetailsFromXML(workId);
    if (workDetails && workDetails.genres && workDetails.genres.length > 0) {
      return workDetails.genres[0].termDE || workDetails.genres[0].termEN;
    }
    return null;
  }

  // ==================== LEMMATA EXPLORER ====================

  showLemmata() {
    if (this.authorityData.lemmata.length > 500) {
      this.showLemmataWithSearch();
    } else {
      this.showAllLemmata();
    }
  }

  showAllLemmata() {
    const displayCount = Math.min(100, this.authorityData.lemmata.length);
    const results = this.authorityData.lemmata
      .slice(0, displayCount)
      .map((l) => ({
        meta: formatMetadata([
          `ID: ${l.id}`,
          l.pos ? `POS: ${l.pos}` : null,
          l.senseCount ? `${l.senseCount} Bedeutungen` : null,
        ]),
        snippet: l.lemma,
      }));

    displayResults(
      `🔤 Lemmata aus Authority Files (erste ${displayCount} von ${this.authorityData.lemmata.length})`,
      results
    );
  }

  showLemmataWithSearch() {
    const searchHTML = createSearchInterface({
      title: "🔤 Lemmata-Suche",
      placeholder: "Lemma eingeben (z.B. vriunt, minne, ere)",
      searchInputId: "lemmaSearch",
      resultsId: "lemmaResults",
      totalCount: this.authorityData.lemmata.length,
    });

    renderToContainer("resultsContainer", searchHTML);
    setupSearchInput("lemmaSearch", (term) => this.searchLemmata(term));
  }

  searchLemmata(searchTerm) {
    if (!searchTerm.trim()) {
      showEmptySearchState("lemmaResults");
      return;
    }

    const matches = SearchPatterns.textContains(
      this.authorityData.lemmata,
      searchTerm,
      (lemma) => lemma.lemma
    );

    const result = handleSearchResults(searchTerm, matches, {
      maxResults: 50,
      emptyMessage: 'Keine Lemmata gefunden für "{term}"',
    });

    if (typeof result === "string") {
      renderToContainer("lemmaResults", result);
      return;
    }

    const resultHTML = result.matches
      .map((lemma) =>
        generateResultItem({
          meta: formatMetadata([
            `ID: ${lemma.id}`,
            lemma.pos ? `POS: ${lemma.pos}` : null,
            lemma.senseCount ? `${lemma.senseCount} Bedeutungen` : null,
          ]),
          title: lemma.lemma,
          buttons:
            lemma.senseCount > 0
              ? [
                  {
                    text: "Bedeutungen anzeigen",
                    action: `window.playground.ui.authorityExplorers.showLemmaSenses('${lemma.id}')`,
                  },
                ]
              : [],
          detailsId: `senses-${lemma.id}`,
        })
      )
      .join("");

    renderToContainer("lemmaResults", result.headerHTML + resultHTML);
  }

  showLemmaSenses(lemmaId) {
    toggleDetails(`senses-${lemmaId}`, () => {
      const lexiconXML = this.authorityData.parsedXML.find((xml) =>
        xml.filename.includes("lexicon")
      );

      if (!lexiconXML) return "Lexicon XML nicht gefunden";

      const lemmaEntry = Array.from(
        lexiconXML.doc.querySelectorAll("entry")
      ).find((entry) => entry.getAttribute("xml:id") === lemmaId);

      if (!lemmaEntry) return "Lemma nicht im XML gefunden";

      const senses = lemmaEntry.querySelectorAll("sense");
      if (senses.length === 0) return "Keine Bedeutungen gefunden";

      const sensesHTML = Array.from(senses)
        .map((sense, index) => {
          const senseId = sense.getAttribute("xml:id") || `sense_${index + 1}`;
          const conceptPtrs = sense.querySelectorAll(
            'ptr[target*="concepts.xml#"]'
          );

          let conceptsHTML = "";
          if (conceptPtrs.length > 0) {
            const concepts = Array.from(conceptPtrs)
              .map((ptr) => {
                const conceptId = ptr.getAttribute("target").split("#")[1];
                const concept = this.authorityData.concepts.find(
                  (c) => c.id === conceptId
                );
                return concept ? concept.termDE || concept.termEN : conceptId;
              })
              .filter(Boolean);

            if (concepts.length > 0) {
              conceptsHTML = `
                            <div style="margin-top: 5px; font-size: 0.85rem; color: #666;">
                                <strong>Konzepte:</strong> ${concepts.join(
                                  " • "
                                )}
                            </div>
                        `;
            }
          }

          return `
                    <div style="margin-bottom: 8px; font-size: 0.9rem;">
                        <strong>Bedeutung ${index + 1}:</strong> ${senseId}
                        ${conceptsHTML}
                    </div>
                `;
        })
        .join("");

      return `
                <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">
                    🔍 ${senses.length} Bedeutungen:
                </div>
                ${sensesHTML}
            `;
    });
  }

  // ==================== CONCEPTS EXPLORER ====================

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

    displayResults("💭 Alle Konzepte aus Authority Files", results);
  }

  showConceptsWithSearch() {
    const searchHTML = createSearchInterface({
      title: "💭 Konzepte-Explorer",
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

    const matches = SearchPatterns.multiField(
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
                🔤 ${
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

  // ==================== GENRES EXPLORER ====================

  // ==================== GENRE HELPER METHODS ====================

  findWorksInGenre(genreId) {
    const workIds =
      window.playground.authorityManager.indexes.genreToWorks.get(genreId) ||
      [];

    return workIds
      .map((workId) => this.authorityData.works.find((w) => w.id === workId))
      .filter(Boolean);
  }

  getGenreHierarchy(genreId) {
    return (
      window.playground.authorityManager.indexes.genreHierarchy.get(genreId) ||
      null
    );
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

    displayResults("🎭 Alle Gattungen aus Authority Files", results);
  }

  showGenresWithSearch() {
    const searchHTML = createSearchInterface({
      title: "🎭 Gattungen-Explorer",
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

    const matches = SearchPatterns.multiField(
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
                📚 ${worksInGenre.length} Werke in "${genreName}"${
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
                👥 ${authorsInGenre.length} Autoren in "${genreName}"${
        authorsInGenre.length > 15 ? " (erste 15)" : ""
      }:
            </div>
            ${authorsHTML}
        `;
    });
  }

  // ==================== NAMES EXPLORER ====================

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

    displayResults("📛 Alle Namen aus Authority Files", results);
  }

  showNamesWithSearch() {
    const searchHTML = createSearchInterface({
      title: "📛 Namen-Explorer",
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

    const matches = SearchPatterns.multiField(
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
              ? `${conceptConnections.length} Konzepte`
              : null,
          ]),
          title: name.termDE || name.termEN,
          buttons:
            conceptConnections.length > 0
              ? [
                  {
                    text: "Konzepte anzeigen",
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
        return "Keine Konzept-Verbindungen für diesen Namen gefunden.";
      }

      const conceptsHTML = concepts
        .slice(0, 10)
        .map(
          (concept) => `
            <div style="margin-bottom: 3px; font-size: 0.85rem;">
                • <strong>${concept.termDE || concept.termEN}</strong>
                <span style="color: #666;">(${concept.id})</span>
            </div>
        `
        )
        .join("");

      return `
            <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">
                💭 ${concepts.length} verwandte Konzepte zu "${nameText}"${
        concepts.length > 10 ? " (erste 10)" : ""
      }:
            </div>
            ${conceptsHTML}
        `;
    });
  }

  findConceptsForName(nameId) {
    // Look for semantic connections between names and concepts
    // This would need to be implemented based on actual data structure
    // For now, return empty array as we don't have explicit name->concept mappings
    const namesXML = this.authorityData.parsedXML.find((xml) =>
      xml.filename.includes("names")
    );

    if (!namesXML) return [];

    const nameElement = Array.from(
      namesXML.doc.querySelectorAll("category")
    ).find((cat) => cat.getAttribute("xml:id") === nameId);

    if (!nameElement) return [];

    // Look for exactMatch or related pointers to concepts
    const conceptPtrs = nameElement.querySelectorAll(
      'ptr[target*="concepts.xml#"]'
    );
    const relatedConcepts = [];

    conceptPtrs.forEach((ptr) => {
      const target = ptr.getAttribute("target");
      if (target) {
        const conceptId = target.split("#")[1];
        const concept = this.authorityData.concepts.find(
          (c) => c.id === conceptId
        );
        if (concept) {
          relatedConcepts.push(concept);
        }
      }
    });

    return relatedConcepts;
  }
}
