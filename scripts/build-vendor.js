// Copies third-party browser assets from node_modules into assets/vendor/.
//
// Why this exists: GitHub Pages serves static files, no npm install at deploy
// time. Like tailwind-output.css, the vendor output is committed to the repo.
// This script makes the source of those files explicit and version-pinned via
// package-lock.json — no manual downloads, no CDN dependency.
//
// Manifests are deterministic (no timestamp), analog zu den Index-Builds
// (#125): identischer node_modules-Stand erzeugt byte-identische Manifeste.
//
// Run via: npm run build:vendor

import { copyFileSync, mkdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, '..');

// One entry per vendored npm package. `files` maps node_modules sources to
// assets/vendor/<dir>/ destinations; each package dir gets its own MANIFEST.txt.
const packages = [
    {
        name: 'prismjs',
        homepage: 'https://github.com/PrismJS/prism',
        dir: 'assets/vendor/prism',
        files: [
            ['node_modules/prismjs/components/prism-core.min.js', 'prism-core.min.js'],
            ['node_modules/prismjs/components/prism-markup.min.js', 'prism-markup.min.js'],
            ['node_modules/prismjs/themes/prism-okaidia.min.css', 'prism.css']
        ]
    },
    {
        name: 'pako',
        homepage: 'https://github.com/nodeca/pako',
        dir: 'assets/vendor/pako',
        files: [
            ['node_modules/pako/dist/pako.min.js', 'pako.min.js']
        ]
    },
    {
        name: 'dexie',
        homepage: 'https://github.com/dexie/Dexie.js',
        dir: 'assets/vendor/dexie',
        files: [
            ['node_modules/dexie/dist/dexie.min.js', 'dexie.min.js']
        ]
    }
];

function sha256(filePath) {
    const buf = readFileSync(filePath);
    return createHash('sha256').update(buf).digest('hex').slice(0, 16);
}

for (const pkg of packages) {
    const pkgJson = JSON.parse(
        readFileSync(resolve(repoRoot, `node_modules/${pkg.name}/package.json`), 'utf8')
    );
    const outDir = resolve(repoRoot, pkg.dir);
    mkdirSync(outDir, { recursive: true });

    const manifestLines = [
        `${pkg.name} vendor bundle`,
        `Source package: ${pkg.name}@${pkgJson.version}`,
        `License: ${pkgJson.license || 'see package'} (see ${pkg.homepage})`,
        ``,
        `Files:`
    ];

    for (const [src, dstName] of pkg.files) {
        const srcAbs = resolve(repoRoot, src);
        const dstAbs = resolve(outDir, dstName);
        if (!existsSync(srcAbs)) {
            console.error(`[build-vendor] Missing source: ${src} — run npm install first`);
            process.exit(1);
        }
        mkdirSync(dirname(dstAbs), { recursive: true });
        copyFileSync(srcAbs, dstAbs);
        const hash = sha256(dstAbs);
        const size = readFileSync(dstAbs).length;
        manifestLines.push(`  ${pkg.dir}/${dstName}  (${size} bytes, sha256:${hash})`);
        console.log(`[build-vendor] ${src} -> ${pkg.dir}/${dstName}`);
    }

    writeFileSync(resolve(outDir, 'MANIFEST.txt'), manifestLines.join('\n') + '\n');
    console.log(`[build-vendor] Wrote ${pkg.dir}/MANIFEST.txt`);
}
