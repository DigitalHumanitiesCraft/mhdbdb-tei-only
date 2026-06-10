# WB-DEA meets MHDBDB: 150.000 blinde Wörter und was daraus wurde

Julia Hintersteiner (Paris Lodron Universität Salzburg) / Christopher Pollin (Zentrum für Informationsmodellierung, Universität Graz)

**1000 Worte Forschung**: *Miniprojekt (Digital Humanities/Germanistische Mediävistik) im Rahmen von CLARIAH-AT, Paris Lodron Universität Salzburg / Zentrum für Informationsmodellierung, Universität Graz, 2025*

---

Wenn man eine mittelalterliche Bibelübersetzung in eine computationelle Suchinfrastruktur einbringt, begegnet man irgendwann dem Wort *vortilgen*. Für eine Leserin mit Kenntnissen böhmischer Schreibkonventionen ist das offensichtlich *vertilgen* — ein ganz gewöhnliches mittelhochdeutsches Wort. Für ein automatisches Wörterbuchabgleichsystem ist es nichts. Kein Treffer. Kein Lemma. Ein unsichtbares Wort in einem sichtbaren Text.

Diese Lücke — in tausend Varianten — ist der Ausgangspunkt des CLARIAH-AT Projekts zur Integration der *Wenzelsbibel* (Pentateuch: Gen–Dtn) in die *Mittelhochdeutsche Begriffsdatenbank* (*MHDBDB*).

**Zwei Infrastrukturen, eine Frage**

Die *Wenzelsbibel Digital Edition and Annotation* (*WB-DEA*) und die *MHDBDB* haben grundverschiedene Zielsetzungen. *WB-DEA* ist eine editorische Tiefenbohrung: diplomatische Transkription, normalisierte Formen, elaborierter Kommentar — alles auf einen einzigen außergewöhnlichen Text konzentriert. Die *MHDBDB* ist ein semantisches Suchnetz: rund 670 mittelhochdeutsche Texte, 43.750 Lexikoneinträge, verknüpft mit GND, Wikidata und Handschriftencensus. Die Leitfrage des Projekts: Wie überführt man eine hochwertige digitale Edition in eine semantische Korpusinfrastruktur, ohne die editorische Substanz des einen oder die Suchmächtigkeit des anderen zu opfern?

Das Objekt ist außergewöhnlich. Die *Wenzelsbibel* entstand um 1389–1395 im Auftrag König Wenzels IV. von Böhmen: sechs Prachtbände, 1.214 Blätter, über 650 ganzseitige Miniaturen — eines der aufwändigsten Buchprojekte des deutschsprachigen Mittelalters und eine der frühesten volkssprachlichen Vollübersetzungen der Bibel. Sprachlich steht sie am Übergang von Mittelhochdeutsch zu Frühneuhochdeutsch: bairisch-österreichisch, mit deutlich böhmischem Kolorit. Das Produkt einer höfischen Werkstatt für Wenzels zweisprachige Kanzlei — und das wird noch eine Rolle spielen.

**150.000 blinde Wörter**

Nach der strukturellen TEI-Konversion der *WB-DEA*-Quelldaten lagen rund 150.000 Wörter vor — formal korrekt, aber ohne eine einzige semantische Annotation. Jedes fehlende Attribut bedeutet eine fehlende Funktion: Lemma-Referenzen machen Tokens lemmasuchbar, Wortartmarkierungen ermöglichen grammatische Filterung, Bedeutungsreferenzen öffnen die Konzeptnavigation. Ohne sie ist die *Wenzelsbibel* im Korpus vorhanden, aber blind: Kein Suchergebnis verweist auf sie, keine Lemmafrequenz wird aus ihr berechnet, kein semantisches Netz schließt sie ein.

Die Aufgabe war keine singuläre Fleißarbeit. Rund ein Drittel der 670 *MHDBDB*-Texte verfügt noch nicht über Bedeutungsannotationen — die *Wenzelsbibel* ist der erste kontrollierte Testfall für eine Pipeline, die diese Lücke systematisch schließen soll.

**Die Pipeline: Automatisierung an den Grenzen des Machbaren**

Die Annotationspipeline folgt einem einfachen Prinzip: das Sprachmodell nicht als Orakel einsetzen, sondern als Unterstützung an den Ambiguitätsgrenzen. Automatisierung so weit wie möglich, LLM-Assistenz wo nötig, menschliches Review an den Unsicherheitsstellen. Alle Entscheidungen laufen durch eine versionierbare Zwischenschicht — kein Schritt schreibt direkt ins Dokument.

Phase 1, der Lexikonabgleich, löst rund 60 % der Tokens direkt auf. Die verbleibenden 72.000 Fälle gehen in Phase 1b: Das Sprachmodell liest Kontextfenster und schlägt Lemmata mit Konfidenzangabe vor; niedrig-konfidente Entscheidungen kommen zum menschlichen Review. Das Ergebnis: 95,3 % Lemma-Abdeckung. Phase 2, das POS-Tagging, nutzt denselben Mechanismus: Lemmata mit eindeutigem Wortart-Eintrag werden direkt zugewiesen, mehrdeutige Fälle — *daz* als Artikel oder Konjunktion, *ein* als Artikel oder Zahlwort — gehen in den Review-Workflow. Auch hier: 95,3 % Abdeckung.

**Die böhmischen Überraschungen**

Was kein Standard-MHG-Text hätte: Die *Wenzelsbibel* brachte drei Annotationsprobleme mit, die aus ihrer Entstehungsgeschichte an der kulturellen Schnittstelle zwischen deutschem und böhmischem Sprachraum folgen.

Böhmische Schreibkonventionen bedeuteten, dass Wörter wie *czeit*, *vnd*, *vortilgen* in keinem Wörterbuch unter dieser Form stehen — obwohl sie triviale mittelhochdeutsche Wörter sind. Die Normalisierungslogik der Pipeline musste um systematische Substitutionsmuster erweitert werden.

Noch überraschender: In den Exodus- und Numeri-Abschnitten tauchen altböhmische Interlinearglossen auf — Notizen aus dem Scriptorium für Wenzels zweisprachige Hofkanzlei. Sie sind keine mittelhochdeutschen Lexeme. Die Lösung war pragmatisch: ein neues Lemma als Platzhalter für altböhmisches Paratextmaterial. Insgesamt entstanden vier neue Lexikoneinträge im Zuge des Projekts, darunter *scot* (Schekel, böhmische Münzeinheit) und *weise* im Sinne von Waise — zu unterscheiden von *weise* als Adjektiv für klug.

Diese Probleme waren im Vorfeld nicht sichtbar. Das ist charakteristisch für historische Handschriften: Die wirklichen philologischen Entscheidungen entstehen beim Kontakt mit dem konkreten Dokument, nicht beim Lesen der Forschungsliteratur darüber.

**Was die *Wenzelsbibel* jetzt kann**

Seit Mai 2026 ist die *Wenzelsbibel* als Sigle WZB in der *MHDBDB* zugänglich: lemmasuchbar über 142.185 annotierte Tokens, mit Volltextanzeige und Lemma-Highlighting in der Leseansicht, eingebunden in das Normdatennetz der Mittelalterforschung (GND, Wikidata, Handschriftencensus).[^1] Ein Text, der in keiner computationellen Korpusressource lemmasuchbar war, ist jetzt vollwertiger Teilnehmer im semantischen Suchnetz über das mittelhochdeutsche Schrifttum.

Was das Projekt dabei gezeigt hat: Infrastruktur-Interoperabilität ist lösbar — aber sie erfordert philologische Entscheidungen, nicht nur technische Transformation. Welches Format hat ein „Wort" in *WB-DEA*? Was ist ein „Lemma" in der *MHDBDB*? Diese Fragen haben keine technische Antwort; sie sind editorische Entscheidungen, die getroffen und dokumentiert werden müssen. Und: Residuale Ambiguität ist keine Niederlage. Die rund 5 % unaufgelösten Tokens benennen korrekt, wo automatische Annotation an ihre Grenze stößt — das ist eine wissenschaftliche Aussage.

**Der offene Horizont: Phase 3**

Phase 3 — die Bedeutungsdisambiguierung — ist noch nicht abgeschlossen. Sie ist gleichzeitig Infrastrukturarbeit und empirisches Testbett einer laufenden Dissertation über LLM-gestützte Word Sense Disambiguation in historischen Sprachstufen. Die Baseline: Den häufigsten Sinn pro Lemma auf alle Vorkommen anzuwenden ergibt eine gewichtete Genauigkeit von 66,7 %. Das ist die Hürde. Nach sechs Bulk-Batches liegt die Bedeutungsabdeckung bei 76,2 % — die hochambigen Hochfrequenzlemmata (*in*, *haben*, *werden*) warten noch auf token-genaue Entscheidungen.

Die eigentlich interessante Frage bleibt offen: Schlägt die Pipeline die Mehrheitssinn-Baseline von 66,7 %? Und falls ja — unter welchen Bedingungen, für welche Wortarten, bei welchem Polysemiegrad? Das ist die Dissertation.

---

*Alle angegebenen Links wurden am 26. Mai 2026 geprüft.*

[^1]: *MHDBDB — Mittelhochdeutsche Begriffsdatenbank*, Salzburg: Paris Lodron Universität Salzburg, 1995– , https://mhdbdb.sbg.ac.at. Das Miniprojekt wurde im Rahmen von CLARIAH-AT gefördert. Kontakt: mhdbdb@plus.ac.at
