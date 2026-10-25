#!/usr/bin/env python3
"""
Will Breaker Delta-Detection — arXiv Paper Collector
Collects papers from arXiv for corpus expansion (10K → 50K)

Usage:
    python arxiv_collector.py --category quant-ph --max-docs 5000 --output ../corpus/built/arxiv_quant-ph.txt
    python arxiv_collector.py --category cs.AI --max-docs 5000 --output ../corpus/built/arxiv_cs-AI.txt
    python arxiv_collector.py --category q-bio.NC --max-docs 3000 --output ../corpus/built/arxiv_q-bio-NC.txt
"""

import argparse
import requests
import time
import xml.etree.ElementTree as ET
from pathlib import Path


class ArxivCollector:
    """Collect papers from arXiv for delta-detection corpus."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, delay=1.0):
        self.delay = delay
        self.session = requests.Session()

    def collect(self, category, max_docs, output_file):
        """Collect papers from arXiv category."""
        query = f"cat:{category}"
        start = 0
        batch_size = 100
        docs_collected = 0

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Collecting arXiv papers from category '{category}'")
        print(f"Target: {max_docs} documents")
        print(f"Output: {output_file}")
        print("-" * 60)

        with open(output_path, "w", encoding="utf-8") as f:
            while docs_collected < max_docs:
                current_batch = min(batch_size, max_docs - docs_collected)
                params = {
                    "search_query": query,
                    "start": start,
                    "max_results": current_batch,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                }

                try:
                    resp = self.session.get(self.BASE_URL, params=params, timeout=30)
                    resp.raise_for_status()
                except requests.RequestException as e:
                    print(f"Request error at start={start}: {e}")
                    time.sleep(self.delay * 3)
                    continue

                root = ET.fromstring(resp.content)
                entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")

                if not entries:
                    print(f"No more entries at start={start}. Done.")
                    break

                for entry in entries:
                    if docs_collected >= max_docs:
                        break

                    title = self._get_text(entry, "title")
                    summary = self._get_text(entry, "summary")
                    published = self._get_text(entry, "published")
                    
                    authors = []
                    for a in entry.findall(".//{http://www.w3.org/2005/Atom}author"):
                        name_elem = a.find("{http://www.w3.org/2005/Atom}name")
                        if name_elem is not None and name_elem.text:
                            authors.append(name_elem.text.strip())

                    doc = f"""DOCUMENT
ID: arxiv_{category}_{docs_collected}
SOURCE: arxiv
CATEGORY: {category}
TITLE: {title}
AUTHORS: {', '.join(authors)}
PUBLISHED: {published}
TEXT: {summary}
---
"""
                    f.write(doc)
                    docs_collected += 1

                    if docs_collected % 500 == 0:
                        print(f"  Collected {docs_collected}/{max_docs} documents...")

                start += len(entries)
                time.sleep(self.delay)

        print(f"Done. Collected {docs_collected} documents.")
        return docs_collected

    def _get_text(self, entry, tag):
        """Extract text from an Atom entry element."""
        elem = entry.find(f".//{{http://www.w3.org/2005/Atom}}{tag}")
        return elem.text.strip() if elem is not None and elem.text else ""


def main():
    parser = argparse.ArgumentParser(description="Collect arXiv papers for delta-detection corpus")
    parser.add_argument("--category", "-c", required=True, help="arXiv category (e.g., quant-ph, cs.AI, q-bio.NC)")
    parser.add_argument("--max-docs", "-m", type=int, default=5000, help="Maximum documents to collect")
    parser.add_argument("--output", "-o", default="../corpus/built/arxiv_{category}.txt", help="Output file path")
    parser.add_argument("--delay", "-d", type=float, default=1.0, help="Delay between requests (seconds)")

    args = parser.parse_args()

    collector = ArxivCollector(delay=args.delay)
    if "{category}" in args.output:
        output_file = args.output.format(category=args.category.replace(".", "-"))
    else:
        output_file = args.output

    collector.collect(args.category, args.max_docs, output_file)


if __name__ == "__main__":
    main()
