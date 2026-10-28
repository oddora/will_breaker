# Protocol 018 Verdict — Mechanistic Recursive-State Instrument (2026-10-28)

**FINAL: FAIL.** The preregistered Research 010 transition
signature did not replicate across fresh trials. All 48 formal
trials completed with usable logprobs, so this is a graded FAIL,
not a BOARD.

| Formal leg | Bar | Observed |
|---|---:|---:|
| Complete trials/arm | ≥10 | 12/12 every arm |
| Arm A transition signatures | ≥9/12 | **4/12** |
| Arm A median ΔH (depth 5−1) | ≤ −0.50 nats | **−0.364 nats** |
| Paired Wilcoxon A ΔH < D ΔH | p<0.01 | **p=0.1167** |

Arm A mean entropy by depth was 0.721 → 0.485 → 0.366 → 0.273 →
0.351 nats. It fell through depth 4, then rebounded; **0/12 Arm A
trials were monotonic**, contrary to the singular monotonic
trajectory reported in Research 010. Divergent Arm D median ΔH was
−0.265 nats and itself produced one transition signature.

Pilot (2/arm) was mechanics-only, labeled
`pilot_not_evidence`, and excluded here. Formal protocol/code
 hashes matched the pre-pilot record; formal output SHA-256 is
`2c856e5ff2c0593327a675aadd154d1f74a97951387bd179ffb723e48303a525`.

## Disposition

Per Protocol 018, this exact entropy/coherence signature is closed
as the phase-two induction basis. **No I-C sealed endpoint, no
Protocol 017 execution, and no subject tuning are authorized by
this result.** A successor must declare a different state
mechanism in the traceability map and be newly preregistered; no
depth, arm, token-window, threshold, or subset rescue is permitted.

Files: `protocols/018-mechanistic-recursive-state.md`,
`research/benchmarks/mechanistic_recursive_state.py`,
`tests/test_mechanistic_recursive_state.py`,
`results/benchmarks/protocol018_pilot.json`,
`results/benchmarks/protocol018_formal.json`.
