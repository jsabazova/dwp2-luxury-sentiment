"""
Download and save stock price data for all tickers and benchmarks.

Usage:
    python src/stock_data.py

Outputs:
    data/raw/stocks/prices.csv   — adjusted close prices
    data/raw/stocks/returns.csv  — daily log returns
"""

import logging
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

from utils import TICKERS, ALL_BENCHMARKS, EVENT_DATES, log_returns

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
log = logging.getLogger(__name__)

RAW_DIR = Path(__file__).parent.parent / "data" / "raw" / "stocks"

# Download window: covers all events including the musical (Oct 2024).
# Earliest event is musical_previews Oct 24 2024; estimation window starts
# 60 trading days before that (~Jul 2024). Use a comfortable buffer.
DOWNLOAD_START = "2024-07-01"
DOWNLOAD_END   = date.today().isoformat()

ALL_TICKERS = list(TICKERS.keys()) + ALL_BENCHMARKS


def download_prices() -> pd.DataFrame:
    log.info(f"Downloading {len(ALL_TICKERS)} tickers: {ALL_TICKERS}")
    raw = yf.download(
        ALL_TICKERS,
        start=DOWNLOAD_START,
        end=DOWNLOAD_END,
        auto_adjust=True,
        progress=True,
    )

    # yfinance returns MultiIndex columns when >1 ticker; extract Close
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        prices = raw[["Close"]].rename(columns={"Close": ALL_TICKERS[0]})

    prices.index = pd.to_datetime(prices.index)
    prices = prices.sort_index()

    missing = [t for t in ALL_TICKERS if t not in prices.columns]
    if missing:
        log.warning(f"Missing tickers (may need manual check): {missing}")

    log.info(f"Downloaded {len(prices)} trading days, {prices.shape[1]} tickers")
    log.info(f"Date range: {prices.index[0].date()} → {prices.index[-1].date()}")
    return prices


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    returns = np.log(prices / prices.shift(1)).dropna(how="all")
    return returns


def run():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    prices_path  = RAW_DIR / "prices.csv"
    returns_path = RAW_DIR / "returns.csv"

    prices = download_prices()
    prices.to_csv(prices_path)
    log.info(f"Prices saved to {prices_path}")

    returns = compute_returns(prices)
    returns.to_csv(returns_path)
    log.info(f"Returns saved to {returns_path}")

    # Quick sanity check: print coverage for each event
    log.info("\nEvent coverage check:")
    for name, ev_date in EVENT_DATES.items():
        ev_dt = pd.Timestamp(ev_date)
        before = prices[prices.index < ev_dt]
        after  = prices[prices.index >= ev_dt]
        log.info(
            f"  {name} ({ev_date}): "
            f"{len(before)} trading days before, {len(after)} after"
        )


if __name__ == "__main__":
    run()
