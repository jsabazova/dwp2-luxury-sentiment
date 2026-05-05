# I Built a Sentiment Analysis Pipeline to Test Whether a Fashion Film Moves Luxury Stock Prices

**The Devil Wears Prada 2 dropped May 1. I dropped a research project the same week.**

Here's the question I'm trying to answer:

*Can social media sentiment around a fashion-coded cultural event predict short-term abnormal returns in luxury equities — even when the film has zero financial relationship with the brands it references?*

Prada S.p.A. had no stake in this film. No licensing deal. No product placement revenue. And yet every fashion editor, every finance Twitter account, and every person who owned a cerulean blue anything in 2006 was talking about this movie for six months before it released.

That's a sentiment signal. And sentiment moves markets — at least in the short term.

So I built a pipeline to test it.

---

## Why This Case Study Is Interesting

Most fashion-finance sentiment research focuses on earnings calls, brand partnerships, or direct promotional events. This is different.

The Devil Wears Prada 2 gave me something rare: **four clean, timestamped, high-magnitude sentiment events** with no confounding financial announcements attached.

- **Nov 12, 2025** — Teaser trailer. 181.5 million views in 24 hours.
- **Feb 1, 2026** — Full trailer. 222 million views in 24 hours — the most-viewed trailer in 20th Century Studios history.
- **Apr 20, 2026** — NYC Premiere, live-streamed globally.
- **May 1, 2026** — Theatrical release.

Each of these is a natural experiment. The question is whether luxury stock prices moved abnormally around them — and whether Reddit sentiment data predicted it.

---

## The Stock Universe

I tracked six tickers across three exchanges:

- **Prada (1913.HK)** — the obvious one, despite having no financial stake
- **LVMH (MC.PA)** — owns Dior, central to the original film's aesthetic
- **Kering (KER.PA)** — Gucci, Saint Laurent, Balenciaga
- **Capri Holdings (CPRI)** — Versace (Donatella had a cameo in the film)
- **Tapestry (TPR)** — Coach; included as an accessible luxury benchmark
- **Estée Lauder (EL)** — beauty/fashion adjacent; included as a control

The cross-exchange design is intentional. If a sentiment effect exists, it should show up across geographies — not just in US-listed names.

---

## The Sentiment Pipeline

### Data Source: Reddit (not X/Twitter)

The X/Twitter API is now prohibitively expensive for meaningful data volumes. Reddit via PRAW is free, well-documented, and actually better for this use case — the fashion and investing communities on Reddit produce high-volume, high-engagement discourse that correlates well with broader sentiment shifts.

Target subreddits: `r/fashion`, `r/femalefashionadvice`, `r/movies`, `r/boxoffice`, `r/investing`, `r/stocks`, `r/LVMH`.

Collection window: ±7 days around each event date.

### Two Models, Run in Parallel

**FinBERT** (ProsusAI) — a BERT model fine-tuned on financial text. Returns positive/neutral/negative with a confidence score. Best for posts discussing market reaction, brand valuation, stock movement.

**VADER** — lexicon-based, designed for social media language. Better at capturing fashion commentary, pop culture enthusiasm, and the kind of informal language that dominates Reddit threads. Returns a compound score in [-1, 1].

I'm running both and comparing. The hypothesis is that VADER will perform better on fashion/culture subreddits and FinBERT will perform better on finance subreddits — which itself is an interesting finding about model domain specificity.

### Aggregation

Daily sentiment is aggregated as a **weighted average**, with each post's weight proportional to its upvote score. A post with 10k upvotes carries more signal than one with 3.

```python
def daily_weighted_sentiment(df, score_col="sentiment", weight_col="score"):
    df["weighted"] = df[score_col] * df[weight_col].clip(lower=1)
    return df.groupby("date").apply(
        lambda x: x["weighted"].sum() / x[weight_col].clip(lower=1).sum()
    )
```

---

## The Event Study Framework

I'm using standard **event study methodology** from market microstructure research:

- **Estimation window:** [-60, -10] trading days before each event — used to estimate normal expected returns via a market model (CAPM)
- **Event window:** [-2, +5] trading days — captures both anticipation effects and post-event drift
- **Abnormal return:** actual return minus expected return from the market model
- **Cumulative Abnormal Return (CAR):** sum of daily ARs across the event window

Benchmarks: S&P 500 for US-listed stocks, STOXX Europe 600 for European names, Hang Seng for Prada.

The key test: **do t-1 and t-2 sentiment scores predict t abnormal returns?** A positive lag correlation would suggest sentiment leads price — which is the interesting finding for anyone thinking about fashion as an alternative data source.

---

## What I'm Expecting (and What Would Falsify It)

Honest priors:

**Most likely finding:** Weak or inconsistent correlation. Short-term stock prices are noisy, and cultural sentiment is one signal among thousands that move markets on any given day. Macro conditions, FX movements, and broader luxury sector momentum will dominate.

**Interesting positive finding:** A statistically significant CAR in the trailer drop windows (November and February) for LVMH and Kering — not Prada — because the film's visual references skew more toward those houses than toward Prada the brand directly.

**Most interesting finding:** No stock effect, but a clean sentiment time series that tracks the cultural moment. That's still a useful dataset and a valid null result worth publishing.

The null hypothesis — that sentiment has no significant relationship with luxury stock returns here — is entirely plausible and would be an honest finding.

---

## Why I Built This

Two reasons.

First, I work in trading and risk systems. Understanding how alternative data sources relate to price discovery is directly relevant to what I do — and building this pipeline is a better learning tool than reading about it.

Second, the intersection of fashion, culture, and quantitative finance is underexplored. There's serious academic work on earnings sentiment and social media. There's almost nothing on cultural event sentiment and luxury goods specifically. Even a clean null result contributes something.

---

## Results Coming Soon

The film released two days ago. I'm pulling data now. Results, visualisations, and the full write-up will follow once the event window closes and I've had time to run the analysis properly.

Code is on GitHub: [github.com/jsabazova/dwp2-luxury-sentiment](https://github.com/jsabazova/dwp2-luxury-sentiment)

If you're interested in the methodology, have run similar event studies, or have thoughts on the model selection — I'd genuinely love to hear from you.

---

*The cerulean is in the data now.*

---

## Production Notes — Visuals & Layout

### Suggested article structure

```
[Hero image: red heel installation outside Dominion Theatre, or NYC premiere red carpet]

Hook paragraph

[Chart: sentiment_timeseries.png — multi-source Reddit + YouTube + Guardian]

Methodology section

[Chart: car_heatmap.png — the money shot, all tickers × events]

Findings section

[Chart: price_performance.png — most accessible to non-quant readers]

Conclusion
```

### Figures to attach (already generated in results/figures/)

| File | Use for |
|------|---------|
| `car_heatmap.png` | Most visually striking — shows all tickers × events at a glance |
| `sentiment_timeseries.png` | Tells the story arc across all 3 data sources |
| `price_performance.png` | Accessible to non-quant readers |
| `post_volume.png` | Good for the "here's how I collected the data" section |

### Where to get imagery (no copyright issues)

**Movie / premiere:**
- Screenshot a frame from the official trailers on YouTube — editorial fair use
- Disney press release images from the NYC premiere are usable with attribution
- Search `site:prada.com` for official brand imagery

**Red heel shoe at Dominion Theatre:**
- Search `"Dominion Theatre" "devil wears prada" shoe` on Instagram or X
- Dozens of fans posted their own photos outside the theatre
- DM one for reshare permission — takes 2 minutes, people almost always say yes

**Prada runway:**
- `@prada` on Instagram posts every show publicly — taggable in LinkedIn
- Prada SS26 womenswear (Sep 2025) and FW26 (Feb 2026) are both relevant

**Getty free editorial embeds:**
- Getty offers free editorial embeds for non-commercial use
- Search "Devil Wears Prada musical" or "Prada 2026" at gettyimages.com
- Use their embed code directly in the LinkedIn article

### Key cross-source sentiment finding to highlight visually

The audience vs press divergence is the most visually interesting story:

- **YouTube audience** (trailer comments): +0.31 to +0.32 — positive throughout
- **Guardian press** (professional critics): -0.19 at NYC premiere, -0.08 at theatrical release
- **West End musical** (both sources agree): strongly positive

A simple bar chart comparing these three numbers side by side would make a clean, shareable visual that non-quants immediately understand.

---

**Tags:** #quantitativefinance #nlp #sentimentanalysis #alternativedata #luxurygoods #financialmarkets #python #machinelearning #eventdriven
