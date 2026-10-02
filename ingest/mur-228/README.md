# Mur bei Murstetten (#228)

Recherchepfad zu der Frage, die @wachauer am 01.10.2026 in #228 gestellt hat: Ist `lemma_66692` *Mur* (NAM, Gewässername) als Bestandteil von `lemma_66691` *Murstetten* fachlich richtig? Der Vorschlag steht als Kommentar in #228 (https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/228#issuecomment-5952554439). Geändert ist nichts in `authority-files/`.

## Belege (am TEI gelesen)

Drei Stellen in `tei/HZU2.tei.xml`, alle Herzogenburger Urkunden und alle derselbe Ort in Niederösterreich:

| Wort-ID | Datum (aus der ID) | Kontext |
|---|---|---|
| `HZU2_10213390312001_10` | 12.03.1339 | "ich hertweich der lochler vnd ich ofmey sein hausfrowe von **mvrresteten** veriehen" |
| `HZU2_22813920222007_3` | 22.02.1392 | "daz do ierleich dient den tanpruggner ze **murstetten** vier phenning" |
| `HZU2_23213960410017_18` | 10.04.1396 | "ich vorgenanter hanns tanpruger von **mursteten** vnd daniel mein brueder" |

Das Datum ist aus dem Muster der Wort-ID abgelesen (`HZU2_<Nr><JJJJMMTT><Zähler>`), nicht am Header geprüft. Die Belege sagen über die Herkunft des Namens nichts.

## Quellen zur Deutung

- **Gelesen am Original:** Otto Friedrich Winter, *Antike Baureste als Element der Toponymie in Niederösterreich*, Jahrbuch für Landeskunde von Niederösterreich 54/55, S. 349-361, PDF-Seite 5 (https://www.zobodat.at/pdf/Jb-Landeskde-Niederoesterreich_54-55_0349-0361.pdf). Winter nennt Murstetten (1176/82 *de Murristetin*) und gibt Schusters Deutung wieder: *-stetten* mit einem vermutlich slawischen Personennamen als Bestimmungswort; falls sich das nicht verifizieren lässt, stünde nichts dagegen, es zu den Mauer-Orten (mhd. *mûre*, römerzeitliche Baureste an der Limesstraße) zu stellen. Von der Mur ist nirgends die Rede.
- **Nur über Winter bekannt, nicht geöffnet:** Elisabeth Schuster, *Die Etymologie der niederösterreichischen Ortsnamen* (Ergänzung zum Historischen Ortsnamenbuch von Niederösterreich), Eintrag M 317; Handbuch der historischen Stätten (Winters Anm. 23, S. 432); Lechner, Siedlungsgeschichte (S. 332).
- **Gesehen, ohne Deutung:** de.wikipedia.org/wiki/Murstetten (Lage, Geschichte, keine Namensdeutung).

## Was offen ist

- Schuster selbst am Original prüfen (Eintrag M 317).
- `lemma_33528` *Mûrouwe* (Murau) behält `Mur`; die Deutung des Namens Murau ist hier nicht geprüft.
- Entscheidung bei KZW: `Mur` aus der Etymologie von `lemma_66691` streichen, kein Ersatzziel.
