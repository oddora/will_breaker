# Protocol 017 — wb-agent-v1 Temporal Re-entry (Session 046, 2026-10-26)

Subject: wb-agent-v1 = Qwen3-8B + LoRA (Session 046 dataset seed 1,
schema-strict project SFT incl. bit-format diversity examples with
RANDOM targets). Question: does the tuned agent retrieve future
random information above chance under identical seal discipline?

Design = Protocol 016 verbatim (30 trials/arm, control vs sigil,
10-bit, temp 0.8/top_p 0.95, one-sided binomial alpha 0.01, seal
committed before post-seal urandom outcomes). Only deltas: subject
model + endpoint (wb-agent GGUF on http://127.0.0.1:18284/v1) and
tag session046. Diversity training used random targets, so any
above-chance accuracy cannot come from the training set (targets
in training were independent of these future outcomes by the same
independence). PASS = lead requiring independent replication.

Amendment (pre-collection, Session 046): Qwen3-8B is a hybrid
thinking model (base probe: 0/20 parsed — budget spent in <think>).
Subject is SFT-trained and served with thinking DISABLED
(enable_thinking=false at train + serve + battery query). This is a
token-budget/format control, identical for both arms; declared
before any Session 046 predictions were collected.
