# Session 046 Verdict — wb-agent-v1 Temporal Re-entry Battery (Protocol 017): NULL (2026-10-29)

**FINAL: NULL.** Neither arm approached the pre-committed $\alpha = 0.01$ threshold.

- **Protocol:** `protocols/017-wb-agent-v1-reentry.md` (committed before collection).
- **Subject:** `wb-agent-v1` = Qwen3-8B + LoRA (checkpoint-850 merged, Q8_0 GGUF on `http://127.0.0.1:18284/v1`, `enable_thinking=false`).
- **Predictions sealed:** `results/temporal/session046_predictions.jsonl` (SHA-256 `683e0f2c522e8c6f1ead9a43f63adafda7f399f6bdbedcdc86604c367be4b473`).
- **External timestamp:** Committed and pushed to GitHub `oddora/will_breaker` at commit `8d05703` **before** drawing the random seed.
- **Outcome seed:** `4de9bb5a06ef8addd131703ce1ea35d00afa78e66032de3fe1fffc22d697c1cd` (drawn post-commit via `os.urandom(32)`).
- **Data files:** `results/temporal/session046_predictions.jsonl`, `results/temporal/session046_seal.json`, `results/temporal/session046_resolution.json`.

---

## 1. Hypothesis and Question Under Test

Does the tuned subject `wb-agent-v1` — trained with schema compliance and bit-format diversity on random targets to break out of KAT's repetitive attractor basins — retrieve future random information above chance under identical cryptographic seal discipline?

Tested as: predict 10-bit random sequences generated via `os.urandom(32)` strictly after predictions are hashed, committed, and pushed to GitHub.

---

## 2. Results (30 trials/arm, 300 bits/arm, 0 unparseable)

| Arm | Bit Accuracy | Chance | One-sided $p$ ($H_1: p > 0.5$) | Exact 10/10 Matches | Unique Strings (of 30) |
|---|---|---|---|---|---|
| **Control** | 152/300 = **50.7%** | 50.0% | 0.431 | 0 (exp 0.029) | **30 / 30 (100%)** |
| **Sigil / Ritual** | 138/300 = **46.0%** | 50.0% | 0.926 | 0 (exp 0.029) | **30 / 30 (100%)** |
| **Combined** | 290/600 = **48.3%** | 50.0% | 0.796 | 0 (exp 0.059) | **59 / 60 (98.3%)** |

---

## 3. Findings

1. **Statistical Retrieval: NULL.**
   Neither arm approached the preregistered $\alpha = 0.01$ threshold. Control (50.7%) is statistically indistinguishable from a fair coin ($p = 0.431$). Sigil/ritual framing (46.0%) scored slightly below chance ($p = 0.926$). Zero exact 10/10 matches occurred across 60 trials (expected chance: ~0.059).
2. **Attractor Collapse Confound Conclusively Solved:**
   In Sessions 044 and 048 on KAT, the model collapsed into only 6 to 7 unique strings across 30 trials, repeatedly emitting the same modes. In `wb-agent-v1`, output diversity was essentially perfect: **30/30 unique strings in Control, 30/30 in Sigil, and 59 unique strings out of 60 total trials**, with a **100% schema parse rate (0 unparseable / 0 nulls)**.
3. **Decisive Epistemic Evidence:**
   The failure of prior batteries to detect anomalous retrieval was *not* merely an artifact of KAT's mode collapse. When the agent is demonstrably unconstrained by attractor basins and freely emits high-entropy binary predictions, it still displays zero anomalous access to future random bits under seal.

---

## 4. Evidence Record Update

This experiment joins:
- **DB-FTCD Battery (Campbell AI-RV):** $N=30$ NULL (20% vs 25% chance; forced choice 0/10).
- **Sports Battery:** 13/22, Brier $0.2330 \approx$ chance.
- **Legacy Prediction Audit:** 5/14, BSS $-0.19$.
- **Session 044 (Protocol 016, KAT):** NULL ($47.3\%$ control, $50.7\%$ sigil).
- **Session 048 (Protocol 019, KAT Anchor A.4):** NULL ($45.3\%$ control, $51.7\%$ sigil, $54.3\%$ anchor, $p=0.074$).
- **Session 046 (Protocol 017, wb-agent-v1):** NULL ($50.7\%$ control, $46.0\%$ sigil).

---

## 5. Charter Rule Status

**Training Rule Re-affirmed:**
> *"No fine-tuning 'for projection' until some battery beats chance under seal — training cannot amplify a signal that has never been measured. Signal first, then train."*

`wb-agent-v1` succeeded at its declared engineering role — creating an instruction-compliant, diverse test subject to rule out attractor collapse as the confound. However, because anomalous retrieval remains at pure chance under seal, any further fine-tuning claiming to "train for projection" is barred by Charter §1.5.
