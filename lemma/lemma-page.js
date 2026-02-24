/**
 * Lemma Page Controller
 * Renders a persistent lemma page from pre-built authority + corpus indexes.
 * URL patterns: /lemma/879, /lemma/?id=879, /lemma/#879
 */

import { CorpusLoader } from '../assets/js/lib/corpus-loader.js';

class LemmaPage {
    constructor() {
        this.corpusLoader = new CorpusLoader('../data');
        this.authorityIndex = null;
        this.corpusIndex = null;

        this.elements = {
            loadingScreen: document.getElementById('loadingScreen'),
            loadingStatus: document.getElementById('loadingStatus'),
            loadingProgress: document.getElementById('loadingProgress'),
            errorDisplay: document.getElementById('errorDisplay'),
            errorMessage: document.getElementById('errorMessage'),
            lemmaContent: document.getElementById('lemmaContent'),
            lemmaTitle: document.getElementById('lemmaTitle'),
            lemmaNormalized: document.getElementById('lemmaNormalized'),
            lemmaPos: document.getElementById('lemmaPos'),
            lemmaId: document.getElementById('lemmaId'),
            copyIdBtn: document.getElementById('copyIdBtn'),
            etymologySection: document.getElementById('etymologySection'),
            etymologyContent: document.getElementById('etymologyContent'),
            sensesSection: document.getElementById('sensesSection'),
            sensesContent: document.getElementById('sensesContent'),
            occurrencesSection: document.getElementById('occurrencesSection'),
            occurrenceCount: document.getElementById('occurrenceCount'),
            occurrencesContent: document.getElementById('occurrencesContent'),
            externalLinks: document.getElementById('externalLinks'),
            variantsSection: document.getElementById('variantsSection'),
            variantsCount: document.getElementById('variantsCount'),
            variantsContent: document.getElementById('variantsContent'),
            compoundsSection: document.getElementById('compoundsSection'),
            compoundsCount: document.getElementById('compoundsCount'),
            compoundsContent: document.getElementById('compoundsContent'),
        };
    }

    /**
     * Extract lemma ID from URL.
     * Supports: /lemma/879, /lemma/?id=879, /lemma/#879
     */
    parseLemmaId() {
        // 1. Try query parameter (?id=879)
        const params = new URLSearchParams(window.location.search);
        if (params.get('id')) {
            return params.get('id').replace(/\/$/, ''); // trim trailing slash
        }

        // 2. Try hash (#879)
        if (window.location.hash && window.location.hash.length > 1) {
            return window.location.hash.slice(1);
        }

        // 3. Try path segment (/lemma/879) — for direct access or after 404 redirect
        const pathParts = window.location.pathname.split('/');
        const lemmaIdx = pathParts.indexOf('lemma');
        if (lemmaIdx !== -1 && lemmaIdx < pathParts.length - 1) {
            const candidate = pathParts[lemmaIdx + 1];
            // Skip 'index.html' or empty segments
            if (candidate && candidate !== 'index.html' && candidate !== '') {
                return candidate;
            }
        }

        return null;
    }

    async init() {
        try {
            const numericId = this.parseLemmaId();

            if (!numericId) {
                this.showError('Keine Lemma-ID angegeben. Bitte verwenden Sie eine URL wie /lemma/879');
                return;
            }

            this.updateLoading('Lade Wörterbuchdaten...', 20);

            // Load authority index (has lemma definitions)
            this.authorityIndex = await this.corpusLoader.loadAuthorityIndex();
            this.updateLoading('Suche Lemma...', 60);

            // Find the lemma
            const lemmaKey = `lemma_${numericId}`;
            const lemma = this.authorityIndex.lemmata.find(l => l.id === lemmaKey);

            if (!lemma) {
                this.showError(`Lemma mit ID ${numericId} wurde nicht gefunden.`);
                return;
            }

            // Update page title
            document.title = `${lemma.lemma} - MHDBDB Lemma`;

            // Render lemma data
            this.renderLemma(lemma);

            // Render variants, compounds, and navigation (from authority index)
            this.renderVariants(lemmaKey);
            this.renderCompounds(lemmaKey);

            // Load corpus index for occurrences (non-blocking)
            this.updateLoading('Lade Belegstellen...', 80);
            try {
                this.corpusIndex = await this.corpusLoader.loadCorpusIndex();
                this.renderOccurrences(lemmaKey);
            } catch (e) {
                console.warn('[LemmaPage] Corpus index unavailable, skipping occurrences:', e.message);
            }

            // Render external links
            this.renderExternalLinks(numericId, lemma);

            // Done — hide loading, show content
            this.updateLoading('Fertig!', 100);
            this.elements.loadingScreen.style.display = 'none';
            this.elements.lemmaContent.classList.remove('hidden');

        } catch (error) {
            console.error('[LemmaPage] Init failed:', error);
            this.showError(`Fehler beim Laden: ${error.message}`);
        }
    }

    renderLemma(lemma) {
        // Title block
        this.elements.lemmaTitle.textContent = lemma.lemma;
        this.elements.lemmaNormalized.textContent = `Normalisiert: ${lemma.normalized}`;
        this.elements.lemmaPos.textContent = lemma.pos || '—';
        this.elements.lemmaId.textContent = lemma.id;

        // Copy ID button
        this.elements.copyIdBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(lemma.id).then(() => {
                this.elements.copyIdBtn.textContent = 'kopiert!';
                setTimeout(() => { this.elements.copyIdBtn.textContent = 'kopieren'; }, 1500);
            });
        });

        // Etymology
        if (lemma.etymology && lemma.etymology.length > 0) {
            this.elements.etymologySection.classList.remove('hidden');
            this.elements.etymologyContent.innerHTML = lemma.etymology.map(comp => {
                const numId = comp.lemmaRef ? comp.lemmaRef.replace('lemma_', '') : null;
                if (numId) {
                    return `<a href="?id=${numId}" class="etymology-link">${comp.text}</a>`;
                }
                return `<span class="etymology-link">${comp.text}</span>`;
            }).join(' <span class="text-slate-300">+</span> ');
        }

        // Senses
        if (lemma.senses && lemma.senses.length > 0) {
            this.elements.sensesSection.classList.remove('hidden');
            this.elements.sensesContent.innerHTML = lemma.senses.map((sense, idx) => {
                const conceptLabels = this.resolveConceptLabels(sense.conceptIds);
                return `
                    <div class="border-l-2 border-brand-200 pl-4">
                        <div class="text-xs text-slate-400 mb-1">Bedeutung ${idx + 1}</div>
                        <div class="text-sm text-slate-700">
                            ${conceptLabels.length > 0
                                ? conceptLabels.map(c => `<span class="inline-block bg-slate-100 px-2 py-0.5 rounded text-xs mr-1 mb-1">${c}</span>`).join('')
                                : '<span class="text-slate-400">Keine Konzeptzuordnung</span>'
                            }
                        </div>
                    </div>
                `;
            }).join('');
        }
    }

    resolveConceptLabels(conceptIds) {
        if (!conceptIds || !this.authorityIndex.concepts) return [];

        return conceptIds.map(cid => {
            const concept = this.authorityIndex.concepts.find(c => c.id === cid);
            if (concept) {
                // Prefer German label, fall back to English
                return concept.termDE || concept.termEN || cid;
            }
            return cid;
        });
    }

    renderOccurrences(lemmaKey) {
        if (!this.corpusIndex || !this.corpusIndex.lemmaIndex) return;

        const textIds = this.corpusIndex.lemmaIndex[lemmaKey];
        if (!textIds || textIds.length === 0) return;

        this.elements.occurrencesSection.classList.remove('hidden');
        this.elements.occurrenceCount.textContent = `(${textIds.length} von ${this.corpusIndex.texts.length} Texten)`;

        // Build occurrence list with frequency data
        const occurrences = textIds.map(textId => {
            const text = this.corpusIndex.texts.find(t => t.id === textId);
            if (!text) return null;

            const positions = text.lemmata?.[lemmaKey] || [];
            return {
                textId,
                title: text.title || textId,
                author: text.author || '',
                frequency: positions.length
            };
        }).filter(Boolean);

        // Sort by frequency (most first)
        occurrences.sort((a, b) => b.frequency - a.frequency);

        this.elements.occurrencesContent.innerHTML = occurrences.map(occ => `
            <div class="occurrence-row">
                <div>
                    <a href="../korpus.html?textId=${encodeURIComponent(occ.textId)}&lemmaIds=${lemmaKey.replace('lemma_', '')}"
                       class="text-sm font-medium text-brand-600 hover:text-brand-800 transition">
                        ${occ.title}
                    </a>
                    ${occ.author ? `<span class="text-xs text-slate-400 ml-2">${occ.author}</span>` : ''}
                </div>
                <span class="text-xs text-slate-400 flex-shrink-0">${occ.frequency}x</span>
            </div>
        `).join('');
    }

    renderExternalLinks(numericId, lemma) {
        const staticLinks = [
            {
                label: 'MHDBDB (alt)',
                url: `https://mhdbdb-old.sbg.ac.at/mhdbdb/App?action=Dic&lid=${numericId}`,
                icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75z"></path></svg>'
            },
            {
                label: 'MWB Online (Trier)',
                url: `https://www.mhdwb-online.de/`,
                icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>'
            },
            {
                label: 'REALonline (IMAREAL)',
                url: `https://realonline.imareal.sbg.ac.at/suche#${encodeURIComponent(JSON.stringify({ s: lemma.normalized }))}`,
                icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z"></path></svg>'
            },
            {
                label: 'Im Korpus suchen',
                url: `../korpus.html?search=${encodeURIComponent(lemma.lemma)}`,
                icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"></path></svg>'
            }
        ];

        this.elements.externalLinks.innerHTML = staticLinks.map(link =>
            `<a href="${link.url}" class="external-link" target="_blank" rel="noopener">
                ${link.icon} ${link.label}
            </a>`
        ).join('');

        // Fetch Wörterbuchnetz entries asynchronously (non-blocking)
        this.fetchWoerterbuchnetz(lemma.normalized);
    }

    /**
     * Query Wörterbuchnetz API for matching lemmata in MHG dictionaries.
     * Searches BMZ, Lexer, LexerN, and FindeB in parallel; renders results or hides section on failure.
     */
    async fetchWoerterbuchnetz(normalizedForm) {
        const wbnetzContainer = document.getElementById('wbnetzLinks');
        if (!wbnetzContainer) return;

        const dictionaries = ['BMZ', 'Lexer', 'LexerN', 'FindeB'];
        const apiBase = 'https://api.woerterbuchnetz.de/open-api/dictionaries';

        try {
            const results = await Promise.allSettled(
                dictionaries.map(sigle =>
                    fetch(`${apiBase}/${sigle}/lemmata/${encodeURIComponent(normalizedForm)}`)
                        .then(r => r.ok ? r.json() : null)
                )
            );

            const entries = [];
            results.forEach((result, i) => {
                if (result.status === 'fulfilled' && result.value?.result_set) {
                    for (const entry of result.value.result_set) {
                        entries.push({
                            sigle: entry.sigle,
                            lemma: this.decodeHtmlEntities(entry.lemma),
                            gram: entry.gram || '',
                            url: entry.wbnetzlink
                        });
                    }
                }
            });

            if (entries.length > 0) {
                document.getElementById('wbnetzSection').classList.remove('hidden');
                const bookIcon = '<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>';
                wbnetzContainer.innerHTML = entries.map(e =>
                    `<a href="${e.url}" class="external-link" target="_blank" rel="noopener">
                        ${bookIcon}
                        <span class="font-semibold text-xs">${e.sigle}</span>
                        ${e.lemma}${e.gram ? ` <span class="text-slate-400 text-xs">(${e.gram})</span>` : ''}
                    </a>`
                ).join('');
            }
        } catch (e) {
            console.warn('[LemmaPage] Wörterbuchnetz API unavailable:', e.message);
        }
    }

    renderVariants(lemmaKey) {
        if (!this.authorityIndex.variants) return;

        // Invert the flat variants map: find all variants pointing to this lemma
        const variantForms = [];
        for (const [variant, targetId] of Object.entries(this.authorityIndex.variants)) {
            if (targetId === lemmaKey) {
                variantForms.push(variant);
            }
        }

        if (variantForms.length === 0) return;

        variantForms.sort();
        this.elements.variantsSection.classList.remove('hidden');
        this.elements.variantsCount.textContent = `(${variantForms.length})`;
        this.elements.variantsContent.innerHTML = variantForms.map(v =>
            `<a href="../korpus.html?search=${encodeURIComponent(v)}"
                class="inline-block bg-slate-100 px-2 py-0.5 rounded text-xs mr-1 mb-1 hover:bg-brand-50 hover:text-brand-700 transition">${v}</a>`
        ).join('');
    }

    renderCompounds(lemmaKey) {
        // Find all lemmata whose etymology references this lemma
        const compounds = this.authorityIndex.lemmata.filter(l =>
            l.etymology && l.etymology.some(comp => comp.lemmaRef === lemmaKey)
        );

        if (compounds.length === 0) return;

        compounds.sort((a, b) => a.lemma.localeCompare(b.lemma));
        this.elements.compoundsSection.classList.remove('hidden');
        this.elements.compoundsCount.textContent = `(${compounds.length})`;
        this.elements.compoundsContent.innerHTML = compounds.map(c => {
            const numId = c.id.replace('lemma_', '');
            return `<a href="?id=${numId}"
                class="inline-block bg-slate-100 px-2 py-0.5 rounded text-xs mr-1 mb-1 hover:bg-brand-50 hover:text-brand-700 transition">${c.lemma}</a>`;
        }).join('');
    }

    decodeHtmlEntities(str) {
        const textarea = document.createElement('textarea');
        textarea.innerHTML = str;
        return textarea.value;
    }

    showError(message) {
        this.elements.loadingScreen.style.display = 'none';
        this.elements.errorDisplay.classList.remove('hidden');
        this.elements.errorMessage.textContent = message;
    }

    updateLoading(message, percent) {
        if (this.elements.loadingStatus) {
            this.elements.loadingStatus.textContent = message;
        }
        if (this.elements.loadingProgress) {
            this.elements.loadingProgress.style.width = `${percent}%`;
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    const page = new LemmaPage();
    page.init();
});
