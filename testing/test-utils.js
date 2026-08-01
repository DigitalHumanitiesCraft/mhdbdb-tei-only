/**
 * MHDBDB Playground - Test Utilities
 * Helper functions for testing the playground functionality
 */

export class TestUtils {
    constructor() {
        this.testResults = [];
        this.testSuiteStartTime = null;
    }

    // ==================== TEST FRAMEWORK ====================

    async describe(suiteName, testFunction) {
        console.group(`📋 ${suiteName}`);
        this.currentSuite = suiteName;

        try {
            await testFunction();
        } catch (error) {
            this.fail(`Suite "${suiteName}" crashed: ${error.message}`);
        }

        console.groupEnd();
    }

    async it(testName, testFunction) {
        const startTime = performance.now();

        try {
            await testFunction();
            const duration = Math.round(performance.now() - startTime);
            this.pass(testName, duration);
        } catch (error) {
            const duration = Math.round(performance.now() - startTime);
            this.fail(testName, error.message, duration);
        }
    }

    pass(testName, duration = 0) {
        this.testResults.push({
            suite: this.currentSuite,
            test: testName,
            status: 'pass',
            duration,
            timestamp: Date.now()
        });
        console.log(`✅ ${testName} (${duration}ms)`);
    }

    fail(testName, error = '', duration = 0) {
        this.testResults.push({
            suite: this.currentSuite,
            test: testName,
            status: 'fail',
            error,
            duration,
            timestamp: Date.now()
        });
        console.error(`❌ ${testName} - ${error} (${duration}ms)`);
    }

    // ==================== ASSERTIONS ====================

    assert(condition, message) {
        if (!condition) {
            throw new Error(message || 'Assertion failed');
        }
    }

    assertEqual(actual, expected, message) {
        if (actual !== expected) {
            throw new Error(message || `Expected ${expected}, but got ${actual}`);
        }
    }

    assertNotEqual(actual, unexpected, message) {
        if (actual === unexpected) {
            throw new Error(message || `Expected value not to be ${unexpected}`);
        }
    }

    assertTrue(value, message) {
        if (value !== true) {
            throw new Error(message || `Expected true, but got ${value}`);
        }
    }

    assertFalse(value, message) {
        if (value !== false) {
            throw new Error(message || `Expected false, but got ${value}`);
        }
    }

    assertExists(value, message) {
        if (value === null || value === undefined) {
            throw new Error(message || 'Expected value to exist');
        }
    }

    assertElementExists(selector, message) {
        const element = document.querySelector(selector);
        if (!element) {
            throw new Error(message || `Expected element "${selector}" to exist`);
        }
        return element;
    }

    // ==================== MOCK DATA GENERATORS ====================

    generateMockTEIContent(wordCount = 10) {
        const words = [
            'vriunt', 'minne', 'herze', 'tugent', 'êre',
            'got', 'welt', 'rîche', 'guot', 'leben',
            'wîse', 'kunst', 'liep', 'leit', 'fröude'
        ];

        let content = '<?xml version="1.0" encoding="UTF-8"?>\n';
        content += '<TEI xmlns="http://www.tei-c.org/ns/1.0">\n';
        content += '  <teiHeader>\n';
        content += '    <fileDesc>\n';
        content += '      <titleStmt><title>Test TEI File</title></titleStmt>\n';
        content += '      <publicationStmt><p>Test publication</p></publicationStmt>\n';
        content += '      <sourceDesc><p>Generated for testing</p></sourceDesc>\n';
        content += '    </fileDesc>\n';
        content += '  </teiHeader>\n';
        content += '  <text>\n';
        content += '    <body>\n';
        content += '      <p>\n';

        for (let i = 0; i < wordCount; i++) {
            const word = words[i % words.length];
            const lemmaRef = `lexicon.xml#lemma_${1000 + i}`;
            content += `        <w xml:id="w_${i + 1}" lemmaRef="${lemmaRef}" pos="NN">${word}</w>\n`;
        }

        content += '      </p>\n';
        content += '    </body>\n';
        content += '  </text>\n';
        content += '</TEI>';

        return content;
    }

    createMockFile(filename, content = null, size = null) {
        content = content || this.generateMockTEIContent();
        size = size || content.length;

        return {
            name: filename,
            size: size,
            type: 'text/xml',
            lastModified: Date.now()
        };
    }

    createMockFileList(filenames) {
        return filenames.map(filename => this.createMockFile(filename));
    }

    // ==================== STORAGE UTILITIES ====================

    async clearTestStorage() {
        // Clear IndexedDB test data
        try {
            if ('indexedDB' in window) {
                // Clear IndexedDB database
                const dbName = 'mhdbdb_playground';
                await new Promise((resolve, reject) => {
                    const deleteReq = indexedDB.deleteDatabase(dbName);
                    deleteReq.onsuccess = () => resolve();
                    deleteReq.onerror = () => reject(deleteReq.error);
                });
                console.log('🧹 Test IndexedDB cleared');
            }

            // Also clear sessionStorage for any remaining legacy data
            const keys = Object.keys(sessionStorage);
            keys.forEach(key => {
                if (key.startsWith('mhdbdb_') || key.includes('test')) {
                    sessionStorage.removeItem(key);
                }
            });
        } catch (error) {
            console.warn('⚠️ Failed to clear test storage:', error);
        }
    }

    getStorageSize() {
        let size = 0;
        for (let key in sessionStorage) {
            if (sessionStorage.hasOwnProperty(key)) {
                size += key.length + sessionStorage[key].length;
            }
        }
        return size;
    }

    // ==================== DOM UTILITIES ====================

    waitForElement(selector, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const element = document.querySelector(selector);
            if (element) {
                resolve(element);
                return;
            }

            const observer = new MutationObserver((mutations, obs) => {
                const element = document.querySelector(selector);
                if (element) {
                    obs.disconnect();
                    resolve(element);
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });

            setTimeout(() => {
                observer.disconnect();
                reject(new Error(`Element ${selector} not found within ${timeout}ms`));
            }, timeout);
        });
    }

    triggerClick(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.click();
        } else {
            throw new Error(`Element ${selector} not found`);
        }
    }

    // ==================== INDEXEDDB TEST UTILITIES ====================

    async testIndexedDBSupport() {
        this.assertExists(window.indexedDB, 'IndexedDB should be available');
    }

    async createTestTEIContent(size = 1024) {
        // Create a test TEI file of specified size
        const baseContent = `<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title>Test TEI Document</title>
            </titleStmt>
        </fileDesc>
    </teiHeader>
    <text>
        <body>`;

        const endContent = `
        </body>
    </text>
</TEI>`;

        let content = baseContent;
        const wordPattern = '<w lemmaRef="lexicon.xml#lemma_123">testword</w> ';

        // Fill to desired size
        while (content.length + endContent.length < size) {
            content += `<p>Test paragraph with ${wordPattern.repeat(10)}</p>\n`;
        }

        content += endContent;
        return content;
    }

    generateReport() {
        const passed = this.testResults.filter(r => r.status === 'pass').length;
        const failed = this.testResults.filter(r => r.status === 'fail').length;
        const total = this.testResults.length;

        const report = {
            summary: {
                total,
                passed,
                failed,
                passRate: total > 0 ? Math.round((passed / total) * 100) : 0,
                duration: Date.now() - this.testSuiteStartTime
            },
            results: this.testResults
        };

        return report;
    }

    displayReport(containerId = 'test-results') {
        const container = document.getElementById(containerId);
        if (!container) return;

        const report = this.generateReport();

        let html = `
            <div class="test-report">
                <div class="test-summary ${report.summary.failed === 0 ? 'success' : 'failure'}">
                    <h2>Test Results</h2>
                    <div class="stats">
                        <span class="total">${report.summary.total} total</span>
                        <span class="passed">${report.summary.passed} passed</span>
                        <span class="failed">${report.summary.failed} failed</span>
                        <span class="rate">${report.summary.passRate}% pass rate</span>
                        <span class="duration">${report.summary.duration}ms</span>
                    </div>
                </div>
                <div class="test-details">
        `;

        // Group by suite
        const suites = {};
        report.results.forEach(result => {
            if (!suites[result.suite]) suites[result.suite] = [];
            suites[result.suite].push(result);
        });

        Object.entries(suites).forEach(([suiteName, tests]) => {
            html += `<div class="test-suite">
                <h3>${suiteName}</h3>
                <ul>`;

            tests.forEach(test => {
                const icon = test.status === 'pass' ? '✅' : '❌';
                html += `<li class="${test.status}">
                    ${icon} ${test.test} (${test.duration}ms)
                    ${test.error ? `<div class="error">${test.error}</div>` : ''}
                </li>`;
            });

            html += `</ul></div>`;
        });

        html += `</div></div>`;
        container.innerHTML = html;
    }

    startTestSuite() {
        this.testSuiteStartTime = Date.now();
        this.testResults = [];
        console.log('🧪 Starting test suite...');
    }
}