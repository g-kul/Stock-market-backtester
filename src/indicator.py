"""Technical indicator calculations, added as columns on a Stock's dataframe."""


class Indicator:
    def __init__(self, stock):
        self._stock_obj = stock
        self._stock = stock.data

    def add_sma(self, short_period: int = 20, long_period: int = 50, column="Close"):
        """Add short and long Simple Moving Average columns."""
        self._stock["Short_SMA"] = self._stock[column].rolling(window=short_period).mean()
        self._stock["Long_SMA"] = self._stock[column].rolling(window=long_period).mean()

    def add_ema(self, short_period: int = 10, long_period: int = 40, column="Close"):
        """Add short and long Exponential Moving Average columns."""
        self._stock["Short_EMA"] = self._stock[column].ewm(span=short_period, adjust=False).mean()
        self._stock["Long_EMA"] = self._stock[column].ewm(span=long_period, adjust=False).mean()

    def add_rsi(self, period: int = 14):
        """Add a Relative Strength Index column."""
        delta = self._stock["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        self._stock["RSI"] = rsi.fillna(50)

    def check_indicators(self):
        """Return True if all expected indicator columns are present."""
        required = {"Short_SMA", "Long_SMA", "Short_EMA", "Long_EMA", "RSI"}
        missing = required - set(self._stock.columns)
        if missing:
            print(f"Missing indicators: {missing}")
            return False
        return True
