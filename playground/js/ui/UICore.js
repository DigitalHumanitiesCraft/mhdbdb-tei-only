/**
 * MHDBDB Playground - UI Core
 * Tailwind-based UI operations: status, overviews, results display
 */

// ==================== STATUS MANAGEMENT ====================

export function updateStatus(indicator, text) {
  const statusIndicator = document.getElementById('statusIndicator');
  const statusText = document.getElementById('statusText');

  if (statusIndicator) {
    // Map emoji indicators to Heroicons
    const iconMap = {
      '🔄': '<svg class="w-6 h-6 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>',
      '✅': '<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
      '📥': '<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 12l3 3m0 0l3-3m-3 3V9"></path></svg>',
      '🗂️': '<svg class="w-6 h-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>'
    };

    const svgIcon = iconMap[indicator] || iconMap['🗂️']; // fallback to folder icon
    statusIndicator.innerHTML = svgIcon;
  }

  if (statusText) statusText.textContent = text;
}

// ==================== OVERVIEW UPDATES ====================

export function updateAuthorityOverview(authorityData) {
  const stats = document.getElementById('authorityStats');
  if (!stats) return;

  const items = [
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>', label: 'Authority Files', value: authorityData.files.length },
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path></svg>', label: 'Personen', value: authorityData.persons.length },
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>', label: 'Werke', value: authorityData.works.length },
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m0 0V1h4a1 1 0 011 1v20a1 1 0 01-1 1H3a1 1 0 01-1-1V2a1 1 0 011-1h4v3z"></path></svg>', label: 'Lemmata', value: authorityData.lemmata.length },
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>', label: 'Konzepte', value: authorityData.concepts.length },
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m0 0V1h4a1 1 0 011 1v20a1 1 0 01-1 1H3a1 1 0 01-1-1V2a1 1 0 011-1h4v3zm5 8a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>', label: 'Gattungen', value: authorityData.genres.length },
    { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path></svg>', label: 'Namen', value: authorityData.names.length }
  ];

  stats.innerHTML = `
    <dl class="space-y-2">
      ${items
        .map(
          ({ icon, label, value }) => `
            <div class="flex items-center justify-between rounded-xl bg-white/80 px-4 py-2 shadow-sm ring-1 ring-slate-200/70">
              <dt class="flex items-center gap-3 text-sm font-medium text-slate-600">
                <span class="text-lg">${icon}</span>
                <span>${label}</span>
              </dt>
              <dd class="text-sm font-semibold text-brand-700">${value}</dd>
            </div>
          `
        )
        .join('')}
    </dl>
  `;
}

export function updateTEIOverview(teiData) {
  const overview = document.getElementById('teiOverview');
  const stats = document.getElementById('teiStats');

  if (teiData.files.length > 0 && overview && stats) {
    overview.style.display = 'block';

    const items = [
      { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>', label: 'TEI-Dateien', value: teiData.files.length },
      { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>', label: 'Wörter', value: teiData.words.length },
      { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>', label: 'Textzeilen', value: teiData.lines.length },
      { icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path></svg>', label: 'Annotationen', value: teiData.annotations.length }
    ];

    stats.innerHTML = `
      <dl class="space-y-2">
        ${items
          .map(
            ({ icon, label, value }) => `
              <div class="flex items-center justify-between rounded-xl bg-white/80 px-4 py-2 shadow-sm ring-1 ring-brand-100/80">
                <dt class="flex items-center gap-3 text-sm font-medium text-slate-600">
                  <span class="text-lg">${icon}</span>
                  <span>${label}</span>
                </dt>
                <dd class="text-sm font-semibold text-brand-700">${value}</dd>
              </div>
            `
          )
          .join('')}
      </dl>
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

  buttonIds.forEach((id) => {
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
  fileItem.className = 'file-item shadow-sm ring-1 ring-slate-200/70 bg-white/90 backdrop-blur-sm';
  fileItem.setAttribute('data-filename', file.name.toLowerCase());
  fileItem.innerHTML = `
    <div class="file-name">${file.name}</div>
    <div class="file-info">${(file.size / 1024).toFixed(1)} KB • TEI-Textdatei</div>
  `;
  container.appendChild(fileItem);

  // Update file count and show summary
  updateFileCount();
}

// ==================== COLLAPSIBLE FILE LIST ====================

export function setupCollapsibleFileList() {
  const filesSummary = document.getElementById('filesSummary');
  const filesContent = document.getElementById('filesContent');
  const expandIcon = document.getElementById('expandIcon');

  if (!filesSummary || !filesContent || !expandIcon) return;

  filesSummary.addEventListener('click', () => {
    const isExpanded = filesSummary.classList.contains('expanded');

    if (isExpanded) {
      // Collapse
      filesSummary.classList.remove('expanded');
      filesContent.classList.add('hidden');
    } else {
      // Expand
      filesSummary.classList.add('expanded');
      filesContent.classList.remove('hidden');
    }
  });
}

export function setupFileFilter() {
  const fileFilter = document.getElementById('fileFilter');
  const uploadedFiles = document.getElementById('uploadedFiles');

  if (!fileFilter || !uploadedFiles) return;

  fileFilter.addEventListener('input', (e) => {
    const filterValue = e.target.value.toLowerCase();
    const fileItems = uploadedFiles.querySelectorAll('.file-item');

    fileItems.forEach(item => {
      const filename = item.getAttribute('data-filename') || '';
      const matches = filename.includes(filterValue);

      if (matches) {
        item.removeAttribute('data-hidden');
        item.style.display = '';
      } else {
        item.setAttribute('data-hidden', 'true');
        item.style.display = 'none';
      }
    });
  });
}

export function updateFileCount() {
  const uploadedFiles = document.getElementById('uploadedFiles');
  const fileCount = document.getElementById('fileCount');
  const filesSummary = document.getElementById('filesSummary');

  if (!uploadedFiles || !fileCount || !filesSummary) return;

  const totalFiles = uploadedFiles.querySelectorAll('.file-item').length;
  fileCount.textContent = totalFiles;

  // Show/hide summary based on file count
  if (totalFiles > 0) {
    filesSummary.style.display = 'flex';
  } else {
    filesSummary.style.display = 'none';
  }
}

// ==================== RESULTS DISPLAY ====================

export function displayResults(title, results) {
  const container = document.getElementById('resultsContainer');
  if (!container) return;

  if (!results || results.length === 0) {
    container.innerHTML = `
      <div class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center text-sm text-slate-500">
        <p class="font-medium text-slate-600">${title}</p>
        <p class="mt-2 text-slate-500">Keine Ergebnisse gefunden.</p>
      </div>
    `;
    return;
  }

  const resultsHTML = results
    .map(
      (result) => `
        <article class="result-item rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm transition hover:border-brand-200">
          <header class="result-meta text-xs font-semibold uppercase tracking-wide text-brand-600">${result.meta}</header>
          <p class="result-snippet mt-2 text-sm leading-relaxed text-slate-700">${result.snippet}</p>
        </article>
      `
    )
    .join('');

  container.innerHTML = `
    <div class="mb-4 flex items-center justify-between rounded-xl bg-slate-50/80 px-4 py-2 text-sm font-medium text-slate-600">
      <span>${title}</span>
      <span class="text-xs uppercase tracking-wide text-slate-400">${results.length} Treffer</span>
    </div>
    <div class="space-y-3">
      ${resultsHTML}
    </div>
  `;
}

// ==================== SUMMARY RESULTS DISPLAY ====================

export function displaySummaryResults(title, summaryData) {
  const container = document.getElementById('resultsContainer');
  if (!container) return;

  if (!summaryData || summaryData.length === 0) {
    container.innerHTML = `
      <div class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center text-sm text-slate-500">
        <p class="font-medium text-slate-600">${title}</p>
        <p class="mt-2 text-slate-500">Keine Ergebnisse gefunden.</p>
      </div>
    `;
    return;
  }

  const totalResults = summaryData.reduce((sum, s) => sum + (s.count || 0), 0);
  const summariesHTML = summaryData.map((summary, index) => createSummaryCard(summary, index)).join('');

  container.innerHTML = `
    <div class="mb-4 flex items-center justify-between rounded-xl bg-slate-50/80 px-4 py-2 text-sm font-medium text-slate-600">
      <span>${title}</span>
      <span class="text-xs uppercase tracking-wide text-slate-400">${totalResults} Treffer · ${summaryData.length} Kontexte</span>
    </div>
    <div class="space-y-3">
      ${summariesHTML}
    </div>
  `;

  setupSummaryExpansion();
}

function createSummaryCard(summary, index) {
  const previewText = summary.preview || 'Klicken für Details…';
  const detailsHTML = summary.details ? createDetailsHTML(summary.details) : '';

  return `
    <article class="result-summary group overflow-hidden rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm transition hover:border-brand-200" data-summary-id="${index}">
      <div class="summary-header flex items-start justify-between gap-4">
        <div class="flex-1">
          <h4 class="text-sm font-semibold text-slate-900">${summary.title}</h4>
          <p class="summary-preview mt-2 text-sm text-slate-600">${previewText}</p>
        </div>
        <div class="flex items-center gap-2">
          <span class="summary-count">${summary.count}</span>
          <span class="expand-icon text-lg">⌄</span>
        </div>
      </div>
      <p class="summary-expand-hint mt-3 text-xs font-medium uppercase tracking-wide text-slate-400">Klicken zum Erweitern</p>
      <div class="result-details">
        ${detailsHTML}
      </div>
    </article>
  `;
}

function createDetailsHTML(details) {
  if (Array.isArray(details)) {
    return details
      .map(
        (detail) => `
          <div class="detail-item">
            <div class="detail-meta">${detail.meta || ''}</div>
            <div class="detail-snippet">${detail.snippet || detail.text || ''}</div>
          </div>
        `
      )
      .join('');
  }
  return `<div class="detail-snippet">${details}</div>`;
}

function setupSummaryExpansion() {
  const summaries = Array.from(document.querySelectorAll('.result-summary'));
  summaries.forEach((summary) => {
    const clone = summary.cloneNode(true);
    summary.replaceWith(clone);
  });

  document.querySelectorAll('.result-summary').forEach((summary) => {
    summary.addEventListener('click', (event) => {
      event.preventDefault();
      summary.classList.toggle('expanded');
    });
  });
}

// ==================== FILE-GROUPED RESULTS ====================

export function displayGroupedResults(title, groupedData) {
  const container = document.getElementById('resultsContainer');
  if (!container) return;

  const groups = Object.entries(groupedData || {});
  const totalResults = groups.reduce((sum, [, results]) => sum + results.length, 0);

  const groupsHTML = groups
    .map(([filename, results]) => {
      const groupId = `group_${filename.replace(/[^a-z0-9]/gi, '_')}`;
      return `
        <section class="file-group">
          <header class="file-group-header" data-group-id="${groupId}">
            <span class="flex items-center gap-2 text-sm font-semibold text-slate-800">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              ${filename}
            </span>
            <span class="file-group-count">${results.length}</span>
          </header>
          <div id="${groupId}" class="group-results">
            ${results
              .map(
                (result) => `
                  <div class="detail-item">
                    <div class="detail-meta">${result.meta || ''}</div>
                    <div class="detail-snippet">${result.snippet || result.text || ''}</div>
                  </div>
                `
              )
              .join('')}
          </div>
        </section>
      `;
    })
    .join('');

  container.innerHTML = `
    <div class="mb-4 flex items-center justify-between rounded-xl bg-slate-50/80 px-4 py-2 text-sm font-medium text-slate-600">
      <span>${title}</span>
      <span class="text-xs uppercase tracking-wide text-slate-400">${totalResults} Treffer · ${groups.length} Dateien</span>
    </div>
    <div class="space-y-3">
      ${groupsHTML}
    </div>
  `;
}

// ==================== WELCOME & ERROR STATES ====================

export function showWelcomeMessage() {
  const container = document.getElementById('resultsContainer');
  if (!container) return;

  container.innerHTML = `
    <div class="rounded-2xl border border-brand-100 bg-brand-50/70 p-8 text-center">
      <h3 class="text-lg font-semibold text-brand-700">MHDBDB Playground bereit!</h3>
      <p class="mt-3 text-sm text-brand-800/90">
        Authority Files sind geladen. Laden Sie nun TEI-Textdateien oder nutzen Sie die Abfragen, um sofort mit der Forschung zu beginnen.
      </p>
    </div>
  `;
}

export function showError(message) {
  const container = document.getElementById('resultsContainer');
  if (!container) return;

  const errorDiv = document.createElement('div');
  errorDiv.className = 'rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 shadow-sm';
  errorDiv.textContent = message;
  container.insertBefore(errorDiv, container.firstChild);
}

// ==================== LOADING STATES ====================

export function showLoading(containerId, message = 'Lädt…') {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = `
      <div class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center text-sm text-slate-500">
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

// ==================== SPINNER INFRASTRUCTURE ====================

export function showSpinner(containerId, message = 'Lädt…', large = false) {
  const container = document.getElementById(containerId);
  if (!container) return false;

  const spinnerClass = large ? 'spinner spinner-large' : 'spinner';
  const loadingHTML = `
    <div class="loading-message">
      <div class="${spinnerClass}"></div>
      ${message}
    </div>
  `;

  container.innerHTML = loadingHTML;
  return true;
}

export function showOverlaySpinner(containerId, message = 'Lädt…', large = false) {
  const container = document.getElementById(containerId);
  if (!container) return false;

  const computedStyle = window.getComputedStyle(container);
  if (computedStyle.position === 'static') {
    container.style.position = 'relative';
  }

  const spinnerClass = large ? 'spinner spinner-large' : 'spinner';
  const overlayHTML = `
    <div class="loading-overlay">
      <div class="loading-message">
        <div class="${spinnerClass}"></div>
        ${message}
      </div>
    </div>
  `;

  const existingOverlay = container.querySelector('.loading-overlay');
  if (existingOverlay) {
    existingOverlay.remove();
  }

  container.insertAdjacentHTML('beforeend', overlayHTML);
  return true;
}

export function hideSpinner(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return false;

  const overlay = container.querySelector('.loading-overlay');
  if (overlay) {
    overlay.remove();
    return true;
  }

  // Special handling for uploadedFilesSection to restore collapsible structure
  if (containerId === 'uploadedFilesSection') {
    container.innerHTML = `
      <!-- Summary header (always visible) -->
      <div id="filesSummary" class="flex items-center justify-between p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition" style="display: none;">
          <span class="font-medium text-slate-700">
              <span id="fileCount">0</span> TEI-Dateien geladen
          </span>
          <svg id="expandIcon" class="w-5 h-5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
      </div>

      <!-- Collapsible content -->
      <div id="filesContent" class="hidden space-y-3">
          <!-- Search/filter input -->
          <input type="text"
                 id="fileFilter"
                 placeholder="Dateinamen filtern (z.B. 'ABG')..."
                 class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200">

          <!-- File list container -->
          <div id="uploadedFiles" class="space-y-2 max-h-96 overflow-y-auto"></div>
      </div>
    `;

    // Re-setup collapsible functionality
    setupCollapsibleFileList();
    setupFileFilter();
    return true;
  }

  container.innerHTML = '';
  return true;
}

// ==================== PROGRESS TRACKING ====================

export function showProgress(containerId, current, total, message = 'Bearbeitung…') {
  const container = document.getElementById(containerId);
  if (!container) return false;

  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;
  const progressHTML = `
    <div class="upload-progress">
      <div class="upload-progress-text">
        ${message} (${current}/${total})
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width: ${percentage}%"></div>
      </div>
    </div>
  `;

  container.innerHTML = progressHTML;
  return true;
}

export function updateProgress(containerId, current, total, message = 'Bearbeitung…') {
  const container = document.getElementById(containerId);
  if (!container) return false;

  const progressText = container.querySelector('.upload-progress-text');
  const progressFill = container.querySelector('.progress-fill');

  if (progressText && progressFill) {
    const percentage = total > 0 ? Math.round((current / total) * 100) : 0;
    progressText.textContent = `${message} (${current}/${total})`;
    progressFill.style.width = `${percentage}%`;
    return true;
  }

  return showProgress(containerId, current, total, message);
}

// ==================== CONTAINER MANAGEMENT ====================

export function renderToContainer(containerId, html) {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = html;
    return true;
  }
  console.warn(`Container not found: ${containerId}`);
  return false;
}

export function appendToContainer(containerId, html) {
  const container = document.getElementById(containerId);
  if (container) {
    container.insertAdjacentHTML('beforeend', html);
    return true;
  }
  console.warn(`Container not found: ${containerId}`);
  return false;
}

// ==================== UI STATE COORDINATION ====================

export function updateAllUI(authorityData, teiData) {
  const loadedLabel = `${authorityData.files.length}/6 Authority Files geladen`;
  const indicator = authorityData.files.length === 6 ? '✅' : '📥';
  updateStatus(indicator, loadedLabel);

  updateAuthorityOverview(authorityData);
  updateTEIOverview(teiData);

  enableAuthorityQueries();

  if (teiData.files.length > 0) {
    enableTEIQueries();
  }

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
