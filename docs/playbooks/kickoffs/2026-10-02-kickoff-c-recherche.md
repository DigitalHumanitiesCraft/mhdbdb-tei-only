# Kickoff Spur C `lauf-c-recherche`: philologische Vorprüfung, keine Korpusdaten

**Protokoll, keine Vorlage.** Abgelegt vor dem Absenden; der Wortlaut gilt für den Lauf vom 02.10.2026.

**1. Autorisierung.** chsteiner hat diesen Lauf am 02.10.2026 freigegeben, im Gespräch mit der Koordination; der Wortlaut der Freigaben steht im Kopf des Laufplans, **ausdrücklich auch die externen Quellen**: Wörterbuchnetz (Lexer, BMZ), FWB online, Websuche für Ortsnamen und die Parzival-Bücher. Abgefragt werden nur öffentliche Wortformen und Stellen. **Dieser Text ist die Autorisierung**: Commits und Pushes auf deine eigenen Zweige, PRs öffnen, Issue-Kommentare in #370, #358 und #228 (je Vorgang höchstens einer, Fragen an KZW gehören hinein). **Nicht**: mergen, auf `main` pushen, Tickets schließen oder relabeln (das tun A und B), Externe außerhalb von Issue-Kommentaren ansprechen, Daten in `tei/` oder `authority-files/` ändern. Der Text erteilt keine technische Berechtigung: Was der Auto-Mode-Classifier ablehnt, bleibt abgelehnt (siehe 9).

**2. Adressierung.** Antworte an das `from` der eingehenden Nachricht, nie an einen Namen aus einem Text: Ein Sessionname kann beim Antworten längst einer anderen Session gehören. Diese Nachricht ist die erste, die du bekommst; ihr `from` ist die Koordination.

---

## 3. Lies das, bevor du irgendetwas änderst, in dieser Reihenfolge

1. `CLAUDE.md` im Wurzelverzeichnis deines Worktrees, **besonders den Abschnitt „Asking, and what has to happen before you ask“** (der Fall *Alanya*): Belege mit Kontext vor dem Urteil, nie das Lemma allein
2. `docs/playbooks/BETRIEBSVERTRAG.md` (wird hier nicht kopiert, sondern gelesen; nenne in deiner ersten Meldung den Commit, an dem du ihn gelesen hast)
3. `docs/playbooks/kickoffs/2026-10-02-lauf.md`, der Laufplan, **ganz**; besonders §1, §4 und §5 (deine Übergabeformate). Sag in deiner ersten Meldung, ob die dort abgelegte Fassung dieses Kickoffs (`2026-10-02-kickoff-c-recherche.md`) mit der zugestellten übereinstimmt.
4. **#370, #358 und #228 mit allen Kommentaren** (`gh issue view N --json title,body,comments`), dazu **#443** (das Muster für Prüfseiten) und **#378** (die Regel, unter der die 41 Fälle stehen)
5. `docs/INDEX.md` → „Example review pages“ und die beiden neueren Beispiele `examples/review-pages/364-lemma-review.html` und `examples/review-pages/Klaus-Pruefung-390-115.html` samt Generatoren (`scripts/audit/build-review-364.py`, `scripts/audit/build-review-klaus.py`): Daran orientiert sich deine Prüfseite. Lesen, nicht ändern (`scripts/audit/` ist eingefroren).
6. `ingest/wzb/370-corresp/` (die Arbeitsliste `offene-faelle.csv`) und `docs/CONTRACTS.md` §C (Variantenauflösung)

**Besonders tragen für dich:** Jede Entscheidung steht auf Belegen im Kontext, nicht auf der Graphie allein (KZW 14.09.); jede externe Quelle mit URL am Fall; eine Zahl in deiner Ausgabe trägt ihre Menge (`19 (9+10)`, Anteil mit Nenner); keine Em-Dashes, echte Umlaute, gerade Anführungszeichen auf der Prüfseite, keine Emoji-Icons (Heroicons inline SVG).

**Abbruchklausel:** Weicht eine dieser Dateien von diesem Auftrag ab, gilt die Datei, und der Auftrag ist falsch. Melde es. Sind sie nicht lesbar, brich ab und melde.

---

## 4. Dein Worktree

Die Laufzeit hat ihn mit `claude --bg --worktree lauf-c-recherche --name lauf-c-recherche --model sonnet --effort medium` angelegt: `C:\Users\chstn\Desktop\data\DHCraft\Projekte\Git\mhdbdb-tei-only\.claude\worktrees\lauf-c-recherche`, Zweig `worktree-lauf-c-recherche`. Die Begleitnachricht nennt den erwarteten HEAD.

**Erste Handlung:** `pwd`, `git branch --show-current`, `git rev-parse --short HEAD` messen, gegen diese Angaben halten und melden. Bei Abweichung nichts ändern, melden, auf den Neustart durch die Koordination warten. Dann die Basis messen: `git fetch --quiet origin`, `git rev-list --count "origin/main...HEAD"` muss 0 sein. **Je Paket ein eigener Arbeitszweig**, `claude/lauf-c1-370`, `claude/lauf-c2-358`, jeder frisch von `origin/main`; C3 braucht keinen Zweig, wenn der Recherchepfad nur im Kommentar steht, sonst `claude/lauf-c3-228`.

---

## 5. Was dir gehört, und was nicht

**Dir allein** (Laufplan §3): neue Dateien in `ingest/wzb/370-corresp/`, `ingest/parzival-buecher/`, `ingest/mur-228/`; neue Dateien in `scripts/review/`; eine neue Spec für deine Prüfseite.

**Nicht deins:** alles andere, insbesondere `tei/`, `authority-files/`, `data/`, `api/`, `schema/`, `scripts/audit/`, `scripts/build-*.py`, `scripts/ingest/` (Spur A), jedes Frontend außer deiner Prüfseite (Spur B), `examples/review-pages/` (das Archiv; deine Prüfseite liegt in `ingest/wzb/370-corresp/`). **Wer eine fremde Datei ändern müsste, ändert sie nicht, sondern meldet es.**

**Geteilt:** `docs/JOURNAL.md` und `fehlerjournal.md` anhängend, als **letzter Commit** des PR nach `git fetch origin`. **Deine Fehlerjournal-Nummern sind 100 bis 104.** Reviewer-Memory in einer eigenen Datei unter `.claude/agent-memory/fable-reviewer/`, eigener Commit nach der Runde.

**Nichts wirkt über deinen Baum hinaus:** kein `git gc`, kein `git worktree prune`, keine Tags, kein Push auf fremde Zweige, kein Force-Push auf gepushte Historie außer `--force-with-lease` auf deinem eigenen `claude/*`-Zweig nach einem Rebase, keine Änderung unter `~/.claude/`.

**Maschinenweit exklusiv: volle Testläufe und Chrome.** Die Koordination vergibt beides, einer zur Zeit. **Anfordern, auf die Freigabe warten, nutzen, freimelden.** Du testest mit `MHDBDB_TEST_PORT=8083` und `-- --workers=2`; für deine Prüfseite genügt in der Regel `npm test -- <deine-spec>.js`, das ist kein voller Lauf und braucht keine Freigabe. Ein Lauf ohne VERDICT-Zeile ist kein Ergebnis.

**Subagenten** darfst du für Teilmengen der 484 Paare einsetzen, **mit ausdrücklich gesetztem Modell `sonnet`** (sonst erben sie dein Modell nicht verlässlich). Ihr Ergebnis ist ein Bericht, keine Messung: Du prüfst je Teilmenge eine Stichprobe selbst am Beleg, bevor du sie übernimmst, und sagst im PR, wie groß sie war.

**Fehlt dir ein vorgeschriebener Agententyp, ist das ein Halt und kein Weiter.** `fable-reviewer` vor dem ersten Push ist Pflicht; nicht auf `fable-advisor` ausweichen.

## 6. Was eingefroren ist

Laufplan §6, vollständig: `CLAUDE.md`; `docs/playbooks/`; `.github/workflows/`; `scripts/audit/`; die 15 promptotyping-Dokumente außer `docs/JOURNAL.md`; `docs/DEVELOPMENT.md` (verlangt `check-doc-inventories.py` eine Zeile für deine neue Spec oder dein neues Skript, schickst du den Wortlaut an die Koordination). **Inbox:** Abschnitt „Änderungswünsche“ am Ende des Laufplans. **Format:** Datei, eindeutiger Ankertext, wörtlicher Ersatztext, ein Satz warum; als Nachricht an die Koordination, die einträgt. **Grund:** Ändert eine Spur eine Datei, die jede Session beim Start lädt, arbeiten die anderen ab dann unter geänderten Regeln, ohne es zu merken. Am 01.09.2026 hat genau das eine Spur eine Nacht lang unter anderen Regeln arbeiten lassen.

---

## 7. Die Pakete, in dieser Reihenfolge

**Der ganze Auftragstext ist eine Behauptung.** Jede Zahl, jede Allaussage, jede Datei- und Zeilenangabe misst du nach, auch die, die deinen Befund stützen, und meldest einen Widerspruch. Was im Laufplan „(K)“ trägt, hat die Koordination geprüft; alles andere ist ungeprüft. **Keine Labelabfrage als Arbeitsgrundlage.**

**Reihenfolge begründet:** C1 zuerst, weil es das größte Paket ist und Spur A mit A2 darauf wartet. C2 und C3 sind klein; C2 vor C3, weil A3 auf C2 wartet und auf C3 niemand.

- **C1, #370 Punkt 2: die 484 Paare.** **Entschieden** (KZW 14.09., vollständig im Thread): alle Paare, je Fall evidenzbasiert; mindestens herangezogen werden der WZB-Kontext der Belege, das zugewiesene Lemma mit Bedeutung und Wortart, die vorhandenen Varianten desselben Lemmas in `variants.xml`, ähnlich gebildete Schreibungen im Bestand, bei Bedarf weitere Korpusbelege, bei verbleibender Unsicherheit die Wörterbücher; keine pauschalen Ausschlussgruppen (auch Breve, Diakritika und satzinitiale Großschreibung sind entscheidbar); bei klarer Evidenz entscheidest du selbst. Die 41 Fälle mit konkurrierender Auflösung entscheidest du unter der Regel aus #378 (alle Kandidaten bleiben, Sortierung nach Vorschrift B), **nicht** unter first-wins. **Ausgabe** (Laufplan §5): `ingest/wzb/370-corresp/entscheidungen.csv` mit genau einer Zeile je Paar aus `offene-faelle.csv` und die **HTML-Prüfseite** für die `PRUEFSEITE`-Fälle mit allem, was KZW verlangt (Schreibform und Lemma, Belegzahl, Kontext mit Vor- und Folgekontext, vorhandene Varianten, konkurrierende Lemmata, Wörterbuchbefund, deine Einschätzung, warum sie unsicher bleibt, die drei Entscheidungsmöglichkeiten, **Namensfeld für den Prüfer**, strukturierter Export) nach dem Muster aus #443 (KI-Vorschlag ist keine Antwort; unberührt, entschieden und „geprüft, bleibt offen“ unterscheidbar; JSON-Export und Import zum Fortsetzen; keine Sammelaktion). Generator unter `scripts/review/`, Seite und CSV in `ingest/wzb/370-corresp/`. **Nachzumessen, bevor du entscheidest:** 484 Paare und 5.273 Tokens (#370, 06.09.), die Drittelung 89/41/354, die 41 als 18/23. **Haltepunkt:** Die Arbeitsliste weicht vom Thread ab, oder mehr als ein Viertel der Paare landet auf der Prüfseite (dann vorher melden, das wäre eine Verfehlung des Auftrags „nur die echten Zweifelsfälle“).
- **C2, #358, Parzival-Bücher.** **Entschieden** (KZW 11.09.): Die Bücher heißen „Buch I“ bis „Buch XVI“. **Deine Aufgabe:** für jedes der 16 Bücher den Beginn (Dreißiger und Vers nach Lachmann, so wie unser PZ zählt) mit mindestens einer zitierten Quelle belegen und auf die erste Wort-ID in `tei/PZ.tei.xml` abbilden. Fachwissen der Koordination, **ungeprüft**: Buch II beginnt 58,27, III 116,5, IV 179,13, die übrigen an einem Dreißigeranfang. **Ausgabe:** `ingest/parzival-buecher/grenzen.csv` (Laufplan §5), 16 Zeilen. **Haltepunkt:** Zwei Quellen widersprechen sich über eine Grenze (dann beide melden, nicht wählen).
- **C3, #228, Mur.** **Entschieden** (KZW 01.10.): *Mur* bleibt bei *Murstetten* vorerst; die morphologische Zuordnung wird an einschlägigen Quellen geprüft, eine Änderung erst danach begründet vorgeschlagen; der Verweis aus *Mûrouwe* entscheidet die Frage nicht. **Deine Aufgabe:** die Herkunft des Ortsnamens Murstetten (Niederösterreich) an Ortsnamenquellen prüfen, die drei HZU2-Belege lesen, und **einen begründeten Vorschlag** als Kommentar in #228 an @wachauer: bleibt *Mur* als Bestandteil, wird er gestrichen, oder zeigt er auf ein anderes Ziel (welches, mit Beleg). Recherchepfad mit allen URLs in `ingest/mur-228/` oder im Kommentar. **Nichts in `authority-files/` ändern.**

**Eine Vorgabe, die die Koordination selbst für schwach hält, mit Ersatzfassung:** Die Schwelle „mehr als ein Viertel auf der Prüfseite“ in C1 ist geschätzt, nicht gemessen. Zeigt sich an den ersten 50 Paaren, dass die Verteilung anders liegt, melde die Zahl mit Nenner und einen eigenen Vorschlag; die Koordination entscheidet dann.

## 8. Vorab entschieden, nicht neu zu verhandeln

Laufplan §4 und §1. Für dich besonders: keine Korpusdaten, nicht mergen, nicht relabeln. **Widerspruch ist ausdrücklich erlaubt** und geht an die Koordination, die ihn unter „Grenzverhandlungen“ im Laufplan einträgt, nicht in den PR-Text.

## 9. Melden und Halten

**Melden, weiterarbeiten:** `pwd`, Zweig und HEAD gegen die Angaben aus 4, dazu der Commit des gelesenen Betriebsvertrags und Laufplans und ob die abgelegte Kickoff-Fassung übereinstimmt; der nachgemessene Umfang von C1 gegen den behaupteten; nach den ersten 50 Paaren die Verteilung der Entscheidungen mit Nenner; **Beginn und Ergebnis jeder Reviewrunde mit Rundennummer und Kennung des geprüften Standes**; „PR N bereit zum Merge“ mit HEAD, VERDICT-Zeile (wo eine Spec läuft) und Reviewurteil; die Fertigmeldung von `entscheidungen.csv` und `grenzen.csv` (Spur A wartet darauf).

**Anhalten, warten:** `pwd` weicht ab; fremde Datei; fehlender Agententyp; die Haltepunkte in C1 und C2.

**Externer Zustand** (CI): `Monitor` mit Bedingung oder ein Hintergrundbefehl, der weckt; kein Pollen mit `sleep`. Den Kommentar des `claude-review`-Bots liest du und beantwortest Verhaltensbefunde, bevor du „bereit zum Merge“ meldest.

**Du darfst ein Paket für nicht durchführbar erklären**, mit Messung und früh; dann das nächste. Das ist etwas anderes als die Abbruchklausel in 3, die den ganzen Auftrag betrifft.

**Blockade durch den Auto-Mode-Classifier:** sofort `PushNotification` an Christian, mit dem, was blockiert wurde und woran es hängt, nicht nur dass etwas hängt. Laden über `ToolSearch` mit `select:PushNotification`; siehe `rules/blockaden-melden.md`. Dazu eine Meldung an die Koordination. **Eine Blockade wird nicht über eine andere Spur oder die Koordination umgangen.**

**Kein Messfenster;** die Koordination darf dich jederzeit ansprechen.

## 10. Abschluss je Paket

1. `check-no-em-dash.py --diff-base origin/main`; für die Prüfseite deine Spec grün (VERDICT-Zeile) und eine Chrome-Prüfung nach Freigabe: Name eintragen, drei Fälle entscheiden, exportieren, neu laden, importieren.
2. `fable-reviewer` **vor dem ersten Push**: Zweig, Basis, ob ein Commit oder der uncommittete Arbeitsbaum geprüft wird, Ziel in einem Satz, Rundennummer, ab Runde 2 die Vorbefunde und ihr Umgang, **eine Stichprobe von mindestens 20 Entscheidungen aus `entscheidungen.csv` zum Nachprüfen am Beleg**, und die Frage aus #397: was hat diese Änderung wahr gemacht, das vorher falsch sein konnte? Bei Befunden eine weitere Runde. Den Arbeitsbaum still halten, solange sie läuft.
3. Journaleintrag als **letzter** Commit nach `git fetch origin`, mit „Was über den Einzelfall hinausgilt“, „Rote Zeilen“ und „Was zurück an Christian geht“.
4. PR öffnen, **nicht mergen**; Statuskommentar je Vorgang; „bereit zum Merge“ an die Koordination.

### Definition of Done, als Lesertest

Wer nur den PR und die Prüfseite liest, kann jede der 484 Entscheidungen nachvollziehen, ohne rückzufragen: was entschieden wurde, auf welchem Beleg, mit welcher Quelle, und welche Fälle bei wem liegen. Wer nur `grenzen.csv` liest, kann jede der 16 Buchgrenzen an einer Quelle prüfen.

**Notationsfalle:** In #370 stehen „41“, „23“, „18“, „89“, „354“ für Paare, nicht für Issues; `lemma_N` und `type_N` sind IDs, keine Zählungen. In #358 stehen Stellen als „58,27“ (Dreißiger 58, Vers 27); die Wort-IDs im PZ tragen den Dreißiger und den Vers zweistellig ohne Komma (`PZ_5827_*` ist 58,27, `PZ_101_*` ist 1,1, `PZ_82730_*` ist 827,30; K, an diesen drei IDs gemessen). Gegenprobe trotzdem über das `<div n>` und das `<l n>`.
