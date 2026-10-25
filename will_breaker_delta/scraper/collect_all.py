#!/usr/bin/env python3
"""
Will Breaker Delta-Detection — Corpus Expansion Orchestrator
Runs all scrapers to build up to target document corpus.

Usage:
    python collect_all.py [--target 50000] [--dry-run]
"""

import argparse
import json
import os
import re
import shlex
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
    ("arxiv_quant_ph", "arxiv_collector.py", "--category quant-ph", 5000),
    ("arxiv_cs_AI", "arxiv_collector.py", "--category cs.AI", 5000),
    ("arxiv_q_bio_NC", "arxiv_collector.py", "--category q-bio.NC", 3000),
    
    # PubMed (consciousness research)
    ("pubmed_consciousness", "pubmed_collector.py", "--query consciousness", 5000),
    ("pubmed_quantum", "pubmed_collector.py", "--query quantum consciousness", 3000),
    
    # Semantic Scholar (cross-disciplinary)
    ("ss_consciousness", "semantic_scholar.py", "--query consciousness", 3000),
    ("ss_quantum_cognition", "semantic_scholar.py", '--query "quantum cognition"', 2000),
    
    # Will Breaker internal (direct correlation target)
    ("will_breaker_research", "internal_collector.py", "--source research", 2000),
    ("will_breaker_protocols", "internal_collector.py", "--source protocols", 1000),
    ("will_breaker_sessions", "internal_collector.py", "--source sessions", 1000),
]


def count_docs_in_file(file_path: Path) -> int:
    """Accurately count documents in a jsonl or txt corpus file."""
    if not file_path.exists():
        return 0
    try:
        if file_path.suffix == '.jsonl':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for line in f if line.strip())
        elif file_path.suffix == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if "DOCUMENT" in content:
                count = len(re.findall(r"^DOCUMENT\b", content, re.MULTILINE))
                return count if count > 0 else len([d for d in content.split("---") if d.strip()])
            else:
                return sum(1 for line in content.splitlines() if line.strip())
    except Exception:
        pass
    return 0


def run_scraper(name, script, args, output_dir, max_docs):
    """Run a single scraper and return actual docs added."""
    script_path = Path(__file__).parent / script
    is_jsonl = "internal" in script
    output_file = output_dir / f"{name}.{'jsonl' if is_jsonl else 'txt'}"
    
    prev_docs = count_docs_in_file(output_file)
    cmd = [sys.executable, str(script_path), "--max-docs", str(max_docs), "--output", str(output_file)]
    if args:
        cmd.extend(shlex.split(args))
    
    print(f"[RUN] {name}: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.stdout:
            print(f"[OUT] {name}: {result.stdout[-200:].strip()}")
        if result.stderr:
            print(f"[ERR] {name}: {result.stderr[-200:].strip()}")
        
        new_docs = count_docs_in_file(output_file)
        added = max(0, new_docs - prev_docs)
        return added
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {name}")
        return 0
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        return 0


def collect_internal(source_name, output_dir, max_docs):
    """Collect Will Breaker internal documents specific to source_name."""
    wb_dir = Path(__file__).parent.parent.parent
    docs = []
    
    if "research" in source_name:
        for f in sorted((wb_dir / "research").glob("*.md")):
            content = f.read_text(encoding="utf-8", errors="ignore")
            docs.append({
                "id": f"wb_research_{len(docs)}",
                "source": "research",
                "title": f.name,
                "content": content,
                "type": "research"
            })
    elif "protocols" in source_name:
        for f in sorted((wb_dir / "protocols").glob("*.md")):
            content = f.read_text(encoding="utf-8", errors="ignore")
            docs.append({
                "id": f"wb_protocol_{len(docs)}",
                "source": "protocols",
                "title": f.name,
                "content": content,
                "type": "protocol"
            })
    elif "sessions" in source_name:
        for f in sorted((wb_dir / "sessions").glob("session-*.md")):
            content = f.read_text(encoding="utf-8", errors="ignore")
            docs.append({
                "id": f"wb_session_{len(docs)}",
                "source": "sessions",
                "title": f.name,
                "content": content,
                "type": "session"
            })
    
    output_file = output_dir / f"{source_name}.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for doc in docs[:max_docs]:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    
    count = min(len(docs), max_docs)
    print(f"[INTERNAL] {source_name}: {count} documents written to {output_file.name}")
    return count


def main():
    parser = argparse.ArgumentParser(description="Build corpus for delta-detection")
    parser.add_argument("--target", "-t", type=int, default=50000, help="Target corpus size")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be collected")
    parser.add_argument("--output-dir", "-o", default="../corpus/built", help="Output directory")
    args = parser.parse_args()
    
    # Resolve output_dir relative to scraper directory
    if Path(args.output_dir).is_absolute():
        output_dir = Path(args.output_dir)
    else:
        output_dir = (Path(__file__).parent / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.dry_run:
        print("[DRY RUN] Corpus expansion plan:")
        total = 0
        for name, script, cmd_args, target in SOURCES:
            print(f"  {name}: {target} docs ({script} {cmd_args})")
            total += target
        print(f"\nTotal target: {total} documents")
        print(f"Output directory: {output_dir}")
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
        collect_target = min(target, remaining)
        
        if "internal" in script:
            count = collect_internal(name, output_dir, collect_target)
        else:
            count = run_scraper(name, script, cmd_args, output_dir, collect_target)
        
        total_docs += count
        print(f"[PROGRESS] {total_docs}/{args.target} documents collected (+{count} from {name})")
        print("-" * 60)
    
    print(f"\n[COMPLETE] Corpus built: {total_docs} documents")
    print(f"Location: {output_dir}")


if __name__ == "__main__":
    main()
