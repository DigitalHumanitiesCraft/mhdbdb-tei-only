# Browser Compatibility Matrix

**Target Support**: Modern browsers from 2020+

## Minimum Browser Versions

| Browser | Version | Release Date | Notes |
|---------|---------|--------------|-------|
| Chrome | 90+ | April 2021 | Full support |
| Firefox | 100+ | May 2022 | Full support |
| Safari | 14+ | September 2020 | **Critical**: Use pako for gzip (DecompressionStream only Safari 16.4+) |
| Edge | 90+ | April 2021 | Chromium-based, same as Chrome |

## Feature Compatibility

### Core Technologies

| Feature | Chrome 90+ | Firefox 100+ | Safari 14+ | Edge 90+ | Notes |
|---------|------------|--------------|------------|----------|-------|
| ES6 Modules | ✅ | ✅ | ✅ | ✅ | Native support |
| IndexedDB | ✅ | ✅ | ✅ | ✅ | Full support |
| Fetch API | ✅ | ✅ | ✅ | ✅ | Full support |
| DOMParser | ✅ | ✅ | ✅ | ✅ | XML parsing |
| XPath | ✅ | ✅ | ✅ | ✅ | document.evaluate() |

### Compression APIs

| Feature | Chrome 90+ | Firefox 100+ | Safari 14+ | Edge 90+ | Notes |
|---------|------------|--------------|------------|----------|-------|
| DecompressionStream | ✅ (Chrome 80+) | ✅ (Firefox 113+) | ❌ (Safari 16.4+) | ✅ (Edge 80+) | **Use pako instead** |
| pako.js (gzip) | ✅ | ✅ | ✅ | ✅ | **Cross-browser solution** |

### Storage APIs

| Feature | Chrome 90+ | Firefox 100+ | Safari 14+ | Edge 90+ | Notes |
|---------|------------|--------------|------------|----------|-------|
| navigator.storage.estimate() | ✅ | ✅ | ✅ | ✅ | Quota checking |
| IndexedDB v2 | ✅ | ✅ | ✅ | ✅ | Binary keys, getAll() |
| Storage Manager API | ✅ | ✅ | ✅ | ✅ | persist(), estimate() |

### CSS Features (Tailwind)

| Feature | Chrome 90+ | Firefox 100+ | Safari 14+ | Edge 90+ | Notes |
|---------|------------|--------------|------------|----------|-------|
| Flexbox | ✅ | ✅ | ✅ | ✅ | Full support |
| Grid | ✅ | ✅ | ✅ | ✅ | Full support |
| Custom Properties | ✅ | ✅ | ✅ | ✅ | CSS variables |
| backdrop-filter | ✅ | ✅ | ✅ | ✅ | Modal backgrounds |

## Critical Decisions

### 1. Compression Library Choice

**Decision**: Use **pako.js** instead of native `DecompressionStream`

**Reason**: Safari 14-16.3 doesn't support `DecompressionStream`. Pako provides cross-browser gzip decompression.

```javascript
// ❌ DON'T USE (Safari <16.4 incompatible)
const ds = new DecompressionStream('gzip');
const decompressed = stream.pipeThrough(ds);

// ✅ USE (cross-browser)
const arrayBuffer = await response.arrayBuffer();
const decompressed = pako.ungzip(new Uint8Array(arrayBuffer), { to: 'string' });
```

### 2. IndexedDB Wrapper

**Decision**: Use **Dexie.js** for IndexedDB operations

**Reason**:
- Simplifies promise-based API
- Cross-browser compatibility layer
- Better error handling
- Type-safe queries

### 3. XML Parsing

**Decision**: Use native **DOMParser** with namespace handling

**Reason**:
- Supported in all target browsers
- No external dependencies needed
- Handles TEI namespace correctly with proper XPath

```javascript
const parser = new DOMParser();
const doc = parser.parseFromString(xmlText, 'text/xml');

// Check for parse errors
const parseError = doc.querySelector('parsererror');
if (parseError) {
  throw new Error('XML parsing failed');
}
```

## Testing Strategy

### Automated Testing (Playwright)

```javascript
// playwright.config.js
module.exports = {
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit', // Safari engine
      use: { ...devices['Desktop Safari'] }
    }
  ]
};
```

### Manual Testing Checklist

- [ ] Chrome 90+ on Windows 10/11
- [ ] Chrome 90+ on macOS
- [ ] Firefox 100+ on Windows 10/11
- [ ] Firefox 100+ on macOS
- [ ] Safari 14+ on macOS
- [ ] Safari 14+ on iOS 14+
- [ ] Edge 90+ on Windows 10/11

## Known Limitations

### Safari-Specific Issues

1. **IndexedDB Quota**: Safari has stricter quota limits (typically 1GB vs Chrome's dynamic allocation)
2. **Private Browsing**: IndexedDB may be disabled or have 0 quota
3. **Blob Storage**: Large blob storage can be unreliable

**Mitigation**: Storage quota checking with graceful degradation

### Mobile Browser Support

**Not officially supported** (Desktop-focused application, min 1200px width)

However, basic functionality should work on:
- Safari iOS 14+ (iPad)
- Chrome Android 90+

## Polyfills & Fallbacks

### Not Needed

All target browsers support required features natively:
- ES6 modules
- Promises
- async/await
- Fetch API
- IndexedDB
- DOMParser
- XPath

### External Dependencies

| Library | Purpose | CDN Version |
|---------|---------|-------------|
| pako.js | gzip decompression | 2.1.0 |
| Dexie.js | IndexedDB wrapper | 3.2.4 |
| Tailwind CSS | Responsive styling | 3.x (CDN) |

## Performance Considerations

### Safari-Specific

- IndexedDB reads can be slower than Chrome/Firefox
- Large file processing may be slower
- Strict memory limits in some contexts

**Mitigation**:
- Lazy loading
- Progressive enhancement
- Clear feedback on long operations

## Accessibility

All target browsers support:
- ARIA attributes
- Keyboard navigation
- Focus management
- Screen reader APIs

## Security Considerations

### CORS & Local Files

TEI files must be served via HTTP server (not `file://`) for:
- Fetch API access
- CORS compliance
- IndexedDB access

**Development**: Use `http-server` or `npm run serve`

## Testing Commands

```bash
# Test on all browsers
npm run test

# Test specific browser
npm run test -- --project=webkit  # Safari
npm run test -- --project=chromium  # Chrome
npm run test -- --project=firefox  # Firefox

# View test report
npm run report
```

## Version Support Policy

**Minimum versions will be tested** at Phase 4, Step 4.5 (Cross-Browser Testing)

**Support window**: Browsers released within last 3-4 years (2020+)

**Rationale**:
- Academic users typically have modern browsers
- University IT departments update regularly
- Older browsers lack critical features (IndexedDB v2, Storage API)

---

**Status**: Compatibility matrix defined
**Next**: Create test fixtures for automated testing
