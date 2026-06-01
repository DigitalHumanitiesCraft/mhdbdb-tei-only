/**
 * MHDBDB Site Chrome
 *
 * Shared behaviour for the build-injected footer (includes/_footer.html), loaded
 * on EVERY page via the footer partial. It owns the "clear site data" button and
 * keeps the footer year current.
 *
 * Single source of truth: every page used to carry its own inline clear-site-data
 * handler (and the main-site pages wired it through app.js). Those are removed in
 * favour of this one implementation — binding the same button in two places would
 * fire two confirm dialogs and race two clear+reload sequences.
 *
 * NOTE: the mobile-menu toggle is intentionally NOT handled here — each page
 * still carries its own inline mobile-menu script (toggle + click-outside-close).
 * Binding it here too would double-toggle and cancel out.
 *
 * See docs/superpowers/plans/2026-06-01-shared-site-chrome.md.
 */
(function () {
  "use strict";

  function initCurrentYear() {
    const year = String(new Date().getFullYear());
    document.querySelectorAll(".current-year").forEach((el) => {
      el.textContent = year;
    });
  }

  // Close known IndexedDB connections so deleteDatabase() is not blocked by an
  // open handle. On the main-site pages app.js (window._mhdbdbApp) holds the big
  // corpus/authority DB (Dexie 'MHDBDBMainSite') and the TEI cache (IDBDatabase);
  // an open connection makes deleteDatabase fire "blocked" and the drop silently
  // does not run while the page is alive. Best-effort + optional chaining so this
  // never throws on pages that have no app.
  function closeKnownConnections() {
    try {
      const app = window._mhdbdbApp;
      app?.corpusLoader?.db?.close?.();
      app?.textRenderer?.cache?.db?.close?.();
    } catch (error) {
      console.warn("[SiteChrome] Could not close DB connections:", error);
    }
  }

  // Delete every IndexedDB database and WAIT for each drop (success/error/blocked)
  // before returning, so the indices are actually gone before we reload.
  function deleteAllDatabases() {
    if (typeof indexedDB.databases !== "function") return Promise.resolve();
    return indexedDB.databases().then((dbs) =>
      Promise.all(
        dbs.map(
          (db) =>
            new Promise((resolve) => {
              if (!db.name) return resolve();
              const req = indexedDB.deleteDatabase(db.name);
              req.onblocked = () => {
                console.warn(`[SiteChrome] deleteDatabase blocked: ${db.name}`);
                resolve();
              };
              req.onsuccess = () => resolve();
              req.onerror = () => resolve();
            })
        )
      )
    );
  }

  function initClearSiteData() {
    const btn = document.getElementById("clearSiteDataBtn");
    if (!btn) return;
    btn.addEventListener("click", async () => {
      const message =
        "Alle gespeicherten Daten löschen?\n\n" +
        "Dies umfasst:\n" +
        "• TEI-Dateien Cache\n" +
        "• Authority- und Corpus-Indizes\n" +
        "• Alle lokalen Einstellungen\n\n" +
        "Die Seite wird neu geladen.";
      if (!window.confirm(message)) return;
      try {
        console.log("[SiteChrome] Clearing all site data...");
        closeKnownConnections();
        await deleteAllDatabases();
        localStorage.clear();
        sessionStorage.clear();
        console.log("[SiteChrome] All site data cleared.");
        window.alert("Alle Daten wurden gelöscht. Die Seite wird neu geladen.");
        window.location.reload();
      } catch (error) {
        console.error("[SiteChrome] Error clearing site data:", error);
        window.alert("Fehler beim Löschen der Daten: " + error.message);
      }
    });
  }

  function init() {
    initCurrentYear();
    initClearSiteData();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
