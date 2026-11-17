Ergebnis des Laufs vom 2026-11-17 nach `docs/playbooks/BALL-RUECKGABE.md`, auf dem Stand von #44 aus dem Lauf `issue-matrix.yml` vom 2026-11-16T12:53:50Z: 1 von 1 Eintrag, 0 schon vorgelegt.

Herkunft der Zahlen in dieser Zeile: `gh api repos/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44 --jq .body` (Zeile `| **Ball bei uns (1)** |` zwischen den MATRIX-Markern, ein Eintrag: #262 für Katharina), `gh api "repos/DigitalHumanitiesCraft/mhdbdb-tei-only/actions/workflows/issue-matrix.yml/runs?per_page=1" --jq '.workflow_runs[0].created_at'` für das Datum. Schon vorgelegt: 0, der Antwort-Link `issuecomment-6914924044` steht in keiner früheren Datei unter `docs/playbooks/routinen/` (`grep -c`). Offene PRs mit Kopf `claude/ball-rueckgabe-*`: keine (offen sind nur `claude/doku-check-2026-11-16` und `fyndling/139-gegenprobe`).

Gelaufen als wöchentliche Cloud-Routine. Geschrieben wurde nichts außer dieser Datei: kein Kommentar, kein Label, kein Ping.

## Übersicht

| Ticket | Person | Klasse | ein Satz |
|---|---|---|---|
| #262 | Katharina | B | Katharina hat bestätigt, dass `apk_free.xml` auf ihrem OneDrive liegt; offen ist, wer die Mail nach Trier schickt. |

Zusammen: A 0, B 1, C 0, D 0, Summe 1.

**Seit der Antwort geschehen:** `git log origin/main --since=2026-11-16 -E --grep="#262([^0-9]|$)"` gibt nichts aus, Stand `origin/main` = `0ea78f00b`. Seit dem 15.11. gibt es auf `main` genau einen Commit, eben `0ea78f00b` vom 16.11. (#711, Mantis-Textliste 2017). Er nennt #262 nicht, führt die Apokalypse aber in seiner CSV (`sources/mantis-textliste-2017/mantis-MHDBDB_TEXTE-2017-02-23-eintraege-1-50-von-97.csv`, Zeile 48: Eintrag `0000318`, Status `assigned`/`open`, zugewiesen an `klaus`, 2016-09-15, "Die Apokalypse Heinrichs von Hesler"). Der Text stand also schon 2016 auf der Planungsliste der alten MHDBDB und war am Stand der Liste (23.02.2017) noch offen; das passt zu Christians Befund vom 10.09., dass er im Korpus fehlt.

## Zum Posten (B)

Hinweis aus `CLAUDE.md` ("Who is on turn"): Eine Frage wird nur dann oben auf unseren letzten Kommentar editiert, wenn der neuer ist als ihre Antwort. Unser letzter Kommentar ist vom 06.10., ihre Antwort vom 16.11., also als **neuer Kommentar** posten.

### #262 (Katharina)

```
@wachauer Frage: Schreibst du die Mail nach Trier zur Nachnutzung der Hesler-Apokalypse (APK) selbst, oder soll Christian sie schicken?
```

Kontext darunter: Katharina hat am 16.11. bestätigt, dass die Datei liegt (Pfad `MHDBDB/Backup SEMD_Sharefolder/MHDBDB_Inhaltliches/Texte/Neue Texte Klaus/apk_free.xml`, 1.565.852 Bytes, 21.02.2013, TEI.2 mit eingebettetem CSS-Block vom Browser-Export) und geschrieben: "Offen bleibt nur die Mail an Ute Recker-Hamm (Trier) zu den Nachnutzungsbedingungen" ([Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/262#issuecomment-6914924044)). Wer die Mail schickt, sagt der Thread nicht. Christian hat sie am 10.09. vorgeschlagen und dazu geschrieben "`wait:kzw` bleibt für die Mail"; das heutige `wait:kzw` ist aber erst am 06.10. neu gesetzt worden, mit der Begründung, dass die Datei auf ihrem OneDrive liegt (Label-Historie: `wait:kzw` am 23.09. entfernt, am 06.10. wieder gesetzt). Zugesagt hat Katharina die Mail nirgends. Eine Session darf Trier nicht selbst anschreiben (Betriebsvertrag Regel 4), deshalb der Entwurf unten.

Hinweis für den, der postet: Die Fragezeile bleibt unter den 140 Zeichen, die `frage_text()` in `scripts/audit/build-issue-matrix.py` in ihre Liste übernimmt, und stellt deshalb nur eine Frage. Der Dateiweg kommt als zweiter Absatz in denselben Kommentar, ohne eigene Frage-Zeile (gezählt wird nur die erste), postfertig:

```
Und unabhängig von der Mail: Damit eine Session Stage 0 vorbereiten kann, brauchen wir `apk_free.xml` außerhalb deines OneDrive. Am einfachsten schickst du die Datei an Christian; sie kommt in den DHCraft-Drive unter `Projekte/mhdbdb/extern/` und nicht ins Repo, solange die Bedingungen aus Trier nicht da sind.
```

Ob Katharina selbst in diesen Drive-Ordner (Konto office@dhcraft.org, `sources/INVENTAR-ARCHIV.md`) schreiben kann, ist ungeprüft, deshalb der Weg über Christian.

Was die Quellen schon beantworten und deshalb nicht mehr gefragt wird:

- **Zeitraum:** Die Apokalypse Heinrichs von Hesler ist mittelalterlich, die Grenze "vor 1600" (`docs/RESEARCH.md`, Corpus Scope) ist nicht berührt; dort steht auch, dass das Trierer Textarchiv-Material die Grenze nie berührt.
- **Rechtsfrage zur Edition aus dem Kommentar vom 06.09.:** Nach der Rechtsgrundlage des Projekts (`docs/RESEARCH.md`, Rights Basis, § 76b UrhG-AT, 25 Jahre ab Erstveröffentlichung) fällt Helms Ausgabe von 1907 unter "Editionen, deren Erstveröffentlichung mehr als 25 Jahre zurückliegt, sind gänzlich unproblematisch". Der Kommentar vom 06.09. hatte das selbst schon so gesehen (die kürzere Frist für wissenschaftliche Ausgaben sei "längst abgelaufen"); sein Vorbehalt war, dass die Freigabe im Header von 2002 eine amerikanische Begründung trägt und nach österreichischem Recht angesehen werden sollte. Für die Edition beantwortet das die Rights Basis. Offen bleibt nur die Seite der Trierer bzw. Virginia-Konversion von 2002, und das ist genau die Mail.
- **Bytezahl:** stimmt mit `sources/archiv-inventar.csv` überein (`Neue Texte Klaus,apk_free.xml,.xml,text,1565852,2013-02-21`).

Mail-Entwurf zum Mitposten (Kern aus Christians Kommentar vom 10.09., Frage 1 dort ist durch Katharinas Fund beantwortet):

```
Betreff: Nachnutzung der MHGTA-Fassung der Apokalypse Heinrichs von Hesler (HeslApk) in der MHDBDB

Sehr geehrte Frau Recker-Hamm,

in einem Backup der Mittelhochdeutschen Begriffsdatenbank (Universität Salzburg) liegt die
TEI.2-Fassung der Apokalypse Heinrichs von Hesler (ed. Helm, DTM 8, 1907) aus dem Digitalen
Mittelhochdeutschen Textarchiv, konvertiert 2002 am Electronic Text Center der University of
Virginia. Wir würden den Text gern in unser TEI-Korpus aufnehmen (https://dhcraft.org/mhdbdb-tei-only/,
Daten unter CC BY-NC-SA 4.0), mit Lemmatisierung und Nennung von Trier und Virginia im Header.

Unter welchen Bedingungen ist das möglich, und gibt es eine neuere Fassung als die von 2002,
von der wir besser ausgehen?

Mit freundlichen Grüßen
```

Absender, Anrede und Unterschrift setzt, wer schickt. Die Lizenzangabe CC BY-NC-SA 4.0 steht in `LICENSE-DATA`.

**Labels:** stimmen für die Frage (`auto:blocked`, `wait:kzw`, `ingest`, `area:data`, `effort:large`). Ist die Mail verschickt, wird `wait:kzw` zu `wait:extern` (Trier), sobald Katharina weder die Mail noch die Datei mehr schuldet.

Belege: [Antwort](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/262#issuecomment-6914924044); Mail-Vorschlag im [Kommentar vom 10.09.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/262#issuecomment-5621484163); Frage und heutige Labelbegründung vom 06.10. im [Kommentar 6010143398](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/262#issuecomment-6010143398); Rechtsvorbehalt im [Kommentar vom 06.09.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/262#issuecomment-5561806808). Label-Historie: `gh api --paginate .../issues/262/events` (labeled/unlabeled). Thread vollständig gelesen: Body plus 6 Kommentare (`gh api --paginate .../issues/262/comments`).

## Zum Schließen oder Umlabeln (D)

Keine.

## Auftrag für eine autonome Session (A)

Keiner. Der Ingest von #262 (Stage 0 bis Phase 3 nach `docs/DATA-MODEL.md`) wird erst ein Arbeitspaket, wenn die Datei erreichbar und die Antwort aus Trier da ist.
