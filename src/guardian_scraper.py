"""
Guardian API data collection.

Fetches articles related to the film, musical, and luxury brands
across the full study period. Article text is scored with VADER for
professional/critical sentiment — a useful contrast to Reddit's
casual social media sentiment.

Usage:
    python src/guardian_scraper.py

Output:
    data/raw/guardian/articles.csv
    data/processed/guardian_sentiment.csv  (daily weighted sentiment)

Free tier: 500 calls/day — more than enough for this project.
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

RAW_DIR       = Path(__file__).parent.parent / "data" / "raw" / "guardian"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

BASE_URL = "https://content.guardianapis.com/search"
API_KEY  = os.getenv("GUARDIAN_API_KEY")

# Study start: just before earliest event (musical previews Oct 2024)
STUDY_START = date(2024, 10, 1)
STUDY_END   = date.today()

# Search queries — Guardian supports AND/OR operators
SEARCH_QUERIES = [
    '"devil wears prada"',
    '"prada" AND ("luxury" OR "fashion" OR "stock")',
    '"LVMH" AND "fashion"',
    '"Kering" AND "fashion"',
]

DELAY = 0.5  # seconds between requests (well within 12/sec rate limit)


def fetch_articles(query: str, from_date: date, to_date: date,
                   page_size: int = 50) -> list[dict]:
    """Fetch all articles matching a query in a date range."""
    if not API_KEY:
        raise EnvironmentError("GUARDIAN_API_KEY not set in .env")

    all_articles = []
    page = 1

    while True:
        params = {
            "q":           query,
            "from-date":   from_date.isoformat(),
            "to-date":     to_date.isoformat(),
            "page-size":   page_size,
            "page":        page,
            "show-fields": "bodyText,headline,wordcount",
            "api-key":     API_KEY,
        }

        try:
            resp = requests.get(BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            log.warning(f"  Request failed: {e}")
            break

        data = resp.json().get("response", {})
        results = data.get("results", [])
        all_articles.extend(results)

        total_pages = data.get("pages", 1)
        log.debug(f"  Page {page}/{total_pages} — {len(results)} articles")

        if page >= total_pages:
            break
        page += 1
        time.sleep(DELAY)

    return all_articles


def parse_articles(raw: list[dict], query: str) -> pd.DataFrame:
    rows = []
    for item in raw:
        fields = item.get("fields", {})
        body = fields.get("bodyText", "") or ""
        headline = fields.get("headline", "") or item.get("webTitle", "")
        rows.append({
            "id":         item.get("id", ""),
            "date":       item.get("webPublicationDate", "")[:10],
            "headline":   headline,
            "body":       body[:2000],  # cap for sentiment scoring
            "combined":   headline + ". " + body[:1000],
            "section":    item.get("sectionName", ""),
            "url":        item.get("webUrl", ""),
            "query":      query,
        })
    return pd.DataFrame(rows)


def score_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    df = df.copy()
    df["vader"] = df["combined"].apply(
        lambda t: analyzer.polarity_scores(str(t))["compound"]
    )
    return df


def daily_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    df["date"] = pd.to_datetime(df["date"]).dt.date
    daily = (
        df.groupby("date")
        .agg(
            guardian_vader=("vader", "mean"),
            article_count=("id", "count"),
        )
        .reset_index()
    )
    return daily


def run():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    log.info(f"Guardian API: {STUDY_START} → {STUDY_END}")
    log.info(f"Queries: {SEARCH_QUERIES}")

    all_articles = []
    seen_ids: set[str] = set()

    for query in SEARCH_QUERIES:
        log.info(f"\nQuery: {query}")
        raw = fetch_articles(query, STUDY_START, STUDY_END)
        df = parse_articles(raw, query)

        # Deduplicate by article ID
        new = df[~df["id"].isin(seen_ids)]
        seen_ids.update(new["id"].tolist())
        all_articles.append(new)
        log.info(f"  {len(new)} new articles")

    if not all_articles:
        log.error("No articles fetched — check API key in .env")
        return

    articles = pd.concat(all_articles, ignore_index=True)
    articles = articles.sort_values("date")

    # Save raw articles
    raw_path = RAW_DIR / "articles.csv"
    articles.to_csv(raw_path, index=False)
    log.info(f"\nSaved {len(articles)} articles → {raw_path}")

    # Score and aggregate
    scored = score_sentiment(articles)
    daily  = daily_sentiment(scored)

    out_path = PROCESSED_DIR / "guardian_sentiment.csv"
    daily.to_csv(out_path, index=False)
    log.info(f"Daily sentiment saved → {out_path}")

    # Print around each event
    log.info("\nGuardian coverage around events:")
    daily["date"] = pd.to_datetime(daily["date"]).dt.date
    for event_name, event_date in EVENT_DATES.items():
        start, end = event_calendar_window(event_date, window_days=7)
        window = daily[(daily["date"] >= start) & (daily["date"] <= end)]
        if not window.empty:
            log.info(
                f"  {event_name}: {len(window)} days with coverage, "
                f"mean sentiment={window['guardian_vader'].mean():.3f}, "
                f"total articles={window['article_count'].sum()}"
            )
        else:
            log.info(f"  {event_name}: no Guardian coverage in window")


if __name__ == "__main__":
    run()
