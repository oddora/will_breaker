"""Unit tests for SearXNGCollector and PrecursorDeltaEngine (Protocol 020 / Candidate I-E)."""

import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from will_breaker_delta.scraper.searxng_collector import SearXNGCollector
from will_breaker_delta.analyzer.precursor_delta_engine import PrecursorDeltaEngine


class TestSearXNGCollector:
    """Test SearXNG query parsing, filtering, and error handling."""

    def test_init_default_domains(self):
        collector = SearXNGCollector()
        assert "geopolitical" in collector.DEFAULT_DOMAINS
        assert "financial" in collector.DEFAULT_DOMAINS
        assert "geophysical" in collector.DEFAULT_DOMAINS
        assert "scientific_anomaly" in collector.DEFAULT_DOMAINS

    @patch("urllib.request.urlopen")
    def test_search_domain_success(self, mock_urlopen):
        mock_resp = MagicMock()
        payload = {
            "results": [
                {
                    "title": "Severe Seismic Activity Detected",
                    "content": "A magnitude 6.2 earthquake occurred along the tectonic plate boundary today.",
                    "url": "https://example.com/quake",
                    "publishedDate": "2026-10-30T12:00:00Z",
                    "engine": "duckduckgo",
                },
                {
                    "title": "Short",
                    "content": "Too short.",
                    "url": "https://example.com/short",
                },
            ]
        }
        mock_resp.read.return_value = json.dumps(payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        collector = SearXNGCollector()
        docs = collector.search_domain("geophysical", "earthquake test")
        # Second item is filtered out (<30 chars)
        assert len(docs) == 1
        assert docs[0]["domain"] == "geophysical"
        assert docs[0]["source"] == "searxng"
        assert "magnitude 6.2 earthquake" in docs[0]["text"]

    @patch("urllib.request.urlopen")
    def test_search_domain_failure_fails_gracefully(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection refused on :18080")
        collector = SearXNGCollector()
        docs = collector.search_domain("financial", "banking crisis")
        assert docs == []


@pytest.fixture(scope="module")
def engine():
    return PrecursorDeltaEngine(tag="test_engine_tag")


class TestPrecursorDeltaEngine:
    """Test PrecursorDeltaEngine baseline scoring, wb-agent synthesis, and cryptographic sealing."""

    def test_engine_initialization(self, engine):
        assert engine.tag == "test_engine_tag"
        assert engine.context_model is not None
        assert engine.lexicon is not None
        assert engine.scorer is not None

    @patch("urllib.request.urlopen")
    def test_query_wb_agent_clean_json(self, mock_urlopen, engine):
        expected_forecast = {
            "event_id": "financial_test",
            "domain": "financial",
            "anomalous_precursors": ["liquidity"],
            "predicted_hypothesis": "Liquidity contraction in interbank markets",
            "falsifiable_criterion": "Repo rates exceed policy rate by > 50 bps",
            "target_window_days": 14,
            "confidence_probability": 0.82,
        }
        mock_resp = MagicMock()
        llm_reply = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(expected_forecast),
                    }
                }
            ]
        }
        mock_resp.read.return_value = json.dumps(llm_reply).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        delta_words = [{"word": "liquidity", "anomaly_score": 1.45, "valence": -0.3, "emotions": ["fear"], "count": 3}]
        result = engine.query_wb_agent("financial", 10, delta_words)
        assert result == expected_forecast

    @patch("urllib.request.urlopen")
    def test_query_wb_agent_handles_markdown_fence(self, mock_urlopen, engine):
        forecast = {
            "event_id": "geophysical_test",
            "domain": "geophysical",
            "anomalous_precursors": ["earthquake"],
            "predicted_hypothesis": "Seismic cluster in subduction zone",
            "falsifiable_criterion": "USGS records >= 3 M5.0+ events in target zone",
            "target_window_days": 14,
            "confidence_probability": 0.70,
        }
        fenced_content = f"```json\n{json.dumps(forecast)}\n```"
        mock_resp = MagicMock()
        llm_reply = {"choices": [{"message": {"content": fenced_content}}]}
        mock_resp.read.return_value = json.dumps(llm_reply).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        delta_words = [{"word": "earthquake", "anomaly_score": 1.2, "valence": -0.4, "emotions": ["fear"], "count": 2}]
        result = engine.query_wb_agent("geophysical", 5, delta_words)
        assert result == forecast

    def test_analyze_domain_scoring(self, engine):
        mock_docs = [
            {"text": "Severe escalation in conflict and military escalation tensions across the border."},
            {"text": "The military escalation continues with severe casualties and missile strikes."},
        ]
        with patch.object(engine, "query_wb_agent", return_value={"mock": "forecast"}):
            deltas, forecast = engine.analyze_domain("geopolitical", mock_docs)
            assert isinstance(deltas, list)
            assert forecast == {"mock": "forecast"}
            # "escalation" should appear as a recurring candidate
            words = [d["word"] for d in deltas]
            assert "escalation" in words or "military" in words or len(deltas) > 0

    def test_session050_seal_verification(self):
        """Verify that the published Session 050 seal matches the payload SHA-256 exactly."""
        seal_path = project_root / "results" / "delta_forecasts" / "session050_delta_seal.json"
        if not seal_path.exists():
            pytest.skip("session050_delta_seal.json not found")

        with open(seal_path, "r", encoding="utf-8") as f:
            seal_data = json.load(f)

        published_seal = seal_data["sha256_seal"]
        payload = seal_data["payload"]

        # Canonical bytes reproduction
        canonical_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        computed_sha = hashlib.sha256(canonical_bytes).hexdigest()

        assert computed_sha == published_seal, "Cryptographic seal integrity mismatch for Session 050"
        assert seal_data["n_forecasts"] == 4
        assert seal_data["status"] == "SEALED_PRE_COMMITMENT"
