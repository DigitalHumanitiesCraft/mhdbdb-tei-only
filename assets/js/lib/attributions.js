/**
 * MHDBDB - Zuschreibungen eines Werks (#452)
 *
 * works[].attributions im Authority-Index fuehrt alle <author> eines Werks in
 * Dokumentreihenfolge: { ref, name, status?, role?, note? }.
 *   status  disputed | uncertain | rejected  (fehlt = allgemein anerkannt)
 *   role    adapter                           (Bearbeiter, kein Autor)
 *
 * Gezaehlt als Autor wird, wer weder Bearbeiter noch verworfen ist. Das
 * Kompatibilitaetsfeld works[].author/authorRef ist der erste davon; wer alle
 * Zuschreibungen braucht (Autorfilter, Leseansicht, Werkansicht), liest diese
 * Datei. Geteilt von Hauptseite und Playground, gespiegelt in
 * scripts/build-authority-index.py (is_counting_author).
 */

/** Anzeigetexte des Zuschreibungsstatus (KZW 08.10.2026, #452). */
export const STATUS_LABEL = {
    disputed: 'umstritten',
    uncertain: 'unsicher zugeschrieben',
    rejected: 'verworfen',
};

export const ADAPTER_LABEL = 'Bearbeiter';

/** Personen-ID aus "persons.xml#person_1" oder "#person_1". */
export function personIdOf(ref) {
    if (!ref) return null;
    return ref.includes('#') ? ref.split('#')[1] : ref;
}

function listOf(work) {
    return (work && Array.isArray(work.attributions)) ? work.attributions : [];
}

/** Zaehlt als Autor: weder Bearbeiter noch verworfen. */
export function isCountingAuthor(attribution) {
    return !attribution.role && attribution.status !== 'rejected';
}

/** Alle Autoren in Dokumentreihenfolge, "umstritten" und "unsicher" eingeschlossen. */
export function countingAttributions(work) {
    return listOf(work).filter(isCountingAuthor);
}

/** Bearbeiter. */
export function adapters(work) {
    return listOf(work).filter(a => a.role === 'adapter');
}

/** Verworfene Zuschreibungen (ohne Bearbeiter). */
export function formerAttributions(work) {
    return listOf(work).filter(a => !a.role && a.status === 'rejected');
}

/** "Konrad von Würzburg (umstritten)"; ohne Status nur der Name. */
export function formatAttribution(attribution) {
    const label = STATUS_LABEL[attribution.status];
    return label ? `${attribution.name} (${label})` : attribution.name;
}

/**
 * Die Autorenzeile eines Werks: "Anonym; Konrad von Würzburg (umstritten)".
 * Leer, wenn das Werk keine Zuschreibungen fuehrt.
 */
export function formatAttributionList(work) {
    return countingAttributions(work).map(formatAttribution).join('; ');
}

/** Alle Namen, unter denen ein Werk als Autorwerk gefunden werden soll. */
export function attributionNames(work) {
    return countingAttributions(work).map(a => a.name);
}
