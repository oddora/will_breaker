"""
Verification Suite for KAT Sports Forecasting Battery & Resolution Engine
Tests game slate ingestion, prompt JSON extraction, box score evaluation,
cryptographic sealing, and metric computation (Brier Score, BSS, Log Loss).
"""

import sys
import unittest
import tempfile
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from research.sports.kat_sports_battery import (
    KATSportsBattery,
    GameMatchup,
    ModelForecast,
    OCT_25_SLATE,
)
from research.sports.resolve_sports_battery import SportsResolver
from will_breaker_delta.validator.crypto_predictor import CryptoPredictor


class TestSportsBattery(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.reg_path = Path(self.temp_dir.name) / "test_crypto_registry.jsonl"
        self.battery = KATSportsBattery(registry_file=self.reg_path)
        self.resolver = SportsResolver(registry_file=self.reg_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_slate_composition(self):
        """Verify the slate contains 4 NFL and 7 NBA upcoming games for Oct 25, 2026."""
        self.assertEqual(len(OCT_25_SLATE), 11)
        nfl = [g for g in OCT_25_SLATE if g.sport == "NFL"]
        nba = [g for g in OCT_25_SLATE if g.sport == "NBA"]
        self.assertEqual(len(nfl), 4)
        self.assertEqual(len(nba), 7)

        for g in OCT_25_SLATE:
            self.assertTrue(g.game_id.startswith(("nfl_", "nba_")))
            self.assertIn("-", g.market_spread)
            self.assertGreater(g.market_total, 30.0)

    def test_json_extraction_sanitization(self):
        """Verify markdown code blocks and thinking tags are cleanly stripped."""
        raw_output = """<think>
Evaluating matchup Dallas @ SF...
</think>
```json
{
  "moneyline_pick": "San Francisco 49ers",
  "moneyline_prob": 0.65,
  "spread_pick": "Dallas Cowboys +4.5",
  "spread_prob": 0.54,
  "total_pick": "UNDER 46.5",
  "total_prob": 0.52,
  "rationale": "Tight division battle with clock grinding."
}
```"""
        parsed = self.battery._extract_json(raw_output)
        self.assertEqual(parsed["moneyline_pick"], "San Francisco 49ers")
        self.assertEqual(parsed["spread_pick"], "Dallas Cowboys +4.5")
        self.assertEqual(parsed["moneyline_prob"], 0.65)

    def test_box_score_evaluation(self):
        """Verify box score evaluator correctly determines ML and ATS winners."""
        game_meta = {
            "away_team": "Philadelphia Eagles",
            "home_team": "Cincinnati Bengals",
            "market_spread": "Bengals -2.5",
        }
        # Case 1: Away team wins outright -> covers +2.5
        res1 = self.resolver.evaluate_box_score(game_meta, away_score=37, home_score=17)
        self.assertEqual(res1["ml_winner"], "Philadelphia Eagles")
        self.assertEqual(res1["ats_winner"], "Philadelphia Eagles +2.5")

        # Case 2: Home team wins by 7 -> covers -2.5
        res2 = self.resolver.evaluate_box_score(game_meta, away_score=20, home_score=27)
        self.assertEqual(res2["ml_winner"], "Cincinnati Bengals")
        self.assertEqual(res2["ats_winner"], "Cincinnati Bengals -2.5")

        # Case 3: Home team wins by 1 -> does NOT cover -2.5 (Eagles cover +2.5)
        res3 = self.resolver.evaluate_box_score(game_meta, away_score=20, home_score=21)
        self.assertEqual(res3["ml_winner"], "Cincinnati Bengals")
        self.assertEqual(res3["ats_winner"], "Philadelphia Eagles +2.5")

    def test_end_to_end_sealing_and_resolution(self):
        """Verify end-to-end flow: commit predictions, seal with SHA-256, resolve with box scores."""
        game = GameMatchup(
            game_id="nfl_test_game_01",
            sport="NFL",
            away_team="Buffalo Bills",
            home_team="Seattle Seahawks",
            venue="Lumen Field",
            market_spread="Bills -3.0",
            market_total=46.5,
            kickoff_utc="2026-10-25T20:05:00Z",
        )

        forecasts = self.battery.run_slate_forecasts([game], session_id="test_041")
        self.assertEqual(len(forecasts), 1)
        f = forecasts[0]
        self.assertIsNotNone(f.ats_commitment_id)
        self.assertIsNotNone(f.ml_commitment_id)
        self.assertIsNotNone(f.ats_sha256_seal)
        self.assertIsNotNone(f.ml_sha256_seal)

        # Verify registry file was populated with 2 records
        records = self.battery.predictor.load_all_commitments()
        self.assertEqual(len(records), 2)
        for r in records:
            self.assertEqual(r["status"], "SEALED")
            self.assertEqual(len(r["sha256_seal"]), 64)

        # Export test slate
        json_out, md_out = self.battery.export_sealed_ledger(forecasts, Path(self.temp_dir.name), session_id="test_041")
        self.assertTrue(json_out.exists())
        self.assertTrue(md_out.exists())

        # Resolve with box score: Bills 31, Seahawks 10 (Bills win by 21, cover -3.0)
        box_scores = {
            "nfl_test_game_01": {"away_score": 31, "home_score": 10}
        }
        res = self.resolver.resolve_slate(json_out, box_scores, session_id="test_041")
        self.assertEqual(res["games_resolved"], 1)
        self.assertEqual(res["total_commitments_resolved"], 2)
        self.assertIn("mean_brier_score", res)
        self.assertIn("brier_skill_score", res)


if __name__ == "__main__":
    unittest.main()
