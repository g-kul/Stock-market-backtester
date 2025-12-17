# Stock class
class Stock:
    def __init__(self, ticker):
        self._ticker = ticker
        self._data = None

    @property
    def ticker(self):
        return self._ticker

    @property
    def data(self):
        return self._data

    def fetch_data(self, start_date, end_date):
        try:
            self._data = yf.download(self._ticker, start=start_date, end=end_date)
            return self._data
        except Exception as e:
            print(f"Error: {e}")
            return None

    def fetch_full_data(self):
        try:
            self._data = yf.download(self._ticker, period="max")
            return self._data
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_close_price(self):
        if self.__has_data():
            try:
                return self._data["Close"]
            except KeyError:
                print("There is no data set up to retrieve from")

    def get_price_on_date(self, date):
        if self.__has_data():
            try:
                return self._data["Close"][date]
            except KeyError:
                print(f"The entered date - {date} is not correct!!!")
                return None

    def get_latest_price(self):
        if self.__has_data():
            try:
                return self._data["Close"].iloc[-1]
            except Exception as e:
                print(f"Error: {e}")
                return None

    def get_column(self, column_name):
        if self.__has_data() and column_name in self._data.columns:
            try:
                return self._data[column_name]
            except Exception as e:
                print(f"Error: {e}")
                return None

    def __has_data(self):
        return self._data is not None
