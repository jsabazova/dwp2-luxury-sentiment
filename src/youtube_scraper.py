"""
YouTube Data API v3 comment collection.

Searches for Devil Wears Prada 2 / musical videos, then pulls top-level
comments and scores them with VADER. Comments are much richer than Reddit
for audience reaction data — trailer comment sections capture real-time
public sentiment at the moment of viewing.

Usage:
    python src/youtube_scraper.py

Output:
    data/raw/youtube/comments.csv
    data/processed/youtube_sentiment.csv  (daily weighted sentiment)

Free quota: 10,000 units/day.
  - search.list  = 100 units per call
  - commentThreads.list = 1 unit per call (up to 100 comments)
"""

from __future__ import annotations

import os
import time
import logging
from pathlib import Path
from datetime import date

import requests
import pandas as pd
from dotenv import load_dotenv

from utils import EVENT_DATES, event_calendar_window

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
log = logging.getLogger(__name__)

RAW_DIR       = Path(__file__).parent.parent / "data" / "raw" / "youtube"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

API_KEY      = os.getenv("YOUTUBE_API_KEY")
BASE_SEARCH  = "https://www.googleapis.com/youtube/v3/search"
BASE_COMMENTS = "https://www.googleapis.com/youtube/v3/commentThreads"

# Search queries — what videos to target
VIDEO_QUERIES = [
    "devil wears prada 2 trailer",
    "devil wears prada 2 movie 2026",
    "devil wears prada musical west end",
    "devil wears prada musical review",
    "prada luxury brand 2025 2026",
]

MAX_COMMENTS_PER_VIDEO = 200   # top 200 comments per video
DELAY = 0.5                    # seconds between requests


def search_videos(query: str, max_results: int = 10) -> list[dict]:
    """Search for videos matching a query. Costs 100 units per call."""
    if not API_KEY:
        raise EnvironmentError("YOUTUBE_API_KEY not set in .env")

    params = {
        "part":       "snippet",
        "q":          query,
        "type":       "video",
        "maxResults": max_results,
        "order":      "relevance",
        "key":        API_KEY,
    }
    try:
        resp = requests.get(BASE_SEARCH, params=params, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        log.warning(f"  Search failed: {e}")
        return []

    items = resp.json().get("items", [])
    videos = []
    for item in items:
        snippet = item.get("snippet", {})
        videos.append({
            "video_id":    item["id"]["videoId"],
            "title":       snippet.get("title", ""),
            "channel":     snippet.get("channelTitle", ""),
            "published":   snippet.get("publishedAt", "")[:10],
            "description": snippet.get("description", "")[:200],
            "query":       query,
        })
    return videos


def fetch_comments(video_id: str, max_comments: int = MAX_COMMENTS_PER_VIDEO) -> list[dict]:
    """Fetch top-level comments for a video. Costs 1 unit per page."""
    comments = []
    page_token = None

    while len(comments) < max_comments:
        params = {
            "part":              "snippet",
            "videoId":           video_id,
            "maxResults":        min(100, max_comments - len(comments)),
            "order":             "relevance",
            "textFormat":        "plainText",
            "key":               API_KEY,
        }
        if page_token:
            params["pageToken"] = page_token

        try:
            resp = requests.get(BASE_COMMENTS, params=params, timeout=15)
            if resp.status_code == 403:
                # Comments disabled on this video
                log.debug(f"  Comments disabled for {video_id}")
                break
            resp.raise_for_status()
        except requests.RequestException as e:
            log.warning(f"  Comment fetch failed for {video_id}: {e}")
            break

        data = resp.json()
        for item in data.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "video_id":   video_id,
                "comment_id": item["id"],
                "text":       top.get("textDisplay", ""),
                "likes":      top.get("likeCount", 0),
                "date":       top.get("publishedAt", "")[:10],
                "author":     top.get("authorDisplayName", ""),
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break
        time.sleep(DELAY)

    return comments


def score_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    df = df.copy()
    df["vader"] = df["text"].apply(
        lambda t: analyzer.polarity_scores(str(t))["compound"]
    )
    return df


def daily_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    df["date"] = pd.to_datetime(df["date"]).dt.date
    # Weight by (likes + 1) so highly-liked comments count more
    df["weight"] = df["likes"].clip(lower=0) + 1
    df["weighted_vader"] = df["vader"] * df["weight"]

    daily = (
        df.groupby("date")
        .agg(
            youtube_vader=("weighted_vader", "sum"),
            total_weight=("weight", "sum"),
            comment_count=("comment_id", "count"),
        )
        .reset_index()
    )
    daily["youtube_vader"] = daily["youtube_vader"] / daily["total_weight"]
    return daily[["date", "youtube_vader", "comment_count"]]


def run():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    log.info("YouTube Data API: searching for relevant videos")

    all_videos: list[dict] = []
    seen_video_ids: set[str] = set()

    for query in VIDEO_QUERIES:
        log.info(f"\nSearch: {query}")
        videos = search_videos(query, max_results=10)
        new = [v for v in videos if v["video_id"] not in seen_video_ids]
        seen_video_ids.update(v["video_id"] for v in new)
        all_videos.extend(new)
        log.info(f"  {len(new)} new videos")
        time.sleep(DELAY)

    if not all_videos:
        log.error("No videos found — check API key")
        return

    log.info(f"\nTotal unique videos: {len(all_videos)}")

    # Fetch comments for each video
    all_comments: list[dict] = []
    for video in all_videos:
        vid = video["video_id"]
        log.info(f"  Fetching comments: {video['title'][:60]}  ({vid})")
        comments = fetch_comments(vid)
        for c in comments:
            c["video_title"] = video["title"]
            c["video_query"] = video["query"]
        all_comments.extend(comments)
        log.info(f"    → {len(comments)} comments")
        time.sleep(DELAY)

    if not all_comments:
        log.error("No comments fetched")
        return

    comments_df = pd.DataFrame(all_comments)

    # Save raw comments
    raw_path = RAW_DIR / "comments.csv"
    comments_df.to_csv(raw_path, index=False)
    log.info(f"\nSaved {len(comments_df)} comments → {raw_path}")

    # Score and aggregate
    scored = score_sentiment(comments_df)
    daily  = daily_sentiment(scored)

    out_path = PROCESSED_DIR / "youtube_sentiment.csv"
    daily.to_csv(out_path, index=False)
    log.info(f"Daily sentiment saved → {out_path}")

    # Coverage around events
    log.info("\nYouTube coverage around events:")
    daily["date"] = pd.to_datetime(daily["date"]).dt.date
    for event_name, event_date in EVENT_DATES.items():
        start, end = event_calendar_window(event_date, window_days=7)
        window = daily[(daily["date"] >= start) & (daily["date"] <= end)]
        if not window.empty:
            log.info(
                f"  {event_name}: {len(window)} days with comments, "
                f"mean sentiment={window['youtube_vader'].mean():.3f}, "
                f"total comments={window['comment_count'].sum()}"
            )
        else:
            log.info(f"  {event_name}: no YouTube comments in window")

    # Print top videos by comment count
    video_counts = (
        scored.groupby(["video_id", "video_title"])
        .agg(comments=("comment_id", "count"), mean_sentiment=("vader", "mean"))
        .sort_values("comments", ascending=False)
        .head(10)
    )
    log.info("\nTop videos by comment count:")
    for (vid, title), row in video_counts.iterrows():
        log.info(f"  {title[:55]:<55}  {row['comments']:>4} comments  sentiment={row['mean_sentiment']:.3f}")


if __name__ == "__main__":
    run()
