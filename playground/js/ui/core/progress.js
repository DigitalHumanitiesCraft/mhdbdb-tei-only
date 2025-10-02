/**
 * MHDBDB Playground - Progress & Loading States
 * Handles spinners, loading states, and progress bars
 */

// Forward declaration for setupCollapsibleFileList and setupFileFilter
// These will be imported when needed
let setupCollapsibleFileList, setupFileFilter;

export function setFileDisplayHelpers(setupCollapsible, setupFilter) {
  setupCollapsibleFileList = setupCollapsible;
  setupFileFilter = setupFilter;
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
    if (setupCollapsibleFileList) setupCollapsibleFileList();
    if (setupFileFilter) setupFileFilter();
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
