/**
 * MHDBDB Playground - Progress & Loading States
 * Handles spinners, loading states, and progress bars
 */

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
