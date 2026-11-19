# Normdaten für die Hesler-Apokalypse: Vorschlag, nicht geschrieben

Stand 19.11.2026, #262. Nichts davon steht in `authority-files/`. Geschrieben wird es erst beim Schritt nach `tei/`, wenn Ute Recker-Hamm (MWB Trier) den Ingest gesehen hat. Bis dahin trägt der Header von `ingest/apk/APK.tei.xml` die Platzhalter `works.xml#work_TBD`, `#person_TBD` und `genre_TBD`.

Jede Kennung unten ist bei der Quelle selbst abgefragt, mit dem Link daneben. Was dort nicht steht, ist `UNKNOWN`.

## Person: Heinrich von Hesler

In `authority-files/persons.xml` fehlt er (`grep -i -c 'hesler\|heseler' authority-files/persons.xml` gibt 0, ebenso in `works.xml` und `names.xml`).

```xml
<person xml:id="person_NNNN">
  <persName type="preferred">Heinrich von Hesler</persName>
  <idno type="GND">118548387</idno>
  <idno type="wikidata">Q121644</idno>
</person>
```

| Angabe | Wert | Beleg |
|---|---|---|
| GND | 118548387 („Heinrich, von Hesler“, Lebensdaten 1270 bis 1347, Schriftsteller) | https://d-nb.info/gnd/118548387 (abgefragt über https://lobid.org/gnd/search?q=Heinrich+von+Hesler&filter=type:Person) |
| Wikidata | Q121644 („Heinrich von Hesler“, verweist mit P227 auf dieselbe GND 118548387) | https://www.wikidata.org/wiki/Q121644 |
| ID | `person_NNNN`: die nächste freie Nummer beim Schreiben. Am 19.11.2026 war die höchste `person_1772` (`grep -o 'person_[0-9]*' authority-files/persons.xml \| sort -t_ -k2 -n \| tail -1`) | |

Die Quelle selbst schreibt den Namen zweimal anders: „Heinrich von Heseler“ im `titleStmt` von `apk_free.xml`, „Heinrich von Hesler“ im `sourceDesc`. Eine alternative Namensform „Heinrich von Heseler“ ist daher denkbar, ist aber eine redaktionelle Entscheidung.

## Werk: Apokalypse

```xml
<bibl xml:id="work_NNN">
  <title xml:lang="de">Apokalypse</title>
  <title xml:lang="gmh" type="alternate" ana="historic">Dys ist Apokalipsis.</title>
  <idno type="sigle">APK</idno>
  <idno type="handschriftencensus">http://www.handschriftencensus.de/werke/488</idno>
  <ptr target="genres.xml#genre_f3daf714"/>
  <author ref="persons.xml#person_NNNN">Heinrich von Hesler</author>
  <relatedItem>
    <biblStruct type="book" xml:id="APK_APK" key="APK">
      <!-- wie im Header von ingest/apk/APK.tei.xml; corresp auf Zotero erst, wenn der Eintrag dort angelegt ist -->
    </biblStruct>
  </relatedItem>
</bibl>
```

| Angabe | Wert | Beleg |
|---|---|---|
| Sigle | `APK`, frei (`ls tei/APK*`: keine Datei; `grep -c '>APK<' authority-files/works.xml`: 0; beides am 19.11.2026) | |
| MWB-Sigle | `HeslApk` (steht im Header als `idno type="mwb-sigle"`) | https://mhdwb-online.de/textarchiv.php, festgehalten in #262 am 10.09.2026 |
| Handschriftencensus | Werk 488, „Heinrich von Hesler: 'Apokalypse'“ | https://handschriftencensus.de/werke/488 |
| GND (Werk) | 4343318-2, „Apokalypse“, Verfasser „Heinrich, von Hesler“ | https://d-nb.info/gnd/4343318-2 (lobid) |
| Wikidata (Werk) | Q139619460 „Die Apokalypse“, Ziel von P800 in Q121644. **Vorbehalt:** das Objekt ist als Übersetzungswerk modelliert und führt als Autor (P50) Johannes (Q44015), nicht Hesler, und es trägt keine GND. Ob die MHDBDB darauf verweisen will, ist offen. | https://www.wikidata.org/wiki/Q139619460 |
| Gattung | `genre_f3daf714` Bibeldichtung (Oberbegriffe Geistliche Literatur, Epik/Lyrik/Dramatik). Möglich als zweite Gattung: `genre_4a1c4ec3` Exegetischer Text (Bibelexegese, Bibelkommentar), weil Hesler den Text nicht nur nacherzählt, sondern Stück für Stück auslegt. `genre_bba5ba78` Offenbarungsschrift ist im Begriffssystem unter Mystik eingeordnet und passt deshalb weniger. **Entscheidung KZW.** | `authority-files/genres.xml`; 26 Werke tragen heute Bibeldichtung, keines Exegetischer Text (`grep -c` in `works.xml`) |
| ID | `work_NNN`: die nächste freie Nummer beim Schreiben. Am 19.11.2026 war die höchste numerische `work_668` | |

Beim Schreiben gilt die Kette aus `docs/DATA-MODEL.md` → Backward sync and registration: die Gattung kommt als `<ptr>` in `works.xml` und wiederholt sich im Header (`check-header-genres.py --check`), der Header-`biblStruct` muss zum `works.xml`-Eintrag passen (`sync_tei_headers.py --works --check`).
