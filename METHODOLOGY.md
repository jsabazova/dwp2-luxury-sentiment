# Methodology — How This Study Works

*An educational breakdown for software engineers, quant-curious readers, and anyone who wants to understand how you go from a film trailer to a t-statistic.*

---

## The Core Question

> Can measurable public sentiment around a cultural event predict short-term abnormal price movements in stocks that are thematically — but not financially — connected to that event?

This is not a question about whether Prada made money from the film. They had no stake in it. The question is whether *cultural discourse* has information content that the market prices in — and whether we can measure that discourse systematically before the market does.

---

## Part 1 — The Research Design: Event Study

### What is an event study?

An event study is a statistical technique from academic finance used to measure how much a stock moves *in excess of what you'd expect* around a specific event. It was first formalised by Fama, Fisher, Jensen & Roll in 1969 and is now standard practice in empirical finance research — and increasingly in quantitative trading.

The core insight is simple: on any given day, a stock moves for a thousand reasons. To isolate the effect of one specific event, you need to strip out the "expected" return — the return the stock would have had anyway based on market conditions — and look only at what's *left over*. That leftover is called the **Abnormal Return (AR)**.

```
Abnormal Return = Actual Return − Expected Return
```

Sum the daily abnormal returns across the event window, and you get the **Cumulative Abnormal Return (CAR)**: the total excess return attributable to the event period.

---

### Step 1 — Define your events

Every event study starts with a list of clean, timestamped events. The events need to be:
- **Exogenous** — they happen for reasons outside the stock's own fundamentals
- **Timestamped precisely** — you need to know the exact date the information became public
- **Separable** — ideally not overlapping with major earnings releases or macro events

For this study, we identified 9 events across three categories:

| Category | Events |
|----------|--------|
| Film (Devil Wears Prada 2) | Teaser trailer, full trailer, NYC premiere, theatrical release |
| West End musical | Previews, opening night, run extension announcement |
| Fashion Week | Prada SS26 womenswear show, Prada FW26 womenswear show |

---

### Step 2 — Define your windows

Two time windows matter in an event study:

**Estimation window:** The period *before* the event used to estimate how the stock normally behaves. We used [-60, -10] trading days relative to the event date — starting 60 days before and ending 10 days before, leaving a 10-day buffer so any anticipatory trading doesn't contaminate the baseline.

```
|←——————— estimation window ———————→|  buffer  |←— event window —→|
   t-60                            t-10      t-2    t=0    t+5
```

**Event window:** The period around the event where we measure abnormal returns. We used [-2, +5] trading days — two days before (to capture leakage and anticipation) through five days after (to capture drift and post-event repricing).

---

### Step 3 — Build the market model

To compute *expected* returns, we fit a simple linear regression during the estimation window:

```
R_stock = α + β × R_benchmark + ε
```

Where:
- `R_stock` is the daily log return of the stock
- `R_benchmark` is the daily log return of the appropriate market index
- `β` is the stock's sensitivity to the market (its beta)
- `α` is the stock's excess return independent of the market
- `ε` is the residual (what we want to study)

Benchmarks used:
- Prada (1913.HK) → Hang Seng Index (^HSI)
- LVMH, Kering, Hermès (Paris-listed) → EURO STOXX 50 (^STOXX50E)
- Capri, Tapestry, Estée Lauder (US-listed) → S&P 500 (^GSPC)

This is the **CAPM market model** — the simplest and most common baseline in event study research. It's not the most sophisticated model (you could add Fama-French factors, for example), but it's transparent and reproducible, which matters for a study like this.

---

### Step 4 — Compute abnormal returns and test significance

Once we have β and α from the estimation window, we apply them to each day in the event window:

```
Expected Return_t = α̂ + β̂ × R_benchmark_t
Abnormal Return_t = R_stock_t − Expected Return_t
CAR = Σ AR_t  for t in [-2, +5]
```

To test whether the CAR is meaningfully different from zero, we run a **t-test**:

```
t = mean(AR) / (std(AR) / √n)
```

Where n = 8 (the number of trading days in the event window). With df=7, we need |t| > 2.36 for p < 0.05. This is a high bar with only 8 observations — which is why we report near-significant results (p < 0.10) alongside significant ones.

---

## Part 2 — Data Collection

### Why three different sources?

No single source captures the full picture of cultural sentiment. Each has a different audience, a different signal type, and different timing characteristics:

| Source | Who | What | When |
|--------|-----|------|------|
| Reddit | Fashion enthusiasts, investors, film fans | Discussion, opinions, reactions | Real-time to days after |
| YouTube | Mass audience | Emotional reactions to trailers and clips | Days to weeks after viewing |
| Guardian | Professional journalists and critics | Considered editorial opinion | Hours to days after event |

Running all three lets us measure sentiment from three angles and compare them — which turns out to be as interesting as the sentiment data itself.

---

### Reddit — public JSON API

Reddit was collected using the public JSON search endpoint (`reddit.com/r/{subreddit}/search.json`) — no authentication required, completely free. We searched 8 subreddits with event-specific queries, collected posts within a ±7 day window around each event, and deduplicated by post ID.

**Why not use the official API?** Reddit overhauled its API pricing in 2023-24. Meaningful data volumes now require paid access. The public JSON endpoint gives the same data for read-only research use.

**Rate limiting:** 1.1-second delay between requests, with exponential backoff (30s → 60s → 120s → 240s) on HTTP 429 errors.

**Subreddits targeted:**
`r/fashion`, `r/femalefashionadvice`, `r/malefashionadvice`, `r/movies`, `r/boxoffice`, `r/investing`, `r/stocks`, `r/musicals`

---

### YouTube — Data API v3

The YouTube Data API (free, 10,000 units/day quota) was used to:
1. Search for relevant videos by keyword (5 queries, 10 results each = 50 search calls = 5,000 quota units)
2. Pull up to 200 top-level comments per video (1 unit per page of 100 comments)

41 unique videos were identified, yielding 3,141 comments.

**What you can get from YouTube API:**
- Comments (text, like count, date, author)
- Video metadata (title, view count snapshot, channel)
- Search results

**What you cannot get:**
- Historical view count time series (only current snapshot — the API doesn't expose this)
- Watch time or retention data (YouTube Analytics API only, requires OAuth as channel owner)

---

### Guardian — Open Platform API

The Guardian provides a free content API (500 calls/day limit, well within our needs) that returns full article text, section, publication date, and metadata. Articles were fetched using four boolean queries targeting film, luxury fashion, LVMH, and Kering coverage.

272 articles were collected and scored. The Guardian is valuable precisely because it represents *professional editorial sentiment* — a systematically different signal from social media enthusiasm.

---

### Stock data — yfinance

All price data was downloaded using `yfinance` with `auto_adjust=True` (split and dividend adjusted). Log returns were computed as `ln(P_t / P_{t-1})`.

Log returns are used instead of simple returns because:
1. They are time-additive (daily log returns sum to period log return)
2. They are approximately normally distributed for short intervals
3. They behave better in regression models

**Download period:** July 1, 2024 to present — providing 60+ estimation window days before the earliest event (West End previews, Oct 24, 2024).

---

## Part 3 — Sentiment Scoring with VADER

### What is VADER?

VADER (Valence Aware Dictionary and sEntiment Reasoner) is a lexicon and rule-based sentiment analysis tool specifically designed for social media text. It was developed at Georgia Tech (Hutto & Gilbert, 2014) and is one of the most widely cited sentiment tools in computational social science.

VADER returns a **compound score** in the range [-1, +1]:
- Near +1 = strongly positive
- Near 0 = neutral
- Near -1 = strongly negative

### Why VADER and not a large language model?

Three reasons:

**Speed:** VADER scores a sentence in microseconds. Scoring 50,000 sentences takes seconds. A transformer model (like FinBERT or GPT) takes seconds per sentence — prohibitive at this scale without GPU infrastructure.

**Social media calibration:** VADER was explicitly trained on tweets, Reddit posts, and product reviews. It handles slang, ALL CAPS emphasis, emoji, punctuation (!!! vs .) and negation correctly. "Not bad at all!!" scores correctly as positive.

**Reproducibility:** VADER is deterministic and has no training/inference stochasticity. Given the same input you always get the same output — important for research reproducibility.

We also attempted FinBERT (a BERT model fine-tuned on financial text), but the local installation had dependency conflicts. VADER is actually the *better* choice for this corpus anyway — Reddit posts are informal social language, not Bloomberg headlines.

### Upvote weighting

A Reddit post with 15,000 upvotes should carry more signal than one with 3 upvotes. Daily sentiment is computed as a weighted average:

```python
weighted_sentiment = Σ(score_i × weight_i) / Σ(weight_i)
weight_i = max(upvote_count_i, 1)  # floor at 1 to include zero-upvote posts
```

Similarly, YouTube comments are weighted by like count, so a highly-liked comment counts more than an unread one.

---

## Part 4 — Information Coefficient (IC)

The IC is how quantitative analysts measure whether a signal has predictive value. It is simply the **Pearson correlation** between the signal value at time t-1 and the return at time t, computed across all available observations.

```
IC = corr(sentiment_{t-1}, abnormal_return_t)
```

Industry benchmarks:
- IC < 0.02: essentially noise
- IC 0.02–0.05: weak but potentially exploitable at scale
- IC 0.05–0.10: meaningful single factor
- IC > 0.10: strong single factor (rare for social media data)

Our results:
- Reddit IC = **0.142** — above the "meaningful" threshold, not significant at n=52
- YouTube IC = **0.041** — weak, confirming comments lag price
- Guardian IC = **−0.176** — contrarian signal

The Rank IC (Spearman correlation) is also reported as a robustness check — it measures whether the *ranking* of sentiment scores predicts the *ranking* of returns, which is more robust to outliers than the raw Pearson correlation.

---

## Part 5 — VIX Regime Analysis

The VIX (CBOE Volatility Index) measures the market's expectation of 30-day implied volatility, derived from S&P 500 options prices. It is often called the "fear index":

- VIX < 15: calm, low-uncertainty market
- VIX 15–20: normal range
- VIX > 20: elevated uncertainty
- VIX > 30: fear / crisis regime

**Why does this matter for event studies?**

In high-volatility regimes, idiosyncratic signals (like fashion sentiment) are drowned out by macro noise. A stock that "should" react to positive cultural sentiment might move ±5% on the same day due to interest rate news, geopolitical risk, or sector rotation — completely independent of the event you're studying.

In low-volatility regimes, the signal-to-noise ratio is higher and event-specific effects are easier to detect.

Three of our five most interesting events (musical previews, musical opening, teaser trailer) occurred when VIX was between 14 and 18. The theatrical release and NYC premiere occurred when VIX was 24–28 — a period of significant macro volatility in spring 2026. This is a material confound for the film event null results.

---

## Part 6 — Sector Control (LUXE ETF)

The LUXE ETF (Roundhill Global Luxury ETF) holds a basket of global luxury goods companies. By computing the CAR of LUXE at each event and comparing it to individual tickers, we can ask:

> Did this stock outperform *because of the event*, or did the whole luxury sector move together?

```
Alpha_vs_sector = Ticker_CAR − LUXE_CAR
```

A positive alpha means the stock moved more than the luxury sector average — suggesting event-specific pricing, not just sector momentum. This matters for claiming causality rather than correlation with sector trends.

---

## Part 7 — The Backtest (Proof of Concept)

The simple backtest answers: *if you had traded on this signal, what would have happened?*

**Signal:** Average Reddit VADER score over the 5 days before each event.

**Position:**
- Signal > 0 → Long the basket (Prada + LVMH + Kering, equal weight)
- Signal ≤ 0 → Short the basket

**Measurement:** Equal-weight average log return of the basket over the [-2, +5] event window.

This is deliberately naive. In a production strategy you would account for transaction costs, market impact, position sizing, correlation between events, and borrow costs for short positions. The point here is to demonstrate the *framework* — that sentiment can be mechanically translated into a position — not to claim the strategy is profitable.

**The Sharpe ratio estimate from 7–9 events is statistically meaningless.** You need at minimum ~50 independent observations to have confidence in a Sharpe estimate. This is disclosed explicitly in the notebook.

---

## Part 8 — What We Can and Cannot Claim

### What we can claim:
- LVMH and Hermès showed statistically significant positive CARs (p < 0.05) in the West End musical preview week
- Reddit sentiment is significantly correlated with LVMH and Hermès returns on the same day (p < 0.05)
- Professional press sentiment (Guardian) and audience sentiment (YouTube/Reddit) systematically diverge for the film events
- The musical events generated cleaner signals than the film events, partly due to lower market volatility
- Reddit's IC of 0.142 is directionally consistent with commercial alternative data benchmarks

### What we cannot claim:
- That the film or musical *caused* the stock movements (correlation, not causation)
- That the backtest strategy is profitable out-of-sample (7 events is not enough)
- That the IC is statistically significant (it's not, at this sample size)
- That Prada benefited financially — it had no revenue stake in either production

### The honest null:
No significant abnormal returns were found for any film event (trailers, premiere, theatrical release). This is partly a statistical power problem (only 8 trading days per test), partly a timing problem (high VIX during film events), and partly a genuine null — cultural sentiment around a sequel may not be sufficient to move individual stocks in normal conditions.

Honest null results are a legitimate scientific contribution. The absence of a film stock effect is itself interesting given the enormous cultural footprint of the trailers (222M views in 24 hours for the full trailer).

---

## Technical Stack

| Component | Tool | Why |
|-----------|------|-----|
| Data collection | Python + requests | Flexible, reproducible |
| Stock data | yfinance | Free, reliable for this date range |
| Sentiment | VADER (vaderSentiment) | Calibrated for social media, fast |
| Market model | scikit-learn LinearRegression | Standard OLS, reproducible |
| Statistics | scipy.stats | t-tests, Pearson/Spearman correlation |
| Data manipulation | pandas + numpy | Standard scientific Python |
| Visualisation | matplotlib + seaborn | Publication-quality figures |
| Notebooks | Jupyter (executed via nbconvert) | Reproducible end-to-end pipeline |
| Version control | git | Full history, all data committed |

**Python version:** 3.9 (Anaconda). All `str | None` type hints use `from __future__ import annotations` for compatibility.

---

## Reproducibility

Every step of this analysis is reproducible from source:

```bash
git clone https://github.com/jsabazova/dwp2-luxury-sentiment
cd dwp2-luxury-sentiment

# Install dependencies
pip install -r requirements.txt

# Collect data (requires Guardian + YouTube API keys in .env)
python src/reddit_scraper.py
python src/guardian_scraper.py
python src/youtube_scraper.py
python src/stock_data.py

# Run sentiment scoring and event study
python src/sentiment.py
python src/event_study.py

# Execute all notebooks
for nb in notebooks/0*.ipynb; do
    jupyter nbconvert --to notebook --execute --inplace "$nb"
done
```

All raw data, processed outputs, and figures are committed to the repository. The analysis can be replicated in full or partially re-run as new events occur (e.g. re-running after the theatrical_release window completes in May 2026).
