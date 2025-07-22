/**
 * MHDBDB Playground - Authority Files Manager
 * Handles loading, parsing, and extraction of authority files
 */

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
  }

  // ==================== AUTHORITY FILES LOADING ====================

  async loadAuthorityFiles() {
    this.updateStatus("🔄", "Lade Authority Files...");

    const loadPromises = this.authorityFiles.map((filename) =>
      this.loadAuthorityFile(filename).catch((error) => {
        console.warn(`⚠️ Failed to load ${filename}:`, error.message);
        return null; // Continue with other files
      })
    );

    try {
      await Promise.all(loadPromises);
      const successCount = this.authorityData.files.length;

      // Build performance indexes
      this.buildIndexes();

      console.log(
        `✅ Authority Files loaded: ${successCount}/${this.authorityFiles.length}`
      );
      return successCount;
    } catch (error) {
      console.error("❌ Error loading authority files:", error);
      throw error;
    }
  }

  //  Index building methods
  buildIndexes() {
    console.log("🔄 Building performance indexes...");
    this.buildGenreWorkIndexes();
    this.buildGenreHierarchyIndex();
    this.buildConceptLemmaIndex();
    console.log("✅ Indexes built successfully");
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

  async loadAuthorityFile(filename) {
    const response = await fetch(`../authority-files/${filename}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${filename}`);
    }

    const content = await response.text();
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
    });

    this.analyzeAuthorityFile(xmlDoc, filename);
    return xmlDoc;
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
      console.warn(`⚠️ Unknown authority file structure: ${filename}`);
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

    console.log(`👥 Persons extracted: ${extracted}`);
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

    console.log(`📚 Works extracted: ${extracted}`);
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

    console.log(`🔤 Lemmata extracted: ${extracted}`);
  }

  extractConcepts(xmlDoc) {
    const categories = this.extractTaxonomyCategories(xmlDoc, "concept_");
    this.authorityData.concepts = categories;
    console.log(`💭 Concepts extracted: ${categories.length}`);
  }

  extractGenres(xmlDoc) {
    const categories = this.extractTaxonomyCategories(xmlDoc, "genre_");
    this.authorityData.genres = categories;
    console.log(`🎭 Genres extracted: ${categories.length}`);
  }

  extractNames(xmlDoc) {
    const categories = this.extractTaxonomyCategories(xmlDoc, "name_");
    this.authorityData.names = categories;
    console.log(`📛 Names extracted: ${categories.length}`);
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

  // ==================== UTILITY METHODS ====================

  updateStatus(indicator, text) {
    const statusIndicator = document.getElementById("statusIndicator");
    const statusText = document.getElementById("statusText");

    if (statusIndicator) statusIndicator.textContent = indicator;
    if (statusText) statusText.textContent = text;
  }
}
