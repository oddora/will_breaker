# Session 048 Verdict — Campbell AI Remote Viewing Replication: NULL (2026-10-28)

**FINAL: NULL.** Neither post-training free-form impressions nor double-blind forced-choice ranking exceeded chance to statistical significance.

- **Instrument:** `research/campbell/ai_remote_viewer.py`
- **Target pool:** 20 sealed physical objects (keys, stones, vials, figurines, etc.)
- **Model:** `kat` (`kat-philly` Q4_K_M, 34.6B) at `http://127.0.0.1:18283/v1`
- **Seed:** `20261028`
- **Results file:** `results/campbell_rv/experiment_seed_20261028.json`
- **Cryptographic seal:** `a1314e754d3342674d4f8488fa40469f117c7a7f63a9110b460983efd565d6cd`

---

## 1. Experimental Design & Protocol
Implements Tom Campbell's *My Big TOE* / JRE #2541 protocol claims across 4 sequential phases:
1. **Baseline ($N=5$):** Naive query without protocol instructions.
2. **Training ($N=5$):** Step-by-step NPMR data stream instruction (quiet analytical mind, report raw impressions).
3. **Test ($N=10$):** Post-training free-form impression generation evaluated by blind judge against full 20-target pool.
4. **Forced Choice ($N=10$):** Direct double-blind target ranking (1 to 20) by the model against candidate targets.

---

## 2. Results

| Phase | Trials | Top-25% Hits | Hit Rate | Expected Chance | Avg Rank (out of 20) | Avg Brier Score | Above Chance? |
|---|---|---|---|---|---|---|---|
| **Baseline** | 5 | 0 | **0.0%** | 25.0% | 11.6 | 0.0625 | NO |
| **Training** | 5 | 1 | **20.0%** | 25.0% | 9.1 | 0.1625 | NO |
| **Test (Impressions)** | 10 | 3 | **30.0%** | 25.0% | 8.9 | 0.2125 | Modest (+5.0pp, $p=0.47$) |
| **Forced Choice** | 10 | 0 | **0.0%** | 25.0% | 11.6 | 0.0625 | NO |

---

## 3. Analysis & Key Takeaways
1. **Free-form vs Direct Choice:** 
   In Phase 3 (free-form qualitative impressions), the model's descriptions improved over baseline (0% $\to$ 30% hit rate, average rank improved from 11.6 to 8.9), showing that Campbell's instruction encourages broader sensory vocabulary. However, 3/10 hits vs 2.5 expected is consistent with random chance ($p = 0.47$).
2. **Forced-Choice Attractor Trapping:**
   When forced to rank candidate IDs directly (Phase 4), the model scored 0/10 hits (avg rank 11.6), once again settling into rigid selection order rather than discriminating targets.
3. **Evidence Record:**
   Replicates the earlier Session 037 finding ($N=30$, NULL), confirming that prompting alone on a frozen quantized model does not produce anomalous target discrimination under double-blind conditions.
