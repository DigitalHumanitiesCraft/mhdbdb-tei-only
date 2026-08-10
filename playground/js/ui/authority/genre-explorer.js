/**
 * MHDBDB Playground - Genre Explorer
 * Handles genre browsing with work and author connections
 */

import {
  createSearchInterface,
  handleSearchResults,
  generateResultItem,
  setupSearchInput,
  toggleDetails,
  renderToContainer,
  escapeForJS,
  formatMetadata,
  SearchPatterns,
} from "../search/SearchHelpers.js";

import { displayResults } from "../core/ui-helpers.js";

// Self-contained per module (DESIGN.md §Escaping-Konvention).
function escapeHtml(s) {
  if (s == null) return "";
  return String(s).replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

export class GenreExplorer {
  constructor(authorityData) {
    this.authorityData = authorityData;
    this.onlyWithWorks = false; // #119 filter: only show genres that have assigned works
    this.tree = null; // #361: lazily built, see buildTree()
    this.expanded = new Set(); // #361: expanded tree nodes, keyed by path
  }

  // ==================== HIERARCHY (#361) ====================

  /**
   * Build the lookup structures the tree view needs, once per session.
   *
   * genre.parents[] holds the *direct* parents as ids (authority index v1.9.0,
   * reduced from the full closure in genres.xml at build time). The result is a
   * DAG rather than a tree: 171 of 615 categories have more than one parent,
   * which is the typology working as intended, not an error in the data.
   *
   * subtreeWorks counts distinct works in a category and everything below it,
   * so a branch that leads nowhere can be marked as such instead of inviting a
   * click. It is a set union, not a sum: a work sitting in two sibling genres
   * must not be counted twice.
   */
  buildTree() {
    if (this.tree) return this.tree;

    const byId = new Map();
    const children = new Map();
    for (const genre of this.authorityData.genres) {
      byId.set(genre.id, genre);
      if (!children.has(genre.id)) children.set(genre.id, []);
    }
    for (const genre of this.authorityData.genres) {
      for (const parentId of genre.parents || []) {
        if (children.has(parentId)) children.get(parentId).push(genre.id);
      }
    }
    for (const list of children.values()) {
      list.sort((a, b) =>
        (byId.get(a).termDE || "").localeCompare(byId.get(b).termDE || "", "de")
      );
    }

    const roots = this.authorityData.genres
      .filter((genre) => !(genre.parents || []).length)
      .map((genre) => genre.id);

    const genreToWorks =
      window.playground?.authorityManager?.indexes?.genreToWorks || new Map();

    const subtreeWorks = new Map();
    const collect = (id, seen) => {
      if (subtreeWorks.has(id)) return subtreeWorks.get(id);
      if (seen.has(id)) return new Set();
      const next = new Set(seen).add(id);
      const works = new Set(genreToWorks.get(id) || []);
      for (const childId of children.get(id) || []) {
        for (const workId of collect(childId, next)) works.add(workId);
      }
      subtreeWorks.set(id, works);
      return works;
    };
    for (const id of byId.keys()) collect(id, new Set());

    this.tree = { byId, children, roots, subtreeWorks };
    return this.tree;
  }

  /**
   * All root-to-category paths, as arrays of ids. A category with several
   * parents has several paths and every one of them is true; the detail view
   * shows them all rather than picking one.
   */
  pathsTo(genreId, seen = new Set()) {
    const { byId } = this.buildTree();
    const genre = byId.get(genreId);
    if (!genre) return [];
    const parents = (genre.parents || []).filter((p) => !seen.has(p));
    if (!parents.length) return [[genreId]];
    const next = new Set(seen).add(genreId);
    return parents.flatMap((parentId) =>
      this.pathsTo(parentId, next).map((path) => [...path, genreId])
    );
  }

  /** One path as "Epik, Lyrik und Dramatik › Kurzdichtung › Märe". */
  formatPath(path) {
    const { byId } = this.buildTree();
    return path
      .map((id) => escapeHtml(byId.get(id)?.termDE || id))
      .join(' <span class="text-slate-400">›</span> ');
  }

  showGenres() {
    if (this.authorityData.genres.length > 30) {
      this.showGenresWithSearch();
    } else {
      this.showAllGenres();
    }
  }

  showAllGenres() {
    const results = this.authorityData.genres.map((g) => ({
      meta: `ID: ${g.id}`,
      snippet: g.termDE || g.termEN,
    }));

    displayResults("Alle Gattungen aus Authority Files", results);
  }

  showGenresWithSearch() {
    const checkboxHTML = `
      <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
        <input type="checkbox" id="genreOnlyWithWorks" ${this.onlyWithWorks ? "checked" : ""}
               class="w-4 h-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500" />
        <span>Nur Gattungen mit zugeordneten Werken anzeigen</span>
      </label>
    `;

    const searchHTML = createSearchInterface({
      title: "Gattungen-Explorer",
      placeholder: "Gattung suchen (z.B. Höfischer Roman, Epik, Lyrik)",
      searchInputId: "genreSearch",
      resultsId: "genreResults",
      totalCount: this.authorityData.genres.length,
      extraControlsHTML: checkboxHTML,
      // #361: kein "Geben Sie einen Suchbegriff ein" mehr. Der Ruhezustand
      // dieses Explorers ist der Baum darunter, und die Aufforderung wuerde
      // ueber einer vollstaendigen Ansicht stehen und ihr widersprechen.
      helpText: "",
    });

    // #361: the tree is the resting state of this explorer. It sits below the
    // search box and steps aside while a search term is active.
    renderToContainer(
      "resultsContainer",
      searchHTML +
        `
      <section id="genreTreeSection" class="space-y-3">
        <header class="rounded-xl bg-slate-50/80 px-4 py-2 text-sm font-medium text-slate-600">
          Textreihentypologie
          <span class="ml-2 font-normal text-slate-500">
            zwei Wurzeln, aufklappbar. Kategorien mit mehreren übergeordneten
            Gattungen stehen an jeder dieser Stellen.
          </span>
        </header>
        <div id="genreTree" class="text-sm text-slate-700"></div>
        <div id="genreDetail" class="hidden"></div>
      </section>
    `
    );
    setupSearchInput("genreSearch", (term) => this.searchGenres(term));
    document.getElementById("genreResults")?.classList.add("hidden");
    this.renderTree();

    // #119: re-run the search with the current term when the filter toggles.
    // The checkbox lives in the outer section, so it survives the genreResults re-render.
    document
      .getElementById("genreOnlyWithWorks")
      ?.addEventListener("change", (event) => {
        this.onlyWithWorks = event.target.checked;
        const term = document.getElementById("genreSearch")?.value || "";
        this.searchGenres(term);
      });
  }

  // ==================== TREE VIEW (#361) ====================

  renderTree() {
    const { roots } = this.buildTree();
    renderToContainer(
      "genreTree",
      roots.map((id) => this.renderNode(id, [])).join("")
    );
  }

  /**
   * One tree node and, if expanded, its children.
   *
   * The DOM key is the whole path, not the genre id: a category with several
   * parents is drawn once per parent, and two nodes for the same category must
   * be able to be open and closed independently.
   */
  renderNode(genreId, ancestors) {
    const { byId, children, subtreeWorks } = this.buildTree();
    const genre = byId.get(genreId);
    if (!genre) return "";

    const path = [...ancestors, genreId];
    const key = path.join("/");
    const kinder = ancestors.includes(genreId) ? [] : children.get(genreId) || [];
    const offen = this.expanded.has(key);
    const eigene = this.findWorksInGenre(genreId).length;
    const imZweig = subtreeWorks.get(genreId)?.size || 0;
    const leer = imZweig === 0;

    // Heroicons chevron, down when open and right when closed, like the
    // metadata panel in the reading view (DESIGN.md: inline SVG is the only
    // icon style in this project).
    const chevron = offen ? "M19 9l-7 7-7-7" : "M9 5l7 7-7 7";
    const toggle = kinder.length
      ? `<button type="button"
             class="w-5 shrink-0 text-slate-400 transition hover:text-brand-600"
             aria-expanded="${offen}"
             aria-label="${offen ? "Zuklappen" : "Aufklappen"}"
             onclick="window.playground.ui.authorityExplorers.toggleGenreNode('${key}')"
           ><svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${chevron}"/></svg></button>`
      : `<span class="w-5 shrink-0"></span>`;

    // Own works first, because that is what a click delivers; the subtree count
    // only appears when it says something the own count does not.
    const zahlen = [
      eigene ? `${eigene} ${eigene === 1 ? "Werk" : "Werke"}` : null,
      imZweig > eigene ? `${imZweig} im Zweig` : null,
    ].filter(Boolean);

    return `
      <div class="genre-node">
        <div class="flex items-baseline gap-1 py-0.5 ${leer ? "opacity-60" : ""}">
          ${toggle}
          <button type="button"
            class="text-left text-slate-700 transition hover:text-brand-600 hover:underline"
            onclick="window.playground.ui.authorityExplorers.showGenreDetail('${genreId}')"
          >${escapeHtml(genre.termDE || genre.termEN)}</button>
          ${
            zahlen.length
              ? `<span class="text-xs text-slate-500">${zahlen.join(", ")}</span>`
              : `<span class="text-xs italic text-slate-400">keine Werke</span>`
          }
        </div>
        ${
          offen
            ? `<div class="ml-3 border-l border-slate-200 pl-3">
                 ${kinder.map((id) => this.renderNode(id, path)).join("")}
               </div>`
            : ""
        }
      </div>
    `;
  }

  toggleGenreNode(key) {
    if (this.expanded.has(key)) {
      this.expanded.delete(key);
    } else {
      this.expanded.add(key);
    }
    this.renderTree();
  }

  /**
   * Detail panel for one category: every path that leads to it, plus its works.
   * There is exactly one panel for the whole tree, so nothing depends on which
   * of the duplicated nodes was clicked.
   */
  showGenreDetail(genreId) {
    const { byId, subtreeWorks } = this.buildTree();
    const genre = byId.get(genreId);
    const panel = document.getElementById("genreDetail");
    if (!genre || !panel) return;

    const pfade = this.pathsTo(genreId);
    const werke = this.findWorksInGenre(genreId);
    const imZweig = subtreeWorks.get(genreId)?.size || 0;

    const pfadHTML = pfade
      .map((p) => `<li class="leading-relaxed">${this.formatPath(p)}</li>`)
      .join("");

    const werkeHTML = werke.length
      ? `<ul class="mt-1 space-y-0.5">
           ${werke
             .slice(0, 20)
             .map(
               (w) =>
                 `<li>${escapeHtml(w.title)}${
                   w.sigle ? ` (${escapeHtml(w.sigle)})` : ""
                 } <span class="text-slate-500">von ${escapeHtml(
                   w.author
                 )}</span></li>`
             )
             .join("")}
         </ul>
         ${
           werke.length > 20
             ? `<p class="mt-1 text-xs text-slate-500">erste 20 von ${werke.length}</p>`
             : ""
         }`
      : `<p class="mt-1 text-slate-500">${
          imZweig
            ? `Dieser Gattung ist kein Werk direkt zugeordnet, im Zweig darunter stehen ${imZweig}.`
            : "Weder dieser Gattung noch einer darunter ist ein Werk der MHDBDB zugeordnet."
        }</p>`;

    panel.className =
      "rounded-2xl border border-slate-200 bg-white p-4 text-sm shadow-sm";
    panel.innerHTML = `
      <h3 class="font-medium text-slate-800">${escapeHtml(
        genre.termDE || genre.termEN
      )}</h3>
      <p class="mt-0.5 text-xs text-slate-500">${escapeHtml(genre.id)}${
      genre.termEN ? ` · ${escapeHtml(genre.termEN)}` : ""
    }</p>
      <div class="mt-3">
        <div class="text-xs uppercase tracking-wide text-slate-500">
          ${pfade.length === 1 ? "Einordnung" : `${pfade.length} Einordnungen`}
        </div>
        <ul class="mt-1 space-y-0.5">${pfadHTML}</ul>
      </div>
      <div class="mt-3">
        <div class="text-xs uppercase tracking-wide text-slate-500">Werke</div>
        ${werkeHTML}
      </div>
    `;
    panel.classList.remove("hidden");
  }

  searchGenres(searchTerm) {
    // #361: Baum und Trefferliste loesen einander ab, statt uebereinander zu
    // stehen. Ohne Begriff ist der Baum die Ansicht, mit Begriff die Liste.
    const treffer = document.getElementById("genreResults");
    const baum = document.getElementById("genreTreeSection");
    if (!searchTerm.trim()) {
      treffer?.classList.add("hidden");
      baum?.classList.remove("hidden");
      return;
    }
    treffer?.classList.remove("hidden");
    baum?.classList.add("hidden");

    let matches = SearchPatterns.multiFieldNormalized(
      this.authorityData.genres,
      searchTerm,
      [(genre) => genre.termDE || "", (genre) => genre.termEN || ""]
    );

    // #119: optional filter to genres that actually have assigned works.
    if (this.onlyWithWorks) {
      matches = matches.filter(
        (genre) => this.findWorksInGenre(genre.id).length > 0
      );
    }

    const result = handleSearchResults(searchTerm, matches, {
      maxResults: 30,
      emptyMessage: 'Keine Gattungen gefunden für "{term}"',
    });

    if (typeof result === "string") {
      renderToContainer("genreResults", result);
      return;
    }

    const resultHTML = result.matches
      .map((genre) => {
        const worksInGenre = this.findWorksInGenre(genre.id);
        const hasWorks = worksInGenre.length > 0;
        const parentGenre = this.getGenreHierarchy(genre.id);

        return generateResultItem({
          meta: formatMetadata([
            `ID: ${genre.id}`,
            hasWorks ? `${worksInGenre.length} Werke` : null,
            parentGenre ? `Einordnung: ${parentGenre}` : null,
          ]),
          title: genre.termDE || genre.termEN,
          // #119: genres without assigned works get a placeholder note + dimmed card
          subtitle: hasWorks ? "" : "Noch keine Werke in der MHDBDB zugeordnet",
          dimmed: !hasWorks,
          buttons: hasWorks
            ? [
                {
                  text: "Werke anzeigen",
                  action: `window.playground.ui.authorityExplorers.showWorksInGenre('${
                    genre.id
                  }', '${escapeForJS(genre.termDE || genre.termEN)}')`,
                },
                {
                  text: "Autor*innen anzeigen",
                  action: `window.playground.ui.authorityExplorers.showAuthorsInGenre('${
                    genre.id
                  }', '${escapeForJS(genre.termDE || genre.termEN)}')`,
                },
              ]
            : [],
          detailsId: `genre-details-${genre.id}`,
        });
      })
      .join("");

    renderToContainer("genreResults", result.headerHTML + resultHTML);
  }

  showWorksInGenre(genreId, genreName) {
    toggleDetails(`genre-details-${genreId}`, () => {
      const worksInGenre = this.findWorksInGenre(genreId);

      if (worksInGenre.length === 0) {
        return "Keine Werke in dieser Gattung gefunden.";
      }

      const worksHTML = worksInGenre
        .slice(0, 20)
        .map(
          (work) => `
            <div style="margin-bottom: 3px; font-size: 0.85rem;">
                • <strong>${work.title}</strong>${
            work.sigle ? ` (${work.sigle})` : ""
          }
                <span style="color: #475569;">von ${work.author}</span>
            </div>
        `
        )
        .join("");

      return `
            <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">
                ${worksInGenre.length} Werke in "${genreName}"${
        worksInGenre.length > 20 ? " (erste 20)" : ""
      }:
            </div>
            ${worksHTML}
        `;
    }, undefined, 'works');
  }

  showAuthorsInGenre(genreId, genreName) {
    const worksInGenre = this.findWorksInGenre(genreId);
    const authorsInGenre = [...new Set(worksInGenre.map((w) => w.author))];

    toggleDetails(`genre-details-${genreId}`, () => {
      if (authorsInGenre.length === 0) {
        return "Keine Autor*innen in dieser Gattung gefunden.";
      }

      const authorsHTML = authorsInGenre
        .slice(0, 15)
        .map((author) => {
          const worksCount = worksInGenre.filter(
            (w) => w.author === author
          ).length;
          return `
                <div style="margin-bottom: 3px; font-size: 0.85rem;">
                    • <strong>${author}</strong> (${worksCount} ${
            worksCount === 1 ? "Werk" : "Werke"
          })
                </div>
            `;
        })
        .join("");

      return `
            <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">
                ${authorsInGenre.length} Autor*innen in "${genreName}"${
        authorsInGenre.length > 15 ? " (erste 15)" : ""
      }:
            </div>
            ${authorsHTML}
        `;
    }, undefined, 'authors');
  }

  findWorksInGenre(genreId) {
    const workIds =
      window.playground.authorityManager.indexes.genreToWorks.get(genreId) ||
      [];

    return workIds
      .map((workId) => this.authorityData.works.find((w) => w.id === workId))
      .filter(Boolean);
  }

  /**
   * Where a genre sits, for the one line a search result has room for.
   *
   * Until #361 this joined all ancestors with " UND ", which on the deepest
   * categories produced a 408-character line of 20 unordered names. It now
   * shows one path from the root and says how many further ones exist.
   */
  getGenreHierarchy(genreId) {
    const pfade = this.pathsTo(genreId);
    if (!pfade.length || pfade[0].length < 2) return null;

    const erster = this.formatPath(pfade[0].slice(0, -1));
    return pfade.length > 1
      ? `${erster} <span class="text-slate-500">(+${pfade.length - 1} weitere)</span>`
      : erster;
  }
}
