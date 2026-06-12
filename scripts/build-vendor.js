// Copies third-party browser assets from node_modules into assets/vendor/.
//
// Why this exists: GitHub Pages serves static files, no npm install at deploy
// time. Like tailwind-output.css, the vendor output is committed to the repo.
// This script makes the source of those files explicit and version-pinned via
// package-lock.json — no manual downloads, no CDN dependency.
//
// Run via: npm run build:vendor

import { copyFileSync, mkdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, '..');

const prismPkg = JSON.parse(
    readFileSync(resolve(repoRoot, 'node_modules/prismjs/package.json'), 'utf8')
);

const targets = [
    {
        src: 'node_modules/prismjs/components/prism-core.min.js',
        dst: 'assets/vendor/prism/prism-core.min.js'
    },
    {
        src: 'node_modules/prismjs/components/prism-markup.min.js',
        dst: 'assets/vendor/prism/prism-markup.min.js'
    },
    {
        src: 'node_modules/prismjs/themes/prism-okaidia.min.css',
        dst: 'assets/vendor/prism/prism.css'
    }
];

function sha256(filePath) {
    const buf = readFileSync(filePath);
    return createHash('sha256').update(buf).digest('hex').slice(0, 16);
}

const outDir = resolve(repoRoot, 'assets/vendor/prism');
mkdirSync(outDir, { recursive: true });

const manifestLines = [
    `Prism.js vendor bundle`,
    `Source package: prismjs@${prismPkg.version}`,
    `License: ${prismPkg.license || 'MIT'} (see https://github.com/PrismJS/prism)`,
    `Generated: ${new Date().toISOString()}`,
    ``,
    `Files:`
];

for (const { src, dst } of targets) {
    const srcAbs = resolve(repoRoot, src);
    const dstAbs = resolve(repoRoot, dst);
    if (!existsSync(srcAbs)) {
        console.error(`[build-vendor] Missing source: ${src}`);
        process.exit(1);
    }
    mkdirSync(dirname(dstAbs), { recursive: true });
    copyFileSync(srcAbs, dstAbs);
    const hash = sha256(dstAbs);
    const size = readFileSync(dstAbs).length;
    manifestLines.push(`  ${dst}  (${size} bytes, sha256:${hash})`);
    console.log(`[build-vendor] ${src} -> ${dst}`);
}

writeFileSync(resolve(outDir, 'MANIFEST.txt'), manifestLines.join('\n') + '\n');
console.log(`[build-vendor] Wrote MANIFEST.txt`);
