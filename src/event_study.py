"""
Event study: compute Cumulative Abnormal Returns (CARs) for each
ticker × event combination using the market model (OLS beta).

Usage:
    python src/event_study.py

Inputs:  data/raw/stocks/returns.csv
Outputs: data/processed/car_results.csv
         data/processed/car_summary.csv  (mean CAR + t-stat per ticker × event)

Methodology:
    - Estimation window: [-60, -10] trading days before event
    - Event window:      [-2,  +5] trading days around event
    - Normal return:     E[R] = alpha + beta * R_benchmark (OLS from estimation window)
    - Abnormal return:   AR_t = R_t - E[R_t]
    - CAR:               cumulative sum of AR_t over event window
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression

from utils import (
    EVENT_DATES, TICKERS, BENCHMARKS,
    ESTIMATION_WINDOW, EVENT_WINDOW,
    trading_days_around,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
log = logging.getLogger(__name__)

RAW_DIR       = Path(__file__).parent.parent / "data" / "raw" / "stocks"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"


def load_returns() -> pd.DataFrame:
    path = RAW_DIR / "returns.csv"
    if not path.exists():
        raise FileNotFoundError(f"Returns file not found at {path}. Run stock_data.py first.")
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index)
    return df


def estimate_market_model(ticker_returns: pd.Series,
                           bench_returns: pd.Series) -> tuple[float, float]:
    """
    OLS regression: ticker_return ~ alpha + beta * benchmark_return
    Returns (alpha, beta).
    """
    aligned = pd.concat([ticker_returns, bench_returns], axis=1).dropna()
    if len(aligned) < 20:
        log.warning(f"Only {len(aligned)} obs in estimation window — beta may be unreliable")

    X = aligned.iloc[:, 1].values.reshape(-1, 1)
    y = aligned.iloc[:, 0].values

    model = LinearRegression().fit(X, y)
    return float(model.intercept_), float(model.coef_[0])


def compute_car_for_event(returns: pd.DataFrame, ticker: str,
                           event_name: str, event_date) -> pd.DataFrame | None:
    """
    Compute daily abnormal returns and CAR for one ticker × event.
    Returns a DataFrame with columns: [ticker, event, event_date, day, ar, car, beta].
    """
    if ticker not in returns.columns:
        log.warning(f"Ticker {ticker} not in returns data")
        return None

    benchmark = BENCHMARKS[ticker]
    if benchmark not in returns.columns:
        log.warning(f"Benchmark {benchmark} not in returns data")
        return None

    idx = returns.index

    # ── Estimation window ──────────────────────────────────────────────────────
    try:
        est_dates = trading_days_around(idx, event_date, ESTIMATION_WINDOW[0], ESTIMATION_WINDOW[1])
    except ValueError as e:
        log.warning(f"[{event_name} / {ticker}]  {e}")
        return None

    ticker_est = returns.loc[est_dates, ticker].dropna()
    bench_est  = returns.loc[est_dates, benchmark].dropna()

    if len(ticker_est) < 10:
        log.warning(f"[{event_name} / {ticker}]  Too few estimation window observations ({len(ticker_est)})")
        return None

    alpha, beta = estimate_market_model(ticker_est, bench_est)

    # ── Event window ───────────────────────────────────────────────────────────
    try:
        ev_dates = trading_days_around(idx, event_date, EVENT_WINDOW[0], EVENT_WINDOW[1])
    except ValueError as e:
        log.warning(f"[{event_name} / {ticker}]  {e}")
        return None

    ticker_ev = returns.loc[ev_dates, ticker]
    bench_ev  = returns.loc[ev_dates, benchmark]

    expected = alpha + beta * bench_ev
    ar = ticker_ev - expected

    records = []
    cumulative = 0.0
    for i, (date, ar_val) in enumerate(ar.items()):
        day = i + EVENT_WINDOW[0]  # relative day: -2, -1, 0, +1, ...
        cumulative += ar_val
        records.append({
            "ticker":       ticker,
            "event":        event_name,
            "event_date":   event_date,
            "date":         date.date(),
            "day":          day,
            "ar":           ar_val,
            "car":          cumulative,
            "beta":         beta,
            "alpha":        alpha,
        })

    return pd.DataFrame(records)


def compute_summary(car_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each ticker × event: compute total CAR, t-statistic, p-value.
    Also compute average CAR across events per ticker.
    """
    rows = []
    for (ticker, event), grp in car_df.groupby(["ticker", "event"]):
        ars = grp["ar"].values
        total_car = grp["car"].iloc[-1]
        n = len(ars)
        if n < 2:
            continue

        # t-test: H0 = mean(AR) = 0
        t_stat, p_val = stats.ttest_1samp(ars, 0)

        rows.append({
            "ticker":     ticker,
            "event":      event,
            "n_days":     n,
            "total_car":  total_car,
            "mean_ar":    ars.mean(),
            "std_ar":     ars.std(),
            "t_stat":     t_stat,
            "p_value":    p_val,
            "significant": p_val < 0.05,
            "beta":       grp["beta"].iloc[0],
        })

    return pd.DataFrame(rows).sort_values(["ticker", "event"])


def run():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    returns = load_returns()
    log.info(f"Loaded returns: {returns.shape[0]} days × {returns.shape[1]} tickers")

    all_cars = []

    for event_name, event_date in EVENT_DATES.items():
        log.info(f"\n── Event: {event_name} ({event_date}) ──")
        for ticker in TICKERS:
            df = compute_car_for_event(returns, ticker, event_name, event_date)
            if df is not None:
                all_cars.append(df)
                final_car = df["car"].iloc[-1]
                log.info(f"  {ticker:10s}  CAR = {final_car:+.4f}  (beta={df['beta'].iloc[0]:.3f})")

    if not all_cars:
        log.error("No CAR results — check that stock data exists in data/raw/stocks/")
        return

    car_df = pd.concat(all_cars, ignore_index=True)
    car_path = PROCESSED_DIR / "car_results.csv"
    car_df.to_csv(car_path, index=False)
    log.info(f"\nCAR results saved to {car_path}")

    summary = compute_summary(car_df)
    summary_path = PROCESSED_DIR / "car_summary.csv"
    summary.to_csv(summary_path, index=False)
    log.info(f"CAR summary saved to {summary_path}")

    # Print significant results
    sig = summary[summary["significant"]]
    if len(sig) > 0:
        log.info(f"\nStatistically significant CARs (p < 0.05):\n{sig[['ticker','event','total_car','t_stat','p_value']].to_string()}")
    else:
        log.info("\nNo statistically significant CARs found (null hypothesis not rejected)")


if __name__ == "__main__":
    run()
