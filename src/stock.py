# Stock class
class Stock:
    market = "To be entered"

    def __init__(self, ticker):
        self._ticker = ticker
        self._start_date = None
        self._end_date = None
        self._data = None
        self._date = date
        self.amount = 0

    def fetch_data(self, start_date, end_date):
        if yf.Ticker(self.ticker):
            self._data = yf.download(
                self._ticker, start=self._start_date(), end=self._end_date()
            )
            return self._data

    def _start_date(self):
        if datetime.strptime(self._start_date, "%Y/%m/%d"):
            self._start_date = start_date
            return self._start_date
        else:
            raise ValueError(
                "The entered start date is wrong, please enter a valid start date"
            )

    def _end_date(self):
        if datetime.strptime(self._end_date, "%Y/%m/%d"):
            self._end_date = end_date
            return self._end_date
        else:
            raise ValueError(
                "The entered end date is wrong, please enter a valid end date"
            )

    def get_close_price(self):
        if self._data:
            return self._data["Close"]
        else:
            raise print("There is no data set up to retrieve from")

    def get_price_on_date(self, date):
        if dataframe.strptime(self._date, "%Y/%m/%d"):
            return self._data["Close"][self._date]

    def get_latest_price(self, amount):
        return self._data.tail(1)
