"""Simulates trading a strategy's buy/sell signals against a Portfolio."""

from .portfolio import Portfolio


class Backtester:
    def __init__(self, strategy=None, initial_cash: int = 10000):
        self._strategy = strategy
        self._initial_cash = initial_cash
        self._results = {}
        self._portfolio = None
        self._holding_track = []
        self._last_signals_df = None

    @property
    def last_signals_df(self):
        """The signals dataframe from the most recent run, if any. Lets
        callers (e.g. a web frontend) chart the exact buy/sell markers a
        backtest traded on without recomputing them."""
        return self._last_signals_df

    def run_test(self, stock):
        """Generate signals from the configured strategy and backtest them."""
        if self._strategy is None:
            raise ValueError("Backtester requires a strategy to call run_test().")

        df_run = self._strategy.generate_signals()
        if df_run is None:
            print("No signals generated; check that indicators were added first.")
            return self._results

        return self.run_on_signals(stock, df_run, self._strategy.signal_column)

    def run_on_signals(self, stock, df_run, signal_col, initial_cash=None):
        """Run the trading simulation on any dataframe containing a signal
        column (1 = buy, -1 = sell, 0 = hold). Shared by run_test() and by
        ML_Predictor, so rule-based and ML strategies use one execution engine.
        """
        if initial_cash is not None:
            self._initial_cash = initial_cash

        self._portfolio = Portfolio(self._initial_cash)
        self._holding_track = []
        self._last_signals_df = df_run
        holding = False
        date = None

        for index, row in df_run.iterrows():
            date = index
            signal = row[signal_col].item()
            price = row["Close"].item()

            if signal == 1 and not holding:
                quantity = self._portfolio.cash // price
                if quantity > 0:
                    holding = self._portfolio.buy(stock, quantity, price, date)

            elif signal == -1 and holding:
                quantity = self._portfolio.holdings.get(stock, 0)
                if quantity > 0:
                    holding = not self._portfolio.sell(stock, quantity, price, date)

            self._holding_track.append(
                (date, self._portfolio.get_total_value_for_date(stock, date))
            )

        if date is None:
            print("No data available to backtest.")
            return self._results

        self._calculate_metrics(stock, date)
        return self._results

    def _calculate_metrics(self, stock, date):
        if not self._portfolio.transactions:
            print("No portfolio history")
            return

        final_total_value = self._portfolio.get_total_value_for_date(stock, date)
        total_returns = final_total_value - self._initial_cash
        total_returns_percentage = (total_returns / self._initial_cash) * 100

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
