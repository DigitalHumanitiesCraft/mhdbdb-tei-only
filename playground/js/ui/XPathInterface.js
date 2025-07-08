/**
 * MHDBDB Playground - XPath Interface
 * Handles XPath execution on authority files and TEI texts
 */

import { displayResults } from './UICore.js';

export class XPathInterface {
    constructor(authorityData, teiData) {
        this.authorityData = authorityData;
        this.teiData = teiData;
    }

    // ==================== XPATH EXECUTION ====================

    executeXPath() {
        const xpath = document.getElementById('xpathInput')?.value?.trim();
        const target = document.getElementById('xpathTarget')?.value;

        if (!xpath) {
            this.showError('Bitte geben Sie einen XPath-Ausdruck ein.');
            return;
        }

        try {
            const results = this.performXPathQuery(xpath, target);
            this.displayXPathResults(xpath, target, results);
        } catch (error) {
            this.showError(`XPath Fehler: ${error.message}`);
        }
    }

    performXPathQuery(xpath, target) {
        const results = [];
        let targetData = [];

        // Determine target data based on selection
        switch (target) {
            case 'authority':
                targetData = this.authorityData.parsedXML;
                break;
            case 'tei':
                targetData = this.teiData.parsedXML;
                break;
            default: // 'all'
                targetData = [...this.authorityData.parsedXML, ...this.teiData.parsedXML];
        }

        // Execute XPath on each XML document
        targetData.forEach(xmlData => {
            try {
                const xpathResult = xmlData.doc.evaluate(
                    xpath,
                    xmlData.doc,
                    this.createNamespaceResolver(xmlData.doc),
                    XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
                    null
                );

                for (let i = 0; i < xpathResult.snapshotLength; i++) {
                    const node = xpathResult.snapshotItem(i);
                    results.push({
                        filename: xmlData.filename,
                        node: node,
                        nodeName: node.nodeName,
                        textContent: node.textContent?.trim(),
                        nodeType: this.getNodeTypeDescription(node.nodeType),
                        attributes: this.extractNodeAttributes(node),
                        outerHTML: node.outerHTML?.substring(0, 300)
                    });
                }
            } catch (error) {
                results.push({
                    filename: xmlData.filename,
                    error: `XPath Error: ${error.message}`,
                    nodeName: 'ERROR',
                    textContent: error.message
                });
            }
        });

        return results;
    }

    // ==================== NAMESPACE HANDLING ====================

    createNamespaceResolver(document) {
        return function(prefix) {
            const nsMap = {
                'tei': 'http://www.tei-c.org/ns/1.0',
                'xml': 'http://www.w3.org/XML/1998/namespace'
            };
            return nsMap[prefix] || null;
        };
    }

    // ==================== RESULT DISPLAY ====================

    displayXPathResults(xpath, target, results) {
        const targetDescription = this.getTargetDescription(target);
        
        if (results.length === 0) {
            displayResults(
                `⚡ XPath auf ${targetDescription}: ${xpath}`,
                [{ meta: 'Keine Ergebnisse', snippet: 'Der XPath-Ausdruck ergab keine Treffer.' }]
            );
            return;
        }

        const formattedResults = results.map(result => {
            if (result.error) {
                return {
                    meta: `❌ ${result.filename}`,
                    snippet: result.error
                };
            }

            return {
                meta: this.formatResultMeta(result),
                snippet: this.formatResultSnippet(result)
            };
        });

        displayResults(
            `⚡ XPath auf ${targetDescription}: ${xpath} (${results.length} Treffer)`,
            formattedResults
        );
    }

    formatResultMeta(result) {
        const parts = [result.filename, `Node: ${result.nodeName}`];
        
        if (result.nodeType) {
            parts.push(`Type: ${result.nodeType}`);
        }
        
        if (result.attributes && Object.keys(result.attributes).length > 0) {
            const attrCount = Object.keys(result.attributes).length;
            parts.push(`${attrCount} Attribute`);
        }

        return parts.join(' • ');
    }

    formatResultSnippet(result) {
        let snippet = '';

        // Show text content if available
        if (result.textContent && result.textContent.length > 0) {
            snippet = result.textContent.length > 200 
                ? result.textContent.substring(0, 200) + '...'
                : result.textContent;
        } else if (result.outerHTML) {
            snippet = `<code>${this.escapeHTML(result.outerHTML)}</code>`;
        } else {
            snippet = `<${result.nodeName}> (leerer Knoten)`;
        }

        // Add attributes if present
        if (result.attributes && Object.keys(result.attributes).length > 0) {
            const attrList = Object.entries(result.attributes)
                .map(([key, value]) => `${key}="${value}"`)
                .join(', ');
            snippet += `<br><small style="color: #666;">Attribute: ${attrList}</small>`;
        }

        return snippet;
    }

    // ==================== XPATH TEMPLATES ====================

    insertXPathTemplate(template) {
        const xpathInput = document.getElementById('xpathInput');
        if (xpathInput) {
            xpathInput.value = template;
            xpathInput.focus();
        }
    }

    getCommonXPathTemplates() {
        return {
            authority: [
                '//person[@xml:id]//persName[@type="preferred"]',
                '//bibl[@xml:id]//title',
                '//entry//form[@type="lemma"]//orth',
                '//category//catDesc//term[@xml:lang="de"]',
                '//idno[@type="GND"]'
            ],
            tei: [
                '//w[@lemmaRef]',
                '//l[@n]',
                '//w[@pos="NOM"]',
                '//seg[@type="pc"]',
                '//w[contains(@meaningRef, "concept")]'
            ],
            advanced: [
                '//person[contains(.//note[@type="works"], "work_")]',
                '//w[@lemmaRef and @meaningRef]',
                '//bibl[contains(.//ref/@target, "genre")]',
                '//entry[count(.//sense) > 1]',
                '//l[contains(., "vriunt")]'
            ]
        };
    }

    showXPathHelp() {
        const templates = this.getCommonXPathTemplates();
        let helpHTML = `
            <div style="margin-bottom: 15px; font-weight: 600; color: #667eea;">
                ⚡ XPath Beispiele und Hilfe
            </div>
        `;

        Object.entries(templates).forEach(([category, xpaths]) => {
            const categoryTitle = {
                authority: '📄 Authority Files',
                tei: '📜 TEI Texte', 
                advanced: '🔧 Erweiterte Queries'
            }[category];

            helpHTML += `
                <div style="margin-bottom: 15px;">
                    <h4 style="color: #667eea; margin-bottom: 8px;">${categoryTitle}</h4>
                    ${xpaths.map(xpath => `
                        <div style="margin-bottom: 5px;">
                            <code style="background: #f8f9fa; padding: 2px 4px; border-radius: 3px; font-size: 0.85rem;">${xpath}</code>
                            <button onclick="window.playground.ui.xpathInterface.insertXPathTemplate('${xpath}')"
                                    style="margin-left: 10px; padding: 2px 6px; background: #28a745; color: white; border: none; border-radius: 3px; font-size: 0.75rem; cursor: pointer;">
                                Verwenden
                            </button>
                        </div>
                    `).join('')}
                </div>
            `;
        });

        const container = document.getElementById('resultsContainer');
        if (container) {
            container.innerHTML = helpHTML;
        }
    }

    // ==================== UTILITY METHODS ====================

    getTargetDescription(target) {
        const descriptions = {
            authority: 'Authority Files',
            tei: 'TEI Texte',
            all: 'Alle Dateien'
        };
        return descriptions[target] || 'Unbekannt';
    }

    getNodeTypeDescription(nodeType) {
        const types = {
            1: 'Element',
            2: 'Attribute',
            3: 'Text',
            4: 'CDATA',
            8: 'Comment',
            9: 'Document'
        };
        return types[nodeType] || `Type ${nodeType}`;
    }

    extractNodeAttributes(node) {
        const attributes = {};
        if (node.attributes) {
            for (let i = 0; i < node.attributes.length; i++) {
                const attr = node.attributes[i];
                attributes[attr.name] = attr.value;
            }
        }
        return attributes;
    }

    escapeHTML(html) {
        return html
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // ==================== ERROR HANDLING ====================

    showError(message) {
        displayResults('❌ XPath Fehler', [{
            meta: 'Fehler',
            snippet: message
        }]);
    }

    // ==================== VALIDATION ====================

    validateXPath(xpath) {
        try {
            // Simple validation by trying to create XPathExpression
            document.evaluate(xpath, document, null, XPathResult.ANY_TYPE, null);
            return { valid: true };
        } catch (error) {
            return { valid: false, error: error.message };
        }
    }

    // ==================== EXPORT XPATH RESULTS ====================

    exportLastResults() {
        // This would export the last XPath results as CSV/JSON
        // Implementation depends on requirements
        console.log('Export functionality would be implemented here');
    }
}