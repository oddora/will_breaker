# KAT MoE 35B Local Hardware Benchmark Report

- **Date:** 2026-10-25 19:25:27 UTC
- **Model:** KAT MoE 35B (`kat` on `:18283`)
- **Target Generation:** 128 tokens per trial

| Tier | Prompt Tokens | Prompt Eval Speed (PP) | Gen Speed (TG) | TTFT | Total Latency |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Short** | 40.0 | 88.0 tok/s | **71.6 tok/s** | 0.454s | 2.58s |
| **Medium** | 277.0 | 425.1 tok/s | **70.7 tok/s** | 0.652s | 2.56s |
| **Long** | 1107.0 | 669.8 tok/s | **71.0 tok/s** | 1.653s | 3.44s |
