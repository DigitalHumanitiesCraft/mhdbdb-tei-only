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

  /* Zwei Faltungen: ohne Akzente ("Wurzburg") und mit deutscher Umschrift ("Wuerzburg"). */
  function normalize(s) {
    return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ß/g, 'ss');
  }
  function translit(s) {
    return s.toLowerCase().replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
      .normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  var tags = {};
  entries.forEach(function (e) {
    var all = e.textContent + ' ' + (e.getAttribute('data-tags') || '').replace(/\|/g, ' ');
    e._text = normalize(all) + '\u0001' + translit(all);
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
    var raw = query.value.trim();
    var variants = raw ? [normalize(raw)] : [];
    if (raw && translit(raw) !== variants[0]) variants.push(translit(raw));
    var tag = tagSel.value;
    var shown = 0;
    entries.forEach(function (e) {
      var textOk = !variants.length || variants.some(function (v) { return e._text.indexOf(v) !== -1; });
      var ok = textOk && (!tag || e._tags.indexOf(tag) !== -1);
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
