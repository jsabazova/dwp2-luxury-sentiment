# 🎬 Devil Wears Prada 2: Fashion Sentiment & Luxury Stock Analysis

> *Does a fashion film move luxury stock prices — even when it has no financial stake in the brands it references?*

This project uses NLP sentiment analysis on social media data to examine whether the cultural hype around **The Devil Wears Prada 2** (released May 1, 2026) produced measurable short-term price effects on luxury fashion stocks — despite the film having no direct financial relationship with Prada S.p.A. or any other luxury house.

---

## 📌 Research Question

**Can sentiment derived from social media predict abnormal returns in luxury fashion equities around a high-profile fashion cultural event?**

Sub-questions:
- Does sentiment *lead* price movement, and by how many days?
- Which event window (trailer drop vs. premiere vs. release) produces the strongest signal?
- Is the effect concentrated in directly-referenced brands or does it spill over to the luxury sector broadly?

---

## 🎯 Hypothesis

A fashion-coded cultural event generates elevated positive sentiment toward luxury goods broadly. This sentiment shift is detectable in social media data and precedes (or coincides with) short-term abnormal returns in luxury fashion equities — even in the absence of any direct financial relationship between the film and the brands.

**Null hypothesis:** Sentiment around the film has no statistically significant relationship with luxury stock returns in the event windows studied.

---

## 📅 Event Windows

The film provides four clean, timestamped sentiment events — ideal for event-driven analysis:

| Event | Date | Notes |
|---|---|---|
| Teaser trailer | Nov 12, 2025 | 181.5M views in 24hrs — most-viewed comedy trailer in 15 years |
| Full trailer | Feb 1, 2026 | 222M views in 24hrs — most-viewed trailer in 20th Century Studios history |
| NYC Premiere | Apr 20, 2026 | Live-streamed on Disney+ and Hulu |
| Theatrical release | May 1, 2026 | US opening weekend |

For each event, the analysis window is **[-2, +5] trading days** around the event date.

---

## 📈 Stock Universe

| Ticker | Exchange | Company | Relevance |
|---|---|---|---|
| `1913.HK` | HKEx | Prada S.p.A. | Film named after brand |
| `MC.PA` | Euronext Paris | LVMH | Owns Dior (featured in original film); largest luxury conglomerate |
| `KER.PA` | Euronext Paris | Kering | Owns Gucci, Saint Laurent, Balenciaga |
| `CPRI` | NYSE | Capri Holdings | Owns Versace (Donatella Versace cameo in film) |
| `TPR` | NYSE | Tapestry | Owns Coach — accessible luxury benchmark |
| `EL` | NYSE | Estée Lauder | Beauty/fashion adjacent; control stock |

**Note on Prada:** Prada has no financial stake in the film. Any correlation is purely a cultural sentiment effect — which is the analytically interesting finding either way.

---

## 🗂️ Project Structure

```
dwp2-fashion-sentiment/
│
├── data/
│   ├── raw/
│   │   ├── reddit/          # Raw Reddit JSON from PRAW
│   │   └── stocks/          # Raw OHLCV data from yfinance
│   ├── processed/
│   │   ├── sentiment_scores.csv
│   │   └── stock_returns.csv
│   └── README.md            # Data dictionary
│
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_sentiment_analysis.ipynb
│   ├── 03_stock_returns.ipynb
│   ├── 04_event_study.ipynb
│   └── 05_results_visualisation.ipynb
│
├── src/
│   ├── reddit_scraper.py
│   ├── sentiment.py
│   ├── stock_data.py
│   ├── event_study.py
│   └── utils.py
│
├── results/
│   ├── figures/
│   └── tables/
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🛠️ Methodology

### 1. Sentiment Data Collection

**Source:** Reddit (free, no rate-limiting issues unlike X/Twitter API)

**Target subreddits:**
- `r/fashion`, `r/femalefashionadvice`, `r/malefashionadvice`
- `r/movies`, `r/boxoffice`
- `r/investing`, `r/stocks` (for market reaction commentary)
- `r/LVMH`, `r/Prada` (brand-specific)

**Tool:** PRAW (Python Reddit API Wrapper)

**Collection window:** 7 days before and after each event date

```python
import praw
import pandas as pd

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="dwp2-sentiment-analysis"
)

def scrape_subreddit(subreddit_name, query, start_date, end_date, limit=500):
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    for post in subreddit.search(query, time_filter="month", limit=limit):
        posts.append({
            "title": post.title,
            "text": post.selftext,
            "score": post.score,
            "created_utc": post.created_utc,
            "num_comments": post.num_comments
        })
    return pd.DataFrame(posts)
```

**Search queries:** `"devil wears prada"`, `"devil wears prada 2"`, `"prada film"`, `"runway magazine film"`, `"miranda priestly"`

---

### 2. Sentiment Scoring

Two models are run in parallel and compared:

#### FinBERT (finance-tuned BERT)
Best for: posts discussing stocks, returns, brand valuation, market reaction

```python
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline

tokenizer = BertTokenizer.from_pretrained("ProsusAI/finbert")
model = BertForSequenceClassification.from_pretrained("ProsusAI/finbert")
nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

def score_finbert(text):
    result = nlp(text[:512])[0]  # FinBERT max 512 tokens
    label_map = {"positive": 1, "neutral": 0, "negative": -1}
    return label_map[result["label"]] * result["score"]
```

#### VADER (Valence Aware Dictionary and sEntiment Reasoner)
Best for: casual social media language, fashion commentary, pop culture posts

```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def score_vader(text):
    return analyzer.polarity_scores(text)["compound"]  # Range: [-1, 1]
```

**Aggregation:** Daily weighted-average sentiment score, weighted by post upvote score (higher-engagement posts carry more weight).

```python
def daily_weighted_sentiment(df, score_col="sentiment", weight_col="score"):
    df["weighted"] = df[score_col] * df[weight_col].clip(lower=1)
    return df.groupby("date").apply(
        lambda x: x["weighted"].sum() / x[weight_col].clip(lower=1).sum()
    )
```

---

### 3. Stock Price Data

```python
import yfinance as yf

tickers = ["1913.HK", "MC.PA", "KER.PA", "CPRI", "TPR", "EL"]

def get_returns(tickers, start, end):
    data = yf.download(tickers, start=start, end=end, auto_adjust=True)["Close"]
    returns = data.pct_change().dropna()
    return returns
```

**Abnormal returns** are calculated relative to a market benchmark:
- US-listed stocks: S&P 500 (`^GSPC`)
- European stocks: STOXX Europe 600 (`^STOXX`)
- HK-listed stocks: Hang Seng Index (`^HSI`)

```
Abnormal Return = Actual Return - Expected Return (CAPM or market-model)
Cumulative Abnormal Return (CAR) = sum of ARs over event window
```

---

### 4. Event Study

Classic market microstructure event study methodology:

1. **Estimation window:** [-60, -10] trading days before each event (used to estimate normal returns)
2. **Event window:** [-2, +5] trading days around each event
3. **Test statistic:** t-test on CARs across the four events

```python
def compute_car(returns, benchmark_returns, event_date, window=(-2, 5)):
    # Estimate beta from estimation window
    estimation = returns[event_date - 60 : event_date - 10]
    beta = np.cov(estimation, benchmark_returns[estimation.index])[0,1] / \
           np.var(benchmark_returns[estimation.index])
    
    # Compute abnormal returns in event window
    event = returns[event_date + window[0] : event_date + window[1]]
    expected = benchmark_returns[event.index] * beta
    ar = event - expected
    return ar.cumsum()
```

---

### 5. Sentiment–Return Correlation

**Key test:** Does *t-1* or *t-2* sentiment predict *t* abnormal returns?

```python
from scipy.stats import pearsonr, spearmanr

# Lag sentiment by 1 and 2 days
for lag in [0, 1, 2]:
    lagged_sentiment = sentiment_series.shift(lag)
    aligned = pd.concat([lagged_sentiment, abnormal_returns], axis=1).dropna()
    r, p = pearsonr(aligned.iloc[:, 0], aligned.iloc[:, 1])
    print(f"Lag {lag}: r={r:.3f}, p={p:.3f}")
```

---

## 📦 Dependencies

```
# requirements.txt
praw>=7.7.0
yfinance>=0.2.36
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.11.0
transformers>=4.40.0
torch>=2.0.0
vaderSentiment>=3.3.2
matplotlib>=3.7.0
seaborn>=0.12.0
jupyter>=1.0.0
python-dotenv>=1.0.0
scikit-learn>=1.3.0
statsmodels>=0.14.0
```

Install:
```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Setup

Copy `.env.example` to `.env` and fill in your credentials:

```bash
# .env.example
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=dwp2-sentiment/1.0
```

Reddit API credentials are free — register at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).

---

## 📊 Expected Outputs

- **Sentiment time series** plots for each event window
- **CAR plots** for each stock across each event window
- **Correlation heatmap** — sentiment lag vs. abnormal return by stock
- **Summary statistics table** — mean CAR, t-stat, p-value per event
- **Key finding narrative** — did sentiment lead price? Which stocks? Which events?

---

## ⚠️ Limitations & Honest Caveats

- **Prada has no financial stake in the film** — any correlation is cultural, not fundamental
- **Reddit ≠ X/Twitter** — skews toward English-speaking, US/UK audiences; may underweight Asian sentiment relevant to HKEx-listed Prada
- **Short-term stock prediction is noisy** — macro conditions (Fed decisions, FX moves) can swamp cultural signals in any given window
- **Small event sample** — four events is not enough for robust statistical inference; findings should be framed as exploratory
- **Survivorship / selection** — we chose these stocks because they're fashion-adjacent; null results are equally valid and interesting

---

## 🔭 Extensions (Future Work)

- Add X/Twitter data if API access becomes affordable
- Expand to Google Trends as a free, high-volume sentiment proxy
- Test on other fashion-coded cultural events (Met Gala, major fashion weeks, brand campaigns)
- Build a generalised "fashion sentiment → luxury equity" signal pipeline
- Compare FinBERT vs. VADER performance on fashion-specific language

---

## 👤 Author

**J. Sabazova**  
Quantitative analysis | NLP | Financial markets  
[GitHub](https://github.com/jsabazova) · [LinkedIn](https://linkedin.com/in/jamila-sabazova)

---

## 📄 License

MIT License — see `LICENSE` for details.

---

*This project is for research and portfolio purposes only. Nothing in this repository constitutes financial advice.*
