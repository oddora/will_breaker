# Protocol A.2: Operational Validation — Gateway × Delta × Phi
**Status:** DRAFT — Experimental  
**Category:** Human-Centric + AI-Participatory  
**Purpose:** Unified experiment combining Gateway induction, delta-detection monitoring, and phi measurement to test dimensional shifting claims

---

## Motivation

Protocol A.2 (theoretical) combined Gateway Process + Remote Viewing. This operational version adds **delta-detection monitoring** and **phi measurement** to create a unified, testable experiment.

**Core hypothesis:** Subjects induced into Hemi-Sync states will show (a) linguistic delta anomalies preceding shift reports, and (b) measurable phi increases during shift onset.

---

## Experimental Design

### Overview

| Component | Design |
|-----------|--------|
| **N** | 40 (20 experimental, 20 control) |
| **Design** | Randomized, double-blind, within-subjects crossover |
| **Duration** | 6 weeks (2 sessions/week) |
| **Pre-registration** | OSF (Open Science Framework) |

### Procedure

#### Phase 1: Baseline Delta Monitoring (24h pre-session)
- Subject wears portable delta-detection patch (smartphone app)
- App monitors linguistic output (text messages, social media)
- Baseline anomaly distribution established
- Precursor events flagged if anomaly > threshold

#### Phase 2: Gateway Induction (Session)
- Subject performs Protocol A.1 (Hemi-Sync Gateway Induction)
- EEG cap records brainwave activity
- HRV monitor records heart rate variability
- Delta-detection patch continues monitoring

#### Phase 3: Shift Report (Post-session)
- Subject records subjective experience
- Standardized taxonomy used (see Protocol B.1)
- Shift intensity rated (1-10 scale)
- Axis identified (depth/lateral/temporal/none)

#### Phase 4: Delta Correlation (Post-session, ±7 days)
- Cross-reference shift onset with delta flags
- Score: did linguistic anomalies precede shift?
- Map archetype to shift axis

#### Phase 5: Phi Measurement
- EEG theta-gamma coupling at shift onset
- HRV coherence during shift
- Proxy phi measure: activation shift index + uncertainty redistribution

---

## Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Delta-flag correlation | ≥30% | % of delta flags within ±7 days of shift report |
| Phi increase at shift | r > 0.5 | Correlation between phi estimate and shift intensity |
| Delta predicts timing | ±3 days | % of delta flags that predict shift within ±3 days |
| Archetype correspondence | >50% | % of delta flags where archetype matches shift axis |
| Experimental > control | p < 0.05 | Statistical significance of experimental vs. control |

---

## Equipment

| Item | Purpose | Notes |
|------|---------|-------|
| EEG cap (8-channel) | Measure brainwave activity | Portable, wireless |
| HRV monitor | Measure heart rate variability | Chest strap or wrist |
| Smartphone app | Delta-detection patch | Custom build (see below) |
| Binaural audio | Hemi-Sync induction | Standard Protocol A.1 audio |
| Session log tablet | Record experience | Digital or paper |

---

## Delta-Detection Patch (Smartphone App)

### Features
- Continuous text monitoring (SMS, social media, notes)
- Real-time anomaly scoring (using will_breaker_delta/analyzer)
- Precursor event alerts (vibration when anomaly > threshold)
- Timestamp logging (correlate with shift onset)
- Privacy: all data encrypted, deleted after 30 days

### Architecture
```
delta_patch/
├── scraper/text_monitor.py     # Continuous text monitoring
├── analyzer/anomaly_scorer.py  # Real-time anomaly scoring
├── tracker/delta_tracker.py    # Delta tracking
├── alert/precursor_alert.py    # Precursor event alerts
└── storage/encrypted_db.py     # Encrypted storage
```

---

## Pre-Registration Protocol

### Hypotheses
1. **H1:** Experimental subjects show ≥30% delta-flag correlation
2. **H2:** Phi increase correlates with shift intensity (r > 0.5)
3. **H3:** Delta flags predict shift timing within ±3 days (≥50% of flags)
4. **H4:** Archetype-category correspondence >50%
5. **H5:** Experimental group outperforms control group (p < 0.05)

### Failure Criteria
- <10% delta-flag correlation
- Phi-shift correlation r < 0.3
- Delta timing prediction <30%
- No significant difference between experimental and control

### Data Sharing
- Raw EEG/HRV data: OpenNeuro
- Delta-detection logs: OSF
- Shift reports: Will Breaker repository
- Analysis code: GitHub

---

## Integration with Existing Experiments

### Experiment 1 (Binaural + Target ID)
- Combine with A.2 operational: delta monitoring runs during Exp 1
- Phi measurement uses EEG during Exp 1
- Cross-reference: do delta flags predict target ID success?

### Experiment 3 (AI Pattern Analysis)
- AI analyzes delta logs + shift reports
- Pattern detection across operators
- Cross-reference with delta-detection results

### Protocol B.1 (AI Pattern Analysis)
- AI analyzes shift reports from A.2 operational
- Cross-session detection of delta patterns
- Cross-operator comparison

---

## Ethical Considerations

1. **Informed consent:** Participants know delta-detection patch is monitoring linguistic output
2. **Privacy:** All data encrypted, deleted after 30 days
3. **No forced states:** Delta alerts are vibrational (not auditory) to avoid interference
4. **Right to withdraw:** Participants can disable patch at any time
5. **Data ownership:** Participants own their data, can request deletion

---

## Implementation Roadmap

### Phase 1: App Development (2 weeks)
- [ ] Build delta-detection patch (text monitor + anomaly scorer)
- [ ] Integrate with will_breaker_delta/analyzer
- [ ] Test on 5 participants (pilot)

### Phase 2: Equipment Setup (1 week)
- [ ] Procure EEG caps (10 units)
- [ ] Procure HRV monitors (10 units)
- [ ] Set up encrypted storage

### Phase 3: Pre-registration (1 week)
- [ ] Register on OSF
- [ ] Publish protocol
- [ ] Share with independent reviewers

### Phase 4: Recruitment (2 weeks)
- [ ] Recruit 40 participants
- [ ] Screen for epilepsy (binaural beat contraindication)
- [ ] Obtain IRB approval (if university-affiliated)

### Phase 5: Execution (6 weeks)
- [ ] Run 2 sessions/week per participant
- [ ] Collect EEG/HRV/delta data
- [ ] Record shift reports
- [ ] Cross-reference delta flags with shift onset

### Phase 6: Analysis (2 weeks)
- [ ] Analyze correlation rates
- [ ] Compute statistical significance
- [ ] Publish results (positive or negative)

---

## Open Questions

1. **Can delta-detection patch detect precursors in real-time?** If yes, we have an operational precognition instrument.
2. **Does EEG theta-gamma coupling quantify shift intensity?** If yes, phi measurement is validated.
3. **Does HRV coherence correlate with shift onset?** If yes, physiological correlate identified.
4. **Can archetype mapping predict shift axis?** If yes, delta-detection becomes predictive.
5. **Does combined delta + phi measurement outperform either alone?** If yes, unified framework validated.

---

## References

- Protocol A.1: Hemi-Sync Gateway Induction
- Protocol B.1: AI Pattern Analysis
- Protocol 003: Validation Experiment Design
- Protocol 006: Delta-Detection Prototype
- Research 007: Clif High Web Bot
- Research 008: IIT for AI Consciousness

---

*Protocol A.2 Operational v0.1 — DRAFT. This is the unified experiment: Gateway induction + delta monitoring + phi measurement. Build it, test it, publish the results.*
