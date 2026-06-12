# #117 Wörterbuch-Einstiegsseite (Design-Spec)

**Issue:** [#117](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/117) · **Status:** Design approved (Christian, 2026-06-11) · **Lebensdauer:** bis Issue-Close, dann Wissen in stabile Docs extrahieren und löschen (Temporal-Artifacts-Konvention).

## Ziel

Konventionelle Wörterbuch-Einstiegsseite für die ~43.754 Lemma-Seiten (`lemma/?id=N`): semasiologisch sortiert von A–Z, mit Indexleiste und Blätterfunktion, plus Menüpunkt auf allen Seiten.

## Namensentscheidung: „Wörterbuch"

Gewählt gegenüber „Lemmata" und „Wortindex" (Alt-MHDBDB):

1. Hauptseiten-Zielgruppe (Studierende, Allgemeinheit) versteht „Wörterbuch" sofort; „Lemmata" bleibt Fachbegriff des Playground-Explorers für Forschende.
2. Die Lemma-Seiten leisten mehr als ein bloßer Index: Bedeutungen über das Begriffssystem, Schreibformen, Komposita, Belegstellen, MWB/Lexer-Links.
3. „Wortindex" wird als Brücke für Altnutzer im Untertitel der Seite erwähnt.

Bekannte Einschränkung: keine ausformulierten Definitionen wie MWB/Lexer; die Seite verlinkt aber beide Wörterbücher pro Lemma.

## Architektur

**Neue Dateien:** `woerterbuch.html` (Root) + `assets/js/woerterbuch.js` (ES-Modul, Controller-Klasse analog `lemma/lemma-page.js`).

**Datenquelle:** bestehender `data/authority-index.json.gz` über `CorpusLoader` (IndexedDB-gecacht, 30 Tage). Bewusst **kein** neues Build-Artefakt und **keine** Erweiterung des Data-Change-Lifecycle; verworfene Alternativen: separater schlanker Lemma-Index (Drift-Risiko, kaum Ladezeit-Gewinn dank Cache), 26 statische Buchstaben-Seiten (Artefakt-Wildwuchs).

**Bucketing:** Anfangsbuchstabe von `normalized` (Fallback `lemma`). Randfälle: `ë`/`ú` (19 Lemmata) via Unicode-NFD-Strip nach `e`/`u`; Lemmata mit Ziffern-Anfang (5 Stück: „1", „36", „42", „46", „49") in einen `#`-Bucket am Ende der Leiste.

**Sortierung im Bucket:** `localeCompare(normalized, 'de')`, Sekundärschlüssel `lemma`.

## UI

- **Indexleiste:** A–Z + `#`, sticky unter dem Header, aktiver Buchstabe hervorgehoben, Eintragszahl pro Buchstabe als Tooltip/Subtext. Leere Buckets (falls vorhanden) deaktiviert.
- **Einträge:** mehrspaltiges Registerblatt (3–4 Spalten Grid, Desktop ≥1200px): Lemma als Link auf `lemma/?id=<numerisch>` + POS-Badge (Stil `pos-badge` wie auf der Lemma-Seite).
- **Blätterfunktion:** Pagination à 200 Einträge innerhalb des Buchstabens (größter Bucket S: 4.457 → 23 Seiten); Vor/Zurück + Seitenzahlen.
- **URL-State:** `?buchstabe=s&seite=3` (Lesen beim Laden, Schreiben via `history.replaceState`) für Bookmarks und Deep-Links.
- **Untertitel:** verweist auf den historischen „Wortindex" der MHDBDB.
- Ladebildschirm/Fehlerzustand nach dem Muster der bestehenden Seiten.

## Navigation

`includes/_nav.html` (Desktop **und** Mobile-Block im Partial): „Wörterbuch" mit `data-nav="woerterbuch"` an Position 4 — Startseite, Korpussuche, Playground, Wörterbuch, Hilfe, Kontakt (Reihenfolge aus dem Issue). Neuer Eintrag `"woerterbuch.html": ("woerterbuch", "")` in `PAGES` von `scripts/build-pages.py`, danach Rebuild aller Seiten.

## Nebenverbesserung

`lemma/index.html` ohne `id`-Parameter zeigt bisher nur eine Fehlermeldung; der Fehlertext verlinkt künftig auf `../woerterbuch.html`.

## Abschlusskriterien

- `python scripts/build-pages.py --check` grün (alle Seiten in sync).
- `npm run build:css` vor Push, falls neue Utility-Klassen.
- Playwright-Smoke-Test (Seite lädt, Buchstabenwechsel, Pagination, Link zur Lemma-Seite) — Testlauf nur nach Rückfrage.
- Kein Commit/Push ohne Christians Test und Freigabe.
- Nach Push: @wachauer im Issue anpingen (Live-URL + Test-Hinweise), Issue offen lassen bis ihr OK.
- Doc-Count-Drift prüfen (INDEX/FEATURES/ARCHITECTURE/DESIGN: neue Hauptseite erwähnen).
