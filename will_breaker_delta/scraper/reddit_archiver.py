#!/usr/bin/env python3
"""
Will Breaker Delta-Detection — Reddit Historical Archive Collector
Collects historical Reddit posts for corpus expansion (10K → 50K)

Usage:
    python reddit_archiver.py --subreddit consciousness --max-docs 5000 --output ../corpus/built/reddit_consciousness.txt
    python reddit_archiver.py --subreddit Futurology --max-docs 5000 --output ../corpus/built/reddit_futurology.txt
"""

import argparse
import requests
import time
import json


class RedditArchiver:
    """Collect historical Reddit posts for delta-detection corpus."""

    BASE_URL = "https://www.reddit.com/r/{}/{}.json"

    def __init__(self, user_agent="WillBreakerDelta/1.0", delay=1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
        })

    def collect(self, subreddit, max_docs, output_file):
        """Collect posts from Reddit subreddit."""
        start = 0
        docs_collected = 0

        print(f"Collecting Reddit posts from r/{subreddit}")
        print(f"Target: {max_docs} documents")
        print(f"Output: {output_file}")
        print("-" * 60)

        with open(output_file, "w", encoding="utf-8") as f:
            while docs_collected < max_docs:
                url = self.BASE_URL.format(subreddit, "all")
                params = {
                    "limit": 100,
                    "after": f"_t3_{start}" if start else None,
                }
                params = {k: v for k, v in params.items() if v is not None}

                try:
                    resp = self.session.get(url, params=params, timeout=30)
                    resp.raise_for_status()
                except requests.RequestException as e:
                    print(f"Request error at start={start}: {e}")
                    time.sleep(self.delay * 3)
                    continue

                data = resp.json()
                children = data.get("data", {}).get("children", [])

                if not children:
                    print(f"No more posts. Done.")
                    break

                for child in children:
                    if docs_collected >= max_docs:
                        break

                    post = child["data"]
                    title = post.get("title", "")
                    selftext = post.get("selftext", "")
                    created_utc = post.get("created_utc", 0)
                    score = post.get("score", 0)
                    num_comments = post.get("num_comments", 0)
                    url = post.get("url", "")
                    subreddit = post.get("subreddit", "")

                    # Combine title and body as document text
                    text = f"{title}\n\n{selftext}" if selftext else title

                    doc = f"""DOCUMENT
ID: reddit_{subreddit}_{docs_collected}
SOURCE: reddit
SUBREDDIT: {subreddit}
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

                    start = post.get("id", "")

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
    output_file = args.output.format(subreddit=args.subreddit)

    archiver.collect(args.subreddit, args.max_docs, output_file)


if __name__ == "__main__":
    main()
