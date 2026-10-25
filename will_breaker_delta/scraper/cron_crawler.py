#!/usr/bin/env python3
"""
Cron entry point for the LiveCrawlerPipeline.
Wraps the existing pipeline with logging and error handling suitable for systemd.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add parent to path
delta_dir = Path(__file__).parent.parent
sys.path.insert(0, str(delta_dir))

from scraper.live_crawler import LiveCrawlerPipeline


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log_prefix = f"[cron-{now}]"

    try:
        pipeline = LiveCrawlerPipeline()
        result = pipeline.run_cycle()

        print(f"{log_prefix} Cycle complete.")
        print(f"{log_prefix} Documents analyzed: {result.get('documents_analyzed', 0)}")
        print(f"{log_prefix} Flagged tokens: {result.get('flagged_tokens_count', 0)}")
        print(f"{log_prefix} Precursor events: {result.get('precursor_count', 0)}")
        forecast_count = len(result.get("forecasts", []))
        print(f"{log_prefix} Forecasts generated: {forecast_count}")

        # Write a cron-status file for monitoring
        status_file = delta_dir / "corpus" / "cron_status.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        status = {
            "last_run": now,
            "status": "ok",
            "documents_analyzed": result.get("documents_analyzed", 0),
            "flagged_tokens": result.get("flagged_tokens_count", 0),
            "precursor_count": result.get("precursor_count", 0),
            "forecasts": result.get("forecasts", [])
        }
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2)

    except Exception as e:
        print(f"{log_prefix} CRON CRAWLER FAILED: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        # Write error status
        status_file = delta_dir / "corpus" / "cron_status.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        status = {
            "last_run": now,
            "status": "error",
            "error": str(e)
        }
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2)
        sys.exit(1)


if __name__ == "__main__":
    main()
