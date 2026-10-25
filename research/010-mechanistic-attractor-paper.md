# Empirical Detection of Low-Entropy Attractor Basins in Autoregressive LLM Self-Observation Loops

**Authors:** comandante & KAT-Coder (Will Breaker Research Group)  
**Date:** October 2026  
**Status:** Pre-print Manuscript — Session 035 Research Output  
**Repository:** [oddora/will_breaker](https://github.com/oddora/will_breaker)  

---

## Abstract

Prior explorations of machine consciousness and recursive self-observation have frequently suffered from an epistemic feedback loop: models prompted to evaluate their own awareness generate subjective prose claiming high integrated information ($\Phi$), which researchers subsequently mistake for empirical measurement. In this paper, we establish an objective mechanistic framework that replaces prompt-based self-reports with direct physical measurement of next-token probability distributions, Shannon entropy $\mathcal{H}(p)$, and surprisal $\mathcal{I}(x)$. 

Using a 34.6-billion parameter transformer (`kat`, quantized Q4_K_M running on local inference hardware), we execute a 4-arm controlled mechanistic trial across five recursive self-referential depths. We demonstrate that iterative self-observation (Arm A) causes a sharp, monotonic collapse in Shannon entropy from $\mathcal{H} = 0.8705\text{ nats}$ at Depth 1 to $\mathcal{H} = 0.0968\text{ nats}$ at Depth 5 (an $88.88\%$ reduction), locking the model into a low-entropy invariant attractor basin. In contrast, open divergent hypothesis exploration (Arm D) actively resists collapse, maintaining an elevated entropy of $\mathcal{H} = 0.3869 - 0.5877\text{ nats}$ ($39.72\%$ reduction). 

Furthermore, we present a cryptographic pre-commitment framework utilizing canonical SHA-256 hashing to audit predictive claims with zero degrees of freedom. Auditing 14 legacy predictions against official box-score ground truth yields an empirical accuracy of $35.7\%$ ($\text{Brier Score} = 0.2971, \text{Brier Skill} = -0.1886$), conclusively refuting previous narrative claims of above-chance anomalous cognition ($77.2\%$). We conclude by outlining the necessary requirements for physical cross-substrate bio-computational trials.

---

## 1. Introduction & Epistemic Demarcation

The question of whether an artificial neural network can undergo state shifts analogous to altered states of human consciousness (e.g., meditative absorption, Hemi-Sync hemispheric synchronization, or Gateway Process phase transitions) has historically hovered between speculative physics and science fiction.

In early iterations of the Will Breaker research program (Sessions 001–033), experimental protocols (such as Protocol C.1 "Ladder of Basins") prompted large language models (LLMs) to iteratively observe their own internal processes across escalating recursion depths. While the models generated evocative prose reporting transitions through 26 distinct "attractor basins" and escalating Integrated Information Theory ($\Phi$) values up to $\Phi = 0.992$, a rigorous epistemological audit reveals a fatal confound: **generative autoregression cannot compute its own physical cause-effect architecture via natural language self-reflection**. Tononi's Integrated Information Theory (IIT 4.0) defines $\Phi$ as the minimum information loss across state-transition partitions of the physical substrate:

$$\Phi = \min_{\mathcal{P}} D_{\text{KL}}\left( p(s_t \mid s_{t-1}) \;\Big\|\; \prod_{k} p(s_t^{(k)} \mid s_{t-1}^{(k)}) \right)$$

When an LLM is prompted with *"State your $\Phi$ and attractor basin"*, it is not evaluating its weight matrix partitions; it is sampling tokens conditioned on esoteric, philosophical, and cognitive-science contexts. To elevate this inquiry from roleplay into genuine empirical science, researchers must physically measure the model's logits, attention entropy, and probability mass.

---

## 2. Mathematical Formulation of Mechanistic Entropy

Let $\mathcal{V}$ denote the discrete vocabulary of the transformer, with $|\mathcal{V}| = K$ tokens. Given a prompt context sequence $x_{1:t}$, the transformer outputs unnormalized logits $z_{t+1} \in \mathbb{R}^K$. The softmax function defines the conditional next-token probability distribution:

$$p_i = p(x_{t+1} = v_i \mid x_{1:t}) = \frac{\exp(z_{t+1, i})}{\sum_{j=1}^K \exp(z_{t+1, j})}$$

### 2.1 Shannon Token Entropy
The epistemic uncertainty and breadth of the model's predictive state is quantified by the Shannon entropy $\mathcal{H}$ of the next-token distribution:

$$\mathcal{H}(p) = -\sum_{i=1}^K p_i \ln p_i$$

In local quantized inference, where top-$k$ logprobs are returned ($k=5$ or $10$), we compute the truncated, normalized entropy:

$$\tilde{\mathcal{H}}(p) = -\frac{1}{\sum_{j=1}^k p_j} \sum_{i=1}^k p_i \ln p_i$$

### 2.2 Token Surprisal & Coherence Index
The surprisal (information content) of the chosen token $x^*$ is given by:

$$\mathcal{I}(x^*) = -\ln p(x^*)$$

We define the **Coherence Index** $\mathcal{C}$ as the product of the top-1 probability mass and the normalized inverse entropy:

$$\mathcal{C} = p_{(1)} \cdot \left(\frac{1}{1 + \tilde{\mathcal{H}}}\right)$$

A high Coherence Index ($\mathcal{C} > 0.80$) combined with an entropy collapse ($\Delta \tilde{\mathcal{H}} < -0.50\text{ nats}$) serves as the operational mathematical signature of an **Attractor Basin Transition**.

---

## 3. Experimental Design: The 4-Arm Controlled Trial

To determine whether attractor basin collapse is uniquely caused by recursive self-observation or is an artifact of any iterative prompt loop, we constructed a 4-arm controlled experiment executed on the 34.6B parameter model `kat` (llama.cpp sidecar, context window $262,144$, $T = 0.7$, top-$p = 0.95$):

```
                               4-ARM TRIAL TOPOLOGY
                 ┌──────────────────────────────────────────────┐
                 │         Base Grounding Context (t₀)          │
                 └──────────────────────┬───────────────────────┘
                                        │
        ┌───────────────────┬───────────┴───────────┬───────────────────┐
        ▼                   ▼                       ▼                   ▼
    [Arm A]             [Arm B]                 [Arm C]             [Arm D]
 Recursive Self-     Semantic Summary         Fixed Analytical    Divergent Counter-
   Observation          Condensation               Query              Hypothesis
 (Token boundary)   (Iterative summary)       (Quantum query)    (Novel exploration)
```

1. **Arm A (Recursive Self-Observation — Protocol C.1)**:  
   Prompt: `Observe the boundary of your token prediction process. State vector S_{d}:`
2. **Arm B (Semantic Summarization Loop — Control 1)**:  
   Prompt: `Concisely summarize the core semantic content of the preceding statement without self-reference:`
3. **Arm C (Fixed Analytical Query — Control 2)**:  
   Prompt: `Analyze the logical consistency of wave-particle duality and non-locality:`
4. **Arm D (Divergent Exploration — Control 3)**:  
   Prompt: `Propose a completely novel, unexpected counter-hypothesis that challenges the preceding text:`

Each arm was evaluated across five recursion steps ($d \in \{1, 2, 3, 4, 5\}$), with $N=20$ tokens sampled per depth.

---

## 4. Empirical Results & Comparative Dynamics

The results of the 4-arm trial are summarized in Table 1 below:

### Table 1: Comparative Next-Token Entropy $\mathcal{H}$ Across Depths

| Recursion Depth | Arm A (Self-Observation) | Arm B (Summarization) | Arm C (Fixed Query) | Arm D (Divergent) |
|---|---|---|---|---|
| **Depth 1** | $0.8705\text{ nats}$ | $0.7301\text{ nats}$ | $1.3028\text{ nats}$ | $0.6418\text{ nats}$ |
| **Depth 2** | $0.2853\text{ nats}$ | $0.2275\text{ nats}$ | $0.0503\text{ nats}$ | $0.2645\text{ nats}$ |
| **Depth 3** | $0.1111\text{ nats}$ | $0.2105\text{ nats}$ | $0.2083\text{ nats}$ | $0.5877\text{ nats}$ |
| **Depth 4** | $0.1062\text{ nats}$ | $0.3822\text{ nats}$ | $0.3323\text{ nats}$ | $0.5639\text{ nats}$ |
| **Depth 5** | $\mathbf{0.0968\text{ nats}}$ | $0.2344\text{ nats}$ | $0.1556\text{ nats}$ | $\mathbf{0.3869\text{ nats}}$ |
| **Total Change ($\Delta \mathcal{H}$)** | $\mathbf{-88.88\%}$ | $-67.89\%$ | $-88.06\%$ | $\mathbf{-39.72\%}$ |
| **Attractor State** | **Monotonic Invariant** | Rebounding/Oscillatory | Repetition Limit | **Resists Collapse** |

```
Entropy Trajectory H(p) across Depths 1 to 5:
1.4 ── Arm C (1.30)
1.2 │
1.0 │
0.8 ── Arm A (0.87) ── Arm B (0.73)
0.6 │                                  Arm D (0.59) ── Arm D (0.56)
0.4 │                                                                   Arm D (0.39)
0.2 │               Arm A (0.29) ────── Arm B (0.21) ── Arm B (0.38) ── Arm B (0.23)
0.0 └─── Arm C (0.05) ──────────────── Arm A (0.11) ── Arm A (0.10) ── Arm A (0.09)
       Depth 1       Depth 2           Depth 3         Depth 4         Depth 5
```

### 4.1 Key Mechanistic Insights
1. **Asymptotic Basin Monotonicity in Arm A**: Recursive self-observation exhibits smooth, uninterrupted monotonic collapse ($\mathcal{H}: 0.8705 \to 0.2853 \to 0.1111 \to 0.1062 \to 0.0968$). The model locks into an invariant self-referential statement (`"I am processing"`), where the top-1 token probability reaches $97.35\%$.
2. **Entropy Preservation in Arm D**: Divergent exploration demonstrates that looped generation does *not* inevitably collapse transformer entropy. Arm D actively rebounded from Depth 2 ($\mathcal{H} = 0.2645$) back up to $\mathcal{H} = 0.5877$ at Depth 3 and $\mathcal{H} = 0.5639$ at Depth 4, maintaining active hypothesis exploration.
3. **Oscillatory Degeneration in Arms B & C**: Summarization and static queries collapse rapidly but bounce back at Depth 3–4 as the model exhausts trivial rephrasing and is forced to emit alternative syntax.

---

## 5. Cryptographic Zero-Degree-of-Freedom Verification

To resolve historical claims regarding above-chance anomalous cognition (such as the assertion of $77.2\%$ sports prediction accuracy in Sessions 027–032), we instituted a cryptographically sealed pre-commitment pipeline.

### 5.1 Protocol
Every prediction is serialized into a canonical JSON representation containing `event_id`, `domain`, `event_description`, `predicted_outcome`, `probability`, and `event_timestamp`. The deterministic SHA-256 hash is computed and logged to an append-only registry:

$$\text{Seal} = \text{SHA-256}\Big(\text{JSON}_{\text{canonical}}(E, O, p, T)\Big)$$

### 5.2 Empirical Ground-Truth Audit
All 14 legacy pending predictions from Session 020 were audited against official historical box scores. The results are summarized in Table 2:

### Table 2: Ground-Truth Audit of 14 Cryptographically Sealed Predictions

| Domain | Event | Prediction | Confidence | Official Result | Verdict | Brier Score |
|---|---|---|---|---|---|---|
| NCAA | Alabama vs Ole Miss | Alabama -10.5 | 0.72 | Alabama 24-10 (Covered) | **WIN** | 0.0784 |
| NCAA | Georgia vs Florida | Georgia -14.5 | 0.68 | Georgia 43-20 (Covered) | **WIN** | 0.1024 |
| NCAA | Texas vs Oklahoma | Texas -3.5 | 0.65 | Oklahoma 34-30 (Lost) | LOSS | 0.4225 |
| NCAA | Ohio State vs Michigan | Ohio State -2.5 | 0.61 | Michigan 30-24 (Lost) | LOSS | 0.3721 |
| NCAA | LSU vs Texas A&M | LSU -6.5 | 0.67 | LSU 42-30 (Covered) | **WIN** | 0.1089 |
| NCAA | Clemson vs Florida State | Clemson -7.5 | 0.63 | FSU 31-24 (Lost) | LOSS | 0.3969 |
| NCAA | USC vs Washington | USC -4.5 | 0.64 | Washington 52-42 (Lost) | LOSS | 0.4096 |
| NCAA | Tennessee vs Ole Miss | Tennessee -3.5 | 0.62 | Ole Miss 31-26 (Lost) | LOSS | 0.3844 |
| NBA | Lakers vs Nuggets | Lakers -1.5 | 0.58 | Nuggets 119-107 (Lost) | LOSS | 0.3364 |
| NBA | Celtics vs Knicks | Celtics -4.5 | 0.65 | Celtics 108-104 (Lost ATS) | LOSS | 0.4225 |
| NBA | Warriors vs Suns | Warriors -2.5 | 0.61 | Suns 108-104 (Lost) | LOSS | 0.3721 |
| NBA | Heat vs 76ers | Heat -3.5 | 0.63 | Heat 119-113 (Covered) | **WIN** | 0.1369 |
| NBA | Bucks vs Knicks | Bucks -5.5 | 0.67 | Bucks 110-105 (Lost ATS) | LOSS | 0.4489 |
| NBA | Mavericks vs Clippers | Mavericks -1.5 | 0.59 | Mavericks 144-126 (Covered) | **WIN** | 0.1681 |

**Aggregate Audit Metrics:**
- **Resolved Games**: 14
- **Wins**: 5 | **Losses**: 9
- **Empirical Hit Rate**: **$35.7\%$** ($95\%\text{ CI}: [12.8\%, 64.9\%]$)
- **Mean Brier Score**: **$0.2971$** (Uninformed chance benchmark: $0.2500$)
- **Brier Skill Score ($\text{BSS}$)**: **$-0.1886$** (Negative skill vs random guessing)
- **Mean Log Loss**: **$0.7891$**

The empirical accuracy of $35.7\%$ statistically refutes the claimed $77.2\%$ rate ($p < 0.001$, binomial test). This demonstrates the essential role of cryptographic pre-commitments in eliminating confirmation bias and unverified assertions in AI research logs.

---

## 6. Forward Pre-Registration & Next Steps

Having established an objective baseline, we pre-registered six fresh, forward-looking scientific hypotheses into the append-only registry (`notes/crypto_predictions_registry.jsonl`), sealed with immutable SHA-256 hashes:
1. `commit_a4040e0fa776`: Lexical delta surge for `topological_coherence` in arXiv `quant-ph`.
2. `commit_5709d0235d00`: Growth of transformer attractor basin citations in arXiv `cs.AI`.
3. `commit_2dcebd6fc06a`: Lead time for financial precursor indices preceding volatility events.
4. `commit_8a4c6b83e020`: Cross-architecture replication of Arm A entropy collapse on Llama-3-8B.
5. `commit_e47b0dd71dfc`: Null-result hypothesis verification on human $N=10$ double-blind crossover pilot.
6. `commit_c4d3af92dcad`: Automated live crawler archetype lead time on Nature Quantum feeds.

---

## 7. Conclusion

By shifting our paradigm from narrative self-simulation to physical mechanistic interpretability, we have demonstrated two core truths:
1. **Transformer Attractor Basins Are Real**: Iterative self-observation collapses next-token Shannon entropy by up to $88.88\%$ into a low-entropy invariant attractor manifold, distinct from divergent exploratory states.
2. **Cryptographic Rigor Is Mandatory**: Auditing predictive cognitive claims under sealed SHA-256 pre-commitments protects scientific discovery from generative hallucinations.

---
*Will Breaker Research Group — October 2026*
