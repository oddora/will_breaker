#!/usr/bin/env python3
"""
Will Breaker Delta-Detection — PubMed Abstract Collector
Collects PubMed abstracts for corpus expansion (10K → 50K)

Usage:
    python pubmed_collector.py --query consciousness --max-docs 5000 --output ../corpus/built/pubmed_consciousness.txt
    python pubmed_collector.py --query "quantum consciousness" --max-docs 3000 --output ../corpus/built/pubmed_quantum-consciousness.txt
"""

import argparse
import requests
import time
import xml.etree.ElementTree as ET
from pathlib import Path


class PubMedCollector:
    """Collect PubMed abstracts for delta-detection corpus."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    def __init__(self, delay=1.0):
        self.delay = delay
        self.session = requests.Session()

    def collect(self, query, max_docs, output_file):
        """Collect PubMed abstracts."""
        docs_collected = 0

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Collecting PubMed abstracts for query '{query}'")
        print(f"Target: {max_docs} documents")
        print(f"Output: {output_file}")
        print("-" * 60)

        # Step 1: Search for IDs
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_docs,
            "sort": "relevance",
            "retmode": "xml",
        }

        try:
            resp = self.session.get(self.BASE_URL, params=search_params, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Search error: {e}")
            return 0

        root = ET.fromstring(resp.content)
        id_list = root.findall(".//Id")
        all_ids = [id_elem.text for id_elem in id_list if id_elem.text]

        print(f"Found {len(all_ids)} matching articles. Fetching abstracts...")

        # Step 2: Fetch abstracts in batches
        batch_size = 200
        with open(output_path, "w", encoding="utf-8") as f:
            for i in range(0, min(len(all_ids), max_docs), batch_size):
                batch = all_ids[i:i + batch_size]
                batch_num = i // batch_size + 1

                fetch_params = {
                    "db": "pubmed",
                    "id": ",".join(batch),
                    "retmode": "xml",
                    "rettype": "abstract",
                }

                try:
                    resp = self.session.get(self.FETCH_URL, params=fetch_params, timeout=30)
                    resp.raise_for_status()
                except requests.RequestException as e:
                    print(f"Fetch error at batch {batch_num}: {e}")
                    time.sleep(self.delay * 3)
                    continue

                articles = ET.fromstring(resp.content).findall(".//PubmedArticle")

                for article in articles:
                    if docs_collected >= max_docs:
                        break

                    article_id = self._get_text(article, "PMID")
                    title = self._get_text(article, "ArticleTitle")
                    
                    authors = []
                    for a in article.findall(".//Author"):
                        last = a.findtext("LastName") or ""
                        fore = a.findtext("ForeName") or a.findtext("Initials") or ""
                        full = f"{fore} {last}".strip()
                        if full:
                            authors.append(full)
                            
                    journal = self._get_text(article, "Source") or self._get_text(article, "Title")
                    year = self._get_text(article, "PubDate/Year") or self._get_text(article, "DateRevised/Year")
                    abstract_elem = article.find(".//AbstractText")
                    abstract = abstract_elem.text if abstract_elem is not None and abstract_elem.text else ""

                    doc = f"""DOCUMENT
ID: pubmed_{article_id}
SOURCE: pubmed
TITLE: {title}
AUTHORS: {', '.join(authors)}
JOURNAL: {journal}
YEAR: {year}
ABSTRACT: {abstract}
---
"""
                    f.write(doc)
                    docs_collected += 1

                    if docs_collected % 500 == 0:
                        print(f"  Collected {docs_collected}/{max_docs} documents...")

                time.sleep(self.delay)

        print(f"Done. Collected {docs_collected} documents.")
        return docs_collected

    def _get_text(self, parent, path):
        """Extract text from XML element using relative path."""
        elem = parent.find(f".//{path}")
        return elem.text.strip() if elem is not None and elem.text else ""


def main():
    parser = argparse.ArgumentParser(description="Collect PubMed abstracts for delta-detection corpus")
    parser.add_argument("--query", "-q", required=True, help="PubMed search query")
    parser.add_argument("--max-docs", "-m", type=int, default=5000, help="Maximum documents to collect")
    parser.add_argument("--output", "-o", default="../corpus/built/pubmed_{query}.txt", help="Output file path")
    parser.add_argument("--delay", "-d", type=float, default=1.0, help="Delay between requests (seconds)")

    args = parser.parse_args()

    collector = PubMedCollector(delay=args.delay)
    if "{query}" in args.output:
        output_file = args.output.format(query=args.query.replace(" ", "-"))
    else:
        output_file = args.output

    collector.collect(args.query, args.max_docs, output_file)


if __name__ == "__main__":
    main()
