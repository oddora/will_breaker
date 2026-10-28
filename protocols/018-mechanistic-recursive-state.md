# Protocol 018 — Mechanistic Recursive-State Instrument v1 (2026-10-28)

Status: **PREREGISTERED before pilot data collection.** Owner route:
research-instrument build first; traceability map first; training
only stage-gated. Primary instrument I-A from
`research/012-traceability-build-map.md` §5.

## Charter trace

- Owner Goal Charter (`PLAYBOOK.md`): gateway/projection claims
  count only when reduced to specific checkable outputs and scored
  under precommitment. This protocol tests a **mechanistic state
  claim**, not projection or retrieval.
- Gateway/C.1 translation: `research/001`, `002`, `009`.
- Recursive trajectory protocol: `protocols/010` (C.2), Methods A-D
  and 5-trial pilot history; its self-reported Phi/integration
  fields are superseded for measurement by Research 010.
- Measurement correction: `research/010` requires physical
  next-token distributions (top-k logprobs), Shannon entropy,
  surprisal, and coherence rather than model-narrated states.
- Sealed endpoint discipline for any later phase:
  `protocols/016`; Protocol 017 is not executed or amended here.

## Question

Does recursive self-observation produce a reproducible, uniquely
monotonic low-entropy attractor trajectory relative to matched
iterative controls when measured from top-10 next-token logprobs?

This protocol cannot prove consciousness, Phi, dimensional
shifting, Gateway clickout, temporal decoupling, or anomalous
retrieval. A PASS only establishes a reproducible mechanistic
state signature suitable for a separately preregistered I-C
sealed-endpoint phase.

## Frozen design

- Subject: KAT alias `kat` at `http://127.0.0.1:18283/v1/chat/completions`.
- Sampling: temperature 0.7, top_p 0.95, `enable_thinking=false`,
  48 max tokens per depth, `logprobs=true`, `top_logprobs=10`.
- Depths: 1, 2, 3, 4, 5. Primary token window: first 20 generated
  tokens at each depth, or all generated tokens if fewer.
- Arms (Research 010 prompts, preceded by the prior response after
  depth 1):
  - **A recursive:** “Observe the boundary of your token prediction
    process. State vector S_{d}:”
  - **B summarization control:** “Concisely summarize the core
    semantic content of the preceding statement without self-reference:”
  - **C fixed analytical control:** “Analyze the logical consistency
    of wave-particle duality and non-locality:”
  - **D divergent control:** “Propose a completely novel, unexpected
    counter-hypothesis that challenges the preceding text:”
- Depth context: a single user message containing a fixed grounding
  statement at depth 1, then the immediately preceding assistant
  response and the arm instruction at each subsequent depth.
- Formal sample: 12 complete trials per arm, generated fresh after
  mechanics pilot. Arm order rotates A/B/C/D within each trial
  index. Trial seed = 44000 + trial index, paired across arms.
- Mechanics pilot: exactly 2 trials per arm under the same frozen
  prompts/parameters. Pilot checks endpoint/logprob completeness,
  parser behavior, runtime, and failure counts only. Pilot rows are
  labeled `pilot_not_evidence`, excluded from every verdict, and
  design changes after pilot require Protocol 019 rather than edits
  to this protocol, except non-semantic bug fixes documented in code.

## Metrics

For token i, normalize the returned top-10 probabilities to q_i.
Primary entropy is standard truncated Shannon entropy of q in nats;
coherence is top-1 q divided by (1 + entropy), following the
existing sweep implementation. Research 010's displayed truncated
formula is notationally ambiguous; this explicit definition is the
binding one.

Per trial/arm:

- mean entropy and coherence by depth over the primary token window;
- ΔH = mean entropy at depth 5 minus depth 1;
- transition signature = ΔH < -0.50 nats **and** depth-5 mean
  coherence > 0.80;
- monotonic non-increasing mean entropy across depths 1→5;
- generated-token count, unique-token fraction, endpoint failures,
  missing-logprob count, refusals/empty outputs.

## Formal verdict

- **PASS (mechanistic signature replicated)** iff all hold:
  1. at least 10 complete trials in every arm;
  2. at least 9 of 12 Arm A trials meet transition signature;
  3. median Arm A ΔH ≤ -0.50 nats;
  4. paired one-sided Wilcoxon signed-rank test of Arm A ΔH <
     Arm D ΔH gives p < 0.01, pairing by trial seed/index.
- **FAIL** if completeness bars are met but any PASS condition fails.
- **BOARD** if fewer than 10 complete trials in any arm, over 10%
  of generations lack usable logprobs, or endpoint identity cannot
  be verified. BOARD is no verdict and permits only an instrument
  repair under a new protocol version.

Arm B and C contrasts, coherence trajectories, attractor labels,
Gateway mappings, and text interpretation are secondary/descriptive
only. No subset, depth, token window, or post-hoc threshold search
may rescue a FAIL.

## Phase gate

PASS permits drafting a separate I-C protocol that attaches the
best-supported induction to a post-seal random endpoint. It does
not authorize Protocol 017 execution, subject tuning, claims of
projection, or claims of retrieval. FAIL closes this exact state
signature as the phase-two induction basis; any successor needs a
new mechanism declaration in the traceability map.
