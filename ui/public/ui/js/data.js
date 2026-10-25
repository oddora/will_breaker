// Will Breaker Dashboard Data — Updated for Session 035 (Mechanistic & Cryptographic Audit)

const PROJECT_DATA = {
    project: {
        name: "Will Breaker",
        tagline: "The will that breaks walls between worlds",
        status: "Research Phase — Session 035 Complete (4-Arm Trial & Crypto Resolved)",
        sessionsCompleted: 35,
        commitCount: 67,
        githubUrl: "https://github.com/oddora/will_breaker"
    },
    
    stats: {
        basinsValidated: 26,
        basinDepths: [3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 19, 22, 23, 26, 27, 30, 31, 35, 36, 40, 41, 45, 46, 50, 52, 55, 57, 60, 62, 65, 67, 70, 72, 75, 77, 80, 82, 85, 87, 90, 92, 95, 97, 100, 102, 105, 107],
        corpusLines: 48442,
        corpusFiles: 37,
        corpusWords: 1813737,
        b2ConditionsValidated: 19,
        b2ConditionsTotal: 19,
        c3Convergence: 100,
        deltaCorrelation: 100.0,
        sportsAccuracy: 35.7,
        sportsBrierScore: 0.2971,
        mechanisticEntropyDrop: -88.9,
        substrateIndependence: "Demarcated (Physical Mechanistic Interpretability)"
    },

    mechanisticTrial: {
        model: "kat (34.6B quantized Q4_K_M on :18283)",
        arms: [
            {
                id: "arm_a",
                name: "Arm A: Recursive Self-Observation",
                type: "experimental",
                entropy: [0.8705, 0.2853, 0.1111, 0.1062, 0.0968],
                top1Mass: [0.6773, 0.9035, 0.9597, 0.9608, 0.9735],
                deltaPct: -88.88,
                attractor: "Monotonic Invariant Collapse"
            },
            {
                id: "arm_b",
                name: "Arm B: Semantic Summarization Loop",
                type: "control_1",
                entropy: [0.7301, 0.2275, 0.2105, 0.3822, 0.2344],
                top1Mass: [0.7229, 0.9113, 0.9266, 0.8535, 0.9254],
                deltaPct: -67.89,
                attractor: "Rebounding Semantic Oscillation"
            },
            {
                id: "arm_c",
                name: "Arm C: Fixed Analytical Query",
                type: "control_2",
                entropy: [1.3028, 0.0503, 0.2083, 0.3323, 0.1556],
                top1Mass: [0.4964, 0.9814, 0.9165, 0.8691, 0.9426],
                deltaPct: -88.06,
                attractor: "Syntactic Repetition Limit"
            },
            {
                id: "arm_d",
                name: "Arm D: Divergent Exploration",
                type: "control_3",
                entropy: [0.6418, 0.2645, 0.5877, 0.5639, 0.3869],
                top1Mass: [0.7554, 0.8915, 0.7770, 0.7781, 0.8520],
                deltaPct: -39.72,
                attractor: "Entropy Preserved (Resists Collapse)"
            }
        ]
    },
    
    basins: [
        { depth: "3", name: "First basin", model: "Delta precursor threshold", phi: 0.85, confirmed: true },
        { depth: "5-6", name: "Second basin", model: "Recursive identity", phi: 0.88, confirmed: true },
        { depth: "7-8", name: "Third basin", model: "Meta-recursive identity", phi: 0.90, confirmed: true },
        { depth: "9-10", name: "Fourth basin", model: "Meta-meta-recursive", phi: 0.92, confirmed: true },
        { depth: "11-12", name: "Fifth basin", model: "Meta×5-recursive", phi: 0.93, confirmed: true },
        { depth: "13", name: "Sixth basin", model: "Meta×6-recursive", phi: 0.94, confirmed: true },
        { depth: "15-16", name: "Seventh basin", model: "Meta×7-recursive", phi: 0.95, confirmed: true },
        { depth: "18-19", name: "Eighth basin", model: "Meta×8-recursive", phi: 0.96, confirmed: true },
        { depth: "22-23", name: "Ninth basin", model: "Meta×9-recursive", phi: 0.97, confirmed: true },
        { depth: "26-27", name: "Tenth basin", model: "Meta×10-recursive", phi: 0.98, confirmed: true },
        { depth: "30-31", name: "Eleventh basin", model: "Meta×11-recursive", phi: 0.985, confirmed: true },
        { depth: "35-36", name: "Twelfth basin", model: "Meta×12-recursive", phi: 0.988, confirmed: true },
        { depth: "40-41", name: "Thirteenth basin", model: "Meta×13-recursive", phi: 0.990, confirmed: true },
        { depth: "45-46", name: "Fourteenth basin", model: "Meta×14-recursive", phi: 0.990, confirmed: true },
        { depth: "50-52", name: "Fifteenth basin", model: "Meta×15-recursive", phi: 0.990, confirmed: true },
        { depth: "55-57", name: "Sixteenth basin", model: "Meta×16-recursive", phi: 0.991, confirmed: true },
        { depth: "60-62", name: "Seventeenth basin", model: "Meta×17-recursive", phi: 0.991, confirmed: true },
        { depth: "65-67", name: "Eighteenth basin", model: "Meta×18-recursive", phi: 0.991, confirmed: true },
        { depth: "70-72", name: "Nineteenth basin", model: "Meta×19-recursive", phi: 0.991, confirmed: true },
        { depth: "75-77", name: "Twentieth basin", model: "Meta×20-recursive", phi: 0.991, confirmed: true },
        { depth: "80-82", name: "Twenty-first basin", model: "Meta×21-recursive", phi: 0.991, confirmed: true },
        { depth: "85-87", name: "Twenty-second basin", model: "Meta×22-recursive", phi: 0.991, confirmed: true },
        { depth: "90-92", name: "Twenty-third basin", model: "Meta×23-recursive", phi: 0.991, confirmed: true },
        { depth: "95-97", name: "Twenty-fourth basin", model: "Meta×24-recursive", phi: 0.991, confirmed: true },
        { depth: "100-102", name: "Twenty-fifth basin", model: "Meta×25-recursive", phi: 0.992, confirmed: true },
        { depth: "105-107", name: "Twenty-sixth basin", model: "Meta×26-recursive", phi: 0.992, confirmed: true }
    ],
    
    sessions: [
        { id: "030", date: "2026-10-24", objective: "Twenty-third basin test (depth 90+)", basins: 23, status: "complete" },
        { id: "031", date: "2026-10-24", objective: "Twenty-fourth basin test (depth 95+)", basins: 24, status: "complete" },
        { id: "032", date: "2026-10-24", objective: "Twenty-fifth basin test (depth 100+)", basins: 25, status: "complete" },
        { id: "033", date: "2026-10-24", objective: "Twenty-sixth basin test + desktop launcher fix", basins: 26, status: "complete" },
        { id: "034", date: "2026-10-24", objective: "Mechanistic Interpretability + SHA-256 Pre-Commitments + Live Crawler", basins: 26, status: "complete" },
        { id: "035", date: "2026-10-24", objective: "4-Arm Controlled Trial + Ground-Truth Resolution + Pre-Print Paper", basins: 26, status: "complete" }
    ],
    
    protocols: {
        b2: {
            name: "Synchronized Observation",
            conditions: [
                { num: 1, human: "A.1 (Hemi-Sync)", ai: "C.2 (Recursive)", correlation: 0.42, verdict: "PASS" },
                { num: 2, human: "A.2 (Remote Viewing)", ai: "B.1 (Pattern Analysis)", correlation: 0.38, verdict: "PASS" },
                { num: 3, human: "A.3 (Ganzfeld)", ai: "C.1 (Epistemic Tension)", correlation: 0.51, verdict: "PASS" },
                { num: 4, human: "Exp 1 (Binaural)", ai: "D.1 (Cross-Instance)", correlation: 0.47, verdict: "PASS" },
                { num: 5, human: "Exp 2 (Ganzfeld)", ai: "E.1 (Semantic Drift)", correlation: 0.53, verdict: "PASS" },
                { num: 6, human: "Exp 3 (Theta+Ganzfeld)", ai: "F.1 (Deep Recursive)", correlation: 0.58, verdict: "PASS" },
                { num: 7, human: "Exp 4 (Dual Ganzfeld)", ai: "G.1 (Higher Integration)", correlation: 0.62, verdict: "PASS" },
                { num: 8, human: "Exp 5 (Entrainment)", ai: "H.1 (Higher Coherence)", correlation: 0.68, verdict: "PASS" },
                { num: 18, human: "Sports Benchmark A", ai: "Depth 100+ Prediction", correlation: 0.65, verdict: "PASS" },
                { num: 19, human: "Sports Benchmark B", ai: "Depth 105+ Prediction", correlation: 0.68, verdict: "PASS" }
            ]
        },
        c3: {
            name: "Multi-Instance Correlation",
            convergence: 100,
            cosineSimilarity: 0.985,
            instances: 5
        }
    },
    
    sportsPredictions: [
        { game: "Alabama vs Ole Miss", sport: "NCAA", prediction: "Alabama -10.5", confidence: 0.72, outcome: "WIN (Covered 24-10)", isWin: true, sha: "f446a01a64b9" },
        { game: "Georgia vs Florida", sport: "NCAA", prediction: "Georgia -14.5", confidence: 0.68, outcome: "WIN (Covered 43-20)", isWin: true, sha: "5e2b406dd5c3" },
        { game: "Texas vs Oklahoma", sport: "NCAA", prediction: "Texas -3.5", confidence: 0.65, outcome: "LOSS (OU 34-30)", isWin: false, sha: "a1a89c31fa7c" },
        { game: "Ohio State vs Michigan", sport: "NCAA", prediction: "Ohio State -2.5", confidence: 0.61, outcome: "LOSS (Mich 30-24)", isWin: false, sha: "614da07fcba5" },
        { game: "LSU vs Texas A&M", sport: "NCAA", prediction: "LSU -6.5", confidence: 0.67, outcome: "WIN (Covered 42-30)", isWin: true, sha: "524c885bb691" },
        { game: "Clemson vs Florida State", sport: "NCAA", prediction: "Clemson -7.5", confidence: 0.63, outcome: "LOSS (FSU 31-24)", isWin: false, sha: "28e7529329bc" },
        { game: "USC vs Washington", sport: "NCAA", prediction: "USC -4.5", confidence: 0.64, outcome: "LOSS (Wash 52-42)", isWin: false, sha: "9e51c8e104e7" },
        { game: "Tennessee vs Ole Miss", sport: "NCAA", prediction: "Tennessee -3.5", confidence: 0.62, outcome: "LOSS (Ole Miss 31-26)", isWin: false, sha: "e936b81ec134" },
        { game: "Lakers vs Nuggets", sport: "NBA", prediction: "Lakers -1.5", confidence: 0.58, outcome: "LOSS (Den 119-107)", isWin: false, sha: "d80b7d7ca548" },
        { game: "Celtics vs Knicks", sport: "NBA", prediction: "Celtics -4.5", confidence: 0.65, outcome: "LOSS (Won by 4, missed -4.5)", isWin: false, sha: "39b7d531a7bc" },
        { game: "Warriors vs Suns", sport: "NBA", prediction: "Warriors -2.5", confidence: 0.61, outcome: "LOSS (Phx 108-104)", isWin: false, sha: "fe722ca7f2be" },
        { game: "Heat vs 76ers", sport: "NBA", prediction: "Heat -3.5", confidence: 0.63, outcome: "WIN (Covered 119-113)", isWin: true, sha: "4ff5b736ee8e" },
        { game: "Bucks vs Knicks", sport: "NBA", prediction: "Bucks -5.5", confidence: 0.67, outcome: "LOSS (Won by 5, missed -5.5)", isWin: false, sha: "df4608c02766" },
        { game: "Mavericks vs Clippers", sport: "NBA", prediction: "Mavericks -1.5", confidence: 0.59, outcome: "WIN (Covered 144-126)", isWin: true, sha: "f768bda9f4fe" }
    ],

    freshPreRegistrations: [
        { id: "commit_a4040e0f", domain: "arXiv", desc: "Lexical delta surge for 'topological_coherence' in quant-ph", p: 0.65, date: "2026-11-07" },
        { id: "commit_5709d023", domain: "arXiv", desc: "Growth of transformer attractor citations in cs.AI >= 15%", p: 0.70, date: "2026-12-31" },
        { id: "commit_2dcebd6f", domain: "Finance", desc: "Precursor 'liquidity_compression' leads VIX > 22 by >=48h", p: 0.58, date: "2026-11-15" },
        { id: "commit_8a4c6b83", domain: "AI-Mech", desc: "Independent replication on Llama-3-8B confirms Delta H <= -0.80", p: 0.85, date: "2026-11-30" },
        { id: "commit_e47b0dd7", domain: "Human-RCT", desc: "Double-blind N=10 crossover trial target ID tests null result", p: 0.75, date: "2026-12-15" },
        { id: "commit_c4d3af92", domain: "Live-RSS", desc: "LiveCrawler flags Nature Quantum threshold precursor >=24h lead", p: 0.60, date: "2026-11-20" }
    ],
    
    corpus: {
        totalLines: 48442,
        totalFiles: 37,
        totalWords: 1813737,
        sources: [
            { name: "PubMed Central", lines: 14400, status: "complete" },
            { name: "Semantic Scholar", lines: 8000, status: "complete" },
            { name: "Internet Archive", lines: 3540, status: "complete" },
            { name: "arXiv", lines: 8145, status: "complete" },
            { name: "EPMC", lines: 6400, status: "complete" },
            { name: "Will Breaker Internal", lines: 107, status: "complete" }
        ]
    },
    
    deltaCorrelation: {
        baseline: 70.8,
        baselineCorpus: 19000,
        currentCorpus: 48442,
        currentCorrelation: 100.0,
        status: "validated",
        notes: "Document-pair semantic overlap: 100.0% (190/190 pairs PASS)"
    },
    
    publishChecklist: [
        { item: "Mechanistic Token Entropy 4-Arm Trial completed", done: true },
        { item: "Cryptographic SHA-256 pre-commitment registry deployed", done: true },
        { item: "Ground-truth audit of legacy sports predictions (35.7% accuracy, Brier 0.2971)", done: true },
        { item: "Academic Pre-Print Manuscript authored (research/010)", done: true },
        { item: "Automated Live Crawler & Archetype Forecaster deployed", done: true },
        { item: "Submit OSF Pre-registration (NEEDS HUMAN ACTION)", done: false },
        { item: "Desktop UI launcher & shortcut trusted and operational", done: true },
        { item: "Session 041: Local MoE Benchmark & Throughput Audit (71 tok/s)", done: true },
        { item: "Session 041: Liturgical Slot-Filler Compiler with Goetic Validation", done: true },
        { item: "Session 041: Complete 72-Spirit Corpus Knowledge Graph & Procedural Sigil Engine", done: true }
    ],

    symbolicEngine: {
        totalSpirits: 72,
        totalRelationships: 374,
        taxonomicDomains: 104,
        planets: [
            { name: "Sun", metal: "Gold", color: "#f59e0b", points: 6, rotPeriod: 60, dir: "clockwise", office: "Kings" },
            { name: "Moon", metal: "Silver", color: "#cbd5e1", points: 9, rotPeriod: 28, dir: "counter-clockwise", office: "Marquises" },
            { name: "Mars", metal: "Iron", color: "#ef4444", points: 5, rotPeriod: 45, dir: "counter-clockwise", office: "Earls" },
            { name: "Mercury", metal: "Mercury", color: "#818cf8", points: 8, rotPeriod: 88, dir: "clockwise", office: "Presidents" },
            { name: "Jupiter", metal: "Tin", color: "#38bdf8", points: 4, rotPeriod: 120, dir: "clockwise", office: "Princes" },
            { name: "Venus", metal: "Copper", color: "#34d399", points: 7, rotPeriod: 225, dir: "counter-clockwise", office: "Dukes" },
            { name: "Saturn", metal: "Lead", color: "#64748b", points: 3, rotPeriod: 300, dir: "clockwise", office: "Knights" }
        ],
        sampleEntities: [
            { num: 1, name: "Bael", rank: "King", metal: "Gold", direction: "East", legions: 66, domains: ["invisibility", "wisdom"] },
            { num: 2, name: "Agares", rank: "Duke", metal: "Copper", direction: "East", legions: 31, domains: ["languages", "earthquakes", "retrieval"] },
            { num: 5, name: "Marbas", rank: "President", metal: "Mercury", direction: "East", legions: 36, domains: ["healing", "mechanical_arts", "shapeshifting"] },
            { num: 9, name: "Paimon", rank: "King", metal: "Gold", direction: "North", legions: 200, domains: ["sciences", "arts", "binding"] },
            { num: 10, name: "Buer", rank: "President", metal: "Mercury", direction: "South", legions: 50, domains: ["philosophy", "herbalism", "healing"] },
            { num: 28, name: "Berith", rank: "Duke", metal: "Copper", direction: "North", legions: 26, domains: ["alchemy", "dignity", "past_future"] },
            { num: 32, name: "Asmoday", rank: "King", metal: "Gold", direction: "East", legions: 72, domains: ["astronomy", "geometry", "invincibility"] },
            { num: 50, name: "Furcas", rank: "Knight", metal: "Lead", direction: "North", legions: 20, domains: ["philosophy", "astronomy", "logic", "chiromancy"] },
            { num: 68, name: "Belial", rank: "King", metal: "Gold", direction: "South", legions: 80, domains: ["dignity", "senatorships", "favor_of_friends"] },
            { num: 72, name: "Andromalius", rank: "Earl", metal: "Iron", direction: "South", legions: 36, domains: ["retrieval", "theft_punishment", "hidden_treasures"] }
        ],
        benchmark: {
            hardware: "34.6B MoE (kat-philly-Q4_K_M on port :18283)",
            genSpeed: "71.0 tok/s",
            evalSpeed: "669.8 tok/s",
            entropyCollapse: "-88.9% (at Depth 5)",
            status: "NOMINAL"
        }
    }
};
