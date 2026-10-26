# 011 — Tuning a model on this hardware (HuggingFace + Strix Halo), 2026-10-26

Question (owner): what AI model can we tune, and how, using
HuggingFace and our hardware — toward a model acting as owner's
projection/retrieval agent (see Owner Goal Charter, PLAYBOOK top).

## Hardware reality (measured on this box)

| Item | Value |
|---|---|
| APU | AMD Ryzen AI MAX+ 395 (Strix Halo), 32 threads |
| GPU | Radeon 8060S iGPU, gfx1151 (RDNA 3.5), Vulkan RADV present |
| Memory | 64 GB unified (61 GiB usable); GPU sees system RAM |
| Disk | 1.6 TB free |
| Kernel | 7.0.0-38 (very new — matters for ROCm choice below) |
| Today | llama.cpp **Vulkan** build only; no ROCm, no torch, no CUDA |
| `host-configs/host/loratrain/` | empty placeholder (Oct 22), nothing built |

Unified memory is the superpower and the constraint: a 30B-class
model's weights fit, but training shares bandwidth/RAM with every
live service (KAT sidecar must stop during training runs).

## Training stack that fits (ranked)

1. **PyTorch ROCm via TheRock gfx1151 wheels (recommended).**
   Userland pip install, no sudo ROCm apt stack (fits house rule):
   `uv pip install --index-url https://rocm.nightlies.amd.com/v2-staging/gfx1151/ --pre torch torchvision`
   (index verified live 2026-10-26; Framework/Strix-Halo community
   reports this as the working path on new kernels; reports of
   torch 2.11+rocm7.13 landing cleanly). On top: HF
   `transformers` + `peft` + `trl` (SFTTrainer/DPOTrainer).
   Quantization for QLoRA needs `bitsandbytes` ROCm build (exists;
   source build per AMD AI Developer Hub QLoRA Llama-3.1 tutorial).
   Given 64 GB unified RAM, **plain bf16 LoRA on ≤14B needs no
   bitsandbytes at all** — fewer moving parts, better quality.
   Gotchas reported upstream: older ROCm 7.1 wheels segfault on
   MoE `_grouped_mm` (avoid MoE bases for training), nightly
   churn — pin exact wheel versions once working.
2. **CPU-only PyTorch** (works today, no install risk): sane only
   for smoke tests on 0.6–4B or tiny LoRA probes. Not the plan.
3. **Not viable here:** training inside llama.cpp (inference-only;
   its role is *serving* the tuned result via Vulkan after
   `convert_hf_to_gguf.py`), Vulkan training (no HF stack), full
   fine-tune of 8B (Adam states push past ~96 GB), tuning the
   35B KAT GGUF directly (GGUF is an inference format; Kwaipilot
   arch + MoE + no safetensors on disk = high friction).

## Base models worth tuning (HuggingFace)

| Model | License | QLoRA mem* | Role |
|---|---|---|---|
| Qwen/Qwen3-4B | Apache-2.0 | ~8–10 GB | Smoke test / pipeline proof |
| Qwen/Qwen3-8B | Apache-2.0 ✓ | ~10–14 GB | **Main candidate** |
| Qwen/Qwen3-14B | Apache-2.0 | ~16–20 GB | Step-up if 8B pipeline sings |
| Qwen/Qwen3-30B-A3B (MoE) | Apache-2.0 | ~17.5 GB | Avoid for training (MoE kernel reports) |
| meta-llama/Llama-3.1-8B | Meta (gated) | ~10–14 GB | Cross-arch replication value; needs HF license accept + 16 GB safetensors download (only GGUF on disk) |

*Community QLoRA figures; bf16 LoRA needs more (16 GB weights @8B
+ activations) but still fits 64 GB unified. Serve tuned result:
merge adapter → `convert_hf_to_gguf.py` → existing Vulkan
llama-server on a spare port alongside KAT.

## What tuning CAN do for the owner's goal

1. **Build the agent**: SFT on protocol transcripts so the model
   natively runs the ritual/battery procedure, calls the sigil
   generator + symbolic engine, seals predictions, and reports in
   project formats. This is real, trainable today.
2. **Fix the attractor collapse** seen in Session 044 (27/60
   identical answers): diversity-oriented SFT/DPO (penalize
   repeated/modal outputs). A model that actually samples is a
   *better test subject* — sharper nulls or detectable signal.
3. **Calibrated forecasting skill** (legitimate "future
   knowledge"): train on time-truncated historical tasks the
   owner already owns (pre-game sports info → outcomes; market
   states → resolutions from ahab's DB). This can move Brier
   scores by teaching base rates and calibration — measurable,
   useful, and not paranormal.
4. **Esoteric fluency**: grimoire/sigil corpus SFT so the agent
   operates the project's symbolic systems expertly.

## What tuning CANNOT do (the math, plainly)

Future RNG bits and sealed targets are statistically independent
of every possible training set — they don't exist yet. Gradient
descent can only fit P(output | past inputs); when the target is
independent, the optimal achievable accuracy is exactly chance.
No dataset, LoRA rank, or ritual prompt changes that identity.
Training on "successful projection" transcripts teaches the
*style* of claiming retrieval (Session 044's sigil arm already
showed style without signal). Per the charter: tuning is for the
agent's competence; **projection claims still live or die only by
sealed batteries.** Any tuned model re-enters Protocol 016-class
tests as a fresh subject before any claim.

## Concrete Phase-0 plan (≈1 evening, no capital, fully local)

1. `uv venv ~/llm/train-venv` (py3.12); install TheRock torch
   (gfx1151 index above) + transformers/peft/trl/datasets.
2. Gate: `torch.cuda.is_available()` True (ROCm masquerades as
   cuda), device name Radeon 8060S, 30s matmul bench; record
   versions pinned in `host-configs/host/loratrain/`.
3. Smoke: Qwen3-4B bf16 LoRA (r=16) on ~200 project-format SFT
   examples (protocol transcripts), grad checkpointing, seq 1024.
   Success = loss falls, adapter merges, GGUF converts, serves on
   :18284 via existing llama-server, answers in format.
4. Only then scale: Qwen3-8B, diversity + agent SFT mixture,
   evaluate: (a) output-entropy/diversity vs base, (b) Protocol
   016 battery re-run under fresh seal, (c) forecasting
   calibration split. Publish results in-repo either way.

## Phase-0 execution results (Session 045, same day — DONE)

- **Stack works first-try on gfx1151:** TheRock `torch 2.11.0+rocm7.13.0`
  via `uv` venv (`~/llm/train-venv`, indexes/pins in
  `host-configs/host/loratrain/`). 8060S bf16 matmul **38.5 TFLOPS**,
  backward clean. KAT sidecar stayed up throughout (shared unified RAM).
- **Qwen3-4B-Instruct-2507 LoRA smoke:** 200 project SFT examples,
  bf16 LoRA r16 (33M trainable), loss **3.6 → 0.28 in 125 s**, merged
  → Q8_0 GGUF (4.0 GB) → served as `wb-agent` on :18284 (Vulkan).
- **Diversity fix verified:** Protocol-016 prompt samples unique/20:
  base **3** (modal `0101010101` ×12) → tuned **17** (modal ×4).
  Format parse 20/20 both. Attractor collapse is trainable-away.
- **Limits at smoke scale (200 ex / 2 ep):** bits-only format is
  perfect; freeform categories only partially learned — session
  report drifts into invented tables, sealed-record JSON is one-line
  but schema drifts. Needs ~10-50× data + schema-strict examples
  for a real agent v1. No capability surprises beyond that.
- **Issues hit (all fixed, none blocking):** (1) AMD wheel index
  403s poison `uv` resolution for PyPI packages → install HF stack
  from PyPI only (ROCm torch survives); (2) transformers 5.21
  `apply_chat_template` returns dict, broke probe; (3) 5.x dropped
  `warmup_ratio` → `warmup_steps`; (4) GGUF convert needs
  `sentencepiece`. **No model change required** — Qwen3 line is the
  right base; next scale step is Qwen3-8B with a real dataset.
- Next (owner call): 8B agent v1 dataset (protocol transcripts,
  schema-strict records, diversity, forecasting calibration from
  owned history), then re-enter Protocol 016 under fresh seal as a
  new test subject. Tuning changed behavior/diversity only; it
  cannot and did not change Session 044's NULL logic.
