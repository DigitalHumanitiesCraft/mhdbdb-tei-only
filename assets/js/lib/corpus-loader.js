/**
 * Corpus Loader
 * Handles loading and caching of pre-built corpus indices
 * Uses Pako for gzip decompression (Safari 14+ compatible)
 * Uses Dexie.js for IndexedDB caching
 */

const INDEX_VERSION = '4.2.21';  // 4.1.5: #143 APO/HMT/HH Prosa-Konversion l→lb. 4.1.6: #198 habe/hab-Disambiguierung (25 Tokens zu lemma_2593, 179 NOM-Strips). 4.1.7: #189 GWTK-Pilot — 257 nackte rot/jung-Tokens neu annotiert (Goldstandard-validiert). 4.1.8: #138 814 Strophenziffern aus dem HUG-Verstext entfernt (706 davon pos=DIG, 108 unannotiert). 4.2.0: #236 Frauenlob-Revision — FR3 Parallelueberlieferungs-Ebene rekonstruiert (23 gleichrangige Toene zu 10 zusammengefuehrt, 36 <div type="parallel">, 1.563 Verse jetzt als Parallelueberlieferung erkennbar); 42 roemische Ordnungszahl-Tokens aus FR1/FR2/FR3 entfernt und durch <head> ersetzt. 4.2.1: #228 sieben leere <author>-Elemente im titleStmt gefuellt (ALX/BVSN/PSG/PTS Moench von Heilsbronn, BOP Boppe, MHG Herger, MRB Burggraf von Riedenburg); betrifft nur das Feld text.author, keine Token- oder Positionsdaten. Ausserdem normalisiert der Build Whitespace im Autornamen: LUU trug ihn ueber zwei eingerueckte Zeilen, der Umbruch stand so in Index und API. 4.2.2: #216 Serie 1 (minne): 5.435 zuvor unannotierte Tokens der Form minne in 255 Texten kontextdisambiguiert (5.106 zu lemma_4130 NOM, 329 zu lemma_4133 VRB); 1.547 ambige Faelle blieben absichtlich unannotiert. 4.2.3: #369 Serie 2 (stat): 7.760 zuvor unannotierte Tokens der Form stat in 322 Texten kontextdisambiguiert (6.665 zu lemma_5732 NOM, 1.095 zu lemma_5710 VRB); 95 Faelle blieben absichtlich unannotiert. 4.2.4: #369 Nachlauf — Fehltag SKT_502140_4 von lemma_5732 NOM auf lemma_5710 VRB korrigiert. 4.2.5: #367 - 40 Tokens der Fuegung 'der/die waeren minne' vom Verb aufs Adjektiv umannotiert (lemma_7505 wesen VRB auf lemma_7338 waer ADJ). 4.2.6: #235 Punkt 3 - 66 bisher unannotierte Breve-Tokens der WZB mechanisch nachannotiert (lemmaRef und pos, kein corresp); aendert die Positionszaehlung in WZB. 4.2.7: #235 Punkt 3 (Rest) - 89 der 98 zurueckgehaltenen Breve-Tokens der WZB kontextdisambiguiert nachannotiert (lemmaRef und pos, kein corresp); aendert die Positionszaehlung in WZB. 4.2.8: Werktitel der fuenf Frauendienst-Sigel korrigiert (FD, FDS, FH, FLD, FP trugen 'Frauenbuch', referenzieren aber work_6 = Frauendienst); betrifft nur text.title. 4.2.9: #216 Punkt 3 (vrouwe vor minne): 152 zuvor unannotierte Tokens der Anredeform vrouwe in 10 Texten zu lemma_7260 NOM annotiert (150 mechanisch, 2 redaktionell entschieden, kein LLM-Lauf); aendert die Positionszaehlung in den 10 Texten. 3 Tokens der Zirkumflex-Schreibung blieben ohne Variantentyp unannotiert. 4.2.10: #387 (vrouwe, mechanischer Teil): 948 zuvor unannotierte Tokens der Form vrouwe in 31 Texten zu lemma_7260 NOM annotiert (kein LLM-Lauf, mit Belegschwelle je Schreibung); aendert die Positionszaehlung in den 31 Texten. 399 Tokens blieben unannotiert, davon 390 der kontextpflichtigen Form fro. 4.2.11: #387 (fro): 355 von 390 Tokens der Schreibung fro und frô in 58 Texten kontextdisambiguiert (345 lemma_7250 ADJ, 9 lemma_7260 NOM, 1 ADV); aendert die Positionszaehlung in den 58 Texten. 35 blieben unannotiert. 4.2.12: #216 Punkt 3, Nachtrag - die drei RVBR-Belege der Zirkumflex-Schreibung frô vor minne annotiert (lemma_7260 NOM); dafuer type_372365 neu gepraegt, weil unter dem Ziel-Lemma kein Typ existierte und die #370-Ratsche ein Schreiben ohne corresp ausschliesst. Aendert die Positionszaehlung in RVBR. 4.2.13: #387 Nachlauf - 19 zurueckgehaltene fro-Belege in der Wortart bestimmt (lemma_7250 ADJ), zweiter Durchgang mit feststehendem Lemma und einem am Bestand gemessenen Prior gegen ADV. 11 bleiben zurueckgehalten. Aendert die Positionszaehlung in 6 Texten. 4.2.14: #363 Hausenblase - 32 Tokens der Konstruktion huesenblater in 7 Kochbuch-Sigeln auf lemma_49714 vereinheitlicht (19 Belege: 6 Komposita, 13 getrennte Paare mit je beiden Tokens); die getrennten Paare als Mehrwort-Einheit nach TEI-MODEL.md Paragraf 4.1a. Aendert die Positionszaehlung in 3 der 7 Sigel (HUB3, KBL4, KDO). 4.2.15: #198 Schritt 2. Die drei aus PR #205 zurückgehaltenen NOM-Tokens sind entschieden (AC3_23010_1 auf lemma_9644 houwe, DA_8222_3 auf lemma_2593 habe, JT_6192000_1 verbal); kein <w> unter lemma_2598 trägt noch ein NOM. Dazu das in PR #205 entfernte @ana der umgehängten Tokens: 25 auf lemma_2593_sense_4159 (Besitz), eines auf den einzigen Sense von lemma_9644, drei bleiben bewusst leer. 4.2.16: Drei am 14.09.2026 von KZW entschiedene Korrekturen in einem Lauf. #308 Autorangaben: HHP traegt im titleStmt jetzt die preferred-Form 'Heinrich von Pressela' statt 'Heinrich von Breslau' (betrifft nur text.author, keine Token- oder Positionsdaten), VOR zeigt statt auf die nie existierende ID person_schweizer_anonymus auf person_1772, WZB schreibt @ref in der in tei/ durchgehaltenen Kurzform, und LUUs Autorname steht nicht mehr ueber zwei eingerueckte Zeilen (letzteres ohne Indexwirkung, weil der Build seit 4.2.1 normalisiert). #375 acht eindeutige Belege der Form waeren/wâren/woren vom Verb aufs Adjektiv umannotiert (lemma_7505 wesen VRB auf lemma_7338 waer ADJ), Fortsetzung von 4.2.5; alle acht trugen schon ein @lemmaRef, die Positionszaehlung aendert sich also nicht. Die acht uebrigen Faelle des Vorgangs bleiben liegen. #432 WH_6214_3 'der din eine zehen wuerfe drin' vom Zahlwort auf den Koerperteil (lemma_7779 NUM auf lemma_9653 NOM, mit @ana und @corresp). Ein neuer Variantentyp (type_372376 fuer die Schreibung waeren unter lemma_7338), deshalb Authority-Index 1.9.5 auf 1.9.6. 4.2.17: #444 Moriz von Craun (CR, work_5) fuehrt nur noch Anonym als Autor. Das Werk war zugleich Bligger von Steinach (person_227) und Anonym zugeordnet, und weil der Build den ersten Autor uebernimmt, erschien die verworfene Zuschreibung als aktuelle. Korrigiert im CR-Header (Bligger-Eintrag entfernt) und im Werk-Rueckverweis von MBS; betrifft nur text.author, keine Token- oder Positionsdaten. 4.2.18: Drei von KZW entschiedene Annotationspakete in einem Lauf, 88 Tokens in 45 Texten. #366 fyndling-Beitrag: 8 unlemmatisierte Tokens in DES2, KBL3, KBL4, KDO und MBS2 annotiert (Barsch, Gewuerz dreimal, Geweih, Zimtrinde, Hausen zweimal); Entscheidungen KZW 11.09. und 17.09.2026. #375: die vier letzten Faelle der Form waren mit Zirkumflex vom Verb aufs Adjektiv umannotiert (lemma_7505 VRB auf lemma_7338 ADJ), Fortsetzung von 4.2.5 und 4.2.16; die acht eindeutigen sind seit 4.2.16 erledigt, die vier VRB-Faelle bestaetigen den Ist-Stand. #371: 76 bislang unlemmatisierte Tokens der Formen stat und stat mit Zirkumflex nach dem actions-Array in KZWs Review vom 15.09.2026 annotiert (26 Ufer auf lemma_5712 stade, 31 auf lemma_5732 stat, 18 verbal auf lemma_5710, 1 adjektivisch auf lemma_5713 staete); die 17 Faelle mit option OFFEN und die 2 mit NEU_STAND blieben unangetastet. 84 der 88 Tokens bekommen erstmals ein lemmaRef, die Positionszaehlung aendert sich also in den betroffenen Texten. Zehn neu gepraegte Variantentypen (type_372377 bis type_372386), deshalb Authority-Index 1.9.7 auf 1.9.8. 4.2.19: Welle A1 vom 23.09.2026. #387: die 21 Resttokens der vrouwe/vro-Serie nach KZWs Einzelentscheidungen vom 17.09.2026 annotiert (14 auf lemma_7250 vro: acht ADV, zwei NOM, zwei ADJ und zwei als ADJ NOM mit erklaerendem @reason; 5 auf lemma_7256 vroeuwen VRB; 2 auf lemma_7260 vrouwe NOM). Alle 21 bekommen erstmals ein lemmaRef, die Positionszaehlung aendert sich also in FLG, FR1, FR2, FR3, GWTK, MR1, NEIM, RVBR, SVP und WZB. #418: die 12 offenen hawe-Tokens von lemma_2598 haben auf lemma_2923 houwen (7, VRB) und lemma_9644 houwe (5, NOM; drei auf sense_15624, zwei auf den neuen sense_119194) umannotiert, AC3_23010_1 dazu auf den neuen Typ. #464: ENE_10090_1 und ROT_28700_1 von pos PRO VRB auf VRB PRO mit reason zalte+er. Fuenf neu gepraegte Variantentypen (type_372387 bis type_372391), type_117159 entfaellt, deshalb Authority-Index 1.9.8 auf 1.9.9. 4.2.20: #228 editorischer Apparat und neuhochdeutsche Inhaltsangaben entannotiert (Entscheidung KZW 11.09.2026): 132 Tokens in 69 Noten mit @n ohne Vers (BRW 64, NML 25, CEFB 10, DL2 7, dazu die acht Dichternamen-Ueberschriften der Edition von Kraus in BRH, HAW, HDM, HHP, HHW, NIU, OBP, OVB) und 2.058 Tokens in den 422 GWTK-Inhaltsangaben verlieren lemmaRef, pos, ana und corresp. NEIM bleibt unangetastet (Konkordanz #453), NEIR, CL und KVO sind entschieden ausgenommen. KVO_300001_2 lob nachannotiert (lemma_3849). Die 2.190 Tokens trugen vorher ein lemmaRef, die Positionszaehlung aendert sich also in den 13 entannotierten Texten. 275 Variantentypen entfallen, deshalb Authority-Index 1.9.11 auf 1.9.12. 4.2.21: #235 Punkt 1, Nachtrag: 30 der 34 WZB-Split-Tokens aus f3dcf2a86 lemmatisiert (lemmaRef und pos, kein ana, kein corresp); die Positionszaehlung der WZB aendert sich, variants.xml nicht.
const AUTHORITY_INDEX_VERSION = '1.9.13';  // 1.2.0: Authority migration. 1.2.1: WZB-Lemmata + Werk-Eintrag. 1.2.2: #104 FLG/FLG1-Werk-Titel + work_571 biblStruct (Vollmann-Profe/Neumann 1990). 1.3.0: #113-Followup — concepts altDE/altEN/altNormalized. 1.4.0: #44/#115 variants.xml aus Korpus regeneriert (+64.287 Formen). 1.4.1: #125 deterministischer Build (generatedAt entfernt). 1.4.2: #143 HH-Genre-Korrektur (work_137). 1.4.3: #143 APO-Gattung nach Terrahe (work_568). 1.4.4: #115 A-Stub-Backfill (+125 Lemmata). 1.5.0: Audit #5 — parse_genres last-wins-Fix (250 Genre-Labels) + genre altDE/altEN/altNormalized. 1.6.0: #161 posAll[] Multi-POS (pos bleibt Erstwert). 1.6.1: #189 GWTK-Pilot — variants.xml +2 Typen (rotte/rotten unter lemma_4954) + Formen-Zuwachs aus der Neu-Annotation. 1.6.2: #224 NFC-Unicode-Komposition im Normalizer — zerlegte Umlaute (o + U+0308) werden jetzt komponiert, bevor die Umlaut-Regeln greifen; korrigiert 'hugo von mühldorf' zu 'hugo von muehldorf' in persons.xml (die Quelldatei traegt dort ein zerlegtes ue). 1.6.3: #235 kaputte Tilden in URLs (kombinierendes U+0303 hinter einem Leerzeichen statt ASCII-Tilde) in 24 works.xml-Notizen repariert; die gleichen Notizen stehen im TEI-Header, dort ohne Indexwirkung. 1.6.4: #138 814 Strophenziffern aus dem HUG-Verstext entfernt; variants.xml verliert dadurch den Typ type_195524 'cxlvix', der nur in HUG vorkam. 1.6.5: #236 FR3-Metadaten auf den Supplementband 2000 umgestellt (ISBN 3-525-82504-8, Hrsg. Haustein/Stackmann, Reihenband 232) und Zotero-Title-Case 'Teil Ii'/'Teil Iii' repariert; variants.xml unveraendert. 1.7.0: kuratierte Lemma-Angaben: lemma.origin (Herkunftssprache, Schicht B von #28) sowie sense.definition/sense.comment (Prosa aus <def> bzw. <note type="comment">); erster Eintrag lemma_37818 Abba. 1.7.1: #228 works.xml-Autornamen werden wie im Korpus-Index mit itertext() und Whitespace-Kollaps gelesen; work_563 trug den Umbruch der XML-Einrueckung bis in api/works/work_563.json. 1.8.0: #307 altNames/altNormalized je Person (134 Nebenformen bei 80 Personen, dedupliziert 100); der Personen-Explorer sucht damit mit und zeigt die Trefferform an. 1.8.1: #193 Baustein 1 — lemma_3036 Ingliart von Personenname auf Pferdename umklassifiziert (concept_21012000 Maennlich/Mann + concept_23112500 Personennamen raus, concept_14012100 Haustiere/Namen + concept_23221000 Pferd und Reiten/Namen rein, wie bei den neun anderen arthurischen Pferden). Belegt durch Pz. 389,26 'mit den kurzen oeren ingliart' und 398,14; Quelle Borek 2023. Der dritte Korpus-Token REN_242090_0 'ingligar von jelezie' steht in einem Ritter-Katalog und haengt vermutlich falsch an diesem Lemma; das ist ein aelterer Befund, liegt bei KZW und beruehrt die Klassifikation des Lemmas nicht. 1.9.0: #361 genre.parents[] — direkte Eltern als IDs aus der transitiven Reduktion (615 Kategorien, zwei Wurzeln, Baumtiefe 9); ersetzt maps.genreHierarchy, das Eltern-Namen und die volle Hülle trug. 1.9.1: #369 Nachlauf — variants.xml verliert type_218598 'stât' unter lemma_5732, weil sein einziger Beleg (SKT_502140_4) ein Fehltag war und auf lemma_5710 VRB korrigiert wurde. 1.9.2: #367 - variants.xml gewinnt zwei Typen unter lemma_7338 (waer): type_372363 fuer waeren (CHH) und type_372364 fuer woren (FR3), neu gepraegt statt umgehaengt. 1.9.3: #216 Punkt 3, Nachtrag - variants.xml gewinnt type_372365 fuer die Schreibung frô unter lemma_7260 (RVBR); neu gepraegt statt umgehaengt, weil frô bereits als type_25866 unter lemma_7250 gefuehrt ist. 1.9.4: #363 Hausenblase - variants.xml gewinnt 10 neu gepraegte Typen (type_372366 bis type_372375) und haengt 5 bestehende um; lemma_27031 hasenblase faellt weg, sein einziger Beleg war das falsch gelesene KDO-Kompositum. 1.9.5: #198 Schritt 2. <pos>NOM</pos> aus lemma_2598 haben entfernt, nachdem der letzte NOM-Token unter diesem Lemma aufgelöst ist. Kein Sense wandert nach lemma_2593: alle acht Senses von lemma_2598 sind im Korpus ausschließlich verbal belegt. 1.9.6: #375 praegt type_372376 fuer die Schreibung waeren unter lemma_7338 (Regel aus #367: neue Nummer, nie eine bestehende umhaengen). #308 ergaenzt zwei persName type=alternative in persons.xml und dreht bei person_1249 die Hauptform: preferred ist jetzt 'Jakob von Warte' (Ansetzungsform von GND und Deutscher Biographie), 'Jakob von Wart' bleibt als belegte Alternative. person_1050 bekommt 'Heinrich von Breslau' als Alternative neben der preferred-Form 'Heinrich von Pressela'. 1.9.7: #444 work_5 Moriz von Craun verliert in works.xml den Autor Bligger von Steinach und fuehrt nur noch person_anonym. Damit faellt work_5 aus den Werken von person_227 (bleibt: work_313) und kommt zu person_anonym. Bliggers Lyrik bleibt ihm zugeordnet; variants.xml unveraendert. 1.9.8: #366, #375 und #371 in einem Lauf. variants.xml gewinnt zehn neu gepraegte Typen und haengt keinen bestehenden um (Regel aus #367): type_372377 bersige unter lemma_26988, type_372378 gehornn unter lemma_2039, type_372379 gewuertz unter lemma_7736, type_372380 hawsen unter lemma_42619, type_372381 wuerczenn und type_372382 wuertzenn unter lemma_7736, type_372383 zimendtrinttenn unter lemma_26776, type_372384 stat unter lemma_5712, type_372385 stat unter lemma_5713, type_372386 stat mit Zirkumflex unter lemma_5732. Der Fall hawsen ist der lehrreiche: die Form wird bereits als type_372368 unter lemma_49714 huesenblater gefuehrt (aus #363), ein Umhaengen haette jene Tokens mitgerissen. Formen 256.773 auf 256.783, Eintraege unveraendert 42.626, keine zusaetzliche Mehrdeutigkeit (Typen mit mehr als einem Lemma bleiben bei 1). 1.9.9: Welle A1 vom 23.09.2026 (#387, #418, #464). Fuenf neu gepraegte Variantentypen nach der Regel aus #367: type_372387 vrowe mit Breve unter lemma_7260, type_372388 vroewe unter lemma_7256, type_372389 froewen unter lemma_7250, type_372390 hawe unter lemma_2923, type_372391 hawe unter lemma_9644. type_117159 hawe unter lemma_2598 haben entfaellt, weil keines seiner 13 Tokens bei haben bleibt; ihn fuer houwe weiterzufuehren waere Umhaengen gewesen. Damit faellt die einzige Typ-ID mit mehr als einem Lemma weg (1 auf 0). Neuer Sense lemma_9644_sense_119194 (houwe als Schlag, die drei Konzepte aus lemma_2923_sense_4697). Formen 256.783 auf 256.787, Eintraege unveraendert 42.626. Laufzeit-Woerterbuch (first-wins, 234.250 Mappings beiderseits): 0 neu, 0 entfallen, 2 umgeklappt, froewen von lemma_7256 auf lemma_7250 (Korpus: 35 unter lemma_7260, 21 unter lemma_7256, 1 unter lemma_7250, also gegen Vorschrift B aus ADR-021) und hawe von lemma_2598 auf lemma_2923 (7 unter lemma_2923, 6 unter lemma_9644, B-konform). 1.9.10: #270 sense.commentRespName, der Anzeigename zu sense.commentResp, beim Build aus contributors.xml aufgeloest (ADR-018 Weg 2); Lemma-Seite und Playground zeigen 'Kommentar von <Name>'. 1.9.11: #357 lemma_3036 Ingliart bekommt einen zweiten Sense lemma_3036_sense_119195 fuer den Menschennamen (concept_21012000 Maennlich/Mann + concept_23112500 Personennamen, wie die Nachbarn Wimiligar, Rufter und Echerabant im Rennewart-Katalog). REN_242090_0 'ingligar von jelezie' zeigt mit @ana darauf, der Pferde-Sense behaelt die beiden Parzival-Belege. Entscheidung KZW 14.09.2026: kein eigenes Lemma, ein Name bezeichnet mehrere Entitaeten. Der Befund stand seit 1.8.1 offen. 1.9.12: #228 165 Lemmata geloescht, die mit der Entannotierung von Apparat und GWTK-Inhaltsangaben jeden Korpusbeleg verloren haben (neuhochdeutsche Woerter aus den Inhaltsangaben, Apparatsigel, das Ziffern-Lemma 46). lemma_66692 Mur bleibt trotz fehlender Belege, weil lemma_33528 Murouwe und lemma_66691 Murstat per etym auf ihn verweisen. variants.xml regeneriert: 275 Typen und 166 Eintraege entfallen, keiner kommt dazu, keiner wird umgehaengt. 1.9.13: #237 VTC-Editionsnachweis aus Zotero: Josef Jirecek als Mitherausgeber von FRB III, 'IV' statt 'Iv'. Nur dieses Werk; die uebrigen Aenderungen eines Online-Syncs sind bewusst nicht uebernommen.
const CACHE_DURATION = 30 * 24 * 60 * 60 * 1000; // 30 days in milliseconds

class CorpusLoader {
    constructor(basePath = 'data') {
        this.basePath = basePath; // Allow custom base path (e.g., '../data' from playground)
        this.db = null;
        this.dbReady = this.initDatabase();
    }

    async initDatabase() {
        try {
            // Initialize Dexie database
            this.db = new Dexie('MHDBDBMainSite');

            this.db.version(1).stores({
                indices: 'name, version, timestamp, data'
            });

            await this.db.open();

            console.log('[CorpusLoader] IndexedDB initialized');
        } catch (error) {
            console.error('[CorpusLoader] Failed to initialize IndexedDB:', error);
            throw error;
        }
    }

    /**
     * Load authority index (persons, works, lemmata, variants)
     */
    async loadAuthorityIndex() {
        await this.dbReady;
        const cachedIndex = await this.getCachedIndex('authority-index');

        if (cachedIndex) {
            console.log('[CorpusLoader] Using cached authority index');
            return cachedIndex;
        }

        console.log('[CorpusLoader] Fetching authority index from network...');

        try {
            const response = await fetch(`${this.basePath}/authority-index.json.gz`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const compressedData = await response.arrayBuffer();
            const decompressedData = pako.ungzip(new Uint8Array(compressedData), { to: 'string' });
            const index = JSON.parse(decompressedData);

            console.log(`[CorpusLoader] Authority index loaded: ${index.lemmata.length} lemmata, ${Object.keys(index.variants).length} variant mappings`);

            // Cache for future use
            await this.cacheIndex('authority-index', index);

            return index;

        } catch (error) {
            console.error('[CorpusLoader] Failed to load authority index:', error);
            throw new Error(`Authority index konnte nicht geladen werden: ${error.message}`);
        }
    }

    /**
     * Load corpus index (texts metadata and lemma positions)
     */
    async loadCorpusIndex() {
        await this.dbReady;
        const cachedIndex = await this.getCachedIndex('corpus-index');

        if (cachedIndex) {
            console.log('[CorpusLoader] Using cached corpus index');
            return cachedIndex;
        }

        console.log('[CorpusLoader] Fetching corpus index from network...');

        try {
            const response = await fetch(`${this.basePath}/corpus-index.json.gz`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const compressedData = await response.arrayBuffer();
            const decompressedData = pako.ungzip(new Uint8Array(compressedData), { to: 'string' });
            const index = JSON.parse(decompressedData);

            console.log(`[CorpusLoader] Corpus index loaded: ${index.texts.length} texts indexed`);

            // Cache for future use
            await this.cacheIndex('corpus-index', index);

            return index;

        } catch (error) {
            console.error('[CorpusLoader] Failed to load corpus index:', error);
            throw new Error(`Korpus-Index konnte nicht geladen werden: ${error.message}`);
        }
    }

    /**
     * Get cached index from IndexedDB
     */
    async getCachedIndex(name) {
        try {
            const cached = await this.db.indices.get(name);

            if (!cached) {
                return null;
            }

            const expectedVersion = name === 'corpus-index' ? INDEX_VERSION : AUTHORITY_INDEX_VERSION;
            if (cached.version !== expectedVersion) {
                console.log(`[CorpusLoader] Cache version mismatch for ${name}: ${cached.version} != ${expectedVersion}`);
                await this.db.indices.delete(name);
                return null;
            }

            // Check expiration
            const age = Date.now() - cached.timestamp;
            if (age > CACHE_DURATION) {
                console.log(`[CorpusLoader] Cache expired for ${name} (age: ${Math.round(age / (24 * 60 * 60 * 1000))} days)`);
                await this.db.indices.delete(name);
                return null;
            }

            return cached.data;

        } catch (error) {
            console.error(`[CorpusLoader] Failed to read cache for ${name}:`, error);
            return null;
        }
    }

    /**
     * Cache index in IndexedDB
     */
    async cacheIndex(name, data) {
        try {
            const version = name === 'corpus-index' ? INDEX_VERSION : AUTHORITY_INDEX_VERSION;

            await this.db.indices.put({
                name: name,
                version: version,
                timestamp: Date.now(),
                data: data
            });

            console.log(`[CorpusLoader] Cached ${name} (version ${version})`);

        } catch (error) {
            console.error(`[CorpusLoader] Failed to cache ${name}:`, error);
            // Non-critical error, continue without caching
        }
    }

}

export { CorpusLoader, INDEX_VERSION, AUTHORITY_INDEX_VERSION };
