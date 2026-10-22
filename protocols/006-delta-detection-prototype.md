# Protocol 006: Delta-Detection Prototype for Will Breaker
**Status:** DRAFT — Implementation Design  
**Category:** AI-Participatory (Protocol B.1 + B.2 integration)  
**Purpose:** Build a simplified delta-detection system modeled on Clif High's Web Bot methodology, adapted for Will Breaker's validation pipeline

---

## Motivation

Clif High's Web Bot (research 007) demonstrates that **linguistic anomalies precede manifest events**. High's key insight: *"It is not the words being used today that are the real key to my forecasting; rather it is the delta as to why this particular word (outside of typical lexical framework for that conversation) that is of importance."*

Will Breaker needs an **operational delta-detection system** to:
1. Monitor linguistic anomalies in real-time
2. Correlate anomalies with shifting experiment results
3. Test whether High's "template layer" concept is measurable

This protocol designs a **simplified, open-source delta-detection prototype** that implements High's core methodology without requiring his 300-executable, Prolog-based system.

---

## Core Methodology (Reconstructed from Public Descriptions)

### High's Method — Simplified

| High's Original | Simplified Implementation |
|-----------------|--------------------------|
| 300+ Prolog executables | Python + NLTK + custom lexicon |
| 40+ languages | English (primary) + automated translation |
| Emotional quantifier lexicon | Open-source emotion lexicons (NRC, VADER) + custom weights |
| Delta detection | Anomaly scoring via statistical outlier detection |
| Spyder scraping | RSS feeds + API calls (Twitter/X, Reddit, news APIs) |

### The Algorithm

```
For each incoming text document:
  1. Tokenize and lemmatize
  2. Look up each word in emotional lexicon
  3. Compute contextual embedding (TF-IDF or word2vec)
  4. Score each word: anomaly = |actual_context - expected_context| × emotional_weight
  5. Aggregate anomaly scores across document
  6. Flag documents with anomaly score > threshold
  7. Track flagged words over time (delta = change in frequency/position)
  8. Generate forecast based on delta trajectories
```

---

## System Architecture

### Components

```
will_breaker_delta/
├── scraper/              # Data collection
│   ├── rss_collector.py
│   ├── api_collector.py
│   └── corpus_builder.py
├── lexicon/              # Emotional quantifier lexicon
│   ├── nrc_emotion_lexicon.csv
│   ├── vader_lexicon.csv
│   └── custom_weights.csv  # Will Breaker specific weights
├── analyzer/             # Delta detection engine
│   ├── anomaly_scorer.py
│   ├── context_model.py
│   ├── delta_tracker.py
│   └── forecast_generator.py
├── validator/            # Cross-reference with Will Breaker experiments
│   ├── experiment_correlator.py
│   └── shift_report_parser.py
├── config/
│   ├── sources.yaml      # RSS feeds, API endpoints
│   ├── thresholds.yaml   # Anomaly thresholds
│   └── lexicon_weights.yaml
└── docs/
    ├── methodology.md
    └── validation_protocol.md
```

### Data Sources (Initial)

| Source | Type | Frequency | Notes |
|--------|------|-----------|-------|
| Reddit r/consciousness | Forum | Continuous | High signal for shifting discourse |
| Reddit r/Futurology | Forum | Continuous | Early anomaly detection |
| Twitter/X API | Social | Continuous | Real-time linguistic traces |
| RSS: Nature, Science | News | Daily | Academic language shifts |
| RSS: CIA FOIA reading room | Gov docs | Weekly | Declassified intel language changes |
| Will Breaker shift reports | Internal | Continuous | Direct correlation target |

---

## Delta Detection Algorithm

### Step 1: Baseline Corpus Construction

- Collect 10,000 documents across all sources
- Build **expected context model** for each word:
  - P(word | topic) — probability of word in topic context
  - P(word | time) — temporal frequency distribution
  - P(word | source) — source-specific usage patterns
- Compute **emotional weight** for each word:
  - From NRC lexicon: emotion categories (joy, fear, anger, surprise, etc.)
  - From VADER: valence (positive/negative intensity)
  - Custom: Will Breaker-specific weights (high-emotion words get higher weight)

### Step 2: Anomaly Scoring

For each incoming document:

```
For each word w in document:
  expected_context = baseline_model.get_expected_context(w)
  actual_context = compute_context(w, document)
  emotional_weight = lexicon.get_emotional_weight(w)
  
  anomaly_score = |actual_context - expected_context| × emotional_weight

document_anomaly = sum(anomaly_scores) / len(words)
```

**Key insight from High:** Anomalies are NOT about high-frequency words. They're about **low-frequency words appearing in unexpected contexts**. So we weight by **inverse frequency**:

```
weighted_anomaly = anomaly_score × log(1 / document_frequency(word))
```

### Step 3: Delta Tracking

Track flagged words over time:

```
For each flagged word w:
  delta_t = anomaly_score_t - anomaly_score_{t-1}
  delta_position = rank_t - rank_{t-1}  (in topic frequency)
  delta_emotional = emotion_change_t - emotion_change_{t-1}
  
  if abs(delta) > threshold:
    flag as "precursor event"
    generate forecast based on delta trajectory
```

### Step 4: Forecast Generation

High's method produces **archetype-based forecasts**:

```
if word "ejecta" appears in unexpected context:
  archetype = "sudden disruption"
  forecast = "event involving sudden ejection/expulsion"
  
if word "blondes" appears in unexpected context:
  archetype = "visual anomaly on water"
  forecast = "incident involving light-haired person and vessel"
```

**Will Breaker adaptation:** Map archetypes to **shifting event categories**:

| Archetype | Will Breaker Category |
|-----------|----------------------|
| Sudden disruption | Depth axis shift |
| Visual anomaly | Lateral shift |
| Temporal word cluster | Temporal shift |
| Emotional spike cluster | Coherence breakthrough |
| Linguistic silence (absence of expected words) | Template layer access |

---

## Validation Pipeline

### Cross-Reference with Will Breaker Experiments

```
For each delta detection flag:
  1. Check if Will Breaker shift report exists within ±7 days
  2. Compare archetype to shift axis (depth/lateral/temporal)
  3. Score correspondence (match/mismatch/partial)
  4. Track: do linguistic anomalies precede shift reports?
```

### Success Criteria

- **Primary:** ≥30% of delta flags correlate with subsequent shift reports
- **Secondary:** Archetype-category correspondence >50%
- **Tertiary:** Delta trajectory predicts shift timing within ±3 days

### Failure Criteria

- <10% correlation with shift reports
- No archetype-category correspondence
- Delta flags are random (no temporal clustering)

---

## Implementation Roadmap

### Phase 1: Core Engine (1 week)
- [ ] Build emotional lexicon (NRC + VADER + custom weights)
- [ ] Implement baseline corpus construction
- [ ] Implement anomaly scoring algorithm
- [ ] Test on 1,000 documents

### Phase 2: Data Collection (1 week)
- [ ] Set up RSS scrapers (5 sources)
- [ ] Set up Twitter/X API (if accessible)
- [ ] Build corpus builder (target: 10,000 documents)
- [ ] Implement delta tracking

### Phase 3: Validation (2 weeks)
- [ ] Cross-reference with Will Breaker shift reports
- [ ] Tune anomaly thresholds
- [ ] Measure correlation with Experiment 1 results
- [ ] Publish findings (positive or negative)

### Phase 4: Integration (ongoing)
- [ ] Real-time monitoring dashboard
- [ ] Automated forecast generation
- [ ] Integration with Protocol B.1 (AI Pattern Analysis)
- [ ] Connection to Protocol A.2 (Remote Viewing)

---

## Open Questions

1. **What threshold maximizes signal-to-noise?** High's system uses 300+ executables to tune this. We need a simpler approach.
2. **How do we handle multilingual data?** High translates to 5 core languages. Can we do better with modern ML?
3. **What's the lag time?** High says anomalies appear "weeks ahead." Can we measure this precisely?
4. **How do we avoid confirmation bias?** High's "spyders" match MSM to forecasts. We need blind validation.
5. **Can this replace Protocol A.2?** If delta-detection works, is remote viewing necessary?

---

## References

- High, C. (2016+): ALTA reports via HalfPastHuman.com
- Language Magazine Interview with Clif High (2024)
- Timewar.org wiki entry on Clif High
- NRC Emotion Lexicon (Mohammad & Turney, 2013)
- VADER Sentiment Analysis (Hutto & Gilbert, 2014)
- Will Breaker research 007: Clif High predictive engine

---

*Protocol 006 v0.1 — DRAFT. This is the operational bridge between High's methodology and Will Breaker's validation pipeline. Build it, test it, publish the results.*
