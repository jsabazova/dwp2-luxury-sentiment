# The Devil Wears Prada 2: Does Cultural Hype Move Luxury Stocks?
### A Research Note on Event-Driven Sentiment Analysis
*J. Sabazova — May 2026*

---

## The Question

On May 1, 2026, *The Devil Wears Prada 2* opened in US cinemas and grossed $115 million in its opening weekend. The film features Meryl Streep, Anne Hathaway, Donatella Versace, and the fashion world as its backdrop — the same aesthetic universe that made the original a cultural phenomenon in 2006.

Here is what makes this an interesting research case: **Prada S.p.A. has no financial stake in this film.** It is a Fox/Disney production. Prada the brand does not receive royalties, licensing fees, or any direct economic benefit from a film that carries its name in the title.

And yet — investors and analysts watching luxury stocks this week are asking the same question: did it move the needle?

This project attempts to answer that question with data.

---

## Why This Is Analytically Interesting

Most event studies in finance examine events with direct economic content — earnings surprises, M&A announcements, central bank decisions. The confounding challenge in all of them is separating signal from noise: did the stock move *because* of the event, or because of fifty other things that happened that week?

This case is different in a productive way. Because Prada has *no* direct financial relationship with the film, any measurable stock price effect cannot be fundamental. It would have to be entirely **sentiment-driven** — the product of investor and consumer psychology responding to cultural salience.

That makes the causal chain cleaner to reason about, even if not cleaner to measure:

```
Film hype → elevated social media sentiment about luxury/fashion
         → increased consumer interest in luxury brands
         → either (a) actual demand effect, or
                  (b) investor sentiment effect (or both)
         → short-term abnormal stock returns
```

A null result is equally informative: it would suggest that cultural associations — however loud on social media — do not translate into equity market movements in the absence of real earnings impact. That is itself a useful finding for the broader literature on sentiment investing.

---

## The Four Event Windows

What makes this study unusually well-structured is that the film provides **four distinct, timestamped events**, each with a clear before/after boundary:

**1. Teaser Trailer — November 12, 2025**
The teaser generated 181.5 million views in 24 hours, described as the most-viewed comedy trailer in 15 years. This is the first moment the market could price in the cultural event. If sentiment leads price, this is the most likely window to show it — it's the earliest, furthest from confounding macro events around the release date, and represents pure anticipation with no revenue data attached.

**2. Full Trailer — February 1, 2026**
222 million views in 24 hours — the most-viewed trailer in 20th Century Studios history. A second signal amplification event. The question here: does the market update on *more of the same* signal, or has the original shock already been priced in from November?

**3. NYC Premiere — April 20, 2026**
The premiere was live-streamed globally. Celebrity appearances, fashion coverage, and media saturation in the week prior. A softer signal — less about new information, more about sustained cultural saturation.

**4. Theatrical Release — May 1, 2026**
The release is the cleanest event for stock analysis because it comes with hard data: opening weekend box office ($115M) confirms the film is a genuine commercial event, not just social media noise. Analysis of this window is happening in real time as of this writing.

Running the same methodology across all four windows creates a **natural replication structure** — rare in event studies where a single event is typically all you have.

---

## Why These Stocks

The stock universe is deliberately constructed to test different proximity to the cultural signal:

| Ticker | Thesis |
|--------|--------|
| `1913.HK` Prada | Directly named in the film title. Highest expected signal, but listed on HKEx (UTC+8), which introduces timing friction relative to US social media sentiment. |
| `MC.PA` LVMH | Owns Dior, which featured heavily in the original film. Also the world's largest luxury conglomerate — functions as a sector proxy. |
| `KER.PA` Kering | Owns Gucci and Saint Laurent — less directly referenced, but deeply embedded in the same fashion-cultural world. A test of spill-over effects. |
| `CPRI` Capri Holdings | Owns Versace — Donatella Versace appears in the film as herself. This is the clearest direct association after Prada. |
| `TPR` Tapestry | Owns Coach — accessible luxury. If the sentiment effect is real, does it reach down-market? |
| `EL` Estée Lauder | Beauty/fashion-adjacent but not luxury fashion. A control: if EL moves similarly, the effect is broad market noise, not fashion-specific. |

The comparison between `CPRI` (Versace cameo, direct association) and `TPR` (no association) is particularly interesting. A significant difference in CARs between these two would be strong evidence that the signal is brand-specific, not just a broad luxury sector trade.

---

## Sentiment Data: Why Reddit

The X/Twitter Academic API now requires enterprise pricing that puts it out of reach for individual research projects. Reddit via PRAW is free, rate-limit generous, and — critically — covers the subreddits where fashion and investment sentiment actually intersect:

- `r/fashion`, `r/femalefashionadvice`: genuine consumer sentiment, fashion-native language
- `r/movies`, `r/boxoffice`: cultural reception, not brand-focused
- `r/investing`, `r/stocks`: where retail investors discuss market reactions explicitly

The limitation is real: Reddit skews English-speaking and Western, which may underweight sentiment relevant to `1913.HK` (Prada's primary exchange). A more complete study would incorporate Chinese-language social platforms (Xiaohongshu, Weibo) for the HKEx analysis. This is flagged as an honest caveat, not buried.

---

## Model Choice: FinBERT vs. VADER

Running two sentiment models in parallel is not just methodological belt-and-suspenders — it tests something meaningful:

**FinBERT** is trained on financial news and analyst reports. It will classify finance-specific language accurately ("Prada stock undervalued," "luxury sector rally") but may mishandle fashion-casual language ("obsessed with this coat," "runway looks incredible").

**VADER** is trained on social media language. It handles casual, emoji-heavy, hyperbolic text well but has no domain knowledge about financial sentiment.

Fashion-adjacent investment chatter sits in the overlap between these two domains. Comparing their outputs across the event windows tests whether the financial framing of posts (FinBERT-friendly) or the cultural/emotional framing (VADER-friendly) better predicts stock movements. That comparison is itself a finding.

---

## What the Analysis Will Show (and Won't)

**What we can measure:**
- Whether sentiment around each event date was significantly elevated vs. baseline
- Whether CARs in the event windows are statistically different from zero
- Whether lagged sentiment (t-1, t-2) is correlated with next-day abnormal returns

**What we cannot establish:**
- Causation. Sentiment and returns might both be responses to the same underlying factor (e.g. strong pre-release buzz causing both Reddit activity and institutional buying).
- Generalisability. Four events across one film is exploratory, not confirmatory. Any findings would need replication across other fashion-cultural events.

**The honest framing:**
If we find significant positive CARs, the interesting question is *which stocks* and *which events* — particularly whether Versace (direct cameo) outperforms Prada (title association only), and whether the trailer drops or the release produces stronger signals.

If we find no significant CARs, that is also a publishable result: it would suggest that cultural noise does not systematically translate into equity market signals, which has implications for sentiment-based trading strategies in consumer discretionary sectors.

---

## On Timing

This analysis is being written and run in the first week of May 2026 — days after the theatrical release. The May 1 event window is literally happening in real time. Reddit data for the release window is being collected while the film is still in its opening weekend.

This is not a post-hoc analysis of a past event. It is a live study. That's both its strength (no look-ahead bias in data collection) and its constraint (final results for the release window won't be complete until mid-May when the full +5 trading day window closes).

---

## Next Steps

1. **Data collection** — pull Reddit posts for all four event windows using PRAW (see `src/reddit_scraper.py`)
2. **Stock data** — download OHLCV via yfinance for all six tickers across all event windows
3. **Sentiment scoring** — run FinBERT and VADER on collected posts (see `src/sentiment.py`)
4. **Event study** — compute CARs using market-model expected returns (see `src/event_study.py`)
5. **Correlation analysis** — test sentiment lag → return relationship
6. **Visualisation** — CAR plots, sentiment time series, correlation heatmap (Notebook 05)

Results and findings will be written up as an addendum to this document once the May 1 event window closes (~May 8, 2026).

---

*Research and portfolio purposes only. Nothing herein constitutes financial advice.*
