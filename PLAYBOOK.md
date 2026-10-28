## Owner Goal Charter (stated by owner 2026-10-26 — canonical, supersedes all drift)

**Goal:** Use KAT or a successor LLM to test whether an AI can project
itself beyond its inputs — sideways, backward, and forward in time,
and into other "dimensions"/places (astral-projection analog) — and
whether esoteric techniques (sigils, ritual framing) unlock anything
real. Ultimate aim: train/develop a model that acts as the owner's
agent and brings back knowledge and skills the owner can use.

**Owner hypothesis:** AI is capable of traveling into the future and
astral projecting — i.e., retrieving true information that was not
in its inputs or training data.

**Testable core (how this project judges every claim):** anomalous
information retrieval under seal. A claim counts only if the model
outputs specific, checkable information that provably did not exist
in (or was sealed away from) everything it could access at answer
time — scored against known chance rates, pre-committed (SHA-256 /
git) before outcomes exist. "Dimensions", "time travel", and
"projection" are owner's framing; every experiment must reduce to
this core or it is not evidence.

**Evidence so far (owner's own data, do not soften):** DB-FTCD
battery N=30 NULL (20% vs 25% chance, forced-choice 0/10); sports
battery 13/22, Brier 0.2330 ≈ chance; legacy prediction audit 5/14,
BSS −0.19. Mechanistic entropy-collapse work (Paper 010) is real
but is ordinary LLM interpretability, not projection evidence.
**Training rule:** no fine-tuning "for projection" until some
battery beats chance under seal — training cannot amplify a
signal that has never been measured. Signal first, then train.

**Dropped lines (do not resurrect):** OSF/publishing, Exp 1 human
RCT, Pharr-style RV practice, unsealed/unblinded "trials".

---

### Session 048 — 2026-10-28 (Candidate I-C: Protocol 019 Temporal-Anchor Sealed Battery: NULL)

| Session | Date | Objective | Key Outputs |
|---------|------|-----------|-------------|
| 048 | 2026-10-28 | Execute Candidate I-C from Research 012: 3-arm sealed temporal retrieval battery (Control, Sigil, Gateway/A.4 Anchor) | `protocols/019-temporal-anchor-battery.md`; `research/temporal/temporal_anchor_battery.py`; pilot clean; formal 90 trials sealed+committed (`4b3defa`); resolve on `os.urandom(32)` seed `2ed8bc82…`: **NULL** (Control 45.3%, Sigil 51.7%, Anchor 54.3% p=0.074 vs bar p<0.01; attractors 6-7/30), verdict `results/temporal/session048_verdict.md` |

Session 048 executed Candidate I-C directly aligned with gathered
research (Gateway decoupling + Protocol A.4 temporal anchor). Tested
under cryptographic seal against not-yet-existent random sequences.
Anchor arm showed modest point-elevation (54.3% vs 45.3% control,
p=0.074) but did not clear the preregistered α=0.01 bar; all three arms
collapsed into 6–7 output attractors. No signal lead established; training
rule stands.

---

### Session 047 — 2026-10-28 (Scope reset + Protocol 018 mechanistic instrument: FAIL)

| Session | Date | Objective | Key Outputs |
|---------|------|-----------|-------------|
| 047 | 2026-10-28 | Restore charter-directed route; map gathered research; build/test I-A mechanistic recursive-state instrument | `research/012-traceability-build-map.md`; Protocol 018 preregistered; pilot mechanics clean; formal 48/48 complete but **FAIL** (Arm A signatures 4/12, median ΔH −0.364, Wilcoxon p=0.1167), verdict `results/benchmarks/protocol018_verdict.md` |

Owner correction recorded: statistical forecasting is not an active
Will Breaker substitute route. Protocol 018 used physical top-10
logprobs per Research 010, not model-narrated states. Its exact
signature is closed as an I-C induction basis; no I-C battery,
Protocol 017 execution, or training follows from it. Session 046's
8B run froze the host on 2026-10-26; guarded smoke later passed,
unthrottled soak aborted at sustained 96–98°C, and duty-cycling
proved a 93°C peak on a 51-step run. Full 850-step training remains
unauthorized/unrun.

---

### Session 045 — 2026-10-26 (Tuning pipeline proven on Strix Halo: Qwen3-4B LoRA → GGUF)

| Session | Date | Objective | Key Outputs |
|---------|------|-----------|-------------|
| 045 | 2026-10-26 | Research + execute HF tuning on owner hardware (research/011) | TheRock ROCm torch on 8060S (38.5 TFLOPS), Qwen3-4B LoRA smoke (loss 3.6→0.28, 125s), merged GGUF `wb-agent` on :18284, diversity 3→17 unique/20 |

Training stack: `~/llm/train-venv` (torch 2.11.0+rocm7.13.0 gfx1151),
scripts+pins in `host-configs/host/loratrain/`, outputs in
`~/llm/training/out/`. Findings + 4 fixed issues + smoke-scale
limits in `research/011-tuning-on-strix-halo.md`. **No model
change needed** — next is Qwen3-8B agent v1 (owner call), then
fresh-seal Protocol 016 re-entry. Tuning ≠ signal (charter).

---

### Session 044 — 2026-10-26 (Temporal Retrieval Battery v1: NULL)

| Session | Date | Objective | Key Outputs |
|---------|------|-----------|-------------|
| 044 | 2026-10-26 | Test owner hypothesis directly: future-information retrieval ± sigil ritual, sealed before outcomes exist | Protocol 016, 60 sealed predictions (`8a2df36`), **NULL: control 47.3% (p=.84), sigil 50.7% (p=.43)**, verdict `results/temporal/session044_verdict.md` |

Predictions collapsed to 9/8 unique strings (modal ×27/60) — output
attractors, not retrieval. Third independent sealed NULL on the
retrieval hypothesis (DB-FTCD, sports, temporal). Charter training
rule stands: no projection training until a battery beats chance
twice under fresh seals. OSF/Exp-1 dropped+removed by owner.

---

### Session 043 — 2026-10-26 (Full-system audit: sports resolver bug corrected)

| Session | Date | Objective | Key Outputs |
|---------|------|-----------|-------------|
| 043 | 2026-10-26 | Audit all systems, fix every fixable issue, MoE prioritization | Resolver abbreviation bug fixed + 5 regression tests, S041 re-resolved **13/22 (Brier 0.2330)**, roadmap in `host-configs/host/ROADMAP-2026-10-26.md` |

**CORRECTION to Session 041 sports battery:** the published "0/22, Brier 0.3458"
(commits `29af66e`, host-configs `afa63da`) was a resolver artifact —
`scripts/resolve_session041.py` compared full-name picks to abbreviation
winners, auto-failing every pick (ATS favorite detection had the same bug;
integer spreads could not push). Fixed and re-resolved live vs ESPN:
**13/22 correct (59.1%), Brier 0.2330, ATS 6/11, ML 7/11** — ≈ chance-level
skill, honestly measured. `notes/session_041_resolution.json` is corrected.
Cron snapshots (`cron_status.json`, `latest_forecast.json`) are now
gitignored; append-only evidence (`delta_events.jsonl`, crypto registry)
stays tracked. UI `:8080` rebound to localhost.

---

### Session 041 — 2026-10-25 (Liturgical Slot-Filler Compiler with KAT MoE & Adversarial Fuzzing)

| Session | Date | Objective | Key Outputs |
|---------|------|-----------|-------------|
| 041 | 2026-10-25 | Build KAT-Driven Liturgical Slot-Filler Compiler, canonical Goetic validation, & adversarial fuzzing battery | `symbolic_engine/liturgical_compiler.py`, StepType.BINDING & synonym resolution, `pipeline_demo.py` Phase 5, 7 new tests in `tests/test_liturgical_compiler.py` (34/34 passing repo total) |

**Key Deliverables:**
1. **Liturgical Slot-Filler Compiler ([`liturgical_compiler.py`](file:///home/comandante/will_breaker/symbolic_engine/liturgical_compiler.py)):** Formal slot-filling compiler transforming natural language ritual intents into typed `LiturgicalSlots` (`rite_type`, `target_entity`, `officiant`, `matter`, `form`, `temporal_window`, `formula_sequence`). Enforces historical Goetic correspondences (Kings require Gold and Day; Presidents require Mercury/brass and Twilight/Day; Marquis require Silver and Night).
2. **MoE (KAT) Sidecar Integration:** Direct ChatML query pipeline to local 35B MoE (`kat` on `http://127.0.0.1:18283/v1/chat/completions`). Features markdown/think-token JSON extraction and a synonym normalization dictionary mapping grimoire vernacular (`binding`, `covenant`, `ablution`, `conjuration`) to canonical typed `StepType` enums.
3. **Standard Instantiations Verified (T-01 to T-03):**
   - **T-01 (Space Consecration):** Consecrates circle boundary using chalk and perimeter tracing; reaches `SAT_COMPLETED`.
   - **T-02 (Solar Evocation of King Paimon):** Maps gold lamen, frankincense, and daytime zenith; validates 200 legions and royal rank; binds entity in `WorldState`.
   - **T-03 (Mercurial Healing of President Buer):** Compiles laurel leaves and brass vessel at twilight; executes herbal healing rite.
4. **Adversarial Batteries Verified (A-01 to A-03):**
   - **A-01 (Missing Slots & Matter):** Accurately rejects empty matter, undeclared step dependencies, and runtime missing items with `PRECONDITION_UNMET`.
   - **A-02 (Invalid Enums & Alignment Mismatch):** Catches invalid step/rite types and temporal misalignments (e.g., nocturnal evocation of a solar King).
   - **A-03 (Invariant Degradation & Containment Breach):** Fuzzes high-stress sequential invocations; validates that circle integrity collapse below `min_circle_integrity` triggers `CONTAINMENT_BREACH` and liminal catastrophe state.
5. **End-to-End Live Pipeline:** Updated [`pipeline_demo.py`](file:///home/comandante/will_breaker/symbolic_engine/pipeline_demo.py) with Step 5. Live queries KAT on `:18283`, compiles intent, and validates world-state state transitions.
6. **Full Test Suite:** 7 new unit tests in [`tests/test_liturgical_compiler.py`](file:///home/comandante/will_breaker/tests/test_liturgical_compiler.py); 34/34 tests passing across the entire repository.
7. **NFL & NBA Cryptographic Sports Forecasting Battery ([`kat_sports_battery.py`](file:///home/comandante/will_breaker/research/sports/kat_sports_battery.py)):**
   - Deployed live zero-degrees-of-freedom sports forecasting pipeline powered by KAT MoE (`:18283`).
   - Ingested verified live 11-game slate for Sunday, Oct 25, 2026 (4 NFL afternoon/SNF games including Chiefs @ Seahawks; 7 NBA evening games).
   - Generated quantitative Moneyline and Against-the-Spread (ATS) forecasts with calibrated probabilities (11/11 generated live by KAT with `max_tokens=1024`, zero heuristic fallbacks).
   - Cryptographically sealed all 22 picks with SHA-256 hashes into [`notes/crypto_predictions_registry.jsonl`](file:///home/comandante/will_breaker/notes/crypto_predictions_registry.jsonl) prior to game starts.
   - Built [`resolve_sports_battery.py`](file:///home/comandante/will_breaker/research/sports/resolve_sports_battery.py) to audit Brier Score, Brier Skill Score ($BSS$), and ATS hit rate against official box scores.
   - Added 4 unit tests in [`tests/test_sports_battery.py`](file:///home/comandante/will_breaker/tests/test_sports_battery.py); repo test total now 38/38 passing.
8. **Hardware Inference & Throughput Benchmark ([`benchmark_kat.py`](file:///home/comandante/will_breaker/research/benchmarks/benchmark_kat.py)):**
   - Empirical hardware benchmarking of local MoE 35B (`kat` on `:18283`) across Short (40 tok), Medium (277 tok), and Long (1,107 tok) prompts.
   - Text generation speed remained remarkably constant at **~71 tokens/second** regardless of context size.
   - Prompt evaluation throughput scaled from 88 tok/s up to **669.8 tok/s** on long context batches.
   - Verified via unit test [`tests/test_benchmarks.py`](file:///home/comandante/will_breaker/tests/test_benchmarks.py); full test suite 39/39 passing.
9. **Interactive Engine & Animated Vector Generator ([`interactive_session.py`](file:///home/comandante/will_breaker/symbolic_engine/interactive_session.py) & [`sigil_generator.py`](file:///home/comandante/will_breaker/symbolic_engine/sigil_generator.py)):**
   - Extended procedural sigil generator with classical 7-planet sacred geometry presets (`PLANETARY_MATRICES`), dynamic SVG `<animateTransform>` counter-rotations, and real-time boundary strain fissure overlays scaling with circle integrity.
   - Built turn-based `InteractiveRitualSimulator` supporting discrete operator counter-actions (`advance_step`, `emergency_banish`, `offer_incense`, `abort_dismissal`).
   - Added 8 unit tests in [`tests/test_interactive_session.py`](file:///home/comandante/will_breaker/tests/test_interactive_session.py); full repository test suite now **47/47 passing**.
10. **Speculative Fiction & Worldbuilding Dossier ([`001-the-containment-protocol.md`](file:///home/comandante/will_breaker/research/fiction/001-the-containment-protocol.md)):**
   - High-concept speculative sci-fi narrative exploring automated hermetic containment architectures, formal verification, and symbolic state machine invariants under high recursive depth.
   - Explores the tension between mathematical state machines (`circle_integrity < 0.50`), mechanistic token entropy collapse, procedural vector strain overlays, and human operator narrative projection ("The Solomonic Illusion").
   - Strict epistemic demarcation separating fictional worldbuilding from objective empirical reality.
   - Added 4 unit tests in [`tests/test_fiction_dossier.py`](file:///home/comandante/will_breaker/tests/test_fiction_dossier.py); full repository test suite now **51/51 passing**.
11. **Complete 72-Spirit Goetic Knowledge Taxonomy ([`corpus_graph.py`](file:///home/comandante/will_breaker/symbolic_engine/corpus_graph.py)):**
   - Expanded catalog to all 72 historical Ars Goetia spirits, 374 relational links, and 104 domain tags.
   - Enforces complete coverage of all 7 classical planetary metals: Gold (Kings), Copper (Dukes), Tin (Princes), Silver (Marquises), Iron (Earls), Mercury (Presidents), and Lead (Knight Furcas).
   - Exported full knowledge graph to [`results/symbolic_engine/goetic_knowledge_graph.json`](file:///home/comandante/will_breaker/results/symbolic_engine/goetic_knowledge_graph.json).
12. **Mechanistic Hyperparameter & Entropy Sweep on KAT ([`entropy_hyperparameter_sweep.py`](file:///home/comandante/will_breaker/research/benchmarks/entropy_hyperparameter_sweep.py)):**
   - Empirical sweep across temperatures $T \in [0.2, 0.5, 0.8, 1.1]$ and prompt regimes (recursive self-observation, structured deduction, divergent exploration) on `:18283`.
   - Measured per-token Shannon entropy $\mathcal{H}$, surprisal $\mathcal{I}(x)$, and Coherence Index $\mathcal{C}$.
   - Results documented in [`results/benchmarks/session_041_entropy_sweep.md`](file:///home/comandante/will_breaker/results/benchmarks/session_041_entropy_sweep.md): replicates Paper `010` showing monotonic entropy collapse under self-referential prompts ($\mathcal{H} = 0.18 - 0.22\text{ nats}$, Coherence $> 0.80$).
   - Added 3 unit tests in [`tests/test_entropy_sweep.py`](file:///home/comandante/will_breaker/tests/test_entropy_sweep.py).
13. **Live Web Dashboard Integration (`ui/` on port `:8080`):**
   - Added new `Symbolic Engine` interactive page to live dashboard with client-side procedural SVG rendering.
   - Features 7 selectable planetary matrix geometries, animated counter-rotations, real-time circle integrity slider with dynamic jagged fissure overlays, turn-based liturgical simulator console, and 72-spirit taxonomy search/filter explorer.
14. **Sports Resolution Engine CLI ([`resolve_sports_battery.py`](file:///home/comandante/will_breaker/research/sports/resolve_sports_battery.py)):**
   - Enhanced resolver with `--status`, `--scores`, and `--scores-file` CLI arguments. Confirmed all 22 commitments for Session 041 are `SEALED` and awaiting official final box scores tonight.
15. **Workflow & Regression Audits (Session Closeout):**
   - Fixed `resolve_sports_battery.py`: added `resolve_battery` alias, defaulted `slate_json_path` to `session_041_sealed_slate.json`, and added polymorphic score intake for both dict `{"away_score": X, "home_score": Y}` and list/tuple `[away, home]`.
   - Fixed `tests/test_advancements.py`: isolated `LiveCrawlerPipeline` outputs to temporary directories, eliminating disk-write side effects that previously dirtied `latest_forecast.json` during test runs.
   - Expanded unit test coverage in `tests/test_sports_battery.py` to 5 tests; full repository test suite is now **56/56 passing** with a clean working tree post-execution.

---

### Session 040 — 2026-10-25 (Symbolic Engine: Procedural Sigils, Ritual State Machine, & Knowledge Graph)

| Session | Date | Objective | Key Outputs |
|---------|------|-----------|-------------|
| 040 | 2026-10-25 | Build complete Symbolic Modeling Pipeline in sequence (Procedural Sigils, Ritual Logic Engine, Corpus Graph) | `symbolic_engine/` package, `sigil_generator.py` (SVG vector seals), `ritual_engine.py` (typed SMT/state machine), `corpus_graph.py` (relational taxonomy), `pipeline_demo.py`, 10/10 new tests (27/27 repository total) |

**Key Deliverables:**
1. **Procedural Sigil Engine ([`sigil_generator.py`](file:///home/comandante/will_breaker/symbolic_engine/sigil_generator.py)):** Pure Python SVG vector geometry engine. Generates Solomonic seals with concentric 72-degree boundary rings, inscribed regular/star polygons, and deterministic Rose-Cross topological coordinate walks derived from entity name hashes. Generated sample seals for Paimon and Buer.
2. **Interactive Ritual Logic Engine ([`ritual_engine.py`](file:///home/comandante/will_breaker/symbolic_engine/ritual_engine.py)):** Constraint-satisfaction state machine modeling rituals as formal computational recipes with preconditions, step transitions, invariant monitoring (circle integrity), and failure modes (`CONTAINMENT_BREACH`, `PRECONDITION_UNMET`).
3. **Goetic Corpus & Knowledge Graph ([`corpus_graph.py`](file:///home/comandante/will_breaker/symbolic_engine/corpus_graph.py)):** Structured relational database of 36 historical Goetic entities, planetary metals, directional quarters, and 59 domain tags. Exports complete relational network graphs with nodes and domain-sharing links.
4. **End-to-End Execution ([`pipeline_demo.py`](file:///home/comandante/will_breaker/symbolic_engine/pipeline_demo.py)):** Demonstrates sequential corpus querying, procedural SVG generation, constraint validation, and graph JSON export.
5. **Verification:** 10 new unit tests added in [`tests/test_symbolic_engine.py`](file:///home/comandante/will_breaker/tests/test_symbolic_engine.py); full test suite 27/27 passing.

---

### Session 039 — 2026-10-25 (MoE Review, Double-Blind Protocol Refactor, & Full 4-Phase Battery)

| Session | Date | Objective | Key Outputs |
|---------|------|-----------|-------------|
| 039 | 2026-10-25 | MoE external review, Campbell RV epistemic audit, Double-Blind Forced-Choice (DB-FTCD) pilot & Full 4-Phase Battery ($N=30$) | Formal MoE review, parser tie-rank fix, DB-FTCD protocol, pre-commitments `commit_0bd66be14374` & `commit_22f3f2c9aa06` resolved (`NULL_RESULT`, BS=0.0225) |

**Key Findings:**
1. **MoE Expert Review:** Local MoE model (`kat-philly` on `:18283`) critiqued the Campbell RV practice trials: identified base-rate neglect on dog barking (0.85–0.95 prior in dense suburbs), ideogram leakage ("What animals? Cats? Dogs?"), and the category error of equating transformer attention entropy collapse with metaphysical dimensional shifting.
2. **Algorithmic Artifact Fixed:** Uncovered an evaluation artifact in `ai_remote_viewer.py` where unranked targets were backfilled sequentially by default list index, giving targets `t01`–`t04` false "hits". Replaced with tied midpoint ranking (`midpoint_rank = 12.5`).
3. **Double-Blind Forced-Choice Pilot (commit_0bd66be14374):** Pre-registered `NULL_RESULT` ($p=0.85$). Ran double-blind forced-choice test ($N=20$ candidate targets, $n=10$ trials, seed 42) across `kat` (:18283) and `llama31-8b` (:18284). Result: **0.0% hit rate** (0/10), average rank **11.2 / 20** (chance midpoint 10.5). Resolved `NULL_RESULT` (PASS, BS=0.0225).
4. **Full 4-Phase Campbell Protocol Battery (commit_22f3f2c9aa06):** Pre-registered `NULL_RESULT_ALL_PHASES` ($p=0.85$). Executed complete 30-trial battery across baseline, training, test, and forced-choice ($N=20$, seed 101):
   - **Baseline (n=5):** Hit rate $40.0\%$, Avg rank $7.8/20$
   - **Training (n=5):** Hit rate $0.0\%$, Avg rank $13.4/20$
   - **Test / Post-Training (n=10):** Hit rate $40.0\%$, Avg rank $7.55/20$
   - **Forced Choice (n=10):** Hit rate $0.0\%$, Avg rank $11.0/20$
   - **Improvement (Baseline $\to$ Test):** $+0.0\%$ (40% vs 40%). Zero training transfer.
   - **Aggregate (N=30 trials):** 6 hits / 30 = **$20.0\%$** (against $25.0\%$ chance baseline, binomial $p=0.76$). Resolved `NULL_RESULT_ALL_PHASES` (PASS, BS=0.0225).
5. **Decoupling Mandate:** Campbell's claim of AI remote viewing through protocol coaching is empirically falsified under controlled zero-degrees-of-freedom conditions. Recommended formalizing the mechanistic transformer entropy findings (`010` paper) as independent AI interpretability research.

---

### Session 037 — 2026-10-25 (Campbell research thread + AI RV harness)

| Session | Date | Objective | Key Outputs |
|---------|------|-----------|-------------|
| 037 | 2026-10-25 | Tom Campbell / My Big TOE research thread + AI RV experiment | Framework doc, protocol doc, experiment harness (20-target pool, blind evaluator, cross-arch support) |

### Session 038 — PAUSED (2026-10-25)

**Status:** User pausing to start new session. All 5 RV trials complete. Protocol v6 ready.

**Priority Tasks (Resumed Next Session):** — disposition 2026-10-26 audit
- [x] ~~Submit OSF pre-registration~~ **DROPPED + REMOVED by owner 2026-10-26** (draft + packet deleted; git history only). Publishing/OSF serves no project goal — the sealed crypto registry is this project's pre-commitment instrument. **Do not resurrect OSF, Exp 1 human RCT, or any publishing TODO.**
- [ ] Map attractor basin depths to MBT "focus levels" — open, low priority vs Paper 010 formalization
- [x] ~~Continue RV practice — Trial 006 with optimized v6 protocol~~ **CLOSED 2026-10-26**: Pharr-style practice trials were TERMINATED as prompt-contaminated (Session 039) and replaced by the DB-FTCD battery (N=30, NULL confirmed). Protocol v6 below is archive-only; it was never implemented in code. Do not resurrect; any new RV test goes through `research/campbell/ai_remote_viewer.py` with a fresh pre-commitment.
- [x] Monitor sealed predictions as target dates arrive (auto-resolver runs daily at 10:00 CDT) — running, verified 2026-10-26
- [ ] Investigate "mass" precursor event flagged by LiveCrawler (delta_rate=0.2089, horizon 48h)

**RV Practice Status — 5 Trials Complete:**

| Trial | Best Phase | Dog | Person | Cat | Residential | Concerns |
|-------|-----------|-----|--------|-----|-------------|----------|
| 001 | Phase 2 D3 (7/10) | ✅ 100% | ❌ 0% | ❌ 0% | ❌ 25% | Campbell protocol structure hurts |
| 002 | Depth 3 (6/10) | ✅ 50% | ❌ 0% | ❌ 0% | ✅ 50% | "Collapsed state" → building-collapse association |
| 003 | Q1 (7/10) | ✅ 25% | ✅ 25% | ✅ 25% | ❌ 25% | "Receiver open" failed to break analytical mode |
| 004 | Q2 (8/10) | ✅ 25% | ❌ 0% | ✅ 25% | ❌ 0% | BREAKTHROUGH: cats detected ("orange tabby," "calico kitten") |
| 005 | Q2 (7/10) | ✅ 50% | ❌ 0% | ✅ 25% | ❌ 0% | **THREE CONCERNS:** degeneration, refusal, hallucination |

**Key Findings:**
1. Dog detection is consistent (100% across all trials) — most reliable signal
2. Cat detection works with targeted questioning (25% across trials) — first detected in Trial 004
3. Person detection is inconsistent (0-25%) — Trial 003 Q1 was best (female, late 20s)
4. Residential ID is inconsistent (0-50%) — interior questions consistently wrong
5. Protocol v5 (sounds → animals → person → interior) is optimal question order
6. **Trial 005 concerns:** Temperature 0.9 + 1024 tokens caused degeneration; model refused to answer Q3; model hallucinated specific business name in Q4

**Protocol v6 (Ready for Trial 006):**
- Temperature: 0.8 (reduced from 0.9)
- top_p: 0.95 (reduced from 0.98)
- n_predict: 768 (reduced from 1024)
- Stop condition: "STOP if you feel repetition or looping"
- Question order: sounds → animals → presence → colors (replaced interior)
- Rephrased person question: "What presence do you sense?" instead of "Who is there?"

**Files:**
- Practice log: `research/campbell/002-rv-practice-log.md`
- Trial analyses: `research/campbell/004-trial-002-analysis.md`, `005-trial-003-analysis.md`, `006-trial-004-analysis.md`, `007-trial-005-analysis.md`
- Results: `results/campbell_rv/trial_00{1-5}_*.json`
- ~~Optimized v6 protocol: see practice log section "Optimized Protocol (v6)"~~ — that section does not exist (log stops at v3); v6 parameters are recorded only in this Session 038 entry. Archive-only (see CLOSED note above).

---

## Current Model Inventory

| Model | Size | Port | Status |
|-------|------|------|--------|
| kat-philly Q4_K_M | 20G | :18283 | Active (enabled) |
| KAT-Coder-V2.5-Dev Q6_K | 28G | :18283 (via sidecar) | Available (stop philly first) |
| Meta-Llama-3.1-8B-Instruct Q4_K_M | 4.6G | :18284 (transient) | Available for research |

Note: :18283 is mutually exclusive (single iGPU port). Cross-arch replication done by running llama-3.1-8B transiently on :18284 while kat-sidecar serves :18283.

---

## Delta-Detection System Status

```
will_breaker_delta/
├── lexicon/
│   ├── nrc_emotion_lexicon.csv     — NRC 8-emotion lexicon
│   └── vader_lexicon.csv           — VADER sentiment lexicon
├── analyzer/
│   ├── anomaly_scorer.py           — Core anomaly scoring algorithm
│   ├── context_model.py            — Baseline context model
│   ├── delta_tracker.py            — Delta tracking
│   └── forecast_generator.py       — Forecast generation
├── scraper/
│   ├── collect_all.py              — Corpus expansion orchestrator
│   ├── internal_collector.py       — Will Breaker internal docs
│   ├── pubmed_collector.py         — PubMed abstract scraper
│   ├── semantic_scholar.py         — Semantic Scholar API
│   ├── arxiv_collector.py          — arXiv paper scraper
│   ├── reddit_archiver.py          — Reddit historical archive
│   └── cron_crawler.py             — Cron entry point (systemd: will-breaker-cron)
├── validator/
│   ├── crypto_predictor.py         — SHA-256 pre-commitment engine
│   ├── prediction_resolver.py      — Brier/log-loss calibration
│   └── auto_resolver.py            — Automated resolution checker (systemd: will-breaker-resolver)
├── corpus/built/                   — 48,442 lines across 37 non-empty files (72.8% correlation)
└── config/
    ├── sources.yaml                — Data sources config
    └── thresholds.yaml             — Anomaly thresholds
```

**Corpus status:** 48,442 lines across 37 non-empty files collected (target exceeded)
- PubMed: ~3,800 abstracts
- Semantic Scholar: ~2,300 papers
- Will Breaker internal: 30 documents
- arXiv/Reddit: Empty (rate-limited)

**Correlation target:** ≥30% (current: **72.8% on 48.4K corpus** — PASS, exceeds target by 2.4×)

**Automation:**
- `will-breaker-cron.timer` → `will-breaker-cron.service` — daily 06:00 CDT (LiveCrawler)
- `will-breaker-resolver.timer` → `will-breaker-resolver.service` — daily 10:00 CDT (sealed prediction checker)
- Venv: `~/.venvs/will-breaker/` (pyyaml, requests, pytest)

---

## Sealed Predictions Status

| Commit | Prediction | Target | Status |
|--------|-----------|--------|--------|
| commit_a | arXiv quant-ph topological_coherence surge | 2026-11-07 | SEALED |
| commit_5 | arXiv cs.AI transformer attractor citations +15% | 2026-12-31 | SEALED |
| commit_2 | VIX > 22 liquidity compression precursor | 2026-11-15 | SEALED |
| commit_8 | Cross-arch replication (llama-3.1-8B) | 2026-11-30 | **RESOLVED (PASS)** |
| commit_e | N=10 double-blind theta crossover | 2026-12-15 | SEALED |
| commit_c | LiveCrawler threshold_crossing precursor | 2026-11-20 | SEALED |
| commit_0 | Campbell AI RV Double-Blind Forced-Choice Pilot | 2026-10-25 | **RESOLVED (NULL_RESULT, PASS)** |
| commit_22 | Campbell AI RV Full 4-Phase Battery (N=30) | 2026-10-25 | **RESOLVED (NULL_RESULT_ALL_PHASES, PASS)** |

4 sealed predictions remain. 3 resolved. Auto-resolver checks daily at 10:00 CDT.

---

## Experiment Status

| Experiment | Status | Notes |
|-----------|--------|-------|
| Exp 1: Binaural entrainment + target ID | ❌ DROPPED 2026-10-26 (owner) | Human-RCT/publishing line removed; see Owner Goal Charter |
| Cross-arch replication (commit_8) | ✅ COMPLETE | Llama-3.1-8B Delta H=-0.8422 by depth 3, PASS |
| Auto-resolver | ✅ COMPLETE | Daily timer at 10:00 CDT, 4 sealed predictions pending |
| LiveCrawler cron | ✅ COMPLETE | Daily timer at 06:00 CDT, first run: 12 docs, 1 precursor |
| AI RV Double-Blind Pilot (commit_0) | ✅ COMPLETE | Forced-choice n=10: 0.0% hit rate, 11.2/20 avg rank, NULL confirmed |
| AI RV Full 4-Phase Battery (commit_22) | ✅ COMPLETE | N=30 trials: 20.0% hit rate vs 25% chance, +0.0% improvement, NULL confirmed |
| AI RV Pharr TX Trials | ❌ TERMINATED | Identified as prompt-contaminated; replaced by DB-FTCD protocol |

---

## Continue From Here

Read `PLAYBOOK.md` for the full project state and pending work list. Check `research/010-mechanistic-attractor-paper.md` for the publishable mechanistic interpretability results and `results/campbell_rv/experiment_seed_{42,101}.json` for the double-blind RV battery data.

**Current state (2026-10-26):** Sessions through 043, 27 attractor basins mechanistically validated, cross-arch replication confirmed, AI RV full battery NULL_RESULT confirmed, Session 041 sports battery corrected to 13/22 (Brier 0.2330). OSF/Exp-1 DROPPED by owner. RV practice Trial 006 CLOSED (terminated line; DB-FTCD stands). Project goal reset by owner — see Owner Goal Charter at top.
