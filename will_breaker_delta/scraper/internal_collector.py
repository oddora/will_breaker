#!/usr/bin/env python3
"""
Will Breaker Delta-Detection — Internal Document Collector
Collects Will Breaker research, protocols, and session logs for corpus expansion.

Usage:
    python internal_collector.py --source research --max-docs 2000 --output ../corpus/built/will_breaker_research.jsonl
    python internal_collector.py --source protocols --max-docs 1000 --output ../corpus/built/will_breaker_protocols.jsonl
    python internal_collector.py --source sessions --max-docs 1000 --output ../corpus/built/will_breaker_sessions.jsonl
"""

import argparse
import json
from pathlib import Path


class InternalCollector:
    """Collect Will Breaker internal documents for delta-detection corpus."""

    def __init__(self, wb_dir, delay=0.1):
        self.wb_dir = Path(wb_dir)
        self.delay = delay

    def collect(self, source_type, max_docs, output_file):
        """Collect documents of a specific type."""
        docs = []

        print(f"Collecting Will Breaker {source_type} documents")
        print(f"Target: {max_docs} documents")
        print(f"Output: {output_file}")
        print("-" * 60)

        # Collect based on source type
        if source_type == "research":
            pattern = "research/*.md"
        elif source_type == "protocols":
            pattern = "protocols/*.md"
        elif source_type == "sessions":
            pattern = "sessions/session-*.md"
        else:
            print(f"Unknown source type: {source_type}")
            return 0

        for f in self.wb_dir.glob(pattern):
            if len(docs) >= max_docs:
                break

            content = f.read_text(encoding="utf-8")
            doc = {
                "id": f"wb_{source_type}_{len(docs)}",
                "source": source_type,
                "title": f.name,
                "content": content,
                "type": source_type,
                "path": str(f.relative_to(self.wb_dir)),
                "size": len(content),
                "word_count": len(content.split())
            }
            docs.append(doc)

            if len(docs) % 10 == 0:
                print(f"  Collected {len(docs)}/{max_docs} documents...")

        # Write as JSONL
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for doc in docs:
                f.write(json.dumps(doc, ensure_ascii=False) + "\n")

        print(f"Done. Collected {len(docs)} documents.")
        print(f"\n[STATS]")
        for doc in docs[:5]:
            print(f"  {doc['title']}: {doc['word_count']} words")
        if len(docs) > 5:
            print(f"  ... and {len(docs) - 5} more")

        return len(docs)


def main():
    parser = argparse.ArgumentParser(description="Collect Will Breaker internal documents for delta-detection corpus")
    parser.add_argument("--source", "-s", required=True, choices=["research", "protocols", "sessions"],
                        help="Document source type")
    parser.add_argument("--max-docs", "-m", type=int, default=2000, help="Maximum documents to collect")
    parser.add_argument("--output", "-o", required=True, help="Output file path")
    parser.add_argument("--wb-dir", "-d", default="..", help="Will Breaker project directory")

    args = parser.parse_args()

    collector = InternalCollector(wb_dir=args.wb_dir)
    collector.collect(args.source, args.max_docs, args.output)


if __name__ == "__main__":
    main()
