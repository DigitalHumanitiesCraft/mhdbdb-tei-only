#!/usr/bin/env python3
"""ONAMA-Datenpaket fuer den Narrativ-Explorer (#609, Paket O2): Argonautensage.

Erzeugt aus onamaObjects.ttl und dem Ergebnis von anker-abgleich.py ein
statisches JSON-Paket. Rohdaten (RDF) und daraus erzeugte Sicht sind getrennt:
das Paket nennt Quell-URIs, beide Input-Commits und das Auswahlkriterium.
Es aendert nichts an tei/, authority-files/ oder Annotationen.

Quellenauswahl (Checkin G2, 18.10.2026):
  Teilbaum:  Konzept Q1309 und alles, was ueber onama:narrower erreichbar ist.
  Aufnahme:  Realisierung, deren onama:realises-Konzept im Teilbaum liegt UND
             die (a) Mitglied der Sammlung TRO (Q271), TRY (Q272) oder
             OeNB cod. 2773 (Q1155) ist ("sammlung") oder (b) keine Sammlung
             hat, ein Bild mit RO-Label ist ("abgeleitet": Zuordnung nur ueber
             Konzept und RO-Label; Quelle "REALONLINE", die Handschrift ist
             nicht belegt).
  Nebenhandlung: Bildrealisierung ohne onama:realises, aber mit
             onama:realisesAsSupplementaryNarrative auf ein Konzept im Teilbaum
             (gleiche Sammlungsregel); getrennt gezaehlt.
  Ausgeschlossen: Realisierungen anderer Sammlungen (Hobbit Q1002, Iwein Q889).
  Randfaelle (nicht im Bestand, an KZW zur Entscheidung): Realisierungen der
             drei Sammlungen mit Konzept ausserhalb des Teilbaums, ohne
             Konzept, sowie Realisierungen ohne Sammlung und ohne RO-Label.

Aufruf (Quelle in eigenem leeren Verzeichnis ausserhalb des Repos):
  python scripts/ingest/onama/anker-abgleich.py --ttl <dir>/onamaObjects.ttl \\
      --ttl-commit <sha> --out playground/data/onama/anker-abgleich.json
  python scripts/ingest/onama/build-paket.py --ttl <dir>/onamaObjects.ttl \\
      --ttl-commit <sha> --ontologie-commit <sha> \\
      --abgleich playground/data/onama/anker-abgleich.json \\
      --out playground/data/onama/argonauten.json
Abhaengigkeit: rdflib (nicht in requirements.txt, die pinnt nur die Build-Kette).
"""
import argparse
import collections
import json
import sys
from pathlib import Path

import rdflib

REPO = Path(__file__).resolve().parents[3]
O = rdflib.Namespace("http://onama.sbg.ac.at/ontology#")
OB = "http://onama.sbg.ac.at/object/"
RDF_TYPE = rdflib.RDF.type
WURZEL = rdflib.URIRef(OB + "Q1309")
SAMMLUNGEN = {OB + "Q271": "TRO", OB + "Q272": "TRY", OB + "Q1155": "OENB2773"}
ROLLENKLASSEN = ("AgentRole", "PatientRole", "ThemeRole", "RecipientRole", "InstrumentRole",
                 "GoalRole", "PlaceRole", "WitnessRole", "BenefactiveRole", "ActantRole",
                 "SourceRole", "ExperiencerRole", "StimulusRole", "Co-AgentRole", "ModeRole",
                 "TemporalityRole", "ParticipatorRole", "LocalisationRole", "PredicativeRole",
                 "CauserRole", "PossessorRole")
ENTITAETSKANTEN = ("hasActor", "hasThing", "hasPlace", "hasTemporalEntity", "hasNarrative")


def kurz(u):
    return str(u).split("/")[-1].split("#")[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ttl", required=True, type=Path)
    ap.add_argument("--ttl-commit", required=True)
    ap.add_argument("--ontologie-commit", required=True)
    ap.add_argument("--abgleich", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    g = rdflib.Graph()
    g.parse(str(args.ttl), format="turtle")
    abgleich = json.loads(args.abgleich.read_text(encoding="utf-8"))
    if abgleich["eingaben"]["onama_corpus_commit"] != args.ttl_commit:
        sys.exit("harter Fehler: Abgleich und Paket stammen aus verschiedenen Korpus-Commits")
    passage = {p["uri"]: p for p in abgleich["passagen"]}

    def labels(s):
        out = {}
        for l in g.objects(s, rdflib.RDFS.label):
            lang = getattr(l, "language", None)
            if lang in ("de", "en"):
                out[lang] = str(l)
            else:
                sys.exit(f"harter Fehler: Label ohne de/en-Sprache an {s}")
        return out

    def typen(s):
        return sorted(kurz(t) for t in g.objects(s, RDF_TYPE))

    # --- Teilbaum
    baum = {WURZEL}
    stapel = [WURZEL]
    while stapel:
        x = stapel.pop()
        for n in g.objects(x, O.narrower):
            if n not in baum:
                baum.add(n)
                stapel.append(n)

    # --- Realisierungen einordnen
    alle = sorted(set(g.subjects(RDF_TYPE, O.TextualRealisation)) |
                  set(g.subjects(RDF_TYPE, O.VisualRealisation)), key=str)
    aufgenommen = {}
    randfaelle = []
    ausgeschlossen = []
    for r in alle:
        cs = [str(c) for c in g.objects(r, O.partOfCollection)]
        meine = [SAMMLUNGEN[c] for c in cs if c in SAMMLUNGEN]
        konzepte = list(g.objects(r, O.realises))
        neben = list(g.objects(r, O.realisesAsSupplementaryNarrative))
        im_baum = any(c in baum for c in konzepte)
        neben_im_baum = (not konzepte) and any(c in baum for c in neben)
        de = labels(r).get("de", "")
        ist_ro = de.startswith("RO ")
        isvis = (r, RDF_TYPE, O.VisualRealisation) in g
        if not (im_baum or neben_im_baum):
            if meine:
                grund = ("Konzept ausserhalb des Teilbaums Q1309" if konzepte else
                         "ohne realises-Konzept, Nebenhandlungs-Konzept ausserhalb des Teilbaums" if neben else
                         "ohne Konzept")
                randfaelle.append({"uri": str(r), "id": kurz(r), "label": de, "sammlung": meine[0],
                                   "grund": grund, "konzepte": [kurz(c) for c in konzepte + neben]})
            continue
        if meine:
            zuordnung = "sammlung"
            quelle = meine[0]
        elif not cs and isvis and ist_ro:
            # Die Handschrift ist hier nicht belegt: von den 41 abgeleiteten teilen nur 9 den
            # RO-Nummernkreis (erste fuenf Zeichen) mit Sammlungsmitgliedern (gemessen 18.10.2026),
            # deshalb bleibt die Quelle "REALONLINE" statt "OENB2773".
            zuordnung = "abgeleitet"
            quelle = "REALONLINE"
        elif not cs:
            randfaelle.append({"uri": str(r), "id": kurz(r), "label": de, "sammlung": None,
                               "grund": "Konzept im Teilbaum, aber ohne Sammlung und ohne RO-Label",
                               "konzepte": [kurz(c) for c in konzepte + neben]})
            continue
        else:
            ausgeschlossen.append({"id": kurz(r), "label": de, "sammlungen": [kurz(c) for c in cs],
                                   "grund": "Sammlung ausserhalb des Pilots (Tolkien, Iwein)"})
            continue
        aufgenommen[r] = (zuordnung, quelle, neben_im_baum)

    # --- Entitaeten und Funktionen einsammeln
    entitaeten = {}
    funktionen = {}
    verben = {}

    def entitaet(e):
        k = kurz(e)
        if k not in entitaeten:
            allgemein = [kurz(f) for f in g.objects(e, O.hasGeneralEntityFunction)]
            for f in g.objects(e, O.hasGeneralEntityFunction):
                funktionen[kurz(f)] = labels(f)
            entitaeten[k] = {
                "uri": str(e), "id": k, "typen": typen(e), "labels": labels(e),
                "beschreibung": sorted(str(d) for d in g.objects(e, rdflib.URIRef("http://schema.org/description"))) or None,
                "wikidata": sorted(str(w) for w in g.objects(e, O.hasWikiDataEquivalent)),
                "allgemeine_funktionen": allgemein,
            }
        return k

    def rollen(knoten):
        aus = []
        for rn in sorted(g.objects(knoten, O.hasSemanticRole), key=str):
            klassen = [t for t in typen(rn) if t in ROLLENKLASSEN]
            if len(klassen) != 1:
                sys.exit(f"harter Fehler: Rollenknoten {rn} mit Klassen {typen(rn)}")
            teile = []
            for kante in ENTITAETSKANTEN:
                for e in g.objects(rn, O[kante]):
                    if (e, RDF_TYPE, O.Concept) in g or (e, RDF_TYPE, O.VisualRealisation) in g:
                        teile.append({"kante": kante, "verweis": kurz(e)})
                    elif (e, RDF_TYPE, O.TemporalEntity) in g:
                        teile.append({"kante": kante, "zeit": labels(e)})
                    else:
                        teile.append({"kante": kante, "entitaet": entitaet(e)})
            tf = []
            for f in g.objects(rn, O.hasTemporaryEntityFunction):
                funktionen[kurz(f)] = labels(f)
                tf.append(kurz(f))
            aus.append({"klasse": klassen[0], "beteiligte": teile, "temporaere_funktionen": sorted(tf)})
        return aus

    def aktion(knoten):
        aus = []
        for a in g.objects(knoten, O.hasAction):
            for v in g.objects(a, O.hasVerb):
                verben[kurz(v)] = labels(v)
                aus.append(kurz(v))
        return sorted(aus)

    # --- Konzepte
    konzept_ids = set()
    for r in aufgenommen:
        for c in list(g.objects(r, O.realises)) + list(g.objects(r, O.realisesAsSupplementaryNarrative)):
            konzept_ids.add(c)
    konzepte = {}
    for c in sorted(konzept_ids | baum, key=str):
        konzepte[kurz(c)] = {
            "uri": str(c), "labels": labels(c),
            "im_teilbaum": c in baum,
            "uebergeordnet": sorted(kurz(b) for b in g.objects(c, O.broader)),
            "untergeordnet": sorted(kurz(n) for n in g.objects(c, O.narrower)),
            "wikidata": sorted(str(w) for w in g.objects(c, O.hasWikiDataEquivalent)),
            "iconclass": sorted(str(i) for i in g.objects(c, O.hasIconClassEquivalent)),
            "handlung": aktion(c),
            "rollen": rollen(c),
        }

    # --- Realisierungen
    reals = []
    for r, (zuordnung, quelle, neben) in sorted(aufgenommen.items(), key=lambda kv: str(kv[0])):
        isvis = (r, RDF_TYPE, O.VisualRealisation) in g
        eintrag = {
            "uri": str(r), "id": kurz(r), "art": "bild" if isvis else "text",
            "labels": labels(r), "quelle": quelle, "zuordnung": zuordnung,
            "nebenhandlung": neben,
            "konzepte": sorted(kurz(c) for c in g.objects(r, O.realises)),
            "nebenhandlungs_konzepte": sorted(kurz(c) for c in g.objects(r, O.realisesAsSupplementaryNarrative)),
            "sammlungen": sorted(kurz(c) for c in g.objects(r, O.partOfCollection)),
            "handlung": aktion(r), "rollen": rollen(r),
            "vorher": sorted(kurz(x) for x in g.objects(r, O.previousFabula)),
            "nachher": sorted(kurz(x) for x in g.objects(r, O.nextFabula)),
            "gleichzeitig": sorted(kurz(x) for x in g.objects(r, O.occursSimultaneously)),
        }
        if isvis:
            links = sorted(str(x) for x in g.objects(r, O.hasRoWorkURL))
            eintrag["bildlink"] = links[0] if links else None
            eintrag["bild_werk_uri"] = sorted(str(x) for x in g.objects(r, O.depictedIn))
        passagen = []
        for p in sorted(g.objects(r, O.hasTextPassage), key=str):
            a = passage[str(p)]
            if a["status"] in ("wortanker", "nichtwort_anker") and not a.get("wortspanne"):
                sys.exit(f"harter Fehler: Passage {a['uri']} ohne Wortspanne trotz Status {a['status']}")
            passagen.append({
                "uri": a["uri"], "von": a["von"]["original"], "bis": a["bis"]["original"],
                "status": a["status"], "wortspanne": a.get("wortspanne"),
                "text": a["von"]["sigle"] if a["von"]["gefunden"] else None,
                # Die Spanne ist umgerechnet, wenn ein Endpunkt kein gezaehltes Wort ist
                # (anderes Element oder <w> ohne lemmaRef): Start rueckt vor, Ende zurueck.
                "umgerechnet": a["status"] in ("wortanker", "nichtwort_anker") and (
                    a["von"].get("wortposition") is None or a["bis"].get("wortposition") is None),
            })
        eintrag["passagen"] = passagen
        # Pruefstatus (technisch, nie fachlich), Vorrang offen vor abgeleitet vor geprueft.
        # "offen": Anker nicht gefunden oder umgekehrt, Text ohne Passage, Bild ohne Bildlink.
        # "abgeleitet": Zuordnung ohne Sammlung oder mindestens eine Passage mit umgerechneter
        # Spanne. "geprueft": der Rest, also Zuordnung ueber die Sammlung, bei Text jede
        # Passage mit zwei gezaehlten Wortankern in richtiger Reihenfolge, bei Bild ein Bildlink.
        if (eintrag["art"] == "text" and not passagen) \
                or any(p["status"] in ("nicht_gefunden", "umgekehrt") for p in passagen) \
                or (eintrag["art"] == "bild" and not eintrag.get("bildlink")):
            ps = "offen"
        elif zuordnung == "abgeleitet" or any(p["umgerechnet"] for p in passagen):
            ps = "abgeleitet"
        else:
            ps = "geprueft"
        eintrag["pruefstatus"] = ps
        reals.append(eintrag)

    sammlungen = {}
    for r in reals:
        for c in r["sammlungen"]:
            c_uri = rdflib.URIRef(OB + c)
            sammlungen[c] = labels(c_uri)

    zaehl = collections.Counter()
    for r in reals:
        zaehl[(r["quelle"], r["art"], r["zuordnung"], "neben" if r["nebenhandlung"] else "haupt")] += 1
    ps_zaehl = collections.Counter(r["pruefstatus"] for r in reals)
    stat = {
        "realisierungen_gesamt": len(reals),
        "je_quelle_art_zuordnung_ebene": [
            {"quelle": k[0], "art": k[1], "zuordnung": k[2], "ebene": k[3], "anzahl": v}
            for k, v in sorted(zaehl.items())],
        "pruefstatus": dict(sorted(ps_zaehl.items())),
        "konzepte_im_teilbaum": len(baum),
        "konzepte_im_paket": len(konzepte),
        "entitaeten": len(entitaeten),
        "randfaelle": len(randfaelle),
        "ausgeschlossen": len(ausgeschlossen),
    }
    paket = {
        "meta": {
            "titel": "ONAMA: Argonautensage (Pilot)",
            "zweck": "Kuratierter, selektiver Ausschnitt; kein Gesamtbestand der Mittelalter-Narrative.",
            "quellen": {
                "korpus": "https://github.com/Middle-High-German-Conceptual-Database/onama-corpus",
                "korpus_commit": args.ttl_commit,
                "ontologie": "https://github.com/Middle-High-German-Conceptual-Database/onama",
                "ontologie_commit": args.ontologie_commit,
                "mhdbdb_commit": abgleich["eingaben"]["mhdbdb_commit"],
            },
            "erzeugt_mit": ["scripts/ingest/onama/anker-abgleich.py", "scripts/ingest/onama/build-paket.py"],
            "auswahl": "Teilbaum des Konzepts Q1309; Realisierungen aus TRO, TRY und OeNB cod. 2773; "
                       "siehe Docstring von build-paket.py",
            "lizenz": {
                "festlegung": "Nachnutzung der ONAMA-Daten im Playground unter der MHDBDB-Lizenz "
                              "(Projektleitung, 15.10.2026)",
                "herkunft": "GitHub-Korpus und Ontologie: CC BY-SA 4.0; Website und Teile des Endberichts: "
                            "CC BY-NC-SA; Frontend und Backend: GPL-3.0. Bilder sind nur verlinkt (REALonline).",
            },
            "hinweise": {
                "namensraum": "ONAMA-Q-Nummern sind keine Wikidata-Q-Nummern.",
                "pruefstatus": "Vorrang offen vor abgeleitet vor geprueft. offen = Anker nicht gefunden "
                               "oder umgekehrt, Text ohne Passage, Bild ohne Bildlink; abgeleitet = Zuordnung "
                               "ohne Sammlung oder eine Passage mit umgerechneter Spanne; geprueft (technisch) "
                               "= der Rest: Zuordnung ueber Sammlung und bei Text jede Passage mit zwei "
                               "gezaehlten Wortankern in richtiger Reihenfolge, bei Bild ein Bildlink. "
                               "Fachlich bestaetigt ist keiner.",
                "wortspanne": "Wortpositionen zählen nur <w> mit lemmaRef und Text; liegt ein Endpunkt "
                              "auf einem anderen Element oder einem nicht gezählten <w>, rückt der Start "
                              "auf das nächste, das Ende auf das vorige gezählte Wort.",
            },
            "statistik": stat,
        },
        "konzepte": konzepte,
        "realisierungen": reals,
        "entitaeten": dict(sorted(entitaeten.items())),
        "funktionen": dict(sorted(funktionen.items())),
        "verben": dict(sorted(verben.items())),
        "sammlungen": sammlungen,
        "randfaelle": sorted(randfaelle, key=lambda x: x["id"]),
        "ausgeschlossen": sorted(ausgeschlossen, key=lambda x: x["id"]),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(paket, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps(stat, ensure_ascii=False, indent=1))
    print(f"{args.out.name}: {args.out.stat().st_size} Bytes")


if __name__ == "__main__":
    main()
