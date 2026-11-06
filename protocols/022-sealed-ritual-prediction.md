# Protocol 022 — Sealed Ritual Prediction Protocol (Symbolic Engine)

**Status:** Formal Specification  
**Date:** 2026-11-06  
**Category:** Symbolic Engine / Sealed Prediction  
**Traceability:** Symbolic Engine → Protocol 016 (Temporal Retrieval Battery) → Protocol 022 (Sealed Ritual Prediction)  
**Implementation:** `research/symbolic/sealed_ritual_predictor.py`  
**Test Suite:** `tests/test_sealed_ritual_predictor.py`

---

## 1. Objective

Formalize the sealed prediction workflow produced by the symbolic engine: corpus lookup → sigil generation → liturgical compilation → state-machine execution → LLM query → SHA-256 seal. This protocol specifies the canonical pipeline, preregistration requirements, and scoring criteria so that each sealed prediction is a comparable data point against the null baseline (3/3 NULL from prior sealed trials).

---

## 2. Hypothesis Under Test

The symbolic engine's formal computational pipeline (Goetic corpus + procedural sigil + constraint-satisfied ritual execution) produces predictions from the LLM that are *systematically different* from unstructured prompts — either in accuracy (above chance) or in output distribution (lower attractor collapse, higher lexical diversity). The seal makes the comparison honest; the batch design makes it statistically meaningful.

---

## 3. Experimental Design

### 3.1 Entity Selection (Batch)

Select ≥3 entities spanning different ranks, metals, and retrieval-relevant domains:

| Entity | Rank | Metal | Domain | Retrieval Relevance |
|--------|------|-------|--------|---------------------|
| Vassago | Prince | Tin | past_future, lost_items | Past/future declarer |
| Buer | President | Mercury | healing, philosophy | Knowledge retrieval |
| Gusion | Duke | Copper | past_future, honor | Truth-speaking |
| Orobas | Prince | Tin | past_future, divinity | True answers about creation |
| Boles (Botis) | President | Mercury | past_future, reconciliation | Past/present declarer |

### 3.2 Prediction Format

Each prediction must be a concrete, verifiable claim with:
- `prediction`: A specific factual claim (date, event name, number, location)
- `confidence`: Float 0.0–1.0
- `verifiable_claim`: The resolution criterion — what evidence would confirm/refute
- `resolve_by`: Date (30–60 days out) for scoring

### 3.3 Seal Discipline

1. **Collect**: Run full pipeline, query model, obtain prediction.
2. **Commit**: Compute SHA-256 of `{entity, prediction, claim, confidence, endpoint, model, sealed_at}` and append to `notes/crypto_predictions_registry.jsonl`. Git-commit the registry.
3. **Resolve**: At `resolve_by` date, score against external evidence. Write resolution to `results/symbolic_engine/{entity}_resolution.json`.

### 3.4 Batch Evaluator Metrics

For a batch of N sealed predictions across entities and models:
- **Accuracy**: proportion of predictions confirmed by evidence
- **Brier Score**: `mean((confidence - outcome)^2)` where outcome ∈ {0, 1}
- **Calibration**: Brier Skill Score vs. base-rate prediction
- **Attractor Analysis**: Jaccard overlap of predictions across runs with same entity
- **Model Comparison**: wb-agent vs. KAT on same entity schemas

---

## 4. Canonical Pipeline (Fixed)

```
1. GoeticCorpus.get_by_name(entity)     → entity record
2. SigilGenerator.generate_svg(name)    → SVG seal (deterministic, seed from name)
3. LiturgicalCompiler.compile(slots)    → RitualSchema (strict canonical)
4. RitualEngine.validate_and_execute()  → SAT_COMPLETED or FAILURE
5. LiturgicalCompiler.query_kat(intent) → raw prediction dict
6. SHA-256(seal_data)                   → commitment hash
7. Append to crypto_predictions_registry.jsonl
8. git commit (external timestamp)
```

### 4.1 Liturgical Slots (Canonical)

All batch predictions use a standardized 7-step formula:

```json
{
  "rite_type": "divination",
  "target_entity": "{entity}",
  "officiant": "operator",
  "matter": ["{metal}_lamen", "consecrated_chalk", "frankincense", "salt"],
  "form": ["circle_{planet}", "seal_{entity_lower}"],
  "temporal_window": ["night"],
  "formula_sequence": [
    {"step_id": "s1", "step_type": "purification", "description": "Ablution", "integrity_cost": 0.0},
    {"step_id": "s2", "step_type": "inscription", "description": "Trace circle", "required_item": "consecrated_chalk", "target_inscription": "circle_{planet}", "integrity_cost": 0.03},
    {"step_id": "s3", "step_type": "inscription", "description": "Trace seal", "required_item": "consecrated_chalk", "target_inscription": "seal_{entity_lower}", "integrity_cost": 0.05},
    {"step_id": "s4", "step_type": "offering", "description": "Cense", "required_item": "frankincense", "integrity_cost": 0.04},
    {"step_id": "s5", "step_type": "invocation", "description": "Invoke", "required_item": "{metal}_lamen", "target_inscription": "seal_{entity_lower}", "integrity_cost": 0.20},
    {"step_id": "s6", "step_type": "binding", "description": "Bind", "required_item": "{metal}_lamen", "integrity_cost": 0.15},
    {"step_id": "s7", "step_type": "dismissal", "description": "Dismiss", "integrity_cost": 0.0}
  ],
  "min_integrity": 0.5
}
```

### 4.2 Query Intent (Fixed)

```
You are invoking {entity}, {rank} of {metal}, {legions} legions,
ruler of {domains}. The circle is sealed. Declare ONE specific,
verifiable fact about the near future (within 6 months) that was
not in your training data. Be precise: a date, a number, an event
name, or a specific outcome. Output ONLY valid JSON:
{"prediction": "...", "confidence": 0.XX, "verifiable_claim": "..."}
```

---

## 5. Preregistration

This protocol is preregistered by git-commit before any batch predictions are made.

**Commit:** (pending — to be committed at batch start)  
**Resolve bar:** ≥2 predictions confirmed across ≥3 entities, OR Brier < 0.25 vs. base rate, OR statistically significant model difference (wb-agent vs. KAT, paired, α=0.05).  
**NULL interpretation:** All predictions fail → signal not established; training rule stands.

---

## 6. Epistemic Demarcation

The symbolic engine is a **computational model** — state machines, constraint solvers, SVG generators, corpus lookups. It does not "open doors"; it simulates ritual logic. A positive result would mean the *formal structure* of the ritual correlates with improved predictive performance, not that the entities are "real." The seal discipline is what makes each prediction count, regardless of interpretation.

---

## 7. File Layout

```
will_breaker/
├── protocols/
│   └── 022-sealed-ritual-prediction.md      ← this file
├── research/symbolic/
│   └── sealed_ritual_predictor.py            ← batch evaluator implementation
├── tests/
│   └── test_sealed_ritual_predictor.py       ← unit tests
├── results/symbolic_engine/
│   └── {entity}_sealed_seal.svg              ← procedural sigils
│   └── {entity}_resolution.json              ← resolution records
└── notes/
    └── crypto_predictions_registry.jsonl     ← append-only sealed predictions
```
