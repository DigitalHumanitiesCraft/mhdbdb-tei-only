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
 * It also owns the mobile-menu toggle (open/close + click-outside + close-on-link),
 * centralized here so that ~10 lines are no longer duplicated inline on every page.
 * Pages must therefore NOT keep their own mobile-menu script, or the two handlers
 * would double-toggle and cancel out.
 */
(function () {
  "use strict";

  function initCurrentYear() {
    const year = String(new Date().getFullYear());
    document.querySelectorAll(".current-year").forEach((el) => {
      el.textContent = year;
    });
  }

  // Mobile-menu toggle (the nav burger is md:hidden, so only relevant < md). Single
  // implementation for all pages; the per-page inline copies were removed with this.
  function initMobileMenu() {
    const button = document.getElementById("mobileMenuButton");
    const menu = document.getElementById("mobileMenu");
    if (!button || !menu) return;
    button.addEventListener("click", () => menu.classList.toggle("hidden"));
    document.addEventListener("click", (event) => {
      if (!button.contains(event.target) && !menu.contains(event.target)) {
        menu.classList.add("hidden");
      }
    });
    menu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => menu.classList.add("hidden"));
    });
  }

  // Project IndexedDB databases, deleted explicitly BY NAME so the reset works in
  // Firefox too — it still does not implement indexedDB.databases(), so name-based
  // deleteDatabase (supported everywhere) is the only cross-browser path. This also
  // covers the app-less help pages, which have no app object to clear through.
  const KNOWN_DB_NAMES = ["MHDBDBMainSite", "MHDBDB_TEI_Cache", "MHDBDB_Playground"];

  // Close the open app handles first so the drop is not "blocked". On the main-site
  // pages app.js (window._mhdbdbApp) holds the corpus/authority DB (Dexie) and the
  // TEI cache; best-effort + optional chaining so it never throws where there is no app.
  function closeKnownConnections() {
    try {
      const app = window._mhdbdbApp;
      app?.corpusLoader?.db?.close?.();
      app?.textRenderer?.cache?.db?.close?.();
    } catch (error) {
      console.warn("[SiteChrome] Could not close DB connections:", error);
    }
  }

  function dropDatabase(name) {
    return new Promise((resolve) => {
      const req = indexedDB.deleteDatabase(name);
      // A connection still open on the page that owns this DB blocks the drop; it
      // then completes on the reload below. Resolve either way so we never hang.
      req.onblocked = () => {
        console.warn(`[SiteChrome] deleteDatabase blocked, finishes on reload: ${name}`);
        resolve();
      };
      req.onsuccess = () => resolve();
      req.onerror = () => resolve();
    });
  }

  // Delete the known project DBs by name (cross-browser) plus any extras that
  // indexedDB.databases() can enumerate (Chromium only), and wait for each drop.
  async function deleteAllDatabases() {
    const names = new Set(KNOWN_DB_NAMES);
    if (typeof indexedDB.databases === "function") {
      try {
        const dbs = await indexedDB.databases();
        dbs.forEach((db) => { if (db.name) names.add(db.name); });
      } catch (error) {
        console.warn("[SiteChrome] indexedDB.databases() failed:", error);
      }
    }
    await Promise.all([...names].map(dropDatabase));
  }

  function initClearSiteData() {
    const btn = document.getElementById("clearSiteDataBtn");
    if (!btn) return;
    btn.addEventListener("click", async () => {
      const message =
        "Alle gespeicherten Daten löschen?\n\n" +
        "Dies umfasst:\n" +
        "• TEI-Dateien Cache\n" +
        "• Authority- und Korpus-Indizes\n" +
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
    initMobileMenu();
    initCurrentYear();
    initClearSiteData();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
