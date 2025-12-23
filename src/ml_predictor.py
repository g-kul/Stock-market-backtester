from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd


class ML_Predictor:
    def __init__(self, stock):
        self._stock = stock
        self._data = stock.data
        self._model = LinearRegression()
        self._is_trained = False
        self._initial_cash = 0
        self._results = {}
        self._portfolio = None
        self._holding_track = []

    def _prepare_features(self):
        df = self._data.copy()
        df["Price_Change"] = df["Close"].pct_change()
        df["SMA_Diff"] = df["Short_SMA"] - df["Long_SMA"]
        df["RSI_Feature"] = df["RSI"]
        df["Future_Returns"] = (df["Close"].shift(-1) / df["Close"]) - 1
        df = df.dropna()
        feature_columns = ["Price_Change", "SMA_Diff", "RSI_Feature"]
        X = df[feature_columns]
        Y = df["Future_Returns"]
        dates = df.index

        return X, Y, dates

    def train_model(self):
        X, Y, dates = self._prepare_features()

        X_train, X_test, Y_train, Y_test = train_test_split(
            X, Y, test_size=0.2, shuffle=False
        )

        self._model.fit(X_train, Y_train)
        train_score = self._model.score(X_train, Y_train)
        test_score = self._model.score(X_test, Y_test)

        print("Model training complete")
        print(f"Training R2 score: {train_score:.4f}")
        print(f"Test R2 score: {test_score:.4f}")
        self._is_trained = True
        return train_score, test_score

    def _predict(self):
        if not self._is_trained:
            print("The model is not trained, call train_model() first")
            return None

        X, Y, dates = self._prepare_features()
        predictions = self._model.predict(X)

        self._data["ML_Prediction"] = np.nan
        self._data.loc[dates, "ML_Prediction"] = predictions

        return predictions

    def generate_ml_signals(self, threshold=0.01):
        self._predict()
        df = self._data.copy()
        df["ML_Signal"] = 0
        df.loc[df["ML_Prediction"] > threshold, "ML_Signal"] = 1
        df.loc[df["ML_Prediction"] < -threshold, "ML_Signal"] = -1

        buy_signals_generated = (df["ML_Signal"] == 1).sum()
        sell_signals_generated = (df["ML_Signal"] == -1).sum()

        print("ML Signals generated: ")
        print(f"Buy Signals: {buy_signals_generated}")
        print(f"Sell Signals: {sell_signals_generated}")
        print(f"Threshold: {threshold * 100:.1f}%")

        return df

    def backtest_ml_signals(self, ml_df, initial_cash: int = 10000):
        self._initial_cash = initial_cash
        self._portfolio = Portfolio(self._initial_cash)
        self._holding_track = []
        holding = False

        signal_col = "ML_Signal"
        df_run = ml_df

        for index, row in df_run.iterrows():
            date = index
            signal = row[signal_col]
            price = row["Close"]

            if signal == 1 and not holding:
                quantity = self._portfolio.cash // price

                if quantity > 0:
                    success = self._portfolio.buy(self._stock, quantity, price, date)

                    if success:
                        holding = True

            elif signal == -1 and holding:
                quantity = self._portfolio.holdings.get(self._stock, 0)

                if quantity > 0:
                    success = self._portfolio.sell(self._stock, quantity, price, date)

                    if success:
                        holding = False

            final_value = self._portfolio.get_total_value_for_date(self._stock, date)
            self._holding_track.append((date, final_value))

        if not self._portfolio.transactions:
            print("No portfolio history")
            return

        final_total_value = self._portfolio.get_total_value_for_date(self._stock, date)
        total_returns = final_total_value - self._initial_cash
        total_returns_percentage = (
            (final_total_value - self._initial_cash) / (self._initial_cash)
        ) * 100

        self._results = {
            "Initial cash": self._initial_cash,
            "Final total cash": final_total_value,
            "Total returns": total_returns,
            "Percentage returns": total_returns_percentage,
            "No of trades": len(self._portfolio.transactions),
            "Trades done": self._portfolio.transactions,
            "Portfolio history": self._holding_track,
        }

        return self._results
