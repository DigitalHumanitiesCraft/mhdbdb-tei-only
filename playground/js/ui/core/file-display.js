/**
 * MHDBDB Playground - File Display
 * Handles TEI file list display, filtering, and collapsible interface
 */

// ==================== FILE DISPLAY ====================

export function displayFileItem(data, container) {
  if (!container) return;

  // Detect data type: File object (uploaded) vs corpus metadata
  const isCorpusData = 'xmlDoc' in data;
  const isFileObject = data instanceof File;

  const fileItem = document.createElement('div');
  fileItem.className = 'file-item shadow-sm ring-1 ring-slate-200/70 bg-white/90 backdrop-blur-sm relative';

  // Get filename from either source (handle both File objects and synthetic file objects)
  const filename = data.name || data.filename;
  if (!filename) {
    console.error('displayFileItem: No filename found in data', data);
    return;
  }
  fileItem.setAttribute('data-filename', filename.toLowerCase());

  // Build file display based on data source
  let statusIcon, statusText, statusColor, fileInfo;

  if (isCorpusData) {
    // Corpus data from pre-built index
    statusIcon = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
    </svg>`;
    statusColor = 'text-purple-600';

    // Build metadata info line
    const metaParts = [];
    if (data.wordCount) metaParts.push(`${data.wordCount.toLocaleString()} words`);
    if (data.author) metaParts.push(data.author);
    if (data.genre) metaParts.push(data.genre);

    fileInfo = metaParts.join(' • ');
    statusText = 'From corpus index';

    fileItem.setAttribute('data-corpus-file', 'true');
  } else {
    // Uploaded file
    const isCachedFile = data.isCachedFile;
    const savedToCache = data.savedToCache;

    if (isCachedFile) {
      statusIcon = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 1.79 4 4 4h8c2.21 0 4-1.79 4-4V7M4 7c0-2.21 1.79-4 4-4h8c2.21 0 4 1.79 4 4M4 7l8 4 8-4"></path>
      </svg>`;
      statusText = 'Cached file';
      statusColor = 'text-green-600';
      fileItem.setAttribute('data-cached-file', 'true');
    } else if (savedToCache) {
      statusIcon = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
      </svg>`;
      statusText = 'New upload (cached)';
      statusColor = 'text-blue-600';
    } else {
      statusIcon = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5l-6.928-12c-.77-.833-1.732-.833-2.5 0L4.732 18.5c-.77.833.192 2.5 1.732 2.5z"></path>
      </svg>`;
      statusText = 'Not cached (lost on refresh)';
      statusColor = 'text-amber-600';
    }

    // Build metadata info line for uploaded files (same format as corpus)
    const metaParts = [];
    metaParts.push(`${(data.size / 1024).toFixed(1)} KB`);
    if (data.author) metaParts.push(data.author);
    metaParts.push(statusText);

    fileInfo = metaParts.join(' • ');
  }

  // Display title if available (both corpus and uploaded files)
  const displayTitle = data.title ? `<div class="text-xs text-slate-500 mt-0.5 truncate">${data.title}</div>` : '';

  fileItem.innerHTML = `
    <div class="flex items-start justify-between gap-3">
      <div class="flex-1 min-w-0">
        <div class="file-name flex items-center gap-2">
          <span class="${statusColor}">${statusIcon}</span>
          <span class="truncate">${filename}</span>
        </div>
        ${displayTitle}
        <div class="file-info">${fileInfo}</div>
      </div>
      <div class="flex items-center gap-1 flex-shrink-0">
        ${!isCorpusData && (data.isCachedFile || data.savedToCache) ? `
          <button
            onclick="window.playground.removeTEIFile('${filename}')"
            class="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
            title="Remove file"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </button>
        ` : ''}
      </div>
    </div>
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
      // Get filename from data attribute
      const filename = item.getAttribute('data-filename') || '';

      // For corpus files, also search in visible text (title, author, genre, etc.)
      const isCorpusFile = item.hasAttribute('data-corpus-file');
      let matches = filename.includes(filterValue);

      if (!matches && isCorpusFile) {
        // Search in all visible text content for corpus metadata
        const textContent = item.textContent.toLowerCase();
        matches = textContent.includes(filterValue);
      }

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
  const cacheControls = document.getElementById('cacheControls');
  const cacheInfo = document.getElementById('cacheInfo');

  if (!uploadedFiles || !fileCount || !filesSummary) return;

  const totalFiles = uploadedFiles.querySelectorAll('.file-item').length;

  // Separate corpus files from uploaded files
  const corpusFiles = uploadedFiles.querySelectorAll('[data-corpus-file="true"]').length;
  const uploadedFilesCount = totalFiles - corpusFiles;
  const cachedFiles = uploadedFiles.querySelectorAll('[data-cached-file="true"]').length;
  const newFiles = uploadedFilesCount - cachedFiles;

  fileCount.textContent = totalFiles;

  // Show/hide summary based on file count
  if (totalFiles > 0) {
    filesSummary.style.display = 'flex';
  } else {
    filesSummary.style.display = 'none';
  }

  // Show/hide cache controls based on cached files (only for uploaded files, not corpus)
  if (cacheControls && cacheInfo) {
    if (cachedFiles > 0 && corpusFiles === 0) {
      cacheControls.style.display = 'flex';

      // Update cache info text
      const cacheText = cachedFiles === 1
        ? `1 gecachte Datei`
        : `${cachedFiles} gecachte Dateien`;
      const newText = newFiles > 0
        ? ` • ${newFiles} neu in dieser Sitzung`
        : '';

      cacheInfo.textContent = `${cacheText}${newText} • Bleiben über Sitzungen erhalten`;
    } else {
      cacheControls.style.display = 'none';
    }
  }
}
