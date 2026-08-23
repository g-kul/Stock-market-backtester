# Stock Market Backtester — Web Frontend

A Flask + HTML/CSS dashboard for the Stock Market Analyzer & Backtester,
styled after apple.com — clean type, generous whitespace, a frosted nav bar —
so you can configure and run a backtest from a real UI instead of the
command line.

## Run it

```
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Notes

- Data is fetched live from Yahoo Finance via `yfinance` on every backtest —
  nothing is cached or stored locally, so you'll need an internet connection
  each time you run one.
- Pages: **Overview** (what the tool does), **New Backtest** (ticker, date
  range, starting cash, which strategies to test, and an "Advanced" panel for
  indicator periods/thresholds), and **Results** (indicator chart, big
  spec-style return numbers per strategy, signals + portfolio charts, a
  cross-strategy comparison when 2+ are selected, and the ML model's
  predicted-direction chart).
- This wraps the existing `src/` engine (`Stock`, `Indicator`, `Strategy`,
  `Backtester`, `ML_Predictor`) directly — the CLI `main.py` still works
  unchanged, side by side with the web app.
- Designed for desktop browsers only — no mobile layout.
