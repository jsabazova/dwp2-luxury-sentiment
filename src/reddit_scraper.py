"""
Reddit data collection via PRAW.

Usage:
    python src/reddit_scraper.py

Outputs one CSV per event to data/raw/reddit/{event_name}.csv

Notes on historical data:
- Reddit's search API is unreliable for posts older than ~6 months.
  For the Nov 2025 and Feb 2026 events, results may be incomplete.
  The scraper filters by UTC timestamp client-side to ensure date accuracy.
- Duplicate posts (same ID from multiple queries) are deduplicated.
- Rate limiting: PRAW handles this automatically, but large collections
  may take several minutes per event.
"""

import os
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

import praw
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

from utils import EVENT_DATES, SUBREDDITS, SEARCH_QUERIES, event_calendar_window

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
log = logging.getLogger(__name__)

RAW_DIR = Path(__file__).parent.parent / "data" / "raw" / "reddit"


def build_reddit_client() -> praw.Reddit:
    client_id     = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent    = os.getenv("REDDIT_USER_AGENT", "dwp2-sentiment/1.0")

    if not client_id or not client_secret:
        raise EnvironmentError(
            "REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set in .env"
        )

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


def _date_to_epoch(d) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())


def scrape_event(reddit: praw.Reddit, event_name: str, event_date,
                 window_days: int = 7, limit_per_query: int = 500) -> pd.DataFrame:
    """
    Scrape Reddit posts for a single event window.

    Returns a DataFrame of deduplicated posts within the date window.
    """
    start_date, end_date = event_calendar_window(event_date, window_days)
    start_epoch = _date_to_epoch(start_date)
    end_epoch   = _date_to_epoch(end_date)

    log.info(f"[{event_name}]  window {start_date} → {end_date}")

    all_posts: dict[str, dict] = {}  # keyed by post ID for deduplication

    for subreddit_name in tqdm(SUBREDDITS, desc=f"{event_name} subreddits"):
        subreddit = reddit.subreddit(subreddit_name)

        for query in SEARCH_QUERIES:
            try:
                # Pass before/after directly to Reddit API via params dict.
                # This is the most reliable way to get date-bounded results from PRAW.
                results = subreddit.search(
                    query,
                    sort="relevance",
                    time_filter="all",
                    limit=limit_per_query,
                    params={"before": end_epoch, "after": start_epoch},
                )

                for post in results:
                    if post.id in all_posts:
                        continue
                    created = post.created_utc
                    if not (start_epoch <= created <= end_epoch):
                        continue  # client-side date guard

                    all_posts[post.id] = {
                        "id":            post.id,
                        "subreddit":     subreddit_name,
                        "title":         post.title,
                        "text":          post.selftext or "",
                        "score":         post.score,
                        "num_comments":  post.num_comments,
                        "created_utc":   created,
                        "query":         query,
                        "event":         event_name,
                    }

            except Exception as e:
                log.warning(f"  Error on r/{subreddit_name} query='{query}': {e}")
                time.sleep(2)

    if not all_posts:
        log.warning(f"[{event_name}]  No posts found — check credentials or date range")
        return pd.DataFrame()

    df = pd.DataFrame(all_posts.values())
    df["date"] = pd.to_datetime(df["created_utc"], unit="s", utc=True).dt.date
    df["combined_text"] = df["title"] + " " + df["text"]
    df["combined_text"] = df["combined_text"].str.strip()

    log.info(f"[{event_name}]  {len(df)} unique posts collected")
    return df


def run_all():
    reddit = build_reddit_client()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for event_name, event_date in EVENT_DATES.items():
        out_path = RAW_DIR / f"{event_name}.csv"

        if out_path.exists():
            log.info(f"[{event_name}]  Already collected — skipping (delete file to re-run)")
            continue

        df = scrape_event(reddit, event_name, event_date)

        if not df.empty:
            df.to_csv(out_path, index=False)
            log.info(f"[{event_name}]  Saved to {out_path}")
        else:
            log.warning(f"[{event_name}]  Empty result — no file written")


if __name__ == "__main__":
    run_all()
