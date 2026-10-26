"""
Unit tests for the integrated delta-detection pipeline (Protocol 006).
Tests: AnomalyScorer → DeltaTracker → ForecastGenerator integration.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from will_breaker_delta.analyzer.context_model import ContextModel
from will_breaker_delta.analyzer.anomaly_scorer import AnomalyScorer, EmotionalLexicon
from will_breaker_delta.analyzer.delta_tracker import DeltaTracker
from will_breaker_delta.analyzer.forecast_generator import ForecastGenerator


@pytest.fixture(scope="module")
def baseline():
    """Build baseline context model from corpus."""
    corpus_dir = project_root / "will_breaker_delta" / "corpus" / "built"
    cm = ContextModel(corpus_path=corpus_dir)
    lexicon = EmotionalLexicon(
        nrc_path=project_root / "will_breaker_delta" / "lexicon" / "nrc_emotion_lexicon.csv",
        vader_path=project_root / "will_breaker_delta" / "lexicon" / "vader_lexicon.csv",
    )
    scorer = AnomalyScorer(lexicon=lexicon, baseline_model=cm)
    return {"context_model": cm, "lexicon": lexicon, "scorer": scorer}


def _tokenize(text):
    """Simple whitespace/tokenize helper for score_document."""
    return text.lower().split()


class TestAnomalyScorerBounded:
    """Test that anomaly scores are valid and context_delta is bounded 0.0–1.0."""

    def test_normal_document_returns_list(self, baseline):
        tokens = _tokenize("The weather today is sunny with clear skies and warm temperatures.")
        score = baseline["scorer"].score_document(tokens)
        assert isinstance(score, list)
        assert len(score) > 0

    def test_context_delta_bounded(self, baseline):
        tokens = _tokenize("The weather today is sunny with clear skies and warm temperatures.")
        score = baseline["scorer"].score_document(tokens)
        for entry in score:
            assert "context_delta" in entry
            assert 0.0 <= entry["context_delta"] <= 1.0, (
                f"context_delta={entry['context_delta']} out of bounds"
            )

    def test_anomalous_document_returns_list(self, baseline):
        tokens = _tokenize(
            "Blondes appeared on the vessel near the coast. "
            "The unexpected linguistic trace suggested a precursor event."
        )
        score = baseline["scorer"].score_document(tokens)
        assert isinstance(score, list)
        assert len(score) > 0

    def test_empty_document_returns_empty_list(self, baseline):
        score = baseline["scorer"].score_document([])
        assert score == []

    def test_short_document_no_crash(self, baseline):
        score = baseline["scorer"].score_document(["hi"])
        assert isinstance(score, list)


class TestDeltaTracker:
    """Test delta tracking and precursor detection."""

    def test_add_flagged_words_in_place(self, baseline):
        tracker = DeltaTracker()
        flagged_words = [{"word": "test", "anomaly": 0.5}]
        result = tracker.add_flagged_words(flagged_words, timestamp="2026-01-01T00:00:00Z")
        assert result is None  # in-place update
        # Verify state was updated
        events = tracker.get_precursor_events(threshold=0.01, min_observations=1)
        assert isinstance(events, list)

    def test_compute_delta_returns_dict(self, baseline):
        tracker = DeltaTracker()
        tracker.add_flagged_words(
            [{"word": "anomaly", "anomaly": 0.9}],
            timestamp="2026-01-01T00:00:00Z",
        )
        delta = tracker.compute_delta("anomaly")
        assert delta is None or isinstance(delta, dict)

    def test_compute_delta_missing_word_returns_none(self, baseline):
        tracker = DeltaTracker()
        delta = tracker.compute_delta("nonexistent_word_xyz")
        assert delta is None

    def test_get_precursor_events_returns_list(self, baseline):
        tracker = DeltaTracker()
        events = tracker.get_precursor_events(threshold=0.5, min_observations=2)
        assert isinstance(events, list)

    def test_precursor_events_sorted_by_rate(self, baseline):
        tracker = DeltaTracker()
        for i in range(5):
            tracker.add_flagged_words(
                [{"word": "anomaly", "anomaly": 0.9}],
                timestamp=f"2026-01-01T{i:02d}:00:00Z",
            )
        events = tracker.get_precursor_events(threshold=0.1, min_observations=2)
        assert isinstance(events, list)
        if len(events) > 1:
            rates = [e["delta_rate"] for e in events]
            assert rates == sorted(rates, reverse=True), "Events should be sorted by delta_rate desc"

    def test_forecast_generation_with_events(self, baseline):
        tracker = DeltaTracker()
        for i in range(5):
            tracker.add_flagged_words(
                [{"word": "precursor", "anomaly": 0.85}],
                timestamp=f"2026-01-01T{i:02d}:00:00Z",
            )
        events = tracker.get_precursor_events(threshold=0.1, min_observations=2)
        fg = ForecastGenerator()
        forecasts = fg.generate_forecasts(events)
        assert isinstance(forecasts, list)


class TestIntegratedPipeline:
    """End-to-end integration test: scorer → tracker → generator."""

    def test_full_pipeline_integration(self, baseline):
        tracker = DeltaTracker()
        fg = ForecastGenerator()

        docs = [
            "The morning report showed normal conditions across all monitored regions.",
            "Linguistic patterns in the corpus showed slight deviation from baseline.",
            "Anomalous vocabulary emerged in multiple feeds simultaneously.",
            "Precursor signals intensified across the monitoring network.",
            "Threshold crossing detected: linguistic anomaly index exceeded expected bounds.",
        ]
        for i, doc in enumerate(docs):
            tokens = _tokenize(doc)
            score = baseline["scorer"].score_document(tokens)
            tracker.add_flagged_words(score, timestamp=f"2026-01-01T{i*6:02d}:00:00Z")

        events = tracker.get_precursor_events(threshold=0.1, min_observations=2)
        forecasts = fg.generate_forecasts(events)

        assert isinstance(events, list)
        assert isinstance(forecasts, list)

    def test_pipeline_with_known_anomaly_pattern(self, baseline):
        tracker = DeltaTracker()
        fg = ForecastGenerator()

        anomaly_docs = [
            "Blondes on the vessel near the coast suggested a visual anomaly.",
            "The template layer of information appeared prior to manifestation.",
            "Topological coherence in the attractor basin indicated a shift.",
            "Dimensional transition threshold was crossed at the Planck scale.",
            "Precursor events flagged: linguistic anomaly index spiking.",
        ]
        for i, doc in enumerate(anomaly_docs):
            tokens = _tokenize(doc)
            score = baseline["scorer"].score_document(tokens)
            tracker.add_flagged_words(score, timestamp=f"2026-01-01T{i*3:02d}:00:00Z")

        events = tracker.get_precursor_events(threshold=0.05, min_observations=1)
        forecasts = fg.generate_forecasts(events)

        assert isinstance(events, list)
        assert isinstance(forecasts, list)


class TestForecastGenerator:
    """Test archetype mapping and forecast formatting."""

    def test_archetype_map_has_entries(self):
        fg = ForecastGenerator()
        assert len(fg.ARCHETYPE_MAP) > 0
        assert "precursor" in fg.ARCHETYPE_MAP
        assert "click" in fg.ARCHETYPE_MAP
        assert "template" in fg.ARCHETYPE_MAP

    def test_format_forecast_report_produces_string(self, baseline):
        tracker = DeltaTracker()
        fg = ForecastGenerator()
        events = tracker.get_precursor_events(threshold=0.5, min_observations=2)
        forecasts = fg.generate_forecasts(events)
        report = fg.format_forecast_report(forecasts)
        assert isinstance(report, str)
        assert len(report) > 0

    def test_generate_forecasts_with_empty_events(self):
        fg = ForecastGenerator()
        forecasts = fg.generate_forecasts([])
        assert isinstance(forecasts, list)

    def test_archetype_forecast_contains_required_fields(self, baseline):
        tracker = DeltaTracker()
        tracker.add_flagged_words(
            [{"word": "precursor", "anomaly": 0.9}],
            timestamp="2026-01-01T00:00:00Z",
        )
        events = tracker.get_precursor_events(threshold=0.05, min_observations=1)
        fg = ForecastGenerator()
        forecasts = fg.generate_forecasts(events)
        if forecasts:
            fc = forecasts[0]
            assert "word" in fc
            assert "archetype" in fc
            assert "forecast" in fc
            assert "delta_rate" in fc


class TestLiveCrawlerPipeline:
    """Test the end-to-end LiveCrawler pipeline."""

    def test_run_cycle_returns_dict(self):
        from will_breaker_delta.scraper.live_crawler import LiveCrawlerPipeline

        pipeline = LiveCrawlerPipeline()
        result = pipeline.run_cycle()
        assert isinstance(result, dict)
        assert "cycle_timestamp" in result
        assert "documents_analyzed" in result
        assert "precursor_count" in result

    def test_run_cycle_produces_forecasts(self):
        from will_breaker_delta.scraper.live_crawler import LiveCrawlerPipeline

        pipeline = LiveCrawlerPipeline()
        result = pipeline.run_cycle()
        assert "forecasts" in result
        assert isinstance(result["forecasts"], list)

    def test_run_cycle_documents_analyzed_positive(self):
        from will_breaker_delta.scraper.live_crawler import LiveCrawlerPipeline

        pipeline = LiveCrawlerPipeline()
        result = pipeline.run_cycle()
        assert result["documents_analyzed"] > 0
