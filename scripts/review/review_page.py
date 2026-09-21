#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Das Basisformat fuer kuratorische Pruefseiten (#443).

Eine einzelne HTML-Datei, die man verschickt und ohne Installation im Browser
oeffnet. Keine externe Datei, kein Server, kein Build beim Empfaenger: CSS, JS
und Daten stehen in der Datei.

## Warum eingebettet und nicht nachgeladen

KZW im Body von #443: "Fuer mich ist die einzelne HTML-Datei, die man
verschickt und ohne Installation im Browser oeffnet, weiterhin das gewuenschte
Grundformat." Eine nachladende Seite scheitert unter `file://` an CORS, also
genau in der Lage, fuer die sie gebaut ist. Der Preis ist, dass die Seite
altert; die Antwort darauf ist dieses Skript und nicht ein Nachladeweg: aendern
sich die Daten, wird die Seite neu erzeugt. Der Datenstand steht deshalb
sichtbar im Kopf.

## Was das Format zusichert

Die Punkte aus dem Body von #443, jeder mit seiner Stelle im erzeugten HTML:

  Kopf        Titel, Pruefanleitung, Vorgang, Datenstand, Namensfeld
  Beleg       Pruefeindeutige Frage, Werk und Fundstelle, Kontext, Zielwort hervorgehoben
  Vorschlag   als Maschinenvorschlag ausgewiesen, mit Begruendung und Unsicherheit
  Antwort     wenige passende Optionen, dazu immer eine freie Antwort
  Kommentar   immer sichtbar, vier Zeilen hoch, vergroesserbar, unabhaengig von der Antwort
  Uebersicht  Fortschritt und Filter nach Bearbeitungsstand
  Speichern   automatisch im Browser, mit sichtbarer Anzeige
  Weitergeben JSON und ein menschenlesbarer HTML-Bericht, dazu Import

Und Alans drei Punkte aus demselben Body:

  1. Die Auswahl passt zum Fall; weitere Moeglichkeiten sind aufklappbar, eine
     freie Antwort bleibt immer moeglich.
  2. Der Kommentar ist ein echtes Textfeld, vier Zeilen hoch, und haengt an
     keiner Antwortoption.
  3. Drei Bearbeitungsstaende: unbearbeitet, entschieden, geprueft und offen.
     Der dritte ist eine dokumentierte Rueckmeldung und bleibt im Export.

## Was das Format NICHT tut

Es entscheidet nichts. Ein Maschinenvorschlag ist keine menschliche
Entscheidung, und die Seite sagt das an jeder Karte. Es gibt keine
Sammelaktion, die Faelle unbesehen auf denselben Wert setzt.

## Gestaltung

Die Tokens stammen aus `docs/DESIGN.md` und sind hier woertlich eingesetzt
statt importiert: die Datei darf auf nichts im Repositorium zeigen. Icons sind
Heroicons als inline SVG, der einzige Icon-Stil des Projekts; keine Emoji.
"""
import html
import json

FORMAT_VERSION = '1.0.0'

CSS = r"""
:root {
  --brand-50:  #f1f5fd;
  --brand-100: #e2ebfa;
  --brand-200: #c0d3f4;
  --brand-500: #3b75d8;
  --brand-600: #265cc4;
  --brand-700: #1f4aa2;
  --bg-page:      #f1f5f9;
  --bg-primary:   #ffffff;
  --bg-secondary: #f8fafc;
  --text-primary:   #1f2937;
  --text-secondary: #64748b;
  --border-primary: #e2e8f0;
  --accent-primary: #3b75d8;
  --info-bg: #eff6ff; --info-br: #bfdbfe; --info-tx: #1e40af;
  --warn-bg: #fefce8; --warn-br: #fde68a; --warn-tx: #854d0e;
  --ok-bg:   #f0fdf4; --ok-br:   #bbf7d0; --ok-tx:   #15803d;
  --open-bg: #fdf4ff; --open-br: #e9d5ff; --open-tx: #6b21a8;
  --mark-bg: #fbbf24; --mark-tx: #78350f;
  --shadow: 0 1px 2px rgba(15, 23, 42, .06), 0 1px 3px rgba(15, 23, 42, .08);
}
:root[data-theme="dark"] {
  --bg-page:      #0f172a;
  --bg-primary:   #1e293b;
  --bg-secondary: #172033;
  --text-primary:   #e2e8f0;
  --text-secondary: #94a3b8;
  --border-primary: #334155;
  --brand-50:  #16243f;
  --brand-100: #1c2f52;
  --brand-200: #2a4472;
  --brand-600: #8ab0f0;
  --brand-700: #b7cdf7;
  --info-bg: #17273f; --info-br: #2b4a7a; --info-tx: #bfdbfe;
  --warn-bg: #2e2716; --warn-br: #5b4a1e; --warn-tx: #fde68a;
  --ok-bg:   #14281d; --ok-br:   #1f5134; --ok-tx:   #bbf7d0;
  --open-bg: #281a33; --open-br: #4b2a63; --open-tx: #e9d5ff;
  --mark-bg: #92670a; --mark-tx: #fef3c7;
  --shadow: 0 1px 2px rgba(0, 0, 0, .4);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg-page);
  color: var(--text-primary);
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: 16px;
  line-height: 1.55;
}
a { color: var(--brand-600); }
.wrap { max-width: 1040px; margin: 0 auto; padding: 0 24px 96px; }

/* Kopfleiste: Name, Fortschritt, Export. Bleibt beim Scrollen stehen. */
.bar {
  position: sticky; top: 0; z-index: 50;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-primary);
  backdrop-filter: blur(6px);
}
.bar-inner {
  max-width: 1040px; margin: 0 auto; padding: 12px 24px;
  display: flex; flex-wrap: wrap; gap: 12px 20px; align-items: center;
}
.bar-title { font-weight: 700; font-size: .95rem; margin-right: auto; }
.bar-title span { display: block; font-weight: 500; font-size: .8rem; color: var(--text-secondary); }
.field { display: flex; align-items: center; gap: 8px; }
label { font-size: .8rem; font-weight: 600; color: var(--text-secondary); }
input[type="text"], textarea, select {
  font: inherit; color: var(--text-primary); background: var(--bg-primary);
  border: 1px solid var(--border-primary); border-radius: 10px; padding: 7px 10px;
}
input[type="text"]:focus, textarea:focus, select:focus {
  outline: none; border-color: var(--brand-500); box-shadow: 0 0 0 3px var(--brand-100);
}
.btn {
  font: inherit; font-size: .85rem; font-weight: 600; cursor: pointer;
  display: inline-flex; align-items: center; gap: 6px;
  border-radius: 10px; padding: 7px 13px;
  background: var(--brand-50); color: var(--brand-700);
  border: 1px solid var(--brand-200);
}
.btn:hover { background: var(--brand-100); border-color: var(--brand-500); }
.btn-plain { background: var(--bg-primary); color: var(--text-primary); border-color: var(--border-primary); }
.btn-plain:hover { background: var(--bg-secondary); border-color: var(--text-secondary); }
.btn svg { width: 16px; height: 16px; }

.saveflag { font-size: .78rem; color: var(--text-secondary); display: inline-flex; align-items: center; gap: 5px; }
.saveflag svg { width: 14px; height: 14px; }
.saveflag.on { color: var(--ok-tx); }

/* Fortschritt */
.progress { min-width: 190px; }
.progress-track { height: 7px; border-radius: 999px; background: var(--border-primary); overflow: hidden; display: flex; }
.progress-track i { display: block; height: 100%; }
.seg-done { background: #22c55e; }
.seg-open { background: #a855f7; }
.progress-text { font-size: .76rem; color: var(--text-secondary); margin-top: 3px; }

/* Kopfbereich */
header.page { padding: 34px 0 10px; }
header.page h1 { font-size: 1.875rem; margin: 0 0 6px; line-height: 1.25; }
header.page .sub { color: var(--text-secondary); margin: 0 0 22px; font-size: 1.02rem; }
.panel {
  background: var(--bg-primary); border: 1px solid var(--border-primary);
  border-radius: 18px; padding: 22px 24px; box-shadow: var(--shadow); margin-bottom: 18px;
}
.panel h2 { font-size: 1.1rem; margin: 0 0 10px; }
.panel.wichtig { border-color: var(--warn-br); background: var(--warn-bg); }
.panel.wichtig h2 { color: var(--warn-tx); }
ul.nav { list-style: none; margin: 12px 0 0; padding: 0; display: grid; gap: 6px; }
ul.nav a { text-decoration: none; font-weight: 600; }
ul.nav li { font-size: .9rem; }
ul.nav .anz { color: var(--text-secondary); font-weight: 400; }
.panel p { margin: 0 0 10px; }
.panel p:last-child { margin-bottom: 0; }
.eyebrow {
  font-size: .75rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: .07em; color: var(--text-secondary); margin: 0 0 8px;
}
dl.stand { display: grid; grid-template-columns: max-content 1fr; gap: 5px 18px; margin: 0; font-size: .88rem; }
dl.stand dt { color: var(--text-secondary); }
dl.stand dd { margin: 0; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .92em; }
/* Ein zitierter Beleg im Fliesstext, gesetzt wie die Belege selbst. */
.zit { font-family: Georgia, "Times New Roman", serif; font-size: 1.04em; }

/* Filter */
.filters { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 4px 0 24px; }
.chip {
  font: inherit; font-size: .82rem; font-weight: 600; cursor: pointer;
  border-radius: 999px; padding: 5px 13px;
  background: var(--bg-primary); color: var(--text-secondary);
  border: 1px solid var(--border-primary);
}
.chip[aria-pressed="true"] { background: var(--brand-600); border-color: var(--brand-600); color: #fff; }
:root[data-theme="dark"] .chip[aria-pressed="true"] { color: #0f172a; }

/* Gruppen */
section.gruppe { margin: 34px 0 0; }
section.gruppe > h2 { font-size: 1.4rem; margin: 0 0 4px; }
section.gruppe > .gruppe-text { color: var(--text-secondary); margin: 0 0 16px; max-width: 76ch; }

/* Fallkarte */
.fall {
  background: var(--bg-primary); border: 1px solid var(--border-primary);
  border-radius: 18px; padding: 0; box-shadow: var(--shadow); margin-bottom: 20px; overflow: hidden;
}
.fall[data-status="entschieden"] { border-color: var(--ok-br); }
.fall[data-status="offen"] { border-color: var(--open-br); }
.fall-kopf { padding: 18px 24px 14px; border-bottom: 1px solid var(--border-primary); }
.fall-kopf h3 { margin: 0 0 6px; font-size: 1.12rem; }
.fall-kopf h3 .form { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.fall-frage { margin: 0; font-weight: 600; }
.merkmale { display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0 0; }
.tag {
  font-size: .75rem; border-radius: 999px; padding: 3px 10px;
  background: var(--bg-secondary); border: 1px solid var(--border-primary); color: var(--text-secondary);
}
.tag b { font-weight: 600; color: var(--text-primary); }
.statusmark { font-size: .75rem; font-weight: 600; border-radius: 999px; padding: 3px 10px; border: 1px solid; }
.st-neu  { background: var(--bg-secondary); border-color: var(--border-primary); color: var(--text-secondary); }
.st-ent  { background: var(--ok-bg);   border-color: var(--ok-br);   color: var(--ok-tx); }
.st-off  { background: var(--open-bg); border-color: var(--open-br); color: var(--open-tx); }

.fall-koerper { padding: 18px 24px 22px; }
.block { margin-bottom: 20px; }
.block:last-child { margin-bottom: 0; }

/* Belege */
.belege { border: 1px solid var(--border-primary); border-radius: 14px; overflow: hidden; }
.beleg { padding: 13px 16px; border-bottom: 1px solid var(--border-primary); }
.beleg:last-child { border-bottom: 0; }
.beleg-kopf {
  font-size: .78rem; color: var(--text-secondary);
  display: flex; flex-wrap: wrap; gap: 4px 14px; margin-bottom: 7px;
}
.beleg-kopf .werk { font-weight: 600; color: var(--text-primary); }
.zitat { font-family: Georgia, "Times New Roman", serif; font-size: 1.06rem; line-height: 1.75; }
.zitat .z { display: block; }
.zitat .z.neben { color: var(--text-secondary); }
.zitat .vnr {
  display: inline-block; min-width: 3.6em; margin-right: .5em;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: .72rem; color: var(--text-secondary); text-align: right; user-select: none;
}
.zitat mark { background: var(--mark-bg); color: var(--mark-tx); font-weight: 600; padding: 0 2px; border-radius: 3px; }
.beleg-mehr { padding: 10px 16px; font-size: .82rem; color: var(--text-secondary); background: var(--bg-secondary); }

/* Vorschlag */
.vorschlag { border: 1px solid var(--info-br); background: var(--info-bg); border-radius: 14px; padding: 15px 17px; }
.vorschlag .eyebrow { color: var(--info-tx); display: flex; align-items: center; gap: 6px; }
.vorschlag .eyebrow svg { width: 15px; height: 15px; }
.vorschlag p { margin: 0 0 9px; }
.vorschlag p:last-child { margin-bottom: 0; }
.vorschlag .satz { font-weight: 600; }
.vorschlag .unsicher { font-size: .88rem; color: var(--info-tx); }
.kein-vorschlag { border: 1px dashed var(--border-primary); background: var(--bg-secondary); border-radius: 14px; padding: 15px 17px; color: var(--text-secondary); }
.kein-vorschlag .eyebrow { color: var(--text-secondary); }

/* Antwort */
.optionen { display: grid; gap: 7px; }
.opt {
  display: flex; gap: 10px; align-items: flex-start;
  border: 1px solid var(--border-primary); border-radius: 12px; padding: 10px 13px;
  cursor: pointer; background: var(--bg-primary);
}
.opt:hover { border-color: var(--brand-200); background: var(--brand-50); }
.opt input { margin: 3px 0 0; accent-color: var(--accent-primary); flex: none; }
.opt span { font-size: .94rem; }
.opt.gewaehlt { border-color: var(--brand-500); background: var(--brand-50); }
details.mehr { margin-top: 7px; }
details.mehr > summary { cursor: pointer; font-size: .85rem; font-weight: 600; color: var(--brand-600); list-style: none; padding: 5px 0; }
details.mehr > summary::-webkit-details-marker { display: none; }
details.mehr > summary::before { content: "+ "; }
details[open].mehr > summary::before { content: "\2212 "; }
.freitext { margin-top: 8px; }
.freitext input { width: 100%; }

textarea.komm { width: 100%; resize: vertical; min-height: 5.6em; line-height: 1.5; }

.stand-wahl { display: flex; flex-wrap: wrap; gap: 7px; }
.stand-wahl button {
  font: inherit; font-size: .84rem; font-weight: 600; cursor: pointer;
  border-radius: 10px; padding: 7px 13px;
  background: var(--bg-primary); color: var(--text-secondary); border: 1px solid var(--border-primary);
}
.stand-wahl button[aria-pressed="true"].w-ent { background: var(--ok-bg);   border-color: var(--ok-br);   color: var(--ok-tx); }
.stand-wahl button[aria-pressed="true"].w-off { background: var(--open-bg); border-color: var(--open-br); color: var(--open-tx); }
.stand-wahl button[aria-pressed="true"].w-neu { background: var(--bg-secondary); border-color: var(--text-secondary); color: var(--text-primary); }

.leer { border: 1px dashed var(--border-primary); background: var(--bg-secondary); border-radius: 16px; padding: 26px; text-align: center; color: var(--text-secondary); }

footer.page { margin-top: 40px; padding-top: 18px; border-top: 1px solid var(--border-primary); font-size: .84rem; color: var(--text-secondary); }
footer.page p { margin: 0 0 6px; }

@media print {
  .bar, .filters, .stand-wahl, .btn { display: none !important; }
  .fall { break-inside: avoid; box-shadow: none; }
}
@media (max-width: 720px) {
  .wrap { padding: 0 16px 72px; }
  .bar-inner { padding: 10px 16px; }
}
"""

JS = r"""
(function () {
  "use strict";
  var DATEN = window.__PRUEFDATEN__;
  var SCHLUESSEL = "pruefseite:" + DATEN.kennung;
  var STAENDE = ["unbearbeitet", "entschieden", "offen"];

  var zustand = { name: "", faelle: {}, gespeichert: null };

  function leer(fallId) { return { antwort: null, frei: "", kommentar: "", stand: "unbearbeitet" }; }
  function fall(id) {
    if (!zustand.faelle[id]) { zustand.faelle[id] = leer(id); }
    return zustand.faelle[id];
  }

  /* Speichern: der Browser ist der Ablageort, der Export der Weitergabeweg.
     Jeder Zugriff in try/catch, weil localStorage im privaten Fenster wirft. */
  function laden() {
    try {
      var roh = window.localStorage.getItem(SCHLUESSEL);
      if (!roh) { return; }
      var d = JSON.parse(roh);
      if (d && typeof d === "object") {
        zustand.name = typeof d.name === "string" ? d.name : "";
        zustand.faelle = (d.faelle && typeof d.faelle === "object") ? d.faelle : {};
        zustand.gespeichert = d.gespeichert || null;
      }
    } catch (e) { /* kein Speicher: die Seite funktioniert trotzdem */ }
  }
  var speicherTimer = null;
  function speichern() {
    zustand.gespeichert = new Date().toISOString();
    try {
      window.localStorage.setItem(SCHLUESSEL, JSON.stringify({
        name: zustand.name, faelle: zustand.faelle, gespeichert: zustand.gespeichert
      }));
      flagge("ok");
    } catch (e) { flagge("fehlt"); }
  }
  function speichernGleich() {
    if (speicherTimer) { window.clearTimeout(speicherTimer); }
    speicherTimer = window.setTimeout(speichern, 350);
  }
  /* Drei Zustaende, nicht zwei. "noch nichts gespeichert" ist der normale
     Anfang und darf nicht aussehen wie "der Browser speichert nicht": die
     zweite Meldung ist eine Warnung und wuerde beim ersten Oeffnen jedem
     Nutzer erscheinen, der noch nichts getan hat. */
  function flagge(stand) {
    var el = document.getElementById("saveflag");
    if (!el) { return; }
    el.className = "saveflag" + (stand === "ok" ? " on" : "");
    el.querySelector("span").textContent =
        stand === "ok"    ? "im Browser gespeichert " + uhrzeit(zustand.gespeichert)
      : stand === "fehlt" ? "Browser speichert nicht, bitte exportieren"
      :                     "noch nichts eingetragen";
  }
  /* Kann der Browser ueberhaupt speichern? Unter file:// gibt es Chrome-
     Einstellungen, in denen das fehlschlaegt, und dann muss die Seite es
     sagen, statt es beim ersten Klick zu merken. */
  function speicherProbe() {
    try {
      window.localStorage.setItem(SCHLUESSEL + ":probe", "1");
      window.localStorage.removeItem(SCHLUESSEL + ":probe");
      return true;
    } catch (e) { return false; }
  }
  function uhrzeit(iso) {
    if (!iso) { return ""; }
    var d = new Date(iso);
    return ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
  }

  function zaehle() {
    var n = { unbearbeitet: 0, entschieden: 0, offen: 0 };
    DATEN.faelle.forEach(function (f) {
      var s = (zustand.faelle[f.id] && zustand.faelle[f.id].stand) || "unbearbeitet";
      if (STAENDE.indexOf(s) < 0) { s = "unbearbeitet"; }
      n[s] += 1;
    });
    return n;
  }
  function fortschritt() {
    var n = zaehle(), g = DATEN.faelle.length;
    var t = document.getElementById("fortschritt-text");
    document.getElementById("seg-done").style.width = (100 * n.entschieden / g) + "%";
    document.getElementById("seg-open").style.width = (100 * n.offen / g) + "%";
    t.textContent = n.entschieden + " entschieden, " + n.offen + " geprüft und offen, "
                  + n.unbearbeitet + " unbearbeitet, von " + g;
  }

  var filter = "alle";
  function anwenden() {
    var sichtbar = 0;
    DATEN.faelle.forEach(function (f) {
      var el = document.getElementById("fall-" + f.id);
      if (!el) { return; }
      var s = (zustand.faelle[f.id] && zustand.faelle[f.id].stand) || "unbearbeitet";
      var zeig = (filter === "alle") || (filter === s);
      el.hidden = !zeig;
      if (zeig) { sichtbar += 1; }
    });
    document.querySelectorAll("section.gruppe").forEach(function (sec) {
      var offen = sec.querySelectorAll(".fall:not([hidden])").length;
      sec.hidden = offen === 0;
    });
    document.getElementById("nichts").hidden = sichtbar !== 0;
  }

  function markiere(id) {
    var z = fall(id);
    var el = document.getElementById("fall-" + id);
    if (!el) { return; }
    el.setAttribute("data-status", z.stand);
    var m = el.querySelector(".statusmark");
    m.className = "statusmark " + (z.stand === "entschieden" ? "st-ent" : z.stand === "offen" ? "st-off" : "st-neu");
    m.textContent = z.stand === "entschieden" ? "entschieden"
                  : z.stand === "offen" ? "geprüft, bleibt offen" : "unbearbeitet";
    el.querySelectorAll(".stand-wahl button").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-stand") === z.stand));
    });
    el.querySelectorAll(".opt").forEach(function (o) {
      var inp = o.querySelector("input");
      o.classList.toggle("gewaehlt", inp.checked);
    });
  }

  function verdrahte(f) {
    var el = document.getElementById("fall-" + f.id);
    if (!el) { return; }
    var z = fall(f.id);

    el.querySelectorAll('input[type="radio"]').forEach(function (inp) {
      if (z.antwort !== null && inp.value === z.antwort) { inp.checked = true; }
      inp.addEventListener("change", function () {
        z.antwort = inp.value;
        /* Die Antwort setzt den Stand auf "entschieden", wenn er noch
           unbearbeitet war. Einen bereits gesetzten Stand ueberschreibt sie
           nicht: wer "geprueft, bleibt offen" gewaehlt und dazu eine Tendenz
           angekreuzt hat, meint beides. */
        if (z.stand === "unbearbeitet") { z.stand = "entschieden"; }
        markiere(f.id); fortschritt(); anwenden(); speichernGleich();
      });
    });

    var frei = el.querySelector(".freitext input");
    if (frei) {
      frei.value = z.frei || "";
      frei.addEventListener("input", function () { z.frei = frei.value; speichernGleich(); });
    }

    var komm = el.querySelector("textarea.komm");
    komm.value = z.kommentar || "";
    komm.addEventListener("input", function () { z.kommentar = komm.value; speichernGleich(); });

    el.querySelectorAll(".stand-wahl button").forEach(function (b) {
      b.addEventListener("click", function () {
        z.stand = b.getAttribute("data-stand");
        markiere(f.id); fortschritt(); anwenden(); speichernGleich();
      });
    });

    markiere(f.id);
  }

  /* Weitergeben. Der Export traegt Name, Antworten, Kommentare und Staende,
     dazu die Kennung der Seite: ein Import in eine andere Seite waere ein
     stiller Datenverlust und wird abgelehnt. */
  function exportDaten() {
    return {
      format: "mhdbdb-pruefseite",
      formatVersion: DATEN.formatVersion,
      kennung: DATEN.kennung,
      vorgang: DATEN.vorgang,
      datenstand: DATEN.datenstand,
      bearbeiterin: zustand.name,
      exportiert: new Date().toISOString(),
      antworten: DATEN.faelle.map(function (f) {
        var z = zustand.faelle[f.id] || leer(f.id);
        return {
          id: f.id, gruppe: f.gruppe, kopf: f.kopfText, frage: f.frage,
          vorschlag: f.vorschlagText || null,
          stand: z.stand, antwort: z.antwort, freieAntwort: z.frei || "", kommentar: z.kommentar || ""
        };
      })
    };
  }
  function hole(name, typ, text) {
    var b = new Blob([text], { type: typ + ";charset=utf-8" });
    var u = URL.createObjectURL(b);
    var a = document.createElement("a");
    a.href = u; a.download = name;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    window.setTimeout(function () { URL.revokeObjectURL(u); }, 2000);
  }
  function dateiname(endung) {
    var n = (zustand.name || "ohne-namen").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    return DATEN.kennung + "_" + (n || "ohne-namen") + "." + endung;
  }
  function esc(s) {
    return String(s === null || s === undefined ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  function bericht() {
    var d = exportDaten(), n = zaehle();
    var zeilen = d.antworten.map(function (a) {
      var f = DATEN.faelle.filter(function (x) { return x.id === a.id; })[0] || {};
      return "<article><h3>" + esc(a.kopf) + " <em>" + esc(a.stand) + "</em></h3>"
        + "<p class='q'>" + esc(a.frage) + "</p>"
        + (f.belegHtml ? "<div class='b'>" + f.belegHtml + "</div>" : "")
        + "<p><b>Maschinenvorschlag:</b> " + esc(a.vorschlag || "keiner") + "</p>"
        + "<p><b>Antwort:</b> " + esc(a.antwort || "keine")
        + (a.freieAntwort ? " <i>(" + esc(a.freieAntwort) + ")</i>" : "") + "</p>"
        + "<p><b>Kommentar:</b> " + (a.kommentar ? esc(a.kommentar) : "<i>keiner</i>") + "</p></article>";
    }).join("\n");
    return "<!DOCTYPE html>\n<html lang=\"de\"><head><meta charset=\"utf-8\">"
      + "<title>Ergebnisbericht " + esc(DATEN.titel) + "</title><style>"
      + "body{font-family:ui-sans-serif,system-ui,sans-serif;max-width:56rem;margin:2rem auto;padding:0 1.5rem;color:#1f2937;line-height:1.55}"
      + "h1{font-size:1.6rem}article{border:1px solid #e2e8f0;border-radius:14px;padding:1rem 1.2rem;margin:0 0 1rem}"
      + "h3{margin:0 0 .3rem;font-size:1.05rem}h3 em{font-weight:500;font-style:normal;color:#64748b;font-size:.85rem}"
      + ".q{font-weight:600;margin:.2rem 0 .6rem}.b{font-family:Georgia,serif;background:#f8fafc;border-radius:10px;padding:.6rem .8rem;margin:0 0 .7rem;font-size:.95rem}"
      + ".b mark{background:#fbbf24;color:#78350f}p{margin:.3rem 0}"
      + "</style></head><body><h1>Ergebnisbericht: " + esc(DATEN.titel) + "</h1>"
      + "<p>Vorgang " + esc(DATEN.vorgang) + ". Bearbeiterin oder Bearbeiter: <b>"
      + esc(d.bearbeiterin || "nicht angegeben") + "</b>. Erzeugt am "
      + esc(new Date().toLocaleString("de-AT")) + ".</p>"
      + "<p>" + n.entschieden + " entschieden, " + n.offen + " geprüft und offen, "
      + n.unbearbeitet + " unbearbeitet, von " + DATEN.faelle.length + ".</p>"
      + "<p>Datenstand: " + esc(DATEN.datenstand.map(function (p) { return p[0] + ": " + p[1]; }).join(" &middot; ")) + "</p>"
      + zeilen + "</body></html>";
  }

  function importieren(datei) {
    var leser = new FileReader();
    leser.onload = function () {
      var d;
      try { d = JSON.parse(String(leser.result)); }
      catch (e) { window.alert("Die Datei ist kein gültiges JSON."); return; }
      if (!d || d.format !== "mhdbdb-pruefseite") {
        window.alert("Das ist kein Export einer Prüfseite."); return;
      }
      if (d.kennung !== DATEN.kennung) {
        window.alert("Dieser Export gehört zu einer anderen Prüfseite (" + d.kennung
          + "). Er wird nicht eingelesen, damit nichts still verlorengeht.");
        return;
      }
      var neu = {};
      (d.antworten || []).forEach(function (a) {
        if (!a || !a.id) { return; }
        neu[a.id] = {
          antwort: a.antwort || null, frei: a.freieAntwort || "",
          kommentar: a.kommentar || "",
          stand: STAENDE.indexOf(a.stand) >= 0 ? a.stand : "unbearbeitet"
        };
      });
      /* Gezaehlt wird, was BEARBEITET ist, auf beiden Seiten. Die Zahl der
         Eintraege sagt nichts: der Export schreibt jeden Fall der Seite, auch
         den unberuehrten, also waeren es immer alle 45, und eine Meldung, die
         immer dasselbe sagt, ist keine. Und was hier stand, wird ersetzt: das
         gehoert in die Meldung, sonst merkt niemand, dass eine halbe Stunde
         Arbeit weg ist. */
      function bearbeitet(z) {
        return !!(z && (z.antwort || z.kommentar || z.frei
                        || (z.stand && z.stand !== "unbearbeitet")));
      }
      var ausDatei = 0;
      Object.keys(neu).forEach(function (k) { if (bearbeitet(neu[k])) { ausDatei += 1; } });
      var vorher = 0;
      Object.keys(zustand.faelle).forEach(function (k) {
        if (bearbeitet(zustand.faelle[k])) { vorher += 1; }
      });
      zustand.faelle = neu;
      zustand.name = d.bearbeiterin || zustand.name;
      document.getElementById("name").value = zustand.name;
      DATEN.faelle.forEach(function (f) {
        var el = document.getElementById("fall-" + f.id);
        if (!el) { return; }
        var z = fall(f.id);
        el.querySelectorAll('input[type="radio"]').forEach(function (i) { i.checked = (i.value === z.antwort); });
        var fr = el.querySelector(".freitext input"); if (fr) { fr.value = z.frei || ""; }
        el.querySelector("textarea.komm").value = z.kommentar || "";
        markiere(f.id);
      });
      fortschritt(); anwenden(); speichern();
      window.alert("Eingelesen: " + ausDatei
        + (ausDatei === 1 ? " bearbeiteter Fall" : " bearbeitete Fälle") + " aus der Datei."
        + (vorher > 0
            ? "\n\nDamit ist ersetzt, was vorher in diesem Browser stand ("
              + vorher + (vorher === 1 ? " bearbeiteter Fall" : " bearbeitete Fälle") + ")."
            : ""));
    };
    leser.readAsText(datei, "utf-8");
  }

  function thema(wert) {
    document.documentElement.setAttribute("data-theme", wert);
    try { window.localStorage.setItem(SCHLUESSEL + ":thema", wert); } catch (e) { /* egal */ }
    document.getElementById("thema").setAttribute("aria-pressed", String(wert === "dark"));
  }

  document.addEventListener("DOMContentLoaded", function () {
    laden();
    var t = "light";
    try { t = window.localStorage.getItem(SCHLUESSEL + ":thema") || "light"; } catch (e) { /* egal */ }
    thema(t === "dark" ? "dark" : "light");

    var nameFeld = document.getElementById("name");
    nameFeld.value = zustand.name;
    nameFeld.addEventListener("input", function () { zustand.name = nameFeld.value; speichernGleich(); });

    DATEN.faelle.forEach(verdrahte);
    fortschritt();
    flagge(!speicherProbe() ? "fehlt" : (zustand.gespeichert ? "ok" : "leer"));

    document.querySelectorAll(".chip[data-filter]").forEach(function (c) {
      c.addEventListener("click", function () {
        filter = c.getAttribute("data-filter");
        document.querySelectorAll(".chip[data-filter]").forEach(function (o) {
          o.setAttribute("aria-pressed", String(o === c));
        });
        anwenden();
      });
    });
    anwenden();

    document.getElementById("export-json").addEventListener("click", function () {
      hole(dateiname("json"), "application/json", JSON.stringify(exportDaten(), null, 2));
    });
    document.getElementById("export-html").addEventListener("click", function () {
      hole(dateiname("bericht.html"), "text/html", bericht());
    });
    document.getElementById("import").addEventListener("change", function (e) {
      if (e.target.files && e.target.files[0]) { importieren(e.target.files[0]); }
      e.target.value = "";
    });
    document.getElementById("thema").addEventListener("click", function () {
      thema(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });
  });
})();
"""

# Heroicons, outline, 24x24. Der einzige Icon-Stil des Projekts.
ICONS = {
    'check': '<path d="M4.5 12.75l6 6 9-13.5"/>',
    'download': '<path d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/>',
    'upload': '<path d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M7.5 7.5L12 3m0 0l4.5 4.5M12 3v13.5"/>',
    'sparkles': ('<path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 '
                 '003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z"/>'),
    'moon': '<path d="M21.752 15.002A9.72 9.72 0 0118 15.75 9.75 9.75 0 018.25 6c0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z"/>',
}


def icon(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % ICONS[name])


def e(text):
    return html.escape('' if text is None else str(text), quote=True)


def _json_inline(daten):
    """JSON fuer ein <script>-Element.

    `</` wird maskiert: eine Zeichenfolge wie `</script>` in einem Belegtext
    wuerde das Element sonst schliessen und die Seite zerlegen. Das ist kein
    hypothetischer Fall, sondern der Grund, warum Daten in HTML immer so
    eingebettet werden.
    """
    roh = json.dumps(daten, ensure_ascii=False)
    return roh.replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def _beleg_html(b):
    """Ein Beleg als Zitat: Zeilen davor, Trefferzeile, Zeilen danach."""
    teile = []
    for z in b.get('zeilen_davor', []):
        teile.append('<span class="z neben">%s%s</span>'
                     % (_vnr(z.get('n')), e(z.get('text'))))
    teile.append('<span class="z">%s%s<mark>%s</mark>%s</span>' % (
        _vnr(b.get('zeile_n')),
        (e(b.get('treffer_davor')) + ' ') if b.get('treffer_davor') else '',
        e(b.get('treffer')),
        (' ' + e(b.get('treffer_danach'))) if b.get('treffer_danach') else '',
    ))
    for z in b.get('zeilen_danach', []):
        teile.append('<span class="z neben">%s%s</span>'
                     % (_vnr(z.get('n')), e(z.get('text'))))
    return '<div class="zitat">%s</div>' % ''.join(teile)


def _vnr(n):
    return '<span class="vnr">%s</span>' % (e(n) if n else '')


def _optionen(fall):
    """Antwortblock: sichtbare Optionen, aufklappbare weitere, freie Antwort.

    Alans erster Punkt: die Auswahl passt zum Fall. Deshalb bringt jeder Fall
    seine eigenen Optionen mit, statt dass die Seite eine Liste fuer alle
    fuehrt. Die freie Antwort steht immer da und haengt an keiner Option.
    """
    def zeile(i, text):
        return ('<label class="opt"><input type="radio" name="a-%s" value="%s">'
                '<span>%s</span></label>' % (e(fall['id']), e(text), e(text)))

    sicht = fall['optionen'][:fall.get('sichtbar', 4)]
    rest = fall['optionen'][fall.get('sichtbar', 4):]
    html_teile = ['<div class="optionen">%s</div>' % ''.join(
        zeile(i, t) for i, t in enumerate(sicht))]
    if rest:
        html_teile.append(
            '<details class="mehr"><summary>weitere Antwortmöglichkeiten (%d)</summary>'
            '<div class="optionen" style="margin-top:7px">%s</div></details>'
            % (len(rest), ''.join(zeile(i, t) for i, t in enumerate(rest))))
    html_teile.append(
        '<label class="opt freitext" style="display:block"><span>Andere Antwort</span>'
        '<input type="text" placeholder="eigene Formulierung, auch neben einer gewählten Option"></label>')
    return ''.join(html_teile)


def _vorschlag_html(v):
    if v is None:
        return ('<div class="kein-vorschlag"><p class="eyebrow">Kein Maschinenvorschlag</p>'
                '<p>Zu diesem Fall gibt es keinen Vorschlag. Die Begründung steht darüber: '
                'entweder tragen die Belegstellen keinen, oder es gibt keine.</p></div>')
    teile = ['<div class="vorschlag"><p class="eyebrow">%s Maschinenvorschlag, keine Entscheidung</p>' % icon('sparkles')]
    teile.append('<p class="satz">%s</p>' % v['text'])
    if v.get('begruendung'):
        teile.append('<p>%s</p>' % v['begruendung'])
    if v.get('unsicherheit'):
        teile.append('<p class="unsicher"><b>Unsicherheit:</b> %s</p>' % v['unsicherheit'])
    teile.append('</div>')
    return ''.join(teile)


def _fall_html(f):
    merkmale = ''.join('<span class="tag"><b>%s</b> %s</span>' % (e(k), e(v))
                       for k, v in f.get('merkmale', []))
    belege = ''.join('<div class="beleg"><div class="beleg-kopf">'
                     '<span class="werk">%s</span><span>%s</span><span class="mono">%s</span>%s</div>%s</div>'
                     % (e(b['werk']), e(b['fundstelle']), e(b['xml_id']),
                        ('<span>%s</span>' % e(b['wortart'])) if b.get('wortart') else '',
                        _beleg_html(b))
                     for b in f['belege'])
    if not f['belege']:
        belege = ('<div class="beleg"><p style="margin:0;color:var(--text-secondary)">'
                  'Für diesen Fall gibt es im Korpus keinen einzigen Beleg.</p></div>')
    mehr = ('<div class="beleg-mehr">%s</div>' % f['beleg_hinweis']) if f.get('beleg_hinweis') else ''

    return """
<article class="fall" id="fall-%(id)s" data-status="unbearbeitet">
  <div class="fall-kopf">
    <h3><span class="form">%(kopf)s</span></h3>
    <p class="fall-frage">%(frage)s</p>
    <div class="merkmale">%(merkmale)s<span class="statusmark st-neu">unbearbeitet</span></div>
  </div>
  <div class="fall-koerper">
    <div class="block">
      <p class="eyebrow">Belegstellen</p>
      <div class="belege">%(belege)s%(mehr)s</div>
    </div>
    <div class="block">%(vorschlag)s</div>
    <div class="block">
      <p class="eyebrow">Ihre Antwort</p>
      %(optionen)s
    </div>
    <div class="block">
      <p class="eyebrow"><label for="k-%(id)s">Kommentar</label></p>
      <textarea class="komm" id="k-%(id)s" rows="4"
        placeholder="Freier Text. Bleibt erhalten, egal welche Antwort gewählt ist, und steht im Export."></textarea>
    </div>
    <div class="block">
      <p class="eyebrow">Bearbeitungsstand</p>
      <div class="stand-wahl">
        <button type="button" class="w-neu" data-stand="unbearbeitet" aria-pressed="true">unbearbeitet</button>
        <button type="button" class="w-ent" data-stand="entschieden" aria-pressed="false">entschieden</button>
        <button type="button" class="w-off" data-stand="offen" aria-pressed="false">geprüft, bleibt offen</button>
      </div>
    </div>
  </div>
</article>""" % dict(
        id=e(f['id']), kopf=e(f['kopf']), frage=e(f['frage']), merkmale=merkmale,
        belege=belege, mehr=mehr, vorschlag=_vorschlag_html(f.get('vorschlag')),
        optionen=_optionen(f))


# Die Prosafelder der Spec sind HTML und werden nicht escaped. Der Generator
# ist fuer beides zustaendig: escapen, was Text ist, und auszeichnen, was
# Auszeichnung braucht. Diese Liste sagt, welche Felder das betrifft, und
# `_rohe_auszeichnung` haelt die Zusage nach.
HTML_FELDER = ('frage', 'beleg_hinweis')
HTML_FELDER_VORSCHLAG = ('text', 'begruendung', 'unsicherheit')


def _rohe_auszeichnung(spec):
    """Ein Rueckwaertsstrich in einem HTML-Feld heisst: hier fehlt `markup()`.

    Anlass ist Runde 1 zu #443/#359: `kurz`, `vorschlag.text`,
    `vorschlag.unsicherheit` und `beleg_hinweis` gingen durch `e()` statt durch
    die Auszeichnung des Generators, und in der fertigen Seite standen an 21
    Stellen Rueckwaertsstriche im sichtbaren Text. Das faellt beim Bauen nicht
    auf, weil die Nachbarfelder daneben richtig gesetzt sind.

    Die Pruefung ist bewusst stumpf: sie versteht die Auszeichnung nicht, sie
    verlangt nur, dass keine Markdown-Reste uebrig sind. Wer einen
    Rueckwaertsstrich als Zeichen meint, schreibt ihn als `&#96;`.

    Sie sieht nur die Felder, die dieses Modul selbst rendert. Ein Generator,
    der `_fall_html` ersetzt und eigene Bloecke einhaengt, prueft sein
    Ergebnis selbst; `build-359-page.py` tut das am fertigen Dokument.
    """
    fundstellen = []
    for f in spec.get('faelle', []):
        for feld in HTML_FELDER:
            if '`' in (f.get(feld) or ''):
                fundstellen.append('Fall %s, Feld %s' % (f.get('id', '?'), feld))
        v = f.get('vorschlag')
        if isinstance(v, dict):
            for feld in HTML_FELDER_VORSCHLAG:
                if '`' in (v.get(feld) or ''):
                    fundstellen.append('Fall %s, vorschlag.%s' % (f.get('id', '?'), feld))
    for g in spec.get('gruppen', []):
        if '`' in (g.get('beschreibung') or ''):
            fundstellen.append('Gruppe %s, Beschreibung' % g.get('id', '?'))
    for p in spec.get('anleitung', []):
        if '`' in p:
            fundstellen.append('Anleitung')
    return fundstellen


def render(spec):
    """Die fertige Seite als ein einziger HTML-String.

    `spec` ist der ganze Vertrag dieses Formats. Fehlt ein Pflichtfeld, ist das
    ein harter Fehler: eine Pruefseite ohne Datenstand oder ohne Vorgang ist
    genau die Seite, deren Herkunft spaeter niemand mehr feststellen kann.
    """
    for feld in ('kennung', 'titel', 'untertitel', 'vorgang', 'datenstand', 'anleitung', 'gruppen', 'faelle'):
        if feld not in spec:
            raise ValueError('spec fehlt das Pflichtfeld: %s' % feld)
    if not spec['faelle']:
        raise ValueError('spec enthaelt keinen einzigen Fall')

    ids = [f['id'] for f in spec['faelle']]
    doppelt = sorted({i for i in ids if ids.count(i) > 1})
    if doppelt:
        raise ValueError('doppelte Fall-IDs: %s' % ', '.join(doppelt))

    roh = _rohe_auszeichnung(spec)
    if roh:
        raise ValueError(
            'Rueckwaertsstriche in einem HTML-Feld, hier fehlt die Auszeichnung:\n  '
            + '\n  '.join(roh))

    gruppen_html = []
    for g in spec['gruppen']:
        drin = [f for f in spec['faelle'] if f['gruppe'] == g['id']]
        if not drin:
            continue
        gruppen_html.append(
            '<section class="gruppe" id="g-%s"><h2>%s</h2><p class="gruppe-text">%s</p>%s</section>'
            % (e(g['id']), e(g['titel']), g['beschreibung'],
               ''.join(_fall_html(f) for f in drin)))

    stand_html = ''.join('<dt>%s</dt><dd>%s</dd>' % (e(k), e(v)) for k, v in spec['datenstand'])
    anleitung_html = ''.join('<p>%s</p>' % p for p in spec['anleitung'])

    daten = dict(
        kennung=spec['kennung'],
        titel=spec['titel'],
        vorgang=spec['vorgang'],
        datenstand=[[k, v] for k, v in spec['datenstand']],
        formatVersion=FORMAT_VERSION,
        faelle=[dict(
            id=f['id'], gruppe=f['gruppe'], kopfText=f['kopf'], frage=f['frage'],
            vorschlagText=(f['vorschlag']['text'] if f.get('vorschlag') else None),
            belegHtml=(_beleg_html(f['belege'][0]) if f['belege'] else ''),
        ) for f in spec['faelle']],
    )

    return """<!DOCTYPE html>
<html lang="de" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(titel)s</title>
<meta name="generator" content="mhdbdb review_page.py %(fv)s">
<style>%(css)s</style>
</head>
<body>
<div class="bar">
  <div class="bar-inner">
    <div class="bar-title">%(titel)s<span>Vorgang %(vorgang)s</span></div>
    <div class="field">
      <label for="name">Name</label>
      <input type="text" id="name" placeholder="wer prüft" autocomplete="name" size="18">
    </div>
    <div class="progress">
      <div class="progress-track">
        <i class="seg-done" id="seg-done" style="width:0"></i>
        <i class="seg-open" id="seg-open" style="width:0"></i>
      </div>
      <div class="progress-text" id="fortschritt-text"></div>
    </div>
    <button type="button" class="btn" id="export-json">%(ic_dl)s JSON</button>
    <button type="button" class="btn" id="export-html">%(ic_dl)s Bericht</button>
    <label class="btn btn-plain" for="import">%(ic_up)s Import
      <input type="file" id="import" accept="application/json,.json" hidden></label>
    <button type="button" class="btn btn-plain" id="thema" aria-pressed="false" title="Dunkelmodus">%(ic_moon)s</button>
    <span class="saveflag" id="saveflag">%(ic_check)s<span></span></span>
  </div>
</div>

<div class="wrap">
<header class="page">
  <h1>%(titel)s</h1>
  <p class="sub">%(untertitel)s</p>

  <div class="panel">
    <h2>So wird geprüft</h2>
    %(anleitung)s
  </div>

  %(vorab)s

  <div class="panel">
    <p class="eyebrow">Datenstand</p>
    <dl class="stand">%(stand)s</dl>
  </div>
</header>

<div class="filters">
  <span class="eyebrow" style="margin:0 4px 0 0">Anzeigen</span>
  <button type="button" class="chip" data-filter="alle" aria-pressed="true">alle</button>
  <button type="button" class="chip" data-filter="unbearbeitet" aria-pressed="false">unbearbeitet</button>
  <button type="button" class="chip" data-filter="entschieden" aria-pressed="false">entschieden</button>
  <button type="button" class="chip" data-filter="offen" aria-pressed="false">geprüft, bleibt offen</button>
</div>

%(gruppen)s

<div class="leer" id="nichts" hidden>In dieser Ansicht steht kein Fall. Wählen Sie oben einen anderen Filter.</div>

<footer class="page">
  %(fuss)s
</footer>
</div>

<script>window.__PRUEFDATEN__ = %(daten)s;</script>
<script>%(js)s</script>
</body>
</html>
""" % dict(
        titel=e(spec['titel']), untertitel=spec['untertitel'], vorgang=e(spec['vorgang']),
        anleitung=anleitung_html, stand=stand_html, gruppen='\n'.join(gruppen_html),
        vorab=spec.get('vorab', ''),
        fuss=spec.get('fuss', ''), css=CSS, js=JS, daten=_json_inline(daten),
        fv=FORMAT_VERSION, ic_dl=icon('download'), ic_up=icon('upload'),
        ic_moon=icon('moon'), ic_check=icon('check'),
    )
