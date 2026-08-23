"""Trains a simple linear regression model on technical indicators and
turns its predictions into tradeable buy/sell signals.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from .backtester import Backtester


class ML_Predictor:
    SIGNAL_COLUMN = "ML_Signal"

    def __init__(self, stock):
        self._stock = stock
        self._data = stock.data
        self._model = LinearRegression()
        self._is_trained = False

    def _prepare_features(self):
        df = self._data.copy()
        df["Price_Change"] = df["Close"].pct_change()
        df["SMA_Diff"] = df["Short_SMA"] - df["Long_SMA"]
        df["RSI_Feature"] = df["RSI"]
        df["Future_Returns"] = (df["Close"].shift(-1) / df["Close"]) - 1
        df = df.dropna()

        feature_columns = ["Price_Change", "SMA_Diff", "RSI_Feature"]
        X = df[feature_columns]
        y = df["Future_Returns"]
        return X, y, df.index

    def train_model(self):
        X, y, _ = self._prepare_features()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        self._model.fit(X_train, y_train)
        train_score = self._model.score(X_train, y_train)
        test_score = self._model.score(X_test, y_test)

        print("Model training complete")
        print(f"Training R2 score: {train_score:.4f}")
        print(f"Test R2 score: {test_score:.4f}")
        self._is_trained = True
        return train_score, test_score

    def _predict(self):
        if not self._is_trained:
            print("The model is not trained, call train_model() first")
            return None

        X, _, dates = self._prepare_features()
        predictions = self._model.predict(X)

        self._data["ML_Prediction"] = np.nan
        self._data.loc[dates, "ML_Prediction"] = predictions
        return predictions

    def generate_ml_signals(self, threshold=0.01):
        self._predict()
        df = self._data.copy()
        df[self.SIGNAL_COLUMN] = 0
        df.loc[df["ML_Prediction"] > threshold, self.SIGNAL_COLUMN] = 1
        df.loc[df["ML_Prediction"] < -threshold, self.SIGNAL_COLUMN] = -1

        buy_signals = (df[self.SIGNAL_COLUMN] == 1).sum()
        sell_signals = (df[self.SIGNAL_COLUMN] == -1).sum()
        print("ML Signals generated:")
        print(f"Buy Signals: {buy_signals}")
        print(f"Sell Signals: {sell_signals}")
        print(f"Threshold: {threshold * 100:.1f}%")

        return df

    def backtest_ml_signals(self, ml_df, initial_cash: int = 10000):
        """Reuses Backtester's shared execution engine instead of duplicating
        the trading loop."""
        backtester = Backtester(initial_cash=initial_cash)
        return backtester.run_on_signals(self._stock, ml_df, self.SIGNAL_COLUMN)
