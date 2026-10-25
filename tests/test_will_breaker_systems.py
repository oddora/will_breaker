"""
Comprehensive Verification Test Suite for Will Breaker Systems Code
Tests all components across analyzer, scraper, validator, and UI data flow.
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime, timedelta

# Add paths
wb_dir = Path(__file__).parent.parent
sys.path.insert(0, str(wb_dir / 'will_breaker_delta'))

from analyzer.anomaly_scorer import (
    EmotionalLexicon, BaselineContextModel, AnomalyScorer, tokenize, load_lexicons
)
from analyzer.context_model import ContextModel
from analyzer.delta_tracker import DeltaTracker
from analyzer.forecast_generator import ForecastGenerator
from validator.shift_report_parser import ShiftReportParser
from validator.experiment_correlator import ExperimentCorrelator
from scraper.corpus_builder import CorpusBuilder
from scraper.collect_all import count_docs_in_file


class TestAnomalyScorer(unittest.TestCase):
    def setUp(self):
        base_dir = wb_dir / 'will_breaker_delta'
        self.lexicon = load_lexicons(
            base_dir / 'lexicon' / 'nrc_emotion_lexicon.csv',
            base_dir / 'lexicon' / 'vader_lexicon.csv',
            base_dir / 'config' / 'lexicon_weights.yaml'
        )
        self.baseline = BaselineContextModel()
        sample_corpus = [
            "Consciousness transcends spacetime through coherent brainwave states.",
            "The planck distance represents the threshold between time-space and non-time-space.",
            "The template layer of information exists prior to manifestation.",
            "Attractor basins stabilize recursive self-reference at depth thresholds."
        ]
        for s in sample_corpus:
            self.baseline.add_document(s)
        self.scorer = AnomalyScorer(self.lexicon, self.baseline)

    def test_unseen_word_no_crash(self):
        """Verify unseen words do not crash with TypeError (previously float object not subscriptable)."""
        doc = "completely_novel_pseudoword observed near coastline"
        flagged = self.scorer.score_document(doc, threshold=0.1)
        self.assertIsInstance(flagged, list)
        self.assertTrue(any(f['word'] == 'completely_novel_pseudoword' for f in flagged))
        target = next(f for f in flagged if f['word'] == 'completely_novel_pseudoword')
        self.assertIn('anomaly', target)
        self.assertIn('context_delta', target)
        self.assertGreater(target['anomaly'], 0)

    def test_custom_lexicon_weights_loaded(self):
        """Verify custom weights from lexicon_weights.yaml are applied."""
        self.assertIn('ejecta', self.lexicon.custom_weights)
        weight_ejecta = self.lexicon.get_emotional_weight('ejecta')
        self.assertGreater(weight_ejecta, 0.5)

    def test_context_delta_bounded(self):
        """Verify context delta is properly bounded between 0 and 1."""
        doc = "Consciousness transcends spacetime through coherent brainwave states."
        flagged = self.scorer.score_document(doc, threshold=0.0)
        for f in flagged:
            self.assertGreaterEqual(f['context_delta'], 0.0)
            self.assertLessEqual(f['context_delta'], 1.0)


class TestDeltaTrackerAndForecast(unittest.TestCase):
    def setUp(self):
        self.tracker = DeltaTracker()

    def test_rate_calculation_not_clamped(self):
        """Verify sub-hour intervals do not clamp to 1 hour."""
        t0 = datetime(2026, 10, 24, 10, 0, 0)
        t1 = datetime(2026, 10, 24, 10, 30, 0)  # 0.5 hours
        self.tracker.add_flagged_words([{'word': 'ejecta', 'anomaly': 2.0}], timestamp=t0)
        self.tracker.add_flagged_words([{'word': 'ejecta', 'anomaly': 4.0}], timestamp=t1)
        
        delta = self.tracker.compute_delta('ejecta')
        self.assertIsNotNone(delta)
        self.assertAlmostEqual(delta['time_delta_hours'], 0.5, places=2)
        # 2.0 anomaly change in 0.5 hours -> rate = 4.0/hr
        self.assertAlmostEqual(delta['delta_rate'], 4.0, places=1)
        self.assertIn('timestamp', delta)

    def test_forecast_generator(self):
        """Verify forecast generation and non-negative projections."""
        gen = ForecastGenerator()
        events = [
            {'word': 'clickout', 'last_anomaly': 3.0, 'delta_rate': 0.05, 'observations': 5, 'timestamp': '2026-10-24T10:00:00'},
            {'word': 'ejecta', 'last_anomaly': 1.0, 'delta_rate': -0.1, 'observations': 5, 'timestamp': '2026-10-24T10:00:00'}
        ]
        forecasts = gen.generate_forecasts(events, horizon_hours=24)
        self.assertEqual(len(forecasts), 2)
        # clickout projected = 3.0 + 0.05*24 = 4.2
        self.assertAlmostEqual(forecasts[0]['projected_anomaly'], 4.2, places=1)
        # ejecta projected = max(0, 1.0 - 0.1*24) = 0.0
        self.assertGreaterEqual(forecasts[1]['projected_anomaly'], 0.0)


class TestShiftReportParserAndCorrelator(unittest.TestCase):
    def test_parser_finds_all_sessions(self):
        """Verify parser extracts state vectors from sessions including subscript S₀, S₂ notation."""
        sessions_dir = wb_dir / 'sessions'
        parser = ShiftReportParser(sessions_dir)
        reports = parser.parse_all_reports()
        flat = parser.get_flat_reports()
        
        self.assertGreaterEqual(len(reports), 25, "Should parse at least 25 session files")
        self.assertGreaterEqual(len(flat), 80, "Should extract at least 80 state vectors")
        
        # Verify dates are extracted
        for r in flat[:10]:
            self.assertIsNotNone(r['date'], f"Date should not be None for {r['id']}")

    def test_correlator_runs_cleanly(self):
        """Verify experiment correlator computes both overlap and temporal correlations."""
        sessions_dir = wb_dir / 'sessions'
        built_dir = wb_dir / 'will_breaker_delta' / 'corpus' / 'built'
        correlator = ExperimentCorrelator(sessions_dir, built_dir)
        
        correlations = correlator.correlate(window_days=7)
        self.assertIsInstance(correlations, list)
        self.assertGreater(len(correlations), 0, "Temporal correlations should be detected")


class TestCorpusBuilder(unittest.TestCase):
    def test_corpus_builder_counts_docs_in_txt_and_jsonl(self):
        """Verify CorpusBuilder counts documents inside .txt and .jsonl files."""
        built_dir = wb_dir / 'will_breaker_delta' / 'corpus' / 'built'
        builder = CorpusBuilder(built_dir)
        total = builder.get_total_docs()
        self.assertGreater(total, 20000, "Corpus should contain over 20,000 documents")
        stats = builder.get_source_stats()
        self.assertGreater(len(stats), 30, "Should have over 30 source files")


if __name__ == '__main__':
    unittest.main()
