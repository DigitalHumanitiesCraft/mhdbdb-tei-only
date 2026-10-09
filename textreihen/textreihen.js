/* SKOS-Browser der MHDBDB-Textreihentypologie (#93).
 * Laedt data/textreihen.json (gebaut von scripts/build-textreihen.py) und zeigt die
 * Hierarchie als aufklappbaren Baum. Eine Kategorie mit mehreren direkten Eltern
 * steht unter jedem dieser Eltern. Keine Laufzeit-Abhaengigkeit von dhplus.sbg.ac.at:
 * die historischen Adressen werden nur als Bezeichner angezeigt, nie als Link.
 */
(function () {
  'use strict';

  var MAX_RESULTS = 50;
  var MAX_PATHS = 24;
  var $ = function (id) { return document.getElementById(id); };

  function h(tag, attrs) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === 'class') node.className = attrs[k];
        else if (k === 'text') node.textContent = attrs[k];
        else node.setAttribute(k, attrs[k]);
      });
    }
    for (var i = 2; i < arguments.length; i++) {
      var c = arguments[i];
      if (c == null) continue;
      node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    }
    return node;
  }

  function normalize(s) {
    return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ß/g, 'ss');
  }

  var CHEVRON = '<svg class="tr-chevron" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd"/></svg>';
  var LANG_NAME = { de: 'Deutsch', en: 'Englisch', la: 'Latein', fr: 'Französisch' };

  var data, C, children, rootIds, selected = null;

  function label(id) { return C[id].l.de; }

  function buildIndex() {
    C = data.concepts;
    children = {};
    Object.keys(C).forEach(function (id) { children[id] = []; });
    Object.keys(C).forEach(function (id) {
      (C[id].p || []).forEach(function (p) { children[p].push(id); });
    });
    rootIds = Object.keys(C).filter(function (id) { return !C[id].p; });
    Object.keys(C).forEach(function (id) {
      var parts = [id, label(id)];
      Object.keys(C[id].l).forEach(function (lg) { parts.push(C[id].l[lg]); });
      Object.keys(C[id].a || {}).forEach(function (lg) { parts = parts.concat(C[id].a[lg]); });
      C[id]._s = normalize(parts.join(' | '));
    });
  }

  /* ---------- Pfade ---------- */
  var pathCountMemo = {};
  function pathCount(id) {
    if (pathCountMemo[id] != null) return pathCountMemo[id];
    var ps = C[id].p || [];
    var n = ps.length ? ps.reduce(function (a, p) { return a + pathCount(p); }, 0) : 1;
    pathCountMemo[id] = n;
    return n;
  }

  /* Wurzelpfade [wurzel, ..., id], hoechstens MAX_PATHS */
  function rootPaths(id) {
    var out = [];
    (function walk(cur, tail) {
      if (out.length >= MAX_PATHS) return;
      var ps = C[cur].p || [];
      if (!ps.length) { out.push([cur].concat(tail)); return; }
      ps.forEach(function (p) { walk(p, [cur].concat(tail)); });
    })(id, []);
    return out;
  }

  /* ---------- Baum ---------- */
  function rowFor(id) {
    var c = C[id];
    var kids = children[id];
    var row = h('div', { 'class': 'tr-row', 'data-row': id });
    if (kids.length) {
      var t = h('button', { type: 'button', 'class': 'tr-toggle', 'aria-expanded': 'false', 'aria-label': label(id) + ': Unterkategorien aufklappen' });
      t.innerHTML = CHEVRON;
      t.addEventListener('click', function () { toggle(row.parentNode); });
      row.appendChild(t);
    } else {
      row.appendChild(h('span', { 'class': 'tr-leaf', 'aria-hidden': 'true' }));
    }
    var btn = h('button', { type: 'button', 'class': 'tr-name', text: label(id) });
    btn.addEventListener('click', function () { select(id, false); });
    row.appendChild(btn);
    if (c.l.en && c.l.en !== c.l.de) row.appendChild(h('span', { 'class': 'tr-en', text: c.l.en }));
    if (c.d) row.appendChild(h('span', { 'class': 'tr-badge tr-badge-old', text: 'veraltet' }));
    var np = (c.p || []).length;
    if (np > 1) {
      row.appendChild(h('span', {
        'class': 'tr-badge tr-badge-multi',
        title: 'Steht unter ' + np + ' übergeordneten Kategorien: ' + c.p.map(label).join(', '),
        text: np + ' Eltern'
      }));
    }
    if (kids.length) row.appendChild(h('span', { 'class': 'tr-count', title: kids.length + ' direkte Unterkategorien', text: String(kids.length) }));
    return row;
  }

  function nodeFor(id) {
    var li = h('li', { 'class': 'tr-node', 'data-id': id });
    li.appendChild(rowFor(id));
    return li;
  }

  function toggle(li, forceOpen) {
    var btn = li.querySelector(':scope > .tr-row > .tr-toggle');
    if (!btn) return null;
    var open = btn.getAttribute('aria-expanded') === 'true';
    var want = forceOpen == null ? !open : forceOpen;
    if (want === open) return li.querySelector(':scope > ul');
    var ul = li.querySelector(':scope > ul');
    if (want) {
      if (!ul) {
        ul = h('ul', { 'class': 'tr-children' });
        children[li.getAttribute('data-id')].forEach(function (k) { ul.appendChild(nodeFor(k)); });
        li.appendChild(ul);
      }
      ul.hidden = false;
    } else if (ul) {
      ul.hidden = true;
    }
    btn.setAttribute('aria-expanded', String(want));
    li.classList.toggle('is-open', want);
    return ul;
  }

  function expandPath(path) {
    var ul = $('trTree');
    var li = null;
    for (var i = 0; i < path.length; i++) {
      li = null;
      for (var j = 0; j < ul.children.length; j++) {
        if (ul.children[j].getAttribute('data-id') === path[i]) { li = ul.children[j]; break; }
      }
      if (!li) return null;
      if (i < path.length - 1) {
        ul = toggle(li, true);
        if (!ul) return null;
      }
    }
    return li;
  }

  function collapseAll() {
    var tree = $('trTree');
    tree.innerHTML = '';
    rootIds.forEach(function (id) { tree.appendChild(nodeFor(id)); });
  }

  function openLevels(n) {
    collapseAll();
    (function rec(ul, depth) {
      if (depth >= n) return;
      Array.prototype.forEach.call(ul.children, function (li) {
        var sub = toggle(li, true);
        if (sub) rec(sub, depth + 1);
      });
    })($('trTree'), 0);
  }

  function reveal(id) {
    var first = null;
    rootPaths(id).forEach(function (p) {
      var li = expandPath(p);
      if (li && !first) first = li;
    });
    return first;
  }

  function markSelected(id) {
    Array.prototype.forEach.call(document.querySelectorAll('.tr-row.is-selected'), function (r) { r.classList.remove('is-selected'); });
    if (!id) return;
    Array.prototype.forEach.call(document.querySelectorAll('li[data-id="' + id + '"] > .tr-row'), function (r) { r.classList.add('is-selected'); });
  }

  function select(id, doReveal) {
    selected = id;
    var first = null;
    if (doReveal) first = reveal(id);
    markSelected(id);
    renderDetail(id);
    if (location.hash !== '#' + id) {
      try { history.replaceState(null, '', '#' + id); } catch (e) { /* file:// */ }
    }
    if (first) {
      var row = first.querySelector(':scope > .tr-row');
      if (row && row.scrollIntoView) row.scrollIntoView({ block: 'center' });
    }
  }

  /* ---------- Details ---------- */
  function linkButton(id) {
    var b = h('button', { type: 'button', 'class': 'tr-link', text: label(id) });
    b.addEventListener('click', function () { select(id, true); });
    return b;
  }

  function section(title) {
    return h('h3', { 'class': 'tr-detail-h', text: title });
  }

  function renderDetail(id) {
    var box = $('trDetail');
    box.innerHTML = '';
    if (!id || !C[id]) {
      box.appendChild(h('p', { 'class': 'tr-muted', text: 'Eine Kategorie im Baum oder in den Suchtreffern anklicken, dann erscheinen hier Bezeichnungen, übergeordnete und untergeordnete Kategorien und der historische Bezeichner.' }));
      return;
    }
    var c = C[id];
    box.appendChild(h('h2', { 'class': 'tr-detail-title', text: c.l.de }));
    if (c.d) box.appendChild(h('p', { 'class': 'tr-badge tr-badge-old', text: 'veraltet (owl:deprecated)' }));

    box.appendChild(section('Bezeichnungen'));
    var dl = h('dl', { 'class': 'tr-dl' });
    Object.keys(c.l).forEach(function (lg) {
      dl.appendChild(h('dt', { text: LANG_NAME[lg] || lg }));
      var dd = h('dd', { text: c.l[lg] });
      var alts = (c.a && c.a[lg]) || [];
      if (alts.length) dd.appendChild(h('span', { 'class': 'tr-muted', text: ' (auch: ' + alts.join(', ') + ')' }));
      dl.appendChild(dd);
    });
    Object.keys(c.a || {}).forEach(function (lg) {
      if (c.l[lg]) return;
      dl.appendChild(h('dt', { text: (LANG_NAME[lg] || lg) + ', alternativ' }));
      dl.appendChild(h('dd', { text: c.a[lg].join(', ') }));
    });
    box.appendChild(dl);

    if (c.n) {
      box.appendChild(section('Anmerkung der Redaktion'));
      var nl = h('dl', { 'class': 'tr-dl' });
      Object.keys(c.n).forEach(function (lg) {
        nl.appendChild(h('dt', { text: LANG_NAME[lg] || lg }));
        nl.appendChild(h('dd', { text: c.n[lg] }));
      });
      box.appendChild(nl);
    }

    var ps = c.p || [];
    box.appendChild(section(ps.length > 1 ? 'Übergeordnet (' + ps.length + ' direkte Eltern)' : ps.length ? 'Übergeordnet' : 'Übergeordnet'));
    if (ps.length) {
      var pul = h('ul', { 'class': 'tr-linklist' });
      ps.slice().sort(function (a, b) { return label(a).localeCompare(label(b), 'de'); })
        .forEach(function (p) { pul.appendChild(h('li', null, linkButton(p))); });
      box.appendChild(pul);
      if (ps.length > 1) {
        box.appendChild(h('p', { 'class': 'tr-muted', text: 'Diese Kategorie steht im Baum unter jedem dieser Eltern.' }));
      }
    } else {
      box.appendChild(h('p', { 'class': 'tr-muted', text: 'Oberste Kategorie des Vokabulars.' }));
    }

    var kids = children[id];
    box.appendChild(section('Untergeordnet (' + kids.length + ')'));
    if (kids.length) {
      var kul = h('ul', { 'class': 'tr-linklist' });
      kids.forEach(function (k) { kul.appendChild(h('li', null, linkButton(k))); });
      box.appendChild(kul);
    } else {
      box.appendChild(h('p', { 'class': 'tr-muted', text: 'Keine Unterkategorien.' }));
    }

    var n = pathCount(id);
    box.appendChild(section('Wege von der obersten Kategorie (' + n + ')'));
    var paths = rootPaths(id);
    var pl = h('ol', { 'class': 'tr-paths' });
    paths.forEach(function (p) {
      var li = h('li');
      p.forEach(function (pid, i) {
        if (i) li.appendChild(h('span', { 'class': 'tr-sep', 'aria-hidden': 'true', text: ' › ' }));
        if (i === p.length - 1) li.appendChild(h('strong', { text: label(pid) }));
        else li.appendChild(linkButton(pid));
      });
      pl.appendChild(li);
    });
    box.appendChild(pl);
    if (n > paths.length) box.appendChild(h('p', { 'class': 'tr-muted', text: 'Gezeigt sind ' + paths.length + ' von ' + n + ' Wegen.' }));

    box.appendChild(section('Bezeichner'));
    var uri = data.meta.uriBasis + id;
    var idl = h('dl', { 'class': 'tr-dl' });
    idl.appendChild(h('dt', { text: 'ID' }));
    idl.appendChild(h('dd', null, h('code', { text: id })));
    idl.appendChild(h('dt', { text: 'Historische URI' }));
    idl.appendChild(h('dd', null, h('code', { 'class': 'tr-uri', text: uri })));
    idl.appendChild(h('dt', { text: 'Angelegt' }));
    idl.appendChild(h('dd', { text: c.c }));
    idl.appendChild(h('dt', { text: 'Zuletzt geändert' }));
    idl.appendChild(h('dd', { text: c.m }));
    box.appendChild(idl);
    box.appendChild(h('p', { 'class': 'tr-muted', text: 'Die URI ist ein Bezeichner und keine Adresse: dhplus.sbg.ac.at ist nicht mehr erreichbar. Als Referenz dient die ID.' }));
    var copy = h('button', { type: 'button', 'class': 'tr-btn', text: 'URI kopieren' });
    copy.addEventListener('click', function () {
      var done = function () { copy.textContent = 'Kopiert'; setTimeout(function () { copy.textContent = 'URI kopieren'; }, 1500); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(uri).then(done, function () {});
    });
    box.appendChild(copy);
  }

  /* ---------- Suche ---------- */
  function mark(text, q) {
    var frag = document.createDocumentFragment();
    var norm = normalize(text);
    var i = q ? norm.indexOf(q) : -1;
    if (i < 0 || norm.length !== text.length) { frag.appendChild(document.createTextNode(text)); return frag; }
    frag.appendChild(document.createTextNode(text.slice(0, i)));
    frag.appendChild(h('mark', { text: text.slice(i, i + q.length) }));
    frag.appendChild(document.createTextNode(text.slice(i + q.length)));
    return frag;
  }

  function search() {
    var raw = $('trSearch').value.trim();
    var box = $('trResults');
    box.innerHTML = '';
    if (!raw) { box.hidden = true; return; }
    var q = normalize(raw);
    var hits = Object.keys(C).filter(function (id) { return C[id]._s.indexOf(q) !== -1; });
    box.hidden = false;
    var info = hits.length === 0 ? 'Keine Treffer' : hits.length + (hits.length === 1 ? ' Treffer' : ' Treffer') + (hits.length > MAX_RESULTS ? ' (die ersten ' + MAX_RESULTS + ' sind aufgelistet)' : '');
    box.appendChild(h('p', { 'class': 'tr-results-info', role: 'status', text: info }));
    var ul = h('ul', { 'class': 'tr-results-list' });
    hits.slice(0, MAX_RESULTS).forEach(function (id) {
      var b = h('button', { type: 'button', 'class': 'tr-result' });
      b.appendChild(h('span', { 'class': 'tr-result-name' }, mark(label(id), q)));
      var sub = [];
      if (C[id].l.en && C[id].l.en !== C[id].l.de) sub.push(C[id].l.en);
      var ps = C[id].p || [];
      sub.push(ps.length ? 'unter: ' + ps.map(label).join(', ') : 'oberste Kategorie');
      b.appendChild(h('span', { 'class': 'tr-result-sub', text: sub.join(' · ') }));
      b.addEventListener('click', function () { select(id, true); });
      ul.appendChild(h('li', null, b));
    });
    box.appendChild(ul);
  }

  /* ---------- Start ---------- */
  function fromHash() {
    var id = decodeURIComponent(location.hash.replace(/^#/, ''));
    if (id && C[id]) select(id, true);
  }

  function init() {
    buildIndex();
    var m = data.meta;
    $('trMeta').textContent = m.konzepte + ' Kategorien, ' + m.wurzeln.length + ' oberste Kategorien, ' +
      m.mitMehrerenEltern + ' Kategorien mit mehreren direkten Eltern. Datenstand: textseries, Commit ' + m.commit.slice(0, 9) + '.';
    collapseAll();
    openLevels(1);
    renderDetail(null);
    var timer;
    $('trSearch').addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(search, 120); });
    $('trSearch').addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { $('trSearch').value = ''; search(); }
    });
    $('trCollapse').addEventListener('click', function () { openLevels(0); markSelected(selected); });
    $('trOpen2').addEventListener('click', function () { openLevels(2); markSelected(selected); });
    window.addEventListener('hashchange', fromHash);
    fromHash();
    document.documentElement.setAttribute('data-tr-ready', '1');
  }

  fetch('data/textreihen.json')
    .then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    })
    .then(function (d) { data = d; init(); })
    .catch(function (e) {
      $('trTree').appendChild(h('li', { 'class': 'tr-error', role: 'alert', text: 'Die Daten konnten nicht geladen werden (' + e.message + '). Die Seite braucht einen Webserver; lokal: npm run serve.' }));
    });
})();
