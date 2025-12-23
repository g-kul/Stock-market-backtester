from .portfolio import Portfolio
from .strategy import MAC_S, RSI_S, COMBINED_S
import yfinance as yf
import numpy as np
import pandas as pd


# Backtester class
class Backtester:
    def __init__(self, strategy, initial_cash: int = 10000):
        self._strategy = strategy
        self._initial_cash = initial_cash
        self._results = {}
        self._portfolio = None
        self._holding_track = []

    def run_test(self, stock):
        self._portfolio = Portfolio(self._initial_cash)
        self._holding_track = []
        holding = False

        df_run = self._strategy.generate_signals()

        if isinstance(self._strategy, MAC_S):
            signal_col = "MAC_Signal"
        elif isinstance(self._strategy, RSI_S):
            signal_col = "RSI_Signal"
        elif isinstance(self._strategy, COMBINED_S):
            signal_col = "COMB_Signal"

        for index, row in df_run.iterrows():
            date = index
            signal = row[signal_col].item()
            price = row["Close"].item()
            print(f"Debug: signal type = {type(signal)}, value = {signal}")

            if signal == 1 and not holding:
                quantity = self._portfolio.cash // price

                if quantity > 0:
                    success = self._portfolio.buy(stock, quantity, price, date)

                    if success:
                        holding = True

            elif signal == -1 and holding:
                quantity = self._portfolio.holdings.get(stock, 0)

                if quantity > 0:
                    success = self._portfolio.sell(stock, quantity, price, date)

                    if success:
                        holding = False

            final_value = self._portfolio.get_total_value_for_date(stock, date)
            self._holding_track.append((date, final_value))

        self._calculate_metrics(stock, date)
        return self._results

    def _calculate_metrics(self, stock, date):
        if not self._portfolio.transactions:
            print("No porfolio history")
            return

        final_total_value = self._portfolio.get_total_value_for_date(stock, date)
        total_returns = final_total_value - self._initial_cash
        total_returns_percentage = (
            (final_total_value - self._initial_cash) / (self._initial_cash)
        ) * 100

        self._results = {
            "Initial cash": self._initial_cash,
            "Final total cash": final_total_value,
            "Total returns": total_returns,
            "Percentage returns": total_returns_percentage,
            "No of trades": len(self._portfolio.transactions),
            "Trades done": self._portfolio.transactions,
            "Portfolio history": self._holding_track,
        }

    def get_results(self):
        return self._results
