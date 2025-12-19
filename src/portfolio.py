# Portfolio class
class Portfolio:
    def __init__(self, initial_cash, stock):
        self._stock_obj = stock
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

    def _get_current_prices(self):
        return {key: self._stock_obj.data["Close"].iloc[-1] for key in self._holdings}

    def buy(self, ticker, quantity, price, date):
        if self._cash > (quantity * price):
            self._holdings[ticker] = self._holdings.get(ticker, 0) + quantity
            trade = {}
            trade["BUY"] = {
                "ticker": ticker,
                "quantity": quantity,
                "price": price,
                "date": date,
            }
            self._transactions.append(trade)
            self._cash -= quantity * price
            return True
        else:
            print("Not enough cash to buy the shares")
            return False

    def sell(self, ticker, quantity, price, date):
        if ticker in self._holdings and self._holdings[ticker] >= quantity:
            self._holdings[ticker] -= quantity
            trade = {}
            trade["SELL"] = {
                "ticker": ticker,
                "quantity": quantity,
                "price": price,
                "date": date,
            }
            self._transactions.append(trade)
            self._cash += quantity * price
            return True
        else:
            print("Not enough shares available to execute sell")
            return False

    def get_total_value(self):
        current_prices = self._get_current_prices()
        total_value = 0
        for i in self._holdings:
            total_value += self._holdings[i] * current_prices[i]
        return total_value
