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

    def buy(self, stock_obj, quantity, price, date):
        if self._cash >= (quantity * price):
            self._holdings[stock_obj] = self._holdings.get(stock_obj, 0) + quantity
            trade = {}
            trade = {
                "type": "BUY",
                "ticker": stock_obj.ticker,
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

    def sell(self, stock_obj, quantity, price, date):
        if stock_obj in self._holdings and self._holdings[stock_obj] >= quantity:
            self._holdings[stock_obj] -= quantity
            trade = {}
            trade = {
                "type": "SELL",
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

    def get_total_value_for_date(self, stock_obj, date):
        price_for_date = stock_obj.get_price_on_date(date)
        stock_value = 0
        for i in self._holdings:
            stock_value += self._holdings[i] * price_for_date[i]
        total_value = stock_value + self.cash
        return total_value
