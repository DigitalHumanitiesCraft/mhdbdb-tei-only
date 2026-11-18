Ergebnis des Laufs vom 2026-11-18 nach `docs/playbooks/VORPRUEFUNG.md`, auf dem Stand von #44 aus dem Lauf `issue-matrix.yml` vom 2026-11-17T15:17:51Z: 27 von 38 Fragen geprüft, 11 jünger als 14 Tage, 0 schon vorgeprüft.

Herkunft der Zahlen in dieser Zeile: `gh api repos/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44 --jq .body`, Abschnitt „Für Katharina“ zwischen den PERSONEN-Markern: 38 Zeilen mit der Art `Entscheiden`, davon 27 mit `seit` vor dem 2026-11-04, also mehr als 14 Tage vor dem Laufdatum (die Zeilen vom 04.11. an zählen nicht). Datum des Stands: `gh api "repos/DigitalHumanitiesCraft/mhdbdb-tei-only/actions/workflows/issue-matrix.yml/runs?per_page=1" --jq '.workflow_runs[0].created_at'`. Schon vorgeprüft: 0, unter `docs/playbooks/routinen/` liegt auf `main` noch keine `*-vorpruefung.md`. Offene PRs mit Kopf `claude/vorpruefung-*`: keine.

Gelaufen als monatliche Cloud-Routine. Geschrieben wurde nichts außer dieser Datei: kein Kommentar, kein Label, kein Ping. Jede Frage wurde gegen Thread, verlinkte Tickets, Commits, Daten und Doku gehalten; die tragenden Datenbefunde (DAR_38101080_4, die *gener*-Stellen der WZB, JT_43134000_4 und JT_48611000_4, LZT_2360_0, die 11 Tokens auf `lemma_74628`, die 104 Lücken in GWTK) hat der Lauf zusätzlich selbst mit `grep` über `tei/` nachgesehen.

**Ergebnis:** Keine Frage ist anderswo ganz entschieden oder ganz aus den Quellen beantwortbar (Klasse 1 und 2: je 0). 11 lassen sich enger fassen, weil Katharinas eigene frühere Antworten, eine ADR oder die Daten einen Teil schon klären. 16 bleiben offen, meist Freigaben, Prioritäten oder editorische Grundsatzentscheidungen.

## Übersicht

| Ticket | Klasse | Vorschlag |
|---|---|---|
| #255 | 4 | offen lassen, eine Methoden- und Encoding-Entscheidung. |
| #189 | 4 | offen lassen, eine Grundsatzentscheidung über Aufwand und Nutzen. |
| #371 | 3 | die 6 Ufer-Fälle als Bestätigung vorlegen, PRJ als lateinisch aus der Frage nehmen, die übrigen 10 und die 2 Neulemmata als Restfrage stehen lassen. |
| #359 | 3 | die Fragezeile auf die 14 verbliebenen Fälle umstellen. |
| #237 | 3 | die Fragezeile auf die zwei echten Gattungsoptionen umstellen, GND, Census und den fehlenden Zotero-Eintrag darunter weiterführen. |
| #370 | 4 | offen lassen, die Einzelfälle sind nach ihrer eigenen Vorgabe der echte Rest. Die Nebenfrage zur Abnahme von #522 ließe sich als `@juliahin Abnahme:` abtrennen. |
| #252 | 4 | offen lassen, eine Modellierungsentscheidung ohne Regel in Daten oder Doku. |
| #497 | 3 | Mauricius nach ADR-020 als entschieden behandeln (Split für die weltlichen Träger), nur Pilde bestätigen lassen. |
| #263 | 4 | offen lassen, wie weit eine Anfrage an ihren Kontakt reicht, ist ihr Ermessen; ERM als Präzedenz für den Mnd.-Punkt mitgeben. |
| #226 | 4 | offen lassen, Freigabe und Termin sind ihre Entscheidung. |
| #28 | 4 | offen lassen, die Frage ist schon so eng, wie die Quellen es erlauben. |
| #109 | 4 | offen lassen, den Stand des Antrags kennt nur Katharina. |
| #265 | 4 | offen lassen, eine editorische Richtungsentscheidung. Beim nächsten Kommentar erwähnen, dass die Antwort auch #264 entscheidet. |
| #492 | 3 | ī als erledigt melden, „Gen er“ mit den Parallelen als Bestätigung vorlegen, „salacha“ der Antwort in #526 folgen lassen. Die zwei *gener*-Stellen bei der Umsetzung mitprüfen. |
| #526 | 3 | die Frage auf die Wörter ohne jeden Lemma-Kandidaten eingrenzen; die rund 90 mit Kandidat brauchen keine Grundsatzfrage. |
| #542 | 3 | mit dem Akrostichon-Befund als Bestätigung stellen. |
| #470 | 4 | offen lassen, eine editorische Grundsatzentscheidung; die Doku-Regel löst sie nicht auf. |
| #579 | 4 | offen lassen, eine Prioritätsentscheidung. |
| #419 | 3 | auf die zwei offenen Punkte verkürzen. |
| #460 | 3 | JT_48611000_4 als Bestätigung (zu `lemma_3102` wie jagennes), AXU_18452_5 bleibt die eigentliche Frage. |
| #251 | 4 | offen lassen, eine Präferenz, die nur sie beantworten kann. |
| #462 | 3 | Kommentarort und Lesung als geklärt nennen; gefragt bleiben die Freigabe des neuen Lemmas und das Ziellemma für unpeweglich. |
| #461 | 4 | offen lassen. Eine Tendenz ist keine Entscheidung, und mit `sense_49690` gibt es eine Alternative zu einem neuen Sense. Beim nächsten Kommentar die drei Zweifelsfälle und die Alternative mitgeben. |
| #554 | 3 | Die Zählregel als durch den 16.10. entschieden zurückziehen und die Lemmatisierung als Ja/Nein-Frage stellen. |
| #58 | 4 | offen lassen, eine Gestaltungsentscheidung, die keine Quelle beantwortet. |
| #118 | 4 | offen lassen, eine fachliche Grundsatzentscheidung; die Spannung zu #81 beim nächsten Kommentar offenlegen. |
| #649 | 4 | offen lassen, eine Frage der Zuständigkeit, keine Quellenfrage. |

Zusammen: Klasse 1: 0, Klasse 2: 0, Klasse 3: 11, Klasse 4: 16, Summe 27.

**Zum Einsetzen der neuen Zeilen** (Klasse 3), Hinweis aus `CLAUDE.md` („Who is on turn“): Eine Frage wird nur dann oben auf unseren letzten Kommentar editiert, wenn der neuer ist als Katharinas letzte Antwort, sonst als neuer Kommentar gepostet. Bei allen 11 Fragen der Klasse 3 ist unser letzter Kommentar neuer als ihr letzter, oder sie hat im Thread nie geschrieben; die Zeile „Zeitpunkte“ nennt je Frage die Daten. Die neuen Zeilen haben samt Präfix 105 bis 139 Zeichen, bleiben also unter den 140, die `frage_text()` in `scripts/audit/build-issue-matrix.py` in ihre Liste übernimmt, und enthalten keins der Zeichen, die `frage_text()` streicht (Stern, Unterstrich, Backtick, Raute, spitze Klammer). Deshalb nennen sie Sigle und Stelle statt xml:ids.

## Klasse 1: anderswo entschieden

Keine.

## Klasse 2: aus den Quellen beantwortbar

Keine.

## Klasse 3: enger fassbar

### #371 (seit 2026-09-21)
- Frage heute: Wie sollen die 17 stat-Belege mit "OFFEN" und die zwei Fälle, die ein neues Lemma bräuchten, behandelt werden? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/371#issuecomment-5759587223))
- Klasse: 3
- Belege: Grundlage ist Katharinas Review-JSON vom [15.09.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/371#issuecomment-5677967283). Die nachgesehenen OFFEN-Tokens stehen in `tei/` noch ohne `@lemmaRef`, die zwei Neulemma-Fälle GAR_99470_6 und WVO_988600_5 eingeschlossen.
  - **6 Fälle** (ER_706600_3, ER_762600_3, GAR_34970_5, OVG_975200_3, TRM_1429_3, TRO_25465_4) tragen ihre eigene Notiz „neutrum NOM 5712“, dieselbe wie DAR_38101080_4, das heute als `lemmaRef="lexicon.xml#lemma_5712" pos="NOM"` in `tei/DAR.tei.xml` steht („uf daz stat geriten“). Der Kontext stützt in allen sechs „Ufer“: ER „ûz an daz stat gerunnen“ und „gât an daz stat stân / unde bitet si gân ûz ziu an den sant“; GAR „hin ueber fueren an daz stat“; OVG „nû was daz stat îses lære“; TRM „weinende siu fuoren über se . do siu das stat ergriffen“; TRO „gemachet über an daz stat“.
  - **1 Fall,** PRJ_1981120_1, ist lateinisch: „quia in ore duorum vel trium stat omne verbum“. Nach `docs/POS-TAGSET.md` §6.4 wird Fremdsprachliches über `@xml:lang` erfasst, nicht über Lemma und `@pos`.
  - **Echt offen** bleiben 10 Fälle und die 2 Neulemmata: zu den fünf HZU2-Fällen schreibt sie „das scheint österreichisch zu sein, das kann ich schlecht beurteilen“, zu BRW „muss nochmal bei hennig gucken“, zu DJEM „traue ich mir nicht zu“, zu MSG „ich habe keine ahnung“; DIO und FR1 haben keine Notiz.
- Vorschlag: die 6 Ufer-Fälle als Bestätigung vorlegen, PRJ als lateinisch aus der Frage nehmen, die übrigen 10 und die 2 Neulemmata als Restfrage stehen lassen.
- Neue Zeile: `@wachauer Frage: Dürfen die 6 offenen stat-Belege mit deiner Notiz „neutrum NOM 5712“ wie der Beleg in DAR auf stade (Ufer)?`
- Zeitpunkte: unser letzter Kommentar 2026-09-21 (Fragezeile am 09.10. ergänzt), Katharinas letzter 2026-09-15: auf unseren Kommentar editieren möglich.

### #359 (seit 2026-09-21)
- Frage heute: Wie entscheidest du die 17 Fälle auf der Borek-Prüfseite (3 Fehlannotationen, 5 fehlende Konzepte, 4 ohne Beleg, 5 offen)? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/359#issuecomment-5762460301))
- Klasse: 3
- Belege: Unser Kommentar vom [19.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/359#issuecomment-6263030014) hält fest, dass drei Fälle umgezogen sind: `gebeine` (Konzept fehlt) sowie `jaget` und `jagen` (unsicher) laufen nach Katharinas Antworten vom 15.10. in #461 und #460 weiter (Commits `bef17e9dc`, `7a11b4dd9`). Offen sind hier also 14. Ihre Grundsatzentscheidung zu den Körperteilen vom [16.09.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/359#issuecomment-5696100083) gilt; danach kam von ihr nichts. Die übrigen Fälle sind philologische Einzelentscheidungen ohne weitere Quelle.
- Vorschlag: die Fragezeile auf die 14 verbliebenen Fälle umstellen.
- Neue Zeile: `@wachauer Frage: Wie entscheidest du die 14 noch offenen Fälle der Borek-Prüfseite (gebeine und jaget laufen in eigenen Tickets weiter)?`
- Zeitpunkte: unser letzter Kommentar 2026-10-19, Katharinas letzter 2026-09-16: auf unseren Kommentar vom 19.10. editieren möglich.

### #237 (seit 2026-09-28)
- Frage heute: Welche Gattung soll der Werkeintrag der Wenzelslegende (WLK) tragen: Heiligenlegende (`genre_2292de8a`), die Hystoria nova de sancto Wenceslao (Geschichtsquellen) oder beides? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/237#issuecomment-5869061505))
- Klasse: 3
- Belege: Nach dem 23.09. hat Katharina nicht geantwortet; die Suche nach WLK findet nur #496 (gemergt, ohne Antwort von ihr) und #487. `work_WLK` in `authority-files/works.xml` trägt bis heute weder Genre-`ptr` noch `relatedItem`. Die „Hystoria nova“ ist keine Gattung: `grep -i "hystoria\|wencesla"` findet in `genres.xml` nichts, sie ist die lateinische Vorlage, also ein Werk. Zur Wahl stehen damit zwei Gattungen: Heiligenlegende, wie VTC (`work_572`, `genres.xml#genre_2292de8a`), oder die Chronik-Gattung nach dem Auftrag AA-3 („Genre analog PUC prüfen“), dem PUC (`work_577`, `genre_00bb7cc9`) folgt. Die Teilfrage GND/Wikidata und Handschriftencensus bleibt davon unberührt.
- Vorschlag: die Fragezeile auf die zwei echten Gattungsoptionen umstellen, GND, Census und den fehlenden Zotero-Eintrag darunter weiterführen.
- Neue Zeile: `@wachauer Frage: Soll der Werkeintrag WLK die Gattung Heiligenlegende tragen (wie VTC), die Chronik-Gattung von PUC oder beide?`
- Zeitpunkte: unser letzter Kommentar 2026-09-28 (Fragezeile am 09.10. ergänzt), Katharinas letzter 2026-09-23: editieren möglich.

### #497 (seit 2026-10-08)
- Frage heute: Pilde bleibt unverändert, und der Sense von Mauricius wird für die weltlichen Namensträger abgespalten oder bleibt? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/497#issuecomment-6059342406))
- Klasse: 3
- Belege: **Mauricius ist anderswo entschieden.** ADR-020 in `docs/DECISIONS.md` stützt sich auf Katharina in [#357, 14.09.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/357#issuecomment-5663752448): „Das gilt für alle Namen. Dass ein Namen mehrere Entitäten bezeichnet, ist ja normal.“ Die ADR folgert: „Each referent class gets its own sense … A lemma with one sense and two kinds of referent is the defect.“ `lemma_4028` hat heute einen einzigen Sense `sense_6331` (Konzepte 21012000, 23112500, 23123100, 24411100), weltliche Träger stehen in CR (etwa „mîn her maurîcius von craûn“) und REN V. 24216 („und sin bruoder muris von pilde“). **Pilde:** Katharinas Auflage vom [25.09.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/357#issuecomment-5829639204) war, vor einer Änderung Herkunft und Quellen zu prüfen; das RDF-Export-CSV hat schon alle vier Konzepte, und 350 Senses mit „Personennamen/Familiennamen“ tragen zusätzlich ein Ortskonzept, Pilde selbst eingerechnet. Das Namenregister bei Hübner (DTM 39) ist nicht geprüft.
- Vorschlag: Mauricius nach ADR-020 als entschieden behandeln (Split für die weltlichen Träger), nur Pilde bestätigen lassen.
- Neue Zeile: `@wachauer Frage: Bleibt Pilde (REN 24216) unverändert, also Ortskonzepte plus Personennamen wie bei 349 weiteren Senses?`
- Zeitpunkte: unser letzter Kommentar 2026-10-08 (Fragezeile am 09.10. ergänzt), von Katharina kein Kommentar in #497: editieren möglich.

### #492 (seit 2026-10-09)
- Frage heute: Wie sollen drei Split-Tokens der Wenzelsbibel lemmatisiert werden ("Gen er" in Lev 16,26, ī mit Makron, "salacha")? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/492#issuecomment-6085809023))
- Klasse: 3
- Belege:
  - **ī ist erledigt:** WZB_143vb_10_4 trägt `lemmaRef="lexicon.xml#lemma_3028" pos="PRP"`, gekommen mit #534 (siehe [#526, 07.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/526#issuecomment-6034297936)).
  - **„Gen er“:** In `tei/WZB.tei.xml` lautet die Stelle „her ouf dem alter Gen er / vor war der do hat gelasen den“ (WZB_116va_14/15), beide Tokens ohne `@lemmaRef`. Die WZB schreibt *jener* auch sonst mit g: „aber gener sach sie an swigende“ (WZB_21rb_22_0), „Ich wart gegeben meinem ampte wider vnd gener wart gehangen“ (WZB_42ra_17_3); die Vulgata ist nicht nachgeschlagen. Beide Parallelstellen hängen heute an `lemma_2122` *genern* (VRB), vermutlich eine Fehlannotation. `lemma_3114` *jener* ist in der WZB 20-mal belegt, alle als ADJ.
  - **„salacha“:** WZB_227ra_19_1b, „perge / vnd in salacha | vnd“, kein Lexikoneintrag. Die WZB annotiert Namen (169 `pos="NAM"`), ob neue Namenslemmata angelegt werden dürfen, ist dieselbe Grundsatzfrage wie in #526.
- Vorschlag: ī als erledigt melden, „Gen er“ mit den Parallelen als Bestätigung vorlegen, „salacha“ der Antwort in #526 folgen lassen. Die zwei *gener*-Stellen bei der Umsetzung mitprüfen.
- Neue Zeile: `@wachauer Frage: Dürfen wir „Gen er“ in der WZB (Lev 16,26) zu einem Wort gener (= jener) zusammenführen?`
- Zeitpunkte: unser letzter Kommentar 2026-10-09, von Katharina kein Kommentar im Thread: editieren möglich.

### #526 (seit 2026-10-09)
- Frage heute: Dürfen wir für Wenzelsbibel-Wörter, die das Lexikon nicht kennt, neue Lemmata anlegen, und mit welchem Mindestumfang? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/526#issuecomment-6085810550))
- Klasse: 3
- Belege: Laut [Kommentar vom 08.11.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/526#issuecomment-6722834261) gehören 10 von 10 Stichproben zu einem vorhandenen Lemma. `ingest/wzb/526-breve/lexikonluecken-kandidaten.csv` zählt 32 Zeilen „kandidat-eindeutig“, 58 „kandidat-mehrdeutig“, 19 „kein-kandidat“. Neue Lemmata kämen nur für einen kleinen Rest in Frage, dazu `etwenn̆` und `vngesow̆erteigtes` von Julias Prüfseite ([13.11.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/526#issuecomment-6860328132)) und „salacha“ aus #492. Katharina hat eine Untergrenze schon gesetzt, [#554, 16.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/554#issuecomment-6216557849): „Bei bestätigtem Fehlen kein unbelegtes Lemma anlegen“; in [#115 (29.05.)](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/115#issuecomment-4572895289) „das entscheide ich erst, wenn ich sehe, worum es sich … handelt“. Eine allgemeine Freigabe gibt es nicht.
- Vorschlag: die Frage auf die Wörter ohne jeden Lemma-Kandidaten eingrenzen; die rund 90 mit Kandidat brauchen keine Grundsatzfrage.
- Neue Zeile: `@wachauer Frage: Dürfen wir für WZB-Wörter ohne jedes passende Lemma (etwa vngesow̆erteigtes) ein Lemma mit Grundform und Wortart anlegen?`
- Zeitpunkte: unser letzter Kommentar 2026-11-13, Katharinas letzter 2026-10-08: auf unseren Kommentar vom 13.11. editieren.

### #542 (seit 2026-10-10)
- Frage heute: Ist die Zeile „das ist das a b c d e f etc“ am Anfang des Gedichts „alphabetischer liebesgruß“ in MR2 Verstext der Handschrift (dann bleibt sie annotiert) oder ein Hinweis des Herausgebers (dann Apparat, 7 Tokens würden entannotiert)? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/542#issuecomment-6094889873))
- Klasse: 3
- Belege: In `tei/MR2.tei.xml` steht V. 1 (`MR2_20155200001100_0` bis `_9`) ganz in `<supplied>`. Das Gedicht ist ein Abecedarius, dessen Alphabet erst mit V. 2 beginnt: „ach edeliu …“, V. 3 „by dir …“, V. 4 „cur haut …“, V. 5 „das sie …“, V. 6 „ein diener …“ bis V. 22 „xius …“, V. 23 „yetz …“, V. 24 „zart frow …“. V. 1 steht außerhalb des Akrostichons, beschreibt die Form und endet auf das lateinische „etc“: das spricht für einen Herausgeberhinweis. `<supplied>` allein entscheidet nichts, denn auch echte Versergänzungen stehen darin (V. 87). Ob die Zeile in der Handschrift steht, sagt nur die Edition, die nicht im Repo liegt.
- Vorschlag: mit dem Akrostichon-Befund als Bestätigung stellen.
- Neue Zeile: `@wachauer Frage: Ist „das ist das a b c d e f etc“ (MR2, V. 1) ein Herausgeberzusatz, da das Akrostichon a bis z erst mit V. 2 beginnt?`
- Zeitpunkte: unser letzter Kommentar 2026-10-10, von Katharina kein Kommentar im Thread: editieren möglich.

### #419 (seit 2026-10-16)
- Frage heute: Passt es für die Suche im Wörterbuch so, dass `*` für beliebig viele Zeichen (auch keines) steht, am Anfang, in der Mitte und am Ende stehen darf und gegen Kopfformen und Schreibformen geprüft wird, wobei ein Treffer nur über eine Schreibform diese Form in der Zeile mitzeigt? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/419#issuecomment-6209880102))
- Klasse: 3
- Belege: Am [13.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/419#issuecomment-6142474787) hat Katharina `*meise` und `am*` „mindestens“ gewünscht (führendes und abschließendes Sternchen), keinen ODER-Operator, und nur Formen, die das Muster erfüllen; „weitere Syntaxdetails sind … noch nicht entschieden“. Am [15.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/419#issuecomment-6189645860): zumindest im Wörterbuch einbauen. Von ihr nicht gedeckt sind nur das Sternchen in der Wortmitte und die Prüfung gegen Schreibformen.
- Vorschlag: auf die zwei offenen Punkte verkürzen.
- Neue Zeile: `@wachauer Frage: Darf das Wörterbuch-Sternchen auch mitten im Wort stehen und neben Kopfformen auch Schreibformen prüfen?`
- Zeitpunkte: unser letzter Kommentar 2026-10-16, Katharinas letzter 2026-10-15: editieren möglich.

### #460 (seit 2026-10-16)
- Frage heute: Gehören AXU_18452_5 und JT_48611000_4 mit dem längeren Kontext unten zum Verb jagen oder zum Nomen jagât? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/460#issuecomment-6212801872))
- Klasse: 3
- Belege: Zu JT_48611000_4 („andolt, der meister jagenes“): Katharina hat am [15.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/460#issuecomment-6195157283) die gleiche Form `JT_43134000_4` „der erste was er jagennes“ als „Verb“ entschieden; der Token steht heute auf `lemma_3102` (VRB). Zwei Verse später steht „den baten si do sagenes“ (`JT_48612000_4`, `lemma_5061` VRB). Zu AXU_18452_5 („die wârheit hie dem gelîche jaget :“) liefern die Quellen nichts Neues.
- Vorschlag: JT_48611000_4 als Bestätigung (zu `lemma_3102` wie jagennes), AXU_18452_5 bleibt die eigentliche Frage.
- Neue Zeile: `@wachauer Frage: Kommt jagenes (JT) wie jagennes zu jagen, und gehört jaget in AXU 18452 zum Verb jagen oder zum Nomen jagât?`
- Zeitpunkte: unser letzter Kommentar 2026-10-16, Katharinas letzter 2026-10-15: editieren möglich.

### #462 (seit 2026-10-18)
- Frage heute: Dürfen wir bei indelicius den Beleg "indeliciis" auf ein neues Lemma deliciae (in deliciis) umstellen, wohin gehört dein Kommentartext zu Ezechiel 28,13, und genügt bei unpeweglich der Token-`@pos` ADJ? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/462#issuecomment-6249713059))
- Klasse: 3
- Belege: **Kommentarort:** Ihr Text vom [16.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/462#issuecomment-6217024833) zitiert „In deliciis paradisi Dei fuisti“ (Ez 28,13). Das einzige Vorkommen im Korpus ist `ADP_104900_10` in `tei/ADP.tei.xml`: „tu signaculum similitudinis plenus sapientia . et perfectus decore . indeliciis paradisi dei fuisti“. Der Kommentar gehört also zu diesem Beleg, und ihr Text liest ihn selbst als „in deliciis“ („In den Wonnen“). **unpeweglich:** `lexicon.xml` führt `lemma_74628` `unbewëgelich` (ADJ), den MWB-Ansatz aus unserem Kommentar, mit 11 ADJ-Tokens. `LZT_2360_0` steht aber auf `lemma_24478` enbewegen (`pos="NEG VRB"`), wo schon 9 weitere Adjektivformen liegen (`unbewegelich` ×7, `vnbeweglich` ×2). Die Wahl ist also „ADJ auf enbewegen wie die 9“ oder „Umhängen auf unbewëgelich“.
- Vorschlag: Kommentarort und Lesung als geklärt nennen; gefragt bleiben die Freigabe des neuen Lemmas und das Ziellemma für unpeweglich.
- Neue Zeile: `@wachauer Frage: Neues Lemma deliciae für indeliciis (ADP) samt deinem Ez-28,13-Kommentar, und unpeweglich zu unbewëgelich umhängen?`
- Zeitpunkte: unser letzter Kommentar 2026-10-18, Katharinas letzter 2026-10-16: editieren möglich.

### #554 (seit 2026-10-18)
- Frage heute: Wie sollen die vier unklaren trûbe-Belege (HIS_98_2, WZB_79rb_15_5, FR1_2007050_8, ROT_19160_2) annotiert werden, und ist es für die ersetzten Trefferzahlen in Ordnung, dass nur Wörter mit Lemma-Annotation gezählt sind? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/554#issuecomment-6250915880))
- Klasse: 3
- Belege: Die zweite Teilfrage hat Katharina am [16.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/554#issuecomment-6216557849), Punkt 4, beantwortet: „Sie durch heutige Lemmazahlen zu ersetzen, ist ausdrücklich in Ordnung … die aktuellen Zahlen sind am heutigen Korpus zu ermitteln.“ Die erste ist offen. Alle 4 Tokens stehen weiter auf `lemma_15282` (trûbe, Traube), `sense_25272`, `pos="NOM"`. Kontext: HIS_98_2 „ein vakeln hecht so schone quam daz di [[trube]] gar benam di sich e ob dem schiffe truc“; WZB_79rb_15_5 „rufte im vnser herre ous der mitte der [[trube]] Aber die gestalt der eren“; FR1_2007050_8 „wer gap verkoufter joseph heil der [[trüben]] sel“; ROT_19160_2 „manige werlt wunne vnde ovch [[trube]] dar vnder“. `trüebe` (`lemma_6251`) führt nur ADJ/ADV/GRA, kein Substantiv. FR1 liest sich attributiv, HIS, WZB und ROT substantivisch; ein Lexikonnachweis für ein Substantiv (etwa Lexer) ist nicht geprüft.
- Vorschlag: Die Zählregel als durch den 16.10. entschieden zurückziehen und die Lemmatisierung als Ja/Nein-Frage stellen.
- Neue Zeile: `@wachauer Frage: Sollen die unklaren trûbe-Belege in HIS, WZB und ROT ein neues Substantiv trüebe bekommen, der in FR1 das Adjektiv trüebe?`
- Zeitpunkte: unser letzter Kommentar 2026-11-04, Katharinas letzter 2026-10-16: editieren möglich.

## Klasse 4: bleibt offen

### #255 (seit 2026-08-31)
- Frage heute: Sollen Keyness und Wortfrequenz die Parallelüberlieferung herausrechnen, die Hapax-Suche sie aber mitzählen, wie in der Liste empfohlen? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/255#issuecomment-5478549085)), gerichtet an Katharina und Julia
- Klasse: 4
- Belege: Katharinas einzige Antwort ([30.07.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/255#issuecomment-5130393168)) legt nur den Schwerpunkt fest („in einer Belegsuche alle Zeugen auffindbar machen“) und bestellt die Liste. Eine Entscheidung zu Keyness und Frequenz steht nirgends: Commits mit #255 betreffen #380 (Messskript), #281/#304 (CONTRACTS §H) und Doku. `docs/CONTRACTS.md` nennt #255 weiter als „Open dependency“. Auch die Voraussetzung ist offen: alle 51 `<div type="parallel">` in `tei/` tragen nur `@n`, kein `@subtype`.
- Vorschlag: offen lassen, eine Methoden- und Encoding-Entscheidung.
- Zeitpunkte: unser letzter Kommentar 2026-08-31 (Fragezeile am 09.10. ergänzt), Katharinas letzter 2026-07-30.

### #189 (seit 2026-09-06)
- Frage heute: Sollen die hochfrequenten Funktionswort-Homographen (in, ir, er, sî, man, sîn, was; rund 1,85 Mio. Tokens ohne Lemma) überhaupt nachannotiert werden? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/189#issuecomment-5561288742))
- Klasse: 4
- Belege: Katharinas Kommentar vom 30.07. ist ein Datenhinweis zum Trierer Dump, keine Antwort. In #216 und #198 sagt sie nichts zur Funktionswortschicht; die Suche nach „Funktionswort“ in Issues und PRs findet keine Entscheidung. In `docs/` erscheint das Thema nur als Filter (`FUNCTION_WORD_POS`, FEATURES.md, CONTRACTS.md §H) und als offene Frage in `journal-archive.md`.
- Vorschlag: offen lassen, eine Grundsatzentscheidung über Aufwand und Nutzen.
- Zeitpunkte: unser letzter Kommentar 2026-09-06 (Fragezeile am 09.10. ergänzt), Katharinas letzter 2026-07-30.

### #370 (seit 2026-10-02)
- Frage heute: Wie entscheidest du die 29 Schreibung-Lemma-Paare der WZB auf der Prüfseite (eigenen Variantentyp anlegen oder nicht)? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/370#issuecomment-5954406833))
- Klasse: 4
- Belege: Katharina hat am [14.09.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/370#issuecomment-5663707066) verlangt, dass nur Fälle zu ihr kommen, die nach Kontext-, Varianten- und Wörterbuchprüfung „weiterhin ernsthaft mehrdeutig“ sind. Die 29 sind genau dieser Rest aus der Vorprüfung #516 (ANLEGEN 412, NICHT_ANLEGEN 43, PRUEFSEITE 29). Die Prüfseite liegt unter `ingest/wzb/370-corresp/pruefseite-370.html`; ein JSON-Rücklauf liegt weder im Ordner noch im Thread.
- Vorschlag: offen lassen, die Einzelfälle sind nach ihrer eigenen Vorgabe der echte Rest. Die Nebenfrage zur Abnahme von #522 ließe sich als `@juliahin Abnahme:` abtrennen.
- Zeitpunkte: unser letzter Kommentar 2026-10-02 (Fragezeile am 09.10. ergänzt), Katharinas letzter 2026-09-14.

### #252 (seit 2026-10-06)
- Frage heute: Wie sollen die Lücken kodiert werden, die der Herausgeber Koppitz im Göttweiger Trojanerkrieg (GWTK) ansetzt, die Handschrift aber nicht zeigt: `reason="editorial"`, unverändert lassen oder wie die übrigen `reason="lost"`? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/252#issuecomment-6018807202))
- Klasse: 4
- Belege: Der Editionsbefund ist erhoben: laut Apparat zeigt keine der 104 GWTK-Lücken eine Handschriftenlücke. `GWTK.tei.xml` hat 104 `<gap reason="lost"/>`, korpusweit tragen alle `<gap>` den Wert `lost`; einen Präzedenzfall für einen anderen Wert gibt es nicht. Das Schema lässt `@reason` frei (`schema/mhdbdb.rnc`), `docs/TEI-MODEL.md` §6.5a trennt Herausgeber- und Handschriftenlücke nicht. Katharinas letzte Vorgabe vom 02.10.: „Editionsgrundlage prüfen …, bis dahin unverändert lassen.“
- Vorschlag: offen lassen, eine Modellierungsentscheidung ohne Regel in Daten oder Doku.
- Zeitpunkte: unser letzter Kommentar 2026-10-06 (Fragezeile am 09.10. ergänzt), Katharinas letzter 2026-10-02.

### #263 (seit 2026-10-08)
- Frage heute: Soll die Wunschliste an Thomas Gloning nur die Koch-, Diät- und Weinliteratur umfassen oder auch seine E-Texte für #266? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/263#issuecomment-6060702607))
- Klasse: 4
- Belege: Weder in #263 noch in #266, #376 oder #537 hat Katharina nach dem 08.10. etwas dazu gesagt. Ihr Kommentar vom 08.10. ordnet die E-Texte „mit dem Vorgang … #266 abzugleichen“ zu, „durch ihre Nennung hier noch nicht zur Aufnahme beschlossen“. Die Grenze „vor 1600“ (`docs/RESEARCH.md`) trennt die Listen nicht. Zum Nebenpunkt Mittelniederdeutsch: mit `ERM` („Koninc Ermenrîkes Dôt: Ein Niederdeutsches Lied“, `works.xml`) steht schon ein niederdeutscher Text im Korpus.
- Vorschlag: offen lassen, wie weit eine Anfrage an ihren Kontakt reicht, ist ihr Ermessen; ERM als Präzedenz für den Mnd.-Punkt mitgeben.
- Zeitpunkte: unser letzter Kommentar 2026-10-08 13:15 (Fragezeile am 09.10. ergänzt), Katharinas letzter 2026-10-08 11:56.

### #226 (seit 2026-10-09)
- Frage heute: Gibst du den Blogbeitrag mit den vier Änderungsvorschlägen von Christian frei, und für welchen Termin? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/226#issuecomment-6080073547))
- Klasse: 4
- Belege: Katharina hat im Thread nie kommentiert (sie hat den Body geschrieben). `hilfe-publikationen.html` führt den Beitrag nicht, er ist dem Repo nach nicht erschienen.
- Vorschlag: offen lassen, Freigabe und Termin sind ihre Entscheidung.
- Zeitpunkte: unser letzter Kommentar 2026-10-09, von Katharina kein Kommentar im Thread.

### #28 (seit 2026-10-09)
- Frage heute: Gilt "UR nein" aus deiner Entscheidung vom 29.07. auch für Schicht B, also darf die Herkunftsangabe im Lexikon auch Kirchenwortschatz wie bischof, engel, missa tragen? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/28#issuecomment-6080723878))
- Klasse: 4
- Belege: Ihre Entscheidung vom [29.07.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/28#issuecomment-5117959116) fasst „ZITAT ja, UR nein“ als Regel für die Auszeichnung („Ausgezeichnet wird nur, was 1. keine mhd. Flexion trägt …“), also für Schicht A. Zu INT schreibt sie: „Die Suche [wird] aus beiden Schichten gespeist … `tjoste` erscheint bei ‚Französisch‘ so oder so.“ Der Phasenplan `docs/features/FREMDSPRACHEN-PHASENPLAN-28.md` hält fest: „Auszeichnungsregel für `@xml:lang`: … INT und UR gar nicht.“ Das betrifft Schicht A und INT; zu UR in Schicht B, also genau dem, was gefragt ist, sagen die Quellen nichts.
- Vorschlag: offen lassen, die Frage ist schon so eng, wie die Quellen es erlauben.
- Zeitpunkte: unser letzter Kommentar 2026-11-08 (Statusnotiz), Katharinas letzter 2026-09-17.

### #109 (seit 2026-10-09)
- Frage heute: Ist der FWF-Antrag eingereicht, und braucht er von uns noch technische Klarstellungen? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/109#issuecomment-6085793747))
- Klasse: 4
- Belege: Nach der Frage steht im Thread nichts mehr. Die Suche nach „FWF“ in den Issues findet keine Antwort zum Antragsstand (#139 nennt FWF als Förderhinweis von CoReMA, #271 verweist nur auf #109). `git log origin/main -E --grep="#109([^0-9]|$)"` gibt nichts aus. `docs/ROADMAP.md` führt die Frage als offen, `docs/journal-archive.md` nur „wartet auf @wachauer-Antragstext“.
- Vorschlag: offen lassen, den Stand des Antrags kennt nur Katharina.
- Zeitpunkte: unser letzter Kommentar 2026-10-09, von Katharina kein Kommentar im Thread.

### #265 (seit 2026-10-09)
- Frage heute: Soll die vollständige Transkription von Reinmar von Zweter nach Roethe 1887 ins Korpus (Neuaufnahme mit Annotation), oder wartet ihr auf eine neuere Edition? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/265#issuecomment-6085800786))
- Klasse: 4
- Belege: Katharina hat am 21.10. in [#537](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/537#issuecomment-6322268588) die Reihenfolge für „Demnächst im Korpus“ festgelegt („#139 … #147 … #651 … #141 …, dann ohne Q die anderen“), zu Roethe oder Altausgaben dort nichts. `data/demnaechst-zeitplan.json` führt #265 unter `nicht_freigegeben` mit dem Grund „Frage an KZW vom 09.10.2026 (Roethe 1887 oder neuere Edition) offen“. #264 hängt laut seinem Body an dieser Entscheidung. Reinmar fehlt in `works.xml` und `persons.xml`.
- Vorschlag: offen lassen, eine editorische Richtungsentscheidung. Beim nächsten Kommentar erwähnen, dass die Antwort auch #264 entscheidet.
- Zeitpunkte: unser letzter Kommentar 2026-10-09, von Katharina kein Kommentar im Thread.

### #470 (seit 2026-10-10)
- Frage heute: Sollen römische Kapitelzahlen, die am Anfang eines Verses stehen (etwa „ii . nû wart ein“ in OVG oder „ii âventiure von sîvride“ in NLC), wie Randzählungen aus dem Text genommen werden, oder bleiben sie als Wort im Vers? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/470#issuecomment-6094970174))
- Klasse: 4
- Belege: Im Thread hat nur Christian geschrieben. Die Suche nach „Kapitelzahlen“ findet nur #390 (WZB) ohne Regel dazu; kein Commit nennt #470. `docs/DATA-MODEL.md` widerspricht sich: römische Zahlen im Textfluss bleiben, Randzählungen gehen, und die Randzählung wird am eigenen xml:id-Block erkannt, den diese Kapitelzahlen nicht haben.
- Vorschlag: offen lassen, eine editorische Grundsatzentscheidung; die Doku-Regel löst sie nicht auf.
- Zeitpunkte: unser letzter Kommentar 2026-10-10, von Katharina kein Kommentar im Thread.

### #579 (seit 2026-10-16)
- Frage heute: Soll als Erstes die Stellenangabe in den Treffern der Multi-Lemma-Suche eindeutig gemacht werden (Arbeitspaket A unten)? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/579#issuecomment-6209867949))
- Klasse: 4
- Belege: Katharina schrieb zuletzt am 12.10. und 15.10. (Ort, Präzisierung durch Klaus), nicht zur Reihenfolge. Christian am 17.11.: „Die offene Frage an @wachauer vom 16.10. (Paket A zuerst?) ist davon nicht berührt.“ Paket A ist nicht umgesetzt (`formatLineRef` in `assets/js/search/kwic-service.js` gibt weiter nur `V. n`/`Z. n`/`S. n` aus).
- Vorschlag: offen lassen, eine Prioritätsentscheidung.
- Zeitpunkte: unser letzter Kommentar 2026-11-17, Katharinas letzter 2026-10-15.

### #251 (seit 2026-10-18)
- Frage heute: Darf die offene Zählerfrage vom 30.07. ("Schreibformen" statt "Lemmata", wenn gleich geschriebene Lemmata wie `sal` gemeinsam schalten) entfallen, solange sie dich im Alltag nicht stört? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/251#issuecomment-6249505277))
- Klasse: 4
- Belege: Katharina schrieb zuletzt am 08.09., zur Zählerfrage nie. Julias Rückmeldung vom 16.10. betrifft die Anzeige, nicht den Zähler. `componentPicked` in `playground/js/ui/authority/lemma-explorer.js` führt weiter Schreibformen, nicht Lemma-IDs.
- Vorschlag: offen lassen, eine Präferenz, die nur sie beantworten kann.
- Zeitpunkte: unser letzter Kommentar 2026-10-18, Katharinas letzter 2026-09-08.

### #461 (seit 2026-10-18)
- Frage heute: Sollen wir für die lebenden Gebeine eine eigene Bedeutung an `lemma_1958` anlegen und die 12 sicheren (plus 3 zweifelhafte) Belege von `sense_3004` dorthin umhängen, wie du es vermutet hast? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/461#issuecomment-6249713487))
- Klasse: 4
- Belege: Katharina hat vor der Frage eine Tendenz geäußert, unter der Bedingung einer Messung: „Du solltest erst messen … Ich tendiere dazu, eine weitere Bedeutung für die lebenden Gebeine anzulegen und diese umzuhängen“ ([16.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/461#issuecomment-6216809576)). Die Messung liegt vor (12 lebend, 3 mit Zweifel, `ingest/review/461-gebeine/sense3004-lebend.tsv`), entschieden hat sie danach nichts; unsere Statusnotiz vom [08.11.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/461#issuecomment-6724797893) sagt selbst: „Die Frage vom 18.10. (eigener Sense für die lebenden Gebeine?) bleibt offen.“ Die 2 Ochsen sind seit #688 erledigt (Commit `eb82b96`). Ihre Regel vom 15.10. („bei unklaren Gebeinen an die menschlichen“) entscheidet Mensch gegen Tier, nicht lebend gegen tot. Die 3 Zweifelsfälle aus der TSV: `HTR_214570_5` „die fleisch do wâren und [[gebein]] / die sint nu holz erde und stein“; `JEW_2330900000_1` „die ammen man ûf ein rat bant / ir [[gebein]] hiez man zerstôzen“; `ROL_3841_3` „wir treten si in den graben / daz ir unraine [[gebaine]] / daz ir lebentic nehaine“. Nebenbefund: `sense_49690` in `lexicon.xml` trägt nur `concept_21030000`, ohne Tod-Konzept, und wäre eine Alternative zu einem neuen Sense.
- Vorschlag: offen lassen. Eine Tendenz ist keine Entscheidung, und mit `sense_49690` gibt es eine Alternative zu einem neuen Sense. Beim nächsten Kommentar die drei Zweifelsfälle und die Alternative mitgeben.
- Zeitpunkte: unser letzter Kommentar 2026-11-08, Katharinas letzter 2026-10-16.

### #58 (seit 2026-10-18)
- Frage heute: Soll der Knopf „Gesamten Text öffnen“ im Kopf der Trefferkarte bleiben, oder lieber in eine eigene Zeile darunter? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/58#issuecomment-6253011809))
- Klasse: 4
- Belege: Julia hat danach nur die Abnahme bestätigt („Ja, das funktioniert perfekt“, [19.10.](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/58#issuecomment-6266653672)), nichts zur Position. Der Knopf steht weiter im Kartenkopf (`playground/js/ui/core/ui-helpers.js:328`).
- Vorschlag: offen lassen, eine Gestaltungsentscheidung, die keine Quelle beantwortet.
- Zeitpunkte: unser letzter Kommentar 2026-10-19, Katharinas letzter 2026-10-12.

### #118 (seit 2026-10-21)
- Frage heute: Sind die Schwellen 1350/1450 für die Zuordnung Mittelhochdeutsch/Frühneuhochdeutsch philologisch tragfähig, und welche Quelle gilt, wenn sich Verfasserlexikon, Edition und Handschriftencensus bei Datierung oder Raum widersprechen? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/118#issuecomment-6315624072))
- Klasse: 4
- Belege: Keine Entscheidung anderswo (Suchen nach `1350 1450`, `Quellenhierarchie`, `Verfasserlexikon`). `docs/RESEARCH.md` nennt für das Mittelhochdeutsche „Approximately 1050-1350“, `docs/TEI-MODEL.md` „ca. 1050-1350“; für 1450 steht nichts. Die Korpusgrenze „vor 1600“ (#263) betrifft den Umfang, nicht die Sprachstufe. Katharina schrieb in [#81 (08.05.)](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/81#issuecomment-4405607970): „Solange es keinen ISO-Code für Early Modern German … gibt, bleibt uns eh nur gmh als TEI-konformste Lösung.“ Das steht in Spannung zur technischen Festlegung `de-x-fnhd` vom 21.10.
- Vorschlag: offen lassen, eine fachliche Grundsatzentscheidung; die Spannung zu #81 beim nächsten Kommentar offenlegen.
- Zeitpunkte: unser letzter Kommentar 2026-10-21, von Katharina kein Kommentar im Thread.

### #649 (seit 2026-11-03)
- Frage heute: Trägst du die Erläuterung zu HZ als Notiz am Zotero-Eintrag Schröder 1970 (CGXT3NQ6) ein und ersetzt dabei die alte Notiz „Heinrich von Kempten …“, damit der nächste Sync sie in works.xml und den HZ-Header bringt? ([Kommentar](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/649#issuecomment-6613230621))
- Klasse: 4
- Belege: Die alte Notiz steht unverändert in `tei/HZ.tei.xml` und `authority-files/works.xml`; kein Commit nennt #649. Es geht darum, wer eine externe Zotero-Änderung vornimmt.
- Vorschlag: offen lassen, eine Frage der Zuständigkeit, keine Quellenfrage.
- Zeitpunkte: unser letzter Kommentar 2026-11-03, von Katharina kein Kommentar im Thread.
