/**
 * MHDBDB Playground - UI Core
 * Basic UI operations: status, overviews, results display
 */

// ==================== STATUS MANAGEMENT ====================

export function updateStatus(indicator, text) {
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');

    if (statusIndicator) statusIndicator.textContent = indicator;
    if (statusText) statusText.textContent = text;
}

// ==================== OVERVIEW UPDATES ====================

export function updateAuthorityOverview(authorityData) {
    const stats = document.getElementById('authorityStats');
    if (!stats) return;

    stats.innerHTML = `
        <div class="data-stat">
            <span class="label">📄 Authority Files:</span>
            <span class="value">${authorityData.files.length}</span>
        </div>
        <div class="data-stat">
            <span class="label">👥 Personen:</span>
            <span class="value">${authorityData.persons.length}</span>
        </div>
        <div class="data-stat">
            <span class="label">📚 Werke:</span>
            <span class="value">${authorityData.works.length}</span>
        </div>
        <div class="data-stat">
            <span class="label">🔤 Lemmata:</span>
            <span class="value">${authorityData.lemmata.length}</span>
        </div>
        <div class="data-stat">
            <span class="label">💭 Konzepte:</span>
            <span class="value">${authorityData.concepts.length}</span>
        </div>
        <div class="data-stat">
            <span class="label">🎭 Gattungen:</span>
            <span class="value">${authorityData.genres.length}</span>
        </div>
        <div class="data-stat">
            <span class="label">📛 Namen:</span>
            <span class="value">${authorityData.names.length}</span>
        </div>
    `;
}

export function updateTEIOverview(teiData) {
    const overview = document.getElementById('teiOverview');
    const stats = document.getElementById('teiStats');

    if (teiData.files.length > 0 && overview && stats) {
        overview.style.display = 'block';
        stats.innerHTML = `
            <div class="data-stat">
                <span class="label">📄 TEI Dateien:</span>
                <span class="value">${teiData.files.length}</span>
            </div>
            <div class="data-stat">
                <span class="label">📝 Wörter:</span>
                <span class="value">${teiData.words.length}</span>
            </div>
            <div class="data-stat">
                <span class="label">📏 Textzeilen:</span>
                <span class="value">${teiData.lines.length}</span>
            </div>
            <div class="data-stat">
                <span class="label">🏷️ Annotationen:</span>
                <span class="value">${teiData.annotations.length}</span>
            </div>
        `;
    }
}

// ==================== BUTTON STATE MANAGEMENT ====================

export function enableAuthorityQueries() {
    const buttonIds = [
        'showAuthorsBtn',
        'showWorksBtn', 
        'showLemmataBtn',
        'showConceptsBtn',
        'showGenresBtn',
        'showNamesBtn',
        'xpathExecute'
    ];

    buttonIds.forEach(id => {
        const button = document.getElementById(id);
        if (button) {
            button.disabled = false;
        }
    });
}

export function enableTEIQueries() {
    const teiQueriesSection = document.getElementById('teiQueries');
    if (teiQueriesSection) {
        teiQueriesSection.style.display = 'block';
    }
}

// ==================== FILE DISPLAY ====================

export function displayFileItem(file, container) {
    if (!container) return;

    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.innerHTML = `
        <div class="file-name">${file.name}</div>
        <div class="file-info">${(file.size / 1024).toFixed(1)} KB • TEI Textdatei</div>
    `;
    container.appendChild(fileItem);
}

// ==================== RESULTS DISPLAY ====================

export function displayResults(title, results) {
    const container = document.getElementById('resultsContainer');
    if (!container) return;

    if (results.length === 0) {
        container.innerHTML = `
            <div class="result-item">
                <div class="result-meta">${title}</div>
                <div class="result-snippet">Keine Ergebnisse gefunden.</div>
            </div>
        `;
        return;
    }

    const resultsHTML = results.map(result => `
        <div class="result-item">
            <div class="result-meta">${result.meta}</div>
            <div class="result-snippet">${result.snippet}</div>
        </div>
    `).join('');

    container.innerHTML = `
        <div style="margin-bottom: 15px; font-weight: 600; color: #667eea;">
            ${title} (${results.length} Ergebnisse)
        </div>
        ${resultsHTML}
    `;
}

// ==================== WELCOME & ERROR STATES ====================

export function showWelcomeMessage() {
    const container = document.getElementById('resultsContainer');
    if (!container) return;

    container.innerHTML = `
        <div style="text-align: center; padding: 20px; color: #667eea;">
            <h3>🎉 MHDBDB Playground bereit!</h3>
            <p style="margin-top: 10px; color: #666;">
                Authority Files sind geladen. Laden Sie TEI-Textdateien hoch oder beginnen Sie mit der Analyse der Authority Files.
            </p>
        </div>
    `;
}

export function showError(message) {
    const container = document.getElementById('resultsContainer');
    if (!container) return;

    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.style.cssText = 'color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 6px; margin: 10px 0;';
    errorDiv.textContent = message;
    container.insertBefore(errorDiv, container.firstChild);
}

// ==================== LOADING STATES ====================

export function showLoading(containerId, message = "Lädt...") {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #999;">
                ${message}
            </div>
        `;
        return true;
    }
    return false;
}

export function hideLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '';
        return true;
    }
    return false;
}

// ==================== CONTAINER MANAGEMENT ====================

export function renderToContainer(containerId, html) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = html;
        return true;
    }
    console.warn(`⚠️ Container not found: ${containerId}`);
    return false;
}

export function appendToContainer(containerId, html) {
    const container = document.getElementById(containerId);
    if (container) {
        container.insertAdjacentHTML('beforeend', html);
        return true;
    }
    console.warn(`⚠️ Container not found: ${containerId}`);
    return false;
}

// ==================== UI STATE COORDINATION ====================

export function updateAllUI(authorityData, teiData) {
    // Update status based on loaded data
    updateStatus('✅', `${authorityData.files.length}/6 Authority Files geladen`);
    
    // Update overviews
    updateAuthorityOverview(authorityData);
    updateTEIOverview(teiData);
    
    // Enable appropriate queries
    enableAuthorityQueries();
    
    if (teiData.files.length > 0) {
        enableTEIQueries();
    }
    
    // Show welcome if only authority files loaded
    if (authorityData.files.length > 0 && teiData.files.length === 0) {
        showWelcomeMessage();
    }
}

// ==================== EVENT DELEGATION HELPERS ====================

export function delegateClick(containerId, selector, handler) {
    const container = document.getElementById(containerId);
    if (container) {
        container.addEventListener('click', (e) => {
            if (e.target.matches(selector)) {
                handler(e);
            }
        });
        return true;
    }
    return false;
}