# Kickoff Spur B: das Prüfseiten-Format aus #443 und seine erste Anwendung in #359

**1. Autorisierung.** chsteiner hat diesen Lauf am 21.09.2026 freigegeben. Dieser Text ist die Autorisierung. Er erteilt keine technische Berechtigung: was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt, siehe Baustein 9.

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text. Die Koordination ist wach und antwortet in Minuten. **Beide Vorgänge tragen `auto:checkin`, du sollst also unterwegs fragen. Tu das, statt zu schätzen.**

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees
2. `docs/playbooks/BETRIEBSVERTRAG.md`
3. `docs/playbooks/kickoffs/2026-09-21-datenlauf.md`, der Laufplan
4. `docs/DESIGN.md`, bevor du eine Zeile HTML oder CSS schreibst
5. **#443 und #359 mit allen Kommentaren**: `gh issue view N --json title,body,comments`. In diesem Projekt ist der Body regelmäßig der älteste und falscheste Text im Ticket, und bei #359 steht KZWs Entscheidung vom 16.09. ausschließlich im Thread

**Abbruchklausel:** weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es, statt es aufzulösen.

---

## 4. Dein Worktree

```
C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\mhdbdb-pruefseite
```

Zweig `worktree-mhdbdb-pruefseite`, angelegt aus `origin/main` bei `0d0404641`. `npm ci` ist dort gelaufen.

**Der Zweigname ist vom Werkzeug vergeben, nicht gewählt.** Du darfst auf einen sprechenden Arbeitszweig wechseln, aber dann bleiben beim Abbau zwei Zweige liegen statt einem; sag es der Koordination, wenn du es tust.

**Erste Handlung, vor allem anderen:** miss `pwd`, `git branch --show-current` und `git rev-parse --short HEAD`, halte sie gegen die drei Angaben oben und melde das Ergebnis. Bei Abweichung ändere nichts, melde und warte auf einen Neustart durch die Koordination. Du ziehst nicht selbst um.

---

## 5. Was dir gehört, und was nicht

**Dir allein:** der Generator der Prüfseite (leg ihn unter `scripts/review/` an, das Verzeichnis gibt es noch nicht), die erzeugten Seiten, und dein Review-Material unter `ingest/review/359-borek/`.

**Dir, falls dein Format dort andockt:** `playground/` und `assets/js/` im Übrigen. **Frag vorher**, ob es dort andocken soll: eine Prüfseite, die man verschickt und ohne Installation öffnet, ist möglicherweise gerade **nicht** Teil der Anwendung. Das ist die erste Entscheidung, die dein `auto:checkin` meint.

**Nicht deins, unter keinen Umständen:** `tei/`, `authority-files/`, `data/`, `api/`, `scripts/build-*.py`, `scripts/sync/`. Die gehören Spur A, die parallel an ihnen arbeitet. **Du liest sie für Belegstellen, du schreibst nicht hinein.** Fällt dir dabei ein Datenfehler auf, meldest du ihn, statt ihn zu beheben.

**Geteilt, und deshalb mit Regel:** `docs/JOURNAL.md` und `fehlerjournal.md` schreibst du anhängend und **als letzten Commit**, unmittelbar nach `git fetch origin`. Kein `merge`, kein `rebase`: du stehst auf einem eigenen Zweig, ein Fast-Forward scheitert dort. **Deine Fehlerjournal-Nummern sind 45 bis 49**, Spur A hat 40 bis 44.

**Dein eigenes Reviewer-Memory:** eine eigene Datei unter `.claude/agent-memory/fable-reviewer/`, nie eine gemeinsame Reihe.

**Eingefroren** (Liste und Grund im Laufplan): `CLAUDE.md`, die 15 promptotyping-Dokumente, `docs/playbooks/`, `.github/workflows/`, `scripts/audit/`. Willst du dort etwas geändert haben, meldest du den Wunsch mit Datei, Ankertext, wörtlichem Ersatztext und einem Satz Begründung. Die Koordination trägt ein.

**Nichts wirkt über deinen Baum hinaus.** Kein `git push` auf fremde Zweige, kein Eingriff in den Hauptcheckout, keine Änderung an globalen Einstellungen unter `~/.claude/`.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` ist vor deinem ersten Push Pflicht. Melde und warte, statt auf `fable-advisor` auszuweichen oder ohne Runde zu pushen.

**Ein maschinenweit exklusives Betriebsmittel: Port 8080**, und du bist der Grund, warum es hier steht. `npm run serve` und `npm test` belegen ihn, und Spur A muss testen können. **Du forderst ihn an, statt ihn zu nehmen**: melde, wenn dein Dev-Server anläuft, und melde, wenn er aus ist. Lass ihn nicht dauerhaft laufen, nur um deine Seite offen zu haben. Spur A hat Vorrang.

Die **Indexversionsnummern** sind ebenfalls exklusiv, gehören aber allein Spur A. Du bumpst nichts.

---

## 6. Die Pakete, in dieser Reihenfolge

**Die Reihenfolge #443 vor #359 ist entschieden und wird nicht neu verhandelt.** KZW verlangt sie wörtlich („Bitte hierzu auch #443 berücksichtigen"), Alans Anforderungen liegen vor, und #359 wäre sonst die vierte Einzelseite, gegen die #443 überhaupt geschrieben wurde.

**Die Umfangszahlen zu #359 stehen hier bewusst nicht.** Bei drei von drei nachgemessenen Datenvorgängen dieses Laufs war der Ticketkopf falsch, zweimal um mehr als die Hälfte. **Miss sie als erste Handlung nach dem Lesen und melde sie**, bevor du baust.

### B1: #443, das Basisformat

Eine HTML-Datei, die man verschickt und die ohne Installation im Browser aufgeht. Anforderungen stehen im Body, Alans drei Punkte ebenfalls. Bau es so weit, wie #359 es braucht, und nicht weiter.

**Was dieser Lauf ausdrücklich nicht tut: #443 abschließen.** Ob das Format die Grundlage aller künftigen Prüfseiten wird, entscheidet KZW nach dem ersten Gebrauch. Ein Format, das nach einer Anwendung als fertig erklärt wird, ist eine Behauptung über Fälle, die noch niemand gesehen hat.

**Eine Entscheidung, die du melden musst, bevor du sie triffst:** ob die Seite ihre Daten eingebettet trägt oder nachlädt. Eingebettet heißt verschickbar, aber ohne Aktualisierung; nachgeladen heißt aktuell, aber nicht verschickbar. Das ist die Grundfrage des Formats und keine Implementierungsdetailfrage.

### B2: #359, die erste Anwendung

Die Prüfseite für die Verdachtsfälle und Klassifikationskandidaten, gebaut mit B1, mit **begründeten** Vorschlägen für die Pferdebezeichnungen und Gangarten.

**Begründet heißt hier etwas Bestimmtes**, und es ist die wichtigste Regel dieses Auftrags. Aus `CLAUDE.md`, nach @wachauer: „Bei unsicheren Entscheidungen immer beim Mensch nachfragen, aber erst, nachdem alle seriösen Quelldaten (Normdaten, Lexika usw.) geprüft wurden."

Beide Hälften tragen. Die erste verbietet, eine unsichere Zuordnung als sicher in die Seite zu schreiben. Die zweite verbietet, KZWs Aufmerksamkeit für etwas auszugeben, was die Belegstellen beantwortet hätten. **Der praktische Griff: leg dir die Belegstellen mit Kontext vor, nicht das Stichwort.** Am 10.09. hat eine Session dieses Projekts `Alanya` aus dem Stichwort heraus für einen türkischen Ortsnamen gehalten; die sieben Belege im Korpus lesen sechsmal „der kuenc von alanye", also ein Land mit einem König. Eine Minute Lesen hätte gereicht.

Eine Seite mit 40 Vorschlägen, die alle aus dem Stichwort gebildet sind, macht diesen Fehler 40-mal, und sie sieht dabei aus wie sorgfältige Arbeit.

---

## 7. Wie gearbeitet wird

- **Deterministisch, wo es geht.** Die Seite wird von einem Skript erzeugt, nicht von Hand geschrieben. Ein Generator lässt sich erneut laufen, wenn KZW eine Änderung wünscht, eine handgeschriebene Datei nicht.
- **Defensiv parsen.** Eine unbekannte Eingabe ist ein harter Fehler und kein stilles Überspringen.
- **Keine Zahl in der Seite oder in einem Kommentar, die du nicht gemessen hast.** Was die Aussage nicht braucht, wird gestrichen statt belegt.
- **Vor neuen Skripten lies zwei oder drei bestehende** und halte dich an die Topologie (`scripts/README.md`).
- **Keine Emoji-Icons.** Heroicons als inline SVG ist der einzige Icon-Stil im Projekt.
- **Deutsche Prosa mit echten Umlauten**, schließende Anführungszeichen U+201C, **keine Em-Dashes**. Das Gate ist `scripts/audit/check-no-em-dash.py --diff-base main`, und es prüft HTML vollständig.
- **Führt dein HTML oder JS neue Tailwind-Klassen ein, läuft `npm run build:css` vor dem Push**, sonst fehlen sie im gepurgten Ausgabestand.

---

## 8. Vorab entschieden, nicht neu zu verhandeln

- **#443 zuerst**, #359 als erste Anwendung.
- **Nicht mergen.** Du öffnest einen PR und meldest. An ihm hängt KZWs Abnahme, und die kommt nach dem Merge und dem Deploy, nicht an einer PR-Vorschau.
- **Kein Ticket schließen.** Ein `Closes` ist keine Abnahme.
- **Relabeln**, was du anfasst, in derselben Session, plus ein Statuskommentar je Vorgang.

**Widerspruch ist ausdrücklich erlaubt**, auch gegen die vier Punkte oben, und er geht an die Koordination. Sie trägt ihn in den Laufplan ein, unter „Grenzverhandlungen", damit er nach dem Lauf noch gelesen wird. Ein Einwand in einem PR-Text ist verloren: den öffnet nach dem Merge niemand mehr.

**Eine Vorgabe hält die Koordination selbst für schwach, und hier ist die Ersatzfassung.** Dass #443 vor #359 kommt, ist entschieden. Nicht entschieden ist, **wie viel** von #443 vor #359 kommt, und die naheliegende Lesart („erst das Format fertig, dann anwenden") ist vermutlich die falsche: ein Format, das ohne echten Fall entsteht, löst die Probleme, die man sich vorstellt, statt der Probleme, die es gibt. Ersatzfassung, falls du nach dem Lesen zu diesem Schluss kommst: **bau beides verschränkt**, also das Format nur so weit, wie der nächste Schritt von #359 es braucht, und zieh es nach. Sag es, wenn du so vorgehst.

---

## 9. Melden und Halten

**Melden, dann weiterarbeiten:**

- nach dem Lesen: `pwd`, Zweig, HEAD gegen die Angaben in Baustein 4
- der **gemessene** Umfang von #359, bevor du baust
- Beginn und Ende jedes Dev-Server-Laufs, siehe Port 8080 unten
- Beginn und Ergebnis jeder Reviewrunde, mit Rundennummer **und der Kennung des geprüften Standes**

**Anhalten und warten:**

- `pwd` weicht ab
- eine Änderung würde eine fremde Datei berühren, besonders unter `tei/`, `authority-files/`, `data/` oder `api/`
- die Grundfrage aus B1 steht an: eingebettet oder nachgeladen
- ob das Format in `playground/` andockt
- der vorgeschriebene Agententyp fehlt
- **eine fachliche Zuordnung bleibt nach dem Lesen der Belegstellen unsicher.** Die kommt auf die Liste für KZW und nicht als Vorschlag in die Seite

**Ein eigener Fall, weder Melde- noch Haltepunkt: das Warten auf einen externen Zustand.** Ein CI-Lauf, ein `gh pr checks`. Dafür hältst du nicht an und meldest auch nicht, sondern **weckst dich selbst**: `Monitor` mit einer Bedingung, oder ein Hintergrundbefehl, der dich bei seinem Ende erneut aufruft. Pollen in einer Schleife mit `sleep` ist die falsche Antwort und kostet nur Kontext.

**Du darfst ein Paket für nicht durchführbar erklären.** Das ist etwas anderes als die Abbruchklausel aus Baustein 3: die greift, wenn eine Datei dem Auftrag widerspricht, und dann gilt die Datei. Hier geht es um den Fall, dass der Auftrag mit sich selbst stimmig ist und die Sache trotzdem nicht geht. Bei dir ist der wahrscheinlichste Fall, dass #359 nach dem Messen ein anderer Vorgang ist als der, den der Ticketkopf beschreibt. Dann sagst du das mit Messung, und du sagst es **früh**.

**Kein Messfenster, und das ist geprüft, nicht vergessen:** keines deiner beiden Pakete misst eine Bedingung, die vom Zustand deines eigenen Prozesses abhängt. Es gibt deshalb keine Funkstille-Zusage, und die Koordination darf dich jederzeit ansprechen.

**Blockiert der Auto-Mode-Classifier einen Werkzeugaufruf, schick sofort eine `PushNotification` an Christian**, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Das Werkzeug steht in keiner Werkzeugliste und lädt über `ToolSearch` mit `select:PushNotification`; eine Fehlermeldung beim ersten Griff heißt nicht, dass es fehlt, sondern dass es noch nicht geladen ist. Begründung in `rules/blockaden-melden.md`. **Umgeh eine Blockade nicht über die andere Spur**, Berechtigungen gelten je Session, und ein Peer, der es für dich tut, hebelt Christians Entscheidung aus.

---

## 10. Abschluss

1. `npm test`, und das Ergebnis ist die **VERDICT-Zeile**, nicht die Konsolenzusammenfassung und nicht der Exit-Code. Nie `npx playwright test` aus dem Wurzelverzeichnis, nie durch eine Pipe.
2. `fable-reviewer` **vor dem ersten Push**, Pflicht. Gib ihm mit: Zweig und Basis, ob du einen Commit oder den Arbeitsbaum prüfen lässt, das Ziel in einem Satz, die Rundennummer, ab Runde 2 die Vorbefunde und ihren Verbleib. Halt deinen Arbeitsbaum still, solange eine Runde läuft.
3. **Eine Frage gehört zusätzlich in jede Übergabe** (#397): was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?
4. Journaleintrag als **letzter** Commit, nach `git fetch origin`.
5. PR öffnen, nicht mergen, und der Koordination berichten.

**Beide Spuren starten gleichzeitig**, keine wartet auf die andere. Berührungspunkte sind nur Port 8080 und die beiden geteilten Dateien.

### Definition of Done, als Lesertest

Du bist fertig, wenn jemand, der diesen Lauf nicht miterlebt hat, aus dem PR allein beantworten kann:

- **Was ist das Format**, und was muss jemand tun, um eine Prüfseite daraus zu erzeugen?
- **Eingebettet oder nachgeladen**, und warum so?
- **Welche Fälle stehen in der Seite**, wie viele, und woher kommt die Zahl?
- **Welcher Vorschlag stützt sich auf welche Belegstelle?** Ein Vorschlag ohne diese Spur ist genau der Fehler, den die Regel in Baustein 6 verbietet.
- **Was bleibt für KZW zu entscheiden**, und wo trägt sie es ein?

Und der eigentliche Test, weil er über den PR hinausgeht: **KZW soll die Datei öffnen können, ohne jemanden zu fragen, wie es geht.** Braucht es dafür eine Erklärung im Ticket, die länger ist als zwei Sätze, ist das Format noch nicht fertig.
