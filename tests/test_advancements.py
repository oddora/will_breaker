"""
Unit Tests for Will Breaker Advancements:
1. Mechanistic Analyzer (entropy & attractor transition)
2. Crypto Predictor (SHA-256 pre-commitments, verification, Brier scoring)
3. Live Crawler Pipeline
"""

import math
import unittest
from pathlib import Path
import tempfile
import json

wb_dir = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(wb_dir / "will_breaker_delta"))

from analyzer.mechanistic_analyzer import MechanisticAnalyzer
from validator.crypto_predictor import CryptoPredictor
from validator.prediction_resolver import PredictionResolver
from scraper.live_crawler import LiveCrawlerPipeline


class TestMechanisticAnalyzer(unittest.TestCase):
    def test_compute_distribution_metrics(self):
        sample_probs = [
            {
                "token": "quantum",
                "logprob": -0.223,
                "top_logprobs": [
                    {"token": "quantum", "logprob": -0.223},
                    {"token": "classical", "logprob": -1.897},
                    {"token": "system", "logprob": -2.525}
                ]
            },
            {
                "token": "state",
                "logprob": -0.051,
                "top_logprobs": [
                    {"token": "state", "logprob": -0.051},
                    {"token": "system", "logprob": -3.218}
                ]
            }
        ]
        metrics = MechanisticAnalyzer.compute_distribution_metrics(sample_probs)
        self.assertEqual(metrics["token_count"], 2)
        self.assertGreater(metrics["mean_entropy"], 0.0)
        self.assertGreater(metrics["mean_top1_mass"], 0.5)
        self.assertGreater(metrics["coherence_index"], 0.0)

    def test_detect_attractor_transition(self):
        depth_metrics = [
            {"depth": 1, "mean_entropy": 1.65, "coherence_index": 0.20},
            {"depth": 2, "mean_entropy": 0.35, "coherence_index": 0.78}  # drop of 1.30
        ]
        transition = MechanisticAnalyzer.detect_attractor_transition(depth_metrics, entropy_drop_threshold=0.5)
        self.assertIsNotNone(transition)
        self.assertEqual(transition["from_depth"], 1)
        self.assertEqual(transition["to_depth"], 2)
        self.assertEqual(transition["type"], "attractor_collapse")


class TestCryptoPredictor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.reg_file = Path(self.temp_dir.name) / "test_registry.jsonl"
        self.predictor = CryptoPredictor(registry_file=self.reg_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_commit_and_integrity_verification(self):
        record = self.predictor.commit_prediction(
            event_id="test_event_1",
            domain="sports",
            event_description="Team A vs Team B",
            predicted_outcome="Team A -3.5",
            probability=0.70,
            event_timestamp="2026-10-25T18:00:00Z"
        )
        self.assertEqual(record["status"], "SEALED")
        self.assertTrue(self.predictor.verify_commitment_integrity(record))

        # Tampering detection
        tampered_record = dict(record)
        tampered_record["prediction"] = dict(record["prediction"])
        tampered_record["prediction"]["probability"] = 0.99
        self.assertFalse(self.predictor.verify_commitment_integrity(tampered_record))

    def test_resolution_and_brier_scoring(self):
        rec = self.predictor.commit_prediction(
            event_id="event_resolve_test",
            domain="finance",
            event_description="Asset X close > $100",
            predicted_outcome="YES",
            probability=0.80,
            event_timestamp="2026-10-25T20:00:00Z"
        )
        cid = rec["commitment_id"]
        resolved = self.predictor.resolve_prediction(cid, actual_outcome="YES")
        self.assertEqual(resolved["status"], "RESOLVED")
        self.assertTrue(resolved["resolution"]["is_correct"])
        # Brier score for p=0.80 and outcome=1: (0.80 - 1.0)^2 = 0.04
        self.assertAlmostEqual(resolved["resolution"]["brier_score"], 0.04, places=3)

        perf = self.predictor.evaluate_performance()
        self.assertEqual(perf["resolved_count"], 1)
        self.assertEqual(perf["accuracy"], 1.0)
        self.assertAlmostEqual(perf["mean_brier_score"], 0.04, places=3)


class TestPredictionResolver(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.reg_file = Path(self.temp_dir.name) / "test_registry.jsonl"
        self.resolver = PredictionResolver(registry_file=self.reg_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_batch_resolution_and_calibration(self):
        # Commit two predictions
        p1 = self.resolver.predictor.commit_prediction(
            event_id="e1", domain="test", event_description="d1",
            predicted_outcome="WIN", probability=0.70, event_timestamp="2026-10-25T00:00:00Z"
        )
        p2 = self.resolver.predictor.commit_prediction(
            event_id="e2", domain="test", event_description="d2",
            predicted_outcome="WIN", probability=0.60, event_timestamp="2026-10-25T00:00:00Z"
        )

        # Resolve e1 as WIN (correct) and e2 as LOSS (incorrect)
        outcomes = {"e1": "WIN", "e2": "LOSS"}
        metrics = self.resolver.resolve_batch(outcomes)

        self.assertEqual(metrics["resolved_count"], 2)
        self.assertEqual(metrics["correct_count"], 1)
        self.assertEqual(metrics["accuracy"], 0.5)
        self.assertIsNotNone(metrics["mean_brier_score"])
        self.assertIsNotNone(metrics["brier_skill_score"])
        self.assertIsNotNone(metrics["log_loss"])
        self.assertGreater(len(metrics["calibration"]), 0)


class TestLiveCrawler(unittest.TestCase):
    def test_run_cycle_with_documents(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = LiveCrawlerPipeline()
            pipeline.output_forecast_file = Path(tmpdir) / "latest_forecast.json"
            pipeline.output_events_file = Path(tmpdir) / "delta_events.jsonl"
            mock_docs = [
                {
                    "title": "Quantum Attractor Basin Collapse in Deep Recursion",
                    "content": "Recursive self-referential observation demonstrates phase transition and metric deformation.",
                    "source": "test_mock"
                }
            ]
            result = pipeline.run_cycle(documents=mock_docs)
            self.assertIn("forecasts", result)
            self.assertIn("documents_analyzed", result)
            self.assertEqual(result["documents_analyzed"], 1)


if __name__ == "__main__":
    unittest.main()
