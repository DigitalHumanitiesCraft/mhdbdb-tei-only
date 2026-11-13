/**
 * Filter der Hilfe-Unterseite "Publikationen" (#417).
 *
 * Rein clientseitig: jeder Eintrag der Liste trägt data-jahr (leer ohne Jahr) und
 * data-team (IDs aus authority-files/contributors.xml, durch Leerzeichen getrennt),
 * beide von scripts/build-publikationen.py gesetzt. Das Formular steht per `hidden`
 * im HTML und wird erst hier eingeblendet: ohne Skript bleibt die ganze Liste sichtbar.
 */
(function () {
    'use strict';

    var form = document.getElementById('pub-filter');
    if (!form) return;

    var team = document.getElementById('pub-team');
    var von = document.getElementById('pub-von');
    var bis = document.getElementById('pub-bis');
    var zurueck = document.getElementById('pub-zurueck');
    var status = document.getElementById('pub-status');
    var abschnitte = Array.prototype.slice.call(document.querySelectorAll('section[id] > .pub-liste')).map(function (liste) {
        return {
            liste: liste,
            anzahl: liste.parentNode.querySelector('.pub-anzahl'),
            eintraege: Array.prototype.slice.call(liste.querySelectorAll('li[data-jahr]')),
            leer: null
        };
    });

    function zahl(feld) {
        var n = parseInt(feld.value, 10);
        return isNaN(n) ? null : n;
    }

    function anwenden() {
        var t = team.value;
        var v = zahl(von);
        var b = zahl(bis);
        var gefiltert = t !== '' || v !== null || b !== null;
        var sichtbar = 0;
        var gesamt = 0;

        abschnitte.forEach(function (a) {
            var treffer = 0;
            a.eintraege.forEach(function (li) {
                var jahr = li.getAttribute('data-jahr');
                var j = jahr === '' ? null : parseInt(jahr, 10);
                var ok = true;
                if (t !== '' && (' ' + li.getAttribute('data-team') + ' ').indexOf(' ' + t + ' ') < 0) ok = false;
                if ((v !== null || b !== null) && j === null) ok = false;
                if (v !== null && j !== null && j < v) ok = false;
                if (b !== null && j !== null && j > b) ok = false;
                li.hidden = !ok;
                if (ok) treffer++;
            });
            sichtbar += treffer;
            gesamt += a.eintraege.length;
            a.anzahl.textContent = gefiltert ? treffer + ' von ' + a.eintraege.length : String(a.eintraege.length);
            // Ein Abschnitt ohne Einträge trägt schon seinen eigenen pub-leer-Hinweis (Platzhalter vom Build)
            if (treffer === 0 && gefiltert && a.eintraege.length > 0) {
                if (!a.leer) {
                    a.leer = document.createElement('li');
                    a.leer.className = 'pub-leer';
                    a.leer.textContent = 'Kein Eintrag passt zu dieser Auswahl.';
                    a.liste.appendChild(a.leer);
                }
                a.leer.hidden = false;
            } else if (a.leer) {
                a.leer.hidden = true;
            }
        });

        status.textContent = gefiltert
            ? sichtbar + ' von ' + gesamt + ' Einträgen angezeigt.'
            : '';
    }

    [team, von, bis].forEach(function (feld) {
        feld.addEventListener('input', anwenden);
        feld.addEventListener('change', anwenden);
    });
    zurueck.addEventListener('click', function () {
        team.value = '';
        von.value = '';
        bis.value = '';
        anwenden();
    });

    form.hidden = false;
    anwenden();
})();
