# TikTok / Instagram Content Plan
## Devil Wears Prada 2 × Luxury Stocks Project

---

## The Core Format

**You are the unreliable narrator of your own research.**
Deadpan. Slightly unhinged. But the code actually runs.

The bit: present genuinely serious quantitative work in the voice of someone who watched a fashion film and made it everyone else's problem.

---

## Video 1 — The Hook (Post NOW, this week)

**Title:** "I watched Devil Wears Prada 2 and immediately opened my terminal"

**Format:** Talking head or screen record, 30–45 seconds

**Script:**
> "So I watched Devil Wears Prada 2 on the weekend.
> Normal people left thinking about Anne Hathaway's wardrobe.
> I left thinking about whether the trailer drop in November caused abnormal returns in LVMH stock.
> So I built a sentiment analysis pipeline to find out.
> Because that's a normal and healthy response to a comedy film."

**Visual:** Cut between the movie poster / trailer clip → your terminal → yfinance stock chart → FinBERT output

**Hook line on screen:** *"The cerulean is in the data now"*

**Why post now:** The film just released. You're riding peak cultural conversation. This video gets the algorithm on your side before results exist.

---

## Video 2 — The Method (Post in ~1 week)

**Title:** "How I'm actually doing this (it's not that complicated)"

**Format:** Screen record with voiceover, 60–90 seconds

**Structure:**
1. "Step one — I'm not paying for the Twitter API. Reddit is free and honestly better." → show PRAW scraping live
2. "Step two — two sentiment models because I couldn't decide." → show FinBERT vs VADER output side by side on the same post
3. "Step three — event study. Standard market microstructure stuff." → show the CAR chart template
4. "Step four — find out if I wasted my weekend."

**Tone:** Dry, confident, self-deprecating at the end

---

## Video 3 — The Results (Post when you have them)

**This is the main event. The previous two videos are the setup.**

**Format:** Talking head + data visualisation cuts, 60–90 seconds

**Two versions depending on result:**

### If you find something:
> "Okay so. The November trailer drop — 181 million views in 24 hours —
> produced a [X]% cumulative abnormal return in LVMH over the following three days.
> Prada itself barely moved.
> Which makes sense because Prada had nothing to do with this film.
> LVMH owns Dior. The film is Dior-coded.
> The market apparently knows this.
> Anyway. Movies are just vibes-based trading signals now."

### If you find nothing:
> "Good news: I ran the analysis.
> Bad news: luxury stocks do not care about Anne Hathaway.
> The null hypothesis survived.
> I have a very clean dataset and a very humbling result.
> Posting the full write-up anyway because null results are data too
> and also I spent a week on this."

**Why the null result version is still great content:** It's honest, it's funny, and it shows you understand what a null result means. That's actually more impressive than a cherry-picked positive finding.

---

## Ongoing Series Potential

If this gets traction, the format is repeatable:

| Event | Stocks | Angle |
|---|---|---|
| Met Gala | LVMH, Kering | Does the most-talked-about look predict brand search volume? |
| Viral TikTok fashion trend | ELF Beauty, e.l.f. | Does TikTok virality lead stock price by 48hrs? |
| A brand collab drops | Relevant ticker | Collab announcement vs. stock pop |
| Fashion week | Luxury basket | Does Paris Fashion Week produce sector-wide abnormal returns? |

---

## Caption Templates

**Video 1:**
```
watched devil wears prada 2. immediately opened terminal.
building a sentiment analysis pipeline to test whether a fashion film 
moves luxury stock prices. results in a few weeks.
full methodology on github (link in bio)
#quantfinance #python #sentimentanalysis #devilwearsprada #luxurystocks #fintech
```

**Video 2:**
```
the methodology video. reddit > twitter api. finbert vs vader. 
event study framework. four natural experiments.
this is a normal thing to do after watching a movie.
#python #nlp #machinelearning #eventdriven #alternativedata
```

**Video 3 (result):**
```
results are in. [teaser line — one sentence, no spoiler]
full write-up on linkedin + github (link in bio)
#quantfinance #sentimentanalysis #luxurystocks #devilwearsprada2
```

---

## Production Notes

- **No need for fancy setup.** Terminal on screen + your voice is the aesthetic. The code is the visual.
- **Don't over-explain the finance.** The joke is that you're doing serious quant work because of a fashion film. Trust the audience to find that funny without explaining it.
- **The LinkedIn article is the depth layer.** TikTok/Insta is the hook. People who want the methodology go to LinkedIn. People who just want to watch someone be slightly unhinged about stocks watch the video.
- **Post Video 1 this week** while the film is in cultural conversation. Do not wait for results.
