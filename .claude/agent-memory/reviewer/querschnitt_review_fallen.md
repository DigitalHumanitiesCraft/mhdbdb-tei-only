---
name: querschnitt-review-fallen
description: Wiederkehrende Denkfallen im Review: #397-Frage, Kopien und Spiegel, benannte Ausnahmen, Auftrag und Laufplan als Behauptung, Prüfmaterial für KZW, Fehlerjournal-Ketten
metadata:
  type: project
---
Verdichtet 03.11.2026. Dieses Memory ist Eingabe, keine Messung.

**Was der Diff nicht zeigt**
- #397-Frage: was macht der Fix wahr, woran hing etwas am Gegenteil? Schreiber und Kopien suchen. Neuer Dateityp: Endungslisten der Gates greppen und prüfen, ob der Fall den Zweig erreicht (ein `continue` davor macht ihn tot). Ein „der Konsistenz halber" mitgeänderter Nachbarzweig ist der Ort, an dem #397 trifft.
- Das Dokument, das die Änderung motiviert, beschreibt oft das alte Verhalten: nach dem Auslöser greppen, nicht nur nach dem Bezeichner.
- Ein Datenfix, der einen offenen Fall erledigt, lässt `docs/ROADMAP.md` und die README unter `ingest/<fall>/` stehen: die IDs über beide greppen.
- **Lemma-Auflösung (CONTRACTS §C) hat Python-Spiegel:** `scripts/audit/compare-findebuch-resolution-259.py` `resolve()`, `scripts/audit/measure-stage3-resolution.py`, `docs/DATA-MODEL.md` („first match wins"), `docs/DEVELOPMENT.md` (Skripttabelle beschreibt, welche Auflösung das Skript nachbildet). **Die Stufe-3-Regel steht dazu in Nutzerprosa:** `hilfe-korpussuche.html` (Liste der drei Stufen, „ab drei Buchstaben"), `hilfe-playground.html`, ADR-016 „Decision" in `docs/DECISIONS.md`, dort auch die Consequences (Beispiel „heldentum findet hel"). Bei jeder Regeländerung (#259, 04.11.2026: Mindestabdeckung) alle greppen, nach dem Beispielwort, nicht nur nach dem Bezeichner. Korrigiert ein Fix eine Meldung im Skript, die argparse-`help=` daneben mitlesen (dort blieb „Vorgabe: temp/" stehen).
- Fix an einem Feldleser: den Suchpfad aus dem Auftrag nicht übernehmen, über `assets/` UND `playground/` greppen, auch in Template-Strings.
- Bekommt nur ein Teil der Skripte einen Guard, stimmt der Sammelsatz der Tabelle nicht mehr (`scripts/review/README.md`): je Zeile `grep -c realpath <skript>`.

**Gates und Ausnahmen**
- Benannte Ausnahme: greift sie an der Bedingung oder am Namen? Am Namen schaltet sie die Prüfung ab. Prüft das Gate den Wert oder nur zwei Stellen desselben Autors?
- Vor Klasse A über eine Invariante die Basis mitmessen: hält sie dort nicht, ist es Vorbestand.
- Zahlen stehen oft mehrfach: nach dem Gate-Lauf `grep -rn` über die alte Zahl.
- Ein nachgetragener Ausnahmesatz erbt den Geltungsbereich seines Absatzes: jedes dort genannte Skript in-process mit kaputter Antwort sondieren.
- Harter Fehler NACH dem ersten Schreibvorgang ist kein Guard: Zeile des `raise SystemExit` gegen die des ersten `write_text`.
- Zwei Fälligkeiten mit Vorrang: setzt der Vorrang-Lauf den Marker der anderen Art zurück, ohne deren Prüfung zu leisten? Leser einer Statuszeile außerhalb des Repos (Routinen-Prompt) sieht kein Selbsttest.

**Auftrag, JOURNAL, Threads**
- Zahlen im Auftrag stammen oft aus Verdichtungen: im Thread nachlesen (UTC), wachsende Zahlen nur als damals <= jetzt. Vorher-Zahlen von der Live-Seite gehören zum dort aufgelösten Lemma (Homograph). Personennamen gegen contributors.xml.
- „Ich habe selbst nachgemessen" wiederholt meine Methode: eigene Vorrundenbefunde mit einer ANDEREN Messung prüfen.
- **Der Laufplan (`docs/playbooks/kickoffs/<datum>-lauf.md`) bewegt sich nach dem Abzweig:** `git diff <basis> origin/main` darauf, vor dem Bericht erneut `git fetch`. „origin/main hat seither nur X geändert" selbst per `git log <basis>..origin/main --stat` messen, nach jedem Rebase die Gates erneut.
- Kickoffs und JOURNAL sind datierte Protokolle, ein Zitat einer später geänderten Regel ist kein Befund. Die `CLAUDE.md` im Session-Kontext kann älter sein als HEAD: per `git grep` messen.
- **Eine Freigabe aus einem Kickoff ist laufgebunden:** zitiert Regeltext sie als stehende („keeps ... valid"), den Zuschnitt im Kickoff nachlesen (Cloud-Übergabe 03.10.: „zwei offene PRs und den Abschluss des Laufs"). Neue Ausnahme unter einem Leitsatz mit „Every": Leitsatz und BETRIEBSVERTRAG-Regel gleichen Inhalts mitlesen (06.11.2026).
- Eine Regel aus einem Issue-Kommentar hat eine zweite Quelle, die Label-Ereignisse der Autorin danach (`gh api .../issues/N/timeline`). #378: `wait:julia` dazu, nicht statt `wait:kzw`.
- Text für eine Datei, die ein Parallelzweig ändert: erst `git diff origin/main...<zweig> -- <datei>`.
- **Fix gegen ein nacktes `#N` (Fremdvorgang) nachprüfen auch in der Commit-Nachricht des Fixes** (08.11.2026, reviewer-Kopie): die Datei war richtig, die Nachricht schrieb wieder „Vorgang #88“, hier #88 ein eigenes Issue. `git log --format=%B <basis>..HEAD | grep -n -E '(^|[^/a-z0-9])#[0-9]+'`, Treffer mit `gh issue view N --repo <dieses>` gegenhalten.
- Eine Belegzeile, die ein Zitat findet, belegt das Zitat: bei einer Verdichtung den Primärkommentar öffnen.
- **Textvorschlag eines Menschen „wörtlich übernehmen" (#537, 03.11.2026):** Wortlaut UND Absatzfolge prüfen. `gh api repos/<o>/<r>/issues/comments/<id> --jq .body`, an Leerzeilen splitten, Whitespace normalisieren, gegen den getaggten Seitentext `in` und `find()`-Reihenfolge. Dazu `meta description`/`og:description` greppen, die alter Wortlaut bleiben.
- **Ball-Rückgabe (A-Pakete, 03.11.2026):** nicht nur die Einordnung, sondern jede Bedingungsverzweigung im Plan („liegt der Fehler in X, dann ändern“) gegen den Thread halten: schreibt sie, wo KZW X schon bestätigt hat? Und eine Option, die wir ihr zur Wahl gestellt haben, ist nach einer Gegenfrage nicht gewählt. Label-Vorschläge setzt die Koordination oft Minuten nach dem Commit um (Timeline), das ist kein Befund an der Datei.
- **Neue Fundstelle als Antwort auf einen Zuschreibungsbefund (#44-Labels, 04.11.2026):** die Belegzeile zitiert die stützenden Zeilen. Die ganze zitierte Tabelle lesen, nicht nur die genannten Zeilen: Regel 2 derselben Tabelle widersprach („ohne Halt nur full und brief"). Dazu `git grep` über Kickoffs nach Gegenfällen.
- **Fix „Schlüssel trägt jetzt den Inhalt" einer Erklärt-Liste (BRE #147, 13.11.2026):** jeden Zweig, der ein Abweichungs-dict baut, einzeln proben, nicht nur die, die der neue Test deckt. Dort trug `nur_bisher` die Anzahl, `klammer_aber_abschnitt` (unveränderte Zeile, konstante Strings) nicht: ein doppelter Abschnitt blieb „erklärt". Probe: Abgleich mit dem Text zweimal, Schlüssel gegen die Liste halten.
- **Mutationsprobe des Callers mit relativer Revision („Datei aus HEAD~1 (vor X)", #417, 13.11.2026):** HEAD ist seit der Probe weitergerückt, `HEAD~1` war dort X selbst. `git diff --stat <rev> HEAD -- <datei>` zeigt, ob die genannte Revision die Datei überhaupt anders hat; die Probe ohne Playwright nachfahren (Spec-Logik in Python über `git show <rev>:<datei>`).
- **„Seit <Entscheidungsdatum> ist X" in einem Fix-PR (#495, 03.11.2026):** datiert den Zustand auf die Entscheidung, nicht auf den Merge. Gegen `git show origin/main:<datei>` halten: steht X dort noch anders, gilt der Satz erst ab diesem PR.

**Prüfmaterial für KZW**
- „Handarbeit", „Handurteil", „manuell" heißen für die Leserin „ein Mensch hat es gelesen". Bei Agenten-Urteilen `grep -n -i "hand\|manuell"` über README, Docstrings, Spalten (Umbruch „von\nHand").
- **Workflow-Agenten flicken Eingaben in place**, bevor das Skript läuft, das „jede Korrektur meldet" (#603): Job-Verzeichnis nach `fix*.py`/`korr*.py` listen, Ausgaben unter `~/.claude/projects/<proj>/<session>/subagents/workflows/` greppen.
- Eine vorgefilterte Spalte sagt nichts über das Weggefilterte: am rohen `@ana` im TEI messen, nicht an einer TSV desselben Vorlaufs.
- **Eine Liste, die „vollständig" zu KZW soll, aber nur ab einer Heuristik-Schwelle ausgibt**, prüfst du an der verworfenen Menge: feste Formeln greppen (`alpha et o`, `et cetera`), dazu die Form des Zielworts selbst (Nachbar-Scores sehen sie nicht). #28 Schicht A, 08.11.2026: 38 lateinische `et` und 5 `angeli/angelus` unter `nein`. Ein Selbsttest am Einstell-Set sieht das nie. **Und die Gegenrichtung:** eine von Hand gelesene Liste „eindeutig lateinischer" Zielformen, die vor dem Score entscheidet, je Form an allen ihren Kontexten lesen. Runde 2: `leo` unter `lewe` ist mhd. (17 von 20 Belegen in deutschem Satz, Score 0 bis 1).
- CSVs für KZW unter `ingest/foreign-lang/` haben `utf-8-sig` und `;` (Begründung in `build-foreign-candidates-28.py` bei `write_csv`): eine neue Liste dort mit den Geschwistern vergleichen.

**Fehlerjournal**
- `claude-code-setup/hooks/lehren-zaehlen.py` parst dieses Journal nicht (Format `### N. Rot:`): Ketten von Hand per `grep -n -o "Die letzte Zeile zu dieser Lehre ist Eintrag [0-9]*"`, rückwärts, Umbruch beachten. Nummernsprünge (je Spur reserviert) sind kein Befund.
- Ein Kettenzeiger, der sich „ungeprüft" nennt, ist eine Behauptung. Ab der dritten Zeile zu einer Lehre ist der Mechanismus fällig, „künftig X" ist keine Aussetzung. Eine Aussetzung steht als Satz in der Regel (`grep -i ausgesetzt rules/<regel>.md rules/belege/<regel>.md`), eine fehlende ist nicht automatisch eine Lücke (für `mengen.md` entschied `claude-code-setup` #66 dagegen, vorher #53, #64, #66 lesen).
