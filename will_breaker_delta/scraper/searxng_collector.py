"""SearXNG Collector — Will Breaker Delta Detection (Candidate I-E / Protocol 020).

Queries local SearXNG (:18080) across pre-registered archetypal categories
to capture real-time discourse streams for emotional lexical delta scoring.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


class SearXNGCollector:
    """Collects real-time documents from local SearXNG across archetypal domains."""

    DEFAULT_DOMAINS = {
        "geopolitical": "geopolitical military conflict diplomatic tension escalation",
        "financial": "banking liquidity debt default currency shock economic crisis",
        "geophysical": "earthquake volcano seismic anomaly geomagnetic solar flare",
        "scientific_anomaly": "quantum physics anomalous observation breakthrough experimental discovery",
    }

    def __init__(self, endpoint: str = "http://127.0.0.1:18080/search"):
        self.endpoint = endpoint

    def search_domain(self, domain: str, query: str, limit: int = 25) -> List[Dict]:
        """Query SearXNG for a domain and return formatted document records."""
        url = f"{self.endpoint}?q={urllib.parse.quote(query)}&format=json&categories=news,general"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "WillBreaker-Delta/1.0", "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            print(f"[SEARXNG] Warning: Search failed for '{domain}': {exc}")
            return []

        results = data.get("results", [])[:limit]
        documents = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for item in results:
            title = item.get("title") or ""
            content = item.get("content") or ""
            combined_text = f"{title}. {content}".strip()
            if len(combined_text) < 30:
                continue

            documents.append({
                "source": "searxng",
                "domain": domain,
                "query": query,
                "title": title,
                "url": item.get("url") or "",
                "text": combined_text,
                "publishedDate": item.get("publishedDate") or now_iso,
                "engine": item.get("engine") or "unknown",
                "collected_at": now_iso,
            })
        return documents

    def collect_all_domains(self, domains: Optional[Dict[str, str]] = None) -> List[Dict]:
        """Collect live discourse documents across all registered domains."""
        active_domains = domains or self.DEFAULT_DOMAINS
        all_docs = []
        for domain, query in active_domains.items():
            docs = self.search_domain(domain, query)
            print(f"[SEARXNG] Collected {len(docs)} live documents for domain '{domain}'")
            all_docs.extend(docs)
        return all_docs


if __name__ == "__main__":
    collector = SearXNGCollector()
    docs = collector.collect_all_domains()
    print(f"\nTotal live documents collected: {len(docs)}")
    if docs:
        print(f"Sample document:\n{json.dumps(docs[0], indent=2)}")
