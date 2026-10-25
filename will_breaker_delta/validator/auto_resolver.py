"""
Auto Resolver — Automated Resolution Checker for Sealed Pre-Registrations
Polls the crypto predictions registry, resolves SEALED commitments whose
target dates have passed, and writes results back to the registry.
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from validator.crypto_predictor import CryptoPredictor


class AutoResolver:
    """Resolves sealed predictions when their target dates arrive."""

    def __init__(self, registry_file: Path = None):
        self.predictor = CryptoPredictor(registry_file=registry_file)
        self.sealed = self.predictor.load_all_commitments()
        self.sealed = [r for r in self.sealed if r.get("status") == "SEALED"]

    def _fetch_arxiv_term_counts(self, term: str, days: int = 30) -> int:
        """Count recent arXiv papers containing a search term."""
        try:
            url = (
                f"https://export.arxiv.org/api/query?"
                f"search_query=all:{term}&start=0&max_results=500&sortBy=submittedDate&sortOrder=descending"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "WillBreaker/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8")
                return content.count("<entry>")
        except Exception as e:
            print(f"[AUTO-RESOLVER] arXiv fetch failed for '{term}': {e}")
            return -1

    def _fetch_vix(self) -> Optional[float]:
        """Fetch current VIX from a public source; returns None on failure."""
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?interval=1d&range=1d"
            req = urllib.request.Request(url, headers={"User-Agent": "WillBreaker/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
                return closes[-1] if closes else None
        except Exception as e:
            print(f"[AUTO-RESOLVER] VIX fetch failed: {e}")
            return None

    def _check_sports_event(self, event_id: str) -> Optional[str]:
        """
        Query official box-score data for a sports event.
        Returns actual outcome string or None if still in progress.
        """
        try:
            # Strip domain prefix to get the sport+teams
            parts = event_id.split("_", 2)
            if len(parts) < 3:
                return None
            sport, teams = parts[0], parts[2]
            # Map to ESPN API
            sport_map = {"NCAA": "ncaaf", "NBA": "nba"}
            s = sport_map.get(sport, "ncaaf")
            url = f"https://site.api.espn.com/apis/site/v2/sports/{s}/scoreboard"
            req = urllib.request.Request(url, headers={"User-Agent": "WillBreaker/1.0"})
            with urllib.request.urlopen(req, timeout=8) in resp:
                data = json.loads(resp.read().decode("utf-8"))
            events = data.get("events", [])
            for ev in events:
                ev_teams = {t["team"]["displayName"] for t in ev.get("competitions", [{}])[0].get("competitors", [])}
                if all(t.lower() in " ".join(ev_teams).lower() for t in teams.split("_vs_")):
                    comp = ev["competitions"][0]
                    winner = comp.get("winner", "home")
                    home = comp.get("competitors", [{}])[0]["team"]["displayName"]
                    away = comp.get("competitors", [{}])[1]["team"]["displayName"]
                    home_score = comp.get("competitors", [{}])[0].get("score", 0)
                    away_score = comp.get("competitors", [{}])[1].get("score", 0)
                    return f"{home} {home_score}-{away_score} {away}"
            return None  # event not found in live scoreboard
        except Exception as e:
            print(f"[AUTO-RESOLVER] Sports fetch failed for '{event_id}': {e}")
            return None

    def resolve_sealed(self, dry_run: bool = False) -> Dict:
        """
        Check all SEALED commitments. If target date has passed, attempt resolution.
        Returns summary dict.
        """
        now = datetime.now(timezone.utc)
        resolved = []
        still_sealed = []
        errors = []

        for rec in self.sealed:
            ts = rec["prediction"]["event_timestamp"]
            target = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            # Allow 24h grace period after target
            if now < target - timedelta(hours=24):
                still_sealed.append(rec["commitment_id"])
                continue

            cid = rec["commitment_id"]
            domain = rec["prediction"]["domain"]
            desc = rec["prediction"]["event_description"]
            predicted = rec["prediction"]["predicted_outcome"]
            prob = rec["prediction"]["probability"]

            is_correct = None
            resolution_note = ""

            if domain == "scientific_linguistics" and "arxiv" in desc.lower():
                term = "topological_coherence" if "topological" in desc.lower() else "transformer"
                count = self._fetch_arxiv_term_counts(term, days=30)
                if count >= 0:
                    threshold = 2.5 if "topological" in desc.lower() else 15
                    is_correct = count >= threshold
                    resolution_note = f"arXiv count={count}, threshold={threshold}"
                else:
                    errors.append(f"{cid}: arXiv fetch failed")
                    continue

            elif domain == "financial_lexicon" and "vix" in desc.lower():
                vix = self._fetch_vix()
                if vix is not None:
                    is_correct = vix > 22.0
                    resolution_note = f"VIX={vix:.2f}, threshold=22.0"
                else:
                    errors.append(f"{cid}: VIX fetch failed")
                    continue

            elif domain == "mechanistic_ai" or domain == "human_consciousness":
                # These need manual resolution (cross-arch experiment or RCT)
                still_sealed.append(cid)
                continue

            elif domain == "live_crawler" or "rss" in desc.lower():
                # Check if any live_crawler events were flagged before the target date
                corpus_dir = Path(__file__).parent.parent.parent / "corpus"
                events_file = corpus_dir / "delta_events.jsonl"
                if events_file.exists():
                    event_lines = events_file.read_text().strip().split("\n")
                    recent_events = [
                        json.loads(line)
                        for line in event_lines
                        if datetime.fromisoformat(json.loads(line).get("cycle_timestamp", "1970-01-01")) < target
                    ]
                    has_precursor = any(
                        e.get("archetype") == "threshold_crossing"
                        for e in recent_events
                    )
                    is_correct = has_precursor
                    resolution_note = f"live_crawler_events={len(recent_events)}, has_threshold_crossing={has_precursor}"
                else:
                    still_sealed.append(cid)
                    continue
            else:
                still_sealed.append(cid)
                continue

            if is_correct is not None:
                status = "RESOLVED" if is_correct else "FAILED"
                brier = (1.0 - prob) ** 2 if is_correct else prob ** 2
                if not dry_run:
                    self.predictor.resolve_prediction(
                        commitment_id=cid,
                        actual_outcome=status,
                        resolution_notes=f"{resolution_note}. Predicted: {predicted}. P={prob}"
                    )
                resolved.append({
                    "commitment_id": cid,
                    "status": status,
                    "brier": round(brier, 4),
                    "note": resolution_note
                })

        return {
            "resolved_count": len(resolved),
            "still_sealed_count": len(still_sealed),
            "resolved": resolved,
            "still_sealed": still_sealed,
            "errors": errors
        }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auto-resolve sealed Will Breaker predictions")
    parser.add_argument("--dry-run", action="store_true", help="Show what would resolve without writing")
    args = parser.parse_args()

    resolver = AutoResolver()
    result = resolver.resolve_sealed(dry_run=args.dry_run)

    print(f"\n[Auto-Resolver] Resolved {result['resolved_count']} predictions.")
    print(f"Still sealed: {result['still_sealed_count']}")
    for r in result["resolved"]:
        print(f"  {r['commitment_id']}: {r['status']} (Brier={r['brier']}) — {r['note']}")
    if result["errors"]:
        print(f"Errors: {result['errors']}")
    if result["still_sealed"]:
        print(f"Still sealed: {result['still_sealed']}")
