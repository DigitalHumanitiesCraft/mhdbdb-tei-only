/**
 * MHDBDB Playground - Authority Files Manager
 * Handles loading, parsing, and extraction of authority files with IndexedDB caching
 */

import { AuthorityStorageManager } from './authority-storage-manager.js';

export class AuthorityFilesManager {
  constructor(authorityData) {
    this.authorityData = authorityData;
    this.authorityFiles = [
      "persons.xml",
      "works.xml",
      "lexicon.xml",
      "concepts.xml",
      "genres.xml",
      "names.xml",
    ];
    // Performance indexes
    this.indexes = {
      genreToWorks: new Map(),
      workToGenres: new Map(),
      genreHierarchy: new Map(),
      conceptToLemmas: new Map(),
    };
    // Storage manager for caching
    this.storageManager = new AuthorityStorageManager();
    this.loadStats = {
      totalFiles: 0,
      cachedFiles: 0,
      networkFiles: 0,
      failedFiles: 0
    };
  }

  // ==================== AUTHORITY FILES LOADING ====================

  async loadAuthorityFiles() {
    this.updateStatus("🔄", "Lade Authority Files...");

    try {
      // Use batch loading from storage manager
      const results = await this.storageManager.loadAllAuthorityFiles(this.authorityFiles);

      // Update load statistics
      this.loadStats.totalFiles = results.successful.length + results.failed.length;
      this.loadStats.cachedFiles = results.successful.filter(r => r.cached).length;
      this.loadStats.networkFiles = results.successful.filter(r => !r.cached).length;
      this.loadStats.failedFiles = results.failed.length;

      // Process successful loads
      for (const result of results.successful) {
        await this.processAuthorityFileContent(result.filename, result.content, result.cached, result.source);
      }

      // Build performance indexes
      this.buildIndexes();

      const successCount = results.successful.length;
      console.log(
        `✅ Authority Files loaded: ${successCount}/${this.authorityFiles.length} (${this.loadStats.cachedFiles} cached, ${this.loadStats.networkFiles} network)`
      );

      if (results.failed.length > 0) {
        console.warn(`⚠️ Failed to load ${results.failed.length} authority files:`, results.failed.map(f => f.filename));
      }

      return successCount;
    } catch (error) {
      console.error("❌ Error loading authority files:", error);
      throw error;
    }
  }

  //  Index building methods
  buildIndexes() {
    console.log("Building performance indexes...");
    this.buildGenreWorkIndexes();
    this.buildGenreHierarchyIndex();
    this.buildConceptLemmaIndex();
    console.log("Indexes built successfully");
  }

  buildGenreWorkIndexes() {
    const worksXML = this.authorityData.parsedXML.find((xml) =>
      xml.filename.includes("works")
    );

    if (!worksXML) return;

    const allBibls = worksXML.doc.querySelectorAll("bibl");
    const works = Array.from(allBibls).filter((bibl) => {
      const id = bibl.getAttribute("xml:id");
      return id && id.startsWith("work_");
    });

    works.forEach((workElement) => {
      const workId = workElement.getAttribute("xml:id");
      const genreRefs = workElement.querySelectorAll(
        'ref[target*="genres.xml#"]'
      );

      const workGenres = [];
      const processedGenres = new Set(); // Prevent duplicates within same work

      genreRefs.forEach((ref) => {
        const target = ref.getAttribute("target");
        if (target) {
          const genreId = target.split("#")[1];

          // Only process each genre once per work
          if (!processedGenres.has(genreId)) {
            processedGenres.add(genreId);
            workGenres.push(genreId);

            // Build genre → works mapping
            if (!this.indexes.genreToWorks.has(genreId)) {
              this.indexes.genreToWorks.set(genreId, []);
            }
            this.indexes.genreToWorks.get(genreId).push(workId);
          }
        }
      });

      // Build work → genres mapping
      if (workGenres.length > 0) {
        this.indexes.workToGenres.set(workId, workGenres);
      }
    });
  }

  buildGenreHierarchyIndex() {
    const genresXML = this.authorityData.parsedXML.find((xml) =>
      xml.filename.includes("genres")
    );

    if (!genresXML) return;

    const categories = Array.from(
      genresXML.doc.querySelectorAll("category")
    ).filter((cat) => {
      const id = cat.getAttribute("xml:id");
      return id && id.includes("genre_");
    });

    categories.forEach((category) => {
      const genreId = category.getAttribute("xml:id");
      const parentPtrs = category.querySelectorAll('ptr[type="broader"]');

      if (parentPtrs.length > 0) {
        const parentNames = [];

        parentPtrs.forEach((parentPtr) => {
          const parentTarget = parentPtr.getAttribute("target");
          if (parentTarget) {
            const parentId = parentTarget.replace("#", "");
            const parentGenre = this.authorityData.genres.find(
              (g) => g.id === parentId
            );
            if (parentGenre) {
              parentNames.push(parentGenre.termDE || parentGenre.termEN);
            }
          }
        });

        if (parentNames.length > 0) {
          this.indexes.genreHierarchy.set(genreId, parentNames);
        }
      }
    });
  }

  buildConceptLemmaIndex() {
    const lexiconXML = this.authorityData.parsedXML.find((xml) =>
      xml.filename.includes("lexicon")
    );

    if (!lexiconXML) return;

    const entries = lexiconXML.doc.querySelectorAll("entry");

    entries.forEach((entry) => {
      const lemmaId = entry.getAttribute("xml:id");
      const conceptPtrs = entry.querySelectorAll(
        'ptr[target*="concepts.xml#"]'
      );

      conceptPtrs.forEach((ptr) => {
        const target = ptr.getAttribute("target");
        if (target) {
          const conceptId = target.split("#")[1];

          if (!this.indexes.conceptToLemmas.has(conceptId)) {
            this.indexes.conceptToLemmas.set(conceptId, []);
          }
          this.indexes.conceptToLemmas.get(conceptId).push(lemmaId);
        }
      });
    });
  }

  async processAuthorityFileContent(filename, content, cached = false, source = 'Unknown') {
    try {
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(content, "text/xml");

      const parseError = xmlDoc.querySelector("parsererror");
      if (parseError) {
        throw new Error(`XML Parse Error: ${parseError.textContent}`);
      }

      this.authorityData.files.push(filename);
      this.authorityData.parsedXML.push({
        filename: filename,
        doc: xmlDoc,
        content: content,
        cached: cached,
        source: source
      });

      this.analyzeAuthorityFile(xmlDoc, filename);

      const statusIcon = cached ? "📁" : "🌐";
      this.updateStatus(statusIcon, `${filename} geladen (${source})`);
    } catch (error) {
      console.error(`❌ Error processing ${filename}:`, error);
      throw error;
    }
  }

  analyzeAuthorityFile(xmlDoc, filename) {
    // Detect file type and extract data accordingly
    if (filename.includes("persons") || xmlDoc.querySelector("listPerson")) {
      this.extractPersons(xmlDoc);
    } else if (filename.includes("works") || xmlDoc.querySelector("listBibl")) {
      this.extractWorks(xmlDoc);
    } else if (filename.includes("lexicon") || xmlDoc.querySelector("entry")) {
      this.extractLemmata(xmlDoc);
    } else if (
      filename.includes("concepts") ||
      this.hasConceptCategories(xmlDoc)
    ) {
      this.extractConcepts(xmlDoc);
    } else if (filename.includes("genres") || this.hasGenreCategories(xmlDoc)) {
      this.extractGenres(xmlDoc);
    } else if (filename.includes("names") || this.hasNameCategories(xmlDoc)) {
      this.extractNames(xmlDoc);
    } else {
      console.warn(`Unknown authority file structure: ${filename}`);
    }
  }

  // Helper methods for better detection
  hasConceptCategories(xmlDoc) {
    return xmlDoc.querySelector('category[xml\\:id*="concept"]') !== null;
  }

  hasGenreCategories(xmlDoc) {
    return xmlDoc.querySelector('category[xml\\:id*="genre"]') !== null;
  }

  hasNameCategories(xmlDoc) {
    return xmlDoc.querySelector('category[xml\\:id*="name"]') !== null;
  }

  // ==================== DATA EXTRACTION METHODS ====================

  extractPersons(xmlDoc) {
    const persons = xmlDoc.querySelectorAll("person");
    let extracted = 0;

    persons.forEach((person) => {
      const id = person.getAttribute("xml:id");
      const preferredName = person
        .querySelector('persName[type="preferred"]')
        ?.textContent?.trim();
      const gnd = person.querySelector('idno[type="GND"]')?.textContent?.trim();
      const wikidata = person
        .querySelector('idno[type="wikidata"]')
        ?.textContent?.trim();
      const works = person
        .querySelector('note[type="works"]')
        ?.textContent?.trim();

      if (id && preferredName) {
        this.authorityData.persons.push({
          id,
          preferredName,
          gnd,
          wikidata,
          works,
        });
        extracted++;
      }
    });

    console.log(`Persons extracted: ${extracted}`);
  }

  extractWorks(xmlDoc) {
    const allBibls = xmlDoc.querySelectorAll("bibl");
    const works = Array.from(allBibls).filter((bibl) => {
      const id = bibl.getAttribute("xml:id");
      return id && id.startsWith("work_");
    });

    let extracted = 0;

    works.forEach((work) => {
      const id = work.getAttribute("xml:id");
      const titleElement = work.querySelector(":scope > title");
      const title = titleElement?.textContent?.trim();

      // Extract ALL sigle values
      const sigleElements = work.querySelectorAll('idno[type="sigle"]');
      const sigles = Array.from(sigleElements)
        .map((s) => s.textContent?.trim())
        .filter(Boolean);
      const sigle = sigles.length > 0 ? sigles.join(", ") : null;

      const authorRef = work.querySelector("author")?.getAttribute("ref");
      const authorText = work.querySelector("author")?.textContent?.trim();
      const author = authorText || authorRef;

      if (id && title) {
        this.authorityData.works.push({
          id,
          title,
          sigle,
          author: author || "Unbekannt",
        });
        extracted++;
      }
    });

    console.log(`Works extracted: ${extracted}`);
  }

  extractLemmata(xmlDoc) {
    const entries = xmlDoc.querySelectorAll("entry");
    let extracted = 0;

    entries.forEach((entry) => {
      const id = entry.getAttribute("xml:id");
      const lemma = entry
        .querySelector('form[type="lemma"] orth')
        ?.textContent?.trim();
      const pos = entry.querySelector("pos")?.textContent?.trim();
      const senses = entry.querySelectorAll("sense");

      if (id && lemma) {
        this.authorityData.lemmata.push({
          id,
          lemma,
          pos,
          senseCount: senses.length,
        });
        extracted++;
      }
    });

    console.log(`Lemmata extracted: ${extracted}`);
  }

  extractConcepts(xmlDoc) {
    const categories = this.extractTaxonomyCategories(xmlDoc, "concept_");
    this.authorityData.concepts = categories;
    console.log(`Concepts extracted: ${categories.length}`);
  }

  extractGenres(xmlDoc) {
    const categories = this.extractTaxonomyCategories(xmlDoc, "genre_");
    this.authorityData.genres = categories;
    console.log(`Genres extracted: ${categories.length}`);
  }

  extractNames(xmlDoc) {
    const categories = this.extractTaxonomyCategories(xmlDoc, "name_");
    this.authorityData.names = categories;
    console.log(`Names extracted: ${categories.length}`);
  }

  // Unified extraction for taxonomy-based authority files (concepts, genres, names)
  extractTaxonomyCategories(xmlDoc, idPrefix) {
    const categories = xmlDoc.querySelectorAll("category");
    const results = [];

    // Filter categories by ID prefix
    const filteredCategories = Array.from(categories).filter((cat) => {
      const id = cat.getAttribute("xml:id");
      return id && id.includes(idPrefix);
    });

    filteredCategories.forEach((category) => {
      const id = category.getAttribute("xml:id");
      const catDesc = category.querySelector("catDesc");

      if (catDesc) {
        // TEI namespace fix: Manual filtering for xml:lang attributes
        const allTerms = Array.from(catDesc.querySelectorAll("term"));
        const termDE = allTerms
          .find((t) => t.getAttribute("xml:lang") === "de")
          ?.textContent?.trim();
        const termEN = allTerms
          .find((t) => t.getAttribute("xml:lang") === "en")
          ?.textContent?.trim();

        if (id && (termDE || termEN)) {
          results.push({ id, termDE, termEN });
        }
      }
    });

    return results;
  }

  // ==================== CROSS-REFERENCE HELPERS ====================

  findLemmaInXML(lemmaId) {
    const lexiconXML = this.authorityData.parsedXML.find((xml) =>
      xml.filename.includes("lexicon")
    );

    if (!lexiconXML) return null;

    // TEI namespace fix: Manual filtering instead of CSS selector
    const allEntries = lexiconXML.doc.querySelectorAll("entry");
    return Array.from(allEntries).find((entry) => {
      const id = entry.getAttribute("xml:id");
      return id === lemmaId;
    });
  }

  findWorksInGenre(genreId) {
    // Find works that reference this genre
    const matchingWorks = this.authorityData.works.filter((work) => {
      // Check if any work references this genre
      const worksXML = this.authorityData.parsedXML.find((xml) =>
        xml.filename.includes("works")
      );

      if (!worksXML) return false;

      // Find the work element in XML
      const workElement = Array.from(
        worksXML.doc.querySelectorAll("bibl")
      ).find((bibl) => {
        const id = bibl.getAttribute("xml:id");
        return id === work.id;
      });

      if (!workElement) return false;

      // Check if this work has a ref to our genre
      const genreRefs = workElement.querySelectorAll(
        'ref[target*="genres.xml#"]'
      );
      return Array.from(genreRefs).some((ref) => {
        const target = ref.getAttribute("target");
        return target && target.includes(genreId);
      });
    });

    return matchingWorks;
  }

  // ==================== LEMMA RESOLUTION ====================

  resolveLemmaNames(searchTerms) {
    const resolvedLemmas = [];
    
    searchTerms.forEach(term => {
      // Check if it's already a lemma ID
      if (/^lemma_\d+$/.test(term) || /^\d+$/.test(term)) {
        const lemmaId = term.replace('lemma_', '');
        const lemma = this.authorityData.lemmata.find(l => l.id === `lemma_${lemmaId}`);
        if (lemma) {
          resolvedLemmas.push({
            input: term,
            lemmaId: lemmaId,
            lemma: lemma
          });
        }
        return;
      }
      
      // Search by orthography
      const normalizedTerm = term.toLowerCase();
      const matchingLemma = this.authorityData.lemmata.find(l => 
        l.lemma && l.lemma.toLowerCase() === normalizedTerm
      );
      
      if (matchingLemma) {
        resolvedLemmas.push({
          input: term,
          lemmaId: matchingLemma.id.replace('lemma_', ''),
          lemma: matchingLemma
        });
      }
    });
    
    return resolvedLemmas;
  }

  searchLemmaByOrthography(orthography) {
    const normalized = orthography.toLowerCase();
    return this.authorityData.lemmata.filter(lemma => 
      lemma.lemma && lemma.lemma.toLowerCase().includes(normalized)
    );
  }

  findLemmaById(lemmaId) {
    return this.authorityData.lemmata.find(l => 
      l.id === `lemma_${lemmaId}` || l.id === lemmaId
    );
  }

  getLemmaSuggestions(partialInput, maxSuggestions = 10) {
    const normalized = partialInput.toLowerCase();
    return this.authorityData.lemmata
      .filter(lemma => 
        lemma.lemma && lemma.lemma.toLowerCase().startsWith(normalized)
      )
      .slice(0, maxSuggestions)
      .map(lemma => ({
        lemma: lemma.lemma,
        id: lemma.id.replace('lemma_', ''),
        pos: lemma.pos
      }));
  }

  // ==================== UTILITY METHODS ====================

  updateStatus(indicator, text) {
    const statusIndicator = document.getElementById("statusIndicator");
    const statusText = document.getElementById("statusText");

    if (statusIndicator) statusIndicator.textContent = indicator;
    if (statusText) statusText.textContent = text;

    // Enhanced logging with cache information
    console.log(`${indicator} ${text}`);
  }

  // ==================== CACHE MANAGEMENT ====================

  async getCacheStatus() {
    return await this.storageManager.getCacheStatus();
  }

  async clearCache() {
    const cleared = await this.storageManager.clearCache();
    if (cleared) {
      console.log('🧹 Authority files cache cleared');
    }
    return cleared;
  }

  async clearExpiredCache() {
    const removedCount = await this.storageManager.clearExpired();
    if (removedCount > 0) {
      console.log(`🧹 Removed ${removedCount} expired authority files from cache`);
    }
    return removedCount;
  }

  getLoadStatistics() {
    return {
      ...this.loadStats,
      cacheHitRate: this.loadStats.totalFiles > 0 ?
        Math.round((this.loadStats.cachedFiles / this.loadStats.totalFiles) * 100) : 0
    };
  }

  // Enhanced search with caching awareness
  async refreshAuthorityFile(filename) {
    try {
      // Remove from cache and reload
      await this.storageManager.removeCachedFile(filename);

      // Remove from current data
      this.authorityData.files = this.authorityData.files.filter(f => f !== filename);
      this.authorityData.parsedXML = this.authorityData.parsedXML.filter(x => x.filename !== filename);

      // Reload from network
      const result = await this.storageManager.loadAuthorityFile(filename);
      if (result.success) {
        await this.processAuthorityFileContent(filename, result.content, false, 'Network (refreshed)');
        // Rebuild indexes if needed
        this.buildIndexes();
        console.log(`🔄 Authority file refreshed: ${filename}`);
        return true;
      }
      return false;
    } catch (error) {
      console.error(`❌ Failed to refresh ${filename}:`, error);
      return false;
    }
  }

  // ==================== DEBUG INFORMATION ====================

  async getStorageDebugInfo() {
    const storageStats = await this.storageManager.getStorageStats();
    const loadStats = this.getLoadStatistics();

    return {
      loadStats,
      storageStats,
      authorityFiles: this.authorityFiles,
      loadedFiles: this.authorityData.files,
      indexSizes: {
        genreToWorks: this.indexes.genreToWorks.size,
        workToGenres: this.indexes.workToGenres.size,
        genreHierarchy: this.indexes.genreHierarchy.size,
        conceptToLemmas: this.indexes.conceptToLemmas.size
      }
    };
  }
}
