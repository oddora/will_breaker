#!/usr/bin/env python3
"""
Will Breaker Delta-Detection — Corpus Expansion Orchestrator
Runs all scrapers to build 50K document corpus.

Usage:
    python collect_all.py [--target 50000] [--dry-run]
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


# Source configuration: (name, script, args, target_docs)
SOURCES = [
    # Reddit (high signal for shifting discourse)
    ("reddit_consciousness", "reddit_archiver.py", "--subreddit consciousness", 5000),
    ("reddit_futurology", "reddit_archiver.py", "--subreddit Futurology", 5000),
    ("reddit_precognition", "reddit_archiver.py", "--subreddit precognition", 3000),
    ("reddit_spirituality", "reddit_archiver.py", "--subreddit spirituality", 3000),
    
    # arXiv (academic papers)
    ("arxiv_quant-ph", "arxiv_collector.py", "--category quant-ph", 5000),
    ("arxiv_cs.AI", "arxiv_collector.py", "--category cs.AI", 5000),
    ("arxiv_q-bio.NC", "arxiv_collector.py", "--category q-bio.NC", 3000),
    
    # PubMed (consciousness research)
    ("pubmed_consciousness", "pubmed_collector.py", "--query consciousness", 5000),
    ("pubmed_quantum", "pubmed_collector.py", "--query quantum consciousness", 3000),
    
    # Semantic Scholar (cross-disciplinary)
    ("ss_consciousness", "semantic_scholar.py", "--query consciousness", 3000),
    ("ss_quantum_cognition", "semantic_scholar.py", "--query quantum cognition", 2000),
    
    # Will Breaker internal (direct correlation target)
    ("will_breaker_research", "internal_collector.py", "", 2000),
    ("will_breaker_protocols", "internal_collector.py", "", 1000),
    ("will_breaker_sessions", "internal_collector.py", "", 1000),
]


def run_scraper(name, script, args, output_dir):
    """Run a single scraper and return doc count."""
    script_path = Path(__file__).parent / script
    output_file = output_dir / f"{name}.txt"
    
    cmd = [sys.executable, str(script_path), "--max-docs", str(5000), "--output", str(output_file)]
    if args:
        cmd.extend(args.split())
    
    print(f"[RUN] {name}: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        print(f"[OUT] {name}: {result.stdout[-200:] if result.stdout else 'no output'}")
        if result.stderr:
            print(f"[ERR] {name}: {result.stderr[-200:]}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {name}")
        return False
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        return False


def collect_internal(source_name, output_dir, max_docs):
    """Collect Will Breaker internal documents (research, protocols, sessions)."""
    wb_dir = Path(__file__).parent.parent.parent
    docs = []
    
    # Collect research papers
    for f in (wb_dir / "research").glob("*.md"):
        content = f.read_text(encoding="utf-8")
        docs.append({
            "id": f"wb_{source_name}_{len(docs)}",
            "source": source_name,
            "title": f.name,
            "content": content,
            "type": "research"
        })
    
    # Collect protocols
    for f in (wb_dir / "protocols").glob("*.md"):
        content = f.read_text(encoding="utf-8")
        docs.append({
            "id": f"wb_{source_name}_{len(docs)}",
            "source": source_name,
            "title": f.name,
            "content": content,
            "type": "protocol"
        })
    
    # Collect session logs
    for f in (wb_dir / "sessions").glob("session-*.md"):
        content = f.read_text(encoding="utf-8")
        docs.append({
            "id": f"wb_{source_name}_{len(docs)}",
            "source": source_name,
            "title": f.name,
            "content": content,
            "type": "session"
        })
    
    # Write as JSONL
    output_file = output_dir / f"{source_name}.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for doc in docs[:max_docs]:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    
    print(f"[INTERNAL] {source_name}: {min(len(docs), max_docs)} documents")
    return min(len(docs), max_docs)


def main():
    parser = argparse.ArgumentParser(description="Build 50K corpus for delta-detection")
    parser.add_argument("--target", "-t", type=int, default=50000, help="Target corpus size")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be collected")
    parser.add_argument("--output-dir", "-o", default="../corpus/built", help="Output directory")
    args = parser.parse_args()
    
    output_dir = Path(__file__).parent.parent / args.output_dir.lstrip("/")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.dry_run:
        print("[DRY RUN] Corpus expansion plan:")
        total = 0
        for name, script, cmd_args, target in SOURCES:
            print(f"  {name}: {target} docs ({script})")
            total += target
        print(f"\nTotal target: {total} documents")
        return
    
    print(f"Building corpus: target {args.target} documents")
    print(f"Output directory: {output_dir}")
    print("=" * 60)
    
    total_docs = 0
    for name, script, cmd_args, target in SOURCES:
        if total_docs >= args.target:
            print(f"[SKIP] {name}: target reached ({total_docs}/{args.target})")
            continue
        
        remaining = args.target - total_docs
        
        if "internal" in script:
            count = collect_internal(name, output_dir, remaining)
        else:
            success = run_scraper(name, script, cmd_args, output_dir)
            count = remaining if success else 0
        
        total_docs += count
        print(f"[PROGRESS] {total_docs}/{args.target} documents collected")
        print("-" * 60)
    
    print(f"\n[COMPLETE] Corpus built: {total_docs} documents")
    print(f"Location: {output_dir}")
    
    # List generated files
    print("\n[FILES]")
    for f in sorted(output_dir.glob("*")):
        size = f.stat().st_size / 1024 / 1024
        print(f"  {f.name}: {size:.1f} MB")


if __name__ == "__main__":
    main()
