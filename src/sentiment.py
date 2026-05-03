"""
Sentiment scoring: VADER (always runs) + FinBERT (optional, skipped if unavailable).

Usage:
    python src/sentiment.py

Inputs:  data/raw/reddit/{event_name}.csv
Outputs: data/processed/sentiment_scores.csv
         data/processed/{event_name}_scored_posts.csv

FinBERT is disabled automatically if torch/transformers are incompatible.
VADER alone is sufficient for analysis — it performs well on social media text.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from utils import EVENT_DATES

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
log = logging.getLogger(__name__)

RAW_DIR       = Path(__file__).parent.parent / "data" / "raw" / "reddit"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

FINBERT_MODEL = "ProsusAI/finbert"
BATCH_SIZE    = 32

# ── Check FinBERT availability once at startup ─────────────────────────────────

FINBERT_AVAILABLE = False
try:
    import torch
    from transformers import pipeline as hf_pipeline
    FINBERT_AVAILABLE = True
    log.info("FinBERT available — will run both VADER and FinBERT")
except Exception as e:
    log.warning(f"FinBERT not available ({e}) — running VADER only")


# ── VADER ──────────────────────────────────────────────────────────────────────

def score_vader(texts: pd.Series) -> pd.Series:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    return texts.apply(lambda t: analyzer.polarity_scores(str(t))["compound"])


# ── FinBERT ────────────────────────────────────────────────────────────────────

def score_finbert(texts: pd.Series) -> pd.Series:
    import torch
    from transformers import pipeline as hf_pipeline

    device = 0 if torch.cuda.is_available() else -1
    log.info(f"  FinBERT on {'GPU' if device == 0 else 'CPU'}")

    pipe = hf_pipeline(
        "sentiment-analysis",
        model=FINBERT_MODEL,
        tokenizer=FINBERT_MODEL,
        device=device,
        truncation=True,
        max_length=512,
    )

    label_map = {"positive": 1.0, "neutral": 0.0, "negative": -1.0}
    results = []

    for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="FinBERT"):
        batch = [str(t)[:1000] for t in texts.iloc[i : i + BATCH_SIZE].tolist()]
        for out in pipe(batch):
            results.append(label_map.get(out["label"].lower(), 0.0) * out["score"])

    return pd.Series(results, index=texts.index)


# ── Aggregation ────────────────────────────────────────────────────────────────

def weighted_daily_sentiment(df: pd.DataFrame, score_col: str) -> pd.DataFrame:
    df = df.copy()
    df["weight"] = df["score"].clip(lower=1)
    df["weighted_score"] = df[score_col] * df["weight"]

    daily = (
        df.groupby("date")
        .apply(lambda g: pd.Series({
            f"{score_col}_weighted": g["weighted_score"].sum() / g["weight"].sum(),
            "post_count":            len(g),
            "total_weight":          g["weight"].sum(),
        }))
        .reset_index()
    )
    return daily


# ── Main ───────────────────────────────────────────────────────────────────────

def score_event(event_name: str) -> pd.DataFrame | None:
    path = RAW_DIR / f"{event_name}.csv"
    if not path.exists():
        log.warning(f"[{event_name}]  No data file — run reddit_scraper.py first")
        return None

    df = pd.read_csv(path, parse_dates=["date"])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    log.info(f"[{event_name}]  {len(df)} posts")

    # VADER (always)
    log.info(f"[{event_name}]  Running VADER...")
    df["vader"] = score_vader(df["combined_text"])

    # FinBERT (optional)
    if FINBERT_AVAILABLE:
        log.info(f"[{event_name}]  Running FinBERT...")
        df["finbert"] = score_finbert(df["combined_text"])
    else:
        df["finbert"] = float("nan")

    # Save scored posts
    df.to_csv(PROCESSED_DIR / f"{event_name}_scored_posts.csv", index=False)

    # Aggregate to daily
    vader_daily = weighted_daily_sentiment(df, "vader")

    if FINBERT_AVAILABLE:
        finbert_daily = weighted_daily_sentiment(df, "finbert")
        daily = vader_daily.merge(finbert_daily[["date", "finbert_weighted"]], on="date")
    else:
        daily = vader_daily.copy()
        daily["finbert_weighted"] = float("nan")

    daily["event"] = event_name
    return daily


def run():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    all_daily = []
    for event_name in EVENT_DATES:
        result = score_event(event_name)
        if result is not None:
            all_daily.append(result)

    if not all_daily:
        log.error("No events scored — check data/raw/reddit/")
        return

    combined = pd.concat(all_daily, ignore_index=True).sort_values(["event", "date"])
    out_path = PROCESSED_DIR / "sentiment_scores.csv"
    combined.to_csv(out_path, index=False)
    log.info(f"\nSaved → {out_path}")

    summary = combined.groupby("event")[["vader_weighted", "finbert_weighted"]].agg(["mean", "std"]).round(3)
    log.info(f"\n{summary}")


if __name__ == "__main__":
    run()
