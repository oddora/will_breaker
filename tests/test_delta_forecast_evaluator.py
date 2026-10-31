"""Unit tests for DeltaForecastEvaluator — Will Breaker Protocol 020."""

import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import sys

# Ensure will_breaker root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from will_breaker_delta.validator.delta_forecast_evaluator import DeltaForecastEvaluator


@pytest.fixture
def evaluator():
    return DeltaForecastEvaluator()


def test_verify_seal_valid(tmp_path):
    import hashlib
    payload = {"test": 123, "forecasts": [{"event_id": "test_1"}]}
    canonical_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    seal = hashlib.sha256(canonical_bytes).hexdigest()

    seal_file = tmp_path / "test_seal.json"
    seal_file.write_text(json.dumps({"sha256_seal": seal, "payload": payload}))

    is_valid, data = DeltaForecastEvaluator.verify_seal(seal_file)
    assert is_valid is True
    assert data["sha256_seal"] == seal


def test_verify_seal_tampered(tmp_path):
    payload = {"test": 123}
    seal_file = tmp_path / "tampered_seal.json"
    seal_file.write_text(json.dumps({"sha256_seal": "bad_hash_value", "payload": payload}))

    is_valid, data = DeltaForecastEvaluator.verify_seal(seal_file)
    assert is_valid is False


def test_verify_seal_missing():
    is_valid, data = DeltaForecastEvaluator.verify_seal(Path("/nonexistent/seal.json"))
    assert is_valid is False
    assert data is None


def test_compute_window_status():
    start = datetime(2026, 10, 1, 0, 0, 0, tzinfo=timezone.utc).isoformat()

    # Midway through window
    now_mid = datetime(2026, 10, 8, 0, 0, 0, tzinfo=timezone.utc)
    status_mid = DeltaForecastEvaluator.compute_window_status(start, window_days=14, now_dt=now_mid)
    assert status_mid["is_window_closed"] is False
    assert status_mid["elapsed_days"] == 7.0
    assert status_mid["remaining_days"] == 7.0

    # Past window
    now_past = datetime(2026, 10, 16, 0, 0, 0, tzinfo=timezone.utc)
    status_past = DeltaForecastEvaluator.compute_window_status(start, window_days=14, now_dt=now_past)
    assert status_past["is_window_closed"] is True
    assert status_past["elapsed_days"] == 15.0
    assert status_past["remaining_days"] == 0.0


def test_calculate_probabilistic_metrics():
    # Empty
    res_empty = DeltaForecastEvaluator.calculate_probabilistic_metrics([])
    assert res_empty["n_resolved"] == 0
    assert res_empty["mean_brier_score"] is None

    # Two resolved forecasts:
    # 1) prob=0.8, outcome=1.0 -> (0.8 - 1.0)^2 = 0.04
    # 2) prob=0.6, outcome=0.0 -> (0.6 - 0.0)^2 = 0.36
    # mean BS = (0.04 + 0.36) / 2 = 0.20
    # ref (climatology 0.5): (0.5 - 1)^2 = 0.25, (0.5 - 0)^2 = 0.25 -> mean = 0.25
    # BSS = 1 - (0.20 / 0.25) = 1 - 0.8 = 0.20
    forecasts = [
        {"confidence_probability": 0.80, "resolved_outcome": 1.0},
        {"confidence_probability": 0.60, "resolved_outcome": 0.0},
        {"confidence_probability": 0.70, "resolved_outcome": None},  # unresolved
    ]
    metrics = DeltaForecastEvaluator.calculate_probabilistic_metrics(forecasts, reference_climatology=0.50)
    assert metrics["n_resolved"] == 2
    assert metrics["mean_brier_score"] == 0.20
    assert metrics["reference_brier_score"] == 0.25
    assert metrics["brier_skill_score"] == 0.20
    assert metrics["mean_log_loss"] is not None


def test_evaluate_geopolitical(evaluator):
    with patch.object(evaluator, "query_searxng") as mock_searx:
        mock_searx.return_value = [
            {"title": "No progress in negotiations", "content": "Tensions remain high with Iran."}
        ]
        res = evaluator.evaluate_geopolitical({})
        assert res["falsification_condition_met"] is False

        mock_searx.return_value = [
            {"title": "Peace accord", "content": "Both nations signed ceasefire agreement today."}
        ]
        res_ceasefire = evaluator.evaluate_geopolitical({})
        assert res_ceasefire["falsification_condition_met"] is True


def test_evaluate_geophysical(evaluator):
    with patch.object(evaluator, "query_usgs_earthquakes") as mock_usgs:
        # 2 events occurred
        mock_usgs.return_value = [
            {"place": "Vanuatu", "mag": 5.1, "time_epoch_ms": 1793400000000},
            {"place": "Peru", "mag": 4.6, "time_epoch_ms": 1793405000000},
        ]
        res = evaluator.evaluate_geophysical({}, "2026-10-29T00:00:00+00:00")
        assert res["event_count_mag_ge_4_5"] == 2
        # Condition was "catalog shows zero events" -> zero events is False
        assert res["falsification_condition_met"] is False

        # 0 events occurred
        mock_usgs.return_value = []
        res_zero = evaluator.evaluate_geophysical({}, "2026-10-29T00:00:00+00:00")
        assert res_zero["event_count_mag_ge_4_5"] == 0
        assert res_zero["falsification_condition_met"] is True


def test_evaluate_session_simulated(tmp_path, monkeypatch):
    import will_breaker_delta.validator.delta_forecast_evaluator as dfe_mod
    monkeypatch.setattr(dfe_mod, "RESULTS_DIR", tmp_path)

    payload = {
        "tag": "test_sess",
        "timestamp_utc": "2026-10-20T00:00:00+00:00",
        "forecasts": [
            {
                "event_id": "geo_test",
                "domain": "geopolitical",
                "confidence_probability": 0.75,
                "falsifiable_criterion": "ceasefire signed",
            }
        ],
    }
    canonical_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    import hashlib
    seal = hashlib.sha256(canonical_bytes).hexdigest()

    seal_file = tmp_path / "test_sess_delta_seal.json"
    seal_file.write_text(json.dumps({
        "sha256_seal": seal,
        "collected_at": payload["timestamp_utc"],
        "resolution_window_days": 14,
        "payload": payload
    }))

    evaluator = DeltaForecastEvaluator()
    with patch.object(evaluator, "query_searxng", return_value=[]):
        # Simulate simulated outcome = 1.0 (confirmed)
        res = evaluator.evaluate_session("test_sess", simulated_outcomes={"geo_test": 1.0})
        assert res["is_seal_valid"] is True
        assert res["metrics"]["n_resolved"] == 1
        assert res["metrics"]["mean_brier_score"] == round((0.75 - 1.0) ** 2, 4)
