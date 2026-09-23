/**
 * MHDBDB - Gattungen samt Untergattungen
 *
 * Geteilt von der Korpussuche (Gattungs-Vorschlag im Textfilter, #433) und dem
 * Gattungen-Explorer im Playground. Beide müssen dieselbe Menge meinen: KZW am
 * 2026-09-15 in #433, "die Untergattungen kommen immer mit, das geht nicht
 * anders. Das beeinflusst auch den Gattungsexplorer."
 *
 * Die Hierarchie ist ein DAG, kein Baum: genre.parents[] trägt die direkten
 * Eltern (Authority-Index seit v1.9.0, im Build aus der transitiven Hülle
 * reduziert, #361), und eine Gattung kann mehrere haben. Die Werkmenge eines
 * Teilbaums ist deshalb eine Vereinigung, keine Summe: ein Werk in zwei
 * Geschwistergattungen zählt einmal.
 */

/**
 * Werke je Gattung, einschließlich aller Untergattungen.
 *
 * @param {Array<{id: string, parents?: string[]}>} genres - authorityIndex.genres
 * @param {Map<string, string[]>|Object<string, string[]>} genreToWorks -
 *   direkte Zuordnung (authorityIndex.maps.genreToWorks, im Playground als Map)
 * @returns {{children: Map<string, string[]>, subtreeWorks: Map<string, Set<string>>}}
 */
export function buildGenreSubtrees(genres, genreToWorks) {
    const direct = (id) => (genreToWorks instanceof Map
        ? genreToWorks.get(id)
        : genreToWorks?.[id]) || [];

    const children = new Map();
    for (const genre of genres || []) {
        if (!children.has(genre.id)) children.set(genre.id, []);
    }
    for (const genre of genres || []) {
        for (const parentId of genre.parents || []) {
            if (children.has(parentId)) children.get(parentId).push(genre.id);
        }
    }

    const subtreeWorks = new Map();
    // `seen` schützt vor einem Zyklus in den Daten; der Build erzeugt keinen,
    // aber eine Endlosrekursion wäre die teuerste Art, das herauszufinden.
    const collect = (id, seen) => {
        if (subtreeWorks.has(id)) return subtreeWorks.get(id);
        if (seen.has(id)) return new Set();
        const next = new Set(seen).add(id);
        const works = new Set(direct(id));
        for (const childId of children.get(id) || []) {
            for (const workId of collect(childId, next)) works.add(workId);
        }
        subtreeWorks.set(id, works);
        return works;
    };
    for (const id of children.keys()) collect(id, new Set());

    return { children, subtreeWorks };
}

/**
 * Werk-ID aus einem @ref des Korpus-Index: "works.xml#work_89" → "work_89".
 */
export function workIdFromRef(workRef) {
    if (!workRef) return null;
    return workRef.includes('#') ? workRef.split('#')[1] : workRef;
}
