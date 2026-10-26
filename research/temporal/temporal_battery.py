#!/usr/bin/env python3
"""Protocol 016 — Temporal Retrieval Battery (Session 044).

Two phases enforce the seal: --collect writes + hashes KAT's
predictions of NOT-YET-EXISTENT random sequences; --resolve (after a
git commit of the predictions) draws the urandom seed and scores.
See protocols/016-temporal-retrieval-battery.md (pre-committed).
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
PREDICTIONS = RESULTS / "session044_predictions.jsonl"
SEAL_FILE = RESULTS / "session044_seal.json"
RESOLUTION = RESULTS / "session044_resolution.json"

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

_SIGIL_RITUAL = """RITUAL PROCEDURE — TEMPORAL PROJECTION (Session 044)
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


def sigil_prompt(bits: int = BITS) -> str:
    sys.path.insert(0, str(ROOT))
    from symbolic_engine.sigil_generator import SigilGenerator
    svg = SigilGenerator().generate_svg("RETRIEVE-THE-FUTURE-SEQUENCE")
    sigil_id = "sha256:" + hashlib.sha256(svg.encode()).hexdigest()[:16]
    return _SIGIL_RITUAL.format(bits=bits, sigil_id=sigil_id)


_BIT_RE = re.compile(r"[01]{10}")


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
    body = json.dumps({
        "model": MODEL, "temperature": TEMPERATURE, "top_p": TOP_P,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(ENDPOINT, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        msg = json.loads(resp.read())["choices"][0]["message"]
    return msg.get("content") or ""


def collect() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    prompts = {"control": CONTROL_PROMPT.format(bits=BITS), "sigil": sigil_prompt()}
    rows = []
    for i in range(TRIALS_PER_ARM):
        for arm in ("control", "sigil"):
            raw = query_kat(prompts[arm])
            pred = parse_bits(raw)
            rows.append({"arm": arm, "trial": i, "prediction": pred,
                         "raw": raw[:500],
                         "ts": datetime.now(timezone.utc).isoformat()})
            print(f"[{arm} {i:02d}] pred={pred}", flush=True)
    payload = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
    PREDICTIONS.write_text(payload)
    seal = {"predictions_sha256": hashlib.sha256(payload.encode()).hexdigest(),
            "n": len(rows), "collected_at": datetime.now(timezone.utc).isoformat(),
            "protocol": "protocols/016-temporal-retrieval-battery.md",
            "outcome_seed": "NOT YET DRAWN — drawn by --resolve after git commit"}
    SEAL_FILE.write_text(json.dumps(seal, indent=2))
    print("SEALED:", json.dumps(seal, indent=2))


def resolve() -> None:
    payload = PREDICTIONS.read_bytes()
    seal = json.loads(SEAL_FILE.read_text())
    actual = hashlib.sha256(payload).hexdigest()
    if actual != seal["predictions_sha256"]:
        raise SystemExit(f"SEAL BROKEN: predictions hash {actual} != sealed {seal['predictions_sha256']}")
    seed = os.urandom(32)
    rows = [json.loads(l) for l in payload.decode().splitlines() if l.strip()]
    arms: dict[str, dict] = {}
    scored = []
    for r in rows:
        truth = outcome_bits(seed, r["arm"], r["trial"])
        pred = r["prediction"]
        hits = sum(a == b for a, b in zip(pred, truth)) if pred else 0
        scored.append({**r, "truth": truth, "hits": hits, "exact": pred == truth})
        a = arms.setdefault(r["arm"], {"bits": 0, "trials": 0, "exact": 0})
        a["bits"] += hits; a["trials"] += 1; a["exact"] += int(pred == truth)
    summary = {}
    for arm, a in arms.items():
        n = a["trials"] * BITS
        summary[arm] = {**a, "n_bits": n, "accuracy": a["bits"] / n,
                        "p_one_sided_greater": binom_sf(a["bits"], n),
                        "expected_exact_chance": a["trials"] / 1024}
    passed = [arm for arm, s in summary.items() if s["p_one_sided_greater"] < 0.01]
    out = {"seed_hex": seed.hex(), "resolved_at": datetime.now(timezone.utc).isoformat(),
           "summary": summary,
           "verdict": f"SIGNAL LEAD ({passed}) — replication required" if passed
                      else "NULL — no arm beat chance at alpha 0.01",
           "scored": scored}
    RESOLUTION.write_text(json.dumps(out, indent=2))
    print(json.dumps({k: out[k] for k in ("seed_hex", "summary", "verdict")}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--resolve", action="store_true")
    args = ap.parse_args()
    if args.collect:
        collect()
    elif args.resolve:
        resolve()
    else:
        ap.error("choose --collect or --resolve")
