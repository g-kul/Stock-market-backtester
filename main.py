from backtester import Backtester
from indicator import Indicator
from ml_predictor import ML_Predictor
from portfolio import Portfolio
from stock import Stock
from strategy import Strategy
from visualizer import Visualizer


def test_rule_based_strategies():
    print("------Testing Rule-Based Strategies-------")

    stock_ticker = input("Enter the stock ticker: ")
    stock = Stock(stock_ticker)
    start_date = input(
        "Enter the start date for stock data in yyyy/mm/dd \nOR\n Enter 'max' to get the maximum date available: "
    )
    end_date = input("Enter the end date for stock data in yyyy/mm/dd : ")
