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
    const resultHTML = this.authorityData.lemmata
      .slice(0, displayCount)
      .map((l) =>
        generateResultItem({
          meta: formatMetadata([
            `ID: ${l.id}`,
            l.pos ? `POS: ${l.pos}` : null,
            l.senseCount ? `${l.senseCount} Bedeutungen` : null,
          ]),
          title: `<a href="../lemma/?id=${l.id.replace(/^lemma_/, '')}" target="_blank" rel="noopener" class="text-brand-700 hover:text-brand-900 hover:underline">${l.lemma}</a>`,
          buttons: [
            ...(l.senseCount > 0
              ? [
                  {
                    text: "Bedeutungen anzeigen",
                    action: `window.playground.ui.authorityExplorers.showLemmaSenses('${l.id}')`,
                  },
                ]
              : []),
            {
              text: "MEHR \u2192",
              action: `window.open('../lemma/?id=${l.id.replace(/^lemma_/, '')}', '_blank')`,
            },
          ],
          detailsId: `senses-${l.id}`,
        })
      )
      .join("");

    const header = `<div class="rounded-xl bg-slate-50/80 px-4 py-2 text-sm font-medium text-slate-600">
      <span>Lemmata-Explorer</span>
      <span class="ml-2 text-sm uppercase tracking-wide text-slate-600">erste ${displayCount} von ${this.authorityData.lemmata.length}</span>
    </div>`;

    renderToContainer("resultsContainer", header + `<div class="space-y-3">${resultHTML}</div>`);
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

    // #137: alphabetisch nach Lemma-Label sortieren (vorher implizit nach Lemma-ID),
    // VOR dem maxResults-Cut in handleSearchResults. Idiom wie concept-explorer.js.
    matches.sort((a, b) => (a.lemma || "").localeCompare(b.lemma || "", "de"));

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
          title: `<a href="../lemma/?id=${lemma.id.replace(/^lemma_/, '')}" target="_blank" rel="noopener" class="text-brand-700 hover:text-brand-900 hover:underline">${lemma.lemma}</a>`,
          buttons: [
            ...(lemma.senseCount > 0
              ? [
                  {
                    text: "Bedeutungen anzeigen",
                    action: `window.playground.ui.authorityExplorers.showLemmaSenses('${lemma.id}')`,
                  },
                ]
              : []),
            {
              text: "MEHR \u2192",
              action: `window.open('../lemma/?id=${lemma.id.replace(/^lemma_/, '')}', '_blank')`,
            },
          ],
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
                    <div style="margin-top: 5px; font-size: 0.85rem; color: #475569;">
                        <strong>Begriffe:</strong> ${concepts.join(" • ")}
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

  showLemmaDetails(lemmaId, lemmaText) {
    // Navigate to Lemma Explorer with pre-filled search
    this.showLemmataWithSearch();

    // Pre-fill search input and trigger search
    setTimeout(() => {
      const searchInput = document.getElementById("lemmaSearch");
      if (searchInput) {
        searchInput.value = lemmaText;
        this.searchLemmata(lemmaText);
        searchInput.focus();
      }
    }, 0);
  }
}
