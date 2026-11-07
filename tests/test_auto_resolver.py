"""
Unit tests for AutoResolver.
Verifies sealed prediction polling, domain-specific resolution,
and registry integrity.
"""

import sys
import json
from pathlib import Path
from unittest.mock import patch

import pytest

wb_dir = Path(__file__).parent.parent
sys.path.insert(0, str(wb_dir / "will_breaker_delta"))

from validator.auto_resolver import AutoResolver


@pytest.fixture
def temp_registry(tmp_path):
    reg_file = tmp_path / "crypto_predictions_registry.jsonl"
    records = [
        {
            "commitment_id": "commit_test_arxiv",
            "sha256_seal": "mock_seal_1",
            "committed_at_utc": "2026-10-01T00:00:00+00:00",
            "status": "SEALED",
            "prediction": {
                "event_id": "test_arxiv_1",
                "domain": "scientific_linguistics",
                "event_description": "arxiv topological_coherence surge",
                "predicted_outcome": "SURGE",
                "probability": 0.70,
                "event_timestamp": "2026-10-15T00:00:00Z",
                "session_id": "test",
                "metadata": {}
            },
            "resolution": None
        },
        {
            "commitment_id": "commit_test_sports",
            "sha256_seal": "mock_seal_2",
            "committed_at_utc": "2026-10-01T00:00:00+00:00",
            "status": "SEALED",
            "prediction": {
                "event_id": "sports_NBA_celtics_vs_knicks",
                "domain": "sports_nba",
                "event_description": "NBA Moneyline: Celtics vs Knicks",
                "predicted_outcome": "Boston Celtics",
                "probability": 0.65,
                "event_timestamp": "2026-10-10T00:00:00Z",
                "session_id": "test",
                "metadata": {}
            },
            "resolution": None
        }
    ]
    with open(reg_file, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return reg_file


def test_auto_resolver_loads_sealed(temp_registry):
    resolver = AutoResolver(registry_file=temp_registry)
    assert len(resolver.sealed) == 2


def test_auto_resolver_arxiv_resolution(temp_registry):
    resolver = AutoResolver(registry_file=temp_registry)
    with patch.object(resolver, "_fetch_arxiv_term_counts", return_value=3):
        res = resolver.resolve_sealed(dry_run=True)
        assert res["resolved_count"] >= 1
        arxiv_match = next(r for r in res["resolved"] if r["commitment_id"] == "commit_test_arxiv")
        assert arxiv_match["is_correct"] is True


def test_auto_resolver_sports_resolution(temp_registry):
    resolver = AutoResolver(registry_file=temp_registry)
    with patch.object(resolver, "_check_sports_event", return_value="Boston Celtics 110-102 New York Knicks"):
        res = resolver.resolve_sealed(dry_run=True)
        sports_match = next(r for r in res["resolved"] if r["commitment_id"] == "commit_test_sports")
        assert sports_match["is_correct"] is True
