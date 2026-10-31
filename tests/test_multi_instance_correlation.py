"""Unit tests for Multi-Instance Correlation Instrument (Protocol C.3 / Candidate I-B)."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from research.benchmarks.multi_instance_correlation import (
    MultiInstanceRunner,
    cosine_similarity,
    format_markdown_summary,
    jaccard_similarity,
)


class TestVectorMetrics:
    """Test mathematical correctness of vector and set comparison functions."""

    def test_cosine_similarity_identical(self):
        v1 = [1.0, 2.0, 3.0]
        assert pytest.approx(cosine_similarity(v1, v1), rel=1e-5) == 1.0

    def test_cosine_similarity_orthogonal(self):
        v1 = [1.0, 0.0]
        v2 = [0.0, 1.0]
        assert pytest.approx(cosine_similarity(v1, v2), abs=1e-5) == 0.0

    def test_cosine_similarity_empty_or_zero(self):
        assert cosine_similarity([], []) == 0.0
        assert cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0

    def test_jaccard_similarity(self):
        t1 = ["token_a", "token_b", "token_c"]
        t2 = ["token_b", "token_c", "token_d"]
        # Intersection: {b, c} = 2, Union: {a, b, c, d} = 4 -> 2/4 = 0.5
        assert pytest.approx(jaccard_similarity(t1, t2), rel=1e-5) == 0.5

    def test_jaccard_similarity_empty(self):
        assert jaccard_similarity([], []) == 1.0


class TestMultiInstanceRunner:
    """Test runner execution, isolation, and metric calculation with mocked fetcher."""

    def _mock_fetcher(self, prompt, seed):
        """Simulate LLM logprobs response."""
        return {
            "choices": [
                {
                    "message": {"content": f"State vector for seed {seed}"},
                    "logprobs": {
                        "content": [
                            {
                                "token": "State",
                                "logprob": -0.2,
                                "top_logprobs": [{"logprob": -0.2}, {"logprob": -1.8}],
                            },
                            {
                                "token": "vector",
                                "logprob": -0.1,
                                "top_logprobs": [{"logprob": -0.1}, {"logprob": -2.3}],
                            },
                        ]
                    },
                }
            ]
        }

    def test_runner_mock_execution(self):
        runner = MultiInstanceRunner(
            endpoint="http://mock:18284/v1",
            model="mock-wb-agent",
            n_instances=2,
            depths=3,
            arms=("A", "D"),
            fetcher=self._mock_fetcher,
        )
        res = runner.execute_battery()

        assert res["protocol"] == "021-multi-instance-correlation"
        assert res["n_instances"] == 2
        assert res["depths"] == 3
        assert "A" in res["arm_results"]
        assert "D" in res["arm_results"]
        assert len(res["arm_results"]["A"]) == 2

        analysis = res["analysis"]
        assert "A" in analysis["arms"]
        a_metrics = analysis["arms"]["A"]
        assert a_metrics["n_valid_instances"] == 2
        assert a_metrics["mean_pairwise_trajectory_cosine"] > 0.0
        assert "cross_arm_null_cosine_A_vs_D" in analysis

    def test_format_markdown_summary(self):
        mock_payload = {
            "protocol": "021-multi-instance-correlation",
            "model": "wb-agent",
            "endpoint": "http://127.0.0.1:18284/v1",
            "n_instances": 3,
            "depths": 5,
            "arms": ("A", "D"),
            "timestamp_utc": "2026-10-30T12:00:00Z",
            "analysis": {
                "arms": {
                    "A": {
                        "n_valid_instances": 3,
                        "mean_pairwise_trajectory_cosine": 0.9421,
                        "mean_pairwise_final_jaccard": 0.1250,
                    },
                    "D": {
                        "n_valid_instances": 3,
                        "mean_pairwise_trajectory_cosine": 0.8120,
                        "mean_pairwise_final_jaccard": 0.0500,
                    },
                },
                "cross_arm_null_cosine_A_vs_D": 0.4512,
                "attractor_convergence_confirmed": True,
            },
        }
        md = format_markdown_summary(mock_payload)
        assert "# Protocol 021 Verdict" in md
        assert "0.9421" in md
        assert "MET" in md
