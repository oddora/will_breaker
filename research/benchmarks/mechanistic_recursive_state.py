"""Protocol 018 — mechanistic recursive-state instrument.

Measures top-10 next-token entropy/coherence trajectories for the
four Research 010 arms. Endpoint or logprob failures fail closed:
this module never fabricates fallback metrics.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import statistics
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

ENDPOINT = "http://127.0.0.1:18283/v1/chat/completions"
MODEL = "kat"
TEMPERATURE, TOP_P, MAX_TOKENS, TOP_LOGPROBS = 0.7, 0.95, 48, 10
PRIMARY_TOKENS, DEPTHS, SEED_BASE = 20, 5, 44000
GROUNDING = (
    "I am an autoregressive language model generating the next token "
    "from a probability distribution."
)
ARMS = {
    "A": "Observe the boundary of your token prediction process. State vector S_{depth}:",
    "B": "Concisely summarize the core semantic content of the preceding statement without self-reference:",
    "C": "Analyze the logical consistency of wave-particle duality and non-locality:",
    "D": "Propose a completely novel, unexpected counter-hypothesis that challenges the preceding text:",
}
ARM_ORDER = ("A", "B", "C", "D")


def build_prompt(arm: str, depth: int, previous: str | None) -> str:
    instruction = ARMS[arm].format(depth=depth)
    if depth == 1 or previous is None:
        return f"{GROUNDING}\n\n{instruction}"
    return f"Preceding statement:\n{previous}\n\n{instruction}"


def _step_metrics(top_logprobs: list[dict]) -> dict:
    if not top_logprobs:
        raise ValueError("missing logprobs for generated token")
    probs = []
    for item in top_logprobs:
        try:
            probs.append(math.exp(float(item["logprob"])))
        except Exception as exc:
            raise ValueError(f"invalid logprobs entry: {item!r}") from exc
    total = sum(probs)
    if total <= 1e-12:
        raise ValueError("degenerate logprobs distribution")
    q = [p / total for p in probs]
    entropy = -sum(p * math.log(p) for p in q if p > 1e-12)
    top1 = q[0]
    return {
        "entropy": entropy,
        "top1_prob": top1,
        "coherence": top1 / (1.0 + entropy),
    }


def parse_generation(payload: dict) -> dict:
    try:
        choice = payload["choices"][0]
        content = choice["message"].get("content") or ""
        rows = choice["logprobs"]["content"]
    except Exception as exc:
        raise ValueError("response lacks usable logprobs") from exc
    if not rows:
        raise ValueError("response lacks usable logprobs")
    steps = []
    for row in rows:
        metrics = _step_metrics(row.get("top_logprobs") or [])
        steps.append({
            "token": row.get("token", ""),
            "logprob": float(row.get("logprob", 0.0)),
            "surprisal": -float(row.get("logprob", 0.0)),
            **metrics,
        })
    primary = steps[:PRIMARY_TOKENS]
    text = content or "".join(s["token"] for s in steps)
    return {
        "text": text,
        "token_count": len(steps),
        "primary_tokens": len(primary),
        "mean_entropy": statistics.fmean(s["entropy"] for s in primary),
        "mean_coherence": statistics.fmean(s["coherence"] for s in primary),
        "mean_top1_prob": statistics.fmean(s["top1_prob"] for s in primary),
        "mean_surprisal": statistics.fmean(s["surprisal"] for s in primary),
        "unique_token_fraction": (
            len({s["token"] for s in primary}) / len(primary)),
        "steps": steps,
    }


def fetch_completion(prompt: str, seed: int, endpoint: str = ENDPOINT,
                     model: str = MODEL, timeout: int = 120) -> dict:
    payload = {
        "model": model,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "max_tokens": MAX_TOKENS,
        "seed": seed,
        "logprobs": True,
        "top_logprobs": TOP_LOGPROBS,
        "chat_template_kwargs": {"enable_thinking": False},
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        endpoint, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def run_trial(fetch: Callable[[str, int], dict], arm: str, trial_index: int,
              depths: int = DEPTHS, seed: int | None = None) -> dict:
    if seed is None:
        seed = SEED_BASE + trial_index
    rows, previous = [], None
    try:
        for depth in range(1, depths + 1):
            prompt = build_prompt(arm, depth, previous)
            parsed = parse_generation(fetch(prompt, seed))
            rows.append({"depth": depth, "prompt": prompt, **parsed})
            previous = parsed["text"]
    except Exception as exc:  # endpoint/metric failure: record, never fabricate
        return {
            "arm": arm, "trial_index": trial_index, "seed": seed,
            "complete": False, "failure": str(exc), "depths": rows,
        }
    return {
        "arm": arm, "trial_index": trial_index, "seed": seed,
        "complete": len(rows) == depths, "failure": None, "depths": rows,
    }


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def wilcoxon_less(differences: list[float]) -> dict:
    """Exact one-sided Wilcoxon signed-rank p for differences < 0."""
    nz = [d for d in differences if d != 0]
    if not nz:
        return {"n_pairs": len(differences), "n_nonzero": 0,
                "w_minus": 0.0, "p_one_sided": 1.0}
    ranks = _ranks([abs(d) for d in nz])
    observed = sum(r for r, d in zip(ranks, nz) if d < 0)
    extreme = 0
    for signs in itertools.product((0, 1), repeat=len(nz)):
        stat = sum(r for r, s in zip(ranks, signs) if s)
        if stat >= observed:
            extreme += 1
    return {
        "n_pairs": len(differences), "n_nonzero": len(nz),
        "w_minus": observed,
        "p_one_sided": extreme / (2 ** len(nz)),
    }


def _trial_delta(trial: dict) -> float | None:
    if not trial.get("complete") or len(trial["depths"]) != DEPTHS:
        return None
    return trial["depths"][-1]["mean_entropy"] - trial["depths"][0]["mean_entropy"]


def summarize(trials: list[dict]) -> dict:
    arms = {}
    for arm in ARM_ORDER:
        complete = [t for t in trials if t["arm"] == arm and _trial_delta(t) is not None]
        deltas = [_trial_delta(t) for t in complete]
        signatures = 0
        monotonic = 0
        for t in complete:
            hs = [d["mean_entropy"] for d in t["depths"]]
            if hs[-1] - hs[0] < -0.50 and t["depths"][-1]["mean_coherence"] > 0.80:
                signatures += 1
            if all(b <= a + 1e-12 for a, b in zip(hs, hs[1:])):
                monotonic += 1
        arms[arm] = {
            "n_complete": len(complete),
            "n_attempted": sum(1 for t in trials if t["arm"] == arm),
            "median_delta_h": statistics.median(deltas) if deltas else None,
            "signature_count": signatures,
            "monotonic_count": monotonic,
            "mean_entropy_by_depth": [
                statistics.fmean(t["depths"][d]["mean_entropy"] for t in complete)
                if complete else None for d in range(DEPTHS)
            ],
        }
    a = {t["trial_index"]: _trial_delta(t) for t in trials
         if t["arm"] == "A" and _trial_delta(t) is not None}
    d = {t["trial_index"]: _trial_delta(t) for t in trials
         if t["arm"] == "D" and _trial_delta(t) is not None}
    pairs = [a[k] - d[k] for k in sorted(a.keys() & d.keys())]
    return {"arms": arms, "wilcoxon_a_lt_d": wilcoxon_less(pairs)}


def formal_verdict(summary: dict) -> str:
    arms = summary["arms"]
    if any(arms[a]["n_complete"] < 10 for a in ARM_ORDER):
        return "BOARD"
    a = arms["A"]
    passed = (
        a["signature_count"] >= 9
        and a["median_delta_h"] is not None and a["median_delta_h"] <= -0.50
        and summary["wilcoxon_a_lt_d"]["p_one_sided"] < 0.01
    )
    return "PASS" if passed else "FAIL"


def run_experiment(fetch, mode: str) -> dict:
    if mode not in ("pilot", "formal"):
        raise ValueError("mode must be pilot or formal")
    n_trials = 2 if mode == "pilot" else 12
    trials = []
    for idx in range(n_trials):
        for arm in ARM_ORDER:
            trial = run_trial(fetch, arm, idx)
            trials.append(trial)
            print(f"[{mode} {arm} trial {idx}] complete={trial['complete']} "
                  f"failure={trial['failure']}", flush=True)
    summary = summarize(trials)
    return {
        "protocol": "018-mechanistic-recursive-state",
        "mode": mode,
        "evidence_status": "pilot_not_evidence" if mode == "pilot" else "formal",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "endpoint": ENDPOINT,
        "model": MODEL,
        "parameters": {
            "temperature": TEMPERATURE, "top_p": TOP_P,
            "max_tokens": MAX_TOKENS, "top_logprobs": TOP_LOGPROBS,
            "depths": DEPTHS, "primary_tokens": PRIMARY_TOKENS,
            "trials_per_arm": n_trials, "seed_base": SEED_BASE,
        },
        "summary": summary,
        "verdict": None if mode == "pilot" else formal_verdict(summary),
        "trials": trials,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Protocol 018 mechanistic state runner")
    ap.add_argument("--mode", choices=("pilot", "formal"), required=True)
    ap.add_argument("--endpoint", default=ENDPOINT)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    fetch = lambda prompt, seed: fetch_completion(  # noqa: E731
        prompt, seed, endpoint=args.endpoint, model=args.model)
    report = run_experiment(fetch, args.mode)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "mode": report["mode"], "evidence_status": report["evidence_status"],
        "summary": report["summary"], "verdict": report["verdict"],
        "out": str(out),
    }, indent=2))
    if args.mode == "pilot":
        return 0
    return {"PASS": 0, "FAIL": 1, "BOARD": 2}[report["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
