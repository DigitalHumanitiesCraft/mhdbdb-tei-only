#!/usr/bin/env python3
"""
Externe Links der ausgelieferten HTML-Seiten pruefen (#653).

Liest alle `<a href="http(s)://...">` der ausgelieferten Seiten und fragt jede
eindeutige URL einmal ab. Ein toter Link faellt sonst erst auf, wenn ein Besucher
ihn anklickt; Verlage, DOIs und kleine Projektseiten verschwinden ohne Ankuendigung.

## Welche Seiten

Alle `*.html` im Wurzelverzeichnis, unter `textreihen/`, `playground/` und
`lemma/` (rekursiv). `lemma/` ist klein (die Lemmaseiten werden im Browser aus dem
Index gebaut, im Repo liegen nur `index.html` und das Skript) und gehoert zur
ausgelieferten Seite, also dabei. Nicht dabei: `includes/` (Fragmente, die
build-pages.py in die Seiten spritzt, stehen damit schon in den Seiten),
`examples/`, `publications/`, `docs/`, `testing/`.

HTML-Entities in href werden entschluesselt (`&amp;` -> `&`), das erledigt der
HTMLParser beim Lesen des Attributs. Das Fragment (`#...`) wird abgeschnitten, die
URL danach dedupliziert: je eindeutiger URL eine Abfrage.

## Wie gefragt wird

Gedrosselt: je Host hoechstens eine Anfrage pro Sekunde, gezaehlt je Anfrage (HEAD,
GET und Wiederholung laufen alle durch dieselbe Drossel; ein Thread je Host, mehrere
Hosts parallel). Anfragen, die eine Weiterleitung auf einen anderen Host ausloest,
zaehlen nicht gegen dessen Drossel. HEAD zuerst, bei jedem Fehlschlag (Status ab 400
oder Netzfehler) GET als Rueckfall, weil viele Server HEAD falsch beantworten, bei
einem fluechtigen Fehler (5xx, TIMEOUT, SSL, sonstiger Netzfehler FEHLER, nicht DNS)
nach fuenf Sekunden ein zweiter GET. Weiterleitungen werden gefolgt, der Endstatus
zaehlt: 200 bis 399 gilt als erreichbar, alles andere als tot, soweit die Allowlist
es nicht freistellt. Eigener allgemeiner User-Agent ohne E-Mail.

## Allowlist

`scripts/audit/link-check-allowlist.json` nennt Domains mit bekannten
Fehlalarmen (meist Sperren gegen Skripte, etwa Verlage hinter doi.org). Eintrag: `domain` (trifft auch Subdomains), `status` (Liste von HTTP-Status
oder der Netzfehlerklassen DNS, TIMEOUT, SSL, FEHLER), `grund`. Statt `domain` kann
ein Eintrag `url` tragen (genau eines von beiden): er trifft nur diese eine URL
(ohne Fragment, zeichengleich) und wird vor den Domain-Eintraegen geprueft; einen
Status, den er nicht nennt, prueft danach der Domain-Eintrag. Das ist fuer einen
Ausfall hinter doi.org, den ein Domain-Eintrag fuer jede DOI freistellen wuerde. Eine
Antwort, die zu einem Eintrag passt, zaehlt als freigestellt und nicht als tot. Alles
andere nicht Erfolgreiche ist tot. Ohne diese Datei waere der Lauf dauerhaft rot.

## Defensiv

Eine unbekannte Eingabe ist ein harter Fehler (Exit 2), kein stilles Ueberspringen:
ein href mit unbekanntem Schema (nicht http, https, mailto, tel, javascript), ein
protokollrelativer href (`//host`), eine nicht lesbare HTML-Datei, ein Fehler in der
Allowlist (fehlendes oder unbekanntes Feld, unbekannte Statusklasse, doppelte Domain
oder URL, ein Eintrag mit beiden oder keinem von `domain` und `url`, eine `url` ohne
http(s), ohne Host oder mit Fragment).

## Ausgabe

Je toter URL der Status und die Datei(en). Jede Zahl traegt ihre Menge in derselben
Zeile (`12 von 427`).

Usage:
    python scripts/audit/check-external-links.py                      # alles pruefen
    python scripts/audit/check-external-links.py --bericht datei.txt  # Ausgabe zusaetzlich in eine Datei
    python scripts/audit/check-external-links.py --liste              # nur die URLs zeigen, nichts abfragen
    python scripts/audit/check-external-links.py --selftest

Exit codes:
    0 = keine toten Links
    1 = mindestens ein toter Link (bei --selftest: ein Fall ist fehlgeschlagen)
    2 = harter Fehler in der Eingabe
"""
import argparse
import concurrent.futures
import http.client
import io
import json
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urlsplit

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

REPO_DIR = Path(__file__).resolve().parents[2]
ALLOWLIST = Path(__file__).resolve().parent / 'link-check-allowlist.json'

# Ordner mit ausgelieferten Seiten. Wurzel nicht rekursiv (sonst docs/, examples/ ...).
WURZEL_ORDNER = ('textreihen', 'playground', 'lemma')

USER_AGENT = 'mhdbdb-link-check (+https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only)'
TIMEOUT_S = 20
PAUSE_JE_HOST_S = 1.0
THREADS = 12
WIEDERHOLUNG_PAUSE_S = 5.0

# Schemata, die ein href tragen darf, ohne dass wir sie abfragen.
ERLAUBTE_SCHEMATA = ('http', 'https', 'mailto', 'tel', 'javascript')
# Netzfehlerklassen, die ein Allowlist-Eintrag nennen darf, neben ganzen HTTP-Status.
FEHLERKLASSEN = ('DNS', 'TIMEOUT', 'SSL', 'FEHLER')
ALLOW_FELDER = ('domain', 'url', 'status', 'grund')
ALLOW_PFLICHT = ('status', 'grund')  # dazu genau eines von domain und url


class Fehler(Exception):
    """Harter Fehler in der Eingabe (Exit 2)."""


# ---------------------------------------------------------------- reine Logik

class _HrefSammler(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        for name, wert in attrs:
            if name == 'href' and wert is not None:
                self.hrefs.append(wert)


def hrefs_aus_html(text):
    """Alle href-Werte der <a>-Elemente; Entities sind schon entschluesselt."""
    sammler = _HrefSammler()
    sammler.feed(text)
    sammler.close()
    return sammler.hrefs


def externe_url(href, quelle):
    """Die abzufragende URL ohne Fragment, oder None fuer interne und nicht abfragbare Links.

    Unbekanntes Schema und protokollrelative Adressen sind harte Fehler.
    """
    h = href.strip()
    if h.startswith('//'):
        raise Fehler(f'{quelle}: protokollrelativer href {href!r}')
    teile = urlsplit(h)
    if not teile.scheme:
        return None  # relativ, Anker oder leer
    schema = teile.scheme.lower()
    if schema not in ERLAUBTE_SCHEMATA:
        raise Fehler(f'{quelle}: href mit unbekanntem Schema {href!r}')
    if schema not in ('http', 'https'):
        return None
    if not teile.hostname:
        raise Fehler(f'{quelle}: http(s)-href ohne Host {href!r}')
    return urldefrag(h)[0]


def sammle_urls(dateien, lies):
    """{url: sortierte Liste der Dateien}. `lies(pfad)` liefert den HTML-Text."""
    urls = {}
    for pfad in dateien:
        for href in hrefs_aus_html(lies(pfad)):
            url = externe_url(href, pfad)
            if url is not None:
                urls.setdefault(url, set()).add(pfad)
    return {u: sorted(d) for u, d in sorted(urls.items())}


def lade_allowlist(daten):
    """Prueft den Inhalt der Allowlist; gibt [(schluessel, frozenset(status), grund)] zurueck.

    Der Schluessel ist die Domain oder, bei einem URL-Eintrag, die URL (ist_url_eintrag).
    """
    if not isinstance(daten, dict) or set(daten) - {'_comment', 'eintraege'} or 'eintraege' not in daten:
        raise Fehler("Allowlist: erwartet wird ein Objekt mit '_comment' (optional) und 'eintraege'")
    if not isinstance(daten['eintraege'], list):
        raise Fehler("Allowlist: 'eintraege' ist keine Liste")
    ergebnis, gesehen = [], set()
    for i, e in enumerate(daten['eintraege']):
        if not isinstance(e, dict):
            raise Fehler(f'Allowlist-Eintrag {i}: kein Objekt')
        fehlt = [f for f in ALLOW_PFLICHT if f not in e]
        if fehlt:
            raise Fehler(f'Allowlist-Eintrag {i} ohne Feld ' + ', '.join(repr(f) for f in fehlt))
        unbekannt = sorted(set(e) - set(ALLOW_FELDER))
        if unbekannt:
            raise Fehler(f'Allowlist-Eintrag {i} mit unbekanntem Feld ' + ', '.join(repr(f) for f in unbekannt))
        art = [f for f in ('domain', 'url') if f in e]
        if len(art) != 1:
            raise Fehler(f"Allowlist-Eintrag {i}: genau eines von 'domain' und 'url' erwartet, "
                         f"vorhanden {len(art)} von 2")
        if art == ['domain']:
            domain = e['domain']
            if not isinstance(domain, str) or not domain or domain != domain.lower() or '/' in domain:
                raise Fehler(f'Allowlist-Eintrag {i}: domain {domain!r} ist kein kleingeschriebener Hostname')
            schluessel = domain
        else:
            url = e['url']
            teile = urlsplit(url) if isinstance(url, str) else None
            if (teile is None or teile.scheme not in ('http', 'https') or not teile.hostname
                    or urldefrag(url)[0] != url or url != url.strip()):
                raise Fehler(f'Allowlist-Eintrag {i}: url {url!r} ist keine http(s)-URL mit Host ohne Fragment')
            schluessel = url
        if schluessel in gesehen:
            raise Fehler(f'Allowlist: {art[0]} {schluessel!r} doppelt')
        gesehen.add(schluessel)
        status = e['status']
        if not isinstance(status, list) or not status:
            raise Fehler(f'Allowlist-Eintrag {schluessel}: status ist keine nichtleere Liste')
        for s in status:
            ok_int = isinstance(s, int) and not isinstance(s, bool) and 100 <= s <= 599
            if not ok_int and s not in FEHLERKLASSEN:
                raise Fehler(f'Allowlist-Eintrag {schluessel}: unbekannter status {s!r} '
                             f'(erlaubt: HTTP-Status 100 bis 599 oder {", ".join(FEHLERKLASSEN)})')
        if not isinstance(e['grund'], str) or not e['grund'].strip():
            raise Fehler(f'Allowlist-Eintrag {schluessel}: grund ist kein nichtleerer Text')
        ergebnis.append((schluessel, frozenset(status), e['grund']))
    return ergebnis


def ist_url_eintrag(schluessel):
    """Ein Domain-Schluessel enthaelt kein '/' (lade_allowlist prueft das), eine URL schon."""
    return '://' in schluessel


def host_passt(host, domain):
    return host == domain or host.endswith('.' + domain)


def ist_erfolg(status):
    return isinstance(status, int) and 200 <= status < 400


def allowlist_treffer(url, status, allowlist):
    """Schluessel des passenden Eintrags oder None; ein URL-Eintrag geht einem Domain-Eintrag vor."""
    for schluessel, stati, _ in allowlist:
        if ist_url_eintrag(schluessel) and schluessel == url and status in stati:
            return schluessel
    host = (urlsplit(url).hostname or '').lower()
    for schluessel, stati, _ in allowlist:
        if not ist_url_eintrag(schluessel) and host_passt(host, schluessel) and status in stati:
            return schluessel
    return None


def klassifiziere(ergebnisse, allowlist):
    """ergebnisse {url: status} -> (tot {url: status}, frei {url: (status, domain)}, ok [url])."""
    tot, frei, ok = {}, {}, []
    for url, status in ergebnisse.items():
        if ist_erfolg(status):
            ok.append(url)
            continue
        d = allowlist_treffer(url, status, allowlist)
        if d is not None:
            frei[url] = (status, d)
        else:
            tot[url] = status
    return tot, frei, ok


def bericht_zeilen(urls, ergebnisse, allowlist, n_dateien):
    tot, frei, ok = klassifiziere(ergebnisse, allowlist)
    n = len(urls)
    z = [f'Externe Links: {n} eindeutige URLs aus {n_dateien} HTML-Dateien geprueft',
         f'{len(tot)} von {n} tot, {len(frei)} von {n} durch die Allowlist freigestellt, '
         f'{len(ok)} von {n} erreichbar']
    if frei:
        je_domain = {}
        for _, d in frei.values():
            je_domain[d] = je_domain.get(d, 0) + 1
        z.append('Freigestellt nach Eintrag (Domain oder URL): ' +', '.join(f'{d} {c} von {len(frei)}'
                                                          for d, c in sorted(je_domain.items())))
    benutzt = {d for _, d in frei.values()}
    ungenutzt = [d for d, _, _ in allowlist if d not in benutzt]
    if ungenutzt:
        z.append(f'Allowlist-Eintraege ohne Treffer ({len(ungenutzt)} von {len(allowlist)}): ' + ', '.join(ungenutzt))
    for url, status in sorted(tot.items()):
        z.append('')
        z.append(f'TOT {status}  {url}')
        for d in urls[url]:
            z.append(f'    {d}')
    return z, len(tot)


# --------------------------------------------------------------------- Netz

def _klasse(exc):
    """Netzfehler -> Klasse aus FEHLERKLASSEN."""
    ursache = exc.reason if isinstance(exc, urllib.error.URLError) else exc
    if isinstance(ursache, socket.gaierror):
        return 'DNS'
    if isinstance(ursache, (socket.timeout, TimeoutError)):
        return 'TIMEOUT'
    if isinstance(ursache, ssl.SSLError):
        return 'SSL'
    return 'FEHLER'


def _anfrage(url, methode):
    req = urllib.request.Request(url, method=methode, headers={'User-Agent': USER_AGENT, 'Accept': '*/*'})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as antwort:
            return antwort.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, OSError, ValueError, http.client.HTTPException) as exc:
        return _klasse(exc)


def ist_fluechtig(status):
    """Ein Fehler, der beim naechsten Versuch verschwinden kann: Server 5xx, TIMEOUT, SSL und
    sonstiger Netzfehler (FEHLER). Nicht DNS und kein 4xx."""
    return (isinstance(status, int) and status >= 500) or status in ('TIMEOUT', 'SSL', 'FEHLER')


class Drossel:
    """Haelt zwischen zwei Anfragen (Start zu Start) mindestens `pause` Sekunden ein.

    Eine Drossel gehoert einem Host und einem Thread; HEAD, GET und Wiederholung
    laufen alle durch sie, nicht nur der Wechsel von einer URL zur naechsten.
    """

    def __init__(self, pause, uhr=time.monotonic, schlaf=time.sleep):
        self.pause, self.uhr, self.schlaf, self.letzte = pause, uhr, schlaf, None

    def warten(self):
        if self.letzte is not None:
            rest = self.pause - (self.uhr() - self.letzte)
            if rest > 0:
                self.schlaf(rest)
        self.letzte = self.uhr()


def frage_ab(url, drossel, anfrage=_anfrage):
    """Status der URL: HEAD, bei Misserfolg GET, bei einem fluechtigen Fehler ein zweiter GET.

    Jede Anfrage geht durch die Drossel des Hosts.
    Zwei Laeufe am 03.11.2026 hintereinander unterschieden sich an zwei URLs (ein SSL-Fehler,
    der beim zweiten Mal fehlte, ein 403, das ein 500 wurde), ein toter Link darf aber nicht von einem Moment abhaengen.
    """
    drossel.warten()
    status = anfrage(url, 'HEAD')
    if ist_erfolg(status):
        return status
    drossel.warten()
    status = anfrage(url, 'GET')
    if ist_fluechtig(status):
        time.sleep(WIEDERHOLUNG_PAUSE_S)
        drossel.warten()
        status = anfrage(url, 'GET')
    return status


def frage_alle_ab(urls):
    """{url: status}; je Host nacheinander mit Pause, mehrere Hosts parallel."""
    je_host = {}
    for u in urls:
        je_host.setdefault(urlsplit(u).hostname.lower(), []).append(u)

    def lauf(host_urls):
        drossel = Drossel(PAUSE_JE_HOST_S)
        return {u: frage_ab(u, drossel) for u in host_urls}

    ergebnisse = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as pool:
        for teil in pool.map(lauf, je_host.values()):
            ergebnisse.update(teil)
    return ergebnisse


# ------------------------------------------------------------------- Dateien

def html_dateien():
    """Relative Pfade (mit /) aller ausgelieferten HTML-Dateien."""
    pfade = sorted(p for p in REPO_DIR.glob('*.html'))
    for ordner in WURZEL_ORDNER:
        basis = REPO_DIR / ordner
        if not basis.is_dir():
            raise Fehler(f'Ordner {ordner}/ fehlt')
        pfade += sorted(basis.rglob('*.html'))
    if not pfade:
        raise Fehler('keine HTML-Dateien gefunden')
    return [p.relative_to(REPO_DIR).as_posix() for p in pfade]


def lies_datei(rel):
    try:
        return (REPO_DIR / rel).read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as exc:
        raise Fehler(f'{rel} nicht lesbar: {exc}')


def lade_allowlist_datei():
    try:
        daten = json.loads(ALLOWLIST.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise Fehler(f'Allowlist nicht lesbar ({ALLOWLIST}): {exc}')
    return lade_allowlist(daten)


# ------------------------------------------------------------------- Selbsttest

def selftest():
    cases = []

    def wirft(f, teil):
        try:
            f()
        except Fehler as exc:
            return teil in str(exc)
        return False

    html = ('<a href="https://a.example/x?p=1&amp;q=2#frag">1</a><A HREF=\'http://b.example/\'>2</A>'
            '<a href="mailto:x@y.z">3</a><a href="seite.html#a">4</a><a href="#oben">5</a>'
            '<a name="nur-anker">6</a><link href="https://nicht-a.example/">')
    cases.append(('href: Entity entschluesselt, Fragment ab, nur <a>, interne Links raus',
                  sammle_urls(['x.html'], lambda p: html)
                  == {'http://b.example/': ['x.html'], 'https://a.example/x?p=1&q=2': ['x.html']}))
    cases.append(('gleiche URL aus zwei Dateien: einmal, mit beiden Dateien',
                  sammle_urls(['b.html', 'a.html'], lambda p: '<a href="https://a.example/">x</a>')
                  == {'https://a.example/': ['a.html', 'b.html']}))
    cases.append(('unbekanntes Schema: harter Fehler',
                  wirft(lambda: externe_url('ftp://a.example/', 'x.html'), 'unbekanntem Schema')))
    cases.append(('protokollrelativ: harter Fehler',
                  wirft(lambda: externe_url('//a.example/', 'x.html'), 'protokollrelativer')))
    cases.append(('http ohne Host: harter Fehler',
                  wirft(lambda: externe_url('http:///x', 'x.html'), 'ohne Host')))
    cases.append(('mailto, tel, javascript sind keine Abfrage',
                  externe_url('mailto:a@b.c', 'x') is None and externe_url('tel:+43', 'x') is None
                  and externe_url('javascript:void(0)', 'x') is None))

    gut = {'_comment': 'c', 'eintraege': [
        {'domain': 'doi.org', 'status': [403, 202], 'grund': 'g'},
        {'domain': 'verlag.example', 'status': [403, 'TIMEOUT'], 'grund': 'g'}]}
    al = lade_allowlist(gut)
    cases.append(('Allowlist gueltig', len(al) == 2))
    cases.append(('Allowlist: Objekt ohne eintraege', wirft(lambda: lade_allowlist({}), "'eintraege'")))
    cases.append(('Allowlist: unbekanntes Feld',
                  wirft(lambda: lade_allowlist({'eintraege': [{'domain': 'a.de', 'status': [403], 'grund': 'g', 'x': 1}]}),
                        "unbekanntem Feld 'x'")))
    cases.append(('Allowlist: fehlendes Feld',
                  wirft(lambda: lade_allowlist({'eintraege': [{'domain': 'a.de', 'status': [403]}]}), "ohne Feld 'grund'")))
    cases.append(('Allowlist: unbekannte Statusklasse',
                  wirft(lambda: lade_allowlist({'eintraege': [{'domain': 'a.de', 'status': ['KAPUTT'], 'grund': 'g'}]}),
                        'unbekannter status')))
    cases.append(('Allowlist: doppelte Domain',
                  wirft(lambda: lade_allowlist({'eintraege': [{'domain': 'a.de', 'status': [403], 'grund': 'g'},
                                                              {'domain': 'a.de', 'status': [404], 'grund': 'g'}]}),
                        'doppelt')))
    cases.append(('Allowlist: Domain mit Pfad oder Grossbuchstaben',
                  wirft(lambda: lade_allowlist({'eintraege': [{'domain': 'A.de/x', 'status': [403], 'grund': 'g'}]}),
                        'kein kleingeschriebener Hostname')))

    ergebnisse = {
        'https://doi.org/10.1/x': 403,          # freigestellt
        'https://www.doi.org/10.1/y': 404,      # Subdomain, aber falscher Status: tot
        'https://verlag.example/a': 'TIMEOUT',  # freigestellt (Fehlerklasse)
        'https://anders.example/a': 403,        # tot, keine Domain
        'https://notdoi.org/a': 403,            # kein Subdomain-Treffer von doi.org: tot
        'https://ok.example/': 200,
        'https://weiter.example/': 301,
    }
    tot, frei, ok = klassifiziere(ergebnisse, al)
    cases.append(('Klassifikation: tot, freigestellt und erreichbar getrennt',
                  sorted(tot) == ['https://anders.example/a', 'https://notdoi.org/a', 'https://www.doi.org/10.1/y']
                  and sorted(frei) == ['https://doi.org/10.1/x', 'https://verlag.example/a']
                  and sorted(ok) == ['https://ok.example/', 'https://weiter.example/']))
    cases.append(('fluechtig: 5xx und Netzfehler ja, 404, 403 und DNS nein',
                  all(ist_fluechtig(s) for s in (500, 503, 'TIMEOUT', 'SSL', 'FEHLER'))
                  and not any(ist_fluechtig(s) for s in (404, 403, 401, 'DNS', 200))))
    # Drosselung je Anfrage: HEAD, GET und Wiederholung einer URL laufen mit echter Uhr
    # durch dieselbe Drossel, die Abstaende Start zu Start muessen alle >= Pause sein.
    global WIEDERHOLUNG_PAUSE_S
    zeiten = []

    def falsche_anfrage(url, methode):
        zeiten.append(time.monotonic())
        return 500

    alt, WIEDERHOLUNG_PAUSE_S = WIEDERHOLUNG_PAUSE_S, 0.0
    try:
        pause = 0.2
        drossel = Drossel(pause)
        for u in ('https://h.example/1', 'https://h.example/2'):
            frage_ab(u, drossel, falsche_anfrage)
    finally:
        WIEDERHOLUNG_PAUSE_S = alt
    abstaende = [b - a for a, b in zip(zeiten, zeiten[1:])]
    cases.append((f'Drosselung je Anfrage: {len(zeiten)} Anfragen (HEAD, GET, Wiederholung je URL), '
                  f'kleinster Abstand {min(abstaende):.2f} s >= {pause} s',
                  len(zeiten) == 6 and min(abstaende) >= pause - 0.01))
    schlaf = []
    uhr = iter([0.0, 0.3, 1.0, 2.5, 2.5]).__next__  # setzen, rechnen, setzen, rechnen, setzen
    d = Drossel(1.0, uhr=uhr, schlaf=schlaf.append)
    d.warten(); d.warten(); d.warten()
    cases.append(('Drossel: schlaeft nur den fehlenden Rest',
                  len(schlaf) == 1 and abs(schlaf[0] - 0.7) < 1e-9))
    cases.append(('Subdomain trifft, Namensendung ohne Punkt nicht',
                  host_passt('www.doi.org', 'doi.org') and not host_passt('notdoi.org', 'doi.org')))
    # URL-Eintraege: nur die genannte URL mit dem genannten Status, vor dem Domain-Eintrag
    al_url = lade_allowlist({'eintraege': [
        {'domain': 'doi.org', 'status': [403, 405], 'grund': 'g'},
        {'url': 'https://doi.org/10.9/z', 'status': [503, 403], 'grund': 'g'}]})
    erg_url = {
        'https://doi.org/10.9/z': 503,       # URL-Eintrag
        'https://doi.org/10.9/z2': 503,      # gleiche Domain, andere URL: tot
        'https://doi.org/10.9/zz': 404,      # Status nicht genannt: tot
        'https://doi.org/10.9/a': 403,       # Domain-Eintrag
    }
    tot_u, frei_u, _ = klassifiziere(erg_url, al_url)
    cases.append(('URL-Eintrag: nur genau diese URL und dieser Status',
                  sorted(tot_u) == ['https://doi.org/10.9/z2', 'https://doi.org/10.9/zz']
                  and frei_u == {'https://doi.org/10.9/z': (503, 'https://doi.org/10.9/z'),
                                 'https://doi.org/10.9/a': (403, 'doi.org')}))
    cases.append(('URL-Eintrag: dieselbe URL mit nicht genanntem Status bleibt tot',
                  klassifiziere({'https://doi.org/10.9/z': 404}, al_url)[0] == {'https://doi.org/10.9/z': 404}))
    cases.append(('URL-Eintrag: nicht genannter Status faellt auf den Domain-Eintrag durch',
                  allowlist_treffer('https://doi.org/10.9/z', 405, al_url) == 'doi.org'))
    cases.append(('URL-Eintrag geht dem Domain-Eintrag vor',
                  allowlist_treffer('https://doi.org/10.9/z', 403, al_url) == 'https://doi.org/10.9/z'))
    cases.append(('Allowlist: domain und url zugleich',
                  wirft(lambda: lade_allowlist({'eintraege': [{'domain': 'a.de', 'url': 'https://a.de/x',
                                                              'status': [403], 'grund': 'g'}]}), 'genau eines')))
    cases.append(('Allowlist: weder domain noch url',
                  wirft(lambda: lade_allowlist({'eintraege': [{'status': [403], 'grund': 'g'}]}), 'genau eines')))
    cases.append(('Allowlist: url mit Fragment, ohne Schema, ohne Host, kein Text',
                  all(wirft(lambda u=u: lade_allowlist({'eintraege': [{'url': u, 'status': [403], 'grund': 'g'}]}),
                            'keine http(s)-URL')
                      for u in ('https://a.de/x#f', 'a.de/x', 'https:///x', 5, ' https://a.de/x'))))
    cases.append(('Allowlist: doppelte URL',
                  wirft(lambda: lade_allowlist({'eintraege': [{'url': 'https://a.de/x', 'status': [403], 'grund': 'g'},
                                                              {'url': 'https://a.de/x', 'status': [404], 'grund': 'g'}]}),
                        "url 'https://a.de/x' doppelt")))
    z_url, _ = bericht_zeilen({u: ['d.html'] for u in erg_url}, erg_url, al_url, 1)
    cases.append(('Bericht: URL-Eintrag erscheint unter den Freistellungen',
                  'Freigestellt nach Eintrag (Domain oder URL): doi.org 1 von 2, https://doi.org/10.9/z 1 von 2'
                  in '\n'.join(z_url)))

    urls = {u: ['d.html'] for u in ergebnisse}
    zeilen, n_tot = bericht_zeilen(urls, ergebnisse, al, 3)
    text = '\n'.join(zeilen)
    cases.append(('Bericht: Zahlen tragen ihre Menge, tote URL mit Datei',
                  n_tot == 3 and '3 von 7 tot, 2 von 7 durch die Allowlist freigestellt, 2 von 7 erreichbar' in text
                  and 'TOT 403  https://anders.example/a\n    d.html' in text
                  and '7 eindeutige URLs aus 3 HTML-Dateien' in text))

    failed = [n for n, ok_ in cases if not ok_]
    for n, ok_ in cases:
        print(f"  {'OK  ' if ok_ else 'FAIL'}  {n}")
    if failed:
        print(f'\nSelbsttest fehlgeschlagen: {len(failed)} von {len(cases)}', file=sys.stderr)
        return 1
    print(f'\nSelbsttest bestanden: {len(cases)} Faelle')
    return 0


def main():
    ap = argparse.ArgumentParser(description='Externe Links der ausgelieferten HTML-Seiten pruefen.')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--liste', action='store_true', help='nur die gesammelten URLs zeigen, nichts abfragen')
    ap.add_argument('--bericht', help='Ausgabe zusaetzlich in diese Datei schreiben')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    try:
        allowlist = lade_allowlist_datei()
        dateien = html_dateien()
        urls = sammle_urls(dateien, lies_datei)
        if args.liste:
            for u, d in urls.items():
                print(f'{u}  ({len(d)} Datei(en))')
            print(f'{len(urls)} eindeutige URLs aus {len(dateien)} HTML-Dateien')
            return 0
        print(f'Frage {len(urls)} URLs ab (je Host hoechstens eine Anfrage pro {PAUSE_JE_HOST_S:g} s) ...', flush=True)
        zeilen, n_tot = bericht_zeilen(urls, frage_alle_ab(list(urls)), allowlist, len(dateien))
    except Fehler as exc:
        print(f'FEHLER: {exc}', file=sys.stderr)
        return 2
    text = '\n'.join(zeilen)
    print(text)
    if args.bericht:
        Path(args.bericht).write_text(text + '\n', encoding='utf-8')
    return 1 if n_tot else 0


if __name__ == '__main__':
    sys.exit(main())
