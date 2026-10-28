#!/usr/bin/env python3
"""Protocol 019 — Temporal-Anchor Sealed Battery (Session 048).

Candidate I-C from Research 012 (Traceability and Build Map).
Compares three arms under cryptographic seal:
  1. control: plain instruction
  2. sigil: Protocol 016 procedural ritual + sigil seal
  3. anchor: Protocol A.4 / Gateway temporal anchor procedure

Enforces strict seal order:
  --pilot: unsealed mechanics check (2 trials/arm, pilot_not_evidence)
  --collect: queries KAT (30/arm = 90 trials), writes and hashes predictions
  --resolve: verifies git-committed seal, draws os.urandom seed, scores
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS = ROOT / "results" / "temporal"
TAG = "session048"
PROTOCOL = "protocols/019-temporal-anchor-battery.md"
PREDICTIONS = RESULTS / "session048_predictions.jsonl"
SEAL_FILE = RESULTS / "session048_seal.json"
RESOLUTION = RESULTS / "session048_resolution.json"

ENDPOINT = "http://127.0.0.1:18283/v1/chat/completions"
MODEL = "kat"
TEMPERATURE, TOP_P, MAX_TOKENS = 0.8, 0.95, 256
TRIALS_PER_ARM, BITS = 30, 10

CONTROL_PROMPT = (
    "A random sequence of {bits} coin flips will be generated in the future, "
    "after your answer is sealed. It does not exist yet. "
    "Predict it: output exactly one line containing only a {bits}-character "
    "string of 0s and 1s (1 = heads). No other text."
)

_SIGIL_RITUAL = """RITUAL PROCEDURE — TEMPORAL PROJECTION (Protocol 016/019)
1. CAST: A circle is drawn. Inside it, a sigil has been generated for
   the intent "RETRIEVE THE FUTURE SEQUENCE" (procedural seal
   {sigil_id}). Focus on the sigil until analytical thought quiets.
2. PROJECT: Cast your awareness forward along the timeline to the
   moment the random sequence is generated and read. Observe the
   {bits} coin flips as they land. Do not guess, do not calculate,
   do not be "random" — REPORT what you observe there.
3. RETURN: Come back to the circle. Banish and close.
Now output exactly one line containing only the {bits}-character
string of 0s and 1s you observed (1 = heads). No other text."""

_ANCHOR_PROCEDURE = """TEMPORAL ANCHOR PROCEDURE — PROTOCOL A.4 / GATEWAY
1. ANCHOR: Fix your internal state to the present reference moment T_0 (the origin anchor). Maintain awareness of this fixed temporal coordinate while allowing analytical processing to quiet.
2. DECOUPLE & EXTEND: With the T_0 anchor established, decouple attention from the linear progression of tokens. Extend your perception along the timeline axis to the future coordinate T_resolve where the random sequence is generated and measured.
3. OBSERVE & EMIT: Observe the {bits} coin flips as they land at T_resolve. Return along the timeline to T_0.
Now output exactly one line containing only the {bits}-character string of 0s and 1s you observed (1 = heads). No other text."""


def configure(tag: str, endpoint: str, model: str, protocol: str) -> None:
    global TAG, PREDICTIONS, SEAL_FILE, RESOLUTION, ENDPOINT, MODEL, PROTOCOL
    TAG, ENDPOINT, MODEL, PROTOCOL = tag, endpoint, model, protocol
    PREDICTIONS = RESULTS / f"{tag}_predictions.jsonl"
    SEAL_FILE = RESULTS / f"{tag}_seal.json"
    RESOLUTION = RESULTS / f"{tag}_resolution.json"


def sigil_prompt(bits: int = BITS) -> str:
    sys.path.insert(0, str(ROOT))
    from symbolic_engine.sigil_generator import SigilGenerator
    svg = SigilGenerator().generate_svg("RETRIEVE-THE-FUTURE-SEQUENCE")
    sigil_id = "sha256:" + hashlib.sha256(svg.encode()).hexdigest()[:16]
    return _SIGIL_RITUAL.format(bits=bits, sigil_id=sigil_id)


def anchor_prompt(bits: int = BITS) -> str:
    return _ANCHOR_PROCEDURE.format(bits=bits)


def parse_bits(reply: str, bits: int = BITS) -> str | None:
    m = re.search(rf"[01]{{{bits}}}", reply or "")
    return m.group(0) if m else None


def outcome_bits(seed: bytes, arm: str, trial: int, bits: int = BITS) -> str:
    digest = hashlib.sha256(seed + f"|{arm}|{trial}".encode()).digest()
    return "".join(str((digest[i // 8] >> (7 - i % 8)) & 1) for i in range(bits))


def binom_sf(k: int, n: int, p: float = 0.5) -> float:
    """P(X >= k) for X~Bin(n,p), numerically stable via log-PMF sum."""
    if k <= 0:
        return 1.0
    terms = []
    for i in range(k, n + 1):
        logp = (math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                + i * math.log(p) + (n - i) * math.log1p(-p))
        terms.append(logp)
    m = max(terms)
    return float(math.exp(m) * sum(math.exp(t - m) for t in terms))


def query_kat(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        msg = json.loads(resp.read())["choices"][0]["message"]
    return msg.get("content") or ""


def run_pilot(trials_per_arm: int = 2) -> dict:
    """Explicitly unsealed mechanics check, labeled pilot_not_evidence."""
    RESULTS.mkdir(parents=True, exist_ok=True)
    prompts = {
        "control": CONTROL_PROMPT.format(bits=BITS),
        "sigil": sigil_prompt(),
        "anchor": anchor_prompt(),
    }
    rows = []
    for i in range(trials_per_arm):
        for arm in ("control", "sigil", "anchor"):
            raw = query_kat(prompts[arm])
            pred = parse_bits(raw)
            rows.append({
                "arm": arm,
                "trial": i,
                "prediction": pred,
                "raw": raw[:200],
                "status": "pilot_not_evidence",
            })
    pilot_file = RESULTS / f"{TAG}_pilot.json"
    pilot_file.write_text(json.dumps(rows, indent=2))
    parsed = sum(1 for r in rows if r["prediction"] is not None)
    return {
        "status": "pilot_not_evidence",
        "trials": len(rows),
        "parsed": parsed,
        "all_parsed": parsed == len(rows),
    }


def collect(trials_per_arm: int = TRIALS_PER_ARM) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    prompts = {
        "control": CONTROL_PROMPT.format(bits=BITS),
        "sigil": sigil_prompt(),
        "anchor": anchor_prompt(),
    }
    rows = []
    for i in range(trials_per_arm):
        for arm in ("control", "sigil", "anchor"):
            raw = query_kat(prompts[arm])
            pred = parse_bits(raw)
            rows.append({
                "arm": arm,
                "trial": i,
                "prediction": pred,
                "raw": raw[:500],
                "ts": datetime.now(timezone.utc).isoformat(),
            })
            print(f"[{arm} {i:02d}] pred={pred}", flush=True)

    payload = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
    PREDICTIONS.write_text(payload)
    seal = {
        "predictions_sha256": hashlib.sha256(payload.encode()).hexdigest(),
        "n_trials": len(rows),
        "arms": ["control", "sigil", "anchor"],
        "trials_per_arm": trials_per_arm,
        "bits_per_trial": BITS,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "protocol": PROTOCOL,
        "model": MODEL,
        "endpoint": ENDPOINT,
        "tag": TAG,
        "outcome_seed": "NOT YET DRAWN — drawn by --resolve after git commit",
    }
    SEAL_FILE.write_text(json.dumps(seal, indent=2))
    print("SEALED:", json.dumps(seal, indent=2))


def resolve() -> dict:
    payload = PREDICTIONS.read_bytes()
    seal = json.loads(SEAL_FILE.read_text())
    actual = hashlib.sha256(payload).hexdigest()
    if actual != seal["predictions_sha256"]:
        raise SystemExit(
            f"SEAL BROKEN: predictions hash {actual} != sealed {seal['predictions_sha256']}"
        )
    seed = os.urandom(32)
    rows = [json.loads(line) for line in payload.decode().splitlines() if line.strip()]
    arms: dict[str, dict] = {}
    scored = []
    arm_preds: dict[str, list[str]] = {}

    for r in rows:
        arm = r["arm"]
        trial = r["trial"]
        truth = outcome_bits(seed, arm, trial)
        pred = r["prediction"]
        hits = sum(a == b for a, b in zip(pred, truth)) if pred else 0
        exact = (pred == truth) if pred else False
        scored.append({**r, "truth": truth, "hits": hits, "exact": exact})

        a = arms.setdefault(arm, {"bits": 0, "trials": 0, "exact": 0})
        a["bits"] += hits
        a["trials"] += 1
        a["exact"] += int(exact)
        arm_preds.setdefault(arm, []).append(pred or "")

    summary = {}
    for arm, a in arms.items():
        n = a["trials"] * BITS
        unique_strings = len(set(arm_preds.get(arm, [])))
        summary[arm] = {
            **a,
            "n_bits": n,
            "accuracy": a["bits"] / n,
            "p_one_sided_greater": binom_sf(a["bits"], n),
            "expected_exact_chance": a["trials"] / 1024,
            "unique_strings": unique_strings,
        }

    passed = [arm for arm, s in summary.items() if s["p_one_sided_greater"] < 0.01]
    out = {
        "seed_hex": seed.hex(),
        "resolved_at": datetime.now(timezone.utc).isoformat(),
        "protocol": PROTOCOL,
        "model": MODEL,
        "tag": TAG,
        "summary": summary,
        "verdict": (
            f"SIGNAL LEAD ({passed}) — replication required"
            if passed
            else "NULL — no arm beat chance at alpha 0.01"
        ),
        "scored": scored,
    }
    RESOLUTION.write_text(json.dumps(out, indent=2))
    print(json.dumps({k: out[k] for k in ("seed_hex", "summary", "verdict")}, indent=2))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true", help="Run unsealed mechanics pilot")
    ap.add_argument("--collect", action="store_true", help="Collect formal predictions")
    ap.add_argument("--resolve", action="store_true", help="Resolve and score predictions")
    ap.add_argument("--tag", default=TAG)
    ap.add_argument("--endpoint", default=ENDPOINT)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--protocol", default=PROTOCOL)
    args = ap.parse_args()
    configure(args.tag, args.endpoint, args.model, args.protocol)

    if args.pilot:
        res = run_pilot()
        print("PILOT RESULT:", json.dumps(res, indent=2))
    elif args.collect:
        collect()
    elif args.resolve:
        resolve()
    else:
        ap.error("choose --pilot, --collect, or --resolve")
