#!/usr/bin/env python3
"""
Will Breaker Delta-Detection — Reddit Historical Archive Collector
Collects Reddit posts for corpus expansion (10K → 50K)

Usage:
    python reddit_archiver.py --subreddit consciousness --max-docs 5000 --output ../corpus/built/reddit_consciousness.txt
    python reddit_archiver.py --subreddit Futurology --max-docs 5000 --output ../corpus/built/reddit_futurology.txt
"""

import argparse
import requests
import time
from pathlib import Path


class RedditArchiver:
    """Collect Reddit posts for delta-detection corpus."""

    BASE_URL = "https://www.reddit.com/r/{}/{}.json"

    def __init__(self, user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 WillBreaker/1.0", delay=1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
        })

    def collect(self, subreddit, max_docs, output_file):
        """Collect posts from Reddit subreddit."""
        after_token = None
        docs_collected = 0

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Collecting Reddit posts from r/{subreddit}")
        print(f"Target: {max_docs} documents")
        print(f"Output: {output_file}")
        print("-" * 60)

        with open(output_path, "w", encoding="utf-8") as f:
            while docs_collected < max_docs:
                url = self.BASE_URL.format(subreddit, "hot")
                params = {
                    "limit": min(100, max_docs - docs_collected),
                }
                if after_token:
                    params["after"] = after_token

                try:
                    resp = self.session.get(url, params=params, timeout=30)
                    resp.raise_for_status()
                except requests.RequestException as e:
                    print(f"Request error for r/{subreddit}: {e}")
                    time.sleep(self.delay * 3)
                    break

                try:
                    data = resp.json()
                except Exception as e:
                    print(f"JSON decode error: {e}")
                    break

                data_node = data.get("data", {})
                children = data_node.get("children", [])
                after_token = data_node.get("after")

                if not children:
                    print(f"No more posts. Done.")
                    break

                for child in children:
                    if docs_collected >= max_docs:
                        break

                    post = child.get("data", {})
                    title = post.get("title", "")
                    selftext = post.get("selftext", "")
                    created_utc = post.get("created_utc", 0)
                    score = post.get("score", 0)
                    num_comments = post.get("num_comments", 0)
                    sub_name = post.get("subreddit", subreddit)

                    # Combine title and body as document text
                    text = f"{title}\n\n{selftext}" if selftext else title

                    doc = f"""DOCUMENT
ID: reddit_{sub_name}_{docs_collected}
SOURCE: reddit
SUBREDDIT: {sub_name}
TITLE: {title}
SCORE: {score}
COMMENTS: {num_comments}
CREATED: {created_utc}
TEXT: {text}
---
"""
                    f.write(doc)
                    docs_collected += 1

                    if docs_collected % 500 == 0:
                        print(f"  Collected {docs_collected}/{max_docs} documents...")

                if not after_token:
                    break

                time.sleep(self.delay)

        print(f"Done. Collected {docs_collected} documents.")
        return docs_collected


def main():
    parser = argparse.ArgumentParser(description="Collect Reddit posts for delta-detection corpus")
    parser.add_argument("--subreddit", "-s", required=True, help="Reddit subreddit name")
    parser.add_argument("--max-docs", "-m", type=int, default=5000, help="Maximum documents to collect")
    parser.add_argument("--output", "-o", default="../corpus/built/reddit_{subreddit}.txt", help="Output file path")
    parser.add_argument("--delay", "-d", type=float, default=1.0, help="Delay between requests (seconds)")

    args = parser.parse_args()

    archiver = RedditArchiver(delay=args.delay)
    if "{subreddit}" in args.output:
        output_file = args.output.format(subreddit=args.subreddit)
    else:
        output_file = args.output

    archiver.collect(args.subreddit, args.max_docs, output_file)


if __name__ == "__main__":
    main()
