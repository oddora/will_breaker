"""
RSS Feed Collector — Will Breaker Delta-Detection Phase 2
Collects documents from RSS feeds for corpus building.
Supports feedparser if installed, with native xml.etree fallback.
"""

import time
import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

try:
    import feedparser
except ImportError:
    feedparser = None


class RSSCollector:
    """Collect documents from RSS/Atom feeds."""
    
    def __init__(self, output_dir: Path, max_docs_per_source: int = 500):
        self.output_dir = Path(output_dir)
        self.max_docs_per_source = max_docs_per_source
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.last_fetch: Dict[str, datetime] = {}
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "WillBreakerDelta/2.0 (Research Prototype; Contact: research@oddora.local)"
        })
    
    def fetch_feed(self, feed_url: str, source_name: str) -> List[Dict]:
        """Fetch a single RSS/Atom feed."""
        if feedparser:
            try:
                feed = feedparser.parse(feed_url)
                if feed.bozo != 0 and not getattr(feed, 'entries', None):
                    print(f"[WARN] Feed {source_name} parse error: {feed.bozo_exception}")
                    return self._fetch_feed_xml(feed_url, source_name)
                
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
            except Exception as e:
                print(f"[WARN] feedparser failed for {source_name}: {e}. Trying fallback.")
                return self._fetch_feed_xml(feed_url, source_name)
        else:
            return self._fetch_feed_xml(feed_url, source_name)
    
    def _fetch_feed_xml(self, feed_url: str, source_name: str) -> List[Dict]:
        """Native XML fallback for RSS/Atom parsing."""
        try:
            resp = self.session.get(feed_url, timeout=20)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
        except Exception as e:
            print(f"[ERROR] Failed to fetch/parse feed {source_name} ({feed_url}): {e}")
            return []
        
        documents = []
        # Check RSS <channel><item>
        items = root.findall(".//item")
        if items:
            for item in items[:self.max_docs_per_source]:
                title = item.findtext("title") or ""
                desc = item.findtext("description") or item.findtext("{http://purl.org/rss/1.0/modules/content/}encoded") or ""
                pub = item.findtext("pubDate") or ""
                link = item.findtext("link") or ""
                documents.append({
                    'source': source_name,
                    'title': title.strip(),
                    'content': desc.strip(),
                    'published': pub.strip(),
                    'link': link.strip(),
                    'fetched_at': datetime.now().isoformat()
                })
            return documents
        
        # Check Atom <entry>
        entries = root.findall(".//{http://www.w3.org/2005/Atom}entry") or root.findall(".//entry")
        for entry in entries[:self.max_docs_per_source]:
            title = entry.findtext("{http://www.w3.org/2005/Atom}title") or entry.findtext("title") or ""
            summary = entry.findtext("{http://www.w3.org/2005/Atom}summary") or entry.findtext("{http://www.w3.org/2005/Atom}content") or entry.findtext("summary") or ""
            published = entry.findtext("{http://www.w3.org/2005/Atom}published") or entry.findtext("{http://www.w3.org/2005/Atom}updated") or ""
            link_elem = entry.find("{http://www.w3.org/2005/Atom}link")
            link = link_elem.get("href", "") if link_elem is not None else ""
            documents.append({
                'source': source_name,
                'title': title.strip(),
                'content': summary.strip(),
                'published': published.strip(),
                'link': link.strip(),
                'fetched_at': datetime.now().isoformat()
            })
            
        return documents
    
    def save_documents(self, documents: List[Dict], source_name: str):
        """Save collected documents to corpus directory as JSONL."""
        if not documents:
            return
        
        output_file = self.output_dir / f"{source_name}.jsonl"
        with open(output_file, 'a', encoding='utf-8') as f:
            for doc in documents:
                f.write(json.dumps(doc, ensure_ascii=False) + '\n')
        
        print(f"[INFO] Saved {len(documents)} docs from {source_name}")
    
    def collect_all(self, sources: List[Dict]):
        """Collect from all configured sources."""
        for source in sources:
            url = source['url']
            name = source['name']
            
            print(f"[INFO] Fetching {name}...")
            docs = self.fetch_feed(url, name)
            self.save_documents(docs, name)
            time.sleep(1)
    
    def get_corpus_stats(self) -> Dict:
        """Get statistics about the built corpus."""
        stats = {}
        total_docs = 0
        
        for file in self.output_dir.glob('*.jsonl'):
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    count = sum(1 for line in f if line.strip())
                stats[file.stem] = count
                total_docs += count
            except Exception:
                pass
        
        stats['total'] = total_docs
        return stats


if __name__ == '__main__':
    sources = [
        {'name': 'nature_news', 'url': 'https://www.nature.com/nature.rss'},
        {'name': 'science_news', 'url': 'https://www.sciencemag.org/rss/news_current.xml'},
    ]
    
    base_dir = Path(__file__).parent.parent
    collector = RSSCollector(base_dir / 'corpus' / 'built')
    print("Testing RSS fallback collector...")
    docs = collector.fetch_feed('https://www.nature.com/nature.rss', 'nature_news')
    print(f"Fetched {len(docs)} docs from Nature RSS")
    if docs:
        print(f"Sample: {docs[0]['title']}")
