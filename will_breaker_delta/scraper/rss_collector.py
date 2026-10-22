"""
RSS Feed Collector — Will Breaker Delta-Detection Phase 2
Collects documents from RSS feeds for corpus building.
"""

import feedparser
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class RSSCollector:
    """Collect documents from RSS feeds."""
    
    def __init__(self, output_dir: Path, max_docs_per_source: int = 500):
        self.output_dir = output_dir
        self.max_docs_per_source = max_docs_per_source
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track last fetch time for each source
        self.last_fetch: Dict[str, datetime] = {}
    
    def fetch_feed(self, feed_url: str, source_name: str) -> List[Dict]:
        """Fetch a single RSS feed."""
        feed = feedparser.parse(feed_url)
        
        if feed.bozo != 0:
            print(f"[WARN] Feed {source_name} parse error: {feed.bozo_exception}")
            return []
        
        documents = []
        for entry in feed.entries[:self.max_docs_per_source]:
            doc = {
                'source': source_name,
                'title': entry.get('title', ''),
                'content': entry.get('summary', entry.get('description', '')),
                'published': entry.get('published', entry.get('updated', '')),
                'link': entry.get('link', ''),
                'fetched_at': datetime.now().isoformat()
            }
            documents.append(doc)
        
        return documents
    
    def save_documents(self, documents: List[Dict], source_name: str):
        """Save collected documents to corpus directory."""
        if not documents:
            return
        
        # Save as JSONL (one doc per line)
        output_file = self.output_dir / f"{source_name}.jsonl"
        
        with open(output_file, 'a') as f:
            for doc in documents:
                f.write(json.dumps(doc) + '\n')
        
        print(f"[INFO] Saved {len(documents)} docs from {source_name}")
    
    def collect_all(self, sources: List[Dict]):
        """Collect from all configured sources."""
        for source in sources:
            url = source['url']
            name = source['name']
            
            print(f"[INFO] Fetching {name}...")
            docs = self.fetch_feed(url, name)
            self.save_documents(docs, name)
            
            # Rate limiting
            time.sleep(1)
    
    def get_corpus_stats(self) -> Dict:
        """Get statistics about the built corpus."""
        stats = {}
        total_docs = 0
        
        for file in self.output_dir.glob('*.jsonl'):
            count = sum(1 for _ in open(file))
            stats[file.stem] = count
            total_docs += count
        
        stats['total'] = total_docs
        return stats


if __name__ == '__main__':
    # Configured sources
    sources = [
        {'name': 'reddit_consciousness', 'url': 'https://www.reddit.com/r/consciousness/.rss'},
        {'name': 'reddit_futurology', 'url': 'https://www.reddit.com/r/Futurology/.rss'},
        {'name': 'nature_news', 'url': 'https://www.nature.com/nature.rss'},
        {'name': 'science_news', 'url': 'https://www.sciencemag.org/rss/news_current.xml'},
        {'name': 'cia_foia', 'url': 'https://www.cia.gov/rss/foia-reading-room.xml'},
    ]
    
    collector = RSSCollector(Path(__file__).parent.parent / 'corpus' / 'built')
    collector.collect_all(sources)
    
    stats = collector.get_corpus_stats()
    print(f"\n[STATS] Corpus: {stats['total']} documents across {len(stats) - 1} sources")
