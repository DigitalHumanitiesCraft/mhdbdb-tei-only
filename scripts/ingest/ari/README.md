# ARI Ingest Pipeline

Ingest-Pipeline für das **ARITHMETIC**-Korpus (Issue [#92](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/92)) — 6 frühneuhochdeutsche Rechenbuch-Handschriften aus dem Arithmetic-Projekt der Universität Graz (GAMS-Repositorium, beigetragen von Carina, 2026-04-30).

> Die Pipeline ist **inkrementell**. Stand 2026-05-08 ist nur Stage 0 (mechanische Schema-Konversion) implementiert. Phase 1 (Lemmatisierung) bis Phase 3 (Sense) folgen analog zum WZB-Pattern in [`scripts/ingest/wzb/`](../wzb/).

## Dogfood-Befund (München UB 279, 2026-05-08)

Die kleinste der sechs Handschriften (München, Universitätsbibliothek, 8 Cod.ms. 279, 575 Zeilen Original / 212 Zeilen MHDBDB-Variante) wurde als erster Konversions-Test verwendet. Sie zeigte zwei Klassen von Schema-Verstößen:

### Mechanisch fixbar (im Skript erledigt)

| Quelle (Carinas TEI) | Ziel (MHDBDB) | Heuristik |
|---|---|---|
| `tei:`-Präfix + Default-NS doppelt deklariert | nur Default-NS | `tei:` weg, Element-Tags in Default-NS umsetzen |
| `<seg type="token" xml:id="...">` | `<w xml:id="...">` | xml:id übernommen |
| `<seg type="pc">` ohne `@join` | `<pc join="left\|right">` | Vorgänger-Heuristik (identisch zu [`wzb-convert-seg-pc.py`](../wzb/wzb-convert-seg-pc.py)) |
| Minimaler Header (`<title>` + `<sourceDesc><p>URL</p>`) | Voll-Header mit Lizenz, Autor, Genre, particDesc | Template mit Defaults, einige Felder als TBD-Platzhalter |
| Kein xml-model PI | `mhdbdb.rng` + `tei_all.rng` PIs | Festes Pattern |
| `<TEI xml:id>` fehlt | `<TEI xml:id="{SIGLE}">` | aus `--sigle`-Argument |

### Pending Decision PD-001 (offen, blockiert Stage-2-PASS)

Fünf Element-/Attributklassen in Carinas Daten sind nicht im aktuellen MHDBDB-Schema. Sie wurden bewusst **stehengelassen**, damit der Befund den Entscheidungs-Hebel für [`docs/DECISIONS.md § PD-001`](../../../docs/DECISIONS.md) liefert:

| Element / Attribut | Vorkommen in MUE279 | Forschungsrelevanz |
|---|---|---|
| `<unit type="measurement\|weight">` | 6× | Maß- und Gewichtseinheiten in Rechenbeispielen |
| `<rs type="currency\|goods">` | 11× | Währungsbezeichnungen, Handelsgüter |
| `<unclear>` | 1× | Editorische Unsicherheits-Markierung (TEI-P5-Standard, aber bisher nicht im Korpus) |
| `<hi rend="superscript\|subscript">` | 8× | Hoch-/Tiefstellung von Bruch-Zähler/-Nenner |
| `<div type="commodity_calculation\|reckoning_example">` | 5× | Domänen-Klassifikation der Rechenbeispiele |

**Cascade-Effekt:** Ein einziges Schema-fremdes Element bricht die ganze RelaxNG-Validierung des umschließenden `<div>`/`<body>`. Die rohe Fehlerliste zeigt 6 Fehler in `<unit>`/`<div>`/`<body>` — sie kollabieren auf 0, sobald die fünf PD-001-Klassen entweder wegtransformiert oder ins Schema aufgenommen werden (Test verifiziert 2026-05-08).

### PD-001 Optionen

1. **Schema erweitern:** `<unit>`, `<rs>`, `<unclear>` als optionale Inline-Elemente in `mhdbdb.rnc` aufnehmen; `superscript`/`subscript` zum `hi/@rend`-Tokenset hinzufügen; neue `<div>/@type`-Werte ins Enum aufnehmen. Pro: Forschungs-Annotation bleibt erhalten. Contra: Schema bekommt genre-spezifische Sonderkonstrukte.
2. **Wegtransformieren:** Wrapper-Unwrap (`<unit>`, `<rs>`, `<unclear>`, problematische `<hi>`); `div/@type`-Werte auf bestehende Werte mappen oder fallenlassen. Pro: Schema bleibt sauber. Contra: Carinas Domänen-Annotation geht verloren.
3. **Hybrid:** TEI-konforme Standard-Elemente nutzen (`<measure>` statt `<unit>`, `<persName>` statt `<person>`) und Domänen-Klassifikation in `@type`/`@ana` tragen.

Die Entscheidung gehört Carina und Katharina.

## Skripte

### Stage 0 — Schema-Konversion

| Skript | Zweck |
|--------|-------|
| `01-convert-original-to-mhdbdb.py` | Mechanische Konversion: `tei:`-Präfix weg, `<seg type="token">` → `<w>`, `<seg type="pc">` → `<pc join>`, Header-Stub einfügen, xml-model PIs setzen. Nimmt Carinas TEI als Input, schreibt MHDBDB-Format. PD-001-Elemente bleiben unangetastet. |

```bash
PYTHONIOENCODING=utf-8 python scripts/ingest/ari/01-convert-original-to-mhdbdb.py \
    --input /pfad/zu/Arithmetic_MHDBDB/MHDBDB/{file}.xml \
    --sigle ARI_MUE279 \
    --title-de "Muenchen, Universitaetsbibliothek, 8 Cod.ms. 279" \
    --source-url https://gams.uni-graz.at/o:arithmetic.mue279 \
    --output tei/ARI_MUE279.tei.xml
```

### Stage 1 — PD-001 entscheiden, dann Phase 1+2 (geplant)

Folgt dem WZB-Pipeline-Pattern (`auto-match` → `pos-assign` → `sense-assign`), sobald PD-001 entschieden ist und die Schema-Konformität hergestellt ist. Erwartung: Coverage-Targets ≥85 % `@lemmaRef`, ≥90 % `@pos` (FNHD-Sprachstufe niedriger als WZB-MHG, weil weniger Lexikon-Überdeckung).

## Status

| Datum | Aktion | Ergebnis |
|---|---|---|
| 2026-05-07 | Issue #92 angelegt, Mail-Entwurf an Carina | Carina-Antwort steht aus |
| 2026-05-08 | Stage 0 implementiert + Dogfood München UB 279 | 100 Wort-Tokens konvertiert; 6 Stage-2-Fehler durch 5 PD-001-Element-Klassen, alle anderen Aspekte sauber |
| 2026-05-08 | Mail-Klärung mit Carina + Schema-Diskussion mit Katharina | PD-001 entschieden: alle Domain-Tags ins Schema |
| 2026-05-08 | Vollständiger Audit aller 6 HS | 12 nicht-Schema-Element-Klassen + 24 div/@type-Werte + 7 hi/@rend-Werte gefunden |

## Geklärt durch Katharina (2026-05-08)

| Frage | Antwort |
|---|---|
| Sigle-Strategie | `ARI` mit Suffix ist OK; Carina darf auch alternative Sigle wählen. Default fürs Kernteam-Skript: `ARI_<KÜRZEL>` (z.B. `ARI_MUE279`) |
| Lizenz | **CC BY-SA 4.0** für alles. Carinas Quell-Lizenz ist BY-SA, dessen Share-Alike-Klausel ist mit BY-NC-SA inkompatibel. Daher übernehmen wir BY-SA für Daten **und** MHDBDB-Annotationen (kein Lizenz-Stack wie im MHDBDB-Bestand). |
| Autor | „alles was sie haben" — Schreiber-Zuschreibungen falls vorhanden, sonst `person_anonym` |
| Edition | Druckausgabe als `<biblStruct>`; bei eigenen Änderungen an der Druckedition expliziter Hinweis im Header |
| Genre | „Arithmetik" oder „Arithmetischer Lehrtext" aus der MHDBDB-Textreihentypologie (siehe https://www.marketext.at/Textreihentypologie/?page_id=30); Genre-IDs aus `genres.xml` lookupen |

## PD-001 entschieden (2026-05-08, Katharina + Christian)

**Beschluss: Mittelweg.** Alle 12 Element-Klassen aus Carinas Daten kommen als optionale Elemente ins MHDBDB-Hauptschema. In `docs/TEI-MODEL.md` werden sie klar getrennt nach „Pflicht-Bestand für jedes Korpus" und „Domain-Erweiterung Arithmetik (optional)". Begründung: alle 12 Elemente sind TEI-P5-Standard, kein Erfinden neuer Tags. Schema-Aufnahme heißt erlauben, nicht vorschreiben — Lyrik-Editor:innen müssen sie nie nutzen.

**Konkret aufzunehmen:**

| Kategorie | Elemente | Begründung |
|---|---|---|
| Editorisches TEI-P5-Standard-Vokabular | `<unclear>`, `<add>`, `<gap>`, `<abbr>`, `<expan>`, `<am>`, `<g>` | Genre-agnostisch nützlich für jede edition-with-apparatus-Aufnahme. Katharina explizit: `<unclear>` war früher kursiv im Bestand, ist verloren gegangen, soll wieder rein. |
| Onomastik (TEI-P5-Standard) | `<roleName>`, `<occupation>`, `<placeName>` | Generisch nützlich für alle Korpora mit Personen- oder Ortsbezug |
| Domain-Erweiterung Arithmetik (optional) | `<unit>`, `<rs>`, `<figure>`, plus 24 zusätzliche `<div>/@type`-Werte (`outline`, `commodity_calculation`, `reckoning_example`, `fraction_calculation`, `regula_de_tri`, …), plus `<hi rend>`-Tokens (`superscript`, `subscript`, `line-through`, `heading`, `underline`) | Forschungsspezifisch für Rechenbücher. Klassifikation als „Domain-Erweiterung" in der Doku, im Schema als optional. |

**Folge-Tasks (post-Schema-Aufnahme):**

1. **Begriffssystem-Anbindung** für `<unit>` und `<rs>`: damit Maßeinheiten und Währungen über die MHDBDB-Suche auffindbar sind, müssen sie auf `concepts.xml` verlinken (via `@ana="concepts.xml#concept_NNNN"`). Mapping-Aufgabe gemeinsam mit Carina.
2. **Reading-View-Render-Policy**: TEI darf reich sein, Frontend rendert sparsam. Konkret: Abbreviaturen auflösen (`<expan>`-Form anzeigen). Bruch-Display, Figur-Rendering, Rechnungs-Darstellung sind separate, **förderbare** Baustellen für die Zukunft.
