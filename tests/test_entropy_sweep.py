"""
Verification Suite for Entropy & Attractor Hyperparameter Sweep
Tests entropy calculation, logprob parsing, coherence index, and report generation.
"""

import math
import unittest
import tempfile
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from research.benchmarks.entropy_hyperparameter_sweep import (
    EntropyHyperparameterSweep,
    TokenEntropyStep,
    SweepTrialResult,
)


class TestEntropySweep(unittest.TestCase):
    def test_compute_step_entropy_deterministic(self):
        """Verify that a 100% certain token produces 0 entropy and 1.0 coherence."""
        top_lp = [
            {"token": "the", "logprob": 0.0},
            {"token": "a", "logprob": -50.0},
        ]
        res = EntropyHyperparameterSweep.compute_step_entropy(top_lp)
        self.assertAlmostEqual(res["entropy"], 0.0, places=3)
        self.assertAlmostEqual(res["top1_prob"], 1.0, places=3)
        self.assertAlmostEqual(res["coherence"], 1.0, places=3)

    def test_compute_step_entropy_uniform(self):
        """Verify that uniform distribution across 2 tokens produces ln(2) ~ 0.6931 entropy."""
        top_lp = [
            {"token": "A", "logprob": -0.693147},
            {"token": "B", "logprob": -0.693147},
        ]
        res = EntropyHyperparameterSweep.compute_step_entropy(top_lp)
        self.assertAlmostEqual(res["entropy"], math.log(2), places=3)
        self.assertAlmostEqual(res["top1_prob"], 0.5, places=3)
        expected_coherence = 0.5 / (1.0 + math.log(2))
        self.assertAlmostEqual(res["coherence"], expected_coherence, places=3)

    def test_generate_markdown_report_structure(self):
        """Verify markdown report generation correctly tabulates results."""
        trial = SweepTrialResult(
            mode="recursive_self_obs",
            temperature=0.2,
            prompt="Observe...",
            generated_text="The invariant holds.",
            token_count=5,
            mean_entropy=0.15,
            min_entropy=0.01,
            max_entropy=0.25,
            mean_coherence=0.85,
            steps=[
                TokenEntropyStep("The", -0.01, 0.99, 0.05, 0.94),
            ],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "test_report.md"
            content = EntropyHyperparameterSweep.generate_markdown_report([trial], out_file)
            self.assertTrue(out_file.exists())
            self.assertIn("COLLAPSED BASIN", content)
            self.assertIn("recursive_self_obs", content)
            self.assertIn("0.1500", content)


if __name__ == "__main__":
    unittest.main()
