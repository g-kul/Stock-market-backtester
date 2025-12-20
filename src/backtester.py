# Backtester class
class Backtest:
    def __init__(self, strategy, initial_cash: int = 10000):
        self._strategy = strategy
        self._initial_cash = initial_cash
        self._results = {}
        self._porfolio = None
        self._portfolio_history = []

    def run_test(self, stock):
        self._portfolio = Portfolio(self._initial_cash)
        self._porfolio_history = []
        holding = False

        df_run = self._strategy.generate_signals()

        if isinstance(self._strategy, MAC_S):
            signal_col = "MAC_Signal"
        elif isinstance(self._strategy, RSI_S):
            signal_col = "RSI_Signal"
        elif isinstance(self._strategy, COMBINED_S):
            signal_col = "COMB_Signal"

        for date, row in df_run.iterrows():
            date = index
            signal = row[signal_col]
            price = row["Close"]

            if signal == 1:
                quantity = self._initial_cash // price

                if quantity > 0:
                    success = self._portfolio.buy(stock, quantity, price, date)

                    if success and self._portfolio is not None:
                        holding = True

            elif signal == -1 and holding:
                quantity = self._initial_cash // price

                if quantity > 0:
                    success = self._portfolio.sell(stock, quantity, price, date)

                    if success and self._portfolio is None:
                        holdings = False

            portfolio_value = self._portfolio.get_total_value_for_date(stock, date)
            self._portfolio_history.append((date, portfolio_value))

            self._calculate_metrics()

            return self._results

    def _calculate_metrics(self):
        if not self._portfolio_history:
            print("No porfolio history")
            return

        final_value = self._porfolio_history[-1][1]
        total_returns = final_value - self._initial_cash
        total_returns_percentage = (
            (final_value - self._initial_cash) / (self._initial_cash)
        ) * 100

        self._results = {
            "Initial Cash": self._initial_cash,
            "Final Cash": final_value,
            "Total returns": total_returns,
            "Percentage returns": total_returns_percentage,
            "No of trades": len(self._porfolio_history),
            "Portfolio history": self._porfolio_history,
            "Trades done": self._portfolio.transactions,
        }

    def get_results(self):
        return self._results
