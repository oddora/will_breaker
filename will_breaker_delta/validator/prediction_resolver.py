"""
Prediction Resolution Engine — Will Breaker Validator
Evaluates cryptographically sealed predictions against ground-truth outcomes,
computing Brier Score, Brier Skill Score, Log Loss, and Calibration Error.
"""

import json
import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from validator.crypto_predictor import CryptoPredictor


class PredictionResolver:
    """Resolves sealed predictions and computes strict probabilistic skill metrics."""

    def __init__(self, registry_file: Path = None):
        self.predictor = CryptoPredictor(registry_file=registry_file)

    def resolve_batch(self, outcomes_map: Dict[str, str], notes_prefix: str = "Ground truth verification") -> Dict:
        """
        Resolve multiple predictions by event_id or commitment_id.
        outcomes_map: {commitment_id_or_event_id: outcome_value}
        e.g., {"sports_NCAA Football_Alabama_vs_Ole_Miss": "Alabama -10.5"} (win)
        or {"sports_NCAA Football_Alabama_vs_Ole_Miss": "Ole Miss +10.5"} (loss)
        """
        records = self.predictor.load_all_commitments()
        resolved_count = 0

        for rec in records:
            cid = rec["commitment_id"]
            eid = rec["prediction"]["event_id"]
            outcome = outcomes_map.get(cid) or outcomes_map.get(eid)

            if outcome is not None:
                self.predictor.resolve_prediction(
                    commitment_id=cid,
                    actual_outcome=outcome,
                    resolution_notes=f"{notes_prefix}: Verified against official recorded result."
                )
                resolved_count += 1

        perf = self.compute_advanced_metrics()
        return perf

    def compute_advanced_metrics(self) -> Dict:
        """Compute Brier Score, Brier Skill Score, Log Loss, and Decile Calibration."""
        records = self.predictor.load_all_commitments()
        resolved = [r for r in records if r.get("status") == "RESOLVED" and r.get("resolution")]

        if not resolved:
            return {
                "total_records": len(records),
                "resolved_count": 0,
                "pending_count": len(records),
                "accuracy": 0.0,
                "mean_brier_score": None,
                "brier_skill_score": None,
                "log_loss": None,
                "calibration_deciles": []
            }

        correct_count = 0
        brier_sum = 0.0
        log_loss_sum = 0.0

        # Calibration bins: [0.5, 0.6), [0.6, 0.7), [0.7, 0.8), [0.8, 0.9), [0.9, 1.0]
        bins = {
            "0.5-0.6": {"preds": [], "actuals": []},
            "0.6-0.7": {"preds": [], "actuals": []},
            "0.7-0.8": {"preds": [], "actuals": []},
            "0.8-0.9": {"preds": [], "actuals": []},
            "0.9-1.0": {"preds": [], "actuals": []}
        }

        for r in resolved:
            prob = r["prediction"]["probability"]
            is_correct = r["resolution"]["is_correct"]
            y = 1.0 if is_correct else 0.0

            if is_correct:
                correct_count += 1

            # Brier score: (p - y)^2
            brier_sum += (prob - y) ** 2

            # Log loss with epsilon clamping
            p_clamped = min(max(prob, 1e-6), 1.0 - 1e-6)
            log_loss_sum += -(y * math.log(p_clamped) + (1.0 - y) * math.log(1.0 - p_clamped))

            # Binning for calibration
            if 0.5 <= prob < 0.6:
                bins["0.5-0.6"]["preds"].append(prob)
                bins["0.5-0.6"]["actuals"].append(y)
            elif 0.6 <= prob < 0.7:
                bins["0.6-0.7"]["preds"].append(prob)
                bins["0.6-0.7"]["actuals"].append(y)
            elif 0.7 <= prob < 0.8:
                bins["0.7-0.8"]["preds"].append(prob)
                bins["0.7-0.8"]["actuals"].append(y)
            elif 0.8 <= prob < 0.9:
                bins["0.8-0.9"]["preds"].append(prob)
                bins["0.8-0.9"]["actuals"].append(y)
            else:
                bins["0.9-1.0"]["preds"].append(prob)
                bins["0.9-1.0"]["actuals"].append(y)

        n = len(resolved)
        accuracy = correct_count / n
        mean_brier = brier_sum / n
        # Reference Brier score for uninformed coin flip: (0.5 - 1)^2 = 0.25
        bss = 1.0 - (mean_brier / 0.25)
        mean_log_loss = log_loss_sum / n

        calibration = []
        for b_name, b_data in bins.items():
            if b_data["preds"]:
                mean_conf = sum(b_data["preds"]) / len(b_data["preds"])
                emp_acc = sum(b_data["actuals"]) / len(b_data["actuals"])
                calibration.append({
                    "bin": b_name,
                    "count": len(b_data["preds"]),
                    "mean_confidence": round(mean_conf, 4),
                    "empirical_accuracy": round(emp_acc, 4),
                    "calibration_error": round(abs(mean_conf - emp_acc), 4)
                })

        return {
            "total_records": len(records),
            "resolved_count": n,
            "pending_count": len(records) - n,
            "correct_count": correct_count,
            "accuracy": round(accuracy, 4),
            "mean_brier_score": round(mean_brier, 4),
            "brier_skill_score": round(bss, 4),
            "log_loss": round(mean_log_loss, 4),
            "calibration": calibration
        }


if __name__ == "__main__":
    resolver = PredictionResolver()
    metrics = resolver.compute_advanced_metrics()
    print("Initial prediction metrics:", metrics)
