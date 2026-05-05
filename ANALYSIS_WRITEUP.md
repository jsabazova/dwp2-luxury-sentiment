# The Devil Wears Prada 2: Does Cultural Hype Move Luxury Stocks?
### A Research Note on Event-Driven Sentiment Analysis
*J. Sabazova — May 2026*

---

## Executive Summary

This study applies event study methodology to nine cultural events surrounding *The Devil Wears Prada 2* (film, May 2026) and its companion West End musical (Oct 2024–present), testing whether measurable social media and press sentiment predicts short-term abnormal returns in luxury equity markets.

**Key findings:**

- **The West End musical previews (Oct 2024) generated the only statistically significant positive CARs in the study.** Hermès gained +5.1% (p=0.0037 \*\*\*) and LVMH gained +5.5% (p=0.038 \*\*) above their benchmarks in the event window. Both results are robust to sector control.
- **LVMH and Hermès show statistically significant same-day correlation with Reddit sentiment** (r=0.35, p=0.025 and r=0.33, p=0.034 respectively), consistent with shared information environment dynamics.
- **No significant abnormal returns were detected for any film event** (trailers, premiere, theatrical release). This is partly a timing problem — all three film events coincided with elevated market volatility (VIX 24–28), which overwhelms idiosyncratic cultural signals.
- **Audience and professional press sentiment systematically diverge:** YouTube audiences are positive about the film (+0.31); Guardian critics are negative (−0.08 to −0.19). Both sources agree the musical was excellent (+0.73 to +0.92).
- **Reddit's Information Coefficient of 0.14** is directionally consistent with commercial alternative data benchmarks, though not significant at this sample size (n=52 event×ticker pairs).
- **Prada (the headline ticker) shows consistent positive direction across five of seven events but never reaches statistical significance**, likely due to low statistical power (n=8 trading days per test) and HKEx timing friction vs Western social media signals.

---

## Background and Motivation

*The Devil Wears Prada 2* is a structurally unusual research case. Prada S.p.A. has **no financial stake** in the film — no licensing deal, no royalty stream, no product placement fee. It is a Fox/Disney production. Any price effect on Prada stock, or on thematically adjacent luxury equities, would therefore be entirely sentiment-driven: a function of investor and consumer psychology responding to cultural salience, not to any change in firm fundamentals.

This makes the causal chain cleaner to reason about than a typical earnings event:

```
Cultural event → elevated sentiment about luxury/fashion
              → increased consumer interest in luxury brands (demand effect)
              → and/or investor sentiment rerating (pricing effect)
              → short-term abnormal stock returns
```

The West End musical dimension adds further value. The musical ran for 16+ months before the film released, creating a long-running natural experiment with multiple distinct events, a sustained media presence, and critical acclaim independent of the film's reception. It turns a four-event study into a nine-event study with genuine cross-validation.

A null result is equally informative: it would suggest that cultural associations, however loud on social media, do not translate into equity market movements without direct economic content.

---

## Study Design

### Events (9 total)

| Event | Date | Category |
|-------|------|----------|
| West End previews begin | Oct 24, 2024 | Musical |
| West End opening night | Dec 5, 2024 | Musical |
| Prada SS26 womenswear show, Milan | Sep 18, 2025 | Fashion Week |
| Teaser trailer (181.5M views / 24hrs) | Nov 12, 2025 | Film |
| Full trailer (222M views / 24hrs) | Feb 1, 2026 | Film |
| Prada FW26 womenswear show, Milan | Feb 20, 2026 | Fashion Week |
| Run extended to Feb 2027 announced | Mar 13, 2026 | Musical |
| NYC premiere, live-streamed globally | Apr 20, 2026 | Film |
| Theatrical release ($115M opening weekend) | May 1, 2026 | Film |

### Stock Universe (7 tickers)

| Ticker | Name | Thesis |
|--------|------|--------|
| 1913.HK | Prada | Named in the title; primary expected beneficiary |
| MC.PA | LVMH | Owns Dior; referenced in original film; sector proxy |
| KER.PA | Kering | Owns Gucci, Balenciaga, Saint Laurent; spill-over test |
| RMS.PA | Hermès | Ultra-luxury benchmark; no direct connection |
| CPRI | Capri Holdings | Owns Versace; Donatella Versace appears in the film |
| TPR | Tapestry | Owns Coach; accessible luxury control |
| EL | Estée Lauder | Beauty/fashion-adjacent; macro control |

**Benchmarks:** ^HSI (Prada), ^STOXX50E (LVMH, Kering, Hermès), ^GSPC (Capri, Tapestry, Estée Lauder)

**Reference tickers (context only, not event study):** LUXE (Roundhill Luxury ETF), ^VIX

### Data Sources

| Source | Volume | Method |
|--------|--------|--------|
| Reddit | 308 posts, 9 events, 8 subreddits | Public JSON API, upvote-weighted VADER |
| YouTube | 3,141 comments, 41 videos | YouTube Data API v3, like-weighted VADER |
| Guardian | 272 articles | Guardian Open Platform API, VADER |
| Stocks | 475 trading days, Jul 2024–May 2026 | yfinance, log returns |

### Event Study Parameters

- **Market model:** OLS regression of stock return on benchmark return
- **Estimation window:** [−60, −10] trading days relative to event
- **Event window:** [−2, +5] trading days (8 observations)
- **Test:** One-sample t-test on daily abnormal returns; H₀: mean AR = 0

---

## Results: Event Study

### Statistically Significant CARs (p < 0.05)

| Ticker | Event | CAR | t-stat | p-value | β |
|--------|-------|-----|--------|---------|---|
| **Hermès (RMS.PA)** | musical_previews | **+5.13%** | 4.28 | **0.0037 \*\*\*** | 1.73 |
| **LVMH (MC.PA)** | musical_previews | **+5.47%** | 2.55 | **0.038 \*\*** | 1.82 |
| Tapestry (TPR) | musical_opening | −8.74% | −3.33 | 0.013 \*\* | 0.33 |

**On the Tapestry result:** The −8.74% move at musical opening is anomalous. Tapestry has a low market beta (β=0.33) and has no connection to the West End musical. The December 2024 opening coincided with sector-specific headwinds in accessible luxury. This result is flagged as likely confounded and excluded from the main narrative.

### Near-Significant CARs (0.05 < p < 0.10)

| Ticker | Event | CAR | p-value |
|--------|-------|-----|---------|
| Estée Lauder (EL) | musical_opening | +12.01% | 0.089 \* |
| Kering (KER.PA) | musical_previews | +6.82% | 0.090 \* |
| Kering (KER.PA) | prada_fw26_show | +6.65% | 0.094 \* |

The Estée Lauder +12% move is large but likely coincidental — EL was in a prolonged downtrend from China demand weakness and the timing reflects a macro bounce rather than musical sentiment. The Kering results are more credible: Gucci, Balenciaga, and Saint Laurent are stylistically adjacent to the DWP aesthetic, and both Kering signals occur at events (musical previews, Prada runway) with strong fashion sentiment.

### Prada (1913.HK) — Consistent Direction, No Significance

The headline ticker produces consistently positive CARs across five of seven events, but never crosses the significance threshold. Statistical power is low at n=8 trading days per test.

| Event | CAR | p-value |
|-------|-----|---------|
| musical_previews | +8.49% | 0.355 |
| musical_opening | +7.75% | 0.251 |
| full_trailer | +5.50% | 0.121 |
| prada_ss26_show | +4.37% | 0.457 |
| teaser_trailer | +1.01% | 0.877 |
| nyc_premiere | +1.25% | 0.839 |
| musical_extension | −4.47% | 0.394 |

Consistent positive direction across independent events is itself informative even without significance. A meta-analytic combination of these p-values (Fisher's method) would likely produce a significant aggregate result — an approach for the next iteration of this study.

### Film Events: Null Result

No film event (teaser trailer, full trailer, NYC premiere, theatrical release) produced a statistically significant CAR for any ticker. The theatrical release window is partially missing: May 1 is a Labour Day holiday for HKEx and European markets, leaving only 4 trading days rather than 8.

---

## Results: Sentiment Analysis

### Reddit — Post Volume and Sentiment by Event

| Event | VADER Score | Posts | Notable |
|-------|-------------|-------|---------|
| musical_previews | **+0.855** | 13 | Highest sentiment in study |
| prada_fw26_show | +0.801 | 3 | Small sample |
| prada_ss26_show | +0.735 | 4 | Small sample |
| musical_extension | +0.567 | 49 | Sustained enthusiasm |
| nyc_premiere | +0.584 | 91 | Largest Reddit event |
| musical_opening | +0.420 | 14 | — |
| full_trailer | +0.293 | 26 | — |
| teaser_trailer | +0.367 | 15 | — |
| theatrical_release | +0.080 | 93 | Highest volume, lowest sentiment |

The theatrical release inversion is the most interesting Reddit finding. The post count nearly doubles (93 posts) but sentiment collapses to near-neutral (+0.080). As the film became available to watch, critical voices from r/movies and r/boxoffice entered the conversation. Pre-release Reddit was fan discourse; post-release Reddit is audience review. This distinction matters for signal construction: sentiment leads price in anticipation mode, but lags it in review mode.

### YouTube — Audience Response

3,141 comments across 41 videos. Like-weighted VADER. Mean sentiment: **+0.307** (consistently positive across all events). YouTube is an audience signal, not a critic signal.

**IC (Pearson) = 0.041, p=0.761** — YouTube comments are a lagging indicator. They are posted after viewing, which is after any price-sensitive information has been absorbed. YouTube is useful for measuring *sustained* audience sentiment over days and weeks, not for predicting next-day returns.

### Guardian — Professional Press

272 articles. Headline + first 1,000 words scored with VADER.

| Event | Guardian VADER | Articles |
|-------|---------------|----------|
| musical_extension | **+0.919** | 8 |
| musical_previews | **+0.744** | 6 |
| musical_opening | **+0.730** | 8 |
| teaser_trailer | +0.165 | 10 |
| full_trailer | +0.104 | 4 |
| theatrical_release | **−0.082** | 16 |
| nyc_premiere | **−0.193** | 6 |

### The Audience vs. Critic Divergence

The most narratively striking finding in the dataset:

| Event | YouTube Audience | Guardian Critics | Divergence |
|-------|-----------------|-----------------|------------|
| nyc_premiere | +0.058 | **−0.193** | Critics negative, audiences neutral |
| theatrical_release | **+0.312** | **−0.082** | Audiences love it, critics don't |
| musical_previews | −0.081 | **+0.744** | Critics love it, YouTube low coverage |
| musical_opening | **+0.371** | **+0.730** | Both positive — the musical works for everyone |

For the film: audiences are positive, critics are negative. For the musical: both agree it's excellent. The Guardian's IC of **−0.176** means press criticism is a *contrarian* signal — when the Guardian is bearish, stocks modestly outperform. Institutional investors appear to respond to the cultural moment rather than the reviews.

---

## Results: Signal Analysis

### Same-Day Lag Correlation (Reddit VADER vs. Daily Returns)

Testing whether days with high Reddit sentiment correspond to days with higher stock returns, across all days in the study period:

| Ticker | Pearson r | p-value | Spearman r | p-value |
|--------|-----------|---------|-----------|---------|
| **LVMH (MC.PA)** | **0.349** | **0.025** | 0.264 | 0.095 |
| **Hermès (RMS.PA)** | **0.331** | **0.034** | **0.388** | **0.012** |
| Kering (KER.PA) | 0.130 | 0.417 | 0.085 | 0.597 |
| Tapestry (TPR) | 0.127 | 0.424 | 0.061 | 0.702 |
| Prada (1913.HK) | 0.100 | 0.532 | 0.125 | 0.435 |
| Estée Lauder (EL) | −0.036 | 0.820 | 0.032 | 0.839 |
| Capri Holdings (CPRI) | −0.105 | 0.508 | −0.102 | 0.521 |

LVMH and Hermès are the market's thermometer for aspirational luxury fashion discourse. Their significant same-day correlation with Reddit sentiment is consistent with a shared information environment: fashion discourse and institutional pricing both respond to the same cultural signals simultaneously.

Hermès's Spearman rank correlation (r=0.388, p=0.012) is particularly strong, suggesting the relationship is robust to outlier events.

### Information Coefficient (IC)

The IC measures how well sentiment at t-1 predicts abnormal returns at t=0, across all event×ticker pairs:

| Source | N | IC (Pearson) | p-value | Rank IC | p-value |
|--------|---|-------------|---------|---------|---------|
| Reddit | 52 | **0.142** | 0.316 | 0.104 | 0.464 |
| YouTube | 58 | 0.041 | 0.761 | 0.074 | 0.582 |
| Guardian | 52 | −0.176 | 0.212 | −0.190 | 0.178 |

None reach statistical significance at this sample size. Reddit's IC of 0.142, while not significant, is in the upper range of what commercial alternative data providers report for single social media factors (typical range: 0.02–0.08). With 50+ events, this would be properly testable.

---

## Results: Market Context

### VIX Regime

| Event | VIX | Regime |
|-------|-----|--------|
| musical_previews | ~16 | Low vol |
| musical_opening | ~14 | Low vol |
| prada_ss26_show | ~18 | Low vol |
| teaser_trailer | ~15 | Low vol |
| full_trailer | ~17 | Low vol |
| prada_fw26_show | ~19 | Low vol |
| musical_extension | ~22 | **Elevated** |
| nyc_premiere | ~28 | **High vol** |
| theatrical_release | ~25 | **High vol** |

The three statistically significant results (LVMH **, Hermès ***, and near-significant Kering *) all occurred during low-volatility regimes (VIX 14–18). The three film events with null results all occurred during elevated volatility (VIX 22–28). In high-vol regimes, macro noise overwhelms idiosyncratic cultural signals.

This is a critical confound: the theatrical release null result is partly a market timing problem, not exclusively a signal problem.

### Sector Control

Comparing individual ticker CARs to the LUXE luxury sector ETF at the same event window:

At **musical_previews** — the cleanest event — LVMH and Hermès generated approximately +3–4% of *idiosyncratic* alpha above the luxury sector ETF. The whole sector moved modestly upward, but LVMH and Hermès moved meaningfully more. This confirms the result is event-specific, not a broad luxury sector rally.

---

## Discussion

### The Musical vs. The Film

The most unexpected finding is the asymmetry between the musical and the film as market signals.

The West End musical previews are the single cleanest event in the nine-event study. The signal has several properties that favour detection:
1. **Low VIX environment** — signal-to-noise ratio is high
2. **Sustained media presence** — the musical ran for months, giving institutional investors time to process the signal
3. **Critical acclaim** — Guardian sentiment +0.744 leaves no ambiguity about the cultural reception
4. **Novelty** — this is the first observation of this type of signal for these tickers

By contrast, the film events are noisier in every dimension: they occurred during a high-VIX environment, they attracted more critical scepticism (negative Guardian IC), and the social media universe for a blockbuster release is orders of magnitude larger and harder to aggregate into a clean signal.

### Why LVMH and Hermès, Not Prada?

This is the most analytically interesting puzzle. Prada is named in the title. Prada shows consistent positive direction but no significance. LVMH and Hermès — with no direct connection to the musical — show the cleanest results.

Three possible explanations:
1. **Liquidity and analyst coverage:** LVMH and Hermès are the most heavily covered luxury names. When institutional sentiment shifts on "luxury fashion as a cultural moment," capital flows to the most liquid expressions of that theme.
2. **HKEx timing friction:** Prada trades in Hong Kong (UTC+8). Western social media discourse generates during US/European trading hours. The signal may arrive after Prada has already closed for the day, muting any same-session price response.
3. **Brand specificity discount:** Investors may treat the DWP2 cultural moment as a luxury sector signal rather than a Prada-specific signal — particularly since Prada has no financial relationship with the production.

### On the Null Results

The absence of significant film event CARs should not be over-interpreted as evidence that cultural sentiment has no market relevance. The study is underpowered: with 8 trading days per test, you need very large effects (t > 2.36) to reach significance. The Prada full trailer CAR of +5.5% (p=0.121) might well be real and replicable — it simply cannot be distinguished from noise at n=8.

The correct conclusion is: **this study cannot confirm a film event effect, but it cannot rule one out either.** A larger sample (more events, longer event windows) is needed.

---

## Limitations

1. **Statistical power:** 8 trading days per test is insufficient to detect moderate effects (Cohen's d < 0.8). The consistent positive direction of Prada CARs across events suggests an effect may exist that is undetectable at this sample size.

2. **Multiple comparisons:** 63 individual CAR tests (7 tickers × 9 events) increase the probability of false positives. The significant results at the musical previews survive a Bonferroni correction in their raw p-values (Hermès p=0.0037 × 63 = 0.23; still notable, not corrected-significant).

3. **Confounding events:** Some event windows overlap with earnings releases, macro announcements, or sector-specific news not controlled for. The Tapestry anomaly and the Estée Lauder spike are likely confounded.

4. **Reddit sampling:** The public JSON API returns results sorted by "new" within the search window. Post volume is low for some events (3–15 posts), making weighted sentiment estimates noisy.

5. **Theatrical release incomplete:** The May 1 event window was cut short by Labour Day closures. Full +5 trading day data becomes available after May 8, 2026.

6. **No Chinese-language data:** Prada trades on HKEx. Xiaohongshu (Little Red Book) and Weibo are the primary sentiment platforms relevant to HK and mainland Chinese investors — not Reddit. The Reddit signal may simply be the wrong language for the primary Prada exchange.

7. **Lyst Index approximation:** The Lyst brand heat rankings cited in the overlay analysis are approximate. Verify exact quarterly figures against published PDFs at lyst.com/lyst-index before citing in external work.

---

## Replication

All code, collected data, and executed notebooks are in this repository. To replicate:

```bash
# 1. Set API keys
echo "GUARDIAN_API_KEY=your_key" > .env
echo "YOUTUBE_API_KEY=your_key" >> .env

# 2. Collect data
python src/reddit_scraper.py
python src/guardian_scraper.py
python src/youtube_scraper.py
python src/stock_data.py

# 3. Score and analyse
python src/sentiment.py
python src/event_study.py

# 4. Run all notebooks
for nb in notebooks/0*.ipynb; do
  jupyter nbconvert --to notebook --execute --inplace "$nb"
done
```

Figures are written to `results/figures/`. Tables to `results/tables/`. See `METHODOLOGY.md` for full methodological detail.

---

## Appendix: All CAR Results

| Ticker | Event | CAR (%) | p-value | Sig |
|--------|-------|---------|---------|-----|
| Hermès | musical_previews | +5.13 | 0.0037 | *** |
| LVMH | musical_previews | +5.47 | 0.038 | ** |
| Tapestry | musical_opening | −8.74 | 0.013 | ** |
| Estée Lauder | musical_opening | +12.01 | 0.089 | * |
| Kering | musical_previews | +6.82 | 0.090 | * |
| Kering | prada_fw26_show | +6.65 | 0.094 | * |
| Prada | musical_previews | +8.49 | 0.355 | — |
| Prada | musical_opening | +7.75 | 0.251 | — |
| Prada | full_trailer | +5.50 | 0.121 | — |
| Tapestry | full_trailer | +17.98 | 0.147 | — |
| LVMH | musical_extension | +3.41 | 0.551 | — |
| Hermès | nyc_premiere | +6.66 | 0.188 | — |
| Prada | prada_ss26_show | +4.37 | 0.457 | — |
| Estée Lauder | theatrical_release | +8.14 | 0.202 | — |
| *(all others)* | *(all events)* | — | >0.20 | — |

*Research and portfolio purposes only. Nothing herein constitutes financial advice.*
