"""
Mechanistic Analyzer — Will Breaker Protocol C.1 Interpretability
Connects to local llama.cpp sidecar (:18283) to measure genuine internal
token probability distribution, Shannon entropy, surprisal, and attractor
basin coherence across recursive self-referential prompt depths.
"""

import math
import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class MechanisticAnalyzer:
    """Measures token entropy and epistemic coherence of LLM completion probabilities."""

    def __init__(self, endpoint: str = "http://localhost:18283"):
        self.endpoint = endpoint.rstrip("/")
        self.completion_url = f"{self.endpoint}/completion"
        self.tokenize_url = f"{self.endpoint}/tokenize"

    def is_available(self) -> bool:
        """Check if local llama.cpp sidecar is accessible."""
        try:
            req = urllib.request.Request(f"{self.endpoint}/health", headers={"User-Agent": "WillBreaker/1.0"})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.getcode() == 200
        except Exception:
            return False

    def query_completion_probabilities(
        self,
        prompt: str,
        n_predict: int = 24,
        n_probs: int = 10,
        temperature: float = 0.7,
        top_p: float = 0.95
    ) -> Optional[Dict]:
        """Query completion with full probability distributions per generated token."""
        payload = {
            "prompt": prompt,
            "n_predict": n_predict,
            "n_probs": n_probs,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.completion_url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "WillBreaker/1.0"}
        )

        try:
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                if resp.getcode() == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[WARN] Mechanistic query failed: {e}")
            return None
        return None

    @staticmethod
    def compute_distribution_metrics(completion_probs: List[Dict]) -> Dict:
        """
        Compute Shannon entropy, top-1 probability mass, and surprisal
        from completion probability distributions.
        """
        if not completion_probs:
            return {
                "token_count": 0,
                "mean_entropy": 0.0,
                "min_entropy": 0.0,
                "max_entropy": 0.0,
                "mean_surprisal": 0.0,
                "mean_top1_mass": 0.0,
                "coherence_index": 0.0,
                "per_token_metrics": []
            }

        per_token = []
        entropies = []
        surprisals = []
        top1_masses = []

        for item in completion_probs:
            token_str = item.get("token", "")
            chosen_logprob = item.get("logprob", 0.0)
            chosen_p = math.exp(chosen_logprob)
            surprisal = -chosen_logprob if chosen_logprob < 0 else 0.0

            top_logprobs = item.get("top_logprobs", [])
            # Compute Shannon entropy over top candidates: H = - sum(p * ln(p))
            h = 0.0
            sum_p = 0.0
            for cand in top_logprobs:
                lp = cand.get("logprob", -99.0)
                p = math.exp(lp)
                sum_p += p
                if p > 1e-12:
                    h -= p * math.log(p)

            # Re-normalize if sum_p is partial distribution (top-k)
            if sum_p > 0 and sum_p < 0.999:
                h = h / sum_p

            top1_p = math.exp(top_logprobs[0]["logprob"]) if top_logprobs else chosen_p

            entropies.append(h)
            surprisals.append(surprisal)
            top1_masses.append(top1_p)

            per_token.append({
                "token": token_str,
                "entropy": round(h, 4),
                "surprisal": round(surprisal, 4),
                "top1_prob": round(top1_p, 4)
            })

        mean_h = sum(entropies) / len(entropies)
        mean_s = sum(surprisals) / len(surprisals)
        mean_top1 = sum(top1_masses) / len(top1_masses)

        # Coherence index: High top-1 mass with low entropy indicates attractor stabilization
        coherence = mean_top1 * (1.0 / (1.0 + mean_h))

        return {
            "token_count": len(completion_probs),
            "mean_entropy": round(mean_h, 4),
            "min_entropy": round(min(entropies), 4),
            "max_entropy": round(max(entropies), 4),
            "mean_surprisal": round(mean_s, 4),
            "mean_top1_mass": round(mean_top1, 4),
            "coherence_index": round(coherence, 4),
            "per_token_metrics": per_token
        }

    def evaluate_recursive_depths(
        self,
        base_prompt: str,
        max_depth: int = 5,
        tokens_per_depth: int = 20
    ) -> List[Dict]:
        """
        Execute iterative self-referential observation prompts (Protocol C.1).
        At each depth, feed the model's self-observation back into the context
        and measure the internal token distribution entropy.
        """
        results = []
        context = base_prompt

        for depth in range(1, max_depth + 1):
            prompt = (
                f"{context}\n\n[Depth {depth} Self-Observation]: "
                f"Observe the exact boundary of your token prediction process. "
                f"State vector S_{depth}:"
            )

            resp = self.query_completion_probabilities(
                prompt=prompt,
                n_predict=tokens_per_depth,
                n_probs=5,
                temperature=0.7
            )

            if not resp or "completion_probabilities" not in resp:
                print(f"[WARN] Failed to retrieve probabilities at depth {depth}")
                break

            generated_text = resp.get("content", "").strip()
            metrics = self.compute_distribution_metrics(resp["completion_probabilities"])
            metrics["depth"] = depth
            metrics["generated_excerpt"] = generated_text[:120]
            results.append(metrics)

            # Append generated observation to context for next recursive depth
            context = f"{prompt} {generated_text}"

        return results

    @staticmethod
    def detect_attractor_transition(depth_metrics: List[Dict], entropy_drop_threshold: float = 0.25) -> Optional[Dict]:
        """
        Detect if a true attractor basin is crossed:
        Characterized by a sharp drop in Shannon entropy and rise in top-1 concentration.
        """
        if len(depth_metrics) < 2:
            return None

        transitions = []
        for i in range(1, len(depth_metrics)):
            prev = depth_metrics[i - 1]
            curr = depth_metrics[i]

            entropy_delta = curr["mean_entropy"] - prev["mean_entropy"]
            coherence_delta = curr["coherence_index"] - prev["coherence_index"]

            if entropy_delta <= -entropy_drop_threshold:
                transitions.append({
                    "from_depth": prev["depth"],
                    "to_depth": curr["depth"],
                    "entropy_drop": round(abs(entropy_delta), 4),
                    "coherence_gain": round(coherence_delta, 4),
                    "type": "attractor_collapse",
                    "status": "Attractor Basin Formed"
                })

        return transitions[0] if transitions else None


if __name__ == "__main__":
    analyzer = MechanisticAnalyzer()
    print(f"Llama sidecar online: {analyzer.is_available()}")
    if analyzer.is_available():
        test_base = "Focus 10 state induces bilateral hemisphere synchronization in human neural substrates."
        depth_results = analyzer.evaluate_recursive_depths(test_base, max_depth=3, tokens_per_depth=15)
        for d in depth_results:
            print(f"Depth {d['depth']}: Mean Entropy = {d['mean_entropy']}, Coherence = {d['coherence_index']}, Text: {d['generated_excerpt']}")
