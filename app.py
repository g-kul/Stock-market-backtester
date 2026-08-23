"""Flask frontend for the Stock Market Analyzer & Backtester.

Wraps the existing engine in src/ (Stock, Indicator, strategies, Backtester,
ML_Predictor) with a web UI: configure a backtest, run it, and see the
resulting charts and metrics without touching the command line.
"""

import base64
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Flask, flash, redirect, render_template, request, url_for

from src.stock import Stock
from src.indicator import Indicator
from src.strategy import MAC_S, RSI_S, COMBINED_S
from src.backtester import Backtester
from src.ml_predictor import ML_Predictor

app = Flask(__name__)
app.secret_key = "dev-only-secret-key"  # fine for local/personal use

# ---------------------------------------------------------------------------
# Look & feel — shared palette with static/css/style.css
# ---------------------------------------------------------------------------
COLOR_BLUE = "#0071e3"
COLOR_GREEN = "#1d8a4c"
COLOR_RED = "#d70015"
COLOR_GREY = "#86868b"
COLOR_INK = "#1d1d1f"
COLOR_PALETTE = [COLOR_BLUE, COLOR_GREEN, COLOR_RED, "#8e44ad"]

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.edgecolor": "#d2d2d7",
    "axes.labelcolor": COLOR_INK,
    "text.color": COLOR_INK,
    "xtick.color": COLOR_GREY,
    "ytick.color": COLOR_GREY,
    "axes.grid": True,
    "grid.color": "#e8e8ed",
    "grid.linewidth": 0.6,
})

STRATEGY_INFO = {
    "mac": {
        "label": "Moving Average Crossover",
        "desc": "Buys when the short-term average crosses above the long-term average, and sells on the reverse cross.",
    },
    "rsi": {
        "label": "RSI Overbought / Oversold",
        "desc": "Buys when RSI drops below the oversold line, sells when it rises above the overbought line.",
    },
    "combined": {
        "label": "Combined (MAC + RSI)",
        "desc": "Only trades when a moving-average crossover and a confirming RSI reading agree.",
    },
    "ml": {
        "label": "Machine Learning",
        "desc": "A linear regression model trained on price change, moving-average spread, and RSI predicts next-day returns.",
    },
}


# ---------------------------------------------------------------------------
# Chart helpers — render matplotlib figures to base64 PNGs for inline <img>
# ---------------------------------------------------------------------------
def _fig_to_base64():
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=150, transparent=True)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def chart_indicators(stock):
    data = stock.data
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 6), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )
    ax1.plot(data.index, data["Close"], label="Close", color=COLOR_INK, linewidth=1.6)
    ax1.plot(data.index, data["Short_SMA"], label="Short SMA", color=COLOR_BLUE, linewidth=1.1)
    ax1.plot(data.index, data["Long_SMA"], label="Long SMA", color=COLOR_RED, linewidth=1.1)
    ax1.plot(data.index, data["Short_EMA"], label="Short EMA", color=COLOR_GREEN, linewidth=1, linestyle="--")
    ax1.plot(data.index, data["Long_EMA"], label="Long EMA", color=COLOR_GREY, linewidth=1, linestyle="--")
    ax1.set_ylabel("Price")
    ax1.set_title(f"{stock.ticker} \u2014 Price & Indicators")
    ax1.legend(loc="upper left", frameon=False, fontsize=9)

    ax2.plot(data.index, data["RSI"], color=COLOR_BLUE, linewidth=1.2)
    ax2.axhline(70, color=COLOR_RED, linestyle="--", linewidth=1)
    ax2.axhline(30, color=COLOR_GREEN, linestyle="--", linewidth=1)
    ax2.set_ylabel("RSI")
    ax2.set_ylim(0, 100)

    return _fig_to_base64()


def chart_signals(dates, close, signal_series, title):
    fig, ax = plt.subplots(figsize=(11, 4.3))
    ax.plot(dates, close, color=COLOR_INK, linewidth=1.4, label="Close")

    buy_mask = signal_series == 1
    sell_mask = signal_series == -1
    ax.scatter(dates[buy_mask], close[buy_mask], marker="^", color=COLOR_GREEN, s=70, label="Buy", zorder=5)
    ax.scatter(dates[sell_mask], close[sell_mask], marker="v", color=COLOR_RED, s=70, label="Sell", zorder=5)

    ax.set_title(title)
    ax.set_ylabel("Price")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    return _fig_to_base64()


def chart_portfolio(results, title):
    history = results["Portfolio history"]
    dates = [x[0] for x in history]
    values = [x[1] for x in history]

    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.plot(dates, values, color=COLOR_BLUE, linewidth=1.8, label="Portfolio value")
    ax.axhline(results["Initial cash"], color=COLOR_GREY, linestyle="--", linewidth=1, label="Initial cash")
    ax.set_title(title)
    ax.set_ylabel("Value ($)")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    return _fig_to_base64()


def chart_comparison(results_by_label):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    for i, (label, results) in enumerate(results_by_label.items()):
        history = results["Portfolio history"]
        dates = [x[0] for x in history]
        values = [x[1] for x in history]
        ax1.plot(dates, values, label=label, color=COLOR_PALETTE[i % len(COLOR_PALETTE)], linewidth=1.6)
    ax1.set_title("Portfolio growth")
    ax1.set_ylabel("Value ($)")
    ax1.legend(loc="upper left", frameon=False, fontsize=8)

    labels = list(results_by_label.keys())
    returns = [results_by_label[l]["Percentage returns"] for l in labels]
    colors = [COLOR_GREEN if r >= 0 else COLOR_RED for r in returns]
    ax2.bar(labels, returns, color=colors, alpha=0.85)
    ax2.axhline(0, color=COLOR_INK, linewidth=0.8)
    ax2.set_title("Total return (%)")
    ax2.tick_params(axis="x", labelrotation=20)

    return _fig_to_base64()


def chart_ml_predictions(ml_df, ticker):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)

    ax1.plot(ml_df.index, ml_df["Close"], color=COLOR_INK, linewidth=1.4, label="Close")
    up_days = ml_df[ml_df["ML_Signal"] > 0]
    down_days = ml_df[ml_df["ML_Signal"] < 0]
    ax1.scatter(up_days.index, up_days["Close"], color=COLOR_GREEN, alpha=0.35, s=18, label="Predicted up")
    ax1.scatter(down_days.index, down_days["Close"], color=COLOR_RED, alpha=0.35, s=18, label="Predicted down")
    ax1.set_title(f"{ticker} \u2014 ML predicted direction")
    ax1.legend(loc="upper left", frameon=False, fontsize=9)

    ax2.plot(ml_df.index, ml_df["ML_Prediction"], color=COLOR_BLUE, linewidth=1.2)
    ax2.axhline(0, color=COLOR_GREY, linewidth=0.8)
    ax2.set_ylabel("Predicted return")
    ax2.set_title("Predicted next-day return")

    return _fig_to_base64()


def build_strategy_view(key, strat, bt, results, ticker):
    info = STRATEGY_INFO[key]
    view = {
        "key": key,
        "label": info["label"],
        "desc": info["desc"],
        "results": results,
        "signals_chart": None,
        "performance_chart": None,
    }

    signals_df = bt.last_signals_df
    if results and signals_df is not None:
        view["signals_chart"] = chart_signals(
            signals_df.index,
            signals_df["Close"],
            signals_df[strat.signal_column],
            f"{ticker} \u2014 {info['label']} signals",
        )
        view["performance_chart"] = chart_portfolio(
            results, f"{ticker} \u2014 {info['label']} portfolio value"
        )
    return view


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/backtest", methods=["GET", "POST"])
def backtest():
    if request.method == "GET":
        return render_template("backtest_form.html")

    form = request.form
    ticker = (form.get("ticker") or "").strip().upper()
    start_date = (form.get("start_date") or "max").strip()
    end_date = (form.get("end_date") or "").strip()
    selected = form.getlist("strategies")

    if not ticker:
        flash("Enter a ticker symbol to run a backtest.")
        return redirect(url_for("backtest"))
    if not selected:
        flash("Select at least one strategy to test.")
        return redirect(url_for("backtest"))
    if start_date.lower() != "max" and not end_date:
        flash('Enter an end date, or type "max" in the start date field for full history.')
        return redirect(url_for("backtest"))

    try:
        initial_cash = float(form.get("initial_cash") or 10000)
    except ValueError:
        initial_cash = 10000.0

    sma_short = int(form.get("sma_short") or 20)
    sma_long = int(form.get("sma_long") or 50)
    ema_short = int(form.get("ema_short") or 12)
    ema_long = int(form.get("ema_long") or 26)
    rsi_period = int(form.get("rsi_period") or 14)
    rsi_oversold = int(form.get("rsi_oversold") or 30)
    rsi_overbought = int(form.get("rsi_overbought") or 70)

    stock = Stock(ticker)
    try:
        if start_date.lower() == "max":
            stock.fetch_full_data()
            date_range_label = "Full available history"
        else:
            stock.fetch_data(start_date, end_date)
            date_range_label = f"{start_date} \u2192 {end_date}"
    except Exception as e:
        flash(f"Couldn't fetch data for {ticker}: {e}")
        return redirect(url_for("backtest"))

    if stock.data is None or stock.data.empty:
        flash(f'No data returned for "{ticker}". Check the ticker symbol and date range.')
        return redirect(url_for("backtest"))

    indicator = Indicator(stock)
    indicator.add_sma(short_period=sma_short, long_period=sma_long)
    indicator.add_ema(short_period=ema_short, long_period=ema_long)
    indicator.add_rsi(period=rsi_period)

    if not indicator.check_indicators():
        flash("Not enough data to compute indicators for this range. Try a longer date range.")
        return redirect(url_for("backtest"))

    indicator_chart = chart_indicators(stock)

    strategy_results = []
    results_by_label = {}

    if "mac" in selected:
        strat = MAC_S(stock)
        bt = Backtester(strat, initial_cash=initial_cash)
        res = bt.run_test(stock)
        strategy_results.append(build_strategy_view("mac", strat, bt, res, ticker))
        if res:
            results_by_label[STRATEGY_INFO["mac"]["label"]] = res

    if "rsi" in selected:
        strat = RSI_S(stock, oversold=rsi_oversold, overbought=rsi_overbought)
        bt = Backtester(strat, initial_cash=initial_cash)
        res = bt.run_test(stock)
        strategy_results.append(build_strategy_view("rsi", strat, bt, res, ticker))
        if res:
            results_by_label[STRATEGY_INFO["rsi"]["label"]] = res

    if "combined" in selected:
        strat = COMBINED_S(stock, oversold=rsi_oversold, overbought=rsi_overbought)
        bt = Backtester(strat, initial_cash=initial_cash)
        res = bt.run_test(stock)
        strategy_results.append(build_strategy_view("combined", strat, bt, res, ticker))
        if res:
            results_by_label[STRATEGY_INFO["combined"]["label"]] = res

    ml_view = None
    if "ml" in selected:
        try:
            predictor = ML_Predictor(stock)
            predictor.train_model()
            ml_df = predictor.generate_ml_signals()
            ml_res = predictor.backtest_ml_signals(ml_df, initial_cash=initial_cash)

            ml_view = {
                "label": STRATEGY_INFO["ml"]["label"],
                "desc": STRATEGY_INFO["ml"]["desc"],
                "results": ml_res,
                "prediction_chart": chart_ml_predictions(ml_df, ticker),
                "signals_chart": None,
                "performance_chart": None,
            }
            if ml_res:
                ml_view["signals_chart"] = chart_signals(
                    ml_df.index, ml_df["Close"], ml_df["ML_Signal"], f"{ticker} \u2014 ML signals"
                )
                ml_view["performance_chart"] = chart_portfolio(ml_res, f"{ticker} \u2014 ML portfolio value")
                results_by_label[STRATEGY_INFO["ml"]["label"]] = ml_res
        except Exception as e:
            flash(f"The machine learning strategy couldn't be run: {e}")

    comparison_chart = chart_comparison(results_by_label) if len(results_by_label) >= 2 else None

    return render_template(
        "results.html",
        ticker=ticker,
        date_range_label=date_range_label,
        initial_cash=initial_cash,
        indicator_chart=indicator_chart,
        strategy_results=strategy_results,
        ml_view=ml_view,
        comparison_chart=comparison_chart,
    )


if __name__ == "__main__":
    app.run(debug=True)
