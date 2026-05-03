"""
Reddit data collection using Reddit's public JSON API.
No credentials or registration required.

Usage:
    python src/reddit_scraper.py

Outputs one CSV per event to data/raw/reddit/{event_name}.csv

How it works:
    Reddit exposes a public JSON endpoint at:
        https://www.reddit.com/r/{subreddit}/search.json
    This works without authentication for read-only searches.
    We paginate through results, filter by UTC timestamp client-side,
    and deduplicate across queries by post ID.

Rate limiting:
    Reddit allows ~1 request/second for unauthenticated requests.
    We use a 1.1s delay between requests to stay well within limits.

Notes on historical data:
    For events from Nov 2025 and Feb 2026, Reddit's search index
    may not return all posts — search coverage degrades for older content.
    Apr/May 2026 events will have the most complete coverage.
"""

from __future__ import annotations

import time
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests
import pandas as pd

from utils import EVENT_DATES, SUBREDDITS, EVENT_QUERY_MAP, event_calendar_window

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
log = logging.getLogger(__name__)

RAW_DIR    = Path(__file__).parent.parent / "data" / "raw" / "reddit"
BASE_URL   = "https://www.reddit.com"
HEADERS    = {"User-Agent": "dwp2-luxury-sentiment-research/1.0 (academic project)"}
DELAY      = 1.1   # seconds between requests
MAX_PAGES  = 10    # max pagination depth per query (100 posts/page = 1000 posts max)


def _epoch(d) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())


def fetch_page(subreddit: str, query: str, after_token: str | None,
               start_epoch: int, end_epoch: int) -> tuple[list[dict], str | None]:
    """
    Fetch one page of search results from Reddit's public JSON API.
    Returns (list_of_post_dicts, next_page_token_or_None).
    """
    params = {
        "q":           query,
        "sort":        "new",
        "t":           "all",
        "limit":       100,
        "restrict_sr": 1,
        "type":        "link",
    }
    if after_token:
        params["after"] = after_token

    url = f"{BASE_URL}/r/{subreddit}/search.json"

    for attempt in range(4):
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
            if resp.status_code == 429:
                wait = 30 * (2 ** attempt)  # 30s, 60s, 120s, 240s
                log.warning(f"    Rate limited — waiting {wait}s before retry")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            break
        except requests.RequestException as e:
            log.warning(f"    Request failed: {e}")
            return [], None
    else:
        log.warning("    Max retries hit, skipping this query")
        return [], None

    data = resp.json().get("data", {})
    children = data.get("children", [])
    next_token = data.get("after")  # None if no more pages

    posts = []
    stop_early = False

    for child in children:
        post = child.get("data", {})
        created = post.get("created_utc", 0)

        # Posts come newest-first (sort=new). Once we go past the window, stop.
        if created < start_epoch:
            stop_early = True
            break

        # Skip posts outside our date window
        if created > end_epoch:
            continue

        posts.append({
            "id":           post.get("id", ""),
            "subreddit":    subreddit,
            "title":        post.get("title", ""),
            "text":         post.get("selftext", "") or "",
            "score":        post.get("score", 0),
            "num_comments": post.get("num_comments", 0),
            "created_utc":  created,
            "query":        query,
        })

    if stop_early:
        next_token = None  # don't paginate further, we've passed the window

    return posts, next_token


def scrape_subreddit_query(subreddit: str, query: str,
                            start_epoch: int, end_epoch: int) -> list[dict]:
    """Paginate through all results for one subreddit × query combination."""
    all_posts = []
    after_token = None

    for page in range(MAX_PAGES):
        posts, after_token = fetch_page(subreddit, query, after_token, start_epoch, end_epoch)
        all_posts.extend(posts)
        time.sleep(DELAY)

        if not after_token or not posts:
            break

        log.debug(f"      page {page + 2}, {len(all_posts)} posts so far")

    return all_posts


def scrape_event(event_name: str, event_date, window_days: int = 7) -> pd.DataFrame:
    start_date, end_date = event_calendar_window(event_date, window_days)
    start_epoch = _epoch(start_date)
    end_epoch   = _epoch(end_date)

    log.info(f"[{event_name}]  {start_date} → {end_date}")

    seen_ids: set[str] = set()
    all_posts: list[dict] = []

    queries = EVENT_QUERY_MAP.get(event_name, list(EVENT_QUERY_MAP.values())[0])

    for subreddit in SUBREDDITS:
        log.info(f"  r/{subreddit}")
        for query in queries:
            posts = scrape_subreddit_query(subreddit, query, start_epoch, end_epoch)
            for p in posts:
                if p["id"] and p["id"] not in seen_ids:
                    seen_ids.add(p["id"])
                    p["event"] = event_name
                    all_posts.append(p)

        log.info(f"    {len(all_posts)} unique posts so far")

    if not all_posts:
        log.warning(f"[{event_name}]  No posts found")
        return pd.DataFrame()

    df = pd.DataFrame(all_posts)
    df["date"] = pd.to_datetime(df["created_utc"], unit="s", utc=True).dt.date
    df["combined_text"] = (df["title"] + " " + df["text"]).str.strip()

    log.info(f"[{event_name}]  Done — {len(df)} unique posts")
    return df


def run_all():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for event_name, event_date in EVENT_DATES.items():
        out_path = RAW_DIR / f"{event_name}.csv"

        if out_path.exists():
            existing = pd.read_csv(out_path)
            log.info(f"[{event_name}]  Already collected ({len(existing)} posts) — delete file to re-run")
            continue

        df = scrape_event(event_name, event_date)

        if not df.empty:
            df.to_csv(out_path, index=False)
            log.info(f"[{event_name}]  Saved → {out_path}\n")
        else:
            log.warning(f"[{event_name}]  No data — no file written\n")


if __name__ == "__main__":
    run_all()
