from src.backtester import Backtester
from src.indicator import Indicator
from src.ml_predictor import ML_Predictor
from src.portfolio import Portfolio
from src.stock import Stock
from src.strategy import Strategy, MAC_S, RSI_S, COMBINED_S
from src.visualizer import Visualizer


def test_rule_based_strategies():
    print("------Testing Rule-Based Strategies-------")

    # Create stock and fetch data
    stock_ticker = input("Enter the stock ticker: ")
    stock = Stock(stock_ticker)
    start_date = input(
        "Enter the start date for stock data in yyyy-mm-dd \nOR\n Enter 'max' to get the maximum date available: "
    )
    if start_date == "max":
        stock.fetch_full_data()
        print(f"Fetched full data of {len(stock.data)} days data for {stock.ticker}")
    else:
        end_date = input("Enter the end date for stock data in yyyy-mm-dd : ")
        stock.fetch_data(start_date, end_date)
        print(f"Fetched full data of {len(stock.data)} days data for {stock.ticker}")

    # Add Indicators
    indicator = Indicator(stock)
    indicator.add_sma(short_period=20, long_period=50, column="Close")
    indicator.add_ema(short_period=12, long_period=26, column="Close")
    indicator.add_rsi(period=14)
    if indicator.check_indicators():
        print(f"Indicators added successfully to {stock.ticker}")
    else:
        print(f"Error in adding Indicators to {stock.ticker}")

    # Strategies

    # MAC Strategy
    print("-------MA Crossover Strategy-------")
    mac_strategy = MAC_S(stock)
    mac_backtester = Backtester(mac_strategy, initial_cash=10000)
    mac_results = mac_backtester.run_test(stock)
    print("-------MAC Strategy Results-------")
    print(f"{mac_results}")

    # RSI Strateagy
    print("-------RSI Strategy-------")
    rsi_strategy = RSI_S(stock)
    rsi_backtester = Backtester(rsi_strategy, initial_cash=10000)
    rsi_results = rsi_backtester.run_test(stock)
    print("-------RSI Strategy Results-------")
    print(f"{rsi_results}")

    # Combined Strategy
    print("-------COMBINED Strategy(MAC and RSI)-------")
    combined_strategy = COMBINED_S(stock)
    combined_backtester = Backtester(combined_strategy, initial_cash=10000)
    combined_results = combined_backtester.run_test(stock)
    print("-------combined Strategy Results-------")
    print(f"{combined_results}")

    # Visualizer
    vis = Visualizer(stock)
    choice = int(
        input(
            "Enter 1 to show indicator Visualization\nEnter 2 to show signals visulazation\nEnter 3 to show portfolio peformace visulazation\nEnter 4 to show strategies comparison visulazation"
        )
    )
    if choice == 1:
        # Plotting Indicators
        vis.plot_indicators()
    elif choice == 2:
        # Plot Signals
        mac_signal_vis = vis.plot_signals(mac_strategy)
        rsi_signal_vis = vis.plot_signals(rsi_strategy)
        combined_signal_vis = vis.plot_signals(combined_strategy)
    elif choice == 3:
        # Portfolio peformace
        mac_backtester_vis = vis.plot_portfolio_performance(mac_backtester)
        rsi_backtester_vis = vis.plot_portfolio_performance(rsi_backtester)
        combined_backtester_vis = vis.plot_portfolio_performance(combined_backtester)
    elif choice == 4:
        # Compare Strategies
        results_dict = {
            "MAC": mac_results,
            "RSI": rsi_results,
            "COMBINED": combined_results,
        }

        vis.compare_strategies(results_dict)


def test_ml_strategy():
    print("------Testing ML Strategy-------")

    # Create and fetch stock data
    stock_ticker = input("Enter the stock ticker: ")
    stock = Stock(stock_ticker)
    start_date = input(
        "Enter the start date for stock data in yyyy-mm-dd \nOR\n Enter 'max' to get the maximum date available: "
    )
    if start_date == "max":
        stock.fetch_full_data()
        print(f"Fetched full data of {len(stock.data)} days data for {stock.ticker}")
    else:
        end_date = input("Enter the end date for stock data in yyyy-mm-dd : ")
        stock.fetch_data(start_date, end_date)
        print(f"Fetched full data of {len(stock.data)} days data for {stock.ticker}")

    # Add Indicators
    indicator = Indicator(stock)
    indicator.add_sma(short_period=20, long_period=50)
    indicator.add_ema(short_period=12, long_period=26)
    indicator.add_rsi(period=14)
    if indicator.check_indicators():
        print(f"Indicators added successfully to {stock.ticker}")
    else:
        print(f"Error in adding Indicators to {stock.ticker}")

    # Training ML model
    print("-------Training ML Model-------")
    predictor = ML_Predictor(stock)
    predictor.train_model()
    print("-------ML Model Training complete")

    # Generate ML signals
    ml_df = predictor.generate_ml_signals(threshold=0.01)
    print("-------ML Signals Generated-------")

    # Backtester
    print("-------ML Backtesting-------")
    ml_results = predictor.backtest_ml_signals(ml_df, initial_cash=10000)
    print("-------ML Strategy Results-------")
    print(f"{ml_results}")

    # Visualizer
    vis = Visualizer(stock)
    vis.plot_ml_predictions(ml_df)
    vis.plot_signals_ml(ml_df)


def main():
    test_rule_based_strategies()

    test_ml_strategy()

    print("-------ALL TESTS COMPLETE-------")


if __name__ == "__main__":
    main()
