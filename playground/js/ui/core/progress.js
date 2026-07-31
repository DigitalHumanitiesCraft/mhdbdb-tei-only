/**
 * MHDBDB Playground - Progress & Loading States
 * Handles spinners, loading states, and progress bars
 */

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

  container.innerHTML = '';
  return true;
}
