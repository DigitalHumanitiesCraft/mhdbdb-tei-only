/**
 * MHDBDB Playground - Search Helpers
 * Common search patterns and utilities (no over-engineering)
 */

// ==================== SEARCH INTERFACE CREATION ====================

export function createSearchInterface(config) {
  const {
    title,
    placeholder,
    searchInputId,
    resultsId,
    totalCount,
    helpText = "Geben Sie einen Suchbegriff ein, um zu suchen...",
  } = config;

  return `
        <div style="margin-bottom: 15px; font-weight: 600; color: #667eea;">
            ${title} (${totalCount} verfügbar)
        </div>
        <div style="margin-bottom: 15px;">
            <input type="text" id="${searchInputId}" placeholder="${placeholder}" 
                   style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9rem;">
        </div>
        <div id="${resultsId}" style="color: #666; font-style: italic; padding: 20px; text-align: center;">
            ${helpText}
        </div>
    `;
}

// ==================== SEARCH RESULT HANDLING ====================

export function handleSearchResults(searchTerm, matches, config) {
  const {
    searchTermForDisplay = searchTerm,
    maxResults = 50,
    emptyMessage = 'Keine Ergebnisse gefunden für "{term}"',
  } = config;

  if (matches.length === 0) {
    return `
            <div style="color: #999; padding: 20px; text-align: center;">
                ${emptyMessage.replace("{term}", searchTermForDisplay)}
            </div>
        `;
  }

  const displayMatches = matches.slice(0, maxResults);
  const countInfo =
    matches.length > maxResults ? ` (erste ${maxResults} angezeigt)` : "";

  return {
    matches: displayMatches,
    headerHTML: `
            <div style="margin-bottom: 15px; color: #667eea; font-weight: 500;">
                ${matches.length} Treffer für "${searchTermForDisplay}"${countInfo}
            </div>
        `,
  };
}

// ==================== INPUT EVENT SETUP ====================

export function setupSearchInput(inputId, searchHandler) {
  const searchInput = document.getElementById(inputId);
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      searchHandler(e.target.value);
    });
    return searchInput;
  }
  console.warn(`⚠️ Search input not found: ${inputId}`);
  return null;
}

// ==================== RESULT ITEM GENERATION ====================

export function generateResultItem(config) {
  const {
    meta,
    title,
    subtitle = "",
    buttons = [],
    detailsId = "",
    highlight = false,
  } = config;

  const buttonHTML = buttons
    .map(
      (btn) => `
        <button onclick="${btn.action}"
                style="margin-left: 10px; padding: 4px 8px; background: ${
                  btn.color || "#667eea"
                }; color: white; border: none; border-radius: 4px; font-size: 0.8rem; cursor: pointer;">
            ${btn.text}
        </button>
    `
    )
    .join("");

  const subtitleHTML = subtitle
    ? `
        <div style="font-size: 0.85rem; color: #666; margin-top: 5px;">
            ${subtitle}
        </div>
    `
    : "";

  const detailsHTML = detailsId
    ? `
        <div id="${detailsId}" style="display: none; margin-top: 10px; padding: 10px; background: rgba(102, 126, 234, 0.05); border-radius: 6px;"></div>
    `
    : "";

  const titleClass = highlight ? 'class="highlight"' : "";

  return `
        <div class="result-item">
            <div class="result-meta">${meta}</div>
            <div class="result-snippet">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span ${titleClass}><strong>${title}</strong></span>
                    ${buttonHTML}
                </div>
                ${subtitleHTML}
            </div>
            ${detailsHTML}
        </div>
    `;
}

// ==================== TOGGLE DETAILS FUNCTIONALITY ====================

export function toggleDetails(
  detailsId,
  contentGenerator,
  emptyMessage = "Details nicht verfügbar"
) {
  const container = document.getElementById(detailsId);
  if (!container) return false;

  // Toggle visibility
  if (container.style.display !== "none") {
    container.style.display = "none";
    return true;
  }

  try {
    const content = contentGenerator();
    if (content === null || content === "") {
      container.innerHTML = `
                <div style="color: #999; font-style: italic;">
                    ${emptyMessage}
                </div>
            `;
    } else {
      container.innerHTML = content;
    }
    container.style.display = "block";
    return true;
  } catch (error) {
    container.innerHTML = `
            <div style="color: #dc3545; font-style: italic;">
                Fehler beim Laden: ${error.message}
            </div>
        `;
    container.style.display = "block";
    return false;
  }
}

// ==================== EMPTY STATE HANDLING ====================

export function showEmptySearchState(
  containerId,
  message = "Geben Sie einen Suchbegriff ein, um zu suchen..."
) {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = `
            <div style="color: #666; font-style: italic; padding: 20px; text-align: center;">
                ${message}
            </div>
        `;
    return true;
  }
  return false;
}

// ==================== RENDER TO CONTAINER ====================

export function renderToContainer(containerId, html) {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = html;
    return true;
  }
  console.warn(`⚠️ Container not found: ${containerId}`);
  return false;
}

// ==================== STRING UTILITIES ====================

export function escapeForJS(str) {
  return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

export function formatMetadata(items, separator = " • ") {
  return items.filter(Boolean).join(separator);
}

export function formatMultiLanguage(termDE, termEN) {
  if (termDE && termEN) return `${termDE} / ${termEN}`;
  return termDE || termEN || "";
}

// ==================== SEARCH PATTERNS ====================

export const SearchPatterns = {
  // Simple text search
  textContains: (items, searchTerm, fieldGetter) => {
    const term = searchTerm.toLowerCase().trim();
    return items.filter((item) =>
      fieldGetter(item).toLowerCase().includes(term)
    );
  },

  /// Multi-field search
  multiField: (items, searchTerm, fieldGetters) => {
    const term = searchTerm.toLowerCase().trim();
    const matchedItems = new Set(); // Use Set to prevent duplicates

    items.forEach((item) => {
      const hasMatch = fieldGetters.some(
        (getter) => getter(item) && getter(item).toLowerCase().includes(term)
      );
      if (hasMatch) {
        matchedItems.add(item);
      }
    });

    return Array.from(matchedItems);
  },

  // Exact match search
  exactMatch: (items, searchTerm, fieldGetter) => {
    const term = searchTerm.toLowerCase().trim();
    return items.filter((item) => fieldGetter(item).toLowerCase() === term);
  },
};
