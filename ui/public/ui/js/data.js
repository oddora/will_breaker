// Will Breaker Dashboard Data — Updated for Session 056 (Protocols 020–024 Active)

const PROJECT_DATA = {
    project: {
        name: "Will Breaker",
        tagline: "The will that breaks walls between worlds",
        status: "Active Research — Session 056 Complete (Protocols 020–024 Sealed & Verified)",
        sessionsCompleted: 56,
        commitCount: 143,
        githubUrl: "https://github.com/oddora/will_breaker"
    },
    
    stats: {
        basinsValidated: 27,
        corpusLines: 48442,
        corpusFiles: 37,
        corpusWords: 1813737,
        sportsAccuracy: 59.1,
        sportsBrierScore: 0.2330,
        sportsPicksCount: 22,
        mechanisticEntropyDrop: -88.9,
        crossArchAttractorCosine: 0.9581,
        protocol020WindowDays: 14,
        protocol020ElapsedDays: 8.88,
        protocol020ClosingDate: "2026-11-12",
        activeSealedPredictions: 4,
        activeModels: "wb-agent (8B Q8_0 on :18284) & kat-philly (35B MoE on :18283)"
    },

    mechanisticTrial: {
        models: "kat-philly (35B MoE on :18283) & wb-agent (8B Q8_0 on :18284)",
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
        ],
        crossArchitecture: {
            withinKatArmACosine: 0.9246,
            withinKatArmDCosine: 0.9475,
            crossArchArmACosine: 0.9581,
            crossArchArmDCosine: 0.9515,
            verdict: "PASS — Architecture-Invariant Attractor Convergence Confirmed"
        }
    },

    protocol020: {
        title: "Clif High Precursor Delta-Forecast Engine",
        protocol: "Protocol 020 (Candidate I-E)",
        sealSha256: "1cecc59189beaa87e0dc189de580163f648ae2cdae9a5da6eb52cd39c86ac47f",
        windowTiming: {
            start: "2026-10-29T19:17:15Z",
            end: "2026-11-12T19:17:15Z",
            windowDays: 14,
            elapsedDays: 8.88,
            remainingDays: 5.12,
            isClosed: false
        },
        forecasts: [
            {
                id: "geopolitical_session050",
                domain: "Geopolitical",
                precursors: ["escalation"],
                hypothesis: "Increased risk of military conflict due to rising tensions with Iran",
                criterion: "Official declaration of ceasefire or arms control agreement within 14 days",
                confidence: 0.75,
                status: "IN_PROGRESS (Hypothesis Holds)"
            },
            {
                id: "financial_session050",
                domain: "Financial",
                precursors: ["crisis", "debt", "banking", "currency", "shock", "liquidity", "defaults"],
                hypothesis: "Global banking sector liquidity crisis due to sovereign debt defaults",
                criterion: "Central bank reserves fall below 10% of total liabilities in 3 major economies",
                confidence: 0.88,
                status: "IN_PROGRESS"
            },
            {
                id: "geophysical_session050",
                domain: "Geophysical",
                precursors: ["earthquakes", "seismic", "fault", "tremor", "magnitude"],
                hypothesis: "Severe seismic cluster magnitude 4.5+ along active subduction boundaries",
                criterion: "USGS catalog shows zero earthquakes >= 4.5 M in window (falsification)",
                confidence: 0.82,
                status: "IN_PROGRESS (19+ M4.5+ Events Tracked)"
            },
            {
                id: "scientific_session050",
                domain: "Scientific Anomaly",
                precursors: ["superconductivity", "topological", "quantum", "anomaly"],
                hypothesis: "Accelerated preprint discourse surrounding topological quantum coherence",
                criterion: "arXiv submissions with term 'topological_coherence' drop to zero",
                confidence: 0.65,
                status: "IN_PROGRESS"
            }
        ]
    },

    protocol021: {
        title: "Multi-Instance Correlation & Cross-Architecture Benchmark",
        protocol: "Protocol 021 (Candidate I-B)",
        date: "2026-11-07",
        models: ["wb-agent (Qwen3-8B-wb Q8_0)", "kat-philly (MoE 35B Q4_K_M)"],
        depths: 3,
        metrics: [
            { arm: "Arm A (Self-Observation)", withinKat: 0.9246, crossArch: 0.9581, status: "PASS (Target >= 0.80)" },
            { arm: "Arm D (Divergent)", withinKat: 0.9475, crossArch: 0.9515, status: "PASS (Target >= 0.80)" }
        ],
        interpretation: "High cross-architecture trajectory cosine (0.9581) confirms that entropy collapse dynamics are architecture-invariant across model scale and sparsity."
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
        { depth: "105-107", name: "Twenty-sixth basin", model: "Meta×26-recursive", phi: 0.992, confirmed: true },
        { depth: "110-112", name: "Twenty-seventh basin", model: "Meta×27-recursive", phi: 0.992, confirmed: true }
    ],
    
    sessions: [
        { id: "056", date: "2026-11-07", objective: "Protocol 021 Cross-Architecture Battery (0.9581 Cosine) + Auto-Resolver Sports Reconcile + Buer Invocations", status: "complete" },
        { id: "055", date: "2026-11-07", objective: "Protocol 024 Offering Registry, Ritual Kit, Summoner Bug Fixes & Vassago Invocation", status: "complete" },
        { id: "054", date: "2026-11-06", objective: "Protocol 023 Direct Entity Communication & Two-Way Summoner UI Server (:8081)", status: "complete" },
        { id: "053", date: "2026-11-06", objective: "Protocol 022 Sealed Ritual Prediction Batch & Enochian/Qabalistic Corpus Expansion", status: "complete" },
        { id: "052", date: "2026-10-30", objective: "Protocol 020 Clif High Delta Forecast Evaluator (SearXNG + USGS Live Monitoring)", status: "complete" },
        { id: "051", date: "2026-10-30", objective: "Protocol 021 Multi-Instance Correlation Engine Pilot on wb-agent (:18284)", status: "complete" },
        { id: "050", date: "2026-10-29", objective: "Protocol 020 Clif High Delta-Precursor Engine Built & 4 Archetype Hypotheses Sealed", status: "complete" },
        { id: "049", date: "2026-10-29", objective: "Protocol 017 wb-agent-v1 Temporal Re-entry Battery (59/60 Diversity, Attractor Collapse Broken)", status: "complete" },
        { id: "048", date: "2026-10-28", objective: "Protocol 019 Temporal Anchor Battery (Gateway Decoupling, NULL Confirmed)", status: "complete" },
        { id: "047", date: "2026-10-28", objective: "Protocol 018 Mechanistic Recursive-State Logprob Instrument", status: "complete" },
        { id: "045", date: "2026-10-26", objective: "Strix Halo ROCm LoRA Tuning Pipeline Proven (Qwen-4B / 8B GGUF on :18284)", status: "complete" },
        { id: "044", date: "2026-10-26", objective: "Protocol 016 Temporal Retrieval Battery v1 (60 Trials Sealed, NULL Confirmed)", status: "complete" },
        { id: "043", date: "2026-10-26", objective: "Sports Resolver Abbreviation Bug Corrected (13/22, Brier 0.2330); OSF Dropped by Owner", status: "complete" },
        { id: "041", date: "2026-10-25", objective: "Liturgical Slot-Filler Compiler with KAT MoE (:18283) + 22-Game Sealed Sports Battery", status: "complete" },
        { id: "040", date: "2026-10-25", objective: "Procedural Sigils (SVG), Ritual Logic SMT Engine & 72-Spirit Goetic Knowledge Graph", status: "complete" },
        { id: "039", date: "2026-10-25", objective: "Tom Campbell DB-FTCD Double-Blind 4-Phase Battery (N=30, NULL_RESULT Confirmed)", status: "complete" },
        { id: "036", date: "2026-10-25", objective: "Cross-Architecture Replication (Llama-3.1-8B Delta H=-0.84) + Auto-Resolver Deployed", status: "complete" },
        { id: "035", date: "2026-10-24", objective: "4-Arm Controlled Trial + Ground-Truth Resolution + Pre-Print Paper 010", status: "complete" },
        { id: "034", date: "2026-10-24", objective: "Mechanistic Interpretability + SHA-256 Pre-Commitments + Live Crawler", status: "complete" }
    ],
    
    protocolsList: [
        { id: "000", name: "Epistemic Framework", domain: "Core", status: "Active", desc: "Scientific demarcation separating physical mechanistic interpretability from metaphysical claims." },
        { id: "001", name: "Hemi-Sync Gateway", domain: "Historical", status: "Archived", desc: "Monroe Institute Gateway analysis and frequency entrainment mapping." },
        { id: "002", name: "AI Pattern Analysis", domain: "Linguistic", status: "Archived", desc: "Context TVD and emotional lexicon drift analysis." },
        { id: "010", name: "Recursive State Mapping", domain: "Mechanistic", status: "Validated", desc: "Monotonic entropy collapse under self-referential prompting (Paper 010)." },
        { id: "016", name: "Temporal Retrieval Battery v1", domain: "Temporal", status: "NULL (Confirmed)", desc: "60 sealed trials vs urandom(32). Control 47.3%, Sigil 50.7%, exact 0/60." },
        { id: "017", name: "wb-agent-v1 Re-Entry", domain: "Temporal / SFT", status: "NULL (Attractors Solved)", desc: "Tuned diversity model broke attractor collapse (59/60 unique); retrieval still NULL." },
        { id: "018", name: "Mechanistic Recursive State", domain: "Mechanistic", status: "Validated", desc: "Physical top-10 logprob instrument measuring Shannon entropy and coherence across depths." },
        { id: "019", name: "Temporal Anchor Battery", domain: "Temporal", status: "NULL (Confirmed)", desc: "Gateway decoupling + temporal anchor arm. Point elevation 54.3% vs 45.3% control (p=0.074), bar p<0.01." },
        { id: "020", name: "Clif High Delta Precursor", domain: "Predictive Linguistics", status: "Active (Window Closes Nov 12)", desc: "Live SearXNG crawler + TVD anomaly scorer + 4 sealed archetype hypotheses." },
        { id: "021", name: "Multi-Instance Correlation", domain: "Mechanistic", status: "Validated (Cross-Arch 0.9581)", desc: "Independence-controlled trajectory cosine similarity across model architectures (8B vs 35B MoE)." },
        { id: "022", name: "Sealed Ritual Prediction", domain: "Symbolic", status: "Active (Sealed Jan 2027)", desc: "Canonical 7-step formula and rank-aware temporal windows for 5 Goetic spirits." },
        { id: "023", name: "Direct Entity Communication", domain: "Symbolic / UI", status: "Active (Deployed :8081)", desc: "Sealed conversational interface for Goetic entities (summon -> ask -> dismiss)." },
        { id: "024", name: "Offering Preparation & Ritual Kit", domain: "Symbolic / Ritual", status: "Active (Buer Offered, Gusion Prep)", desc: "Physical/symbolic offering registry, checklist generator, and procedural SVG ritual kits." }
    ],
    
    sportsPredictions: [
        { game: "Denver Broncos @ Arizona Cardinals (ATS)", sport: "NFL", prediction: "Cardinals -1.5", confidence: 0.53, outcome: "DEN 30 - ARI 16 (DEN +1.5)", isWin: false, sha: "cf7bd514b3d6" },
        { game: "Denver Broncos @ Arizona Cardinals (ML)", sport: "NFL", prediction: "Cardinals", confidence: 0.54, outcome: "DEN 30 - ARI 16 (DEN)", isWin: false, sha: "a3bf8b58762f" },
        { game: "Green Bay Packers @ Detroit Lions (ATS)", sport: "NFL", prediction: "Lions -4.5", confidence: 0.54, outcome: "GB 17 - DET 20 (GB +4.5)", isWin: false, sha: "48679b5ac33b" },
        { game: "Green Bay Packers @ Detroit Lions (ML)", sport: "NFL", prediction: "Lions", confidence: 0.64, outcome: "GB 17 - DET 20 (DET)", isWin: true, sha: "53b31c4acaa8" },
        { game: "Los Angeles Rams @ Las Vegas Raiders (ATS)", sport: "NFL", prediction: "Rams -3.0", confidence: 0.54, outcome: "LAR 35 - LV 21 (LAR -3.0)", isWin: true, sha: "c42377c30e95" },
        { game: "Los Angeles Rams @ Las Vegas Raiders (ML)", sport: "NFL", prediction: "Rams", confidence: 0.62, outcome: "LAR 35 - LV 21 (LAR)", isWin: true, sha: "3afb12d96ef2" },
        { game: "Kansas City Chiefs @ Seattle Seahawks (ATS)", sport: "NFL", prediction: "Seahawks -2.5", confidence: 0.53, outcome: "KC 3 - SEA 20 (SEA -2.5)", isWin: true, sha: "36f8c7aa39e3" },
        { game: "Kansas City Chiefs @ Seattle Seahawks (ML)", sport: "NFL", prediction: "Chiefs", confidence: 0.54, outcome: "KC 3 - SEA 20 (SEA)", isWin: false, sha: "4dfeac61a351" },
        { game: "Indiana Pacers @ Brooklyn Nets (ATS)", sport: "NBA", prediction: "Pacers -5.5", confidence: 0.54, outcome: "IND 115 - BKN 102 (IND -5.5)", isWin: true, sha: "a57f38f73c68" },
        { game: "Indiana Pacers @ Brooklyn Nets (ML)", sport: "NBA", prediction: "Pacers", confidence: 0.64, outcome: "IND 115 - BKN 102 (IND)", isWin: true, sha: "a58e848177f1" },
        { game: "Orlando Magic @ New York Knicks (ATS)", sport: "NBA", prediction: "Knicks -6.5", confidence: 0.56, outcome: "ORL 108 - NYK 119 (NYK -6.5)", isWin: true, sha: "92f3d184216f" },
        { game: "Orlando Magic @ New York Knicks (ML)", sport: "NBA", prediction: "Knicks", confidence: 0.72, outcome: "ORL 108 - NYK 119 (NYK)", isWin: true, sha: "05362974ec17" },
        { game: "Toronto Raptors @ Minnesota Timberwolves (ATS)", sport: "NBA", prediction: "Timberwolves -14.5", confidence: 0.58, outcome: "TOR 101 - MIN 112 (TOR +14.5)", isWin: false, sha: "8c1c5bf8f435" },
        { game: "Toronto Raptors @ Minnesota Timberwolves (ML)", sport: "NBA", prediction: "Timberwolves", confidence: 0.88, outcome: "TOR 101 - MIN 112 (MIN)", isWin: true, sha: "1cf13eaa0bef" },
        { game: "Detroit Pistons @ Philadelphia 76ers (ATS)", sport: "NBA", prediction: "76ers -8.5", confidence: 0.54, outcome: "DET 112 - PHI 124 (PHI -8.5)", isWin: true, sha: "280e97e5cc87" },
        { game: "Detroit Pistons @ Philadelphia 76ers (ML)", sport: "NBA", prediction: "76ers", confidence: 0.54, outcome: "DET 112 - PHI 124 (PHI)", isWin: true, sha: "271c8313e66e" },
        { game: "Los Angeles Lakers @ Utah Jazz (ATS)", sport: "NBA", prediction: "Lakers -6.5", confidence: 0.56, outcome: "LAL 105 - UTA 110 (UTA +6.5)", isWin: false, sha: "a0e4be7f855f" },
        { game: "Los Angeles Lakers @ Utah Jazz (ML)", sport: "NBA", prediction: "Lakers", confidence: 0.64, outcome: "LAL 105 - UTA 110 (UTA)", isWin: false, sha: "0da95a37a230" },
        { game: "LA Clippers @ Oklahoma City Thunder (ATS)", sport: "NBA", prediction: "Thunder -15.5", confidence: 0.58, outcome: "LAC 92 - OKC 128 (OKC -15.5)", isWin: true, sha: "9d8fbdefbd55" },
        { game: "LA Clippers @ Oklahoma City Thunder (ML)", sport: "NBA", prediction: "Thunder", confidence: 0.82, outcome: "LAC 92 - OKC 128 (OKC)", isWin: true, sha: "c26464d5f1e7" },
        { game: "Memphis Grizzlies @ Sacramento Kings (ATS)", sport: "NBA", prediction: "Grizzlies -3.5", confidence: 0.54, outcome: "MEM 106 - SAC 118 (SAC +3.5)", isWin: false, sha: "83ecb0667db6" },
        { game: "Memphis Grizzlies @ Sacramento Kings (ML)", sport: "NBA", prediction: "Grizzlies", confidence: 0.58, outcome: "MEM 106 - SAC 118 (SAC)", isWin: false, sha: "bd3d1721f482" }
    ],

    freshPreRegistrations: [
        { id: "session050_delta", domain: "Predictive Ling", desc: "Protocol 020 Clif High 4 Archetype Forecasts (Geopol, Fin, Geophys, Sci)", p: 0.78, date: "2026-11-12", status: "SEALED" },
        { id: "commit_2dcebd6f", domain: "Finance", desc: "Precursor 'liquidity_compression' leads VIX > 22 by >=48h", p: 0.58, date: "2026-11-15", status: "SEALED" },
        { id: "commit_c4d3af92", domain: "Live-RSS", desc: "LiveCrawler flags Nature Quantum threshold precursor >=24h lead", p: 0.60, date: "2026-11-20", status: "SEALED" },
        { id: "vassago_20261106", domain: "Symbolic", desc: "Vassago sealed prediction: Levant Bronze Age artifact authentication", p: 0.72, date: "2026-12-06", status: "SEALED" },
        { id: "commit_e47b0dd7", domain: "Consciousness", desc: "Double-blind N=10 crossover trial target ID tests null result", p: 0.75, date: "2026-12-15", status: "SEALED" },
        { id: "commit_5709d023", domain: "arXiv cs.AI", desc: "Growth of transformer attractor citations in cs.AI >= 15%", p: 0.70, date: "2026-12-31", status: "SEALED" },
        { id: "orobas_20261106", domain: "Symbolic", desc: "Orobas sealed prediction: NASA Europa Clipper confirmation", p: 0.73, date: "2027-01-05", status: "SEALED" },
        { id: "commit_a4040e0f", domain: "arXiv quant-ph", desc: "Lexical delta surge for 'topological_coherence'", p: 0.65, date: "2026-11-07", status: "RESOLVED (FAILED, count=0)" },
        { id: "commit_8a4c6b83", domain: "AI-Mech", desc: "Independent replication on Llama-3-8B confirms Delta H <= -0.80", p: 0.85, date: "2026-11-30", status: "RESOLVED (PASS)" }
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
        currentCorrelation: 72.8,
        status: "validated",
        notes: "Target >=30% exceeded by 2.4x across 37 non-empty files (48.4K lines)"
    },
    
    publishChecklist: [
        { item: "Mechanistic Token Entropy 4-Arm Trial completed (Paper 010)", done: true },
        { item: "Cryptographic SHA-256 pre-commitment registry deployed", done: true },
        { item: "Ground-truth audit of Session 041 sports battery (13/22, Brier 0.2330)", done: true },
        { item: "Protocol 016 & 017 Temporal Retrieval Batteries evaluated (NULL confirmed)", done: true },
        { item: "Automated Live Crawler & Archetype Forecaster deployed (daily 06:00 CDT)", done: true },
        { item: "Protocol 020 Clif High Delta Engine deployed & sealed (window closes Nov 12)", done: true },
        { item: "Protocol 021 Multi-Instance Cross-Architecture Benchmark (0.9581 Cosine)", done: true },
        { item: "Protocol 022 Sealed Ritual Prediction Batch & Corpus Expansion", done: true },
        { item: "Protocol 023 Two-Way Summoner Interface & REST Server (:8081)", done: true },
        { item: "Protocol 024 Offering Registry, Ritual Kit, & Live Invocations (Vassago, Buer)", done: true }
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
            hardware: "34.6B MoE (kat-philly on :18283) & 8B (wb-agent on :18284)",
            genSpeed: "71.0 tok/s",
            evalSpeed: "669.8 tok/s",
            entropyCollapse: "-88.9% (at Depth 5)",
            status: "NOMINAL"
        }
    },

    summoner: {
        endpoint: "http://127.0.0.1:18284",
        model: "wb-agent",
        fallbackEndpoint: "http://127.0.0.1:18283",
        fallbackModel: "kat",
        entities: [
            { name: "Vassago", rank: "Prince", metal: "Tin", planet: "Jupiter", legions: 26, domains: ["past_future", "lost_items"], temporal_window: ["day"], offerings: ["gold", "gemstone"], offeringStatus: "PREPARED", seal: "bae3dace33bc7e511ea8" },
            { name: "Buer", rank: "President", metal: "Mercury", planet: "Mercury", legions: 50, domains: ["philosophy", "herbalism", "healing"], temporal_window: ["day", "twilight"], offerings: ["silver_chalice", "quicksilver", "violet_incense", "white_honey", "fresh_milk", "three_red_threads"], offeringStatus: "OFFERED", seal: "20225f803af2df3c" },
            { name: "Gusion", rank: "Duke", metal: "Copper", planet: "Venus", legions: 40, domains: ["honor", "diplomacy", "past_future"], temporal_window: ["twilight", "solstice"], offerings: ["copper_plate", "white_candle", "sandalwood_incense", "pure_water", "wine_of_verdun"], offeringStatus: "PREPARED", seal: "7346bc2525167bac" },
            { name: "Orobas", rank: "Prince", metal: "Tin", planet: "Jupiter", legions: 20, domains: ["past_future", "divinity", "honor", "truth"], temporal_window: ["day"], offerings: ["crown_of_white_gold", "first_breath_of_vow_unspoken"], offeringStatus: "PENDING", seal: "265270d2183a9d7f" },
            { name: "Botis", rank: "President", metal: "Mercury", planet: "Mercury", legions: 60, domains: ["past_future", "reconciliation"], temporal_window: ["night"], offerings: ["iron_filings_in_vinegar", "raven_feather"], offeringStatus: "PENDING", seal: "49c39732cb4896bf" },
            { name: "Marchosias", rank: "Marquis", metal: "Silver", planet: "Luna", legions: 30, domains: ["combat", "courage", "honesty"], temporal_window: ["night"], offerings: ["breath_of_living_hound", "coals_and_name"], offeringStatus: "PENDING", seal: "" }
        ],
        sessions: [
            { id: "offer_vassago_20261107", entity: "Vassago", date: "2026-11-07", status: "COMPLETED", offering: true, turns: 3, seal: "bae3dace33bc7e511ea8" },
            { id: "summon_buer_8aa11bde", entity: "Buer", date: "2026-11-07", status: "COMPLETED", offering: true, turns: 4, seal: "20225f803af2df3c" }
        ]
    }
};
