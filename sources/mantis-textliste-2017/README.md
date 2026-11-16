# Mantis-Textliste 2017: die einzige erhaltene Seite des alten Bugtrackers

Nicht normativ, siehe [`../README.md`](../README.md). Nichts hier wird indexiert oder von
einem Skript gelesen. Die Datei ist eine historische Quelle zur Textaufnahme der MHDBDB in
den Jahren 2015 bis 2017 und dient als Beleg für Ingest-Desiderata.

## Herkunft

Die MHDBDB führte bis 2017 einen Mantis-Bugtracker unter `www.mhdbdb.sbg.ac.at:8300/mantis/`,
nicht nur für Softwarefehler, sondern als Arbeitsliste der Redaktion. Vier Projekte waren dort
angelegt (`MHDBDB`, `MHDBDB_NEU`, `MHDBDB_ORG`, `MHDBDB_TEXTE`); die Ticketnummern reichen bis
mindestens 345. Die Ticket-Datenbank (`bugtracker`, MySQL) ist beim Serverumzug vom
1. August 2023 nicht mitkopiert worden und gilt seit dem 16. November 2026 als verloren
(Entscheidung KZW). Das Internet Archive hat keine Aufnahme von Port 8300 (CDX-Abfrage,
2026-11-16, Kontrolle: die Startseite `www.mhdbdb.sbg.ac.at/` ist seit 2002 archiviert).

Erhalten ist eine einzige Seite: die Ansicht „View Issues" des Projekts `MHDBDB_TEXTE`, als
Browser-Sicherung vom 23. Februar 2017, 09:22 CET, angemeldet als `katharina`. Original auf
KZWs OneDrive (`MHDBDB_Inhaltliches/Texte/Sicherheitskopie Textliste MANTIS/`,
`TEXTLISTE - View Issues - MantisBT.htm`, 69.285 Byte, sha256
`453ff60c20c5bf44e917a870787b0b675d5a423e9c42239dbd74c7ee943c7fb0`); eine Kopie mit Stilen
liegt im privaten Obsidian-Vault unter `Quellen/Mantis-Sicherung-2017-02-23/`. Die Seite
zeigt Tickets 1 bis 50 von 97; die zweite Seite (51 bis 97) ist nicht gesichert.

## Dateien

| Datei | Inhalt |
|---|---|
| `mantis-MHDBDB_TEXTE-2017-02-23-tickets-1-50-von-97.csv` | Die 50 Tickets, aus dem HTML extrahiert, nach `ticket_id` sortiert. Trenner `;`, UTF-8 |
| `mantis-MHDBDB_TEXTE-2017-02-23.png` | Die Seite, gerendert aus der HTML-Sicherung (Playwright, 2026-11-16) |

Spalten der CSV: `ticket_id`, `notizen` (Anzahl Notizen, meist leer), `anhang` (leer),
`kategorie` (durchgehend „Inhaltlich (MHD)"), `schweregrad`, `status`, `bearbeiter`,
`aktualisiert`, `titel`. Alle Werte stehen so in der Quelle; nichts wurde ergänzt oder
normalisiert.

## Was die 50 Zeilen sagen (gezählt aus der CSV)

- Status: 24 `new`, 15 `confirmed`, 8 `assigned`, 3 `resolved`.
- Bearbeiter: Klaus 6 Tickets (3 `resolved`, 3 `assigned`), Katharina 5 (`assigned`).
- Zuletzt geändert zwischen 2015-11-25 (40 Tickets, offenbar die Anlage der Liste) und
  2017-01-25.
- Je Ticket ein Text, der aufgenommen werden sollte. Welche davon heute im Korpus sind, steht
  nicht hier, sondern wird gegen `authority-files/works.xml` gemessen. Stand 2026-11-16 ließen
  sich 12 der 50 Titel einer Sigle zuordnen (Stichwortabgleich plus Lesen, drei davon
  unsicher: MAG, WUT, RSP); die übrigen 38 stehen im Ingest-Issue zu dieser Liste.
