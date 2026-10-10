/**
 * MHDBDB Playground - Authority Files Manager
 * Handles building performance indexes from pre-loaded authority data
 * NOTE: Authority data is now loaded via pre-built index (authority-index.json.gz)
 *       in main.js using CorpusLoader, not via XML files anymore.
 */

import { TextNormalizer } from '../../../assets/js/lib/text-normalizer.js';
import { isStage3Match, stage3Distance, stage1Holds } from '../../../assets/js/lib/lemma-resolve.js';

// Einmal angelegt statt je Vergleich `localeCompare(b, 'de')` (#564); gleiche Ordnung
const AUTOCOMPLETE_COLLATOR = new Intl.Collator('de');

export class AuthorityFilesManager {
  constructor(authorityData) {
    this.authorityData = authorityData;

    // Performance indexes (built from pre-loaded data)
    this.indexes = {
      genreToWorks: new Map(),
      workToGenres: new Map(),
      conceptToLemmas: new Map(),
    };
  }

  // ==================== PERFORMANCE INDEXES (NEW - FROM PRE-LOADED DATA) ====================

  /**
   * Build performance indexes from pre-loaded authority data
   * Called after authority index is loaded in main.js
   */
  buildPerformanceIndexes() {
    console.log('[AuthorityFilesManager] Building performance indexes from pre-loaded data...');

    // These indexes are optional - if data is missing, skip
    try {
      // Build genre-work mappings (if we have the data)
      // NOTE: Currently not available in pre-built index
      // Could be added in future versions

      // Build concept-lemma mappings (if needed for concept searches)
      // NOTE: Currently not needed as concept search doesn't use this

      console.log('[AuthorityFilesManager] Performance indexes built (optional indexes skipped)');
    } catch (error) {
      console.warn('[AuthorityFilesManager] Error building performance indexes:', error);
    }
  }

  // ==================== LEMMA RESOLUTION ====================

  /**
   * Nachschlagetafeln ueber das Lemma-Array (#564), einmal je geladenem Array
   * statt einmal je Aufloesung. Vorher normalisierte jede Suche alle rund
   * 44.000 Lemmata neu (Stufe 1 und 3) und suchte per `find` nach IDs; das
   * kostete im Playground ein Vielfaches der Hauptseite. Die Tafeln haengen
   * an der Identitaet des Arrays (und seiner Laenge): wer `lemmata` ersetzt
   * oder anhaengt, bekommt neue; wer ein Element in place aendert, nicht
   * (playground-main.js weist das Array nur einmal zu).
   *
   * `first`/`last`: Index der ersten/letzten Zeile je ID, weil `find` den
   * ersten Treffer nimmt, die Kandidatenabbildung in Stufe 2 aber den letzten
   * (gemessen 10.10.2026: 0 doppelte IDs, das Verhalten bleibt trotzdem
   * erhalten). `lower`/`norm`: Indizes je Kleinschreibung bzw. je
   * normalisierter Form, aufsteigend. `normArr`: Stufe-3-Form je Zeile, ''
   * ohne `lemma.lemma`.
   */
  getLemmaTables() {
    const lemmata = this.authorityData.lemmata;
    const t = this._lemmaTables;
    if (t && t.source === lemmata && t.length === lemmata.length) return t;
    const first = new Map();
    const last = new Map();
    const lower = new Map();
    const norm = new Map();
    const normArr = new Array(lemmata.length);
    const push = (map, key, idx) => {
      const list = map.get(key);
      if (list) list.push(idx); else map.set(key, [idx]);
    };
    lemmata.forEach((l, idx) => {
      if (!first.has(l.id)) first.set(l.id, idx);
      last.set(l.id, idx);
      if (!l.lemma) {
        normArr[idx] = '';
        return;
      }
      const lw = l.lemma.toLowerCase();
      const n = TextNormalizer.normalizeMHG(lw);
      normArr[idx] = n;
      push(lower, lw, idx);
      push(norm, n, idx);
    });
    this._lemmaTables = { source: lemmata, length: lemmata.length, first, last, lower, norm, normArr };
    return this._lemmaTables;
  }

  /** Gibt es ueberhaupt Varianten? Einmal je Objekt, nicht je Aufloesung (O(n)). */
  hasVariants() {
    const variants = this.authorityData.variants;
    if (variants !== this._variantsSeen) {
      this._variantsSeen = variants;
      this._variantsUsable = !!variants && Object.keys(variants).length > 0;
    }
    return this._variantsUsable;
  }

  resolveLemmaNames(searchTerms) {
    const resolvedLemmas = [];
    const tables = this.getLemmaTables();
    const lemmata = this.authorityData.lemmata;

    searchTerms.forEach(term => {
      // Check if it's already a lemma ID
      if (/^lemma_\d+$/.test(term) || /^\d+$/.test(term)) {
        const lemmaId = term.replace('lemma_', '');
        const lemma = lemmata[tables.first.get(`lemma_${lemmaId}`)];
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
      const matchingLemma = lemmata[tables.lower.get(normalizedTerm)?.[0]];
      
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
    const normalizedCharacters = TextNormalizer.normalizeMHG(normalized);

    // Stage 1: Exact match in lexicon (canonical forms). Sammelt ALLE
    // Homographen (z.B. rôt: NAM lemma_11330, NOM lemma_19417, ADJ
    // lemma_4954) statt nur den ersten Array-Treffer — matches[0]-Konsumenten
    // (Multi-Lemma-Suche, Kookkurrenz, Reim, Versposition) bekamen sonst
    // je nach Index-Reihenfolge einen 1-Beleg-Eigennamen statt des
    // hochfrequenten Appellativs (#163/#164). Sortierung: Korpus-Frequenz
    // absteigend, bei Gleichstand diakritisch-exakte Eingabe zuerst.
    // Ueber die Tafeln statt eines Laufs mit Normalisierung je Lemma (#564);
    // Indizes beider Treffermengen, dedupliziert und in Array-Reihenfolge.
    const tables = this.getLemmaTables();
    const lemmataAll = this.authorityData.lemmata;
    const byLower = tables.lower.get(normalized);
    const byNorm = tables.norm.get(normalizedCharacters);
    let exactIdx;
    if (!byLower) exactIdx = byNorm || [];
    else if (!byNorm) exactIdx = byLower;
    else exactIdx = [...new Set([...byLower, ...byNorm])].sort((a, b) => a - b);
    const exactMatches = exactIdx.map(i => lemmataAll[i]);
    // Stufe 1 haelt nur mit mindestens einem belegten Treffer (#463, wie die
    // Hauptseite). Sonst wird Stufe 2 mitgefragt (Stufe 3 bleibt den Eingaben
    // vorbehalten, die in Stufe 1 und 2 nichts finden) und die unbelegten
    // Stufe-1-Treffer bleiben in der Liste. Ohne geladenen Corpus-Index
    // gilt alles als belegt (altes Verhalten).
    const lemmaIndex = this.getAttestationIndex();
    if (stage1Holds(exactMatches.map(l => l.id), lemmaIndex)) {
      return this.rankHomographs(exactMatches, normalized);
    }
    // Die unbelegten Stufe-1-Treffer stehen HINTEN: matches[0]-Konsumenten
    // (Multi-Lemma-Suche, Kookkurrenz, Reim, Versposition) duerfen nicht ein
    // Lemma ohne Beleg als ersten Treffer nehmen (#163/#164).
    const withStage1 = (found) => {
      const seen = new Set(exactMatches);
      return [...found.filter(l => !seen.has(l)), ...this.rankHomographs(exactMatches, normalized)];
    };

    // Stage 2: Search in variants index (orthographic variants from TEI corpus)
    // Structure: variants = {normalized_variant: lemma_id, ...}
    // Die Leerpruefung ist O(n) ueber 234.264 Schluessel (gemessen 10.10.2026
    // ca. 37 ms im Node-Skript des Subagenten, #564) und laeuft deshalb einmal
    // je Objekt (hasVariants), nicht je Aufloesung.
    if (this.hasVariants()) {
      // Mehrere Kandidaten (ADR-021, #378): alle, geordnet nach Vorschrift B
      // (Tokens DIESER Form unter dem Lemma); matches[0]-Konsumenten nehmen
      // damit den haeufigsten, die uebrigen bleiben erhalten.
      const candidateIds = this.authorityData.variantCandidates?.[normalizedCharacters];
      if (Array.isArray(candidateIds)) {
        // Letzte Zeile je ID, wie die frühere Schleife mit Map.set (Überschreiben)
        const candidates = candidateIds.map(id => lemmataAll[tables.last.get(id)]).filter(Boolean);
        if (candidates.length > 0) {
          return exactMatches.length === 0 ? candidates : withStage1(candidates);
        }
      }

      // Try normalized lookup in variants dictionary
      const lemmaId = this.authorityData.variants[normalizedCharacters];

      if (lemmaId) {
        // Find the corresponding lemma in lemmata array
        const lemma = lemmataAll[tables.first.get(lemmaId)];
        if (lemma) {
          return exactMatches.length === 0 ? [lemma] : withStage1([lemma]);
        }
      }
    }

    // Unbelegter Stufe 1 ohne Stufe 2: wie vor #463 bleibt es bei Stufe 1.
    if (exactMatches.length > 0) return this.rankHomographs(exactMatches, normalized);

    // Stage 3: Partial-Match-Fallback, praefixorientiert in beide Richtungen
    // (Stamm-Eingabe -> Lemma, flektierte Eingabe -> Lemma). Regel und
    // Begruendung: assets/js/lib/lemma-resolve.js, Vertrag: CONTRACTS.md §C.
    //
    // Vorher stand hier ein einseitiger Infix-Test (Lemma enthaelt Eingabe),
    // die Hauptseite testete bidirektional — dieselbe Eingabe lieferte je nach
    // Oberflaeche andere Mengen (#169 Punkt #45). Seit #224 teilen sich beide
    // dasselbe Praedikat. Die Infix-Discovery ("lantwin" enthaelt "win", was
    // hier keinen Treffer mehr gibt, sofern eine Eingabe Stufe 3 ueberhaupt
    // erreicht: "win" ist selbst Lemma und bricht oben bei Stufe 1 ab) faellt
    // dabei bewusst weg; sie war der Traeger des #224-Rauschens.
    //
    // Sortierung wie bei den Homographen: erst Naehe zur Eingabe, dann
    // Korpus-Frequenz, damit matches[0]-Konsumenten (Multi-Lemma-Suche,
    // Kookkurrenz, Reim, Versposition) nicht wieder einen 1-Beleg-Eigennamen
    // vor das hochfrequente Appellativ gesetzt bekommen (#163/#164).
    const partialMatches = lemmataAll
      .map((lemma, idx) => ({
        lemma,
        idx,
        norm: tables.normArr[idx]
      }))
      .filter(entry => isStage3Match(entry.norm, normalizedCharacters))
      .sort((a, b) =>
        (stage3Distance(a.norm, normalizedCharacters) - stage3Distance(b.norm, normalizedCharacters))
        || (this.getCorpusFrequency(b.lemma.id) - this.getCorpusFrequency(a.lemma.id))
        || (a.idx - b.idx)
      )
      .map(entry => entry.lemma);
    return partialMatches;
  }

  /**
   * Der Reverse-Index fuer die Belegregel (#463) oder null, wenn es keinen
   * brauchbaren gibt. playground-main.js faellt bei fehlendem Feld auf `{}`
   * zurueck; ein leeres Objekt ist truthy und wuerde jedes Lemma als
   * unbelegt zaehlen. Die Leerpruefung ist O(n) und laeuft deshalb einmal je
   * geladenem Index-Objekt, nicht je Aufloesung.
   */
  getAttestationIndex() {
    const lemmaIndex = window.playground?.corpusData?.lemmaIndex;
    if (lemmaIndex !== this._attestationSeen) {
      this._attestationSeen = lemmaIndex;
      this._attestationUsable = !!lemmaIndex && Object.keys(lemmaIndex).length > 0;
    }
    return this._attestationUsable ? lemmaIndex : null;
  }

  /**
   * Homographen nach Korpus-Frequenz absteigend sortieren; bei Gleichstand
   * gewinnt die diakritisch-exakte Schreibform der Eingabe, danach bleibt
   * die Index-Reihenfolge stabil. Ist der Corpus-Index noch nicht geladen,
   * sind alle Frequenzen 0 und die bisherige Reihenfolge bleibt erhalten.
   */
  rankHomographs(lemmata, normalizedInput) {
    if (lemmata.length <= 1) return lemmata;
    const decorated = lemmata.map((lemma, idx) => ({
      lemma,
      idx,
      freq: this.getCorpusFrequency(lemma.id),
      exact: lemma.lemma && lemma.lemma.toLowerCase() === normalizedInput ? 0 : 1
    }));
    decorated.sort((a, b) =>
      (b.freq - a.freq) || (a.exact - b.exact) || (a.idx - b.idx)
    );
    return decorated.map(d => d.lemma);
  }

  /**
   * Gesamtzahl der Vorkommen eines Lemmas im Korpus (Summe über alle
   * texts[].lemmata[id]-Positionslisten des Corpus-Index). Ergebnisse werden
   * gecacht — aber erst, sobald der Corpus-Index geladen ist, damit ein
   * früher Aufruf (Autocomplete vor Corpus-Load) keine Nullen einfriert.
   */
  getCorpusFrequency(lemmaId) {
    if (this._corpusFreqCache?.has(lemmaId)) {
      return this._corpusFreqCache.get(lemmaId);
    }
    const texts = window.playground?.corpusData?.texts;
    if (!texts || texts.length === 0) return 0;
    let total = 0;
    for (const t of texts) {
      const positions = t.lemmata?.[lemmaId];
      if (positions) total += positions.length;
    }
    if (!this._corpusFreqCache) this._corpusFreqCache = new Map();
    this._corpusFreqCache.set(lemmaId, total);
    return total;
  }

  findLemmaById(lemmaId) {
    const { first } = this.getLemmaTables();
    const a = first.get(`lemma_${lemmaId}`);
    const b = first.get(lemmaId);
    // find nimmt die erste Zeile, die eine der beiden Formen traegt
    const idx = a === undefined ? b : (b === undefined ? a : Math.min(a, b));
    return this.authorityData.lemmata[idx];
  }

  /**
   * Live-Autocomplete-Suggestions: prefix-match auf `lemma.normalized`
   * (mhd-normalisiert) mit includes-Fallback. Liefert vollständige Lemma-
   * Objekte (`{id, lemma, pos, ...}` mit `lemma_X`-Präfix).
   *
   * Genutzt von lemma-distribution.js, verse-position-search.js,
   * cooccurrence-ranking.js für Live-Dropdown im Lemma-Input. Siehe
   * DESIGN.md §Live autocomplete dropdown.
   *
   * Eingabe wird mit TextNormalizer.normalizeMHG normalisiert (â→a, ê→e,
   * ü→ue, æ→ae, ō→o, …) damit „ere" auch „êre" matcht — derselbe Normalizer,
   * mit dem lemma.normalized gebaut wird (CONTRACTS §A). Linear scan über
   * rund 44.000 Lemmata, ~5-10ms pro Aufruf — akzeptabel für keystroke-Frequenz.
   */
  getLemmaAutocompleteMatches(partialInput, maxSuggestions = 8) {
    const trimmed = (partialInput || '').trim();
    if (!trimmed) return [];
    // Kanonischer Normalizer statt Inline-Regex-Kette: lemma.normalized ist
    // mit normalizeMHG gebaut — eine abweichende Eingabe-Normalisierung
    // (fehlende Ligaturen æ/œ, Makrons ā/ē/ī/ō/ū) liefert für „mære" oder
    // „brōt" sonst keine Vorschläge (#167 Finding 86, CONTRACTS §A).
    const needle = TextNormalizer.normalizeMHG(trimmed);
    const lemmata = this.authorityData?.lemmata || [];
    const startsWith = [];
    const includes = [];
    // Voll-Scan (43k) ohne Early-Break, sonst springen kurze Treffer wie „êre“
    // unter längere wie „êrengir“ weil das Lemma-Array nicht ID-sortiert ist.
    // Tippt jemand weiter, enthält jedes Lemma des neuen Suchworts auch das
    // vorige (Teilstring des Teilstrings): dann reicht ein Scan über die
    // Treffer des vorigen Tastendrucks (#564), in Array-Reihenfolge, damit
    // die stabile Sortierung unten bei Gleichstand dasselbe liefert.
    const cache = this._autocompletePool;
    const pool = cache && cache.source === lemmata && cache.length === lemmata.length
      && needle.startsWith(cache.needle) ? cache.pool : lemmata;
    const hits = [];
    for (const l of pool) {
      if (!l.normalized) continue;
      const ln = l.normalized;
      if (ln.startsWith(needle)) { startsWith.push(l); hits.push(l); }
      else if (ln.includes(needle)) { includes.push(l); hits.push(l); }
    }
    this._autocompletePool = { source: lemmata, length: lemmata.length, needle, pool: hits };
    // Sortierung: exakt-match → kürzere Lemmata → alphabetisch. So steht
    // „êre" über „êrengir" und „minne" über „minnesänger".
    const sortByRelevance = (a, b) => {
      const an = a.normalized;
      const bn = b.normalized;
      const aExact = an === needle ? 0 : 1;
      const bExact = bn === needle ? 0 : 1;
      if (aExact !== bExact) return aExact - bExact;
      if (an.length !== bn.length) return an.length - bn.length;
      return AUTOCOMPLETE_COLLATOR.compare(an, bn);
    };
    // Nur die ersten maxSuggestions werden gebraucht: Auswahl statt Sortierung
    // der ganzen Treffermenge (bei „ê" sind es zehntausende, #564). Bei
    // Gleichstand bleibt die frühere Reihenfolge, wie bei der stabilen Sortierung.
    const top = (liste, k) => {
      const best = [];
      for (const l of liste) {
        if (best.length === k && sortByRelevance(l, best[k - 1]) >= 0) continue;
        let i = best.length;
        while (i > 0 && sortByRelevance(l, best[i - 1]) < 0) i--;
        best.splice(i, 0, l);
        if (best.length > k) best.pop();
      }
      return best;
    };
    if (maxSuggestions <= 0) return [];
    const first = top(startsWith, maxSuggestions);
    if (first.length >= maxSuggestions) return first;
    return [...first, ...top(includes, maxSuggestions - first.length)];
  }

}
