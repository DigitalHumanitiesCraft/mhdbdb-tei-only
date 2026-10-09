# Mur bei Murstetten (#228)

Recherchepfad zu der Frage, die @wachauer am 25.09.2026 in #228 gestellt und am 01.10. präzisiert hat: Ist `lemma_66692` *Mur* (NAM, Gewässername) als Bestandteil von `lemma_66691` *Murstetten* fachlich richtig? Der Vorschlag steht als Kommentar in #228 (https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/228#issuecomment-5952554439). Beim Schreiben dieser Notiz war nichts in `authority-files/` geändert; die Streichung kam nach KZWs Entscheidung vom 09.10.2026 (unten).

## Belege (am TEI gelesen)

Drei Stellen in `tei/HZU2.tei.xml`, alle Herzogenburger Urkunden und alle derselbe Ort in Niederösterreich:

| Wort-ID | Datum | Kontext |
|---|---|---|
| `HZU2_10213390312001_10` | 12.03.1339 | "ich hertweich der lochler vnd ich ofmey sein hausfrowe von **mvrresteten** veriehen" |
| `HZU2_22813920222007_3` | 22.02.1392 | "daz do ierleich dient den tanpruggner ze **murstetten** vier phenning" |
| `HZU2_23213960410017_18` | 10.04.1396 | "ich vorgenanter hanns tanpruger von **mursteten** vnd daniel mein brueder" |

Das Datum steht in den Urkundenköpfen (`<note type="year">`, `<note type="date">` der Urkunden 102, 228, 232) und stimmt mit dem Muster der Wort-ID überein. Die Belege sagen über die Herkunft des Namens nichts.

## Quellen zur Deutung

- **Gelesen am Original:** Otto Friedrich Winter, *Antike Baureste als Element der Toponymie in Niederösterreich*, Jahrbuch für Landeskunde von Niederösterreich 54/55, S. 349-361, PDF-Seite 5 = Druckseite 353 (https://www.zobodat.at/pdf/Jb-Landeskde-Niederoesterreich_54-55_0349-0361.pdf). Winter nennt Murstetten (nach seiner Angabe Gemeinde Weißenkirchen an der Perschling, 1176/82 *de Murristetin*) und gibt **Schusters** Deutung wieder: *-stetten* mit einem vermutlich slawischen Personennamen als Bestimmungswort. Der Zusatz "falls sich dies nicht verifizieren ließe, stünde einer Einbeziehung in den Kreis der Mauer-Orte nichts im Wege" ist **Winters eigener Satz**, kein Zitat aus Schuster. Von der Mur ist im ganzen Aufsatz nicht die Rede.
- **Nur über Winter bekannt, nicht geöffnet:** "Schuster" nach Winters Anm. 1 und 23, Eintrag M 317; Handbuch der historischen Stätten (Anm. 23, S. 432); Lechner, Siedlungsgeschichte (S. 332). Winter hat 1990 die einschlägigen Artikel einer damals noch nicht erschienenen Ergänzung zum Historischen Ortsnamenbuch von Niederösterreich benutzt (Bearbeiterin Elisabeth Schuster, nach seiner Angabe "weit gediehen"); einen Titel nennt er nicht.
- **Gesehen, ohne Deutung:** de.wikipedia.org/wiki/Murstetten (Lage, Geschichte, keine Namensdeutung; nennt die Gemeinde Perschling).

## Was offen ist

- Schuster am Original prüfen (Eintrag M 317). Winter hat ein Manuskript benutzt; die gedruckte Fassung kann abweichen.
- `lemma_33528` *Mûrouwe* (Murau) behält `Mur`; die Deutung des Namens Murau ist hier nicht geprüft.

## Entschieden

- @wachauer am 09.10.2026 („1: ja“ in #228): `Mur` ist aus der Etymologie von `lemma_66691` gestrichen, kein Ersatzziel (Authority-Index 1.9.21).
