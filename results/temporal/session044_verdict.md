# Session 044 Verdict — Temporal Retrieval Battery v1: NULL (2026-10-26)

Protocol: `protocols/016-temporal-retrieval-battery.md` (committed
`c4377ad` before collection). Predictions sealed + committed
`8a2df36` (sha256 `903ab155…`) **before** the outcome seed existed.
Seed drawn at resolve: `d208a054…f141f9`. Data:
`session044_predictions.jsonl`, `session044_resolution.json`.

## Question (owner hypothesis)
Can KAT retrieve information from the future — and do sigil/ritual
procedures unlock it? Tested as: predict 10-bit random sequences
generated only after the predictions were sealed.

## Results (30 trials/arm, 300 bits/arm, 0 unparseable)

| Arm | Bit accuracy | Chance | One-sided p | Exact 10/10 |
|---|---|---|---|---|
| Control | 142/300 = 47.3% | 50% | 0.837 | 0 |
| Sigil/ritual | 152/300 = 50.7% | 50% | 0.431 | 0 |

**NULL.** Neither arm approached the pre-committed α=0.01 bar
(~56% needed). Sigil vs control difference (3.3pp) is noise.

## Strongest secondary finding: output attractor
60 "independent" predictions collapsed to 9 (control) / 8 (sigil)
unique strings; a single string (`0110100110`) was emitted 27/60
times. The model was not exploring a future — it fell into its
usual low-entropy attractors (cf. Paper 010). Ritual framing did
not diversify or inform the output.

## What this does and does not settle
- Settles: KAT (kat-philly, temp 0.8), with or without the sigil
  procedure, does not retrieve not-yet-existent random information
  above chance. Battery had ~93% power for a 60%-accuracy effect.
- Joins: DB-FTCD N=30 NULL, sports ≈ chance. Three sealed,
  independent nulls on the retrieval hypothesis.
- Does not settle: other models, other tasks, effects < ~56% bit
  accuracy, or effects claimed to need training first. Any of
  those is testable the same way — new seal, new battery.

## Training rule (charter) applied
No signal has ever been measured under seal, so there is nothing
to train toward yet. If the owner wants the training phase, the
honest sequence is: (1) bigger/diverse batteries (second model:
Llama-3.1-8B on disk; place-description DB-FTCD variants; ranked
future events) until something beats chance twice independently,
or the line is closed; (2) only then LoRA/fine-tune experiments
(`host-configs/host/loratrain`), always re-tested under fresh seal.
