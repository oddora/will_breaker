"""
API Collector — Will Breaker Delta-Detection Phase 2
Stub for Twitter/X API collection (requires API key).
"""

import json
from pathlib import Path
from typing import List, Dict


class APICollector:
    """Collect documents from APIs (Twitter/X, news APIs, etc.)."""
    
    def __init__(self, output_dir: Path, api_key: str = None):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.api_key = api_key
    
    def collect_twitter(self, query: str, max_tweets: int = 1000) -> List[Dict]:
        """Collect tweets matching query (stub — requires Twitter API v2)."""
        # TODO: Implement Twitter API v2 collection
        # For now, return empty list with warning
        print(f"[WARN] Twitter collection stub — API key required")
        return []
    
    def collect_news_api(self, api_endpoint: str, query: str) -> List[Dict]:
        """Collect from news API (stub)."""
        # TODO: Implement news API collection
        print(f"[WARN] News API collection stub — API key required")
        return []
    
    def save_documents(self, documents: List[Dict], source_name: str):
        """Save collected documents."""
        if not documents:
            return
        
        output_file = self.output_dir / f"{source_name}.jsonl"
        
        with open(output_file, 'a') as f:
            for doc in documents:
                f.write(json.dumps(doc) + '\n')
        
        print(f"[INFO] Saved {len(documents)} docs from {source_name}")


if __name__ == '__main__':
    collector = APICollector(Path(__file__).parent.parent / 'corpus' / 'built')
    
    # Example usage (requires API key)
    # tweets = collector.collect_twitter("dimensional shifting", max_tweets=500)
    # collector.save_documents(tweets, "twitter_dimensional")
