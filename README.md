# Devil Wears Prada 2: Fashion Sentiment & Luxury Stock Analysis

> *Does a cultural event move luxury stock prices — even when the brands have no financial stake in it?*

This project applies **event study methodology** and **multi-source NLP sentiment analysis** to nine events surrounding *The Devil Wears Prada 2* (film, May 2026) and its companion West End musical (Oct 2024–present), testing whether measurable public sentiment predicts short-term abnormal returns across seven luxury equity tickers.

**→ Full write-up:** [`ANALYSIS_WRITEUP.md`](ANALYSIS_WRITEUP.md)
**→ Methodology explained:** [`METHODOLOGY.md`](METHODOLOGY.md)
**→ All findings by indicator:** [`ANALYSIS_RESULTS.md`](ANALYSIS_RESULTS.md)

---

## Key Findings

- **Hermès +5.1% CAR** at West End musical previews, p=0.0037 (\*\*\*)
- **LVMH +5.5% CAR** at West End musical previews, p=0.038 (\*\*)
- **LVMH and Hermès** show statistically significant same-day correlation with Reddit sentiment (p<0.05)
- **Audience vs. critic divergence:** YouTube audiences are positive about the film (+0.31); Guardian critics are negative (−0.08 to −0.19); both agree the musical was excellent (+0.73–0.92)
- **Reddit IC = 0.14** — in the upper range of commercial alternative data benchmarks, not significant at n=52
- Film events (trailers, premiere, theatrical release) produced **no statistically significant CARs**, partly due to high-VIX market conditions during spring 2026

---

## Research Question

**Can sentiment derived from social media and press data predict abnormal returns in luxury fashion equities around a high-profile cultural event?**

Prada S.p.A. has no financial stake in the film — no licensing deal, no royalties. Any measurable stock price effect is therefore entirely sentiment-driven, making the causal chain cleaner to reason about than a typical earnings event study.

---

## Events (9 total)

| Event | Date | Category |
|-------|------|----------|
| West End previews begin | Oct 24, 2024 | Musical |
| West End opening night | Dec 5, 2024 | Musical |
| Prada SS26 womenswear show, Milan | Sep 18, 2025 | Fashion Week |
| Teaser trailer (181.5M views / 24hrs) | Nov 12, 2025 | Film |
| Full trailer (222M views / 24hrs) | Feb 1, 2026 | Film |
| Prada FW26 womenswear show, Milan | Feb 20, 2026 | Fashion Week |
| Run extended to Feb 2027 | Mar 13, 2026 | Musical |
| NYC premiere, live-streamed globally | Apr 20, 2026 | Film |
| Theatrical release ($115M opening weekend) | May 1, 2026 | Film |

---

## Stock Universe (7 tickers)

| Ticker | Exchange | Company | Relevance |
|--------|----------|---------|-----------|
| `1913.HK` | HKEx | Prada S.p.A. | Film named after the brand |
| `MC.PA` | Euronext Paris | LVMH | Owns Dior; largest luxury conglomerate |
| `KER.PA` | Euronext Paris | Kering | Owns Gucci, Saint Laurent, Balenciaga |
| `RMS.PA` | Euronext Paris | Hermès | Ultra-luxury benchmark; no direct connection |
| `CPRI` | NYSE | Capri Holdings | Owns Versace; Donatella cameo in film |
| `TPR` | NYSE | Tapestry | Owns Coach; accessible luxury control |
| `EL` | NYSE | Estée Lauder | Beauty/fashion-adjacent; macro control |

**Reference tickers (context only):** `LUXE` (Roundhill Luxury ETF), `^VIX`

---

## Data Sources

| Source | Volume | Auth Required |
|--------|--------|--------------|
| Reddit | 308 posts, 9 events, 8 subreddits | None — public JSON API |
| YouTube | 3,141 comments, 41 videos | YouTube Data API v3 key |
| Guardian | 272 articles | Guardian Open Platform key (free) |
| Stocks + VIX | 475 trading days, Jul 2024–May 2026 | None — yfinance |

---

## Project Structure

```
dwp2-luxury-sentiment/
│
├── src/
│   ├── utils.py              # Shared constants, event dates, tickers, helpers
│   ├── reddit_scraper.py     # Reddit public JSON API (no credentials)
│   ├── guardian_scraper.py   # Guardian Open Platform API
│   ├── youtube_scraper.py    # YouTube Data API v3
│   ├── trends_scraper.py     # Google Trends via pytrends
│   ├── stock_data.py         # yfinance downloader
│   ├── sentiment.py          # VADER scoring + daily aggregation
│   └── event_study.py        # CAPM market model + CAR computation
│
├── notebooks/
│   ├── 01_data_collection.ipynb       # Data sanity checks + post volume plots
│   ├── 02_sentiment_analysis.ipynb    # Sentiment time series + distributions
│   ├── 03_stock_returns.ipynb         # Return EDA + correlation matrix
│   ├── 04_event_study.ipynb           # CAR computation + t-tests
│   ├── 05_results_visualisation.ipynb # All publication-quality figures
│   └── 06_signal_ic_vix_backtest.ipynb # IC, VIX regime, sector alpha, backtest
│
├── data/
│   ├── raw/
│   │   ├── reddit/           # Per-event post CSVs
│   │   ├── youtube/          # comments.csv
│   │   ├── guardian/         # articles.csv
│   │   └── stocks/           # prices.csv, returns.csv
│   └── processed/            # Scored sentiment + CAR results
│
├── results/
│   ├── figures/              # 14 PNG figures
│   └── tables/               # car_summary_formatted.csv, IC table, lag correlation
│
├── ANALYSIS_WRITEUP.md       # Full research note with all results
├── ANALYSIS_RESULTS.md       # Brain dump — every finding by source/indicator
├── METHODOLOGY.md            # Educational breakdown of every technique
├── requirements.txt
└── README.md
```

---

## Methodology Summary

**Event study:** CAPM market model with estimation window [−60, −10] trading days and event window [−2, +5] trading days. Abnormal returns tested with one-sample t-test (H₀: mean AR = 0).

**Sentiment:** VADER compound score (calibrated for social media text), upvote/like-weighted daily aggregation.

**Signal analysis:** Information Coefficient (IC = Pearson correlation between sentiment at t-1 and abnormal return at t), lag correlation across [0, 1, 2] day lags, VIX regime analysis, sector control via LUXE ETF alpha.

**Backtest:** Naive long/short basket (Prada + LVMH + Kering) triggered by sign of Reddit sentiment before each event. Proof-of-concept only — 9 events is insufficient for a statistically meaningful Sharpe estimate.

See [`METHODOLOGY.md`](METHODOLOGY.md) for a full educational breakdown.

---

## Quickstart

```bash
git clone https://github.com/jsabazova/dwp2-luxury-sentiment
cd dwp2-luxury-sentiment
pip install -r requirements.txt

# Add API keys (Guardian + YouTube only — Reddit needs no auth)
cp .env.example .env   # then fill in your keys

# Collect data
python src/reddit_scraper.py     # no credentials needed
python src/guardian_scraper.py
python src/youtube_scraper.py
python src/stock_data.py

# Score and analyse
python src/sentiment.py
python src/event_study.py

# Run all notebooks
for nb in notebooks/0*.ipynb; do
  jupyter nbconvert --to notebook --execute --inplace "$nb"
done
```

---

## Environment Setup

Create a `.env` file in the project root:

```bash
GUARDIAN_API_KEY=your_key_here    # free at open-platform.theguardian.com
YOUTUBE_API_KEY=your_key_here     # free at console.cloud.google.com
```

Reddit requires **no credentials** — this project uses the public JSON search endpoint (`reddit.com/r/{sub}/search.json`), which is free and read-only.

---

## Figures

All figures are pre-generated in `results/figures/`:

| Figure | Description |
|--------|-------------|
| `car_heatmap.png` | All tickers × events — the overview |
| `ic_scatter.png` | Sentiment vs abnormal return, per source |
| `vix_regime.png` | VIX level at each event + regime-split CARs |
| `sentiment_timeseries.png` | Reddit + YouTube + Guardian across all events |
| `sector_alpha.png` | Idiosyncratic alpha vs LUXE ETF |
| `signal_backtest.png` | Cumulative P&L of sentiment-driven strategy |
| `lyst_overlay.png` | Prada share price vs Lyst brand heat rank |
| `price_performance.png` | Normalised price performance, indexed to 100 |
| `car_paths.png` | Daily AR paths through event windows |
| `lag_correlation_vader.png` | Lag [0,1,2] correlation heatmap |
| `return_correlation.png` | Cross-ticker return correlation matrix |
| `return_distributions.png` | Daily return distributions, all 7 tickers |
| `post_volume.png` | Reddit post volume around each event |
| `cpri_vs_tpr.png` | Capri vs Tapestry event study comparison |

---

## Limitations

- **Statistical power:** 8 trading days per test is insufficient to detect moderate effects
- **Sample size:** 9 events; IC and Sharpe estimates require 50+ for statistical validity
- **VIX confound:** Film events occurred during high-volatility regime (VIX 24–28)
- **No Chinese-language data:** Xiaohongshu / Weibo would better capture sentiment relevant to HKEx-listed Prada
- **Reddit sampling:** Low post counts for some events (3–15 posts) make weighted sentiment noisy

---

## Future Extensions

- Google Trends integration (scraper written in `src/trends_scraper.py` — re-run after rate limit clears)
- Re-run theatrical_release analysis after May 8 when the full +5 trading day window closes
- Expand to other fashion-cultural events (Met Gala, BAFTA, major brand campaigns)
- Add Chinese-language social platforms for HKEx coverage
- Meta-analytic combination of Prada p-values across events (Fisher's method)

---

## Author

**J. Sabazova**
Quantitative analysis · NLP · Financial markets
[GitHub](https://github.com/jsabazova) · [LinkedIn](https://linkedin.com/in/jamila-sabazova)

---

*Research and portfolio purposes only. Nothing in this repository constitutes financial advice.*
