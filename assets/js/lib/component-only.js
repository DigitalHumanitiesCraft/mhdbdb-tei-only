/**
 * Reine Wortbestandteile (#228): Lemmata ohne Korpusbeleg, die eine andere
 * Etymologie als Bestandteil nennt (`seg type="component"`).
 *
 * Der Status wird abgeleitet und nirgends gespeichert. Quelle sind zwei Dinge
 * im Authority-Index: `lemma.noCorpus === true` (der Build setzt es nur bei
 * Lemmata, die im Corpus-Index keinen Beleg haben) und `etymology[].lemmaRef`
 * der übrigen Lemmata. Beide Seiten (Wörterbuch, Lemmaseite) benutzen diese
 * eine Regel, damit sie nicht auseinanderlaufen.
 *
 * Die Kennzeichnung beschreibt den Erschließungsstand. Sie sagt nichts
 * darüber, ob die hinterlegte Zerlegung fachlich stimmt.
 */

/** Voller Hinweistext (Lemmaseite, Tooltip im Wörterbuch). Wortlaut KZW, #228, 01.10.2026. */
export const COMPONENT_ONLY_NOTE =
    'Als Wortbestandteil erfasst; kein eigenständiger Beleg im aktuellen Korpus.';

/** Kurzmarke für die enge Zeile der Wörterbuchliste. */
export const COMPONENT_ONLY_SHORT = 'nur als Wortbestandteil';

/**
 * Menge aller Lemma-IDs, die irgendeine andere Etymologie als Bestandteil
 * nennt. Ein Verweis auf sich selbst zählt nicht.
 */
export function buildComponentRefSet(lemmata) {
    const refs = new Set();
    for (const lemma of lemmata) {
        for (const comp of lemma.etymology || []) {
            if (comp.lemmaRef && comp.lemmaRef !== lemma.id) refs.add(comp.lemmaRef);
        }
    }
    return refs;
}

/** `true`, wenn der Eintrag ein reiner Bestandteil ist. */
export function isComponentOnly(lemma, refSet) {
    return lemma.noCorpus === true && refSet.has(lemma.id);
}
