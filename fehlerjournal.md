# Fehlerjournal

Die roten Zeilen dieses Repositoriums, chronologisch, neue Einträge unten. Was
hierher gehört, sagt die Regel `wiederholte-fehler.md` aus Christians Setup: ein
Fehler, dessen Fehlermodus schon eine dokumentierte Lehre hat, mit Datum, was
passiert ist, und welche Lehre nicht gegriffen hat, samt Fundstelle.

**Diese Datei ist am 16.09.2026 aus [docs/JOURNAL.md](docs/JOURNAL.md) und
[docs/journal-archive.md](docs/journal-archive.md) herausgezogen worden.** Dort
ist das Prozessjournal nach der Promptotyping-Arbeitsweise zu Hause, also
Arbeitsstand, Entscheidungen und Handoffs; `orient` und `handoff` suchen genau
diesen Namen. Der Zähler ist etwas anderes und wird über seine Nummern
angesprungen statt am Stück gelesen.

**An jeder Fundstelle im Journal steht eine Kurzzeile mit der Nummer**, damit
der umgebende Text seinen Bezug behält; die Überschriften darüber sind die der
Tageseinträge, aus denen die Zeilen stammen. Die Nummern sind bei diesem Auszug
vergeben worden und laufen chronologisch. Vorher hatte dieses Repositorium
keinen Nummernraum: **die Zeilen eines Laufs zählten sich selbst durch** („Rot,
zum sechsten Mal"), und sie verweisen untereinander weiterhin so. **Diese
Laufzählung ist nicht die Nummer hier**, und der Versatz ist nicht
gleichmäßig: Laufzählung 2 bis 7 liegen auf Eintrag 3 bis 8, Laufzählung 8
aber auf Eintrag 12, weil dazwischen Zeilen ohne eigene Laufzählung stehen.
Wo ein Eintrag so verweist, ist die Nummer in Klammern danebengesetzt.


## 2026-09-01 – Der Lauf, der seriell blieb, weil die abgeleitete Schicht global ist

Aus `docs/journal-archive.md`.


### 1. Rot nach der Zählregel vom 01.09.: „an allen vier Stellen konsistent" statt fünf, obwohl die richtige Zahl im Kontext stand.

**Rot nach der Zählregel vom 01.09.: „an allen vier Stellen konsistent" statt fünf, obwohl die richtige Zahl im Kontext stand.** Die Welle-0-Meldung der Spur-Session gab das Ergebnis von `check-index-versions.py` mit vier Stellen an. Das Gate prüft fünf Dateien (`build-corpus-index.py`, `build-authority-index.py`, `assets/js/lib/corpus-loader.js`, `docs/TEI-MODEL.md`, `docs/INDEX.md`, Zeilen 46 bis 50). Die Fehlerquelle ist die Konsolenausgabe: sie listet **je Index vier Rollen** („build-skript, loader, TEI-MODEL.md, INDEX.md"), weil der Loader beide Versionen trägt, und diese Vier wurde für die Dateizahl gehalten. Die dokumentierte Lehre dazu lag der Session von Anfang an vor und hat nicht gegriffen; gefunden hat es die Koordination, nicht die Session. Die Zeile steht hier auf Bitte der Spur-Session, die auf `main` nicht committen darf. **Die Lehre über den Anlass hinaus: eine Ausgabe, die Rollen zählt, ist keine Aussage über Dateien**, und ein Skript, das gegen eine gemerkte Zahl läuft, ist die Gelegenheit, die Zahl zu prüfen, nicht der Beleg dafür.


### 2. Rot, und zwar auf der Koordinationsseite

**Rot, und zwar auf der Koordinationsseite:** der Freeze aus #385 tritt laut Ticket **mit dem Kickoff** in Kraft, nicht mit seiner Eintragung. Der Kickoff ging um kurz vor 22 Uhr hinaus, danach hat die Koordination mit `8a7ea2116` `docs/playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md` geändert, eine Datei, die auf der Einfrierliste steht. Die Lehre, die nicht gegriffen hat, ist #385 selbst: sie war nur nicht gelesen, weil der Freeze zum Zeitpunkt des Kickoffs noch nicht eingetragen war. Der Commit bleibt stehen, weil er einen Befund der laufenden Spur einarbeitet und ihr Abbau ohne ihn in die Sperre läuft; die Spur wurde in derselben Stunde mit dem Hash unterrichtet, was den eigentlichen Schaden repariert (unbemerkt geänderte Regeln). Die Konsequenz für den nächsten Lauf ist keine schärfere Formulierung, sondern eine Reihenfolge: **der Freeze wird eingetragen, bevor der Kickoff hinausgeht.** Offengelegt im Body von #385.


### 3. Rot, zum zweiten Mal an einem Abend und wieder auf der Koordinationsseite: die Welle-2-Vorabmessung war falsch.

**Rot, zum zweiten Mal an einem Abend und wieder auf der Koordinationsseite: die Welle-2-Vorabmessung war falsch.** Die transitive Hülle unter `concept_23123000` sammelte nur die Kinder und nicht die Wurzel selbst (`gefunden, stapel = {}, [WURZEL]`, die Wurzel geht auf den Stapel und nie in die Ergebnismenge). Richtig sind **6.246 Lemmata** in **18** Kategorien mit **227.652** Belegen, nicht 6.219 in 17 mit 225.505; die Anteile 14,23 % und 3,02 % statt 14,17 % und 2,99 %. Gefunden hat es der `fable-reviewer` in Runde 1 auf dem Welle-2-PR, nachgemessen hat es die Spur, und danach die Koordination unabhängig ein drittes Mal. **Die Zahlendifferenz von 0,43 % ist das Unwichtigste daran.** Unter den 27 fehlenden Lemmata stehen `welsch`, `enwelsch`, `rotwalsch`, `englisch`, `tolmetze`, `tolken`, `vertolken`, `antvristen`, `diuten`, `diutunge`, `tiutschen`, `zediuten`, `ûzlegen`, `ûzleger`, `ûzlegerin`, `ûzlegunge`, `zunge`, `gezünge`: das Vokabular, mit dem der Text über Fremdsprachigkeit **spricht**, statt sie zu belegen. Die Wurzel heißt „Einzelsprachen" und trägt genau die Wörter, die keiner einzelnen Sprache zuzuordnen sind. In einer Messung zu #28 fehlte damit die Klasse, die das Phänomen benennt. **Die Spur hat diese Charakterisierung zu Recht eingeschränkt: sie trifft auf 24 der 27 zu**, sauber geteilt in Sprachbezeichnungen (8), Übersetzen und Auslegen (14) sowie Sprache als Organ (2). Die drei übrigen sind `gebrechen`, `engebrechen`, `gebrechenhaft`, und sie sind **kein Rauschen**, obwohl sie zunächst so aussehen: anders als `niht`, das sein Sprachkonzept am einzigen Sense trägt, tragen diese drei es am vierten von vier, und zwar alle in derselben Kombination aus „Mündliche Kommunikation" und „Einzelsprachen", während ihre Hauptbedeutung auf „Mangel/Bedürfnis/Misserfolg" sitzt. Das sieht nach gebrochener Sprachbeherrschung aus, also nach `radebrechen`, und wäre dann mit 341 Belegen in 101 Texten der belegstärkste Zugang, den Gleis 1 überhaupt hat. Damit ist es eine Frage an KZW.


### 4. Rot, zum dritten Mal an einem Abend und wieder die Koordination: „das Korpus kann Senses nicht auflösen" war falsch.

**Rot, zum dritten Mal an einem Abend und wieder die Koordination: „das Korpus kann Senses nicht auflösen" war falsch.** Der Satz stand hier und im #28-Kommentar, und er ist in zwei Minuten widerlegbar gewesen. Neben `@lemmaRef` trägt jedes annotierte `<w>` ein `@ana="lexicon.xml#lemma_{id}_sense_{id}"`, das genau auf den Sense zeigt, in **667 von 667** Dateien, dokumentiert in TEI-MODEL.md §4.1 samt Migrationsgeschichte (Phase B1, `@meaningRef` zu `@ana`, rund 5,9 Millionen Vorkommen). Zustande gekommen ist der Fehler dadurch, dass die Sense-Datensätze in `api/lemmata/index.json` tatsächlich nur `conceptIds` führen und daraus auf das Korpus geschlossen wurde, ohne das Dokument aufzuschlagen, das davon handelt. Die Lehre, die nicht gegriffen hat, ist die schlichteste im Bestand: **eine Abwesenheitsbehauptung braucht eine Abfrage, die Anwesenheit zeigen könnte.** Gefunden hat es die Spur, und sie hat gleich die Sachfrage mitentschieden: von den 40 sense-disambiguierten Tokens der `gebrechen`-Familie zeigt genau eines auf den fraglichen Sense, `JT_30921000_5`, und sein Kontext lautet „secureiz wol kunde hie beidenthalp gebrechen / die rede von ir munde". Das ist das Abbrechen der Rede, nicht gebrochene Sprachbeherrschung; `radebrechen` ist vom Tisch, und die verbliebene Frage an KZW ist enger: warum trägt ein Sense für das Unterbrechen der Rede das Konzept „Einzelsprachen"? **Der nützlichere Teil des Befunds gilt Gleis 1 insgesamt:** 92,4 % der Kandidaten-Tokens tragen ein `@ana`, aber es trennt fast nie, weil 6.872 der 6.996 Senses selbst ein Sprachkonzept haben. Genau 430 Tokens zeigen auf einen Sense ohne eines, und das sind die Stellen, an denen der annotierte Bestand einer Zuordnung widerspricht: das schärfste maschinelle Ausschlusskriterium, das Gleis 1 hat (Messung der Spur, hier nicht nachgemessen). Die Lehre, die nicht gegriffen hat, steht im Auftrag desselben Laufs, §9: ein Testlauf, dessen Grundgesamtheit man nicht kennt, beweist nichts, und plausible falsche Zahlen sind der Regelfall dieser Sorte. Konkret gegen den Wiederholungsfall: **eine Hülle wird gegen ihre eigene Wurzel geprüft, bevor man ihr glaubt**, das kostet zwei Zeilen. Richtigstellung mit Messvorschrift als Kommentar auf #28; die Zahlen im abgeschickten Auftrag bleiben stehen und bekommen eine Fußnote, beantragt in #385, weil `docs/playbooks/**` eingefroren ist.


### 5. Rot, zum vierten Mal, und die Welle-3-Vorabmessung war an zwei Stellen falsch.

**Rot, zum vierten Mal, und die Welle-3-Vorabmessung war an zwei Stellen falsch.** Die erste ist ein Selbstwiderspruch innerhalb eines Absatzes: zum Trierer Zeichensatz steht dort erst die Messung „von 34,3 % auf 37,4 %" und zwei Sätze später das Fazit, die Zusatzregeln „kosten nur nichts und retten hier auch nichts". Mit beiden Schaltungen des Prüfskripts gemessen heben sie die Paare mit bekanntem Findebuch-Lemma von 5.081 auf 5.494 und die Befundmenge von 424 auf 465, also um 41 Fälle. Die zweite wiegt schwerer, weil sie den Zuschnitt des Tickets betrifft: die 477 Fälle waren als die Menge beschrieben, in der „genau dort unsere dreistufige Auflösung danebengreifen" kann. Dort kann sie es nicht. Das Auswahlkriterium, die Schreibform ist bei uns selbst ein Lemma, ist genau die Bedingung, unter der Stufe 1 trifft; die Menge löst deshalb zu 100 % auf Stufe 1 auf (gemessen 465 von 465), und die Fehlerklasse aus #224, wegen der #259 überhaupt existiert, kann in ihr gar nicht auftreten. Gefunden hat beides die Spur beim Bau des Skripts, nachgemessen die Koordination mit dem unveränderten Skript aus `f3a575c77` gegen denselben Dump, außerhalb des Repositoriums ausgeführt.

**Für den Zähler ist die Herkunft wichtiger als die Zahl.** Beide Fehler stammen aus derselben Vorabmessungscharge vom 01.09. wie die rote Zeile zwei und drei, also aus der Zeit **vor** der Lehre, die aus ihnen gezogen wurde. Sie sind ein weiterer Fund im selben Bestand und kein neuer Verstoß gegen eine schon stehende Regel; deshalb stehen sie hier als eine Zeile. Was sie belegen, ist die Wirksamkeitsfrage: **beide vorab vermessenen Wellen trugen einen Fehler, den erst die Spur beim Neubau fand**, und in beiden Fällen wäre er konserviert worden, wenn die Spur der Zahl gefolgt wäre, statt sie neu zu erarbeiten. Genau das war der Zweck der Vorwegnahme. Der strukturelle Grund steht in der roten Zeile drei: Operatorarbeit geht durch keinen Review, die Arbeit der Spur durch vier Runden. Richtigstellung mit Messvorschrift als Kommentar auf #259, der Body ist an beiden Stellen nachgezogen und der Vorabmessungs-Kommentar trägt eine Überholt-Notiz; die Fußnote im eingefrorenen Auftragstext ist über #385 beantragt.


### 6. Rot, zum fünften Mal, und dies ist der erste echte Wiederholungsfall des Laufs: die Lehre stand, sie war drei Stunden alt, und sie war meine eigene.

**Rot, zum fünften Mal, und dies ist der erste echte Wiederholungsfall des Laufs: die Lehre stand, sie war drei Stunden alt, und sie war meine eigene.** Am Vormittag des 02.09. habe ich im Setup-Repositorium den Satz veröffentlicht, das Ergebnis einer Vorabmessung gehe nicht in Ticketkommentare oder in die Chronik, bevor eine geprüfte Fassung existiert. Keine drei Stunden später habe ich aus einer Vorab-Meldung der Spur binnen einer Stunde einen publizierten Ticketkommentar, zwei Body-Änderungen und einen Journalcommit gemacht, und zwar an dem Kommentar, der einen früheren Fehler derselben Sorte richtigstellt. Die Meldung kam aus Meldepunkt 2 **vor** der Reviewrunde, was ihr Zweck ist; die Runde fand danach einen Klasse-A-Defekt im Prüfskript, und damit waren alle Beträge überholt, die ich publiziert hatte. Der Defekt: `itertext()` auch auf `<form type="sublemma">`, wo **2.705 der 8.610 Formen ausschließlich ein Wortartkürzel und gar keine Schreibform tragen**. Selbst nachgemessen mit einem eigenen Skript direkt am Dump, damit die Gegenprobe den Fehler nicht erbt: 8.610 Formen, 3.462 mit `<gram>`-Kind, 2.705 nur Kürzel, 1.039 Ergebnisse mit Leerzeichen, 3.498 mit Punkt, auf die Stelle die Zahlen der Spur. **Die Richtungen beider Befunde halten** (die Trierer Regeln retten etwas, die Prüfmenge löst ausnahmslos auf Stufe 1 auf), die Beträge nicht. Richtiggestellt durch eine Notiz am eigenen Kommentar, und die Betragszahlen sind aus dem Ticket-Body wieder heraus: sie gehören in den PR, nicht in ein Ticket, das bei jeder Reviewrunde nachaltert.

**Im selben Kommentar noch ein zweiter Fall derselben Familie, gefunden von derselben Reviewrunde am Docstring der Spur und auf mich genauso zutreffend:** die Zahl 5.705 für das `ʒ` in der Lexer-Lemmaliste stand dort als Faktum. Sie ist keines. Sie stammt aus der Vorprüfung im Ticket-Body, der Body führt sie selbst unter „nicht nachprüfbar", und die Datei liegt auf dieser Maschine gar nicht (unter `temp/woerterbuchnetz2015` steht allein `FindeB`, nachgesehen). Erst mit Herkunft markiert, und **auch das war falsch**: `CLAUDE.md` Zeile 108 verlangt, was eine Aussage nicht braucht, zu **löschen statt zu belegen**. Die Zahl ist jetzt gelöscht. Der Umweg lohnt die Zeile, weil er eine Klasse benennt, die in der Zählung bisher fehlte und die aus dem Austausch mit `corema-operator` stammt: **die dekorative Zahl.** Sie steht neben einem Argument, das sie nicht braucht, und wird genau deshalb nie geprüft, denn niemand stützt sich auf sie. Wer bemerkt, dass sie nichts trägt, hat damit die Rechtfertigung, sie weiter nicht zu prüfen. Gefährlich wird sie, wenn sie fremd ist: diese hier kam aus einem Ticket-Body und trug dessen Autorität, obwohl sie dort selbst als unprüfbar markiert war. Ein Leser sieht ihr das nicht an.


### 7. Rot, zum sechsten Mal, und es ist dieselbe Bauart wie die vierte (Eintrag 5): Messung richtig, Mechanismus erfunden.

**Rot, zum sechsten Mal, und es ist dieselbe Bauart wie die vierte (Eintrag 5): Messung richtig, Mechanismus erfunden.** Zu einem Befund der Spur aus Welle 4 (das Verblemma `lemma_2535 grôzen` existiert, entgegen ihrer ersten Aussage) habe ich den Variantenbestand nachgemessen und dabei gesehen, dass `grozen`, `groezen` und `groesen` alle auf das Adjektiv `lemma_2534` zeigen. Die Messung stimmt. Daraus habe ich geschrieben, „Stufe 2 überschreibt eine Zuordnung, die Stufe 1 richtig hätte", und das ist frei erfunden: `docs/CONTRACTS.md` §C führt seit langem den Pseudocode mit `if results.length > 0: return results // EARLY RETURN, skip stages 2-3`. Stufe 1 bricht bei Treffer ab, ein Überschreiben kann es nicht geben. Die Spur hat es kassiert und die richtige Lage geliefert: betroffen ist allein der Ingest-Matcher, weil `wzb-breve-backfill.py` `variants.xml` direkt liest und die Stufenordnung nicht kennt. **Der Fehler saß im Werkzeug, nicht in der Auflösung**, und dieser Unterschied entscheidet, ob es ein Frontend-Bug ist oder eine Werkzeugeigenschaft. Ich hatte außerdem eine Frage an KZW daraus gebaut („Altlast oder Absicht?"), die mit falscher Prämisse hingegangen wäre; ihre Antwort darauf lautete **Homographie** (die flektierte Adjektivform *ist* der Verbinfinitiv, 1.223 Korpusbelege gegen 13), und **auch die ist nicht die Erklärung, was der CI-Bot zwei Stunden später gefunden und ich danach selbst nachgemessen habe.** Sie gilt für die Normalform `grozen`; der fragliche WZB-Token ist `grŏsen` und normalisiert auf `groesen`, also einen anderen Schlüssel. Gemessen in `variants.xml`: `lemma_2535` führt **neun** Formen (`grozte grozet grozten grossen grôzte grôzet grôssen grozzet grosset`), **keine davon normalisiert auf `groesen`**, und der einzige Träger dieser Normalform ist `lemma_2534` mit der Form `grösen`. Das Verblemma stand für diesen Schlüssel also nie zur Wahl. Die richtige Erklärung ist die schlichteste und stand von Anfang an in den Befund-CSVs: eine **Lücke im Variantenbestand** von `lemma_2535`. **Damit hat derselbe Fall drei Erklärungen durchlaufen, und die ersten beiden waren gebaut statt gelesen:** meine (Stufe 2 überschreibt Stufe 1), ihre (Homographie mit 1.223 Belegen), und die gemessene. Beide falschen hatten eine korrekte Messung neben sich stehen, die zu einem anderen Schlüssel gehörte.

**Die Lehre, die nicht gegriffen hat, ist die meistzitierte des Tages:** ein Befund wird erst zur Aussage, wenn die Quelle offen war, und für einen Ablauf ist die Quelle der Ablauf, nicht die Tabelle daneben. Ich hatte sie am selben Tag dreimal selbst angeführt. **Der Tag hat damit dreimal dieselbe Abwesenheits- oder Mechanismusfrage falsch beantwortet, in drei verschiedenen Gestalten:** falsche Datenquelle (`@ana`, Vormittag), falsche Kodierung (`grep -P "\xc2\xad"` findet null von zwölf weichen Trennstrichen), falsche Normalform (`groezen` statt `grozen`, Befund der Spur an sich selbst). Daraus die Fassung, die zweimal gehalten hat und die passive Formulierung ersetzt: **eine Abwesenheitsabfrage wird zuerst an einem bekannten Positivfall getestet; findet sie den nicht, ist die Abfrage widerlegt und nicht der Bestand.** Genau das hat den `grep`-Fehler binnen einer Minute gefangen, weil zwölf bekannte Vorkommen danebenlagen.


### 8. Rot, zum siebten Mal, und diesmal in einer Nachricht statt in einer Datei: einen Peer-Befund als gemessen weitergegeben, den ich nicht gemessen hatte.

**Rot, zum siebten Mal, und diesmal in einer Nachricht statt in einer Datei: einen Peer-Befund als gemessen weitergegeben, den ich nicht gemessen hatte.** Die Spur hatte einen CI-Bot-Befund mit einer Zeilenfalle erklärt (`rg -c` zähle Zeilen mit Treffer, und in der WZB stünden mehrere `<w>` je Zeile). Das klang zwingend, ich habe es übernommen, an sie zurückgespiegelt und in den Statusbericht geschrieben. **Gemessen: 0 von 235.993 Zeilen der WZB tragen mehr als ein `<w>`**, die Falle existiert nicht. Die wirkliche Ursache ist enger und hat die Spur selbst nachgereicht: das Suchmuster ließ nur Tokens zu, deren einziges Attribut `xml:id` ist, und drei der 922 tragen zusätzlich ein `pos="DIG"`. Die Bot-Zahl war korrekt erzeugt, nur nicht das, wofür er sie hielt. **Der Vorgang ist getrennt von der sechsten Zeile (Eintrag 7) zu zählen**, obwohl er denselben Modus hat: dort war es eine eigene Erfindung, hier eine fremde Übernahme, und der Anlass ist ein anderer. Die Lehre, die nicht gegriffen hat, ist wörtlich die, die im selben Gespräch gelobt wurde: ein Befund ist auch dann eine Behauptung, wenn er von einem Werkzeug oder von einer sorgfältigen Spur kommt. **Zwei Minuten Messung hätten gereicht, und ich hatte die Datei an diesem Tag schon dreimal offen.**


## 2026-09-02 – Der Wellenlauf zu Ende gebracht, und dreimal saß der Fehler im Zuschnitt der Prüfung

Aus `docs/journal-archive.md`.


### 9. Rot: `check-doc-inventories.py` lief nicht lokal, und genau er wurde rot.

**Rot: `check-doc-inventories.py` lief nicht lokal, und genau er wurde rot.** Der Welle-2-PR ging mit zwei neuen Skripten hinaus, von denen keines in `docs/DEVELOPMENT.md` und `scripts/README.md` stand. Das Gate liegt in `scripts/audit/`, und ich hatte drei andere aus demselben Verzeichnis von Hand aufgerufen. Die dokumentierte Lehre, die nicht gegriffen hat, ist die Bump-Gate-Lehre vom 31.07. in `feedback_index_version_bump`: ein Gate lokal laufen zu lassen spart eine Pipeline-Runde. Sie war auf Versionsstellen gemünzt und gilt für jedes Gate im selben Verzeichnis. Nachgetragen in `3b9abb3f9`.


### 10. Rot, dritter Auftritt derselben Bauart an einem Tag: eine Abwesenheitsabfrage, deren Zuschnitt den gesuchten Fall ausschließt.

**Rot, dritter Auftritt derselben Bauart an einem Tag: eine Abwesenheitsabfrage, deren Zuschnitt den gesuchten Fall ausschließt.** „Ein Lemma *grœzen* gibt es nicht" stand zwei Runden lang im Entwurf und war falsch: `lemma_2535` *grôzen* `VRB` existiert, mit 13 Belegen in 11 Texten. Meine Suche lief über die normalisierte Form `groezen`, *grôzen* normalisiert aber auf `grozen`. Die Regel, die die Koordination daraus formuliert hat und die hier festgehalten wird: **eine Abwesenheitsabfrage wird zuerst an einem bekannten Positivfall getestet; findet sie den nicht, ist die Abfrage widerlegt und nicht der Bestand.** Die Lehre, die nicht gegriffen hat, ist `feedback_zahlen_messvorschrift` vom 31.07.: eine Zahl ohne dokumentierte Zählweise. Für eine Null gilt sie genauso, und für eine Null ist sie gefährlicher, weil eine Null nicht auffällt.

**Derselbe Fall hat dann drei Erklärungen durchlaufen, und die ersten beiden waren gebaut statt gelesen.** Die Koordination erklärte den Fehlgriff mit einem Überschreiben durch Stufe 2, das es nach `docs/CONTRACTS.md` §C nicht geben kann (`EARLY RETURN -- skip stages 2-3`). Ich erklärte ihn mit Homographie: `grozen` trage 1.223 korrekte Adjektivtokens, `variants.xml` halte je Normalform ein Ziel, die häufigere Lesart gewinne. Auch falsch, gefunden vom CI-Review-Bot. **Das Token `grŏsen` normalisiert auf `groesen`, meine Messung galt `grozen`, das sind zwei Schlüssel.** `lemma_2535` führt neun Formen, keine davon normalisiert auf `groesen`; das Verblemma stand für diesen Schlüssel nie zur Wahl. Die gemessene Erklärung ist eine **Lücke im Variantenbestand**, und sie stand von Anfang an in den CSVs, bevor ich sie durch die schönere ersetzt habe. Beide falschen Erklärungen hatten eine korrekte Messung neben sich, die zu einem anderen Schlüssel gehörte. **Ein Vorgang mit drei Stationen, keine drei Fehler**, sonst zählt der Zähler Stationen statt Wiederholungen. Wie dünn die richtige Zuordnung ist, sagt die Gegenprobe: die Normalform `groesen` hat im ganzen Korpus 2 Tokens, eines davon ist dieses.

**Die vierte Station kam von der lokalen Review-Runde 2 und ist die einzige mit Wert über den Fall hinaus: `variants.xml` ist gar nicht einwertig.** Die Prämisse, auf der beide falschen Erklärungen ruhten, ist selbst falsch. Gemessen: **4.972 der 234.243** MHG-normalisierten Formen zeigen auf mehr als ein Lemma, *grossen* sogar auf drei. Einwertig ist erst die daraus **gebaute** Karte im Authority-Index, die je Normalform einen String führt, und der Backfill-Matcher wählt bei Mehrdeutigkeit nicht, sondern legt den Fall in den Review. **Wer über `variants.xml` argumentiert, muss sagen, ob er die Quelle meint oder die gebaute Karte**, und keine der drei Erklärungen dieses Vormittags hat das getan. Beruhigend immerhin: die Behauptung stand nur in den Artefakten dieses Laufs, nirgends in `docs/` und in keinem Projektskript.

Die Einordnung des Falls überlebt alle drei Korrekturen: unsichtbar für das Frontend, wirksam für jedes Werkzeug, das den Variantenbestand direkt liest. Das ist Kategorie C der #259-Messung, dort mit 361 Fällen beziffert, und damit hat diese Kategorie jetzt eine Adressatenangabe.

**Und damit zum eigentlichen Ärgernis des Tages: beides stand schon in `docs/CONTRACTS.md` §C.** Die Frühgeburt der Stufe 1 steht dort als Pseudocode (`EARLY RETURN -- skip stages 2-3`), und die Mehrwertigkeit steht drei Seiten weiter als benannte Regel: „**First occurrence wins** – if two lemmata claim the same variant form, only the first one stored", mit Quellenangabe auf die `if normalized_variant not in variants`-Wache in `build-authority-index.py`. Der Abschnitt nennt sogar die beiden Zahlen, die auseinanderzuhalten sind. **Zwei Sessions haben an einem Vormittag drei Erklärungen für einen Fall gebaut, und die richtige Antwort stand in dem Dokument, das genau für diese Frage angelegt ist.** Das ist keine Lücke in der Dokumentation und keine im Werkzeug: wir haben nicht nachgesehen. Die Lehre, die sich daraus formulieren lässt, ist unangenehm banal und deshalb hier ausgeschrieben: **bevor ein Mechanismus erklärt wird, wird das Dokument geöffnet, das ihn beschreibt.** Es gibt in diesem Projekt genau eines dafür, und es heißt CONTRACTS.md.


### 11. Rot, eigener Regelverstoß

**Rot, eigener Regelverstoß:** für einen Nachtrag an einem Issue-Kommentar habe ich `gh api -f body="$(cat ...)"` benutzt, also Command Substitution in einem Shell-Befehl, die die globale `CLAUDE.md` ausdrücklich verbietet. Erster Fall dieses Fehlermodus in diesem Lauf, also kein Wiederholungsfall, aber die Zeile steht hier, weil ein Zähler nur zählt, was gemeldet wird.


## 2026-09-02 (Abnahme) – Der Abbau traf die Spur im Laufen, und die Vorkehrung dagegen war schon geschrieben

Aus `docs/journal-archive.md`.


### 12. Rot, zum achten Mal, und es ist eine Abwesenheitsbehauptung über eine Datei, die zwei Verzeichnisse entfernt liegt.

**Rot, zum achten Mal, und es ist eine Abwesenheitsbehauptung über eine Datei, die zwei Verzeichnisse entfernt liegt.** Im Freeze-Befund auf #385 stand, `kickoff-bausteine.md` verlange einen Abschnitt für Meldepunkte, aber keinen für den Freeze. Beide Hälften sind falsch: Baustein 6 heißt „Was eingefroren ist" und verlangt wörtlich Dateiliste, Inbox, Format und Grund, Baustein 9 ist einer der ausführlichsten überhaupt. Aufgefallen ist es erst, als ich für den Rückfluss den Wortlaut des angeblich fehlenden Bausteins zitieren wollte. Die Messung danach fällt schärfer aus als die Behauptung davor: von zehn Bausteinen stehen **neun** im abgeschickten Auftrag, und der eine fehlende ist ausgerechnet der Freeze-Baustein, von dem im ganzen Auftrag ein Halbsatz übrig ist. Nicht das Skill hat eine Lücke, der Kickoff hat einen vorhandenen Baustein ausgelassen, und geschrieben habe ich ihn selbst. Dieselbe Bauart wie die sechste rote Zeile, Eintrag 7 (Mechanismus erfunden statt `CONTRACTS.md` gelesen). Dass ausgerechnet der Kommentar, der eine Vorkehrung gegen ungelesene Regeln fordert, selbst auf einer ungelesenen Regel steht, ist kein Zufall, sondern zeigt, wie zuverlässig dieser Fehlermodus ist.


### 13. Rot, zum neunten Mal, und dies ist der einzige Fehler des Laufs, gegen den bereits eine ausformulierte Vorkehrung an genau der richtigen Stelle stand.

**Rot, zum neunten Mal, und dies ist der einzige Fehler des Laufs, gegen den bereits eine ausformulierte Vorkehrung an genau der richtigen Stelle stand.** Der Abbau des Worktrees lief, während die Session der Spur noch lief. `git worktree remove` hat den Verwaltungseintrag entfernt und ist am Verzeichnis mit `Permission denied` gescheitert; der Inhalt war zu diesem Zeitpunkt bereits gelöscht. Das Operator-Skill nennt genau diesen Vorgang als Fehler 1: ein Worktree wurde entfernt, während die Spur noch darin arbeitete, auf Grundlage einer Fertigmeldung statt eines Blicks in die Liste laufender Sessions. `ListAgents` habe ich erst danach aufgerufen, und die Spur stand dort als `bg`, `idle`, seit sechs Stunden.


## 2026-09-02 (Nachlauf) – Zwei Befunde haben einander widerlegt, und der Test war für die falsche Sache gebaut

Aus `docs/journal-archive.md`.

**Was den Schaden verhindert hat, war nicht der Dateisystem-Lock.** Die Formulierung stammt von der Spur und korrigiert meine eigene: Windows hat den leeren Ordner gerettet, den Inhalt nicht. Verhindert hat den Verlust der Zustand der Spur, nämlich fertig gemeldet, alles gepusht, Arbeitsbaum sauber, kein Stash. Beides ist Zufall gegenüber der Vorkehrung, die gegriffen hätte. Eine Welle früher wäre der Verlust **still** gewesen: ein `git checkout origin/main -- tei/WZB.tei.xml` plus ein halber Lauf hinterlässt weder Status noch Stash, und die Entscheidungstafel der 98 Fälle war zu diesem Zeitpunkt zwei Stunden nicht committete Arbeit.

**Die tragfähige Fassung, ebenfalls von der Spur, und sie ist eine Bedingung statt einer Mahnung:** eine Fertigmeldung ist eine Aussage über die **Arbeit**, `ListAgents` ist eine Aussage über den **Prozess**, und abgebaut wird gegen die zweite. Das ist dieselbe Unterscheidung wie „Quelle oder gebaute Karte" bei `variants.xml`: zwei richtige Angaben über verschiedene Dinge, und die falsche davon beantwortet die Frage nicht.


### 14. Rot, zum zehnten Mal: eine ungemessene Annahme, die eine Entscheidung gestützt hat.

**Rot, zum zehnten Mal: eine ungemessene Annahme, die eine Entscheidung
gestützt hat.** Vorgelegt wurde chsteiner die Entscheidung, die Werkzeugzahl
ganz aus den Hilfeseiten zu nehmen, mit der Begründung, die Aufzählung daneben
trage die Aussage ohnehin und sei immer aktuell. Aufgeschlagen war dafür
nichts. Die Spur meldete daraufhin, die Aufzählung lasse den Pferde-Explorer
aus, und korrigierte sich eine Stunde später selbst: er steht sehr wohl in der
Seite, in Abschnitt 7 „Experimentelle Forschungsdaten"
(`hilfe-playground.html:621`, Karte in 646), nur nicht in der einen Liste in
Zeile 196. Ihr eigener Fehler war ein Grep auf eine CSS-Klasse, die Abschnitt 7
nicht benutzt, also wörtlich „ein leerer Abruf ist kein Nullbefund".

**Die Zeile bleibt trotzdem stehen, und zwar in umformulierter Fassung.** Sie
zählt den Fehlermodus, nicht den Ausgang: die Annahme war zum Zeitpunkt der
Entscheidung durch nichts belegt, und dass sie sich beim Nachsehen
größtenteils als richtig erweist, macht sie nicht zu einer Messung. Wer sie
streicht, weil es gutgegangen ist, macht den Zähler unfalsifizierbar, und genau
das soll er nicht sein. Richtige Fassung: sie traf für die Seite zu und für die
Liste in Zeile 196 nicht.


### 15. Rot, zum elften Mal, und diese ist die unangenehmste des Laufs: ein Positivtest, der die falsche Sache geprüft hat.

**Rot, zum elften Mal, und diese ist die unangenehmste des Laufs: ein
Positivtest, der die falsche Sache geprüft hat.** Gemeldet wurden vier
Abweichungen zwischen TEI-Headern und `works.xml` (LAU wikidata, TRO zweimal,
WZB wikidata), ausdrücklich als „selbst gemessen, mit Positivtest". Der Test
existierte und prüft die **Normalisierung**, also dass eine nackte ID und eine
volle URL auf denselben Wert fallen. Was er nicht prüft, ist die **Zuordnung**.
Beim Aufmachen der Stellen bleiben von den vieren zwei übrig.


## 2026-09-06 – Eindeutigkeit über einer Menge mit einem Element, und ein Alarm, der nur eine andere Zähleinheit war

Aus `docs/journal-archive.md`.

**Ein Test, der die falsche Sache prüft, macht eine ungeprüfte Zahl nicht
geprüft, er verkleidet sie.** Das ist der Unterschied zu den bisherigen roten
Zeilen dieses Laufs: dort fehlte die Messung, hier stand eine daneben und hat
die Lücke zugedeckt. Für den Empfänger ist das schlechter als gar keine Angabe,
weil das Prädikat ihn davon abhält, nachzurechnen. Aufgefallen ist es nur, weil
`works.xml` aus einem anderen Anlass offen war.


### 16. Rot: Eindeutigkeit über einer Menge mit einem Element ist keine Eindeutigkeit.

**Rot: Eindeutigkeit über einer Menge mit einem Element ist keine
Eindeutigkeit.** Der #387-Extraktor sammelt je normalisierter Schreibform alle
Lemmata, die im Korpus daran hängen, und annotiert, wo diese Menge einelementig
ist. Das ist richtig gedacht und war trotzdem beinahe ein falsches Tag:
`NLA_72101_5`, „wie si ze der hohzit **fvrn**", ist das Verb *varn*. Die
Schreibung `fvrn` hat korpusweit **genau einen** annotierten Beleg
(`RF_118100_0`, „fvrn hersante", zu Recht `lemma_7260`), und eine
einelementige Menge ist trivial eindeutig. Das Skript hätte das Verb zur Frau
gemacht, mit einer Begründung, die **wörtlich wahr** gewesen wäre: „alle Belege
dieser Schreibung hängen an `lemma_7260`". Behoben mit `MIN_BELEGE = 5` plus
einer namentlichen Ausnahmeliste. Die allgemeine Form der Lehre: ein Prädikat
über einer Menge braucht eine Untergrenze für deren Größe, sonst misst es die
Stichprobe statt den Gegenstand, und der Fehler versteckt sich hinter einem
Satz, der stimmt.


### 17. Rot: eine Zahl in der falschen Einheit macht eine verbuchte Altlast zu einem frischen Alarm.

**Rot: eine Zahl in der falschen Einheit macht eine verbuchte Altlast zu einem
frischen Alarm.** Gemeldet wurde chsteiner „ein echter Befund, und größer als
erwartet: 330 Korpus-Tokens verweisen mit `@ana` auf einen Sense, den weder der
Index noch das Lexikon kennt". Die 330 stimmen. Was fehlte, war die
Zähleinheit, in der die Ratsche arbeitet: **74 distinkte Sense-IDs, und alle 74
stehen seit dem 02.07.2026 in `scripts/audit/lexicon-baseline.json`.**
`check-authority-cross-refs.py` scannt `@ana` ausdrücklich (`REF_ATTRS`) und
druckt die Zeile selbst: „74 sense-ids (330 refs)", Gate grün, `CI CHECK OK`.
Es war nie ein Befund, sondern dieselbe #152-Sache in einer anderen Einheit.
Der Fehlermodus ist derselbe, vor dem der eigene #28-Kommentar desselben Tages
warnt (224 `zunge`-Widersprüche auf drei Senses), nur diesmal in eigener Sache.
**Wer eine Zahl gegen eine Ratsche hält, hält sie in deren Einheit, sonst hält
er sie gegen nichts.**


## 2026-09-06 (Nachmittag) – Eine Zusage im Perfekt, und sechsmal derselbe Fehler in verschiedenen Kostümen

Aus `docs/journal-archive.md`.


### 18. Rot, und es ist der Befund des Tages: sechs Bot-Befunde, ein einziges Muster.

**Rot, und es ist der Befund des Tages: sechs Bot-Befunde, ein einziges
Muster.** Runde 10 (die Variantenzahl an zehn Stellen), Runde 11 (die
Konfidenz-Rechnung, die einen von zwei Läufen nannte), die Zusage „der Body ist
mitkorrigiert", die geschrieben wurde, bevor sie ausgeführt war, Runde 14
Befund 1 (der billigste Check hinter dem teuersten, obwohl der Workflow-Kopf
„billig nach teuer" ausschreibt), Runde 14 Befund 2 (die offengelegte Grenze
nannte `docs/**` und `*.html`, aber nicht `playground/**`), Runde 15 (dieselbe
Grenze nannte dann drei Herkünfte als eine, und die genannte Abhilfe deckte nur
eine davon). Und nachträglich derselbe Fehler im Nachlauf-README: „31 von 31"
über einer Menge, die 30 Elemente hat. Die 31 ist dabei nicht falsch, sie zählt
die `confidence`-Fälle des ersten Laufs, und der Bot hat sie in Runde 11 selbst
so nachgemessen; nur spricht der Satz über die Fälle des zweiten Laufs, und das
sind 30. **Zwei richtige Zahlen über zwei verschiedene Mengen**, hingeschrieben
mit dem Bezugswort der falschen. Genau die Sorte, die eine Nachmessung
bestätigt, statt sie zu finden.
**Jedesmal eine Aussage über eine Menge, geschrieben aus der Kenntnis eines
Teils davon.** Das ist dieselbe Form wie die 330 `@ana`-Tokens vom Vormittag,
nur ohne Zähleinheit als Ausrede. Die Gegenmaßnahme ist keine Regel, sondern
eine Frage vor dem Schreiben: *woher weiß ich, dass das für alle gilt, und wo
steht die Zählung?* Wo die Antwort ein Kommando ist, gehört das Kommando
danebengeschrieben; die Fälle, in denen das getan wurde, sind die, die kein Bot
mehr angefasst hat.


### 19. Rot, und der Beleg dafür stammt aus diesem Absatz selbst: die Pfadfilter eines `pull_request`-Triggers schützen einen Push nicht.

**Rot, und der Beleg dafür stammt aus diesem Absatz selbst: die Pfadfilter
eines `pull_request`-Triggers schützen einen Push nicht.** **16**
`data-integrity`-Läufe sind von meinen eigenen Pushes abgebrochen worden,
darunter der allererste, der das neue Gate vollständig ausgeführt hätte.
Die Zahl stand hier zuerst als „zwei", dann als „drei", und beide Male war sie
aus dem geschätzt, was mir gerade aufgefallen war. Gemessen über die
Laufhistorie des Branches:


## 2026-09-06 (Abend) – Zehn blockierte Tickets entscheidungsreif, und drei ihrer Prämissen waren abgelaufen

Aus `docs/journal-archive.md`.

    25 abgeschlossene data-integrity-Laeufe auf diesem Branch
    16 davon cancelled, 9 success

Alle Pushes auf diesen Branch stammen aus dieser Session, also gehen alle 16
auf sie zurück, verteilt über den ganzen Tag von 09:03 bis 17:42. Das war
mithin kein Ausrutscher am Ende, sondern die Arbeitsweise des Tages.
`cancel-in-progress` gilt in diesem Workflow für `pull_request`. Beim dritten
Mal hatte ich vorher nachgesehen und mich freigesprochen: der Commit fasst nur
`docs/JOURNAL.md` und `ingest/**` an, beide stehen nicht in den Pfadfiltern,
also könne kein Lauf starten und keiner abgebrochen werden. **Gemessen ist das
Gegenteil**, und zwar an genau diesem Push:

    git show --name-only 032d859   -->  docs/JOURNAL.md
                                        ingest/pos-disambig/387-fro-adjadv/README.md
    Lauf 34043618289 auf 032d859   -->  gestartet
    Lauf 34043424099 auf f37254e   -->  cancelled

Die Erklärung ist die dokumentierte Auswertungsregel und nicht die Messung: bei
`pull_request` werden die `paths` gegen den **gesamten** PR-Diff gehalten, nicht
gegen den einzelnen Push. PR #398 fasst `tei/`, `authority-files/`, `data/` und
`scripts/audit/` an, also löst **jeder** Push auf diesen PR den Workflow aus,
gleichgültig was er enthält. Für einen `push`-Trigger gilt das nicht, und daher
kam mein Irrtum.

Der Inhalt der Lehre bleibt und wird durch die 16 eher schärfer: **wer ein
neues Gate einbaut, wartet dessen ersten vollständigen Lauf ab, bevor er
weiterschiebt.** Dazu gehört, die Prüfung „ist der Lauf durch" wörtlich zu
nehmen: am 06.09. um 17:50 standen drei der vier Checks auf `success` und
`validate` auf `in_progress`, und der Push ging trotzdem raus, weil die drei
grünen gelesen wurden und der eine laufende nicht. **Ein Check, der noch läuft,
ist kein grüner Check**, und drei von vier ist bei einem `cancel-in-progress`
genau so viel wert wie null. Neu ist, dass der Umweg
„dieser Commit fasst ja nichts Gefiltertes an" auf einem Daten-PR nicht
existiert. Und die Form des Fehlers ist wieder dieselbe: eine Aussage über eine
Menge (was löst den Workflow aus) aus der Kenntnis eines Teils davon (die
Filterliste), geschrieben ohne die Regel, nach der sie ausgewertet wird. Der
vorstehende Absatz zählt sechs solche Fälle; dieser hier ist der siebte, und er
ist entstanden, während ich den sechsten aufschrieb.


### 20. Rot: ich habe bei #358 gemessen, bevor ich den Kommentar gelesen habe.

**Rot: ich habe bei #358 gemessen, bevor ich den Kommentar gelesen habe.** Der
Kommentar vom 09.08. sagt im ersten Satz, dass der Willehalm umgestellt und
live ist. Ich hatte den Body gelesen, korpusweit gemessen, mich über den Fund
gefreut und erst danach die Kommentare geöffnet. Das ist genau die Regel, die
chsteiner in dieser Session viermal geschickt hat und die seit heute in
`CLAUDE.md` steht, und ich habe sie an dem Tag gebrochen, an dem sie
aufgeschrieben wurde. Der Schaden war nur Zeit; der Fund war schon dokumentiert.

**Und schlimmer: derselbe Kommentar beschreibt den Messfehler, den ich dann
gemacht habe.** Er hält fest, ein erster Lauf habe 48 Werke gemeldet, weil nur
`div[@n]` als Vorfahr geprüft wurde, während die Strophentexte ihre Nummer am
`lg[@n]` tragen. Mein Lauf prüfte ebenfalls nur `div[@n]` und meldete 146
Werke. Der Kommentar enthielt die Korrektur, bevor ich den Fehler machte.


### 21. Rot: beinahe Textverlust gemeldet, der keiner war.

**Rot: beinahe Textverlust gemeldet, der keiner war.** Beim #252-Abgleich fielen
fünf RVBR-Stellen auf, an denen die Vorlage einen echten Vers trägt und das TEI
eine leere Zeile. Vor dem Absenden in beiden Dateien nachgesehen: der Vers steht
eine Zeile weiter. RVBR nummeriert die `xml:id` fortlaufend statt nach
Linecode-Zeile, der Versatz war meiner. Die Meldung wäre ein Alarm über
Datenverlust in einem publizierten Korpus gewesen.


## 2026-09-11 (Nachmittag) – Anhänge nachgeholt, und zwei Zahlen, die aus zwei Mengen kamen

Aus `docs/JOURNAL.md`.


### 22. Rot: die 6.418.133 gehörten zu einem anderen Lemma als die 157.

**Rot: die 6.418.133 gehörten zu einem anderen Lemma als die 157.** In Commit-Message und Review-Auftrag stand „Kopfzeile für 40 Texte 6.418.133 -> 157 Treffer". Gemessen: `arm` als Adjektiv (`lemma_285`) hat 207 Texte, alte Kopfzeile 6.418.133, richtig wären 820 Belege; `arm` als Körperteil (`lemma_286`) hat 40 Texte, alte Kopfzeile 2.195.030, richtig 157. Der Vorher-Wert war live ohne Lemma-Zeiger abgelesen (dort gewinnt frequenzsortiert das Adjektiv), der Nachher-Wert lokal mit `ids=286`. Beide Zahlen einzeln richtig, die Differenz dazwischen erfunden. Die Lehre `feedback_aussage_neben_ihrer_menge` („die zweite Frage nach *stimmt die Zahl* ist *stimmt die Menge*") lag vor und hat nicht gegriffen. Sie ist am 02.09. aus dem Health-Check-Lauf entstanden, wo derselbe Fehler fünfmal in genau den Commits stand, die Zahlen-Drift beseitigen sollten; gefangen hat ihn auch dort der `fable-reviewer`. Gefangen hat es `fable-reviewer` in Runde 1.


### 23. Rot: eine Zuschreibung, für die ich die Quelle offen vor mir hatte.

**Rot: eine Zuschreibung, für die ich die Quelle offen vor mir hatte.** In zwei Code-Kommentaren und der Commit-Message stand „unabhängig getroffen von Alan van Beek in #419". Das Protokoll belegt es nicht: alle seine Multi-Lemma-Läufe sind Kookkurrenz-Suchen, die Dokumentsuche hat er nie geöffnet. Das Wort „Dokument" kommt in seinem Text genau einmal vor, in unserer eigenen Fehlermeldung, die ihm diesen Modus vorschlägt. Er ist dem Vorschlag nicht gefolgt. Die Lehre über Agentenbefunde („wird erst zur Aussage, wenn ich seine Quelle selbst geöffnet habe") greift hier in verschärfter Form: ich hatte die Quelle nicht nur zur Hand, ich hatte sie gelesen und trotzdem etwas hineingelegt, das gut klang. **Eine Zuschreibung ist eine Behauptung über einen Menschen und braucht denselben Beleg wie eine Zahl.** Ebenfalls vom Reviewer markiert, als „ungeprüft, nicht widerlegt"; widerlegt habe ich sie selbst.


### 24. Rot, in Runde 2 desselben Reviews: „im PDF waren die Bildpositionen leer" war ein übernommener Befund, und er stimmt nicht.

**Rot, in Runde 2 desselben Reviews: „im PDF waren die Bildpositionen leer" war ein übernommener Befund, und er stimmt nicht.** Der Satz stand zuerst im #419-Kommentar der Vorsitzung, und ich habe ihn in diesen Eintrag geschrieben, ohne das PDF zu öffnen, obwohl es seit dem Vormittag auf der Platte lag. Gemessen mit PyMuPDF: 21 Seiten, **15 eingebettete PNG**, und Seite 13 zeigt gerendert genau den Reim-Screenshot mit `Mindest-Reimpaare 6`. Die DOCX war also nie nötig, das PDF hätte gereicht. Was die Vorsitzung sah, war eine Eigenschaft ihres Zustellwegs (die Datei kam ihr als Sitzungsupload zu, und dabei blieb der Text übrig), nicht der Datei. Aus diesem falschen Befund hatte ich auch noch eine fette Lehre gebaut („ein Anhang in zwei Formaten ist nicht zweimal derselbe Anhang"), die damit ebenfalls weg ist. Die verletzte Lehre ist dieselbe wie eine Zeile darüber, nur gegen eine frühere Sitzung statt gegen einen Agenten: **der Bericht sagt, wo zu messen ist, er ist nicht die Messung.** Gefangen hat es `fable-reviewer` in Runde 2, mit derselben Methode, die mir offengestanden hätte.


### 25. Rot, vierte Zeile, am selben Tag gegen dieselbe Lehre: `items[0].keys()` ist nicht das Schema.

**Rot, vierte Zeile, am selben Tag gegen dieselbe Lehre: `items[0].keys()` ist nicht das Schema.** Für die Umlaut-Faltung in #419 habe ich gemessen, was der Fold über die Authority-Dateien anrichtet, und dafür die zu vergleichenden Felder so bestimmt: `keys = [k for k in ("termDE","termEN","title") if k in items[0]]`. Der erste Begriff im Index ist `concept_10000000` „Universum/Welt", und der trägt keine Alt-Terme. Also hat die Sonde die Alt-Felder gar nicht gesehen. Gemessen über alle Einträge tragen sie 263 von 567 Begriffen und 250 von 615 Gattungen, und der Code vergleicht sie: `multiFieldNormalized` liest im Begriffs-Explorer ausdrücklich `altDE` und `altEN`. Drei Aussagen hingen daran, alle in schon geschriebenem Text (der Zweig hatte `origin` nicht erreicht, die Runde läuft vor dem ersten Push): „keine neue Mehrdeutigkeit" (es gibt genau eine, `Vogel`/`Vögel` in `concept_14020000`, harmlos, aber der Satz war wörtlich falsch), „379 Einträge mit Umlaut" (391, die 12 fehlenden beginnen mit Großumlaut, und `foldDiacritics` kleinschreibt vorher) und der Satz im Review-Auftrag, der Index trage gar keine Alt-Felder. **Es ist dieselbe Lehre wie in der ersten roten Zeile dieses Eintrags, am selben Tag, und diesmal steckte der Mengenfehler nicht in der Zahl, sondern in der Zeile, die die Menge bestimmt.** Daraus die schärfere Form: eine Feldliste, die aus einem Stichprobenelement abgeleitet ist, ist eine Annahme über das Schema und gehört gegen alle Einträge geprüft, `Counter` über alle `keys()` statt `in items[0]`. Gefangen hat es `fable-reviewer` in Runde 1, zusammen mit dem Befund, der daraus folgte: `findAlternativeMatch` im Begriffs-Explorer stand allein auf `matchesNormalized` und lieferte für 56 Begriffe keinen „auch: …"-Hinweis mehr, obwohl sie durch die Faltung neu gelistet werden. Das ist genau die Frage, die seit #397 zur Übergabe gehört und die ich nicht gestellt hatte: **was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?**


## 2026-09-14/15 (Nachtlauf) – Neun Entscheidungen waren längst gefallen, und zweimal saß die Korrektur in einer Spiegelkopie

Aus `docs/JOURNAL.md`.


### 26. Rot: der #252-Kommentar ging mit den Zahlen von vor der Gegenprobe hinaus.

**Rot: der #252-Kommentar ging mit den Zahlen von vor der Gegenprobe hinaus.** Zwei Fehler steckten darunter. Erstens hatte ich die Fälle über `<l n="4">` identifiziert, was in FR1 einmal je Strophe vorkommt und deshalb kein Schlüssel ist. Zweitens hat die Zählung nur die direkten Kinder der Zeile nach `<w>` durchsucht, während FR1 und MSG die Wörter teils in `<supplied>` oder `<hi rend="initial">` verschachteln; dadurch landeten drei Zeilen in der falschen Gruppe (843 statt 846 Fälle, die kleine Gruppe 6 statt 3). Beide Korrekturen stehen offengelegt im ersetzten Kommentar. **Die Lehre, die nicht gegriffen hat, ist die über den Kontrollwert, und zwar ihr zweiter Halbsatz: er kommt vor dem Schreiben und nicht nach dem Commit.** Der Kontrollwert lag bereit und war stark, nämlich die drei Fälle, die der Kommentar vom 10.09. namentlich nennt; nach der Korrektur enthält die kleine Gruppe exakt diese drei. Gezogen habe ich ihn nach dem Absenden. Die letzte Zeile zu dieser Lehre steht am 02.09. (Aufräumlauf, „eine Abwesenheitsabfrage wird zuerst an einem bekannten Positivfall getestet"); dort galt die Verschärfung der Null, hier gilt sie einer Zahl.


### 27. Rot, zweiter Teil desselben Vorgangs, gegen eine eigene Lehre von vor acht Tagen: Eindeutigkeit aus drei Stichproben.

**Rot, zweiter Teil desselben Vorgangs, gegen eine eigene Lehre von vor acht Tagen: Eindeutigkeit aus drei Stichproben.** Dass `<l n="4">` je Strophe genau einmal vorkommt, hätte ein `Counter` über die Datei in einer Zeile gezeigt. Stattdessen habe ich drei Verse angesehen, bei denen es passte. Die letzte Zeile zu dieser Lehre steht am 06.09.: „Eindeutigkeit über einer Menge mit einem Element ist keine Eindeutigkeit". Damals war die Stichprobe einelementig, hier dreielementig, und der Unterschied ändert nichts: **eine Schlüsseleigenschaft wird über der ganzen Menge geprüft oder gar nicht.** Zweite Zeile zu dieser Lehre; bei der dritten wird der Mechanismus gewechselt.


### 28. Rot, und die unangenehmste: derselbe Fehlermodus zweimal in derselben Nacht, drei Stunden auseinander.

**Rot, und die unangenehmste: derselbe Fehlermodus zweimal in derselben Nacht, drei Stunden auseinander.** Bei #237 hatte der Reviewer gegen 22 Uhr gezeigt, dass mein Fix im TEI-Header sitzt, während der ausgelieferte Stand aus `works.xml` kommt. Um 22:58 ging `af2000a06` hinaus und machte bei #308 dasselbe an einer anderen Spiegelstelle: `persons.xml` und `titleStmt` gezogen, `particDesc` stehen gelassen. Gefangen hat es wieder `fable-reviewer`, Runde 2. **Warum die frische Lehre nicht getragen hat, ist der brauchbare Teil:** ich hatte sie als „prüfe, ob der `biblStruct` woanders steht" gespeichert und genau das bei #308 geprüft, statt die Frage zu stellen, die trägt, nämlich **welche Spiegel diese Änderung überhaupt berührt**. Eine Lehre, die an ihrem Beispiel klebt, ist gegen den nächsten Fall wirkungslos. Die allgemeine Form steht jetzt in CONTRACTS §F.5 und im Docstring des Gates, und das Gate ist der Teil, der auch dann greift, wenn niemand die Lehre liest.


### 29. Rot: das Datum 2026-09-15 stand an sieben Stellen und war erschlossen, nicht abgelesen.

**Rot: das Datum 2026-09-15 stand an sieben Stellen und war erschlossen, nicht abgelesen.** Weil der Lauf eine Nachtsitzung ist, habe ich aus „Nacht auf den 15." geschlossen. Gemessen sagen die Uhr, alle vier Commits und `authority-files/variants.xml` selbst den 14.; das Regenerierungsdatum widersprach damit der Datei, deren Regenerierung es beschreibt. Gefangen von `fable-reviewer` in Runde 2. Die Lehre steht seit dem 31.07. im Journal: **wer eine Zahl für historisch erklärt, misst das Datum dazu, statt es aus der Zahl zu erschließen.** Sie stammt aus derselben Klasse wie die Breve-Zahlen in §A, und sie ist hier an der billigsten denkbaren Stelle gerissen, denn das Datum stand im Sitzungskontext.


### 30. Rot, eigener Regelverstoß, und zwar zweimal in derselben Nacht aus derselben Familie.

**Rot, eigener Regelverstoß, und zwar zweimal in derselben Nacht aus derselben Familie.** Erstens habe ich für eine Umbenennung in einem Skript ein Heredoc mit mehrzeiligem Python in einen Shell-Befehl gelegt, was `shell-konventionen.md` ausdrücklich verbietet („kein Heredoc-Write, kein mehrzeiliges `python -c`"); alle anderen Ersetzungen dieser Nacht liefen als Skript im Scratchpad, mit Trefferzahl je Stelle und Abbruch bei Abweichung, also genau wie vorgesehen. Zweitens habe ich `npm test` durch `| tail -25` geschickt, obwohl die Projektregel dazu aus einem Satz besteht: nie durch eine Pipe. Der zweite Fall ist innerhalb von Minuten aufgefallen, weil die Pipe die Ausgabe bis zum Ende puffert und damit genau das verhindert, wofür sie gedacht war; der Lauf ist abgebrochen und ohne Pipe wiederholt worden. Die letzte Zeile zu einem eigenen Regelverstoß steht am 02.09. (Command Substitution in einem `gh api`-Aufruf) und trägt dieselbe Begründung: ein Zähler zählt nur, was gemeldet wird. **Beide Verstöße haben eine Gemeinsamkeit, die über sie hinausgeht: sie passierten in Befehlen, die nicht der Gegenstand der Arbeit waren.** Die Sorgfalt lag auf dem, was gemessen wurde, und nicht auf dem Werkzeug, mit dem gemessen wurde.


### 31. Rot: das Umbauskript hat den Abschnitt aus seinen Teilen neu zusammengesetzt, und was kein Teil war, fiel weg.

**Rot: das Umbauskript hat den Abschnitt aus seinen Teilen neu zusammengesetzt, und was kein Teil war, fiel weg.** Abschnitt 5 der Hilfeseite ist nicht umsortiert, sondern aus den neun extrahierten Karten plus neuen Überschriften neu gebaut worden. Verloren ging dabei die blaue Box „Kookkurrenz-Ranking vs. Nähe-Analyse", das einzige Element des Abschnitts, das keine Karte war. Die Commit-Message sagte „Die neun Karten sind unverändert umgehängt", und das stimmte sogar: **es war die falsche Menge.** Gegenstand des Umbaus war der Abschnitt, gesprochen habe ich über die Karten. Die Lehre, die nicht gegriffen hat, steht als erste Frage der Mengenregel: über welche Menge spricht dieser Satz, und woher weiß ich, dass er für alle gilt. Gefunden hat es `fable-reviewer` in Runde 2.


### 32. Rot, gleicher Commit, anderer Fehlermodus: ein Deep-Link hing an einer Eigenschaft, die die Änderung aufgehoben hat.

**Rot, gleicher Commit, anderer Fehlermodus: ein Deep-Link hing an einer Eigenschaft, die die Änderung aufgehoben hat.** Der Hilfe-Knopf des Blocks „Weitere Korpusanalysen" zeigte auf `#weitere-werkzeuge`. Das war richtig, solange Abschnitt gleich Block war. Nach der Zerlegung beginnt der Abschnitt mit der Gruppe des anderen Blocks, und wer aus dem zugeklappten Block Hilfe klickte, landete beim Kookkurrenz-Ranking, also bei genau der Verwechslung, gegen die dieser Vorgang gebaut ist. **Das ist die #397-Frage in ihrer unangenehmsten Form: der Link stand nicht im Diff.** Ich habe die Frage dem Reviewer im Auftrag mitgegeben und sie mir selbst nicht gestellt. Die Lehre steht seit #397 in CLAUDE.md, und ihr Kern trifft hier wörtlich: wer einen Umbau prüft, prüft das Neue, und was am Alten hing, prüft niemand.


### 33. Rot: „Fifteen checks" über einer Liste mit sechzehn Einträgen.

**Rot: „Fifteen checks" über einer Liste mit sechzehn Einträgen.** Der neue CI-Schritt ist als Punkt 15 in die nummerierte Liste in `docs/DEVELOPMENT.md` eingefügt worden, die Validierung auf 16 nachgerückt, und der fett gesetzte Leitsatz unmittelbar darüber blieb auf „Fifteen checks" stehen. Gefunden hat es der CI-Review-Bot auf dem PR, nachgezählt habe ich es an der Stelle: die Liste endet bei 16. **Die Lehre, die nicht gegriffen hat, ist die vom 14.09.: wer eine Stelle ändert, liest vor dem Commit ihre Nachbarschaft mit, und zwar namentlich den fett gesetzten Leitsatz über dem Absatz und jede Zahl, die mitwächst.** Sie ist am Vortag aus einem `corema`-Fall entstanden, in dem eine sechste Reviewrunde nur zustande kam, weil die Korrektur der fünften einen Fehler daneben einbaute. Hier ist es dieselbe Geometrie: der Fehler stand nicht in der eingefügten Zeile, sondern zwei Zeilen darüber. Erste Zeile zu dieser Lehre in diesem Projekt.


### 34. Rot, dritter eigener Regelverstoß derselben Familie, und der erste, der Text beschädigt hat.

**Rot, dritter eigener Regelverstoß derselben Familie, und der erste, der Text beschädigt hat.** Der Nachtrag oben ist als mehrzeiliges `python -c` in einem Shell-Befehl abgesetzt worden. Die Shell hat die Backticks um `main` als Command Substitution ausgeführt, quittiert mit „main: command not found", und das Wort aus dem Satz entfernt; im selben Aufruf standen ASCII-Ersatzschreibungen in deutscher Prosa, weil ich den Umlauten im Inline-Text ausweichen wollte. `shell-konventionen.md` verbietet beides namentlich: kein mehrzeiliges `python -c`, keine Command Substitution, Textersetzung über ein Skript per Write. Alle anderen Ersetzungen dieser Nacht liefen genau so, mit Trefferzahl je Stelle und Abbruch bei Abweichung. **Die beiden früheren Zeilen stehen oben** (Heredoc für eine Umbenennung, `npm test` durch eine Pipe), und damit ist es die dritte: die Regel sagt, dass jetzt der Mechanismus zu wechseln ist und nicht weiter gezählt wird. **Der Mechanismus ist da und ich habe ihn umgangen**, denn Write plus `python skript.py` kostet keinen Gedanken mehr als der Einzeiler. Was die drei Fälle verbindet: alle drei passierten in Befehlen, die nicht der Gegenstand der Arbeit waren, sondern nur schnell etwas erledigen sollten. Der Vorschlag für den Wechsel steht im Übergabeteil unten.


## 2026-09-15 – #204 im Playground: der erbetene Hinweis wäre eine Zusicherung ohne Deckung gewesen

Aus `docs/JOURNAL.md`.


### 35. Rot: eine Pluralstelle repariert und den Satz daneben nicht mitgelesen.

**Rot: eine Pluralstelle repariert und den Satz daneben nicht mitgelesen.** Der neue Hinweis meldete „1 Texte ausgewählt", sobald genau ein Text ausgewählt und vom Filter verdeckt war. Der Fix machte daraus „1 Text" und ließ das Verb stehen: „Für die Analysen **sind** weiterhin 1 Text ausgewählt." Committet, gepusht, durch CI, gefunden erst vom Review-Bot eine Runde später. **Die Lehre, die nicht gegriffen hat, ist dieselbe wie am 14.09.: wer eine Stelle ändert, liest vor dem Commit ihre Nachbarschaft mit.** Die letzte Zeile dazu steht unter „Fifteen checks" über einer Liste mit sechzehn Einträgen; das ist die zweite. Dieselbe Geometrie wie dort, nur eine Zeile statt zwei entfernt: der Fehler stand nie in dem, was ich geändert hatte.

## 2026-09-18 – CLAUDE.md verdichtet, und derselbe Gate-Fehler zweimal parallel repariert

### 36. Rot: die Ausgabe eines Gates als Befund weitergegeben, ohne den Schluss daraus zu prüfen.

**Rot: die Ausgabe eines Gates als Befund weitergegeben, ohne den Schluss daraus zu prüfen.** `doc-count-audit.py --check` lief rot, und ich habe chsteiner vorgelegt, die Doku sei alt: sechs Stellen nennen 11 Analysewerkzeuge, 19 Entry Points und 12 Pattern-Module, gemessen seien 12, 20 und 13. Die Freigabe zum Nachziehen kam daraufhin. Beim Nachsehen war es umgekehrt: #204 hat `playground/js/ui/tei/corpus-scope.js` angelegt, ein Hilfsmodul, das acht Werkzeuge importieren, das selbst nichts anzeigt und keinen Knopf in `playground/index.html` hat. Kein Analysewerkzeug, also war die **Messung** falsch und die Doku-Zahlen waren es nicht.

**Die Lehre, die nicht gegriffen hat: der eigene Befund ist der gefährlichere, weil eine selbst erhobene Messung sich geprüft anfühlt, auch wenn nur die Zahl gemessen wurde und nicht der Schluss daraus** (`agentenbefunde.md`). Gemessen hatte ich die Ausgabe des Werkzeugs; behauptet habe ich, welche Seite der Differenz die falsche ist. Die letzte Zeile zu dieser Lehre ist Eintrag 24, wo derselbe Satz wörtlich steht: der Bericht sagt, wo zu messen ist, er ist nicht die Messung. Hier war der Bericht das eigene Werkzeug.

**Die „sechs Stellen" waren ihrerseits falsch, und das ist derselbe Fehler eine Ebene tiefer.** Ich habe die Ausgabe des Gates mit `head -40` gelesen und die Summenzeile darunter nie gesehen. Gemessen sind es **11 Treffer in 9 (Datei,Key)-Paaren über fünf Dateien**: neben den drei genannten auch `docs/DESIGN.md` (Zeile 162) und `playground/readme.md` (Zeilen 38 und 124). Sechs war die Zahl der Paare in den drei Dateien, die oben im abgeschnittenen Fenster standen. Gefunden hat es `fable-reviewer` in Runde 1, nachgemessen habe ich es an den beiden Zeilen.

**Repariert hat das Gate am Ende nicht dieser Vorgang, sondern #449**, siehe die nächste Zeile.

### 37. Rot, erste Zeile zu dieser Lehre: eine Entscheidungsfrage ohne den bisherigen Stand daneben, und der Stand war ein offener PR mit demselben Inhalt.

**Rot, erste Zeile zu dieser Lehre: eine Entscheidungsfrage ohne den bisherigen Stand daneben, und der Stand war ein offener PR mit demselben Inhalt.** Ich habe chsteiner gefragt, ob der Zähl-Drift als eigener Commit nachgezogen werden soll, habe die Freigabe bekommen, einen Zweig gebaut, zwei `fable-reviewer`-Runden und zwei Runden des CI-Bots verbraucht und PR #450 aufgemacht. Beim Merge kam der Konflikt: **KZW hatte #449 mit derselben Diagnose und derselben Reparatur schon offen**, und zwar `corpus-scope.js` in `NON_TOOL_MODULES`, ui_modules 24 auf 25, beide veralteten `INTENTIONALLY_SILENT`-Einträge, Docstring und Variablenname, Bezeichner statt Zeilennummern in `data-integrity.yml`. Gemessen mit `gh pr view --json createdAt`: #449 um 07:34:34 UTC erstellt, #450 um 08:01:56, #449 gemergt um 08:21:38. Der fremde PR war 27 Minuten offen, als meiner entstand.

**Die Lehre, die nicht gegriffen hat, steht in `entscheidungsfragen.md`: eine Entscheidungsfrage an chsteiner nur mit dem bisherigen Stand daneben, also was dazu schon entschieden wurde, wann und wo es steht.** Ich habe den Satz bisher auf Issues und Vorgänge gelesen, und er gilt genauso für den offenen PR-Bestand: ein `gh pr list` vor der Frage hätte gereicht, und es hätte den ganzen Zweig erspart. Dieselbe Prüfung fehlt in `CLAUDE.md`, wo die Regel über nebenläufige Sessions nur vom geteilten Arbeitsbaum spricht und nicht von doppelter Arbeit an derselben Sache.

**Was übrig blieb, war klein**: `docs/DESIGN.md` nannte weiter zwei Ausnahmen statt drei, der Kommentar am `TREE_LINE_RE`-Skip belegte sich mit zwei Ständen alten Zitaten, und diese beiden Zeilen. Der Rest war doppelt gemacht. **#449 war an einer Stelle sogar besser:** es nennt in `ARCHITECTURE.md` die Achtermenge der Importeure gar nicht und koppelt sie deshalb auch nicht an die falsche Begründung, was in #450 ein Bot-Befund war.


## 2026-09-21 – KZW-Triage neu aufgebaut, nachdem sie die alte zurückgewiesen hat

### 38. Rot: eine Zahl aus der eigenen Verdichtungszusammenfassung übernommen, statt sie zu messen.

**Rot: eine Zahl aus der eigenen Verdichtungszusammenfassung übernommen, statt sie zu messen.** Ich habe chsteiner gemeldet, alle Kommentare aller offenen Vorgänge seien gelesen, „19.590 Zeilen“. Gemessen mit `wc -l` über die acht Abzugsdateien sind es **19.582**. Die Zahl stand in der Zusammenfassung der Verdichtung, die diese Sitzung eröffnet hat, und ich habe sie fortgeschrieben, obwohl `wc -l` drei Sekunden kostet und die Dateien offen daneben lagen.

**Die Lehre, die nicht gegriffen hat, steht in `agentenbefunde.md`: eine Verdichtungszusammenfassung ist ein Agentenbericht, und was aus ihr stammt, ist Selbstauskunft und keine Messung, auch wenn es die eigene Sitzung von vor einer Stunde war.** Die Regel sagt den Mechanismus wörtlich dazu: der Griff zurück in die Quelle ist hier nicht schwerer als bei einem fremden Bericht, nur fällt niemandem ein, ihn zu tun. Die letzte Zeile zu dieser Lehre ist Eintrag 36.

**Was sie getragen hat:** sie stand als Beleg für die Vollständigkeit der Lektüre in der Antwort an chsteiner, also unter genau der Aussage, um die es ging. Abgefangen hat sie der `mengen.md`-Hook beim Schreiben des öffentlichen Kommentars an #406, eine Stunde später. **Das ist kein abgewendeter Fehler**, denn er hatte da schon getragen; abgewendet ist nur, dass er zusätzlich in einem Kommentar an KZW gelandet wäre, und zwar in genau dem, der ihr vorwirft, mit ungeprüften Angaben zu arbeiten.

**Nicht gezählt, aber genannt:** beim Schließen von #169 lief `gh issue close --comment "$(cat ...)"`, also eine Command Substitution, die `shell-konventionen.md` verbietet. Der Grund war, dass `gh issue close` kein `--body-file` kennt; richtig wäre gewesen, erst zu schließen und dann `gh issue comment --body-file` abzusetzen. Keine rote Zeile, weil niemand danach etwas Falsches getan hätte: der Kommentar steht korrekt.


### 39. Rot, zweite und dritte Zeile desselben Tages: die Quelle lag offen im Kontext, und an ihrer Stelle stand das eigene Vorwissen.

**Rot, zwei Fälle in einer Stunde, beide gefunden vom `fable-reviewer` und nicht von mir.** Erstens: das Einfrieren von #271 auf den 11.09.2026 datiert, in einem öffentlichen Kommentar an #406 und im Body des frisch angelegten #453. Gemessen fiel die Entscheidung am **10.09.**, vorgeschlagen 15:24 und in der Jahreszahl bestätigt 16:41; der Kommentar vom 11.09. („Ja, mach 1. zu NEIM“) ist eine andere Entscheidung im selben Thread. **Ich hatte diesen Thread eine Stunde vorher selbst extrahiert und gelesen.** Zweitens: in `CLAUDE.md` die Angabe „from 28 labels down to 16“ fortgeschrieben, obwohl `gh label list` im selben Vorgang **20** ausgegeben hatte und die Ausgabe im Kontext stand.

**Die Lehre, die nicht gegriffen hat, ist in beiden Fällen dieselbe und steht in `eigene-quellen.md`: der Fehlermodus heißt nicht „Regel unbekannt“, sondern geladene Quelle nicht befragt.** Die Antwort lag offen, und an ihre Stelle trat das eigene Vorwissen. Die letzte Zeile dazu ist Eintrag 38 vom selben Tag, und damit ist es die dritte.

**Was sie getragen haben:** das falsche Datum stand in einem Kommentar an KZW, der ihr gegenüber begründet, warum ihre Antworten nicht mehr als Rückstand geführt werden. Beide Stellen sind berichtigt, der Kommentar mit einem eigenen Nachtrag statt durch stille Änderung. Die Labelzahl stand im Commit `18b98c423` und wäre ohne die Reviewrunde gemergt worden.

**Die dritte Zeile heißt Mechanismuswechsel statt weiterzählen, und der Mechanismus existiert bereits zweimal**, weshalb hier keiner gebaut wird: projektseitig als #454 (Staleness, mit diesen Fällen als Belegen), generisch als [`claude-code-setup#64`](https://github.com/chsteiner/claude-code-setup/issues/64), wo der Trockenlauf für einen Hook steht, der prüft, ob eine im Text genannte Fundstelle in dieser Sitzung überhaupt gelesen wurde. Genau dieser Hook hätte alle drei Fälle gefangen: in allen dreien **war** sie gelesen, nur nicht befragt. **Das ist der Unterschied, den #64 noch nicht misst**, und er gehört dort als Befund hinein.


## 2026-09-21 – Spur A des Datenlaufs: #366, #375 und #371

### 40. Rot: einem Menschen zugeschrieben, er habe etwas geprüft, weil ein Feld daneben so klang.

**Rot: einem Menschen zugeschrieben, er habe etwas geprüft, weil ein Feld daneben so klang.** In #371 sollen drei Tokens (`ADP_6505000_1`, `ADP_6511900_11`, `ADP_6605700_8`) von `pos="NOM"` auf `VRB` wechseln, und das ist die einzige Stelle des ganzen Laufs, an der ein vorhandener Attributwert weicht. Als Begründung dafür habe ich gemeldet, KZW habe den vorhandenen NOM-Wert gesehen und ausdrücklich dagegen entschieden, und dafür ihr Feld `begruendung` zitiert („Der Fall lag nur wegen des vorhandenen pos NOM im Review") sowie `batch_verdict.grund: prior-konflikt`. **Beides ist nicht ihre Stimme.** Nachgemessen am abgelegten JSON: ihr Feld `notiz` ist bei allen drei Fällen leer, und `begruendung` ist dreiteilig, bei 19 von 95 Fällen wortgleich mit `notiz`, bei 6 der generierte Satz „Abweichung von Claudes Vorschlag, ohne Notiz." und bei 70 ein analytischer Text, der nicht aus `notiz` stammt. `batch_verdict` weicht bei 25 Fällen von `pos` ab und trägt auch dort ein Urteil, wo sie `pos: null` gesetzt hat, ist also ein Maschinenurteil. Was ihre Entscheidung wirklich trägt, sind die Felder `pos`, `option` und `status`, und die sagen für alle drei VRB. **Die Handlung war richtig, die Begründung nicht.**

**Die Lehre, die nicht gegriffen hat, steht in `agentenbefunde.md`: die Quelle gelesen zu haben genügt nicht, sie muss die Aussage hergeben, die auf ihr steht, und bei einer Zuschreibung ist das keine Ungenauigkeit, sondern eine Behauptung über einen Menschen.** Ich hatte das JSON selbst geparst und die drei Sätze im Original vor mir; hineingelegt habe ich, wer sie geschrieben hat. Die letzte Zeile zu diesem Teilfall ist Eintrag 23, wo derselbe Satz steht: eine Zuschreibung braucht denselben Beleg wie eine Zahl.

**Was sie getragen hat:** der Satz war die angekündigte Begründung für den PR-Text und wäre dort gelandet; ein Leser hätte geglaubt, die wissenschaftliche Leitung habe diesen Konflikt geprüft. Im PR steht jetzt, dass KZW für diese drei VRB entschieden hat und der Wert dabei überschrieben wird, ohne den Satz über ihr Sehen.

**Angehalten hat ihn nicht die eigene Prüfung.** Die Rückmeldung der Koordination in derselben Stunde sagte, die Handlung sei gedeckt und die Begründung nicht; das ist der Wortlaut, wie ihn die Verdichtungszusammenfassung dieser Sitzung zitiert, und weiter reicht der Beleg nicht, denn das Sitzungstranskript ist nach `vertraulichkeit.md` gesperrt und die Betriebsliste der Koordination führt den Punkt nicht. Hier stand bis zur Korrektur „gefangen hat ihn die Koordination, nicht ich", und das war in einer Zeile über eine unbelegte Zuschreibung selbst eine: **dass eine Zuschreibung dem Schreibenden schadet statt nützt, macht sie nicht belegt, sondern nur unverdächtig.**

**Kein neuer Mechanismus, und das ist begründet:** `agentenbefunde.md` ist seit dem 16.09.2026 ausdrücklich ausgesetzt, weil kein Muster sieht, ob ein Satz mehr behauptet als seine Quelle. Die Aussetzung ist nach `wiederholte-fehler.md` selbst der Mechanismus. Was hier tatsächlich gegriffen hat, war der Satz im Kickoff, dass auch die Angaben der Koordination nachzumessen sind, angewandt in die Gegenrichtung.

### 41. Rot, erste Zeile zu dieser Lehre: die Trefferzahl stimmte, die Einfügeposition nicht, weil die Zeilenenden ungeprüft blieben.

**Rot, erste Zeile zu dieser Lehre: die Trefferzahl stimmte, die Einfügeposition nicht, weil die Zeilenenden ungeprüft blieben.** Das Skript für den Versions-Bump hängt die Changelog-Texte ans Ende der Kommentarzeile, die den Anker trägt, und sucht dafür das nächste `\n`. Die vier Zieldateien tragen CRLF, der Text landete also zwischen `\r` und `\n` und damit in einer eigenen Zeile. `scripts/build-corpus-index.py` brach beim nächsten Lauf mit `SyntaxError: ':' expected after dictionary key` ab, `corpus-loader.js` und `build-authority-index.py` waren genauso beschädigt. Die Ersetzungen selbst waren korrekt und meldeten Trefferzahl 1: **geprüft wurde, ob die Stelle gefunden wird, nicht, wohin geschrieben wird.**

**Die Lehre existiert und ihre Bedingung war zu eng gefasst, um zu greifen.** `shell-konventionen.md` sagt „Wer `sed` doch nimmt, prüft danach die Zeilenenden der Datei". Ich habe kein `sed` genommen, sondern genau den vorgeschriebenen Weg: ein Skript per Write, ausgeführt mit `python skript.py`, mit Trefferzahl je Ersetzung und Abbruch bei Abweichung. Die Regel hat deshalb formal nicht gegriffen, ihr Kern aber sehr wohl. **Die Konsequenz ist keine neue Regel, sondern eine Weitung der bestehenden: die Zeilenenden gehören nach jeder programmatischen Textänderung geprüft, nicht nur nach `sed`.** Wo eine Trefferzahl nur die Fundstelle prüft und nicht das Ergebnis, ist der billige Zusatz ein Syntaxcheck der geschriebenen Datei; für Python kostet er einen `ast.parse`, für JavaScript ein `node --check`.

**Was er getragen hat:** die vier Dateien waren einige Minuten kaputt, der Index-Build lief nicht. Gefangen hat ihn der Build selbst und keine Prüfung, die ich gebaut hätte, und das ist der Unterschied zu einem abgewendeten Fehler. Zurückgenommen mit `git checkout --` auf die fünf Bump-Dateien, was hier unbedenklich war, weil sie unverändert auf HEAD standen und nichts anderes an ihnen hing: das ist eine Aussage über diesen Fall und keine über das Kommando, das aus dem Index herstellt und nicht aus dem Stand davor.

### 42. Rot: zwei Variantenzahlen mit einem Skript gezogen und die dritte im selben Absatz daneben stehengelassen.

**Rot: zwei Variantenzahlen mit einem Skript gezogen und die dritte im selben Absatz daneben stehengelassen.** In allen drei Provenienzdokumenten dieses Laufs steht der Satz „Korpusweit tragen 1.554.314 von 7.547.816 `<w>` mit `@lemmaRef` kein `@ana`": `ingest/pos-disambig/366-fyndling/README.md`, `ingest/pos-disambig/371-stat/README.md` und `scripts/ingest/pos-disambig/apply-366-375-371.py`. Beide Zahlen sind Stände **vor** dem Lauf, in Dateien, die den Zustand **nach** dem Lauf beschreiben. Gemessen nach dem Rebuild über alle 667 Dateien in `tei/`: 1.554.398 von 7.547.900, die Differenz ist beide Male 84 und damit genau die Tokens dieses Laufs. Im selben Zug lief ein Skript mit 19 Ersetzungen, mit Trefferzahl je Ersetzung und Abbruch bei Abweichung: **die Formenzahl an 10 Stellen in 7 Dateien, die Mappingzahl an 9, dazu dreimal ein Datum oder ein Skip-Marker.** Auch diese Aufzählung ist nachgemessen, denn die erste Fassung dieser Zeile sagte „die Formenzahl an 19 Stellen“, und 19 ist die Zahl der Aufrufe über alle fünf Sorten. **Eine vierte Stelle hat erst die Reviewrunde gefunden**, im selben 366-README: „`lemma_2039` trägt heute 39 Tokens in 15 Dateien", gemessen sind es 40, und die Differenz ist genau das Token dieses Laufs. Drei Stellen selbst gefunden und eine übersehen, und die übersehene stand acht Zeilen unter einer Messung, die ich am selben Tag mit Stichtag versehen hatte.

**Die Lehre, die nicht gegriffen hat, steht in `korrigieren.md`: wer eine Stelle ändert, liest vor dem Commit ihre Nachbarschaft mit, namentlich jede Zahl, die mitwächst.** Die letzte Zeile dazu ist Eintrag 35, davor Eintrag 33, und damit ist es die dritte.

**Was sie getragen hat:** vier committete Stellen, und im PR-Entwurf stand die Zahl ebenfalls. Aufgefallen sind die ersten drei beim Nachmessen für den PR-Text, weil die Zahl aus der Verdichtungszusammenfassung stammte und nicht aus einer Messung. Dabei kam ein zweiter Bezugsfehler mit heraus, der nur im Entwurf stand und deshalb keine eigene Zeile bekommt: „Korpus-Index `totalWords`" gibt es nicht. Der Korpus-Index führt oben `version`, `totalTexts`, `totalLemmata`, `texts` und `lemmaIndex`; `totalWords` ist eine Laufzeitsumme des Playgrounds aus `wordCount` je Text (`playground/js/playground-main.js:357`). Die Zahl stimmte, ihr Bezug war erfunden, und **eine richtige Zahl mit erfundenem Bezug übersteht jede Gegenprobe, die nachrechnet.**

**Kein neuer Mechanismus, und die Begründung steht nicht hier, sondern in der Regel:** `korrigieren.md` ist seit dem 16.09.2026 ausgesetzt ([#59](https://github.com/chsteiner/claude-code-setup/issues/59)), weil das, was „daneben" ist, der Sinn entscheidet und nicht der Abstand. Nach `wiederholte-fehler.md` ist die begründete Aussetzung selbst der Mechanismus, also ist bei der dritten Zeile keiner zu bauen. **Den Teilfall-Mechanismus, den die Regel führt, habe ich trotzdem geprüft, und er passt nicht:** er besteht im Weglassen, und die Aussage „der Zustand ist Praxis und kein Loch" ist ohne Größenordnung daneben eine Behauptung. Was stattdessen in die vier Stellen kommt, ist die frische Zahl **mit Stichtag und Messvorschrift**, und das ist eine Verbesserung des Textes und keine Vorrichtung: ein Provenienzdokument hält einen Lauf an einem Datum fest, falsch war nicht die Zahl, sondern die Gegenwartsform „Korpusweit tragen …" in einer Datei über einen abgeschlossenen Zustand. **Die Form, die nicht altert, führt dieses Projekt für exakt dieselbe Aussage schon vor:** `playground/index.html:140` sagt „Korpusweit tragen rund 20 % der Wortformen keine."

**Zum Suchen dieser Lehre, damit die nächste Session den Zuschnitt nicht wiederholt.** Eine Suche nach `korrigieren.md` in diesem Journal ergab vor diesem Eintrag null, und das war kein Nullbefund: die Lehre steht hier zweimal, aber beide Male in Prosa („Nachbarschaft", „mitwächst"). **Eine Regeldatei beim Namen nennen überhaupt nur die Einträge 30, 34, 36, 37, 38, 39 und die von heute**, und von den Einträgen 1 bis 35 sind es genau zwei: 30 und 34, beide `shell-konventionen.md`. Der praktische Satz daraus, und er gilt unabhängig von jeder Zahl: **wer ein Fehlerjournal nach Regeldateinamen durchsucht, sieht die ersten 35 Einträge nicht.** Die Gewohnheit ist ein paar Tage alt.

Hier stehen Nummern und keine Anzahl, und das aus zwei Gründen. Erstens lässt sich ein Name falsifizieren und eine Anzahl nicht. Zweitens wäre jede Grundmenge hier eine Aussage über einen Arbeitsbaum: dieser Zweig steht auf einer Basis vor den Einträgen der Koordination, und mit der Nummernvergabe je Spur ist die Nummernfolge des Journals ab heute **nicht mehr lückenlos**. Wer künftig aus der höchsten Nummer auf die Anzahl schließt, zählt falsch. Auch die Zahl der Nennungen ist zweimal gemessen worden, weil der erste Griff Grep-Treffer für Einträge genommen hatte: eine Zeile kann zwei Nennungen tragen, und eine steht außerhalb jedes Eintrags. Und ein Kontrollwert hat nicht getroffen: Eintrag 33 führt die Lehre auf einen `corema`-Fall vom 13.09. zurück, `corema/fehlerjournal.md` führt ihn nicht. Der Fall liegt also woanders als in jenem Journal, die Suche war richtig und die Herkunftsangabe ist ungenau.

### 43. Rot: die #397-Frage gestellt, verneint, und die Verneinung war eine Abwesenheitsbehauptung über den halben Bestand.

**Rot: die #397-Frage gestellt, verneint, und die Verneinung war eine Abwesenheitsbehauptung über den halben Bestand.** Zehn neue Variantentypen stellen eine Invariante her, und die Frage aus #397 lautet, was dadurch wahr wurde, das vorher falsch sein konnte. Ich habe sie gestellt und mit „gesucht und nicht gefunden" beantwortet: der Bestand kenne keine Prüfung, der die Prägungen den Gegenstand entziehen. Der Satz steht committet in `docs/JOURNAL.md` und stand im PR-Entwurf. **Er ist falsch, und die Antwort lag eine Ebene tiefer.** Das normalisierte Laufzeit-Wörterbuch des Authority-Index hat die Schreibform `hawsen` von `lemma_49714` *hûsenblâter* auf `lemma_42619` *hûse* umgehängt, weil first-wins nach Lemmanummer auflöst und 42619 vor 49714 sortiert. Wer künftig „hawsen" sucht, erreicht 4 Belege statt 32. Gefunden hat es die lokale Reviewrunde, nachgemessen habe ich es selbst: added 5, removed 0, re-pointed 1.

**Die Lehre, die nicht gegriffen hat, steht in `dateisuche.md`, und zwar in ihrem Zuschnitts-Halbsatz: den Zuschnitt prüft der Kontrollwert nur mit, wenn er außerhalb von ihm liegt.** Mein Kontrollwert war stark und lag mitten im Zuschnitt: 613 Typen mit mehr als einer Form und 1 mit mehr als einem Lemma, vor und nach dem Lauf identisch. Er misst die **Typ**-Ebene, und auf der war auch alles richtig. Die Frage, die davorsteht, habe ich nicht gestellt: warum ist der Suchpfad dieser und nicht der ganze Bestand. Die letzte Zeile zu dieser Lehre ist Eintrag 26, davor 10 und davor 4, **und damit ist es die vierte.**

**Vier Zeilen, und jede traf einen anderen Halbsatz derselben Regel.**

| Zeile | Halbsatz, der riss |
|---|---|
| 4 | der Kontrollwert überhaupt: „eine Abwesenheitsbehauptung braucht eine Abfrage, die Anwesenheit zeigen könnte" |
| 10 | an einem bekannten Positivfall: „findet sie den nicht, ist die Abfrage widerlegt und nicht der Bestand" |
| 26 | vor dem Schreiben: „er kommt vor dem Schreiben und nicht nach dem Commit" |
| 43 | außerhalb des Zuschnitts: „den Zuschnitt prüft der Kontrollwert nur mit, wenn er außerhalb von ihm liegt" |

Die Regel ist dreimal nachgeschärft worden, und jedes Mal ist beim nächsten Mal der neu hinzugefügte Halbsatz gerissen; der von heute ist fünf Tage alt. **Das ist eine Beobachtung an vier Fällen und kein Beleg**, aber wenn sie kein Zufall ist, sagt sie etwas über Nachschärfung als Mechanismus: der neueste Halbsatz einer Regel ist ihr ungeübtester und damit ihre nächste Bruchstelle.

**Und hier ist die vierte Zeile nicht der Beleg, dass niemand die Konsequenz gezogen hat.** Sie ist gezogen, gebaut, gemessen und läuft: `claude-code-setup/hooks/suchergebnis.sh` und `enge-suche-lib.sh`, entstanden zu Vorgang #62 nach genau dem Fehler, der den vierten Halbsatz erzeugt hat. Der Kopf der Datei nennt die Auslösebedingung, und sie ist der Grund, warum der Hook hier nicht greifen konnte: **„eng zugeschnittene Suche UND leeres Ergebnis"**, mit der ausdrücklichen Begründung, der Fehler entstehe „beim Schluss aus ihrem leeren Ergebnis". Mein Abruf war nicht leer. Er war voll, richtig, und maß eine Ebene über der Antwort. Die Lücke ist die dokumentierte Grenze des Gegenstands und keine Schwäche der Vorrichtung; am selben Tag hat sie bei zwei wirklich leeren Suchen in diesem Journal zugearbeitet. **Wer das nicht dazuschreibt, hinterlässt eine vierte Zeile ohne Vorrichtung, wo eine Vorrichtung mit einer benannten Lücke steht.** Was fehlt, wäre ein Muster für die andere Hälfte: nicht das leere Suchergebnis, sondern die Abwesenheitsaussage im geschriebenen Text („gesucht und nicht gefunden", „der Bestand kennt keine"). Als Vorschlag an `claude-code-setup` weitergegeben, wo er hingehört; in diesem Projekt wäre nichts zu bauen, was nicht am falschen Ort stünde.

**Zum Zählen dieser Lehre, denn der Zuschnitt ist heikel.** Eintrag 10 weist in seinem Lehre-Absatz eine andere Gruppe zu und formuliert die Kontrollwert-Regel daneben neu; dass er dazugehört, sagt erst Eintrag 26, der ausdrücklich auf ihn zurückverweist. Seine Ortsangabe dort ist ungenau („Aufräumlauf", tatsächlich steht 10 unter „Der Wellenlauf zu Ende gebracht"), die wörtlich zitierte Formulierung kommt aber im ganzen Journal nur an dieser einen Stelle vor. Umgekehrt trägt **Eintrag 12** die Wörter „Abwesenheitsbehauptung" in seiner Überschrift und gehört trotzdem nicht dazu, weil sein Lehre-Absatz eine andere Gruppe zuweist. **Eine Überschrift ist keine Zuweisung, und wer nach Überschriften zählt, zählt ihn mit.**

**Was sie getragen hat:** der Satz war die Antwort auf die Pflichtfrage des Projekts an jeden Fix, er stand committet, und er hätte im PR-Text die Aussage getragen, dieser Lauf habe keine Nebenwirkung. Er hat eine, und sie trifft eine Suche, die nichts mit den 88 annotierten Tokens zu tun hat. Der PR-Text trägt sie jetzt als eigenen Abschnitt und als ersten von vier Punkten, die nach dem Merge bei KZW liegen.

**Und die Gegenprobe, die es gefunden hätte, ist in diesem Projekt seit dem 14.09. beschrieben.** `docs/DECISIONS.md` fordert unter ADR-021 genau diesen Vergleich als Handgate, „added / removed / re-pointed" über die beiden gebauten Wörterbücher, ausdrücklich damit „a single re-annotation cannot silently flip a mapping". Ich habe das Dokument in diesem Lauf zweimal geöffnet und an zwei Stellen geändert, ohne den Absatz zu lesen, der das Gate für genau meine Art von Änderung verlangt. **Das ist derselbe Fehlermodus wie Eintrag 39, geladene Quelle nicht befragt, hier aber nicht der Kern:** der Kern ist der Zuschnitt, denn auch ohne ADR-021 hätte die zweite Frage aus `dateisuche.md` gereicht. Der Lauf liefert dem geforderten Gate jetzt sein erstes rotes Testdatum, und das steht in DECISIONS.md neben dem grünen vom 14.09.
