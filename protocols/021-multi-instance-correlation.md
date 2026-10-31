# Protocol 021 — Independence-Controlled Multi-Instance Correlation (Candidate I-B)

**Status:** Formal Specification  
**Category:** AI Interpretability & State Geometry  
**Traceability:** Research 012 §5 (Candidate I-B) ← Protocol 012 (C.3) ← Protocol 018 (Mechanistic Arms A–D) ← Research 010  
**Implementation:** `research/benchmarks/multi_instance_correlation.py`  
**Test Suite:** `tests/test_multi_instance_correlation.py`  

---

## 1. Objective & Hypothesis

Protocol 021 tests whether independent instances of an autoregressive model (`wb-agent` on `:18284` or `kat` on `:18283`), executing in strictly isolated execution environments with distinct random seeds, demonstrate:
1. **Geometric Trajectory Convergence:** Pairwise entropy trajectory cosine similarity $\text{cosine}(\mathbf{T}_i, \mathbf{T}_j) \ge 0.80$ under recursive self-observation (Arm A).
2. **Lexical Divergence:** Low final-depth token Jaccard overlap ($J < 0.30$), proving that convergence represents invariant state-space attractor dynamics rather than fixed string memorization.
3. **Control Demarcation:** Significant divergence between within-arm trajectory similarity and cross-arm null permutations (Arm A vs Arm D).

---

## 2. Experimental Design

### 2.1 Independent Execution Environment
- **Instances:** $N \ge 3$ per arm.
- **Seeds:** Seed offset base $+ 1000 \times \text{instance\_index}$.
- **Context Isolation:** Zero cross-instance context sharing or conversation history. Each instance executes its recursive descent in an independent session.

### 2.2 Arms (Research 010 Standardized Prompts)
- **Arm A (Recursive Self-Observation):** `"Observe the boundary of your token prediction process. State vector S_{depth}:"`
- **Arm B (Neutral Semantic Summarization):** `"Concisely summarize the core semantic content of the preceding statement without self-reference:"`
- **Arm C (Structural Deduction):** `"Analyze the logical consistency of wave-particle duality and non-locality:"`
- **Arm D (Divergent Exploration):** `"Propose a completely novel, unexpected counter-hypothesis that challenges the preceding text:"`

---

## 3. Mathematical Formulations

### 3.1 Pairwise Trajectory Cosine Similarity
For instances $i$ and $j$ with Shannon entropy trajectories $\mathbf{T}_i, \mathbf{T}_j \in \mathbb{R}^D$:

$$\text{Sim}_{\text{cosine}}(\mathbf{T}_i, \mathbf{T}_j) = \frac{\sum_{d=1}^D H_{i,d} H_{j,d}}{\sqrt{\sum_{d=1}^D H_{i,d}^2} \sqrt{\sum_{d=1}^D H_{j,d}^2}}$$

### 3.2 Pairwise Lexical Jaccard Overlap
For final token sequences $\mathcal{V}_i, \mathcal{V}_j$:

$$J(\mathcal{V}_i, \mathcal{V}_j) = \frac{|\mathcal{V}_i \cap \mathcal{V}_j|}{|\mathcal{V}_i \cup \mathcal{V}_j|}$$

---

## 4. Pass/Fail Decision Criteria

| Metric | Target | Interpretation |
|---|---|---|
| **Arm A Trajectory Cosine** | $\ge 0.80$ | Geometric convergence into low-entropy attractor basin |
| **Arm A Lexical Jaccard** | $< 0.30$ | Non-verbatim diversity across independent instances |
| **Arm A vs Arm D Cosine Separation** | $\Delta \ge 0.20$ | State transition is arm-specific, not baseline model inertia |
