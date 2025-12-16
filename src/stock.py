# Stock class
class Stock:
    def __init__(self, ticker):
        self._ticker = ticker
        self._data = None

    def fetch_data(self, start_date, end_date):
        try:
            self._data = yf.download(self._ticker, start=start_date, end=end_date)
            return self._data
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_close_price(self):
        if self._data:
            return self._data["Close"]
        else:
            raise print("There is no data set up to retrieve from")

    def get_price_on_date(self, date):
        try:
            return self._data["Close"][date]
        except Exception as e:
            print(f"Error: {e}")

    def get_latest_price(self):
        return self._data["Close"].iloc[-1]
