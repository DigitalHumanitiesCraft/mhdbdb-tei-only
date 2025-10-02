/**
 * MHDBDB Playground - Lemma Explorer
 * Handles lemma browsing, search, and sense display with etymology
 */

import {
  createSearchInterface,
  handleSearchResults,
  generateResultItem,
  setupSearchInput,
  toggleDetails,
  showEmptySearchState,
  renderToContainer,
  formatMetadata,
  SearchPatterns,
} from "../search/SearchHelpers.js";

import { displayResults } from "../core/ui-helpers.js";

export class LemmaExplorer {
  constructor(authorityData) {
    this.authorityData = authorityData;
  }

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
      `Lemmata aus Authority Files (erste ${displayCount} von ${this.authorityData.lemmata.length})`,
      results
    );
  }

  showLemmataWithSearch() {
    const searchHTML = createSearchInterface({
      title: "Lemmata-Explorer",
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

    const matches = SearchPatterns.textContainsNormalized(
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
      const lemma = this.authorityData.lemmata.find((l) => l.id === lemmaId);
      if (!lemma) return "Lemma nicht gefunden";

      return this.generateLemmaSenseContent(lemma, lemmaId);
    });
  }

  showComponentLemma(originalLemmaId, componentLemmaId, componentText) {
    const container = document.getElementById(`senses-${originalLemmaId}`);
    if (!container) return;

    const lemma = this.authorityData.lemmata.find((l) => l.id === componentLemmaId);

    if (!lemma) {
      container.innerHTML = `Lemma "${componentText}" nicht gefunden`;
      return;
    }

    const content = this.generateLemmaSenseContent(
      lemma,
      componentLemmaId,
      originalLemmaId
    );

    container.innerHTML = `
        <div style="margin-bottom: 10px; padding: 8px; background: rgba(40, 167, 69, 0.1); border-radius: 4px;">
            <strong>Komponente:</strong> ${componentText} → ${lemma.lemma}
            <button onclick="window.playground.ui.authorityExplorers.showLemmaSenses('${originalLemmaId}')"
                    style="float: right; padding: 2px 6px; background: #6c757d; color: white; border: none; border-radius: 3px; font-size: 0.75rem; cursor: pointer;">
                ← Zurück
            </button>
        </div>
        ${content}
    `;
  }

  generateLemmaSenseContent(lemma, lemmaId, originalLemmaId = null) {
    let resultHTML = "";

    // Extract etymology from index data
    if (lemma.etymology && lemma.etymology.length > 0) {
      const componentsHTML = lemma.etymology
        .map((comp) => {
          const text = comp.text;
          const referencedLemmaId = comp.lemmaRef;

          if (referencedLemmaId) {
            const targetOriginal = originalLemmaId || lemmaId;
            return `
                      <span style="background: rgba(40, 167, 69, 0.1); padding: 2px 6px; border-radius: 3px; margin-right: 5px;">
                          <strong>${text}</strong>
                          <button onclick="window.playground.ui.authorityExplorers.showComponentLemma('${targetOriginal}', '${referencedLemmaId}', '${text}')"
                                  style="margin-left: 4px; padding: 1px 4px; background: #28a745; color: white; border: none; border-radius: 2px; font-size: 0.7rem; cursor: pointer;">
                              →
                          </button>
                      </span>
                  `;
          }
          return `<span style="background: rgba(108, 117, 125, 0.1); padding: 2px 6px; border-radius: 3px; margin-right: 5px;">${text}</span>`;
        })
        .join("");

      resultHTML += `
              <div style="font-weight: 500; margin-bottom: 8px; color: #28a745;">
                  Morphologie: ${componentsHTML}
              </div>
          `;
    }

    // Extract senses from index data
    if (!lemma.senses || lemma.senses.length === 0) {
      resultHTML += "Keine Bedeutungen gefunden";
      return resultHTML;
    }

    const sensesHTML = lemma.senses
      .map((sense, index) => {
        const senseId = sense.id || `sense_${index + 1}`;

        let conceptsHTML = "";
        if (sense.conceptIds && sense.conceptIds.length > 0) {
          const concepts = sense.conceptIds
            .map((conceptId) => {
              const concept = this.authorityData.concepts.find(
                (c) => c.id === conceptId
              );
              return concept ? concept.termDE || concept.termEN : conceptId;
            })
            .filter(Boolean);

          if (concepts.length > 0) {
            conceptsHTML = `
                    <div style="margin-top: 5px; font-size: 0.85rem; color: #666;">
                        <strong>Konzepte:</strong> ${concepts.join(" • ")}
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

    resultHTML += `
        <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">
            ${lemma.senses.length} Bedeutungen:
        </div>
        ${sensesHTML}
    `;

    return resultHTML;
  }
}
