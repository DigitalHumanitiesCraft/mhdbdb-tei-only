/* Literatursuche der Textreihentypologie (#93): filtert die statisch gebaute Bibliografie
 * (scripts/build-textreihen-bibliography.py) nach Text und Textreihen-Schlagwort.
 * Ohne JavaScript bleibt die ganze Liste sichtbar. */
(function () {
  'use strict';

  var entries = Array.prototype.slice.call(document.querySelectorAll('.tr-bib-entry'));
  var query = document.getElementById('bibQuery');
  var tagSel = document.getElementById('bibTag');
  var status = document.getElementById('bibStatus');
  if (!entries.length || !query || !tagSel) return;

  function normalize(s) {
    return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ß/g, 'ss');
  }

  var tags = {};
  entries.forEach(function (e) {
    e._text = normalize(e.textContent + ' ' + (e.getAttribute('data-tags') || '').replace(/\|/g, ' '));
    e._tags = (e.getAttribute('data-tags') || '').split('|').filter(Boolean);
    e._tags.forEach(function (t) { tags[t] = (tags[t] || 0) + 1; });
  });
  Object.keys(tags).sort(function (a, b) { return a.localeCompare(b, 'de'); }).forEach(function (t) {
    var o = document.createElement('option');
    o.value = t;
    o.textContent = t + ' (' + tags[t] + ')';
    tagSel.appendChild(o);
  });

  function apply() {
    var q = normalize(query.value.trim());
    var tag = tagSel.value;
    var shown = 0;
    entries.forEach(function (e) {
      var ok = (!q || e._text.indexOf(q) !== -1) && (!tag || e._tags.indexOf(tag) !== -1);
      e.hidden = !ok;
      if (ok) shown++;
    });
    status.textContent = shown === entries.length
      ? entries.length + ' Einträge'
      : shown + ' von ' + entries.length + ' Einträgen';
  }

  query.addEventListener('input', apply);
  tagSel.addEventListener('change', apply);
  apply();
})();
