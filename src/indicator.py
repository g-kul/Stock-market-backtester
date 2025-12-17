# Indicator class
class Indicator:
    def __init__(self, stock_data):
        self._stock = stock_data

    def add_sma(self, period: int = 10, column="Close"):
        self._stock["SMA"] = self._stock[column].rolling(window=period).mean()

    def add_ema(self, period: int = 20, column="Close"):
        self._stock["EMA"] = self._stock[column].ewm(span=period, adjust=False).mean()

    def add_rsi(self, period: int = 14):
        delta = self._stock["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        for i in range(period, len(self._stock["Close"])):
            avg_gain.iloc[i] = (
                avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]
            ) / period
            avg_loss.iloc[i] = (
                avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]
            ) / period

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        self._stock["RSI"] = rsi.fillna(0)
