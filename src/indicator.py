import numpy as np
import pandas as pd


# Indicator class
class Indicator:
    def __init__(self, stock):
        self._stock_obj = stock
        self._stock = stock.data

    def add_sma(self, short_period: int = 20, long_period: int = 50, column="Close"):
        self._stock["Short_SMA"] = (
            self._stock[column].rolling(window=short_period).mean()
        )
        self._stock["Long_SMA"] = self._stock[column].rolling(window=long_period).mean()
        print(f"{self._stock.columns}")

    def add_ema(self, short_period: int = 10, long_period: int = 40, column="Close"):
        self._stock["Short_EMA"] = (
            self._stock[column].ewm(span=short_period, adjust=False).mean()
        )
        self._stock["Long_EMA"] = (
            self._stock[column].ewm(span=long_period, adjust=False).mean()
        )
        print(f"{self._stock.columns}")

    def add_rsi(self, period: int = 14):
        delta = self._stock["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        self._stock["RSI"] = rsi.fillna(50)
        print(f"{self._stock.columns}")

    def check_indicators(self):
        # required = {"Short_SMA", "Long_SMA", "Short_EMA", "Long_EMA", "RSI"}
        # return required.issubset(self._stock.columns)
        added = set(self._stock.columns)
        required = {"Short_SMA", "Long_SMA", "Short_EMA", "Long_EMA", "RSI"}
        missing = required - added
        if missing:
            print(f"Missing indicators: {missing}")
            return False
        return True
