import numpy as np
import pandas as pd


# Strategy class
class Strategy:
    def __init__(self, stock):
        self._stock_obj = stock
        self._data = stock.data


class MAC_S(Strategy):
    def __init__(self, stock):
        super().__init__(stock)

    def _check_data(self):
        if "Short_SMA" in self._data.columns and "Long_SMA" in self._data.columns:
            return True
        else:
            print("The data doesnt have the necessary indicators set up")
            return False

    def generate_signals(self):
        if self._check_data():
            df_mac = self._data.copy()
            df_mac["MAC_Signal"] = 0

            # buy Signal
            df_mac.loc[
                (df_mac["Short_SMA"] > df_mac["Long_SMA"])
                & (df_mac["Short_SMA"].shift(1) <= df_mac["Long_SMA"].shift(1)),
                "MAC_Signal",
            ] = 1
            # sell Signal
            df_mac.loc[
                (df_mac["Short_SMA"] < df_mac["Long_SMA"])
                & (df_mac["Short_SMA"].shift(1) >= df_mac["Long_SMA"].shift(1)),
                "MAC_Signal",
            ] = -1

            return df_mac


class RSI_S(Strategy):
    def __init__(self, stock, oversold: int = 30, overbought: int = 70):
        super().__init__(stock)
        self._ovs = oversold
        self._ovb = overbought

    def _check_data(self):
        if "RSI" in self._data.columns:
            return True
        else:
            print("The data doesnt have the necessary indicators set up")
            return False

    def generate_signals(self):
        if self._check_data():
            df_rsi = self._data.copy()
            df_rsi["RSI_Signal"] = 0

            # buy_singal
            df_rsi.loc[(df_rsi["RSI"] < self._ovs), "RSI_Signal"] = 1
            # sell Signal
            df_rsi.loc[(df_rsi["RSI"] > self._ovb), "RSI_Signal"] = -1

            return df_rsi


class COMBINED_S(Strategy):
    def __init__(self, stock, oversold: int = 30, overbought: int = 70):
        super().__init__(stock)
        self._ovs = oversold
        self._ovb = overbought

    def _check_data(self):
        if (
            "Short_SMA" in self._data.columns
            and "Long_SMA" in self._data.columns
            and "RSI" in self._data.columns
        ):
            return True
        else:
            print("The data doesnt have the necessary indicators set up")
            return False

    def generate_signals(self):
        if self._check_data():
            df_comb = self._data.copy()
            df_comb["COMB_Signal"] = 0

            # buy signal
            df_comb.loc[
                (
                    ((df_comb["Short_SMA"]) > df_comb["Long_SMA"])
                    & (df_comb["Short_SMA"].shift(1) <= df_comb["Long_SMA"].shift(1))
                    & (df_comb["RSI"] < self._ovs)
                ),
                "COMB_Signal",
            ] = 1
            # sell signal
            df_comb.loc[
                (
                    ((df_comb["Short_SMA"]) < df_comb["Long_SMA"])
                    & (df_comb["Short_SMA"].shift(1) >= df_comb["Long_SMA"].shift(1))
                    & (df_comb["RSI"] > self._ovb)
                ),
                "COMB_Signal",
            ] = -1

            return df_comb
