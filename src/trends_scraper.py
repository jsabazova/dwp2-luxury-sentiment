"""
Google Trends data collection via pytrends.

Fetches daily search interest for film + musical keywords over the full
study period. Google Trends is free, requires no API key, and captures
a much broader audience than Reddit.

Usage:
    python src/trends_scraper.py

Output:
    data/processed/google_trends.csv

Columns:
    date            — calendar date
    dwp_film        — "devil wears prada 2" search interest (0–100)
    dwp_musical     — "devil wears prada musical" search interest (0–100)
    miranda         — "miranda priestly" search interest (0–100)
    prada_brand     — "prada" brand search interest (0–100)

Note:
    Google Trends returns relative interest (peak = 100 in the period).
    Values are comparable within a series but not across different series
    unless you request them in the same batch (which we do here).
    Daily granularity is only available for windows ≤ 270 days,
    so we fetch in overlapping 6-month chunks and stitch together.
"""

from __future__ import annotations

import time
import logging
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
log = logging.getLogger(__name__)

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

# Keywords to track — keep to ≤5 per request (Google Trends limit)
KEYWORDS = [
    "devil wears prada 2",
    "devil wears prada musical",
    "miranda priestly",
    "prada",
]

# Full study period
STUDY_START = date(2024, 10, 1)   # just before musical previews
STUDY_END   = date.today()

CHUNK_DAYS  = 180   # fetch in 6-month chunks for daily granularity
OVERLAP     = 7     # overlap days between chunks for stitching


def fetch_chunk(keywords: list[str], start: date, end: date) -> pd.DataFrame | None:
    """Fetch one chunk of Google Trends data."""
    try:
        from pytrends.request import TrendReq
    except ImportError:
        log.error("pytrends not installed. Run: pip install pytrends")
        return None

    pytrends = TrendReq(hl="en-US", tz=0, timeout=(10, 30))

    timeframe = f"{start.isoformat()} {end.isoformat()}"
    log.info(f"  Fetching {timeframe}")

    try:
        pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo="", gprop="")
        df = pytrends.interest_over_time()
        time.sleep(2)  # be polite to Google
    except Exception as e:
        log.warning(f"  Failed: {e}")
        time.sleep(10)
        return None

    if df.empty:
        log.warning("  Empty response from Google Trends")
        return None

    df = df.drop(columns=["isPartial"], errors="ignore")
    df.index = pd.to_datetime(df.index).date
    return df


def fetch_all(keywords: list[str], start: date, end: date) -> pd.DataFrame:
    """Fetch trends data in chunks and stitch into a single daily series."""
    chunks = []
    chunk_start = start

    while chunk_start < end:
        chunk_end = min(chunk_start + timedelta(days=CHUNK_DAYS), end)
        df = fetch_chunk(keywords, chunk_start, chunk_end)
        if df is not None:
            chunks.append(df)
            chunk_start = chunk_end - timedelta(days=OVERLAP)
        else:
            # On failure always advance past this chunk to avoid infinite loop
            chunk_start = chunk_end

    if not chunks:
        log.error("No data fetched from Google Trends")
        return pd.DataFrame()

    combined = pd.concat(chunks)
    combined = combined[~combined.index.duplicated(keep="last")]
    combined = combined.sort_index()
    return combined


def run():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "google_trends.csv"

    log.info(f"Fetching Google Trends: {STUDY_START} → {STUDY_END}")
    log.info(f"Keywords: {KEYWORDS}")

    df = fetch_all(KEYWORDS, STUDY_START, STUDY_END)

    if df.empty:
        log.error("No trends data — check pytrends installation")
        return

    # Rename columns for clarity
    col_map = {
        "devil wears prada 2":       "dwp_film",
        "devil wears prada musical": "dwp_musical",
        "miranda priestly":          "miranda",
        "prada":                     "prada_brand",
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
    df.index.name = "date"

    df.to_csv(out_path)
    log.info(f"Saved → {out_path}  ({len(df)} days)")
    log.info(f"\nPeak interest dates:")
    for col in df.columns:
        peak_date = df[col].idxmax()
        log.info(f"  {col}: {peak_date} (score={df[col].max()})")


if __name__ == "__main__":
    run()
