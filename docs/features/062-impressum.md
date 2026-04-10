# Issue #62: Impressum

## Context

Austrian/German legal requirement: any public website needs an Impressum (legal notice). Currently missing entirely — no page, no footer link. Katharina provided the full text in the issue. This is a hard prerequisite for going public.

**Priority:** Quick win, effort:small. Blocker for public launch.

## Current State

- No `impressum.html` exists
- All three pages (`index.html`, `korpus.html`, `playground/index.html`) share an identical footer structure: logos + copyright + links + "Clear Site Data" button
- No Impressum/Datenschutz link anywhere

## Content (from Katharina, Issue #62)

### Kontakt

Universität Salzburg
Mittelhochdeutsche Begriffsdatenbank (MHDBDB)
Koordination: Dr. Katharina Zeppezauer-Wachauer
Fachbereich Germanistik

E-Mail: mhdbdb@plus.ac.at
Web: mhdbdb.plus.ac.at

### Impressum

Medieninhaberin, Herausgeberin sowie inhaltliche und redaktionelle Verantwortung für diese Website der Mittelhochdeutschen Begriffsdatenbank (MHDBDB):
Universität Salzburg, Kapitelgasse 4-6, 5020 Salzburg, Österreich

Die Mittelhochdeutsche Begriffsdatenbank (MHDBDB) ist ein Projekt der Universität Salzburg.

Verantwortliche Ansprechpartnerin: Dr. Katharina Zeppezauer-Wachauer, Koordinatorin der MHDBDB

Webbetreuung: Dr. Katharina Zeppezauer-Wachauer, DHcraft.org
Grafische Konzeption und Design: DHcraft.org
Technische Umsetzung und Entwicklung: DHcraft.org
Technische Bereitstellung: GitHub Pages

Im Übrigen gelten die allgemeinen rechtlichen Rahmenbedingungen der Universität Salzburg (Link: https://www.plus.ac.at/impressum/), soweit auf diese Website anwendbar.

### Haftung

Inhalte sorgfältig geprüft, keine Gewähr für Richtigkeit/Vollständigkeit. Haftung der Universität Salzburg soweit gesetzlich zulässig ausgeschlossen. Keine Verantwortung für externe Links.

### Lizenz

CC BY-NC-SA 4.0 (Annotationen). Volltextlizenzen gesondert ausgewiesen.

### Open Question (from Katharina)

Christian (chsteiner) can optionally be listed under Kontakt namentlich — Katharina said "mir ist alles recht". Decision pending.

## Implementation

### New File: `impressum.html`

- Same layout frame as `korpus.html` (header, nav, footer)
- Static HTML content, no JS required
- Sections: Kontakt, Impressum, Haftung, Lizenz
- Clean typography, same design tokens as main site

### Footer Links (all 3 pages)

Add "Impressum" link to the shared footer in:
- `index.html` (landing page)
- `korpus.html` (search/reader)
- `playground/index.html` (research tool)

Link placement: next to existing footer links (E-Mail, Web, GitHub), separated by `|` or in its own row.

### Design

Follow existing page patterns:
- Header with nav (same as other pages)
- Content area: max-width container, `prose` typography
- Sections as `<h2>` with body text
- External link to Uni Salzburg Impressum opens in new tab
- Footer identical to other pages

## Files to Touch

- **New:** `impressum.html`
- `index.html` — add footer link
- `korpus.html` — add footer link
- `playground/index.html` — add footer link

## Testing

1. Navigate to `impressum.html` — all content renders correctly
2. All footer links on all 3 pages point to impressum.html
3. External link to plus.ac.at/impressum works
4. Email link (`mailto:mhdbdb@plus.ac.at`) works
5. Page uses same design tokens / visual language as rest of site
6. `npm test` — no regressions

## Out of Scope

- Datenschutzerklärung (privacy policy) — may be needed later but not requested now
- Cookie banner (no cookies used on static site)
- Barrierefreiheitserklärung (accessibility statement)
