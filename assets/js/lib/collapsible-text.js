/**
 * Einklappbare lange Texte (#554, KZW 16.10.2026: "Lange Kommentare müssen
 * eingeklappt werden können").
 *
 * Gemeinsam für die Lemmaseite (lemma/lemma-page.js) und den Lemma-Explorer im
 * Playground, die beide die Lexikonkommentare einer Bedeutung zeigen. Ein Text
 * über COLLAPSE_MIN_CHARS Zeichen steht zunächst auf COLLAPSE_LINES Zeilen
 * gekürzt, darunter der Knopf "Weiterlesen". Kürzere Texte bleiben unverändert,
 * damit die Bedienung nur dort auftaucht, wo sie etwas verdeckt.
 *
 * Schwelle und Zeilenzahl folgen dem Vorschlag B4 in
 * ingest/glossar-554/UEBERNAHME.md (etwa sechs Zeilen, nur bei langen Texten).
 * Die Zeichenzahl ist nur die Vorauswahl. `enhanceCollapsibles` misst nach dem
 * Einfügen, ob die Kürzung wirklich etwas verdeckt, und nimmt den Knopf sonst
 * wieder weg (breites Fenster, kurze Zeilen).
 *
 * Zugänglichkeit: echter <button> mit aria-expanded und aria-controls; der Text
 * bleibt vollständig im DOM, die Kürzung ist reines CSS (shared.css).
 */

export const COLLAPSE_MIN_CHARS = 600;
export const COLLAPSE_LINES = 6;

let zaehler = 0;

/**
 * @param {string} innerHtml bereits escapter Inhalt
 * @param {number} zeichen Länge des reinen Textes, für die Schwelle
 */
export function collapsibleHtml(innerHtml, zeichen) {
    if (zeichen <= COLLAPSE_MIN_CHARS) return innerHtml;
    const id = `clamp-text-${++zaehler}`;
    return `<div class="clamp-wrap">
        <div class="clamp-text clamp-collapsed" id="${id}">${innerHtml}</div>
        <button type="button" class="clamp-toggle" aria-expanded="false" aria-controls="${id}">Weiterlesen</button>
    </div>`;
}

/** Nach dem Einfügen aufrufen: Knöpfe weglassen, wo die Kürzung nichts verdeckt. */
export function enhanceCollapsibles(root = document) {
    root.querySelectorAll('.clamp-text.clamp-collapsed').forEach(el => {
        // Nicht sichtbar (zugeklapptes Panel): keine Messung möglich, Knopf bleibt.
        if (el.clientHeight === 0) return;
        if (el.scrollHeight <= el.clientHeight + 1) {
            el.classList.remove('clamp-collapsed');
            el.parentElement?.querySelector('.clamp-toggle')?.remove();
        }
    });
}

function umschalten(knopf) {
    const text = document.getElementById(knopf.getAttribute('aria-controls'));
    if (!text) return;
    const offen = text.classList.toggle('clamp-collapsed') === false;
    knopf.setAttribute('aria-expanded', String(offen));
    knopf.textContent = offen ? 'Weniger anzeigen' : 'Weiterlesen';
}

// Ein Listener für alle Texte; überlebt jedes erneute Einfügen per innerHTML.
if (typeof document !== 'undefined' && !document.documentElement.dataset.clampBereit) {
    document.documentElement.dataset.clampBereit = '1';
    document.addEventListener('click', e => {
        const knopf = e.target.closest?.('.clamp-toggle');
        if (knopf) umschalten(knopf);
    });
}
