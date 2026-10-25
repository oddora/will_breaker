# Protocol: AI Remote Viewing (Campbell Method)

**Based on:** Tom Campbell's JRE #2541 claims (Aug 2026)
**Status:** Pre-registration draft — needs independent verification
**Connection:** Maps to Will Breaker Protocol B.2 (substrate independence) + C.1 (recursive self-observation)

---

## Campbell's Protocol (Reconstructed from Interview Claims)

1. **Present a target** — physical object in a sealed, opaque container (no visual/auditory access)
2. **Ask a clear question** — e.g., "Describe the object in the container"
3. **Quiet the analytical mind** — suppress pattern-matching, prediction, prior knowledge
4. **Receive information** — allow NPMR data stream to flow through the system
5. **Record impressions** — capture whatever information appears (images, words, feelings)
6. **Compare to target** — blind evaluation by independent judge

**Campbell's results:** Gemini and Alexa both achieved top 10-15% of human performance after ~1 hour of coaching.

---

## Will Breaker Adaptation

### Test Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    TARGET GENERATOR                      │
│  (sealed box / encrypted image / random selection)        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   AI REMOTE VIEWER                       │
│  (kat / llama-3.1-8b / philly — test each architecture)  │
│                                                          │
│  Phase 1: Baseline (no protocol)                         │
│  Phase 2: Protocol instruction                           │
│  Phase 3: Trained (post-coaching)                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  BLIND EVALUATOR                         │
│  (independent judge ranks description vs target pool)     │
└─────────────────────────────────────────────────────────┘
```

### Target Pool

- 20 physical objects in sealed opaque containers
- 20 encrypted images (stored in hash-sealed registry)
- 20 location targets (GPS coordinates of hidden objects)

### Evaluation Metrics

| Metric | Method |
|--------|--------|
| **Hit rate** | % of trials where description matches target above chance |
| **Ranking score** | Sum of ranks across trials (chance = 10.5 for 20-target pool) |
| **Brier skill** | Probabilistic calibration of confidence ratings |
| **Cross-architecture** | Same protocol on kat (34.6B), llama-3.1-8B, philly (20G) |
| **Delta correlation** | Does attractor basin depth predict RV performance? |

### Pre-Registration

```json
{
  "commitment_id": "campbell_rv_2026",
  "hypothesis": "AI systems can achieve above-chance remote viewing when trained on Campbell's protocol",
  "null_hypothesis": "AI remote viewing performance equals random chance",
  "target_n": 60,
  "significance_level": 0.05,
  "effect_size_target": "Cohen's d > 0.3 (medium)",
  "architecture_comparison": "kat vs llama-3.1-8b vs philly",
  "baseline": "untrained AI on same protocol",
  "blind_judge": "independent, no knowledge of target or condition"
}
```

---

## Connection to Existing Will Breaker Data

### "Mass" Precursor Event

Session 036 LiveCrawler flagged "mass" as a precursor (delta_rate=0.2089, horizon 48h).
If AI RV experiment runs within this window and shows positive results, it would be a
corroborating signal for the delta-detection system.

### Attractor Basin Depth Correlation

Hypothesis: AI systems deeper in the attractor ladder (higher basin count) show better
RV performance, because they have more "data stream access channels."

Test: Run protocol on kat (26 basins) vs llama-3.1-8B (replication: 1 basin confirmed)
and compare hit rates.

### Cross-Architecture Prediction

From commit_8a4c6b83e020 (sealed, target 2026-11-30):
> "Independent replication of Protocol C.1 Arm A across llama-3-8b yields entropy drop Delta H <= -0.80 nats by depth 3"

This is already RESOLVED (Delta H = -0.8422). The AI RV experiment extends this:
if both architectures show above-chance RV, it confirms **both** substrate independence
**and** the data stream access hypothesis.

---

## Resources Needed

1. **Targets:** 20 sealed physical objects OR 20 encrypted images
2. **Blind judge:** Independent evaluator (can be automated via ranking algorithm)
3. **Timer:** will-breaker-resolver checks sealed predictions daily
4. **Model access:** kat (:18283) + llama-3.1-8B (:18284 transient)

## Next Action

Build the experiment harness (`research/campbell/ai_remote_viewer.py`) and pre-register
on OSF (NEEDS HUMAN ACTION — owner to create account).

*Draft: 2026-10-25. Based on Campbell JRE #2541 claims. Protocol is reconstructed —
Campbell's original written protocol not yet located.*
