# #118: Sprachstufen im TEI-Header – Konzept-Entscheidungsvorlage

Temporal Artifact (Promptotyping-Konvention): lebt, solange #118 offen ist.
Erstellt 2026-07-12 (autonome Session) als Entscheidungsvorlage für KZW/Team.
Es ändert nichts an den Daten; Umsetzung erst nach Freigabe der Optionen unten.

## Ausgangslage

Alle 667 Header tragen pauschal `<langUsage><language ident="gmh"/></langUsage>`.
Das ist für die Mehrheit korrekt, aber nachweislich zu grob:

- **FNHD-Texte:** Rechenbücher (ARITHMETIC #92, künftig), Fecht-/Kochbücher
  (AC2/AC3, CEFB, KFB ...), PL1-3, PUC u. a. sind frühneuhochdeutsch.
- **Nicht-deutsche Passagen:** WZB enthält lateinische und tschechische
  Passagen (Julias Befund in #28, 2026-06-10), Eckhart-Texte lateinische
  Zitate. Token-Ebene ist Gegenstand von #28, nicht von #118; aber
  `<langUsage>` sollte die Textsprachen summarisch korrekt nennen.
- Prosa/Vers oder Datierung liegen teils in Header-Metadaten, teils in
  works.xml, teils extern (Handschriftencensus) vor.

## Vorschlag Zielformat (Option A, empfohlen)

TEI-konform mehrere `<language>` mit `@usage` (Prozent, grob gestuft):

```xml
<langUsage>
  <language ident="gmh" usage="95">Mittelhochdeutsch</language>
  <language ident="la" usage="5">Lateinische Zitate</language>
</langUsage>
```

- **Codes:** BCP-47/ISO 639. `gmh` (Mittelhochdeutsch; der ISO-639-3-Umfang
  reicht bis ca. 1500 und deckt Teile des FNHD mit ab) und `gml`
  (Mittelniederdeutsch) existieren als ISO-639-3-Codes. Die Schwellen 1350/1450
  im Regelgerüst unten sind Projekt-Konvention, nicht ISO-Definition. **Frühneuhoch-
  deutsch hat keinen eigenen ISO-Code** – Entscheidungsbedarf:
  - A1 (empfohlen): private-use-Subtag **`de-x-fnhd`** (BCP-47-konform,
    selbstdokumentierend; Muster für weitere Stufen erweiterbar)
  - A2: pauschal `de` mit Klartext im Elementinhalt (verliert Suchbarkeit)
  - A3: `gmh` behalten und FNHD nur im Klartext nennen (Status quo plus,
    wissenschaftlich unsauber)
- Der Elementinhalt (Klartext) bleibt menschenlesbar deutsch.

## Datenquellen und Ableitungsregeln (Priorität absteigend)

1. **Vorhandene Header-Metadaten:** Datierung der Handschrift/des Texts
   (`<origDate>`, `<date>` in msDesc/biblStruct, sofern vorhanden).
2. **works.xml:** Entstehungszeit des Werks, Gattungszuordnung.
3. **Handschriftencensus** (via vorhandener HSC-Verweise in den Headern):
   Datierung + Schreibsprache; nur lesend, als Evidenz protokolliert.
4. **Wikidata/GND:** nur als Anstoß (Issue-Vorgabe), nie allein entscheidend.
5. **Korpus-Empirie als Plausibilitätscheck:** FNHD-Indikatorformen
   (Diphthongierung: ei/au/eu-Schreibungen für mhd. î/û/iu) pro Text zählen;
   rein diagnostisch, keine automatische Zuweisung.

Regelgerüst (Entwurf, an ~20 Kalibrier-Texten festzuziehen):

| Evidenz | Zuweisung | Unsicherheitsstufe |
|---------|-----------|--------------------|
| Datierung <= 1350 und keine FNHD-Indikatoren | gmh (Status quo) | sicher |
| Datierung >= 1450 oder starke FNHD-Indikatoren | de-x-fnhd | sicher |
| 1350-1450 oder widersprüchliche Evidenz | Kandidatenliste -> Review | unsicher |
| Belegte Fremdsprach-Passagen (WZB, Eckhart) | Zweitsprache ergänzen | je Beleg |

## Prozess (dreiphasig, analog #28-Phasenplan)

1. **Kalibrierung:** ~20 Beispielfälle über das Spektrum (sicher gmh, sicher
   fnhd, Grenzfälle, Mischtexte) mit Evidenz-Tabelle an KZW; daraus Regeln
   fixieren (analog der Lehnwort-Grenzziehung in #28).
2. **Batch:** Skript ordnet alle 667 Texte den Stufen zu, schreibt
   Evidenz-Log (Quelle je Zuweisung) + Review-Paket der unsicheren Fälle.
   Kein Header-Write vor KZW-Sichtung der Unsicheren.
3. **Anwendung + Lifecycle:** Header-Edits per Skript mit revisionDesc-
   Eintrag; `<langUsage>` steht nicht im Corpus-Index (kein Index-Bump
   nötig), aber `api/texts/*.json` exponiert Header-Metadaten -> API-Rebuild
   prüfen; Schema: `<language>` erlaubt `@usage` bereits in tei_all,
   `schema/mhdbdb.rnc` ist zu prüfen (ggf. Produktion erweitern, Daten vor
   Schema beachten: hier ist es eine echte Modell-Erweiterung, kein
   Aufweichen).

## Aufwand und Abhängigkeiten

- Kalibrierung + Regelfixierung: 1 Session + KZW-Feedback
- Batch + Review-Paket: 1 Session; Anwendung: klein
- Synergie mit #28 (Fremdsprachen auf Token-Ebene): gemeinsame
  BCP-47-Policy; #28-Phase-0-Entscheidung sollte die Codes für beide
  Ebenen festlegen, damit Header- und Token-Ebene nicht divergieren.
- Blockiert nichts; Issue ist als future plans/nachrangig markiert.

## Entscheidungsbedarf (KZW/Team)

1. Zielformat: Option A mit A1 (`de-x-fnhd`) – ja/nein?
2. `@usage`-Prozentangaben: grob gestuft (95/5) oder weglassen, wenn nicht
   belegbar?
3. Schwellen des Regelgerüsts (1350/1450) – plausibel aus philologischer
   Sicht?
4. Reihenfolge: vor oder nach #28-Phase 1 (Empfehlung: Code-Policy gemeinsam
   in #28 Phase 0 festlegen, Umsetzung von #118 danach unabhängig)?
