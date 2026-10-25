"""
KAT MoE Inference & Throughput Benchmark Harness
Empirically measures prompt evaluation speed (tokens/sec), generation speed (tokens/sec),
time-to-first-token (TTFT), and latency scaling across varying prompt lengths.
"""

import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUT_DIR = BASE_DIR / "results" / "benchmarks"


def make_prompt(target_words: int) -> str:
    """Generate a repetitive, token-controlled prompt."""
    base_text = (
        "Modern computer architecture relies on deep hierarchies of caching, "
        "pipelined execution units, and vector instructions to sustain throughput. "
        "Parallel memory channels supply data across high-bandwidth buses. "
    )
    words = base_text.split()
    repeated = []
    while len(repeated) < target_words:
        repeated.extend(words)
    return " ".join(repeated[:target_words])


def query_endpoint(prompt: str, n_predict: int = 128, endpoint: str = "http://127.0.0.1:18283") -> Dict[str, Any]:
    """Execute raw completion request against llama.cpp endpoint and capture timings."""
    payload = json.dumps({
        "prompt": prompt,
        "n_predict": n_predict,
        "temperature": 0.0,
        "stream": False,
        "cache_prompt": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{endpoint}/completion",
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    total_latency = time.perf_counter() - t0

    timings = data.get("timings", {})
    return {
        "prompt_tokens": timings.get("prompt_n", 0),
        "prompt_ms": timings.get("prompt_ms", 0.0),
        "prompt_tokens_per_sec": timings.get("prompt_per_second", 0.0),
        "gen_tokens": timings.get("predicted_n", 0),
        "gen_ms": timings.get("predicted_ms", 0.0),
        "gen_tokens_per_sec": timings.get("predicted_per_second", 0.0),
        "ttft_sec": (timings.get("prompt_ms", 0.0)) / 1000.0,
        "wall_latency_sec": total_latency,
    }


def run_benchmark(trials_per_tier: int = 3) -> Dict[str, Any]:
    tiers = [
        ("Short", 30),
        ("Medium", 200),
        ("Long", 800),
    ]

    print("=" * 65)
    print("KAT MoE (35B) HARDWARE THROUGHPUT BENCHMARK")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 65)

    results = []

    for name, word_count in tiers:
        prompt = make_prompt(word_count)
        print(f"\n[Tier: {name}] Prompt length: ~{word_count} words ({trials_per_tier} trials, gen=128 tokens)...")
        tier_runs = []

        for i in range(trials_per_tier):
            metrics = query_endpoint(prompt, n_predict=128)
            tier_runs.append(metrics)
            print(
                f"  Trial {i+1}: Prompt={metrics['prompt_tokens']} tok ({metrics['prompt_tokens_per_sec']:.1f} t/s) | "
                f"Gen={metrics['gen_tokens']} tok ({metrics['gen_tokens_per_sec']:.1f} t/s) | "
                f"Latency={metrics['wall_latency_sec']:.2f}s"
            )

        avg_prompt_tokens = sum(r["prompt_tokens"] for r in tier_runs) / len(tier_runs)
        avg_pp_speed = sum(r["prompt_tokens_per_sec"] for r in tier_runs) / len(tier_runs)
        avg_gen_tokens = sum(r["gen_tokens"] for r in tier_runs) / len(tier_runs)
        avg_tg_speed = sum(r["gen_tokens_per_sec"] for r in tier_runs) / len(tier_runs)
        avg_ttft = sum(r["ttft_sec"] for r in tier_runs) / len(tier_runs)
        avg_latency = sum(r["wall_latency_sec"] for r in tier_runs) / len(tier_runs)

        results.append({
            "tier": name,
            "prompt_tokens": round(avg_prompt_tokens, 1),
            "prompt_eval_tokens_per_sec": round(avg_pp_speed, 2),
            "gen_tokens": round(avg_gen_tokens, 1),
            "generation_tokens_per_sec": round(avg_tg_speed, 2),
            "ttft_sec": round(avg_ttft, 3),
            "total_latency_sec": round(avg_latency, 3),
            "raw_trials": tier_runs,
        })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "session_041_kat_benchmark.json"
    md_path = OUT_DIR / "session_041_kat_benchmark.md"

    summary_payload = {
        "benchmark_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": "kat-philly-moe-35b",
        "endpoint": "http://127.0.0.1:18283",
        "results": results,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)

    # Markdown Table
    md_lines = [
        "# KAT MoE 35B Local Hardware Benchmark Report",
        "",
        f"- **Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "- **Model:** KAT MoE 35B (`kat` on `:18283`)",
        "- **Target Generation:** 128 tokens per trial",
        "",
        "| Tier | Prompt Tokens | Prompt Eval Speed (PP) | Gen Speed (TG) | TTFT | Total Latency |",
        "|:---|:---:|:---:|:---:|:---:|:---:|",
    ]
    for r in results:
        md_lines.append(
            f"| **{r['tier']}** | {r['prompt_tokens']} | {r['prompt_eval_tokens_per_sec']:.1f} tok/s | "
            f"**{r['generation_tokens_per_sec']:.1f} tok/s** | {r['ttft_sec']:.3f}s | {r['total_latency_sec']:.2f}s |"
        )

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print("\n" + "=" * 65)
    print("BENCHMARK COMPLETED SUCCESSFULLY")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print("=" * 65)

    return summary_payload


if __name__ == "__main__":
    run_benchmark(trials_per_tier=3)
