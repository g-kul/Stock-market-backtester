"""Trading strategy implementations.

Each strategy consumes indicator columns already present on the stock's
dataframe and produces a signal column (1 = buy, -1 = sell, 0 = hold).
Subclasses declare their own `signal_column` name so that callers
(Backtester, Visualizer) can look it up generically instead of branching
on the strategy's type.
"""


class Strategy:
    """Base class for all trading strategies."""

    #: Name of the column generate_signals() adds to the dataframe.
    #: Subclasses must override this.
    signal_column = None

    def __init__(self, stock):
        self._stock_obj = stock
        self._data = stock.data

    def generate_signals(self):
        raise NotImplementedError("Subclasses must implement generate_signals().")


class MAC_S(Strategy):
    """Moving Average Crossover strategy."""

    signal_column = "MAC_Signal"

    def _check_data(self):
        if "Short_SMA" in self._data.columns and "Long_SMA" in self._data.columns:
            return True
        print("The data doesn't have the necessary indicators set up")
        return False

    def generate_signals(self):
        if not self._check_data():
            return None

        df_mac = self._data.copy()
        df_mac[self.signal_column] = 0

        # Buy signal: short SMA crosses above long SMA
        df_mac.loc[
            (df_mac["Short_SMA"] > df_mac["Long_SMA"])
            & (df_mac["Short_SMA"].shift(1) <= df_mac["Long_SMA"].shift(1)),
            self.signal_column,
        ] = 1
        # Sell signal: short SMA crosses below long SMA
        df_mac.loc[
            (df_mac["Short_SMA"] < df_mac["Long_SMA"])
            & (df_mac["Short_SMA"].shift(1) >= df_mac["Long_SMA"].shift(1)),
            self.signal_column,
        ] = -1

        return df_mac


class RSI_S(Strategy):
    """RSI overbought/oversold strategy."""

    signal_column = "RSI_Signal"

    def __init__(self, stock, oversold: int = 30, overbought: int = 70):
        super().__init__(stock)
        self._ovs = oversold
        self._ovb = overbought

    def _check_data(self):
        if "RSI" in self._data.columns:
            return True
        print("The data doesn't have the necessary indicators set up")
        return False

    def generate_signals(self):
        if not self._check_data():
            return None

        df_rsi = self._data.copy()
        df_rsi[self.signal_column] = 0

        df_rsi.loc[df_rsi["RSI"] < self._ovs, self.signal_column] = 1
        df_rsi.loc[df_rsi["RSI"] > self._ovb, self.signal_column] = -1

        return df_rsi


class COMBINED_S(Strategy):
    """Combines MA Crossover and RSI conditions for stronger signals."""

    signal_column = "COMB_Signal"

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
        print("The data doesn't have the necessary indicators set up")
        return False

    def generate_signals(self):
        if not self._check_data():
            return None

        df_comb = self._data.copy()
        df_comb[self.signal_column] = 0

        df_comb.loc[
            (
                (df_comb["Short_SMA"] > df_comb["Long_SMA"])
                & (df_comb["Short_SMA"].shift(1) <= df_comb["Long_SMA"].shift(1))
                & (df_comb["RSI"] < self._ovs)
            ),
            self.signal_column,
        ] = 1
        df_comb.loc[
            (
                (df_comb["Short_SMA"] < df_comb["Long_SMA"])
                & (df_comb["Short_SMA"].shift(1) >= df_comb["Long_SMA"].shift(1))
                & (df_comb["RSI"] > self._ovb)
            ),
            self.signal_column,
        ] = -1

        return df_comb
