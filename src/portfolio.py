"""Tracks cash, holdings, and trade history for a single backtest run."""


class Portfolio:
    def __init__(self, initial_cash):
        self._cash = initial_cash
        self._holdings = {}
        self._transactions = []

    @property
    def holdings(self):
        return self._holdings

    @property
    def cash(self):
        return self._cash

    @property
    def transactions(self):
        return self._transactions

    def buy(self, stock, quantity, price, date):
        if self._cash < (quantity * price):
            print("Not enough cash to buy the shares")
            return False

        self._holdings[stock] = self._holdings.get(stock, 0) + quantity
        self._cash -= quantity * price
        self._transactions.append({
            "type": "BUY",
            "ticker": stock.ticker,
            "quantity": quantity,
            "price": price,
            "date": date,
            "balance_cash": self._cash,
        })
        return True

    def sell(self, stock, quantity, price, date):
        if stock not in self._holdings or self._holdings[stock] < quantity:
            print("Not enough shares available to execute sell")
            return False

        self._holdings[stock] -= quantity
        self._cash += quantity * price
        self._transactions.append({
            "type": "SELL",
            "ticker": stock.ticker,
            "quantity": quantity,
            "price": price,
            "date": date,
            "balance_cash": self._cash,
        })
        return True

    def get_total_value_for_date(self, stock, date):
        price_for_date = stock.get_price_on_date(date)
        stock_value = self._holdings.get(stock, 0) * price_for_date
        return stock_value + self._cash
