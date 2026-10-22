#!/usr/bin/env python3
"""
Will Breaker Delta-Detection — Semantic Scholar API Collector
Collects paper metadata and abstracts from Semantic Scholar for corpus expansion (10K → 50K)

Usage:
    python semantic_scholar.py --query "consciousness" --max-docs 3000 --output ../corpus/built/ss_consciousness.txt
    python semantic_scholar.py --query "quantum cognition" --max-docs 2000 --output ../corpus/built/ss_quantum-cognition.txt
"""

import argparse
import requests
import time


class SemanticScholarCollector:
    """Collect papers from Semantic Scholar API."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

    def __init__(self, api_key=None, delay=1.0):
        self.delay = delay
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def collect(self, query, max_docs, output_file):
        """Collect papers from Semantic Scholar."""
        offset = 0
        batch_size = 100
        docs_collected = 0

        print(f"Collecting papers from Semantic Scholar for query '{query}'")
        print(f"Target: {max_docs} documents")
        print(f"Output: {output_file}")
        print("-" * 60)

        with open(output_file, "w", encoding="utf-8") as f:
            while docs_collected < max_docs:
                params = {
                    "query": query,
                    "limit": batch_size,
                    "offset": offset,
                    "fields": "title,abstract,year,authors,journal,citationCount,referenceCount",
                }

                try:
                    resp = self.session.get(self.BASE_URL, params=params, timeout=30)
                    resp.raise_for_status()
                except requests.RequestException as e:
                    print(f"Request error at offset={offset}: {e}")
                    time.sleep(self.delay * 3)
                    continue

                data = resp.json()
                papers = data.get("data", [])

                if not papers:
                    print(f"No more papers. Done.")
                    break

                for paper in papers:
                    if docs_collected >= max_docs:
                        break

                    title = paper.get("title", "")
                    abstract = paper.get("abstract", "") or ""
                    year = paper.get("year", "")
                    authors = [a.get("name", "") for a in paper.get("authors", [])]
                    journal = paper.get("journal", {}).get("name", "") if paper.get("journal") else ""
                    citations = paper.get("citationCount", 0)
                    paper_id = paper.get("paperId", "")

                    # Skip papers without abstracts (low quality)
                    if not abstract or len(abstract) < 100:
                        continue

                    doc = f"""DOCUMENT
ID: ss_{paper_id}
SOURCE: semantic_scholar
TITLE: {title}
AUTHORS: {', '.join(authors)}
JOURNAL: {journal}
YEAR: {year}
CITATIONS: {citations}
ABSTRACT: {abstract}
---
"""
                    f.write(doc)
                    docs_collected += 1

                    if docs_collected % 500 == 0:
                        print(f"  Collected {docs_collected}/{max_docs} documents...")

                offset += batch_size
                time.sleep(self.delay)

        print(f"Done. Collected {docs_collected} documents.")
        return docs_collected


def main():
    parser = argparse.ArgumentParser(description="Collect papers from Semantic Scholar for delta-detection corpus")
    parser.add_argument("--query", "-q", required=True, help="Semantic Scholar search query")
    parser.add_argument("--max-docs", "-m", type=int, default=3000, help="Maximum documents to collect")
    parser.add_argument("--output", "-o", default="../corpus/built/ss_{query}.txt", help="Output file path")
    parser.add_argument("--delay", "-d", type=float, default=1.0, help="Delay between requests (seconds)")
    parser.add_argument("--api-key", "-k", default=None, help="Semantic Scholar API key (optional)")

    args = parser.parse_args()

    collector = SemanticScholarCollector(api_key=args.api_key, delay=args.delay)
    output_file = args.output.format(query=args.query.replace(" ", "-"))

    collector.collect(args.query, args.max_docs, output_file)


if __name__ == "__main__":
    main()
