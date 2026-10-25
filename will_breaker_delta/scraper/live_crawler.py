"""
Live Crawler & Automated Pipeline Runner — Will Breaker Delta Detection
Fetches live feeds, tokenizes documents, runs anomaly scoring against baseline,
tracks deltas, and produces continuous archetype forecasts.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional

import sys
delta_dir = Path(__file__).parent.parent
sys.path.insert(0, str(delta_dir))

from analyzer.anomaly_scorer import AnomalyScorer, load_lexicons, BaselineContextModel, tokenize
from analyzer.context_model import ContextModel
from analyzer.delta_tracker import DeltaTracker
from analyzer.forecast_generator import ForecastGenerator
from scraper.rss_collector import RSSCollector
from scraper.arxiv_collector import ArxivCollector


class LiveCrawlerPipeline:
    """End-to-end automated pipeline runner for live delta detection."""

    def __init__(self, base_dir: Path = None):
        self.base_dir = Path(base_dir) if base_dir else delta_dir
        self.corpus_built_dir = self.base_dir / "corpus" / "built"
        self.lexicon_dir = self.base_dir / "lexicon"
        self.config_dir = self.base_dir / "config"
        self.output_events_file = self.base_dir / "corpus" / "delta_events.jsonl"
        self.output_forecast_file = self.base_dir / "corpus" / "latest_forecast.json"

        # Load resources
        self.lexicon = load_lexicons(
            self.lexicon_dir / "nrc_emotion_lexicon.csv",
            self.lexicon_dir / "vader_lexicon.csv",
            self.config_dir / "lexicon_weights.yaml"
        )
        self.context_model = ContextModel(self.corpus_built_dir)
        self.scorer = AnomalyScorer(self.lexicon, self.context_model)
        self.tracker = DeltaTracker(self.corpus_built_dir)
        self.forecaster = ForecastGenerator(self.config_dir / "forecast_rules.yaml")

    def run_cycle(self, documents: Optional[List[Dict]] = None) -> Dict:
        """
        Execute one complete delta-detection cycle.
        If documents is None, attempts live fetching with graceful offline handling.
        """
        now = datetime.now(timezone.utc)
        print(f"[CRAWLER] Starting delta cycle at {now.isoformat()}")

        feed_docs = documents or []
        if not feed_docs:
            # 1. Attempt RSS feed collection
            try:
                rss = RSSCollector(output_dir=self.base_dir / "corpus" / "raw")
                default_feeds = [
                    {"name": "phys_org_physics", "url": "https://phys.org/rss-feed/physics-news/"},
                    {"name": "nature_quantum", "url": "https://www.nature.com/subjects/quantum-physics.rss"}
                ]
                for src in default_feeds:
                    docs = rss.fetch_feed(src["url"], src["name"])
                    if docs:
                        feed_docs.extend(docs[:5])
                print(f"[CRAWLER] Collected {len(feed_docs)} items from RSS feeds")
            except Exception as e:
                print(f"[WARN] Live RSS collection skipped: {e}")

            # 2. Ingest recent session / research updates
            try:
                sessions_dir = self.base_dir.parent / "sessions"
                recent_logs = sorted(sessions_dir.glob("session-*log.md"))[-2:]
                for log_p in recent_logs:
                    feed_docs.append({
                        "title": log_p.name,
                        "content": log_p.read_text(encoding="utf-8", errors="ignore")[:3000],
                        "source": "local_session_stream"
                    })
                print(f"[CRAWLER] Ingested {len(recent_logs)} recent session documents for stream monitoring.")
            except Exception as e:
                print(f"[WARN] Local session ingestion skipped: {e}")

        # If offline or no live feeds returned, use system baseline text
        if not feed_docs:
            print("[CRAWLER] No external documents collected; using synthetic monitoring probe.")
            feed_docs = [
                {
                    "title": "Quantum Metric Perturbations in Bilateral Coherence",
                    "content": "Observation of non-local correlation across recursive depth thresholds in neural models.",
                    "source": "internal_probe",
                    "timestamp": now.isoformat()
                }
            ]

        # Score documents
        total_flagged = []
        for doc in feed_docs:
            text = f"{doc.get('title', '')} {doc.get('content', '')}"
            flagged = self.scorer.score_document(text, threshold=0.15)
            for f in flagged:
                f['source'] = doc.get('source', 'stream')
            total_flagged.extend(flagged)

        print(f"[CRAWLER] Scored {len(feed_docs)} documents, flagged {len(total_flagged)} tokens.")

        # Update DeltaTracker
        self.tracker.add_flagged_words(total_flagged, timestamp=now, source="live_pipeline")

        # Detect precursors
        precursors = self.tracker.get_precursor_events(threshold=0.2, min_observations=1)
        print(f"[CRAWLER] Identified {len(precursors)} precursor events.")

        # Generate forecasts
        forecasts = self.forecaster.generate_forecasts(precursors, horizon_hours=48)
        print(f"[CRAWLER] Generated {len(forecasts)} archetype forecasts.")

        # Save latest forecast
        forecast_payload = {
            "cycle_timestamp": now.isoformat(),
            "documents_analyzed": len(feed_docs),
            "flagged_tokens_count": len(total_flagged),
            "precursor_count": len(precursors),
            "forecasts": forecasts
        }

        self.output_forecast_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_forecast_file, "w", encoding="utf-8") as f:
            json.dump(forecast_payload, f, indent=2)

        # Append precursor events to log
        if precursors:
            with open(self.output_events_file, "a", encoding="utf-8") as f:
                for p in precursors:
                    p["cycle_timestamp"] = now.isoformat()
                    f.write(json.dumps(p) + "\n")

        return forecast_payload


if __name__ == "__main__":
    pipeline = LiveCrawlerPipeline()
    res = pipeline.run_cycle()
    print("Cycle complete. Top forecasts:")
    for fc in res.get("forecasts", [])[:3]:
        print(f"  - [{fc['archetype']}] {fc['word']}: projected {fc['projected_anomaly']} (rate: {fc['delta_rate']})")
