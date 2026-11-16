# Mantis-Textliste 2017: die einzige erhaltene Seite des alten Bugtrackers

Nicht normativ, siehe [`../README.md`](../README.md). Nichts hier wird indexiert oder von
einem Skript gelesen. Die Datei ist eine historische Quelle zur Textaufnahme der MHDBDB in
den Jahren 2015 bis 2017 und der Beleg für die Ingest-Desiderata in #710.

## Herkunft

Die MHDBDB führte bis mindestens Februar 2017 (Datum der Sicherung) einen Mantis-Bugtracker
unter `www.mhdbdb.sbg.ac.at:8300/mantis/`, nicht nur für Softwarefehler, sondern als
Arbeitsliste der Redaktion. Vier Projekte waren dort angelegt (`MHDBDB`, `MHDBDB_NEU`,
`MHDBDB_ORG`, `MHDBDB_TEXTE`); die Ticketnummern reichen bis mindestens 345. Die
Ticket-Datenbank (laut `config_inc.php` der erhaltenen Installation: Name `bugtracker`,
Typ `mysql`; gelesen von KZW auf dem Server am 2026-11-16) ist beim Serverumzug vom
1. August 2023 nicht mitkopiert worden und gilt seit dem 16. November 2026 als verloren
(Entscheidung KZW). Das Internet Archive hat keine Aufnahme von Port 8300 (CDX-Abfrage,
2026-11-16, Kontrolle: die Startseite `www.mhdbdb.sbg.ac.at/` ist seit 2002 archiviert).

Erhalten ist eine einzige Seite: die Ansicht „View Issues" des Projekts `MHDBDB_TEXTE`, als
Browser-Sicherung vom 23. Februar 2017, 09:22 CET, angemeldet als `katharina`. Sie liegt im
Archiv bei KZW (`MHDBDB_Inhaltliches/Texte/Sicherheitskopie Textliste MANTIS/`, Zeile 5008
in [`../archiv-inventar.csv`](../archiv-inventar.csv): `TEXTLISTE - View Issues - MantisBT.htm`,
69.285 Byte, sha256 `453ff60c20c5bf44e917a870787b0b675d5a423e9c42239dbd74c7ee943c7fb0`);
eine Kopie mit Stilen liegt im privaten Obsidian-Vault unter
`Quellen/Mantis-Sicherung-2017-02-23/`.

Die Seite zeigt die Einträge 1 bis 50 von 97, sortiert nach letzter Änderung absteigend
(Filterkopf: „Sort by: Updated Descending", „Hide Status: none"). Die zweite Seite
(Einträge 51 bis 97) ist nicht gesichert; aus der Sortierung folgt, dass ihre 47 Einträge
alle eine letzte Änderung am oder vor dem 2015-11-25 haben.

## Dateien

| Datei | Inhalt |
|---|---|
| `mantis-MHDBDB_TEXTE-2017-02-23-eintraege-1-50-von-97.csv` | Die 50 Einträge, aus dem HTML extrahiert. Trenner `;`, UTF-8 |
| `mantis-MHDBDB_TEXTE-2017-02-23.png` | Die Seite, gerendert aus der HTML-Sicherung (Playwright, 2026-11-16) |

Spalten der CSV: `ticket_id`, `prioritaet` (aus dem `title` des Symbols in Spalte „P":
49 `normal`, 1 `high`), `notizen` (Anzahl Notizen, 48 leer), `anhang` (50 leer),
`kategorie` (50 mal „Inhaltlich (MHD)"), `schweregrad`, `status`, `aufloesung` (aus dem
`title` des Status-Elements: 3 `fixed` bei den `resolved`, 47 `open`), `bearbeiter`,
`aktualisiert`, `titel`. Drei Abweichungen von der Quelle, die Werte betreffen: die
Status-Zelle „assigned (katharina)" ist in `status` und `bearbeiter` zerlegt, die Zeilen
sind nach `ticket_id` aufsteigend sortiert statt nach Änderungsdatum absteigend, und die
zwei Spalten links ohne Kopf (Auswahlkästchen mit der Ticketnummer als Wert, Bearbeiten-Link)
sind weggelassen, weil sie nichts Eigenes tragen.

## Was die 50 Zeilen sagen (gezählt aus der CSV)

- Status: 24 `new`, 15 `confirmed`, 8 `assigned`, 3 `resolved`.
- Bearbeiter: Klaus 6 Einträge (3 `resolved`, 3 `assigned`), Katharina 5 (`assigned`).
- Zuletzt geändert zwischen 2015-11-25 (40 Einträge, offenbar die Anlage der Liste) und
  2017-01-25.
- Je Ticket ein Text oder eine Textgruppe („Marienlegenden", „Lehrdichtung"), die
  aufgenommen werden sollte. Welche davon heute im Korpus sind, steht nicht hier, sondern
  wird gegen `authority-files/works.xml` gemessen. Stand 2026-11-16 ließen sich 12 der 50
  Titel einer Sigle zuordnen (Stichwortabgleich plus Lesen, drei davon unsicher: MAG, WUT,
  RSP); die übrigen 38 stehen in #710.
