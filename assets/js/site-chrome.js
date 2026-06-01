/**
 * MHDBDB Site Chrome
 *
 * Shared behaviour for the build-injected footer (includes/_footer.html), loaded
 * on EVERY page via the footer partial. It owns the "clear site data" button
 * (previously wired only in app.js, so the button was dead on the pages that do
 * not load app.js — hilfe/impressum/barrierefreiheit/…) and keeps the footer
 * year current.
 *
 * NOTE: the mobile-menu toggle is intentionally NOT handled here — each page
 * already carries its own inline mobile-menu script (toggle + click-outside-close).
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
        // Delete every IndexedDB database (covers TEI cache + authority/corpus indices).
        if (typeof indexedDB.databases === "function") {
          const dbs = await indexedDB.databases();
          for (const db of dbs) {
            if (db.name) indexedDB.deleteDatabase(db.name);
          }
        }
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
