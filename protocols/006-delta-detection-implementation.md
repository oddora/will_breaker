# Protocol 006: Delta-Detection Prototype — Implementation

**Status:** IN PROGRESS
**Category:** AI-Participatory (Protocol B.1 + B.2)
**Purpose:** Operational delta-detection system modeled on Clif High's Web Bot methodology

---

## Implementation Plan

### Phase 1: Pipeline Integration (Current)
- [x] Review existing analyzer components
- [ ] Wire `anomaly_scorer` → `delta_tracker` → `forecast_generator`
- [ ] Add threshold crossing detection
- [ ] Unit tests for integrated pipeline

### Phase 2: LiveCrawler Enhancement
- [ ] Connect to existing corpus (48,442 lines, 72.8% correlation)
- [ ] Add real-time document scoring on ingest
- [ ] Precursor event flagging with archetype mapping

### Phase 3: Validation
- [ ] Cross-reference with Will Breaker shift reports
- [ ] Measure lead time between delta flags and shifting events
- [ ] Archive results to `results/delta_detection/`

---

## Component Map

```
will_breaker_delta/
├── analyzer/
│   ├── anomaly_scorer.py      ← Core TVD anomaly scoring (bounded 0.0-1.0)
│   ├── context_model.py       ← Baseline across 37 corpus files
│   ├── delta_tracker.py       ← Window filtering + sub-hour rate calc
│   └── forecast_generator.py  ← Archetype mapping from YAML
├── scraper/
│   ├── live_crawler.py        ← RSS/arXiv delta detection (cron)
│   ├── corpus_builder.py      ← 48,442 lines collected
│   └── cron_crawler.py        ← systemd timer entry point
└── validator/
    ├── experiment_correlator.py ← 100% doc overlap (190/190 pairs)
    └── prediction_resolver.py ← Brier/log-loss calibration
```

---

## Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Corpus correlation | ≥30% | Current: 72.8% — PASS |
| Threshold crossing detection | <5% false positive | Precursor flags per 1K docs |
| Lead time accuracy | ±7 days | Delta flag → shift report window |
| Archetype correspondence | >50% | Flagged archetype matches shift axis |

---

*Protocol 006 v0.2 — Implementation in progress. See Protocol 006 DRAFT for full methodology.*
