"""bre_hauptseite.py: Ueberlieferungsbeschreibung der Hauptseite als Quelle der Werkzuordnung (#147).

Die Hauptseite "Kategorie:Quelle Weingruß" fuehrt im Abschnitt "Überlieferung" je Zeuge die
Einzeltexte in der Reihenfolge der Handschrift auf (nummerierte Listen unter einem
`;Sigle`-Kopf), mit Anmerkungen in Klammern ("nur die letzten drei Verse", "als Gruß
ausgeführt", "(rudimentär)"). Dieses Modul liest sie aus der gepinnten Revision und gleicht sie
gegen die Zuordnung der Transkription (Synopsen, segmentierung.tsv) ab.

Massgeblich fuer die Werkzuordnung ist die Hauptseite (Silvan Wagner, 2026-11-12, #147), die
Synopsen sind ergaenzend. Ein Abgleich-Ergebnis ist ein Befund, keine Korrektur: was nicht
uebereinstimmt, steht in bre_common.ABWEICHUNG_ERKLAERT oder bricht den Lauf ab.
"""
import collections
import re

import bre_common as bc

RE_SIGLE = re.compile(r"^;\s*([A-Za-z]+)(?:<sup>(\d+)</sup>)?\s*$")
RE_ITEM = re.compile(r"^#\s*(\(?)\s*\[\[([^\]|]+)(?:\|[^\]]*)?\]\](\)?)\s*(.*)$")
RE_KLAMMER = re.compile(r"^\((.*)\)$")


def norm_titel(t):
    """Seitentitel ohne Autorzusatz "(Hans Rosenplüt)" und mit einfachen Leerzeichen."""
    return re.sub(r"\s+", " ", re.sub(r"\s*\([^)]*\)\s*$", "", t)).strip()


def abschnitt_ueberlieferung(inhalt):
    """Der Abschnitt "== Überlieferung ==" bis zur naechsten Ueberschrift gleicher Ebene,
    ohne die Uebersichtstabelle."""
    m = re.search(r"^==\s*Überlieferung\s*==\s*$", inhalt, re.M)
    if not m:
        raise bc.HarterFehler("Hauptseite: Abschnitt '== Überlieferung ==' fehlt")
    rest = inhalt[m.end():]
    n = re.search(r"^==[^=\n]+==\s*$", rest, re.M)  # naechste Ebene-2-Ueberschrift
    if n:
        rest = rest[:n.start()]
    u = re.search(r"^===\s*Übersicht der Überlieferung\s*===", rest, re.M)
    if u:
        rest = rest[:u.start()]
    return rest


def parse(inhalt):
    """-> {editionssigle: [ {"teil": n, "titel": ..., "anmerkung": ..., "klammer": bool,
    "zeile": Nr in der Hauptseite} ]} in der Reihenfolge der Hauptseite.

    "teil" zaehlt die Listen je Zeuge (D und W1 haben zwei Teile, R eine zweite Liste mit
    dem Biergruss). Harter Fehler bei einer Listenzeile ausserhalb eines Zeugen oder
    einem unbekannten Siglenkopf.
    """
    erg, sigle, teil, in_liste = {}, None, 0, False
    for nr, z in enumerate(abschnitt_ueberlieferung(inhalt).splitlines(), 1):
        m = RE_SIGLE.match(z.strip()) if z.startswith(";") else None
        if m:
            s = m.group(1) + (m.group(2) or "")
            if s not in bc.ZEUGEN:
                raise bc.HarterFehler(f"Hauptseite: unbekannter Zeuge {s!r} im Kopf {z!r}")
            if s in erg:
                raise bc.HarterFehler(f"Hauptseite: Zeuge {s} doppelt")
            erg[s], sigle, teil, in_liste = [], s, 0, False
            continue
        if z.startswith("#"):
            if sigle is None:
                raise bc.HarterFehler(f"Hauptseite: Listenzeile vor dem ersten Zeugen: {z!r}")
            im = RE_ITEM.match(z)
            if not im:
                raise bc.HarterFehler(f"Hauptseite: Listenzeile nicht lesbar: {z!r}")
            if not in_liste:
                teil += 1
                in_liste = True
            erg[sigle].append({
                "teil": teil, "titel": norm_titel(im.group(2)),
                "anmerkung": im.group(4).strip(), "klammer": bool(im.group(1)),
            })
        elif not z.strip():
            in_liste = False
        elif z.startswith(";"):
            # ";Darüber hinaus ..." (Handschrift ohne Zeugenseite): kein Zeuge
            sigle, in_liste = None, False
    return erg


def parse_matrix(inhalt):
    """Die "Übersicht der Überlieferung" (Tabelle Text x Zeuge) -> {titel: {sigle: zelle}}.

    Nur nichtleere Zellen. Die Zelle traegt die Stellung im Zeugen (mit Teilbuchstabe bei D
    und W1, in Klammern fragmentarisch oder aufgenommen, mit Asterisk eigenstaendige Version).
    Harter Fehler, wenn die Spaltenkoepfe nicht der Zeugenliste entsprechen oder eine Zeile
    nicht 21 Zellen hat.
    """
    m = re.search(r"^===\s*Übersicht der Überlieferung\s*===\s*$", inhalt, re.M)
    if not m:
        raise bc.HarterFehler("Hauptseite: 'Übersicht der Überlieferung' fehlt")
    tab = inhalt[m.end():]
    a, b = tab.find("{|"), tab.find("|}")
    if a < 0 or b < 0:
        raise bc.HarterFehler("Hauptseite: Tabelle der Uebersicht nicht gefunden")
    zeilen = [z for z in tab[a:b].split("\n|-")[1:]]
    kopf = [re.sub(r"</?sup>", "", c.split("|")[-1]).strip() for c in
            re.findall(r"^\|style[^\n]*", zeilen[0], re.M)]
    kopf = [k for k in kopf if k]
    if kopf != list(bc.ZEUGEN):
        raise bc.HarterFehler(f"Hauptseite: Spaltenkoepfe {kopf} != Zeugenliste {list(bc.ZEUGEN)}")
    erg = {}
    for z in zeilen[1:]:
        z = z.strip("\n")
        if not z.strip():
            continue
        erstes, _, rest = z.partition("\n")
        t = re.search(r"\[\[([^\]|]+)", erstes)
        if not t:
            raise bc.HarterFehler(f"Hauptseite: Tabellenzeile ohne Titel: {erstes!r}")
        zellen = [c.strip() for c in ("\n" + rest).replace("\n||", "\x00").split("\x00")[1:]]
        if len(zellen) != len(kopf):
            raise bc.HarterFehler(f"Hauptseite: Zeile {t.group(1)!r} hat {len(zellen)} Zellen "
                                  f"statt {len(kopf)}")
        erg[norm_titel(t.group(1))] = {s: c for s, c in zip(kopf, zellen) if c}
    return erg


def matrix_folge(matrix, sigle):
    """Die Texte eines Zeugen laut Uebersichtstabelle in der Reihenfolge der Stellungen.

    -> Liste wie parse() (titel, teil, anmerkung = Zelle, klammer). Eine Zelle mit zwei
    Stellungen ("A10<br />B8") ergibt zwei Eintraege. Harter Fehler bei einer Zelle, die
    nicht Teilbuchstabe, Zahl, Asterisk und Klammern ist.
    """
    eintraege = []
    for titel, zellen in matrix.items():
        if sigle not in zellen:
            continue
        for teil_zelle in re.split(r"\s*<br\s*/?>\s*", zellen[sigle]):
            m = re.fullmatch(r"(\(?)([A-Z]?)(\d+)(\*?)(\)?)", teil_zelle)
            if not m or bool(m.group(1)) != bool(m.group(5)):
                raise bc.HarterFehler(f"Hauptseite, Uebersicht: Zelle {teil_zelle!r} ({titel}, {sigle}) "
                                      f"nicht lesbar")
            eintraege.append(((m.group(2), int(m.group(3))), {
                "titel": titel, "teil": m.group(2) or "1", "anmerkung": teil_zelle,
                "klammer": bool(m.group(1))}))
    eintraege.sort(key=lambda e: e[0])
    return [e for _, e in eintraege]


def lade_hauptseite():
    """Gepinnte Hauptseite (Manifest + Cache) -> (Seite, geparste Zeugenlisten)."""
    seite = bc.lade_seite(bc.HAUPT_TITEL)
    erg = parse(seite["inhalt"])
    fehlt = [s for s in bc.ZEUGEN if s not in erg]
    if fehlt:
        raise bc.HarterFehler(f"Hauptseite fuehrt keine Ueberlieferung fuer {fehlt}")
    return seite, erg


def abgleich(sigle, haupt_liste, texte_titel, vorspann_art):
    """Vergleicht die Hauptseite eines Zeugen mit den Texten der Transkription.

    texte_titel: Titel der Texte aus der Segmentierung in der Reihenfolge der Transkription
    (mit oder ohne Autorzusatz). vorspann_art: None, "reihentitel", "fragment" oder
    "text_ohne_einzelseite" (bre_common.VORSPANN).

    -> Liste von Abweichungen (dict: art, titel, bisher, hauptseite). Leer, wenn beide
    Listen dieselben Texte in derselben Reihenfolge fuehren. Ein Text, den die Hauptseite
    in Klammern setzt (in einen anderen Text aufgenommen), ist kein eigener Text des Zeugen:
    steht er in der Segmentierung als Abschnitt, ist das die Abweichung "klammer_aber_abschnitt"
    (Anzahl der Abschnitte in "bisher", ebenso bei "nur_bisher"; bei "nur_hauptseite" steht
    "bisher" auf "fehlt" und die Anzahl der fehlenden Vorkommen mit den Anmerkungen in
    "hauptseite"; "reihenfolge" traegt Stellen und Folge).
    Ein Fragment steht bei der Hauptseite ohne Klammer vor dem Link, mit Anmerkung dahinter.
    """
    eigene = [h for h in haupt_liste if not h["klammer"]]
    ht = [h["titel"] for h in eigene]
    unser = [norm_titel(t) for t in texte_titel]
    abw = []
    fehlt_haupt = collections.Counter(unser) - collections.Counter(ht)
    fehlt_unser = collections.Counter(ht) - collections.Counter(unser)
    klammer = {h["titel"]: h for h in haupt_liste if h["klammer"]}
    for t, n in fehlt_haupt.items():
        if t in klammer:
            abw.append({"art": "klammer_aber_abschnitt", "titel": t,
                        "bisher": f"{n}x eigener Abschnitt",
                        "hauptseite": "in Klammern (kein eigener Text)"})
        else:
            abw.append({"art": "nur_bisher", "titel": t, "bisher": f"{n}x", "hauptseite": "fehlt"})
    for titel, n in fehlt_unser.items():
        anm = [h["anmerkung"] or "ohne Anmerkung" for h in eigene if h["titel"] == titel]
        abw.append({"art": "nur_hauptseite", "titel": titel, "bisher": "fehlt",
                    "hauptseite": f"{n}x, " + " / ".join(dict.fromkeys(anm))})
    # Reihenfolge der gemeinsamen Texte
    gemeinsam = collections.Counter(unser) & collections.Counter(ht)

    def filtere(liste):
        rest, out = collections.Counter(gemeinsam), []
        for t in liste:
            if rest.get(t, 0) > 0:
                rest[t] -= 1
                out.append(t)
        return out

    a_, b_ = filtere(unser), filtere(ht)
    if a_ != b_:
        # der Befund traegt die Stellen, an denen die Folgen auseinandergehen (erste bis letzte
        # Abweichung), damit eine weitere Vertauschung eine andere Abweichung ist
        von = next(i for i, (x, y) in enumerate(zip(a_, b_)) if x != y)
        bis = max(i for i, (x, y) in enumerate(zip(a_, b_)) if x != y)
        abw.append({"art": "reihenfolge", "titel": "",
                    "bisher": f"ab Stelle {von + 1}: " + " > ".join(a_[von:bis + 1]),
                    "hauptseite": f"ab Stelle {von + 1}: " + " > ".join(b_[von:bis + 1])})
    return abw


def schluessel(sigle, abw):
    """Schluessel einer Abweichung in bre_common.ABWEICHUNG_ERKLAERT: Zeuge, Art, Text und
    der Inhalt der Abweichung (bisher, laut Hauptseite). Eine andere Abweichung der gleichen
    Art ist ein anderer Schluessel."""
    return (sigle, abw["art"], abw["titel"], abw["bisher"], abw["hauptseite"])
