"""
Sports Prediction Resolution Engine — Will Breaker Validator
Evaluates cryptographically sealed NFL and NBA predictions against official box scores,
computing Brier Score, Brier Skill Score, Log Loss, and Calibration Error.
"""

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))

from will_breaker_delta.validator.crypto_predictor import CryptoPredictor


class SportsResolver:
    """Resolves sports commitments against game box scores."""

    def __init__(self, registry_file: Optional[Path] = None):
        self.predictor = CryptoPredictor(registry_file=registry_file)

    @staticmethod
    def evaluate_box_score(
        game_meta: Dict[str, Any],
        away_score: int,
        home_score: int,
    ) -> Dict[str, str]:
        """
        Evaluate official final score to determine winning Moneyline and ATS pick.
        """
        away_team = game_meta["away_team"]
        home_team = game_meta["home_team"]
        market_spread = game_meta["market_spread"] # e.g. "Bengals -2.5" or "Bills -3.0"
        
        # 1. Moneyline Winner
        if away_score > home_score:
            ml_winner = away_team
        elif home_score > away_score:
            ml_winner = home_team
        else:
            ml_winner = "PUSH_TIE"

        # 2. ATS Spread Winner
        parts = market_spread.split()
        fav_team = " ".join(parts[:-1])
        spread_val_raw = parts[-1]
        spread_val = float(spread_val_raw) # e.g. -2.5
        spread_abs_str = spread_val_raw.replace("-", "").replace("+", "")

        fav_is_home = (fav_team.lower() in home_team.lower()) or (home_team.lower() in fav_team.lower())

        if fav_is_home:
            # Home team is favored: home_score + spread_val vs away_score
            adjusted_home = home_score + spread_val
            if adjusted_home > away_score:
                ats_winner = f"{home_team} -{spread_abs_str}"
            elif adjusted_home < away_score:
                ats_winner = f"{away_team} +{spread_abs_str}"
            else:
                ats_winner = "PUSH"
        else:
            # Away team is favored: away_score + spread_val vs home_score
            adjusted_away = away_score + spread_val
            if adjusted_away > home_score:
                ats_winner = f"{away_team} -{spread_abs_str}"
            elif adjusted_away < home_score:
                ats_winner = f"{home_team} +{spread_abs_str}"
            else:
                ats_winner = "PUSH"

        return {
            "ml_winner": ml_winner,
            "ats_winner": ats_winner,
            "final_score": f"{away_team} {away_score} - {home_team} {home_score}",
        }

    def resolve_slate(
        self,
        slate_json_path: Path,
        box_scores: Dict[str, Dict[str, int]],
        session_id: str = "041",
    ) -> Dict[str, Any]:
        """
        Resolve all sealed commitments from the slate against ground truth box scores.
        box_scores format: { game_id: {"away_score": X, "home_score": Y} }
        """
        with open(slate_json_path, "r", encoding="utf-8") as f:
            slate_data = json.load(f)

        forecasts = slate_data.get("forecasts", [])
        records = self.predictor.load_all_commitments()
        commitments_by_id = {r["commitment_id"]: r for r in records}

        resolutions = []
        ats_hits = 0
        ats_total = 0
        ml_hits = 0
        ml_total = 0
        brier_scores = []
        log_losses = []

        for f_item in forecasts:
            gid = f_item["game_id"]
            if gid not in box_scores:
                continue

            score = box_scores[gid]
            outcomes = self.evaluate_box_score(f_item, score["away_score"], score["home_score"])

            # Resolve ATS Commitment
            ats_cid = f_item["ats_commitment_id"]
            if ats_cid and ats_cid in commitments_by_id:
                pred_rec = commitments_by_id[ats_cid]
                pred_pick = pred_rec["prediction"]["predicted_outcome"]
                pred_prob = float(pred_rec["prediction"]["probability"])

                is_correct = (pred_pick.lower().strip() == outcomes["ats_winner"].lower().strip())
                bs = (pred_prob - 1.0) ** 2 if is_correct else (pred_prob - 0.0) ** 2
                prob_clamped = max(0.001, min(0.999, pred_prob))
                ll = -math.log(prob_clamped) if is_correct else -math.log(1.0 - prob_clamped)

                self.predictor.resolve_prediction(
                    commitment_id=ats_cid,
                    actual_outcome=outcomes["ats_winner"],
                    resolution_notes=f"Box Score: {outcomes['final_score']} (Winner ATS: {outcomes['ats_winner']})"
                )

                ats_total += 1
                if is_correct:
                    ats_hits += 1
                brier_scores.append(bs)
                log_losses.append(ll)

                resolutions.append({
                    "commitment_id": ats_cid,
                    "game_id": gid,
                    "type": "ATS",
                    "predicted": pred_pick,
                    "actual": outcomes["ats_winner"],
                    "is_correct": is_correct,
                    "probability": pred_prob,
                    "brier_score": round(bs, 4),
                })

            # Resolve ML Commitment
            ml_cid = f_item["ml_commitment_id"]
            if ml_cid and ml_cid in commitments_by_id:
                pred_rec = commitments_by_id[ml_cid]
                pred_pick = pred_rec["prediction"]["predicted_outcome"]
                pred_prob = float(pred_rec["prediction"]["probability"])

                is_correct = (pred_pick.lower().strip() == outcomes["ml_winner"].lower().strip())
                bs = (pred_prob - 1.0) ** 2 if is_correct else (pred_prob - 0.0) ** 2
                prob_clamped = max(0.001, min(0.999, pred_prob))
                ll = -math.log(prob_clamped) if is_correct else -math.log(1.0 - prob_clamped)

                self.predictor.resolve_prediction(
                    commitment_id=ml_cid,
                    actual_outcome=outcomes["ml_winner"],
                    resolution_notes=f"Box Score: {outcomes['final_score']} (Winner ML: {outcomes['ml_winner']})"
                )

                ml_total += 1
                if is_correct:
                    ml_hits += 1
                brier_scores.append(bs)
                log_losses.append(ll)

                resolutions.append({
                    "commitment_id": ml_cid,
                    "game_id": gid,
                    "type": "ML",
                    "predicted": pred_pick,
                    "actual": outcomes["ml_winner"],
                    "is_correct": is_correct,
                    "probability": pred_prob,
                    "brier_score": round(bs, 4),
                })

        mean_bs = sum(brier_scores) / len(brier_scores) if brier_scores else None
        mean_ll = sum(log_losses) / len(log_losses) if log_losses else None
        # Chance benchmark for binary choice with p=0.5: BS_ref = 0.250
        bss = 1.0 - (mean_bs / 0.250) if mean_bs is not None else None

        summary = {
            "session_id": session_id,
            "resolved_at_utc": datetime.now(timezone.utc).isoformat(),
            "games_resolved": len(box_scores),
            "total_commitments_resolved": len(resolutions),
            "ats_hit_rate": round(ats_hits / ats_total, 4) if ats_total else 0.0,
            "ats_record": f"{ats_hits}-{ats_total - ats_hits}",
            "ml_hit_rate": round(ml_hits / ml_total, 4) if ml_total else 0.0,
            "ml_record": f"{ml_hits}-{ml_total - ml_hits}",
            "overall_accuracy": round((ats_hits + ml_hits) / len(resolutions), 4) if resolutions else 0.0,
            "mean_brier_score": round(mean_bs, 4) if mean_bs is not None else None,
            "brier_skill_score": round(bss, 4) if bss is not None else None,
            "mean_log_loss": round(mean_ll, 4) if mean_ll is not None else None,
            "resolutions": resolutions,
        }

        return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Will Breaker Sports Resolution Engine")
    parser.add_argument("--status", action="store_true", help="List all sealed sports commitments")
    parser.add_argument("--scores", type=str, help="JSON dictionary of game_id -> [away_score, home_score]")
    parser.add_argument("--scores-file", type=str, help="Path to JSON file containing box scores")
    parser.add_argument("--session", type=str, default="041", help="Session ID to resolve (default: 041)")
    args = parser.parse_args()

    resolver = SportsResolver()

    if args.status or (not args.scores and not args.scores_file):
        print(f"=== WILL BREAKER SPORTS PREDICTIONS: SESSION {args.session} ===")
        all_records = resolver.predictor.load_all_commitments()
        unresolved = [
            r for r in all_records
            if r.get("status") == "SEALED" and r.get("prediction", {}).get("session_id") == args.session
        ]
        print(f"Total Sealed Commitments: {len(unresolved)}")
        for r in unresolved:
            p = r.get("prediction", {})
            print(f"  [{r['commitment_id']}] {p.get('event_description')}")
            print(f"    Pick: {p.get('predicted_outcome')} (p={p.get('probability')}) | Seal: {r['sha256_seal'][:12]}...")

    if args.scores or args.scores_file:
        box_scores = {}
        if args.scores:
            box_scores.update(json.loads(args.scores))
        if args.scores_file:
            with open(args.scores_file, "r", encoding="utf-8") as f:
                box_scores.update(json.load(f))

        print(f"\nResolving {len(box_scores)} game(s) for Session {args.session}...")
        summary = resolver.resolve_battery(box_scores, session_id=args.session)
        print(f"Games Resolved: {summary['games_resolved']}")
        print(f"ATS Record: {summary['ats_record']} ({summary['ats_hit_rate'] * 100:.1f}%)")
        print(f"Moneyline Record: {summary['ml_record']} ({summary['ml_hit_rate'] * 100:.1f}%)")
        print(f"Overall Accuracy: {summary['overall_accuracy'] * 100:.1f}%")
        print(f"Mean Brier Score: {summary['mean_brier_score']}")
        print(f"Brier Skill Score (BSS): {summary['brier_skill_score']}")
