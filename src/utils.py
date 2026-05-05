"""
Shared constants and helpers used across all modules.
"""

from __future__ import annotations

from datetime import date, timedelta
import pandas as pd
import numpy as np

# ── Event dates ────────────────────────────────────────────────────────────────

EVENT_DATES = {
    # ── Film events ────────────────────────────────────────────────────────────
    "teaser_trailer":      date(2025, 11, 12),   # 181.5M views in 24hrs
    "full_trailer":        date(2026,  2,  1),   # 222M views in 24hrs
    "nyc_premiere":        date(2026,  4, 20),   # live-streamed globally
    "theatrical_release":  date(2026,  5,  1),   # $115M opening weekend

    # ── Musical events (West End, Dominion Theatre, London) ───────────────────
    # Elton John music; Vanessa Williams as Miranda Priestly
    "musical_previews":    date(2024, 10, 24),   # West End previews begin
    "musical_opening":     date(2024, 12,  5),   # West End opening night
    "musical_extension":   date(2026,  3, 13),   # run extended to Feb 2027

    # ── Milan Fashion Week — Prada runway shows ───────────────────────────────
    # Stock-only events (no Reddit sentiment collected); validate brand signal
    # independently of the film/musical narrative
    "prada_ss26_show":     date(2025,  9, 18),   # MFW SS26 Womenswear, Milan
    "prada_fw26_show":     date(2026,  2, 20),   # MFW FW26 Womenswear, Milan
}

# ── Stock universe ─────────────────────────────────────────────────────────────

TICKERS = {
    "1913.HK": "Prada",
    "MC.PA":   "LVMH",
    "KER.PA":  "Kering",
    "CPRI":    "Capri Holdings",
    "TPR":     "Tapestry",
    "EL":      "Estee Lauder",
    "RMS.PA":  "Hermes",          # ultra-luxury benchmark, Euronext Paris
}

# Benchmark index for each ticker (used in market model)
BENCHMARKS = {
    "1913.HK": "^HSI",
    "MC.PA":   "^STOXX50E",
    "KER.PA":  "^STOXX50E",
    "CPRI":    "^GSPC",
    "TPR":     "^GSPC",
    "EL":      "^GSPC",
    "RMS.PA":  "^STOXX50E",
}

ALL_BENCHMARKS = list(set(BENCHMARKS.values()))

# ── Reference / context tickers ────────────────────────────────────────────────
# Downloaded alongside main tickers but NOT subject to event study.
# Used for sector control and volatility regime analysis.
REFERENCE_TICKERS = {
    "LUXE":  "Roundhill Luxury ETF",    # global luxury sector benchmark
    "^VIX":  "CBOE Volatility Index",   # market vol regime
}

# ── Lyst Index — quarterly brand hotness rankings ──────────────────────────────
# Source: lyst.com/lyst-index (verify each entry against the published PDF).
# Prada Group (Prada + Miu Miu) has ranked consistently in top 5 since 2023.
# Use as qualitative narrative anchor in the article, not a quantitative input.
LYST_INDEX = {
    date(2024,  7,  1): {"prada_rank": 4,  "miu_miu_rank": 1,  "quarter": "Q2 2024"},
    date(2024, 10,  1): {"prada_rank": 3,  "miu_miu_rank": 1,  "quarter": "Q3 2024"},
    date(2025,  1,  1): {"prada_rank": 2,  "miu_miu_rank": 2,  "quarter": "Q4 2024"},
    date(2025,  4,  1): {"prada_rank": 1,  "miu_miu_rank": 3,  "quarter": "Q1 2025"},
}

# ── Reddit config ──────────────────────────────────────────────────────────────

SUBREDDITS = [
    "fashion",
    "femalefashionadvice",
    "malefashionadvice",
    "movies",
    "boxoffice",
    "investing",
    "stocks",
    "musicals",
]

SEARCH_QUERIES = [
    "devil wears prada 2",
    "devil wears prada",
    "miranda priestly",
    "runway magazine film",
]

# Separate queries for musical events — broader to catch theatre discourse
MUSICAL_QUERIES = [
    "devil wears prada musical",
    "devil wears prada west end",
    "devil wears prada dominion theatre",
    "prada musical elton john",
    "miranda priestly musical",
]

FASHION_WEEK_QUERIES = [
    "prada fashion week",
    "prada runway",
    "prada milan fashion week",
    "prada womenswear",
]

# Which events use film queries vs musical queries vs fashion week queries
EVENT_QUERY_MAP = {
    "teaser_trailer":     SEARCH_QUERIES,
    "full_trailer":       SEARCH_QUERIES,
    "nyc_premiere":       SEARCH_QUERIES,
    "theatrical_release": SEARCH_QUERIES,
    "musical_previews":   MUSICAL_QUERIES,
    "musical_opening":    MUSICAL_QUERIES,
    "musical_extension":  MUSICAL_QUERIES,
    "prada_ss26_show":    FASHION_WEEK_QUERIES,
    "prada_fw26_show":    FASHION_WEEK_QUERIES,
}

# ── Event study windows ────────────────────────────────────────────────────────

ESTIMATION_WINDOW = (-60, -10)   # trading days relative to event
EVENT_WINDOW      = (-2,   +5)   # trading days relative to event

# ── Date helpers ───────────────────────────────────────────────────────────────

def event_calendar_window(event_date: date, window_days: int = 7) -> tuple[date, date]:
    """Return (start, end) calendar dates for Reddit collection window."""
    return (
        event_date - timedelta(days=window_days),
        event_date + timedelta(days=window_days),
    )

def trading_days_around(prices_index: pd.DatetimeIndex, event_date: date,
                         start_offset: int, end_offset: int) -> pd.DatetimeIndex:
    """
    Given a DatetimeIndex of trading days and an event date, return the
    sub-index covering [event + start_offset, event + end_offset] trading days.
    """
    event_dt = pd.Timestamp(event_date)
    # Find the closest trading day on or after event_date
    future = prices_index[prices_index >= event_dt]
    if len(future) == 0:
        raise ValueError(f"No trading days found on or after {event_date}")
    event_idx = prices_index.get_loc(future[0])

    start_idx = event_idx + start_offset
    end_idx   = event_idx + end_offset + 1  # +1 for inclusive slice

    start_idx = max(start_idx, 0)
    end_idx   = min(end_idx, len(prices_index))

    return prices_index[start_idx:end_idx]

def log_returns(prices: pd.Series) -> pd.Series:
    return np.log(prices / prices.shift(1)).dropna()
