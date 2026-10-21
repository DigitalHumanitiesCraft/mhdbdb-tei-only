# #118: Sprachstufen im TEI-Header – Konzept-Entscheidungsvorlage

Temporal Artifact (Promptotyping-Konvention): lebt, solange #118 offen ist.
Erstellt 2026-07-12 (autonome Session) als Entscheidungsvorlage für KZW/Team.
Es ändert nichts an den Daten; Umsetzung erst nach Freigabe der Optionen unten.

**Stand 2026-10-21:** erweitert auf Datierung und Raum, die Sprachstufe wird
daraus abgeleitet. Entscheidungsfragen 1, 2 und 4 sind von chsteiner
entschieden, offen bei KZW sind nur noch Frage 3 und die neue Frage 5
([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/118#issuecomment-6315624072)).

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
- **Nachgemessen (06.09. und 21.10.2026):** keiner der 667 Header hat
  `<creation>`, `<origDate>` oder `<origPlace>`. In `works.xml` stehen nur
  Druck- und Editionsjahre. Die Datierung muss also erst beschafft werden.

## Zielformat Sprachstufe (Option A1, entschieden 2026-10-21)

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
- **Entschieden:** A1, also `de-x-fnhd`. `@usage` steht nur, wo ein Anteil
  belegt ist, geschätzte Prozentwerte gibt es nicht. Die Codes gelten für
  Header- und Token-Ebene, #28 übernimmt sie, #118 wartet nicht auf #28.

## Datierung und Raum (entschieden 2026-10-21)

Werk und Handschrift werden getrennt erfasst:

- **Werk (Entstehung):** `profileDesc/creation` mit
  `<origDate notBefore="…" notAfter="…" source="…">` und
  `<origPlace source="…">`. Gepflegt in `works.xml` und in die Header
  generiert, nach dem Muster der Identifier aus #399.
- **Handschrift (Überlieferung, Schreibsprache):** `msDesc/history/origin`.
  Gemeint ist die Leithandschrift der Edition. Sie steht nirgends
  maschinenlesbar, das Feld bleibt bis dahin leer.
- **Was der Handschriftencensus für das Werk hergibt:** nur eine Obergrenze
  (`notAfter` = späteste Grenze der ältesten datierten Handschrift), keine
  Untergrenze. Die Schreibsprachen der Überlieferung sind ein
  Überlieferungsprofil, nicht der Entstehungsraum.
- Die Editionen sind oft normalisiert. Aus der Sprachgestalt des Korpustexts
  wird deshalb kein Raum abgeleitet.
- **Zwischenlager:** `ingest/datierung-118/`, zwei Tabellen: Handschriften
  mit den wörtlichen Angaben (primär) und Werke mit der abgeleiteten
  Obergrenze, dazu eine Sicht je Sigle. Schlüssel ist das Werk über
  `msIdentifier/@corresp`, nicht die Sigle (CONTRACTS §F.4, TRO). Ohne Beleg
  kommt nichts ins TEI. Unbekannt bleibt leer.
- **Lizenz des Zwischenlagers:** der Handschriftencensus ist CC BY-SA 4.0,
  nicht unter `LICENSE-DATA` (CC BY-NC-SA) weitergebbar (RESEARCH.md →
  License compatibility). Entschieden (chsteiner, 2026-10-21): Dual-Lizenz,
  `ingest/datierung-118/` steht unter CC BY-SA 4.0 mit eigener LICENSE.
- **Normalisierung per Skript:** Angaben wie „um 1200" werden nach fester
  Konvention in `notBefore`/`notAfter` aufgeweitet, der Name der Regel steht
  in einer eigenen Spalte. Der Legacy-Export macht es anders: er lässt
  `Datum von`/`Datum bis` eng und führt die Unschärfe getrennt in
  `Datum Abweichung` (FH: 1255, 1255, 5). Datiert eine Quelle nur den Autor
  und nicht den Einzeltext, ist das eine eigene Unsicherheitsstufe.
- **Schema:** `schema/mhdbdb.rnc` kennt heute weder `creation` in
  `profileDesc` noch `history` in `msDesc` noch `@usage` an `language`. Die
  Erweiterung kommt mit dem ersten Daten-PR.

## Datenquellen und Ableitungsregeln (Priorität absteigend)

1. **Vorhandene Header-Metadaten:** Datierung der Handschrift/des Texts
   (`<origDate>`, `<date>` in msDesc/biblStruct, sofern vorhanden).
   Gemessen: leer.
2. **works.xml:** Entstehungszeit des Werks, Gattungszuordnung. Gemessen:
   keine Entstehungsdaten, nur Druckjahre.
3. **Handschriftencensus** (via vorhandener HSC-Verweise in den Headern):
   355 von 667 Headern tragen eine HSC-ID, 311 verschiedene (21.10.2026).
   Das sind **Werk-IDs**. Die Werkseite listet nur die Überlieferung
   (Parzival: 88 Handschriften), `/werke/N.json` trägt die VL-Fundstelle
   (`vlverweis`). Datierung und Schreibsprache stehen erst je Handschrift
   (`/N.json`: `entstehungszeit`, `schreibsprache`, Freitext mit
   Literaturverweis). Nur lesend, als Evidenz protokolliert.
4. **Wikidata/GND:** nur als Anstoß (Issue-Vorgabe), nie allein entscheidend.
5. **Legacy-Export** `docs/data/linecode-templates.csv`: `Datum von`,
   `Datum bis` und `Datum Abweichung` mit Zitaten aus VL und GND, befüllt in
   22 von 665 Zeilen (21.10.2026). Keine Raumspalte (`ORIGIN` ist
   Stoffgeschichte).
6. **Verfasserlexikon (²VL):** Hauptquelle für die Werkdatierung. Es ist
   Teil der Verfasser-Datenbank (VDB) von De Gruyter Brill, dort als
   Publikation „Die deutsche Literatur des Mittelalters", neben dem Killy
   (Probe 21.10.2026 über den Zugang der Universität Graz). Die Fundstelle
   je Werk liefert der Handschriftencensus in `vlverweis`, wo er eine führt.
   Übernommen werden nur Datierungs- und Raumangaben als Tatsachen mit
   Fundstelle, kein Artikeltext. Maschinelle Auswertung nach § 42h UrhG
   (Abs. 1: wer rechtmäßig Zugang hat, darf für eine Forschungseinrichtung
   automatisiert auswerten, Abs. 5: vertraglich nicht abdingbar,
   Schutzmaßnahmen nur soweit für Sicherheit und Integrität nötig). Die
   Probe stieß nach vier Seitenaufrufen auf eine Verifizierungsseite, die
   nicht umgangen wird. Anfrage an De Gruyter und an den Handschriftencensus
   über KZW (21.10.2026). Bis zur Antwort nur Erhebung von Hand. Die
   Rechtsangaben sind am Gesetzestext gelesen, nicht juristisch geprüft.
   Die 312 Header ohne HSC-ID sind die zweite Welle, über die Suche in der
   VDB.
7. **Korpus-Empirie als Plausibilitätscheck:** FNHD-Indikatorformen
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
   `schema/mhdbdb.rnc` nicht (geprüft 2026-10-21, ebenso fehlen `creation`
   und `history`, siehe oben). Das ist eine echte Modell-Erweiterung, kein
   Aufweichen.

## Aufwand und Abhängigkeiten

- Kalibrierung + Regelfixierung: 1 Session + KZW-Feedback
- Batch + Review-Paket: 1 Session; Anwendung: klein
- Synergie mit #28 (Fremdsprachen auf Token-Ebene): gemeinsame
  BCP-47-Policy. Seit 2026-10-21 legt #118 die Codes für beide Ebenen fest,
  #28 übernimmt sie.
- Die Datierung ist zuerst ein Beschaffungsprojekt (Handschriftencensus,
  VL), erst danach greift das Regelgerüst.
- Blockiert nichts; Issue ist als future plans/nachrangig markiert.

## Entscheidungsbedarf (KZW/Team)

1. Zielformat: Option A mit A1 (`de-x-fnhd`) – ja/nein?
   **Entschieden 2026-10-21 (chsteiner): A1.**
2. `@usage`-Prozentangaben: grob gestuft (95/5) oder weglassen, wenn nicht
   belegbar? **Entschieden 2026-10-21 (chsteiner): nur belegt, sonst weglassen.**
3. Schwellen des Regelgerüsts (1350/1450) – plausibel aus philologischer
   Sicht? **Offen, KZW.**
4. Reihenfolge: vor oder nach #28-Phase 1 (Empfehlung: Code-Policy gemeinsam
   in #28 Phase 0 festlegen, Umsetzung von #118 danach unabhängig)?
   **Entschieden 2026-10-21 (chsteiner): die Codes oben gelten für beide
   Ebenen, #118 wartet nicht auf #28.**
5. Neu 2026-10-21: Welche Quelle gilt, wenn sich VL, Edition und
   Handschriftencensus bei Datierung oder Raum widersprechen? **Offen, KZW.**
