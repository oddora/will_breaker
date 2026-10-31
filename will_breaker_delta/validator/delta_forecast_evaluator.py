"""Delta Forecast Evaluator — Will Breaker Protocol 020 (Candidate I-E).

Evaluates cryptographically sealed Clif High precursor delta forecasts against
ground-truth real-world evidence gathered via SearXNG (:18080) and domain APIs
(e.g., USGS Earthquake Catalog). Tracks window progression (14-day default),
evaluates falsification criteria, and computes probabilistic scoring metrics (Brier, Log-Loss).
"""

from __future__ import annotations

import hashlib
import json
import math
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DELTA_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = DELTA_DIR.parent
RESULTS_DIR = ROOT_DIR / "results" / "delta_forecasts"


class DeltaForecastEvaluator:
    """Evaluates sealed precursor delta forecasts and computes calibration metrics."""

    def __init__(
        self,
        searxng_endpoint: str = "http://127.0.0.1:18080/search",
        usgs_endpoint: str = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson",
    ):
        self.searxng_endpoint = searxng_endpoint
        self.usgs_endpoint = usgs_endpoint

    @staticmethod
    def verify_seal(seal_path: Path) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Verify the cryptographic SHA-256 seal of a sealed forecast file.

        Returns (is_valid, seal_data).
        """
        if not seal_path.exists():
            return False, None

        with open(seal_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        expected_seal = data.get("sha256_seal")
        payload = data.get("payload")
        if not expected_seal or not payload:
            return False, data

        canonical_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        computed_seal = hashlib.sha256(canonical_bytes).hexdigest()
        return (computed_seal == expected_seal), data

    @staticmethod
    def compute_window_status(
        collected_at_iso: str,
        window_days: int = 14,
        now_dt: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Compute window elapsed time, expiration status, and days remaining."""
        if now_dt is None:
            now_dt = datetime.now(timezone.utc)

        start_dt = datetime.fromisoformat(collected_at_iso)
        end_dt = start_dt + timedelta(days=window_days)
        elapsed_seconds = (now_dt - start_dt).total_seconds()
        elapsed_days = max(0.0, elapsed_seconds / 86400.0)
        remaining_days = max(0.0, (end_dt - now_dt).total_seconds() / 86400.0)
        is_expired = now_dt >= end_dt

        return {
            "start_time_utc": start_dt.isoformat(),
            "target_end_time_utc": end_dt.isoformat(),
            "now_utc": now_dt.isoformat(),
            "window_days": window_days,
            "elapsed_days": round(elapsed_days, 2),
            "remaining_days": round(remaining_days, 2),
            "is_window_closed": is_expired,
        }

    def query_searxng(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Query local SearXNG for real-time domain evidence."""
        params = urllib.parse.urlencode({
            "q": query,
            "format": "json",
            "categories": "general,news",
        })
        url = f"{self.searxng_endpoint}?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "WillBreakerEvaluator/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("results", [])
                return [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", ""),
                    }
                    for r in results[:max_results]
                ]
        except Exception as exc:
            return [{"error": f"SearXNG query failed: {exc}"}]

    def query_usgs_earthquakes(self, min_time_epoch_ms: Optional[int] = None) -> List[Dict[str, Any]]:
        """Query USGS magnitude 4.5+ earthquake GeoJSON feed."""
        req = urllib.request.Request(self.usgs_endpoint, headers={"User-Agent": "WillBreakerEvaluator/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                features = data.get("features", [])
                filtered = []
                for feat in features:
                    props = feat.get("properties", {})
                    eq_time = props.get("time", 0)
                    if min_time_epoch_ms is None or eq_time >= min_time_epoch_ms:
                        filtered.append({
                            "place": props.get("place", "Unknown"),
                            "mag": props.get("mag"),
                            "time_epoch_ms": eq_time,
                            "time_iso": datetime.fromtimestamp(eq_time / 1000.0, tz=timezone.utc).isoformat(),
                            "url": props.get("url"),
                        })
                return filtered
        except Exception as exc:
            return [{"error": f"USGS query failed: {exc}"}]

    def evaluate_geopolitical(self, forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate geopolitical forecast falsification criterion.

        Criterion: 'official declaration of ceasefire or arms control agreement within 14 days'
        """
        query = "Iran military ceasefire official declaration OR arms control agreement"
        results = self.query_searxng(query, max_results=5)
        has_error = any("error" in r for r in results)

        ceasefire_indicators = [
            "signed ceasefire", "official ceasefire", "arms control treaty signed",
            "peace treaty ratified", "hostilities ended officially"
        ]

        found_evidence = False
        matching_snippets = []
        if not has_error:
            for r in results:
                text = (r.get("title", "") + " " + r.get("content", "")).lower()
                for ind in ceasefire_indicators:
                    if ind in text:
                        found_evidence = True
                        matching_snippets.append(r)
                        break

        return {
            "domain": "geopolitical",
            "falsification_condition_met": found_evidence,
            "evidence_count": len(results),
            "matching_snippets": matching_snippets,
            "notes": "Ceasefire/agreement found -> hypothesis falsified; no ceasefire -> hypothesis holds."
                     if not has_error else "SearXNG query degraded.",
        }

    def evaluate_financial(self, forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate financial forecast falsification criterion.

        Criterion: 'Central bank reserves fall below 10% of total liabilities in 3 major economies'
        """
        query = "central bank foreign reserves fall below 10% liabilities sovereign default"
        results = self.query_searxng(query, max_results=5)
        has_error = any("error" in r for r in results)

        found_evidence = False
        matching_snippets = []
        if not has_error:
            for r in results:
                text = (r.get("title", "") + " " + r.get("content", "")).lower()
                if "reserves fell below 10%" in text or "central bank reserve collapse" in text:
                    found_evidence = True
                    matching_snippets.append(r)

        return {
            "domain": "financial",
            "falsification_condition_met": found_evidence,
            "evidence_count": len(results),
            "matching_snippets": matching_snippets,
            "notes": "Reserve collapse found in 3 major economies -> criterion met."
                     if not has_error else "SearXNG query degraded.",
        }

    def evaluate_geophysical(self, forecast: Dict[str, Any], start_dt_iso: str) -> Dict[str, Any]:
        """Evaluate geophysical forecast falsification criterion.

        Criterion: 'USGS earthquake catalog shows zero events above magnitude 4.5'
        """
        start_epoch_ms = int(datetime.fromisoformat(start_dt_iso).timestamp() * 1000)
        events = self.query_usgs_earthquakes(min_time_epoch_ms=start_epoch_ms)
        has_error = any("error" in e for e in events)

        if has_error:
            return {
                "domain": "geophysical",
                "falsification_condition_met": None,
                "event_count_mag_ge_4_5": 0,
                "notes": "USGS query degraded or offline.",
            }

        event_count = len(events)
        # Criterion states "catalog shows zero events above magnitude 4.5"
        # If event_count == 0, the falsification condition is met (zero events occurred).
        # If event_count > 0, seismic events did occur (criterion violated).
        falsification_condition_met = (event_count == 0)

        return {
            "domain": "geophysical",
            "event_count_mag_ge_4_5": event_count,
            "falsification_condition_met": falsification_condition_met,
            "recent_events": events[:3],
            "notes": f"Recorded {event_count} earthquakes >= 4.5 since start. Zero events criterion is {falsification_condition_met}.",
        }

    def evaluate_scientific_anomaly(self, forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate scientific anomaly forecast falsification criterion.

        Criterion: 'publication of peer-reviewed results confirming anomaly-driven breakthroughs'
        """
        query = "peer-reviewed particle physics anomaly breakthrough confirmation Nature Science Physical Review"
        results = self.query_searxng(query, max_results=5)
        has_error = any("error" in r for r in results)

        found_evidence = False
        matching_snippets = []
        if not has_error:
            for r in results:
                text = (r.get("title", "") + " " + r.get("content", "")).lower()
                if "peer-reviewed" in text and ("anomaly confirmed" in text or "physics breakthrough" in text):
                    found_evidence = True
                    matching_snippets.append(r)

        return {
            "domain": "scientific_anomaly",
            "falsification_condition_met": found_evidence,
            "evidence_count": len(results),
            "matching_snippets": matching_snippets,
            "notes": "Verified peer-reviewed publication confirming breakthrough found."
                     if not has_error else "SearXNG query degraded.",
        }

    @staticmethod
    def calculate_probabilistic_metrics(
        forecasts_evaluated: List[Dict[str, Any]],
        reference_climatology: float = 0.50,
    ) -> Dict[str, Any]:
        """Calculate Brier score, Brier Skill Score (BSS), and Log Loss for resolved items."""
        resolved = [f for f in forecasts_evaluated if f.get("resolved_outcome") is not None]
        if not resolved:
            return {
                "n_resolved": 0,
                "mean_brier_score": None,
                "reference_brier_score": None,
                "brier_skill_score": None,
                "mean_log_loss": None,
            }

        brier_sum = 0.0
        log_loss_sum = 0.0
        ref_brier_sum = 0.0

        for item in resolved:
            p = float(item["confidence_probability"])
            y = float(item["resolved_outcome"])

            bs = (p - y) ** 2
            brier_sum += bs
            ref_brier_sum += (reference_climatology - y) ** 2

            p_clamped = min(max(p, 1e-6), 1.0 - 1e-6)
            log_loss_sum += -(y * math.log(p_clamped) + (1.0 - y) * math.log(1.0 - p_clamped))

        n = len(resolved)
        mean_bs = brier_sum / n
        mean_ref_bs = ref_brier_sum / n
        bss = 1.0 - (mean_bs / mean_ref_bs) if mean_ref_bs > 0 else 0.0
        mean_ll = log_loss_sum / n

        return {
            "n_resolved": n,
            "mean_brier_score": round(mean_bs, 4),
            "reference_brier_score": round(mean_ref_bs, 4),
            "brier_skill_score": round(bss, 4),
            "mean_log_loss": round(mean_ll, 4),
        }

    def evaluate_session(
        self,
        tag: str = "session050",
        simulated_outcomes: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Run full evaluation on a session's sealed predictions and seal file."""
        seal_file = RESULTS_DIR / f"{tag}_delta_seal.json"
        is_seal_valid, seal_data = self.verify_seal(seal_file)

        if not is_seal_valid or not seal_data:
            return {
                "tag": tag,
                "error": f"Invalid or missing seal file at {seal_file}",
                "is_seal_valid": is_seal_valid,
            }

        payload = seal_data.get("payload", {})
        forecasts = payload.get("forecasts", [])
        collected_at = payload.get("timestamp_utc", seal_data.get("collected_at"))
        window_days = seal_data.get("resolution_window_days", 14)

        timing = self.compute_window_status(collected_at, window_days=window_days)

        evaluations = []
        for fc in forecasts:
            eid = fc.get("event_id")
            domain = fc.get("domain")

            # Perform live domain evidence check
            if domain == "geopolitical":
                evidence = self.evaluate_geopolitical(fc)
            elif domain == "financial":
                evidence = self.evaluate_financial(fc)
            elif domain == "geophysical":
                evidence = self.evaluate_geophysical(fc, collected_at)
            elif domain == "scientific_anomaly":
                evidence = self.evaluate_scientific_anomaly(fc)
            else:
                evidence = {"domain": domain, "notes": "Unknown domain"}

            # Determine resolution state
            resolved_outcome = None
            if simulated_outcomes and eid in simulated_outcomes:
                resolved_outcome = simulated_outcomes[eid]
            elif timing["is_window_closed"]:
                # When window is closed, determine final binary outcome
                # If falsification condition was met, hypothesis failed (y = 0.0); else survived (y = 1.0)
                cond_met = evidence.get("falsification_condition_met")
                if cond_met is not None:
                    resolved_outcome = 0.0 if cond_met else 1.0

            item_eval = {
                **fc,
                "status": "RESOLVED" if resolved_outcome is not None else "IN_PROGRESS",
                "resolved_outcome": resolved_outcome,
                "evidence": evidence,
            }
            if resolved_outcome is not None:
                p = float(fc.get("confidence_probability", 0.5))
                item_eval["brier_score"] = round((p - resolved_outcome) ** 2, 4)

            evaluations.append(item_eval)

        metrics = self.calculate_probabilistic_metrics(evaluations)

        report = {
            "tag": tag,
            "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
            "seal_sha256": seal_data.get("sha256_seal"),
            "is_seal_valid": is_seal_valid,
            "window_timing": timing,
            "forecasts_evaluated": evaluations,
            "metrics": metrics,
        }

        # Write evaluation report
        out_path = RESULTS_DIR / f"{tag}_evaluation_report.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        report["report_path"] = str(out_path)
        return report


if __name__ == "__main__":
    evaluator = DeltaForecastEvaluator()
    rep = evaluator.evaluate_session("session050")
    print(f"\n[EVALUATOR] Evaluated Session 050:")
    print(f"  Seal Valid: {rep.get('is_seal_valid')}")
    print(f"  Window Closed: {rep.get('window_timing', {}).get('is_window_closed')}")
    print(f"  Elapsed Days: {rep.get('window_timing', {}).get('elapsed_days')} / {rep.get('window_timing', {}).get('window_days')}")
    print(f"  Report: {rep.get('report_path')}")
