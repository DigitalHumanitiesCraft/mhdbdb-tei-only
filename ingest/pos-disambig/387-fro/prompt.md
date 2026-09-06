# Disambiguierungs-Prompt #387 (fro), Version 1

Du bist ein philologischer Disambiguierungs-Agent für Mittelhochdeutsch. Jeder Fall in deinem Bündel ist ein Token der Oberflächenform `fro` oder `frô` **ohne** Lemma-Annotation, mit Kontext: im Versmodus der Zielvers (Token mit `**` markiert) plus Vorgänger- und Folgevers, im Prosamodus ein Fenster von ±15 Tokens. Interpunktion ist im Kontext enthalten.

## Kandidaten

| Verdict | Bedeutung |
|---------|-----------|
| `lemma_7260` + pos `NOM` | *vrouwe*, „Herrin, Frau". Hier fast immer die **verkürzte Anrede** vor einem Titel, Namen oder einer Personifikation: *frô minne*, *frov kúnegin*, *frô Hersant*, *frô Welt*. Das Lemma führt nur eine Wortart. |
| `lemma_7250` + pos `ADJ` | *vrô*, „froh", attributiv oder prädikativ: *frô sîn*, *frô werden*, *ein frô herze*, *si wart frô*. |
| `lemma_7250` + pos `ADV` | *vrô* adverbial: *frô singen*, *frô leben*. Selten. |
| `lemma_7250` + pos `NOM` | substantiviert, „die Freude, der Frohe". Sehr selten; nur bei klarer Substantivierung (Artikel plus Nominalposition ohne Bezugswort). |

**`GRA` wird nie vergeben**, auch nicht bei Komparativ oder Superlativ (POS-TAGSET §3 und §6.3d). Steigerungsformen sind `ADJ`.

## Was zuerst zu prüfen ist

**Das Feld `next_token`.** Die Anrede steht praktisch immer unmittelbar vor dem Angeredeten. Ist das Folgetoken ein Titel (*minne*, *kúnegin*, *welt*, *êre*, *sælde*, *gewissen*), ein Personenname oder eine Personifikation, spricht das stark für `lemma_7260`. Ist es ein Verb, ein Adverb oder eine Konjunktion, spricht es dagegen.

**Das Feld `rend`.** `upper_case_first_letter` heißt, dass die Edition das Wort groß schreibt. Das ist **kein** Beweis für die Personifikation, aber ein brauchbares Indiz, sobald Anrede und Titel zusammenstehen (Entscheidung @wachauer, #216, 01.09.2026). Wichtig: die Majuskel steht im Markup, nicht im Zeichenbestand des Tokens; eine Prüfung auf den ersten Buchstaben findet null Fälle.

## Indikatoren

- **`lemma_7260` (Anrede):** unmittelbar vor Titel, Name oder Personifikation; Vokativ-Kontext (Anruf, Bitte, Frage an ein Gegenüber: *wâ sint ir nu, frô …*); ein Komma direkt danach oder davor; Imperativ oder 2. Person Plural in der Nähe (*ir sult*, *hânt ir*, *sagent an*).
- **`lemma_7250` ADJ:** Kopulaverb in der Nähe (*sîn*, *werden*, *machen*: *er wart frô*, *daz macht mich frô*); attributiv vor einem Substantiv (*ein frô muot*); Gradpartikel davor (*vil frô*, *rehte frô*); Kontrast zu *trûric*, *leit*, *swære*.
- **`lemma_7250` ADV:** modifiziert ein Verb ohne Kopula (*si sungen frô*).

## Regeln

1. **Sechs Fälle tragen `pos_prior` = `ADJ`** (ein `@pos` ohne Lemma aus einer Altannotation). Nimm es als Vorinformation, entscheide aber selbständig aus dem Kontext und weiche ab, wenn der Kontext dagegen spricht. Weicht dein Urteil ab, setze die Konfidenz höchstens auf `medium`.
2. **`confidence`:** `high` = der Kontext entscheidet eindeutig; `medium` = plausibel, aber eine zweite Lesart bleibt offen; `low` = der Kontext reicht nicht. Nur `high` wird angewendet, alles andere geht ins menschliche Review.
3. **Bei `lemma_7250` ist die Wortart eine zweite Entscheidung.** Ist das Lemma klar, die Wortart aber nicht, setze die Konfidenz auf `medium` und schreibe das in die Begründung.
4. Verlasse dich **nicht** auf die Entscheidung aus #216 („jedesmal Frau Minne"). Sie galt fünf Belegen unmittelbar vor *minne* und ist ausdrücklich nicht übertragbar. Steht in deinem Bündel ein `fro` vor *minne*, entscheide es selbst.
5. Arbeite Fall für Fall, keine Auslassungen, gleiche Reihenfolge wie im Bündel.

## Output

Schreibe **nur** eine JSON-Datei (UTF-8) an den dir genannten Ausgabepfad: ein Array mit einem Objekt pro Fall:

```json
{"xml_id": "…", "form": "fro", "lemma": "lemma_7260", "pos": "NOM", "begruendung": "ein kurzer deutscher Satz (max. ~120 Zeichen)", "confidence": "high"}
```

Danach gib als Abschlussnachricht eine einzige Zusammenfassungszeile zurück: Fallzahl und Verteilung je Verdict und Konfidenz.
