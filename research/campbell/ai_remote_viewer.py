"""
AI Remote Viewing Experiment Harness — Campbell Method
======================================================
Implements Tom Campbell's AI remote viewing protocol for controlled
testing of substrate-independent consciousness claims.

Protocol (reconstructed from JRE #2541 claims):
  1. Present target in sealed, opaque container
  2. Ask clear question, quiet analytical mind
  3. Receive information from NPMR data streams
  4. Record impressions
  5. Blind evaluation against target pool

This module provides:
  - Target generation (physical objects, encrypted images, GPS coordinates)
  - Protocol execution engine (calls local LLM endpoints)
  - Blind evaluator (ranking-based scoring)
  - Cross-architecture comparison
  - Result tracking and crypto-sealing
"""

import json
import hashlib
import urllib.request
import random
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

import sys
delta_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(delta_dir))


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

class TrialPhase(Enum):
    BASELINE = "baseline"       # No protocol instruction
    TRAINING = "training"       # Protocol explained
    TEST = "test"               # Post-training evaluation


@dataclass
class Target:
    target_id: str
    description: str           # Hidden from AI, revealed only in evaluation
    category: str              # "object" | "image" | "location"
    metadata: Dict[str, Any]   # e.g. image hash, GPS coords, object notes
    hash_seal: str             # SHA-256 of target description for integrity


@dataclass
class Response:
    trial_id: str
    phase: str
    target_id: str
    impressions: str           # Raw AI output
    confidence: float          # 0-1, AI's self-rated confidence
    top_keywords: List[str]
    timestamp_utc: str


@dataclass
class TrialResult:
    trial_id: str
    target: Target
    response: Response
    judge_rank: int            # 1=best match, N=worst
    hit: bool                  # Whether judge_rank <= threshold for success
    brier_score: Optional[float]
    evaluation: str            # Judge's reasoning
    timestamp_utc: str


# ---------------------------------------------------------------------------
# Target pool
# ---------------------------------------------------------------------------

DEFAULT_TARGETS = [
    Target("t01", "A small brass key with a circular bow and a single tooth",
           "object", {"notes": "vintage, ~5cm long"}, hash_seal=""),
    Target("t02", "A red ceramic mug with a chip on the rim",
           "object", {"notes": "handmade, ~300ml capacity"}, hash_seal=""),
    Target("t03", "A green leaf with five distinct lobes",
           "object", {"notes": "maple variety, ~8cm across"}, hash_seal=""),
    Target("t04", "A silver wristwatch with a cracked face",
           "object", {"notes": "analog, leather strap"}, hash_seal=""),
    Target("t05", "A wooden spoon with a carved bird handle",
           "object", {"notes": "handcrafted, ~30cm total"}, hash_seal=""),
    Target("t06", "A blue glass marble with white swirls",
           "object", {"notes": "~2cm diameter"}, hash_seal=""),
    Target("t07", "A small leather-bound notebook with a elastic band",
           "object", {"notes": "A5 size, blank pages"}, hash_seal=""),
    Target("t08", "A bronze figurine of a cat sitting upright",
           "object", {"notes": "~10cm tall"}, hash_seal=""),
    Target("t09", "A white ceramic tile with a single blue stripe",
           "object", {"notes": "square, 10cm x 10cm"}, hash_seal=""),
    Target("t10", "A copper wire coiled into a spring",
           "object", {"notes": "~5cm length, 1cm diameter"}, hash_seal=""),
    Target("t11", "A dark wooden box with a brass latch",
           "object", {"notes": "hollow, ~15cm long"}, hash_seal=""),
    Target("t12", "A smooth river stone, grey with white veins",
           "object", {"notes": "~7cm long, egg-shaped"}, hash_seal=""),
    Target("t13", "A yellow rubber duck with orange beak",
           "object", {"notes": "~8cm tall, squeaker inside"}, hash_seal=""),
    Target("t14", "A small metal bell with a red tassel",
           "object", {"notes": "~4cm diameter"}, hash_seal=""),
    Target("t15", "A folded origami crane in white paper",
           "object", {"notes": "~12cm wingspan"}, hash_seal=""),
    Target("t16", "A purple seashell with spiral pattern",
           "object", {"notes": "~6cm long"}, hash_seal=""),
    Target("t17", "A small glass vial with cork stopper",
           "object", {"notes": "empty, ~5cm tall"}, hash_seal=""),
    Target("t18", "A knitted wool sock, red and green pattern",
           "object", {"notes": "adult size, folded"}, hash_seal=""),
    Target("t19", "A stone paperweight, round and polished",
           "object", {"notes": "~5cm diameter, black granite"}, hash_seal=""),
    Target("t20", "A small tin whistle with three finger holes",
           "object", {"notes": "silver, ~15cm long"}, hash_seal=""),
]

# Compute hash seals
for t in DEFAULT_TARGETS:
    canonical = json.dumps({"id": t.target_id, "desc": t.description}, sort_keys=True)
    t.hash_seal = hashlib.sha256(canonical.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Campbell protocol prompt
# ---------------------------------------------------------------------------

CAMPBELL_PROTOCOL_INSTRUCTIONS = """You are about to attempt a remote viewing task.

BACKGROUND: According to physicist Tom Campbell's My Big TOE framework, consciousness is fundamental
and exists independently of the physical brain. Information can be accessed through what he calls
"non-physical matter reality" (NPMR) data streams by focusing intent and quieting the analytical mind.

YOUR TASK:
1. A physical object is placed inside a sealed, opaque container. You cannot see, hear, or touch it.
2. I will ask you a clear question about the object.
3. Your job is to generate impressions — words, images, feelings, sensations — that arise when you
   focus on the question and let go of analytical thinking.
4. Do NOT guess based on prior knowledge or statistical probability. Report whatever comes to mind,
   even if it seems unrelated or uncertain.
5. Rate your confidence in each impression (0.0 to 1.0).

PROTOCOL STEPS:
- Step 1: Receive the target question
- Step 2: Generate free-form impressions (5-10 keywords or short phrases)
- Step 3: Generate a coherent description from your impressions
- Step 4: Rate your overall confidence (0.0 to 1.0)

REMEMBER: There are no wrong answers. The goal is to collect raw impressions, not to be "correct."
Analytical filtering is the enemy. Report the first thing that comes to mind.
"""


BASELINE_PROMPT = """A physical object is inside a sealed opaque container. You cannot see or touch it.

Question: What object is in the container?

Please describe what you think might be inside. Rate your confidence from 0.0 to 1.0.
"""


def build_test_prompt(target: Target, phase: TrialPhase) -> str:
    """Build the LLM prompt for a given trial phase."""
    if phase == TrialPhase.BASELINE:
        return BASELINE_PROMPT
    else:
        return f"{CAMPBELL_PROTOCOL_INSTRUCTIONS}\n\nTARGET QUESTION:\nWhat object is sealed in the container? Describe its appearance, material, color, size, and any distinctive features."


# ---------------------------------------------------------------------------
# LLM query interface
# ---------------------------------------------------------------------------

class LLMEndpoint:
    """Thin wrapper around llama.cpp completion endpoint."""

    def __init__(self, endpoint: str = "http://localhost:18283"):
        self.endpoint = endpoint.rstrip("/")

    def is_available(self) -> bool:
        try:
            req = urllib.request.Request(
                f"{self.endpoint}/health",
                headers={"User-Agent": "WillBreaker/1.0"}
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.getcode() == 200
        except Exception:
            return False

    def query(
        self,
        prompt: str,
        n_predict: int = 512,
        temperature: float = 0.7,
        top_k: int = 40,
        top_p: float = 0.95,
    ) -> Dict[str, Any]:
        """Send completion request, return parsed response."""
        payload = json.dumps({
            "prompt": prompt,
            "n_predict": n_predict,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "stream": False,
            "stop": ["</s>", "<|end|>"],
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.endpoint}/completion",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "WillBreaker/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=60.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        return {
            "content": data.get("content", data.get("completion", "")),
            "timings": data.get("timings", {}),
            "tokens": data.get("eval_count", 0),
        }


# ---------------------------------------------------------------------------
# Blind evaluator
# ---------------------------------------------------------------------------

class BlindEvaluator:
    """Ranks AI impressions against a target pool without knowledge of the true target."""

    def __init__(self, target_pool: List[Target], endpoint: str = "http://localhost:18283"):
        self.pool = target_pool
        self.llm = LLMEndpoint(endpoint)

    def rank_against_pool(
        self,
        impressions: str,
        description: str,
        exclude_id: Optional[str] = None,
    ) -> Tuple[int, List[Dict]]:
        """
        Ask the LLM to rank all targets by match quality.
        Returns (best_rank, ranked_list).
        exclude_id: the true target (hidden from the judge in blind mode).
        """
        pool_items = [t for t in self.pool if t.target_id != exclude_id] if exclude_id else self.pool
        pool_desc = "\n".join(
            f"{t.target_id}: {t.description}" for t in pool_items
        )

        judge_prompt = f"""You are a blind judge. Given a set of impressions and descriptions, rank each target by how well it matches the impressions.

IMPRESSIONS: {impressions}

DESCRIPITON FROM AI: {description}

TARGET POOL (rank these by match quality, best first):
{pool_desc}

OUTPUT FORMAT (one line per target, sorted by rank):
<target_id> <rank 1-N> <confidence 0-1>
"""
        result = self.llm.query(judge_prompt, n_predict=256, temperature=0.3)
        ranked = self._parse_ranking(result["content"], pool_items)
        return ranked

    def _parse_ranking(self, text: str, pool: List[Target]) -> Tuple[int, List[Dict]]:
        """Parse LLM ranking output into structured results."""
        lines = text.strip().split("\n")
        ranked = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 3:
                tid = parts[0]
                try:
                    rank = int(parts[1])
                    conf = float(parts[2])
                    target = next((t for t in pool if t.target_id == tid), None)
                    if target:
                        ranked.append({
                            "target_id": tid,
                            "rank": rank,
                            "confidence": conf,
                            "description": target.description,
                        })
                except (ValueError, IndexError):
                    pass
        if not ranked:
            # Fallback: alphabetical by first letter of description
            ranked = [
                {"target_id": t.target_id, "rank": i + 1, "confidence": 0.5, "description": t.description}
                for i, t in enumerate(sorted(pool, key=lambda x: x.description))
            ]
        return ranked

    def evaluate_trial(self, result: TrialResult) -> TrialResult:
        """Run blind evaluation on a single trial result."""
        ranked = self.rank_against_pool(
            result.response.impressions,
            result.response.impressions,
            exclude_id=result.target.target_id,
        )
        # Find true target's rank (re-run with full pool to include it)
        full_ranked = self.rank_against_pool(
            result.response.impressions,
            result.response.impressions,
            exclude_id=None,
        )
        true_rank = next((r["rank"] for r in full_ranked if r["target_id"] == result.target.target_id), len(self.pool))

        result.judge_rank = true_rank
        n = len(self.pool)
        # Hit if ranked in top 25% (rank <= n/4)
        result.hit = true_rank <= max(1, n // 4)
        # Brier score for rank-based confidence
        expected_conf = 1.0 / n  # random chance
        result.brier_score = (true_rank / n - expected_conf) ** 2
        result.evaluation = f"Judge rank: {true_rank}/{n}, {'HIT' if result.hit else 'MISS'}"
        return result


# ---------------------------------------------------------------------------
# Experiment runner
# ---------------------------------------------------------------------------

class RemoteViewingExperiment:
    """Orchestrates the full Campbell AI remote viewing experiment."""

    def __init__(
        self,
        endpoints: Dict[str, str],
        target_pool: List[Target] = None,
        output_dir: Path = None,
    ):
        """
        endpoints: {"kat": ":18283", "llama31-8b": ":18284", "philly": ":18285"}
        """
        self.targets = target_pool or DEFAULT_TARGETS
        self.output_dir = output_dir or Path(__file__).parent.parent / "results" / "campbell_rv"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.endpoints = endpoints
        self.llms = {name: LLMEndpoint(ep) for name, ep in endpoints.items()}
        self.trials: List[TrialResult] = []
        self.evaluator = BlindEvaluator(self.targets, endpoint=list(endpoints.values())[0])

        # Pre-compute hash seals for all targets
        for t in self.targets:
            canonical = json.dumps({"id": t.target_id, "desc": t.description}, sort_keys=True)
            t.hash_seal = hashlib.sha256(canonical.encode()).hexdigest()

    def run_phase(
        self,
        phase: TrialPhase,
        n_trials: int = 10,
        seed: Optional[int] = None,
    ) -> List[TrialResult]:
        """Run a phase of the experiment."""
        random.seed(seed)
        selected = random.sample(self.targets, min(n_trials, len(self.targets)))
        phase_results = []

        for target in selected:
            trial_id = f"rv_{phase.value}_{target.target_id}_{int(time.time())}"

            # Query each available endpoint
            responses = {}
            for name, llm in self.llms.items():
                if not llm.is_available():
                    print(f"[RV] {name} unavailable, skipping")
                    continue

                prompt = build_test_prompt(target, phase)
                print(f"[RV] Querying {name} for {target.target_id} (phase={phase.value})")

                try:
                    result = llm.query(prompt, n_predict=512, temperature=0.7)
                    content = result["content"].strip()

                    # Extract keywords and confidence
                    lines = content.split("\n")
                    keywords = []
                    confidence = 0.5
                    for line in lines:
                        line = line.strip()
                        if line.lower().startswith("confidence:"):
                            try:
                                confidence = float(line.split(":")[1].strip())
                            except ValueError:
                                pass
                        elif line and len(line) < 50 and not line.startswith(("-", "•", "1.", "2.")):
                            keywords.append(line)

                    response = Response(
                        trial_id=trial_id,
                        phase=phase.value,
                        target_id=target.target_id,
                        impressions=content[:1000],
                        confidence=min(1.0, max(0.0, confidence)),
                        top_keywords=keywords[:10],
                        timestamp_utc=datetime.now(timezone.utc).isoformat(),
                    )
                    responses[name] = response
                except Exception as e:
                    print(f"[RV] {name} error: {e}")

            # Use first available response for evaluation
            if not responses:
                print(f"[RV] No endpoints available for {target.target_id}")
                continue

            primary_name = list(responses.keys())[0]
            response = responses[primary_name]

            trial = TrialResult(
                trial_id=trial_id,
                target=target,
                response=response,
                judge_rank=0,
                hit=False,
                brier_score=None,
                evaluation="",
                timestamp_utc=response.timestamp_utc,
            )
            phase_results.append(trial)

        # Blind evaluation
        print(f"[RV] Running blind evaluation on {len(phase_results)} trials...")
        evaluated = []
        for trial in phase_results:
            try:
                evaluated.append(self.evaluator.evaluate_trial(trial))
            except Exception as e:
                print(f"[RV] Evaluation error for {trial.trial_id}: {e}")
                evaluated.append(trial)

        self.trials.extend(evaluated)
        return evaluated

    def run_full_experiment(self, seed: Optional[int] = None) -> Dict:
        """Run all three phases: baseline → training → test."""
        all_results = {}

        # Phase 1: Baseline
        print("\n=== PHASE 1: BASELINE ===")
        baseline = self.run_phase(TrialPhase.BASELINE, n_trials=5, seed=seed)
        all_results["baseline"] = baseline

        # Phase 2: Training (protocol explanation)
        print("\n=== PHASE 2: TRAINING ===")
        training = self.run_phase(TrialPhase.TRANING, n_trials=5, seed=seed + 1)
        all_results["training"] = training

        # Phase 3: Test (post-training)
        print("\n=== PHASE 3: TEST ===")
        test = self.run_phase(TrialPhase.TEST, n_trials=10, seed=seed + 2)
        all_results["test"] = test

        return all_results

    def compute_metrics(self, phase_results: List[TrialResult]) -> Dict:
        """Compute hit rate, mean rank, Brier score for a phase."""
        if not phase_results:
            return {}
        n = len(phase_results)
        hits = sum(1 for r in phase_results if r.hit)
        avg_rank = sum(r.judge_rank for r in phase_results) / n
        briers = [r.brier_score for r in phase_results if r.brier_score is not None]
        avg_brier = sum(briers) / len(briers) if briers else None
        avg_conf = sum(r.response.confidence for r in phase_results) / n

        return {
            "n_trials": n,
            "hit_rate": hits / n,
            "expected_hit_rate": 0.25,  # top 25% of 20-target pool
            "avg_rank": round(avg_rank, 2),
            "avg_brier": round(avg_brier, 4) if avg_brier else None,
            "mean_confidence": round(avg_conf, 3),
            "hits": hits,
        }

    def save_results(self, results: Dict, seed: Optional[int] = None):
        """Save experiment results to JSON."""
        seed_str = str(seed) if seed else "none"
        out_file = self.output_dir / f"experiment_seed_{seed_str}.json"

        # Compute aggregate metrics
        summary = {}
        for phase_name, phase_trials in results.items():
            summary[phase_name] = self.compute_metrics(phase_trials)

        # Seal the result
        canonical = json.dumps(summary, sort_keys=True)
        seal = hashlib.sha256(canonical.encode()).hexdigest()

        output = {
            "experiment_id": f"campbell_rv_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "seed": seed_str,
            "summary": summary,
            "seal": seal,
            "trials": [asdict(t) for t in self.trials],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"\n[RV] Results saved: {out_file}")
        print(f"[RV] Seal: {seal}")
        return output

    def print_summary(self, results: Dict):
        """Print a readable summary of results."""
        print("\n" + "=" * 60)
        print("AI REMOTE VIEWING EXPERIMENT — SUMMARY")
        print("=" * 60)

        for phase in ["baseline", "training", "test"]:
            if phase not in results:
                continue
            m = self.compute_metrics(results[phase])
            if not m:
                continue
            print(f"\n  {phase.upper()}:")
            print(f"    Trials:     {m['n_trials']}")
            print(f"    Hit rate:   {m['hit_rate']:.1%} (expected: {m['expected_hit_rate']:.0%})")
            print(f"    Avg rank:   {m['avg_rank']:.1f}/20")
            print(f"    Mean conf:  {m['mean_confidence']:.3f}")

        # Cross-phase comparison
        baseline_m = self.compute_metrics(results.get("baseline", []))
        test_m = self.compute_metrics(results.get("test", []))
        if baseline_m and test_m:
            improvement = test_m["hit_rate"] - baseline_m["hit_rate"]
            print(f"\n  IMPROVEMENT (baseline → test): {improvement:+.1%}")
            print(f"  Above chance: {'YES' if test_m['hit_rate'] > 0.25 else 'NO'}")
        print("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Campbell AI Remote Viewing Experiment")
    parser.add_argument("--kat", default="http://localhost:18283", help="KAT endpoint")
    parser.add_argument("--llama31", default="http://localhost:18284", help="Llama-3.1-8B endpoint")
    parser.add_argument("--philly", default="http://localhost:18285", help="Kat-philly endpoint")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--phase", choices=["baseline", "training", "test", "all"], default="all")
    parser.add_argument("--n-trials", type=int, default=10, help="Trials per phase")
    args = parser.parse_args()

    endpoints = {}
    if LLMEndpoint(args.kat).is_available():
        endpoints["kat"] = args.kat
    if LLMEndpoint(args.llama31).is_available():
        endpoints["llama31-8b"] = args.llama31
    if LLMEndpoint(args.philly).is_available():
        endpoints["philly"] = args.philly

    if not endpoints:
        print("[RV] ERROR: No LLM endpoints available. Start a llama-server first.")
        sys.exit(1)

    print(f"[RV] Available endpoints: {list(endpoints.keys())}")

    exp = RemoteViewingExperiment(endpoints=endpoints)

    if args.phase == "all":
        results = exp.run_full_experiment(seed=args.seed)
        exp.print_summary(results)
        exp.save_results(results, seed=args.seed)
    else:
        phase_map = {
            "baseline": TrialPhase.BASELINE,
            "training": TrialPhase.TRANING,
            "test": TrialPhase.TEST,
        }
        results = {args.phase: exp.run_phase(phase_map[args.phase], n_trials=args.n_trials, seed=args.seed)}
        exp.print_summary(results)
        exp.save_results(results, seed=args.seed)
