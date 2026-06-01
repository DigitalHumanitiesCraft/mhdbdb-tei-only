/**
 * MHDBDB Playground - Authority UI Coordinator
 * Central coordinator for all authority file explorers
 */

import { PersonExplorer } from './person-explorer.js';
import { WorkExplorer } from './work-explorer.js';
import { LemmaExplorer } from './lemma-explorer.js';
import { ConceptExplorer } from './concept-explorer.js';
import { GenreExplorer } from './genre-explorer.js';
import { NameExplorer } from './name-explorer.js';

export class AuthorityUI {
  constructor(authorityData) {
    this.authorityData = authorityData;

    // Initialize all explorers
    this.personExplorer = new PersonExplorer(authorityData);
    this.workExplorer = new WorkExplorer(authorityData);
    this.lemmaExplorer = new LemmaExplorer(authorityData);
    this.conceptExplorer = new ConceptExplorer(authorityData);
    this.genreExplorer = new GenreExplorer(authorityData);
    this.nameExplorer = new NameExplorer(authorityData);
  }

  // ==================== PERSON/AUTHOR METHODS ====================

  showAuthors() {
    this.personExplorer.showAuthors();
  }

  showAllAuthors() {
    this.personExplorer.showAllAuthors();
  }

  showAuthorsWithSearch() {
    this.personExplorer.showAuthorsWithSearch();
  }

  searchAuthorFromWork(authorName) {
    this.personExplorer.searchAuthorFromWork(authorName);
  }

  searchAuthors(searchTerm) {
    this.personExplorer.searchAuthors(searchTerm);
  }

  showWorksByAuthor(authorId, authorName) {
    this.personExplorer.showWorksByAuthor(authorId, authorName);
  }

  // ==================== WORK METHODS ====================

  showWorks() {
    this.workExplorer.showWorks();
  }

  showWorksWithSearch() {
    this.workExplorer.showWorksWithSearch();
  }

  searchWorks(searchTerm) {
    this.workExplorer.searchWorks(searchTerm);
  }

  showWorkDetails(workId, workTitle) {
    this.workExplorer.showWorkDetails(workId, workTitle);
  }

  toggleAlternateTitles(workId) {
    this.workExplorer.toggleAlternateTitles(workId);
  }

  getWorkDetailsFromXML(workId) {
    return this.workExplorer.getWorkDetailsFromXML(workId);
  }

  getWorkGenre(workId) {
    return this.workExplorer.getWorkGenre(workId);
  }

  // ==================== LEMMA METHODS ====================

  showLemmata() {
    this.lemmaExplorer.showLemmata();
  }

  showAllLemmata() {
    this.lemmaExplorer.showAllLemmata();
  }

  showLemmataWithSearch() {
    this.lemmaExplorer.showLemmataWithSearch();
  }

  searchLemmata(searchTerm) {
    this.lemmaExplorer.searchLemmata(searchTerm);
  }

  showLemmaSenses(lemmaId) {
    this.lemmaExplorer.showLemmaSenses(lemmaId);
  }

  showComponentLemma(originalLemmaId, componentLemmaId, componentText) {
    this.lemmaExplorer.showComponentLemma(originalLemmaId, componentLemmaId, componentText);
  }

  generateLemmaSenseContent(lemma, lemmaId, originalLemmaId = null) {
    return this.lemmaExplorer.generateLemmaSenseContent(lemma, lemmaId, originalLemmaId);
  }

  // ==================== CONCEPT METHODS ====================

  showConcepts() {
    this.conceptExplorer.showConcepts();
  }

  showAllConcepts() {
    this.conceptExplorer.showAllConcepts();
  }

  showConceptsWithSearch() {
    this.conceptExplorer.showConceptsWithSearch();
  }

  searchConcepts(searchTerm) {
    this.conceptExplorer.searchConcepts(searchTerm);
  }

  showLemmasWithConcept(conceptId, conceptName, detailsId) {
    // detailsId is optional: the name-explorer passes a namespaced container id
    // (lemmas-<nameId>-<conceptId>) so two open name cards sharing a concept do
    // not collide; the concept-explorer's own buttons omit it (default applies). See #120.
    this.conceptExplorer.showLemmasWithConcept(conceptId, conceptName, detailsId);
  }

  findLemmasWithConcept(conceptId) {
    return this.conceptExplorer.findLemmasWithConcept(conceptId);
  }

  // ==================== GENRE METHODS ====================

  showGenres() {
    this.genreExplorer.showGenres();
  }

  showAllGenres() {
    this.genreExplorer.showAllGenres();
  }

  showGenresWithSearch() {
    this.genreExplorer.showGenresWithSearch();
  }

  searchGenres(searchTerm) {
    this.genreExplorer.searchGenres(searchTerm);
  }

  showWorksInGenre(genreId, genreName) {
    this.genreExplorer.showWorksInGenre(genreId, genreName);
  }

  showAuthorsInGenre(genreId, genreName) {
    this.genreExplorer.showAuthorsInGenre(genreId, genreName);
  }

  findWorksInGenre(genreId) {
    return this.genreExplorer.findWorksInGenre(genreId);
  }

  getGenreHierarchy(genreId) {
    return this.genreExplorer.getGenreHierarchy(genreId);
  }

  // ==================== NAME METHODS ====================

  showNames() {
    this.nameExplorer.showNames();
  }

  showAllNames() {
    this.nameExplorer.showAllNames();
  }

  showNamesWithSearch() {
    this.nameExplorer.showNamesWithSearch();
  }

  searchNames(searchTerm) {
    this.nameExplorer.searchNames(searchTerm);
  }

  showConceptsForName(nameId, nameText) {
    this.nameExplorer.showConceptsForName(nameId, nameText);
  }

  findConceptsForName(nameId) {
    return this.nameExplorer.findConceptsForName(nameId);
  }
}
