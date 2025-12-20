# Portfolio class
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
        if self._cash >= (quantity * price):
            self._holdings[stock] = self._holdings.get(stock, 0) + quantity
            balance_cash = self._cash - (quantity * price)
            trade = {}
            trade = {
                "type": "BUY",
                "ticker": stock.ticker,
                "quantity": quantity,
                "price": price,
                "date": date,
                "balance_cash": balance_cash,
            }
            self._transactions.append(trade)
            self._cash -= quantity * price
            return True
        else:
            print("Not enough cash to buy the shares")
            return False

    def sell(self, stock, quantity, price, date):
        if stock in self._holdings and self._holdings[stock] >= quantity:
            self._holdings[stock] -= quantity
            balance_cash = self._cash + (quantity * price)
            trade = {}
            trade = {
                "type": "SELL",
                "ticker": stock.ticker,
                "quantity": quantity,
                "price": price,
                "date": date,
                "balance cash": balance_cash,
            }
            self._transactions.append(trade)
            self._cash += quantity * price
            return True
        else:
            print("Not enough shares available to execute sell")
            return False

    def get_total_value_for_date(self, stock, date):
        price_for_date = stock.get_price_on_date(date)
        stock_value = 0
        stock_value += self._holdings[stock] * price_for_date
        total_value = stock_value + self.cash
        return total_value
