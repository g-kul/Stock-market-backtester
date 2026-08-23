"""Chart helpers for indicators, signals, ML predictions, and portfolio performance.

This is used by the CLI (main.py) and opens interactive matplotlib windows
via plt.show(). The web frontend (app.py) has its own headless chart
functions that render to PNG instead, since a Flask process can't pop up a
GUI window.
"""

import matplotlib.pyplot as plt


class Visualizer:
    def __init__(self, stock):
        self._stock_obj = stock
        self._data = stock.data
        self._ticker = stock.ticker

    def plot_indicators(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
        try:
            ax1.plot(self._data.index, self._data["Close"], label="Price")
            ax1.plot(self._data.index, self._data["Short_SMA"], label="Short_SMA")
            ax1.plot(self._data.index, self._data["Long_SMA"], label="Long_SMA")
            ax1.plot(self._data.index, self._data["Short_EMA"], label="Short_EMA")
            ax1.plot(self._data.index, self._data["Long_EMA"], label="Long_EMA")
            ax1.set_ylabel("Price")
            ax1.legend()
            ax1.set_title(f"{self._ticker} Price and Indicators")

            ax2.plot(self._data.index, self._data["RSI"], color="purple")
            ax2.axhline(70, color="red", linestyle="--", label="Overbought")
            ax2.axhline(30, color="green", linestyle="--", label="Oversold")
            ax2.set_ylabel("RSI")
            ax2.set_ylim(0, 100)
            ax2.legend()

            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Error: {e}")

    def _plot_signals_on_series(self, dates, close, signal_series, title):
        fig, ax = plt.subplots(figsize=(14, 8))
        try:
            ax.plot(dates, close, label="Close Price", linewidth=2)

            buy_mask = signal_series == 1
            sell_mask = signal_series == -1

            ax.scatter(
                dates[buy_mask], close[buy_mask],
                marker="^", color="green", s=100, label="Buy Signal", zorder=5,
            )
            ax.scatter(
                dates[sell_mask], close[sell_mask],
                marker="v", color="red", s=100, label="Sell Signal", zorder=5,
            )
            ax.set_xlabel("Date")
            ax.set_ylabel("Price")
            ax.set_title(title)
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Error: {e}")

    def plot_signals(self, strategy):
        """Plot buy/sell markers for a rule-based strategy's signal column.

        Calls strategy.generate_signals() itself rather than reading from the
        stock's dataframe, since strategies work on a copy of that data and
        never write the signal column back onto it.
        """
        df = strategy.generate_signals()
        if df is None:
            print("No signals to plot; indicators may be missing.")
            return
        self._plot_signals_on_series(
            df.index,
            df["Close"],
            df[strategy.signal_column],
            f"Signals plot - {self._ticker}",
        )

    def plot_signals_ml(self, ml_df):
        """Plot buy/sell markers for the ML strategy's signal column."""
        self._plot_signals_on_series(
            ml_df.index,
            ml_df["Close"],
            ml_df["ML_Signal"],
            f"ML Signals plot - {self._ticker}",
        )

    def plot_portfolio_performance(self, backtest):
        backtest_results = backtest.get_results()
        portfolio_history = backtest_results["Portfolio history"]
        dates = [x[0] for x in portfolio_history]
        values = [x[1] for x in portfolio_history]

        fig, ax = plt.subplots(figsize=(14, 8))
        try:
            ax.plot(dates, values, linewidth=2, label="Portfolio Value")
            ax.axhline(y=backtest_results["Initial cash"], color="gray", linestyle="--", label="Initial Cash")
            ax.set_xlabel("Date")
            ax.set_ylabel("Portfolio Value ($)")
            ax.set_title(f"Portfolio performance - {self._ticker}")
            ax.legend()
            ax.grid(True, alpha=0.3)

            textstr = (
                f"Initial: {backtest_results['Initial cash']:.2f}\n"
                f"Final: {backtest_results['Final total cash']:.2f}\n"
                f"Return: {backtest_results['Total returns']:.2f}\n"
                f"Trades: {backtest_results['No of trades']}\n"
            )
            props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
            ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10, verticalalignment="top", bbox=props)

            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Error: {e}")

    def compare_strategies(self, results_dict):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        for strategy_name, results in results_dict.items():
            history = results["Portfolio history"]
            dates = [x[0] for x in history]
            values = [x[1] for x in history]
            ax1.plot(dates, values, label=strategy_name, linewidth=2)

        ax1.set_xlabel("Date")
        ax1.set_ylabel("Portfolio Value ($)")
        ax1.set_title("Strategy Comparison - Portfolio Growth")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        strategy_names = list(results_dict.keys())
        returns = [results_dict[name]["Total returns"] for name in strategy_names]
        colors = ["green" if r > 0 else "red" for r in returns]
        ax2.bar(strategy_names, returns, color=colors, alpha=0.7)
        ax2.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
        ax2.set_ylabel("Return (%)")
        ax2.set_title("Strategy Comparison - Total Returns")
        ax2.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        plt.show()

    def plot_ml_predictions(self, ml_df):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        try:
            ax1.plot(ml_df.index, ml_df["Close"], label="Actual Price", linewidth=2)
            up_days = ml_df[ml_df["ML_Signal"] > 0]
            ax1.scatter(up_days.index, up_days["Close"], color="green", alpha=0.3, s=20, label="Predicted Up")

            down_days = ml_df[ml_df["ML_Signal"] < 0]
            ax1.scatter(down_days.index, down_days["Close"], color="red", alpha=0.3, s=20, label="Predicted Down")
            ax1.set_ylabel("Price")
            ax1.set_title(f"ML Prediction - {self._ticker}")
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            ax2.plot(ml_df.index, ml_df["ML_Prediction"], label="Predicted Return", color="purple", linewidth=1.5)
            ax2.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
            ax2.fill_between(ml_df.index, 0, ml_df["ML_Signal"], where=ml_df["ML_Signal"] > 0, color="green", alpha=0.3)
            ax2.fill_between(ml_df.index, 0, ml_df["ML_Signal"], where=ml_df["ML_Signal"] < 0, color="red", alpha=0.3)
            ax2.set_xlabel("Date")
            ax2.set_ylabel("Predicted Return")
            ax2.set_title("ML Predicted Returns")
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Error: {e}")
