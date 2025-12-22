class ML_Predictor:
    def __init__(self, stock):
        self._stock = stock
        self._data = stock.data
        self._model = LinearRegression()
        self._is_trained = False

    def prepare_features(self):
        df = self._data.copy()
        df["Price_Change"] = df["Close"].pct_change()
        df["SMA_Diff"] = df["Short_SMA"] - df["Long_SMA"]
        df["RSI_Feature"] = df["RSI"]
        df["Future_Returns"] = (df["Close"].shift(-1) / df["Close"]) - 1
        df = df.dropna()
        feature_columns = ["Price_Change", "SMA_Diff", "RSI_Feature"]
        X = df["feature_columns"]
        Y = df["Future_Returns"]
        dates = df.index

        return X, Y, dates

    def train_model(self):
        X, Y, dates = self.prepare_features()

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

    def predict(self):
        if not self._is_trained:
            print("The model is not trained, call train_model() first")
            return None

        X, Y, dates = self.prepare_features()
        predictions = self._model.predict(X)

        self._data["ML_Prediction"] = np.nan
        self._data.loc[dates, "ML_Prediction"] = predictions

        return predictions

    def generate_ml_signals(self, threshold=0.01):
        self.predict()
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
