"""Precursor Delta Engine — Will Breaker Protocol 020 (Candidate I-E).

Integrates SearXNG live discourse collection (:18080), baseline context modeling,
emotional lexical anomaly scoring (Clif High methodology), wb-agent archetype
synthesis (:18284), and cryptographic SHA-256 pre-commitment.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import sys
DELTA_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DELTA_DIR))

from analyzer.anomaly_scorer import AnomalyScorer, EmotionalLexicon, tokenize
from analyzer.context_model import ContextModel
from scraper.searxng_collector import SearXNGCollector
from validator.crypto_predictor import CryptoPredictor

ROOT_DIR = DELTA_DIR.parent
RESULTS_DIR = ROOT_DIR / "results" / "delta_forecasts"


class PrecursorDeltaEngine:
    """End-to-end pipeline for predictive linguistic delta detection and sealed forecasting."""

    def __init__(
        self,
        searxng_endpoint: str = "http://127.0.0.1:18080/search",
        wb_agent_endpoint: str = "http://127.0.0.1:18284/v1/chat/completions",
        tag: str = "session050",
    ):
        self.tag = tag
        self.collector = SearXNGCollector(endpoint=searxng_endpoint)
        self.wb_agent_endpoint = wb_agent_endpoint

        # Load baseline resources
        corpus_built_dir = DELTA_DIR / "corpus" / "built"
        lexicon_dir = DELTA_DIR / "lexicon"
        self.context_model = ContextModel(corpus_path=corpus_built_dir)
        self.lexicon = EmotionalLexicon(
            nrc_path=lexicon_dir / "nrc_emotion_lexicon.csv",
            vader_path=lexicon_dir / "vader_lexicon.csv",
        )
        self.scorer = AnomalyScorer(lexicon=self.lexicon, baseline_model=self.context_model)
        self.predictor = CryptoPredictor()

    def query_wb_agent(self, domain: str, doc_count: int, delta_words: List[Dict]) -> Optional[Dict]:
        """Query wb-agent to synthesize pre-manifestation archetype from anomalous deltas."""
        words_summary = "\n".join(
            f"- '{w['word']}' (anomaly={w['anomaly_score']:.3f}, valence={w['valence']:.2f}, "
            f"emotions={w['emotions']}, occurrences={w['count']})"
            for w in delta_words[:8]
        )

        user_content = f"""DOMAIN: {domain}
COLLECTED TEXT COUNT: {doc_count}

DETECTED ANOMALOUS DELTA WORDS (Outliers appearing outside baseline context with high emotional weight):
{words_summary}

TASK:
Synthesize 1 specific, testable pre-manifestation forecast based on these linguistic deltas.
Output MUST be strict JSON matching this schema:
{{
  "event_id": "{domain}_{self.tag}",
  "domain": "{domain}",
  "anomalous_precursors": ["{delta_words[0]['word'] if delta_words else 'unknown'}"],
  "predicted_hypothesis": "<clear statement of the macro event indicated by the delta>",
  "falsifiable_criterion": "<concrete objective condition that confirms or refutes this forecast>",
  "target_window_days": 14,
  "confidence_probability": <float 0.05-0.95>
}}
Output ONLY the raw JSON object, no markdown, no conversational text."""

        payload = {
            "model": "wb-agent",
            "messages": [
                {"role": "system", "content": "You are the Will Breaker Delta Precursor Synthesizer. Output ONLY strict JSON."},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.3,
            "max_tokens": 300,
            "chat_template_kwargs": {"enable_thinking": False},
        }

        try:
            req = urllib.request.Request(
                self.wb_agent_endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"].strip()
                # Parse JSON, handling optional code fence
                json_str = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
                return json.loads(json_str)
        except Exception as exc:
            print(f"[ENGINE] Error querying wb-agent for domain '{domain}': {exc}")
            return None

    def analyze_domain(self, domain: str, docs: List[Dict]) -> Tuple[List[Dict], Optional[Dict]]:
        """Compute word-level anomaly scores across domain documents and get archetype forecast."""
        word_scores = defaultdict(lambda: {"total_anomaly": 0.0, "count": 0, "max_anomaly": 0.0})
        
        for doc in docs:
            tokens = tokenize(doc["text"])
            scores = self.scorer.score_document(tokens)
            for item in scores:
                w = item["word"]
                score = item.get("anomaly", item.get("anomaly_score", 0.0))
                word_scores[w]["total_anomaly"] += score
                word_scores[w]["count"] += 1
                if score > word_scores[w]["max_anomaly"]:
                    word_scores[w]["max_anomaly"] = score

        # Filter and rank top anomalies
        delta_candidates = []
        for w, stats in word_scores.items():
            if stats["count"] >= 2:  # Appeared multiple times in live stream
                profile = self.lexicon.get_emotion_profile(w)
                valence = profile.get("valence", 0.0)
                emotions = [k for k, v in profile.items() if k not in ("valence", "custom_weight") and v > 0]
                delta_candidates.append({
                    "word": w,
                    "anomaly_score": round(stats["max_anomaly"], 4),
                    "count": stats["count"],
                    "valence": round(valence, 2),
                    "emotions": emotions[:3],
                })

        delta_candidates.sort(key=lambda x: (x["anomaly_score"], x["count"]), reverse=True)
        top_deltas = delta_candidates[:10]

        forecast = None
        if top_deltas:
            forecast = self.query_wb_agent(domain, len(docs), top_deltas)

        return top_deltas, forecast

    def run(self) -> Dict:
        """Run complete precursor collection, anomaly scoring, archetype synthesis, and cryptographic seal."""
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"\n[ENGINE] Starting Clif High Precursor Delta Run ({self.tag})...")

        # Step 1: Collect live discourse across domains via SearXNG
        all_docs = self.collector.collect_all_domains()
        docs_by_domain = defaultdict(list)
        for doc in all_docs:
            docs_by_domain[doc["domain"]].append(doc)

        # Step 2: Analyze each domain and synthesize forecasts
        forecasts = []
        domain_reports = {}

        for domain, docs in docs_by_domain.items():
            print(f"\n[ENGINE] Processing domain '{domain}' ({len(docs)} documents)...")
            top_deltas, forecast = self.analyze_domain(domain, docs)
            domain_reports[domain] = {
                "doc_count": len(docs),
                "top_anomalies": top_deltas[:5],
                "forecast": forecast,
            }
            if forecast:
                print(f"  -> Projected: {forecast.get('predicted_hypothesis')}")
                forecasts.append(forecast)

        # Step 3: Cryptographic Seal & Pre-commitment
        now_iso = datetime.now(timezone.utc).isoformat()
        seal_payload = {
            "tag": self.tag,
            "protocol": "protocols/020-clif-high-delta-precursor.md",
            "model": "wb-agent",
            "searxng_endpoint": self.collector.endpoint,
            "timestamp_utc": now_iso,
            "total_documents": len(all_docs),
            "forecasts": forecasts,
        }

        canonical_bytes = json.dumps(seal_payload, sort_keys=True).encode("utf-8")
        sha256_seal = hashlib.sha256(canonical_bytes).hexdigest()

        seal_record = {
            "sha256_seal": sha256_seal,
            "tag": self.tag,
            "collected_at": now_iso,
            "n_forecasts": len(forecasts),
            "total_documents": len(all_docs),
            "status": "SEALED_PRE_COMMITMENT",
            "resolution_window_days": 14,
        }

        # Write prediction files
        pred_file = RESULTS_DIR / f"{self.tag}_delta_predictions.jsonl"
        with open(pred_file, "w") as f:
            for fc in forecasts:
                f.write(json.dumps(fc) + "\n")

        seal_file = RESULTS_DIR / f"{self.tag}_delta_seal.json"
        with open(seal_file, "w") as f:
            json.dump({**seal_record, "payload": seal_payload}, f, indent=2)

        print("\n" + "=" * 60)
        print(f"PRECURSOR DELTA ENGINE — {self.tag} SEALED")
        print("=" * 60)
        print(f"SHA-256 Seal: {sha256_seal}")
        print(f"Forecasts Emitted: {len(forecasts)}")
        print(f"Total Live Documents: {len(all_docs)}")
        print(f"Predictions File: {pred_file}")
        print(f"Seal File: {seal_file}")
        print("=" * 60)

        return {
            "seal": sha256_seal,
            "forecasts": forecasts,
            "reports": domain_reports,
            "files": {"predictions": str(pred_file), "seal": str(seal_file)},
        }


if __name__ == "__main__":
    engine = PrecursorDeltaEngine(tag="session050")
    engine.run()
