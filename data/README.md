# Data Dictionary

## data/raw/reddit/
One CSV per event window. Filename format: `{event_name}.csv`

| Column | Type | Description |
|--------|------|-------------|
| `id` | str | Reddit post ID (unique) |
| `subreddit` | str | Subreddit name |
| `title` | str | Post title |
| `text` | str | Post body (selftext) |
| `combined_text` | str | title + " " + text (used for scoring) |
| `score` | int | Upvote score at time of collection |
| `num_comments` | int | Comment count |
| `created_utc` | float | Unix timestamp of post creation |
| `date` | date | Date extracted from created_utc |
| `query` | str | Search query that returned this post |
| `event` | str | Event name this post was collected for |

## data/raw/stocks/
- `prices.csv` — daily adjusted close prices for all tickers + benchmarks
- `returns.csv` — daily log returns computed from prices

| Column | Description |
|--------|-------------|
| `date` | Trading date |
| `1913.HK` | Prada adjusted close |
| `MC.PA` | LVMH adjusted close |
| `KER.PA` | Kering adjusted close |
| `CPRI` | Capri Holdings adjusted close |
| `TPR` | Tapestry adjusted close |
| `EL` | Estée Lauder adjusted close |
| `^GSPC` | S&P 500 (US benchmark) |
| `^STOXX50E` | STOXX Europe 50 (EU benchmark) |
| `^HSI` | Hang Seng Index (HK benchmark) |

## data/processed/
- `sentiment_scores.csv` — daily weighted sentiment per event
- `car_results.csv` — cumulative abnormal returns per ticker × event

### sentiment_scores.csv

| Column | Description |
|--------|-------------|
| `date` | Date |
| `event` | Event name |
| `vader_score` | Weighted daily VADER compound score |
| `finbert_score` | Weighted daily FinBERT score |
| `post_count` | Number of posts that day |
| `total_weight` | Sum of upvote weights |

### car_results.csv

| Column | Description |
|--------|-------------|
| `ticker` | Stock ticker |
| `event` | Event name |
| `event_date` | Event date |
| `day` | Trading day relative to event (−2 to +5) |
| `ar` | Abnormal return for that day |
| `car` | Cumulative abnormal return up to that day |
| `beta` | Beta estimated from estimation window |
