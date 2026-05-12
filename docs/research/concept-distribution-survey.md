# Concept-Distribution Survey

Programmatischer Vollscan aller Concepts gegen den Korpus, um Worst-Case-Lasten fuer das Frontend-Modul `playground/js/ui/tei/concept-distribution.js` zu identifizieren. Spiegelt die JS-Aggregations-Logik 1:1.

**Datenstand:** authority-index v1.2.1, corpus-index v4.1.1. Insgesamt 567 Concepts ausgewertet.

## Verteilungs-Statistik

- **Lemmata pro Concept** (n=562 von 567 non-zero): min=1, median=98, P95=1,144, max=8,718
- **Texte mit Treffern pro Concept** (n=560 von 567 non-zero): min=1, median=360, P95=665, max=667
- **Gesamtvorkommen pro Concept** (n=560 von 567 non-zero): min=1, median=8,022, P95=259,850, max=2,979,407
- **Distinkte Lemmata pro Text (Maximum je Concept)** (n=560 von 567 non-zero): min=1, median=25, P95=252, max=1,856

## Anomalien

- Concepts ohne zugeordnete Lemmata: **5** (von 567)
- Concepts mit >= 2,000 Lemmata (Aggregation-Hotspots): **13**
- Concepts mit >= 100,000 Vorkommen (Render-Last): **75**

## Worst-Case-Kandidaten

**Hoechste Lemma-Last:** `concept_21072000` (Objektbezogene Aktivität/Tätigkeit) mit 8,718 zugeordneten Lemmata, 667 Texten, 1,223,881 Vorkommen.

**Hoechste Vorkommen-Last:** `concept_90000000` (Funktionswörter) mit 2,979,407 Vorkommen, 695 Lemmata, 667 Texten.

Empfehlung fuer Browser-Performance-Check: das erste der beiden Concepts im Playground laden und DevTools-Profiler messen. Wenn das rendering+aggregation `<` 500ms bleibt, Playwright-Regression-Test schreiben; wenn `>` 2s, Performance-Patch (Web-Worker oder requestIdleCallback-Chunking in `findMatchingLemmata`).

## Top 15 nach Lemma-Count

| Concept-ID | termDE | Lemmata | Text-Hits | Vorkommen |
|---|---|---:|---:|---:|
| `concept_21072000` | Objektbezogene Aktivität/Tätigkeit | 8,718 | 667 | 1,223,881 |
| `concept_21012000` | Männlich/Mann | 7,348 | 667 | 565,981 |
| `concept_23112500` | Personennamen/Familiennamen | 6,375 | 517 | 140,773 |
| `concept_21071000` | Selbstbezogene Aktivität/Tätigkeit | 4,485 | 667 | 1,005,309 |
| `concept_23123100` | Latein | 3,640 | 662 | 168,590 |
| `concept_31500000` | Raum | 3,105 | 665 | 1,290,657 |
| `concept_31600000` | Zeit | 2,741 | 667 | 1,864,720 |
| `concept_23240000` | Kriegswesen/Kampf/Gewalt | 2,628 | 667 | 362,744 |
| `concept_22920000` | Charakterzug | 2,440 | 665 | 343,139 |
| `concept_31800000` | Bewegung | 2,365 | 664 | 291,188 |
| `concept_31310000` | Verhältnis | 2,347 | 667 | 1,908,240 |
| `concept_24330000` | Recht | 2,208 | 666 | 440,715 |
| `concept_22833000` | Unterstützung/Hinderung | 2,023 | 666 | 330,730 |
| `concept_31410000` | Mengenbegriffe | 1,979 | 667 | 2,878,545 |
| `concept_31200000` | Eigenschaften/Zustände | 1,953 | 666 | 427,707 |

## Top 15 nach Vorkommen

| Concept-ID | termDE | Lemmata | Text-Hits | Vorkommen |
|---|---|---:|---:|---:|
| `concept_90000000` | Funktionswörter | 695 | 667 | 2,979,407 |
| `concept_31410000` | Mengenbegriffe | 1,979 | 667 | 2,878,545 |
| `concept_31310000` | Verhältnis | 2,347 | 667 | 1,908,240 |
| `concept_31600000` | Zeit | 2,741 | 667 | 1,864,720 |
| `concept_31500000` | Raum | 3,105 | 665 | 1,290,657 |
| `concept_21072000` | Objektbezogene Aktivität/Tätigkeit | 8,718 | 667 | 1,223,881 |
| `concept_21071000` | Selbstbezogene Aktivität/Tätigkeit | 4,485 | 667 | 1,005,309 |
| `concept_21012000` | Männlich/Mann | 7,348 | 667 | 565,981 |
| `concept_22831400` | Zielrichtung der Handlung | 905 | 665 | 522,577 |
| `concept_23308000` | Betteln | 1,830 | 667 | 498,037 |
| `concept_24330000` | Recht | 2,208 | 666 | 440,715 |
| `concept_31200000` | Eigenschaften/Zustände | 1,953 | 666 | 427,707 |
| `concept_22831300` | Grund der Handlung | 358 | 665 | 392,873 |
| `concept_22832000` | Ausführung | 1,541 | 666 | 376,217 |
| `concept_31100000` | Leben | 448 | 667 | 371,780 |

## Top 15 nach Texte mit Treffern

| Concept-ID | termDE | Lemmata | Text-Hits | Vorkommen |
|---|---|---:|---:|---:|
| `concept_21012000` | Männlich/Mann | 7,348 | 667 | 565,981 |
| `concept_21071000` | Selbstbezogene Aktivität/Tätigkeit | 4,485 | 667 | 1,005,309 |
| `concept_21072000` | Objektbezogene Aktivität/Tätigkeit | 8,718 | 667 | 1,223,881 |
| `concept_22831600` | Möglichkeit | 209 | 667 | 283,722 |
| `concept_22834000` | Ergebnis der Handlung | 930 | 667 | 335,050 |
| `concept_23240000` | Kriegswesen/Kampf/Gewalt | 2,628 | 667 | 362,744 |
| `concept_23308000` | Betteln | 1,830 | 667 | 498,037 |
| `concept_31100000` | Leben | 448 | 667 | 371,780 |
| `concept_31310000` | Verhältnis | 2,347 | 667 | 1,908,240 |
| `concept_31410000` | Mengenbegriffe | 1,979 | 667 | 2,878,545 |
| `concept_31600000` | Zeit | 2,741 | 667 | 1,864,720 |
| `concept_90000000` | Funktionswörter | 695 | 667 | 2,979,407 |
| `concept_22620000` | Anschauung/Begriff/Vorstellung/Denkprozesse | 657 | 666 | 204,539 |
| `concept_22825000` | Resignation | 774 | 666 | 195,812 |
| `concept_22826000` | Willensausübung auf andere | 1,147 | 666 | 190,623 |

## Concepts ohne zugeordnete Lemmata (5)

Diese Concepts haben kein einziges Lemma mit `senses[*].conceptIds.includes(this.id)`. Im Frontend zeigen sie den Block "Keine Lemmata sind diesem Begriff zugeordnet".

| Concept-ID | termDE |
|---|---|
| `concept_11300000` | Himmelsrichtungen |
| `concept_14011400` | Säugetiere/Namen |
| `concept_14062000` | Verarbeitung von Weichtieren |
| `concept_30000000` | Menschen und ihre Umwelt |
| `concept_32900000` | Geschichtswissenschaft |
