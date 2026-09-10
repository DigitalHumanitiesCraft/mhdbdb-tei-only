---
name: hausenblase-363
description: Messmuster fuer Batch-Skripte, die wenige TEI-Dateien textuell umschreiben (#363 Hausenblase, 10.09.2026): Sandkasten per Symlinks, Rezept-Zaehlung per getpath, Typ-Traeger per Regex, Kompositum-Formen-Messung aus CONTRACTS, Lemma-Anzahl in hilfe-daten.html
metadata:
  type: project
---

Runde 1 auf uncommittetem Arbeitsstand (`claude/agents-setup-network-check-08f1ri`), Skript `scripts/ingest/pos-disambig/fix-363-hausenblase.py`, 7 Kochbuch-Sigel, 32 Tokens.

## Sandkasten ohne Korpuskopie (unter 1 min)
`tei/` ist 1,4 GB. Statt `git archive`: Scratch-ROOT mit `scripts/corpus_files.py` + Fix-Skript kopiert, `authority-files/lexicon.xml` per `git show origin/main:...`, in `tei/` die 660 unveraenderten Dateien als Symlinks auf den Arbeitsbaum, die 7 geaenderten per `git show origin/main:tei/X` als echte Kopie. `corpus_files()` nimmt PROJECT_ROOT = `scripts/..`, liest ueber Symlinks. Trockenlauf, dann `--apply`, dann `cmp` gegen den Arbeitsbaum: 8/8 byteidentisch. Zweiter Lauf auf dem Ergebnis: 27 Abweichungen, Abbruch (nicht idempotent, wie dokumentiert).

## Zaehlfallen
- **Rezepte sind `<div>` mit `<head>`, ohne `@n`** (HUB3: 61 divs, alle mit head). `lb/@n` startet je Rezept neu, darum liegen `HUB3_71010` und `HUB3_71040` im selben Rezept. 13 getrennte Paare = **11 Rezepte**, 6 Komposita = 6, alle 19 = 16 divs, genau 1 div mit beiden Schreibungen (SUB1 61). Doku sagte „thirteen recipes".
- Div-Identitaet NIE ueber `id(elem)`: lxml-Proxies teilen Adressen ueber Baeume hinweg (alle 19 bekamen dieselbe id). `tree.getpath(div)` plus Dateiname nehmen.
- „acht Lemmata": Quell-Lemmata der 27 falschen Tokens sind 7 (2670, 27031, 2730, 2934, 734, 737, 738); die 7 Tokens ohne lemmaRef sind kein Lemma. Aus `faelle.csv` per DictReader mit `;` zaehlen.
- Typ-Traeger korpusweit: `re.finditer(r'<w xml:id="([^"]+)"[^>]*corresp="variants\.xml#(type_\d+)"')` ueber alle tei, ~30 s. type_106683 pleter 45 -> 43 stimmt; die 5 umgehaengten Typen tragen nur Zieltokens.
- Das Skript **bricht nicht ab**, wenn ein Bestands-Typ fremde Traeger hat, es praegt still neu (`typ_plan`, `fremd` -> `formen_neu`). Docstring und README behaupten Abbruch.

## CONTRACTS-Messung „67,913 Formen an Komposita, 8 nackte Komponenten"
Kompositum = `<etym type="morphological">` mit >= 2 `<seg type="component">` (18.524 Lemmata auf Basis, 18.523 danach). Formen in variants.xml an diesen Lemmata zaehlen, Form == Komponententext ist „nackt". Basis 67.913/8, nach #363 67.927/8 (netto +14: 15 Formen zu lemma_49714, 1 weg mit lemma_27031). Regex-Skript ohne lxml, unter 10 s.

## Breite Korpussuche nach Zweitgliedern
Erstglied `^h[a-zäöüßûâ]{0,4}[sßz]+e?n+$` + Folgetoken `^[pb]l[aoeäö]` findet neben den 13 Paaren nur *herzen blanc/bloet/bloedikeit/blendet/pleuwen*, *hosen blanc*, *hehsen bleib*; Komposita `^h...[sßz]+e?n+[pb]l` nur *herzenbluote* dazu. Menge vollstaendig.

## Lemma-Anzahl in den Hilfeseiten
`hilfe-daten.html` (5x) und `hilfe-korpussuche.html` (1x) tragen „43.879 Lemmata"; gesetzt in `4458686ab` (#368) im selben Commit wie `api/index.json count 43879`. Beim Loeschen eines Lemmas mitziehen, sonst Drift. Kein Gate dafuer.
