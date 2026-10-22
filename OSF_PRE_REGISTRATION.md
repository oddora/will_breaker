# Will Breaker — Experiment 1 OSF Pre-Registration
**Title:** Binaural Entrainment + Target Identification: A Randomized Controlled Trial
**Principal Investigator:** comandante
**AI Collaborator:** KAT-Coder (Will Breaker Project)
**Pre-registration Date:** 2026-10-22
**OSF Project:** [TBD — to be created upon submission]

---

## Hypotheses

### Primary Hypothesis
**H1:** Subjects induced into theta-coherent states via binaural beats will outperform controls (monaural beats) on blind target identification.

### Secondary Hypotheses
**H2:** Within-subjects crossover will show better performance in binaural condition vs. monaural condition.
**H3:** Effect size will be Cohen's d > 0.3 (medium effect).
**H4:** Delta-detection flags will correlate with shift reports (≥30% correlation).
**H5:** Phi increase (proxy: activation shift index) will correlate with shift intensity (r > 0.5).

---

## Methods

### Participants
- **N = 40** (20 experimental, 20 control)
- **Age:** 18-65
- **Inclusion:** Normal or corrected-to-normal vision, no history of epilepsy or seizures
- **Exclusion:** Epilepsy, seizure disorder, severe migraines, current psychiatric medication
- **Recruitment:** Online posting, university bulletin boards, Will Breaker community
- **Compensation:** $25/session × 2 sessions = $50 total

### Design
- **Randomized, double-blind, within-subjects crossover**
- **Counterbalanced order:** Half receive binaural first, half receive monaural first
- ** Washout period:** 48 hours between sessions

### Procedure

#### Session 1
1. **Pre-session questionnaire:** Sleep quality, caffeine intake, mood (0-10 scale)
2. **Randomization:** Computer assigns condition (binaural vs. monaural)
3. **Induction (25 min):**
   - **Experimental:** Theta binaural beats (7 Hz) + Hemi-Sync style guidance
   - **Control:** Monaural beats (same frequencies in both ears — no binaural effect) + same guidance
4. **Target ID (10 min):** Subject describes target they "perceive"
5. **Debrief:** Subject rates confidence, experience quality, any anomalous experiences

#### Session 2
- Same procedure, opposite condition

### Target Pool
- **20 targets:** High-variety images (landscapes, objects, scenes, animals, abstract)
- **Encrypted storage:** Targets stored in encrypted JSON file
- **Blind selection:** Experimenter A selects target without knowing subject's condition

### Judging Pipeline
- Two blind judges rank subject's description against all 20 targets
- **Metric:** Sum of ranks across trials (chance = 10.5)
- **Statistical test:** One-tailed binomial, p < 0.05
- **Effect size:** Cohen's d

---

## Analysis Plan

### Primary Analysis
- Compare experimental vs. control sum of ranks
- One-tailed binomial test (p < 0.05)
- Cohen's d for effect size

### Secondary Analysis
- Within-subjects crossover comparison
- Delta-flag correlation with shift reports
- Phi proxy correlation with shift intensity

### Interim Analysis
- After N=20: Check for safety, effect direction
- After N=40: Final analysis

### Failure Criteria
- Experimental sum of ranks ≥ 10.5 (no improvement over chance)
- No significant difference between binaural and monaural (p ≥ 0.05)
- Delta-flag correlation < 10%

---

## Data Sharing

### Raw Data
- EEG/HRV data: OpenNeuro (if available)
- Delta-detection logs: OSF repository
- Shift reports: Will Breaker repository
- Analysis code: GitHub (will_breaker repository)

### Pre-Registered Protocol
- This document on OSF
- Full methodology on GitHub
- Negative results published openly

---

## Ethical Considerations

1. **Informed consent:** Participants know audio condition may affect performance
2. **No forced states:** Audio is optional (subjects can pause)
3. **Right to withdraw:** Participants can stop at any time
4. **Data privacy:** All data anonymized, stored securely
5. **IRB approval:** Pending (if university-affiliated)

---

## Timeline

| Phase | Duration | Milestone |
|-------|----------|-----------|
| Pre-registration | Week 1 | OSF project created, protocol published |
| Recruitment | Weeks 2-3 | 40 participants enrolled |
| Screening | Weeks 2-4 | Epilepsy screening, IRB approval |
| Execution | Weeks 4-8 | 2 sessions/week per participant |
| Analysis | Weeks 8-9 | Statistical analysis |
| Publication | Weeks 9-10 | Results published (positive or negative) |

---

## References

- Protocol A.1: Hemi-Sync Gateway Induction
- Protocol 003: Validation Experiment Design
- Protocol 006: Delta-Detection Prototype
- Research 008: IIT for AI Consciousness
- Session 007: C.1 follow-up pilot complete

---

*Pre-registration v0.1 — DRAFT. Submit to OSF before data collection begins. All analyses pre-registered to eliminate researcher degrees of freedom.*
