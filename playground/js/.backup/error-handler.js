/**
 * Error Handler Utility
 *
 * Provides centralized error handling with user-friendly messages
 * and optional UI display.
 */

export class ErrorHandler {
  /**
   * Wrap an async function with error boundary
   * @param {Function} fn - Async function to execute
   * @param {string} context - Context description for logging
   * @returns {Promise<any>} - Result from function or throws error
   */
  static async withErrorBoundary(fn, context = 'Operation') {
    try {
      return await fn();
    } catch (error) {
      console.error(`❌ ${context} failed:`, error);

      // Log stack trace in development
      if (error.stack) {
        console.error('Stack trace:', error.stack);
      }

      // Get user-friendly message
      const userMessage = this.getUserFriendlyMessage(error);

      // Show error to user (if UI element exists)
      this.showUserError(`${context}: ${userMessage}`);

      // Re-throw for caller to handle
      throw error;
    }
  }

  /**
   * Convert technical error to user-friendly message
   * @param {Error} error - Error object
   * @returns {string} - User-friendly message
   */
  static getUserFriendlyMessage(error) {
    const messages = {
      // Storage errors
      'QuotaExceededError': 'Speicherplatz voll. Bitte Speicherplatz freigeben.',
      'UnknownError': 'Datenbankfehler. Bitte Browser-Cache leeren.',

      // Network errors
      'NetworkError': 'Netzwerkfehler. Bitte Internetverbindung prüfen.',
      'TypeError': 'Fehler beim Laden der Daten. Bitte Seite neu laden.',

      // Parse errors
      'SyntaxError': 'Ungültige Dateiformat. Bitte TEI-XML hochladen.',
      'ParseError': 'XML-Parserfehler. Datei ist möglicherweise beschädigt.',

      // Permission errors
      'NotAllowedError': 'Zugriff verweigert. Bitte Browserrechte prüfen.',
      'SecurityError': 'Sicherheitsfehler. Dateien müssen über HTTP-Server geladen werden.',

      // File errors
      'NotFoundError': 'Datei nicht gefunden.',
      'AbortError': 'Vorgang abgebrochen.',
    };

    // Check error name
    if (error.name && messages[error.name]) {
      return messages[error.name];
    }

    // Check error message for patterns
    if (error.message) {
      if (error.message.includes('quota')) {
        return messages['QuotaExceededError'];
      }
      if (error.message.includes('network') || error.message.includes('fetch')) {
        return messages['NetworkError'];
      }
      if (error.message.includes('parse') || error.message.includes('XML')) {
        return messages['ParseError'];
      }
    }

    // Default message
    return error.message || 'Ein unbekannter Fehler ist aufgetreten.';
  }

  /**
   * Display error message to user in UI
   * @param {string} message - Error message to display
   * @param {number} duration - Auto-hide after milliseconds (0 = manual close)
   */
  static showUserError(message, duration = 0) {
    // Check if error display element exists
    const errorDisplay = document.getElementById('error-display');

    if (!errorDisplay) {
      // Fallback to console if no UI element
      console.warn('No error-display element found. Error:', message);
      return;
    }

    // Find or create error message element
    let messageEl = errorDisplay.querySelector('p');
    if (!messageEl) {
      messageEl = document.createElement('p');
      messageEl.className = 'text-red-800';
      errorDisplay.appendChild(messageEl);
    }

    // Set message
    messageEl.textContent = message;

    // Show error display
    errorDisplay.classList.remove('hidden');

    // Auto-hide if duration specified
    if (duration > 0) {
      setTimeout(() => {
        this.hideUserError();
      }, duration);
    }
  }

  /**
   * Hide error display
   */
  static hideUserError() {
    const errorDisplay = document.getElementById('error-display');
    if (errorDisplay) {
      errorDisplay.classList.add('hidden');
    }
  }

  /**
   * Log error to console with context
   * @param {Error} error - Error object
   * @param {string} context - Context description
   */
  static logError(error, context = 'Unknown') {
    console.error(`❌ Error in ${context}:`, {
      name: error.name,
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Check if error is a storage quota error
   * @param {Error} error - Error to check
   * @returns {boolean}
   */
  static isQuotaError(error) {
    return error.name === 'QuotaExceededError' ||
           (error.message && error.message.includes('quota'));
  }

  /**
   * Check if error is a network error
   * @param {Error} error - Error to check
   * @returns {boolean}
   */
  static isNetworkError(error) {
    return error.name === 'NetworkError' ||
           error.name === 'TypeError' && error.message.includes('fetch') ||
           (error.message && error.message.includes('network'));
  }

  /**
   * Check if error is a parse error
   * @param {Error} error - Error to check
   * @returns {boolean}
   */
  static isParseError(error) {
    return error.name === 'SyntaxError' ||
           error.name === 'ParseError' ||
           (error.message && (error.message.includes('parse') || error.message.includes('XML')));
  }

  /**
   * Create a standardized error object
   * @param {string} message - Error message
   * @param {string} code - Error code
   * @param {Object} details - Additional error details
   * @returns {Error}
   */
  static createError(message, code = 'UNKNOWN_ERROR', details = {}) {
    const error = new Error(message);
    error.code = code;
    error.details = details;
    return error;
  }
}

/**
 * Async wrapper for safer error handling
 * Usage: await safeAsync(() => riskyOperation(), 'My Operation')
 *
 * @param {Function} fn - Async function
 * @param {string} context - Context description
 * @returns {Promise<[Error|null, any]>} - [error, result] tuple
 */
export async function safeAsync(fn, context = 'Operation') {
  try {
    const result = await fn();
    return [null, result];
  } catch (error) {
    ErrorHandler.logError(error, context);
    return [error, null];
  }
}

/**
 * Retry wrapper for network operations
 * @param {Function} fn - Async function to retry
 * @param {number} maxRetries - Maximum retry attempts
 * @param {number} delayMs - Delay between retries
 * @returns {Promise<any>}
 */
export async function retryAsync(fn, maxRetries = 3, delayMs = 1000) {
  let lastError;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      if (attempt < maxRetries) {
        console.warn(`⚠️ Attempt ${attempt} failed, retrying in ${delayMs}ms...`);
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
  }

  throw lastError;
}

export default ErrorHandler;
