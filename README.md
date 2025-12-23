# Stock Market Analyzer & Backtester

A Python-based trading system that analyzes stocks, generates signals using technical indicators and machine learning, and backtests strategies.

## Features
- Fetch historical stock data via yfinance API
- Calculate technical indicators (SMA, EMA, RSI)
- Multiple trading strategies:
  - Moving Average Crossover
  - RSI Overbought/Oversold
  - Combined Strategy
  - Machine Learning Predictions
- Backtest strategies on historical data
- Portfolio tracking and performance metrics
- Comprehensive visualizations

## Tech Stack
- Python 3
- yfinance (stock data)
- Pandas (data manipulation)
- NumPy (calculations)
- scikit-learn (machine learning)
- matplotlib (visualization)

## Usage
```bash
python main.py
```

## Project Structure
- `stock.py` - Stock data management
- `indicator.py` - Technical indicator calculations
- `strategy.py` - Trading strategy implementations
- `portfolio.py` - Portfolio management
- `backtester.py` - Backtesting engine
- `ml_predictor.py` - Machine learning predictions
- `visualizer.py` - Visualization tools

## Performance Metrics
- Total return %
- Number of trades
- Portfolio value over time

## Future Improvements
- Multi-stock portfolio support
- More ML models (Random Forest, LSTM)
- Risk management (stop-loss, position sizing)
- Real-time trading integration
- More technical indicators (MACD, Bollinger Bands)
