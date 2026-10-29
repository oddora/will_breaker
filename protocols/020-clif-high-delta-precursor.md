# Protocol 020 — Clif High Delta-Precursor Instrument (Candidate I-E)

**Status:** ACTIVE / SEALED  
**Date:** 2026-10-29  
**Category:** Predictive Linguistics / Precursor Delta Detection  
**Subject:** `wb-agent` (Qwen3-8B LoRA on `:18284`, `--no-think`) + SearXNG Live Crawler (`:18080`) + Emotional Lexicon Anomaly Scorer  
**Traceability:** [Research 007](file:///home/comandante/will_breaker/research/007-clif-high-predictive-engine.md) (Clif High Web Bot / ALTA) $\to$ [Research 012 §5](file:///home/comandante/will_breaker/research/012-traceability-build-map.md#L200) (Candidate I-E).

---

## 1. Hypothesis Under Test

Precognition and future information retrieval do not operate as isolated minds guessing uniform random noise out of thin air. Instead, per Clif High's predictive linguistics framework, **collective human discourse leaks subtle emotional and linguistic anomalies into public communication *before* macro events manifest in physical reality (the "template layer")**.

**Operational test:**
Can an automated pipeline detecting statistical context anomalies (words appearing outside their baseline contextual distribution with high emotional intensity) generate structured event forecasts that achieve positive predictive skill under strict cryptographic pre-commitment?

---

## 2. Experimental Architecture

1. **Discourse Sampling (SearXNG `:18080`):**
   * Real-time multi-engine query across four archetypal macro domains:
     - `geopolitical`: Conflict, military mobilization, diplomatic escalation.
     - `financial`: Liquidity, banking stress, currency volatility, debt default.
     - `geophysical`: Seismic, volcanic, geomagnetic solar disturbances.
     - `scientific_anomaly`: Quantum anomalies, breakthrough observations, physics deviations.
2. **Context Baseline Model:**
   * 37-document baseline corpus (`will_breaker_delta/corpus/built/`, 13 MB) establishing word co-occurrence expectations.
3. **Delta Scoring Engine (`AnomalyScorer`):**
   * NRC Emotion Lexicon (8 dimensions: joy, trust, fear, surprise, sadness, disgust, anger, anticipation).
   * VADER Sentiment Lexicon (compound valence).
   * Anomaly formula: Total Variation Distance (TVD) between incoming context distribution and expected baseline context distribution, scaled by emotional intensity and rarity.
4. **Archetype Synthesis (`wb-agent` on `:18284`):**
   * Top anomalous outlier clusters fed to `wb-agent`.
   * Model projects the underlying archetype into a concrete, falsifiable event hypothesis with an objective resolution criterion and confidence probability.
5. **Cryptographic Seal & Resolution:**
   * Deterministic SHA-256 seal computed and committed to git **before** the 14-day forecast window opens.
   * Scored at resolution using Brier Score ($BS = (p - y)^2$) and binary accuracy.

---

## 3. Pre-registered Endpoints

* **Primary Endpoint:** Directional Brier Skill Score ($BSS > 0$ vs climatological base rate) on sealed hypotheses.
* **Secondary Endpoint:** Anomaly lead time (do detected deltas cluster $>3$ days prior to public event emergence?).
* **Epistemic Demarcation:** A successful forecast is evidence of collective linguistic precursor leakage, not isolated supernatural perception.
